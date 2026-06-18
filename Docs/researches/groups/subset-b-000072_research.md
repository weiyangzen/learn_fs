# subset-b-000072 Research

This grouped report covers the assigned containerd package files. Each section is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/archive/compression/compression_test.go -->
# sources/cloud-native/containerd/pkg/archive/compression/compression_test.go

Purpose: test coverage for the archive compression package, especially gzip, optional pigz/unpigz integration, uncompressed pass-through behavior, command-backed streams, and zstd magic detection.

Important APIs and functions: `TestMain` forces gzip decompressor initialization before tests; `generateData`, `testCompress`, `testDecompress`, and `testCompressDecompress` are reusable helpers around `CompressStream`, `DecompressStream`, and `DetectCompression`. The test cases exercise `Compression` values `Gzip`, `Uncompressed`, and `Zstd`, plus internals `gzipPath`, `detectCommand`, `disablePigzEnv`, and `cmdStream`.

Control flow and state: tests generate a mixed random/zero/random byte buffer, compress it, assert compressed bytes are changed when appropriate, then read all decompressed output and compare with the original. Pigz tests temporarily mutate global `gzipPath` or fake `PATH`, and use `t.Setenv`/defers to restore state. `cmdStream` tests verify stdout forwarding and stderr-included error propagation.

Dependencies and integration: depends on the compression implementation in the same package, standard `compress/gzip`, `os/exec`, and platform PATH handling. It is an integration signal for external `unpigz`; if absent, the pigz path test is skipped.

Risks and test signals: randomness may hide pathological content but verifies large data paths. The fake PATH test guards environment disable handling. `TestDetectCompressionZstd` explicitly covers normal and skippable zstd frames, which is important for OCI artifacts that may contain leading skippable metadata.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/archive/compression/compression_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/archive/issues_test.go -->
# sources/cloud-native/containerd/pkg/archive/issues_test.go

Purpose: regression test for reading tar archives emitted by old Go/containerd combinations using prefix headers, preserving backward compatibility for stored layers.

Important APIs and functions: `TestPrefixHeaderReadable` constructs a known gzipped tar byte sequence, decompresses it with `compression.DecompressStream`, applies it with `Apply(..., WithNoSameOwner())`, and verifies the expected long path exists.

Control flow and state: the test requires root, creates a temp extraction root, streams a static gzip payload into the archive apply path, and checks `os.Lstat` on a path derived from a long prefix/name split.

Dependencies and integration: integrates `pkg/archive/compression` with the core tar `Apply` flow and the test utility root guard. It indirectly verifies `archive/tar` compatibility with historic prefix encoding.

Risks and test signals: the static fixture is small but critical because failures would mean older content in registries or content stores can no longer be unpacked. `WithNoSameOwner` narrows the test to format readability rather than UID/GID preservation.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/archive/issues_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/archive/link_default.go -->
# sources/cloud-native/containerd/pkg/archive/link_default.go

Purpose: default hard-link implementation for all non-FreeBSD builds.

Important APIs and functions: `link(oldname, newname string) error` is a thin wrapper around `os.Link`.

Control flow and state: no persistent state; it delegates directly to the host filesystem and returns the syscall error unchanged.

Dependencies and integration: used by `createTarFile` in `tar.go` when applying tar `TypeLink` entries after resolving the link target with `hardlinkRootPath`.

Risks and test signals: behavior inherits platform `os.Link` semantics. FreeBSD has a separate implementation because containerd needs different link handling there; common hardlink and breakout behavior is covered by `tar_test.go`.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/archive/link_default.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/archive/link_freebsd.go -->
# sources/cloud-native/containerd/pkg/archive/link_freebsd.go

Purpose: FreeBSD-specific hard-link implementation that avoids unsupported cross-device or special-case behavior by delegating through containerd sys helpers and Unix flags.

Important APIs and functions: `link(oldname, newname string) error` calls `sys.Link(oldname, newname, unix.AT_SYMLINK_FOLLOW)`.

Control flow and state: stateless wrapper. The important behavior is that symlink-following semantics are explicit through `AT_SYMLINK_FOLLOW`.

Dependencies and integration: integrates `github.com/containerd/containerd/v2/pkg/sys` and `golang.org/x/sys/unix` into the archive apply flow for tar hardlinks.

Risks and test signals: hardlink security is sensitive because tar linknames may attempt to escape extraction roots. Root bounding is handled in `tar.go` before this function is called; platform-specific link following should be validated with FreeBSD CI.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/archive/link_freebsd.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/archive/tar.go -->
# sources/cloud-native/containerd/pkg/archive/tar.go

Purpose: core OCI diff tar implementation for containerd. It can generate a tar stream representing filesystem changes and apply an OCI-style diff tar to a root directory, including whiteouts, hardlinks, special files, xattrs, ownership, permissions, and reproducible timestamps.

Important APIs and types: exported entry points are `Diff`, `WriteDiff`, `Apply`, `ChangeWriter`, `ChangeWriterOpt`, `WithModTimeUpperBound`, and `NewChangeWriter`. Important helpers include `writeDiffNaive`, `applyNaive`, `createTarFile`, `mkparent`, `copyBuffered`, `hardlinkRootPath`, and `validateWhiteout`. Constants define OCI/AUFS whiteout names and PAX xattr prefixes.

Control flow: `Diff` starts a goroutine with an `io.Pipe`; `WriteDiff` resolves options, honors `epoch.FromContext`, and defaults to `writeDiffNaive`. `writeDiffNaive` uses continuity `fs.Changes` to feed a `ChangeWriter`. `Apply` cleans the root, applies options/defaults, and defaults to `applyNaive`. `applyNaive` iterates tar headers, normalizes names, filters entries, skips unsupported platform files, bounds parent paths via `fs.RootPath`, creates missing parents, validates/converts whiteouts, removes conflicting destinations, creates the file, records unpacked paths, and restores directory mtimes at the end.

State and persistence: persistent effects are filesystem mutations under the extraction root, deletion of whiteouted paths, xattr writes, chmod/chown/chtimes, hardlink creation, and optional inherited parent metadata from `Parents`. `ChangeWriter` tracks inode sources/references to emit hardlinks, `addedDirs` to include required parent directories once, and optional mod-time upper bound for reproducible output. `bufPool` reuses 32 KiB copy buffers.

Dependencies and integration: relies on Go `archive/tar`, containerd `tarheader`, `epoch`, `continuity/fs`, logging, and platform hooks supplied by `tar_unix.go`, `tar_windows.go`, `tar_mostunix.go`, `tar_freebsd.go`, and option files. It implements OCI layer whiteout conventions and integrates with snapshotter diff/apply paths.

