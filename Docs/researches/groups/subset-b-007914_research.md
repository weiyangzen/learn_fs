# subset-b-007914 Research

Grouped source research for XRootD scheduler, send queue, statistics, trace/monitoring contracts, authorization core, auth database parser, capability matching, configuration refresh, entity attributes, group cache handling, and CMake integration. Each source file has its own marker-delimited section for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/Xrd/XrdScheduler.cc -->
# sources/distributed-fs/xrootd/src/Xrd/XrdScheduler.cc

## Purpose

`XrdScheduler.cc` implements the core XRootD in-process scheduler: a pthread-backed work queue for `XrdJob` objects, a time scheduler for delayed jobs, adaptive worker creation and idle thread retirement, XML scheduler stats, and a SIGCHLD-based child reaper used after scheduler-mediated `fork()`. The file was read completely.

## Important APIs, Types, and Functions

External pthread entry points `XrdStartReaper`, `XrdStartTSched`, and `XrdStartWorking` bridge C pthread startup to `XrdScheduler::Reaper()`, `TimeSched()`, and `Run()`. Constructors initialize the scheduler from explicit `XrdSysError`/`XrdSysTrace`, deprecated `XrdOucTrace`, or a standalone stderr logger. `Boot()`, `Init()`, and `setNproc()` establish counters and resource limits. `Schedule()` has immediate, list, and timed overloads. `Cancel()` removes timed jobs. `Start()` launches the timer thread and initial workers. `Stats()` emits `<stats id="sched">`. `hireWorker()` starts worker threads and clamps limits after thread creation failure. `Fork()` and `Reaper()` track and reap child PIDs through local `XrdSchedulerPID` nodes.

## Control Flow

Immediate jobs are appended under `SchedMutex`, `WorkAvail.Post()` wakes workers, and `Run()` repeatedly marks a worker idle, waits on the semaphore, dequeues one job, optionally hires another worker if no idle worker remains, and calls `jp->DoIt()`. Timed jobs are sorted by `SchedTime` under `TimerMutex`; `TimeSched()` waits until the head expires, dequeues it, and reschedules it as immediate work. The scheduler itself is an `XrdJob`; `DoIt()` performs idle-worker layoffs and reschedules itself when `max_Workidl` is positive. `Fork()` adds child PIDs to a reaper list and lazily starts the reaper thread.

## State and Persistence Behavior

State is entirely in memory: worker counters, job queues, timer queue, child PID list, and statistics counters. Synchronization is split across `SchedMutex`, `DispatchMutex`, `TimerMutex`, and `ReaperMutex`. There is no durable persistence. The destructor is intentionally empty because the scheduler is treated as process-lifetime infrastructure.

## Dependencies and Integration Points

The scheduler depends on `XrdJob`, `XrdSysThread`, `XrdSysMutex`, `XrdSysSemaphore`, `XrdSysCondVar`, `XrdSysError`, `XrdSysTrace`, and platform process APIs. It is used by global server code, the send queue, stats reporter, config refresh jobs, and any module that schedules `XrdJob` work.

## Risks and Edge Cases

Timed `Cancel()` only unlinks a job and does not clear `NextJob`, so callers must not assume detached state. `Run()` self-deletes neither jobs nor worker objects; job lifetime is caller-owned unless the job's `DoIt()` deletes itself. `setNproc()` mutates process resource limits and must be validated on Linux-like systems with unusual `pid_max` or `RLIMIT_NPROC`. The reaper assumes `SIGCHLD` is blocked in `main()` for `sigwait()` semantics. Worker count correction after thread creation failure lowers `max_Workers` to the current count, which can permanently constrain the scheduler until reconfigured.

## Test Signals

