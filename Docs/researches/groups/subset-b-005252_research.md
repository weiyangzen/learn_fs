# subset-b-005252 research

Work item: `subset-b-005252`

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/cxgbi/cxgb4i/cxgb4i.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/cxgbi/cxgb4i/cxgb4i.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/cxgbi/cxgb4i/cxgb4i.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/cxgbi/cxgb4i/cxgb4i.h

## Purpose

`cxgb4i.h` is the small adapter-specific public header for the Chelsio T4/T5/T6 iSCSI driver. It centralizes driver limits and transmit-header sizing used by `cxgb4i.c`, keeping the adapter module's constants separate from the common `libcxgbi` library.

## Important APIs, Types, And Functions

The header defines constants rather than functions or structs. `CXGB4I_SCSI_HOST_QDEPTH` sets the SCSI host queue depth to 1024. `CXGB4I_MAX_CONN` caps connections at 16384, and `CXGB4I_MAX_TARGET` mirrors that limit. `CXGB4I_MAX_LUN` sets the maximum LUN count to `0x1000`. `CXGB4I_TX_HEADER_LEN` computes the reserved skb transmit headroom required for a firmware offload TX_DATA work request plus the SGE opaque header. `T5_ISS_VALID` is a T5/T6 active-open option bit used when sending an initial send sequence value.

## Control Flow

The header has no runtime control flow. Its values feed `cxgb4i.c`: the host template uses queue and LUN limits; ULD/device initialization clamps the maximum connection count and sizes per-host resources; transmit PDU allocation uses the header length through `cdev->skb_tx_rsvd`; and T5/T6 active-open request construction sets `T5_ISS_VALID`.

## State And Persistence Behavior

There is no mutable state. The constants influence in-memory kernel object sizes, queue limits, and skb layout while the module is loaded. No value is persisted outside the loaded driver and adapter state created by the implementation file.

## Dependencies And Integration Points

`CXGB4I_TX_HEADER_LEN` depends on Chelsio firmware and SGE structures (`struct fw_ofld_tx_data_wr` and `struct sge_opaque_hdr`) being visible to the translation unit that includes the header. The limit constants integrate with Linux SCSI host sizing, libiscsi session sizing, and Chelsio TID/resource sizing in `cxgb4i.c`.

## Risks

The primary risk is size drift: if firmware WR or SGE header structures change and `CXGB4I_TX_HEADER_LEN` is not sufficient, transmit skbs can lack headroom when `cxgbi_sock_tx_queue_up()` prepares offload WRs. Connection and queue constants must also remain compatible with adapter TID limits; `cxgb4i.c` mitigates this by clamping against hardware TID counts, but oversized defaults still affect memory allocation and advertised host capacity.

## Test Signals

Compile coverage is the main signal for this header. Runtime signals include successful skb allocation and TX header push without headroom errors, host queue depth visible through SCSI/iSCSI host attributes, and connection-count clamping behavior during adapter registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/cxgbi/cxgb4i/cxgb4i.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/cxgbi/libcxgbi.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/cxgbi/libcxgbi.c

## Purpose

`libcxgbi.c` is the common Chelsio iSCSI offload library shared by adapter drivers. It owns `cxgbi_device` registration, HBA creation, source-port allocation, route validation, socket lifecycle state transitions, PDU receive delivery into `libiscsi_tcp`, PDU transmit skb assembly from SCSI scatterlists, DDP tag/page-pod reservation, iSCSI endpoint/session/connection binding, and exported helper APIs consumed by adapter-specific modules such as `cxgb4i.c`.

## Important APIs, Types, And Functions

Device/HBA exports include `cxgbi_device_register()`, `cxgbi_device_unregister()`, `cxgbi_device_unregister_all()`, `cxgbi_device_find_by_lldev()`, `cxgbi_device_find_by_netdev()`, `cxgbi_device_find_by_netdev_rcu()`, `cxgbi_hbas_add()`, `cxgbi_hbas_remove()`, `cxgbi_device_portmap_create()`, and `cxgbi_device_portmap_cleanup()`. These maintain global device lists, RCU lookup state, per-port `Scsi_Host` instances, and source-port maps.

