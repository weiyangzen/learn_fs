<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/cpu_event_vs_ebb_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/cpu_event_vs_ebb_test.c

Purpose: Tests coexistence/conflict behavior between a non-pinned CPU perf event and an EBB event.

Important APIs and types: Defines `setup_cpu_event`, `cpu_event_vs_ebb`, and `main()`.

Control flow: The test starts a CPU-wide event, runs an EBB workload, then checks whether both can be scheduled or whether expected failures are reported without leaving child processes behind.

State and persistence: Only transient perf and child process state is used.

Dependencies and integration points: Depends on PMU event scheduling, `ebb_child`, and synchronization helpers from the PMU library.

Risks: Kernel PMU scheduling changes can alter whether events coexist. The test must distinguish expected scheduling failure from EBB malfunction.

Test signals: Pass validates non-pinned CPU event interaction with EBB task events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/cpu_event_vs_ebb_test.c -->
