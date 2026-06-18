# Research Group: subset-b-007926

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClSocket.hh -->
# sources/distributed-fs/xrootd/src/XrdCl/XrdClSocket.hh

## Purpose

This header declares `XrdCl::Socket`, the client-side network socket abstraction used by asynchronous stream handlers and the TLS layer. It wraps a file descriptor, connection state, address/name caching, raw read/write operations, socket options, poll-based readiness, corking, TLS handshakes, and event mapping.

## Important APIs, Types, and Functions

`SocketStatus` distinguishes disconnected, connected, and connecting states. Construction can adopt an existing descriptor or start disconnected. `Initialize`, `Connect`, `ConnectToAddress`, `Close`, `Poll`, `ReadRaw`, and `WriteRaw` form the blocking/raw I/O surface. `Send` has overloads for plain buffers, `XrdSys::KernelBuffer`, and XrdCl `Message`. `Read`, `ReadV`, and `ClassifyErrno` provide lower-level helpers that map transient `EAGAIN`/`EWOULDBLOCK` to retry statuses. TLS-specific methods are `TlsHandShake`, `IsEncrypted`, `MapEvent`, `Cork`, `Uncork`, and `Flash`.

## Control Flow

The typical flow is initialize or adopt a descriptor, connect to a host or resolved `XrdNetAddr`, then let `AsyncSocketHandler` drive `Read`, `ReadV`, and `Send` through poller callbacks. `Poll` guards timeout and readiness decisions for raw reads/writes. If TLS is enabled, the socket delegates reads/writes/event mapping to `Tls`, and corking is used to handle SSL/TLS write limitations around vector writes.

## State and Persistence Behavior

State is in memory only: descriptor, status, server address, cached local/peer/name strings, protocol family, channel ID pointer, corked flag, and optional `Tls` object. There is no persistence; descriptor ownership and close timing are the main lifecycle concerns.

## Dependencies and Integration Points

The header integrates with `XrdClXRootDResponses` for `XRootDStatus`, `XrdNetAddr` for resolved endpoints, `XrdSysKernelBuffer`, `Message`, `AnyObject` channel IDs, `Tls`, and `AsyncSocketHandler`. It is consumed by `Stream`, socket handlers, and TLS handshake code.

## Risks and Edge Cases

Correctness depends on the implementation consistently mapping errno and socket readiness into retryable versus fatal statuses. TLS event remapping can invert read/write readiness during handshakes, so poller callbacks must honor `MapEvent`. Cached name fields are mutable and can become stale after reconnects unless invalidated by implementation code. Callers can manually mutate status through `SetStatus`, which is intentionally dangerous.

## Test Signals

Useful signals include connection timeout tests, nonblocking `EAGAIN` retry behavior, remote disconnect classification, SIGPIPE-free send behavior, cork/uncork behavior, and TLS handshake/event-remap integration through `AsyncSocketHandler`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClSocket.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClStatus.cc -->
# sources/distributed-fs/xrootd/src/XrdCl/XrdClStatus.cc

## Purpose

This implementation provides the string conversion logic for the lightweight `XrdCl::Status` type. It translates internal XrdCl error codes and optional errno/XRootD protocol error numbers into operator-readable messages.

## Important APIs, Types, and Functions

The private `ErrorMap errors[]` table maps XrdCl error constants such as `errSocketTimeout`, `errAuthFailed`, `errCheckSumError`, and `errTlsError` to short messages. `GetErrorMessage` performs a linear lookup and falls back to "Unknown error code". `Status::ToString()` formats success, nonfatal error, and fatal error prefixes and appends decoded OS/protocol errors.

## Control Flow

`ToString` first checks `IsOK()`. Success returns `[SUCCESS]` plus `Continue` or `Retry` when the status code is `suContinue` or `suRetry`. Error statuses are prefixed with `[FATAL]` or `[ERROR]`, then the mapped error text. If `errNo` is at or above `kXR_ArgInvalid`, the code treats it as an XRootD protocol error and converts through `XProtocol::toErrno`; otherwise nonzero values are passed directly to `XrdSysE2T`.

## State and Persistence Behavior

The file has only static read-only mapping data. It does not persist state or mutate global configuration.

## Dependencies and Integration Points

It depends on `XrdClStatus.hh`, `XrdSysE2T` for errno text, and `XProtocol` constants/conversion. It is a common diagnostic path for many client components that return `Status`.

## Risks and Edge Cases

The mapping is manually maintained; new error constants can stringify as unknown if this table is not updated. The `errNo >= kXR_ArgInvalid` heuristic is explicitly compensating for inconsistent use of protocol errors versus errno, so boundary regressions can produce misleading text. Success with `suPartial`, `suAlreadyDone`, or other success hints prints only `[SUCCESS]`.

