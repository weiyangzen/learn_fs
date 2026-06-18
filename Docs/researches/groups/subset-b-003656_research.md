# Research: subset-b-003656

Grouped source research for Qualcomm MSM DRM GPU/display support files. Each section preserves the original source path and is intended to be split into the source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/msm_gem_shrinker.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/msm_gem_shrinker.c

## Purpose
Implements memory-pressure reclaim for MSM DRM GEM buffers. It registers a Linux shrinker for GEM object pages and a vmap purge notifier for kernel virtual mappings, using the driver's GEM LRU buckets to reclaim buffers in increasing order of cost and disruption.

## Important APIs, Types, and Functions
- `msm_gem_shrinker_init()` allocates/registers `priv->shrinker` and registers `priv->vmap_notifier`.
- `msm_gem_shrinker_cleanup()` unregisters the vmap notifier and frees the shrinker.
- `msm_gem_shrinker_count()` reports reclaimable objects from `priv->lru.dontneed` and, when swap is available and eviction enabled, `priv->lru.willneed`.
- `msm_gem_shrinker_scan()` runs four reclaim stages: purge idle dontneed, evict idle willneed, wait/purge active dontneed when blocking is allowed, and wait/evict active willneed when swap and blocking are allowed.
- `with_vm_locks()` locks all GPUVM reservation objects associated with a GEM object before calling `msm_gem_purge()` or `msm_gem_evict()`.
- `msm_gem_shrinker_vmap()` responds to global vmap pressure by unmapping up to `vmap_shrink_limit` mappings across dontneed, willneed, and pinned LRUs.

## Control Flow
The count path is cheap and only reads LRU counts. The scan path builds a local reclaim-stage array, then calls `drm_gem_lru_scan()` for each enabled stage while decrementing `nr_to_scan`. Each object candidate is filtered for purgeability/evictability and current GPU activity. Active stages call `dma_resv_wait_timeout()` briefly before retrying purge/evict. Successful reclaim emits `trace_msm_gem_shrink()`. Vmap purge follows a separate notifier path and scans LRUs for `is_vunmapable()` objects, then calls `msm_gem_vunmap()`.

## State and Persistence
Persistent state lives in `msm_drm_private`: GEM LRU lists, shrinker pointer, and vmap notifier. The module parameter `enable_eviction` gates swappable buffer eviction. No on-disk state exists. The shrinker mutates GEM residency state by purging pages or evicting to swap, and the vmap notifier mutates CPU virtual mapping state.

## Dependencies and Integration Points
Depends on DRM GEM LRU helpers, dma-resv/ww locking, MSM GEM object helpers, Linux shrinker infrastructure, vmap purge notifier infrastructure, and tracepoints from `msm_gpu_trace.h`. It interacts with VM_BIND mappings by locking all GPUVM reservation objects associated with an object before page-table-affecting purge/evict work.

## Risks
Reclaim runs under memory pressure, so deadlock avoidance is central. The code avoids holding `priv->lru.lock` across page acquisition paths, does not do slow ww backoff inside `with_vm_locks()`, and skips candidates it cannot lock. Risks include incomplete reclaim under contention, excessive waiting in blocking reclaim, and correctness bugs if GEM/GPUVM reservation relationships change. Eviction depends on swap availability and `enable_eviction`.

## Test Signals
Useful signals include shrinker invocation under memory pressure, `trace_msm_gem_shrink`, `trace_msm_gem_purge_vmaps`, debugfs `msm_gem_shrinker_shrink()` under `CONFIG_DEBUG_FS`, no lockdep warnings during reclaim, and successful GPU operation after reclaiming idle and active buffers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/msm_gem_shrinker.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/msm_gem_submit.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/msm_gem_submit.c

## Purpose
Implements the legacy MSM GEM command submission ioctl. It converts userspace submit descriptions into DRM scheduler jobs, validates and pins GEM buffers, handles explicit and implicit synchronization, optionally patches relocations, creates userspace-visible fences, and pushes work to the selected GPU submit queue.

## Important APIs, Types, and Functions
- `msm_ioctl_gem_submit()` is the ioctl entry point and main control-flow owner.
- `submit_create()` allocates `struct msm_gem_submit`, allocates a hardware fence, initializes `drm_sched_job`, binds the queue, ring, context VM, pid, and submit identity.
- `submit_lookup_objects()` bulk-copies BO descriptors, validates flags, and looks up GEM handles under `file->table_lock`.
- `submit_lookup_cmds()` validates command descriptors and copies relocation arrays; VM_BIND contexts must provide direct IOVAs and no relocs or submit index/offset.
- `submit_lock_objects()` locks the VM reservation object and BOs with `drm_exec`; VM_BIND mode uses `drm_gpuvm_prepare_vm()` and `drm_gpuvm_prepare_objects()`.
- `submit_fence_sync()` adds implicit dependencies unless suppressed globally or per-BO.
- `submit_pin_objects()` maps and pins BOs in the context VM, stores `vm_bo` refs and IOVAs, and moves objects to the pinned LRU state.
- `submit_attach_object_fences()` attaches the scheduler fence to object reservations or, for VM_BIND, to the GPUVM reservation object and `vm->last_fence`.
- `submit_reloc()` maps command buffers CPU-side and patches relocation targets.
- `msm_submit_retire()` releases BO and GPUVM references after scheduler/GPU retirement.

## Control Flow
The ioctl validates pipe and flags, rejects unusable VMs, obtains the submitqueue, allocates an optional output fence fd, creates a submit, and serializes per-queue submission with `queue->lock`. It imports input sync-file fences, parses syncobj dependencies, parses post-dependencies, copies BO and command arrays, locks all relevant reservation objects, attaches implicit dependencies, pins objects, validates command stream bounds, and applies relocations for non-VM_BIND contexts. It arms the scheduler job, allocates or validates a userspace fence id in `queue->fence_idr`, creates a sync-file if requested, attaches reservation fences, validates the VM when using VM_BIND, dumps RD debug data, and pushes the job to the DRM scheduler. Error paths unwind fd allocation, syncobjs, locks, pins, submit references, and queue references.

## State and Persistence
Submit state is transient but reference-counted across ioctl, scheduler, ring in-flight list, and retirement. Persistent per-context state includes `queue->last_fence`, `queue->fence_idr`, scheduler entities, `ctx` accounting updated later on retirement, and `vm->last_fence` in VM_BIND mode. BO pin and LRU state persists until retire or error cleanup. No disk persistence exists.

## Dependencies and Integration Points
Integrates with `msm_gpu.h` structures, `msm_ringbuffer` scheduler backend, MSM GEM VMA/pin helpers, `msm_syncobj.c`, Linux `sync_file`, DRM scheduler, DRM GPUVM, dma-resv implicit sync, IDR fence lookup, RD debug capture, and GPU tracepoints. It feeds jobs to `msm_ringbuffer.c`, which eventually calls `msm_gpu_submit()`.

## Risks
Primary risk areas are userspace input validation, relocation bounds and ordering, correct lock/pin/unpin ordering under reclaim, fence-id IDR races, error-path reference balancing, and VM_BIND differences. The code intentionally avoids `copy_from_user()` while holding ww locks and separates page acquisition from LRU locking to reduce deadlock risk. VM unusable state is checked before accepting new jobs.

