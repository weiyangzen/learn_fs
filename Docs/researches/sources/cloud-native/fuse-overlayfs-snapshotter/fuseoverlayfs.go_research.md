<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/fuse-overlayfs-snapshotter/fuseoverlayfs.go -->
# sources/cloud-native/fuse-overlayfs-snapshotter/fuseoverlayfs.go

Purpose: Linux containerd `snapshots.Snapshotter` implementation backed by `fuse-overlayfs`.

Important APIs and flow: `NewSnapshotter` creates root, metadata DB, and snapshots directory. `Stat`, `Update`, `Walk`, and `Close` delegate to containerd metadata storage. `Usage` returns stored committed usage or scans active upperdir disk usage. `Prepare`/`View` call `createSnapshot`, which creates a temp snapshot directory, registers metadata, inherits parent ownership, renames into place, commits metadata, and returns mounts. `Commit` records disk usage and commits active snapshots. `Remove` removes metadata and either defers cleanup or computes unreferenced directories for deletion. `Cleanup` deletes abandoned snapshot directories.

State and persistence: persistent state is `root/metadata.db` plus `root/snapshots/<id>/fs` and optional `work`. Mount generation uses bind mounts for single-layer cases and `fuse3.fuse-overlayfs` with `lowerdir`, `upperdir`, `workdir`, and converted UID/GID mapping labels for layered cases. Risks include untested async remove, cleanup races if directories are externally touched, reliance on parent ID order, no direct fsync of metadata/directories, and `convertIDMappingOption` blindly replacing commas with colons. Test signal is containerd's `SnapshotterSuite` in `fuseoverlayfs_test.go`.
<!-- END_FILE_RESEARCH: sources/cloud-native/fuse-overlayfs-snapshotter/fuseoverlayfs.go -->
