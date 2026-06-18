# sources/distributed-fs/ceph-client/arch/mips/pci/fixup-lemote2f.c

## Purpose
Provides Lemote 2F IRQ routing and CS5536/NEC fixups for Loongson2F boards.

## Important APIs, Types, And Functions
Defines `irq_tab`, `pcibios_map_irq`, no-op `pcibios_plat_dev_init`, CS5536 ISA/IDE/audio/OHCI/EHCI fixups, and `loongson_nec_fixup` registered as PCI header fixups.

## Control Flow
Non-CS5536 devices route through a static slot/pin table plus `LOONGSON_IRQ_BASE`. CS5536 functions get explicit IDE/audio/USB interrupts and write `PCI_INTERRUPT_LINE`. Fixups enable UART, IDE muxing, audio/OHCI interrupts, EHCI USB config MSRs and FLADJ, and reduce NEC USB ports.

## State And Persistence
Writes device config registers and CS5536 MSRs that persist until reset. No software state beyond static tables.

## Dependencies And Integration Points
Depends on Loongson, CS5536 PCI/MSR helpers, `_rdmsr/_wrmsr` from `ops-loongson2.c`, and PCI quirk registration.

## Risks And Edge Cases
Hard-coded slot numbers and CS5536 function assumptions are board-specific. MSR writes and USB/EHCI tuning can break peripherals if applied to the wrong revision. IRQ 0 returns indicate unsupported slots.

## Test Signals
Boot or emulated board enumeration, IRQ assignment logs, and successful driver probe/interrupt delivery are the useful signals; most coverage is hardware or defconfig build coverage rather than unit tests.