Useful tests include queue ordering, timed scheduling order and cancellation, worker growth when backlog exceeds idle capacity, idle layoff after `max_Workidl`, stats XML sanity, failure injection for thread creation, and fork/reaper tests with normal exit and signal termination. Concurrency tests should stress simultaneous `Schedule()`, timed `Schedule()`, and `Cancel()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/Xrd/XrdScheduler.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/Xrd/XrdScheduler.hh -->
# sources/distributed-fs/xrootd/src/Xrd/XrdScheduler.hh

## Purpose

`XrdScheduler.hh` declares `XrdScheduler`, the process-wide job scheduler interface used by XRootD server components for immediate work, delayed work, worker pool management, stats, and child-process reaping. The file was read completely.

## Important APIs, Types, and Functions

`XrdScheduler` inherits `XrdJob` so the scheduler can schedule its own idle-monitor job. Public APIs are `Active()`, `Cancel()`, `canStick()`, `DoIt()`, `Fork()`, `Reaper()`, `Run()`, immediate/list/timed `Schedule()`, `setParms()`, `Start()`, `Stats()`, `TimeSched()`, and `setNproc()`. Statistical counters exposed as public fields include `num_TCreate`, `num_TDestroy`, `num_Jobs`, `max_QLength`, and `num_Limited`. Constructors cover modern trace, ABI-compatible old trace, and standalone modes.

## Control Flow

The header exposes two scheduling planes: FIFO immediate work via `WorkFirst`/`WorkLast` and sorted delayed work via `TimerQueue`. `Start()` is the lifecycle entry point; workers run `Run()`, timed dispatch runs `TimeSched()`, and the scheduler's own `DoIt()` handles idle cleanup.

## State and Persistence Behavior

The class owns mutable in-memory counters and queues protected by dedicated mutexes. `WorkAvail` is the work semaphore; `TimerRings` wakes the timer thread when a new earliest timed job arrives; `firstPID` is the reaper list. No on-disk state is declared.

## Dependencies and Integration Points

The header depends on `XrdSysPthread.hh` synchronization wrappers and `XrdJob.hh`. It forward-declares tracing and logging types to keep the public scheduler interface light. `MAX_SCHED_PROCS` and `DFL_SCHED_PROCS` define scheduler resource-limit policy used by the implementation.

## Risks and Edge Cases

Several counters are public, so external code can observe and potentially depend on implementation details. `Active()` computes a non-locked snapshot and can be approximate. Job ownership is not explicit in the type signatures, so misuse can lead to jobs being queued while stack-allocated or deleted. `canStick()` also reads unsynchronized counters.

## Test Signals

Compile checks should cover all constructor overloads for ABI compatibility. Behavioral tests should validate public counters, queue state transitions, and that timed and immediate scheduling remain compatible with `XrdJob` subclasses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/Xrd/XrdScheduler.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/Xrd/XrdSendQ.cc -->
# sources/distributed-fs/xrootd/src/Xrd/XrdSendQ.cc

## Purpose

`XrdSendQ.cc` implements a per-link asynchronous send queue. It tries Linux nonblocking socket sends while the link write mutex is held; if a send cannot complete, it copies the remaining bytes into heap messages and uses the global scheduler to flush them with blocking `send()`. The file was read completely.

## Important APIs, Types, and Functions

`XrdSendQ::Send(const char*, int)` and `Send(const iovec*, int, int)` are the primary caller APIs and require `wMutex` to be locked. `SendNB()` overloads perform Linux-only `MSG_DONTWAIT` sends for contiguous and vector data. `QMsg()` appends copied fragments, schedules the queue runner, enforces `qMax`, and emits slow-client warnings based on `qWarn`. `DoIt()` drains queued messages. `Terminate()` handles link shutdown and object deletion. Private helpers `RelMsgs()` and `Scuttle()` free or quarantine queued messages. The local `LinkShutdown` job calls `XrdLink::Shutdown(true)` asynchronously.

## Control Flow

When no queue runner is active, `Send()` first attempts to write directly. A partial or would-block result is copied into an `mBuff` and queued. If a runner is already active, the whole pending message or current iovec tail is copied directly to the queue. `QMsg()` schedules `this` as an `XrdJob` once per active drain. `DoIt()` locks the write mutex, frees deferred deletion messages, pops the FIFO, unlocks around blocking `send()`, and relocks before checking for more work. On send error it scuttles outstanding messages. Termination either marks an active runner to self-delete or frees queues and deletes immediately.

## State and Persistence Behavior

State is per-object and in memory: FIFO `fMsg`/`lMsg`, deferred `delQ`, socket fd snapshot `theFD`, queued count `inQ`, warning threshold `qWmsg`, discard counter, and `active`/`terminate` flags. Static `qWarn`, `qMax`, and `qPerm` are process-wide knobs, though `qPerm` is settable but unused in this implementation. Lifetime is delicate: active queue runners may delete `this` after unlocking.

## Dependencies and Integration Points

It depends on `XrdLink`, global `XrdGlobal::Sched`, global `XrdGlobal::Log`, `XrdSysMutex`, POSIX `send()`, and Linux `MSG_DONTWAIT`/`MSG_MORE`. It is the buffering layer for network link writes when clients are slow.

## Risks and Edge Cases

The queue copies unsent data into a flexible `mBuff` pattern declared with `mData[4]`; allocation sizes must remain conservative. `QMsg()` can discard on `qMax`, returning failure after data may have been partially sent. `SendNB()` checks `retc == EWOULDBLOCK` instead of `errno == EWOULDBLOCK` in two places, which is likely harmless on Linux where `EAGAIN` usually covers it but is still suspicious. `DoIt()` uses blocking send after unlocking, so link closure races rely on fd invalidation and mutex protocol. `Terminate()` can schedule shutdown before deleting the queue, so link reference accounting must stay correct.

## Test Signals

Tests should simulate full socket buffers, partial sends, iovec partial sends, queue threshold warnings, queue max discard behavior, send errors, and termination with and without an active runner. Linux-specific tests should verify `MSG_MORE` behavior and non-Linux fallback behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/Xrd/XrdSendQ.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/Xrd/XrdSendQ.hh -->
# sources/distributed-fs/xrootd/src/Xrd/XrdSendQ.hh

## Purpose

`XrdSendQ.hh` declares `XrdSendQ`, an `XrdJob` subclass that buffers socket output for an `XrdLink` when immediate nonblocking sends cannot finish. The file was read completely.

## Important APIs, Types, and Functions

Public methods are `Backlog()`, `DoIt()`, contiguous and iovec `Send()` overloads, static setters `SetAQ()`, `SetQM()`, `SetQW()`, and `Terminate()`. The constructor binds the queue to a link and write mutex. Private methods include `SendNB()`, `QMsg()`, `RelMsgs()`, and `Scuttle()`. The nested `mBuff` struct is a variable-length heap message node.

## Control Flow

The header establishes the contract that callers hold `wMutex` for `Send()` and `Terminate()`. `DoIt()` is invoked by `XrdScheduler` when queued data needs draining. Queue state and deletion are coordinated through `active` and `terminate`.

## State and Persistence Behavior

All state is process memory. Static fields define global warning and maximum queue policy. Per-link fields keep FIFO message pointers, deletion queue, fd, backlog count, warning escalation, discard count, and lifecycle flags. No durable state is present.

## Dependencies and Integration Points

It depends on `XrdJob`, `XrdLink`, `XrdSysMutex`, POSIX `unistd.h`, and `struct iovec`. It is part of the Xrd network/link send path and integrates with the global scheduler at implementation time.

## Risks and Edge Cases

The destructor is private and virtual, requiring lifetime to be controlled by `Terminate()` or internal self-deletion. The class exposes `Backlog()` without locking, so it is advisory. `SetAQ()` exposes `qPerm`, but this member has no observed use in the implementation, suggesting a stale or externally consumed policy hook.

## Test Signals

Compile coverage should catch ownership and include-order regressions. Runtime tests should validate that callers can safely use both send overloads under the write mutex and that `Terminate()` does not leak queued messages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/Xrd/XrdSendQ.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/Xrd/XrdStats.cc -->
# sources/distributed-fs/xrootd/src/Xrd/XrdStats.cc

## Purpose

`XrdStats.cc` implements XRootD runtime statistics generation and automatic UDP reporting. It builds XML reports for server subsystems, optional JSON reports for monitor add-ons and plugins, exports monitor-roll state into `XrdOucEnv`, and schedules periodic reporting through `XrdScheduler`. The file was read completely.

## Important APIs, Types, and Functions

The local `XrdStatsJob` schedules recurring `Report()` calls. The constructor builds XML and JSON header templates with version, source, boot time, program, instance, pid, and site, allocates a page-aligned 64 KiB shared buffer, and creates `XrdMonitor`. `Init()` creates up to two `XrdNetMsg` destinations and enables auto-reporting. `Report()` sends XML and plugin/addon JSON UDP packets. `Stats()` provides callback-based on-demand XML stats. `GenStats()` appends selected subsystem stats. `InfoStats()` and `ProcStats()` format host/port/name and `getrusage()` CPU counters.

## Control Flow

Initialization records destinations and creates a timer job if at least one destination is configured. Each timer firing calls `Report()` and reschedules itself. `Report()` optionally disables synchronous stats collection when `autoSync` is enabled and scheduler activity is high, then locks `statsMutex` around the shared XML buffer. Add-on/plugin JSON packets are generated separately into stack UDP buffers and sent as iovec triplets. On-demand `Stats()` locks the same buffer and invokes callback methods with generated data.

## State and Persistence Behavior

State is process-lifetime memory: destinations, scheduler pointer, buffer manager, monitor object, shared XML buffer, immutable header strings, selected XML/JSON options, auto-sync flag, and host/name/port metadata. There is no persistence beyond emitted network telemetry.

## Dependencies and Integration Points

The implementation integrates with `XrdBuffManager::Stats`, `XrdLink::Stats`, `XrdPoll::Stats`, `XrdProtLoad::Statistics`, `XrdScheduler::Stats`, `XrdMonitor::Format`, `XrdNetMsg::Send`, `XrdSysTimer`, and XRootD version macros. It is a central aggregator for server monitoring.

## Risks and Edge Cases

Report generation assumes a 64 KiB UDP-sized buffer; long plugin/addon output may be truncated by `Format()` behavior. `GenStats(std::vector<iovec>&)` duplicates stack-built packet strings but the caller must free those `iov_base` allocations. XML generation uses `snprintf` return lengths without deeply checking available space after each subsystem. `autoSync` trades consistency for lower scheduler pressure when activity exceeds 30. If `posix_memalign()` fails, `GenStats()` returns a minimal null stats document.

## Test Signals

Tests should validate XML fragments for every option bit, JSON plugin/addon packet framing, dual-destination reporting, callback output, behavior with null buffer allocation, large plugin output, and auto-sync behavior under high scheduler activity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/Xrd/XrdStats.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/Xrd/XrdStats.hh -->
# sources/distributed-fs/xrootd/src/Xrd/XrdStats.hh

## Purpose

`XrdStats.hh` declares the stats aggregation and reporting object used by XRootD server processes. It defines option bitmasks for selecting subsystems and exposes callbacks for on-demand stats delivery. The file was read completely.

## Important APIs, Types, and Functions

Option flags include `XRD_STATS_INFO`, `BUFF`, `LINK`, `POLL`, `PROC`, `PROT`, `SCHD`, `SGEN`, `PLUG`, `ADON`, `SYNC`, `SYNCA`, and `JSON`. Public methods are `Export()`, `Init()`, `Report()`, virtual `Stats()`, and the constructor. Nested abstract `CallBack` supports string and iovec delivery. Private methods generate XML/JSON data and subsystem-specific info/process stats.

## Control Flow

The header models two call paths: scheduled reporting through `Init()`/`Report()` and request-driven reporting through `Stats(CallBack*)`. `GenStats()` is the shared formatter, while `Export()` exposes monitor roll state to plugins via an environment pointer.

## State and Persistence Behavior

State includes UDP destinations, scheduler/log/buffer/monitor pointers, a mutex-protected reusable buffer, formatted header strings, option masks, and server identity metadata. `tBoot` is static boot-time state shared across instances. Destructor frees allocated buffers and header strings.

## Dependencies and Integration Points

Forward declarations keep the header decoupled from `XrdNetMsg`, `XrdMonitor`, scheduler, and buffer manager implementations. It includes `XrdSysPthread.hh` for the stats mutex and `vector` for iovec packet generation.

## Risks and Edge Cases

The virtual `Stats()` exists for packaging/linker reasons, so ABI stability matters. Option bit overlap is intentional: `ALLX` includes XML and JSON-class bits. Consumers must understand that JSON is not supported for client-requested `Stats()` in the implementation.

## Test Signals

Compile and ABI tests should cover plugins that receive `XrdStats` through exported interfaces. Functional tests should check option masks and callback behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/Xrd/XrdStats.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/Xrd/XrdTcpMonPin.hh -->
# sources/distributed-fs/xrootd/src/Xrd/XrdTcpMonPin.hh

## Purpose

`XrdTcpMonPin.hh` defines the TCP post-monitoring plugin interface used when an `XrdLink` connection is about to close. The file was read completely.

## Important APIs, Types, and Functions

The abstract class `XrdTcpMonPin` declares `Monitor(XrdNetAddrInfo&, LinkInfo&, int)`. `LinkInfo` carries trace identity, fd, connection seconds, bytes in, and bytes out. The comments specify that plugins should retrieve the g-stream object from environment key `TcpMon.gStream*` and that instances are obtained through `XrdOucPinObject`.

## Control Flow

There is no implementation control flow. Server link teardown code calls `Monitor()` with network and link summary data. Plugin creation is delegated to the plugin manager.

## State and Persistence Behavior

The interface owns no state. Implementations may emit monitoring records based on the passed snapshot and any environment-provided stream object.

## Dependencies and Integration Points

It forward-declares `XrdNetAddrInfo` and documents integration with `XrdOucPinObject`, `XrdXrootdGStream`, and `XrdVERSIONINFO`. This is an extension point rather than core server logic.

## Risks and Edge Cases

The `liLen` argument is the versioning guard for `LinkInfo`; plugins should validate it before reading newly added fields. Implementations must not assume fd remains usable after teardown begins. Missing environment g-stream should cause plugin load failure per comments.

## Test Signals

Plugin ABI tests should load a sample pin object, verify `getInstance()` behavior with and without the expected environment pointer, and call `Monitor()` with short and full `liLen` values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/Xrd/XrdTcpMonPin.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/Xrd/XrdTrace.hh -->
# sources/distributed-fs/xrootd/src/Xrd/XrdTrace.hh

## Purpose

`XrdTrace.hh` defines trace flags and debug macros for Xrd server subsystems. The file was read completely.

## Important APIs, Types, and Functions

Trace masks include `TRACE_DEBUG`, `TRACE_CONN`, `TRACE_MEM`, `TRACE_NET`, `TRACE_POLL`, `TRACE_PROT`, `TRACE_SCHED`, and TLS-specific flags. When `NODEBUG` is not set, `TRACE(act,x)`, `TRACEI(act,x)`, and `TRACING(x)` expand to `XrdSysTrace` checks and `SYSTRACE()` calls. `XRD_TRACE` defaults to `XrdGlobal::XrdTrace.` unless an implementation overrides it.

## Control Flow

The macros gate debug output at runtime by checking `XRD_TRACE What` against a requested mask. With `NODEBUG`, trace macros compile to no-ops and `TRACING()` is zero.

## State and Persistence Behavior

This header owns no runtime state, but relies on the global or overridden `XrdSysTrace` object. Trace settings persist in that object for process lifetime or until configuration changes.

## Dependencies and Integration Points

It integrates with `XrdSysHeaders.hh`, `XrdSysTrace.hh`, and the `XrdGlobal::XrdTrace` singleton. Source files commonly define `TraceID` and optionally override `XRD_TRACE` before including this header.

## Risks and Edge Cases

Macro syntax depends on `XRD_TRACE` ending with a member-access token. New trace categories must avoid bit collisions, especially TLS composite bits. Code compiled with `NODEBUG` loses trace side effects entirely, so trace expressions must be side-effect free.

## Test Signals

Build tests should cover debug and `NODEBUG` configurations. Runtime tests can verify that setting trace masks enables expected scheduler/network/protocol logs without evaluating disabled trace expressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/Xrd/XrdTrace.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdAcc/CMakeLists.txt -->
# sources/distributed-fs/xrootd/src/XrdAcc/CMakeLists.txt

## Purpose

`XrdAcc/CMakeLists.txt` wires the XrdAcc authorization sources and headers into the `XrdServer` target. The file was read completely.

## Important APIs, Types, and Functions

It calls `target_sources(XrdServer PRIVATE ...)` and lists the access engine, audit object, auth DB interface, authorization plugin interface, auth file implementation, capabilities, configuration, entity attributes, groups, and privilege definitions.

## Control Flow

There is no runtime control flow. During configuration/generation, CMake attaches these files to `XrdServer`.

## State and Persistence Behavior

The build graph state is the only state affected. No installation rule is declared here; installation/export behavior is inherited from higher-level targets.

## Dependencies and Integration Points

This file integrates the XrdAcc module with the server library/executable target. It assumes `XrdServer` exists in the parent CMake scope.

## Risks and Edge Cases

Adding a new XrdAcc file without updating this list will omit it from `XrdServer`. Public header installation, if expected, must be handled elsewhere. Target existence is order-sensitive.

## Test Signals

CMake configure/build tests should validate `XrdServer` compiles with all listed files. Packaging tests should confirm authorization headers are exported as intended by the broader build.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdAcc/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdAcc/XrdAccAccess.cc -->
# sources/distributed-fs/xrootd/src/XrdAcc/XrdAccAccess.cc

## Purpose

`XrdAccAccess.cc` implements the default XRootD authorization engine. It loads the default authorization object, computes privileges for authenticated entities against path capabilities, applies auditing, resolves hosts when needed, and atomically swaps access tables built by configuration. The file was read completely.

## Important APIs, Types, and Functions

`XrdAccDefaultAuthorizeObject()` verifies plugin version compatibility, configures `XrdAccConfiguration`, and returns `Authorization`. `XrdAccAccess::Access()` accumulates capabilities from defaults, domain/host/netgroup/user, group/org/role, and inclusive/exclusive set rules. `Access2()` combines positive and negative masks and audits/tests an operation. `Audit()` maps operations to names and routes grant/deny records. `Resolve()` converts IP-like host strings through `XrdNetAddrInfo`. `SwapTabs()` atomically swaps `XrdAccAccess_Tables`. `Test()` maps `Access_Operation` to required `XrdAccPrivs`. `XrdAccAccess_ID::Applies()` tests set-rule selectors.

## Control Flow

`Access()` starts by creating or retrieving an `XrdAccEntity` attribute iterator. It prefers `Entity->eaAPI` `request.name` over `Entity->name`. It locks `Access_Context` shared, applies exclusive set rules first and returns on the first match, then conditionally resolves the host and accumulates default, host/domain, netgroup, fungible user, specific user, group, org, role, and inclusive set capabilities. The lock is released before `Access2()` tests and audits. Table refresh uses `SwapTabs()` under exclusive lock, then purges group caches.

## State and Persistence Behavior

Authorization tables are process-memory hash tables and lists protected by `XrdSysXSLock`. `hostRefX` and `hostRefY` avoid DNS work unless configured rules require host names. The global config owns the current authorization instance. No privileges persist beyond in-memory config refreshes.

## Dependencies and Integration Points

The file integrates with `XrdAccConfig`, `XrdAccEntity`, `XrdAccCapability`, `XrdAccGroups`, `XrdSecEntity`, `XrdSecEntityAttr`, `XrdNetAddrInfo`, `XrdSysPlugin`, and `XrdOucHashVal2`.

## Risks and Edge Cases

`Test()` declares a `need[]` table only through operation indexes 0-14, but `AOP_LastOp` is 16 and the enum includes `AOP_Stage` and `AOP_Poll`; stage/poll checks can read past the table. `Audit()` assumes `Entity` and `Entity->eaAPI` are valid. Host resolution can be expensive and occurs under the shared access-table lock when exclusive rules need it. Negative privileges are global within accumulated caps and can remove bits granted by other matching rules. Exclusive set rules return immediately on the first match.

## Test Signals

Tests should cover every `Access_Operation`, especially stage and poll; all selector types; exclusive rule ordering; inclusive rule accumulation; negative privilege subtraction; token username override; host-domain matching; DNS resolution gating; audit-on-grant/deny; and hot table swap under concurrent access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdAcc/XrdAccAccess.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdAcc/XrdAccAccess.hh -->
# sources/distributed-fs/xrootd/src/XrdAcc/XrdAccAccess.hh

## Purpose

`XrdAccAccess.hh` declares the default access-control implementation and its table structures. The file was read completely.

## Important APIs, Types, and Functions

`XrdAccAccess_ID` stores named set-rule selectors for name, group, host, org, role, and user plus associated capabilities. `XrdAccAccess_Tables` groups hash tables for groups, hosts, netgroups, orgs, roles, sets, templates, and users, plus domain/default/fungible capability lists and inclusive/exclusive set lists. `XrdAccAccess` implements `XrdAccAuthorize` with `Access()`, `Audit()`, `Test()`, `Resolve()`, and `SwapTabs()`.

## Control Flow

The header captures the table-swap architecture: `XrdAccConfig` builds a fresh `XrdAccAccess_Tables`, then `SwapTabs()` publishes it. `Access()` reads the published tables under `Access_Context`.

## State and Persistence Behavior

`XrdAccAccess_Tables` owns hash/list allocations and deletes them in its destructor. `XrdAccAccess_ID::Export()` transfers owned strings/caps from a stack definition into heap state by nulling the original. `XrdAccAccess` holds current tables, host-resolution flags, the reader-writer lock, and an audit object pointer.

## Dependencies and Integration Points

It depends on audit, authorization, capability, security entity, `XrdOucHash`, `XrdSysXSLock`, and platform types. `XrdAccConfig` is a friend because it needs to set the private auditor and tables.

## Risks and Edge Cases

Ownership semantics are manual and pointer-heavy; incorrect table construction can double-free or leak capabilities. `S_Hash` destructor is expected to delete `SXList` and `SYList`, making list ownership coupled to hash ownership. Public inheritance from `XrdAccAuthorize` means ABI changes affect plugins.

## Test Signals

Unit tests should exercise table construction/destruction, `XrdAccAccess_ID::Applies()`, export ownership transfer, and concurrent `SwapTabs()` with active `Access()` calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdAcc/XrdAccAccess.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdAcc/XrdAccAudit.cc -->
# sources/distributed-fs/xrootd/src/XrdAcc/XrdAccAudit.cc

## Purpose

`XrdAccAudit.cc` implements the default audit sink for authorization decisions. It logs grant/deny records to `XrdSysError` when audit options enable them and exposes a singleton factory. The file was read completely.

## Important APIs, Types, and Functions

The constructor initializes `auditops` to `audit_none` and stores the error destination. `Deny()` formats `"deny"` records when `audit_deny` is enabled. `Grant()` formats `"grant"` records. `XrdAccAuditObject()` returns a static `XrdAccAudit` instance.

## Control Flow

The access layer calls `Grant()` or `Deny()` after an operation test when configured auditing requires a record. Each method formats a bounded 2048-byte stack buffer and emits `mDest->Emsg("Audit", buff)`.

## State and Persistence Behavior

The default audit object is a process-lifetime static. Audit state is limited to the selected option mask and error destination pointer. Audit records persist only as far as the configured logging backend persists them.

## Dependencies and Integration Points

It integrates with `XrdAccAudit.hh` and `XrdSysError`. Sites can replace this default by providing a different audit object in a shared library.

## Risks and Edge Cases

`Grant()` checks `auditops & audit_deny`, not `audit_grant`; this appears to make grant-only auditing ineffective and grant logging dependent on deny auditing. The singleton captures the first `XrdSysError*` passed to the factory. Paths and identities are truncated at the fixed buffer size.

## Test Signals

Tests should verify deny-only, grant-only, all, and none audit modes. A grant-only test should catch the current gate mismatch. Logging tests should cover null trace identity and long path truncation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdAcc/XrdAccAudit.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdAcc/XrdAccAudit.hh -->
# sources/distributed-fs/xrootd/src/XrdAcc/XrdAccAudit.hh

## Purpose

`XrdAccAudit.hh` declares the audit policy enum and default audit base class for authorization decisions. The file was read completely.

## Important APIs, Types, and Functions

`XrdAccAudit_Options` defines `audit_none`, `audit_deny`, `audit_grant`, and `audit_all`. `XrdAccAudit` exposes `Auditing()`, virtual `Deny()` and `Grant()`, `setAudit()`, and a constructor receiving `XrdSysError`. `XrdAccAuditObject()` is the external factory.

## Control Flow

The access engine queries `Auditing()` to decide whether a fast privilege test is enough or whether an audit call is needed. Implementations override `Grant()`/`Deny()` to route records elsewhere.

## State and Persistence Behavior

The class stores an option mask and message destination pointer. No persistent audit store is defined by the interface.

## Dependencies and Integration Points

It forward-declares `XrdSysError` and is used by `XrdAccAccess` and `XrdAccConfig`'s `acc.audit` directive. The comments document replacement by site-specific shared libraries.

## Risks and Edge Cases

The default implementation is intentionally minimal and not sufficient for strict audit requirements. `Auditing(ops)` returns a bitwise intersection, so callers must pass the right mask for their decision.

## Test Signals

Compile tests should cover subclass replacement. Functional tests should validate option parsing and that `Audit()` calls are made only under configured modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdAcc/XrdAccAudit.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdAcc/XrdAccAuthDB.hh -->
# sources/distributed-fs/xrootd/src/XrdAcc/XrdAccAuthDB.hh

## Purpose

`XrdAccAuthDB.hh` defines the abstract authorization database reader interface consumed by `XrdAccConfig`. The file was read completely.

## Important APIs, Types, and Functions

The abstract API is `Open()`, `getRec()`, `getID()`, `getPP()`, `Close()`, and `Changed()`. It also declares `XrdAccAuthDBObject()` as the factory returning the active database provider.

## Control Flow

Configuration opens the database, repeatedly calls `getRec()` for record type/name, then consumes either selector pairs via `getID()` or path/template/privilege entries via `getPP()`, and finally calls `Close()`. Warm refresh checks `Changed()` first.

## State and Persistence Behavior

The interface owns no state, but implementations are expected to serialize enumeration and track source modification state. The documented file syntax supports continuation records, comments, blank lines, typed id records, set definitions, templates, and path privilege pairs.

## Dependencies and Integration Points

It depends on `XrdSysError` for diagnostics. The default implementation is `XrdAccAuthFile`, but alternate database backends can implement the same stream-like contract.

## Risks and Edge Cases

The API returns pointers whose lifetime is implementation-defined, so `XrdAccConfig` must copy data when needed. The single-cursor style means concurrent use requires implementation-level locking. Malformed records must be surfaced through `Close()` returning false.

## Test Signals

Backend tests should cover normal enumeration, malformed records, changed/not-changed detection, missing database paths, continuation syntax, and concurrent open attempts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdAcc/XrdAccAuthDB.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdAcc/XrdAccAuthFile.cc -->
# sources/distributed-fs/xrootd/src/XrdAcc/XrdAccAuthFile.cc

## Purpose

`XrdAccAuthFile.cc` implements the default file-backed authorization database reader. It serializes access to an auth file, tokenizes records with `XrdOucStream`, reports parse errors, tracks modification time for warm refresh, and returns record components to `XrdAccConfig`. The file was read completely.

## Important APIs, Types, and Functions

`XrdAccAuthDBObject()` returns a static `XrdAccAuthFile`. The constructor initializes state and an initial error context. `Open()` sets/uses the database path, stats and opens the file, records `st_mtime`, attaches the fd to `DBfile`, and locks `DBcontext`. `getRec()` returns record type/name. `getID()` reads selector type/value pairs. `getPP()` reads template names or path/privilege pairs. `Changed()` compares paths and mtimes. `Close()` closes the stream, unlocks, and returns parse success. `Bail()` centralizes open failure cleanup. `Copy()` bounded-copies stream words into stable buffers.

## Control Flow

The reader is opened under a mutex and remains locked for the full enumeration. `getRec()` skips invalid records and flushes unconsumed words from prior records. It accepts `g`, `h`, `s`, `n`, `o`, `r`, `t`, `u`, `x`, and `=` record types. `getPP()` treats non-slash words as templates, slash-starting words as paths needing a following privilege string, and backslash-prefixed words as escaped object ids.

## State and Persistence Behavior

State includes auth file path, flags, current record type, last modification time, `XrdOucStream`, mutex, and fixed buffers for record names and paths. Persistent source state is the auth file on disk; in-memory enumeration state is reset per open.

## Dependencies and Integration Points

It depends on `XrdOucStream`, POSIX `open/stat`, `XrdSysError`, and `XrdAccAuthDB`. `XrdAccConfig` consumes this implementation through the abstract factory.

## Risks and Edge Cases

If `Open()` is called with no configured path, it returns through `Bail()` and unlocks. Record and path buffers are bounded by `MAXHOSTNAMELEN` and `MAXPATHLEN`; long tokens are truncated silently by `Copy()`. `Changed()` returns unchanged when `stat()` fails after logging, which can delay recovery from file removal/recreation. Parse errors are accumulated in flags and only fail definitively at `Close()`.

## Test Signals

Tests should cover valid auth files, each record type, templates, escaped object IDs, missing privileges, invalid selectors, invalid record types, long tokens, path changes, mtime changes, missing files, and serialized concurrent opens.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdAcc/XrdAccAuthFile.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdAcc/XrdAccAuthFile.hh -->
# sources/distributed-fs/xrootd/src/XrdAcc/XrdAccAuthFile.hh

## Purpose

`XrdAccAuthFile.hh` declares the file-backed implementation of `XrdAccAuthDB`. The file was read completely.

## Important APIs, Types, and Functions

Public overrides are `Open()`, `getRec()`, `getID()`, `getPP()`, `Close()`, and `Changed()`. Private helpers are `Bail()` and `Copy()`. `DBflags` tracks `inRec`, `isOpen`, and `dbError`.

## Control Flow

The class exposes a streaming reader contract: open the file, read one record at a time, read its selectors or path/priv entries, close and check whether parse errors occurred.

## State and Persistence Behavior

State includes the error route, flags, stream, auth filename, current record type, last mtime, mutex, record-name buffer, and path buffer. `DBcontext` serializes access across callers.

## Dependencies and Integration Points

It includes platform limits, networking constants for `MAXHOSTNAMELEN`, `XrdOucStream`, `XrdSysPthread`, and the abstract auth DB header. It is instantiated by the default factory in the `.cc`.

## Risks and Edge Cases

Fixed-size buffers constrain auth id and path lengths. The path buffer is reused for both path and id values, so callers must copy values before the next token call if they need persistence. `DBflags` is a plain enum used as bit flags and cast after bit operations.

## Test Signals

Compile tests should cover platform definitions of `MAXHOSTNAMELEN` and `MAXPATHLEN`. Runtime tests should validate flag transitions for successful and failed opens and parse failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdAcc/XrdAccAuthFile.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdAcc/XrdAccAuthorize.hh -->
# sources/distributed-fs/xrootd/src/XrdAcc/XrdAccAuthorize.hh

## Purpose

`XrdAccAuthorize.hh` defines the public authorization plugin interface and the operation enum used by XRootD authorization checks. The file was read completely.

## Important APIs, Types, and Functions

`Access_Operation` maps server operations to stable indexes from `AOP_Any` through `AOP_Poll`, with `AOP_LastOp` equal to 16. `XrdAccAuthorize` declares virtual `Access()`, an extended-error overload of `Access()`, `Audit()`, and `Test()`. Function pointer typedefs define plugin factories `XrdAccAuthorizeObject_t`, `XrdAccAuthorizeObject2_t`, and wrapper factory `XrdAccAuthorizeObjAdd_t`.

## Control Flow

Server components call `Access()` with an authenticated `XrdSecEntity`, logical path, and operation. Implementations return a nonzero privilege/permit result or zero deny. For `AOP_Any`, implementations return the privilege mask for later `Test()` calls. Plugin loading obtains an object from an extern C factory or uses the statically linked default.

## State and Persistence Behavior

The interface owns no state. Plugin implementations are typically process-lifetime objects. Extended error strings are caller-owned outputs.

## Dependencies and Integration Points

It depends on `XrdAccPrivs.hh`, `std::string`, `XrdSecEntity`, `XrdOucEnv`, and `XrdSysLogger`. It is a cross-module ABI for authorization plugins, wrapper plugins, and server authorization calls.

## Risks and Edge Cases

The operation enum is positional and comments warn that audit/test tables must remain in one-to-one correspondence. Implementations that omit new enum values can fail or read out of bounds. Factory ABI and version metadata must remain stable for shared plugins.

## Test Signals

ABI tests should load a minimal plugin and wrapper plugin. Behavioral tests should call every operation value, including `AOP_Stage` and `AOP_Poll`, through `Access()` and `Test()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdAcc/XrdAccAuthorize.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdAcc/XrdAccCapability.cc -->
# sources/distributed-fs/xrootd/src/XrdAcc/XrdAccCapability.cc