## Test Signals

Tests should cover representative generic, socket, auth, redirect, checksum, and TLS errors; fatal versus nonfatal prefixes; success hints; unknown codes; and errno/protocol conversion behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClStatus.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClStatus.hh -->
# sources/distributed-fs/xrootd/src/XrdCl/XrdClStatus.hh

## Purpose

This header defines the compact status vocabulary used throughout older XrdCl code: status severity bits, success subcodes, error-code ranges, and the `Status` structure.

## Important APIs, Types, and Functions

Constants define severity (`stOK`, `stError`, `stFatal`), success hints (`suDone`, `suRetry`, `suPartial`, and others), generic errors, socket errors, postmaster errors, XRootD protocol errors, and query/redirect response errors. `Status` stores `status`, `code`, and `errNo`; exposes `IsError`, `IsFatal`, `IsOK`, `GetShellCode`, `IsSocketError`, and `ToString`.

## Control Flow

Callers construct `Status` with defaults for success or with an error severity and code. `IsError` tests the error bit; `IsFatal` tests the fatal bit; `GetShellCode` collapses grouped error ranges into shell exit values by returning `(code / 100) + 50`.

## State and Persistence Behavior

`Status` is a plain value type with no ownership, dynamic allocation, or persistence. It is intended to move through call returns and callbacks.

## Dependencies and Integration Points

The header depends only on C++ standard headers and is included by transport, stream, URL, task, and utility code. Many newer APIs in this tree use the richer `XRootDStatus`, but the same constants and semantic categories are shared.

## Risks and Edge Cases

The severity encoding is bit-based and easy to misuse if callers compare exact values instead of using helpers. `IsFatal()` uses `(status & 0x0002) & stFatal`, which works for current constants but is less clear than checking the fatal bit directly. Adding new error groups affects shell-code behavior.

## Test Signals

Useful tests validate bit semantics, shell-code grouping, socket-code detection, default OK construction, and stringification through `Status.cc`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClStatus.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClStream.cc -->
# sources/distributed-fs/xrootd/src/XrdCl/XrdClStream.cc

## Purpose

This file implements `XrdCl::Stream`, the postmaster connection/session engine for a server channel. It manages one control socket plus optional data substreams, outgoing and incoming message queues, reconnect logic, stream TTL handling, failure reporting, monitoring, and synchronization between poller callbacks and close operations.

## Important APIs, Types, and Functions

Private helpers include `InMessageHelper`, `SubStreamData`, `SocketDestroyJob`, and `StreamConnectorTask`. `StreamMutex` implements a recursive, callback-aware lock that can abort substream callback lock acquisition while a close is pending. Public behavior is implemented by `Initialize`, `EnableLink`, `Send`, `ForceConnect`, `Finalize`, `Tick`, `OnIncoming`, `OnReadyToWrite`, `OnMessageSent`, `OnConnect`, `OnConnectError`, `OnError`, `ForceError`, timeout handlers, handler registration, incoming-handler installation, `InspectStatusRsp`, `CanCollapse`, and `Query`.

## Control Flow

`Initialize` creates substream 0. `Send` validates session IDs, asks the transport to choose a path, calls `EnableLink`, and queues the message. `EnableLink` either enables the connected uplink or resolves host addresses and starts an async connect. `OnConnect` marks streams connected, assigns a new session for stream 0, creates extra substreams, starts their connects, emits monitor events, and invokes connect handlers. `OnReadyToWrite` moves an item from the out queue into the incoming queue, and `OnMessageSent` finalizes transport accounting and status callbacks. `OnIncoming` routes reconstructed responses through transport handling, close-request handling, partial-response handling, and job-manager dispatch.

Error flow reinserts in-flight helpers when possible, moves peripheral substream work back to stream 0, retries addresses within connection windows, schedules reconnect tasks, and escalates unrecoverable failures via `OnFatalError`. Stream-0 loss resets the session and reports stateful queued work plus incoming handlers as broken.

## State and Persistence Behavior

All state is process-local: URL pointers, preferred URL, transport/poller/task/job managers, `InQueue`, channel data, substream list, resolved addresses, connection windows/retry counters, last fatal error, session ID, byte counters, channel event handlers, and optional data-stream connect job. There is no disk persistence, but session IDs protect stale stateful messages across reconnects.

## Dependencies and Integration Points

The implementation integrates `AsyncSocketHandler`, `Socket`, `Channel`, `TransportHandler`, `OutQueue`, `InQueue`, `JobManager`, `TaskManager`, `Monitor`, `PostMaster`, `XRootDTransport`, and XRootD message utilities. It is central to all networked client operations.

