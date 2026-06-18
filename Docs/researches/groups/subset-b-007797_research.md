# subset-b-007797 Research

Grouped research for the assigned OpenAFS RX packet, peer, pthread, user-space socket, statistics, tracing, and sample/test build files. Each section preserves its original source path and is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/rx/rx_packet.c -->
# sources/distributed-fs/openafs/src/rx/rx_packet.c

## Purpose
Implements the RX packet object lifecycle and packet wire I/O path. It owns packet and continuation-buffer allocation, free-list management, jumbo datagram splitting/assembly support, slow packet data access across iovecs, UDP receive/send wrappers, debug/version packet responses, raw aborts, special packets, header encode/decode, send-packet preparation through security classes, MTU/datagram sizing helpers, and optional packet dump support.

## Important APIs, Types, And Functions
The file revolves around `struct rx_packet` from `rx_packet.h`, `struct rx_mallocedPacket` for tracking allocation blocks, `rx_freePacketQueue`, `rx_mallocedPacketQueue`, `rx_nPackets`, `rx_nFreePackets`, and optional thread-specific free packet queues under `RX_ENABLE_TSFPQ`. Public/internal entry points include `rx_SlowGetInt32`, `rx_SlowPutInt32`, `rx_SlowReadPacket`, `rx_SlowWritePacket`, `rxi_AllocPackets`, `rxi_FreePackets`, `rxi_AllocDataBuf`, `rxi_MorePackets`, `rxi_MorePacketsTSFPQ`, `rxi_FlushLocalPacketsTSFPQ`, `rxi_FreeAllPackets`, `rx_CheckPackets`, `rxi_RestoreDataBufs`, `rxi_TrimDataBufs`, `rxi_FreePacket`, `rxi_AllocPacket`, `rxi_AllocSendPacket`, `rxi_ReadPacket`, `osi_NetSend`, `rxi_ReceiveDebugPacket`, `rxi_ReceiveVersionPacket`, `rxi_SendPacket`, `rxi_SendPacketList`, `rxi_SendRawAbort`, `rxi_SendSpecial`, `rxi_EncodePacketHeader`, `rxi_DecodePacketHeader`, `rxi_PrepareSendPacket`, `rxi_AdjustIfMTU`, `rxi_AdjustMaxMTU`, `rxi_AdjustDgramPackets`, and `rx_DumpPackets`.

## Control Flow
Allocation starts with `rxi_AllocPacket`/`rxi_AllocPackets`, which draw from either the global free packet queue or a per-thread queue. If user-space queues are empty, `rxi_MorePacketsNoLock` allocates a larger block, initializes iovecs, registers the block for later cleanup, and appends packets to the free pool. Continuation buffers are just additional `rx_packet` objects whose `localdata` areas are attached to another packet's `wirevec`; `rxi_AllocDataBuf` computes how many are needed and appends them up to `RX_MAXWVECS`. Freeing reverses that mapping with `RX_CBUF_TO_PACKET`, returns continuation buffers and the primary packet to the appropriate pool, and wakes packet waiters.

The receive path prepares enough iovec space for `rx_maxJumboRecvSize`, temporarily extends the last iovec by `RX_EXTRABUFFERSIZE`, calls `rxi_Recvmsg`, validates packet length, decodes the RX header, records sender host/port, updates stats, optionally trims unused buffers, and returns a boolean success indicator. Jumbo packets are split by `rxi_SplitJumboPacket`, which treats continuation buffers as follow-on packet objects and reconstructs abbreviated jumbo headers. The send path stamps connection-local serial numbers, updates last large-packet/ping measurements, optionally invokes debug drop hooks, encodes headers, selects client or service socket, calls `rxi_NetSend`, marks packets for resend on failure, updates peer byte counters, and handles jumbograms in `rxi_SendPacketList` by building a compound iovec with abbreviated jumbo headers between packet payloads.

## State And Persistence
State is in memory only. Persistent-looking state is held in global packet pools, allocation-block tracking, counters, debug packet lists, thread-local free-packet data, and per-packet fields such as `length`, `niovecs`, `firstSerial`, `firstSent`, `timeSent`, and header fields. The code also mutates connection serial and large-packet fields, peer byte counters, call wait flags, RX statistics, and packet queue membership flags. `rxi_FreeAllPackets` frees registered allocation blocks but assumes higher-level shutdown has stopped concurrent packet users.

## Dependencies And Integration Points
This is a central RX integration file. It depends on `rx.h`, `rx_packet.h`, `rx_globals.h`, `rx_internal.h`, `rx_stats.h`, `rx_peer.h`, `rx_conn.h`, `rx_call.h`, `rx_clock.h`, `opr_queue`, platform kernel/user socket APIs, and security-class callbacks `RXS_PreparePacket`, `RXS_CheckPacket`, and `RXS_GetStats`. It is called by receive listeners, call read/write code, ack/data transmit logic, debug utilities, kernel network adapters, and Windows socket shims.

## Risks And Test Signals
The main risks are queue corruption, incorrect continuation-buffer ownership, iovec length mismatches, packet leaks under `RX_ENABLE_TSFPQ`, races around best-effort `rxi_NeedMorePackets`, packet-size truncation in jumbo paths, and security trailer/header sizing mistakes. Debug paths intentionally read some simple values without locks and should not be treated as exact. Good signals include packet pool stress tests, send/receive of max-size and jumbo datagrams, RXDEBUG intentional drop behavior, RX stats increments, security-class prepare/check failures causing connection aborts, Windows and Unix socket send/recv compatibility, and leak dumps under `RXDEBUG_PACKET`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/rx/rx_packet.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/rx/rx_packet.h -->
# sources/distributed-fs/openafs/src/rx/rx_packet.h

