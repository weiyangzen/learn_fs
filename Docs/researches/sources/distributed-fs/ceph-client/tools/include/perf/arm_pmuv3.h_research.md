# sources/distributed-fs/ceph-client/tools/include/perf/arm_pmuv3.h

## Purpose
Defines the ARMv8 PMUv3 event-number and register-bit vocabulary used by perf tooling when decoding or programming Arm performance-monitoring counters. It is a tools-side mirror of kernel PMU definitions, not an implementation of counter access.

## Important APIs, Types, and Functions
Exports constants for architectural PMUv3 events, SPE events, AMU events, implementation-defined cache/TLB/bus/speculation events, PMCR, PMOVSR, PMXEVTYPER, event filters, PMUSERENR, PMMIR fields, and `ARMV8_PMU_MAX_COUNTERS`. Helper macros `PMEVN_CASE()` and `PMEVN_SWITCH()` let callers generate a switch over event counter indexes 0 through 30.

## Control Flow, State, and Persistence
There is no runtime state or persistence. The only executable behavior is macro expansion: `PMEVN_SWITCH(x, case_macro)` dispatches to `case_macro(n)` for valid programmable counter numbers and otherwise emits `WARN(1, ...)` then `assert(0)`.

## Dependencies and Integration
Depends on `<assert.h>` and `<asm/bug.h>` for invalid-index handling plus `BIT()`/`GENMASK()` style kernel macros supplied through included tooling headers. It integrates with perf/arm64 PMU support and any decoder that must keep event ids aligned with the Arm architecture.

## Risks and Test Signals
Risks are ABI/spec drift, missing counters above 30 because the cycle counter is separate, and invalid assumptions if future Arm PMU revisions add fields not represented here. Test signals include compile checks for macro availability, perf event encoding tests on Arm systems, and invalid-index tests around `PMEVN_SWITCH()`.