## Test Signals
Exercise submit with valid and invalid BO flags, handles, command sizes, relocations, sync-file in/out, syncobj timeline dependencies, explicit fence sequence numbers, disabled implicit sync, VM_BIND contexts, and closed contexts. Expected observability includes `trace_msm_gpu_submit`, fence-id waitability, RD dumps, no GEM ref leaks, no lockdep complaints, and correct scheduler retirement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/msm_gem_submit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/msm_gem_vma.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/msm_gem_vma.c

## Purpose
Implements MSM GPU virtual address management on top of DRM GPUVM. It supports both kernel-managed address spaces and userspace-managed VM_BIND address spaces, translates bind/unbind ioctls into GPUVM state-machine operations, schedules asynchronous page-table updates, logs VM operations for crash diagnosis, and marks contexts unusable after unrecoverable mapping failures.

## Important APIs, Types, and Functions
- `struct msm_vm_map_op`, `struct msm_vm_unmap_op`, and `struct msm_vm_op` describe physical MMU updates derived from higher-level GPUVM map/unmap operations.
- `struct msm_vm_bind_job` is a DRM scheduler job carrying parsed userspace bind ops, preallocated MMU page-table pages, queued MMU operations, pinned BO state, and a completion fence.
- `msm_gem_vm_create()` constructs `struct msm_gem_vm`, initializes DRM GPUVM and optional VM_BIND scheduler, sets up `drm_mm`, MMU lock, and optional operation log.
- `msm_gem_vm_close()` drains VM_BIND work and tears down remaining mappings on file close.
- `msm_gem_vma_new()`, `msm_gem_vma_map()`, `msm_gem_vma_unmap()`, and `msm_gem_vma_close()` manage individual GPU virtual areas.
- `msm_ioctl_vm_bind()` is the VM_BIND ioctl entry point.
- `vm_bind_job_lookup_ops()`, `vm_bind_prealloc_count()`, `vm_bind_job_lock_objects()`, `vm_bind_job_pin_objects()`, and `vm_bind_job_prepare()` are the staged validation/preparation pipeline.
- DRM GPUVM callbacks `msm_gem_vm_sm_step_map()`, `msm_gem_vm_sm_step_remap()`, and `msm_gem_vm_sm_step_unmap()` translate GPUVM state-machine results into actual `msm_vm_op` lists.
- `msm_vma_job_run()` executes queued map/unmap operations under `vm->mmu_lock`.

## Control Flow
For kernel-managed VMs, callers allocate VMAs through `msm_gem_vma_new()` and perform synchronous map/unmap through `msm_gem_vma_map()` and `msm_gem_vma_unmap()`. For userspace-managed VM_BIND, `msm_ioctl_vm_bind()` validates context and queue type, handles sync-file and syncobj dependencies, copies one or many bind ops, checks alignment/range/flags/PRR support, bulk-resolves GEM handles, estimates page-table preallocation, locks the VM and affected objects, pins pages and LRU state, preallocates page-table memory, then invokes the DRM GPUVM state machine. The state machine may generate unmaps, maps, remaps, and in-place flag updates. The job is armed, exposed through an optional sync-file and syncobjs, and pushed to the VM_BIND scheduler. `msm_vma_job_run()` applies queued unmaps even after a map failure but stops further maps; any failure makes the VM unusable.

## State and Persistence
`struct msm_gem_vm` stores the backing `msm_mmu`, DRM GPUVM, managed/unmanaged mode, `drm_mm` allocator, VM_BIND scheduler, `last_fence`, fault and unusable counters/state, optional pid, operation log, preallocation throttle state, and MMU lock. VMA state includes `mapped`, DRM GPUVA metadata, optional `drm_mm` node, and flags such as `MSM_VMA_DUMP`. VM_BIND jobs hold GEM object refs and queued op refs until run/free. State is in-memory and tied to DRM file/context lifetime.

## Dependencies and Integration Points
Integrates with DRM GPUVM/GPUVA, DRM scheduler, drm_exec, dma-fence/sync-file/syncobj, MSM GEM page/pin helpers, `msm_mmu` map/unmap/preallocation hooks, Adreno PRR support for MAP_NULL, RD/crash dump VMA flags, and submit path VM validation. The submit path rejects unusable VMs and uses `vm->last_fence` for VM_BIND synchronization.

## Risks
The risky parts are partial VM updates, object/VM reservation lock ordering, preallocation accounting, sparse mapping behavior, and asynchronous unmap lifetime. The code holds GEM references for async unmaps, marks VMs unusable after undefined partial state, throttles preallocated page-table pages, uses single-page granules for VM_BIND page tables, and treats in-place remaps specially to avoid page-table churn while GPU work may be active.

## Test Signals
Test single and batched VM_BIND map/unmap/map-null operations, invalid alignment and ranges, MAP_NULL without PRR support, sparse tiny mappings, remaps splitting a VMA into prev/next regions, in-place flag-only remap, fence fd and syncobj behavior, close-time teardown, preallocation throttle wakeups, and crash/fault paths that set `unusable` and print VM logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/msm_gem_vma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/msm_gpu.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/msm_gpu.c

## Purpose
Provides the common MSM GPU core: runtime power sequencing, register/IRQ setup, ringbuffer creation, command submission and retirement, hang detection/recovery, crash-state capture, devcoredump plumbing, performance counter sampling, and common GPU initialization/cleanup used by Adreno generation-specific implementations.

## Important APIs, Types, and Functions
- `msm_gpu_pm_resume()` and `msm_gpu_pm_suspend()` enable/disable regulators, clocks, AXI clock, and devfreq.
- `msm_gpu_hw_init()` invokes the generation-specific `gpu->funcs->hw_init()` with IRQ disabled when `needs_hw_init` is set.
- `msm_gpu_submit()` transitions the device active, initializes hardware, adds submit to the ring in-flight list, updates devfreq active state, calls the generation-specific submit hook, and arms hangcheck.
- `msm_gpu_retire()`, `retire_submits()`, and `retire_submit()` update fence contexts, release BO refs, update context elapsed/cycle accounting, and transition to idle.
- `hangcheck_handler()` detects lack of fence progress; `recover_worker()` captures diagnostics, advances fences, recovers hardware, and replays remaining submits.
- `msm_gpu_fault_crashstate_capture()` handles IOMMU fault crash dump capture.
- `msm_gpu_perfcntr_start()`, `msm_gpu_perfcntr_stop()`, and `msm_gpu_perfcntr_sample()` expose software and hardware perf sampling.
- `msm_gpu_create_private_vm()`, `msm_gpu_init()`, and `msm_gpu_cleanup()` manage common GPU resources.

## Control Flow
Initialization creates a kthread worker, initializes locks/work/timers, maps MMIO, requests IRQ, obtains clocks/regulators, initializes devfreq, creates the GPU VM, allocates memptrs, and creates ringbuffers. Runtime submit happens through the DRM scheduler backend in `msm_ringbuffer.c`, which calls `msm_gpu_submit()` under `gpu->lock`. Hardware completion updates ring memptr fences; IRQs call generation-specific handlers and schedule retirement. Hangcheck samples active ring fence progress and queues recovery if no progress. Recovery identifies the offending submit, marks fault counters and VM state, captures RD and devcoredump data, advances fences to unblock waiters, calls generation-specific recovery, and replays remaining submits unless their VM is unusable.