## Risks and Edge Cases

This is concurrency-sensitive code. `SockHandlerClose` replaces handlers while coordinating with poller callbacks; incorrect locking can deadlock or use freed sockets. Retry behavior depends on connection window, retry count, address ordering, and fatal classification. `OnReadTimeout` may destroy the stream/channel through postmaster disconnect, so callers must honor its boolean return. Partial-response and raw-handler paths must reset timeout fences correctly or requests can hang or expire incorrectly.

## Test Signals

Strong signals include connection to multiple resolved addresses, preferred-address collapse behavior, substream fallback to stream 0, stateful-message invalid-session rejection after reconnect, TTL disconnect, stream-broken and fatal-error event delivery, timeout reporting, partial response handling, and cancellation-safe forced disconnects under poller activity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClStream.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClStream.hh -->
# sources/distributed-fs/xrootd/src/XrdCl/XrdClStream.hh

## Purpose

This header declares the stream/session abstraction and its specialized mutex. It defines how postmaster code sends messages over multiplexed sockets and receives connection, response, timeout, and error callbacks from socket handlers.

## Important APIs, Types, and Functions

`StreamMutex` exposes regular locking, substream-aware locking, deferred close-function locking, and close notifications. `StreamMutexHelper` is the RAII wrapper. `Stream` declares status values, dependency setters, `Initialize`, `Send`, `EnableLink`, `Finalize`, `Tick`, `ForceConnect`, substream callbacks, error callbacks, event-handler management, incoming-handler install/inspection, data-stream on-connect hooks, `CanCollapse`, `Query`, and channel lifetime access.

## Control Flow

Callers construct a stream for a URL, inject transport, poller, queues, task/job managers, and channel data, then call `Initialize`. `Send` and `EnableLink` are the outbound entry points. The `AsyncSocketHandler` calls back into `OnConnect`, `OnReadyToWrite`, `OnMessageSent`, `OnIncoming`, and timeout/error methods. Private helpers handle partial responses, address matching, requeueing failed in-flight work, monitoring disconnects, request-close follow-up, and socket-handler replacement.

## State and Persistence Behavior

The header defines the state held by a stream: URL identity, transport dependencies, mutex, queue dependencies, channel data, retry/error windows, substreams, resolved addresses, network-stack choice, session ID, monitoring timestamps/byte counters, optional on-data-connect job, and weak owning channel reference. It is nonpersistent and tied to channel lifetime.

## Dependencies and Integration Points

It depends on poller, status, URL, postmaster interfaces, channel event handlers, job manager, in queue, utility/network types, atomics, pthread IDs, and transport/message classes. It is the primary integration contract between `Channel`, `AsyncSocketHandler`, `TransportHandler`, and queue managers.

## Risks and Edge Cases

The header documents a subtle lock contract: close must wait for poller callbacks unless running inside the callback thread, and callback lock acquisition can be aborted. Implementers must preserve this behavior when adding callbacks. Public callbacks are callable from poller/job contexts, so ownership and unlock-before-report patterns are critical.

## Test Signals

Header-level coverage should be indirect: compile-time API compatibility, stream lifecycle integration tests, lock stress tests around close and callbacks, and query/event-handler behavior through postmaster/channel tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClStream.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClSyncQueue.hh -->
# sources/distributed-fs/xrootd/src/XrdCl/XrdClSyncQueue.hh

## Purpose

This header implements `SyncQueue<Item>`, a small blocking FIFO queue protected by an XRootD mutex and semaphore. It is a generic producer/consumer helper for thread handoff.

## Important APIs, Types, and Functions

`Put` pushes an item while holding `pMutex` and posts `pSem`. `Get` waits on the semaphore, locks, aborts if the queue is unexpectedly empty, pops, and returns the front item. `Clear` drops queued items and replaces the semaphore with a new zero-count semaphore. `IsEmpty` checks the queue under lock.

## Control Flow

Producers call `Put`; consumers block in `Get` until a posted item exists. The semaphore count mirrors queued item count unless `Clear` is called, which resets both queue contents and semaphore state.

## State and Persistence Behavior

State is in memory: `std::queue<Item>`, `XrdSysMutex`, and a heap-allocated `XrdSysSemaphore`. There is no persistence. Queue elements are copied by value.

## Dependencies and Integration Points

The class depends on `XrdSysPthread.hh` for mutex/semaphore primitives and C++ `std::queue`. It can be used by any XrdCl component that needs synchronous handoff without depending on the job manager.

## Risks and Edge Cases

`Clear` deletes and recreates the semaphore while only holding `pMutex`; a consumer already blocked in `Get` on the old semaphore can be stranded or race with deletion if external synchronization is not used. `Get` aborts the process on impossible semaphore/queue mismatch. There is no shutdown sentinel or timed wait.

