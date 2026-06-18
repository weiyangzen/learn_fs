# sources/distributed-fs/openafs/src/rx/rx.c lines 1-8629

## Scope And Purpose

This chunk is the bulk of OpenAFS's Rx transport implementation. Rx is the UDP-based RPC substrate used by AFS services, and this file owns the core process-global runtime, connection and peer tables, call lifecycle, packet receive/send state machines, retransmission and congestion behavior, security challenge/response integration, server-thread scheduling, shutdown, debug accessors, and the beginning of per-RPC statistics support.

The covered lines start with platform-dependent includes and static prototypes, then define the exported initialization, service, connection, call, packet, timer, debug, and stats entry points. The chunk ends at the start of `rx_CopyProcessRPCStats`; later RPC stats copy/retrieve/enable/disable/marshalling functions continue after line 8629 and should be handled by the following chunk.

## Important APIs, Types, And Globals

The central runtime objects are `struct rx_connection`, `struct rx_call`, `struct rx_peer`, `struct rx_service`, `struct rx_packet`, and `struct rx_securityClass`. Most of their structure definitions live in included headers, but this file mutates their important runtime fields: connection ids and epochs, peer MTU/RTT/congestion data, per-channel call numbers and windows, call transmit/receive queues, service quota counters, security object pointers, per-connection specific data, event handles, and RPC stats queues.

Global state includes `rx_socket`, `rx_port`, `rx_host`, `rx_epoch`, `rx_nextCid`, `rx_connHashTable`, `rx_peerHashTable`, `rx_services`, free packet/call/server queues, `rx_incomingCallQueue`, `rx_idleServerQueue`, and process-wide stats such as `rx_stats`, `rxi_rpc_peer_stat_cnt`, and `rxi_rpc_process_stat_cnt`. `rxi_running` gates initialization and shutdown; `rxLastConn` caches the last matched connection to accelerate packet demultiplexing.

Locking is a first-class part of the design. The file initializes and uses global locks for connection, peer, packet, call, server-pool, quota, stats, and key-create state. The comments document a hierarchy where `rx_connHashTable_lock`, `conn_call_lock`, and `call->lock` are high-impact ordering constraints. Under `RX_ENABLE_LOCKS`, queue membership is tracked through `call->call_queue_lock` to make call reset safe while another thread may be moving the call between queues.

Exported or externally visible APIs in this chunk include:

- Runtime lifecycle: `rx_InitHost`, `rx_Init`, `rx_Finalize`, `shutdown_rx`, `rxi_IsRunning`.
- Client and service setup: `rx_NewConnection`, `rx_DestroyConnection`, `rx_GetConnection`, `rx_NewServiceHost`, `rx_NewService`, `rx_SetSecurityConfiguration`.
- Call lifecycle: `rx_NewCall`, `rx_EndCall`, `rx_SetArrivalProc`, `rx_InterruptCall`.
- Connection timers/config: `rx_SetConnDeadTime`, `rx_SetConnHardDeadTime`, `rx_SetConnIdleDeadTime`, corresponding getters, `rx_SetConnSecondsUntilNatPing`, `rx_rto_setPeerTimeoutSecs`.
- Packet-processing internals used across Rx modules: `rxi_ReceivePacket`, `rxi_SendAck`, `rxi_Send`, `rxi_Start`, `rxi_SendConnectionAbort`, `rxi_ConnectionError`, `rxi_CallError`, `rxi_PacketsUnWait`, `rxi_FindPeer`, `rxi_SetPeerMtu`, `rx_GetNetworkError`.
- Debug/stat accessors: `rx_PrintStats`, `rx_PrintPeerStats`, `rx_GetServerDebug`, `rx_GetServerStats`, `rx_GetServerVersion`, `rx_GetServerConnections`, `rx_GetServerPeers`, `rx_GetLocalPeers`, `rx_StatsOnOff`, `rx_DebugOnOff`.
- Security object refcount helpers: `rxs_Release`, `rxs_Ref`, `rxs_DecRef`, `rxs_SetRefs`.
- User-space specific data hooks: `rx_KeyCreate`, `rx_SetSpecific`, `rx_SetServiceSpecific`, `rx_GetSpecific`, `rx_GetServiceSpecific`.
- Beginning of RPC operation stats: `rx_ClearProcessRPCStats`, `rx_ClearPeerRPCStats`, and the first lines of `rx_CopyProcessRPCStats`.

