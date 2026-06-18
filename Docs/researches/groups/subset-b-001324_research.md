# subset-b-001324 AMDGPU VM, display, VPE, VRAM, and XCP research

This grouped report covers the requested AMDGPU source files. Each file section is delimited for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_vkms.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_vkms.c

## Purpose

This file embeds a VKMS-style virtual KMS implementation inside AMDGPU. It gives devices without usable display hardware, SR-IOV virtual functions, emulation, servers, and early bring-up systems an atomic DRM display pipeline without relying on a separate virtual KMS driver or buffer sharing. It exposes virtual CRTCs, connectors, encoders, primary planes, mode lists, and vblank timing through AMDGPU's display and IP block framework.

## Important APIs, types, and functions

The main exported object is `amdgpu_vkms_ip_block`, an `AMDGPU_DCE` IP block using `amdgpu_vkms_ip_funcs`. DRM callbacks are grouped in `amdgpu_vkms_crtc_funcs`, `amdgpu_vkms_crtc_helper_funcs`, `amdgpu_vkms_connector_funcs`, `amdgpu_vkms_conn_helper_funcs`, `amdgpu_vkms_plane_funcs`, and `amdgpu_vkms_primary_helper_funcs`. Important helpers include `amdgpu_vkms_vblank_simulate()`, `amdgpu_vkms_enable_vblank()`, `amdgpu_vkms_get_vblank_timestamp()`, `amdgpu_vkms_prepare_fb()`, `amdgpu_vkms_cleanup_fb()`, `amdgpu_vkms_output_init()`, `amdgpu_vkms_sw_init()`, and `amdgpu_vkms_hw_init()`.

## Control flow, state, and persistence behavior

`amdgpu_vkms_sw_init()` allocates one `struct amdgpu_vkms_output` per CRTC, installs mode config callbacks, creates common display properties, initializes each virtual output, initializes DRM vblank handling, and starts KMS helper polling. Each output creates a primary plane, CRTC, virtual connector, and virtual encoder, then attaches the connector to the encoder. Vblank is simulated with `amdgpu_crtc.vblank_timer`; enabling vblank computes frame duration and starts the hrtimer, while the timer forwards itself and calls `drm_crtc_handle_vblank()`. Atomic flush arms or sends pending vblank events under the DRM event lock. Framebuffer preparation reserves the AMDGPU BO, reserves move fences, pins it in a scanout-capable domain, allocates GART backing, stores the GPU address in `amdgpu_framebuffer.address`, and takes a BO reference; cleanup unpins and drops the reference. `amdgpu_vkms_hw_init()` disables legacy DCE blocks on selected ASICs so the virtual display path owns display exposure. State is runtime-only: DRM mode objects, pinned framebuffer BOs, vblank hrtimers, KMS polling, and hardware DCE-disable bits.

## Dependencies and integration points

The file depends on DRM atomic, connector, framebuffer, simple KMS, EDID, and vblank helpers plus AMDGPU display, object, IRQ, ATOM, and legacy DCE helpers. It integrates with AMDGPU IP block init/fini/suspend/resume, `adev->mode_info`, `amdgpu_display_user_framebuffer_create()`, and TTM/GEM BO pinning. It provides only `DRM_FORMAT_XRGB8888` and uses CVT-generated common modes, with 1024x768 preferred.

## Risks and test signals

Correctness risks are vblank timer races, event delivery while vblank is disabled, framebuffer BO pin/unpin imbalance, leaked mode objects on partial init failure, and assumptions that primary planes are full-screen and unscaled. Hardware risks are accidental interaction between disabled physical DCE and real display hardware on ASICs where VKMS should be virtual-only. Test signals include successful DRM device registration on headless/SR-IOV devices, `modetest` mode enumeration, page flip completion events, stable suspend/resume, no BO refcount leaks after repeated framebuffer changes, and absence of hrtimer warnings during vblank enable/disable churn.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_vkms.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_vkms.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_vkms.h

## Purpose

This header defines the small public interface for AMDGPU's virtual KMS block. It supplies virtual display resolution limits, the output container type, a CRTC-to-output helper, and the IP block version exported by `amdgpu_vkms.c`.

## Important APIs, types, and functions

