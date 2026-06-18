# sources/distributed-fs/ceph-client/arch/alpha/kernel/sys_mikasa.c

## Purpose
Support for Mikasa/AlphaServer 1000 EV5+CIA systems, including local PCI interrupt mask programming and the Mikasa-Primo machine vector. The source was read as part of `subset-b-000628` and contains 190 lines.

## Important APIs, Types, and Functions
Defines `mikasa_primo_mv` with alias `mikasa_primo`. Important routines are `mikasa_update_irq_hw`, `mikasa_enable_irq`, `mikasa_disable_irq`, `mikasa_device_interrupt`, `mikasa_init_irq`, and `mikasa_map_irq`.

## Control Flow
Initialization optionally uses generic SRM interrupt dispatch, clears the board interrupt enable register at `0x536`, registers IRQs 16-31 with a level chip, then initializes i8259 and ISA DMA. Runtime dispatch combines board status from `0x534` with PIC status from `0xa0` and `0x20`, forwarding low bits to ISA and high bits to `handle_irq`.

## State and Persistence Behavior
`cached_irq_mask` stores enabled board IRQ bits. Hardware state is the 16-bit mask/status pair around ports `0x534/0x536`, the i8259 PIC, ISA DMA, and PCI interrupt-line configuration.

## Dependencies
Depends on CIA I/O/MMU, CIA machine-check and PCI init, common swizzle, i8259, ISA DMA, Alpha IRQ core, and fixed PCI IdSel maps.

## Integration Points
This file integrates with the Alpha architecture build and boot path under `arch/alpha`. Platform files are selected through `struct alpha_machine_vector`; syscall/linker files are consumed by Kbuild, low-level entry assembly, and the final kernel image; library files provide symbols used by the MM, networking, string, usercopy, module, and firmware-console subsystems.

## Risks
Mask bit polarity is enabled-when-set. Mixing board summary bits with i8259 status can accidentally redispatch ISA if status reads are stale. Fixed table only covers expected SCSI, bridge, and three slots.

## Test Signals
Compile Mikasa support, boot AlphaServer 1000 hardware, verify SCSI and each PCI slot interrupt line, check ISA interrupts still dispatch, and ensure SRM/non-SRM paths use the expected interrupt handler.