## Purpose

`XrdAccCapability.cc` implements path capability matching and named domain/template capability lists for the authorization engine. The file was read completely.

## Important APIs, Types, and Functions

The `XrdAccCapability(char*, XrdAccPrivCaps&)` constructor stores a path, hash, privilege masks, and optional `@=` substitution position. The template constructor is defined inline in the header. The destructor deletes the rest of a capability chain. `Privs()` walks a chain, follows template pointers, matches path prefixes or substituted prefixes, and ORs positive/negative masks into a caller-provided accumulator. `Subcomp()` performs `@=` substitution comparison. `XrdAccCapName::~XrdAccCapName()` deletes named lists. `XrdAccCapName::Find()` returns the capability list for the longest suffix-style domain/name match.

## Control Flow

Authorization calls `Privs()` on candidate capability lists. The first matching capability in a chain applies and returns success. Template capabilities delegate to their referenced capability list. Domain lists use `Find()` to compare configured suffix names against the end of the target name.

## State and Persistence Behavior

Capability state is immutable after construction: path string, path length/hash, privilege masks, substitution indices, next pointer, and optional template pointer. Named lists store name strings and capability-list ownership. All state is in memory and rebuilt on auth DB refresh.

## Dependencies and Integration Points

It depends on `XrdAccPrivs`, C string functions, and external `XrdOucHashVal2`. It is used by config table construction and access privilege accumulation.

