# Research: subset-b-005725

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ntfs/dir.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ntfs/dir.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ntfs/dir.h -->
# sources/distributed-fs/ceph-client/fs/ntfs/dir.h

Purpose: declares directory-facing NTFS interfaces and the alias-return structure shared by lookup/namei code.

Important APIs and types:
- `struct ntfs_name` carries an MFT reference, filename namespace type, Unicode length, and optional little-endian Unicode name bytes. It is packed because it mirrors compact on-disk name metadata for dcache alias resolution.
- `extern __le16 I30[5]` exposes the `$I30` Unicode index name used by directory and index code.
- `ntfs_lookup_inode_by_name()` is the directory name-to-MFT-reference lookup API.
- `ntfs_check_empty_dir()` verifies whether a directory MFT record contains only the empty index-root form.

Control flow and integration:
- `namei.c` callers use `ntfs_lookup_inode_by_name()` and inspect the optional `struct ntfs_name` result to avoid dcache aliases for DOS and case-insensitive names.
- Directory removal paths can call `ntfs_check_empty_dir()` before deleting directories.
- `I30` is shared with `index.c`, `inode.c`, `file.c`, and `ea.c` for directory index allocation and syncing.

State and persistence behavior:
- The header owns no persistence, but its APIs expose MFT references containing sequence numbers, so consumers can perform stale-reference checks.
- The flexible `name[]` member is caller-allocated by `dir.c`; users must free it according to lookup ownership rules.

Dependencies:
- Includes `inode.h` for `struct ntfs_inode` and NTFS inode state.
- Uses kernel little-endian integer types and NTFS MFT record declarations from included headers.

Risks and edge cases:
- `struct ntfs_name` packing and flexible array sizing must match allocations in `dir.c`; misuse can overread names.
- Callers must not treat the raw `u64` return as a signed integer without extracting the MFT record number, because error encoding uses NTFS MFT reference macros.

Test signals:
- Compile coverage should catch prototype drift.
- Lookup/namei tests should verify returned `struct ntfs_name` ownership and DOS-name behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ntfs/dir.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ntfs/ea.c -->
# sources/distributed-fs/ceph-client/fs/ntfs/ea.c

Purpose: implements NTFS extended attributes, Linux xattr handlers, WSL metadata EAs, DOS/NTFS attribute xattrs, and optional POSIX ACL storage.

Important APIs and functions:
- `ntfs_get_ea()` reads a named EA from `$EA_INFORMATION` plus `$EA`.
- `ntfs_set_ea()` creates, replaces, removes, and rewrites EA entries while maintaining packed EA size, query length, and `NEED_EA` counts.
- `ntfs_ea_get_wsl_inode()` and `ntfs_ea_set_wsl_inode()` map `$LXUID`, `$LXGID`, `$LXMOD`, and `$LXDEV` EAs to Linux uid/gid/mode/device state.
- `ntfs_listxattr()` lists EA names for VFS xattr enumeration.
- `ntfs_getxattr()` and `ntfs_setxattr()` implement generic xattr handlers including `system.dos_attrib`, `system.ntfs_attrib`, and `system.ntfs_attrib_be`.
- `ntfs_new_attr_flags()` changes sparse/compressed attribute flags for empty regular files by resizing the attribute record layout.
- Optional ACL functions store POSIX ACL xattrs in NTFS EAs and update WSL mode metadata.

Control flow:
- EA lookup iterates packed `struct ea_attr` records using `next_entry_offset`, validates record size/name/value bounds, and returns offset plus effective size.
- `ntfs_get_ea()` validates `NInoHasEA`, reads `$EA_INFORMATION`, bounds `ea_query_length` against `$EA`, and copies or sizes the value.
- `ntfs_set_ea()` creates `$EA_INFORMATION` when missing, removes or replaces an existing entry, writes updated metadata first, writes/truncates `$EA`, then appends the new aligned EA record if a value remains.
- DOS/NTFS xattr set operations update `ni->flags`, adjust write permissions from `FILE_ATTR_READONLY`, mark filename metadata dirty, and dirty the inode.
- ACL set converts ACLs to xattr blobs, writes/removes them as EAs, updates `i_mode` and `$LXMOD`, and rolls back the ACL xattr on WSL mode write failure.