Constants `XRES_DEF`, `YRES_DEF`, `XRES_MAX`, and `YRES_MAX` set default and maximum virtual mode dimensions. `drm_crtc_to_amdgpu_vkms_output()` maps a `struct drm_crtc *` back to `struct amdgpu_vkms_output` through the embedded AMDGPU CRTC. `struct amdgpu_vkms_output` embeds `struct amdgpu_crtc`, `struct drm_encoder`, and `struct drm_connector`, and stores vblank period and a pending vblank event pointer. `amdgpu_vkms_ip_block` is declared for the AMDGPU IP discovery/init path.

## Control flow, state, and persistence behavior

The header itself has no control flow. Its state contract is that each virtual output owns one CRTC/encoder/connector tuple and stores timing/event state used by the C implementation. These objects are allocated per CRTC during software init and destroyed during mode config cleanup; nothing persists across driver unload or reboot.

## Dependencies and integration points

The definitions assume AMDGPU display types are visible before use, especially `struct amdgpu_crtc` and `struct amdgpu_ip_block_version`. It is included by the VKMS implementation and by any AMDGPU code that needs to register or reference the virtual display IP block.

## Risks and test signals

The main risk is structural coupling: the `container_of()` macro depends on `struct amdgpu_vkms_output` embedding `crtc.base` exactly as expected. Resolution limits also shape DRM mode validation and should match implementation constraints. Test signals are compile coverage, virtual output enumeration, and vblank callbacks correctly recovering their containing output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_vkms.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_vm.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_vm.c

## Purpose

This is the central AMDGPU GPUVM implementation. It manages per-process GPU virtual address spaces, VMID/PASID integration, BO-to-VA mappings, page-table update orchestration, TLB flush sequencing, VM memory accounting, page-fault handling, and VM lifecycle. It is the coordination layer between user mappings, TTM BO movement, SDMA/CPU page table writers, hardware VM flush packets, KFD/SVM, and debugfs/sysfs-visible state.

## Important APIs, types, and functions

The file defines interval-tree operations for `struct amdgpu_bo_va_mapping` and internal helpers for PRT callbacks and TLB sequence callbacks. Important exported APIs include `amdgpu_vm_init()`, `amdgpu_vm_make_compute()`, `amdgpu_vm_fini()`, `amdgpu_vm_manager_init()`, `amdgpu_vm_manager_fini()`, `amdgpu_vm_validate()`, `amdgpu_vm_ready()`, `amdgpu_vm_update_pdes()`, `amdgpu_vm_update_range()`, `amdgpu_vm_bo_update()`, `amdgpu_vm_clear_freed()`, `amdgpu_vm_handle_moved()`, `amdgpu_vm_flush_compute_tlb()`, `amdgpu_vm_bo_add()`, `amdgpu_vm_bo_map()`, `amdgpu_vm_bo_replace_map()`, `amdgpu_vm_bo_unmap()`, `amdgpu_vm_bo_clear_mappings()`, `amdgpu_vm_bo_del()`, `amdgpu_vm_bo_invalidate()`, `amdgpu_vm_bo_move()`, `amdgpu_vm_adjust_size()`, `amdgpu_vm_ioctl()`, `amdgpu_vm_handle_fault()`, `amdgpu_vm_update_fault_cache()`, and `amdgpu_sdma_set_vm_pte_scheds()`.

## Control flow, state, and persistence behavior

VM state is organized around explicit lists protected by `vm->status_lock`. Kernel/PT and per-VM BOs flow through `evicted -> relocated/moved -> idle`; user BOs with independent reservation objects flow through `evicted_user` or `invalidated -> done`; freed mappings wait in `vm->freed` until page tables are cleared. `amdgpu_vm_validate()` validates evicted objects, maps page tables for update, and moves them into relocated or moved states. `amdgpu_vm_update_pdes()` consumes relocated page-directory/page-table objects and updates their parent PDEs. `amdgpu_vm_clear_freed()` clears removed ranges, while `amdgpu_vm_handle_moved()` refreshes moved or invalidated mappings and may clear mappings when a BO cannot be reserved.

`amdgpu_vm_update_range()` is the core update orchestration path. It enters the DRM device, allocates a TLB callback object, chooses whether a flush is required, locks VM eviction, waits/fences unlocked updates as needed, prepares the selected update backend, walks resource or DMA-address ranges with `amdgpu_res_cursor`, calls `amdgpu_vm_ptes_update()`, commits, updates TLB sequence state, optionally creates a TLB fence for KFD/user queues, frees child page tables queued for post-flush release, and unlocks eviction. CPU and SDMA behavior is abstracted through `vm->update_funcs`.

