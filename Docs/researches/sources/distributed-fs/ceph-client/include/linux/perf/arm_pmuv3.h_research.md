<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/perf/arm_pmuv3.h -->
# sources/distributed-fs/ceph-client/include/linux/perf/arm_pmuv3.h

## Purpose
Defines ARM PMUv3 architectural event numbers, implementation-defined event numbers, register bit masks, event filter bits, user-access bits, PMMIR fields, and PMEVN switch helpers used by ARM PMUv3 drivers.

## Important APIs, Types, And Functions
- Counter indexes include `ARMV8_PMU_MAX_GENERAL_COUNTERS`, `ARMV8_PMU_CYCLE_IDX`, and `ARMV8_PMU_INSTR_IDX`.
- Architectural event constants cover software increment, cache/TLB refills and accesses, retired/speculative operations, branches, stalls, bus cycles, chain events, SPE/AMU/TRBE/trace/MTE extensions, and recommended implementation-defined events.
- PMCR masks include enable/reset/divider/export/debug/long-counter fields and `ARMV8_PMU_PMCR_MASK`.
- Overflow status masks include `ARMV8_PMU_OVSR_P`, `ARMV8_PMU_OVSR_C`, `ARMV8_PMU_OVSR_F`, and `ARMV8_PMU_OVERFLOWED_MASK`.
- Event type masks include `ARMV8_PMU_EVTYPE_EVENT`, `ARMV8_PMU_EVTYPE_TH`, and `ARMV8_PMU_EVTYPE_TC`.
- Filter bits include EL0/EL1/EL2/EL3 and secure/non-secure include/exclude controls.
- User enable bits include `ARMV8_PMU_USERENR_*` and `ARMV8_PMU_USERENR_MASK`.
- `PMEVN_SWITCH()` expands a runtime counter index into compile-time cases for PMEV0 through PMEV30 operations before including `<asm/arm_pmuv3.h>`.

## Control Flow
PMUv3 drivers map perf events to event numbers from this header, program PMXEVTYPER fields, configure PMCR/user/filter bits, check overflow status, and use `PMEVN_SWITCH()` to access per-counter registers through architecture macros. There is no runtime code in this header beyond generated switch macros.

## State And Persistence
State is hardware PMU register state: enabled counters, selected event codes, overflow flags, privilege filters, user access state, PMMIR capabilities, and current counter values. Constants must match the ARM architecture because perf event encodings and sysfs names depend on them.

## Dependencies And Integration Points
Integrates with ARM/arm64 PMU drivers, KVM PMU emulation, perf event maps, trace/SPE/TRBE code, and architecture-specific register accessors in `asm/arm_pmuv3.h`.

## Risks And Edge Cases
Risks include exposing event constants unsupported by a given PMU revision, mishandling arm64-only high bits on 32-bit ARM, off-by-one counter indexes, missing overflow bit 32 on arm64, invalid `PMEVN_SWITCH()` indexes, and privilege filter combinations that leak or hide events.

## Test Signals
Validate event maps for common architectural events, overflow handling for cycle and event counters, user access enable/disable, privilege filtering, 64-bit/long-counter behavior, PMEVN index warnings, PMUv3 revision-specific capability exposure, and KVM guest PMU event compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/perf/arm_pmuv3.h -->
