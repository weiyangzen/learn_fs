# sources/cloud-native/containerd/integration/image_volume_linux_test.go

## Purpose

This Linux file validates CRI image volume mounts: read-only behavior, SELinux relabeling, subpath validation, snapshot cleanup, volatile overlay options, restart/idempotency behavior, and user namespace idmapped image volume ownership.

## Important APIs, Types, And Functions

- `TestImageVolumeBasic` table-tests read-only content, SELinux levels, subpath success, and rejected unsafe subpaths.
- `setupRunningContainerWithImageVolume` creates a pod/container with `WithImageVolumeMount`.
- `TestImageVolumeCheckVolatileOption` inspects overlay mount options for `volatile` or `fsync=volatile`.
- `TestImageVolumeSetupIfContainerdRestarts` verifies preexisting snapshot state is reused and not double-mounted.
- `TestImageVolumeWithUserNamespace` checks idmapped read-only image volume behavior.

## Control Flow

The basic test creates containers with image-volume mounts, optionally skips SELinux cases, verifies snapshot mounts exist, executes commands inside the container, and after pod cleanup polls until the image volume snapshot is gone. Subpath cases expect create errors for single-file, nonexistent, absolute, escaping, or symlink-escaping paths. The volatile test locates the image volume mount and inspects VFS options. The restart/idempotency test pre-creates snapshot targets before container creation and ensures multiple containers share the same mount. The user namespace test gates on userns, pidfd, and idmap support, then verifies access, read-only enforcement, and root ownership inside the namespace.

## State And Persistence Behavior

The tests create image volume snapshots under pod image volume directories and verify cleanup after pod deletion. They also observe mount table state and containerd overlay snapshotter metadata.

## Dependencies And Integration Points

They integrate CRI image volume mount fields, overlayfs snapshotter, containerd snapshot service, SELinux, kernel idmap support, pidfd support, and images `Alpine`, `Pause`, and `ResourceConsumer`.

## Risks And Edge Cases

Host kernel, SELinux, overlayfs, and idmap capabilities strongly affect coverage. The file contains the namespace label `"image-voloume"` typo only as a test namespace string. Cleanup polling can be slow if snapshot garbage collection stalls.

## Test Signals

Passing shows image volumes are mounted safely, read-only, labeled/idmapped correctly, not double-mounted, and cleaned up.
