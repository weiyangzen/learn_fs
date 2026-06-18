# subset-b-009586 Research

Grouped research for `subset-b-009586`. Each section preserves the source path in its title and is wrapped with deterministic markers for source-tree-aligned splitting into the mapped per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/gcsx/syncer_test.go -->
## sources/user-network-fs/gcsfuse/internal/gcsx/syncer_test.go

### Purpose
`syncer_test.go` verifies the `gcsx.Syncer` upload-decision logic and the `fullObjectCreator` request construction used when local file contents must be materialized back to GCS. It is a behavioral spec for when gcsfuse can append to an object versus when it must perform a full object rewrite.

### Important APIs, Types, And Functions
The file defines `FullObjectCreatorTest`, `fakeObjectCreator`, and `SyncerTest`. `FullObjectCreatorTest.call` drives `objectCreator.Create` through `fullObjectCreator`; `SyncerTest.call` drives `syncer.SyncObject`. `fakeObjectCreator.Create` records `srcObject`, `mtime`, and streamed contents, and returns canned object/error outcomes. Constants include `srcObjectContents`, `appendThreshold`, `chunkRetryDeadlineSecs`, and `chunkTransferTimeoutSecs`.

### Control Flow
The full-object tests expect `CreateObject` to receive generation precondition zero, the uploaded stream, object attributes copied from the source object, metadata merged with `gcsfuse_mtime` when mtime is supplied, and empty properties when source object is nil. Syncer tests set up a fake bucket object and a `TempFile`, mutate the temp file, and assert that `SyncObject` either returns early, calls the full creator, or calls the append creator. Branches cover missing source object, unfinalized source objects, truncation, dirty writes inside the source range, append-eligible growth, source too short for configured append threshold, and component-count exhaustion.

### State, Persistence, And Dependencies
State is in test fixtures: fake bucket contents, simulated clock, temp file dirty metadata, and fake creator call records. The suite depends on `internal/storage/fake`, `internal/storage/gcs`, `timeutil.SimulatedClock`, ogletest/oglemock matchers, and the unlisted production syncer implementation.

### Integration Points
The tests connect `TempFile.Stat().DirtyThreshold`, source object size/finalized/component metadata, and GCS precondition errors to the syncer upload path. They also validate that wrapped GCS errors preserving `*gcs.PreconditionError` still remain detectable with `errors.As`, which is important for upper layers that invalidate cached metadata on stale generations.

### Risks
The sync decision is sensitive to stale size for unfinalized objects, dirty threshold semantics after truncation, and the maximum compose component count. A regression can either reupload unnecessarily or, worse, append to an object whose prefix no longer matches the local file. The tests also encode a special case where unmodified nonzero unfinalized objects return early, while modified unfinalized objects bypass normal dirty-threshold early returns.

### Test Signals
Signals are strong for upload path selection, source object property copying, nil-source behavior, error wrapping, and unfinalized object handling. They do not exercise real GCS compose/append persistence, concurrent syncs, or large streams.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/gcsx/syncer_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/gcsx/temp_file.go -->
## sources/user-network-fs/gcsfuse/internal/gcsx/temp_file.go

### Purpose
`temp_file.go` implements `TempFile`, a lazy temporary-file wrapper around initial object contents. It tracks the earliest byte offset that differs from the original source so sync code can decide whether an object can be appended or must be fully rewritten.

### Important APIs, Types, And Functions
`TempFile` exposes invariant checks, `io.ReadSeeker`, `io.ReaderAt`, `io.WriterAt`, `Truncate`, `Name`, `Stat`, `SetMtime`, and `Destroy`. `StatResult` reports `Size`, `DirtyThreshold`, and optional `Mtime`. Constructors are `NewTempFile`, `NewCacheFile`, and `RecoverCacheFile`. Internal state uses `fileIncomplete`, `fileComplete`, `fileDirty`, and `fileDestroyed`. Helpers include `ensure`, `ensureComplete`, and `minInt64`.

### Control Flow
New temp/cache files start incomplete with a source reader and an `os.File`; recovered cache files start complete with dirty threshold equal to file size. Reads, seeks, stats, writes, and truncates call `ensureComplete`, which copies source data into the backing file in at least 64 MiB chunks until EOF. EOF closes the source, marks the file complete, and sets `dirtyThreshold` to the copied size. Writes and truncates lower the dirty threshold to the write offset or truncation size, mark the file dirty, and set mtime from the injected clock. `Stat` seeks to end for size, so callers are warned that it may invalidate seek position.

### State, Persistence, And Dependencies
Persistent state is the backing anonymous/cache file and in-memory fields for state, dirty threshold, source reader, and mtime. `Destroy` closes and nils the file for anonymous cleanup. Dependencies include `fsutil.AnonymousFile`, `timeutil.Clock`, `os.File`, and standard I/O primitives.

### Integration Points
The syncer and file-cache paths use `TempFile.Stat()` to detect unchanged prefixes and mtimes. `Name` exposes the backing file path for cache-oriented callers. `RecoverCacheFile` integrates already existing cache files by treating them as fully loaded clean content.

### Risks
The type is explicitly not concurrency-safe. `ensure` ignores the `Seek` error in the incomplete branch, so a failing seek can leave `size` zero and return a later copy error or nil in unusual conditions. `SetMtime` does not change `dirtyThreshold` or `state`, allowing mtime-only updates. Because `Stat` changes the seek offset, callers must preserve position if needed.

### Test Signals
Existing tests cover initial stat, reads, writes, truncation, explicit mtime, dirty threshold updates, invariant checks around operations, and simulated clock behavior. Gaps include cache-file recovery, destroy-after-use errors, huge lazy copy chunking, source read errors other than EOF, and concurrent misuse.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/gcsx/temp_file.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/gcsx/temp_file_test.go -->
## sources/user-network-fs/gcsfuse/internal/gcsx/temp_file_test.go

### Purpose
`temp_file_test.go` unit-tests the public `TempFile` contract from the external `gcsx_test` package, using a wrapper that calls `CheckInvariants` before and after each operation.

### Important APIs, Types, And Functions
Helpers include `readAll`, `dummyReadCloser`, and `checkingTempFile`. `TempFileTest` owns a context, simulated clock, and wrapped temp file. Tests are `Stat_InitialState`, `ReadAt`, `WriteAt`, `Truncate`, and `SetMtime`.

### Control Flow
Setup creates a `NewTempFile` with `initialContent`. Each test drives one operation and then checks stat fields and content. `checkingTempFile` invokes production invariants around read, seek, read-at, write-at, truncate, mtime, stat, and destroy, catching internal dirty-threshold/mtime violations during test execution.

### State, Persistence, And Dependencies
State is a temporary anonymous backing file populated from an in-memory string and a `timeutil.SimulatedClock` fixed to a known time. The test depends on ogletest/oglematchers and the production `gcsx.TempFile` interface.

### Integration Points
The tests provide direct confidence for syncer behavior because `DirtyThreshold`, file size, and mtime are what the syncer consumes. They also validate that the external package can interact with the interface rather than relying on unexported internals.

### Risks
Coverage is focused on short content and happy-path source reading. It does not validate `NewCacheFile`, `RecoverCacheFile`, lazy partial copy behavior, destroy semantics, source I/O errors, or large files. The wrapper assumes invariants should hold around operations but intentionally does not inspect private state.

### Test Signals
Signals verify that initial files are clean, reads do not dirty content, writes dirty from the write offset, truncation dirties at the new size, and explicit mtime sticks until a later modifying method.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/gcsx/temp_file_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/kernelparams/contract.go -->
## sources/user-network-fs/gcsfuse/internal/kernelparams/contract.go

