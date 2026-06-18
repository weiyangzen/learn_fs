# sources/distributed-fs/ceph-client/fs/befs/super.h

Purpose: declares BeFS superblock load and validation helpers.

Important APIs/types/functions: `befs_load_sb` and `befs_check_sb`.

Control flow: used by `linuxvfs.c` during mount after raw superblock read.

State and persistence: no header state; interfaces operate on persistent disk superblocks and mounted `befs_sb_info`.

Dependencies and integration: connects `super.c` to the mount path.

Risks: callers must provide a raw superblock at the correct architecture-specific offset.

Test signals: compile and mount validation tests.