## Initialization, Services, And Server Scheduling

`rx_InitHost` is the main runtime initializer. It runs one-time pthread lock initialization, prevents duplicate initialization through `rx_init_mutex` and `rxi_running`, resets statistics, initializes user-space thread support, creates the UDP socket, allocates and zeroes connection and peer hash tables, seeds packet pools, initializes clocks and events, chooses/binds the Rx port, generates a random epoch and next connection id, initializes queues, starts the listener, and finally marks Rx running. The epoch high bit is set and a specific bit is cleared, which matters later because some connection matching rules interpret high-bit epochs specially.

`rx_Init` is a convenience wrapper binding to `INADDR_ANY`. `rx_StartServer` starts server processes according to service `minProcs`/`maxProcs`, initializes quota deficit accounting, schedules connection reaping, and can donate the current thread into the server pool. `rxi_StartServerProcs` computes the required thread count from all registered services: the sum of service minimums plus enough headroom to let one service reach its maximum under good conditions.

`rx_NewServiceHost` registers a service by host, UDP port, service id, service name, security-object vector, and execute callback. It rejects service id zero, resolves port zero against the default initialized port, reuses sockets for multiple services on the same host/port, initializes default service limits and timeout values, and stores the new service in `rx_services` only after fully populating it. `rx_NewService` binds to all local addresses, and `rx_SetSecurityConfiguration` fans configuration changes out to each service security object.

Server scheduling is built around `rx_incomingCallQueue`, `rx_idleServerQueue`, `rx_freeServerQueue`, and quota helpers. `QuotaOK`, `QuotaOK_noreserve`, and `ReturnToServerPool` enforce service `maxProcs`, preserve service `minProcs`, and maintain `rxi_availProcs`/`rxi_minDeficit`. `rx_GetCall` has separate locked and unlocked implementations but the same behavior: return the next eligible incoming call, prefer calls whose first packet is ready, keep one first-come/first-served path to reduce starvation, and otherwise park a server queue entry on the idle queue. `rxi_AttachServerProc` either assigns a ready server, hands off through the hot-thread mechanism, or queues the call for later.

## Connection, Peer, And Call Lifecycle

`rx_NewConnection` creates client connections. It allocates a connection, initializes locks, assigns `RX_CLIENT_CONNECTION`, `rx_epoch`, `rx_nextCid`, a peer from `rxi_FindPeer`, service/security identifiers, dead-time defaults, per-channel send/receive windows, and security state via `RXS_NewConnection`. It inserts the connection into `rx_connHashTable` under `rx_connHashTable_lock` and increments client connection stats.

`rxi_FindConnection` is the packet-demux path for both client and server connections. It first checks `rxLastConn`, then searches the hash table with `rxi_ConnectionMatch`. It refuses packets with a mismatched security index, creates server connections on demand when the service and security index are valid, initializes their service, peer, security, timeout, and window fields, calls `RXS_NewConnection`, and invokes `service->newConnProc` if present. Unknown services cause the caller to send `RX_INVALID_OPERATION` raw aborts for non-abort packets.

`rxi_FindPeer` looks up or creates peers by `(host, port)`, initializes peer locks and RPC stats queues, and increments references when requested. Peer state persists across connections until idle reaping; it carries RTT, MTU, datagram, congestion-window, network-error, byte-count, and RPC-stat information that newly reset calls inherit.

