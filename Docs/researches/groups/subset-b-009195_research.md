# subset-b-009195 research

Grouped research report for Syncthing filesystem, GeoIP, HTTP cache, and ignore matcher files. Each section preserves the exact source path and is wrapped for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/fs/basicfs_test.go -->
# sources/sync-backup/syncthing/lib/fs/basicfs_test.go

## Purpose
Tests the real `BasicFilesystem` implementation against OS-backed temporary directories. It verifies path rooting, permissions, ownership, timestamps, creation, symlink behavior, directory enumeration, globbing, disk usage, xattrs, and walk integration.

## Important APIs, Types, and Functions
`setup` returns a `*BasicFilesystem` and temp root. Tests exercise `Chmod`, `Lchown`, `Chtimes`, `Create`, `CreateSymlink`, `DirNames`, `Glob`, `Usage`, `rooted`, `newBasicFilesystem`, `rel`, `GetXattr`, `SetXattr`, and walk helpers from `walkfs_test.go`. `testXattrFilter` limits xattr tests to `user.test-*`.

## Control Flow
Each test builds real filesystem state with `os` calls, invokes the `BasicFilesystem` method under test with root-relative paths, then validates OS-level results. Path-rooting tests table-drive allowed canonicalizations and rejected upward traversal. Xattr tests write a set, read it back, mutate/remove/add attributes, and verify sorted round-trip state.

## State and Persistence Behavior
State is temporary on-disk content under `t.TempDir`. Tests mutate permissions, ownership, modtimes, symlinks, xattrs, and directories. Root containment is validated without touching outside paths.

## Dependencies and Integration Points
Uses `build` platform flags, `protocol.Xattr`, `syscall`, `rand`, and shared walk tests. Platform skips handle Windows symlink/chown gaps and unsupported xattr filesystems.

## Risks
The tests rely on host filesystem capabilities, root privileges for chown, and xattr support. Some checks tolerate timestamp granularity with a three-second window. Rooting table coverage is broad and safety-critical.

## Test Signals
Strong signal for root escape prevention, path normalization, xattr reconciliation, and basic local filesystem semantics across supported platforms.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/fs/basicfs_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/fs/basicfs_unix.go -->
# sources/sync-backup/syncthing/lib/fs/basicfs_unix.go

## Purpose
Provides non-Windows `BasicFilesystem` behavior for symlinks, hide/unhide no-ops, ownership, removal, filesystem roots, and watch path normalization.

## Important APIs, Types, and Functions
Defines `alwaysOpenFlags = syscall.O_NOFOLLOW`, `CreateSymlink`, `ReadSymlink`, `Hide`, `Unhide`, `Roots`, `Lchown`, `Remove`, `unrootedChecked`, `rel`, `evalSymlinks`, and `watchPaths`.

## Control Flow
All public operations first call `f.rooted` to canonicalize and constrain root-relative names. `Lchown` parses UID/GID strings as integers and calls `os.Lchown`. `watchPaths` resolves the configured root through symlinks, roots the watched name under that canonical root, and returns a notify recursive path plus allowed root list.

## State and Persistence Behavior
Creates symlink entries, changes file ownership, or removes a rooted path. `Hide` and `Unhide` only validate root containment because Unix hiding would require renaming dot prefixes.

## Dependencies and Integration Points
Used by `basicfs.go`, `basicfs_watch.go`, and platform data/xattr code on Unix-like builds. `O_NOFOLLOW` protects final path components from symlink traversal when opening files.

## Risks
`watchPaths` depends on `filepath.EvalSymlinks`; broken symlinked roots prevent watching. `unrootedChecked` is prefix-based after root normalization, so roots must include a single trailing separator to avoid sibling false positives. Ownership parsing rejects non-numeric IDs on Unix.

## Test Signals
Covered by `basicfs_test.go`, `basicfs_watch_test.go`, and symlink walk tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/fs/basicfs_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/fs/basicfs_watch.go -->
# sources/sync-backup/syncthing/lib/fs/basicfs_watch.go

## Purpose
Implements recursive file watching for `BasicFilesystem` using `github.com/syncthing/notify`, normalizing backend events into Syncthing `fs.Event` values.

## Important APIs, Types, and Functions
`backendBuffer` sizes the notify channel. `Watch` prepares paths and masks, installs `notify.WatchWithFilter`, handles inotify limit errors, and starts `watchLoop`. `watchLoop` drains overflow, validates UTF-8, converts absolute paths to relative names, applies ignore rules, sends events and fatal errors, and stops notify on context cancellation. `eventType` maps remove masks to `Remove`, everything else to `NonRemove`.

## Control Flow
Setup calls platform `watchPaths`, constructs event masks from `subEventMask` and optional `permEventMask`, and passes a filter that drops invalid or ignorable absolute paths. Runtime loop first detects full backend buffer and emits a broad rescan event for the watched root, then processes backend events or context cancellation.

## State and Persistence Behavior
No persistent state. Runtime state is channels, notify backend registration, and context lifetime. Overflow intentionally coalesces lost events into a root-level non-remove event.

## Dependencies and Integration Points
Depends on platform event mask files, `unrootedChecked`, `Matcher.Match`, and `ignoreresult` semantics. Integrated through `Filesystem.Watch`.

## Risks
Incorrect platform masks can miss changes or misclassify renames. Fatal outside-root events stop the watcher. Overflow uses `len(channel) == backendBuffer`, which is a heuristic sensitive to backend scheduling. Invalid UTF-8 paths are silently ignored.

## Test Signals
`basicfs_watch_test.go` covers ignores, includes, rename semantics, overflow, outside-root errors, symlinked roots, subpath watches, modtime changes, and Linux inotify-limit interpretation.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/fs/basicfs_watch.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/fs/basicfs_watch_errors_linux.go -->
# sources/sync-backup/syncthing/lib/fs/basicfs_watch_errors_linux.go

## Purpose
Classifies Linux notify setup errors that indicate exhausted inotify watch limits, enabling a user-facing remediation message.

## Important APIs, Types, and Functions
`reachedMaxUserWatches(err error) bool` unwraps `*os.PathError`, then checks `syscall.Errno` for `24` and `28`.

## Control Flow
Called from `BasicFilesystem.Watch` when `notify.WatchWithFilter` fails. A recognized error is replaced with a Syncthing FAQ message about increasing inotify limits.

## State and Persistence Behavior
No state or persistence.

## Dependencies and Integration Points
Linux-only build. Coupled to notify/inotify behavior and `basicfs_watch.go` error reporting.

## Risks
The errno checks are numeric and intentionally broad: `EMFILE` and `ENOSPC` can have meanings outside inotify in other contexts, but here they occur during watch setup.

## Test Signals
`TestWatchErrorLinuxInterpretation` validates errno 24 and 28 are recognized and ordinary errors are not.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/fs/basicfs_watch_errors_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/fs/basicfs_watch_errors_others.go -->
# sources/sync-backup/syncthing/lib/fs/basicfs_watch_errors_others.go

## Purpose
Provides the non-Linux stub for inotify-limit error classification.

## Important APIs, Types, and Functions
`reachedMaxUserWatches(_ error) bool` always returns false.

## Control Flow
Non-Linux `BasicFilesystem.Watch` setup failures are returned as-is without Linux-specific FAQ rewriting.

## State and Persistence Behavior
No state.

## Dependencies and Integration Points
Selected by `//go:build !linux` and used by `basicfs_watch.go`.

## Risks
Other platforms can have watch resource exhaustion errors, but this stub does not translate them into targeted guidance.

## Test Signals
No direct non-Linux test in this subset; behavior is intentionally trivial.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/fs/basicfs_watch_errors_others.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/fs/basicfs_watch_eventtypes_darwin.go -->
# sources/sync-backup/syncthing/lib/fs/basicfs_watch_eventtypes_darwin.go

## Purpose
Defines notify event masks for Darwin FSEvents builds using cgo and not kqueue/iOS.

## Important APIs, Types, and Functions
Constants: `subEventMask`, `permEventMask`, and `rmEventMask`. The subscription includes create, remove, write, rename, inode metadata, and xattr changes. Owner changes are treated as permission events.

## Control Flow
`basicfs_watch.go` combines `subEventMask` with `permEventMask` unless `ignorePerms` is true. Events matching `rmEventMask` become `Remove`; the rest become `NonRemove`.

## State and Persistence Behavior
No runtime state in this file.

## Dependencies and Integration Points
Darwin-specific build for the notify backend. The inode metadata mask is important for truncate-only and mtime changes.

## Risks
FSEvents can emit parent-directory events or coarse events, so scanner behavior must tolerate extra allowed events. Missing metadata masks would lose changes that do not look like writes.

