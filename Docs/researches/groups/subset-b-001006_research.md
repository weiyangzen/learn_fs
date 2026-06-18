# subset-b-001006 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_job.c -->
## sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_job.c

### Purpose
`ivpu_job.c` implements Intel VPU job submission, command queue lifecycle, doorbell registration, DMA fence completion, job timeout integration, and context abort recovery. It is the main bridge between DRM ioctls, GEM buffer objects, firmware job queues, and JSM job-done notifications.

### Important APIs, Types, And Functions
The ioctl entry points are `ivpu_submit_ioctl()`, `ivpu_cmdq_submit_ioctl()`, `ivpu_cmdq_create_ioctl()`, and `ivpu_cmdq_destroy_ioctl()`. Internal queue management is handled by `ivpu_cmdq_create()`, `ivpu_cmdq_register()`, `ivpu_cmdq_unregister()`, `ivpu_cmdq_push_job()`, and `ivpu_cmdq_release_all_locked()`. Job tracking uses `struct ivpu_job`, a private `struct ivpu_fence` wrapper around `dma_fence`, `ivpu_job_create()`, `ivpu_job_submit()`, `ivpu_job_signal_and_destroy()`, `ivpu_jobs_abort_all()`, and `ivpu_cmdq_abort_all_jobs()`. Recovery entry points are `ivpu_job_handle_engine_error()`, `ivpu_context_abort_locked()`, `ivpu_context_abort_work_fn()`, and `reset_engine_and_mark_faulty_contexts()`.

### Control Flow
Legacy submission validates engine, priority, buffer count, command offset alignment, context existence, and MMU fault state before calling `ivpu_submit()` with `cmdq_id` 0. Managed-command-queue submission validates capability and explicit command queue IDs, then uses the same `ivpu_submit()` path. `ivpu_submit()` copies user BO handles, enters the DRM device, creates a job and fence, looks up and binds each GEM object, adds the job fence to BO reservations, takes `pm->reset_lock` for read, then calls `ivpu_job_submit()`. Submission runtime-resumes the device, locks submitted jobs and the file context, lazily acquires or creates a command queue, registers it with firmware, prepares preemption buffers, allocates a job ID in `submitted_jobs_xa`, writes a `vpu_job_queue_entry`, rings the doorbell, starts timeout detection, and leaves the job live until IPC completion.

### State, Persistence, And Dependencies
Persistent per-open state lives in `file_priv->cmdq_xa`, command queue BOs, queue doorbell IDs, queue priority, and optional per-queue preemption buffers. Device-wide in-flight state lives in `vdev->submitted_jobs_xa`, `submitted_jobs_lock`, `busy_start_ts`, `busy_time`, `faults_detected`, and the IPC consumer registered on `VPU_IPC_CHAN_JOB_RET`. Dependencies include DRM file/GEM/reservation APIs, `ivpu_bo` allocation/binding, `ivpu_jsm_msg` doorbell/HWS/reset calls, `ivpu_mmu` context event suppression, runtime PM helpers, firmware boot API structures, and VPU hardware doorbell writes.

### Integration Points
The file integrates with UAPI structs from `ivpu_accel.h`, job queue ABI from `vpu_jsm_api.h`, firmware scheduling mode from `vdev->fw->sched_mode`, IPC completion callbacks through `ivpu_ipc_consumer_add()`, and PM timeout/recovery logic in `ivpu_pm.c`. Hardware scheduling mode creates/destroys command queues and sets context scheduling properties through JSM; OS scheduling mode registers a doorbell directly and releases contexts with `VPU_JSM_MSG_SSID_RELEASE`.

### Risks
The critical risks are concurrency and lifetime ordering. Job submission touches `file_priv->lock`, `submitted_jobs_lock`, runtime PM, BO reservations, and reset locking; lock-order regressions can deadlock. Doorbell IDs are global xarray entries with per-user limits, so unregister/reset paths must keep `db_count` and `db_xa` consistent. Error paths after BO lookup can leave referenced GEM objects until job destruction, making `ivpu_job_destroy()` coverage important. The managed command queue API must reject legacy queue destruction and submissions after `has_mmu_faults`. Preemption buffer handling is split between user-supplied and kernel-created buffers; mappable user buffers are intentionally rejected.

### Test Signals
High-signal tests include successful legacy submit and command-queue submit, queue create/destroy with priority and turbo flags, queue-full `-EBUSY`, invalid BO handle and invalid offset failures, submission during reset, MMU fault followed by context abort, engine-reset-required job status in HWS mode, timeout-driven recovery, user-supplied preemption buffer validation, `npu_busy_time_us` changes while jobs are active, and fence signaling plus BO `job_status` propagation on success, error, and abort.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_job.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_job.h -->
## sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_job.h

### Purpose
`ivpu_job.h` declares the job and command queue state shared by the ivpu driver and exposes job submission, command queue, completion, abort, and recovery entry points.

### Important APIs, Types, And Functions
`struct ivpu_cmdq` holds the firmware-visible `vpu_job_queue`, queue BO, optional preemption BOs, queue and doorbell IDs, priority, entry count, and legacy flag. `struct ivpu_job` records the submitting device/context, completion fence, command buffer VPU address, command queue/job/engine IDs, final status, preemption buffers, and flexible array of referenced BOs. Public functions include the four DRM ioctl handlers, `ivpu_context_abort_locked()`, queue reset/release helpers, job-done consumer init/fini, `ivpu_job_handle_engine_error()`, `ivpu_context_abort_work_fn()`, and `ivpu_jobs_abort_all()`.

### Control Flow
The header has no executable flow, but it defines the data contract used by submit ioctls, IPC callbacks, reset handling, and file cleanup. Callers must hold `file_priv->lock` for several command queue operations as documented by implementation lockdep assertions.

### State, Persistence, And Dependencies
State is per open-file context and per submitted job. The header depends on `ivpu_gem.h` for BO types and uses kernel `dma_fence`, DRM device/file declarations, and workqueue declarations through included or transitive headers.

### Integration Points
Consumers include `ivpu_job.c`, driver open/close paths, PM reset paths, IPC setup, sysfs busy accounting, and MMU fault handling. The queue/job fields mirror firmware ABI structures from `vpu_jsm_api.h`.

### Risks
Changes to `struct ivpu_job` or `struct ivpu_cmdq` can affect flexible-array allocation, cleanup ownership, and command queue registration assumptions. Any caller that bypasses the locking convention can race with queue destruction, context abort, or job completion.

