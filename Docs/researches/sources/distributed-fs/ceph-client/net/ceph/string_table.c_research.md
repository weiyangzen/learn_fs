# sources/distributed-fs/ceph-client/net/ceph/string_table.c

## Purpose
`string_table.c` implements a global intern table for `struct ceph_string`, primarily used for pool namespace strings. Interning lets locators and layouts share equal strings with refcounted lifetime and RCU-safe delayed freeing.

## Important APIs, types, and functions
- `ceph_find_or_create_string()` looks up an existing interned string by length/content, takes a reference if still alive, or allocates and inserts a new string.
- `ceph_release_string()` removes a string from the rbtree if still linked and frees it with `kfree_rcu()`.
- `ceph_strings_empty()` reports whether the global string tree has no entries.
- The implementation uses global `string_tree` and `string_tree_lock`.

## Control flow
Lookup first searches under the spinlock. If it finds a matching node but `kref_get_unless_zero()` fails, the dying node is erased and lookup proceeds as a miss. On miss, the function allocates a new flexible string object, initializes its kref and NUL-terminated contents, then retries insertion under the lock. A concurrent insertion wins by freeing the new object and returning the existing referenced string. A concurrent dying match is erased and the insertion loop retries.

Release runs from `kref_put()` callbacks. It erases the node from the global rbtree if present, clears the rb node, drops the lock, then uses `kfree_rcu()` so RCU readers using `ceph_try_get_string()` can safely observe disappearing pointers.

## State and persistence behavior
The intern table is process-global in kernel memory and persists until all references are dropped. Strings are ordered by length then content using `ceph_compare_string()`. There is no on-disk state. `ceph_strings_empty()` is useful as a leak/test signal but is lockless, so it is best interpreted when no concurrent users remain.

## Dependencies and integration points
`ceph_object_locator` holds `struct ceph_string *pool_ns`. `osdmap.c` copies/destroys locators and object layout pool namespaces through string-table refcounts. CephFS inode layouts and OSD request target copying use these strings across RCU-protected paths.

## Risks and edge cases
- Correctness relies on `kref_get_unless_zero()` to avoid resurrecting strings that are in release.
- Global spinlock contention can appear if namespace churn is high, though expected cardinality is low.
- `ceph_strings_empty()` does not take the spinlock.
- Comparison sorts by length before bytes, which is fine for an internal tree but must remain consistent with all lookup/insert paths.

## Test signals
Test duplicate lookup returning the same object, concurrent create races, release removing a node, retry after dying-node detection, RCU-safe delayed freeing through `ceph_try_get_string()`, empty string interning, and final `ceph_strings_empty()` after all puts.