## Test Signals

Tests should cover single and multiple producers/consumers, ordering, `IsEmpty`, and explicit `Clear` behavior only when no consumer is concurrently blocked.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClSyncQueue.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClTPFallBackCopyJob.cc -->
# sources/distributed-fs/xrootd/src/XrdCl/XrdClTPFallBackCopyJob.cc

## Purpose

This file implements `TPFallBackCopyJob`, a copy job wrapper that prefers third-party copy and falls back to classic streaming copy only for configured, retryable TPC support failures.

## Important APIs, Types, and Functions

The constructor logs source and target. The destructor deletes the currently allocated delegate job. `Run` reads the `thirdParty` property, creates a `ThirdPartyCopyJob`, runs it, and conditionally replaces it with `ClassicCopyJob`.

## Control Flow

If `thirdParty` is `"first"`, fallback is enabled. `Run` executes TPC first. Success returns immediately. If fallback is enabled and TPC returns `errNotSupported` or `errOperationExpired`, the wrapper logs the downgrade, deletes the TPC job, creates a classic streaming job, and runs it with the same progress handler. All other TPC failures are returned unchanged.

## State and Persistence Behavior

The wrapper owns one heap-allocated `CopyJob *pJob` at a time. It shares the base job ID, property list, and results list with the delegated job. No state is persisted outside those result properties.

## Dependencies and Integration Points

It integrates `CopyJob`, `ThirdPartyCopyJob`, `ClassicCopyJob`, `PropertyList`, copy progress handlers, logging, default environment, and status codes. It is selected by copy-process configuration when TPC-first behavior is requested.

## Risks and Edge Cases

Fallback is intentionally narrow. Authentication failures, checksum failures, destination open failures that are not normalized to `errNotSupported`, and most protocol errors do not fall back. Reusing the same property and result lists means partial TPC side effects may be visible to the classic job unless other code clears them.

## Test Signals

Tests should inject TPC success, `errNotSupported`, `errOperationExpired`, and unrelated errors, verifying which path runs and that progress/results are forwarded consistently.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClTPFallBackCopyJob.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClTPFallBackCopyJob.hh -->
# sources/distributed-fs/xrootd/src/XrdCl/XrdClTPFallBackCopyJob.hh

## Purpose

This header declares the fallback copy job type used when copy configuration wants to try third-party copy before streaming.

## Important APIs, Types, and Functions

`TPFallBackCopyJob` derives from `CopyJob`. It exposes a constructor accepting job ID, properties, and results; a virtual destructor; and `Run(CopyProgressHandler*)`. The only member is the owned delegate `CopyJob *pJob`.

## Control Flow

The header establishes the polymorphic `CopyJob` contract. Implementation code chooses the concrete delegate at runtime and forwards `Run` calls.

## State and Persistence Behavior

State is limited to an owned delegate pointer. Job properties/results are non-owned pointers inherited from `CopyJob`.

## Dependencies and Integration Points

It includes copy-process and copy-job interfaces. Copy orchestration code can treat this class as a normal `CopyJob`.

## Risks and Edge Cases

The raw pointer requires destructor and replacement code to remain exception-safe and avoid leaks. The class is not copy-safe and does not declare deleted copy operations.

## Test Signals

Compile/link tests plus runtime fallback tests in the `.cc` file are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClTPFallBackCopyJob.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClTaskManager.cc -->
# sources/distributed-fs/xrootd/src/XrdCl/XrdClTaskManager.cc

## Purpose

This file implements a single-threaded scheduled task runner. It runs short `Task` objects at requested times, supports self-rescheduling tasks, asynchronous unregister requests, and start/stop lifecycle around a pthread runner.

## Important APIs, Types, and Functions

`RunRunnerThread` is the pthread entry point. `Start` creates the runner and protects lifecycle with `pOpMutex`. `Stop` cancels and joins the runner. `RegisterTask` inserts a `TaskHelper` into the multiset. `UnregisterTask` queues a task pointer for later removal. `RunTasks` is the infinite scheduler loop.

## Control Flow

The runner disables cancellation while holding and processing task state. Each loop removes queued unregister requests, selects all tasks with `execTime <= now`, erases them from the active set, unlocks, and calls `Task::Run(now)` for each. A nonzero return value is treated as the next schedule time and reinserted; zero means complete and owned tasks are deleted. Cancellation is re-enabled only during the sleep interval.

## State and Persistence Behavior

State is in memory: resolution seconds, scheduled task multiset, unregister list, runner thread ID, running flag, and mutexes. Ownership is tracked per task. No task state is persisted by the manager.