Socket lifecycle exports include `cxgbi_sock_established()`, `cxgbi_sock_closed()`, `cxgbi_sock_fail_act_open()`, `cxgbi_sock_act_open_req_arp_failure()`, `cxgbi_sock_rcv_abort_rpl()`, `cxgbi_sock_rcv_peer_close()`, `cxgbi_sock_rcv_close_conn_rpl()`, `cxgbi_sock_rcv_wr_ack()`, `cxgbi_sock_select_mss()`, `cxgbi_sock_skb_entail()`, `cxgbi_sock_purge_wr_queue()`, `cxgbi_sock_check_wr_invariants()`, and `cxgbi_sock_free_cpl_skbs()`.

PDU and DDP exports include `cxgbi_conn_tx_open()`, `cxgbi_conn_pdu_ready()`, `cxgbi_conn_alloc_pdu()`, `cxgbi_conn_init_pdu()`, `cxgbi_conn_xmit_pdu()`, `cxgbi_cleanup_task()`, `cxgbi_parse_pdu_itt()`, `cxgbi_ddp_ppm_setup()`, and `cxgbi_ddp_set_one_ppod()`. iSCSI transport exports include `cxgbi_get_conn_stats()`, `cxgbi_set_conn_param()`, `cxgbi_get_ep_param()`, `cxgbi_create_conn()`, `cxgbi_bind_conn()`, `cxgbi_create_session()`, `cxgbi_destroy_session()`, `cxgbi_set_host_param()`, `cxgbi_get_host_param()`, `cxgbi_ep_connect()`, `cxgbi_ep_poll()`, `cxgbi_ep_disconnect()`, `cxgbi_iscsi_init()`, `cxgbi_iscsi_cleanup()`, and `cxgbi_attr_is_visible()`.

## Control Flow

Module initialization allocates a zeroed reserved page for iSCSI padding and asserts that `sk_buff.cb` can hold `struct cxgbi_skb_cb`. Adapter drivers register `cxgbi_device` instances; this library links them into a mutex-protected list and an RCU list, creates per-port iSCSI HBAs, and later tears everything down on unregister.

Endpoint connect begins in `cxgbi_ep_connect()`. It validates the optional requested SCSI host, resolves IPv4/IPv6 routes through `cxgbi_check_route()` or `cxgbi_check_route6()`, rejects multicast/broadcast/down interfaces, maps the netdev to a Chelsio device by netdev or MAC, creates a `cxgbi_sock`, allocates a source port from the rotor map, and calls the adapter's `csk_init_act_open()` callback. If active-open succeeds, it creates an `iscsi_endpoint` with `cxgbi_endpoint` data. Poll simply reports whether the socket reached `CTP_ESTABLISHED`.

Session and connection flow is layered on libiscsi. `cxgbi_create_session()` calls `iscsi_session_setup()` with task private storage large enough for `iscsi_tcp_task` plus `cxgbi_task_data`, then allocates the R2T pool. `cxgbi_create_conn()` uses `iscsi_tcp_conn_setup()`. `cxgbi_bind_conn()` looks up the endpoint, programs DDP page-size index through the adapter callback, binds libiscsi state, links `cxgbi_conn`, `cxgbi_endpoint`, and `cxgbi_sock`, computes data segment limits, and prepares the TCP receive engine.

Transmit flow starts with `cxgbi_conn_alloc_pdu()`, which reserves/sets ITT tags, inspects SCSI command direction, prepares scatterlist fragment metadata, optionally expands a transfer into ISO multi-PDU form, and allocates an skb with adapter-reserved headroom. `cxgbi_conn_init_pdu()` copies or references payload pages into skb frags, adds padding from `rsvd_page`, sets digest submode, restores negotiated max-xmit length after ISO adjustments, and prepares ISO metadata when needed. `cxgbi_conn_xmit_pdu()` writes pending page pods if DDP was deferred to the offload queue, copies non-SCSI headers into the skb, sends through `cxgbi_sock_send_skb()`, updates iSCSI transmit octet counters, and handles credit backpressure by preserving the skb for retry.

Receive flow is adapter-driven. CPL handlers queue skbs and call `cxgbi_conn_pdu_ready()` when a PDU has status. This function drains ready skbs, feeds headers and data into `iscsi_tcp_recv_skb()`, handles coalesced, split header/data, DDP-offloaded, and completion forms, returns RX credits when thresholds are reached, updates `rxdata_octets`, and fails the iSCSI connection on protocol or digest errors.

