<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/ebb_vs_cpu_event_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/ebb_vs_cpu_event_test.c

Purpose: Tests the reverse ordering of EBB event creation versus CPU-wide perf event creation.

Important APIs and types: Defines `setup_cpu_event`, `ebb_vs_cpu_event`, and `main()`.

Control flow: The test starts an EBB workload first, then attempts a CPU event and checks expected scheduling/conflict behavior, contrasting with the CPU-first tests.

State and persistence: Transient perf and child state only.

Dependencies and integration points: Depends on PMU scheduling, `ebb.h`, fork/wait, and event helper APIs.

Risks: Ordering-sensitive PMU constraints may differ by kernel/CPU. The test encodes expected arbitration behavior.

Test signals: Pass confirms event ordering does not leave EBB/CPU events in an inconsistent state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/ebb_vs_cpu_event_test.c -->
