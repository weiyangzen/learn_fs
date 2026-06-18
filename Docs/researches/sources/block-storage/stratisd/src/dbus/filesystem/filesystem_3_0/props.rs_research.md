# File Research: sources/block-storage/stratisd/src/dbus/filesystem/filesystem_3_0/props.rs

Property accessors for filesystem D-Bus revisions.

Properties:
- `created_prop`: RFC3339 creation timestamp, seconds precision.
- `devnode_prop`: mountable filesystem path derived from pool and filesystem names.
- `name_prop`: filesystem name.
- `pool_prop`: parent pool object path from manager.
- `size_prop`: filesystem size as string.
- `used_prop`: optional used bytes as `(bool, String)`.
 
These helpers are reused across filesystem revision files.
