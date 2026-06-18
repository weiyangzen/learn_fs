# File Research: sources/block-storage/lvm2/libdm/mm/pool-fast.c

## Summary
Fast implementation of libdm memory pools. It allocates chunks, bumps a cursor for pool allocations, supports stack-style rewind, one spare chunk, growable objects, optional Valgrind annotations, and optional mprotect-based pool locking support.

## Main Responsibilities
- Creates pools with chunk sizes rounded up to a power of two.
- Allocates aligned memory by bumping the current chunk pointer.
- Rewinds/free chunks back to a pointer.
- Constructs variable-length objects within pool chunks, moving to larger chunks when necessary.
- Computes a checksum over allocated pool memory when lock checking is enabled.
- Protects chunks with `mprotect()` when `DEBUG_ENFORCE_POOL_LOCKING` is configured.

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
The current chunk is a LIFO stack. If the current chunk lacks room, `_new_chunk()` either reuses the one-entry `spare_chunk` or allocates a new chunk and links it as the current head.

`dm_pool_free()` searches for the chunk containing `ptr`, sets that chunk's begin pointer to `ptr`, moves newer chunks through the spare slot/free path, and makes the containing chunk current.

`dm_pool_begin_object()` reserves object state at the current aligned begin pointer. `dm_pool_grow_object()` appends bytes to the in-progress object and moves the object into a new chunk if the current one lacks space. `dm_pool_end_object()` advances the chunk begin by `object_len` and returns the object's starting pointer.

Valgrind hooks mark pool memory no-access when free/reserved and undefined when handed to callers.

## State and Lifetime
`struct dm_pool` stores the current chunk, one spare chunk, name, chunk size, in-progress object length/alignment, lock flag, and CRC. Pools are linked into the global `_dm_pools` list under `_dm_pools_mutex`.

## Risks
Pool frees are stack-style; freeing an old pointer discards all allocations made after it. Pointer containment checks are strict and log internal errors when the pointer is not in any chunk. The CRC implementation is a lightweight checksum, not a cryptographic integrity check.
