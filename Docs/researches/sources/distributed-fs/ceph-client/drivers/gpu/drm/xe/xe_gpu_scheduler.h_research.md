<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gpu_scheduler.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gpu_scheduler.h

## Purpose
`xe_gpu_scheduler.h` declares Xe scheduler wrapper operations and inline helpers around DRM scheduler behavior.

## Important APIs, types, and functions
It declares init/fini, submission start/stop, TDR resume, and message add APIs. Inline helpers lock/unlock the message list, stop scheduler execution, queue immediate TDR, resubmit pending jobs, invalidate a job, find the first unsignaled pending job, initialize a scheduler entity, and alias entity fini to DRM scheduler fini.

## Control flow and integration points
Inline `xe_sched_resubmit_jobs()` walks DRM pending jobs, preserving replay restore behavior: once any pending job requires replay restore or an unsignaled job is found, it calls the backend `run_job()` on jobs in order. `xe_sched_first_pending_job()` returns the first pending job whose scheduler fence is not signaled. Backends use these helpers during reset, timeout, and recovery paths.

## State and persistence behavior
The header owns no state. It operates on `struct xe_gpu_scheduler`, DRM scheduler pending-job lists, and `struct xe_sched_job` flags such as `restore_replay`.

## Dependencies, risks, and test signals
Dependencies are Xe scheduler types, scheduler job conversion, and DRM scheduler APIs. Risks include resubmitting already-signaled jobs incorrectly, backend `run_job()` side effects during replay, and entity casting assumptions. Test signals include timeout recovery, job replay/restore, pending job iteration, scheduler entity lifecycle, and lockdep around message helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gpu_scheduler.h -->
