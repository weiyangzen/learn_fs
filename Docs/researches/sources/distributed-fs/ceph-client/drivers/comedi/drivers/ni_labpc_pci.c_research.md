# sources/distributed-fs/ceph-client/drivers/comedi/drivers/ni_labpc_pci.c

## Purpose
`ni_labpc_pci.c` is the PCI front end for the NI PCI-1200 Lab-PC-family board. It performs PCI resource setup and delegates the device implementation to `labpc_common_attach()`.

## Important APIs, Types, And Functions
`labpc_pci_boards[]` defines the single PCI-1200 board descriptor. `labpc_pci_mite_init()` temporarily maps BAR0 to configure the MITE I/O device window base-size register to point at BAR1. `labpc_pci_auto_attach()` validates the context, enables PCI, initializes MITE, maps BAR1 into `dev->mmio`, and calls common attach with the PCI IRQ and `IRQF_SHARED`. `labpc_pci_detach()` calls common detach and Comedi PCI detach. PCI registration uses `labpc_pci_table`, `labpc_pci_probe()`, and `module_comedi_pci_driver()`.

## Control Flow
PCI ID `PCI_VENDOR_ID_NI, 0x161` maps to the PCI-1200 board. Probe invokes Comedi PCI auto config with that board index. Auto attach sets board metadata, enables the device, sets the MITE data window, maps register MMIO BAR1, and lets common attach select MMIO byte accessors, allocate counters/subdevices, and request the shared IRQ.

## State And Persistence
The PCI front end owns no unique private state. Persistent runtime state is common `labpc_private`, Comedi PCI resource state, and BAR1 MMIO mapping. The MITE BAR0 mapping is temporary and released immediately after window setup.

## Dependencies And Integration Points
The file depends on Comedi PCI helpers, Linux interrupt definitions, MMIO mapping, and `ni_labpc.h`. It integrates with common Lab-PC code by setting `dev->mmio`, which causes `labpc_common_attach()` to use `readb`/`writeb` and MMIO 8254/8255 helpers.

## Risks
MITE setup is a minimal local copy rather than full MITE infrastructure. If BAR1 physical addressing or window setup changes, common MMIO register access fails. The IRQ is passed unconditionally from PCI; common attach may proceed without command support if IRQ request fails. Driver name is `labpc_pci`, while board name is `ni_pci-1200`, which matters for user-visible configuration.

## Test Signals
Tests should cover PCI ID matching, context validation, PCI enable failure, MITE BAR0 map failure, BAR1 map failure, MITE window write value, common attach using MMIO accessors, shared IRQ path, detach ordering, and board flags matching Lab-PC-1200 common behavior.
