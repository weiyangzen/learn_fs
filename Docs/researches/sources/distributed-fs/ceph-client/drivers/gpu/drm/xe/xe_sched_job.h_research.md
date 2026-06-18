<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sched_job.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sched_job.h

Purpose: declares scheduler job lifecycle, fence, query, snapshot, and dependency APIs plus small inline helpers.

Important APIs and constants: `XE_SCHED_HANG_LIMIT`, `XE_SCHED_JOB_TIMEOUT`, module init/exit, create/destroy/get/put, error setting, started/completed checks, arm/push, user-fence init, migration detection, snapshot capture/free/print, and `xe_sched_job_add_deps()`. Inlines expose job pointer from DRM scheduler job, job seqno, LRC seqno, and migration flush flag setter.

Dependencies and risks: callers must balance get/put and arm jobs before push. Tests should verify sequence number helpers after `xe_sched_job_arm()` and migration flush flags consumed by ring ops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sched_job.h -->
