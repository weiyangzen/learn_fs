# sources/distributed-fs/ceph-client/drivers/iommu/sun50i-iommu.c

## Purpose
This file implements the Allwinner sun50i H6/H616 IOMMU driver. It manages a two-level 32-bit page table, permission-domain encoding, TLB/PTW invalidation, reset/clock control, fault IRQ handling, and generic IOMMU domain operations.

## Important APIs, Types, And Functions
`struct sun50i_iommu` stores the IOMMU core object, register lock, device, MMIO base, reset, clock, current domain, and L2 page-table slab pool. `struct sun50i_iommu_domain` embeds the generic domain, refcount, L1 directory table, DMA address, and attached IOMMU pointer. Descriptor helpers include DTE/PTE index extraction, `sun50i_mk_dte()`, `sun50i_mk_pte()`, `sun50i_dte_is_pt_valid()`, `sun50i_pte_is_page_valid()`, and PTE authority-control decoding.

Cache and hardware helpers include `sun50i_table_flush()`, `sun50i_iommu_zap_iova()`, `sun50i_iommu_zap_ptw_cache()`, `sun50i_iommu_zap_range()`, `sun50i_iommu_flush_all_tlb()`, `sun50i_iommu_enable()`, `sun50i_iommu_disable()`, `sun50i_iommu_alloc_page_table()`, and `sun50i_dte_get_page_table()`. IOMMU core hooks include domain allocation/free, attach/detach/identity attach, map/unmap, iova-to-phys, TLB sync, probe-device, and OF xlate. Fault handling is in `sun50i_iommu_irq()`, `sun50i_iommu_handle_pt_irq()`, `sun50i_iommu_handle_perm_irq()`, and `sun50i_iommu_report_fault()`.

## Control Flow
Probe allocates the IOMMU, initializes the register lock, starts in identity domain, creates a DMA32 slab cache for L2 page tables, maps MMIO, gets IRQ/clock/reset, registers the IOMMU core device, and requests the IRQ. Domain allocation creates a 4096-entry L1 directory table in DMA32 memory, sets a 4 KiB page size bitmap, and forces a 32-bit aperture.

Attach increments the domain refcount, detaches any old domain through identity attach, DMA-maps the L1 table, stores cross-pointers, deasserts reset, enables the clock, programs TTB, TLB prefetch, bypass disable, interrupt mask, permission-domain access-control registers, flushes all TLB state, enables auto-gating, and enables the IOMMU. Detach frees every valid L2 page table, disables hardware, unmaps the L1 table, and clears the domain pointer.

Mapping rejects physical addresses above 4 GiB, lazily allocates or races to install a 1 KiB L2 page table, rejects remapping a valid PTE, writes a single 4 KiB PTE with authority index derived from `IOMMU_READ`/`IOMMU_WRITE`, flushes the entry, and reports the mapped size. Unmap clears one valid PTE and flushes it. TLB sync-map zaps selected IOVA and PTW-cache entries under the hardware lock; generic unmap sync flushes all TLBs.

Fault IRQ flow reads global and L1/L2 status under the register lock, classifies invalid L1/L2 page faults versus permission faults, reports through `report_iommu_fault()`, zaps the faulting range, clears interrupt status, resets affected masters, and releases reset for all masters.

## State And Persistence
Persistent state includes the domain L1 directory, slab-allocated DMA-mapped L2 tables, refcounted domain attachment, current hardware domain pointer, reset/clock handles, and hardware permission-domain configuration. Hardware-visible table entries are explicitly DMA-synchronized after updates.

## Dependencies And Integration Points
The driver uses OF platform compatibles `allwinner,sun50i-h6-iommu` and `allwinner,sun50i-h616-iommu`, Linux IOMMU core, reset and clock frameworks, DMA mapping, `iommu-pages` allocation helpers, generic single-device groups, and generic fault reporting.

## Risks
The driver supports only 32-bit IOVA/physical addresses and 4 KiB mappings. Attach error handling does not propagate the return from `sun50i_iommu_attach_domain()` in `sun50i_iommu_attach_device()`, so enable failures deserve scrutiny. The refcount starts at one and is incremented on attach, making detach/free lifetime behavior important to test. TLB range zapping invalidates selected boundary addresses and PTW cache lines, while unmap sync flushes all; correctness depends on hardware cache behavior. Some fault classification defaults to read when direction cannot be inferred.

## Test Signals
Probe on H6/H616 DT, attach/detach with reset and clock sequencing, map/unmap/iova-to-phys for 4 KiB pages, remap rejection, >4 GiB physical-address rejection, TLB/PTW invalidation timeout handling, permission fault direction tests for RD/WR/NONE authority indices, invalid L1/L2 fault tests, runtime behavior with multiple masters, and domain refcount/lifetime tests.
