# subset-b-003781 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_migrate.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_migrate.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_migrate.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_migrate.h

## Purpose

`xe_migrate.h` exposes the migration subsystem API to BO movement, VM binding, page-table update, SR-IOV CCS, and GPU memory access callers. It intentionally hides `struct xe_migrate` internals while defining the callback contract used by page-table code to populate or clear PTE values in CPU or GPU command-buffer memory.

## Important APIs, Types, and Functions

- `enum xe_migrate_copy_dir`: selects VRAM-to-system or system-to-VRAM direction for pagemap-address copy helpers.
- `struct xe_migrate_pt_update_ops`: callback table with `populate`, `clear`, and optional `pre_commit`.
- `struct xe_migrate_pt_update`: embeddable update context carrying callback ops, VMA ops, generated scheduler/TLB jobs, tile id, and invalidation jobs.
- Public lifecycle and accessors: `xe_migrate_alloc()`, `xe_migrate_init()`, `xe_migrate_lrc()`, `xe_migrate_exec_queue()`, and `xe_migrate_get_vm()`.
- Data movement APIs: `xe_migrate_copy()`, `xe_migrate_resolve()`, `xe_migrate_vram_copy_chunk()`, `xe_migrate_to_vram()`, `xe_migrate_from_vram()`, `xe_migrate_clear()`, and `xe_migrate_access_memory()`.
- Synchronization APIs: `xe_migrate_wait()`, `xe_migrate_job_lock()`, `xe_migrate_job_unlock()`, and lockdep-only `xe_migrate_job_lock_assert()`.

## Control Flow

Consumers allocate/init a per-tile migration context, then call copy/clear/update helpers with BO resources or page-table update descriptors. For page-table updates, the caller supplies callbacks that know how to encode PTE content; migration chooses CPU or GPU execution and invokes those callbacks against either an `iosys_map` or command-buffer position. Returned `dma_fence` objects are the caller-visible completion signal.

## State and Persistence Behavior

The header establishes that migration operations are asynchronous unless a helper explicitly waits. The `xe_migrate_pt_update` object is caller-owned but receives transient job pointers while pre-commit hooks run. Clear flags persist through BO contents and CCS state rather than through header-managed state.

## Dependencies and Integration Points

It forward declares core Xe, TTM, DRM pagemap, sync, and scheduler types to keep compile dependencies small. The API is used by BO resource moves, VM bind code, page-fault rebinds, SR-IOV VF CCS handling, and tests.

## Risks and Edge Cases

- Callback contracts rely on consistent qword counts and offsets; the compiler cannot enforce that `populate` and `clear` write the exact number of qwords requested.
- Callers must handle returned `ERR_PTR` fences and partial-copy synchronization semantics from the implementation.
- Lock helper behavior differs for migration queues versus user queues, so callers must pass the correct queue object.

## Test Signals

Build coverage should catch signature drift. Runtime tests should exercise all public movement directions, clear flag combinations, CPU/GPU page-table update paths, and lockdep assertions for migration versus user queues.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_migrate.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_migrate_doc.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_migrate_doc.h

## Purpose

`xe_migrate_doc.h` is documentation-only kernel-doc for the Xe migrate layer. It explains why the driver creates a special per-GT migration VM and how generated jobs use that VM for copy, clear, and page-table bind work.

## Important APIs, Types, and Functions

The file exports no C symbols. Its `DOC: Migrate Layer` block documents the migration VM layout, bind job structure, copy/clear job structure, limits from reserved page-table pages, and future work items.

## Control Flow

The documented flow is two-stage for both bind and copy/clear jobs: first update the migration VM page structure to point at target BOs or page-table BOs, then execute the actual PTE programming, copy, or clear after a ring-side TLB invalidation boundary. Large BO operations are split into multiple jobs.

## State and Persistence Behavior

The documentation states that the migration VM has reserved physical pages for BO mappings, a kernel bind page, user bind pages managed by `drm_suballoc`, and identity-mapped VRAM. User bind suballocations return to the pool after job completion; kernel bind pages are serially reused.

## Dependencies and Integration Points

This file is consumed by generated kernel documentation and complements `xe_migrate.c`/`xe_migrate.h`. It also explains constraints visible to VM bind, BO eviction, and clear/copy callers.

## Risks and Edge Cases

The document contains TODO/future-work notes around diagrams, using identity-mapped VRAM for copy/clear, better async bind page utilization, large pages for sysmem, and possible sysmem identity mapping. These are signs that implementation details may evolve and documentation should be kept synchronized.

## Test Signals

Documentation validation is mostly build-doc coverage. Functional tests should compare documented max copy/clear sizes and two-batch/TLB invalidation expectations against migration implementation behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_migrate_doc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_mmio.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_mmio.c

## Purpose

`xe_mmio.c` maps the GPU GTTMMADR BAR, partitions MMIO register windows by tile, and provides traced typed register read/write/wait helpers for the rest of the Xe driver. It also handles SR-IOV VF register access redirection and PF-side VF MMIO view initialization.

## Important APIs, Types, and Functions

- Probe/lifecycle: `xe_mmio_probe_early()`, `xe_mmio_probe_tiles()`, `mmio_fini()`, and `tiles_fini()`.
- Initialization: `xe_mmio_init()` and multi-tile helper `mmio_multi_tile_setup()`.
- Accessors: `xe_mmio_read8()`, `xe_mmio_write8()`, `xe_mmio_read16()`, `xe_mmio_write32()`, `xe_mmio_read32()`, `xe_mmio_rmw32()`, and `xe_mmio_write32_and_verify()`.
- Utility: `xe_mmio_in_range()`, `xe_mmio_read64_2x32()`, `xe_mmio_wait32()`, and `xe_mmio_wait32_not()`.
- SR-IOV PF helper under `CONFIG_PCI_IOV`: `xe_mmio_init_vf_view()`.

