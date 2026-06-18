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