## Purpose
Defines the RX packet wire format, packet buffer sizing constants, packet type/flag constants, `struct rx_header`, jumbo-header metadata, `struct rx_packet`, and packet data access macros used throughout RX.

## Important APIs, Types, And Functions
Important constants include `RX_HEADER_SIZE`, `RX_MIN_PACKET_SIZE`, `RX_MAX_PACKET_SIZE`, `RX_MAX_PACKET_DATA_SIZE`, `RX_PACKET_TYPE_*`, `RX_CLIENT_INITIATED`, `RX_REQUEST_ACK`, `RX_LAST_PACKET`, `RX_MORE_PACKETS`, `RX_SLOW_START_OK`, `RX_JUMBO_PACKET`, `RX_PKTFLAG_*`, `RX_JUMBOBUFFERSIZE`, `RX_JUMBOHEADERSIZE`, `RX_FIRSTBUFFERSIZE`, `RX_CBUFFERSIZE`, and `RX_EXTRABUFFERSIZE`. `struct rx_packet` embeds queue linkage, timing, header, iovec array, local header/data/extradata buffers, length/flags, and optional debug identity. Macros include `RX_CBUF_TO_PACKET`, `rx_DataOf`, `rx_GetDataSize`, `rx_SetDataSize`, checksum accessors, `rx_GetInt32`, `rx_PutInt32`, `rx_packetwrite`, `rx_packetread`, `rx_computelen`, and `rx_Contiguous`.

## Control Flow
This header does not execute by itself; it defines invariants that `rx_packet.c`, `rx_rdwr.c`, and security code rely on. The first iovec is always the RX header, the second is the first data buffer, and later iovecs point at continuation packet buffers. Fast macros operate when data lies in `wirevec[1]`; otherwise they call slow functions that walk iovec entries.

## State And Persistence
The packet structure is the state carrier for all in-flight RX datagrams. It stores host-order header fields, wire buffers, data length, local packet flags, send timing, retransmission serials, and debug metadata. There is no disk persistence.

## Dependencies And Integration Points
The header includes platform iovec definitions or the Windows shim and relies on `RX_MAXWVECS` from configuration. It is included by packet allocation, call read/write, connection, security, listener, and platform networking code. NT, jumbo datagram, and Linux paths rely on `wirehead`, `localdata`, and `extradata` being physically adjacent.

## Risks And Test Signals
Changing sizes or structure layout can break wire compatibility, security padding, Windows sendmsg/recvmsg assumptions, jumbo split logic, and kernel network paths. Test signals include compile coverage across Unix/Windows/kernel variants, max MTU/jumbo interoperability, packet checksum/security tests, and sanitizer or debug checks for out-of-bounds iovec access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/rx/rx_packet.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/rx/rx_peer.c -->
# sources/distributed-fs/openafs/src/rx/rx_peer.c

## Purpose
Provides small accessor wrappers for `struct rx_peer` host and port fields.

## Important APIs, Types, And Functions
`rx_HostOf(struct rx_peer *peer)` returns `peer->host`; `rx_PortOf(struct rx_peer *peer)` returns `peer->port`. Both values are stored in network byte order.

## Control Flow
There is no branching or lifecycle logic. Callers pass an initialized peer pointer and receive the stored host or UDP port.

## State And Persistence
The file owns no state. It reads fields from peer objects owned by RX peer hash-table management elsewhere.

## Dependencies And Integration Points
It includes `rx.h`, `rx_atomic.h`, `rx_clock.h`, and `rx_peer.h`, giving external code stable functions instead of direct structure access. These functions integrate with consumers that need peer addressing without including private peer internals.

## Risks And Test Signals
The only meaningful risks are null pointers and byte-order misunderstandings by callers. Build/link coverage and debug output showing expected peer addresses are sufficient signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/rx/rx_peer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/rx/rx_peer.h -->
# sources/distributed-fs/openafs/src/rx/rx_peer.h

## Purpose
Defines `struct rx_peer`, the RX representation of a remote process identified by `(host, port)`.

## Important APIs, Types, And Functions
Key fields are hash/free-list `next`, optional `peer_lock`, network-order `host` and `port`, interface and negotiated MTU fields (`ifMTU`, `natMTU`, `maxMTU`, `MTU`, `maxDgramPackets`, `ifDgramPackets`, `nDgramPackets`), lifetime fields (`idleWhen`, `refCount`), RTT/congestion counters (`rtt`, `rtt_dev`, `nSent`, `reSends`, `cwind`, `congestSeq`), byte counters, RPC stats queue, reachability time, max acknowledged packet size, and optional Linux error-queue state.

## Control Flow
The header has no executable flow. Peer objects are initialized by peer lookup code and `rxi_InitPeerParams`, then updated by transmit, receive, RTT, congestion, debug, and network-error paths.

## State And Persistence
Peer state persists in memory for as long as the peer remains referenced or cached. It records transport tuning and statistics across calls to the same remote `(host, port)`, but no state is persisted to disk.

## Dependencies And Integration Points
It depends on RX primitive types, optional lock types, atomics, and `opr_queue`. `rx_packet.c` reads peer MTU and updates `bytesSent`; `rx_user.c` initializes peer network parameters; debug packet handling exports much of the structure through `rx_debugPeer`.