Risks and test signals: the main risk surface is path traversal through symlinks/hardlinks and destructive whiteout handling. The code uses `fs.RootPath`, root checks, `hardlinkRootPath`, and `validateWhiteout`, but comments/tests note some symlink-parent behavior is still compatibility-sensitive. `tar_test.go` heavily tests breakouts, hardlink ordering, xattrs, directory mtimes, whiteouts, sockets, and source date reproducibility.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/archive/tar.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/archive/tar_freebsd.go -->
# sources/cloud-native/containerd/pkg/archive/tar_freebsd.go

Purpose: FreeBSD-specific archive syscall helpers for node creation, xattr creation, and symlink-aware chmod.

Important APIs and functions: `mknod` calls FreeBSD's `unix.Mknod` signature with a `uint64` device; `lsetxattrCreate` calls `unix.Lsetxattr` without `XATTR_CREATE` and ignores unsupported/existing errors; `lchmod` uses `unix.Fchmodat(..., AT_SYMLINK_NOFOLLOW)`.

Control flow and state: no long-lived state. Each helper performs one filesystem syscall and adapts FreeBSD-specific signatures/errors to the generic archive flow.

Dependencies and integration: consumed by `tar_unix.go` and `tar.go` for special file extraction, parent xattr copy-up, and final mode restoration.

Risks and test signals: correctness depends on FreeBSD syscall semantics, especially symlink no-follow behavior and xattr error compatibility. Cross-platform tests may not exercise this unless FreeBSD CI is present.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/archive/tar_freebsd.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/archive/tar_linux_test.go -->
# sources/cloud-native/containerd/pkg/archive/tar_linux_test.go

Purpose: Linux-only integration tests for applying generated diffs as overlay lower layers and converting OCI whiteouts to overlayfs semantics.

Important APIs and types: `TestOverlayApply`, `TestOverlayApplyNoParents`, `overlayDiffApplier`, `overlayContext`, and its `TestContext`/`Apply` methods. The tests exercise `WriteDiff`, `NewChangeWriter`, `Apply`, `WithConvertWhiteout(OverlayConvertWhiteout)`, and `WithParents`.

Control flow and state: tests require root and overlayfs support. Each FSSuite change is applied to a copy, diffed against the current lower/merged state, applied into a new lower directory, and then optionally mounted as an overlay stack. `oc.lowers` grows with each applied diff, and mounted state is unmounted between iterations.

Dependencies and integration: integrates containerd `core/mount`, overlay snapshotter support checks, continuity `fs/fstest`, and archive overlay whiteout conversion.

Risks and test signals: validates parent directory attribute inheritance with and without explicit parent inclusion. It also covers real overlay mount behavior, so it catches issues not visible in plain directory comparison, but it is gated by root and kernel overlay support.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/archive/tar_linux_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/archive/tar_mostunix.go -->
# sources/cloud-native/containerd/pkg/archive/tar_mostunix.go

Purpose: Unix helper implementation for non-Windows, non-FreeBSD platforms.

Important APIs and functions: `mknod`, `lsetxattrCreate`, and `lchmod`. `mknod` adapts `unix.Mknod` device type to `int`; `lsetxattrCreate` uses `XATTR_CREATE` and treats unsupported/no-data/existing as ignorable; `lchmod` skips symlinks and chmods regular paths.

Control flow and state: stateless wrappers around Unix filesystem syscalls.

Dependencies and integration: supplies functions called from `tar_unix.go` for special files, xattr copy-up, and final archive mode application.

Risks and test signals: skipping chmod for symlinks avoids following links during extraction. The xattr function deliberately ignores already-existing attrs during parent copy-up, preventing parent metadata copy from overwriting newly created attributes.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/archive/tar_mostunix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/archive/tar_opts.go -->
# sources/cloud-native/containerd/pkg/archive/tar_opts.go

Purpose: option and callback definitions for archive apply and diff operations.

Important APIs and types: `ApplyOptions`, `ApplyOpt`, `Filter`, `ConvertWhiteout`, `WithFilter`, `WithConvertWhiteout`, `WithNoSameOwner`, `WithParents`, `WriteDiffOptions`, `WriteDiffOpt`, and `WithSourceDateEpoch`.

Control flow and state: option functions mutate option structs before `Apply` or `WriteDiff` run. `ApplyOptions` can override filtering, whiteout conversion, parent metadata lookup, ownership preservation, and the apply implementation. `WriteDiffOptions` can set parent layers, implementation override, and source date epoch.

Dependencies and integration: the option structs are consumed by `tar.go`; platform-specific option files add Linux overlay and Windows layer variants.

Risks and test signals: options can significantly change destructive behavior, particularly custom whiteout conversion and custom apply/diff functions. Tests cover filters implicitly through apply paths and source-date behavior through `TestSourceDateEpoch`.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/archive/tar_opts.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/archive/tar_opts_linux.go -->
# sources/cloud-native/containerd/pkg/archive/tar_opts_linux.go

Purpose: Linux-specific whiteout conversion for overlayfs-backed layers.

Important APIs and functions: `OverlayConvertWhiteout(hdr, path) (bool, error)` converts OCI/AUFS whiteouts to overlayfs representations.

Control flow and state: opaque directory marker `.wh..wh..opq` becomes `trusted.overlay.opaque=y` on the directory and is not written as a file. Per-file `.wh.<name>` becomes a character device at the target path via `unix.Mknod(..., S_IFCHR, 0)` followed by `os.Chown`, and the whiteout file itself is suppressed. Non-whiteout entries return `true`.

Dependencies and integration: used by callers passing `WithConvertWhiteout(OverlayConvertWhiteout)` to `Apply`, especially overlay snapshotter tests and layer application.

Risks and test signals: requires privileges for trusted xattrs, mknod, and chown; tests in `tar_linux_test.go` require root and overlayfs support. Incorrect conversion would make overlay lowerdir deletion semantics wrong.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/archive/tar_opts_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/archive/tar_opts_windows.go -->
# sources/cloud-native/containerd/pkg/archive/tar_opts_windows.go

Purpose: Windows container layer apply/diff option support using hcsshim/ociwclayer.

Important APIs and functions: `applyWindowsLayer`, `AsWindowsContainerLayer`, `writeDiffWindowsLayers`, `AsWindowsContainerLayerPair`, and `WithParentLayers`.

Control flow and state: applying a Windows layer wraps `ociwclayer.ImportLayerFromTar` in `winio.RunWithPrivileges` for `SeSecurityPrivilege`; diffing delegates to `ociwclayer.ExportLayerToTar` with configured parent layers. The option functions install these platform-specific implementations into `ApplyOptions` or `WriteDiffOptions`.

Dependencies and integration: integrates Microsoft `go-winio` and `hcsshim/pkg/ociwclayer`. It is the Windows counterpart to generic Unix directory diff/apply.

Risks and test signals: callers must hold backup/restore privileges as documented, and path/layer semantics are delegated to hcsshim. Failures often depend on Windows privilege state and storage location, so CI needs Windows coverage.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/archive/tar_opts_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/archive/tar_test.go -->
# sources/cloud-native/containerd/pkg/archive/tar_test.go