## State and Persistence
Persistent in-memory state is `struct msm_gpu`: rings, global VM, MMIO, clocks/regulators, worker, hangcheck timer, perf counters, devfreq, crashstate, active submit count, sysprof refcount, and fault counters. Per-context elapsed time and cycles are updated on retire. Crashstate persists until consumed/released by devcoredump. No on-disk persistence exists.

## Dependencies and Integration Points
Depends on generation-specific `msm_gpu_funcs`, MSM GEM submit/VMA/MMU/fence helpers, DRM scheduler ringbuffers, runtime PM, OPP/devfreq, Linux devcoredump, kthread workers, IRQ APIs, and tracepoints. It integrates with IOMMU page-table diagnostics by calling `msm_iommu_pagetable_params()` and `msm_iommu_pagetable_walk()` for fault captures.

## Risks
High-risk areas include recovery correctness, fence advancement on hangs, replaying submits after reset, power-management balance, crash capture under memory pressure, and synchronization between IRQ, worker, scheduler, and hangcheck timer. The code uses `gpu->lock`, `active_lock`, `submit_lock`, `perf_lock`, memalloc noreclaim sections, and runtime PM gets/puts to control those races.

## Test Signals
Signals include successful probe/remove, runtime suspend/resume, submit/retire tracepoints, correct fdinfo elapsed/cycle accounting, devcoredump content after forced hangs, IOMMU fault capture with ptes, no PM ref leaks, hangcheck recovery replaying later submits, and no stale in-flight submits after ring fence advancement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/msm_gpu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/msm_gpu.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/msm_gpu.h

## Purpose
Defines the common MSM GPU abstraction shared by Adreno-specific implementations, submit queues, ringbuffers, MMU/VMA code, devfreq, crash dumps, and debug paths. It is the central contract for GPU operations and per-file context state.

## Important APIs, Types, and Functions
- `struct msm_gpu_funcs` is the generation-specific virtual function table for params, hardware init, firmware upload, PM, submit/flush, IRQ, recovery, state dump, frequency control, VM creation, ring read pointer, progress detection, and sysprof setup.
- `struct msm_gpu` stores the common GPU instance: `drm_device`, platform device, funcs, SMMU private data, rings, locks, power resources, devfreq, workers, hangcheck, memptrs, crashstate, APRIV and relocation policy.
- `struct msm_context` stores per-DRM-file queues, VM, entity table, context labels, sysprof setting, memory/accounting counters, and cumulative elapsed/cycle stats.
- `struct msm_gpu_submitqueue` models a userspace queue with id, flags, ring, faults, last fence, IDR fence map, lock, refcount, and scheduler entity.
- `struct msm_gpu_state` and `struct msm_gpu_fault_info` describe crash/development diagnostic data.
- Inline helpers include `dev_to_gpu()`, `adreno_smmu_has_prr()`, `msm_context_is_vmbind()`, `msm_gpu_convert_priority()`, `msm_gpu_active()`, register read/write helpers, context/queue ref helpers, and crashstate get/put helpers.

## Control Flow
This header does not implement large flows, but its inline helpers shape them. `msm_gpu_convert_priority()` maps userspace priority to ring and DRM scheduler priority. `msm_gpu_active()` scans ring fences to determine active/idle transitions. Register helpers emit `trace_msm_gpu_regaccess` and perform 32-bit MMIO access. Context and queue helpers wrap krefs. Crashstate helpers serialize access with `gpu->lock`.

## State and Persistence
The types here define all durable in-memory GPU state for the driver: submitqueue lists, per-context VM ownership, ring arrays, power and devfreq state, fault counters, crash captures, and per-context accounting. State lifetime is controlled by krefs, DRM file close, GPU cleanup, and devcoredump release.

## Dependencies and Integration Points
Includes DRM scheduler, MSM GEM, MSM fence, ringbuffer, trace, devfreq, regulator, clock, interconnect, OPP, and Adreno SMMU private interfaces. It is included by submit, ringbuffer, devfreq, IOMMU, debug, and generation-specific GPU code.

## Risks
Since this header encodes shared contracts, changes can break ABI-facing behavior indirectly. Risks include priority mapping mismatches, stale context pointers avoided by `cur_ctx_seqno`, incorrect register width assumptions, sysprof PM/refcount imbalance, and VM_BIND mode checks being bypassed by direct `ctx->vm` access.

## Test Signals
Build coverage across all MSM GPU generations is essential. Runtime signals include correct priority-to-ring mapping, fdinfo stats, VM_BIND gating, crashstate lifecycle, tracepoint register access events, and clean context/submitqueue destruction under file close.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/msm_gpu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/msm_gpu_devfreq.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/msm_gpu_devfreq.c

## Purpose
Implements devfreq integration for MSM GPUs. It samples GPU busy cycles, drives OPP/frequency changes through devfreq, handles active/idle frequency transitions, provides temporary PM QoS boost, supports thermal cooling registration, and coordinates with GPU runtime suspend/resume.

## Important APIs, Types, and Functions
- `msm_devfreq_init()` initializes governor tuning, PM QoS boost request, devfreq device, cooling device, and hrtimer-backed idle/boost work.
- `msm_devfreq_cleanup()` unregisters cooling and removes QoS request.
- `msm_devfreq_resume()` and `msm_devfreq_suspend()` update suspended state, baseline busy counter/time, devfreq device state, and cancel delayed work.
- `msm_devfreq_active()` restores the shadow idle frequency and boosts after long idle periods.
- `msm_devfreq_idle()` queues a delayed clamp-to-idle operation.
- `msm_devfreq_boost()` raises the PM QoS minimum frequency for one polling interval.
- `msm_devfreq_target()`, `msm_devfreq_get_dev_status()`, and `msm_devfreq_get_cur_freq()` implement `devfreq_dev_profile`.

## Control Flow
At init, devfreq is enabled only when the GPU supplies `gpu_busy`. The simple_ondemand governor is tuned to ramp up at 50% utilization. While active, target frequency changes call a generation hook `gpu_set_freq()` or `dev_pm_opp_set_rate()`. When the GPU becomes idle, a short hrtimer queues work that records the current frequency as `idle_freq` and optionally clamps hardware to a minimum/zero target. When active again, the saved frequency is restored under the devfreq lock and a boost may be applied if the idle interval would otherwise hide real demand from the governor.

## State and Persistence
State lives in `gpu->devfreq`: devfreq handle, mutex, idle shadow frequency, boost QoS request, busy-cycle baseline, sampling time, idle time, hrtimer works, and suspended flag. Thermal cooling state is stored in `gpu->cooling`. No persistent disk state.

## Dependencies and Integration Points
Depends on Linux devfreq, OPP, PM QoS, devfreq cooling, hrtimer/kthread helpers from `msm_io_utils.c`, tracepoints, and generation-specific busy/frequency hooks from `msm_gpu_funcs`. GPU core calls active/idle/resume/suspend at submit/retire and PM boundaries.

## Risks
Risks include unit mismatch between devfreq Hz and PM QoS kHz, governor confusion during idle clamps, racing target callbacks with suspend or idle work, and stale busy-cycle baselines. The code uses `df->lock` and `df->devfreq->lock`, cancels hrtimer work on suspend, and keeps an idle shadow frequency to preserve governor state.

