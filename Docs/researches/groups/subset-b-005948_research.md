# Research: subset-b-005948

Grouped research for Ceph-client imported Linux networking headers under `sources/distributed-fs/ceph-client/include/net`. Each section preserves the source path and is bounded by the reconciliation markers used to split per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/rtnetlink.h -->
# sources/distributed-fs/ceph-client/include/net/rtnetlink.h

## Purpose
This header defines the in-kernel rtnetlink registration and link/address-family operation contracts. It lets protocol families and virtual/link drivers register message handlers, link kinds, validation callbacks, namespace handling, and netlink dump/fill routines used by `rtnetlink.c`.

## Important APIs, Types, And Functions
Key types are `rtnl_doit_func`, `rtnl_dumpit_func`, `struct rtnl_msg_handler`, `struct rtnl_newlink_params`, `struct rtnl_link_ops`, and `struct rtnl_af_ops`. The handler flags control lock behavior and dump semantics: `RTNL_FLAG_DOIT_UNLOCKED`, `RTNL_FLAG_BULK_DEL_SUPPORTED`, `RTNL_FLAG_DUMP_UNLOCKED`, and `RTNL_FLAG_DUMP_SPLIT_NLM_DONE`. `rtnl_msgtype_kind()` masks message types into new/delete/get/set classes. `rtnl_msg_family()` safely extracts `rtgen_family` only when the nlmsg is long enough. Registration APIs include `rtnl_register_many()`, `rtnl_unregister_many()`, `rtnl_link_register()`, `rtnl_link_unregister()`, `rtnl_af_register()`, and `rtnl_af_unregister()`.

## Control Flow
Netlink receive paths dispatch through registered `rtnl_msg_handler` entries. Link creation flows parse attributes, resolve link and peer namespaces with `rtnl_newlink_link_net()` and `rtnl_newlink_peer_net()`, allocate/configure devices through `rtnl_link_ops::alloc`, `setup`, `validate`, and `newlink`, then use dump callbacks for rtnetlink responses.

## State And Persistence
The header declares registration objects with list and SRCU fields; actual persistence is in global rtnetlink registries. `rtnl_link_ops` and `rtnl_af_ops` lifetime is module-sensitive through `owner` or registration ordering.

## Dependencies And Integration Points
It depends on Linux rtnetlink UAPI, SRCU, netlink attributes, network namespaces, and `net_device`. It integrates virtual devices, address-family specific link data, module aliases via `MODULE_ALIAS_RTNL_LINK`, and namespace-capable lookups through `rtnl_get_net_ns_capable()`.

## Risks And Test Signals
Risks center on attribute validation gaps, namespace mis-selection, unlocked handler races, and module lifetime while SRCU readers walk operations. Test signals include rtnetlink create/change/delete coverage, extack validation failures, namespace peer/link cases, and dump size/fill consistency checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/rtnetlink.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/rtnh.h -->
# sources/distributed-fs/ceph-client/include/net/rtnh.h

## Purpose
This compact header provides helper routines for walking multipath route next-hop (`struct rtnexthop`) payloads embedded in rtnetlink route messages.

## Important APIs, Types, And Functions
`rtnh_ok()` validates that a next-hop record fits the remaining buffer and has at least the base header size. `rtnh_next()` advances by `NLA_ALIGN(rtnh_len)` and updates the caller's remaining byte count. `rtnh_attrs()` returns the first nested netlink attribute after the aligned next-hop header. `rtnh_attrlen()` returns the attribute payload length after subtracting the aligned base header.

## Control Flow
Route parsing loops call `rtnh_ok()` before dereferencing, process the current nexthop and attributes, then move with `rtnh_next()`. The helpers intentionally leave policy parsing to route code while centralizing length arithmetic.

## State And Persistence
The file has no persistent state. It only interprets caller-owned netlink message memory.

## Dependencies And Integration Points
It depends on `linux/rtnetlink.h` for `struct rtnexthop` and `net/netlink.h` for alignment. It is integrated by IPv4/IPv6 route netlink parsing and dump code handling `RTA_MULTIPATH`.

## Risks And Test Signals
Main risks are malformed length fields, alignment mistakes, and callers using `rtnh_attrs()` without first validating. Test signals are fuzzed rtnetlink route messages, multipath route add/delete tests, and sanitizer coverage for truncated attributes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/rtnh.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/sch_generic.h -->
# sources/distributed-fs/ceph-client/include/net/sch_generic.h

## Purpose
This is the central traffic-control scheduler header. It defines qdisc objects, qdisc/class/filter operations, classifier chains and blocks, queue/stat helper functions, packet drop handling, rate conversion helpers, mini-qdisc fast-path structures, and scheduler lifecycle APIs.

## Important APIs, Types, And Functions
Core state types include `struct Qdisc`, `struct Qdisc_ops`, `struct Qdisc_class_ops`, `struct tcf_proto_ops`, `struct tcf_proto`, `struct tcf_chain`, `struct tcf_block`, `struct qdisc_skb_head`, `struct qdisc_rate_table`, `struct qdisc_size_table`, `struct psched_ratecfg`, `struct psched_pktrate`, `struct mini_Qdisc`, and `struct mini_Qdisc_pair`. Inline APIs manage qdisc references, run serialization (`qdisc_run_begin/end()`), root lookup, tree locks, qlen/backlog accounting, enqueue/dequeue/drop, class hashes, and rate-to-time conversion. External lifecycle functions include `dev_init_scheduler()`, `dev_activate()`, `dev_deactivate()`, `qdisc_alloc()`, `qdisc_create_dflt()`, `qdisc_destroy()`, `qdisc_put()`, and offload helpers.

