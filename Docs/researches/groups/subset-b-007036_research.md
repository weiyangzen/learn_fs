# Research Report: subset-b-007036

Work item: `subset-b-007036`

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/http/xrdhttp/EosMgmHttpHandler.cc -->
# sources/distributed-fs/eos/mgm/http/xrdhttp/EosMgmHttpHandler.cc

## Purpose

`EosMgmHttpHandler.cc` implements the EOS MGM XRootD HTTP extension handler. It is the runtime bridge between XRootD HTTP requests and EOS MGM services: it loads the EOS MGM OFS plugin, optionally wires token authorization plugins, recognizes macaroon and REST gateway requests, normalizes request headers, forwards request bodies into EOS HTTP protocol handlers, and sends responses back through `XrdHttpExtReq::SendSimpleResp`.

The file also provides the `extern "C"` plugin entry point `XrdHttpGetExtHandler`, so it is part of the dynamically loaded XRootD plugin ABI rather than only an internal EOS class implementation.

## Important APIs, Types, and Functions

- `XrdHttpGetExtHandler(...)` is the exported factory. It allocates `EosMgmHttpHandler`, calls `Init()` and `Config()`, and returns the handler pointer or `nullptr` on initialization failure.
- `EosMgmHttpHandler::Config()` parses the XRootD/MGM configuration file, detects `eos::mgm::http::redirect-to-https=1`, finds `xrootd.fslib`, parses `mgmofs.macaroonslib`, loads the MGM OFS plugin, and chains token authorization plugins.
- `MatchesPath()` accepts most HTTP paths and rejects only `COPY` and `OPTIONS`, leaving those to the XrdHttpTPC plugin.
- `generateResponseHeaders()` adds `Date` and `X-Eos-Mgm-Version`, copies response headers except `Content-Length`, and rewrites `Location` to `https:` when redirect-to-HTTPS is enabled and request proxy headers allow it.
- `ProcessReq()` is the main dispatcher for shutdown handling, macaroon requests, REST gateway requests, REST-manager body reads, PROPFIND bodies, EOS HTTP handler invocation, and final response transmission.
- `ProcessMacaroonPOST()` remaps VOMS-authenticated identities through EOS VID mapping before delegating the request to the XrdMacaroons handler.
- `ProcessRestApiPost()` forwards REST API gateway POSTs to the local grpc-gateway URL using libcurl.
- `RestApiGwFrwAuthHeaders()` converts XRootD security and authorization data into `Grpc-Metadata-*` headers.
- `GetOfsLibPath()`, `GetAuthzLibPaths()`, and `GetHttpExtLibPath()` parse configured library tokens.
- `GetOfsPlugin()`, `GetHttpExtPlugin()`, and `GetAuthzPlugin()` resolve shared libraries with `XrdOucPinPath`, load symbols with `XrdSysPlugin`, and persist the loaded plugins.
- `readBody()` drains `XrdHttpExtReq` body buffers in 1 MiB aggregate reads backed by 256 KiB XRootD buffer chunks.
- `IsMacaroonRequest()` detects `POST` requests with `Content-Type: application/macaroon-request`.
- `IsRestApiRequest()` detects `POST` resources containing `/v1/eos/rest/gateway/`.

## Control Flow

Startup enters through `XrdHttpGetExtHandler`. The handler object is created, `Init()` is effectively a no-op, and `Config()` performs the meaningful work. Config parsing is line-oriented. When an `xrootd.fslib` line is seen, the file loads `XrdSfsGetFileSystem` from the configured library and stores the resulting `XrdMgmOfs*`. When a `mgmofs.macaroonslib` line is seen, it records the macaroon HTTP extension library and one or two authorization libraries. Missing macaroon configuration is not fatal; missing MGM OFS/authz after token configuration is fatal.

During request handling, `ProcessReq()` first rejects requests if the MGM OFS shutdown flag is set. It then lowercases all incoming header names into a normalized map. Macaroon token requests are routed through MGM redirection first via `ShouldRoute()`, because a slave MGM should redirect to the HTTP port of the current master. If no redirect is needed and the macaroon plugin is available, control is delegated to `ProcessMacaroonPOST()`.

If the MGM REST grpc server is available and the resource path matches the REST gateway prefix, `ProcessRestApiPost()` reads the body, extracts the final path segment as the EOS command name, builds `mRestApiGwUrl + mRestApiGwPath + command`, forwards auth metadata with curl, and returns either a 200 response containing grpc-gateway data or a 500 error.

All remaining requests go through EOS's internal HTTP stack. REST-manager requests have their body read with `readBody()`. Non-REST `PROPFIND` bodies are read directly from XRootD buffers. The code then calls `mMgmOfsHandler->mHttpd->XrdHttpHandler(...)` with verb, resource, normalized headers, empty cookies, request body, client security entity, optional token authz handler, and an error string. The returned `ProtocolHandler` supplies an `HttpResponse`, which is serialized into XRootD's simple response API. `HEAD` is special-cased to return no body while preserving the parsed content length.

## State and Persistence Behavior

This file keeps only process-local handler state. It stores pointers to dynamically loaded plugins (`mTokenHttpHandler`, `mTokenAuthzHandler`, `mMgmOfsHandler`) and configuration values (`mRedirectToHttps`, REST gateway URL/path). It mutates MGM global state once by calling `mMgmOfsHandler->SetTokenAuthzHandler(mTokenAuthzHandler)` after successful authz chaining. It does not persist data to disk or namespace storage.

