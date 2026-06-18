# subset-b-009152 research

Grouped research report for Kopia snapshot upload code and CLI/end-to-end tests. Each section preserves the exact source path and is wrapped for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/snapshot/upload/upload.go -->
# sources/sync-backup/kopia/snapshot/upload/upload.go

## Purpose
Implements Kopia's snapshot uploader for files and directories. It converts `fs.Entry` trees into `snapshot.Manifest` roots, writes file/symlink/directory objects through `repo.RepositoryWriter`, reuses cached objects from previous manifests, handles ignore rules and actions, records progress/statistics, and emits incomplete checkpoint snapshots during long uploads.

## Important APIs, Types, and Functions
`Uploader` is the main mutable coordinator. Public knobs include `Progress`, `MaxUploadBytes`, `ForceHashPercentage`, `ParallelUploads`, `EnableActions`, log-detail overrides, `FailFast`, `CheckpointInterval`, `DisableIgnoreRules`, and `CheckpointLabels`. `NewUploader`, `Upload`, `Cancel`, and `IsCanceled` are the public entry points. Core helpers include `uploadFileInternal`, `uploadFileData`, `uploadSymlinkInternal`, `uploadStreamingFileInternal`, `uploadDirInternal`, `processChildren`, `processDirectoryEntries`, `processSingle`, `checkpointRoot`, `periodicallyCheckpoint`, `wrapIgnorefs`, and cache helpers such as `findCachedEntry`, `metadataEquals`, and `newCachedDirEntry`. `dirReadError` preserves the distinction between root-directory read failure and child-entry failure.

## Control Flow
`Upload` starts tracing/logging/progress, validates checkpoint interval, creates a `workshare.Pool`, initializes a prototype manifest and atomic stats, then dispatches on source type. Directory uploads derive previous root directories from manifests, start background size estimation, wrap the root with `ignorefs`, execute root actions and optional OS snapshots, then call `uploadDirInternal`. `uploadDirInternal` registers a checkpoint callback, runs before/after-folder actions, handles shallow-placeholder directories, recursively processes children, writes a final directory manifest, and returns a summarized root entry. `processSingle` checks non-directory cache hits first, then handles directories, symlinks, files, `fs.ErrorEntry`, and streaming files. Regular files may be uploaded as one object or split into policy-sized parallel parts and concatenated with `repo.ConcatenateObjects`.

## State and Persistence Behavior
Persistent outputs are repository content/object blobs, directory manifests, final `snapshot.Manifest` data returned to callers, and periodic incomplete checkpoint manifests saved with `IncompleteReasonCheckpoint`. Cancellation and max-upload-byte limits set incomplete reasons rather than always failing the upload. `stats`, `totalWrittenBytes`, and cancellation flags are atomic because file work can run in parallel. Caching relies on previous snapshot entries with matching metadata and object IDs; `ForceHashPercentage` can probabilistically bypass cache. Failed entries are persisted in directory summaries via `AddFailedEntry`.

## Dependencies and Integration Points
Integrates `fs`, `ignorefs`, `snapshotfs`, `snapshot`, `policy`, `repo/object`, compression and splitter policies, OpenTelemetry tracing, content logging, `workshare`, `iocopy`, `timetrack`, OS snapshot helpers from sibling platform files, action hooks from `upload_actions.go`, progress from `upload_progress.go`, and estimation from `upload_estimator.go`.

## Risks
The code has several concurrency-sensitive areas: per-entry parallel processing updates a shared directory builder and atomic stats, file part closures capture loop indices, and checkpoints run concurrently with active writers. Error handling is policy-sensitive; root directory read failures abort while child directory failures can become fatal or ignored summary entries. Cached streaming files intentionally skip size comparison, so stable modtime/owner/mode are important. `ForceHashPercentage` uses global random state and creates nondeterministic cache behavior by design. Large-file part concatenation mutates the first part entry, so callers must not reuse part entries after concatenation.

## Test Signals
`upload_test.go` covers cache reuse, metadata compression, fail-fast and ignored error summaries, child policy on `fs.ErrorEntry`, progress callbacks, symlink stats, checkpoint manifests, parallel blob writes, large-file part concatenation, streaming files/directories, deduplication, and log-detail output. End-to-end snapshot/restore and checkpoint tests provide additional behavioral coverage.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/snapshot/upload/upload.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/snapshot/upload/upload_actions.go -->
# sources/sync-backup/kopia/snapshot/upload/upload_actions.go

## Purpose
Implements before/after snapshot and folder action execution for uploads. Actions let policy-defined commands or scripts run around source directories and optionally redirect the snapshot source path.

## Important APIs, Types, and Functions
`actionContext` carries `ActionsEnabled`, random `SnapshotID`, source/snapshot paths, and temporary `WorkDir`. `ensureInitialized` lazily creates the context. `envars` produces `KOPIA_ACTION`, `KOPIA_SNAPSHOT_ID`, `KOPIA_SOURCE_PATH`, `KOPIA_SNAPSHOT_PATH`, and `KOPIA_VERSION`. `prepareCommandForAction` converts a `policy.ActionCommand` into `exec.Cmd`. `runActionCommand` executes sync, async, or essential actions and captures stdout key/value output. `executeBeforeFolderAction`, `executeAfterFolderAction`, and `cleanupActionContext` are called by the uploader.

## Control Flow
A before action initializes context only for local paths and only when uploader actions are enabled. Script actions are materialized into the temporary work directory with `.sh` or `.cmd`; command actions use the configured binary and arguments. Sync actions collect stdout and parse requested captures. Essential action failures abort the before action; non-essential failures are logged. If before action emits `KOPIA_SNAPSHOT_PATH`, the uploader opens that local directory and snapshots it instead. After actions log failures but do not change upload results.

## State and Persistence Behavior
State is transient: a temporary working directory and any action subprocess side effects. The only uploader-visible state carried across before/after hooks is `actionContext`, especially snapshot ID and potentially overridden snapshot path. Cleanup removes the temp directory.

## Dependencies and Integration Points
Depends on `policy.ActionCommand`, `localfs.Directory`, `repo.BuildVersion`, OS runtime detection, and uploader logging. Called from root and nested directory upload paths in `upload.go`.

## Risks
Actions execute user-provided scripts/commands and inherit the process environment plus Kopia variables. Async mode starts without waiting, so cleanup of the work directory can race with long-running scripts. Captures use simple `key=value` parsing and ignore unknown keys. After-action errors are intentionally non-fatal, which can hide cleanup failures.

