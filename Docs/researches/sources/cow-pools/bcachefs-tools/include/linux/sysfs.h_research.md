# File Research: sources/cow-pools/bcachefs-tools/include/linux/sysfs.h

Declares sysfs compatibility structures: `attribute`, `attribute_group`, `bin_attribute`, and `sysfs_ops`. It exposes create/remove functions for normal and binary files; link operations are no-op stubs.

The backing in-memory sysfs/debugfs behavior is implemented in `linux/kobject.c`.
