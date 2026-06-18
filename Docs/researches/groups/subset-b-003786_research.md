# Research: subset-b-003786

Grouped research for Xe VM, VRAM, VSEC, and workaround sources. Each section is source-tree-aligned and delimited for reconciliation into per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_vm.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_vm.c

## Purpose

`xe_vm.c` is the main implementation of Xe virtual memory objects, GPU virtual address areas, VM bind ioctls, rebind handling, page-table encoding, VM fault reporting, memory-attribute helper VMAs, and VM snapshot capture. It is the central integration point between the DRM `drm_gpuvm` range manager, Xe page-table update machinery, TTM buffer validation, userptr/SVM invalidation, long-running compute execution, and user-visible VM uAPIs.

## Important APIs, Types, and Functions

The public entry points are `xe_vm_create()`, `xe_vm_lookup()`, `xe_vm_close_and_put()`, `xe_vm_create_ioctl()`, `xe_vm_destroy_ioctl()`, `xe_vm_bind_ioctl()`, `xe_vm_query_vmas_attrs_ioctl()`, `xe_vm_get_property_ioctl()`, `xe_vm_bind_kernel_bo()`, `xe_vm_lock()`, `xe_vm_unlock()`, `xe_vm_invalidate_vma_submit()`, `xe_vm_invalidate_vma()`, `xe_vm_validate_protected()`, the rebind helpers `xe_vm_rebind()`, `xe_vma_rebind()`, `xe_vm_range_rebind()`, `xe_vm_range_unbind()`, and the auxiliary allocators `xe_vm_alloc_madvise_vma()` and `xe_vm_alloc_cpu_addr_mirror_vma()`. It also exposes compute-mode queue participation through `xe_vm_add_compute_exec_queue()`, `xe_vm_remove_compute_exec_queue()`, `xe_vm_add_exec_queue()`, and `xe_vm_remove_exec_queue()`.

The internal operation model is `struct xe_vma_ops` plus `struct xe_vma_op` from `xe_vm_types.h`. `vm_bind_ioctl_ops_create()` converts user bind arguments into `drm_gpuva_ops`; `vm_bind_ioctl_ops_parse()` allocates or splits `struct xe_vma` objects, counts page-table updates per tile, and commits GPUVA tree changes; `vm_bind_ioctl_ops_execute()` locks and validates resources with `drm_exec`, runs page-table update jobs, attaches user fences, and handles unwind. `ops_execute()` is the common tile loop that prepares update operations, submits `xe_pt_update_ops_run()`, collects TLB invalidation fences, and returns a composite `dma_fence_array`.

Page table encoding is supplied through `xelp_pt_ops`, with `xelp_pde_encode_bo()`, `xelp_pte_encode_bo()`, `xelp_pte_encode_vma()`, and `xelp_pte_encode_addr()`. These encode PAT bits, page-size bits, DM bits for VRAM/stolen device memory, read-only state, and scratch/null PTE handling.

## Control Flow and State

VM creation initializes `vm->lock`, `snap_mutex`, GPUVA state, SVM state, range-fence trees, bind queues, optional preempt rebind work, root page tables, optional scratch page tables, and an ASID for user VMs on devices that support USM. For non-migration VMs it creates per-tile VM bind exec queues. Destruction is split between `xe_vm_close_and_put()`, which closes the address space, clears page tables and TLBs, kills bind queues, removes VMAs, tears down SVM and ASID state, and drops the final GPUVM reference, and `vm_destroy_work_func()`, which runs asynchronously because the final put may happen from fence signaling context.

The bind ioctl validates flags, alignment, PAT/coherency, object sizes, PXP key validity, sync entries, exec queue ownership, VM bounds, and CPU address mirror requirements. It then builds one `drm_gpuva_ops` list per bind, commits GPUVA tree changes under the VM write lock, allocates page-table update arrays, performs SVM prefetch range work if needed, and submits update jobs. Failures after partial commit call `vm_bind_ioctl_ops_unwind()` in reverse order to restore removed VMAs and free newly created VMAs.

Rebind state lives in `vm->rebind_list` and per-VMA tile masks. Non-compute rebind happens during validation through `xe_vm_validate_rebind()`. Long-running compute VMs use preempt fences in `vm->preempt.exec_queues` and `preempt_rebind_work_func()`: the worker waits for or triggers preemption, validates evicted BOs and userptr repins, executes rebinds, waits for kernel-operation fences, checks for a repin race, installs fresh preempt fences, resumes queues, or bans the VM on unrecoverable errors.

Fault reporting uses a capped `vm->faults.list` protected by `faults.lock`. `xe_vm_add_fault_entry_pf()` records at most `MAX_FAULTS_SAVED_PER_VM` non-reserved-engine faults; `xe_vm_get_property_ioctl()` reports count and copies fault records to userspace. Snapshots are protected by `snap_mutex`; dumpable VMAs are captured first as metadata and later copied from BOs or userptr memory in `xe_vm_snapshot_capture_delayed()`.

