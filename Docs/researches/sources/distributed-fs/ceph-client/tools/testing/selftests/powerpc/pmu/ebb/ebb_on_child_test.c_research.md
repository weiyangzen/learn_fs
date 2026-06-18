<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/ebb_on_child_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/ebb_on_child_test.c

Purpose: Tests attempting to create/use EBB events on a child process that is not explicitly cooperating.

Important APIs and types: Defines `victim_child`, `ebb_on_child`, and `main()`.

Control flow: The parent forks a child workload synchronized by pipes, attempts to attach/configure an EBB event against that child, and checks that kernel policy rejects or handles it as expected.

State and persistence: State is child PID, pipes, and perf event fd.

Dependencies and integration points: Depends on `ebb.h`, PMU lib pipe helpers, fork/wait, and perf task attachment semantics.

Risks: Expected behavior is policy-sensitive; tests must avoid leaving child processes running on failure.

Test signals: Pass confirms EBB task attachment to an unwilling child follows the kernel contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/ebb_on_child_test.c -->