## Test Signals
Observe `trace_msm_gpu_freq_change`, devfreq sysfs current frequency, thermal cooling registration, correct active/idle transitions during bursty workloads, no QoS leak after boost expiry, stable runtime suspend/resume, and sane busy_time/total_time samples.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/msm_gpu_devfreq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/msm_gpu_trace.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/msm_gpu_trace.h

## Purpose
Defines MSM GPU tracepoints for submit lifecycle, frequency changes, GEM reclaim, suspend/resume, preemption, MMU preallocation cleanup, and register access. These tracepoints provide low-overhead observability for performance, power, memory pressure, and fault debugging.

## Important APIs, Types, and Functions
Trace events include `msm_gpu_submit`, `msm_gpu_submit_flush`, `msm_gpu_submit_retired`, `msm_gpu_freq_change`, `msm_gmu_freq_change`, `msm_gem_shrink`, `msm_gem_purge_vmaps`, `msm_gpu_suspend`, `msm_gpu_resume`, `msm_gpu_preemption_trigger`, `msm_gpu_preemption_irq`, `msm_mmu_prealloc_cleanup`, and `msm_gpu_regaccess`. The header sets `TRACE_SYSTEM drm_msm_gpu`, `TRACE_INCLUDE_FILE msm_gpu_trace`, and includes `trace/define_trace.h`.

## Control Flow
There is no runtime control flow beyond tracepoint expansion. Producers call generated `trace_msm_*` helpers from submit, retire, devfreq, shrinker, PM, preemption, IOMMU prealloc cleanup, and register access paths. Tracepoint payloads capture submit ids, pid, ring, seqno, timing, frequency, reclaim counts, preemption ring ids, preallocation counts, and register offsets.

## State and Persistence
Tracepoints do not persist driver state. They expose snapshots to ftrace/perf/tracefs consumers. Event fields are typed and formatted through `TP_STRUCT__entry`, `TP_fast_assign`, and `TP_printk`.

## Dependencies and Integration Points
Depends on Linux tracepoint infrastructure and types from `msm_gem_submit`/ringbuffer headers at inclusion sites. It is instantiated by `msm_gpu_tracepoints.c`. Register helpers in `msm_gpu.h` call `trace_msm_gpu_regaccess`, and several core modules call the other generated helpers.

## Risks
Risks are mostly build and trace ABI issues: changing field types or print formats can break tooling, missing include dependencies can fail trace generation, and high-frequency register access tracing can be noisy when enabled. Tracepoints must remain safe when passed partially initialized submit fields.

## Test Signals
Build with tracepoints enabled, inspect `/sys/kernel/tracing/events/drm_msm_gpu`, enable individual events, submit workloads, trigger devfreq and shrinker activity, and verify events carry expected ring, fence, frequency, and reclaim values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/msm_gpu_trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/msm_gpu_tracepoints.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/msm_gpu_tracepoints.c

## Purpose
Instantiates the tracepoints declared in `msm_gpu_trace.h` by defining `CREATE_TRACE_POINTS` in exactly one translation unit.

## Important APIs, Types, and Functions
The file includes `msm_gem.h`, `msm_ringbuffer.h`, defines `CREATE_TRACE_POINTS`, and includes `msm_gpu_trace.h`. It has no functions of its own.

## Control Flow
No runtime control flow. During compilation, tracepoint macros emit the storage and registration metadata for all `drm_msm_gpu` events.

## State and Persistence
The generated tracepoint descriptors are kernel static state. There is no driver-specific mutable state in this file.

## Dependencies and Integration Points
Must include the data-structure headers needed by tracepoint field assignments before including `msm_gpu_trace.h`. Other files include `msm_gpu_trace.h` without `CREATE_TRACE_POINTS` and call the generated trace helpers.

## Risks
Defining `CREATE_TRACE_POINTS` in multiple files would cause duplicate definitions; omitting this file would leave tracepoints unresolved. Include ordering can break if tracepoint expressions require incomplete types.

## Test Signals
Successful module/kernel link and visible `drm_msm_gpu` trace events in tracefs confirm this file is doing its job.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/msm_gpu_tracepoints.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/msm_io_utils.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/msm_io_utils.c

## Purpose
Provides small shared IO, clock, hrtimer-work, and interconnect helpers used by MSM GPU and display code.

## Important APIs, Types, and Functions
- `msm_clk_bulk_get_clock()` finds a clock in bulk data by either canonical name or legacy `<name>_clk`.
- `msm_clk_get()` tries canonical and legacy clock bindings, warning when a legacy binding is used.
- `msm_ioremap_mdss()` maps an MDSS-named memory resource through another platform device's devres.
- `_msm_ioremap()`, `msm_ioremap()`, `msm_ioremap_quiet()`, and `msm_ioremap_size()` map named or first memory resources and optionally return size.
- `msm_hrtimer_work_init()` and `msm_hrtimer_queue_work()` bridge hrtimer expiry to a `kthread_worker`.
- `msm_icc_get()` obtains interconnect paths from a device node, falling back to the parent MDSS node.

## Control Flow
Clock helpers perform lookup/fallback and return pointers or error pointers. IO mapping obtains platform resources, maps them with devm APIs, and reports errors unless quiet. The hrtimer callback queues the embedded kthread work and returns `HRTIMER_NORESTART`. Interconnect lookup first tries the child device and falls back to `dev->parent`.

## State and Persistence
No durable module state. Mappings, clocks, and interconnect paths are devres-managed by caller devices. `struct msm_hrtimer_work` stores timer, worker, and work item in caller-owned state.

## Dependencies and Integration Points
Used by GPU init for MMIO and clocks, devfreq for delayed boost/idle work, KMS pending timers, and display code for interconnect lookup. Depends on Linux platform resources, clk, IO mapping, hrtimer/kthread work, and interconnect APIs.

## Risks
Risks include silently accepting legacy clock names, mapping wrong resources if device tree names differ, hrtimer work queued after worker teardown if callers do not cancel, and fallback interconnect paths hiding device-tree omissions.

## Test Signals
Probe logs for clock fallback warnings, successful MMIO mapping on named resources, delayed work execution/cancellation in devfreq and KMS timers, and correct interconnect path acquisition on both child and MDSS-parent bindings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/msm_io_utils.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/msm_iommu.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/msm_iommu.c

## Purpose
Implements MSM MMU backends for display and GPU IOMMUs, including base domain mapping and Adreno per-process TTBR0 page tables used by GPU private VMs and VM_BIND. It also handles page-table preallocation, PRR MAP_NULL support, TLB flushing, fault routing, and crash diagnostic page-table walking.

## Important APIs, Types, and Functions
- `struct msm_iommu` wraps a parent `iommu_domain`, init lock, per-process page-table count, PRR page, and page-table slab cache.
- `struct msm_iommu_pagetable` wraps a child `msm_mmu`, io-pgtable ops, TLB ops, TTBR, ASID, page-size bitmap, and root page-table pointer.
- `msm_iommu_new()`, `msm_iommu_gpu_new()`, and `msm_iommu_disp_new()` create attached IOMMU domains and install GPU/display fault handlers.
- `msm_iommu_pagetable_create()` clones Adreno SMMU TTBR1 config into TTBR0 per-process page tables, optionally enabling custom alloc/free and PAGE_SIZE-only mappings for userspace-managed VM_BIND.
- `msm_iommu_pagetable_map()` and `msm_iommu_pagetable_unmap()` map/unmap SG tables or PRR pages using io-pgtable ops.
- `msm_iommu_pagetable_prealloc_count()`, `_allocate()`, and `_cleanup()` support async VM_BIND page-table page reservation.
- `msm_iommu_pagetable_params()` and `msm_iommu_pagetable_walk()` expose TTBR/ASID/PTE data for crash dumps.
- `msm_gpu_fault_handler()` and `msm_disp_fault_handler()` route faults to registered MSM handlers.

