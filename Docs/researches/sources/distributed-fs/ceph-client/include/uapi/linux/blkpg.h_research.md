# sources/distributed-fs/ceph-client/include/uapi/linux/blkpg.h

## Purpose

`sources/distributed-fs/ceph-client/include/uapi/linux/blkpg.h` exports the block partition table manipulation ioctl ABI. The complete 36-line header was read. It defines the `BLKPG` ioctl, operation codes for adding, deleting, and resizing partitions, and the argument structures passed from userspace to the block layer.

## Important APIs, Types, and Functions

There are no functions. `BLKPG` is `_IO(0x12,105)`. `struct blkpg_ioctl_arg` carries `op`, `flags`, `datalen`, and a `void __user *data` pointer. Operation codes are `BLKPG_ADD_PARTITION`, `BLKPG_DEL_PARTITION`, and `BLKPG_RESIZE_PARTITION`. `struct blkpg_partition` provides byte `start`, byte `length`, partition number `pno`, and fixed-size `devname`/`volname` arrays that the comments say are unused or ignored.

## Control Flow

The header has no executable flow. Userspace populates `blkpg_ioctl_arg`, points `data` at a `blkpg_partition`, chooses an op, and issues `BLKPG` to a block device. Kernel block partition code copies the data from userspace, validates the operation, and updates the in-kernel partition representation.

## State and Persistence Behavior

This ABI primarily mutates kernel runtime partition state. It does not by itself rewrite the on-disk partition table; persistence requires separate tooling to update partition metadata on media. The effects last until rescans, removal, reboot, or later partition-management operations.

## Dependencies and Integration Points

Direct dependencies are `<linux/compiler.h>` for `__user` and `<linux/ioctl.h>`. Integration points include block device ioctl handling, partition scanning, partition-management tools, udev-style consumers observing partition changes, and disk utilities that coordinate on-disk table edits with kernel table updates.

## Risks and Edge Cases

`data` is a userspace pointer and must be validated through copy-from-user logic. `datalen` must match the expected structure for the selected op. `start` and `length` are byte offsets, not sectors, so tools must avoid unit confusion. The name fields are fixed 64-byte arrays but ignored, so relying on them for naming behavior is wrong. Partition numbers, overlap checks, open partitions, and resize constraints are enforced outside this header and are common failure points.

## Test Signals

Useful tests include add/delete/resize ioctl smoke tests on loop devices, invalid `datalen` and bad pointer tests, byte-versus-sector unit tests, partition overlap and busy-device error tests, and verification that on-disk partition tables are unchanged unless a separate writer updates them.
