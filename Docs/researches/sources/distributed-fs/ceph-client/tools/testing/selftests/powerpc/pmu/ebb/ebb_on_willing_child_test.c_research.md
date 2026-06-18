<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/ebb_on_willing_child_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/ebb_on_willing_child_test.c

Purpose: Tests EBB operation with a child process that cooperates in setting up/running the EBB workload.

Important APIs and types: Defines `victim_child`, `ebb_on_willing_child`, and `main()`.

Control flow: The child waits for parent coordination, then runs EBB setup/workload or allows parent-controlled event setup. The parent synchronizes and verifies successful EBB delivery/cleanup.

State and persistence: Uses child process and pipe synchronization state only.

Dependencies and integration points: Depends on `ebb_child`/pipe helpers, perf events, and EBB support.

Risks: Parent/child synchronization failures can look like PMU failures. Cleanup must kill/wait child on error.

Test signals: Pass indicates EBB works in the intended child coordination scenario.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/ebb_on_willing_child_test.c -->
