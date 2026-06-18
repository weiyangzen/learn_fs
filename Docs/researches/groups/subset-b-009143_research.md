# subset-b-009143 Research

Grouped research for `subset-b-009143`. Each section preserves the source path in its title and is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/metrics/metrics_timeseries_timeres_test.go -->
# sources/sync-backup/kopia/internal/metrics/metrics_timeseries_timeres_test.go

Purpose: verifies Kopia metric time-bucket resolution functions for day, week, quarter, and year boundaries.

Important APIs/types/functions: `TestTimeResolutions`, helper constructors `dayOf`/`monthOf`, and exported metric functions `TimeResolutionByDay`, `TimeResolutionByWeekStartingSunday`, `TimeResolutionByWeekStartingMonday`, `TimeResolutionByQuarter`, and `TimeResolutionByYear`.

Control flow: table-driven cases compute expected start and exclusive end; each case checks exact input, period start, last moment before period end, and midpoint all resolve to the same bucket.

State and persistence behavior: no persistent state; test is deterministic around fixed UTC dates.

Dependencies and integration points: uses `testify/require` and the public `internal/metrics` package, acting as regression coverage for time-series aggregation.

Risks and test signals: protects off-by-one and week-start regressions. It does not cover DST/local time zones, leap years, or all quarter boundaries.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/metrics/metrics_timeseries_timeres_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/metrics/prom_cache.go -->
# sources/sync-backup/kopia/internal/metrics/prom_cache.go

Purpose: caches Prometheus counter and histogram vectors by metric name so repeated metric observations reuse registered collectors.

Important APIs/types/functions: `getPrometheusCounter`, `getPrometheusHistogram`, generic helpers `mapKeys` and `mapValues`, package globals `promCounters`, `promHistograms`, `promCacheMutex`, and constants for Kopia metric naming.

Control flow: each getter locks the global cache, looks up a `CounterVec` or `HistogramVec` by `opts.Name`, lazily registers it via `promauto`, stores it, and returns a child collector with label values derived from the provided map.

State and persistence behavior: process-global in-memory collector caches persist for the lifetime of the process and are synchronized by a mutex.

Dependencies and integration points: integrates with `prometheus/client_golang`, Go `maps` and `slices`, and the rest of Kopia metrics emission.

Risks and test signals: map key/value iteration is not explicitly sorted, so label names and values can become mismatched if iteration orders differ. Tests should exercise multiple labels, repeated names, and concurrent metric creation.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/metrics/prom_cache.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/mockfs/mockfs.go -->
# sources/sync-backup/kopia/internal/mockfs/mockfs.go

Purpose: implements an in-memory `fs` tree for tests, including directories, files, symlinks, device metadata, and entries that intentionally return errors.

Important APIs/types/functions: `Directory`, `File`, `Symlink`, `ErrorEntry`, `ReaderSeekerCloser`, `NewDirectory`, `NewFile`, `AddFile*`, `AddDir*`, `AddSymlink`, `Subdir`, `Remove`, `FailReaddir`, `OnReaddir`, `Child`, `Iterate`, `Open`, and `Resolve`.

Control flow: add methods resolve slash-separated child paths, create typed entries with `DefaultModTime`, append and sort children, and expose `fs.Directory` iteration through `fs.StaticIterator`. File open invokes a source factory to support dynamic content or injected read failures. Symlink resolution starts from parent or root for absolute targets and follows mock Unix-style separators.

State and persistence behavior: all state is in memory: parent pointers, sorted child slices, file source closures, readdir callbacks, and stored device/owner metadata. There is no locking, so callers should treat it as test-local.

Dependencies and integration points: satisfies Kopia `fs.Directory`, `fs.File`, `fs.Symlink`, and `fs.ErrorEntry` interfaces and is used by snapshot, upload, restore, mount, and policy tests.

Risks and test signals: `resolveSubdir("..")` assumes a parent exists, duplicate names are not rejected, file `SetContents` does not update size, and symlink target indexing assumes non-empty target. Useful tests cover ordering, nested path resolution, injected errors, absolute/relative symlinks, and metadata propagation.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/mockfs/mockfs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/mount/mount.go -->
# sources/sync-backup/kopia/internal/mount/mount.go

Purpose: defines the platform-neutral mount control contract and user-facing mount options.

Important APIs/types/functions: `Controller` exposes `Unmount`, `MountPath`, and `Done`; `Options` carries `FuseAllowOther`, `FuseAllowNonEmptyMount`, and `PreferWebDAV`; package `log` is the mount logger.

Control flow: no runtime logic here; build-tagged platform files implement `Directory` and return concrete controllers that satisfy this interface.

State and persistence behavior: no state is held directly. Concrete controllers own mount lifecycle state and temporary mount cleanup.

Dependencies and integration points: consumed by server mount APIs and command code that need an abstract controller independent of FUSE, WebDAV, or Windows `net use`.

Risks and test signals: interface stability matters because server-side mount bookkeeping stores `mount.Controller` values. Tests should use fake controllers and platform-specific integration tests for unmount/done semantics.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/mount/mount.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/mount/mount_fuse.go -->
# sources/sync-backup/kopia/internal/mount/mount_fuse.go

Purpose: implements POSIX non-FreeBSD/OpenBSD mounting through go-fuse, with optional fallback to WebDAV when requested.

Important APIs/types/functions: `Options.toFuseMountOptions`, `Directory`, `fuseController`, `Unmount`, `MountPath`, and `Done`; package `cacheTimeout` controls FUSE entry/attribute/negative cache durations.

Control flow: `Directory` creates a temporary directory for mount point `*`, routes to `newPosixWedavController` when `PreferWebDAV` is set, otherwise wraps the Kopia `fs.Directory` in a FUSE node and calls `gofusefs.Mount`. A goroutine waits on the FUSE server and closes `done`.

State and persistence behavior: controller stores mount path, FUSE server, done channel, and whether the mount point was temporary. Unmount calls FUSE unmount and removes temp directory.

Dependencies and integration points: uses `go-fuse`, `internal/fusemount`, `fs.Directory`, and environment variable `KOPIA_DEBUG_FUSE`.

Risks and test signals: temp directory cleanup only runs after successful unmount; mount option support is OS/FUSE-version sensitive. Integration tests need real FUSE availability, option propagation, `PreferWebDAV`, and temporary mount cleanup.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/mount/mount_fuse.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/mount/mount_net_use.go -->
# sources/sync-backup/kopia/internal/mount/mount_net_use.go

Purpose: Windows implementation that exposes a WebDAV server as a drive letter via `net use`.

Important APIs/types/functions: `Directory`, `netUse`, `netUseMount`, `netUseUnmount`, `isWindowsDrive`, `isValidWindowsDriveOrAsterisk`, and `netuseController`.

Control flow: validates drive letter or `*`, starts a local WebDAV controller, invokes `net use` to map the URL, parses localized output for an assigned drive when `*` was requested, and returns a controller that unmaps the drive before shutting down WebDAV.

State and persistence behavior: the persistent OS state is a Windows drive mapping; in-process state is the wrapped WebDAV controller and selected drive letter.

Dependencies and integration points: depends on `exec.CommandContext`, Windows `net use`, `DirectoryWebDAV`, and server mount API calls.

Risks and test signals: output parsing is heuristic and localized; failed `net use` must unmount WebDAV to avoid leaks. Tests should cover drive validation, `*` parsing, command failure cleanup, and unmount ordering with mocked command execution.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/mount/mount_net_use.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/mount/mount_posix_webdav_helper.go -->
# sources/sync-backup/kopia/internal/mount/mount_posix_webdav_helper.go

Purpose: provides the POSIX WebDAV mount controller used when FUSE is unavailable or explicitly bypassed.

Important APIs/types/functions: `posixWedavController`, `newPosixWedavController`, `Unmount`, `MountPath`, and `Done`.

Control flow: starts a Kopia WebDAV server with `DirectoryWebDAV`, mounts its URL at the target path with platform helper commands, and returns a controller that first unmounts the OS mount then stops the WebDAV server. Temporary mount directories are removed during unmount.

State and persistence behavior: tracks mount point, wrapped WebDAV controller, done channel from the WebDAV server, and temp-dir ownership.

Dependencies and integration points: calls build-tagged `mountWebDavHelper` and `unmountWebDavHelper`, plus `DirectoryWebDAV`.

Risks and test signals: failure after WebDAV start but before OS mount must clean up the server; helper command behavior differs by OS. Tests should inject helper failures, verify temp-dir cleanup, and ensure `Done` reflects server shutdown.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/mount/mount_posix_webdav_helper.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/mount/mount_posix_webdav_helper_darwin.go -->
# sources/sync-backup/kopia/internal/mount/mount_posix_webdav_helper_darwin.go

