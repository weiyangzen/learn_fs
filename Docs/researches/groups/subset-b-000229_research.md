# Research Report: subset-b-000229

Grouped research for Nydus service daemon/cache/upgrade files and smoke-test Dragonfly/API/blobcache coverage. Each section preserves the source path and is delimited for deterministic reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/service/src/daemon.rs -->
## sources/cloud-native/nydus/service/src/daemon.rs

Purpose: defines the common daemon lifecycle contract for Nydus services and the state-machine/controller infrastructure used by FUSE and singleton fscache daemons. Important APIs are `DaemonState`, `DaemonInfo`, the `NydusDaemon` trait, `DaemonStateMachineContext`, `DaemonStateMachineSubscriber`, and `DaemonController`.

Control flow: callers emit `DaemonStateMachineInput` through a concrete daemon's `on_event`; the dedicated `state_machine` thread consumes events and runs actions such as `start`, `stop` plus `wait_service`, `umount`, `restore`, and `StopStateMachine`. `trigger_stop` and `trigger_exit` intentionally send multiple events for running daemons so they move through `Running -> Ready -> Die` or `Running -> Ready -> Die` via exit.

State and persistence: daemon state is abstracted as `INIT`, `RUNNING`, `READY`, `STOPPED`, or `UNKNOWN`; concrete daemons own storage and upgrade persistence through `save`/`restore`. `DaemonController` stores the active daemon, optional blob cache manager, optional default filesystem service, singleton mode, and a `mio::Waker`/`Poll` pair for shutdown.

Dependencies and integration: integrates `rust_fsm`, `mio`, `nydus_api::BuildTimeInfo`, service `FsService`, `BlobCacheMgr`, and `UpgradeManager`. `export_info` serializes daemon metadata and optionally the backend collection for API status.

Risks: the FSM thread panics if channels are broken, invalid events are returned as `UnexpectedEvent`, `get_daemon` panics before registration, and `trigger_stop` behavior relies on concrete daemon state remaining synchronized with FSM state. Controller shutdown behavior differs in singleton mode, which can affect long-running service hosting.

Test signals: unit tests cover integer/string state conversion, exported JSON without fs info, trigger event sequences, controller lifecycle, daemon replacement, singleton mode writes, and waker allocation.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/service/src/daemon.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/service/src/fs_cache.rs -->
## sources/cloud-native/nydus/service/src/fs_cache.rs

Purpose: implements the userspace side of Linux cachefiles/fscache on-demand mode for RAFS/EROFS. `FsCacheHandler` opens `/dev/cachefiles`, binds the cache directory/tag, receives kernel `OPEN`, `CLOSE`, and `READ` messages, maps fscache objects to blob/bootstrap sources, and feeds data back to the kernel cache.

Important APIs/types: `FsCacheOpCode`, `FsCacheMsgHeader`, `FsCacheMsgOpen`, `FsCacheMsgRead`, `FsCacheBootstrap`, `FsCacheBlobCache`, `FsCacheObject`, `FsCacheState`, and public `FsCacheHandler::{new, working_threads, stop, run_loop, get_file, cull_cache}`. Message parsers use unaligned little/native reads and length validation before dispatch.

Control flow: `new` configures cachefiles with `dir`, optional `tag`, and `bind ondemand`, or sends `restore` when handed an upgrade fd. `run_loop` polls the cachefiles fd and a waker. `handle_open_request` resolves `volume_key` and `cookie_key` to a blob-cache config; data blobs create a cache object and spawn lazy blob-cache initialization with retry and optional prefetch, while bootstrap opens/copies metadata into the kernel cache after `copen`. `READ` fetches uncompressed blob ranges or mmaps bootstrap data, then sends `fscache_cread`; `CLOSE` tears down blob state and triggers factory GC.

State and persistence: tracks object-id to cache object/fd and object-id to config maps under a mutex. Kernel cache files persist under `<work_dir>/cache`; blob-cache instances are transient but share factory config. Upgrade support keeps the cachefiles fd clone through `get_file`. `cull_cache` walks cachefiles volume directories and uses `inuse`/`cull` commands from the proper working directory.

