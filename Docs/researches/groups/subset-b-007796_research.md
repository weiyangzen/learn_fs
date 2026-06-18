# Research: subset-b-007796

Grouped research for OpenAFS RX core support files. Each section is source-tree aligned and bounded by reconciliation markers for deterministic splitting into per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/rx/rx.h -->
## sources/distributed-fs/openafs/src/rx/rx.h

### Purpose
`rx.h` is the main public and semi-public RX protocol header. It exposes connection, call, peer, service, security-class, statistics, debug, packet, acknowledgement, and RPC-operation-stat interfaces used by both user-space and kernel RX builds.

### Important APIs, Types, and Constants
- Declares accessors implemented by `rx_conn.c`, `rx_call.c`, and peer code: `rx_GetConnectionEpoch`, `rx_GetConnectionId`, `rx_SetSecurityData`, `rx_SecurityObjectOf`, `rx_ConnectionOf`, `rx_Error`, `rx_GetCallStatus`, `rx_HostOf`, and related helpers.
- Defines packet classes (`RX_PACKET_CLASS_RECEIVE`, `SEND`, `SPECIAL`, continuation buffers), packet type strings, `RX_MAXIOVECS`, and call state/mode/flag constants used by `rx.c`, `rx_rdwr.c`, debug tools, and rxdebug protocol structures.
- Defines default timing and sizing constants: `RX_IDLE_DEAD_TIME`, `RX_DEFAULT_DEAD_TIME`, `RX_MAX_SERVICES`, `RX_MAXCALLS`, `RX_CIDSHIFT`, `RX_CHANNELMASK`, `RX_MAXACKS`, challenge/check-reach timers, and RX error values.
- Defines `struct rx_service`, the installed server service descriptor containing service identity, socket, security classes, execution hooks, per-service concurrency bounds, dead/idle timing, and service-specific data.
- Defines `struct rx_ackPacket`, including buffer-space, skew, first packet, previous packet, serial, reason, and up to 255 ACK/NACK bytes.
- Defines the security API surface: `rx_securityIndex`, security type constants, `struct rx_securityObjectStats`, `rx_securityConfigVariables`, `struct rx_securityClass`, and `RXS_*` dispatch macros.
- Defines wire/debug/stat structures: `struct rx_statistics`, `struct rx_debugIn`, `struct rx_debugStats`, `struct rx_debugConn_vL`, `struct rx_debugConn`, `struct rx_debugPeer`, `rx_function_entry_v1_t`, and `rx_interface_stat_t`.
- Provides macros for common user APIs: `rx_Read`, `rx_Write`, `rx_Readv`, `rx_Writev`, `rx_MaxUserDataSize`, service setters, tranquil mode, abort throttling, and hot-thread controls.

### Control Flow and Integration
This header is not executable control flow, but it defines the contracts consumed throughout RX. `rx.c` owns most lifecycle, packet processing, and call state transitions; `rx_conn.c` and `rx_call.c` provide accessor implementations for the opaque structures; `rx_rdwr.c` consumes the read/write macros; security classes use `RXS_*` hooks during connection setup, packet preparation, challenge/response, packet checking, and destruction. Debug and statistics structures are serialized by rxdebug and RPC stats retrieval code, so field order and version constants are part of the compatibility contract.

### State and Persistence Behavior
All state described here is in-memory process or kernel state. `struct rx_service` persists for the RX process lifetime after service registration. Ack, debug, and statistics structures are transient or exported snapshots. No durable storage is managed here, but the debug/stat structures are wire-visible and therefore persistent compatibility formats.

### Dependencies and Integration Points
The header selects platform headers and thread backends (`rx_kmutex.h`, `rx_kernel.h`, `rx_pthread.h`, `rx_lwp.h`, `rx_user.h`) based on `KERNEL`, `AFS_PTHREAD_ENV`, and `AFS_NT40_ENV`. It depends on `rx_clock.h`, `rx_event.h`, `rx_misc.h`, `rx_null.h`, `rx_multi.h`, and `rx_prototypes.h`. It is an integration hub for RX security modules such as rxnull, rxkad, rxgk, and Kerberos-related classes.

### Risks and Edge Cases
- Debug/stat structures are externally consumed; changing fields, sizes, or version constants can break rxdebug and stats clients.
- `rx_MaxUserDataSize` assumes call MTU and security overhead fields are initialized and consistent.
- Ack packet sizing uses `offsetof` and variable `acks` count; off-by-one changes can corrupt wire parsing.
- Macros write directly to globals and service fields without validation in many cases.
- `rx_securityClass.refCount_data` is deliberately opaque; direct access risks ABI and synchronization bugs.

### Test Signals
Useful tests include rxdebug compatibility checks across versions, unit or integration tests for ACK encoding/decoding and max user data calculations, service registration/startup tests under each threading backend, security class hook tests, and RPC stats retrieval/marshalling tests that verify old clients tolerate current structures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/rx/rx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/rx/rx_atomic.h -->
## sources/distributed-fs/openafs/src/rx/rx_atomic.h

### Purpose
`rx_atomic.h` provides RX's small integer atomic abstraction across Windows, AIX, Darwin, Linux kernel, Solaris, GCC builtins, and a mutex-protected fallback.

### Important APIs and Types
- Defines `RX_ATOMIC_INIT(i)` and `rx_atomic_t`.
- Exposes inline operations: `rx_atomic_set`, `rx_atomic_read`, `rx_atomic_inc`, `rx_atomic_inc_and_read`, `rx_atomic_add`, `rx_atomic_add_and_read`, `rx_atomic_dec`, `rx_atomic_dec_and_read`, and `rx_atomic_sub`.
- Uses platform primitives: Windows `Interlocked*`, AIX `fetch_and_add`, Darwin `OSAtomic*` or kernel compatibility wrappers, Linux kernel `atomic_t`, Solaris `atomic_*_32`, GCC `__sync_*`, or a process-wide `rx_atomic_mutex`.

### Control Flow and State
Most implementations are direct wrappers. The fallback implementation serializes all atomic variables with one global mutex when `RX_ENABLE_LOCKS` is available. No data is persisted; values live in the caller-owned `rx_atomic_t`.

### Dependencies and Integration Points
The header depends on platform feature macros and may include `rx_kmutex.h`, `rx_pthread.h`, or `rx_lwp.h` for fallback locking. It is used by RX statistics, wait counters, event reference counts, and other shared counters.

### Risks and Edge Cases
- The fallback mutex path has much broader contention and depends on `rx_atomic_mutex` being initialized before use.
- `rx_atomic_read` and `rx_atomic_set` are plain volatile accesses on several native paths, not full memory barriers.
- Solaris stores `volatile unsigned int` while the API returns `int`; negative values or overflow semantics need care.
- Darwin OSAtomic APIs are legacy/deprecated in modern user-space, but this source targets older OpenAFS portability.

### Test Signals
Run concurrency stress tests for event cancellation/refcounting and stats counters under pthread builds. Build matrix coverage is important because most behavior is preprocessor-selected. Fallback builds should verify `rx_atomic_mutex` initialization and absence of deadlocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/rx/rx_atomic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/rx/rx_call.c -->
## sources/distributed-fs/openafs/src/rx/rx_call.c

### Purpose
`rx_call.c` implements lightweight public accessors and statistics recording for `struct rx_call`, keeping callers from directly depending on internal call layout.

### Important Functions
- `rx_ConnectionOf`, `rx_Error`, `rx_GetRemoteStatus`, `rx_GetLocalStatus`, `rx_SetLocalStatus`, `rx_GetCallAbortCode`, and `rx_SetCallAbortCode` expose simple fields.
- `rx_RecordCallStatistics` computes queue and execution durations and calls `rxi_IncrementTimeAndCount`.
- `rx_GetCallStatus` returns read sequence, transmit sequence, last send time, and last receive time for monitoring.

### Control Flow and State
The accessor functions read or write fields directly. `rx_RecordCallStatistics` takes current time, subtracts `call->startTime` to compute execution duration, subtracts `call->queueTime` from `startTime` for queue duration, and records bytes sent/received through the peer stats path. `rx_GetCallStatus` only writes non-NULL output pointers.

