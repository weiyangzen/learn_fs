# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/vio.c

## Purpose
`vio.c` implements VDO I/O object support. It allocates VDO-owned bios, initializes metadata VIOs, maps VIOs to backing-device bios, records metadata I/O errors, manages thread-affine VIO pools, and maintains bio statistics for VDO-generated and externally serviced I/O.

## Important APIs, Types, and Functions
The local `struct vio_pool` owns preallocated `pooled_vio` entries, a shared data buffer, available/busy lists, a wait queue, and the VDO thread on which it may be used. Important functions include `pbn_from_vio_bio()`, `vdo_create_bio()`, `allocate_vio_components()`, `create_multi_block_metadata_vio()`, `vio_reset_bio_with_size()`, `update_vio_error_stats()`, `vio_record_metadata_io_error()`, `make_vio_pool()`, `acquire_vio_from_pool()`, `return_vio_to_pool()`, and bio accounting helpers.

## Control Flow
Metadata VIO creation allocates a VIO-owned bio sized for one or more VDO blocks, initializes completion metadata, and attaches an optional parent and data buffer. Submission paths reset the bio, set device/operation/endio/sector properties, build inline bvecs from kernel or vmalloc memory, and later continue the VIO completion after endio. VIO pools synchronously hand an available entry to a waiter callback or enqueue the waiter until `return_vio_to_pool()` notifies the oldest waiter.

## State and Persistence Behavior
VIOs do not persist state directly, but they are the mechanism used by superblock, geometry, journal, and block-map metadata to reach storage. The pool tracks `busy_count`, busy and available lists, and waiters. Error handling increments read-only, no-space, and other error counters and rate-limits log output. `pbn_from_vio_bio()` reverses the bio sector mapping to report physical block numbers with geometry offset accounted for.

## Dependencies and Integration Points
The file depends on Linux bio/blkdev/page APIs, ratelimit logging, VDO memory allocation, assertions, constants, io-submitter, wait queues, and `vdo.h`. It integrates with completion scheduling via `continue_vio_after_io()`, and its statistics feed the VDO statistics reported by `vdo_fetch_statistics()`.

## Risks and Test Signals
Important risks are bvec construction for vmalloc vs direct memory, multi-block size bounds, thread-affine pool misuse, returning pooled VIOs while waiters exist, and accounting errors when endio paths are retried. Tests should cover unaligned buffer offsets, maximum block counts, pool starvation/wakeup order, metadata I/O failures, and statistic increments for reads, writes, discards, flushes, FUA, and empty flushes.
