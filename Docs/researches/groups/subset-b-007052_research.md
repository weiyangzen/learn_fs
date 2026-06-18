# Research: subset-b-007052

Grouped source research for EOS MGM workflow/xattr/zmq and namespace interface/support files. Each section preserves its source path for source-tree-aligned reconciliation.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/wfe/WFE.hh -->
## sources/distributed-fs/eos/mgm/wfe/WFE.hh

Purpose: Declares the MGM workflow engine that executes asynchronous and synchronous workflow events, especially CTA/protobuf workflow actions and queue-backed policy processing. `WFE` owns the assisted engine thread, root virtual identity, an active-job counter, and a completion condition variable.

Important APIs and types: `WFE::Start`, `Stop`, and `WFEr` control the engine loop. `WFE::Job` extends `XrdJob` and carries `Action` records, file id, virtual identity, workflow path, retry count, and error text. Handler APIs cover `notify`, `proto`, prepare/abort/evict/create/delete/close/archived/offline/update-fid failure paths, `SendProtoWFRequest`, `EvictAsRoot`, `CollectAttributes`, and queue persistence methods `Save`, `Load`, `Move`, `Results`, and `Delete`.

Control flow: callers create `Job`, add one or more `Action`s, then either dispatch it through XRootD scheduling or invoke `DoIt` synchronously. `DoIt` delegates by method/event, records results, and moves jobs across queues, including retry handling. `Action` constructors derive string timestamps and day partitions used by persisted queue entries.

State and persistence: runtime state is `mActiveJobs`, `mDoneSignal`, `mThread`, and `gScheduler`; durable state is expressed through queue/day/action records managed by the `Job` persistence methods. Jobs include retry count and saved day to support moving between queued, running, retry, result, and delete states.

Dependencies and integration: integrates MGM namespace state, `VirtualIdentity`, file identifiers, `ThreadPool`/`AssistedThread`, XRootD job/scheduler/error types, CTA frontend protobuf requests, console reply protobufs, and global MGM services used in implementation. Workflow attributes from namespace metadata feed the engine through `Workflow`.

Risks: queue moves and retry behavior must remain idempotent, especially for external CTA events. `Job` copy construction omits `mVid` and `mWorkflowPath`, which is safe only if copies are not used for execution requiring those fields. Scheduler singleton lifetime and detached/asynchronous jobs require careful shutdown ordering. Proto opaque parsing must reject missing request ids without corrupting workflow state.

Test signals: cover sync and async workflow dispatch, queue save/load/move/delete, retry transitions, proto request construction, prepare idempotency, owner/user/group lookup, active-job publishing, and error propagation from each event handler.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/wfe/WFE.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/workflow/Workflow.cc -->
## sources/distributed-fs/eos/mgm/workflow/Workflow.cc

Purpose: Implements the metadata-driven workflow trigger surface used by MGM operations. It converts event/workflow names and namespace xattrs into `WFE::Job` actions, with special behavior for synchronous close/open workflows and WFE enablement flags.

Important APIs and functions: `Trigger` resolves `sys.workflow.<event>.<workflow>` attributes and invokes `Create`; `getCGICloseW` and `getCGICloseR` generate CGI query fragments for FST close callbacks; `Create` wraps `ExceptionThrowingCreate`; `WfeRecordingEnabled` and `WfeEnabled` read space configuration.

Control flow: `Trigger` normalizes some workflow names (`none`, retrieve-written, default), looks up the matching xattr key, stores the selected event/workflow/action, then calls `Create`. `ExceptionThrowingCreate` builds a `WFE::Job`; sync events run immediately when WFE is `on`, while async events are saved to queue `q` when WFE is not `off`.

State and persistence: `Workflow` itself only mutates transient members inherited from initialization, but async creation persists jobs through `WFE::Job::Save`. Sync closew CGI generation fetches file metadata and encodes custom attributes into a base64 parameter.

Dependencies and integration: depends on MGM global `gOFS`, namespace `Prefetcher`, `IView`, `FsView::gFsView` space configuration, `WFE`, `SymKey::Base64Encode`, and workflow constants. It must be called while metadata pointers and file ids are valid.

Risks: missing xattrs return `-1` with `errno=ENOKEY`, so callers must distinguish absent workflows from real failures. `getCGICloseW` fetches metadata and parent URI and can suppress workflow URL creation on `MDException`. WFE config semantics differ for sync (`wfe == on`) and async recording (`wfe != off`), which should be explicit in tests.

Test signals: test xattr key selection, sudo `none` handling, retrieve-written protocol fallback, enonet stall return, sync versus async job creation, exception-to-`ECANCELED` conversion, and CGI payload fields for closew/closer.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/workflow/Workflow.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/workflow/Workflow.hh -->
## sources/distributed-fs/eos/mgm/workflow/Workflow.hh

Purpose: Declares the `Workflow` helper that binds namespace xattrs, a path/file id, an event, and a workflow name into WFE job creation or callback CGI generation.

Important APIs and types: `Init` attaches an external xattr map and optional file identity; `SetFile` updates path/fid; `Trigger`, `getCGICloseW`, `getCGICloseR`, `Create`, and `ExceptionThrowingCreate` are the public workflow operations. `IsSync` checks the stored event prefix, and `Reset` clears all transient state.

Control flow: callers initialize with metadata attributes, optionally set a file, then trigger by event/workflow. The header intentionally keeps persistence details private behind `Create`, while static helpers query global WFE configuration.

State and persistence: stores a raw pointer to `IContainerMD::XAttrMap`, path, fid, current event, workflow, and action. It does not own the attribute map, so lifetime and locking are caller responsibilities.