Mapping APIs validate page alignment, overflow, BO bounds, and max PFN, then insert mappings into the VM interval tree and invalid list. Replacement first clears overlapping mappings and creates split before/after mappings as needed. Unmap removes a mapping from valid or invalid lists; valid mappings are put on `vm->freed` so page tables can be cleared later. PRT mappings increment a global PRT user counter and decrement through fence callbacks after unmap completion.

VM init creates scheduler entities, selects CPU or SDMA update mode, allocates and clears the root page directory, creates task info, and stores nonzero PASIDs in an XArray. Compute conversion can switch update backends, map all page tables for CPU access, reset `last_update`, and force TLB fences. Fini unregisters KFD VM state, removes PASID mapping, waits for unlocked and TLB flush fences, clears freed mappings, frees page tables, destroys entities, releases VMIDs, checks memory stats, and drops task info. Persistent effects are runtime kernel objects and hardware page-table/TLB state only.

## Dependencies and integration points

This file integrates with DRM exec and GEM, TTM resources and reservation locks, DMA fences, GPU scheduler entities, AMDGPU BO/TTM/GMC/ring/VMID/KFD/SVM/XGMI/dma-buf layers, KFD compute page fault restore, and debugfs. It emits hardware VM flush, PASID mapping, GDS switch, SPM update, cleaner shader, pipeline sync, and fence packets through ring callbacks. VM manager state includes VMID managers, PRT counters, PASID XArray, PTE scheduler list, and global fault cache.

## Risks and test signals

Risks are high because this code coordinates locking, eviction, asynchronous fences, page table freeing, and fault handling. Specific hazards include reservation-lock ordering, freeing page tables before required TLB flushes, stale PASID-to-VM lookups, interval-tree split errors, memory accounting drift, incorrect CPU/SDMA update mode switching, page fault recursion with SVM restore, missing TLB sequence increments, and incorrect behavior during GPU reset or device unplug. Test signals include GPUVM mmap/map/unmap tests, KFD/SVM page-fault recovery, compute and graphics submissions after BO eviction/migration, suspend/resume and GPU reset, imported dma-buf/XGMI mappings, debugfs VM BO list sanity, zero VM stats at fini, and tracepoints showing expected PTE/PDE and TLB activity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_vm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_vm.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_vm.h

## Purpose

This header defines AMDGPU GPUVM data structures, page table bit encodings, VM manager state, update backends, lifecycle APIs, mapping APIs, and helper macros. It is the contract shared by VM core code, page-table walkers, CPU/SDMA update implementations, TLB-fence code, submission paths, KFD, and fault handlers.

## Important APIs, types, and functions

Important constants include `AMDGPU_VM_MAX_UPDATE_SIZE`, `AMDGPU_VM_PTE_COUNT()`, PTE/PDE flag bits (`AMDGPU_PTE_VALID`, `SYSTEM`, `SNOOPED`, `TMZ`, `READABLE`, `WRITEABLE`, `PRT`, `TF`, `NOALLOC`, `IS_PTE`), mtype macros for GFX9/GFX10/GFX12, `AMDGPU_VM_NORETRY_FLAGS`, VM fault-stop modes, reserved VA ranges, VM update mode bits, VMHUB indices, and `enum amdgpu_vm_level`. Core types include `struct amdgpu_vm_bo_base`, `struct amdgpu_vm_pte_funcs`, `struct amdgpu_vm_update_params`, `struct amdgpu_vm_update_funcs`, `struct amdgpu_vm_fault_info`, `struct amdgpu_mem_stats`, `struct amdgpu_vm`, and `struct amdgpu_vm_manager`. It declares the CPU and SDMA update function tables plus all exported VM, mapping, page-table, fault, and debug APIs.

## Control flow, state, and persistence behavior

The header encodes the main state model. `struct amdgpu_vm` owns the VA interval tree, eviction lock, status lock, memory stats, BO state lists, freed mappings, root page directory, update entities, TLB sequence/fences, generation token, PASID, reserved VMIDs, update backend selection, fault FIFO, KFD process linkage, task info, LRU bulk move data, compute/TLB-fence flags, memory partition id, and cached fault info. `struct amdgpu_vm_manager` stores device-wide VMID managers, address-space sizing, page-table format, PTE writer functions, PTE schedulers, PRT state, update-mode policy, PASID XArray, and global fault info. Inline helpers expose `amdgpu_vm_tlb_seq()` and eviction lock/unlock wrappers that use `memalloc_noreclaim_save()` to avoid reclaim-FS deadlocks from MMU notifiers.

