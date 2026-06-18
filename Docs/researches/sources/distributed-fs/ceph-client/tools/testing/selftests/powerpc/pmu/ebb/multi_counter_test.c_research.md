<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/multi_counter_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/multi_counter_test.c

Purpose: Tests EBB handling when multiple PMCs are enabled. It verifies overflows and counts across more than one counter.

Important APIs and types: Defines `multi_counter()` and `main()`.

Control flow: The test configures a group of EBB-capable events/counters, enables relevant PMC counting bits, runs the busy loop, then validates each enabled counter through shared EBB stats.

State and persistence: Uses `ebb_state.pmc_enable` and per-PMC accumulated counts.

Dependencies and integration points: Depends on EBB support for multiple PMCs, perf grouping, and handler `count_pmc` logic.

Risks: Counter routing and availability differ by CPU; the test assumes the selected events can coexist.

Test signals: Pass means the handler accounts multiple counter overflows correctly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/multi_counter_test.c -->
