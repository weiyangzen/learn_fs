# subset-b-009780 research

Grouped research for rclone library files covering build information, in-memory caches, call-stack detection, daemon spawning, debug wrappers, directory ID caching, disk usage probes, and filename encoding. Each section is source-tree aligned and bounded by reconciliation markers.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/buildinfo/osversion_windows.go -->
# sources/user-network-fs/rclone/lib/buildinfo/osversion_windows.go

## Purpose
This Windows-only buildinfo file builds the user-facing OS version and kernel strings reported by rclone. It augments generic `gopsutil` host information with Windows registry release labels and architecture annotations, while normalizing noisy Windows kernel output.

## Important APIs, types, and functions
- `GetOSVersion() (osVersion, osKernel string)` is the exported entry point for Windows build information.
- `getRegistryVersionString(name string) string` reads string values such as `DisplayVersion` and `ReleaseId` from `HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion`.
- `regVersionKeyUTF16` caches the registry key path as a UTF-16 pointer for Win32 calls.

## Control flow
`GetOSVersion` first asks `host.PlatformInformation` for platform and version, then asks `host.KernelVersion` for the kernel. If the OS version already contains the kernel string, it removes the duplicate. It also collapses kernel strings of the form `major.minor.build.revision Build build.revision` when the build portion is repeated. Next it reads `DisplayVersion`, falling back to `ReleaseId`, and appends that friendly release name. Finally it reads `host.KernelArch`; 64-bit arches add `(64 bit)` to the OS version and append the raw arch to the kernel string.

## State and persistence behavior
The file has no persistent state. It reads live host and registry state each time `GetOSVersion` runs. Registry handles are opened per lookup and closed with `RegCloseKey`.

## Dependencies and integration points
The code depends on `github.com/shirou/gopsutil/v4/host` for platform/kernel/architecture probes and `golang.org/x/sys/windows` for registry access. It integrates with the wider buildinfo package as the Windows implementation of OS version reporting.

## Risks and edge cases
Registry access can fail due to permissions, missing keys, or non-standard Windows versions; failures intentionally degrade to partial host information. The registry buffer is sized from the reported byte length and interpreted as UTF-16, so type mismatches or malformed data would return odd strings rather than validated semantic versions. The kernel normalization regex is narrow and only handles one duplicated-build pattern.

## Test signals
No direct tests are in this subset. Coverage is likely indirect through version-reporting commands on Windows; non-Windows CI will not compile this file.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/buildinfo/osversion_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/buildinfo/snap.go -->
# sources/user-network-fs/rclone/lib/buildinfo/snap.go

## Purpose
This tiny build-tag-gated file records that the binary was built as a Snap package.

## Important APIs, types, and functions
- The file is compiled only with the `snap` build tag.
- `init()` appends `"snap"` to the package-level `Tags` slice.

## Control flow
During package initialization, the build tag causes this file to participate in the build and its `init` function mutates `Tags`. Later `GetLinkingAndTags` includes this tag in sorted build-tag output.

## State and persistence behavior
The only state change is in-process initialization of `buildinfo.Tags`. There is no persistent state.

## Dependencies and integration points
It depends on `tags.go` defining `Tags`. It integrates with packaging/version display logic that reports build tags.

## Risks and edge cases
The correctness depends entirely on build tooling passing the `snap` tag. If omitted, Snap builds will not self-identify. If other init functions also append tags, final ordering is handled later by sorting.

## Test signals
No local tests are present; validation is build-configuration based.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/buildinfo/snap.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/buildinfo/tags.go -->
# sources/user-network-fs/rclone/lib/buildinfo/tags.go

## Purpose
This file owns build-tag reporting for rclone. It stores tags discovered by build-specific files and converts them into a displayable linking mode plus tag string.

## Important APIs, types, and functions
- `var Tags []string` is the mutable package-level registry populated by init functions in this and other packages/files.
- `GetLinkingAndTags() (linking, tagString string)` returns `"static"` or `"dynamic"` and a sorted tag list or `"none"`.

## Control flow
`GetLinkingAndTags` assumes static linking, walks `Tags`, treats the special tag `"cgo"` as evidence of dynamic linking, and excludes it from the displayed tag list. All remaining tags are sorted and joined by spaces; an empty list is represented as `"none"`.

## State and persistence behavior
`Tags` is process-global mutable state. It is initialized during package startup and then read without locking, so callers assume tag mutation only happens at init time.

