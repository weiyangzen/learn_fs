# subset-b-006264 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rxrpc/ar-internal.h -->
# sources/distributed-fs/ceph-client/net/rxrpc/ar-internal.h

## Purpose
`ar-internal.h` is the private contract for the AF_RXRPC implementation. It defines the socket, local endpoint, peer, connection, call, transmit-buffer, transmit-queue, ACK-summary, state, flag, event, and security-operation structures shared by the rxrpc source files. It also declares the cross-file APIs used by receive dispatch, call lifecycle, connection management, output, peer/local handling, security, key management, recvmsg/sendmsg, statistics, and tracing.

## Important APIs, types, and functions
- `struct rxrpc_net` stores per-network-namespace state: active calls, connection and bundle proc lists, service connection reaper state, peers, keepalive state, and rx/tx statistics.
- `struct rxrpc_sock` extends `struct sock` and owns service backlog preallocation, receive queues, socket call indexes, security keys, service IDs, and application callbacks.
- `struct rxrpc_local` represents a UDP endpoint and owns the I/O kthread queues: `rx_queue`, `conn_attend_q`, `call_attend_q`, `new_client_calls`, client bundle tree, and idle client connection list.
- `struct rxrpc_peer` is the remote transport endpoint, with service-connection tree, error target list, PMTU state, RTT cache, and congestion threshold.
- `struct rxrpc_connection` models a virtual RxRPC connection, including four channels, security state, connection-level rx queue, timers/work items, retransmittable terminal packet state, and service/client identity.
- `struct rxrpc_call` models one RPC call and carries call state, socket ownership, timers, tx/rx queues, congestion state, RACK/TLP state, ACK-generation state, RTT samples, completion, abort metadata, and user-visible identifiers.
- `struct rxrpc_security` is the pluggable security interface for no-security, rxkad, and rxgk implementations.
- Inline helpers such as `rxrpc_set_call_state()`, `rxrpc_call_state()`, `rxrpc_is_conn_aborted()`, `rxrpc_queue_rx_call_packet()`, `rxrpc_tx_window_space()`, and sequence comparison helpers encode ordering, queueing, and wraparound assumptions used throughout the implementation.

## Control flow and integration
The header ties the main runtime loop together: UDP input enters through `rxrpc_encap_rcv()`, the local I/O thread calls into packet input, call packets are queued to `call->rx_queue`, and call/connection pokes place objects on local attend queues. Client calls are created in socket/sendmsg code, queued through `local->new_client_calls`, assigned to bundle channels by `conn_client.c`, then driven by `call_event.c` and `input.c`. Service calls are preallocated through `call_accept.c`, attached to service connections, and published through peer service trees. Output functions declared here send ACK, DATA, ABORT, RESPONSE, reject, and PMTU-probe packets.

## State and persistence behavior
The persistent in-memory state is mostly refcounted and RCU protected. Calls and connections are listed in namespace-global structures for proc/debug and teardown checks. Socket-visible call completion is ordered with release/acquire barriers around `_state`, `completion`, `abort_code`, and `error`. Connection abort state uses release/acquire ordering around `conn->state`. Call and connection timers are reduced to the earliest pending deadline, and final destruction may be deferred to workqueue or RCU when invoked from softirq or while processing is active.

## Dependencies
This header depends on Linux networking (`sock`, `sk_buff`, UDP transport), keyrings, RCU, IDR/rbtree/list primitives, timers, workqueues, seqlocks, atomics/refcounts, minmax RTT helpers, and `protocol.h` wire-format definitions. It is the dependency hub for every rxrpc implementation file in this subset.

## Risks and invariants
Important invariants include backlog ordering `calls >= conns >= peers`, four channels per connection, no serial number zero, call completion before final put, socket release before call free, connection final ACK bits matching channel cached terminal state, and seq-number comparisons using wrap-safe helpers. Bugs here affect the whole subsystem, especially memory ordering, refcount ownership, timer cancellation, and queue ownership.

## Test signals
Useful signals are KUnit/static assertions around inline helpers, lockdep and KCSAN coverage for state transitions, packet-driven integration tests for call phase transitions, namespace teardown leak checks for `nr_calls` and `nr_conns`, and tracepoint validation for call/connection refcount and timer flows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rxrpc/ar-internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rxrpc/call_accept.c -->
# sources/distributed-fs/ceph-client/net/rxrpc/call_accept.c

## Purpose
`call_accept.c` handles service-side call acceptance. It prepares backlog objects for services, turns the first incoming DATA packet into a live service call, attaches the call to a service connection, and charges user or kernel accept slots with application-supplied call IDs.

