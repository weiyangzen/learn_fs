# Research: subset-b-003606

Grouped source research for subset B work item `subset-b-003606`. Each delimited section preserves the source path and can be split into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_pages.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_pages.c

## Purpose
This file is the central GEM object page-management implementation for i915. It attaches and detaches scatter-gather page tables to `drm_i915_gem_object`, pins object backing storage, manages kernel mappings, invalidates cached TLB state, supports panic-time framebuffer access, and provides fast page/DMA address lookup helpers.

## Important APIs, Types, and Functions
Key entry points are `__i915_gem_object_set_pages`, `____i915_gem_object_get_pages`, `__i915_gem_object_get_pages`, `i915_gem_object_pin_pages_unlocked`, `i915_gem_object_truncate`, `__i915_gem_object_unset_pages`, `__i915_gem_object_put_pages`, `i915_gem_object_pin_map`, `i915_gem_object_pin_map_unlocked`, `__i915_gem_object_flush_map`, `__i915_gem_object_release_map`, `__i915_gem_object_page_iter_get_sg`, `__i915_gem_object_get_page`, `__i915_gem_object_get_dirty_page`, and the DMA address helpers. `struct intel_panic` and the `i915_gem_object_panic_*` functions bridge GEM objects to `drm_panic` scanout writes.

## Control Flow
Page acquisition routes through object ops: the public pin path locks the object, calls the backend `get_pages` if no pages exist, then increments `pages_pin_count`. Setting pages initializes SG iterators, page-size masks, shrinker state, cache dirty handling, and swizzle quirks. Releasing pages refuses pinned objects, drops mmap offsets, removes the object from shrink lists, unmaps cached virtual mappings, clears lookup radix trees, invalidates per-GT TLB generation records, and calls the backend `put_pages`.

Kernel mapping flow first pins pages, selects WB/WC based on object placement and DGFX rules, waits for moving fences, and maps either struct pages via `vmap` or IOMEM PFNs via `vmap_pfn`. Reusing a mapping with a different cache type is allowed only when the caller did not enter through a preexisting pin.

## State and Persistence Behavior
The file mutates `obj->mm.pages`, `mm.mapping`, `mm.page_sizes`, page iterators, `pages_pin_count`, shrink list links, `shrink_pin`, `madv`, `dirty`, `cache_dirty`, and per-GT `mm.tlb[]`. Volatile objects temporarily become `DONTNEED` while pages are set and return to `WILLNEED` on unset. Cached kernel mappings persist until explicit release or page teardown.

## Dependencies and Integration Points
It depends on GEM object ops implemented by shmem, userptr, stolen, phys, and TTM backends; `i915_scatterlist` iterators; shrinker helpers; GTT mmap release; local-memory placement; GT TLB invalidation; display framebuffer tiling callbacks; and DRM panic scanout buffer APIs.

## Risks
Incorrect pin accounting can release active backing storage. Cache-type mismatch or missing clflush can corrupt CPU/GPU data sharing. Page-size mask errors affect GTT insertion. Radix iterator updates are concurrent and must preserve lookup correctness. Panic paths run under constrained allocation and mapping rules. IOMEM mappings require WC/PAT availability and correct physical offset calculations.

## Test Signals
Useful signals include GEM shmem/stolen/TTM selftests, pin/unpin stress, mmap and kernel-map cache mode tests, suspend/resume with TLB invalidation, dirty page read/write tests, DGFX local-memory mapping tests, panic framebuffer rendering, and shrinker pressure while objects are pinned or mapped.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_pages.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_phys.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_phys.c

## Purpose
This file converts eligible shmem GEM objects to physically contiguous coherent allocations and implements pread/pwrite for those physically backed objects. It supports older or special paths that require a single contiguous DMA allocation rather than normal shmem scatter-gather pages.

## Important APIs, Types, and Functions
The internal backend functions are `i915_gem_object_get_pages_phys`, `i915_gem_object_put_pages_phys`, and `i915_gem_object_shmem_to_phys`. Public helpers used by shmem and callers are `i915_gem_object_pwrite_phys`, `i915_gem_object_pread_phys`, and `i915_gem_object_attach_phys`.

## Control Flow
`i915_gem_object_attach_phys` requires a locked shmem object, rejects too-large alignment, non-shmem objects, purged objects, tiling quirks, existing mappings, and pinned pages, then unbinds active GPU use before conversion. Conversion unsets old pages, allocates a coherent DMA block rounded to a power-of-two object size, builds a one-entry SG table, copies each shmem page into the coherent allocation with cache flushes, sets the GEM pages, perma-pins them, releases the original shmem pages, and removes the object from its memory-region list.

Read and write helpers wait for GPU completion, directly copy between userspace and the coherent allocation, flush CPU cache ranges, and for writes invalidate/flush frontbuffer state.

## State and Persistence Behavior
The object changes from struct-page backed shmem to a fake single-SG physical allocation by clearing `I915_BO_FLAG_STRUCT_PAGE`. Physical pages remain permanently pinned until object release. Dirty physical data is copied back to the shmem file in `put_pages_phys` if `obj->mm.dirty` is set, then the coherent allocation is freed.

## Dependencies and Integration Points
The code integrates with shmem release helpers, frontbuffer invalidation, GT chipset flushes, tiling swizzle checks, GEM unbind/wait paths, DMA coherent allocation, shmem pagecache reads, and selftests included under `CONFIG_DRM_I915_SELFTEST`.

## Risks
The contiguous allocation can fail for large objects, and the code intentionally rejects bit17-swizzled objects. The apparent use of the SG pointer before assignment in the overflow check is fragile and depends on compiler/static-analysis behavior. Dirty copyback errors are skipped page-by-page, so data loss can occur if shmem pages cannot be reacquired. Permanent pinning reduces reclaimability.

## Test Signals
Exercise `i915_gem_object_attach_phys` selftests, pwrite/pread round trips, conversion rejection for tiled or pinned objects, GPU wait behavior before CPU access, dirty copyback after release, and memory pressure around large coherent allocations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_phys.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_pm.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_pm.c

## Purpose
This file coordinates GEM object state across suspend, hibernation freeze, and resume. Its main responsibility is preserving local-memory contents using TTM backup/restore and making CPU/GPU cache-domain state safe for platform power transitions.

