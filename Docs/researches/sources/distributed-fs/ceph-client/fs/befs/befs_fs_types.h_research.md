# sources/distributed-fs/ceph-client/fs/befs/befs_fs_types.h

Purpose: describes BeFS on-disk structures, constants, bitwise filesystem integer types, superblock/inode flags, datastream layout, and B+tree node/superblock formats.

Important APIs/types/functions: `befs_disk_block_run`, `befs_block_run`, `befs_super_block`, `befs_disk_data_stream`, `befs_data_stream`, `befs_inode`, `befs_disk_btree_super`, `befs_btree_super`, `befs_btree_nodehead`, and `befs_host_btree_nodehead`.

Control flow: parsing code in `super.c`, `inode.c`, `datastream.c`, and `btree.c` reads these packed disk structures and converts fields through `endian.h`.

State and persistence: this file is the persistent contract for BeFS volumes: magic values, byte order, allocation group runs, inode data, inline symlink storage, long symlink datastreams, and directory/index B+trees.

Dependencies and integration: uses Linux fixed-width types and `__bitwise` filesystem-endian wrappers to prevent accidental host-endian use.

Risks: packed structure definitions must match disk layout exactly. B+tree and double-indirect constants influence read bounds and can corrupt lookup if changed incorrectly.

Test signals: sparse/endianness builds, mounting little- and big-endian BeFS images, checking directory B+tree traversal and long symlink reads.
