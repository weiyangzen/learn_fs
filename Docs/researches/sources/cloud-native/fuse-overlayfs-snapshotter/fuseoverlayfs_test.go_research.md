<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/fuse-overlayfs-snapshotter/fuseoverlayfs_test.go -->
# sources/cloud-native/fuse-overlayfs-snapshotter/fuseoverlayfs_test.go

Purpose: containerd snapshotter conformance test wiring for the fuse-overlayfs snapshotter.

Important flow: `newSnapshotter` creates a snapshotter rooted at the test directory and returns its `Close` cleanup. `TestFUSEOverlayFS` requires root, creates a temp dir, skips if `Supported` fails, then runs containerd `testsuite.SnapshotterSuite`.

State and integration: performs real filesystem, FUSE, and metadata operations in a temp directory. Requires root and functional fuse-overlayfs. Risks include environment-dependent skips, no dedicated assertions for async remove or ID mapping labels, and relying on upstream testsuite coverage. Test signal is strong behavioral conformance for standard snapshotter operations.
<!-- END_FILE_RESEARCH: sources/cloud-native/fuse-overlayfs-snapshotter/fuseoverlayfs_test.go -->
