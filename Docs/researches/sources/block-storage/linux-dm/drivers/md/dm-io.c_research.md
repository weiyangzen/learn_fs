# File Research: sources/block-storage/linux-dm/drivers/md/dm-io.c

## Purpose
Implements the exported `dm_io()` helper used by DM targets to issue synchronous or asynchronous I/O to one or more block-device regions from several memory source types.

## Main Interfaces
- Client lifecycle: `dm_io_client_create()`, `dm_io_client_destroy()`.
- I/O submission: `dm_io()`.
- Module setup: `dm_io_init()`, `dm_io_exit()`.
- Internal dispatch: `sync_io()`, `async_io()`, `dispatch_io()`, `do_region()`.
- Memory adapters: page-list, bio, vmalloc/VMA, and kernel-memory `dpages` implementations.

## Control Flow
A caller supplies a `dm_io_request`, region array, operation, flags, memory description, optional callback, and optional error bitmap. `dm_io()` initializes a `dpages` adapter for the supplied memory type. Without a callback it performs synchronous I/O and waits for completion; with a callback it submits asynchronously.

`dispatch_io()` iterates regions, rewinding the page iterator for each region, and calls `do_region()`. `do_region()` splits requests into bios based on remaining sectors, page availability, operation type, and queue limits. Completion records region error bits and invokes the final callback when the aggregate atomic count reaches zero.

## State And Synchronization
Each `dm_io_client` owns a mempool of aligned `struct io` objects and a bioset. `struct io` tracks the aggregate completion count, error bits, callback, context, and VMA invalidation info. The region index is packed into low alignment bits of `bio->bi_private` alongside the `struct io` pointer.

## Integration Points
Used by DM targets for metadata, journal, copy, flush, and data movement I/O. It integrates with block-layer bios, queue limits for discard/write-zeroes/write-same, vmalloc cache flush/invalidate helpers, and DM reserved bio counts.

## Notable Behaviors
- Multi-region reads are rejected; multi-region I/O is only allowed for writes.
- Read errors zero-fill the bio before completion.
- VMA reads invalidate the kernel vmap range after completion.
- Discard, write zeroes, and write same requests are split according to device limits and fail with `BLK_STS_NOTSUPP` if unsupported.
- Asynchronous callers are warned in comments to use `REQ_SYNC` or unplug later to avoid delayed dispatch.

## Risks And Review Focus
- The pointer-plus-region packing depends on `struct io` alignment and `DM_IO_MAX_REGIONS`.
- The memory adapters assume caller-provided buffers cover the requested byte count.
- Multi-region write error bits must be interpreted by the caller.
- Special command splitting depends on current queue limits and can produce zero-bvec bios.
