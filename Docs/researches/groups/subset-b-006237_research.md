# subset-b-006237 MPTCP net research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mptcp/pm_netlink.c -->
# sources/distributed-fs/ceph-client/net/mptcp/pm_netlink.c

## Purpose

`pm_netlink.c` is the generic-netlink front door for the MPTCP path-manager API. It registers the `MPTCP_PM_NAME` family, parses and formats endpoint address attributes, dispatches address operations either to the in-kernel PM or userspace PM depending on whether a token is present, and emits MPTCP path-management events to listeners.

## Important APIs, types, and functions

- `mptcp_genl_family`: exported generic-netlink family using generated `mptcp_pm_nl_ops` from `mptcp_pm_gen.h`.
- `mptcp_pm_parse_addr()` and `mptcp_pm_parse_entry()`: shared parsers for nested address attributes into `mptcp_addr_info` and `mptcp_pm_addr_entry`.
- `mptcp_pm_nl_get_addr_doit()` and `mptcp_pm_nl_get_addr_dumpit()`: netlink GET endpoint handlers.
- `mptcp_pm_nl_set_flags_doit()`: dispatches backup/fullmesh-like endpoint flag changes to userspace or kernel PM backends.
- `mptcp_event()`, `mptcp_event_addr_announced()`, `mptcp_event_addr_removed()`, `mptcp_event_pm_listener()`: multicast event producers for connection, subflow, address, and listener lifecycle events.
- `mptcp_userspace_pm_active()`: tests whether userspace PM event listeners exist in the socket netns.

## Control flow

Address parsing starts in `mptcp_pm_parse_pm_addr_attr()`: it validates nested policy, optional ID, required family when requested, IPv4/IPv6 address payload, and optional port. GET and SET handlers parse a user-provided endpoint and dispatch by the presence of `MPTCP_PM_ATTR_TOKEN`: no token means the global/kernel PM namespace, token means a specific MPTCP socket managed by userspace PM.

Event emission first checks for listeners on `MPTCP_PM_EV_GRP_OFFSET`, allocates an skb, writes event-specific attributes, and multicasts in the socket network namespace. `mptcp_event()` handles common connection/subflow events, while address announced/removed and listener events use dedicated helpers because they carry different attribute sets.

## State and persistence

This file does not own durable PM state. It serializes PM state owned by other modules into netlink messages and reads socket state through `mptcp_sock`, `mptcp_subflow_context`, and inet socket fields. The only persistent object here is the registered `mptcp_genl_family` and its multicast groups. Runtime events are transient skb messages.

## Dependencies and integration points

It depends on `protocol.h` for MPTCP socket/subflow structures and PM backend declarations, `mptcp_pm_gen.h` for generated netlink policies/ops, generic-netlink helpers, inet address helpers, and optional IPv6 support. It integrates with `pm_userspace.c` through token-dispatched functions and with the kernel PM via `mptcp_pm_nl_*` backend functions declared in `protocol.h`.

## Risks and edge cases

Important risks are netlink ABI compatibility, missing or mismatched address-family attributes, `-EMSGSIZE` paths while filling nested attributes, and correct GFP choice for event contexts. Event helpers intentionally return silently when no listeners exist; tests must not expect side effects without a subscribed multicast listener. IPv6 code is conditional, so AF_INET6 parsing/event coverage depends on `CONFIG_MPTCP_IPV6`.

## Test signals

Useful tests include generic-netlink endpoint add/get/dump/set-flag paths for kernel PM and token-scoped userspace PM, negative tests for missing family/address/port attributes, IPv4 and IPv6 event decoding, and listener-created/listener-closed multicast notifications. Runtime signals include `MPTCP_EVENT_*` messages, extack strings, and MPTCP PM selftests that exercise the `mptcp_pm` netlink family.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mptcp/pm_netlink.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mptcp/pm_userspace.c -->
# sources/distributed-fs/ceph-client/net/mptcp/pm_userspace.c

## Purpose

`pm_userspace.c` implements the userspace path-manager backend. It lets a netlink controller, identified by an MPTCP token, announce/remove local addresses, create/destroy subflows, set backup flags, and query per-socket userspace-managed local endpoint state.

## Important APIs, types, and functions

