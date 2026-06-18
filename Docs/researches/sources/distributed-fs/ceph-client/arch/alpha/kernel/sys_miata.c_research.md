# sources/distributed-fs/ceph-client/arch/alpha/kernel/sys_miata.c

## Purpose
Machine support for Miata EV56/PYXIS systems, covering SRM vector adjustment, Pyxis IRQ initialization, PCI IRQ mapping/swizzling, audio/SuperIO setup, and reboot behavior. The source was read as part of `subset-b-000628` and contains 295 lines.

## Important APIs, Types, and Functions
Defines `miata_mv`. Key routines are `miata_srm_device_interrupt`, `miata_init_irq`, `miata_map_irq`, `miata_swizzle`, `miata_init_pci`, and `miata_kill_arch`.

## Control Flow
IRQ init swaps in a Miata-specific SRM dispatcher, initializes i8259, masks unwanted Pyxis interrupt bits, initializes ISA DMA, and requests no-op handlers for halt-switch and timer-cascade lines. PCI mapping uses a fixed IdSel table plus special USB function handling via ALI config byte `0x40`. Swizzling distinguishes root bus devices, built-in bridges, and card bridges.

## State and Persistence Behavior
Hardware state includes Pyxis interrupt masks, PIC/DMA registers, requested IRQ descriptors, PCI interrupt-line bytes, SMC669/ES1888 initialization, and a reset write to `PYXIS_RESET` during SRM restart. No persistent storage is updated.

## Dependencies
Uses CIA/Pyxis core support, `init_pyxis_irqs`, i8259 helpers, common ISA DMA, PCI config helpers, SMC669, ES1888, and Linux reboot command constants.

## Integration Points
This file integrates with the Alpha architecture build and boot path under `arch/alpha`. Platform files are selected through `struct alpha_machine_vector`; syscall/linker files are consumed by Kbuild, low-level entry assembly, and the final kernel image; library files provide symbols used by the MM, networking, string, usercopy, module, and firmware-console subsystems.

## Risks
The SRM vector correction adds 8 for IRQs above 15 to compensate for firmware numbering. The USB special case depends on function number and a companion config read. Riser and bridge handling is intentionally limited, so unexpected bus topology can misroute interrupts.

## Test Signals
Boot Miata and MiataGL variants, verify halt switch and timer cascade IRQ requests, enumerate PCI and USB devices, trigger restart/halt/poweroff paths, and compare firmware-assigned IRQ lines with Linux `/proc/interrupts`.