## Test Signals
Direct tests are not in this subset, but upload tests exercise action-enabled repository setup and OS snapshot disabling. Useful tests would cover script/command modes, timeout, essential versus non-essential failures, path override, Windows extension behavior, capture parsing, and temp cleanup.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/snapshot/upload/upload_actions.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/snapshot/upload/upload_estimator.go -->
# sources/sync-backup/kopia/snapshot/upload/upload_estimator.go

## Purpose
Provides background data-size estimation for directory uploads so progress UIs can show expected file count and total bytes before or while upload work proceeds.

## Important APIs, Types, and Functions
`EstimationDoneFn`, `EstimationStarter`, `EstimationController`, and `Estimator` define the small control surface. `NoOpEstimationController` handles disabled estimation. `NewEstimator` creates an `estimator` with `EstimationParameters`, logger, root directory, policy tree, wait group, cancel function, and injectable `VolumeSizeInfoFn`. `WithVolumeSizeInfoFn` supports tests. `StartEstimation`, `Cancel`, `Wait`, `doRoughEstimation`, and `doClassicEstimation` implement the logic.

## Control Flow
`StartEstimation` is idempotent once started. It launches one goroutine with a cancelable context. Rough and adaptive modes first call volume-size information; failures or adaptive file counts below threshold fall back to classic scanning. Classic mode calls `Estimate` with a `scanResults` collector. The callback is always invoked with the last computed values, including zeroes after cancellation/failure.

## State and Persistence Behavior
No persistent repository state is written. Internal state is the active cancel function and wait group. Estimation reads filesystem metadata and policy ignore rules. `Wait` clears `cancelCtx`; `Cancel` cancels and clears it if active.

## Dependencies and Integration Points
Uses `internal/volumesizeinfo` for rough estimates, `Estimate` from upload scanning code for classic estimates, and `logging` for debug/warn messages. `Uploader.startDataSizeEstimation` wires it to `Progress.EstimationParameters` and `Progress.EstimatedDataSize`.

## Risks
Rough estimation returns volume-wide used size and file count, which can overestimate a subtree. `Cancel` sets `cancelCtx` nil before the goroutine completes, so callers should still call `Wait`. Fallback behavior makes rough-estimation failures non-fatal, but it can perform an expensive full scan. Unsupported/unknown estimation type effectively returns zero values unless a caller constrains inputs.

## Test Signals
`upload_estimator_test.go` covers classic, rough, rough fallback, adaptive rough/classic paths, volume-info failure fallback, context cancellation, explicit cancel, and ignore policy filtering.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/snapshot/upload/upload_estimator.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/snapshot/upload/upload_estimator_test.go -->
# sources/sync-backup/kopia/snapshot/upload/upload_estimator_test.go

## Purpose
Tests estimator behavior independently of full uploads, especially selection between rough volume-size estimates and classic tree scans.

## Important APIs, Types, and Functions
Defines a zap-backed `mockLogger`, `withFailedVolumeSizeInfo`, `withVolumeSizeInfo`, and `expectSuccessfulEstimation`. The single `TestUploadEstimator` table of subtests builds `mockfs` directories and `upload.NewEstimator` instances.

## Control Flow
The helper starts estimation in a goroutine, waits for callback plus `Wait`, and fails after one second. Subtests cover classic scans, rough estimates with fake volume info, rough fallback on injected error, adaptive rough or classic selection based on threshold, cancellation via context during readdir, `Estimator.Cancel` during readdir, and ignore rules excluding `file1`.

## State and Persistence Behavior
All state is in-memory mock filesystem data. No repository is created. Cancellation is triggered by `mockfs` readdir hooks.

## Dependencies and Integration Points
Depends on `mockfs`, `volumesizeinfo`, `policy.BuildTree`, `upload.NewEstimator`, and `testify/require`. It validates that `scanResults` and policy ignore integration work through the public estimator API.

## Risks
The one-second timeout can be sensitive on overloaded test hosts, but the fixture is small. Rough tests rely on injected volume info rather than platform-specific volume APIs, which is good for determinism but does not test the real provider.

## Test Signals
Successful tests signal correct estimation counts/bytes, fallback to classic scanning, zero results on cancellation, and ignore-policy compliance.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/snapshot/upload/upload_estimator_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/snapshot/upload/upload_os_snapshot_nonwindows.go -->
# sources/sync-backup/kopia/snapshot/upload/upload_os_snapshot_nonwindows.go

## Purpose
Provides non-Windows stubs for OS filesystem snapshot support.

## Important APIs, Types, and Functions
`osSnapshotMode` always returns `policy.OSSnapshotNever`. `createOSSnapshot` returns a "not supported on this platform" error.

## Control Flow
Because mode is always `Never`, normal non-Windows uploads do not call `createOSSnapshot` through the OS snapshot branch. The error remains available if called directly.

## State and Persistence Behavior
No state or persistence.

## Dependencies and Integration Points
Selected by `//go:build !windows`. Paired with `upload_os_snapshot_windows.go` and called by `uploadDirWithCheckpointing`.

## Risks
Non-Windows policies requesting OS snapshots are effectively ignored because mode is forced to `Never`. This is intentional platform gating but means policy behavior differs by build target.

## Test Signals
Upload logging tests explicitly set VolumeShadowCopy to never for predictable behavior. Platform-specific Windows tests would be needed to cover the active implementation.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/snapshot/upload/upload_os_snapshot_nonwindows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/snapshot/upload/upload_os_snapshot_windows.go -->
# sources/sync-backup/kopia/snapshot/upload/upload_os_snapshot_windows.go

## Purpose
Implements Windows Volume Shadow Copy integration for snapshot uploads.

## Important APIs, Types, and Functions
`osSnapshotMode` reads `policy.OSSnapshotPolicy.VolumeShadowCopy.Enable`. `createOSSnapshot` validates local filesystem roots, detects existing shadow copies, creates a VSS snapshot with retry for "another operation in progress", opens the shadow-copy device path as `localfs.Directory`, and returns cleanup that removes the VSS snapshot.

## Control Flow
The uploader asks for mode, then calls `createOSSnapshot` for `Always` or `WhenAvailable`. Creation splits the local path into volume and relative path, creates or reuses a shadow copy, maps the original path into `sc.DeviceObject`, and defers removal unless setup failed.

## State and Persistence Behavior
Creates external OS VSS state and removes it in cleanup. Repository persistence is indirect: upload reads from the shadow-copy directory rather than the live path.

## Dependencies and Integration Points
Windows-only file using `github.com/mxk/go-vss`, `localfs`, `clock.SleepInterruptibly`, and uploader logging. Integrated by `uploadDirWithCheckpointing`.