## Dependencies and Integration Points

This file depends on DRM GPUVA/GPUVM helpers, TTM and `dma_resv`, Xe BO validation and migration, `xe_pt` page-table update code, `xe_tlb_inval`, `xe_sync`, `xe_exec_queue`, `xe_svm`, `xe_userptr`, PAT metadata, PXP key checks, runtime PM, tracepoints, and generated WA headers. The WA `22014953428` can force scratch-page creation during `xe_vm_create_ioctl()`. CPU-address-mirror and madvise helper paths are shared with `xe_vm_madvise.c`, while SVM range binds are shared with `xe_svm.c`.

## Risks and Edge Cases

The highest-risk areas are lock ordering, partial-commit unwind, userptr/SVM invalidation races, compute preempt fence lifetime, and dma-fence restrictions in fault mode. `vm_bind_ioctl_check_args()` contains many security-sensitive validation rules around PAT coherency, compression, imported dma-bufs, userptrs, and CPU address mirrors. Purgeable BO state is also delicate: new WILLNEED mappings to DONTNEED or PURGED BOs are rejected, while remap leftovers can inherit DONTNEED. Snapshot capture must avoid UAF by pinning BO references or `mm_struct` references before delayed copying.

## Test Signals

Useful tests include VM create/destroy ioctls for scratch, LR, fault, no-overcommit, and illegal flag combinations; bind/unbind/remap arrays with overlapping ranges; injected `TEST_VM_OPS_ERROR` failures at lock/prepare/run positions; userptr invalidation and repin races; compute-mode preempt rebind under eviction; purgeable DONTNEED/PURGED map and prefetch rejection; PAT/coherency validation on imported and CPU-cached BOs; SVM prefetch to system and VRAM; TLB invalidation paths; VM fault property reporting; and devcoredump snapshot capture for BO, userptr, null, and CPU-address-mirror VMAs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_vm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_vm.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_vm.h

## Purpose

`xe_vm.h` declares the Xe VM and VMA public interface used across the driver. It provides lifetime helpers, locking helpers, VMA accessors, VM mode predicates, bind ioctl entry points, rebind and invalidation APIs, kernel BO binding, snapshot APIs, and VM fault recording hooks.

## Important APIs, Types, and Functions

The header forwards `struct xe_vm`, `struct xe_vma`, `struct xe_userptr_vma`, exec queues, sync entries, SVM ranges, and DRM objects through included type headers. Core declarations include `xe_vm_create()`, `xe_vm_lookup()`, `xe_vm_lock()`, `xe_vm_unlock()`, `xe_vm_close_and_put()`, all VM ioctls, compute queue add/remove helpers, rebind helpers, invalidation helpers, protected-BO validation, snapshot capture/print/free, and `xe_vm_add_fault_entry_pf()`.

Inline helpers are important integration glue: `xe_vm_get()` and `xe_vm_put()` wrap `drm_gpuvm_get/put`; `gpuvm_to_vm()`, `gpuva_to_vm()`, `gpuva_to_vma()`, and `gpuva_op_to_vma_op()` define the embedding conversions; `xe_vma_start()`, `xe_vma_size()`, `xe_vma_end()`, `xe_vma_bo_offset()`, `xe_vma_bo()`, `xe_vma_vm()`, `xe_vma_read_only()`, `xe_vma_userptr()`, `xe_vma_is_null()`, `xe_vma_is_cpu_addr_mirror()`, `xe_vma_has_no_bo()`, and `xe_vma_is_userptr()` centralize layout access. Mode helpers identify scratch, fault, LR, preempt-fence, closed, banned, and eviction-allowed states.

The validation helpers `xe_vm_set_validating()`, `xe_vm_clear_validating()`, `xe_vm_is_validating()`, `xe_vm_set_validation_exec()`, and `xe_vm_validation_exec()` expose task-local validation state stored on the VM reservation object. `xe_vm_has_valid_gpu_mapping()` is an advisory READ_ONCE-based tile-present/tile-invalidated predicate.

## Control Flow and State

This header does not implement control flow, but it documents the call contracts: most VM/VMA helpers expect `vm->lock`, VM dma-resv, or BO dma-resv to be held depending on the path. `xe_vm_queue_rebind_worker()` queues compute-mode rebind work on the ordered workqueue, while `xe_vm_reactivate_rebind()` restarts a deactivated rebind worker after compute submission.

## Dependencies and Integration Points

The header depends on DRM GPUVM, Xe BO, map, VM types, assertions, and TLB invalidation batch types. It is included by VM bind, SVM, exec, page fault, madvise, BO eviction, and debug snapshot code. The accessors deliberately hide the embedded DRM GPUVA layout so implementation details can change without touching callers.

## Risks and Edge Cases

