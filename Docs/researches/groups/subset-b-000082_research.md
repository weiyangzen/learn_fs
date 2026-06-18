# subset-b-000082 research

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/archive/changes_linux.go -->
# sources/cloud-native/containers-storage/pkg/archive/changes_linux.go

Purpose: Linux-specific change collection for `archive`, optimized for comparing two directory trees while avoiding unnecessary `lstat(2)` calls. It builds pruned `FileInfo` trees for `ChangesDirs`/layer diffing and implements overlay whiteout deletion detection.

Important APIs/types/functions: `walker`, `collectFileInfoForChanges`, `walkchunk`, `(*walker).walk`, `nameIno`, `readdirnames`, `parseDirent`, `OverlayChanges`, `overlayLowerContainsWhiteout`, and `overlayDeletedFile`. The `walker` tracks old/new dirs, root `FileInfo` nodes, and ID mappings. `readdirnames` uses `unix.ReadDirent` to surface filename+inode pairs.

Control flow: `collectFileInfoForChanges` stats both roots and calls `walker.walk("/")`. `walk` registers non-root nodes, reads both directories, merges sorted names, prunes children whose inode and device match, stats only changed/missing entries, and recurses. `walkchunk` copies stat metadata, security capability, user xattrs, and symlink targets into `FileInfo`.

State/persistence: no durable state, but it reads filesystem metadata, xattrs, symlink targets, directory entries, inode/dev pairs, and overlay xattrs. Returned `FileInfo` trees intentionally omit unchanged subtrees and must only be used for change detection.

Dependencies/integration: integrates with common change logic in `changes.go`, `system.StatT`, `idtools`, Linux `getdents`, `logrus`, and overlay layer semantics. `OverlayChanges` delegates into `changes` with overlay-specific callbacks.

Risks: unsafe dirent parsing depends on Linux struct layout and assumes valid `Reclen`; large xattrs may be skipped only for `E2BIG`; same inode/device pruning can hide metadata differences if filesystem semantics are unusual; overlay opaque xattr handling is security-sensitive because it controls deletion output. Whiteout/opaque errors must not be swallowed except for expected not-exist/not-dir cases.

Test signals: covered indirectly by `changes_test.go`, `changes_posix_test.go`, overlay/archive tests, and `diff_test.go` whiteout application. Linux-specific behavior is also exercised by symlink timestamp tests and hardlink export ordering.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/archive/changes_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/archive/changes_other.go -->
# sources/cloud-native/containers-storage/pkg/archive/changes_other.go

Purpose: non-Linux fallback for collecting full `FileInfo` trees for directory change comparisons.

Important APIs/types/functions: `collectFileInfoForChanges` and `collectFileInfo`. The former runs old and new tree collection concurrently; the latter walks a single source tree into a `FileInfo` hierarchy.

Control flow: `collectFileInfoForChanges` starts two goroutines, each calling `collectFileInfo`, then waits for two errors on a channel before returning both roots. `collectFileInfo` stats the root, walks with `filepath.WalkDir`, rebases paths to absolute-in-tree paths, creates child `FileInfo` nodes under already-created parents, skips directory mount points on device changes, records `system.Lstat` metadata, and best-effort reads security capability xattrs.

State/persistence: no writes. It reads filesystem metadata and xattrs and materializes an in-memory tree. Unlike Linux, it does not prune unchanged inode/device matches.

Dependencies/integration: used by the platform-neutral change engine on non-Linux platforms. It depends on `system`, `idtools`, `filepath`, and Windows path cleanup for doubled backslashes.

Risks: concurrent old/new collection mutates separate result variables but returns on the first channel error; the other goroutine may still finish later, though the channel is buffered. Mount-point skipping only applies to directories and depends on `system.StatT.Dev`. Capability xattr errors are ignored here, unlike the Linux walker.

Test signals: exercised by generic change tests where supported; many symlink-heavy tests skip Windows. Windows path behavior is guarded by Windows-specific implementations and tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/archive/changes_other.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/archive/changes_posix_test.go -->
# sources/cloud-native/containers-storage/pkg/archive/changes_posix_test.go

Purpose: POSIX-oriented test coverage for hardlink ordering in exported change archives.

Important APIs/types/functions: `TestHardLinkOrder`, `tarHeaders`, and `walkHeaders`. The test builds a source tree, copies it, creates multiple hardlinks for each file in the destination, calls `ChangesDirs`, and exports the same changes in forward and reverse order.

Control flow: after building hardlinks, the test sorts changes ascending, exports headers, sorts changes descending, exports headers again, sorts both header lists by name, and compares name, size, type, and link target. Solaris is skipped because the copy helper is unreliable there.

State/persistence: uses temporary directories and hardlinks only. No durable state remains after test cleanup.

Dependencies/integration: validates `ChangesDirs`, `ExportChanges`, hardlink detection, and tar header generation from the archive package.

Risks/test signal: this specifically protects deterministic hardlink archive semantics: export order must not change whether an entry is emitted as file content or hardlink metadata. Regressions would produce archives that unpack differently depending on change ordering.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/archive/changes_posix_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/archive/changes_test.go -->
# sources/cloud-native/containers-storage/pkg/archive/changes_test.go

Purpose: broad behavioral tests for change detection, export/apply round-trips, and change size accounting.

Important APIs/types/functions: helpers `copyDir`, `FileType`, `FileData`, `createSampleDir`, `mutateSampleDir`, and `checkChanges`; tests `TestChangeString`, `TestChangesWithNoChanges`, `TestChangesWithChanges`, `TestChangesWithChangesGH13590`, `TestChangesDirsEmpty`, `TestChangesDirsMutated`, `TestApplyLayer`, and `TestChangesSize*`.

Control flow: tests create deterministic sample directories containing files, directories, symlinks, permissions, and timestamps. Mutation tests remove, replace, touch, and add entries, then compare expected `Change` sets. `TestApplyLayer` exports changes from a mutated tree, applies them back to the original, and asserts no remaining differences.

State/persistence: temporary filesystem state only. The tests force timestamps on non-symlinks and reset symlink times through platform hooks so symlink target changes are detectable.

Dependencies/integration: exercises `Changes`, `ChangesDirs`, `ExportChanges`, `ApplyLayer`, `NewTempArchive`, `ChangesSize`, `idtools.IDMappings`, and `system.Chtimes`.

Risks/test signal: tests guard subtle semantics: whiteout deletes, directory modification propagation, symlink target changes with same size/times, hardlink size accounting, and no-op diffs. Windows and Solaris skips highlight portability gaps.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/archive/changes_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/archive/changes_unix.go -->
# sources/cloud-native/containers-storage/pkg/archive/changes_unix.go

Purpose: Unix-specific metadata comparison helpers for archive change detection.

Important APIs/types/functions: `statDifferent`, `(*FileInfo).isDir`, `getIno`, and `hasHardlinks`.

Control flow: `statDifferent` maps old/new UIDs and GIDs into container IDs when possible, then compares mode, owner, rdev, file flags, mtime via `sameFsTimeSpec`, and size for non-directories. `isDir` treats the synthetic root as a directory and otherwise checks the Unix directory bit. `getIno` and `hasHardlinks` read `syscall.Stat_t`.

State/persistence: no writes; consumes stat metadata attached to `FileInfo`.

Dependencies/integration: called from common change sorting/comparison logic. Depends on `system.StatT`, `idtools`, and `x/sys/unix`.

Risks: owner comparison depends on successful ID map conversion and can fall back to host IDs. Directory size is intentionally ignored; filesystems with coarse timestamp precision rely on `sameFsTimeSpec`. File flags are compared on Unix, so BSD immutable/opaque flags influence diffs.

Test signals: generic change tests cover metadata mutations; BSD-specific file flag tests live outside this subset, and `changes_unix_test.go` provides symlink timestamp support.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/archive/changes_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/archive/changes_unix_test.go -->
# sources/cloud-native/containers-storage/pkg/archive/changes_unix_test.go

Purpose: Unix helper for tests that need stable symlink timestamps.

