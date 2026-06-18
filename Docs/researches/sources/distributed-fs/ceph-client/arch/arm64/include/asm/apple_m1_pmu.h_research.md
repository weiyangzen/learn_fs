## sources/distributed-fs/ceph-client/arch/arm64/include/asm/apple_m1_pmu.h

### Purpose
Defines Apple M1 implementation-defined PMU system register encodings and bit fields.

### Important APIs, Types, And Functions
Defines counter registers `SYS_IMP_APL_PMC0_EL1` through `SYS_IMP_APL_PMC9_EL1`; control registers `SYS_IMP_APL_PMCR0_EL1` through `PMCR4`; event selector registers `PMESR0/1`; status register `PMSR`; and bit masks such as `PMCR0_CNT_ENABLE_*`, `PMCR0_PMI_ENABLE_*`, `PMCR0_IMODE_*`, `PMCR1_COUNT_A64_*`, and `PMSR_OVERFLOW`.

### Control Flow
No runtime flow. PMU drivers include these constants and use generic system-register accessors to program Apple-specific counters.

### State, Persistence, And Dependencies
No local state. Hardware PMU register state persists in CPU system registers. Dependencies are `linux/bits.h` and `asm/sysreg.h`.

### Integration Points
Used by Apple M1 PMU/perf support to configure counters, interrupts, overflow status, and event selection.

### Risks
Implementation-defined register encodings must be exact. Wrong bit masks can misprogram counters, expose EL0 counting unexpectedly, or break PMU interrupt delivery.

### Test Signals
Run perf event tests on Apple M1 hardware, validate counter overflow interrupts, user/kernel counting filters, event selector programming, and cross-build non-Apple ARM64 configs.