Purpose: main non-Windows archive test suite for diff/apply correctness, security-sensitive path handling, whiteout semantics, hardlinks, xattrs, directory creation, source-date reproducibility, and integration with system `tar`.

Important APIs and functions: top-level tests include `TestUnpack`, `TestBaseDiff`, `TestRelativeSymlinks`, `TestSymlinks`, `TestTarWithXattr`, `TestBreakouts`, `TestDiffApply`, `TestApplyTar`, `TestDiffTar`, and `TestSourceDateEpoch`. Helpers include `testApply`, `testBaseDiff`, `testDiffApply`, `makeWriterToTarTest`, `makeDiffTarTest`, validators for tar entries, `diffApplier`, and `requireTar`.

Control flow and state: tests build synthetic filesystems with `continuity/fs/fstest`, produce tar streams either through system `tar`, `Diff`, or `tartest`, apply them into temp dirs, and compare with expected filesystem state or tar-entry validators. Security cases intentionally create symlinks/hardlinks with absolute, relative, parent, empty, and replacement paths to check root bounding.

Dependencies and integration: integrates archive code with continuity test fixtures, system `tar`, `go-digest`, root-only xattr checks, and the tartest tar-stream builder.

Risks and test signals: the suite is the strongest signal for archive regressions. It validates invalid whiteout names return `errInvalidArchive`, sockets are ignored, hardlink parent inclusion is deterministic, source-date mtimes are capped while whiteouts remain Unix epoch, and repeated diff generation has stable digests outside short mode.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/archive/tar_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/archive/tar_unix.go -->
# sources/cloud-native/containerd/pkg/archive/tar_unix.go

Purpose: non-Windows filesystem operations for tar extraction and creation: permissions, device headers, secure file opening, special files, xattrs, and parent metadata copy-up.

Important APIs and functions: `chmodTarEntry`, `setHeaderForSpecialDevice`, `open`, `openFile`, `mkdir`, `skipFile`, `handleTarTypeBlockCharFifo`, `getxattr`, `setxattr`, `copyDirInfo`, and `copyUpXAttrs`.

Control flow and state: regular files are opened then explicitly chmodded to bypass umask; directories are created then chmodded. Special tar entries become `mknod` calls unless user namespaces require skipping block/char devices. Xattrs are read/written with lget/lset behavior, trusted attrs are rejected or skipped, and parent copy-up preserves chown/chmod/timestamps/xattrs from lower parents.

Dependencies and integration: relies on `golang.org/x/sys/unix`, `moby/sys/userns`, `continuity/fs` and `continuity/sysx`. It supplies platform hooks used by `tar.go`.

Risks and test signals: root/user namespace behavior, xattr namespaces, NFS permission errors, and symlink no-follow timestamp/chmod behavior are sensitive. `tar_test.go` and Linux overlay tests cover many cases; platform-specific files cover FreeBSD differences.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/archive/tar_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/archive/tar_windows.go -->
# sources/cloud-native/containerd/pkg/archive/tar_windows.go

Purpose: Windows implementation of archive filesystem hooks for generic tar apply/diff.

Important APIs and functions: `chmodTarEntry`, `setHeaderForSpecialDevice`, `open`, `openFile`, `mkdir`, `skipFile`, `handleTarTypeBlockCharFifo`, `lchmod`, `getxattr`, `setxattr`, `copyDirInfo`, and `copyUpXAttrs`.

Control flow and state: permissions are masked to 0755 and execute bits are added; file opens use `moby/sys/sequential` to avoid standby-list pressure; colon-containing filenames are skipped; special devices, lchmod, xattrs, and xattr copy-up are no-ops or unsupported.

Dependencies and integration: used by `tar.go` on Windows for non-hcsshim generic tar paths. Windows container layer-specific behavior is in `tar_opts_windows.go`.

Risks and test signals: skipping colon names is a compatibility compromise for pulling Linux images during development. Xattrs from archives fail as unsupported, so Windows archives should not contain them. Windows-specific tests are mostly in IO/log URI files, not archive extraction.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/archive/tar_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/archive/tarheader/tarheader.go -->
# sources/cloud-native/containerd/pkg/archive/tarheader/tarheader.go

Purpose: create tar headers from `os.FileInfo` without OS user/group lookups, making header generation safe in chrooted or restricted contexts.

Important APIs and types: `nosysFileInfo`, package variable `sysStat`, and exported `FileInfoHeaderNoLookups(fi, link)`.

Control flow and state: `nosysFileInfo.Sys` hides native `Sys` data unless it is already a `*tar.Header`. `FileInfoHeaderNoLookups` calls `tar.FileInfoHeader` with the wrapper, then optionally invokes `sysStat` to populate safe system-dependent fields.

Dependencies and integration: used by `ChangeWriter.HandleChange` in `archive/tar.go` to avoid propagating host user/group names into layer tars.

Risks and test signals: Uname/Gname are intentionally absent; callers needing atime/ctime must handle them explicitly. Unix population is installed by `tarheader_unix.go`.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/archive/tarheader/tarheader.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/archive/tarheader/tarheader_unix.go -->
# sources/cloud-native/containerd/pkg/archive/tarheader/tarheader_unix.go

Purpose: Unix system metadata population for lookup-free tar headers.

Important APIs and functions: `init` assigns `sysStat = statUnix`; `statUnix` copies UID/GID and special-device major/minor numbers from `syscall.Stat_t`.

Control flow and state: on Unix, every `FileInfoHeaderNoLookups` call can receive UID/GID and device metadata. FreeBSD regular-file `Rdev == -1` is intentionally ignored unless the header is block/char.

Dependencies and integration: depends on `syscall.Stat_t` and `x/sys/unix`. Used by archive diff tar generation for ownership and device entries.

Risks and test signals: incorrect major/minor extraction breaks special device layer entries. FreeBSD behavior prevents unencodable large device numbers in regular file headers.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/archive/tarheader/tarheader_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/archive/tartest/tar.go -->
# sources/cloud-native/containerd/pkg/archive/tartest/tar.go

Purpose: test helper package for programmatically constructing tar streams with controlled entries, ownership, mtimes, links, symlinks, and xattrs.

Important APIs and types: `WriterToTar`, `TarAll`, `TarFromWriterTo`, `TarContext`, `WithUIDGID`, `WithModTime`, `WithXattrs`, `File`, `Dir`, `Symlink`, `Link`, and `writeHeaderAndContent`.

Control flow and state: `TarFromWriterTo` uses an `io.Pipe` and goroutine to stream tar records. `TarContext` is immutable-by-copy for UID/GID/mtime, but `WithXattrs` mutates or shares the map on the copied context, so callers should treat returned contexts as the owner of the xattr map.

Dependencies and integration: used heavily by `archive/tar_test.go` to manufacture edge-case tar entries that system `tar` would not easily produce.

