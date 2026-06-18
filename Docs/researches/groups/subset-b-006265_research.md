# subset-b-006265 Research

Grouped code research for the Ceph client copy of Linux AF_RXRPC local/peer endpoint management, packet send/receive, diagnostics, RTT, security, RxGK/RxKAD, and rxperf test server files. Each section preserves the source path in its title and is bounded by reconciliation markers for source-tree-aligned splitting.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rxrpc/local_event.c -->
# sources/distributed-fs/ceph-client/net/rxrpc/local_event.c

## Purpose
`local_event.c` handles small local-endpoint events that are not part of normal call data delivery, currently the AF_RXRPC VERSION packet response path. It builds the Linux version identity string and replies to remote VERSION requests using the local UDP transport socket.

## Important APIs, Types, And Functions
The file exposes `rxrpc_gen_version_string()` and `rxrpc_send_version_request()`. It uses `rxrpc_version_string`, `struct rxrpc_wire_header`, `struct rxrpc_host_header`, `struct rxrpc_skb_priv`, `struct sockaddr_rxrpc`, `rxrpc_extract_addr_from_skb()`, `kernel_sendmsg()`, and TX tracepoints.

## Control Flow
Module setup calls `rxrpc_gen_version_string()` to fill a bounded `"linux-<UTS_RELEASE> AF_RXRPC"` string. On a VERSION request, `rxrpc_send_version_request()` extracts the source transport address from the received SKB, mirrors the received epoch, cid, call number, service ID, and opposite client/server direction bit into a VERSION reply header, appends the version string, and sends both buffers through `local->socket`.

## State And Persistence
The only persistent state is the static 65-byte version string. Per-packet state is stack-local and derived from the incoming SKB. No endpoint refcount or queue state is mutated; the function assumes the caller owns a live `rxrpc_local`.

## Dependencies And Integration Points
This file integrates with the UDP socket established by `local_object.c`, packet layout from `protocol.h`, address extraction helpers, kernel release metadata, and rxrpc tracing. It is part of the non-call packet handling path used by local endpoint receive dispatch.

## Risks And Edge Cases
If source address extraction fails, the request is silently ignored. The version string is fixed-size and deliberately truncates long `UTS_RELEASE` values. The response uses `kernel_sendmsg()` directly rather than the `do_udp_sendmsg()` helper, so IPv6 behavior depends on the bound socket context already being correct.

## Test Signals
Useful checks include VERSION request/reply interoperability, IPv4 and IPv6 source address extraction, tracepoint emission for send failures and successes, long release-string truncation, and endpoint teardown races where a request arrives while the local socket is shutting down.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rxrpc/local_event.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rxrpc/local_object.c -->
# sources/distributed-fs/ceph-client/net/rxrpc/local_object.c

## Purpose
`local_object.c` manages AF_RXRPC local endpoint objects. It allocates, deduplicates, references, activates, deactivates, opens, and destroys the UDP tunnel socket backing an rxrpc local address, and it owns local endpoint list membership in the per-network namespace.

## Important APIs, Types, And Functions
Important functions include `rxrpc_lookup_local()`, `rxrpc_get_local()`, `rxrpc_get_local_maybe()`, `rxrpc_put_local()`, `rxrpc_use_local()`, `rxrpc_unuse_local()`, `rxrpc_destroy_local()`, `rxrpc_destroy_all_locals()`, and `rxrpc_local_dont_fragment()`. Internal helpers include `rxrpc_alloc_local()`, `rxrpc_open_socket()`, `rxrpc_local_cmp_key()`, `rxrpc_encap_err_rcv()`, and the client connection reap timer callback.

## Control Flow
Lookup takes `rxnet->local_mutex`, searches `rxnet->local_endpoints` for an address match ignoring service ID, rejects service socket sharing, tries to reuse a live endpoint, or allocates a replacement/new object. Socket open creates a UDP socket, installs rxrpc tunnel callbacks and `sk_user_data`, enables ICMP error reporting and DF behavior, starts the `rxrpc_io_thread`, and publishes the thread pointer after readiness. Unuse decrements active users and stops the IO thread at zero. Destruction removes the endpoint from the namespace list, cleans local connections, shuts down and releases the socket, purges receive queues, drops client connections, and drains the page fragment cache before RCU frees the object.

## State And Persistence
Persistent state lives in `struct rxrpc_local`: `ref`, `active_users`, net/rxnet pointers, socket, IO thread, endpoint address, service lock, queues, connection IDs, client bundle/connection structures, timers, and debug ID. List membership is protected by `local_mutex` and RCU; lifetime combines refcounting with an active-user count that controls transport shutdown.

## Dependencies And Integration Points
The file depends on UDP tunnel setup, IPv4/IPv6 ICMP error delivery, per-net namespace storage from `net_ns.c`, receive encapsulation in `rxrpc_encap_rcv`, IO thread processing, client/service connection cleanup, peer keepalive users, and tracing.

## Risks And Edge Cases
The code intentionally replaces dying endpoints but bind/open may still fail if the old socket still owns the address. Services cannot share a UDP endpoint with other services. `sk_user_data` and socket shutdown ordering are critical because callbacks can race teardown. Active-user and refcount transitions must stay paired to avoid stopping a socket while peers or calls still need it.

## Test Signals
Test endpoint reuse, duplicate service bind rejection, IPv4/IPv6 socket creation, ICMP error callback delivery, DF toggling, IO-thread start/stop, lookup races during endpoint death, namespace exit leak checks, and lockdep/RCU coverage around `local_endpoints`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rxrpc/local_object.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rxrpc/misc.c -->
# sources/distributed-fs/ceph-client/net/rxrpc/misc.c

## Purpose
`misc.c` centralizes AF_RXRPC runtime tunables and protocol defaults used by receive windows, delayed ACK scheduling, backlog sizing, jumbo packet handling, and optional receive-delay injection.