Plugin objects are persisted in memory by `XrdSysPlugin::Persist()`. The destructor logs its invocation but does not unload plugin state or free the plugin pointers explicitly, which matches the usual XRootD plugin lifetime assumption but means ownership is intentionally non-obvious.

## Dependencies and Integration Points

The implementation is tightly integrated with XRootD HTTP extension APIs (`XrdHttpExtHandler`, `XrdHttpExtReq`), XRootD plugin loading (`XrdSysPlugin`, `XrdOucPinPath`), XRootD security (`XrdSecEntity`), XRootD authorization (`XrdAccAuthorize`), EOS MGM OFS (`XrdMgmOfs`), EOS HTTP infrastructure (`HttpServer`, `ProtocolHandler`, `HttpResponse`), EOS VID mapping (`eos::common::Mapping`), and libcurl for grpc-gateway forwarding.

Config semantics depend on `xrootd.fslib` and `mgmofs.macaroonslib` directive shape. Runtime routing depends on MGM master/slave routing via `XrdMgmOfs::ShouldRoute`. REST handling depends on `mRestGrpcSrv`, `mRestApiManager`, and a grpc-gateway listening at the configured local URL.

## Risks and Edge Cases

- `GetHttpExtPlugin()` unconditionally uses `myEnv->PutPtr(...)`; if XRootD ever invokes config with a null environment, this path can dereference null despite comments allowing null.
- `RestApiGwFrwAuthHeaders()` allocates a `curl_slist` and attaches it to the curl handle, but `ProcessRestApiPost()` only calls `curl_easy_cleanup()` and does not call `curl_slist_free_all()`, so repeated REST gateway calls may leak header-list allocations.
- `ProcessRestApiPost()` returns early on `RestApiGwFrwAuthHeaders()` failure without cleaning the initialized curl handle.
- `IsMacaroonRequest()` looks up exactly `Content-Type` in the original header map, while `ProcessReq()` already builds lower-case headers. A lower-case `content-type` header may not be recognized as a macaroon request.
- REST gateway response handling always sends HTTP 200 on successful curl transport and does not propagate grpc-gateway HTTP status codes.
- Redirect rewriting inserts `s` at offset 4 for any `Location` header if redirect conditions match. It assumes the value starts with `http`, so malformed or already-HTTPS values could be rewritten incorrectly.
- Body reading loops until `contentLeft` is zero. If `BuffgetData()` returns 0 before consuming the announced length, `contentLeft` is not reduced and the outer loop can spin indefinitely.
- Plugin loading depends on exact symbols (`XrdSfsGetFileSystem`, `XrdHttpGetExtHandler`, `XrdAccAuthorizeObjAdd`) and ABI compatibility with the compiled XRootD version.

## Test Signals

Useful tests include config-line parsing for `xrootd.fslib` variants and `mgmofs.macaroonslib`, plugin-load failure paths, macaroon request detection with varied header casing, HTTPS redirect header rewriting, `HEAD` content-length behavior, REST gateway forwarding with mocked curl/status handling, shutdown rejection, and body-read error/short-read behavior. Integration tests should exercise MGM master/slave redirection for macaroon requests and verify that token authz chaining falls back to MGM authz in the configured order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/http/xrdhttp/EosMgmHttpHandler.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/http/xrdhttp/EosMgmHttpHandler.hh -->
# sources/distributed-fs/eos/mgm/http/xrdhttp/EosMgmHttpHandler.hh

## Purpose

`EosMgmHttpHandler.hh` declares the EOS MGM implementation of `XrdHttpExtHandler`. It defines the class surface used by XRootD to initialize, match, and process HTTP requests, plus private helpers for EOS-specific plugin discovery, macaroon authorization, request body reading, REST gateway forwarding, and response header generation.

## Important APIs, Types, and Functions

- `class EosMgmHttpHandler : public XrdHttpExtHandler, public eos::common::LogId` is the plugin handler type.
- `using HdrsMapT = std::map<std::string, std::string>` names normalized request header maps used by REST forwarding.
- Constructor initializes HTTPS redirect to false and plugin pointers to null. `mRestApiGwUrl` defaults to `http://localhost:40054`; `mRestApiGwPath` defaults to `/v1/eos/rest/gateway/`.
- `Init(const char*) override` is intentionally a no-op because config-time arguments are handled in `Config()`.
- `Config(XrdSysError*, const char*, const char*, XrdOucEnv*)` is the real initialization hook.
- `MatchesPath(const char*, const char*) override` and `ProcessReq(XrdHttpExtReq&) override` form the XRootD request dispatch surface.
- `CopyXrdSecEntity()` is declared as a helper for security entity copying, but this source pair does not define or call it in the inspected implementation.
- Private library parsing/loading helpers declare the dynamic plugin integration contract for OFS, HTTP extension, and authorization plugins.
- `readBody()`, `IsMacaroonRequest()`, `ProcessMacaroonPOST()`, `IsRestApiRequest()`, `ProcessRestApiPost()`, `RestApiGwFrwAuthHeaders()`, `WriteCallback()`, and `generateResponseHeaders()` declare the request-processing helper set.

## Control Flow

The header encodes a lifecycle where XRootD constructs the handler through the exported C factory, calls `Init()` and `Config()`, asks `MatchesPath()` whether the plugin should receive a request, and then calls `ProcessReq()`. Internally, `ProcessReq()` can branch to macaroon plugin delegation, local REST grpc-gateway forwarding, or EOS MGM HTTP protocol handling.

