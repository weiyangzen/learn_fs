# Research Group: subset-b-007925

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClParallelOperation.hh -->
# sources/distributed-fs/xrootd/src/XrdCl/XrdClParallelOperation.hh

## Purpose

This header implements the client pipeline combinator for running multiple `XrdCl::Pipeline` instances in parallel and collapsing their terminal statuses into one `Resp<void>` operation. It is part of the high-level operation DSL built on `XrdClOperations.hh`, `XrdClOperationHandlers.hh`, `DefaultEnv`, `PostMaster`, and the client `JobManager`.

## Important APIs, Types, And Functions

`PolicyExecutor` is the abstract policy interface with `Examine(const XRootDStatus&)` and `Result()`. `ParallelOperation<HasHndl>` derives from `ConcreteOperation<ParallelOperation, HasHndl, Resp<void>>` and owns a vector of pipelines plus a selected policy. Public policy builders are `All()`, `Any()`, `Some(threshold)`, and `AtLeast(threshold)`. Free functions `Parallel(container)` and variadic `Parallel(operations...)` convert operations/pipelines into a vector.

The private policy implementations are `AllPolicy`, `AnyPolicy`, `SomePolicy`, and `AtLeastPolicy`. `Ctx` owns the final `PipelineHandler`, the policy, and a barrier that prevents an early completion callback from firing before `RunImpl` has launched all child pipelines. `PipelineEnd` is a `Job` used to schedule policy examination on the client worker pool.

## Control Flow

Construction move-copies child pipelines out of an input container and clears the source container. `RunImpl` installs `AllPolicy` by default, creates a shared `Ctx`, computes an effective timeout as the minimum of the inherited pipeline timeout and this operation's timeout, starts each non-null child pipeline with a completion lambda, then lifts the barrier. Each completion lambda queues `PipelineEnd`; the job calls `Ctx::Examine`; when the policy says the aggregate result is determined, `Ctx::Handle` atomically exchanges the handler pointer to `nullptr` and calls `HandleResponse(new XRootDStatus(...), nullptr)` exactly once.

## State And Persistence Behavior

State is transient in memory. The operation owns moved child pipelines and a policy until `RunImpl`, then transfers policy ownership into `Ctx`. `Ctx` is shared by completion jobs, so it remains alive until queued completions release it. The only persisted state is side effects of child pipelines elsewhere; this header itself writes no files and stores no global state.

## Dependencies And Integration Points

The file integrates the operation DSL with `DefaultEnv::GetPostMaster()->GetJobManager()`, so aggregate completion runs through the same worker pool as other client callbacks. It depends on `PipelineHandler`, `Pipeline`, `Operation<HasHndl>`, `ConcreteOperation`, `XRootDStatus`, and the client environment singleton. It is intended for asynchronous multi-target client workflows such as mirrored operations, replication, or quorum-style metadata/file operations.

## Risks And Edge Cases

Threshold validation is not explicit: `Some(0)`, `AtLeast(0)`, or thresholds larger than the pipeline count can produce unintuitive behavior. `SomePolicy::Examine` declares `std::unique_lock<std::mutex> resMtx;`, which does not lock the member mutex and shadows the member name; that is a concurrency risk for `failed`, `succeeded`, and `res`. Early-return policies do not cancel outstanding child pipelines, so late completions still enqueue jobs but cannot call the final handler after the atomic exchange. `barrier_t::wait` uses a single `if` instead of a predicate loop, so spurious wakeups would weaken the "all children started first" guarantee.

## Test Signals

Useful tests should cover all four policies with mixed success/failure orderings, empty and null child entries, threshold boundary values, callbacks completing before all child pipelines are launched, and repeated late completions after final handler delivery. Thread sanitizer or stress tests around `SomePolicy` would be valuable because its lock appears ineffective.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClParallelOperation.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClPlugInInterface.hh -->
# sources/distributed-fs/xrootd/src/XrdCl/XrdClPlugInInterface.hh

## Purpose

This header defines the client-side plugin ABI for replacing or extending `XrdCl::File` and `XrdCl::FileSystem` behavior. It is intentionally broad: plugin implementations may override file open/read/write/control operations, filesystem metadata operations, extended attributes, and factory creation for URL-specific clients.

## Important APIs, Types, And Functions

`FilePlugIn` is the file-object interface. It mirrors `File` methods such as `Open`, `OpenUsingTemplate`, `Close`, `Stat`, `Read`, `PgRead`, `Write`, `PgWrite`, `Sync`, `Truncate`, `PreRead`, `VectorRead`, `VectorWrite`, `WriteV`, `Fcntl`, `Visa`, `IsOpen`, property accessors, `ExportTemplate`, and `Clone`. Most default implementations return `XRootDStatus(stError, errNotImplemented)`; `PreRead` returns success, `IsOpen` returns false, and template export returns an empty unique pointer.

`FileSystemPlugIn` mirrors `FileSystem` methods including `Locate`, `DeepLocate`, `Mv`, `Query`, path `Truncate`, `Rm`, `MkDir`, `RmDir`, `ChMod`, `Ping`, `Stat`, `StatVFS`, `Protocol`, `DirList`, `SendInfo`, `Prepare`, xattr operations, and property accessors. `PlugInFactory` creates `FilePlugIn` and `FileSystemPlugIn` instances for a URL.

## Control Flow

The header contains interface defaults only; dispatch happens in `File`, `FileSystem`, and `PlugInManager`. A consumer asks a factory to create a plugin for a URL, then forwards public client operations to the returned object. Implementations can be partial because unsupported methods fail with `errNotImplemented`.

## State And Persistence Behavior

The base classes keep no state. Implementations may maintain open handles, caches, clone templates, or backend-specific configuration. Ownership is raw-pointer based at the factory boundary: callers must know who owns returned plugin instances, while `PlugInManager` owns factories.

## Dependencies And Integration Points