## Important APIs, Types, And Functions
The file exports global variables: `rxrpc_max_backlog`, `rxrpc_soft_ack_delay`, `rxrpc_idle_ack_delay`, `rxrpc_rx_window_size`, `rxrpc_rx_mtu`, `rxrpc_rx_jumbo_max`, and, when enabled, `rxrpc_inject_rx_delay`.

## Control Flow
There is no executable control flow. Other rxrpc subsystems read these variables to decide how many calls can be queued, when DELAY or IDLE ACKs should be scheduled, how many unconsumed packets may be retained, and what jumbo/PMTU capacity should be advertised.

## State And Persistence
The variables are process-global kernel module state rather than per-network namespace state. Defaults persist for the module lifetime. Some are marked `__read_mostly`; optional injection state exists only for builds with `CONFIG_AF_RXRPC_INJECT_RX_DELAY`.

## Dependencies And Integration Points
Receive-side ACK logic uses the delay/window values, ACK trailers in `output.c` advertise MTU/window values, PMTU handling uses `rxrpc_rx_mtu` and jumbo limits, socket listen paths use the backlog limit, and test/fault-injection paths use the delay knob.

## Risks And Edge Cases
Because the values are global, tuning one namespace affects all namespaces. Oversized receive windows or jumbo MTUs increase memory pressure; too-small windows or ACK delays can harm throughput. Fault-injection variables must not leak into production behavior unless explicitly configured.

## Test Signals
Useful signals include sysctl/module-parameter style coverage if wired elsewhere, ACK delay behavior under partial receives, receive-window overflow ACKs, jumbo advertisement correctness, and builds with and without receive-delay injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rxrpc/misc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rxrpc/net_ns.c -->
# sources/distributed-fs/ceph-client/net/rxrpc/net_ns.c

## Purpose
`net_ns.c` creates and tears down AF_RXRPC per-network namespace state. It initializes namespace-scoped call, connection, local endpoint, peer, keepalive, reaper, statistics, and `/proc/net/rxrpc` structures.

## Important APIs, Types, And Functions
The file defines `rxrpc_net_id`, `rxrpc_net_ops`, `rxrpc_init_net()`, `rxrpc_exit_net()`, `rxrpc_service_conn_reap_timeout()`, and `rxrpc_peer_keepalive_timeout()`. It initializes `struct rxrpc_net` fields and proc entries backed by seq operations from `proc.c`.

## Control Flow
Namespace init marks the rxrpc namespace live, generates a random epoch with `RXRPC_RANDOM_EPOCH`, initializes call and connection lists/counters/locks, service connection reaper work and timer, local endpoint list and mutex, peer hash and keepalive buckets, and creates proc entries for calls, conns, bundles, peers, locals, and stats. Namespace exit marks the namespace dead, synchronously stops keepalive timers/work, destroys calls, connections, peers, and locals, then removes proc state.

## State And Persistence
State persists in `struct rxrpc_net` for the lifetime of the network namespace. The `live` bit gates timers/work. The epoch tags outgoing packets from the namespace. Proc entries expose namespace-local runtime state and counters.

## Dependencies And Integration Points
This file integrates with Linux pernet operations, procfs, call/connection/peer/local object destructors, peer keepalive worker, service connection reaper, and statistics display/clear support.

## Risks And Edge Cases
Exit ordering is important: timers can rearm work, so the peer keepalive timer is deleted both before and after work cancellation. Calls and connections must be gone before peers and locals are leak-checked. Proc creation failures leave the namespace non-live and abort initialization.

## Test Signals
Exercise namespace create/destroy loops, proc entry visibility per namespace, timer/work cancellation on namespace teardown, leak diagnostics from destroy-all functions, and concurrent sockets active during namespace shutdown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rxrpc/net_ns.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rxrpc/oob.c -->
# sources/distributed-fs/ceph-client/net/rxrpc/oob.c

## Purpose
`oob.c` implements out-of-band message delivery and response handling, primarily for security challenge/response flows that must be surfaced to userspace or kernel services outside normal call data.

## Important APIs, Types, And Functions
Important APIs include `rxrpc_notify_socket_oob()`, `rxrpc_add_pending_oob()`, `rxrpc_sendmsg_oob()`, `rxrpc_kernel_query_oob()`, `rxrpc_kernel_dequeue_oob()`, `rxrpc_kernel_free_oob()`, `rxrpc_kernel_query_challenge()`, and `rxrpc_kernel_reject_challenge()`. Internal helpers parse `SOL_RXRPC` control messages and locate pending OOB SKBs by `RXRPC_OOB_ID`.

## Control Flow
Security code posts an OOB SKB with `rxrpc_notify_socket_oob()`. The function assigns a monotonically increasing OOB ID, queues the SKB on `recvmsg_oobq`, invokes app callbacks when present, or wakes userspace readers. `recvmsg()` exposes the message and moves response-required SKBs into a red-black pending tree. `sendmsg()` with OOB control messages parses `RXRPC_OOB_ID`, `RXRPC_RESPOND`, optional `RXRPC_ABORT`, and RxGK appdata, removes the matching pending SKB, then either aborts the connection or dispatches to the security module's `sendmsg_respond_to_challenge()`.

## State And Persistence
OOB state lives on `struct rxrpc_sock`: `recvmsg_oobq`, `pending_oobq`, `oob_id_counter`, `recvmsg_lock`, and optional app ops. SKBs carry the OOB type in `skb->mark`, the OOB ID in `skb_mstamp_ns`, and challenge connection references in `rxrpc_skb_priv`.

## Dependencies And Integration Points
This file integrates with `recvmsg.c`, `sendmsg` control-message parsing, security challenge handlers in RxGK/RxKAD, socket callbacks, SKB ref tracking, and kernel-service exported APIs.

## Risks And Edge Cases
The pending tree assumes the 64-bit OOB ID counter will not wrap. A response without a valid ID returns `-EBADSLT`; wrong OOB type returns protocol errors. Connection references must be released exactly once when an OOB SKB is freed. Socket-close state suppresses new OOB notifications.

