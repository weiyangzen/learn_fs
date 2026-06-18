# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/prcm_mpu7xx.h

## Purpose
Provides DRA7xx MPU_PRCM base, instance offsets, clockdomain offsets, and CPU-local power/reset/clock register offsets.

## APIs, Flow, And State
The `DRA7XX_PRCM_MPU_REGADDR(inst, reg)` macro maps MPU_PRCM physical addresses into L4 IO space. Instances cover OCP socket, device, PRM/CM for CPU0 and CPU1. Register offsets include revision, fractional incrementer numerator/denominator, CPU power state, reset control/status, context, clock state control, and CPU clock control. It is declarative only.

## Dependencies And Integration
Includes the shared 44xx/54xx PRCM MPU prototypes. The definitions are consumed by DRA7xx platform PM and clock code that shares the OMAP4+ register-access model.

## Risks And Test Signals
As generated data, the principal risk is stale DRA7xx offsets or naming mismatches in call sites. Test signals are DRA7xx CPU idle, SMP suspend/resume, and PRCM MPU MMIO access without BUGs or bus errors.