Dependencies and integration: uses common file ids, `VirtualIdentity`, MGM namespace macros, and namespace `IView` types. The implementation integrates with `WFE` and MGM filesystem view globals.

Risks: raw xattr pointer can dangle or race if the caller releases metadata locks too early. `SetFile` ignores zero fid and empty path, which is convenient but can leave stale values if callers expected clearing. `IsSync` assumes `mEvent` has at least six characters but `substr` itself is safe.

Test signals: validate reset semantics, event prefix detection, path/fid retention rules, and trigger behavior when `mAttr` is null or lacks keys.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/workflow/Workflow.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/xattr/XattrLock.hh -->
## sources/distributed-fs/eos/mgm/xattr/XattrLock.hh

Purpose: Implements application-level file locks stored in EOS extended attributes, including shared/exclusive mode, owner matching with limited wildcards, expiry, and FUSE open-state bypass.

Important APIs and types: `XattrLock` can parse an `IFileMD::XAttrMap`, `Parse` decodes `expires/type/owner`, `foreignLock` decides whether access is blocked, `Lock` writes `EOS_APP_LOCK_ATTR`, `Unlock` removes it, and `Value` serializes the lock attribute.

Control flow: `Lock` prefetches and write-locks file metadata, reads any existing app-lock xattr, rejects active foreign locks, validates lifetime and wildcard rules, computes owner and expiry, and sets the xattr. `Unlock` performs the same prefetch/write-lock/get/foreign-lock check before removing the xattr.

State and persistence: object state mirrors the xattr fields plus `isfuseopen`, and persisted state is the `EOS_APP_LOCK_ATTR` string. `sys.fusex.state` ending without `|` disables foreign-lock enforcement while a FUSE commit is open.

Dependencies and integration: depends on MGM `gOFS`, namespace `Prefetcher`, `MDLocking::writeLock`, `_attr_get/_attr_set/_attr_rem`, `VirtualIdentity`, and common lock attribute constants.

Risks: the constructor uses `attr["sys.fusex.state"]`, which inserts an empty entry into the copied map. Expiry parsing uses `atoi`, so malformed or overflowing values can become zero. Locks longer than one week are ignored for access and rejected on create; tests should keep those semantics aligned. `foreignLock` owner matching only supports exact, wildcard-user, or wildcard-app, not both.

Test signals: cover parse failures, shared read pass-through, exclusive write blocking, expired lock behavior, illegal lifetime, wildcard validation, FUSE open bypass, errno values (`EBUSY`, `EINVAL`, metadata errno), and xattr removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/xattr/XattrLock.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/xattr/XattrSet.hh -->
## sources/distributed-fs/eos/mgm/xattr/XattrSet.hh

Purpose: Provides a small serializer/deserializer for storing a set of strings as a single space-separated extended attribute value.

Important APIs and types: `XattrSet::values` is the backing `std::set`; constructors optionally deserialize C strings; `deserialize` accepts C string or `std::string`; `serialize` joins set values with single spaces.

Control flow: deserialization scans from token start to space or NUL, inserts tokens with length greater than one, and continues until NUL. Serialization iterates the sorted set, appends a trailing space per value, then removes the final separator.

State and persistence: there is no external persistence beyond the xattr-compatible string. Using `std::set` sorts and deduplicates values, so original order and duplicate tokens are intentionally lost.

Dependencies and integration: only depends on MGM namespace macros and standard library containers. It is suited for simple xattrs whose values cannot contain spaces.

Risks: single-character tokens are dropped because the condition is `str-begin > 1`; if one-character values are valid, this is a bug. Empty or repeated spaces are ignored. Values containing spaces cannot round-trip.

Test signals: cover empty strings, repeated tokens, leading/trailing/multiple spaces, one-character tokens, sorted serialization, and round-trip behavior for expected xattr values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/xattr/XattrSet.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/zmq/ZMQ.cc -->
## sources/distributed-fs/eos/mgm/zmq/ZMQ.cc

Purpose: Implements the MGM ZeroMQ proxy used by the FUSE server path. It binds a ROUTER frontend, fans messages to in-process DEALER workers, parses FUSE heartbeat protobufs, and feeds `FuseServer::Server`.

Important APIs and functions: `ZMQ::ServeFuse` creates and detaches the task thread. `Task::run` configures sockets, keepalives, backend, injector, and worker threads before entering `zmq::proxy`. `Task::reply` injects replies to a client identity. `Worker::work` reads multipart messages and dispatches heartbeat/statistics.

Control flow: frontend receives client identity plus protobuf payload; the proxy sends work to workers over `inproc://backend`; workers parse `eos::fusex::container`, compute heartbeat clock delta, dispatch heartbeat and statistics to `gFuseServer.Client()`, and log unknown or unparseable messages.

State and persistence: state is process-local: a ZMQ context/sockets, detached worker threads, and the static `gFuseServer`. No durable persistence is performed.

Dependencies and integration: uses `zmq.hpp`, FUSE protobufs, MGM FuseServer, common timing/logging/string-to-hex utilities, and XRootD mutex for reply serialization.

Risks: worker threads are detached and allocated with `new`; workers delete themselves only on `ETERM`, while `Task` deletes thread objects but cannot join them. The worker constructor allocation is passed directly into detached thread creation, so startup failures could leak. `Task::reply` relies on a static mutex for injector socket safety.

Test signals: integration test socket bind/proxy startup, heartbeat parse and delta computation, statistics forwarding, malformed multipart handling, unparseable payload logging, reply framing, and clean shutdown on context close.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/zmq/ZMQ.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/zmq/ZMQ.hh -->
## sources/distributed-fs/eos/mgm/zmq/ZMQ.hh

