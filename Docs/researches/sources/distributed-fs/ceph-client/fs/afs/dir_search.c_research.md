# sources/distributed-fs/ceph-client/fs/afs/dir_search.c

Purpose: `dir_search.c` searches the AFS directory hash table for one name and returns its FID plus the directory data version observed during the search.

Important APIs and functions: `afs_dir_hash_name()` implements protocol-compatible bucket hashing. `afs_dir_init_iter()` prepares slot count, bucket, and loop budget. `afs_dir_find_block()` maps a directory block from the vnode folio queue. `afs_dir_search_bucket()` walks one hash chain. `afs_dir_search()` wraps directory loading, retry, version capture, and bucket search.

Control flow: `afs_dir_search()` initializes an iterator, calls `afs_read_dir()` to obtain validated directory contents under `validate_lock`, records `inode_peek_iversion_raw()`, and calls the bucket walker. The walker maps block zero for the hash table, follows `hash_next` entry indexes, validates reserved-slot boundaries, maps target blocks, compares NUL-terminated names, decodes vnode/unique on success, and detects loops with `loop_check`.

State and persistence: iterator state tracks the current folio queue, slot, file position, mapped block, bucket, required slots, previous hash-chain entry, and loop budget. It persists no durable state but invalidates the directory cache on stale mapping or malformed chains.

Dependencies and integration points: depends on `afs_read_dir()` from `dir.c`, AFS directory constants/XDR structures, folio queue mapping, inode i_version, and vnode validation flags. `dir.c` uses it for lookup; `dir_edit.c` uses it to find removals and hash-chain predecessors.

Risks: stale or corrupt directory data must lead to invalidation. Hash compatibility is mandatory. Loop detection and reserved-slot checks protect against malformed server data or local edit bugs. Lock release discipline is important because `afs_read_dir()` returns with `validate_lock` held.

Test signals: known hash vectors, present/missing names, chain head and tail matches, chain loops, reserved-slot entries, stale block mapping, retry after `-ESTALE`, and lock release after success/failure.