Dependencies and integration: depends on `BlobCacheMgr`, `BLOB_FACTORY`, `ASYNC_RUNTIME`, `BlobPrefetchRequest`, Linux cachefiles ioctls, `mio`, libc fd reads/writes/mmap/pwrite, and generated blob keys. It is owned by `singleton.rs` and exposed through `FsCacheHandler` on Linux.

Risks: unsafe fd ownership is delicate (`from_raw_fd` plus `mem::forget`), cachefiles protocol parsing assumes host endianness/layout, `cull_cache` changes process cwd, blob-cache initialization is asynchronous so early reads may see "not ready", and prefetch/error handling often logs instead of failing the open. Cache hash/path logic must match kernel cachefiles layout exactly.

Test signals: tests validate opcode/header/open/read parsing failures, UTF-8 handling, helper hash/rotate/rounding behavior, cookie path determinism, max-value reads, and local handler construction. Real cachefiles behavior still requires root, a new enough kernel, and `/dev/cachefiles` integration tests through the singleton service.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/service/src/fs_cache.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/service/src/fs_service.rs -->
## sources/cloud-native/nydus/service/src/fs_service.rs

Purpose: provides the common filesystem-service trait and backend factory used by FUSE daemons to mount RAFS, passthroughfs, and optional overlayfs layers into a `fuse_backend_rs::api::Vfs`.

Important APIs/types: `FsBackendMountCmd`, `FsBackendUmountCmd`, `FsBackendCollection`, `FsService`, `mountpoint_invalidation_target`, `validate_prefetch_file_list`, and `fs_backend_factory`. `FsBackendCollection::add` records sanitized RAFS config, mountpoint, backend type, and mounted time for API status/metrics.

Control flow: `mount` rejects duplicate mountpoints, creates a backend, mounts it into VFS, records backend metadata, and updates upgrade state/VFS bytes. `remount` finds an existing RAFS backend, opens the new bootstrap, parses config, calls `Rafs::update`, and refreshes metrics/upgrade mount state. `restore_mount` recreates a backend at a saved VFS index. `umount` optionally sends FUSE invalidation for RAFS trees, unmounts from VFS, deletes collection state, saves upgrade VFS state, and runs blob factory GC.

State and persistence: mount state lives in VFS, `FsBackendCollection`, and `UpgradeManager` mount/VFS snapshots. RAFS bootstrap/config sources are not persisted here beyond `FsBackendMountCmd`; upgrade replay reuses those commands.

Dependencies and integration: uses `fuse-backend-rs` VFS, RAFS import/update APIs, `nydus_api::ConfigV2`, `BLOB_FACTORY`, Linux `PassthroughFs` and `OverlayFs`, and versionize for mount-command compatibility. `FusedevFsService` implements this trait and API handlers call its default methods.

Risks: mount/remount/umount are documented as not thread-safe and rely on single-threaded FSM/API usage; invalidation target resolution must handle root and nested pseudo-fs paths; overlayfs requires valid upper/work dirs and is Linux-only; prefetch paths must be absolute; remount assumes existing backend is RAFS.

Test signals: unit tests cover backend collection add/delete, prefetch path validation, root/nested/missing invalidation target resolution, passthrough descriptor behavior, and RAFS backend creation from a fixture bootstrap.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/service/src/fs_service.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/service/src/fusedev.rs -->
## sources/cloud-native/nydus/service/src/fusedev.rs

Purpose: implements the FUSE-backed Nydus daemon. It creates a `FuseSession`, runs threaded `/dev/fuse` request loops, exposes a `FusedevFsService` implementing `FsService`, supports live upgrade/failover, and creates the configured VFS backend.

Important APIs/types: `FuseOp`/`FuseOpWrapper` track in-flight FUSE requests, `FuseServer` wraps a `Server<Arc<Vfs>>` plus channel, `FusedevNotifier` and `FuseSysfsNotifier` send resend/flush notifications, `FusedevFsService` owns the session/VFS/backend collection/upgrade manager, `FusedevDaemon` implements `NydusDaemon`, and public helpers are `create_fuse_daemon` and `create_vfs_backend`.