Purpose: Declares the ZeroMQ wrapper, worker, and task classes for MGM FUSE proxying.

Important APIs and types: `ZMQ` owns the bind URL and a `std::unique_ptr<Task>`, with `ServeFuse` starting proxy service. `ZMQ::Task` owns context, ROUTER frontend, DEALER backend, DEALER injector, worker thread list, and `reply`. `ZMQ::Worker` owns a DEALER socket tied to the task context.

Control flow: a `ZMQ` instance is constructed with a URL, `ServeFuse` creates a `Task`, `Task::run` starts workers and proxy, and workers call `work` until shutdown.

State and persistence: all state is runtime socket/thread state; `gFuseServer` is static process-wide service state. The destructor logs but does not itself stop the task.

Dependencies and integration: depends on MGM namespace macros, `FuseServer::Server`, `<zmq.hpp>`, and POSIX/standard threading.

Risks: detached thread lifecycle means destruction of `ZMQ` without orderly task shutdown can leave work running. `Task` constructor takes non-const `std::string&`, making it less flexible than necessary. Typo-only comments do not affect behavior but signal limited local documentation.

Test signals: compile/link tests against libzmq, lifecycle tests for create/destroy/serve, reply framing, and static fuse server availability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/zmq/ZMQ.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/namespace/CMakeLists.txt -->
## sources/distributed-fs/eos/namespace/CMakeLists.txt

Purpose: Defines the EOS namespace common object library, shared library, optional static library, include paths, dependencies, install target, and QuarkDB namespace subdirectory inclusion.

Important APIs and targets: `EosNsCommon-Objects` is the object library containing namespace interfaces, utilities, QuarkDB implementations, accounting, views, inspectors, and persistency code. `EosNsCommon` is the shared library built from those objects. `EosNsCommon-Static` is Linux-only.

Control flow: CMake includes generated and qclient headers, lists all object sources, links required public dependencies, enables PIC, creates shared/static products, sets version properties, installs the shared library, and descends into `ns_quarkdb`.

State and persistence: no runtime state; build graph state controls which sources and dependencies are part of namespace linkage.

Dependencies and integration: integrates `qclient`, EOS CLI protobuf objects, `EosCommon`, XRootD utils, RocksDB, JsonCpp, and CRC/common static variants. The source list is the central contract for namespace implementation compilation.

Risks: adding a new namespace source without this list can compile in tests only if included elsewhere, causing production link gaps. Public link dependencies can affect consumers. Static target exists only under `Linux`, so portability tests must account for target absence.

Test signals: CMake configure on Linux/non-Linux, shared/static target creation, install layout, link checks for QuarkDB and RocksDB symbols, and source-list coverage for new files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/namespace/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/namespace/Constants.cc -->
## sources/distributed-fs/eos/namespace/Constants.cc

Purpose: Defines namespace-wide constants declared in `Constants.hh`.

Important APIs and values: provides the single definition of `eos::QUOTA_NODE_FLAG` as `0x0001`.

Control flow: no executable control flow beyond static initialization of a constant.

State and persistence: no runtime mutable state; this value is a compile/link-time ABI-visible symbol used to mark quota-node containers.

Dependencies and integration: includes `namespace/Constants.hh` and participates in `EosNsCommon-Objects`.

Risks: changing the numeric flag can reinterpret persisted metadata flags. Because it is an external constant rather than `constexpr`, consumers require this object to link.

Test signals: link tests for `QUOTA_NODE_FLAG` and metadata tests verifying quota-node flag interpretation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/namespace/Constants.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/namespace/Constants.hh -->
## sources/distributed-fs/eos/namespace/Constants.hh

Purpose: Declares namespace constants shared across namespace components.

Important APIs and values: declares `extern const uint16_t QUOTA_NODE_FLAG`.

Control flow: header-only declaration with no runtime flow.

State and persistence: the constant is used as a bit in metadata flags and therefore participates in persisted container state semantics.

Dependencies and integration: includes `<stdint.h>` and exposes the symbol in namespace `eos`.

Risks: consumers must include the matching object definition. Header does not document bit ownership beyond the name, so flag collisions should be checked before adding more constants.

Test signals: compile tests including the header from C++ consumers and behavior tests for quota-node registration/removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/namespace/Constants.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/namespace/MDException.cc -->
## sources/distributed-fs/eos/namespace/MDException.cc

Purpose: Implements `MDStatus` construction and logging for namespace metadata operation status.

Important APIs and functions: `MDStatus::MDStatus(int, const std::string&)` stores errno and error text, logging at critical level for non-`ENOENT` errors and debug level for `ENOENT`.

Control flow: construction performs the only behavior: choose log severity based on errno, then leave `ok()` false because `err` is non-empty.

State and persistence: no durable persistence; status objects carry local errno and message for caller-side throwing or inspection.

Dependencies and integration: includes `MDException.hh`, common logging, and folly exception wrapper headers. Used by metadata services as a non-exception status channel.

Risks: constructing `MDStatus` for expected non-ENOENT failures emits critical logs, so high-volume paths should avoid using it for benign conditions. Empty error strings are the only `ok()` signal.

Test signals: verify log severity expectations, `ok/getError/getErrno`, and `throwIfNotOk` behavior through header implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/namespace/MDException.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/namespace/MDException.hh -->
## sources/distributed-fs/eos/namespace/MDException.hh

Purpose: Defines exception and status primitives for EOS namespace metadata operations.

Important APIs and types: `MDException` stores errno and stream-built message, overrides `what`, supports copy construction, and offers `wrapAndRethrow`. Macros `throw_mdexception`, `make_mdexception`, and `SSTR` simplify throwing and folly exception wrappers. `MDStatus` stores errno/message and can throw if not ok.