### Dependencies and Integration Points
Includes `rx.h`, `rx_call.h`, `rx_conn.h`, `rx_atomic.h`, and `rx_internal.h`. The statistics path integrates with `rxi_IncrementTimeAndCount` in `rx.c` and peer-level RPC stats. Monitoring tools such as VolMonitor use `rx_GetCallStatus`.

### Risks and Edge Cases
- Accessors do not lock the call. Callers must already be in a context where these fields are stable enough or accept a snapshot race.
- `rx_RecordCallStatistics` assumes `queueTime`, `startTime`, `conn`, `peer`, and application byte counters are initialized.
- Return targets in `rx_GetCallStatus` are signed while stored fields are unsigned, which can truncate large sequence values.

### Test Signals
Exercise RPC stats with known queue/execution timing and byte counts. Validate monitoring output during active calls and with NULL output pointer combinations. Race-focused tests should verify consumers tolerate snapshot values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/rx/rx_call.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/rx/rx_call.h -->
## sources/distributed-fs/openafs/src/rx/rx_call.h

### Purpose
`rx_call.h` defines the internal `struct rx_call` and application-facing per-call substructure used by RX data marshalling, packet queues, scheduling events, retransmission state, congestion control, status, and reference management.

### Important Types and Fields
- `struct rx_call_appl` holds unlocked application-thread state: iovec queue, current packet, current vector position, mode, and byte counters.
- `struct rx_call` contains queue links, transmit/receive queues, channel, state, optional locks/condition variables, parent connection, call number pointer, flags, status/error fields, receive/transmit sequence windows, congestion state, RTT/RTO values, scheduled events, abort throttling state, arrival callback, timing fields, MTU, optional refcount/debug fields, current readv/writev vectors, and xmit list.
- Reference macros `CALL_HOLD`, `CALL_RELE`, `CALL_HOLD_R`, and `CALL_RELE_R` manage refcounts under `rx_refcnt_mutex` when locks are enabled; `RX_REFCOUNT_CHECK` adds per-hold-type diagnostics.

### Control Flow and State
This header defines the state layout manipulated by `rx.c`, `rx_rdwr.c`, `rx_packet.c`, `rx_multi.c`, and event callbacks. A call transitions through states defined in `rx.h`, carries packet queues while active or dallying, and uses scheduled events for resend, keepalive, delayed ACK, delayed abort, and MTU growth. Application marshalling state is intentionally accessible while the call lock is not held, except when `RX_CALL_IOVEC_WAIT` allows other thread intervention.

### Dependencies and Integration Points
The structure depends on `opr_queue`, `rx_packet`, `rx_connection`, `rxevent`, `struct clock`, and RX locking globals. `arrivalProc` is used by multi-RX orchestration and by lower RX receive paths. The layout is central to packet send/receive, read/write, timeout, and debug code.

### Risks and Edge Cases
- Several fields are accessed without the call lock by design; changing ownership rules can introduce races.
- Refcount macros become no-ops without `RX_ENABLE_LOCKS`, so lifetime assumptions differ across builds.
- `xmitList` is bounded by `RX_MAXACKS`; ACK parsing and retransmission must not exceed it.
- Event pointers require careful cancellation and reference handling to avoid use-after-free.

### Test Signals
Regression tests should cover call lifecycle, refcount leak diagnostics, delayed ACK/resend/keepalive cancellation, readv/writev concurrency constraints, and debug packet queue counters when enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/rx/rx_call.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/rx/rx_clock.c -->
## sources/distributed-fs/openafs/src/rx/rx_clock.c

### Purpose
`rx_clock.c` implements the older non-pthread, non-gettimeofday user-space elapsed-time backend using `ITIMER_REAL`, while other builds mostly use inline macros from `rx_clock.h`.

### Important Functions and State
- `clock_Init` initializes the relative clock and calls `clock_UpdateTime`.
- `clock_UnInit` resets initialization state.
- `clock_UpdateTime` reads the remaining interval timer and computes elapsed time into global `clock_now`.
- `clock_Sync` resets the interval timer to a large `STARTVALUE` and advances `relclock_epoch` so elapsed time remains monotonic across timer resets.
- Globals include `clock_now`, `clock_haveCurrentTime`, `clock_nUpdates`, and static epoch/start values.

### Control Flow
On initialization, `clock_Sync` installs an ignored `SIGALRM` handler and calls `setitimer`. Later `clock_UpdateTime` computes elapsed offset from the decrementing timer; if the timer has counted below half the start value, it calls `clock_Sync` to avoid expiration. The `clock_GetTime` macro in `rx_clock.h` lazily calls `clock_UpdateTime` when `clock_haveCurrentTime` has been cleared by `clock_NewTime`.

### Dependencies and Integration Points
Depends on `rx.h`, `rx_clock.h`, `setitimer`, `getitimer`, `signal`, and `osi_Panic`. RX event scheduling and retransmission timing depend on this time base when this backend is active.

### Risks and Edge Cases
- This backend monopolizes `ITIMER_REAL`; other code using it can break RX timing.
- The time base is elapsed time since `clock_Init`, not wall time, unlike gettimeofday/pthread paths.
- System timer rounding is handled, but signal/timer interactions remain platform-sensitive.
- Time moving backwards is mostly handled by `rx_event.c`, not this file.

### Test Signals
Tests should verify event scheduling under this backend, repeated timer resyncs, `clock_NewTime` caching behavior, and no timer expiration after long-running processes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/rx/rx_clock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/rx/rx_clock.h -->
## sources/distributed-fs/openafs/src/rx/rx_clock.h

### Purpose
`rx_clock.h` defines RX's `struct clock`, time-source selection, and arithmetic/comparison macros used throughout event scheduling, retransmission, RTT calculation, and RPC statistics.

### Important APIs and Macros
- Defines `struct clock { afs_int32 sec; afs_int32 usec; }`.
- Selects `clock_Init`, `clock_NewTime`, `clock_UpdateTime`, `clock_GetTime`, and `clock_Sec` implementations for kernel, pthread/gettimeofday/UKERNEL, or interval-timer backends.
- Provides `clock_ElapsedTime`, comparison macros (`clock_Gt`, `clock_Ge`, `clock_Eq`, `clock_Le`, `clock_Lt`), zeroing/testing, add/subtract, millisecond conversion macros, and `clock_AddSq` for square accumulation in statistics.

### Control Flow and State
Most behavior is macro-expanded at call sites. Non-kernel pthread/gettimeofday paths read wall time directly. Kernel paths call `osi_GetTime`/`osi_Time`. Legacy non-pthread user-space paths use cached `clock_now` from `rx_clock.c`, invalidated by `clock_NewTime`.

### Dependencies and Integration Points
This header is used by `rx_event.c`, `rx.c`, `rx_call.c`, `rx_globals.h`, RPC stats, and any timeout code. It depends on platform time headers, `afs/afs_osi.h` in kernel builds, and `afs/afsutil.h` on Windows.

### Risks and Edge Cases
- Some macros assume non-negative durations and normalized microseconds.
- `clock_Sub` assumes the second operand is not greater than the first.
- `clock_Float` returns seconds plus a double expression but can surprise callers if integer conversions are introduced.
- The wall-time paths can move backwards after system clock changes; `rx_event.c` compensates for timer scheduling.

### Test Signals
Unit tests for arithmetic normalization, subtraction borrow behavior, elapsed milliseconds, square accumulation, and scheduler behavior after backward clock jumps are high-value.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/rx/rx_clock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/rx/rx_clock_nt.c -->
## sources/distributed-fs/openafs/src/rx/rx_clock_nt.c

### Purpose
`rx_clock_nt.c` implements the Windows NT RX clock backend using high-resolution performance counters.