Purpose: Darwin-specific WebDAV mount helper.

Important APIs/types/functions: `mountWebDavHelper` invokes `mount_webdav`; `unmountWebDavHelper` invokes `umount`.

Control flow: builds an external command with the WebDAV URL and target path, executes it through `exec.CommandContext`, and wraps command errors with output context.

State and persistence behavior: state is held by the OS mount table; the file itself stores none.

Dependencies and integration points: used by `newPosixWedavController` on macOS.

Risks and test signals: external command availability and permissions dominate reliability. Integration tests should cover command failure messages and unmount cleanup on Darwin.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/mount/mount_posix_webdav_helper_darwin.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/mount/mount_posix_webdav_helper_linux.go -->
# sources/sync-backup/kopia/internal/mount/mount_posix_webdav_helper_linux.go

Purpose: Linux-specific WebDAV mount helper.

Important APIs/types/functions: `mountWebDavHelper` uses `mount -t davfs`; `unmountWebDavHelper` uses `umount`.

Control flow: delegates mounting and unmounting to system commands under the caller context and returns wrapped command errors.

State and persistence behavior: mount table state is managed by the operating system; no process-local state is stored here.

Dependencies and integration points: depends on davfs support and is called by the POSIX WebDAV controller.

Risks and test signals: Linux hosts may lack `davfs2` or require privileges; command output should be surfaced for diagnostics. Tests are mostly integration or command-wrapper substitution tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/mount/mount_posix_webdav_helper_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/mount/mount_unsupported.go -->
# sources/sync-backup/kopia/internal/mount/mount_unsupported.go

Purpose: build-tag fallback for platforms without a supported mount implementation.

Important APIs/types/functions: `Directory` has the same signature as supported platform files and returns a clear unsupported error.

Control flow: immediately returns nil controller and an error mentioning unsupported OS/filesystem mounting.

State and persistence behavior: no state.

Dependencies and integration points: ensures callers can compile on unsupported platforms while receiving runtime failure.

Risks and test signals: callers must surface this error rather than assuming mounts always work. Build-tag validation should ensure only one `Directory` implementation is selected per target.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/mount/mount_unsupported.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/mount/mount_webdav.go -->
# sources/sync-backup/kopia/internal/mount/mount_webdav.go

Purpose: exposes a Kopia `fs.Directory` over a local WebDAV HTTP server and returns its URL as a mount path.

Important APIs/types/functions: `DirectoryWebDAV`, `webdavServerLogger`, `webdavController`, `Unmount`, `MountPath`, and `Done`.

Control flow: creates a `webdav.Handler` backed by `internal/webdavfs`, listens on loopback port `0`, serves HTTP in a goroutine, and returns a controller containing the server, listener URL, and done channel. Unmount calls `Shutdown`.

State and persistence behavior: process-local HTTP server and listener are active until shutdown; no repository state is mutated.

Dependencies and integration points: used directly on Windows before `net use` and on POSIX WebDAV fallback; integrates `golang.org/x/net/webdav`, `net/http`, and `fs.Directory`.

Risks and test signals: local server lifecycle and shutdown races are key. Tests should verify URL formation, error logging, server shutdown, and read-only WebDAV behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/mount/mount_webdav.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/osexec/osexec.go -->
# sources/sync-backup/kopia/internal/osexec/osexec.go

Purpose: package anchor for OS-specific command execution helpers.

Important APIs/types/functions: the portable API is supplied by build-tagged `DisableInterruptSignal` implementations.

Control flow: no executable logic in this file.

State and persistence behavior: no state.

Dependencies and integration points: package is imported where Kopia starts child processes and needs platform-specific signal behavior.

Risks and test signals: build tags must always provide exactly one implementation for target OSes.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/osexec/osexec.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/osexec/osexec_test.go -->
# sources/sync-backup/kopia/internal/osexec/osexec_test.go

Purpose: verifies the portable `DisableInterruptSignal` API is callable for an `exec.Cmd`.

Important APIs/types/functions: `TestDisableInterruptSignal` constructs a command and calls `osexec.DisableInterruptSignal`.

Control flow: the test does not run the command; it asserts the helper can mutate command attributes without panicking.

State and persistence behavior: no persistent state or process execution.

Dependencies and integration points: tests the exported API from package `osexec_test`, so only public behavior is visible.

Risks and test signals: this is smoke coverage only. Platform-specific behavioral validation would need subprocess signal tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/osexec/osexec_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/osexec/osexec_unix.go -->
# sources/sync-backup/kopia/internal/osexec/osexec_unix.go

Purpose: Unix implementation that prevents child commands from receiving terminal interrupt signals intended for Kopia.

Important APIs/types/functions: `DisableInterruptSignal(c *exec.Cmd)`.

Control flow: sets `SysProcAttr.Setpgid = true` so the child runs in a separate process group.

State and persistence behavior: mutates the `exec.Cmd` before start; no persistent state.

Dependencies and integration points: depends on `syscall.SysProcAttr` and is used before starting external helpers.

Risks and test signals: callers must invoke it before `Start`; tests should confirm process group isolation on Unix where feasible.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/osexec/osexec_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/osexec/osexec_windows.go -->
# sources/sync-backup/kopia/internal/osexec/osexec_windows.go

Purpose: Windows implementation of interrupt-signal isolation for child commands.

Important APIs/types/functions: `DisableInterruptSignal(c *exec.Cmd)`.

Control flow: sets Windows process creation flags so the child does not receive console Ctrl-C events as part of the parent process group.

State and persistence behavior: mutates `exec.Cmd.SysProcAttr` before process start; no persistence.

Dependencies and integration points: used by command-running code on Windows.

Risks and test signals: behavior depends on Windows console semantics. Tests should run a child command and verify parent interrupt handling separately from child lifetime.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/osexec/osexec_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/ospath/ospath.go -->
# sources/sync-backup/kopia/internal/ospath/ospath.go

Purpose: centralizes user-visible path and directory resolution across platforms.

Important APIs/types/functions: package variables for `homeDir`, `configDir`, and `logsDir`; `ConfigDir`, `LogsDir`, `IsAbs`, and `ResolveUserFriendlyPath`.

Control flow: `ConfigDir` and `LogsDir` return platform-initialized directories. `IsAbs` expands leading `~` first then delegates to `filepath.IsAbs`. `ResolveUserFriendlyPath` expands `~`, optionally makes relative paths home-relative, and cleans the result.

State and persistence behavior: package-level variables are initialized by OS-specific `init` files and environment lookups; no files are written here.

Dependencies and integration points: server path APIs, config discovery, log placement, and CLI path handling call into this package.

Risks and test signals: environment-dependent init paths can vary by OS and CI setup. Tests cover absolute-path behavior, but additional checks should cover tilde expansion and relative-to-home behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/ospath/ospath.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/ospath/ospath_darwin.go -->
# sources/sync-backup/kopia/internal/ospath/ospath_darwin.go

Purpose: Darwin-specific path initialization.

Important APIs/types/functions: `init` sets config and log directory defaults under macOS user library locations.

Control flow: runs at package initialization after shared variables are available.

State and persistence behavior: updates process-global path variables only.

Dependencies and integration points: affects `ConfigDir` and `LogsDir` on macOS.

Risks and test signals: macOS directory conventions should be verified in platform tests, especially when home directory discovery fails.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/ospath/ospath_darwin.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/ospath/ospath_nonwindows.go -->
# sources/sync-backup/kopia/internal/ospath/ospath_nonwindows.go

Purpose: non-Windows filename helper.

Important APIs/types/functions: `SafeLongFilename`.

Control flow: returns the input filename unchanged because POSIX paths do not need the Windows long-path prefix.

State and persistence behavior: stateless.

Dependencies and integration points: callers can use one API without OS checks.

Risks and test signals: only build-tag selection matters; Unix tests should assert identity behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/ospath/ospath_nonwindows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/ospath/ospath_openbsd.go -->
# sources/sync-backup/kopia/internal/ospath/ospath_openbsd.go

Purpose: OpenBSD-specific path initialization.

Important APIs/types/functions: `init` sets OpenBSD config/log defaults.

Control flow: package initialization assigns OS-appropriate directories.

State and persistence behavior: process-global directory variables only.

Dependencies and integration points: consumed through `ConfigDir` and `LogsDir`.

Risks and test signals: platform-specific default paths should be checked in OpenBSD CI or targeted unit tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/ospath/ospath_openbsd.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/ospath/ospath_test.go -->
# sources/sync-backup/kopia/internal/ospath/ospath_test.go

Purpose: portable unit tests for absolute-path detection.

Important APIs/types/functions: `TestIsAbs`.

