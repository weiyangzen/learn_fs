# Research: sources/distributed-fs/openafs/src/rx/rx.c

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-007794`: lines 1-8629, `Docs/researches/chunks/subset-b-007794_research.md`
- `subset-b-007795`: lines 8630-9761, `Docs/researches/chunks/subset-b-007795_research.md`

## Chunk Research

### subset-b-007794: lines 1-8629

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

### subset-b-007795: lines 8630-9761

# sources/distributed-fs/openafs/src/rx/rx.c lines 8630-9761

## Purpose

This chunk implements the public and internal tail of RX RPC statistics handling, plus a few platform/debug helpers near the end of `rx.c`. It begins in the middle of `rx_CopyProcessRPCStats`, whose prologue at lines 8624-8629 allocates a single `rx_function_entry_v1_t` copy buffer; the visible lines complete the copy, lookup, and release behavior for one process-level RPC operation statistic. The rest of the statistics block records per-call timing/byte counts, marshals process and peer statistics into the rxstat wire representation, exposes query/enable/disable/clear controls, and installs the authorization callback used by the rxstat service.

The non-statistics tail contains Windows DLL initialization, optional debug dumping of all live RX calls, socket error-queue draining and retry-aware sends for platforms with `AFS_RXERRQ_ENV`, the common `rxi_NetSend` wrapper used by packet transmission code, and `rxi_GetLocalAddr`, which reports the loopback-or-bound local address RX should use for packets sent to itself.

## Important APIs, Types, and Functions

- `rx_CopyProcessRPCStats(afs_uint64 op)` completes a single-operation process-stat copy. `op` packs `rxInterface` in the high 32 bits and `currentFunc` in the low 32 bits. It requires process stats to be enabled, rejects interface `-1`, finds the matching `rx_interface_stat` in `processStats`, copies one `rx_function_entry_v1_t`, and returns an owned blob for accessor helpers in `rx.h`.
- `rx_CopyPeerRPCStats(afs_uint64 op, afs_uint32 peerHost, afs_uint16 peerPort)` mirrors the process copy path for a specific `rx_peer`, using `rxi_FindPeer(peerHost, peerPort, 0)` and the peer's `rpcStats` queue.
- `rx_ReleaseRPCStats(void *stats)` frees the one-entry blob returned by the copy helpers.
- `rxi_AddRpcStat(...)` is the shared update primitive. It finds or creates an `rx_interface_stat` entry, verifies that the recorded function count matches the caller's interface shape, bounds-checks `currentFunc`, then increments invocation count, byte counters, queue/execution time sums, squared sums, and min/max clocks.
- `rxi_IncrementTimeAndCount(...)` is the internal recorder called by `rx_RecordCallStatistics` in `rx_call.c`. It updates peer and/or process queues depending on `rxi_monitor_peerStats` and `rxi_monitor_processStats`.
- `rx_IncrementTimeAndCount(...)` is the legacy public wrapper for older rxgen stubs. It converts `afs_hyper_t` byte counters to `afs_uint64` and delegates to `rxi_IncrementTimeAndCount`.
- `rx_MarshallProcessRPCStats(...)` serializes an array of `rx_function_entry_v1_t` records as `afs_uint32` words. Each 64-bit counter is split into high and low words, and each `struct clock` contributes `sec` and `usec`.
- `rx_RetrieveProcessRPCStats(...)` and `rx_RetrievePeerRPCStats(...)` snapshot all enabled process or peer stats into an allocated wire buffer for rxstat service responses.
- `rx_FreeRPCStats(...)` releases buffers allocated by the retrieve APIs.
- `rx_queryProcessRPCStats`, `rx_queryPeerRPCStats`, `rx_enableProcessRPCStats`, `rx_enablePeerRPCStats`, `rx_disableProcessRPCStats`, `rx_disablePeerRPCStats`, `rx_clearProcessRPCStats`, and `rx_clearPeerRPCStats` are the operational control surface.
- `rx_SetRxStatUserOk` and `rx_RxStatUserOk` manage the authorization callback consulted by `src/rxstat/rxstat.c` before enabling, disabling, or clearing stats through the `MRXSTATS_*` RPCs.
- `rx_DumpCalls(FILE *outputFile, char *cookie)` is available outside the kernel and, when `RXDEBUG_PACKET` is built, writes call queue depths, state, connection IDs, timers, abort state, and optional refcount diagnostics for every `rx_call` in `rx_allCallsp`.
- `rxi_HandleSocketErrors`, `NetSend_retry`, and `rxi_NetSend` isolate platform socket send behavior. `rxi_NetSend` refuses sends after RX shutdown, otherwise calls `osi_NetSend` directly or via error-queue retries.
- `rxi_GetLocalAddr(struct sockaddr_in *sin)` fills the address RX uses for local self-traffic after successful `rx_InitHost`.

The central data types come from `rx.h`: `rx_function_entry_v1_t` stores remote peer/port, direction, interface/function identity, invocation and byte counters, and queue/execution timing aggregates; `rx_interface_stat_t` embeds queue links plus a flexible `stats[1]` array that this code allocates as `sizeof(rx_interface_stat_t) + totalFunc * sizeof(rx_function_entry_v1_t)`. Clear flags such as `AFS_RX_STATS_CLEAR_INVOCATIONS` and `AFS_RX_STATS_CLEAR_EXEC_TIME_MAX` select fields for bulk zeroing or min/max reset.

## Control Flow

RPC statistics collection starts when an admin or server initialization path calls one of the enable functions. Both enable functions take `rx_rpc_stats`, set global `rx_enable_stats = 1`, and set either `rxi_monitor_processStats` or `rxi_monitor_peerStats`. The global `rx_enable_stats` is consumed by generated rxgen stubs; modern generated stubs call `rx_RecordCallStatistics`, which computes queue time as `call->startTime - call->queueTime` and execution time as current time minus `call->startTime`, then calls `rxi_IncrementTimeAndCount`.

`rxi_IncrementTimeAndCount` exits immediately if neither monitor flag is set. Otherwise it holds `rx_rpc_stats` across the whole update. For peer stats it also takes `peer->peer_lock`, adds or updates an entry on `peer->rpcStats`, and, on first creation, links the same stat object into the global `peerStats` queue via `entryPeers`. For process stats it adds or updates an entry in `processStats` using wildcard remote host/port values `0xffffffff`. `rxi_AddRpcStat` rejects inconsistent interface metadata before writing counters, so a reused interface id with a different `totalFunc` or an out-of-range function index will silently skip that invocation by returning `-1`.

Snapshot retrieval follows a two-phase shape. `rx_RetrieveProcessRPCStats` and `rx_RetrievePeerRPCStats` initialize all out parameters to empty success, set `*myVersion = RX_STATS_RETRIEVAL_VERSION`, acquire `rx_rpc_stats`, and return an empty success if the relevant monitor is disabled. For supported callers, they compute `space = stat_count * sizeof(rx_function_entry_v1_t)` using `rxi_rpc_process_stat_cnt` or `rxi_rpc_peer_stat_cnt`, allocate that much memory through `rxi_Alloc`, then scan `processStats` or global `peerStats` and call `rx_MarshallProcessRPCStats` for each interface's function array. On allocation failure they return `ENOMEM` after leaving the result pointer null. The rxstat service wraps these functions and reports `rpcStats_len` as allocated bytes divided by `sizeof(afs_uint32)`.

Disabling process stats holds `rx_rpc_stats`, clears `rxi_monitor_processStats`, disables global `rx_enable_stats` if peer monitoring is also off, walks `processStats` with `opr_queue_ScanSafe`, unlinks every stat, frees its flexible allocation, and decrements `rxi_rpc_process_stat_cnt` by the freed function count.

Disabling peer stats clears `rxi_monitor_peerStats` and potentially `rx_enable_stats`, then walks every bucket of `rx_peerHashTable`. For each bucket it takes `rx_peerHashTable_lock` and `rx_rpc_stats`, tries to acquire each peer lock, and only clears peers whose `peer_lock` is immediately available. For a clearable peer it temporarily unlinks the peer from the hash chain, bumps neighboring and target refcounts before dropping the hash-table lock, removes all per-peer `rpcStats` entries from both the peer queue and `peerStats`, frees each allocation, decrements `rxi_rpc_peer_stat_cnt`, releases `peer_lock`, reacquires the hash-table lock, drops temporary refs, and continues. Peers whose lock cannot be acquired are left in place and skipped for that pass.

The two clear functions keep stat objects allocated but reset selected fields. They scan `processStats` or `peerStats` under `rx_rpc_stats`, iterate over each interface's `func_total`, and apply the requested bitmask. Counters and sums are zeroed, max clocks are set to zero, and min clocks are reset to the sentinel `9999999` seconds/useconds used by the allocator/clear path.

The send helper path is short: `rxi_NetSend` first checks `rxi_IsRunning()`. If RX is still running it delegates to `NetSend_retry` when `AFS_RXERRQ_ENV` is enabled; that helper retries `osi_NetSend` up to `RXI_SENDMSG_RETRY` times, draining pending asynchronous socket errors with `rxi_HandleSocketErrors` after failed attempts. Without that build option it calls `osi_NetSend` once. If RX is no longer running, `rxi_NetSend` returns `WSAESHUTDOWN` on Windows or `ESHUTDOWN` elsewhere.

## State and Persistence Behavior

All stats in this chunk are in-memory runtime state. There is no durable persistence; disabling stats frees the currently accumulated structures, while clear operations preserve structure identity but reset selected fields. Process stats accumulate for the process lifetime until disabled or cleared. Peer stats are tied to `rx_peer` lifetime and are also represented in the global `peerStats` queue so retrieval can scan all peer-backed stat blocks without traversing every peer hash bucket.

The state accounting is explicit: `rxi_rpc_process_stat_cnt` and `rxi_rpc_peer_stat_cnt` count function entries, not interface objects. They are incremented by `totalFunc` when `rxi_FindRpcStat` creates an interface stat and decremented by the same function count when freeing. Retrieval uses those counters to size the serialized output, so counter/queue drift would either truncate marshaling, overrun the allocation, or report misleading `statCount`.

The monitor flags gate both collection and retrieval. `rx_enable_stats` is a broader exported flag that generated stubs test before invoking the recorder; `rxi_monitor_processStats` and `rxi_monitor_peerStats` select which queues are actually updated. Query and enable paths consistently use `rx_rpc_stats`, but `rx_disablePeerRPCStats` writes `rxi_monitor_peerStats` and `rx_enable_stats` before taking `rx_rpc_stats`, making those particular flag transitions more concurrency-sensitive than the process-disable path.

Socket helper state is limited to transient error queues and the global RX running flag. `rxi_HandleSocketErrors` preserves userland `errno`, allocates a 256-byte control-message buffer, repeatedly calls `osi_HandleSocketError` until no pending errors remain, then frees the buffer. `rxi_GetLocalAddr` reads the global `rx_host` and `rx_port`; it returns the configured bind address when nonzero or IPv4 loopback `127.0.0.1` otherwise.

## Dependencies and Integration Points

- Generated rxgen stubs test `rx_enable_stats` and call `rx_RecordCallStatistics`, which lives in `rx_call.c` and feeds this chunk's `rxi_IncrementTimeAndCount`.
- `src/rxstat/rxstat.c` exposes these APIs through the `RX_STATS_SERVICE_ID` service. Retrieve/query methods call directly into the retrieval/query functions, while enable/disable/clear methods first call `rx_RxStatUserOk`.
- Server and client initialization code such as `bosserver`, `kaserver`, `ptserver`, `vlserver`, `viced`, `volser`, and kernel pioctl paths can enable process stats directly.
- `rx.h` publishes the stat structs, clear flags, retrieval version constants, and inline accessors such as `RPCOpStat_NumCalls`, `RPCOpStat_BytesSent`, and `RPCOpStat_ExecTimeSum` for one-entry copy blobs.
- `rx_prototypes.h` exports the process/peer retrieval, query, enable/disable, clear, copy, release, authorization, `rxi_NetSend`, and local-address helper prototypes to other RX components.
- `rxi_NetSend` is the common network send dependency for `rx_packet.c` packet transmission, multi-packet sends, raw abort sends, and internal keepalive/challenge paths in `rx.c`.
- Queue manipulation depends on `opr_queue` primitives; memory management uses `rxi_Alloc`/`rxi_Free`; timing math uses `clock_GetTime`, `clock_Add`, `clock_AddSq`, `clock_Lt`, and `clock_Gt`.
- Platform integration is controlled by build flags: `AFS_NT40_ENV` for `DllMain` and Windows shutdown codes, `RXDEBUG_PACKET` for call dumping, `RX_ENABLE_LOCKS`/`RX_REFCOUNT_CHECK` for extra dump fields, and `AFS_RXERRQ_ENV` for Linux-style asynchronous socket error handling.

## Risks and Edge Cases

- Both copy helpers allocate their one-entry buffer before checking monitor flags, `rxInterface == -1`, and peer existence. Early returns on those checks do not free `rpcop_stat`, so repeated failed copy calls can leak `sizeof(rx_function_entry_v1_t)` allocations. The not-found-after-lock path does free correctly.
- `rx_CopyPeerRPCStats` returns without releasing the allocated copy buffer if `rxi_FindPeer` fails. It also does not visibly release a peer reference after a successful `rxi_FindPeer`; whether that is correct depends on `rxi_FindPeer`'s refcount contract from earlier in the file.
- `currentFunc` from the low 32 bits of `op` is not bounds-checked in the copy helpers before indexing `rpc_stat->stats[currentFunc]`. In contrast, update path `rxi_AddRpcStat` explicitly rejects out-of-range `currentFunc`. A malformed copy request for a valid interface could read past the allocated stats array.
- Retrieval allocates `rxi_rpc_*_stat_cnt * sizeof(rx_function_entry_v1_t)` bytes but marshals `rx_function_entry_v1_t` as 28 `afs_uint32` words per function, not necessarily the in-memory struct size on every ABI. The type definition and comment warn that version/format changes require care; any padding or layout change must preserve the allocation-versus-marshaled-word contract.
- `rx_RetrieveProcessRPCStats` and `rx_RetrievePeerRPCStats` set `*allocSize = space` before confirming allocation success. On `ENOMEM`, callers should rely on the returned code and null `*stats`, not on `allocSize` alone.
- `rx_disablePeerRPCStats` skips peers whose lock cannot be acquired with `MUTEX_TRYENTER`, so disabling peer stats may leave old per-peer stat structures allocated until peer destruction, shutdown cleanup, or a later disable pass that can acquire the lock.
- `rx_disablePeerRPCStats` mutates monitor/global flags outside `rx_rpc_stats`, unlike query, enable, and process disable. Concurrent recorders may observe transitional state inconsistently, especially because generated stubs gate on `rx_enable_stats` before entering this code's locked update path.
- The peer-disable loop temporarily removes peers from the hash chain while freeing stats, then does not reinsert them in the visible block. That may be intentional because this code is trying to isolate peers during cleanup, but it is a high-risk area: peer hash traversal, refcount bumps, and stat freeing are interleaved under multiple locks.
- Clear functions reset min clocks to `9999999`, matching allocation initialization. Tests and reporting tools must treat that sentinel as "no sample yet" after a clear.
- `rxi_NetSend` returns a positive shutdown errno (`ESHUTDOWN`/`WSAESHUTDOWN`) without calling `osi_NetSend` after RX shutdown, while other send errors may be platform-specific positive or negative codes. Callers such as `rx_packet.c` treat any nonzero return as failure, but tests should not assume a single sign convention for all errors.
- `NetSend_retry` drains all pending socket errors after each failed send attempt. This can consume asynchronous errors caused by other peers or threads, which is acknowledged by the comment; the recovery model relies on RX packet retransmission tolerating occasional dropped sends.
- `rx_DumpCalls` locks each call while formatting fields but traverses `rx_allCallsp` without an obvious global list lock in this chunk. It is debug-only, but concurrent call teardown could be a concern depending on surrounding debug build invariants.

## Test Signals

- Enabling process stats should make `rx_queryProcessRPCStats` nonzero and set exported `rx_enable_stats`; disabling process stats should clear process monitoring, free `processStats`, decrement `rxi_rpc_process_stat_cnt` to zero, and clear `rx_enable_stats` only when peer stats are also disabled.
- Enabling peer stats should make `rx_queryPeerRPCStats` nonzero and cause `rxi_IncrementTimeAndCount` to create entries in both a peer's `rpcStats` queue and the global `peerStats` queue.
- A recorded call should increment exactly one function entry's invocation count, add sent/received bytes, update queue and execution sums/squares, and adjust min/max clocks from the sentinel values.
- Mismatched `totalFunc` for an existing interface id/direction should not corrupt or resize the existing stats array; out-of-range `currentFunc` should be rejected by the recorder.
- Retrieval with stats disabled should return success with `statCount == 0`, `allocSize == 0`, and `stats == NULL`. Retrieval with stats enabled and records present should return `myVersion == RX_STATS_RETRIEVAL_VERSION`, a current clock stamp, and a `statCount` equal to the function-entry counter.
- Marshaling tests should verify field order and 64-bit high/low splitting for invocations, bytes sent, and bytes received, plus `sec/usec` pairs for every queue and execution clock aggregate.
- `rx_FreeRPCStats` should be paired with successful retrieve allocations, and `rx_ReleaseRPCStats` should be paired with successful single-operation copy blobs.
- Clear-flag tests should cover individual bits and `AFS_RX_STATS_CLEAR_ALL`, confirming that counters/sums zero, max fields zero, and min fields reset to `9999999`.
- Rxstat service tests should verify authorization: with no `rx_SetRxStatUserOk` callback or a callback returning false, enable/disable/clear RPCs return `EPERM`; retrieve/query/version paths remain callable.
- Peer-disable tests should include peers whose locks are held so the `MUTEX_TRYENTER` skip path is exercised, then verify whether skipped stat objects remain reachable or are cleaned by a later pass.
- `rxi_NetSend` tests should cover running versus shutdown states, direct `osi_NetSend` behavior without `AFS_RXERRQ_ENV`, retry behavior with a failing first send and drained socket errors, and eventual propagation of the last nonzero send error after retry exhaustion.
- `rxi_GetLocalAddr` should return `rx_host:rx_port` when RX was initialized with a bind host and `127.0.0.1:rx_port` when `rx_host == 0`.