### Important Functions and State
- `clock_Init` obtains `QueryPerformanceFrequency`, marks initialization, and updates current time.
- `clock_UnInit` clears initialization state for non-kernel builds.
- `clock_UpdateTime` reads `QueryPerformanceCounter`, subtracts `rxi_clock0`, converts ticks to seconds/useconds, and updates `clock_now`, `clock_haveCurrentTime`, and `clock_nUpdates`.
- Globals: `clock_now`, `clock_haveCurrentTime`, `clock_nUpdates`, `rxi_clock0`, and `rxi_clockFreq`.

### Control Flow and Integration
This file is compiled only for `AFS_NT40_ENV`. `rx_clock.h` undefines or maps clock macros so these functions provide the concrete implementation. RX event and timeout code consume the same `struct clock` API.

### State and Persistence
State is in-memory only and process-local. The epoch is the captured performance counter baseline in `rxi_clock0`.

### Risks and Edge Cases
- The file shown initializes frequency but does not set `rxi_clock0` in `clock_Init`; callers must ensure it has a meaningful baseline elsewhere or elapsed time starts from zero-initialized process state.
- If no high-performance counter is available, the process exits.
- Double conversion may lose precision for very long runtimes.

### Test Signals
Windows-specific tests should validate monotonic increases, correct usec normalization, initialization of `rxi_clock0`, and event scheduling after long-running uptime.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/rx/rx_clock_nt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/rx/rx_conn.c -->
## sources/distributed-fs/openafs/src/rx/rx_conn.c

### Purpose
`rx_conn.c` provides public accessor and mutator functions for `struct rx_connection`, isolating callers from internal connection layout.

### Important Functions
- Accessors: `rx_GetConnectionEpoch`, `rx_GetConnectionId`, `rx_GetSecurityData`, `rx_IsUsingPktCksum`, `rx_GetSecurityHeaderSize`, `rx_GetSecurityMaxTrailerSize`, `rx_IsServerConn`, `rx_IsClientConn`, `rx_PeerOf`, `rx_ServiceIdOf`, `rx_SecurityClassOf`, `rx_SecurityObjectOf`, `rx_ServiceOf`, and `rx_ConnError`.
- Mutators: `rx_SetSecurityData`, `rx_SetSecurityHeaderSize`, `rx_SetSecurityMaxTrailerSize`, and `rx_SetMsgsizeRetryErr`.

### Control Flow and State
All functions are direct field reads or writes. They do not allocate, lock, or persist state. Mutators update security-related overhead and retry behavior that are later consumed by packet sizing and send error handling.

### Dependencies and Integration Points
Includes `rx.h` and `rx_conn.h`. Used by security modules, connection cache, RPC callers, debug code, and packet sizing macros such as `rx_MaxUserDataSize`.

### Risks and Edge Cases
- No synchronization is performed; callers must respect connection lock ownership.
- Security header/trailer sizes directly affect max payload calculations and can cause packet sizing errors if changed after active calls begin.
- `rx_ConnError` is a snapshot and may race with connection error transitions.

### Test Signals
Tests should cover security module setup of header/trailer sizes, msgsize retry error propagation, and accessor correctness for client/server connections.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/rx/rx_conn.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/rx/rx_conn.h -->
## sources/distributed-fs/openafs/src/rx/rx_conn.h

### Purpose
`rx_conn.h` defines the internal RX connection object: an authenticated communication path with up to `RX_MAXCALLS` simultaneous call channels plus security, timing, NAT, and per-connection state.

### Important Fields
- Hash/free-list link, `peer`, optional locks/cv, epoch, CID, error, call pointers, per-channel call numbers/window values, busy timestamps, serial number, MTU probe state, and event pointers.
- Server/client role fields: `service`, `serviceId`, `type`, `securityIndex`, `securityObject`, and `securityData`.
- Timeout and liveness fields: `secondsUntilPing`, `timeout`, `lastSendTime`, `secondsUntilDead`, `hardDeadTime`, `idleDeadTime`, `secondsUntilNatPing`, and `natKeepAliveEvent`.
- Security overhead fields and `msgsizeRetryErr`.
- Connection-specific data array.

### Control Flow and State
The structure is allocated and initialized primarily by `rx.c`; it is searched and refcounted through connection hash tables and destroyed through RX lifecycle paths. It stores per-channel state needed to create and receive calls, and event pointers are used by challenge, delayed abort, reachability, and NAT keepalive scheduling.

### Dependencies and Integration Points
Used by `rx.c`, `rx_conn.c`, `rx_conncache.c`, security classes, debug/stat code, and call allocation. It relies on constants and flags defined in `rx.h` and peer state from `rx_peer`.

### Risks and Edge Cases
- Bottom bits of `cid` encode channel information; code must mask/shift consistently.
- Event pointer lifetime must be coordinated with connection refcounts.
- Cached connections set `RX_CONN_CACHED` and follow special release rules in `rx_conncache.c`.
- Security object and data lifetime is shared with security modules.

### Test Signals
Exercise multi-channel call allocation, connection timeout changes, NAT ping scheduling, security object attach/destroy, connection cache interactions, and debug export of connection fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/rx/rx_conn.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/rx/rx_conncache.c -->
## sources/distributed-fs/openafs/src/rx/rx_conncache.c

### Purpose
`rx_conncache.c` implements a small process-local cache of client RX connections keyed by remote address, port, service, security object, and security index.

### Important Functions and Types
- `rx_connParts_t` captures the cache key.
- `cache_entry_t` stores queue link, connection pointer, key parts, `inUse` channel count, and error marker.
- Internal helpers: `rxi_CachedConnectionsEqual`, `rxi_FindCachedConnection`, `rxi_AddCachedConnection`, and `rxi_GetCachedConnection`.
- Public functions: `rx_GetCachedConnection`, `rx_ReleaseCachedConnection`, and `rxi_DeleteCachedConnections`.

### Control Flow
`rx_GetCachedConnection` builds a key and calls the internal getter. Under `rxi_connCacheMutex` on pthread builds, the cache is scanned for a matching non-error entry with `inUse < RX_MAXCALLS`; on hit, `inUse` is incremented and the existing connection is returned. On miss, `rx_NewConnection` creates a new connection and `rxi_AddCachedConnection` prepends a cache entry and sets `RX_CONN_CACHED`.

`rx_ReleaseCachedConnection` destroys non-cached connections directly. For cached connections, it decrements `inUse`; if `rx_ConnError` is set, the entry is marked errored and destroyed once no users remain. `rxi_DeleteCachedConnections` is intended for `rx_Finalize` and destroys all cached connections.

### State and Persistence
The cache is an in-memory global `opr_queue`. It persists until RX finalization and has no durable storage.

### Dependencies and Integration Points
Depends on `rx_NewConnection`, `rxi_DestroyConnection`, `rx_ConnError`, `RX_MAXCALLS`, `RX_CONN_CACHED`, and `opr_queue`. It is an optimization for callers that repeatedly contact the same service/security tuple.

### Risks and Edge Cases
- `malloc` failure in `rxi_AddCachedConnection` silently leaves a connection flagged as cached even without an entry, which can make release leak or fail to find it.
- `inUse` tracks handed-out uses, not necessarily live RX calls; caller release discipline is critical.
- Only pthread builds lock the cache; non-pthread/LWP assumes cooperative execution.
- Cache search is linear.

### Test Signals
Tests should cover cache hit/miss behavior, reuse up to `RX_MAXCALLS`, errored connection retirement, non-cached release behavior, and finalization cleanup. A memory-failure test for `rxi_AddCachedConnection` would expose the flag/entry inconsistency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/rx/rx_conncache.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/rx/rx_event.c -->
## sources/distributed-fs/openafs/src/rx/rx_event.c

### Purpose
`rx_event.c` implements RX's timer event scheduler using a red-black tree keyed by event time, with a per-time queue for events that share the same timestamp.