The file includes `XrdClFile.hh`, `XrdClFileSystem.hh`, and `XrdClOptional.hh`, tying the plugin ABI to public file and filesystem request/response types such as `OpenFlags`, `Access`, `ResponseHandler`, `Buffer`, `ChunkList`, `TractList`, `QueryCode`, `DirListFlags`, `PrepareFlags`, `xattr_t`, `ExportedFileTemplate`, and `CloneLocations`.

## Risks And Edge Cases

The ABI uses many raw pointers and asynchronous handlers, so plugins must document ownership and callback behavior carefully. Default success for `PreRead` can hide missing prefetch support. Some methods accept file descriptors, buffers, or iovecs and must respect lifetime constraints after returning. Factory-created objects need ABI-compatible allocation/deallocation across shared libraries.

## Test Signals

Tests should register a fake plugin and verify that `File`/`FileSystem` route all supported operations, unsupported operations return `errNotImplemented`, properties round-trip, clone/template paths reject incompatible templates, and async response handlers are invoked exactly once.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClPlugInInterface.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClPlugInManager.cc -->
# sources/distributed-fs/xrootd/src/XrdCl/XrdClPlugInManager.cc

## Purpose

This implementation manages runtime discovery, loading, registration, lookup, and cleanup of XrdCl client plugins. It supports programmatic registration, an environment-selected default plugin, config-directory plugin definitions, and an optional built-in erasure-coding plugin path under `WITH_XRDEC`.

## Important APIs, Types, And Functions

`RegisterFactory(url, factory)` registers or removes a programmatic factory for a normalized URL. `RegisterDefaultFactory(factory)` installs/removes a default factory. `GetFactory(url)` resolves URL-specific, protocol-specific, environment, and default factories. `ProcessEnvironmentSettings()` loads `PlugIn`/`PlugInConfDir` settings from `DefaultEnv`. `ProcessConfigDir` scans sorted `.conf` files. `ProcessPlugInConfig` parses mandatory `url`, `lib`, and `enable` keys. `LoadFactory` loads `XrdClGetPlugIn` via `XrdOucPinLoader`. The private `RegisterFactory(urlString, lib, factory, plugin)` handles semicolon-separated config URL registration and ownership sharing.

## Control Flow

Environment processing first checks `PlugIn`; if set, it attempts to load that library as a default factory and disables config scanning. Otherwise it scans `/etc/xrootd/client.plugins.d`, the user's `~/.xrootd/client.plugins.d`, and `PlugInConfDir`. Config files are processed alphabetically so later files can supersede earlier ones. Enabled config entries load a factory, disabled entries remove normalized mappings. Lookups prefer an environment default, then exact environment mapping, then protocol environment mapping, then programmatic default, exact mapping, protocol mapping.

## State And Persistence Behavior

`pFactoryMap` maps normalized URL/protocol strings to `FactoryHelper` objects. Helpers own a plugin loader and factory and carry `isEnv` plus a reference counter because one helper can be shared by multiple URL keys. `pDefaultFactory` owns the default helper. All public mutations and lookups are protected by `pMutex`. No registry state is persisted; config is reread only when `ProcessEnvironmentSettings` is invoked.

## Dependencies And Integration Points

The implementation depends on `DefaultEnv`, `Env`, `Log`, `Utils::GetDirectoryEntries`, `Utils::ProcessConfig`, `Utils::splitString`, `URL`, `XrdSysPwd`, `XrdOucPinLoader`, and version symbols from `XrdVersion.hh`. Plugin libraries must export `extern "C" void *XrdClGetPlugIn(const void *arg)` returning a `PlugInFactory*` and accepting the config map pointer.

## Risks And Edge Cases

`ProcessEnvironmentSettings` allocates `pDefaultFactory` even when `LoadFactory` returns a null loader/factory for the `PlugIn` path, so failed default loading can still leave an env default helper with null factory. Programmatic registration cannot override environment plugins. Counter management is manual; incorrect sharing/removal can leak or double-delete factories. Config docs mention `enabled`, while code requires `enable`. `NormalizeURL` rejects invalid URL strings and collapses wildcard hostnames to protocol-only keys.

## Test Signals

Tests should cover exact URL, wildcard host/protocol, and default precedence; disabling config entries; multiple URLs sharing one factory; failed library load; invalid config keys; programmatic override rejection for env entries; and destructor cleanup. Integration tests should load a minimal shared plugin exporting `XrdClGetPlugIn`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClPlugInManager.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClPlugInManager.hh -->
# sources/distributed-fs/xrootd/src/XrdCl/XrdClPlugInManager.hh

## Purpose

This header declares `PlugInManager`, the central registry that maps client URLs to plugin factories and owns dynamically loaded plugin libraries. It provides the public API used by the client environment and by programmatic plugin installers.

## Important APIs, Types, And Functions

Public methods are the constructor/destructor, `RegisterFactory(const std::string&, PlugInFactory*)`, `RegisterDefaultFactory(PlugInFactory*)`, `GetFactory(std::string)`, and `ProcessEnvironmentSettings()`. Private support includes `PlugInFunc_t`, `FactoryHelper`, `ProcessConfigDir`, `ProcessPlugInConfig`, `LoadFactory`, config-aware `RegisterFactory`, and `NormalizeURL`.

`FactoryHelper` owns `XrdOucPinLoader *plugin` and `PlugInFactory *factory`, records whether the entry came from environment/config (`isEnv`), and maintains a `counter` for shared helper entries.

## Control Flow

The public registration APIs normalize URLs and mutate the map under a mutex. Environment processing is a separate explicit call that can load a default plugin or scan config directories. Lookups return non-owned factory pointers. The private config registration path can associate one factory with multiple normalized URLs or install a config default for `url=*`.

## State And Persistence Behavior

`pFactoryMap` and `pDefaultFactory` are in-memory only. The manager owns factories and plugin loaders through `FactoryHelper`; callers do not own pointers returned by `GetFactory`. `pMutex` serializes access.

## Dependencies And Integration Points