## Test Signals
`TestWatchModTime` and `TestTruncateFileOnly` document Darwin-specific metadata behavior and allowed parent events.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/fs/basicfs_watch_eventtypes_darwin.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/fs/basicfs_watch_eventtypes_fen.go -->
# sources/sync-backup/syncthing/lib/fs/basicfs_watch_eventtypes_fen.go

## Purpose
Defines Solaris FEN notify masks for cgo builds.

## Important APIs, Types, and Functions
Constants select `notify.Create`, file modified/delete/rename events, no-follow behavior, `FileAttrib` permissions, and remove masks for delete or rename-from.

## Control Flow
The masks are consumed by the generic `BasicFilesystem.Watch` setup and `eventType` mapping.

## State and Persistence Behavior
No state.

## Dependencies and Integration Points
Builds only for `solaris && cgo`. Integrates with `github.com/syncthing/notify`.

## Risks
Solaris event naming distinguishes rename-from and rename-to; only rename-from is remove-like. Incorrect mask composition can produce duplicate or missing scan triggers.

## Test Signals
Watcher tests include Solaris in platform conditionals for rename expectations, but full coverage depends on running on Solaris with cgo.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/fs/basicfs_watch_eventtypes_fen.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/fs/basicfs_watch_eventtypes_inotify.go -->
# sources/sync-backup/syncthing/lib/fs/basicfs_watch_eventtypes_inotify.go

## Purpose
Defines Linux inotify masks used by `BasicFilesystem.Watch`.

## Important APIs, Types, and Functions
`subEventMask` includes create, moved-to, delete, delete-self, modify, moved-from, move-self, and attrib events. `permEventMask` is zero because `InAttrib` is always subscribed to catch both permissions and modtime. `rmEventMask` covers delete and moved-from/self removal events.

## Control Flow
All Linux watches include attrib notifications regardless of `ignorePerms`; `eventType` maps delete/move-away to `Remove`.

## State and Persistence Behavior
No state.

## Dependencies and Integration Points
Linux-only notify integration for scanner invalidation and permission/modtime detection.

## Risks
`ignorePerms` cannot suppress `InAttrib` because it is also needed for modtime, so permission-only changes may still wake scans on Linux.

## Test Signals
Watcher tests exercise rename, modtime, modify, overflow, and Linux inotify-limit error handling.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/fs/basicfs_watch_eventtypes_inotify.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/fs/basicfs_watch_eventtypes_kqueue.go -->
# sources/sync-backup/syncthing/lib/fs/basicfs_watch_eventtypes_kqueue.go

## Purpose
Defines notify masks for kqueue-style platforms and exposes whether kqueue watching is selected.

## Important APIs, Types, and Functions
`subEventMask` includes delete, write, rename, synthetic create, attrib, and extend. `permEventMask` is zero. `rmEventMask` covers delete and rename. `WatchKqueue = true`.

## Control Flow
The generic watcher subscribes to these masks where the supported watch implementation is compiled. The `WatchKqueue` constant lets other code distinguish kqueue behavior.

## State and Persistence Behavior
No state.

## Dependencies and Integration Points
Builds for BSDs, iOS, or explicit `kqueue`. Uses `github.com/syncthing/notify`.

## Risks
kqueue lacks native create events, relying on notify synthesis; this may differ from inotify/FSEvents behavior. Some darwin+kqueue combinations use the unsupported watcher file instead.

## Test Signals
Watch tests have platform skips and expectations, but full validation requires target OS coverage.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/fs/basicfs_watch_eventtypes_kqueue.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/fs/basicfs_watch_eventtypes_other.go -->
# sources/sync-backup/syncthing/lib/fs/basicfs_watch_eventtypes_other.go

## Purpose
Provides a fallback notify event mask for platforms not otherwise covered.

## Important APIs, Types, and Functions
`subEventMask = notify.All`, `permEventMask = 0`, and `rmEventMask = notify.Remove | notify.Rename`.

## Control Flow
Generic watcher subscribes to all notify events, then collapses remove/rename to `Remove` and everything else to `NonRemove`.

## State and Persistence Behavior
No state.

## Dependencies and Integration Points
Catch-all build selection for non-Linux, non-Windows, non-BSD, non-Solaris, non-Darwin, non-cgo, non-iOS platforms.

## Risks
Subscribing to all events can create extra scan wakeups. Platform notify support may still be incomplete even when this compiles.

## Test Signals
No direct tests for this catch-all path; behavioral validation depends on platform-specific test runs.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/fs/basicfs_watch_eventtypes_other.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/fs/basicfs_watch_eventtypes_readdcw.go -->
# sources/sync-backup/syncthing/lib/fs/basicfs_watch_eventtypes_readdcw.go

## Purpose
Defines Windows ReadDirectoryChangesW notify masks.

## Important APIs, Types, and Functions
`subEventMask` includes file and directory name changes, size, creation, and last-write changes. `permEventMask` is attributes. `rmEventMask` covers removed and renamed-old-name actions.

## Control Flow
Used by the generic watcher to configure notify subscriptions and classify backend remove events.

## State and Persistence Behavior
No state.

## Dependencies and Integration Points
Windows-only build. Interacts with Windows path normalization and 8.3 name handling in `basicfs_windows.go`.

## Risks
Windows watcher events can vary by case, short names, and root spelling. Attribute-only notifications are suppressed only when `ignorePerms` omits `permEventMask`.

## Test Signals
`basicfs_watch_test.go` includes Windows-specific root, case, and issue-regression scenarios.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/fs/basicfs_watch_eventtypes_readdcw.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/fs/basicfs_watch_notkqueue.go -->
# sources/sync-backup/syncthing/lib/fs/basicfs_watch_notkqueue.go

## Purpose
Provides `WatchKqueue = false` for non-kqueue platforms.

## Important APIs, Types, and Functions
Single constant `WatchKqueue`.

## Control Flow
No control flow; compile-time platform signal.

## State and Persistence Behavior
No state.

## Dependencies and Integration Points
Complements `basicfs_watch_eventtypes_kqueue.go` so callers can use `WatchKqueue` on all builds.

## Risks
The build tags must remain the exact inverse of kqueue-supported tags to avoid duplicate or missing constants.

## Test Signals
No direct tests; compilation across build matrix is the primary signal.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/fs/basicfs_watch_notkqueue.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/fs/basicfs_watch_test.go -->
# sources/sync-backup/syncthing/lib/fs/basicfs_watch_test.go

## Purpose
Exercises `BasicFilesystem.Watch` end-to-end and at the `watchLoop` level across ignore filtering, event classification, path normalization, overflow, and platform edge cases.

## Important APIs, Types, and Functions
`TestMain` creates a real watched root and shrinks `backendBuffer`. `testScenario`, `testWatchOutput`, `fakeMatcher`, and `fakeEventInfo` drive scenarios. Tests cover ignore/include, rename, Windows root handling, outside-root errors, subpath events, overflow, Linux error interpretation, symlinked roots, Windows case issue 4877, modtime changes, and truncate-only changes.

## Control Flow
Most tests create a watched directory, start `Watch`, mutate files, and wait until expected events cancel the context. Lower-level tests inject fake backend events into `watchLoop` to avoid relying on OS notification timing for path checks.

## State and Persistence Behavior
Uses a shared `testdata` directory under the package working directory, removed before and after the test run. Watch goroutines are canceled via contexts.

## Dependencies and Integration Points
Depends on `notify`, `build` platform flags, `ignoreresult`, and real OS notifications.

## Risks
Timing-based waits can be flaky on loaded systems. Platform-specific notify behavior requires allowed extra events and skips for OpenBSD. Overflow checks depend on intentionally small channel buffering.

## Test Signals
Provides high-value regression coverage for watcher safety: outside-root events become fatal errors, ignored paths are filtered, overflow schedules a broad scan, and symlinked roots do not panic.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/fs/basicfs_watch_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/fs/basicfs_watch_unsupported.go -->
# sources/sync-backup/syncthing/lib/fs/basicfs_watch_unsupported.go

## Purpose
Provides a `BasicFilesystem.Watch` implementation for build targets where recursive watching is intentionally unsupported.

## Important APIs, Types, and Functions
`Watch(name string, ignore Matcher, ctx context.Context, ignorePerms bool)` returns nil channels and `ErrWatchNotSupported`.

## Control Flow
No setup is attempted on unsupported builds.

## State and Persistence Behavior
No state.

## Dependencies and Integration Points
Selected for Solaris without cgo, Darwin without cgo, Android amd64, or Darwin kqueue builds. Satisfies the `Filesystem` interface.

## Risks
Callers must handle `ErrWatchNotSupported` and fall back to periodic scanning. Build tags must stay aligned with event mask files.