## Control Flow
Transmit scheduling enters qdisc enqueue callbacks, updates per-qdisc or per-cpu stats, and serializes dequeue through either root-lock `running` state or `TCQ_F_NOLOCK` `seqlock`/state bits. Missed work sets `__QDISC_STATE_MISSED` and reschedules at `qdisc_run_end()`. Classifier paths traverse `tcf_block` to chains and `tcf_proto` instances under RCU and explicit locks, while `mini_Qdisc` provides a reduced ingress/clsact fast path.

## State And Persistence
Qdisc state persists on `netdev_queue` objects and includes packet lists, GSO/deferred queues, refcounts, rate estimators, stats, RCU lifetime, lock classes, and private data. Class/filter state persists in chain lists, xarray ports, shared block indices, and offload counters. Packet metadata is carried in `skb->cb` through `qdisc_skb_cb`/`tc_skb_cb`.

## Dependencies And Integration Points
The file ties together `netdevice`, rtnetlink, generic stats, flow offload, packet scheduler/classifier UAPI, dynamic queue limits, RCU, per-cpu stats, and drop-reason reporting. Hardware offload paths integrate with `tc_setup_type` callbacks and block callback lists.

## Risks And Test Signals
High-risk areas are lock ordering between RTNL, qdisc root locks, seqlock no-lock qdiscs, RCU chain updates, deferred skb freeing, per-cpu stat aggregation, and `skb->cb` size pressure. Test signals include qdisc attach/detach, classful qdisc grafts, clsact ingress/egress, no-lock qdisc stress, offload add/remove, drop-reason accounting, and netdev queue count changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/sch_generic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/sch_priv.h -->
# sources/distributed-fs/ceph-client/include/net/sch_priv.h

## Purpose
This private scheduler header declares common helpers for multiqueue qdiscs. It is shared by mq-like scheduler implementations that manage one leaf qdisc per hardware transmit queue.

## Important APIs, Types, And Functions
`struct mq_sched` stores the leaf qdisc array. `mq_init_common()` initializes a multiqueue root with child qdiscs, while `mq_destroy_common()`, `mq_attach()`, and `mq_dump_common()` handle teardown, device attachment, and netlink dump state. Class operations include `mq_select_queue()`, `mq_leaf()`, `mq_find()`, `mq_dump_class()`, `mq_dump_class_stats()`, and `mq_walk()`.

## Control Flow
The root mq qdisc delegates class-like operations to hardware queue leaves. During init, child qdiscs are allocated using the supplied `Qdisc_ops`; attach installs them on netdev queues. Dump and walk callbacks expose each queue as a class to tc.

## State And Persistence
Persistent state is only the `qdiscs` pointer array in qdisc private data. Each child qdisc owns its normal queue and stats lifecycle.

## Dependencies And Integration Points
It depends on `sch_generic.h` and integrates with `mq_qdisc_ops`, `mqprio` style class traversal, netdev queue selection, and tc dump/stat APIs.

## Risks And Test Signals
Risks include mismatched real transmit queue counts, child qdisc leaks, invalid class IDs, and stale queue mappings after device reconfiguration. Test signals are multiqueue device activation, `real_num_tx_queues` changes, tc class dump/walk, and qdisc replacement on individual queues.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/sch_priv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/scm.h -->
# sources/distributed-fs/ceph-client/include/net/scm.h

## Purpose
This header defines socket control-message state used for passing credentials, file descriptors, and security labels through Unix-domain and other socket ancillary data paths.

## Important APIs, Types, And Functions
`SCM_MAX_FD` caps descriptor passing at 253. `struct scm_creds` carries pid/uid/gid; `struct scm_fp_list` owns passed file pointers plus Unix inflight graph metadata under `CONFIG_UNIX`; `struct scm_cookie` bundles credentials, file list, pid reference, and optional security ID. APIs include `scm_send()`, `__scm_send()`, `scm_recv()`, `scm_recv_unix()`, `scm_detach_fds()`, `scm_detach_fds_compat()`, `scm_fp_dup()`, and `scm_recv_one_fd()`. Inline helpers manage credential references and optional peer security.

## Control Flow
Send-side callers initialize a cookie through `scm_send()`, optionally force current process credentials, collect peer security, and parse ancillary data with `__scm_send()`. Receive-side paths detach file descriptors and credentials into user msghdr control buffers. Destroy paths release pid references and any passed file list.

## State And Persistence
SCM state is per-message and must be destroyed after use. File descriptor lists hold referenced `struct file` objects and `struct user_struct`; Unix inflight state tracks garbage-collection edges for descriptor cycles.

## Dependencies And Integration Points
It depends on credentials, file tables, pid references, LSM network hooks, compat control-message handling, and Unix socket internals. `receive_fd()` bridges kernel files to user fd tables.

## Risks And Test Signals
Risks include fd leaks, credential lifetime bugs, Unix inflight GC cycles, compat layout errors, and missing LSM secid propagation. Test signals are SCM_RIGHTS/SCM_CREDENTIALS send-receive tests, forced credentials, descriptor-limit tests, compat syscall tests, and Unix garbage collection stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/scm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/sctp/auth.h -->
# sources/distributed-fs/ceph-client/include/net/sctp/auth.h

## Purpose
This SCTP-AUTH header defines shared-key and HMAC primitives used to authenticate selected SCTP chunks according to the SCTP authentication extension.

## Important APIs, Types, And Functions
`struct sctp_hmac` identifies supported HMAC algorithms and output lengths. `struct sctp_auth_bytes` is a refcounted variable-length byte vector for key material. `struct sctp_shared_key` binds a key id, key bytes, refcount, deactivation flag, and list node. APIs create, copy, hold, release, activate, deactivate, delete, and destroy keys, select HMAC algorithms, verify HMAC ids, decide whether chunk IDs require send/receive authentication, compute HMACs, and initialize/free endpoint auth state.

