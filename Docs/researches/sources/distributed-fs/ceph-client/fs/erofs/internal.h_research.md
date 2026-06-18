<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/erofs/internal.h -->
# sources/distributed-fs/ceph-client/fs/erofs/internal.h

## Purpose
`internal.h` defines EROFS in-kernel private structures, mount options, feature helpers, mapping types, operation declarations, and compile-time stubs for optional subsystems.

## Important APIs, types, and functions
Key types include `struct erofs_device_info`, `struct erofs_mount_opts`, `struct erofs_dev_context`, `struct erofs_sb_info`, `struct erofs_buf`, `struct erofs_inode`, `struct erofs_map_blocks`, and `struct erofs_map_dev`. It declares core operations, aops/fops/iops, mapping/read helpers, decompression lifecycle, fscache/fileio hooks, inode-share hooks, ioctl helpers, and feature-test inline functions.

## Control flow
The header has no direct runtime flow. It routes call sites through inline feature checks such as fileio/fscache mode and `erofs_get_aops`, which selects compressed, fscache, file-backed, or normal address-space operations. Optional features compile to real declarations or no-op/error stubs.

## State and persistence
It defines runtime superblock and inode state for devices, compression, xattrs, metabox, packed inode, sysfs, fscache domains, page-cache sharing, and mount flags. Persistent disk state is referenced through fields decoded from `erofs_fs.h`.

## Dependencies and integration points
It depends on VFS, DAX, bio, pagemap, iomap, xarray, module, and EROFS on-disk definitions. Every EROFS implementation file includes it, making it the central internal ABI.

## Risks and test signals
Risks include feature-stub mismatches, stale declarations, incorrect aops selection when modes combine, and struct field assumptions across optional configs. Test signals include compile matrices for every optional feature, normal/compressed/fileio/fscache address-space selection, multi-device map resolution, and mount option bit behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/erofs/internal.h -->