## Important APIs and functions
- `rxrpc_service_prealloc()` allocates the `rxrpc_backlog` container for a service socket.
- `rxrpc_service_prealloc_one()` fills circular preallocation pools for peers, service connections, and calls, registers the call under `rx->calls`, attaches user IDs and optional kernel callbacks, and queues it in the call backlog.
- `rxrpc_discard_prealloc()` drains unused peer, connection, and call preallocations during service shutdown.
- `rxrpc_alloc_incoming_call()` consumes preallocated objects, optionally creates a new peer and service connection, or references an existing connection, then initializes call fields from the connection.
- `rxrpc_new_incoming_call()` is called from packet input to validate service/security state, allocate/initialize the call, notify the application, start connection challenge if needed, and queue the first packet to the call.
- `rxrpc_user_charge_accept()` and exported `rxrpc_kernel_charge_accept()` are the userspace/kernel charging entry points.

## Control flow
Services first create `rx->backlog`; user or kernel code charges individual accept entries with a user call ID. On the first DATA packet for a missing service call, `io_thread.c` calls `rxrpc_new_incoming_call()`. That function checks the local service binding, service ID, security class, listen/shutdown state, and backlog availability. It then consumes a preallocated call plus a connection/peer if needed, calls `rxrpc_incoming_call()`, optionally notifies application code, queues a connection challenge for secured service connections, assesses MTU, links error delivery, queues the packet to the call, and drops its input reference.

## State and persistence behavior
The service backlog is a set of ring buffers with release/acquire head and tail updates because producers charge accept entries and the I/O thread consumes them. Calls are inserted into the socket rbtree and socket call list before entering the backlog. Incoming calls transition from `RXRPC_CALL_SERVER_PREALLOC` to live server receive state in `rxrpc_incoming_call()`. Service connections either come from preallocation and get published to the peer service tree, or are refcounted if already present.

## Dependencies and integration points
This file integrates with peer allocation, service connection publishing, security lookup, call object creation/release, socket notification callbacks, direct reject/abort packet marking, MTU assessment, and the I/O thread's packet dispatch. Kernel services can receive callbacks through `rxrpc_kernel_ops`.

## Risks
The main risks are backlog exhaustion returning BUSY, duplicate user call IDs, consuming backlog entries out of order, service shutdown racing incoming packets, and missing security rejection paths. The invariant that preallocated calls, connections, and peers remain ordered by capacity is asserted in the allocator.

## Test signals
Exercise accept charging limits, duplicate user IDs, missing services, unsupported security, listen-disabled shutdown, peer reuse vs new peer allocation, secured service challenge initiation, and backlog discard on socket close.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rxrpc/call_accept.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rxrpc/call_event.c -->
# sources/distributed-fs/ceph-client/net/rxrpc/call_event.c

## Purpose
`call_event.c` is the per-call event engine. It processes queued call packets, call timers, delayed ACKs, pings, keepalives, retransmissions, initial service pings, transmission of fresh data, RACK/TLP timer expiry, and completion-time disconnection/crypto cleanup.

## Important APIs and functions
- `rxrpc_propose_ping()` and `rxrpc_propose_delay_ACK()` schedule future ACK generation.
- `rxrpc_transmit_some_data()` sends fresh DATA if the call state and transmit window allow it.
- `rxrpc_resend_tlp()` retransmits the highest transmitted DATA packet for tail-loss probing.
- `rxrpc_input_call_event()` is the central call-attend handler invoked by the I/O thread.
- Internal helpers handle retransmission of lost txqueue segments, service reply phase start, tx phase closure, and initial parameter pings.

## Control flow
The I/O thread places a call on `local->call_attend_q` through `rxrpc_poke_call()`. `rxrpc_input_call_event()` drains `call->rx_queue`, unshares encrypted DATA skbs if in-place verification may modify them, and passes packets to `rxrpc_input_call_packet()`. It then checks RACK timeout, receive/request/hard lifetime timers, delayed ACK, ping, keepalive, initial-ping event, fresh transmit opportunity, lost-ACK event, lost DATA retransmission, idle ACK requests, and ACK pressure. Finally it restarts the call timer to the earliest pending deadline or completes teardown if the call is complete.

## State and persistence behavior
This file mutates call timer fields (`delay_ack_at`, `ping_at`, `keepalive_at`, `expect_*`, `rack_timo_at`), event bits, tx queue progress, congestion loss counters, and call state. On completion it deletes the timer, disconnects from the connection if still connected, and frees per-call crypto. It intentionally centralizes these changes in the I/O thread path to simplify locking.

## Dependencies and integration points
It depends on `input.c` for packet semantics, `output.c` for ACK/DATA transmission, `input_rack.c` for RACK/TLP, `conn_object.c` for disconnection, `security` hooks for call crypto cleanup, RTT/RTO helpers, tracepoints, and socket notification via call completion.