## Control Flow
Base IOMMU creation allocates a paging domain, applies quirks, attaches the device, and returns `msm_mmu` ops. GPU creation additionally creates a page-table cache from TTBR config, installs a fault handler, and enables SMMU stall if available. Per-process page-table creation obtains TTBR1 config from Adreno SMMU private hooks, builds TTBR0 config, optionally sets custom page-table allocation for VM_BIND, allocates io-pgtable ops, and on the first pagetable enables TTBR0 in the arm-smmu driver plus PRR page support. Map paths iterate SG entries, select the largest valid page size with `calc_pgsize()`, and roll back partial mappings on failure. Unmap loops over page sizes and flushes IOTLB. Destroy tears down TTBR0/PRR on the last pagetable.

## State and Persistence
State is in-memory: IOMMU domain attachment, page-table cache, active per-process pagetable count, PRR page, child page tables, preallocation arrays, root page-table memory, TTBR, and ASID. Fault handler callbacks are stored in `msm_mmu`. No disk persistence.

## Dependencies and Integration Points
Depends on Linux IOMMU, io-pgtable ARM LPAE, Qualcomm Adreno SMMU private hooks, kmem_cache, kmemleak, runtime PM for TLB flushes, and MSM MMU abstractions. It is consumed by GPU VM creation, display KMS VM creation, VM_BIND map/unmap, crashstate capture, and fault handling.

## Risks
High-risk areas include partial map rollback, sign-extension for 49-bit IOVAs, TTBR0 lifecycle across multiple page tables, PRR page allocation/cleanup, page-table preallocation over/under-counting, and fault handling while the device is runtime suspended. VM_BIND restricts to PAGE_SIZE to avoid unsafe block-split behavior.

## Test Signals
Test IOMMU probe/attach failures, GPU and display fault callbacks, VM_BIND sparse mappings, MAP_NULL PRR mappings, TLB flush with runtime PM inactive/active, forced map failures and rollback, devcoredump TTBR/PTE output, and clean TTBR0 disable when last private VM is destroyed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/msm_iommu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/msm_kms.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/msm_kms.c

## Purpose
Provides common KMS/display initialization and lifecycle glue for MSM display backends. It wires DRM mode config, IRQ installation, vblank enable/disable work, display IOMMU VM creation, suspend/resume helpers, shutdown, and post-init client/poll setup.

## Important APIs, Types, and Functions
- `msm_drm_kms_init()` is the main KMS initialization path.
- `msm_drm_kms_uninit()`, `msm_drm_kms_unregister()`, `msm_drm_kms_post_init()`, and `msm_kms_shutdown()` handle teardown, unregister shutdown, polling, client setup, and platform shutdown.
- `msm_crtc_enable_vblank()` and `msm_crtc_disable_vblank()` queue ordered work to backend vblank hooks.
- `msm_kms_init_vm()` creates a kernel-managed display GPUVM using the MDP or MDSS IOMMU device.
- `msm_kms_pm_prepare()` and `msm_kms_pm_complete()` wrap DRM mode config suspend/resume.
- Static IRQ helpers call backend `msm_kms_funcs` hooks.

## Control Flow
Initialization removes conflicting firmware framebuffers, initializes display snapshot support, calls the backend `priv->kms_init()`, sets DRM mode config callbacks, runs backend hardware init, moves panel connectors, creates per-CRTC FIFO event workers, initializes vblank, installs IRQ under runtime PM, and resets mode config. Vblank control is deferred through the ordered KMS workqueue so enable/disable happens in process context. Uninit flushes that workqueue before uninstalling IRQs, destroys event workers, finalizes polling/snapshots, uninstalls IRQ under runtime PM, and calls backend destroy.

## State and Persistence
State lives in `priv->kms` and `struct drm_device`: mode_config callbacks, IRQ requested flag, KMS workqueue, event threads, display snapshot state, and optional display VM. State is in-memory and device-lifetime scoped.

## Dependencies and Integration Points
Depends on DRM mode config, atomic helpers, vblank helpers, client setup, aperture removal, MSM display snapshot, MSM GEM VM/MMU, backend `msm_kms_funcs`, runtime PM, and kthread workers. It integrates with IOMMU fault handling by capturing a display snapshot once per attach on display faults.

## Risks
Risks include vblank work racing IRQ uninstall, event-thread teardown ordering, runtime PM imbalance around IRQ install/uninstall, missing IOMMU devices for display VM, and backend hook assumptions. The code flushes the workqueue before IRQ uninstall and rate-limits fault snapshots with `fault_snapshot_capture`.

## Test Signals
Signals include successful DRM registration, vblank enable/disable on each CRTC, IRQ install/uninstall, suspend/resume via mode_config helper, display IOMMU fault snapshot capture, clean shutdown after registration, and no workqueue activity after uninit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/msm_kms.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/msm_kms.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/msm_kms.h

## Purpose
Defines the common MSM KMS abstraction and helper structures used by MDP/DPU display backends. It describes backend operations, shared KMS state, commit timers, event threads, and top-level init/uninit entry points.

## Important APIs, Types, and Functions
- `struct msm_kms_funcs` is the backend vtable for hardware init, IRQ setup/handling, vblank, atomic commit lifecycle, format/pixel-clock helpers, destroy, snapshot, and debugfs.
- `struct msm_pending_timer` models per-CRTC async commit flush timers backed by `msm_hrtimer_work`.
- `struct msm_drm_thread` wraps per-CRTC kthread workers.
- `struct msm_kms` stores backend funcs, DRM device, connector/controller pointers, IRQ state, display VM, snapshot worker/mutex, commit locks, pending timers, workqueue, and event threads.
- `msm_kms_init()` initializes commit locks, backend funcs, ordered workqueue, and pending timers.
- `msm_kms_destroy()` destroys pending timers and workqueue.
- `for_each_crtc_mask` helpers iterate CRTCs by mask.

## Control Flow
The header mostly defines contracts. Backend implementations call `msm_kms_init()` during construction and `msm_kms_destroy()` during destruction. Top-level code in `msm_kms.c` calls the function-table hooks in specific init, IRQ, vblank, and atomic-commit phases. Stub functions return `-ENODEV` or no-op when `CONFIG_DRM_MSM_KMS` is disabled.

## State and Persistence
The `struct msm_kms` layout is the persistent in-memory display state across probe/runtime. It tracks commit synchronization, pending async work, IRQ ownership, display VM, attached interfaces, and snapshot state. No disk persistence.

## Dependencies and Integration Points
Depends on Linux clocks/regulators, DRM core types, MSM driver declarations, DSI/DP/HDMI forward declarations, atomic commit helpers, and hrtimer-work utilities. It is consumed by common KMS, DPU, MDP, and display interface code.

## Risks
Because backend hooks are broad, incompatible changes can break multiple display generations. Async commit semantics require careful balance between prepare/flush/wait/complete hooks, especially when multiple async updates accumulate before a vblank. Workqueue and timer lifetimes must match backend teardown.

