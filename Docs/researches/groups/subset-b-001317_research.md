# subset-b-001317 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_gfx.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_gfx.c

## Purpose
`amdgpu_gfx.c` provides common AMDGPU graphics/compute IP block helpers shared by generation-specific GC implementations. It owns queue selection and bitmap policy, KIQ setup, MQD backing allocation, compute and graphics queue map/unmap, KIQ register access, GFXOFF gating, RAS glue, compute partition sysfs, cleaner-shader/process-isolation control, workload power-profile tracking, command stream preamble construction, and debugfs scheduler masks.

## Important APIs, types, and functions
Key exported helpers include `amdgpu_gfx_compute_queue_acquire()`, `amdgpu_gfx_graphics_queue_acquire()`, `amdgpu_gfx_kiq_init()`, `amdgpu_gfx_kiq_init_ring()`, `amdgpu_gfx_mqd_sw_init()`, `amdgpu_gfx_enable_kcq()`, `amdgpu_gfx_disable_kcq()`, `amdgpu_gfx_enable_kgq()`, `amdgpu_gfx_disable_kgq()`, `amdgpu_kiq_rreg()`, `amdgpu_kiq_wreg()`, `amdgpu_kiq_hdp_flush()`, and `amdgpu_gfx_cp_init_microcode()`. User/admin interfaces are created through `amdgpu_gfx_sysfs_init()` and the debugfs mask initializers. RAS entry points are `amdgpu_gfx_ras_sw_init()`, `amdgpu_gfx_ras_late_init()`, `amdgpu_gfx_cp_ecc_error_irq()`, `amdgpu_gfx_process_ras_data_cb()`, and `amdgpu_gfx_ras_error_func()`.

## Control flow
Queue ownership starts by translating MEC/ME pipe queue coordinates into bit indexes, then populating `adev->gfx.mec_bitmap[xcc].queue_bitmap` and `adev->gfx.me.queue_bitmap` according to multipipe policy, ASIC generation, module parameters, and XCC count. KIQ initialization allocates an EOP/HPD BO, picks an otherwise unowned MEC queue that can issue required queue-management packets, initializes an unscheduled ring, and later allocates MQD BOs/backups for KIQ, KGQ, and KCQ rings.

Queue enable and disable flow either uses MES legacy map/unmap helpers or emits KIQ PM4 packets under `kiq->ring_lock`. KCQ enable builds a set-resource queue mask, flushes HDP, maps each compute ring, commits the KIQ ring, and waits with a ring test. KGQ enable maps graphics rings only from the master XCC. Disable paths unmap or preempt the same ring sets and then run a ring test to confirm command processing.

GFXOFF control is reference-counted by `gfx_off_req_count` under `gfx_off_mutex`: disable cancels delayed enable work and asks SMU to ungate GFX; enable decrements the count and either schedules delayed gating or gates immediately for suspend paths. KIQ register read/write and HDP flush emit tiny command sequences plus polling fences, with early bailout during GPU reset or interrupt context to avoid deadlocking recovery.

Sysfs handlers expose current/available compute partition modes, partition memory allocation mode, cleaner shader execution, isolation enforcement, and supported reset masks. Partition switching validates SPX/DPX/TPX/QPX/CPX against XCC topology and takes the reset-domain semaphore. Cleaner shader execution creates a temporary scheduler entity, submits a tiny kernel IB marked for isolation/cleaner shader handling, and waits for completion. Isolation begin/end hooks coordinate kernel submissions with KFD user queues through delayed work and scheduler stop/start calls. Power profile hooks toggle fullscreen3D or compute profiles while rings have emitted fences or submissions.

## State and persistence behavior
State is runtime-only in `struct amdgpu_device` and hardware queues. Persistent-looking values such as firmware versions, MQD backups, queue bitmaps, GFXOFF reference count, XCP partition state, isolation mode arrays, cleaner shader BOs, and workload profile flags are recreated on driver initialization. Firmware image metadata is copied into `adev->firmware.ucode[]` when PSP loading is used. Sysfs writes change in-memory driver state or request hardware partition changes; no on-disk persistence is used.

## Dependencies and integration points
The file depends on `amdgpu_ring`, `amdgpu_rlc`, MES, SMU/DPM, PSP firmware loading, RAS, KFD, XCP partition management, XGMI, TTM BO allocation, DRM scheduler entities, debugfs, sysfs, runtime PM, reset-domain semaphores, and generation-specific KIQ/GFX function tables. It is a central integration layer between common scheduling/memory management and ASIC-specific GC implementations.

## Risks and edge cases
High-risk areas include queue bitmap mismatches with hardware topology, KIQ queue selection constraints, partial MQD allocation cleanup, MES-vs-KIQ path divergence, queue map/unmap commands issued during reset, KIQ polling timeouts, GFXOFF reference-count imbalance, sysfs partition switching while reset/suspend is active, cleaner shader submission when kernel queues are disabled, and isolation scheduling races with KFD. The queue mask uses a 64-bit set-resource mask even though software constants allow up to 128 queues, so future hardware with more enabled queues needs review.

## Test signals
Useful signals are ring bring-up and ring tests across single/multiple XCC devices, MES enabled and disabled queue map paths, KIQ register read/write timeout injection, GFXOFF toggling and residency counters, sysfs partition mode validation, cleaner shader sysfs execution per XCP, KFD/process-isolation stress, RAS ECC interrupt dispatch, debugfs scheduler mask toggling, suspend/resume with GFXOFF immediate mode, SR-IOV VF unload/reload, and firmware loading size accounting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_gfx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_gfx.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_gfx.h

## Purpose
`amdgpu_gfx.h` is the common graphics/compute IP state and API contract for AMDGPU. It defines queue limits, compute partition modes, RAS memory identifiers, ME/MEC/KIQ structures, graphics configuration caches, CU layout, cleaner shader/isolation state, `struct amdgpu_gfx`, ASIC function tables, and prototypes implemented by `amdgpu_gfx.c`.