## Control Flow

Early probe maps the entire GTTMMADR BAR and initializes root tile registers to the first 4 MiB. Later tile probing assigns remote tile MMIO windows at 16 MiB strides. Register access first applies `xe_mmio_adjusted_addr()`, optionally flushes pending writes for a device workaround before reads, routes non-VF registers through SR-IOV VF mediated access when running as a VF, performs raw IO access otherwise, and emits `trace_xe_reg_rw` events.

The wait helpers poll masked register values until match or mismatch, using exponential backoff with either `udelay()` or `usleep_range()` depending on atomic context. The 64-bit read helper reads upper/lower/upper 32-bit values to reduce rollover races.

## State and Persistence Behavior

`xe->mmio.regs` owns the mapped BAR pointer until devm teardown. Each `struct xe_mmio` stores a tile backpointer, register-window pointer/size, optional adjustment fields, and optional SR-IOV VF GT override. Remote tile `regs` pointers are cleared on cleanup, while the root mapping is iounmapped.

## Dependencies and Integration Points

Nearly all hardware programming code uses these helpers, including IRQ, PAT, MOCS, OA, GSC, VRAM discovery, hwmon, and workarounds. The file depends on PCI BAR resources, Linux IO accessors, DRM managed cleanup, Xe tracing, SR-IOV VF helper functions, and generated workaround predicates.

## Risks and Edge Cases

- Register address adjustment must not split 64-bit register pairs; `xe_mmio_read64_2x32()` asserts this.
- `xe_mmio_in_range()` treats ranges as inclusive after address adjustment.
- VF redirection applies only when `reg.vf` is false; register definitions must mark VF-safe direct registers correctly.
- Poll timeouts are minimum waits and may exceed the requested time in sleeping context.
- BAR partitioning assumes a 16 MiB tile stride and 4 MiB register window.

## Test Signals

Probe tests should validate BAR map failure handling and multi-tile pointer setup. Unit or fault-injection tests should cover address adjustment, wait timeout/success paths, 64-bit rollover stabilization, SR-IOV VF routing, and trace-visible register access ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_mmio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_mmio.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_mmio.h

## Purpose

`xe_mmio.h` declares the Xe MMIO mapping and register accessor interface and provides the inline address-adjustment helper shared by low-level register users.

## Important APIs, Types, and Functions

The header exposes probe functions, `xe_mmio_init()`, typed accessors, read-modify-write, write-and-verify, range checking, 64-bit split reads, wait-until-match/not-match helpers, and `xe_mmio_init_vf_view()` when PCI IOV is enabled. `xe_mmio_adjusted_addr()` applies `adj_offset` to addresses below `adj_limit`.

## Control Flow

Callers initialize a `struct xe_mmio` with a tile, pointer, and size, then pass `struct xe_reg` descriptors to accessors. Address adjustment happens inline before the implementation touches hardware.

## State and Persistence Behavior

The header does not own state, but its inline helper defines how persistent `adj_limit`/`adj_offset` fields in `struct xe_mmio` affect all users.

## Dependencies and Integration Points

It includes `xe_mmio_types.h` and forward declares `xe_device`/`xe_reg`. It is included by most Xe hardware programming modules.

## Risks and Edge Cases

Consumers must pass valid `struct xe_reg` offsets for the target region. Incorrect adjustment fields can silently redirect every access below the limit.

## Test Signals

Build coverage catches API drift. Focused tests should validate adjusted and non-adjusted addresses, including boundary `addr == adj_limit`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_mmio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_mmio_gem.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_mmio_gem.c

## Purpose

`xe_mmio_gem.c` wraps a page-aligned physical MMIO region in a private DRM GEM object so authorized userspace can mmap a selected register window through a DRM fake offset. It exists for narrow cases where exposing hardware registers is intentional.

## Important APIs, Types, and Functions

- `struct xe_mmio_gem`: private GEM object containing `drm_gem_object base` and starting `phys_addr`.
- Public API: `xe_mmio_gem_create()`, `xe_mmio_gem_mmap_offset()`, and `xe_mmio_gem_destroy()`.
- GEM callbacks: `xe_mmio_gem_free()`, `xe_mmio_gem_mmap()`, and `xe_mmio_gem_vm_fault()`.
- Hot-unplug fallback: `xe_mmio_gem_vm_fault_dummy_page()` maps a zero dummy page when `drm_dev_enter()` fails.

## Control Flow

Creation validates page alignment, initializes a private GEM object, creates a fake mmap offset, and allows only the creating `drm_file` to use the VMA node. mmap validates exact size and shared mapping, forces noncached IO PFNMAP flags, and defers PFN insertion to the fault handler. Fault handling maps each page of the physical MMIO range, or maps a zero dummy page over the whole VMA after unplug/removal.

## State and Persistence Behavior

The object stores only `phys_addr` and GEM base metadata. VMA-node permissions persist until object destruction. Dummy pages are registered with DRM managed cleanup on the device.

## Dependencies and Integration Points

It depends on DRM GEM private objects, DRM VMA offset management, `drm_dev_enter()` for hot-unplug safety, Linux VM PFN insertion, and Xe device typing. Callers must decide which MMIO regions are safe to expose.

## Risks and Edge Cases

