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
