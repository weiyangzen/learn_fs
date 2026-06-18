<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/smc/smc_pnet.c -->
# sources/distributed-fs/ceph-client/net/smc/smc_pnet.c

Purpose: Implements SMC PNETID management and lookup. It backs the `smc_pnet` generic netlink family, stores user configured Ethernet/RDMA/ISM PNET table entries, tracks hardware PNETIDs from netdevices, and maps an established TCP handshake socket to usable SMC-R RoCE or SMC-D ISM resources.

Important APIs/types/functions: `struct smc_pnetentry` is the private list entry for PNET table rows, keyed either by Ethernet device name or by IB/ISM device name and port. `smc_pnet_init()`/`smc_pnet_exit()` register generic netlink operations and the netdevice notifier. `smc_pnet_net_init()`/`smc_pnet_net_exit()` initialize and destroy per-net `smc_pnettable` and `pnetids_ndev` lists. Netlink handlers `smc_pnet_add()`, `smc_pnet_del()`, `smc_pnet_get()`, `smc_pnet_dump()`, and `smc_pnet_flush()` expose add/delete/query/flush. Runtime lookup APIs include `smc_pnet_find_roce_resource()`, `smc_pnet_find_ism_resource()`, `smc_pnet_find_alt_roce()`, `smc_pnetid_by_table_ib()`, `smc_pnetid_by_table_smcd()`, `smc_pnet_is_ndev_pnetid()`, and `smc_pnet_is_pnetid_set()`.

Control flow: Add requests validate and uppercase PNETIDs, optionally attach an Ethernet entry to a live netdevice, and in `init_net` optionally apply the PNETID to matching IB/ISM devices if they do not already have hardware or user PNETIDs. Delete/flush walks the per-net table and, in `init_net`, clears matching user PNETIDs on global SMC-R and SMC-D devices. The netdevice notifier updates table references on register/unregister and maintains a reference-counted list of hardware PNETIDs for UP base devices. Resource lookup takes the route device from the TCP socket, collapses stacked devices to a base netdevice, gets a hardware or table PNETID, and scans active RDMA/ISM devices in the same namespace for a matching usable port/device.

State and persistence behavior: State is in memory only: per-net list entries protected by `pnettable->lock`, a per-net UP-netdevice PNETID list protected by rwlock, held netdevice references with `netdev_tracker`, and user-owned PNET flags in SMC device objects. Entries disappear on namespace exit or module exit.

Dependencies and integration points: Uses generic netlink UAPI from `uapi/linux/smc.h`, `netns/generic`, RDMA namespace checks, SMC IB/ISM/core device lists, hardware `pnet_id_by_dev_port()` when configured, route destination devices, and netdevice lifecycle notifications. It feeds SMC connection setup by filling `struct smc_init_info`.

Risks and test signals: Risk areas are netdevice reference lifetime, stacked-device base selection, only allowing global IB/ISM PNET table entries in `init_net`, races with device removal, and mismatch between hardware PNETIDs and table PNETIDs. Test with netlink add/get/dump/del/flush, net namespace table isolation, netdevice register/unregister/up/down, hardware PNETID discovery, SMC-R and SMC-D connection setup, alternate RoCE link selection, and concurrent device removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/smc/smc_pnet.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/smc/smc_pnet.h -->
# sources/distributed-fs/ceph-client/net/smc/smc_pnet.h

Purpose: Declares the SMC PNETID table data structures and exported lookup/lifecycle APIs used by SMC namespace setup, device discovery, and connection establishment.

Important APIs/types/functions: `struct smc_pnettable` contains the per-net PNET entry list and mutex. `struct smc_pnetids_ndev` and `struct smc_pnetids_ndev_entry` track unique PNETIDs observed on UP netdevices with a refcount per PNETID. `smc_pnetid_by_dev_port()` abstracts platform hardware PNET lookup, returning `-ENOENT` when `CONFIG_HAVE_PNETID` is absent. Public functions initialize/exit global and per-net PNET state, find SMC-R/SMC-D resources, apply table entries to new IB/SMCD devices, find alternate RoCE resources, and query PNETID presence.

Control flow: Callers initialize per-net state before PNET lookup, use `smc_pnet_find_roce_resource()` or `smc_pnet_find_ism_resource()` during handshake, and call device-table helpers when IB or SMCD devices appear. The inline hardware lookup selects either architecture support or a no-op fallback at compile time.

State and persistence behavior: The header defines state containers but does not allocate them. State is tied to `struct smc_net` and SMC device objects and is destroyed during namespace/device/module teardown.

Dependencies and integration points: Depends on `include/net/smc.h`, optional `asm/pnet.h`, and forward declarations for SMC IB, SMCD, init-info, and link-group structures. It is the boundary between PNET management and SMC core/handshake code.