### Important Types and Functions
- Private `struct rxevent` holds queue node, rb-tree node, scheduled time, refcount, handled flag, callback, and three callback arguments.
- `rxevent_Init` initializes clock, locks, event tree, free list, allocation unit, and optional scheduler callback.
- `rxevent_Post` allocates and inserts an event; if it becomes the earliest event, it invokes the scheduler callback.
- `rxevent_Cancel` removes a pending event and releases references.
- `rxevent_RaiseEvents` fires all expired events and returns the wait interval for the next event.
- `rxevent_Get`, `rxevent_Put`, and `rxevent_Put`'s internal refcount logic manage event references.
- `shutdown_rxevent` frees allocated event blocks.

### Control Flow
Events are allocated from a free list in batches. Posting compares the target time with existing tree nodes: earlier/later goes left/right; exact-time events are queued on the existing node. If the new event is earlier than the current first event, the scheduler callback wakes the event loop. Raising events gets current time, adjusts all event times if the clock moved backwards, repeatedly removes the first expired event or a same-time queued event, drops the tree lock, calls the callback, and releases the event. Cancellation handles both rb-tree head nodes and same-time queue elements, replacing tree nodes when necessary.

### State and Persistence Behavior
State is in-memory only: `freeEvents`, `eventTree`, `eventSchedule`, `allocUnit`, and `initialised`. `rxevent` has atomic references for tree and caller ownership. No events persist across process/kernel lifetime.

### Dependencies and Integration Points
Depends on `opr_queue`, `opr_rbtree`, `rx_atomic`, RX locks, `clock_*`, and allocation wrappers. Used by retransmission timers, keepalives, delayed ACKs, delayed aborts, challenge retries, reachability checks, NAT keepalives, and kernel/user event loops.

### Risks and Edge Cases
- Cancellation of same-time queued events and rb-tree node replacement is subtle and vulnerable to list/tree invariant bugs.
- The event comparison in `rxevent_RaiseEvents` fires events when `eventTime < now`; exactly equal timestamps wait until time advances.
- Backward clock adjustment walks the whole tree and assumes event-thread context.
- `shutdown_rxevent` destroys locks and frees allocation blocks but does not explicitly cancel outstanding logical events first.

### Test Signals
Unit tests should cover insertion ordering, equal-time queues, canceling head/list/tail events, refcount release, scheduler callback wakeups, backward-time adjustment, shutdown after many batch allocations, and stress with concurrent post/cancel/raise under pthread locks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/rx/rx_event.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/rx/rx_event.h -->
## sources/distributed-fs/openafs/src/rx/rx_event.h

### Purpose
`rx_event.h` exposes the RX timer event API while keeping `struct rxevent` opaque to callers.

### Important APIs
- `rxevent_Init(int nEvents, void (*scheduler)(void))`
- `rxevent_Post(struct clock *when, struct clock *now, callback, arg, arg1, arg2)`
- `rxevent_Cancel(struct rxevent **)`
- `rxevent_RaiseEvents(struct clock *wait)`
- `rxevent_Get(struct rxevent *)`, `rxevent_Put(struct rxevent **)`
- `shutdown_rxevent(void)`

### Control Flow and State
Callers initialize the package, post callbacks for absolute `struct clock` times, optionally hold references to events, cancel by pointer-to-pointer, and periodically call `rxevent_RaiseEvents` from the listener/event thread to execute due callbacks and obtain the next wait interval.

### Dependencies and Integration Points
Forward-declares `struct clock` and `struct rxevent`; actual scheduling is implemented in `rx_event.c`. Integrated by user LWP/pthread listeners and kernel event daemons.

### Risks and Edge Cases
- `rxevent_Cancel` requires a pending event pointer; a currently executing event may not cancel itself.
- Callers must use pointer-to-pointer APIs correctly because cancellation and put clear caller references.
- `when` uses RX's clock time base, which differs by platform backend.

### Test Signals
API-level tests should verify post/cancel semantics, reference get/put ownership, scheduler wakeups, and listener integration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/rx/rx_event.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/rx/rx_getaddr.c -->
## sources/distributed-fs/openafs/src/rx/rx_getaddr.c

### Purpose
`rx_getaddr.c` discovers local IPv4 interface addresses, masks, and MTUs for user-space and kernel/UKERNEL RX builds, with platform-specific paths for routing-socket/sysctl systems and ioctl-based systems.

### Important Functions
- `rxi_setaddr` and `rxi_getaddr` provide advisory address storage in kernel builds; user-space `rxi_setaddr` is a no-op.
- User-space `rxi_getaddr` returns the first address from `rx_getAllAddr`.
- `rx_getAllAddr_internal` enumerates addresses with loopback filtering.
- `rx_getAllAddr` returns non-loopback IPv4 addresses.
- `rx_getAllAddrMaskMtu` returns address, netmask, and MTU arrays, with defaults where platform APIs cannot provide them.
- Platform helpers include `rt_xaddrs`, `rxi_IsLoopbackIface`, and OpenBSD `ifm_fixversion`.

### Control Flow
On Darwin/XBSD-style systems, the code uses `sysctl` with `NET_RT_IFLIST`, parses `RTM_IFINFO` and `RTM_NEWADDR` messages, expands compact sockaddr lists, filters down/up/loopback interfaces, and records IPv4 addresses. `rx_getAllAddrMaskMtu` additionally opens a datagram socket to query interface MTU. On fallback systems, it opens an AF_INET datagram socket, calls `SIOCGIFCONF`, iterates `ifreq` entries with platform-specific sizing, filters AF_INET and loopback addresses, and optionally queries `SIOCGIFNETMASK`, `SIOCGIFMTU`, or `SIOCRIPMTU`.

### State and Persistence
No durable state. Kernel `rxi_tempAddr` is a global advisory value used for random/noise address approximation. User-space functions fill caller-provided arrays.

### Dependencies and Integration Points
Depends on `rx.h`, `rx_globals.h`, `rx_kcommon.h`, platform interface headers, `ioctl`, `sysctl`, and `rx_IsLoopbackAddr`. RX initialization and peer parameter selection use these addresses and MTUs.

### Risks and Edge Cases
- Many paths return `0` on failure, making "no interfaces" and "error" indistinguishable.
- Some error paths after opening sockets or allocating buffers may miss cleanup; for example routing-socket MTU code returns after socket failure without freeing the sysctl buffer.
- Loopback handling differs between normal and `loopbacks` modes and may skip aliased loopbacks specially.
- Fixed `NIFS` and caller `maxSize` limits truncate interface lists.
- IPv6 is not handled.

### Test Signals
Tests should run on representative platforms with multiple interfaces, loopback aliases, down interfaces, IPv4-only and no-interface scenarios, and MTU/netmask query failures. Static analysis should check cleanup paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/rx/rx_getaddr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/rx/rx_globals.c -->
## sources/distributed-fs/openafs/src/rx/rx_globals.c

### Purpose
`rx_globals.c` instantiates RX global variables by defining `GLOBALSINIT` before including `rx_globals.h`, and implements a small set of runtime tuning accessors.

### Important Functions
- `rx_SetMaxReceiveWindow` and `rx_SetMaxSendWindow` cap requested values at `rx_maxWindow`.
- `rx_GetMaxReceiveWindow` and `rx_GetMaxSendWindow` return current maxima.
- `rx_SetMinPeerTimeout` accepts values in `[1, 999]` milliseconds.
- `rx_GetMinPeerTimeout` returns the minimum peer timeout.
- Windows-only `rx_SetRxDeadTime`, `rx_GetMinUdpBufSize`, and `rx_SetUdpBufSize` provide exported functions where macros are not used.

### Control Flow and State
Including `rx_globals.h` with `GLOBALSINIT(stuff) = stuff` turns the `EXT` declarations into definitions. Setter functions mutate global tuning variables directly. No file or persistent state is written.

### Dependencies and Integration Points
Includes `rx.h`, `rx_clock.h`, `rx_packet.h`, and `rx_globals.h`. The globals are used by nearly every RX subsystem: packet pools, connection/call hashes, service pools, congestion windows, debug output, and thread-specific free packet queues.

### Risks and Edge Cases
- Setters do not enforce lower bounds for send/receive windows.
- Global tuning changes after RX startup can affect existing calls/peers unpredictably.
- The file relies on header macro choreography; including `rx_globals.h` incorrectly can create duplicate definitions or declarations.