### Purpose
`contract.go` defines the JSON schema shared between GCSFuse and the GKE GCSFuse CSI driver for zero-configuration kernel parameter handoff. Its comments explicitly classify JSON tag, field, type, and `ParamName` value changes as compatibility-sensitive.

### Important APIs, Types, And Functions
`ParamName` is a string enum with `MaxPagesLimit`, `TransparentHugePages`, `MaxReadAheadKb`, `MaxBackgroundRequests`, and `CongestionWindowThreshold`. `KernelParam` holds one name/value pair. `KernelParamsConfig` contains `RequestID`, `Timestamp`, and `Parameters`. `newKernelParamsConfig` creates a config with a UUID and RFC3339Nano timestamp.

### Control Flow
There is no complex runtime flow in this file. Construction is one shot: create a UUID string, format current time, and leave the parameter slice empty for `KernelParamsManager` to populate.

### State, Persistence, And Dependencies
The persistent contract is serialized JSON with stable tags `request_id`, `timestamp`, `parameters`, `name`, and `value`. Dependencies are `time` and `github.com/google/uuid`.

### Integration Points
`kernelparams.go` embeds this config in `KernelParamsManager`, writes it atomically for GKE environments, and applies it directly for non-GKE mounts. The CSI driver is an external consumer, so this file is an inter-process and cross-repository API boundary.

### Risks
The largest risk is backward-incompatible schema drift. Adding fields or constants is documented as safe, but changing existing JSON names or enum string values can break CSI driver parsing. Timestamp uses local `time.Now()` with RFC3339Nano, so consumers must accept nanosecond precision.

### Test Signals
Tests in `kernelparams_test.go` exercise serialized GKE output and parameter names indirectly. Contract-specific golden JSON or compatibility tests against CSI-side expectations would strengthen this boundary.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/kernelparams/contract.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/kernelparams/kernelparams.go -->
## sources/user-network-fs/gcsfuse/internal/kernelparams/kernelparams.go

### Purpose
`kernelparams.go` manages kernel parameter tuning for GCSFuse mounts. It can write the shared JSON contract for a privileged CSI driver in GKE, or directly mutate host procfs/sysfs values in non-GKE environments.

### Important APIs, Types, And Functions
`KernelParamsManager` embeds `*KernelParamsConfig` and guards it with a mutex. Public methods are `NewKernelParamsManager`, `PathForParam`, `ShouldUpdateMaxPagesLimit`, setter methods for each supported parameter, `ApplyGKE`, and `ApplyNonGKE`. Internal helpers are `readMaxPagesLimitFunc`, `getDeviceMajorMinor`, `atomicFileWrite`, `writeValue`, `applyDirectly`, and `addParam`.

### Control Flow
Setters validate positive/nonempty values and upsert parameters. `ApplyGKE` exits if there are no params, marshals the config, and atomically writes it. `ApplyNonGKE` resolves device major/minor from the mount point, maps each parameter to procfs/sysfs paths, then writes values directly or via non-interactive `sudo tee` on permission errors. `ShouldUpdateMaxPagesLimit` reads the current shared machine limit and only recommends increasing it.

### State, Persistence, And Dependencies
Manager state is in-memory until written. GKE persistence is an atomic JSON file in the caller-provided path. Non-GKE persistence is host kernel state under `/proc/sys/fs/fuse`, `/sys/class/bdi`, `/sys/fs/fuse/connections`, and `/sys/kernel/mm/transparent_hugepage`. Dependencies include `os`, `exec`, `encoding/json`, `syscall.Stat_t`, `x/sys/unix`, and the global logger.

### Integration Points
This package integrates with mount configuration and GKE sidecar/CSI flows. It is Linux-specific for direct application. The direct path depends on FUSE connection minor numbers and BDI major/minor derived from the mount point.

### Risks
Direct kernel writes are privileged and environment-sensitive; sudo fallback only works with passwordless sudo and may be inappropriate in unattended contexts. `writeValue` uses file mode `0644` for direct writes, although existing sysfs/procfs permissions usually dominate. Holding the manager mutex through file writes/sysfs mutations can block concurrent setter/apply calls. Machine-level `max_pages_limit` safety relies on successfully reading the existing value.

### Test Signals
Tests cover atomic writes, Linux major/minor extraction, path mapping, setter upserts, empty/no-op GKE application, direct write success/failure, sudo fallback behavior, and `ShouldUpdateMaxPagesLimit` branches. Real sysfs/FUSE connection mutation is not integration-tested.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/kernelparams/kernelparams.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/kernelparams/kernelparams_test.go -->
## sources/user-network-fs/gcsfuse/internal/kernelparams/kernelparams_test.go

### Purpose
`kernelparams_test.go` validates the kernel parameter manager's filesystem, serialization, mapping, and safety behaviors.

### Important APIs, Types, And Functions
Tests target `atomicFileWrite`, `getDeviceMajorMinor`, `PathForParam`, all `Set*` methods, `ApplyGKE`, `writeValue`, and `ShouldUpdateMaxPagesLimit`. The suite replaces `readMaxPagesLimitFunc` to test host-limit decisions deterministically.

### Control Flow
The tests create temp files/directories for atomic writes and direct writes, skip Linux-only checks on other OSes, verify path strings for all known `ParamName` values, write a JSON GKE file and unmarshal it, and simulate current max-pages limits through a function override.

### State, Persistence, And Dependencies
Persistent test state is limited to temp directories. Some tests interact with OS permissions and may attempt a sudo fallback when a read-only file triggers permission denial. Dependencies are `testing`, `assert`, `os`, `filepath`, `runtime`, and JSON decoding.

### Integration Points
The tests ensure the manager emits a CSI-driver-readable config and resolves sysfs/procfs paths consistently with production code. Linux skips keep the suite portable while still testing platform-specific paths when possible.

### Risks
`TestWriteValue_PermissionDenied_SudoFallback` is environment-dependent and can pass either via successful sudo or an expected sudo error. It does not assert no sudo is attempted in restricted CI beyond error content. Direct `ApplyNonGKE` is not exercised against real FUSE mount points.

### Test Signals
Signals are good for schema shape, setter validation, parameter replacement, no-op empty apply, path mapping, and max-pages safety logic. Missing signals include concurrent manager mutation and end-to-end CSI consumption.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/kernelparams/kernelparams_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/locker/locker.go -->
## sources/user-network-fs/gcsfuse/internal/locker/locker.go

### Purpose
`locker.go` provides a `sync.Locker` factory with optional invariant checking and deadlock debugging wrappers.

### Important APIs, Types, And Functions
Globals `EnableInvariantsCheck` and `EnableDebugMessages` enable wrappers before lockers are created. `Locker` aliases `sync.Locker`. `New` returns a base mutex optionally wrapped by `checker` and/or `debugger`. `checker.Lock/Unlock` call a supplied invariant function. `debugger.Lock/Unlock` track the holder stack and emit a delayed trace log after five seconds.

### Control Flow
`New` constructs a `sync.Mutex`, wraps it in `checker` if invariant checks are enabled, then wraps the result in `debugger` if debug messages are enabled. A debug lock captures the current goroutine stack after acquiring the mutex and starts a timer; unlock clears holder state, stops the timer, and unlocks the underlying locker.

### State, Persistence, And Dependencies
State is per-locker wrapper state plus package-level feature flags. There is no persistent storage. Dependencies include `runtime.Stack`, `time.AfterFunc`, `sync`, and the logger package.