## Risks And Test Signals
Risks include lock discipline around `peer_lock` versus `rx_peerHashTable_lock`, stale MTU/congestion values affecting new calls, and byte-order mistakes for `host` and `port`. Useful signals are peer debug output, RTT/congestion behavior under loss, path-MTU adaptation, and network error reporting tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/rx/rx_peer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/rx/rx_prototypes.h -->
# sources/distributed-fs/openafs/src/rx/rx_prototypes.h

## Purpose
Centralizes RX internal and public prototypes across core RX, clock, connection cache, event, address, globals, kernel adapters, thread support, misc, multi-call, null security, packet, read/write, stats, user-space socket, and external OSI helper modules.

## Important APIs, Types, And Functions
The header declares lifecycle APIs (`rx_Init`, `rx_InitHost`, `rx_StartServer`, `rx_Finalize`, `shutdown_rx`), connection/call APIs, service creation, stats/debug APIs, RPC stats controls, event functions, address discovery, window configuration, kernel socket hooks, LWP/pthread primitives, packet functions from `rx_packet.c`, stream functions from `rx_rdwr.c`, stats allocation/free, user-space UDP helpers, MTU controls, and selected external AFS OSI functions. It also declares debug hooks `rx_justReceived` and `rx_almostSent`.

## Control Flow
This file has no runtime flow, but it documents module call boundaries. RX initialization sets up sockets, thread/event support, packet pools, services, and listeners; listeners feed packets to receive code; call processing uses the read/write APIs; packet APIs implement transport I/O; stats/debug APIs introspect those paths.

## State And Persistence
The header declares state surfaces but stores none. It exposes globals such as event counters, socket hooks, interface mutexes, and debug callback pointers, all of which are owned by implementation files.

## Dependencies And Integration Points
This is a high-fanout compatibility header for RX. It bridges user/kernel builds, platform variants, generated RX stubs, security classes, multi-call clients, and debug tools. Because many modules include it instead of narrower headers, declaration drift can have large build impact.

## Risks And Test Signals
Risks are stale prototypes, duplicate declarations under conditional compilation, mismatches between pthread/LWP/kernel signatures, and accidental exposure of private internals. Full matrix builds across pthread, LWP, Unix, Windows, and kernel configurations are the main test signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/rx/rx_prototypes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/rx/rx_pthread.c -->
# sources/distributed-fs/openafs/src/rx/rx_pthread.c

## Purpose
Implements pthread-based RX thread support: listener threads, server-thread startup, event scheduling thread, `recvmsg`/`sendmsg` wrappers, per-thread RX identifiers, and listener/server role handoff for hot threads.

## Important APIs, Types, And Functions
Key functions include `rx_NewThreadId`, `rxi_Delay`, `rxi_InitializeThreadSupport`, `rxi_StartServerProc`, `rxi_ReScheduleEvents`, `rxi_Listen`, `rxi_StartListener`, `rx_ServerProc`, `rxi_Recvmsg`, `rxi_Sendmsg`, `rx_GetThreadNum`, and `rx_SetThreadNum`. Important local functions are `event_handler`, `server_entry`, `rxi_ListenerProc`, `rx_ListenerProc`, and `rxi_SetThreadNum`. State includes `event_handler_thread`, `rx_event_handler_cond`, `event_handler_mutex`, `rx_listener_cond`, `listener_mutex`, `listeners_started`, `rxi_clockNow`, `threadHiNum`, and `rx_pthread_event_rescheduled`.

## Control Flow
`rxi_Listen` creates a detached listener thread per socket. Listeners block on `rx_listener_cond` until `rxi_StartListener` starts the detached event handler and broadcasts startup. Listener loops allocate/reuse receive packets, call `rxi_ReadPacket`, timestamp successful reads, and pass packets to `rxi_ReceivePacket`. With hot threads, a listener can return with `newcallp` set and become a server thread. `rx_ServerProc` reserves packets/quota, assigns a unique thread ID, calls the core `rxi_ServerProc`, then can become a listener when handed a socket. The event handler repeatedly raises due events and sleeps until the next deadline or `rxi_ReScheduleEvents` signals an earlier event.

## State And Persistence
State is process-local thread and synchronization state. Thread IDs are stored in pthread-specific data using `rx_thread_id_key`. There is no disk persistence. Listener startup is intentionally one-way; comments note `listeners_started` is not reset unless listener termination is implemented.

## Dependencies And Integration Points
This file is compiled under `AFS_PTHREAD_ENV` and depends on `rx_globals.h`, `rx_pthread.h`, `rx_clock.h`, `rx_atomic.h`, `rx_internal.h`, packet receive functions, event functions, and platform `recvmsg`/`sendmsg` or Windows shim functions. It is the pthread implementation behind prototypes shared with LWP and kernel code.

## Risks And Test Signals
Risks include detached-thread creation failures causing panic, listener startup races, hot-thread role handoff mistakes, event reschedule timing bugs, ignored stack-size parameter, and platform-specific send error normalization. Test signals include pthread RX server/client smoke tests, timer/event latency, simultaneous listeners, packet receive under load, send failures returning negative errno values, and thread ID uniqueness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/rx/rx_pthread.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/rx/rx_pthread.h -->
# sources/distributed-fs/openafs/src/rx/rx_pthread.h

## Purpose
Defines pthread-backed lock and condition-variable primitives for thread-safe user-mode RX builds.

## Important APIs, Types, And Functions
The header enables `RX_ENABLE_LOCKS`, includes `pthread_nosigs.h`, `opr.h`, and `opr/lock.h`, typedefs `afs_kmutex_t` and `afs_kcondvar_t` to pthread types, maps `pthread_yield` to platform equivalents, and defines `MUTEX_*`/`CV_*` macros onto OPR lock wrappers.

