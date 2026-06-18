# sources/cloud-native/containerd/plugins/snapshots/erofs/erofs_linux.go

## Purpose
`erofs_linux.go` provides Linux-specific helpers for the EROFS snapshotter.

## Important APIs, Types, And Functions
`defaultWritableSize` is `0` on Linux. `FindErofs` checks `/proc/filesystems`. `checkCompatibility` verifies d_type support and EROFS kernel support. `setImmutable` toggles `FS_IMMUTABLE_FL` with ioctls. `cleanupUpper` unmounts EROFS mounts under an upper path. `convertDirToErofs` calls `erofsutils.ConvertErofs` then removes upperdir children. `getParentOwnership` returns UID/GID from `syscall.Stat_t`.

## Control Flow
Compatibility checking runs during snapshotter creation when not in block mode. Immutable toggling opens the file, reads inode flags, updates the bit if needed, and writes flags back. Conversion cleans up the overlay upperdir after producing an EROFS layer.

## State And Persistence
The file mutates Linux inode flags, removes converted upperdir contents, and unmounts mount points. It does not own metadata.

## Dependencies And Integration Points
It depends on `/proc/filesystems`, continuity d_type checks, Linux ioctls, containerd mount helpers, EROFS conversion utilities, and syscall stat data. `erofs.go` calls these helpers for initialization, commit, remove, and ownership propagation.

## Risks
Kernel/filesystem support is mandatory. Immutable flag manipulation can fail due to permissions or unsupported filesystems. `convertDirToErofs` removes all children under the upperdir after conversion, so conversion correctness is critical before cleanup.

## Test Signals
No tests in this subset directly target these helpers. Linux EROFS snapshotter tests outside the requested list should cover compatibility and conversion behavior.