Risks and test signals: panics on impossible `tar.FileInfoHeader` errors, which is acceptable for test fixtures. It validates content length before writing to catch inconsistent test setup.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/archive/tartest/tar.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/archive/time.go -->
# sources/cloud-native/containerd/pkg/archive/time.go

Purpose: common time helpers for archive extraction timestamp restoration.

Important APIs and functions: `boundTime`, `latestTime`, and platform hook `chtimes`.

Control flow and state: `latestTime` chooses the newer of two `time.Time` values for access-time restoration; `boundTime` likely clamps out-of-range times for syscall compatibility before `chtimes` applies them.

Dependencies and integration: called from `createTarFile` and delayed directory mtime restoration in `tar.go`. Platform files implement the actual timestamp syscall.

Risks and test signals: timestamp bounds are important for old dates, zero times, and platform-specific syscall ranges. Source-date behavior is tested in `tar_test.go`.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/archive/time.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/archive/time_unix.go -->
# sources/cloud-native/containerd/pkg/archive/time_unix.go

Purpose: Unix implementation of archive timestamp application.

Important APIs and functions: `chtimes(path string, atime, mtime time.Time) error` uses nanosecond timespecs and no-follow semantics where available.

Control flow and state: converts Go times into Unix syscall structures and updates timestamps on the target path as part of extraction.

Dependencies and integration: used by `tar.go` after file creation and again after all directory children are unpacked.

Risks and test signals: symlink and directory mtime behavior can differ by OS; delayed directory updates in `tar.go` are the main integration safeguard.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/archive/time_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/archive/time_windows.go -->
# sources/cloud-native/containerd/pkg/archive/time_windows.go

Purpose: Windows timestamp application for extracted archive entries.

Important APIs and functions: Windows `chtimes` adapts `time.Time` values to Windows file time operations through `x/sys/windows`.

Control flow and state: opens the path with `FILE_WRITE_ATTRIBUTES`, `FILE_SHARE_WRITE`, `OPEN_EXISTING`, and `FILE_FLAG_BACKUP_SEMANTICS`, converts `mtime` to Windows filetime, and calls `SetFileTime` with that value as the creation time. The `atime` parameter is accepted to satisfy the shared hook but is not applied.

Dependencies and integration: called from the same `tar.go` extraction points as Unix `chtimes`, but uses Windows APIs and path semantics.

Risks and test signals: Windows timestamp precision/range differs from Unix. Generic archive tests are build-tagged away on Windows, so Windows CI should cover layer operations separately.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/archive/time_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/atomicfile/file.go -->
# sources/cloud-native/containerd/pkg/atomicfile/file.go

Purpose: provide an `io.ReadWriteCloser` that writes through a temporary file and atomically publishes changes by syncing, closing, and renaming over the target.

Important APIs and types: `File` interface, `ErrClosed`, `New`, `atomicFile`, `Close`, `Cancel`, `Read`, and `Write`.

Control flow and state: `newFile` creates a temp file in the destination directory and chmods it. `Close` is idempotent under a mutex, syncs, closes, renames, and removes the temp file on error. `Cancel` closes/removes without publishing. `Read`/`Write` hold an RW lock and return `ErrClosed` after close/cancel.

Dependencies and integration: uses only standard `os`, `filepath`, `sync`, and `io`. Intended for config/state files that need readers to see either old or new contents.

Risks and test signals: Windows rename is documented as not fully atomic. Directory fsync is not performed, so rename durability across power loss may depend on filesystem behavior. Tests cover single write and sequential concurrent writers.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/atomicfile/file.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/atomicfile/file_test.go -->
# sources/cloud-native/containerd/pkg/atomicfile/file_test.go

Purpose: validate atomicfile publish behavior for normal and concurrent writers.

Important APIs and functions: `TestFile` and `TestConcurrentWrites` exercise `New`, `Write` through `fmt.Fprint`, `Close`, and reading the destination path.

Control flow and state: tests create temp dirs, open one or two atomic writers to the same final path, write different contents, close in a controlled order, and assert the visible file contents after each close.

Dependencies and integration: uses testify assertions and standard filesystem operations.

Risks and test signals: confirms last closer wins without partial content. It does not test `Cancel`, post-close `ErrClosed`, sync/rename failure cleanup, or concurrent goroutine races during `Write`.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/atomicfile/file_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/blockio/blockio_linux.go -->
# sources/cloud-native/containerd/pkg/blockio/blockio_linux.go

Purpose: Linux integration wrapper around Intel goresctrl block I/O classes for containerd.

Important APIs and functions: `IsEnabled`, `SetConfig`, `ClassNameToLinuxOCI`, and `ContainerClassFromAnnotations`. Package globals include `config` and `configMu`.

Control flow and state: `SetConfig` parses a blockio config file via goresctrl, logs class names, and stores it under a mutex. `IsEnabled` checks whether config is non-nil. `ClassNameToLinuxOCI` translates a class to OCI `LinuxBlockIO`; `ContainerClassFromAnnotations` chooses class name from container/pod annotations using goresctrl rules.

Dependencies and integration: depends on `github.com/intel/goresctrl/pkg/blockio`, OCI runtime spec types, and containerd logging. It feeds runtime spec blockio settings.

Risks and test signals: global mutable config affects all callers and needs synchronization. Config parsing and annotation policy are delegated to goresctrl; failures should surface early during daemon config load.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/blockio/blockio_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/blockio/blockio_nonlinux.go -->
# sources/cloud-native/containerd/pkg/blockio/blockio_nonlinux.go

Purpose: non-Linux stub for block I/O support.

Important APIs and functions: `IsEnabled` always false, `SetConfig` no-op, `ClassNameToLinuxOCI` returns nil, and `ContainerClassFromAnnotations` returns empty class.

Control flow and state: no state and no filesystem/config effects.

Dependencies and integration: keeps package API portable for callers that compile on non-Linux platforms while returning no Linux OCI blockio configuration.

Risks and test signals: callers must handle nil/empty results. This intentionally hides unsupported functionality rather than failing on non-Linux builds.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/blockio/blockio_nonlinux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/cap/cap_linux.go -->
# sources/cloud-native/containerd/pkg/cap/cap_linux.go

Purpose: Linux capability utilities for decoding kernel capability bitmaps and reading the current process capabilities from `/proc`.

Important APIs and types: `FromNumber`, `FromBitmap`, `Type` constants (`Inheritable`, `Permitted`, `Effective`, `Bounding`, `Ambient`), `ParseProcPIDStatus`, `Current`, `Known`, and capability lists by kernel vintage.

Control flow and state: `ParseProcPIDStatus` scans `/proc/<pid>/status`, recognizes `Cap*` fields, parses hex bitmaps, and returns a map by `Type`. `Current` reads `/proc/self/status`, decodes effective capabilities, and returns known names. `FromBitmap` iterates set bits, separates known capability names from unknown numbers, and masks only the latest known list.

