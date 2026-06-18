# File Research: sources/block-storage/kvdo/vdo/data-vio.h

## Purpose
Defines `struct data_vio`, its substructures, async operation identifiers, conversion helpers, thread-affinity assertions, callback launch helpers, and public data_vio operations.

## Key Types
- `enum async_operation_number`: diagnostic state for the last async operation.
- `struct lbn_lock`: LBN, locked flag, waiter queue, logical zone.
- `struct tree_lock`: block-map tree traversal state and page lock waiters.
- `struct compression_state`: atomic compression status, compressed size, packer slot/bin, batch link, packer lock holder, compressed block.
- `struct allocation`: allocation zone, PBN, PBN lock, write lock type, first allocation zone, clean-slab wait flag.
- `struct data_vio`: full per-request state for VDO data I/O.

## Important `data_vio` Fields
- Embedded `struct vio`.
- Waiter link for internal wait queues.
- Logical lock, tree lock, mapped/new mapped locations.
- Chunk hash, duplicate advice/location, hash zone/lock.
- Recovery journal and flush generation state.
- User bio, partial block offset, discard remainder.
- Dedupe context pointer.
- Persistent pooled buffers: compression state, `data_block`, `scratch_block`, pool entry.

## Inline Helpers
- Type conversions: `vio_as_data_vio()`, `data_vio_as_vio()`, `as_data_vio()`, `data_vio_as_completion()`.
- Operation checks: read/write/read-modify-write/trim/FUA.
- Allocation helpers: `get_data_vio_allocation()`, `data_vio_has_allocation()`.
- Wait queue helpers: `enqueue_data_vio()`, waiter conversions.
- VDO/thread accessors: `vdo_from_data_vio()`, `get_thread_config_from_data_vio()`.

## Thread Routing
Provides assertion and callback launch helpers for:
- Hash zone
- Logical zone
- Allocated zone
- Duplicate zone
- Mapped zone
- New mapped zone
- Journal thread
- Packer thread
- Dedupe thread
- CPU thread
- Bio zone
- Bio ack queue

## Public Operations
Declares lifecycle, launch/completion, mapping updates, logical lock release, allocation, acknowledgement, compression/decompression, I/O preparation, and zero-block detection.

## Research Notes
This header encodes VDO’s asynchronous execution model. Most subsystem transitions are expressed by setting a completion callback to the owning thread and invoking it.