- This is security-sensitive: exposing the wrong register page can compromise stability or isolation.
- `xe_mmio_gem_destroy()` directly frees the GEM object; callers must ensure no remaining references require normal GEM refcount release behavior.
- mmap requires exact object size and shared mapping, while comments describe userspace passing matching length.
- Fault handler maps the entire VMA on each fault, which is simple but could repeat work.

## Test Signals

Tests should cover alignment rejection, fake offset creation, VMA permission enforcement, exact-length mmap, PFN insertion, dummy-page behavior on simulated unplug, and denial of unauthorized file access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_mmio_gem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_mmio_gem.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_mmio_gem.h

## Purpose

`xe_mmio_gem.h` declares the small MMIO-to-GEM wrapper API used by Xe code that needs to hand a safe MMIO mmap offset to userspace.

## Important APIs, Types, and Functions

It forward declares `struct xe_mmio_gem` and exposes `xe_mmio_gem_create()`, `xe_mmio_gem_mmap_offset()`, and `xe_mmio_gem_destroy()`.

## Control Flow

Callers create an object for a page-aligned physical range, retrieve the fake mmap offset, communicate it through a driver-specific interface, and destroy the object when the exposure is no longer needed.

## State and Persistence Behavior

State lives in the opaque implementation object. The header makes ownership explicit enough that callers are responsible for balancing create/destroy.

## Dependencies and Integration Points

It depends only on Linux types and forward declarations for DRM file and Xe device types.

## Risks and Edge Cases

The header does not encode the security policy for which registers may be exposed; all policy remains with callers.

## Test Signals

Compile tests should catch API drift. Integration tests should verify callers balance create/destroy and do not leak mmap offsets after teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_mmio_gem.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_mmio_types.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_mmio_types.h

## Purpose

`xe_mmio_types.h` defines the persistent data structures used by Xe MMIO register access code: an MMIO region descriptor and a simple register-range descriptor.

## Important APIs, Types, and Functions

- `struct xe_mmio`: tile backpointer, mapped `regs` pointer, optional SR-IOV VF GT backpointer, register-region size, and address-adjustment fields.
- `struct xe_mmio_range`: inclusive `[start, end]` register range used by validation and filtering code.

## Control Flow

The structures are initialized by `xe_mmio_init()` or specialized SR-IOV helpers and then passed into `xe_mmio_*` accessors. Range tables are walked by helpers such as OA config validation.

## State and Persistence Behavior

`struct xe_mmio` persists for device/tile/GT lifetime and may share the same underlying ioremap with other regions. Its adjustment fields persistently affect all future accesses through that instance.

## Dependencies and Integration Points

The types are embedded in tile and GT objects and are used across IRQ, query, OA, MOCS, PAT, GSC, VRAM, hwmon, and workaround code.

## Risks and Edge Cases

Incorrect `regs_size`, `adj_limit`, or `adj_offset` values are global hazards for all register users of a region. `sriov_vf_gt` is only meaningful for GT MMIO while running as an SR-IOV VF.

## Test Signals

Structural compile coverage plus runtime assertions around size limits, address adjustment, and SR-IOV VF-specific access paths are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_mmio_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_mocs.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_mocs.c

## Purpose

`xe_mocs.c` defines and programs platform-specific MOCS/L3 cacheability tables for Xe GTs. It selects uncached/writeback indices used elsewhere, writes global MOCS and LNCF/L3CC registers, and supports debug dumping of programmed table state.

## Important APIs, Types, and Functions

- Data model: `struct xe_mocs_entry`, `struct xe_mocs_info`, and `struct xe_mocs_ops`.
- Platform tables: Gen12, DG1, DG2, PVC, Meteor Lake, Xe2, and Xe3P/Crescent Island variants.
- Selection and lookup: `get_mocs_settings()`, `get_entry_control()`, `get_entry_l3cc()`, and `l3cc_combine()`.
- Programming: `xe_mocs_init_early()`, `xe_mocs_init()`, `__init_mocs_table()`, and `init_l3cc_table()`.
- Diagnostics: `xe_mocs_dump()` with per-platform dump callbacks.

## Control Flow

Early GT init calls `xe_mocs_init_early()` to populate `gt->mocs.uc_index` and `gt->mocs.wb_index`. Full init skips SR-IOV VFs, selects the platform table, decides whether global MOCS and/or LNCF MOCS registers are present, and writes each register either through MCR multicast or direct MMIO depending on platform/GT type. Dumping takes runtime PM and forcewake, then reads and prints the relevant registers.

## State and Persistence Behavior

The programmed register state persists in hardware until reset/reprogramming. The selected UC/WB indices persist in `gt->mocs` for command emitters such as migration copy/clear and OA programming. Undefined table entries are filled from `unused_entries_index` to keep hardware registers deterministic.

## Dependencies and Integration Points

MOCS depends on platform info, GT type, MCR register access, MMIO helpers, forcewake/runtime PM, SR-IOV mode checks, and register definitions. MOCS indices are consumed by batch emitters and other memory-transaction programming paths.

## Risks and Edge Cases

- MOCS tables are hardware ABI; changing existing entries can break userspace assumptions.
- Missing `unused_entries_index` is asserted because index 0 is not a safe default on most platforms.
- DG2 leaves the last entry out of validation because hardware treats it as read-only.
- SR-IOV VFs skip programming, so PF/firmware must provide usable state.
- Dumping requires forcewake domain selection to match table type.

## Test Signals

KUnit coverage via `tests/xe_mocs.c`, platform table selection tests, register write/readback dumps, forcewake timeout tests, and validation that `gt->mocs.uc_index`/`wb_index` match expected platform values are useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_mocs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_mocs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_mocs.h

## Purpose