## Control Flow
There is no runtime flow in the header. Implementation files use the macros to initialize, enter, exit, wait, signal, and broadcast synchronization primitives.

## State And Persistence
No state is stored. The types it defines are embedded in RX globals, peers, calls, and server queue entries.

## Dependencies And Integration Points
This is included by pthread RX user-mode code and any header needing RX lock types. On Windows it includes WinSock/WinBase and pthread headers; on Unix it includes pthreads and platform yield alternatives.

## Risks And Test Signals
Risks are macro compatibility across platforms and assumptions that `opr_*` wrappers match pthread semantics. Build coverage on Windows, Solaris, AIX, and common Unix pthread builds plus condition-variable stress tests are useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/rx/rx_pthread.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/rx/rx_queue.h -->
# sources/distributed-fs/openafs/src/rx/rx_queue.h

## Purpose
Provides the legacy RX intrusive doubly linked queue macro package.

## Important APIs, Types, And Functions
The header defines `struct rx_queue`, internal macros `_RXQ`, `_RXQA`, `_RXQS`, `_RXQSP`, `_RXQMV`, `_RXQR`, and public macros `queue_Init`, `queue_NodeInit`, `queue_Prepend`, `queue_Append`, insertion, splice, split, replace, move, remove, first/last/next/prev, empty/on-queue/end checks, forward/backward scans, and `queue_Count`.

## Control Flow
All operations are macro-expanded pointer rewrites on intrusive `prev`/`next` links. Scan macros generate `for` loop clauses and require caller-provided current/next variables so removing the current item is safe.

## State And Persistence
Queue state is embedded in caller-owned structs. A queue head points to itself when empty; removed nodes have `next` cleared by `queue_Remove`. There is no persistence beyond memory.

## Dependencies And Integration Points
This header predates the newer `opr_queue` used by many current RX files. It remains included by older RX code and test makefiles. Its API assumes the queue link can be coerced to the containing structure pointer, so layout discipline is critical.

## Risks And Test Signals
Risks include side effects in macro arguments, type confusion from casts, the apparent `queue_IsFirst` use of a nonexistent `first` member, double removal, and misuse with structures where the queue link is not at the expected offset. Compile coverage and focused queue-manipulation unit tests are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/rx/rx_queue.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/rx/rx_rdwr.c -->
# sources/distributed-fs/openafs/src/rx/rx_rdwr.c

## Purpose
Implements RX call stream read/write APIs over packet queues. It translates application byte streams and iovecs into ordered RX data packets, handles receive queue consumption and hard ACK scheduling, manages transmit-window waits, and flushes final packets.

## Important APIs, Types, And Functions
Important functions are `rxi_GetNextPacket`, `rxi_ReadProc`, `rx_ReadProc`, `rx_ReadProc32`, `rxi_FillReadVec`, `rxi_ReadvProc`, `rx_ReadvProc`, `rxi_WriteProc`, `rx_WriteProc`, `rx_WriteProc32`, `rx_WritevAlloc`, `rxi_WritevProc`, `rx_WritevProc`, `rxi_FlushWrite`, `rxi_FlushWriteLocked`, and `rx_FlushWrite`. The file manipulates `struct rx_call` fields including `rq`, `tq`, `app.currentPacket`, `app.curvec`, `app.curpos`, `app.curlen`, `app.nLeft`, `app.nFree`, `app.mode`, `app.iovq`, `rnext`, `tnext`, `tfirst`, `twind`, `nHardAcks`, `flags`, and call condition variables.

## Control Flow
Reads first free any previously loaned iovec packets. If no current packet has data, `rxi_GetNextPacket` removes the next in-sequence packet from `rq`, checks it with the connection security class, advances `rnext`, initializes application cursor fields, and increments hard ACK accounting. Scalar reads copy bytes to caller buffers and free packets as they are exhausted. Vector reads fill caller iovecs with direct pointers into packet buffers, move exhausted packets into `app.iovq` so they stay alive until the next read/write call, and wait on `cv_rq` when more data is needed.

Writes switch server calls from receive to send mode when legal, allocate send packets sized by MTU and security overhead, copy bytes into packet iovecs, extend packets with continuation buffers when useful, prepare full packets with `rxi_PrepareSendPacket`, append them to the transmit queue, and start transmission unless fast recovery is active. Vector writes split into allocation (`rx_WritevAlloc`, which gives the application direct packet-buffer iovecs) and commit (`rx_WritevProc`, which validates the returned iovecs, adjusts cursors, queues full packets, and handles protocol errors). Flush sends a final packet, possibly zero-length, marks it with `RX_LAST_PACKET`, and transitions clients to receiving or servers to EOF.

## State And Persistence
All state is in-memory per call. The file persists stream position across API calls through `call->app` fields and holds packet buffers in `currentPacket`, `rq`, `tq`, and `iovq`. It also updates per-call byte counters, hard ACK counters, wait timestamps, mode flags, and error state.

## Dependencies And Integration Points
It depends on packet allocation/freeing, security-class packet checks/preparation, ACK scheduling, retransmit start logic, call locks/CVs, RX clock, and connection state. It is used by generated RX stubs and application code through `rx_ReadProc*`, `rx_WriteProc*`, vector APIs, and flush.

