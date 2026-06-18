<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/erofs/erofs_fs.h -->
# sources/distributed-fs/ceph-client/fs/erofs/erofs_fs.h

## Purpose
`erofs_fs.h` defines the EROFS on-disk format: superblock, device table, inode layouts, xattrs, chunk indexes, directory entries, compression config, compressed map headers, and compile-time layout checks.

## Important APIs, types, and functions
Key definitions include feature flags, `struct erofs_super_block`, inode datalayout enum, compact and extended inode structs, xattr headers/entries, `struct erofs_inode_chunk_index`, `struct erofs_dirent`, compression algorithm ids, algorithm config structs, `struct z_erofs_map_header`, `struct z_erofs_lcluster_index`, `struct z_erofs_extent`, and `erofs_check_ondisk_layout_definitions`.

## Control flow
The header has no runtime control flow, but mount and inode readers interpret every EROFS image through these structures and feature masks. Compile-time `BUILD_BUG_ON` checks ensure struct sizes and special bit placement remain stable.

## State and persistence
It describes persistent disk state: feature compatibility, block size, root nid, metadata starts, xattr starts, external devices, packed/metabox inode ids, inode contents, xattr filters, chunk maps, directories, and compressed cluster metadata.

## Dependencies and integration points
It is the local on-disk ABI consumed by `super.c`, `inode.c`, `data.c`, xattr code, zmap/zdata, and decompressor config parsing. It must stay compatible with userspace mkfs tooling and kernel documentation.

## Risks and test signals
Risks include ABI-breaking struct layout changes, feature flag aliasing, 48-bit address parsing mistakes, compression metadata version mismatches, and endian handling errors. Test signals include compile-time layout checks, mounts of images using each feature bit, big-endian/little-endian parsing tests, and fsck/mkfs interoperability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/erofs/erofs_fs.h -->