### Test Signals
Build/link tests should ensure exactly one definition of globals. Runtime tests should verify window caps, timeout validation, and UDP buffer minimum behavior on Windows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/rx/rx_globals.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/rx/rx_globals.h -->
## sources/distributed-fs/openafs/src/rx/rx_globals.h

### Purpose
`rx_globals.h` declares or defines RX's process/kernel global state and tuning variables depending on `GLOBALSINIT`. It is the central configuration and shared-state header for RX internals.

### Important State
- Sockets/services: `rx_socket`, `rx_services`, server pool locks, port and dead/idle timings.
- Packet pool and quota state: `rx_freePacketQueue`, `rx_mallocedPacketQueue`, `rx_nFreePackets`, `rx_packetQuota`, `rxi_dataQuota`, `rx_nPackets`, packet size and jumbo size limits.
- Thread-specific packet queue support for pthread builds: `rx_ts_info_key`, `rx_ts_info_t`, and `RX_TS_FPQ_*` macros.
- Connection/call state: free call queue, `rx_port`, select masks for LWP, `rx_nextCid`, `rx_epoch`, peer and connection hash tables, cleanup list, and locks.
- Tuning variables: window sizes, NACK threshold, datagram fragment counts, soft/hard ACK rates, send/receive frag counts, peer timeout minimums, and packet quota behavior.
- Debug/stat state: debug files, packet type strings, key-create destructors, abort throttling thresholds, stats flags, hot-thread flag, and IP/UDP size.

### Control Flow
Most content is declarations, definitions, or macros. Thread-specific free packet queue macros move packets between local and global queues, update counters, and recompute limits under packet locks. Allocation macros map typed RX objects onto `rxi_Alloc`/`rxi_Free`.

### Dependencies and Integration Points
Depends on `rx.h`, `rx_packet.h`, and platform locking/threading headers. It is consumed by packet allocation, call allocation, receive/transmit paths, service scheduling, debug and stats code, connection cache, LWP/pthread listeners, and kernel support.

### State and Persistence Behavior
All state is in-memory. Some values are exported over debug/stat protocols, but no durable persistence occurs.

### Risks and Edge Cases
- This file exposes many globals; ordering and lock discipline are critical and mostly enforced by convention.
- Thread-specific free packet queue macros assume locks are held as documented and can corrupt queues if misused.
- `FD_SETSIZE` manipulation must happen before system headers; include order matters.
- Packet size globals must never decrease in some cases while applications are running.
- A typo in comments names "Threshholds"; variable names preserve the historic spelling `Threshhold`.

### Test Signals
High-value tests include packet pool stress under pthread local queues, quota exhaustion/deadlock prevention tests, dynamic window tuning tests, hash table initialization/finalization tests, and debug/stat export validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/rx/rx_globals.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/rx/rx_identity.c -->
## sources/distributed-fs/openafs/src/rx/rx_identity.c

### Purpose
`rx_identity.c` implements allocation, copying, comparison, population, and freeing of RX identity objects, which pair an identity kind, display name, and opaque exported name.

### Important Functions
- `rx_identity_match` compares kind, exported-name length, and exported-name bytes.
- `rx_identity_populate` zeroes a structure, sets kind, copies display name, and populates the exported opaque name.
- `rx_identity_new` allocates and populates a new identity.
- `rx_identity_copy` and `rx_identity_copyContents` duplicate identity contents.
- `rx_identity_freeContents` frees display name and opaque data.
- `rx_identity_free` clears caller pointer, frees contents, and frees the identity.

### Control Flow and State
Population and copy functions replace existing contents without freeing them first, as documented. Free functions clear owned pointers after release. State is heap memory allocated through `rxi_Alloc`/`rxi_Free`; no durable persistence.

### Dependencies and Integration Points
Depends on `rx/rx.h`, `rx/rx_identity.h`, and `rx_opaque` helpers. Used by security/authentication layers that need to carry a typed RX identity.

### Risks and Edge Cases
- `rx_identity_populate` can leak existing contents if called on a populated identity without first freeing.
- Allocation failures from display-name allocation and `rx_opaque_populate` are not reported; partial objects are possible.
- `rx_identity_match` assumes non-NULL identity pointers and valid exportedName buffers when length is non-zero.
- `rx_identity_freeContents` frees displayName with `strlen(displayName)`, not including the NUL byte allocated by populate.

### Test Signals
Tests should cover match/non-match by kind/name bytes, NULL display name, zero-length exported name, copy independence, repeated populate leak checks, allocation-failure behavior, and free pointer clearing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/rx/rx_identity.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/rx/rx_identity.h -->
## sources/distributed-fs/openafs/src/rx/rx_identity.h

### Purpose
`rx_identity.h` defines the RX identity structure and identity management API.

### Important APIs and Types
- `rx_identity_kind` values: `RX_ID_SUPERUSER`, `RX_ID_KRB4`, and `RX_ID_GSS`.
- `struct rx_identity` with `kind`, optional `displayName`, and `struct rx_opaque exportedName`.
- Prototypes for creation, population, matching, copying, content-freeing, and full freeing.

### Control Flow and State
The header only declares structure and operations. Implementations allocate owned copies of display and exported names.

### Dependencies and Integration Points
Includes `rx/rx_opaque.h`. It is meant for RX security layers and callers that need a common identity payload independent of the specific security mechanism.

### Risks and Edge Cases
Because ownership is in the implementation, users must know whether a function replaces existing contents without freeing. Kind values include a negative superuser sentinel, so serialization or casts to unsigned types need care.

### Test Signals
Compile tests for consumers, identity serialization tests in security layers, and memory ownership tests around copy/free are appropriate.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/rx/rx_identity.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/rx/rx_internal.h -->
## sources/distributed-fs/openafs/src/rx/rx_internal.h

### Purpose
`rx_internal.h` declares RX-private globals and functions that should not be exposed to ordinary RX library callers.

### Important APIs and State
- Private globals: `rx_nWaiting`, `rx_nWaited`, and `rx_host`.
- Defines `RXI_SENDMSG_RETRY` for error-queue send retry behavior.
- Declares internal functions from `rx.c`: running checks, delayed ACK cancellation/posting, packet wait wakeup, peer MTU updates, network error handling, peer lookup, packet receive dispatch, connection interestingness, connection/call errors, send/start/ack/abort helpers, RPC stats increment, TQ busy wait, and local address retrieval.
- Declares packet helpers: `rxi_SplitJumboPacket` and `rxi_GetLocalSpecialPacket`.
- Declares `osi_Msg` for applicable platforms.

### Control Flow and Integration
This header is a cross-file linkage contract. Receive loops in LWP/kernel paths call `rxi_ReceivePacket`; event callbacks call delayed ACK/abort/send helpers; packet and network layers call MTU and error handlers.

### State and Persistence
Only in-memory RX runtime state is referenced. No durable persistence.

### Dependencies and Integration Points
Conditionally includes Linux error-queue headers for `AFS_RXERRQ_ENV`. It is consumed by RX implementation files such as `rx_call.c`, `rx_lwp.c`, `rx_kcommon.c`, packet code, and platform socket paths.

### Risks and Edge Cases
- Internal prototypes are broad and tightly coupled to `rx.c`; signature drift breaks multiple platform paths.
- Error-queue support depends on Linux-specific types and must stay guarded.
- Callers of these functions usually need specific locks or refcounts that are not encoded in the type signatures.

### Test Signals
Build coverage with and without `AFS_RXERRQ_ENV`, kernel/user-space variants, and network error integration tests are key.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/rx/rx_internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/rx/rx_kcommon.c -->
## sources/distributed-fs/openafs/src/rx/rx_kcommon.c

### Purpose
`rx_kcommon.c` contains shared in-kernel RX support across platforms: kernel UDP socket creation/closing, RX port registration, listener startup, packet allocation/arrival adapters, peer MTU/interface initialization, interface enumeration, event daemon support, listener loops, packet receive, messaging, and panic/assertion helpers.