## Risks
Timer restart logic must include every pending deadline or calls can hang. Retransmission scans must not access freed txqueue entries. Encrypted skb unsharing failures drop packets and rely on retransmission. Completion teardown must not race with call release and refcount ownership.

## Test signals
Use tests or packet traces for delayed ACK expiry, ping keepalive, hard timeout, idle timeout, retransmit on loss, RACK timer expiry, service reply transition, tx underflow, encrypted skb clone handling, and complete-call disconnection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rxrpc/call_event.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rxrpc/call_object.c -->
# sources/distributed-fs/ceph-client/net/rxrpc/call_object.c

## Purpose
`call_object.c` owns call allocation, publication, lookup, connection setup for client calls, incoming call activation, reference management, socket detachment, buffer cleanup, final destruction, and the kernel query API for call security.

## Important APIs and functions
- `rxrpc_alloc_call()` initializes a call object, queues, timers, refcount, default windows, congestion state, RTT state, and namespace counters.
- `rxrpc_new_client_call()` creates and publishes a client call under a user call ID, then queues it for connection assignment.
- `rxrpc_incoming_call()` activates a preallocated service call on a connection/channel.
- `rxrpc_poke_call()` queues a call for I/O thread attention.
- `rxrpc_release_call()` and `rxrpc_release_calls_on_socket()` detach calls from a socket.
- `rxrpc_put_call()`, `rxrpc_cleanup_call()`, and `rxrpc_destroy_call()` implement final lifetime cleanup.
- `rxrpc_kernel_query_call_security()` exposes service/security info to kernel users.

## Control flow
Client creation obtains a global user or kernel call slot, allocates security, publishes the call in the socket rbtree/list and namespace call list, releases the socket lock, then queues the call on `local->new_client_calls` for the I/O thread to bind to a connection. Incoming service calls are supplied by `call_accept.c` and get call ID, cid, service, state, channel pointer, error target link, and timer initialized here.

## State and persistence behavior
Calls have a strict lifecycle: allocated with refcount 1, published in socket and namespace lists, optionally assigned a connection/channel, completed through `call_state.c`, released from socket ownership, then final-put removes from namespace list and destroys buffers, connection, bundle, peer, local, and key references. The call limiter semaphores cap user and kernel call creation separately.

## Dependencies and integration points
This file connects socket send/recv APIs, client bundle lookup, service accept, connection disconnection, workqueue/RCU destruction, key/security initialization, and proc/debug lists. It relies on `rxrpc_set_call_completion()` for successful or failed terminal states.

## Risks
Duplicate user call IDs must be detected under `rx->call_lock`. Error after socket publication intentionally leaves completion for recvmsg rather than returning sendmsg failure. Release requires `RXRPC_CALL_RELEASED` exactly once; final put asserts completion. Destruction must be safe under RCU and while timers/work may still be active.

## Test signals
Cover duplicate user IDs, client connection allocation failure after socket publication, service incoming activation, socket close with accepted and to-be-accepted calls, final refcount cleanup, limiter release, and namespace teardown leak detection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rxrpc/call_object.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rxrpc/call_state.c -->
# sources/distributed-fs/ceph-client/net/rxrpc/call_state.c

## Purpose
`call_state.c` centralizes terminal call-state changes. It records completion, abort, and local pre-start failure outcomes and provides the single point that wakes waiters and notifies the socket when a call becomes complete.

## Important APIs and functions
- `rxrpc_set_call_completion()` stores completion class, abort code, and errno, transitions the state to `RXRPC_CALL_COMPLETE`, traces, wakes `call->waitq`, and notifies the socket.
- `rxrpc_call_completed()` records normal success.
- `rxrpc_abort_call()` records a local abort and transmits an ABORT packet if the call has been exposed.
- `rxrpc_prefail_call()` marks calls complete and released before they are fully started, used for allocation/attachment failures.

## Control flow
Most files call into this module rather than writing completion fields directly. Input uses it for remote aborts and protocol failures, call event uses it for timeout/reset, connection event uses it when a connection abort propagates to calls, and object/accept code uses prefail for setup errors.

## State and persistence behavior
Completion data is written before the state transition. `rxrpc_set_call_state()` in the header uses release semantics, and readers use acquire semantics through `rxrpc_call_state()`. This permits lockless readers to see consistent `completion`, `abort_code`, and `error` after observing `RXRPC_CALL_COMPLETE`.

## Dependencies and integration points
It depends on output ABORT transmission, socket notification, tracepoints, and wait queues. It intentionally does not release object references; lifecycle cleanup remains in `call_object.c` and `call_event.c`.

