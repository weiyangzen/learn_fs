<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/close_clears_pmcc_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/close_clears_pmcc_test.c

Purpose: Verifies that closing an EBB perf event clears PMU control state enough that later privileged PMC access faults as expected.

Important APIs and types: Defines `close_clears_pmcc()` and `main()`, using `catch_sigill`, `write_pmc1`, and event helpers.

Control flow: The test opens/enables an EBB event, closes it, then attempts direct PMC access under a SIGILL catcher to ensure permissions/control bits were cleared.

State and persistence: Local perf event state is opened and closed; no persistence.

Dependencies and integration points: Depends on `ebb.h`, perf event cleanup, and SIGILL behavior for unauthorized SPR access.

Risks: If hardware allows PMC writes for other reasons, interpretation changes. Cleanup ordering matters.

Test signals: Pass means perf close removes user PMC access enabled for EBB.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/close_clears_pmcc_test.c -->
