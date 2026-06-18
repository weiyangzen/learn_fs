# subset-b-003571 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/etnaviv/etnaviv_gem_submit.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/etnaviv/etnaviv_gem_submit.c

### Purpose
`etnaviv_gem_submit.c` implements the userspace command-stream submission ioctl for the Etnaviv DRM driver. It copies submit arguments from userspace, validates buffer objects, relocations, softpin addresses, sync fences, and performance-monitor requests, then creates a `drm_sched_job` for GPU execution.

### Important APIs, Types, And Functions
The central type is `struct etnaviv_gem_submit`, allocated by `submit_create()` and reference-counted through `etnaviv_submit_put()`. `etnaviv_ioctl_gem_submit()` is the UAPI entry point. Helper paths include `submit_lookup_objects()`, `submit_lock_objects()`, `submit_pin_objects()`, `submit_reloc()`, `submit_perfmon_validate()`, `submit_fence_sync()`, and `submit_attach_object_fences()`.

### Control Flow
The ioctl validates pipe, stream alignment, exec state, flags, MMU compatibility for softpin, and argument limits. It copies BO, relocation, PMR, and command stream arrays outside locks, reserves an output fence fd when requested, initializes a command buffer and scheduler job, looks up GEM handles under `file->table_lock`, optionally validates the command stream, imports an input sync file, pins objects into the submit MMU context, patches relocations, validates perfmon writes, locks reservations with wound/wait retry handling, adds implicit dependencies, pushes the job to the scheduler, and attaches the output fence to every BO reservation.

### State, Persistence, And Dependencies
State persists only through kernel objects: pinned `etnaviv_vram_mapping`s, GEM references, reservation fences, scheduler job state, xarray user fence id, and command-buffer storage. Cleanup unpins mappings, drops MMU contexts, removes user-fence xarray entries, wakes fence waiters, and releases copied PMR storage. Dependencies include GEM object lookup, dma-resv locking/fencing, sync_file, `drm_gpu_scheduler`, Etnaviv command buffers, MMU contexts, and perfmon validation.

### Integration Points
The ioctl feeds `etnaviv_sched_push_job()` and ultimately `etnaviv_gpu_submit()`. BO mapping is provided by `etnaviv_gem_mapping_get()`, relocation addresses by `mapping->iova`, and PMRs are consumed later by sync-point callbacks in `etnaviv_gpu.c`.

### Risks
Late output-fence allocation failure happens after the job has been handed to the scheduler, so cleanup must avoid `drm_sched_job_cleanup()` on that path. Softpin forbids relocations and requires MMUv2. Reservation locking must handle duplicate BOs and `-EDEADLK` correctly. PMR offsets are in mapped CPU memory and must not overwrite userspace sequence word zero. Any missing cleanup leaks GEM refs, active counts, or user fence ids.

### Test Signals
Useful signals include invalid handles, duplicate BO handles, invalid flags, unaligned stream and relocation offsets, softpin on MMUv1, softpin address mismatch, relocation outside object, input and output sync-fd behavior, `ETNA_SUBMIT_NO_IMPLICIT`, PMR validation failures, scheduler push failure, and fault injection around allocation and copy-from-user paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/etnaviv/etnaviv_gem_submit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/etnaviv/etnaviv_gpu.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/etnaviv/etnaviv_gpu.c

### Purpose
`etnaviv_gpu.c` is the main Vivante GPU device implementation for Etnaviv. It handles hardware identification, reset and initialization, command processor startup, fences, event slots, IRQ handling, runtime PM, thermal throttling, scheduler binding, debugfs state, hang recovery, and platform component registration.

### Important APIs, Types, And Functions
Public entry points include `etnaviv_gpu_get_param()`, `etnaviv_gpu_init()`, `etnaviv_gpu_debugfs()`, `etnaviv_gpu_submit()`, `etnaviv_gpu_recover_hang()`, `etnaviv_gpu_wait_fence_interruptible()`, `etnaviv_gpu_wait_obj_inactive()`, `etnaviv_gpu_wait_idle()`, and `etnaviv_gpu_start_fe()`. Internal machinery covers `etnaviv_hw_identify()`, `etnaviv_hw_specs()`, `etnaviv_hw_reset()`, `etnaviv_gpu_hw_init()`, event allocation/free, custom `dma_fence_ops`, sync-point perfmon workers, `irq_handler()`, runtime PM callbacks, and component bind/unbind.

### Control Flow
Probe maps registers, acquires reset, IRQs, and clocks, enables runtime PM, and registers as a component. Bind creates the scheduler, workqueue, fence context, and user-fence xarray. Initialization powers the device, deasserts reset, reads or overrides chip identity, selects security mode, resets hardware, initializes the global MMU, allocates the idle-loop command buffer, configures the linear window, initializes event completions, and programs hardware. Submit allocates one or three events, allocates a fence under `gpu->lock`, starts the FE idle loop when needed, queues PMR sync points and the user command buffer, and returns the fence.

### State, Persistence, And Dependencies
Persistent driver state lives in `struct etnaviv_gpu`: identity fields, GPU state enum, command buffer, event bitmap, fence counters, xarray user fence registry, current MMU context, hangcheck markers, clocks, reset, runtime-PM state, thermal frequency scale, and workqueue. Hardware state is register programming in the HI, FE, MMU, PM, and MC blocks. Dependencies include platform/component APIs, DRM scheduler and fences, Etnaviv MMU/cmdbuf/scheduler/perfmon/dump helpers, generated register headers, runtime PM, reset, clocks, and optional thermal cooling.

### Integration Points
The file connects submit-side scheduler jobs to hardware through `etnaviv_buffer_queue()`, signals fences from IRQ event bits, calls `drm_sched_fault()` on MMU exceptions, and cooperates with `etnaviv_sched.c` for hang recovery. Userspace observes it through get-param ioctls, fence waits, debugfs, and sync fd completion.