### Test Signals
Compile tests should catch declaration drift. Runtime signals are clean open/close cleanup, successful command queue reuse, no BO/fence leaks after aborted jobs, and lockdep-clean submit/abort/reset paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_job.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_jsm_msg.c -->
## sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_jsm_msg.c

### Purpose
`ivpu_jsm_msg.c` is the typed firmware IPC wrapper layer for Job Scheduler Module commands. It builds `struct vpu_jsm_msg` requests, sends them on the correct IPC channel, waits for expected response message types, decodes selected response payloads, and maps serious failures into PM recovery when required.

### Important APIs, Types, And Functions
`ivpu_jsm_msg_type_to_str()` provides trace/debug names for every JSM message enum. Doorbell and context APIs are `ivpu_jsm_register_db()`, `ivpu_jsm_unregister_db()`, `ivpu_jsm_context_release()`, and `ivpu_jsm_hws_register_db()`. Engine APIs are `ivpu_jsm_get_heartbeat()`, `ivpu_jsm_reset_engine()`, `ivpu_jsm_preempt_engine()`, and `ivpu_jsm_hws_resume_engine()`. HWS command queue APIs include create, destroy, priority-band setup, context scheduling properties, and scheduling log setup. Telemetry/debug/power APIs include trace capability/config, dynamic debug control, metric streamer start/stop/update/info, D0i3 entry, DCT enable/disable, and state dump.

### Control Flow
Each function initializes a request with a fixed `type`, fills only the relevant union payload, then calls `ivpu_ipc_send_receive()`, `ivpu_ipc_send_receive_internal()`, or `ivpu_ipc_send_and_wait()` with the expected response type and timeout from `vdev->timeout`. Some functions validate `engine == VPU_ENGINE_COMPUTE`. Metric update validates returned `bytes_written` against the buffer size, and metric info rejects zero sample size. Engine reset increments `pm->engine_reset_counter`; reset or HWS resume failures trigger `ivpu_pm_trigger_recovery()`.

### State, Persistence, And Dependencies
This file stores no long-lived state itself. It modifies firmware state: doorbell registrations, command queue registrations, scheduling properties, trace configuration, metric streams, power DCT state, D0i3 save state, and engine reset state. Dependencies are `ivpu_ipc`, `ivpu_pm`, hardware idle polling, `vpu_jsm_api.h`, and device timeout settings.

### Integration Points
Job submission uses doorbell/HWS queue calls; PM uses heartbeat, D0i3, DCT, and state dump calls; debugfs/fw log paths can use trace and dynamic debug calls; metric-streamer ioctls use the metric APIs; context abort uses context release and HWS resume/reset calls. The tracepoint code depends on `ivpu_jsm_msg_type_to_str()`.

### Risks
The functions encode a firmware ABI. Wrong response type, channel, timeout, or payload union member can produce hangs or silent firmware misconfiguration. Some warnings are ratelimited, so repeated transient firmware failures may be easy to miss. D0i3 and DCT calls use internal IPC paths and must be coordinated with runtime PM state. Metric update has explicit overflow checking, but callers must still serialize buffer ownership.

### Test Signals
Useful signals include firmware boot with successful priority-band setup, doorbell register/unregister cycles in OS and HWS modes, heartbeat progress during long jobs, engine reset and resume after injected faults, trace config round trips, dynamic-debug commands, metric streamer start/update/stop with nonzero sample sizes, D0i3 entry on suspend, and DCT enable/disable acknowledgments.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_jsm_msg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_jsm_msg.h -->
## sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_jsm_msg.h

### Purpose
`ivpu_jsm_msg.h` declares the ivpu firmware JSM wrapper API used by jobs, PM, tracing, metric streaming, and debug paths.

### Important APIs, Types, And Functions
The header exports message-type stringification and wrappers for doorbells, heartbeat, engine reset/preempt, dynamic debug, trace capability/config, context release, D0i3 entry, HWS command queue lifecycle, scheduling logs/properties, priority bands, metric streamer operations, DCT, and state dumps.

### Control Flow
There is no runtime flow in the header. It defines a synchronous command/response contract: most functions return `0` or a negative errno after sending one JSM request.

### State, Persistence, And Dependencies
The header includes `vpu_jsm_api.h`, so it is tied to firmware ABI definitions and `struct vpu_jsm_msg`. It forward-uses `struct ivpu_device` through included driver headers.

### Integration Points
This is the shared boundary between higher-level driver code and firmware IPC. It is included by job, PM, sysfs/debug, trace, metric streamer, and IPC code.

### Risks
Prototype changes ripple through many subsystems and can break firmware ABI call sites. Because functions expose raw firmware fields like context IDs, command queue IDs, masks, and VPU addresses, callers must validate user input before invoking them.

### Test Signals
Compile coverage across ivpu modules is the first signal. Runtime tests should exercise all exported wrapper families at least once: submit, reset, suspend/resume, trace config, metric streamer, DCT, and state dump.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_jsm_msg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_mmu.c -->
## sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_mmu.c

### Purpose
`ivpu_mmu.c` programs and services the VPU SMMU-like MMU block. It allocates context descriptor, stream table, command queue, and event queue memory; resets/enables the MMU; installs context descriptors; invalidates TLBs; and handles MMU event and global-error interrupts.

### Important APIs, Types, And Functions
Public APIs are `ivpu_mmu_init()`, `ivpu_mmu_enable()`, `ivpu_mmu_disable()`, `ivpu_mmu_cd_set()`, `ivpu_mmu_cd_clear()`, `ivpu_mmu_invalidate_tlb()`, `ivpu_mmu_irq_evtq_handler()`, `ivpu_mmu_irq_gerr_handler()`, `ivpu_mmu_evtq_dump()`, `ivpu_mmu_discard_events()`, and `ivpu_mmu_disable_ssid_events()`. Key internal helpers allocate the CDTAB/STRTAB/CMDQ/EVTQ, write CR0/IRQ control registers, enqueue MMU commands (`CFGI_ALL`, `TLBI_NH_ASID`, `TLBI_NSNH_ALL`, `SYNC`), link stream table entries to the CD table, and translate event/error codes to strings.