## Dependencies and integration points
It depends only on `sort` and `strings`, but is extended by build-tag files such as `snap.go` and comments note `cmd/cmount/mount.go` and `cmd/selfupdate/noselfupdate.go` also append tags.

## Risks and edge cases
Late mutation of `Tags` would race with readers because no mutex is used. Unknown tags are displayed as-is, and duplicate tags are not deduplicated. The `"cgo"` tag has semantic meaning beyond display, so producers must use that exact spelling.

## Test signals
No tests in this subset directly exercise tag formatting. Any version/build-info tests should verify sorted output and cgo handling.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/buildinfo/tags.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/cache/cache.go -->
# sources/user-network-fs/rclone/lib/cache/cache.go

## Purpose
`cache.go` implements a small thread-safe string-keyed cache for arbitrary values. Entries expire after a period of disuse, can store creation errors for negative caching, can be pinned against expiry, and can run a finalizer when removed.

## Important APIs, types, and functions
- `Cache` holds the protected map, expiry settings, timer state, and finalizer.
- `cacheEntry` stores value, cached error, key, `lastUsed`, and `pinCount`.
- `CreateFunc` creates values and reports whether an error should still be cached.
- Public operations include `New`, `SetExpireDuration`, `SetExpireInterval`, `Get`, `PutErr`, `Put`, `GetMaybe`, `Delete`, `DeletePrefix`, `Rename`, `Clear`, `Entries`, `SetFinalizer`, `Pin`, `Unpin`, and `EntriesWithPinCount`.
- `cacheExpire` is the timer callback that removes old unpinned entries.

## Control flow
`Get` locks the cache, returns an existing entry when present, or unlocks while running the caller's `CreateFunc` so recursive cache use cannot deadlock. If creation returns an error with `ok == false`, the error is returned but not cached. Otherwise the new entry is inserted unless caching is disabled, then `used` updates `lastUsed` and starts an expiry timer if needed. Removal functions call `finalize` before deletion. `Rename` prefers an existing `newKey` entry, finalizes the displaced old value if distinct, and otherwise moves `oldKey` to `newKey`.

## State and persistence behavior
All state is in memory. Expiry uses `time.AfterFunc`; the boolean `expireRunning` ensures only one scheduled expiry chain exists while the cache has live entries. `SetExpireDuration(<=0)` disables caching, while `SetExpireInterval(<=0)` effectively disables periodic expiry by setting a very long interval.

## Dependencies and integration points
The package depends only on the Go standard library. It is a generic utility used by higher-level rclone components that need short-lived process-local memoization, including caches that need finalizers for resource cleanup.

## Risks and edge cases
`Get` has a duplicate-creation race: two goroutines missing the same key can both run `create`, and the later insert wins. That is acceptable for simple memoization but unsafe for create functions with non-idempotent side effects. `Pin`/`Unpin` can drive `pinCount` negative; expiry treats non-positive as unpinned. Finalizers run while the cache mutex is held, so slow or reentrant finalizers can block the cache or deadlock. Timer callbacks are not cancellable after `Clear`; they will run later and observe the empty map.

## Test signals
`cache_test.go` covers ordinary get reuse, cached errors, uncached errors, explicit put, disabled caching, expiry timing, pinning, clearing, entry counts, maybe-get, deletion, prefix deletion, rename collision behavior, and finalizer calls.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/cache/cache.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/cache/cache_test.go -->
# sources/user-network-fs/rclone/lib/cache/cache_test.go

## Purpose
This file tests the cache package's creation, negative caching, expiry, pinning, deletion, rename, and finalization semantics.

## Important APIs, types, and functions
- `setup(t)` builds a fresh `Cache` and a `CreateFunc` with deterministic responses for root, file, and error paths.
- Tests include `TestGet`, `TestGetFile`, `TestGetError`, `TestPutErr`, `TestPut`, `TestCacheExpire`, `TestCacheNoExpire`, `TestCachePin`, `TestClear`, `TestEntries`, `TestGetMaybe`, `TestDelete`, `TestDeletePrefix`, `TestCacheRename`, and `TestCacheFinalize`.

## Control flow
Most tests create a cache, perform one or more public operations, and inspect either public counts or internal map state under lock. Expiry tests shorten intervals and mutate `lastUsed` to avoid waiting for default durations. Finalizer tests install a counting finalizer and exercise every removal path.