## Risks
VSS creation/removal is external and can fail due to permissions, concurrent VSS operations, or non-local paths. Retry uses randomized delay. Cleanup logs but does not propagate removal failures. If `WhenAvailable` is configured, creation errors are downgraded by the caller.

## Test Signals
No direct tests in this subset. Practical coverage requires Windows integration tests for local paths, existing shadow copy paths, retryable VSS error 9, cancellation during retry, and cleanup failure logging.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/snapshot/upload/upload_os_snapshot_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/snapshot/upload/upload_progress.go -->
# sources/sync-backup/kopia/snapshot/upload/upload_progress.go

## Purpose
Defines upload progress callbacks and a counter-based implementation used by CLI/UI code.

## Important APIs, Types, and Functions
Constants define estimation modes: `classic`, `rough`, `adaptive`, and `AdaptiveEstimationThreshold`. `EstimationParameters` configures estimator choice. `Progress` is the uploader callback interface. `NullUploadProgress` is a no-op default. `Counters` captures current totals. `CountingUploadProgress` embeds `NullUploadProgress` and atomically tracks bytes/files/errors/exclusions plus mutex-protected current directory and last error. `Snapshot` and `UITaskCounters` expose state.

## Control Flow
Uploader calls `UploadStarted` and `UploadFinished` around each upload, emits hashing/cached/excluded/error/directory events during traversal, and emits estimated size from the estimator. The counting implementation resets on start, increments atomic counters in event methods, stores errors under lock, and builds UI counters with estimated values omitted in final mode.

## State and Persistence Behavior
No persistent state. Counters are in-memory and concurrency-safe for uploader parallelism. `UploadStarted` resets the struct, so callers should snapshot before starting a new upload.

## Dependencies and Integration Points
Used by `Uploader.Progress`, estimator settings, and `internal/uitask`. Tests access counters directly because they are in the same package.

## Risks
`Snapshot` omits `TotalExcludedFiles`, `TotalExcludedDirs`, and `TotalUploadedBytes`, while `UITaskCounters` includes them; consumers must choose the right API. `FinishedHashingFile` increments hashed file count even for failed hash attempts because uploader defers it after starting hash progress. `UploadedBytes` is only useful if lower layers call it; file copy reports `HashedBytes`.

## Test Signals
`upload_test.go` checks ignored progress is not double-counted, `FinishedFile` is invoked for success/error/cache paths, and log/UI-adjacent counters match upload outcomes.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/snapshot/upload/upload_progress.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/snapshot/upload/upload_scan.go -->
# sources/sync-backup/kopia/snapshot/upload/upload_scan.go

## Purpose
Adapts the upload estimator's scan progress callback into simple final file-count and byte totals.

## Important APIs, Types, and Functions
`scanResults` stores `numFiles` and `totalFileSize`. It implements `EstimateProgress` with no-op `Error` and `Processing`, and a `Stats` method that copies final `snapshot.Stats.TotalFileCount` and `TotalFileSize` using atomic loads.

## Control Flow
Classic estimation calls `Estimate` with `scanResults`. Intermediate stats are ignored; only `final == true` updates the totals used by `doClassicEstimation`.

## State and Persistence Behavior
In-memory only. It intentionally ignores scan errors in the progress callback; `Estimate` returns the actual terminal error.

## Dependencies and Integration Points
Depends on `snapshot.Stats` and the scanner's `EstimateProgress` contract. Used by `upload_estimator.go`.

## Risks
Only final stats are captured, so if `Estimate` changes to omit a final call on partial success the estimator returns zeroes. `numFiles` narrows from `int32` through `int`; this is acceptable on supported platforms but is a theoretical portability concern.

## Test Signals
Covered indirectly by classic estimator tests and ignore-policy estimator tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/snapshot/upload/upload_scan.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/snapshot/upload/upload_test.go -->
# sources/sync-backup/kopia/snapshot/upload/upload_test.go

## Purpose
Unit/integration tests for the snapshot upload package using real repository writers, mock filesystems, virtual filesystems, faulty blob storage, fake time, and captured logs.

## Important APIs, Types, and Functions
`uploadTestHarness` creates a filesystem-backed repository wrapped in faulty/logging storage and a populated `mockfs.Directory`. Helpers include `findAllEntries`, `verifyMetadataCompressor`, `verifyErrors`, `randomBytes`, `verifyFileContent`, `verifyContainsOffset`, `mockProgress`, `mockLogger`, `loggedAction`, and `verifyLogDetails`.

## Control Flow
Tests build repositories, run `NewUploader(...).Upload` under different policies and source trees, then inspect manifests, stats, repository content metadata, restored entries, blob call concurrency, and captured uploader logs. Some tests use fake ticker/checkpoint channels to deterministically trigger checkpointing, while large parallel tests use real temp files and are skipped unless suitable for CI/Linux AMD64.

## State and Persistence Behavior
Each harness initializes an on-disk Kopia repository and write session. Tests write snapshots, content blobs, directory manifests, checkpoint manifests, and sometimes flush repositories. Mock filesystem hooks inject readdir/open failures and cancellation points. Log tests install a context logger and force `ParallelUploads=1` for stable order.

## Dependencies and Integration Points
Touches most upload dependencies: `repo`, filesystem blob storage, content compression, snapshot manifests, policy trees, `snapshotfs`, `mockfs`, `virtualfs`, `localfs`, `workshare` behavior through uploader knobs, and blob fault instrumentation.

## Risks
Some tests are resource-heavy (`TestParallelUploadDedup`, `TestParallelUploadOfLargeFiles`) and gated. Parallel tests share package globals only through logging/time utilities, so order is mostly isolated. Logging assertions are intentionally strict and can fail on output schema changes. Random data tests depend on repository size heuristics.

## Test Signals
Coverage includes cache stability across snapshots, metadata compression headers, top-level versus child read failures, ignored/fatal error summaries, child error policy, progress callbacks for successes/errors/cache, symlink summaries, checkpoint retention labels, parallel upload concurrency, streaming files/directories, compression with streaming files, dedup of identical large files, large-file part concatenation offsets/content, and log-detail keys/messages.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/snapshot/upload/upload_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/clitestutil/clitestutil.go -->
# sources/sync-backup/kopia/tests/clitestutil/clitestutil.go

## Purpose
Provides parsing helpers for CLI end-to-end tests, primarily for `snapshot list -l --manifest-id` and `ls -l` output.