The inline mode predicates can be safely relied on only under their documented locks. `xe_vm_is_closed()` notes that `vm->size` is stable only while `vm->lock` is held. `xe_vm_has_valid_gpu_mapping()` is explicitly advisory and unsafe as a hard synchronization primitive; it is intended only where stale reads are harmless. Validation state relies on pairing WRITE_ONCE and READ_ONCE and assumes the VM dma-resv is held when a caller observes current-task validation.

## Test Signals

Compile coverage is important because this header provides many inline conversions. Runtime assertions should cover userptr/null/CPU-address-mirror classification, closed/banned checks under the VM lock, validation exec pairing, rebind worker reactivation, and opportunistic valid-mapping decisions in eviction, userptr invalidation, and fault paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_vm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_vm_doc.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_vm_doc.h

## Purpose

`xe_vm_doc.h` is a kernel-doc narrative for the Xe VM subsystem. It explains the conceptual model behind VM creation, scratch pages, VM binds, page-table updates, bind engines, munmap-style unbind semantics, userptr invalidation, compute-mode preempt fences, fault mode, access counters, locking, dma-resv slot usage, and future work.

## Important APIs, Types, and Functions

The file has no executable API. Its important content is the `DOC: Xe VM (user address space)` block. It names uAPI concepts such as `DRM_XE_VM_CREATE_FLAG_SCRATCH_PAGE`, `DRM_XE_VM_BIND_OP_MAP`, `DRM_XE_VM_BIND_OP_UNMAP`, `DRM_XE_VM_BIND_OP_MAP_USERPTR`, `DRM_XE_VM_BIND_FLAG_IMMEDIATE`, and VM bind engine class behavior. It also documents internal synchronization concepts that map directly to `xe_vm.c`: `vm->lock`, VM dma-resv, external BO dma-resv, bind queues, user fences, preempt fences, and `DMA_RESV_USAGE_*` slots.

## Control Flow and State

The document describes VM creation as root page-table allocation plus default bind engine creation. VM bind updates are described as a hybrid CPU/GPU page-table modification sequence: newly allocated page-table pages are initialized on the CPU, while updates into existing page-table structures are submitted through GPU jobs unless immediate CPU update bypass applies. Munmap-style unbinds are modeled as full unbinds plus edge rebinds to preserve large-page correctness.

Compute mode flow is documented as a loop that checks closure, pins userptrs, locks VM and BO reservations, validates evicted BOs, waits for preempt fences, rebinds invalidated or evicted memory, waits for the last rebind fence and kernel slot, installs new preempt fences, resumes engines, and retries on userptr invalidation races. Fault-mode flow is documented as ASID lookup, VMA lookup, backing-store allocation, page pin or BO validation/migration, rebind, TLB invalidation, and page-fault response.

## Dependencies and Integration Points

This documentation ties together `xe_vm.c`, `xe_lrc.c`, `xe_guc_ads.c`, userptr MMU notifiers, page fault workers, access counter workers, bind engines, and dma-resv semantics. It is a design map for reasoning about implementation behavior rather than a compiled dependency.

## Risks and Edge Cases

The doc calls out why fault mode cannot use dma fences, why G2H page fault handling must not allocate or acquire VM locks under CT locks, why munmap-style unbinds need kernel-operation ordering, and why eviction/userptr invalidation in fault mode uses lockless leaf-PTE zapping. These are the main areas where implementation drift can introduce deadlocks, memory corruption windows, or incorrect user-visible synchronization.

## Test Signals

Tests and reviews should compare implementation changes against this documented model. Signals include correct ordering of dma-resv slot waits and installs, correct bind-engine ordering for array binds, correct handling of immediate vs deferred fault-mode binds, correct compute preempt fence replacement, and lockdep coverage for VM global lock, VM reservation lock, external BO reservation locks, CT/G2H workers, and notifier paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_vm_doc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_vm_madvise.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_vm_madvise.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_vm_madvise.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_vm_madvise.h

## Purpose

`xe_vm_madvise.h` is the public declaration header for the Xe VM madvise ioctl implementation. It exposes the ioctl entry point without leaking internal madvise helper structures.

## Important APIs, Types, and Functions

The only function declared is `xe_vm_madvise_ioctl(struct drm_device *dev, void *data, struct drm_file *file)`. The header forward-declares `struct drm_device`, `struct drm_file`, and `struct xe_bo`; the `xe_bo` forward declaration is currently not used by the visible prototype but keeps the header ready for BO-related madvise integration.

## Control Flow and State

The header contains no state and no executable control flow. It exists so the DRM ioctl dispatch table or other Xe VM code can call into `xe_vm_madvise.c`.

## Dependencies and Integration Points

The integration point is the DRM ioctl layer for `DRM_IOCTL_XE_MADVISE`. Implementation dependencies remain private to the C file, keeping compile dependencies for callers minimal.

## Risks and Edge Cases