- `mptcp_pm_userspace`: PM backend registered under the name `userspace`.
- `mptcp_userspace_pm_free_local_addr_list()`: frees per-socket userspace PM endpoint entries.
- `mptcp_userspace_pm_get_local_id()` and `mptcp_userspace_pm_is_backup()`: lookup helpers used by common PM/subflow code.
- `mptcp_pm_nl_announce_doit()`: validates and queues an ADD_ADDR announcement for a token-selected MPTCP socket.
- `mptcp_pm_nl_remove_doit()` and `mptcp_pm_remove_addr_entry()`: remove announced or subflow-backed local addresses and generate RM_ADDR signaling.
- `mptcp_pm_nl_subflow_create_doit()` and `mptcp_pm_nl_subflow_destroy_doit()`: userspace-requested subflow lifecycle operations.
- `mptcp_userspace_pm_set_flags()`: updates local entry backup flags and sends MP_PRIO.
- `mptcp_userspace_pm_dump_addr()` and `mptcp_userspace_pm_get_addr()`: token-scoped endpoint reporting.

## Control flow

Most netlink operations start with `mptcp_userspace_pm_get_sock()`, which validates `MPTCP_PM_ATTR_TOKEN`, resolves it via `mptcp_token_get_sock()`, verifies `mptcp_pm_is_userspace()`, and returns a referenced MPTCP socket. Address operations parse attributes with the shared parser from `pm_netlink.c`.

Announce flow appends a local entry, allocates an announce-list item, increments `add_addr_signaled`, calls `mptcp_pm_announce_addr()`, and schedules an ACK. Remove flow handles ID 0 specially because it can correspond to the initial subflow, otherwise deletes the local entry by ID, removes matching announcement/subflow state, sends RM_ADDR, then frees the entry with RCU-aware cleanup and socket memory accounting adjustment. Subflow create validates local/remote family compatibility, records a local entry with SUBFLOW flag, calls `__mptcp_subflow_connect()`, and rolls back the entry on failure. Destroy maps local/remote tuples to an existing subflow and closes it through `mptcp_subflow_shutdown()` and `mptcp_close_ssk()`.

## State and persistence

Userspace PM state is per `mptcp_sock` in `msk->pm.userspace_pm_local_addr_list`, protected by `msk->pm.lock`. Entries are socket-accounted allocations from `sock_kmemdup()` and carry address, flags, ifindex, and ID. Counters such as `local_addr_used`, `extra_subflows`, and `add_addr_signaled` mirror list and signaling state. The file deliberately keeps removed entries in some remote-close cases so IDs are not immediately reused incorrectly.

## Dependencies and integration points

It relies on `protocol.h` PM structures, common netlink parsing from `pm_netlink.c`, token lookup, common PM helpers such as `mptcp_pm_alloc_anno_list()`, `mptcp_pm_remove_addr()`, `mptcp_pm_mp_prio_send_ack()`, and subflow helpers from the MPTCP core. It increments MPTCP MIB counters for subflow removal and registers with the PM registry via `mptcp_pm_register()`.

## Risks and edge cases

ID management is subtle: ID 0 needs special handling, duplicate address/ID combinations are rejected unless both match, and ID reuse is intentionally conservative. Locking crosses socket locks, PM spinlocks, RCU list deletion, and subflow locks; ABBA regressions are a main risk. IPv4-mapped IPv6 normalization in destroy must match actual subflow tuples. A TODO notes missing refcounting for address entries that could be used multiple times, such as fullmesh-style cases.

## Test signals

Coverage should include token validation, userspace-PM-only rejection, announce/remove of signaled addresses, ID 0 removal, create/destroy subflow by tuple, MP_PRIO backup flag updates, dump/get address APIs, duplicate address/ID rejection, and IPv4/IPv6 tuple matching. MPTCP PM selftests and packet traces for ADD_ADDR, RM_ADDR, MP_JOIN, and MP_PRIO are the strongest behavioral signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mptcp/pm_userspace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mptcp/protocol.c -->
# sources/distributed-fs/ceph-client/net/mptcp/protocol.c

## Purpose

`protocol.c` is the MPTCP socket protocol implementation. It registers IPv4 and optional IPv6 MPTCP stream protocols, creates and manages the first TCP subflow, maps send/receive data between MPTCP data sequence numbers and TCP subflow sequence spaces, schedules subflows, retransmits pending MPTCP data, handles fallback/fastclose/DATA_FIN state, and implements socket operations such as connect, bind, listen, accept, sendmsg, recvmsg, poll, read_sock, splice_read, shutdown, close, and ioctl.