`xe_mocs.h` declares the public MOCS initialization and dump interface for GT setup and diagnostics.

## Important APIs, Types, and Functions

It exposes `xe_mocs_init_early()`, `xe_mocs_init()`, and `xe_mocs_dump()`.

## Control Flow

GT setup first calls the early function to populate cacheability indices, then the full init function to program hardware registers before GuC initialization. Debugfs or diagnostic paths can call the dump function with a `drm_printer`.

## State and Persistence Behavior

State changes occur in `gt->mocs` and hardware registers through the implementation.

## Dependencies and Integration Points

The header forward declares `drm_printer` and `xe_gt` and is used by GT initialization and diagnostics.

## Risks and Edge Cases

Call order matters: MOCS programming should happen before GuC work that depends on memory transaction attributes.

## Test Signals

Compile coverage and GT init sequencing tests should catch misuse.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_mocs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_module.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_module.c

## Purpose

`xe_module.c` is the Linux module entry point for the Xe driver. It defines module parameters, runs module-wide initialization functions in order, unwinds on failure, and performs reverse-order cleanup on module unload.

## Important APIs, Types, and Functions

- Global `struct xe_modparam xe_modparam` with defaults for display probing, GuC log level, firmware paths, force-probe, VRAM BAR size, wedged policy, SVM notifier size, and SR-IOV max VFs.
- Module parameters declared with `module_param_named*` and `MODULE_PARM_DESC`.
- `xe_check_nomodeset()` rejects loading when firmware-only drivers are requested.
- `struct init_funcs` plus `init_funcs[]` sequences configfs, hw fence, sched job, PCI driver, observation sysctl, and PM init.
- `xe_init()` and `xe_exit()` are registered with `module_init`/`module_exit`.

## Control Flow

Module load iterates `init_funcs[]` in order. On the first error it logs the failing init function pointer and unwinds only functions whose init already ran. Module unload iterates the table in reverse and calls any exit function. Some entries, like `xe_pm_module_init`, have no exit callback.

## State and Persistence Behavior

`xe_modparam` stores process-wide module configuration. Init functions register global subsystems such as PCI driver binding, sysctl entries, configfs, and scheduler/fence infrastructure. Unload removes only entries with explicit exits.

## Dependencies and Integration Points

This file ties together DRM module support, Xe PCI probing, PM, scheduler jobs, hw fences, configfs, and observation sysctl registration. It includes module metadata for author, description, and license.

## Risks and Edge Cases

- Init ordering is important; PCI registration occurs after shared infrastructure and before observation sysctl/PM in this table.
- Unsafe module parameters can alter firmware paths and force-probe behavior early in driver load.
- Failure unwind only calls exits for prior entries, so entries with side effects but no exit must be safe on later failure or be intentionally one-way.

## Test Signals

Module load/unload testing, parameter parsing tests, forced init failure injection, `nomodeset`/firmware-only behavior, and repeated bind/unbind cycles are useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_module.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_module.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_module.h

## Purpose

`xe_module.h` defines the module parameter structure shared by the Xe driver and declares the global instance populated from module parameters.

## Important APIs, Types, and Functions

- `struct xe_modparam`: fields for execlist forcing, display probing, VRAM BAR sizing, GuC logging, firmware override paths, force-probe, SR-IOV VF limit, wedged mode, and SVM notifier size.
- `extern struct xe_modparam xe_modparam`.

## Control Flow

Other Xe modules read `xe_modparam` during probe and subsystem initialization to choose feature policy and firmware behavior.

## State and Persistence Behavior

`xe_modparam` is process-wide module state and remains stable after module parameter parsing, except for writable parameters exposed with write permissions.

## Dependencies and Integration Points

The header is included by PCI probing, configfs, firmware loading, and other policy-sensitive code.

## Risks and Edge Cases

The structure is a broad shared configuration object; adding fields or changing semantics affects many subsystems. Conditional `max_vfs` changes layout under `CONFIG_PCI_IOV`.

## Test Signals

Build matrix coverage with and without PCI IOV, plus module parameter parse/probe tests, should catch most regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_module.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_nvm.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_nvm.c

## Purpose

`xe_nvm.c` exposes discrete GPU internal NVM regions to the generic Intel DG NVM auxiliary driver when the platform supports GSC NVM access. It builds an auxiliary device with resource windows and platform-specific writable/erase behavior flags.

## Important APIs, Types, and Functions

- Static region table names descriptor, GSC, padding, OptionROM, and DAM regions.
- `xe_nvm_init()` allocates and registers `struct intel_dg_nvm_dev`.
- `xe_nvm_fini()` deletes/uninitializes the auxiliary device on managed teardown.
- `xe_nvm_release_dev()` frees the allocated NVM object.
- Platform policy helpers: `xe_nvm_writable_override()` and `xe_nvm_non_posted_erase()`.

## Control Flow

Initialization exits early when no GSC NVM exists or the device is an SR-IOV VF. It validates `xe->nvm` is empty, allocates the auxiliary device data, reads platform registers to determine write override and non-posted erase behavior, creates BAR resource descriptors for GUNIT and DEBUG NVM windows relative to PCI BAR0, initializes/adds the auxiliary device, stores `xe->nvm`, and registers devm cleanup.

## State and Persistence Behavior

`xe->nvm` points to the auxiliary NVM device while registered. Resource descriptors and region metadata persist in that object. The auxiliary device release callback owns final memory freeing.

## Dependencies and Integration Points

It integrates with `intel_dg_nvm_aux`, PCI resources, GSC/HECI register definitions, PCODE scratch registers, root tile MMIO, SR-IOV mode checks, and DRM logging.

## Risks and Edge Cases

