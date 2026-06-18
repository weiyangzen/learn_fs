# sources/distributed-fs/ceph-client/drivers/edac/thunderx_edac.c

Purpose: `thunderx_edac.c` is a combined Cavium ThunderX EDAC module for LMC memory controllers, OCX/CCPI fabric, and L2C subdevices. It registers three PCI drivers and reports MC errors through EDAC MC APIs and fabric/cache errors through EDAC device APIs.

Important APIs/types/functions: shared helpers include `decode_register()` and debugfs macros. LMC uses `struct thunderx_lmc`, `thunderx_lmc_probe/remove()`, `thunderx_lmc_err_isr()`, `thunderx_lmc_threaded_isr()`, and `thunderx_faddr_to_phys()`. OCX uses `struct thunderx_ocx` plus common/link IRQ handlers. L2C uses `struct thunderx_l2c`, per-device ISR selection, and `thunderx_l2c_threaded_isr()`.

Control flow: init refuses GHES systems, registers LMC, OCX, and L2C PCI drivers with unwind. Probes enable PCI/MMIO, allocate EDAC objects, enable MSI-X, request threaded IRQs, clear stale status, enable masks, and optionally create debugfs nodes. Hard IRQs snapshot registers into rings and clear hardware; threaded handlers drain and report CE/UE.

State and persistence: state is per PCI device: MMIO base, EDAC object, MSI-X entries, rings, and decode parameters. Debug injection temporarily allocates a page and uses cache maintenance. No persistent state exists.

Dependencies/integration: Cavium PCI IDs, 64-bit MMIO, MSI-X, EDAC MC/device APIs, debugfs, ARM cache maintenance, NUMA, GHES arbitration.

Risks: no ring overflow protection; OCX link thread uses head rather than tail when selecting entries; L2C thread does not refresh `ctx` inside the drain loop; LMC physical address reconstruction is highly hardware-specific; debug ECC injection is invasive.

Test signals: device registration on ThunderX, CE/UE MSI-X interrupts for LMC/OCX/L2C, debugfs injection, multiple queued interrupt stress, and module unwind ordering.
