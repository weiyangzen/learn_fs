# sources/distributed-fs/ceph-client/include/linux/hfs_common.h

## Purpose
`hfs_common.h` is a shared on-disk format header for HFS and HFS+ filesystem code. It defines magic values, fixed geometry constants, catalog/extents/attributes B-tree keys and records, Finder metadata structures, POSIX permission records, fork descriptors, and HFS+ volume header layout. The file is a schema contract: implementation files parse, validate, create, and update disk blocks using these packed big-endian structures.

## Important APIs, Types, And Functions
The header exports no callable functions, but its typedefs and structures are core APIs. Important items include `hfsplus_cnid`, `hfsplus_unichr`, `struct hfs_name`, `struct hfsplus_unistr`, `struct hfsplus_fork_raw`, `struct hfs_mdb`, `struct hfsplus_vh`, `struct hfs_cat_key`, `struct hfsplus_cat_key`, `struct hfs_ext_key`, `struct hfsplus_ext_key`, `hfs_cat_rec`, `hfsplus_cat_entry`, `struct hfsplus_attr_key`, and `hfsplus_attr_entry`. Constants such as `HFS_SUPER_MAGIC`, `HFSPLUS_VOLHEAD_SIG`, CNID constants, catalog record type constants, fork type constants, and B-tree attribute bits drive validation and dispatch.

## Control Flow And State
Control flow is implicit. Mount and B-tree code read sector or node buffers, compare signatures and type fields, choose a union member, and interpret offsets and key lengths based on HFS versus HFS+. Persistent state is entirely on disk: volume headers, MDB fields, B-tree headers, catalog nodes, extent records, fork sizes, file counts, folder counts, CNID allocation, xattr records, and finder metadata. All multibyte persistent values are big-endian or explicitly packed; callers must convert with endian helpers before arithmetic.

## Dependencies And Integration Points
This header depends on kernel integer and endian types supplied by Linux headers included by filesystem implementation files. It integrates with HFS/HFS+ superblock, catalog, extents, attributes, inode, and xattr code. It also bridges legacy Mac OS metadata (`FInfo`, `DInfo`, `FXInfo`, `DXInfo`) into Linux inode and xattr semantics.

## Risks
The main risks are structure packing drift, endian misuse, union member confusion, malformed key lengths, extent count overflow, and trusting disk-provided sizes. `HFSPLUS_MAX_INLINE_DATA_SIZE` and string length constants protect fixed node layouts only if callers validate lengths before copying. CNID and B-tree constants are externally persistent ABI values and cannot be changed without breaking filesystem compatibility.

## Test Signals
Useful tests include mounting HFS and HFS+ images, HFSX case-sensitive key behavior, malformed volume headers, bad B-tree node type/key length cases, catalog records for files/directories/threads, inline and forked xattrs, resource fork extents, hardlink/symlink creator/type mappings, and endian checks on known-good images.
