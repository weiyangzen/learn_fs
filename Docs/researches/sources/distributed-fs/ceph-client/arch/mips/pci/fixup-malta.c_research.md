# sources/distributed-fs/ceph-client/arch/mips/pci/fixup-malta.c

## Purpose
Implements MIPS Malta PIIX4 IRQ discovery and chipset compatibility fixups.

## Important APIs, Types, And Functions
Defines static `pci_irq`, `irq_tab`, `pcibios_map_irq`, no-op `pcibios_plat_dev_init`, and PIIX4 fixups `malta_piix_func3_base_fixup`, `malta_piix_func0_fixup`, `malta_piix_func1_fixup`, and `quirk_dlcsetup`.

## Control Flow
PIIX function 0 fixup reads PIRQ routing registers and fills `pci_irq`, then enables SERIRQ and special cycles. Function 3 sets PM I/O base and enable. Function 1 enables IDE decode on expected slot. Final quirk enables passive release and delayed transaction. IRQ mapping uses board slot/pin swizzle to index the discovered PIRQ-to-IRQ table.

## State And Persistence
Persists PIRQ mappings in static `pci_irq` and modifies PIIX config registers. No durable state.

## Dependencies And Integration Points
Depends on Malta PIIX4 register definitions and PCI quirk infrastructure.

## Risks And Edge Cases
IRQ mapping is invalid until PIIX fixup fills `pci_irq`. Slot table assumes Malta topology. Hard-coded PIIX settings interact with firmware versions noted in comments.

## Test Signals
Malta QEMU or hardware boot with PCI devices should show correct IRQs, IDE/USB enumeration, and no PIIX regressions. Build coverage for `CONFIG_MIPS_MALTA` is required.