## Dependencies and integration points

The header depends on Linux IDR/KFIFO/RB-tree/sched-mm, DRM scheduler/file/TTM BO types, and AMDGPU sync/ring/ID/TTM headers. It integrates with `amdgpu_vm_pt.c`, `amdgpu_vm_cpu.c`, `amdgpu_vm_sdma.c`, `amdgpu_vm_tlb_fence.c`, ring submission code, KFD, debugfs, and user IOCTL handling. The update abstraction is the key integration point: page-table code calls `vm->update_funcs`, while hardware-specific SDMA packet functions come through `adev->vm_manager.vm_pte_funcs`.

## Risks and test signals

Risks are ABI-like coupling across many VM users. Incorrect bit definitions can corrupt page tables, wrong list semantics can break update state machines, and lock helper misuse can deadlock with MMU notifiers. GFX12 flag differences and no-retry flag translations are especially sensitive. Test signals are full driver compile coverage, successful VM init/fini for graphics and compute contexts, correct page fault status reporting, KFD TLB flush behavior, and no lockdep complaints around eviction locks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_vm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_vm_cpu.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_vm_cpu.c

## Purpose

This file implements the CPU-backed VM page-table update backend. It is selected for graphics or compute VMs when `vm_update_mode` requests CPU writes, usually on large-BAR systems where VRAM page tables are CPU-visible.

## Important APIs, types, and functions

The exported object is `amdgpu_vm_cpu_funcs`, a `struct amdgpu_vm_update_funcs`. Its methods are `amdgpu_vm_cpu_map_table()`, `amdgpu_vm_cpu_prepare()`, `amdgpu_vm_cpu_update()`, and `amdgpu_vm_cpu_commit()`.

## Control flow, state, and persistence behavior

`amdgpu_vm_cpu_map_table()` marks a page-table BO as CPU-access-required and kmap's it. `amdgpu_vm_cpu_prepare()` waits synchronously on an optional `amdgpu_sync`. `amdgpu_vm_cpu_update()` waits for kernel-usage fences on the target PD/PT reservation object, converts the page-entry byte offset to a CPU pointer, traces the operation, maps GART DMA addresses when `pages_addr` is supplied, and writes each entry with `amdgpu_gmc_set_pte_pde()`. `amdgpu_vm_cpu_commit()` increments the VM TLB sequence if needed, issues a memory barrier, and flushes HDP unless a reset is already holding the reset-domain semaphore. State changes are direct writes to CPU-mapped page-table memory plus TLB sequence updates.

## Dependencies and integration points

The backend depends on AMDGPU BO kmap helpers, DMA reservation waits, GMC PTE/PDE encoding, reset-domain locking, HDP flushing, and VM tracepoints. It is installed into `vm->update_funcs` by `amdgpu_vm_init()` or `amdgpu_vm_make_compute()`.

## Risks and test signals

Risks include using CPU update on systems without fully visible VRAM, missing synchronization with pending GPU page-table moves, stale HDP visibility, and long blocking waits in paths expecting asynchronous SDMA behavior. Test signals are successful compute VM conversion to CPU updates, no page faults after BO moves, correct TLB invalidation sequence increments, and no reset-time deadlocks around HDP flushing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_vm_cpu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_vm_pt.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_vm_pt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_vm_sdma.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_vm_sdma.c

## Purpose

This file implements the SDMA-backed VM page-table update backend. It builds scheduler jobs and indirect buffers that write or copy PTE/PDE entries through hardware packet functions rather than CPU stores.

## Important APIs, types, and functions

The exported object is `amdgpu_vm_sdma_funcs`. Its methods are `amdgpu_vm_sdma_map_table()`, `amdgpu_vm_sdma_prepare()`, `amdgpu_vm_sdma_update()`, and `amdgpu_vm_sdma_commit()`. Internal helpers include `amdgpu_vm_sdma_alloc_job()`, `amdgpu_vm_sdma_copy_ptes()`, and `amdgpu_vm_sdma_set_ptes()`. It uses `AMDGPU_VM_SDMA_MIN_NUM_DW` and `AMDGPU_VM_SDMA_MAX_NUM_DW` to size command buffers.

## Control flow, state, and persistence behavior

