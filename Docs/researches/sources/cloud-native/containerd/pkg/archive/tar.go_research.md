<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/archive/tar.go -->
# sources/cloud-native/containerd/pkg/archive/tar.go

Purpose: core OCI diff tar implementation for containerd. It can generate a tar stream representing filesystem changes and apply an OCI-style diff tar to a root directory, including whiteouts, hardlinks, special files, xattrs, ownership, permissions, and reproducible timestamps.

Important APIs and types: exported entry points are `Diff`, `WriteDiff`, `Apply`, `ChangeWriter`, `ChangeWriterOpt`, `WithModTimeUpperBound`, and `NewChangeWriter`. Important helpers include `writeDiffNaive`, `applyNaive`, `createTarFile`, `mkparent`, `copyBuffered`, `hardlinkRootPath`, and `validateWhiteout`. Constants define OCI/AUFS whiteout names and PAX xattr prefixes.

Control flow: `Diff` starts a goroutine with an `io.Pipe`; `WriteDiff` resolves options, honors `epoch.FromContext`, and defaults to `writeDiffNaive`. `writeDiffNaive` uses continuity `fs.Changes` to feed a `ChangeWriter`. `Apply` cleans the root, applies options/defaults, and defaults to `applyNaive`. `applyNaive` iterates tar headers, normalizes names, filters entries, skips unsupported platform files, bounds parent paths via `fs.RootPath`, creates missing parents, validates/converts whiteouts, removes conflicting destinations, creates the file, records unpacked paths, and restores directory mtimes at the end.

State and persistence: persistent effects are filesystem mutations under the extraction root, deletion of whiteouted paths, xattr writes, chmod/chown/chtimes, hardlink creation, and optional inherited parent metadata from `Parents`. `ChangeWriter` tracks inode sources/references to emit hardlinks, `addedDirs` to include required parent directories once, and optional mod-time upper bound for reproducible output. `bufPool` reuses 32 KiB copy buffers.

Dependencies and integration: relies on Go `archive/tar`, containerd `tarheader`, `epoch`, `continuity/fs`, logging, and platform hooks supplied by `tar_unix.go`, `tar_windows.go`, `tar_mostunix.go`, `tar_freebsd.go`, and option files. It implements OCI layer whiteout conventions and integrates with snapshotter diff/apply paths.

Risks and test signals: the main risk surface is path traversal through symlinks/hardlinks and destructive whiteout handling. The code uses `fs.RootPath`, root checks, `hardlinkRootPath`, and `validateWhiteout`, but comments/tests note some symlink-parent behavior is still compatibility-sensitive. `tar_test.go` heavily tests breakouts, hardlink ordering, xattrs, directory mtimes, whiteouts, sockets, and source date reproducibility.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/archive/tar.go -->
