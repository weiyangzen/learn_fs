<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/server/server_maintenance.go -->
# sources/sync-backup/kopia/internal/server/server_maintenance.go

- Purpose: Implements the server-side background maintenance manager for direct, writable Kopia repositories.
- Important APIs/types/functions: `srvMaintenance`, `maintenanceManagerServerInterface`, `trigger`, `stop`, `beforeRun`, `afterFailedRun`, `refresh`, `refreshLocked`, `nextMaintenanceTime`, `maybeStartMaintenanceManager`.
- Control flow: startup rejects non-direct and read-only repositories, refreshes next maintenance time, then runs one goroutine selecting between a buffered trigger channel and a closed channel. A trigger clears cached schedule state, coalesces duplicate requests, runs `srv.runMaintenanceTask`, applies failure backoff, sends optional generic-error notifications, then refreshes scheduling.
- State and persistence: `cachedNextMaintenanceTime` and `nextMaintenanceNoEarlierThan` are mutex-protected in-memory scheduling state; durable maintenance configuration is read through `maintenance.TimeToAttemptNextMaintenance` from the direct repository.
- Dependencies and integration points: Uses `clock`, `repo.DirectRepository`, `repo/maintenance`, `notification`, `notifydata`, and `notifytemplate`; it plugs into the server scheduler through `refreshScheduler`.
- Risks and edge cases: Failure throttling is process-local, trigger coalescing can hide repeated requests by design, and notification delivery is best-effort through repository state.
- Test signals: Directly covered by `server_maintenance_test.go`, including successful run, scheduler refresh, failed-run backoff, and read-only repository rejection.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/server/server_maintenance.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/server/server_maintenance_test.go -->
# sources/sync-backup/kopia/internal/server/server_maintenance_test.go

- Purpose: Verifies maintenance manager behavior against a test repository and fake server implementation.
- Important APIs/types/functions: `testServer`, `runMaintenanceTask`, `refreshScheduler`, `enableErrorNotifications`, `notificationTemplateOptions`, `TestServerMaintenance`, `TestServerMaintenanceReadOnlyRepoConnection`.
- Control flow: Tests configure maintenance params in a direct write session, start the manager, trigger runs, wait for atomics to observe execution, inject one error, and verify retry backoff. The read-only case rewrites client options and reopens the repo before startup.
- State and persistence: Uses repository maintenance manifests/params plus in-memory atomics and a mutex-protected injected error in `testServer`.
- Dependencies and integration points: Uses `repotesting`, `repo.DirectWriteSession`, `maintenance.SetParams`, `clock`, and `testify/require`.
- Risks and edge cases: Timing assertions use `Eventually` and wall-clock intervals; tests disable error notifications, so notification-send behavior is not exercised here.
- Test signals: This is the direct test signal for `server_maintenance.go`.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/server/server_maintenance_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/server/server_mount_manager.go -->
# sources/sync-backup/kopia/internal/server/server_mount_manager.go

- Purpose: Manages active snapshot mount controllers keyed by root object ID.
- Important APIs/types/functions: `getMountController`, `listMounts`, `deleteMount`, `unmountAllLocked`.
- Control flow: `getMountController` checks the `Server.mounts` map under `serverMutex`, returns an existing controller, optionally creates a new `mount.Directory` over `snapshotfs.DirectoryEntry`, and stores it. Listing clones the map; delete/unmount remove entries.
- State and persistence: State is in-memory only in `Server.mounts`; mounted filesystem state is owned by the mount controller.
- Dependencies and integration points: Integrates `internal/mount`, `snapshot/snapshotfs`, repository object IDs, and server HTTP mount routes elsewhere.
- Risks and edge cases: `unmountAllLocked` requires the caller already hold `serverMutex`; unmount failures are logged but entries are still deleted.
- Test signals: No direct test in this file; mount behavior is indirectly exercised through server API tests and mount controller implementations.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/server/server_mount_manager.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/server/server_test.go -->
# sources/sync-backup/kopia/internal/server/server_test.go

- Purpose: Integration-tests API-server-backed repository access, authentication, UI access restrictions, object/manifest operations, and remote notifications.
- Important APIs/types/functions: `TestServer`, `TestGRPCServer_AuthenticationError`, `TestServerUIAccessDeniedToRemoteUser`, `remoteRepositoryTest`, `remoteRepositoryNotificationTest`, `mustWriteObject`, `mustReadObject`, `mustReadManifest`, `mustListSnapshotCount`.
- Control flow: Tests start an in-process test server, connect via API server config, cancel the original context to verify detached operation, then perform repository reads/writes, manifest saves/deletes, object prefetch, notification sends, and UI/remote user access checks.
- State and persistence: Uses repotesting repositories, remote API repository clients, temporary caches, snapshot manifests, notification profile manifests, and HTTP test server counters.
- Dependencies and integration points: Integrates `apiclient`, `servertesting`, `repotesting`, `repo`, `content`, `snapshot`, `notifyprofile`, `notification`, and webhook senders.
- Risks and edge cases: Access-control expectations depend on route-specific CSRF policy; notification tests use one webhook success and one failing path but do not validate all sender types.
- Test signals: This is high-value integration coverage for server API repository behavior and remote notification forwarding.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/server/server_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/server/source_manager.go -->
# sources/sync-backup/kopia/internal/server/source_manager.go

- Purpose: Implements the per-source snapshot scheduling/upload state machine used by the server.
- Important APIs/types/functions: `sourceManager`, `sourceManagerServerInterface`, `Status`, `start`, `runLocal`, `runReadOnly`, `scheduleSnapshotNow`, `upload`, `cancel`, `pause`, `resume`, `stop`, `snapshotInternal`, `refreshStatus`, `uitaskProgress`, `newSourceManager`.
- Control flow: A source starts by refreshing policy/snapshot status, then runs local mode waiting for snapshot requests or remote read-only mode. Upload requests enqueue a buffered signal, local mode runs a server snapshot task, and `snapshotInternal` opens the local filesystem, creates a repository write session, constructs an uploader and policy tree, reports UI progress, saves a snapshot unless identical snapshots are ignored, and applies retention.
- State and persistence: Mutex-protected state tracks current uploader, scheduling policy, status, next snapshot time, last snapshots, pause flag, current task, last attempted time, and read-only mode. Durable state is repository policy and snapshot manifests.
- Dependencies and integration points: Integrates `fs/localfs`, `serverapi`, `uitask`, `notifydata`, `repo.WriteSession`, `snapshot`, `policy`, and `upload`.
- Risks and edge cases: Cancellation depends on uploader registration order, refresh failures collapse into `FAILED` without detail, and failed upload backoff only changes an already-known next snapshot time.
- Test signals: Covered indirectly by server/scheduler/API tests; progress callbacks are tied to upload package behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/server/source_manager.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/server/util_test.go -->
# sources/sync-backup/kopia/internal/server/util_test.go

- Purpose: Provides test helper functions for server API tests.
- Important APIs/types/functions: `mustCreateSource`, `mustSetPolicy`, `mustListSources`, `mustGetTask`, `mustListTasks`, `mustGetLatestTask`, `waitForTask`.
- Control flow: Helpers wrap typed `serverapi` calls with `testlogging.Context`, assert no error, and return decoded source/task data; `waitForTask` polls until completion or timeout.
- State and persistence: No persistent state; uses remote server API state, source policy manifests, and UI task state created by tests.
- Dependencies and integration points: Integrates `apiclient`, `serverapi`, `testlogging`, `uitask`, `snapshot`, `policy`, and `clock`.
- Risks and edge cases: Polling sleeps on real time and fails the test with the last task state when timeout is reached.
- Test signals: Supports broader server test files; it has no top-level `Test...` function itself.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/server/util_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/serverapi/client_wrappers.go -->
# sources/sync-backup/kopia/internal/serverapi/client_wrappers.go

- Purpose: Provides typed client-side wrappers for Kopia server API endpoints.
- Important APIs/types/functions: `CreateSnapshotSource`, `Estimate`, `Restore`, `GetTask`, `UploadSnapshots`, `CancelUpload`, `CreateRepository`, `ConnectToRepository`, `DisconnectFromRepository`, `Shutdown`, `RepoStatus`, `Status`, `GetThrottlingLimits`, `SetThrottlingLimits`, `ListSources`, `ListSnapshots`, `ListPolicies`, `SetPolicy`, `ResolvePolicy`, `ListTasks`, `GetObject`, `matchSourceParameters`.
- Control flow: Each wrapper constructs a route string, allocates the expected response type, invokes `KopiaAPIClient.Get/Post/Put`, wraps errors with operation context, and returns the decoded value.
- State and persistence: Stateless wrapper layer; all persistent effects occur on the server/repository side.
- Dependencies and integration points: Integrates `apiclient`, `uitask`, throttling limits, `object.ErrObjectNotFound`, `snapshot`, and `policy`.
- Risks and edge cases: Query strings are built by string concatenation without URL escaping, so unusual host/user/path values can alter parameters.
- Test signals: Exercised by server API integration tests and helpers in `server/util_test.go`.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/serverapi/client_wrappers.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/serverapi/serverapi.go -->
# sources/sync-backup/kopia/internal/serverapi/serverapi.go

- Purpose: Defines the JSON request/response contract for Kopia server APIs.
- Important APIs/types/functions: `StatusResponse`, `SourcesResponse`, `SourceStatus`, `PolicyListEntry`, `PoliciesResponse`, `Empty`, `APIErrorCode`, `ErrorResponse`, `SourceActionResponse`, `MultipleSourceActionResponse`, `CreateRepositoryRequest`, `ConnectRepositoryRequest`, `SupportedAlgorithmsResponse`, `Snapshot`, `RestoreRequest`, `EstimateRequest`, `ResolvePolicyRequest`, `ResolvePolicyResponse`, `UIPreferences`.
- Control flow: This file is declarative; server handlers and clients marshal/unmarshal these structs.
- State and persistence: Struct fields expose repository configuration, source status, snapshots, tasks, policies, restore/estimate inputs, and UI preferences; persistence is owned by the server and repository layers.
- Dependencies and integration points: Integrates `fs`, `uitask`, `repo`, `blob`, `format`, `manifest`, `object`, `snapshot`, `policy`, `restore`, and `upload`.
- Risks and edge cases: JSON tags are API compatibility surface; changing fields or names can break UI, CLI, or remote clients.
- Test signals: Validated indirectly by server API integration tests and client wrappers.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/serverapi/serverapi.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/servertesting/servertesting.go -->
# sources/sync-backup/kopia/internal/servertesting/servertesting.go

