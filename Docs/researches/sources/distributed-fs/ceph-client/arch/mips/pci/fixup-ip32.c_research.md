# sources/distributed-fs/ceph-client/arch/mips/pci/fixup-ip32.c

## Purpose
Provides SGI O2/IP32 MACE PCI interrupt routing for onboard SCSI controllers and the expansion slots.

## Important APIs, Types, And Functions
Defines `irq_tab_mace`, `pcibios_map_irq`, and no-op `pcibios_plat_dev_init`.

## Control Flow
Enumeration maps the PCI slot and interrupt pin directly through `irq_tab_mace`; onboard SCSI slots are fixed to SCSI IRQs and expansion slots swizzle shared IRQs.

## State And Persistence
No persistent state. The file contributes boot-time or PCI-enumeration-time callbacks only.

## Dependencies And Integration Points
Depends on IP32 interrupt definitions and the MACE PCI controller files.

## Risks And Edge Cases
The table assumes O2's fixed five-device wiring and has no bounds checks. Unexpected slot/pin values can return wrong or zero IRQs.

## Test Signals
Boot or emulated board enumeration, IRQ assignment logs, and successful driver probe/interrupt delivery are the useful signals; most coverage is hardware or defconfig build coverage rather than unit tests.
