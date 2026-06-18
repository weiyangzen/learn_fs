# subset-b-000500 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/kvstore/mapstore_test.go -->
# sources/distributed-fs/beegfs-go/common/kvstore/mapstore_test.go

Purpose: this file is the main behavioral and performance test suite for the generic Badger-backed `MapStore`. It validates key legality, create/get/update/delete flows, lock release semantics, iteration, concurrency behavior, auto-generated keys, and the Badger value-log garbage-collection runner.

Important APIs exercised include `NewMapStore[T]`, `CreateAndLockEntry`, `GetAndLockEntry`, `GetEntry`, `GetEntries`, `DeleteEntry`, release options such as `WithValue`, `WithAllowExisting`, `WithUpdateOnly`, and `WithDeleteEntry`, plus garbage-collection helpers such as `StartRunner`, `attemptGarbageCollection`, `runGarbageCollection`, and `systemLoad.isSystemLoadHigh`.

Control flow is test-driven around temporary Badger directories under `/tmp`. Entries are created, mutated through locked pointers, committed through release callbacks, and then read or iterated in lexicographic Badger key order. Several tests intentionally hold locks across goroutines to prove the in-memory `entryLocks` cache and `keepLock` counter preserve serialization.

State and persistence behavior centers on BadgerDB records plus transient per-key locks. Tests assert that deleted entries disappear from both DB and cache, auto-generated keys are fixed-width base-36 strings, iterators can be cleaned up repeatedly, and GC delays change depending on system load and Badger `ErrNoRewrite`.

Dependencies include Badger v4, `testify/assert`, `testify/require`, `testify/mock`, OS temp directories, runtime CPU counts, and package-local mock GC/system-load types. Integration points are the production `MapStore` implementation and Badger's value-log GC.

Risks: benchmarks contain acknowledged races around concurrent create/delete timing and use sleeps for synchronization. Tests also inspect private fields such as `entryLocks`, making them sensitive to internal refactors. System-load parsing is Linux `/proc/loadavg` shaped.

Test signals: coverage is broad for CRUD, reserved-key rejection, iterator boundaries, locking, concurrent access, GC scheduling, and load detection. Performance benchmarks cover create, lock/get, delete, iteration, and two-DB concurrent flows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/kvstore/mapstore_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/logger/badgerlog.go -->
# sources/distributed-fs/beegfs-go/common/logger/badgerlog.go

Purpose: bridges BadgerDB logging to the repository's zap-based logging system. Badger expects an interface with `Errorf`, `Warningf`, `Infof`, and `Debugf`; this type adapts those formatted calls to zap levels.

Important APIs are `BadgerLoggerBridge`, `NewBadgerLoggerBridge(subComponent string, logger *zap.Logger)`, and the four level methods. The constructor adds a `database=<subComponent>` field so Badger messages can be attributed to a logical database.

Control flow is direct: each Badger callback trims a trailing newline from the format string, calls `fmt.Sprintf`, and emits one zap message at the corresponding level. There is no buffering, persistence, or retry behavior in the bridge itself.

State is limited to the wrapped `*zap.Logger`. Dependencies are `fmt`, `strings`, and `go.uber.org/zap`. Integration points are Badger's `Logger` interface and any package that wants Badger logs to share application logging configuration.

Risks: formatting every message eagerly can be expensive if Badger debug logs are high volume. Format-string mismatches are not type checked. The bridge assumes newline trimming is enough to normalize Badger messages.

Test signals: no direct test in this subset, but it is exercised indirectly wherever `MapStore` configures Badger logging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/logger/badgerlog.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/logger/logfile.go -->
# sources/distributed-fs/beegfs-go/common/logger/logfile.go

Purpose: validates and prepares file-system paths used by logfile logging before lumberjack rotation is installed.

Important APIs are unexported `ensureLogsAreWritable(configFile string)` and `ensureLogDirExists(dirPath string, perm os.FileMode)`. `ensureLogsAreWritable` derives the directory from the requested log file, creates it if needed, writes and closes a process-id-named temp file, then removes it.

Control flow is fail-fast: directory creation/stat errors return immediately; temp-file create, close, and remove errors are propagated. The temp file check is specifically about directory write permission, not just target-file writability, because rotation creates sibling files.

State and persistence behavior is intentionally temporary. The only lasting side effect should be creation of the log directory. Dependencies are `os`, `filepath`, and `fmt`.

Integration points: `logger.New` calls this before constructing `lumberjack.Logger` for `LogFile` output.

Risks: temp files use `0755`, which is executable and broader than typical log-file permissions. A process crash between create and remove may leave a dot temp file. Existing directories are not permission-normalized.

Test signals: no direct unit test here; `logger_test.go` currently covers logger construction but not logfile directory and permission edge cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/logger/logfile.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/logger/logger.go -->
# sources/distributed-fs/beegfs-go/common/logger/logger.go

Purpose: provides a configurable zap logger wrapper that supports stdout, stderr, rotating log files, syslog, and dynamic log-level updates through the config manager listener interface.

Important APIs/types are `Logger`, `Config`, `supportedLogTypes`, `SupportedLogTypes`, `New`, `Configurer`, `UpdateConfiguration`, and `getLevel`. BeeGFS log levels 0 through 5 map to zap fatal, error, warn, info, and debug.

Control flow in `New` forks between developer and production modes. Developer mode ignores configured level and builds zap's development logger at debug. Production mode creates a console encoder with ISO timestamps, creates an atomic zap level, chooses a write syncer by configured type, then builds a zap core. `LogFile` uses `ensureLogsAreWritable` and lumberjack; `Syslog` uses `NewSyslogWriteSyncer`.

State is the embedded `*zap.Logger` plus `zap.AtomicLevel`. `UpdateConfiguration` type-asserts a `Configurer`, reads its logging config, computes the new level, and mutates only the atomic level; destination and encoder are not changed at runtime.

Dependencies include zap, zapcore, lumberjack, syslog, `configmgr`, reflection, and OS streams. Integration points include app config reload, syslog, file rotation, and packages that embed logger config in their own configuration structs.

Risks: runtime updates ignore destination changes, which may surprise callers. Syslog parsing depends on the console encoder format. Invalid levels return info plus an error, so callers must honor the error. Developer mode discards configured type/file entirely.

Test signals: `logger_test.go` checks developer/stdout creation, unsupported type errors, level updates, and all level mappings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/logger/logger.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/logger/logger_test.go -->
# sources/distributed-fs/beegfs-go/common/logger/logger_test.go