- Purpose: Supplies helpers for starting a Kopia server inside tests and connecting API-server-backed repositories.
- Important APIs/types/functions: `TestUsername`, `TestHostname`, `TestPassword`, `TestUIUsername`, `TestUIPassword`, `StartServer`, `StartServerContext`, `ConnectAndOpenAPIServer`.
- Control flow: `StartServerContext` builds a server with test authenticators, sets a repository, installs API/static handlers on a mux, starts an HTTP or TLS test server, and returns `APIServerInfo`. `ConnectAndOpenAPIServer` creates a temporary config, connects, registers cleanup, and opens the repo.
- State and persistence: Uses temporary config files, UI preferences files, test server lifecycle cleanup, and the provided repotesting repository.
- Dependencies and integration points: Integrates `auth`, `passwordpersist`, `repotesting`, `server`, `testlogging`, `testutil`, `repo`, and `content`.
- Risks and edge cases: TLS fingerprint calculation must match client trust behavior; cleanup order disconnects the repository before closing the server.
- Test signals: Used by `server_test.go` and other integration tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/servertesting/servertesting.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/sleepable/sleepable_timer.go -->
# sources/sync-backup/kopia/internal/sleepable/sleepable_timer.go

- Purpose: Implements a timer that fires at or soon after a target time while tolerating machine sleep by waking periodically.
- Important APIs/types/functions: `MaxSleepTime`, `Timer`, `Stop`, `NewTimer`.
- Control flow: `NewTimer` starts a goroutine that repeatedly calls `nowFunc`, closes the public channel once time is after the target, otherwise sleeps for `min(until-now, MaxSleepTime)`. `Stop` closes `stopChan` once and exits without closing `C`.
- State and persistence: State is a goroutine, `time.Timer`, stop channel, and `sync.Once`; there is no persistence.
- Dependencies and integration points: Uses only `sync` and `time`; callers can inject `nowFunc` for tests.
- Risks and edge cases: Exact equality with target time relies on timer granularity and `After` semantics; tests expect immediate behavior for now/past times.
- Test signals: `sleepable_timer_test.go` covers timing, stop behavior, concurrent stops, past/now targets, long waits, and channel closure semantics.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/sleepable/sleepable_timer.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/sleepable/sleepable_timer_test.go -->
# sources/sync-backup/kopia/internal/sleepable/sleepable_timer_test.go

- Purpose: Tests sleepable timer timing, stopping, concurrency, and channel behavior.
- Important APIs/types/functions: `testMaxSleepTime`, `setMaxSleepTimeForTest`, `TestNewTimer`, `TestTimerStop`, `TestTimerConcurrentStop`, `TestTimerEdgeCases`, `TestTimerChannelBehavior`.
- Control flow: Tests lower `MaxSleepTime`, create timers against `clock.Now`, wait on channels, stop timers before/after firing, and assert timing tolerances.
- State and persistence: Uses package global `MaxSleepTime` with cleanup restoration and temporary goroutines.
- Dependencies and integration points: Uses `clock`, `sync`, `testing`, and `time`.
- Risks and edge cases: Real-time sleeps can be flaky under heavy load, though tolerances are broad and durations are short.
- Test signals: Direct coverage for `sleepable_timer.go`.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/sleepable/sleepable_timer_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/sparsefile/sparsefile.go -->
# sources/sync-backup/kopia/internal/sparsefile/sparsefile.go

- Purpose: Copies data to a seekable destination while converting all-zero blocks into sparse file holes.
- Important APIs/types/functions: `Copy`, `copyBuffer`, `isAllZero`.
- Control flow: `Copy` borrows a shared buffer from `iocopy`, slices it to requested size, and delegates. `copyBuffer` reads into the buffer, seeks over zero blocks, writes non-zero blocks, accounts bytes, and handles read/write/short-write errors.
- State and persistence: Persistent effects are writes/seeks on the destination file; no package state beyond borrowed buffer lifecycle.
- Dependencies and integration points: Integrates `io`, `pkg/errors`, and `internal/iocopy`.
- Risks and edge cases: `isAllZero` is called on the full buffer rather than `buf[:nr]`, so short reads with stale non-zero bytes could defeat sparse skipping.
- Test signals: `sparsefile_test.go` checks content equivalence for empty, hole, mixed, and null sparse copies on non-Windows systems.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/sparsefile/sparsefile.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/sparsefile/sparsefile_test.go -->
# sources/sync-backup/kopia/internal/sparsefile/sparsefile_test.go

- Purpose: Validates sparse copy output content against source files.
- Important APIs/types/functions: `TestSparseCopy`.
- Control flow: The test skips Windows, creates source/destination files, writes chunks at offsets, truncates destination, gets filesystem block size, runs `Copy`, then reads both files and compares bytes.
- State and persistence: Uses a temporary directory and filesystem sparse allocation behavior.
- Dependencies and integration points: Uses `stat.GetBlockSize`, `os`, `filepath`, `runtime`, and `testify/require`.
- Risks and edge cases: It verifies byte equality but does not assert physical allocation savings or short-reader buffer behavior.
- Test signals: Direct test coverage for `sparsefile.Copy`.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/sparsefile/sparsefile_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/stat/stat_bsd.go -->
# sources/sync-backup/kopia/internal/stat/stat_bsd.go

- Purpose: Provides OpenBSD-specific filesystem allocation and block-size helpers.
- Important APIs/types/functions: `diskBlockSize`, `errInvalidBlockSize`, `GetFileAllocSize`, `GetBlockSize`.
- Control flow: `GetFileAllocSize` calls `syscall.Stat` and multiplies block count by 512. `GetBlockSize` calls `syscall.Statfs`, validates `F_bsize`, and returns it.
- State and persistence: Reads filesystem metadata only; no mutation or repository state.
- Dependencies and integration points: Build-constrained to `openbsd`; depends on `syscall` and `pkg/errors`.
- Risks and edge cases: Platform syscall fields differ from other Unix variants, requiring this separate file.
- Test signals: `stat_test.go` runs on non-Windows platforms and covers positive block/allocation sizes.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/stat/stat_bsd.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/stat/stat_test.go -->
# sources/sync-backup/kopia/internal/stat/stat_test.go

- Purpose: Tests stat helpers on non-Windows platforms.
- Important APIs/types/functions: `TestGetBlockSize`, `TestGetBlockSizeFromCurrentFS`, `TestGetFileAllocSize`.
- Control flow: Tests query block size for `os.DevNull` and current directory, then create a one-byte temp file and require allocated size to be at least 512 bytes.
- State and persistence: Uses temporary filesystem files only.
- Dependencies and integration points: Build-constrained to `!windows`; uses `os`, `filepath`, and `testify/require`.
- Risks and edge cases: Allocation minimum assumes conventional block accounting; exotic filesystems may behave differently.
- Test signals: Direct test coverage for Unix/BSD stat implementations.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/stat/stat_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/stat/stat_unix.go -->
# sources/sync-backup/kopia/internal/stat/stat_unix.go

- Purpose: Provides Linux, FreeBSD, and Darwin filesystem allocation and block-size helpers.
- Important APIs/types/functions: `diskBlockSize`, `errInvalidBlockSize`, `GetFileAllocSize`, `GetBlockSize`.
- Control flow: `GetFileAllocSize` reads `syscall.Stat_t.Blocks` and multiplies by 512; `GetBlockSize` validates `syscall.Statfs_t.Bsize`.
- State and persistence: Reads filesystem metadata only.
- Dependencies and integration points: Build-constrained to `linux || freebsd || darwin`; depends on `syscall` and `pkg/errors`.
- Risks and edge cases: Casts and syscall field sizes vary by architecture; invalid or unsupported paths return raw syscall errors.
- Test signals: Covered by `stat_test.go` on matching platforms.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/stat/stat_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/stat/stat_windows.go -->
# sources/sync-backup/kopia/internal/stat/stat_windows.go

- Purpose: Provides Windows stubs for stat helpers where sparse allocation/block-size behavior is not implemented.
- Important APIs/types/functions: `errNotImplemented`, `GetFileAllocSize`, `GetBlockSize`.
- Control flow: Both public functions immediately return zero and `errNotImplemented`.
- State and persistence: No state or filesystem mutation.
- Dependencies and integration points: Build-constrained to `windows`; callers must handle unsupported behavior.
- Risks and edge cases: Any cross-platform caller expecting real values must avoid or special-case Windows.
- Test signals: `stat_test.go` is excluded on Windows, so this stub is not directly tested here.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/stat/stat_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/stats/count_map.go -->
# sources/sync-backup/kopia/internal/stats/count_map.go

- Purpose: Implements a generic concurrent map of atomic uint32 counters.
- Important APIs/types/functions: `CountersMap`, `Increment`, `add`, `Length`, `Get`, `Range`, `CountMap`.
- Control flow: Increment first attempts `Load`, then `LoadOrStore` for new counters, increments length only for new keys, and atomically adds to the pointed counter. Range and CountMap iterate over `sync.Map`.
- State and persistence: In-memory `sync.Map` plus atomic length/counters; no removal or persistence.
- Dependencies and integration points: Uses `sync` and `sync/atomic`.
- Risks and edge cases: Length and snapshots are approximate under concurrent mutation; counters can overflow because `add` has no overflow guard.
- Test signals: `count_map_test.go` covers missing keys, new/existing increments, add, range, length, early stop, snapshot, and concurrent increments.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/stats/count_map.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/stats/count_map_test.go -->
# sources/sync-backup/kopia/internal/stats/count_map_test.go