Control flow: table-driven cases compare `ospath.IsAbs` with expected values for ordinary absolute and relative paths on the current platform.

State and persistence behavior: no state changes.

Dependencies and integration points: validates shared behavior used by config and API path resolution.

Risks and test signals: platform differences limit expectations; Windows-specific edge cases live in a separate test file.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/ospath/ospath_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/ospath/ospath_windows.go -->
# sources/sync-backup/kopia/internal/ospath/ospath_windows.go

Purpose: Windows-specific path initialization and long-filename conversion.

Important APIs/types/functions: Windows `init` and `SafeLongFilename`.

Control flow: initialization chooses Windows config/log directories. `SafeLongFilename` converts long local drive or UNC paths to extended-length forms while leaving short, relative, or already-prefixed paths alone.

State and persistence behavior: only package globals are initialized; no filesystem writes.

Dependencies and integration points: protects Windows filesystem operations that may exceed traditional MAX_PATH limits.

Risks and test signals: extended path prefix handling is subtle for drive letters, UNC shares, and already-safe paths. Windows tests cover these conversions.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/ospath/ospath_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/ospath/ospath_windows_test.go -->
# sources/sync-backup/kopia/internal/ospath/ospath_windows_test.go

Purpose: Windows-only tests for `SafeLongFilename`.

Important APIs/types/functions: `TestSafeLongFilename_Windows`.

Control flow: table cases feed normal drive paths, UNC paths, relative paths, and existing extended paths into the helper and compare exact strings.

State and persistence behavior: no external state.

Dependencies and integration points: validates path strings used by Windows file operations elsewhere in Kopia.

Risks and test signals: these tests are build-tagged for Windows and will not run on Unix CI; cross-platform coverage depends on Windows jobs.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/ospath/ospath_windows_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/ospath/ospath_xdg.go -->
# sources/sync-backup/kopia/internal/ospath/ospath_xdg.go

Purpose: XDG-based path initialization for Unix-like non-Darwin/OpenBSD/non-Windows systems.

Important APIs/types/functions: `init`.

Control flow: reads relevant XDG environment variables when present and falls back to home-relative defaults for config and logs.

State and persistence behavior: assigns package-global path variables during initialization.

Dependencies and integration points: affects default config and log paths on Linux and related platforms.

Risks and test signals: XDG environment combinations should be tested with isolated process-level tests because init-time state is hard to reset in-process.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/ospath/ospath_xdg.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/ownwrites/ownwrites.go -->
# sources/sync-backup/kopia/internal/ownwrites/ownwrites.go

Purpose: wraps eventually consistent blob storage so recent local writes appear in listings and recent deletes disappear from listings.

Important APIs/types/functions: `CacheStorage`, `ListBlobs`, `PutBlob`, `DeleteBlob`, `NewWrapper`, `isCachedPrefix`, `maybeSweepCache`, marker prefixes `add` and `del`, and `markerData`.

Control flow: writes and deletes delegate to the underlying storage, then record cache markers for configured prefixes. Listing sweeps old markers, loads add/delete markers for the requested prefix, filters underlying provider results through delete markers, removes already-visible add markers, and fetches metadata for remaining recent additions.

State and persistence behavior: mutation markers are stored in the provided cache `blob.Storage` for `cacheDuration`; `nextSweepTime` is in-memory and mutex-protected.

Dependencies and integration points: used by repository blob layers where providers may be list-eventually-consistent.

Risks and test signals: marker write failures are intentionally ignored, and marker timestamp ordering decides add-vs-delete conflicts. Tests simulate eventual consistency, prefix filtering, deletion hiding, and sweeping expired markers.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/ownwrites/ownwrites.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/ownwrites/ownwrites_test.go -->
# sources/sync-backup/kopia/internal/ownwrites/ownwrites_test.go

Purpose: validates own-writes consistency behavior with fake time and eventually consistent storage.

Important APIs/types/functions: `TestOwnWrites`, fake time sources, `blobtesting.NewEventuallyConsistentStorage`, and `NewWrapper`.

Control flow: seeds settled data, writes cached and uncached prefixes, asserts cache marker creation, checks that wrapper lists fresh writes before provider consistency catches up, deletes a blob and verifies deletion hiding, then advances cache time to trigger marker sweep.

State and persistence behavior: all state lives in in-memory map storages and fake clocks.

Dependencies and integration points: exercises the real `CacheStorage` implementation through the `blob.Storage` interface.

Risks and test signals: strong coverage for add/delete marker semantics; does not cover cache-storage failures or concurrent listing/writes.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/ownwrites/ownwrites_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/parallelwork/parallel_work_queue.go -->
# sources/sync-backup/kopia/internal/parallelwork/parallel_work_queue.go

Purpose: implements a dynamically growable parallel work queue where tasks may enqueue more work while workers are running.

Important APIs/types/functions: `Queue`, `CallbackFunc`, `EnqueueFront`, `EnqueueBack`, `Process`, `dequeue`, `completed`, `ProgressCallback`, `OnNthCompletion`, and `NewQueue`.

Control flow: enqueue pushes callbacks to a `container/list` and signals a condition variable. `Process` starts a fixed worker pool under `errgroup`; workers dequeue until the queue is empty and no worker is active. Completion increments counters and wakes waiters. Progress callbacks are rate-limited through `maybeReportProgress`.

State and persistence behavior: in-memory queue, counters, active worker count, and next progress report time protected by `sync.Cond` lock.

Dependencies and integration points: supports upload, validation, and other bulk concurrent workflows.

Risks and test signals: correctness depends on condition signaling and active-worker accounting. Tests cover front/back order, errors, waiting for active workers, progress callbacks, and `OnNthCompletion`.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/parallelwork/parallel_work_queue.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/parallelwork/parallel_work_queue_test.go -->
# sources/sync-backup/kopia/internal/parallelwork/parallel_work_queue_test.go

Purpose: tests queue ordering, concurrency completion, error propagation, progress reporting, and completion wrappers.

Important APIs/types/functions: `TestEnqueueFrontAndProcess`, `TestEnqueueBackAndProcess`, `TestProcessWithError`, `TestWaitForActiveWorkers`, `TestProgressCallback`, and `TestOnNthCompletion`.

Control flow: creates queues, enqueues callbacks that send results, block, or return errors, then runs `Process` with multiple workers and asserts counters/order/returned errors.

State and persistence behavior: uses channels and atomics for deterministic in-memory synchronization.

Dependencies and integration points: exercises the public `parallelwork` API from an external test package.

Risks and test signals: good coverage for core scheduling; race-detector runs are important because cond-variable bugs may pass normal tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/parallelwork/parallel_work_queue_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/passwordpersist/passwordpersist.go -->
# sources/sync-backup/kopia/internal/passwordpersist/passwordpersist.go

Purpose: defines the password persistence strategy abstraction and helper for connect/create success handling.

Important APIs/types/functions: `Strategy`, `ErrPasswordNotFound`, `ErrUnsupported`, and `OnSuccess`.

Control flow: strategies provide get, persist, and delete methods. `OnSuccess` deletes a stored password when the preceding operation failed and persists the supplied password when it succeeded.

State and persistence behavior: this file owns no storage; concrete strategies may use files, OS keyrings, or no persistence.

Dependencies and integration points: repository connect/create flows use this abstraction through server options and CLI options.

Risks and test signals: `OnSuccess` logs delete failures but returns original operation errors. Tests should exercise failure cleanup and persist error wrapping with fake strategies.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/passwordpersist/passwordpersist.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/passwordpersist/passwordpersist_file.go -->
# sources/sync-backup/kopia/internal/passwordpersist/passwordpersist_file.go

Purpose: stores repository passwords in a sidecar file next to the config file.

Important APIs/types/functions: `File`, `filePasswordStorage`, `GetPassword`, `PersistPassword`, `DeletePassword`, `passwordFileName`, and `passwordFileMode`.

Control flow: password values are base64-encoded into `<config>.kopia-password`; reads translate missing files to `ErrPasswordNotFound` and invalid base64 to a wrapped error; delete ignores missing files.

State and persistence behavior: persists plaintext-equivalent base64 data in a `0600` file.

Dependencies and integration points: fallback or configured persistence strategy for repository passwords.

Risks and test signals: base64 is not encryption, so file permissions are security-critical. Tests should cover mode, invalid contents, missing file, and delete idempotence.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/passwordpersist/passwordpersist_file.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/passwordpersist/passwordpersist_keyring.go -->
# sources/sync-backup/kopia/internal/passwordpersist/passwordpersist_keyring.go

Purpose: stores repository passwords in the operating-system keyring.

