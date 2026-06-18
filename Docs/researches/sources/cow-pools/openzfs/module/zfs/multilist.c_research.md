# File Research: sources/cow-pools/openzfs/module/zfs/multilist.c

## Scope

Thread-scalable sharded list implementation. This file wraps multiple independently locked `list_t` sublists behind one `multilist_t`, providing lower-contention insertion/removal and explicit sublist operations for callers that need controlled traversal or locking.

## Main Interfaces

- Creation/destruction: `multilist_create()`, `multilist_destroy()`.
- Whole-multilist operations: `multilist_insert()`, `multilist_remove()`, `multilist_is_empty()`, `multilist_get_num_sublists()`, `multilist_get_random_index()`.
- Sublist locking: `multilist_sublist_lock()`, `multilist_sublist_lock_idx()`, `multilist_sublist_lock_obj()`, `multilist_sublist_unlock()`.
- Sublist mutation: `multilist_sublist_insert_head()`, `multilist_sublist_insert_tail()`, `multilist_sublist_insert_after()`, `multilist_sublist_insert_before()`, `multilist_sublist_move_forward()`, `multilist_sublist_remove()`.
- Sublist inspection: `multilist_sublist_is_empty()`, `multilist_sublist_is_empty_idx()`, `multilist_sublist_head()`, `multilist_sublist_tail()`, `multilist_sublist_next()`, `multilist_sublist_prev()`.
- Link helpers: `multilist_link_init()`, `multilist_link_active()`.
- Tunable: `zfs_multilist_num_sublists`.

## State And Control Flow

`multilist_create()` chooses the number of sublists from `zfs_multilist_num_sublists` or `MAX(boot_ncpus, 4)`, records object offset and caller-supplied index function, allocates `ml_sublists`, initializes one mutex and `list_t` per sublist.

`multilist_insert()` and `multilist_remove()` compute the target sublist with `ml_index_func`, lock it unless the current thread already holds it, then insert or remove. Direct sublist insert helpers require the sublist lock and allow callers to place objects at head, tail, or relative positions.

`multilist_is_empty()` checks each sublist under its lock one at a time, so it is safe against list corruption but only provides a fuzzy answer under concurrent mutation. `multilist_sublist_move_forward()` swaps an object with its previous list neighbor and is constrained to remove only the target object because ARC eviction code depends on that behavior.

## Dependencies

Depends on OpenZFS `list_t`, mutex primitives, `random_in_range()`, `boot_ncpus`, DTrace probes, and module parameter plumbing.

## Correctness Notes

The index function must be stable for each object and return a valid sublist index; otherwise `multilist_remove()` can remove from the wrong list. Whole-list insert/remove intentionally tolerate callers already holding the sublist mutex. Direct sublist insertion can violate index-function placement, so callers must ensure they later remove consistently. Destroy asserts all sublists are empty.