## Risks
Double completion must be harmless; `rxrpc_set_call_completion()` returns false if the call is already complete. `rxrpc_prefail_call()` sets `RXRPC_CALL_RELEASED`, so callers must not later release the same call as a normal live socket call.

## Test signals
Check double-completion behavior, abort packet emission only for exposed calls, waiter wakeups, recvmsg notification, memory-ordering assumptions under KCSAN, and setup failure cleanup paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rxrpc/call_state.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rxrpc/conn_client.c -->
# sources/distributed-fs/ceph-client/net/rxrpc/conn_client.c

## Purpose
`conn_client.c` implements client-side connection caching and channel assignment. It groups compatible client calls into bundles, allocates client connections and connection IDs, multiplexes calls onto four channels per connection, handles service upgrade probing, idles/reaps reusable connections, and cleans up local client connection state.

## Important APIs and functions
- `rxrpc_look_up_bundle()` finds or creates a bundle keyed by peer, key, security level, and upgrade flag.
- `rxrpc_connect_client_calls()` moves new calls into bundle waiting queues and activates channels.
- `rxrpc_expose_client_call()` marks a call ID as visible on the wire and links error delivery.
- `rxrpc_disconnect_client_call()` releases a channel, schedules final ACK retransmission, passes the channel to a waiting call, or idles the connection.
- `rxrpc_discard_expired_client_conns()` reaps idle client connections.
- `rxrpc_clean_up_local_conns()` kills all idle client connections during local endpoint teardown.

## Control flow
`call_object.c` queues new client calls on `local->new_client_calls`. The I/O thread invokes `rxrpc_connect_client_calls()`, which appends calls to their bundle and ensures capacity. Bundles allocate up to four connections, each with four channels, and an available-channel bitmask. `rxrpc_activate_one_channel()` assigns cid, call ID, connection reference, service ID, congestion state, starts the call timer, changes state to client send request, and wakes waiters.

## State and persistence behavior
Bundles are refcounted and have an active count for tree membership. Client connections get IDs from `local->conn_ids`, are listed for proc visibility, and may be cached idle after all channels drain. `DONT_REUSE` prevents reuse after exclusive calls, call counter exhaustion, epoch mismatch, invalid state, or sparse ID distance. Final ACKs are delayed briefly so a subsequent DATA packet can implicitly ACK the previous call.

## Dependencies and integration points
This file integrates with local endpoint IDR state, peer/key refs, connection allocation/destruction, call state/timers, congestion thresholds stored on peers, output final ACK retransmission, and the I/O thread client-call queue.

## Risks
Channel accounting is delicate: `avail_chans`, `act_chans`, bundle slots, and `conn->channels[]` must agree. Delayed final ACK state must be forced before unbundling. Reuse policy must avoid call ID wrap and stale epochs. Idle list refs must be balanced with reap/unbundle puts.

## Test signals
Cover parallel client calls, channel reuse, exclusive calls, service upgrade probing, call counter high-water behavior, idle reaping thresholds, final ACK deferral/subsumption, local teardown, and IDR leak assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rxrpc/conn_client.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rxrpc/conn_event.c -->
# sources/distributed-fs/ceph-client/net/rxrpc/conn_event.c

## Purpose
`conn_event.c` processes connection-level events and packets: aborts, challenges, responses, delayed final ACK retransmission, service security transitions, and queued RESPONSE transmission.

## Important APIs and functions
- `rxrpc_abort_conn()` marks a connection locally aborted and pokes it.
- `rxrpc_input_conn_packet()` handles BUSY, ABORT, CHALLENGE, and RESPONSE packets targeted at call number zero.
- `rxrpc_input_conn_event()` runs in the I/O thread for connection-attend events, abort propagation, response sending, service-secured notification, and final ACK timers.
- `rxrpc_process_connection()` is the workqueue processor for queued connection-level skbs and challenge issuance.
- `rxrpc_conn_retransmit_call()` retransmits cached terminal ACK or ABORT for a previous call.
- `rxrpc_post_response()` stores the newest challenge response for I/O-thread transmission.

## Control flow
Input routes callNumber-zero packets to `rxrpc_input_conn_packet()`. CHALLENGE packets are either posted to a call/socket for userspace-managed response or queued directly to the connection work processor. RESPONSE packets are verified by the security module, then the service connection transitions from challenging to service and a special skb mark is queued to the local I/O thread so all challenged calls can be notified. ABORTs mark the connection aborted and propagate completion to active channel calls.

## State and persistence behavior
Connection abort fields are stored before `RXRPC_CONN_ABORTED` with release semantics. Connection event bits track challenge and abort-call work. Channels cache terminal ACK/ABORT information after calls disconnect; delayed final ACK bits in `conn->flags` drive later retransmission. `tx_response` is protected by `local->lock` and retains the newest response by challenge serial.