## Risks and Edge Cases

The stored `pkey` is computed but not used in the observed matching path, leaving prefix checks string-based. `Privs()` stops after the first match in a chain, so ordering of configured path capabilities matters. `@=` substitution matching requires a prefix, inserted substitute, and tail; malformed or unexpected substitute values can deny intended access. Destructor chain ownership requires callers to detach before deleting subchains.

## Test Signals

Tests should cover exact prefix matches, non-matches, chain order, template delegation, positive/negative mask ORing, `@=` substitution, domain suffix lookup, and destructor behavior for multi-node chains.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdAcc/XrdAccCapability.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdAcc/XrdAccCapability.hh -->
# sources/distributed-fs/xrootd/src/XrdAcc/XrdAccCapability.hh

## Purpose

`XrdAccCapability.hh` declares capability chains and named capability lists used by XRootD authorization tables. The file was read completely.

## Important APIs, Types, and Functions

`XrdAccCapability` exposes `Add()`, `Next()`, three `Privs()` overloads, `Subcomp()`, a concrete path/privilege constructor, a template-reference constructor, and a destructor. `XrdAccCapName` maps a name/domain suffix to a capability list with `Add()` and `Find()`.

## Control Flow

Configured records become chains of capabilities. At access time, the authorization engine calls `Privs()` with a path and optional substitution string to merge privileges from the first matching capability or template.

