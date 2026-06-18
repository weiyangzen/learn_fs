# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/prcm_mpu44xx.h

## Purpose
Declares OMAP44xx PRCM_MPU base address, instance offsets, clockdomain offsets, and CPU0/CPU1 register offsets for the local MPU PRCM block.

## APIs, Flow, And State
The key accessor macro is `OMAP44XX_PRCM_MPU_REGADDR(inst, reg)`, based on `OMAP4430_PRCM_MPU_BASE`. Constants identify OCP socket, device PRM, CPU0, and CPU1 instances plus registers such as `PM_CPUx_PWRSTCTRL`, `PM_CPUx_PWRSTST`, `RM_CPUx_CPUx_CONTEXT`, reset control/status, and clock control/status. It contains no state beyond generated address constants.

## Dependencies And Integration
Includes the shared PRCM MPU prototype header. Used by `prcm_mpu44xx.c`, SMP/PM code, and partitioned PRM access. It aligns OMAP4 CPU-local register layout with generated hwmod/clock/powerdomain data.

## Risks And Test Signals
Register offsets are generated hardware data; manual drift can break CPU idle, reset, or context-loss accounting. Test signals are CPU0/CPU1 low-power entry, hotplug/suspend behavior, and access to PRCM_MPU context registers without faults.