The main risk is API drift: if the ioctl signature or dispatch expectations change, this header and the implementation must stay synchronized. Because it intentionally hides internal state, any future helper exported here should be reviewed to avoid exposing lock-order-sensitive madvise internals.

## Test Signals

Build coverage confirms the ioctl prototype matches the implementation and call sites. Runtime test signals live in `xe_vm_madvise.c` ioctl tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_vm_madvise.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_vm_types.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_vm_types.h

## Purpose

`xe_vm_types.h` defines the core data structures and flags used by the Xe VM implementation: VMAs, userptr VMAs, VM fault records, VM object state, memory attributes, bind-operation state, SVM range operations, and per-operation page-table update arrays.

## Important APIs, Types, and Functions

The key VMA flags are `XE_VMA_READ_ONLY`, `XE_VMA_DESTROYED`, `XE_VMA_ATOMIC_PTE_BIT`, page-size flags `XE_VMA_PTE_4K/2M/1G/64K/COMPACT`, `XE_VMA_DUMPABLE`, `XE_VMA_SYSTEM_ALLOCATOR`, and `XE_VMA_MADV_AUTORESET`. `struct xe_vma_mem_attr` stores preferred location, atomic access, default/current PAT index, and purgeable state. `struct xe_vma` embeds `struct drm_gpuva` and tracks rebind/destroy links, async destruction callbacks, tile state masks, skip-invalidation state, an optional user fence, and memory attributes. `struct xe_userptr_vma` extends `xe_vma` with `struct xe_userptr`.

`struct xe_vm` embeds `struct drm_gpuvm`, SVM state, per-tile bind queues, LRU bulk move state, root and scratch page tables, flags, locks, rebind and destruction work, range-fence trees, userptr state, preempt state, exec queue lists, ASID and last fault VMA, fault list, validation task state, TLB flush state, and file ownership.

Bind operation types include `struct xe_vma_op_map`, `xe_vma_op_remap`, `xe_vma_op_prefetch`, `xe_vma_op_map_range`, `xe_vma_op_unmap_range`, and `xe_vma_op_prefetch_range`. `enum xe_vma_op_flags` tracks commit state for unwind. `struct xe_vma_op` wraps `drm_gpuva_op` with Xe-specific operation payload. `struct xe_vma_ops` is an execution batch with a VMA op list, bind queue, syncs, per-tile `xe_vm_pgtable_update_ops`, and flags such as SVM prefetch, madvise, array-of-binds, skip-TLB-wait, and allow-SVM-unmap.

## Control Flow and State

These structures define how `xe_vm.c` persists state across VM creation, binds, execs, evictions, fault handling, madvise, and destruction. The VM object owns the GPUVA tree and page-table roots. VMAs persist in the GPUVA tree until removed by bind/unbind or VM close. Operation structs are temporary per-ioctl or per-rebind objects and carry enough commit bits to unwind partial updates.

## Dependencies and Integration Points

The file depends on DRM GPUVM/GPUSVM, DRM pagemap utilities, Linux dma-resv/kref/mmu notifier/scatterlist primitives, Xe device types, page-table types, range fences, TLB invalidation types, and userptr state. It is included throughout VM, SVM, BO, exec, page fault, and madvise code.

## Risks and Edge Cases

The lock comments are part of the contract. `tile_invalidated`, `tile_present`, and `tile_staged` have different protection rules for BO, userptr, VM lock, and notifier lock cases; misuse can cause stale GPU mappings or missed invalidations. The unioned `combined_links` and destroy callback/work fields are mutually exclusive lifecycle states and must not be used in the wrong phase. `validation.validating` is task state stored on a shared VM object and must be paired carefully. Purgeable state is protected by BO dma-resv and must remain coherent with BO-level holder counts.

## Test Signals

Important signals include lockdep coverage of documented lock rules, KASAN/UAF coverage for VMA destroy callbacks and delayed work, bind unwind tests that exercise each commit flag, SVM/userptr invalidation races around tile masks, purgeable state transitions under BO locks, and compile coverage for configuration-dependent debug error injection and pagemap fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_vm_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_vram.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_vram.c

## Purpose

`xe_vram.c` probes and describes local memory on discrete Xe devices. It discovers the PCI LMEM BAR, computes per-tile actual and usable VRAM sizes, handles flat CCS or GSM reserved regions, initializes per-tile and aggregate `xe_vram_region` descriptors, and exposes safe accessors for region fields.

## Important APIs, Types, and Functions

The main entry point is `xe_vram_probe(struct xe_device *xe)`. Region objects are allocated by `xe_vram_region_alloc()`. Field accessors are `xe_vram_region_io_start()`, `xe_vram_region_io_size()`, `xe_vram_region_dpa_base()`, `xe_vram_region_usable_size()`, and `xe_vram_region_actual_physical_size()`.