Risks and test signals: The main risk is contract drift between table/list fields and implementation locking/refcount expectations. Build with and without `CONFIG_HAVE_PNETID`, exercise namespace init/exit, verify PNETID lookup on platforms without hardware support, and run SMC connection setup tests that require both SMC-R and SMC-D resource discovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/smc/smc_pnet.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/smc/smc_rx.c -->
# sources/distributed-fs/ceph-client/net/smc/smc_rx.c

Purpose: Implements receive-side SMC data handling. It copies or splices data from the local RMBE into user buffers/pipes, advances consumer cursors, handles urgent data, wakes readers, and sends CDC consumer updates to the peer.

Important APIs/types/functions: `smc_rx_recvmsg()` is the socket receive entry point under the socket lock. `smc_rx_wait()` blocks until data/error/shutdown/criterion. `smc_rx_init()` installs `sk_data_ready` and initializes splice and urgent state. Internal helpers include `smc_rx_wake_up()`, `smc_rx_update_consumer()`, `smc_rx_splice()`, `smc_rx_recv_urg()`, and `smc_rx_recvmsg_data_available()`.

Control flow: On receive, the code rejects unsupported error-queue reads, handles listen/not-connected and `MSG_OOB`, computes timeout and low-water target, then loops until the requested target is read or a stop condition occurs. It waits for `bytes_to_rcv`, handles shutdown/error rules, copies up to two ring-buffer chunks to `msghdr` or a pipe, syncs RMB memory for CPU access, decrements `bytes_to_rcv` for non-peek reads, advances the consumer cursor, and sends a CDC update when thresholds, urgent data, or peer requests require it. Splice buffers defer consumer cursor advancement until pipe buffer release.

State and persistence behavior: State lives in `struct smc_connection`: local consumer cursor, `bytes_to_rcv`, urgent state/cursor/byte, `splice_pending`, RMB descriptor and offsets, and CDC flags. Pipe buffer private state holds an SMC socket reference, page reference, and byte count until release.

Dependencies and integration points: Depends on SMC core cursor helpers, CDC update transmission via `smc_tx_consumer_update()`, socket wait queues and async wakeups, splice pipe APIs, tracepoints, and SMC stats. It is called by AF_SMC socket receive paths after CDC receive processing has made data visible.

Risks and test signals: Risks include ring wrap accounting, `MSG_PEEK` interaction with urgent data, splice lifetime/page ownership, memory barriers around `bytes_to_rcv`, and missed consumer updates causing sender stalls. Test normal reads, partial reads, `MSG_WAITALL`, nonblocking timeouts, shutdown/error behavior, urgent byte inline/non-inline, splice and pipe release, wrapped RMB buffers, SMC-R vmalloc RMBs, and CDC update threshold behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/smc/smc_rx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/smc/smc_rx.h -->
# sources/distributed-fs/ceph-client/net/smc/smc_rx.h

Purpose: Exposes the receive-side SMC entry points and the small data-availability helper used by AF_SMC socket code and peer CDC handling.

Important APIs/types/functions: `smc_rx_init()` installs receive callbacks and initializes connection receive state. `smc_rx_recvmsg()` receives into a userspace message or pipe. `smc_rx_wait()` waits on socket state plus caller-provided data criteria. `smc_rx_data_available()` returns `bytes_to_rcv - peeked` from the connection.

Control flow: Higher-level socket receive code calls `smc_rx_recvmsg()` under the socket lock. Other code can call `smc_rx_wait()` with either raw data availability or stricter criteria such as no pending splice bytes. The inline availability helper is used by both wait and receive loops.

State and persistence behavior: The header itself has no persistent state, but all functions operate on `struct smc_sock`/`struct smc_connection` receive counters, cursors, and socket wait queues.

Dependencies and integration points: Depends on Linux socket types and `smc.h`. It integrates with `smc_tx.h` through consumer updates implemented in the `.c` file and with socket receive operations in the AF_SMC layer.

Risks and test signals: Risks are mainly interface misuse: calling without expected socket locking, passing the wrong baseline for peeking, or ignoring splice-pending constraints. Test by compiling AF_SMC receive users and running read, peek, splice, timeout, and shutdown paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/smc/smc_rx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/smc/smc_stats.c -->
# sources/distributed-fs/ceph-client/net/smc/smc_stats.c

Purpose: Provides per-network-namespace SMC statistics allocation and generic-netlink dump handlers for aggregate SMC transport and fallback counters.

Important APIs/types/functions: `smc_stats_init()` allocates `net->smc.fback_rsn` and per-CPU `struct smc_stats`; `smc_stats_exit()` frees them. `smc_nl_get_stats()` folds per-CPU counters into one temporary `struct smc_stats` and emits nested SMC-D and SMC-R attributes. `smc_nl_get_fback_stats()` dumps server/client fallback reason counters incrementally. Helpers fill RMB counters, payload/RMB size histograms, and per-technology counters.

Control flow: Net namespace init allocates storage. Runtime macros in `smc_stats.h` update per-CPU fields and fallback arrays elsewhere. Netlink GET_STATS emits one multipart record and uses callback position to avoid repeating it. GET_FBACK_STATS walks fallback reason slots, emits server and client records when present, and tracks list position plus half-emitted server/client state in `cb_ctx->pos[]`.

