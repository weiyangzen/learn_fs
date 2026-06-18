<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/aq_pci_func.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/aq_pci_func.c

Purpose: implements PCI driver registration, device ID to hardware-ops selection, PCI resource setup, IRQ allocation/freeing, probe/remove, shutdown, and power-management glue for Atlantic adapters.

Important APIs/functions: exports `aq_pci_func_alloc_irq`, `aq_pci_func_free_irqs`, `aq_pci_func_get_irq_type`, `aq_pci_func_register_driver`, and `aq_pci_func_unregister_driver`. Static probe helpers include `aq_pci_probe_get_hw_by_id`, `aq_pci_func_init`, `aq_pci_probe`, `aq_pci_remove`, `aq_pci_shutdown`, and PM suspend/resume wrappers.

Control flow: `aq_pci_probe` enables the device, requests regions, allocates the netdev, chooses A0/B0/ATL2 ops/caps from tables, allocates `aq_hw_s`, maps MMIO BARs, allocates IRQ vectors including PTP/service slots, starts NIC config, initializes and registers the netdev, then initializes driver info. Error labels unwind in reverse order. Remove unregisters netdev and frees filters, MACsec, vectors, IRQs, MMIO, hardware memory, PCI regions, and netdev.

State and persistence: stores `aq_nic_s` in PCI drvdata, tracks `irqvecs` and `msix_entry_mask`, maps MMIO into `aq_hw->mmio`, and controls PCI D0/D3/WOL state during shutdown and suspend. No disk persistence.

Dependencies and integration: binds Linux PCI core to `aq_nic`, hardware caps in `hw_atl_a0`, `hw_atl_b0`, `hw_atl2`, filters, MACsec, and driver metadata.

Risks: board table mismatches can select wrong ops/caps; IRQ mask bookkeeping must match vector ownership, especially link/PTP vectors; probe error unwinds must not leak BARs/MMIO/IRQ vectors; PM resume must deinit partially initialized hardware on errors. Test signals include PCI modalias binding, probe failure injection, MSI-X/MSI/INTx modes, suspend/resume, shutdown with WOL, and hot remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/aq_pci_func.c -->
