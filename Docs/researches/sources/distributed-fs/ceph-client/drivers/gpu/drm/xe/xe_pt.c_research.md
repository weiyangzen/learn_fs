<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pt.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pt.c

## Purpose

`xe_pt.c` implements Xe GPU page-table allocation, population, bind/unbind staging, CPU-side commit/abort, GPU migration updates, TLB invalidation scheduling, SVM/userptr validation, page reclaim list generation, and PTE zapping for eviction and invalidation.

## Important APIs, Types, and Functions

Public APIs are `xe_pt_create()`, `xe_pt_populate_empty()`, `xe_pt_shift()`, `xe_pt_destroy()`, `xe_pt_clear()`, `xe_pt_zap_ptes()`, `xe_pt_zap_ptes_range()`, `xe_pt_update_ops_prepare()`, `xe_pt_update_ops_run()`, `xe_pt_update_ops_fini()`, and `xe_pt_update_ops_abort()`. Internal structures include `struct xe_pt_dir` for directory page tables with child/staging arrays, `struct xe_pt_stage_bind_walk`, `struct xe_pt_stage_unbind_walk`, and `struct xe_pt_update`. Major helper groups cover shared-update staging, huge/64K/compact PTE selection, atomic-access PTE flags, SVM range DMA cursors, nonshared offset detection, PRL generation, dependency gathering, commit preparation, and operation-level bind/unbind/remap/prefetch handling.

## Control Flow and State

Page-table creation allocates metadata plus a pinned mapped 4 KiB page-table BO. Empty population writes scratch PDE/PTEs when the VM has scratch support or zeros otherwise. Bind preparation walks the target range, allocates disconnected subtrees when needed, writes private subtree entries immediately, and records shared page-table updates in `xe_vm_pgtable_update` arrays. It handles null/purged BOs, userptr DMA arrays, VRAM/stolen/SG resources, compact 64K L0 tables, PS64 hints, huge PTEs, device atomic flags, and scratch invalidation needs. Unbind preparation walks only shared tables, computes entries to clear, may kill private subtrees, updates `num_live`, and optionally builds page reclaim entries. Run creates migration/TLB jobs, inserts dependencies/range fences, performs GPU or CPU page-table updates, commits CPU child/staging state at the point of no return, adds fences to VM/BO reservations, updates VMA or SVM tile-present state, and returns the migration fence. Abort unwinds staged CPU state for operations not committed; fini frees staging arrays and deferred BO puts.

## Dependencies and Integration Points

This file integrates BO/TTM resource cursors, DRM GPUVA operations, VM locks/reservations, exec queues, migrate engine, TLB invalidation jobs, GuC page reclaim hardware assist, SVM notifier locks, userptr invalidation, scheduler jobs, range fence trees, GT stats, PAT indices, scratch page tables, trace/debug helpers, and memory placement flags.

## Risks and Test Signals

This is a high-risk state machine. Locking contracts differ for BO-backed VMAs, userptr, SVM ranges, and CPU address mirrors. The point-of-no-return in `xe_pt_update_ops_run()` kills the VM on some late failures for non-root tiles. `num_live`, child/staging pointers, range fences, and tile_present/tile_invalidated bits must remain consistent across prepare/run/fini/abort. Huge/64K/compact decisions depend on VA and DMA alignment; VRAM with `XE_VM_FLAG_64K` fails if 64K hints cannot be formed. Tests should cover bind/unbind/remap/prefetch for BO, userptr, null, purged, scratch and non-scratch VMs; SVM range retry paths; compact and normal 64K PTEs; huge PTE alignment; PRL overflow/abort; TLB invalidation creation for primary/media GT; dependency failures for CPU updates; injected prepare/run errors; and abort/fini leak checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pt.c -->