State and persistence behavior: Stats are in-memory per-net state. Most counters are per-CPU and folded during dump without locking. Fallback reasons are protected by `net->smc.mutex_fback_rsn`. State is reset when the namespace exits.

Dependencies and integration points: Integrates with `smc_netlink.h` generic netlink family and UAPI attributes from `linux/smc.h`. It depends on all SMC paths using the macros consistently for handshake success/errors, payload byte counts, RMB sizes, and buffer pressure.

Risks and test signals: Risks include netlink message-size failures, inconsistent per-CPU aggregation if structure layout changes, partial fallback dump cursor bugs, and missing locking on fallback arrays. Test net namespace init failure unwind, stats dump with SMC-D and SMC-R traffic, fallback reason dumping across multipart boundaries, zero-counter dumps, and netlink attribute compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/smc/smc_stats.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/smc/smc_stats.h -->
# sources/distributed-fs/ceph-client/net/smc/smc_stats.h

Purpose: Defines SMC statistics structures and update macros used throughout AF_SMC for payload, RMB, handshake, fallback, urgent, splice, cork, and buffer-pressure accounting.

Important APIs/types/functions: `struct smc_stats` contains two `struct smc_stats_tech` entries for SMC-D and SMC-R plus handshake error counters. `struct smc_stats_tech` stores payload bytes/counts, buffer-size histograms, RMB counters, success counters, and feature counters. `struct smc_stats_rsn` stores client/server fallback reason arrays. Macros such as `SMC_STAT_TX_PAYLOAD`, `SMC_STAT_RX_PAYLOAD`, `SMC_STAT_RMB_SIZE`, `SMC_STAT_RMB_*`, `SMC_STAT_INC`, `SMC_STAT_CLNT_SUCC_INC`, and `SMC_STAT_SERV_SUCC_INC` update the current CPU's per-net counters.

Control flow: Call sites pass an SMC socket, size/result values, and SMC-D/SMC-R direction flags. Macros derive `sock_net(&smc->sk)`, select SMC-D when `conn.lnk` is absent, bucket lengths by powers over 8 KiB, and use `this_cpu_inc/add/sub` to avoid global contention.

State and persistence behavior: The header defines per-net, per-CPU in-memory accounting. Fallback arrays are shared per net namespace and require external synchronization by users. Counter values persist until namespace teardown or explicit process lifetime end; they are not stored on disk.

Dependencies and integration points: Depends on `linux/smc.h` UAPI constants and SMC CLC structures. Exported dump function declarations are implemented in `smc_stats.c` and wired into SMC netlink handling.

Risks and test signals: Macro risks include multiple evaluation mistakes, wrong SMC-D/SMC-R classification, unsigned underflow in RMB usage subtraction, and histogram bucket changes affecting userspace observability. Test with KASAN/lockdep builds, SMC-D and SMC-R transfer accounting, buffer add/remove symmetry, large payload buckets, fallback reason saturation, and netlink dumps after mixed traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/smc/smc_stats.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/smc/smc_sysctl.c -->
# sources/distributed-fs/ceph-client/net/smc/smc_sysctl.c

Purpose: Registers per-network-namespace `/proc/sys/net/smc` sysctls controlling SMC buffer sizes, SMC-R buffer layout, testlink timing, link-group limits, WR queue limits, handshake limiting, autocorking, and optional BPF handshake control selection.

Important APIs/types/functions: `smc_sysctl_net_init()` clones and retargets the ctl table for non-init namespaces, registers it, and initializes defaults. `smc_sysctl_net_exit()` unregisters and frees namespace-specific tables. When `CONFIG_SMC_HS_CTRL_BPF` is enabled, `smc_net_replace_smc_hs_ctrl()` atomically swaps an RCU-protected controller by name, and `proc_smc_hs_ctrl()` exposes it as a string sysctl.

Control flow: Init namespaces use the static `smc_table`; non-init namespaces kmemdup the table and adjust each `.data` pointer by the `struct net` offset from `init_net`. Optional handshake controllers can be inherited from `init_net` when marked inheritable and module references can be taken. Sysctl handlers enforce min/max constraints on selected integer tunables. Exit unregisters the table, clears BPF handshake control, and frees cloned tables.

State and persistence behavior: State is per `struct net->smc` and visible through procfs sysctl while the namespace exists. BPF handshake controller pointers are RCU protected and module refcounted. Values reset to defaults on namespace creation.

Dependencies and integration points: Depends on sysctl infrastructure, net namespaces, SMC core constants, LLC defaults, and optional SMC handshake BPF registry. TX autocorking and WR allocation consume these values at runtime.