- Purpose: Tests `CountersMap` behavior and concurrency.
- Important APIs/types/functions: `TestConcurrentCountMap_Get_MissingKey`, `TestConcurrentCountMap_IncrementAndGet_NewAndExistingKey`, `TestConcurrentCountMap_Add`, `TestConcurrentCountMap_Range`, `TestConcurrentCountMap_Length`, `TestConcurrentCountMap_Range_StopEarly`, `TestConcurrentCountMap_CountMap_Snapshot`, `TestConcurrentCountMap_ConcurrentIncrement`.
- Control flow: Tests instantiate maps with string/int keys, perform adds/increments, inspect values and length, stop iteration early, and run multiple goroutines incrementing one key.
- State and persistence: In-memory atomic counters only.
- Dependencies and integration points: Uses `sync`, `testing`, and `testify/require`.
- Risks and edge cases: Tests do not cover overflow or heavily contended new-key creation beyond one shared key.
- Test signals: Direct coverage for `count_map.go`.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/stats/count_map_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/stats/countsum.go -->
# sources/sync-backup/kopia/internal/stats/countsum.go

- Purpose: Tracks an atomic count and sum pair for simple concurrent statistics.
- Important APIs/types/functions: `CountSum`, `Add`, `Approximate`.
- Control flow: `Add` atomically increments count and sum and returns the new values; `Approximate` loads both independently.
- State and persistence: In-memory atomics only.
- Dependencies and integration points: Uses `sync/atomic`.
- Risks and edge cases: Count and sum are not read as one atomic snapshot, so returned pairs are approximate under concurrent updates.
- Test signals: No direct test in this subset; behavior is small and relies on atomic primitives.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/stats/countsum.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/tempfile/tempfile.go -->
# sources/sync-backup/kopia/internal/tempfile/tempfile.go

- Purpose: Documents the cross-platform tempfile package for private read-write files that auto-delete on close.
- Important APIs/types/functions: package declaration only.
- Control flow: Implementation is selected by platform-specific files in the same package.
- State and persistence: Actual state is OS file descriptors and temporary directory entries managed by platform implementations.
- Dependencies and integration points: No imports in this file.
- Risks and edge cases: Behavior depends entirely on platform-specific files and build tags.
- Test signals: `tempfile_test.go`, `tempfile_verify_test.go`, and Linux fallback tests cover behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/tempfile/tempfile.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/tempfile/tempfile_linux.go -->
# sources/sync-backup/kopia/internal/tempfile/tempfile_linux.go

- Purpose: Creates Linux auto-deleting temporary files using `O_TMPFILE` when supported.
- Important APIs/types/functions: `permissions`, `CreateAutoDelete`.
- Control flow: Opens `os.TempDir()` with `O_RDWR|O_TMPFILE|O_CLOEXEC`; on supported fallback errors (`EISDIR`, `EOPNOTSUPP`, or nil invalid fd) it calls `createUnixFallback`; otherwise returns an `os.PathError`.
- State and persistence: Returns an unlinked anonymous file descriptor when possible; fallback creates then unlinks a named file.
- Dependencies and integration points: Uses `golang.org/x/sys/unix`, `syscall`, and `os`.
- Risks and edge cases: `O_TMPFILE` support varies by filesystem/kernel; fallback path must preserve delete-on-close semantics.
- Test signals: Covered by generic tempfile verification and `tempfile_linux_fallback_test.go`.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/tempfile/tempfile_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/tempfile/tempfile_linux_fallback_test.go -->
# sources/sync-backup/kopia/internal/tempfile/tempfile_linux_fallback_test.go

- Purpose: Explicitly tests the Unix fallback tempfile path on Linux.
- Important APIs/types/functions: `TestCreateFallback`.
- Control flow: Calls `VerifyTempfile` with `createUnixFallback`.
- State and persistence: Uses a temporary file that is unlinked while open.
- Dependencies and integration points: Build-constrained to Linux; depends on package-local fallback function.
- Risks and edge cases: Does not force `O_TMPFILE` failure in `CreateAutoDelete`; it directly exercises the fallback helper.
- Test signals: Direct fallback coverage on Linux.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/tempfile/tempfile_linux_fallback_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/tempfile/tempfile_test.go -->
# sources/sync-backup/kopia/internal/tempfile/tempfile_test.go

- Purpose: Tests the public `tempfile.CreateAutoDelete` implementation selected for the current platform.
- Important APIs/types/functions: `TestTempFile`.
- Control flow: Delegates to `tempfile.VerifyTempfile`.
- State and persistence: Uses platform temporary files and close-time deletion.
- Dependencies and integration points: Imports package externally as `tempfile_test` to exercise public API.
- Risks and edge cases: Coverage is behavioral, not implementation-specific except through selected build tags.
- Test signals: Direct public API coverage.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/tempfile/tempfile_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/tempfile/tempfile_unix_fallback.go -->
# sources/sync-backup/kopia/internal/tempfile/tempfile_unix_fallback.go

- Purpose: Provides create-and-unlink fallback implementation for Unix-like platforms.
- Important APIs/types/functions: `createUnixFallback`.
- Control flow: Creates a temp file with prefix `kt-`, immediately removes the directory entry while keeping the handle open, closes on unlink failure, and returns the open file.
- State and persistence: File contents live only through the open descriptor; no path should remain after creation.
- Dependencies and integration points: Build-constrained to `linux || freebsd || darwin || openbsd`; uses `os` and `pkg/errors`.
- Risks and edge cases: If unlink fails, descriptor cleanup must happen to avoid leaks; returned `Name` can refer to a removed path.
- Test signals: Covered by generic tempfile tests and explicit Linux fallback test.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/tempfile/tempfile_unix_fallback.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/tempfile/tempfile_unix_nonlinux.go -->
# sources/sync-backup/kopia/internal/tempfile/tempfile_unix_nonlinux.go

- Purpose: Selects the Unix fallback implementation as the public auto-delete tempfile implementation on FreeBSD, Darwin, and OpenBSD.
- Important APIs/types/functions: `CreateAutoDelete`.
- Control flow: Immediately delegates to `createUnixFallback`.
- State and persistence: Same create-and-unlink descriptor behavior as the fallback helper.
- Dependencies and integration points: Build-constrained to `freebsd || darwin || openbsd`; imports `os` for signature.
- Risks and edge cases: Lacks Linux `O_TMPFILE` optimization but should preserve deletion behavior.
- Test signals: Generic tempfile tests cover this path on matching platforms.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/tempfile/tempfile_unix_nonlinux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/tempfile/tempfile_verify_test.go -->
# sources/sync-backup/kopia/internal/tempfile/tempfile_verify_test.go

- Purpose: Provides shared tempfile behavior assertions for platform implementations.
- Important APIs/types/functions: `VerifyTempfile`.
- Control flow: Creates a file, writes `hello`, seeks, reads `ello`, closes, and if the file has a name, verifies `os.Stat` fails with platform-appropriate not-found text.
- State and persistence: Uses a single temporary file descriptor from the provided factory.
- Dependencies and integration points: Uses `io`, `os`, `runtime`, `testing`, and `testify/require`.
- Risks and edge cases: Error message text is platform-specific and can vary by Go/OS localization.
- Test signals: Shared direct coverage for public and fallback tempfile creators.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/tempfile/tempfile_verify_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/tempfile/tempfile_windows.go -->
# sources/sync-backup/kopia/internal/tempfile/tempfile_windows.go

- Purpose: Creates Windows temporary files that are deleted automatically on close.
- Important APIs/types/functions: `CreateAutoDelete`.
- Control flow: Builds a random path under `os.TempDir`, converts to UTF-16, calls `syscall.CreateFile` with read/write access and `FILE_FLAG_DELETE_ON_CLOSE`, and wraps the handle as `*os.File`.
- State and persistence: The filesystem entry is scheduled for deletion by Windows handle semantics.
- Dependencies and integration points: Build-constrained to Windows; uses `google/uuid`, `x/sys/windows`, `syscall`, and `os`.
- Risks and edge cases: Sharing mode is zero, so concurrent access is intentionally restricted; path conversion and handle ownership must be correct.
- Test signals: Generic tempfile public API test covers behavior on Windows.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/tempfile/tempfile_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/testlogging/ctx.go -->
# sources/sync-backup/kopia/internal/testlogging/ctx.go

- Purpose: Builds test contexts with Kopia loggers that write to `testing.T`.
- Important APIs/types/functions: `testingT`, `Level`, `LevelDebug`, `LevelInfo`, `LevelWarn`, `LevelError`, `NewTestLogger`, `Context`, `ContextForCleanup`, `ContextWithLevel`, `ContextWithLevelAndPrefix`, `ContextWithLevelAndPrefixFunc`.
- Control flow: Functions wrap a test context with `logging.WithLogger` and module-specific `PrintfLevel` loggers; cleanup contexts use `context.WithoutCancel`.
- State and persistence: No durable state; logger behavior is carried in context values.
- Dependencies and integration points: Integrates `repo/logging`, zap levels, and Go test cleanup patterns.
- Risks and edge cases: Cleanup contexts deliberately ignore cancellation, so cleanup operations can continue after test context cancellation.
- Test signals: Used throughout tests in this subset; no direct unit test.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/testlogging/ctx.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/testlogging/printf.go -->
# sources/sync-backup/kopia/internal/testlogging/printf.go

- Purpose: Adapts printf-style functions such as `testing.T.Logf` into zap sugared loggers.
- Important APIs/types/functions: `Printf`, `PrintfLevel`, `PrintfFactory`, `printfWriter`, `Write`, `Sync`.
- Control flow: Builds a zap core with Kopia console encoder and a writer that trims trailing newlines and prefixes messages before calling the provided printf function.
- State and persistence: Stateless aside from the writer's function and prefix fields.
- Dependencies and integration points: Integrates `zap`, `zapcore`, `zaplogutil`, and `repo/logging`.
- Risks and edge cases: Output formatting depends on the custom console encoder; `Sync` is a no-op because test loggers do not need flush.
- Test signals: Indirectly exercised by test contexts and helper output.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/testlogging/printf.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/testutil/dockertestutil.go -->
# sources/sync-backup/kopia/internal/testutil/dockertestutil.go

- Purpose: Provides Docker execution helpers for tests that depend on containers.
- Important APIs/types/functions: `RunDockerAndGetOutputOrSkip`, `runDockerAndGetOutputOrSkip`, `RunContainerAndKillOnCloseOrSkip`, `GetContainerMappedPortAddress`.
- Control flow: Runs `docker` commands with test logging context, skips locally on failure but fails in CI, registers cleanup to kill containers, and parses mapped ports/`DOCKER_HOST`.
- State and persistence: External Docker containers are started and killed through test cleanup.
- Dependencies and integration points: Integrates `exec.CommandContext`, `testlogging`, `testing`, and Docker CLI behavior.
- Risks and edge cases: Docker availability changes test outcome; cleanup uses a context without cancellation because `t.Context()` is canceled during cleanup.
- Test signals: Utility file; no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/testutil/dockertestutil.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/testutil/norace.go -->
# sources/sync-backup/kopia/internal/testutil/norace.go

