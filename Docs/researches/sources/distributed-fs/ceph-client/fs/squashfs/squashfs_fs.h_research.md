# sources/distributed-fs/ceph-client/fs/squashfs/squashfs_fs.h

## Purpose

This header defines the SquashFS on-disk format constants, table indexing macros, compression IDs, packed inode/directory/fragment/xattr structures, and metadata index cache structures.

## Important APIs, Types, and Functions

Important constants include version numbers, metadata size, device block size, max file block size/log, name length, inode type IDs, xattr type IDs, compression IDs, and invalid sentinel values. Important macros decode compressed-size bits, inode block/offset, fragment/id/lookup/xattr table addressing, and meta-index dimensions. Important structs include `meta_entry`, `meta_index`, `squashfs_super_block`, all inode variants, `squashfs_dir_index`, `squashfs_dir_entry`, `squashfs_dir_header`, `squashfs_fragment_entry`, `squashfs_xattr_entry`, `squashfs_xattr_val`, `squashfs_xattr_id`, and `squashfs_xattr_id_table`.

## Control Flow

The only inline executable helper is `squashfs_block_size()`, which rejects impossible encoded block sizes and returns a CPU-endian value. The rest defines the layout consumed by mount, inode, directory, file, fragment, id, export, and xattr code.

## State and Persistence Behavior

The structs mirror persistent on-disk SquashFS metadata. They are read-only when mounted. `meta_index` is in-memory cache state derived from file block lists.

## Dependencies and Integration Points

Included by all SquashFS modules and by superblock/private-state headers. Any format change must remain compatible with SquashFS tools and existing images.

## Risks and Edge Cases

This is ABI-critical. Field order, endian annotations, and size macros must match disk format. Size arithmetic must avoid overflow for large xattr/inode counts and table lengths.

## Test Signals

Mount known-good images from squashfs-tools, fuzz/corruption tests around table sizes and block-size fields, endian-build coverage, and compile-time layout review for format changes.
