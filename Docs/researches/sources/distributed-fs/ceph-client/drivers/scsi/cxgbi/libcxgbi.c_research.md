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