## Important APIs, types, and functions
Important types include `struct amdgpu_gfx`, `struct amdgpu_gfx_funcs`, `struct kiq_pm4_funcs`, `struct amdgpu_kiq`, `struct amdgpu_mec`, `struct amdgpu_me`, `struct amdgpu_gfx_config`, `struct amdgpu_cu_info`, `struct amdgpu_gfx_ras`, `struct amdgpu_gfx_shadow_info`, and `struct amdgpu_isolation_work`. Enums define graphics pipe priorities, XCP compute partition modes, partition memory allocation modes, queue unmap actions, and GFX RAS memory IDs. Inline helpers convert partition modes to sysfs text and create bitmasks.

## Control flow
The header has no standalone execution, but it defines how GC implementations plug into common code. ASIC files fill `amdgpu_gfx_funcs` for register selection, wave reads, partition queries/switching, XCC mapping, and HDP flush-mask lookup. KIQ packet emitters are provided through `kiq_pm4_funcs`, and common code calls those function pointers while mapping queues, invalidating TLBs, querying status, or resetting hardware queues.

## State and persistence behavior
`struct amdgpu_gfx` aggregates volatile driver state for firmware handles and versions, rings, queue counts, queue bitmaps, IRQ sources, CU/config caches, power-gating state, RAS pointers, XCC partition state, MQD backup buffers, cleaner shader BO state, delayed isolation work, workload profile counters, and debug/control flags. The state is not durable across driver reloads; it mirrors firmware images, hardware topology, and runtime submissions.

## Dependencies and integration points
The header depends on ring, RLC, IMU, SOC15, RAS, ring mux, and XCP declarations. It is included by common GFX code and generation-specific GC implementations, and it exposes the common API used by scheduler, VM/TLB, RAS, KFD, PM, sysfs, and debugfs code.

## Risks and edge cases
Because this header defines shared layout, changes can affect many IP-version implementations. Queue limit constants must remain consistent with ring arrays and KIQ queue masks. Function pointer contracts need null checks in users. `amdgpu_gfx_create_bitmask()` shifts a 64-bit one and returns `u32`, so callers must not request unsupported widths. The structure carries many per-XCC arrays; incorrect indexing by logical XCC/XCP can corrupt state for partitioned devices.

## Test signals
Build coverage across multiple ASIC generations, queue map/unmap tests, XCP partition tests, cleaner shader tests, RAS query/injection paths, KIQ TLB invalidation, and debugfs/sysfs interface tests are the main validation signals for this header contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_gfx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_gfxhub.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_gfxhub.h

## Purpose
`amdgpu_gfxhub.h` defines the small function-table wrapper for graphics VM hub operations. The gfxhub is the GC-side VM/GART integration point used by generation-specific code to set up page-table registers, enable the GART, handle faults, query XGMI information, and preserve/restore mode2 state.

## Important APIs, types, and functions
The central type is `struct amdgpu_gfxhub_funcs`, with hooks for `get_fb_location`, `get_mc_fb_offset`, `setup_vm_pt_regs`, `gart_enable`, `gart_disable`, `set_fault_enable_default`, `init`, `get_xgmi_info`, `utcl2_harvest`, `mode2_save_regs`, `mode2_restore_regs`, and `halt`. `struct amdgpu_gfxhub` stores the installed function table.

## Control flow
The header has no executable logic. Common GMC/GART and ASIC initialization code call the function pointers after the specific gfxhub version has installed its implementation.

## State and persistence behavior
The only state represented here is a pointer to constant function tables. Hardware register state manipulated by the functions is runtime state and is restored by generation-specific mode2 save/restore helpers when supported.

## Dependencies and integration points
It depends on `struct amdgpu_device` and is consumed by GMC/GFX hub implementations. It integrates with VM page-table setup, GART lifecycle, XGMI discovery, UTCL2 harvest configuration, VM fault policy, and reset/halt flows.

## Risks and edge cases
Missing function pointers can break bring-up on an IP version if callers assume hooks are present. The table abstracts hardware-specific register layouts, so wrong implementations can misprogram VMID page-table bases or fault policy.

## Test signals
GART enable/disable, VM page-table register programming, VM fault enable defaults, XGMI information reporting, mode2 reset save/restore, and UTCL2 harvest tests validate this contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_gfxhub.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_gmc.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_gmc.c

## Purpose
`amdgpu_gmc.c` implements common Graphics Memory Controller helpers. It computes VRAM/GART/AGP/sysvm address apertures, allocates and initializes VMID0 PDB0 for XGMI/sysvm cases, writes CPU-side PTE/PDE entries, filters retry VM faults, delegates recoverable faults, registers GMC-family RAS blocks, allocates VM invalidation engines, flushes GPU TLBs, selects TMZ and no-retry defaults, reserves stolen/VGA VRAM, exposes memory partition sysfs, and initializes partition memory ranges.

## Important APIs, types, and functions
Address and page-table helpers include `amdgpu_gmc_vram_location()`, `amdgpu_gmc_sysvm_location()`, `amdgpu_gmc_gart_location()`, `amdgpu_gmc_agp_location()`, `amdgpu_gmc_set_agp_default()`, `amdgpu_gmc_pdb0_alloc()`, `amdgpu_gmc_init_pdb0()`, `amdgpu_gmc_get_pde_for_bo()`, `amdgpu_gmc_pd_addr()`, `amdgpu_gmc_set_pte_pde()`, `amdgpu_gmc_vram_mc2pa()`, and `amdgpu_gmc_vram_pa()`. Fault/TLB paths are `amdgpu_gmc_filter_faults()`, `amdgpu_gmc_filter_faults_remove()`, `amdgpu_gmc_handle_retry_fault()`, `amdgpu_gmc_allocate_vm_inv_eng()`, `amdgpu_gmc_flush_gpu_tlb()`, `amdgpu_gmc_flush_gpu_tlb_pasid()`, and `amdgpu_gmc_fw_reg_write_reg_wait()`. Partition and sysfs helpers include `amdgpu_gmc_sysfs_init()`, `amdgpu_gmc_get_nps_memranges()`, `amdgpu_gmc_request_memory_partition()`, `amdgpu_gmc_prepare_nps_mode_change()`, and `amdgpu_gmc_init_mem_ranges()`.