### Integration Points
Internal packages can opt into invariant checks around lock-protected state and deadlock diagnostics globally. The logger dependency means debug output follows the global logging configuration and level.

### Risks
Feature flags are unsynchronized globals and are documented as needing to be set before creating lockers. `debugger` fields are not protected outside the lock lifecycle, and timer callbacks read `holder` asynchronously, so diagnostics are best-effort. `timer.Stop` return value is ignored, so a callback may already be running while unlock proceeds.

### Test Signals
No direct tests are in this shard. Useful tests would cover wrapper ordering, invariant invocation on lock/unlock, timer emission with a fake clock or short interval, and no panic when unlock races with timer execution.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/locker/locker.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/locker/rw_locker.go -->
## sources/user-network-fs/gcsfuse/internal/locker/rw_locker.go

### Purpose
`rw_locker.go` extends the locker factory pattern to read/write locks, adding optional invariant checks and writer-only deadlock diagnostics around `sync.RWMutex`.

### Important APIs, Types, And Functions
`RWLocker` embeds `sync.Locker` and adds `RLock`/`RUnlock`. `NewRW` builds a base `sync.RWMutex` and optionally wraps it in `rwChecker` and `rwDebugger`. `rwChecker` validates invariants after acquiring and before releasing both read and write locks. `rwDebugger` tracks only write locks with delayed trace logging.

### Control Flow
Construction mirrors `locker.New`. Write-lock acquisition captures a goroutine stack and starts a five-second timer after the lock is obtained; unlock clears and stops it. Read locks simply delegate in the debug wrapper, while the checker wrapper still invokes the invariant function for readers.

### State, Persistence, And Dependencies
State is in wrapper fields and global flags shared with `locker.go`. There is no persistent state. Dependencies are `sync`, `runtime`, `time`, and logger.

### Integration Points
Packages using read-mostly state can use `NewRW` to centralize invariant checks without changing call sites to direct `sync.RWMutex`.

### Risks
Read-lock deadlocks are intentionally not diagnosed. The same global flag and timer race caveats as `locker.go` apply. Running invariant checks while holding read locks may be expensive or may require the invariant function to avoid write-lock acquisition.

### Test Signals
No tests are present. Targeted tests should validate read/write invariant call counts, writer debug log behavior, and read-lock pass-through behavior under debug mode.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/locker/rw_locker.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/logger/legacy_logger.go -->
## sources/user-network-fs/gcsfuse/internal/logger/legacy_logger.go

### Purpose
`legacy_logger.go` bridges the package's `slog` logging system to the standard-library `log.Logger` API for dependencies that still require legacy loggers, especially `jacobsa/fuse`.

### Important APIs, Types, And Functions
The file exposes `NewLegacyLogger(level slog.Level, prefix, fsName string) *log.Logger`. It builds a handler from `defaultLoggerFactory`, adds mount attributes via `loggerAttr`, creates an `slog.NewLogLogger`, and resets the package logging level.

### Control Flow
When called, it creates a handler with the shared `programLevel` and prefix, attaches mount instance metadata, converts it to a legacy logger at the supplied slog level, then calls `setLoggingLevel(defaultLoggerFactory.level)` to keep global filtering aligned with current config.

### State, Persistence, And Dependencies
It reads and reuses global logger factory state and global mount ID behavior. There is no direct persistence. Dependencies are `log`, `log/slog`, and helpers from `logger.go`/`slog_helper.go`.

### Integration Points
This is a compatibility layer for third-party libraries that cannot yet accept `slog.Logger`. It preserves gcsfuse formatting, severity naming, prefixing, and mount-id attributes.

### Risks
Because it depends on global logger factory state, calls before logger initialization or during tests that mutate globals can affect output. The file is marked temporary, so new code should prefer native package logging functions.

### Test Signals
No direct legacy logger tests are present, but logger formatting tests indirectly cover the handler behavior it uses. A direct test would verify prefix, mount-id, and severity filtering through `log.Logger.Print`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/logger/legacy_logger.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/logger/logger.go -->
## sources/user-network-fs/gcsfuse/internal/logger/logger.go

### Purpose
`logger.go` centralizes gcsfuse logging configuration, global logger state, mount-instance IDs, severity-filtered formatted logging helpers, file/syslog output, and fatal exit behavior.

### Important APIs, Types, And Functions
Constants include `ProgramName`, `GCSFuseInBackgroundMode`, `MountUUIDEnvKey`, `MountIDKey`, and `mountUUIDLength`. Public functions include `InitLogFile`, `MountUUID`, `MountInstanceID`, `UpdateDefaultLogger`, `Tracef`, `Debugf`, `Infof`, `Info`, `Warnf`, `Errorf`, `Error`, `GetLogFHandler`, `Fatal`, and `SetOutput`. `loggerFactory` creates text or JSON handlers and chooses file, syslog, or stdout writers.

### Control Flow
Package init seeds a default stdout logger from default config. `InitLogFile` opens a configured file and creates a lumberjack rotator, or creates a syslog writer when running in background mode without a file path. It then creates a logger with mount-id attributes. Mount UUID is lazily initialized once: background mode reads `GCSFUSE_MOUNT_UUID`, foreground mode generates an eight-character UUID prefix. Logging helper functions manually check `programLevel` before emitting records. `Fatal` logs an error, logs a stack trace, then exits.

### State, Persistence, And Dependencies
Global mutable state includes `defaultLoggerFactory`, `defaultLogger`, `mountUUID`, `setupMountUUIDOnce`, and `programLevel`. Persistent outputs are log files via `lumberjack`, syslog, or stdout. Dependencies include `slog`, `syslog`, `debug.Stack`, `uuid`, config types, and lumberjack rotation.

### Integration Points
Most internal packages use these logging helpers. Monitoring, kernelparams, perf, profiler, and locker code all depend on it. Mount-id attributes tie logs from a running filesystem instance to metrics/tracing identifiers.

### Risks
Global state makes tests and concurrent reconfiguration order-sensitive. `InitLogFile` opens an `os.File` just to obtain a path for lumberjack and retains it, so callers/tests must close it if they care about descriptors. `Fatal` is hard process exit. Unsupported log levels in `setLoggingLevel` leave the previous level unchanged.

### Test Signals
`logger_test.go` verifies text/JSON formatting across levels, file logger initialization, runtime format update, UUID generation, background/foreground UUID setup, and `GetLogFHandler`. Tests do not cover syslog creation, fatal exit, log rotation behavior, or concurrent reconfiguration.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/logger/logger.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/logger/logger_test.go -->
## sources/user-network-fs/gcsfuse/internal/logger/logger_test.go

### Purpose
`logger_test.go` is the behavioral test suite for logger formatting, severity filtering, log-file configuration, mount UUID generation, and severity-to-function lookup.

### Important APIs, Types, And Functions
Helpers include `expectedLogRegex`, `redirectLogsToGivenBuffer`, `getTestLoggingFunctions`, `fetchAllLogLevelOutputsForSpecifiedSeverityLevel`, and `validateLogOutputs`. Tests cover text and JSON output at `OFF`, `ERROR`, `WARNING`, `INFO`, `DEBUG`, and `TRACE`; `setLoggingLevel`; `InitLogFile`; `UpdateDefaultLogger`; UUID generation/setup; and `GetLogFHandler`.

### Control Flow
Most format tests set `defaultLoggerFactory.format`, redirect output to a buffer with a prefix and mount-id attr, run each logging helper, and compare captured lines against regexes. UUID tests reset package globals with `t.Cleanup` and use environment variables for background mode. `GetLogFHandler` tests direct handlers and the fallback path for unsupported levels, expecting both a warning and a trace log.

