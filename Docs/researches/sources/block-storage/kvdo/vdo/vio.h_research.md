# File Research: sources/block-storage/kvdo/vdo/vio.h

## Purpose
Defines the base VIO structure and helpers for metadata/data VIO identification, bio preparation, zone routing, and I/O completion continuation.

## Key Types
- `struct vio`: generic VDO I/O object with completion, physical block, bio zone, priority, type, block count, data buffer, owned bio, and merged-bio list.
- `MAX_BLOCKS_PER_VIO`: derived from `BIO_MAX_VECS` and `VDO_BLOCK_SIZE`.

## Public/Inline API
- Conversion: `as_vio()`, `vio_as_completion()`, `vdo_from_vio()`.
- Construction: `create_multi_block_metadata_vio()`, `create_metadata_vio()`, `initialize_vio()`, `free_vio()`.
- Routing: `set_vio_physical()`, `get_vio_bio_zone_thread_id()`, `assert_vio_in_bio_zone()`.
- Classification: `is_data_vio()`, `is_metadata_vio()`.
- I/O: `prepare_vio_for_io()`, `continue_vio()`, `continue_vio_after_io()`.
- Errors: `update_vio_error_stats()`, `record_metadata_io_error()`.

## Important Invariants
- `set_vio_physical()` must be used before I/O so `bio_zone` matches the PBN.
- Metadata priority maps to work queue priority via `get_metadata_priority()`.
- `continue_vio_after_io()` counts completed bios, sets the next callback/thread, and enqueues the completion with the bio result.
