# File Research: sources/block-storage/bcache-tools/lib.h

This header defines the in-memory summary structs used by the CLI: generic `struct dev`, backing-specific `struct bdev`, and cache-specific `struct cdev`. It declares list/detail/sysfs mutation helpers, superblock conversion helpers, bucket-size setup, device-list cleanup, and label encoding helpers.

Constants define display strings such as `N/A`, `active`, `inactive`, `Alone`, `Non-Exist`, and the `/dev/` prefix length used by path trimming.
