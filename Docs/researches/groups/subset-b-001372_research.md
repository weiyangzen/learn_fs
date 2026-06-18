# Research: subset-b-001372

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_device.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_device.c

## Purpose
`kfd_device.c` is the AMD KFD device lifecycle bridge between amdgpu/KGD and the HSA compute runtime. It probes whether an `amdgpu_device` has a supported KFD GFX target, initializes device-wide shared resources, creates one or more `kfd_node` objects for XCP/partitioned devices, starts queue managers, and exposes reset, suspend/resume, interrupt, eviction, scheduler, and debug entry points back to amdgpu.

## Important APIs, Types, and Functions
The main public entry points are `kgd2kfd_probe`, `kgd2kfd_device_init`, `kgd2kfd_device_exit`, `kgd2kfd_pre_reset`, `kgd2kfd_post_reset`, `kgd2kfd_suspend`, `kgd2kfd_resume`, `kgd2kfd_interrupt`, `kgd2kfd_quiesce_mm`, `kgd2kfd_resume_mm`, scheduler halt/unhalt helpers, and `kgd2kfd_vmfault_fast_path`. Internally, `kfd_device_info_init` and its SDMA/event helpers fill `kfd->device_info` from GC/SDMA IP versions. `kfd_cwsr_init` selects the correct CWSR trap image. `kfd_init_node` wires interrupts, DQM, GWS, topology, SMI, and resume. `kfd_gtt_sa_init`, `kfd_gtt_sa_allocate`, and `kfd_gtt_sa_free` implement a bitmap suballocator over one GTT backing allocation.

## Control Flow and State
Probe maps ASIC/IP versions to `kfd2kgd_calls` and `gfx_target_version`; unsupported or disallowed VFs return `NULL`. Device init validates PCI atomics when required, derives KFD VMID ranges, adjusts multi-XCP CPX VMID ownership, allocates a shared GTT slab, initializes doorbells, CWSR, and per-node queue managers, then marks `init_complete`. Reset/suspend paths bump the global `kfd_locked` reference so process open/restore paths stop queue execution while KFD is unsafe. Interrupts are filtered per node by `interrupt_is_wanted` and queued to the node IH workqueue. GTT allocator state persists in `kfd->gtt_sa_bitmap`; process activity is tracked with `compute_profile`.

## Dependencies and Integration Points
This file integrates with amdgpu firmware version queries, `amdgpu_xcp`, GPUVM eviction fences, topology, SMI events, KFD interrupts, DQM, SVM range sizing, doorbells, and debugfs. Risks concentrate around version tables, VMID partitioning assumptions, lock reference balance (`kfd_locked`, `kfd_dev_lock`), shared GTT exhaustion/fragmentation, and reset races while nodes are being cleaned up.

## Test Signals
Useful validation includes boot/probe on each supported GC family, multi-XCP CPX partition tests, suspend/resume and GPU reset while queues are active, PCI atomics rejection paths, doorbell/GTT allocation failure injection, IH routing with multiple nodes, debugfs HWS hang, eviction fence replay, and teardown waiting for `kfd_processes_count` to drain.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_device.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_device_queue_manager.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_device_queue_manager.c

## Purpose
`kfd_device_queue_manager.c` is the central KFD queue scheduler implementation. It hides the selected scheduling mode behind `device_queue_manager_ops`, manages user and kernel queues, VMID/PASID programming, doorbell assignment, SDMA allocation, MQD lifecycle, HWS runlists, MES queue submission, eviction/restore, queue suspension for debug, CRIU checkpoint support, and hung-queue recovery.

## Important APIs, Types, and Functions
`device_queue_manager_init` selects no-HWS, HWS, or HWS-no-oversubscription operations and installs ASIC-specific callbacks. Queue APIs are `create_queue_*`, `destroy_queue_*`, `update_queue`, `process_termination_*`, `evict_process_queues_*`, `restore_process_queues_*`, `suspend_queues`, `resume_queues`, and debug helpers. Hardware-resource helpers include `allocate_vmid`, `deallocate_vmid`, `allocate_hqd`, `allocate_sdma_queue`, `allocate_doorbell`, `program_sh_mem_settings`, `set_pasid_vmid_mapping`, and MES wrappers `add_queue_mes`/`remove_queue_mes`. HWS runlist control is driven by `map_queues_cpsch`, `unmap_queues_cpsch`, and `execute_queues_cpsch`.