## Control flow
Memory placement starts with VRAM/FB location, then GART and optional AGP apertures are fit into the MC address space while avoiding the VA hole and 4 GiB crossing constraints. Sysvm mode for XGMI uses hive-wide VRAM at low addresses and puts GART after aligned hive VRAM. PDB0 allocation creates pinned, CPU-mapped VRAM storage; initialization writes PDE0 entries directly as PTEs for hive VRAM and one PDE pointing to the GART PTB.

Retry fault handling first filters repeated faults by `(addr,pasid)` and IH timestamp unless retry CAM is enabled. Hardware faults can be delegated from the main IH ring to a secondary/software ring, then `amdgpu_vm_handle_fault()` attempts page-table recovery and writes the retry-CAM doorbell when required. Fault filter removal marks an expiry timestamp so a future fault on an address can be reprocessed after the current IH stream checkpoint.

TLB flush paths either call ASIC MMIO hooks under the reset-domain read lock or submit a small SDMA/IB workaround job for GART VMID0 invalidation. PASID flush can use direct GMC hooks or emit KIQ invalidation packets and wait on a polling fence. VM invalidation engines are assigned to rings from a reserved bitmap while excluding firmware/MES/UMSCH rings and sharing engines for selected SDMA page rings.

NPS sysfs parses requested partition modes, stores requests either in XGMI hive state or device state, and tells users to reload the driver. During unload/init preparation, the code asks XGMI/PSP/ASIC hooks to apply requested NPS changes. Memory ranges come from discovery tables where possible, are validated for count, ordering, and overlap, and otherwise fall back to software partitioning.

## State and persistence behavior
The file mutates `adev->gmc` runtime fields: aperture starts/ends/sizes, real/visible VRAM limits, PDB0 BO and CPU mapping, retry fault ring/hash, partition request and supported-mode fields, memory partition array, XGMI view, TMZ/no-retry flags, and reset flags. NPS requests can be stored in hive memory until driver reload, but no disk persistence is used. Sysfs nodes represent live driver state and requested hardware changes.

## Dependencies and integration points
GMC depends on TTM BOs/resources, VM manager fields, GART, IH timestamp decoding, KIQ/MES rings, SDMA workaround submission, RAS subblocks (UMC, MMHUB, HDP, MCA, XGMI), XGMI hive management, PSP memory partition calls, Atom firmware VRAM info, ACPI NUMA memory info, reset-domain synchronization, and ASIC-specific `gmc_funcs`/`vmhub_funcs`.

## Risks and edge cases
Address placement must not overlap VRAM/GART/AGP or the VA hole. XGMI/sysvm PDB0 calculations depend on node segment size, physical node id, and page-table block size. Retry fault filtering is timestamp-sensitive and can suppress legitimate retries if expiry handling is wrong. TLB flushes during reset intentionally skip work; callers must tolerate that. KIQ-based PASID flush can timeout. Partition range validation currently has TODOs for holes and invalid hardware reports. Sysfs memory partition writes only request a mode change and require reload, which can surprise callers.

## Test signals
Validate VRAM/GART/AGP placement on APUs, dGPUs, SR-IOV, and XGMI hives; PDB0 allocation/init; VM fault retry recovery and duplicate filtering; retry CAM doorbell writes; TLB flush via MMIO, SDMA workaround, and KIQ; VM invalidation engine allocation across ring mixes; RAS init ordering; TMZ/no-retry defaults per IP version; sysfs NPS show/store; discovery and fallback memory-range construction; and VRAM checking fault injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_gmc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_gmc.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_gmc.h

## Purpose
`amdgpu_gmc.h` defines the shared GMC, VM hub, retry-fault, memory-partition, and aperture state used by AMDGPU memory-management code. It is the contract between common GMC helpers, VM code, ASIC-specific hub implementations, TTM/GART, RAS, XGMI, and partition-management logic.

## Important APIs, types, and functions
Important definitions include VA hole macros, retry fault ring/hash sizing, `enum amdgpu_memory_partition`, `struct amdgpu_gmc_fault`, `struct amdgpu_vmhub_funcs`, `struct amdgpu_vmhub`, `struct amdgpu_gmc_funcs`, `struct amdgpu_mem_partition_info`, `struct amdgpu_gmc_memrange`, `enum amdgpu_gart_placement`, and the large `struct amdgpu_gmc`. Macros dispatch VM PTE/PDE and TLB packet hooks through `gmc_funcs`. Function prototypes expose aperture placement, PDB0, VM fault filtering, TLB flushing, TMZ/noretry selection, sysfs, NPS partition, and VRAM info helpers.

## Control flow
The header does not execute by itself. It defines function pointers called by common code when flushing TLBs, emitting VM packets, querying/requesting memory partition mode, and checking reset-on-init requirements. Its inline `amdgpu_gmc_vram_full_visible()` and sign-extension macro are used by memory placement and user-visible reporting paths.

## State and persistence behavior
`struct amdgpu_gmc` stores all live MC state: CPU BAR aperture, GPU VRAM/GART/AGP apertures, VRAM sizes/type/vendor, firmware metadata, VM fault IRQ state, page-fault filter ring/hash, TMZ/no-retry flags, memory partition arrays, XGMI state, PDB0 BO, MALL fields, mode2 restore registers, and TLB flush quirk flags. This is runtime state reconstructed from firmware, discovery tables, module parameters, and hardware registers.

## Dependencies and integration points
The header depends on AMDGPU IRQ, XGMI, RAS, firmware, VM, BO, and ring types. It integrates with TTM/GART allocation, VM page-table programming, IH fault processing, RAS reporting, PSP/NBIO partition switching, ACPI NUMA discovery, and generation-specific GMC implementations.

## Risks and edge cases
The fault ring stores timestamps in 48-bit bitfields and relies on wrap-aware comparison. Aperture fields have subtly different CPU, local GPU, hive FB, GART, and AGP meanings. `AMDGPU_ALL_NPS_MASK` uses mode enum values directly as bit positions, while some validation code uses `mode - 1`; edits need care. Function pointer macros do not guard against null hooks. Mode2 register caches must stay aligned with actual hardware save/restore needs.

## Test signals
Compile coverage across GC/MMHUB generations, VM fault injection, XGMI hive bring-up, NPS mode query/request, PDB0/sysvm tests, TLB flush tests, RAS registration, visible VRAM reporting, and mode2 reset coverage are the primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_gmc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_gtt_mgr.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_gtt_mgr.c