Important APIs/types/functions: `resetSymlinkTimes`.

Control flow: creates two zero `unix.Timeval` values and calls `unix.Lutimes` so the symlink itself, not its target, has deterministic atime/mtime.

State/persistence: mutates temporary test symlink metadata only.

Dependencies/integration: used by `createSampleDir` and mutation tests in `changes_test.go` to make symlink target changes visible even when length and timestamp would otherwise be ambiguous.

Risks/test signal: if `Lutimes` behavior varies by filesystem/platform, symlink change tests may become flaky. The helper is Unix-only; Windows uses a no-op variant.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/archive/changes_unix_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/archive/changes_windows.go -->
# sources/cloud-native/containers-storage/pkg/archive/changes_windows.go

Purpose: Windows implementation of archive change comparison primitives.

Important APIs/types/functions: `statDifferent`, `(*FileInfo).isDir`, `getIno`, and `hasHardlinks`.

Control flow: `statDifferent` compares mtime, mode, and size for non-directories. Windows inode and hardlink helpers return zero/false because this path does not use Unix inode/hardlink metadata.

State/persistence: no writes; reads `system.StatT` values supplied by the common change scanner.

Dependencies/integration: used by common archive change logic on Windows. It keeps the API shape compatible with Unix files while reflecting reduced metadata support.

Risks: no UID/GID, rdev, xattr, file flag, inode, or hardlink comparison means Windows diffs are necessarily less precise. Size comparison expression relies on operator precedence to ignore directory size.

Test signals: Windows-specific reset helper is no-op, and many generic symlink/hardlink tests skip Windows; coverage is mainly compile-time and generic path behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/archive/changes_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/archive/changes_windows_test.go -->
# sources/cloud-native/containers-storage/pkg/archive/changes_windows_test.go

Purpose: Windows test shim for symlink timestamp reset.

Important APIs/types/functions: `resetSymlinkTimes`.

Control flow: returns nil without modifying filesystem metadata.

State/persistence: none.

Dependencies/integration: satisfies the helper used by shared `changes_test.go` on Windows, where the symlink-heavy tests are mostly skipped.

Risks/test signal: the no-op means shared tests cannot assert symlink timestamp-sensitive behavior on Windows. This file is a portability shim, not substantive behavior coverage.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/archive/changes_windows_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/archive/copy.go -->
# sources/cloud-native/containers-storage/pkg/archive/copy.go

Purpose: implements Docker-style copy semantics by turning source resources into tar streams, optionally rebasing entries, and extracting into destination paths.

Important APIs/types/functions: errors `ErrNotDirectory`, `ErrDirNotExists`, `ErrCannotCopyDir`, `ErrInvalidCopySource`; path helpers `PreserveTrailingDotOrSeparator`, `SplitPathDirEntry`; `CopyInfo`; `CopyInfoSourcePath`; `CopyInfoDestinationPath`; `PrepareArchiveCopy`; `RebaseArchiveEntries`; `CopyResource`; `CopyTo`; `ResolveHostSourcePath`; `GetRebaseName`.

Control flow: source paths are normalized, cleaned, and optionally resolved through symlinks. `TarResourceRebase` archives the containing directory with `IncludeFiles` and `RebaseNames`. `CopyInfoDestinationPath` follows destination symlinks, validates parent existence, and records whether the target exists and is a directory. `PrepareArchiveCopy` applies the copy matrix: merge into existing directories, reject directory-to-file copies, reject file-to-nonexistent-asserted-directory copies, or rebase the first archive path element to the desired destination basename. `CopyTo` extracts with `NoLchown` and `NoOverwriteDirNonDir`.

State/persistence: writes happen only through final `Untar` extraction. The rebasing path uses an `io.Pipe` goroutine and tar reader/writer; no intermediate archive file is persisted.

Dependencies/integration: integrates with `TarWithOptions`, `Untar`, `fileutils.Lexists`, tar headers, path normalization in OS-specific files, and archiver copy helpers.

Risks: path intent is encoded in trailing slash and `/.`, so normalization bugs can copy the wrong level. Destination symlink resolution follows up to 10 hops. `RebaseArchiveEntries` uses first string replacement, so callers must pass normalized base names. Pipe goroutine errors propagate only when the returned reader is consumed.

Test signals: `copy_unix_test.go` covers source/destination matrix cases A-J, symlink following, trailing slash/current-dir preservation, and expected error classes.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/archive/copy.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/archive/copy_unix.go -->
# sources/cloud-native/containers-storage/pkg/archive/copy_unix.go

Purpose: Unix path normalization shim for archive copy code.

Important APIs/types/functions: `normalizePath`.

Control flow: returns the input path unchanged because Unix paths already use the process-native separator conventions expected by `filepath`.

State/persistence: none.

Dependencies/integration: called throughout `copy.go` before path cleaning, splitting, symlink resolution, and copy decisions. The Windows counterpart adapts paths for Windows semantics.

Risks/test signal: behavior is intentionally minimal; correctness is validated indirectly by the Unix copy matrix tests in `copy_unix_test.go`.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/archive/copy_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/archive/copy_unix_test.go -->
# sources/cloud-native/containers-storage/pkg/archive/copy_unix_test.go

Purpose: exhaustive Unix tests for `CopyResource` and the copy preparation matrix.

Important APIs/types/functions: helpers `getTestTempDirs`, `isNotDir`, `joinTrailingSep`, `fileContentsEqual`, `dirContentsEqual`, `logDirContents`, `testCopyHelper`, `testCopyHelperFSym`; tests `TestCopyErr*` and `TestCopyCaseA` through `TestCopyCaseJ` plus symlink-following variants.

Control flow: tests create sample trees, prepare source/destination combinations, call `CopyResource` with follow-link false or true, and verify file hashes or directory diffs using `ChangesDirs`. The documented matrix covers file-to-new-file, file-to-asserted-directory error, file overwrite, file into directory, directory creation, directory-to-file errors, directory under existing directory, contents-only copy with `/.`, and symlink-to-file/directory variants.

State/persistence: temporary directories, files, symlinks, and copy outputs only.

Dependencies/integration: validates `CopyInfoSourcePath`, `TarResource`, `CopyTo`, `CopyResource`, path intent preservation, symlink following, tar rebasing, and diff-based directory equality.

Risks/test signal: protects user-facing copy semantics where a trailing separator or `/.` changes whether the directory itself or only contents are copied. It also asserts errors for invalid parent or not-directory destinations.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/archive/copy_unix_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/archive/copy_windows.go -->
# sources/cloud-native/containers-storage/pkg/archive/copy_windows.go

Purpose: Windows path normalization shim for archive copy code.

Important APIs/types/functions: `normalizePath`.

Control flow: converts slash separators to Windows separators via `filepath.FromSlash`.

State/persistence: none.

Dependencies/integration: used by `copy.go` before path cleaning, destination symlink resolution, split logic, and archive copy decisions.

Risks/test signal: Windows path handling differs for volumes, long paths, and trailing separators; this shim only normalizes separators. Coverage comes from Windows archive/copy tests outside this subset and compile-time integration.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/archive/copy_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/archive/diff.go -->
# sources/cloud-native/containers-storage/pkg/archive/diff.go

Purpose: applies OCI/Docker layer tar streams to a destination directory, including whiteout handling, AUFS metadata compatibility, ID remapping, immutable flag reset, and directory mtime restoration.

Important APIs/types/functions: `UnpackLayer`, `ApplyLayer`, `ApplyUncompressedLayer`, and `applyLayerHandler`.

Control flow: `applyLayerHandler` cleans destination, sets umask to zero, optionally decompresses, and calls `UnpackLayer`. `UnpackLayer` iterates tar headers, normalizes names, creates missing parent dirs, skips AUFS metadata except hardlink plnk targets, rejects path breakout via `filepath.Rel`, processes `.wh.*` whiteouts and opaque directory whiteouts, removes/replaces existing non-merge entries after resetting immutable flags, remaps IDs, extracts via `extractTarFileEntry`, tracks unpacked paths, and restores directory times/file flags after all entries.