## Test Signals
Unsupported behavior is compile-time/platform-gated rather than directly tested in this subset.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/fs/basicfs_watch_unsupported.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/fs/basicfs_windows.go -->
# sources/sync-backup/syncthing/lib/fs/basicfs_windows.go

## Purpose
Implements Windows-specific `BasicFilesystem` behavior: hidden attributes, drive roots, read-only removal retry, ownership via SIDs, path canonicalization, 8.3 short-name resolution, and watch path preparation.

## Important APIs, Types, and Functions
Defines `alwaysOpenFlags = 0`, `errNotSupported`, `ReadSymlink`, `CreateSymlink`, `Hide`, `Unhide`, `Roots`, `Lchown`, `Remove`, `unrootedChecked`, `rel`, `resolveWin83`, `isMaybeWin83`, `getFinalPathName`, `evalSymlinks`, and `watchPaths`.

## Control Flow
Hide/unhide fetch and mutate Windows attributes. `Roots` calls `GetLogicalDriveStringsA`. `Remove` retries after clearing read-only permissions. `unrootedChecked` normalizes case and possible 8.3 names before root matching. `evalSymlinks` falls back to `GetFinalPathNameByHandleW`, trims Win32 namespace prefixes, and applies long filename support. `watchPaths` allows both canonicalized and user-provided roots for event matching.

## State and Persistence Behavior
Mutates filesystem attributes, ownership security descriptors, and deletes files. Watch helpers maintain no persistent state.

## Dependencies and Integration Points
Uses `golang.org/x/sys/windows`, raw Win32 syscalls, `UnicodeLowercaseNormalized`, `WindowsTempPrefix`, and notify watcher setup.

## Risks
The `Lchown` group branch parses `uid` instead of `gid`, which can break group-only ownership changes. Symlinks are unsupported here. Windows path namespace and short-name handling are complex and require broad platform tests.

## Test Signals
`basicfs_windows_test.go` covers root normalization, 8.3 detection/resolution, case-insensitive rel/unrooting, final path lookup, and read-only directory removal.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/fs/basicfs_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/fs/basicfs_windows_test.go -->
# sources/sync-backup/syncthing/lib/fs/basicfs_windows_test.go

## Purpose
Windows-only tests for root normalization, long-path support, 8.3 path handling, case-insensitive relative conversion, final path resolution, and read-only removal behavior.

## Important APIs, Types, and Functions
Tests target `newBasicFilesystem`, `resolveWin83`, `isMaybeWin83`, `rel`, `unrootedChecked`, `getFinalPathName`, and `Remove`.

## Control Flow
Table-driven tests assert expected `root` and `URI` for drive and UNC inputs. 8.3 tests create a long filename and verify short-name expansion or fallback truncation. Rel tests exercise mixed-case roots. Removal test sets a directory read-only attribute and confirms `BasicFilesystem.Remove` clears enough attributes to delete it.

## State and Persistence Behavior
Creates files/directories in temp roots and mutates Windows file attributes. Some tests query system paths such as `C:\Windows\System32`.

## Dependencies and Integration Points
Uses `syscall` Windows APIs, `TempName`, and shared `setup`.

## Risks
Tests depend on Windows filesystem behavior, short-name support, and permissions. Some final-path cases ignore missing paths to avoid environment-specific failures.

## Test Signals
Strong Windows regression coverage for path canonicalization, watcher root matching prerequisites, and deletion of read-only/custom-icon folders.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/fs/basicfs_windows_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/fs/basicfs_xattr_bsdish.go -->
# sources/sync-backup/syncthing/lib/fs/basicfs_xattr_bsdish.go

## Purpose
Lists extended attributes on FreeBSD and NetBSD while preserving namespace information missing from Go's generic API.

## Important APIs, Types, and Functions
Defines `namespaces`, `namespacePrefixes`, `listXattr`, `unixLlistxattr`, and `initxattrdest`.

## Control Flow
`listXattr` iterates user and system namespaces, reads length-prefixed extattr names, prefixes them with `user.` or `system.`, handles buffer growth, ignores EPERM for non-user namespaces, sorts names, and returns them.

## State and Persistence Behavior
Read-only metadata query. No xattrs are mutated here.

## Dependencies and Integration Points
Used by `basicfs_xattr_unix.go` on FreeBSD/NetBSD. Calls `unix.ExtattrListLink` directly to retain namespace IDs.

## Risks
Parsing length-prefixed buffers must guard corrupt lengths; it does. Namespace prefix array indexing is tied to unix constants. Permission-denied system namespace is silently ignored.

## Test Signals
Indirectly covered by `TestXattr` when run on supported BSD platforms.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/fs/basicfs_xattr_bsdish.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/fs/basicfs_xattr_linuxish.go -->
# sources/sync-backup/syncthing/lib/fs/basicfs_xattr_linuxish.go

## Purpose
Lists extended attribute names on Linux and Darwin using NUL-separated `Llistxattr` results.

## Important APIs, Types, and Functions
`listXattr(path string) ([]string, error)` uses `unix.Llistxattr`, grows the buffer on `ERANGE`, compacts empty NUL split parts, sorts names, and returns them.

## Control Flow
Initial 1024-byte read is retried with exact size when too small. Errors wrap the path for diagnostics. Empty entries from trailing NULs are removed by `compact`.

## State and Persistence Behavior
Read-only metadata query.

## Dependencies and Integration Points
Used by `basicfs_xattr_unix.go` for xattr filtering and synchronization on Linux/Darwin.

## Risks
Darwin and Linux xattr naming and namespaces differ, but this file returns raw names for higher-level filtering. Concurrent xattr changes between size query and read can still error.

## Test Signals
Indirectly covered by `TestXattr` where xattrs are supported.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/fs/basicfs_xattr_linuxish.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/fs/basicfs_xattr_unix.go -->
# sources/sync-backup/syncthing/lib/fs/basicfs_xattr_unix.go

## Purpose
Implements `BasicFilesystem` extended attribute read/write support on Unix-like platforms with xattr APIs.

## Important APIs, Types, and Functions
`GetXattr`, `SetXattr`, `xattrBufPool`, `getXattr`, and `compact`. `GetXattr` applies `XattrFilter` permission, max-entry, and max-total limits. `SetXattr` reconciles current and desired attributes by removing absent entries and setting changed values.

## Control Flow
`GetXattr` roots the path, lists names, filters names, reads values with `Lgetxattr`, handles BSD `ENOATTR`, applies size limits, and returns `protocol.Xattr` values. `getXattr` uses a pooled buffer, resizes on `ERANGE`, and returns either the buffer slice or a compact copy. `SetXattr` indexes desired/current xattrs, roots the path, removes no-longer-present xattrs, then sets new or changed values.

## State and Persistence Behavior
Reads and mutates filesystem xattrs on symlink paths using l* APIs. Size filters affect what gets synchronized or deleted.

## Dependencies and Integration Points
Depends on platform `listXattr`, `protocol.Xattr`, `x/sys/unix`, and `Filesystem.PlatformData`.

## Risks
Current xattrs are fetched through the same filter, so unpermitted attributes are intentionally untouched. Concurrent changes can cause missing-attribute races. Large xattr values can increase memory retention if returned from pooled buffers.

## Test Signals
`TestXattr` verifies set, read, removal, mutation, addition, sorting, and unsupported-platform skips.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/fs/basicfs_xattr_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/fs/basicfs_xattr_unsupported.go -->
# sources/sync-backup/syncthing/lib/fs/basicfs_xattr_unsupported.go

## Purpose
Provides xattr stubs for platforms without supported extended attribute implementation.

## Important APIs, Types, and Functions
`GetXattr` and `SetXattr` both return `ErrXattrsNotSupported`.

## Control Flow
No filesystem access is attempted.

## State and Persistence Behavior
No state or mutation.

## Dependencies and Integration Points
Builds for Windows, DragonFly, illumos, Solaris, and OpenBSD. Satisfies the `Filesystem` interface and lets callers detect unsupported xattrs via `errors.Is`.

## Risks
Callers must treat unsupported xattrs as a capability gap, not a hard sync failure unless configured to require them.

## Test Signals
`TestXattr` skips when `ErrXattrsNotSupported` is returned.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/fs/basicfs_xattr_unsupported.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/fs/casefs.go -->
# sources/sync-backup/syncthing/lib/fs/casefs.go

## Purpose
Wraps a filesystem to detect case conflicts, making case-insensitive filesystems behave like case-sensitive ones from Syncthing's perspective.