### Risks
Reset and clock/power sequencing is hardware-sensitive. Event allocation holds runtime-PM references per event and must free them on every IRQ or error path. MMU faults transition to `ETNA_GPU_STATE_FAULT` and rely on scheduler recovery. FE sync-point workers restart the FE after register sampling, so worker/IRQ ordering is delicate. Fence sequence accounting must handle out-of-order event bits. Identity quirks and HWDB overrides can change exposed UAPI capabilities.

### Test Signals
High-value tests are probe/remove with missing optional clocks, runtime suspend refusal while scheduler credits exist, get-param identity coverage, fence wait timeout and poll behavior, event exhaustion, PMR pre/post sampling, MMU fault interrupt handling, hangcheck forward-progress cases, reset recovery with active events, debugfs reads under runtime PM, and thermal cooling frequency-scale changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/etnaviv/etnaviv_gpu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/etnaviv/etnaviv_gpu.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/etnaviv/etnaviv_gpu.h

### Purpose
`etnaviv_gpu.h` declares the GPU-facing data model and public interfaces shared across Etnaviv submit, scheduler, MMU, perfmon, dump, and platform code.

### Important APIs, Types, And Functions
Key types are `struct etnaviv_chip_identity`, `enum etnaviv_sec_mode`, `struct etnaviv_event`, `enum etnaviv_gpu_state`, and `struct etnaviv_gpu`. Inline register helpers are `gpu_write()`, `gpu_read()`, `gpu_fix_power_address()`, `gpu_write_power()`, and `gpu_read_power()`. The header declares lifecycle, debugfs, submit, recovery, fence wait, object wait, idle wait, and FE-start APIs.

### Control Flow
The header does not implement control flow beyond MMIO helpers. `gpu_read()` performs an extra read for FE register ranges to work around inconsistent reads on some variants. Power-register helpers remap PM register offsets for old GC300 revisions before read/write.

### State, Persistence, And Dependencies
`struct etnaviv_gpu` persists all per-device mutable state: DRM device pointer, workqueue, scheduler, command buffer, events, fences, MMU context, hangcheck fields, MMIO base, IRQ, clocks, reset, and frequency scaling. It depends on Etnaviv command buffer, GEM, MMU, DRM driver structures, and generated common/state register definitions.

### Integration Points
Every Etnaviv GPU submodule includes this header to access identity, locking, events, fences, and MMIO accessors. The exported `etnaviv_gpu_driver` is the platform-driver symbol used by the wider DRM module.

### Risks
Incorrect register helper semantics affect every hardware path. The event count is fixed at `ETNA_NR_EVENTS` and must match hardware event vector usage. Shared structure fields are protected by different locks (`lock`, `sched_lock`, spinlocks), so new callers must respect existing lock ownership.

### Test Signals
Compile coverage across MMU, scheduler, submit, and perfmon catches declaration drift. Runtime signals include FE register reads on affected cores, GC300 power-register access, event bitmap bounds, and lockdep assertions around fields guarded by `gpu->lock`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/etnaviv/etnaviv_gpu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/etnaviv/etnaviv_hwdb.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/etnaviv/etnaviv_hwdb.c

### Purpose
`etnaviv_hwdb.c` provides a small built-in hardware database of known Vivante GPU identities. It corrects or fills chip feature and specification fields when hardware registers are incomplete, unreliable, or use wildcard product/customer/ECO ids.

### Important APIs, Types, And Functions
The file defines `etnaviv_chip_identities[]`, an array of `struct etnaviv_chip_identity` records, and exposes `etnaviv_fill_identity_from_hwdb()`.

### Control Flow
`etnaviv_fill_identity_from_hwdb()` compares the already-read model, revision, product id, customer id, and ECO id against each table entry. Product, customer, and ECO fields in the table may be `~0U` as wildcards. On match, it copies the full identity record into `gpu->identity`, restores the originally read id values for wildcarded fields, and reports success.

### State, Persistence, And Dependencies
There is no mutable state. The persistent effect is the replacement of `gpu->identity` during `etnaviv_hw_identify()` before raw feature-register fallback. The file depends only on `etnaviv_gpu.h`.

### Integration Points
`etnaviv_gpu.c` calls this after model/revision quirks and before reading feature registers. The resulting identity drives get-param UAPI responses, MMU/security decisions, clock-gating workarounds, scheduler behavior, perfmon domain availability, and userspace driver feature selection.

### Risks
Incorrect table entries can expose unsupported features or hide supported ones, causing userspace command streams or kernel workarounds to mismatch hardware. Wildcards are useful but increase the chance of overmatching. New cores require careful validation against register dumps and userspace expectations.

### Test Signals
Tests should compare known hardware register dumps against expected identity fields, cover wildcard preservation of product/customer/ECO ids, verify no unintended matches for close revisions, and validate userspace feature queries on each table-supported model.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/etnaviv/etnaviv_hwdb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/etnaviv/etnaviv_iommu.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/etnaviv/etnaviv_iommu.c

### Purpose
`etnaviv_iommu.c` implements MMUv1 context allocation and page-table operations for older Vivante GPUs. MMUv1 uses a single shared GPU address context because the hardware cannot switch contexts without a stop-the-world operation.

### Important APIs, Types, And Functions
The private `struct etnaviv_iommuv1_context` embeds `struct etnaviv_iommu_context` and owns a 2 MiB write-combined page table. The exported ops table `etnaviv_iommuv1_ops` supplies `.free`, `.map`, `.unmap`, `.dump_size`, `.dump`, and `.restore`. `etnaviv_iommuv1_context_alloc()` creates or references the shared context.

