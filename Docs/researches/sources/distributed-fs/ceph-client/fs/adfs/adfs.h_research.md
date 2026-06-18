<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/adfs/adfs.h -->
# sources/distributed-fs/ceph-client/fs/adfs/adfs.h

## Purpose
`adfs.h` is the internal ADFS filesystem header defining in-memory inode/superblock/directory state, directory operation abstraction, object metadata, map helpers, and cross-file declarations.

## Important APIs, types, and functions
Key types are `struct adfs_inode_info`, `struct adfs_sb_info`, `struct adfs_dir`, `struct object_info`, `struct adfs_dir_ops`, and `struct adfs_discmap`. Important helpers include `ADFS_I`, `ADFS_SB`, `adfs_filetype`, `adfs_inode_is_stamped`, `__adfs_block_map`, `adfs_map_discrecord`, and `adfs_disc_size`.

## Control flow
The header establishes polymorphic directory operations through `adfs_dir_ops`, allowing common directory code to call F or F+ implementations. Block mapping translates object indirect addresses and logical block offsets into physical sectors through the disc map.

## State and persistence
It defines runtime inode metadata copied from ADFS objects, superblock mount settings and map pointers, loaded directory buffers, and disc map buffer heads. Persistent state is the on-disk ADFS structures referenced by these fields.

## Dependencies and integration points
It depends on buffer heads, VFS inode/superblock structures, Linux ADFS disk-format headers, and map/inode/file/super source files.

## Risks and test signals
Risks include indirect address arithmetic, endian/packed structure assumptions, max name length handling, and union lifetime during shutdown. Test signals include mounting F and F+ images, filetype suffix option, block map lookup, and inode metadata conversion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/adfs/adfs.h -->
