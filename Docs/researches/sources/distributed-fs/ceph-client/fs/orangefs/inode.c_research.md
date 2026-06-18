## sources/distributed-fs/ceph-client/fs/orangefs/inode.c

### Purpose
This file implements OrangeFS inode operations and address-space operations: page-cache read/writeback, direct I/O dispatch, mmap write faults, setattr/getattr/permission/update-time, file attributes, and inode instantiation.

### Important APIs, types, and functions
- Writeback helpers: `orangefs_writepage_locked()`, `struct orangefs_writepages`, `orangefs_writepages_work()`, `orangefs_writepages_callback()`, and `orangefs_writepages()`.
- Read helpers: `orangefs_readahead()` and `orangefs_read_folio()`.
- Page-cache mutation helpers: `orangefs_write_begin()`, `orangefs_write_end()`, `orangefs_invalidate_folio()`, `orangefs_release_folio()`, `orangefs_free_folio()`, and `orangefs_launder_folio()`.
- I/O and mmap: `orangefs_direct_IO()` and `orangefs_page_mkwrite()`.
- Metadata: `orangefs_setattr_size()`, `__orangefs_setattr()`, `__orangefs_setattr_mode()`, `orangefs_setattr()`, `orangefs_getattr()`, `orangefs_permission()`, `orangefs_update_time()`, `orangefs_fileattr_get()`, and `orangefs_fileattr_set()`.
- Inode lifecycle: `orangefs_init_iops()`, `orangefs_handle_hash()`, `orangefs_set_inode()`, `orangefs_test_inode()`, `orangefs_iget()`, and `orangefs_new_inode()`.

### Control flow
Reads from page cache issue `wait_for_direct_io(READ)` from readahead or read_folio and mark folios uptodate. Writes attach a private `orangefs_write_range` to folios recording dirty range and caller credentials, mark dirty, then writeback batches adjacent folios with matching uid/gid into a single daemon I/O where possible. Direct I/O loops in bufmap-sized chunks and updates file size/time on success. Truncate refreshes size, adjusts page cache and `i_size`, sends `ORANGEFS_VFS_OP_TRUNCATE`, and marks ctime/mtime changes. New or looked-up inodes are keyed by OrangeFS fsid/khandle through `iget5_locked()` or `insert_inode_locked4()`, then populated by getattr and assigned file/dir/symlink operation tables.

### State and persistence behavior
Inode private state holds object references, xattr cache, attr cache metadata, mapping timeout, and folio dirty-range private data. Server-persistent changes happen through truncate, setattr writeback, xattr-backed file flags, ACL helpers, and data I/O upcalls. The page cache is treated as time-limited because other clients can mutate data.

### Dependencies and integration points
Depends on `file.c` for `wait_for_direct_io()`, `orangefs-utils.c` for getattr/setattr/xattrs/error mapping, `orangefs-bufmap.c` for I/O buffer sizing, POSIX ACL helpers, generic address-space helpers, and VFS inode/file/directory operation contracts. It exports operation vectors used by namei and superblock code.

### Risks
Folio private dirty ranges are complex: invalidation, mmap writes, laundering, and batched writeback must keep range/credentials correct. Writeback grouping by uid/gid affects permission semantics. Truncate intentionally reorders `truncate_setsize` steps and must recover cleanly from server failure. `orangefs_update_time()` may block and returns `-EAGAIN` for NOWAIT. Inode number hashing can collide, so iget uses handle comparison, but user-visible inode numbers are not globally unique beyond the hash.

### Test signals
Use xfstests for buffered writeback, mmap write faults, truncate extend/shrink, partial folio invalidation, direct I/O, readahead, writeback under memory pressure, chmod/chown/time updates, fileattr flags, ACL create inheritance, hard server/daemon errors, and stale inode detection.
