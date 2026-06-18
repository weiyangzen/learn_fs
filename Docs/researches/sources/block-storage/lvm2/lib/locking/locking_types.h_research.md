# File Research: sources/block-storage/lvm2/lib/locking/locking_types.h

## Purpose
Defines the small backend interface used by `locking.c` to call a concrete locking implementation, currently file/flock locking.

## Main Contents
- Declares `lock_resource_fn`, `fin_lock_fn`, and `reset_lock_fn` callback types.
- Defines `LCK_FLOCK` as the backend flag for flock-based locking.
- Defines `struct locking_type`, containing backend flags and lock/reset/final callbacks.
- Declares `init_file_locking`, which populates a `struct locking_type`.

## Dependencies
Only requires integer types and forward declarations for command context and logical volumes.

## Risk Notes
A zero `flags` value means locking is disabled to the generic layer. Any new backend must preserve this convention because `locking.c` uses it as a policy branch.