### Control Flow
Initialization checks hardware ID registers, initializes the MMU mutex, allocates coherent tables/queues, links stream IDs 0 and 3 to the context descriptor table, then enables the MMU. Enable resets command/event queues, disables CR0, writes cache/shareability and table/queue base registers, enables command queue, invalidates configuration and TLBs, enables event queue and ATS checking, enables MMU interrupts, then sets SMMU enable. Context descriptor changes write CD table entries, flush cache when needed, and issue CFGI/SYNC if the MMU is on. Event IRQ handling drains EVTQ entries, maps SSIDs to `file_priv`, marks contexts with `has_mmu_faults`, sets `faults_detected`, and queues context abort work; global or reserved context faults trigger PM recovery.

### State, Persistence, And Dependencies
MMU state is in `vdev->mmu`: coherent tables, queues, producer/consumer indices, a lock, and `on`. Hardware register state persists until power/reset. Dependencies include register IO macros, DMA coherent memory, cache flushing when force snoop is disabled, `ivpu_mmu_context` page table roots, `vdev->context_xa`, PM recovery, hardware diagnostics, and VPU address-space constants.

### Integration Points
`ivpu_mmu_context.c` calls CD set/clear and TLB invalidation after map/unmap/protection changes. PM calls enable/disable around resume/suspend. Job/context abort logic calls `ivpu_mmu_disable_ssid_events()` and `ivpu_mmu_discard_events()`. Interrupt handlers call the EVTQ and GERROR paths from the hardware IRQ layer.

### Risks
Register sequencing and queue synchronization are fragile. A missed write memory barrier or cache flush can make the MMU consume stale commands or descriptors. Bounds checks use `ssid > IVPU_MMU_CDTAB_ENT_COUNT`, which allows `ssid == count` even though valid indices are normally `0..count-1`; callers should not pass out-of-range SSIDs. `ivpu_mmu_disable_ssid_events()` ignores return values from command queue writes/sync, so fault-event suppression failures may be only indirectly visible. Any event queue desynchronization can block new MMU interrupts until events are discarded.

### Test Signals
Test with boot/resume MMU enable, context map/unmap followed by successful firmware access, TLB invalidation after remap and read-only changes, injected user-context faults causing only that context to abort, injected global/reserved faults causing recovery, GERROR interrupt logging, suspend/resume cycles, force-snoop on/off paths, and stress submissions that churn context descriptors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_mmu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_mmu.h -->
## sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_mmu.h

### Purpose
`ivpu_mmu.h` defines MMU management state and the driver-internal API for MMU lifecycle, context descriptor installation, TLB invalidation, and interrupt handling.

### Important APIs, Types, And Functions
`struct ivpu_mmu_cdtab`, `struct ivpu_mmu_strtab`, and `struct ivpu_mmu_queue` describe coherent MMU resources. `struct ivpu_mmu_info` groups these resources with the mutex and `on` flag. Exported functions cover init/enable/disable, CD set/clear, TLB invalidation, EVTQ/GERROR interrupt service, event dump/discard, and per-SSID event suppression.

### Control Flow
The header has no executable flow. Its API is called during device init/resume/suspend, BO mapping, context teardown, and IRQ processing.

### State, Persistence, And Dependencies
The state structure is owned by `struct ivpu_device`. It depends on DMA addresses, mutexes, and `struct ivpu_mmu_pgtable` from the context layer.

### Integration Points
`ivpu_mmu_context.c`, PM, IRQ, and job recovery are the principal consumers. The `on` flag gates invalidation and descriptor updates while the device is suspended.

### Risks
Callers must respect the MMU lock and runtime state. Adding fields to `ivpu_mmu_info` requires careful initialization because the MMU is active across runtime PM transitions.

### Test Signals
Compile and runtime signals include clean init/fini, no lockdep warnings during map/unmap/interrupt paths, correct MMU re-enable after resume, and successful fault recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_mmu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_mmu_context.c -->
## sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_mmu_context.c

### Purpose
`ivpu_mmu_context.c` manages per-context VPU virtual address spaces. It allocates and frees four-level page tables, maps and unmaps scatter-gather tables into VPU addresses, changes page permissions, manages VPU virtual address ranges with `drm_mm`, and initializes global/reserved/user contexts.

### Important APIs, Types, And Functions
Public APIs include `ivpu_mmu_context_init()`, `ivpu_mmu_context_fini()`, global and reserved context init/fini helpers, `ivpu_mmu_context_insert_node()`, `ivpu_mmu_context_remove_node()`, `ivpu_mmu_context_map_sgt()`, `ivpu_mmu_context_unmap_sgt()`, and `ivpu_mmu_context_set_pages_ro()`. Internal helpers lazily ensure PGD/PUD/PMD/PTE pages, map 4K or contiguous 64K pages, split contiguous mappings, set read-only bits, and free nested page-table allocations.

### Control Flow
Mapping validates context, page alignment, and 48-bit VPU address range, builds protection bits, locks the context, walks each DMA scatterlist segment, maps pages using 64K contiguous entries when aligned and enabled, checks the scatterlist covers the BO size exactly, installs the context descriptor on first map, flushes write-combining buffers, unlocks, and invalidates the TLB. Unmapping clears PTEs to a dummy invalid physical address and invalidates the TLB. Read-only conversion optionally splits boundary 64K contiguous mappings, sets RO bits over the range, flushes, and invalidates.

### State, Persistence, And Dependencies
Each `struct ivpu_mmu_context` owns a mutex, `drm_mm`, `struct ivpu_mmu_pgtable`, CD-valid flag, and SSID. Page tables are highmem pages mapped write-combining and DMA-mapped bidirectionally. Dependencies include DRM MM address allocation, DMA mapping, vmalloc/vmap, cache attribute changes, `ivpu_mmu_cd_set()/clear()`, and hardware address ranges from `vdev->hw`.

### Integration Points
GEM BO binding uses this layer to map BO scatter-gather memory before job submission. File contexts use user/dma/shave ranges; the global context covers runtime through shave ranges; the reserved context installs an empty root table to deliberately fault reserved accesses. `ivpu_mmu.c` consumes page-table roots via context descriptors and handles TLB invalidation.

### Risks
Partial-map error handling unmaps only the accumulated SG size and relies on page table structures remaining valid. Contiguous 64K mappings must be split before partial RO conversion or permissions can affect neighboring pages. Page-table allocation uses nested pointer arrays sized as page-table entry counts; allocation failures must unwind correctly. TLB invalidation failures after unmap are warning-only, which can leave stale translations until a later invalidation or reset.