`map_table()` ensures PD/PT BOs have GART mappings. `prepare()` allocates an AMDGPU VM update job on the immediate or delayed VM scheduler entity and pushes sync dependencies into the job. `update()` adds dependencies on kernel fences from the target table, then emits set commands for contiguous physical mappings or stages generated PTE values at the end of the IB and copies them into the page table for discontiguous `pages_addr` mappings. If the IB runs low on space it commits the current job and allocates a new one. `commit()` pads the IB, increments TLB sequence if needed, submits the job, records `last_unlocked` for unlocked updates or adds a bookkeeping fence to the root reservation object, and optionally returns the delayed fence with `DRM_SCHED_FENCE_DONT_PIPELINE` set.

## Dependencies and integration points

The backend depends on AMDGPU job allocation/submission, VM scheduler entities, SDMA/GMC-specific `vm_pte_funcs`, ring padding, BO GPU offsets, DMA reservation iterators, DRM scheduler dependencies, and VM tracepoints. It is the default update backend for many graphics VMs and for compute VMs when CPU updates are disabled.

## Risks and test signals

Risks include underestimated IB space, dependency leaks or missing fence refs, staging PTEs over command space, incorrect delayed/immediate entity selection, and failing to serialize TLB flushes when the page-table queue shares hardware with userspace. Test signals are VM update jobs visible on SDMA/page queues, clean fence completion, correct behavior with discontiguous system memory, no IB length warnings, successful fallback across multiple committed jobs for large mappings, and no page faults after SDMA-updated mappings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_vm_sdma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_vm_tlb_fence.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_vm_tlb_fence.c

## Purpose

This file creates a synthetic DMA fence that represents completion of a PASID TLB flush after VM page-table updates. It is used when AMDGPU needs a fenceable TLB invalidation, especially for KFD or user queue paths where page-table memory must not be freed until invalidation completes.

## Important APIs, types, and functions

The private `struct amdgpu_tlb_fence` embeds `struct dma_fence`, device pointer, dependency fence, work item, spinlock, and PASID. The exported API is `amdgpu_vm_tlb_fence_create()`. Internal functions are the DMA fence ops name helpers and `amdgpu_tlb_fence_work()`.

## Control flow, state, and persistence behavior

`amdgpu_vm_tlb_fence_create()` allocates a TLB fence object. On allocation failure it synchronously waits for the input dependency, flushes the PASID TLB, and returns a stub fence because page tables have already been updated and the operation cannot fail cleanly. On success it stores the dependency and PASID, initializes a work item and fence with the VM TLB fence context and current TLB sequence, takes an extra reference for the worker, schedules work, and replaces the caller's fence pointer with the synthetic fence. The worker waits on the dependency, drops it, calls `amdgpu_gmc_flush_gpu_tlb_pasid()`, records an error on the fence if the flush fails, signals the fence, and drops the worker reference.

## Dependencies and integration points

The file depends on Linux DMA fences and workqueues plus AMDGPU GMC PASID TLB flush helpers. It is called from `amdgpu_vm_update_range()` when `vm->need_tlb_fence` is set and updates are not unlocked; the returned fence is also attached to the VM root reservation object.

## Risks and test signals

Risks include workqueue ordering, flush failure propagation, PASID reuse while an old fence is pending, and the OOM fallback blocking in sensitive paths. The TODO about a separate workqueue signals possible latency isolation risk. Test signals are KFD/user queue unmap stress, page-table free-after-flush correctness, fence error visibility on TLB flush failure injection, and no use-after-free when destroying VMs with pending TLB fences.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_vm_tlb_fence.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_vpe.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_vpe.c

## Purpose

This file implements AMDGPU's Video Processing Engine IP block support for VPE 6.1 family hardware. It handles early IP function selection, firmware loading, a command ring, DPM configuration, power gating, idle work, ring packet emission, preemption, reset, self-tests, and a reset-mask sysfs attribute.

## Important APIs, types, and functions

Externally visible functions include `amdgpu_vpe_configure_dpm()`, `amdgpu_vpe_psp_update_sram()`, `amdgpu_vpe_init_microcode()`, `amdgpu_vpe_ring_init()`, `amdgpu_vpe_ring_fini()`, `amdgpu_vpe_sysfs_reset_mask_init()`, and `amdgpu_vpe_sysfs_reset_mask_fini()`. The IP block is `vpe_v6_1_ip_block`, using `vpe_ip_funcs`. The ring function table `vpe_ring_funcs` supplies packet operations for NOP, IB, fence, VM flush, register writes/waits, conditional execute, preempt, begin/end use, and reset.

