# sources/distributed-fs/ceph-client/fs/squashfs/symlink.c

## Purpose

`symlink.c` implements symlink page-cache reads for SquashFS. Symlink targets are stored inline in inode-table metadata, not as separate file data blocks.

## Important APIs, Types, and Functions

Exports are `squashfs_symlink_aops` and `squashfs_symlink_inode_ops`. The main function is `squashfs_symlink_read_folio()`.

## Control Flow

The read function starts from the symlink metadata block/offset stored in `squashfs_inode_info`, optionally skips bytes for nonzero folio position, then loops through metadata cache entries copying bytes into the folio via `kmap_local_folio()`. When the requested target bytes are complete it zero-fills the rest of the page, flushes dcache, and completes the folio read.

## State and Persistence Behavior

The symlink target persists in compressed inode metadata; successful reads populate the page cache. No mutable filesystem state is changed.

## Dependencies and Integration Points

`inode.c` assigns these ops to symlink inodes after validating symlink size. It depends on metadata cache functions and `page_get_link`.

## Risks and Edge Cases

The code avoids `squashfs_read_metadata()` during mapped folio writes because that helper can sleep; direct cache access must still release entries correctly. Symlinks larger than a page are rejected in `inode.c`.

## Test Signals

Readlink tests for short and page-near symlinks, symlink metadata spanning compressed metadata blocks, corrupt metadata, and xattr listing on symlinks.
