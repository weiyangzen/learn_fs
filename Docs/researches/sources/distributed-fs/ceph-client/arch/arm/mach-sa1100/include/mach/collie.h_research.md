# sources/distributed-fs/ceph-client/arch/arm/mach-sa1100/include/mach/collie.h

## Purpose
This SA-1100 machine header collects board or SoC constants for `collie` users: GPIO assignments, IRQ lines, register offsets, memory windows, and helper declarations consumed by legacy board files and companion drivers.

## Important APIs, Types, and Functions
- Register/constant macro families: `COLLIE`(52), `_COL`(8), `__AS`(1); examples: `__ASM_ARCH_COLLIE_H`, `COLLIE_SCOOP_GPIO_BASE`, `COLLIE_GPIO_CHARGE_ON`, `COLLIE_SCP_DIAG_BOOT1`, `COLLIE_SCP_DIAG_BOOT2`, `COLLIE_SCP_MUTE_L`, `COLLIE_SCP_MUTE_R`, `COLLIE_SCP_5VON`, `COLLIE_SCP_AMP_ON`, `COLLIE_GPIO_VPEN`, `COLLIE_SCP_LB_VOL_CHG`, `COLLIE_SCOOP_IO_DIR`, `COLLIE_SCOOP_IO_OUT`, `COLLIE_GPIO_ON_KEY`, `COLLIE_GPIO_AC_IN`, `COLLIE_GPIO_SDIO_INT`, plus 45 more.

## Control Flow
There is no runtime control flow in this header. Including C files expand its macros into direct memory-mapped register accesses, IRQ-number calculations, board tests, and timing constants at compile time.

## State and Persistence Behavior
State is kernel-resident and hardware-facing: the file itself stores no runtime state beyond compile-time declarations. No user-space persistent files are written by this code.

## Dependencies and Integration Points
- Direct includes: `hardware.h`.
- Integrates with Linux IRQ domains/chained interrupt flow and board IRQ number definitions.
- Integrates with gpiolib lookup tables, GPIO chips, or board GPIO bit definitions.
- Integrates with clocksource/clock framework setup during early platform initialization.

## Risks
- IRQ number/routing mistakes show up as lost interrupts or interrupt storms rather than compile failures.
- headers are broadly included, so macro changes have a large blast radius across legacy board code.

## Test Signals
- Compile-test all in-tree users with `make ARCH=arm` for the affected SA-1100/SPEAr/shmobile/SoCFPGA configs; header regressions are best caught by building every including board file.
- Validate interrupt and GPIO paths with the attached devices that use the declared lines, watching `/proc/interrupts` and driver probe logs.

## Research Notes
- Read coverage: full file (3434 bytes, 95 lines).
- This is Linux ARM platform support code under `sources/distributed-fs/ceph-client`; it is kernel/architecture glue rather than distributed filesystem client logic.
