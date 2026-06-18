<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rds/send.c -->
# sources/distributed-fs/ceph-client/net/rds/send.c

## Purpose
Implements the core RDS transmit path: user `sendmsg()` validation, RDS message allocation and ancillary control parsing, connection/path selection, queueing onto socket and connection queues, transport-driven transmission, ACK-based cleanup, cancellation, and probe/ping messages used by handshake and multipath negotiation.

## Important APIs, Types, and Functions
Key exported entry points are `rds_send_path_reset()`, `rds_send_xmit()`, `rds_rdma_send_complete()`, `rds_atomic_send_complete()`, `rds_send_path_drop_acked()`, `rds_send_drop_acked()`, and `rds_send_ping()`. The file centers on `struct rds_conn_path`, `struct rds_connection`, `struct rds_sock`, `struct rds_message`, `struct rm_rdma_op`, `struct rm_atomic_op`, `struct rds_notifier`, and transport callbacks in `struct rds_transport`. Local helpers include `acquire_in_xmit()`, `release_in_xmit()`, `rds_mprds_cp0_catchup()`, `rds_send_remove_from_sock()`, `rds_send_queue_rm()`, `rds_rm_size()`, `rds_cmsg_send()`, and `rds_send_probe()`.

## Control Flow
`rds_sendmsg()` rejects unsupported flags, validates IPv4/IPv6 destinations and scope IDs, enforces bound-source compatibility, computes RDMA payload size, allocates a message large enough for data scatterlists plus cmsg state, copies or pins payload data, finds or creates an outgoing connection, selects a multipath lane, parses SOL_RDS cmsgs, waits on congestion, queues the message, and invokes `rds_send_xmit()`. `rds_send_xmit()` serializes each path with `RDS_IN_XMIT`, checks connection state, optionally sends a congestion map update, moves queued messages to the retransmit list, marks periodic ACK requirements, runs RDMA/atomic/data transport transmit callbacks, updates partial header/data offsets, drops non-retransmittable flushed or RDMA-retransmitted messages, and reschedules when work remains or the lower layer reports temporary backpressure. ACK processing moves retransmit-list entries to a private list and then removes them from the owning socket queue outside the connection lock.

## State and Persistence
Transmit state is in `cp_xmit_rm`, `cp_xmit_sg`, `cp_xmit_hdr_off`, `cp_xmit_data_off`, `cp_xmit_*_sent`, `cp_send_queue`, `cp_retrans`, `cp_next_tx_seq`, `cp_unacked_packets`, `cp_unacked_bytes`, and `cp_send_gen`. Socket send-buffer accounting is `rs_snd_bytes` plus `rs_send_queue`. Message flags such as `RDS_MSG_ON_CONN`, `RDS_MSG_ON_SOCK`, `RDS_MSG_ACK_REQUIRED`, `RDS_MSG_RETRANSMITTED`, `RDS_MSG_MAPPED`, and `RDS_MSG_HAS_ACK_SEQ` coordinate ownership and lifetime. No durable persistence is written; state is in kernel memory and is reset on path shutdown, socket close, or connection destruction.

## Dependencies and Integration
Depends on RDS connection, congestion, message, RDMA, atomic, and transport helpers declared through `rds.h`. TCP, IB, or other transports provide `xmit`, `xmit_rdma`, `xmit_atomic`, `xmit_path_prepare`, `xmit_path_complete`, and ACK classification. It integrates with socket sleeping/wakeup, sysctls for max unacked packets/bytes, global RDS stats, multipath negotiation extensions, and zero-copy support for TCP-only `MSG_ZEROCOPY`.

## Risks and Test Signals
Risk is concentrated in lock ordering across `rs_lock`, `cp_lock`, and `m_rs_lock`, message reference balancing between socket and connection queues, partial-send progress tracking, and reconnect races around `RDS_IN_XMIT`. Multipath ordering depends on lane 0 catch-up and source-port path hashing. Test signals should include blocking and nonblocking send-buffer exhaustion, ACK cleanup for TCP sequence wrap, RDMA/atomic notifier completion and cancellation, retransmission after reset, congestion-map sends, zero-length ping/probe messages, IPv4/IPv6 scope validation, and multipath lane fan-out without out-of-order delivery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rds/send.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rds/stats.c -->
# sources/distributed-fs/ceph-client/net/rds/stats.c

## Purpose
Exports global RDS runtime counters through the RDS info interface and provides the shared formatting helper used by transport-specific statistics.

## Important APIs, Types, and Functions
Defines and exports per-CPU `struct rds_statistics rds_stats`. `rds_stats_info_copy()` formats counter names and values as `struct rds_info_counter` records. `rds_stats_init()` registers `RDS_INFO_COUNTERS`, and `rds_stats_exit()` deregisters it. The local `rds_stats_info()` callback sums per-CPU counters and appends transport-specific stats through `rds_trans_stats_info_copy()`.

## Control Flow
When an RDS info request asks for counters, `rds_stats_info()` converts byte length to entry capacity, sums all online CPU counter slots into a local aggregate, copies named global counters if the caller supplied enough room, then delegates remaining capacity to transports. The result lengths report a fixed record size and a total count that includes transport counters even when the caller had insufficient buffer space.

## State and Persistence
State is per-CPU, cacheline-aligned, volatile counter memory. It persists only for the lifetime of the module or built-in subsystem and is reset by boot or module reload.

## Dependencies and Integration
Depends on the RDS info registry, per-CPU counter macros, online CPU iteration, and transport registration. The counter names must stay in field order with `struct rds_statistics` for the cast-and-sum logic to remain correct.

