# sources/distributed-fs/ceph-client/drivers/infiniband/core/ib_core_uverbs.c

## Purpose
This file implements shared RDMA uverbs helpers for userspace mmap tracking, IO memory mapping, mmap-entry allocation/removal, dma-buf revocation integration, and resolving a live `ib_device` from uverbs request data. It supports hot-unplug/disassociation by tracking VMAs and preventing new mappings after driver removal.

## Important APIs, Types, And Functions
Exported APIs include `rdma_umap_priv_init()`, `rdma_user_mmap_io()`, `rdma_user_mmap_entry_get_pgoff()`, `rdma_user_mmap_entry_get()`, `rdma_user_mmap_entry_put()`, `rdma_user_mmap_entry_remove()`, `rdma_user_mmap_entry_insert_range()`, `rdma_user_mmap_entry_insert()`, and `rdma_udata_to_dev()`. Main state types are `struct rdma_umap_priv`, `struct rdma_user_mmap_entry`, `struct ib_ucontext`, `struct ib_uverbs_file`, and `struct ib_uverbs_dmabuf_file`.

## Control Flow
Drivers insert mmap entries into a ucontext xarray with `_insert_range()` or `_insert()`, which finds a contiguous page-offset range under `ufile->umap_lock` and `mmap_xa`, stores the entry in every slot, initializes refcount/dma-buf state, and records `start_pgoff`/`npages`. Mmap retrieves entries by offset, validates shared mapping and exact size, rejects removed entries, remaps PFNs, and links a VMA private object into the file's `umaps` list. Removal marks entries `driver_removed`, revokes attached dma-bufs, invalidates mappings, waits for fences/completions, and drops the final reference so xarray slots and provider `mmap_free()` are released.

## State And Persistence
State is runtime-only per uverbs file and ucontext. `mmap_xa` stores page-offset ownership; `umap_lock` serializes range allocation and VMA list updates; mmap entries have krefs, dma-buf lists, and removal gates. Active VMAs hold references through `rdma_umap_priv`, delaying provider cleanup until userspace unmaps.

## Dependencies And Integration Points
The file depends on uverbs core types, xarray, Linux VMA/MM helpers, IO PFN remapping, SRCU disassociation, dma-buf reservation/invalidation APIs, and optional provider `mmap_free()`. Drivers mapping BARs or doorbells use these helpers from provider mmap implementations.

## Risks And Test Signals
Risks include accepting non-shared mappings, size/offset mismatches, entry use after driver removal, dma-buf revocation races, leaking multi-page xarray slots, and deadlocks around reservation locks or disassociate SRCU. Tests should cover correct and incorrect mmap sizes, non-shared mappings, offset reuse after close, concurrent mmap/remove, hot unplug with live VMAs, dma-buf invalidation, range exhaustion, provider `mmap_free()` timing, and lockdep coverage.