## Important APIs, Types, and Functions
Public lifecycle hooks are `i915_gem_suspend`, `i915_gem_backup_suspend`, `i915_gem_suspend_late`, `i915_gem_freeze`, `i915_gem_freeze_late`, and `i915_gem_resume`. Local helpers `lmem_suspend`, `lmem_restore`, and `lmem_recover` iterate local memory regions and call the TTM PM APIs.

## Control Flow
Suspend first disables the userfault auto wakeref, waits for pending RCU callbacks, flushes driver workqueues, asks each GT to prepare suspend, and drains freed GEM objects. Backup suspend then performs staged LMEM handling: evict unpinned objects with GPU allowed, suspend GTs, evict/backup newly unpinned and pinned non-early objects, and finally memcpy-backup remaining pinned objects after migrate contexts are no longer used. Any failure frees partial backups.

Late suspend walks shrink and purge lists under `obj_lock`, marks objects as CPU-written for hibernation, and flushes CPU caches with `wbinvd_on_all_cpus` if non-coherent CPU-visible data may exist. Resume restores early backups, resumes GTs, then restores GPU-assisted backups; GT resume failures wedge affected GTs.

## State and Persistence Behavior
The file does not own object data itself but changes persistence guarantees for LMEM objects through `obj->ttm.backup`, TTM placement, shrink/purge list domain state, runtime PM userfault wakerefs, and GT suspend/resume state. Hibernation paths force objects toward CPU domain so the image contains coherent backing data.

## Dependencies and Integration Points
It depends on `i915_gem_ttm_pm` for LMEM backup/restore, GT PM and request retirement, runtime PM wakeref helpers, shrinker reclaim, freed-object draining, and architecture cache flush support.

## Risks
Incorrect staging can lose LMEM contents, especially pinned objects and CCS aux state. Missing global cache flushes can write stale data into hibernation images. Resume ordering matters because the kernel context image is disposable but user object contents are not. On non-x86, the fallback only warns for missing `wbinvd`.

## Test Signals
Suspend/resume and hibernate cycles on integrated and DGFX platforms, LMEM object checksum validation before/after power transitions, wedged-GT resume fault injection, framebuffer preservation, early-PM object tests, and shrink-list domain assertions are important signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_pm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_pm.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_pm.h

## Purpose
This header declares the GEM power-management entry points used by the wider i915 driver during suspend, hibernation, idle work, and resume.

## Important APIs, Types, and Functions
It forward-declares `struct drm_i915_private` and `struct work_struct`, then exposes `i915_gem_resume`, `i915_gem_idle_work_handler`, `i915_gem_suspend`, `i915_gem_suspend_late`, `i915_gem_backup_suspend`, `i915_gem_freeze`, and `i915_gem_freeze_late`.

## Control Flow
There is no executable flow in the header. It allows driver PM code to call the staged GEM PM implementation in `i915_gem_pm.c`, with early suspend, late suspend, freeze, freeze-late, backup suspend, and resume split into explicit phases.

## State and Persistence Behavior
The header stores no state. The declared functions affect runtime PM wakerefs, GT state, object cache domains, shrink-list processing, and TTM LMEM backup objects in the implementation.

## Dependencies and Integration Points
It is included by driver suspend/resume paths and by GEM modules that need PM declarations. The `i915_gem_idle_work_handler` declaration is part of the broader GEM idle-work integration even though its implementation is elsewhere.

## Risks
The main risk is phase misuse: callers must invoke the right function at the right PM stage or local-memory preservation and cache coherency assumptions can fail. Header declarations must stay synchronized with implementation signatures.

## Test Signals
Build coverage catches signature drift. Runtime PM, system suspend, hibernation, and module unload paths validate that each declared hook remains wired into the platform lifecycle.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_pm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_region.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_region.c

## Purpose
This file provides generic GEM object creation and iteration for `intel_memory_region` backends. It is the common entry point for shmem, TTM system, local memory, and stolen-region object allocation.

## Important APIs, Types, and Functions
Public functions are `i915_gem_object_init_memory_region`, `i915_gem_object_release_memory_region`, `i915_gem_object_create_region`, `i915_gem_object_create_region_at`, and `i915_gem_process_region`. The internal creator `__i915_gem_object_create_region` validates size, page size, flags, and delegates object initialization to `mem->ops->init_object`.

## Control Flow
Creation validates allocation flags, rejects incompatible GPU-only flags, rounds size to the selected page size, forces contiguous allocation for single-page-size objects, checks global GEM size limits, allocates a GEM object, adds PM-early for page sizes below the region minimum, and calls the memory-region object initializer. Fixed-offset creation additionally validates offset/size alignment, region bounds, mappable IO coverage, and aperture availability before forcing contiguous allocation.

`i915_gem_process_region` iterates a region's object list under `mr->objects.lock`, temporarily moves entries to a side list, takes a safe object reference, drops the region lock, acquires the GEM object ww lock, verifies the object still belongs to the region, invokes caller ops, then restores unprocessed entries.

## State and Persistence Behavior
Objects are linked to `mem->objects.list` through `obj->mm.region_link` and record their current region in `obj->mm.region`. Iteration temporarily reorders the list but restores entries at the end. Creation traces `i915_gem_object_create`.

## Dependencies and Integration Points
This file is used by shmem, stolen, TTM system, LMEM, and TTM PM backup/restore code. It depends on memory-region ops, GEM object allocation/free, ww locking, object refcounts, GTT aperture checks, and tracepoints.

## Risks
Concurrent region iteration can skip objects because entries are temporarily removed. Region membership is unstable until the object lock is acquired, so callers must respect the post-lock `obj->mm.region == mr` check. Misaligned fixed offsets or wrong page-size assumptions can create objects that cannot be inserted into the GTT or migrated safely.

## Test Signals
Tests should cover region creation flags, fixed-offset allocation rejection, region object-list membership on create/release, concurrent `i915_gem_process_region` users, PM backup iteration, and migration that changes `obj->mm.region` during iteration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_region.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_region.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_region.h

## Purpose
This header defines the public interface for GEM objects backed by `intel_memory_region` instances and for region-wide object processing.

## Important APIs, Types, and Functions
It defines `I915_BO_INVALID_OFFSET`, `struct i915_gem_apply_to_region_ops` with `process_obj`, and `struct i915_gem_apply_to_region` containing ops, a ww context pointer, and an interruptible flag. It declares memory-region attach/release, region object creation, fixed-offset creation, and `i915_gem_process_region`.

## Control Flow
The header has no executable logic. It documents that `process_obj` may be rerun for the same object after `-EDEADLK` when part of a ww transaction.