## State and persistence behavior
Tests use package-level `called` and sentinel errors to assert create-call behavior. Cache state is in memory only. Some tests directly inspect or mutate private fields because they are in package `cache`, not `cache_test`.

## Dependencies and integration points
The tests use `testing`, `time`, `errors`, `fmt`, and `testify` assertions. They are direct unit tests for `cache.go` and do not require remote services.

## Risks and edge cases
`TestCacheExpire` uses real timers and sleeps, so it can be timing-sensitive on overloaded CI. The tests do not cover concurrent access or duplicate create races. They also do not check finalizer reentrancy or negative pin counts.

## Test signals
The suite is a strong signal for the documented single-threaded semantics: errors cache only when requested, disabled caches keep nothing, pinned stale entries survive expiry, prefix deletion counts exact matches, rename prefers existing destination values, and all removal paths call finalizers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/cache/cache_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/caller/caller.go -->
# sources/user-network-fs/rclone/lib/caller/caller.go

## Purpose
This package provides a small runtime helper for detecting whether a named function appears higher in the current call stack.

## Important APIs, types, and functions
- `Present(functionName string) bool` scans stack frames and returns true when a frame's fully qualified function name has the requested suffix.

## Control flow
`Present` collects up to 48 program counters with `runtime.Callers(3, ...)`, skipping `runtime.Callers`, `Present`, and the immediate caller. It iterates frames with `runtime.CallersFrames` and checks `strings.HasSuffix(f.Function, functionName)`.

## State and persistence behavior
The function has no persistent state. It samples the current goroutine's stack at call time.

## Dependencies and integration points
It depends on `runtime` and `strings`. Callers can use it for behavior switches that need to know whether a higher-level function is already on the call stack.

## Risks and edge cases
The suffix match can produce false positives when unrelated functions share suffixes. The fixed 48-frame buffer can miss very deep callers. It intentionally ignores the immediate caller, so direct checks for the calling function return false.

## Test signals
`caller_test.go` verifies not-found behavior, immediate-caller exclusion, and detection when wrapped in an anonymous function. Benchmarks measure shallow and 100-level stack performance.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/caller/caller.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/caller/caller_test.go -->
# sources/user-network-fs/rclone/lib/caller/caller_test.go

## Purpose
This file validates and benchmarks `caller.Present`.

## Important APIs, types, and functions
- `TestPresent` checks negative lookup, immediate-caller skipping, and successful detection of a higher frame.
- `BenchmarkPresent` measures a shallow miss.
- `BenchmarkPresent100` measures a miss under 100 recursive stack frames.

## Control flow
The unit test calls `Present` directly and from an anonymous nested function. The recursive benchmark builds a deep stack once, then loops calls to `Present("NotFound")` from that depth.

## State and persistence behavior
No persistent state is used.

## Dependencies and integration points
The tests use `testing` and `testify/assert`. They directly exercise `caller.go`.

## Risks and edge cases
Benchmarks only cover misses, not successful early or late matches. The unit test does not cover suffix collision behavior or stacks deeper than the 48-frame capture limit.

## Test signals
The direct false result for `"TestPresent"` documents that `Present` skips its immediate caller; the nested true result documents intended higher-stack detection.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/caller/caller_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/daemonize/daemon_other.go -->
# sources/user-network-fs/rclone/lib/daemonize/daemon_other.go

## Purpose
This build-tagged file provides the daemonize API stub for platforms where rclone does not support daemon mode: non-Unix platforms and AIX.

## Important APIs, types, and functions
- Build constraint: `!unix || aix`.
- `errNotSupported` reports that daemon mode is unsupported on the current `runtime.GOOS`.
- `StartDaemon(args []string) (*os.Process, error)` always returns the unsupported error.
- `Check(daemon *os.Process) error` also always returns the unsupported error.

## Control flow
There is no branching beyond returning the package-level error. The exported function signatures match the Unix implementation.

## State and persistence behavior
No daemon process is created and no state is persisted.

## Dependencies and integration points
It imports `fmt`, `os`, and `runtime`. It lets higher-level mount/daemon code compile uniformly while receiving a platform-specific unsupported error.

## Risks and edge cases
Callers must treat the returned error as expected unsupported behavior. Because `Check` ignores its argument, passing nil or a dead process makes no difference on these platforms.

## Test signals
No tests in this subset target the stub directly. Platform build coverage is the main signal.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/daemonize/daemon_other.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/daemonize/daemon_unix.go -->
# sources/user-network-fs/rclone/lib/daemonize/daemon_unix.go