## Test Signals
Cover userspace challenge receive/respond, invalid/missing duplicate control messages, challenge rejection, kernel dequeue/free/query paths, pending OOB lookup/removal, app callback versus `sk_data_ready`, and socket close while OOB messages are queued.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rxrpc/oob.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rxrpc/output.c -->
# sources/distributed-fs/ceph-client/net/rxrpc/output.c

## Purpose
`output.c` is the AF_RXRPC packet transmission engine. It sends ACKs, PMTU probes, call and connection aborts, DATA and jumbo DATA packets, reject packets, keepalive VERSION packets, and security RESPONSE packets through the local UDP socket.

## Important APIs, Types, And Functions
Important functions include `do_udp_sendmsg()`, `rxrpc_send_ACK()`, `rxrpc_send_probe_for_pmtud()`, `rxrpc_send_abort_packet()`, `rxrpc_send_data_packet()`, `rxrpc_send_conn_abort()`, `rxrpc_reject_packet()`, `rxrpc_send_keepalive()`, and `rxrpc_send_response()`. Internal helpers allocate/fill ACK buffers, start RTT probes, choose REQUEST_ACK reasons, prepare TX queue metadata, and assemble jumbo subpackets.

## Control Flow
ACK transmission allocates page-frag-backed header/SACK/trailer buffers, snapshots receive ACK-window state, fills ACK reason, SACK bytes, advertised receive window and MTU, optionally starts RTT or PMTU probes, and sends through UDP. DATA transmission allocates a wire header, obtains serials for all subpackets, updates TX queue RACK/TLP metadata, secures prebuilt txbufs, sets jumbo headers after the first subpacket, toggles DF according to PMTU/retransmission decisions, advances `tx_transmitted`, handles injected loss, maps send failures to call completion for unrecoverable initial/routing errors, and updates TX backoff. Control packet helpers build ABORT, BUSY, VERSION, and RESPONSE packets and trace outcomes.

## State And Persistence
The file mutates call transmission state: serials, ACK counters, RTT slots, keepalive deadlines, expected-RX timers, RACK/TLP timers, tx counts, `tx_backoff`, `tx_transmitted`, PMTU probe fields, and local page-frag buffers/kvec/bvec scratch arrays. Peer state receives last-transmit marks and PMTU probe flags.

## Dependencies And Integration Points
It depends on `protocol.h`, UDP/UDPv6 send paths, local endpoint DF controls, peer PMTU state, congestion/RACK/TLP helpers, security-prepared txbufs, response SKBs from RxGK/RxKAD, receive ACK state, tracepoints, and rxrpc statistics.

## Risks And Edge Cases
ACK buffer allocation may fail under pressure and drops the ACK. PMTU probes deliberately pad ACKs and must not exceed kvec capacity. Jumbo sequencing and serial assignment must remain consistent across TX queue boundaries. `-EMSGSIZE` is treated specially for PMTU feedback, while some routing errors complete calls. Abort suppression for client calls after all request data is hard-ACKed prevents wasting a reusable channel.

## Test Signals
High-value tests include DATA send/retransmit/jumbo paths, SACK ACK formatting, REQUEST_ACK reason counters, PMTU probe success/failure, IPv6 `do_udp_sendmsg()`, abort/reject packet formatting, connection RESPONSE sends from security modules, injected TX loss, RACK/TLP timer updates, and stats/tracepoint validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rxrpc/output.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rxrpc/peer_event.c -->
# sources/distributed-fs/ceph-client/net/rxrpc/peer_event.c

## Purpose
`peer_event.c` handles asynchronous peer-level events: ICMP/ICMPv6/local socket errors, PMTU reduction/probing feedback, distribution of peer errors to affected calls, and namespace-wide peer keepalive scheduling.

## Important APIs, Types, And Functions
Important functions include `rxrpc_input_error()`, `rxrpc_peer_keepalive_worker()`, and `rxrpc_input_probe_for_pmtud()`. Internal helpers include `rxrpc_lookup_peer_local_rcu()`, `rxrpc_adjust_mtu()`, `rxrpc_store_error()`, `rxrpc_distribute_error()`, `rxrpc_peer_get_tx_mark()`, and `rxrpc_peer_keepalive_dispatch()`.

## Control Flow
Socket error input reconstructs the remote `sockaddr_rxrpc` from `sock_exterr_skb`, looks up and references the peer under RCU, traces the ICMP data, applies MTU reductions for fragmentation-needed/packet-too-big, or maps the error to local/network call completion and drains `peer->error_targets`. Keepalive work collects new and expired peers from hashed time buckets, optionally uses the local endpoint, sends VERSION keepalives when the last TX time is outside the keepalive window, and requeues peers into future buckets. PMTU probing interprets ACKed probe serials or send failures, adjusts good/bad/trial data sizes and jumbo capacity, and marks pending probes.

## State And Persistence
Persistent peer state includes `if_mtu`, `max_data`, PMTU good/bad/trial/lost/probing/pending fields, `ackr_max_data`, `pmtud_jumbo`, `last_tx_at`, and the peer error target list. Namespace state includes keepalive bucket lists, cursor, base time, timer, and work item.

## Dependencies And Integration Points
This file integrates with UDP error queues, IPv4/IPv6 ICMP metadata, peer lookup from `peer_object.c`, call completion/event input, VERSION keepalive sends from `output.c`, local endpoint active use accounting, and RACK/PMTU logic in ACK handling.

## Risks And Edge Cases
Address reconstruction differs for IPv4 errors on IPv6 sockets and vice versa. MTU reports of zero force heuristic reductions. Error distribution temporarily drops the peer lock while completing calls. Keepalive scheduling relies on signed low-word timestamp reconstruction and bucket cursor arithmetic.

## Test Signals
Test ICMP frag-needed and ICMPv6 packet-too-big handling, local errors distributed to calls, mixed-family error reconstruction, PMTU binary-search progression and lost-probe retry, keepalive bucket scheduling, peer/local refcount balance, and namespace shutdown with keepalive work pending.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rxrpc/peer_event.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rxrpc/peer_object.c -->
# sources/distributed-fs/ceph-client/net/rxrpc/peer_object.c