The `IN_TEST_HARNESS` conditional moves private members into public visibility, suggesting unit tests can directly exercise configuration parsing and request classification helpers.

## State and Persistence Behavior

The class owns only runtime pointers and configuration flags. It has no persistent storage fields. Important mutable state includes:

- `mRedirectToHttps`, which affects response header rewriting.
- `mTokenHttpHandler`, the delegated XrdMacaroons HTTP handler.
- `mTokenAuthzHandler`, the chained token authorization object installed into MGM OFS.
- `mMgmOfsHandler`, the loaded MGM OFS plugin pointer used for routing and EOS HTTP handling.
- REST gateway URL/path string literals.

Because pointer ownership is not expressed with smart pointers, ownership and lifetime are delegated to XRootD plugin conventions and `XrdSysPlugin::Persist()` behavior in the implementation.

## Dependencies and Integration Points

The header depends on XRootD HTTP extension headers, XRootD versioning, XRootD authorization/security forward declarations, EOS common logging, EOS `HttpResponse`, and libcurl. It is intentionally coupled to the MGM OFS plugin through a forward declaration because implementation needs an `XrdMgmOfs*`.

The ABI-sensitive entry point itself is implemented in the `.cc` file, but this header defines the class that XRootD will call through virtual methods.

## Risks and Edge Cases

- `CopyXrdSecEntity()` appears declared but not implemented in the inspected file, which may indicate dead API, a missing definition in another build unit, or a latent link issue if used in tests.
- Raw pointers hide ownership. Destruction does not communicate whether delegated plugin handlers or authorization handlers are owned by this class.
- REST gateway URL/path are hard-coded default `const char*` members with no visible setter in the header.
- Several helper methods accept nullable XRootD pointers by comment, but the type signatures do not enforce null handling.
- The public API receives C strings from XRootD, so null or malformed `verb` and `path` handling depends on implementation assumptions.

## Test Signals

Header-level tests should compile the handler under `IN_TEST_HARNESS` and directly exercise helper methods. ABI tests should confirm `EosMgmHttpHandler` still satisfies `XrdHttpExtHandler` overrides after XRootD upgrades. Static checks should flag declared-but-unused/private helpers and raw pointer lifetime assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/http/xrdhttp/EosMgmHttpHandler.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/imaster/IMaster.cc -->
# sources/distributed-fs/eos/mgm/imaster/IMaster.cc

## Purpose

`IMaster.cc` implements shared helper behavior for the abstract MGM master-state interface declared in `IMaster.hh`. It supplies log buffering, lock/status file management, and namespace cache sizing defaults used by concrete master implementations.

## Important APIs, Types, and Functions

- `IMaster::MasterLog(const char* log)` appends non-empty log messages to `mLog` under `mMutex`.
- `IMaster::CreateStatusFile(const char* path)` creates a status/lock file with mode `S_IRWXU | S_IRGRP | S_IROTH` if it does not exist.
- `IMaster::RemoveStatusFile(const char* path)` unlinks an existing status/lock file.
- `IMaster::FillNsCacheConfig(IConfigEngine*, std::map<std::string, std::string>&)` reads namespace cache size settings and writes QuarkDB namespace constants.

## Control Flow

Status-file helpers first `stat()` the target path. Creation only calls `creat()` when the file is missing; removal only calls `unlink()` when the file exists. Errors are logged through `MasterLog()` using EOS static log formatting and return `false`.

`FillNsCacheConfig()` starts with defaults of 40,000,000 files and 5,000,000 directories. It asks `IConfigEngine` for `ns.cache-size-nfiles` and `ns.cache-size-ndirs`, parses them as unsigned integers, logs critical parse failures, and writes stringified values into the passed map under `constants::sMaxNumCacheFiles` and `constants::sMaxNumCacheDirs`.

## State and Persistence Behavior

`mLog` is the only object-local state changed by this file. Status-file creation/removal affects filesystem state, commonly under `/var/eos` paths defined in the header. Namespace cache config is not persisted directly here; it mutates the caller-provided map that later configures namespace services.

## Dependencies and Integration Points

The file depends on `mgm/config/IConfigEngine.hh` for config reads, `namespace/ns_quarkdb/Constants.hh` for namespace cache keys, POSIX filesystem calls (`stat`, `creat`, `unlink`, `close`), and EOS parse/logging helpers.

Concrete master implementations call these helpers while managing MGM master/slave transitions. The lock-file semantics are paired with XrdMqOfs behavior by convention rather than direct linkage.

## Risks and Edge Cases

- `CreateStatusFile()` treats any `stat()` failure as "file missing"; permission errors or transient filesystem errors will lead to a `creat()` attempt rather than a distinct diagnostic.
- `RemoveStatusFile()` ignores `stat()` errors, so permission or path errors can be silently treated as already removed.
- `CreateStatusFile()` uses `creat()` without `O_CLOEXEC`.
- `FillNsCacheConfig()` dereferences `configEngine` without a null check.
- On parse failures, defaults remain in effect but only a critical log indicates the bad config.

## Test Signals

Tests should cover successful create/remove, permission-denied failure paths, idempotent behavior when files already exist or are already absent, log appending under repeated calls, default namespace cache values, valid config override parsing, and invalid numeric strings preserving defaults.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/imaster/IMaster.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/imaster/IMaster.hh -->
# sources/distributed-fs/eos/mgm/imaster/IMaster.hh

## Purpose

`IMaster.hh` defines the abstract interface for EOS MGM master/slave state management. It standardizes initialization, namespace booting, config application, master identity updates, transition status reporting, master logs, and shared filesystem status-file helpers.

