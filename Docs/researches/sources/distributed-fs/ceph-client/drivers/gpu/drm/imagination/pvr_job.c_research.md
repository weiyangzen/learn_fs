# sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_job.c

## Purpose
Implements userspace job submission conversion into firmware commands, job object lifetime, sync dependency/signal preparation, reservation locking/fence updates, queue push, and geometry/fragment pairing for atomic render submission.

## Important APIs, types, and functions
- `pvr_submit_jobs()` is the ioctl-facing entry point for batch job submission.
- `create_job()` allocates and initializes one `pvr_job`.
- `pvr_job_fw_cmd_init()` dispatches to geometry, fragment, compute, and transfer command builders.
- `prepare_job_syncs()` and `prepare_job_syncs_for_each()` collect sync ops, add dependencies, arm jobs, and update signal fences.
- `prepare_job_resvs_for_each()`, `update_job_resvs_for_each()`, and `pvr_jobs_link_geom_frag()` handle reservation locking, fence publication, and render-pair linking.
- `pvr_job_put()` releases job resources through `pvr_job_release()`.

## Control flow
Submission rejects empty batches, copies the userspace job array, allocates per-job helper data, creates each job and copies sync-op arrays, flushes deferred MMU work, initializes a `drm_exec`, prepares sync dependencies/signals for each job, locks context and HWRT reservation objects, detects adjacent geometry->fragment pairs with an explicit scheduled-fence dependency, updates reservation fences, pushes jobs to queues, and finally publishes signal fences.

Job creation validates command stream presence, disallows HWRT handles for non-render jobs, allocates an ID in `pvr_dev->job_ids`, looks up the context and optional HWRT data, builds the FW command from the user stream through `pvr_stream_process()`, converts UAPI flags to FW flags, writes HWRT FW addresses for render jobs, and initializes the scheduler queue job.

Geometry/fragment pairing requires adjacent geometry then fragment jobs, same context, same HWRT, and a dependency from fragment to geometry scheduled fence. The geometry job is made to submit the fragment job atomically, the fragment KCCB fence is dropped, cross pointers are installed, and the fragment holds a reference on the geometry job.

## State and persistence
Each `pvr_job` persists in `pvr_dev->job_ids` with a kref, scheduler job base, type/id, optional paired job, CCB fences, done fence, context ref, HWRT data ref, command buffer, firmware CCB command type, and power-management reference flag. Reservation fences are attached to HWRT firmware objects as write usage for geometry and read usage for fragment. Sync signal fences are staged in an xarray until all push operations are past the must-succeed point.

## Dependencies and integration points
Depends on context lookup and queues, DRM scheduler, DRM exec/reservation locking, PVR stream definitions, sync object helpers, MMU flush, PM helpers, KCCB/CCCB queue code, HWRT data, GEM reservation objects, and UAPI job/flag layouts. Queue implementation consumes `pvr_job_submit()`/job fields after push.

## Risks
The point after reservation update is intentionally must-succeed because fences are externally visible. Pairing assumes adjacent jobs in the ioctl batch and specific dependency shape; otherwise geometry and fragment are scheduled independently. Error paths mutate `args->jobs.count` while unwinding partial work. Sync preparation arms jobs before later reservation locking, so cleanup must release all refs/fences correctly. Incorrect context type or HWRT validation would let incompatible FW commands reach queues.

## Test signals
Validate empty submission rejection, malformed command streams, invalid flags per job type, context-type checks, HWRT handle/index checks, sync dependency import and signal fence publication, MMU flush failure unwind, geometry/fragment pairing and non-pairing cases, reservation fence usage, queue push order, and job release removing IDs and PM refs.