### Test Signals
Exercise small and large BO maps, unaligned VPU address rejection, scatterlist too-small/too-large rejection, 64K contiguous page mapping and disabled-contiguous mode, read-only conversion at aligned and unaligned-within-64K boundaries, context teardown after partial failure, reserved context fault behavior, and repeated runtime suspend/resume with existing contexts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_mmu_context.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_mmu_context.h -->
## sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_mmu_context.h

### Purpose
`ivpu_mmu_context.h` declares the per-context page table and virtual-address allocator structures plus the API used by GEM, context lifecycle, and MMU descriptor code.

### Important APIs, Types, And Functions
`IVPU_MMU_PGTABLE_ENTRIES` is 512 entries per level. `struct ivpu_mmu_pgtable` stores the root DMA pointer and nested CPU pointer arrays for PUD/PMD/PTE pages. `struct ivpu_mmu_context` stores the lock, `drm_mm`, page table, CD-valid flag, and context ID. Exported operations initialize/finalize contexts, manage global/reserved contexts, insert/remove address nodes, map/unmap SG tables, and set pages read-only.

### Control Flow
No executable flow exists in the header. The API implies context lock protection for address allocation and page-table mutation.

### State, Persistence, And Dependencies
The context persists for a DRM file/private context or device global/reserved context. It depends on `drm_mm`, DMA page-table roots, and hardware SSID identity.

### Integration Points
GEM BO allocation/binding and job submission depend on correct VPU virtual mappings from this API. MMU descriptor code consumes `pgd_dma` when installing context descriptors.

### Risks
The nested pointer layout is memory-heavy and assumes page-table levels are lazily allocated. Callers must keep BO lifetime, SG lifetime, and mapping lifetime synchronized with context teardown.

### Test Signals
Compile tests, lockdep on concurrent BO operations, leak checks after context close, and map/unmap stress with many sparse VPU ranges are the strongest signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_mmu_context.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_ms.c -->
## sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_ms.c

### Purpose
`ivpu_ms.c` implements metric streamer ioctls for collecting firmware-generated telemetry samples into kernel-managed BO buffers and copying sample or descriptor data back to userspace.

### Important APIs, Types, And Functions
Public ioctl handlers are `ivpu_ms_start_ioctl()`, `ivpu_ms_get_data_ioctl()`, `ivpu_ms_stop_ioctl()`, and `ivpu_ms_get_info_ioctl()`. Cleanup helpers are `ivpu_ms_cleanup()` and `ivpu_ms_cleanup_all()`. Internal helpers find instances by metric mask, copy leftover bytes, swap active/inactive buffers, allocate a reusable info BO, and free streamer instances.

### Control Flow
Start validates metric mask, read-period samples, and a minimum sampling period, runtime-resumes the device, serializes on `file_priv->ms_lock`, rejects duplicate masks, queries sample size with JSM, computes a double-buffered BO size, allocates a global cached mappable BO, starts firmware collection, returns sample and max-data sizes, and links the instance into the file context. Data retrieval either queries bytes available or switches firmware to the inactive buffer, swaps active/inactive pointers, and copies buffered plus leftover data to userspace. Stop finds the instance, sends metric stop, frees the BO, and removes it from the list.

### State, Persistence, And Dependencies
Per-file state is `ms_instance_list`, `ms_lock`, and optional `ms_info_bo`. Each instance stores metric mask, global BO, buffer size, active/inactive VPU addresses and CPU pointers, and leftover copy position. Dependencies include runtime PM, `ivpu_bo_create_global()`, JSM metric commands, and DRM ioctl UAPI structures.

### Integration Points
PM reset cleanup calls `ivpu_ms_cleanup_all()` to stop streams and free BOs. Metric descriptors and sample streams are firmware ABI objects defined in `vpu_jsm_api.h`. Userspace discovers metric info through `get_info` and starts streams through UAPI ioctls.

### Risks
Metric masks uniquely identify instances, so overlapping domains are delegated to firmware validation. Buffer sizing multiplies user read period, sample size, multiplier, and buffer count; overflow is not explicit before `PAGE_ALIGN()`, so large inputs should be reviewed carefully. `ivpu_ms_get_info_ioctl()` does not runtime-resume before JSM calls, unlike start/data/stop, so callers rely on surrounding device state or JSM availability. Copying from cached BO memory assumes firmware coherency and JSM update ordering.

### Test Signals
Test invalid masks and sample periods, duplicate start, start/get-data/stop cycles, zero-size get-data availability queries, undersized descriptor buffers returning `-ENOSPC`, reset cleanup of active streams, large read-period rejection by global range size, and repeated partial reads that exercise leftover handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_ms.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_ms.h -->
## sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_ms.h

### Purpose
`ivpu_ms.h` declares metric streamer instance state and ioctl/cleanup APIs for ivpu telemetry collection.

### Important APIs, Types, And Functions
`struct ivpu_ms_instance` stores the BO, list node, metric mask, buffer sizes, active/inactive VPU addresses and CPU pointers, and leftover copy bookkeeping. The header exports start/stop/get-data/get-info ioctl handlers and per-file/all-context cleanup.

### Control Flow
The header has no executable flow; it defines the state consumed under `file_priv->ms_lock`.

### State, Persistence, And Dependencies
Instances persist per open DRM file until stopped, file cleanup, or PM reset cleanup. Dependencies are list handling, ivpu BOs, and DRM device/file types.

### Integration Points
Used by ioctl registration, file cleanup, and PM reset recovery. Firmware metric payload layout is defined separately in `vpu_jsm_api.h`.

### Risks
The active/inactive pointer fields must remain synchronized with firmware buffer switching. Any consumer added outside the lock can race with cleanup.

### Test Signals
Build coverage plus stream lifecycle tests, reset cleanup tests, and leak checks after file close are the primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_ms.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_pm.c -->
## sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_pm.c

### Purpose
`ivpu_pm.c` implements ivpu power management, runtime suspend/resume, cold/warm boot preparation, reset/recovery, job timeout detection, and DCT duty-cycle control.

### Important APIs, Types, And Functions
PM callbacks are `ivpu_pm_suspend_cb()`, `ivpu_pm_resume_cb()`, `ivpu_pm_runtime_suspend_cb()`, and `ivpu_pm_runtime_resume_cb()`. Reset callbacks are `ivpu_pm_reset_prepare_cb()` and `ivpu_pm_reset_done_cb()`. Runtime helpers are `ivpu_rpm_get()`, `ivpu_rpm_put()`, `ivpu_pm_init()`, `ivpu_pm_enable()`, `ivpu_pm_disable()`, and `ivpu_pm_disable_recovery()`. Recovery/timeout APIs include `ivpu_pm_trigger_recovery()`, `ivpu_start_job_timeout_detection()`, and `ivpu_stop_job_timeout_detection()`. DCT APIs include init/enable/disable and IRQ work handling.