- Purpose: Declares race-detector state for non-race builds.
- Important APIs/types/functions: `isRaceDetector`.
- Control flow: Declaration-only file selected by `!race` build tag.
- State and persistence: Compile-time constant only.
- Dependencies and integration points: Used by testutil skip/complexity helpers.
- Risks and edge cases: Must stay complementary with `race.go`.
- Test signals: Indirectly affects tests that call `ShouldReduceTestComplexity` or skip helpers.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/testutil/norace.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/testutil/race.go -->
# sources/sync-backup/kopia/internal/testutil/race.go

- Purpose: Declares race-detector state for race-enabled builds.
- Important APIs/types/functions: `isRaceDetector`.
- Control flow: Declaration-only file selected by `race` build tag.
- State and persistence: Compile-time constant only.
- Dependencies and integration points: Used by testutil skip/complexity helpers.
- Risks and edge cases: Must stay complementary with `norace.go`.
- Test signals: Indirectly changes test skip/reduction behavior under `go test -race`.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/testutil/race.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/testutil/serverparameters.go -->
# sources/sync-backup/kopia/internal/testutil/serverparameters.go

- Purpose: Parses ephemeral connection parameters emitted by `kopia server start`.
- Important APIs/types/functions: `serverOutputAddress`, `serverOutputCertSHA256`, `serverOutputPassword`, `serverOutputControlPassword`, `ServerParameters`, `ProcessOutput`.
- Control flow: `ProcessOutput` checks known line prefixes, fills matching struct fields, and returns false only when the server address line is seen.
- State and persistence: Stores parsed strings in a caller-owned `ServerParameters` struct.
- Dependencies and integration points: Used by tests or command runners that consume server stderr startup lines.
- Risks and edge cases: Prefix text is an implicit contract with server startup logging.
- Test signals: No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/testutil/serverparameters.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/testutil/testutil.go -->
# sources/sync-backup/kopia/internal/testutil/testutil.go

- Purpose: Provides common test helpers for skips, complexity decisions, leak checking, JSON parsing, reflection-driven tests, directory sizing, and type assertions.
- Important APIs/types/functions: `ProviderTest`, `SkipNonDeterministicTestUnderCodeCoverage`, `SkipTestUnlessLinux`, `SkipTestOnCIUnlessLinuxAMD64`, `ShouldReduceTestComplexity`, `ShouldSkipUnicodeFilenames`, `ShouldSkipLongFilenames`, `MyTestMain`, `MustParseJSONLines`, `RunAllTestsWithParam`, `MustGetTotalDirSize`, `EnsureType`.
- Control flow: Helpers inspect environment/runtime flags, call `testing` skip/fatal methods, run releasable verification after `m.Run`, decode JSON with unknown-field rejection, and recurse through directories.
- State and persistence: Uses environment variables and filesystem reads; `MyTestMain` exits the process with final status.
- Dependencies and integration points: Integrates `releasable`, `testify/require`, runtime metadata, and Go testing conventions.
- Risks and edge cases: Environment-driven skips can hide coverage locally; `MyTestMain` owns process exit.
- Test signals: Widely used by tests; no direct unit test in this subset.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/testutil/testutil.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/testutil/tmpdir.go -->
# sources/sync-backup/kopia/internal/testutil/tmpdir.go

- Purpose: Creates interesting temporary directories and log directories for tests, with cleanup and log dumping.
- Important APIs/types/functions: `interestingLengths`, `GetInterestingTempDirectoryName`, `TempDirectory`, `TempDirectoryShort`, `TempLogDirectory`, `dumpLogs`, `dumpLogFile`, `trimOutput`, `splitLines`.
- Control flow: Temp helpers create names with random target lengths, optionally extend paths, register cleanup that preserves failed-test artifacts, and log helpers dump bounded log output unless disabled.
- State and persistence: Creates and removes filesystem directories; may preserve logs/temp files on failures or `KOPIA_KEEP_LOGS`.
- Dependencies and integration points: Integrates `clock`, environment variables, `testing.TB`, and filesystem APIs.
- Risks and edge cases: Random path lengths can expose platform limits; preserved logs can consume disk in repeated failures.
- Test signals: Utility file; behavior is indirectly exercised by tests using temp/log helpers.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/testutil/tmpdir.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/timestampmeta/timestampmeta.go -->
# sources/sync-backup/kopia/internal/timestampmeta/timestampmeta.go

- Purpose: Converts timestamps to/from metadata map values stored as Unix nanoseconds.
- Important APIs/types/functions: `ToMap`, `FromValue`.
- Control flow: `ToMap` returns nil for zero time, otherwise a one-entry map with decimal nanoseconds. `FromValue` parses an int64 and returns `time.Unix(0, nanos)` plus success flag.
- State and persistence: Metadata maps are caller-owned; no package state.
- Dependencies and integration points: Intended for per-blob metadata/tags; depends on `strconv` and `time`.
- Risks and edge cases: Invalid numeric strings fail gracefully; timezone names are not preserved because Unix nanoseconds are absolute.
- Test signals: `timestampmeta_test.go` covers `ToMap`; `FromValue` lacks direct test in this subset.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/timestampmeta/timestampmeta.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/timestampmeta/timestampmeta_test.go -->
# sources/sync-backup/kopia/internal/timestampmeta/timestampmeta_test.go

- Purpose: Tests timestamp-to-map conversion.
- Important APIs/types/functions: `timeValue`, `storedValue`, `TestToMap`.
- Control flow: Compares a fixed UTC time to the expected nanosecond string and verifies zero time returns nil.
- State and persistence: None beyond table globals.
- Dependencies and integration points: Uses external test package `timestampmeta_test` and `testify/require`.
- Risks and edge cases: Does not test `FromValue` or malformed metadata.
- Test signals: Partial direct coverage for `timestampmeta.go`.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/timestampmeta/timestampmeta_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/timetrack/estimator.go -->
# sources/sync-backup/kopia/internal/timetrack/estimator.go

- Purpose: Estimates task completion percentage, end time, remaining duration, and speed.
- Important APIs/types/functions: `Estimator`, `Timings`, `Estimate`, `Completed`, `Start`.
- Control flow: `Estimate` requires elapsed time over one second and positive progress/total, clamps completed ratio for prediction, computes remaining time against `clock.Now`, and returns speed. `Completed` returns elapsed duration and average speed.
- State and persistence: Holds only an in-memory start time.
- Dependencies and integration points: Uses `clock` and real `time.Now`.
- Risks and edge cases: ETA is unavailable for short or zero-progress tasks; percent uses raw completed/total and can exceed 100 even though prediction clamps.
- Test signals: No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/timetrack/estimator.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/timetrack/throttle.go -->
# sources/sync-backup/kopia/internal/timetrack/throttle.go

- Purpose: Provides atomic throttling for periodic UI/progress output.
- Important APIs/types/functions: `Throttle`, `ShouldOutput`, `Reset`.
- Control flow: `ShouldOutput` reads the next allowed Unix nano timestamp, compares real time, and uses compare-and-swap to reserve the next interval; `Reset` clears the timestamp.
- State and persistence: In-memory atomic int64 only.
- Dependencies and integration points: Used by progress reporters that need cheap concurrent throttling.
- Risks and edge cases: Uses wall-clock time, so clock jumps can affect throttling.
- Test signals: No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/timetrack/throttle.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/timetrack/timer.go -->
# sources/sync-backup/kopia/internal/timetrack/timer.go

- Purpose: Measures elapsed time from construction.
- Important APIs/types/functions: `Timer`, `Elapsed`, `StartTimer`.
- Control flow: `StartTimer` captures `time.Now`; `Elapsed` returns `time.Since(startTime)`.
- State and persistence: In-memory start timestamp only.
- Dependencies and integration points: Used by operations needing simple duration measurement.
- Risks and edge cases: Uses real time rather than injectable clock.
- Test signals: No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/timetrack/timer.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/tlsutil/tlsutil.go -->
# sources/sync-backup/kopia/internal/tlsutil/tlsutil.go

- Purpose: Provides TLS certificate generation, PEM writing, and single-fingerprint trust helpers.
- Important APIs/types/functions: `GenerateServerCertificate`, `WritePrivateKeyToFile`, `WriteCertificateToFile`, `TLSConfigTrustingSingleCertificate`, `TransportTrustingSingleCertificate`, `verifyPeerCertificate`.
- Control flow: Certificate generation creates RSA key, validity window, random serial, server-auth self-signed cert, and DNS/IP SANs. Write helpers open files mode `0600` and PEM-encode. Trust helpers clone HTTP transport and install fingerprint verification.
- State and persistence: Writes private key/certificate files when requested; otherwise returns in-memory TLS objects.
- Dependencies and integration points: Integrates `crypto/x509`, `tls`, `net/http`, `clock`, and Kopia logging.
- Risks and edge cases: `InsecureSkipVerify` is intentionally used with fingerprint verification; wrong fingerprints reject all certs and normal hostname PKI checks are bypassed.
- Test signals: `tlsutil_test.go` covers cert SAN/validity and fingerprint accept/reject.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/tlsutil/tlsutil.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/tlsutil/tlsutil_test.go -->
# sources/sync-backup/kopia/internal/tlsutil/tlsutil_test.go

- Purpose: Tests generated TLS certificates and fingerprint-based trust transport.
- Important APIs/types/functions: `TestGenerateServerCertificate`, `TestTransportTrustingSingleCertificate`.
- Control flow: Generates certs with IP/DNS names, checks SANs and validity window, computes SHA256 fingerprint, obtains a transport, and directly invokes `VerifyPeerCertificate` for matching and mismatching raw certs.
- State and persistence: Uses in-memory certificates only; file writing helpers are not covered.
- Dependencies and integration points: Uses `clock`, `crypto/sha256`, `http.Transport`, and `testify/require`.
- Risks and edge cases: Does not perform a real TLS handshake or test PEM file permissions.
- Test signals: Direct coverage for core TLS utility behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/tlsutil/tlsutil_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/uitask/uitask.go -->
# sources/sync-backup/kopia/internal/uitask/uitask.go