### Important Functions and State
- Port/socket tracking: `rxk_ports`, `rxk_portRocks`, `rxk_AddPort`, `rxk_DelPort`, `rxk_shutdownPorts`, `rxi_GetHostUDPSocket`, and `rxi_GetUDPSocket`.
- Utility/assertion: `osi_utoa`, `osi_AssertFailK`, `osi_Msg`, and `osi_Panic`.
- Kernel server/listener: `rx_ServerProc`, `MyPacketProc`, `MyArrivalProc`, `rxi_StartListener`, `afs_rxevent_daemon`, `rxk_ReadPacket`, `rxk_Listener`, and platform-specific `osi_StopListener`.
- Peer/interface sizing: `rxi_InitPeerParams`, `rxi_GetcbiInfo`, `rxi_Findcbi`, `rxi_GetIFInfo`, and `rxi_FindIfnet`.
- Socket lifecycle: `rxk_NewSocketHost`, `rxk_NewSocket`, and `rxk_FreeSocket` for supported non-Linux/non-Sun/non-sockproxy platforms in this common path.
- Globals: `rxk_PacketArrivalProc`, `rxk_GetPacketProc`, `rxk_initDone`, static local interface address/MTU arrays, and listener PID/task globals in listener builds.

### Control Flow
RX kernel initialization calls `rxi_GetHostUDPSocket` to create/bind a UDP socket via `rxk_NewSocketHost`, then registers the bound port. `rxi_StartListener` either installs packet allocation/arrival callbacks and calls `rxk_init`, or platform listener builds run `rxk_Listener`. Incoming packets are allocated by `MyPacketProc` or `rxk_ReadPacket`, decoded, and passed to `rxi_ReceivePacket`; returned packet buffers are freed. Server worker threads reserve packets and quotas before entering `rxi_ServerProc`.

Peer initialization calls interface discovery on demand, finds the best interface for a remote address, sets retransmission timeout defaults, derives interface MTU after IP/UDP/RX overhead, clamps to RX send/receive limits, initializes NAT/max MTU and datagram packet counts, and starts congestion control at one packet. The event daemon periodically calls `rxevent_RaiseEvents` and transitions `afs_termState` through shutdown states.

### State and Persistence
State is kernel memory only: registered RX ports, socket pointers, interface caches, listener PID/task, packet callbacks, and global RX tuning. No durable persistence.

### Dependencies and Integration Points
Depends on extensive kernel networking headers via `rx_kcommon.h`, `rx_packet.h`, `rx_internal.h`, `rx_stats.h`, `rx_peer.h`, `afs/opr.h`, `afsint.h`, and platform socket APIs (`socreate`, `sobind`, `soreserve`, `soclose`, `sock_socket`, `osi_NetReceive`). It integrates with `rx.c` packet processing, `rx_event.c`, AFS global lock macros, and platform shutdown state.

### Risks and Edge Cases
- Platform preprocessor paths are numerous; compile coverage is the main risk.
- Port registration has a fixed `MAXRXPORTS` limit and no locking in the common code shown.
- `rxk_shutdownPorts` conditionally closes sockets; incorrect build macros can leak or double-close.
- Packet receive sizes are inferred partly from maximum advertised receive size because the RX header lacks a full packet length.
- Interface cache update logic includes complex platform loops and must handle vnet/epoch locking correctly.
- Kernel socket setup uses platform-specific allocation and cleanup; error paths can be hard to validate.

### Test Signals
Kernel build matrix coverage is essential. Runtime signals include successful bind/listen/shutdown, packet receive/decode under jumbo and small packet sizes, interface MTU derivation, peer timeout selection, listener wakeup on shutdown, event daemon shutdown state transitions, and panic/assert formatting tests where possible.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/rx/rx_kcommon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/rx/rx_kcommon.h -->
## sources/distributed-fs/openafs/src/rx/rx_kcommon.h

### Purpose
`rx_kcommon.h` is the common kernel include umbrella and type/macro bridge for RX kernel builds across supported operating systems.

### Important Definitions
- Includes large sets of platform kernel, socket, route, interface, UDP/IP, process, stdarg, AFS, RX, XDR, stats, and errno headers.
- Defines `MAXRXPORTS`, `rxk_ports_t`, `rxk_portRocks_t`, and externs `rxk_ports`/`rxk_portRocks`.
- Defines workarounds such as empty `struct coda_inode_info` for Linux header conflicts.
- Externs platform objects such as `inetdomain` and Solaris interface info when relevant.

### Control Flow and State
This header has no executable flow, but it determines which kernel APIs and structs are visible to `rx_kcommon.c` and other kernel RX files. It maps platform availability through preprocessor branches.

### Dependencies and Integration Points
Central to kernel RX compilation. It includes `rx/rx.h`, `rx_kmutex.h`, `rx/rx_globals.h`, `afs/afs_osi.h`, `afs/lock.h`, `rx/xdr.h`, and `afs/afs_stats.h`.

### Risks and Edge Cases
- Include order is fragile and platform-specific; small changes can break old kernels.
- The Linux Coda header workaround intentionally defines guard macros and a dummy struct, which can conflict if real Coda definitions are later needed.
- Kernel API drift makes these branches high-maintenance.

### Test Signals
Compile-only matrix testing across Linux, BSD, Darwin, Solaris, AIX, and UKERNEL configurations is the main signal. Static include-order tests or CI jobs per platform macro set are valuable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/rx/rx_kcommon.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/rx/rx_kernel.h -->
## sources/distributed-fs/openafs/src/rx/rx_kernel.h

### Purpose
`rx_kernel.h` defines RX kernel-client environment mappings for allocation, sockets, sleep/wakeup, panic/assertion, network epoch handling, and interface abstraction.

### Important APIs and Macros
- Maps `osi_Alloc`/`osi_Free` to AFS kernel allocators.
- Defines `osi_socket` as `struct socket *` and `OSI_NULLSOCKET`.
- Maps `osi_rxSleep` and `osi_rxWakeup` to AFS sleep/wakeup tracing wrappers.
- Defines kernel `osi_Panic`/`osi_Assert` variants for Linux, AIX, and other platforms.
- Defines `RX_NET_EPOCH_ENTER`/`RX_NET_EPOCH_EXIT` for FreeBSD epoch-protected network access.
- Abstracts interface types and accessors: `rx_ifnet_t`, `rx_ifaddr_t`, `rx_ifnet_mtu`, `rx_ifnet_flags`, `rx_ifaddr_withnet`, `rx_ifaddr_ifnet`, and address/netmask/dstaddr copy helpers.

### Control Flow and State
The header is macro-driven. It affects how kernel RX code sleeps, wakes, allocates, asserts, enters network epochs, and traverses interface structures. No state is persisted.

### Dependencies and Integration Points
Used by `rx.h` in kernel builds and by kernel RX sources. Integrates with AFS tracing, AFS global lock behavior, kernel socket types, FreeBSD network epochs, and Darwin/BSD interface APIs.

### Risks and Edge Cases
- Macros can evaluate arguments more than once or require surrounding statement care.
- Interface accessors hide platform differences but make compile-time coverage necessary.
- Assertion/panic behavior differs substantially across platforms; Linux uses `BUG()`.
- `rxi_ReScheduleEvents` is defined as `0` in some kernel configurations, so callers must tolerate that.

### Test Signals
Kernel compile coverage and smoke tests for sleep/wakeup, network epoch macros, interface lookup, and assertions under each platform macro set are most relevant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/rx/rx_kernel.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/rx/rx_lwp.c -->
## sources/distributed-fs/openafs/src/rx/rx_lwp.c

### Purpose
`rx_lwp.c` implements RX's user-space LWP threading backend, including sleeps/wakeups, listener and server process startup, select/event integration, packet receive dispatch, socket registration, and sendmsg/recvmsg wrappers.