State/persistence: mutates the destination tree by creating, replacing, deleting, chmod/chowning, timestamping, xattrs/flags, and temporary AUFS hardlink files. Size returned is cumulative tar payload size.

Dependencies/integration: relies on tar readers, `fileutils.Lexists`, `idtools`, `system.Umask/Chtimes`, `DecompressStream`, `WriteFileFlagsFromTarHeader`, `resetImmutable`, whiteout constants, and lower-level extraction helpers from archive package.

Risks: this is security-sensitive. Breakout prevention, hardlink/symlink extraction, whiteout deletion, and immutable flag reset must stay correct. Windows colon filtering is permissive for Linux images on Windows. AUFS plnk temporary extraction requires correct cleanup. Directory mtime restoration can fail after later mutations.

Test signals: `diff_test.go` covers invalid filenames, hardlink/symlink breakout attempts, and whiteout layering. `changes_test.go` applies exported layers round-trip. Chroot archive tests exercise this through a sandboxed reexec path.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/archive/diff.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/archive/diff_test.go -->
# sources/cloud-native/containers-storage/pkg/archive/diff_test.go

Purpose: security and whiteout tests for applying layer tar streams.

Important APIs/types/functions: `TestApplyLayerInvalidFilenames`, `TestApplyLayerInvalidHardlink`, `TestApplyLayerInvalidSymlink`, `TestApplyLayerWhiteouts`, `makeTestLayer`, and `readDirContents`.

Control flow: breakout tests build malicious tar headers and pass them to shared `testBreakout` with `applylayer`, expecting either a `breakoutError` or no mutation/leak outside the destination. Whiteout tests apply a sequence of synthetic layers and verify final directory contents after regular entries, `.wh.<name>` removals, escaped dot names, and `.wh..wh..opq` opaque directory behavior.

State/persistence: temporary test trees and generated layer streams only.

Dependencies/integration: exercises `UnpackLayer`, `ApplyLayer`, `Tar`, whiteout constants, path breakout detection, hardlink/symlink extraction checks, and directory walking.

Risks/test signal: protects against archive breakout vulnerabilities and whiteout regressions. Windows skips indicate platform gaps in link and whiteout behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/archive/diff_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/archive/example_changes.go -->
# sources/cloud-native/containers-storage/pkg/archive/example_changes.go

Purpose: ignored build-tag example command that creates an archive stream from differences between an old and new directory.

Important APIs/types/functions: flags `-D`, `-newdir`, `-olddir`; `main`; helper `prepareUntarSourceDirectory`.

Control flow: `main` parses flags, enables debug logging, creates default temp old/new dirs when paths are absent, populates the new dir with files and optional hardlinks, calls `archive.ChangesDirs`, exports changes with `archive.ExportChanges`, copies the archive to stdout, and reports byte count on stderr.

State/persistence: temporary directories are created and removed when defaults are used. Output is a tar stream on stdout.

Dependencies/integration: demonstrates the public archive diff/export API and logrus debugging. It has `//go:build ignore`, so it is not part of normal builds.

Risks/test signal: it references older `ChangesDirs`/`ExportChanges` call shapes that may drift from current signatures; as an ignored sample, it can silently rot unless manually built. No direct tests target it.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/archive/example_changes.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/archive/fflags_bsd.go -->
# sources/cloud-native/containers-storage/pkg/archive/fflags_bsd.go

Purpose: FreeBSD implementation for preserving BSD file flags in tar PAX records and resetting immutable flags before layer mutations.

Important APIs/types/functions: `paxSCHILYFflags`, maps `flagNameToValue` and `flagValueToName`, `parseFileFlags`, `formatFileFlags`, `ReadFileFlagsToTarHeader`, `WriteFileFlagsFromTarHeader`, and `resetImmutable`.

Control flow: reading formats flags from `system.Lstat(path).Flags()` and writes `SCHILY.fflags` into PAX records. Writing parses comma-separated flags, supports `no<flag>` clear operations, reads current flags, and applies `(current & ^clear) | set` with `system.Lchflags`. `resetImmutable` clears system/user immutable bits before delete/replace operations.

State/persistence: reads and writes FreeBSD file flags; tar headers carry flag metadata through PAX records.

Dependencies/integration: used by archive tar creation/extraction and `diff.go` replacement/deletion handling. Depends on `system` FreeBSD flag constants and `syscall.Stat_t.Flags`.

Risks: unknown flags cause hard errors, which can block archive operations. Clearing immutable flags is necessary but security-sensitive. The reverse map emits only short names, so formatting is normalized rather than round-tripping aliases.

Test signals: BSD-specific tests outside this subset cover file flag diffs, copy preservation, and applying layers to immutable files.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/archive/fflags_bsd.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/archive/fflags_unsupported.go -->
# sources/cloud-native/containers-storage/pkg/archive/fflags_unsupported.go

Purpose: non-FreeBSD no-op implementation of file flag preservation hooks.

Important APIs/types/functions: `ReadFileFlagsToTarHeader`, `WriteFileFlagsFromTarHeader`, and `resetImmutable`.

Control flow: all functions return nil and do not inspect their inputs.

State/persistence: none.

Dependencies/integration: keeps archive extraction and tar creation call sites platform-neutral. On unsupported platforms, `diff.go` can call `resetImmutable` without conditional code.

Risks/test signal: platforms using this file do not preserve BSD-style flags and cannot clear immutable flags through this abstraction. Behavior is intentional and covered mostly by compile-time portability plus non-BSD layer tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/archive/fflags_unsupported.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/archive/filter.go -->
# sources/cloud-native/containers-storage/pkg/archive/filter.go

Purpose: helper for running external compression/decompression filters as streaming subprocesses.

Important APIs/types/functions: package cache `filterPath`, `getFilterPath`, `errorRecordingReader`, and `tryProcFilter`.

Control flow: `getFilterPath` memoizes `exec.LookPath` results in `sync.Map`, using an empty string for missing commands. `tryProcFilter` returns `(nil,false)` when the command is unavailable. Otherwise it builds an `exec.Command`, wires input through an `errorRecordingReader`, stdout to an `io.Pipe`, stderr to a buffer, starts a goroutine, runs the process, prefers input read errors over process errors, includes stderr in process errors, closes the pipe with the final error, and calls caller cleanup.

State/persistence: caches filter executable paths in-process. No durable writes.

Dependencies/integration: used by archive compression paths that can delegate to external tools such as bzip2/xz. Integrates with streaming readers so callers can consume stdout lazily.

Risks: process lifetime is tied to reader consumption; if callers do not drain/close, goroutines and subprocesses can linger. Cached negative lookups mean later PATH changes are ignored. Cleanup is only called after process execution, not when command is missing.

Test signals: `filter_test.go` covers missing commands, successful `cat`, stderr-enriched failure, and cleanup invocation.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/archive/filter.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/archive/filter_test.go -->
# sources/cloud-native/containers-storage/pkg/archive/filter_test.go

Purpose: tests external filter subprocess helper behavior.

Important APIs/types/functions: `TestTryProcFilter`.

Control flow: subtests verify three cases: a nonexistent command returns nil/false; `cat -` returns input unchanged; a shell command that writes stderr and exits 21 causes `io.ReadAll` to return an error containing stderr and exit status, and eventually calls the cleanup function.

State/persistence: no durable state; uses an atomic bool to observe cleanup.

Dependencies/integration: requires common Unix-like tools `cat` and `sh` in PATH for success/failure subtests.

Risks/test signal: protects error propagation and cleanup behavior. It does not test cached path invalidation, input read errors, or early reader closure.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/archive/filter_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/archive/time_linux.go -->
# sources/cloud-native/containers-storage/pkg/archive/time_linux.go

Purpose: Linux conversion from Go `time.Time` to `syscall.Timespec` for timestamp syscalls that support `UTIME_OMIT`.

Important APIs/types/functions: `timeToTimespec`.

