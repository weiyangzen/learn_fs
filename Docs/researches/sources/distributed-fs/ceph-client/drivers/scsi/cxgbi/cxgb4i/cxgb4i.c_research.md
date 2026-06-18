# sources/distributed-fs/ceph-client/drivers/scsi/cxgbi/cxgb4i/cxgb4i.c

## Purpose

`cxgb4i.c` is the Chelsio T4/T5/T6 adapter-specific iSCSI offload driver. It binds the common `libcxgbi` iSCSI library to the `cxgb4` lower-layer driver, registers an iSCSI transport and SCSI host template, translates iSCSI TCP lifecycle events into Chelsio CPL/FW work requests, receives CPL completions from the adapter, and configures hardware DDP/page-pod state for direct placement of SCSI Data-In payloads. It is adapter-facing code: most high-level iSCSI session and PDU mechanics live in `libcxgbi.c`, while this file owns TID/ATID handling, L2T, CLIP, ULD registration, firmware work request construction, and Chelsio-specific resource cleanup.

## Important APIs, Types, And Functions

The module exposes no normal C API directly; its important entry points are kernel/module callbacks and function pointers installed into `struct cxgbi_device`. Module parameters tune runtime behavior: `dbg_level`, `cxgb4i_rcv_win`, `cxgb4i_snd_win`, `cxgb4i_rx_credit_thres`, `cxgb4i_max_connect`, and `cxgb4i_sport_base`.

Important top-level integration objects are `cxgb4i_uld_info`, `cxgb4i_host_template`, and `cxgb4i_iscsi_transport`. `cxgb4i_uld_info` registers add, receive, and state callbacks with `cxgb4_register_uld()`. The SCSI host template delegates command execution and error handling to libiscsi helpers. The iSCSI transport delegates most session, connection, PDU, and endpoint operations to `libcxgbi.c`.

Connection setup and teardown are driven by `init_act_open()`, `send_act_open_req()`, `send_act_open_req6()`, `do_act_establish()`, `do_act_open_rpl()`, `send_close_req()`, `send_abort_req()`, `send_abort_rpl()`, `do_peer_close()`, `do_close_con_rpl()`, `do_abort_req_rss()`, and `do_abort_rpl_rss()`. These functions allocate ATIDs, resolve neighbours, program L2T entries, send active-open CPLs for IPv4/IPv6 and T4/T5/T6 formats, insert/remove TIDs, and update the common `cxgbi_sock` state machine.

Transmit data flow is built around `push_tx_frames()`, `send_tx_flowc_wr()`, `cxgb4i_make_tx_data_wr()`, and `cxgb4i_make_tx_iso_cpl()`. They convert queued iSCSI skbs into firmware offload work requests, manage WR credits, optionally emit FlowC context before first TX data, account digest bytes in TCP sequence space, and use ISO mode when the common layer prepared multi-PDU transmission.

Receive dispatch starts in `t4_uld_rx_handler()`, indexes `cxgb4i_cplhandlers[]`, and hands CPLs to functions such as `do_rx_iscsi_hdr()`, `do_rx_iscsi_data()`, `do_rx_data_ddp()`, `do_rx_iscsi_cmp()`, `do_fw4_ack()`, and `do_set_tcb_rpl()`. These functions annotate skb control blocks, maintain `rcv_nxt`, queue complete or partial PDUs to `csk->receive_queue`, report DDP/digest/padding status, and call `cxgbi_conn_pdu_ready()` once a PDU is ready for libiscsi consumption.

DDP setup is managed by `cxgb4i_ddp_init()`, `ddp_set_map()`, `ddp_ppod_write_idata()`, `ddp_setup_conn_pgidx()`, and `ddp_setup_conn_digest()`. These functions translate common page-pod metadata into Chelsio ULP memory writes and TCB updates.

## Control Flow

Module initialization calls `cxgbi_iscsi_init()` to register the iSCSI transport, then registers the Chelsio ULD. When the lower-layer driver adds an adapter, `t4_uld_add()` allocates a `cxgbi_device`, copies `cxgb4_lld_info` into private storage, sets adapter capabilities, initializes DDP, initializes offload callbacks, creates the source-port map, and adds one iSCSI HBA per physical port. It also reduces queue depth and disables ISO when the adapter lacks external memory, and enables ISO only on supported T5/T6 firmware.