## Dependencies and integration points
The file depends on security module hooks, output helpers for ACK/ABORT/RESPONSE, connection workqueue scheduling, call completion and socket notification, I/O-thread queues, and peer MTU/window data for ACK trailers.

## Risks
Security handshakes require careful skb unsharing for in-place decryption. Userspace-managed challenge delivery can fail if no call/socket can receive it. Final ACK retransmission must ignore stale call IDs. Connection abort propagation must handle all active channels without racing teardown.

## Test signals
Exercise rxkad/rxgk challenge-response flows, invalid challenge/response aborts, connection abort propagation, delayed final ACK retransmission, userspace-managed RESPONSE replacement, service-secured notification, and cloned skb verification paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rxrpc/conn_event.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rxrpc/conn_object.c -->
# sources/distributed-fs/ceph-client/net/rxrpc/conn_object.c

## Purpose
`conn_object.c` provides common connection allocation, lookup, refcounting, disconnection, timers, cleanup, service-connection reaping, and namespace teardown checks for both client and service connections.

## Important APIs and functions
- `rxrpc_alloc_connection()` initializes a connection object, timers, work items, queues, locks, default no-security module, and debug ID.
- `rxrpc_find_client_connection_rcu()` looks up client connections by local connection ID and validates epoch/local/peer port.
- `__rxrpc_disconnect_call()` caches terminal per-channel ACK/ABORT state.
- `rxrpc_disconnect_call()` detaches a completed call from client or service connection state.
- `rxrpc_poke_conn()`, `rxrpc_queue_conn()`, `rxrpc_put_connection()`, and `rxrpc_get_connection*()` manage connection work and refs.
- `rxrpc_service_connection_reaper()` expires idle service connections.
- `rxrpc_destroy_all_connections()` asserts namespace cleanup.

## Control flow
Call completion eventually calls `rxrpc_disconnect_call()`. Client calls delegate channel/cache handling to `conn_client.c`; service calls clear the channel, update idle timestamp, decrement active count, and arm the service reaper when the connection becomes idle. Connection timers poke the I/O thread. Last put schedules or performs cleanup depending on context, active timers, and processor work.

## State and persistence behavior
Connections are refcounted and RCU freed. Service connections also use `active` to represent live channel usage and reaper eligibility. Cleanup removes proc-list entries, handles PMTU probe loss state, purges connection rx queue and response skb, releases client ID/bundle/peer/local/key/security resources, drains tx page fragments, and waits for RCU before namespace counters reach zero.

## Dependencies and integration points
It integrates with client connection IDR, service peer trees, PMTU handling, output terminal retransmission, security clear hooks, local/peer/bundle refs, workqueues, timers, proc lists, and namespace lifecycle.

## Risks
Context-sensitive destruction is high risk: softirq or busy work paths must defer cleanup. Service reaping must not remove preallocated or active connections. `__rxrpc_disconnect_call()` must cache enough terminal state for duplicate packet handling after call free. Client lookup by cid must reject stale epoch or wrong peer port.

## Test signals
Test duplicate terminal packet handling after call free, service idle reaping, closed-service fast expiry, client lookup rejection, PMTU probe cleanup, namespace destroy leak assertions, and last-put cleanup from softirq/workqueue contexts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rxrpc/conn_object.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rxrpc/conn_service.c -->
# sources/distributed-fs/ceph-client/net/rxrpc/conn_service.c

## Purpose
`conn_service.c` manages service-side connection lookup, publication, preallocation, initialization from incoming packets, service upgrade, and unpublication from peer connection trees.

## Important APIs and functions
- `rxrpc_find_service_conn_rcu()` finds a service connection in a peer rbtree keyed by epoch and cid.
- `rxrpc_prealloc_service_connection()` allocates a service connection and places it on namespace service/proc lists.
- `rxrpc_new_incoming_connection()` initializes a preallocated connection from the first incoming packet and publishes it.
- `rxrpc_unpublish_service_conn()` removes a service connection from the peer tree.

## Control flow
Packet input first finds or creates a peer, then looks for a service connection under that peer. If no connection exists, `call_accept.c` consumes a preallocated connection and calls `rxrpc_new_incoming_connection()`. That function copies protocol identifiers, service ID, security index, direction, and security module, decides secured vs unsecured state, applies service ID upgrade when requested by the first packet, sets active count, and publishes into `peer->service_conns`.

## State and persistence behavior
Peer service connections are stored in an rbtree guarded by a seqlock so RCU readers can retry on mutation. Preallocated service connections start with refcount 2 because namespace service/proc lists hold them before activation. Published connections carry `RXRPC_CONN_IN_SERVICE_CONNS`; unpublish clears the flag and erases the node.