Control flow: returns a timespec with `Nsec` equal to `(1<<30)-2` for zero time, matching Linux `UTIME_OMIT`; otherwise converts `UnixNano` with `syscall.NsecToTimespec`.

State/persistence: none.

Dependencies/integration: used by archive timestamp application paths to leave timestamps unchanged when a zero time means omitted.

Risks/test signal: Linux-specific sentinel behavior differs from unsupported platforms. Incorrect sentinel values would unexpectedly set timestamps to epoch or current time.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/archive/time_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/archive/time_unsupported.go -->
# sources/cloud-native/containers-storage/pkg/archive/time_unsupported.go

Purpose: fallback timestamp conversion for non-Linux platforms without Linux `UTIME_OMIT` semantics.

Important APIs/types/functions: `timeToTimespec`.

Control flow: zero time maps to Unix nanoseconds `0`; non-zero times map to `time.UnixNano()`, then `syscall.NsecToTimespec`.

State/persistence: none.

Dependencies/integration: used by shared archive timestamp code on non-Linux platforms.

Risks/test signal: zero time becomes epoch instead of omit, so behavior can diverge from Linux. Platform tests for timestamp behavior outside this subset cover user-visible effects.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/archive/time_unsupported.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/archive/utils_test.go -->
# sources/cloud-native/containers-storage/pkg/archive/utils_test.go

Purpose: shared test helpers for archive breakout/security tests.

Important APIs/types/functions: `testUntarFns` and `testBreakout`.

Control flow: `testBreakout` creates sibling `dest` and `victim` directories, writes a unique `victim/hello`, streams supplied tar headers into `Untar` or `ApplyLayer`, allows `breakoutError` as a successful detection, then verifies the victim directory and file were not removed, modified, replaced, or read into destination output.

State/persistence: temporary test directories only.

Dependencies/integration: supports `diff_test.go` and related untar tests by abstracting both extraction APIs behind `testUntarFns`.

Risks/test signal: this is a high-value security oracle for path traversal through names, hardlinks, and symlinks. It cannot prove all breakouts are impossible, but it checks concrete read/write/remove scenarios.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/archive/utils_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/archive/whiteouts.go -->
# sources/cloud-native/containers-storage/pkg/archive/whiteouts.go

Purpose: central constants describing Docker/AUFS whiteout filenames used in layer archives.

Important APIs/types/functions: `WhiteoutPrefix`, `WhiteoutMetaPrefix`, `WhiteoutLinkDir`, and `WhiteoutOpaqueDir`.

Control flow: no functions; constants are consumed by tar creation/extraction and diff logic.

State/persistence: these names become on-disk tar entries and drive deletion/opaque-directory semantics during layer application.

Dependencies/integration: used by `diff.go`, change export, overlay conversion, and tests. `.wh.<file>` denotes deletion; `.wh..wh..opq` makes a directory opaque; `.wh..wh.plnk` carries AUFS hardlink targets.

Risks/test signal: changing constants breaks layer compatibility. Whiteout handling is covered by `diff_test.go`, `changes_test.go`, and overlay archive tests outside this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/archive/whiteouts.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/archive/wrap.go -->
# sources/cloud-native/containers-storage/pkg/archive/wrap.go

Purpose: small testing/demo helper for generating in-memory tar archives from path/content string pairs.

Important APIs/types/functions: `Generate` and `parseStringPairs`.

Control flow: `parseStringPairs` groups variadic strings into `[name,content]` pairs, defaulting missing content to empty. `Generate` writes each pair as a tar regular file header and content into a `bytes.Buffer`, closes the tar writer, and returns the buffer as an `io.Reader`.

State/persistence: all state is in memory. No filesystem writes.

Dependencies/integration: useful for tests and examples that need simple tar streams without setting full metadata.

Risks: buffers the entire archive, sets minimal tar metadata, and treats incomplete pairs as empty files. It is not suitable for large archives or production metadata preservation.

Test signals: `wrap_test.go` validates empty-file and content-file generation.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/archive/wrap.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/archive/wrap_test.go -->
# sources/cloud-native/containers-storage/pkg/archive/wrap_test.go

Purpose: tests `Generate` tar helper output.

Important APIs/types/functions: `TestGenerateEmptyFile` and `TestGenerateWithContent`.

Control flow: each test calls `Generate`, reads the returned tar stream with `tar.NewReader`, collects header names and payload strings, and compares them with expected pairs.

State/persistence: in-memory buffers only.

Dependencies/integration: verifies the helper produces a valid tar stream consumable by Go's tar reader.

Risks/test signal: coverage is intentionally narrow; it does not inspect permissions, multiple pairs, malformed names, or large payloads.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/archive/wrap_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/chrootarchive/archive.go -->
# sources/cloud-native/containers-storage/pkg/chrootarchive/archive.go

Purpose: public chroot-aware archiver facade that routes tar/untar/copy/apply operations through safer platform-specific implementations.

Important APIs/types/functions: `NewArchiver`, `NewArchiverWithChown`, `Untar`, `UntarWithRoot`, `UntarUncompressed`, `untarHandler`, `Tar`, `CopyFileWithTarAndChown`, `CopyWithTarAndChown`, and `UntarPathAndChown`.

Control flow: `untarHandler` validates non-nil archive, defaults options and rootless `InUserNS`, ensures destination exists with mapped root ownership, creates an `unpackDestination`, optionally decompresses, and invokes platform-specific unpack. `Tar` delegates to platform-specific pack. Copy/chown helpers create archive archivers with untar mappings and optional chown overrides; when a hasher is supplied, they wrap `Untar` with `io.TeeReader` or a pipe to hash either whole archives or file payload.

State/persistence: creates destination directories, extracts archives, writes copied files, and may hash streamed content. No independent persistent metadata is stored.

Dependencies/integration: wraps `pkg/archive` archiver APIs, `idtools`, `unshare`, and platform-specific `newUnpackDestination`, `invokeUnpack`, and `invokePack`.

Risks: security depends on correct `root` selection; `UntarWithRoot` is intended for attacker-controlled destination paths. Hasher goroutine/pipe handling must not deadlock if untar fails. Chown/ID map interactions affect file ownership.

Test signals: `archive_test.go` covers chroot tar/untar, huge exclude lists, nil archive errors, copy/chown helpers, empty slow readers, and dot-dot-like safe names. `archive_unix_test.go` covers CVE-2018-15664 symlink attack scenarios.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/chrootarchive/archive.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/chrootarchive/archive_darwin.go -->
# sources/cloud-native/containers-storage/pkg/chrootarchive/archive_darwin.go

Purpose: macOS fallback implementation for chrootarchive pack/unpack hooks.

Important APIs/types/functions: `unpackDestination`, `Close`, `newUnpackDestination`, `invokeUnpack`, and `invokePack`.

Control flow: `newUnpackDestination` records only `dest`. `invokeUnpack` calls `archive.Unpack` directly. `invokePack` ignores `root` and calls `archive.TarWithOptions`.

State/persistence: extraction and tar creation happen inline in the current process without chroot sandboxing.

Dependencies/integration: satisfies platform hook interfaces for `archive.go` on Darwin.

Risks: root restriction is explicitly not implemented for pack, and unpack is not sandboxed through chroot/pivot. Security properties differ from Linux/Unix reexec implementations.

Test signals: generic chroot tests may run where applicable, but malicious symlink root tests are Unix-not-Windows and most meaningful on platforms with real chroot support.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/chrootarchive/archive_darwin.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/chrootarchive/archive_test.go -->
# sources/cloud-native/containers-storage/pkg/chrootarchive/archive_test.go

Purpose: broad tests for chrootarchive public operations and wrappers.

Important APIs/types/functions: test wrappers `TarUntar`, `CopyFileWithTar`, `UntarPath`, `CopyWithTar`; helpers `prepareSourceDirectory`, `compareDirectories`, `compareDirectoriesChown`, `compareFiles`, `slowEmptyTarReader`; tests from `TestChrootTarUntar` through `TestChrootApplyDotDotFile`.

