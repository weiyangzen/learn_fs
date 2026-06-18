<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/ebb.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/ebb.h

Purpose: Public header for the EBB selftest support library. It defines shared state shape, constants, inline helpers, and exported helper prototypes.

Important APIs and types: Defines `PMC_INDEX`, `NUM_PMC_VALUES`, `COUNTER_OVERFLOW`, `struct ebb_state`, `pmc_sample_period`, `ebb_enable_pmc_counting`, and prototypes for handler setup, event init, PMU controls, diagnostics, child runner, SIGILL catcher, and PMC access.

Control flow: No executable control flow except tiny inline helpers. Tests include it to configure events and inspect shared `ebb_state`.

State and persistence: Declares external `ebb_state` and `sample_period`, which are process-global in `ebb.c`.

Dependencies and integration points: Depends on PMU `event.h`, powerpc SPR macros via included utilities, and `core_busy_loop` assembly.

Risks: Header/API drift breaks all EBB tests. Inline SPR manipulation assumes callers already verified EBB/PMU support.

Test signals: Compile coverage by every EBB binary plus runtime helper use validates the header contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/ebb.h -->