## Dependencies and Integration Points

It depends on XrdSys mutex/timer/error text utilities, logging/default environment, constants, pthreads, and `Utils::TimeToString`. `Stream` uses it to schedule reconnect attempts through `StreamConnectorTask`.

## Risks and Edge Cases

The destructor deletes scheduled owned tasks but does not stop a running thread, so lifecycle users must call `Stop` before destruction. `Stop` uses pthread cancellation, so long-running `Task::Run` calls delay shutdown. `UnregisterTask` is asynchronous and does not interrupt a task already selected to run. `TaskHelperCmp` compares only execution time, so equal-time tasks rely on multiset equivalence handling and cannot be uniquely found by comparator alone.

## Test Signals

Tests should cover start/stop, one-shot deletion, rescheduling, unregister before execution, non-owned task retention, same-time task ordering/count, and delayed shutdown while a task is running.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClTaskManager.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClTaskManager.hh -->
# sources/distributed-fs/xrootd/src/XrdCl/XrdClTaskManager.hh

## Purpose

This header declares `Task`, the scheduled-work interface, and `TaskManager`, a simple one-thread delayed task scheduler used by client infrastructure.

## Important APIs, Types, and Functions

`Task::Run(time_t now)` returns zero to complete or a timestamp for rerun. Tasks also carry a name for logging. `TaskManager` exposes `Start`, `Stop`, `RegisterTask`, `UnregisterTask`, and `RunTasks`. Private `TaskHelper` stores task pointer, execution time, and ownership; `TaskHelperCmp` orders scheduled tasks.

## Control Flow

Clients register tasks with a target execution time. The manager thread repeatedly scans due tasks, runs them, reinserts rescheduled tasks, and deletes owned completed tasks. Unregistration requests are queued for the runner loop to process.

## State and Persistence Behavior

The manager keeps scheduled tasks and unregister requests in memory. Ownership is explicit per registration. There is no persistence or cross-process coordination.

## Dependencies and Integration Points

It depends on C time containers, pthread IDs, and `XrdSysMutex`. It is used by stream/postmaster logic for delayed reconnect and can support other short client tasks.

## Risks and Edge Cases

The header warns that one task can interfere with another because only one worker thread exists. Long tasks block all later scheduled work. The API does not return cancellation completion or registration handles, so pointer identity is the only unregister key.

## Test Signals

Compile-time signals should verify subclassing `Task`; runtime tests should validate owned versus non-owned deletion, reschedule timestamps, and unregister semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClTaskManager.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClThirdPartyCopyJob.cc -->
# sources/distributed-fs/xrootd/src/XrdCl/XrdClThirdPartyCopyJob.cc

## Purpose

This file implements XrdCl third-party copy. It validates whether a copy can run remotely, configures destination/source TPC CGI parameters, supports delegated TPC-lite, runs the copy through `File::Sync`, reports progress and cancellation, closes resources, and optionally verifies checksums.

## Important APIs, Types, and Functions

Private helpers include `TPCStatusHandler`, which waits for async sync completion via semaphore; `InitTimeoutCalc`, which tracks remaining initial timeout; and `UpdateErrMsg`, which annotates status messages. Main methods are `Run`, `CanDo`, `RunTPC`, `RunLite`, and `GenerateKey`.

## Control Flow

`Run` calls `CanDo`, dispatches to TPC-lite or vanilla TPC, then performs checksum verification for configured modes. `CanDo` rejects local files and non-root targets, reads job properties (`initTimeout`, checksum settings, `force`, `coerce`, `delegate`), opens the source when possible to resolve actual URL and size, merges original source CGI with redirector CGI, enables or disables delegation, builds destination TPC CGI with `XrdOucTPC::cgiC2Dst`, opens the destination with update/new/delete/force flags, checks destination TPC-lite support, optionally checks source TPC support, and records the remaining init timeout.

`RunTPC` builds source CGI with `cgiC2Src`, syncs the destination rendezvous, opens the source, starts async destination sync, periodically stats the destination for progress, can issue `ofs.tpc cancel`, waits for completion, closes both files, and stores size. `RunLite` follows the destination-only delegated flow. Checksum verification can use preset, metalink redirector checksum, or remote checksum queries and emits monitor checksum events.

## State and Persistence Behavior

State is per-job: destination `File`, resolved `tpcSource`, `realTarget`, rendezvous key, checksum settings, source size, init timeout, copy flags, delegation flag, stream count, and `tpcLite`. Results are persisted only in the provided `PropertyList` keys such as `size`, `sourceCheckSum`, and `targetCheckSum`.

## Dependencies and Integration Points