## State and Persistence Behavior
The structures are transient control objects used by region iterators. The implementation mutates object region membership, but the header itself stores no persistent state.

## Dependencies and Integration Points
Consumers include shmem and TTM object creation paths, stolen object setup, local-memory region code, and TTM PM backup/restore. The header forward-declares GEM object, memory region, and SG-table types to keep dependencies light.

## Risks
Callers embedding `i915_gem_apply_to_region` must treat `apply->ww` as owned by the iterator today; passing a preexisting ww context is warned against in the implementation. Incorrect assumptions about one-pass processing can break under deadlock backoff.

## Test Signals
Build coverage for all region users, ww-deadlock fault injection, and PM backup/restore iteration are the main signals for this interface.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_region.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_shmem.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_shmem.c

## Purpose
This file implements the system-memory shmem GEM backend. It allocates page-cache backed objects, builds SG tables from shmem folios, handles shrink/writeback/truncate behavior, supports pre-page-instantiation pwrite, configures cache coherency, and creates the system memory region.

## Important APIs, Types, and Functions
Important helpers are `shmem_sg_alloc_table`, `shmem_sg_free_table`, `__shmem_writeback`, `__i915_gem_object_release_shmem`, `i915_gem_object_put_pages_shmem`, `i915_gem_object_create_shmem`, `i915_gem_object_create_shmem_from_data`, `i915_gem_shmem_setup`, and `i915_gem_object_is_shmem`. Backend ops are in `i915_gem_shmem_ops`.

## Control Flow
Page acquisition creates an SG table sized by object pages, marks the mapping unevictable, allocates folios using constrained no-reclaim GFP, invokes i915 shrinker retries on failure, merges contiguous PFNs up to the DMA segment limit, trims the SG table, prepares pages for GTT DMA, falls back from large segments to PAGE_SIZE on DMA remap failure, applies bit17 swizzle, sets cache-dirty when LLC can be bypassed, and installs pages.

Release flushes or marks dirty as needed, finishes GTT mappings, saves swizzle metadata, releases folios through a batch that updates LRU/dirty/accessed state, clears dirty, and frees the SG table. `shmem_pwrite` writes directly into the shmem file only before pages are instantiated; normal pread is rejected for struct-page shmem and delegated only for phys-converted objects.

## State and Persistence Behavior
State lives in the object's shmem file, pagecache mapping, `obj->mm.madv`, dirty/cache flags, swizzle bitmap, cache coherency, domain fields, and memory-region membership. `shmem_truncate` drops all backing pages immediately and marks the object purged. `init_shmem` may create a DRM hugepage mount and names the region `system`.

## Dependencies and Integration Points
It integrates with Linux shmem/folio/writeback APIs, DRM GEM private object setup, GTT DMA mapping helpers, i915 shrinker, tiling swizzle logic, phys conversion, memory-region creation, THP mount helpers, and platform cache/LLC policy.

## Risks
Allocation is sensitive to reclaim recursion, dirty shmem behavior, and DMA segment limits. Unevictable mapping state must be cleared on every error path. Direct write short-write handling returns `-EIO`. Cache coherency differs across LLC, DGFX, and MTL one-way coherency. `shmem_truncate` leaves `mm.pages` as an error pointer, so later paths must treat purged state carefully.

## Test Signals
Signals include shmem object creation with/without THP, pwrite before and after page instantiation, shrinker/writeback/truncate behavior under memory pressure, bit17 swizzle save/restore, DMA remap fallback, cache-domain tests on LLC and non-LLC platforms, and `create_shmem_from_data` content checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_shmem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_shrinker.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_shrinker.c

## Purpose
This file implements i915 GEM memory reclaim. It registers kernel shrinker, OOM, and vmap purge callbacks; frees purgeable or swappable object pages; and manages object visibility on shrink and purge lists.

## Important APIs, Types, and Functions
Main APIs are `i915_gem_shrink`, `i915_gem_shrink_all`, `i915_gem_driver_register__shrinker`, `i915_gem_driver_unregister__shrinker`, `i915_gem_shrinker_taints_mutex`, `i915_gem_object_make_unshrinkable`, `__i915_gem_object_make_shrinkable`, `__i915_gem_object_make_purgeable`, `i915_gem_object_make_shrinkable`, and `i915_gem_object_make_purgeable`. Internal callbacks include shrinker count/scan, OOM, and vmap purge handlers.

## Control Flow
`i915_gem_shrink` chooses purge-list first, then shrink-list depending on flags. It may acquire a runtime PM wakeref for bound objects, retire active requests when active shrinking is requested, then loops one object at a time under `obj_lock`, moves it to a temporary list, filters by vmap/framebuffer/releasability, takes a ref, locks the object, unbinds according to bound/active flags, puts pages, and asks backend shrink/writeback ops to finalize. Entries are spliced back afterward.

The kernel shrinker count reports `shrink_memory` and dynamically adjusts batch size. The scan path does a normal pass, then kswapd may force active/writeback reclaim. OOM and vmap notifiers perform aggressive passes and report freed pages.

## State and Persistence Behavior
The file owns list membership and accounting in `i915->mm.shrink_list`, `purge_list`, `shrink_count`, and `shrink_memory`, protected by `obj_lock`. Object `mm.shrink_pin` prevents reclaim while pinned or intentionally hidden. MADV state decides shrink vs purge placement.

## Dependencies and Integration Points
It depends on GEM object locking/refcounts, unbind paths, backend `shrink` ops, runtime PM, GT request retirement, Linux shrinker/OOM/vmap notifier APIs, swap availability, and lockdep fs-reclaim annotations.

## Risks
Reclaim can run inside allocation paths, so deadlock avoidance is critical. Objects can be freed while lists are walked, requiring refcount checks. The CHV/VTD workaround uses trylock VM unbinds. Framebuffers are skipped unless active shrinking is explicit. `i915_gem_shrink` returns an unsigned long but can return `err`, so callers must tolerate encoded negative values only where expected.

## Test Signals
Memory-pressure tests, OOM notifier tests, vmap exhaustion tests, pinned-object skip tests, purgeable MADV behavior, active GPU reclaim, kswapd writeback behavior, and lockdep under fs reclaim provide useful coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_shrinker.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_shrinker.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_shrinker.h

## Purpose
This header exposes the GEM shrinker interface and shrink-selection flags for the rest of i915.

