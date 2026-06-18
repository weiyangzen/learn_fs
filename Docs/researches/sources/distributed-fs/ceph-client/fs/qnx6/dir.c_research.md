# sources/distributed-fs/ceph-client/fs/qnx6/dir.c

## Purpose
`dir.c` implements QNX6 directory iteration and name lookup, including short names stored in directory entries and long names stored in the special longfile.

## Important APIs, types, and functions
Important functions are `qnx6_readdir`, `qnx6_find_ino`, `qnx6_dir_longfilename`, `qnx6_longname`, `qnx6_long_match`, `qnx6_match`, and `qnx6_lfile_checksum`. It exports `qnx6_dir_operations` and `qnx6_dir_inode_operations`.

## Control flow
Directory folios are read through the file mapping. Readdir aligns `ctx->pos`, walks fixed-size entries, emits short names directly, and resolves long names by reading the longfile block referenced by the directory entry. Lookup starts from the cached `i_dir_start_lookup` page, wraps around the directory, and returns the matching inode number.

## State and persistence
State is read-only. Runtime lookup acceleration stores the last successful page in `qnx6_inode_info.i_dir_start_lookup`; persistent names remain on disk.

## Dependencies and integration points
It depends on folio mapping APIs, QNX6 endian helpers, longfile private inode, VFS dir context, and checksum behavior that differs for `mmi_fs`.

## Risks and test signals
Risks include the `last_entry` byte/entry calculation, long filename folio offset math, checksum warnings not rejecting names, stale lookup hint, and malformed `de_size`. Test signals include short names, long names, MMI and non-MMI checksums, lookup wraparound, interrupted `dir_emit`, and corrupt longfile pointers.
