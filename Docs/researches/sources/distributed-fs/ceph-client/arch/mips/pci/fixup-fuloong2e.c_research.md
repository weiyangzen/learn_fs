# sources/distributed-fs/ceph-client/arch/mips/pci/fixup-fuloong2e.c

## Purpose
Provides Lemote Fuloong2E IRQ routing and VIA686B/NEC USB PCI header fixups.

## Important APIs, Types, And Functions
Defines `pcibios_map_irq`, `pcibios_plat_dev_init`, fixups for VIA functions 0/1/2/3/5, and `loongson2e_nec_fixup`, registered with `DECLARE_PCI_FIXUP_HEADER`.

## Control Flow
The VIA ISA bridge fixup records `sb_slot`, programs ISA refresh, line buffers, delay transaction, IRQ trigger/routing bytes, legacy peripheral routing, and enables audio/modem functions. IDE, USB, and audio functions receive fixed interrupt lines and controller configuration. Non-southbridge devices map to `LOONGSON_IRQ_BASE + 25 + pin`.

## State And Persistence
Persists southbridge slot number in static `sb_slot` and writes multiple chipset PCI config bytes that remain active until reset.

## Dependencies And Integration Points
Depends on Loongson IRQ constants, VIA/NEC PCI IDs, port I/O, and the Loongson2 PCI ops selected for this board.

## Risks And Edge Cases
Magic VIA registers and hard-coded IRQs are board-specific. Interrupt routing depends on the ISA bridge fixup running before `pcibios_map_irq` needs `sb_slot`. Some disabled alternative IDE tuning indicates fragile hardware behavior.

## Test Signals
Boot or emulated board enumeration, IRQ assignment logs, and successful driver probe/interrupt delivery are the useful signals; most coverage is hardware or defconfig build coverage rather than unit tests.
