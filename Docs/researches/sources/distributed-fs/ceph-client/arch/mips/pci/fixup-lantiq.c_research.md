# sources/distributed-fs/ceph-client/arch/mips/pci/fixup-lantiq.c

## Purpose
Provides Lantiq PCI platform hooks with device-tree interrupt mapping.

## Important APIs, Types, And Functions
Defines no-op `pcibios_plat_dev_init` and `pcibios_map_irq` using `of_irq_parse_and_map_pci`.

## Control Flow
The MIPS PCI core calls the platform hooks during device setup; this file delegates IRQ mapping to OF data and otherwise leaves devices unchanged.

## State And Persistence
No persistent state. The file contributes boot-time or PCI-enumeration-time callbacks only.

## Dependencies And Integration Points
Depends on `linux/of_pci.h` and the Lantiq PCI controller stack.

## Risks And Edge Cases
Correctness depends entirely on board DT interrupt-map data. There is no static fallback.

## Test Signals
Boot or emulated board enumeration, IRQ assignment logs, and successful driver probe/interrupt delivery are the useful signals; most coverage is hardware or defconfig build coverage rather than unit tests.