### State, Persistence, And Dependencies
Tests mutate logger globals, `programLevel`, environment variables, and temp log files. They depend on `testify`, regex matching, and default config constants.

### Integration Points
The tests protect the log schema consumed by log collectors: text severity key, JSON timestamp object, `message` key, and `mount-id`. They also check the per-mount identity behavior used by metrics and operational debugging.

### Risks
Because global logger state is shared, tests must isolate state carefully; some subtests reset factory fields but not every global. Regexes assume timestamp lengths and mount UUID format. Syslog and rotation are not covered.

### Test Signals
Signals are comprehensive for level filtering and formatting of the main logging helpers. Additional value would come from testing `NewLegacyLogger`, syslog fallback, invalid severity strings, and file rotation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/logger/logger_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/logger/slog_helper.go -->
## sources/user-network-fs/gcsfuse/internal/logger/slog_helper.go

### Purpose
`slog_helper.go` adapts Go `slog` output to the gcsfuse log schema: custom severity names, custom message key, custom timestamp shape, optional prefixes, and package log-level filtering.

### Important APIs, Types, And Functions
It defines custom levels `LevelTrace` and `LevelOff` plus aliases for debug/info/warn/error. Internal helpers are `setLoggingLevel`, `customiseLevels`, `addPrefixToMessage`, `customiseTimeFormat`, and `getHandlerOptions`.

### Control Flow
`setLoggingLevel` maps config strings to `programLevel`. Handler options use `ReplaceAttr` to rename `level` to `severity`, convert custom level values to config strings, rename message to `message` while prepending a prefix, and convert time either to a formatted text string or to a JSON `timestamp` group with seconds and nanos.

### State, Persistence, And Dependencies
The file mutates the package-global `programLevel`. It persists only through emitted log records. Dependencies are `log/slog`, `strings`, `time`, and config constants.

### Integration Points
`loggerFactory` uses `getHandlerOptions` for both text and JSON handlers, and `NewLegacyLogger` reuses the same logic. This file defines the schema expected by tests and external logging systems such as FluentD.

### Risks
`customiseLevels`, `addPrefixToMessage`, and `customiseTimeFormat` type-assert attribute values; unexpected attribute shapes from future `slog` changes or custom records could panic. Unknown levels default to INFO label. Invalid config strings leave the previous `programLevel` unchanged.

### Test Signals
The logger tests validate the resulting schema, level names, timestamps, prefixes, and filtering. There are no direct unit tests for malformed attributes or invalid level strings.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/logger/slog_helper.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/monitor/bucket.go -->
## sources/user-network-fs/gcsfuse/internal/monitor/bucket.go

### Purpose
`bucket.go` wraps a `gcs.Bucket` to record GCS operation counts, operation latencies, reader lifecycle counts, and read-byte counts.

### Important APIs, Types, And Functions
Public functions are `NewMonitoringBucket` and `CaptureMultiRangeDownloaderMetrics`. Internal helpers include `recordRequest`, `setupReader`, `recordReader`, and `newMonitoringReadCloser`. `monitoringBucket` implements `gcs.Bucket`; `monitoringReadCloser` wraps `gcs.StorageReader`.

### Control Flow
Each bucket method records `startTime`, delegates to the wrapped bucket, then calls `recordRequest` with the appropriate `metrics.GcsMethod`. Successful reader creation wraps the storage reader so open count is incremented immediately, reads add bytes to `GcsReadBytesCount`, and close increments closed count after a successful close. Metadata-only methods such as `Name`, `BucketType`, and `GCSName` simply delegate.

### State, Persistence, And Dependencies
State is the wrapped bucket and a `metrics.MetricHandle`; metrics are exported through the metric subsystem rather than local storage. Dependencies include `internal/storage/gcs`, `metrics`, `time`, `context`, and Cloud Storage read handles.

### Integration Points
This wrapper composes with storage, caching, throttling, and monitoring setup. It instruments both object and folder APIs, including hierarchical namespace methods and multi-range downloader creation.

### Risks
Requests are counted regardless of success, which is intentional but should match dashboard semantics. A reader close error prevents the closed count from being incremented, potentially making open/close gauges diverge. Multi-range downloader byte-level reads are not wrapped here; only creation metrics are recorded unless external code calls `CaptureMultiRangeDownloaderMetrics`.

### Test Signals
No direct tests are in this shard. Valuable tests would use a fake metric handle to verify method labels, latency calls on error and success, reader byte counts, and close-error behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/monitor/bucket.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/monitor/otelexporters.go -->
## sources/user-network-fs/gcsfuse/internal/monitor/otelexporters.go

### Purpose
`otelexporters.go` configures OpenTelemetry metric export for gcsfuse, including Prometheus scraping, Google Cloud Monitoring export, metric filtering, resource attribution, and exporter shutdown joining.

### Important APIs, Types, And Functions
`SetupOTelMetricExporters` is the main entry point. Helpers include `dropDisallowedMetricsView`, `setupCloudMonitoring`, `metricFormatter`, `setupPrometheus`, `serveMetrics`, and `getResource`. `permissionAwareExporter` wraps an OTel metric exporter and disables itself after Cloud Monitoring permission-denied errors.

### Control Flow
Setup collects metric provider options from Prometheus and Cloud Monitoring configuration, attempts to detect/build a GCP resource with service name/version/instance ID, adds a view that drops disallowed metric prefixes, disables exemplars, creates and installs a global meter provider, and returns a joined shutdown function. Prometheus starts an HTTP server on `/metrics` and waits on a shutdown channel. Cloud Monitoring creates a periodic reader when interval seconds are positive.

### State, Persistence, And Dependencies
State includes the global OTel meter provider, the Prometheus server goroutines, and `permissionAwareExporter.disabled`. Persistent output is external: Prometheus HTTP endpoint and Cloud Monitoring custom metrics with prefix `custom.googleapis.com/gcsfuse/`. Dependencies include OTel SDK, GCP resource detector, Google Cloud metric exporter, Prometheus exporter/client, gRPC status codes, and common shutdown utilities.

### Integration Points
Metrics emitted by `metrics` package instruments and the monitoring bucket flow through this provider. Resource attributes connect metrics to mount ID and gcsfuse version.

### Risks
Global OTel provider replacement can affect tests or multiple mounts in one process. `setupPrometheus` uses an unbuffered shutdown channel; callers must invoke shutdown at most once. The metric filtering view silently drops instruments outside hard-coded prefixes. PermissionDenied disables Cloud Monitoring after the first such export, but the first call still returns the original error.

### Test Signals
`otelexporters_test.go` covers `permissionAwareExporter` success, PermissionDenied disable/skip, and non-permission error behavior. Prometheus serving, resource detection, metric prefix filtering, and Cloud Monitoring reader creation are not directly tested.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/monitor/otelexporters.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/monitor/otelexporters_test.go -->
## sources/user-network-fs/gcsfuse/internal/monitor/otelexporters_test.go

### Purpose
`otelexporters_test.go` validates the defensive wrapper around the Cloud Monitoring metric exporter.

### Important APIs, Types, And Functions
`mockExporter` implements `metric.Exporter` methods with an injectable `exportFunc`. Tests are `TestPermissionAwareExporter_ExportSuccess`, `TestPermissionAwareExporter_ExportPermissionDenied`, and `TestPermissionAwareExporter_ExportOtherError`.

