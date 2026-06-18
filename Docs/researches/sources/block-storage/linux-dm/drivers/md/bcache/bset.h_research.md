# File Research: sources/block-storage/linux-dm/drivers/md/bcache/bset.h

## Purpose
Declares bkey/bset abstractions, btree key operations, btree iterators, sorting state, keylist helpers, and debug hooks used by bcache's log-structured btree nodes.

## Main Interfaces
- Structures: `bset_tree`, `btree_keys_ops`, `btree_keys`, `btree_iter`, `bset_sort_state`, `bset_stats`, and `keylist`.
- Constants and helpers for `MAX_BSETS`, bset byte/block sizing, bkey comparison, bkey init/copy, bset last/index, and unwritten-space accounting.
- Function prototypes for allocation, set initialization, search, insert, iterator, sorting, merge, trimming, keylist reallocation/pop, and debug dumps.

## Control Flow
The header defines the callback-based split between generic bset mechanics and key-type-specific behavior. Generic code calls operation hooks for sorting, insert fixup, invalid/bad detection, merging, and textual dumping.

## State And Synchronization
No locking by itself. `btree_keys` stores multiple sorted sets plus auxiliary search metadata; callers serialize access with btree node locks.

## Integration Points
Used by `bset.c`, `btree.c`, `extents.c`, and central `bcache.h`. `btree_keys_ops.is_extents` controls whether iteration/search compares extent start keys or exact keys.

## Notable Behaviors
- Comments explain why bsets use auxiliary search trees instead of binary searching variable-length keys.
- `bch_btree_keys_u64s_remaining()` only reports capacity when the last set is unwritten.
- `preceding_key()` creates the search key immediately before a target to position insert iterators.

## Risks And Review Focus
- Macro and inline helpers encode assumptions about contiguous bset memory.
- `KEYLIST_INLINE` is sized around btree split needs; changes to split key counts may require revisiting it.
- Debug stubs compile away most checks when `CONFIG_BCACHE_DEBUG` is disabled.
