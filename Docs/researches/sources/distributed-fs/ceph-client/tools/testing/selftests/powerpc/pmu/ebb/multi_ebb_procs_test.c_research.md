<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/multi_ebb_procs_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/multi_ebb_procs_test.c

Purpose: Runs multiple EBB child processes in parallel to test isolation and concurrent PMU use.

Important APIs and types: Defines SIGINT handler/action, `cycles_child`, `NR_CHILDREN`, `multi_ebb_procs`, and `main()`.

Control flow: `multi_ebb_procs()` forks several children running cycles EBB workloads, waits for completion, handles interrupt cleanup, and fails if any child reports EBB failure.

State and persistence: State is child PID list, signal action, and per-child EBB process state.

Dependencies and integration points: Depends on `ebb.h`, fork/wait, and PMU scheduling across processes.

Risks: Parallel PMU tests can be affected by system load and counter scarcity. Cleanup on interrupt is important to avoid stray busy children.

Test signals: Pass means separate processes can use EBBs concurrently without corrupting each other.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/multi_ebb_procs_test.c -->