## Important APIs, Types, and Functions
It declares `i915_gem_shrink`, `i915_gem_shrink_all`, shrinker register/unregister helpers, and `i915_gem_shrinker_taints_mutex`. Flags are `I915_SHRINK_UNBOUND`, `I915_SHRINK_BOUND`, `I915_SHRINK_ACTIVE`, `I915_SHRINK_VMAPS`, and `I915_SHRINK_WRITEBACK`.

## Control Flow
The header has no executable control flow. The flags define how callers select unbound objects, bound objects requiring runtime PM, active objects requiring request retirement/waits, vmapped objects, and writeback behavior.

## State and Persistence Behavior
No state is stored here. Implementations use the declarations to mutate object shrink-list state, page backing, and kernel shrinker registration.

## Dependencies and Integration Points
This header is included by allocation paths, shmem retry logic, PM freeze, and other GEM code that needs explicit reclaim. It forward-declares `drm_i915_private`, `i915_gem_ww_ctx`, and `mutex`.

## Risks
Flag combinations are semantically important: asking for bound or active reclaim can wake hardware or wait on GPU work, while writeback changes shmem/TTM persistence behavior. Callers in reclaim context must avoid flags that can deadlock.

## Test Signals
Compile coverage plus targeted shrink calls using each flag combination, especially shmem allocation retry and freeze-late paths, validate this interface.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_shrinker.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_stolen.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_stolen.c

## Purpose
This file manages BIOS/GPU-reserved stolen memory as i915 memory regions and GEM objects. It discovers valid stolen ranges, excludes hardware-reserved WOPCM/GSCPSMI areas, allocates objects from a `drm_mm` allocator, wraps stolen allocations in SG tables, and exposes a display-facing stolen-memory interface.

## Important APIs, Types, and Functions
Key public setup and query functions are `i915_gem_stolen_smem_setup`, `i915_gem_stolen_lmem_setup`, `i915_gem_object_create_stolen`, `i915_gem_object_is_stolen`, and `i915_display_stolen_interface`. Internal helpers handle node insertion/removal, stolen validation, platform reserved range decoding (`g4x_get_stolen_reserved`, `gen6_get_stolen_reserved`, `vlv_get_stolen_reserved`, `gen7_get_stolen_reserved`, `chv_get_stolen_reserved`, `bdw_get_stolen_reserved`, `icl_get_stolen_reserved`), memory-region init/release, and stolen object ops.

## Control Flow
Initialization rejects vGPU, older VT-d cases, invalid ranges, and conflicting system memory reservations. It adjusts old platforms where GTT lives inside stolen memory, records the full DSM, discovers reserved top-of-stolen areas, shrinks usable region, initializes `i915->mm.stolen`, and may disable userspace access on MTL A0. LMEM stolen setup derives DSM size/base from LMEMBAR, MCR tile range, DSMBASE, or MTL GGC, then creates an IO mapping when direct or BAR access is possible.

Object creation allocates or reserves a `drm_mm_node`, initializes a private GEM object with contiguous stolen ops, pins its pages immediately, and releases nodes on failure. Page get creates a one-entry SG table with DMA address `dsm.stolen.start + offset`; release removes the node and memory-region membership.

## State and Persistence Behavior
Persistent driver state includes `i915->dsm.stolen`, `dsm.reserved`, `dsm.usable_size`, `i915->mm.stolen`, `stolen_lock`, memory-region `private` flags, optional region `iomap`, and per-object `obj->stolen`. Stolen contents persist outside normal system memory and are often reused for BIOS/display allocations.

## Dependencies and Integration Points
It integrates with PCI BAR/resource discovery, uncore register reads, GT MCR, `drm_mm`, stolen display-parent interface, GGTT error-capture poisoning in debug builds, memory-region creation, local-memory region logic, and many platform feature macros.

## Risks
Platform register decoding is fragile and safety-critical; reusing reserved WOPCM/GSCPSMI space can hang hardware. System stolen reservation conflicts point to BIOS/kernel resource bugs. CPU accessibility differs between system stolen, local stolen, small-BAR, and direct DSM modes. Immediate pinning and contiguous allocation limit flexibility. Debug poisoning must avoid stop_machine inversion.

## Test Signals
Boot logs for stolen size/usable size, BIOS framebuffer handoff, display stolen allocations, stolen object create/pin/release tests, MTL GGC decoding, small-BAR DGFX behavior, vGPU/VT-d disable paths, and debug GEM poisoning are relevant signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_stolen.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_stolen.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_stolen.h

## Purpose
This header declares stolen-memory region setup, stolen GEM object creation, stolen-object identification, and the display stolen-memory interface.

## Important APIs, Types, and Functions
Exports are `i915_gem_stolen_smem_setup`, `i915_gem_stolen_lmem_setup`, `i915_gem_object_create_stolen`, `i915_gem_object_is_stolen`, `I915_GEM_STOLEN_BIAS`, and `i915_display_stolen_interface`.

## Control Flow
There is no executable flow. `I915_GEM_STOLEN_BIAS` reserves the first 128 KiB bias used by allocator helpers to avoid problematic low stolen addresses.

## State and Persistence Behavior
The header stores no state; implementations maintain DSM resources, `drm_mm` allocator state, and per-object stolen nodes.

## Dependencies and Integration Points
It forward-declares i915 private and GEM object types and references `struct intel_memory_region` and `struct intel_display_stolen_interface` through declarations. Display code uses the exported interface to allocate stolen memory without directly depending on GEM internals.

## Risks
The bias constant and setup entry points are part of platform allocation policy; changing them can affect BIOS framebuffer reuse and hardware workarounds.

## Test Signals
Build coverage, stolen-region setup at probe, display stolen allocation paths, and object identification tests validate the header contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_stolen.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_throttle.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_throttle.c

## Purpose
This file implements the legacy `DRM_IOCTL_I915_GEM_THROTTLE` behavior. It limits CPU submission lead by waiting for this file's old outstanding requests, roughly preventing userspace from getting more than one frame ahead of the GPU.

## Important APIs, Types, and Functions
The sole exported ioctl handler is `i915_gem_throttle_ioctl`. `DRM_I915_THROTTLE_JIFFIES` is a 20 ms threshold used to choose requests old enough to wait on.

