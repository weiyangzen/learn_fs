<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dm-io.h -->
# sources/distributed-fs/ceph-client/include/linux/dm-io.h

## Purpose
Declares Device Mapper's low-level multi-region I/O helper for reading or writing one memory source to one or more block-device regions.

## Important APIs, Types, And Functions
Key types are `struct dm_io_region`, `struct page_list`, `enum dm_io_mem_type`, `struct dm_io_memory`, `struct dm_io_notify`, `struct dm_io_client`, and `struct dm_io_request`. APIs are `dm_io_client_create()`, `dm_io_client_destroy()`, and `dm_io()`. Memory can be represented as a page list, bio, VMA, or kernel memory.

## Control Flow
Callers create a client with private pools, fill a `dm_io_request` with operation flags, memory description, optional callback, and regions, then call `dm_io()`. If `notify.fn` is NULL the call is synchronous and can report per-region errors through `sync_error_bits`; otherwise completion is delivered asynchronously.

## State And Persistence
State is transient I/O request state and client memory pools. Persistent effects depend on the submitted block operation and target device.

## Dependencies And Integration Points
Depends on block operation flags, bios/pages, block devices, and DM targets needing low-level metadata or copy I/O.

## Risks And Edge Cases
Regions with zero count are ignored. The `sync_error_bits` mapping must match region ordering. Memory type, offset, and length must describe enough data for all regions. Callback context and client lifetime must outlive async I/O.

## Test Signals
Tests should cover sync and async reads/writes, multiple regions, ignored zero-length regions, all memory types, per-region error bits, ioprio propagation, and client teardown only after async completions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dm-io.h -->