Risks and test signals: Risks include pointer-retargeting mistakes in cloned ctl tables, teardown ordering of BPF controllers, invalid WR limits, and namespace inheritance surprises. Test init and non-init netns sysctl reads/writes, min/max rejection, namespace teardown, BPF controller set/clear/inherit behavior, and runtime effects on autocorking, buffer type, link-group limits, and WR queue sizing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/smc/smc_sysctl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/smc/smc_sysctl.h -->
# sources/distributed-fs/ceph-client/net/smc/smc_sysctl.h

Purpose: Declares SMC sysctl namespace lifecycle hooks and provides no-sysctl fallback initialization for key SMC tunables.

Important APIs/types/functions: With `CONFIG_SYSCTL`, `smc_sysctl_net_init()` and `smc_sysctl_net_exit()` are external functions. Without sysctl support, inline `smc_sysctl_net_init()` initializes defaults for autocorking, link-group limits, connection limits, and SMC-R WR queue sizes, while exit is a no-op.

Control flow: SMC net namespace setup calls the init function regardless of configuration. The preprocessor selects either procfs-backed registration or direct default assignment.

State and persistence behavior: State is stored in `net->smc` fields. In no-sysctl builds there is no runtime procfs persistence or user adjustment surface.

Dependencies and integration points: Depends on SMC constants from included code and `struct net`. It is consumed by SMC namespace initialization code and by runtime logic that reads the tunables.

Risks and test signals: Risk is default drift between the full sysctl implementation and the fallback inline path. Build both `CONFIG_SYSCTL=y` and `n`, verify defaults match expected operational values, and run connection setup and WR allocation under no-sysctl builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/smc/smc_sysctl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/smc/smc_tracepoint.c -->
# sources/distributed-fs/ceph-client/net/smc/smc_tracepoint.c

Purpose: Instantiates and exports the SMC tracepoints declared in `smc_tracepoint.h`.

Important APIs/types/functions: Defines `CREATE_TRACE_POINTS`, includes the tracepoint header, and exports `smc_switch_to_fallback`, `smc_tx_sendmsg`, `smc_rx_recvmsg`, and `smcr_link_down` with `EXPORT_TRACEPOINT_SYMBOL()`.

Control flow: At build time this single translation unit causes tracepoint definitions to be emitted. Other SMC files include the header normally and call generated trace functions without owning storage.

State and persistence behavior: No runtime state is maintained here beyond kernel tracepoint registration data generated by the tracing infrastructure.

Dependencies and integration points: Depends on Linux tracepoint generation rules and must remain the only C file defining `CREATE_TRACE_POINTS` for this trace system. Trace consumers include ftrace/perf/BPF tooling and SMC TX/RX/fallback/link-down paths.

Risks and test signals: Risks are duplicate tracepoint definition if another file defines `CREATE_TRACE_POINTS`, missing exports for modules, or header/name mismatch. Build with tracing enabled, load SMC as module if applicable, list events under tracing, and attach a BPF or ftrace consumer to each exported event.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/smc/smc_tracepoint.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/smc/smc_tracepoint.h -->
# sources/distributed-fs/ceph-client/net/smc/smc_tracepoint.h

Purpose: Declares SMC trace events for fallback, transmit, receive, and SMC-R link-down diagnostics.

Important APIs/types/functions: `TRACE_EVENT(smc_switch_to_fallback)` records SMC socket, CLC socket, net cookie, and fallback reason. `DECLARE_EVENT_CLASS(smc_msg_event)` and two `DEFINE_EVENT`s record TX/RX message length and device name. `TRACE_EVENT(smcr_link_down)` records link, link group, net cookie, link state, device name, and call-site location.

Control flow: SMC runtime code calls generated `trace_smc_*` helpers at important state transitions. The trace macros collect stable fields from socket/link structures and format them for trace buffers only when enabled.

State and persistence behavior: The header defines trace metadata, not SMC state. Emitted records are transient tracing data controlled by kernel tracing buffers.

Dependencies and integration points: Depends on `linux/tracepoint.h`, IPv6/TCP headers, and SMC core structures. `TRACE_INCLUDE_PATH` and `TRACE_INCLUDE_FILE` point trace generation to this header, while `smc_tracepoint.c` creates the definitions.

Risks and test signals: Risks include dereferencing fields that may be null in unusual fallback or link teardown states, format ABI churn visible to tracing tools, and missing net/device context for diagnosis. Test by enabling each event, forcing fallback, sending/receiving SMC-D and SMC-R data, triggering link-down paths, and validating trace fields under module builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/smc/smc_tracepoint.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/smc/smc_tx.c -->
# sources/distributed-fs/ceph-client/net/smc/smc_tx.c

Purpose: Implements SMC send-buffer producer and consumer logic. It copies user data into the local send ring, controls corking/autocorking, transfers data to peer RMBEs with SMC-R RDMA writes or SMC-D ISM writes, and emits CDC messages that advertise producer/cursor state.