State and persistence behavior:
- Writes use `ntfs_write_ea()`, which opens a fake attribute inode, calls `ntfs_inode_attr_pwrite()`, optionally truncates trailing old EA bytes, and marks the base MFT record dirty.
- `NInoHasEA` is updated based on remaining EA query size.
- Attribute flag changes mutate both on-disk `attr_record.flags` and in-memory NTFS inode flags/compression fields.
- xattr and ACL setters update ctime and call `mark_inode_dirty()`.
- WSL EA getters can overwrite Linux inode uid/gid/mode during inode load unless mount options already supplied uid/gid.

Dependencies and integration points:
- Depends on `layout.h`, `attrib.h`, `index.h`, `dir.h`, and `ea.h`.
- Uses inode attribute read/write helpers from `inode.c`.
- Integrates with VFS xattr and POSIX ACL APIs through `ntfs_xattr_handlers` and inode operation tables in `file.c`.
- Sparse/compressed flag changes depend on mapping pair sizing and `ntfs_attr_record_resize()`.

Risks and edge cases:
- `ntfs_set_ea()` writes `$EA_INFORMATION` before `$EA` in some removal paths; later failure can leave metadata inconsistent despite comments promising restore.
- Setting a generic xattr with `value == NULL` and nonzero size would be unsafe, though VFS normally controls this.
- `ntfs_new_attr_flags()` returns early when flags do not change without releasing the search context or unmapping the MFT record, which appears to leak resources.
- `ntfs_setxattr()` always updates ctime and dirties the inode even on failed set operations.
- EA list parsing trusts `ea_query_length` after top-level bounds and must reject malformed `next_entry_offset` loops.

Test signals:
- xattr tests should cover create/replace/remove, ERANGE sizing, malformed EA records, DOS/NTFS endian attributes, read-only bit mode interaction, and empty-EA cleanup.
- WSL tests should verify uid/gid/mode/device round trips and mount-option override behavior.
- ACL tests should cover default ACL rejection on non-directories, symlink rejection, chmod ACL update, and rollback on `$LXMOD` write failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ntfs/ea.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ntfs/ea.h -->
# sources/distributed-fs/ceph-client/fs/ntfs/ea.h

Purpose: declares the NTFS EA/xattr and ACL interface used by inode and file operation setup.

Important APIs and types:
- `NTFS_EA_UID`, `NTFS_EA_GID`, and `NTFS_EA_MODE` select which WSL metadata EAs should be written.
- `ntfs_xattr_handlers` is the exported VFS xattr handler table.
- `ntfs_ea_get_wsl_inode()` loads WSL uid/gid/mode/device metadata from EAs.
- `ntfs_ea_set_wsl_inode()` writes WSL metadata EAs and can return packed EA size.
- `ntfs_listxattr()` is the inode operation hook for listing xattrs.
- When `CONFIG_NTFS_FS_POSIX_ACL` is enabled, `ntfs_get_acl()`, `ntfs_set_acl()`, and `ntfs_init_acl()` are declared; otherwise get/set are `NULL`.

Control flow and integration:
- `inode.c` calls WSL EA helpers during inode load and metadata changes.
- `file.c` exposes `ntfs_listxattr` and ACL handlers through regular and special inode operations.
- `ea.c` owns all implementations behind this header.

State and persistence behavior:
- The header defines selection bits but no state. Persistence happens through `$EA_INFORMATION` and `$EA` writes in `ea.c`.
- ACL macro fallback means builds without POSIX ACL omit ACL operation hooks cleanly.

Dependencies:
- Requires NTFS inode and VFS type declarations from surrounding includes in consumers.
- Uses kernel `xattr_handler`, `dentry`, `inode`, `mnt_idmap`, `posix_acl`, `dev_t`, and endian types.

Risks and edge cases:
- Callers must hold the expected NTFS inode locks around WSL EA setters where required by implementation.
- The compile-time ACL `NULL` macros mean code must tolerate missing ACL handlers.

Test signals:
- Build matrix should cover `CONFIG_NTFS_FS_POSIX_ACL=y` and disabled cases.
- Metadata tests should verify chmod/chown update WSL EAs only for selected flags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ntfs/ea.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ntfs/file.c -->
# sources/distributed-fs/ceph-client/fs/ntfs/file.c

Purpose: provides VFS regular-file, symlink, and special-inode operations for NTFS, including open/release, fsync, getattr/setattr, buffered/direct I/O, mmap, ioctl, and fallocate-style range operations.