## Control flow, state, and persistence behavior

Early init selects VPE 6.1 function hooks based on IP version, enables collaborate mode for IP 6.1.1, installs ring functions, and caches register offsets. Software init allocates a one-page GTT command buffer, initializes IRQ, ring, microcode, reset mask, and sysfs. Microcode init requests `amdgpu/<ip-version>.bin`, parses firmware version and feature version, and registers VPE context/control firmware chunks for PSP loading when PSP firmware loading is active. Hardware init ungates VPE, loads microcode through hardware-specific callbacks, and starts the ring. Hardware fini cancels idle work, stops the ring, and gates power.

The ring path writes VPE-specific packets for indirect buffers, fences/traps, pipeline sync, register writes, register waits, VM flushes through GMC helpers, and conditional execution. `begin_use()` cancels idle power-down, ungates VPE, and toggles a context indicator on first context use. `end_use()` schedules delayed idle work. The idle worker waits until no emitted fences remain and, for older PM firmware needing DPM0 at power-down, until the requested DPM level is zero before gating VPE.

## Dependencies and integration points

The file depends on firmware loading, AMDGPU ucode metadata, PSP, SMU/DPM clock tables, SOC15 flush helpers, VPE 6.1 register functions, ring/fence/IB infrastructure, workqueues, and AMDGPU reset helpers. It integrates with power management through `amdgpu_device_ip_set_powergating_state()` and `amdgpu_dpm_enable_vpe()`, and with sysfs through `vpe_reset_mask`.

## Risks and test signals

