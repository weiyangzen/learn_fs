# File Research: sources/block-storage/kvdo/vdo/uds-sysfs.h

This header declares UDS sysfs lifecycle functions:
- `uds_init_sysfs()` initializes the `/sys/<module_name>` tree and returns `0` or a kernel error.
- `uds_put_sysfs()` tears the tree down during module unload.
