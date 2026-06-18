# File Research: sources/block-storage/stratisd/src/dbus/blockdev/blockdev_3_0/props.rs

Property accessors for blockdev D-Bus revisions.

Properties:
- `devnode_prop`: returns metadata path.
- `hardware_info_prop`: optional hardware info as D-Bus `(bool, String)`.
- `init_time_prop`: initialization timestamp as `u64`.
- `physical_path_prop`: actual device node path.
- `pool_prop`: resolves parent pool object path from manager.
- `total_physical_size_prop`: device size in bytes as string.
- `tier_prop`: data/cache tier as `u16`.
- `user_info_prop`: optional user info as `(bool, String)`.

These functions are reused by later blockdev revisions.
