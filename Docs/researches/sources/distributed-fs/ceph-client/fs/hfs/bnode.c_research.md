# sources/distributed-fs/ceph-client/fs/hfs/bnode.c

## Purpose
`bnode.c` implements low-level HFS B-tree node I/O, validation, sibling unlinking, hash-cache lookup, node creation/loading, reference counting, deletion cleanup, and page-backed memory operations.

## Important APIs, Types, And Functions
Read/write helpers include `hfs_bnode_read`, `hfs_bnode_read_u16`, `hfs_bnode_read_u8`, `hfs_bnode_read_key`, `hfs_bnode_write`, `hfs_bnode_write_u16`, `hfs_bnode_write_u8`, `hfs_bnode_clear`, `hfs_bnode_copy`, and `hfs_bnode_move`. Structural helpers include `hfs_bnode_dump`, `hfs_bnode_unlink`, `hfs_bnode_findhash`, `hfs_bnode_unhash`, `hfs_bnode_find`, `hfs_bnode_free`, `hfs_bnode_create`, `hfs_bnode_get`, and `hfs_bnode_put`.

Internal guards `is_bnode_offset_valid` and `check_and_correct_requested_length` reject or clamp invalid node offsets/lengths. `hfs_bnode_hash` maps CNIDs to the tree hash table.

## Control Flow
`hfs_bnode_find` first searches the tree hash under `hash_lock`; if absent, `__hfs_bnode_create` allocates a node, inserts a new placeholder into the hash, reads backing pages from the B-tree inode mapping, and leaves `HFS_BNODE_NEW` set while validation proceeds. Other waiters find the placeholder, increment its refcount, and wait for `HFS_BNODE_NEW` to clear.

Validation reads the node descriptor, records prev/next links, record count, type, and height, verifies type/height consistency with tree depth, then walks the record offset table to ensure monotonic, in-range, even offsets and plausible key sizes. `hfs_bnode_create` creates a zeroed new node and clears `HFS_BNODE_NEW`. `hfs_bnode_put` decrements the refcount under the hash lock; deleted nodes are unhashed, zeroed, freed in the bitmap, and released.

## State And Persistence
Persistent state is the page-backed B-tree node data, descriptor, record offsets, links, and records. In-memory state includes node refcount, flags (`NEW`, `ERROR`, `DELETED`), hash chain membership, loaded pages, node identity, type, height, sibling links, and parent. Writes mark affected pages dirty.

## Dependencies And Integration Points
This file depends on Linux page cache helpers, HFS B-tree structures, hash locking, wait queues, and B-tree bitmap allocation/freeing. Higher-level B-tree search, insert/delete, catalog, extent, and xattr code depend on these node primitives.

## Risks And Test Signals
Risks include page-boundary assumptions in write/copy/move helpers, clamped reads hiding corruption, stale hash entries, refcount underflow, waiting on nodes that remain `NEW`, and malformed offset tables. Signals include KASAN/KCSAN/lockdep under B-tree mutation, malformed image mount rejection, catalog/extent iteration tests, node create/delete stress, and dirty page writeback checks.