## Purpose
`peer_object.c` manages remote transport endpoint records. Peers are deduplicated per local endpoint and remote address, hold route/PMTU/congestion metadata, provide exported kernel query helpers, and integrate with keepalive and error distribution.

## Important APIs, Types, And Functions
Important functions include `rxrpc_lookup_peer_rcu()`, `rxrpc_assess_MTU_size()`, `rxrpc_alloc_peer()`, `rxrpc_new_incoming_peer()`, `rxrpc_lookup_peer()`, `rxrpc_get_peer()`, `rxrpc_get_peer_maybe()`, `rxrpc_put_peer()`, `rxrpc_destroy_all_peers()`, `rxrpc_kernel_get_call_peer()`, `rxrpc_kernel_get_srtt()`, `rxrpc_kernel_remote_srx()`, `rxrpc_kernel_remote_addr()`, `rxrpc_kernel_set_peer_data()`, and `rxrpc_kernel_get_peer_data()`.

## Control Flow
Peer lookup hashes local pointer plus transport address, searches the namespace peer hash under RCU, and either references an existing peer or creates a candidate, assesses its route MTU, then inserts it under `peer_hash_lock` after a race recheck. Incoming peers allocated elsewhere are initialized and inserted into the same hash and keepalive-new list. Refcount drop removes the peer from hash and keepalive lists, asserts no error targets remain, releases the local endpoint, and RCU-frees the peer.

## State And Persistence
`struct rxrpc_peer` persists remote `sockaddr_rxrpc`, hash key/link, local reference, refcount, error target hlist, service connection tree/seqlock, keepalive link, MTU/PMTU data, GSO segment max, recent RTT/RTO, congestion slow-start threshold, debug ID, and application data.

## Dependencies And Integration Points
The file uses route lookup (`ip_route_output_ports`, `ip6_route_output`), namespace peer hash/keepalive lists, local endpoint refs, PMTU/keepalive/event code, connection and call ownership, and exported AF_RXRPC kernel APIs for services such as AFS.

## Risks And Edge Cases
Route lookup failures leave conservative MTU defaults. IPv6 support is conditional. Hash buckets are not sorted despite a compare function. Candidate insertion must handle races without leaking refs. Exported address pointers are borrowed; callers must keep peer lifetime stable.

## Test Signals
Cover concurrent peer lookup races, incoming and outgoing peer insertion, IPv4/IPv6 route MTU assessment, refcount underflow/leak checks, exported app-data helpers, destroy-all leak diagnostics, and PMTU defaults on route failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rxrpc/peer_object.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rxrpc/proc.c -->
# sources/distributed-fs/ceph-client/net/rxrpc/proc.c

## Purpose
`proc.c` implements `/proc/net/rxrpc` diagnostics for calls, connections, bundles, peers, local endpoints, and statistics. It provides seq_file operations and a write handler to clear counters.

## Important APIs, Types, And Functions
The file defines `rxrpc_call_seq_ops`, `rxrpc_connection_seq_ops`, `rxrpc_bundle_seq_ops`, `rxrpc_peer_seq_ops`, `rxrpc_local_seq_ops`, `rxrpc_stats_show()`, and `rxrpc_stats_clear()`. Show helpers format call state, connection state, bundle flags, peer RTT/MTU, local endpoint queue/use counts, and stat groups.

## Control Flow
Each seq start/next/stop pair acquires the appropriate lock: calls use RCU list iteration, conns and bundles use `conn_lock`, peers iterate hash buckets with encoded positions under RCU, and locals iterate the endpoint hlist under RCU. Show callbacks print a header for the start token/head and then format one object. Stats show reads atomic counters; stats clear accepts only empty/newline writes and resets the relevant atomic counters and arrays.

## State And Persistence
No protocol state is owned here. The file observes namespace lists/hash tables and atomics from `struct rxrpc_net`, plus per-object fields such as call windows, connection channels, bundle connection IDs, peer PMTU/RTT, local active users, and queue lengths.

## Dependencies And Integration Points
Proc entries are created by `net_ns.c`. The file depends on call/connection/peer/local layout, state-name tables, kernel key serial numbers, seq_file networking helpers, RCU/list/hash iteration primitives, and rxrpc stats counters incremented throughout TX/RX paths.

## Risks And Edge Cases
Diagnostics are lock-light and can show moving values. Peer hash iteration encodes bucket and index into `loff_t`; position handling must avoid infinite loops and UINT overflow. Stats clear uses `memset()` on atomic arrays, which assumes atomic_t storage representation is compatible with zeroing.

## Test Signals
Read all proc files under active traffic, exercise namespace isolation, clear stats with valid and invalid writes, check peer hash iteration across empty buckets, and run under lockdep/RCU debug while calls/connections are created and destroyed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rxrpc/proc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rxrpc/protocol.h -->
# sources/distributed-fs/ceph-client/net/rxrpc/protocol.h

## Purpose
`protocol.h` defines AF_RXRPC on-wire packet layout, fixed protocol constants, packet type/flag values, ACK payload/trailer structures, jumbo-packet sizing, and security challenge/response headers shared by TX, RX, and security modules.

## Important APIs, Types, And Functions
Important definitions include `rxrpc_seq_t`, `rxrpc_serial_t`, `struct rxrpc_wire_header`, connection/channel masks and shifts, packet type constants, packet flags, `struct rxrpc_jumbo_header`, `RXRPC_JUMBO_DATALEN`, `RXRPC_MAX_NR_JUMBO`, `RXRPC_JUMBO()`, `struct rxrpc_ackpacket`, ACK reason/type constants, `struct rxrpc_acktrailer`, `struct rxkad_challenge`, `struct rxkad_response`, `struct rxgk_header`, and `struct rxgk_response`.

## Control Flow
The header has no runtime control flow. It establishes the byte-exact network-order contract used by packet construction, parsing, verification, ACK/SACK generation, jumbo subpacket expansion, PMTU calculations, and security handshakes.