Important APIs and functions:
- `ntfs_file_ops`, `ntfs_file_inode_ops`, `ntfs_symlink_inode_operations`, and `ntfs_special_inode_operations` are the exported VFS operation tables.
- `ntfs_file_open()` rejects shutdown volumes, checks 32-bit page-cache limits, and enables nowait/direct-I/O capability flags.
- `ntfs_trim_prealloc()` trims unused preallocated sparse holes on last close for non-compressed files.
- `ntfs_file_fsync()` persists file data, base and extent MFT records, named nonresident attributes, parent directory indexes, MFT bitmap, LCN bitmap, MFT, and block device cache.
- `ntfs_setattr()` handles truncation, chmod/chown timestamps, readonly flag updates, POSIX ACL chmod, and WSL EA metadata.
- `ntfs_file_read_iter()` and `ntfs_file_write_iter()` dispatch to iomap buffered/direct I/O and compressed writes.
- `ntfs_ioctl()` handles shutdown, get/set volume label, and FITRIM.
- `ntfs_fallocate()` supports allocate, keep-size, punch-hole, collapse-range, and insert-range modes.

Control flow:
- Write path rejects shutdown/encrypted writes and direct I/O to compressed files, locks the inode or returns `-EAGAIN` for NOWAIT, performs generic write checks, marks the volume dirty, snapshots sizes, and dispatches to compressed, direct, or buffered write helpers. On error it rolls initialized size and data size back.
- Direct writes use `iomap_dio_rw()` and may fall back to buffered writes for remaining bytes; fallback writes are synced and invalidated.
- Size setattr waits for DIO, updates VFS size, truncates NTFS attributes, rolls back on failure, and zeroes partial page gaps for nonresident extension.
- Fallocate maps the whole runlist if needed, marks the volume dirty, waits DIO, locks mapping invalidation for destructive modes, calls the mode-specific helper, then updates times, filename metadata, and dirty state.
- Hole punching zeroes unaligned edge clusters through iomap before deallocating full clusters.
- Collapse and insert require cluster-aligned offset/length and rewrite nonresident runlists through attribute helpers.

State and persistence behavior:
- Volume dirty flag is set before writes, setattr, and fallocate mutations.
- Release-time trim can change runlist, allocated size, and mapping pairs after application closes a file.
- `ntfs_getattr()` reports birth time, compressed/encrypted/immutable/append attributes, DIO alignment for eligible regular files, and includes pending deallocation clusters in block count.
- Fsync writes parent directory index allocation inodes for every filename hardlink, then flushes volume allocation metadata and block device cache.
- Symlink `get_link` returns the parsed `NTFS_I(inode)->target` generated during inode load.

Dependencies and integration points:
- Depends on `lcnalloc.h`, `ntfs.h`, `reparse.h`, `ea.h`, `iomap.h`, and `bitmap.h`.
- Uses iomap operation sets from NTFS iomap code for read/write/seek/page-mkwrite.
- Uses EA helpers for WSL uid/gid/mode metadata and listxattr/ACL inode hooks.
- Uses allocation helpers for cluster trim and FITRIM.
- Shares ioctl handlers with directory operations.

Risks and edge cases:
- `ntfs_file_write_iter()` error message checks `NInoEncrypted()` but prints compressed/encrypted based on `NInoCompressed()`, making compressed text unreachable in that branch.
- Release-time prealloc trim can fail after userspace close; errors from `.release` are often ignored by applications.
- Direct-I/O alignment requires superblock block size, while reported DIO alignment uses bdev logical block size; mismatches should be tested.
- `ntfs_dio_write_iter()` treats `-ENOTBLK` as partial fallback success; accounting around mixed direct/buffered writes is subtle.
- Fallocate waits indefinitely for free-cluster knowledge and returns `-ENOSPC` when the MFT zone length is zero, which can surprise callers unrelated to requested range.

Test signals:
- Exercise buffered/direct read/write, NOWAIT lock contention, compressed/encrypted rejection, partial direct-write fallback, mmap shared write initialization, and fsync metadata propagation.
- Test truncate extension over partial pages, shrink rollback, chmod/chown WSL EA updates, readonly DOS bit mapping, and POSIX ACL chmod.
- Fallocate tests should cover all supported modes, cluster alignment errors, sparse-disabled behavior, edge zeroing for punch-hole, and filename metadata updates.
- Ioctl tests should cover capability checks, volume-label copy bounds, FITRIM minlen/granularity, and shutdown gating.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ntfs/file.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ntfs/index.c -->
# sources/distributed-fs/ceph-client/fs/ntfs/index.c

Purpose: implements generic NTFS index B+tree lookup, traversal, insertion, deletion, index block I/O, and bitmap-backed index allocation. Directory code uses it primarily for `$I30` filename indexes, while special view indexes also share the machinery.