## Risks And Test Signals
Risks include deadlocks around call lock drops in `rxi_PrepareSendPacket`, packet lifetime bugs with `iovq`, off-by-one iovec cursor logic, returning 0 on errors without preserving partial-byte semantics, transmit-window wait starvation, and protocol errors when applications alter allocated iovecs. Test signals include scalar and vector RPCs, zero-length responses, fragmented large replies, security check failures, lost packet/retransmit recovery, hard ACK scheduling, and concurrent client/server mode transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/rx/rx_rdwr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/rx/rx_server.h -->
# sources/distributed-fs/openafs/src/rx/rx_server.h

## Purpose
Defines the server idle-queue entry used by RX server threads waiting for calls or listener duties.

## Important APIs, Types, And Functions
`struct rx_serverQueueEntry` contains an `opr_queue` entry, `newcall`, optional lock and condition variable, thread number `tno`, and `socketp` pointer. The comments define the handoff contract between listener and server roles.

## Control Flow
Server threads enqueue this structure when idle. When a call arrives, RX fills `newcall` and wakes the thread. If `socketp` is non-null, the sleeping server is willing to become a listener; it sleeps with `*socketp == -1` and wakes with a real socket when selected as listener.

## State And Persistence
State is transient per idle server thread. It records the call/socket assignment and synchronization primitive used for wakeup.

## Dependencies And Integration Points
The structure integrates `rx.c` server scheduling with pthread/LWP listener code and `rx_idleServerQueue`. It relies on `struct rx_call`, `opr_queue`, lock types, and `osi_socket`.

## Risks And Test Signals
Risks are missed wakeups, stale `socketp` values, and inconsistent lock use around queue entries. Server pool tests, hot-thread listener handoff, and high-concurrency incoming call tests are useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/rx/rx_server.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/rx/rx_stats.c -->
# sources/distributed-fs/openafs/src/rx/rx_stats.c

## Purpose
Implements allocation, copying, freeing, and reset of RX internal statistics.

## Important APIs, Types, And Functions
The file defines `rx_stats_mutex` when locks are enabled and global `struct rx_statisticsAtomic rx_stats`. Functions are `rx_GetStatistics`, `rx_FreeStatistics`, and private `rxi_ResetStatistics`.

## Control Flow
`rx_GetStatistics` allocates an external `struct rx_statistics`, locks `rx_stats_mutex`, asserts layout compatibility between atomic and external structures, copies the global stats block, unlocks, and returns it. `rx_FreeStatistics` frees a non-null stats block and clears the caller pointer. `rxi_ResetStatistics` zeroes the atomic stats structure.

## State And Persistence
Statistics are process/kernel memory counters only. No disk persistence exists. Atomic fields can be incremented without holding the stats mutex, while non-atomic fields are protected by `rx_stats_mutex` for snapshot copying.

## Dependencies And Integration Points
It depends on `rx_atomic.h`, `rx_stats.h`, RX allocation helpers `rxi_Alloc`/`rxi_Free`, and the public `struct rx_statistics` layout from RX headers. Packet, connection, and socket paths update `rx_stats`.

## Risks And Test Signals
Risks include layout drift between `rx_statisticsAtomic` and `rx_statistics`, missing locking for non-atomic members, and reset races during active traffic. Test signals are stats API calls under traffic, reset behavior, and compile-time/static assertion failures on layout changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/rx/rx_stats.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/rx/rx_stats.h -->
# sources/distributed-fs/openafs/src/rx/rx_stats.h

## Purpose
Defines RX's internal atomic statistics structure and declares the stats globals.

## Important APIs, Types, And Functions
`struct rx_statisticsAtomic` mirrors public `struct rx_statistics` using `rx_atomic_t` for counters such as packet requests, allocation failures, socket buffer success, bogus reads, packet reads/sends by type, RTT samples, connection/peer/call counts, send failures, fatal errors, and spare counters. It declares `rx_stats_mutex`, `rx_stats`, and `rxi_ResetStatistics`.

## Control Flow
No runtime flow is present. Producers update fields directly, usually through atomic helpers; `rx_stats.c` snapshots and resets the whole structure.

## State And Persistence
The structure defines in-memory telemetry for an RX process or kernel instance. It is not persisted.

## Dependencies And Integration Points
It depends on `rx_atomic_t`, `struct clock`, and `RX_N_PACKET_TYPES`. Its layout must remain synchronized with public stats structures consumed by debug/stat APIs.

## Risks And Test Signals
Risks are ABI/layout mismatch, assuming `sizeof(rx_atomic_t) == sizeof(int)`, and inconsistent atomic versus mutex-protected access. Static assertions, stats debug queries, and counter monotonicity under load are key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/rx/rx_stats.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/rx/rx_stubs.c -->
# sources/distributed-fs/openafs/src/rx/rx_stubs.c

## Purpose
Provides fallback exported RX routines when optional RXGK support is not compiled.

## Important APIs, Types, And Functions
When `ENABLE_RXGK` is not defined, the file implements `rxgk_GetServerInfo(struct rx_connection *conn, RXGK_Level *level, struct afs_time64 *expiry, struct rx_identity **identity)` and returns `EINVAL`.

## Control Flow
There is a single stub path: any caller asking for RXGK server information in a non-RXGK build receives an invalid-argument error.

## State And Persistence
No state is read or written.

## Dependencies And Integration Points
It includes RX, RXGK, and identity headers so libraries can export a consistent symbol even when `src/rxgk` is excluded. This supports link compatibility for `libafsrpc` consumers.

## Risks And Test Signals
Risks are callers treating the stub as partially functional or failing to handle `EINVAL`. Link tests for non-RXGK builds and runtime checks that RXGK-dependent features report unsupported status are the useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/rx/rx_stubs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/rx/rx_trace.c -->
# sources/distributed-fs/openafs/src/rx/rx_trace.c

