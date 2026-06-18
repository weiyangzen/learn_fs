# File Research: sources/block-storage/kvdo/vdo/pbn-lock-pool.h

## Purpose
Declares the opaque PBN lock pool API.

## API
- `vdo_make_pbn_lock_pool`
- `vdo_free_pbn_lock_pool`
- `vdo_borrow_pbn_lock_from_pool`
- `vdo_return_pbn_lock_to_pool`

## Integration Notes
Includes `pbn-lock.h` and VDO types. The pool owns lock storage; callers borrow initialized locks and must return them to the same pool.