The class depends on `XrdClPlugInInterface.hh`, `XrdOucPinLoader`, and `XrdSysMutex`. It is normally reachable through `DefaultEnv`, and plugin implementations must use the `PlugInFactory` ABI declared in the interface header.

## Risks And Edge Cases

The API uses raw factory pointers and ownership transfer, so callers must not delete registered factories. `GetFactory` takes `url` by value rather than const reference. Environment-derived factories are protected from programmatic replacement. A helper can be referenced by several map keys, making counter correctness central to safe destruction.

## Test Signals

Header-level contract tests should assert that registering null removes mappings/defaults, returned factories are non-owned, environment entries take precedence, and invalid URLs are rejected without altering existing state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClPlugInManager.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClPoller.hh -->
# sources/distributed-fs/xrootd/src/XrdCl/XrdClPoller.hh

## Purpose

This header defines the socket event polling abstraction used by XrdCl channels. It separates transport/channel logic from the concrete polling backend and gives socket handlers a small callback interface for readiness and timeout events.

## Important APIs, Types, And Functions

`SocketHandler` declares event bits `ReadyToRead`, `ReadTimeOut`, `ReadyToWrite`, and `WriteTimeOut`, optional lifecycle hooks `Initialize(Poller*)` and `Finalize()`, required `Event(uint8_t, Socket*)`, and `EventTypeToString`. `Poller` declares lifecycle methods `Initialize`, `Finalize`, `Start`, `Stop`, socket registration/removal, `ShutdownEvents`, read/write notification toggles with timeouts, `IsRegistered`, and `IsRunning`.

## Control Flow

Channels create or receive sockets, register them with a `Poller`, and use `EnableReadNotification`/`EnableWriteNotification` to arm callbacks. Concrete pollers translate OS/backend events into `SocketHandler::Event` calls. `ShutdownEvents` is the non-removal path for suppressing future callbacks before or during teardown.

## State And Persistence Behavior

The header has no state. Implementations are expected to keep socket-to-handler/channel maps and event-arm state. There is no persistence.

## Dependencies And Integration Points

This is consumed by `PollerBuiltIn`, `PostMaster`, and `Channel` code. It depends only on forward declarations for `Socket` and `Poller` plus standard integer/time/string headers.

## Risks And Edge Cases

`EventTypeToString` erases the last character even when no event bits are set, which can underflow on an empty string. Removal semantics warn that `RemoveSocket` may block on backend dispatch loops; callers that need quick callback suppression should use `ShutdownEvents`. Implementers must define timeout behavior consistently because channel retry logic depends on these event bits.

## Test Signals

Tests should verify event bit translation, initialization/finalization order, read/write enable/disable idempotence, callback suppression via `ShutdownEvents`, and behavior for empty/unknown event masks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClPoller.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClPollerBuiltIn.cc -->
# sources/distributed-fs/xrootd/src/XrdCl/XrdClPollerBuiltIn.cc

## Purpose

This file implements `PollerBuiltIn`, the concrete `Poller` backed by `XrdSys::IOEvents::Poller` and `IOEvents::Channel`. It manages multiple poller threads, socket registration, event callback translation, read/write notification state, and safe callback shutdown.

## Important APIs, Types, And Functions

Private `PollerHelper` stores an IOEvents channel, callback, enabled flags, and timeouts. Private `SocketCallBack` translates IOEvents flags to `SocketHandler` flags and invokes the user handler. Its nested `DisableControl` coordinates `ShutdownEvents` with in-flight callbacks. `PollerBuiltIn` implements lifecycle, `AddSocket`, `RemoveSocket`, `ShutdownEvents`, read/write notification toggles, `IsRegistered`, `GetNextPoller`, `RegisterAndGetPoller`, `UnregisterFromPoller`, `GetPoller`, and `GetNbPollerInit`.

## Control Flow

`Start` creates `pNbPoller` backend pollers, initializes round-robin state, and reattaches any sockets stored while stopped, re-enabling saved read/write notifications. `AddSocket` validates status, assigns a backend poller by file descriptor, creates a callback/channel, calls `handler->Initialize(this)`, and stores the helper. Notification methods update helper state and enable/disable backend channel event masks if a backend poller exists. `Stop` stops and deletes backend pollers, clears fd-to-poller mappings, disables/deletes live channels, and leaves helper registration state for a later `Start`. `Finalize` deletes remaining helpers and callbacks.

## State And Persistence Behavior

State is in-memory: `pSocketMap` maps `Socket*` to helper objects, `pPollerMap` maps file descriptors to backend pollers, `pPollerPool` owns backend pollers while running, and `pNext` implements round-robin assignment. `pMutex` protects those structures. No state persists across process lifetime.

## Dependencies And Integration Points

The implementation uses `XrdSysIOEvents`, `XrdSysPthread`, `XrdSysE2T`, `DefaultEnv`, `Env`, `Log`, `Constants`, `Socket`, and optimizer macros. It is created by `PollerFactory` and owned by `PostMaster`.

## Risks And Edge Cases

Callback teardown is delicate: handlers may remove their own socket during `Event`, so `SocketCallBack` saves the control object before invoking the handler. `ShutdownEvents` waits unless called from the same callback thread. `Stop` and `RemoveSocket` unlock while stopping/deleting backend objects, so concurrent channel operations must follow poller locking expectations. Backend creation failure after some pollers are created returns false without cleaning already-created pollers in that path. `EventTypeToString` inherited empty-mask risk can be triggered by backend flags that map to no known bits.

## Test Signals

Tests should register sockets, enable/disable notifications, simulate callback self-removal, call `ShutdownEvents` during an in-flight callback, stop/start with registered sockets, and verify multiple sockets are assigned round-robin across configured `ParallelEvtLoop` pollers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClPollerBuiltIn.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClPollerBuiltIn.hh -->
# sources/distributed-fs/xrootd/src/XrdCl/XrdClPollerBuiltIn.hh

## Purpose

This header declares the built-in XrdCl poller implementation. It adapts the generic `Poller` interface to XRootD's internal IOEvents pollers and supports multiple event-loop threads.