## Control Flow
The ioctl first returns terminal wedge status for ABI compatibility. It walks all contexts in the file private context xarray under RCU, takes a context ref, locks the context engine set, and for each engine timeline scans requests in reverse order. It skips completed requests and requests emitted more recently than the threshold, takes a reference to the first old incomplete request, drops the timeline mutex, waits interruptibly forever for that request, then continues unless interrupted.

## State and Persistence Behavior
No persistent state is stored. The function temporarily references contexts and requests and observes per-timeline request lists. It can cause scheduling latency by blocking the caller until selected requests complete.

## Dependencies and Integration Points
It depends on DRM file private state, GEM contexts and engine iteration, request timelines, terminal wedge reporting, jiffies timekeeping, and `i915_request_wait`.

## Risks
Timeline scanning assumes request list ordering and correct `emitted_jiffies`. The wait is unbounded except for signals. RCU is dropped and reacquired around context processing, so context lifetime must be protected by refs. This is legacy latency policy, not a precise frame pacing mechanism.

## Test Signals
Throttle ioctl ABI tests, wedged-device return tests, multi-context/multi-engine request submission, signal interruption, and frame-latency workloads show whether behavior remains compatible.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_throttle.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_tiling.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_tiling.c

## Purpose
This file implements legacy GEM tiling and swizzle ABI support for X/Y tiled objects and fence-register requirements. Modern tiling layouts are intentionally left to userspace, but old fence and bit17 swizzle behavior still requires kernel tracking.

## Important APIs, Types, and Functions
Public helpers are `i915_gem_fence_size`, `i915_gem_fence_alignment`, `i915_gem_object_needs_bit17_swizzle`, `i915_gem_object_set_tiling`, `i915_gem_set_tiling_ioctl`, and `i915_gem_get_tiling_ioctl`. Internal helpers validate tiling/stride and unbind GGTT VMAs whose current placement cannot satisfy new fence constraints.

## Control Flow
Fence size/alignment depends on graphics generation: gen4+ aligns to fence pages and rounds by tile height, while older generations require power-of-two fence regions. `i915_gem_object_set_tiling` rejects framebuffers, locks the object, unbinds incompatible GGTT VMAs, handles swizzled-page pinning quirks by moving objects between shrinkable and unshrinkable states, updates VMA fence size/alignment and dirty fence flags, writes `tiling_and_stride`, allocates or frees bit17 metadata, unlocks, and releases GTT mmap state.

The set ioctl validates handle/proxy/tiling constraints, reports swizzle ABI values with bit17 hidden, falls back to untiled on unknown swizzle, applies the tiling change, then returns the actual stored tiling/stride. The get ioctl uses an RCU handle lookup to read tiling and returns logical and physical swizzle modes.

## State and Persistence Behavior
Persistent object state includes `tiling_and_stride`, per-VMA fence constraints, dirty fence flags, `bit_17` swizzle bitmap, tiling-quirk flags, shrink-list membership, and released GTT mmap offsets.

## Dependencies and Integration Points
It integrates with GGTT VMA lists, fence registers, GEM mmap, shrinker pinning, display framebuffer checks, platform swizzle fields in GGTT, and UAPI structs in `i915_drm.h`.

## Risks
Tiling changes can corrupt active scanout, so framebuffer objects are rejected twice. Swizzle ABI compatibility hides bit17 from old userspace. Unknown swizzling disables tiling. VMA unbind error recovery must restore list membership. Pinning swizzled pages reduces reclaimability.

## Test Signals
Set/get tiling ioctl tests, stride validation across generations, fence alignment tests, swizzle reporting compatibility, framebuffer rejection, VMA unbind/rebind behavior, and gen3/gen4 bit17 swizzle tests are key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_tiling.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_tiling.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_tiling.h

## Purpose
This header declares the core tiling helpers shared outside the tiling ioctl implementation.

## Important APIs, Types, and Functions
It declares `i915_gem_object_needs_bit17_swizzle`, `i915_gem_fence_size`, and `i915_gem_fence_alignment`, with forward declarations for GEM object and i915 private types.

## Control Flow
No executable logic is present. The declarations expose generation-specific fence sizing/alignment and bit17 swizzle detection implemented in `i915_gem_tiling.c`.

## State and Persistence Behavior
The header has no state. The declared functions inspect object tiling and platform GGTT swizzle state or compute fence geometry.

## Dependencies and Integration Points
Users include shmem page setup/release, physical object conversion checks, and code that needs GTT fence constraints for tiled objects.

## Risks
Consumers must pass valid tiling/stride combinations; implementation uses `GEM_BUG_ON` for invalid internal inputs. Misusing bit17 swizzle detection can cause data corruption after page migration or swap.

## Test Signals
Build coverage plus tiling, shmem swizzle, and phys-conversion tests validate this small interface.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_tiling.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_ttm.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_ttm.c

## Purpose
This file is the i915 GEM integration layer for TTM-backed objects. It implements TTM page-vector creation/population, placement selection, eviction policy, resource-to-SG conversion, shrink/purge behavior, mmap fault handling, object lifecycle, and the TTM system memory region.

## Important APIs, Types, and Functions
Important APIs include `i915_ttm_sys_placement`, `i915_ttm_free_cached_io_rsgt`, `i915_ttm_purge`, `i915_ttm_resource_get_st`, `i915_ttm_resource_mappable`, `i915_ttm_driver`, `i915_ttm_adjust_lru`, `__i915_gem_ttm_object_init`, and `i915_gem_ttm_system_setup`. `struct i915_ttm_tt` extends `ttm_tt` with DMA device, cached refcounted SG table, shmem mode, and optional shmem file. Object ops are `i915_gem_ttm_obj_ops`; TTM callbacks are in `i915_ttm_bo_driver`.

## Control Flow
Placement construction maps GEM memory regions to TTM memory types, applies fixed offsets, contiguous flags, mappable IO limits, GPU-only top-down placement, and fallback placements. `i915_ttm_get_pages` validates initial desired placement without eviction, retries full placement with eviction, populates TT pages if needed, converts current resource into a cached SG table, installs GEM pages, and adjusts TTM LRU priority.

TT population either uses shmem-backed external pages for shrinkable cached objects or the TTM pool for ordinary TT pages. Purge validates into an empty placement, truncates shmem files, clears domains, drops cached IO SG state, and marks the object purged. Mmap faults reserve the BO, reject purged or read-only writes, resurrect swapped-out system TT resources, migrate non-mappable LMEM to a CPU-visible placement if possible, then delegate to TTM VM fault handling while holding runtime PM for IOMEM faults.