Control flow: tests create temporary trees, tar and untar through chroot archiver wrappers, exercise huge exclude lists passed via pipe/JSON instead of argv/env, reject nil archives and invalid directory untar/copy operations, copy files/directories/symlinks with and without chown, compare output via archive diffs or CRCs, and verify slow zero-padded empty tar readers complete. `TestChrootApplyDotDotFile` verifies a name containing `..` but not path traversal is allowed.

State/persistence: temporary files, directories, symlinks, tar files, and ownership changes where permitted.

Dependencies/integration: uses `archive`, `idtools`, `reexec.Init`, filesystem syscalls, and chrootarchive public APIs.

Risks/test signal: tests protect IPC of large options, rootless/ownership behavior, wrapper correctness, empty archive handling, and accidental over-rejection of safe dot-dot names. Several tests skip Windows/Solaris for known platform limitations.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/chrootarchive/archive_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/chrootarchive/archive_unix.go -->
# sources/cloud-native/containers-storage/pkg/chrootarchive/archive_unix.go

Purpose: Unix non-Windows/non-Darwin reexec implementation for sandboxed archive unpacking and packing.

Important APIs/types/functions: `unpackDestination`, `procPathForFd`, `untar`, `newUnpackDestination`, `invokeUnpack`, `tar`, and `invokePack`. Constants define extra file descriptors 3 for tar options and 4 for root.

Control flow: parent `newUnpackDestination` opens the root directory as an fd and computes an absolute path inside the future chroot. `invokeUnpack` starts `storage-untar`, passes the archive on stdin, JSON-encodes `TarOptions` through fd 3, and passes the root fd as fd 4. Child `untar` locks its OS thread, reads options, fchdirs to fd 4 when using `/proc/self/fd/4`, chroots, unpacks to the relative dest, and flushes stdin. `invokePack` starts `storage-tar`, streams tar stdout through a pipe, and sends options as JSON stdin; child `tar` chroots and calls `archive.TarWithOptions`.

State/persistence: extraction mutates the chroot root; packing reads from it. Parent/child coordinate through pipes and inherited fds, not durable files.

Dependencies/integration: uses `reexec`, `archive.Unpack`, `archive.TarWithOptions`, JSON via `jsoniter`, Unix fd/chroot helpers, and root path safety from `archive.go`.

Risks: descriptor numbering is part of the ABI between parent and child. If child errors while upstream decompression is active, `invokeUnpack` drains input to avoid pipe deadlock. Path relativity and root fd handling are security-sensitive.

Test signals: huge exclude list test confirms options are not passed via argv/env. CVE symlink tests in `archive_unix_test.go` validate root confinement.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/chrootarchive/archive_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/chrootarchive/archive_unix_test.go -->
# sources/cloud-native/containers-storage/pkg/chrootarchive/archive_unix_test.go

Purpose: Unix security regression tests for CVE-2018-15664 style malicious symlink paths.

Important APIs/types/functions: `TestUntarWithMaliciousSymlinks`, `TestTarWithMaliciousSymlinks`, and `isDataInTar`.

Control flow: `TestUntarWithMaliciousSymlinks` creates a root containing a symlink to a host-controlled parent and verifies `UntarWithRoot(..., root)` does not overwrite the host file, while deliberately using the symlink as root demonstrates the misuse can overwrite. `TestTarWithMaliciousSymlinks` attempts several path/include combinations and verifies host file data is not leaked into tar output when using the safe root.

State/persistence: temporary root/host files/symlinks only.

Dependencies/integration: exercises `UntarWithRoot`, `Tar`, `archive.TarWithOptions`, Unix symlinks, and tar readers.

Risks/test signal: high-value tests for chroot confinement and symlink race avoidance. They make the intended root trust boundary explicit: the root must not be attacker controlled.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/chrootarchive/archive_unix_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/chrootarchive/archive_windows.go -->
# sources/cloud-native/containers-storage/pkg/chrootarchive/archive_windows.go

Purpose: Windows implementation of chrootarchive hooks without chroot/reexec sandboxing.

Important APIs/types/functions: `unpackDestination`, `Close`, `newUnpackDestination`, `chroot`, `invokeUnpack`, and `invokePack`.

Control flow: records destination directly, no-ops `chroot`, invokes `archive.Unpack` inline with `longpath.AddPrefix(dest.dest)`, and invokes `archive.TarWithOptions` inline for packing.

State/persistence: extraction and tar creation happen in the current process.

Dependencies/integration: integrates with `archive` and `longpath` for Windows path length handling.

Risks: no chroot isolation exists on Windows, so safety relies on archive path sanitization rather than process root confinement. `applyLayerHandler` in `diff_windows.go` also passes nil options to `UnpackLayer`, ignoring its `options` parameter.

Test signals: Windows-specific archive tests outside this subset cover some canonical naming and invalid destination cases; many chroot tests skip Windows.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/chrootarchive/archive_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/chrootarchive/chroot_linux.go -->
# sources/cloud-native/containers-storage/pkg/chrootarchive/chroot_linux.go

Purpose: Linux root-switch implementation for chrootarchive child processes, preferring `pivot_root` in a private mount namespace and falling back to `chroot`.

Important APIs/types/functions: `chroot` and `realChroot`.

Control flow: loads process capabilities, preloads NSS lookups outside the chroot, uses `realChroot` when only `CAP_SYS_CHROOT` is available, otherwise unshares mount namespace, makes `/` private, bind-mounts the target root if needed, creates `.pivot_root`, calls `unix.PivotRoot`, changes to `/`, makes old root private, unmounts it, and cleans up the pivot dir. `realChroot` calls `unix.Chroot` then `Chdir("/")`.

State/persistence: creates/removes a temporary pivot directory and may add a bind mount/mount namespace state inside the child process. It changes the process root and cwd.

Dependencies/integration: used by reexec children in `archive_unix.go` and `diff_unix.go`. Depends on `mount`, Linux capabilities, NSS preloading, and `x/sys/unix`.

Risks: mount namespace and pivot cleanup are subtle. Failure paths fall back to chroot only after cleanup. If old root is not unmounted, extraction could see host paths. NSS preloading avoids loading attacker-controlled libraries/config from the new root.

Test signals: exercised indirectly by chrootarchive tests and malicious symlink tests on Linux.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/chrootarchive/chroot_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/chrootarchive/chroot_unix.go -->
# sources/cloud-native/containers-storage/pkg/chrootarchive/chroot_unix.go

Purpose: non-Linux/non-Darwin Unix chroot implementation.

Important APIs/types/functions: `realChroot` and `chroot`.

Control flow: `realChroot` calls `unix.Chroot(path)` then `unix.Chdir("/")`; `chroot` delegates to `realChroot`.

State/persistence: changes process root and current working directory in the reexec child.

Dependencies/integration: used by `archive_unix.go` and `diff_unix.go` on supported Unix platforms without Linux pivot_root implementation.

Risks/test signal: weaker than Linux pivot_root because the old root is not explicitly unmounted. Correctness depends on OS chroot behavior and child process isolation.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/chrootarchive/chroot_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/chrootarchive/diff.go -->
# sources/cloud-native/containers-storage/pkg/chrootarchive/diff.go

Purpose: public chrootarchive wrappers for applying layer diffs.

Important APIs/types/functions: `ApplyLayer` and `ApplyUncompressedLayer`.

Control flow: `ApplyLayer` delegates to platform `applyLayerHandler` with decompression enabled and default empty `archive.TarOptions`; `ApplyUncompressedLayer` delegates with caller options and no decompression.

State/persistence: all filesystem mutation occurs in platform-specific handlers, typically through `archive.UnpackLayer` inside a chroot/reexec child.

Dependencies/integration: thin facade over `archive` diff semantics and per-platform `diff_*` files.

Risks/test signal: public comments say `ApplyLayer` stream can only be uncompressed, but the implementation passes `decompress=true`, matching archive package behavior. Tests in `archive_test.go` cover empty archive application and safe dot-dot names.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/chrootarchive/diff.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/chrootarchive/diff_darwin.go -->
# sources/cloud-native/containers-storage/pkg/chrootarchive/diff_darwin.go