## Control Flow and State
No-HWS mode directly allocates a VMID for the first queue in a process, reserves HQD/SDMA slots, creates an MQD, and loads it while the user mm is current. HWS mode registers process QPDs, builds runlists through the packet manager, and toggles `active_runlist`; MES mode bypasses packet runlists and calls `adev->mes.funcs`. Queue state persists in each QPD list plus DQM counters: `processes_count`, `active_queue_count`, `active_cp_queue_count`, `gws_queue_count`, `total_queue_count`, SDMA bitmaps, VMID PASID map, `sched_running`, `sched_halt`, and hang-detection buffers. Eviction is refcounted by `qpd->evicted`; restore updates page-table bases and records eviction duration.

## Dependencies and Integration Points
The manager depends on `kfd_mqd_manager`, `kfd_packet_manager`, `kfd_kernel_queue`, `kfd_debug`, amdgpu MES/reset domains, SDMA reset, MMU/GPUVM page directories, CWSR, and device-specific `kfd2kgd` callbacks. It is called by process queue manager, device lifecycle, interrupt handlers, debug ioctls, CRIU, and debugfs.

## Risks and Test Signals
High-risk areas are DQM lock ordering with reclaim/MMU notifiers, runlist fence timeouts, MES unrecoverable errors triggering GPU reset, queue counter drift, stale doorbell/SDMA IDs during CRIU restore, debug suspend/destroy races, and per-queue reset false positives. Test with max queue counts, mixed compute/SDMA/XGMI queues, MES and non-MES schedulers, eviction under memory pressure, queue update active/inactive transitions, bad-queue interrupt handling, HWS hang injection, CRIU restore with fixed IDs, and debug suspend/resume arrays with invalid IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_device_queue_manager.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_device_queue_manager.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_device_queue_manager.h

## Purpose
This header defines the DQM contract used by KFD device lifecycle, process queue management, debug, event reset paths, and ASIC-specific queue manager files. It is the abstraction boundary between generic queue scheduling logic and generation-specific SH_MEM/MQD/SDMA details.

## Important APIs and Types
`struct device_queue_manager_ops` contains the scheduler-facing vtable: create, destroy, update, register/unregister process, initialize/start/stop/uninitialize, halt/unhalt, kernel queue creation, cache policy, process termination, eviction/restore, wave-state, queue reset, and CRIU MQD checkpoint calls. `struct device_queue_manager_asic_ops` provides per-ASIC `update_qpd`, `set_cache_memory_policy`, `init_sdma_vm`, and `mqd_manager_init`. `struct device_queue_manager` stores scheduler state, queue lists, MQD managers, packet manager, counts, bitmaps, VMID/PASID mapping, fence memory, runlist state, debug trap VMID, hang/reset flags, wait tuning, destroy waitqueue, and per-queue hang-detection records.

## Control Flow and State
Callers interact through `dqm->ops`; generic code installs those ops in `device_queue_manager_init` based on scheduling policy and ASIC generation. ASIC init functions populate `dqm->asic_ops`. The header also exposes helpers for queue geometry, SDMA counts, debug trap VMID reservation, debug runlist unmap/remap, queue suspension/resume, queue snapshots, and queue lookup by doorbell. Inline helpers encode SH_MEM base extraction, enforce DQM locking with `memalloc_noreclaim_save`, read SDMA activity counters from userspace RPTR+8, and refresh IQ wait times.

## Dependencies and Integration Points
The header depends on `kfd_priv.h`, `kfd_mqd_manager.h`, Linux list/mutex/rwsem/mm APIs, and queue/process types. It is included by generic DQM, all generation-specific DQM files, device init, and debug paths.

## Risks and Test Signals
The biggest risk is ABI-like coupling: changing fields or operation semantics can silently break multiple scheduler modes. `dqm_lock` must be used where DQM state is mutated because it also suppresses reclaim-FS deadlock scenarios. Test signals include build coverage across all ASIC init files, lockdep under MMU notifier/reclaim pressure, queue snapshot correctness, SDMA counter user-copy fault handling, and debug suspend/resume behavior with MES and packet-manager schedulers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_device_queue_manager.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_device_queue_manager_cik.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_device_queue_manager_cik.c

## Purpose
This file supplies DQM ASIC callbacks for CIK/GFX7 devices. Its role is narrow: install the CIK MQD manager and implement CIK-specific SH_MEM cache policy programming and SDMA virtual-address setup.