## State and Persistence Behavior

Each capability owns either a concrete path/privilege record or a template pointer. Chain ownership is intrusive through `next`; deleting a node deletes all following nodes. `XrdAccCapName` similarly owns a linked list and the capability lists associated with names.

## Dependencies and Integration Points

It depends on `XrdAccPrivs.hh` and C string allocation. The config loader creates these objects, and `XrdAccAccess` consumes them.

## Risks and Edge Cases

Manual ownership and chain deletion are the main risks. `pathsub` support adds matching complexity. Because matching is prefix-based, configuration must distinguish file and directory path prefixes carefully.

## Test Signals

Tests should validate all constructors, list addition, suffix-name lookup, path prefix matching, substitution matching, and deletion without leaks or double frees.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdAcc/XrdAccCapability.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdAcc/XrdAccConfig.cc -->
# sources/distributed-fs/xrootd/src/XrdAcc/XrdAccConfig.cc

## Purpose

`XrdAccConfig.cc` implements default authorization system configuration. It parses `acc.*` directives, chooses an auth DB path, periodically refreshes the authorization database, converts DB records into access tables and capability chains, configures audit/group options, and publishes refreshed tables to `XrdAccAccess`. The file was read completely.

## Important APIs, Types, and Functions

The global `XrdAccConfiguration` is the singleton config object. `XrdAccConfig_Refresh()` runs periodic warm refresh. The constructor picks `/opt/xrd/etc/Authfile` or `/etc/xrootd/authdb` if readable and sets defaults. `Configure()` creates `XrdAccAccess`, parses config, loads DB, and starts the refresh thread. `ConfigDB()` creates fresh hashes, reads records, validates and swaps tables. `ConfigFile()` scans config directives. `ConfigXeq()` dispatches directives. Directive handlers include `xaud`, `xart`, `xdbp`, `xenc`, `xglt`, `xgrt`, `xnis`, and `xspc`. `ConfigDBrec()` builds capabilities for each auth DB record. `idDef()` and `idChk()` handle set selectors and inclusive/exclusive ordering. `PrivsConvert()` maps privilege characters to masks.