### Control Flow
The success test exports once and expects no disabled state. The PermissionDenied test makes the first export return a gRPC PermissionDenied status, expects the wrapper to return that error and set `disabled`, then verifies the next export is skipped with nil error. The other-error test verifies generic errors do not disable the exporter.

### State, Persistence, And Dependencies
State is the wrapper's atomic disabled flag and mock export function. Dependencies are OTel metric data, gRPC status/codes, and testify assertions.

### Integration Points
These tests protect production behavior intended to avoid repeated noisy Cloud Monitoring failures when a mount lacks IAM permissions.

### Risks
The tests do not assert `ForceFlush` behavior when disabled or the log line emitted on first disable. They also do not check concurrent export races around `CompareAndSwap`.

### Test Signals
Signals are focused and good for the main permission-denied circuit-breaker behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/monitor/otelexporters_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/monitor/traceexporter.go -->
## sources/user-network-fs/gcsfuse/internal/monitor/traceexporter.go

### Purpose
`traceexporter.go` bootstraps OpenTelemetry tracing for gcsfuse using configured exporters, resource attribution, and sampling ratio.

### Important APIs, Types, And Functions
Public entry point `SetupTracing` calls `newTraceProvider`. `exporterFactory` abstracts exporter creation. Exporter helpers are `newStdoutTraceExporter` and `newGCPCloudTraceExporter`.

### Control Flow
`SetupTracing` creates a trace provider and installs it globally if creation succeeds. `newTraceProvider` maps configured exporter names `stdout` and `gcpexporter` to factories, adds each initialized exporter as a batcher, obtains the same resource shape used by metrics, applies a `TraceIDRatioBased` sampler, constructs a SDK tracer provider, and returns its shutdown function.

### State, Persistence, And Dependencies
State is the global OTel tracer provider and exporter batch processors. Output goes to stdout or Google Cloud Trace. Dependencies include OTel trace SDK, stdout trace exporter, GCP Cloud Trace exporter, config, common shutdown type, logger, and `getResource`.

### Integration Points
Tracing shares service name/version/mount ID resource identity with metrics. It depends on config-provided exporter names, GCP project ID, and sampling ratio.

### Risks
Unknown exporter names are silently ignored, which can hide configuration mistakes. Resource detection errors fail tracing setup. Multiple calls replace the global provider. Invalid sampling ratios are not validated in this file.

### Test Signals
No direct tests are present. Valuable tests would cover exporter selection, unknown names, GCP project option, resource failure, and sampler ratio propagation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/monitor/traceexporter.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/monitor/units.go -->
## sources/user-network-fs/gcsfuse/internal/monitor/units.go

### Purpose
`units.go` centralizes metric unit constants used by monitoring code.

### Important APIs, Types, And Functions
It exports `UnitDimensionless`, `UnitMicroseconds`, and `UnitBytes`. Dimensionless and bytes reuse OpenCensus unit constants; microseconds is a literal `"us"`.

### Control Flow
There is no runtime control flow.

### State, Persistence, And Dependencies
There is no state. The only dependency is `go.opencensus.io/stats`.

### Integration Points
Metric definitions can import these constants to avoid unit string drift across monitoring packages.

### Risks
The file mixes OpenCensus unit constants with OTel metric infrastructure elsewhere; migrations should preserve unit names consumed by dashboards.

### Test Signals
No tests are necessary beyond compile-time usage, though dashboard compatibility is the practical signal.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/monitor/units.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/mount/flag.go -->
## sources/user-network-fs/gcsfuse/internal/mount/flag.go

### Purpose
`flag.go` defines legacy mount flag defaults and a parser for comma-separated mount option strings.

### Important APIs, Types, And Functions
`ClientProtocol` has deprecated constants `HTTP1`, `HTTP2`, and `GRPC`, plus `IsValid`. Defaults include `DefaultStatOrTypeCacheTTL`, `DefaultStatCacheCapacity`, and `DefaultTypeCacheSizeMB`. `ParseOptions` populates a map from mount-style options.

### Control Flow
`IsValid` switches over the three known protocols. `ParseOptions` splits the input on commas, then splits each component at the first equals sign; options without `=` receive an empty value, and later duplicates overwrite earlier values.

### State, Persistence, And Dependencies
There is no persistent state. The caller-provided map is mutated. Dependencies are `strings` and `time`.

### Integration Points
This supports mount helpers and fstab-style option parsing. Deprecated protocol constants are retained for compatibility while newer code should use config package constants.

### Risks
There is intentionally no escaping or quoting, so commas cannot appear in names or values. Empty segments from leading/trailing/double commas produce empty-string keys. The parser does not trim whitespace.

### Test Signals
No tests in this shard. Useful tests would cover multiple equals signs, duplicate names, empty segments, whitespace, and protocol validation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/mount/flag.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/perf/cpu.go -->
## sources/user-network-fs/gcsfuse/internal/perf/cpu.go

### Purpose
`cpu.go` installs a signal-driven CPU profiling loop for operational debugging.

### Important APIs, Types, And Functions
`HandleCPUProfileSignals` creates a local `profileOnce(duration, path)` helper, registers for `SIGUSR1`, and writes profiles under `/tmp/cpu-<nanotime>.pprof`.

### Control Flow
On each SIGUSR1, it creates a timestamped profile file, starts `pprof.StartCPUProfile`, sleeps for 30 seconds, stops profiling, closes the file, and logs success or error. The signal loop runs forever.

### State, Persistence, And Dependencies
State is the process-wide CPU profiler and signal subscription. Persistent artifacts are pprof files in `/tmp`. Dependencies include `os/signal`, `syscall`, `runtime/pprof`, `time`, and logger.

### Integration Points
This is intended to be run in a goroutine by the main process so operators can trigger CPU profiles without restarting a mount.

### Risks
`StartCPUProfile` fails if another CPU profile is already active. The handler blocks for the profile duration per signal, so repeated signals queue in a size-one channel and may be dropped by signal semantics. Files are written to `/tmp` without cleanup.

### Test Signals
No tests are present, likely because signal/profiler globals are awkward. Manual signals and profile-file creation are the practical validation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/perf/cpu.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/perf/memory.go -->
## sources/user-network-fs/gcsfuse/internal/perf/memory.go

### Purpose
`memory.go` installs a signal-driven heap profile dump path for debugging memory usage.

### Important APIs, Types, And Functions
Constants define `KiB` and `MiB`. `HandleMemoryProfileSignals` creates `profileOnce(path)`, listens for `SIGUSR2`, logs current heap allocation, and writes `/tmp/mem-<nanotime>.pprof`.

### Control Flow
Each signal triggers `runtime.GC`, creates a profile file, writes the heap profile with `pprof.Lookup("heap").WriteTo`, reads current memory stats for logging, and reports success/failure. The loop runs indefinitely.

### State, Persistence, And Dependencies
State is process signal registration and runtime heap profiler state. Persistent artifacts are heap profile files in `/tmp`. Dependencies include `runtime`, `runtime/pprof`, `os/signal`, `syscall`, `time`, and logger.

### Integration Points
This complements CPU profiling and can be enabled by the main daemon for live mount diagnostics.

### Risks
Forcing GC changes process timing and memory behavior while profiling. Like CPU profiles, files accumulate in `/tmp`. The signal loop blocks while writing the profile.

### Test Signals
No direct tests. Validation is usually via sending SIGUSR2 and loading the generated pprof file.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/perf/memory.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/perms/perms.go -->
## sources/user-network-fs/gcsfuse/internal/perms/perms.go

### Purpose
`perms.go` provides a small system helper to obtain the current process UID and GID as unsigned IDs for filesystem ownership logic.