## Test Signals
Build both with and without `CONFIG_DRM_MSM_KMS`. Runtime checks include backend init/destroy, async commit timer cleanup, CRTC-mask iteration correctness, vblank operations, and suspend/shutdown paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/msm_kms.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/msm_mdss.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/msm_mdss.c

## Purpose
Implements the top-level Qualcomm MDSS platform driver. It manages MDSS register mapping, clocks, interconnect bandwidth, reset, chained IRQ domain, UBWC decoder programming, runtime/system PM, child device population, and platform registration for MDP5/DPU display stacks.

## Important APIs, Types, and Functions
- `struct msm_mdss` stores device, MMIO, clocks, MDP5 flag, IRQ domain/enabled mask, UBWC config data, interconnect paths, and register bus bandwidth.
- `msm_mdss_init()` performs reset, allocation, UBWC/device match data lookup, MMIO map, ICC/clock parsing, IRQ domain setup, chained IRQ install, and runtime PM enable.
- `msm_mdss_enable()` votes minimum interconnect bandwidth, enables clocks, and programs UBWC static registers for supported decoder versions.
- `msm_mdss_disable()` disables clocks and drops ICC votes.
- `msm_mdss_irq()` dispatches top-level MDSS interrupt bits into a child IRQ domain.
- `msm_mdss_setup_ubwc_dec_*()` encode per-version UBWC programming.
- `mdss_probe()` initializes MDSS and populates child platform devices; `mdss_remove()` depopulates and destroys.
- `msm_mdss_register()` and `msm_mdss_unregister()` register/unregister the platform driver.

## Control Flow
Probe determines MDP5 compatibility, calls `msm_mdss_init()`, stores drvdata, then populates child nodes. Runtime resume calls `msm_mdss_enable()`, which sets ICC bandwidth, enables clocks, and programs UBWC registers when applicable. Runtime suspend calls `msm_mdss_disable()`. The chained IRQ handler reads `REG_MDSS_HW_INTR_STATUS`, dispatches each set bit to `generic_handle_domain_irq()`, and exits the parent chip. Remove depopulates children and destroys PM/IRQ-domain state.

## State and Persistence
Runtime state is in `struct msm_mdss`, including enabled IRQ mask and ICC/clock handles. Hardware state includes UBWC static/control registers and interconnect bandwidth votes. Match-table `reg_bus_bw` constants are static. No disk persistence.

## Dependencies and Integration Points
Depends on platform/device-tree probing, irqdomain/chained IRQ APIs, runtime PM, reset controller, interconnect, clocks, Qualcomm UBWC config, generated MDSS register headers, and child display drivers populated under MDSS. KMS backends rely on MDSS clocks/ICC/IRQ hierarchy being available.

## Risks
Risks include incorrect UBWC programming for new SoCs, missing or wrong `reg_bus_bw` match data, child IRQ masking races, ICC path absence, reset timing assumptions, and top-level clock dependencies that vary between MDP5 and DPU. The x1e80100 match includes a TODO placeholder for real bandwidth.

## Test Signals
Probe on each compatible SoC, runtime PM suspend/resume, child device population, child IRQ delivery, UBWC register values for compressed framebuffer formats, interconnect votes during enable/disable, and clean remove with IRQ domain and chained handler removed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/msm_mdss.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/msm_mmu.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/msm_mmu.h

## Purpose
Defines the MSM MMU abstraction used by GPU and display VM code. It provides a common function table for attaching, mapping, unmapping, destroying, fault handling, and VM_BIND page-table preallocation across GPUMMU, base IOMMU, and IOMMU page-table backends.

## Important APIs, Types, and Functions
- `struct msm_mmu_funcs` declares `detach`, `prealloc_count`, `prealloc_allocate`, `prealloc_cleanup`, `map`, `unmap`, `destroy`, and `set_stall`.
- `enum msm_mmu_type` distinguishes `MSM_MMU_GPUMMU`, `MSM_MMU_IOMMU`, and `MSM_MMU_IOMMU_PAGETABLE`.
- `struct msm_mmu_prealloc` tracks page-table pages reserved for async VM updates.
- `struct msm_mmu` stores funcs, device, optional fault handler callback and arg, type, and currently active prealloc pointer.
- `msm_mmu_init()` initializes the base fields.
- Factory/diagnostic declarations include `msm_iommu_new()`, `msm_iommu_gpu_new()`, `msm_iommu_disp_new()`, `msm_iommu_pagetable_create()`, `msm_iommu_pagetable_params()`, `msm_iommu_pagetable_walk()`, and `msm_iommu_get_geometry()`.

## Control Flow
This header defines dispatch contracts. Callers create an `msm_mmu`, then call `mmu->funcs->map()` and `unmap()` from VMA/VM_BIND paths. VM_BIND jobs set `mmu->prealloc` while running so the IOMMU page-table allocator can consume preallocated pages. Fault producers call the configured handler through backend code.

## State and Persistence
State is in-memory and backend-owned. The `prealloc` pointer is transient, protected by `msm_gem_vm::mmu_lock` according to comments. Fault handler pointers persist for the MMU lifetime.

## Dependencies and Integration Points
Consumed by `msm_iommu.c`, `msm_gem_vma.c`, `msm_gpu.c`, and `msm_kms.c`. Depends on Linux IOMMU and SG table types. It links KMS/GPU VM creation to the common VMA map/unmap code.

## Risks
Any backend must implement map/unmap semantics compatible with GEM VMA callers, especially partial failure behavior and preallocation cleanup. The transient `prealloc` pointer requires strict locking. Optional funcs need callers to guard feature availability.

## Test Signals
Compile all MMU backends, exercise GPU and display mapping, fault callbacks, VM_BIND preallocation paths, page-table diagnostic calls, and cleanup/detach flows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/msm_mmu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/msm_perf.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/msm_perf.c

## Purpose
Implements the `debugfs` `perf` file that streams GPU busy percentage and hardware performance counters for profiling when `CONFIG_DEBUG_FS` is enabled.

## Important APIs, Types, and Functions
- `struct msm_perf_state` tracks the DRM device, open state, sample counter, read mutex, output buffer, and next sample jiffies.
- `msm_perf_debugfs_init()` creates the `perf` debugfs file once per device.
- `msm_perf_debugfs_cleanup()` destroys state.
- `perf_open()` enforces single-open, starts GPU perf counters, and initializes sampling cadence.
- `perf_read()` refills and copies text samples to userspace.
- `refill_buf()` emits a header every 32 lines and otherwise waits for the next sample, samples counters, and formats output.
- `perf_release()` stops perf counters and clears open state.

## Control Flow
Opening the file requires a GPU and `gpu->lock`, rejects concurrent opens, and calls `msm_gpu_perfcntr_start()`. Reads serialize on `read_lock`; when the local buffer is exhausted, `refill_buf()` either writes a header or waits `SAMPLE_TIME` then calls `msm_gpu_perfcntr_sample()`. Release stops sampling through `msm_gpu_perfcntr_stop()`.

## State and Persistence
Debugfs state is stored in `priv->perf`. Sampling state is per-open but the file is single-open. GPU perf counter active state is owned by `msm_gpu.c`. No persistent disk state.

## Dependencies and Integration Points
Depends on debugfs, DRM minor infrastructure, MSM GPU perf counter APIs, and userspace reading `/sys/kernel/debug/dri/<minor>/perf`. It is a diagnostic interface only and compiles out without `CONFIG_DEBUG_FS`.