## Important APIs, Types, and Functions

- `EOSMGMMASTER_SUBSYS_RW_LOCKFILE` points to `/var/eos/eos.mgm.rw`, whose existence means the node should be treated as MGM master/read-write.
- `EOSMQMASTER_SUBSYS_REMOTE_LOCKFILE` points to `/var/eos/eos.mq.remote.up`, whose existence tells local MQ to redirect to remote MQ.
- `struct Transition::Type` enumerates master transition categories: master-to-master, slave-to-master, master-to-master-read-only, master-read-only-to-slave, and secondary-slave failover.
- Pure virtual methods define the implementation contract: `Init()`, `BootNamespace()`, `ApplyMasterConfig()`, `IsMaster()`, `IsRemoteMasterOk()`, `GetMasterId()`, `SetMasterId()`, `GetServiceDelay()`, `GetLog()`, and `PrintOut()`.
- Shared implemented helpers are `ResetLog()`, `MasterLog()`, `FillNsCacheConfig()`, `CreateStatusFile()`, and `RemoveStatusFile()`.

## Control Flow

Concrete master implementations are expected to initialize current state with `Init()`, boot namespace services through `BootNamespace()`, apply stall/redirection and master settings through `ApplyMasterConfig()`, and report runtime identity/state through the query methods. Transition code uses `GetServiceDelay()` after failover-like changes to avoid immediately reissuing transfers before maps converge.

The header-provided `ResetLog()` takes `mMutex` and clears `mLog`. Other shared helper implementations are in `IMaster.cc`.

## State and Persistence Behavior

`IMaster` stores an in-memory log string and mutex. The interface also defines lock-file paths that represent persistent local host state for master/read-write and remote MQ redirection. Derived classes are responsible for the actual master identity, namespace boot state, redirection/stall rules, and service delay calculations.

## Dependencies and Integration Points

The interface lives in `EOSMGMNAMESPACE` and inherits `eos::common::LogId`. It uses `IConfigEngine` for namespace cache settings and POSIX file mode definitions for status-file helpers. Comments explicitly note that lock-file defines must agree with `XrdMqOfs.cc` without creating a direct code dependency, making this header part of a cross-module operational contract.

## Risks and Edge Cases

- The lock-file contract is duplicated with `XrdMqOfs.cc` by convention. Divergence would break master/MQ coordination without compiler help.
- `GetMasterId()` returns `const std::string` by value; the `const` qualifier on a returned value is unnecessary and can inhibit move semantics in older compilers.
- `ResetLog()` and `MasterLog()` protect `mLog`, but concrete `GetLog()` implementations must also lock consistently.
- The interface does not define thread-safety expectations for master identity transitions.

## Test Signals

Concrete implementations should be tested through this interface for transition behavior, master ID validation, service delay after transition, lock-file side effects, and log thread safety. ABI/compile tests should detect changes to the transition enum and pure virtual method set because consumers depend on the interface shape.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/imaster/IMaster.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/inflighttracker/InFlightTracker.cc -->
# sources/distributed-fs/eos/mgm/inflighttracker/InFlightTracker.cc

## Purpose

`InFlightTracker.cc` implements reporting and throttling calculations for the in-flight request tracker. The corresponding header handles most request accounting inline; this file formats per-user request state and computes stall delays when per-user or global thread limits are exceeded.

## Important APIs, Types, and Functions

- `InFlightTracker::PrintOut(bool monitoring)` emits a table of active users, thread counts, active sessions, limits, stall counts, stall time estimates, and overload status.
- `InFlightTracker::getStallTime(uid_t uid, size_t& limit)` estimates a bounded randomized stall delay based on active sessions and the relevant limit.
- `InFlightTracker::ShouldStall(uid_t uid, bool& saturated, size_t& threads_used)` checks per-user and global thread limits and returns a stall duration in seconds, or zero if the request should proceed.

## Control Flow

`PrintOut()` selects human-readable or monitoring-oriented table formats, snapshots current per-uid in-flight counts with `getInFlightUids()`, queries `Access::ThreadLimit()` and `Mapping::ActiveSessions()`, and classifies each uid as `pool-OL`, `user-OL`, `user-LIMIT`, or `user-OK`.

`ShouldStall()` first gets user and global limits with the non-enforcing/lookup form of `Access::ThreadLimit(..., false)`. If the per-user limit is greater than one and the uid's in-flight count exceeds it, the method increments stall accounting, marks `saturated` if the global pool is also over limit, and returns `getStallTime(uid, limit)`. If the user is not over limit but the global pool is over limit, it increments stalls for the uid and returns a stall time based on global active sessions. Otherwise it returns zero.

`getStallTime()` derives a base from `2.0 * sessions / limit`, clamps it to the range 1..60, picks a random value in that range, and returns half the base plus the random component.

## State and Persistence Behavior

The file updates in-memory stall counters through `incStalls(uid)` and reads in-memory request counts. There is no persistent state. Stall behavior depends on live process state in `eos::common::Mapping::ActiveSessions()` and `Access::ThreadLimit()`.

## Dependencies and Integration Points

The implementation integrates with MGM access policy (`mgm/access/Access.hh`), EOS identity/session mapping (`eos::common::Mapping`), random utility helpers (`common::getRandom`), and table formatting (`TableFormatterBase`, `TableData`, `TableCell`). It is used anywhere request admission needs to display or enforce in-flight request pressure.

## Risks and Edge Cases

