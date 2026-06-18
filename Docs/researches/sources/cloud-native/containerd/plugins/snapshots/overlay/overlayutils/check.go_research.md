<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/plugins/snapshots/overlay/overlayutils/check.go -->
# sources/cloud-native/containerd/plugins/snapshots/overlay/overlayutils/check.go

## Purpose
Provides Linux overlayfs capability probes for backing filesystem support, multiple lowerdirs, tmpfs detection, userxattr needs, and ID-mapped overlay mounts.

## Important APIs, Types, And Functions
Exports `SupportsMultipleLowerDir`, `Supported`, `IsPathOnTmpfs`, `NeedsUserXAttr`, and `SupportsIDMappedMounts`. Constant `tmpfsMagic` identifies tmpfs via statfs.

## Control Flow
`Supported` creates the root, checks `d_type`, then attempts a real multiple-lowerdir overlay mount. `NeedsUserXAttr` returns false outside user namespaces and on tmpfs, returns true quickly on kernels >= 5.11, otherwise attempts a temporary overlay mount with `userxattr`. `SupportsIDMappedMounts` fast-paths kernels >= 5.19, otherwise creates temp dirs, obtains a user namespace fd, ID-maps a lowerdir, mounts overlay, and verifies merged directory ownership.

## State And Persistence
All probes create temporary directories and mounts, then unmount and remove them. Failed cleanup is logged, not persisted intentionally.

## Dependencies And Integration Points
Uses containerd mount helpers, kernel version utilities, continuity `fs.SupportsDType`, moby userns detection, Linux `unix` syscalls, and logging. Called by overlay and EROFS plugin initialization and by embedders through `Supported`.

## Risks And Edge Cases
Probes require privileges and can fail because of policy rather than kernel capability. Vendor backports make version checks insufficient, which is why slow paths exist. Mount cleanup failures can leave temporary mounts/directories.

## Test Signals
Benchmarks in `check_test.go` exercise `Supported` on loopback filesystems with ext4, XFS ftype variants, and FAT when tooling is available.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/plugins/snapshots/overlay/overlayutils/check.go -->
