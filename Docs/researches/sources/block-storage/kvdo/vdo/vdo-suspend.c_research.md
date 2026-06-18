# File Research: sources/block-storage/kvdo/vdo/vdo-suspend.c

## Purpose
Implements VDO suspend by draining all active work, flushing persisted data, waiting for read-only transitions, and saving clean state when appropriate.

## Suspend Phases
- Start draining with the configured suspend type.
- Drain packer.
- Drain data VIO pool.
- Drain dedupe/hash zones.
- Drain flushes.
- Synchronously flush backing storage and drain logical zones.
- Drain block map.
- Drain recovery journal.
- Drain slab depot.
- Wait for read-only-mode entry to settle.
- Save clean superblock if this is a true suspend and no error occurred.
- Finish draining.

## Key Functions
- `vdo_suspend()` starts the admin suspend operation and maps expected read-only results to success.
- `suspend_callback()` drives phase transitions.
- `write_super_block()` records `VDO_CLEAN` for `VDO_DIRTY` or `VDO_NEW`, then saves components.
- `get_thread_id_for_phase()` routes packer/flusher phases to packer thread, data VIO phase to CPU thread, journal phase to journal thread, and others to admin.

## Important Behavior
- Device-mapper may suspend the device even if this post-suspend work reports an error.
- If already read-only, the operation records `VDO_READ_ONLY` so partially resumed components do not cause `VDO_INVALID_ADMIN_STATE`.
- Logical-zone phase issues `vdo_synchronous_flush()` before draining metadata paths.
- `VDO_READ_ONLY` is returned to callers as suspend success.
