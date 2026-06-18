# sources/distributed-fs/ceph-client/fs/zonefs/zonefs.h

## Purpose
`zonefs/zonefs.h` centralizes zonefs constants, on-disk format, in-memory zone/superblock structures, feature and mount option flags, helper accessors, logging macros, and cross-file declarations.

## Important APIs, types, and functions
It defines `enum zonefs_ztype`, `struct zonefs_zone`, `struct zonefs_zone_group`, `struct zonefs_inode_info`, `struct zonefs_super`, `enum zonefs_features`, mount option flags, and `struct zonefs_sb_info`. Inline helpers convert block zones to zonefs types, recover `ZONEFS_I` and `ZONEFS_SB`, test conventional/sequential zones, fetch an inode zone, wrap `zonefs_io_error`, and declare file, directory, super, and sysfs operations.

## Control flow
All zonefs C files use this header to share the same view of zone metadata and mount state. The on-disk superblock definition is size-checked at module init. Helpers guide file IO decisions, mount feature validation, and error handling.

## State and persistence
The persistent structure is `struct zonefs_super`, including magic, CRC, label, UUID, feature bits, optional UID/GID/permissions, and reserved padding. In-memory state tracks zone condition flags, write pointer offsets, per-group zone arrays, active/open counters, mount options, stats, and sysfs kobject lifetime.

## Dependencies and integration points
It integrates VFS inode/superblock types, block zoned definitions, UUIDs, kobjects, mutexes, and zonefs source files. It also encodes feature compatibility between mkzonefs format options and kernel mount behavior.

## Risks and test signals
Risks include on-disk structure layout drift, feature flag mismatch, incorrect mount option bit semantics, and lock-order assumptions around `i_truncate_mutex`. Test signals include `BUILD_BUG_ON` super size, endian/CRC mount tests, feature matrix mounts, and lockdep on truncate/IO paths.
