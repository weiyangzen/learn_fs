# sources/distributed-fs/ceph-client/fs/zonefs/super.c

## Purpose
`zonefs/super.c` implements zonefs mount, superblock validation, zone discovery, inode and directory synthesis, mount options, error recovery, statfs, and module registration.

## Important APIs, types, and functions
Important exported functions are `zonefs_inode_account_active`, `zonefs_inode_zone_mgmt`, `zonefs_i_size_write`, `zonefs_update_stats`, `__zonefs_io_error`, `zonefs_dir_inode_operations`, and `zonefs_dir_operations`. Internal paths include superblock CRC validation, fs_context parsing, zone report callbacks, zone group initialization, lookup/readdir, inode allocation cache, fill/kill super, and filesystem registration.

## Control flow
Mount verifies the block device is zoned, allocates `zonefs_sb_info`, sets block size to zone write granularity, reads and checks the on-disk zonefs superblock, applies feature flags, reports all zones, groups them into `cnv` and `seq` directories, optionally aggregates contiguous conventional zones, closes initially open sequential zones, creates the synthetic root and group directory inodes, and registers sysfs. Lookup parses numeric names inside group directories and uses sector-derived inode numbers. IO errors re-report the affected zone, update readonly/offline flags and inode modes, correct inode size/write pointer, and optionally remount read-only.

## State and persistence
Persistent state is the 4 KiB `struct zonefs_super` at block 0 with magic, crc, label, uuid, feature flags, uid/gid/permissions. Most file state is reconstructed from block zone reports at mount. Runtime state includes zone arrays, active/write-open counters, mount options, stats block counts, and sysfs kobject state.

## Dependencies and integration points
The file integrates with fs_context, block zone reporting/management, VFS inode/dentry/directory operations, iomap file ops from `file.c`, sysfs, CRC32, slab caches, quota transfer on setattr, and tracepoint definition.

## Risks and test signals
Risks include invalid zone reports, feature incompatibility, aggregated conventional zone condition handling, active/open counter drift, inode number collisions, mount option reconfigure behavior, IO-error policy confusion, readonly/offline mode transitions, and cleanup after partial mount failure. Test signals include malformed superblocks, unknown features, devices with mixed zone types, explicit-open limits, errors= modes, lookup/readdir correctness, setattr/truncate, remount option changes, and mount/unmount leak checks.