## State And Persistence
The structures describe transient wire state, not persistent in-memory ownership. Multi-byte fields are explicitly network byte order and packed. Constants such as `RXRPC_MAXCALLS` determine persistent connection channel array sizing elsewhere.

## Dependencies And Integration Points
`output.c`, `recvmsg.c`, input paths, RxKAD, RxGK, peer PMTU code, proc output, and tracepoints all depend on these definitions. User-status and security-index fields connect protocol framing with AuriStor service upgrade and security module dispatch.

## Risks And Edge Cases
Any layout or constant change is wire-protocol compatibility-sensitive. The flag bit `0x20` is overloaded as DATA jumbo and ACK slow-start support by packet type. Jumbo sizing assumes UDP/IP maximums and exact subpacket header accounting. The comment typo in RESPONSE does not affect ABI but signals this is legacy protocol surface.

## Test Signals
Build-time structure size/packing checks, interoperability with OpenAFS/YFS peers, jumbo boundary tests up to `RXRPC_MAX_NR_JUMBO`, ACK reason parsing, endian tests, and security challenge/response packet decode coverage are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rxrpc/protocol.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rxrpc/recvmsg.c -->
# sources/distributed-fs/ceph-client/net/rxrpc/recvmsg.c

## Purpose
`recvmsg.c` implements AF_RXRPC userspace and kernel receive APIs. It notifies sockets about ready calls, prioritizes out-of-band security messages, copies verified DATA payloads to callers, advances receive windows, reports terminal call status, and exposes `rxrpc_kernel_recv_data()`.

## Important APIs, Types, And Functions
Important functions include `rxrpc_notify_socket()`, `rxrpc_recvmsg()`, and `rxrpc_kernel_recv_data()`. Internal helpers include `rxrpc_recvmsg_term()`, `rxrpc_rotate_rx_window()`, `rxrpc_verify_data()`, `rxrpc_recvmsg_user_id()`, `rxrpc_recvmsg_challenge()`, `rxrpc_recvmsg_oob()`, and `rxrpc_recvmsg_data()`.

## Control Flow
Call notification queues a referenced call on `rx->recvmsg_q` or invokes kernel callbacks. `rxrpc_recvmsg()` blocks or returns immediately according to socket timeout, handles OOB messages first, dequeues or peeks a call, serializes user access with `call->user_mutex`, emits user-call-ID and peer address control data, copies DATA through `rxrpc_recvmsg_data()`, and finally emits terminal ACK/ABORT/ERROR control messages when the call completes. Data receive verifies each SKB through the connection security module once, copies partial packet data, rotates fully consumed packets out of the receive window, sets idle ACK triggers, and stops on OOB priority or buffer fullness. Kernel receive follows the same data path but enforces expected length and want-more semantics.

## State And Persistence
State lives in socket `recvmsg_q`, `recvmsg_oobq`, locks, call `recvmsg_queue`, `rx_pkt_offset`, `rx_pkt_len`, `rx_consumed`, `ackr_nr_consumed`, `ackr_window`, flags such as `RECVMSG_READ_ALL`, and completion/error fields. Consuming SKBs updates ACK state and may poke the call for IDLE ACK generation.

## Dependencies And Integration Points
The file integrates with security `verify_packet()`, OOB challenge handling, socket callbacks/wait queues, call release/completion, SKB timestamp/control-message APIs, kernel service APIs, and ACK scheduling.

## Risks And Edge Cases
Concurrent recvmsg callers are serialized by call mutex but socket queues still need careful requeue logic. `MSG_PEEK` must not advance offsets or consume SKBs. OOB messages interrupt normal data delivery. Short/excess kernel-service reads abort at higher layers through returned errors. The function assumes `call->socket` exists when notifying; released calls are skipped.

## Test Signals
Test blocking/nonblocking receive, `MSG_PEEK`, partial reads across packet boundaries, terminal control messages, OOB challenge priority, concurrent recvmsg requeue behavior, security verification failures, kernel receive short/excess data, idle ACK triggering, and call release races.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rxrpc/recvmsg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rxrpc/rtt.c -->
# sources/distributed-fs/ceph-client/net/rxrpc/rtt.c

## Purpose
`rtt.c` calculates smoothed RTT, RTT variance, RTO, RACK minimum RTT, and retransmission backoff for AF_RXRPC calls, adapting TCP-style RFC6298/Jacobson logic.

## Important APIs, Types, And Functions
Externally used functions are `rxrpc_call_add_rtt()`, `rxrpc_get_rto_backoff()`, and `rxrpc_call_init_rtt()`. Internal helpers include `rxrpc_rto_min_us()`, `__rxrpc_set_rto()`, `rxrpc_bound_rto()`, `rxrpc_rtt_estimator()`, `rxrpc_set_rto()`, `rxrpc_update_rtt_min()`, and `rxrpc_ack_update_rtt()`.

## Control Flow
Call initialization sets initial RTO and deviation. When an ACK response matches an RTT probe, `rxrpc_call_add_rtt()` computes elapsed microseconds, ignores negative samples, updates the RACK min RTT, feeds the sample to the estimator, recalculates bounded RTO, resets backoff, increments sample counters, publishes recent peer SRTT/RTO, and traces the sample. Timeout selection reads current RTO, shifts by backoff, optionally increments backoff for retransmissions, clamps to at least 1 microsecond, and returns a ktime.

## State And Persistence
Per-call persistent fields include `srtt_us` scaled by 8, `mdev_us`, `mdev_max_us`, `rttvar_us`, `rto_us`, `backoff`, `rtt_count`, `rtt_taken`, and `min_rtt`. Peer fields `recent_srtt_us` and `recent_rto_us` cache current diagnostics.

## Dependencies And Integration Points
The file is used by ACK/RTT probe handling in `output.c` and ACK receive paths, RACK/TLP timeout logic, peer proc diagnostics, and tracepoints. It depends on kernel minmax helpers, jiffies/ktime conversion, and rxrpc call/peer structures.