## Important APIs and Functions
`device_queue_manager_init_cik` fills `device_queue_manager_asic_ops` with `set_cache_memory_policy_cik`, `update_qpd_cik`, `init_sdma_vm`, and `mqd_manager_init_cik`. `compute_sh_mem_bases_64bit` maps the process LDS/scratch/GPUVM top-address nybble into CIK `SH_MEM_BASES`. `set_cache_memory_policy_cik` validates the alternate aperture (APE1) against FSA64 encoding restrictions, programs APE1 base/limit, chooses default and APE1 memory types, preserves `PTR32`, sets unaligned alignment mode, and computes `sh_mem_bases`. `update_qpd_cik` is a no-op. `init_sdma_vm` encodes the shared-base nybble into the SDMA virtual-address register field.

## Control Flow and State
The generic DQM calls these callbacks during process registration, cache policy ioctls, and SDMA queue creation. The persistent state is stored in the QPD: `sh_mem_config`, `sh_mem_ape1_base`, `sh_mem_ape1_limit`, `sh_mem_bases`, and per-queue `sdma_vm_addr`. Invalid APE1 base/limit alignment causes the cache-policy callback to return false without programming the policy.

## Dependencies and Integration Points
The implementation depends on GFX7 and OSS register masks, `get_sh_mem_bases_nybble_64`, CIK MQD manager support, and DQM's later `program_sh_mem_settings`. It is selected for Kaveri and Hawaii by `device_queue_manager_init`.

## Risks and Test Signals
Risks are mostly address encoding errors: APE1 must stay user-mode, 64 KiB aligned, and representable in sign-extended base/limit registers. Incorrect memory type choices can alter cache coherency. Test with cache-policy ioctl variants, zero-sized APE1 disable, invalid base/limit rejection, SDMA queue creation, and CIK/Hawaii no-HWS queue loading.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_device_queue_manager_cik.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_device_queue_manager_v10.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_device_queue_manager_v10.c

## Purpose
This file provides GFX10 DQM ASIC callbacks. It adapts generic queue management to Navi-era SH_MEM register layout, MQD creation, and SDMA VM behavior.

## Important APIs and Functions
`device_queue_manager_init_v10` installs `set_cache_memory_policy_v10`, `update_qpd_v10`, `init_sdma_vm_v10`, and `mqd_manager_init_v10`. `compute_sh_mem_bases_64bit` derives shared and private SH_MEM base fields from `pdd->lds_base` and `pdd->scratch_base`. `set_cache_memory_policy_v10` programs unaligned SH_MEM mode, sets initial instruction prefetch to `3`, disables APE1 by zeroing base/limit, and records computed SH_MEM bases. `update_qpd_v10` is a no-op because cache policy initialization performs the needed QPD programming. `init_sdma_vm_v10` sets `sdma_vm_addr` to zero because SDMAv4+ no longer needs the older SDMA VM aperture programming used on CIK/VI.

## Control Flow and State
The callbacks are invoked by DQM process registration, cache-policy setup, and SDMA queue creation. Persistent state is in `qpd->sh_mem_config`, `qpd->sh_mem_bases`, APE1 base/limit fields, and queue properties. There is no per-process XNACK update in this file; GFX9 and GFX12.1 contain that extra handling.

## Dependencies and Integration Points
It depends on GFX10 register masks, `mqd_manager_init_v10`, and the aperture values initialized earlier by `kfd_flat_memory.c`. It is selected for GC versions at least 10.1.1 and below GFX11 in generic DQM init.

## Risks and Test Signals
Risks include wrong SH_MEM base extraction if aperture layout changes, accidental loss of instruction prefetch programming, and assumptions that SDMA VM address remains unused for all GFX10 SDMA variants. Validate with GFX10 queue creation, cache policy ioctls, SDMA and XGMI SDMA queues, runlist/MES scheduling, and shader flat-memory access to LDS/scratch apertures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_device_queue_manager_v10.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_device_queue_manager_v11.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_device_queue_manager_v11.c

## Purpose
This file supplies GFX11/SOC21 DQM ASIC callbacks. It is structurally similar to GFX10, with GFX11 register masks and MQD manager selection.