`rx_NewCall` is the client call allocator. It serializes channel selection with `conn_call_lock` and `RX_CONN_MAKECALL_ACTIVE/WAITING`, avoids channels that recently returned `BUSY`, reuses dallying calls when possible, allocates missing call structures through `rxi_NewCall`, sets the call active and initially sending, records timing and byte counters, and schedules keepalive and MTU growth events. It carefully drops `conn_call_lock` around potentially expensive reset work to avoid blocking `rx_EndCall`.

`rx_EndCall` completes a call. For server calls it flushes pending output, moves calls to `HOLD` until response packets are acknowledged, or to `DALLY` when all outgoing data is accounted for. For client calls it ensures input/output completion, sends any delayed ACK immediately, records busy-channel hints on timeout, marks the call dallying, clears app packet/iovec state, releases the begin reference, and maps Rx errors to local system errors before returning. `rxi_FreeCall` later resets and moves inactive calls to `rx_freeCallQueue`, increments the channel call number when appropriate, and may finish destroying a connection marked `RX_CONN_DESTROY_ME`.

Connection destruction is staged. `rx_DestroyConnection` and `rxi_DestroyConnection` call `rxi_DestroyConnectionNoLock` under the connection hash lock. Destruction decrements refcounts, defers when calls or make-call activity are still present, forces final delayed ACKs for client calls, removes the connection from the hash table and `rxLastConn`, asserts no pending connection events, and pushes the connection onto `rx_connCleanup_list`. `rxi_CleanupConnection`, called after dropping the hash lock, notifies service/security destroy hooks, drops the peer reference, runs connection-specific destructors, destroys locks, and frees the connection.

## Packet Receive Control Flow

`rxi_ReceivePacket` is the main inbound dispatch routine. It handles version and debug packets before connection lookup, optionally passes packets through `rx_justReceived`, derives whether the local endpoint is acting as client or server from `RX_CLIENT_INITIATED`, finds or creates the connection, updates peer receive stats, rejects packets on errored connections with connection aborts, and dispatches connection-level abort/challenge/response/params packets when `callNumber` is zero.

For call-specific packets, `rxi_ReceiveClientCall` verifies that the channel has an expected call number, records `BUSY` timestamps, and ignores late ACKs for dallying calls. `rxi_ReceiveServerCall` validates call numbers, requires new calls to begin with plausible DATA packets, enforces the busy threshold through `rxi_AbortIfServerBusy`, allocates or resets channel call structures for incoming client calls, and protects active calls from being overwritten by newer call numbers.

`rxi_ReceiveDataPacket` is the receive-window and receive-queue engine. It handles jumbo packets by splitting a datagram into logical packets, rejects receive packets under kernel quota pressure, records packet checksum use, inserts in-order or out-of-order packets into `call->rq`, detects duplicates, rejects packets beyond the receive window, tracks `RX_LAST_PACKET`, `RX_CALL_HAVE_LAST`, and `RX_CALL_RECEIVE_DONE`, invokes arrival callbacks, wakes readers, fills waiting iovecs, and decides whether to send immediate ACKs, delayed hard ACKs, delayed soft ACKs, or no ACK. It also attempts to attach a server process to newly arriving server calls after the first packet.

`rxi_ReceiveAckPacket` is the transmit-queue ACK processor. It validates that the peer's ACK window does not move backwards, parses `firstPacket`, `previousPacket`, `serial`, explicit ACK/NACK bytes, and optional AFS 3.3/3.4/3.5 trailer fields. It frees or marks implicitly acknowledged packets, updates soft ACK state, computes RTT samples for newly acknowledged packets, updates peer MTU/window/jumbogram capabilities, wakes senders when the transmit window opens, restarts the RTO timer on new ACKs, enters or exits fast recovery, adjusts congestion window and datagram packet counts, and restarts transmission through `rxi_Start` when the transmit queue still has work. It marks invalid/truncated/out-of-order ACKs so packet stats can count them as spurious.

