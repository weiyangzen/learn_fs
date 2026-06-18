<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/reg_access_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/reg_access_test.c

Purpose: Checks userspace access to PMU/EBB registers when EBB is enabled. It validates that expected SPR accesses are legal or faulting.

Important APIs and types: Defines `reg_access()` and `main()` and uses helpers such as `catch_sigill`, `write_pmc`, and EBB setup APIs.

Control flow: The test attempts selected SPR reads/writes before/after EBB event setup and verifies SIGILL behavior or success matches the kernel access-control contract.

State and persistence: No persistence; only PMU SPRs and event fds are touched.

Dependencies and integration points: Depends on powerpc SPR access rules, EBB support, and signal handling.

Risks: Hardware generation and kernel policy determine which registers are accessible; expected cases must stay aligned with the ABI.

Test signals: Pass confirms PMU register access control around EBB setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/reg_access_test.c -->
