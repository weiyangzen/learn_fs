# sources/distributed-fs/ceph-client/fs/freevxfs/vxfs_dir.h

## Purpose

`sources/distributed-fs/ceph-client/fs/freevxfs/vxfs_dir.h` defines FreeVxFS on-disk directory block and entry formats plus record-size helpers. The complete 68-line file was read for this report.

## Important APIs, Types, and Functions

Key definitions are `struct vxfs_dirblk`, `struct vxfs_direct`, `VXFS_NAMELEN`, `VXFS_DIRPAD`, `VXFS_NAMEMIN`, `VXFS_DIRROUND()`, `VXFS_DIRLEN()`, and `VXFS_DIRBLKOV()`.

## Control Flow

The header has no runtime flow. `vxfs_lookup.c` uses these layouts to skip the per-block hash/free-space header, walk variable-length directory entries, compare names, and emit directory entries to VFS.

## State and Persistence Behavior

The structures model on-disk directory records. `d_ino`, `d_reclen`, `d_namelen`, and `d_hashnext` are endian-tagged fields read through the superblock byte-order helpers.

## Dependencies and Integration Points

The file depends on `fs16_to_cpu()` for the `VXFS_DIRBLKOV()` macro and integrates directly with directory lookup/readdir page walking.

## Risks and Edge Cases

Malformed `d_nhash`, `d_reclen`, or `d_namelen` fields can affect directory scanning because the implementation performs little structural validation. Name length is capped at 256 bytes, matching the fixed `d_name` array.

## Test Signals

Signals include directory images with empty entries, long names, block-boundary entries, hash overhead variations, zero record-length terminators, and fuzzed directory blocks.
