# sources/distributed-fs/ceph-client/fs/btrfs/lru_cache.c

## Purpose
`lru_cache.c` implements a small generic Btrfs LRU cache built from a global LRU list plus a maple tree keyed by the low bits of a u64 key. It supports optional generations per key and evicts the least-recently-used entry when a bounded cache reaches capacity. The source was read as a complete 166-line file.

## Important APIs, Types, and Functions
The exported functions are `btrfs_lru_cache_init()`, `btrfs_lru_cache_lookup()`, `btrfs_lru_cache_store()`, `btrfs_lru_cache_remove()`, and `btrfs_lru_cache_clear()`. The internal `match_entry()` scans the list stored for a maple-tree key and matches the full u64 key plus generation.

## Control Flow
Initialization sets up the LRU list, maple tree, size, and max size. Lookup loads the per-key list from the maple tree, scans for matching key/generation, and moves a hit to the LRU tail. Store allocates a new list head, attempts maple-tree insert, folds into an existing key list on `-EEXIST`, rejects duplicate key/generation pairs, evicts the oldest entry if the bounded cache is full, then appends the new entry to both the per-key list and the LRU list. Remove unlinks both list memberships, erases and frees an empty maple-tree bucket, frees the entry, and decrements size. Clear repeatedly removes entries from the LRU list.

## State and Persistence Behavior
All state is volatile memory in `struct btrfs_lru_cache`, per-key list heads stored in the maple tree, and caller-allocated entries that this module frees with `kfree()`. There is no locking in this module; callers must serialize access.

## Dependencies and Integration Points
The file depends on Linux maple tree and list APIs through `lru_cache.h`, allocation helpers, and Btrfs `ASSERT()` from `messages.h`. It is intended as an embedded-entry utility for Btrfs code that needs a small keyed cache.

## Risks and Edge Cases
Entries must embed `struct btrfs_lru_cache_entry` at offset zero and be `kmalloc()`-allocated because removal frees the entry directly. Duplicate key/generation insertion returns `-EEXIST` after the caller has already allocated the entry, so the caller owns cleanup. The per-key linked-list design handles 32-bit maple-tree key truncation but is efficient only when generation collisions are small. The lack of internal locking is a contract that must be respected by users.

## Test Signals
Unit-style tests should cover lookup recency updates, duplicate rejection, max-size eviction, unlimited-size mode, removal of the last entry in a maple-tree bucket, mixed generations for the same key, 32-bit key-collision behavior, and clear assertions leaving an empty tree and zero size.
