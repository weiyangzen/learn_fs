# sources/distributed-fs/ceph-client/kernel/events/hw_breakpoint_test.c

Purpose: KUnit coverage for hardware breakpoint constraint accounting. It validates that generic slot reservation rejects impossible CPU/task combinations and restores state after unregistering breakpoints.

Important APIs/types/functions: `register_test_bp()` creates kernel perf breakpoint counters, `unregister_test_bp()` releases them, `get_test_bp_slots()` caches `hw_breakpoint_slots(TYPE_DATA)`, and `fill_one_bp_slot()`/`fill_bp_slots()` saturate requested dimensions. `TEST_EXPECT_NOSPC()` checks `-ENOSPC`; `TEST_REQUIRES_BP_SLOTS()` skips scenarios needing more debug registers.

Control flow: each case fills one or more breakpoint dimensions, attempts an extra registration that should fail, optionally unregisters an earlier breakpoint, and checks whether a CPU or task target can reuse capacity. `test_init()` skips when fewer than two CPUs are online or breakpoints are already in use. `test_exit()` unregisters all live events, stops the dummy task, and asserts `hw_breakpoint_is_used()` is false.

State and persistence: static `break_vars[]` provide watched addresses, `test_bps[]` stores live perf event pointers, and `__other_task` stores the lazily created kthread. No state persists after the KUnit suite; clean accounting is the final invariant.

Dependencies and integration points: depends on KUnit, online CPU iteration, kthreads, perf kernel counters, hardware breakpoint APIs, and architecture `hw_breakpoint_slots()`. It exercises public registration paths instead of private accounting functions.

Risks: cases are environment-sensitive and skip on insufficient CPUs, insufficient slots, or pre-existing breakpoint users. `MAX_TEST_BREAKPOINTS` bounds coverage on very large CPU systems. Failed cleanup can poison later cases.

Test signals: covers one CPU full, many CPUs independent, one or two tasks across all CPUs, task-on-one-CPU, mixed all-CPU and CPU-specific breakpoints, two tasks on one CPU, and accounting transitions between CPU-dependent and CPU-independent task breakpoints.
