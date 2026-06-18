# sources/distributed-fs/ceph-client/fs/squashfs/dir.c

## Purpose

`dir.c` implements directory iteration for SquashFS. It decodes packed directory metadata, synthesizes `"."` and `".."`, optionally uses long-directory indexes to skip near the current position, and emits VFS directory entries.

## Important APIs, Types, and Functions

The exported object is `squashfs_dir_ops`. Internal helpers are `get_dir_index_using_offset()` and `squashfs_readdir()`. It uses `struct squashfs_dir_header`, `struct squashfs_dir_entry`, `struct dir_context`, and the file-type translation table.

## Control Flow

`squashfs_readdir()` allocates a max-size directory entry buffer, emits synthetic dot entries while `ctx->pos < 3`, uses the directory index to locate the metadata block for the requested position, then loops over directory headers and entries. It validates counts, name sizes, and type values before calling `dir_emit()`.

## State and Persistence Behavior

Directory iteration state is `ctx->pos`; no persistent mutable filesystem state is changed. On-disk directory positions are offset by 3 externally because dot entries are synthetic.

## Dependencies and Integration Points

It depends on `squashfs_read_metadata()`, directory fields stored in `squashfs_inode_info`, and VFS directory operation hooks. `inode.c` assigns `squashfs_dir_ops` to directory inodes.

## Risks and Edge Cases

Malformed directory counts, oversized names, bad types, or read errors cause iteration to stop with an error log but return 0 to userspace. Position translation around synthetic dot entries is subtle.

## Test Signals

Run `find`, `ls -la`, telldir/seekdir-style tests, large indexed directories, corrupted directory metadata images, and short-buffer directory iteration tests.