`rxi_ReceiveChallengePacket` and `rxi_ReceiveResponsePacket` integrate Rx security classes. Clients ignore challenges when idle to avoid oracle behavior, otherwise ask `RXS_GetResponse` to populate a response. Servers ignore impossible or repeated responses, verify responses with `RXS_CheckResponse`, throttle aborts for bad credentials, attach waiting calls after successful authentication, and update reachability. `rxi_ChallengeOn` creates and schedules challenge retries through `rxi_ChallengeEvent`, which aborts precall calls after max retries.

## Packet Send, ACK, RTO, And Congestion Behavior

The retransmission timeout helpers implement a TCP-style RTO. `rxi_rto_packet_sent` starts an event when the first unacknowledged packet is sent; `rxi_rto_packet_acked` cancels and restarts the timer for the next outstanding sent packet; `rxi_Resend` fires on timeout, marks unacked packets unsent, doubles the RTO up to 60 seconds, enters fast recovery, collapses congestion and datagram windows, updates peer congestion sequence state, and calls `rxi_Start`.

`rxi_SendAck` constructs ACK packets from the receive queue. It advertises the first packet not yet delivered, explicit ACK/NACK bytes for queued receive packets, optional MTU/window/datagram trailer data, slow-start support, and `RX_REQUEST_ACK` for ping ACKs. It can pad MTU probe ACKs, resets soft/hard ACK counters, handles `ACKALL` semantics, calls `rxi_Send`, and returns the optional packet to the caller for reuse.

`rxi_SendList`, `rxi_SendXmitList`, and `rxi_Start` drive data transmission. `rxi_Start` scans the transmit queue, skips ACKed packets, respects send window and congestion window limits, marks window wait flags, batches packets into `call->xmitList`, and invokes `rxi_SendXmitList`. `rxi_SendXmitList` enforces jumbogram constraints: no more than peer/call datagram packet limits, no retransmitted packets inside jumbograms, no oversized or multi-iovec packet grouping, and bounded bursts. `rxi_SendList` stamps send times, chooses when to request ACKs, sets `RX_MORE_PACKETS`, sends via `rxi_SendPacket` or `rxi_SendPacketList`, updates packet/peer stats, and starts RTO tracking.

`rxi_Send` is the generic protected send path for non-list packets. It stamps `userStatus`, gives the security object `RXS_SendPacket` a chance to transform or reject the packet, cancels delayed ACKs, sends while holding a temporary call reference, and updates last-send timestamps for real traffic and ping ACKs.

Abort handling is deliberately throttled. `rxi_SendCallAbort` and `rxi_SendConnectionAbort` send immediate aborts for clients, forced cases, opcodes that are not misbehavior, or until thresholds are exceeded. After thresholds, they schedule delayed abort events through `rxi_SendDelayedCallAbort` or `rxi_SendDelayedConnAbort` to avoid loops or hammering peers. `rxi_ConnectionError` cancels connection events, marks each call in error, and records fatal-error stats; `rxi_CallError` resets call queues when safe and preserves the first error.

## Timers, Reachability, NAT, And Reaping

`rxi_CheckCall` is the timeout and cleanup judge used by keepalive events and connection reaping. It checks ICMP/network-error generation under `AFS_RXERRQ_ENV`, detects large backward clock jumps, accounts for smoothed RTT fudge, applies dead, idle, and hard timeouts, can shrink MTU after message-size retry errors, and frees non-active timed-out calls when safe.

`rxi_KeepAliveEvent` sends ping ACKs when a call has not sent traffic within `secondsUntilPing`, reschedules itself, and releases its event-held call reference. `rxi_GrowMTUEvent` sends padded MTU ping ACKs when peer state and idle-dead-time configuration make MTU probing useful. `rxi_NatKeepAliveEvent` sends a minimal version packet to keep NAT mappings alive and reschedules only if the connection still has references. `rxi_CheckReachEvent`, `rxi_CheckConnReach`, and `rxi_UpdatePeerReach` implement optional server-side reachability checks before attaching precall calls, sending ping ACKs and delaying attachment until a recent peer response is seen.

