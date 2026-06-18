# sources/distributed-fs/ceph-client/init/do_mounts.h

## Purpose
`do_mounts.h` shares declarations and small helpers among the early root-mount source files for root mounting, device-node creation, optional ramdisk/initrd loading, and delayed file-close flushing.

## Important APIs, Types, and Functions
It declares `mount_root_generic()`, `mount_root()`, and `root_mountflags`. `create_dev()` removes an existing path and creates a block device node using `init_mknod()`. Config stubs wrap `rd_load_image()` and `initrd_load()`. `init_flush_fput()` runs delayed fput and task work to avoid stale file references during mount retries.

## Control Flow
Root mount code calls `create_dev()` before mounting block roots or ramdisk roots. `do_mounts.c` calls `initrd_load()` unconditionally through a config-safe wrapper; `do_mounts_initrd.c` calls `rd_load_image()` through a similar wrapper when ramdisk support exists.

## State and Persistence Behavior
The helper mutates early rootfs namespace by unlinking and creating device nodes. The header itself stores no state beyond exposing `root_mountflags`.

## Dependencies and Integration Points
It depends on init syscall wrappers, block device encoding, root device constants, task work, delayed fput, and mount/initrd source files. It is the private contract among `do_mounts*.c`.

## Risks and Test Signals
Risks include creating wrong device-node modes, missing delayed fput flush before retrying filesystems, and config stubs causing silent no-op behavior. Test signals include builds with/without `BLK_DEV_RAM` and `BLK_DEV_INITRD`, device node creation failures, and root mount retry paths.
