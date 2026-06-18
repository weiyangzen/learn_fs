# sources/distributed-fs/ceph-client/fs/ntfs/dir.c

Purpose: implements NTFS directory lookup, directory iteration, empty-directory checks, directory open/release, and directory fsync for the kernel NTFS driver.

Important APIs and functions:
- `I30` is the global little-endian `$I30` index name used for normal directory filename indexes.
- `ntfs_lookup_inode_by_name()` searches a directory B+tree by Unicode name and returns an MFT reference. It also returns a `struct ntfs_name` for case-insensitive or DOS-name alias handling by namei.
- `ntfs_readdir()` is the `.iterate_shared` implementation. It emits dot entries, walks the `$I30` index with `ntfs_index_*()` helpers, resumes from a saved key in `file->private_data`, and builds MFT readahead ranges.
- `ntfs_check_empty_dir()` treats a directory as empty only when `$INDEX_ROOT` has exactly the root plus terminal entry shape.
- `ntfs_dir_fsync()` writes parent directory indexes, this directory's bitmap/index allocation metadata, MFT bitmaps, LCN bitmap, MFT, and the block device.
- `ntfs_dir_ops` wires VFS directory operations and shares ioctl handling with regular files.

Control flow:
- Lookup maps the directory MFT record, opens `$INDEX_ROOT/$I30`, scans root entries with bounds and consistency checks, keeps the first valid case-insensitive candidate, and uses NTFS collation to decide whether to descend into a child VCN.
- When lookup descends, it opens the index allocation inode, reads the target page, copies it to temporary memory, applies MST post-read fixups, validates the `INDX` record, scans entries, and either returns a match, descends again, returns the cached case-insensitive match, or returns `-ENOENT`.
- Readdir initializes an `ntfs_index_context`, optionally seeks by the saved key with `ntfs_index_lookup()`, otherwise starts at index root and walks to the leftmost child. It emits entries through `ntfs_filldir()` and stores the current key when the caller's dirent buffer fills.
- Readdir accumulates contiguous MFT page indexes in an rb-tree and performs synchronous readahead on the MFT inode after iteration.
- Directory fsync first finds all parent directories from `AT_FILE_NAME` attributes and writes their `$I30` allocation inodes, then waits data pages and writes local bitmap/index/MFT metadata.

State and persistence behavior:
- Lookup allocates `struct ntfs_name` only when dcache alias handling is needed; error exits free it and clear `*res`.
- `struct ntfs_file_private` stores a serialized index key, key length, end marker, and current logical position across `readdir()` calls.
- Directory iteration logical offsets are synthetic sums of index entry lengths after dot entries, not byte offsets in a single file.
- Index allocation reads use page cache folios but copy one page into `kaddr` before applying MST fixups, avoiding modification of cached data during lookup.
- `ntfs_dir_fsync()` explicitly persists parent indexes, local bitmap attributes, volume allocation bitmaps, the MFT, and the block device.

Dependencies and integration points:
- Depends on `mft.h`, `ntfs.h`, `index.h`, and `reparse.h`.
- Uses `ntfs_index_entry_inconsistent()`, `ntfs_index_ctx_get()`, `ntfs_index_lookup()`, `ntfs_index_walk_down()`, and `ntfs_index_next()` from `index.c`.
- Uses VFS directory helpers `dir_emit_dots()`, `dir_emit()`, `generic_read_dir`, `generic_file_llseek`, and `generic_setlease`.
- Reparse tags are converted to directory entry types by `ntfs_reparse_tag_dt_types()`.
- Parent directory syncing relies on `ntfs_iget()` and `ntfs_index_iget()` from inode handling.

Risks and edge cases:
- Directory corruption checks are extensive, but several paths collapse to `-EIO`; tests need to distinguish corruption from lookup miss.
- Lookup assumes index blocks do not cross page boundaries and refuses larger-than-page index blocks.
- The rb-tree readahead merge condition has suspicious `!cnir->start_index && cnir->start_index - 1 == index` checks; with unsigned arithmetic this likely never expresses the intended predecessor merge except at wraparound.
- Readdir masks internal errors to `0` after setting `end_in_iterate`, which prevents userspace from seeing some corruption or allocation failures.
- Directory fsync loops parent `AT_FILE_NAME` attributes and skips failures to open parents or index allocation inodes, so sync may be best-effort for damaged hardlink metadata.

Test signals:
- Lookup tests should cover exact-case match, case-insensitive match, DOS short-name match, duplicate insensitive names as corruption, child-node descent, and corrupted bounds.
- Readdir tests should cover resume after small dirent buffers, hidden/system filtering, reparse point d_type, large index traversal, and non-monotonic `actor->pos`.
- Fsync tests should verify parent `$I30`, local `$BITMAP/$INDEX_ALLOCATION`, MFT bitmap, LCN bitmap, and block flush calls after directory mutations.