## Purpose
Implements optional RX call tracing under `RXDEBUG` and a `DUMPTRACE` reader utility.

## Important APIs, Types, And Functions
When tracing is disabled, it defines `rxi_tracename` as a diagnostic string and optional no-op `main`. Under `RXDEBUG`, it defines `rxi_tracename`, `rxi_logfd`, `rxi_tracebuf`, `rxi_tracepos`, private `struct rx_trace`, `rxi_flushtrace`, `rxi_calltrace`, and optionally a dump utility `main`.

## Control Flow
`rxi_calltrace` returns immediately when tracing is disabled by a leading NUL in `rxi_tracename`. Otherwise it lazily opens the trace file, timestamps the event, records connection ID, call number, queue length, service/wait timings depending on event type, appends the binary record to a 4096-byte buffer, and flushes when nearly full. `rxi_flushtrace` writes buffered bytes and resets the position. `DUMPTRACE` reads records and prints human-readable event lines.

## State And Persistence
Runtime state includes the trace file path, file descriptor, buffer, buffer offset, and per-call `traceStart`/`traceWait` fields. When enabled, trace records persist to the configured file path.

## Dependencies And Integration Points
The file depends on RX debug configuration, `rx_globals.h`, `rx_internal.h`, `rx_trace.h`, `rx_conn.h`, `rx_call.h`, and clock/atomic helpers. Server scheduling and call lifecycle code call `rxi_calltrace` through macros declared in `rx_trace.h`.

## Risks And Test Signals
Risks include binary trace format portability, permissive trace file mode, unsynchronized global buffer access in multi-threaded debug builds, silent write errors, and stale path activation semantics. Test signals include enabling trace with `RXTRACEON` or patched pathname, call arrival/start/end/drop records, flush behavior, and `DUMPTRACE` output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/rx/rx_trace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/rx/rx_trace.h -->
# sources/distributed-fs/openafs/src/rx/rx_trace.h

## Purpose
Declares or disables RX call tracing hooks depending on `RXDEBUG`.

## Important APIs, Types, And Functions
Without `RXDEBUG`, `rxi_calltrace(a,b)` and `rxi_flushtrace()` expand to no-ops. With `RXDEBUG`, the header declares both functions and defines event IDs `RX_CALL_ARRIVAL`, `RX_CALL_START`, `RX_CALL_END`, and `RX_TRACE_DROP`.

## Control Flow
The header controls compile-time behavior: production builds compile tracing calls away, while debug builds route them to `rx_trace.c`.

## State And Persistence
No state is stored in the header. Debug builds rely on `rx_trace.c` globals and per-call trace timing fields.

## Dependencies And Integration Points
It forward-uses `struct rx_call` and is included by RX lifecycle code that wants low-cost tracing hooks.

## Risks And Test Signals
Risks are event ID drift and assuming trace side effects in non-debug builds. Compile coverage with and without `RXDEBUG` is the main signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/rx/rx_trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/rx/rx_user.c -->
# sources/distributed-fs/openafs/src/rx/rx_user.c

## Purpose
Implements user-space RX platform support: UDP socket creation, diagnostic/panic helpers, interface address/MTU discovery, local address enumeration, peer network parameter initialization, jumbo/MTU configuration, and optional Linux extended socket-error processing.

## Important APIs, Types, And Functions
Key functions are `rxi_GetHostUDPSocket`, `rxi_GetUDPSocket`, `osi_Msg`, `osi_Panic`, `osi_AssertFailU`, optional AIX `osi_Alloc`/`osi_Free`, Windows `rxi_getaddr`, `rx_getAllAddr`, `rx_getAllAddrMaskMtu`, `rx_GetIFInfo`, `rxi_InitMorePackets`, Unix `rxi_syscall`, `fudge_netmask`, `rxi_InitPeerParams`, `rx_SetNoJumbo`, `rx_SetMaxMTU`, and Linux `osi_HandleSocketError`. State includes interface arrays `rxi_NetAddrs`, `myNetMTUs`, `myNetMasks`, `myNetFlags`, `rxi_numNetAddrs`, and `Inited`, with pthread mutexes for interface initialization and data.

## Control Flow
`rxi_GetHostUDPSocket` validates reserved-port permissions, creates a UDP socket, initializes Windows transmit extensions when applicable, binds the requested host/port, sets close-on-exec, tries to enlarge send/receive buffers, configures Linux path-MTU/error-queue options, starts a listener with `rxi_Listen`, and returns the socket or closes it on error. `rx_GetIFInfo` lazily discovers interfaces: Windows delegates to `syscfg_GetIFInfo`; Unix uses `SIOCGIFCONF`, filters loopback/duplicates, reads flags, MTU, and netmask from syscalls/ioctls/fallback classful masks, updates maximum receive sizing, and preallocates continuation packet capacity for jumbo receives. `rxi_InitPeerParams` ensures interface discovery, matches peer address to local networks, sets timeout hints, computes interface/natural/max MTUs and datagram counts, optionally clamps with path MTU, and initializes slow-start fields.

## State And Persistence
State is in process memory: socket descriptors, interface caches, MTU globals, packet pool sizing, and peer transport parameters. `Inited` prevents repeated Unix interface scans; Windows can refresh addresses on each public query. No state is written to disk.

## Dependencies And Integration Points
The file depends on platform sockets/ioctls, `rx_globals.h`, `rx_stats.h`, `rx_peer.h`, `rx_packet.h`, `rx_internal.h`, packet allocation, listener startup, RX MTU helpers, and optional Linux `IP_RECVERR` handling. It is the user-mode counterpart to kernel RX network adapters.