## Risks And Edge Cases
The current minimum RTO helper returns 200 microseconds but `rxrpc_bound_rto()` clamps with a hardcoded 200000 microsecond lower term plus 100000 slack, so changes must be made carefully. Negative time samples are ignored. Backoff uses left shifts and caps increment only when doubling stays under the max.

## Test Signals
Unit-style tests should feed first and subsequent RTT samples, decreasing RTT variance, negative samples, retransmission backoff growth, max RTO clamp, peer diagnostic updates, and RACK min RTT window behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rxrpc/rtt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rxrpc/rxgk.c -->
# sources/distributed-fs/ceph-client/net/rxrpc/rxgk.c

## Purpose
`rxgk.c` implements YFS RxGK, a GSSAPI/Kerberos-based AF_RXRPC security class. It handles server-key parsing, connection security initialization, rekeying, packet signing/encryption/verification, challenge/response generation, userspace/kernel challenge responses, response verification, and cleanup.

## Important APIs, Types, And Functions
The file exports `rxgk_yfs`, `rxgk_kernel_query_challenge()`, and `rxgk_kernel_respond_to_challenge()`. Major internals include `rxgk_preparse_server_key()`, `rxgk_rekey()`, `rxgk_get_key()`, `rxgk_init_connection_security()`, `rxgk_alloc_txbuf()`, `rxgk_secure_packet()`, `rxgk_verify_packet()`, `rxgk_issue_challenge()`, `rxgk_validate_challenge()`, `rxgk_challenge_to_recvmsg()`, `rxgk_construct_response()`, `rxgk_sendmsg_respond_to_challenge()`, `rxgk_verify_authenticator()`, `rxgk_verify_response()`, and `rxgk_clear()`.

## Control Flow
Connection initialization derives the first transport key from the client token or server response. TX allocation reserves crypto/header space according to security level. Securing a packet obtains the current key, validates the rxrpc key, writes the low key number into the wire checksum field, and either leaves data plain, attaches a MIC, or encrypts an RxGK header plus payload. Verification obtains the key indicated by the packet key number, possibly rekeying, then verifies MICs or decrypts and validates sealed headers. Server challenge sends a random nonce; client response builds token, ticket, and encrypted authenticator with optional appdata. Server response verification decrypts the token, instantiates a session key, derives transport keys, decrypts the authenticator, validates nonce/level/epoch/cid/call counters, and installs `conn->key`.

## State And Persistence
RxGK persistent state lives in `conn->rxgk`: key ring slots, current key number, enctype, nonce, and start time. Each `struct rxgk_context` holds usage refs, key number, expiry, byte lifetime, Kerberos enctype, source key, AEAD/shash transforms, and rekey flags. Connection security locks protect slow rekey generation and fast key use.

## Dependencies And Integration Points
The file depends on crypto Kerberos helpers, `rxgk_common.h` KDF/decrypt helpers, app-specific ticket decoding in `rxgk_app.c`, response transmission in `output.c`, OOB/recvmsg challenge delivery, keyring server-key lookup, and the generic security dispatcher.

## Risks And Edge Cases
Only 16 key-number bits are exposed on wire, so rekey logic accepts current, previous, or next low-word values. Rekey rollover can mark connections non-reusable. Authenticator parsing must reject short, misaligned, stale, or inconsistent call counters. Temporary errors during token processing deliberately cause response retry rather than immediate abort.

## Test Signals
Cover all supported Kerberos enctypes, plain/auth/encrypt packet paths, key expiry and byte-life rekey, previous/current/next key-number receive, challenge OOB userspace appdata, kernel challenge response, malformed token/authenticator aborts, call-counter synchronization, and cleanup refcounting of `rxgk_context` ciphers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rxrpc/rxgk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rxrpc/rxgk_app.c -->
# sources/distributed-fs/ceph-client/net/rxrpc/rxgk_app.c

## Purpose
`rxgk_app.c` contains application-specific RxGK token handling for YFS. It decrypts token containers, looks up server secrets, decodes default YFS tickets, and instantiates rxrpc keys that expose session key material to the generic RxGK transport-key logic.

## Important APIs, Types, And Functions
The file implements `rxgk_yfs_decode_ticket()` and `rxgk_extract_token()`. It uses `struct rxgk_key`, `RXGK_TokenContainer`, XDR length helpers, `rxrpc_look_up_server_security()`, `rxgk_set_up_token_cipher()`, `rxgk_decrypt_skb()`, `key_alloc()`, and `key_instantiate_and_link()`.

## Control Flow
`rxgk_extract_token()` parses kvno, enctype, and encrypted-token length from the response, looks up the matching service key, sets up the Kerberos AEAD for server token decryption, decrypts the token region in place, and delegates ticket parsing to the security module's default decoder. The YFS decoder validates minimum ticket shape, reads enctype and session-key length, copies the ticket into an XDR-formatted rxrpc key payload, maps ticket fields into token metadata, copies session key and original ticket, instantiates an anonymous rxrpc key, marks it `no_leak_key`, and returns it.

## State And Persistence
The decoder allocates temporary sensitive payload buffers and returns a live `struct key` containing `struct rxrpc_key_token` data. It does not persist state in the connection directly; callers install the returned key after authenticator verification.

## Dependencies And Integration Points
This file bridges RxGK response verification, rxrpc key type parsing, server keyrings, Kerberos crypto, and YFS ticket format. It is called from `rxgk_verify_response()` through `rxgk_extract_token()`.

## Risks And Edge Cases
Length and XDR rounding checks are security-critical. The code currently uses `current_cred()` and TODO comments for socket credentials/ownership. Unsupported or missing server keys map to protocol aborts. Sensitive buffers are freed with `kfree_sensitive()`.

## Test Signals
Test short token/ticket lengths, bad key lengths, unsupported enctypes, missing/expired server keys, successful YFS ticket decode, instantiated key payload fields, sensitive free paths, and credential/key permission behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rxrpc/rxgk_app.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rxrpc/rxgk_common.h -->
# sources/distributed-fs/ceph-client/net/rxrpc/rxgk_common.h