Important APIs/types/functions: `Keyring`, `keyringStrategy`, `GetPassword`, `PersistPassword`, `DeletePassword`, `getKeyringItemID`, and `keyringUsername`.

Control flow: derives a stable keyring item ID from config basename plus SHA-256 prefix, uses current OS user as username, normalizes Windows domain names, and maps keyring errors to Kopia persistence errors.

State and persistence behavior: secrets persist in OS keychain/keyring; no in-process cache.

Dependencies and integration points: uses `github.com/zalando/go-keyring`, `os/user`, and repository config paths.

Risks and test signals: keyring availability and locked keyrings vary by platform/session. Tests need mocks or integration opt-ins for unsupported, not found, save, delete, and username normalization.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/passwordpersist/passwordpersist_keyring.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/passwordpersist/passwordpersist_multiple.go -->
# sources/sync-backup/kopia/internal/passwordpersist/passwordpersist_multiple.go

Purpose: composes multiple password persistence strategies with fallback semantics.

Important APIs/types/functions: `Multiple`, `GetPassword`, `PersistPassword`, and `DeletePassword`.

Control flow: get returns the first successful password, skips `ErrPasswordNotFound`, and fails on other errors. Persist tries strategies until one succeeds, skips `ErrUnsupported`, and returns `ErrUnsupported` if none work. Delete calls all strategies and suppresses expected not-found/unsupported outcomes.

State and persistence behavior: state is delegated to child strategies.

Dependencies and integration points: lets Kopia prefer keyring while falling back to file or none.

Risks and test signals: delete can partially fail after earlier strategies succeeded. Tests should cover strategy ordering, fatal errors, unsupported fallback, and aggregate delete behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/passwordpersist/passwordpersist_multiple.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/passwordpersist/passwordpersist_none.go -->
# sources/sync-backup/kopia/internal/passwordpersist/passwordpersist_none.go

Purpose: explicit strategy that disables password persistence.

Important APIs/types/functions: `None`, `noneStrategy`, and methods implementing `Strategy`.

Control flow: `GetPassword` returns `ErrPasswordNotFound`; `PersistPassword` returns `ErrUnsupported`; `DeletePassword` succeeds as a no-op.

State and persistence behavior: stores nothing.

Dependencies and integration points: useful for users or environments that do not want secrets persisted.

Risks and test signals: callers must handle unsupported persistence as nonfatal when configured with fallbacks.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/passwordpersist/passwordpersist_none.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/providervalidation/providervalidation.go -->
# sources/sync-backup/kopia/internal/providervalidation/providervalidation.go

Purpose: validates a blob storage provider against Kopia assumptions for capacity reporting, missing-blob errors, conditional writes, listing, partial reads, metadata, clock drift, and concurrent access.

Important APIs/types/functions: `Options`, `DefaultOptions`, `ValidateProvider`, `equivalentBlobStorageConnections`, `openEquivalentStorageConnections`, `concurrencyTest`, worker methods, `cleanupAllBlobs`, and `verifyBlobCount`.

Control flow: unless `KOPIA_SKIP_PROVIDER_VALIDATION` is set, validation opens multiple equivalent storage connections, creates a unique temp prefix, checks capacity semantics, verifies empty/missing/list behavior, writes a large blob, probes `DoNotRecreate`, validates full and partial reads and metadata timestamp drift, then runs concurrent put/get/metadata workers until a deadline.

State and persistence behavior: temporary blobs are written to the target storage and removed with deferred cleanup. Concurrency state tracks generated blob IDs, seeds, and write completion under a mutex.

Dependencies and integration points: used during repository/storage setup; integrates `blob.Storage`, `gather`, logging wrappers, fake clock, and UUID temp prefixes.

Risks and test signals: the list worker is a TODO, random lengths can be zero and generated ID needs at least 16 bytes of data, and validation can be expensive. Tests should use map storage and short durations to verify basic pass/fail behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/providervalidation/providervalidation.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/providervalidation/providervalidation_test.go -->
# sources/sync-backup/kopia/internal/providervalidation/providervalidation_test.go

Purpose: smoke-tests provider validation against in-memory storage.

Important APIs/types/functions: `TestProviderValidation`, `blobtesting.NewMapStorage`, and `DefaultOptions` with shortened duration.

Control flow: constructs a map storage, adjusts validation options to make the run cheap, and asserts `ValidateProvider` succeeds.

State and persistence behavior: temporary validation blobs live only in map storage and should be cleaned up.

Dependencies and integration points: confirms the validation path works for a compliant provider.

Risks and test signals: this is a happy-path test; additional tests should inject bad metadata, wrong missing errors, failed partial reads, and clock drift.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/providervalidation/providervalidation_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/releasable/releaseable_tracker.go -->
# sources/sync-backup/kopia/internal/releasable/releaseable_tracker.go

Purpose: provides optional process-wide tracking for resources that must be released, capturing allocation stack traces for leak diagnostics.

Important APIs/types/functions: `ItemKind`, `Created`, `Released`, `Active`, `Verify`, `EnableTracking`, `DisableTracking`, and `perKindTracker`.

Control flow: enabling a kind installs a tracker. `Created` records `debug.Stack()` under an item ID, `Released` deletes it, `Active` clones all maps, and `Verify` formats any remaining active items into an error.

State and persistence behavior: global in-memory maps protected by mutexes; tracking is disabled per kind by removing its tracker.

Dependencies and integration points: test and debug-only consumers can enable tracking around resource lifecycles.

Risks and test signals: globals can leak between tests if not disabled, and item IDs must be comparable. Tests cover enable/create/release/verify lifecycle.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/releasable/releaseable_tracker.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/releasable/releaseable_tracker_test.go -->
# sources/sync-backup/kopia/internal/releasable/releaseable_tracker_test.go

Purpose: validates releasable resource tracking behavior.

Important APIs/types/functions: `TestReleaseable`, `EnableTracking`, `Created`, `Released`, `Verify`, `Active`, and `DisableTracking`.

Control flow: enables a kind, creates and releases items, checks active maps and verification errors, and disables tracking.

State and persistence behavior: mutates package-global trackers, so cleanup is important for test isolation.

Dependencies and integration points: tests the public package from `releasable_test`.

Risks and test signals: should be run with race detector if resource tracking is used concurrently.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/releasable/releaseable_tracker_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/repodiag/blob_writer.go -->
# sources/sync-backup/kopia/internal/repodiag/blob_writer.go

Purpose: asynchronously encrypts and writes diagnostic blobs.

Important APIs/types/functions: `BlobWriter`, `EncryptAndWriteBlobAsync`, `Wait`, and `NewWriter`.

Control flow: `EncryptAndWriteBlobAsync` starts an errgroup task that encrypts gathered bytes through a crypter, writes them to blob storage under a prefix-derived ID, logs progress, and invokes a close callback. `Wait` joins all pending writes.

State and persistence behavior: diagnostic data is persisted as encrypted blobs in the target storage; pending goroutines are tracked by `errgroup`.

Dependencies and integration points: used by diagnostic log manager; depends on `blob.Storage`, `blobcrypto.Crypter`, `gather`, and logging.

Risks and test signals: callers must call `Wait` to surface asynchronous errors, and close callbacks must always run. Tests should validate encryption, blob IDs, callback invocation, and write error propagation.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/repodiag/blob_writer.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/repodiag/blob_writer_test.go -->
# sources/sync-backup/kopia/internal/repodiag/blob_writer_test.go

Purpose: verifies diagnostic writer encryption and storage output.

Important APIs/types/functions: `TestDiagWriter` and `newStaticCrypter`.

Control flow: creates a map storage and static crypter, writes diagnostic data asynchronously, waits, then asserts expected encrypted blob content exists.

State and persistence behavior: in-memory blob storage receives encrypted output.

Dependencies and integration points: validates `BlobWriter` behavior without a real repository.

Risks and test signals: focuses on happy path; error-path tests should simulate storage write and crypter failures.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/repodiag/blob_writer_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/repodiag/log_manager.go -->
# sources/sync-backup/kopia/internal/repodiag/log_manager.go

Purpose: captures repository diagnostic logs into encrypted blobs and optional text output.

Important APIs/types/functions: `LogManager`, `NewLogger`, `Enable`, `Disable`, `outputEntry`, `flushNextBuffer`, `Sync`, `initNewBuffer`, `NewLogManager`, and `LogBlobPrefix`.

Control flow: log entries are written to a current gather buffer when enabled. Buffer size or sync triggers rotate the buffer, enqueue encrypted blob writes through `BlobWriter`, and optionally mirror entries to a text writer. `Sync` flushes the current buffer and waits for pending blob writes.

State and persistence behavior: maintains enabled flag, active buffer, blob sequence IDs, and pending async writes; log data persists as encrypted blobs.