### Control Flow
Allocation is serialized under `global->lock`. If a shared context already exists, it returns a new kref. Otherwise it allocates the context, allocates the page table, fills all entries with the global bad-page DMA address, initializes `drm_mm` from `GPU_MEM_START` over the 2 MiB page-table aperture, and stores the shared context. Map/unmap accept only 4 KiB pages and write physical or bad-page addresses into the indexed page-table slot. Restore programs memory-base and page-table registers for FE, TX, PE, PEZ, and RA.

### State, Persistence, And Dependencies
State persists in the shared context page table, `drm_mm`, mapping list, global bad page, and `global->v1.shared_context`. Dependencies include DMA write-combined allocation, DRM memory manager, generated HI/MC register definitions, and GPU MMIO helpers.

### Integration Points
Generic MMU code in `etnaviv_mmu.c` invokes these ops. GPU initialization selects MMUv1 unless identity advertises MMUv2. Submit and command-buffer mapping code see a normal `etnaviv_iommu_context` even though MMUv1 is shared.

### Risks
Shared context semantics mean isolation is weaker than MMUv2 and stale mappings affect all clients. Only 4 KiB operations are supported. Address indexing assumes IOVAs are inside the `GPU_MEM_START` aperture. Restore must program every relevant MC page-table register or a pipeline can see inconsistent memory.

### Test Signals
Signals include shared-context refcount reuse, map/unmap of single pages, dump size/content, bad-page fill after unmap, command buffer below MMUv1 limits, and context restore on hardware with FE/TX/PE/RA memory access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/etnaviv/etnaviv_iommu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/etnaviv/etnaviv_iommu_v2.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/etnaviv/etnaviv_iommu_v2.c

### Purpose
`etnaviv_iommu_v2.c` implements MMUv2 page-table contexts. MMUv2 supports per-context master/second-level page tables, optional security-mode PTA loading, 4 GiB minus first-page virtual address space, and softpin-capable addressing.

### Important APIs, Types, And Functions
`struct etnaviv_iommuv2_context` embeds the generic context and owns a PTA id, one MTLB page, and lazily allocated STLB pages. Important functions are `etnaviv_iommuv2_context_alloc()`, `etnaviv_iommuv2_map()`, `etnaviv_iommuv2_unmap()`, `etnaviv_iommuv2_ensure_stlb()`, dump helpers, `etnaviv_iommuv2_restore_nonsec()`, `etnaviv_iommuv2_restore_sec()`, `etnaviv_iommuv2_get_mtlb_addr()`, and `etnaviv_iommuv2_get_pta_id()`.

### Control Flow
Allocation chooses a free PTA id under the global lock, allocates and initializes an MTLB page with exception entries, records the MTLB DMA in the global PTA array, and initializes the generic address manager. Mapping validates 4 KiB size, computes MTLB/STLB indexes, lazily allocates the STLB, encodes present/write/upper-physical bits, and writes the STLB entry. Unmap restores the exception entry. Nonsecure restore configures MMUv2 through a command buffer and enables `VIVS_MMUv2_CONTROL`; secure restore programs PTA and safe addresses, loads the selected PTA id through the FE, and enables secure MMU control.

### State, Persistence, And Dependencies
State persists in per-context MTLB/STLB DMA pages, PTA allocation bitmap, global PTA memory, bad page DMA, and GPU `mmu_context`. Dependencies include Etnaviv command-buffer helpers, generated MMUv2 registers, DMA WC allocation, vmalloc, and GPU security mode.

### Integration Points
Generic mapping and submit code call the ops through `etnaviv_mmu.c`. Softpin submit support is gated on `ETNAVIV_IOMMU_V2`. GPU reset/security logic in `etnaviv_gpu.c` selects secure versus nonsecure restore behavior.

### Risks
PTA id leaks or stale PTA entries can cross-wire contexts. Unmap assumes the STLB exists for mapped IOVA. Restore exits early if hardware MMU is already enabled, so reset paths must clear hardware state. Secure-mode register programming must agree with hardware security ownership.

### Test Signals
Tests should cover PTA exhaustion, map/unmap across multiple MTLB slots, write-protection bit encoding, 64-bit physical address encoding, dump sizing with sparse STLBs, nonsecure and secure restore paths, and softpin submissions at fixed addresses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/etnaviv/etnaviv_iommu_v2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/etnaviv/etnaviv_mmu.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/etnaviv/etnaviv_mmu.c

### Purpose
`etnaviv_mmu.c` is the version-independent MMU manager. It allocates GPU virtual address ranges, maps GEM scatterlists and command-buffer suballocations, reaps idle mappings under pressure, tracks flush sequence numbers, and owns global MMU state shared by one or more GPU devices.

### Important APIs, Types, And Functions
Key functions include `etnaviv_iommu_map_gem()`, `etnaviv_iommu_unmap_gem()`, `etnaviv_iommu_reap_mapping()`, `etnaviv_iommu_context_init()`, `etnaviv_iommu_context_put()`, `etnaviv_iommu_restore()`, `etnaviv_iommu_get_suballoc_va()`, `etnaviv_iommu_put_suballoc_va()`, `etnaviv_iommu_global_init()`, and `etnaviv_iommu_global_fini()`. Internal helpers map/unmap page ranges and manage `drm_mm` insertion.

### Control Flow
GEM mapping locks the object, then the context, optionally uses an MMUv1 contiguous-linear shortcut, inserts either an exact softpin node or a free IOVA, maps each DMA scatterlist segment page-by-page through version ops, records the mapping, and increments `flush_seq`. If space is unavailable, it scans idle mappings and reaps enough nodes before retry. Unmapping removes page-table entries and `drm_mm` nodes unless another thread already reaped the mapping. Context init selects v1/v2 allocation and maps the shared command-buffer suballocation. Global init detects MMU version from chip features, allocates the bad page and optional PTA, and enforces one global version.

