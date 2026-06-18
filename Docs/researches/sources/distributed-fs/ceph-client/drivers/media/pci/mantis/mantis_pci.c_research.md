# sources/distributed-fs/ceph-client/drivers/media/pci/mantis/mantis_pci.c

- Purpose: Low-level PCI resource setup and teardown for the Mantis bridge.
- Important APIs/types/functions: `mantis_pci_init()` and `mantis_pci_exit()`.
- Control flow: Init enables the PCI device, sets 32-bit coherent DMA mask, enables bus mastering, claims BAR0, ioremaps it, records latency/revision, requests the shared IRQ using the board-configured handler, and stores driver data. Exit frees IRQ, unmaps and releases BAR0, and disables the device.
- State and persistence: Stores MMIO pointer, latency, revision, and PCI device pointer in `struct mantis_pci`; no persistence.
- Dependencies and integration points: Called first by probe and last during remove; underpins every MMIO helper and interrupt path.
- Risks: `mantis_addr` is logged but not assigned. Error handling jumps through resource release steps, so any future changes must preserve exact ownership. Only a coherent mask is set, not streaming mask.
- Test signals: Probe failure injection, request_irq failure, BAR mapping failure, and unload after active interrupts.