## Risks
Risks include single-open serialization, read blocking/interruption behavior, PM refs held while perf counters are active, fixed 256-byte buffer sizing versus counter names/counts, and stale `priv->gpu` on teardown. The driver uses mutexes and cleanup hooks to manage state.

## Test Signals
Open/read/release `perf`, verify headers and samples, concurrent open returns `-EBUSY`, interrupted reads return restart, counters stop on close, and cleanup works after debugfs removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/msm_perf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/msm_rd.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/msm_rd.c

## Purpose
Implements MSM debugfs RD capture streams used by freedreno/cffdump tooling. The `rd` file streams submitted command buffers, and `hangrd` captures offending submits during GPU hangs. Optional `rd_full` captures full buffer contents.

## Important APIs, Types, and Functions
- `enum rd_sect_type` defines the binary section protocol.
- `struct msm_rd_state` stores device, open flag, read/write mutexes, waitqueue, circular buffer, and storage.
- `msm_rd_debugfs_init()` creates `rd` and `hangrd`; `msm_rd_debugfs_cleanup()` frees them.
- `rd_open()` enforces single-open, resets FIFO, and writes GPU/chip id sections.
- `rd_read()` drains the circular buffer to userspace.
- `rd_write()` and `rd_write_section()` produce binary sections with blocking backpressure.
- `msm_rd_dump_submit()` serializes submit metadata, BO GPU addresses/contents, and command stream addresses.
- `snapshot_buf()` writes `RD_GPUADDR` and optional `RD_BUFFER_CONTENTS`.

## Control Flow
Userspace opens a debugfs file, causing the FIFO to reset and GPU id metadata to be emitted. Producers call `msm_rd_dump_submit()` under `gpu->lock`; it skips work if the stream is not open, serializes messages, task/fence identity, BO snapshots, and command-stream address sections. In VM_BIND mode it iterates all GPUVAs in the submit VM and honors `MSM_VMA_DUMP`; legacy mode iterates submit BOs and commands, snapshotting command buffers even when full BO dump is disabled. Readers block until FIFO data is available and wake producers as space opens.

## State and Persistence
State is transient debugfs memory in `priv->rd` and `priv->hangrd`. The circular buffer is only 512 bytes and blocks producers when full while open. `rd_full` is a module parameter controlling capture depth. Output persistence is up to userspace redirecting the stream.

## Dependencies and Integration Points
Depends on debugfs, waitqueues, circular buffer macros, MSM GEM vaddr helpers, GPU parameter hooks, submit structures, VM_BIND GPUVA iteration, and hang recovery in `msm_gpu.c`. `msm_gem_submit.c` dumps normal submits; hang recovery dumps offending submits.

## Risks
Risks include blocking producers if userspace opens but does not read, capturing large buffer contents with `rd_full`, object lifetime during snapshots, and VM_BIND iteration requiring the VM reservation lock. The code uses separate read/write mutexes, waitqueue backpressure, and checks `rd->open` while writing.

## Test Signals
Read `rd` while running workloads and verify cffdump can parse GPU/chip ids, BO addresses, command streams, and optional contents. Force a hang and inspect `hangrd`. Test VM_BIND dumps, `rd_full`, close while producer waits, and single-open rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/msm_rd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/msm_ringbuffer.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/msm_ringbuffer.c

## Purpose
Creates and owns MSM GPU ringbuffer instances and their DRM scheduler backend. It bridges scheduler jobs to `msm_gpu_submit()`, initializes hardware fences, unpins active BOs when jobs enter hardware, and destroys ring resources.

## Important APIs, Types, and Functions
- `msm_ringbuffer_new()` allocates a ring, creates its GEM command buffer, initializes the DRM scheduler, submit/preempt locks, in-flight submit list, and MSM fence context.
- `msm_ringbuffer_destroy()` finalizes the scheduler, frees fence context, releases the ring GEM object, and frees the ring.
- `msm_job_run()` is the DRM scheduler `run_job` callback.
- `msm_job_free()` is the scheduler `free_job` callback.
- Module parameter `num_hw_submissions` controls scheduler credit limit.

## Control Flow
When the scheduler runs a submit, `msm_job_run()` initializes the submit hardware fence from the ring fence context, unpins active BOs under the LRU lock because the job is now protected by the hardware fence, locks `gpu->lock`, no-ops the submit if its context is closed, calls `msm_gpu_submit()`, restores `nr_cmds`, unlocks, and returns a ref to the hardware fence. Ring creation allocates a write-combined GPU-readonly GEM buffer in the GPU VM, names it, sets pointers, associates memptrs, initializes the scheduler with priority queues, and creates a fence context backed by `memptrs->fence`.

## State and Persistence
Ring state includes command buffer BO and CPU pointer, start/end/cur/next pointers, DRM scheduler, in-flight submit list, memptrs and IOVA, fence context, hangcheck state, preemption lock/state, and last context sequence. It persists for GPU lifetime.

## Dependencies and Integration Points
Depends on DRM scheduler, MSM GEM kernel allocation, MSM fence contexts, GPU core submit/retire, LRU pin helpers, and structures from `msm_ringbuffer.h`. Generation-specific GPU submit hooks write commands into the ring and flush it.

## Risks
Risks include scheduler/hardware fence lifetime, restoring `nr_cmds` after closed-context no-op submission, BO pin accounting under LRU lock, command buffer pointer wrapping handled by header helpers, and teardown while jobs exist. Scheduler finalization in destroy must happen before freeing ring resources.

## Test Signals
Signals include scheduler job execution, hardware fence signaling, correct no-op behavior after context close, active BO unpinning, ring creation failure unwinding, `num_hw_submissions` limiting in-flight jobs, and clean GPU cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/msm_ringbuffer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/msm_ringbuffer.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/msm_ringbuffer.h

## Purpose
Defines ringbuffer memory layouts, statistics structures, the `struct msm_ringbuffer` state object, and small helpers used by GPU generation-specific command emission.

## Important APIs, Types, and Functions
- `rbmemptr()` and `rbmemptr_stats()` compute GPU IOVAs for fields inside shared ring memptrs.
- `struct msm_gpu_submit_stats` records CP cycle and always-on timestamps per completed submit.
- `struct msm_rbmemptrs` is shared CPU/GPU memory for read pointer, fence, A7xx BV fields, submit stats, TTBR0, and context id.
- `struct msm_cp_state` tracks CP IB state for progress detection.
- `struct msm_ringbuffer` stores ring BO, CPU pointers, scheduler, in-flight list, locks, IOVA, memptrs, fence context, hangcheck/preemption state, and context sequence.
- `OUT_RING()` writes one dword to the pending ring write pointer with wraparound.

## Control Flow
Generation-specific submit code writes commands with `OUT_RING()` into `ring->next`, then flushes by committing write pointers. GPU core and ringbuffer code use memptrs to observe read/fence progress, stats, and context state. Hangcheck uses `hangcheck_fence`, `hangcheck_progress_retries`, and `last_cp_state`.

## State and Persistence
The structures define GPU-lifetime ring state and the shared memory contract between CPU and GPU firmware/hardware. Memptrs are volatile because hardware writes them. Submit stats retain a circular set of 64 records indexed by sequence.

