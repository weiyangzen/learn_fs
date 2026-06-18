# File Research: sources/block-storage/kvdo/vdo/vio.c

## Purpose
Implements metadata VIO allocation/freeing and common VIO error logging/statistics helpers.

## Key Functions
- `create_multi_block_metadata_vio()` allocates a metadata `struct vio`, creates a bio sized for multiple VDO blocks, initializes completion/type/priority, and attaches caller data.
- `free_vio()` frees non-data VIOs and their bios.
- `update_vio_error_stats()` increments read-only/no-space/error stats and rate-limits error logging.
- `record_metadata_io_error()` formats operation type from bio flags and records a metadata I/O error.

## Important Behavior
- Metadata VIOs are allocated directly, not from the data bio buffer pool.
- `MAX_BLOCKS_PER_VIO` is enforced by assertion.
- `struct vio` is asserted to remain at or below 256 bytes.
- `VDO_READ_ONLY` increments stats but is not logged as an error.
- `VDO_NO_SPACE` is logged at debug priority.
