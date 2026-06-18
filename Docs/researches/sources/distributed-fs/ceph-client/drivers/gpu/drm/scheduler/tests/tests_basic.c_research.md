# sources/distributed-fs/ceph-client/drivers/gpu/drm/scheduler/tests/tests_basic.c

Purpose: KUnit basic and smoke tests for the DRM GPU scheduler using the mock backend. It covers ordinary submission, dependency chains, entity cleanup, cancellation, timeout handling, priority behavior, scheduler migration, and credit limits.

Important APIs and types: `drm_sched_basic_init()` and `drm_sched_timeout_init()` create mock schedulers with infinite or short timeout. Parameterized cases use `struct drm_sched_basic_params` and `KUNIT_ARRAY_PARAM`. Test helpers call `drm_mock_sched_entity_new()`, `drm_mock_sched_job_new()`, `drm_sched_job_add_dependency()`, `drm_sched_entity_set_priority()`, `drm_sched_entity_modify_sched()`, and `drm_mock_sched_advance()`.

Control flow: simple tests submit jobs, wait for scheduling, assert non-completion before advancement, then advance the mock timeline. Parameterized tests submit queues across one or more entities, optionally chaining each job to the previous job's finished fence. Cleanup tests destroy entities while work remains. Timeout tests let a job exceed `MOCK_TIMEOUT`; reset-skip tests mark `DONT_RESET` then manually complete. Priority and modify-scheduler tests mutate scheduling state while long queues drain.

State and persistence: state is per KUnit case. Scheduler/entity/job allocations are KUnit-managed except explicit scheduler finalization and entity destruction. The tests inspect mock job flags and fence errors as the result state.

Dependencies and integration: depends on the mock scheduler implementation, DRM scheduler core, KUnit, `linux/delay.h`, and DMA fence dependencies. The final `kunit_test_suites()` registers six suites.

Risks: several tests use timing (`HZ`, `usleep_range()`, job durations) and can be sensitive to slow or overloaded environments. `drm_sched_cancel` defines suite init/exit while also allocating/finalizing its own scheduler inside the test, which means the suite-private scheduler is separate from the one under assertion. Slow cases are marked with `KUNIT_CASE_SLOW` where they spin on priority or credit behavior.

Test signals: this file itself is the test signal. A healthy scheduler should pass all suites: `drm_sched_basic_tests`, `drm_sched_basic_timeout_tests`, `drm_sched_basic_cancel_tests`, `drm_sched_basic_priority_tests`, `drm_sched_basic_modify_sched_tests`, and `drm_sched_basic_credits_tests`.