Purpose: unit tests the common logger constructor, dynamic configuration update path, and BeeGFS-to-zap log-level mapping.

Important test helpers include `testConfig`, which implements `Configurer` via `GetLoggingConfig`. Tests call `New`, `UpdateConfiguration`, and unexported `getLevel`.

Control flow: `TestNew` builds a developer logger and a stdout logger, then verifies unsupported types fail. `TestUpdateConfiguration` starts at warn level, supplies a replacement config with debug level, and checks the atomic level changes. `TestGetLevel` table-tests all valid numeric levels plus invalid level 6.

State behavior under test is the `Logger.level` atomic level and the embedded zap logger pointer. Persistence and external destinations are not heavily exercised; the test avoids logfile and syslog setup.

Dependencies include `testing`, `testify/assert`, `fmt`, and zapcore. Integration signal is focused on the logger package's config contract rather than real config manager reloads.

Risks: tests do not cover file permission failure, lumberjack setup, syslog write translation, developer-mode update behavior, or destination immutability after update. Assertions read private fields, so internal restructuring can require test updates.

Test signals: current coverage is good for core level semantics and constructor sanity but intentionally shallow for IO-backed destinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/logger/logger_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/logger/syslog.go -->
# sources/distributed-fs/beegfs-go/common/logger/syslog.go

Purpose: implements a zap `WriteSyncer` that sends console-encoded zap log entries to syslog with severity mapping.

Important APIs are `SyslogWriteSyncer`, `NewSyslogWriteSyncer(priority syslog.Priority, tag string)`, `Write`, and `Sync`. The constructor opens a `log/syslog` writer. `Write` parses zap console output as timestamp, level, and message separated by tabs.

Control flow: if the encoded line has fewer than three tab-separated fields, it writes bytes unchanged to syslog. Otherwise it drops zap's timestamp, joins remaining fields into the syslog message, maps zap levels to syslog methods, and returns `len(p)` plus the syslog error. `Sync` is a no-op because `log/syslog` does not expose flushing.

State is the underlying `*syslog.Writer`. Dependencies include `log/syslog` and `strings`. Integration points are `logger.New` with `Type=Syslog` and zapcore's write path.

Risks: parsing is tightly coupled to zap console encoder output. `strings.Join(splitString[2:], "")` removes tab separators from structured fields, which can reduce readability. `log/syslog` is not portable to every platform. Performance is noted as lower than other destinations.

Test signals: no direct tests in this subset. Regression tests would need a fake syslog writer or an interface extraction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/logger/syslog.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/probecache/probecache.go -->
# sources/distributed-fs/beegfs-go/common/probecache/probecache.go

Purpose: caches negative capability or feature probe results for a bounded window so tight loops avoid repeatedly invoking known-failing newer operations while still allowing later recovery after upgrades.

Important API is `Availability` with `New(recheckAfter)`, `ShouldAttempt`, and `MarkUnavailable`. The type stores `unavailableUntil`, `recheckAfter`, and a mutex.

Control flow: `ShouldAttempt` returns true when current time is after the deadline. `MarkUnavailable` sets the deadline to now plus `recheckAfter` only if the previous deadline has expired. That non-extending behavior is central: repeated failures during the same window do not postpone the next re-probe.

State is in-memory only and protected by `sync.Mutex`. There is no persistence across process restarts. Dependencies are only `sync` and `time`.

Integration points are callers that optimistically try newer ioctls/RPCs, call `MarkUnavailable` on unsupported responses, and fall back until `ShouldAttempt` becomes true again.

Risks: use of `time.Now` directly makes tests sleep-based and can be affected by clock changes. A zero or negative `recheckAfter` effectively disables negative caching. It caches only one availability state per instance, so callers need distinct instances per probe target.

Test signals: `probecache_test.go` covers cold state, unavailable state, expiry, non-extension, and re-arming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/probecache/probecache.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/probecache/probecache_test.go -->
# sources/distributed-fs/beegfs-go/common/probecache/probecache_test.go

Purpose: verifies the intended negative-probe cache semantics for `Availability`.

Important tests are `TestAvailabilityColdState`, `TestAvailabilityAfterMarkUnavailable`, `TestAvailability_AfterWindowExpires`, `TestAvailabilityRepeatedMarkUnavailableDoesNotExtendWindow`, and `TestAvailabilityMarkUnavailableAfterWindowResetsDeadline`.

Control flow uses short TTLs and sleeps to move through the unavailability window. The repeated-mark test inspects the package-private `unavailableUntil` deadline to ensure a second mark inside the window is a no-op. The reset test waits past expiry, confirms probing is allowed, then re-arms the window.

State behavior under test is the in-memory deadline protected by the mutex. There is no persistence or external dependency.

Dependencies are `testing`, `time`, `fmt`, and `testify/assert`. Integration signal is pure unit-level; no caller-specific feature probe is exercised.

Risks: sleep-based timing can be flaky under extreme scheduling delays, though durations are small and assertions are simple. Tests do not exercise concurrent callers, zero TTL, negative TTL, or clock jumps.

Test signals: good coverage of the core API contract, especially the important non-extending deadline behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/probecache/probecache_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/registry/cache.go -->
# sources/distributed-fs/beegfs-go/common/registry/cache.go

Purpose: provides a thread-safe TTL cache for a remote component capability registry, including lazy initialization and refresh-on-error behavior.

Important types/APIs are `getClientFunc`, `CachedComponentRegistry`, options `WithRegistryTTL` and `WithSkipInit`, `NewCachedComponentRegistry`, `GetBuildInfo`, `RequireFeature`, `RequireFeatures`, `updateIfNeeded`, and `updateRegistry`.

Control flow: construction applies options, validates the client resolver, and either fetches capabilities immediately or starts with `ErrRegistryUninitialized`. Public reads call `updateIfNeeded`, then inspect cached registry and last error under an RW mutex. If a prior error exists, refresh is synchronous. If TTL has expired without an error, refresh happens asynchronously in a goroutine.

State includes the cached `ComponentRegistry`, component `startTime`, `lastUpdate`, `lastErr`, TTL, and mutex. Registry replacement occurs only when the component start timestamp changes, so same-process feature responses do not replace the cached registry.

Dependencies are `context`, `sync`, `time`, and protobuf `flex`. Integration points are long-lived CTL or service clients that need to gate behavior by remote capabilities without hitting gRPC on every check.

Risks: asynchronous refresh means callers may observe stale data for one call after TTL expiry. If capabilities change without a start timestamp change, the registry is not replaced. `lastUpdate` is set before the fetch, so repeated failures are throttled only after the first error path forces sync retries.