## Control Flow

Startup calls `Configure()`: parse config, load database cold, and start refresh. The refresh thread sleeps `AuthRT` seconds and calls `ConfigDB(1)`, which returns early if `Database->Changed()` says unchanged. DB records are streamed one at a time. Normal id records build capability chains from template references or path/privilege pairs. `=` records define named selector sets, `x` records create exclusive set rules, and `s` records create inclusive set rules. After successful parse, empty hashes are deleted, set lists are ordered, and `Authorization->SwapTabs()` publishes the new tables.

## State and Persistence Behavior

State includes auth DB provider, auth DB path, authorization object, group master, refresh interval, options, current rule number, space substitution char, URI-path decoding flag, config mutex, and refresh thread handle. Persistent state is external config/auth DB files; runtime state is rebuilt into memory on each successful refresh.

## Dependencies and Integration Points

It integrates with `XrdOucStream`, `XrdOucEnv`, `XrdOucUri`, `XrdOuca2x`, `XrdSysThread`, `XrdAccAccess`, `XrdAccAuthDB`, `XrdAccGroups`, `XrdAccAudit`, and `XrdAccCapability`.

## Risks and Edge Cases

`xdbp()` overwrites `dbpath` without freeing an existing value, leaking on repeated config parsing. Refresh thread runs forever and uses the `XrdSysError` pointer passed at startup. Duplicate rules, missing templates, invalid privileges, or unused set definitions are handled through diagnostics and failed refresh. `PrivsConvert()` supports negative privilege transition only once. URI decoding uses stack allocation sized to encoded path length. Warm refresh skips reload if `Changed()` returns false after stat errors.

