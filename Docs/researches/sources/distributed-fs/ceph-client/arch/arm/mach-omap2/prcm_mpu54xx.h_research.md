# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/prcm_mpu54xx.h

## Purpose
Defines OMAP54xx local MPU PRCM base, instance offsets, clockdomain offsets, and CPU0/CPU1 power/reset/clock register offsets.

## APIs, Flow, And State
The primary macro is `OMAP54XX_PRCM_MPU_REGADDR(inst, reg)`. Instances are split into OCP socket, device, PRM_C0/CM_C0, and PRM_C1/CM_C1. The header provides offsets for revision, reset status, fractional incrementer registers, CPU power state control/status, CPU reset control/status/context, clock state control, and `CM_CPUx_CPUx_CLKCTRL`. No mutable state is stored.

## Dependencies And Integration
Includes `prcm_mpu_44xx_54xx.h` and `common.h`; used by OMAP5 PRCM MPU consumers and by generated clock/powerdomain tables. It mirrors the OMAP4 programming model but with OMAP5 instance splits.

## Risks And Test Signals
The OMAP5 CPU PRM/CM split means cross-porting OMAP4 offsets directly would be unsafe. Test signals are OMAP5 CPU idle/resume, clockdomain control for CPU0/CPU1, and reset/context register access.