## Important APIs and Functions
`device_queue_manager_init_v11` installs the GFX11 callback table. `compute_sh_mem_bases_64bit` combines `lds_base >> 48` and `scratch_base >> 48` into `SH_MEM_BASES`. `set_cache_memory_policy_v11` sets unaligned alignment, enables initial instruction prefetch value `3`, disables APE1, computes SH_MEM bases, and returns success. `update_qpd_v11` is a no-op. `init_sdma_vm_v11` clears `sdma_vm_addr` because SDMAv4 onward does not require explicit SDMA aperture addressing.

## Control Flow and State
The generic queue manager calls these callbacks after process-device aperture initialization and before hardware programming. SH_MEM state is stored in QPD fields and later pushed by `program_sh_mem_settings` or conveyed through MES queue input. No local dynamic state is kept in this file.

## Dependencies and Integration Points
Dependencies are `gc_11_0_0` register masks, `soc21_enum`, `mqd_manager_init_v11`, and aperture setup from `kfd_flat_memory.c`. The generic DQM selects this implementation for GC versions from 11.0.0 up to but not including 12.0.0.

## Risks and Test Signals
The main risk is that GFX11-specific retry, prefetch, or aperture semantics diverge from the simple GFX10 pattern without this callback being updated. Test by creating compute and SDMA queues on each GFX11 IP variant, validating SH_MEM programming through debug dumps, running flat-memory LDS/scratch workloads, exercising MES scheduling, and confirming cache-policy ioctls do not require APE1 semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_device_queue_manager_v11.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_device_queue_manager_v12.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_device_queue_manager_v12.c

## Purpose
This file provides GFX12.0 DQM ASIC callbacks, continuing the SDMAv4+ and SH_MEM programming model for SOC24-class devices.

## Important APIs and Functions
`device_queue_manager_init_v12` installs `set_cache_memory_policy_v12`, `update_qpd_v12`, `init_sdma_vm_v12`, and `mqd_manager_init_v12`. `compute_sh_mem_bases_64bit` derives shared/private SH_MEM bases from process LDS and scratch apertures. `set_cache_memory_policy_v12` programs unaligned alignment, initial instruction prefetch value `3`, disables APE1, and computes the bases. `update_qpd_v12` is a no-op. `init_sdma_vm_v12` leaves `sdma_vm_addr` at zero.

## Control Flow and State
The generic DQM selects this implementation for GC versions at least 12.0.0 and below 12.1.0. It has no independent lifecycle; it only mutates QPD and queue-property fields consumed later by generic DQM, MQD managers, packet manager, or MES.

## Dependencies and Integration Points
It depends on `gc_12_0_0_sh_mask.h`, `soc24_enum.h`, `mqd_manager_init_v12`, and aperture values from `kfd_flat_memory.c`. It integrates with `program_sh_mem_settings`, queue creation, and cache policy ioctl paths.

## Risks and Test Signals
The main risks are subtle GC12 register-layout differences and the TODO elsewhere in device event interrupt selection that still maps GFX12.0 to v11 event handling. Validate with GFX12.0 hardware queue creation, MES and non-MES scheduler paths where available, SH_MEM register dumps, SDMA queue operation, flat-memory tests, and cache policy ioctl compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_device_queue_manager_v12.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_device_queue_manager_v12_1.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_device_queue_manager_v12_1.c

## Purpose
This file provides GFX12.1 DQM ASIC callbacks. Unlike GFX12.0, it updates both SH_MEM and VM context retry controls and uses a different private-base encoding.

## Important APIs and Functions
`device_queue_manager_init_v12_1` installs `update_qpd_v12_1`, `init_sdma_vm_v12_1`, and `mqd_manager_init_v12_1`; it intentionally does not set `set_cache_memory_policy`, so generic cache-policy calls become no-ops unless later support is added. `compute_sh_mem_bases_64bit` uses `lds_base >> 48` for shared base and `scratch_base >> 58` shifted into `PRIVATE_BASE`. `update_qpd_v12_1` copies `vm_cntx_cntl` from GFXHUB, initializes SH_MEM config with unaligned mode, prefetch, and F8 mode, and toggles `RETRY_DISABLE` plus `GCVM_CONTEXT0_CNTL__RETRY_PERMISSION_OR_INVALID_PAGE_FAULT` based on per-process XNACK. `init_sdma_vm_v12_1` sets SDMA VM address to zero.

## Control Flow and State
The generic DQM selects this for GC 12.1+. Process registration invokes `update_qpd_v12_1`; later queue creation and MES input consume `qpd->sh_mem_config`, `qpd->sh_mem_bases`, and `qpd->vm_cntx_cntl`. State is per QPD and reflects the owning process's XNACK setting.

