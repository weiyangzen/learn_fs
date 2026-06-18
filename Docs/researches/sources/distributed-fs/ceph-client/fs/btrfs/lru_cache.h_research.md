# sources/distributed-fs/ceph-client/fs/btrfs/lru_cache.h

## Purpose
`lru_cache.h` defines the public structure contract for the generic Btrfs LRU cache implemented in `lru_cache.c`. The source was read as a complete 71-line header.

## Important APIs, Types, and Functions
`struct btrfs_lru_cache_entry` contains LRU linkage, a u64 key, an optional generation, and linkage for the per-maple-tree bucket list. `struct btrfs_lru_cache` contains the LRU list, maple tree, current size, and maximum size. The header declares all cache operations and provides `btrfs_lru_cache_for_each_entry_safe()` plus `btrfs_lru_cache_lru_entry()`.

## Control Flow
There is no independent flow. Consumers embed the entry as the first field of their own allocation, initialize a cache, store and lookup entries, and either explicitly remove/clear them or allow bounded store to evict the oldest entry.

## State and Persistence Behavior
The header defines in-memory cache state only. Entries are owned by the cache after successful store and are freed by removal or eviction.

## Dependencies and Integration Points
It includes Linux `types.h`, `maple_tree.h`, and `list.h`. It integrates with `lru_cache.c` and any Btrfs subsystem that needs u64-keyed LRU caching with optional generations.

## Risks and Edge Cases
The offset-zero and `kmalloc()` allocation requirements are semantic, not compiler-enforced. On 32-bit systems, the maple tree indexes only the lower unsigned-long part of a u64 key, so correctness depends on retaining and comparing the full key in each entry.

## Test Signals
Build coverage catches API drift. Behavioral signals are the `lru_cache.c` tests around duplicate generations, key collisions, eviction order, and clear/remove ownership.
