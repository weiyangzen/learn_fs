# sources/distributed-fs/ceph-client/include/uapi/linux/suspend_ioctls.h

## Purpose
Defines ioctl ABI for the snapshot/suspend device used by hibernation and suspend-to-RAM userspace helpers.

## Important APIs, Types, and Constants
`struct resume_swap_area` is a packed structure carrying resume swap `offset` and device id `dev` for `SNAPSHOT_SET_SWAP_AREA`. Ioctls include `SNAPSHOT_FREEZE`, `SNAPSHOT_UNFREEZE`, `SNAPSHOT_ATOMIC_RESTORE`, `SNAPSHOT_FREE`, `SNAPSHOT_FREE_SWAP_PAGES`, `SNAPSHOT_S2RAM`, `SNAPSHOT_SET_SWAP_AREA`, `SNAPSHOT_GET_IMAGE_SIZE`, `SNAPSHOT_PLATFORM_SUPPORT`, `SNAPSHOT_POWER_OFF`, `SNAPSHOT_CREATE_IMAGE`, `SNAPSHOT_PREF_IMAGE_SIZE`, `SNAPSHOT_AVAIL_SWAP_SIZE`, and `SNAPSHOT_ALLOC_SWAP_PAGE`.

## Control Flow, State, and Persistence
Userspace coordinates freezing, image creation, swap allocation, restore, and platform power transitions via ioctl sequence. Kernel state includes frozen task state, hibernation image pages, swap allocations, and platform support flags.

## Dependencies and Integration Points
Depends on `<linux/types.h>` and ioctl macros. Integrates with `/dev/snapshot`, swsusp, power management, and initramfs resume tooling.

## Risks and Test Signals
Risks are unsafe ioctl order, packed `resume_swap_area` layout, device-number mismatch, and data loss if swap/image accounting is wrong. Test hibernation create/resume paths, invalid order failures, 32/64-bit structure layout, low-swap behavior, and platform support detection.
