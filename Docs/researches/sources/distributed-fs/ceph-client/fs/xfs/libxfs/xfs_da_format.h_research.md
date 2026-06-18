# sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_da_format.h

## Purpose
`xfs_da_format.h` defines the persistent on-disk format for XFS directory and attribute blocks that share the DA btree framework. It covers v2 and CRC-enabled v3 block headers, directory shortform/data/leaf/free/block layouts, attribute shortform/leaf/remote layouts, filetype and attr flag constants, and inline layout accessors.

## Important APIs, Types, And Functions
DA btree definitions include `struct xfs_da_blkinfo`, `struct xfs_da3_blkinfo`, node magic constants, `struct xfs_da_node_hdr`, `struct xfs_da3_node_hdr`, `struct xfs_da_node_entry`, and `XFS_DA_NODE_MAXDEPTH`.

Directory definitions include magic constants for block/data/free/leaf formats, filetype constants, `struct xfs_dir2_sf_hdr`, `struct xfs_dir2_sf_entry`, data block headers, active and unused data entries, leaf and free block headers, and block-tail helpers such as `xfs_dir2_block_leaf_p()` and `xfs_dir2_leaf_bests_p()`. Offset/dataptr/db types and constants define the directory's three large logical spaces: data, leaf, and free.

Attribute definitions include shortform headers/entries, leaf headers, free maps, local and remote name/value records, v3 leaf headers, attr namespace/incomplete flags, leaf entry size helpers, remote attr block headers, and the parent pointer value record `struct xfs_parent_rec`.

## Control Flow
The header is mostly declarative. Inline helpers compute variable-layout offsets and sizes for shortform directories, block tails, leaf bests, attr local/remote entries, and directory block bytes. These helpers are part of the control path for all readers and writers because the on-disk structures contain flex arrays and packed variable-length records.

## State And Persistence
Everything in this file is either on-disk metadata or a constant used to interpret on-disk metadata. v3 headers persist CRC, LSN, uuid, owner, and block-number fields. Directory data entries persist inode numbers, names, filetypes, and back-tags; unused entries persist free tags and lengths. Attribute leaf entries persist hashes, name indexes, namespace/local/incomplete flags, local values, or remote value extents. Parent pointer attributes persist parent inode and generation in the attr value.

## Dependencies And Integration Points
This format header is consumed by DA btree, directory shortform/data/block/leaf/node code, attr leaf/remote code, parent pointer code, buffer verifiers, repair/scrub code, and userspace tools that must match kernel layout. It depends on XFS endian types, UUIDs, block/inode types, and geometry from the mount code.

## Risks
Layout drift is the highest risk. The comments around flex-array conversion in attr local/remote records document historically encoded padding; changing `xfs_attr_leaf_entsize_*()` would break existing filesystems. Endian mistakes, incorrect v2/v3 header-size selection, filetype values beyond `XFS_DIR3_FT_MAX`, or malformed free/tag offsets can lead to silent directory or xattr corruption. The attr incomplete bit is crash-recovery visible and must preserve atomicity of large attr updates.

## Test Signals
Tests should validate exact structure sizes/offsets on multiple architectures, v2 and v3 directory/attr images, shortform inode-number width transitions, directory entry filetype round trips, attr local/remote size calculations after flex-array changes, free-space tag verification, remote attr header CRC/owner checks, and parent pointer attr hash/value decoding.