## Risks and Test Signals
Risks include counter-name drift from structure layout, buffer-size under-reporting, and CPU hotplug snapshot races inherent in unlocked per-CPU summation. Test signals are correct `RDS_INFO_COUNTERS` sizing, stable counter names, nonzero increments from send/receive paths, and appended TCP transport counters when `rds_tcp` is registered.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rds/stats.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rds/sysctl.c -->
# sources/distributed-fs/ceph-client/net/rds/sysctl.c

## Purpose
Defines the global `/proc/sys/net/rds` controls for reconnect backoff, ACK cadence, and ping behavior used by the RDS core.

## Important APIs, Types, and Functions
Exports runtime variables `rds_sysctl_reconnect_min_jiffies`, `rds_sysctl_reconnect_max_jiffies`, `rds_sysctl_max_unacked_packets`, `rds_sysctl_max_unacked_bytes`, and `rds_sysctl_ping_enable`. `rds_sysctl_init()` initializes and registers the table under init_net, and `rds_sysctl_exit()` unregisters it.

## Control Flow
The sysctl table uses `proc_doulongvec_ms_jiffies_minmax` for reconnect delays and `proc_dointvec` for ACK/ping integer controls. Init converts the minimum reconnect delay from milliseconds to jiffies before registration. Writes mutate the exported globals directly, so reconnect scheduling and send ACK pacing pick up new values without restart.

## State and Persistence
State is global kernel memory exposed through sysctl. It is not per-netns in this file and is not persisted across reboot unless user space reapplies settings.

## Dependencies and Integration
Used by `threads.c` reconnect backoff and by `send.c` to set `cp_unacked_packets` and `cp_unacked_bytes`. Depends on sysctl/proc support and RDS core initialization order.

## Risks and Test Signals
Risks include invalid tuning that can increase reconnect storms or ACK pressure, plus global rather than per-netns scope. Test signals are sysctl registration at `net/rds`, min/max enforcement for reconnect delays, live effect on reconnect worker delay growth, and ACK-required frequency changes during sustained sends.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rds/sysctl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rds/tcp.c -->
# sources/distributed-fs/ceph-client/net/rds/tcp.c

## Purpose
Registers and owns the RDS TCP transport, including per-net namespace listen sockets and sysctls, TCP socket callback replacement/restoration, transport allocation/free, transport info export, unload handling, and lifecycle teardown.

## Important APIs, Types, and Functions
Defines `struct rds_transport rds_tcp_transport` and `int rds_tcp_netid`. Important functions include `rds_tcp_write_seq()`, `rds_tcp_snd_una()`, `rds_tcp_set_callbacks()`, `rds_tcp_reset_callbacks()`, `rds_tcp_restore_callbacks()`, `rds_tcp_laddr_check()`, `rds_tcp_tune()`, `rds_tcp_accept_work()`, pernet callbacks `rds_tcp_init_net()` and `rds_tcp_exit_net()`, sysctl handlers for `rds_tcp_sndbuf` and `rds_tcp_rcvbuf`, and module init/exit. Internal lists `rds_tcp_tc_list` and `rds_tcp_conn_list` track active callback-installed sockets and allocated TCP transport objects.

## Control Flow
Module init creates the TCP connection slab, initializes receive allocation, registers pernet state, registers the RDS transport, and registers TCP socket info providers. Per-net init creates a netns-private sysctl table, then creates an IPv6 listener or falls back to IPv4. Connection allocation creates one `struct rds_tcp_connection` per multipath lane, attaches each to an `rds_conn_path`, and links all objects on the global cleanup list. Callback setup saves original TCP callbacks, stores the RDS path in `sk_user_data`, installs RDS data-ready/write-space/state-change hooks, and adds the object to the info list. Reset handles dueling SYN cases by forcing path state to resetting, waiting out transmitters, cancelling send/recv work, restoring and releasing the old socket, resetting RDS send state, then installing callbacks on the new socket. Exit marks unloading, drains RCU, deregisters info and pernet state, destroys connections, unregisters transport, exits receive support, and destroys the slab.

## State and Persistence
Global state includes active TCP connection lists, counts for IPv4 and IPv6 info reporting, unloading flag, and the connection slab. Per-net `struct rds_tcp_net` stores accept lock, listen socket, one stashed accepted socket, accept work, sysctl header/table, and configured socket buffer sizes. Per-connection state lives in `struct rds_tcp_connection`. All state is runtime-only.

## Dependencies and Integration
Integrates the generic RDS transport API with kernel TCP sockets, net namespaces, sysctl, RDS info, RDS workqueue, and IPv6 address checks. The transport supplies send, receive, connect, shutdown, local-address validation, stats, and path-slot callbacks used by the RDS core.

## Risks and Test Signals
Risks include callback restoration races, stale sockets during netns teardown, incorrect list count updates, sysctl-triggered reconnect storms, and deadlocks if reset waits while holding a socket lock in the wrong order. Test signals are module load/unload, per-net listener creation and fallback, sysctl writes causing connection drops and reconnects, `RDS_INFO_TCP_SOCKETS`/`RDS6_INFO_TCP_SOCKETS` counts, dueling SYN reset, and clean netns deletion with no leaked sockets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rds/tcp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rds/tcp.h -->
# sources/distributed-fs/ceph-client/net/rds/tcp.h

## Purpose
Declares the private interface and state shared by the RDS TCP transport implementation files.

## Important APIs, Types, and Functions
Defines `RDS_TCP_PORT` as 16385, `struct rds_tcp_net`, `struct rds_tcp_incoming`, `struct rds_tcp_connection`, and `struct rds_tcp_statistics`. It declares transport entry points from `tcp.c`, `tcp_connect.c`, `tcp_listen.c`, `tcp_recv.c`, `tcp_send.c`, and `tcp_stats.c`, plus the `rds_tcp_stats_inc()` wrapper over the generic per-CPU stats helper.

