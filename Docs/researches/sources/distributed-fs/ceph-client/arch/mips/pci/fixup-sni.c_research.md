# sources/distributed-fs/ceph-client/arch/mips/pci/fixup-sni.c

## Purpose
Provides SNI RM200/RM300 PCI IRQ routing tables for PCIMT and PCIT variants.

## Important APIs, Types, And Functions
Defines multiple static IRQ tables, `is_rm300_revd`, `pcibios_map_irq`, and no-op `pcibios_plat_dev_init`.

## Control Flow
`pcibios_map_irq` switches on `sni_brd_type`, applies a special PCI Tower C Plus slot-4 bus-1 workaround, distinguishes RM300 revision D via `PCIMT_CSMSR`, and returns the selected table entry.

## State And Persistence
No software persistence; board type is external global platform state.

## Dependencies And Integration Points
Depends on SNI board type constants, memory-mapped SNI registers, and platform IRQ definitions.

## Risks And Edge Cases
Tables are topology-specific and unchecked. The C Plus workaround walks parent bridges and depends on bus numbering and devfn thresholds. Direct volatile register access must be valid on PCIMT systems.

## Test Signals
Boot or emulated board enumeration, IRQ assignment logs, and successful driver probe/interrupt delivery are the useful signals; most coverage is hardware or defconfig build coverage rather than unit tests.
