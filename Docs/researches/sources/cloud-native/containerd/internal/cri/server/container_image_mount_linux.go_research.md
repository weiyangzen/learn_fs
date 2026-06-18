# sources/cloud-native/containerd/internal/cri/server/container_image_mount_linux.go

## Purpose
This Linux-specific image-volume helper optimizes overlay cleanup, detects real mountpoints, and converts CRI user namespace ID mappings into snapshot remapper labels.

## Important APIs, Types, and Functions
`addVolatileOptionOnImageVolumeMount` appends `volatile` to overlay mounts on kernels >= 5.10 unless already present. `ensureImageVolumeMounted` checks `os.Stat` and `mount.Lookup` to verify the target itself is the mountpoint. `getImageVolumeSnapshotOpts` parses UID/GID mappings and returns `containerd.WithRemapperLabels`.

## Control Flow, State, and Persistence
Kernel volatile support is cached via `sync.Once`. Mount detection distinguishes an existing directory from an actual mountpoint. Snapshot options are returned only when both UID and GID mappings exist; the first mapping drives remapper labels.

## Dependencies and Integration Points
It depends on containerd mount/snapshot APIs, kernel version detection, CRI runtime mount ID mappings, and Linux user namespace parsing helpers. It is called by `mutateImageMount` before preparing image-volume snapshots.

## Risks and Test Signals
Risks include incorrect kernel feature detection, treating plain directories as mounted volumes, and wrong idmap label selection. `container_image_mount_linux_test.go` checks remapper labels, empty mappings, partial mappings, and multi-line mapping rejection.