## Control Flow
The header has no executable control flow, but it encodes module boundaries: connection allocation attaches a `struct rds_tcp_connection` to every `rds_conn_path`, receive code fills `struct rds_tcp_incoming`, pernet code owns `struct rds_tcp_net`, and send/listen/connect files call across the declared interfaces.

## State and Persistence
Structures define runtime-only state: accept serialization, listener and accepted sockets, sysctl values, partial incoming header/data tracking, original TCP callbacks, active socket info fields, client source-port group, and receive-drain waitqueue.

## Dependencies and Integration
Depends on RDS core types, kernel sockets, skb queues, work structs, wait queues, and sysctl types. This header is the integration contract that keeps the TCP transport split across smaller compilation units.

## Risks and Test Signals
Risks include stale prototypes after implementation changes and fields whose ownership is split across callback, workqueue, and teardown paths. Test signals are clean compile coverage for all TCP transport files, CFI/prototype consistency, and behavior that exercises each declared callback path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rds/tcp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rds/tcp_connect.c -->
# sources/distributed-fs/ceph-client/net/rds/tcp_connect.c

## Purpose
Implements active TCP connection establishment, TCP state-change handling, and orderly TCP path shutdown for the RDS TCP transport.

## Important APIs, Types, and Functions
Exports `rds_tcp_state_change()`, `rds_tcp_conn_path_connect()`, and `rds_tcp_conn_path_shutdown()`. It uses `struct rds_conn_path`, `struct rds_connection`, `struct rds_tcp_connection`, kernel socket creation/bind/connect/shutdown APIs, and helpers from `tcp.c`, `tcp_send.c`, and RDS core state management.

## Control Flow
`rds_tcp_conn_path_connect()` refuses secondary multipath lanes until negotiation established multiple paths, serializes with `t_conn_path_lock`, creates an IPv4 or IPv6 TCP socket, tunes it, binds to the local RDS address using a source port whose low bits encode `cp_index`, installs callbacks before nonblocking connect, and keeps the socket on success. `rds_tcp_state_change()` reacts to TCP transitions: established connections either complete RDS path connect or are dropped when address ordering says the peer should reconnect, closing states wake shutdown waiters and drop the path. `rds_tcp_conn_path_shutdown()` sends `SHUT_WR`, repeatedly drains inbound data while waiting up to about five seconds for a closing TCP state and empty receive queue, drops messages already ACKed at TCP level, restores callbacks, releases the socket, and resets partial incoming state.

## State and Persistence
State includes `t_sock`, `t_client_port_group`, `t_recv_done_waitq`, partial incoming tracking, RDS path state, and TCP sequence fields used by ACK cleanup. It is all in-memory and bound to the connection path lifetime.

## Dependencies and Integration
Integrates with TCP state machine callbacks, RDS path transitions, RDS workqueue reconnect policy, multipath source-port encoding, address ordering from `rds_addr_cmp()`, keepalive setup from listen code, and ACK cleanup from `tcp_send.c`/`send.c`.

## Risks and Test Signals
Risks include dueling connect races, source-port exhaustion, waiting too long or not long enough during shutdown drain, callback ownership after failed connect, and IPv6 link-local scope handling. Test signals include simultaneous active connects from both peers, reconnect after RST, multipath lane ports modulo worker count, shutdown with queued receive data, and no callback invocation after socket release.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rds/tcp_connect.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rds/tcp_listen.c -->
# sources/distributed-fs/ceph-client/net/rds/tcp_listen.c

## Purpose
Owns passive TCP listener setup, accept scheduling, accepted socket validation, multipath lane-slot selection, and listener teardown for RDS over TCP.

## Important APIs, Types, and Functions
Key functions are `rds_tcp_keepalive()`, `rds_tcp_conn_slots_available()`, `rds_tcp_accept_one()`, `rds_tcp_listen_data_ready()`, `rds_tcp_listen_init()`, and `rds_tcp_listen_stop()`. Local helpers include `rds_tcp_get_peer_sport()` and `rds_tcp_accept_one_path()`.

## Control Flow
`rds_tcp_listen_init()` creates an IPv4 or IPv6 kernel TCP listener on `RDS_TCP_PORT`, enables reuse and nodelay, replaces the listener data-ready callback, binds wildcard address, and listens with backlog 64. `rds_tcp_listen_data_ready()` queues accept work only for the listen socket and chains to the original callback. `rds_tcp_accept_one()` accepts or reuses a stashed socket, applies keepalive/tuning, derives local and peer addresses, rejects local-address peers except loopback cases, creates or finds an RDS connection, resolves address-ordering rules, assigns an available path based on source-port modulo when supported, installs callbacks, marks the path up, queues receive work, and sends a probe when path count is still unknown. If all slots are busy, it stashes the accepted socket to avoid losing already ACKed data.

## State and Persistence
Per-net state includes the listen socket, accept lock, accept work, and one `rds_tcp_accepted_sock` retained across `-ENOBUFS`. Per-connection state is the target `struct rds_tcp_connection` selected for an accepted path. No persistent storage is used.

## Dependencies and Integration
Depends on kernel accept/listen APIs, TCP keepalive tuning, RDS connection creation, path state transitions, multipath handshake state, netns private `rds_tcp_net`, and the common callback installation functions in `tcp.c`.