### Important Functions and State
- Thread primitives: `rxi_Sleep`, `rxi_Wakeup`, `rxi_Delay`, `rxi_InitializeThreadSupport`.
- Listener control: `rxi_StopListener`, `rxi_ReScheduleEvents`, `rxi_StartListener`, static `rx_ListenerProc`, and internal `rxi_ListenerProc`.
- Server startup: `rxi_StartServerProc`, `rx_ServerProc`.
- Socket integration: `rxi_Listen`, `rxi_Recvmsg`, `rxi_Sendmsg`.
- Globals: `debugSelectFailure`, `rx_listenerPid`, and static `quitListening`.

### Control Flow
Initialization sets up LWP and IOMGR support and clears `rx_selectMask`. `rxi_StartListener` creates a high-priority listener LWP. The listener loop allocates or reuses a receive packet, raises due RX events to compute the next select timeout, polls opportunistically when the last poll found data or every few seconds, otherwise calls `IOMGR_Select`, and dispatches readable sockets through `rxi_ReadPacket` and `rxi_ReceivePacket`. If a new server call is found, the listener trades into `rxi_ServerProc`; server workers similarly alternate between serving and listening, implementing the hot-thread style handoff.

`rxi_Sendmsg` simulates blocking send on a nonblocking socket by retrying `sendmsg`, waiting with `select` on writable readiness for `EWOULDBLOCK`/`ENOBUFS` and Linux-specific tolerated errors.

### State and Persistence
All state is in-memory. The select mask and min/max socket descriptors are global RX state. No durable persistence.

### Dependencies and Integration Points
Depends on LWP/IOMGR, `rx_globals.h`, `rx_internal.h`, `rx_stats.h`, packet allocation/read functions, event scheduler, and optional registration/swap-name callbacks. Integrates with non-pthread RX user-space service loops.

### Risks and Edge Cases
- `FD_SETSIZE` and descriptor bounds matter; `rxi_Listen` rejects descriptors beyond the configured size.
- Listener/server role swapping is subtle and relies on returned `newcall`/thread IDs.
- Select errors increment a debug counter but otherwise continue.
- `rxi_Sendmsg` returns negative errno-style values on some paths and `-1` on others.
- Nonblocking sockets and tolerated Linux UDP errors require careful behavior under packet loss or ICMP errors.

### Test Signals
Integration tests should cover LWP server startup, listener wakeup from new earlier events, socket registration bounds, packet receive dispatch, listener stop, send retry behavior under `EWOULDBLOCK`/`ENOBUFS`, and hot-thread handoff.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/rx/rx_lwp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/rx/rx_lwp.h -->
## sources/distributed-fs/openafs/src/rx/rx_lwp.h

### Purpose
`rx_lwp.h` provides no-op mutex, condition variable, and call refcount macros for RX builds using cooperative LWP rather than preemptive pthread locks.

### Important Definitions
- Typedefs `afs_kmutex_t` and `afs_kcondvar_t` as `int`.
- Defines `MUTEX_*`, `CV_*`, `CALL_HOLD*`, and `CALL_RELE*` macros as no-ops or constant success for try-enter.

### Control Flow and State
There is no runtime state. The header compiles shared RX code without lock objects when LWP scheduling guarantees are expected to provide sufficient serialization.

### Dependencies and Integration Points
Included by `rx.h` when not `KERNEL` and not `AFS_PTHREAD_ENV`. Used indirectly by all RX code compiled under the LWP backend.

### Risks and Edge Cases
- Shared code that relies on actual locking must not run concurrently under LWP in ways that violate cooperative assumptions.
- Refcount macros are no-ops, so lifetime diagnostics differ from pthread/kernel builds.
- Adding new code that assumes condition variables actually block will fail under this backend.

### Test Signals
Build and run RX LWP server/client tests, especially call lifecycle and event interactions, to ensure no code accidentally depends on real mutex/cv behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/rx/rx_lwp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/rx/rx_misc.c -->
## sources/distributed-fs/openafs/src/rx/rx_misc.c

### Purpose
`rx_misc.c` provides miscellaneous RX support: host/network system error conversions, zero-length allocation wrappers, optional refcount debug state, and an optional lock database for selected kernel builds.

### Important Functions and State
- `hton_syserr_conv` maps local `ENOSPC` and `EDQUOT` to AFS network errors `VDISKFULL` and `VOVERQUOTA`.
- `ntoh_syserr_conv` maps network errors back to local `ENOSPC`/`EDQUOT`.
- User-space `osi_alloc`/`osi_free` wrap `mem_alloc`/`mem_free` and special-case zero-length allocations with a static sentinel.
- `rx_callHoldType` is defined when lock/refcount checking is enabled.
- Under `RX_LOCKS_DB`, `rxdb_init`, `rxdb_RecordLockLocation`, `rxdb_grablock`, and `rxdb_droplock` track held locks and lock locations for debugging.

### Control Flow and State
Error conversion is simple conditional mapping. Allocation returns a non-NULL sentinel for zero-size requests and ignores free requests for that sentinel or NULL. The lock database initializes free lists and hash tables, records lock ownership by holder id, panics on duplicate acquisition or invalid release, and optionally records coverage of lock locations.

### Dependencies and Integration Points
Depends on `afs/errors.h`, XDR/memory allocation support, RX locking macros in debug configurations, and platform kernel lock primitives for lock database builds. Used by RX callers and generated RPC paths that need portable system error values.

### Risks and Edge Cases
- Only a small subset of errno values is translated.
- `osi_free` ignores the supplied `size` for the zero sentinel; callers must pass the original size for normal allocations.
- Lock database uses fixed-size arrays and panics when exhausted.
- Some old-style function definitions in `RX_LOCKS_DB` paths lack modern prototypes, which can be compiler-sensitive.

### Test Signals
Unit tests for errno translation, zero-length allocation/free, and lock database duplicate/invalid release panic behavior under debug builds are useful.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/rx/rx_misc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/rx/rx_misc.h -->
## sources/distributed-fs/openafs/src/rx/rx_misc.h

### Purpose
`rx_misc.h` provides small RX configuration helpers, platform pinning macros, and file identifiers for the optional RX lock database.

### Important Definitions
- Includes Solaris socket/fcntl headers when needed.
- Defines `PIN`/`UNPIN` as AIX kernel pin/unpin or no-ops elsewhere.
- Defines lock database file IDs: `RXDB_FILE_RX`, `RXDB_FILE_RX_EVENT`, `RXDB_FILE_RX_PACKET`, and `RXDB_FILE_RX_RDWR`.

### Control Flow and State
No runtime control flow. Macros are compile-time integration points for platform memory pinning and lock debug metadata.

### Dependencies and Integration Points
Included by `rx.h` and lock-debug-aware files. The file IDs are used by optional lock database instrumentation.

### Risks and Edge Cases
File IDs must remain unique if new lock-instrumented files are added. `PIN`/`UNPIN` no-ops hide platform-specific memory residency behavior from most builds.

### Test Signals
Compile tests with AIX kernel macros and `RX_LOCKS_DB` enabled are the main validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/rx/rx_misc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/rx/rx_multi.c -->
## sources/distributed-fs/openafs/src/rx/rx_multi.c

### Purpose
`rx_multi.c` implements the runtime support for multi-RX calls, allowing similar RPC calls to be issued concurrently over multiple connections and processed as replies arrive.

### Important Functions
- `multi_Init` allocates call and ready arrays plus a `multi_handle`, initializes lock/cv, creates one `rx_NewCall` per connection, and installs `multi_Ready` as each call's arrival procedure.
- `multi_Select` waits until a call index is ready or all calls are ready, then returns the next ready index or `-1`.
- `multi_Ready` is the RX arrival callback that appends an index to the ready list and wakes waiters.
- `multi_Finalize` aborts any unfinished calls with `RX_USER_ABORT`, destroys synchronization primitives, and frees allocated arrays/handle.

### Control Flow
Callers use the macros in `rx_multi.h` to start all calls, flush writes, and then repeatedly select ready replies. The arrival callback is invoked when the first reply packet or abort arrives. `multi_Select` blocks on a condition variable or LWP sleep until new ready entries exist. Finalization ensures outstanding calls are ended.

