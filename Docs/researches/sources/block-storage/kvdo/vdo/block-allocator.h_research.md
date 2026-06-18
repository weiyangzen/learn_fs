# File Research: sources/block-storage/kvdo/vdo/block-allocator.h

## Purpose

Declares the per-zone block allocator structure and API.

## Contents

- Defines `VIO_POOL_SIZE = 128`.
- Defines allocator drain-step enum.
- Defines `struct slab_actor` for applying slab actions in parallel.
- Defines `struct block_allocator` with:
  - completion,
  - slab depot/summary,
  - read-only notifier,
  - nonce and zone/thread identity,
  - slab counts,
  - admin state,
  - open slab,
  - priority table,
  - slab scrubber,
  - statistics,
  - dirty slab journal list,
  - VIO pool,
  - kcopyd eraser,
  - slab iterator for erasure.
- Declares creation, allocation, load, drain, resume, grow, VIO pool, scrub, stats, and dump APIs.

## Dependencies and Role

The header exposes allocator internals because closely related slab, depot, and recovery code need direct coordination with allocator-owned state.