## Risks and Test Signals
Risks include losing data if an accepted socket is dropped while no path slot is free, accepting the wrong side of a dueling SYN, source-port/path mismatch during fan-out, listener callback teardown races, and netns deletion with pending accept work. Test signals are incoming connection storms, no-slot stashing and later replay, IPv6 and IPv4 listener fallback, loopback/self-connect rejection behavior, and clean listener stop while data-ready fires.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rds/tcp_listen.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rds/tcp_recv.c -->
# sources/distributed-fs/ceph-client/net/rds/tcp_recv.c

## Purpose
Adapts TCP byte streams into complete RDS incoming messages, including partial header/data reassembly, congestion bitmap updates, skb-backed payload retention, copy-to-user support, and receive callback scheduling.

## Important APIs, Types, and Functions
Exports `rds_tcp_inc_free()`, `rds_tcp_inc_copy_to_user()`, `rds_tcp_recv_path()`, `rds_tcp_data_ready()`, `rds_tcp_recv_init()`, and `rds_tcp_recv_exit()`. Internal helpers include `rds_tcp_inc_purge()`, `rds_tcp_cong_recv()`, `rds_tcp_data_recv()`, and `rds_tcp_read_sock()`.

## Control Flow
`rds_tcp_data_ready()` runs under the TCP callback lock, reads available data with `GFP_ATOMIC`, and queues receive work if allocation fails. The worker path locks the socket and retries with `GFP_KERNEL`. `rds_tcp_data_recv()` is the `tcp_read_sock()` descriptor callback: it allocates a `struct rds_tcp_incoming` when needed, copies header bytes until complete, records payload length, clones payload ranges into an skb list, and when header and data are complete either applies a congestion bitmap or passes the incoming message to `rds_recv_incoming()`. Complete messages reset header/data counters and drop the incoming reference.

## State and Persistence
Receive state is `t_tinc`, `t_tinc_hdr_rem`, `t_tinc_data_rem`, and each incoming object's `ti_skb_list`. The remote congestion map pages are mutated when receiving `RDS_FLAG_CONG_BITMAP`. State is volatile and cleared on path shutdown or incoming free.

## Dependencies and Integration
Depends on TCP `tcp_read_sock()`, skb copy/extract helpers, RDS incoming lifetime helpers, congestion map updates, socket callback locking, and the TCP incoming kmem cache. It integrates with RDS receive delivery and userspace copyout through the transport `inc_copy_to_user` callback.

## Risks and Test Signals
Risks include partial-read state corruption, allocation failure in callback context, malformed congestion-map sizes, skb clone lifetime, and shutdown races with the receive queue. Test signals are fragmented headers, fragmented payloads across many skbs, zero-length messages, congestion bitmap exact-size updates, allocation-failure fallback to worker, copy-to-user over multi-skb payloads, and receive-drain wakeups during shutdown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rds/tcp_recv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rds/tcp_send.c -->
# sources/distributed-fs/ceph-client/net/rds/tcp_send.c

## Purpose
Implements the TCP transport's data transmit callback, TCP ACK interpretation, socket corking around batched sends, and write-space callback that drives ACK cleanup and send retry.

## Important APIs, Types, and Functions
Exports `rds_tcp_xmit_path_prepare()`, `rds_tcp_xmit_path_complete()`, `rds_tcp_xmit()`, `rds_tcp_is_acked()`, and `rds_tcp_write_space()`. Local helper `rds_tcp_sendmsg()` sends header bytes with `kernel_sendmsg()`.

## Control Flow
Before a send batch, `rds_tcp_xmit_path_prepare()` enables TCP cork; completion disables it. `rds_tcp_xmit()` records the TCP sequence corresponding to the last byte of the RDS message when starting a header, sets `RDS_MSG_HAS_ACK_SEQ`, sends remaining header bytes, then sends each data scatterlist with `MSG_SPLICE_PAGES`, `MSG_DONTWAIT`, `MSG_NOSIGNAL`, and `MSG_MORE` where appropriate. `-EAGAIN` is treated as temporary backpressure and converted to no-progress; other errors drop the path if it is still up. `rds_tcp_write_space()` records `snd_una`, drops RDS messages whose stored TCP ack sequence is before the unacked pointer, queues send work when space is available, chains to the original callback, and restores `SOCK_NOSPACE` so future TCP ACKs continue to trigger callbacks.

## State and Persistence
Uses TCP `write_seq` and `snd_una` to populate `t_last_sent_nxt`, `t_last_expected_una`, `t_last_seen_una`, and each message's `m_ack_seq`. It mutates socket flags and message flags but has no durable persistence.

## Dependencies and Integration
Depends on kernel TCP send APIs, splice-pages send support, RDS generic send partial-offset contract, RDS ACK cleanup, TCP stats counters, and callback state saved by `tcp.c`.

## Risks and Test Signals
Risks include 32-bit TCP sequence wrap comparisons, partial header/data accounting, page-backed send failures, repeated `SOCK_NOSPACE` callback dependence, and incorrectly treating fatal TCP errors as transient. Test signals are partial sends, `-EAGAIN` retries, ACK cleanup at sequence wrap, send-space wakeups under full sndbuf, retransmitted header flag setting, and path drop on non-EAGAIN send errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rds/tcp_send.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rds/tcp_stats.c -->
# sources/distributed-fs/ceph-client/net/rds/tcp_stats.c

## Purpose
Provides per-CPU RDS TCP transport counters and the transport stats export callback used by the generic RDS counter interface.

## Important APIs, Types, and Functions
Defines per-CPU `struct rds_tcp_statistics rds_tcp_stats` and `rds_tcp_stats_info_copy()`. The exported counter names are `tcp_data_ready_calls`, `tcp_write_space_calls`, `tcp_sndbuf_full`, `tcp_connect_raced`, and `tcp_listen_closed_stale`.

