# File Research: sources/cow-pools/openzfs/module/os/linux/zfs/vdev_raidz.c

## Purpose

Linux kernel-parameter glue for selecting/reporting the active RAIDZ implementation.

## Behavior

- `param_get_raidz_impl()` writes the current RAIDZ implementation name/details into the supplied buffer by calling `vdev_raidz_impl_get(buf, PAGE_SIZE)`.
- `param_set_raidz_impl()` passes the requested value to `vdev_raidz_impl_set()` and returns its error code.

## Integration

The actual RAIDZ implementation selection logic is elsewhere. This file only adapts it to the Linux `zfs_kernel_param_t` get/set interface.