For a new endpoint, the common library creates a `cxgbi_sock` and later calls this file's `init_act_open()` callback. That function validates address family, resolves a neighbour, allocates an ATID, grabs an L2T entry, selects queue/channel/MSS/window values, reserves WR credits, pins the module while the active-open is pending, sets `CTP_ACTIVE_OPEN`, and sends the appropriate active-open CPL. `do_act_establish()` handles success by inserting the hardware TID, freeing the ATID, setting initial send/receive sequence numbers and advertised MSS, transitioning to established state via `cxgbi_sock_established()`, and notifying libiscsi TX that the connection can transmit. `do_act_open_rpl()` handles negative advice, retry-on-existing-connection, TID removal, and open failure mapping to errno.

Transmit control flow starts in the common layer's `cxgbi_conn_xmit_pdu()`, which queues skbs on `csk->write_queue`. `push_tx_frames()` runs under the socket lock, checks connection state, computes WR credits from skb fragments and immediate/offload form, sends FlowC before first data, stops when credits are unavailable, constructs the TX_DATA or ISCSI_TX_DATA WR header, advances `snd_nxt`, enqueues the skb on the pending-WR list for later ACK reconciliation, installs an ARP error handler, and sends via `cxgb4_l2t_send()`. `do_fw4_ack()` returns credits to the common layer through `cxgbi_sock_rcv_wr_ack()`.

Receive control flow begins in the ULD RX callback. CPL handlers find `cxgbi_sock` by ATID or TID through the adapter TID table, validate state, prepare the skb by removing CPL headers, set receive flags such as `SKCBF_RX_HDR`, `SKCBF_RX_DATA`, `SKCBF_RX_STATUS`, `SKCBF_RX_ISCSI_COMPL`, and `SKCBF_RX_DATA_DDPD`, and queue skbs in an order expected by `cxgbi_conn_pdu_ready()`. Header/data/DDP/completion variants converge on `cxgbi_conn_pdu_ready()` once status is present. Unexpected raw `CPL_RX_DATA`, bad sequence, missing header, PDU length mismatch, and bad close-state receive paths abort the connection.

## State And Persistence Behavior

All state is in kernel memory and adapter firmware tables; there is no filesystem persistence. Persistent-for-connection state includes ATID/TID ownership, L2T/CLIP references, WR credit counters, pending WR list, receive and write queues, TCP sequence variables, digest sizes, DCB priority, retry timer, and page-pod/DDP metadata in the common `cxgbi_sock` and `cxgbi_ppm` structures. Module parameters persist only for the loaded module instance. Hardware state is programmed through CPL/firmware work requests and cleaned in `release_offload_resources()`, which frees CPL skbs, purges write and pending-WR queues, releases L2T and IPv6 CLIP entries, frees ATID or removes TID, and drops socket references.

## Dependencies And Integration Points

This file depends on the Chelsio `cxgb4` lower-layer driver, CPL/FW header definitions, L2T, CLIP, TID tables, adapter/register helpers, Linux SCSI/libiscsi/libiscsi_tcp, networking route/neighbour infrastructure, and optional DCB support. Its primary internal contract is `struct cxgbi_device`: `cxgb4i_ofld_init()` installs adapter-specific callbacks that `libcxgbi.c` calls for active open, close, abort, RX credits, TX push, CPL allocation, DDP digest/page-index setup, and DDP map writes. It also consumes `libcxgbi.h` skb control flags and socket state helpers.

## Risks

Credit accounting is a high-risk area: `push_tx_frames()` uses skb `csum` as a WR-credit count, combines FlowC and data credits, and relies on ACKs to free pending skbs. Any mismatch can leak skbs, stall transmission, or trip `cxgbi_sock_check_wr_invariants()`. Receive-side ordering is also sensitive: DDP/completion handlers must pair headers, data skbs, and completion status correctly or libiscsi will parse corrupt PDU streams. Active-open cleanup has multiple reference owners: ATID, TID, L2T, CLIP, module references, and socket krefs must be balanced across success, retry, ARP failure, and abort paths. Another risk is synchronous waits in DDP TCB setup (`wait_for_completion()`), which assume the adapter returns `CPL_SET_TCB_RPL`. ISO enable/disable depends on firmware version, memory presence, queue credits, and one-second retry throttling; regressions can cause throughput drops or repeated ENOBUFS/EAGAIN loops.

## Test Signals

Useful signals include module load/unload with ULD attach/detach, IPv4 and IPv6 iSCSI login/logout through Chelsio ports, active-open failure injection for ARP miss, TCAM full, duplicate connection, and timeout statuses, traffic with header/data digest combinations, DDP-enabled Data-In reads with aligned and unaligned SGLs, large Data-Out workloads that trigger ISO, low-credit transmission that forces backpressure, adapter recovery/detach while sessions are active, and DCB priority change events. Kernel logs from `dbg_level` categories, WR-credit invariant errors, iSCSI connection failures, digest errors, and SCSI error-handler paths are direct validation evidence.
