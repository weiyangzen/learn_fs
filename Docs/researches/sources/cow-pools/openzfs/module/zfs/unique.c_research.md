# File Research: sources/cow-pools/openzfs/module/zfs/unique.c

This file implements a small process-wide unique numeric identifier allocator backed by an AVL tree. It is part of subset A through `sources/cow-pools/openzfs`.

Primary APIs:
- `unique_init()`
- `unique_fini()`
- `unique_create()`
- `unique_insert(uint64_t value)`
- `unique_remove(uint64_t value)`

Core data structures:
- Static `avl_tree_t unique_avl` stores currently reserved values.
- Static `kmutex_t unique_mtx` protects the AVL tree.
- `unique_t` stores an AVL node link plus `uint64_t un_value`.
- `UNIQUE_MASK` limits generated/accepted values to `UNIQUE_BITS` significant bits.

`unique_init()` behavior:
- Creates `unique_avl` using `unique_compare()`.
- Initializes `unique_mtx`.

`unique_fini()` behavior:
- Destroys the AVL tree and mutex.
- It assumes callers have removed outstanding entries before teardown.

`unique_create()` behavior:
- Calls `unique_insert(0)` to generate and reserve a random valid value.
- Immediately removes that value from the reservation tree.
- Returns the generated value.

`unique_insert()` behavior:
- Allocates a `unique_t`.
- Starts with the requested value.
- Under `unique_mtx`, rejects values that are zero, exceed `UNIQUE_MASK`, or already exist in the AVL tree.
- For rejected values, temporarily drops the mutex, fills `un_value` with pseudo-random bytes, masks it to the valid bit range, and retries.
- Inserts the accepted value into `unique_avl`.
- Returns the accepted value, which may differ from the caller’s requested value.

`unique_remove()` behavior:
- Looks up the supplied value in `unique_avl`.
- If found, removes it and frees the `unique_t`.
- If absent, it is a no-op.
- All AVL access is protected by `unique_mtx`.

Filesystem relevance:
- This provides a lightweight reservation mechanism for unique IDs in ZFS code paths that need collision-resistant, nonzero, bounded identifiers.
- The AVL tree tracks active reservations so concurrently created IDs do not collide.
- `unique_create()` is useful for obtaining an unreserved unique value, while `unique_insert()` reserves a value until explicit removal.

Notable implementation details:
- Random generation uses `random_get_pseudo_bytes()`, not cryptographic uniqueness.
- Mutex release during random generation avoids holding the global lock across entropy calls.
- Zero is never a valid unique value.
- The allocator silently substitutes a random value when the requested value is invalid or already reserved.
