# sources/distributed-fs/ceph-client/mm/migrate_device.c

## Purpose
Implements HMM/device-memory migration between CPU system memory, device-private memory, and device-coherent memory. It provides the driver-facing `migrate_vma_*()` workflow for virtual-address-based migration and PFN-range helpers for moving device private pages back to normal memory when a driver needs to evict or release device memory.

## Important APIs, Types, and Functions
Exported APIs are `migrate_vma_setup()`, `migrate_vma_pages()`, `migrate_vma_finalize()`, `migrate_device_pages()`, `migrate_device_finalize()`, `migrate_device_range()`, `migrate_device_pfns()`, and `migrate_device_coherent_folio()`. The central caller-provided type is `struct migrate_vma`, whose `vma`, `start`, `end`, `src`, `dst`, `npages`, `cpages`, `flags`, `pgmap_owner`, and optional `fault_page` fields describe the migration operation.

Important local helpers include `migrate_vma_collect_pmd()` and `migrate_vma_collect_huge_pmd()` for walking CPU page tables, `migrate_device_unmap()` for LRU isolation and rmap unmapping, `__migrate_device_pages()` for moving `struct page` metadata, `migrate_vma_insert_page()` and `migrate_vma_insert_huge_pmd_page()` for populating anonymous holes, and `__migrate_device_finalize()` for restoring CPU page tables and unlocking pages.

## Control Flow
The virtual-address workflow starts with `migrate_vma_setup()`, which validates VMA constraints, page-aligned range bounds, source/destination arrays, and optional locked device-private fault pages. It clears the source array, starts an MMU notifier `MMU_NOTIFY_MIGRATE` invalidation, walks the range, and records one source PFN entry per base page or one compound entry for PMD-sized THP migration. Present system pages, device-private swap entries, device-coherent pages, zero pages, and anonymous holes are either selected for migration or skipped according to `MIGRATE_VMA_SELECT_*` flags and `pgmap_owner`.

Collection installs migration entries opportunistically while holding page-table locks when it can lock the backing folio. Large folios are either collected as compound PMD migrations when selected and aligned, or split before base-page collection. After collection, `migrate_vma_unmap()` isolates non-device folios from LRU, calls `try_to_migrate()` for remaining mappings, checks for pins with `migrate_vma_check_page()`, restores pinned pages immediately, and leaves successfully selected pages locked and unmapped for driver copying.

The driver allocates and locks destination pages, copies data, writes `MIGRATE_PFN_VALID` destination PFNs, then calls `migrate_vma_pages()`. `__migrate_device_pages()` handles anonymous hole population, optional compound splitting when source and destination granularity differ, rejects unsupported ZONE_DEVICE destination types, frees swapcache for anonymous migration to device memory where possible, calls `folio_migrate_mapping()`, and copies folio flags. `migrate_vma_finalize()` then adds non-device destination folios to LRU, removes migration PTEs to either destination or source, unlocks pages, and drops references.

The PFN workflows `migrate_device_range()` and `migrate_device_pfns()` lock device PFNs directly with `migrate_device_pfn_lock()`, mark compound groups, call `migrate_device_unmap()`, and let drivers use `migrate_device_pages()` and `migrate_device_finalize()` without a VMA walk. `migrate_device_coherent_folio()` is a single-folio helper that migrates a device-coherent folio back to normal memory by unmapping, allocating a base system folio, moving metadata, copying contents on success, and finalizing.

## State and Persistence Behavior
During setup, source PTEs are replaced by migration entries or device-private entries and MMU notifiers tell device drivers to invalidate secondary mappings. Source and destination arrays carry persistent-in-the-operation flags such as `MIGRATE_PFN_MIGRATE`, `MIGRATE_PFN_WRITE`, `MIGRATE_PFN_COMPOUND`, and encoded PFNs. Folios remain locked across driver copy and page-table update phases, so drivers can inspect success after `migrate_vma_pages()` but before finalization.

Successful migration transfers address-space metadata and folio flags through the generic migration helpers, updates CPU page tables to the new page or restores the old page, adjusts LRU state for non-device pages, and drops operation references. Failed or skipped entries have `MIGRATE_PFN_MIGRATE` cleared and are restored to their original mapping during finalization.

## Dependencies and Integration Points
This file depends on MMU notifiers, page walking, rmap migration entries, `memremap`/`dev_pagemap`, ZONE_DEVICE page types, THP split/PMD helpers, anon_vma preparation, memcg charging, LRU isolation, and the generic migration helpers in `migrate.c`. It is designed for GPU, accelerator, and heterogeneous-memory drivers that mirror CPU page tables and need to migrate anonymous memory to/from device-owned memory.

## Risks and Edge Cases
Risk concentrates around secondary MMU synchronization, driver ownership filtering by `pgmap_owner`, compound THP selection and fallback splitting, preserving write/dirty/young/soft-dirty/uffd-wp state in migration entries, handling anonymous holes without delivering userfaultfd faults, memcg charge failure after driver allocation, and pinned-page detection. Device-private memory migration back to system memory must not fail lightly because an unserviceable device fault can become `SIGBUS`; the setup comments explicitly warn drivers about this. Unsupported ZONE_DEVICE types, DAX/special/hugetlb VMAs, unaligned or out-of-VMA ranges, and unlocked fault pages are rejected.

## Test Signals
Useful signals include HMM selftests or GPU-driver tests that migrate anonymous pages to device-private memory and back, device-coherent folio eviction, range-based migration during driver unload, write-protected and uffd-wp mappings, zero-page and anonymous-hole population, pinned-page rejection, THP compound migration and split fallback, memcg charge failure, mmu-notifier ordering observed by a secondary page table, and fault-page paths where the fault folio remains locked by the caller.
