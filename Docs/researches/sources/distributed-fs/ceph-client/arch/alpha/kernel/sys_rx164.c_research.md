# sources/distributed-fs/ceph-client/arch/alpha/kernel/sys_rx164.c

## Purpose
RX164 platform support for a Pyxis/CIA Alpha board, with board interrupt mask programming and a fixed PCI routing table. The source was read as part of `subset-b-000628` and contains 203 lines.

## Important APIs, Types, and Functions
Defines `rx164_mv`. Key routines are `rx164_update_irq_hw`, `rx164_enable_irq`, `rx164_disable_irq`, `rx164_device_interrupt`, `rx164_init_irq`, and `rx164_map_irq`.

## Control Flow
IRQ init clears the board mask, initializes i8259/ISA DMA, and registers board IRQs as level-triggered. Runtime dispatch reads board status and PIC state, sends ISA bits to the ISA handler, and calls `handle_irq` for board PCI lines. PCI mapping translates IdSel and interrupt pin through a fixed table.

## State and Persistence Behavior
`cached_irq_mask` stores enabled board IRQ bits. Hardware state includes the board IRQ mask/status ports, i8259, ISA DMA controller, and PCI config lines.

## Dependencies
Depends on Pyxis/CIA core support, i8259 helpers, common ISA DMA, Alpha IRQ core, and PCI common table lookup.

## Integration Points
This file integrates with the Alpha architecture build and boot path under `arch/alpha`. Platform files are selected through `struct alpha_machine_vector`; syscall/linker files are consumed by Kbuild, low-level entry assembly, and the final kernel image; library files provide symbols used by the MM, networking, string, usercopy, module, and firmware-console subsystems.

## Risks
The IRQ mask is a single word, so invalid IRQ ranges can shift undefined bits. Fixed PCI tables must match the board revision. ISA/PIC summary reads can introduce duplicate dispatch if mishandled.

## Test Signals
Compile and boot RX164, exercise PCI slot interrupts, verify i8259 ISA devices, and inspect `/proc/interrupts` before and after mask/unmask activity.
