# sources/distributed-fs/ceph-client/arch/alpha/kernel/sys_noritake.c

## Purpose
Noritake/Primo platform support for EV5+CIA systems with local PCI interrupt masking, SRM vector support, PCI table mapping, and bridge swizzling. The source was read as part of `subset-b-000628` and contains 276 lines.

## Important APIs, Types, and Functions
Defines `noritake_primo_mv`. Important routines are `noritake_update_irq_hw`, `noritake_enable_irq`, `noritake_disable_irq`, `noritake_device_interrupt`, `noritake_srm_device_interrupt`, `noritake_init_irq`, `noritake_map_irq`, and `noritake_swizzle`.

## Control Flow
IRQ init clears board interrupt mask, optionally installs SRM dispatch, registers level IRQs, and initializes i8259/ISA DMA. Runtime dispatch reads board summary plus PIC status, routes low bits to ISA and high bits to Linux IRQs. PCI mapping uses fixed IdSel tables and swizzling handles built-in and card PCI bridges.

## State and Persistence Behavior
`cached_irq_mask` represents enabled PCI/board IRQ bits. Hardware state is held in board I/O ports, PIC/DMA registers, and PCI configuration.

## Dependencies
Uses CIA core, i8259, ISA DMA, PCI common table lookup, standard PCI swizzling, and Alpha machine vectors.

## Integration Points
This file integrates with the Alpha architecture build and boot path under `arch/alpha`. Platform files are selected through `struct alpha_machine_vector`; syscall/linker files are consumed by Kbuild, low-level entry assembly, and the final kernel image; library files provide symbols used by the MM, networking, string, usercopy, module, and firmware-console subsystems.

## Risks
Fixed routing tables and bridge assumptions are fragile for add-in bridge cards. SRM vector handling differs from direct hardware summary handling. Incorrect mask polarity would silence PCI lines.

## Test Signals
Build and boot Noritake/Primo, verify SCSI and PCI slot interrupts, exercise devices behind bridges, and compare SRM vector paths against direct PAL interrupt paths.
