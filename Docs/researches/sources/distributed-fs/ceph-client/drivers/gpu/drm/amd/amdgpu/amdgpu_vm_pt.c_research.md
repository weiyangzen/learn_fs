# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_vm_pt.c

## Purpose

This file owns AMDGPU VM page-directory/page-table allocation, traversal, clearing, PDE updates, PTE updates, huge-page fragment selection, and page-table freeing after TLB flush. It is the structural page-table layer used by the VM core regardless of whether entries are written by CPU or SDMA.

## Important APIs, types, and functions

The internal `struct amdgpu_vm_pt_cursor` tracks a walk by PFN, parent entry, current entry, and level. Important helpers include `amdgpu_vm_pt_level_shift()`, `amdgpu_vm_pt_num_entries()`, `amdgpu_vm_pt_entries_mask()`, `amdgpu_vm_pt_size()`, cursor descendant/sibling/ancestor/DFS helpers, and `for_each_amdgpu_vm_pt_dfs_safe`. Exported APIs are `amdgpu_vm_pt_clear()`, `amdgpu_vm_pt_create()`, `amdgpu_vm_pt_free_list()`, `amdgpu_vm_pt_free_root()`, `amdgpu_vm_pde_update()`, `amdgpu_vm_ptes_update()`, and `amdgpu_vm_pt_map_tables()`.

## Control flow, state, and persistence behavior

Page table creation sizes the BO for the requested level, chooses VRAM or GTT, applies contiguous/CPU-access flags, shares the root reservation object for child tables, and stores XCP placement. Allocation temporarily drops `vm->eviction_lock`, creates a table, links it to the parent BO, initializes VM tracking, and clears it. Clearing validates the BO, maps it through the active update backend, chooses level-specific invalid/default flags, writes zero or PDE-as-PTE entries, and commits.

`amdgpu_vm_ptes_update()` walks the address range from root to leaves. It allocates missing tables for locked updates, constrains huge mappings by ASIC capabilities and fragment size, writes either leaf PTEs or higher-level PDE-as-PTE entries, updates flags for no-retry and ASIC-specific encodings, handles NUMA MTYPE override for contiguous APU system mappings, and queues child page tables for freeing when a huge mapping or unmap covers them. The queued tables are moved to `params->tlb_flush_waitlist` and freed only after the VM core has arranged required flush behavior.

## Dependencies and integration points

The file depends on `amdgpu_vm.h`, AMDGPU BO creation, GMC PDE/PTE helpers, TTM validation, DRM device enter/exit, GPU page sizing, tracepoints, and the selected `vm->update_funcs`. It integrates with `amdgpu_vm_update_range()` for mapping/unmapping and with `amdgpu_vm_init()` for root directory creation.

## Risks and test signals

Risks include off-by-one PFN traversal, wrong level shift/mask math, freeing active child tables before TLB invalidation, huge-page fragmentation mistakes, invalid default PTE flags on GMC9/GFX12, and update backend errors being ignored inside `amdgpu_vm_pte_update_flags()` because that helper does not propagate return values. Test with sparse mappings, overlapping clear/replace operations, huge-page aligned and unaligned BOs, GFX8 no-huge-page paths, GFX12 PTE flags, CPU and SDMA update modes, and GPU fault tests after page-table free/reuse.