Test signals: cache tests cover constructor errors, TTL, async refresh, refresh after error, lazy initialization, and feature requirements.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/registry/cache.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/registry/cache_test.go -->
# sources/distributed-fs/beegfs-go/common/registry/cache_test.go

Purpose: tests `CachedComponentRegistry` behavior against a configurable mock `RegistryGetter`.

Important helpers are `mockResponse`, `mockRegistryClient`, `newCapabilities`, and `registryClientFunc`. The mock returns queued responses and counts calls under a mutex.

Control flow: tests verify missing clients and unimplemented capability RPCs surface the expected sentinels; TTL values are applied; reads inside TTL do not refresh; reads after TTL eventually trigger asynchronous refresh; failed refresh stores `lastErr`; a subsequent call refreshes synchronously and clears the error; lazy `WithSkipInit` registries fetch on first `RequireFeature(s)`.

State behavior under test includes `ttl`, `lastErr`, cached build info, call counts, and nested feature trees. The tests use `assert.Eventually` for asynchronous refresh.

Dependencies are `testing`, `time`, `sync`, `grpc/status`, `grpc/codes`, `timestamppb`, and `testify/assert`.

Integration points are the gRPC capabilities endpoint and the feature validation layer in `capability.go`.

Risks: async timing tests can be sensitive to slow environments. Tests inspect private mutex-protected state, which makes internal changes visible. They do not test concurrent callers racing through `updateRegistry`, nil response shape errors, or unchanged start timestamp with changed features.

Test signals: strong coverage of cache refresh and lazy/error behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/registry/cache_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/registry/capability.go -->
# sources/distributed-fs/beegfs-go/common/registry/capability.go

Purpose: models a component's build metadata and supported feature tree, retrieves it from a remote gRPC endpoint, and validates required features.

Important APIs are `RegistryGetter`, `ComponentRegistry`, `NewComponentRegistry`, `GetComponentRegistry`, `GetBuildInfo`, `GetCapabilities`, `RequireFeature`, `RequireFeatures`, `GetBuild`, `getBuild`, `isRequiredFeatureSupported`, and `isRequiredFeaturesSupported`.

Control flow: `GetComponentRegistry` calls `GetCapabilities`, translates gRPC `Unimplemented` to `ErrCapabilitiesNotSupported`, validates non-nil response and non-zero `StartTimestamp`, and builds a deep-copy registry. Feature checks descend through nested `flex.Feature.SubFeature` maps, with `nil` representing a plain supported feature.

State is immutable by convention: constructor and getters clone protobuf messages and feature maps to avoid callers mutating registry internals. Dependencies include gRPC status/codes, protobuf cloning, and `flex` messages.

Integration points include `CachedComponentRegistry`, feature-gated commands such as RST filter support, and remote services exposing `GetCapabilities`.

Risks: `isRequiredFeatureSupported` checks only path existence and does not inspect payload fields beyond nested maps. Nil available features mean no subfeatures are allowed. Error messages include build labels but not the missing subfeature path except for single-feature checks.

Test signals: `capability_test.go` covers plain and nested feature support and unsupported error wrapping. Cache tests also exercise lazy capability checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/registry/capability.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/registry/capability_test.go -->
# sources/distributed-fs/beegfs-go/common/registry/capability_test.go

Purpose: validates feature support checks for `ComponentRegistry`, including nested subfeature trees.

Important tests are `TestRequireFeatureSupportMatrix`, `TestRequireFeature`, and `TestRequireFeatures`. They construct in-memory registries with plain features, nested child/grandchild features, and unused features.

Control flow is table-driven. Single-feature tests call `RequireFeature(feature, sub...)` and assert success or `ErrUnsupportedFeature`. Multi-feature tests pass maps of required `flex.Feature` trees to `RequireFeatures` and verify recursive matching behavior.

State behavior is limited to immutable test registry maps. Persistence and remote RPC retrieval are outside this file.

Dependencies include `testing`, `testify/assert`, and protobuf `flex`. Integration point is the public feature validation API consumed by registry cache and callers.

Risks: tests do not verify clone isolation from `NewComponentRegistry` or `GetCapabilities`, build-info formatting, nil build-info fallback, malformed `GetCapabilities` responses, or gRPC error translation. One test name has a typo (`supported nexted`) but behavior is clear.

Test signals: good coverage of the recursive feature matrix and sentinel wrapping for unsupported features.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/registry/capability_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/registry/errors.go -->
# sources/distributed-fs/beegfs-go/common/registry/errors.go

Purpose: defines registry package sentinel errors for feature and capability lookup failures.

Important exported errors are `ErrUnsupportedFeature`, `ErrRegistryClientUnavailable`, `ErrRegistryUninitialized`, and `ErrCapabilitiesNotSupported`.

Control flow is indirect: other registry files wrap or compare these sentinels with `errors.Is`. `capability.go` returns unsupported-feature errors when required feature trees are absent and maps unimplemented gRPC capabilities to `ErrCapabilitiesNotSupported`. `cache.go` uses unavailable and uninitialized sentinels for client resolver and lazy-init states.

State and persistence: none; these are package-level immutable `error` values from `errors.New`.

Dependencies are only the standard `errors` package. Integration points are callers that branch on unsupported remote features versus inability to fetch the registry at all.

Risks: callers need to preserve wrapping with `%w` or `errors.Join` for `errors.Is` to work. The sentinels intentionally distinguish unsupported features from unsupported capability RPC, which should not be collapsed in UI or retry logic.

Test signals: cache and capability tests assert these sentinels with `assert.ErrorIs`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/registry/errors.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/registry/feature.go -->
# sources/distributed-fs/beegfs-go/common/registry/feature.go

Purpose: centralizes string constants for known registry capability feature names.

Important API is `FeatureFilterFiles = "filter-files"`. This is used by RST job request preparation when filter expressions are supplied, requiring the remote BeeRemote registry to advertise filter support before compiling and applying file filters.

Control flow and state are absent; this file is a compile-time constants holder.

Dependencies: none beyond the package itself. Integration points are feature-gated callers and `ComponentRegistry.RequireFeature`.

Risks: feature names are wire/API contracts; renaming breaks compatibility with services that publish the old capability name. New features should be added here to avoid ad hoc strings.

Test signals: no direct tests for the constant. Its behavior is indirectly covered when callers require feature strings against registry responses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/registry/feature.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/rst/builder.go -->
# sources/distributed-fs/beegfs-go/common/rst/builder.go

Purpose: implements `JobBuilderClient`, a special RST provider that turns broad user requests over paths, globs, directories, or remote prefixes into concrete BeeRemote job requests.