## Control Flow
`rds_tcp_stats_info_copy()` checks available entry capacity, sums all online CPU counter slots into a local aggregate, and formats the results through `rds_stats_info_copy()`. It always returns the number of TCP stats entries so the caller can report total required length.

## State and Persistence
State is per-CPU runtime counter memory, reset on module unload or boot.

## Dependencies and Integration
Depends on `tcp.h` for the statistics structure and on the generic RDS stats formatter from `stats.c`. Registered indirectly through `rds_tcp_transport.stats_info_copy`.

## Risks and Test Signals
Risks mirror global stats: structure/name ordering must remain aligned and snapshots are approximate under concurrent updates. Test signals include counter increments from data-ready/write-space callbacks and visibility through `RDS_INFO_COUNTERS` after TCP transport registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rds/tcp_stats.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rds/threads.c -->
# sources/distributed-fs/ceph-client/net/rds/threads.c

## Purpose
Provides the shared RDS workqueue and worker functions that serialize connection management, send retry, receive retry, shutdown, reconnect backoff, and address ordering.

## Important APIs, Types, and Functions
Defines exported `struct workqueue_struct *rds_wq`, `rds_connect_path_complete()`, `rds_connect_complete()`, and `rds_addr_cmp()`. Worker functions are `rds_connect_worker()`, `rds_send_worker()`, `rds_recv_worker()`, and `rds_shutdown_worker()`. Init/exit are `rds_threads_init()` and `rds_threads_exit()`. Reconnect scheduling is handled by `rds_queue_reconnect()`.

## Control Flow
Successful connect transitions a path to `RDS_CONN_UP`, queues congestion map send and receive work, clears reconnect delay, and resets protocol proposal state. Reconnect scheduling uses an initial immediate attempt followed by randomized exponential backoff capped by sysctl max, while TCP peers with the larger address defer initiation to avoid dueling connects. Send and receive workers only run while the path is up, invoke transport callbacks, and reschedule immediately for `-EAGAIN` or after a short delay for `-ENOMEM`. The shutdown worker delegates to `rds_conn_shutdown()`.

## State and Persistence
State lives in per-path delayed works, `cp_state`, `cp_flags`, `cp_reconnect_jiffies`, and global `rds_wq`. No durable persistence is used.

## Dependencies and Integration
Depends on RDS connection state helpers, transport callback tables, sysctl reconnect values, random bytes, RCU destroy-pending checks, and the singlethread workqueue named `krdsd`.

## Risks and Test Signals
Risks include reconnect livelock, workqueue serialization bottlenecks, address-comparison asymmetry across architectures, and missed retries if destroy-pending races are mishandled. Test signals are transition coverage for DOWN/CONNECTING/UP/DISCONNECTING/ERROR, randomized reconnect delay growth, TCP address-order deferral, send/recv retry stats, and correct IPv6 comparison for both aligned 64-bit and fallback 32-bit paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rds/threads.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rds/transport.c -->
# sources/distributed-fs/ceph-client/net/rds/transport.c

## Purpose
Maintains the registry of RDS transports, handles lazy module loading, chooses preferred transports for local addresses, releases transport module references, and aggregates transport-specific stats.

## Important APIs, Types, and Functions
Exports `rds_trans_register()`, `rds_trans_unregister()`, `rds_trans_put()`, `rds_trans_get_preferred()`, and `rds_trans_get()`. `rds_trans_stats_info_copy()` is used by stats export. State is `transports[RDS_TRANS_COUNT]`, `rds_trans_modules[]`, and `rds_trans_sem`.

## Control Flow
Registration validates transport name length and installs one transport per type under write lock. Lookup by type first checks the registry, drops the read lock to `request_module()` if a known module is absent, then reacquires the lock and takes a module reference. Preferred lookup returns the loopback transport for loopback addresses; otherwise it scans registered transports and selects the first whose `laddr_check()` succeeds and whose module reference can be acquired. Stats aggregation unmaps the info iterator, walks registered transports under read lock, and lets each transport copy as many counters as available.

## State and Persistence
The registry is runtime global memory protected by an rwsem. Module references persist until released by callers through `rds_trans_put()`.

## Dependencies and Integration
Depends on module loading, IPv6/IPv4 address helpers, RDS loopback transport, transport callback structures, and RDS info iterator utilities.

## Risks and Test Signals
Risks include module reference leaks, out-of-range transport type callers, duplicate registration, and preferred-transport ambiguity when multiple transports accept the same local address. Test signals are lazy loading of `rds_tcp`, loopback preference, duplicate registration logging, transport unregister during module unload, and stats aggregation across registered transports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rds/transport.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rfkill/Kconfig -->
# sources/distributed-fs/ceph-client/net/rfkill/Kconfig

## Purpose
Declares build-time configuration for the RF switch subsystem, optional LED/input integrations, and the generic GPIO rfkill platform driver.

## Important APIs, Types, and Functions
Defines `RFKILL` as tristate, `RFKILL_LEDS` as a dependent bool, `RFKILL_INPUT` as an optional/default input bridge, and `RFKILL_GPIO` as a tristate GPIO driver. It uses dependencies on `LEDS_TRIGGERS`, `INPUT`, `GPIOLIB`, and `COMPILE_TEST`.

## Control Flow
Kconfig selection controls which objects the Makefile builds. Enabling `RFKILL` builds the core. LED trigger support defaults on when compatible. Input support defaults on outside expert mode when input is available. GPIO support remains opt-in and depends on GPIO library or compile testing.

