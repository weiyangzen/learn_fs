# sources/distributed-fs/ceph-client/arch/sparc/kernel/pci_msi.c

## Purpose
Common sparc64 PCI MSI layer above controller-specific MSI queue hardware. It parses OF MSI properties, allocates software MSI state, brings up MSI queue IRQs, dispatches queued messages, and installs PBM MSI setup/teardown callbacks.

## Important APIs, Types, and Functions
`sparc64_pbm_msi_init()` is the PBM entry point. `sparc64_msiq_interrupt()` drains one MSI queue and calls `generic_handle_irq()`. `pick_msiq()` round-robins queues. `alloc_msi()` / `free_msi()` manage the MSI bitmap. `sparc64_setup_msi_irq()` allocates a Linux IRQ, reserves an MSI number, programs hardware, writes the device MSI message, and updates `msi_irq_table`. `sparc64_teardown_msi_irq()` reverses the mapping. Allocation helpers build cookies, IRQ tables, and bitmaps.

## Control Flow
PBM probe calls `sparc64_pbm_msi_init()` with controller queue ops. It reads OF MSI queue/range/address properties, allocates software and hardware queue state, requests one IRQ per queue, logs the layout, and installs callbacks. Device MSI enable later enters through `setup_msi_irq`; queue interrupts dispatch through the common handler.

## State and Persistence
Runtime state includes `msi_bitmap`, `msi_irq_table`, `msiq_irq_cookies`, queue rotor, OF-derived ranges, and controller-owned `msi_queues`. No persistence.

## Dependencies and Integration Points
Uses Linux interrupt, IRQ, PCI MSI, OF, slab APIs, `pci_pbm_info`, and controller-provided `sparc64_msiq_ops`.

## Risks and Test Signals
Malformed OF properties disable MSI. Queue bringup lacks full unwind on partial failure. Teardown returns early on hardware teardown error. Test via MSI boot logs, device MSI enable/disable, queue IRQ dispatch, and absence of MSI number leaks.