`rxi_ReapConnections` periodically scans all connection buckets and peer buckets. It calls `rxi_CheckCall` for reachable calls, destroys idle server connections and refcount-zero client connections, drains `rx_connCleanup_list`, frees idle peers and their per-peer RPC stats after `rx_idlePeerTime`, wakes packet waiters, and posts itself again after `RX_REAP_TIME`. This is the main persistence boundary for long-lived in-memory peer and connection state.

`rx_Finalize` is the user-space graceful client/server shutdown path. It marks Rx not running, deletes cached client connections, destroys client connections in the hash table, drains cleanup lists, flushes trace state, and cleans up Winsock on Windows. `shutdown_rx` is a broader teardown routine that clears listener/event/clock state, frees free calls, idle server entries, peers, peer RPC stats, services, connections and their calls, server queue entries, hash tables, and resets quota globals.

## Debug, Monitoring, And RPC Stats

`rx_PrintTheseStats`, `rx_PrintStats`, and `rx_PrintPeerStats` format local statistics for humans, including packet allocation failures, read/send counters, RTT samples, connection/peer/call counts, and peer RTT/send counters.

When `RXDEBUG` or `MAKEDEBUGCALL` is enabled, `MakeDebugCall` sends raw debug or version packets over UDP and waits with exponential backoff for a response matching a generated call number. `rx_GetServerDebug`, `rx_GetServerStats`, `rx_GetServerVersion`, `rx_GetServerConnections`, and `rx_GetServerPeers` wrap that raw mechanism, convert network-byte-order fields, and negotiate supported debug structure features for older server formats. `rx_GetLocalPeers` directly snapshots local peer state under peer locks.

The chunk begins the RPC operation statistics subsystem. `processStats` stores process-wide interface/function totals, `peerStats` stores the union of all peer RPC stats, and `rxi_monitor_processStats`/`rxi_monitor_peerStats` gate collection. `rxi_ClearRPCOpStat` resets invocation, byte, queue-time, and execution-time counters with min fields set high. `rxi_FindRpcStat` locates or allocates a per-interface array of `rx_function_entry_v1_t` records, links it into the requested queue, and optionally links peer stats into the global peer list. `rx_ClearProcessRPCStats` and `rx_ClearPeerRPCStats` reset all operation entries for an interface. `rx_CopyProcessRPCStats` starts at the chunk boundary and is not complete here.

## Dependencies And Integration Points

This file depends on OpenAFS portability layers for kernel/user-space differences, time, sockets, memory allocation, locking, condition variables, tracing, and byte-order conversion. Important local dependencies include `rx_globals.h`, `rx_internal.h`, `rx_event.h`, `rx_peer.h`, `rx_conn.h`, `rx_call.h`, `rx_packet.h`, `rx_server.h`, and `rx_stats.h`.

Security integration is abstracted through `RXS_*` hooks: new/destroy connection, packet send processing, authentication checks, challenge creation, challenge packet fill, response generation, response validation, close/release, and configuration. Server services integrate through callbacks such as `executeRequestProc`, `beforeProc`, `afterProc`, `postProc`, `newConnProc`, and `destroyConnProc`.

Networking integration spans UDP socket creation and send/receive helpers, raw debug calls, socket error queue handling under `AFS_RXERRQ_ENV`, ICMP translation, MTU discovery under `AFS_ADAPT_PMTU`, and platform-specific behavior for kernel builds, Windows, pthreads, LWP, and TSFPQ packet queues. Packet memory and queue operations rely heavily on the Rx packet allocator and `opr_queue`.

## State And Persistence Behavior

All state in this chunk is in-memory process or kernel module state. There is no file persistence. Long-lived state persists until explicit shutdown or reaping: peer RTT/MTU/congestion estimates, peer byte counters, peer RPC stats, connection call-number vectors, per-channel windows, service registrations, process stats, debug counters, and free object queues.