Important APIs and functions:
- `ntfs_index_entry_inconsistent()` validates entry and payload bounds.
- `ntfs_index_ctx_get()`, `ntfs_index_ctx_put()`, and `ntfs_index_ctx_reinit()` manage `struct ntfs_index_context` lifetime and cached root/allocation resources.
- `ntfs_index_lookup()` searches by key and leaves the context at the found entry or insertion point.
- `ntfs_index_entry_mark_dirty()` and `ntfs_icx_ib_sync_write()` persist modified root or allocation entries.
- `ntfs_index_add_filename()` builds and inserts a filename index entry.
- `ntfs_ie_add()` is the generic insertion engine.
- `ntfs_index_rm()` and `ntfs_index_remove()` remove entries and rebalance/leafify as needed.
- `ntfs_index_walk_down()` and `ntfs_index_next()` support ordered traversal for readdir.

Control flow:
- Lookup loads resident `$INDEX_ROOT`, validates block size and collation rule, scans entries with `ntfs_ie_lookup()`, and follows child VCNs through `$INDEX_ALLOCATION` until it finds a match or insertion point.
- Index allocation block reads/writes use `ntfs_inode_attr_pread/pwrite()` and MST fixups around `INDX` records.
- Insertion first performs lookup to reject duplicates and find position. If the target index header has room, it inserts in place. If not, root insertion grows `$INDEX_ROOT` or reparents root into a new index allocation block; allocation-block insertion splits around a median and propagates median entries upward.
- Reparenting creates `$BITMAP` and `$INDEX_ALLOCATION` if needed, copies root entries to a new index block, converts root into a large-index node containing only an end entry with a child VCN, and marks index allocation present.
- Bitmap helpers create/grow `$BITMAP`, find free VCN slots, set and clear bits, and translate between bitmap positions and allocation VCNs.
- Deletion removes leaf entries directly when possible, replaces internal entries with successors from child leaves, clears empty allocation blocks in the bitmap, reparents end entries, and can collapse a large root back to a leaf root.

State and persistence behavior:
- `struct ntfs_index_context` owns current root search context, current index block copy, index allocation inode, parent VCN/position stack, dirty flag, block size, VCN size, and sync-write preference.
- Root modifications mark the containing MFT record dirty; allocation-block modifications set `ib_dirty` or write immediately.
- `ntfs_index_ctx_put()` writes a dirty current allocation block before freeing it.
- Split and reparent paths allocate bitmap slots before writes and clear them on rollback.
- Root resizing updates resident attribute size, inode data/initialized/allocated sizes, and `NInoIndexAllocPresent`.

Dependencies and integration points:
- Depends on `collate.h`, `index.h`, `ntfs.h`, and `attrlist.h`.
- Uses `ntfs_collate()` for collation-rule-aware key comparison.
- Uses attribute manipulation helpers for root resize, index allocation creation, bitmap writes, attrlist creation, and attribute record moves.
- Directory lookup and readdir consume lookup/traversal APIs; inode filename sync uses lookup plus dirty marking; namei/create/remove paths use add/remove APIs.

Risks and edge cases:
- Parent depth is capped by `MAX_PARENT_VCN` at 32; deeper or corrupt trees fail with `-EOPNOTSUPP`.
- `ntfs_index_ctx_reinit()` assigns `idx_ni`, `name`, and `name_len` from `icx` after `ntfs_index_ctx_free()`; because the struct is overwritten using its own fields, this is fragile if the compiler evaluation order or future edits change.
- `ntfs_index_entry_inconsistent()` rejects entries at `ie_end <= ie + length`, which may be stricter than intended for an entry ending exactly at index end.
- Many rollback paths can leave allocation bitmap or root/allocation state inconsistent if a later write fails after earlier metadata writes.
- Median selection is count-based rather than byte-balanced, so pathological entry-size distributions can cause repeated splits.
- `ntfs_ib_write()` returns raw short-write values in some paths instead of normalized negative errno.

Test signals:
- Lookup tests should cover root-only, multi-level, insertion-point `-ENOENT`, unsupported collation, corrupt child VCN, and invalid entry bounds.
- Insertion tests should force root growth, root reparenting, allocation-block split, parent split propagation, duplicate key rejection, and bitmap rollback on injected write failures.
- Removal tests should cover leaf removal, internal-node successor replacement, empty leaf deletion, large-root leafification, and retry after `-EAGAIN`.
- Traversal tests should validate ordered `ntfs_index_next()` across root and allocation levels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ntfs/index.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ntfs/index.h -->
# sources/distributed-fs/ceph-client/fs/ntfs/index.h