Internal helpers include `resource_is_valid()` for PCI BAR sanity, `determine_lmem_bar_size()` for BAR start/length and write-combining ioremap, `get_flat_ccs_offset()` for reading platform registers that describe flat CCS reservation, `tile_vram_size()` for tile size/offset/usable calculation, `vram_region_init()` for filling an `xe_vram_region`, `print_vram_region_info()` for boot logs, and `vram_fini()` for managed teardown of mappings.

## Control Flow and State

`xe_vram_probe()` exits immediately on non-dGFX devices. For dGFX it validates and maps the LMEM BAR, then iterates tiles. SR-IOV VF mode uses virtual LMEM sizes and cumulative offsets from `xe_tile_sriov_vf_lmem()`. DG1 uses the LMEM BAR length as tile size; other platforms read `SG_TILE_ADDR_RANGE`. Usable size is the offset to flat CCS or GSM, minus tile offset. Each tile region receives physical size, CPU-visible IO size limited by remaining BAR space, DPA base, BAR mapping pointer, and usable size. After per-tile initialization, an aggregate `xe->mem.vram` region is initialized with total physical and available usable size.

## Dependencies and Integration Points

This file depends on PCI BAR resources, DRM managed allocation, MMIO register reads, forcewake, MCR reads, GT/tile topology, SR-IOV VF helpers, and TTM VRAM manager region state. The resulting `xe_vram_region` objects feed memory placement, TTM VRAM managers, pagemap support, migration, and user-visible memory region reporting elsewhere in the driver.

## Risks and Edge Cases

Small BAR systems may expose less CPU-visible VRAM than usable device VRAM, so IO size and usable size must not be confused. Flat CCS platforms require forcewake and correct conversion from hardware view to software view; the code asserts no hole between CCS and GSM on Xe2+. BAR validation and zero IO-size checks prevent unusable configurations. Multi-tile accounting must decrement remaining IO size carefully to avoid mapping a tile beyond CPU-visible BAR space.

## Test Signals

KUnit can cover accessor behavior and `xe_vram_region_actual_physical_size()` is explicitly exported for KUnit. Platform tests should cover non-dGFX no-op, invalid BAR resources, small BAR logging, DG1 sizing, multi-tile offsets, SR-IOV VF virtual LMEM sizing, flat CCS offset calculation, forcewake timeout handling, and devm cleanup clearing mappings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_vram.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_vram.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_vram.h

## Purpose

`xe_vram.h` declares the public VRAM probe and region accessor interface. It keeps callers independent of the concrete `struct xe_vram_region` layout in `xe_vram_types.h`.

## Important APIs, Types, and Functions

The header declares `xe_vram_probe()`, `xe_vram_region_alloc()`, and accessors for IO start, IO size, DPA base, usable size, and actual physical size. It forward-declares `struct xe_device` and `struct xe_vram_region`.

## Control Flow and State

There is no executable control flow in the header. The declared functions are used during device and tile memory initialization and by code that needs read-only VRAM region metadata.

## Dependencies and Integration Points

The header depends only on Linux fixed-width type definitions and is consumed by Xe device/tile setup, TTM VRAM manager setup, memory region reporting, migration, and tests.

## Risks and Edge Cases

The accessors intentionally return zero for NULL regions in the implementation, so callers must distinguish "missing region" from a valid zero-valued field when that matters. Future additions should preserve this low-dependency API boundary.

## Test Signals

Build coverage and probe tests should verify declarations stay synchronized with `xe_vram.c`. Unit tests can call accessors on NULL and initialized regions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_vram.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_vram_freq.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_vram_freq.c

## Purpose

`xe_vram_freq.c` creates read-only sysfs files that report fused HBM/VRAM frequency points for supported tiles. It currently exposes PVC-only `device/tile#/memory/freq0/max_freq` and `min_freq`.

## Important APIs, Types, and Functions

The exported initializer is `xe_vram_freq_sysfs_init(struct xe_tile *tile)`. Sysfs show handlers are `max_freq_show()` and `min_freq_show()`, both using `xe_pcode_read()` with `PCODE_FREQUENCY_CONFIG`, HBM domain selection, and fused P0 or PN subcommands. `dev_to_tile()` maps a sysfs device back to the tile via `kobj_to_tile()`. `vram_freq_sysfs_fini()` removes the attribute group and drops the kobject through devm cleanup.

## Control Flow and State

Initialization is a no-op unless `xe->info.platform == XE_PVC`. On PVC it creates a `memory` kobject below the tile sysfs kobject, registers the `freq0` attribute group, and stores managed cleanup through `devm_add_action_or_reset()`. Reads issue a pcode mailbox command and multiply the returned fused frequency unit by 50 MHz before formatting the value.

## Dependencies and Integration Points

This file depends on Linux sysfs, DRM managed cleanup, Xe tile sysfs, pcode mailbox APIs, pcode command definitions, and platform detection. It integrates with tile sysfs initialization and exposes firmware-reported fuse data to userspace.

