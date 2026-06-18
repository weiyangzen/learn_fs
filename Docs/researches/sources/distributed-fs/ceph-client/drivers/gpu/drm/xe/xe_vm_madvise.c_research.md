# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_vm_madvise.c

## Purpose

`xe_vm_madvise.c` implements the `DRM_IOCTL_XE_MADVISE` path for changing memory attributes on VMAs in a VM address range. It supports preferred location, atomic access policy, PAT index, and per-VMA purgeable state. It also splits or creates helper VMAs for the advised range, validates resource and coherency constraints, updates VMA/BO attributes, and invalidates affected GPU mappings.

## Important APIs, Types, and Functions

The exported entry point is `xe_vm_madvise_ioctl()`. Internal state is gathered in `struct xe_vmas_in_madvise_range`, which stores the target address/range, a dynamically grown VMA array, and bo/SVM-userptr presence flags. `struct xe_madvise_details` carries a reference-counted `drm_pagemap`, purge tracking, and a userspace retained pointer. Attribute handlers are selected through `madvise_funcs[]`: `madvise_preferred_mem_loc()`, `madvise_atomic()`, `madvise_pat_index()`, and `madvise_purgeable()`.

Validation helpers include `madvise_args_are_sane()`, `xe_madvise_details_init()`, `check_pat_args_are_sane()`, and `check_bo_args_are_sane()`. Invalidation is handled by `xe_zap_ptes_in_madvise_range()` and `xe_vm_invalidate_madvise_range()`, using `xe_pt_zap_ptes()` for ordinary VMAs and `xe_svm_ranges_zap_ptes_in_range()` for CPU address mirror ranges.

## Control Flow and State

The ioctl looks up the VM, validates uAPI fields and retained-pointer preconditions, flushes pending SVM unmaps, takes `vm->lock` in write mode, rejects closed or banned VMs, initializes details, and calls `xe_vm_alloc_madvise_vma()` so the target range is represented by separate VMAs before mutation. `get_vmas()` walks the GPUVA range and records all target VMAs.

For PAT advice, the path validates PAT bounds, coherency mode, L2 flush optimized restrictions, imported BO restrictions, and CPU cached memory restrictions. For BO VMAs it locks all BO reservation objects under `drm_exec` before updating BO-visible state. For SVM/userptr VMAs it takes the SVM notifier lock. After the selected handler updates attributes and `skip_invalidation`, the code zaps PTEs for VMAs that need invalidation, submits a TLB invalidation over the advised range and affected tiles, then unlocks and optionally writes the purgeable retained result to userspace after releasing locks.

Preferred-location advice updates only CPU-address-mirror VMAs; repeated equivalent advice sets `skip_invalidation`. Atomic advice updates VMA and BO atomic policies, and for VRAM BOs switching to CPU/global atomics unmaps CPU virtual mappings so later access can migrate appropriately. PAT advice changes `vma->attr.pat_index`. Purgeable advice applies only to BO-backed VMAs and transitions VMA/BO WILLNEED holder counts between WILLNEED and DONTNEED; already purged BOs remain purged.

## Dependencies and Integration Points

This file integrates with `xe_vm.c` for VMA splitting, default attributes, TLB invalidation, and CPU-address-mirror behavior; `xe_svm.c` for SVM range zapping and pagemap lookup; `xe_bo.c` for purgeable and atomic BO state; `xe_pat.c` for PAT coherency; TTM for CPU mapping invalidation; and DRM pagemap for cross-device preferred locations.

## Risks and Edge Cases

The retained pointer protocol is security-sensitive: userspace must initialize retained to zero, and the driver writes it only after locks are released. PAT coherency rules prevent CPU cached system memory or unknown imported dma-bufs from using non-coherent modes. Preferred location rejects foreign pagemaps without peer connectivity. Purgeable transitions must keep BO holder counts balanced and must not zap mappings at DONTNEED time because pages are still valid until shrinker purge. CPU-address-mirror ranges with active SVM mappings can be busy unless the operation explicitly permits SVM unmap behavior.

## Test Signals

Tests should cover each madvise type, invalid type and reserved fields, unaligned or zero ranges, VMA splitting at range boundaries, PAT coherency failures on iGPU/userptr/imported BOs, L2 flush optimized PAT restrictions, preferred-location dpagemap fd failures and foreign-device rejection, BO atomic placement constraints, purgeable WILLNEED/DONTNEED transitions and retained output, already-purged BO behavior, skip-invalidation cases, and SVM/userptr notifier lock interactions.