## Important APIs, Types, and Functions
`CaseConflictError`, `IsErrCaseConflict`, `OptionDetectCaseConflicts`, `caseFilesystemRegistry`, `caseFilesystem`, `checkCase`, `checkCaseExisting`, `defaultRealCaser`, `caseCache`, `caseNode`, `newCaseNode`, and `realCase`.

## Control Flow
`NewFilesystem` applies this option as the outermost layer. Mutating and opening operations check input case before delegating; creating/removing/renaming drops cached directory names. `realCase` walks path components through cached directory listings, mapping lowercase-normalized names back to real names. Existing paths whose NFC-normalized real spelling differs from requested spelling return `CaseConflictError`.

## State and Persistence Behavior
Maintains process-local LRU directory-name caches keyed by filesystem type, URI, and options. A background cleaner purges caches every minute. No persistent data is written by the wrapper itself.

## Dependencies and Integration Points
Uses `hashicorp/golang-lru/v2`, Unicode normalization from `x/text`, `UnicodeLowercaseNormalized`, and all wrapped `Filesystem` methods. It is deliberately outside `mtimeFS` and `walkFilesystem`.

## Risks
Cache freshness is central; stale cache triggers retry on not-exist, but other races can still report transient conflicts. `newCaseNode` compares `lower != lastLower` but assigns `lastLower = n`, which may reduce duplicate-fold handling accuracy if adjacent names fold together. Performance depends on directory size and cache invalidation frequency.

## Test Signals
`casefs_test.go` covers real-case lookup, sensitive/insensitive Stat behavior, stress concurrency, and benchmarks. `filesystem_test.go` guards mtime wrapper preservation with case cache reuse.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/fs/casefs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/fs/casefs_test.go -->
# sources/sync-backup/syncthing/lib/fs/casefs_test.go

## Purpose
Tests and benchmarks case-conflict detection over fake and real filesystems, including cache behavior under concurrent access.

## Important APIs, Types, and Functions
`TestRealCase`, `TestRealCaseSensitive`, `TestCaseFSStat`, `BenchmarkWalkCaseFakeFS100k`, `TestStressCaseFS`, `doubleWalkFS`, `doubleWalkFSWithOtherOps`, and `fakefsForTest`.

## Control Flow
Tests create mixed-case directory trees, query `realCase` with multiple spellings, and compare output to actual on-disk case. Stat tests distinguish underlying sensitive and insensitive filesystems. Benchmarks simulate scanner passes by walking and restatting paths. Stress tests run parallel walkers and touchers against a large fake FS with case conflict detection.

## State and Persistence Behavior
Uses fakeFS roots and real temp directories. Benchmarks and stress tests populate many in-memory fake entries and exercise shared case caches.

## Dependencies and Integration Points
Uses `OptionDetectCaseConflicts`, `NewFilesystem`, `UnicodeLowercaseNormalized`, `runtime`, and `testing.Short`.

## Risks
Real filesystem sensitivity detection can vary by platform and mount options. Stress test is skipped in short mode and timing-bound to ten seconds, so race coverage depends on CI settings.

## Test Signals
High confidence for case resolution correctness, case-sensitive behavior emulation, and cache concurrency under scanner-like workloads.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/fs/casefs_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/fs/copyrangemethod.go -->
# sources/sync-backup/syncthing/lib/fs/copyrangemethod.go

## Purpose
Defines the selectable copy-range strategies used by Syncthing to copy file ranges, including clone/offload-capable system calls and the standard fallback.

## Important APIs, Types, and Functions
`CopyRangeMethod` enum values: `Standard`, `Ioctl`, `CopyFileRange`, `SendFile`, `DuplicateExtents`, and `AllWithFallback`. `String` renders stable configuration/metric names.

## Control Flow
No copy logic here; methods are registered in platform-specific files and dispatched by `CopyRange`.

## State and Persistence Behavior
No state.

## Dependencies and Integration Points
Integrated with `filesystem_copy_range.go` registry and platform copy implementations.

## Risks
Unknown enum values stringify as `unknown`, so configuration validation must happen elsewhere if strictness is required.

## Test Signals
`filesystem_copy_range_test.go` iterates registered methods and uses `String` in subtest names.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/fs/copyrangemethod.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/fs/debug.go -->
# sources/sync-backup/syncthing/lib/fs/debug.go

## Purpose
Defines the package logger adapter for filesystem access logging.

## Important APIs, Types, and Functions
Package variable `l = slogutil.NewAdapter("Filesystem access")`.

## Control Flow
No direct control flow. Other files call `l.Debugf`, `l.Debugln`, and `l.ShouldDebug` for conditional wrappers and diagnostics.

## State and Persistence Behavior
Logger state is owned by the shared logging system, not this file.

## Dependencies and Integration Points
Used by `filesystem.go`, `logfs.go`, `metrics.go`, `casefs.go`, `walkfs.go`, `basicfs_watch.go`, xattr code, and copy-range registration.

## Risks
Debug logging can change wrapper layering in `NewFilesystem` when `walkfs` or `fs` debug facilities are enabled, so logging configuration has minor behavioral/performance impact.

## Test Signals
No direct tests; logger use is indirectly exercised by package tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/fs/debug.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/fs/errorfs.go -->
# sources/sync-backup/syncthing/lib/fs/errorfs.go

## Purpose
Implements a `Filesystem` that consistently returns a construction error, allowing `NewFilesystem` to return an object even for unrecognized or failed filesystem factories.

## Important APIs, Types, and Functions
`errorFilesystem` stores `err`, `fsType`, and `uri`. It implements all `Filesystem` methods, returning `fs.err` for operations while preserving `Type` and `URI`.

## Control Flow
`NewFilesystem` creates this wrapper when factory lookup or construction fails. Downstream callers can still hold a `Filesystem` but operations fail deterministically.

## State and Persistence Behavior
No filesystem state is mutated. The only state is the stored error and identity.

## Dependencies and Integration Points
Depends on `context`, `time`, and `protocol.PlatformData`. Implements `wrappingFilesystem` as non-unwrappable.

## Risks
Because `Options` returns nil and `SameFile` false, some higher-level code may proceed until first operation rather than failing at construction. This is intentional but can delay error surfacing.

## Test Signals
No direct tests in this subset; behavior is indirectly covered where unknown factories or missing wrappers are exercised.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/fs/errorfs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/fs/fakefs.go -->
# sources/sync-backup/syncthing/lib/fs/fakefs.go

## Purpose
Provides an in-memory, deterministic filesystem for tests and benchmarks. Metadata is stored in memory, contents can be generated pseudo-randomly from file names or stored explicitly, and optional case-insensitive behavior mimics Windows/macOS.

## Important APIs, Types, and Functions
Registers `FilesystemTypeFake`. Core types are `fakeFS`, `fakeEntry`, `fakeFile`, and `fakeFileInfo`. Implements most `Filesystem` operations, `PlatformData`, metrics counters, and fake content reads via `readShortAt`.

## Control Flow
`newFakeFilesystem` parses query parameters, reuses roots from a global cache, optionally populates random files, and creates `.stfolder` unless disabled. Operations lock `fs.mut`, find entries via path components, and mutate in-memory trees. Reads either return stored `content` or deterministic random blocks seeded by file name and block number. `NewFilesystem` wraps fakeFS with walk/case/mtime layers as requested.

## State and Persistence Behavior
Persistent only for process lifetime: `fakeFSCache` maps root URI to shared fake trees. File writes update size and optional content, but default fake content is generated rather than stored. Ownership, modtime, mode, symlink destination, and child maps are stored per entry.

## Dependencies and Integration Points
Used heavily by fs tests, benchmarks, case conflict detection, and mtime tests. Integrates with `unixPlatformData` for ownership/xattr-shaped metadata.

## Risks
`RemoveAll` increments its counter twice. `Walk` is not implemented directly and relies on `NewWalkFilesystem` wrapping. `SameFile` is approximate and can false-positive. `ReadAt` comments note it affects internal offset despite Go's usual contract.

## Test Signals
`fakefs_test.go` covers sensitive/insensitive operations, deterministic reads, content mode, symlinks, rename/remove semantics, `SameFile`, and name presentation.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/fs/fakefs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/fs/fakefs_test.go -->
# sources/sync-backup/syncthing/lib/fs/fakefs_test.go

## Purpose
Validates fakeFS behavior against expected filesystem semantics and, where possible, compares it with a real local filesystem of matching case sensitivity.

## Important APIs, Types, and Functions
`TestFakeFS`, `TestFakeFSCaseSensitive`, `TestFakeFSCaseInsensitive`, `testFakeFSRead`, `testFakeFSOpenFile`, `testFakeFSRemoveAll`, `testFakeFSRemove`, `testFakeFSRename`, `testFakeFSMkdir`, `testFakeFSSameFile`, `testReadWriteContent`, `createTestDir`, `runTests`, and `cleanup`.