### Important APIs, Types, And Functions
The exported function is `MyUserAndGroup() (uid, gid uint32, err error)`.

### Control Flow
It calls `os.Getuid()` and `os.Getgid()`, checks for negative values, returns an error if either is negative, otherwise casts both to `uint32`.

### State, Persistence, And Dependencies
There is no mutable or persistent state. Dependency is standard `os` plus `fmt` for error construction.

### Integration Points
Mount and inode code can use this helper to default ownership to the current process identity.

### Risks
Negative UID/GID is mostly a non-Unix concern; on platforms where `os.Getuid` is unsupported or returns -1, callers must handle the error. Casting large signed IDs to uint32 assumes OS IDs fit the expected range.

### Test Signals
`perms_test.go` asserts the helper succeeds in the test environment and does not return uint32(-1). It does not simulate negative OS return values.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/perms/perms.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/perms/perms_test.go -->
## sources/user-network-fs/gcsfuse/internal/perms/perms_test.go

### Purpose
`perms_test.go` validates that current UID/GID lookup works in the test environment.

### Important APIs, Types, And Functions
The suite defines `PermsTest`, registers it through testify suite, and runs `MyUserAndGroupNoError`.

### Control Flow
The test calls `perms.MyUserAndGroup`, expects no error, and checks both returned IDs are not `uint32(-1)`.

### State, Persistence, And Dependencies
There is no persistent state. The test depends on the process environment and `testify`.

### Integration Points
This is a smoke test for filesystem ownership defaults on supported systems.

### Risks
The test cannot force the negative-ID error branch because `os.Getuid` and `os.Getgid` are not injectable. It also does not compare against expected IDs from the OS.

### Test Signals
Signal is limited but useful: the helper is callable and returns plausible IDs where the suite runs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/perms/perms_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/profiler/cloud_profiler.go -->
## sources/user-network-fs/gcsfuse/internal/profiler/cloud_profiler.go

### Purpose
`cloud_profiler.go` starts Google Cloud Profiler based on gcsfuse configuration.

### Important APIs, Types, And Functions
`SetupCloudProfiler` delegates to `setupCloudProfiler` with `cloudprofiler.Start`. `startFunctionType` makes the profiler start function injectable for tests.

### Control Flow
If `mpc.Enabled` is false, setup returns nil without side effects. Otherwise it builds `cloudprofiler.Config` from service name, label, and individual profiling booleans. Config booleans invert gcsfuse enable flags where the Cloud Profiler API uses `No*Profiling` fields. It forces GC for allocation profiling, calls the start function, and logs success.

### State, Persistence, And Dependencies
State is held by the Cloud Profiler library after start. Output is external profiler telemetry. Dependencies include Cloud Profiler, config types, logger, and Google API options.

### Integration Points
This is part of observability startup and ties profiler service/version labels to gcsfuse release/configuration.

### Risks
The function assumes a non-nil config pointer. Cloud Profiler start errors propagate and may affect mount startup depending on caller policy. No client options are currently passed despite the function type accepting them.

### Test Signals
Tests cover disabled no-op, enabled config mapping, and start failure propagation. They do not verify actual Cloud Profiler integration.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/profiler/cloud_profiler.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/profiler/cloud_profiler_test.go -->
## sources/user-network-fs/gcsfuse/internal/profiler/cloud_profiler_test.go

### Purpose
`cloud_profiler_test.go` verifies Cloud Profiler startup gating and config translation without contacting the real profiler service.

### Important APIs, Types, And Functions
Tests call the injectable `setupCloudProfiler` with mock start functions. Cases are disabled, enabled success, and enabled start failure.

### Control Flow
The disabled test ensures the mock start is not called. The success test captures `cloudprofiler.Config` and checks service, version, mutex, CPU, heap, allocated heap, goroutine, and `AllocForceGC` values. The failure test returns an error from the mock start and expects it to propagate.

### State, Persistence, And Dependencies
State is local mock variables. Dependencies are Cloud Profiler config types, gcsfuse config, Google API options, and testify.

### Integration Points
The tests protect the mapping between user-facing config flags and Cloud Profiler's inverse `No*Profiling` fields.

### Risks
They do not validate logging or real authentication/project behavior. Nil config is not tested.

### Test Signals
Signals are good for the core decision and mapping logic.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/profiler/cloud_profiler_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/ratelimit/limiter_capacity.go -->
## sources/user-network-fs/gcsfuse/internal/ratelimit/limiter_capacity.go

### Purpose
`limiter_capacity.go` computes a token bucket burst capacity that bounds transient overrun within a chosen time window.

### Important APIs, Types, And Functions
The exported function is `ChooseLimiterCapacity(rateHz float64, window time.Duration) (uint64, error)`. It uses a constant `N = 50`, corresponding to about 2 percent overrun.

### Control Flow
The function rejects non-positive or infinite rates and non-positive windows. It converts the window to seconds, computes `floor(windowSeconds * rateHz / N)`, and errors if the result is less than one or cannot fit in `uint64`. Otherwise it returns the capacity.

### State, Persistence, And Dependencies
There is no state or persistence. Dependencies are `fmt`, `math`, and `time`.

### Integration Points
Throttle setup can use this helper to choose a burst size for `NewThrottle` so operation or byte rates remain close to configured limits over operational windows.

### Risks
Very low rates or very small windows cannot be represented with a useful token bucket capacity and return errors. NaN rates are not explicitly rejected; comparisons with NaN make the final capacity check fail with the token-bucket error rather than the illegal-rate error.

### Test Signals
Tests cover negative/zero rates, negative/zero windows, zero computed capacity, and a normal expected capacity. Infinite and NaN rates are not covered.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/ratelimit/limiter_capacity.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/ratelimit/limiter_capacity_test.go -->
## sources/user-network-fs/gcsfuse/internal/ratelimit/limiter_capacity_test.go

### Purpose
`limiter_capacity_test.go` validates rate/window input handling and capacity calculation.

### Important APIs, Types, And Functions
The testify suite `LimiterCapacityTest` exercises `ChooseLimiterCapacity`. Helpers validate less-than-or-equal-to-zero rate and window errors.

### Control Flow
Tests call the helper with invalid rates, invalid windows, an undersized rate/window combination that yields capacity zero, and a normal case where `20 Hz` over `10s` yields capacity `4`.

### State, Persistence, And Dependencies
No state is persisted. Dependencies are `testing`, `time`, `fmt`, and testify.

### Integration Points
The tests protect configuration validation before token bucket construction.

### Risks
The zero-capacity test uses `time.Duration(1)` nanosecond, so the expected error describes a tiny window. Boundary cases around `math.MaxUint64`, infinity, and NaN are missing.

### Test Signals
Signals are focused on deterministic mathematical behavior and user-facing error strings.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/ratelimit/limiter_capacity_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/ratelimit/throttle.go -->
## sources/user-network-fs/gcsfuse/internal/ratelimit/throttle.go

### Purpose
`throttle.go` defines a concurrency-safe throttling abstraction backed by `golang.org/x/time/rate.Limiter`.

### Important APIs, Types, And Functions
`Throttle` exposes `Capacity()` and `Wait(ctx, tokens)`. `NewThrottle(rateHz, capacity)` returns a `limiter` wrapper. `limiter.Capacity` returns burst size, and `limiter.Wait` delegates to `WaitN`.

### Control Flow
Callers construct a token bucket with a per-second rate and burst capacity. Each `Wait` request blocks until the requested number of tokens is available or the context is canceled. The interface requires callers to request no more than `Capacity`.

