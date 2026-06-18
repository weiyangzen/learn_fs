# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh2a/setup-sh7206.c

## Purpose
`setup-sh7206.c` describes the SH7206 on-chip interrupt controller and early/normal platform devices for serial ports and timers. It is board-independent CPU setup glue that lets generic SH platform code discover SCIF, CMT, and MTU2 resources before and after normal driver init.

## Important APIs, Types, And Functions
The file defines INTC source enums, `vectors`, `groups`, `prio_registers`, `mask_registers`, and `DECLARE_INTC_DESC(intc_desc, "sh7206", ...)`. Platform resources include four `sh-sci` SCIF devices, an `sh-cmt-16` device with `channels_mask = 3`, and an `sh-mtu2s` device. Key functions are `sh7206_devices_setup()`, `plat_irq_setup()`, and `plat_early_device_setup()`.

## Control Flow
At `arch_initcall`, `platform_add_devices()` registers the full device list. During interrupt setup, `plat_irq_setup()` registers the SH7206 INTC descriptor. During early boot, `plat_early_device_setup()` clears clock-stopping bits in `STBCR4` for CMT and `STBCR3` for MTU2, then calls `sh_early_platform_add_devices()` for early console and timer availability.

## State And Persistence
Persistent state is hardware-facing: INTC priority/mask programming and standby-control register writes that enable timer clocks. Device state is static `__initdata` and platform-resource metadata consumed by drivers; no filesystem state exists.

## Dependencies And Integration Points
It depends on the SH intc layer, `platform_device`, `serial_sci`, `sh_timer`, raw MMIO access, and `asm/platform_early.h`. IRQ numbers and MMIO addresses are consumed by the `sh-sci`, `sh-cmt-16`, and `sh-mtu2s` drivers.

## Risks
Wrong vector numbers, priority-register bit positions, or standby bits can make interrupts or clocksource devices fail very early. The MTU device name differs from later SH726x files (`sh-mtu2s`), so driver binding must match that subtype.

## Test Signals
Useful signals are boot logs showing early console/timer registration, `/proc/interrupts` entries for SCIF/CMT/MTU events, and successful timer tick/serial interrupt operation on SH7206 hardware or emulator support.
