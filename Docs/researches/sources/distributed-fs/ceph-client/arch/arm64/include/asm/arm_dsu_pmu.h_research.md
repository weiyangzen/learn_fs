## sources/distributed-fs/ceph-client/arch/arm64/include/asm/arm_dsu_pmu.h

### Purpose
Defines low-level register access helpers for ARM DynamIQ Shared Unit PMU cluster counters.

### Important APIs, Types, And Functions
Defines DSU PMU sysreg encodings such as `CLUSTERPMCR_EL1`, `CLUSTERPMCNTENSET_EL1`, `CLUSTERPMOVS*`, `CLUSTERPMSELR_EL1`, `CLUSTERPMINTEN*`, `CLUSTERPMCCNTR_EL1`, `CLUSTERPMXEVTYPER_EL1`, `CLUSTERPMXEVCNTR_EL1`, and `CLUSTERPMCEID*`. Helpers include `__dsu_pmu_read_pmcr`, `__dsu_pmu_write_pmcr`, `__dsu_pmu_get_reset_overflow`, counter select/read/write, event setup, cycle counter access, enable/disable, interrupt enable/disable, and `__dsu_pmu_read_pmceid`.

### Control Flow
Inline helpers select counters through `CLUSTERPMSELR_EL1`, access selected event registers, and use `isb()` after writes that must take effect before subsequent operations. Overflow read clears overflow bits by writing the read value back.

### State, Persistence, And Dependencies
State is in DSU PMU cluster system registers and counters. Dependencies include bitops, build bug checks, compiler/types, barriers, and sysreg helpers.

### Integration Points
Consumed by DSU PMU perf driver code to program cluster-level events and interrupts.

### Risks
Counter selection is shared state; missing barriers can read/write the wrong selected counter. Invalid PMCEID index intentionally triggers `BUILD_BUG()`. Interrupt and overflow clear masks must match hardware.

### Test Signals
Run perf stat/record on DSU events, overflow interrupt tests, counter enable/disable tests, multi-CPU cluster tests, and cross-build configs without DSU hardware.