## Test Signals

Tests should cover all directives, default path selection, cold and warm DB loads, refresh skip/change detection, record types `g/h/n/o/r/t/u/x/=/s`, templates, duplicate detection, exclusive ordering, inclusive accumulation, URI path decoding, space substitution, negative privileges, and concurrent access during table swap.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdAcc/XrdAccConfig.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdAcc/XrdAccConfig.hh -->
# sources/distributed-fs/xrootd/src/XrdAcc/XrdAccConfig.hh

## Purpose

`XrdAccConfig.hh` declares the authorization configuration singleton type and helper structures used to build access tables from config and auth DB sources. The file was read completely.

## Important APIs, Types, and Functions

`XrdAccGlist` is a simple linked list of group names. `XrdAccConfig` exposes `Configure()`, `ConfigDB()`, public `Authorization`, `GroupMaster`, and `AuthRT`. Private helpers cover group list addition, DB record parsing, defaults, config-file execution, set id validation/definition, space substitution, privilege conversion, and directive handlers.

## Control Flow

The public flow is `Configure()` at startup and `ConfigDB()` during refresh. Private directive handlers mutate config options before DB load.

## State and Persistence Behavior

The class owns the database provider pointer, auth DB path, config mutex/thread wrapper, options, current rule number, space encoding char, and URI-path flag. Destructor frees `dbpath`.

## Dependencies and Integration Points

It depends on access, auth DB, capability, groups, `XrdOucStream`, `XrdOuca2x`, `XrdOucHash`, `XrdSysError`, and pthread wrappers. `XrdAccAccess` uses this singleton indirectly through the external `XrdAccConfiguration`.

## Risks and Edge Cases

The singleton design means only one authorization configuration can exist per process. Manual ownership of `dbpath`, capabilities, and hash tables requires care in refresh paths. Private friend-like coupling with `XrdAccAccess` is strong.

## Test Signals

Compile tests should cover all private handler declarations with implementation signatures. Functional tests should validate object construction defaults and repeated configuration/refresh behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdAcc/XrdAccConfig.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdAcc/XrdAccEntity.cc -->
# sources/distributed-fs/xrootd/src/XrdAcc/XrdAccEntity.cc

## Purpose

`XrdAccEntity.cc` compiles authorization-relevant attributes from `XrdSecEntity` into reusable `XrdAccEntity` objects. It tokenizes virtual organization, role, and group strings into aligned attribute combinations and caches the result on the security entity. The file was read completely.

## Important APIs, Types, and Functions

The constructor copies `secP->vorg`, `role`, and `grps`, then builds `attrVec`. `GetEntity()` retrieves cached attributes from `secP->eaAPI` using a static signature or builds a new object. `PutEntity()` attaches a newly built object to the entity or deletes it if another thread won. `OneOrZero()` accepts the short-form case with zero or one VO/role. `setAttr()` advances tokenizers for aligned multi-attribute columns. `setError()` stores a diagnostic destination.

## Control Flow

When access checks start, `XrdAccEntityInit` calls `GetEntity()`. If attributes are already cached, they are reused. If not, a new object tokenizes attributes. The common case of at most one VO and role combines that with each group token. The multi-column case advances VO, role, and group lists together and fails if one list ends early. `XrdAccEntityInit` attaches newly built objects on destruction.

## State and Persistence Behavior

Each entity object owns duplicated source strings and a vector of lightweight `EntityAttr` entries pointing into those strings. Cached objects persist on `XrdSecEntity` via `eaAPI`. `accSig` is a static key for the attribute cache, and `eDest` is a file-local static error pointer.

## Dependencies and Integration Points

It depends on `XrdSecEntity`, `XrdSecEntityAttr`, `XrdSecAttr`, `XrdOucTokenizer`, and `XrdSysError`. `XrdAccAccess` iterates the resulting attributes through `Next()`.

## Risks and Edge Cases

The multi-column mode requires all provided lists to have the same number of tokens; mismatches deny compiled-entity creation and can deny access. Pointers in `attrVec` are valid only while duplicated strings live. Parallel caching relies on `eaAPI->Add()` rejecting duplicates. Tokenization treats spaces as separators after any configured higher-level substitutions.

## Test Signals

Tests should cover no attributes, single VO/role with multiple groups, aligned multi-column VO/role/group lists, mismatched list lengths, cache reuse, parallel creation, and diagnostic emission on invalid attributes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdAcc/XrdAccEntity.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdAcc/XrdAccEntity.hh -->
# sources/distributed-fs/xrootd/src/XrdAcc/XrdAccEntity.hh

## Purpose

`XrdAccEntity.hh` declares the compiled authorization entity attribute cache used during access checks. The file was read completely.

## Important APIs, Types, and Functions

`XrdAccEntityInfo` carries name, host, virtual org, role, and group for rule matching. `XrdAccEntity` derives from `XrdSecAttr` and exposes static `GetEntity()`, `Next()`, `PutEntity()`, and `setError()`. `XrdAccEntityInit` is an RAII helper that obtains an entity and attaches a new one on destruction.

## Control Flow

`Next(int&, XrdAccEntityInfo&)` is the iterator used by `XrdAccAccess`. It updates VO/role/group while caller-provided name and host remain intact. RAII setup/teardown avoids cache insertion races and leaks.

## State and Persistence Behavior

Objects own duplicated source strings and vector entries pointing into those strings. Cached state is attached to `XrdSecEntity` through `eaAPI` and keyed by a static signature.

## Dependencies and Integration Points

It depends on `XrdSecAttr` and forward declarations for tokenizer, security entity, and error routing. It is tightly integrated with `XrdAccAccess`.

## Risks and Edge Cases

The class has a private destructor and lifecycle is tied to the security attribute API. `Next()` does not reset name/host, which is intentional but requires callers to initialize them before iteration. Invalid compiled entities return null and force fallback access behavior.

## Test Signals

Tests should validate iteration semantics, RAII cache insertion, object reuse, and correct preservation of caller-provided name/host.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdAcc/XrdAccEntity.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdAcc/XrdAccGroups.cc -->
# sources/distributed-fs/xrootd/src/XrdAcc/XrdAccGroups.cc

## Purpose

`XrdAccGroups.cc` implements group and netgroup lookup support for authorization. It registers configured group names, resolves Unix group memberships and NIS netgroups, caches lookup results with TTLs, supports primary-only mode, and handles gid retranslation exceptions. The file was read completely.

## Important APIs, Types, and Functions

The global `XrdAccGroupMaster` is the process group helper. `AddName()` and `FindName()` manage interned group/netgroup names. `Groups()` returns relevant Unix groups for a user. `NetGroups()` returns configured netgroups matching user/host/domain. `PurgeCache()` clears both caches. `Retran()` configures gids that must be retranslated. Private `addGroup()` filters Unix groups to configured names. `Dotran()` suppresses cached group names for retran gids. External `XrdAccCheckNetGroup()` is applied across netgroup names.

## Control Flow