## State and Persistence
No runtime state is present. Configuration choices persist in the kernel build configuration.

## Dependencies and Integration
Connects rfkill to the kernel device model, input layer, LED trigger framework, and GPIO platform driver build.

## Risks and Test Signals
Risks include invalid dependency combinations hiding expected functionality or building optional integration without its provider. Test signals are Kconfig dependency resolution for built-in/module combinations, allmodconfig coverage, and `RFKILL_INPUT`/`RFKILL_LEDS` matching their provider availability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rfkill/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rfkill/Makefile -->
# sources/distributed-fs/ceph-client/net/rfkill/Makefile

## Purpose
Maps RFKILL Kconfig symbols to object files for the core rfkill module and GPIO driver.

## Important APIs, Types, and Functions
Builds `rfkill-y += core.o`, conditionally adds `input.o` through `rfkill-$(CONFIG_RFKILL_INPUT)`, builds the aggregate `rfkill.o` for `CONFIG_RFKILL`, and builds `rfkill-gpio.o` for `CONFIG_RFKILL_GPIO`.

## Control Flow
The kernel build system links `core.o` and optional `input.o` into the rfkill module or built-in object. The GPIO platform driver is independent and only built when selected.

## State and Persistence
No runtime state; the file defines build artifacts.

## Dependencies and Integration
Integrates with Kbuild and the symbols declared in `Kconfig`. It ensures input support is part of the core rfkill object rather than a separate module.

## Risks and Test Signals
Risks are limited to build omissions when object lists fall out of sync with source or Kconfig. Test signals are successful builds for `RFKILL=y/m`, `RFKILL_INPUT=y/n`, and `RFKILL_GPIO=y/m`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rfkill/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rfkill/core.c -->
# sources/distributed-fs/ceph-client/net/rfkill/core.c

## Purpose
Implements the rfkill core: driver-facing rfkill device allocation/registration/state APIs, global software-state and emergency power-off handling, sysfs attributes, uevents, optional LED triggers, polling, suspend/resume behavior, and the `/dev/rfkill` userspace ABI.

## Important APIs, Types, and Functions
Defines private `struct rfkill`, event wrapper `struct rfkill_int_event`, and per-file-descriptor `struct rfkill_data`. Exported APIs include `rfkill_alloc()`, `rfkill_register()`, `rfkill_unregister()`, `rfkill_destroy()`, `rfkill_set_hw_state_reason()`, `rfkill_set_sw_state()`, `rfkill_init_sw_state()`, `rfkill_set_states()`, `rfkill_blocked()`, `rfkill_soft_blocked()`, `rfkill_find_type()`, `rfkill_pause_polling()`, and `rfkill_resume_polling()`. Under input support it also provides `rfkill_switch_all()`, `rfkill_epo()`, `rfkill_restore_states()`, `rfkill_remove_epo_lock()`, `rfkill_is_epo_lock_active()`, and `rfkill_get_global_sw_state()`.

## Control Flow
Drivers allocate an object with `rfkill_alloc()`, optionally initialize persistent software state, then call `rfkill_register()`, which assigns an index, adds the device, registers LED triggers, starts polling, syncs global state, and emits add events. State changes flow through `rfkill_set_block()` for user/global requested software changes, `rfkill_set_hw_state_reason()` for hardware blocks, or direct setters for driver state. Changes update LED triggers, global triggers, sysfs/uevent state, and `/dev/rfkill` event queues. Userspace opens `/dev/rfkill` to receive initial add events and later changes; writes with `RFKILL_OP_CHANGE` or `RFKILL_OP_CHANGE_ALL` apply software blocks. Module init registers the rfkill class, misc device, LED triggers, and optional input handler; exit reverses that order.

## State and Persistence
Global runtime state includes `rfkill_list`, `rfkill_fds`, `rfkill_global_states[]`, `rfkill_epo_lock_active`, default state module parameter, and optional input-disable count. Each rfkill tracks software/hardware block bits, previous software bit during set calls, hard block reason mask, index, registration/persistence/poll/suspend flags, ops, device, works, and name. Each open file owns a capped event list and ABI max-size setting. No durable persistence is written, but devices may be marked persistent so global sync does not override their initialized software state.

## Dependencies and Integration
Depends on the device model/class core, sysfs, miscdevice, wait queues, poll/read/write/ioctl file operations, capabilities (`CAP_NET_ADMIN` for sysfs writes), LED triggers when configured, PM sleep callbacks, workqueues, input bridge through `rfkill.h`, and driver `struct rfkill_ops` callbacks.

## Risks and Test Signals
Risks include the documented global mutex versus driver lock ABBA potential, event queue overflow per fd, userspace ABI size compatibility, state races around `RFKILL_BLOCK_SW_SETCALL`, polling during suspend/unregister, and EPO lock semantics. Test signals are sysfs `soft`/`state` permission and value checks, `/dev/rfkill` initial and change event ordering, max event cap behavior, ioctl max-size negotiation and input disable, LED trigger updates, poll pause/resume, register/unregister with active readers, and EPO restore/unlock flows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rfkill/core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rfkill/input.c -->
# sources/distributed-fs/ceph-client/net/rfkill/input.c

## Purpose
Bridges input-layer rfkill keys and switches to rfkill global operations, including type-specific toggles, master switch EPO/restore/unblock behavior, and rate limiting of repeated operations.

## Important APIs, Types, and Functions
Defines `enum rfkill_input_master_mode`, `enum rfkill_sched_op`, module parameter `master_switch_mode`, delayed work `rfkill_op_work`, and input handler `rfkill_handler`. Exported init/exit for the core are `rfkill_handler_init()` and `rfkill_handler_exit()`. Internal scheduling helpers include `rfkill_schedule_global_op()`, `rfkill_schedule_toggle()`, `rfkill_schedule_evsw_rfkillall()`, and `rfkill_op_handler()`.