## Important APIs, Types, and Functions
`SourceInfo`, `SnapshotInfo`, and `DirEntry` are parsed representations. `MustParseSnapshots`, `mustParseSnapshotInfo`, `mustParseSourceInfo`, `ListSnapshotsAndExpectSuccess`, `ListDirectory`, and `ListDirectoryRecursive` are the main helpers. `testEnv` captures the `RunAndExpectSuccess` method needed from test environments.

## Control Flow
Snapshot parsing treats non-indented lines as `user@host:path` source headers and two-space-indented lines as snapshots. Snapshot lines are split by spaces, timestamp fields are joined and parsed, and manifest/object fields shift depending on whether the line contains `incomplete`. Directory parsing uses fixed fields from `ls -l`.

## State and Persistence Behavior
No persistent state; helpers fail tests directly through `testing.TB`.

## Dependencies and Integration Points
Used by many end-to-end tests in this subset for snapshot count, snapshot IDs, object IDs, and directory entry object IDs.

## Risks
Parsing is tightly coupled to CLI text column formats and timezone layout. Any display wording, spacing, or incomplete-marker change can break unrelated tests. `mustParseDirectoryEntries` assumes at least seven fields.

## Test Signals
Indirectly validated across ACL, all-format, compression, diff, ECC, index recovery, restore, repository sync, and checkpoint tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/clitestutil/clitestutil.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/compat_test/compat_test.go -->
# sources/sync-backup/kopia/tests/compat_test/compat_test.go

## Purpose
Black-box compatibility tests across historical Kopia binaries and the current binary.

## Important APIs, Types, and Functions
Global environment-derived binary paths are `KOPIA_CURRENT_EXE`, `KOPIA_08_EXE`, and `KOPIA_017_EXE`. Tests use `testenv.NewExeRunnerWithBinary` and `NewCLITest`.

## Control Flow
Tests create repositories or server configs with old/current binaries, switch runners, connect, list snapshots, perform upgrades, and assert expected success/failure. The v0.17 server test starts an old server, connects an old client, then switches that client config to the current binary.

## State and Persistence Behavior
Creates real filesystem repositories, client configs, format cache files, server TLS files, and server user records. Upgrade tests mutate repository format state and poison old-client access.

## Dependencies and Integration Points
Exercises CLI repo create/connect/status/upgrade, snapshot commands, server start/users, TLS fingerprint handling, old format cache refresh, and persisted client config compatibility.

## Risks
Tests skip when required binary env vars are absent, so coverage depends on CI setup. They rely on old executable behavior and text output stability. Time sleeps guard cache mtime checks and server startup.

## Test Signals
Signals include current opening v0.8 repos, v0.8 opening current format v1 repos, v0.8 rejection of default current/v2 repos, cache refresh throttling, upgrade lock behavior, and current client compatibility with v0.17 server config.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/compat_test/compat_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/end_to_end_test/acl_test.go -->
# sources/sync-backup/kopia/tests/end_to_end_test/acl_test.go

## Purpose
End-to-end server ACL test covering default ACL setup, rule overwrites, user visibility, append-only behavior, retention, and credential refresh.

## Important APIs, Types, and Functions
Single `TestACL` uses `testenv.NewInProcRunner`, `server acl`, `server users`, `policy set`, `server start`, `server refresh`, and `clitestutil.ListSnapshotsAndExpectSuccess`.

## Control Flow
The test creates a server repository, enables ACLs, modifies default snapshot access, adds per-user snapshot/policy rules, creates users, starts a TLS server, connects three clients, and verifies each user's snapshot visibility and permissions. It also changes a user's password, refreshes server auth cache with admin credentials, verifies refresh fails with non-admin credentials, and reconnects with the new password.

## State and Persistence Behavior
Persists ACL manifests, user records, policies, snapshots, retention effects, and server auth cache state in a real repository. Multiple client configs connect to the same server.

## Dependencies and Integration Points
Integrates auth defaults, server control API, repository ACL evaluation, retention policy, snapshot creation/list/delete, TLS startup, and CLI password handling.

## Risks
Long, stateful, and order-dependent. Failure messages sometimes mention the wrong user in `Fatalf` text, but assertions are clear. Retention behavior under append access is subtle: server-side maintenance can keep latest snapshots while client delete is denied.

## Test Signals
Confirms default ACL count, duplicate rule rejection without overwrite, scoped read/append/full access, cross-user snapshot visibility, retention enforcement for append users, delete denial, and auth cache refresh requirements.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/end_to_end_test/acl_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/end_to_end_test/all_formats_test.go -->
# sources/sync-backup/kopia/tests/end_to_end_test/all_formats_test.go

## Purpose
Smoke-tests repository creation, snapshotting, disconnect/reconnect, and snapshot listing across all supported encryption and hashing algorithms.

## Important APIs, Types, and Functions
`TestAllFormatsSmokeTest` iterates `encryption.SupportedAlgorithms(false)` and `hashing.SupportedAlgorithms()`, using `testdirtree.CreateDirectoryTree`, `repo create filesystem --block-hash --encryption`, `snap create`, and `clitestutil.ListSnapshotsAndExpectSuccess`.

## Control Flow
A shared small source tree is created once. Each encryption/hash subtest runs in parallel with a fresh CLI test repository, creates a snapshot, validates one source, reconnects, and validates the same source count again.

## State and Persistence Behavior
Creates many real filesystem repositories and one shared source tree. Repository format is not constrained beyond the algorithm flags.

## Dependencies and Integration Points
Exercises format initialization, cryptographic algorithm selection, content hashing, snapshot upload, and persisted config reconnect.

## Risks
The nested parallel matrix can be expensive. The test checks only basic usability, not restore correctness or algorithm-specific metadata.

## Test Signals
Failure indicates an algorithm combination cannot create, write, reconnect, or list snapshots.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/end_to_end_test/all_formats_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/end_to_end_test/api_server_repository_test.go -->
# sources/sync-backup/kopia/tests/end_to_end_test/api_server_repository_test.go

## Purpose
End-to-end API server repository tests for htpasswd/repository-user auth, transparent client reconnect after server restart, remote snapshot writes, JSON log upload, and GRPC manifest pagination.

## Important APIs, Types, and Functions
`TestAPIServerRepository_htpasswd`, `TestAPIServerRepository_RepositoryUsers`, `testAPIServerRepository`, `verifyServerJSONLogs`, `verifyFindManifestCount`, and `TestFindManifestsPaginationOverGRPC`. Uses `apiclient`, `serverapi`, `servertesting.ConnectAndOpenAPIServer`, `repo.Repository`, `repo.WriteSession`, and CLI server commands.

