# sources/distributed-fs/ceph-client/drivers/md/dm-clone-metadata.h

## Purpose
`dm-clone-metadata.h` is the private interface between the dm-clone target and its persistent metadata implementation. It defines metadata sizing constants, declares the opaque `struct dm_clone_metadata`, and documents the threading and transaction contract for region hydration bitmap updates.

## Important APIs, Types, And Functions
The header defines `DM_CLONE_METADATA_BLOCK_SIZE`, `DM_CLONE_METADATA_MAX_SECTORS`, `DM_CLONE_METADATA_MAX_SECTORS_WARNING`, and `SPACE_MAP_ROOT_SIZE`. The opaque `struct dm_clone_metadata` hides the implementation details from the target. Creation and teardown use `dm_clone_metadata_open` and `dm_clone_metadata_close`. Mutation APIs are `dm_clone_set_region_hydrated` and `dm_clone_cond_set_range`. Transaction APIs are `dm_clone_metadata_pre_commit`, `dm_clone_metadata_commit`, `dm_clone_metadata_abort`, `dm_clone_metadata_set_read_only`, and `dm_clone_metadata_set_read_write`. Query APIs include hydration completion/range checks, hydrated-region count, next-unhydrated lookup, metadata changed state, and metadata block accounting.

## Control Flow Contract
The intended flow is: open metadata for a target size and region size; handle I/O by marking hydrated regions as they become valid on the destination device; periodically call `dm_clone_metadata_pre_commit`; flush destination data; then call `dm_clone_metadata_commit`. After `pre_commit`, subsequent metadata updates belong to the next transaction, allowing the target to commit exactly the bits covered by the data flush. On metadata errors, the target should set metadata read-only, abort, reload the in-core bitset if needed, and avoid future mutating calls until recovery.

## State And Persistence Behavior
The header makes the crash-consistency contract explicit. Hydrated-region bits may be updated without blocking, but they are not durable until the two-phase commit completes. `dm_clone_metadata_pre_commit` freezes the current set of dirty region bits; `dm_clone_metadata_commit` persists them. The target must flush destination data between those phases so committed metadata never claims that a region is hydrated before its data is durable. `dm_clone_reload_in_core_bitset` is reserved for abort/read-only recovery because it performs I/O and rewrites the in-core bitmap without taking the bitmap spinlock.

## Dependencies And Integration Points
The interface includes persistent-data block manager and space-map headers for metadata block sizing and `dm_block_t` types. It is used directly by `dm-clone-target.c` and implemented by `dm-clone-metadata.c`. The comments encode context rules that the target relies on: single-region updates are safe from interrupt context; conditional range updates are nonblocking but not safe when interrupts are already disabled; reload must not run concurrently with mutation.

## Risks And Edge Cases
Callers must respect context restrictions or risk deadlocks and bitmap corruption. Failing to pair pre-commit with destination flush and commit breaks crash consistency. Calling reload while writes are still allowed can lose in-core updates. Read-only mode intentionally makes mutating functions return `-EPERM`, and target error paths must handle that without retry loops that keep accepting writes. The metadata device has maximum and warning sizes; excess space is not part of the managed metadata space.

## Test Signals
Header-level contract tests map to target and metadata integration tests: interrupt-context single-bit updates, non-interrupt range discard updates, FUA/flush-triggered two-phase commits, read-only error propagation, abort-and-reload recovery, hydration completion detection, next-unhydrated scanning, and status queries for free and total metadata blocks.