Important APIs are `NewJobBuilderClient`, `GetJobRequest`, `GenerateWorkRequests`, `ExecuteJobBuilderRequest`, `executeJobBuilderRequest`, and `walkLocalPathInsteadOfRemote`. Most normal provider methods return unsupported operations because the builder does not transfer data.

Control flow: `GetJobRequest` wraps `flex.JobRequestCfg` in a builder job with RST ID 0. `GenerateWorkRequests` recreates a single builder work request. `ExecuteJobBuilderRequest` compiles optional filters, chooses local or remote walking, handles download path mapping, and delegates to `executeJobBuilderRequest`. That function fans out path processing with `errgroup`, increases worker count when the submission channel is draining quickly, emits job requests, and stores resume tokens on the work request when walks hit `maxRequests`.

State includes the builder's submitted/error counters, resume token in `ExternalId`, and access to the shared RST map and mount point. It may persist RST configuration to files/directories when `--update` is set via helpers in `rst.go`.

Dependencies include filesystem walking/filtering, RST provider map, protobuf job messages, errgroup, runtime GOMAXPROCS, and path mapping helpers.

Integration points are BeeRemote job submission, local BeeGFS filesystem traversal, remote provider `GetWalk`, and `BuildJobRequests`.

Risks: concurrency updates are protected only around builder counters and resume state; path-generation logic must stay deterministic across local and remote walks. Filters are rejected for downloads. Reschedule behavior depends on provider resume tokens being correct.

Test signals: no direct builder tests here, but RST tests cover work-request recreation and segment generation; RST integration tests should cover builder walking separately.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/rst/builder.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/rst/errors.go -->
# sources/distributed-fs/beegfs-go/common/rst/errors.go

Purpose: defines RST sentinel errors and a timestamp-wrapping error used by job preparation and completion logic.

Important APIs are exported errors such as `ErrConfigRSTTypeNotSet`, `ErrReqAndRSTTypeMismatch`, `ErrUnsupportedOpForRST`, `ErrConfigUpdateNotAllowed`, `ErrJobAlreadyComplete`, `ErrJobAlreadyOffloaded`, precondition/open-file/stub-file errors, `IsErrJobTerminalSentinel`, `MtimeErr`, and `GetErrJobAlreadyCompleteWithMtime`.

Control flow is indirect. Provider implementations and builders wrap these sentinels to classify terminal no-op states, invalid configuration, unsupported request/provider combinations, lock/precondition failures, and remote unavailability. `MtimeErr` preserves the mtime associated with already-complete jobs while still unwrapping to the sentinel.

State is limited to package-level immutable errors and per-instance `MtimeErr` fields. Dependencies are `errors`, `fmt`, and `time`.

Integration points are BeeRemote job status mapping, CLI error reporting, file-state preparation, and tests that use `errors.Is`.

Risks: sentinel overload can hide context if wrappers are not descriptive. `IsErrJobTerminalSentinel` currently treats only already-complete/offloaded as terminal; adding new terminal states requires updating it. `MtimeErr.Error` uses `time.String`, not a stable RFC3339 format.

Test signals: S3 and store tests assert several sentinels; no dedicated tests for `MtimeErr`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/rst/errors.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/rst/flags.go -->
# sources/distributed-fs/beegfs-go/common/rst/flags.go

Purpose: centralizes CLI flag-name constants used in RST error messages and command wiring.

Important constants are `AllowRestoreFlag`, `PriorityFlag`, `RemotePathFlag`, `RemoteTargetFlag`, `StorageClassFlag`, and `UpdateFlag`.

Control flow and state are absent. The constants are read by RST helpers to produce consistent messages such as missing `--remote-target`, missing `--remote-path`, or requiring `--allow-restore`.

Dependencies: none. Integration points include RST job request preparation, S3 archive restore checks, and CTL commands that define matching flags.

Risks: these strings are user-facing CLI contracts. Renaming a constant value without updating cobra command definitions would create misleading error messages. Adding new RST flags should use this file to avoid drift.

Test signals: no direct tests. Error-message assertions elsewhere may indirectly depend on these values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/rst/flags.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/rst/jobrequest.go -->
# sources/distributed-fs/beegfs-go/common/rst/jobrequest.go

Purpose: prepares and submits BeeRemote job requests from user-facing `flex.JobRequestCfg` values.

Important APIs/types are `JobResponse`, `SubmitJobRequest`, `prepareJobRequests`, `mountPathInfo`, and `getMountPathInfo`.

Control flow: `SubmitJobRequest` creates a BeeRemote client, spawns a goroutine, prepares one or more `beeremote.JobRequest`s, submits each through `SubmitJob`, and streams `JobResponse`s. Unavailable gRPC submit errors are marked fatal. `prepareJobRequests` resolves the BeeGFS mount, normalizes the path, sets default remote path/priority, validates filter feature support, decides whether a builder job is needed, and otherwise builds provider-specific requests from explicit RST ID, stub-file contents, or entry metadata RST IDs.

State and persistence behavior: preparation may mutate the supplied config with normalized path, remote path, priority, and remote target. It reads BeeGFS entry details, stub contents, mappings, and remote registry capabilities; it does not itself persist data except through later builder/RST flows.

Dependencies include CTL config clients, filesystem filters, registry feature checks, scheduler default priority, entry/mapping utilities, BeeRemote protobuf/gRPC clients, and OS/stat metadata.

Integration points are CLI request submission, BeeRemote RPCs, local BeeGFS metadata, stub files, RST provider map construction, and job builder fallback.

Risks: config mutation can surprise callers that reuse a cfg. `SubmitJobRequest` continues after `prepareJobRequests` error and may iterate a nil slice after sending one error response. Filter support depends on remote registry availability. Ambiguous stub/RST cases are pushed to later helpers.

Test signals: no direct tests in this subset; behavior is exercised by higher-level RST/CTL flows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/rst/jobrequest.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/rst/mock.go -->
# sources/distributed-fs/beegfs-go/common/rst/mock.go

Purpose: provides a `Provider` implementation for tests and higher-level packages that need an RST without real remote storage.

Important API is `MockClient`, embedding `testify/mock.Mock`, with implementations of all `Provider` methods. It has special built-in behavior for `flex.MockJob` requests and mock-driven behavior for other request types.

Control flow: `GenerateWorkRequests` returns generated segments for mock jobs or configured mock expectations. `ExecuteWorkRequestPart` marks parts completed unless a mock job asks to fail. `CompleteWorkRequests` succeeds or fails for mock jobs, otherwise delegates to mock expectations. Unsupported methods such as builder execution and remote info return RST sentinels.

