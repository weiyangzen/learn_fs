<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/pmc56_overflow_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/pmc56_overflow_test.c

Purpose: Verifies EBB delivery and accounting for PMC5/PMC6 overflows, not just PMC1-4.

Important APIs and types: Defines custom `ebb_callee`, `pmc56_overflow`, and `main()`.

Control flow: The test configures events routed to PMC5/PMC6, enables counting, runs work until overflows occur, and the handler counts/resets those PMCs before validation.

State and persistence: Uses shared EBB per-PMC counters.

Dependencies and integration points: Depends on hardware support for PMC5/PMC6 EBB overflow and local handler logic.

Risks: Some CPUs or event combinations may not route as expected. Overflow detection for higher PMCs must match SPR numbering.

Test signals: Pass indicates PMC5/PMC6 overflow handling is covered by EBB support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/pmc56_overflow_test.c -->