### State, Persistence, And Dependencies
Persistent state includes `etnaviv_iommu_global`, bad page, optional PTA, per-context `drm_mm`, mapping lists, mapping use counts, and command-buffer mapping lifetime. Dependencies include GEM scatter-gather tables, DMA APIs, DRM memory manager scanning, cmdbuf suballocation, and MMUv1/MMUv2 ops.

### Integration Points
Submit pinning calls through GEM mapping helpers into this layer. GPU FE startup restores contexts through `etnaviv_iommu_restore()`. Dump code can query and copy page tables. The global MMU object is stored in `etnaviv_drm_private`.

### Risks
Mapping lifetime is subtle: active mappings are protected by `mapping->use`, while idle mappings can be reaped to satisfy address-space pressure. Exact softpin insertion must reject overlapping live mappings but may reap idle ones. MMUv1 linear shortcut bypasses page tables and depends on `memory_base`. Error unroll must not leave partial page-table entries.

### Test Signals
Signals include fragmented address-space pressure, idle mapping reaping, exact softpin overlap with live and idle mappings, scatterlist alignment failures, partial map failure unroll, MMUv1 contiguous shortcut, command-buffer mapping limits, global version mismatch across GPUs, and global refcount cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/etnaviv/etnaviv_mmu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/etnaviv/etnaviv_mmu.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/etnaviv/etnaviv_mmu.h

### Purpose
`etnaviv_mmu.h` declares the generic MMU abstraction used by Etnaviv GPU, GEM, command-buffer, and dump code.

### Important APIs, Types, And Functions
It defines protection bits, `enum etnaviv_iommu_version`, `struct etnaviv_iommu_ops`, `struct etnaviv_iommu_global`, and `struct etnaviv_iommu_context`. Public functions cover global init/fini, GEM map/unmap/reap, suballocation VA get/put, dump, context init/get/put, restore, v1/v2 context allocation, and MMUv2 MTLB/PTA helpers.

### Control Flow
The header itself only supplies `etnaviv_iommu_context_get()` as a kref increment. The ops table defines the dynamic dispatch used by `etnaviv_mmu.c` for version-specific page-table operations.

### State, Persistence, And Dependencies
`etnaviv_iommu_global` persists the selected MMU version, ops, use count, bad page, memory base, and either MMUv1 shared context or MMUv2 PTA storage. `etnaviv_iommu_context` persists the kref, global pointer, mapping lock/list, `drm_mm`, flush sequence, and command-buffer mapping.

### Integration Points
This header is the contract between MMUv1, MMUv2, generic MMU, GEM mapping, GPU startup, and command-buffer suballocation. Softpin and dump paths rely on fields exposed here.

### Risks
Ops implementations must keep `.map` and `.unmap` semantics consistent, especially return sizes from unmap. Global union fields are mutually exclusive by version; using the wrong member corrupts state. Context users must hold references while mappings or GPU state can still point at the context.

### Test Signals
Compile coverage with both MMU versions, kref lifetime tests, lockdep around context mapping locks, dump helpers, global version mismatch tests, and softpin builds validate this contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/etnaviv/etnaviv_mmu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/etnaviv/etnaviv_perfmon.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/etnaviv/etnaviv_perfmon.c

### Purpose
`etnaviv_perfmon.c` implements Etnaviv performance-monitor domain discovery, signal discovery, request validation, and counter sampling. It presents pipe-specific performance counters to userspace and services submit-time PMR requests.

### Important APIs, Types, And Functions
Private table types are `struct etnaviv_pm_signal`, `struct etnaviv_pm_domain`, and `struct etnaviv_pm_domain_meta`. Public functions are `etnaviv_pm_query_dom()`, `etnaviv_pm_query_sig()`, `etnaviv_pm_req_validate()`, and `etnaviv_perfmon_process()`. Sampling helpers include `perf_reg_read()`, `pipe_select()`, `pipe_perf_reg_read()`, `pipe_reg_read()`, and model-specific HI cycle readers.

### Control Flow
Static domain tables describe 3D, 2D, and VG pipe counters. Query functions count only domains whose pipe feature bits are present in `gpu->identity.features`, then iterate domain or signal names with sentinel iterator values. Submit validation indexes the domain metadata by exec state and checks domain/signal bounds. Processing picks the requested domain and signal, invokes the signal sampling callback, and writes the sampled value into the mapped PMR buffer at the requested offset.

### State, Persistence, And Dependencies
The tables are immutable. Sampling mutates hardware profile config registers and, for multi-pixel-pipe reads, temporarily changes `VIVS_HI_CLOCK_CONTROL_DEBUG_PIXEL_PIPE`. PMR results persist in userspace-provided GEM buffers. Dependencies include generated HI profile register constants, GPU identity, `gpu->lock` for pipe selection, and submit sync-point ordering.

### Integration Points
`etnaviv_gem_submit.c` validates PMRs and maps target BOs. `etnaviv_gpu.c` invokes `etnaviv_perfmon_process()` from pre/post sync-point events with clock gating temporarily disabled and writes sequence completion values for userspace.

### Risks
Domain metadata indexing assumes exec-state constants align with the `doms_meta` order. Pipe selection must be restored to pipe 0 to avoid GPU hangs. Sampling shares profile registers with hangcheck primitive-id reads, requiring lock coordination. Offset units must match submit-side validation.

### Test Signals
Tests should query domains/signals for GPUs with 3D-only, 2D-only, and mixed features; validate invalid domain/signal ids; sample multi-pipe counters under lockdep; verify PMR pre/post sequencing; and confirm sequence writes do not clobber counter values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/etnaviv/etnaviv_perfmon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/etnaviv/etnaviv_perfmon.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/etnaviv/etnaviv_perfmon.h

### Purpose
`etnaviv_perfmon.h` declares the perfmon request structure and public perfmon query/validation/processing APIs.

