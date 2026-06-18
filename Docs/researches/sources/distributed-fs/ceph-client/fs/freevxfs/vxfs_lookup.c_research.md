# sources/distributed-fs/ceph-client/fs/freevxfs/vxfs_lookup.c

## Purpose

`sources/distributed-fs/ceph-client/fs/freevxfs/vxfs_lookup.c` implements FreeVxFS directory lookup and readdir support. It walks VxFS directory pages, finds matching directory entries, and exposes directory operations to VFS. The complete 273-line file was read for this report.

## Important APIs, Types, and Functions

External operation tables are `vxfs_dir_inode_ops` and `vxfs_dir_operations`. Internal functions are `vxfs_find_entry()`, `vxfs_inode_by_name()`, `vxfs_lookup()`, and `vxfs_readdir()`.

## Control Flow

Lookup checks name length, scans directory pages with `vxfs_find_entry()`, extracts the found inode number, loads the target with `vxfs_iget()`, and returns through `d_splice_alias()`. Directory scanning emits `.` and `..` first, then walks entries from `ctx->pos`, skips per-block directory headers, advances by `d_reclen`, ignores deleted entries with zero inode, and calls `dir_emit()` with `DT_UNKNOWN`.

## State and Persistence Behavior

Directory state is read-only on-disk directory blocks exposed through pagecache. `ctx->pos` is the persistent userspace iteration cursor for an open directory stream. No directory modifications are supported.

## Dependencies and Integration Points

The code uses `vxfs_get_page()`/`vxfs_put_page()`, directory layout macros from `vxfs_dir.h`, byte-order helpers from `vxfs.h`, inode lookup from `vxfs_inode.c`, and generic VFS directory helpers including `generic_file_llseek`, `generic_read_dir`, and `generic_setlease`.

## Risks and Edge Cases

Malformed directory records can affect scanning because `d_reclen` and header overhead are trusted after minimal checks. The code returns `-ENOMEM` for any page read error in readdir, losing the original error. `vxfs_inode_by_name()` manually does `kunmap()` and `put_page()` rather than `vxfs_put_page()`, so consistency is worth preserving.

## Test Signals

Tests should cover lookup hits/misses, long names, empty directories, deleted entries, entries spanning page/block boundaries, stable `telldir`/`seekdir` behavior, corrupt zero or oversized record lengths, and directory fuzzing under KASAN.