Important APIs/types/functions: `smc_tx_sendmsg()` is the socket send entry point. `smc_tx_sndbuf_nonempty()` pushes prepared data to the peer. `smc_tx_pending()` and `smc_tx_work()` retry sends from process/workqueue context. `smc_tx_consumer_update()` sends receive-side consumer cursor updates. `smcd_tx_ism_write()` performs the SMC-D write primitive. Internal helpers manage write-space wakeups, send waits, cork decisions, RDMA/ISM ring chunking, and cursor advancement.

Control flow: The producer loop validates socket state, handles urgent flags, waits for `sndbuf_space`, copies up to two wrapped chunks from `msghdr` into the send buffer, syncs for device access, advances `tx_curs_prep`, decrements send space, and either corks or triggers the consumer. The consumer computes prepared bytes and peer RMBE space, sets write-blocked flags, breaks source and destination rings into chunks, posts RDMA writes for SMC-R or ISM writes for SMC-D, advances producer/sent cursors, then sends CDC. Completion/slot pressure can reschedule TX work.

State and persistence behavior: State is connection-local: send buffer descriptor, `sndbuf_space`, `peer_rmbe_space`, local and remote CDC controls, prepared/sent cursors, urgent flags, send lock, delayed work, link pointer, and stats. No disk persistence exists.

Dependencies and integration points: Depends on socket wait queues, TCP cork state via the underlying CLC socket, SMC CDC, SMC WR slot management, SMC close wakeups, SMC-D ISM APIs, sysctl autocorking, stats, and tracepoints.

Risks and test signals: Risks include cursor wrap errors, peer RMBE window underflow, urgent-data state bugs, link-change races while holding WR slots, corking latency, and missed wakeups for `EPOLLOUT`. Test blocking/nonblocking sends, partial sends, `MSG_MORE`/TCP_CORK/autocorking, urgent data, SMC-D attached buffers, SMC-R inline and non-inline RDMA, peer window exhaustion/reopen, link failover, and close while data is prepared.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/smc/smc_tx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/smc/smc_tx.h -->
# sources/distributed-fs/ceph-client/net/smc/smc_tx.h

Purpose: Declares SMC transmit entry points and exposes the prepared-send cursor helper used to decide whether data is waiting for transfer.

Important APIs/types/functions: `smc_tx_prepared_sends()` computes the difference between `tx_curs_sent` and `tx_curs_prep` in the send buffer ring. Public functions initialize TX callbacks, send user messages, push nonempty send buffers, wake producers when space returns, send consumer updates, run deferred TX work, and perform SMC-D ISM writes.

Control flow: Send paths call `smc_tx_sendmsg()` to stage bytes, then `smc_tx_sndbuf_nonempty()`/`smc_tx_pending()` to transmit staged bytes. Receive paths call `smc_tx_consumer_update()` after consuming RMB data. Workqueue code invokes `smc_tx_work()` when a send could not complete immediately.

State and persistence behavior: The header does not own state; it operates on `struct smc_connection` cursors, buffer descriptors, link-group transport type, and socket callbacks.

Dependencies and integration points: Depends on socket types, SMC core definitions, and CDC cursor/control structures. It bridges AF_SMC socket code, RX consumer updates, CDC, SMC-D, and SMC-R WR code.

Risks and test signals: Risks are stale cursor differences or callers invoking APIs without required socket/send locking. Test compile users, prepared-send detection across wrap, RX-triggered consumer updates, SMC-D write callers, and deferred TX work after WR slot pressure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/smc/smc_tx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/smc/smc_wr.c -->
# sources/distributed-fs/ceph-client/net/smc/smc_wr.c

Purpose: Owns SMC-R RDMA work-request infrastructure for LLC/CDC sends, RDMA write helpers, receive queue demultiplexing, completion processing, memory allocation, DMA mapping, and link teardown coordination.

Important APIs/types/functions: `struct smc_wr_tx_pend` tracks pending send WRs. TX APIs include `smc_wr_tx_get_free_slot()`, `smc_wr_tx_get_v2_slot()`, `smc_wr_tx_put_slot()`, `smc_wr_tx_send()`, `smc_wr_tx_v2_send()`, `smc_wr_tx_send_wait()`, `smc_wr_reg_send()`, and `smc_wr_tx_wait_no_pending_sends()`. RX APIs include `smc_wr_rx_register_handler()`, `smc_wr_rx_post_init()`, and CQ handlers. Lifecycle APIs allocate/free link and link-group memory, remember QP attributes, create links, and setup/kill device tasklets.

Control flow: Senders reserve a bitmap slot, fill a WR buffer and pending context, then post to the QP. Send CQ interrupts schedule a tasklet, which polls completions, finds the pending slot by WR ID, clears buffers/masks, wakes waiters, invokes completion handlers, and schedules link-down on fatal status. Receive CQ tasklets poll completions, locate the RX buffer by WR ID modulo queue size, demultiplex by SMC message type through a handler hash, repost receive WRs, or schedule link-down on retry/flush errors. Link creation maps buffers for DMA, initializes SGEs/IB WRs, wait queues, completions, and percpu references.

