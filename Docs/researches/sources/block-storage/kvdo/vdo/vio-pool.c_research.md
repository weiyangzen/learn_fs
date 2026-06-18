# File Research: sources/block-storage/kvdo/vdo/vio-pool.c

## Purpose
Implements a fixed-size pool of preallocated metadata VIOs and block-sized buffers, with async waiters for pool exhaustion.

## Main Concepts
- `struct vio_pool` owns available and busy lists, waiter queue, busy count, thread ownership, shared buffer storage, and entries.
- Each `vio_pool_entry` owns one VIO and one `VDO_BLOCK_SIZE` buffer slice.
- The pool is thread-affine; acquire and return assert the configured thread ID.

## Key Functions
- `make_vio_pool()` allocates the pool, contiguous buffers, constructs each VIO with the supplied constructor, and places entries on the available list.
- `free_vio_pool()` asserts no waiters or busy entries, frees available VIOs, validates all entries were removed, and frees backing storage.
- `is_vio_pool_busy()` reports outstanding entries.
- `acquire_vio_from_pool()` immediately hands an available entry to the waiter callback or queues the waiter if empty.
- `return_vio_to_pool()` either hands the entry directly to the next waiter or moves it back to available and decrements busy count.

## Important Invariants
- Pool entries must be returned on the same thread from which they are acquired.
- `busy_count` remains unchanged when returning an entry directly to a waiting requestor.
- `entry->vio->completion.error_handler` is cleared on return.
