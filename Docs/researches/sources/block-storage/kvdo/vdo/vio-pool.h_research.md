# File Research: sources/block-storage/kvdo/vdo/vio-pool.h

## Purpose
Declares the VIO pool API and `vio_pool_entry` type.

## Key Types
- `struct vio_pool_entry`: list entry, VIO pointer, data buffer, parent, and context.
- `vio_constructor`: callback used to construct each pooled VIO.

## Public API
- `make_vio_pool()`
- `free_vio_pool()`
- `is_vio_pool_busy()`
- `acquire_vio_from_pool()`
- `return_vio_to_pool()`
- `as_vio_pool_entry()`

## Usage
Used for metadata blocks that need preallocated VIOs and buffers without runtime allocation in the hot path.
