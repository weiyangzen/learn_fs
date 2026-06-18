# sources/distributed-fs/ceph-client/arch/powerpc/platforms/83xx/suspend.c

## Purpose
`suspend.c` is the MPC83xx Power Management Controller driver. It provides standby and deep-sleep suspend operations, PCI-agent power-management handling, wake event interrupt handling, and exports deep-sleep state to other drivers.

## Important APIs, Types, and Functions
`pmc_probe()` binds `"fsl,mpc8313-pmc"` or `"fsl,mpc8349-pmc"`, maps PMC/clock/SYSCR registers, requests the PMC IRQ, detects PCI host/agent role, optionally starts a PCI power-management kthread, and installs `mpc83xx_suspend_ops`. `mpc83xx_suspend_enter()` configures low-power mode, masks wake events, saves/restores SICR/SCCR for deep sleep, calls `mpc83xx_enter_deep_sleep()` or `mpc6xx_enter_standby()`, and handles PME enable. `fsl_deep_sleep()` exports whether the system is entering deep sleep.

## Control Flow, State, and Persistence
Global state tracks deep-sleep capability, current deep-sleep flag, PMC IRQ, mapped registers, saved registers, PCI-agent flags, IMMR base, PCI PM state, and a wait queue. PCI-agent state transitions wake a kernel thread that calls `pm_suspend()`.

## Dependencies and Integration Points
It integrates OF platform probing, PowerPC suspend core, PMC IRQs, FSL SOC IMMR helpers, low-level assembly, PCI power-management state, freezer-aware kthreads, and drivers that query `fsl_deep_sleep()`.

## Risks and Test Signals
Risks include PCI-agent races noted in comments, global singleton PMC state, wake mask errors, deep-sleep register restore gaps, and resource leaks on partial probe. Test signals are standby and mem suspend, wake by GPIO/PCI/USB/timer events, PCI-agent D-state transitions, `fsl_deep_sleep()` behavior during suspend, and repeated suspend cycles.