## State and Persistence Behavior
This file coordinates `obj->__do_not_access` as an embedded `ttm_buffer_object`, `obj->mm.region`, placements, `bo_offset`, `obj->mm.rsgt`, cached IO SG tables, `obj->ttm.get_io_page`, `obj->mm.ttm_shrinkable`, object domains, cache coherency, userfault lists, TTM resources, TT shmem files, and purged/swapped flags. TTM-backed objects self-manage shrink-list membership outside the normal `mm.pages` lifecycle.

## Dependencies and Integration Points
It integrates with DRM TTM core, i915 TTM buddy managers, memory regions, shmem SG allocation, GEM page helpers, TTM move and PM modules, mmap APIs, runtime PM userfault tracking, local-memory IOMEM mappings, DMA mapping, and refcounted SG helpers.

## Risks
TTM ghost objects must not be downcast. Region state can diverge from TTM resource state during eviction and is corrected only for allowable placements. Cached SG tables and radix iterators must be invalidated on moves. Non-mappable small-BAR LMEM faults can fail with SIGBUS. Shrinker and TTM LRUs interact through extra shrink pins. Purged objects use NULL resources and special recovery paths.

## Test Signals
TTM object create/destroy tests, placement fallback and eviction tests, LMEM/system migration, small-BAR mmap faults, shrink/purge/writeback, swapped TT recovery, cached SG lifetime, userfault RPM tracking, ghost object callback coverage, and suspend/resume with TTM objects are essential signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_ttm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_ttm.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_ttm.h

## Purpose
This header defines the i915 GEM/TTM conversion helpers, TTM placement constants, and internal TTM-backed object APIs.

## Important APIs, Types, and Functions
Inline helpers are `i915_gem_to_ttm`, `i915_ttm_is_ghost_object`, `i915_ttm_to_gem`, `i915_ttm_gtt_binds_lmem`, and `i915_ttm_cpu_maps_iomem`. It declares `i915_ttm_bo_destroy`, `__i915_gem_ttm_object_init`, `i915_ttm_sys_placement`, `i915_ttm_free_cached_io_rsgt`, `i915_ttm_resource_get_st`, `i915_ttm_adjust_lru`, `i915_ttm_purge`, and `i915_ttm_resource_mappable`. Constants map i915 memory types to TTM placements: `I915_PL_LMEM0`, `I915_PL_SYSTEM`, `I915_PL_STOLEN`, and `I915_PL_GGTT`.

## Control Flow
There is no runtime flow beyond simple inline classification. `i915_ttm_is_ghost_object` protects callbacks from downcasting non-i915 TTM ghost BOs. Resource helpers classify non-system memory as LMEM for GTT binding and IOMEM for CPU mapping.

## State and Persistence Behavior
The header stores no state but defines how callers interpret embedded TTM BOs and TTM resources. These interpretations affect cache coherency, SG table creation, mmap behavior, and migration.

## Dependencies and Integration Points
It depends on DRM TTM placement definitions and i915 GEM object types. It is used by TTM core, move, PM, local-memory region, and object lifecycle code.

## Risks
The conversion helper assumes the TTM BO is embedded in `struct drm_i915_gem_object` at `__do_not_access`; using it on ghost objects is invalid. Placement constants must match TTM memory manager registration.

## Test Signals
Build coverage, TTM callback ghost-object paths, system/LMEM resource classification tests, and migration/mmap tests validate the interface.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_ttm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_ttm_move.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_ttm_move.c

## Purpose
This file implements i915's TTM buffer-object move and copy operations. It prepares objects for migration, chooses GPU blit or CPU memcpy fallback, handles failure interception, updates GEM cache/domain state after moves, and exposes selftest failure controls.

## Important APIs, Types, and Functions
Public/internal APIs are `i915_ttm_move_notify`, `i915_ttm_adjust_domains_after_move`, `i915_ttm_adjust_gem_after_move`, `i915_ttm_move`, and `i915_gem_obj_copy_ttm`. Selftest hooks are `i915_ttm_migrate_set_failure_modes` and `i915_ttm_migrate_set_ban_memcpy`. Important internal types are `struct i915_ttm_memcpy_arg` and `struct i915_ttm_memcpy_work`.

## Control Flow
Move notification unbinds active GPU mappings asynchronously and drops GEM pages before TTM changes resources. Accelerated moves use the GT migrate context to clear or copy between SG tables with PAT/cache attributes and LMEM binding classification. If GPU migration is scheduled, the code may arm a custom DMA fence callback that signals success cheaply or queues work to perform memcpy on GPU error. If no GPU path is available or interception fails, synchronous memcpy is used when both source and destination are CPU mappable; otherwise the object enters unknown state and GTs are wedged.

`i915_ttm_move` handles NULL resources with multihop through system memory, purges DONTNEED objects instead of moving them, populates TT pages when required, gathers destination SG tables, attaches migration fences to TTM cleanup, caches IO SG tables for IOMEM destinations, adjusts domains/cache/region, and updates LRUs. `i915_gem_obj_copy_ttm` copies between two locked TTM GEM objects and adds the resulting fence to both reservation objects.

## State and Persistence Behavior
Move state affects TTM resources, `obj->mm.region`, `mem_flags`, cache coherency, read/write domains, `obj->ttm.cached_io_rsgt`, page iterators, migration fences, `unknown_state`, and reservation fences. Async memcpy work owns object and SG references until its fence signals.

## Dependencies and Integration Points
It depends on TTM move cleanup, i915 deps/reservation collection, GT migrate blitter, engine PM, refcounted SG tables, TTM kmap iterators, runtime platform cache rules, GEM unbind/page helpers, and selftest infrastructure.

## Risks
Fallback logic is complex: failing GPU migration to non-mappable memory without memcpy support wedges GTs and marks the object unknown. Reservation fence ordering must protect source and destination. Cached IO SG tables must be refreshed after moves. CCS-aux objects cannot use memcpy. Multihop and purged-object paths must preserve TTM invariants.

## Test Signals
Selftests that force GPU failure, work allocation failure, and memcpy ban are critical. Additional signals include LMEM-to-system and system-to-LMEM migration, eviction moves, copy fences on reservations, CCS object migration, small-BAR non-mappable failures, and data integrity after suspend/move stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_ttm_move.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_ttm_move.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_ttm_move.h

## Purpose
This header declares i915 TTM migration, copy, and post-move state adjustment helpers.