### Important APIs, Types, And Functions
`struct etnaviv_perfmon_request` stores PMR flags, domain, signal, userspace sequence value, mapped BO pointer, and offset. The header declares `etnaviv_pm_query_dom()`, `etnaviv_pm_query_sig()`, `etnaviv_pm_req_validate()`, and `etnaviv_perfmon_process()`.

### Control Flow
The header does not implement flow. Its structure is filled by submit validation and later consumed by GPU sync-point callbacks.

### State, Persistence, And Dependencies
PMR state persists inside `struct etnaviv_gem_submit` until scheduler free-job cleanup releases the submit. The header depends on DRM UAPI PM domain/signal structures and `struct etnaviv_gpu`.

### Integration Points
Submit code includes this header for PMR validation and storage; GPU code includes it for sync-point sampling; ioctl query handlers use the query APIs to enumerate available counters.

### Risks
`bo_vma` is a raw CPU mapping pointer, so lifetime must remain tied to the target GEM object and submit lifetime. Offsets must be interpreted consistently by validator and processor. Adding fields changes internal ABI between files but not the external UAPI.

### Test Signals
Compile checks across submit/GPU/perfmon files, PMR lifetime under submit cleanup, invalid offset rejection, and query ioctl coverage validate the header contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/etnaviv/etnaviv_perfmon.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/etnaviv/etnaviv_sched.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/etnaviv/etnaviv_sched.c

### Purpose
`etnaviv_sched.c` adapts Etnaviv submits to the DRM GPU scheduler. It runs jobs on hardware, allocates userspace-visible fence ids, detects hangs, captures dumps, recovers the GPU, resubmits jobs, and frees submit references when scheduler jobs retire.

### Important APIs, Types, And Functions
Public APIs are `etnaviv_sched_init()`, `etnaviv_sched_fini()`, and `etnaviv_sched_push_job()`. Scheduler backend callbacks are `etnaviv_sched_run_job()`, `etnaviv_sched_timedout_job()`, and `etnaviv_sched_free_job()`. Module parameters `job_hang_limit` and `hw_job_limit` tune DRM scheduler behavior.

### Control Flow
Push holds `gpu->sched_lock`, allocates a cyclic xarray fence id, arms the DRM scheduler job, stores the scheduler finished fence in both the submit and user-fence xarray, takes a submit reference for scheduler ownership, and pushes the job to its entity. Run-job skips jobs whose scheduler fence already has an error, otherwise calls `etnaviv_gpu_submit()`. Timeout checks for spurious already-signaled fences, then compares FE DMA address, completed fence, and 3D primitive id to detect forward progress. A real hang stops the scheduler, increases karma, dumps state, resets the GPU, resubmits jobs, and restarts scheduling.

### State, Persistence, And Dependencies
Scheduler state is in `gpu->sched`, `gpu->sched_lock`, submit `sched_job`, user-fence xarray entries, and hangcheck fields in `struct etnaviv_gpu`. Dependencies include DRM scheduler APIs, DMA fences, generated profile registers, Etnaviv dump, GPU submit/recover, and GEM submit refcounting.

### Integration Points
`etnaviv_gem_submit.c` calls `etnaviv_sched_push_job()`. `etnaviv_gpu.c` provides hardware submission and recovery. User fence waits look up xarray ids allocated here.

### Risks
Fence id allocation and scheduler fence sequence ordering require `sched_lock`. If hardware submission returns `NULL`, scheduler behavior depends on DRM handling of run-job failure. Hangcheck must avoid false positives while FE or primitive id advances. Timeout sampling of profile registers must coordinate with perfmon.

### Test Signals
Tests should cover push failure paths, cyclic fence-id allocation, bad dependency skipping, timeout when fence already signaled, forward-progress deferral, real hang reset and resubmit, scheduler fini with queued jobs, and module parameter boundary values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/etnaviv/etnaviv_sched.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/etnaviv/etnaviv_sched.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/etnaviv/etnaviv_sched.h

### Purpose
`etnaviv_sched.h` declares the small scheduler interface between submit code and GPU scheduler implementation.

### Important APIs, Types, And Functions
The inline `to_etnaviv_submit()` converts a `struct drm_sched_job` to its containing `struct etnaviv_gem_submit`. The header declares `etnaviv_sched_init()`, `etnaviv_sched_fini()`, and `etnaviv_sched_push_job()`.

### Control Flow
No standalone control flow exists beyond the container conversion helper.

### State, Persistence, And Dependencies
The header depends on `<drm/gpu_scheduler.h>` and forward declarations for Etnaviv GPU/submit types. It encodes the structural invariant that `struct etnaviv_gem_submit` contains a member named `sched_job`.

### Integration Points
Submit, GPU bind/unbind, and scheduler implementation all include this header. It is the narrow public surface for initializing the scheduler and enqueueing jobs.

### Risks
Changing the submit structure member name or embedding pattern breaks `to_etnaviv_submit()`. The header must stay minimal to avoid circular includes between submit, GPU, and scheduler files.

### Test Signals
Compile coverage is the primary signal. Runtime validation comes from successful submit enqueue, scheduler timeout, and free-job callbacks using the conversion helper.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/etnaviv/etnaviv_sched.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/etnaviv/state.xml.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/etnaviv/state.xml.h

### Purpose
`state.xml.h` is an autogenerated Vivante GPU register-definition header from rules-ng-ng XML files. It provides address constants and mask/shift/value helpers for frontend, shader, texture, raster, pixel, GL, NFE, and related state blocks.

### Important APIs, Types, And Functions
The file is macro-only. Representative families include `FE_DATA_TYPE_*`, `VIVS_FE_*` command/DMA/vertex-stream registers, `VIVS_GL_*` stall and cache state, `VIVS_NFE_*` new frontend stream and attribute registers, and `VIVS_WD_*` definitions. Field helpers follow the pattern `NAME__MASK`, `NAME__SHIFT`, and `NAME(x)`.