DDP flow begins when `task_reserve_itt()` sees a SCSI read. `cxgbi_ddp_reserve()` validates DDP availability, transfer size, page-size index, SGL alignment, reserves page pods from the PPM, maps the SGL for DMA, builds a page-pod header, and either marks the pods for deferred offload-queue write or asks the adapter to write them immediately. Completion cleanup in `task_release_itt()` detects DDP tags, clears hardware maps when needed, releases pods, and unmaps DMA.

## State And Persistence Behavior

All state is in memory. Global device lists are protected by `cdev_mutex` and `cdev_rcu_lock`; registered devices own port arrays, HBA arrays, adapter callbacks, and PPM/DDP resources. The source-port map stores live `cxgbi_sock` pointers indexed by `sport_base + idx` and holds socket references until `sock_put_port()`. Each `cxgbi_sock` owns state machine state, flags, reference count, queues, completion, timer, route/dst, addresses, sequence numbers, digest lengths, and adapter-owned handles. Each iSCSI task has transient `cxgbi_task_data` for skb, SGL fragments, DDP tag info, offsets, counts, and ISO state. Persistent hardware state is mediated by adapter callbacks and cleaned during socket close/task cleanup; nothing is written to disk.

## Dependencies And Integration Points

The file depends on Linux SCSI, libiscsi, libiscsi_tcp, networking route/neighbour APIs, IPv6 route/source-address helpers, VLAN handling, PCI reference management, skbuff/page-frag/scatterlist/DMA APIs, and `libcxgb_ppm` page-pod management. Adapter drivers supply callbacks in `struct cxgbi_device` for active open, close, abort, RX credits, TX push, CPL allocation, DDP digest/page-index setup, page-pod map writes, and offload resource release. The iSCSI transport callback table in adapter code points back into these exported functions.

## Risks

Reference ownership is complex across endpoints, sockets, source-port map entries, routes, HBAs, TID/ATID resources, and libiscsi objects. A missed put or early close can leak sockets or free adapter resources while callbacks still run. DDP correctness depends on SGL alignment, DMA map/unmap symmetry, tag age/index encoding, page-pod reservation/release, and adapter map clearing; failures can corrupt SCSI read placement or leak DMA mappings. Receive parsing is sensitive to skb flag combinations supplied by adapter CPL handlers; wrong flags can cause header/data mismatches or duplicate credit return. Transmit retry logic must preserve `tdata->skb` only for retryable backpressure and clear it on successful handoff. The source-port map currently rejects non-zero source ports and assumes in-range ports belong to its rotor, so changes to user-specified source binding require careful redesign. `cxgbi_ep_poll()` ignores `timeout_ms` and only samples state, so callers depend on external polling cadence.

## Test Signals

Useful validation includes route selection over real, VLAN, loopback, IPv4, and IPv6 devices; failed route and down-link cases; endpoint connect/bind/disconnect under normal logout and abrupt failure; source-port exhaustion and reuse; SCSI read workloads with DDP enabled and disabled; unaligned SGL fallback to non-DDP; SCSI write workloads with fragmented and copied payloads; negotiated digest combinations; max segment length negotiation boundaries; RX coalesced/split/DDP completion paths; TX backpressure with retry; session teardown ensuring R2T pool, skb, DDP, DMA, and socket state are released; and module unload with live devices. Kernel log signatures include iSCSI connection failures, digest errors, DDP full counters, WR invariant warnings, and route/device lookup failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/cxgbi/libcxgbi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/cxgbi/libcxgbi.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/cxgbi/libcxgbi.h

## Purpose

`libcxgbi.h` defines the shared contract between Chelsio iSCSI adapter drivers and the common `libcxgbi` implementation. It contains debug infrastructure, protocol sizing constants, skb control-block layout, socket/device/HBA/endpoint/task/ISO data structures, state and flag enums, inline helpers for reference/queue/state handling, adapter callback slots, and exported function prototypes.

## Important APIs, Types, And Functions

Important constants describe iSCSI offload sizing: `SKB_TX_ISCSI_PDU_HEADER_MAX`, `ISCSI_PDU_NONPAYLOAD_LEN`, `ULP2_MAX_PKT_SIZE`, `ULP2_MAX_PDU_PAYLOAD`, `CXGBI_ULP2_MAX_ISO_PAYLOAD`, `CXGBI_MAX_ISO_DATA_IN_SKB`, and `cxgbi_align_pdu_size()`. `cxgbi_ulp_extra_len()` reports TCP sequence-space bytes consumed by hardware-inserted header/data digests.