State is test expectation state inside `mock.Mock` plus direct mutations of `flex.Work_Part.Completed`. There is no persistence.

Dependencies include `testify/mock`, filesystem stream result types, protobuf job/work messages, and RST segment recreation helpers.

Integration points are worker-manager tests, `ClientStore.SetMockClientForTesting`, and any package that initializes a mock RST through `rst.New`.

Risks: some mock methods call `args.Get(0).(*flex.RemoteStorageTarget)` or `args.Get(1).(time.Duration)`, so missing expectations panic. `GetJobRequest` returns nil, which is fine for current mock use but unsafe if used as a normal provider.

Test signals: this file is itself test support. RST tests use mock-job behavior indirectly through `RecreateWorkRequests`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/rst/mock.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/rst/rst.go -->
# sources/distributed-fs/beegfs-go/common/rst/rst.go

Purpose: defines the core Remote Storage Target abstraction, provider construction, common work-request generation helpers, BeeGFS file locking/preparation logic, stub-file helpers, download path mapping, and RST map construction.

Important APIs/types are `Provider`, `SupportedRSTTypes`, `New`, `RecreateWorkRequests`, `generateSegments`, `BuildJobRequests`, `BuildJobRequest`, state predicates like `IsFileLocked` and `IsFileAlreadySynced`, `PrepareFileStateForWorkRequests`, `GetLockedInfo`, `CreateOffloadedDataFile`, `GetOffloadedUrlPartsFromFile`, `CheckEntry`, `IsValidRstId`, `GetDownloadRemotePathDirectory`, `GetDownloadInMountPath`, `NormalizePath`, `GetLastCompletedJobFromRst`, and `GetRstMap`.

Control flow: providers are selected from protobuf RST config. Job requests are recreated from job plus segment data. `BuildJobRequests` gathers locked info, handles fatal/nonfatal preconditions, clones configs per RST, calls provider-specific request building, prepares file state, and decides whether to keep BeeGFS locks. `PrepareFileStateForWorkRequests` handles synced/offloaded no-op states, stub creation, overwrite checks, preallocation, data-state transitions, persistent RST config updates, rollback on error, and external ID generation.

State and persistence behavior is substantial: BeeGFS access flags are set/cleared, file data state may switch between normal/offloaded, stub files contain `rst://id:path`, files may be preallocated or removed on rollback, and RST IDs can be written to file or directory metadata.

Dependencies include BeeGFS messaging and entry CTL packages, filesystem providers, BeeRemote/Flex protobufs, config clients, gRPC status handling, OS/fs/syscall, protobuf cloning, and timestamps.

Integration points are every RST provider, BeeRemote job lifecycle, CTL entry metadata, local filesystem operations, and S3 implementation.

Risks: locking and rollback paths are complex; missed unlocks or partial rollback can leave files locked, preallocated, or with wrong data state. `parseRstUrl` is S3-key oriented. Download path mapping must remain consistent with builder walking. Provider config mutation requires cloning discipline.

Test signals: `rst_test.go` covers request recreation and segments, while `s3_test.go` and `store_test.go` cover provider-specific and store behaviors. Many file-state branches need integration tests with BeeGFS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/rst/rst.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/rst/rst_test.go -->
# sources/distributed-fs/beegfs-go/common/rst/rst_test.go

Purpose: unit tests common RST helpers for recreating work requests from jobs and splitting file ranges into work segments.

Important fixtures are `baseTestJob`, `baseTestSegments`, and `getNewTestSegments`. Tests are `TestRecreateWorkRequests` and `TestGenerateSegments`.

Control flow: `TestRecreateWorkRequests` clones a base job into sync and mock request types, regenerates work requests from two segments, and checks copied job/request fields, request IDs, external IDs, segment identity, remote target, and type-specific payload cloning. It also verifies invalid request types produce work requests with nil type. `TestGenerateSegments` table-tests empty, one-byte, evenly split, and unevenly split files.

State behavior under test includes deep-copy expectations for protobuf fields and direct segment reuse. Persistence is not involved.

Dependencies include `testing`, `testify/assert`, `testify/require`, protobuf cloning, and BeeRemote/Flex messages.

Integration points are provider `GenerateWorkRequests` implementations that use `RecreateWorkRequests` and `generateSegments`, especially mock and S3 providers.

Risks: tests do not cover builder work-request recreation with nil segments in depth, segment invalid inputs such as zero segment count, or file sizes large enough to expose overflow. They intentionally rely on private helpers from the same package.

Test signals: good coverage for core request shape and byte/part range math.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/rst/rst_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/rst/s3.go -->
# sources/distributed-fs/beegfs-go/common/rst/s3.go

Purpose: implements the S3-backed RST provider, including AWS client construction, job request generation, object walking, archive restore handling, upload/download execution, multipart completion, and metadata synchronization.

Important APIs/types include `S3StorageClass`, `S3Client`, `newS3`, `checkStartAfterSupport`, `GetJobRequest`, `GenerateWorkRequests`, `IsWorkRequestReady`, `ExecuteWorkRequestPart`, `CompleteWorkRequests`, `GetWalk`, `s3ResumeToken`, `GetRemotePathInfo`, `GenerateExternalId`, `SanitizeRemotePath`, upload/download work generation, completion helpers, `prepareJobRequest`, `archiveStatus`, `getObjectMetadata`, multipart helpers, `upload`, `download`, and `recommendedSegments`.

Control flow: construction loads AWS config from RST settings, chooses path-style when endpoint host is not bucket-prefixed, and validates archival storage-class policy. Job generation validates sync type and external ID, prepares locks/metadata, creates multipart upload IDs when needed, and splits into work requests. Work execution dispatches to put/upload-part or ranged get. Completion aborts or finishes multipart uploads, verifies mtimes have not changed, writes stubs for offloaded uploads, clears offloaded state for downloads, and updates file mtimes.

State and persistence span S3 objects, multipart upload IDs, `beegfs-mtime` metadata, object tags/storage class, archive restore requests, local file parts, BeeGFS locks, data state, and resume tokens encoded as base64 gob.

Dependencies include AWS SDK v2 S3, smithy errors, doublestar glob matching, filesystem provider IO, BeeGFS entry/data-state helpers, protobuf cloning/timestamps, and RST common helpers.

Integration points are BeeRemote workers, S3-compatible object stores, directory-bucket pagination differences, archive storage classes, local BeeGFS mounts, and CTL configuration.