### Control Flow
There is no executable control flow. The macros are consumed by command construction, validation, debug, and hardware programming code elsewhere.

### State, Persistence, And Dependencies
The persistent contract is the numeric register map and bit layout. The file is generated from multiple XML sources and includes a permissive generated-header license notice. It has no runtime dependencies.

### Integration Points
Etnaviv GPU, command-buffer, scheduler, perfmon, and userspace-facing validation code include this register vocabulary. `etnaviv_gpu_start_fe()` uses FE command-control constants from this header.

### Risks
Manual edits would be overwritten or drift from XML truth. Incorrect masks or addresses can cause invalid command streams, GPU hangs, or misreported debug state. Duplicate or cut-down definitions must remain compatible with included generated headers.

### Test Signals
Signals include successful driver build, command-stream validation against known registers, hardware smoke tests for FE startup and DMA debug reads, and regeneration diffs from the source XML.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/etnaviv/state.xml.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/etnaviv/state_3d.xml.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/etnaviv/state_3d.xml.h

### Purpose
`state_3d.xml.h` is a cut-down generated register header for selected 3D, shader, compute, texture-status, and NTE registers used by the Etnaviv driver.

### Important APIs, Types, And Functions
It defines macro constants for CL compute configuration/workgroup registers, PS/VS shader input/output/uniform/instruction registers, shader config bits, texture-status flush, and NTE descriptor flush fields. It also uses mask/shift/value helper macros such as `VIVS_CL_CONFIG_DIMENSIONS(x)` and `VIVS_PS_INPUT_COUNT_COUNT(x)`.

### Control Flow
There is no executable flow. The macros are compile-time data for command-buffer programming and validation.

### State, Persistence, And Dependencies
The file has no mutable state. Its persistent role is to keep numeric state addresses synchronized with the generated XML register database. It is intentionally smaller than the full upstream generated file.

### Integration Points
3D command emission, cache flush, shader setup, and validation code can use these definitions without including a larger generated header. It complements `state.xml.h` and `state_hi.xml.h`.

### Risks
Because it is cut down, adding code that needs omitted 3D registers requires regenerating or extending the header carefully. Duplicated CL config definitions must stay identical. Wrong shader-state constants can cause hard-to-debug GPU hangs.

### Test Signals
Build coverage, shader command-stream tests, cache-flush tests, compute command tests on supported cores, and comparison with regenerated XML output are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/etnaviv/state_3d.xml.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/etnaviv/state_blt.xml.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/etnaviv/state_blt.xml.h

### Purpose
`state_blt.xml.h` is a cut-down generated header for Vivante BLT engine registers.

### Important APIs, Types, And Functions
It defines `VIVS_BLT_SET_COMMAND`, `VIVS_BLT_ENABLE`, and `VIVS_BLT_ENABLE_ENABLE`. There are no types or functions.

### Control Flow
There is no executable control flow; these constants are used by code that emits or validates BLT commands.

### State, Persistence, And Dependencies
The persistent contract is the BLT register address and enable bit. The file is generated from XML metadata and carries the generated-header license notice.

### Integration Points
It integrates with Etnaviv command and state handling for GPUs exposing BLT capabilities, and with broader generated register headers that describe HI, FE, and 3D state.

### Risks
The header is intentionally minimal. Code that assumes a complete BLT register map will fail to compile or may be tempted to duplicate constants elsewhere. Incorrect enable-bit values could activate the wrong hardware state.

### Test Signals
Builds that include BLT paths, BLT command validation, hardware BLT smoke tests, and regeneration comparisons validate this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/etnaviv/state_blt.xml.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/etnaviv/state_hi.xml.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/etnaviv/state_hi.xml.h

### Purpose
`state_hi.xml.h` is the generated register map for high-level Vivante GPU control blocks: HI identity/clock/interrupt/idle registers, PM power controls, MMUv2 registers, MC memory/profile registers, and related blocks.

### Important APIs, Types, And Functions
The file is macro-only. Major families include `VIVS_HI_CLOCK_CONTROL`, `VIVS_HI_IDLE_STATE`, `VIVS_HI_INTR_ACKNOWLEDGE`, chip identity/spec registers, `VIVS_PM_*`, `VIVS_MMUv2_*`, `VIVS_MC_*`, profile config selectors, and MMU exception reason constants. It uses generated mask/shift/value helpers throughout.

### Control Flow
There is no runtime flow. Hardware-control code reads and writes these numeric constants through `gpu_read()`, `gpu_write()`, and power-register helpers.

### State, Persistence, And Dependencies
The file persists the register ABI expected by the kernel driver and hardware. It has no mutable state and is generated from XML sources.

### Integration Points
`etnaviv_gpu.c` uses it for reset, identity, clock, interrupt, idle, power, and security setup. `etnaviv_iommu.c` and `etnaviv_iommu_v2.c` use MMU/MC registers. `etnaviv_perfmon.c` uses MC profile selectors. Debugfs and hangcheck paths depend on these definitions.

### Risks
Bad constants directly affect reset, MMU fault reporting, interrupt handling, and performance counters. Some registers are model/revision-sensitive, so callers still need identity guards. Generated files should not be manually edited.

### Test Signals
Driver build, reset/init on multiple GC revisions, MMU fault dumps, IRQ event completion, perfmon counter sampling, runtime suspend/resume, and XML regeneration diffs validate this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/etnaviv/state_hi.xml.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/exynos/Kconfig -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/exynos/Kconfig

### Purpose
`drivers/gpu/drm/exynos/Kconfig` defines the build-time configuration menu for the Samsung Exynos DRM driver, including core dependencies, CRTC blocks, encoders/bridges, and image-processing subdrivers.