## Purpose
This Unix implementation starts a background twin of the current rclone process and provides a non-blocking health check for the child. It is designed to emulate daemonization without unsafe `fork` in a Go process with goroutines.

## Important APIs, types, and functions
- Build constraint: `unix && !aix`.
- `StartDaemon(args []string) (*os.Process, error)` starts the child process or returns nil in a process already marked daemonized.
- `argsToEnv(origArgs, origEnv []string) (args, env []string)` converts mount-helper style `--flag` and `--flag=value` options to `RCLONE_*` environment variables.
- `Check(daemon *os.Process) error` uses `unix.Wait4(..., WNOHANG, ...)` to detect child exit.

## Control flow
`StartDaemon` first checks `fs.IsDaemon` to avoid spawning again. It marks the child via `fs.DaemonMarkVar=fs.DaemonMarkChild`, resolves the executable path, replaces `args[0]` with that path when args are provided, optionally moves flags into environment variables, opens `/dev/null` for stdin/stdout/stderr, and starts a process with `Setsid: false`. `Check` performs a non-blocking wait: no exited child returns nil, an exited child returns an error with its exit code, and wait errors are propagated.

## State and persistence behavior
State is external process state plus environment variables passed to the child. No files are persisted. The child has standard streams redirected to `/dev/null`.

## Dependencies and integration points
The file depends on `github.com/rclone/rclone/fs` for daemon markers and argument-passing policy, and `golang.org/x/sys/unix` for wait status. It integrates with mount helpers and command flows that need to background rclone while preserving processed options.

## Risks and edge cases
`StartDaemon` mutates the provided `args` slice by replacing element zero. The `/dev/null` file is not explicitly closed after `StartProcess`. `Setsid` is deliberately false for autofs process-group expectations, so this is not classic full daemon detachment. `argsToEnv` only handles long flags and assumes no `--flag value` or short-flag forms. `Check` only reports normal exit status; signal termination returns nil unless represented differently by wait status handling.

## Test signals
No tests in this subset exercise daemon spawning. Behavior is platform-sensitive and would need Unix integration tests around environment conversion, process lifecycle, and mount-helper expectations.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/daemonize/daemon_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/debug/common.go -->
# sources/user-network-fs/rclone/lib/debug/common.go

## Purpose
This file exposes small wrappers around Go runtime debug knobs so rclone code can use package-local helpers for GC percentage and memory-limit changes.

## Important APIs, types, and functions
- `SetGCPercent(percent int) int` calls `runtime/debug.SetGCPercent`.
- `SetMemoryLimit(limit int64) int64` calls `runtime/debug.SetMemoryLimit`.

## Control flow
Both functions are direct pass-throughs returning the previous runtime setting from the Go runtime.

## State and persistence behavior
The functions mutate process-wide runtime settings. The changes last for the life of the process or until changed again; nothing is persisted to disk.

## Dependencies and integration points
The only dependency is the standard `runtime/debug` package. The wrappers are integration points for code that wants stable rclone-local symbols across Go versions.

## Risks and edge cases
These settings are global and can affect performance and memory use across the whole process. There is no validation or synchronization here; callers must supply sensible values.

## Test signals
No direct tests are present in this subset. Runtime behavior is inherited from the Go standard library.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/debug/common.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/dircache/dircache.go -->
# sources/user-network-fs/rclone/lib/dircache/dircache.go

## Purpose
`dircache.go` implements rclone's directory path-to-ID cache for backends whose directories have opaque IDs. It maps relative paths to IDs and IDs back to paths, discovers or creates missing parent directories, and helps prepare safe directory moves.

## Important APIs, types, and functions
- `DirCache` stores forward/inverse maps plus root state: true root ID, configured root path, current root ID, root parent ID, and whether the configured root has been found.
- `DirCacher` is the backend interface: `FindLeaf(ctx, parentID, leaf)` and `CreateDir(ctx, parentID, leaf)`.
- Basic cache methods include `Get`, `GetInv`, `Put`, `Flush`, `FlushDir`, `String`, and `SetRootIDAlias`.
- Path/root methods include `SplitPath`, `FindDir`, `_findDir`, `FindPath`, `FindRoot`, `_findRoot`, `FoundRoot`, `RootID`, `RootParentID`, and `ResetRoot`.
- `DirMove` performs preflight lookup and directory creation for a backend directory move.

