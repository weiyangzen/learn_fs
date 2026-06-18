<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/regs_access_pmccext_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/regs_access_pmccext_test.c

Purpose: Tests PMU register access when the extended PMCC capability is involved. It is a focused access-control regression test.

Important APIs and types: Defines `regs_access_pmccext()` and `main()`.

Control flow: The test probes PMC access under conditions involving PMCC extension support, expecting allowed operations to succeed and disallowed ones to SIGILL/fail.

State and persistence: Only transient PMU and signal state is used.

Dependencies and integration points: Depends on kernel exposure of PMC access extension semantics and `ebb.h` helpers.

Risks: CPU feature availability controls whether the test is meaningful. Misdetecting support can create false failures.

Test signals: Pass means extended PMC access rules are enforced as expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/regs_access_pmccext_test.c -->