Purpose: defines the NTFS index context structure and public index manipulation API.

Important APIs and types:
- `VCN_INDEX_ROOT_PARENT` is the sentinel parent VCN for entries rooted in `$INDEX_ROOT`.
- `MAX_PARENT_VCN` caps remembered parent depth at 32.
- `struct ntfs_index_context` describes the current index, key entry, payload pointer, root/allocation ownership, parent stack, dirty allocation block state, block size, VCN sizing, and sync write mode.
- Public APIs include context allocation/free/reinit, lookup, entry dirtying, filename add, index remove, tree walking, generic entry add/remove, and synchronous index-block write.

Control flow and integration:
- Callers allocate a context with `ntfs_index_ctx_get()`, perform lookup/traversal/mutation, optionally mark entries dirty, then call `ntfs_index_ctx_put()`.
- Directory iteration uses `ntfs_index_walk_down()` and `ntfs_index_next()`.
- Directory creation/link uses `ntfs_index_add_filename()`.
- Unlink/remove paths use `ntfs_index_remove()` or lower-level `ntfs_index_rm()` after lookup.
- Filename metadata sync uses lookup plus dirty marking and synchronous write.

State and persistence behavior:
- The context's `entry`, `data`, and `data_len` point into either resident root memory or an in-memory index block copy; they are invalid after context reinit/put.
- `ib_dirty` defers allocation-block persistence until put or explicit sync write.
- `sync_write` switches allocation-block writes to synchronous `ntfs_inode_attr_pwrite()`.

Dependencies:
- Includes Linux fs declarations plus NTFS `attrib.h` and `mft.h`.
- Relies on on-disk layout types such as `struct index_entry`, `struct index_root`, `struct index_block`, and `struct file_name_attr`.

Risks and edge cases:
- Callers must hold the right inode/MFT locks around operations that touch mutable index state.
- Pointers returned in the context are borrowed; storing them past context lifetime will use freed or unmapped memory.
- Dirtying an allocation entry without put/sync risks losing modifications if a caller leaks the context.

Test signals:
- Compile tests catch prototype drift.
- Mutation tests should assert context dirty/write semantics by changing entries in root and allocation blocks.
- Traversal tests should validate parent stack behavior up to expected tree depths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ntfs/index.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ntfs/inode.c -->
# sources/distributed-fs/ceph-client/fs/ntfs/inode.c

Purpose: owns NTFS inode lifecycle, MFT record loading/writing, fake attribute and index inodes, extent inode attachment, attribute-list creation, VFS operation selection, mount-time `$MFT` bootstrap, eviction, truncate/initialized-size helpers, and raw attribute pread/pwrite.

Important APIs and functions:
- `ntfs_iget()`, `ntfs_attr_iget()`, and `ntfs_index_iget()` obtain normal, attribute, and index inodes through `iget5_locked()`.
- `ntfs_test_inode()` and `ntfs_init_locked_inode()` key inode-cache identity by MFT number plus optional attribute type/name.
- `__ntfs_init_inode()` initializes NTFS-private inode state, locks, runlists, index/compression fields, extent state, and cached MFT locations.
- `ntfs_read_locked_inode()`, `ntfs_read_locked_attr_inode()`, and `ntfs_read_locked_index_inode()` populate VFS and NTFS inode state from MFT records and attributes.
- `ntfs_read_inode_mount()` bootstraps the `$MFT` inode before normal page-cache based MFT mapping is available.
- `__ntfs_write_inode()` syncs standard information, filename index entries, mapping pairs, base MFT records, and extent MFT records.
- `ntfs_inode_sync_filename()` updates parent directory `$I30` entries with current sizes, flags, times, and reparse tag.
- `ntfs_inode_attach_all_extents()` and `ntfs_inode_add_attrlist()` manage multi-record inodes.
- `ntfs_inode_attr_pread()` and `ntfs_inode_attr_pwrite()` provide byte I/O for fake attribute inodes.

