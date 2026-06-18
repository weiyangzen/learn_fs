<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/cpu_event_pinned_vs_ebb_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/cpu_event_pinned_vs_ebb_test.c

Purpose: Tests conflict behavior between a pinned CPU perf event and a task EBB event.

Important APIs and types: Defines `setup_cpu_event`, `cpu_event_pinned_vs_ebb`, and `main()`.

Control flow: It opens a pinned CPU event on a target CPU, forks or coordinates an EBB child, attempts to enable the EBB event, and checks that scheduling/conflict behavior matches expectations.

State and persistence: Perf fds and child process state are transient.

Dependencies and integration points: Depends on `ebb.h`, CPU-bound perf events, fork/wait, and event pinning semantics.

Risks: Results depend on PMU scheduling policy and available counters. Pinned conflicts are architecture/kernel policy sensitive.

Test signals: Pass confirms pinned CPU events and EBB events arbitrate consistently.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/cpu_event_pinned_vs_ebb_test.c -->