## Important APIs, Types, And Functions

`PollerBuiltIn` overrides all `Poller` methods: lifecycle, socket registration/removal, callback shutdown, read/write notification toggles, registration checks, and `IsRunning`. Private helpers select/associate backend pollers: `GetNextPoller`, `RegisterAndGetPoller`, `UnregisterFromPoller`, `GetPoller`, and `GetNbPollerInit`. Type aliases define `PollerMap`, `SocketMap`, and `PollerPool`.

## Control Flow

Construction initializes `pNbPoller` from the environment via `GetNbPollerInit`. Public calls delegate to implementation logic in the `.cc` file while shared structures are protected by `pMutex`.

## State And Persistence Behavior

The object owns socket-helper registrations and backend poller pointers while active. `IsRunning` is defined as non-empty `pPollerPool`. State survives `Stop` enough to permit restart with previous registrations, but not process persistence.

## Dependencies And Integration Points

The header depends on `XrdSysPthread`, `XrdClPoller`, and forward declarations for `XrdSys::IOEvents::Poller` and `AnyObject`. It is the only built-in implementation registered by `PollerFactory`.

## Risks And Edge Cases

Socket maps use raw `Socket*` keys and raw helper pointers, so ownership/lifetime must be managed externally by channels. The class assumes file descriptors uniquely identify backend-poller assignment while registered. Restart behavior depends on helper flags matching backend channel state.

## Test Signals

Compile and lifecycle tests should verify that all virtual methods are implemented, `IsRunning` tracks backend pool state, and configured `ParallelEvtLoop` values affect `pNbPoller`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClPollerBuiltIn.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClPollerFactory.cc -->
# sources/distributed-fs/xrootd/src/XrdCl/XrdClPollerFactory.cc

## Purpose

This file implements `PollerFactory::CreatePoller`, which chooses a concrete socket event poller from a comma-separated preference list. In this source snapshot the only registered backend is `"built-in"`.

## Important APIs, Types, And Functions

The anonymous `createBuiltIn()` returns `new PollerBuiltIn()`. `CreatePoller(preference)` builds a local map from poller names to creator functions, logs available pollers, splits the preference string with `Utils::splitString`, and returns the first matching implementation.

## Control Flow

If `preference` is empty, the function logs an error and returns null. Otherwise it iterates preference tokens in order. Unknown tokens are logged at debug level and skipped. The first known token creates and returns a poller immediately. If no token matches, the function returns null.

## State And Persistence Behavior

There is no persistent state and no static registry beyond the function-local map rebuilt on each call. The caller owns the returned `Poller*`.

## Dependencies And Integration Points

The factory includes `PollerFactory.hh`, `PollerBuiltIn.hh`, `Constants`, `Log`, `Utils`, and `DefaultEnv`. `PostMaster::Initialize` calls it using the environment's `PollerPreference` value.

## Risks And Edge Cases

Preference tokens are not trimmed here; split behavior determines whether `"built-in, other"` matches the second token. The registry is not externally extensible without source changes. A null return prevents `PostMaster` initialization.

## Test Signals

Tests should cover empty preference, known first token, unknown tokens before known token, all-unknown preferences, and logging/ownership expectations for the created poller.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClPollerFactory.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClPollerFactory.hh -->
# sources/distributed-fs/xrootd/src/XrdCl/XrdClPollerFactory.hh

## Purpose

This header declares the small factory responsible for creating `Poller` implementations from a runtime preference string.

## Important APIs, Types, And Functions

`PollerFactory` exposes one static method: `CreatePoller(const std::string &preference)`. It returns a newly allocated `Poller*` or null if no preferred implementation is known.

## Control Flow

The header defines the contract only. The `.cc` implementation parses a comma-separated preference list and picks the first available backend.

## State And Persistence Behavior

No state is declared. Ownership of returned pollers belongs to the caller.

## Dependencies And Integration Points

The header includes `XrdClPoller.hh` and is used by `PostMaster` during initialization. It decouples environment configuration from concrete poller classes.

## Risks And Edge Cases

Because the API returns a raw pointer, callers must delete the poller on failure paths and final shutdown. A null return is a hard startup failure for client networking.

## Test Signals

Compile-time tests should include the header from PostMaster-like code; runtime tests belong to the implementation and should verify null handling by `PostMaster::Initialize`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClPollerFactory.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClPostMaster.cc -->
# sources/distributed-fs/xrootd/src/XrdCl/XrdClPostMaster.cc

## Purpose

This file implements `PostMaster`, the central XrdCl hub for asynchronous message delivery, channel creation, polling, task execution, job callbacks, transport queries, redirects, and forced connection lifecycle operations.

## Important APIs, Types, And Functions

`PostMasterImpl` owns `Poller`, `TaskManager`, `JobManager`, a channel map keyed by `URL::GetChannelId()`, a non-owning finalize set, mutexes, and global connect/error handlers. `PostMaster::Initialize`, `Start`, `Stop`, and `Finalize` manage subsystem lifecycle. `Send` obtains/creates a `Channel` and delegates. `Redirect` delegates to `RedirectorRegistry`. Query/event/disconnect/reconnect methods locate channels and delegate. `CollapseRedirect` replaces an alias channel with an active channel labeled by a redirected URL. `PostMasterImpl::GetChannel` creates channels with the protocol `TransportHandler`.

## Control Flow

Initialization reads `PollerPreference`, creates and initializes a poller, then initializes the job manager. Start order is poller, task manager, job manager; failures roll back already-started subsystems. Stop order is job manager, poller, task manager. Finalize stops job callbacks, copies the finalize set, finalizes channels, clears the channel map, and finalizes the poller.

For send paths, `GetChannel` locks the map, locates or creates a `Channel` using `TransportManager::GetHandler(protocol)`, stores a `shared_ptr` with a custom deleter that removes it from the finalize set, then returns it. Most public channel operations use this helper or locked map lookup.

