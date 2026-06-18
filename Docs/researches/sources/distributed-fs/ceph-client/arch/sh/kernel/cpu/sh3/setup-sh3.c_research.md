# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh3/setup-sh3.c

## Purpose
`setup-sh3.c` contains common SH3 interrupt-pin setup shared by multiple SH3 subtypes. It handles external IRQ0-IRQ5 mode and priority setup that subtype files layer on top of.

## Important APIs, Types, And Functions
The key functions are `plat_irq_setup_sh3()` and `plat_irq_setup_pins()`. It defines common INTC vectors and priority/mask descriptors for IRQ pin handling.

## Control Flow
Subtype `plat_irq_setup()` functions register their SoC-specific controller and then call `plat_irq_setup_sh3()`. Board code can call `plat_irq_setup_pins(mode)` to configure IRQ pin mode and register additional external IRQ descriptors.

## State And Persistence
The file writes interrupt-control hardware registers for pin mode and registers static interrupt descriptors. There is no durable software state.

## Dependencies And Integration Points
It integrates with `linux/sh_intc.h`, IRQ mode constants, raw MMIO, and subtype setup files including SH7705, SH770x, SH7710, and SH7720.

## Risks
IRQ pin mode is board-sensitive. Unsupported modes intentionally `BUG()`, so bad board setup can halt boot. Shared use makes regressions broad across SH3 machines.

## Test Signals
External interrupt tests on IRQ0-IRQ5, boot without `BUG()`, and correct `/proc/interrupts` external IRQ entries validate this common setup.
