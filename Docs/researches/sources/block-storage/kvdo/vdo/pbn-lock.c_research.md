# File Research: sources/block-storage/kvdo/vdo/pbn-lock.c

## Purpose
Implements PBN lock typing, read/write downgrade, reference increment claiming, and provisional reference release.

## Key Concepts
`LOCK_IMPLEMENTATIONS` maps each `pbn_lock_type` to its type, name, and provisional-reference release reason:
- read lock: candidate duplicate
- write lock: newly allocated
- block-map write lock: block map write

## Key Functions
- `vdo_initialize_pbn_lock`: clears holder count and sets type.
- `vdo_is_pbn_read_lock`: type check.
- `vdo_downgrade_pbn_write_lock`: converts write lock to read lock and sets increment limit.
- `vdo_claim_pbn_lock_increment`: atomically claims a read-lock reference-count increment.
- `vdo_assign_pbn_lock_provisional_reference`
- `vdo_unassign_pbn_lock_provisional_reference`
- `vdo_release_pbn_lock_provisional_reference`

## Concurrency
`vdo_claim_pbn_lock_increment` uses `atomic_add_return` because multiple hash-zone threads may deduplicate against a single compressed-block PBN lock.

## Integration Notes
References `MAXIMUM_REFERENCE_COUNT` from `packed-reference-block.h` and calls `vdo_release_block_reference` through the block allocator when releasing provisional references.
