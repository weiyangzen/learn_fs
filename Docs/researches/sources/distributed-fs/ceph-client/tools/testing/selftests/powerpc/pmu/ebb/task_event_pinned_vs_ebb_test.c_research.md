<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/task_event_pinned_vs_ebb_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/task_event_pinned_vs_ebb_test.c

Purpose: Tests conflict behavior between a pinned task perf event on a child and an EBB event.

Important APIs and types: Defines `setup_child_event`, `task_event_pinned_vs_ebb`, and `main()`.

Control flow: The test creates a child workload, attaches a pinned task event, then attempts/runs EBB setup and checks expected scheduling failure or coexistence behavior.

State and persistence: State is child PID, perf event fd, and pipe/wait coordination.

Dependencies and integration points: Depends on task-attached perf events, event pinning, and EBB scheduling rules.

Risks: Pinned task events can monopolize counters; expected behavior may vary with PMU counter availability.

Test signals: Pass validates kernel arbitration between pinned task events and EBB events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/task_event_pinned_vs_ebb_test.c -->