State and persistence behavior: State is per link and per device: WR IDs, pending arrays, masks, buffers, SGEs, IB WR descriptors, DMA addresses, v2 shared buffers, wait queues, tasklets, registration state, and percpu references. It is in-memory and must be drained/unmapped before link/device destruction.

Dependencies and integration points: Depends on RDMA ib verbs, SMC core link/link-group state, SMC CDC/LLC handlers registered elsewhere, tasklets for CQ bottom halves, DMA mapping APIs, and link-down scheduling.

Risks and test signals: Risks include WR slot leaks, completion races, use-after-free during link teardown, incorrect v2 large-buffer clearing, DMA map/unmap imbalance, RX handler registration order, and missed CQ notifications. Test high WR slot pressure, send-wait timeouts, MR registration success/failure, CQ error statuses, RX repost failures, SMC-Rv2 large messages, link teardown with pending WRs, and RDMA device removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/smc/smc_wr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/smc/smc_wr.h -->
# sources/distributed-fs/ceph-client/net/smc/smc_wr.h

Purpose: Declares SMC-R work-request constants, callback types, inline helpers, and public WR lifecycle/TX/RX APIs.

Important APIs/types/functions: Defines `SMC_WR_TX_WAIT_FREE_SLOT_TIME`, `SMC_WR_TX_SIZE`, and `SMC_WR_TX_PEND_PRIV_SIZE`. `struct smc_wr_tx_pend_priv` is opaque completion context storage. Callback typedefs cover TX completion, filtering, and dismissal. `struct smc_wr_rx_handler` maps receive message types to handlers. Inline helpers generate WR IDs, manage link percpu references, wake/drain wait queues, and post receive WRs by WR ID modulo queue size.

Control flow: Callers allocate/create link WR resources, reserve TX slots, send WRs, optionally wait for completion, register RX handlers, post initial receives, and free resources at teardown. `smc_wr_rx_post()` increments the tasklet-context RX ID and posts the next receive buffer to the QP.

State and persistence behavior: No standalone state is owned by the header. Its helpers mutate per-link WR IDs, references, waits, and IB receive WR descriptors.

Dependencies and integration points: Depends on RDMA ib verbs, SMC core structures, and `smc.h`. It is used by CDC, LLC, TX, link setup, and device lifecycle code.

Risks and test signals: Risks include using `smc_wr_rx_post()` outside its expected serialization, failing to hold `wr_tx_refs` around sends, and mismatching pending private storage size with users. Test compile-time users, RX queue wrap, reference kill/drain during teardown, WR slot reservation/release, and SMC-Rv2 slot usage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/smc/smc_wr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/socket.c -->
# sources/distributed-fs/ceph-client/net/socket.c

Purpose: Implements the Linux socket top-level VFS, syscall, protocol-family registry, sockfs, ancillary data, ioctl, compat, and in-kernel socket helper layer. It is the main bridge between file descriptors/user memory and protocol `proto_ops`.

Important APIs/types/functions: Core objects include `socket_file_ops`, sockfs inode/xattr handlers, `net_families[]`, and `sock_inode_cachep`. Exported helpers include `sock_alloc_file()`, `sock_from_file()`, `sockfd_lookup()`, `sock_alloc()`, `sock_release()`, `sock_sendmsg()`, `sock_recvmsg()`, `kernel_sendmsg()`, `kernel_recvmsg()`, `sock_register()`, `sock_unregister()`, `get_user_ifreq()`, `put_user_ifreq()`, and kernel bind/listen/accept/connect/name/shutdown/IP-overhead helpers. Syscall internals cover socket/socketpair/bind/listen/accept/connect/getname/send/recv/setsockopt/getsockopt/shutdown/sendmsg/sendmmsg/recvmsg/recvmmsg/socketcall.

Control flow: Socket creation validates family/type, runs LSM hooks, allocates a sockfs inode/socket, module-loads and RCU-resolves a protocol family, calls its `create`, holds protocol module refs, and maps the socket to a file descriptor. File operations translate read/write/poll/ioctl/splice/mmap/fasync/close into `proto_ops`. Send/recv paths import user buffers/iovecs, copy addresses/control messages, apply nonblocking flags, run LSM/BPF cgroup hooks, and dispatch to protocol methods. Batched send/recv loops maintain partial-success semantics and update user message lengths.

State and persistence behavior: Global state includes the protocol-family RCU table, sockfs mount, inode cache, ioctl hooks, and optional busy-poll sysctls. Per-socket state is held in sockfs inodes, files, wait queues, fasync lists, xattrs, module references, and protocol-owned `sock` objects. State is in-memory and released on close/module/namespace teardown.

Dependencies and integration points: Integrates with VFS, fd tables, pseudo filesystems, LSM, audit, BPF cgroup sockopt hooks, io_uring, netdevice ioctls, bridge/VLAN/wireless hooks, timestamping/PTP, netfilter init, procfs, compat syscalls, and every registered network protocol including PF_SMC.