Control flow: callers stream context into `getMessage()` and throw. `what()` materializes the stream into an owned C string each call. `MDStatus::throwIfNotOk` converts failed statuses into `MDException`.

State and persistence: exception state is transient errno plus message stream. There is no durable state, but errno values drive caller behavior and protocol return codes.

Dependencies and integration: used throughout namespace services, resolver, prefetcher callers, and MGM code. Depends on standard exceptions/streams/cerrno and folly `ExceptionWrapper`.

Risks: `what()` mutates a `mutable char*` even on a const exception, so concurrent calls on the same exception object are unsafe. Macros create local names and should be used carefully in nested scopes. `SSTR` relies on stream expression conversion patterns that can be compiler-sensitive.

Test signals: exception copy preserves message/errno, `what()` is stable enough for logging, `wrapAndRethrow` prefixes messages, folly wrapper construction works, and `MDStatus` ok/error paths throw as expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/namespace/MDException.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/namespace/MDLocking.cc -->
## sources/distributed-fs/eos/namespace/MDLocking.cc

Purpose: Implements factory functions for namespace metadata RAII locks.

Important APIs and functions: `MDLocking::readLock/writeLock` overloads create `std::unique_ptr` wrappers for file and container read/write locks.

Control flow: each function simply constructs the corresponding `NSObjectMDLock` alias around a raw metadata pointer and returns it to the caller.

State and persistence: no durable state; returned lock objects own mutex acquisition/release lifetime.

Dependencies and integration: includes `MDLocking.hh`, `NSObjectLocker.hh`, and file/container interfaces. Used anywhere namespace metadata needs lock-order-aware read/write locking.

Risks: callers must pass valid metadata pointers and respect higher-level lock ordering. The wrappers do not encode cross-object order by themselves.

Test signals: compile tests for overload resolution, lock acquisition/release under read/write contention, and use with both file and container raw pointers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/namespace/MDLocking.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/namespace/MDLocking.hh -->
## sources/distributed-fs/eos/namespace/MDLocking.hh

Purpose: Centralizes type aliases and factories for locking namespace file/container metadata objects, including individual and bulk locks.

Important APIs and types: exposes `ContainerReadLock`, `ContainerWriteLock`, `FileReadLock`, `FileWriteLock`, pointer aliases, bulk file/container locks, bulk mixed metadata locks, factory functions, and `FileOrContainerMDLocked` holder types.

Control flow: header declares type structure; implementation constructs locks. Bulk aliases integrate with try-lockers and multi-object lockers to avoid ad hoc locking in callers.

State and persistence: no persistence. Lock objects manage runtime access to metadata object mutexes exposed by `LockableNSObjMD`.

Dependencies and integration: depends on namespace macros, `LockableNSObject.hh`, raw pointer wrappers, `NSObjectLocker`, and metadata interfaces. It is included by interfaces and MGM xattr code.

Risks: aliases use raw pointer wrappers rather than shared ownership, so object lifetime remains external. Misordered manual locking can still deadlock; comments in `IView` warn about parent-container/file order. Bulk lock behavior should be preferred for multi-object operations.

Test signals: deadlock/regression tests for file/container order, bulk lock conflict tests, and static compile coverage where both `shared_ptr` and raw pointer usages are expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/namespace/MDLocking.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/namespace/Namespace.hh -->
## sources/distributed-fs/eos/namespace/Namespace.hh

Purpose: Defines namespace macros for EOS namespace code.

Important APIs and macros: `EOSNSNAMESPACE_BEGIN` expands to `namespace eos {`, `EOSNSNAMESPACE_END` closes it, and `USE_EOSNSNAMESPACE` imports `eos`.

Control flow: no runtime behavior.

State and persistence: no state. The file only affects source organization and symbol namespace.

Dependencies and integration: included by most namespace interface/support headers to keep namespace declarations uniform.

Risks: macro-based namespace boundaries can hide mismatched braces during review. `USE_EOSNSNAMESPACE` introduces a using-directive and should be avoided in headers outside controlled scope.

Test signals: compile tests for namespace headers and include-order checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/namespace/Namespace.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/namespace/PermissionHandler.cc -->
## sources/distributed-fs/eos/namespace/PermissionHandler.cc

Purpose: Implements utility functions for translating POSIX permission bits and `access(2)` request masks into EOS internal permission flags, plus filtering modes with `sys.mask`.

Important APIs and functions: `convertModetUser`, `convertModetGroup`, `convertModetOther`, `convertRequested`, `checkPerms`, `parseOctalMask`, and `filterWithSysMask`.

Control flow: conversion functions map read/write/execute or read/write/enter bits into `CANREAD`, `CANWRITE`, and `CANENTER`. `checkPerms` verifies every requested bit is present. `parseOctalMask` uses base-8 `stol` and rejects partial parses. `filterWithSysMask` applies `mode & mask` when parsing succeeds.

State and persistence: stateless; `sys.mask` itself is stored in metadata xattrs and interpreted here.

Dependencies and integration: depends on sys/stat/access constants and the header template overload for xattr maps. Used by file/container metadata access logic and callers applying xattr permission masks.

Risks: invalid masks are silently ignored, preserving original mode; this is permissive and should be documented in admin behavior. Internal flags are macros, not scoped enum values.

Test signals: cover all user/group/other bit combinations, requested `R_OK/W_OK/X_OK`, missing-bit denial, octal parsing failures, and `sys.mask` map filtering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/namespace/PermissionHandler.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/namespace/PermissionHandler.hh -->
## sources/distributed-fs/eos/namespace/PermissionHandler.hh