## Important APIs, types, and functions

- Protocol registration: `mptcp_proto_init()`, `mptcp_proto_v6_init()`, `mptcp_prot`, `mptcp_stream_ops`, `mptcp_v6_stream_ops`.
- Subflow setup and connection: `__mptcp_socket_create()`, `__mptcp_nmpc_sk()`, `mptcp_connect()`, `mptcp_finish_connect()`, `mptcp_finish_join()`, `mptcp_sk_clone_init()`.
- Send path: `mptcp_sendmsg()`, `mptcp_sendmsg_frag()`, `__mptcp_push_pending()`, `mptcp_subflow_get_send()`, `mptcp_check_send_data_fin()`.
- Receive path: `mptcp_data_ready()`, `__mptcp_move_skbs_from_subflow()`, `__mptcp_move_skb()`, `mptcp_data_queue_ofo()`, `__mptcp_ofo_queue()`, `mptcp_recvmsg()`, `mptcp_read_sock()`, `mptcp_splice_read()`.
- Reliability and timers: `__mptcp_clean_una()`, `__mptcp_retransmit_pending_data()`, `__mptcp_retrans()`, `mptcp_retransmit_timer()`, `mptcp_tout_timer()`, `mptcp_reset_tout_timer()`.
- Lifecycle: `__mptcp_close()`, `mptcp_close()`, `mptcp_close_ssk()`, `__mptcp_close_ssk()`, `mptcp_do_fastclose()`, `mptcp_disconnect()`, `mptcp_destroy_common()`, `__mptcp_destroy_sock()`.
- Deferred work: `mptcp_worker()`, `mptcp_release_cb()`, `mptcp_subflow_delegate()`, `mptcp_napi_poll()`.

## Control flow

Active sockets allocate an initial TCP subflow lazily via `__mptcp_nmpc_sk()`. `mptcp_connect()` initializes MPTCP keys/tokens when possible, otherwise falls back to TCP-compatible behavior, then lets the subflow protocol connect. Passive sockets are cloned in `mptcp_sk_clone_init()` after an MP_CAPABLE request; the new MPTCP socket takes ownership of the accepted subflow and initializes data sequence state.

On send, `mptcp_sendmsg()` copies user data into socket-accounted `mptcp_data_frag` records on the MPTCP retransmission queue, advances `write_seq`, and calls `__mptcp_push_pending()`. The scheduler marks one or more subflows as scheduled, `mptcp_sendmsg_frag()` builds TCP skbs with MPTCP extensions carrying DSS mappings, updates subflow relative write sequence, optional checksums, and MPTCP `snd_nxt`/`bytes_sent`.

On receive, subflow callbacks call `mptcp_data_ready()`. Data is initialized with MPTCP sequence metadata, moved to the MPTCP receive queue if in-order, or stored in the MPTCP out-of-order rbtree if ahead of `ack_seq`. The receive queue is drained by `mptcp_recvmsg()`, `read_sock`, or splice; consumed bytes update `bytes_consumed`, receive-buffer autotuning, and ACK cleanup on subflows. DATA_FIN state changes are deferred to safe socket-lock contexts.

Close and error flows mirror TCP state transitions at the MPTCP layer while managing multiple TCP subflows. Graceful close emits DATA_FIN and shuts down subflows when the data-level FIN is sent or acknowledged. Fastclose resets subflows, destroys tokens, purges backlog, and marks the MPTCP socket closed. The worker handles PM work, close-subflow work, retransmission work, fail timeout, DATA_FIN processing, and destruction of dead sockets.

## State and persistence

The central persistent state is `struct mptcp_sock`: data sequence counters (`write_seq`, `snd_nxt`, `snd_una`, `ack_seq`), retransmission queue, receive queue, out-of-order rbtree, backlog list, subflow list, PM state, scheduler pointer, fallback flags, timers, counters, and socket-option mirrors. Each TCP subflow has `struct mptcp_subflow_context` carrying mapping state, local/remote IDs, relative sequence numbers, flags, delegated actions, and references back to the parent MPTCP socket.

Synchronization uses the MPTCP socket lock, `mptcp_data_lock()` over `sk_lock.slock`, subflow locks, PM/fallback spinlocks, callback-lock grafting, timers, workqueues, and per-CPU delegated NAPI lists. Memory accounting is explicit: receive skbs lend/borrow forward allocation between subflow and MPTCP sockets, send fragments are charged to the MPTCP socket and TCP subflow, and backlog memory is reconciled at accept time for memory cgroups.