Dependencies and integration points: integrates `contentlog.Logger`, repository diagnostic blob writer, and notification/logging code.

Risks and test signals: concurrency around buffer rotation and context cancellation is sensitive. Tests cover enabled logging, auto-flush, disabled mode, canceled context, and null writer behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/repodiag/log_manager.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/repodiag/log_manager_test.go -->
# sources/sync-backup/kopia/internal/repodiag/log_manager_test.go

Purpose: validates diagnostic log manager modes and flushing behavior.

Important APIs/types/functions: `TestLogManager_Enabled`, `TestLogManager_AutoFlush`, `TestLogManager_NotEnabled`, `TestLogManager_CancelledContext`, and `TestLogManager_Null`.

Control flow: constructs log managers with fake writers/storage, emits log entries, toggles enablement, syncs, and asserts blob/text outputs or absence of output.

State and persistence behavior: test state is in-memory buffers and storages.

Dependencies and integration points: exercises `contentlog` integration and `BlobWriter`-backed persistence.

Risks and test signals: useful for regression around flush thresholds and disabled logging; race detector helps for concurrent logging paths.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/repodiag/log_manager_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/repotesting/reconnectable_storage.go -->
# sources/sync-backup/kopia/internal/repotesting/reconnectable_storage.go

Purpose: registers a blob storage wrapper used in tests to reconnect to an existing underlying storage by UUID.

Important APIs/types/functions: `reconnectableStorage`, `ReconnectableStorageType`, `ReconnectableStorageOptions`, `NewReconnectableStorage`, `ConnectionInfo`, `New`, and `init`.

Control flow: wrapping stores the underlying storage in a package `sync.Map` by UUID and returns a storage whose `ConnectionInfo` references that UUID. Reopening through registered blob provider options looks up the same backing storage.

State and persistence behavior: process-global map holds references to test storages; no external persistence.

Dependencies and integration points: used by repository tests that need close/reopen paths without real remote storage.

Risks and test signals: global map entries can leak for long test processes; UUID lookup failures should return clear errors. Tests around repository reopen exercise this indirectly.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/repotesting/reconnectable_storage.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/repotesting/repotesting.go -->
# sources/sync-backup/kopia/internal/repotesting/repotesting.go

Purpose: provides a high-level test environment for creating, opening, reopening, and inspecting Kopia repositories.

Important APIs/types/functions: `Environment`, `Options`, `RepositoryMetrics`, `RootStorage`, `setup`, `Close`, `ConfigFile`, `MustReopen`, `MustOpenAnother`, `MustConnectOpenAnother`, `VerifyBlobCount`, `LocalPathSourceInfo`, `repoOptions`, `NewEnvironment`, `DefaultPasswordForTesting`, and `FormatNotImportant`.

Control flow: setup creates temp config/storage, initializes a repository at a requested format, opens it with test client options and optional time/metrics hooks, and exposes helpers for reopening or opening additional connections. Close shuts down repository and storage resources.

State and persistence behavior: test repository state persists in temp directories or in-memory blob storage for the test lifetime; environment records config file, storage, repository writer, metrics, and injected time.

Dependencies and integration points: heavily used by server, repo, snapshot, and maintenance tests.

Risks and test signals: helpers call `require`/`Fatal` style APIs and are unsuitable for production code; tests should close environments and validate blob counts after operations.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/repotesting/repotesting.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/repotesting/repotesting_test.go -->
# sources/sync-backup/kopia/internal/repotesting/repotesting_test.go

Purpose: validates that repository test environments wire custom time functions into repository operations.

Important APIs/types/functions: `TestTimeFuncWiring`.

Control flow: creates a test environment with fake time options and verifies repository behavior observes that time source.

State and persistence behavior: temporary repository state only.

Dependencies and integration points: protects consumers relying on deterministic timestamps in tests.

Risks and test signals: narrow coverage; most `repotesting` behavior is tested indirectly by broad repository/server tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/repotesting/repotesting_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/retry/retry.go -->
# sources/sync-backup/kopia/internal/retry/retry.go

Purpose: generic retry helpers for value-returning and no-value operations with exponential or fixed-interval backoff.

Important APIs/types/functions: `IsRetriableFunc`, `WithExponentialBackoff`, `WithExponentialBackoffMaxRetries`, `Periodically`, `PeriodicallyNoValue`, `WithExponentialBackoffNoValue`, `NoValueFn`, `Always`, `Never`, and `internalRetry`.

Control flow: `internalRetry` runs attempts until success, context cancellation, non-retriable error, or retry count exhaustion. Between failures it logs and sleeps interruptibly using a configurable interval, factor, and max sleep.

State and persistence behavior: stateless except for local counters and sleep duration.

Dependencies and integration points: shared by network/storage/repository operations that need retry policies.

Risks and test signals: off-by-one retry counts and context cancellation handling are critical. Tests cover success after retries, non-retriable stop, max retry exhaustion, and cancellation.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/retry/retry.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/retry/retry_test.go -->
# sources/sync-backup/kopia/internal/retry/retry_test.go

Purpose: tests retry helper behavior.

Important APIs/types/functions: `TestRetry`, `TestRetryContextCancel`, sentinel `errRetriable`, and `isRetriable`.

Control flow: uses attempts that fail then succeed or remain failing, asserts number of calls and returned errors, and cancels context to ensure retry exits.

State and persistence behavior: no persistence; counters are local to tests.

Dependencies and integration points: validates public retry functions in-package to access helpers.

Risks and test signals: tests should stay fast despite sleeps; fake clock or short intervals are important for deterministic CI.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/retry/retry_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/scheduler/scheduler.go -->
# sources/sync-backup/kopia/internal/scheduler/scheduler.go

Purpose: runs a lightweight scheduler that periodically asks for upcoming items and triggers due callbacks.

Important APIs/types/functions: `GetItemsFunc`, `Item`, `Scheduler`, `Options`, `Start`, `upcomingItems`, `Stop`, `run`, and `TriggerNames`.

Control flow: `Start` creates a scheduler goroutine. Each loop calls `getItems`, partitions due items from future items, triggers due callbacks, then sleeps until the nearest future time, a refresh signal, or stop. With no upcoming items it sleeps for a long default interval.

State and persistence behavior: in-memory goroutine, stop channel, refresh channel, time function, and item source. It persists nothing externally.

Dependencies and integration points: server uses it for repository refresh, maintenance, and scheduled snapshots.

Risks and test signals: timer/refresh races and past-due handling are key. Tests validate scheduling, past triggers, refresh behavior, and trigger-name formatting.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/scheduler/scheduler.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/scheduler/scheduler_test.go -->
# sources/sync-backup/kopia/internal/scheduler/scheduler_test.go

Purpose: validates scheduler triggering and refresh semantics.

Important APIs/types/functions: `TestScheduler`, `TestSchedulerWillTriggerItemsInThePast`, `TestSchedulerRefresh`, `TestTriggerNames`, and helper `reportTriggered`.

Control flow: supplies fake item lists and channels, starts schedulers with controlled times/refreshes, and asserts due callbacks fire in expected order and names are joined correctly.

State and persistence behavior: goroutine-local scheduler state; tests communicate through channels.

Dependencies and integration points: protects server scheduling behavior indirectly.

Risks and test signals: timing tests can be flaky if real sleeps are long; controlled time functions reduce this risk.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/scheduler/scheduler_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/scrubber/scrub_sensitive.go -->
# sources/sync-backup/kopia/internal/scrubber/scrub_sensitive.go

Purpose: recursively redacts struct fields marked as sensitive before logging or display.

Important APIs/types/functions: `ScrubSensitiveData(reflect.Value)`.

Control flow: expects a struct value, creates a copy, iterates fields, replaces fields tagged as sensitive with zero/redacted values, and recursively scrubs nested structs where appropriate.

State and persistence behavior: returns a scrubbed reflected value without mutating persistent storage.

Dependencies and integration points: used around config/API values that may contain secrets.

Risks and test signals: reflection can panic on unsupported inputs or unexported fields; test coverage checks nested structs, pointer-like values, and panic on non-struct input.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/scrubber/scrub_sensitive.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/scrubber/scrub_sensitive_test.go -->
# sources/sync-backup/kopia/internal/scrubber/scrub_sensitive_test.go

Purpose: tests sensitive-field redaction.

Important APIs/types/functions: test structs `S` and `Q`, `TestScrubber`, and `TestScrubberPanicsOnNonStruct`.

Control flow: builds structs with sensitive tags, scrubs them, and compares output; separately asserts non-struct input panics.

State and persistence behavior: no persistence.

Dependencies and integration points: validates the reflection contract for callers that log scrubbed values.