## Purpose
`amdgpu_gtt_mgr.c` implements the TTM resource manager for AMDGPU GTT/GART address space. It tracks GART virtual address ranges with `drm_mm`, reports GTT total/used sysfs values, allocates ordinary TTM TT resources lazily or within a constrained aperture, supports standalone GART entry allocations for mappings not backed by a GTT BO, and recovers GART mappings after reset.

## Important APIs, types, and functions
The TTM callbacks are `amdgpu_gtt_mgr_new()`, `amdgpu_gtt_mgr_del()`, `amdgpu_gtt_mgr_intersects()`, `amdgpu_gtt_mgr_compatible()`, and `amdgpu_gtt_mgr_debug()` in `amdgpu_gtt_mgr_func`. Exported helpers are `amdgpu_gtt_mgr_has_gart_addr()`, `amdgpu_gtt_mgr_alloc_entries()`, `amdgpu_gtt_mgr_free_entries()`, `amdgpu_gtt_mgr_recover()`, `amdgpu_gtt_mgr_init()`, and `amdgpu_gtt_mgr_fini()`. Sysfs attributes are `mem_info_gtt_total` and `mem_info_gtt_used`.

## Control flow
Initialization sets up a TT resource manager, initializes `drm_mm` over the full GART page range, installs the manager for `TTM_PL_TT`, and marks it used. Allocation creates a `ttm_range_mgr_node`; if `place->lpfn` is nonzero it immediately reserves a GART range under `mgr->lock`, otherwise it creates a resource with `AMDGPU_BO_INVALID_OFFSET` so address allocation can be deferred. Free removes an allocated `drm_mm_node`, finalizes the TTM resource, and frees the node. Recovery walks allocated nodes and calls `amdgpu_ttm_recover_gart()` for normal BO-backed entries, skipping specially colored standalone entries.

## State and persistence behavior
State lives in `adev->mman.gtt_mgr`: a TTM manager, a `drm_mm` range allocator, and a spinlock. Standalone non-BO entries use a reserved color so recovery can skip them. Sysfs reads are live snapshots of manager size and usage. No state persists across driver reload.

## Dependencies and integration points
This file depends on DRM TTM resource-manager interfaces, `ttm_range_mgr_node`, `drm_mm`, AMDGPU memory manager state, TTM GART recovery, sysfs device attributes, and the GMC GART size. It is the GTT placement backend for BO validation/migration and non-BO physical mapping helpers.

## Risks and edge cases
Deferred resources without a GART address must be handled by callers before GPU access. Usage is checked before range insertion for non-temporary placements, so accounting and actual address exhaustion can fail separately. Standalone entries must be freed with the matching helper to avoid address leaks. `amdgpu_gtt_mgr_fini()` returns early if eviction fails, leaving cleanup incomplete by design.

## Test signals
Exercise BO allocation with and without `lpfn`, GTT exhaustion, standalone GART entry allocation/free, reset recovery, manager debug dump, sysfs total/used reporting, concurrent allocation under stress, and cleanup when resources remain busy.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_gtt_mgr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_hdp.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_hdp.c

## Purpose
`amdgpu_hdp.c` provides common Host Data Path cache flush/invalidate dispatch and HDP RAS registration. HDP flushes make GPU-visible writes coherent for host/device interactions, and generation-specific implementations can override both flush and invalidate operations.

## Important APIs, types, and functions
The file implements `amdgpu_hdp_ras_sw_init()`, `amdgpu_hdp_generic_flush()`, `amdgpu_hdp_invalidate()`, and `amdgpu_hdp_flush()`.

## Control flow
RAS initialization registers the HDP RAS block when `adev->hdp.ras` exists, names it `hdp`, sets the block/type fields, and records `adev->hdp.ras_if`. Generic flush either writes the remapped `KFD_MMIO_REMAP_HDP_MEM_FLUSH_CNTL` register directly and optionally reads NBIO memory size as a posting read, or emits the same write through a ring when an emit-wreg capable ring is supplied. Flush/invalidate dispatch first consults `adev->asic_funcs`, then falls back to `adev->hdp.funcs`.

## State and persistence behavior
Only runtime state is updated: HDP RAS registration pointers and hardware/cache state. Flush/invalidate operations do not keep software persistence beyond the command stream or MMIO write.

## Dependencies and integration points
The file depends on AMDGPU core device state, RAS registration, KFD remapped MMIO constants, NBIO posting-read hooks, ring `emit_wreg`, and ASIC/HDP function tables. It is used by IB submission, KFD, memory-management, and synchronization paths needing HDP coherency.

## Risks and edge cases
If no ring is supplied, the direct register path assumes MMIO is accessible and should not be used when hardware access is unsafe. Ring flush requires `emit_wreg`. Missing ASIC/HDP hooks make dispatch a no-op. Flush ordering relies on callers placing it at the correct points around command submission and memory updates.

## Test signals
Validate HDP RAS registration, direct and ring-emitted flush paths, posting-read behavior, generation-specific flush/invalidate hooks, KFD memory coherency, and suspend/reset cases where direct MMIO may be unavailable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_hdp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_hdp.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_hdp.h

## Purpose
`amdgpu_hdp.h` defines the common HDP state, HDP RAS wrapper, and function-table contract used by common and ASIC-specific HDP code.

## Important APIs, types, and functions
It defines `struct amdgpu_hdp_ras`, `struct amdgpu_hdp_funcs`, and `struct amdgpu_hdp`. Function pointers cover HDP flush, invalidate, clock-gating update/query, and register initialization. It declares the common RAS and flush/invalidate helper functions.

## Control flow
The header itself has no control flow. ASIC code installs `amdgpu_hdp_funcs`; common paths call through `amdgpu_hdp_flush()` and `amdgpu_hdp_invalidate()`.

## State and persistence behavior
`struct amdgpu_hdp` holds runtime RAS and function-table pointers. HDP register state is hardware state and is not persistent in this header.

## Dependencies and integration points
The header depends on AMDGPU RAS types and forward-declared device/ring types. It integrates with GMC RAS initialization, memory coherency paths, and IP-specific clock-gating/register initialization.