- `threads_used` is set to `limit` rather than the actual current count, which may surprise callers expecting observed usage.
- Limit comparison uses `>` for stalling but `PrintOut()` labels `user-OL` at `>= limit`; behavior and status text differ at exactly the limit.
- `getStallTime()` returns at least one second even when the computed load is tiny and the caller has already decided stalling is required.
- Randomized stall time makes exact behavior harder to test unless the random helper is controllable.
- `PrintOut()` snapshots maps, but status values can change immediately after formatting because request accounting is concurrent.

## Test Signals

Tests should cover no-stall, user-limit stall, global-limit stall, combined saturation, stall counter increments, output status at below/near/at/above limits, and deterministic stall-time behavior with a mocked random source or bounded assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/inflighttracker/InFlightTracker.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/inflighttracker/InFlightTracker.hh -->
# sources/distributed-fs/eos/mgm/inflighttracker/InFlightTracker.hh

## Purpose

`InFlightTracker.hh` defines request admission and accounting primitives for MGM code that needs to know how many requests are currently inside a critical path. It also provides a shutdown barrier: after accepting is disabled, new registrations are refused and callers can spin until all accepted requests have exited.

## Important APIs, Types, and Functions

- `class InFlightTracker` holds the accepting flag, atomic in-flight count, per-thread recursion/request counts, per-thread uid mappings, per-uid counts, and per-uid stall counts.
- `Up(const VirtualIdentity&)` attempts to register the current thread/uid as in-flight and returns false when request acceptance is disabled.
- `Down()` unregisters the current thread and decrements per-thread/per-uid state.
- `SetAcceptingRequests()`, `IsAcceptingRequests()`, `SpinUntilNoRequestsInFlight()`, and `GetInFlight()` form the shutdown barrier surface.
- `getInFlightThreads()`, `getInFlightUids()`, `getInFlight(uid)`, `incStalls(uid)`, and `getStalls(uid)` expose accounting snapshots.
- `getStallTime()`, `PrintOut()`, and `ShouldStall()` are declared here and implemented in the `.cc` file.
- `class InFlightRegistration` is an RAII helper that calls `Up()` in its constructor and `Down()` in its destructor when registration succeeded.

## Control Flow

`Up()` has a carefully documented sequence around `mAcceptingRequests` and `mInFlight`. It first rejects if accepting is already false, increments `mInFlight`, checks accepting again, and rolls back if shutdown won the race. Only after this double-check does it record the current `pthread_t` and uid under `mInFlightPidMutex`. This ensures that once accepting is disabled and `mInFlight` reaches zero, no future request can be admitted without incrementing the counter first.

`Down()` decrements `mInFlight`, asserts non-negative state, locks the maps, decrements the current thread's nested count, and removes thread and uid accounting when the last nested registration exits. It also clears stall counters for a uid when no in-flight request remains for that uid.

`SpinUntilNoRequestsInFlight()` asserts accepting is disabled, repeatedly reads `GetInFlight()`, optionally logs waiting progress, optionally sleeps, and exits only when the count reaches zero.

`InFlightRegistration` packages this protocol for scope-based use. Consumers can check `IsOK()` to reject work that was not admitted.

## State and Persistence Behavior

All state is process-local and in memory. `mAcceptingRequests` and `mInFlight` are atomic. Detailed per-thread and per-uid maps are protected by `mInFlightPidMutex`. No state survives process restart.

The tracker allows nested registrations on the same thread: `mInFlightPids[pthread_self()]` increments on each successful registration, but `mInFlightVids[uid]` increments only when the thread first appears. `mInFlight` increments for every successful `Up()`, so global request count and per-uid/thread maps measure slightly different concepts under nested use.

## Dependencies and Integration Points

The header depends on EOS namespace macros, logging, `VirtualIdentity`, table formatter declarations, atomics, pthread thread IDs, standard maps/sets, and mutexes. It integrates with request-processing code by wrapping request scopes in `InFlightRegistration` and with admission control by using `ShouldStall()`.

## Risks and Edge Cases

- `Down()` uses `mInFlightUid[mythread]` and `mInFlightPids[mythread]`, which default-insert entries if `Down()` is called without a matching successful `Up()` on the same thread. The RAII helper prevents this when used correctly, but direct calls are risky.
- The assertion `mInFlight >= 0` on an atomic relies on signed atomic conversion and is debug-only protection.
- Per-uid counts are incremented only for the first registration per thread, while `mInFlight` increments for nested registrations. That distinction must be understood by callers interpreting user counts.
- `SpinUntilNoRequestsInFlight()` has no timeout or cancellation parameter.
- `pthread_t` as a `std::map` key assumes comparable thread ID semantics for the platform.

## Test Signals

Tests should cover acceptance on/off race behavior, RAII success/failure, nested registration on one thread, multi-thread registration, `SpinUntilNoRequestsInFlight()` after disabling acceptance, direct misuse of `Down()` if supported, per-uid map cleanup, and stall-counter cleanup when uid activity drains.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/inflighttracker/InFlightTracker.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/inspector/FileInspector.cc -->
# sources/distributed-fs/eos/mgm/inspector/FileInspector.cc

## Purpose

`FileInspector.cc` implements a background MGM service that periodically scans QuarkDB file metadata for a storage space, computes file-health, age, size, cost, usage, and link statistics, persists the last scan into QuarkDB, and renders current/last scan data for admin and monitoring commands.

## Important APIs, Types, and Functions