## Purpose
`rxgk_common.h` defines shared RxGK context state, XDR helpers, prototypes for app/KDF modules, and inline SKB crypto helpers used by RxGK packet and token processing.

## Important APIs, Types, And Functions
Important definitions include `struct rxgk_context`, `RXGK_TK_NEEDS_REKEY`, `xdr_round_up()`, `xdr_round_down()`, `xdr_object_len()`, prototypes for `rxgk_yfs_decode_ticket()`, `rxgk_extract_token()`, `rxgk_put()`, `rxgk_generate_transport_key()`, `rxgk_set_up_token_cipher()`, and inline helpers `rxgk_decrypt_skb()` and `rxgk_verify_mic_skb()`.

## Control Flow
The inline helpers convert SKB ranges to scatterlists, call Kerberos decrypt/MIC verification helpers, update caller-provided offset/length on success, and translate crypto errors into RxGK abort codes such as `RXGK_SEALEDINCON`, `RXGK_PACKETSHORT`, and `RXGK_INCONSISTENCY`.

## State And Persistence
`struct rxgk_context` is the persistent per-key-number transport context. It stores refcount, key number, expiry, byte lifetime, Kerberos enctype/key pointer, TX/RX AEADs, TX/RX checksum transforms, and response encryption transform.

## Dependencies And Integration Points
The header depends on kernel Kerberos crypto APIs and is shared by `rxgk.c`, `rxgk_app.c`, and `rxgk_kdf.c`. Its error-code mapping directly affects connection abort behavior from packet verification and token decryption.

## Risks And Edge Cases
Scatterlist arrays are fixed at 16 entries; unusually fragmented SKBs beyond that rely on `skb_to_sgvec()` failure handling. Offset/length mutation must happen only after successful crypto. Context lifetime requires every `rxgk_get_key()` reference to be paired with `rxgk_put()`.

## Test Signals
Compile coverage across RxGK files, fragmented SKB decrypt/MIC cases, checksum mismatch abort-code mapping, packet-short mapping, context refcount KASAN/KCSAN checks, and XDR rounding boundary tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rxrpc/rxgk_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rxrpc/rxgk_kdf.c -->
# sources/distributed-fs/ceph-client/net/rxrpc/rxgk_kdf.c

## Purpose
`rxgk_kdf.c` derives RxGK transport keys and per-usage crypto transforms from Kerberos session keys. It also owns `struct rxgk_context` destruction and token-decryption cipher setup.

## Important APIs, Types, And Functions
Important functions include `rxgk_put()`, `rxgk_generate_transport_key()`, and `rxgk_set_up_token_cipher()`. Internal helpers include `rxgk_free()`, `rxgk_derive_transport_key()`, and `rxgk_set_up_ciphers()`. Usage constants select client/server packet encryption, MIC, response encryption, and server token encryption keys.

## Control Flow
Transport-key generation allocates a context, finds the Kerberos enctype, derives TK with PRF+ over epoch, cid, start time, and key number, derives response encryption plus direction-specific TX/RX MIC or encryption transforms according to service/client role and security level, computes byte lifetime and jiffies expiry, and returns a referenced context. Token cipher setup prepares the server-token AEAD from a service secret and enctype.

## State And Persistence
`struct rxgk_context` owns AEAD and shash transform pointers until its refcount reaches zero. It records remaining byte lifetime and expiry time for rekey decisions. Temporary key material buffers are zeroed/freed through sensitive free paths where appropriate.

## Dependencies And Integration Points
The file depends on Kerberos crypto helpers, rxrpc connection role/security-level fields, key tokens from rxrpc key type, and the rekey/packet paths in `rxgk.c`.

## Risks And Edge Cases
Direction-specific usage constants must be paired correctly for clients versus services or packets become unverifiable. Crypto transform block/auth sizes are checked against Kerberos tables. Byte-life semantics accept both exponent-like values and literal counts. Lifetime conversion must avoid jiffies overflow.

## Test Signals
Test every supported enctype and security level, client/server direction interop, transform allocation failures, byte-life and expiry-triggered rekey, token cipher setup with unsupported enctype, and refcounted cleanup of partially initialized contexts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rxrpc/rxgk_kdf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rxrpc/rxkad.c -->
# sources/distributed-fs/ceph-client/net/rxrpc/rxkad.c

## Purpose
`rxkad.c` implements the legacy Kerberos/DES-based RxKAD AF_RXRPC security class. It parses server keys, initializes connection ciphers, signs or encrypts packets, verifies received packets, performs challenge/response authentication, decrypts Kerberos tickets, and creates server-side data keys.

## Important APIs, Types, And Functions
The file exports `rxkad` and `rxkad_kernel_respond_to_challenge()`. Major functions include `rxkad_preparse_server_key()`, `rxkad_init_connection_security()`, `rxkad_alloc_txbuf()`, `rxkad_prime_packet_security()`, `rxkad_secure_packet()`, `rxkad_verify_packet()`, `rxkad_issue_challenge()`, `rxkad_validate_challenge()`, `rxkad_respond_to_challenge()`, `rxkad_decrypt_ticket()`, `rxkad_decrypt_response()`, `rxkad_verify_response()`, `rxkad_clear()`, `rxkad_init()`, and `rxkad_exit()`.

## Control Flow
Client connection initialization allocates `pcbc(fcrypt)`, loads the session key, validates security level, and primes checksum IVs from epoch/cid/security index. TX buffers reserve 8-byte-aligned security headers for AUTH or ENCRYPT. Securing a packet computes the wire checksum from call/channel/sequence, then either encrypts only the level-1 header or encrypts the entire level-2 secure payload. Verification recomputes the checksum, decrypts the appropriate secure region in place, checks sequence/call-derived header checks, and trims payload length. Server challenge sends a nonce. Response generation builds an encrypted response plus ticket; verification looks up the service key, decrypts the ticket to obtain a session key/expiry, decrypts response fields, validates checksum, nonce, level, epoch/cid/security index, and call counters, then stores a server data key.