Purpose: Declares permission conversion and filtering helpers for namespace metadata access checks.

Important APIs and types: defines `CANREAD`, `CANWRITE`, `CANENTER` bit macros and static `PermissionHandler` methods, including a templated xattr-map overload for `filterWithSysMask`.

Control flow: callers convert stored mode and requested access into internal flags, then call `checkPerms`; xattr-aware callers pass maps containing optional `sys.mask`.

State and persistence: stateless helper. It interprets persisted `sys.mask` xattr values.

Dependencies and integration: includes namespace macros and `IFileMD.hh` for mode/metadata context. Template works with `std::map` and protobuf-like maps exposing `find` and `second`.

Risks: macros can collide in global preprocessor scope. The template assumes mapped values are string-like. Permission behavior must remain consistent with POSIX expectations and EOS `enter` semantics.

Test signals: compile test with both std and protobuf map types, plus behavior tests matching `PermissionHandler.cc`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/namespace/PermissionHandler.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/namespace/Prefetcher.cc -->
## sources/distributed-fs/eos/namespace/Prefetcher.cc

Purpose: Implements asynchronous metadata prefetching to populate namespace caches before callers perform synchronous metadata operations, reducing QuarkDB/cache latency in path, inode, directory, and filesystem-list workflows.

Important APIs and functions: staging methods add file, container, item, and URI futures; `wait` blocks on staged futures. Static convenience methods prefetch by path/id/inode, with parents, with children, filesystem file lists, unlinked lists, and parent URIs.

Control flow: all methods return immediately for in-memory views. Stage methods request futures from `IView`, `IFileMDSvc`, or `IContainerMDSvc`; parent prefetch chains metadata futures into URI futures. Child prefetch fetches the container, checks a ten-minute `lastPrefetch` throttle, iterates subcontainers/files with optional limits, stages each child, waits, and updates `lastPrefetch`.

State and persistence: `Prefetcher` owns vectors of futures only for its lifetime. Persistent metadata is not changed except for the in-memory `IContainerMD::lastPrefetch` timestamp used to throttle child prefetches.

Dependencies and integration: integrates `IView`, `IFsView`, file/container services, `ContainerMapIterator`, `FileMapIterator`, `FileId` inode helpers, folly futures, and EOS logging. MGM callers use it before locking or xattr operations.

Risks: staged item futures in `mItems` are never waited in `wait`, so `stageItem` may not provide the same synchronization guarantee as file/container/URI staging. Exceptions during path staging are logged as benign races. Child prefetch can be expensive without limits, and limit defaults use `uint64_t(-1)`.

Test signals: verify in-memory no-op behavior, future waiting for files/containers/URIs, item prefetch synchronization expectation, child prefetch throttling, limit handling, inode file/container detection, unlinked filesystem list prefetch, and race handling on deleted paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/namespace/Prefetcher.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/namespace/Prefetcher.hh -->
## sources/distributed-fs/eos/namespace/Prefetcher.hh

Purpose: Declares the metadata prefetch engine and its static convenience API for namespace callers.

Important APIs and types: `Prefetcher(IView*)`, stage methods for file/container/item and parent URI resolution, `wait`, and static prefetch helpers for paths, ids, inodes, children, filesystem lists, unlinked lists, and parent paths.

Control flow: header separates manual staging/wait usage from one-shot helpers. Private `prefetchFileUri` and `prefetchContUri` are used for future chaining.

State and persistence: holds raw service/view pointers and vectors of folly futures. No ownership of services is implied.

Dependencies and integration: depends on namespace macros, `IFileMD`, and folly futures; forward-declares services/views. Used broadly by MGM and namespace operations before reading metadata.

Risks: raw `IView*` must outlive the prefetcher and all pending futures. The declared `prefetchContainerMDWithParentsAndWait` takes `IFileMD::id_t` though it represents a container id, which is type-confusing.

Test signals: compile coverage for all overloads, service lifetime assumptions in async tests, and consistency between header declarations and implementation behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/namespace/Prefetcher.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/namespace/Resolver.cc -->
## sources/distributed-fs/eos/namespace/Resolver.cc

Purpose: Implements utilities to resolve protobuf or string identifiers into namespace metadata identifiers/objects.

Important APIs and functions: `resolveContainer` accepts a console namespace container specification and returns `IContainerMDPtr`; `retrieveFileIdentifier` parses `fid:`, `fxid:`, `/.fxid:`, and `ino:` strings into a `FileIdentifier`.

Control flow: `resolveContainer` switches on protobuf oneof case: path uses `view->getContainer`, decimal cid parses base 10 then calls container service, hex cxid parses base 16, and empty/unknown throws `MDException(EINVAL)`. `retrieveFileIdentifier` uses prefix checks and converts file inode values through `FileId`.

State and persistence: stateless resolver; returned metadata objects come from view/service caches or backing stores.

Dependencies and integration: depends on `IView`, container service, console protobufs, common parse utilities, `FileId`, XRootD string, and `MDException`.

Risks: `retrieveFileIdentifier` uses `strtoull` without end-pointer validation, so malformed suffixes can partially parse. Container resolve assumes caller holds `eosViewRWMutex`, which is documented but not enforced.

Test signals: cover each protobuf oneof, invalid decimal/hex strings, empty proto exception, all file id prefixes, non-file inode rejection, and malformed string handling expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/namespace/Resolver.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/namespace/Resolver.hh -->
## sources/distributed-fs/eos/namespace/Resolver.hh

Purpose: Declares namespace resolver helpers for console protobuf container specs and file identifier strings.

