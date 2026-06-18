# sources/distributed-fs/ceph-client/arch/alpha/kernel/sys_sx164.c

## Purpose
SX164 board support for Pyxis-based Alpha systems, including architecture init quirks, IRQ setup, PCI mapping, and the SX164 machine vector. The source was read as part of `subset-b-000628` and contains 179 lines.

## Important APIs, Types, and Functions
Defines `sx164_mv`. Important routines are `sx164_init_irq`, `sx164_map_irq`, `sx164_init_pci`, and `sx164_init_arch`.

## Control Flow
Architecture init configures Pyxis/CIA resources and any SX164 alignment quirks. IRQ init sets up i8259 and Pyxis IRQs with selected mask bits. PCI init calls the platform PCI initialization path. Runtime interrupts are handled by the generic `pyxis_device_interrupt` selected in the machine vector, while this file supplies the board IRQ table.

## State and Persistence Behavior
State is primarily hardware state in Pyxis interrupt registers, i8259/DMA controllers, PCI config space, and scatter-gather alignment fields touched during init.

## Dependencies
Depends on Pyxis I/O macros, CIA machine-check handler, generic Pyxis IRQ support, i8259, common PCI setup, and Alpha machine vector registration.

## Integration Points
This file integrates with the Alpha architecture build and boot path under `arch/alpha`. Platform files are selected through `struct alpha_machine_vector`; syscall/linker files are consumed by Kbuild, low-level entry assembly, and the final kernel image; library files provide symbols used by the MM, networking, string, usercopy, module, and firmware-console subsystems.

## Risks
Board-specific PCI routing is hard-coded and must match SX164 slot wiring. Init-order regressions can break Pyxis IRQ setup before device discovery. Alignment changes affect DMA mappings.

## Test Signals
Build SX164 config, boot hardware, validate PCI slot routing, verify DMA-capable devices, and confirm generic Pyxis interrupt dispatch reaches board-mapped IRQs.