- Unknown platforms in writable override log an error and return `true`, effectively treating access as overridden.
- VFs never expose internal NVM.
- Resource offsets are hard-coded Gen12-era constants and must stay valid for supported platforms.
- Auxiliary device add failure must uninit but not double-free because release semantics differ before/after init.

## Test Signals

Tests should cover no-NVM and VF early exits, each platform policy register path, auxiliary init/add failure injection, resource address calculations, and managed cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_nvm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_nvm.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_nvm.h

## Purpose

`xe_nvm.h` declares the Xe NVM auxiliary-device initialization entry point.

## Important APIs, Types, and Functions

It forward declares `struct xe_device` and exposes `int xe_nvm_init(struct xe_device *xe)`.

## Control Flow

Device probe calls `xe_nvm_init()` after enough platform/MMIO state exists to determine NVM availability and policy.

## State and Persistence Behavior

All persistent state is stored in `xe->nvm` by the implementation.

## Dependencies and Integration Points

The header is consumed by device probe code that conditionally creates the NVM auxiliary device.

## Risks and Edge Cases

Callers must not assume NVM exists after a successful `0` return because unsupported devices and VFs also return success with no device registered.

## Test Signals

Probe tests should assert both registered and intentionally absent NVM outcomes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_nvm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_oa.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_oa.c

## Purpose

`xe_oa.c` implements Xe Observability Architecture performance counter streams. It initializes OA units and formats, manages dynamic metric configurations, opens anon stream file descriptors, programs OA/OAR/OAC/OAM hardware through MMIO and command batches, reads OA circular buffers, and exposes config/status/info operations through stream ioctls.

## Important APIs, Types, and Functions

- Internal config/state: `struct xe_oa_config`, `struct xe_oa_open_param`, `struct xe_oa_config_bo`, `struct xe_oa_fence`, and static `oa_formats[]`.
- Public entry points: `xe_oa_init()`, `xe_oa_register()`, `xe_oa_stream_open_ioctl()`, `xe_oa_add_config_ioctl()`, `xe_oa_remove_config_ioctl()`, `xe_oa_timestamp_frequency()`, and `xe_oa_unit_id()`.
- Stream file operations: `xe_oa_read()`, `xe_oa_poll()`, `xe_oa_ioctl()`, `xe_oa_mmap()`, and `xe_oa_release()`.
- Stream lifecycle: `xe_oa_stream_init()`, `xe_oa_stream_open_ioctl_locked()`, `xe_oa_stream_enable()`, `xe_oa_stream_disable()`, `xe_oa_stream_destroy()`, and `xe_oa_destroy_locked()`.
- Hardware programming: `xe_oa_enable_metric_set()`, `xe_oa_disable_metric_set()`, `xe_oa_enable()`, `xe_oa_disable()`, `xe_oa_configure_oa_context()`, `xe_oa_emit_oa_config()`, and `xe_oa_submit_bb()`.
- Config validation: `decode_oa_format()`, `xe_oa_user_extensions()`, `xe_oa_alloc_regs()`, and address validators for flex, B-counter, and mux registers.

## Control Flow

Device initialization enables OA only for GuC submission, non-VF devices, and Gen12+ platforms. It initializes per-GT OA units, assigns engines to OA units, selects supported formats, and later registers a `metrics` sysfs directory. Userspace opens a stream through the observation ioctl by passing extension properties. The open path validates privileges, OA unit, format, exec queue, sampling mode, buffer size, syncs, and exclusivity, then allocates a stream, OA buffer, kernel exec queue, forcewake/runtime PM refs, and initial metric config.

When enabled, the stream initializes OA buffer registers, programs OA control/debug/context registers, emits metric register loads via MI LRI batches, optionally disables preemption/timeslicing for a target exec queue, and starts an hrtimer for sampling streams. Reads poll/check the hardware tail, avoid partially landed reports by checking report id/timestamp, copy reports to userspace, clear consumed report headers, and advance OAHEADPTR. Config ioctls can switch metric sets by emitting a new config batch and using a delayed software fence to signal when NOA programming is active.

## State and Persistence Behavior

`struct xe_oa` persists on the device and owns supported format bits, the dynamic metrics IDR, `metrics_kobj`, and monotonically assigned OA unit ids. Each GT owns OA units protected by `gt_lock`; each OA unit permits one `exclusive_stream`. Each stream owns PM/forcewake refs, OA buffer BO, cached head/tail pointers, poll timer, sync entries, active config ref, cached config BOs, last fence, optional exec queue ref, and anon FD lifetime. Dynamic configs persist in `metrics_idr` and sysfs until removed or device teardown.

## Dependencies and Integration Points

OA integrates with the top-level observation ioctl, Xe query OA-unit reporting, DRM syncobj/sync entries, anon inodes, scheduler jobs, GGTT-pinned BOs, forcewake/runtime PM, MMIO/MCR registers, GuC RC/workarounds, hardware engine topology, and sysfs metrics. It relies on UAPI format encodings in `xe_drm.h`.

## Risks and Edge Cases

- OA is privilege-sensitive; sampling and config changes are gated by `xe_observation_paranoid`/`perfmon_capable`, while query-only OAR/OAC can be less privileged.
- Tail processing assumes OA writes land in order; partial report handling is defensive but hardware-order dependent.
- OA unit access is exclusive; teardown must clear `exclusive_stream` under GT lock and restore preemption/timeslice settings.
- Config register validation must stay current with platform MMIO allowlists.
- `xe_oa_emit_oa_config()` has point-of-no-return behavior after creating a software fence and cleaning syncs.
- Buffer mmap is read-only/private and maps system-memory pages directly; permission flag mistakes could expose writable counter buffers.