### State, Persistence, And Dependencies
State is inside `rate.Limiter`; it is safe for concurrent access. There is no persistence. Dependencies are `x/time/rate` and context.

### Integration Points
`throttled_reader.go` uses it for byte bandwidth, and `throttled_bucket.go` uses it for operation rate limiting.

### Risks
The implementation casts `uint64` tokens and capacity to `int`; extremely large capacities can overflow on 32-bit platforms or unrealistic configurations. The precondition `tokens <= capacity` is not enforced by the wrapper.

### Test Signals
`throttle_test.go` runs integration-style concurrent arrival simulations and checks throughput is close to min(arrival rate, limit rate).
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/ratelimit/throttle.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/ratelimit/throttle_reader_test.go -->
## sources/user-network-fs/gcsfuse/internal/ratelimit/throttle_reader_test.go

### Purpose
`throttle_reader_test.go` verifies that `ThrottledReader` gates reads through a throttle, respects throttle capacity, and preserves reader error/short-read semantics.

### Important APIs, Types, And Functions
It defines `funcReader`, `funcThrottle`, and `ThrottledReaderTest`. Tests cover throttle invocation, throttle errors, wrapped reader invocation, wrapped errors/EOF, full reads, short reads followed by second reads, and read-size clipping to throttle capacity.

### Control Flow
Setup creates a no-op throttle and wraps a function-backed reader. Each test replaces throttle or reader callbacks, calls `Read`, and checks token counts, buffer slices, total bytes, and propagated errors.

### State, Persistence, And Dependencies
State is local function callbacks and context. Dependencies are `io`, `context`, and testify suite/assertions.

### Integration Points
The suite protects byte-rate limiting used by throttled GCS readers, especially when consumers ask for reads larger than the limiter burst.

### Risks
The tests do not cover context cancellation with the real `rate.Limiter`, zero-length reads, or readers that return `(0, nil)`, which could spin in the production loop.

### Test Signals
Signals are strong for capacity clipping, pre-read throttling, short-read refill behavior, and preserving EOF/non-EOF errors.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/ratelimit/throttle_reader_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/ratelimit/throttle_test.go -->
## sources/user-network-fs/gcsfuse/internal/ratelimit/throttle_test.go

### Purpose
`throttle_test.go` is an integration-style throughput test for the token-bucket throttle under concurrent simulated arrivals.

### Important APIs, Types, And Functions
Helpers include `makeSeed` and `processArrivals`. `ThrottleTest.TestIntegration` runs cases for one and four actors at arrival rates below, equal to, and above the configured limit.

### Control Flow
Each actor receives ticks at a steady per-actor arrival rate, randomly batches up to four packets, waits on the shared throttle, and accumulates processed packets until a one-second context deadline. The test compares total processed packets against the lesser of arrival and limit rates with 10 percent tolerance.

### State, Persistence, And Dependencies
State is goroutine-local random sources, tick channels, a shared throttle, and an atomic total counter. Dependencies include crypto randomness for seeding, math/rand, sync, atomics, runtime, and testify.

### Integration Points
This test validates that `ChooseLimiterCapacity` and `NewThrottle` work together for operation-rate limiting in realistic concurrent use.

### Risks
Timing-based tests can be flaky under slow or heavily loaded machines. Random batching improves realism but adds nondeterminism. The test does not explicitly cover cancellation errors or capacities above `int`.

### Test Signals
The main signal is end-to-end rate enforcement within tolerance across single and multi-goroutine workloads.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/ratelimit/throttle_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/ratelimit/throttled_bucket.go -->
## sources/user-network-fs/gcsfuse/internal/ratelimit/throttled_bucket.go

### Purpose
`throttled_bucket.go` wraps a `gcs.Bucket` to rate-limit GCS operations and object read bandwidth.

### Important APIs, Types, And Functions
`NewThrottledBucket(opThrottle, egressThrottle, wrapped)` returns a `gcs.Bucket`. `throttledBucket` implements bucket methods. `throttledGCSReader` combines a throttled `io.Reader` with the original `gcs.StorageReader` close/read-handle behavior.

### Control Flow
Most bucket methods call `opThrottle.Wait(ctx, 1)` before delegating to the wrapped bucket. `NewReaderWithReadHandle` additionally wraps successful readers with `ThrottledReader` using `egressThrottle`. `FinalizeUpload` and `FlushPendingWrites` intentionally skip op throttling to avoid risking data loss after a write has started. `NewMultiRangeDownloader` also delegates without throttling in this file.

### State, Persistence, And Dependencies
State consists of two throttles and the wrapped bucket. Persistent effects are the wrapped bucket's GCS operations. Dependencies include `internal/storage/gcs`, Cloud Storage read handles, `io`, and context.

### Integration Points
This wrapper composes around real, monitored, or cached buckets to enforce configured operation and bandwidth limits. It preserves folder, object, reader, and write APIs in the `gcs.Bucket` interface.

### Risks
Skipping throttling for finalize/flush is deliberate but means write-heavy traffic can still create unthrottled requests after writer creation. `NewMultiRangeDownloader` is not op-throttled or egress-throttled here, so multi-range paths require separate metrics/limits if desired. Read bandwidth throttling limits only calls through the returned reader.

### Test Signals
No direct throttled bucket tests are present in this shard. Reader-level throttling is covered by `throttle_reader_test.go`; operation-level bucket method coverage would require a fake bucket and fake throttle.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/ratelimit/throttled_bucket.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/ratelimit/throttled_reader.go -->
## sources/user-network-fs/gcsfuse/internal/ratelimit/throttled_reader.go

### Purpose
`throttled_reader.go` creates an `io.Reader` that limits read bandwidth by acquiring tokens before reading from an underlying reader.

### Important APIs, Types, And Functions
`ThrottledReader(ctx, r, throttle)` returns a `*throttledReader`. `throttledReader.Read` enforces capacity, waits for tokens, and loops until the requested slice is filled or the wrapped reader returns an error.

### Control Flow
For each read call, the buffer is clipped to `throttle.Capacity()` if larger. The reader waits for exactly the clipped length. It then repeatedly calls the wrapped reader, advancing the slice by bytes read, until all acquired bytes are served or an error such as EOF occurs.

### State, Persistence, And Dependencies
State is the context, wrapped reader, and throttle references. There is no persistence. Dependencies are `io` and context.

### Integration Points
`throttled_bucket.go` uses this for GCS reader egress limiting. It can also wrap any stream where bytes correspond to throttle tokens.

### Risks
If a wrapped reader returns `(0, nil)`, the loop can spin because `len(p)` does not decrease and `err` remains nil. The implementation charges for requested bytes, not bytes actually returned; short reads with EOF can consume more tokens than delivered. Zero-capacity throttles would clip every read to zero and wait for zero tokens.

### Test Signals
`throttle_reader_test.go` covers throttle invocation, capacity clipping, full reads, short reads, EOF, and error propagation. It does not cover `(0, nil)` or real-time rate behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/ratelimit/throttled_reader.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/storage/bucket_handle.go -->
## sources/user-network-fs/gcsfuse/internal/storage/bucket_handle.go

### Purpose
`bucket_handle.go` adapts the project-level `gcs.Bucket` interface to `cloud.google.com/go/storage` object APIs and Cloud Storage Control folder APIs.