## State And Persistence Behavior

State is process-local. Channels are shared pointers in `pChannelMap`; the finalize set tracks live raw channel pointers for cleanup. `pRunning` and `pInitialized` gate lifecycle methods. Global connection callbacks are stored under `pMtx` and queued on `JobManager`. There is no disk persistence.

## Dependencies And Integration Points

PostMaster depends on `PollerFactory`, `XRootDTransport`, `Message`, `DefaultEnv`, `TaskManager`, `JobManager`, `TransportManager`, `Channel`, `RedirectorRegistry`, and `Log`. It is accessed through `DefaultEnv` by operations and transport code.

## Risks And Edge Cases

`Finalize` assumes no concurrency because poller and job manager are stopped; callers must respect lifecycle ordering. `NotifyConnectHandler` queues the same stored `Job` pointer with newly allocated `URL` args, so the job implementation must tolerate repeated runs and own/free args as expected by `JobManager`. `CollapseRedirect` retries recursively if the map changes; pathological churn could recurse repeatedly. `ForceDisconnect` erases channels before delegation, so callers cannot query that channel afterward. `Reinitialize` is a stub returning true and does not rebuild post-fork resources.

## Test Signals

Tests should cover lifecycle ordering/failure rollback, send channel creation, protocol handler absence, channel map reuse by channel ID, forced disconnect/reconnect, redirect collapse aliasing, global connect/error handler queuing, and finalization while channels remove themselves from the finalize set.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClPostMaster.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClPostMaster.hh -->
# sources/distributed-fs/xrootd/src/XrdCl/XrdClPostMaster.hh

## Purpose

This header declares `PostMaster`, the public facade for XrdCl's asynchronous network messaging subsystem. It hides `PostMasterImpl` and exposes lifecycle, send, redirect, channel query, event-handler, and connection-control APIs.

## Important APIs, Types, And Functions

Important methods include `Initialize`, `Finalize`, `Start`, `Stop`, `Reinitialize`, `Send`, `Redirect`, `QueryTransport`, `RegisterEventHandler`, `RemoveEventHandler`, `GetTaskManager`, `GetJobManager`, `ForceDisconnect`, `ForceReconnect`, `NbConnectedStrm`, `SetOnDataConnectHandler`, `SetOnConnectHandler`, `SetConnectionErrorHandler`, `NotifyConnectHandler`, `NotifyConnErrHandler`, `CollapseRedirect`, `DecFileInstCnt`, and `IsRunning`.

## Control Flow

The header contract makes `PostMaster` the layer that callers use instead of constructing channels directly. Messages are submitted with a destination `URL`, `Message*`, `MsgHandler*`, statefulness flag, and expiration time. Channel-level event and disconnect operations are all URL-addressed.

## State And Persistence Behavior

The visible class owns a `std::unique_ptr<PostMasterImpl>`. All state is hidden in the implementation. No persistence is part of the public contract.

## Dependencies And Integration Points

The header depends on `Status`, `URL`, `PostMasterInterfaces`, `XrdSysPthread`, and forward declarations for `Poller`, `TaskManager`, `Channel`, `JobManager`, and `Job`. It is used by `DefaultEnv`, operations, file/filesystem code, and transport/channel internals.

## Risks And Edge Cases

The `Send` comment warns about deadlocks if callers hold locks that callbacks also need. Many APIs accept raw handler/job pointers with async behavior; lifetime must outlive registration or be transferred according to channel/job manager conventions. `Reinitialize` is promised for fork handling but implemented as a no-op.

## Test Signals

Public API tests should verify lifecycle idempotence, URL-addressed handler registration/removal, disconnected URL errors, async send insertion status, and no deadlocks when callbacks are delivered through `JobManager`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClPostMaster.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClPostMasterInterfaces.hh -->
# sources/distributed-fs/xrootd/src/XrdCl/XrdClPostMasterInterfaces.hh

## Purpose

This header defines the interfaces between channels, message handlers, and protocol transports. It is the core contract that lets PostMaster and Channel code handle XRootD and other transports uniformly.

## Important APIs, Types, And Functions

`MsgHandler` declares action flags (`Ignore`, `RemoveHandler`, `Raw`, `NoProcess`, `Corrupted`, `More`, etc.), stream events, message examination, status inspection, SID access, processing, optional raw body read/write hooks, stream-event handling, send-status notification, ready/waiting send hooks, raw-write detection, and expiration.

`ChannelEventHandler` receives channel events and returns whether it remains registered. `HandShakeData` carries handshake messages, URL, substream, start time, server address, client/stream names. `PathID` identifies upstream/downstream stream choices. Query structs define transport, XRootD, and stream query IDs. `TransportHandler` declares transport operations for parsing messages, initializing/finalizing channel data, handshaking, stream health, multiplexing, disconnect cleanup, queries, stream actions, sent/received notifications, encryption, signatures, file-instance count, and bind preferences.

## Control Flow

Channels use `TransportHandler` to initialize protocol-specific channel data, perform per-stream handshakes, choose streams for outbound messages, parse inbound headers/bodies, and react to received control messages. Incoming messages are offered to `MsgHandler::Examine`; handler action bits drive whether the message is ignored, processed, read raw, or causes handler removal/disconnect. Channel event handlers observe stream readiness/failure independently from request handlers.

## State And Persistence Behavior

This header declares contracts only. State is carried through `AnyObject &channelData`, `HandShakeData`, messages, and handler implementations. No persistence is defined.

## Dependencies And Integration Points

The file depends on XrdCl response/status types, `AnyObject`, `URL`, `Message`, `Socket`, and `XrdNetAddr`. It is implemented by XRootD transport code and consumed by `Channel`, `PostMaster`, request handlers, and redirect handling.

## Risks And Edge Cases

Action flags are bitmasks, so combinations must be handled consistently by channel code. Raw read/write hooks bypass normal message body buffering and must only return socket-related errors. `TransportHandler` owns a large, stateful protocol contract; incomplete implementations can break reconnect, multiplexing, encryption, or request matching. Query ID ranges have comments that appear inconsistent for stream IDs, so extension authors should check existing usage.