## Dependencies and integration points

This file is integrated tightly with Linux TCP internals, inet protocol registration, IPv6 support, socket memory accounting, netfilter/BPF pre-connect hooks, RPS/RFS, tracepoints, MPTCP PM/token/crypto/subflow modules, and `sockopt.c` for option synchronization on joins. It emits netlink PM events through `pm_netlink.c`, calls PM worker and path checks, and is the main implementation behind the protocol hooks exported through `protocol.h`.

## Risks and edge cases

The highest-risk areas are lock ordering across MPTCP and TCP subflow sockets, receive memory ownership during backlog spooling and subflow close, sequence wrap/overlap handling in the out-of-order tree, fallback transitions when infinite maps or DSS corruption are observed, and closing races involving accepted-but-not-yet-grafted sockets. DATA_FIN state must remain consistent with TCP state transitions. Scheduler decisions depend on stale flags, pacing rates, backup status, and notsent/wmem limits; regressions can cause stalls rather than obvious crashes.

## Test signals

Test signals include MPTCP kselftests for connect/listen/accept, MP_JOIN, fallback, checksum, DSS corruption, ADD_ADDR/RM_ADDR, fastclose, and close timeout; packet captures showing DSS maps and DATA_FIN; tracepoints from `trace/events/mptcp.h`; MIB counters such as fallback, retransmission, duplicate data, out-of-window, and current established; and socket API tests for `sendmsg`, `recvmsg`, `poll`, splice, ioctl queue sizes, and IPv6 registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mptcp/protocol.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mptcp/protocol.h -->
# sources/distributed-fs/ceph-client/net/mptcp/protocol.h

## Purpose

`protocol.h` is the internal MPTCP contract shared by the protocol core, subflow code, options parser, path managers, scheduler, token code, crypto, sockopt handling, and diagnostics. It defines wire-option constants, shared socket/subflow/request structures, state bits, helper macros, inline functions, and cross-file function prototypes.

## Important APIs, types, and functions

- Wire constants: `OPTION_MPTCP_*`, `MPTCPOPT_*`, TCP option lengths, DSS/ADD_ADDR/PRIO/RST flags, and `MPTCP_SUPPORTED_VERSION`.
- Shared metadata: `struct mptcp_skb_cb`, `struct mptcp_options_received`, `struct csum_pseudo_header`.
- Path-manager types: `enum mptcp_pm_status`, `enum mptcp_pm_type`, `enum mptcp_addr_signal_status`, `struct mptcp_pm_data`, `struct mptcp_pm_local`, `struct mptcp_pm_addr_entry`.
- Core socket state: `struct mptcp_sock`, `struct mptcp_data_frag`, `struct mptcp_subflow_request_sock`, `struct mptcp_subflow_context`, `struct mptcp_delegated_action`.
- Iteration and conversion helpers: `mptcp_sk()`, `mptcp_for_each_subflow()`, `mptcp_subflow_ctx()`, `mptcp_subflow_tcp_sock()`, `subflow_get_local_id()`.
- Inline behavior helpers: receive-space conversion, RTT estimate, pending send-frag navigation, fallback checks, DATA_FIN checks, PM signal checks, delegated-action queueing, sndbuf propagation, and socket writeability helpers.
- Prototypes for protocol, subflow, scheduler, PM, userspace PM, netlink events, token, crypto, and sockopt modules.

## Control flow

The header does not run a top-level flow, but it shapes all MPTCP flows. Incoming TCP options are parsed into `mptcp_options_received`; subflow handshake code populates request and subflow contexts; `protocol.c` consumes the shared state to move data and drive socket lifecycle; PM modules inspect and mutate `mptcp_pm_data`; scheduler code uses `mptcp_sched_ops` hooks to mark subflows; and sockopt code syncs MPTCP-level options to subflows using `setsockopt_seq`.

Inline helpers also encode hot-path decisions: whether data is available, whether epoll should report readable, whether a subflow is active, whether fallback has occurred, how long PM options are on the wire, and how to schedule delegated per-CPU subflow work without directly taking parent locks in softirq context.

## State and persistence

