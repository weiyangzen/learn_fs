# subset-b-003631 research

Grouped research for the PowerVR Imagination DRM MMU, power-management, and queue/scheduler files under `sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_mmu.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_mmu.c

## Purpose
Implements the PowerVR device MMU page-table manager. It creates and destroys MMU contexts, maps scatter-gather backed GEM memory into GPU virtual addresses, unmaps ranges, tracks host-side mirror page tables, syncs table memory for device consumption, and sends firmware MMU cache/TLB flush commands when mappings change.

## Important APIs, types, and functions
- Public APIs: `pvr_mmu_flush_request_all()`, `pvr_mmu_flush_exec()`, `pvr_mmu_context_create()`, `pvr_mmu_context_destroy()`, `pvr_mmu_get_root_table_dma_addr()`, `pvr_mmu_op_context_create()`, `pvr_mmu_op_context_destroy()`, `pvr_mmu_map()`, and `pvr_mmu_unmap()`.
- Backing memory: `struct pvr_mmu_backing_page` wraps one zeroed host page, CPU mapping, DMA address, raw page pointer, and owning `pvr_device`.
- Raw tables: `struct pvr_page_table_l2_entry_raw`, `pvr_page_table_l1_entry_raw`, `pvr_page_table_l0_entry_raw`, `pvr_page_flags_raw`, and raw L2/L1/L0 table structs encode Rogue MMU entries with compile-time size checks.
- Mirror tables: `struct pvr_page_table_l2`, `pvr_page_table_l1`, and `pvr_page_table_l0` mirror the hardware tree and track children, parents, parent indices, and entry counts.
- Operation state: `struct pvr_mmu_context`, `struct pvr_page_table_ptr`, and `struct pvr_mmu_op_context` cache traversal position, preallocated tables for map operations, freed tables from unmaps, SG mapping parameters, and required sync level.
- Core helpers include table entry set/clear/is-valid helpers, `pvr_page_table_l1_get_or_insert()`, `pvr_page_table_l0_get_or_insert()`, `pvr_mmu_op_context_set_curr_page()`, `pvr_mmu_op_context_next_page()`, `pvr_page_create()`, `pvr_page_destroy()`, and `pvr_mmu_map_sgl()`.

## Control flow
MMU cache flushing is flag driven. Table writes call `pvr_mmu_set_flush_flags()` through sync helpers. `pvr_mmu_flush_exec()` atomically consumes `pvr_dev->mmu_flush_cache_flags`, skips work before firmware boot or when no flags are pending, sends a `ROGUE_FWIF_KCCB_CMD_MMUCACHE` command, waits for completion, and hard-resets the GPU once before retrying. If retry or waited completion fails, it marks the device lost.

Context creation allocates a root L2 table and stores the owning device. Operation context creation optionally preallocates enough L1/L0 tables for a requested mapping range, using the supplied size and offset. Mapping calls set the current GPU page with creation enabled, derive L0 flags from GEM BO flags, walk the DMA SG table from `sgt_offset`, call `pvr_mmu_map_sgl()` for each covered segment, and roll back already-created pages if a later segment fails. Unmapping sets the current page without creation, skips missing intermediate tables, clears existing leaf entries, and queues empty L0/L1 tables for later freeing.

Traversal flushes stale tables before changing cached pointers. `pvr_mmu_op_context_next_page()` increments L0, then L1, then L2 indices and syncs levels that are about to be unloaded. Insertion uses preallocated table lists, issues write memory barriers before linking parent entries, and marks the needed parent sync level. Removal clears raw parent entries, detaches mirror child pointers, moves emptied tables to free lists, and recursively removes empty parents. Operation context destruction performs the remaining page-table sync, immediately waits for a firmware flush for unmaps, frees unused preallocations and unmap-deleted tables, then frees the op context.

## State and persistence
Persistent driver state is the root and child mirror page-tree under each `pvr_mmu_context`, plus DMA-backed raw table pages visible to the GPU. Per-operation state is transient but can mutate persistent mappings by inserting or deleting table entries. `pvr_dev->mmu_flush_cache_flags` coalesces cache/TLB flush requirements across page-table writes until `pvr_mmu_flush_exec()` consumes it. Mapped GPU virtual addresses persist until explicitly unmapped or the owning VM/MMU context is destroyed.

## Dependencies and integration points
The file depends on PowerVR device, firmware, KCCB, GEM flags, Rogue firmware interface, and Rogue MMU register-definition headers. It uses Linux page allocation, `vmap()`, DMA mapping/sync APIs, SG iteration, atomics, barriers, `drm_dev_enter()`, and runtime device-loss handling through `pvr_power_reset()` and `pvr_device_lost()`. VM code obtains the root table DMA address for firmware memory contexts and creates op contexts around VM bind/unbind operations.

## Risks
Flush failure is treated as memory-corruption risk and escalates to reset/device loss, so KCCB wait behavior is critical. Table range preallocation uses `sgt_offset + size` to estimate table counts; boundary conditions around exact table-size multiples deserve scrutiny. Mapping rollback only unmaps pages counted as successfully mapped and must preserve traversal state exactly. The code assumes callers pass page-aligned sizes and device addresses; some validation exists for mapping size/SG offsets, but index helpers do not bounds-check. Non-coherent DMA paths rely on the correct sync level and leaf-to-root sync ordering.

## Test signals
Useful signals are successful VM bind/unbind under sparse and multi-SG objects, `-EEXIST` on double-map attempts, no leaks from failed map preallocation or mid-SG rollback, correct firmware MMU cache commands, reset/device-lost logs on forced KCCB failures, and GPU page-fault behavior after unmap. Boundary tests should cover L0/L1/L2 index rollover, zero-size map/unmap, offsets into SG entries, non-coherent DMA devices, and mappings crossing table boundaries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_mmu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_mmu.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_mmu.h

## Purpose
Declares the public PowerVR MMU API and constants used by VM, firmware-context, and memory-binding code. It exposes device page-size and address-space assumptions while keeping the concrete MMU context and operation-context layouts private to `pvr_mmu.c`.

## Important APIs, types, and functions
- Constants: `PVR_DEVICE_PAGE_SIZE`, `PVR_DEVICE_PAGE_SHIFT`, `PVR_DEVICE_PAGE_MASK`, `PVR_PAGE_TABLE_ADDR_SPACE_SIZE`, `PVR_PAGE_TABLE_ADDR_BITS`, and `PVR_PAGE_TABLE_ADDR_MASK`.
- Opaque types: `struct pvr_mmu_context` and `struct pvr_mmu_op_context`.
- Flush APIs: `pvr_mmu_flush_request_all()` and `pvr_mmu_flush_exec()`.
- Context APIs: `pvr_mmu_context_create()`, `pvr_mmu_context_destroy()`, and `pvr_mmu_get_root_table_dma_addr()`.
- Operation APIs: `pvr_mmu_op_context_create()`, `pvr_mmu_op_context_destroy()`, `pvr_mmu_map()`, and `pvr_mmu_unmap()`.

## Control flow
The header has no runtime control flow. It defines the lifecycle expected by callers: create an MMU context, create one or more operation contexts around SG-backed map or unmap work, call map/unmap, destroy the operation context to sync and free staging resources, and execute MMU flushes before GPU work observes the changed mappings.

## State and persistence
No storage is defined in the header. Its constants make the current ABI assumption explicit: device pages track `PAGE_SIZE`, and the represented GPU virtual address space is 1 TiB. The opaque context pointers refer to persistent page-tree state managed by the implementation.

## Dependencies and integration points
Depends on Linux memory and type headers plus forward declarations for `pvr_device`, `pvr_vm_context`, and `sg_table`. It integrates with VM bind paths, GEM object mapping, firmware memory context creation, and queue submission paths that need pending MMU flushes completed before new jobs run.

## Risks
Changing the page-size or address-space constants affects page-table encoding, VM validation, firmware-visible root tables, and every caller's alignment assumptions. The opaque API keeps internals private, but callers must still obey page alignment and lifetime rules because the implementation does not defensively validate every address/index.

## Test signals
Build coverage catches signature and include drift. Runtime signals come from VM bind/unbind tests, firmware context boot with the root table DMA address, and job submission after map/unmap plus flush.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_mmu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_power.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_power.c

## Purpose
Implements PowerVR GPU power sequencing, firmware power transitions, watchdog-based firmware stall detection, reset recovery, runtime PM callbacks, and multi-power-domain attachment. It is the central integration point between DRM device lifetime, platform clocks/resets or power sequencers, firmware start/stop, queue reset handling, and device-loss reporting.

## Important APIs, types, and functions
- Public APIs: `pvr_device_lost()`, `pvr_power_is_idle()`, `pvr_watchdog_init()`, `pvr_watchdog_fini()`, `pvr_power_device_suspend()`, `pvr_power_device_resume()`, `pvr_power_device_idle()`, `pvr_power_reset()`, `pvr_power_domains_init()`, and `pvr_power_domains_fini()`.
- Firmware power helpers: `pvr_power_send_command()`, `pvr_power_request_idle()`, `pvr_power_request_pwr_off()`, `pvr_power_fw_disable()`, and `pvr_power_fw_enable()`.
- Watchdog helpers: `pvr_watchdog_kccb_stalled()` and `pvr_watchdog_worker()`.
- Platform sequencing implementations: `pvr_power_sequence_ops_manual` for clocks/reset controls and `pvr_power_sequence_ops_pwrseq` for `pwrseq` providers.
- Recovery helpers: `pvr_power_clear_error()` and `pvr_power_get_clear()`.

## Control flow
Firmware disable optionally cancels the watchdog, asks firmware to forced-idle and power off, disables IRQs for runtime suspend, and stops firmware. Firmware enable optionally reenables IRQs, starts firmware, waits for boot, queues the watchdog, and rolls IRQ state back on failure. Runtime suspend enters the DRM device, disables firmware if booted, then calls the platform `power_off()` operation. Runtime resume powers hardware on and restarts firmware if it had been booted before suspend.

The watchdog runs every 500 ms while the device is active. It takes a runtime PM reference only if the device is already in use, skips unbooted firmware, and checks KCCB progress. Two consecutive polls with pending KCCB work and unchanged executed-command count are treated as a stall and trigger a hard reset. When command progress is unchanged but KCCB is idle and there are no active queue-list entries, it sends a firmware health-check command to prove liveness.

`pvr_power_reset()` holds a runtime PM reference, serializes with `reset_sem`, disables IRQs, optionally stops all queues for hard reset, then loops through firmware disable and enable. A hard reset powers the device down, runs `pvr_fw_hard_reset()`, powers it back up, and restarts firmware. A soft reset clears firmware HWR fault flags and restarts firmware; if it fails, the loop escalates to hard reset. Hard reset failure marks the DRM device lost and leaves IRQs disabled.

Power-domain initialization counts device-tree `power-domains`. With more than one domain it attaches named domains `a` through `e`, creates stateless runtime-PM device links from later domains to the first domain, and stores the domain list/link array in `pvr_dev->power`. Finalization deletes links in reverse, detaches domains, frees the link array, and zeros the state.

## State and persistence
Persistent state lives in `pvr_device`: `lost`, `irq`, `reset`, `pwrseq`, clocks, `fw_dev.booted`, firmware shared memory fields, watchdog delayed work and counters, queue lists, runtime PM status, and attached power-domain metadata. The watchdog mutates `old_kccb_cmds_executed` and `kccb_stall_count`. Reset temporarily changes queue scheduler state and may update firmware boot state around hard reset.

## Dependencies and integration points
Depends on DRM unplug/device-enter helpers, runtime PM, IRQ control, clocks, reset controls, generic power sequencer consumer API, OF power-domain helpers, device links, firmware start/stop/hard-reset helpers, KCCB command submission, queue pre/post reset hooks, and Rogue firmware shared structures. It is called from PM ops, watchdog workqueue, MMU flush recovery, firmware interrupt recovery paths, and driver probe/remove domain setup.

## Risks
Reset and PM paths are concurrency-sensitive: IRQ disable mode differs for hard reset and threaded-IRQ soft reset, and runtime PM error clearing temporarily disables PM. If `pvr_power_get_clear()` fails, `pvr_power_reset()` only warns and still proceeds, which can complicate recovery on persistent PM errors. Watchdog health-check logic depends on queue active/idle list correctness. Device-loss handling intentionally prevents further DRM access, so false positives are severe. Multi-domain support is limited to five named domains and assumes link direction/order matches platform requirements.

## Test signals
Expected signals include clean suspend/resume with firmware booted and unbooted, watchdog recovery after injected KCCB stalls, escalation from soft reset to hard reset, device-lost logs on hard reset failure, IRQ state remaining correct after failures, and no active queue deadlocks across reset. Platform tests should cover manual clock/reset sequencing, pwrseq sequencing, one-domain and multi-domain DT configurations, deferred power-sequencer probe, and runtime PM idle returning `-EBUSY` while firmware or KCCB work is active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_power.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_power.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_power.h

## Purpose
Declares the PowerVR power-management interface shared by probe, PM callbacks, firmware control, MMU recovery, and queue reset code. It also provides small inline wrappers for taking and dropping runtime PM references on a `pvr_device`.

## Important APIs, types, and functions
- Watchdog: `pvr_watchdog_init()` and `pvr_watchdog_fini()`.
- Device loss and state: `pvr_device_lost()` and `pvr_power_is_idle()`.
- PM callbacks: `pvr_power_device_suspend()`, `pvr_power_device_resume()`, and `pvr_power_device_idle()`.
- Reset and references: `pvr_power_reset()`, inline `pvr_power_get()`, and inline `pvr_power_put()`.
- Power domains: `pvr_power_domains_init()` and `pvr_power_domains_fini()`.
- Platform operations: `struct pvr_power_sequence_ops`, `pvr_power_sequence_ops_manual`, and `pvr_power_sequence_ops_pwrseq`.

## Control flow
The header itself only contains inline `pvr_power_get()` and `pvr_power_put()`, which translate a `pvr_device` into its DRM device and call `pm_runtime_resume_and_get()` or `pm_runtime_put()`. The declared sequencing callbacks allow device-data tables to select manual clock/reset control or generic power-sequencer control.

## State and persistence
No standalone state is defined here. The declared APIs operate on persistent `pvr_device` power, firmware, watchdog, and domain fields. `struct pvr_power_sequence_ops` persists in platform/device-data tables as function pointers.

## Dependencies and integration points
Includes `pvr_device.h`, mutex declarations, and runtime PM declarations. It is used by MMU flush recovery, firmware paths, PM ops, probe/remove domain setup, and queue/reset integration. The inline helpers centralize runtime PM reference handling for call sites that need the GPU powered.

## Risks
Because the runtime PM wrappers are inline and minimal, callers must handle errors and balance references correctly. Any signature change affects multiple subsystems. Platform power operation implementations must preserve the `init`, `power_on`, and `power_off` contract or runtime PM and reset recovery will fail.

## Test signals
Build coverage catches declaration drift. Runtime validation comes from balanced PM reference tests, suspend/resume, reset, watchdog initialization/finalization, and platform probe on both manual and pwrseq-backed devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_power.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_queue.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_queue.c

## Purpose
Implements PowerVR per-context job queues on top of `drm_gpu_scheduler`. It creates firmware queue contexts and CCCBs, manages scheduler jobs and internal dependencies, converts native PowerVR fences into firmware UFO waits/updates, submits KCCB kicks, handles combined geometry/fragment submissions, processes firmware completion events, and coordinates queue stop/start around reset.

## Important APIs, types, and functions
- Public APIs: `pvr_queue_fence_is_ufo_backed()`, `pvr_queue_job_init()`, `pvr_queue_job_arm()`, `pvr_queue_job_cleanup()`, `pvr_queue_job_push()`, `pvr_queue_create()`, `pvr_queue_kill()`, `pvr_queue_destroy()`, `pvr_queue_process()`, `pvr_queue_device_pre_reset()`, `pvr_queue_device_post_reset()`, `pvr_queue_device_init()`, and `pvr_queue_device_fini()`.
- Scheduler backend: `pvr_queue_prepare_job()`, `pvr_queue_run_job()`, `pvr_queue_timedout_job()`, `pvr_queue_free_job()`, and `pvr_queue_sched_ops`.
- Fence helpers: `pvr_queue_fence_alloc()`, `pvr_queue_fence_init()`, `pvr_queue_cccb_fence_init()`, `pvr_queue_job_fence_init()`, `pvr_queue_fence_put()`, `to_pvr_queue_job_fence()`, and the job/CCCB `dma_fence_ops`.
- Submission helpers: `job_cmds_size()`, `job_count_remaining_native_deps()`, `pvr_queue_get_job_cccb_fence()`, `pvr_queue_get_job_kccb_fence()`, `pvr_queue_get_paired_frag_job_dep()`, and `pvr_queue_submit_job_to_cccb()`.
- Queue lifecycle helpers: `get_ctx_state_size()`, `get_ctx_offset()`, `init_fw_context()`, `pvr_queue_cleanup_fw_context()`, `reg_state_init()`, `pvr_queue_update_active_state_locked()`, `pvr_queue_signal_done_fences()`, and `pvr_queue_check_job_waiting_for_cccb_space()`.

## Control flow
Queue creation validates that the requested queue type matches the owning context type, computes firmware context-state size from device features, allocates a queue, initializes fence contexts and the CCCB, creates firmware register-state and timeline-UFO objects, writes the queue's common firmware-context fields into the parent context mapping, initializes a single-runqueue DRM scheduler and entity, and inserts the queue on the device idle list.

Job initialization rejects faulty contexts, selects the queue for the job type, verifies the command sequence can ever fit into the CCCB, initializes the DRM scheduler job, and preallocates CCCB, KCCB, and done fences so arm/push paths do not fail. `pvr_queue_job_arm()` exposes the scheduler finished fence. `pvr_queue_job_push()` records the last scheduled fence for combined-submit ordering, takes a job reference, and pushes to the entity.

`prepare_job()` initializes the internal done fence and returns one internal dependency at a time: CCCB space fence, KCCB slot fence, then paired-fragment dependency. CCCB dependencies attach the waiting job to `queue->cccb_fence_ctx.job` until firmware progress frees enough CCCB space. KCCB dependencies reserve a kernel CCB slot. For combined geometry/fragment work, the geometry job waits until the paired fragment job's earlier dependencies are gone, while the paired fragment job can return an already-initialized done fence after the geometry path has submitted both jobs.

`run_job()` acquires runtime PM references, writes firmware-side UFO wait commands for unsignaled native dependencies, writes the job command, then writes a UFO update command for the job done fence. Combined geometry/fragment submissions write both queues' commands and send a combined KCCB kick. Non-paired jobs send a normal KCCB kick. The returned parent fence is the internal done fence backed by the queue timeline UFO.

Firmware completion processing is driven by `pvr_queue_process()` under the device queue lock. It checks whether a CCCB-space waiter now fits and signals its CCCB fence, signals done fences whose seqno is covered by the timeline UFO value, releases job PM references, decrements in-flight counts, and moves queues between active and idle lists. Timeout handling stops the scheduler, reassigns parent fences to internal done fences for pending jobs, restores list membership and in-flight counts, optionally processes the queue, then restarts the scheduler.

Reset handling stops all idle and active queue schedulers before hard reset. Post-reset sets each timeline UFO to the current job-fence sequence, reattaches completed parent fences, marks contexts faulty when pending jobs did not complete, and restarts schedulers. Queue kill prevents new jobs by destroying the scheduler entity; queue destroy removes list membership, finalizes scheduler/entity state, waits for firmware context cleanup, releases firmware objects, destroys the CCCB and mutex, and frees the queue.

## State and persistence
Persistent per-queue state includes the DRM scheduler/entity, queue type, context pointer, active/idle list node, in-flight count, CCCB fence waiter, job fence timeline, firmware timeline UFO object and CPU mapping, last queued scheduled fence, CCCB, firmware register-state object, firmware context offset, and geometry callstack address. Device-level persistent state includes active and idle queue lists, their mutex, and the scheduler workqueue. Per-job queue state includes scheduler job fields, internal CCCB/KCCB/done fences, PM reference state, dependencies, paired job links, command buffer pointer/length, firmware command type, HWRT, and job IDs.

## Dependencies and integration points
Depends on DRM GPU scheduler and dma-fence, PowerVR CCCB/KCCB, context lifetime/refcounting, job objects, VM firmware memory context, firmware object allocation, Rogue firmware command structures, runtime PM through job helpers, and device feature queries. It integrates with ioctl job submission, context creation/destruction, firmware event/IRQ processing via `pvr_queue_process()`, and power reset via pre/post reset hooks.

## Risks
This file is concurrency-heavy. Races between firmware completion, scheduler stop/start, timeout handling, and queue active-list transitions can corrupt pending-list or in-flight accounting. CCCB waiter management assumes DRM scheduler entity serialization means only one job waits for CCCB space. Native fence dependency counting must match the number of firmware UFO wait commands or CCCB sizing is wrong. Combined geometry/fragment submission has strict ordering and same-context/HWRT assumptions. `pvr_queue_job_init()` can return `-ENOMEM` after `drm_sched_job_init()` without local cleanup unless caller follows the release path. Timeout handling is explicitly incomplete and mainly reassigns fences rather than recovering the GPU.

## Test signals
Useful signals include successful geometry, fragment, compute, transfer, and combined geometry/fragment submissions; correct fence signaling from timeline UFO values; CCCB-full jobs blocking and later unblocking; KCCB reservation pressure; no PM reference leaks after completion or timeout; context faulty state after reset with unfinished jobs; and clean queue destroy after in-flight work. Stress tests should cover many native dependencies, cross-queue UFO waits, scheduler timeouts, firmware reset during pending work, job completion racing with reset, and command sizes near CCCB limits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_queue.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_queue.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_queue.h

## Purpose
Defines the public queue data structures and API for PowerVR job scheduling. It exposes the per-queue state used by contexts, jobs, firmware event processing, and reset handling while keeping most scheduler/fence mechanics implemented in `pvr_queue.c`.

## Important APIs, types, and functions
- `struct pvr_queue_fence_ctx` holds a dma-fence context ID, sequence counter, and spinlock.
- `struct pvr_queue_cccb_fence_ctx` extends the base fence context with the single job waiting for CCCB space and a mutex.
- `struct pvr_queue_fence` wraps a `dma_fence`, the creating queue, and deferred release work.
- `struct pvr_queue` holds the DRM scheduler/entity, job type, owning context, active/idle node, in-flight counter, CCCB and job fence contexts, timeline UFO firmware object/mapping, last scheduled fence, CCCB, register-state object, firmware context offset, and callstack address.
- Declares queue job lifecycle, queue lifecycle, firmware event processing, reset hooks, and device-level init/fini functions.

## Control flow
The header has no executable control flow beyond declarations. The exposed lifecycle is device queue init, per-context queue creation, per-job init/arm/push/cleanup, firmware event processing through `pvr_queue_process()`, reset stop/start through device pre/post reset, queue kill/destroy, and device queue finalization.

## State and persistence
The structures declared here are persistent runtime state. `pvr_queue` objects live with a PowerVR context but can outlive handle destruction while jobs/fences hold references. Fence contexts persist for sequence allocation over the queue lifetime. The timeline UFO is firmware-visible state used to signal and wait for native queue fences.

## Dependencies and integration points
Includes DRM GPU scheduler, Linux workqueue declarations, `pvr_cccb.h`, and `pvr_device.h`; forward-declares `pvr_context`. The declarations are used by context management, job submission, power reset, firmware event processing, and other code that needs to test UFO-backed fences.

## Risks
The header exposes mutable queue internals, so changes to structure layout or locking expectations can affect several subsystems. The `pvr_queue_cccb_fence_ctx` comment documents an important invariant: only one CCCB-space waiter should exist because scheduler entity submission is serialized. Callers must respect queue lifetime and use kill/destroy in the intended order.

## Test signals
Build coverage catches structural and signature drift. Runtime coverage comes from context creation/destruction, job submit/cleanup, reset, firmware event processing, fence release work, and CCCB-space wait/unwait paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_queue.h -->