## Risks and edge cases
Null function tables must be handled by callers. Clock-gating and register-init hooks are hardware-specific and can affect coherency if installed incorrectly.

## Test signals
Build tests, HDP RAS init, flush/invalidate behavior across ASIC generations, and clock-gating state tests validate this contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_hdp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_hmm.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_hmm.c

## Purpose
`amdgpu_hmm.c` implements AMDGPU HMM/MMU interval notifier support for userptr BOs and KFD/HSA user memory. It blocks or evicts GPU users during CPU page-table invalidations and provides helpers to fault and validate CPU page ranges for GPU mappings.

## Important APIs, types, and functions
Key functions are `amdgpu_hmm_register()`, `amdgpu_hmm_unregister()`, `amdgpu_hmm_range_get_pages()`, `amdgpu_hmm_range_valid()`, `amdgpu_hmm_range_alloc()`, and `amdgpu_hmm_range_free()`. Internal invalidation callbacks are `amdgpu_hmm_invalidate_gfx()` and `amdgpu_hmm_invalidate_hsa()`, installed through `amdgpu_hmm_gfx_ops` or `amdgpu_hmm_hsa_ops`.

## Control flow
Registration chooses the HSA/KFD notifier path when `bo->kfd_bo` is present, otherwise the graphics path. Graphics invalidation refuses non-blockable ranges, locks `adev->notifier_lock`, records the notifier sequence, waits indefinitely for the BO reservation fences at bookkeeping usage, and unlocks. HSA invalidation delegates eviction to `amdgpu_amdkfd_evict_userptr()`. Range faulting allocates an HMM PFN array, fills `struct hmm_range`, faults the CPU pages in chunks no larger than `MAX_WALK_BYTE`, retries transient `-EBUSY` until a timeout, and restores the original PFN pointer before returning. Validation checks the saved notifier sequence with `mmu_interval_read_retry()`.

## State and persistence behavior
The notifier lives in `bo->notifier` and is tied to the current process `mm`. `amdgpu_hmm_range` holds a BO reference plus a transient PFN array and HMM range. All state is runtime and is removed on unregister/free.

## Dependencies and integration points
The file depends on Linux HMM and MMU interval notifier APIs, DMA reservation fences, AMDGPU BOs, KFD eviction hooks, DRM logging, and the device notifier lock. It integrates with userptr validation, VM update, KFD user queues, and command submission paths that need stable CPU page mappings.

## Risks and edge cases
Non-blockable invalidations return false and require the MMU notifier core to retry. Waiting with `MAX_SCHEDULE_TIMEOUT` can stall invalidation behind long GPU work. Large ranges are chunked, but PFN allocation still scales with total page count. `-EBUSY` maps to `-EAGAIN` after timeout. Callers must validate ranges after use and free PFN arrays to avoid stale mappings or leaks.

## Test signals
Userptr BO invalidation under GPU load, KFD userptr eviction, HMM range faulting for read-only and writable pages, large >2 GiB walks, notifier sequence invalidation races, `CONFIG_HMM_MIRROR` disabled builds, OOM paths, and page-table churn during command submission are relevant tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_hmm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_hmm.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_hmm.h

## Purpose
`amdgpu_hmm.h` declares AMDGPU HMM range state and notifier helpers, with fallback stubs when `CONFIG_HMM_MIRROR` is disabled.

## Important APIs, types, and functions
It defines `struct amdgpu_hmm_range`, which wraps `struct hmm_range` and an AMDGPU BO reference. It declares `amdgpu_hmm_range_get_pages()`, `amdgpu_hmm_range_valid()`, `amdgpu_hmm_range_alloc()`, `amdgpu_hmm_range_free()`, `amdgpu_hmm_register()`, and `amdgpu_hmm_unregister()`.

## Control flow
When HMM mirror support is enabled, callers use the implementation in `amdgpu_hmm.c`. When it is disabled, registration warns once and returns `-ENODEV`, range allocation returns NULL, validation returns false, and unregister/free are no-ops.

## State and persistence behavior
The represented state is transient: HMM PFN arrays, notifier sequence, and a BO reference. No persistent storage is involved.

## Dependencies and integration points
The header depends on Linux HMM, MMU notifier, workqueue/rwsem/interval tree headers, DRM logging for the fallback warning, and AMDGPU BO forward declarations. It is included by userptr and VM paths.

## Risks and edge cases
Callers must handle disabled-HMM stubs and NULL range allocation. The include guard name `__AMDGPU_MN_H__` is legacy-looking but functional. Code using HMM APIs must not assume `CONFIG_HMM_MIRROR` availability.

## Test signals
Build both with and without `CONFIG_HMM_MIRROR`, validate warning behavior in disabled builds, and run userptr/HMM tests in enabled builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_hmm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_i2c.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_i2c.c

## Purpose
`amdgpu_i2c.c` implements AMDGPU display I2C/DDC bus creation and routing for legacy AtomBIOS paths. It supports hardware AtomBIOS I2C when enabled, software bit-banging over GPIO/DDC registers, bus lookup, bus initialization/finalization, and external DDC/clock-data router mux selection.

## Important APIs, types, and functions
Exported functions are `amdgpu_i2c_create()`, `amdgpu_i2c_init()`, `amdgpu_i2c_fini()`, `amdgpu_i2c_lookup()`, `amdgpu_i2c_router_select_ddc_port()`, and `amdgpu_i2c_router_select_cd_port()`. Internal bit-bang callbacks include `amdgpu_i2c_pre_xfer()`, `amdgpu_i2c_post_xfer()`, `amdgpu_i2c_get_clock()`, `amdgpu_i2c_get_data()`, `amdgpu_i2c_set_clock()`, and `amdgpu_i2c_set_data()`.

## Control flow
`amdgpu_i2c_create()` rejects MM I2C buses if hardware I2C is disabled, allocates an `amdgpu_i2c_chan`, copies the AtomBIOS bus record, initializes the adapter and mutex, and either registers a hardware AtomBIOS algorithm adapter or a software `i2c-algo-bit` adapter. Bit-bang transfer setup locks the channel, switches pads into DDC mode, clears output values, sets pins to input, and masks GPIO pins for software control. Post-transfer unsets the masks and unlocks. Router selection reads and writes mux control registers over the selected router bus to choose DDC or clock/data paths.

