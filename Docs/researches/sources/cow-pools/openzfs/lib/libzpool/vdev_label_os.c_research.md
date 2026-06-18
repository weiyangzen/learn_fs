# File Research: sources/cow-pools/openzfs/lib/libzpool/vdev_label_os.c

Libzpool OS hook for checking reserved boot area usage during vdev attach/raidz expansion.

`vdev_check_boot_reserve()` currently always returns success. The comments explain that Linux has no known external reserved-area users, FreeBSD can use reserved boot areas for ZFS root from MBR, and current libzpool consumers cannot add disks to pools anyway.