The implementation integrates copy framework classes, `File`, `URL`, `Utils`, message CGI merging, monitor events, redirector registry/metalink handling, delegated-credential environment, `XrdOucTPC`, semaphores/timers, and XRootD protocol errors.

## Risks and Edge Cases

TPC behavior depends on server capability strings and error normalization. Source open is optional only with delegation; without delegation it becomes fatal. Timeout accounting is subtle because zero has special meaning and close attempts should still happen after expiry. Progress polling every 2.5 seconds can miss fast copies and cancellation waits for async sync completion. `GenerateKey` combines time and process IDs and is not cryptographic. Close failure attribution in `RunTPC` appears to choose the wrong label in the `UpdateErrMsg` argument when source close fails.

## Test Signals

Useful tests include unsupported local/source/target cases, delegated TPC-lite only flow, vanilla rendezvous flow, fallback-triggering `errNotSupported`, cancellation via progress handler, checksum match/mismatch, timeout during `CanDo`, destination open TPC-not-supported mapping, and monitor event emission.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClThirdPartyCopyJob.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClThirdPartyCopyJob.hh -->
# sources/distributed-fs/xrootd/src/XrdCl/XrdClThirdPartyCopyJob.hh

## Purpose

This header declares the `ThirdPartyCopyJob` concrete `CopyJob` implementation and the state it needs to perform remote-to-remote copies.

## Important APIs, Types, and Functions

The public API is the constructor and `Run(CopyProgressHandler*)`. Private methods are `CanDo`, `RunTPC`, `RunLite`, and `GenerateKey`. Members hold the destination file, source/target URLs, TPC key, checksum configuration, source size, timeout, force/coerce/delegate flags, substream count, and TPC-lite selection.

## Control Flow

The header separates feasibility/probing from execution. `Run` is the external entry point; private methods implement the two copy protocols and key generation.

## State and Persistence Behavior

The object owns an `XrdCl::File dstFile` and value-copy URLs/strings/flags for one job. Results are reported through inherited property/result lists rather than direct persistence.

## Dependencies and Integration Points

It includes copy-process, copy-job, and file interfaces. The job is created directly by copy orchestration or by `TPFallBackCopyJob`.

## Risks and Edge Cases

Because the class stores mutable per-run state, a single instance should not be reused concurrently. Header consumers need the implementation to close `dstFile` in all error paths.

## Test Signals

Compile/link coverage plus the behavior tests for the `.cc` file validate this declaration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClThirdPartyCopyJob.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClTls.cc -->
# sources/distributed-fs/xrootd/src/XrdCl/XrdClTls.cc

## Purpose

This file implements the XrdCl TLS wrapper over `XrdTlsSocket`. It initializes a process-wide TLS context, configures TLS logging, performs nonblocking TLS handshakes with host verification, maps TLS read/write retry states into XrdCl statuses, and remaps poll events during handshake reversals.

## Important APIs, Types, and Functions

`InitTLS` creates the global `XrdTlsContext` once, using `X509_CERT_DIR`/`X509_CERT_FILE` or `/etc/grid-security/certificates`, validates CA directory permissions, and records `NoTlsOK` on failure. `SetTlsMsgCB` installs XrdTls message/debug callbacks based on `TlsDbgLvl`. `Tls::Connect`, `Read`, `ReadV`, `Send`, `Shutdown`, `ToStatus`, `MapEvent`, and `ClearErrorQueue` implement the wrapper.

## Control Flow

The constructor installs callbacks, calls `InitTLS`, throws on failure, and creates a nonblocking handshake socket wrapper. `Connect` skips host verification for loopback names, calls TLS connect, logs and returns errors, uncorks the underlying socket when the handshake needs I/O, and enables or disables uplink depending on whether TLS wants write or read. `Read` and `Send` call TLS I/O, convert status, manage handshake reversal states (`ReadOnWrite`, `WriteOnRead`), alter uplink notifications, and return `suRetry` when no bytes moved. `ReadV` emulates vector reads by sequential TLS reads.

## State and Persistence Behavior

TLS context is a process-global `unique_ptr` guarded by a static mutex. Per-socket state includes the underlying `Socket`, owned `XrdTlsSocket`, handshake reversal state, and socket handler pointer. No on-disk state is written, but environment variables and `DefaultEnv` affect initialization.

## Dependencies and Integration Points

It depends on `XrdTls`, `XrdTlsContext`, `XrdTlsSocket`, XrdCl socket/poller/default environment/logging, `XrdOucUtils::ValPath`, and async socket handlers for uplink toggles. `Socket::TlsHandShake` and encrypted streams use it.

## Risks and Edge Cases