## State and persistence behavior
State is held in allocated `amdgpu_i2c_chan` objects and `adev->i2c_bus[]`. Register changes configure GPIO/DDC pins and mux chips at runtime. `amdgpu_i2c_fini()` clears stored bus pointers; devm-managed adapters are removed with the DRM device lifecycle. There is no persistence.

## Dependencies and integration points
The file depends on Linux I2C core and bit-bang APIs, DRM EDID/display paths, AtomBIOS I2C helpers, AMDGPU register access macros, connector router metadata, and module parameters controlling hardware I2C. It feeds display connector probing and EDID/DDC access for non-DC or legacy paths.

## Risks and edge cases
GPIO register programming must leave pads unmasked after transfers. Hardware I2C availability depends on AtomBIOS records and module parameters. Router I2C failures are silently ignored by mux selection. `amdgpu_i2c_destroy()` is declared in the header but not implemented in this file, so ownership is likely devm/device-lifecycle based elsewhere. Bus finalization only nulls array entries.

## Test signals
EDID reads on bit-bang and hardware buses, module parameter combinations, Polaris OEM I2C init, router mux selection for DDC and clock/data, concurrent transfers on one bus, transfer timeout behavior, and device removal/reprobe are relevant tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_i2c.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_i2c.h

## Purpose
`amdgpu_i2c.h` declares the AMDGPU I2C bus creation, lifecycle, lookup, and router-selection helpers used by display/AtomBIOS code.

## Important APIs, types, and functions
The declared API is `amdgpu_i2c_create()`, `amdgpu_i2c_destroy()`, `amdgpu_i2c_init()`, `amdgpu_i2c_fini()`, `amdgpu_i2c_lookup()`, `amdgpu_i2c_router_select_ddc_port()`, and `amdgpu_i2c_router_select_cd_port()`.

## Control flow
The header has no executable logic. Display code calls these helpers to create adapters from BIOS bus records, initialize legacy bus lists, find existing buses by ID, and switch connector routers before DDC/clock-data transactions.

## State and persistence behavior
State is external in `struct amdgpu_i2c_chan`, connector router metadata, and `adev->i2c_bus[]`. No persistent state is defined here.

## Dependencies and integration points
It depends on AMDGPU display/connector and DRM device types. It integrates with AtomBIOS I2C, EDID probing, and connector router control.

## Risks and edge cases
The declaration of `amdgpu_i2c_destroy()` requires a matching definition elsewhere or dead code avoidance. Callers must handle NULL bus returns and router helpers that silently skip invalid router metadata.

## Test signals
Compile/link coverage, display probe EDID reads, router switching, and bus lookup tests validate the header contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_i2c.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_ib.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_ib.c

## Purpose
`amdgpu_ib.c` manages indirect buffer allocation, scheduling, testing, and debug reporting. IBs hold GPU command streams allocated from suballocator pools and are wrapped with VM flushes, HDP flush/invalidate, context-control packets, secure frame control, fences, conditional execution, and scheduler/job metadata when submitted to rings.

## Important APIs, types, and functions
Public functions are `amdgpu_ib_get()`, `amdgpu_ib_free()`, `amdgpu_ib_schedule()`, `amdgpu_ib_pool_init()`, `amdgpu_ib_pool_fini()`, `amdgpu_ib_ring_tests()`, and `amdgpu_debugfs_sa_init()`. The debugfs show helper dumps delayed, immediate, and direct SA pools.

## Control flow
IB allocation uses `amdgpu_sa_bo_new()` from the selected pool, maps CPU and GPU addresses, and defaults to `AMDGPU_IB_FLAG_EMIT_MEM_SYNC`. Scheduling validates ring readiness, VMID presence for VM jobs, and secure-submission support. It allocates ring space, determines context switch and pipeline sync requirements, emits VM flushes, begins the IB frame, inserts optional start packets, memory sync, high-priority wave limit, GFX shadow state, conditional execution, HDP flush, context-control, secure frame controls, each IB packet, HDP invalidate, user fence, shadow cleanup, hardware fence, optional end/switch-buffer/wave-limit cleanup, and commits the ring. Ring tests iterate ready rings with ASIC test hooks, use longer timeouts for SR-IOV/runtime/XGMI cases, and disable failed non-primary rings.

## State and persistence behavior
IB memory comes from runtime SA BO managers in `adev->ib_pools[]`. Scheduling updates ring write pointers, current context, fence metadata, VM fence packet offsets, job flags, and emitted hardware fences. Debugfs only reads live allocator state. There is no persistent storage.

## Dependencies and integration points
The file depends on SA BO managers, AMDGPU rings and ring funcs, DRM scheduler jobs/entities, VM flush logic, DMA fences, HDP coherency helpers, secure TMZ submission support, tracepoints, debugfs, and SR-IOV/XGMI runtime configuration. It is on the hot path for user command submission and kernel jobs.

## Risks and edge cases
`amdgpu_ib_schedule()` is dense and sensitive to ordering: VM flush must precede IBs, HDP flush/invalidate must bracket command execution, secure frame transitions must match IB flags, and fences must be emitted even with optional packets. `cond_exec` is patched unconditionally after optional initialization, so ring funcs must provide coherent behavior. Failure after ring allocation generally relies on pre-validation; error unwinding is limited. Primary GFX IB test failure disables acceleration.

## Test signals
IB pool init/fini, allocation failure injection, secure and mixed secure/nonsecure IB submissions, VM flush and context switch paths, user fence writes, high-priority ring wave limits, GFX shadow state, guilty context skip offsets, SR-IOV and XGMI ring tests, debugfs SA dump, and timeout-induced ring disabling are key tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_ib.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_ids.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_ids.c

## Purpose
`amdgpu_ids.c` manages global PASID allocation and per-VMHUB VMID assignment. PASIDs identify shared address spaces across GPU/IOMMU/driver, while VMIDs identify active GPU page-table contexts on each VM hub. The code delays PASID reuse behind fences and assigns/reuses VMIDs with LRU fairness, active-fence tracking, reserved IDs, TLB-flush decisions, and GDS/GWS/OA compatibility checks.