Dependencies and integration: standard `bufio`, `io`, `os`, `strconv`, and capability knowledge embedded as static slices. Used by code that needs diagnostic or runtime capability reporting.

Risks and test signals: `Known` is fixed to kernel 5.9 capability names, so newer kernels can appear as unknown bits until updated. Fuzz tests cover proc-status parsing shape.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/cap/cap_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/cap/cap_linux_test.go -->
# sources/cloud-native/containerd/pkg/cap/cap_linux_test.go

Purpose: tests and fuzzing for Linux capability name/bitmap/proc-status parsing.

Important APIs and functions: `TestCapsList`, `TestFromNumber`, `TestFromBitmap`, `TestParseProcPIDStatus`, `TestCurrent`, `TestKnown`, and `FuzzParseProcPIDStatus`.

Control flow and state: table tests verify capability list lengths and bitmap decoding across kernel capability vintages. A fixture `/proc/<pid>/status` string validates parsed `CapInh`, `CapPrm`, `CapEff`, `CapBnd`, and `CapAmb` values. `TestCurrent` reads live `/proc/self/status`.

Dependencies and integration: uses testify assertions and the real procfs for current process coverage.

Risks and test signals: live `TestCurrent` depends on Linux procfs availability. Fuzzing asserts parser never returns both a non-nil result and error for arbitrary inputs.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/cap/cap_linux_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/cdi/oci_opt.go -->
# sources/cloud-native/containerd/pkg/cdi/oci_opt.go

Purpose: provide an OCI spec option that injects requested CDI devices into a container spec.

Important APIs and functions: `WithCDIDevices(devices ...string)` returns an `oci.SpecOpts` closure. It refreshes the CDI registry and calls `cdi.InjectDevices` against the OCI spec.

Control flow and state: if no devices are requested it returns without changes. Otherwise it calls `cdi.Refresh`; refresh failures are logged as warnings but not fatal, because CDI injection can still decide whether requested devices are usable. Injection failures are wrapped and returned. There is no package-local persistent state.

Dependencies and integration: integrates `core/containers`, `pkg/oci`, containerd logging, and CDI registry behavior. It is part of container creation spec assembly.

Risks and test signals: injection can add environment variables, hooks, and mounts, so later spec options must not reset those fields. Correctness depends on CDI registry availability and caller-provided device names.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/cdi/oci_opt.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/cio/io.go -->
# sources/cloud-native/containerd/pkg/cio/io.go

Purpose: shared container IO abstractions and helpers for creating, attaching, logging, loading, and closing task standard streams.

Important APIs and types: `Config`, `IO`, `Creator`, `Attach`, `FIFOSet`, `Streams`, options `WithStdio`, `WithTerminal`, `WithStreams`, `WithFIFODir`, `NewCreator`, `NewAttach`, `NullIO`, `DirectIO`, `LogURI`, `BinaryIO`, `LogFile`, `LogURIGenerator`, `Load`, and `pipes`.

Control flow and state: `NewCreator` materializes FIFO/named-pipe paths then delegates to platform `copyIO`; absent user streams clear corresponding FIFO paths. `NewAttach` reuses an existing `FIFOSet`. `cio` tracks config, copy waitgroup, closers, and cancel function. `Close` joins closer errors; `Cancel` aborts active operations. Log URI creators return lightweight `logURI` instances without copy goroutines.

Dependencies and integration: used by task/process creation and attach flows. Depends on defaults for FIFO directory, URL/path encoding, and platform files for actual FIFO/named pipe behavior.

Risks and test signals: only one reader should attach to FIFO output. `LogURIGenerator` requires absolute paths and handles Windows drive URI details. Tests cover URI generation and platform FIFO behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/cio/io.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/cio/io_test.go -->
# sources/cloud-native/containerd/pkg/cio/io_test.go

Purpose: platform-neutral tests for logging URI creator behavior.

Important APIs and functions: tests cover `BinaryIO`, `LogFile`, `LogURIGenerator`, and path handling with Windows/non-Windows prefixes.

Control flow and state: tests build creators with absolute and relative paths, call them with dummy IDs, compare stdout/stderr config strings, and parse generated URLs to validate scheme/path/query encoding.

Dependencies and integration: uses `runtime.GOOS` to adjust drive-letter expectations, testify assertions, and `net/url`.

Risks and test signals: protects against invalid file URI construction, especially Windows `file:///C:/...` handling and rejection of relative paths.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/cio/io_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/cio/io_unix.go -->
# sources/cloud-native/containerd/pkg/cio/io_unix.go

Purpose: Unix implementation of container IO through filesystem FIFOs.

Important APIs and functions: `NewFIFOSetInDir`, `copyIO`, `openFifos`, `NewDirectIO`, `TerminalLogURI`, and `TerminalBinaryIO`.

Control flow and state: `NewFIFOSetInDir` creates a temp directory under the FIFO root and configures stdin/stdout/stderr paths. `openFifos` creates/opens requested FIFOs with nonblocking flags and cleans up on error. `copyIO` starts goroutines to copy stdin into FIFO and stdout/stderr out to writers, omitting stderr when terminal mode is active. Direct IO exposes FIFO pipes to callers.

Dependencies and integration: uses `github.com/containerd/fifo`, `syscall` flags, and common `cio` buffer pool. Used by shim task IO setup on Unix.

Risks and test signals: FIFO open order and cancellation are deadlock-sensitive. Terminal mode must suppress stderr. Tests cover missing-path errors, terminal stderr omission, temp path layout, and copy behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/cio/io_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/cio/io_unix_test.go -->
# sources/cloud-native/containerd/pkg/cio/io_unix_test.go

Purpose: Unix tests for FIFO path creation, FIFO opening, terminal behavior, direct IO, and copy/close handling.

Important APIs and functions: `TestOpenFifos`, `TestOpenFifosWithTerminal`, `TestNewFIFOSetInDir`, and additional tests over FIFO/direct IO helpers.

Control flow and state: tests create temp FIFO roots, intentionally use invalid directories for error cases, open FIFO sets with/without terminal mode, and assert generated paths and pipe availability. Some tests exercise copy paths with actual FIFO readers/writers.

Dependencies and integration: depends on `containerd/fifo`, Unix syscalls, and testify assertions.

Risks and test signals: covers important cleanup/error cases, but timing-sensitive FIFO copy behavior still depends on goroutine scheduling and correct cancellation.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/cio/io_unix_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/cio/io_windows.go -->
# sources/cloud-native/containerd/pkg/cio/io_windows.go

Purpose: Windows named-pipe implementation of container IO plus Windows-specific direct IO and terminal logging creators.

Important APIs and functions: `NewFIFOSetInDir`, `copyIO`, `NewDirectIO`, `NewDirectIOFromFIFOSet`, `TerminalLogURI`, and `TerminalBinaryIO`.

