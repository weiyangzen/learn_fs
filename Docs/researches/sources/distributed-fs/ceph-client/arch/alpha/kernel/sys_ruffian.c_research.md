# sources/distributed-fs/ceph-client/arch/alpha/kernel/sys_ruffian.c

## Purpose
Ruffian system support for CIA/Pyxis-style Alpha boards, including IRQ init, RTC/reboot quirks, PCI IRQ mapping, and memory bank sizing. The source was read as part of `subset-b-000628` and contains 240 lines.

## Important APIs, Types, and Functions
Defines `ruffian_mv`. Important routines include `ruffian_init_irq`, `ruffian_init_rtc`, `ruffian_kill_arch`, `ruffian_map_irq`, `ruffian_swizzle`, and `ruffian_get_bank_size`.

## Control Flow
IRQ init configures i8259 and platform IRQs, RTC init programs board-specific CMOS/RTC behavior, reboot logic drives Ruffian reset/power behavior, PCI mapping uses a fixed IdSel table, and swizzling walks bridges to produce the root-slot/pin pair. Memory sizing reads board registers by bank offset.

## State and Persistence Behavior
Platform state is in PIC/DMA, RTC/CMOS, board reset registers, PCI config space, and memory bank registers. The code does not keep persistent software state beyond init-time calculations.

## Dependencies
Uses CIA/Pyxis core support, i8259/ISA helpers, PCI config, Linux reboot command constants, machine vector registration, and common Alpha RTC hooks.

## Integration Points
This file integrates with the Alpha architecture build and boot path under `arch/alpha`. Platform files are selected through `struct alpha_machine_vector`; syscall/linker files are consumed by Kbuild, low-level entry assembly, and the final kernel image; library files provide symbols used by the MM, networking, string, usercopy, module, and firmware-console subsystems.

## Risks
RTC and reset behavior is board-specific and easy to regress on firmware variants. PCI swizzling assumes known bridge topology. Memory bank sizing uses low-level register offsets and can corrupt boot memory accounting if wrong.

## Test Signals
Boot Ruffian hardware, check RTC tick/time behavior, test reboot/halt/poweroff, verify all PCI slot interrupts, and compare detected memory size with firmware-reported banks.