## Control Flow
Input events for `KEY_WLAN`, `KEY_BLUETOOTH`, `KEY_UWB`, `KEY_WIMAX`, and `KEY_RFKILL` schedule toggles. `SW_RFKILL_ALL` schedules either EPO on switch-off or a configurable master operation on switch-on. The delayed work first drains pending global operations, bypassing rate limiting for new EPO, then applies type-specific toggles unless the EPO lock is active. `rfkill_connect()` registers and opens matching input devices, while `rfkill_start()` samples initial switch state under the input device event lock.

## State and Persistence
State is in pending bitmaps `rfkill_sw_pending` and `rfkill_sw_state`, pending global op fields, `rfkill_last_scheduled`, and the configured master switch mode. It is runtime-only.

## Dependencies and Integration
Depends on the input layer, delayed work, rfkill core global functions in `rfkill.h`, and key/switch event codes. Built into the rfkill object when `CONFIG_RFKILL_INPUT` is enabled.

## Risks and Test Signals
Risks include lost toggles while a global op is pending, rate-limit latency, EPO lock preventing normal toggles, and changing semantics through the master switch mode parameter. Test signals are key press toggles for each type, master switch off causing immediate EPO, switch on performing unlock/restore/unblock according to mode, initial switch-state handling on device start, and handler unregister cancelling delayed work.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rfkill/input.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rfkill/rfkill-gpio.c -->
# sources/distributed-fs/ceph-client/net/rfkill/rfkill-gpio.c

## Purpose
Implements a generic platform rfkill driver that controls radio power using reset/shutdown GPIOs and an optional clock, with ACPI/OF property support.

## Important APIs, Types, and Functions
Defines `struct rfkill_gpio_data`, `rfkill_gpio_set_power()` as the rfkill `set_block` callback, `rfkill_gpio_probe()`, and `rfkill_gpio_remove()`. ACPI support uses GPIO mappings for `reset-gpios` and `shutdown-gpios`; match tables cover ACPI IDs `BCM4752` and `LNV4752`, OF compatible `rfkill-gpio`, and a DMI deny table.

## Control Flow
Probe rejects denied systems, reads name/type properties, maps ACPI type when present, obtains optional clock and reset/shutdown GPIOs, requires at least one GPIO, drives GPIOs initially active, allocates an rfkill device, optionally initializes default-blocked state, registers it, and stores driver data. `rfkill_gpio_set_power()` enables the clock before unblocking, drives GPIOs to match power state, and disables the clock when blocking. Remove unregisters and destroys the rfkill object.

## State and Persistence
State is devm-managed driver data plus an rfkill object pointer, optional clock pointer, GPIO descriptors, type/name, and `clk_enabled`. No persistent storage is used; platform firmware properties define configuration.

## Dependencies and Integration
Depends on platform device core, GPIO consumer API, optional clocks, rfkill core API, ACPI device properties, OF matching, DMI matching, and firmware properties such as `label`/`radio-type` or `name`/`type`.

## Risks and Test Signals
Risks include optional GPIO NULL handling with direction/value calls, clock enable/disable imbalance if `clk_enabled` desynchronizes, firmware with bogus ACPI devices, and active-high assumptions from initial GPIO output values. Test signals are probe with reset-only, shutdown-only, and both GPIOs; `default-blocked`; ACPI and OF property parsing; blocked/unblocked GPIO and clock transitions; DMI-denied platform rejection; and remove while unblocked.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rfkill/rfkill-gpio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rfkill/rfkill.h -->
# sources/distributed-fs/ceph-client/net/rfkill/rfkill.h

## Purpose
Provides the private interface between rfkill core and optional input support.

## Important APIs, Types, and Functions
Declares global rfkill operations `rfkill_switch_all()`, `rfkill_epo()`, `rfkill_restore_states()`, `rfkill_remove_epo_lock()`, `rfkill_is_epo_lock_active()`, and `rfkill_get_global_sw_state()`, plus input lifecycle hooks `rfkill_handler_init()` and `rfkill_handler_exit()`.

## Control Flow
No executable code. The declarations let `core.c` initialize/exit input support and let `input.c` invoke global state changes without exposing these internals as public rfkill API.

## State and Persistence
No state is defined in this header.

## Dependencies and Integration
Depends on public rfkill types such as `enum rfkill_type` being available through included kernel headers in users. It is local to `net/rfkill`.

## Risks and Test Signals
Risks are compile-time only: mismatched prototypes or use when `CONFIG_RFKILL_INPUT` conditional compilation changes. Test signals are successful builds with input enabled and disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rfkill/rfkill.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rxrpc/Kconfig -->
# sources/distributed-fs/ceph-client/net/rxrpc/Kconfig

## Purpose
Defines build-time configuration for AF_RXRPC session sockets, IPv6 support, packet loss/delay injection, dynamic debugging, security classes, and the rxperf test service.

## Important APIs, Types, and Functions
Top-level `AF_RXRPC` is tristate and depends on `INET`, selecting crypto, keys, and UDP tunnel support. Nested options include `AF_RXRPC_IPV6`, `AF_RXRPC_INJECT_LOSS`, `AF_RXRPC_INJECT_RX_DELAY`, `AF_RXRPC_DEBUG`, `RXKAD`, `RXGK`, and `RXPERF`.

## Control Flow
Kconfig controls object inclusion in the Makefile and feature guards in source. Security options select required crypto algorithms. Delay injection depends on sysctl; IPv6 support depends on kernel IPv6.