Control flow and state: named pipe paths are built under `\\.\pipe`. `copyIO` creates `winio.ListenPipe` listeners for requested streams and launches accept/copy goroutines. Terminal FIFO sets omit stderr, and terminal log creators set stderr to empty because HCSShim requires it.

Dependencies and integration: depends on Microsoft `go-winio` and containerd logging. Used by Windows shims/HCS integration.

Risks and test signals: listener accept errors are logged from goroutines, and cleanup depends on closing listener closers. Windows tests cover FIFOSet path shape and terminal stderr requirements.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/cio/io_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/cio/io_windows_test.go -->
# sources/cloud-native/containerd/pkg/cio/io_windows_test.go

Purpose: Windows tests for named-pipe FIFOSet creation and Windows log URI behavior.

Important APIs and functions: `TestNewFifoSetInDir_NoTerminal`, `TestNewFifoSetInDir_Terminal`, `TestLogFileBackslash`, and `TestLogURIGenerator`.

Control flow and state: tests create FIFO sets for terminal and non-terminal modes, assert stdin/stdout/stderr presence or absence, and verify backslash paths normalize to valid file URLs.

Dependencies and integration: uses testify and URL generation helpers from `cio`.

Risks and test signals: specifically protects the HCSShim terminal contract that stderr must be empty, and URI normalization for Windows paths.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/cio/io_windows_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/deprecation/deprecation.go -->
# sources/cloud-native/containerd/pkg/deprecation/deprecation.go

Purpose: central registry of deprecation warning identifiers and human-readable messages.

Important APIs and types: `Warning`, `Prefix`, `EnvPrefix`, warning constants such as `CRIRegistryMirrors`, `CgroupV1`, `CRIEnableCDI`, and helper functions `Valid` and `Message`.

Control flow and state: a static `messages` map stores warning text. `Valid` checks membership; `Message` returns text and presence flag.

Dependencies and integration: no external dependencies. Other packages can use warning IDs for plugin exports, logs, config validation, and environment gates.

Risks and test signals: string constants are API-like because users and config tooling may depend on them. No local tests in this file; changes need review for wording, removal dates, and backward compatibility.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/deprecation/deprecation.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/dialer/dialer.go -->
# sources/cloud-native/containerd/pkg/dialer/dialer.go

Purpose: context-aware dial helper for containerd local endpoints with retry-on-not-found behavior.

Important APIs and functions: `ContextDialer`, unexported `timeoutDialer`, and `dialResult`.

Control flow and state: `ContextDialer` derives timeout from context deadline, then `timeoutDialer` starts a goroutine repeatedly calling platform `dialer` until success/non-ENOENT error or stop. If timeout fires, it closes the stop channel and asynchronously closes any late connection.

Dependencies and integration: platform files provide Unix socket or Windows named-pipe dialing and `isNoent`. Used as a gRPC dialer for containerd endpoints.

Risks and test signals: when timeout is zero, `time.After(0)` can fire immediately, so callers without deadlines rely on platform dial timing. Retry delay is fixed at 10 ms for missing sockets/pipes.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/dialer/dialer.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/dialer/dialer_unix.go -->
# sources/cloud-native/containerd/pkg/dialer/dialer_unix.go

Purpose: Unix socket address formatting and dialing for the shared dialer.

Important APIs and functions: `DialAddress`, `isNoent`, and platform `dialer`.

Control flow and state: `DialAddress` prepends `unix://`; `dialer` trims that prefix and calls `net.DialTimeout("unix", ...)`; `isNoent` recognizes `syscall.ENOENT`.

Dependencies and integration: used by gRPC clients connecting to Unix-domain containerd sockets.

Risks and test signals: string prefix handling is simple; malformed addresses are passed to `net.DialTimeout`. Retry behavior for missing sockets is implemented in common code.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/dialer/dialer_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/dialer/dialer_windows.go -->
# sources/cloud-native/containerd/pkg/dialer/dialer_windows.go

Purpose: Windows named-pipe address formatting and dialing for the shared dialer.

Important APIs and functions: `DialAddress`, `isNoent`, and platform `dialer`.

Control flow and state: addresses are slash-normalized, prefixed with `npipe://` if needed, trimmed before dialing, and passed to `winio.DialPipe` with timeout.

Dependencies and integration: depends on Microsoft `go-winio`; used for containerd named pipe gRPC connections on Windows.

Risks and test signals: path normalization must preserve Windows named pipe semantics. Missing-pipe retry is driven by `os.IsNotExist` through common code.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/dialer/dialer_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/display/manifest_printer.go -->
# sources/cloud-native/containerd/pkg/display/manifest_printer.go

Purpose: render OCI image, manifest, index, config, layer, and content metadata as a readable tree.

Important APIs and types: `TreeFormat`, `LineTreeFormat`, `ImageTreePrinter`, options `Verbose`, `WithWriter`, `WithFormat`, constructor `NewImageTreePrinter`, and methods `PrintImageTree`, `PrintManifestTree`, `printManifestTree`, and `showContent`.

Control flow and state: the printer writes to its configured writer, recursively reads descriptors from a content store, prints descriptor media type/digest/size/platform, unmarshals manifests or indexes, and prints child config/layer/manifest entries with tree prefixes. Verbose mode prints content labels and indented JSON content for JSON media types.

Dependencies and integration: integrates containerd `content` and `images`, OCI image spec descriptors, platform formatting, and `errdefs.IsNotFound` handling.

Risks and test signals: tree output order follows manifest/index order but map label order is not deterministic. Missing local content is non-fatal and displayed as skipped, while other content errors abort printing.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/display/manifest_printer.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/epoch/context.go -->
# sources/cloud-native/containerd/pkg/epoch/context.go

Purpose: context carrier for `SOURCE_DATE_EPOCH` values without relying on environment variables.

Important APIs and types: private context key type, `WithSourceDateEpoch`, and `FromContext`.

Control flow and state: `WithSourceDateEpoch` stores a `*time.Time` in context; `FromContext` retrieves it and returns nil when absent or wrong type.

Dependencies and integration: used by `archive.WriteDiff` to apply reproducible timestamp limits from context if no explicit write option is set.

Risks and test signals: stores a pointer, so caller mutation of the pointed time after insertion would affect readers. This file intentionally does not read the environment.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/epoch/context.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/epoch/epoch.go -->
# sources/cloud-native/containerd/pkg/epoch/epoch.go

Purpose: parse and manage the `SOURCE_DATE_EPOCH` environment variable for reproducible builds/artifacts.

Important APIs and constants: `SourceDateEpochEnv`, `SourceDateEpoch`, `ParseSourceDateEpoch`, `SetSourceDateEpoch`, and `UnsetSourceDateEpoch`.

Control flow and state: `SourceDateEpoch` reads the env var, returns nil when unset, and wraps parse errors. `ParseSourceDateEpoch` rejects empty strings, parses an integer Unix timestamp, and returns UTC time. Set/unset mutate process environment.

