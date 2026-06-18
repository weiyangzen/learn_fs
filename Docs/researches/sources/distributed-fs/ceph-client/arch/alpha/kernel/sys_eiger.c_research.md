# sources/distributed-fs/ceph-client/arch/alpha/kernel/sys_eiger.c

## Purpose
Machine-vector support for the Eiger EV6 plus Tsunami platform, with IRQ programming modeled after Takara but using SRM-provided PCI interrupt values. The source was read as part of `subset-b-000628` and contains 225 lines.

## Important APIs, Types, and Functions
Exports `eiger_mv` via `ALIAS_MV(eiger)`. Key routines are `eiger_update_irq_hw`, `eiger_enable_irq`, `eiger_disable_irq`, `eiger_device_interrupt`, `eiger_srm_device_interrupt`, `eiger_init_irq`, `eiger_map_irq`, and `eiger_swizzle`.

## Control Flow
Boot selects `eiger_mv`; IRQ init resets ISA DMA, installs SRM vector dispatch when needed, masks each hardware IRQ bank through I/O ports around `0x510`, initializes i8259 IRQs, and registers IRQs 16-127 as level-triggered Eiger interrupts. Runtime interrupt dispatch reads the master interrupt register at `0x500`; if no accelerated PCI bits are set, it falls back to ISA dispatch. PCI swizzling counts backplane bridges from port `0x502` before applying standard bridge swizzle rules.

## State and Persistence Behavior
`cached_irq_mask[2]` stores disabled IRQ bits for two 64-bit ranges; mask writes are persistent hardware state in Eiger/Tsunami interrupt controller ports. PCI routing state is taken from `PCI_INTERRUPT_LINE` programmed by firmware.

## Dependencies
Uses Tsunami machine-check/I/O/MMU macros, generic PCI setup, i8259 ISA helpers, PCI core config access, and Alpha machine vector registration.

## Integration Points
This file integrates with the Alpha architecture build and boot path under `arch/alpha`. Platform files are selected through `struct alpha_machine_vector`; syscall/linker files are consumed by Kbuild, low-level entry assembly, and the final kernel image; library files provide symbols used by the MM, networking, string, usercopy, module, and firmware-console subsystems.

## Risks
The disabled-bit mask polarity is opposite DP264. Firmware IRQ values are adjusted by subtracting `0x80`; bad firmware or unexpected bridge layouts can map negative or wrong IRQs. Backplane bridge counting has hard-coded patterns.

## Test Signals
Compile with Eiger support, boot with SRM and non-SRM firmware, confirm IRQs 16-127 register, verify PCI devices keep working behind backplane bridges, and test both PCI and ISA interrupt delivery.