## Risks And Test Signals
Risks include stale interface cache after address changes on Unix, incomplete bind retry behavior because the loop breaks after one bind attempt, platform-specific MTU ioctl differences, packet preallocation before RX locks are initialized, and path-MTU/error-queue portability. Test signals include binding privileged/unprivileged ports, listener startup, interface enumeration on multihomed hosts, loopback filtering, MTU clamping, jumbo disable/max MTU APIs, and Linux ICMP error processing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/rx/rx_user.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/rx/rx_user.h -->
# sources/distributed-fs/openafs/src/rx/rx_user.h

## Purpose
Defines user-mode RX platform macros and socket/allocator abstractions.

## Important APIs, Types, And Functions
The header defines no-op priority/GLOCK macros (`SPLVAR`, `NETPRI`, `USERPRI`, `AFS_GLOCK`, `AFS_GUNLOCK`, `AFS_ASSERT_GLOCK`, `ISAFS_GLOCK`), `osi_socket` and `OSI_NULLSOCKET` for UAFS, Windows, and Unix, sleep/wakeup macros, allocation/free macros, `osi_GetTime`, and `osi_Assert`.

## Control Flow
No runtime flow exists. The macros let shared RX code compile in user mode without kernel priority or global-lock operations.

## State And Persistence
No state is stored. The socket typedef determines how socket values are represented by user-mode code.

## Dependencies And Integration Points
It includes AFS parameters, standard C allocation headers, and LWP headers. `rx_packet.c`, `rx_user.c`, and user-mode transport code include it to bridge platform differences.

## Risks And Test Signals
Risks include mismatched socket type assumptions, allocator macro conflicts, and accidentally relying on no-op lock/priority macros in code later used in kernel builds. Cross-platform user-mode builds and basic socket tests are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/rx/rx_user.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/rx/rx_xmit_nt.c -->
# sources/distributed-fs/openafs/src/rx/rx_xmit_nt.c

## Purpose
Provides Windows implementations of `sendmsg` and `recvmsg` semantics for RX, using Winsock extension functions when available and copy-based fallbacks otherwise.

## Important APIs, Types, And Functions
The file defines extension function pointers `pWSARecvMsg` and `pWSASendMsg`, initializes them in `rxi_xmit_init`, and implements `recvmsg(osi_socket socket, struct msghdr *msgP, int flags)` and `sendmsg(osi_socket socket, struct msghdr *msgP, int flags)` under `AFS_NT40_ENV`.

## Control Flow
`rxi_xmit_init` fetches `WSARecvMsg` and `WSASendMsg` via `WSAIoctl`, enables UDP connection-reset notifications and circular queueing. `recvmsg` uses `WSARecvMsg` if present; otherwise it receives into a temporary packet-sized buffer with `recvfrom` and copies into caller iovecs. `sendmsg` uses `WSASendMsg` if present; otherwise it sends directly from the first iovec when there are at most two iovecs, or packs multiple iovecs into a temporary buffer before `sendto`. Winsock errors are mapped to `errno` values expected by RX.

## State And Persistence
State is limited to cached Winsock extension function pointers. No disk persistence exists.

## Dependencies And Integration Points
It depends on Windows Winsock headers, `rx.h`, `rx_globals.h`, `rx_packet.h`, and `rx_xmit_nt.h`. `rx_packet.c` and `rx_pthread.c` call `rxi_Recvmsg`/`rxi_Sendmsg`, which ultimately use these macros/functions on NT builds.

## Risks And Test Signals
Risks include strong assumptions that the first two RX iovecs are physically contiguous, fallback stack buffers capped at `RX_MAX_PACKET_SIZE`, partial-copy behavior on receive truncation, and global extension pointers initialized per socket but shared process-wide. Test signals include Windows RX client/server traffic, jumbo and multi-iovec sends, WSA extension unavailable fallback, WSAEWOULDBLOCK/ECONNRESET handling, and host-unreachable propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/rx/rx_xmit_nt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/rx/rx_xmit_nt.h -->
# sources/distributed-fs/openafs/src/rx/rx_xmit_nt.h

## Purpose
Declares the Windows RX transmit shim and remaps POSIX-style `sendmsg`/`recvmsg` names to RX wrapper names.

## Important APIs, Types, And Functions
It declares `rxi_sendmsg`, `rxi_recvmsg`, and `rxi_xmit_init`, undefines `sendmsg`, defines `sendmsg` as `rxi_sendmsg`, and defines `recvmsg` as `rxi_recvmsg`.

## Control Flow
No runtime flow exists in the header. The macro remapping ensures code written against `sendmsg`/`recvmsg` calls the Windows-compatible shim.

## State And Persistence
The header stores no state; implementation state lives in `rx_xmit_nt.c`.

## Dependencies And Integration Points
It requires `osi_socket` and `struct msghdr` definitions from surrounding includes and is included by Windows RX packet/pthread code.

## Risks And Test Signals
Risks include declaration/name mismatches with implementation and macro remapping surprises in files that include other socket headers later. Windows compile/link coverage is the main signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/rx/rx_xmit_nt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/rx/simple.example/Makefile.in -->
# sources/distributed-fs/openafs/src/rx/simple.example/Makefile.in

## Purpose
Builds the simple RX example client/server and generated RX stubs.