### Important APIs, Types, And Functions
This is Kconfig metadata, not C code. Key symbols are `DRM_EXYNOS`, `DRM_EXYNOS_FIMD`, `DRM_EXYNOS5433_DECON`, `DRM_EXYNOS7_DECON`, `DRM_EXYNOS_MIXER`, `DRM_EXYNOS_VIDI`, `DRM_EXYNOS_DPI`, `DRM_EXYNOS_DSI`, `DRM_EXYNOS_DP`, `DRM_EXYNOS_HDMI`, `DRM_EXYNOS_MIC`, and G2D/IPP/FIMC/ROTATOR/SCALER/GSC options.

### Control Flow
Kconfig dependencies gate symbol visibility and selection. `DRM_EXYNOS` depends on OF, DRM, COMMON_CLK, an allowed architecture or compile-test, and MMU, then selects shared DRM helpers. Subsymbols are available only inside `if DRM_EXYNOS` and select helper libraries such as panel, MIPI DSI, Analogix DP, DP helper, CEC, or IPP support.

### State, Persistence, And Dependencies
The persistent output is the kernel `.config`, which controls object inclusion in the Makefile and feature availability. Dependencies encode architecture conflicts, legacy framebuffer exclusions, and helper-library requirements.

### Integration Points
The Makefile consumes these symbols to add objects to `exynosdrm-y`. Platform drivers in this subset depend on `DRM_EXYNOS5433_DECON`, `DRM_EXYNOS7_DECON`, and `DRM_EXYNOS_DP`.

### Risks
Missing selects produce link failures; overbroad selects increase build footprint. Incorrect `depends on` can allow broken combinations with legacy framebuffer drivers or without required display helpers.

### Test Signals
Signals include `allyesconfig`, `allmodconfig`, Exynos defconfigs, `COMPILE_TEST` builds on non-Exynos architectures, and configs toggling individual CRTC/encoder symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/exynos/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/exynos/Makefile -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/exynos/Makefile

### Purpose
`drivers/gpu/drm/exynos/Makefile` maps Exynos DRM Kconfig symbols to the objects linked into the `exynosdrm` module or built-in driver.

### Important APIs, Types, And Functions
It defines `exynosdrm-y` for core objects: driver, CRTC, framebuffer, GEM, plane, and DMA support. Conditional object additions include fbdev emulation, FIMD, Exynos5433 DECON, Exynos7 DECON, DPI, DSI, DP, mixer, HDMI, VIDI, G2D, IPP, FIMC, rotator, scaler, GSC, and MIC. `obj-$(CONFIG_DRM_EXYNOS) += exynosdrm.o` emits the final target.

### Control Flow
Kbuild concatenates `exynosdrm-y` and enabled `exynosdrm-$(CONFIG_*)` fragments when `CONFIG_DRM_EXYNOS` is set. Disabled symbols contribute no object files.

### State, Persistence, And Dependencies
There is no runtime state. Persistent behavior is build composition determined by `.config` and Kbuild ordering.

### Integration Points
The Kconfig file defines the symbols used here. Platform driver declarations in Exynos source files are linked only when their symbols append the corresponding object.

### Risks
Missing an object causes unresolved symbols or absent platform support. Adding an object under the wrong symbol can produce link errors when dependencies are absent. Ordering matters when initialization arrays or shared symbols have implicit expectations.

### Test Signals
Builds for each individual Exynos subdriver, allmodconfig, built-in and module builds, and link checks for `exynosdrm.o` validate this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/exynos/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/exynos/exynos5433_drm_decon.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/exynos/exynos5433_drm_decon.c

### Purpose
`exynos5433_drm_decon.c` implements the Exynos5433 DECON display controller CRTC backend for DRM/KMS. It programs display timing, window planes, blending, triggers, vblank handling, runtime PM clocks, DMA registration, and component binding for LCD/I80 and HDMI-style outputs.

### Important APIs, Types, And Functions
`struct decon_context` stores device, DRM, DMA, CRTC, five planes, register base, sysreg, clocks, IRQs, output flags, vblank lock, and frame id. Important functions include vblank enable/disable, `decon_get_frame_count()`, `decon_setup_trigger()`, `decon_commit()`, blending/pixfmt helpers, `decon_update_plane()`, `decon_atomic_flush()`, `decon_swreset()`, atomic enable/disable, IRQ handlers, bind/unbind, runtime PM suspend/resume, IRQ configuration, probe, and remove.

### Control Flow
Probe allocates context, reads match output flags, gets ten clocks, maps registers, requests optional `vsync`, `lcd_sys`, and `te` IRQs with auto-enable disabled, resolves sysreg for hardware-trigger mode, enables runtime PM, and registers a component. Bind initializes planes from `first_win`, creates an Exynos CRTC with DECON ops, clears channels, and registers DMA. Atomic enable resumes PM, enables pipe clocks, resets DECON, and commits mode registers. Plane updates program coordinates, DMA addresses, pitch/offset, alpha, pixel format, burst length, and enable bits under shadow protection. Atomic flush unprotects, triggers update, records frame id, and handles pending events.

### State, Persistence, And Dependencies
State persists in DECON registers, clock/runtime-PM state, vblank IRQ enablement, frame counter tracking, plane states, and DMA/IOMMU registration. Dependencies include Exynos DRM CRTC/plane/fb helpers, DECON5433 register definitions, syscon/regmap for trigger mux, DRM blend/fourcc/vblank helpers, platform IRQs, and clocks.

### Integration Points
This file is selected by `DRM_EXYNOS5433_DECON` and links into `exynosdrm`. It exposes an `exynos5433_decon_driver` platform driver and registers with the DRM component framework. HDMI output changes timing programming and skips window 0 by setting `first_win`.

### Risks
Frame count adjustment differs for I80, RGB, and interlaced HDMI; incorrect accounting causes missed or duplicate vblanks. Small buffers need 8-word bursts to avoid tearing/IOMMU faults. IRQ availability determines mode validity. TE/hardware trigger paths depend on sysreg and IRQ masking. Atomic disable must disable windows before connector suspend to avoid scanout from destroyed buffers.

