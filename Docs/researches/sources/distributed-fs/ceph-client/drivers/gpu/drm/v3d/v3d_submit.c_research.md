# sources/distributed-fs/ceph-client/drivers/gpu/drm/v3d/v3d_submit.c

## Purpose

`v3d_submit.c` is the V3D userspace submission front end. It implements the CL, TFU, CSD, and CPU job ioctls; copies and validates user extension payloads; resolves GEM BO handles; attaches reservation and syncobj dependencies; creates scheduler jobs; sequences dependent jobs; and returns completion fences through legacy single syncobjs or the multi-sync extension.

## Important APIs, Types, and Functions

- `v3d_lookup_bos` and `v3d_lock_bo_reservations`: build `job->bo[]`, reserve each BO, and add implicit reservation dependencies to the scheduler job.
- `v3d_job_init`, `v3d_push_job`, `v3d_job_cleanup`, and `v3d_job_put`: common lifetime machinery around `drm_sched_job_init`, krefs, done fences, stats refs, and scheduler push.
- `v3d_get_extensions`: walks the user-provided extension chain and dispatches to multi-sync and CPU-job extension parsers.
- Multi-sync helpers: `v3d_get_multisync_submit_deps`, `v3d_get_multisync_post_deps`, `v3d_put_multisync_post_deps`, and output handling in `v3d_attach_fences_and_unlock_reservation`.
- CPU extension parsers: indirect CSD, timestamp query/reset/copy, and performance query/reset/copy parsers populate `struct v3d_cpu_job`.
- Ioctl entry points: `v3d_submit_cl_ioctl`, `v3d_submit_tfu_ioctl`, `v3d_submit_csd_ioctl`, and `v3d_submit_cpu_ioctl`.

## Control Flow

For GPU work, each ioctl validates padding and flags, optionally parses the extension chain, allocates queue-specific job structures, initializes their scheduler jobs against the calling file's scheduler entity, copies hardware register or CL address arguments, resolves BOs, reserves them, and pushes jobs under `v3d->sched_lock`. CL submission can create a bin job, a render job, and optionally a cache-clean job, wiring bin-to-render and render-to-clean dependencies with `drm_sched_job_add_dependency`. CSD submission similarly pushes CSD then cache-clean. TFU is a single hardware job.

CPU submission first allocates a `v3d_cpu_job`, requires exactly one CPU job extension, checks the submitted BO count against `cpu_job_bo_handle_count`, initializes a CPU scheduler job, and pushes it. For indirect CSD, the CPU job is followed by a dependent CSD job and a dependent cache-clean job; output fences are attached to the cache-clean job rather than the CPU job. Other CPU jobs return the CPU job's done fence.

Error handling unwinds scheduler job init, krefs, BO refs, syncobj refs, and reservations. Success attaches the job fence to each reserved BO as a write fence, unlocks reservations, replaces output syncobjs, and drops local krefs so scheduler completion owns the final references.

## State and Persistence Behavior

Submit-time state is mostly transient, but it creates persistent scheduler/fence effects: BO reservation fences remain on GEM objects, syncobjs are replaced with done fences, and perfmon references persist until job cleanup. `struct v3d_job` owns BO refs, stats refs, perfmon refs, `irq_fence`, `done_fence`, and scheduler state. CPU job query arrays persist until `v3d_cpu_job_free` frees syncobj and perfmon-id storage. Multisync output syncobj refs are consumed after fence replacement.

## Dependencies and Integration Points

The file depends on DRM GEM lookup/reservation helpers, DMA reservation objects, DRM syncobj dependencies, DRM GPU scheduler entities, V3D perfmon lookup, V3D CSD feature detection, BO types from `v3d_drv.h`, tracepoints, and scheduler callbacks in `v3d_sched.c`. Its ioctls are exposed by the V3D DRM driver and are expected by Mesa/userspace.

## Risks and Edge Cases

- Several CPU query parsers do little offset/stride bounds checking in this file; scheduler CPU handlers later write into mapped BOs.
- `v3d_copy_query_info` allocates `kperfmon_ids` using `sizeof(struct v3d_performance_query *)` rather than `sizeof(u32)`, wasting memory and potentially hiding type mistakes.
- Some syncobj dependency errors ignore `-ENOENT`, with TODO comments; behavior should be kept compatible but reviewed for silent dependency loss.
- Extension chains are trusted to terminate; cyclic user `next` pointers can repeatedly copy from user memory until fault or soft lockup unless generic ioctl guards exist elsewhere.
- Failure after indirect CSD setup has two reservation contexts to unwind; null `clean_job` assumptions in generic failure paths need care.

## Test Signals

Exercise all four ioctls with valid and invalid flags, padding, BO counts, multisync counts, missing syncobjs, dependency chains, perfmon conflicts, and CSD-on-non-CSD hardware. CPU query tests should cover timestamp reset/copy, performance reset/copy, indirect CSD rewrite, partial-copy flags, 32/64-bit writes, syncobj replacement, and error unwinding under fault-injected `copy_from_user`, GEM lookup, reservation, and scheduler dependency failures.