Risks include firmware header mismatch, DPM ratio calculation errors, power-gating races with in-flight fences, collaborate-mode doorbell assumptions, ring preemption timeout handling, CSA address assumptions, and reset path failures leaving the ring unusable. Test signals are successful VPE firmware load, ring and IB tests writing `0xdeadbeef`, VM flush packet operation on VPE jobs, idle power-gating/resume under repeated submissions, reset-mask sysfs presence, and timeout recovery through `vpe_ring_reset()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_vpe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_vpe.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_vpe.h

## Purpose

This header defines the AMDGPU VPE state object, hardware callback interface, register cache, exported helper APIs, and IP block declaration for VPE v6.1 support.

## Important APIs, types, and functions

`AMDGPU_MAX_VPE_INSTANCES` caps supported instances. `struct vpe_funcs` declares hardware-specific callbacks for register offsets, register setup, IRQ init, firmware init/load, and ring lifecycle. `struct vpe_regs` caches register offsets used by common code. `struct amdgpu_vpe` contains the ring, trap IRQ source, function table, register table, firmware metadata, command buffer BO/GPU/CPU addresses, idle delayed work, context state, instance count, collaborate-mode flag, and supported reset mask. Public APIs include VPE firmware, ring, DPM, and sysfs helpers. Convenience macros call optional function pointers with zero defaults.

## Control flow, state, and persistence behavior

The header itself does not run code. It defines how common VPE code delegates ASIC-specific behavior through `vpe_funcs` while keeping shared ring, firmware, idle-work, and reset state in `struct amdgpu_vpe`. State exists for the life of the AMDGPU device and is initialized/freed by `amdgpu_vpe.c`.

## Dependencies and integration points

It depends on AMDGPU ring and IRQ types plus `vpe_6_1_fw_if.h`. The declared `vpe_v6_1_ip_block` is consumed by AMDGPU IP discovery/init code, and hardware-specific files fill `vpe_funcs`.

## Risks and test signals

Risks are mostly interface drift: common code assumes callbacks are present or safely optional, register offsets are initialized before use, and firmware metadata matches the included interface. Test signals are compile coverage across supported VPE IP versions, successful early init callback installation, and ring/sysfs paths working when optional callbacks are absent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_vpe.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_vram_mgr.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_vram_mgr.c

## Purpose

This file implements AMDGPU's VRAM TTM resource manager on top of `gpu_buddy`. It allocates and frees VRAM blocks, tracks visible VRAM usage, handles reserved ranges, exports VRAM resources as scatter-gather tables, reports sysfs memory information, supports placement compatibility/intersection checks, and records task ownership for block-address queries.

## Important APIs, types, and functions

The TTM manager callbacks are in `amdgpu_vram_mgr_func`: `amdgpu_vram_mgr_new()`, `amdgpu_vram_mgr_del()`, `amdgpu_vram_mgr_intersects()`, `amdgpu_vram_mgr_compatible()`, and `amdgpu_vram_mgr_debug()`. Exported/helper APIs include `amdgpu_vram_mgr_bo_visible_size()`, `amdgpu_vram_mgr_reserve_range()`, `amdgpu_vram_mgr_query_page_status()`, `amdgpu_vram_mgr_query_address_block_info()`, `amdgpu_vram_mgr_alloc_sgt()`, `amdgpu_vram_mgr_free_sgt()`, `amdgpu_vram_mgr_vis_usage()`, `amdgpu_vram_mgr_clear_reset_blocks()`, `amdgpu_vram_mgr_init()`, and `amdgpu_vram_mgr_fini()`. Sysfs attributes expose total/visible/used/vendor memory information.

## Control flow, state, and persistence behavior

Init registers a DRM memory cgroup region, initializes the TTM resource manager with real VRAM size, initializes locks and reservation/allocation lists, initializes `gpu_buddy`, installs the VRAM manager for `TTM_PL_VRAM`, and marks it used. Allocation computes placement bounds, reserves top VRAM for VM page tables for non-kernel BOs, chooses contiguous or THP-sized chunks, applies buddy flags for top-down/range/clear/DCC, allocates blocks under `mgr->lock`, records current task pid/comm, optionally trims DCC-aligned contiguous allocations, calculates `res->start`, visible usage, contiguity, and bus caching, then returns the TTM resource. Free removes task ownership, frees blocks back to buddy, replays pending reservations, updates visible usage, finalizes the resource, and frees it.

Reserved ranges are stored first in `reservations_pending`; `amdgpu_vram_mgr_do_reserve()` attempts to allocate them from buddy, moves successful reservations to `reserved_pages`, and accounts usage. Visible usage is tracked in `mgr->vis_usage` and computed per buddy block against `adev->gmc.visible_vram_size`. SG export walks resource blocks, maps physical VRAM aperture ranges with `dma_map_resource()`, and builds an `sg_table`.

## Dependencies and integration points

The file depends on TTM resource management, DRM cgroups, `gpu_buddy`/DRM buddy helpers, DMA mapping, AMDGPU BO flags, GMC sizing, resource cursors, sysfs, and debug printers. It integrates with BO placement/eviction, dma-buf/peer export through SG tables, memory accounting, VRAM vendor reporting, and reset clear-state management.

## Risks and test signals

Risks include buddy allocation fragmentation, incorrect visible usage accounting, DCC alignment trimming mistakes, over-reserving VRAM, non-contiguous fallback behavior for supposedly contiguous BOs, SG map/unmap leaks, and stale `allocated_vres_list` task ownership. Test signals include VRAM allocation stress with mixed sizes, contiguous allocation fallback, visible VRAM sysfs values matching allocations, reserved firmware ranges surviving allocations, dma-buf export/import of VRAM, debugfs buddy dumps, and clean manager fini after evict-all.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_vram_mgr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_vram_mgr.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_vram_mgr.h

## Purpose

This header defines the VRAM manager's public structures and small helpers around `gpu_buddy` blocks and AMDGPU TTM resources.

## Important APIs, types, and functions

`struct amdgpu_vram_mgr` embeds a `ttm_resource_manager`, `gpu_buddy`, mutex, pending/reserved reservation lists, atomic visible usage, default page size, and allocated-resource list. `struct amdgpu_vres_task` stores pid/command ownership. `struct amdgpu_vram_block_info` reports a block start, size, and owning task. `struct amdgpu_vram_mgr_resource` extends `ttm_resource` with allocated buddy blocks, flags, list node, and task owner. Inline helpers expose block start/size/cleared state, convert `ttm_resource` to AMDGPU VRAM resource, and mark a resource cleared. The exported query is `amdgpu_vram_mgr_query_address_block_info()`.

## Control flow, state, and persistence behavior

There is no standalone control flow. The structures define the state that `amdgpu_vram_mgr.c` maintains while the device is active: buddy allocator contents, reservation lists, visible usage, and per-allocation task metadata. State is rebuilt on driver init and destroyed on manager fini.

## Dependencies and integration points

The header depends on Linux `gpu_buddy` and TTM resource types. It is included by AMDGPU memory management code that needs to inspect VRAM allocations, mark cleared resources, or query which task owns a physical VRAM address block.

## Risks and test signals

Risks include misuse of the `to_amdgpu_vram_mgr_resource()` cast on non-VRAM resources, double-setting `GPU_BUDDY_CLEARED`, and stale task metadata if resources are not removed from the allocation list. Test signals are compile coverage, clear-state reset behavior, and address-owner queries returning expected pid/comm during VRAM allocation stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_vram_mgr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_xcp.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_xcp.c

## Purpose

This file implements AMDGPU XCP, the compute partition manager. It tracks XCP partitions, maps IP instances into partitions, creates per-partition DRM nodes, routes file opens and scheduler selection to partitions, handles partition-mode switching, exposes partition resource/metric sysfs, and coordinates KFD around partition changes.

## Important APIs, types, and functions

Transition APIs are `amdgpu_xcp_prepare_suspend()`, `amdgpu_xcp_suspend()`, `amdgpu_xcp_prepare_resume()`, and `amdgpu_xcp_resume()`, implemented through `amdgpu_xcp_run_transition()`. Manager and mode APIs include `amdgpu_xcp_init()`, `amdgpu_xcp_switch_partition_mode()`, `amdgpu_xcp_restore_partition_mode()`, `amdgpu_xcp_query_partition_mode()`, `amdgpu_xcp_mgr_init()`, `amdgpu_xcp_update_supported_modes()`, `amdgpu_xcp_pre_partition_switch()`, and `amdgpu_xcp_post_partition_switch()`. Runtime APIs include `amdgpu_xcp_get_partition()`, `amdgpu_xcp_get_inst_details()`, `amdgpu_xcp_dev_register()`, `amdgpu_xcp_dev_unplug()`, `amdgpu_xcp_open_device()`, `amdgpu_xcp_select_scheds()`, `amdgpu_xcp_release_sched()`, `amdgpu_xcp_update_partition_sched_list()`, `amdgpu_xcp_sysfs_init()`, and `amdgpu_xcp_sysfs_fini()`.

## Control flow, state, and persistence behavior

`amdgpu_xcp_mgr_init()` allocates a manager, stores device/function hooks, initializes the lock, optionally initializes partitions, attaches the manager to the device, and allocates extra partition DRM devices. `amdgpu_xcp_init()` clears old XCP validity, asks the hardware-specific manager for IP details per XCP/block, adds valid blocks, calculates memory partition ids, sets unique IDs from GFX instance UID data, sets the mode and memory allocation mode, and rebuilds partition scheduler lists. Partition switching takes `xcp_lock`, marks mode transient, calls the hardware switch hook, updates sysfs visibility on success, and repairs cached mode on failure.

Runtime file open maps a render node to an XCP id and assigns `fpriv->vm.mem_id`. Scheduler selection picks the least-used partition when the file has no partition, otherwise uses the selected XCP's scheduler array for the requested hardware IP/priority and increments a partition refcount. Release decrements the refcount for the scheduler's ring partition. Scheduler-list updates assign each ring an `xcp_id` based on ring type and instance mask, then populate per-XCP scheduler arrays; selected VCN rings can be shared by adjacent partitions.

Sysfs configuration creates `compute_partition_config` with supported XCP modes, optional supported NPS modes, writable `xcp_config`, and per-resource child kobjects with `num_inst` and `num_shared`. Per-partition `xcp` kobjects expose metrics from DPM and hide attributes when a partition is invalid. State is runtime-only and tied to current partition mode, DRM nodes, KFD init state, scheduler arrays, sysfs kobjects, and hardware partition configuration.

## Dependencies and integration points

The file depends on AMDGPU XCP manager hooks, DRM device allocation/registration, AMD partition driver redirection, ring schedulers, KFD init/fini, DPM metrics, GFX/XCC topology, GMC memory partition modes, and sysfs/kobject APIs. It also touches per-file private VM memory partition selection through `fpriv->vm.mem_id`.

## Risks and test signals

Risks include switching partition mode while queues are active (the pre-switch TODO is explicit), stale cached mode versus hardware mode, sysfs kobject cleanup mistakes, out-of-range scheduler array indexing by ring type/priority, refcount imbalance in scheduler selection/release, invalid partition opens, and shared VCN partition assignment errors. Test signals include successful creation/removal of render nodes, valid partition-specific file opens, scheduler selection load balancing, KFD teardown/reprobe on mode switch, sysfs `compute_partition_config` contents, DPM metrics reads per XCP, and ring `xcp_id` assignments matching hardware instance masks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_xcp.c -->
