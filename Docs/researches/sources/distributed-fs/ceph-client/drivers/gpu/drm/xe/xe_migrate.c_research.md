
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_migrate.c

## Purpose

`xe_migrate.c` implements the Xe migration engine support used for buffer moves, clears, VRAM/system-memory copies, flat-CCS metadata handling, GPU page-table updates, and small CPU-buffer accesses performed through GPU blits. It builds and owns a special migration VM per tile, creates the default migration execution queue, and emits MI/BLT/MEM_COPY batch buffers that update temporary mappings before running the actual copy, clear, or page-table write commands.

## Important APIs, Types, and Functions

- `struct xe_migrate`: private per-tile migration context with default queue, migration VM page-table BO, batch base offsets, cleared/null mapping offset, large-page copy mappings, VM update suballocator, minimum VRAM chunk size, and `job_mutex`/last `fence` tracking.
- Initialization: `xe_migrate_alloc()`, `xe_migrate_init()`, `xe_migrate_fini()`, `xe_migrate_prepare_vm()`, `xe_migrate_pt_bo_alloc()`, and `xe_migrate_suballoc_manager_init()`.
- Copy/clear entry points: `xe_migrate_copy()`, `xe_migrate_resolve()`, `xe_migrate_clear()`, `xe_migrate_vram_copy_chunk()`, `xe_migrate_to_vram()`, `xe_migrate_from_vram()`, and `xe_migrate_access_memory()`.
- Page-table update entry point: `xe_migrate_update_pgtables()` with CPU fast path `xe_migrate_update_pgtables_cpu()` and GPU path `__xe_migrate_update_pgtables()`.
- Batch emit helpers include `emit_pte()`, `pte_update_size()`, `write_pgtable()`, `emit_copy()`, `emit_mem_copy()`, `emit_xy_fast_copy()`, `emit_clear()`, `emit_copy_ccs()`, and `emit_flush_invalidate()`.
- CCS/SR-IOV helpers: `xe_migrate_ccs_rw_copy()` and `xe_migrate_ccs_rw_copy_clear()` prepare/clear special CCS read/write batch buffers for VF contexts.
- Synchronization helpers: `xe_migrate_wait()`, `xe_migrate_job_lock()`, `xe_migrate_job_unlock()`, and `xe_migrate_job_lock_assert()`.

## Control Flow

Initialization creates a migration VM with `XE_VM_FLAG_MIGRATION`, allocates a pinned page-table BO, installs a self-referential layout, maps the kernel batch-buffer pool, reserves scratch page-table slots, creates a null clear mapping, and identity maps VRAM on dGPU at a high VM offset. It then creates a permanent kernel copy queue, selecting the USM-reserved copy engine where USM fault servicing requires it.

Copy and clear paths run in chunked passes. Each pass computes the largest safe transfer size, chooses identity mappings for contiguous VRAM where possible, emits temporary PTE updates for fragmented or system memory, inserts a `MI_BATCH_BUFFER_END` boundary, then emits the actual copy or clear command after the mapping preamble. Jobs are created with migration flush/TLB invalidation flags, dependency fences are attached on the first pass, and the returned fence represents the final pass.

Page-table updates first try the CPU path, unless KUnit forces GPU or callback `pre_commit()`/conditions require GPU execution. The GPU path builds a batch that maps target PT BOs into the migration VM on integrated devices, writes PTEs with `MI_STORE_DATA_IMM`, optionally suballocates async update space, arms the job, and frees the suballocation on the job fence.

## State and Persistence Behavior

The migration VM layout and `pt_bo` persist for the tile lifetime. `m->fence` stores the last migration job fence and is protected by `job_mutex`; `xe_migrate_wait()` drains it before teardown or tile shutdown. `vm_update_sa` persists as a pool for user bind page-table update mappings. Copy/clear temporary PTEs are overwritten in the migration VM rather than allocated per operation. BO state can be persisted by setting `bo->ccs_cleared`, by installed page-table updates, and by generated SR-IOV CCS batch buffers stored in `src_bo->bb_ccs[]`.

## Dependencies and Integration Points

This file is central to TTM BO movement (`xe_bo.c`), VM bind/rebind (`xe_pt`/`xe_vm`), USM page-fault service, SR-IOV VF CCS flows, GGTT/batch-buffer pools, PAT/MOCS selection, scheduler jobs, TLB invalidation, and DMA mapping. It depends on Xe page-table ops for PTE/PDE encoding, `xe_res_cursor` for fragmented resources, DRM suballocators for shared update pages, dma-fence/dma-resv for synchronization, and hardware command definitions under `instructions/`.

## Risks and Edge Cases

- Chunk sizing is constrained by preemption-disable time, CCS metadata alignment, VRAM block fragmentation, `MAX_PTE_PER_SDI`, and copy-command field limits; mistakes can produce invalid batches or large latency spikes.
- Identity VRAM mappings assume correct DPA base, actual physical size, and flat-CCS offset accounting on Xe2+.
- Copying CCS between distinct BOs is explicitly rejected; future support must preserve metadata ownership and security-clearing semantics.
- Error paths wait for partial copy fences but comments note some waits are not under `job_mutex`.
- `xe_migrate_access_memory()` uses bounce-buffer recursion for unaligned legacy copy paths and DMA maps caller memory page-by-page; bad length/offset handling risks overrun or stale DMA mappings.
- Page-table GPU updates require external synchronization for overlapping updates on non-migration queues.

## Test Signals

Useful signals include KUnit live migrate tests, BO move/eviction tests across sysmem/VRAM, flat-CCS clear/copy/resolve validation, fault-mode rebinds under USM load, SR-IOV VF CCS batch generation/clear tests, lockdep coverage around `job_mutex` and VM locks, and fault injection for BO allocation, batch allocation, suballocation, and scheduler job creation failures.