## Test Signals

Signals include OA query enumeration, stream open/close with privilege matrix, invalid extension/property fuzzing, dynamic config add/remove/sysfs id tests, OA buffer read/poll/mmap behavior, overrun/status reporting, config switch sync signaling, forced job/allocation failures, engine/OA-unit assignment tests, and platform format/address allowlist validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_oa.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_oa.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_oa.h

## Purpose

`xe_oa.h` declares the public OA subsystem interface used by device init, query code, and observation ioctls.

## Important APIs, Types, and Functions

It exposes initialization/registration, stream open, add/remove config ioctls, timestamp frequency lookup, and engine-to-OA-unit id lookup. It includes `xe_oa_types.h` for shared data structures.

## Control Flow

Device probe calls `xe_oa_init()` and later `xe_oa_register()`. Observation ioctl dispatch calls stream/config functions. Query paths call `xe_oa_timestamp_frequency()` and `xe_oa_unit_id()`.

## State and Persistence Behavior

State is stored in device and GT OA structures defined in `xe_oa_types.h`; this header only declares access.

## Dependencies and Integration Points

It forward declares DRM and Xe types and is included by observation, query, and initialization code.

## Risks and Edge Cases

Callers must handle `-ENODEV` from OA ioctls when OA is unsupported or disabled by platform/SR-IOV conditions.

## Test Signals

Compile coverage plus query/observation integration tests catch API and lifecycle regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_oa.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_oa_types.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_oa_types.h

## Purpose

`xe_oa_types.h` defines the shared OA data structures embedded in Xe device, GT, unit, stream, and buffer state, plus the internal OA format enumeration.

## Important APIs, Types, and Functions

- `enum xe_oa_format_name` and `struct xe_oa_format` describe supported report encodings, report sizes, UAPI types, header width, counter size, and BC report fields.
- `struct xe_oa_regs` groups the OA register set for one unit.
- `struct xe_oa_unit` represents one hardware OA unit with type, GT, regs, engine count, id, and exclusive stream.
- `struct xe_oa_gt` stores per-GT OA lock and unit array.
- `struct xe_oa` stores device-level OA state, metrics sysfs/IDR, format table/mask, and id allocator.
- `struct xe_oa_buffer` stores the OA BO, vaddr, head/tail/circular size, format, and pointer lock.
- `struct xe_oa_stream` stores all per-FD state for OA stream operation.

## Control Flow

Implementation code initializes `xe_oa`, then each `xe_oa_gt` and `xe_oa_unit`. Stream open allocates and fills `xe_oa_stream`, while read/poll/ioctl paths mutate stream and buffer fields under their locks.

## State and Persistence Behavior

The structures define persistent lifetime boundaries: device OA state for device lifetime, GT OA units for GT lifetime, dynamic stream state for anon FD lifetime, and OA buffer state while a stream is active.

## Dependencies and Integration Points

The header depends on Linux IDR/mutex/bitops, UAPI OA definitions, register descriptors, hardware engine types, and DRM syncobj forward declarations.

## Risks and Edge Cases

- `exclusive_stream` must be protected by GT locking and cleared reliably.
- `oa_buffer.circ_size` may differ from BO size on Xe2+ overrun mode, so users must not assume full BO size is consumable reports.
- `wait_num_reports` and report size affect poll readiness and buffer sizing.
- Stream fields combine PM, forcewake, fences, syncs, and queues, making teardown ordering important.

## Test Signals

Structure-size/build coverage, stream lifecycle tests, lockdep on `gt_lock`/`stream_lock`/`ptr_lock`, and query tests for OA unit ids are useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_oa_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_observation.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_observation.c

## Purpose

`xe_observation.c` is the top-level observation ioctl dispatcher for Xe performance/diagnostic streams and owns the `dev/xe/observation_paranoid` sysctl controlling non-root access.

## Important APIs, Types, and Functions

- Global `u32 xe_observation_paranoid = true`.
- `xe_observation_ioctl()` dispatches by observation type.
- Internal dispatchers route OA operations to `xe_oa_*` and EU stall stream open to `xe_eu_stall_stream_open()`.
- `xe_observation_sysctl_register()` and `xe_observation_sysctl_unregister()` manage the sysctl table.

## Control Flow

The DRM ioctl receives `drm_xe_observation_param`, rejects top-level extensions, selects OA or EU stall by `observation_type`, then dispatches supported operations. OA supports stream open, add config, and remove config; EU stall currently supports stream open only.

## State and Persistence Behavior

The paranoid sysctl persists globally while the module is loaded. Its value is consulted by OA stream/config and OA mmap permission checks.

## Dependencies and Integration Points

It connects UAPI observation types to OA and EU stall backends and is registered/unregistered from module init/exit.

## Risks and Edge Cases

- Unsupported extensions or operation/type combinations return `-EINVAL`.
- Sysctl registration currently returns 0 unconditionally; a failed `register_sysctl()` would leave `sysctl_header` NULL for unregister.
- Relaxing `observation_paranoid` broadens access to sensitive performance data.

## Test Signals

Ioctl dispatch tests should cover all valid and invalid type/op combinations, extension rejection, sysctl registration/unregistration, and permission behavior when toggling `observation_paranoid`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_observation.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_observation.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_observation.h

## Purpose

`xe_observation.h` declares the observation ioctl/sysctl entry points and the global paranoid access-control flag.

## Important APIs, Types, and Functions

It exposes `xe_observation_paranoid`, `xe_observation_ioctl()`, `xe_observation_sysctl_register()`, and `xe_observation_sysctl_unregister()`.