## Control Flow
Endpoint keys are configured by socket options, copied into associations, and combined with peer random/chunk/HMAC parameters during association setup. When outbound or inbound chunks require authentication, lookup and default-HMAC selection feed `sctp_auth_calculate_hmac()`.

## State And Persistence
Key material persists in endpoint and association key lists with explicit refcounts. Active key ids and deactivated keys are long-lived association state; raw `sctp_auth_bytes` may be shared.

## Dependencies And Integration Points
It integrates with `sctp_endpoint`, `sctp_association`, SCTP chunk parameter parsing, user API key objects, and crypto HMAC implementations declared through SCTP constants.

## Risks And Test Signals
Risks include key lifetime races, accepting unsupported HMAC ids, authenticating the wrong chunk set, deactivated-key misuse, and memory disclosure of key material. Test signals include SCTP_AUTH socket-option tests, authenticated COOKIE/ASCONF cases, unsupported algorithm negotiation, and key add/delete/deactivate sequences.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/sctp/auth.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/sctp/checksum.h -->
# sources/distributed-fs/ceph-client/include/net/sctp/checksum.h

## Purpose
This header provides the inline SCTP CRC32c checksum computation for packets held in `sk_buff`.

## Important APIs, Types, And Functions
`sctp_compute_cksum(const struct sk_buff *skb, unsigned int offset)` locates the SCTP header at `skb->data + offset`, saves and clears the checksum field, computes CRC32c over the SCTP packet bytes, restores the old field, and returns the little-endian checksum.

## Control Flow
Transmit and receive validation paths call the helper with the transport offset. The helper mutates the checksum field only temporarily so callers can operate on packet data in place.

## State And Persistence
No persistent state is held. The observable packet checksum field is restored before returning.

## Dependencies And Integration Points
It depends on `struct sctphdr`, `sk_buff`, `skb_crc32c()`, and endian conversion. It is used by SCTP input validation and output checksum filling unless checksum disable paths bypass it.

## Risks And Test Signals
Risks include invalid offsets, non-linear skb handling assumptions delegated to `skb_crc32c()`, and concurrent modification of shared skb data. Test signals are SCTP checksum receive rejection, transmit checksum verification, UDP-encapsulated SCTP offsets, and checksum-disable configuration tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/sctp/checksum.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/sctp/command.h -->
# sources/distributed-fs/ceph-client/include/net/sctp/command.h

## Purpose
This header defines the command-sequence abstraction emitted by SCTP state functions and consumed by the side-effect interpreter. It decouples pure state-machine decisions from actions such as timers, replies, SACK processing, transport changes, and ULP notifications.

## Important APIs, Types, And Functions
`enum sctp_verb` enumerates actions including new/delete association, state changes, TSN reporting, SACK generation/processing, packet/chunk replies, retransmission, ECN, timer management, heartbeat/probe handling, transport state changes, association failure, FWD-TSN, AUTH shared keys, stream reset, and ASCONF queue purge. `union sctp_arg` carries typed arguments. Constructor macros build typed args such as `SCTP_CHUNK()`, `SCTP_ASOC()`, `SCTP_TRANSPORT()`, and `SCTP_STATE()`. `struct sctp_cmd_seq` stores up to `SCTP_MAX_NUM_COMMANDS` commands, filled backward and iterated by `sctp_next_cmd()`.

## Control Flow
State functions append commands with `sctp_add_cmd_sf()`. The side-effect engine later walks commands in intended order via `sctp_next_cmd()`, applying transport, association, timer, and ULP actions.

## State And Persistence
Command sequences are transient per event. Persistent effects occur only when interpreted against associations, transports, queues, and sockets.

## Dependencies And Integration Points
It includes SCTP constants and structs, so it connects the state-machine tables to all main SCTP objects. It is central to `sm.h` state functions and primitive/chunk/timeout handling.

## Risks And Test Signals
Risks include command overflow causing `BUG_ON`, mismatched union member use, missing commands for new state transitions, and ordering-dependent behavior. Test signals include handshake, shutdown, retransmission, ECN, ASCONF, AUTH, and stream-reset state-machine coverage with command tracing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/sctp/command.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/sctp/constants.h -->
# sources/distributed-fs/ceph-client/include/net/sctp/constants.h

## Purpose
This header centralizes SCTP internal constants, state/event enumerations, default timers, retransmission parameters, path MTU probing limits, address scope policy, xmit results, and AUTH constants.

## Important APIs, Types, And Functions
It defines stream defaults, chunk-type counts, event families (`sctp_event_type`, timeouts, primitives, other events), `union sctp_subtype` constructors, internal errors, association states, socket-state mappings, PLPMTUD states, TSN map sizes, duplicate/gap limits, default heartbeat/SACK/RTO/cookie/rwnd/MTU values, UDP encapsulation port, PF exposure modes, transmit outcomes, transport commands, retransmit/lower-cwnd reasons, address scopes, bind-copy flags, and HMAC identifiers. Name helpers `sctp_cname()`, `sctp_oname()`, `sctp_tname()`, and `sctp_pname()` support diagnostics.

## Control Flow
The state machine indexes by state, event type, and subtype values declared here. Timers and retransmission code use the timeout enumerations and defaults. Transport and congestion-control code use the xmit/retransmit/cwnd enums.

## State And Persistence
The file itself has no mutable state. Its values shape persistent association, transport, and socket configuration initialized elsewhere.

## Dependencies And Integration Points
It depends on SCTP UAPI, IPv6 headers, and TCP socket states. It feeds almost every SCTP header in this set, especially `command.h`, `sm.h`, `sctp.h`, `structs.h`, and `tsnmap.h`.

