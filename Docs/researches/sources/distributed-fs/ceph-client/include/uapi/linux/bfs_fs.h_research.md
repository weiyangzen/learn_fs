# sources/distributed-fs/ceph-client/include/uapi/linux/bfs_fs.h

## Purpose

`sources/distributed-fs/ceph-client/include/uapi/linux/bfs_fs.h` exports the on-disk BFS filesystem layout and helper macros. The complete 82-line header was read. It defines block sizing, magic values, inode and directory layouts, superblock layout, and arithmetic for translating between BFS inode numbers, offsets, file sizes, and dirty-state checks.

## Important APIs, Types, and Functions

There are no functions. Important constants include `BFS_BSIZE_BITS`, `BFS_BSIZE`, `BFS_MAGIC`, `BFS_ROOT_INO`, `BFS_INODES_PER_BLOCK`, `BFS_VDIR`, `BFS_VREG`, `BFS_NAMELEN`, `BFS_DIRENT_SIZE`, and `BFS_DIRS_PER_BLOCK`. Important structs are `struct bfs_inode`, `struct bfs_dirent`, and `struct bfs_super_block`. Macros include `BFS_OFF2INO`, `BFS_INO2OFF`, `BFS_NZFILESIZE`, `BFS_FILESIZE`, `BFS_FILEBLOCKS`, and `BFS_UNCLEAN`.

## Control Flow

The header has no executable flow, but it encodes filesystem traversal arithmetic. Mount and fsck-like code read `bfs_super_block`, confirm `BFS_MAGIC`, map inode numbers to disk offsets with `BFS_INO2OFF`, read `bfs_inode` entries, compute file size/block count from start/end fields, and iterate fixed-size directory entries containing a little-endian inode and 14-byte name.

## State and Persistence Behavior

The main state is persistent on disk. Inodes, directory entries, and the superblock are stored in little-endian form. Runtime callers convert fields with `le32_to_cpu()` before arithmetic. `BFS_UNCLEAN` describes mount-time dirty state by comparing `s_from` and `s_to` to `-1` and checking that the VFS superblock is not read-only.

## Dependencies and Integration Points

The only direct include is `<linux/types.h>`, but some macros assume conversion helpers such as `le32_to_cpu()` and VFS flag `SB_RDONLY` are visible from the including kernel context. Integration points are the BFS filesystem driver, filesystem check/repair utilities, and any tool that reads raw BFS images.

## Risks and Edge Cases

This is an on-disk ABI. Changing struct fields or padding would break existing images. `BFS_NZFILESIZE` subtracts a block-derived start offset from `i_eoffset + 1`; corrupted images can underflow or overflow if callers do not validate block ranges. Directory names are fixed 14-byte arrays and may not behave like C strings. `BFS_UNCLEAN` mixes little-endian superblock fields and VFS state, so it is not a pure UAPI helper for standalone userspace without equivalent constants.

## Test Signals

Useful signals include mounting known BFS images, fsck parsing of clean and unclean superblocks, endian/offset tests for `BFS_OFF2INO` and `BFS_INO2OFF`, corrupt-image tests with invalid block ranges and names, and structure size/offset checks against historical BFS disk images.