## Important APIs, Types, And Functions
Targets include `all`, `sample_client`, `sample_server`, generated `sample.cs.c`, `sample.ss.c`, `sample.h`, and `clean`. It includes `Makefile.config` and `Makefile.pthread`, uses `RXGEN`, links `libafsauthent.a`, `libafsrpc.a`, `util.a`, crypto/roken libraries, and `XLIBS`. Comments show an alternate LWP RX library setup.

## Control Flow
`all` builds client and server. RXGEN generates client stubs with `-C`, server stubs with `-S`, and the header with `-h` from `sample.xg`. Object dependencies ensure generated header availability. Link rules combine local objects, generated stubs, and RX/auth libraries.

## State And Persistence
Generated C/header files, object files, and binaries are build artifacts. `clean` removes objects, generated stubs, and binaries.

## Dependencies And Integration Points
This makefile integrates RXGEN-generated RPC code with the pthread RX library stack and the simple example sources. It depends on top-level OpenAFS build variables and libraries.

## Risks And Test Signals
Risks include stale generated files, wrong thread flavor if switching between pthread/LWP comments, and missing library ordering. Successful `make` in the example directory and a client/server add/subtract run are the primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/rx/simple.example/Makefile.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/rx/simple.example/sample_client.c -->
# sources/distributed-fs/openafs/src/rx/simple.example/sample_client.c

## Purpose
Demonstrates a minimal RX client that connects to the sample service and invokes generated add/subtract RPCs.

## Important APIs, Types, And Functions
The local helper `GetIpAddress` resolves a hostname with `gethostbyname`. `main` calls `rx_Init(0)`, creates a null client security object with `rxnull_NewClientSecurityObject`, opens a connection with `rx_NewConnection`, and repeatedly calls generated `TEST_Add` and `TEST_Sub`.

## Control Flow
The program expects the server hostname as `argv[1]`, resolves it, initializes RX on an ephemeral local port, creates a null-security connection to `SAMPLE_SERVER_PORT`/`SAMPLE_SERVICE_ID`, then loops from 1 to 9 printing each RPC input, result, and error code.

## State And Persistence
State is limited to the process RX runtime, one connection, and loop-local result variables. No persistence exists.

## Dependencies And Integration Points
It includes generated `sample.h`, RX runtime APIs, null security, and libc networking. It exercises the generated client stubs from `sample.xg` and the sample server.

## Risks And Test Signals
Risks include no argument validation before `argv[1]`, legacy IPv4-only `gethostbyname`, no connection destruction/finalization, and null security being unsuitable beyond a demo. Test signal is successful printed add/subtract responses against `sample_server`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/rx/simple.example/sample_client.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/rx/simple.example/sample_server.c -->
# sources/distributed-fs/openafs/src/rx/simple.example/sample_server.c

## Purpose
Demonstrates a minimal RX server that exports generated sample add/subtract RPC operations over null security.

## Important APIs, Types, And Functions
`main` initializes RX with `rx_Init(SAMPLE_SERVER_PORT)`, creates a null server security object, registers a service with `rx_NewService`, and donates the process to the server pool with `rx_StartServer(1)`. Server RPC handlers `STEST_Add` and `STEST_Sub` implement generated service operations. `Quit` prints an error and exits.

## Control Flow
Startup initializes RX on the fixed sample port, builds the one-entry security object array, creates the service using generated `TEST_ExecuteRequest`, and enters the RX server loop. Incoming RPCs dispatch through generated server stubs into `STEST_Add`/`STEST_Sub`, which compute results and return success.

## State And Persistence
State is in-memory RX service registration and security object state. No persistent storage is used.

## Dependencies And Integration Points
It depends on generated `sample.h`, RX service APIs, null security, and generated server stubs from `sample.xg`. It is paired with `sample_client.c`.

## Risks And Test Signals
Risks include null security, fixed port conflicts, minimal error reporting, and no graceful shutdown path. Test signals are service startup and correct client-visible add/subtract results.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/rx/simple.example/sample_server.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/rx/test/Makefile.in -->
# sources/distributed-fs/openafs/src/rx/test/Makefile.in

## Purpose
Builds RX test programs for LWP and selected pthread/multithreaded variants.

## Important APIs, Types, And Functions
It includes `Makefile.config` and `Makefile.lwp`, defines library paths and `LIBS`, sets `MODULE_CFLAGS=-DRXDEBUG`, lists `RXTESTOBJS`, `BASICINCLS`, link macros, LWP test binaries (`testclient`, `testserver`, `kstest`, `kctest`, `tableGen`, `generator`), pthread binaries (`th_testserver`, `th_testclient`), and `clean`.

## Control Flow
`all` builds both `test` and `th_test`. Individual LWP binaries link against local `../librx.a`, LWP, command, util, sys, OPR, crypto, roken, and platform libraries. Threaded test objects compile `testclient.c`/`testserver.c` with `MT_CC`/`MT_CFLAGS` and link against `libafsrpc.a`. Object dependencies force rebuilds when core RX headers change.

## State And Persistence
Build artifacts are object files, archives, binaries, and possible core files. `clean` removes these artifacts.

## Dependencies And Integration Points
The makefile integrates RX unit/integration test sources with the OpenAFS build system, LWP RX library, pthread RX library, and debug compilation. It references `rx_clock.h`, `rx_queue.h`, `rx_event.h`, and `rx.h` as basic dependencies.

## Risks And Test Signals
Risks include Solaris-specific comments around threaded link lines, library-order sensitivity, stale dependencies that omit newer headers, and debug-only behavior due to `RXDEBUG`. Successful `make test`, `make th_test`, and running client/server test pairs are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/rx/test/Makefile.in -->