Control flow: `create_fuse_daemon` canonicalizes the mountpoint, starts the daemon FSM thread, optionally mounts an initial backend, mounts the FUSE session, emits `Mount` and `Start`, stores the calculated FUSE connection id, and hands the fuse fd to `UpgradeManager`. `start` launches `threads_cnt` `fuse_server` threads; each handles messages until session shutdown and wakes the controller on exit. `umount` shuts down and wakes the session; `stop` just wakes; `wait` joins state-machine and service threads.

State and persistence: daemon state is an atomic `i32`; service state includes FUSE connection id, failover policy, session fd, VFS, mounted backend collection, inflight operation wrappers, and optional upgrade manager. Upgrade save/restore is delegated to `upgrade::fusedev_upgrade`, including VFS bytes and held fuse fd.

Dependencies and integration: depends on `fuse-backend-rs` transport/server/VFS APIs, RAFS inode walking, `mio::Waker`, sysfs/procfs FUSE connection files, `nix` device major/minor helpers, `FsService` defaults, and daemon FSM. It integrates with API status through `export_inflight_ops` and backend collection.

Risks: FUSE shutdown paths are timing-sensitive; connection-id calculation depends on platform mount metadata; failover resend first tries `/dev/fuse` then sysfs, and flush/resend availability varies by kernel. Recursive invalidation logs child failures but continues. `is_crashed` depends on both residual mount and API socket state.

Test signals: unit tests cover sysfs base paths, notifier connection reference behavior, and Linux FUSE connection-id calculation on existing/nonexistent paths. Broader behavior is exercised by smoke API mount/remount tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/service/src/fusedev.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/service/src/lib.rs -->
## sources/cloud-native/nydus/service/src/lib.rs

Purpose: crate root for `nydus-service`, documenting service modes and exporting the public daemon, filesystem, blob-cache, block-device, and UFFD APIs behind platform/feature gates.

Important APIs/types: exports `BlobCacheMgr`, `FsBackendCollection`, `FsBackendMountCmd`, `FsBackendUmountCmd`, `FsService`, `create_fuse_daemon`, `create_vfs_backend`, `FusedevDaemon`, `create_daemon`, and Linux `FsCacheHandler`. Defines central `Error`, `Result`, `FuseNotifyError`, `FsBackendType`, `FsBackendDescriptor`, `validate_threads_configuration`, and `ServiceArgs`.

Control flow: there is no runtime loop here; it normalizes error conversion into `io::Error` and `nydus_api::DaemonErrorKind`, parses backend type strings, validates thread counts in `[1,1024]`, and exposes modules conditionally based on target OS and block features.

State and persistence: only serializable descriptors/types live here. `FsBackendDescriptor` records backend type, mountpoint, mounted time, and optional sanitized `ConfigV2`; versionize annotations allow mount commands and backend type values to participate in upgrade snapshots.

Dependencies and integration: centralizes integration with `fuse-backend-rs`, RAFS, serde, versionize, and `nydus_api`. Non-Linux builds get a stub `BlobCacheMgr` with unimplemented mutation methods, keeping API shape available while Linux-only cache implementation is excluded.

Risks: broad error-to-`io::Error` conversion maps everything to invalid input; adding backend types requires updating parsing/display/version compatibility and tests. Conditional modules mean some exported APIs exist only under Linux or feature gates, which callers must handle.

Test signals: tests cover backend type parsing aliases/errors/display, thread-count boundaries, error conversion to `DaemonErrorKind`, `FuseNotifyError` display, and representative `Error` display messages.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/service/src/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/service/src/singleton.rs -->
## sources/cloud-native/nydus/service/src/singleton.rs

Purpose: implements a singleton-style `ServiceController` daemon that hosts fscache/blob-cache services without creating a FUSE mount itself. It is the daemon path for fscache service mode and online upgrade of cachefiles state.

Important APIs/types: `ServiceController`, `initialize_fscache_service`, `create_daemon`, `start_services`, `stop_services`, `initialize_blob_cache`, `get_fscache_file`, and `delete_blob`. It implements both `NydusDaemon` and `DaemonStateMachineSubscriber`.

Control flow: `create_daemon` builds channels and optional `UpgradeManager`, initializes blob-cache config from a JSON `blobs` list, starts the common daemon FSM thread, checks for crash/failover unless upgrading, initializes fscache when requested, saves its fd/path/thread count into upgrade state, then emits `Mount` and `Start`. `start_services` spawns one fscache run-loop worker per configured thread; each wakes the global controller when exiting. `stop_services` calls `FsCacheHandler::stop`.