## Important APIs, types, and functions
PASID APIs are `amdgpu_pasid_alloc()`, `amdgpu_pasid_free()`, `amdgpu_pasid_free_delayed()`, and `amdgpu_pasid_mgr_cleanup()`. VMID APIs are `amdgpu_vmid_grab()`, `amdgpu_vmid_uses_reserved()`, `amdgpu_vmid_alloc_reserved()`, `amdgpu_vmid_free_reserved()`, `amdgpu_vmid_reset()`, `amdgpu_vmid_reset_all()`, `amdgpu_vmid_mgr_init()`, `amdgpu_vmid_mgr_fini()`, and `amdgpu_vmid_had_gpu_reset()`.

## Control flow
PASID allocation uses a global IRQ-safe xarray cyclic allocator from 1 to `(1 << bits) - 1`. Freeing removes the xarray entry under IRQ lock. Delayed free extracts a singleton reservation fence and either installs a fence callback to free the PASID after completion or blocks as an OOM/fallback path.

VMID grabbing locks the hub manager, first looks for an idle VMID or returns a fence to wait on for fairness. Reserved VMIDs are checked against owner, PD address, GDS/GWS/OA state, update sequence, and last flush fence; they may force a flush or return an active fence. Non-reserved VMIDs try to reuse a compatible active ID, otherwise use the idle ID. The selected ID records the job fence in its active sync, moves in the LRU list, updates flush/update state and resource bases, and writes `job->vmid` and `job->pasid`.

Initialization configures per-hub VMID counts based on GC version, MMHUB, and the KFD VMID boundary, skips VMID0, creates active sync objects, and populates the LRU. Finalization destroys locks, syncs, last flush fences, and PASID mapping fences.

## State and persistence behavior
Global PASID state is the xarray plus cyclic next value. Per-device VMID state lives in `adev->vm_manager.id_mgr[]`: mutex, LRU list, reserved flag, and `struct amdgpu_vmid` entries with owner, PD address, active sync, flush sequence, last flush fence, resource bases, PASID, and mapping fence. All state is in memory and reset on driver/module teardown.

## Dependencies and integration points
This file depends on Linux xarray, DMA fences, DMA reservation objects, AMDGPU VM update sequence helpers, ring fence contexts, sync objects, tracepoints, GPU reset counters, and KFD VMID partitioning. It feeds job submission and VM flush decisions consumed by `amdgpu_ib_schedule()`.

## Risks and edge cases
PASID allocation with `bits >= 32` would make `1U << bits` unsafe; callers must provide supported widths. Delayed PASID free can block under OOM. VMID reuse correctness depends on fence signaling, concurrent flush mode, PD/GDS compatibility, and update sequence tracking. Reserved VMIDs remove one ID from the LRU and can starve if active fences do not drain. Reset handling resets owner/resource state but not all fence fields.

## Test signals
PASID allocation/free wraparound, delayed free with active and already-signaled fences, OOM fallback, VMID reuse with and without concurrent flush, reserved VMID allocation/free, GDS/GWS/OA switching, GPU reset detection, KFD VMID boundary behavior, and multi-ring/multi-hub submission stress are useful tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_ids.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_ids.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_ids.h

## Purpose
`amdgpu_ids.h` declares PASID and VMID manager data structures and APIs for AMDGPU VM submission code.

## Important APIs, types, and functions
It defines `AMDGPU_NUM_VMID`, `struct amdgpu_vmid`, and `struct amdgpu_vmid_mgr`. `struct amdgpu_vmid` tracks LRU linkage, active sync, last flush fence, owner context, PD address, flushed update sequence, reset counter, GDS/GWS/OA ranges, PASID, and PASID mapping fence. It declares all PASID and VMID allocation, reset, and lifecycle helpers implemented in `amdgpu_ids.c`.

## Control flow
The header has no executable flow. VM/job submission code calls `amdgpu_vmid_grab()` before scheduling work, may reserve VMIDs for debugging/SPM, and uses reset helpers to force future flushes.

## State and persistence behavior
The structures describe volatile per-device and global runtime state. Sync/fence fields are used to delay reuse until GPU work is complete; no durable persistence exists.

## Dependencies and integration points
It depends on Linux mutex/list/fence types and `amdgpu_sync`. It integrates with VM manager, ring scheduling, KFD VMID partitioning, PASID/IOMMU address-space identity, and reset handling.

## Risks and edge cases
Callers must hold/use manager locks according to implementation expectations. Fence pointers require balanced references. The fixed 16-VMID array must match hardware VMID limits and KFD partitioning.

## Test signals
Compile coverage, VMID lifecycle tests, fence reference leak checks, PASID allocation tests, reserved VMID tests, and VM submission under reset validate the header contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_ids.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_ih.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_ih.c

## Purpose
`amdgpu_ih.c` implements common Interrupt Handler ring allocation, teardown, software IV injection, checkpoint waiting, ring processing, IV decoding, timestamp decoding, and ring naming. It is the common logic used by hardware IH rings and the software/delegated IH ring.

## Important APIs, types, and functions
The public API includes `amdgpu_ih_ring_init()`, `amdgpu_ih_ring_fini()`, `amdgpu_ih_ring_write()`, `amdgpu_ih_wait_on_checkpoint_process_ts()`, `amdgpu_ih_process()`, `amdgpu_ih_decode_iv_helper()`, `amdgpu_ih_decode_iv_ts_helper()`, and `amdgpu_ih_ring_name()`.

## Control flow
Ring initialization rounds the requested byte size to a power-of-two dword ring, sets masks and pointers, then either allocates one coherent DMA buffer containing ring plus shadow wptr/rptr storage or allocates a GTT BO plus writeback slots. Processing reads the hardware/software wptr, orders ring data with `rmb()`, dispatches up to `AMDGPU_IH_MAX_NUM_IVS` vectors through `amdgpu_irq_dispatch()`, writes the rptr unless overflow is set, wakes checkpoint waiters, and loops if the wptr advanced while processing. Overflow during SR-IOV runtime schedules FLR recovery work. Software write copies IV dwords, wraps the byte wptr, and commits it only if it would not equal rptr.