The header defines the persistent in-memory layout of MPTCP sockets. `struct mptcp_sock` embeds `inet_connection_sock` first and persists connection-level sequence numbers, queues, timers, PM state, scheduler state, locks, fallback state, socket-option mirrors, and counters for diagnostics. `struct mptcp_subflow_context` persists per-TCP-subflow mapping, handshake, PM ID, reset, stale, delegated-action, and callback state. `struct mptcp_pm_data` carries path-manager counters, bitmaps, and address signaling lists.

## Dependencies and integration points

It includes Linux random, TCP, inet connection sock, generic netlink, UAPI MPTCP headers, and reset-reason definitions. The declarations bind together `protocol.c`, `subflow.c`, `options.c`, `pm.c`, `pm_netlink.c`, `pm_userspace.c`, `pm_kernel.c`, `sched.c`, `sockopt.c`, token and crypto modules, diagnostics, and optional IPv6/SYN-cookie support.

## Risks and edge cases

Because this file defines shared structure layout and inline semantics, changes have broad ABI-like internal impact. Bitfield ordering, reset groups used by `memset()`, socket embedding order, SKB control-block size, fallback helpers, and memory-accounting helpers are particularly sensitive. Conditional IPv6 and SYN-cookie declarations must stay consistent with implementation files. Any new field requires careful initialization in active, passive clone, disconnect, and destroy paths.

## Test signals

Build-time `BUILD_BUG_ON()` checks in implementation files validate some size assumptions. Runtime test signals are indirect: MPTCP selftests covering option parsing, fallback, PM behavior, joins, diagnostics, and socket options validate this contract. Static analysis and compile coverage across `CONFIG_MPTCP_IPV6`, `CONFIG_SYN_COOKIES`, and debug-net configurations are important because many helpers are conditional or lock-sensitive.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mptcp/protocol.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mptcp/sched.c -->
# sources/distributed-fs/ceph-client/net/mptcp/sched.c

## Purpose

`sched.c` provides the MPTCP packet scheduler registry and the default scheduler implementation. Schedulers choose which subflow or subflows should transmit new data or retransmitted data by marking `mptcp_subflow_context::scheduled`.

## Important APIs, types, and functions

- `mptcp_sched_default`: built-in scheduler named `default`.
- `mptcp_sched_find()`: RCU lookup by scheduler name.
- `mptcp_get_available_schedulers()`: builds a space-separated scheduler list for sysctl or diagnostics.
- `mptcp_validate_scheduler()`, `mptcp_register_scheduler()`, `mptcp_unregister_scheduler()`: registry lifecycle.
- `mptcp_sched_init()`: registers the default scheduler.
- `mptcp_init_sched()` and `mptcp_release_sched()`: per-socket scheduler selection and module/BPF ref handling.
- `mptcp_sched_get_send()` and `mptcp_sched_get_retrans()`: invoked by the core send and retransmit paths.

## Control flow

At initialization, the default scheduler is registered in the global RCU list. Per MPTCP socket, `mptcp_init_sched()` selects a scheduler by name or falls back to default, takes the module/BPF reference, stores it on `msk->sched`, and calls optional `init`. Send and retransmit paths first respect any already scheduled subflow; otherwise they delegate to fallback handling, the default scheduler, or custom scheduler callbacks. The default scheduler calls `mptcp_subflow_get_send()` or `mptcp_subflow_get_retrans()` from `protocol.c` and marks the returned subflow scheduled.

## State and persistence

Global state is `mptcp_sched_list`, protected by `mptcp_sched_list_lock` for updates and traversed under RCU for reads. Per-socket state is just the selected `msk->sched` pointer and optional scheduler-private state created by callbacks. Per-subflow scheduled state is a boolean in `mptcp_subflow_context`.

## Dependencies and integration points

The registry uses kernel list, RCU, spinlock, module ownership, and BPF module ref helpers. It depends on protocol helpers for selecting default send/retransmit subflows and on `protocol.h` for `struct mptcp_sched_ops` and subflow context access. Core sending in `protocol.c` consumes the scheduled bits set here.

## Risks and edge cases

Schedulers must implement `get_send`; `get_retrans` is optional and falls back to `get_send`. Fallback sockets bypass custom schedulers and only use the first TCP subflow if it can send and has memory. Scheduled bits must be cleared by callers after use; stale scheduled bits can misdirect later sends. Registry updates require RCU safety, and unregistering the default scheduler is intentionally ignored.

## Test signals

