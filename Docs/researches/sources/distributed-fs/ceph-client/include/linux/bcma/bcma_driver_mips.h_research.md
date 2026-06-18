# sources/distributed-fs/ceph-client/include/linux/bcma/bcma_driver_mips.h

## Purpose
Declares BCMA MIPS core register constants and minimal driver state for MIPS 74K/interrupt routing support.

## Important APIs, types, and functions
- `BCMA_MIPS_IPSFLAG` and IRQ masks/shifts describe routing of backplane flags to MIPS interrupt lines.
- MIPS 74K register offsets cover core control, exception base, BIST, interrupt masks, NMI mask, GPIO select/out/en, and clock control/status.
- `BCMA_MIPS_MIPS74K_INTMASK(int)` computes per-interrupt mask register offsets.
- `struct bcma_drv_mips` stores core pointer and setup flags.
- `bcma_cpu_clock()` returns CPU clock for the MIPS core.

## Control flow and state
Platform initialization configures interrupt routing and core setup once, then downstream code queries CPU clock. The setup flags prevent duplicate early/full initialization.

## State and persistence behavior
State is hardware register configuration plus runtime setup flags. Exception-base and interrupt masks affect CPU execution behavior immediately.

## Dependencies and integration points
Included by `bcma.h` and used by BCMA MIPS SoC platform code, interrupt setup, serial clock configuration, and watchdog/timer code.

## Risks
Wrong interrupt mask shifts can route device interrupts to the wrong CPU line. Clock calculation must match PMU/chipcommon state or serial/timer configuration will be wrong.

## Test signals
Boot supported MIPS BCMA SoCs, verify IRQ routing for multiple cores, confirm CPU clock and serial baud accuracy, and check setup idempotence.