## Test Signals

Transport conformance tests should exercise partial header/body reads with retry, handshake progress/failure, stream TTL/broken detection, multiplex and substream hints, raw handler reads/writes, action flag combinations, encryption decision paths, and query responses for transport name/auth/protocol/encryption and stream address values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClPostMasterInterfaces.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClPropertyList.hh -->
# sources/distributed-fs/xrootd/src/XrdCl/XrdClPropertyList.hh

## Purpose

This header implements `PropertyList`, a small string-backed key/value container with templated typed set/get helpers and specializations for XrdCl status, URL, and string-vector values.

## Important APIs, Types, And Functions

`PropertyList::Set(name, value)` streams arbitrary values into strings. `Get(name, item)` streams strings back into an output item and returns whether a key/conversion exists. `Get<Item>(name)` returns the converted value or `Item()`. Indexed overloads store keys as `"name index"`. `HasProperty`, iterators, and `Clear` expose map operations.

Specializations preserve full strings without stream tokenization, serialize `XRootDStatus` as `status;code;errNo#errorMessage`, serialize `URL` as `URL::GetURL()`, and serialize `std::vector<std::string>` as numbered repeated properties.

## Control Flow

Setters update `pProperties`. Generic getters locate the key, stream into the requested type, and fail only on `bad()`. Vector get loops from index zero until the indexed property is missing, appending values in order.

## State And Persistence Behavior

State is an in-memory `std::map<std::string, std::string>`. There is no built-in persistence, but the string map can be iterated for external serialization.

## Dependencies And Integration Points

The header includes `XrdClXRootDResponses.hh`, which supplies `XRootDStatus` and `URL` dependencies. Property lists are a common utility for passing structured metadata through APIs that need generic string properties.

## Risks And Edge Cases

Generic conversion checks `i.bad()` but not `fail()`, so malformed input may be accepted with default/partial values. Indexed keys use spaces despite the `name must not contain spaces` comment, so callers must avoid ambiguous names. Vector serialization does not store a length; missing middle indices truncate reads. `XRootDStatus` serialization uses `#` and semicolons as separators and assumes status message handling remains compatible.

## Test Signals

Tests should cover string values containing spaces, numeric conversion failures, indexed properties, vector round trips with missing middle entries, status error-message preservation, URL parsing, iteration order, and `Clear`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClPropertyList.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClRedirectorRegistry.cc -->
# sources/distributed-fs/xrootd/src/XrdCl/XrdClRedirectorRegistry.cc

## Purpose

This file implements a singleton registry for virtual metadata redirectors, currently Metalink redirectors. It lets the client register a metadata URL, later route requests through a local virtual redirector, and release redirectors when users are done.

## Important APIs, Types, And Functions

`RedirectJob::Run` delivers a synthetic message to a `MsgHandler` via `Examine` and `Process`. `RedirectorRegistry::Instance` returns the singleton. `RegisterImpl` normalizes localfile URLs, validates supported protocols/formats, ref-counts existing redirectors, creates `MetalinkRedirector` for Metalink URLs, loads it, and stores it. `Register`, `RegisterAndWait`, `Get`, and `Release` wrap registry operations. `ConvertLocalfile` maps deprecated `root://localfile//...` URLs to `file://localhost/...` when enabled.

## Control Flow

Registration first converts deprecated localfile syntax, rejects URLs without paths and non-local `file://` URLs, then locks the registry. Existing entries increment their user counter and optionally notify a handler with success. New Metalink entries allocate and load a redirector; successful loads are stored with count one. `RegisterAndWait` uses `SyncResponseHandler` plus `MessageUtils::WaitForStatus`. `Release` decrements the count and deletes/erases at zero.

## State And Persistence Behavior

`pRegistry` maps `URL::GetLocation()` to `(VirtualRedirector*, useCount)`. It is protected by `pMutex`. The registry owns redirectors and deletes them in `Release` or destructor. Metalink content is loaded by redirector implementation; this file only stores the object.

## Dependencies And Integration Points

The file depends on `MetalinkRedirector`, `PostMasterInterfaces`, `DefaultEnv`, constants, logging, and response utilities. `PostMaster::Redirect` calls `RedirectorRegistry::Get(url)` and delegates to `VirtualRedirector::HandleRequest`.

## Risks And Edge Cases

`RegisterImpl` holds the mutex while constructing/loading a new `MetalinkRedirector`; if loading invokes callbacks that reenter the registry, that could be risky. `Get` returns a raw pointer without incrementing the use count, so callers must coordinate lifetime with prior `Register`. Deprecated URL conversion depends on `LocalMetalinkFile`. Only Metalink is supported; other metadata formats return `errNotSupported`.

## Test Signals

Tests should register Metalink URLs asynchronously and synchronously, ref-count duplicate registration/release, verify deprecated localfile conversion and warning path, reject non-local file URLs and URLs without paths, and route a message through `PostMaster::Redirect` to a fake handler.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClRedirectorRegistry.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClRedirectorRegistry.hh -->
# sources/distributed-fs/xrootd/src/XrdCl/XrdClRedirectorRegistry.hh

## Purpose

This header declares the virtual redirector abstraction and singleton registry used to emulate redirector responses from metadata files such as Metalink documents.

## Important APIs, Types, And Functions

`RedirectJob` is a `Job` that runs a message handler on a synthetic redirect message. `VirtualRedirector` declares `HandleRequest`, `Load`, metadata accessors (`GetTargetName`, `GetCheckSum`, `GetSupportedCheckSums`, `GetSize`, `GetReplicas`), and `Count`. `RedirectorRegistry` exposes `Instance`, destructor, `Register`, `RegisterAndWait`, `Get`, and `Release`. Private `RegisterImpl` and `ConvertLocalfile` support implementation details.

## Control Flow

