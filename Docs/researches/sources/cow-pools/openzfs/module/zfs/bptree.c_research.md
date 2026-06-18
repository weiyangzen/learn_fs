# File Research: sources/cow-pools/openzfs/module/zfs/bptree.c

## Scope

Implements the pool bptree queue of destroyed dataset root block pointers, enabling asynchronous freeing by scan/sync code.

## APIs And Behavior

- `bptree_alloc()` creates the bptree object and initializes bonus fields `bt_begin`, `bt_end`, and space accounting.
- `bptree_free()` asserts the queue is empty and frees the object.
- `bptree_is_empty()` checks whether `bt_begin == bt_end`.
- `bptree_add()` appends a destroyed dataset root block pointer plus birth TXG and updates byte/compressed/uncompressed counters; it is sync-context only.
- `bptree_iterate()` reads each queued entry, traverses destroyed dataset blocks with `traverse_dataset_destroyed()`, calls the caller callback for non-hole/non-redacted non-dnode-level BPs, optionally updates space accounting and frees completed queue entries.
- When freeing, traversal bookmarks are saved on errors so later invocations can resume; I/O-like errors can be skipped to later entries while preserving queue state.

## State And Dependencies

Persistent state is `bptree_phys_t` in the bonus buffer plus an array of `bptree_entry_phys_t` records in the object data. Dependencies include DMU object/buf/read/write/free APIs, destroyed-dataset traversal, SPA block size/accounting helpers, and scan/free policy such as `zfs_free_leak_on_eio`.

## Risks And Invariants

Only sync context may mutate/free bptree entries. `bt_begin` only advances when no earlier I/O errors require preserving entry positions; otherwise completed entries may be made future no-ops. Space counters must reach zero when the queue is fully drained, except the leak-on-EIO path forcibly clears them.
