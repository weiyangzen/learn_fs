# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/common/memory.c

## Purpose
This file implements HabanaLabs memory UAPI behavior: device DRAM allocation/free, host userptr pinning, DMA mapping, device virtual-address management, MMU map/unmap, hardware block mmap, dma-buf export, timestamp-buffer allocation, and VM lifecycle.

## Important APIs, Types, And Functions
`hl_mem_ioctl()` dispatches memory operations. `alloc_device_memory()`/`free_device_memory()` manage DRAM page packs. `hl_pin_host_memory()`/`hl_unpin_host_memory()` and `dma_map_host_va()`/`dma_unmap_host_va()` manage userptrs. `get_va_block()`, `hl_reserve_va_block()`, and `hl_unreserve_va_block()` manage VA ranges. `map_device_va()`/`unmap_device_va()` connect handles or userptrs to MMU mappings. `export_dmabuf_from_addr()` implements dma-buf export. VM lifecycle is `hl_vm_init/fini()` and `hl_vm_ctx_init/fini()`.

## Control Flow
Allocation rounds to page size, allocates from a DRAM gen_pool, stores a page pack in an IDR, and updates DRAM counters. Mapping either pins host memory or finds a DRAM handle, reserves a VA block with hint/alignment rules, maps pages under `mmu_lock`, invalidates/prefetches MMU caches, and inserts a hash node. Unmap removes the hash node, unmaps pages, invalidates caches, returns the VA block, and releases mapping/userptr references. Context teardown forcibly unmaps leaked mappings and frees remaining page packs.

## State And Persistence
State includes the device DRAM gen_pool, physical page pack IDR/refcounts, DRAM usage counters, context VA free lists, memory hash, userptr SG tables, dma-buf export count, hardware block mmap list, and timestamp mmap buffers.

## Dependencies And Integration Points
It depends on MMU callbacks, DMA/SG APIs, gen_pool, IDR, get_user_pages, dma-buf, PCI P2P distance checks, debugfs hooks, `memory_mgr.c`, and timestamp interrupt handling in `irq.c`.

## Risks
VA split/merge correctness is central. Error paths must unwind mapping counts, DMA maps, page packs, and VA reservations. Exported dma-bufs prevent unmap through `export_cnt`. Userptr long-term pins can fail partially. Non-VM DRAM accounting trusts userspace.

## Test Signals
Test page-size choices, contiguous/non-contiguous allocation, map/unmap hints, forced hints, huge userptr mappings, MMU failure unwind, leaked mapping teardown, dma-buf export/release, timestamp mmap, and fault injection across allocation/IDR/DMA steps.
