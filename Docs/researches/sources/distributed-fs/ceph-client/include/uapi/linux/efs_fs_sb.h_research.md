## sources/distributed-fs/ceph-client/include/uapi/linux/efs_fs_sb.h

Purpose: This header describes SGI EFS filesystem superblock values and in-memory summary fields. It supports parsing and mounting legacy IRIX EFS volumes.

Important APIs and types: `EFS_MAGIC`, `EFS_NEWMAGIC`, and `IS_EFS_MAGIC()` identify supported superblock magic values. `EFS_SUPER` and `EFS_ROOTINODE` define key filesystem locations. `struct efs_super` models the big-endian on-disk superblock with filesystem size, cylinder group layout, geometry, dirty flag, update time, names, bitmap location/size, free block/inode counters, replicated superblock, last inode allocation, expansion space, and checksum. `struct efs_sb_info` stores normalized in-memory mount information.

Control flow and state: Mount code reads the on-disk superblock, validates magic and checksum, converts big-endian fields, computes group and inode layout, then fills `efs_sb_info`. Runtime free counters and dirty state reflect filesystem metadata handling outside this header.

Persistence and dependencies: `struct efs_super` is persistent disk format. `struct efs_sb_info` is kernel memory state. The header depends on `<linux/types.h>` and `<linux/magic.h>`.

Integration points: It integrates with the EFS filesystem driver, block device reads, VFS mount code, and filesystem checking tools.

Risks and test signals: Risks include endian conversion mistakes, accepting invalid magic or checksum, dirty filesystem handling, reserved bytes not zero, and overflow from legacy geometry fields. Tests should mount known EFS images, reject corrupted magic/checksum, validate root inode lookup, compare free counters, and test big-endian field parsing on little-endian hosts.