- `FileInspector::FileInspector(std::string_view, const QdbContactDetails&)` initializes root identity, starts an assisted background thread, sets default disk/tape prices, and prepares the QuarkDB stats helper.
- `~FileInspector()` joins the assisted thread.
- `getOptions(LockFsView)` reads `inspector`, `inspector.interval`, `inspector.price.disk.tbyear`, `inspector.price.tape.tbyear`, and `inspector.price.currency` from `FsView::gFsView` for the configured space.
- `backgroundThread(ThreadAssistant&)` waits for namespace boot, loads previous stats from QuarkDB, periodically checks options, and runs scans only when enabled and the local MGM is master.
- `performCycleQDB(ThreadAssistant&)` scans all QuarkDB file metadata with `FileScanner`, throttles scan speed to fit the configured interval, handles disable/mastership changes, stores completed stats, and resets current stats.
- `Process(std::shared_ptr<IFileMD>)` updates `mCurrentStats` for one file: symlink/hardlink counters, totals, zero-size/nolocation/shadow-location/repetition-delta classifications, access-time bins, birth-time bins, birth-vs-access bins, size bins, birth-vs-size bins, disk/tape cost, and disk/tape byte attribution by uid/gid.
- `Dump(std::string&, std::string_view, LockFsView)` renders state for human output, export/list modes, and monitoring `key=...` lines.
- `QdbHelper::Store()` and `QdbHelper::Load()` marshal/unmarshal selected `FileInspectorStats` fields into a QuarkDB hash named `eos-file-inspector-stats`.

## Control Flow

The constructor starts `backgroundThread`. That thread waits for namespace boot via `gOFS->WaitUntilNamespaceIsBooted()`, reads the initial space options under the fs-view lock, sleeps briefly, loads last stats from QuarkDB if present, then loops until termination. Each loop refreshes options, enables or disables the inspector atomic, starts an interval stopwatch, runs `performCycleQDB()` only if enabled and `gOFS->mMaster->IsMaster()` is true, then sleeps for the remainder of the configured interval.

`performCycleQDB()` lazily creates a `qclient::QClient`, reads namespace file/container counts under `gOFS->eosViewRWMutex`, creates a `FileScanner`, and iterates through QuarkDB file metadata. Each protobuf item is wrapped in a `QuarkFileMD` and sent to `Process()`. The method updates `scanned_percent` and may sleep up to five seconds at a time to pace the scan across the configured interval. Once per minute it refreshes options and mastership; either disablement or loss of mastership interrupts the scan. Scanner errors are logged and break the loop. At the end it sets progress to 100%, moves `mCurrentStats` to `mLastStats`, persists `mLastStats`, and resets `mCurrentStats`.

`Process()` holds `mutexScanStats` for the entire per-file update. Symlinks and hardlinks are counted and returned early. Normal files update layout-keyed scan stats and global totals. It records faults for missing locations, shadow filesystem locations, shadow deletion locations, and replication deltas up to `maxfaulty` examples while still incrementing total fault count. Time histograms use a fixed bin set ranging from 0 through one day, seven days, month-scale/year-scale values, and an undefined bin. Cost and byte accounting are split into disk index 0 and tape index 1.

`Dump()` first emits human summary and a size histogram unless monitoring mode is requested. It then rejects disabled state. With lock held, monitoring mode emits line-oriented `key=last` metrics. Non-monitoring mode reports progress and optionally current scan data (`c`), last scan data (`l`), printed faulty files (`p`), exported faulty file lists (`e`), and filtered sections for layouts/costs/usage/access/birth/birth-vs-access. `Z` expands top-N listings, and `M` switches cost display from TB-years to configured currency.

## State and Persistence Behavior

Live state includes `mEnabled`, `mCurrentStats`, `mLastStats`, pricing atomics, currency string, scan progress, namespace file/directory counters, `mQcl`, and `mSpaceName`. `mutexScanStats` protects current/last stats during processing and dumps. The background thread lifecycle is managed by `AssistedThread`.

Persistent state is a QuarkDB hash at key `eos-file-inspector-stats` through `QdbHelper`. Store/load cover scan stats, faulty files, access/birth/birth-vs-access distributions, user/group/total costs, user/group/total bytes, faulty count, scan time, and link counts. The code computes size distributions and birth-vs-size distributions, but `QdbHelper::Store()` and `Load()` do not persist `SizeBinsFiles`, `SizeBinsVolume`, `BirthVsSizeFiles`, `BirthVsSizeVolume`, `TotalFileCount`, or `TotalLogicalBytes` despite `Dump()` using them for last-scan summary and monitoring output.

## Dependencies and Integration Points

The implementation depends on global MGM state (`gOFS`), master-state interface (`gOFS->mMaster`), filesystem view (`FsView::gFsView`), namespace services, QuarkDB contact details and qclient, `FileScanner`, `QuarkFileMD`, EOS layout metadata helpers, EOS timing/string conversion helpers, EOS user/group mapping, and `ProcCommand`/MGM admin command integration through `Dump()` output.

The inspector is space-specific and reads its runtime configuration from the corresponding space view. It is master-only to avoid multiple MGMs scanning and writing overlapping stats.

## Risks and Edge Cases