### State and Persistence
`multi_handle` state is allocated per multi-call block and freed at the end. No durable persistence.

### Dependencies and Integration Points
Depends on `rx_NewCall`, `rx_SetArrivalProc`, `rx_FlushWrite`, `rx_EndCall`, RX sleep/wakeup or locks, and allocation wrappers. It is designed for rxgen-generated multi-call macros.

### Risks and Edge Cases
- Allocation failure calls `osi_Panic`, not a recoverable error.
- Complex work inside a multi body can keep call channels occupied and cause deadlocks; `rx_multi.h` documents this risk.
- Concurrent `multi_Rx` over the same connections must use consistent connection ordering.
- Arrival callback ordering and ready array bounds depend on exactly one first-ready event per call.

### Test Signals
Tests should cover multiple successful replies, aborts/errors, finalization aborting unfinished calls, ready ordering, sleep/wakeup behavior, and concurrent calls with consistent connection order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/rx/rx_multi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/rx/rx_multi.h -->
## sources/distributed-fs/openafs/src/rx/rx_multi.h

### Purpose
`rx_multi.h` defines `struct multi_handle` and macros that turn the support functions in `rx_multi.c` into a structured multi-RX calling pattern.

### Important APIs and Macros
- `struct multi_handle` stores call array, ready index array, counters, ready pointers, and optional lock/cv.
- `multi_Rx(conns, nConns)` opens the multi-call block and initializes a handle.
- `multi_Body(startProc, endProc)` starts unstarted calls, flushes writes, selects ready calls, and ends calls.
- `multi_Abort` breaks from the loop.
- `multi_End` finalizes the handle.

### Control Flow
The macros implement a loop over not-yet-started calls and ready calls. They expose `multi_i`, `multi_i0`, `multi_error`, `multi_call`, and `multi_h` to the macro body. This lets rxgen-generated code run call-specific start/end procedures while sharing the same orchestration logic.

### Dependencies and Integration Points
Used with `multi_Init`, `multi_Select`, and `multi_Finalize`. It depends on caller discipline and RX call APIs. Comments document integration constraints for lock ordering and connection reuse.

### Risks and Edge Cases
- Macros introduce scoped variables with fixed names and are sensitive to body structure.
- `multi_Abort` is a simple `break`, so it only exits the macro loop.
- Heavy work inside the macro body can hold channels open longer than expected.
- Same-connection concurrent multi calls can deadlock without stable ordering.

### Test Signals
Generated-code tests should exercise macro expansion paths, early abort, all-error/all-success cases, and nested surrounding control flow.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/rx/rx_multi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/rx/rx_null.c -->
## sources/distributed-fs/openafs/src/rx/rx_null.c

### Purpose
`rx_null.c` implements the RX null security class, which performs no authentication, protection, or per-connection security behavior.

### Important Functions and State
- Static `null_ops` is a zeroed `struct rx_securityOps`, so all security operations are absent.
- Static `null_object` points at `null_ops`.
- `rxnull_NewServerSecurityObject` and `rxnull_NewClientSecurityObject` both return the singleton `null_object`.

### Control Flow and State
The functions simply return the address of the singleton object. `RXS_*` macros in `rx.h` treat absent operation pointers as no-op success/zero behavior.

### Dependencies and Integration Points
Depends on `rx.h` security class definitions. Used by services and clients that select `RX_SECIDX_NULL`.

### Risks and Edge Cases
- The singleton has no reference management in this file; users must not free it.
- Null security intentionally provides no authentication or packet protection.
- Because all ops are NULL, any caller expecting callbacks for setup/teardown must tolerate no-ops.

### Test Signals
Tests should verify null client/server objects are identical singleton pointers, calls succeed without security callbacks, and code does not attempt to release/free the singleton incorrectly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/rx/rx_null.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/rx/rx_null.h -->
## sources/distributed-fs/openafs/src/rx/rx_null.h

### Purpose
`rx_null.h` is a legacy placeholder header whose comment says "Remove this file".

### Important APIs
No declarations or definitions are present in the file.

### Control Flow, State, and Dependencies
There is no runtime behavior and no state. It is included by `rx.h`, likely for historical compatibility with code expecting an RX null header.

### Risks and Edge Cases
Removing it without checking includes would break builds that include `rx_null.h` directly or transitively. Its lack of prototypes means users rely on `rx_prototypes.h` or other headers for null security declarations.

### Test Signals
Build tests should detect whether any consumers still include this header directly. A cleanup would require include-graph validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/rx/rx_null.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/rx/rx_opaque.c -->
## sources/distributed-fs/openafs/src/rx/rx_opaque.c

### Purpose
`rx_opaque.c` implements owned variable-length byte buffers used by RX identity and security-related code.

### Important Functions
- Allocation/population: `rx_opaque_new`, `rx_opaque_alloc`, `rx_opaque_populate`, and `rx_opaque_copy`.
- Cleanup: `rx_opaque_freeContents`, `rx_opaque_zeroFreeContents`, `rx_opaque_free`, and `rx_opaque_zeroFree`.
- Comparison/debug: `rx_opaque_cmp` and `rx_opaque_stringify`.

### Control Flow and State
`rx_opaque_new` allocates the struct and populates it. `rx_opaque_alloc` allocates a zero-filled buffer and stores length. `rx_opaque_populate` resets the destination to empty, allocates new storage if data and length are non-zero, and copies bytes. Cleanup functions free contents and clear fields; zero-free variants wipe data before freeing. `rx_opaque_cmp` compares common-prefix bytes and then length. `rx_opaque_stringify` writes `<len>:<hex>` into a fixed 100-byte stack-owned output buffer supplied by caller.

### Dependencies and Integration Points
Depends on `rxi_Alloc`, `rxi_Free`, `opr_min`, `osi_Assert`, and `rx_opaque.h`. Used by `rx_identity.c` and likely security mechanisms needing exported binary names or tokens.

### Risks and Edge Cases
- Populate/copy functions replace existing contents without freeing them, so callers must avoid leaks.
- `rx_opaque_new` does not handle populate failure by freeing the allocated struct.
- `rx_opaque_alloc` with length zero depends on allocator behavior; populate avoids that path for zero length.
- `rx_opaque_cmp` asserts if length is non-zero and value is NULL.
- `rx_opaque_stringify` truncates large buffers silently except for the length prefix.

### Test Signals
Unit tests should cover zero-length and NULL buffers, copy independence, comparison ordering by bytes and length, zero-free wiping, stringify truncation, and allocation-failure cleanup behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/rx/rx_opaque.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/rx/rx_opaque.h -->
## sources/distributed-fs/openafs/src/rx/rx_opaque.h

### Purpose
`rx_opaque.h` defines the RX opaque byte-buffer type and the API for allocation, copying, secure freeing, comparison, and debug stringification.

### Important APIs and Types
- `struct rx_opaque { size_t len; void *val; }`.
- `struct rx_opaque_stringbuf { char sbuf[100]; }`.
- `RX_EMPTY_OPAQUE` initializer.
- Prototypes for `rx_opaque_new`, `rx_opaque_alloc`, `rx_opaque_populate`, `rx_opaque_copy`, content and object free/zero-free helpers, `rx_opaque_cmp`, and `rx_opaque_stringify`.

### Control Flow and State
The header has no executable flow. It defines ownership-bearing structures whose storage is managed by `rx_opaque.c`.

### Dependencies and Integration Points
Included by `rx_identity.h` and security-related consumers. It intentionally keeps the representation simple for copying and wire/exported-name uses.

### Risks and Edge Cases
Because `val` is a raw pointer and `len` is public, consumers can create invalid states such as non-zero length with NULL value. The 100-byte stringify buffer is for diagnostics only and cannot uniquely identify large opaque values.

### Test Signals
Consumer tests should validate initialization with `RX_EMPTY_OPAQUE`, ownership transfer assumptions, and comparison/stringification behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/rx/rx_opaque.h -->