## Control Flow
Tests create directories/files/symlinks, write/read/seek, mutate ownership, and assert metadata. Shared test suites run against fakeFS and sometimes real `BasicFilesystem`, depending on detected case sensitivity. Case-insensitive tests open, stat, create, rename, remove, and list using varied casing.

## State and Persistence Behavior
Most state is in fakeFS global roots; cleanup removes entries except `.stfolder`. Real temp directories are used to detect host case sensitivity and as comparison backends.

## Dependencies and Integration Points
Depends on `build`, `runtime`, `path/filepath`, and `NewFilesystem` behavior.

## Risks
Global fakeFS cache means root names must be unique to avoid cross-test leakage. Tests are broad but mostly single-threaded except casefs stress elsewhere.

## Test Signals
Strong coverage for fakeFS as a scanner/test backend: file data generation, explicit content storage, case-insensitive path resolution, name preservation, and mutation semantics.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/fs/fakefs_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/fs/filesystem.go -->
# sources/sync-backup/syncthing/lib/fs/filesystem.go

## Purpose
Defines Syncthing's filesystem abstraction and factory/wrapper construction pipeline, plus shared path, event, error, and utility helpers.

## Important APIs, Types, and Functions
Interfaces and types: `Filesystem`, `File`, `FileInfo`, `XattrFilter`, `Matcher`, `Event`, `EventType`, `Usage`, `FileMode`, and `wrappingFilesystem`. Functions include `NewFilesystem`, `IsInternal`, `Canonicalize`, `unwrapFilesystem`, and `WriteFile`. Constants mirror `os` modes/open flags and standard errors.

## Control Flow
`NewFilesystem` extracts case and mtime options, constructs the registered base filesystem or `errorFilesystem`, applies `mtimeFS`, wraps metrics, applies walk/log wrappers based on debug settings, then applies case detection outermost. `Canonicalize` cleans paths, rejects upward traversal, strips leading root separators, and maps root to `"."`.

## State and Persistence Behavior
Global factory registry stores filesystem type constructors. `WriteFile` writes data by truncating/creating a file and can leave partial data on mid-write failures. `NewFilesystem` wrapper choices affect runtime behavior but do not persist.

## Dependencies and Integration Points
Central integration point for `basic`, `fake`, `walkfs`, `metrics`, `logfs`, `mtimefs`, `casefs`, ignore matching, and protocol platform data.

## Risks
Wrapper ordering is subtle and safety-critical. `WriteFile` is non-atomic. `Canonicalize` treats absolute-looking paths as root-relative except double separators, so callers must understand this contract.

## Test Signals
`filesystem_test.go` covers internal names, canonicalization, `FileMode.String`, parent logic, and a regression for caseFS/mtimeFS wrapper caching.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/fs/filesystem.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/fs/filesystem_copy_range.go -->
# sources/sync-backup/syncthing/lib/fs/filesystem_copy_range.go

## Purpose
Maintains the registry and dispatch function for file range copy implementations.

## Important APIs, Types, and Functions
`copyRangeMethods` map, mutex `mut`, `copyRangeImplementation`, `registerCopyRangeImplementation`, and public `CopyRange`.

## Control Flow
Platform files register implementations in `init`. `CopyRange` looks up the requested `CopyRangeMethod` and calls it with source/destination files, offsets, and size; missing methods return `syscall.ENOTSUP`.

## State and Persistence Behavior
Process-local registry only. Copy implementations mutate destination file contents and size; this dispatcher does not.

## Dependencies and Integration Points
Called by higher-level file synchronization code needing efficient range copies. Integrates with basic-file unwrapping and platform copy syscalls in sibling files.

## Risks
Registration is global and method collisions overwrite previous implementations. Missing method support is runtime, not compile-time. Callers must choose fallback behavior.

## Test Signals
`filesystem_copy_range_test.go` iterates the registry and validates data, size, offsets, and expected errors for each registered implementation.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/fs/filesystem_copy_range.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/fs/filesystem_copy_range_allwithfallback.go -->
# sources/sync-backup/syncthing/lib/fs/filesystem_copy_range_allwithfallback.go

## Purpose
Registers and implements a fallback chain that tries all copy-range strategies before giving up.

## Important APIs, Types, and Functions
`init` registers `CopyRangeMethodAllWithFallback`. `copyRangeAllWithFallback` tries ioctl, copy_file_range, sendfile, duplicate extents, then standard copy.

## Control Flow
The method calls `CopyRange` recursively for each concrete method and returns nil on first success. If all fail, it returns the last error.

## State and Persistence Behavior
Destination file may be partially modified by a failed earlier method if that implementation has side effects before erroring. The wrapper itself stores no state.

## Dependencies and Integration Points
Depends on registered concrete methods. Useful when callers prefer best-effort acceleration with standard fallback.

## Risks
Returning only the last error can hide the true best diagnostic from earlier methods. Partial writes before fallback are a concern if implementations are not all-or-nothing.

## Test Signals
Copy-range tests include `AllWithFallback` in expected error and success matrices.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/fs/filesystem_copy_range_allwithfallback.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/fs/filesystem_copy_range_standard.go -->
# sources/sync-backup/syncthing/lib/fs/filesystem_copy_range_standard.go

## Purpose
Provides the portable copy-range implementation using `ReadAt` and `WriteAt`.

## Important APIs, Types, and Functions
`init` registers `CopyRangeMethodStandard`. `copyRangeStandard` loops with a 4 MiB buffer, reading from source offset and writing to destination offset.

## Control Flow
For each chunk, it shrinks the buffer to remaining size, reads with `ReadAt`, converts EOF to `io.ErrUnexpectedEOF`, writes the read bytes, and advances offsets until requested size reaches zero.

## State and Persistence Behavior
Writes destination contents and may extend sparse regions through `WriteAt`. It intentionally does not alter file seek positions.

## Dependencies and Integration Points
Portable fallback used directly or through `AllWithFallback`.

## Risks
Short reads without errors would still progress by `n`; EOF always aborts as unexpected. The buffer allocation is per call and can be large for frequent small copies.

## Test Signals
Copy-range tests validate offsets, appended/overwritten data, sparse gaps, full-file copies, and unexpected EOF.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/fs/filesystem_copy_range_standard.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/fs/filesystem_copy_range_test.go -->
# sources/sync-backup/syncthing/lib/fs/filesystem_copy_range_test.go

## Purpose
Validates all registered copy-range implementations across offset, size, alignment, sparse, and error cases.

## Important APIs, Types, and Functions
Global `testCases` describe source/destination sizes, offsets, starting seek positions, copy size, expected destination size, and per-method expected errors. `TestCopyRange` runs each registered method.

## Control Flow
Tests create random source/destination files, set initial seek positions, unwrap to `basicFile`, call each implementation, then verify original seek positions, destination size, copied bytes, and untouched or zero-filled regions.

## State and Persistence Behavior
Creates temp directories and files, optionally under paths from `STFSTESTPATH` to test specific filesystems. Destination files are mutated by each copy operation.

## Dependencies and Integration Points
Uses `copyRangeMethods`, `unwrap`, `NewFilesystem(FilesystemTypeBasic)`, `io`, `syscall`, and random data.

## Risks
Some hardware/filesystem methods may be unsupported and are skipped when returning unsupported. Expected errors differ by method and platform, so the table must track syscall behavior carefully.

## Test Signals
Strong signal for copy correctness, non-corruption, seek-position preservation, sparse expansion, and graceful unsupported handling.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/fs/filesystem_copy_range_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/fs/filesystem_test.go -->
# sources/sync-backup/syncthing/lib/fs/filesystem_test.go

## Purpose
Tests shared filesystem helpers and a wrapper-ordering regression involving case conflict detection and mtime virtualization.

## Important APIs, Types, and Functions
`TestIsInternal`, `TestCanonicalize`, `TestFileModeString`, `TestIsParent`, and `TestRepro9677MissingMtimeFS`.

## Control Flow
Table tests validate internal `.stfolder`, `.stignore`, `.stversions` handling; canonical path acceptance/rejection; parent path logic across relative/absolute paths; and mode string formatting. The regression test creates an mtime-enabled case-detecting fake FS, resets the global case registry, creates a case FS without mtime, then verifies a later mtime-enabled FS still preserves virtual mtimes.

## State and Persistence Behavior
Uses fakeFS and a map-backed mtime database. Mutates `globalCaseFilesystemRegistry` in the regression test.

## Dependencies and Integration Points
Covers `NewFilesystem` wrapper order, `OptionDetectCaseConflicts`, `NewMtimeOption`, `UnicodeLowercaseNormalized`, and platform path differences.

