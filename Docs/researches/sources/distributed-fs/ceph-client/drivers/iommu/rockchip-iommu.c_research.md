# sources/distributed-fs/ceph-client/drivers/iommu/rockchip-iommu.c

## Purpose
This file implements the Rockchip IOMMU driver. It manages Rockchip two-level page tables, hardware register banks, clocks/runtime PM, stall/paging commands, page-fault IRQs, and generic IOMMU domain operations for Rockchip display/media masters.

## Important APIs, Types, And Functions
`struct rk_iommu_domain` owns the directory table, DMA address, attached IOMMU list, locks, DMA device, and embedded generic domain. `struct rk_iommu` represents one platform IOMMU that may expose multiple MMU register banks and IRQs. `struct rk_iommu_ops` abstracts v1/v2 descriptor encoding, physical address extraction, DMA mask, and allocation flags. `struct rk_iommudata` stores the per-master IOMMU pointer and runtime PM device link.

Important helpers include descriptor encoders/extractors `rk_mk_dte()`, `rk_mk_dte_v2()`, `rk_mk_pte()`, `rk_mk_pte_v2()`, `rk_ops->pt_address()`, index helpers, register commands, `rk_iommu_enable_stall()`, `rk_iommu_disable_stall()`, `rk_iommu_enable_paging()`, `rk_iommu_disable_paging()`, and `rk_iommu_force_reset()`. Generic ops are `rk_iommu_attach_device()`, `rk_iommu_identity_attach()`, `rk_iommu_map()`, `rk_iommu_unmap()`, `rk_iommu_iova_to_phys()`, `rk_iommu_domain_alloc_paging()`, `rk_iommu_domain_free()`, `rk_iommu_probe_device()`, `rk_iommu_release_device()`, and `rk_iommu_of_xlate()`.

## Control Flow
Probe allocates the IOMMU instance, selects v1/v2 ops from the compatible string, maps all memory resources as MMU banks, counts IRQs, reads optional reset-disable property, prepares optional clocks, enables runtime PM, requests shared IRQs, sets the DMA mask, and registers the IOMMU core device. The first matched ops table becomes global `rk_ops`; mixed hardware versions in one kernel instance are rejected.

Domain allocation creates a 4 KiB directory table, maps it for DMA, initializes locks and the attached-IOMMU list, and exposes page sizes from 4 KiB up to one page table worth of contiguous PTEs. Attach first detaches from identity, links the IOMMU into the domain list, and if the hardware is powered, enables hardware by stalling, force-resetting, programming DT address for all banks, zapping cache, enabling IRQs, and enabling paging. Detach switches to identity, removes from the list, and disables hardware if powered.

Mapping obtains or allocates the relevant page table under `dt_lock`, refuses remapping over a valid PTE, writes contiguous PTEs, flushes table cache lines, and zaps first/last IOVA lines to remove stale DTE/PTE cachelines. Unmap clears valid PTEs until it sees an invalid entry, flushes table entries, then zaps the unmapped IOVA range across all powered IOMMUs attached to the domain. IRQ handling powers/clocks the device if active, logs page-fault or bus-error status per bank, calls `report_iommu_fault()` unless identity-attached, zaps cache, clears page fault, and acknowledges interrupts.

## State And Persistence
Persistent state includes the domain DT page, lazily allocated PT pages, DMA mappings, attached IOMMU list, runtime PM device links, prepared clocks, and per-IOMMU current domain pointer. Hardware state includes DTE_ADDR, command/status, IRQ masks, page-fault address, and auto-gating registers. Page tables are freed during domain free after warning if still attached.

## Dependencies And Integration Points
The driver integrates with OF platform bindings `rockchip,iommu` and `rockchip,rk3568-iommu`, runtime PM, clock bulk APIs, DMA mapping, generic single-device IOMMU groups, device links from masters to the IOMMU device, and generic fault reporting.

## Risks
Global `rk_ops` prevents mixing v1/v2 descriptor formats in one running driver instance. Page-table physical address extraction assumes `phys_to_virt()` access to allocated tables. TLB zap uses first/last optimization on map and full per-page loop on unmap; stale intermediate cachelines are assumed not to matter on map. Runtime PM means many operations skip powered-off IOMMUs and rely on resume reprogramming. Fault IRQ logging dereferences page tables from hardware-reported addresses, so corrupted DTE_ADDR/PTE state can affect diagnostics.

## Test Signals
Probe on v1 and rk3568-compatible v2 hardware, map/unmap across 4 KiB to 4 MiB sizes, remap rejection, runtime suspend/resume with attached domain, IRQ fault injection for read/write and bus error, multi-bank register programming, device-link PM ordering, optional clock absence, and reset-disabled boards.
