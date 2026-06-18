<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/persistent-data/dm-space-map.h -->
# sources/distributed-fs/ceph-client/drivers/md/persistent-data/dm-space-map.h

## Purpose
Defines the generic `dm_space_map` interface for persistent reference-count maps. A space map records how many times each metadata or data block is referenced and is committed as part of the transaction.

## Important APIs, Types, And Functions
`struct dm_space_map` is a vtable with operations for destroy, extend, block/free counts, count lookup, count comparison, count set, commit, range inc/dec, new-block allocation, root serialization, and optional threshold callback registration. Inline wrappers such as `dm_sm_inc_block()`, `dm_sm_dec_block()`, `dm_sm_new_block()`, `dm_sm_copy_root()`, and `dm_sm_register_threshold_callback()` provide the common call surface.

`dm_sm_threshold_fn` is an edge callback type for implementations that support low-free-space notification.

## Control Flow
Callers use a concrete constructor from disk or metadata implementations, then manipulate it through the generic wrappers. Mutations occur inside transaction-manager operations. `extend()` adds capacity but the interface states newly added space must not be allocated until after commit. `new_block()` returns a block with its reference count already incremented.

## State And Persistence
The interface defines important transactional semantics: `get_nr_blocks()` excludes uncommitted extensions, `get_nr_free()` reports blocks available for allocation now, and space maps must avoid allocating blocks from the previous transaction so rollback remains safe. `root_size()` and `copy_root()` serialize enough information to reopen the map.

## Dependencies And Integration Points
The header depends on `dm-block-manager.h` for `dm_block_t`. It is consumed by the transaction manager and by disk/metadata space-map implementations.

## Risks
Implementations must uphold rollback-safe allocation semantics or metadata transactions can become unrecoverable. Callers must not assume a block with zero count in the current map is immediately allocatable if it was allocated in the previous committed map. Threshold callbacks are optional and registration can fail with `-EINVAL`.

## Test Signals
Generic tests should run the same allocation/count/commit/root-copy scenarios against both disk and metadata implementations, including extension visibility, free-space accounting, and current-transaction free/reallocate behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/persistent-data/dm-space-map.h -->
