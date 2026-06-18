<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/zram/zram01.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/zram/zram01.sh

## Purpose

`zram01.sh` creates a zram block device, formats it, mounts it, fills it with zero data, and checks that compression produces a ratio above 1:1.

## Important APIs, Types, and Functions

The script sources `zram_lib.sh`, sets `dev_num=1`, `zram_max_streams=2`, `zram_sizes=2097152`, `zram_mem_limits=2M`, `zram_filesystems=ext4`, and `zram_algs=lzo`. Its local `zram_fill_fs()` appends zero-filled 1 KiB blocks with `dd`, reads `/sys/block/zram$i/mm_stat`, computes a compression ratio with shell arithmetic and `bc`, and sets `ERR_CODE` on failure.

## Control Flow and State

The flow is prerequisites, load/create device, set streams, set compression algorithm, set disk size, set memory limit, make filesystem, mount, fill, cleanup, and print `[PASS]` or `[FAIL]`. Shared state from `zram_lib.sh` tracks device range, mounted devices, swap devices, and module/control mode.

## Dependencies and Integration Points

It depends on root privileges, `modprobe`, zram sysfs, `mkfs.ext4` or fallback behavior in the library, `mount`, `dd`, `awk`, `bc`, and writable working directory for mount points and `err.log`.

## Risks and Test Signals

Risks include missing `lzo`, missing filesystem tools, low device size, `mm_stat` format drift, and cleanup failures leaving mounted devices. Passing output includes a compression ratio and `zram01 : [PASS]`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/zram/zram01.sh -->