Purpose: Darwin `applyLayerHandler` implementation without chroot/reexec sandboxing.

Important APIs/types/functions: `applyLayerHandler`.

Control flow: cleans destination, optionally decompresses with `archive.DecompressStream`, creates a temp extraction directory under `os.Getenv("temp")`, calls `archive.UnpackLayer(dest, layer, options)`, removes the temp directory, and wraps errors with destination context.

State/persistence: mutates destination through `UnpackLayer`; creates/removes a temporary directory.

Dependencies/integration: used by public `ApplyLayer` wrappers on Darwin.

Risks: no chroot confinement. `os.Getenv("temp")` may be empty on Unix-like systems, so temp placement depends on `os.MkdirTemp` behavior with an empty dir. Cleanup ignores remove errors.

Test signals: generic chroot apply tests may cover this path on Darwin, but Linux-specific sandbox behavior is not present.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/chrootarchive/diff_darwin.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/chrootarchive/diff_unix.go -->
# sources/cloud-native/containers-storage/pkg/chrootarchive/diff_unix.go

Purpose: Unix non-Windows/non-Darwin reexec implementation for applying layer diffs inside a chroot.

Important APIs/types/functions: `applyLayerResponse`, child entrypoint `applyLayer`, and parent `applyLayerHandler`.

Control flow: parent cleans dest, optionally decompresses, defaults options/rootless `InUserNS`, marshals options into `OPT` env, starts `storage-applyLayer` with dest as root/chroot target, streams layer on stdin, and decodes JSON response containing layer size. Child locks OS thread, detects rootless state, chroots, sets umask zero, unmarshals `OPT`, creates a temporary extraction dir under `/`, sets `TMPDIR`, calls `archive.UnpackLayer("/", os.Stdin, options)`, removes temp dir, JSON-encodes size, flushes stdin, and exits.

State/persistence: mutates the chrooted destination root, creates/removes a temp directory inside it, and uses process environment for options IPC.

Dependencies/integration: uses `reexec`, `archive.DecompressStream`, `archive.UnpackLayer`, `system.Umask`, `unshare`, and `jsoniter`.

Risks: options are passed through environment, unlike untar options; very large option sets could hit env limits here. Error output is captured and included. Chroot/pivot correctness is inherited from platform `chroot`.

Test signals: `archive_test.go` covers chroot apply of slow empty tar and safe `..` filename, while archive diff tests cover lower-level layer semantics.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/chrootarchive/diff_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/chrootarchive/diff_windows.go -->
# sources/cloud-native/containers-storage/pkg/chrootarchive/diff_windows.go

Purpose: Windows `applyLayerHandler` implementation without chroot sandboxing.

Important APIs/types/functions: `applyLayerHandler`.

Control flow: cleans destination, prefixes it with `longpath.AddPrefix`, optionally decompresses, creates a temp extraction directory under `os.Getenv("temp")`, calls `archive.UnpackLayer(dest, layer, nil)`, removes temp dir, and returns size or wrapped error.

State/persistence: mutates destination and creates/removes temp directory.

Dependencies/integration: uses `archive.DecompressStream`, `archive.UnpackLayer`, and Windows long path handling.

Risks: the function ignores its `options` parameter and always passes nil to `UnpackLayer`, so caller-provided tar options are lost on Windows. No chroot isolation exists. Error formatting uses string interpolation instead of wrapping in one path.

Test signals: Windows coverage is limited; many layer/link tests skip Windows.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/chrootarchive/diff_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/chrootarchive/init_unix.go -->
# sources/cloud-native/containers-storage/pkg/chrootarchive/init_unix.go

Purpose: registers Unix reexec entrypoints for chrootarchive helper processes and provides small child-process utilities.

Important APIs/types/functions: package `init`, `fatal`, and `flush`.

Control flow: `init` registers `storage-applyLayer`, `storage-untar`, and `storage-tar` with `reexec`. `fatal` writes an error to stderr and exits 1. `flush` copies all remaining reader bytes to `io.Discard`.

State/persistence: registration is process-local; `fatal` terminates the child process.

Dependencies/integration: required before parent code can call `reexec.Command` for those names. `flush` is used after unpack/apply to consume zero padding and keep upstream decompression processes from blocking.

Risks/test signal: missing registration would make all Unix chroot operations fail at runtime. Error output has no newline and is intended for parent capture.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/chrootarchive/init_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/chrootarchive/jsoniter.go -->
# sources/cloud-native/containers-storage/pkg/chrootarchive/jsoniter.go

Purpose: shared JSON implementation variable for Unix chrootarchive IPC.

Important APIs/types/functions: package variable `json`.

Control flow: binds `jsoniter.ConfigCompatibleWithStandardLibrary` to a package-level variable used by reexec parent/child code for options and responses.

State/persistence: none beyond process-local configuration.

Dependencies/integration: used in `archive_unix.go` and `diff_unix.go` to encode/decode `archive.TarOptions` and apply-layer responses.

Risks/test signal: keeping JSON behavior compatible with the standard library matters because options structs are shared with code that may expect standard encoding semantics.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/chrootarchive/jsoniter.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/chunked/bloom_filter_linux.go -->
# sources/cloud-native/containers-storage/pkg/chunked/bloom_filter_linux.go

Purpose: simple serialized bloom filter used by chunked layer cache files to avoid binary-searching digest tags for definitely-absent digests.

Important APIs/types/functions: `bloomFilterMaxLength`, `bloomFilter`, `newBloomFilter`, `newBloomFilterFromArray`, `hashFn`, `add`, `maybeContains`, `writeTo`, and `readBloomFilter`.

Control flow: `newBloomFilter` rounds bit array length to uint64 slots and guarantees at least one slot. `hashFn` uses CRC32 over seed-split slices modulo bit count to produce an array index and single-bit mask. `add` sets `k` bits; `maybeContains` checks all `k`. Serialization writes array length, `k`, and raw uint64 array in little endian; deserialization caps length at 100 MB before allocation.

State/persistence: serialized inside chunked cache big-data blobs. In memory, it is part of `cacheFile`.

Dependencies/integration: used by `cache_linux.go` when writing and reading layer lookaside caches and in `findDigestInternal`.

Risks: CRC32 hash functions are not cryptographic and false positives are expected; correctness relies on a later exact tag lookup. The max length check is important for malformed cache DoS resistance.

Test signals: `bloom_filter_linux_test.go` checks add/maybeContains behavior, hash bounds/masks over many sizes, and benchmarks bloom-assisted lookup.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/chunked/bloom_filter_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/chunked/bloom_filter_linux_test.go -->
# sources/cloud-native/containers-storage/pkg/chunked/bloom_filter_linux_test.go

Purpose: tests and benchmarks for chunked cache bloom filters.

Important APIs/types/functions: cache initialization globals, `initCache`, `BenchmarkLookupBloomFilter`, `BenchmarkLookupBloomRaw`, `TestBloomFilter`, and `TestStressBloomHashFn`.

Control flow: `initCache` builds many digest tags and a bloom filter. `TestBloomFilter` first verifies generated digests are absent, then adds and checks each. `TestStressBloomHashFn` iterates hash counts and bit-array sizes, including empty input, to assert indexes are in bounds and masks have exactly one bit.

State/persistence: in-memory caches only.

Dependencies/integration: exercises `newBloomFilter`, `hashFn`, `makeBinaryDigest`, `appendTag`, and `writeCacheFileToWriter`.

Risks/test signal: protects against out-of-bounds bloom indexing and malformed single-bit masks. Benchmarks document the intended speedup path but do not assert performance.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/chunked/bloom_filter_linux_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/chunked/cache_linux.go -->
# sources/cloud-native/containers-storage/pkg/chunked/cache_linux.go

Purpose: Linux chunked-layer lookaside cache for finding file payloads, hardlink-compatible files, and chunks in previously stored layers.