Risks and test signals: should be expanded when new tag conventions or nested container types are supported.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/scrubber/scrub_sensitive_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/server/api_cli.go -->
# sources/sync-backup/kopia/internal/server/api_cli.go

Purpose: implements the UI API endpoint that returns a reusable Kopia CLI command for the current server config.

Important APIs/types/functions: `handleCLIInfo` and `maybeQuote`.

Control flow: obtains `os.Executable`, falls back to `kopia`, quotes executable/config paths containing spaces, and returns `serverapi.CLIInfo` with `--config-file=...`.

State and persistence behavior: reads process executable path and server options; no mutation.

Dependencies and integration points: registered as `/api/v1/cli` by `Server.SetupHTMLUIAPIHandlers` and consumed by UI/client code.

Risks and test signals: quoting is minimal and only handles spaces. Tests validate returned command with a test server and repository config path.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/server/api_cli.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/server/api_cli_test.go -->
# sources/sync-backup/kopia/internal/server/api_cli_test.go

Purpose: integration-tests the CLI info API through the HTTP API client.

Important APIs/types/functions: `TestCLIAPI`, `repotesting.NewEnvironment`, `servertesting.StartServer`, and `apiclient`.

Control flow: starts a test repository server, authenticates, fetches CSRF token, calls `GET cli`, and compares the executable/config command string with local expectations.

State and persistence behavior: creates a temporary test repository and server only for test lifetime.

Dependencies and integration points: covers API routing, auth, CSRF setup, and handler output.

Risks and test signals: assumes executable/config paths do not require quoting in this specific environment.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/server/api_cli_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/server/api_error.go -->
# sources/sync-backup/kopia/internal/server/api_error.go

Purpose: centralizes conversion of server handler failures into HTTP status and API error payloads.

Important APIs/types/functions: `apiError`, `requestError`, `unableToDecodeRequest`, `notFoundError`, `accessDeniedError`, `repositoryNotWritableError`, and `internalServerError`.

Control flow: helper constructors choose HTTP code, `serverapi.APIErrorCode`, and message. Request/decode errors are 400, not found is 404, access denied is 403, and internal errors are 500.

State and persistence behavior: stateless value construction.

Dependencies and integration points: all `apiRequestFunc` handlers return `*apiError` for the common response wrapper in `server.go`.

Risks and test signals: overuse of `internalServerError` can hide client-actionable errors. API tests should assert both HTTP status and structured error code.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/server/api_error.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/server/api_estimate.go -->
# sources/sync-backup/kopia/internal/server/api_estimate.go

Purpose: implements the API for estimating snapshot/upload size and exclusion statistics for a local directory.

Important APIs/types/functions: `estimateTaskProgress`, its `Processing`, `Error`, and `Stats` methods, `logBucketSamples`, and `handleEstimate`.

Control flow: decodes `EstimateRequest`, resolves and cleans the root path, verifies it is a local directory, builds a policy tree with overrides, starts an observable UI task, wires cancellation into `upload.Estimate`, reports counters and final bucket samples, then returns the task record.

State and persistence behavior: no repository mutation; task manager stores task progress/log state, and local filesystem is read.

Dependencies and integration points: integrates localfs, policy resolution, snapshot upload estimation, `uitask`, and server APIs.

Risks and test signals: only local directories are supported; request context is intentionally decoupled from cancellation by the server wrapper. Tests should cover malformed root, non-directory roots, policy override errors, cancellation, and final counters.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/server/api_estimate.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/server/api_mount.go -->
# sources/sync-backup/kopia/internal/server/api_mount.go

Purpose: implements HTTP APIs for creating, listing, querying, and deleting mounted snapshot/object roots.

Important APIs/types/functions: `handleMountCreate`, `handleMountGet`, `handleMountDelete`, and `handleMountList`.

Control flow: create decodes mount request, resolves the requested root object into a filesystem directory, calls server mount-controller lookup/creation, and returns mount metadata. Get returns an existing controller for an object ID, delete removes and unmounts it, and list serializes all current mounts.

State and persistence behavior: mutates the server's in-memory `mounts` map and creates OS mount/WebDAV/FUSE state through `mount.Controller`.

Dependencies and integration points: connects server API, repository object IDs, restore filesystem view, and `internal/mount`.

Risks and test signals: object IDs must be validated, unmount failures need surfacing, and controller lifecycle must avoid leaked mounts. Integration tests should cover create/get/list/delete and duplicate create behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/server/api_mount.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/server/api_notification_profile.go -->
# sources/sync-backup/kopia/internal/server/api_notification_profile.go

Purpose: manages notification profiles through server APIs.

Important APIs/types/functions: `handleNotificationProfileCreate`, `handleNotificationProfileTest`, `handleNotificationProfileGet`, `handleNotificationProfileDelete`, and `handleNotificationProfileList`.

Control flow: handlers decode profile/test requests, operate in repository write sessions where mutations are needed, store or remove notification profile definitions, list configured profiles, and send a test notification for validation.

State and persistence behavior: notification profiles persist as repository configuration/manifest data; test sends external notification side effects depending on configured provider.

Dependencies and integration points: integrates `serverapi` requests, repository writer sessions, and Kopia notification packages.

Risks and test signals: profile names are route parameters and must align with stored names; test notification can fail due to external transport settings. Tests cover create/get/list/delete and test paths.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/server/api_notification_profile.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/server/api_notification_profile_test.go -->
# sources/sync-backup/kopia/internal/server/api_notification_profile_test.go

Purpose: integration-tests notification profile API lifecycle.

Important APIs/types/functions: `TestNotificationProfile`.

Control flow: starts a test server, uses API client calls to create notification profiles, retrieve and list them, run test notification behavior, and delete profiles.

State and persistence behavior: profile state persists in the temporary test repository during the test.

Dependencies and integration points: validates server routing, repository writes, auth/CSRF, and serverapi payload shapes.

Risks and test signals: external notification transports are usually mocked or inert; real transport failures require separate tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/server/api_notification_profile_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/server/api_object_get.go -->
# sources/sync-backup/kopia/internal/server/api_object_get.go

Purpose: streams repository object contents over the HTTP API.

Important APIs/types/functions: `handleObjectGet`.

Control flow: parses object ID from the route, checks repository availability and authorization through the request wrapper, opens the object through repository/object APIs, and writes bytes directly to the HTTP response rather than returning JSON.

State and persistence behavior: read-only repository access; no server state mutation.

Dependencies and integration points: registered for `/api/v1/objects/{objectID}` and used by UI restore/browse operations.

Risks and test signals: object ID parsing and streaming errors must not produce partial misleading responses. Tests should cover missing objects, invalid IDs, and large object streaming.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/server/api_object_get.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/server/api_paths.go -->
# sources/sync-backup/kopia/internal/server/api_paths.go

Purpose: resolves user-friendly local paths for the UI.

Important APIs/types/functions: `handlePathResolve`.

Control flow: decodes/reads path input from the request, calls `ospath.ResolveUserFriendlyPath`, and returns the resolved path in a serverapi response.

State and persistence behavior: stateless path string transformation.

Dependencies and integration points: used by UI forms before local filesystem operations such as estimate or source creation.

Risks and test signals: behavior depends on server OS and home directory. Tests cover API request/response around common relative and tilde paths.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/server/api_paths.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/server/api_paths_test.go -->
# sources/sync-backup/kopia/internal/server/api_paths_test.go

Purpose: tests path resolution API behavior.

Important APIs/types/functions: `TestPathsAPI`.

Control flow: starts a test server, authenticates, calls the path resolution endpoint, and asserts resolved output matches local path rules.

State and persistence behavior: no repository mutation beyond test setup.

Dependencies and integration points: covers request routing, CSRF, and `ospath` integration.

Risks and test signals: OS-dependent path rules may require conditional expectations on Windows versus Unix.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/server/api_paths_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/server/api_policies.go -->
# sources/sync-backup/kopia/internal/server/api_policies.go

Purpose: implements policy list/get/resolve/delete/update APIs for snapshot sources.

Important APIs/types/functions: `handlePolicyList`, `getSnapshotSourceFromURL`, `handlePolicyGet`, `handlePolicyResolve`, `handlePolicyDelete`, and `handlePolicyPut`.

Control flow: source identity is parsed from URL query parameters. List returns policy definitions, get fetches direct policy for a source, resolve computes effective policy with inheritance, delete removes direct policy in a write session, and put decodes and stores a policy for the source.

State and persistence behavior: put/delete mutate repository policy manifests; list/get/resolve are read-only.

Dependencies and integration points: integrates `snapshot.SourceInfo`, `snapshot/policy`, server API wrappers, and source manager refresh behavior.

