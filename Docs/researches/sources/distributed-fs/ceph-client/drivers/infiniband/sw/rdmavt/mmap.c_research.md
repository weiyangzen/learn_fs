<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/rdmavt/mmap.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/sw/rdmavt/mmap.c

## Purpose

Implements rdmavt userspace mmap bookkeeping for vmalloc-backed objects such as CQs, QPs, and SRQs, while reserving a low offset range for driver-specific mmap handlers.

## Important APIs, Types, And Functions

`rvt_mmap_init()` initializes pending mmap lists and offset counters. `rvt_create_mmap_info()` creates a pending map descriptor and allocates a dynamic offset. `rvt_update_mmap_info()` updates an existing descriptor after object resize. `rvt_mmap()` resolves offsets to pending descriptors and maps vmalloc memory with `remap_vmalloc_range()`. `rvt_release_mmap_info()`, `rvt_vma_open()`, and `rvt_vma_close()` manage krefs.

## Control Flow

Objects that need userspace mapping create mmap info and put it on `pending_mmaps`. Userspace receives the offset through udata and calls mmap. `rvt_mmap()` delegates reserved offsets below `MMAP_OFFSET_START` to the driver, otherwise finds a matching context and offset, rejects oversized mappings, removes the pending entry, maps the vmalloc object, and installs VM open/close ops for lifetime tracking.

## State And Persistence Behavior

Per-device state includes `pending_mmaps`, `pending_lock`, `mmap_offset`, and `mmap_offset_lock`. Each `rvt_mmap_info` holds offset, size, context, object pointer, pending list node, and kref. Mapped objects persist until the final VMA close and object ref release.

## Dependencies And Integration Points

Used by rdmavt CQ resize/create and other mmap-capable objects. Depends on RDMA uverbs context, vmalloc remapping, VMA operations, and optional driver mmap callback.

## Risks And Edge Cases

Offsets increment by one page regardless of object size, making offset uniqueness rather than range reservation the key contract. Only the creating context can map an object. `rvt_release_mmap_info()` deletes from the pending list even after `list_del_init()` in mmap; list state must remain valid. Objects resized before mmap must update offset and re-add pending state correctly.

## Test Signals

Test reserved-offset delegation, wrong context rejection, oversized mmap rejection, successful remap, VMA open/close refcounting, resize offset update, wrap/reset of offset counter, and destroy before mmap.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/rdmavt/mmap.c -->