## State and Persistence
No runtime state. Configuration persists in the kernel build.

## Dependencies and Integration
Integrates AF_RXRPC with AFS use cases, key retention, crypto providers, UDP networking, proc/sysctl diagnostics, and optional performance testing.

## Risks and Test Signals
Risks include missing crypto dependencies for security modes, feature code not compiled under common configs, and stale help text claiming incomplete support. Test signals are allmodconfig/allnoconfig coverage, module builds with and without IPv6, RXKAD/RXGK crypto link checks, and sysctl availability when injection options are enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rxrpc/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rxrpc/Makefile -->
# sources/distributed-fs/ceph-client/net/rxrpc/Makefile

## Purpose
Defines the AF_RXRPC module object composition and optional feature objects.

## Important APIs, Types, and Functions
Builds `rxrpc.o` for `CONFIG_AF_RXRPC` from core files such as `af_rxrpc.o`, call/connection/local/peer objects, input/output paths, key/security, sendmsg/recvmsg, RTT, skb, txbuf, and utilities. Optional objects include `proc.o`, `rxkad.o`, `sysctl.o`, and RXGK components. `rxperf.o` is built independently for `CONFIG_RXPERF`.

## Control Flow
Kbuild links the listed objects into one rxrpc module or built-in unit. Optional lines compile features according to `CONFIG_PROC_FS`, `CONFIG_RXKAD`, `CONFIG_SYSCTL`, and `CONFIG_RXGK`.

## State and Persistence
No runtime state; it defines build structure.

## Dependencies and Integration
Integrates with Kconfig symbols and the wider RxRPC source tree. `af_rxrpc.o` supplies module init/exit and socket family registration for the aggregate object.

## Risks and Test Signals
Risks include missing an object that provides symbols referenced by `af_rxrpc.c` or optional security/sysctl code. Test signals are builds across minimal, full, RXKAD, RXGK, procfs, sysctl, and rxperf configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rxrpc/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rxrpc/af_rxrpc.c -->
# sources/distributed-fs/ceph-client/net/rxrpc/af_rxrpc.c

## Purpose
Implements the AF_RXRPC socket family front end: socket creation, bind/listen/connect/send/poll/shutdown/release operations, kernel-service helper APIs, socket options, protocol registration, module initialization, and module teardown.

## Important APIs, Types, and Functions
Defines module parameter `debug`, exported `rxrpc_debug_id`, global `rxrpc_n_rx_skbs`, and `rxrpc_workqueue`. Public kernel helpers include `rxrpc_kernel_lookup_peer()`, `rxrpc_kernel_get_peer()`, `rxrpc_kernel_put_peer()`, `rxrpc_kernel_begin_call()`, `rxrpc_kernel_shutdown_call()`, `rxrpc_kernel_put_call()`, `rxrpc_kernel_check_life()`, `rxrpc_kernel_set_notifications()`, and `rxrpc_sock_set_min_security_level()`. Socket ops include `rxrpc_bind()`, `rxrpc_listen()`, `rxrpc_connect()`, `rxrpc_sendmsg()`, `rxrpc_setsockopt()`, `rxrpc_getsockopt()`, `rxrpc_poll()`, `rxrpc_shutdown()`, and `rxrpc_release()`.

## Control Flow
`rxrpc_create()` validates datagram socket type and protocol family, allocates `struct rxrpc_sock`, initializes queues, locks, call trees, state, write-space callback, and schedules peer keepalive soon. `rxrpc_bind()` validates `sockaddr_rxrpc`, obtains or creates a local UDP endpoint, and transitions to client-bound or server-bound state, allowing a second service ID for upgradeable services. `rxrpc_listen()` sizes the service backlog and preallocates service calls, with backlog zero disabling listen. `rxrpc_connect()` stores a default destination without network negotiation. `rxrpc_sendmsg()` auto-binds client sockets when needed, uses connected destination when no msg_name is supplied, and delegates data/OOB transmission to lower send helpers. Release orphan-closes the socket, marks services closed, detaches local service pointers, discards preallocations, releases calls, flushes the ordered workqueue, purges OOB and receive queues, drops local and key references, and finally `sock_put()`s.

## State and Persistence
Socket state is in `sk_state` values such as `RXRPC_UNBOUND`, client/server bound states, listening, listen-disabled, and close. `struct rxrpc_sock` stores family, local endpoint, service IDs, connection flags, security keys/keyrings, min security level, call RB tree, accept and receive queues, OOB queues, locks, and app callbacks. Module state includes the call slab, ordered high-priority reclaim workqueue, registered key types, pernet state, proto registration, socket family registration, security subsystem, and sysctls. All state is runtime-only.

## Dependencies and Integration
Depends on the Linux socket/proto APIs, net namespaces, UDP transport endpoints, RxRPC internal call/connection/peer/local/security/key/send/recv modules, key retention service, crypto-backed security classes, sysctl, RCU teardown, skb queues, and AFS or kernel consumers using exported helper APIs.

## Risks and Test Signals
Risks include state-machine violations for bind/listen/connect/options, reference leaks on local endpoints, peers, calls, keys, and sockets, release-time workqueue flushing latency, OOB queue leaks, service close races, and incorrect address validation tail clearing. Test signals are userspace socket lifecycle tests for client and server modes, second-service binding and upgrade option validation, auto-bind sendmsg, connected sendmsg, poll readability/writability, shutdown idempotence, kernel API begin/shutdown/put call flows, module init failure unwinding at each registration step, and module exit with `rxrpc_n_rx_skbs == 0`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rxrpc/af_rxrpc.c -->