Dependencies and integration: used by archive diff options and any component requiring reproducible timestamps.

Risks and test signals: environment state is process-global; tests use `t.Setenv` style setup. Negative or huge integer behavior follows `strconv.ParseInt` and `time.Unix`.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/epoch/epoch.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/epoch/epoch_test.go -->
# sources/cloud-native/containerd/pkg/epoch/epoch_test.go

Purpose: tests for `SOURCE_DATE_EPOCH` parsing and environment access.

Important APIs and functions: `TestSourceDateEpoch` covers unset, empty, valid UTC/non-UTC time conversion, invalid env values, and direct parse errors.

Control flow and state: tests set/unset environment values, call `SourceDateEpoch` and `ParseSourceDateEpoch`, and assert nil/error/time equality expectations.

Dependencies and integration: uses testify `require` and standard `os/time`.

Risks and test signals: confirms empty environment is treated as unset by `SourceDateEpoch`, while direct parsing of empty string is an error.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/epoch/epoch_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/fifosync/fifo_unix.go -->
# sources/cloud-native/containerd/pkg/fifosync/fifo_unix.go

Purpose: Unix FIFO-based interprocess synchronization primitive.

Important APIs and types: `Trigger`, `Waiter`, `NewTrigger`, `NewWaiter`, internal `fifo`, `new`, `Name`, `AsTrigger`, `Trigger`, `AsWaiter`, and `Wait`.

Control flow and state: `new` validates existing path or creates a FIFO with `unix.Mkfifo`. In this implementation `Trigger` opens the FIFO read-only and drains it with `io.ReadAll`, while `Wait` opens it write-only and writes a single byte. The synchronization effect comes from FIFO open/read/write blocking between the two processes.

Dependencies and integration: uses Unix named pipes through `x/sys/unix` and standard file I/O. Useful for coordinating shim/process startup.

Risks and test signals: FIFO open semantics can block depending on reader/writer order. Cleanup is caller-owned; this file does not remove FIFO paths.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/fifosync/fifo_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/filters/adaptor.go -->
# sources/cloud-native/containerd/pkg/filters/adaptor.go

Purpose: abstraction layer mapping parsed filter field paths to concrete object values.

Important APIs and types: `Adaptor`, `AdapterFunc`, and `AdapterFunc.Field`.

Control flow and state: no state. `AdapterFunc` lets callers use closures as adaptors by implementing `Field(fieldpath []string)`.

Dependencies and integration: consumed by `Filter.Match` implementations in `filter.go`; callers implement this to adapt containers/images/tasks/etc. to generic filter syntax.

Risks and test signals: field path semantics are caller-defined, so interoperability depends on consistent adaptor implementations.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/filters/adaptor.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/filters/filter.go -->
# sources/cloud-native/containerd/pkg/filters/filter.go

Purpose: filter composition and selector matching for containerd's generic filter language.

Important APIs and types: `Filter`, `FilterFunc`, `Always`, `Any`, `All`, `operator`, and `selector`.

Control flow and state: `Any.Match` short-circuits on first matching filter; `All.Match` short-circuits on first non-match. `selector.Match` queries the adaptor and applies present, equal, not-equal, or regexp match operators. Regex patterns are compiled lazily into `selector.re`, but because the receiver is by value this cache is not retained across calls.

Dependencies and integration: parser builds these selectors from user filter strings; logging reports regex compile failures.

Risks and test signals: `operatorNotEqual` returns true for missing fields whose value is empty unless adaptor returns the same value, matching existing semantics. Lazy regex cache by value may repeatedly compile. Tests cover operator strings and filter behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/filters/filter.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/filters/filter_test.go -->
# sources/cloud-native/containerd/pkg/filters/filter_test.go

Purpose: broad behavioral tests for parsing and applying filter expressions.

Important APIs and functions: `TestFilters`, `TestOperatorStrings`, and `FuzzFiltersParse`.

Control flow and state: table tests parse filter strings, build adaptors over test maps/field paths, compare matched results, and verify error strings for malformed input. Operator string tests validate debug formatting. Fuzzing asserts parse never returns both nil filter and nil error.

Dependencies and integration: tests cover parser, scanner, quote handling, selector matching, and adaptor behavior together.

Risks and test signals: the table is the main compatibility contract for filter syntax, including quoted field labels, regex delimiters, separators, and invalid forms.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/filters/filter_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/filters/parser.go -->
# sources/cloud-native/containerd/pkg/filters/parser.go

Purpose: recursive-descent parser for containerd filter expressions.

Important APIs and types: `Parse`, `ParseAll`, internal `parser`, `selectors`, `selector`, `fieldpath`, `field`, `operator`, `value`, `unquote`, `parseError`, and `mkerr`.

Control flow and state: empty input returns `Always`. `ParseAll` parses multiple independent filter strings and wraps them in `Any`. The parser consumes scanner tokens for comma-separated selectors, dot-separated field paths, optional operators, and values. Regex-match values allow alternate quote delimiters; field names do not.

Dependencies and integration: uses `scanner.go` for tokens, `quote.go` for unquoting, and wraps errors with `errdefs.ErrInvalidArgument` in `ParseAll`.

Risks and test signals: error messages include input position and are asserted in tests, so changes are compatibility-sensitive. Hand-written parsing must stay aligned with scanner tokenization.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/filters/parser.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/filters/quote.go -->
# sources/cloud-native/containerd/pkg/filters/quote.go

Purpose: modified Go string unquoting implementation that also supports `/` and `|` delimiters for regular expression filter values.

Important APIs and functions: `unquoteChar`, `unquote`, `unhex`, `contains`, and package error `errQuoteSyntax`.

Control flow and state: decodes escapes for simple, hex, Unicode, octal, and quoted characters; rejects invalid quote syntax and invalid Unicode. Alternate quote delimiters are treated like double quotes for regex-focused parsing.

Dependencies and integration: used by parser `unquote` when processing quoted fields/values. The implementation is adapted from Go's `strconv` logic.

Risks and test signals: quote behavior is syntax-critical and security-adjacent because filters may include arbitrary labels and regexes. Scanner/parser tests cover valid/invalid escape forms.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/filters/quote.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/filters/scanner.go -->
# sources/cloud-native/containerd/pkg/filters/scanner.go

Purpose: lexical scanner for filter syntax.

Important APIs and types: token constants, `token.String`, `token.GoString`, `scanner`, `init`, `next`, `peek`, `scan`, `scanField`, `scanOperator`, `scanValue`, `scanQuoted`, `scanEscape`, `scanDigits`, `error`, and rune classifier helpers.

Control flow and state: scanner tracks current and previous positions, reads runes, emits field/operator/value/separator/quoted/illegal/EOF tokens, and records errors for invalid quotes/escapes. It recognizes field runes, operator runes, separators, quote delimiters, and value characters.

Dependencies and integration: parser depends on token kinds and positions for grammar and error reporting.