State and persistence: stores build/id/state/supervisor, blob cache manager, optional upgrade manager, fscache enabled flag, and optional `Arc<FsCacheHandler>`. Upgrade persistence includes fscache fd, path, thread count, and blob entries. `delete_blob` delegates to `FsCacheHandler::cull_cache` only when fscache is enabled and initialized.

Dependencies and integration: integrates daemon FSM, `BlobCacheMgr`, Linux `FsCacheHandler`, `UpgradeManager`, `mio::Waker`, `/dev/cachefiles`, and API socket crash detection. It is exported as `create_daemon` by `lib.rs`.

Risks: crash detection treats an unavailable `/dev/cachefiles` as either failover or "another daemon is running" depending on residual API socket connectivity. Spawned fscache worker handles are not joined in `wait`; stopping relies on the handler barrier. Blob-cache config parsing silently ignores JSON without `blobs` or invalid shape unless `add_blob_list` fails.

Test signals: Linux tests cover invalid fscache paths, optional root/kernel/device-gated fscache initialization, blob config loading, daemon properties/state, disabled and uninitialized `delete_blob`, missing fscache fd, no-op wait/umount, and optional managers.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/service/src/singleton.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/service/src/uffd_proto.rs -->
## sources/cloud-native/nydus/service/src/uffd_proto.rs

Purpose: defines the JSON protocol used by the block-uffd feature for userfaultfd-style page-fault coordination between a client and server.

Important APIs/types: `UFFD_PROTOCOL_VERSION`, repr-serialized `MessageType` (`Handshake`, `PageFault`, `Stat`, `StatResp`), `FaultPolicy` (`Zerocopy`, `Copy`), `VmaRegion`, `HandshakeRequest`, `PageFaultResponse`, `BlobRange`, `StatRequest`, and `StatResponse`.

Control flow: constructors/defaults provide protocol defaults: handshake message type, zerocopy policy, read-only `prot`, `MAP_PRIVATE | MAP_FIXED` flags, `StatRequest::new`, and `StatResponse::new`. Actual transport and fault handling are implemented elsewhere; this file is schema-only.

State and persistence: all structures are serde serializable/deserializable. `VmaRegion` carries mapping coordinates, page size, optional `page_size_kib`, and mmap protection/flags; `PageFaultResponse` carries blob ranges to satisfy faults; `StatResponse` returns size/block/flags/version metadata.

Dependencies and integration: uses `serde`, `serde_repr`, and libc constants. The module is exported only on Linux with the `block-uffd` feature, coupling it to the block UFFD service path.

Risks: numeric enum encoding is wire-visible and must remain compatible; defaults affect clients that omit fields; mmap flags include `MAP_FIXED`, so consumers must validate address ranges carefully. There is no validation of region alignment, overlap, or protocol version in this schema file.

Test signals: tests cover enum defaults and numeric JSON encoding/decoding, `VmaRegion` constructor/default fields, handshake default type, blob/page-fault serialization, stat response construction, and fault-policy serialization.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/service/src/uffd_proto.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/service/src/upgrade.rs -->
## sources/cloud-native/nydus/service/src/upgrade.rs

Purpose: manages online-upgrade state transfer for fscache and FUSE daemons. It serializes service state through a `nydus_upgrade` storage backend over Unix domain socket and preserves one critical fd for the next process.

Important APIs/types: `UpgradeMgrError`, `FailoverPolicy`, internal `FscacheState`, `MountStateWrapper`, `FusedevState`, `UpgradeManager`, `fscache_upgrade::{BlobCacheEntryState,FscacheBackendState,save,restore}`, and `fusedev_upgrade::{FusedevBackendState,save,restore}`.

Control flow: concrete services update `UpgradeManager` as blobs are added/removed, fscache path/thread count changes, VFS state is saved, mounts are added/updated/removed, and fuse connection id is known. `save` sends serialized bytes plus held fd to `UdsStorageBackend`; `restore` receives fds and state bytes. Fscache restore rebuilds blob entries and reinitializes `FsCacheHandler` with the restored cachefiles fd. FUSE restore restores connection id, fuse fd, drains pending requests, restores VFS bytes, and replays saved mounts by VFS index.