## State And Persistence
Connection state includes `conn->rxkad.cipher`, checksum IV, nonce, and security level. Global module state pins `rxkad_ci` and `rxkad_ci_req` for response decryption under `rxkad_ci_mutex`. Server keys store DES cipher payload and raw secret; response verification may instantiate connection-specific data keys.

## Dependencies And Integration Points
The file depends on Linux crypto skcipher APIs, rxrpc key types, generic security dispatch, packet output, OOB/kernel challenge response APIs, abort codes, and the rxrpc call/connection/channel model.

## Risks And Edge Cases
DES/FCrypt and PCBC are legacy and configuration-sensitive. Packet lengths must be 8-byte aligned before crypto. Ticket parsing enforces printable principal fields, lifetime, issue time, and maximum ticket length. Global response-decrypt cipher serialization is protected by a mutex. RxKAD does not support userspace `sendmsg()` challenge responses.

## Test Signals
Cover plain/auth/encrypt send and receive, checksum mismatch aborts, malformed secure headers, challenge version/min-level checks, expired/future tickets, unknown kvno, call-counter synchronization, cipher allocation failures, module init/exit cleanup, and interoperability with AFS RxKAD peers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rxrpc/rxkad.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rxrpc/rxperf.c -->
# sources/distributed-fs/ceph-client/net/rxrpc/rxperf.c

## Purpose
`rxperf.c` implements an in-kernel AF_RXRPC performance test server. It listens on service 147/port 7009, accepts encrypted calls, unmarshals rxperf request parameters, discards or replies with configured byte counts, and supplies test security keys.

## Important APIs, Types, And Functions
Important functions include `rxperf_init()`, `rxperf_exit()`, `rxperf_open_socket()`, `rxperf_close_socket()`, `rxperf_charge_preallocation()`, `rxperf_deliver_to_call()`, `rxperf_extract_data()`, `rxperf_deliver_param_block()`, `rxperf_deliver_request()`, `rxperf_process_call()`, `rxperf_add_rxkad_key()`, and optional `rxperf_add_yfs_rxgk_key()`. It defines `struct rxperf_call`, protocol constants, and rxrpc kernel callbacks.

## Control Flow
Late init creates a workqueue, allocates a server keyring, adds an RxKAD key and optional RxGK enctype keys, opens an AF_RXRPC IPv6 datagram socket, sets minimum security to encrypt, attaches the keyring and notification ops, binds/listens, and precharges accepts. New call notifications replenish preallocation. Per-call work receives a fixed parameter block, validates version and operation, reads size parameters and request data/magic cookie, sets reply length, sends zero-page reply chunks plus terminal magic cookie, waits for final ACK/life check, then shuts down and releases the call. Errors are mapped to rxgen aborts.

## State And Persistence
Global state includes `rxperf_socket`, `rxperf_sec_keyring`, and `rxperf_workqueue`. Each `rxperf_call` tracks rxrpc call pointer, iterator/kvecs, operation, request/reply lengths, state, abort/error fields, service ID, and work item.

## Dependencies And Integration Points
The server uses AF_RXRPC kernel APIs for accept precharge, notifications, receive, send, TX length, abort, shutdown, and put-call. It depends on kernel keyrings, RxKAD/RxGK security modules, Kerberos enctype lookup, workqueues, zero pages, and trace enum definitions.

## Risks And Edge Cases
The module is test-oriented but binds a real service port in `init_net`. Preallocation must free unattached call records on discard/failure. Large requested replies stream zero pages but still exercise socket/call flow control. Shutdown must stop listening before releasing socket and flush the workqueue to avoid call use-after-free.

## Test Signals
Run rxperf send/recv/rpc operations with RxKAD and each configured RxGK enctype, version/opcode mismatch aborts, large request/reply sizes, client aborts, final ACK wait behavior, module unload during active calls, keyring setup failures, and workqueue/preallocation leak checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rxrpc/rxperf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rxrpc/security.c -->
# sources/distributed-fs/ceph-client/net/rxrpc/security.c

## Purpose
`security.c` is the generic AF_RXRPC security dispatcher. It registers available security classes, selects a security module for client calls/connections and incoming service connections, and looks up server security keys.

## Important APIs, Types, And Functions
Important functions include `rxrpc_init_security()`, `rxrpc_exit_security()`, `rxrpc_security_lookup()`, `rxrpc_init_client_call_security()`, `rxrpc_init_client_conn_security()`, `rxrpc_get_incoming_security()`, and `rxrpc_look_up_server_security()`. The central table is `rxrpc_security_types[]`, populated with no-security, optional RxKAD, and optional YFS RxGK.

## Control Flow
Security init iterates the table and calls each module's `init()`, unwinding prior modules on failure. Client call setup validates the key, scans key tokens, chooses the first supported security module, and records the security index. Client connection setup finds the matching token and, while holding `security_lock`, initializes connection security only if the connection is still unsecured, then transitions it to client-secured state. Incoming service security validates the packet security index and service keyring availability, aborting unsupported or unkeyed secure traffic. Server-key lookup builds a key description from service/security/kvno/enctype, searches the service socket keyring under `services_lock`, validates the key, and returns it referenced.

## State And Persistence
The dispatcher owns no per-call crypto state; it writes selected `call->security`, `call->security_ix`, `conn->security_ix`, connection security state, and returns referenced `struct key` objects. The security table persists for module lifetime.

## Dependencies And Integration Points
It depends on compiled security modules, rxrpc key/keyring types, socket service registration, connection state locks, direct connection abort helpers, and packet header security index fields.

## Risks And Edge Cases
Client keys can contain multiple tokens; unsupported tokens are skipped until a supported one is found. Incoming secure service traffic without a keyring is aborted with module-specific `no_key_abort`. Key description formatting must match server-key preparse conventions for RxKAD and RxGK. Connection state transition is protected against duplicate initialization.

## Test Signals
Cover builds with no RxKAD/RxGK, security table init unwind failures, multi-token client keys, expired/revoked keys, unsupported incoming security indices, missing service keyring aborts, server key lookup by kvno/enctype, and concurrent client connection security initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rxrpc/security.c -->
