<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/task_event_vs_ebb_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/task_event_vs_ebb_test.c

Purpose: Tests interaction between a non-pinned task perf event on a child and an EBB event.

Important APIs and types: Defines `setup_child_event`, `task_event_vs_ebb`, and `main()`.

Control flow: The test attaches a normal task event to a child, runs or attempts an EBB workload, and validates expected scheduling/coexistence outcomes with cleanup.

State and persistence: Transient child and perf state only.

Dependencies and integration points: Depends on `ebb.h`, perf task event scheduling, fork/wait, and pipe helpers.

Risks: PMU scheduler policy can affect whether both events run together. Child cleanup is important on early failure.

Test signals: Pass confirms non-pinned task event and EBB interaction remains stable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/task_event_vs_ebb_test.c -->