Once initialization fails, `NoTlsOK` can suppress later attempts even if environment changes. CA path validation may reject deployments with unusual permissions. TLS wants-read/wants-write reversal must stay synchronized with poller event mapping or handshakes can stall. `TLS_SSL_Error` maps to fatal `errTlsError` with `EAGAIN`, which can be confusing diagnostically.

## Test Signals

Tests should cover successful context initialization, missing/invalid CA paths, loopback verification bypass, want-read/write handshake transitions, event remapping, zero-byte retry behavior, TLS close mapping to socket error, and debug callback setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClTls.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClTls.hh -->
# sources/distributed-fs/xrootd/src/XrdCl/XrdClTls.hh

## Purpose

This header declares TLS support for XrdCl sockets: a global initializer and the `Tls` class that wraps encrypted I/O and handshake event translation.

## Important APIs, Types, and Functions

`InitTLS()` initializes the shared TLS context. `Tls` exposes `Connect`, `Read`, fake `ReadV`, `Send`, `Shutdown`, `MapEvent`, and `ClearErrorQueue`. Private `TlsHSRevert` tracks whether a read callback should be invoked on write readiness or a write callback on read readiness. `ToStatus` maps XrdTls return codes into XrdCl status values.

## Control Flow

The class is constructed with a `Socket` and `AsyncSocketHandler`. Callers use the same read/write style as raw sockets, but the TLS object may perform handshake steps lazily and request event remapping through `MapEvent`.

## State and Persistence Behavior

Per-instance state is nonpersistent: raw socket pointer, owned TLS socket, handshake reversal flag, and socket handler pointer. The global initializer owns context state outside the class.

## Dependencies and Integration Points

It includes XrdTls socket support, XRootD response statuses, and async socket handler declarations. `Socket` owns or uses this class when encryption is enabled.

## Risks and Edge Cases

The constructor can throw if TLS initialization fails, so callers must translate that into `XRootDStatus`. `ReadV` is not true vector I/O; it loops over buffers and can stop on retry after partial progress.

## Test Signals

Compile-level API tests plus TLS integration tests for handshake, read, write, event mapping, and shutdown validate this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClTls.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClTransportManager.cc -->
# sources/distributed-fs/xrootd/src/XrdCl/XrdClTransportManager.cc

## Purpose

This file implements a registry/cache for protocol-specific `TransportHandler` objects. It ships with built-in XRootD transports for root/xroot and secure roots/xroots protocols.

## Important APIs, Types, and Functions

The constructor populates `pHandlers` with new `XRootDTransport` instances for `"root"`, `"xroot"`, `"roots"`, and `"xroots"`. The destructor deletes cached handlers. `RegisterFactory` is intended to register protocol factories. `GetHandler` returns an existing handler or creates one from a registered factory.

## Control Flow

Lookup first checks the handler cache. If no handler exists, `GetHandler` checks `pFactories`; missing factory returns null. If a factory exists, it is called once and the produced handler is cached for later calls.

## State and Persistence Behavior

State is in-memory maps of protocol to handler and protocol to factory. The manager owns all cached handlers and deletes them on destruction. No persistent registry exists.

## Dependencies and Integration Points

It depends on `XrdClTransportManager.hh` and `XrdClXRootDTransport.hh`. Channel/postmaster setup uses this manager to obtain the transport implementation for a URL protocol.

## Risks and Edge Cases

`RegisterFactory` currently returns false when the protocol is absent from `pFactories`, then assigns only when it already exists. Because the map starts empty, this appears to prevent registration of new external factories. There is no duplicate handler cleanup if a factory registration changes after a handler is already cached. The manager is not internally synchronized.

## Test Signals

Tests should assert built-in protocol lookup, unknown protocol null lookup, external factory registration behavior, handler caching, and destructor cleanup under leak checking.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClTransportManager.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClTransportManager.hh -->
# sources/distributed-fs/xrootd/src/XrdCl/XrdClTransportManager.hh

## Purpose

This header declares `TransportManager`, the protocol-to-transport registry used by XrdCl channel creation.

## Important APIs, Types, and Functions

`TransportFactory` is a function pointer returning a `TransportHandler *`. Public methods are constructor, destructor, `RegisterFactory(protocol, factory)`, and `GetHandler(protocol)`. Private maps store cached handlers and registered factories.

## Control Flow

The API supports eager built-in handlers and lazy factory-created handlers. Callers ask for a handler by URL protocol and get either a cached handler, a newly factory-created handler, or null.

## State and Persistence Behavior

The manager owns cached handler pointers for its lifetime. Factories are non-owning function pointers. There is no persistence.

## Dependencies and Integration Points

The header uses C++ maps/strings and forward-declares `TransportHandler`. It is consumed by postmaster/channel initialization code.