## Risks And Test Signals
Risks include ABI-visible state mismatches, default timer regressions, TSN gap overflow, incorrect AUTH chunk counts, and PLPMTUD boundary errors. Test signals are state-table coverage, sysctl/default propagation tests, PLPMTUD probing, SACK gap/dup generation, AUTH negotiation, and address scope filtering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/sctp/constants.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/sctp/sctp.h -->
# sources/distributed-fs/ceph-client/include/net/sctp/sctp.h

## Purpose
This is the base SCTP internal header. It gathers subsystem prototypes, global caches/sysctls, SNMP statistic macros, protocol registration hooks, socket helpers, packet receive/error paths, transport hash traversal, primitive entry points, IPv6 optional hooks, and inline utility functions.

## Important APIs, Types, And Functions
It declares protocol/socket APIs (`sctp_inet_connect()`, `sctp_backlog_rcv()`, `sctp_poll()`), primitive functions (`ASSOCIATE`, `SHUTDOWN`, `ABORT`, `SEND`, `ASCONF`, `RECONF`), input/error handlers, transport hash lookup/traversal, proc/offload/scheduler setup, stream reset calls, caches, sysctl arrays, MIB counters, debug object counters, sysctl registration, IPv6 registration stubs, association-id mapping, list helpers, skb ownership, parameter/error walkers, hash functions, socket/association state predicates, v4/v6 address mapping, PMTU helpers, PLPMTUD state helpers, and `sctp_sock_set_nodelay()`.

## Control Flow
Upper-layer socket operations call primitives, primitives enter the state machine, and commands drive output/input queues. Receive paths enter `sctp_rcv()` and error handlers locate endpoints/transports. Timers and PMTU helpers update transport state and can reschedule probe timers.

## State And Persistence
Persistent state is external: per-net stats, global caches, association idr, transport hash, sysctls, and object counters. Inline helpers update association stats and socket memory accounting.

## Dependencies And Integration Points
It integrates SCTP with inet protosw, sockets, procfs, SNMP, sysctl, IPv6, offload, stream schedulers, rhashtable transport lookup, and kernel memory accounting.

## Risks And Test Signals
Risks include hash-size power-of-two assumptions, skb receive accounting errors, PMTU underflow, address-family mapping mistakes, stale dst cache handling, and config-stub mismatches. Test signals include IPv4/IPv6 SCTP module load, connect/listen/send/recv, ICMP error handling, sysctl registration, SNMP counters, PMTU changes, and UDP encapsulation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/sctp/sctp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/sctp/sm.h -->
# sources/distributed-fs/ceph-client/include/net/sctp/sm.h

## Purpose
This header declares the SCTP state-machine interface: event dispositions, state-function signatures, timer function type, table entries, and the large set of state functions used for chunks, timers, primitives, and protocol validation.

## Important APIs, Types, And Functions
`enum sctp_disposition` describes state-function outcomes such as discard, consume, no-memory, delete TCB, abort, violation, not implemented, user error, and bug. `sctp_state_fn_t` is the uniform state-function signature taking net, endpoint, association, subtype, event arg, and command sequence. `struct sctp_sm_table_entry` pairs a function pointer with a debug name. Prototypes include generic `sctp_sf_not_impl`/`bug`, timer handlers, INIT/COOKIE/DATA/SACK/SHUTDOWN/ERROR handlers, primitive handlers, and validation helpers.

## Control Flow
The SCTP engine selects a state table by event type and current association state, invokes the matching `sctp_sf_*` function, then interprets the emitted `sctp_cmd_seq` if the disposition permits further side effects.

## State And Persistence
The header owns no state, but state functions mutate associations, transports, queues, and timers through commands rather than direct side effects where possible.

## Dependencies And Integration Points
It depends on `command.h`, `sctp.h`, core SCTP structures, and kernel allocation/types. It integrates with receive chunk classification, ULP primitives, timeout callbacks, and diagnostics through function names.

## Risks And Test Signals
Risks include missing table entries, wrong disposition semantics, command emission order bugs, and validation bypasses for malformed chunks. Test signals are protocol conformance tests for handshake, duplicate INIT, shutdown, abort, stale cookie, invalid stream, SACK/FWD-TSN, timeout, and primitive handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/sctp/sm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/sctp/stream_interleave.h -->
# sources/distributed-fs/ceph-client/include/net/sctp/stream_interleave.h

## Purpose
This header defines the pluggable SCTP stream-interleaving operations used to support classic DATA/SSN and interleaved I-DATA/MID/FSN formats.

## Important APIs, Types, And Functions
`struct sctp_stream_interleave` contains chunk/header lengths and callbacks for data chunk creation, assignment, validation, event creation, TSN/FSN handling, FWD-TSN generation/skip, and stream sequence skipping. `sctp_stream_interleave_init()` selects/initializes the stream interleave mode on an `sctp_stream`.

## Control Flow
Send paths use the active interleave ops to build DATA or I-DATA chunks and assign stream sequence metadata. Receive and ULP queue paths use validation, event creation, and reassembly helpers appropriate to the negotiated interleaving capability.

## State And Persistence
The persistent selector is `sctp_stream::si`; stream in/out entries hold either SSN or MID/MID_UO/FSN state depending on mode.

## Dependencies And Integration Points
It integrates with `structs.h` stream definitions, ULP queue reassembly, PR-SCTP FWD-TSN handling, and association capability negotiation (`intl_capable`).

## Risks And Test Signals
Risks include mixing SSN and MID state, wrong chunk length calculations, reassembly ordering bugs, and FWD-TSN skip errors. Test signals include interleaving negotiation, fragmented unordered/ordered messages, classic non-interleaved fallback, and stream reset with I-DATA traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/sctp/stream_interleave.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/sctp/stream_sched.h -->
# sources/distributed-fs/ceph-client/include/net/sctp/stream_sched.h

## Purpose
This header defines the SCTP outbound stream scheduler abstraction and registration/init APIs for scheduler algorithms such as priority, round-robin, fair-capacity, and weighted fair queueing.

