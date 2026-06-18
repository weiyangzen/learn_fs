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