## Dependencies and Integration Points
Depends on DRM GPU scheduler, MSM driver/fence types, and constants from `msm_gpu.h`. Used by GPU core, Adreno command emission, tracepoints, crash dumping, and scheduler backend.

## Risks
Risks include hardware/firmware layout compatibility, volatile access assumptions, pointer wrap correctness, preemption serialization through `preempt_lock`, and stats index wrap. The fixed ring size is assumed power-of-two by creation code.

## Test Signals
Run command submission across ring wrap boundaries, verify fence/read pointer updates, submit stats timing, preemption paths, hangcheck progress detection, and crash dumps including ring data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/msm_ringbuffer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/msm_submitqueue.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/msm_submitqueue.c

## Purpose
Manages MSM per-context submit queues and scheduler entities. It creates/destroys queues, maps userspace priority to rings and DRM scheduler priorities, supports VM_BIND-specific queues, tracks fence IDR state and fault counts, closes queues on file release, and manages per-context sysprof state.

## Important APIs, Types, and Functions
- `msm_context_set_sysprof()` applies per-context profiling mode and balances GPU PM/sysprof refs.
- `__msm_context_destroy()` destroys scheduler entities, releases VM, labels, and context memory.
- `msm_submitqueue_create()` creates legacy or VM_BIND queues and inserts them into `ctx->submitqueues`.
- `msm_submitqueue_init()` creates the default queue id 0.
- `msm_submitqueue_get()`, `msm_submitqueue_put()`, and `msm_submitqueue_destroy()` manage queue refs.
- `msm_submitqueue_close()` removes all queues and closes the context VM.
- `msm_submitqueue_query()` returns queue fault counters.
- `msm_submitqueue_remove()` removes non-default queues.
- `get_sched_entity()` lazily creates per-context/per-ring/per-priority DRM scheduler entities.

## Control Flow
Queue creation validates GPU/context availability. VM_BIND queues require a VM_BIND context, priority zero, and use the VM's scheduler with an embedded scheduler entity. Non-VM_BIND queues validate priority through `msm_gpu_convert_priority()`, reject incompatible preemption flags, and reuse a per-context entity for FIFO behavior at a given ring/priority. The queue is refcounted, assigned an increasing context-local id under `queuelock`, initializes fence IDR and locks, and is appended to the context list. Close removes all queues, flushes VM_BIND entities, drops refs, and then closes the VM.

## State and Persistence
State is in `struct msm_context` and `struct msm_gpu_submitqueue`: submitqueue list, queue ids, scheduler entity table, fence IDR, queue locks, fault counters, sysprof mode, context labels, VM ref, and krefs. All state is per DRM file/context and in-memory.

## Dependencies and Integration Points
Depends on DRM scheduler entities, MSM GPU priority conversion, runtime PM for sysprof, VM close from `msm_gem_vma.c`, and submit/VM_BIND ioctl queue lookup. Fault counts are incremented by GPU recovery and queried via UAPI.

## Risks
Risks include scheduler entity sharing assumptions, queue removal racing submits, VM_BIND queue lifetime, sysprof ref/PM imbalance, and correct default queue semantics. The context close path relies on no more user ioctls, so it uses less locking while tearing down queues.

## Test Signals
Create/remove queues at many priorities, query faults, verify id 0 cannot be removed, create VM_BIND queues only in VM_BIND contexts, close files with queued jobs, check scheduler entity reuse/FIFO behavior, and test sysprof transitions 0/1/2 with PM refs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/msm_submitqueue.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/msm_syncobj.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/msm_syncobj.c

## Purpose
Implements MSM helpers for parsing DRM syncobj arrays from submit and VM_BIND ioctls. It adds syncobj dependencies to scheduler jobs, optionally resets input syncobjs after submission, parses output syncobjs, and installs completion fences or timeline points.

## Important APIs, Types, and Functions
- `msm_syncobj_parse_deps()` copies input `drm_msm_syncobj` descriptors, validates flags/timeline support, adds scheduler dependencies, and returns syncobjs that should be reset.
- `msm_syncobj_reset()` replaces selected syncobj fences with `NULL`.
- `msm_syncobj_parse_post_deps()` copies output descriptors, validates timeline support and flags, allocates fence chains for timeline points, and gets syncobj refs.
- `msm_syncobj_process_post_deps()` replaces binary syncobj fences or adds timeline points using the completed job fence.

## Control Flow
Input parsing allocates an array sized by `nr_in_syncobjs`, walks userspace descriptors at `in_syncobjs_addr + i * syncobj_stride`, copies up to the descriptor size, validates timeline and flags, adds the dependency to the DRM scheduler job, and stores refs for descriptors with `MSM_SYNCOBJ_RESET`. Output parsing similarly copies descriptors, rejects flags, allocates a `dma_fence_chain` for timeline points, and finds syncobj handles. Error paths release all acquired refs/chains. After a job is successfully queued, callers reset input syncobjs and process post dependencies with the job fence.

## State and Persistence
The helper returns temporary arrays owned by ioctl callers. Persistent state changes occur in DRM syncobj objects: dependencies affect scheduler job readiness, resets clear fences, and post-deps install fences or timeline points.

## Dependencies and Integration Points
Depends on DRM syncobj, DRM scheduler, dma-fence-chain, UAPI `drm_msm_syncobj`, and MSM error reporting. Used by both `msm_ioctl_gem_submit()` and `msm_ioctl_vm_bind()`.

## Risks
Risks include userspace stride/copy validation, timeline support gating, leaking syncobj refs or fence chains on partial parse errors, and ordering of reset/post-dep relative to job queuing. The code uses `__GFP_NORETRY` to avoid large allocation stalls.

## Test Signals
Test binary and timeline syncobjs, invalid handles, invalid flags, unsupported timeline points, reset-on-submit behavior, post-dep fence replacement, timeline point insertion, and error-path leak detection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/msm_syncobj.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/msm_syncobj.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/msm_syncobj.h

## Purpose
Declares the MSM syncobj helper interface shared by command submit and VM_BIND code.

## Important APIs, Types, and Functions
- `struct msm_syncobj_post_dep` stores an output syncobj ref, target timeline point, and optional `dma_fence_chain`.
- `msm_syncobj_parse_deps()` parses input dependency descriptors and adds them to a scheduler job.
- `msm_syncobj_reset()` clears selected input syncobjs.
- `msm_syncobj_parse_post_deps()` parses output syncobj descriptors.
- `msm_syncobj_process_post_deps()` installs a job fence into output syncobjs or timeline chains.

## Control Flow
The header defines declarations only. Callers parse input dependencies before arming/pushing a DRM scheduler job, parse post-dependencies before queuing, then after successful queueing reset requested input syncobjs and publish the output fence.

## State and Persistence
No state is stored by this header. It describes temporary helper data and persistent syncobj mutations performed by `msm_syncobj.c`.

## Dependencies and Integration Points
Includes DRM device, syncobj, and GPU scheduler headers. Used by `msm_gem_submit.c` and `msm_gem_vma.c`.

## Risks
The interface requires callers to free returned arrays, put syncobj refs, and free any unused `dma_fence_chain` entries. Misordered calls can expose fences too early or fail to reset input syncobjs.

## Test Signals
Build coverage for submit and VM_BIND users, plus runtime syncobj dependency/reset/post-dep tests through both ioctls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/msm_syncobj.h -->