## State and persistence behavior
`struct amdgpu_ih_ring` stores ring allocation handles, CPU/GPU addresses, shadow pointers, enabled flag, rptr, processed timestamp, waitqueue, and overflow state. Ring content and pointers are runtime-only and are freed at driver teardown.

## Dependencies and integration points
The file depends on DMA coherent allocation, AMDGPU BO/writeback helpers, IRQ dispatch, reset domain scheduling, SR-IOV runtime state, and `amdgpu_ih_funcs` hardware callbacks for wptr/rptr handling and decoding. GMC retry-fault filtering uses IH timestamps and software ring delegation.

## Risks and edge cases
Ring-size rounding changes the requested size. The non-coherent teardown computes writeback offsets from `wptr_addr - gpu_addr`, which assumes those addresses share the same base; this is inherited driver behavior and needs caution. Software ring writes drop/skip commit on overflow and only warn for retry CAM. Processing caps IVs per pass but loops on new wptr changes, so interrupt storms and overflow handling are important.

## Test signals
IH allocation in bus-address and GTT/writeback modes, IV decode correctness, software ring delegation, checkpoint waits, overflow behavior, SR-IOV FLR scheduling, interrupt storm processing, teardown leak checks, and timestamp wrap comparisons are important tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_ih.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_ih.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_ih.h

## Purpose
`amdgpu_ih.h` declares AMDGPU Interrupt Handler ring sizes, register layout, ring state, timestamp comparison helpers, hardware callback table, and common IH helper prototypes.

## Important APIs, types, and functions
Important definitions are `AMDGPU_IH_MAX_NUM_IVS`, `IH_RING_SIZE`, `IH_SW_RING_SIZE`, `struct amdgpu_ih_regs`, `struct amdgpu_ih_ring`, timestamp macros `amdgpu_ih_ts_after()` and `amdgpu_ih_ts_after_or_equal()`, and `struct amdgpu_ih_funcs`. Macros dispatch `get_wptr`, `decode_iv`, `decode_iv_ts`, and `set_rptr` through `adev->irq.ih_funcs`.

## Control flow
The header has no standalone execution. Hardware-specific IH code installs `amdgpu_ih_funcs`, and common processing calls those callbacks while walking IH rings.

## State and persistence behavior
`struct amdgpu_ih_ring` represents volatile ring buffers, GPU/CPU pointer shadows, doorbell configuration, waitqueue state, processed timestamp, and overflow flag. No persistent state is defined.

## Dependencies and integration points
It integrates with AMDGPU IRQ dispatch, GMC fault timestamp filtering, retry CAM software ring use, reset handling, and hardware IH register programming.

## Risks and edge cases
The `amdgpu_ih_decode_iv` macro references `ih` as an implicit argument name, so call-site naming must match expected usage. Timestamp helpers assume 48-bit IH timestamps. Function pointer availability must be checked where optional, as done for `decode_iv_ts`.

## Test signals
Build coverage, IH callback installation, timestamp wrap tests, IV dispatch tests, software ring tests, and interrupt overflow tests validate this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_ih.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_imu.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_imu.h

## Purpose
`amdgpu_imu.h` defines the interface for the AMDGPU IMU block used by some graphics IPs for microcode loading, RLC RAM programming, reset status, compute partition switching, and MCM address lookup setup.

## Important APIs, types, and functions
It defines `enum imu_work_mode` with `DEBUG_MODE` and `MISSION_MODE`, `struct amdgpu_imu_funcs`, `struct imu_rlc_ram_golden`, the `IMU_RLC_RAM_GOLDEN_VALUE()` initializer macro, and `struct amdgpu_imu`.

## Control flow
There is no executable control flow. ASIC-specific code installs `amdgpu_imu_funcs`, then graphics initialization calls through those hooks to initialize/load microcode, set up/start IMU, program RLC RAM, wait for reset status, switch compute partitions, and initialize MCM address lookup tables.

## State and persistence behavior
`struct amdgpu_imu` stores a function-table pointer and runtime mode. Golden RLC RAM entries are static data used to program hardware registers. No persistent state is defined.

## Dependencies and integration points
The header depends on AMDGPU device and register-index conventions such as `*_HWIP` and `*_BASE_IDX`. It integrates with GFX initialization, RLC setup, partition switching, and reset flow for IP generations that use IMU.

## Risks and edge cases
Function pointers must be implemented for the target IP before use. Golden register macros depend on token-pasting register names matching SOC header definitions. Incorrect work mode or RLC RAM data can prevent graphics bring-up or partition switching.

## Test signals
Microcode init/load, IMU start, RLC RAM programming verification, compute partition switch tests, MCM address LUT init, and reset-status timeout tests validate this header contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_imu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_ioc32.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_ioc32.c

## Purpose
`amdgpu_ioc32.c` provides the 32-bit compatibility ioctl entry point for AMDGPU DRM on 64-bit kernels. It decides whether a compat ioctl should use generic DRM compatibility handling or the AMDGPU DRM ioctl path.

## Important APIs, types, and functions
The single exported function is `amdgpu_kms_compat_ioctl(struct file *filp, unsigned int cmd, unsigned long arg)`.

## Control flow
The function extracts the DRM ioctl number with `DRM_IOCTL_NR(cmd)`. Commands below `DRM_COMMAND_BASE` are core DRM ioctls and are delegated to `drm_compat_ioctl()`. Driver-private command numbers are passed directly to `amdgpu_drm_ioctl()`.

## State and persistence behavior
The file maintains no state. It forwards ioctl arguments to existing DRM/AMDGPU handlers.

## Dependencies and integration points
It depends on Linux compat support, DRM ioctl helpers, the AMDGPU UAPI command base, and `amdgpu_drm_ioctl()` from the driver. It is wired into the file operations for compat userspace.

## Risks and edge cases
Correct routing depends on the DRM command-number split. Driver-private AMDGPU ioctls must already be compat-safe or perform their own structure translation. Generic DRM ioctls rely on `drm_compat_ioctl()`.

## Test signals
Run 32-bit userspace ioctl smoke tests on a 64-bit kernel, including core DRM ioctls and AMDGPU private KMS/GEM/CS ioctls, and verify invalid command handling matches native ioctl behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_ioc32.c -->