Important APIs and types: aliases `ContainerSpecificationProto` to the console protobuf type and exposes static `Resolver::resolveContainer` and `Resolver::retrieveFileIdentifier`.

Control flow: header documents that container resolution requires the caller to hold the view mutex. String resolution recognizes explicit id prefixes.

State and persistence: no owned state.

Dependencies and integration: includes namespace macros, `MDException`, identifier types, `IView`, and `proto/Ns.pb.h`; forward-declares `XrdOucString`.

Risks: API returns shared metadata objects whose locking/lifetime rules are defined by the view/service implementation. Mutex precondition is external and easy to miss.

Test signals: compile with console protobuf definitions and behavior tests matching `Resolver.cc`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/namespace/Resolver.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/namespace/interface/ContainerIterators.hh -->
## sources/distributed-fs/eos/namespace/interface/ContainerIterators.hh

Purpose: Provides resilient iterators over a container's file and subcontainer maps while allowing concurrent map resizing.

Important APIs and types: `FileMapIterator` and `ContainerMapIterator` expose `valid`, `next`, `key`, `value`, and `generation`. They traverse `IContainerMD::FileMap` and `ContainerMap` respectively.

Control flow: constructors capture begin iterator, generation, first key/value, and shown-key set. `next` takes a container read lock, compares current generation to stored generation, restarts from begin if resized, skips already shown keys, and updates validity/key/value.

State and persistence: iterator state includes container shared pointer, current map iterator, shown keys, current key/value, generation, resized flag, and validity. No durable persistence.

Dependencies and integration: depends on `IContainerMD`, `IFileMD`, and `MDLocking`. Used by prefetcher and directory scans where container maps can change during traversal.

Risks: constructors read map iterators without taking a visible lock, relying on caller context or implementation safety. Values for container iterator are typed as `IFileMD::id_t` even though they represent container ids, which is type-confusing. Iteration may skip newly added entries already passed in generation restart scenarios but avoids duplicates.

Test signals: mutate maps during iteration to force generation changes, verify no duplicate keys, validate empty containers, and test lock correctness under concurrent add/remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/namespace/interface/ContainerIterators.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/namespace/interface/IContainerMD.hh -->
## sources/distributed-fs/eos/namespace/interface/IContainerMD.hh

Purpose: Defines the abstract metadata contract for a namespace container/directory, including hierarchy links, children, accounting fields, timestamps, ownership, modes, xattrs, serialization, locking, and prefetch state.

Important APIs and types: types include `id_t`, `XAttrMap`, dense-hash `ContainerMap` and `FileMap`, `FileOrContainerMD`, and `identifier_t`. Virtual methods cover child add/remove/find, file add/remove/find, item lookup, identifiers, parent id, flags, mtime/tmtime/ctime, tree counters, ownership, clone metadata, mode, attributes, access checks, serialization, env export, deletion marking, and locality hints.

Control flow: concrete implementations provide all storage behavior; callers manipulate containers through this interface and then update backing services/views as needed. Protected iterator methods expose map begin/end/generation/copy to friend iterators.

State and persistence: abstract persistent metadata includes id, parent, children, files, flags, times, tree accounting, ownership, clone data, mode, xattrs, and serialized buffer representation. Base state includes atomic deleted marker, last-prefetch timestamp, and mutex.

Dependencies and integration: integrates namespace services, identifiers, buffer/locality utilities, Murmur hash, Google dense hash maps, folly futures, and `MDLocking`. It is central to `IView`, container services, quota, prefetcher, and MGM operations.

Risks: large interface surface makes implementation consistency critical. `mLastPrefetch` is default-initialized and guarded separately from the main metadata mutex. Copy/assignment are deleted to avoid slicing. Implementations must maintain map generation counters correctly for iterators.

Test signals: implementation conformance tests for child/file maps, async find, serialization round-trip, tree counter deltas, xattr behavior, access permissions, deleted marker, locality hints, and iterator generation updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/namespace/interface/IContainerMD.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/namespace/interface/IContainerMDSvc.hh -->
## sources/distributed-fs/eos/namespace/interface/IContainerMDSvc.hh

Purpose: Defines the service interface for creating, fetching, caching, updating, deleting, and observing container metadata objects.

Important APIs and types: `IContainerMDChangeListener` reports `Updated`, `Deleted`, `Created`, and `MTimeChange`. `IContainerMDSvc` exposes initialize/configure/finalize, async/sync fetch by id/clock, cache drop, create, update store, remove, count, listeners, quota stats, lost+found, create-in-parent, file service wiring, container accounting, first-free-id, cache stats, and id blacklist.

Control flow: concrete services allocate ids, hydrate metadata from backing stores, keep caches coherent, call listeners on changes, and coordinate with file services/accounting.

State and persistence: service implementations own cache and backing-store persistence for container metadata. Interface also controls listener and quota/accounting links.

Dependencies and integration: depends on container/file metadata interfaces, `MDException`, `MDLocking`, cache statistics, quota stats, and change listeners. QuarkDB and in-memory implementations fulfill this contract.

Risks: comments mention adding file listeners in a container service, indicating inherited terminology. Callers must write-lock objects as required by implementation before store updates/removal. Listener ordering affects quota/accounting correctness.

Test signals: service lifecycle, async and sync fetch equivalence, cache drop, create/update/remove persistence, listener notifications, lost+found creation, id blacklisting, and cache statistics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/namespace/interface/IContainerMDSvc.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/namespace/interface/IFileMD.hh -->
## sources/distributed-fs/eos/namespace/interface/IFileMD.hh

Purpose: Defines the abstract metadata contract for a namespace file, including identity, times, size, checksums, locations, ownership, layout, symlink state, xattrs, serialization, locking, and deletion marking.

