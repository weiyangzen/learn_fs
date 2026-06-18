# sources/distributed-fs/ceph-client/drivers/gpu/drm/scheduler/tests/mock_scheduler.c

Purpose: implements the mock GPU backend used by DRM scheduler KUnit tests. It allocates mock scheduler entities and jobs on the KUnit lifetime, exposes manual and timer-driven completion, and wires a `drm_sched_backend_ops` implementation into the core scheduler.

Important APIs and types: `drm_mock_sched_new()` wraps `drm_sched_init()` with all scheduler priorities, a very high credit limit, configurable timeout, and a single hang limit. `drm_mock_sched_entity_new()` initializes `drm_sched_entity` instances against the mock `drm_gpu_scheduler`. `drm_mock_sched_job_new()` initializes `drm_sched_job`, completion, list link, and an hrtimer. `mock_sched_run_job()`, `mock_sched_timedout_job()`, `mock_sched_free_job()`, and `mock_sched_cancel_job()` are the backend callbacks. Hardware fences are implemented with `dma_fence_ops` and the scheduler spinlock.

Control flow: tests create a scheduler, entities, jobs, arm jobs, and push them to entities. The scheduler calls `mock_sched_run_job()`, which initializes a hardware fence, queues the job in `sched->job_list`, and optionally schedules an hrtimer based on `duration_us`. Timer completion walks the ordered job list until it finds a non-duration or unfinished job. Manual completion uses `drm_mock_sched_advance()` to advance `cur_seqno` and signal eligible fences.

State and persistence: all state is in memory and KUnit-owned. `hw_timeline.context`, `next_seqno`, and `cur_seqno` model an ordered DMA fence timeline. Per-job flags record done, timeout, reset-skip, and no-reset intent. Pending jobs hold a fence reference while linked.

Dependencies and integration: depends on DRM GPU scheduler, DMA fences, hrtimers, completions, KUnit allocation/assertions, and spinlocks. It is consumed by `tests_basic.c` through `sched_tests.h`.

Risks: fence reference ownership is central: run paths take a list reference, completion paths must signal under the scheduler lock, timeout/free/cancel paths put references in complementary places. Timer completion assumes job list ordering by `finish_at`; inserting manual jobs with no duration stops timer-driven completion behind them. Timeout cleanup calls `drm_sched_job_cleanup()` directly, so tests relying on later free callbacks must align with scheduler semantics.

Test signals: KUnit tests validate scheduling, manual advancement, timed completion, cancellation on `drm_sched_fini()`, timeout behavior, reset skipping, priorities, scheduler migration, and credit-limit enforcement.
