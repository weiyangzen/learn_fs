# File Research: sources/block-storage/kvdo/vdo/data-vio.c

## Purpose
Implements `data_vio` allocation, initialization, launch, logical lock handling, completion, allocation lock handling, bio acknowledgement, compression/decompression, and block utility functions.

## Key Functions
- `allocate_data_vio_components()` allocates `data_block`, `compression.block`, `scratch_block`, and creates the backing bio.
- `initialize_data_vio()` and `destroy_data_vio()` manage per-VIO allocated components.
- `launch_data_vio()` resets per-request state, initializes the LBN lock, sets mapping state based on write/discard type, and starts logical lock acquisition.
- `attempt_logical_block_lock()` serializes requests by logical block using the logical zone’s `lbn_operations` map.
- `vdo_release_logical_block_lock()` releases or transfers an LBN lock to the next waiter.
- `data_vio_allocate_data_block()` selects an allocation zone and launches allocation callback.
- `release_data_vio_allocation_lock()` releases PBN allocation lock and optionally resets allocation.
- `acknowledge_data_vio()` completes the original user bio and updates stats.
- `compress_data_vio()` performs LZ4 compression into `compression.block->data`, with `VDO_BLOCK_SIZE + 1` as uncompressible sentinel.
- `uncompress_data_vio()` extracts a compressed fragment and uses LZ4 safe decompression.
- `is_zero_block()` checks a block by 64-bit words.

## Logical Lock Behavior
A request outside configured logical range fails with `VDO_OUT_OF_RANGE`. If a read arrives behind a writing lock holder that already has an allocation, the read can be satisfied directly from the lock holder’s `data_block`; otherwise it queues and may cancel the holder’s compression to avoid packer blocking.

## Completion Flow
- `complete_data_vio()` chooses read or write cleanup after recording errors.
- `finish_data_vio()` sets completion result then calls `complete_data_vio()`.
- `get_data_vio_operation_name()` maps async operation enum values to diagnostic strings.

## Dependencies
Interacts with logical zones, physical zones, block map, allocation selector, packer, dedupe, journals, bio helpers, and VDO completion infrastructure.

## Research Notes
This file is the operational center for user data requests. `data-vio.h` carries much of the thread-routing inline machinery used by this implementation.
