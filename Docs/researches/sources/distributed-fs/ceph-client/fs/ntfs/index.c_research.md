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