## Risks
Path semantics vary by Windows vs Unix and are branch-tested. The regression test intentionally touches global state, so isolation matters.

## Test Signals
High-value safety coverage for root traversal prevention, internal-file ignoring, and wrapper cache correctness.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/fs/filesystem_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/fs/folding.go -->
# sources/sync-backup/syncthing/lib/fs/folding.go

## Purpose
Provides Unicode lowercasing and NFC normalization for case-insensitive path comparison.

## Important APIs, Types, and Functions
`UnicodeLowercaseNormalized`, `isASCII`, `toLowerASCII`, `toLowerUnicode`, and `firstCaseChange`.

## Control Flow
Fast path returns ASCII lowercase strings unchanged or lowercases only changed ASCII spans. Non-ASCII path finds first rune whose lower(upper(r)) differs, writes prefix unchanged, folds remaining runes, and normalizes to NFC. Special handling avoids simple Latin-1 `µ` pitfalls and uses upper-then-lower folding for OS-like behavior.

## State and Persistence Behavior
Pure string transformation; no state.

## Dependencies and Integration Points
Used by case conflict detection, fakeFS case-insensitive mode, Windows path matching, and mtime case-insensitive keys.

## Risks
Unicode case folding is locale-insensitive and intentionally approximate to filesystem behavior. It does not equate German `ß` with `ss` and chooses one Greek sigma form.

## Test Signals
`folding_test.go` covers ASCII, Latin, Cyrillic, Greek, Turkish, non-cased scripts, Kelvin sign, and NFC renormalization.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/fs/folding.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/fs/folding_test.go -->
# sources/sync-backup/syncthing/lib/fs/folding_test.go

## Purpose
Verifies Unicode case folding and normalization behavior used for filesystem case-insensitive comparisons.

## Important APIs, Types, and Functions
`caseCases`, `benchmarkCases`, `TestUnicodeLowercaseNormalized`, and `BenchmarkUnicodeLowercase`.

## Control Flow
The test iterates representative strings and compares `UnicodeLowercaseNormalized` output to expected canonical forms. Benchmarks measure allocations and speed for ASCII, Latin-1, and mixed Unicode names.

## State and Persistence Behavior
No persistent state.

## Dependencies and Integration Points
Targets `folding.go`; indirectly protects caseFS, fakeFS insensitive mode, Windows path handling, and mtime insensitive storage.

## Risks
The expected outputs encode deliberate choices for tricky language cases. Any change to folding semantics can affect conflict detection and path matching.

## Test Signals
Good coverage of the Unicode edge cases Syncthing relies on for portable case folding.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/fs/folding_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/fs/logfs.go -->
# sources/sync-backup/syncthing/lib/fs/logfs.go

## Purpose
Wraps a filesystem to log method calls, callers, arguments, results, and errors for debugging.

## Important APIs, Types, and Functions
`logFilesystem`, `newLogFilesystem`, `getCaller`, and overrides for most `Filesystem` methods including `Watch`, `Glob`, `Roots`, and `Usage`.

## Control Flow
Each method delegates to the embedded filesystem, then logs via `l.Debugln` with caller location, filesystem type/URI, operation name, arguments, and result/error. `underlying` supports wrapper unwrapping.

## State and Persistence Behavior
Stores the wrapped filesystem and caller-skip layer count. No persistent state.

## Dependencies and Integration Points
Constructed in `NewFilesystem` when `fs` or `walkfs` debug facilities are enabled. Works with `walkFilesystem` and caseFS layer counting.

## Risks
Logging can expose paths and operation arguments in debug logs and can add overhead. Caller depth must stay aligned with wrapper layering to identify useful call sites.

## Test Signals
No direct tests; behavior is validated by compilation and debug usage.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/fs/logfs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/fs/metrics.go -->
# sources/sync-backup/syncthing/lib/fs/metrics.go

## Purpose
Wraps filesystem and file operations with Prometheus counters for operation count, duration, and bytes transferred.

## Important APIs, Types, and Functions
Metric vectors `metricTotalOperationSeconds`, `metricTotalOperationsCount`, `metricTotalBytesCount`; constants for operation labels; `metricsFS`; `metricsFile`; `account`; method wrappers for all `Filesystem` and `File` operations.

## Control Flow
Each wrapper defers an accounting closure that records duration, increments count, and records bytes when available. File-returning methods wrap successful files in `metricsFile`, whose `Read`, `ReadAt`, `Write`, and `WriteAt` record byte counts.

## State and Persistence Behavior
Metrics are process-global Prometheus counters labeled by filesystem root URI and operation. No filesystem state is altered beyond delegated operations.

## Dependencies and Integration Points
Always applied by `NewFilesystem`. Integrates with `promauto` and wrapper unwrapping through `underlying` and `metricsFile.unwrap`.

## Risks
`account` calls `m.next.URI()` for every operation, which can itself be nontrivial or instrumented below if wrapper ordering changes. The label typo `mdkir` for mkdir is stable but misspelled. Metrics cardinality follows filesystem URI values.

## Test Signals
No direct metric assertions in this subset; package tests exercise wrappers indirectly through `NewFilesystem`.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/fs/metrics.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/fs/mtimefs.go -->
# sources/sync-backup/syncthing/lib/fs/mtimefs.go

## Purpose
Adds virtual nanosecond modification-time support over filesystems that may round or fail `Chtimes`.

## Important APIs, Types, and Functions
`database` interface, `mtimeFS`, `MtimeFSOption`, `WithCaseInsensitivity`, `optionMtime`, `NewMtimeOption`, `mtimeFileInfo`, `mtimeFile`, and `GetMtimeMapping`.

## Control Flow
`Chtimes` attempts the underlying change, then stats the file and stores the real on-disk mtime plus requested virtual mtime. `Stat`, `Lstat`, and file `Stat` replace `ModTime` with the virtual value only when current disk mtime equals the saved on-disk value. Equal real/virtual mtimes delete the DB mapping.

## State and Persistence Behavior
Persists mtime mappings in the supplied database keyed by folder ID and normalized name when configured case-insensitive. The filesystem itself may or may not store the requested exact timestamp.

## Dependencies and Integration Points
Applied by `NewFilesystem` before walking. Integrates with `walkFilesystem`, `casefs`, and copy-range unwrapping.

## Risks
Database errors in save/delete are ignored. If on-disk mtime changes externally, virtual mtime is no longer applied. Case-insensitive mapping must match underlying filesystem behavior to avoid misses.

## Test Signals
`mtimefs_test.go` covers failed/evil `Chtimes`, walk and open stat behavior, underlying mtime divergence, and case-insensitive mapping.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/fs/mtimefs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/fs/mtimefs_test.go -->
# sources/sync-backup/syncthing/lib/fs/mtimefs_test.go

## Purpose
Tests virtual mtime preservation across stat, walk, open file stat, failed underlying timestamp calls, and case-insensitive paths.

## Important APIs, Types, and Functions
`TestMtimeFS`, `TestMtimeFSWalk`, `TestMtimeFSOpen`, `TestMtimeFSInsensitive`, `mapStore`, `failChtimes`, `evilChtimes`, `newMtimeFS`, and `newMtimeFSWithWalk`.

## Control Flow
Tests inject `chtimes` functions that succeed, fail, or set wrong truncated times, then verify `mtimeFS` still reports requested virtual times while underlying stats differ. Walk and open tests confirm wrapper ordering applies virtual times to traversal and file handles. Case-insensitive tests compare behavior with and without `WithCaseInsensitivity`.

## State and Persistence Behavior
Uses temp dirs and in-memory `mapStore` database. `evilChtimes` deliberately mutates disk mtimes differently from requested values.

## Dependencies and Integration Points
Exercises `NewFilesystem` with `NewMtimeOption`, unwrapping to `walkFilesystem` and `mtimeFS`, and platform case sensitivity assumptions.

## Risks
Case-insensitive test assumes Darwin/Windows filesystems are insensitive, which can be false on unusual mounts. DB errors are not represented by `mapStore`.

## Test Signals
Strong coverage for virtual mtime overlay semantics and wrapper integration.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/fs/mtimefs_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/fs/platform_common.go -->
# sources/sync-backup/syncthing/lib/fs/platform_common.go

## Purpose
Builds protocol platform metadata from filesystem stat ownership and extended attributes, and provides a generic expiring value cache.

## Important APIs, Types, and Functions
`unixPlatformData`, generic `valueCache[K,V]`, `cacheEntry[V]`, `newValueCache`, and `lookup`.

## Control Flow
When ownership scanning is enabled, `unixPlatformData` lstats a file, fills UID/GID, looks up owner/group names through caches, and special-cases numeric zero as `"root"` when lookup fails. When xattr scanning is enabled, it calls `fs.GetXattr` and attaches results to `protocol.PlatformData`.