## Dependencies and integration points
This file is tightly coupled with `call_accept.c`, `io_thread.c`, `conn_object.c`, peer allocation/lookup, rxrpc security selection, namespace service connection lists, and service upgrade configuration in `rxrpc_sock`.

## Risks
The service tree is exposed to attacker-chosen epoch/cid values, so the rbtree design avoids hash bucket stuffing but still depends on correct seqlock retry behavior. Publishing assumes incoming connection setup is non-reentrant for a given connection. Replacement of dead extant nodes must avoid live duplicate connections.

## Test signals
Exercise lookup under concurrent publish/unpublish, new service connection setup, service upgrade on first packet only, security-index zero vs nonzero state, stale dead-node replacement, and unpublish during service reaping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rxrpc/conn_service.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rxrpc/input.c -->
# sources/distributed-fs/ceph-client/net/rxrpc/input.c

## Purpose
`input.c` implements per-call packet semantics. It processes DATA, ACK, ACKALL, and ABORT packets; maintains receive and transmit windows; queues data to recvmsg; handles jumbo packet splitting; derives RTT samples; drives congestion control; and feeds RACK/TLP loss detection.

## Important APIs and functions
- `rxrpc_input_call_packet()` dispatches packet types for an active call.
- `rxrpc_input_data()` and `rxrpc_input_data_one()` validate DATA, maintain receive SACK state, queue in-order/out-of-order packets, and choose ACK reasons.
- `rxrpc_input_ack()` validates ACKs, rotates the transmit window, parses soft ACKs and trailers, updates RTT/congestion/RACK/TLP, and responds to pings.
- `rxrpc_congestion_degrade()` reduces cwnd after idle transmission.
- `rxrpc_implicit_end_call()` handles a new service call implicitly ending the previous call on a channel.

## Control flow
Call packets are queued by `io_thread.c` and drained by `call_event.c`, which invokes `rxrpc_input_call_packet()`. DATA may transition a client into reply receive phase, reset server request idle timers, split jumbo subpackets, queue data to `recvmsg_queue`, and propose or send ACKs. ACKs validate monotonicity, hard-ACK packets by freeing txbufs, process soft ACK/NAK bitmaps per txqueue segment, update trailer-advertised receive window/MTU, advance phase state, drive congestion control, arm RACK loss timers, and send ping responses when required.

## State and persistence behavior
Receive state includes `ackr_window`, `ackr_wtop`, `ackr_sack_base`, `ackr_sack_table`, `rx_highest_seq`, `RXRPC_CALL_RX_LAST`, and queues for in-order and out-of-order skbs. Transmit state includes `tx_bottom`, `tx_top`, `tx_queue`, ACK counters, lost/retransmitted bits, `RXRPC_CALL_TX_LAST`, and `RXRPC_CALL_TX_ALL_ACKED`. Congestion state follows slow start, congestion avoidance, packet loss, and fast retransmit modes.

## Dependencies and integration points
It integrates with output ACK sending, txbuf release, recvmsg notification, call state completion, RTT helpers, RACK/TLP implementation, PMTU peer state, and connection terminal packet caching through later disconnection.

## Risks
ACK validation and txqueue rotation are correctness-critical and must reject window regression/overflow. Jumbo splitting clones skbs and mutates private header state. Receive SACK table indexing must stay aligned as the window advances. NAT/address-change heuristics convert certain ACKs into remote aborts. Congestion and RACK interact through shared ACK summary fields.

## Test signals
Test in-order, duplicate, out-of-order, beyond-window, after-last, and jumbo DATA; ACK hard/soft window advancement; ACK regression rejection; ACK trailer MTU/rwind updates; ACKALL; remote ABORT; implicit service call termination; congestion transitions; RACK/TLP hooks; and ping/ping-response RTT samples.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rxrpc/input.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rxrpc/input_rack.c -->
# sources/distributed-fs/ceph-client/net/rxrpc/input_rack.c

## Purpose
`input_rack.c` implements RACK-TLP loss detection for RxRPC DATA transmission. It tracks delivered transmit timestamps, detects reordering, marks lost packets, calculates and handles RACK reorder timers, sends tail loss probes, and processes ACKs of TLP probes.

## Important APIs and functions
- `rxrpc_input_rack_one()` and `rxrpc_input_rack()` update RACK state when packets are newly ACKed.
- `rxrpc_rack_detect_loss_and_arm_timer()` scans NACKed/unacked packets and arms reorder timers.
- `rxrpc_tlp_calc_pto()` computes probe timeout bounded by RTO.
- `rxrpc_tlp_send_probe()` sends new data or retransmits the highest transmitted DATA as a loss probe.
- `rxrpc_tlp_process_ack()` interprets ACKs for active TLP probes.
- `rxrpc_rack_timer_expired()` handles RACK reorder, TLP PTO, and RTO modes.

