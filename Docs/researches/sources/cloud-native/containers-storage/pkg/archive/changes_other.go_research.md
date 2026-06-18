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
