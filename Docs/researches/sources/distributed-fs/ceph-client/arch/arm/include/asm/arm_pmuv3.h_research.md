<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/arm_pmuv3.h -->
# sources/distributed-fs/ceph-client/arch/arm/include/asm/arm_pmuv3.h

## Purpose
ARM32 PMUv3 CP15 accessor header for the perf ARM PMU driver and related virtualization stubs.

## Important APIs/types/functions
- CP15 register aliases for PMCR, PMCCNTR, PMCNTEN*, PMOVSR, PMSELR, PMXEVTYPER, PMXEVCNTR, PMUSERENR, PMINTEN*, PMCEID*, PMMIR, PMCCFILTR, and numbered event counters/types.
- Dynamic event accessors: `read_pmevcntrn()`, `write_pmevcntrn()`, `write_pmevtypern()`.
- PMU control helpers: `read_pmuver()`, `pmuv3_implemented()`, `is_pmuv3p4/p5/p9()`, `read_pmceid0/1()`, counter/filter/interrupt/user access writes.
- ARM32 stubs for instruction counter and KVM PMU hooks.

## Control flow
Inline helpers map generic PMUv3 operations to CP15 system-register reads/writes. PMU version is decoded from `CPUID_EXT_DFR0`; feature predicates interpret version numbers. PMCEID reads include extension registers for PMUv3.1+.

## State and persistence behavior
State is hardware PMU register state and perf event configuration. The header stores no data, but write helpers mutate counters, event selectors, filters, enable bits, interrupt enables, and overflow status.

## Dependencies and integration points
Depends on `asm/cp15.h`, `asm/cputype.h`, `PMEVN_SWITCH` macro definitions, and the ARM perf PMU driver. KVM hooks are stubs on ARM32 in this file.

## Risks and edge cases
Invalid event counter indices fall through `PMEVN_SWITCH` behavior and return zero/no-op. FEAT_PMUv3 instruction counter is not accessible for 32-bit here. PMU version handling treats IMP_DEF as not implemented.

## Test signals
Run `perf stat`, overflow interrupt tests, event enumeration, counter read/write tests, and builds across PMUv3 versions. Verify PMCEID extension reads on PMUv3.1+ hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/arm_pmuv3.h -->