## Control flow
ACK processing in `input.c` calls RACK update helpers for hard and soft ACKs. RACK records the newest delivered transmit timestamp/sequence and tracks forward ACK progress. Loss detection computes a reordering window, scans txqueue NACK bits, and marks entries lost once their transmit time is old enough relative to the latest delivered packet. Timer expiry either rescans loss, sends a TLP probe, or marks losses on RTO.

## State and persistence behavior
State is stored in `struct rxrpc_call`: `rack_xmit_ts`, `rack_rtt`, `rack_rtt_ts`, `rack_reo_wnd`, multiplier/persistence fields, `rack_fack`, `rack_end_seq`, DSACK/reordering markers, `rack_timer_mode`, `rack_timo_at`, `tlp_serial`, `tlp_seq`, `tlp_is_retrans`, and `tlp_rtt_taken`. Packet loss is represented by per-txqueue `segment_lost` and `segment_retransmitted` bits plus call counters.

## Dependencies and integration points
This file depends on txqueue metadata populated by output, ACK summaries from `input.c`, RTO/RTT helpers, call transmit helpers in `call_event.c`, and timer scheduling in `call_event.c`.

## Risks
RACK decisions depend on correct transmit timestamps; lost packets are assigned `UINT_MAX` timestamps to avoid reuse. Reordering-window adaptation is approximate because RxRPC only has ACK duplicate reasons rather than TCP DSACK. TLP handling must avoid concurrent probes and clear probe state on sufficient ACK progress.

## Test signals
Use deterministic ACK/NAK traces for in-order delivery, reordering, duplicate ACKs, RTO recovery, TLP new-data probe, TLP retransmit probe, single-loss repair, and timer mode transitions. Tracepoints should show loss scans, lost marks, probe sends, and ACK interpretation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rxrpc/input_rack.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rxrpc/insecure.c -->
# sources/distributed-fs/ceph-client/net/rxrpc/insecure.c

## Purpose
`insecure.c` implements the `rxrpc_no_security` security module for anonymous/no-security RxRPC calls. It provides no-op connection/call crypto while still fitting the common `struct rxrpc_security` interface.

## Important APIs and functions
- `rxrpc_no_security` is the exported security module descriptor for `RXRPC_SECURITY_NONE`.
- `none_alloc_txbuf()` allocates plain DATA tx buffers sized up to one jumbo payload.
- `none_secure_packet()` sets plaintext packet length and marks full-size packets as jumbo-capable.
- `none_verify_packet()` marks received packets verified.
- `none_validate_challenge()` and `none_verify_response()` abort if challenge/response packets appear on a no-security connection.

## Control flow
When a call or connection chooses no security, output uses `alloc_txbuf()` and `secure_packet()` without adding crypto headers or checksums, input marks DATA verified immediately, and challenge/response paths reject protocol-inconsistent security handshakes.

## State and persistence behavior
The module stores no per-connection or per-call crypto state. Init, exit, free-call-crypto, and clear hooks are no-ops. Verification sets only `RXRPC_RX_VERIFIED` in skb private flags.

## Dependencies and integration points
It depends on common txbuf allocation, connection abort handling, skb private metadata, and the security lookup/selection code elsewhere. It is the default security pointer for newly allocated connections.

## Risks
The main risk is accidentally accepting secured-control packets on a no-security connection; this implementation aborts such packets as protocol errors. Plaintext packets depend on higher layers to enforce any minimum security policy.

## Test signals
Test anonymous calls, full-size plaintext jumbo eligibility, DATA verification flagging, CHALLENGE rejection, RESPONSE rejection, and no-op cleanup during call/connection teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rxrpc/insecure.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rxrpc/io_thread.c -->
# sources/distributed-fs/ceph-client/net/rxrpc/io_thread.c

## Purpose
`io_thread.c` is the top-level receive and event dispatch loop for a local RxRPC UDP endpoint. It accepts packets from the UDP encap hook, parses and routes packets to calls or connections, handles local socket error reports, rejects invalid packets, and runs the per-local I/O kthread loop.

## Important APIs and functions
- `rxrpc_encap_rcv()` receives UDP-encapsulated packets and queues them to the local I/O thread.
- `rxrpc_error_report()` transfers UDP error-queue skbs into the local rx queue.
- `rxrpc_direct_abort()` and `rxrpc_direct_conn_abort()` mark skbs for reject responses.
- `rxrpc_input_packet()` validates packet headers and routes to client or service connection lookup.
- `rxrpc_input_packet_on_conn()` routes connection-level packets, call packets, duplicate terminal packets, implicit service call ends, and new service calls.
- `rxrpc_io_thread()` drains packet queues, connection attend queue, call attend queue, client connection reaping, and new client calls.