### Control Flow
Suspend prepares for reset, shuts down hardware, and prepares warm boot when possible. Resume restores PCI D0/state, powers hardware, enables MMU, boots firmware, and falls back to cold boot if warm boot fails. Recovery work disables runtime PM, optionally dumps firmware state and coredump, suspends, prepares cold boot, aborts jobs, cleans metric streams, resumes, updates runtime PM state, clears reset pending, and emits a uevent. Job timeout work queries heartbeat; if it does not progress, or if inference retry limits are exceeded, it triggers full recovery for OS scheduling or state dump/coredump plus context abort work for HWS scheduling.

### State, Persistence, And Dependencies
State lives in `vdev->pm`: reset lock, recovery work, delayed timeout work, reset counters, engine reset counter, reset-pending flag, and DCT active percent. Firmware boot state is updated through `vdev->fw->next_boot_mode`, warm boot entry point, and last heartbeat. Dependencies include PCI power state, runtime PM, hardware power/reset/idle helpers, MMU enable/disable, firmware load/boot/shutdown, IPC reset, fw log reset, job abort, metric cleanup, coredump, and JSM power/debug calls.

### Integration Points
Job submission takes `reset_lock` for read, and reset/recovery takes it for write. MMU is disabled before runtime suspend and enabled during resume. Job completion starts/stops timeout detection. Sysfs exposes reset/engine counters indirectly through driver state. Hardware BTRS DCT requests are serviced by `ivpu_pm_irq_dct_work_fn()`.

### Risks
Reset and runtime PM sequencing is high risk: stale jobs, active metric streams, or queued recovery work during suspend can break assumptions. `pm_runtime_get_if_active()` in abort work and sysfs frequency reads must be balanced. Recovery can be disabled by debug parameter, which leaves hangs unrecovered. Heartbeat-based timeout detection must coordinate with firmware scheduling mode and non-progress inference limits. DCT state is stored before firmware command success, so failure leaves requested state in `dct_active_percent`.

### Test Signals
System suspend/resume, runtime autosuspend/resume, warm-boot fallback to cold boot, PCI FLR/reset callbacks, job timeout in OS and HWS modes, recovery uevent emission, coredump on timeout/recovery, active job abort after reset, active metric stream cleanup, DCT enable/disable from IRQ request, and module parameters for timeout/recovery behavior are high-signal tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_pm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_pm.h -->
## sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_pm.h

### Purpose
`ivpu_pm.h` defines ivpu PM state and the driver-internal API for runtime PM, reset/recovery, timeout detection, and DCT control.

### Important APIs, Types, And Functions
`struct ivpu_pm_info` contains the owning device, delayed job timeout work, recovery work, reset read/write semaphore, reset and engine-reset counters, reset-pending flag, and DCT active percentage. Exported functions cover PM init/enable/disable, suspend/resume callbacks, PCI reset callbacks, runtime get/put, recovery triggering, job timeout start/stop, and DCT operations.

### Control Flow
The header itself has no control flow, but its `reset_lock` forms a central control-flow gate: submitters take read access while reset/recovery takes write access.

### State, Persistence, And Dependencies
PM state persists for the device lifetime and spans runtime suspend/resume. Dependencies include workqueues, rwsems, atomics, device/PCI callback types, and ivpu device state.

### Integration Points
Used by job submission/completion, MMU suspend/resume, firmware boot, PCI driver callbacks, and hardware DCT IRQ handling.

### Risks
New code using runtime PM must use `ivpu_rpm_get()`/`ivpu_rpm_put()` consistently and respect `reset_lock` when touching firmware or hardware.

### Test Signals
Lockdep-clean reset versus submit races, balanced runtime PM usage, timeout work cancellation, and recovery work disable during driver teardown are key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_pm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_sysfs.c -->
## sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_sysfs.c

### Purpose
`ivpu_sysfs.c` exposes read-only device attributes for NPU busy time, resident NPU memory utilization, scheduling mode, maximum DPU frequency, and current DPU frequency.

### Important APIs, Types, And Functions
The sysfs show functions are `npu_busy_time_us_show()`, `npu_memory_utilization_show()`, `sched_mode_show()`, `npu_max_frequency_mhz_show()`, and `npu_current_frequency_mhz_show()`. `ivpu_sysfs_init()` registers an attribute group with `devm_device_add_group()`.

### Control Flow
Each show function derives a value from driver state and formats it with `sysfs_emit()`. Busy time locks `submitted_jobs_lock`, adds accumulated `busy_time` and current active interval if jobs are in flight. Memory utilization locks `bo_list_lock` and sums resident BO sizes. Current frequency only reads hardware if `pm_runtime_get_if_active()` succeeds, then releases runtime PM.

### State, Persistence, And Dependencies
The attributes do not store state. They read `submitted_jobs_xa`, busy timestamps, `bo_list`, firmware scheduling mode, and hardware frequency registers. Dependencies include runtime PM, `ivpu_bo`, firmware state, and hardware frequency helpers.

### Integration Points
Registered during device setup and consumed by userspace monitoring. Busy time is maintained by job submission/completion in `ivpu_job.c`; memory residency is maintained by GEM/BO code; scheduling mode is firmware boot state.

### Risks
Frequent busy-time reads take `submitted_jobs_lock` and can affect submission performance, as documented. Current frequency returns zero when suspended, which userspace must distinguish from active low frequency. Memory utilization is resident BO size, not necessarily physical total allocation or firmware internal memory.

### Test Signals
Check attribute presence, formatting as decimal values, busy time increases only while jobs are submitted, memory utilization changes with BO residency, sched mode matches OS/HW firmware mode, max frequency is stable, and current frequency is zero while runtime suspended but nonzero when active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_sysfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_sysfs.h -->
## sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_sysfs.h

### Purpose
`ivpu_sysfs.h` declares the device sysfs registration entry point for ivpu.

### Important APIs, Types, And Functions
The only exported API is `ivpu_sysfs_init(struct ivpu_device *vdev)`.

### Control Flow
There is no executable flow in the header.

