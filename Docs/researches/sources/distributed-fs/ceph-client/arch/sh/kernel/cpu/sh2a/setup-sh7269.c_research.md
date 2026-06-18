# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh2a/setup-sh7269.c

## Purpose
`setup-sh7269.c` is the SH7269 counterpart to SH7264 setup. It registers the SoC interrupt map and platform devices for eight SCIF ports, CMT, MTU2, RTC, and R8A66597 USB host using SH7269-specific MMIO addresses and event numbers.

## Important APIs, Types, And Functions
Important data includes `vectors`, SCIF/PINT `groups`, `prio_registers`, `mask_registers`, and `DECLARE_INTC_DESC(intc_desc, "sh7269", ...)`. Devices are SCIF0-7 using FIFO-data register layout, `sh-cmt-16`, `sh-mtu2`, `sh-rtc`, and `r8a66597_hcd`. Setup hooks are `sh7269_devices_setup()`, `plat_irq_setup()`, and `plat_early_device_setup()`.

## Control Flow
`arch_initcall` registers the full platform-device set. Early setup registers serial and timer devices for boot console and clockevent use. INTC registration is one call to `register_intc_controller(&intc_desc)`.

## State And Persistence
All state is hardware metadata and static init-time structures. The USB host uses on-chip, endian-aware platform data and no DMA mask. There is no runtime persistence beyond driver-owned device state after registration.

## Dependencies And Integration Points
The file connects the CPU backend with serial, timer, RTC, USB HCD, and interrupt-controller subsystems. It uses `DEFINE_RES_MEM`, `DEFINE_RES_IRQ`, named MTU IRQ resources, and raw platform IRQ numbers rather than `evt2irq()`.

## Risks
SH7269 moves SCIF MMIO to the `0xe800xxxx` range and shifts many interrupt numbers versus SH7264; copy/paste drift would produce silent driver misbinding or dead interrupts. The VDC4 vector table includes repeated event entries, so interrupt behavior should be checked against the hardware manual.

## Test Signals
Probe logs for `sh-sci.0` through `.7`, active CMT/MTU clocksource events, RTC IRQ 338, and USB HCD IRQ 170 are the practical validation points. Serial loopback and USB enumeration are strong integration checks.