## Important APIs, Types, and Functions
It declares `i915_ttm_move_notify`, selftest-only failure hooks, `i915_gem_obj_copy_ttm`, `i915_ttm_move`, `i915_ttm_adjust_domains_after_move`, and `i915_ttm_adjust_gem_after_move`. It forward-declares TTM BO, operation context, place, resource, TT, GEM object, and refcounted SG types.

## Control Flow
No executable flow exists except `I915_SELFTEST_DECLARE` conditional exposure. The declared functions are called by the TTM device callbacks, PM backup/restore, and migration/copy code.

## State and Persistence Behavior
The header itself stores no state. Its APIs mutate object bindings, page SG tables, domains, memory-region state, migration fences, and TTM resources.

## Dependencies and Integration Points
It depends on `i915_selftest.h` for conditional declarations and is included by TTM core and TTM PM implementation files.

## Risks
Callers must ensure objects are locked and TTM resources are populated where required by `i915_gem_obj_copy_ttm`; otherwise the implementation returns errors or warns.

## Test Signals
Build coverage plus TTM migration selftests and PM backup/restore copy tests validate this interface.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_ttm_move.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_ttm_pm.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_ttm_pm.c

## Purpose
This file backs up and restores TTM-backed local-memory objects across suspend/resume. It either evicts evictable LMEM objects to system memory or creates system-memory backup GEM objects for pinned contents.

## Important APIs, Types, and Functions
Public APIs are `i915_ttm_backup_free`, `i915_ttm_recover_region`, `i915_ttm_backup_region`, and `i915_ttm_restore_region`. `struct i915_gem_ttm_pm_apply` extends region iteration state with `allow_gpu` and `backup_pinned` flags. Internal callbacks are `i915_ttm_backup`, `i915_ttm_recover`, and `i915_ttm_restore`.

## Control Flow
Backup is applied to every object in a memory region using `i915_gem_process_region`. If an object is not IOMEM-backed or already has a backup, it is skipped. If GPU-assisted eviction is allowed and the object is evictable, TTM validates it into system placement. If pinned backup is enabled, not PM-volatile, and not deferred to a later PM stage, a shmem-region backup object is created, optionally with CCS aux allocation, locked, populated, and filled by `i915_gem_obj_copy_ttm`; the backup object is stored on `obj->ttm.backup`.

Recover frees partial backups after suspend failure. Restore locks backup objects, validates swapped-out backups back to system placement, populates them, copies data back into the original object with or without GPU acceleration depending on stage flags, clears the backup pointer, unlocks, and drops the backup reference.

## State and Persistence Behavior
Persistence is represented by `obj->ttm.backup`, a referenced system-memory GEM object holding a copy of LMEM contents. Flags `I915_TTM_BACKUP_ALLOW_GPU` and `I915_TTM_BACKUP_PINNED` define which objects and copy engines are used in a PM phase. PM-volatile objects are intentionally not backed up.

## Dependencies and Integration Points
It integrates with GEM region iteration, TTM placement validation, TTM population/waiting, shmem memory region allocation, TTM copy/move helpers, CCS aux handling, and the staged PM flow in `i915_gem_pm.c`.

## Risks
Pinned framebuffer objects with CCS need aux backup or resume can corrupt display. Backup allocation or copy failures abort suspend and require recovery. Restore is phased: non-early backups wait until GPU use is allowed. Lock ordering depends on region iteration ww contexts.

## Test Signals
Suspend/resume data integrity for LMEM objects, pinned framebuffer preservation, CCS aux backup tests, PM-volatile skip tests, GPU-allowed vs memcpy-only phases, and fault injection for backup allocation/copy failure are relevant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_ttm_pm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_ttm_pm.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_ttm_pm.h

## Purpose
This header declares the TTM local-memory backup, recovery, restore, and object-backup cleanup APIs used by GEM PM code.

## Important APIs, Types, and Functions
It defines `I915_TTM_BACKUP_ALLOW_GPU` and `I915_TTM_BACKUP_PINNED`, and declares `i915_ttm_backup_region`, `i915_ttm_recover_region`, `i915_ttm_restore_region`, and internal `i915_ttm_backup_free`.

## Control Flow
There is no executable flow. The flags control whether backup/restore may use GPU blits and whether pinned objects should receive explicit backup objects.

## State and Persistence Behavior
The header stores no state. The declared implementation manages `obj->ttm.backup` references and TTM region placement across PM phases.

## Dependencies and Integration Points
It forward-declares memory-region and GEM object types and is included by GEM PM, TTM object destruction, and TTM PM implementation code.

## Risks
Using the wrong flag combination in a PM phase can either attempt GPU access too early/late or skip pinned objects that cannot be evicted. Cleanup must be called during object destruction to avoid leaking backup objects.

## Test Signals
Compile coverage, LMEM suspend/resume tests, backup cleanup on object destruction, and recovery after failed suspend validate the contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_ttm_pm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_userptr.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_userptr.c

## Purpose
This file implements the i915 userptr GEM object type, which wraps page-aligned user virtual memory as a restricted proxy GEM object with MMU interval notifier validation and pinned user pages at submission time.

## Important APIs, Types, and Functions
Primary APIs are `i915_gem_object_userptr_submit_init`, `i915_gem_object_userptr_submit_done`, `i915_gem_object_userptr_validate`, and `i915_gem_userptr_ioctl`. Backend ops include `i915_gem_userptr_get_pages`, `i915_gem_userptr_put_pages`, release, and rejected dmabuf/pread/pwrite hooks. `probe_range` validates that a range maps normal struct-page VMAs.

## Control Flow
The ioctl checks platform snooping/LLC support, flags, size, page alignment, access_ok, synchronized mode, read-only hardware support, and optional VMA probing. With MMU notifier support it allocates a proxy object, sets CPU domains/cache coherency, stores the user pointer, marks read-only if requested, inserts an MMU interval notifier for current mm, creates a GEM handle, and drops the allocation ref.

Submission init verifies the object belongs to current mm, reads the notifier sequence, locks and unbinds old pages if needed, pins all user pages with `pin_user_pages_fast` and optional `FOLL_WRITE`, relocks, retries if the notifier invalidated the range, installs the page vector, and calls the backend get_pages. Submit done checks for notifier collision and returns `-EAGAIN` to force retry.