Risks: S3 client is concrete, making tests hard. Pagination resume is subtle, especially without `StartAfter`. Metadata key `beegfs-mtime` is reserved and user metadata can conflict. Archive restore concurrency relies on specific error codes. Completion only detects mtime changes, not content changes with preserved mtime.

Test signals: `s3_test.go` covers basic request generation and unsupported operation errors, but most S3 IO paths lack unit tests until the client is abstracted.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/rst/s3.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/rst/s3_test.go -->
# sources/distributed-fs/beegfs-go/common/rst/s3_test.go

Purpose: provides focused unit coverage for S3 provider work-request generation and completion error classification without contacting a real S3 service.

Important fixtures include `testS3Client`, a partially initialized `S3Client` with policies, and tests `TestGenerateWorkRequests` and `TestCompleteRequests`.

Control flow: `TestGenerateWorkRequests` uses a mock filesystem, writes a small local file, sets `FastStartMaxSize` to avoid multipart upload, builds upload/download sync jobs with locked info, and verifies upload generation emits one request with the right operation. It also asserts mock job type mismatch, unsupported sync operation, and external-ID precondition errors. `TestCompleteRequests` verifies completion rejects non-sync jobs and unsupported sync operations.

State behavior under test includes local mock filesystem contents, job external IDs, `LockedInfo`, and generated work request fields. Real S3 state and network calls are deliberately avoided.

Dependencies are `testing`, `testify`, mock filesystem provider, BeeRemote/Flex protobufs, and timestamps.

Integration points are S3 `GenerateWorkRequests`, common `RecreateWorkRequests`, and provider error sentinels.

Risks: download generation, object metadata, archive restore, multipart upload, ranged IO, walking, and completion success paths are not tested because `S3Client.client` is concrete. The test comments explicitly call out the need for an S3 provider interface.

Test signals: adequate smoke coverage for supported/unsupported request classification.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/rst/s3_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/rst/store.go -->
# sources/distributed-fs/beegfs-go/common/rst/store.go

Purpose: maintains a thread-safe mapping from RST IDs to provider clients, including the special job-builder provider.

Important APIs/types are `ClientStore`, `NewClientStore`, `Get`, `JobBuilderRstId`, `UpdateConfig`, and `SetMockClientForTesting`.

Control flow: a new store starts empty with a mount point. `UpdateConfig` either initializes clients by calling `New` for each config and then adding `JobBuilderRstId=0`, or, after initialization, rejects any dynamic changes. The rejection path verifies count, forbids RST ID 0, compares existing configs with `proto.Equal`, and ensures all existing configs are present.

State is the `clients` map protected by an RW mutex plus the mount point. Once initialized, provider configs are effectively immutable for the process. The testing hook mutates the map directly under lock.

Dependencies include `sync`, filesystem provider, protobuf cloning/equality, and RST provider construction.

Integration points are worker/manager code that needs current clients by RST ID, dynamic config reload paths, and tests injecting `MockClient`.

Risks: callers are warned not to retain provider references, but the API cannot enforce that. Dynamic updates are currently all-or-nothing rejected, so config changes require restart. `SetMockClientForTesting` can bypass invariants such as adding the builder.

Test signals: `store_test.go` covers initial config and rejection of update/add/remove changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/rst/store.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/rst/store_test.go -->
# sources/distributed-fs/beegfs-go/common/rst/store_test.go

Purpose: tests `ClientStore.UpdateConfig` initialization and immutability rules.

Important test is `TestUpdateConfig`. It creates a mock filesystem, a new client store, and an S3 RST config.

Control flow: first update initializes the store and should succeed. Subsequent calls attempt to modify the bucket, add an RST, and remove all RSTs; each must return `ErrConfigUpdateNotAllowed`.

State behavior under test is the transition from empty `clients` map to initialized map containing the S3 provider and implicit job builder, then rejecting later changes. Persistence is limited to in-memory provider state; no S3 calls are made during the tested config.

Dependencies include `testing`, `testify/assert`, mock filesystem, context, and Flex RST config messages.

Integration points are RST provider construction and protobuf config equality.

Risks: the test does not assert that the job builder was added or that `Get` returns expected providers. It does not cover attempts to use ID 0, same-config reload success after initialization, invalid RST type errors, or mock injection.

Test signals: clear coverage for the major policy that RST configuration cannot change after initial setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/rst/store_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/scheduler/scheduler.go -->
# sources/distributed-fs/beegfs-go/common/scheduler/scheduler.go

Purpose: implements a priority-aware token scheduler for work queues, balancing back-pressure, observed throughput, rescheduled work, and priority fairness.

Important APIs/types are constants `DefaultPriority` and `priorityLevels`, options `WithNodeName`, `WithFairness`, `WithAllowedTokensBufferPct`, `WithAverageWindow`, `WithAllowedTokensGrowthRateMax`, `WithAllowedTokensMin`, `PriorityToken`, `Scheduler`, `NewScheduler`, token/reschedule methods, submission-ID helpers, `getNextPriorityFunc`, `geometricRatio`, and `geometricFairnessWeights`.

Control flow: `NewScheduler` configures defaults, computes geometric weights, registers expvar metrics once, seeds per-priority submission IDs, and starts a ticker goroutine. The goroutine periodically estimates completed work using an exponential moving average, accumulates allowed token budget, subtracts current queue usage, distributes tokens by dynamic priority weights, and publishes a `[5]PriorityToken` batch to a buffered channel.

State includes atomic per-priority pending work tokens, total tokens, rescheduled-work counts, next rescheduled times under a mutex, next submission IDs, expvar metrics, and scheduling accumulator state inside the goroutine.

Dependencies are context, expvar, runtime, math, atomics, sync, time, strconv, strings, and zap logging. Integration points are BeeRemote/worker managers that add/remove work tokens and consume priority token batches.

Risks: global expvar registration uses first scheduler's node name only. Submission ID functions assume non-empty 13-character base-36 keys. Token distribution fairness depends on callers completing full `getNextPriorityFunc` cycles. Negative counters are possible if remove calls are unbalanced.

Test signals: scheduler tests cover submission ID mapping, priority rotation, and distribution benchmarks, but not ticker behavior or reschedule timing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/scheduler/scheduler.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/scheduler/scheduler_test.go -->
# sources/distributed-fs/beegfs-go/common/scheduler/scheduler_test.go

Purpose: validates scheduler submission-ID priority encoding/decoding and priority rotation, and benchmarks token distribution.