- `mCurrentStats.TimeScan` is set before `performCycleQDB()` in the background thread, but a direct caller of `performCycleQDB()` could run with a zero scan time and skew age bins.
- If `nfiles` is zero, progress and pacing calculations divide by `nfiles`.
- `QdbHelper::Store()` does not persist fields that `Dump()` later presents as last-scan data, especially total file/byte summary and size/birth-vs-size histograms.
- `FileInspectorStats` defines `SIZE_*` keys, but this implementation does not store/load those keys.
- Currency parsing accepts indexes `< 6` but does not reject negative values before indexing the six-element array, so a negative parsed index can access out of bounds.
- Cost maps are `uint64_t` in `FileInspectorStats`, but `Process()` accumulates `double` costs into them, truncating fractional values.
- Faulty examples are capped by a global `NumFaultyFiles` count across all categories, so some categories may have no examples once the cap is reached.
- `Dump()` builds very large strings under the stats mutex, which can block scanning on large outputs.
- Export mode writes to `/var/log/eos/mgm/FileInspector.<time>.list`; failures are reported in output but not otherwise recoverable.
- `QdbHelper::Load()` catches all unmarshal errors and resets all stats, which is robust but can hide partial schema migration issues.

## Test Signals

Tests should cover option parsing with/without fs-view locking, master-only scan gating, scan interruption when disabled or demoted, zero-file namespaces, symlink/hardlink early returns, missing/shadow/repetition-delta fault classification, age and size bin boundaries, disk/tape cost and bytes attribution, QDB store/load round trips for every field used by `Dump()`, monitoring output shape, export/list modes, and negative/invalid currency or price config values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/inspector/FileInspector.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/inspector/FileInspector.hh -->
# sources/distributed-fs/eos/mgm/inspector/FileInspector.hh

## Purpose

`FileInspector.hh` declares the space-scoped file-inspection service used by MGM to scan QuarkDB file metadata and report storage health/cost/usage statistics. It defines the public control/reporting surface, the background thread state, and the nested QuarkDB persistence helper.

## Important APIs, Types, and Functions

- `struct Options` contains `enabled` and scan `interval`.
- `enum LockFsView` lets callers decide whether `getOptions()`/`Dump()` should lock the global fs-view mutex.
- `FileInspector(std::string_view, const QdbContactDetails&)` and `~FileInspector()` manage the inspector lifecycle.
- `performCycleQDB(ThreadAssistant&) noexcept` exposes one QDB scan cycle.
- `Dump(std::string&, std::string_view, LockFsView)` renders current/last stats.
- `getOptions(LockFsView)` reads space configuration and updates enabled/pricing state.
- `enabled()`, `disable()`, and `enable()` wrap atomic inspector state transitions.
- Private `backgroundThread()` and `Process()` implement periodic scanning and per-file accounting.
- Nested `QdbHelper` owns a qclient and `QHash`, and provides `Store()`, `Load()`, `Clear()`, and `HasStats()`.

## Control Flow

The header describes a service where construction starts the assisted background thread. The thread periodically calls `getOptions()`, uses mastership checks in the implementation, and invokes `performCycleQDB()` to populate stats. Admin/monitoring callers use `Dump()` to view either current scan progress or last completed scan output.

`enable()` and `disable()` are compare-exchange operations, so they return true only when they actually change the current enabled state. `enabled()` returns the current atomic value.

## State and Persistence Behavior

Important in-memory state includes:

- `AssistedThread mThread` for the background scanner.
- `std::atomic<bool> mEnabled`.
- `mVid` root identity and `mError` error object.
- `mQcl` for scanner access to QuarkDB.
- `mCurrentStats` and `mLastStats`.
- Atomic disk/tape prices, currency string, scanned percentage, file/dir counters.
- `mutexScanStats` guarding stats.
- `mSpaceName`.

Persistent behavior is encapsulated in `QdbHelper`, which stores stats under `kFileInspectorStatsKey = "eos-file-inspector-stats"` via a QuarkDB hash. `Clear()` deletes that key, and `HasStats()` tests for it.

## Dependencies and Integration Points

The header depends on `VirtualIdentity`, `AssistedThread`, `FileInspectorStats`, QuarkDB contact details, qclient, QHash, `IFileMD`, and XRootD error types. It is intended for MGM components that already have global namespace and fs-view context.

The `LockFsView` argument is an integration affordance: some callers already hold the fs-view lock and must avoid taking it again, while others need safe option reads.

## Risks and Edge Cases

- `currency` is a plain string, not atomic and not separately guarded in the header; implementation writes it while dumps may read it.
- `currencies` is a fixed public const array, while config parsing uses numeric indexes rather than symbolic names.
- `performCycleQDB()` is public, but its implementation relies on global MGM state and background-thread initialization conventions.
- `QdbHelper` uses a single fixed QuarkDB key. If multiple spaces instantiate inspectors against the same QDB, stats may collide unless higher-level deployment guarantees only one relevant space or key namespace.
- The header exposes `disable()`/`enable()` as state toggles, but actual options are also refreshed from fs-view config, so manual toggles may be overwritten.

## Test Signals

Tests should instantiate with fake QDB contact details or a mock qclient layer, verify atomic enable/disable return semantics, exercise `getOptions()` with lock on/off, confirm `QdbHelper::Clear()`/`HasStats()` behavior, and ensure multiple space names do not unintentionally share persistent state if the service is expected to be per-space.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/inspector/FileInspector.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/inspector/FileInspectorStats.cc -->
# sources/distributed-fs/eos/mgm/inspector/FileInspectorStats.cc

## Purpose

`FileInspectorStats.cc` implements copy and move assignment for `FileInspectorStats`, including helper templates for fixed-size array members. This lets the inspector move a completed current scan into last-scan storage and copy stats safely when needed.

## Important APIs, Types, and Functions

