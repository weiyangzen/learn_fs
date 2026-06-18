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
