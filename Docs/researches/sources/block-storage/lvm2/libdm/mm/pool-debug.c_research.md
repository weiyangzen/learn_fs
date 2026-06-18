# File Research: sources/block-storage/lvm2/libdm/mm/pool-debug.c

## Summary
Debug implementation of libdm memory pools. It allocates every pool block separately, tracks per-pool allocation statistics, supports growable temporary objects, and favors correctness checks over allocation efficiency.

## Main Responsibilities
- Creates and destroys `dm_pool` objects.
- Allocates, frees, and empties pool blocks.
- Implements grow/end/abandon object construction.
- Tracks debug statistics for bytes, blocks, maximums, and serial numbers.
- Adds pools to the global pool list for leak checking.

## Key APIs Implemented
- `dm_pool_create()`
- `dm_pool_destroy()`
- `dm_pool_alloc()`
- `dm_pool_alloc_aligned()`
- `dm_pool_empty()`
- `dm_pool_free()`
- `dm_pool_begin_object()`
- `dm_pool_grow_object()`
- `dm_pool_end_object()`
- `dm_pool_abandon_object()`

## Important Behavior
Each allocation creates a `struct block` with separate `data`, then appends it to the pool's block list. `dm_pool_free()` finds the block whose `data` matches the pointer and frees that block plus all later blocks, matching stack-like pool semantics.

Object construction repeatedly allocates a larger temporary block, copies the previous object content, frees the previous temporary block, and appends the final object as a normal pool block at `dm_pool_end_object()`.

Alignment is effectively ignored except for an assertion that requested alignment does not exceed default double alignment.

## State and Lifetime
`struct dm_pool` stores block list pointers, current object state, debug stats, lock state, and global-list linkage. Blocks are freed in list order starting from the selected free point.

## Risks
`dm_pool_abandon_object()` frees only the `struct block` header and not `p->object->data`, which is notable in this debug implementation. Alignment support is incomplete by design. Locking/protection CRC helpers are stubs or warnings in this variant.