## Risks and Edge Cases

Raw handler pointers require clear ownership. The class does not declare copy prevention; accidental copying would duplicate owning pointers. No thread-safety guarantees are declared.

## Test Signals

Compile/link tests, registry behavior tests, and copy-prevention/leak checks are the relevant signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClTransportManager.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClURL.cc -->
# sources/distributed-fs/xrootd/src/XrdCl/XrdClURL.cc

## Purpose

This file implements XrdCl URL parsing, normalization, reconstruction, and query-parameter helpers. It supports root/xroot URLs, local file shorthand, stdio `-`, HTTP/DAV default ports, IPv6 bracket handling, metalink detection, secure protocol detection, TPC intent detection, and auth obfuscation.

## Important APIs, Types, and Functions

Constructors call `FromString`. Parsing is split across `FromString`, `ParseHostInfo`, `ParsePath`, and `SetParams`. Derived views include `GetPathWithParams`, `GetPathWithFilteredParams`, `GetLocation`, `GetParamsAsString`, `GetLoginToken`, `GetObfuscatedURL`, and `GetChannelId`. State recomputation uses `ComputeHostId`, `ComputeURL`, and `Clear`. Classification helpers include `IsValid`, `IsMetalink`, `IsLocalFile`, `IsSecure`, `IsTPC`, and `PathEndsWith`.

## Control Flow

`FromString` clears state, selects protocol from `://`, absolute path, `-`, or root default, adjusts default ports for HTTP/DAV, splits host info and path according to protocol, parses host/user/password/port, parses path/query, rebuilds `pURL`, and logs details with optional auth obfuscation. `ParseHostInfo` handles user/password before `@`, IPv6 bracket addresses, IPv6-encoded IPv4 simplification, and numeric port validation. `SetParams` splits opaque info on `&`, supports values with `=`, and extracts login tokens after an embedded `?`.

## State and Persistence Behavior

URL objects store parsed components and a reconstructed URL string. Setters mutate components and recompute dependent fields immediately. There is no persistence.

## Dependencies and Integration Points

It depends on XrdCl logging/default environment/constants/utils/optimizers, XrdOuc utility headers, and metalink environment configuration. Copy, stream, transport, and checksum code consume URL channel IDs, filtered params, security flags, and TPC intent.

## Risks and Edge Cases

The parser is intentionally simple and does not perform general URL escaping/decoding. Query params are stored in `std::map`, so original order and duplicate keys are lost. `GetParamsAsString(true)` can produce an extra ampersand after filtering earlier keys because separator logic uses the original iterator position. `ComputeURL` sets `pURL` empty for invalid state but continues building afterward. Passwords can appear in `pHostId`; callers must use obfuscated accessors for logs.

## Test Signals

Tests should cover root default URLs, absolute local paths, stdio, file trailing slash removal, HTTP/DAV ports, IPv6 and IPv6-mapped IPv4, invalid ports/empty hosts, query filtering, login token extraction, channel ID CGI selection, metalink suffix toggled by env, secure protocol flags, and auth obfuscation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClURL.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClURL.hh -->
# sources/distributed-fs/xrootd/src/XrdCl/XrdClURL.hh

## Purpose

This header declares the `XrdCl::URL` value object, the shared representation for parsed client URLs and opaque query parameters.

## Important APIs, Types, and Functions

`ParamsMap` stores query parameters. Public APIs include constructors, validity/classification helpers, component getters/setters, full/obfuscated URL access, host/channel/location/path views, param serialization and mutation, login token lookup, `FromString`, and `Clear`. Private helpers parse host/path and recompute host ID and URL strings.

## Control Flow

Constructors and setters update the internal representation. `FromString` is the full parser. Getters expose both raw components and derived strings needed by channel reuse, TPC, auth, and logging code.

## State and Persistence Behavior

The object stores protocol, user, password, hostname, port, path, params, host ID, and full URL. It is a copyable in-memory value; no persistence or external ownership is involved.

## Dependencies and Integration Points

Only standard map/string headers are included in the header. It is used across XrdCl copy, transport, stream, redirector, and utility APIs.

## Risks and Edge Cases

Because setters recompute immediately, partial construction through multiple setters can briefly produce invalid or surprising `pURL` values. The header exposes password getter and raw URL getter, so logging code must choose `GetObfuscatedURL` when appropriate. `GetChannelId` includes only selected CGI keys, which must stay aligned with authentication/channel-affinity behavior.

## Test Signals

API tests should verify setter recomputation, path-with-filtered-params behavior, channel ID composition, validity rules, secure/TPC classifications, and round-tripping through `FromString` plus `GetURL`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClURL.hh -->