## Control Flow
The shared helper creates snapshots as multiple users, starts a TLS server with either htpasswd or repository users, opens a remote repo client, creates a write session, shuts the server down, restarts it on the same address/cert, validates read reconnection and broken write-stream behavior, connects a CLI client, creates remote snapshots, verifies server-side blob growth and snapshot counts, shuts down, verifies logs, and checks dead-server connection returns quickly. The GRPC test writes 10,000 large-label manifests and ensures paginated `FindManifests` returns all unique labels.

## State and Persistence Behavior
Creates repositories, user files or repository users, TLS cert/key files, server logs, manifests, blobs, and remote write sessions. Server restarts intentionally break existing streams while preserving repository state.

## Dependencies and Integration Points
Covers CLI server lifecycle, API/GRPC clients, auth, TLS fingerprints, repository remote protocol, manifest listing pagination, blob storage, snapshot upload, log upload, and control shutdown.

## Risks
Timing-sensitive startup/shutdown, large manifest volume, and dependency on reconnect behavior. The dead-server connection call is not checked for returned error in the source, only elapsed time, so it mainly guards retry duration.

## Test Signals
Signals include successful reconnect for read operations, failed stale write session after restart, correct snapshot visibility as `foo@bar`, remote writes producing server blobs, JSON logs containing client/server spans, quick failure to dead server, and complete GRPC pagination over large responses.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/end_to_end_test/api_server_repository_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/end_to_end_test/auto_update_test.go -->
# sources/sync-backup/kopia/tests/end_to_end_test/auto_update_test.go

## Purpose
Tests CLI auto-update check enablement, disablement, and initial delay configuration through flags and environment variables.

## Important APIs, Types, and Functions
`TestAutoUpdateEnableTest` table-drives create/connect flows. `absDuration` normalizes durations for approximate time comparison.

## Control Flow
For each case, the test creates a repository with optional flags/env, checks whether `.kopia.config.update-info.json` exists, disconnects and verifies removal, reconnects with the same options, and if enabled decodes `nextCheckTimestamp` to compare against `clock.Now()+wantInitialDelay`.

## State and Persistence Behavior
Creates and removes update-info JSON beside the client config. Environment map mutations are per test environment, and the process `KOPIA_CHECK_FOR_UPDATES` is unset before cases.

## Dependencies and Integration Points
Exercises CLI global update flags/env, repo create/connect/disconnect, config directory side effects, JSON state shape, and clock abstraction.

## Risks
Parallel cases compare wall-clock-ish times with a one-minute tolerance. The case names for flag/envar delay are slightly misleading in the source, but expected values are explicit.

## Test Signals
Confirms default enabled state, false-like env parsing, flag precedence over env, update-info cleanup on disconnect, and configured initial delay persistence.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/end_to_end_test/auto_update_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/end_to_end_test/compression_test.go -->
# sources/sync-backup/kopia/tests/end_to_end_test/compression_test.go

## Purpose
Format-specific end-to-end test that global compression policy applies to uploaded file data and that content can still be shown correctly.

## Important APIs, Types, and Functions
`formatSpecificTestSuite.TestCompression` and helper `containsLineStartingWith`.

## Control Flow
The test creates a repo, sets global compression to `pgzip`, writes a small compressible file, snapshots it, lists the directory to get the object ID, detects whether repository status reports content-level compression, then either checks object ID prefix or `content ls -c` compression metadata. Finally it runs `show` and compares the original lines.

## State and Persistence Behavior
Persists a global policy manifest, compressed content/object data, and one snapshot. Reads repository status and content metadata.

## Dependencies and Integration Points
Integrates policy CLI, upload compression policy, repository format differences, `ls`, `content ls`, and `show`.

## Risks
Output parsing depends on status and content-list text. The test is intentionally small and does not measure compression ratio.

## Test Signals
Confirms compression metadata/path differs correctly by format capability and decompression/show returns original content.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/end_to_end_test/compression_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/end_to_end_test/content_info_test.go -->
# sources/sync-backup/kopia/tests/end_to_end_test/content_info_test.go

## Purpose
Tests content listing, summaries, stats, and deleted-content visibility after explicit content deletion.

## Important APIs, Types, and Functions
`formatSpecificTestSuite.TestContentListAndStats` uses `snapshot.Manifest`, `content.Info`, and `containsLineStartingWith`.

## Control Flow
The test creates a repository, verifies deleted-only list is empty, sets compression, writes a compressible file, snapshots with JSON output, derives the root content ID, checks it appears in normal list modes and summary, runs stats, sleeps to separate timestamps, deletes the content, then verifies it disappears from normal list modes and appears in deleted list modes.

## State and Persistence Behavior
Creates content and a snapshot manifest, then writes deletion metadata for the content ID. Timestamp separation matters because create/delete in the same second can resolve unexpectedly.

## Dependencies and Integration Points
Exercises content CLI list/stats/delete, snapshot JSON output, object-to-content ID conversion, and compression metadata listing.

## Risks
Relies on textual `content list` prefixes and second-level timestamp behavior. Deleting the root content intentionally corrupts snapshot restoreability but is scoped to the test repo.

## Test Signals
Validates content visibility transitions between active and deleted lists plus long/compressed/summary listing modes.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/end_to_end_test/content_info_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/end_to_end_test/diff_test.go -->
# sources/sync-backup/kopia/tests/end_to_end_test/diff_test.go

## Purpose
End-to-end smoke test for `diff` across every pair of snapshots from a changing directory.

## Important APIs, Types, and Functions
`TestDiff` uses CLI repo/snapshot/diff commands and `clitestutil.ListSnapshotsAndExpectSuccess`.

## Control Flow
The test snapshots an empty directory, adds directories and files, snapshots again, modifies one file and adds another directory, snapshots, deletes a file, snapshots, then runs `diff -f` for every ordered pair of snapshot root object IDs.

## State and Persistence Behavior
Persists four snapshots for one source path and exercises file add/modify/delete state across roots.

## Dependencies and Integration Points
Covers snapshot upload, snapshot listing, object-root addressing, and diff output generation.

## Risks
The test asserts only command success, not diff content. It can miss semantic regressions that still exit zero.

## Test Signals
Any crash or error in pairwise diffing across empty, added, modified, and deleted tree states fails the test.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/end_to_end_test/diff_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/end_to_end_test/ecc_test.go -->
# sources/sync-backup/kopia/tests/end_to_end_test/ecc_test.go

## Purpose
Format-specific tests for error-correction-code overhead and recovery from one-byte corruption in repository blobs.

## Important APIs, Types, and Functions
`TestNoECC`, `TestECC`, `flipOneByteFromEachFile`, and `dirSize`.