Risks and test signals: Risks include user-copy length mistakes, address truncation semantics, module/RCU lifetime bugs, partial batch error reporting, compat ifreq conversion, timestamp ancillary corner cases, sockopt BPF rewrite behavior, and close/fasync races. Test with syscall suites for all socket operations, LSM/audit/BPF enabled, compat 32-bit ioctls, sendmmsg/recvmmsg partial failures/timeouts, timestamping error queue, protocol module load/unload, sockfs xattrs, splice/io_uring, and PF_SMC creation through the generic path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/socket.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/strparser/Kconfig -->
# sources/distributed-fs/ceph-client/net/strparser/Kconfig

Purpose: Defines the kernel configuration symbol controlling compilation of the stream parser module.

Important APIs/types/functions: `config STREAM_PARSER` is a boolean with `def_bool n`; it is normally selected by consumers rather than prompted directly.

Control flow: Kconfig evaluation leaves stream parser disabled unless another feature selects or enables `STREAM_PARSER`. The Makefile then compiles `strparser.o` only when this symbol is set.

State and persistence behavior: No runtime state exists. The symbol persists only in the kernel build configuration.

Dependencies and integration points: Integrates with `net/strparser/Makefile` and consumers such as TLS/KCM/BPF stream parser users that require framed stream parsing.

Risks and test signals: Risk is missing selection by a consumer, causing link failures or unavailable stream parsing. Test relevant configurations with consumers enabled and disabled, and verify `strparser.o` appears only when expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/strparser/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/strparser/Makefile -->
# sources/distributed-fs/ceph-client/net/strparser/Makefile

Purpose: Hooks the stream parser implementation into the kernel build.

Important APIs/types/functions: `obj-$(CONFIG_STREAM_PARSER) += strparser.o` builds `strparser.c` when the Kconfig symbol is enabled.

Control flow: Kbuild expands the conditional object list from the configuration. No additional subdirectories or composite objects are involved.

State and persistence behavior: No runtime state. Build output depends solely on `CONFIG_STREAM_PARSER`.

Dependencies and integration points: Integrates with `net/strparser/Kconfig` and the main networking Makefile inclusion chain.

Risks and test signals: Risk is accidental omission or wrong object name causing consumers to fail at link time. Test builds with `CONFIG_STREAM_PARSER=y/m` where supported and with consumers selecting it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/strparser/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/strparser/strparser.c -->
# sources/distributed-fs/ceph-client/net/strparser/strparser.c

Purpose: Implements the generic stream parser framework that converts a byte stream or supplied skb fragments into complete message skbs according to upper-layer callbacks.

Important APIs/types/functions: Exported APIs are `strp_init()`, `strp_process()`, `strp_data_ready()`, `strp_unpause()`, `strp_done()`, `strp_stop()`, and `strp_check_rcv()`. Core internals include `__strp_recv()`, `strp_read_sock()`, `strp_parser_err()`, `strp_abort_strp()`, `strp_msg_timeout()`, and workqueue callbacks. `strp_wq` is the single-thread workqueue used for deferred parsing.

Control flow: `strp_init()` validates callbacks and sets default socket lock/unlock and abort/read_done handlers. In socket mode, `strp_data_ready()` either parses immediately under lower socket conditions or queues work if the socket is owned by user context or memory pressure occurs. `strp_read_sock()` pulls data through either callback or socket `read_sock`, which calls `__strp_recv()`. The parser clones/appends skbs, asks `parse_msg` for full length, starts a timeout while waiting for header/body, rejects oversized or bad lengths, and calls `rcv_msg` when a complete message is assembled. General mode uses `strp_process()` directly on supplied skb ranges.

State and persistence behavior: `struct strparser` tracks stopped/paused flags, current `skb_head`, append pointer, needed bytes, timeout work, parser work, stats, callbacks, and lower socket pointer. State is in-memory and must be stopped before `strp_done()` cancels work and frees partial skb chains.

Dependencies and integration points: Depends on skb control-buffer layout from `include/net/strparser.h`, socket `peek_len`/`read_sock`, workqueues, timers, and upper-layer parse/receive callbacks. Used by stream protocols that need message framing over TCP-like transports.

Risks and test signals: Risks include skb frag-list ownership mistakes, parse callback returning inconsistent lengths, timeout races, pause/unpause memory ordering, socket lock ordering, and skb `cb[]` overlay size. Test partial header/body delivery, multiple messages in one skb, message spanning fragments, oversized/bad lengths, pause/unpause, timeout abort, no-socket general mode, memory allocation failures, and `BUILD_BUG_ON` for control-buffer size.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/strparser/strparser.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sunrpc/Kconfig -->
# sources/distributed-fs/ceph-client/net/sunrpc/Kconfig

Purpose: Defines SUNRPC, RPC security, backchannel, swap, debugging, test, and RPC-over-RDMA configuration symbols used by NFS/RPC subsystems.