## Dependencies and Integration Points
Dependencies include GFX12.1 register masks, `soc_v1_0_enum`, `mqd_manager_init_v12_1`, GFXHUB VM context defaults, and KFD XNACK support checks. It integrates tightly with MES queue input because `add_queue_mes` passes `vm_cntx_cntl`.

## Risks and Test Signals
Risk areas are missing cache-policy callback behavior, private-base bit encoding, and retry-permission synchronization between SH_MEM and VM context control. Test XNACK-enabled and disabled processes, VM fault retry behavior, MES queue submission, flat LDS/scratch addressing, F8-mode workloads, and SDMA queues.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_device_queue_manager_v12_1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_device_queue_manager_v9.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_device_queue_manager_v9.c

## Purpose
This file provides GFX9 DQM ASIC callbacks, including the first-generation SDMAv4 simplification and per-process retry/XNACK SH_MEM updates.

## Important APIs and Functions
`device_queue_manager_init_v9` installs GFX9 cache policy, QPD update, SDMA VM initialization, and MQD manager callbacks. `compute_sh_mem_bases_64bit` encodes independent LDS and scratch high bits into `SH_MEM_BASES`. `set_cache_memory_policy_v9` initializes SH_MEM config with unaligned mode, optional global retry disable when `noretry` is set, F8 mode for GC 9.4.3/9.4.4, high-precision MFMA mode for GC 9.5.0 when requested, disabled APE1, and computed bases. `update_qpd_v9` lazily initializes SH_MEM config if needed and then toggles retry disable for per-process XNACK support. `init_sdma_vm_v9` clears SDMA VM address.

## Control Flow and State
The generic DQM calls `update_qpd_v9` during process registration and `set_cache_memory_policy_v9` through cache-policy setup. State persists in QPD fields and must reflect process-level XNACK. GFX9.4.x and GFX9.5.0 add IP-version-specific config bits, so GC version gates are part of the persistent process state.

## Dependencies and Integration Points
It depends on Vega/GFX9 register masks, `mqd_manager_init_v9`, `KFD_SUPPORT_XNACK_PER_PROCESS`, process flags, and device `noretry`. The computed QPD state is programmed through generic DQM and consumed by both packet-manager and MES queue paths.

## Risks and Test Signals
Risk areas are retry-disable inversion, stale SH_MEM config after process XNACK changes, and GC 9.4/9.5 feature bits affecting workloads that rely on F8 or MFMA precision. Test XNACK on/off processes, GC 9.4.3/9.4.4 F8 workloads, GC 9.5 high-precision MFMA flag, SDMA queues, and VM fault retry/no-retry behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_device_queue_manager_v9.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_device_queue_manager_vi.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_device_queue_manager_vi.c

## Purpose
This file supplies VI/GFX8 DQM ASIC callbacks. It mirrors the CIK shape but uses GFX8 register encodings and memory-type values for SH_MEM policy.

## Important APIs and Functions
`device_queue_manager_init_vi` installs `set_cache_memory_policy_vi`, `update_qpd_vi`, `init_sdma_vm`, and `mqd_manager_init_vi`. `compute_sh_mem_bases_64bit` encodes the top address nybble into shared and private SH_MEM base fields. `set_cache_memory_policy_vi` validates and encodes APE1, chooses GFX8 memory types (`MTYPE_UC` for coherent, `MTYPE_NC` otherwise), programs unaligned alignment, disables APE1 by base>limit when size is zero, and computes SH_MEM bases from process apertures. `update_qpd_vi` is a no-op. `init_sdma_vm` encodes the shared-base nybble into the SDMA virtual address field.

## Control Flow and State
The file mutates QPD cache/aperture state during cache-policy setup and queue registration, and queue SDMA VM state during SDMA queue creation. Generic DQM later programs SH_MEM registers or includes values in MQDs/MES inputs. There is no independent persistent state outside QPD and queue properties.

## Dependencies and Integration Points
Dependencies include GFX8/OSS masks, VI MQD manager, and `get_sh_mem_bases_nybble_64`. The implementation is selected for Carrizo, Tonga, Fiji, Polaris, and related GFX8 ASICs.