## Control flow
`New` initializes empty maps and resets the root to the true root ID. `FindDir` takes the root-state mutex, ensures `FindRoot` has run, and recursively resolves each path component with `_findDir`. `_findDir` returns cached IDs when possible, otherwise resolves the parent, calls backend `FindLeaf`, optionally calls `CreateDir`, and caches the result. `_findRoot` resolves the configured root from the true root, records its parent ID, flushes the old tree, and re-roots the cache so `""` maps to the configured root ID. `RootParentID` can resolve the parent without creating the root itself. `DirMove` refuses root moves, creates destination parents, verifies destination absence, then resolves source parent and source ID.

## State and persistence behavior
The cache is purely in-memory; backend `CreateDir` and actual move operations persist remote state. `cacheMu` protects map access, while `mu` serializes root discovery and recursive backend lookups. `ResetRoot` clears cached paths and restores the absolute root mapping.

## Dependencies and integration points
The package depends on `context`, `path`, `strings`, `sync`, and rclone `fs` errors such as `ErrorDirNotFound` and `ErrorDirExists`. It is used by ID-based backends including cloud storage remotes to translate rclone paths into backend directory IDs.

## Risks and edge cases
Duplicate names in a backend can make path-to-ID mappings ambiguous; backends must define `FindLeaf` behavior. `SetRootIDAlias` intentionally avoids locking because it is called from backend `FindLeaf`, so misuse outside that path can race. `FlushDir` removes entries by string prefix and assumes slash-separated normalized paths. `RootParentID` returns errors for true-root cases. `DirMove` only prepares IDs; callers must flush source cache after performing the remote move.

## Test signals
No tests for `dircache` are in this subset, but many backend integration tests exercise it indirectly. Important missing direct signals include concurrent lookup behavior, duplicate-name handling, root aliasing, and `DirMove` cache invalidation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/dircache/dircache.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/diskusage/diskusage.go -->
# sources/user-network-fs/rclone/lib/diskusage/diskusage.go

## Purpose
This file defines the cross-platform disk usage package contract and shared return type.

## Important APIs, types, and functions
- `Info` contains `Free`, `Available`, and `Total` byte counts.
- `ErrUnsupported` is returned by platform implementations that cannot provide disk usage.

## Control flow
There is no runtime flow in this file. Platform-specific files provide `New(dir string)`.

## State and persistence behavior
No state is stored or persisted.

## Dependencies and integration points
The only dependency is `errors`. All platform-specific `diskusage_*` files share this type and error value so callers can handle unsupported platforms consistently.

## Risks and edge cases
The semantic difference between `Free` and `Available` depends on platform syscalls and filesystem privilege rules. Callers must not assume every platform supports the probe.

## Test signals
`diskusage_test.go` consumes `Info` and `ErrUnsupported` through the platform `New` implementation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/diskusage/diskusage.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/diskusage/diskusage_netbsd.go -->
# sources/user-network-fs/rclone/lib/diskusage/diskusage_netbsd.go

## Purpose
This NetBSD-specific implementation reports disk space by calling `unix.Statvfs`.

## Important APIs, types, and functions
- Build constraint: `netbsd`.
- `New(dir string) (Info, error)` fills `Info` from `unix.Statvfs_t`.

## Control flow
`New` calls `unix.Statvfs(dir, &statfs)`, propagates errors, and multiplies block counts by `Bsize` for free, available, and total bytes.

## State and persistence behavior
No state is persisted. The returned values are a point-in-time filesystem snapshot.

## Dependencies and integration points
It depends on `golang.org/x/sys/unix`. It satisfies the shared `diskusage.New` API on NetBSD.

## Risks and edge cases
Block-field sizes vary by OS, which is why values are explicitly cast to `uint64`. Multiplication can theoretically overflow on extremely large filesystems, matching the package's unsigned-byte-count model.

## Test signals
`diskusage_test.go` will exercise this file only on NetBSD, checking nonzero total and ordering relationships.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/diskusage/diskusage_netbsd.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/diskusage/diskusage_openbsd.go -->
# sources/user-network-fs/rclone/lib/diskusage/diskusage_openbsd.go

## Purpose
This OpenBSD-specific implementation reports disk space using `unix.Statfs`.

## Important APIs, types, and functions
- Build constraint: `openbsd`.
- `New(dir string) (Info, error)` maps `unix.Statfs_t` fields into byte counts.