Important APIs and types: types include file id/location/layout ids, time structs, `LocationVector`, `XAttrMap`, `QoSAttrMap`, and `identifier_t`. Virtual methods cover clone, ids, ctime/mtime/atime/sync time, clone metadata, size, container id, checksum/alt checksums, name, locations/unlinked locations, owner/group, layout, flags, file service pointer, symlink, attributes, serialization, clock, deleted marker, locality hint, and env export.

Control flow: concrete implementations store mutable file metadata; services and views call methods while holding appropriate locks and notify listeners after changes.

State and persistence: abstract persistent fields include identifiers, timestamps, size, checksums, parent container, replica/unlinked locations, uid/gid, layout, flags, symlink and xattrs. Base class owns an atomic deleted flag and metadata mutex.

Dependencies and integration: depends on container metadata, identifiers, locking, buffer/locality utilities, and common layout ids. It is consumed by file service, filesystem view, quota, prefetcher, and MGM operations.

Risks: many mutators imply listener side effects in concrete implementations; inconsistent notification can break quota/fs views. Copy/assignment deletion prevents slicing. Locking order around file and parent container must be respected.

Test signals: implementation tests for location transitions, checksum and alt checksum behavior, symlink handling, xattr lifecycle, serialization round-trip, deleted marker, locality hints, and listener-triggered accounting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/namespace/interface/IFileMD.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/namespace/interface/IFileMDSvc.hh -->
## sources/distributed-fs/eos/namespace/interface/IFileMDSvc.hh

Purpose: Defines the service interface for file metadata storage, id allocation, cache management, listener notification, quota/accounting integration, and file enumeration.

Important APIs and types: `TreeInfos` accumulates tree-size/file/container deltas and supports negation/addition. `IFileMDChangeListener` reports file changes, reads, checks, and tree add/remove. `IFileVisitor` supports full scans. `IFileMDSvc` exposes lifecycle, async/sync fetch, existence check, cache drop, create/update/remove, counts, listeners, quota stats, container service wiring, visits, first-free-id, cache stats, and id blacklist.

Control flow: concrete implementations fetch or create `IFileMD`, persist updates/removals, notify listeners with `Event`, and support scans/blacklisting during startup or migration.

State and persistence: service implementations own file metadata persistence and cache state. Tree delta events propagate to container accounting/quota.

Dependencies and integration: depends on file/container metadata, identifiers, misc cache statistics, `MDException`, `MDLocking`, and folly futures. Used by `IView`, filesystem view, quota stats, and prefetcher.

Risks: `removeFile` comment requires callers to write-lock before removal, but the type system does not enforce it. Listener callbacks can be order-sensitive and may observe partially updated state if implementations are careless.

Test signals: async/sync fetch, `hasFileMD`, create/update/remove persistence, listener event contents, tree delta math, visitor scans, cache drop/stats, blacklist behavior, and write-lock precondition tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/namespace/interface/IFileMDSvc.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/namespace/interface/IFsView.hh -->
## sources/distributed-fs/eos/namespace/interface/IFsView.hh

Purpose: Defines the filesystem-location view that indexes files by storage filesystem, unlinked state, and no-replica state, and listens to file metadata changes.

Important APIs and types: `ICollectionIterator<T>` is the generic iterator interface. `IFsView::FileList` is a dense hash set of file ids. `IFsView` exposes configure, file change/read callbacks, file-list iterators, streaming iterators, erase, random file selection, counts, unlinked list access/clear, no-replica list access, filesystem id iterator, membership checks, finalize, and shrink.

Control flow: file metadata listener events update filesystem indexes. Callers request iterators for FST cleanup, balancing, repair, or prefetch; iterators expose current element, validity, and next.

State and persistence: concrete views maintain in-memory or persisted indexes mapping filesystem ids to file ids and unlinked/no-replica collections. `FileIterator` holds a reference to a list; `StupidFileSystemIterator` walks a numeric range.

Dependencies and integration: depends on `IFileMDSvc`, `IFileMDChangeListener`, `MDException`, Google dense hash set, Murmur hash, and standard sets. Used by prefetcher and MGM filesystem operations.

Risks: `FileIterator` references an external list, so the list must outlive the iterator and not mutate unsafely. Random selection is approximate by contract. Streaming and snapshot iterator semantics can differ by implementation.

Test signals: listener-driven index updates, unlinked transitions, no-replica tracking, iterator validity on empty/non-empty lists, random file behavior, clear unlinked list, and shrink/finalize lifecycle.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/namespace/interface/IFsView.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/namespace/interface/INamespaceGroup.hh -->
## sources/distributed-fs/eos/namespace/interface/INamespaceGroup.hh

Purpose: Defines an ownership/assembly interface for the full namespace stack: file service, container service, hierarchical view, filesystem view, accounting views, quota stats, stats sink, and cache refresh listener.

Important APIs and types: `initialize` takes a global namespace mutex, config map, error string, and namespace stats. Getters expose file/container services, hierarchical/filesystem views, sync-time accounting, container accounting, quota stats, and in-memory status. `startCacheRefreshListener` starts backend cache invalidation handling.

Control flow: callers construct a concrete namespace group, initialize it, then retrieve service/view pointers and wire MGM operations through them. Startup can fail via boolean/error string.

State and persistence: base class stores non-owning pointers to the global namespace mutex and stats interface. Concrete implementations own persistent/cached namespace components.

Dependencies and integration: depends on namespace stats, common `RWMutex`, metadata services, views, quota stats, and listeners. It is the high-level boundary between MGM and namespace implementation families.

Risks: returned pointers are raw and lifetime is owned by the group implementation. Initialization order matters because services and views depend on each other. Cache refresh listener behavior is backend-specific.

