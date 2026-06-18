# sources/distributed-fs/ceph-client/arch/arm/mach-sa1100/include/mach/h3xxx.h

## Purpose
This SA-1100 machine header collects board or SoC constants for `h3xxx` users: GPIO assignments, IRQ lines, register offsets, memory windows, and helper declarations consumed by legacy board files and companion drivers.

## Important APIs, Types, and Functions
- Register/constant macro families: `H3XXX`(20), `H3600`(19), `H3100`(7), `_INC`(1); examples: `_INCLUDE_H3XXX_H_`, `H3600_EGPIO_PHYS`, `H3600_BANK_2_PHYS`, `H3600_BANK_4_PHYS`, `H3600_EGPIO_VIRT`, `H3600_BANK_2_VIRT`, `H3600_BANK_4_VIRT`, `H3XXX_GPIO_PWR_BUTTON`, `H3XXX_GPIO_PCMCIA_CD1`, `H3XXX_GPIO_PCMCIA_IRQ1`, `H3XXX_GPIO_PCMCIA_CD0`, `H3XXX_GPIO_ACTION_BUTTON`, `H3XXX_GPIO_SYS_CLK`, `H3XXX_GPIO_PCMCIA_IRQ0`, `H3XXX_GPIO_COM_DCD`, `H3XXX_GPIO_OPTION`, plus 31 more.

## Control Flow
There is no runtime control flow in this header. Including C files expand its macros into direct memory-mapped register accesses, IRQ-number calculations, board tests, and timing constants at compile time.

## State and Persistence Behavior
State is kernel-resident and hardware-facing: in-memory locks serialize access to shared controller state. No user-space persistent files are written by this code.

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
- Read coverage: full file (3369 bytes, 82 lines).
- This is Linux ARM platform support code under `sources/distributed-fs/ceph-client`; it is kernel/architecture glue rather than distributed filesystem client logic.