## Important APIs, Types, And Functions
`struct sctp_sched_ops` supplies callbacks for scheduler `set`, `get`, `init`, `init_sid`, `free`, enqueue/dequeue, dequeue completion, scheduling-all, and per-stream value get/set. Public APIs choose and query schedulers (`sctp_sched_set_sched()`, `sctp_sched_get_sched()`), configure stream values, notify dequeue completion, initialize stream ids, register scheduler ops, and initialize built-in scheduler families.

## Control Flow
Outbound chunks enter `sctp_outq` and are enqueued through the selected scheduler. Dequeue picks the next eligible chunk/stream; `sctp_sched_dequeue_done()` and `sctp_sched_dequeue_common()` update scheduler-specific stream state after transmission.

## State And Persistence
Scheduler state persists in `sctp_stream` and `sctp_stream_out_ext` lists/weights/priorities plus `sctp_outq::sched`. Per-stream values may represent priority, weight, or algorithm-specific controls.

## Dependencies And Integration Points
It integrates with `struct sctp_association`, `sctp_outq`, `sctp_chunk`, `sctp_stream`, and SCTP socket options that set stream scheduler type or values.

## Risks And Test Signals
Risks include starvation, list corruption, scheduler changes with queued data, uninitialized stream extensions, and value interpretation mismatches. Test signals include multi-stream send fairness, priority/round-robin behavior, scheduler socket options, stream add/reset, and retransmission interaction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/sctp/stream_sched.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/sctp/structs.h -->
# sources/distributed-fs/ceph-client/include/net/sctp/structs.h

## Purpose
This is the main SCTP data-model header. It defines address abstractions, global hash state, per-socket options, cookies, parameters, address-family operations, messages/chunks/packets, transports, in/out queues, bind addresses, endpoints, streams, associations, cmsg parsing, and debug counters.

## Important APIs, Types, And Functions
Important structures include `union sctp_addr`, `struct sctp_globals`, `struct sctp_sock`, `struct sctp_cookie`, `struct sctp_signed_cookie`, `union sctp_params`, `struct sctp_af`, `struct sctp_pf`, `struct sctp_datamsg`, `struct sctp_chunk`, `struct sctp_packet`, `struct sctp_transport`, `struct sctp_inq`, `struct sctp_outq`, `struct sctp_bind_addr`, `struct sctp_ep_common`, `struct sctp_endpoint`, stream structs, `struct sctp_priv_assoc_stats`, and `struct sctp_association`. APIs cover stream init/free/update, AF/PF registration, datamsg/chunk lifecycle, packet assembly/transmit, transport routing/timers/congestion/PMTU, in/out queue management, bind address operations, endpoint lookup/refcounting, INIT verification/processing, association lifecycle/update/peer management, ASCONF ACK cache, and address comparison.

## Control Flow
Sockets own `sctp_sock` and an endpoint. Associations inherit endpoint binding, negotiate cookie/peer capabilities, create transports, receive chunks through `sctp_inq`, reorder/deliver data through `sctp_ulpq`, and transmit via `sctp_outq`, stream scheduler, packet bundling, and transport xmit callbacks. Handshake state stores peer INIT/cookie data; established paths update TSN maps, rwnd, congestion, timers, AUTH, ASCONF, and stream-reset state.

## State And Persistence
This file defines nearly all persistent SCTP kernel state: global endpoint/port/transport hashes, socket defaults, endpoint shared keys and feature flags, association TCB fields, peer transport lists, timers, queues, buffer accounting, stream sequence numbers, retransmission lists, ASCONF queues, AUTH keys, security IDs, and RCU/refcount lifetime.

## Dependencies And Integration Points
It depends on crypto SHA keys, radix trees, rhashtable, sockets, IPv4/IPv6 headers, sk_buffs, workqueues, SCTP UAPI structs, SCTP auth, TSN maps, ULP events/queues, and stream interleaving. It is the shared contract for SCTP protocol, input, output, state-machine, socket, proc, and stream files.

## Risks And Test Signals
Risk is broad: refcount/RCU lifetime, timer cancellation, transport hash consistency, chunk ownership, skb control block reuse, PMTU/congestion accounting, authentication key lifetime, stream interleaving sequence state, ASCONF serialization, rwnd/sndbuf accounting, and security label propagation. Test signals include full SCTP connect/send/shutdown, multihoming failover, retransmission, SACK gaps, PR-SCTP abandon/FWD-TSN, AUTH, ADDIP/ASCONF, stream reset/add, PLPMTUD, peeloff, IPv6, UDP encapsulation, and memory-leak/object-counter tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/sctp/structs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/sctp/tsnmap.h -->
# sources/distributed-fs/ceph-client/include/net/sctp/tsnmap.h

## Purpose
This header defines the TSN map used by SCTP receive paths to track cumulative acknowledgments, out-of-order data, gaps, duplicates, and pending data for SACK generation.

## Important APIs, Types, And Functions
`struct sctp_tsnmap` stores the bitmap, base TSN, cumulative TSN ACK point, max TSN seen, length, pending data count, and duplicate TSN list. APIs initialize/free maps, check/mark/skip TSNs, compute gap blocks, refresh pending counts, mark duplicates, and renege received TSNs. Inline getters expose cumulative TSN, max seen TSN, duplicate count/list, and gap status.

## Control Flow
When DATA arrives, receive code checks validity, marks the TSN, advances cumulative ack when possible, records duplicates, and later converts gaps/duplicates into SACK fields. FWD-TSN and reneging paths skip or unmark ranges.

## State And Persistence
TSN maps persist inside `sctp_association::peer.tsn_map`. Duplicate reports are reset when `sctp_tsnmap_get_dups()` hands the array to SACK construction.