Risks and test signals: rune classification defines the accepted filter language. Off-by-one position errors affect user-facing parse messages. `scanner_test.go` provides detailed tokenization cases.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/filters/scanner.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/filters/scanner_test.go -->
# sources/cloud-native/containerd/pkg/filters/scanner_test.go

Purpose: tests for tokenization of valid and invalid filter strings.

Important APIs and functions: `TestScanner` drives scanner initialization and repeated `scan` calls over table cases.

Control flow and state: each case supplies an input and expected token sequence; the test scans until EOF or illegal token, asserts token/text/position expectations, and fails if input is not consumed or expected tokens are absent.

Dependencies and integration: directly validates scanner behavior independent from parser, giving precise coverage for quotes, escapes, separators, values, fields, and operators.

Risks and test signals: protects grammar compatibility. Any change to accepted characters or quote handling should update both scanner and parser tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/filters/scanner_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/gc/gc.go -->
# sources/cloud-native/containerd/pkg/gc/gc.go

Purpose: experimental deterministic resource reachability and sweep helpers for containerd garbage collection.

Important APIs and types: `ResourceType`, `ResourceMax`, `Node`, `Stats`, `Tricolor`, `ConcurrentMark`, and `Sweep`.

Control flow and state: `Tricolor` performs single-thread depth-first marking from roots, calling `refs` for each gray node, de-duplicating via `seen`, stripping high bits from `ResourceType` before recording reachable. `ConcurrentMark` receives roots from a channel, fans out reference traversal goroutines, tracks outstanding work with a waitgroup, cancels on first error, and returns the seen set. `Sweep` calls `remove` for nodes absent from the reachable map.

Dependencies and integration: uses only `context`, `sync`, and `time`. Callers provide graph traversal and removal semantics.

Risks and test signals: `ConcurrentMark` mutates `seen` from a single goroutine receiving `grays`, but calls `wg.Add` inside callback goroutines before sending; this is subtle concurrency code. Correct usage requires graph stability until sweep completes. Tests cover basic graphs and benchmark tricolor.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/gc/gc.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/gc/gc_test.go -->
# sources/cloud-native/containerd/pkg/gc/gc_test.go

Purpose: tests and benchmark for GC reachability algorithms.

Important APIs and functions: `TestTricolorBasic`, `BenchmarkTricolor`, `TestConcurrentBasic`, `writeNodes`, `lookup`, `lookupc`, and `toNodes`.

Control flow and state: tests define a directed graph, mark reachable nodes from roots, then compare the retained/swept sequence with expected nodes. Concurrent tests feed roots through a channel and use callback-based reference expansion.

Dependencies and integration: standard testing, context, reflection, and local helper maps.

Risks and test signals: validates basic reachability and cycles but does not deeply stress cancellation or race behavior in `ConcurrentMark`. Benchmark creates a larger reference graph for allocation/performance signal.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/gc/gc_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/httpdbg/debug.go -->
# sources/cloud-native/containerd/pkg/httpdbg/debug.go

Purpose: HTTP client debugging helpers for dumping requests/responses and attaching Go HTTP trace logging.

Important APIs and functions: `debugTransport.RoundTrip`, `DumpRequests`, `NewDebugClientTrace`, `traceTransport.RoundTrip`, `DumpTraces`, and `WithClientTrace`.

Control flow and state: `DumpRequests` wraps a client's transport with `debugTransport`, which uses `httputil.DumpRequestOut` and `DumpResponse` to write full request/response bytes to a provided writer or logger writer. `DumpTraces` wraps transport with a `httptrace.ClientTrace` that logs DNS start/done and connection events. `WithClientTrace` returns a context carrying the trace.

Dependencies and integration: uses standard `net/http`, `net/http/httptrace`, `net/http/httputil`, and containerd `log`. It is intended for ctr push/pull and HTTP client diagnostics.

Risks and test signals: request/response dumps can expose credentials or payloads if enabled inappropriately. `NewDebugClientTrace` assumes DNS results contain at least one address when no error is reported. No local tests were in the assigned set.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/httpdbg/debug.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/identifiers/validate.go -->
# sources/cloud-native/containerd/pkg/identifiers/validate.go

Purpose: validate containerd identifiers against length and character rules.

Important APIs and constants: `Validate` plus unexported maximum length and lazy regular expression. Valid identifiers must be non-empty, no more than 76 characters, and match the configured identifier regexp.

Control flow and state: `Validate` checks empty string, length, and regexp match in order, returning errors wrapped with `errdefs.ErrInvalidArgument`.

Dependencies and integration: uses containerd `internal/lazyregexp` and `errdefs` so callers can classify invalid argument errors.

Risks and test signals: regexp changes affect API compatibility for IDs. Tests cover representative valid and invalid strings plus `errdefs.IsInvalidArgument`.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/identifiers/validate.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/identifiers/validate_test.go -->
# sources/cloud-native/containerd/pkg/identifiers/validate_test.go

Purpose: tests for identifier validation rules and error classification.

Important APIs and functions: `TestValidIdentifiers` and `TestInvalidIdentifiers`.

Control flow and state: table tests call `Validate` for accepted and rejected inputs. Invalid cases assert an error is returned and that `errdefs.IsInvalidArgument` classifies it.

Dependencies and integration: validates both local regexp/length rules and cross-package errdefs wrapping behavior.

Risks and test signals: the examples define the practical identifier contract for callers. Boundary length and character-class coverage are important when updating validation.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/identifiers/validate_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/imageverifier/bindir/bindir.go -->
# sources/cloud-native/containerd/pkg/imageverifier/bindir/bindir.go

Purpose: image verifier implementation that runs executable verifier binaries from a configured directory and combines their judgements.

Important APIs and types: `Config`, `ImageVerifier`, `NewImageVerifier`, `VerifyImage`, `runVerifier`, and `outputLimitBytes`. It implements `imageverifier.ImageVerifier`.

Control flow and state: `VerifyImage` reads verifier directory entries in sorted order, accepts images if the directory is missing/empty, enforces `MaxVerifiers`, and runs each verifier. A nonzero verifier exit code rejects the image with captured stdout reason; execution errors abort verification. `runVerifier` creates a timeout context, starts the binary with image name/digest/media-type args, writes the OCI descriptor JSON to stdin asynchronously, reads bounded stdout as the reason, logs bounded stderr line-by-line, drains truncated streams, waits for process exit, and returns exit code/reason.

Dependencies and integration: depends on `internal/tomlext` for duration config, `pkg/imageverifier` judgement types, containerd logging, OCI descriptors, and OS process/pipe primitives. Platform-specific process cleanup is supplied by sibling files outside this assignment.

Risks and test signals: this code executes external binaries, so timeout, pipe draining, output bounds, sorted order, and process cleanup are critical. Output is capped at 32 KiB and may be truncated. Directory contents are trusted as executables; deployment must control `BinDir`.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/imageverifier/bindir/bindir.go -->
