# sources/distributed-fs/ceph-client/fs/affs/amigaffs.h

## Purpose
`amigaffs.h` documents and defines AFFS on-disk constants and structures, including filesystem signatures, block primary/secondary types, root/header/tail/data layouts, symlink front matter, Amiga timestamps, and protection bits.

## Important APIs, types, and functions
Important definitions include `FS_OFS`, `FS_FFS`, international and dircache variants, MUFS variants, `T_SHORT`, `T_LIST`, `T_DATA`, `ST_FILE`, `ST_USERDIR`, `ST_SOFTLINK`, `ST_LINKFILE`, `ST_ROOT`, `AFFS_ROOT_BMAPS`, `AFFS_EPOCH_DELTA`, `struct affs_date`, `struct affs_root_head`, `struct affs_root_tail`, `struct affs_head`, `struct affs_tail`, `struct slink_front`, and `struct affs_data_head`.

## Control flow
The file is declarative; other AFFS code casts buffer contents through these structures to locate hash tables, tails, bitmap references, names, link chains, extension pointers, and OFS data headers.

## State and persistence
All structures describe persistent big-endian media state. Protection macros encode classic inverted owner bits and extended group/other bits.

## Dependencies and integration points
It depends on Linux fixed-width/big-endian types and is consumed by `affs.h` and all metadata code.

## Risks and test signals
Risks include struct layout drift, incorrect tail positioning for different block sizes, endian mistakes, and misinterpreting dircache/MUFS signatures. Test signals include mounting every supported signature, checksum over block casts, symlink read/write, OFS data block parsing, bitmap-root parsing, and permission conversion tests.
