# sources/distributed-fs/orangefs/src/io/job/job-time-mgr.c

Purpose: manages timeout buckets for outstanding jobs and cancels or refreshes timed-out operations.

Important APIs/functions: `job_time_mgr_init()` initializes the global bucket queue. `job_time_mgr_finalize()` removes all jobs from buckets and frees buckets. `job_time_mgr_add()` inserts a job into a bucket keyed by absolute expiration second via `__job_time_mgr_add()`. `job_time_mgr_rem()` removes a job from its bucket. `job_time_mgr_expire()` scans expired buckets and cancels BMI, Flow, or Trove jobs; flow jobs are refreshed if `FLOW_AMT_COMPLETE_QUERY` shows progress since the last check.

Control flow/state: global `bucket_queue` is sorted by `expire_time_sec` and protected by `bucket_mutex`. Each `time_bucket` owns a list of jobs expiring in the same second. Infinite timeout is a no-op. Flow timeout state persists in the job descriptor so progress can reset the timer.

Dependencies/integration: calls `job_bmi_cancel()`, `job_flow_cancel()`, `job_trove_dspace_cancel()`, and `PINT_flow_getinfo()`. Uses job descriptors from `job-desc-queue.h` and quicklist buckets.

Risks: `job_time_mgr_rem()` checks whether the bucket queue is empty before deleting the job from it, so a bucket with only this job will not be freed at removal time and can remain empty until expire/finalize. Expire asserts cancel returns `0`, making cancellation failures fatal. Re-adding a progressed flow occurs while iterating and after its old link was removed, which is intended but should be tested. Tests should cover bucket ordering, same-second grouping, infinite timeout, flow progress refresh, cancellation paths for BMI/Trove/Flow, removing the only job in a bucket, finalize cleanup, and concurrency around add/remove/expire.