- Purpose: Defines UI task status/data and running-task behavior including cancellation, progress, counters, and in-memory JSON logs.
- Important APIs/types/functions: `Status`, `IsFinished`, `LogLevel`, `Info`, `runningTaskInfo`, `CurrentTaskID`, `OnCancel`, `cancel`, `ReportProgressInfo`, `ReportCounters`, `info`, `loggerForModule`, `uiLevelEncoder`, `addLogEntry`, `log`, `Write`, `Sync`.
- Control flow: Running tasks mutate their own state under a mutex, register cancel callbacks, transition to canceling, clone counters for reads, and collect zap JSON log entries while filtering noisy format logs and enforcing log count limits.
- State and persistence: In-memory task fields, counters, cancel callbacks, and bounded log slices; optional persistent file logging is coordinated in the manager.
- Dependencies and integration points: Integrates `zap`, `content.FormatLogModule`, and `repo/logging`.
- Risks and edge cases: Log filtering is byte-pattern-based, finished tasks ignore new log entries, and cancel callbacks run asynchronously.
- Test signals: `uitask_test.go` covers logs, counters, status, cancellation timing, retention, and summaries.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/uitask/uitask.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/uitask/uitask_counter.go -->
# sources/sync-backup/kopia/internal/uitask/uitask_counter.go

- Purpose: Defines JSON counter values and constructors for UI task counters with units/severity levels.
- Important APIs/types/functions: `CounterValue`, `BytesCounter`, `SimpleCounter`, `NoticeBytesCounter`, `NoticeCounter`, `WarningBytesCounter`, `WarningCounter`, `ErrorBytesCounter`, `ErrorCounter`.
- Control flow: Constructors return small value structs with optional `bytes` units and level strings.
- State and persistence: No state; values are embedded into task API responses.
- Dependencies and integration points: Used by upload/progress reporters and UI task JSON output.
- Risks and edge cases: Level strings are an implicit UI contract.
- Test signals: `uitask_test.go` asserts constructor output through reported counters.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/uitask/uitask_counter.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/uitask/uitask_manager.go -->
# sources/sync-backup/kopia/internal/uitask/uitask_manager.go

- Purpose: Manages lifecycle, lookup, cancellation, logs, summaries, and retention for UI-visible long-running tasks.
- Important APIs/types/functions: `Manager`, `Controller`, `TaskFunc`, `Run`, `ListTasks`, `WaitForTask`, `TaskSummary`, `TaskLog`, `GetTask`, `CancelTask`, `startTask`, `completeTask`, `NewManager`.
- Control flow: `Run` wraps context logging, starts a task, invokes the caller function synchronously, and completes the task. Lookup/list functions combine running and finished maps. Cancellation marks running tasks canceling and triggers callbacks. Completion records end time, final status, error message, and prunes oldest finished tasks.
- State and persistence: `Manager.mu` protects next ID, running map, and finished map. Logs are in memory unless `alsoLogToFile` adds the task logger to an existing persistent logger.
- Dependencies and integration points: Uses `clock`, `repo/logging`, and the `Controller` interface consumed by server snapshot/restore/maintenance tasks.
- Risks and edge cases: Lock ordering between manager and task mutexes must remain consistent; `WaitForTask` with negative wait uses an infinite loop interrupted only by context.
- Test signals: `uitask_test.go` directly exercises manager behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/uitask/uitask_manager.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/uitask/uitask_test.go -->
# sources/sync-backup/kopia/internal/uitask/uitask_test.go

- Purpose: Tests UI task manager behavior, logging, counters, retention, summaries, and cancellation ordering.
- Important APIs/types/functions: `TestUITask_withoutPersistentLogging`, `TestUITask_withPersistentLogging`, `testUITaskInternal`, `verifyTaskList`, `TestUITaskCancel_NonExistent`, `TestUITaskCancel_AfterOnCancel`, `TestUITaskCancel_BeforeOnCancel`, `verifyTaskLog`, `logText`, `mustFindTask`.
- Control flow: Tests run tasks synchronously, inspect running/completed lists, emit logs, verify format-log filtering and max log retention, report counters/progress, force failures, age out finished tasks, and test cancellation before/after callback registration.
- State and persistence: Uses in-memory manager state and an optional external log buffer for persistent logging mode.
- Dependencies and integration points: Integrates `logging`, `content.FormatLogModule`, `google/uuid`, `cmp`, and `testify/require`.
- Risks and edge cases: Cancellation tests use real sleeps and goroutines; persistent logging assertion is exact text.
- Test signals: Direct high-coverage test suite for `uitask`.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/uitask/uitask_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/units/units.go -->
# sources/sync-backup/kopia/internal/units/units.go

- Purpose: Formats byte sizes, rates, and counts into compact human-readable strings.
- Important APIs/types/functions: `BytesStringBase10`, `BytesStringBase2`, `BytesString`, `BytesPerSecondsString`, `Count`, `niceNumber`, `toDecimalUnitString`.
- Control flow: Values are scaled by 1000 or 1024 until below 0.9 of the next unit, formatted with one decimal place, and trimmed. `BytesString` selects base-2 formatting when `KOPIA_BYTES_STRING_BASE_2` parses true.
- State and persistence: Reads an environment variable; otherwise stateless.
- Dependencies and integration points: Used by notification templates and UI/reporting code.
- Risks and edge cases: Threshold choices intentionally produce values like `0.9 KB`; environment selection can make output process-dependent.
- Test signals: `units_test.go` covers many boundary cases and env selection.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/units/units.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/units/units_test.go -->
# sources/sync-backup/kopia/internal/units/units_test.go

- Purpose: Tests base-10/base-2 byte formatting and environment-controlled selection.
- Important APIs/types/functions: `base10Cases`, `base2Cases`, `TestBytesStringBase10`, `TestBytesStringBase2`, `TestBytesString_base2EnvFalse`, `TestBytesString_base2EnvTrue`.
- Control flow: Table tests iterate numeric boundaries from bytes through exabytes and assert exact formatted strings; env tests use `t.Setenv`.
- State and persistence: Environment variable is scoped by test helper cleanup.
- Dependencies and integration points: Uses `testify/require`.
- Risks and edge cases: Does not cover `BytesPerSecondsString` or `Count` directly, but shared scaling code is covered.
- Test signals: Direct coverage for core unit formatting.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/units/units_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/user/hash_password.go -->
# sources/sync-backup/kopia/internal/user/hash_password.go

- Purpose: Encodes generated password hashes into a base64 JSON payload suitable for profile import/set operations.
- Important APIs/types/functions: `passwordHash`, `HashPassword`, `decodeHashedPassword`, `validate`.
- Control flow: `HashPassword` generates a random salt, computes the default-version password hash, marshals version plus hash bytes to JSON, and base64-encodes it. Decoding reverses base64/JSON. Validation checks known algorithm version and salt+hash length.
- State and persistence: No direct repository writes; encoded output can be stored into `Profile`.
- Dependencies and integration points: Uses `computePasswordHash`, default hash version, crypto random source, and JSON/base64 encoding.
- Risks and edge cases: Encoded hashes are only as strong as the selected default algorithm; validation rejects unknown versions and malformed lengths.
- Test signals: `hash_password_test.go` covers encoding round trip and validation failures/success.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/user/hash_password.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/user/hash_password_test.go -->
# sources/sync-backup/kopia/internal/user/hash_password_test.go

- Purpose: Tests encoded password hash creation, decode, profile validation, and `passwordHash.validate`.
- Important APIs/types/functions: `TestHashPassword_encoding`, `TestPasswordHashValidate`.
- Control flow: Generates a random petname password, hashes/decodes it, constructs a profile, validates the password, then table-tests invalid versions and lengths.
- State and persistence: In-memory hash payloads only.
- Dependencies and integration points: Uses `golang-petname` and `testify/require`.
- Risks and edge cases: Random password content is non-deterministic but not security-sensitive.
- Test signals: Direct coverage for `hash_password.go`.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/user/hash_password_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/user/password_hashing_version.go -->
# sources/sync-backup/kopia/internal/user/password_hashing_version.go

- Purpose: Declares the default password hashing scheme for new user password hashes.
- Important APIs/types/functions: `defaultPasswordHashVersion`.
- Control flow: Declaration-only file selecting `ScryptHashVersion`.
- State and persistence: Compile-time constant affects newly generated/stored hashes.
- Dependencies and integration points: Used by `HashPassword`, `GetNewProfile`, and profile password setting.
- Risks and edge cases: Changing this constant affects future hashes but old hashes rely on stored versions.
- Test signals: User profile/hash tests exercise default behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/user/password_hashing_version.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/user/password_hashings.go -->
# sources/sync-backup/kopia/internal/user/password_hashings.go

- Purpose: Maps stored password hash versions to crypto derivation algorithm identifiers.
- Important APIs/types/functions: `getPasswordHashAlgorithm`.
- Control flow: Switches version `0` and `1` to scrypt, version `2` to PBKDF2, and errors for unknown versions.
- State and persistence: Version numbers are persisted in user profiles and encoded hash payloads.
- Dependencies and integration points: Must match algorithm constants registered by `internal/crypto`.
- Risks and edge cases: Unsupported versions make password validation return errors for otherwise well-formed hashes.
- Test signals: `password_hashings_test.go` checks crypto constant alignment, dummy hash, and salt compatibility.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/user/password_hashings.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/user/password_hashings_test.go -->
# sources/sync-backup/kopia/internal/user/password_hashings_test.go

- Purpose: Guards password hashing constants and salt/dummy hash invariants.
- Important APIs/types/functions: `TestPasswordHashingConstantMatchCryptoPackage`, `TestNonZeroDummyHash`, `TestSaltLengthIsSupported`.
- Control flow: Compares package algorithm strings to crypto package constants, checks dummy hash is non-zero, and derives hashes with both supported versions using the configured salt length.
- State and persistence: In-memory constants and derived hashes only.
- Dependencies and integration points: Integrates `internal/crypto`.
- Risks and edge cases: Does not benchmark algorithm cost; it is a compatibility and invariant test.
- Test signals: Direct coverage for version/algorithm mapping assumptions.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/user/password_hashings_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/user/user_manager.go -->
# sources/sync-backup/kopia/internal/user/user_manager.go

