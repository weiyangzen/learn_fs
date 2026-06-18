# File Research: sources/block-storage/kvdo/vdo/pbn-lock-pool.c

## Purpose
Implements a fixed-capacity pool of reusable PBN lock objects.

## Core Model
Uses `idle_pbn_lock` union to overlay `struct list_head` while idle and `struct pbn_lock` while borrowed. This avoids adding free-list fields to live lock objects.

## Key Functions
- `vdo_make_pbn_lock_pool`: allocates pool plus flexible lock storage, initializes all locks as idle.
- `vdo_free_pbn_lock_pool`: asserts all locks are returned before freeing.
- `vdo_borrow_pbn_lock_from_pool`: removes an idle lock, zeroes list memory, initializes as requested type.
- `vdo_return_pbn_lock_to_pool`: zeroes lock memory and appends it to idle list.

## Integration Notes
Used by physical zones to avoid allocating locks dynamically during I/O. Failure to borrow returns `VDO_LOCK_ERROR`.

## Invariants
`borrowed <= capacity`; freeing with outstanding locks logs an assertion failure. Returned lock must be the last live reference.