## Control flow
`New` calls `unix.Statfs`, returns syscall errors directly, and computes byte values from `F_bfree`, `F_bavail`, and `F_blocks` multiplied by `F_bsize`.

## State and persistence behavior
No state is stored. Results reflect current filesystem state for the given directory.

## Dependencies and integration points
It depends on `golang.org/x/sys/unix` and implements the common diskusage API for OpenBSD builds.

## Risks and edge cases
The mapping uses OpenBSD's `F_*` field names, which differ from other Unix variants. As with other implementations, large multiplications may overflow `uint64` only in extreme cases.

## Test signals
The generic diskusage test runs this implementation on OpenBSD and asserts sane totals.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/diskusage/diskusage_openbsd.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/diskusage/diskusage_test.go -->
# sources/user-network-fs/rclone/lib/diskusage/diskusage_test.go

## Purpose
This file provides a platform-generic smoke test for `diskusage.New`.

## Important APIs, types, and functions
- `TestNew` calls `New(".")`, skips on `ErrUnsupported`, logs fields, and asserts basic size relationships.

## Control flow
The test probes the current working directory. Unsupported platforms are explicitly skipped. Supported platforms must return no error, a nonzero total, total greater than free and available, and free greater than or equal to available.

## State and persistence behavior
No persistent state is changed. The test reads live filesystem statistics.

## Dependencies and integration points
The test uses `testify/assert` and `testify/require`, and integrates with whichever build-tagged `New` implementation is compiled.

## Risks and edge cases
The assertion `Total > Free` may fail on unusual or synthetic filesystems that report an empty filesystem as all free, and live filesystem stats can vary. The test is intentionally a smoke test rather than exact accounting.

## Test signals
It confirms the compiled platform implementation can query the local filesystem and returns internally consistent byte counts, or that the platform cleanly reports `ErrUnsupported`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/diskusage/diskusage_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/diskusage/diskusage_unix.go -->
# sources/user-network-fs/rclone/lib/diskusage/diskusage_unix.go

## Purpose
This implementation covers common Unix-like platforms using `unix.Statfs`.

## Important APIs, types, and functions
- Build constraint: `aix || android || darwin || dragonfly || freebsd || ios || linux`.
- `New(dir string) (Info, error)` maps `unix.Statfs_t` fields into `Info`.

## Control flow
`New` calls `unix.Statfs`, returns errors directly, and computes byte counts as `Bfree * Bsize`, `Bavail * Bsize`, and `Blocks * Bsize`.

## State and persistence behavior
No state is persisted. The call reads current filesystem usage for the path.

## Dependencies and integration points
It depends on `golang.org/x/sys/unix` and provides the package API for Linux, macOS/iOS, Android, and several BSD-like systems.

## Risks and edge cases
Different platforms may define block fields with different signedness or widths, hence explicit conversion. Some filesystems report fragment sizes differently from block sizes; this implementation chooses `Bsize` consistently with its historical contract.

## Test signals
`diskusage_test.go` is the direct smoke test on these platforms.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/diskusage/diskusage_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/diskusage/diskusage_unsupported.go -->
# sources/user-network-fs/rclone/lib/diskusage/diskusage_unsupported.go

## Purpose
This file provides the `diskusage.New` implementation for platforms where disk usage is unsupported.

## Important APIs, types, and functions
- Build constraint: `illumos || js || plan9 || solaris`.
- `New(dir string) (Info, error)` returns zero `Info` and `ErrUnsupported`.

## Control flow
The function immediately returns without inspecting `dir`.

## State and persistence behavior
No state is read or changed.

## Dependencies and integration points
It depends only on shared package symbols. Callers and tests can branch on `ErrUnsupported`.

## Risks and edge cases
Callers must handle unsupported platforms gracefully. The function does not validate paths because no platform syscall is attempted.

## Test signals
`diskusage_test.go` skips when this implementation returns `ErrUnsupported`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/diskusage/diskusage_unsupported.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/diskusage/diskusage_windows.go -->
# sources/user-network-fs/rclone/lib/diskusage/diskusage_windows.go

## Purpose
This Windows implementation reports disk usage with the Win32 `GetDiskFreeSpaceEx` API.

## Important APIs, types, and functions
- Build constraint: `windows`.
- `New(dir string) (Info, error)` converts the path to UTF-16 and fills `Available`, `Total`, and `Free`.

