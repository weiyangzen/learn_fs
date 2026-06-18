<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/adfs/dir_f.c -->
# sources/distributed-fs/ceph-client/fs/adfs/dir_f.c

## Purpose
`dir_f.c` implements ADFS E/F format directory parsing, validation, iteration, entry update, and commit logic for fixed-size 2048-byte directories.

## Important APIs, types, and functions
Important helpers are `adfs_readval`, `adfs_writeval`, `adfs_dir_checkbyte`, `adfs_f_validate`, `adfs_f_read`, `adfs_dir2obj`, `adfs_obj2dir`, `__adfs_dir_get`, `adfs_f_setpos`, `adfs_f_getnext`, `adfs_f_iterate`, `adfs_f_update`, and `adfs_f_commit`. It exports `adfs_f_dir_ops`.

## Control flow
Read loads exactly `ADFS_NEWDIR_SIZE`, maps header/tail, validates magic names, sequence numbers, reserved fields, parent ID, and check byte. Iteration walks 77 fixed 26-byte entries until an empty name. Update locates an entry by indirect address, writes metadata fields back, and commit increments sequence numbers and recomputes the check byte.

## State and persistence
Runtime state is the loaded directory buffer and current byte position. Persistent state is fixed-format directory entries, header, tail, and check byte on disk.

## Dependencies and integration points
It depends on `dir_f.h` packed structures, common `adfs_dir_copyfrom/to`, object fixup, and buffer dirty/sync paths in `dir.c`.

## Risks and test signals
Risks include unaligned multi-byte value parsing, checkbyte correctness across multiple buffer heads, fixed entry count limits, and corrupt tail/header handling. Test signals include valid/corrupt F directories, empty entry termination, update/commit verification, and images with parent ID mismatches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/adfs/dir_f.c -->