## Control Flow
`TestNoECC` creates a flat repo without ECC, snapshots a 1 MiB deterministic file, and asserts repo size remains below about 1.1 MiB. `TestECC` creates a flat repo with 50 percent ECC overhead, snapshots the same data, checks v1 lacks ECC support or v2+ size grows, flips one byte in each repository file except format/shard files, then restores and compares data.

## State and Persistence Behavior
Mutates real repository blob bytes to simulate corruption. Restore should recover data when ECC is supported.

## Dependencies and Integration Points
Exercises repo format ECC settings, filesystem storage, snapshot upload, restore, and blob layout. Uses `clitestutil` to find snapshot IDs.

## Risks
Size thresholds are approximate and can be affected by format changes. Byte flipping uses random positions without deterministic seed and skips only known metadata files. The recovery check is limited to one file.

## Test Signals
Confirms ECC-disabled repositories do not incur large overhead, ECC-enabled repositories do, and corrupted blobs can still restore the original data for supported formats.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/end_to_end_test/ecc_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/end_to_end_test/index_optimize_test.go -->
# sources/sync-backup/kopia/tests/end_to_end_test/index_optimize_test.go

## Purpose
Tests index optimization compacts multiple index blobs into one and that flush-per-source creates separate indexes.

## Important APIs, Types, and Functions
`formatSpecificTestSuite.TestIndexOptimize`.

## Control Flow
The test creates a repo, skips if epoch manager is enabled, creates several snapshots to produce six indexes, runs `index optimize`, expects one index, then creates three sources with `--flush-per-source` and expects four indexes total.

## State and Persistence Behavior
Persists content indexes, compacts them, and writes new indexes on later flushes.

## Dependencies and Integration Points
Exercises repository status, snapshot creation, index listing, index optimize, and multi-source flush behavior.

## Risks
Hard-coded index counts depend on flush behavior and disabled epoch manager. The test skips a newer mode rather than validating equivalent behavior there.

## Test Signals
Shows index optimization reduces index count and flush-per-source adds one index per source.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/end_to_end_test/index_optimize_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/end_to_end_test/index_recover_test.go -->
# sources/sync-backup/kopia/tests/end_to_end_test/index_recover_test.go

## Purpose
Tests recovery of content indexes after all index blobs are deleted.

## Important APIs, Types, and Functions
`formatSpecificTestSuite.TestIndexRecover` uses `pretty.Compare` and `clitestutil`.

## Control Flow
The test creates snapshots for three sources, captures `content ls`, deletes every index blob listed by `index ls`, clears cache, verifies indexes and content are no longer visible, runs `index recover --commit`, expects one recovered index, and compares recovered content listing to the original.

## State and Persistence Behavior
Deliberately deletes repository index blobs and rebuilds index state by scanning pack blocks. Cache clearing is required to avoid own-write cache masking the deletion.

## Dependencies and Integration Points
Exercises blob deletion, cache clearing, index listing/recovery, content listing, and snapshot creation.

## Risks
Assumes six initial index blobs and one recovered blob. It verifies content listing equality but not restore from every content.

## Test Signals
Validates that lost indexes make content undiscoverable and `index recover --commit` reconstructs equivalent content metadata.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/end_to_end_test/index_recover_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/end_to_end_test/main_test.go -->
# sources/sync-backup/kopia/tests/end_to_end_test/main_test.go

## Purpose
Provides package-wide setup and cleanup for end-to-end tests by creating reusable source directory trees.

## Important APIs, Types, and Functions
Globals `sharedTestDataDirBase`, `sharedTestDataDir1`, `sharedTestDataDir2`, and `sharedTestDataDir3`. `oneTimeSetup`, `oneTimeCleanup`, and `TestMain`.

## Control Flow
Setup chooses an interesting temp directory, optionally extends the path to trigger long-filename behavior, creates three directory trees with different depth/file-size profiles, and stores paths in globals. `TestMain` runs setup before the package and delegates cleanup to `testutil.MyTestMain`.

## State and Persistence Behavior
Creates real shared source data on disk and removes it after tests. Many tests read these globals concurrently.

## Dependencies and Integration Points
Uses `testutil` path helpers and `testdirtree` generators. All end-to-end tests in the package depend on this setup.

## Risks
Shared immutable fixtures reduce setup cost but require tests not to mutate shared directories. Long path behavior is conditional and may reveal Windows/path bugs only in some environments.

## Test Signals
Setup failure aborts the package. The three fixture shapes support small-tree, large-file, and many-file test coverage.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/end_to_end_test/main_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/end_to_end_test/maintenance_test.go -->
# sources/sync-backup/kopia/tests/end_to_end_test/maintenance_test.go

## Purpose
Format-specific test for full maintenance behavior, safety margins, and blob cleanup after snapshot deletion.

## Important APIs, Types, and Functions
`formatSpecificTestSuite.TestFullMaintenance` uses `cli.MaintenanceInfo` and `snapshot.Manifest`.

## Control Flow
The test creates a repo with repository logs disabled, reads maintenance info, snapshots shared data with JSON output, sleeps to separate deletion time, deletes the snapshot, records data blobs, runs full maintenance with default safety and expects no blob reduction, then runs full maintenance with `--safety=none` and expects blob count to drop to at most two.

## State and Persistence Behavior
Creates and deletes snapshot manifests and data blobs, then maintenance rewrites/removes repository storage. Repository logs are disabled to keep blob counts predictable.

## Dependencies and Integration Points
Exercises maintenance info/run, snapshot create/delete, blob listing, content listing, and retention safety behavior.

## Risks
Blob-count expectations are sensitive to format changes. Sleep is required because create/delete in the same second can affect safety logic.

## Test Signals
Confirms default maintenance safety preserves recently deleted data, explicit no-safety removes unreferenced blobs, and repository remains listable afterward.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/end_to_end_test/maintenance_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/end_to_end_test/norace_test.go -->
# sources/sync-backup/kopia/tests/end_to_end_test/norace_test.go

## Purpose
Resource-heavy non-race test that long snapshot checkpointing does not leave incomplete checkpoint manifests after a successful final snapshot.

## Important APIs, Types, and Functions
Build-tagged `!race`. `TestSnapshotNoLeftoverCheckpoints` and helper `writeRandomFile`.

## Control Flow
The test writes a deterministic 1 GiB file, snapshots it with `--checkpoint-interval 1s`, verifies elapsed time exceeded the interval, then lists snapshots with `--incomplete` and asserts only one complete snapshot remains for the source.

## State and Persistence Behavior
Creates a large source file and checkpoint/final snapshot state in a real repository. Successful upload should clean up or hide incomplete checkpoints.

