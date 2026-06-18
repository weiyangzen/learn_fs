<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/integration/client/mount_manager_linux_test.go -->
# sources/cloud-native/containerd/integration/client/mount_manager_linux_test.go

## Purpose
Tests the Linux mount manager service and runtime rootfs mount composition, including formatted loopback mounts and overlay mounts that reference earlier mounts by index.

## APIs, Types, And Functions
Tests are `TestMountManager` and `TestMountAtRuntime`. Helpers are `createImgFile`, `setupMount`, and `withImage`. The file uses `client.MountManager().List/Info`, `SnapshotService.View`, `container.NewTask` with `containerd.WithRootFS`, mount types `xfs` and `format/overlay`, `identity.ChainID`, image config reads, and OCI spec mutation.

## Control Flow And State
The first test asserts a fresh mount manager has no mounts. The runtime test creates an XFS image file, prepares directories on it, gets a read-only snapshot view for the image rootfs, then starts a container with a composed mount list that overlays the image root and loopback filesystem. It writes a file through the first task, ensures active mount info is present during the task and gone after deletion, then starts a second container using the previous upperdir as a lowerdir and verifies the file content is visible.

## Persistence And Integration Points
State includes a 300 MB loopback image, XFS filesystem metadata, snapshot views, active runtime mounts, and overlay upper/work directories. The test integrates with `mkfs.xfs`, kernel loop mounts, containerd mount formatting, mount manager tracking, and image config parsing.

## Risks And Test Signals
The test skips when `mkfs.xfs` is absent and is sensitive to mount permissions and filesystem support. Failures indicate broken mount placeholder substitution, mount manager leaks, runtime rootfs mount cleanup problems, or incorrect image-config-to-process conversion.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/integration/client/mount_manager_linux_test.go -->