- `clone(T(&dst)[N], const T(&src)[N])` copy-assigns each element of a fixed-size array.
- `FileInspectorStats::operator=(const FileInspectorStats&)` copies map fields, fixed arrays, counters, totals, scan time, and link statistics.
- `move(T(&dst)[N], T(&src)[N]) noexcept` move-assigns each array element and resets the source element to a default value.
- `FileInspectorStats::operator=(FileInspectorStats&&) noexcept` moves map fields and arrays, then copies scalar counters/totals/time/link fields.

## Control Flow

Both assignment operators self-check first. Copy assignment directly assigns every map and scalar and uses `clone()` for two-element array fields. Move assignment moves map fields and uses `move()` for arrays. Source array elements are reset to default values after move.

These operators are used by `FileInspector` when loading stats, moving `mCurrentStats` into `mLastStats`, resetting current stats, and potentially returning/copying stats in admin paths.

## State and Persistence Behavior

The file does not persist anything directly. It determines which in-memory stats survive copy/move operations. That matters because `FileInspector` relies on move assignment to preserve a completed scan before persisting and dumping it.

## Dependencies and Integration Points

The implementation includes `FileInspectorStats.hh`, qclient headers, and JSON helpers. The qclient/JSON includes are not directly used by the visible assignment code, but the stats type is marshalled elsewhere by `FileInspector::QdbHelper`.

## Risks and Edge Cases

- `UserBytes` is copied twice in copy assignment and moved twice in move assignment; this is redundant and likely a typo.
- `SizeBinsFiles`, `SizeBinsVolume`, `BirthVsSizeFiles`, and `BirthVsSizeVolume` exist in the header but are not copied or moved here. That means these computed histograms are lost when `mCurrentStats` is moved into `mLastStats`.
- Move assignment copies scalar fields from `other` but does not reset them in the source. This is legal for moved-from objects but can surprise debugging code.
- Extra includes may hide unused dependency drift.

## Test Signals

Tests should create a fully populated `FileInspectorStats`, copy it, move it, and assert that every field declared in the header survives in the destination. This should specifically catch missing size and birth-vs-size map handling and the duplicate `UserBytes` operation. Tests should also assert moved-from array elements are defaulted if that behavior is relied on.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/inspector/FileInspectorStats.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/inspector/FileInspectorStats.hh -->
# sources/distributed-fs/eos/mgm/inspector/FileInspectorStats.hh

## Purpose

`FileInspectorStats.hh` defines the data model for file-inspector scan results and the string keys used when serializing those results. The struct aggregates health classifications, time distributions, size distributions, owner/group cost and byte accounting, total counters, and link statistics.

## Important APIs, Types, and Functions

- Serialization key macros include `SCAN_STATS_KEY`, `FAULTY_FILES_KEY`, access/birth/birth-vs-access keys, size-distribution keys, size-vs-birth keys, cost/byte keys, fault count, scan time, and link keys.
- `struct FileInspectorStats` declares copy/move constructors and assignment operators implemented in `FileInspectorStats.cc`.
- `ScanStats` is a layout-id to named-counter map for scan classifications such as zero-size, volume, physical size, missing location, shadow location, and replication deltas.
- `FaultyFiles` maps failure type to file id and layout id examples.
- Access, birth, birth-vs-access, size, and birth-vs-size maps capture histogram data.
- `UserCosts`, `GroupCosts`, `TotalCosts`, `UserBytes`, `GroupBytes`, and `TotalBytes` are two-element disk/tape accounting arrays.
- Scalar counters include `NumFaultyFiles`, `TotalFileCount`, `TotalLogicalBytes`, `HardlinkCount`, `HardlinkVolume`, `SymlinkCount`, and `TimeScan`.

## Control Flow

This header has no runtime control flow beyond constructors. The default constructor initializes `TimeScan` to zero and in-class initializers set totals/link counters to zero. `FileInspector::Process()` fills the maps and counters, `FileInspectorStats.cc` copies/moves them, and `FileInspector::QdbHelper` serializes a subset of the fields.

## State and Persistence Behavior

The struct is the state container for both current and last file-inspector scans. Key macros define the persistence schema used by QuarkDB hash storage. The schema includes keys for size distributions and birth-vs-size distributions, but the inspected `QdbHelper::Store()`/`Load()` implementation does not use those keys. This mismatch means the header advertises persistence fields that may not survive restart.

## Dependencies and Integration Points

The header depends on standard maps/sets/atomics, EOS namespace macros, and qclient. It is included by `FileInspector.hh` and implemented by `FileInspectorStats.cc`. Its field names and key macros are coupled to `common/json/Json.hh` `Marshal`/`Unmarshal` calls in `FileInspector.cc`.

## Risks and Edge Cases

- Costs are stored in `uint64_t` maps even though `FileInspector::Process()` computes disk/tape costs as doubles, causing truncation.
- Key macro `BIRTH_VS_ACCESS_TIME_VOLUME_KEY` has value `birth-vs-access-volume-files`, which is awkwardly named and should be kept compatible if already persisted.
- Size and birth-vs-size key macros can give a false sense of persistence coverage because current storage code omits them.
- Copy/move assignment must be kept in sync manually with this struct; missing fields cause silent loss of stats.
- `qclient/QClient.hh` appears unnecessary in this pure data header and increases compile coupling.

## Test Signals

Tests should verify default initialization, copy/move preservation of every field, JSON marshal/unmarshal compatibility for all map and array shapes, persistence key coverage against `QdbHelper::Store()`/`Load()`, and cost precision expectations for fractional cost accumulation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/inspector/FileInspectorStats.hh -->