Clients register a metadata URL before use, obtain redirector responses indirectly through `PostMaster::Redirect`, and call `Release` when done. The registry is a non-copyable singleton backed by a map from URL location to redirector pointer and reference count.

## State And Persistence Behavior

The registry stores `RedirectorMap` in memory and protects it with `XrdSysMutex`. Redirectors are owned by the registry. No on-disk state is written by the registry.

## Dependencies And Integration Points

The header depends on XRootD response types, URL, JobManager, XrdSys mutexes, and STL containers. Implementations are expected to include concrete redirectors such as `MetalinkRedirector`.

## Risks And Edge Cases

`Get` returns a raw pointer and does not retain it. The registry API relies on external register/release discipline. `VirtualRedirector::GetReplicas` returns a const reference, so concrete redirector lifetime must outlive readers.

## Test Signals

Interface tests should use a fake `VirtualRedirector` or Metalink fixture to validate ref-counted registration, raw-pointer lookup, release deletion, and metadata accessor behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClRedirectorRegistry.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClRequestSync.hh -->
# sources/distributed-fs/xrootd/src/XrdCl/XrdClRequestSync.hh

## Purpose

This header implements `RequestSync`, a small semaphore-based helper for running a fixed number of asynchronous or threaded requests with a concurrency quota and waiting for all completions.

## Important APIs, Types, And Functions

The constructor accepts total request count and parallel quota. `WaitForQuota()` blocks until a quota slot is available. `TaskDone(success)` releases a quota slot, decrements remaining count, optionally increments failure count, and posts the completion semaphore when all requests are done. `WaitForAll()` waits for total completion. `FailureCount()` returns the number of failed tasks.

## Control Flow

Callers typically loop over requests, call `WaitForQuota` before launching each one, and call `TaskDone` from each completion path. A separate caller can call `WaitForAll` to block until `pRequestsLeft` reaches zero. If `reqTotal` is zero, the constructor posts the total semaphore immediately.

## State And Persistence Behavior

State is in-memory: two heap-allocated `XrdSysSemaphore` objects, `pRequestsLeft`, `pFailureCounter`, and a mutex for updates. Copy and assignment are private and undefined to prevent accidental copying.

## Dependencies And Integration Points

The class depends only on `XrdSysPthread.hh`. It is useful in higher-level client batch operations that need bounded parallelism without adopting a full task framework.

## Risks And Edge Cases

`FailureCount()` reads `pFailureCounter` without locking, so concurrent reads during active completions may race. If a launched task never calls `TaskDone`, both quota and total waits can block forever. Quota zero would create a semaphore that never permits launches.

## Test Signals

Tests should cover zero total requests, quota limiting, success/failure counts, all-completion wakeup, and misuse cases such as missing `TaskDone` or zero quota under timeout-controlled tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClRequestSync.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClResponseJob.hh -->
# sources/distributed-fs/xrootd/src/XrdCl/XrdClResponseJob.hh

## Purpose

This header defines `ResponseJob`, a `JobManager` task that invokes a user `ResponseHandler` asynchronously with status, response object, and host-list pointers.

## Important APIs, Types, And Functions

`ResponseJob` stores `ResponseHandler *pHandler`, `XRootDStatus *pStatus`, `AnyObject *pResponse`, and `HostList *pHostList`. Its `Run(void*)` calls `pHandler->HandleResponseWithHosts(pStatus, pResponse, pHostList)` and deletes the job object.

## Control Flow

Producer code allocates a `ResponseJob` and queues it on `JobManager`. When a worker runs it, ownership of response payload pointers is effectively handed to the handler according to `HandleResponseWithHosts` conventions, and the job self-deletes.

## State And Persistence Behavior

State is transient and owned by the job until `Run`. The job does not persist data. It does not delete the payload pointers itself, so handler ownership rules are critical.

## Dependencies And Integration Points

The header depends on `XrdClJobManager.hh` and `XrdClXRootDResponses.hh`. It is a common bridge between internal async completion and public response callback delivery.

## Risks And Edge Cases

Raw pointers must remain valid until the job runs. A null handler would crash. Because the job deletes itself, it must be heap-allocated and must not be reused after queuing. Handler exceptions, if any, are not caught here.

## Test Signals

Tests should queue a `ResponseJob` with a fake handler, verify exact pointer delivery, confirm self-deletion under leak checks, and exercise null/invalid pointer behavior only under guarded negative tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClResponseJob.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClSIDManager.cc -->
# sources/distributed-fs/xrootd/src/XrdCl/XrdClSIDManager.cc

## Purpose

This file implements XRootD stream/request ID allocation and pooling. `SIDManager` tracks allocated, free, and timed-out 16-bit SIDs for one channel, while `SIDMgrPool` shares managers by channel ID and recycles them when no users remain.

## Important APIs, Types, And Functions

`SIDManager::AllocateSID` returns a two-byte SID from `pFreeSIDs` or from monotonically increasing `pSIDCeiling`, failing with `errNoMoreFreeSIDs` at `0xffff`. `ReleaseSID` returns an active SID to the free list. `TimeOutSID` moves a SID into the timed-out set. `IsAnySIDOldAs`, `IsTimedOut`, `ReleaseTimedOut`, `ReleaseAllTimedOut`, and `GetNumberOfAllocatedSIDs` inspect or recycle state. `SIDMgrPool::GetSIDMgr` returns a `shared_ptr<SIDManager>` with a custom deleter; `Recycle` decrements refcount and deletes/removes unused managers.

## Control Flow

Allocation and release copy between a `uint16_t` and a two-byte array using `memcpy`, matching protocol SID storage. Pool lookup locks the global pool, creates or finds a manager by `URL::GetChannelId()`, increments the manager refcount under the manager mutex, and returns a shared pointer. The custom deleter calls `Recycle`, which locks pool then manager in the same order and deletes when refcount reaches zero.

## State And Persistence Behavior

SID state is in-memory per manager: allocation timestamps, free list, timed-out set, ceiling, and refcount. The singleton pool is intentionally leaked via a static pointer to avoid shutdown-order issues. No state is persisted.