### Important APIs, Types, And Functions
`bucketHandle` stores the Go storage bucket handle, bucket name/type, control client, billing project, and write config. Methods implement object reads, creates, chunk writers, appendable writer takeover, finalize/flush, copy, list, update, compose, delete, move, folder CRUD/rename, multi-range download, `Name`, `BucketType`, and `GCSName`. Helpers include `getObjectHandleWithPreconditionsSet`, `getProjectionValue`, and `isStorageConditionsNotEmpty`. Constants format HNS bucket/folder resource names.

### Control Flow
Reads configure range, generation, compressed mode, and optional read handle before calling `NewRangeReader`. Create paths set generation/metageneration preconditions, storage writer attributes, retry/transfer deadlines, progress callbacks, append/finalize behavior for rapid writes, then either copy content and close or return a writer. Appendable takeover requires a generation precondition and checks returned offset against requested offset, mapping mismatch to `gcs.PreconditionError`. List builds `storage.Query`, selects minimal attrs plus `Finalized` for rapid buckets, injects billing project metadata, iterates one page according to `MaxResults`, and separates object attrs from prefix/collapsed runs. Compose, copy, update, delete, and move map request preconditions into storage client conditions. Folder methods call Storage Control API resource names and convert control folders to `gcs.Folder`.

### State, Persistence, And Dependencies
Persistent effects are remote GCS object/folder mutations and uploaded object data. Local state includes bucket type, billing project, and write config. Almost every method defers `gcs.GetGCSError` to normalize storage errors. Dependencies include `cloud.google.com/go/storage`, Storage Control API, `gax`, `grpc/metadata`, config, `storageutil`, iterator, and `internal/storage/gcs`.

### Integration Points
This is the concrete storage backend behind caching, monitoring, throttling, and sync layers. It handles hierarchical namespace folders, rapid/zonal appendable-object semantics, gzip read behavior, read handles, generation preconditions, and billing-project propagation.

### Risks
This adapter is correctness-critical because mismapped preconditions can cause non-idempotent writes or stale data. `CreateAppendableObjectWriter` dereferences `GenerationPrecondition`, so callers must supply it. List pagination intentionally stops at current page when `MaxResults` is nonzero; fake-server behavior differs from real GCS for some prefix/max-result combinations. Multi-range downloader is not wrapped with throttling here. Folder rename waits on a long-running operation and can block until completion.

### Test Signals
`bucket_handle_test.go` extensively covers reads, generation handling, gzip compressed/decompressed reads, delete/stat/copy/create/write/finalize/flush, listing options, update, compose, bucket type detection, and HNS folder APIs using fake storage and mock control clients. Real GCS versioning and some fake-server unsupported precondition/listing behaviors remain gaps.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/storage/bucket_handle.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/storage/bucket_handle_test.go -->
## sources/user-network-fs/gcsfuse/internal/storage/bucket_handle_test.go

### Purpose
`bucket_handle_test.go` is the main behavioral test suite for the Cloud Storage-backed `bucketHandle` adapter.

### Important APIs, Types, And Functions
The suite defines `BucketHandleTest`, `createBucketHandle`, `minObjectsToMinObjectNames`, and `readObjectContent`. It uses `NewFakeStorageWithMockClient`, fake storage data constants, and a mocked Storage Control client. Tests cover reader methods, delete/stat/copy/create/update/compose/list/write/finalize/flush, bucket type detection, and hierarchical folder operations.

### Control Flow
Each test builds a bucket handle with a mocked storage layout, performs an operation through the `gcs.Bucket` contract, and asserts returned data or error type. Writer tests inspect `ObjectWriter` chunk size, object name, progress callback, append/finalize flags, and precondition behavior. Compose tests read source and destination contents to validate concatenation. Folder tests assert exact Storage Control requests for delete, get, rename, and create.

### State, Persistence, And Dependencies
State is a fake GCS server plus mock control client expectations. Some tests create objects or writers and then read back contents. Dependencies include Cloud Storage client types, Storage Control protos, gcsfuse config/storage abstractions, testify suite/mock, and gRPC status codes.

### Integration Points
The suite protects the adapter between internal `gcs` request structs and Google Cloud client calls. It also validates rapid/zonal bucket type flags derived from Storage Control layout responses.

### Risks
Several comments note fake storage limitations: generation/metageneration delete checks, object versioning, `IncludeFoldersAsPrefixes`, and real GCS pagination behavior are not fully modeled. Some compose/list expectations differ from real GCS, so these tests are strongest for adapter mapping and less complete for backend semantics.

### Test Signals
Signals are broad and high value: read ranges/generations/compression/read handles, not-found/precondition errors, writer attributes, finalize failure for existing object with generation zero, listing prefix/delimiter/max-result behavior, update metadata fields, compose edge cases, HNS bucket/folder calls, and bucket type defaults/errors.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/storage/bucket_handle_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/storage/caching/fast_stat_bucket.go -->
## sources/user-network-fs/gcsfuse/internal/storage/caching/fast_stat_bucket.go

### Purpose
`fast_stat_bucket.go` implements a caching `gcs.Bucket` wrapper for stat and folder metadata. It caches positive object/folder entries, negative misses, implicit directories, and listing-derived metadata while invalidating entries after mutations.

### Important APIs, Types, And Functions
`CacheMissError` marks cache-only lookup misses. `NewFastStatBucket` constructs `fastStatBucket`. Key helpers include `insertMultiple`, `insertListing`, `insertMultipleMinObjects`, `eraseEntriesWithGivenPrefix`, `insertHierarchicalListing`, `insert`, `insertMinObject`, `insertFolder`, negative-entry helpers, `invalidate`, `lookUp`, and `lookUpFolder`. Bucket methods wrap object, folder, list, stat, read, write, update, delete, move, and multi-range operations.

### Control Flow
Stat first panics on invalid requests for extended attrs without GCS fetch, then bypasses cache when forced, otherwise returns positive cache entries, converts negative entries to `NotFoundError`, optionally returns `CacheMissError`, or fetches from GCS and inserts results. Listings populate cache differently for hierarchical buckets, deprecated type-cache mode, and normal mode. Mutating operations invalidate affected names after wrapped calls, and insert new objects/folders on success. Deletes add negative entries on success and invalidate on precondition/not-found errors. Folder operations have parallel folder cache/negative-entry behavior. Context cancellation is checked after acquiring the mutex before inserting listing results to avoid stale cache updates.

### State, Persistence, And Dependencies
State is protected by `mu` and stored in `metadata.StatCache` with primary and negative TTLs based on an injected clock. Persistent remote state remains in the wrapped bucket. Dependencies include metadata cache, storageutil conversions, logger, `gcs` types, `timeutil.Clock`, context, and string suffix checks for directory markers.

### Integration Points
This wrapper sits between filesystem metadata lookups and the underlying bucket, reducing GCS stat calls. It integrates with HNS folder APIs, implicit directory behavior, appendable writer precondition cache invalidation, and force-fetch/fetch-only cache request flags.

### Risks
Cache coherency is the main risk. Incorrect invalidation after failed writes, stale listings after context cancellation, or wrong negative-entry TTLs can surface stale file/folder existence. `StatObject` panics for one invalid flag combination, so callers must respect request invariants. For hierarchical listings, zero-byte objects ending in `/` are excluded as folders while collapsed runs become folder entries; malformed prefixes only log errors.

### Test Signals
This shard does not include fast-stat tests, but the code has explicit paths that should be tested: positive/negative object and folder cache hits, fetch-only cache misses, force-fetch with extended attrs, listing insertion in HNS and implicit-dir modes, mutation invalidation, appendable takeover precondition invalidation, context-canceled listing suppression, and rename prefix erasure.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/storage/caching/fast_stat_bucket.go -->