## Dependencies And Integration Points
It depends on SCTP constants and gap ack UAPI structures. It integrates with association receive state, SACK generation, ULP queue reneging, and PR-SCTP/FWD-TSN handling.

## Risks And Test Signals
Risks include sequence wrap errors, gap-block overflow, duplicate suppression, pending-data drift, and reneging inconsistency. Test signals are out-of-order delivery, duplicate DATA, large TSN gaps near configured limits, SACK gap block generation, FWD-TSN skip, and receive-buffer pressure reneging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/sctp/tsnmap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/sctp/ulpevent.h -->
# sources/distributed-fs/ceph-client/include/net/sctp/ulpevent.h

## Purpose
This header defines `sctp_ulpevent`, the compact event object stored in `skb->cb` to deliver SCTP data and notifications from the state machine to the socket upper layer.

## Important APIs, Types, And Functions
`struct sctp_ulpevent` carries association, chunk, receive-memory length, stream sequence or message id, PPID or FSN, TSN, cumulative TSN, stream, flags, and message flags. Helpers convert between event and skb. Factory APIs create association-change, peer-address-change, remote-error, send-failed, shutdown, partial-delivery, adaptation, receive-message, auth-key, sender-dry, stream-reset, association-reset, stream-change, and reassembled-message events. Reader APIs fill `sndrcvinfo`, `rcvinfo`, and `nxtinfo`; subscription helpers set and test notification bits.

## Control Flow
SCTP receive/reassembly builds data events, state-machine side effects build notifications, and ULP queue/socket receive paths deliver only notifications enabled by the socket subscription mask.

## State And Persistence
Events live inside skb control buffers and carry receive-memory accounting length for socket ownership. Subscription masks persist in socket/association state.

## Dependencies And Integration Points
It integrates with `sk_buff`, SCTP chunks/associations/transports, socket ancillary data, notification UAPI structs, and `sctp_ulpq`.

## Risks And Test Signals
Risks include `skb->cb` size overflow, packed-layout assumptions, stale association pointers, notification filtering bugs, and receive-memory accounting mismatch. Test signals include all SCTP notification socket options, fragmented reassembly events, send failure, auth key notifications, stream reset/change, and partial delivery API events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/sctp/ulpevent.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/sctp/ulpqueue.h -->
# sources/distributed-fs/ceph-client/include/net/sctp/ulpqueue.h

## Purpose
This header defines the SCTP upper-layer protocol queue, which reassembles, orders, partially delivers, reneges, and forwards data/events from SCTP core to sockets.

## Important APIs, Types, And Functions
`struct sctp_ulpq` tracks partial-delivery mode, owning association, ordered reassembly queue, unordered reassembly queue, and lobby queue. APIs initialize, flush, free, append DATA chunks, append event skb lists, renege data, perform or abort partial delivery, clear socket partial-delivery state, skip SSNs, flush reassembly by TSN, and renege queued lists.

## Control Flow
Inbound DATA chunks enter `sctp_ulpq_tail_data()`, where reassembly and ordering decide whether to produce ULP events or hold chunks. Memory pressure can call reneging helpers. Partial delivery moves data up before full message completion when thresholds require it.

## State And Persistence
ULP queue state persists per association in `sctp_association::ulpq`. Queues hold skb-backed events/chunks until delivered, reneged, or flushed.

## Dependencies And Integration Points
It integrates with SCTP association state, stream interleaving, TSN map reneging, socket receive queues, and ULP events.

## Risks And Test Signals
Risks include ordered/unordered reassembly bugs, partial delivery deadlock, SSN skip mistakes, memory pressure losing accounting, and event ordering regressions. Test signals include fragmented ordered and unordered messages, partial delivery thresholds, receive-buffer pressure, stream reset skip, and FWD-TSN flush behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/sctp/ulpqueue.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/secure_seq.h -->
# sources/distributed-fs/ceph-client/include/net/secure_seq.h

## Purpose
This header declares secure per-flow sequence and ephemeral-port hash helpers used by TCP and related networking code to generate hard-to-predict initial sequence numbers, timestamp offsets, and port-selection hashes.

## Important APIs, Types, And Functions
`union tcp_seq_and_ts_off` overlays a 64-bit hash with 32-bit TCP sequence and timestamp offset fields. APIs include `secure_ipv4_port_ephemeral()`, `secure_ipv6_port_ephemeral()`, `secure_tcp_seq_and_ts_off()`, and `secure_tcpv6_seq_and_ts_off()`. Inline compatibility helpers `secure_tcp_seq()` and `secure_tcpv6_seq()` use `init_net` and return only the sequence half.

## Control Flow
Protocol code supplies source/destination addresses and ports. The implementation returns deterministic secret-keyed values for the flow and network namespace; callers use either the full sequence/timestamp pair or only the sequence value.

## State And Persistence
No state is declared here. Security depends on hidden secret material maintained by the implementation and network namespace context.

## Dependencies And Integration Points
It depends on Linux integer/endian types and `struct net`. It integrates with TCP ISN generation, timestamp randomization, and ephemeral port selection for IPv4 and IPv6.

## Risks And Test Signals
Risks include namespace confusion through init_net wrappers, weak hash secret rotation, endian mistakes, and flow-collision behavior. Test signals are TCP connection establishment, timestamp offset distribution, per-net namespace behavior, and port-randomization collision/regression tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/secure_seq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/seg6.h -->
# sources/distributed-fs/ceph-client/include/net/seg6.h

## Purpose
This header declares core IPv6 Segment Routing (SRv6) helpers, per-net state, checksum adjustment helpers, initialization hooks, SRH validation/extraction, encapsulation/inline insertion, ICMP handling, and nexthop lookup.

