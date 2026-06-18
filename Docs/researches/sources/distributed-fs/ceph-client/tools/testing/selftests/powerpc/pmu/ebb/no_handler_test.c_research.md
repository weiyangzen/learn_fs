<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/no_handler_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/no_handler_test.c

Purpose: Tests behavior when EBBs are enabled without installing a valid userspace handler.

Important APIs and types: Defines `no_handler_test()` and `main()`.

Control flow: The test configures an EBB event but deliberately avoids normal handler setup, runs enough work to trigger an EBB, and verifies the kernel reports or handles the missing handler as expected rather than corrupting state.

State and persistence: Transient perf and signal/process state only.

Dependencies and integration points: Depends on EBB exception delivery semantics and `ebb.h` helpers.

Risks: Expected failure mode is architecture-specific; unsafe handler address behavior must be contained by the test process.

Test signals: Pass confirms missing-handler EBB behavior is controlled and diagnosable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/no_handler_test.c -->