## Control flow
The UDP encap hook queues marked skbs to `local->rx_queue` and wakes the I/O kthread. The thread splices rx packets into a private queue, extracts headers, validates packet type/service/call/seq fields, builds peer addresses, resolves client connections by IDR or service connections by peer tree, and then routes to connection or call handlers. Invalid packets are marked for BUSY/ABORT/CONN_ABORT rejection and sent by `rxrpc_reject_packet()`.

## State and persistence behavior
The local I/O thread serializes many call/connection state changes. It owns delayed rx injection movement, drains `conn_attend_q` and `call_attend_q`, processes client reap timer flags, assigns new client calls, and destroys the local endpoint when the kthread stops. Skb `mark` and `priority` carry dispatch and rejection metadata.

## Dependencies and integration points
It integrates with UDP socket `sk_user_data`, local endpoint lifecycle, peer lookup, service accept, client/service connection lookup, call packet queuing, connection event handling, peer error handling, output reject/version handling, PMTU probe ACK handling, and test-only rx delay/loss injection.

## Risks
The encap callback can run without the UDP socket lock while `sk_user_data` changes, so RCU handling and local/io_thread checks are critical. Header validation must reject malformed packets before state lookup. Duplicate terminal packet logic depends on cached channel state. Service packets can create calls, so backlog exhaustion and unsupported services must map to correct rejects/discards.

## Test signals
Test malformed headers, zero call/seq/service IDs, unsupported packet types, VERSION handling, client vs service routing, missing client connection abort, new service call creation, duplicate terminal retransmission, implicit service call end, UDP error queue handling, rx delay/loss injection, and I/O thread shutdown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rxrpc/io_thread.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rxrpc/key.c -->
# sources/distributed-fs/ceph-client/net/rxrpc/key.c

## Purpose
`key.c` implements the Linux key type for RxRPC client keys. It parses legacy v1 and AFS/YFS XDR token payloads, stores rxkad/rxgk token lists, exposes key descriptions/readback, requests socket keys by description, and creates server-side data/null keys.

## Important APIs and functions
- `key_type_rxrpc` registers the `rxrpc` key type with preparse, destroy, describe, and read operations.
- `rxrpc_preparse_xdr_rxkad()` parses RxKAD XDR tokens.
- `rxrpc_preparse_xdr_yfs_rxgk()` parses YFS-RxGK XDR tokens.
- `rxrpc_preparse_xdr()` validates the AFS token container and dispatches token parsing.
- `rxrpc_preparse()` handles empty no-security keys, XDR payloads, and legacy v1 rxkad payloads.
- `rxrpc_request_key()` requests a socket key by user-supplied description.
- `rxrpc_get_server_data_key()` builds an internal rxkad server data key from a session key.
- `rxrpc_get_null_key()` creates an instantiated no-security key.
- `rxrpc_read()` serializes AFS keys back to XDR form.

## Control flow
Key instantiation calls `rxrpc_preparse()`. For non-empty payloads larger than the XDR threshold, it first attempts XDR parsing. XDR parsing validates flags, printable cell name, token count, token lengths, padding, and supported security indices, then appends parsed tokens to the preparsed payload list. If not XDR, the v1 path validates version, security index, ticket length, allocates an rxkad token, copies session key/ticket fields, and sets key expiry.

## State and persistence behavior
Key payload data is a linked list of `struct rxrpc_key_token` plus a token count in `payload.data[1]`. Tokens own allocated rxkad or rxgk data, including padded rxgk ticket storage for direct XDR encoding. `prep->expiry` is reduced to token expiry. Destroy and failed preparse paths free token lists carefully.

## Dependencies and integration points
This file depends on Linux keyrings, network-domain key lookup, AFS token format constants, rxkad/rxgk structures from key headers, socket setup, server security/keying paths, and security modules that consume `rxrpc_key_token`.

## Risks
Parsing is exposed to userspace key payloads, so length, padding, printable cell, expiry, supported enctype/security, and overflow checks are important. `rxrpc_read()` intentionally refuses non-`afs@` descriptions and suppresses secret material when `no_leak_key` is set. Error paths must free partially allocated nested token data.

## Test signals
Test empty/null keys, valid legacy rxkad, valid XDR rxkad, valid XDR yfs-rxgk, unsupported token types, malformed lengths/padding, expired rxgk tokens, oversize tickets/keys, `rxrpc_read()` sizing and encoding, no-leak readback, socket key request errors, and server data key creation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/rxrpc/key.c -->