State and persistence: fscache state is a map of `domain/blob` to serialized `BlobCacheEntry`, thread count, and path. FUSE state is mountpoint to mount command/index, VFS snapshot bytes, and fuse connection id. The held `File` is cloned from the active cachefiles/fuse fd and returned as a clone during restore.

Dependencies and integration: integrates `nydus_upgrade::StorageBackend`, `UdsStorageBackend`, versionize snapshotters, `BlobCacheEntry`, `Vfs::save_to_bytes`/`restore_from_bytes`, `ServiceController`, `FusedevDaemon`, and `FsService::restore_mount`.

Risks: restore assumes exactly at least one fd and indexes `fds[0]`; missing supervisor path prevents restore; stale source/config paths in saved mount commands break replay; VFS and mount snapshot versions must remain compatible; FUSE drain failures are logged but restore continues.

Test signals: tests cover failover-policy parsing for `none`, `flush`, and `resend`; fscache state conversion/serialization and blob entry removal; FUSE mount state conversion/update/removal and fuse cid; and fd hold/return cloning.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/service/src/upgrade.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/smoke/.golangci.yml -->
## sources/cloud-native/nydus/smoke/.golangci.yml

Purpose: configures linting and formatting for the Go smoke test suite.

Important settings: golangci-lint config version 2, disables default linters, enables `staticcheck`, `unconvert`, `revive`, `ineffassign`, `govet`, `unused`, and `misspell`, enables `gofmt` and `goimports`, and sets a 4-minute run timeout. `revive` enables style/error-flow rules such as blank imports, context argument position, error naming/strings, receiver/time naming, var naming/declaration, range, superfluous else, and unreachable code.

Control flow/state: no runtime behavior; it is consumed by `make test` before running `smoke.test`.

Dependencies and integration: depends on a compatible `golangci-lint` binary that understands config version 2 and formatter settings. It integrates directly with `smoke/Makefile`.

Risks: version 2 schema can fail on older golangci-lint installations; strict revive rules may require naming/style updates when adding smoke helpers.

Test signals: lint success is a prerequisite signal in the Makefile smoke path; failures block execution of the root smoke binary.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/smoke/.golangci.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/smoke/Makefile -->
## sources/cloud-native/nydus/smoke/Makefile

Purpose: provides build and test entry points for the Go smoke suite, including ordinary smoke tests, performance, benchmark, compatibility, and takeover modes.

Important targets: `build` compiles `./tests` into `smoke.test` with `-race`; `test` builds, runs golangci-lint, then executes `sudo -E ./smoke.test` with configurable `TESTS`; `test-performance`, `test-benchmark`, `test-compatibility`, and `test-takeover` set environment gates and run selected tests.

Control flow/state: environment variables supply binary paths, work dirs, stable versions, image names, snapshotter sockets, and coverage flags. `PACKAGES`, `GOPROXY`, `GO_TEST_BUILD_FLAGS`, and `TESTS` are configurable, though `PACKAGES` is not used by the visible targets.

Dependencies and integration: depends on Go tooling, golangci-lint, sudo, compiled Nydus binaries, and smoke test helper environment. It coordinates with `tests/*_test.go` environment gates such as `BENCHMARK_TEST`, `PERFORMANCE_TEST`, and `TAKEOVER_TEST`.

Risks: `sudo -E` must preserve the required environment; race build can slow tests; lint is coupled to golangci-lint config compatibility; root privileges are needed for mount/cache tests.

Test signals: successful targets produce the `smoke.test` binary and run selected Go tests with timeouts and parallelism controls.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/smoke/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/smoke/dragonfly/dragonfly_test.go -->
## sources/cloud-native/nydus/smoke/dragonfly/dragonfly_test.go

Purpose: end-to-end tests for Nydus Dragonfly proxy integration across SDK proxy, HTTP proxy, strict no-fallback, and fallback-enabled modes.

Important APIs/types: `testEnv`, `setupTestEnv`, mode helpers `isSDKMode`, `isStrictMode`, `hasFallback`, `envOrDefault`, `TestDragonflyE2E`, and `truncateString`.