- Purpose: Manages user profile manifests in the repository.
- Important APIs/types/functions: `ManifestType`, `UsernameAtHostnameLabel`, `ErrUserNotFound`, `ErrUserAlreadyExists`, `LoadProfileMap`, `ListUserProfiles`, `GetUserProfile`, `GetNewProfile`, `ValidateUsername`, `SetUserProfile`, `DeleteUserProfile`.
- Control flow: Functions find manifests by type/name labels, dedupe latest entries, reuse cached profiles by manifest ID, load profiles, validate lowercase `user@hostname`, replace manifests for writes, and delete all matching manifests.
- State and persistence: User profiles persist as repository manifests labeled `type=user` and `username=<username@hostname>`.
- Dependencies and integration points: Integrates `repo`, `manifest`, `maps`, `slices`, and username validation used by auth/user management flows.
- Risks and edge cases: Username validation is restrictive and lowercase-only; cache reuse depends on stable manifest IDs.
- Test signals: `user_manager_test.go` covers create/update/delete, missing user, duplicate new profile, and username validation.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/user/user_manager.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/user/user_manager_test.go -->
# sources/sync-backup/kopia/internal/user/user_manager_test.go

- Purpose: Tests repository-backed user profile lifecycle and username validation.
- Important APIs/types/functions: `TestUserManager`, `TestGetNewProfile`, `TestValidateUsername_Valid`, `TestValidateUsername_Invalid`.
- Control flow: Uses a repotesting environment, sets profiles, reads updated hashes, deletes users, checks not-found errors, creates passworded new profiles, and table-tests valid/invalid username strings.
- State and persistence: Uses repository manifests in a test repository.
- Dependencies and integration points: Integrates `repotesting`, `internal/user`, and `testify/require`.
- Risks and edge cases: Does not test `LoadProfileMap` cache reuse or concurrent writers.
- Test signals: Direct coverage for `user_manager.go`.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/user/user_manager_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/user/user_profile.go -->
# sources/sync-backup/kopia/internal/user/user_profile.go

- Purpose: Defines user profile data and public password APIs.
- Important APIs/types/functions: `unsetDefaultHashVersion`, `ScryptHashVersion`, `Pbkdf2HashVersion`, `Profile`, `SetPassword`, `SetPasswordHash`, `IsValidPassword`.
- Control flow: `SetPassword` delegates to salted hash generation. `SetPasswordHash` decodes and validates an encoded hash before installing it. `IsValidPassword` validates against stored hash, or computes against a dummy hash for nil profiles to reduce account-existence timing leakage.
- State and persistence: `Profile` fields are JSON-serializable repository manifest content; `ManifestID` is in-memory only.
- Dependencies and integration points: Integrates manifest IDs and password hashing helpers.
- Risks and edge cases: Nil-profile dummy hashing assumes dummy hash length/version remain valid; invalid stored hash length returns false without error.
- Test signals: `user_profile_test.go` covers valid/invalid passwords, algorithm mismatch, unset version, nil profile, and invalid hash bytes.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/user/user_profile.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/user/user_profile_pw_hash.go -->
# sources/sync-backup/kopia/internal/user/user_profile_pw_hash.go

- Purpose: Implements salted password hash derivation and constant-time password verification.
- Important APIs/types/functions: `dummyHashThatNeverMatchesAnyPassword`, `initDummyHash`, `setPassword`, `computePasswordHash`, `isValidPassword`.
- Control flow: Password setting generates random salt and stores salt+derived key. Hash computation maps version to algorithm, derives a fixed-length key, and prefixes salt. Validation checks payload length, recomputes with stored salt, and uses `subtle.ConstantTimeCompare`.
- State and persistence: Stores salt+hash bytes in the caller's `Profile`; dummy hash is process-global read-only state.
- Dependencies and integration points: Uses `internal/crypto` password key derivation and version mapping.
- Risks and edge cases: Unknown hash versions return errors during recomputation; invalid lengths return false without hashing.
- Test signals: Covered by user profile and hashing tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/user/user_profile_pw_hash.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/user/user_profile_test.go -->
# sources/sync-backup/kopia/internal/user/user_profile_test.go

- Purpose: Tests profile password setting and validation behavior.
- Important APIs/types/functions: `TestUserProfile`, `TestBadPasswordHashVersionWithSCrypt`, `TestBadPasswordHashVersionWithPbkdf2`, `TestUnsetPasswordHashVersion`, `TestNilUserProfile`, `TestInvalidPasswordHash`.
- Control flow: Tests set passwords under different versions, validate correct and incorrect passwords, mutate version fields to prove mismatch failure, verify version zero maps to scrypt, and validate nil/invalid-hash behavior.
- State and persistence: In-memory profiles only.
- Dependencies and integration points: Uses `internal/user` external test package and `testify/require`.
- Risks and edge cases: Does not measure timing resistance; only functional behavior.
- Test signals: Direct coverage for `user_profile.go` and `user_profile_pw_hash.go`.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/user/user_profile_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/volumesizeinfo/volume_size_info.go -->
# sources/sync-backup/kopia/internal/volumesizeinfo/volume_size_info.go

- Purpose: Exposes cross-platform volume size information API.
- Important APIs/types/functions: `VolumeSizeInfo`, `GetVolumeSizeInfo`.
- Control flow: Validates non-empty mount point, delegates to platform implementation, and wraps errors with mount point context.
- State and persistence: Reads filesystem/volume metadata only.
- Dependencies and integration points: Used by storage/capacity reporting code; delegates to build-tagged platform files.
- Risks and edge cases: File count semantics are platform-dependent, especially Windows.
- Test signals: No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/volumesizeinfo/volume_size_info.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/volumesizeinfo/volume_size_info_common.go -->
# sources/sync-backup/kopia/internal/volumesizeinfo/volume_size_info_common.go

- Purpose: Implements volume size information for non-OpenBSD, non-Windows Unix platforms.
- Important APIs/types/functions: `getPlatformVolumeSizeInfo`.
- Control flow: Calls `unix.Statfs`, computes total bytes, used bytes, and used file count from block/file counters.
- State and persistence: Reads filesystem metadata only.
- Dependencies and integration points: Build-constrained to `!openbsd && !windows`; uses `x/sys/unix`.
- Risks and edge cases: Uses unsigned arithmetic on statfs counters; unusual filesystems may report unexpected values.
- Test signals: No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/volumesizeinfo/volume_size_info_common.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/volumesizeinfo/volume_size_info_openbsd.go -->
# sources/sync-backup/kopia/internal/volumesizeinfo/volume_size_info_openbsd.go

- Purpose: Implements OpenBSD volume size information using OpenBSD statfs field names.
- Important APIs/types/functions: `getPlatformVolumeSizeInfo`.
- Control flow: Calls `unix.Statfs` and computes size/file counts from `F_blocks`, `F_bsize`, `F_bfree`, `F_files`, and `F_ffree`.
- State and persistence: Reads filesystem metadata only.
- Dependencies and integration points: Build-constrained to OpenBSD.
- Risks and edge cases: Separate field names must remain aligned with OpenBSD syscall structs.
- Test signals: No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/volumesizeinfo/volume_size_info_openbsd.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/volumesizeinfo/volume_size_info_windows.go -->
# sources/sync-backup/kopia/internal/volumesizeinfo/volume_size_info_windows.go

- Purpose: Implements Windows volume size information using `GetDiskFreeSpaceEx`.
- Important APIs/types/functions: `getPlatformVolumeSizeInfo`.
- Control flow: Converts mount point to UTF-16, fills capacity/free fields, returns total, used, and `math.MaxInt64` as a sentinel file count.
- State and persistence: Reads volume metadata only.
- Dependencies and integration points: Build-constrained to Windows; uses `x/sys/windows` and `repo/blob.Capacity`.
- Risks and edge cases: File count is not measurable and should not be treated as exact.
- Test signals: No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/volumesizeinfo/volume_size_info_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/wcmatch/rune_scanner.go -->
# sources/sync-backup/kopia/internal/wcmatch/rune_scanner.go

- Purpose: Provides rune scanning primitives for wildcard parsing and matching.
- Important APIs/types/functions: `runeScanner`, `newRuneScanner`, `peek`, `read`, `eos`, `indexOf`.
- Control flow: Scanner stores rune slice and position, can peek relative indexes with optional lowercase conversion, read and advance, detect end, and locate a rune from current position.
- State and persistence: In-memory scanner position only.
- Dependencies and integration points: Used by `NewWildcardMatcher` and `doMatch`; depends on `unicode`.
- Risks and edge cases: Case folding only lowercases uppercase runes and does not implement full Unicode case folding equivalence.
- Test signals: Covered indirectly by `wcmatch_test.go`.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/wcmatch/rune_scanner.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/wcmatch/tokens.go -->
# sources/sync-backup/kopia/internal/wcmatch/tokens.go

- Purpose: Defines token types used by wildcard parser and matcher.
- Important APIs/types/functions: `token`, `tokenAnyChar`, `tokenDirSep`, `tokenStar`, `tokenRune`, `tokenSeq`, `seqToken`, `seqTokenRuneRange`, `seqTokenRune`, `seqTokenClass`, `isStar`, `isDirSep`.
- Control flow: Token structs implement `String` and sequence tokens implement `match`; utility functions classify tokens during recursive matching.
- State and persistence: Token values are immutable in-memory parse results.
- Dependencies and integration points: Used by `wcmatch.go`; depends on `fmt` and `strings`.
- Risks and edge cases: String forms are useful for debugging but not a complete re-serialization guarantee.
- Test signals: Indirectly covered by wildcard parser/matcher tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/wcmatch/tokens.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/wcmatch/wcmatch.go -->
# sources/sync-backup/kopia/internal/wcmatch/wcmatch.go

