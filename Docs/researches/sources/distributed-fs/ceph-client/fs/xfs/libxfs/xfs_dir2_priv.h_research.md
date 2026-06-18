# sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_dir2_priv.h

## Purpose
`xfs_dir2_priv.h` is the private interface shared by XFS directory v2/v3 implementation files. It centralizes in-core header abstractions, cross-file prototypes, and small sizing/hash helpers needed by shortform, block, data, leaf, node, and readdir code.

## Important APIs, Types, and Functions
The header defines `struct xfs_dir3_icleaf_hdr` and `struct xfs_dir3_icfree_hdr`, which normalize v4 and v5 on-disk leaf/free headers into host-endian fields plus pointers to the on-disk entry arrays. It declares directory hash and comparison helpers, block-format operations, data-block verifier/free-space helpers, leaf-format operations, node-format operations, shortform operations, and `xfs_readdir`.

Inline helpers include `xfs_dir2_data_unusedsize`, which rounds unused-record length to directory alignment, and `xfs_dir2_data_entsize`, which computes active dirent size including inode, name, optional filetype byte, trailing tag, and alignment. The header also exposes `xfs_dir2_hashname` and `xfs_dir2_compname`, allowing code to use ASCII case-insensitive behavior when mounted that way.

## Control Flow and Integration
This file does not implement control flow directly, but it defines the coupling between implementation files. For example, leaf and node code call data helpers to consume/free data-block ranges; exchange-map post-operation conversion can call shortform conversion helpers; and block/leaf/node conversion routines depend on the declared APIs to move directories across formats.

## State and Persistence
The header describes state layouts indirectly through header abstractions and sizing functions. The in-core header structs are not separately persisted; they are decoded from and encoded back to on-disk buffers by implementation files. The inline size helpers must remain consistent with on-disk directory record layout because their outputs control parsing, allocation, and transaction log ranges.

## Dependencies and Integration Points
The declarations assume types from XFS mount, inode, transaction, DA args/state, buffer, directory format, and VFS directory iteration layers. It is included by many libxfs directory files and provides the private ABI that keeps those files independent of v4/v5 header differences.

## Risks and Test Signals
The main risk is contract drift: if an implementation changes a function signature or directory record layout without updating this header, callers can misparse directory buffers. The sizing helpers are especially critical because off-by-one or missing filetype/tag bytes would corrupt entry walking. Test signals include successful compilation across all directory implementation units, xfstests coverage for filesystems with and without ftype/CRC, and scrub/fsck validation after directory format conversions.
