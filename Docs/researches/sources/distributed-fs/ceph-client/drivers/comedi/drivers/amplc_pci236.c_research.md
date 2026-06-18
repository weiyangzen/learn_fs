# sources/distributed-fs/ceph-client/drivers/comedi/drivers/amplc_pci236.c

## Purpose
This file is the PCI-specific wrapper for the Amplicon PCI236 digital I/O board. The board presents a single 8255 DIO device plus an interrupt-backed pseudo-DI subdevice implemented by shared helper code in `amplc_pc236.h`/common source. This wrapper handles PCI probing, PLX9052 local interrupt control, BAR discovery, and delegation to the common PC236 attach logic.

## Important APIs, Types, and Functions
The driver defines `PCI236_INTR_DISABLE` and `PCI236_INTR_ENABLE` bit patterns for the PLX9052 `INTCSR` register. `pci236_intr_update_cb()` enables/disables and clears the local interrupt latch. `pci236_intr_chk_clr_cb()` checks `PLX9052_INTCSR_LI1STAT`, clears the interrupt, and returns whether this device interrupted. `pc236_pci_board` supplies the board name and callbacks to the common layer. `pci236_auto_attach()` allocates `struct pc236_private`, enables PCI, records PLX local config and I/O bases, and calls `amplc_pc236_common_attach()`.

## Control Flow
`amplc_pci236_pci_probe()` invokes Comedi PCI auto-config, which calls `pci236_auto_attach()`. Attach sets the board descriptor, enables the PCI device, stores the PLX local configuration register base from BAR1, stores the 8255 I/O base from BAR2, and delegates subdevice setup and IRQ registration to `amplc_pc236_common_attach(dev, iobase, pci_dev->irq, IRQF_SHARED)`. During command or interrupt use, the common layer calls the wrapper's interrupt callbacks to update or clear PLX9052 local interrupt 1. Removal uses `comedi_pci_detach()`.

## State and Persistence Behavior
The only wrapper-specific persistent state is `pc236_private->lcr_iobase`, plus the common layer's private state such as IRQ enable flag. Hardware interrupt enable and latch state persist in the PLX9052 `INTCSR` register until changed by callbacks or detach. DIO port state is managed by the common PC236 code and the 8255 registers. No disk-backed state exists.

## Dependencies and Integration Points
This file depends on Comedi PCI helpers, Linux IRQ flags, `amplc_pc236` common code, and `plx9052.h` register definitions. It integrates with the PCI vendor/device table for Amplicon 0x0009 and exposes the board through `module_comedi_pci_driver()`.

## Risks
Correct interrupt behavior depends on PLX9052 bit polarity and the common layer's expectations. Enabling interrupts also clears the latch, so ordering matters around command arming. Because the pseudo-DI interrupt subdevice depends on a physical IRQ, configurations without a connected interrupt leave that function unused. The wrapper delegates most validation to common code, so regressions in callback semantics can break both PCI and any related PC236 variants.

## Test Signals
Probe/remove a PCI236 card, verify BAR1/BAR2 selection, exercise 8255 DIO group direction and bit I/O through common code, run the pseudo-DI external-trigger command on port C bit 3, verify shared IRQ filtering, and confirm interrupt disable/enable clears stale latches without losing a real rising edge.