### Test Signals
Tests should cover LCD, I80 command mode, TE IRQ mode, HDMI/interlaced output, vblank enable/disable, missing IRQ mode rejection, plane blending formats, cursor-sized buffers, runtime suspend/resume clock unwinding, channel clearing, and component bind/unbind with DMA registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/exynos/exynos5433_drm_decon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/exynos/exynos7_drm_decon.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/exynos/exynos7_drm_decon.c

### Purpose
`exynos7_drm_decon.c` implements the Exynos7/Exynos7870 DECON CRTC backend. It programs two display windows, timing registers, vblank interrupts, plane scanout, color keying, runtime-PM clocks, optional DPI encoder integration, and component binding.

### Important APIs, Types, And Functions
`struct decon_data` abstracts SoC-specific register layout shifts and base offsets. `struct decon_context` stores device/DRM/DMA state, CRTC, two planes, four clocks, MMIO, IRQ flags, I80 mode, vblank wait queue, SoC data, and optional encoder. Important functions include `decon_shadow_protect_win()`, `decon_wait_for_vblank()`, `decon_clear_channels()`, `decon_calc_clkdiv()`, `decon_commit()`, vblank enable/disable, `decon_win_set_pixfmt()`, `decon_update_plane()`, atomic enable/disable/flush, IRQ handler, bind/unbind, probe/remove, and runtime PM callbacks.

### Control Flow
Probe matches SoC data, detects I80 timings from DT, maps registers, acquires pclk/aclk/eclk/vclk, requests the correct IRQ, initializes wait state, probes DPI, enables runtime PM, and adds the component. Bind clears channels, registers DMA, initializes primary and cursor planes, creates the LCD CRTC, and binds DPI if present. Atomic enable resumes PM, resets/programs basic output, restores vblank enable if needed, and commits mode timing. Plane updates protect a window, program buffer start/size/offset, OSD coordinates, alpha, format, optional color key, triple buffering, enable bit, unprotect, and trigger standalone update.

### State, Persistence, And Dependencies
State persists in DECON registers, runtime-PM clock enables, IRQ flag bit, wait queue atomic, plane states, optional DPI encoder, and DMA registration. Dependencies include Exynos CRTC/plane/fb helpers, `regs-decon7.h`, DRM fourcc/vblank APIs, platform clocks/IRQs, OF matching, and runtime PM.

### Integration Points
Selected by `DRM_EXYNOS7_DECON`, this object exports `decon_driver`. It integrates with the Exynos DRM component framework, Exynos DPI helper, and DMA/IOMMU registration.

### Risks
SoC data offsets must match the compatible string. I80 mode changes IRQ and timing programming. `decon_bind()` returns early on plane init failure without unregistering DMA, which is a path to inspect if plane initialization can fail after `decon_ctx_initialize()`. Vblank waits have a 50 ms timeout and can mask hardware update failures. Burst length depends on effective width plus padding.

### Test Signals
Signals include Exynos7 and Exynos7870 compatibles, video and I80 modes, vblank wait timeout behavior, small cursor buffers, all advertised pixel formats, DPI bind/remove, runtime PM clock unwind failures, channel clear with active windows, and bind error-path leak checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/exynos/exynos7_drm_decon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/exynos/exynos_dp.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/exynos/exynos_dp.c

### Purpose
`exynos_dp.c` provides Samsung Exynos-specific glue around the shared Analogix DisplayPort bridge driver. It creates the DRM encoder, discovers panels or downstream bridges, bridges Exynos CRTC clock control into Analogix power callbacks, and participates in the component framework.

### Important APIs, Types, And Functions
`struct exynos_dp_device` stores the encoder, connector, optional downstream bridge, DRM/device pointers, fallback videomode, Analogix device, and platform data. Important functions are `exynos_dp_crtc_clock_enable()`, `exynos_dp_poweron()`, `exynos_dp_poweroff()`, `exynos_dp_get_modes()`, `exynos_dp_bridge_attach()`, `exynos_dp_dt_parse_panel()`, bind/unbind, probe/remove, and runtime suspend/resume.

### Control Flow
Probe allocates state and temporarily stores it as platform drvdata, supports legacy `panel` phandle lookup, otherwise uses `drm_of_find_panel_or_bridge()`, fills Analogix platform callbacks, records whether connector creation should be skipped for a downstream bridge, calls `analogix_dp_probe()`, and adds the component. Bind parses a fallback videomode when no panel or bridge exists, initializes a simple TMDS encoder, attaches helper funcs, sets possible Exynos LCD CRTCs, stores the encoder in platform data, and calls `analogix_dp_bind()`. Runtime PM delegates suspend/resume to Analogix.

### State, Persistence, And Dependencies
State persists in the encoder, connector pointer, bridge/panel references, fallback videomode, Analogix private object, and platform data callbacks. Dependencies include DRM bridge/panel/OF helpers, Exynos CRTC clock helpers, Analogix DP core, runtime PM, and component APIs.

### Integration Points
The Kconfig symbol `DRM_EXYNOS_DP` selects Analogix DP and panel helpers; the Makefile links this file into `exynosdrm`. The exported `dp_driver` platform driver matches `samsung,exynos5-dp`.

### Risks
Power callbacks fail with `-EPERM` when the encoder has no CRTC. Legacy panel and graph bridge discovery must not conflict. If `analogix_dp_bind()` fails, the encoder is destroyed; ownership must stay aligned with DRM helper expectations. Fallback videomode parsing only applies when there is no panel or bridge.

### Test Signals
Tests should cover legacy panel phandle, graph panel, graph bridge with skipped connector, fallback videomode, CRTC clock enable/disable during DP power transitions, bind failure cleanup, runtime suspend/resume, and possible-CRTC assignment.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/exynos/exynos_dp.c -->
