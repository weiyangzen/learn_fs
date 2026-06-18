<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/zram/zram_lib.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/zram/zram_lib.sh

## Purpose

`zram_lib.sh` is the shared shell library for zram selftests. It handles root checks, zram device creation across old and new kernels, sysfs configuration, filesystem and swap setup, and cleanup.

## Important APIs, Types, and Functions

Global state includes `dev_makeswap`, `dev_mounted`, `dev_start`, `dev_end`, `module_load`, `sys_control`, `ksft_skip`, and parsed kernel version components. Functions are `check_prereqs()`, `kernel_gte()`, `zram_cleanup()`, `zram_load()`, `zram_max_streams()`, `zram_compress_alg()`, `zram_set_disksizes()`, `zram_set_memlimit()`, `zram_makeswap()`, `zram_swapoff()`, `zram_makefs()`, and `zram_mount()`.

## Control Flow and State

Test scripts set per-device arrays as whitespace-separated strings, call `zram_load()` to determine existing device count and create devices either with `/sys/class/zram-control/hot_add` or `modprobe zram num_devices=`, then call configuration helpers. `zram_cleanup()` reverses state by swapoff, umount, sysfs reset, directory removal, hot_remove, and optional `rmmod`.

## Dependencies and Integration Points

The library depends on root privileges, `/sys/class/zram-control`, `/sys/block/zram*/`, `/proc/modules`, `modprobe`, `rmmod`, `mkswap`, `swapon`, `swapoff`, `mkfs.*`, `mount`, `umount`, `seq`, and shell arithmetic. It encodes kselftest skip code 4.

## Risks and Test Signals

Risks include races with pre-existing zram devices, partial cleanup when commands fail, old-kernel `max_comp_streams` behavior, missing compression algorithms, and echo-only failure reporting. Passing signals are successful sysfs writes, mounted or swap-enabled devices, and cleanup messages without leaked devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/zram/zram_lib.sh -->
