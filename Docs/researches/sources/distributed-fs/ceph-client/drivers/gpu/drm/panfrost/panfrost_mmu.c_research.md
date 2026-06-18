# sources/distributed-fs/ceph-client/drivers/gpu/drm/panfrost/panfrost_mmu.c

## Purpose
This file implements Panfrost GPU MMU contexts, page-table setup, GPU virtual address allocation support, map/unmap, address-space assignment and LRU reuse, lazy heap fault mapping, MMU IRQ handling, and context teardown.

## Important APIs, Types, and Functions
Public entry points are `panfrost_mmu_ctx_create/get/put`, `panfrost_mmu_map`, `panfrost_mmu_unmap`, `panfrost_mmu_as_get/put`, `panfrost_mmu_reset`, `panfrost_mmu_init/fini`, and `panfrost_mmu_suspend_irq`. Internal helpers configure Mali LPAE or AArch64 page tables, encode memory attributes, flush hardware ranges, map sg tables, translate faults to mappings, and allocate heap pages on page fault.

## Control Flow
Context creation chooses page-table format from compatible quirks and hardware features, initializes a 32 MiB-4 GiB drm_mm VA space with executable color adjustment, allocates io-pgtable ops, and stores hardware MMU config. BO mapping walks DMA sg entries and maps 4 KiB/2 MiB pages through io-pgtable, then flushes the GPU range if the AS is active. `as_get` either reuses an assigned address space, re-enables a previously faulty AS, picks a free AS, or evicts an idle LRU AS and programs hardware registers. MMU threaded IRQ handles page faults; heap faults allocate/map 2 MiB chunks, while unhandled faults disable the AS and mask its interrupts.

## State and Persistence Behavior
State includes per-context page tables, drm_mm VA allocator, AS number, AS refcount, hardware config, device AS allocation/fault masks, AS LRU list, heap BO sg tables/pages, and mapping active bits. Runtime PM gates hardware TLB flushes.

## Dependencies and Integration Points
It integrates io-pgtable, DRM MM, GEM shmem and heap BOs, DMA mapping, runtime PM, platform IRQs, Panfrost registers/features, device reset, and job manager AS get/put.

## Risks
AS allocation and LRU eviction are protected by `as_lock`; mistakes can assign one AS to multiple contexts. Heap fault mapping assumes 2 MiB alignment and can leak or double-own folios if partial population invariants fail. TLB flushes are skipped when runtime-suspended, relying on reprogramming later. Unhandled faults disable AS to kill jobs, so recovery depends on later AS get/reset.

## Test Signals
Test BO map/unmap, per-file VA allocation, executable boundary constraints, AS reuse under many clients, heap BO page faults, MMU fault logging, reset after AS_ACTIVE timeout, runtime suspend during mapping changes, and AArch64 page-table compatible quirks.