Control flow: setup reads required env (`TEST_MODE`, `NYDUSD_CONFIG`, `BOOTSTRAP_PATH`, Dragonfly configs through helpers), creates cache/mount dirs, starts a Dragonfly manager/scheduler/dfdaemon cluster, and starts nydusd. Subtests verify mount readability, multi-file and binary reads, directory traversal, blob cache population, reread consistency, SDK-client logs, and proxy/backend log activity. Failure subtests stop dfdaemon/scheduler, stop nydusd, clear caches, restart cold, then assert fallback or strict failure behavior and recovery logs.

State and persistence: uses real mount directory, nydusd log file, blob cache dir, Dragonfly cache dir, and external Dragonfly processes. It deliberately clears caches and drops page cache to force network/proxy behavior.

Dependencies and integration: integrates `testutil.go` process/mount/log helpers, nydusd config JSON, Dragonfly binaries/configs, FUSE mount behavior, and log messages from proxy health/fallback code.

Risks: timing-sensitive health/recovery log checks, fixed port assumptions from helpers, root/mount permissions, reliance on specific files inside the test image, and log-message drift. Some checks warn instead of failing to avoid flaky health-log timing.

Test signals: readable files and populated cache prove data path; strict mode expects read errors with proxy down; fallback modes expect successful cold reads via origin; recovery expects successful reads after Dragonfly restart and optional recovered/fallback log signals.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/smoke/dragonfly/dragonfly_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/smoke/dragonfly/proxy_error_test.go -->
## sources/cloud-native/nydus/smoke/dragonfly/proxy_error_test.go

Purpose: tests nydusd proxy error-handling semantics with a controllable local proxy that injects HTTP status errors and timeouts.

Important APIs/types: `proxyErrorEnv`, `injectError`, `injectTimeout`, `clearInjection`, `setupProxyErrorEnv`, `startNydusdForTest`, `runReadTest`, and `TestProxyErrorSimulation`.

Control flow: setup requires `REPO_ROOT` and `BOOTSTRAP_PATH`, builds `smoke/proxy`, starts it on port 4001, prepares fallback and no-fallback nydusd config paths, and creates cache/mount/log dirs. Each subtest clears caches, starts a fresh nydusd, injects proxy errors, reads `etc/os-release`, and asserts success or failure. Recovery exhausts/clears injected errors and checks that later cold reads succeed without fallback logging.

State and persistence: uses per-run nydusd log files, cache dirs parsed from config, a persistent proxy process with mutable injection rule, and restart counts to avoid log collision.

Dependencies and integration: integrates the test proxy control API, nydusd Dragonfly proxy request/retry code, config files under `misc/dragonfly`, and `testutil.go` process/mount/cache helpers.

Risks: expected outcomes depend on detailed retry semantics (`429` disables proxy, `403` does not retry, `500` and timeout handling differ by fallback mode); config paths must match repo layout; timeout tests are slow; port 4001 conflicts break setup.

Test signals: fallback config succeeds for 429/500/timeout and fails for 403; no-fallback config still succeeds on 429/500/timeout through disable-proxy retry but fails on 403; recovery succeeds through proxy with no fallback log.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/smoke/dragonfly/proxy_error_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/smoke/dragonfly/testutil.go -->
## sources/cloud-native/nydus/smoke/dragonfly/testutil.go

Purpose: shared process, nydusd, Dragonfly cluster, port, mount, cache, log, and filesystem traversal utilities for Dragonfly smoke tests.

Important APIs/types: `Process`, `StartProcess`, `Stop`, `Restart`, `NydusdInstance`, `StartNydusd`, `NydusdInstance::{Stop,Restart,LogLineCount,LogSince,LogContains}`, `DragonflyEnv`, `SetupDragonflyCluster`, `Teardown`, `WaitForPort`, `WaitForPortClosed`, `WaitForMount`, `ClearCaches`, `ParseCacheDir`, `CountFiles`, `FindFiles`, and `WaitForLogPattern`.