## Important APIs, Types, And Functions
`update_csum_diff4()` and `update_csum_diff16()` update skb checksums after 32-bit or IPv6-address changes. `struct seg6_pernet_data` stores the per-net lock, RCU tunnel source address, and optional HMAC rhashtable. `seg6_pernet()` fetches per-net SR data when IPv6 is enabled. Init/exit functions cover core, lwtunnel, and local actions with stubs when disabled. Runtime APIs include `seg6_validate_srh()`, `seg6_get_srh()`, `seg6_icmp_srh()`, `seg6_do_srh_encap()`, `seg6_do_srh_inline()`, `seg6_lookup_nexthop()`, and `seg6_get_daddr()`.

## Control Flow
SRv6 tunnel/local code validates or locates SRHs, updates headers/checksums during inline or encapsulation operations, and resolves next hops. ICMP paths can recover the true destination from an SRH via skb IPv6 control block flags.

## State And Persistence
Per-net SRv6 state persists in `net->ipv6.seg6_data`, with tunnel source protected by RCU and configuration updates serialized by a mutex.

## Dependencies And Integration Points
It integrates with IPv6, lightweight tunnels, SRH UAPI, rhashtable HMAC storage, sk_buffs, and routing lookups.

## Risks And Test Signals
Risks include malformed SRH parsing, checksum update errors, RCU tunnel-source lifetime, feature-stub mismatches, and ICMP destination confusion. Test signals include SRH validation, lwtunnel encapsulation/inline routes, HMAC-enabled configs, ICMP errors containing SRH, and IPv6-disabled builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/seg6.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/seg6_hmac.h -->
# sources/distributed-fs/ceph-client/include/net/seg6_hmac.h

## Purpose
This header defines SRv6 HMAC key storage and validation APIs for authenticated Segment Routing Headers.

## Important APIs, Types, And Functions
`SEG6_HMAC_RING_SIZE` sets a ring size used by implementation internals. `struct seg6_hmac_info` stores rhashtable/RCU nodes, key id, raw secret for userspace reporting, secret length, algorithm id, and prepared SHA1/SHA256 HMAC keys. APIs compute HMACs over SRH/source address, look up/add/delete key info in a net namespace, push HMAC TLVs, validate skb SRH HMAC, and initialize/exit per-net HMAC state.

## Control Flow
Configuration paths add/delete keys in the per-net rhashtable. Packet output can push HMACs using a selected key, while input validation looks up key id and recomputes the HMAC for comparison.

## State And Persistence
HMAC key objects persist per network namespace in SRv6 per-net data and are RCU-freed. Raw secrets are retained specifically for netlink/userspace export.

## Dependencies And Integration Points
It depends on crypto SHA1/SHA256 HMAC key types, SRv6 core state, IPv6/SRH headers, routing, sockets, and rhashtable.

## Risks And Test Signals
Risks include key lifetime races, raw secret exposure, unsupported algorithm handling, incorrect HMAC coverage, and config-disabled stubs. Test signals include SRv6 HMAC netlink configuration, packet validation accept/reject, key deletion under traffic, namespace teardown, and SHA1/SHA256 algorithm cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/seg6_hmac.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/seg6_local.h -->
# sources/distributed-fs/ceph-client/include/net/seg6_local.h

## Purpose
This header declares SRv6 local-action helpers, especially BPF-facing SRH validity state and nexthop lookup support.

## Important APIs, Types, And Functions
It declares `seg6_lookup_nexthop()` and `seg6_bpf_has_valid_srh()`. `struct seg6_bpf_srh_state` stores a per-cpu local lock, current SRH pointer, header length, and validity flag. `DECLARE_PER_CPU(seg6_bpf_srh_states)` exposes per-cpu BPF SRH state.

## Control Flow
SRv6 local processing and BPF helpers use per-cpu state to expose a currently validated SRH while avoiding cross-CPU sharing. Nexthop lookup is shared with core SRv6 route handling.

## State And Persistence
State is per CPU and transient for packet/BPF processing. `local_lock_t` protects bottom-half local access to the current SRH pointer and validity metadata.

## Dependencies And Integration Points
It integrates with IPv6 sk_buffs, SRv6 local actions, BPF helpers, and the SRv6 core nexthop lookup API.

## Risks And Test Signals
Risks include stale per-cpu SRH pointers, missing local lock coverage, BPF helpers accepting invalid SRH state, and nexthop lookup inconsistencies. Test signals include SRv6 BPF local action tests, concurrent softirq traffic, invalid SRH rejection, and route lookup behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/seg6_local.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/selftests.h -->
# sources/distributed-fs/ceph-client/include/net/selftests.h

## Purpose
This header defines a small generic network selftest interface for drivers/devices that support ethtool self-tests with loopback packets.

## Important APIs, Types, And Functions
`struct net_packet_attrs` describes packet addresses, TCP/UDP ports, timeout, size bounds, id, queue mapping, VLAN/checksum traits, and checksum corruption. `struct net_test_priv` tracks a packet, packet handler, completion, VLAN data, and result. `struct netsfhdr` is the test payload header with version, magic, and id. Constants define packet size, magic value, and default timeout. APIs are `net_test_get_skb()`, `net_selftest()`, `net_selftest_get_count()`, and `net_selftest_get_strings()`, with no-op stubs unless `CONFIG_NET_SELFTESTS` is enabled.

## Control Flow
Drivers call the selftest entry point from ethtool test operations. Enabled builds generate skb test packets, install a packet handler, wait for completion, and fill result buffers/strings.

## State And Persistence
State is per test invocation through `net_test_priv`; no persistent global state is declared here.

## Dependencies And Integration Points
It depends on ethtool and netdevice APIs and integrates with driver ethtool self-test callbacks and packet receive hooks.

