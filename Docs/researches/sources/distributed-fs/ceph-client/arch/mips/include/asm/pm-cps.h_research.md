# sources/distributed-fs/ceph-client/arch/mips/include/asm/pm-cps.h

## sources/distributed-fs/ceph-client/arch/mips/include/asm/pm-cps.h

### Purpose
`pm-cps.h` defines the public CPS power-management states and entry/support checks for MIPS systems with CM/CPC coherence and power control.

### Important APIs, Types, And Functions
The file exports `coupled_coherence`, `enum cps_pm_state` with `CPS_PM_NC_WAIT`, `CPS_PM_CLOCK_GATED`, `CPS_PM_POWER_GATED`, and `CPS_PM_STATE_COUNT`, plus `cps_pm_support_state` and `cps_pm_enter_state`.

### Control Flow
Callers first test whether a state is supported, then enter it. If `coupled_coherence` is true, all VP(E)s in a core must coordinate because CM/CPC only handles coherence/power at core granularity.

### State, Persistence, Dependencies, And Integration
State is CPU/core power and coherence state, not persisted storage. Dependencies are CPU feature macros such as MIPSr6, MT, and VP support. Integration is with cpuidle/suspend paths, coherent processing system code, and low-level CPC/CM drivers.

### Risks
Incorrect coupled-entry coordination can leave sibling VPEs incoherent or powered unexpectedly. Platform state support must reflect real hardware wiring, not just CPU capability bits.

### Test Signals
Build with MIPS MT and MIPSr6 variants; exercise cpuidle/suspend states on multi-VPE hardware, validate wakeup, interrupt delivery, cache coherency, and failure returns from unsupported states.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/pm-cps.h -->
