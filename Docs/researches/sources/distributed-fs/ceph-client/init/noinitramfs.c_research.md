# sources/distributed-fs/ceph-client/init/noinitramfs.c

## Purpose
`noinitramfs.c` creates a minimal default rootfs for builds or boots without initramfs extraction. It ensures `/dev/console` and `/root` exist early enough for the rest of init to proceed.

## Important APIs, Types, And Functions
- `default_rootfs()` enables usermode helpers, creates `/dev`, creates `/dev/console` as character device major 5 minor 1 with owner read/write permissions, and creates `/root`.
- `rootfs_initcall(default_rootfs)` schedules it in the rootfs initcall stage.

## Control Flow
The initcall performs three filesystem operations in order. Any failure jumps to a warning path and returns the negative error.

## State And Persistence
Persistent effects are rootfs directories and the console device node. No private state is retained.

## Dependencies And Integration Points
It depends on init syscall wrappers, `new_encode_dev(MKDEV(5,1))`, rootfs initcall ordering, and `usermodehelper_enable()`. `kernel_init_freeable()` later opens `/dev/console`, so this fallback complements the initramfs path.

## Risks And Edge Cases
If rootfs is not writable or device creation fails, later console setup may warn or fail. The function is intentionally minimal and does not populate a complete userspace.

## Test Signals
Boots without an initramfs should show a usable `/dev/console` and `/root`. The warning `Failed to create a rootfs` is the direct failure signal.