- Purpose: Implements .gitignore-style wildcard matcher parsing and path matching.
- Important APIs/types/functions: `WildcardMatcher`, `Options`, `Option`, `IgnoreCase`, `BaseDir`, `Pattern`, `Negated`, `Options`, `NewWildcardMatcher`, `Match`, `doMatch`, `indexOf`.
- Control flow: Parser trims unescaped whitespace, handles negation/rooting/base directory, implicit `**/`, directory-only suffixes, escapes, stars, sequences, ranges, and POSIX-like character classes. Matching recursively consumes tokens and path runes with abort states for `*`/`**` backtracking.
- State and persistence: Matchers store original pattern, parsed tokens, options, and flags only.
- Dependencies and integration points: Used by path filtering/exclusion behavior; depends on `unicode`, `strings`, and `pkg/errors`.
- Risks and edge cases: Recursive matching can be expensive for adversarial patterns; escape/class/rooting rules are subtle.
- Test signals: `wcmatch_test.go` has broad table coverage for base dirs, case sensitivity, recursion, directories, negation, whitespace, errors, and character classes.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/wcmatch/wcmatch.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/wcmatch/wcmatch_test.go -->
# sources/sync-backup/kopia/internal/wcmatch/wcmatch_test.go

- Purpose: Tests wildcard matching semantics and parser error handling.
- Important APIs/types/functions: `wcCase`, `TestMatchWithBaseDir`, `TestMatch`, `TestErrorCases`, `TestCharacterClasses`, `testHelper`.
- Control flow: Table tests construct matchers with case-sensitive and case-insensitive options, normalize trailing slash directory markers, and compare expected matches. Error tests assert invalid patterns return errors and nil matchers.
- State and persistence: In-memory patterns and paths only.
- Dependencies and integration points: Directly exercises `NewWildcardMatcher` and `Match`.
- Risks and edge cases: Large table coverage is good, but performance/adversarial recursion is not measured.
- Test signals: Direct comprehensive coverage for `wcmatch`.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/wcmatch/wcmatch_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/webdavmount/webdavmount.go -->
# sources/sync-backup/kopia/internal/webdavmount/webdavmount.go

- Purpose: Adapts Kopia snapshot filesystem entries to a read-only WebDAV filesystem.
- Important APIs/types/functions: `webdavFile`, `webdavDir`, `webdavFileInfo`, `webdavFS`, `OpenFile`, `Stat`, `findEntry`, `removeEmpty`, `WebDAVFS`.
- Control flow: `OpenFile` resolves a slash path through `findEntry`, opens directories with iterators and files with lazy readers, rejects write/mkdir/remove/rename operations, skips symlinks in directory reads, and wraps entries as `os.FileInfo`.
- State and persistence: Keeps lazy file reader state under a mutex and directory iterator state; no writes are allowed.
- Dependencies and integration points: Integrates `fs`, `x/net/webdav`, and Kopia logging; used by mount/server paths.
- Risks and edge cases: Symlinks are skipped with a one-time global log; read-only errors must match WebDAV client expectations.
- Test signals: No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/webdavmount/webdavmount.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/workshare/workshare_pool.go -->
# sources/sync-backup/kopia/internal/workshare/workshare_pool.go

- Purpose: Implements a generic fixed worker pool for opportunistic shared work.
- Important APIs/types/functions: `ProcessFunc`, `workItem`, `Pool`, `ActiveWorkers`, `NewPool`, `Close`.
- Control flow: `NewPool` creates unbuffered work channel, closed channel, semaphore, and worker goroutines. Workers receive items, increment active count, process, decrement, release semaphore token, and signal the item wait group. `Close` closes the pool and waits workers out.
- State and persistence: In-memory goroutines, channels, atomics, and wait group only.
- Dependencies and integration points: Paired with `AsyncGroup` in `workshare_waitgroup.go`.
- Risks and edge cases: A semaphore token is expected before sending work; misuse can deadlock or panic through the higher-level API.
- Test signals: `workshare_test.go` covers tree summing, worker counts, invalid usage, and benchmark path.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/workshare/workshare_pool.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/workshare/workshare_test.go -->
# sources/sync-backup/kopia/internal/workshare/workshare_test.go

- Purpose: Tests workshare pool and async group using a recursive tree-sum workload.
- Important APIs/types/functions: `treeNode`, `buildTree`, `computeTreeSumRequest`, `dispatchComputeTreeSumRequest`, `computeTreeSum`, `TestComputeTreeSum10`, `TestComputeTreeSum1`, `TestComputeTreeSum0`, `TestComputeTreeSumNegative`, `TestDisallowed_DoubleWait`, `TestDisallowed_WaitAfterClose`, `TestDisallowed_UseAfterPoolClose`, `BenchmarkComputeTreeSum`.
- Control flow: Recursive work opportunistically shares child traversal when capacity is available, waits for async requests, and sums results. Panic tests verify invalid `AsyncGroup` and closed-pool usage.
- State and persistence: In-memory tree, worker pool, and async request structs.
- Dependencies and integration points: Uses `testify/require`.
- Risks and edge cases: Does not test close racing with active producers beyond explicit closed-pool misuse.
- Test signals: Direct coverage for workshare pool/group semantics.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/workshare/workshare_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/workshare/workshare_waitgroup.go -->
# sources/sync-backup/kopia/internal/workshare/workshare_waitgroup.go

- Purpose: Provides `AsyncGroup`, a low-allocation coordination wrapper for workshare pool tasks.
- Important APIs/types/functions: `AsyncGroup`, `Wait`, `Close`, `RunAsync`, `CanShareWork`.
- Control flow: `CanShareWork` reserves pool capacity by sending a semaphore token, and callers must then call `RunAsync` once to send the work item. `Wait` waits once and returns request objects; `Close` ensures waiting happened.
- State and persistence: In-memory wait group pointer, request slice, and lifecycle flags.
- Dependencies and integration points: Works with `Pool` and `ProcessFunc`.
- Risks and edge cases: API has strict usage contracts: double wait, wait after close, use after pool close, or failing to run after capacity reservation can panic or leak capacity.
- Test signals: `workshare_test.go` covers normal recursion and invalid usage panics.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/workshare/workshare_waitgroup.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/zaplogutil/zaplogutil.go -->
# sources/sync-backup/kopia/internal/zaplogutil/zaplogutil.go

- Purpose: Provides reusable zap logging utilities and Kopia console encoder.
- Important APIs/types/functions: `PreciseLayout`, `PreciseTimeEncoder`, `Clock`, `TimezoneAdjust`, `NewStdConsoleEncoder`, `StdConsoleEncoderConfig`, `stdConsoleEncoder`, `Clone`, `EncodeEntry`.
- Control flow: Time helpers wrap zap encoders/clocks. The console encoder builds a line with optional time, level, logger name, message, and structured JSON fields, then appends newline.
- State and persistence: Uses a global zap buffer pool; no durable state.
- Dependencies and integration points: Used by test logging and application logging configuration; integrates `clock`, `zapcore`, and `zap/buffer`.
- Risks and edge cases: Colored output assumes ANSI support; structured field output depends on JSON encoder behavior.
- Test signals: Indirectly covered through logging tests/usages; no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/zaplogutil/zaplogutil.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/main.go -->
# sources/sync-backup/kopia/main.go

- Purpose: Main entrypoint for the Kopia CLI.
- Important APIs/types/functions: `usageTemplate`, `main`.
- Control flow: Constructs the CLI app and kingpin application, installs version/build strings, attaches logfile flags, configures error/usage writers and custom usage template, attaches commands, and parses `os.Args[1:]`.
- State and persistence: Process-level CLI configuration only; persistent effects are delegated to invoked commands.
- Dependencies and integration points: Integrates `cli`, `internal/logfile`, `repo` build metadata, and `kingpin`.
- Risks and edge cases: Usage template is a compatibility surface with kingpin templates and command metadata.
- Test signals: No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/notification/notification_send.go -->
# sources/sync-backup/kopia/notification/notification_send.go

- Purpose: Sends Kopia notifications through local repository-configured senders or remote server notification APIs.
- Important APIs/types/functions: `AdditionalSenders`, `TemplateArgs`, `Severity`, severity constants, `SeverityToNumber`, `SeverityToString`, `notificationSendersFromRepo`, `Send`, `SendInternal`, `MakeTemplateArgs`, `SendTo`, `SendTestNotification`.
- Control flow: `Send` forwards JSON event args to remote repositories when possible; otherwise `SendInternal` loads sender profiles by severity, appends global additional senders, and calls `SendTo`. `SendTo` resolves and parses a template, executes it with build/host/event args, parses headers/body into a sender message, sets severity, and sends.
- State and persistence: Profiles/templates persist in repository manifests; `AdditionalSenders` is global process state; event args serialize to JSON for remote notification transport.
- Dependencies and integration points: Integrates `notifydata`, `notifyprofile`, `notifytemplate`, `sender`, `repo.RemoteNotifications`, and logging.
- Risks and edge cases: `Send` logs and suppresses errors; global `AdditionalSenders` can affect tests/plugins; template parse/execute errors abort a sender.
- Test signals: Server integration test exercises remote notifications; template tests exercise rendering but sender selection has limited direct tests here.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/notification/notification_send.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/notification/notifydata/doc.go -->
# sources/sync-backup/kopia/notification/notifydata/doc.go

- Purpose: Provides package documentation for notification event argument data structures.
- Important APIs/types/functions: package declaration only.
- Control flow: No runtime control flow.
- State and persistence: No state.
- Dependencies and integration points: Package is consumed by `notification` and remote notification unmarshalling.
- Risks and edge cases: None in this file.
- Test signals: Behavior lives in sibling files and tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/notification/notifydata/doc.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/notification/notifydata/empty.go -->
# sources/sync-backup/kopia/notification/notifydata/empty.go

- Purpose: Defines the empty notification event payload.
- Important APIs/types/functions: `EmptyEventData`, `EventArgsType`.
- Control flow: `EventArgsType` returns the gRPC enum for empty arguments.
- State and persistence: Stateless JSON object payload.
- Dependencies and integration points: Used by test notifications and remote notification transport.
- Risks and edge cases: Enum value must stay synchronized with `UnmarshalEventArgs`.
- Test signals: `empty_test.go` round-trips the payload.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/notification/notifydata/empty.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/notification/notifydata/empty_test.go -->
# sources/sync-backup/kopia/notification/notifydata/empty_test.go