## Control Flow

DRM ioctl tables call `xe_observation_ioctl()`, while module init/exit call sysctl register/unregister.

## State and Persistence Behavior

The exported paranoid flag is global module state and can be read by observation backends.

## Dependencies and Integration Points

It forward declares DRM device/file types and is used by module code plus OA/EU stall backends.

## Risks and Edge Cases

External users must treat `xe_observation_paranoid` as policy state and avoid unsynchronized assumptions about sysctl changes.

## Test Signals

Build and ioctl permission tests provide coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_observation.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_page_reclaim.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_page_reclaim.c

## Purpose

`xe_page_reclaim.c` implements helper logic for GuC page reclaim lists, which extend TLB invalidation with page-reclaim/PPC flush work for VM unbind or invalidation flows.

## Important APIs, Types, and Functions

- `xe_page_reclaim_skip()` decides whether a VMA needs page reclaim based on null VMA and PAT L3 policy.
- `xe_page_reclaim_create_prl_bo()` suballocates a GGTT reclaim-pool BO, copies PRL entries, flushes CPU writes, and schedules BO release on a TLB invalidation fence.
- `xe_page_reclaim_list_invalidate()`, `xe_page_reclaim_list_init()`, and `xe_page_reclaim_list_alloc_entries()` manage CPU-side PRL entry storage.
- `xe_guc_page_reclaim_done_handler()` delegates completion messages to the TLB invalidation done handler.

## Control Flow

Callers initialize or allocate a PRL, populate entries elsewhere, skip unnecessary VMAs, then create a reclaim BO when submitting the GuC request. The BO contains entries plus a terminating null entry and is freed when the paired invalidation fence signals. Completion handling follows the same seqno/fence logic as TLB invalidation.

## State and Persistence Behavior

CPU PRL entries live in one allocated page with refcount helpers. A PRL can be invalidated by setting entries to NULL and `num_entries` to `XE_PAGE_RECLAIM_INVALID_LIST`. Reclaim BO suballocations persist only until the associated fence completes.

## Dependencies and Integration Points

The file depends on PAT policy lookup, tile reclaim pools, Xe SA BO helpers, GuC TLB invalidation fence/message code, and GT stats/logging via the header abort macro.

## Risks and Edge Cases

- PRL size is capped at one 4 KiB page and 512 entries; overpopulation must be prevented by callers.
- Atomic allocation is used for reclaim BO creation, so reclaim-pool pressure can fail late.
- `xe_page_reclaim_skip()` assumes transient display policy is safely flushed by hardware sequencing.
- Invalidation drops the backing page ref; callers must not use entries after invalidating.

## Test Signals

Tests should cover skip policy for null/transient-display/other PAT VMAs, PRL allocation/invalidation refcounts, reclaim BO contents including terminator, fence-based suballoc freeing, and malformed GuC completion handling through the delegated TLB path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_page_reclaim.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_page_reclaim.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_page_reclaim.h

## Purpose

`xe_page_reclaim.h` defines GuC page reclaim entry/list formats and declares helper APIs for page reclaim list lifecycle, submission backing storage, skip policy, and completion handling.

## Important APIs, Types, and Functions

- `struct xe_guc_page_reclaim_entry`: packed 64-bit GuC entry with valid bit, reclaim size order, and split physical address fields.
- `struct xe_page_reclaim_list`: CPU-side entries pointer and count, with invalid sentinel `XE_PAGE_RECLAIM_INVALID_LIST`.
- Inline helpers: `xe_page_reclaim_list_is_new()`, `xe_page_reclaim_list_valid()`, `xe_page_reclaim_entries_get()`, and `xe_page_reclaim_entries_put()`.
- Abort macro: `xe_page_reclaim_list_abort()` invalidates, increments a GT stat, and logs a debug reason.
- Declared functions for skip, BO creation, invalidation, init, allocation, and GuC done handling.

## Control Flow

Callers allocate/init a PRL, use inline validity checks while building reclaim requests, optionally abort with diagnostics, create a GuC-visible BO for submission, and release references when complete.

## State and Persistence Behavior

The header defines the PRL state machine: new is `{NULL, 0}`, valid is allocated/non-invalid, invalid uses a sentinel count. Entry storage lifetime is controlled by page refcounts.

## Dependencies and Integration Points

It depends on Linux bits/mm/slab/workqueue types and Xe GT/TLB/GUC/VMA forward declarations. Page-table and TLB invalidation code consume the format.

## Risks and Edge Cases

Because entries are packed bitfields in a raw `u64`, encoding mistakes can produce GuC-invisible or malformed reclaim requests. The abort macro evaluates `gt`/`prl` once but still assumes valid pointers.

## Test Signals

Bitfield encoding tests, validity-state tests, refcount tests, and abort-stat/log behavior should be covered.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_page_reclaim.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pagefault.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pagefault.c

## Purpose

`xe_pagefault.c` implements the consumer side of Xe device page fault handling. Producers parse hardware/firmware fault messages into `struct xe_pagefault`; this file queues those records, services them by resolving VM/VMA mappings, and calls producer acknowledgements with success or error.

## Important APIs, Types, and Functions

- Public API: `xe_pagefault_init()`, `xe_pagefault_reset()`, and `xe_pagefault_handler()`.
- Queue management: `xe_pagefault_queue_init()`, `xe_pagefault_queue_pop()`, `xe_pagefault_queue_work()`, `xe_pagefault_queue_reset()`, and `xe_pagefault_queue_full()`.
- Service path: `xe_pagefault_service()`, `xe_pagefault_asid_to_vm()`, `xe_pagefault_handle_vma()`, `xe_pagefault_begin()`, and `xe_pagefault_access_is_atomic()`.
- Diagnostics/persistence: `xe_pagefault_print()` and `xe_pagefault_save_to_vm()`.

