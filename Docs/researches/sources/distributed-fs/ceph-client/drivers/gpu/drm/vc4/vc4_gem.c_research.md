# sources/distributed-fs/ceph-client/drivers/gpu/drm/vc4/vc4_gem.c

## Purpose
`vc4_gem.c` implements GEN_4 VC4 GEM render submission, job scheduling, dma-fence/syncobj integration, BO reservation/usecount handling, hang detection and recovery, hang-state capture, wait ioctls, and GEM madvise/purgeable state transitions. It is the central V3D userspace execution path for the VC4 render UAPI.

## Important APIs, Types, And Functions
- `vc4_queue_hangcheck()`, `vc4_hangcheck_elapsed()`, `vc4_reset_work()`, and `vc4_reset()` implement progress monitoring and reset scheduling.
- `struct vc4_hang_state`, `vc4_save_hang_state()`, `vc4_free_hang_state()`, and `vc4_get_hang_state_ioctl()` capture active job BOs and V3D registers for root-only hang diagnostics.
- `submit_cl()` writes V3D control-list current/end addresses and starts execution by writing the end register.
- `vc4_wait_for_seqno()`, `vc4_wait_seqno_ioctl()`, and `vc4_wait_bo_ioctl()` implement job seqno waits and BO reservation waits with timeout adjustment on interruption.
- `vc4_flush_caches()` and `vc4_flush_texture_caches()` clear V3D L2/slice caches before bin/render phases.
- `vc4_submit_next_bin_job()`, `vc4_move_job_to_render()`, and `vc4_submit_next_render_job()` schedule the hardware's binning thread 0 and render thread 1 queues.
- `vc4_attach_fences()` adds the job fence to read BO reservations and write BO reservations.
- `vc4_lock_bo_reservations()` uses `drm_exec` to lock BO reservations before fence attachment.
- `vc4_queue_submit()` assigns seqnos, initializes `struct vc4_fence`, installs output syncobjs, attaches fences, queues the job, and kicks the hardware if allowed by current render/perfmon state.
- `vc4_cl_lookup_bos()` looks up userspace BO handles, stores the object array, and increments VC4 BO usecounts.
- `vc4_get_bcl()` copies userspace bin CL, shader records, and uniforms; allocates the validated BCL BO; validates bin CL and shader records; and acquires binner memory if needed.
- `vc4_complete_exec()` releases fences, BO references/usecounts, temporary unref-list BOs, bin slots, binner BO, perfmon, V3D runtime PM, and the exec struct.
- `vc4_job_handle_completed()` and `vc4_job_done_work()` drain completed jobs from `job_done_list`.
- `vc4_submit_cl_ioctl()` is the main userspace submit path, validating flags/padding, acquiring PM, resolving BOs/perfmon/input sync, validating command lists, locking reservations, and queueing the job.
- `vc4_gem_init()` initializes job lists, locks, work/timer state, power/purgeable locks, fence context, and destruction action.
- `vc4_gem_madvise_ioctl()` implements `VC4_MADV_DONTNEED/WILLNEED` transitions and purgeability reporting.

## Control Flow
A userspace render submit enters `vc4_submit_cl_ioctl()`. The ioctl rejects non-GEN_4 devices, missing V3D, unknown flags, and invalid padding, then allocates `struct vc4_exec_info`, gets V3D runtime PM, initializes the unref list, looks up BO handles and increments BO usecounts, attaches a perfmon if requested, waits for an input syncobj fence unless it is from the same VC4 fence context, validates/copies the bin CL if present, builds the render CL through `vc4_get_rcl()`, locks all BO reservations, resolves the output syncobj, clears the stack-owned args pointer, and calls `vc4_queue_submit()`.

Queue submission runs under `job_lock`: it increments `emit_seqno`, initializes a dma fence with `vc4_fence_ops`, optionally replaces the output syncobj fence, attaches the fence to BO reservations, finalizes the `drm_exec` context, adds the job to `bin_job_list`, and starts binning immediately if the hardware queue is idle and perfmon compatibility allows it. Binning completion, render movement, render completion, and `finished_seqno` updates are driven by the IRQ code in other files; this file provides the queue operations and completion cleanup.