Control flow: `StartProcess` opens a log, starts a process in a new process group, writes a pid file, and waits for an optional TCP port. `Stop` sends SIGTERM, waits with timeout, kills if needed, then waits for port closure. `StartNydusd` builds standard CLI args, starts nydusd, and waits for the mountpoint. Cluster setup starts manager, scheduler, and dfdaemon on fixed ports from env configs. Utility waits poll ports, mountpoint command, log patterns, or filesystem traversal.

State and persistence: creates log/stdout/pid files, tracks process handles, reuses/suffixes logs on restart, mutates mount and cache directories, and writes `/proc/sys/vm/drop_caches`.

Dependencies and integration: depends on external binaries (`manager`, `scheduler`, `dfdaemon`, `nydusd`, `umount`, `mountpoint`), root permissions for cache dropping and unmounts, JSON config schema for blob cache work dir, and `testify/require`.

Risks: fixed ports can collide, scanner defaults may truncate very long log lines, stop does not signal whole process group despite setting pgid, cache clearing removes all entries under supplied dirs, and dropping kernel caches requires privileges. `FindFiles` returns `SkipDir` for too-deep files, which can behave unexpectedly when the current entry is not a directory.

Test signals: helpers fail fast when ports/mounts do not become ready or close, config parsing lacks `work_dir`, or process startup fails; higher-level tests use log line deltas and pattern detection for proxy health behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/smoke/dragonfly/testutil.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/smoke/proxy/main.go -->
## sources/cloud-native/nydus/smoke/proxy/main.go

Purpose: standalone HTTP/CONNECT proxy for smoke tests with dynamic and per-request failure simulation.

Important APIs/types: `InjectionRule`, `ProxyStats`, global injection state/counters, `handleControlAPI`, `maybeInjectError`, `handleFailureSimulation`, `httpsProxy`, `httpProxy`, `copyHeader`, and `transfer`.

Control flow: server listens on `:4001`; `/_test/inject` POST installs a rule, DELETE clears it, and `/_test/stats` returns counters/rule. Non-control traffic can be failed by query/header simulation or by the active injection rule. Dynamic injection only applies when `X-Dragonfly-Use-P2P` is present so disable-proxy/direct requests can pass through. CONNECT requests tunnel TCP after hijacking; HTTP requests are forwarded with a plain `http.Client`.

State and persistence: in-memory injection rule protected by mutex, atomic total/injected counters, and process logs. Counted rules decrement and clear when positive count reaches zero; negative count means persistent.

Dependencies and integration: used by `proxy_error_test.go`, exposes Dragonfly-style `X-Dragonfly-Error-Type: proxy`, and supports timeout/status scenarios that exercise nydusd retry/fallback paths.

Risks: listens on a fixed port, lacks graceful shutdown/auth, mutates and reuses the incoming request for forwarding, has no custom transport timeout for HTTP forwarding, and only increments injected counter for status responses, not timeout-only delays.

Test signals: control API status 200, stats JSON, injected HTTP statuses with Dragonfly error header, successful direct forwarding after disable-proxy headers disappear, and CONNECT/HTTP proxying behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/smoke/proxy/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/smoke/tests/api_test.go -->
## sources/cloud-native/nydus/smoke/tests/api_test.go

Purpose: smoke tests for nydusd API v1 and FUSE service behavior: status, metrics, prefetch, repeated submounts, nested mountpoint remount stat behavior, API mount, and hot config reload.

Important APIs/types: `APIV1TestSuite`, tests `TestDaemonStatus`, `TestMetrics`, `TestPrefetch`, `TestSubMountCache`, `TestNestedMountpointStatAfterRemount`, `TestMount`, `TestHotReloadConfig`, helper `buildLayer`, helper `visit`, and top-level `TestAPI`.

Control flow: tests build RAFS layers from generated texture files via `nydus-image`, create `tool.NydusdConfig`, mount nydusd, call APIs through `tool.Nydusd`, read files to generate metrics/prefetch/cache activity, mount/unmount child filesystems by API, and verify file trees. Hot reload fetches config for `/`, updates registry auth twice, and verifies reads through the API.

State and persistence: uses per-test work dirs, blob/cache/bootstrap paths, mount dirs, API sockets, generated layers, and nydusd runtime metrics. Submount test mounts and unmounts 300 unique child paths to exercise VFS index/cache turnover.

