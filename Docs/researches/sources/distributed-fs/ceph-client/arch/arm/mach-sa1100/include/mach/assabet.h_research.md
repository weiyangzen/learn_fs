# sources/distributed-fs/ceph-client/arch/arm/mach-sa1100/include/mach/assabet.h

## Purpose
This SA-1100 machine header collects board or SoC constants for `assabet` users: GPIO assignments, IRQ lines, register offsets, memory windows, and helper declarations consumed by legacy board files and companion drivers.

## Important APIs, Types, and Functions
- Register/constant macro families: `ASSABET`(53), `machine`(2), `__AS`(1); examples: `__ASM_ARCH_ASSABET_H`, `ASSABET_SCR_SDRAM_LOW`, `ASSABET_SCR_SDRAM_HIGH`, `ASSABET_SCR_FLASH_LOW`, `ASSABET_SCR_FLASH_HIGH`, `ASSABET_SCR_GFX`, `ASSABET_SCR_SA1111`, `ASSABET_SCR_INIT`, `machine_has_neponset`, `ASSABET_BCR_BASE`, `ASSABET_BCR`, `ASSABET_BCR_CF_PWR`, `ASSABET_BCR_CF_RST`, `ASSABET_BCR_NGFX_RST`, `ASSABET_BCR_NCODEC_RST`, `ASSABET_BCR_IRDA_FSEL`, plus 39 more.

## Control Flow
There is no runtime control flow in this header. Including C files expand its macros into direct memory-mapped register accesses, IRQ-number calculations, board tests, and timing constants at compile time.

## State and Persistence Behavior
State is kernel-resident and hardware-facing: in-memory locks serialize access to shared controller state. No user-space persistent files are written by this code.

## Dependencies and Integration Points
- Integrates with Linux IRQ domains/chained interrupt flow and board IRQ number definitions.
- Integrates with gpiolib lookup tables, GPIO chips, or board GPIO bit definitions.
- Integrates with clocksource/clock framework setup during early platform initialization.

## Risks
- IRQ number/routing mistakes show up as lost interrupts or interrupt storms rather than compile failures.
- headers are broadly included, so macro changes have a large blast radius across legacy board code.

## Test Signals
- Compile-test all in-tree users with `make ARCH=arm` for the affected SA-1100/SPEAr/shmobile/SoCFPGA configs; header regressions are best caught by building every including board file.
- Run `make ARCH=arm dtbs_check` for affected DTS files and confirm the expected machine compatible reaches this platform code at boot.
- Validate interrupt and GPIO paths with the attached devices that use the declared lines, watching `/proc/interrupts` and driver probe logs.

## Research Notes
- Read coverage: full file (4172 bytes, 100 lines).
- This is Linux ARM platform support code under `sources/distributed-fs/ceph-client`; it is kernel/architecture glue rather than distributed filesystem client logic.