- Purpose: Tests empty notification payload JSON/gRPC type round trip.
- Important APIs/types/functions: `TestEmptyEventInfo`.
- Control flow: Delegates to shared `testRoundTrip` with `EmptyEventData`.
- State and persistence: In-memory JSON only.
- Dependencies and integration points: Uses external `notifydata_test` package.
- Risks and edge cases: Minimal payload test only.
- Test signals: Direct coverage for `empty.go`.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/notification/notifydata/empty_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/notification/notifydata/error_info.go -->
# sources/sync-backup/kopia/notification/notifydata/error_info.go

- Purpose: Defines structured notification payloads for operation errors.
- Important APIs/types/functions: `ErrorInfo`, `EventArgsType`, `StartTimestamp`, `EndTimestamp`, `Duration`, `NewErrorInfo`.
- Control flow: Accessors truncate start/end times to seconds and compute duration. Constructor captures operation metadata plus both simple and detailed error strings.
- State and persistence: JSON-serializable event payload; no repository persistence by itself.
- Dependencies and integration points: Used by maintenance/generic error notifications and template rendering.
- Risks and edge cases: Detailed error uses `%+v`; detail richness depends on wrapped error implementations.
- Test signals: `error_info_test.go` covers constructor, timestamps, duration, and round trip.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/notification/notifydata/error_info.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/notification/notifydata/error_info_test.go -->
# sources/sync-backup/kopia/notification/notifydata/error_info_test.go

- Purpose: Tests `ErrorInfo` construction, timestamp helpers, duration, and event round trip.
- Important APIs/types/functions: `TestNewErrorInfo`.
- Control flow: Creates fixed start/end times and an error, checks all fields and truncated helper methods, then calls shared JSON/gRPC round trip.
- State and persistence: In-memory payload only.
- Dependencies and integration points: Uses `clock`, `testify/require`, and `notifydata`.
- Risks and edge cases: Uses a simple error, so wrapped stack/detail formatting is not covered.
- Test signals: Direct coverage for `error_info.go`.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/notification/notifydata/error_info_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/notification/notifydata/multi_snapshot_status.go -->
# sources/sync-backup/kopia/notification/notifydata/multi_snapshot_status.go

- Purpose: Defines snapshot-result notification payloads and aggregate status helpers.
- Important APIs/types/functions: `ManifestWithError`, `StartTimestamp`, `EndTimestamp`, `TotalSize`, `TotalSizeDelta`, `TotalFiles`, `TotalFilesDelta`, `TotalDirs`, `TotalDirsDelta`, `Duration`, status constants, `StatusCode`, `MultiSnapshotStatus`, `EventArgsType`, `OverallStatusCode`, `OverallStatus`.
- Control flow: Per-manifest methods derive metrics from root entries and optional previous snapshots. Status codes prioritize top-level error, incomplete reason, fatal summary errors, ignored errors, then success. Aggregate status reports fatal/warning/success and user-facing text.
- State and persistence: JSON event payload embeds snapshot manifests; persistence is notification transport/template rendering only.
- Dependencies and integration points: Integrates `grpcapi`, `fs`, and `snapshot`; consumed by snapshot notification templates.
- Risks and edge cases: Overall status code intentionally ignores incomplete as fatal/warning; delta methods return fallback values when summaries are missing.
- Test signals: `multi_snapshot_status_test.go` covers status text/codes, metrics, deltas, duration, and round trip.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/notification/notifydata/multi_snapshot_status.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/notification/notifydata/multi_snapshot_status_test.go -->
# sources/sync-backup/kopia/notification/notifydata/multi_snapshot_status_test.go

- Purpose: Tests snapshot notification metrics, deltas, statuses, and JSON round trips.
- Important APIs/types/functions: `TestOverallStatus`, `TestStatusCode`, `TestManifestWithErrorMethods`, `TestTotalSizeDelta`, `TestTotalFilesDelta`, `TestTotalDirsDelta`, `TestTotalFiles`, `TestTotalDirs`, `TestTotalSize`.
- Control flow: Table tests construct manifests with root summaries, previous manifests, incomplete reasons, and top-level errors, then assert status codes/text and derived numeric values.
- State and persistence: In-memory snapshot manifest payloads only.
- Dependencies and integration points: Uses `fs`, `clock`, `snapshot`, and `testify/require`.
- Risks and edge cases: Strong coverage of helper semantics; template rendering is tested separately.
- Test signals: Direct coverage for `multi_snapshot_status.go`.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/notification/notifydata/multi_snapshot_status_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/notification/notifydata/typed_event_args.go -->
# sources/sync-backup/kopia/notification/notifydata/typed_event_args.go

- Purpose: Defines the notification event argument interface and JSON unmarshal dispatch by gRPC enum.
- Important APIs/types/functions: `TypedEventArgs`, `UnmarshalEventArgs`.
- Control flow: Switches on `NotificationEventArgType`, allocates the matching payload struct, unmarshals JSON into it, and returns unsupported-type errors otherwise.
- State and persistence: In-memory JSON decoding for remote notification transport.
- Dependencies and integration points: Must stay aligned with `EmptyEventData`, `MultiSnapshotStatus`, `ErrorInfo`, and gRPC enum definitions.
- Risks and edge cases: Unknown enum values fail; adding a new payload type requires updating this switch and tests.
- Test signals: `typed_event_args_test.go` iterates known enum values and round-trips payloads.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/notification/notifydata/typed_event_args.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/notification/notifydata/typed_event_args_test.go -->
# sources/sync-backup/kopia/notification/notifydata/typed_event_args_test.go

- Purpose: Tests notification event argument dispatch and shared JSON round-trip behavior.
- Important APIs/types/functions: `TestUnmarshalEventArgs`, `testRoundTrip`.
- Control flow: Iterates gRPC enum names except unknown, unmarshals `{}` for each supported type, and round-trips payloads through JSON plus `EventArgsType`.
- State and persistence: In-memory JSON only.
- Dependencies and integration points: Integrates `grpcapi` enum map and all typed event payloads.
- Risks and edge cases: Empty JSON validates type dispatch but not all populated field combinations.
- Test signals: Direct coverage for `typed_event_args.go` and shared support for other notifydata tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/notification/notifydata/typed_event_args_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/notification/notifyprofile/notification_profile.go -->
# sources/sync-backup/kopia/notification/notifyprofile/notification_profile.go

- Purpose: Manages repository-stored notification sender profiles.
- Important APIs/types/functions: `Config`, `Summary`, `ListProfiles`, `ErrNotFound`, `GetProfile`, `SaveProfile`, `DeleteProfile`, `labelsForProfileName`.
- Control flow: List finds all notification profile manifests and loads each config. Get finds manifests for one profile and loads latest. Save replaces manifests with matching labels. Delete removes all matching manifests.
- State and persistence: Profiles persist as repository manifests with type `notificationProfile` and `profile` labels.
- Dependencies and integration points: Integrates `sender.MethodConfig`, repository manifests, notification send selection, and logging.
- Risks and edge cases: Profile name validation is not enforced here; malformed sender configs are handled later by sender construction.
- Test signals: Indirectly exercised by server remote notification test; no direct profile unit test in this subset.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/notification/notifyprofile/notification_profile.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/notification/notifytemplate/embeddedtemplate.go -->
# sources/sync-backup/kopia/notification/notifytemplate/embeddedtemplate.go

- Purpose: Embeds built-in notification templates and defines template helper functions/options.
- Important APIs/types/functions: `embedded`, `TestNotification`, `Options`, `formatCount`, `functions`, `DefaultOptions`, `GetEmbeddedTemplate`, `SupportedTemplates`, `ParseTemplate`.
- Control flow: Embedded FS provides `.html` and `.txt` templates. `functions` installs byte/count delta helpers, HTML delta helpers, snapshot sorting, and timezone-aware time formatting. `ParseTemplate` attaches helpers before parsing text.
- State and persistence: Built-in templates are embedded at compile time; rendering options are caller-provided.
- Dependencies and integration points: Integrates `units`, `notifydata`, `text/template`, and notification sending.
- Risks and edge cases: Template helper names are part of repository override compatibility; default timezone uses `time.Local`.
- Test signals: `notifytemplate_test.go` executes generic-error and snapshot-report templates against golden files.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/notification/notifytemplate/embeddedtemplate.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/notification/notifytemplate/notifytemplate_test.go -->
# sources/sync-backup/kopia/notification/notifytemplate/notifytemplate_test.go

- Purpose: Golden-tests embedded notification template rendering.
- Important APIs/types/functions: `defaultTestOptions`, `altTestOptions`, `TestNotifyTemplate_generic_error`, `TestNotifyTemplate_snapshot_report`, `TestNotifyTemplate_snapshot_report_single_success`, `verifyTemplate`.
- Control flow: Tests build representative notification args, force event time/hostname, render text/html templates under default and alternate timezone/format options, compare to expected files, and remove actual files on success.
- State and persistence: Writes `.actual` golden-output files under testdata, removing them only when output matches.
- Dependencies and integration points: Integrates `notification.MakeTemplateArgs`, `notifydata`, `notifytemplate`, `fs`, and `snapshot`.
- Risks and edge cases: Failed tests leave actual files by design; output comparisons are exact and sensitive to template formatting.
- Test signals: Direct coverage for embedded templates and helper functions used by rendering.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/notification/notifytemplate/notifytemplate_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/notification/notifytemplate/repotemplate.go -->
# sources/sync-backup/kopia/notification/notifytemplate/repotemplate.go

- Purpose: Stores, lists, resolves, and deletes notification template overrides in repository manifests.
- Important APIs/types/functions: `ManifestType`, `TemplateManifest`, `Info`, `ResolveTemplate`, `GetTemplate`, `ListTemplates`, `SetTemplate`, `ResetTemplate`, `labelsFor`.
- Control flow: Resolution checks profile-specific override, generic override, then embedded template. Get loads latest matching manifest. List merges embedded templates and repository overrides filtered by prefix. Set replaces matching manifests; reset deletes matching overrides.
- State and persistence: Template overrides persist as repository manifests with type `notificationTemplate` and `template` labels.
- Dependencies and integration points: Used by notification senders before parsing/executing templates; integrates `repo`, `manifest`, and embedded template lookup.
- Risks and edge cases: List order is map-derived and not sorted here; template names are label values and lack validation in this file.
- Test signals: Rendering tests cover embedded templates; repository override behavior is not directly tested in this subset.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/notification/notifytemplate/repotemplate.go -->