## Risks and Edge Cases

Sysfs reads can fail with pcode errors and propagate negative errno to userspace. The kobject parent relationship assumes the attribute device sits below the tile kobject. The values are fused fixed points, not live configuration knobs; they are deliberately read-only. Platform gating prevents creating misleading files on non-PVC hardware.

## Test Signals

Tests should verify no sysfs group appears on non-PVC platforms, PVC creates `memory/freq0/max_freq` and `min_freq`, pcode failures propagate, returned values are scaled by 50, cleanup removes the group, and repeated probe/remove cycles do not leak kobjects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_vram_freq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_vram_freq.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_vram_freq.h

## Purpose

`xe_vram_freq.h` declares the VRAM frequency sysfs initialization function.

## Important APIs, Types, and Functions

The single public function is `xe_vram_freq_sysfs_init(struct xe_tile *tile)`. The header forward-declares `struct xe_tile`.

## Control Flow and State

There is no state in the header. The implementation creates read-only sysfs entries for supported platforms and is called after tile sysfs is ready.

## Dependencies and Integration Points

It is a small interface between tile initialization code and the sysfs/pcode implementation in `xe_vram_freq.c`.

## Risks and Edge Cases

The main risk is calling the initializer before `tile->sysfs` exists; the implementation expects tile sysfs to be initialized first. API drift should be caught by build coverage.

## Test Signals

Build coverage and tile sysfs initialization tests should verify the function remains callable from the expected initialization phase.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_vram_freq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_vram_types.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_vram_types.h

## Purpose

`xe_vram_types.h` defines `struct xe_vram_region`, the driver representation of a local-memory region such as HBM, tile-local VRAM, or future extension memory.

## Important APIs, Types, and Functions

`struct xe_vram_region` stores a back pointer to `xe_device`, unique region id, CPU-visible IO start and size, device physical address base, usable size excluding reserved memory, actual physical size including reserved memory, BAR mapping pointer, embedded `xe_ttm_vram_mgr`, TTM placement id, and optional pagemap/migration fields under `CONFIG_DRM_XE_PAGEMAP`.

## Control Flow and State

The structure is allocated and initialized by `xe_vram.c` during dGFX probe. Its fields persist for the device lifetime and are cleared in managed cleanup for mapping pointers. The TTM manager and optional pagemap cache use the region to represent allocatable device memory.

## Dependencies and Integration Points

The type depends on `xe_ttm_vram_mgr_types.h` and conditionally on `drm_pagemap.h`. It is shared with VRAM probing, TTM placement setup, memory migration, pagemap integration, and any caller that needs concrete region fields.

## Risks and Edge Cases

Callers must distinguish `io_size` from `usable_size`: small BAR devices can have less CPU-visible VRAM than device-usable VRAM. `actual_physical_size` includes stolen/reserved regions, while `usable_size` does not. Conditional pagemap fields require configuration-aware initialization and teardown.

## Test Signals

Probe tests should verify all fields are populated consistently for single-tile, multi-tile, small BAR, and pagemap-enabled builds. Static/build coverage should catch configuration-dependent field users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_vram_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_vsec.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_vsec.c

## Purpose

`xe_vsec.c` registers Intel VSEC auxiliary telemetry/crashlog capabilities for supported Xe platforms and implements a PMT telemetry read callback for Battlemage-style GUID encoded telemetry regions.

## Important APIs, Types, and Functions

The public functions are `xe_vsec_init(struct xe_device *xe)` and `xe_pmt_telem_read(struct device *dev, u32 guid, u64 *data, loff_t user_offset, u32 count)`. Static platform data includes `bmg_telemetry`, `bmg_crashlog`, `bmg_capabilities`, `xe_vsec_info[]`, and `vsec_platforms[]`. `xe_guid_decode()` decodes GUID fields into a SoC remapper memory region index and register offset. `xe_pmt_cb` supplies the `.read_telem` callback to the intel_vsec PMT layer.

## Control Flow and State

`xe_vsec_init()` maps the Xe platform to an internal VSEC platform id, rejects unsupported platforms or missing headers, attaches private PMT callbacks for BMG, and calls `intel_vsec_register()` with device-managed cleanup handled by the VSEC subsystem.

`xe_pmt_telem_read()` decodes the GUID, computes an MMIO address from `BMG_TELEMETRY_OFFSET` plus decoded offset plus user offset, takes `xe->pmt.lock`, checks that the SoC remapper callback exists, requires the device to be runtime-PM active via `xe_pm_runtime_get_if_active()`, selects the telemetry region through `soc_remapper.set_telem_region()`, copies MMIO data with `memcpy_fromio()`, drops runtime PM, and returns the byte count.

## Dependencies and Integration Points