The hangcheck timer samples V3D current-address registers for the first bin/render jobs. If either address progresses, it rearms. If neither progresses for the interval, it schedules reset work, which captures hang state and power-cycles V3D through runtime PM before resetting IRQ/job state.

Madvise control looks up a BO, rejects unsupported/imported objects, locks the BO madv state, moves idle BOs into or out of the purgeable pool when transitioning between `WILLNEED` and `DONTNEED`, reports whether the BO was retained, and avoids resurrecting already purged objects.

## State And Persistence Behavior
Global GEM state is stored in `struct vc4_dev`: `emit_seqno`, `finished_seqno`, dma-fence context, bin/render/done job lists, `job_lock`, `job_wait_queue`, `job_done_work`, active perfmon, binner BO allocation bits, power lock/refcount, hangcheck timer/work, and purgeable pool. Each job persists as `struct vc4_exec_info` from ioctl allocation until completion cleanup. It owns references to BOs, temporary command-list BOs on `unref_list`, a fence, optional perfmon, binner BO slot/ref state, and validated command-list addresses.

Hang state persists in `vc4->hang_state` until the root-only ioctl consumes it or a newer state is discarded because one already exists. BO purgeability persists in each `struct vc4_bo` under `madv_lock` and in the global purgeable list/statistics.

## Dependencies And Integration Points
This file depends on Linux timers/workqueues, runtime PM, dma-fence arrays, signals, DRM exec/reservation/syncobj helpers, VC4 UAPI structs, V3D register definitions, validation helpers, BO helpers, V3D PM/bin BO helpers, IRQ reset, perfmon, and tracepoints. It integrates with:
- `vc4_fence.c` for dma-fence ops.
- `vc4_irq.c` for job completion, seqno advancement, IRQ reset, and queue progression.
- `vc4_validate.c` and `vc4_validate_shader.c` for command-list and shader safety.
- `vc4_bo.c` for BO allocation, usecounts, purgeable pool, labels, mmap, and tiling.
- `vc4_v3d.c` for runtime PM and binner BO resources.
- DRM syncobj/dma-reservation for explicit synchronization and implicit BO fences.

## Risks And Edge Cases
- Command submission is security-sensitive: userspace command lists, shader records, uniforms, and BO handles must be validated before hardware execution.
- Error paths in `vc4_submit_cl_ioctl()` must only call `drm_exec_fini()` after reservation locking succeeded; `vc4_complete_exec()` depends on partially initialized fields being either valid or NULL.
- BO usecount increments in `vc4_cl_lookup_bos()` have a custom rollback path because `vc4_complete_exec()` cannot know how many increments succeeded.
- Perfmon compatibility can block starting a new bin job while a render job with a different perfmon is active.
- Hang-state capture intentionally cannot guarantee BO contents remain stable after capture; it only keeps objects from being purged long enough to dump.
- Reset is scheduled from timer context because runtime PM reset can sleep.
- Fences are attached before hardware submission; if immediate completion races the ioctl, output syncobj replacement must already be visible.
- Madvise state has races with BO reuse/purge decisions controlled by `madv_lock`, usecounts, and purgeable list locks.

## Test Signals
- UAPI tests should cover submit with and without bin CL, invalid flags/padding, invalid BO handles, input syncobj waits, same-context syncobj skip, output syncobj signaling, wait seqno timeout/interruption, wait BO timeout adjustment, and madvise transitions.
- Fault-injection tests should cover allocation/copy_from_user/validation failures and ensure BO refs, usecounts, fences, PM refs, perfmon refs, and reservation locks are released.
- Hang tests should submit a stuck job, verify hangcheck reset, root hang-state retrieval, fence signaling, and subsequent queue recovery.
- Performance-counter tests should submit jobs with same/different perfmons and verify scheduling ordering and counter capture.
- Lockdep/KASAN/KCSAN are valuable around `job_lock`, `power_lock`, `madv_lock`, reservation locking, and job completion work.