Risks and test signals: URL-derived source identity must preserve host/user/path correctly; policy writes should refresh source scheduling. Tests cover CRUD and effective policy behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/server/api_policies.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/server/api_policies_test.go -->
# sources/sync-backup/kopia/internal/server/api_policies_test.go

Purpose: integration-tests policy APIs.

Important APIs/types/functions: `TestPolicies`.

Control flow: starts a repository server, uses API calls to read default/effective policies, write policy updates, list policies, and delete them while asserting responses.

State and persistence behavior: policy manifests persist in the temporary test repository.

Dependencies and integration points: validates policy package integration, API auth, JSON payloads, and route query parsing.

Risks and test signals: scheduling refresh side effects are not always directly asserted and should be covered by source-manager tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/server/api_policies_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/server/api_repo.go -->
# sources/sync-backup/kopia/internal/server/api_repo.go

Purpose: implements repository lifecycle and configuration APIs: status, create, exists, connect, disconnect, algorithms, throttle, sync, and description updates.

Important APIs/types/functions: `handleRepoStatus`, `maybeDecodeToken`, `handleRepoCreate`, `handleRepoExists`, `handleRepoConnect`, `handleRepoSetDescription`, `handleRepoSupportedAlgorithms`, `toAlgorithmInfo`, `sortAlgorithms`, throttle handlers, `getConnectOptions`, `connectAPIServerAndOpen`, `connectAndOpen`, `handleRepoDisconnect`, `Server.disconnect`, `handleRepoSync`, and `repoErrorToAPIError`.

Control flow: create/connect decode requests and optional tokens, open blob storage or API-server connections, initialize/open repositories asynchronously when needed, set default policy/maintenance params on create, and install the repository into server state. Status branches direct versus remote repository details. Sync refreshes repository/source state, disconnect closes active state, algorithms returns sorted supported algorithm metadata, and throttle handlers read/write direct repository throttler limits.

State and persistence behavior: creates repository format blobs, writes config/client options, default policies, maintenance params, throttle settings, and mutates server repository/source/scheduler state through `SetRepository`.

Dependencies and integration points: core bridge between `serverapi`, `repo`, `blob`, `policy`, `maintenance`, compression/encryption/hash/splitter packages, and password persistence.

Risks and test signals: async connect can return before completion, token decoding overrides storage/password, and direct-only operations must reject remote repositories. Tests should cover error mapping, already-connected guards, create defaults, disconnect cleanup, and throttle persistence.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/server/api_repo.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/server/api_restore.go -->
# sources/sync-backup/kopia/internal/server/api_restore.go

Purpose: implements restore API as a background task with progress counters.

Important APIs/types/functions: `restoreCounters` and `handleRestore`.

Control flow: decodes restore request, resolves object/source/target parameters, starts a `uitask` restore operation, maps `restore.Stats` into UI counters, wires cancellation, and returns task metadata.

State and persistence behavior: reads repository object content and writes restored files to the local filesystem target; task manager records progress/logs.

Dependencies and integration points: integrates restore package, repository object lookup, server tasks, and UI APIs.

Risks and test signals: filesystem overwrite/safety options and cancellation are high risk. Tests cover restoring snapshots through the API and validating restored contents.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/server/api_restore.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/server/api_restore_test.go -->
# sources/sync-backup/kopia/internal/server/api_restore_test.go

Purpose: integration-tests restoring snapshots through the API.

Important APIs/types/functions: `TestRestoreSnapshots`.

Control flow: creates test snapshot data, starts server/client, invokes restore API, waits for task completion, and verifies restored filesystem output.

State and persistence behavior: temporary repository plus restored local files in test directories.

Dependencies and integration points: covers snapshot creation, restore engine, task manager, and API client behavior.

Risks and test signals: should catch regressions in object selection and task completion but may not cover all overwrite/error modes.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/server/api_restore_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/server/api_snapshots.go -->
# sources/sync-backup/kopia/internal/server/api_snapshots.go

Purpose: implements snapshot listing, deletion, editing, upload trigger, cancellation, pause/resume, filtering, and manifest conversion APIs.

Important APIs/types/functions: `handleListSnapshots`, `handleDeleteSnapshots`, `handleEditSnapshots`, `forAllSourceManagersMatchingURLFilter`, `handleUpload`, `handleCancel`, `handlePause`, `handleResume`, `uniqueSnapshots`, `sourceMatchesURLFilter`, and `convertSnapshotManifest`.

Control flow: list loads snapshot manifests, converts them to API rows, and de-duplicates. Delete/edit operate on selected snapshot manifests in write sessions. Source actions iterate source managers matching URL filters and invoke snapshot, cancel, pause, or resume operations. Conversion maps manifest metadata, retention, statistics, and source fields into `serverapi.Snapshot`.

State and persistence behavior: delete/edit mutate snapshot manifests and retention labels; upload starts background source-manager tasks; pause/resume/cancel mutate source manager runtime state.

Dependencies and integration points: integrates `snapshot`, `manifest`, `policy`, `sourceManager`, server task management, and UI source controls.

Risks and test signals: filtering by host/user/path and manifest de-duplication are subtle; write actions require proper authorization and refresh. Tests cover list/delete/edit flows.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/server/api_snapshots.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/server/api_snapshots_test.go -->
# sources/sync-backup/kopia/internal/server/api_snapshots_test.go

Purpose: integration-tests snapshot list/delete/edit APIs.

Important APIs/types/functions: `TestListAndDeleteSnapshots` and `TestEditSnapshots`.

Control flow: creates snapshots in a test repository, lists through API, deletes selected snapshots, edits metadata/retention fields, and validates resulting API state.

State and persistence behavior: snapshot manifests in the temporary repository are created and mutated.

Dependencies and integration points: covers manifest conversion, retention fields, API client routing, and repository write sessions.

Risks and test signals: source action APIs such as pause/resume/upload need additional source-manager focused tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/server/api_snapshots_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/server/api_sources.go -->
# sources/sync-backup/kopia/internal/server/api_sources.go

Purpose: implements APIs for listing known snapshot sources and creating/refreshing a source manager.

Important APIs/types/functions: `handleSourcesList` and `handleSourcesCreate`.

Control flow: list snapshots all current source managers and returns their source/status/counters. Create decodes a source request, ensures a manager exists for the source, refreshes status, and returns the updated source list or source response.

State and persistence behavior: source managers are runtime server state; source creation may cause manager startup but does not by itself write a snapshot.

Dependencies and integration points: bridges UI source pages, `sourceManager`, repository source lists, and scheduler refresh.

Risks and test signals: source manager lifecycle must be synchronized with repository refresh and policy changes. Tests cover snapshot counters and policy-triggered refresh.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/server/api_sources.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/server/api_sources_test.go -->
# sources/sync-backup/kopia/internal/server/api_sources_test.go

Purpose: tests source API counters and refresh behavior.

Important APIs/types/functions: `TestSnapshotCounters` and `TestSourceRefreshesAfterPolicy`.

Control flow: creates test sources/snapshots or policies, calls source APIs, and asserts source manager counters/status refresh as expected.

State and persistence behavior: temporary repository manifests and runtime source-manager state.

Dependencies and integration points: validates interaction between policies, snapshots, source managers, and API responses.

Risks and test signals: asynchronous refresh can be timing-sensitive; tests should avoid sleeps where possible.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/server/api_sources_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/server/api_tasks.go -->
# sources/sync-backup/kopia/internal/server/api_tasks.go

Purpose: exposes task manager state and controls through APIs.

Important APIs/types/functions: `handleTaskList`, `handleTaskInfo`, `handleTaskSummary`, `handleTaskLogs`, and `handleTaskCancel`.

Control flow: handlers read task lists, individual task info, summary counters, log text, or request task cancellation by ID from the server's `uitask.Manager`.

State and persistence behavior: reads and mutates task manager runtime state; persistent task logs depend on server `PersistentLogs` option.

Dependencies and integration points: used by UI to observe estimate, restore, repository connect, maintenance, and snapshot tasks.

Risks and test signals: cancellation must be idempotent and logs should not leak unrelated task data. Tests should cover missing task IDs, completed tasks, and cancellation propagation.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/server/api_tasks.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/server/api_ui_pref.go -->
# sources/sync-backup/kopia/internal/server/api_ui_pref.go

Purpose: stores and retrieves UI preferences for the server.

Important APIs/types/functions: `getUIPreferencesOrEmpty`, `handleGetUIPreferences`, and `handleSetUIPreferences`.

Control flow: get reads the preferences JSON file if configured and returns empty preferences when missing. Set decodes preferences and writes them to the configured file.

State and persistence behavior: persists JSON preferences to `Options.UIPreferencesFile`; no repository data is required.