### State, Persistence, And Dependencies
It includes `ivpu_drv.h` for `struct ivpu_device`. Registered sysfs attributes persist for the managed lifetime of the device because the implementation uses devm registration.

### Integration Points
The PCI/DRM device setup path calls this after `ivpu_device` exists and before userspace monitoring reads attributes.

### Risks
The header is small, but including `ivpu_drv.h` makes it a broad dependency. Prototype changes affect device initialization.

### Test Signals
Successful build and sysfs attribute presence under the ivpu device are sufficient signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_sysfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_trace.h -->
## sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_trace.h

### Purpose
`ivpu_trace.h` defines ftrace tracepoints for ivpu power-management events, job lifecycle events, and JSM message activity.

### Important APIs, Types, And Functions
Trace events are `pm`, `job`, and `jsm` under `TRACE_SYSTEM vpu`. `pm` records a string event. `job` records event, context ID, engine ID, and job ID. `jsm` records event, message type string, status, request ID, and firmware result.

### Control Flow
The header expands through Linux tracepoint macros. Call sites such as `trace_pm()`, `trace_job()`, and `trace_jsm()` become enabled/disabled tracepoint calls depending on ftrace configuration.

### State, Persistence, And Dependencies
Tracepoints do not persist driver state but expose runtime events to tracing buffers. Dependencies include `ivpu_drv.h`, `ivpu_job.h`, `vpu_jsm_api.h`, `ivpu_jsm_msg.h`, and `ivpu_ipc.h`. `TRACE_INCLUDE_PATH` is set to `.` and the file includes `trace/define_trace.h`.

### Integration Points
PM code traces suspend/resume transitions; job code traces job create/submit/done; IPC/JSM code can trace firmware messages. `ivpu_trace_points.c` instantiates the tracepoints.

### Risks
Tracepoint payloads dereference `job->file_priv` and JSM message pointers at call time, so callers must pass live objects. String fields point to static or caller-provided strings; unstable lifetime would corrupt trace output.

### Test Signals
Build with tracing enabled, inspect `/sys/kernel/tracing/events/vpu/*`, enable events while submitting jobs and suspending/resuming, and verify JSM types stringify correctly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_trace_points.c -->
## sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_trace_points.c

### Purpose
`ivpu_trace_points.c` is the single translation unit that instantiates ivpu tracepoint definitions.

### Important APIs, Types, And Functions
It defines `CREATE_TRACE_POINTS` and includes `ivpu_trace.h` when not running under `__CHECKER__`.

### Control Flow
There is no runtime control flow beyond tracepoint registration generated by the trace infrastructure.

### State, Persistence, And Dependencies
Generated tracepoint metadata persists with the module. The file depends entirely on `ivpu_trace.h` and Linux tracepoint code generation.

### Integration Points
Without this file, call sites could compile as declarations but tracepoint storage would not be emitted. It must remain unique to avoid duplicate tracepoint definitions.

### Risks
Including `ivpu_trace.h` with `CREATE_TRACE_POINTS` in more than one file would cause duplicate symbols. Excluding it from the build would remove the runtime trace events.

### Test Signals
Kernel/module build and visibility of `vpu:pm`, `vpu:job`, and `vpu:jsm` trace events are the key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_trace_points.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/ivpu/vpu_boot_api.h -->
## sources/distributed-fs/ceph-client/drivers/accel/ivpu/vpu_boot_api.h

### Purpose
`vpu_boot_api.h` defines the packed host/firmware boot ABI for Intel VPU firmware images, boot parameters, tracing buffers, scheduling mode, power profile, DVFS, D0i3, and DCT configuration.

### Important APIs, Types, And Functions
The header exports version macros `VPU_BOOT_API_VER_*`, firmware header constants, `struct vpu_firmware_header`, boot type and scheduling mode macros, cache/ECC/governor enums, trace destination and processor bit definitions, `struct vpu_boot_params`, tracing buffer canary/format constants, and `struct vpu_tracing_buffer_header`. There are no functions.

### Control Flow
No code executes here. The driver reads firmware image headers, fills boot parameters, and firmware later reads/writes the shared boot parameter block. Warm boot flow depends on `save_restore_ret_address`, while trace and power-management code depend on boot-time fields and firmware-updated telemetry fields.

### State, Persistence, And Dependencies
The structures are packed to 4-byte alignment and are binary ABI. Fields persist in firmware image headers or shared boot-parameter memory. The boot params include IPC region addresses, global PIO base, IRQ numbers, device identity, trace buffers, DVFS settings, D0i3 residency and timestamps, system time, power-state timestamps, scheduling mode, focus timer, ECC signal mode, power profile, and DCT active/inactive periods.

### Integration Points
`ivpu_fw` and `ivpu_pm` use this ABI for cold/warm boot and suspend/resume. `ivpu_job.c` uses scheduling mode constants, and tracing/firmware-log code uses trace buffer definitions. Firmware packaging tools use the version table and firmware header layout.

### Risks
This is a strict ABI: changing packing, field order, sizes, version macros, or reserved spacing can break firmware compatibility. Many fields are hardware-generation sensitive. The boot parameter struct is large and offset-oriented, so inserted fields outside reserved areas would corrupt subsequent firmware reads. Host and firmware must agree on scheduling mode, IPC memory, IRQ routing, and trace buffer layout.

### Test Signals
Verify firmware header parsing and API version negotiation, cold boot and warm boot paths, D0i3 suspend/resume, trace buffer canary and wrap handling, scheduling mode selection, DVFS parameter programming, power-state timestamps, and firmware compatibility tests across supported VPU generations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/ivpu/vpu_boot_api.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/ivpu/vpu_jsm_api.h -->
## sources/distributed-fs/ceph-client/drivers/accel/ivpu/vpu_jsm_api.h

### Purpose
`vpu_jsm_api.h` defines the packed Job Scheduler Module IPC ABI shared between the ivpu kernel driver and VPU firmware. It covers job queues, inline commands, statuses, IPC channels, message types, HWS scheduling structures, trace configuration, metric streamer descriptors, dynamic debug, power messages, and the top-level `struct vpu_jsm_msg`.

### Important APIs, Types, And Functions
The header provides `VPU_JSM_API_VER_*`, engine IDs, JSM status codes, IPC channel IDs, job and job-queue flag enums, priority bands, `struct vpu_job_queue_entry`, `struct vpu_inline_cmd`, `union vpu_jobq_slot`, `struct vpu_job_queue_header`, `struct vpu_job_queue`, HWS log/native-fence log structs, `enum vpu_ipc_msg_type`, payload structs for every request/response, metric group/counter descriptors, `union vpu_ipc_msg_payload`, and `struct vpu_jsm_msg`. There are no functions.