Important types/tests are `submissionExpectation`, `TestSubmissionIDFunctions`, `TestGetNextPriority`, `BenchmarkDistributeTokensEvenWork`, and `BenchmarkDistributeTokensUnevenWork`.

Control flow: submission tests create IDs from base keys and priorities, decode priority and base key, increment IDs, demote and promote priorities, and verify expected boundaries including max uint64 base-36 rollover. `TestGetNextPriority` confirms rotating cycles start at each priority and each priority appears five times across nested cycles. Benchmarks initialize work-token counters and repeatedly call the distributor for even and skewed queue shapes.

State behavior under test is in-memory ID strings, priority counters, and atomic work token counters. No scheduler goroutine is started in benchmarks; they instantiate `Scheduler{log: zap.NewNop()}` directly.

Dependencies include `testing`, `fmt`, `testify/assert`, and zap.

Integration points are scheduler ID contracts used by queue storage and priority token release.

Risks: tests do not cover `NewScheduler` ticker behavior, moving-average calculations, expvar registration, rescheduled work timing, or invalid malformed submission IDs. Benchmarks exercise performance but do not assert fairness ratios.

Test signals: strong coverage for stable ID encoding contracts, which are critical for persisted queue ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/scheduler/scheduler_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/strfmt/strfmt.go -->
# sources/distributed-fs/beegfs-go/common/strfmt/strfmt.go

Purpose: package-level string formatting helpers used for human-readable BeeGFS Go output.

Important API is `CapitalizeFirst(s string) string`. It decodes the first UTF-8 rune, uppercases it with Unicode rules, and appends the untouched remainder.

Control flow is minimal: empty strings return unchanged; non-empty strings use `utf8.DecodeRuneInString` and `unicode.ToUpper`.

State and persistence: none. Dependencies are `unicode` and `unicode/utf8`.

Integration points are output formatting code that wants capitalization without assuming ASCII-only input.

Risks: invalid UTF-8 decodes to `utf8.RuneError` and will be uppercased/re-emitted, which may change the byte sequence. Only the first rune is capitalized; locale-specific casing is not handled beyond Go's Unicode tables.

Test signals: no direct tests for `CapitalizeFirst` in this subset. The time formatting functions in the same package have tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/strfmt/strfmt.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/strfmt/time.go -->
# sources/distributed-fs/beegfs-go/common/strfmt/time.go

Purpose: formats durations around expiration deadlines into concise human-readable strings.

Important APIs are `ExpirationString(remaining time.Duration)` and `RoundToHoursOrDays(d time.Duration)`.

Control flow: `ExpirationString` treats positive durations under an hour as "expires in less than an hour", positive longer durations as rounded hours/days, zero or negative durations within the last hour as "expired less than an hour ago", and older expirations as rounded elapsed hours/days. `RoundToHoursOrDays` switches to days at `>=24h`, rounds to the nearest day or hour, and pluralizes units.

State and persistence: none. Dependencies are `fmt` and `time`.

Integration points are license, certificate, or status messages that need consistent expiry text.

Risks: rounding can produce "24 hours" for just under a day and "1 day" at exactly a day, which is intentional but can surprise consumers expecting floor behavior. Negative durations should be passed to `ExpirationString`, not `RoundToHoursOrDays` directly.

Test signals: `time_test.go` covers positive and negative thresholds, pluralization, and hour/day rounding boundaries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/strfmt/time.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/strfmt/time_test.go -->
# sources/distributed-fs/beegfs-go/common/strfmt/time_test.go

Purpose: verifies expiration string formatting across hour/day boundaries and expired/not-expired cases.

Important test is `TestExpirationString`, which calls `ExpirationString` with durations from minutes to a year.

Control flow is direct assertions. Positive cases cover 365 days, 364 days, exactly 24 hours, just under 24 hours, 119/90/89/60/59 minutes. Expired cases cover zero, just under an hour ago, exactly and just over an hour ago, 90 minutes, just under a day, and exactly a day.

State and persistence: none. Dependencies are `testing`, `time`, and `testify/assert`.

Integration point is the public formatting contract in `time.go`.

Risks: tests do not call `RoundToHoursOrDays` directly, but cover it through `ExpirationString`. They do not exercise durations that round from 36 hours to 2 days, very large durations, or negative input to `RoundToHoursOrDays`.

Test signals: good threshold coverage for the user-facing messages most likely to regress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/strfmt/time_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/types/errors.go -->
# sources/distributed-fs/beegfs-go/common/types/errors.go

Purpose: defines `MultiError`, a small aggregate error type for combining independent operation failures.

Important APIs are `MultiError.Errors`, `(*MultiError).Error`, and `(*MultiError).Unwrap() []error`.

Control flow: `Error` iterates over contained errors, collects each `err.Error()` string, and joins them with `"; "`. `Unwrap` returns the underlying slice to support Go 1.20 multi-error unwrapping semantics for `errors.Is` and `errors.As`.

State is the exported `Errors []error` field. There is no persistence.

Dependencies are only `strings`.

Integration points are callers that need to return multiple failures while preserving sentinel matching. The file comment warns that `errors.Is` or `errors.As` will match any contained chain, not a specific operation.

Risks: nil entries in `Errors` would panic in `Error`. The exported slice can be mutated by callers after construction. There is no formatting that includes operation labels, so context must be embedded in each child error.

Test signals: no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/types/errors.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/types/types.go -->
# sources/distributed-fs/beegfs-go/common/types/types.go

Purpose: package documentation stub for `common/types`.

Important API surface in this file is only the package declaration and comment stating that the package provides custom types, notably errors.

Control flow, state, persistence, and dependencies are absent.

Integration points are package-level documentation and Go doc output for the adjacent `MultiError` implementation in `errors.go`.

Risks: the comment is sparse and may become stale if the package grows beyond errors. No code behavior can regress from this file alone.

Test signals: no tests are needed for this doc-only file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/common/types/types.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/cmd/beegfs/main.go -->
# sources/distributed-fs/beegfs-go/ctl/cmd/beegfs/main.go

Purpose: entry point for the `beegfs` CTL binary, including panic traceback handling for setuid/setgid packaging scenarios.

Important API is `main`. It imports `net/http/pprof` for side-effect registration and delegates execution to `ctl/internal/cmd.Execute`.

Control flow: if effective UID is root, it resets Go traceback mode to `single` to counter secure-mode suppression from setgid packaging. If effective UID/GID differs from real UID/GID and the process is not root, it installs a deferred recover handler that prints a warning-style panic message noting stack traces may be suppressed. Finally it exits with the command execution status.

State and persistence: it mutates runtime debug traceback state and may write to stderr on recovered panic. It does not persist files.

