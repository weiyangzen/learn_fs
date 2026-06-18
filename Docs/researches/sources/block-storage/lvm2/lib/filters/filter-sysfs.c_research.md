# File Research: sources/block-storage/lvm2/lib/filters/filter-sysfs.c

This Linux-only filter rejects devices that do not have a corresponding sysfs block entry. `_accept_p` clears `DEV_FILTERED_SYSFS`, passes devices whose non-devname IDs already imply sysfs discovery, then checks `<sysfs_dir>/dev/block/<major>:<minor>` with `lstat`.

If sysfs path construction fails, the filter passes rather than rejecting on an internal formatting problem. If the sysfs entry is absent, it marks `DEV_FILTERED_SYSFS` and rejects the device.

`sysfs_filter_create` requires a configured sysfs directory and verifies that `/sys/dev/block` exists for old-kernel compatibility. It allocates one object containing both the filter and a trailing copy of the sysfs directory string, stores that string in `private`, and names the filter `sysfs`. Non-Linux builds return `NULL`.