### Control Flow
The header defines message flow rather than executing it. Host sends async commands, general commands, or job queues; firmware sends job done, native fence, command response, metric notification, scheduling log notification, and power acknowledgments. `ivpu_jsm_msg.c` wraps these definitions, and `ivpu_job.c` writes `vpu_job_queue_entry` records consumed by firmware.

### State, Persistence, And Dependencies
All structures are packed to 8-byte alignment for binary compatibility and cacheline-sensitive IPC. Persistent shared state includes job queue header head/tail fields, queue slots, firmware-owned private job flags, metric streamer buffers, log buffers, and message request IDs/results. The API depends on Linux bit macros for some flag definitions and on firmware honoring reserved fields.

### Integration Points
Job submission, doorbell registration, HWS command queue management, engine reset/preempt, context release, heartbeat, PM D0i3/DCT/state dump, trace configuration, dynamic debug, metric streaming, and native fences all depend on this header. The trace layer stringifies `enum vpu_ipc_msg_type`.

### Risks
ABI drift is the main risk. Status ranges drive recovery decisions, especially engine-reset-required statuses. Queue flag semantics affect firmware scheduling and notification behavior. The metric update structure documents host-side hazards when current and next buffers are both nonzero. HWS suspend/resume/reset structures carry context and command queue IDs that must match driver state. Any packing or field-order change must be versioned and coordinated with firmware.

### Test Signals
Run firmware IPC compatibility tests, submit jobs in OS and HWS modes, exercise engine reset/preempt responses, native-fence queues on supported hardware, metric streamer start/update/info/notification, trace get/set/name/capability, dynamic debug control, D0i3 and DCT messages, and negative tests for non-success `result` and engine-reset-required statuses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/ivpu/vpu_jsm_api.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/qaic/Kconfig -->
## sources/distributed-fs/ceph-client/drivers/accel/qaic/Kconfig

### Purpose
`qaic/Kconfig` declares the build-time configuration option for the Qualcomm Cloud AI accelerator DRM accel driver.

### Important APIs, Types, And Functions
The single option is `CONFIG_DRM_ACCEL_QAIC`, a tristate named "Qualcomm Cloud AI accelerators". It depends on `DRM_ACCEL`, `PCI && HAS_IOMEM`, and `MHI_BUS`, and selects `CRC32` plus `WANT_DEV_COREDUMP`.

### Control Flow
No runtime flow exists. Kconfig controls whether the qaic driver is built-in, built as module `qaic`, or omitted.

### State, Persistence, And Dependencies
The configuration state persists in the kernel `.config`. Dependencies ensure the driver has DRM accel infrastructure, PCI/MMIO support, and MHI bus support. Selected symbols support control-message CRCs and device coredumps.

### Integration Points
The option drives `qaic/Makefile` through `obj-$(CONFIG_DRM_ACCEL_QAIC)`. It also controls availability of qaic PCI probing, MHI channel drivers, DRM ioctls, sysfs/debugfs, RAS, SSR, and Sahara firmware loading compiled into the module.

### Risks
Missing dependencies would produce build or probe failures. Selecting coredump and CRC is necessary for diagnostics and control paths. Users enabling the option without matching hardware get no functional device but loadable module code.

### Test Signals
Build with `y`, `m`, and `n`; verify module name `qaic`; confirm dependencies prevent invalid configs; boot a QAIC system and confirm PCI probe plus MHI channels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/qaic/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/qaic/Makefile -->
## sources/distributed-fs/ceph-client/drivers/accel/qaic/Makefile

### Purpose
`qaic/Makefile` defines how the Qualcomm Cloud AI accelerator driver objects are linked into the `qaic` module or built-in object.

### Important APIs, Types, And Functions
`obj-$(CONFIG_DRM_ACCEL_QAIC) := qaic.o` creates the aggregate target. `qaic-y` lists `mhi_controller.o`, `qaic_control.o`, `qaic_data.o`, `qaic_drv.o`, `qaic_ras.o`, `qaic_ssr.o`, `qaic_sysfs.o`, `qaic_timesync.o`, and `sahara.o`. `qaic-$(CONFIG_DEBUG_FS)` adds `qaic_debugfs.o`.

### Control Flow
No runtime flow exists. Kbuild compiles and links the listed objects when the Kconfig symbol is enabled.

### State, Persistence, And Dependencies
Build state is controlled by `CONFIG_DRM_ACCEL_QAIC` and `CONFIG_DEBUG_FS`. Object ordering is the linker order but runtime init is controlled by module init functions inside the source files.

### Integration Points
The list pulls together the PCI driver, MHI controller setup, control/data ioctls, RAS/SSR recovery, sysfs, timesync, Sahara firmware loading, and optional debugfs support.

### Risks
Omitting an object can break unresolved symbols or silently remove features such as SSR cleanup or timesync channels. Adding debugfs unconditionally would break builds without `CONFIG_DEBUG_FS`.

### Test Signals
Build qaic with and without `CONFIG_DEBUG_FS`, inspect `qaic.o` symbols for expected module init/exit pieces, and boot/probe with all MHI subdrivers available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/qaic/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/qaic/mhi_controller.c -->
## sources/distributed-fs/ceph-client/drivers/accel/qaic/mhi_controller.c

### Purpose
`mhi_controller.c` builds and manages the MHI controller used by qaic PCI devices. It defines family-specific channel/event tables, firmware image paths, controller callbacks, register access quirks, initial power-up, reset handling, and teardown.

### Important APIs, Types, And Functions
Public functions are `qaic_mhi_register_controller()`, `qaic_mhi_free_controller()`, `qaic_mhi_start_reset()`, and `qaic_mhi_reset_done()`. Important internal data are `fw_image_paths`, `aic100_channels`, `aic200_channels`, `aic100_events`, `aic200_events`, and `mhi_cntrl_configs`. Internal helpers implement register read/write callbacks, no-op runtime get/put, MHI status callbacks, and `mhi_reset_and_async_power_up()` fallback from SBL to PBL.