Important APIs/types/functions: `SUNRPC` and `SUNRPC_GSS` are tristate foundations gated by `MULTIUSER`. `RPCSEC_GSS_KRB5` selects Kerberos GSS support and crypto dependencies. AES-SHA1, Camellia-CMAC, and AES-SHA2 enctype symbols add crypto-specific support. `RPCSEC_GSS_KRB5_KUNIT_TEST` enables KUnit tests. `SUNRPC_DEBUG` and `SUNRPC_DEBUG_TRACE` expose debug controls. `SUNRPC_XPRT_RDMA` builds RPC-over-RDMA and selects `SG_POOL`.

Control flow: Kconfig dependency resolution controls whether SUNRPC core, auth_gss, Kerberos mechanisms, debug objects, proc/sysctl support, and RDMA transport objects are built. Defaults enable common Kerberos AES-SHA1 and RDMA when base requirements are available.

State and persistence behavior: No runtime state is stored here. Choices persist in the kernel configuration and determine which code and modules are built.

Dependencies and integration points: Integrates with NFS client/server code, crypto subsystem, OID registry, KUnit, tracing, debugfs/sysctl, InfiniBand address translation, and `net/sunrpc/Makefile`.

Risks and test signals: Risks include unmet crypto dependencies disabling expected security mechanisms, debug trace option flooding trace buffers, and RDMA defaults on systems without RDMA. Test representative configs: SUNRPC built-in/module, Kerberos with each enctype, debug on/off, KUnit, and RPC-over-RDMA enabled/disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sunrpc/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sunrpc/Makefile -->
# sources/distributed-fs/ceph-client/net/sunrpc/Makefile

Purpose: Defines the SUNRPC kernel objects and conditional subdirectories built by Kbuild.

Important APIs/types/functions: `obj-$(CONFIG_SUNRPC) += sunrpc.o`, `obj-$(CONFIG_SUNRPC_GSS) += auth_gss/`, and `obj-$(CONFIG_SUNRPC_XPRT_RDMA) += xprtrdma/`. The `sunrpc-y` composite includes client, transport, socket, scheduler, auth, service, address, rpcbind, timer, XDR, cache, pipe, sysfs, service transport, and multipath objects. Conditional additions include debugfs, backchannel, proc stats, and sysctl.

Control flow: Kbuild links the listed objects into `sunrpc.o` when SUNRPC is enabled and descends into selected subdirectories for GSS and RDMA support.

State and persistence behavior: No runtime state. It controls build composition and module contents.

Dependencies and integration points: Mirrors symbols from `net/sunrpc/Kconfig` and wires `addr.o` into the core SUNRPC object, making the address conversion helpers available to RPC clients/servers.

Risks and test signals: Risks include missing object dependencies when Kconfig symbols change, conditional objects not matching feature code, and module link failures. Test allmodconfig/allyesconfig plus minimal SUNRPC builds, debug/proc/sysctl toggles, and RDMA/GSS module combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sunrpc/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sunrpc/addr.c -->
# sources/distributed-fs/ceph-client/net/sunrpc/addr.c

Purpose: Converts SUNRPC socket addresses between kernel `sockaddr` structures, presentation IP strings, and rpcbind/NFS universal address strings.

Important APIs/types/functions: Exported functions are `rpc_ntop()`, `rpc_pton()`, and `rpc_uaddr2sockaddr()`; `rpc_sockaddr2uaddr()` is also globally visible in this file. IPv4 helpers use `%pI4` and `in4_pton`. IPv6 helpers handle compressed formatting, v4-mapped addresses, optional link-local scope IDs, and `in6_pton`. Universal address helpers append or parse RPCBIND port bytes as `.hibyte.lobyte`.

Control flow: `rpc_ntop()` switches by address family and formats IPv4 or IPv6, including scope ID only for link-local IPv6 with a nonzero scope. `rpc_pton()` selects IPv6 when the input contains `:`; otherwise IPv4. IPv6 parse validates scope delimiters and resolves device names in the provided net namespace or numeric scope IDs. `rpc_sockaddr2uaddr()` formats address plus port bytes, excluding IPv6 scope IDs. `rpc_uaddr2sockaddr()` copies and terminates the supplied string, parses trailing two dot-separated port bytes, parses the remaining address, and writes the network-order port into the resulting sockaddr.

State and persistence behavior: Stateless conversion helpers. Temporary buffers are stack allocated except `rpc_sockaddr2uaddr()`, which returns a caller-owned `kstrdup()` allocation.

Dependencies and integration points: Depends on IPv4/IPv6 parser helpers, netdevice lookup for IPv6 scopes, SUNRPC rpcbind limits, and exported GPL symbols used by SUNRPC transport/rpcbind code.

Risks and test signals: Risks include buffer truncation returning zero, ambiguous colon-based IPv6 detection, scope ID parsing with namespaces, universal address malformed port bytes, and IPv6-disabled builds returning zero for IPv6. Test IPv4, IPv6 compressed, any, loopback, v4-mapped, link-local with numeric and device scopes, max-length universal addresses, malformed ports, small output buffers, and IPv6-disabled configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sunrpc/addr.c -->