## Risks And Test Signals
Risks include false failures from timeout sizing, queue mapping mismatch, packet handler leaks, checksum/VLAN coverage gaps, and stubs hiding untested builds. Test signals are ethtool self-test runs on supported devices, loopback packet receipt, bad-checksum negative tests, VLAN variants, and disabled-config compile checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/selftests.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/slhc_vj.h -->
# sources/distributed-fs/ceph-client/include/net/slhc_vj.h

## Purpose
This legacy header defines Van Jacobson TCP/IP header compression state and APIs for SLIP/PPP-style low-bandwidth links.

## Important APIs, Types, And Functions
Constants define compressed packet types (`SL_TYPE_IP`, `SL_TYPE_UNCOMPRESSED_TCP`, `SL_TYPE_COMPRESSED_TCP`), changed-field flags (`NEW_C`, `NEW_I`, `NEW_S`, `NEW_A`, `NEW_W`, `NEW_U`), special cases, and push-bit handling. `struct cstate` stores per-conversation cached IP/TCP headers, options, header size, connection id, and ring linkage. `struct slcompress` stores transmit/receive state arrays, slot limits, current/oldest ids, toss flag, and detailed in/out counters. APIs are `slhc_init()`, `slhc_free()`, `slhc_compress()`, `slhc_uncompress()`, `slhc_remember()`, and `slhc_toss()`.

## Control Flow
Transmit compression searches cached connection state, emits compressed or uncompressed TCP packets, and updates counters. Receive decompression uses the connection id to reconstruct full headers; on errors it enters toss mode until an uncompressed packet resynchronizes state.

## State And Persistence
Compression state persists per serial link in `struct slcompress`, with cached headers per slot and counters useful for diagnostics.

## Dependencies And Integration Points
It depends on IPv4 and TCP header structs and is integrated by SLIP/PPP compression implementations rather than mainstream Ethernet paths.

## Risks And Test Signals
Risks include stale header reconstruction, option buffer bounds, slot-id desynchronization, endian/sequence delta mistakes, and toss-mode recovery failures. Test signals are compressed/uncompressed TCP round trips, packet loss resync, option-bearing TCP headers, slot-limit edge cases, and counter accuracy.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/slhc_vj.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/smc.h -->
# sources/distributed-fs/ceph-client/include/net/smc.h

## Purpose
This header exposes shared SMC socket and device-facing definitions for Shared Memory Communications over RDMA/ISM, plus optional BPF handshake-control hooks.

## Important APIs, Types, And Functions
`SMC_MAX_PNETID_LEN` sizes PNET identifiers. `struct smc_hashinfo` stores a lock and hlist hash table. `struct smcd_gid` carries ISM GID values. `struct smcd_dev` describes an ISM device: DIBS device pointer, connection array, VLAN list, event workqueue, PNET id and ownership flag, link-group list/lock/count, deletion waitqueue, and going-away flag. `struct smc_hs_ctrl` registers named handshake-control callbacks for SYN and SYN-ACK option decisions, with inheritable flags. `smc_call_hsbpf()` invokes configured callbacks under RCU when BPF control is enabled, otherwise returns the initial value.

## Control Flow
TCP handshake paths can call `smc_call_hsbpf()` before emitting or responding to SMC options. SMC device management uses `smcd_dev` to coordinate connections, VLANs, events, link groups, and teardown.

## State And Persistence
Persistent state includes per-net handshake controller pointers, SMC hash tables, and long-lived ISM device objects with locks, workqueues, and atomic counters.

## Dependencies And Integration Points
It depends on device, spinlock, waitqueue, DIBS, TCP sock, inet request sock, RCU, and optional `CONFIG_SMC_HS_CTRL_BPF`. It integrates with SMC-R/SMC-D connection setup and TCP option negotiation.

## Risks And Test Signals
Risks include RCU callback lifetime, device teardown races, PNET id ownership mistakes, SYN/SYN-ACK policy mismatches, and BPF-disabled behavior drift. Test signals include SMC option negotiation, BPF handshake control, ISM device removal, VLAN/link-group cleanup, and per-net controller inheritance.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/smc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/snmp.h -->
# sources/distributed-fs/ceph-client/include/net/snmp.h

## Purpose
This header defines kernel-side SNMP/MIB statistic storage wrappers and update macros for IP, ICMP, TCP, UDP, Linux, XFRM, and TLS networking counters.

## Important APIs, Types, And Functions
It defines `struct snmp_mib` name/entry descriptors and per-protocol MIB wrapper structs with arrays sized from UAPI enums, including `ipstats_mib`, `icmp_mib`, `icmpmsg_mib`, `icmpv6_mib`, device variants, `tcp_mib`, `udp_mib`, `linux_mib`, `linux_xfrm_mib`, and `linux_tls_mib`. Macros define per-cpu or atomic stat declarations and update helpers: `DEFINE_SNMP_STAT`, `DECLARE_SNMP_STAT`, `SNMP_INC_STATS`, `SNMP_DEC_STATS`, `SNMP_ADD_STATS`, packet/octet pair updates, and 64-bit variants using `u64_stats` synchronization on 64-bit stat builds.

## Control Flow
Protocol code updates per-net/per-cpu counters through macros. `/proc` and seq-file export code reads these arrays and maps entries to names using MIB descriptors.

## State And Persistence
Counters persist in per-net protocol statistic storage, often per-cpu for low overhead. 64-bit updates use synchronization to avoid torn reads.

## Dependencies And Integration Points
It depends on Linux SNMP UAPI enums, SMP/per-cpu support, cache alignment, and `u64_stats`. SCTP and other protocols wrap these macros for their own MIBs.

## Risks And Test Signals
Risks include wrong enum sizing, torn 64-bit stats, per-cpu aggregation mistakes, atomic/per-cpu mismatch, and packet/octet pair update inconsistencies. Test signals include `/proc/net/snmp` and related proc outputs, protocol counter increments under traffic, 32-bit build reads, and namespace-specific statistics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/snmp.h -->
