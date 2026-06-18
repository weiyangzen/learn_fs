# File Research: sources/block-storage/kvdo/vdo/pool-sysfs.h

Read completely: 19 lines.

This header declares the sysfs integration objects for VDO pool exposure: `vdo_directory_type`, `vdo_pool_stats_sysfs_ops`, and `vdo_pool_stats_attrs[]`.

Dependencies: Linux `struct kobj_type`, `struct sysfs_ops`, and `struct attribute`.

Research notes: this header is the narrow linkage point between the main pool sysfs directory and the separate statistics attribute implementation.