Tests should verify scheduler registration, duplicate-name rejection, available scheduler listing, default send/retransmit selection, custom scheduler fallback behavior, module ref release, and behavior during TCP fallback. Packet distribution across subflows and retransmission selection in MPTCP selftests or scheduler-specific tests provide the strongest runtime signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mptcp/sched.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mptcp/sockopt.c -->
# sources/distributed-fs/ceph-client/net/mptcp/sockopt.c

## Purpose

`sockopt.c` implements MPTCP-aware `setsockopt`, `getsockopt`, socket-option synchronization to subflows, diagnostic information export, and MPTCP-specific receive-low-water handling. It decides which options are MPTCP-level only, which are mirrored to all subflows, which apply only to the first subflow before establishment, and which pass through to TCP after fallback.

## Important APIs, types, and functions

- Public entry points: `mptcp_setsockopt()`, `mptcp_getsockopt()`, `mptcp_sockopt_sync_locked()`, `mptcp_set_rcvlowat()`, `mptcp_diag_fill_info()`.
- Sequencing helpers: `sockopt_seq_reset()`, `sockopt_seq_inc()`, `setsockopt_seq` in `mptcp_sock` and `mptcp_subflow_context`.
- SOL_SOCKET handlers: integer option sync, timestamp/timestamping, linger, reuse/bind device, buffer sizes, mark, priority, keepalive, incoming CPU.
- SOL_TCP handlers: congestion control, cork, nodelay, keepalive timers/counts, maxseg, notsent low-water, INQ, fastopen options, and first-subflow-only options.
- SOL_IP/SOL_IPV6 handlers: bind/freebind/transparent/local-port-range/TOS and selected IPv6 socket flags.
- Diagnostics: `MPTCP_INFO`, `MPTCP_FULL_INFO`, `MPTCP_TCPINFO`, `MPTCP_SUBFLOW_ADDRS`.

## Control flow

`mptcp_setsockopt()` handles SOL_SOCKET first, rejects unsupported options through `mptcp_supported_sockopt()`, checks TCP fallback, then dispatches by level. Fallback sockets pass the option directly to the underlying TCP socket. Non-fallback sockets either update MPTCP-level fields, mirror values to all existing subflows under locks, or apply an option to the initial subflow before connection establishment.

`mptcp_getsockopt()` similarly passes through after fallback, otherwise reports MPTCP-level mirrors or first-subflow TCP values. Diagnostic getters validate user-provided buffer headers, walk the subflow list under the MPTCP lock, copy `tcp_info` and address data into user arrays, and report how much was copied. `mptcp_sockopt_sync_locked()` is called when new subflows join; it suppresses latency-related subflow settings that would confuse scheduling, and syncs only when the subflow sequence differs from `msk->setsockopt_seq`.

## State and persistence

Option state persists primarily in `mptcp_sock`: `setsockopt_seq`, congestion-control name, cork/nodelay flags, keepalive values, maxseg, notsent lowat, receive INQ mode, socket-level marks/buffers/userlocks inherited from `struct sock`, and PM counters used by diagnostics. Subflows cache their last `setsockopt_seq` and `cached_sndbuf`. Fallback state redirects option semantics from MPTCP-level handling to TCP-level passthrough.

## Dependencies and integration points

This file integrates with generic socket option helpers, TCP option APIs, IPv4/IPv6 inet option state, UAPI MPTCP diagnostic structures, PM limit helpers, core write-space/readability helpers, and subflow iteration from `protocol.h`. It is called from `mptcp_prot` hooks in `protocol.c`, and `mptcp_sockopt_sync_locked()` is called when a subflow finishes joining.

## Risks and edge cases

Unsupported options are intentionally rejected or no-op; incorrectly broadening support can break multi-subflow semantics. Lock ordering matters because options are mirrored while holding the MPTCP socket and taking subflow locks. `setsockopt_seq` uses high bits from socket state so listener and accepted socket sync states do not collide. Diagnostic copy paths must validate user sizes to avoid ABI regression. Receive-low-water changes may force receive-buffer growth and must be mirrored to subflows without disturbing user-locked buffers.

## Test signals

Test signals include socket-option selftests before connect, after connect, after MP_JOIN, on listeners and accepted sockets, and after TCP fallback. Useful cases are cork/nodelay flushing, congestion-control propagation, keepalive propagation, buffer userlocks, `TCP_INQ`, `TCP_IS_MPTCP`, first-subflow fastopen options, MPTCP diagnostics with short and full buffers, and `SO_RCVLOWAT` readiness behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mptcp/sockopt.c -->