Dependencies and integration: integrates smoke `tool` package, texture/layer builders, snapshotter converter, nydusd binary/API, localfs backend, RAFS modes/cache settings, and FUSE mount behavior.

Risks: root/FUSE permissions required, async prefetch needs polling, metric opcode indexes can drift, submount loop is expensive, and `TestGenerateBlobcache`-style file reads rely on generated texture content. Nested stat behavior specifically guards stale entry invalidation after remount.

Test signals: daemon reaches `RUNNING`; global metrics flags and counters update after reads; blob-cache prefetch amount becomes positive; 300 mount/unmount cycles verify file trees; nested mountpoint can be statted immediately after remount; API-mounted RAFS verifies file tree; registry auth changes are observable.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/smoke/tests/api_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/smoke/tests/benchmark_test.go -->
## sources/cloud-native/nydus/smoke/tests/benchmark_test.go

Purpose: gated benchmark smoke test that converts or selects a container image, runs it through a snapshotter, captures startup/read metrics, and writes a JSON metric file.

Important APIs/types: `BenchmarkTestSuite`, `TestBenchmark`, `prepareImage`, `dumpMetric`, and top-level `TestBenchmark` gate on `BENCHMARK_TEST`.

Control flow: chooses snapshotter from `SNAPSHOTTER` defaulting to `nydus`, chooses mode from `BENCHMARK_MODE` (`oci`, `fs-version-5`, `fs-version-6`, `zran`), validates/selects image, converts via `nydusify convert` when needed, reads conversion JSON, runs a container with a UUID name, builds `tool.ContainerMetrics`, and writes metrics to `BENCHMARK_METRIC_FILE` or `benchmark.json`.

State and persistence: pulls/prepares source image, creates target nydus image tags, writes transient conversion metric JSON, runs a container, and persists benchmark metric JSON.

Dependencies and integration: requires containerd/nerdctl/nydus-snapshotter setup, nydusd/nydus-image/nydusify binaries, smoke `tool` helpers, and image support checks.

Risks: disabled unless `BENCHMARK_TEST` is set; external image/network/runtime dependencies can dominate failures; old nydusify support changes flags; metric map keys are assumed to exist; generated target images/containers require cleanup by helpers/environment.

Test signals: successful conversion, container run metrics (`E2ETime`, read count/amount), image size/conversion elapsed in output JSON, and final benchmark metric file.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/smoke/tests/benchmark_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/smoke/tests/blobcache_test.go -->
## sources/cloud-native/nydus/smoke/tests/blobcache_test.go

Purpose: smoke tests for nydus-image blobcache generation and command-line validation around `--blob-cache-dir`.

Important APIs/types: `BlobCacheTestSuite`, `compareTwoFiles`, `prepareTestEnv`, `TestCommandFlags`, `TestGenerateBlobcache`, and top-level `TestBlobCache`.

Control flow: `prepareTestEnv` creates a lower layer, writes an OCI tar blob into the blob dir named by digest, creates a blobcache output dir, and sets bootstrap path. `TestCommandFlags` runs invalid `nydus-image create` combinations and asserts expected error text. `TestGenerateBlobcache` first creates RAFS metadata and runs nydusd to populate runtime cache, then runs builder with `--blob-cache-dir` and compares generated `.blob.data`/`.blob.meta` against runtime cache files by digest.

State and persistence: uses work dir, blob dir, bootstrap, runtime cache dir, generated blobcache dir, mount dir, and files named from the OCI blob digest. Runtime cache population occurs via reading mounted regular files.

Dependencies and integration: depends on smoke texture/tool helpers, nydus-image builder, nydusd FUSE mount, localfs backend, OpenContainers digest library, and containerd logging for cleanup errors.

Risks: invalid-flag assertions depend on exact CLI error text; FUSE/cache population requires root and correct mount; walking reads use relative paths after deriving mount-relative names, which can be sensitive to current working directory; output file names assume digest hex naming and `.blob.data`/`.blob.meta` suffixes.

Test signals: invalid flag combinations fail with expected messages; builder-generated blobcache data and metadata digests match the runtime cache populated by nydusd.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/smoke/tests/blobcache_test.go -->