Dependencies and integration points: available even when not connected to a repository through `handleUIPossiblyNotConnected`.

Risks and test signals: malformed files and write permission errors should return API errors. Tests cover get/set behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/server/api_ui_pref.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/server/api_ui_pref_test.go -->
# sources/sync-backup/kopia/internal/server/api_ui_pref_test.go

Purpose: tests UI preference API persistence.

Important APIs/types/functions: `TestUIPreferences`.

Control flow: starts a test server with a preferences file, gets default preferences, sets new preferences, and verifies subsequent retrieval.

State and persistence behavior: writes a temporary JSON preferences file.

Dependencies and integration points: validates not-connected-capable UI endpoint handling plus file persistence.

Risks and test signals: malformed existing JSON and filesystem permission failures need separate tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/server/api_ui_pref_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/server/api_user.go -->
# sources/sync-backup/kopia/internal/server/api_user.go

Purpose: returns information about the currently authenticated user.

Important APIs/types/functions: `handleCurrentUser`.

Control flow: reads Basic Auth username from the request and returns it in a serverapi response; wrapper authentication has already validated credentials when configured.

State and persistence behavior: stateless request inspection.

Dependencies and integration points: used by UI session/header code and registered as `/api/v1/current-user`.

Risks and test signals: when authentication is disabled, username may be empty. Tests should cover auth-enabled and auth-disabled modes.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/server/api_user.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/server/grpc_session.go -->
# sources/sync-backup/kopia/internal/server/grpc_session.go

Purpose: implements Kopia's repository gRPC session protocol over HTTP/2, including authentication, handshake, concurrent request dispatch, content/manifest operations, retention policy application, notifications, and gRPC routing.

Important APIs/types/functions: `grpcServerState`, `Server.Session`, `authenticateGRPCSession`, `handleInitialSessionHandshake`, `handleSessionRequest`, request handlers for content/manifest/prefetch/retention/notification operations, `accessDeniedResponse`, `errorResponse`, metadata conversion helpers, `RegisterGRPCHandlers`, `makeGRPCServerState`, `GRPCRouterHandler`, and `ShutdownGRPCServer`.

Control flow: `Session` requires a direct repository, authenticates metadata credentials, authorizes the user, performs an initial initialize-session handshake returning repository parameters, then opens a direct write session. Incoming requests are received in a loop, concurrency-limited by a weighted semaphore, processed in goroutines, and responses are serialized through `sendMutex`. Handlers check content or manifest access levels, parse IDs, perform repository operations, paginate manifest search when requested, and map errors to protocol error codes.

State and persistence behavior: content writes, manifest puts/deletes, retention policy application, flushes, and notifications mutate repository state or external notification side effects. Server state includes a lazily created gRPC server, semaphore, and send mutex.

Dependencies and integration points: connects remote repository clients to `repo.DirectRepositoryWriter`, auth/authz, OpenTelemetry trace context, content/manifest/object packages, notification packages, and HTTP router multiplexing.

Risks and test signals: request goroutine errors are reported through a one-slot channel, so later send failures may be dropped; write session lifetime spans the stream; authz label checks are security-critical. Tests should cover metadata auth, handshake ordering, concurrent requests, access denial, pagination, and graceful shutdown behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/server/grpc_session.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/server/htmlui_embed.go -->
# sources/sync-backup/kopia/internal/server/htmlui_embed.go

Purpose: exposes the bundled HTML UI filesystem when the `nohtmlui` build tag is not set.

Important APIs/types/functions: `AssetFile`.

Control flow: delegates to `htmluibuild.AssetFile()`.

State and persistence behavior: serves embedded/static build assets; no mutation.

Dependencies and integration points: `Server.ServeStaticFiles` uses this filesystem to serve the UI and patch `index.html`.

Risks and test signals: build dependency on generated `htmluibuild` assets must be available for normal builds.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/server/htmlui_embed.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/server/htmlui_fallback.go -->
# sources/sync-backup/kopia/internal/server/htmlui_fallback.go

Purpose: fallback HTML UI asset provider for `nohtmlui` builds.

Important APIs/types/functions: embedded `data` filesystem and `AssetFile`.

Control flow: returns an `http.FileSystem` backed by minimal embedded fallback content.

State and persistence behavior: read-only embedded assets.

Dependencies and integration points: allows server builds without full UI assets while keeping static serving code functional.

Risks and test signals: fallback UI is limited; build-tag tests should ensure both asset providers compile.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/server/htmlui_fallback.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/server/request_context.go -->
# sources/sync-backup/kopia/internal/server/request_context.go

Purpose: defines the internal request context and server interface abstraction used by API handlers and tests.

Important APIs/types/functions: `serverInterface`, `requestContext`, `muxVar`, and `queryParam`.

Control flow: the server wrapper captures HTTP writer/request, request body, current repository, and server interface. Handler helpers read mux route variables or URL query parameters.

State and persistence behavior: per-request in-memory data only.

Dependencies and integration points: API handlers depend on this instead of concrete `Server`, which simplifies testing and fake server implementations.

Risks and test signals: `serverInterface` is broad, so fake implementations must stay in sync with handler needs. Compile-time use across handlers is the primary guard.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/server/request_context.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/server/server.go -->
# sources/sync-backup/kopia/internal/server/server.go

Purpose: core HTTP API server implementation for Kopia, coordinating authentication, CSRF protection, request dispatch, repository lifecycle, source managers, mounts, tasks, maintenance, static UI serving, scheduler integration, and notifications.

Important APIs/types/functions: `Server`, `Options`, handler registration methods, `isAuthenticated`, auth cookie helpers, `requireAuth`, request wrapper helpers, `Refresh`, `SetRepository`, source-manager synchronization, `ServeStaticFiles`, `InitRepositoryAsync`, `RetryInitRepository`, `runSnapshotTask`, `runMaintenanceTask`, scheduler item generation, and `New`.

Control flow: setup methods register UI and control endpoints with appropriate auth/CSRF wrappers. Requests are authenticated, optionally checked for CSRF, body-read before handler execution, authorized by UI/control role, run under a context detached from request cancellation, and serialized as JSON or API errors. Repository changes stop old schedulers, unmount mounts, stop source managers, close repositories, start maintenance, sync sources, and start scheduler. Scheduler items trigger refresh, maintenance, and local-source snapshots.

State and persistence behavior: server holds repository pointer, source manager map, mount controller map, task manager, maintenance manager, scheduler, auth signing key, init task ID, and snapshot concurrency counters. It persists repository/config changes only through delegated APIs and writes task logs when persistent logs are enabled.

Dependencies and integration points: central integration point for `auth`, `repo`, `snapshot`, `policy`, `mount`, `scheduler`, `uitask`, notification, maintenance, and Gorilla mux.

Risks and test signals: lock ordering, async task startup, CSRF/session cookie generation, repository replacement cleanup, and snapshot concurrency are critical. Tests in this subset cover many API surfaces and authz checks; broader server tests should include shutdown, scheduler refresh, mount cleanup, and concurrent repository reconnects.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/server/server.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/server/server_authz_checks.go -->
# sources/sync-backup/kopia/internal/server/server_authz_checks.go

Purpose: implements CSRF token generation/validation and role checks for UI and server-control APIs.

Important APIs/types/functions: `kopiaSessionCookie`, `generateCSRFToken`, `validateCSRFToken`, `requireUIUser`, `requireServerControlUser`, `anyAuthenticatedUser`, and `handlerWillCheckAuthorization`.

Control flow: CSRF tokens are HMAC-SHA256 of the UI session cookie using the auth-cookie signing key and compared in constant time against the API client header. Validation can be disabled by options. Role checks compare Basic Auth username to configured UI or server-control users when authentication is enabled.

State and persistence behavior: relies on session cookie values and server signing key; no persistent storage.

Dependencies and integration points: used by `server.go` request wrappers and static UI index patching.

Risks and test signals: missing UI/control user options deny access when auth is enabled; token correctness depends on stable session cookie. Tests cover token generation and validation.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/server/server_authz_checks.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/server/server_authz_checks_test.go -->
# sources/sync-backup/kopia/internal/server/server_authz_checks_test.go

Purpose: tests CSRF token generation and validation.

Important APIs/types/functions: `TestGenerateCSRFToken` and `TestValidateCSRFToken`.

Control flow: constructs test server/options, generates expected tokens for session IDs, builds HTTP requests with cookies and headers, and asserts validation success/failure cases.

State and persistence behavior: in-memory server signing key and request cookies only.

Dependencies and integration points: protects UI API CSRF enforcement used by all mutating UI handlers.

Risks and test signals: should include disabled-CSRF option and missing cookie/header cases to guard request wrapper behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/server/server_authz_checks_test.go -->