## Dependencies and Integration Points
Exercises upload checkpointing, snapshot list incomplete filtering, large file upload, and CLI command parsing through `clitestutil`.

## Risks
Very expensive in time/disk and excluded under race. It relies on the upload taking more than one second; slow or fast environments can affect timing assumptions.

## Test Signals
Confirms checkpoint generation during long uploads does not leave visible incomplete snapshots after completion.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/end_to_end_test/norace_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/end_to_end_test/policy_test.go -->
# sources/sync-backup/kopia/tests/end_to_end_test/policy_test.go

## Purpose
Tests default global policy creation and visibility in content, manifest, and policy listing commands.

## Important APIs, Types, and Functions
`TestDefaultGlobalPolicy` uses `content.Info`, `manifest.EntryMetadata`, and `policy.TargetWithPolicy`.

## Control Flow
The test creates a repo, shows global policy, parses `content ls --json` and expects one content item, shows that content, parses manifest list filtered to global policy and expects one entry, then parses policy list and expects one policy.

## State and Persistence Behavior
Repository creation persists the default global policy as content and manifest metadata.

## Dependencies and Integration Points
Exercises repo initialization, policy show/list, content list/show, manifest list filters, and JSON output parsing.

## Risks
Assumes repository creation writes exactly one content item before any other side effects. Additional default metadata would require test updates.

## Test Signals
Confirms default global policy is stored and discoverable through all relevant CLI surfaces.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/end_to_end_test/policy_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/end_to_end_test/profile_flags_test.go -->
# sources/sync-backup/kopia/tests/end_to_end_test/profile_flags_test.go

## Purpose
Tests diagnostics/profile CLI flags produce expected pprof files.

## Important APIs, Types, and Functions
`TestProfileFlags` uses an external executable runner, diagnostics output directory, and repo status profile flags.

## Control Flow
The test creates a repo, runs `repo status` with diagnostics directory and CPU/block/mutex/memory profiling options, locates the per-execution `profiles` directory, and asserts seven profile files exist and are non-empty.

## State and Persistence Behavior
Writes diagnostics artifacts to a temp directory. Repository state is otherwise incidental.

## Dependencies and Integration Points
Exercises CLI profiling setup/teardown, diagnostics directory layout, pprof profile writers, and executable-runner path.

## Risks
Uses `NewExeRunner`, so it depends on a built binary rather than in-process execution. Profile file names and layout are part of the test contract.

## Test Signals
Confirms CPU, allocs, block, goroutine, mutex, heap, and threadcreate profiles are emitted on command exit.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/end_to_end_test/profile_flags_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/end_to_end_test/repository_connect_test.go -->
# sources/sync-backup/kopia/tests/end_to_end_test/repository_connect_test.go

## Purpose
End-to-end tests for filesystem repository creation/connect behavior, path validation, reconnect tokens, and format key-derivation configuration.

## Important APIs, Types, and Functions
Tests include `TestFilesystemFlat`, `TestFilesystemRequiresAbsolutePaths`, `TestFilesystemSupportsTildeToReferToHome`, `TestReconnect`, `TestReconnectUsingToken`, `TestRepoConnectKeyDerivationAlgorithm`, and `TestRepoConnectBadKeyDerivationAlgorithm`.

## Control Flow
The tests create flat repositories and inspect directory entries, assert relative paths fail, create under `~/`, disconnect/reconnect normally, parse a reconnect command from `repo status -t -s`, iterate supported key-derivation algorithms and verify `kopia.repository.f`, then corrupt that JSON with a bad algorithm and expect connect failure.

## State and Persistence Behavior
Creates real filesystem repositories, client configs, and modifies the format blob JSON directly in the bad-algorithm test.

## Dependencies and Integration Points
Exercises repository filesystem storage options, path expansion/validation, status token output, format JSON, key derivation algorithm support, and reconnect logic.

## Risks
Text parsing of reconnect command is brittle. Home-directory test writes under the real user home but cleans up. Direct JSON mutation bypasses checksums/encryption assumptions for a targeted failure path.

## Test Signals
Confirms flat repos contain no subdirectories, filesystem paths must be absolute except `~` expansion, reconnect commands work, configured key derivation persists, and unknown algorithms are rejected.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/end_to_end_test/repository_connect_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/end_to_end_test/repository_repair_test.go -->
# sources/sync-backup/kopia/tests/end_to_end_test/repository_repair_test.go

## Purpose
Format-specific test for recovering a missing repository format blob.

## Important APIs, Types, and Functions
`formatSpecificTestSuite.TestRepositoryRepair`.

## Control Flow
The test creates a repo, writes several snapshots, deletes `kopia.repository` via blob command, disconnects, verifies reconnect fails, and for format v1 runs `repo repair filesystem` then verifies reconnect succeeds.

## State and Persistence Behavior
Deletes critical repository format state and relies on v1 embedded replicas in pack blobs for repair. Newer formats with password change enabled do not embed replicas, so repair is not expected there.

## Dependencies and Integration Points
Exercises blob removal, repo connect failure paths, repository repair command, format-version conditional behavior, and snapshot-generated pack blobs.

## Risks
Only v1 repair success is asserted; newer formats only assert failure before repair. Behavior is tightly coupled to format-blob replica policy.

## Test Signals
Confirms missing format blob prevents connect and v1 repair can reconstruct enough state to reconnect.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/end_to_end_test/repository_repair_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/end_to_end_test/repository_set_client_test.go -->
# sources/sync-backup/kopia/tests/end_to_end_test/repository_set_client_test.go

## Purpose
Tests mutable client-side repository settings through `repo set-client`.

## Important APIs, Types, and Functions
`formatSpecificTestSuite.TestRepositorySetClient` and helper `verifyHasLine`.

## Control Flow
The test creates a repo with description, username, hostname, and format cache duration; verifies status lines; sets read-only, description, hostname, and disables format cache; verifies status; asserts snapshot create fails in read-only mode; switches back to read-write with a 5s cache duration; snapshots successfully and verifies status.

## State and Persistence Behavior
Mutates local client config rather than repository data for read-only/description/host/cache settings. Snapshot after read-write creates repository content.

## Dependencies and Integration Points
Exercises repo create flags, repo status output, client config mutation, read-only enforcement in snapshot create, and cache duration formatting.

## Risks
Status text matching is substring-based but still coupled to labels and duration formatting. It does not inspect config files directly.

## Test Signals
Confirms set-client changes are reflected in status and that read-only mode prevents writes until read-write is restored.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/end_to_end_test/repository_set_client_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/end_to_end_test/repository_sync_test.go -->
# sources/sync-backup/kopia/tests/end_to_end_test/repository_sync_test.go