Control flow:
- Normal inode read sets mount uid/gid defaults, maps the MFT record, validates in-use/base record/link count, loads `$STANDARD_INFORMATION`, optional `$ATTRIBUTE_LIST`, optional EA/WSL metadata, determines mode from directory/reparse/data state, validates directory `$INDEX_ROOT` or file `$DATA`, sets runlist/compression/sparse/encrypted sizes, releases the MFT record, and installs VFS operations.
- Attribute inode read mirrors base inode metadata, looks up the selected attribute, validates resident/nonresident constraints and compression/encryption/sparse flags, sets size/block accounting, and pins the base inode with `igrab()`.
- Index inode read validates `$INDEX_ROOT`, optional `$INDEX_ALLOCATION`, matching `$BITMAP`, block size, VCN size, and then pins the base inode.
- Mount-time `$MFT` loading reads record 0 directly from the block device, applies MST fixups, optionally loads `$ATTRIBUTE_LIST`, incrementally decompresses `$DATA` mapping pairs, calls normal inode read once the first extent is known, and then restores no-VFS-operation tables for `$MFT`.
- Writeback ignores fake attribute inodes, maps the base MFT record, updates dirty runlist mapping pairs, syncs standard information, optionally syncs filename indexes while the filesystem is active, writes base and extent records, and marks volume errors on non-memory failures.
- Eviction truncates pages, frees unlinked base inode clusters and extent MFT records, commits dirty linked inodes, frees extent arrays, releases base references from fake inodes, and frees cached runlists/attrlists/names/reparse targets.
- Raw attribute pwrite enlarges/truncates the attribute as needed, writes resident data into the MFT record and page-cache folio, or writes nonresident data through folios and optional synchronous bios.

State and persistence behavior:
- NTFS inode state includes runlist, size trio, MFT sequence, flags, attrlist, compression geometry, directory index geometry, extent list/base pointer, cached target, deallocation cluster count, and cached MFT LCNs.
- `NInoDirty`, `NInoRunlistDirty`, `NInoFileNameDirty`, `NInoAttrList`, `NInoIndexAllocPresent`, and related bits coordinate persistence between helpers.
- Standard information sync writes NTFS creation/mtime/ctime/atime and file attributes without redirtying the VFS inode.
- Filename sync persists duplicated NTFS filename metadata in every parent directory index.
- Attribute-list creation can move records out of the base MFT record to free space, then rolls back by moving attributes back and removing the added record on failure.
- Unlinked inode deletion frees nonresident clusters, extent MFT records, and base MFT record, but logs and leaves inconsistent metadata on some failures.

Dependencies and integration points:
- Depends on allocation, time conversion, index, attrlist, reparse, EA, attrib, iomap, and object-id support.
- Provides inode operations consumed by `file.c`, directory/index open helpers consumed by `dir.c` and `index.c`, and raw attribute I/O consumed by `ea.c` and `index.c`.
- Integrates with VFS inode cache, folio/page cache, writeback, superblock mount options, block-device reads/writes, and lockdep classes.
- Uses `ntfs_make_symlink()` to convert reparse points to symlinks and EA helpers to populate WSL metadata.

Risks and edge cases:
- `ntfs_inode_close()` assumes `base_ni = ni->ext.base_ntfs_ino` before checking for NULL, so calling it on a base inode without a base pointer would dereference NULL; comments imply it is for extent-style closing but the public name is broad.
- Several corruption paths mark volume errors and advise chkdsk; tests should confirm when `NVolSetErrors()` is raised versus suppressed.
- Mount-time `$MFT` bootstrap has circular dependency assumptions around first `$DATA` extent availability.
- Attribute-list creation rollback is complex and can leave attributes moved if rollback helpers fail.
- Raw nonresident synchronous pwrite computes cluster counts from `attr_len`; partial-page writes across multiple clusters require careful coverage.
- Eviction can delete unlinked metadata while earlier writeback/truncate failures have already logged inconsistency, so fault injection is important.

Test signals:
- Inode load tests should cover normal files, directories, reparse symlinks, missing `$DATA` for `$Extend` system files, resident/nonresident data, sparse/compressed/encrypted validation, WSL EAs, and invalid attrlist/index bounds.
- Mount tests should exercise `$MFT` with single and multiple extents, resident and nonresident attrlists, bad MST fixups, and oversized record rejection.
- Writeback tests should cover standard information updates, dirty runlist mapping-pair updates, filename index synchronization for hardlinks, extent record writes, and error handling for `-ENOMEM` versus I/O errors.
- Extent/attrlist tests should force adding attrlists, moving attributes out of the base record, attaching all extents, and rollback failures.
- Raw attr I/O tests should cover resident read/write, nonresident buffered write, synchronous write, enlarge/truncate transitions, compressed/encrypted rejection, and page-cache consistency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ntfs/inode.c -->