### Control Flow
Registration allocates `struct mhi_controller`, fills PCI device pointer, IOVA range, status/runtime/register callbacks, BAR registers, IRQ array, IRQ flags, firmware image path, family name/segment length, copies the family config with the module timeout, registers the controller, prepares power-up, and asynchronously powers up. If async power-up returns `-EIO` while in SBL, it performs a SoC reset, polls execution environment up to 25 seconds for PBL, then retries async power-up. Free powers down, unprepares, and unregisters. Reset start powers down with link-up true; reset done tries async power-up again.

### State, Persistence, And Dependencies
The controller state is owned by the MHI core after registration and referenced by `qaic_device->mhi_cntrl`. Channel tables define QAIC loopback, Sahara, diag, SSR, QDSS/logging, control, status, telemetry, debug, timesync, periodic timesync, and IPCR channels with execution-environment masks. Dependencies include Linux MHI, PCI, firmware files under `qcom/aic100/sbl.bin` and `qcom/aic200/sbl.bin`, and qaic reset cleanup callbacks.

### Integration Points
`qaic_drv.c` calls registration during PCI probe and reset helpers during PCI reset flows. MHI child drivers in qaic modules bind to configured channel names. `mhi_status_cb()` calls `qaic_dev_reset_clean_local_state()` on system error and logs fatal errors.

### Risks
The large static channel tables are hardware ABI; wrong channel number, direction, event ring, or EE mask breaks child drivers or firmware loading. The SOC_HW_VERSION read quirk returns a synthetic value at offset `0x224`; removing it can cause false link-down errors. The controller uses a full physical IOVA range, so remote-side size calculations depend on `PHYS_ADDR_MAX - 1`. Shared MSI handling changes IRQ flags. Power-up fallback timing is fixed and may fail slow devices.

### Test Signals
Probe AIC100 and AIC200, verify all expected MHI channels enumerate in SBL and AMSS, load Sahara firmware from configured paths, test SBL reset fallback, trigger MHI fatal/system error callbacks, exercise PCI reset start/done, vary `mhi_timeout_ms`, and confirm no channel/event table mismatches under MHI debug logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/qaic/mhi_controller.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/qaic/mhi_controller.h -->
## sources/distributed-fs/ceph-client/drivers/accel/qaic/mhi_controller.h

### Purpose
`mhi_controller.h` declares qaic's MHI controller lifecycle API for PCI probe, teardown, and reset flows.

### Important APIs, Types, And Functions
It exports `qaic_mhi_register_controller()`, `qaic_mhi_free_controller()`, `qaic_mhi_start_reset()`, and `qaic_mhi_reset_done()`.

### Control Flow
There is no executable flow in the header. The API expresses a lifecycle: register and power up; power down/free; power down before reset; power up after reset.

### State, Persistence, And Dependencies
The returned `struct mhi_controller` is persisted in `qaic_device`. The prototypes depend on PCI device, MHI controller, MMIO BAR pointer, IRQ, MSI sharing, and family ID.

### Integration Points
Used by qaic PCI driver code and reset callbacks. It hides channel table and MHI-core setup details from the rest of the driver.

### Risks
Family ID must be valid for the static arrays in the implementation. Callers must pair successful registration with free and must not call reset helpers after unregister.

### Test Signals
Build coverage, probe/remove cycles, PCI reset cycles, and family-specific AIC100/AIC200 boot are the key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/qaic/mhi_controller.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/qaic/qaic.h -->
## sources/distributed-fs/ceph-client/drivers/accel/qaic/qaic.h

### Purpose
`qaic.h` is the central shared header for the Qualcomm Cloud AI accelerator driver. It defines device, user, DMA bridge channel, DRM device, GEM BO, and BO slice state plus cross-module function prototypes for control, data, reset, sysfs, and MHI callbacks.

### Important APIs, Types, And Functions
Important constants include DBC BAR offsets/sizes, SSR sentinel, no-partition sentinel, and container macros. Enums define AIC families, device states (`OFFLINE`, `BOOT`, `ONLINE`), and DBC subsystem/reset states. `struct qaic_user` tracks DRM users with kref and SRCU. `struct dma_bridge_chan` tracks a DBC's queues, DMA address, locks, user, request IDs, IRQ/polling, BO lists, wait queue, and state. `struct qaic_device` aggregates PCI/MHI/MMIO, control channel queues, DBCs, SRCU, device state, MHI side channels, RAS counters, SSR state, workqueues, and DRM device reference. `struct qaic_drm_device`, `struct qaic_bo`, and `struct bo_slice` define DRM accel-facing state. Prototypes cover manage ioctls, MHI callbacks, control open/close, user release, DBC enable/disable/release/wakeup, GEM/data ioctls, reset cleanup, SSR transitions, and sysfs.

### Control Flow
The header has no executable flow but describes the cross-file driver architecture. PCI probe creates `qaic_device`, registers MHI, creates DRM devices, and initializes DBC/control/sysfs state. Users open a DRM device, issue manage ioctls to activate/deactivate DBCs, create/attach/execute/wait BOs through data ioctls, and release resources on close or reset. MHI callbacks drive control and side-channel completions.

### State, Persistence, And Dependencies
State spans PCI device lifetime (`qaic_device`), logical DRM partition lifetime (`qaic_drm_device`), open-file lifetime (`qaic_user`), DBC assignment lifetime, and GEM BO/slice lifetime. Synchronization uses mutexes, spinlocks, SRCU, wait queues, completions, workqueues, and krefs. Dependencies include Linux PCI, MHI, interrupt, DRM device/GEM, dma-buf/import, and coredump/RAS/SSR support in other qaic files.

### Integration Points
Every qaic source file includes or depends on this header: PCI driver setup, MHI controller, control-message encoding, data-path DMA queues, RAS/SSR handlers, sysfs/debugfs, timesync, and Sahara boot loading. UAPI ioctls eventually map into the prototypes declared here.

### Risks
This header is a broad coupling point. Struct layout changes can break assumptions in many files, especially DBC queue ownership, BO slicing, reset cleanup, and SSR state transitions. Synchronization is subtle: DBC lists use spinlocks and SRCU, users use krefs/SRCU, control path uses mutexes and workqueues, and BOs use completions and mutexes. Device reset must clean local state while MHI callbacks and users may still reference objects.

### Test Signals
Probe/remove, user open/close, manage activate/deactivate/status, BO create/mmap/import/attach/execute/wait/detach, DBC interrupt and polling modes, MHI control callbacks, SSR enter/exit, RAS counters, reset cleanup under active users, sysfs DBC state updates, and KASAN/KCSAN/lockdep runs are high-signal coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/qaic/qaic.h -->
