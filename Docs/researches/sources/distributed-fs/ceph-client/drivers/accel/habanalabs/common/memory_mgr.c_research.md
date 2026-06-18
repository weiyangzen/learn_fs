# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/common/memory_mgr.c

## Purpose
This file provides a generic handle-based mmap buffer manager for driver-owned buffers exposed to userspace. It is used by timestamp buffers and is suitable for other mappable buffer behaviors.

## Important APIs, Types, And Functions
`hl_mmap_mem_buf_alloc()` allocates and registers a behavior-backed buffer. `hl_mmap_mem_buf_get()`, `hl_mmap_mem_buf_put()`, and `hl_mmap_mem_buf_put_handle()` manage kref lifetime. `hl_mem_mgr_mmap()` maps a handle into a VMA. `hl_mem_mgr_init()`, `hl_mem_mgr_fini()`, and `hl_mem_mgr_idr_destroy()` manage the IDR store. Behavior callbacks provide `alloc`, `mmap`, and `release`.

## Control Flow
Allocation creates a descriptor, reserves an IDR ID, builds a page-shifted handle containing the memory type, initializes the kref, and calls behavior allocation. Mmap decodes the handle from `vm_pgoff`, takes a reference, validates exact size and user access, rejects double mapping, installs VMA ops/private data, and delegates to the behavior. VMA close drops the reference once the whole mapped extent is closed.

## State And Persistence
State includes `mmg->handles`, spinlock, and each buffer's handle, kref, behavior, mmap flag, mappable size, real mapped size, and behavior-private pointer. Fini can report leaked/busy CB, timestamp, or other buffers.

## Dependencies And Integration Points
It depends on IDR, kref, VMA ops, access checks, and higher-level behavior callbacks. It integrates with `habanalabs_drv.c` file-private setup, timestamp buffers in `memory.c`, and timestamp cleanup in `irq.c`.

## Risks
Release callbacks used with interrupt-safe put must not sleep. Partial VMA close accounting is lockless. IDR destruction while non-empty is only reported, so caller teardown order is essential.

## Test Signals
Test failed lookup, callback allocation failure, mmap size mismatch, invalid user range, double mmap, partial and final VMA close, busy stats, put-by-handle, and non-empty IDR destruction.