## Control Flow

Initialization creates a high-priority unbound workqueue when USM is enabled and sizes each page-fault queue from total EU count plus engine count. Producers call `xe_pagefault_handler()` from IRQ or process context; it hashes by ASID, copies the compact fault record into a circular byte queue, and schedules work. The worker pops faults for up to a bounded runtime, skips reset-squashed records, services each fault, records failures into the VM fault list, logs non-prefetch failures, acknowledges through producer ops, and requeues itself if the time budget expires.

Service resolves ASID to a VM only if the VM is in fault mode or has scratch, takes the VM write lock, locates the VMA, checks read-only access, delegates CPU-address mirrors to SVM handling, otherwise validates/migrates the BO and rebinds the VMA on the faulting tile. It waits for the rebind fence before acknowledging success.

## State and Persistence Behavior

The device owns `xe->usm.pf_wq` and `xe->usm.pf_queue[]` while USM is enabled. Queue head/tail/data persist until teardown and are protected by spinlock. VM state can persist successful `last_fault_vma` updates and failure fault entries via `xe_vm_add_fault_entry_pf()`. Reset marks pending faults for a GT by nulling `pf->gt`.

## Dependencies and Integration Points

This layer integrates with USM ASID mappings, VM/VMA locks, BO validation/migration, userptr repinning, SVM mirror faults, TTM/DRM exec locking, validation retry logic, scheduler fences, GT stats, tracepoints, and producer-specific acknowledgement callbacks.

## Risks and Edge Cases

- Queue sizing assumes worst-case EU/engine fault count with an empirical multiplier; overflow returns `-ENOSPC` and warns.
- Worker service waits for fences and may requeue on runtime budget; long fault storms can increase latency.
- VM lookup rejects non-fault-mode VMs except scratch-capable VMs.
- DONTNEED/purged BOs fail faults for non-scratch VMs to avoid repopulating reclaimable pages.
- Atomic faults require VRAM for some VMAs and reject userptr VMAs needing VRAM movement.
- Reset squashing by setting `pf->gt = NULL` must race safely with queued copies.

## Test Signals

Signals include queue sizing/overflow tests, ASID lookup failure, read-only write faults, prefetch failure accounting, purged/DONTNEED BO behavior, userptr repin retry, SVM mirror delegation, VMA rebind success/failure, reset squashing, ack callback invocation, and workqueue time-budget requeue behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pagefault.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pagefault.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pagefault.h

## Purpose

`xe_pagefault.h` declares the consumer page-fault lifecycle API for device initialization, GT reset, and producer fault submission.

## Important APIs, Types, and Functions

It exposes `xe_pagefault_init()`, `xe_pagefault_reset()`, and `xe_pagefault_handler()`.

## Control Flow

Probe initializes queues after fuse/topology data is available. Producers submit parsed faults through `xe_pagefault_handler()`. Reset code calls `xe_pagefault_reset()` to squash queued faults for a resetting GT.

## State and Persistence Behavior

State is stored in `xe_device.usm` fields defined elsewhere and in `xe_pagefault_types.h`.

## Dependencies and Integration Points

It forward declares `xe_device`, `xe_gt`, and `xe_pagefault` for use by fault producers and reset paths.

## Risks and Edge Cases

Callers must not submit faults before initialization on USM devices. Reset callers should invoke the reset function before stale GT work can be acknowledged as live.

## Test Signals

Build coverage and producer integration tests should validate init/handler/reset call sequencing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pagefault.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pagefault_types.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pagefault_types.h

## Purpose

`xe_pagefault_types.h` defines the producer-consumer page fault ABI inside the Xe driver: access/type enums, acknowledgement ops, compact fault record, and queue structure.

## Important APIs, Types, and Functions

- `enum xe_pagefault_access_type`: read, write, and atomic access encodings.
- `enum xe_pagefault_type`: not-present, write access violation, and atomic access violation.
- `struct xe_pagefault_ops`: producer callback `ack_fault()`.
- `struct xe_pagefault`: 64-byte record with GT pointer, consumer fields, producer-private state, producer ops, and original message words.
- `struct xe_pagefault_queue`: byte-oriented circular queue with data pointer, size, head/tail, spinlock, and worker.
- Bit masks: access type mask, prefetch bit, NACK sentinel, fault level/type masks, and producer message length.

## Control Flow

Fault producers fill `struct xe_pagefault`, including producer-private acknowledgement data, then pass it to the consumer queue. The consumer reads only consumer fields plus producer ops for acknowledgement and leaves producer-private payload interpretation to the producer.

## State and Persistence Behavior

Fault records are copied into queues and are transient until worker acknowledgement. Queue state persists for USM lifetime. Producer message words are retained because fault producers may run in allocation-constrained contexts.

## Dependencies and Integration Points

The types are embedded in `xe_device` USM state and included by hardware/firmware fault producers and the consumer implementation.

## Risks and Edge Cases

- The compact layout relies on small integer fields and masks; producers must pack values correctly.
- `XE_PAGEFAULT_TYPE_LEVEL_NACK` lets producers force a negative acknowledgement before service.
- Queue head/tail are byte offsets, and entry size is rounded to a power of two in implementation.

## Test Signals

Tests should validate struct size expectations, mask packing/unpacking, NACK behavior, prefetch flag behavior, queue wraparound, and producer callback invocation with preserved message words.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pagefault_types.h -->
