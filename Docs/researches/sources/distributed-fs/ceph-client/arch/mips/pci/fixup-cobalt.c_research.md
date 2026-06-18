# sources/distributed-fs/ceph-client/arch/mips/pci/fixup-cobalt.c

## Purpose
Implements Cobalt Qube/Raq PCI quirks, board ID discovery, and static IRQ routing tables.

## Important APIs, Types, And Functions
Key fixups are `qube_raq_galileo_early_fixup`, `qube_raq_via_bmIDE_fixup`, `qube_raq_galileo_fixup`, and `qube_raq_via_board_id_fixup`, registered via `DECLARE_PCI_FIXUP_*`. Exposes global `cobalt_board_id`, `pcibios_map_irq`, and `pcibios_plat_dev_init`.

## Control Flow
Early/header fixups correct the GT64111 class code, enable VIA IDE bus mastering, set latency/cache-line values, force Galileo retry timeouts, enable retry interrupts, and read the VIA-wired board ID. IRQ mapping selects one of three static tables based on `cobalt_board_id`.

## State And Persistence
Persists the detected board ID in global `cobalt_board_id` for later IRQ mapping. Hardware config registers are modified persistently until reset.

## Dependencies And Integration Points
Depends on PCI quirk infrastructure, GT64120 register macros, Cobalt board constants, and IRQ definitions.

## Risks And Edge Cases
The file writes magic legacy chipset registers. A failed board-ID read panics. Slot indexes are used directly, so unexpected topology can index invalid or zero IRQ entries. Galileo timeout changes are hardware-critical.

## Test Signals
Boot or emulated board enumeration, IRQ assignment logs, and successful driver probe/interrupt delivery are the useful signals; most coverage is hardware or defconfig build coverage rather than unit tests.