## Risks and Test Signals
Risks are APE1 representability checks, memory-type mismatches that change cache coherency, and SDMA VM address encoding. Validate cache-policy ioctls with coherent/non-coherent default and alternate apertures, invalid APE1 alignment, SDMA queue operation, and GFX8 flat-memory addressing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_device_queue_manager_vi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_doorbell.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_doorbell.c

## Purpose
`kfd_doorbell.c` manages KFD doorbell apertures: MMIO-like write targets used by user and kernel queues to notify hardware of new write pointers. It handles device-wide kernel doorbells, per-process doorbell BOs, mmap of process slices, and doorbell bitmap reservation.

## Important APIs and Functions
`kfd_doorbell_process_slice` returns the per-process allocation size, using either KFD queue count or MES-provided sizing. `kfd_doorbell_init` allocates a kernel doorbell page and bitmap; `kfd_doorbell_fini` frees them. `kfd_doorbell_mmap` validates mmap size, locates process device data, obtains the process doorbell physical base, sets IO/PFNMAP VMA flags, makes it noncached, and remaps it. `kfd_get_kernel_doorbell`, `kfd_release_kernel_doorbell`, `write_kernel_doorbell`, and `write_kernel_doorbell64` manage kernel queue doorbells. `kfd_alloc_process_doorbells`, `kfd_get_process_doorbells`, and `kfd_free_process_doorbells` manage per-process allocations and bitmaps.

## Control Flow and State
Device init creates the kernel page. The first process-doorbell access lazily allocates `qpd->proc_doorbells` and `qpd->doorbell_bitmap`. SOC15 initialization masks non-CP doorbell ranges and mirrored offsets so compute queues do not collide with SDMA, IH, or VCN reservations. Queue creation later allocates IDs from this bitmap in DQM and converts them to BAR offsets with `amdgpu_doorbell_index_on_bar`.

## Dependencies and Integration Points
The file depends on amdgpu doorbell BO allocation, GEM doorbell domain, process device data, `/dev/kfd` mmap routing, and DQM doorbell ID assignment. MES changes slice sizing, while SOC15 changes reservation rules.

## Risks and Test Signals
Risks include off-by-one bitmap allocation, kernel doorbell leak, wrong 32-bit vs 64-bit doorbell alignment, mmap size mismatch, stale process BO after process teardown, and collision with reserved non-CP doorbells. Test per-process mmap, maximum queue count, MES/non-MES slices, SOC15 reserved ranges, kernel queue ring tests, 64-bit doorbell writes, and process cleanup with active queues.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_doorbell.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_events.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_events.c

## Purpose
`kfd_events.c` implements per-process KFD event objects, signal-page slots, wait semantics, CRIU event checkpoint/restore, event mmap, and signaling from interrupts, VM faults, GPU resets, poison, and process termination.

## Important APIs and Functions
Process lifecycle APIs are `kfd_event_init_process` and `kfd_event_free_process`. User-facing operations are `kfd_event_create`, `kfd_event_destroy`, `kfd_set_event`, `kfd_reset_event`, `kfd_wait_on_events`, `kfd_event_mmap`, and `kfd_kmap_event_page`. CRIU hooks are `kfd_criu_checkpoint_events` and `kfd_criu_restore_event`. Interrupt/fault signalers include `kfd_signal_event_interrupt`, `kfd_signal_hw_exception_event`, `kfd_signal_vm_fault_event`, `kfd_signal_reset_event`, `kfd_signal_poison_consumed_event`, and `kfd_signal_process_terminate_event`.

## Control Flow and State
Events live in `p->event_idr`; signal/debug events use low IDs that index a signal page, while nonsignal events use the upper ID range. Signal pages are either kernel-allocated or mapped from a user BO for CRIU restore. `set_event` updates `signaled`, handles auto-reset, increments `event_age`, marks waiters, and wakes the waitqueue. GPU interrupt signaling uses partial ID lookup with signal-page slot validation, then falls back to scanning signaled slots. Wait setup holds `event_mutex`, installs waiters under per-event spinlocks, then sleeps with interruptible timeout handling. Event destruction wakes waiters by nulling waiter event pointers and frees via RCU.

## Dependencies and Integration Points
The file integrates with `/dev/kfd` ioctls, process PASID lookup, GPUVM BO kernel mapping, DQM eviction on userptr VM faults, queue reset signaling, Linux wait queues, IDR, RCU, signals, and UAPI event data structures.