This file depends on Linux `intel_vsec`, PMT register definitions, Xe MMIO, platform types, runtime PM, SoC remapper callbacks, and device type conversion. It imports the `INTEL_VSEC` namespace. Userspace-facing telemetry flows through the intel_vsec auxiliary device rather than Xe-specific ioctls.

## Risks and Edge Cases

GUID decoding is strict: only the BMG device id is accepted, capability type must be valid, and some record/capability pairs deliberately map to zero offset. Reads fail with `-ENODEV` when the GUID or remapper is unsupported and `-ENODATA` when the device is not at an active power level. The telemetry address calculation depends on `count` and `user_offset` supplied by the VSEC layer; bounds expectations should remain aligned with the VSEC header metadata.

## Test Signals

Tests should cover supported and unsupported platforms, GUID decode success for PUNIT/OOBMSM telemetry, watcher, and crashlog records, invalid device id and cap type errors, missing remapper behavior, runtime-suspended reads returning `-ENODATA`, lock serialization, and correct intel_vsec registration with telemetry and crashlog capabilities.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_vsec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_vsec.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_vsec.h

## Purpose

`xe_vsec.h` declares Xe VSEC initialization and PMT telemetry read callbacks.

## Important APIs, Types, and Functions

The header declares `xe_vsec_init(struct xe_device *xe)` and `xe_pmt_telem_read(struct device *dev, u32 guid, u64 *data, loff_t user_offset, u32 count)`. It forward-declares `struct device` and `struct xe_device` and includes Linux types for fixed-width and `loff_t` use.

## Control Flow and State

The header contains no state. The implementation registers intel_vsec auxiliary interfaces during device initialization and serves telemetry reads through the PMT callback.

## Dependencies and Integration Points

It forms the interface between Xe device probe code and the VSEC/PMT implementation. `xe_pmt_telem_read()` is also referenced by the callback table passed to intel_vsec.

## Risks and Edge Cases

The telemetry read prototype must remain compatible with the `pmt_callbacks` contract. Future VSEC support should avoid exposing platform-specific data structures through this small header unless multiple modules need them.

## Test Signals

Build coverage validates prototype compatibility. Runtime coverage belongs to VSEC registration and telemetry read tests in `xe_vsec.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_vsec.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_wa.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_wa.c

## Purpose

`xe_wa.c` defines and processes Xe hardware workaround tables. It covers GT-level register workarounds, engine reset workarounds, LRC/context-image workarounds, generated out-of-band GT/device workarounds, active-workaround bookkeeping, debug dumps, and rare tile-level workaround programming.

## Important APIs, Types, and Functions

The main static data tables are `gt_was[]`, `engine_was[]`, and `lrc_was[]`, each containing `xe_rtp_entry_sr` records with WA names, RTP match rules, and register actions. `oob_was[]` and `device_oob_was[]` include generated C fragments from rule files and are checked against generated counts with `static_assert()`.

Public processing functions are `xe_wa_process_device_oob()`, `xe_wa_process_gt_oob()`, `xe_wa_process_gt()`, `xe_wa_process_engine()`, and `xe_wa_process_lrc()`. Initialization functions are `xe_wa_device_init()` and `xe_wa_gt_init()`. Dump helpers are `xe_wa_device_dump()` and `xe_wa_gt_dump()`. `xe_wa_apply_tile_workarounds()` directly applies uncommon non-GT tile workarounds such as `22010954014` by MMIO RMW when active.

## Control Flow and State

During initialization, `xe_wa_device_init()` allocates a device OOB active bitset and `xe_wa_gt_init()` allocates one contiguous bitset block split across GT, engine, LRC, and OOB active categories. OOB processing builds an `xe_rtp_process_ctx`, enables active tracking, marks OOB initialized, and evaluates generated RTP entries to set active bits. GT, engine, and LRC processing evaluate static tables and store matching register actions into `gt->reg_sr`, `hwe->reg_sr`, or `hwe->reg_lrc`.

The tables are declarative: match rules cover platform, graphics/media version ranges, steps, subplatforms, engine classes, first render/compute selection, even engine instances, SR-IOV exclusion, and other helper predicates. Actions set, clear, or field-set register bits, sometimes with engine-base addressing or readback suppression flags.

## Dependencies and Integration Points

This file depends on the Xe RTP infrastructure, GT and engine types, register definitions, forcewake/MMIO infrastructure, platform and stepping helpers, SR-IOV predicates, generated WA headers and C fragments, and DRM managed memory. Processed register save/restore lists are consumed by GT reset/resume code, engine reset/GuC ADS setup, and LRC/default context setup. OOB bits are queried through `XE_GT_WA()` and `XE_DEVICE_WA()` in other files.

## Risks and Edge Cases

WA table maintenance is high-risk because a too-broad range can program unsupported registers on future IP versions, while a too-narrow range can miss required programming. Readback masks and `XE_RTP_NOCHECK` must be used only where hardware makes read verification impossible or misleading. Active bitset sizes must match table sizes, especially for generated OOB tables. Tile workaround application must skip SR-IOV VFs and should remain rare because it bypasses the RTP save/restore path.

## Test Signals

KUnit or simulated platform tests should verify RTP matching for representative platforms, steps, engine classes, first render/compute predicates, and SR-IOV cases. Static assertions catch generated OOB count drift. Dump tests can confirm active bit names appear. Probe error-injection for `xe_wa_gt_init()` should exercise `ALLOW_ERROR_INJECTION`. Register programming tests should validate GT/engine/LRC save-restore lists and tile RMW behavior for active device WA bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_wa.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_wa.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_wa.h

## Purpose

`xe_wa.h` declares the hardware workaround processing interface and active OOB workaround query macros.

## Important APIs, Types, and Functions

Declared functions include `xe_wa_device_init()`, `xe_wa_gt_init()`, `xe_wa_process_device_oob()`, `xe_wa_process_gt_oob()`, `xe_wa_process_gt()`, `xe_wa_process_engine()`, `xe_wa_process_lrc()`, `xe_wa_apply_tile_workarounds()`, `xe_wa_device_dump()`, and `xe_wa_gt_dump()`. The macros `XE_GT_WA(gt__, id__)`, `XE_DEVICE_WA(xe__, id__)`, and `XE_DEVICE_WA_DISABLE(xe__, id__)` query or clear generated OOB active bits after asserting that OOB processing was initialized.

## Control Flow and State

The header itself has no state, but its macros read and modify `wa_active.oob` bitsets stored on GT or device objects. Initialization must allocate bitsets before processing, and processing must set `oob_initialized` before callers query active OOB workaround bits.

## Dependencies and Integration Points

The header includes `xe_assert.h` and uses generated enum names from generated WA headers indirectly through macro token pasting. It is consumed by device setup, GT setup, engine setup, VM creation, tile programming, and any code path that needs to branch on an OOB workaround.

## Risks and Edge Cases

Calling `XE_GT_WA()` or `XE_DEVICE_WA()` before OOB initialization triggers assertions. Macro ids must match generated names exactly. `XE_DEVICE_WA_DISABLE()` mutates active state and should be used only for deliberate runtime disabling.

## Test Signals

Build coverage validates generated id token names. Runtime tests should verify OOB initialization assertions, active bit queries for known WA/platform matches, and controlled disabling through `XE_DEVICE_WA_DISABLE()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_wa.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_wa_oob.rules -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_wa_oob.rules