## State and Persistence Behavior
Caches user/group lookups in memory for a validity duration. Does not persist metadata; returns data for protocol serialization.

## Dependencies and Integration Points
Used by Unix `BasicFilesystem.PlatformData` and `fakeFS.PlatformData`. Integrates with `protocol.PlatformData`, xattr filters, user/group caches, and filesystem stat methods.

## Risks
Lookup failures are cached as zero values, avoiding repeated lookups but potentially delaying recovery. Ownership name resolution can be stale for up to the cache validity. Xattr errors abort platform data collection.

## Test Signals
Covered indirectly by fakeFS/basicFS platform data use and xattr tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/fs/platform_common.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/fs/tempname.go -->
# sources/sync-backup/syncthing/lib/fs/tempname.go

## Purpose
Creates and detects Syncthing temporary filenames in a platform-aware, filename-length-safe way.

## Important APIs, Types, and Functions
Constants `WindowsTempPrefix`, `UnixTempPrefix`, `maxFilenameLength`; functions `tempPrefix`, `IsTemporary`, `TempNameWithPrefix`, and `TempName`.

## Control Flow
`TempName` chooses a Windows or Unix prefix, then `TempNameWithPrefix` prefixes the basename and appends `.tmp`. Long basenames are replaced with a SHA-256 hex digest to stay under conservative filename length limits. `IsTemporary` recognizes both Windows and Unix prefixes regardless of current platform.

## State and Persistence Behavior
Pure string/path generation; no files are created.

## Dependencies and Integration Points
Used by ignore matching to always ignore temp files, Windows 8.3 detection, and file synchronization temp naming.

## Risks
Hashing long basenames loses human readability and theoretically can collide, though SHA-256 makes that negligible. Length limit is conservative to support unusual filesystems.

## Test Signals
`tempname_test.go` validates long-name shortening and short-name suffix behavior; benchmarks measure allocations.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/fs/tempname.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/fs/tempname_test.go -->
# sources/sync-backup/syncthing/lib/fs/tempname_test.go

## Purpose
Tests and benchmarks temporary filename generation.

## Important APIs, Types, and Functions
`TestLongTempFilename`, `benchmarkTempName`, `BenchmarkTempNameShort`, and `BenchmarkTempNameLong`.

## Control Flow
The test creates a 300-character name, checks generated temp name length is bounded, and verifies short names retain the original basename plus `.tmp`. Benchmarks run `TempName` for short and long basenames under a sample directory.

## State and Persistence Behavior
No filesystem writes; only path string generation.

## Dependencies and Integration Points
Targets `TempName`.

## Risks
The length assertion is broad, not exact, which is fine for guarding the contract but does not pin platform-specific prefixes.

## Test Signals
Basic signal that temp names remain safe for long filenames and recognizable for short ones.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/fs/tempname_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/fs/types.go -->
# sources/sync-backup/syncthing/lib/fs/types.go

## Purpose
Defines filesystem type registration and option extension points.

## Important APIs, Types, and Functions
`FilesystemType`, `Option`, `FilesystemFactory`, global `filesystemFactories`, `filesystemFactoriesMutex`, and `RegisterFilesystemType`.

## Control Flow
Filesystem implementations call `RegisterFilesystemType` in `init`; `NewFilesystem` later looks up the factory under the mutex and invokes it with URI/options.

## State and Persistence Behavior
Maintains a process-global factory map. No disk state.

## Dependencies and Integration Points
`basicfs.go` and `fakefs.go` register built-in types. Plugins/tests can register additional types.

## Risks
Registering the same type overwrites silently. Option equality depends on `String`, so options with parameters must include those parameters in their string representation.

## Test Signals
Exercised indirectly by all `NewFilesystem` tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/fs/types.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/fs/util.go -->
# sources/sync-backup/syncthing/lib/fs/util.go

## Purpose
Provides path, home-directory, Windows filename, sanitization, parent, and common-prefix helpers shared by filesystem code.

## Important APIs, Types, and Functions
`ExpandTilde`, `getHomeDir`, `WindowsInvalidFilename`, `SanitizePath`, `windowsReservedNamePart`, `IsParent`, `CommonPrefix`, `PathComponents`, and `isVolumeNameOnly`.

## Control Flow
`ExpandTilde` expands `~` and `~/` with Windows historical home handling. Windows validation rejects reserved characters, trailing spaces/periods, and reserved device names per path component. `SanitizePath` collapses invalid characters and whitespace to single spaces and prepends `-` for reserved Windows names. `CommonPrefix` compares cleaned path components while respecting absolute/relative mismatch and Windows volume roots.

## State and Persistence Behavior
Pure helper functions, except environment reads for home directory.

## Dependencies and Integration Points
Used by root normalization, ignore matching, path display/safety, Windows path checks, and case/walk code.

## Risks
`IsParent` is lexical and requires both paths to have matching absolute/relative form. `SanitizePath` is intentionally conservative and may alter valid Unix names to avoid surprising shell or Windows behavior.

## Test Signals
`util_test.go` covers common prefixes, invalid Windows names, sanitization, fuzz-like printable UTF-8 guarantee, and benchmarks.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/fs/util.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/fs/util_test.go -->
# sources/sync-backup/syncthing/lib/fs/util_test.go

## Purpose
Tests utility helpers for common path prefixes, Windows filename validation, and path sanitization.

## Important APIs, Types, and Functions
`TestCommonPrefix`, `TestWindowsInvalidFilename`, `TestSanitizePath`, `TestSanitizePathFuzz`, `BenchmarkWindowsInvalidFilenameValid`, and `BenchmarkWindowsInvalidFilenameNUL`.

## Control Flow
Table tests branch on Windows vs Unix expected separators and volume semantics. Filename tests check reserved names, reserved characters, and trailing-space/period rules. Sanitization tests compare exact outputs and fuzz random bytes to ensure valid printable UTF-8.

## State and Persistence Behavior
No persistent state.

## Dependencies and Integration Points
Covers `CommonPrefix`, `WindowsInvalidFilename`, `SanitizePath`, and error wrapping with sentinel invalid filename errors.

## Risks
Platform conditionals mean some cases only run on Windows. Fuzz loop uses random bytes but fixed count, giving smoke coverage rather than exhaustive fuzzing.

## Test Signals
Good regression coverage for path safety helpers used throughout filesystem setup and UI-facing path generation.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/fs/util_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/fs/walkfs.go -->
# sources/sync-backup/syncthing/lib/fs/walkfs.go

## Purpose
Implements deterministic recursive filesystem walking with root-relative paths and optional infinite-recursion detection for Windows junction traversal.

## Important APIs, Types, and Functions
`ErrInfiniteRecursion`, `ancestorDirList`, `WalkFunc`, `walkFilesystem`, `NewWalkFilesystem`, `walk`, `Walk`, and `underlying`.

## Control Flow
`Walk` lstats the root, then recursively calls `walk`. Each path is canonicalized, passed to the callback, and skipped/stopped based on callback errors. Directories list names with `DirNames`, lstat children, and recurse in directory listing order. When `OptionJunctionsAsDirs` is present, ancestor `SameFile` checks detect recursion and call the callback with `ErrInfiniteRecursion`.

## State and Persistence Behavior
No persistent state. Runtime stack tracks ancestor directory `FileInfo` values for recursion detection.

## Dependencies and Integration Points
Always applied by `NewFilesystem`. Relies on underlying `Lstat`, `DirNames`, `SameFile`, and options.

## Risks
Directory names are documented as lexical but this code does not sort `DirNames`; deterministic order depends on underlying implementations returning sorted names. `SkipDir` behavior follows Go filepath semantics. Recursion detection quality depends on `SameFile`.

## Test Signals
`walkfs_test.go` covers symlink skipping, Windows junction traversal, and infinite recursion detection.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/fs/walkfs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/fs/walkfs_test.go -->
# sources/sync-backup/syncthing/lib/fs/walkfs_test.go

## Purpose
Shared walk tests for symlink handling and Windows directory junction traversal/recursion detection.

## Important APIs, Types, and Functions
`testWalkSkipSymlink`, `createDirJunct`, `testWalkTraverseDirJunct`, and `testWalkInfiniteRecursion`.

## Control Flow
Symlink test creates a target tree and a symlink under a walked directory, then asserts the walker sees the symlink but does not descend. Junction tests create Windows junctions with `cmd /c mklink /J`; one verifies traversal when `OptionJunctionsAsDirs` is set, and another creates a cycle and expects one `ErrInfiniteRecursion` callback.

## State and Persistence Behavior
Mutates temp filesystem trees and Windows junctions. No persistent state beyond test roots.

