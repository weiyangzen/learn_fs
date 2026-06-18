<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/cycles_with_mmcr2_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/cycles_with_mmcr2_test.c

Purpose: Checks that MMCR2 freeze-control bits interact correctly with EBB cycles events.

Important APIs and types: Defines expected MMCR2 constants, `cycles_with_mmcr2()`, and `main()`.

Control flow: The test programs MMCR2, runs a cycles EBB workload, samples hardware state, and verifies expected MMCR2 bit patterns before/after enabling and freezing counters.

State and persistence: State is hardware PMU registers plus shared EBB stats.

Dependencies and integration points: Depends on SPR access through `ebb.h`, perf event setup, and CPU support for MMCR2 semantics.

Risks: MMCR2 layout is CPU-generation specific; expected constants must match supported processors.

Test signals: Pass means EBB setup preserves/uses MMCR2 freeze controls as expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/cycles_with_mmcr2_test.c -->
