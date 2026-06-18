# sources/distributed-fs/orangefs/src/io/job/job-time-mgr.h

Purpose: declares the timeout-management API for job descriptors.

Important APIs: `job_time_mgr_init()`, `job_time_mgr_finalize()`, `job_time_mgr_add()`, `job_time_mgr_rem()`, and `job_time_mgr_expire()`.

Integration: included by the job subsystem to register outstanding jobs for timeout cancellation. Depends on `job_desc` and `JOB_TIMEOUT_INF` from job headers.

Risks/test signals: callers must remove jobs before deallocation or finalize must scrub links. Tests should check add/remove/expire ordering and no-op infinite timeouts.