## Dependencies and Integration Points
Called from `basicfs_test.go` for the basic filesystem. Uses `build` platform flags and `NewFilesystem`.

## Risks
Windows junction tests depend on privileges and command availability. Symlink test skips Windows.

## Test Signals
Important coverage for scanner traversal boundaries: symlinks are not followed, junctions can be traversed, and cycles are detected.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/fs/walkfs_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/geoip/geoip.go -->
# sources/sync-backup/syncthing/lib/geoip/geoip.go

## Purpose
Provides an automatically updating MaxMind GeoLite2 City database provider with thread-safe IP lookup.

## Important APIs, Types, and Functions
`Provider` stores edition/account/license/refresh settings, database directory, mutex, current DB directory, and `*geoip2.Reader`. Public APIs are `NewGeoLite2CityProvider`, `City`, and `Serve`; internal `download` performs update/open/swap.

## Control Flow
Constructor initializes a provider and performs an initial download. `Serve` waits for context cancellation or refresh interval ticks, downloading on each tick. `download` creates a temp subdirectory, configures `geoipupdate`, downloads the edition, opens the `.mmdb`, swaps it under lock, closes the prior reader, and removes an old directory.

## State and Persistence Behavior
Persists downloaded MaxMind database files under the configured directory. Runtime state tracks the active reader and current DB subdirectory. `City` is mutex-protected.

## Dependencies and Integration Points
Uses `maxmind/geoipupdate`, `oschwald/geoip2-golang`, network access to MaxMind, and context cancellation.

## Risks
`download` appears to remove `p.currentDBDir` after assigning it to the new subdirectory when `prevDBDir != ""`; that likely deletes the newly active DB directory instead of the previous one. Failed downloads leave temp directories behind. `Serve` uses `time.After` in a loop and returns the first refresh error.

## Test Signals
`geoip_test.go` performs an integration download only when credentials are provided.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/geoip/geoip.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/geoip/geoip_test.go -->
# sources/sync-backup/syncthing/lib/geoip/geoip_test.go

## Purpose
Integration test for downloading and opening a MaxMind GeoLite2 City database.

## Important APIs, Types, and Functions
`TestDownloadAndOpen` reads `GEOIP_ACCOUNT_ID` and `GEOIP_LICENSE_KEY`, constructs a provider, and calls `City` for `8.8.8.8`.

## Control Flow
The test skips when credentials are missing, otherwise downloads into `t.TempDir`, opens the DB through `NewGeoLite2CityProvider`, and verifies a lookup does not error.

## State and Persistence Behavior
Downloads database files into a temporary directory and opens a reader.

## Dependencies and Integration Points
Requires external MaxMind service access and valid credentials. Covers `geoip.go` constructor, download path, and lookup path.

## Risks
Network and credential dependency make this unsuitable for default deterministic CI unless secrets are configured. It does not exercise refresh cleanup behavior.

## Test Signals
Good live integration signal for initial download and DB readability, but not for scheduled refresh or failure modes.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/geoip/geoip_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/httpcache/httpcache.go -->
# sources/sync-backup/syncthing/lib/httpcache/httpcache.go

## Purpose
Implements an in-memory HTTP middleware cache for a single path/response, including precomputed gzip output.

## Important APIs, Types, and Functions
`SinglePathCache`, constructor `SinglePath`, `recordedResponse`, `responseRecorder`, `ServeHTTP`, and `serveCached`.

## Control Flow
Only GET and HEAD use caching; other methods pass through. Requests first attempt cached response under an RLock, then retry under a write lock to avoid duplicate fills. On miss, the child request is cloned with `Accept-Encoding` removed, the next handler is recorded, successful 200 responses are gzipped and stored, then the recorded response is served to the client.

## State and Persistence Behavior
Stores one response in memory with status, headers, plain bytes, gzip bytes, creation time, and keep duration. No disk persistence.

## Dependencies and Integration Points
Uses `net/http`, `compress/gzip`, and standard locking. Intended for endpoints where one cached representation is valid for all GET/HEAD callers.

## Risks
The cache key ignores path, query string, request headers, and user/session identity; it is safe only behind a single-path/public-response contract. HEAD responses are served with a body because `recordedResponse.ServeHTTP` does not suppress writes. Header maps are assigned directly to the response writer.

## Test Signals
No tests in this subset; useful tests would cover GET/HEAD, gzip/plain responses, expiration, non-200 pass-through, and concurrency.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/httpcache/httpcache.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/ignore/cache.go -->
# sources/sync-backup/syncthing/lib/ignore/cache.go

## Purpose
Provides a small match-result cache for ignore matching with access-time based cleanup.

## Important APIs, Types, and Functions
`nower`, package variable `clock`, `cache`, `cacheEntry`, `newCache`, `clean`, `get`, `set`, `len`, and `defaultClock`.

## Control Flow
`get` returns a cached `ignoreresult.R` and refreshes its access time. `set` stores the result with current time. `clean` deletes entries whose last access exceeds the supplied duration.

## State and Persistence Behavior
In-memory map only. Access timestamps are Unix nanoseconds.

## Dependencies and Integration Points
Used by `ignore.Matcher` when `WithCache(true)` is enabled. `clock` is replaceable in tests.

## Risks
The cache is not internally synchronized; callers must hold `Matcher`'s mutex. `set` uses `time.Now()` directly instead of the injectable `clock`, while tests mainly rely on later `get` refreshing via fake time.

## Test Signals
`cache_test.go` verifies hits, false-result caching, access refresh, and cleanup.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/ignore/cache.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/ignore/cache_test.go -->
# sources/sync-backup/syncthing/lib/ignore/cache_test.go

## Purpose
Tests ignore cache storage, retrieval, access-time refresh, and expiration.

## Important APIs, Types, and Functions
`TestCache` and `fakeClock`.

## Control Flow
The test replaces package `clock`, creates a cache, checks a miss, stores ignored/deletable and not-ignored results, verifies both hit, advances fake time, accesses one key to refresh it, cleans with a duration threshold, then asserts only the stale key was removed.

## State and Persistence Behavior
Mutates package-level `clock` temporarily and restores it with defer. Cache state is in-memory.

## Dependencies and Integration Points
Uses `ignoreresult` flags and `cache` internals from the same package.

## Risks
Because `cache.set` uses real `time.Now`, correctness relies on subsequent fake-clock `get` calls to refresh entries before expiration checks.

## Test Signals
Good basic signal that cached ignore decisions can expire without evicting recently accessed entries.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/ignore/cache_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/lib/ignore/ignore.go -->
# sources/sync-backup/syncthing/lib/ignore/ignore.go

## Purpose
Parses `.stignore` files and evaluates Syncthing ignore patterns, including includes, negation, case-folding, deletable flags, skip-dir hints, caching, hashing, and change detection.

## Important APIs, Types, and Functions
`ParseError`, `Pattern`, `ChangeDetector`, `Matcher`, `Option`, `WithCache`, `WithChangeDetector`, `New`, `Load`, `Parse`, `Match`, `Lines`, `Patterns`, `Hash`, `Stop`, `hashPatterns`, `loadParseIncludeFile`, `parseLine`, `parseIgnoreFile`, `WriteIgnores`, and `modtimeChecker`.

## Control Flow
`Load` skips reparsing when remembered files are unchanged, otherwise loads the root ignore file and parses it under lock. Parsing records raw lines, handles `#escape=`, removes duplicate lines, loads `#include` files recursively with loop detection, expands directory-suffix patterns, and compiles gobwas globs. `Match` first ignores Syncthing temp/internal files, checks optional cache, then evaluates patterns in order while tracking whether ignored directories can be skipped.

## State and Persistence Behavior
`Matcher` stores raw lines, compiled patterns, current hash, optional match cache, stop channel, and change detector state. `WriteIgnores` atomically writes ignore contents through `osutil.CreateAtomicFilesystem`, normalizes line endings, closes, and hides the file; empty content removes the ignore file.

## Dependencies and Integration Points
Depends on `fs.Filesystem`, `ignoreresult`, `gobwas/glob`, Unicode normalization, platform build flags, and `osutil`. Used by filesystem watcher filters and scanner ignore logic.

## Risks
Includes can escape the folder root for basic filesystems by design. Cache correctness depends on matcher locking and invalidation when pattern hash changes. Skip-dir inference is subtle around negated/rooted/double-star patterns. Parse errors still leave root `Lines` available.

## Test Signals
This subset includes cache tests; broader ignore parser/matcher tests likely live elsewhere. Key untested edges here include include cycles, custom escape parsing, skip-dir inference, and `WriteIgnores` hiding behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/lib/ignore/ignore.go -->