## Purpose

`xe_wa_oob.rules` is the source rule list for generated GT out-of-band workaround metadata. These are workarounds that are not applied through the central GT, engine, or LRC register tables, but are recorded as active bits for targeted checks elsewhere in the driver.

## Important APIs, Types, and Functions

The file is not C code. Each non-indented rule starts with a workaround id such as `1607983814`, `22014953428`, or `15015404425_disable`, followed by one or more RTP-style match expressions. Indented continuation lines add alternative match expressions for the same id. The build system generates `generated/xe_wa_oob.h` and `generated/xe_wa_oob.c` from these rules. Runtime C code queries the generated ids through `XE_GT_WA(gt, id)`.

## Control Flow and State

At build time, rules are transformed into generated RTP entries and enum/count definitions. At runtime, `xe_wa_process_gt_oob()` evaluates the generated table against each GT, stores active matches in `gt->wa_active.oob`, and marks the OOB state initialized. Later code branches on those bits, for example VM creation checks `XE_GT_WA(wa_gt, 22014953428)` to force scratch-page VMs on affected DG2 G10/G12 subplatforms.

## Dependencies and Integration Points

The rule expressions depend on RTP match vocabulary such as `GRAPHICS_VERSION_RANGE`, `MEDIA_VERSION`, `PLATFORM`, `SUBPLATFORM`, `MEDIA_STEP`, `GRAPHICS_STEP`, and helper predicates like `xe_rtp_match_not_sriov_vf` and `xe_rtp_match_psmi_enabled`. Generated outputs are included by `xe_wa.c` and other code includes the generated header for ids.

## Risks and Edge Cases

Rule formatting matters because generation relies on ids and continuation indentation. Version ranges must be reviewed whenever new IP versions are enabled; broad ranges can accidentally activate OOB behavior on unsupported hardware. Disable-suffixed rules are semantically different and need careful call-site interpretation. SR-IOV and PSMI helper predicates must match the runtime context where the OOB bit is queried.

## Test Signals

Build generation should fail on malformed rules or generated count mismatches. Runtime tests should validate representative OOB bits on DG2, PVC, Xe_LPG, Xe2, Xe3, Panther Lake, and SR-IOV VF/non-VF contexts. Call-site tests should cover behavior changes controlled by OOB ids, including scratch-page forcing and PSMI-related workarounds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_wa_oob.rules -->
