# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/vio.h

## Purpose
`vio.h` declares the VDO I/O abstraction used by metadata and data paths. It exposes helpers for converting completions to VIOs, mapping VIOs to bio-zone threads, initializing VIO objects, resetting bios, accounting completions, and using pooled VIO entries.

## Important APIs, Types, and Functions
`MAX_BLOCKS_PER_VIO` derives the maximum VDO blocks addressable by bio vec limits. `struct pooled_vio` embeds a `struct vio`, pool linkage, and pool context. Inline helpers include `as_vio()`, `get_vio_bio_zone_thread_id()`, `assert_vio_in_bio_zone()`, `initialize_vio()`, `is_data_vio()`, `get_metadata_priority()`, `continue_vio()`, `continue_vio_after_io()`, and `vio_as_pooled_vio()`. Declarations cover VIO allocation/free, bio reset/properties, error stats, and pool operations.

## Control Flow
Callers initialize a VIO around a preallocated bio and VDO completion, then reset the bio per I/O with a target PBN, operation flags, buffer, and endio callback. Endio paths call `continue_vio_after_io()` to count completed bios, install the next completion callback, translate block status, and enqueue the completion. Pooled VIO users acquire asynchronously via a `vdo_waiter` callback and return entries to either the next waiter or the available list.

## State and Persistence Behavior
The header defines VIO state needed for persistence I/O but does not itself persist data. It guarantees that data VIOs are single-block through a `BUG_ON()` in `initialize_vio()`, while metadata VIOs can span up to `MAX_BLOCKS_PER_VIO`. Bio-zone state determines which VDO bio thread should submit the operation.

## Dependencies and Integration Points
`vio.h` includes Linux bio/blkdev/list APIs and VDO completion, constants, types, and VDO declarations. It is used by metadata components, io-submitter, VDO superblock/geometry code, data-vio handling, and statistics collection.

## Risks and Test Signals
The interface is sensitive to callback-thread IDs, bio-zone calculation, completion type correctness, and error propagation. Useful tests assert that completion-to-VIO conversions reject wrong types, data VIOs cannot be multi-block, metadata priority maps to the expected work queue priority, and `continue_vio_after_io()` preserves the first non-success result.
