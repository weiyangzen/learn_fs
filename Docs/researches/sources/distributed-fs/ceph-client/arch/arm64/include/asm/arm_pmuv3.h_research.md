## sources/distributed-fs/ceph-client/arch/arm64/include/asm/arm_pmuv3.h

### Purpose
Provides ARM PMUv3 system-register accessors and feature helpers for perf and virtualization code.

### Important APIs, Types, And Functions
Important helpers include `read_pmevcntrn`, `write_pmevcntrn`, `write_pmevtypern`, `read_pmevtypern`, `read_pmmir`, `read_pmuver`, `pmuv3_has_icntr`, `write_pmcr`, `read_pmcr`, `write_pmselr`, cycle/instruction counter accessors, counter enable/interrupt/filter helpers, `read_pmceid0/1`, `pmuv3_implemented`, `is_pmuv3p4`, `is_pmuv3p5`, and `is_pmuv3p9`.

### Control Flow
Counter-numbered helpers use `PMEVN_SWITCH()` to compile to direct register accesses for supported event counter indices. Feature helpers read ID registers and compare PMU version fields.

### State, Persistence, And Dependencies
State lives in PMU system registers. Dependencies include KVM host definitions for counter-switch macros, cpufeature extraction, and sysreg helpers.

### Integration Points
Used by ARM64 perf PMU drivers, KVM PMU virtualization, and user-access control for PMU counters.

### Risks
Register selection and PMU version comparisons must track ARM architectural revisions. Incorrect user enable or filter writes can expose counters incorrectly or misattribute events. KVM dependencies must not create include cycles.

### Test Signals
Run perf tests across PMUv3 revisions, KVM guest PMU tests, instruction counter support checks, user-access enable/disable tests, and compile coverage for PMUv3p4/p5/p9 feature logic.
