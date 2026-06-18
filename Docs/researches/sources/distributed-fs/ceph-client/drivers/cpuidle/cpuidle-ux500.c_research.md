<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpuidle/cpuidle-ux500.c -->
# sources/distributed-fs/ceph-client/drivers/cpuidle/cpuidle-ux500.c

## Purpose

`cpuidle-ux500.c` is the ST-Ericsson DB8500/ux500 ARM cpuidle driver. It registers a normal ARM WFI state plus `ApIdle`, a retention state entered only when all online CPUs are idle and PRCMU can safely manage GIC decoupling and wakeups.

## Important APIs, Types, And Functions

`ux500_idle_driver` defines state 0 as `ARM_CPUIDLE_WFI_STATE` and state 1 as `ApIdle`. `ux500_enter_idle()` uses the global `master` atomic and `master_lock` spinlock to select a last-man-in CPU. PRCMU calls include `prcmu_gic_decouple()`, `prcmu_is_cpu_in_wfi()`, `prcmu_copy_gic_settings()`, `prcmu_gic_pending_irq()`, `prcmu_pending_irq()`, and `prcmu_set_power_state()`.

## Control Flow

Probe enables ARM, RTC, and ABB wakeups through PRCMU and registers cpuidle. At idle entry each CPU increments `master`; if it is the last online CPU it attempts to become master, decouples GIC, verifies the peer CPU is already in WFI, copies interrupt state, checks no interrupts are pending, and requests `PRCMU_AP_IDLE`. All CPUs then execute WFI; on failure the master recouples GIC manually.

## State And Persistence Behavior

The driver maintains only global coordination state. Actual retention and GIC coupling state is PRCMU-managed. `master` is decremented on every exit, and `recouple` ensures manual recovery when the PRCMU did not take ownership.

## Dependencies And Integration Points

It depends on the dbx500 PRCMU MFD interface, ARM cpuidle WFI helpers, SMP CPU count/state, spinlocks, atomics, and the platform device named `db8500-cpuidle`.

## Risks And Test Signals

Risks include deadlocks or missed unlocks around `master_lock`, incorrect peer-WFI detection, interrupt races between GIC and PRCMU checks, and wakeup-source misconfiguration. Test with SMP idle workloads, RTC/ABB/ARM wakeups, forced pending interrupts during entry, and cpuidle statistics showing `ApIdle` use only when both CPUs can idle.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpuidle/cpuidle-ux500.c -->