Important APIs/types/functions: constants `cacheKey`, `cacheVersion`, bloom settings; types `cacheFile`, `layer`, `layersCache`, `setBigData`; cache lifecycle `getLayersCache`, `load`, `release`; cache IO `loadLayerBigData`, `loadLayerCache`, `createCacheFileFromTOC`, `writeCache`, `readCacheFileFromMemory`; lookup helpers `makeBinaryDigest`, `calculateHardLinkFingerprint`, `generateFileLocation`, `parseFileLocation`, `appendTag`, `findBinaryTag`, `findDigestInternal`, `findFileInOtherLayers`, `findChunkInOtherLayers`, `unmarshalToc`.

Control flow: a process-global cache is ref-counted per `storage.Store`. Loading scans store layers, reuses existing loaded layers unless marked for mmap reload, attempts to mmap existing cache big-data, and creates missing writable caches from TOC big-data. `writeCache` parses TOC metadata, flattens if requested, emits tags for file digest, hardlink fingerprint, and chunk digest, stores variable location data and filenames, builds a bloom filter, writes a versioned binary blob through `SetLayerBigData`, and returns an in-memory `cacheFile`. Lookup converts digest strings to binary, bloom-filters by layer, binary-searches sorted tags, parses location/name, and returns target path plus offset.

State/persistence: persists binary cache blobs as layer big data under `chunked-manifest-cache`; may mmap those blobs and registers finalizers to `Munmap`. Uses mutexes/ref counts for process-local cache lifecycle.

Dependencies/integration: integrates with `containers/storage` layer store, graphdriver output formats, chunked minimal TOC metadata, `jsoniter`, OCI digests, mmap/madvise, and deduplication logic elsewhere in chunked package.

Risks: binary format parsing must be defensive against corrupt or malicious big data; max tag/bloom lengths reduce DoS risk. Global cache assumes one store identity. Finalizer-based mmap cleanup is best-effort, so explicit `release` matters. Hardlink fingerprint must include all metadata relevant to safe hardlink reuse. `unmarshalToc` rejects trailing non-whitespace to keep digests meaningful.

Test signals: `cache_linux_test.go` covers TOC parsing, flat/dir preparation, cache write/read round-trip, tag lookups for file/chunk/hardlink fingerprints, binary digest parsing, and fuzzes cache reading.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/chunked/cache_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/chunked/cache_linux_test.go -->
# sources/cloud-native/containers-storage/pkg/chunked/cache_linux_test.go

Purpose: tests chunked cache construction, serialization, parsing, and TOC unmarshalling.

Important APIs/types/functions: fixture `jsonTOC`, `TestPrepareMetadata`, `TestPrepareMetadataFlat`, `bigDataToBuffer`, `findTag`, `TestWriteCache`, `TestReadCache`, `FuzzReadCache`, `TestUnmarshalToc`, and `TestMakeBinaryDigest`.

Control flow: tests parse fixture TOC, validate prepared entry counts and flattened path shape, write cache data into a buffer-backed fake store, find digest/hardlink/chunk tags and decode locations, read the binary cache back and deep-compare, fuzz the cache parser and lookup path, verify TOC rejects trailing extra JSON, and assert digest string-to-binary conversion.

State/persistence: buffer-backed fake big-data only; no real store writes.

Dependencies/integration: exercises `prepareCacheFile`, `writeCache`, `readCacheFileFromMemory`, `findBinaryTag`, `calculateHardLinkFingerprint`, `parseFileLocation`, `unmarshalToc`, and graphdriver output formats.

Risks/test signal: protects cache binary compatibility and malformed input resilience. Fuzzing is especially relevant because cache blobs can be loaded from persistent layer metadata.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/chunked/cache_linux_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/chunked/compression.go -->
# sources/cloud-native/containers-storage/pkg/chunked/compression.go

Purpose: compatibility facade for chunked compression type constants and deprecated compressor entrypoint.

Important APIs/types/functions: type constants `TypeReg`, `TypeChunk`, `TypeLink`, `TypeChar`, `TypeBlock`, `TypeDir`, `TypeFifo`, `TypeSymlink`; deprecated `ZstdCompressor`.

Control flow: constants alias minimal metadata type strings. `ZstdCompressor` delegates to `pkg/chunked/compressor.ZstdCompressor`.

State/persistence: none.

Dependencies/integration: preserves public API compatibility for callers that imported `pkg/chunked` before the compressor moved to `pkg/chunked/compressor`.

Risks/test signal: removing or changing aliases would break external callers. No direct tests in this subset target this thin wrapper.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/chunked/compression.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/chunked/compression_linux.go -->
# sources/cloud-native/containers-storage/pkg/chunked/compression_linux.go

Purpose: Linux helpers for reading, validating, and decoding estargz and zstd:chunked manifests and tar-split metadata.

Important APIs/types/functions: `maxTocSize`, `typesToTar`, `typeToTarType`, `readEstargzChunkedManifest`, `openTmpFile`, `openTmpFileNoTmpFile`, `readZstdChunkedManifest`, `ensureTOCMatchesTarSplit`, `tarSizeFromTarSplit`, `ensureTimePointersMatch`, `ensureFileMetadataAttributesMatch`, `validateBlob`, `decodeAndValidateBlob`, and `decodeAndValidateBlobToStream`.

Control flow: estargz reading fetches the footer, parses TOC offset, bounds TOC size, fetches/gunzips the embedded tar TOC, and verifies its digest. zstd:chunked reading parses annotations for manifest/tar-split offsets and lengths, bounds sizes, fetches chunks, validates compressed checksums, optionally zstd-decodes, unmarshals TOC, authenticates tar-split only when the TOC carries a digest, writes tar-split to an unlinked temp file, and validates TOC and tar-split metadata match exactly. Helpers compute tar size from tar-split segments/files and compare metadata excluding data-location fields.

State/persistence: creates unlinked temporary files for tar-split data with `O_TMPFILE` or create+unlink fallback. Reads seekable remote blob ranges and annotation metadata.

Dependencies/integration: integrates with chunked layer download/convert logic, `minimal.TOC`, `getBlobAt`, `ensureAllBlobsDone`, `pgzip`, `zstd`, `tar-split`, OCI digests, and fallback error types.

Risks: size caps and digest validation are critical DoS/integrity controls. Tar-split without authenticated digest must be ignored. Metadata comparison must stay in sync with `minimal.FileMetadata`. Temporary file fallback assumes unlink succeeds and `/proc/self/fd` semantics in tests.

Test signals: `compression_linux_test.go` covers tar-split size calculation and unlinked temp-file creation; broader zstdchunked tests outside this subset cover manifest generation/parsing and tar type mapping.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/chunked/compression_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/chunked/compression_linux_test.go -->
# sources/cloud-native/containers-storage/pkg/chunked/compression_linux_test.go

Purpose: tests tar-split size accounting and temporary file unlink behavior for chunked compression helpers.

Important APIs/types/functions: `TestTarSizeFromTarSplit` and `TestOpenTmpFile`.

Control flow: `TestTarSizeFromTarSplit` writes fixture tar entries, records actual tarball length, runs tar-split packing, and asserts `tarSizeFromTarSplit` reconstructs the same size. `TestOpenTmpFile` repeatedly opens temp files through both `openTmpFile` and fallback `openTmpFileNoTmpFile`, checks `/proc/self/fd/<fd>` contains `(deleted)`, and closes files.

State/persistence: temporary tar buffers and temp directory files that are unlinked immediately.

Dependencies/integration: uses tar-split `asm.NewInputTarStream`, `storage.NewJSONPacker`, and Linux `/proc/self/fd`.

Risks/test signal: protects the invariant that tar-split can be used to calculate layer tar size and that temporary tar-split data is not left visible on disk.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/chunked/compression_linux_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/chunked/compressor/compressor.go -->
# sources/cloud-native/containers-storage/pkg/chunked/compressor/compressor.go