Dependencies are `os`, `fmt`, `runtime/debug`, pprof side effects, and the root CTL command package.

Integration points are packaged binary permissions, Go runtime secure mode, pprof registration, and cobra command execution.

Risks: recover catches only panics on the main goroutine. Importing pprof registers handlers only if an HTTP server is started elsewhere. The root check changes traceback behavior globally for the process.

Test signals: no direct tests for main; behavior is mostly integration/runtime-environment dependent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/cmd/beegfs/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/internal/bflag/flags.go -->
# sources/distributed-fs/beegfs-go/ctl/internal/bflag/flags.go

Purpose: wraps cobra/pflag options so CTL commands can expose user-friendly flags and translate them into arguments for external BeeGFS command-line tools.

Important APIs/types are `FlagSet`, `NewFlagSet`, `WrappedArgs`, `FlagWrapper`, `baseFlag`, generic `Flag[T]`, `WithEquals`, concrete `stringFlag`, `intFlag`, `boolFlag`, `GlobalFlag`, and `globalFlag`.

Control flow: `NewFlagSet` binds each wrapper to a cobra command. `WrappedArgs` asks each wrapper for target CLI arguments and concatenates non-nil results. Generic `Flag` switches on default value type to create a string/int/bool wrapper. String flags are omitted when empty, int flags are always emitted, bool flags emit only their wrapped flag when true, and `WithEquals` emits `--flag=value` for string/int wrappers. `GlobalFlag` reads values from viper instead of binding a local pflag.

State is each wrapper's pointer to the bound pflag value and static target flag metadata. Global flags read process-wide viper state.

Dependencies include cobra, viper, strconv, and fmt. Integration points are CTL commands that shell out to legacy BeeGFS utilities.

Risks: int flags are always included, so defaults must match target tool expectations. Global bool handling relies on viper type. Generic support is limited to string/int/bool and panics if expanded incorrectly. There are no quoting semantics beyond returning arg slices.

Test signals: no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/internal/bflag/flags.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/internal/cmd/benchmark/benchmark.go -->
# sources/distributed-fs/beegfs-go/ctl/internal/cmd/benchmark/benchmark.go

Purpose: implements the `beegfs benchmark` command family for starting, stopping, cleaning up, watching, waiting for, and reporting storage target benchmarks.

Important APIs/types are `frontendCfg`, `NewBenchmarkCmd`, subcommand builders, `storageBenchDispatcher`, `hasActiveBenchmark`, `hasBenchmarkError`, `refreshScreenAndPrintResults`, output table functions, `normalizeStorageBenchResults`, `benchStatusResults`, and `benchPerfResults`.

Control flow: the root command defines node/target filters, wait/watch refresh interval, unadorned table mode, and verbose output. Subcommands set `benchmark.StorageBenchConfig.Action` and related backend fields, then call `storageBenchDispatcher`. The dispatcher executes backend action once, optionally switches to status polling for wait/watch, refreshes terminal output, stops when no active benchmark remains, and emits a terminal alert. Status printing renders overall status, optional per-node errors/debug details, summary metrics, and verbose target rows.

State is split between frontend display options and backend benchmark config. Backend execution occurs through `ctl/pkg/ctl/benchmark.ExecuteStorageBenchAction`; this file does not persist benchmark files itself but commands can cause storage nodes to create/delete benchmark data.

Dependencies include cobra/pflag/viper, go-pretty tables/text, unit conversion, BeeGFS benchmark enums/entities, CTL config flags, terminal utilities, and backend benchmark package.

Integration points are storage node benchmark RPCs/ioctls via backend package, terminal refresh, global raw/debug config, and entity ID pflags.

Risks: parent flag sets are added to multiple subcommands, which must remain compatible with cobra behavior. Status without filters can aggregate unrelated benchmark runs and warns users. Mixed read/write results refuse summary. Throughput conversion assumes backend values are KiB/s. Wait/watch with zero interval can create an invalid ticker if validation is not elsewhere enforced.

Test signals: `benchmark_test.go` covers performance summary aggregation. Command dispatch and terminal rendering are otherwise untested.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/internal/cmd/benchmark/benchmark.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/internal/cmd/benchmark/benchmark_test.go -->
# sources/distributed-fs/beegfs-go/ctl/internal/cmd/benchmark/benchmark_test.go

Purpose: tests aggregation logic for benchmark performance summaries.

Important test is `TestStorageBenchSummary`, which appends five target throughput observations from two nodes to `benchPerfResults`.

Control flow: the test appends throughput values including zero and a high maximum, calls `summarize`, and asserts slowest target/node, fastest target/node, average throughput, and aggregate throughput.

State behavior under test is the incremental `benchPerfResults.summary`, `initializedFastest`, `initializedSlowest`, and target count behavior. Persistence and backend benchmark execution are not involved.

Dependencies are `testing`, `testify/assert`, and common BeeGFS entity ID types.

Integration point is `printResultsSummary`, which relies on `benchPerfResults` to compute rows for CLI output.

Risks: this test does not cover table rendering, unit normalization, mixed benchmark-type handling, no-results handling, verbose sorting, status summaries, or command flags. It also does not test overflow/large throughput values.

Test signals: useful focused coverage for min/max/average/aggregate math, including zero throughput as a valid slowest result.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/internal/cmd/benchmark/benchmark_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/internal/cmd/buddygroup/buddygroup.go -->
# sources/distributed-fs/beegfs-go/ctl/internal/cmd/buddygroup/buddygroup.go

Purpose: defines the top-level `beegfs mirror` command for mirroring and buddy group management.

Important API is `NewCmd() *cobra.Command`. It creates a cobra command with `Use: "mirror"`, short and long descriptions, no positional arguments, and attaches subcommands.

Control flow: construction is declarative. It calls `cmd.AddCommand` with list, create, automatic create, set-alias, delete, mirror-root-inode, and resync command groups. Actual behavior lives in sibling files and the `resync` subpackage.

State and persistence: this file creates no persistent state directly. Subcommands may query or mutate BeeGFS buddy groups and mirroring configuration.

Dependencies are cobra and `ctl/internal/cmd/buddygroup/resync`.

Integration points are the CTL command tree and all buddy-group subcommands. The user-facing command name is `mirror`, not `buddygroup`, which is important for documentation and compatibility.

Risks: this file is only an aggregator, so missing an added subcommand here would hide functionality. `Args: cobra.NoArgs` applies to the top-level command but subcommands define their own args.

Test signals: no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-go/ctl/internal/cmd/buddygroup/buddygroup.go -->