## Purpose
Tests repository synchronization to another filesystem location and format compatibility checks.

## Important APIs, Types, and Functions
`TestRepositorySync`.

## Control Flow
The test creates a repo, snapshots two shared directories, records source list, syncs blobs to a second directory with timestamps, changes a repository parameter and syncs again, verifies `--must-exist` fails against an empty target, connects to the synced target and checks source count, then creates a separate incompatible repo and verifies syncing it into the target fails.

## State and Persistence Behavior
Copies full repository blob state between filesystem directories, mutates repository parameters, and reconnects the same client to the copied repository.

## Dependencies and Integration Points
Exercises repo sync-to, filesystem storage, repository format parameter changes, snapshot listing, connect, and incompatible format detection.

## Risks
Only source count is compared after sync, not every snapshot/content. Reusing the same test environment after reconnect changes its active repository.

## Test Signals
Confirms sync handles normal and parameter-changed repos, refuses missing targets with `--must-exist`, produces a connectable copy, and rejects syncing incompatible repositories together.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/end_to_end_test/repository_sync_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/end_to_end_test/restore_fail_test.go -->
# sources/sync-backup/kopia/tests/end_to_end_test/restore_fail_test.go

## Purpose
Negative restore test that deletes a newly created pack blob and verifies restore failure, then verifies `--ignore-errors` permits best-effort restore.

## Important APIs, Types, and Functions
`TestRestoreFail`, `findPackBlob`, `getNewBlobIDs`, and `parseBlobIDFromBlobList`.

## Control Flow
The test creates a repo and source tree, records blob list before snapshot, snapshots source and parses the manifest from logs, records new blobs, selects a pack blob by prefix regex, deletes it, expects `snapshot restore` failure, then reruns restore with `--ignore-errors` and expects success.

## State and Persistence Behavior
Deletes actual pack content required by the snapshot, creating repository corruption for the target snapshot.

## Dependencies and Integration Points
Exercises blob list/delete, snapshot create/restore, log parsing helper `parseSnapshotResultFromLog`, pack blob naming, and restore error handling.

## Risks
Assumes at least one new pack blob exists and text blob-list parsing returns ID in the first field. Best-effort restore success does not verify output contents.

## Test Signals
Confirms missing content causes restore failure and ignore-errors changes the command outcome.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/end_to_end_test/restore_fail_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/end_to_end_test/restore_test.go -->
# sources/sync-backup/kopia/tests/end_to_end_test/restore_test.go

## Purpose
Comprehensive restore end-to-end tests for command aliases, progress reporting, object/snapshot/path addressing, archive output modes, overwrite policies, symlinks, permissions, single-file roots, sparse files, and in-place restore.

## Important APIs, Types, and Functions
Constants define Windows name and expected permissions. `fakeRestoreProgress` records progress callbacks. Major tests are `TestRestoreCommand`, `TestSnapshotRestore`, `TestRestoreSymlinkWithoutTarget`, `TestRestoreSymlinkWithNonSymlinkOverwrite`, `TestRestoreSnapshotOfSingleFile`, `TestSnapshotSparseRestore`, `TestSnapshotRestoreByPath`, and `TestRestoreByPathWithoutTarget`. Helpers include `compareDirs`, `compareDirsWithChange`, `verifyFileSize`, `verifyFileMode`, and archive validators for zip/tar/tgz.

## Control Flow
The tests create repositories and source trees, snapshot them, restore by snapshot ID/root object/subpath/source path, compare restored filesystem hashes, exercise overwrite-denial and skip-existing/delete-extra flags, generate archive outputs with auto-detected and forced modes, test symlink edge cases, restore single-file snapshots with conflicting attribute histories, verify sparse-file logical/physical sizes across many hole/data layouts, and restore in-place by source path.

## State and Persistence Behavior
Writes real source and restore trees, repository snapshots, archive files, symlinks, chmod changes, sparse files, and progress state injected into the in-process CLI app. Some tests intentionally alter source files between snapshots to test attribute resolution.

## Dependencies and Integration Points
Integrates CLI restore/snapshot commands, `snapshot/restore` progress, `fshasher`, `diff`, `localfs`, sparse-file stat helpers, archive libraries, `testdirtree`, and `clitestutil`.

## Risks
OS-specific behavior is significant: Unix permissions are skipped on Windows, sparse files are Linux-only, one arm64 sparse case is skipped, and restore idempotency is skipped on Windows. Archive validation checks structural validity but not complete archive contents. Progress injection depends on `runner.CustomizeApp`.

## Test Signals
Signals include correct restore failure from empty/nonexistent IDs, multiple progress updates and final flush, byte-for-byte tree equivalence, overwrite flag enforcement, skipped existing files, delete-extra cleanup, valid archive generation, directory mode forced for `.zip` path with `--mode=local`, symlink restoration/failure behavior, single-file destination semantics, consistent-attribute conflict behavior, sparse physical allocation preservation, and path-based latest restore.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/end_to_end_test/restore_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/end_to_end_test/server_repo_logs_test.go -->
# sources/sync-backup/kopia/tests/end_to_end_test/server_repo_logs_test.go

## Purpose
Tests that server diagnostic/log blobs are uploaded to the repository when the server exits.

## Important APIs, Types, and Functions
`TestServerRepoLogsUploadedOnShutdown` uses `apiclient.NewKopiaAPIClient`, `serverapi.Status`, `FetchCSRFTokenForTesting`, `CreateSnapshotSource`, and `serverapi.Shutdown`.

## Control Flow
The test creates a repo, verifies repo creation uploaded one log, starts an insecure passwordless server, builds a control API client, waits until status is usable, fetches CSRF token, creates a snapshot source through server control API without taking a snapshot, checks server status, deletes existing logs with `logs cleanup --max-age=1ns`, verifies logs are empty, shuts the server down, waits for exit, and verifies logs list is non-empty.

## State and Persistence Behavior
Persists repository logs, server snapshot-source configuration, and server shutdown log upload. The test deliberately cleans existing logs to isolate shutdown behavior.

## Dependencies and Integration Points
Exercises server startup, control API auth/password generation, CSRF token handling, policy payloads, logs list/cleanup, and graceful shutdown.

## Risks
Startup polling treats some HTTP errors as not-started and others as started; unusual failures could pass the poll then fail later. Log upload timing is tied to graceful shutdown.

## Test Signals
Confirms server creates repository log artifacts on exit after prior logs were removed.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/end_to_end_test/server_repo_logs_test.go -->