## Risks and Test Signals
Risks are lifetime races between waiters and destroyed events, partial-ID collisions, auto-reset rollback on restartable signals, signal-page size compatibility, CRIU restoring duplicate IDs, copy_to_user faults, and sending SIGSEGV/SIGBUS/SIGTERM when no handler event exists. Test signal/debug/memory/HW events, wait-all and wait-any, timeout and signal interruption, event destruction while waiting, partial mailbox interrupts, VM fault events, reset/ECC/poison paths, and CRIU checkpoint/restore with external event page handles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_events.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_events.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_events.h

## Purpose
This header defines the internal KFD event object and event constants shared by event implementation and interrupt processing. It also declares the interrupt signal entry point.

## Important APIs and Types
`struct kfd_event` contains the event ID, monotonically increasing `event_age`, signaled/auto-reset flags, event type, per-event spinlock, waiter queue, optional user signal address, type-specific memory or hardware exception data, and RCU head. ID allocation constants split signal events from nonsignal events: low IDs map to signal-page slots, while `KFD_FIRST_NONSIGNAL_EVENT_ID` through `KFD_LAST_NONSIGNAL_EVENT_ID` are used for memory/HW/etc. `UNSIGNALED_EVENT_SLOT` is the all-ones signal-page marker. Event type constants mirror HSA/UAPI values for signal, HW exception, debug, and memory events. `kfd_signal_event_interrupt` is exported to interrupt-processing code.

## Control Flow and State
The header itself holds no runtime state, but its layout defines concurrency requirements for `kfd_events.c`: event signaled state and wait queues are protected by `ev->lock`, process-level lookup and creation/destruction are protected by `p->event_mutex` or RCU, and event memory is freed asynchronously with `kfree_rcu`.

## Dependencies and Integration Points
It depends on Linux kernel ID/hash/list/wait primitives, `kfd_priv.h`, and `uapi/linux/kfd_ioctl.h`. It is consumed by the event implementation and interrupt paths that signal events from PASID and partial event IDs.

## Risks and Test Signals
Changing constants or field semantics affects userspace ABI behavior indirectly through event IDs, signal slot layout, and copied exception payloads. Validate with build coverage, event ID boundary tests, signal-page slot initialization, interrupt signaling from partial IDs, event-age wait semantics, and memory/HW exception data copying.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_events.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_flat_memory.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_flat_memory.c

## Purpose
`kfd_flat_memory.c` defines the per-process GPU virtual address apertures used for flat shader memory, LDS, scratch, GPUVM/SVM, CWSR trap memory, and kernel IB reservations. It is the address-layout companion to SH_MEM programming in the DQM ASIC files.

## Important APIs and Functions
The public entry point is `kfd_init_apertures`. Generation helpers are `kfd_init_apertures_vi`, `kfd_init_apertures_v9`, and `kfd_init_apertures_v12`. Macros define GPUVM, scratch, LDS, SVM user, CWSR, and IB bases/limits for the supported addressing models.

## Control Flow and State
`kfd_init_apertures` enumerates topology KFD devices, skips inaccessible devices via device cgroup checks, creates `kfd_process_device` data for each device, and fills that PDD's aperture fields. For 32-bit user processes all aperture bases/limits are zero because apertures are not supported. VI-style devices place LDS/scratch in fixed high noncanonical regions, reserve low SVM space for CWSR and IB, and set GPUVM from `SVM_USER_BASE` to device GPUVM size. GFX9 uses 48-bit LDS/scratch aperture bases and places CWSR at `AMDGPU_VA_RESERVED_TRAP_START`. GFX12+ uses shared/private aperture addresses from GMC and also puts CWSR on the opposite side of the VM hole.

## Dependencies and Integration Points
This file depends on topology enumeration, process-device creation, device cgroup permissions, amdgpu VM reserved-address helpers, GMC aperture fields, and KFD CWSR constants. DQM ASIC callbacks later consume `pdd->lds_base`, `scratch_base`, `gpuvm_base`, and QPD CWSR/IB bases to program SH_MEM and queue state.

## Risks and Test Signals
Risks are address-space overlap, invalid canonical/noncanonical placement, mismatched SH_MEM base extraction, 32-bit process behavior, and changes in GFX12 private/shared aperture layout. Test process creation across all accessible devices, cgroup-denied devices, 32-bit processes, VI/GFX9/GFX12 aperture values, SVM user allocation boundaries, CWSR trap placement, and flat-memory workloads targeting LDS, scratch, and GPUVM.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_flat_memory.c -->