Configured auth DB records call `AddName()` to register names and mark whether Unix groups or netgroups are needed. `Groups()` first checks the TTL cache, then uses `XrdSysPwd`, primary gid, and optionally `getgrent()` to build a filtered list while holding `Group_Build_Context` around non-thread-safe group APIs. `NetGroups()` builds `user@host` cache keys, applies `innetgr()` to each configured netgroup, caches the result, and returns a copy.

## State and Persistence Behavior

State is in memory: registered group/netgroup name hashes, result caches, mutexes, retran gid list, NIS domain pointer, options, feature flags, and TTL. Caches are purged on authorization table swap. No durable group state is stored by this module.

## Dependencies and Integration Points

It depends on POSIX password/group APIs, `innetgr`, `XrdSysPwd`, `XrdOucHash`, `XrdAccGroups.hh`, and authorization config. MUSL builds stub `innetgr()` to always return false.

## Risks and Edge Cases

`XrdAccGroupList` construction in the header caps copy count to `NGROUPS_MAX` but uses the original `cnt` when zeroing the tail, which can write out of bounds if `cnt > NGROUPS_MAX`. `Retran()` checks `retrancnt > capacity`, allowing `retrancnt == capacity` to write one past the array. Cache entries store empty lists too, and callers receive null for no groups. Unix group enumeration is expensive and serialized. MUSL lacks netgroup support here.

## Test Signals

Tests should cover primary group only, supplementary groups, configured-name filtering, cache hits and purges, TTL expiry, `gidretran`, too many groups/netgroups, NIS domain behavior, MUSL netgroup stubbing, and boundary counts at `NGROUPS_MAX` and retran capacity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdAcc/XrdAccGroups.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdAcc/XrdAccGroups.hh -->
# sources/distributed-fs/xrootd/src/XrdAcc/XrdAccGroups.hh

## Purpose

`XrdAccGroups.hh` declares group-list containers and the group/netgroup lookup manager used by authorization. The file was read completely.

## Important APIs, Types, and Functions

`XrdAccGroupList` wraps up to `NGROUPS_MAX` group name pointers with `First()`, `Next()`, and `Reset()`. `XrdAccGroups_Options` defines `Primary_Only` and debug flags. `XrdAccGroupType` distinguishes Unix groups and netgroups. `XrdAccGroups` exposes domain, name registration/lookup, `Groups()`, `NetGroups()`, cache purge, gid retranslation, domain/lifetime/options setters, and constructor.

## Control Flow

`XrdAccConfig` registers group names while parsing DB records. `XrdAccAccess` calls `Groups()` and `NetGroups()` only when matching configured group or netgroup privileges.

## State and Persistence Behavior

`XrdAccGroups` owns in-memory name hashes and TTL caches protected by separate mutexes. It also stores up to 128 retran gids, domain, lifetime, options, and feature flags. The group list object stores pointers to interned names rather than owning strings.

## Dependencies and Integration Points

It depends on `<grp.h>`, platform `NGROUPS_MAX`, `XrdOucHash`, and pthread wrappers. It is used by `XrdAccConfig` and `XrdAccAccess`.

## Risks and Edge Cases

`XrdAccGroupList` copies at most `NGROUPS_MAX` entries but its zero-fill uses `cnt`, not the clamped count, if a larger count is supplied. Returned group names rely on interned-name lifetime. Cache validity depends on explicit purge and TTL.

## Test Signals

Tests should cover iteration, copy construction, empty lists, max-size lists, over-max inputs, cache option setters, and use with both Unix group and netgroup name tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdAcc/XrdAccGroups.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdAcc/XrdAccPrivs.hh -->
# sources/distributed-fs/xrootd/src/XrdAcc/XrdAccPrivs.hh

## Purpose

`XrdAccPrivs.hh` defines the authorization privilege bit masks, auth DB privilege characters, and positive/negative privilege accumulator used by XrdAcc. The file was read completely.

## Important APIs, Types, and Functions

`XrdAccPrivs` assigns bit masks for delete, insert, lock, lookup, rename, read, write, stage, poll, composites like chmod/chown/create/update, `All`, and `None`. `XrdAccPrivSpec` maps auth DB characters such as `a`, `d`, `i`, `k`, `l`, `n`, `r`, `w`, and `-`. `XrdAccPrivCaps` stores `pprivs` and `nprivs`.

## Control Flow

There is no executable flow. `XrdAccConfig::PrivsConvert()` parses privilege strings into `XrdAccPrivCaps`; `XrdAccCapability::Privs()` accumulates them; `XrdAccAccess::Access2()` computes `pprivs & ~nprivs`; `Test()` maps operations to required masks.

## State and Persistence Behavior

The file defines compile-time constants and a tiny stack/heap accumulator struct. No persistent state is owned.

## Dependencies and Integration Points

It is included by the authorization interface, capability engine, and config parser. Its bit assignments are an internal ABI for auth DB interpretation.

## Risks and Edge Cases

Composite masks must remain aligned with `Access_Operation` tests. Stage and poll masks exist here, but the observed `XrdAccAccess::Test()` table omits corresponding operation entries. Negative privilege strings can remove bits granted by unrelated matching capabilities.

## Test Signals

Tests should validate conversion of every privilege character, composites for each operation, negative privilege subtraction, and stage/poll authorization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdAcc/XrdAccPrivs.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdApps/CMakeLists.txt -->
# sources/distributed-fs/xrootd/src/XrdApps/CMakeLists.txt

## Purpose

`XrdApps/CMakeLists.txt` defines XRootD application utilities, client plugins, replay tooling, and optional non-client-only executables. The file was read completely.

## Important APIs, Types, and Functions

It builds shared library `XrdAppUtils` from copy/config and multiplexed XML helpers, module plugins `${XrdClProxyPlugin}` and `${XrdClRecorder}`, executable `xrdreplay`, and, when `NOT XRDCL_ONLY`, tools such as `cconfig`, `mpxstats`, `wait41`, `xrdacctest`, `xrdadler32`, `xrdcks`, `xrdcrc32c`, `xrdmapc`, `xrdpinls`, `xrdprep`, and `xrdqstats`. It sets SOVERSION/VERSION for `XrdAppUtils` and installation targets.

## Control Flow

CMake first defines common app utilities and client-side plugins, then installs them. The `NOT XRDCL_ONLY` block adds server/full-build utilities and installs a subset of them.

## State and Persistence Behavior

This file mutates the CMake build graph and install manifest. There is no runtime state.

## Dependencies and Integration Points

Targets link against `XrdUtils`, `XrdCl`, `XrdServer`, `XrdPosix`, `XrdAppUtils`, `ZLIB::ZLIB`, thread libs, socket library, and `${EXTRA_LIBS}`. Plugin names include `${PLUGIN_VERSION}`, so packaging layout depends on global version variables.

## Risks and Edge Cases

Some executables are defined but not included in the shown install list (`xrdprep` and `xrdqstats` are built after the listed install block starts but are not in its target list here), which may be intentional or an install omission. Conditional `XRDCL_ONLY` builds must not reference server-only libraries. Link dependencies must stay consistent with source additions.

## Test Signals

CMake tests should cover full and `XRDCL_ONLY` configurations, plugin filename/version generation, installation manifests, and link success for each executable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdApps/CMakeLists.txt -->
