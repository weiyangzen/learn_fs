# sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_job.h

## Purpose
Defines the PowerVR scheduler job object, reference and power-management helpers, and submission/queue-facing job APIs.

## Important APIs, types, and functions
- `struct pvr_job` embeds `drm_sched_job` and stores kref, UAPI job type, ID, paired job, CCCB/KCCB/done fences, device/context pointers, firmware command buffer and length, FW CCB command type, optional HWRT data, and PM reference state.
- `pvr_job_get()` and `pvr_job_put()` manage job references.
- `pvr_job_get_pm_ref()` and `pvr_job_release_pm_ref()` attach/detach GPU power references to jobs.
- Declares queue/scheduler helpers `pvr_job_wait_first_non_signaled_native_dep()`, `pvr_job_non_native_deps_done()`, `pvr_job_fits_in_cccb()`, `pvr_job_submit()`, and ioctl entry `pvr_submit_jobs()`.

## Control flow
Inline PM flow is idempotent: acquiring a PM ref returns immediately if already held, otherwise calls `pvr_power_get()` and records `has_pm_ref`; release only calls `pvr_power_put()` when the flag is set. `pvr_job_get()` is a nullable kref increment.

## State and persistence
The job object holds all state needed between ioctl parsing, scheduler queuing, firmware submission, and completion. Paired geometry/fragment jobs hold cross references, and the PM ref flag persists until release or explicit PM release.

## Dependencies and integration points
Depends on DRM scheduler, GEM fence types, UAPI job types, PVR power management, and forward declarations for contexts, devices, files, HWRT data, and queues. The implementation coordinates with queue, sync, context, and HWRT subsystems.

## Risks
Job lifetime is shared between scheduler, queue code, sync fences, and pairing references. Any unbalanced `pvr_job_get()` or PM reference leaks jobs or power; premature release can leave scheduler/firmware with stale command pointers.

## Test signals
Build coverage for scheduler API changes, PM get/put balance tests, paired job lifetime tests, and submission completion tests that ensure `pvr_job_release()` cleans context/HWRT/queue resources are the key signals.