## Control flow
`New` calls `windows.StringToUTF16Ptr(dir)`, then `windows.GetDiskFreeSpaceEx(dir16, &info.Available, &info.Total, &info.Free)`, returning the populated `Info` and syscall error.

## State and persistence behavior
No state is persisted. The result is a live volume-space snapshot.

## Dependencies and integration points
It depends on `golang.org/x/sys/windows` and implements the common diskusage API for Windows builds.

## Risks and edge cases
The Win32 API's argument order distinguishes caller-available bytes from total and total-free bytes; this file maps that order directly to `Info`. Invalid paths, inaccessible drives, or special device paths return Windows errors.

## Test signals
`diskusage_test.go` runs on Windows and validates basic totals.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/diskusage/diskusage_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/encoder/encoder.go -->
# sources/user-network-fs/rclone/lib/encoder/encoder.go

## Purpose
`encoder.go` implements rclone's configurable filename encoder. It translates characters and name patterns that are invalid or problematic on particular storage systems into reversible Unicode-safe representations, and converts names between backend-specific encodings and rclone's standard encoding.

## Important APIs, types, and functions
- `QuoteRune` is the escape marker used when input already contains an encoded-looking rune.
- `MultiEncoder` is a bitmask implementing `Encoder`, `pflag.Value`, and `fmt.Scanner` style parsing.
- `Encode*` constants select character classes: slash, Windows punctuation, quotes, hash/percent, control characters, leading/trailing spaces or periods, invalid UTF-8, dot names, and more.
- Synthetic masks include `EncodeWin` and `EncodeHashPercent`.
- `Encoder` defines `Encode`, `Decode`, `FromStandardPath`, `FromStandardName`, `ToStandardPath`, and `ToStandardName`.
- Alias helpers `alias`, `ValidStrings`, `String`, `Set`, `Type`, and `Scan` provide text configuration.
- `MultiEncoder.Encode` and `MultiEncoder.Decode` implement reversible transformation.
- `appendQuotedBytes` and `appendUnquotedByte` handle invalid UTF-8 byte escaping.
- `Identity`, `FromStandardPath`, `FromStandardName`, `ToStandardPath`, and `ToStandardName` provide generic conversion helpers.

## Control flow
Initialization registers human-readable names for every bitmask. `Set` parses comma-separated names or numeric bit values into a mask. `Encode` short-circuits raw and empty names, handles special dot names, strips at most one configured prefix-only and suffix-only character into encoded prefix/suffix strings, then scans for the first rune needing transformation. It writes unchanged leading bytes, then maps configured ASCII punctuation to fullwidth variants, NUL/control/CR/LF/DEL to symbol-for-control runes, encoded-looking input to `QuoteRune` plus the original rune, and optionally invalid UTF-8 bytes to quoted hex pairs. `Decode` mirrors this flow: it handles dot names, reverses prefix/suffix substitutions, scans for encoded runes, tracks quote state, decodes fullwidth/control symbols back to raw characters unless quoted, and reconstructs invalid UTF-8 bytes when that flag is enabled.

## State and persistence behavior
Package-level alias maps are initialized once and then read. Encoding itself is stateless and deterministic. No filesystem or persistent state is touched; persistence implications appear when encoded names are stored on remotes.

## Dependencies and integration points
The file depends on standard packages `bytes`, `fmt`, `io`, `sort`, `strconv`, `strings`, and `unicode/utf8`. It is a central integration point for rclone backends: each backend advertises or configures an encoder to map remote object names into rclone's standard namespace without collisions.

## Risks and edge cases
Reversibility depends on quote handling being exactly symmetrical for every encoded rune. Prefix and suffix handling intentionally transforms only one leading and one trailing character according to priority, which matters for names with multiple restricted edge characters. Invalid UTF-8 handling is byte-oriented and interacts with Go's `range` replacement-rune behavior. `Set` accepts numeric masks, so users can enable unknown future bits that `String` displays as hex and `Encode` may ignore. Because path conversion splits on `/`, slash encoding must be applied to path components rather than whole already-separated standard paths.

## Test signals
No encoder tests are included in this subset, but comments point to `fstests/fstests/fstests.go` `FsEncoding` coverage. Critical test signals should include encode/decode round trips for every flag, quote collisions, dot names, leading/trailing variants, invalid UTF-8 bytes, and path conversion between `Standard` and backend encoders.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/encoder/encoder.go -->
