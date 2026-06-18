# File Research: sources/block-storage/kvdo/vdo/vdo-recovery.h

## Purpose
Declares the public recovery entry points.

## Public API
- `vdo_replay_into_slab_journals()`: slab depot callback used to replay recovery journal entries into one allocator's slab journals.
- `vdo_launch_recovery()`: launches offline crash recovery and completes a parent completion when done.

## Dependencies
Includes `completion.h` and `vdo.h`; uses `struct block_allocator` through declarations available from included headers.