## Dependencies And Integration Points

The implementation depends on `XrdClSIDManager.hh`, `URL`, `Status`, XrdSys mutexes, and standard containers. Channels and request handlers use managers to assign XRootD SIDs and detect stale/timed-out requests.

## Risks And Edge Cases

Released SIDs are not checked for duplicate release, so a bad caller can enqueue the same SID multiple times. Timed-out SIDs are excluded from allocated count until released. Endianness follows local memory layout for the two-byte array; this must match the rest of XrdCl protocol handling. `Recycle` scans the pool linearly by pointer when deleting.

## Test Signals

Tests should allocate/release/reuse SIDs, exhaust the ceiling, time out and release timed-out IDs, check stale allocation detection, verify per-channel manager sharing/refcount recycling, and stress concurrent allocation/release under thread sanitizers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClSIDManager.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClSIDManager.hh -->
# sources/distributed-fs/xrootd/src/XrdCl/XrdClSIDManager.hh

## Purpose

This header declares the SID allocation manager and its pool. It provides the data structures used by XrdCl channels to allocate, time out, recycle, and share stream/request IDs.

## Important APIs, Types, And Functions

`SIDManager` exposes `AllocateSID`, `ReleaseSID`, `TimeOutSID`, `IsAnySIDOldAs`, `IsTimedOut`, `ReleaseTimedOut`, `ReleaseAllTimedOut`, `NumberOfTimedOutSIDs`, and `GetNumberOfAllocatedSIDs`. Private state includes allocation times, free SIDs, timed-out SIDs, the next ceiling, mutex, and pool refcount.

`SIDMgrPool` exposes singleton `Instance`, `GetSIDMgr(URL)`, and `Recycle(SIDManager*)`. `RecycleSidMgr` is the custom shared-pointer deleter. Copy/move construction and assignment are deleted.

## Control Flow

Consumers obtain managers through `SIDMgrPool::GetSIDMgr`, not by constructing `SIDManager` directly. Managers are private-constructed and friend-accessed by the pool. Returned shared pointers recycle managers back through the pool on destruction.

## State And Persistence Behavior

The header defines in-memory state only. Managers are keyed by channel ID in the pool and deleted when their internal refcount reaches zero.

## Dependencies And Integration Points

It depends on STL containers, `XrdSysPthread`, `Status`, and `URL`. It integrates with XRootD request multiplexing where SIDs are two-byte protocol fields.

## Risks And Edge Cases

The manager uses mutable mutex/refcount so const inspection methods still lock. Refcount is separate from `shared_ptr` control blocks because every returned shared pointer uses the same raw manager pointer with a custom deleter. Correct pool locking order is required to avoid deadlocks.

## Test Signals

Header/API tests should verify deleted copy operations, private construction, shared manager identity for equal channel IDs, distinct managers for distinct channel IDs, and safe destruction through the custom deleter.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClSIDManager.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClSocket.cc -->
# sources/distributed-fs/xrootd/src/XrdCl/XrdClSocket.cc

## Purpose

This file implements the XrdCl socket wrapper. It provides nonblocking TCP setup, connect helpers, blocking raw read/write loops, async-friendly send/read wrappers, polling, peer-name caching, errno classification, TCP corking, and TLS handshaking support.

## Important APIs, Types, And Functions

Key methods are constructor/destructor, `Initialize`, `SetFlags`, `GetFlags`, `GetSockOpt`, `SetSockOpt`, `Connect`, `ConnectToAddress`, `Close`, `ReadRaw`, `WriteRaw`, overloads of `Send`, `Poll`, `GetSockName`, `GetPeerName`, `GetName`, `ClassifyErrno`, `Read`, `ReadV`, `Cork`, `Uncork`, `Flash`, `MapEvent`, `TlsHandShake`, and `IsEncrypted`.

## Control Flow

`Initialize` creates an XrdSys socket, sets nonblocking flags, configures `TCP_NODELAY`, and installs platform SIGPIPE protection. `Connect` resolves host addresses and calls `ConnectToAddress`; timeout zero plus `EINPROGRESS` marks the socket `Connecting`, while successful synchronous connect marks it `Connected`. `ReadRaw`/`WriteRaw` loop until the requested size is transferred or timeout/error occurs, using `Poll` before `read`/`write`. Async-style `Send`, `Read`, and `ReadV` perform one syscall/TLS call and return `suRetry` for would-block cases. `Send(Message&)` advances the message cursor until fully written or retry/error.

## State And Persistence Behavior

The object stores file descriptor, connection status, server address, cached local/peer/name strings, protocol family, channel ID pointer, cork state, and optional TLS wrapper. `Close` shuts down TLS, closes the descriptor, clears cached names, and marks disconnected. State is process-local only.

## Dependencies And Integration Points

The implementation depends on `XrdClSocket.hh`, `Utils`, constants, `Message`, `DefaultEnv`, `Tls`, `XrdNetConnect`, `XrdSysFD`, POSIX sockets, `poll`, `fcntl`, `readv`, and TCP options. It is used by channel and transport code and interacts with `Poller` event mapping through `MapEvent`.

## Risks And Edge Cases

`ClassifyErrno(int error)` ignores its `error` parameter and switches on global `errno`, which is risky if callers pass a saved errno. `WriteRaw` uses plain `::write` instead of the SIGPIPE-safe `Send` helper. Timeout math uses `time(0)` seconds, so subsecond precision is unavailable and clock changes can affect waits. `Send(KernelBuffer)` is rejected over TLS. Name caching is mutable and not synchronized. Corking maps to `TCP_CORK` only where available and otherwise just updates the state flag.

## Test Signals

Tests should cover nonblocking initialization, async connect with `EINPROGRESS`, raw read/write success and timeout, would-block classification, remote close handling, message cursor reset on send error, TLS handshake success/failure, cork/flash behavior, and saved-errno classification correctness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClSocket.cc -->