`struct cxgbi_sock` is the central per-offloaded-connection object. It stores adapter identity, TID/ATID, flags, MTU/MSS/RSS/queue/channel state, WR credits, digest lengths, L2T pointer, preallocated CPL skbs, pending ULP header skb, queues, timer, completion, callback data, address unions, route, TCP sequence/window values, and ISO throttling state. `enum cxgbi_sock_states` and `enum cxgbi_sock_flags` define the connection state machine and close/abort/resource flags.

`struct cxgbi_skb_cb` overlays `sk_buff.cb` and is split into RX metadata (`ddigest`, `pdulen`) and TX metadata (`handle`, `arp_err_handler`, `wr_next`, `iscsi_hdr_len`, `ulp_mode`) plus shared flags and TCP sequence. `enum cxgbi_skcb_flags` marks TX header need, memory-write WRs, completion requests, RX header/data/status/DDP/digest/padding conditions, and ISO TX. Inline helpers set/clear/test skb flags and expose control fields.

Other key structs are `cxgbi_hba`, `cxgbi_ports_map`, `cxgbi_device`, `cxgbi_conn`, `cxgbi_endpoint`, `cxgbi_task_data`, and `cxgbi_iso_info`. `cxgbi_device` is the adapter-neutral object with port/HBA arrays and callback slots that adapter drivers populate. `cxgbi_task_data` extends libiscsi TCP tasks with SGL fragment state, skb ownership, transfer offsets, and DDP tag info. `cxgbi_iso_info` is written into reserved skb headroom for adapter ISO work requests.

## Control Flow

The header itself has no standalone runtime flow, but its inline helpers are on hot paths. Socket state is changed by `cxgbi_sock_set_state()`. References are managed through `cxgbi_sock_get()` and `cxgbi_sock_put()`, which wrap `kref` and free with `cxgbi_sock_free()`. Write-request bookkeeping uses `cxgbi_sock_reset_wr_list()`, `cxgbi_sock_enqueue_wr()`, `cxgbi_sock_count_pending_wrs()`, `cxgbi_sock_peek_wr()`, and `cxgbi_sock_dequeue_wr()`. Adapter and common code cooperate through function pointers inside `struct cxgbi_device`: common code calls adapter-specific open/close/abort/TX/RX-credit/DDP operations, while adapter code calls exported common functions for state transitions and PDU delivery.

## State And Persistence Behavior

The header defines in-memory state layouts only. No persistent storage is involved. It does, however, define ownership-relevant fields: socket krefs, queue heads, skbs that must be freed or handed off exactly once, TID/ATID flags that imply hardware table ownership, source-port-map entries, DMA/DDP tag information, and callback pointers into libiscsi. Because these structures are shared across interrupt/softirq, worker, and libiscsi contexts, their lock fields (`spinlock_t`, `rwlock_t`, completion, timer) are part of the state contract.

## Dependencies And Integration Points

The header includes Linux kernel, debugfs, list, netdevice, VLAN, scatterlist, skbuff, vmalloc, SCSI, libiscsi_tcp, and `libcxgb_ppm` definitions. It is included by both common and adapter-specific Chelsio iSCSI code. It also depends on `sk_buff.cb` being large enough for `struct cxgbi_skb_cb`, which `libcxgbi.c` checks at module init. The public prototypes are the API surface used by `cxgb4i.c` and potentially other Chelsio iSCSI adapter drivers.

## Risks

The largest risk is ABI-like coupling through shared structs and skb control blocks. Any field layout or flag semantic change must be coordinated across common and adapter code. The write-pending list stores WR credit counts in `skb->csum`, so helpers assume all enqueued WR skbs follow that convention. `cxgbi_sock_free()` only frees the socket memory; callers must release CPL skbs, route, L2T, TID/ATID, port-map, queues, DMA, and DDP resources before the final put. Inline state setters do not enforce legal transitions, so implementation code must maintain the state machine.

## Test Signals

Compile-time coverage should catch missing dependencies and struct/control-block sizing. Runtime signals include stable socket reference counts across connect/close/abort, WR queue invariant checks, correct skb flag interpretation by receive and transmit paths, successful DDP tag lifecycle, and no crashes under adapter detach or iSCSI session teardown. Because this header defines the shared contract, cross-driver build and load tests are especially valuable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/cxgbi/libcxgbi.h -->