Purpose: implements zstd:chunked tar stream creation with per-file/per-chunk offsets, digests, hole detection, rolling checksums, tar-split metadata, and final manifest frames.

Important APIs/types/functions: constants `RollsumBits` and `holesThreshold`; `holesFinder`; `rollingChecksumReader`; `chunk`; `tarSplitData`; `newTarSplitData`; `writeZstdChunkedStream`; `zstdChunkedWriter`; `makeZstdChunkedWriter`; `ZstdCompressor`; `noCompression`; `NoCompression`.

Control flow: `makeZstdChunkedWriter` returns a pipe-backed writer and runs `writeZstdChunkedStream` in a goroutine. The stream writer wraps the tar input with tar-split packer, writes raw tar headers, restarts zstd at file payload boundaries and content-defined chunk boundaries, tracks chunk compressed offsets, computes payload and chunk digests, treats long zero runs as hole chunks, builds `minimal.FileMetadata` entries, appends remaining tar bytes, closes zstd writers, packages compressed tar-split data, and calls `minimal.WriteZstdChunkedManifest`. `ZstdCompressor` defaults level 10. `NoCompression` uses a resettable writer shim for internal conversion paths.

State/persistence: writes compressed output and metadata annotations to caller-provided writer/metadata map. Maintains in-memory tar-split compressed bytes and metadata slice.

Dependencies/integration: intentionally avoids graphdriver dependencies because containers/image imports it. Uses minimal chunked metadata, `ioutils.WriteCounter`, OCI digests, tar-split, zstd writer factory, and `RollSum`.

Risks: streaming/goroutine errors must propagate through pipe reads/writes; incorrect restart offsets or chunk digests break random access. `holesFinder` and rolling checksum boundaries affect dedup efficiency and sparse-zero representation. `NoCompression` output is intentionally not generally zstd:chunked compliant.

Test signals: `compressor_test.go` covers hole detection and no-compression writer behavior; rollsum tests validate checksum invariants. Broader chunked tests outside this subset verify generated manifest parsing.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/chunked/compressor/compressor.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/chunked/compressor/compressor_test.go -->
# sources/cloud-native/containers-storage/pkg/chunked/compressor/compressor_test.go

Purpose: tests hole detection state machine and no-compression writer shim.

Important APIs/types/functions: `TestHole`, `TestTwoHoles`, `TestNoCompressionWrite`, `TestNoCompressionClose`, `TestNoCompressionFlush`, `TestNoCompressionReset`, `errorWriter`, and `TestNoCompressionWriteError`.

Control flow: hole tests feed zero and mixed zero/nonzero byte streams into `holesFinder` with different thresholds and assert whether holes are coalesced or raw zeros are returned. No-compression tests verify writes append to destination, close/flush are nil, reset switches destinations, nil reset is allowed, and write errors propagate.

State/persistence: in-memory buffers only.

Dependencies/integration: directly exercises internal compressor helpers used by `writeZstdChunkedStream`.

Risks/test signal: protects sparse-zero chunk recognition and internal conversion writer behavior. It does not fully stream-test zstd:chunked manifest output.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/chunked/compressor/compressor_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/chunked/compressor/rollsum.go -->
# sources/cloud-native/containers-storage/pkg/chunked/compressor/rollsum.go

Purpose: rolling checksum implementation used for content-defined chunk splitting in zstd:chunked compression.

Important APIs/types/functions: constants `windowSize`, `charOffset`, `blobBits`, `blobSize`; type `RollSum`; functions `NewRollSum`, `add`, `Roll`, `OnSplit`, `OnSplitWithBits`, `Bits`, and `Digest`.

Control flow: `NewRollSum` initializes sums as if the 64-byte window were filled with offset bytes. `Roll` replaces the next ring-buffer byte, updates `s1` and `s2`, and advances the window offset. `OnSplit` and `OnSplitWithBits` test low checksum bits for split boundaries. `Bits` estimates split strength from trailing zeros in the inverted digest-derived value. `Digest` combines `s1` and low `s2`.

State/persistence: in-memory rolling window and sums only.

Dependencies/integration: used by `rollingChecksumReader` in `compressor.go` to decide chunk boundaries; derived from Perkeep/bup-style rolling checksum code.

Risks: split distribution directly affects chunk sizes, deduplication, and compression seekability. `windowSize` must remain a power of two because ring advancement uses bit masking.

Test signals: `rollsum_test.go` verifies rolling digest invariance across shifted windows and includes a benchmark.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/chunked/compressor/rollsum.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/chunked/compressor/rollsum_test.go -->
# sources/cloud-native/containers-storage/pkg/chunked/compressor/rollsum_test.go

Purpose: validates rolling checksum invariants and benchmarks split scanning.

Important APIs/types/functions: `TestSum` and `BenchmarkRollsum`.

Control flow: `TestSum` fills a deterministic random buffer, compares checksum results for windows that should be equivalent after roll-in/roll-out behavior, then walks 500 positions comparing incrementally rolled digest with freshly computed digest. The benchmark scans a 5 MiB buffer, calls `Roll`, checks `OnSplit`, and logs split frequency.

State/persistence: in-memory random buffers only.

Dependencies/integration: exercises `NewRollSum`, `Roll`, `Digest`, `OnSplit`, and `Bits`.

Risks/test signal: guards the checksum ring-buffer math. Benchmark output is informational and does not enforce chunk-size distribution.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/chunked/compressor/rollsum_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/chunked/dump/dump.go -->
# sources/cloud-native/containers-storage/pkg/chunked/dump/dump.go

Purpose: generates a composefs-info-compatible textual dump from a chunked minimal TOC.

Important APIs/types/functions: escape flags `ESCAPE_STANDARD`, `NOESCAPE_SPACE`, `ESCAPE_EQUAL`, `ESCAPE_LONE_DASH`; helpers `escaped`, `escapedOptional`, `getStMode`, `dumpNode`; public `GenerateDump`.

Control flow: escaping converts non-printable/non-graph bytes, backslash, newline, tab, carriage return, optional equals, spaces, and lone dash into expected textual forms. `dumpNode` normalizes paths, recursively synthesizes missing parent directories, de-duplicates identical entries, writes path, size, mode/type, link count, UID/GID, rdev, timestamp, payload path/link target, inline placeholder, verity digest, and decoded xattrs. `GenerateDump` type-checks TOC, starts a pipe goroutine, computes hardlink counts, emits a root entry for empty TOCs, skips chunk entries, and dumps all non-chunk entries.

State/persistence: streaming in-memory output through an `io.Pipe`; no filesystem writes.

Dependencies/integration: uses minimal TOC metadata, chunked internal path helpers, OCI digest validation, base64 xattr decoding, Unix mode bits, and optional verity digest map.

Risks: output must match composefs expectations exactly. Duplicate path mismatch is an error. Xattrs must be valid base64. Missing-parent synthesis can introduce inferred directories with default mode/time.

Test signals: `dump_test.go` covers escaping, duplicate entries, files, dirs, symlinks, hardlinks, missing parents, xattrs, and expected line formatting.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/chunked/dump/dump.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/chunked/dump/dump_test.go -->
# sources/cloud-native/containers-storage/pkg/chunked/dump/dump_test.go

Purpose: tests composefs dump escaping and node formatting.

Important APIs/types/functions: `TestEscaped` and `TestDumpNode`.

Control flow: `TestEscaped` checks plain strings, control characters, backslashes, equals escaping, lone dash escaping, space handling, and UTF-8 bytes rendered as hex escapes. `TestDumpNode` builds metadata for root, regular file, duplicate roots, directory, symlink, hardlink, and missing-parent cases, then calls `dumpNode` and compares exact output or expected errors.

State/persistence: in-memory buffers only.

Dependencies/integration: exercises `escaped`, `dumpNode`, base64 xattr decoding, digest-to-physical path conversion, and Unix mode formatting.

Risks/test signal: exact-string assertions protect format compatibility but may be brittle to intentional formatting changes. Tests do not cover full `GenerateDump` pipe error propagation.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/chunked/dump/dump_test.go -->
