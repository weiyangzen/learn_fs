# sources/distributed-fs/ceph-client/fs/befs/datastream.h

Purpose: exposes BeFS datastream block mapping and read helpers to VFS and B+tree code.

Important APIs/types/functions: declarations for `befs_read_datastream`, `befs_fblock2brun`, `befs_read_lsymlink`, `befs_count_blocks`, and `BAD_IADDR`.

Control flow: callers use these functions to map file logical blocks, read arbitrary datastream positions, read long symlink content, and compute inode `i_blocks`.

State and persistence: no state in the header; all state is in caller-provided datastreams and returned buffer_heads.

Dependencies and integration: bridges `linuxvfs.c`, `btree.c`, and `datastream.c`.

Risks: caller ownership of returned buffer_heads must be respected; BeFS return codes are not Linux errnos.

Test signals: compile and mount coverage for regular file reads, B+tree directory operations, and long symlinks.