Test signals: initialization success/failure, all getters non-null after init, in-memory flag, listener startup, and teardown/lifetime behavior for concrete groups.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/namespace/interface/INamespaceGroup.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/namespace/interface/INamespaceStats.hh -->
## sources/distributed-fs/eos/namespace/interface/INamespaceStats.hh

Purpose: Defines a minimal stats sink used by namespace operations to report counters and execution timings to MGM statistics infrastructure.

Important APIs and types: `Add(tag, uid, gid, val)` increments a tagged user/group value, and `AddExec(tag, exectime)` records execution time.

Control flow: namespace code calls stats methods around operations; concrete MGM stats implementation handles aggregation.

State and persistence: interface has no state; concrete implementations may maintain runtime counters or export metrics.

Dependencies and integration: depends on namespace macros and sys uid/gid types. Comment states it mirrors MGM `Stat` API.

Risks: no ownership, thread-safety, or failure semantics are expressed; implementers must be safe for namespace call patterns.

Test signals: mock stats capture for namespace operations and concurrency tests for real stats implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/namespace/interface/INamespaceStats.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/namespace/interface/IQuota.hh -->
## sources/distributed-fs/eos/namespace/interface/IQuota.hh

Purpose: Defines quota accounting interfaces for per-container quota nodes and the quota stats manager.

Important APIs and types: `IQuotaNode` wraps `QuotaNodeCore` and exposes per-user/per-group logical space, physical space, and file counts, plus `addFile`, `removeFile`, `meld`, uid/gid enumeration, and core replace/update. `IQuotaStats` manages nodes, provides all ids, and registers a physical-size mapper.

Control flow: file/container accounting calls quota nodes to add/remove files and merge usage; quota stats registers/removes nodes keyed by container id. `getPhysicalSize` calls the registered mapper and throws if none is configured.

State and persistence: `IQuotaNode` stores a quota stats pointer, container id, and `QuotaNodeCore`. Concrete implementations decide whether accounting state is persisted, cached, or recomputed.

Dependencies and integration: depends on file/container metadata and QuarkDB `QuotaNodeCore`. Integrated with services via `setQuotaStats` and view quota-node registration.

Risks: `IQuotaNode` keeps raw quota stats pointer. `getPhysicalSize` throws a default `MDException` with no errno specialization when mapper is missing. Implementations must keep logical and physical accounting consistent with file layout/replica changes.

Test signals: add/remove file accounting, physical-size mapper registration/failure, meld semantics, uid/gid set enumeration, core replace/update, node registration/removal, and quota node id listing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/namespace/interface/IQuota.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/namespace/interface/IView.hh -->
## sources/distributed-fs/eos/namespace/interface/IView.hh

Purpose: Defines the hierarchical namespace view interface responsible for path lookup, creation, removal, symlink handling, URI reconstruction, quota-node operations, and service wiring.

Important APIs and types: service setters/getters, configure/initialize/finalize, async/sync `getFile` and `getContainer`, `getItem`, store updates, create/remove/unlink file, create/remove link, create/remove/rename container, parent lookup, URI and real-path resolution, quota node lookup/register/remove, quota stats setter/getter, file rename, and `inMemory`.

Control flow: callers use path-based operations through `IView`; implementations translate paths to metadata objects, handle symlink following and link depth, update services/backing stores, and maintain quota/view consistency.

State and persistence: concrete views own hierarchy relationships and coordinate persistent metadata updates through file/container services. The interface itself owns no state.

Dependencies and integration: central contract between MGM operations and namespace storage backends. Depends on file/container services, metadata interfaces, quota stats/nodes, folly futures, and `MDException`.

Risks: comments warn `getUri(IFileMD*)` must not be called with the file already locked because it can lock parent containers and deadlock. Multi-stage initialize methods (`initialize1/2/3`) imply ordering constraints. Symlink following/link-depth handling must prevent cycles.

Test signals: path lookup for files/containers/items, symlink resolution and depth limits, create/remove/unlink/rename flows, URI reconstruction without deadlock, quota-node registration/search, async future behavior, and in-memory no-op expectations in prefetcher.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/namespace/interface/IView.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/namespace/interface/Identifiers.hh -->
## sources/distributed-fs/eos/namespace/interface/Identifiers.hh

Purpose: Provides strong phantom types for file and container identifiers to prevent accidental mixing of raw `uint64_t` ids.

Important APIs and types: `FileIdentifier` and `ContainerIdentifier` have explicit `uint64_t` constructors, default zero construction, `getUnderlyingUInt64`, ordering, and equality. `FileOrContainerIdentifier` stores either a file id, a container id, or empty, and converts back with zero-on-wrong-type behavior. Murmur hash specializations allow identifier keys in hash containers.

Control flow: code constructs explicit identifiers at serialization/deserialization or API boundaries, compares them type-safely, and unwraps only when needed for storage or hashing.

State and persistence: each identifier stores a `uint64_t`; combined identifier stores value plus empty/file discriminator. Persisted representation remains the underlying integer, but source code gains type safety.

Dependencies and integration: depends on namespace macros and common Murmur hash. Used by metadata interfaces, services, resolver, and cache APIs.

Risks: default/failed conversion returns id zero, so callers must know whether zero is invalid in their context. `FileOrContainerIdentifier` can compare directly to either typed id but does not expose ordering/hash itself in this header.

Test signals: compile-time rejection of implicit integer conversions, equality/order behavior, wrong-type conversion returning zero, hash container use for file/container identifiers, and serialization boundary unwrap/rewrap.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/namespace/interface/Identifiers.hh -->