Event objects hold references to calls or connections. Delayed ACK, resend, keepalive, grow-MTU, NAT keepalive, delayed abort, reachability, challenge, and reap events must cancel or release those references exactly once. Several code paths explicitly cancel events before reset/destruction, and destruction asserts that connection events are gone before final cleanup.

The service scheduler persists queued precalls in `rx_incomingCallQueue` until a server thread and quota are available. Call reset must safely remove calls from whichever queue currently owns them. The transmit and receive queues persist packet buffers across application reads/writes, ACK processing, retransmission, dally/hold states, and final reset.

## Risks And Edge Cases

The highest-risk area is concurrency. The code interleaves global hash-table locks, connection locks, call locks, peer locks, packet locks, event callbacks, and condition-variable wakeups. Deadlocks, missed wakeups, refcount leaks, and use-after-free bugs are plausible if lock ordering, event reference accounting, or queue ownership is changed casually.

Packet protocol correctness is also fragile. ACK validation, duplicate/out-of-window DATA handling, `ACKALL`, `BUSY`, jumbograms, soft ACKs versus hard ACKs, delayed ACK timing, call-number advancement, and client/server interpretation of `RX_CLIENT_INITIATED` must remain compatible with older OpenAFS peers. The ACK parser contains explicit compatibility paths for older AFS versions and peers that reported incorrect previous-packet values.

Congestion and MTU behavior has many interacting controls: RTO, RTT variance, slow start, fast recovery, NACK thresholds, datagram grouping, peer max MTU, NAT MTU, interface MTU, packet-size pings, ICMP EMSGSIZE, and message-size retry fallback. Small changes can cause either packet loss amplification or severe throughput regressions.

Security and abuse-resistance risks include challenge/response retries, ignoring idle challenges to avoid oracle behavior, delayed abort throttling for bad credentials, unknown-service raw aborts, and ensuring a server call is not attached before authentication and optional reachability checks complete.

Shutdown and reaping are risky because they intentionally traverse mutable global hash tables while releasing locks to avoid deadlocks or contention. Reaping peer RPC stats also touches both per-peer queues and the global `peerStats` queue; stat counters must remain consistent when peers are removed.

## Test Signals

Good tests for this chunk need to exercise the transport rather than just individual helpers:

- Client/server call lifecycle: create services, start server threads, make calls over all `RX_MAXCALLS` channels, complete calls successfully, abort calls, interrupt calls, destroy connections, and verify no leaked calls/connections.
- Packet receive behavior: duplicates, out-of-order packets, packets beyond receive window, missing first packet, late ACKs in dally state, connection-level abort/challenge/response packets, unknown service ids, and busy-threshold aborts.
- ACK and retransmission behavior: soft ACKs, hard ACKs, ping responses, invalid backward ACK windows, NACK-triggered fast recovery, RTO timeout resend, ACKALL, final server HOLD-to-DALLY transition, and delayed ACK cancellation.
- MTU/congestion behavior: old-peer ACK trailers, AFS 3.5 jumbogram negotiation, MTU probe ACKs, ICMP/EMSGSIZE peer MTU shrink, NAT MTU adjustment, and throughput recovery after loss.
- Authentication behavior: valid challenge/response, invalid response delayed aborts, challenge retry exhaustion, idle-client challenge ignoring, and server attachment only after authentication.
- Timer/reaping behavior: dead/idle/hard call timeouts, NAT keepalive scheduling/cancellation, reachability attach-wait, event reference release, idle peer/connection reaping, graceful `rx_Finalize`, and full `shutdown_rx`.
- Debug/stat behavior: local print functions, raw debug queries, old/new debug connection structures, peer snapshots, RPC stat clear/allocation, and byte-order conversions.

Runtime sanitizers, lock-order debugging, packet/refcount tracking builds, RXDEBUG packet traces, and stress tests with packet loss/reordering are especially valuable signals because many defects here only appear under concurrency, loss, or shutdown races.
