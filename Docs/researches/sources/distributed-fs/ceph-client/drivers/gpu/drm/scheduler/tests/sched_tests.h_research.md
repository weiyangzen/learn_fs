# sources/distributed-fs/ceph-client/drivers/gpu/drm/scheduler/tests/sched_tests.h

Purpose: shared header for DRM scheduler KUnit tests. It declares the mock scheduler, mock entity, and mock job structures, helper casts, lifecycle functions, and inline job helpers used by test cases.

Important APIs and types: `struct drm_mock_scheduler` embeds `struct drm_gpu_scheduler` and tracks a spinlock-protected job list plus a simulated hardware timeline. `struct drm_mock_sched_entity` embeds `struct drm_sched_entity`. `struct drm_mock_sched_job` embeds `struct drm_sched_job`, a completion, flags, hrtimer, duration/finish time, and a DMA fence. Public functions create/finalize schedulers, create/destroy entities, create jobs, and advance the mock timeline.

Control flow: tests include this header, create entities/jobs, then call `drm_mock_sched_job_submit()` which arms the DRM scheduler job and pushes it to the entity. Timing is controlled either with `drm_mock_sched_job_set_duration_us()` or with explicit `drm_mock_sched_advance()`. Waiting helpers observe the scheduler fence and mock completion.

State and persistence: no persistent state. The header defines job flag bits as the observable state contract between the backend and tests: `DONE`, `TIMEDOUT`, `DONT_RESET`, and `RESET_SKIPPED`.

Dependencies and integration: includes KUnit, atomics, completions, DMA fences, hrtimers, lists, and `drm/gpu_scheduler.h`. Cast helpers rely on embedded base objects and `container_of()`.

Risks: inline helpers assume the underlying mock backend has initialized `job->base.s_fence` before scheduled/finished waits. `drm_mock_sched_job_wait_scheduled()` asserts the job is not already done before waiting, which is correct for ordering tests but can fail if a duration is very short or the scheduler runs faster than expected.

Test signals: all scheduler tests use this header as their ABI. Any field layout or helper semantic change should be validated by the KUnit suites in `tests_basic.c`.