## State and Persistence Behavior
Object state includes `userptr.ptr`, `userptr.notifier`, `notifier_seq`, `pvec`, and `page_ref`. Pages are pinned only while active, converted into an SG table, marked accessed/dirty on release, and unpinned when the final page ref drops. The object is shrinkable, non-mappable by i915 CPU mmap, and marked proxy.

## Dependencies and Integration Points
It integrates with Linux MMU interval notifiers, GUP pinning, VMA iteration, GEM unbind/page helpers, shmem release semantics, GTT DMA mapping, reservation/submission retry paths, and UAPI `DRM_IOCTL_I915_GEM_USERPTR`.

## Risks
User memory lifetime is inherently racy; notifier sequence handling must force retries. Dirtying pages uses `trylock_page` to avoid migrate-folio deadlock, so dirty marking can be missed. Userptr export and CPU access ioctls are intentionally rejected. Unsynchronized userptr is disabled. Platforms without coherent snooping are rejected.

## Test Signals
Userptr ioctl validation, MMU invalidation retry tests, munmap/free while GPU active, read-only GPU mapping checks, GUP pin/unpin leak tests, dirty/accessed page accounting, probe rejection of PFNMAP/MIXEDMAP, and no-dmabuf/pread/pwrite ABI tests are important.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_userptr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_wait.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_wait.c

## Purpose
This file implements GEM object wait and wait-priority behavior for dma-reservation fences, including the `DRM_IOCTL_I915_GEM_WAIT` ioctl and migration-fence waiting.

## Important APIs, Types, and Functions
Important functions are `i915_gem_object_wait`, `i915_gem_object_wait_priority`, `i915_gem_fence_wait_priority`, `i915_gem_fence_wait_priority_display`, `i915_gem_wait_ioctl`, and `i915_gem_object_wait_migration`. Internal helpers wait on individual fences, preboost i915 requests, convert nanosecond timeouts to jiffies, and set fence priorities.

## Control Flow
Object wait prescans all relevant reservation fences and boosts unstarted i915 requests, then iterates fences and waits on each with timeout propagation. i915 fences use `i915_request_wait_timeout`, non-i915 fences use generic `dma_fence_wait_timeout`. Priority helpers recurse one level into fence arrays or the first fence in a chain, then call the engine schedule hook under RCU and bottom-half disable/enable.

The wait ioctl validates flags, looks up the object, records start time, waits interruptibly with priority on all fences, subtracts elapsed time from the user timeout, clamps to zero, and returns `-EAGAIN` instead of `-ETIME` when remaining time is above jiffy precision.

## State and Persistence Behavior
This file stores no persistent state. It observes and may reprioritize reservation fences and request scheduling attributes. The ioctl mutates the user argument's `timeout_ns` to report remaining time.

## Dependencies and Integration Points
It depends on dma-resv iterators, dma-fence arrays/chains, i915 requests/engines/RPS boost, GEM object lookup, migration moving fences, and UAPI wait structs.

## Risks
Timeout conversions must avoid overflow and jiffy precision regressions. Waiting without exclusive object locks means the object can become busy again immediately after success. Priority boosting order is subtle because reservation fence order can affect whether a request appears boost-worthy.

## Test Signals
Wait ioctl timeout/remaining-time tests, zero-time busy compatibility, signal interruption, foreign dma-fence waits, array/chain priority tests, RPS boost behavior, and migration fence waits cover the behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_wait.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/selftests/huge_gem_object.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/selftests/huge_gem_object.c

## Purpose
This selftest helper creates synthetic very large GEM objects without allocating all unique physical pages. It lets tests exercise address-space, SG iteration, GTT binding, and object-size paths with a large DMA size and a smaller real physical footprint.

## Important APIs, Types, and Functions
The public constructor is `huge_gem_object`. Backend object ops are `huge_get_pages` and `huge_put_pages`, with `huge_free_pages` freeing only the real allocated pages. The object stores its real physical size in `obj->scratch`.

## Control Flow
Creation validates nonzero and aligned `phys_size`, `phys_size <= dma_size`, and DMA-size fit in GEM object size, allocates a GEM object, initializes a private GEM object with `dma_size`, sets struct-page memory, CPU read/write domains, cache coherency, and records `phys_size`. Page get allocates an SG table with one entry per DMA page, allocates real highmem pages for the first `phys_size / PAGE_SIZE` entries, then repeats references to those pages through the remaining SG entries to simulate a huge object. It prepares pages for GTT DMA and installs them. Page put finishes GTT pages, frees only the real pages, and clears dirty state.

## State and Persistence Behavior
Persistent test-object state is the synthetic GEM size (`base.size`) and real backing size (`scratch`). SG entries beyond the real page count alias earlier pages, so contents are not a faithful full-size backing store.

## Dependencies and Integration Points
It depends on GEM object initialization, cache coherency helpers, SG iterators, GTT prepare/finish, and selftest-only consumers that need large object behavior.

## Risks
This is not a production object model: aliasing pages can hide data-integrity bugs but is appropriate for address-space stress. Freeing must stop at the real page count to avoid double-free. `sg_alloc_table` page counts are limited by unsigned int.

## Test Signals
Huge-object selftests should validate size reporting, SG iteration beyond real backing, GTT binding/unbinding, error cleanup on allocation or DMA preparation failure, and no double-free on repeated alias pages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/selftests/huge_gem_object.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/selftests/huge_gem_object.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/selftests/huge_gem_object.h

## Purpose
This header declares the huge GEM selftest object constructor and inline accessors for the synthetic object's physical and DMA sizes.

## Important APIs, Types, and Functions
It declares `huge_gem_object(struct drm_i915_private *i915, phys_addr_t phys_size, dma_addr_t dma_size)`. Inline helpers `huge_gem_object_phys_size` and `huge_gem_object_dma_size` return `obj->scratch` and `obj->base.size`.

## Control Flow
There is no executable control flow beyond the inline accessors. The constructor implementation in `huge_gem_object.c` validates sizes and creates the synthetic object.

## State and Persistence Behavior
The header documents that `obj->scratch` is used as the real physical backing size while `obj->base.size` is the larger DMA-visible GEM size. It stores no state itself.

## Dependencies and Integration Points
It includes Linux types and GEM object type definitions, forward-declares `drm_i915_private`, and is consumed by i915 selftests needing large object fixtures.

## Risks
The accessors depend on the selftest object's convention of storing physical size in `scratch`; using them on other GEM objects would be invalid.

## Test Signals
Build coverage and selftests that compare accessor values against constructor arguments validate this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/selftests/huge_gem_object.h -->
