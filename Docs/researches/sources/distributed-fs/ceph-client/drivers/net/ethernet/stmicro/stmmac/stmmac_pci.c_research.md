# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/stmmac_pci.c

Purpose: PCI binding for STMMAC Ethernet cores. It maps a matched PCI device into the generic STMMAC driver by allocating `plat_stmmacenet_data`, mapping a PCI BAR, installing default platform/DMA/MDIO settings, setting interrupts, and calling `stmmac_dvr_probe()`.

Important APIs and functions: `struct stmmac_pci_info` carries the per-device `setup()` callback. `common_default_data()` sets legacy GMAC defaults, store-and-forward DMA, CSR clock range, and MDIO reset. `stmmac_default_data()` sets synthetic/STMicro defaults: bus ID 1, PHY address 0, GMII, PBL 32, PBLx8. `snps_gmac5_default_data()` configures GMAC5/GMAC4-style operation with TSO, PMT, four queues, WRR TX scheduling, SP RX scheduling, TBS on TX queues above zero, GMII, and AXI burst/outstanding settings. `stmmac_pci_probe()` performs allocation, PCI enablement, BAR mapping, setup, safety-feature enablement, PM callback assignment, and common probe. `stmmac_pci_remove()` delegates to `stmmac_dvr_remove()`.

Control flow: probe allocates platform, MDIO, and safety data; enables the PCI device with `pcim_enable_device()`; scans BARs and maps the first nonempty one with `pcim_iomap_region()`; calls `pci_set_master()`; runs the matched setup callback; maps `pdev->irq` to normal and WoL IRQs; enables safety bits; installs `stmmac_pci_plat_suspend/resume`; and enters common STMMAC probe. Removal is intentionally thin.

State and persistence: devres-owned platform data and mapped BAR persist for device lifetime. Queue, AXI, MDIO, safety, PHY, and PM settings persist in `plat_stmmacenet_data` and `stmmac_resources`.

Dependencies and integration: PCI core, DMI/clock headers, `stmmac.h`, `stmmac_libpci.h`, common STMMAC probe/remove and PM. The ID table supports synthetic STMMAC, STMicro MAC, and Synopsys GMAC5 and exports `MODULE_DEVICE_TABLE(pci, ...)`.

Risks and test signals: first-nonempty-BAR mapping assumes BAR ordering. GMII/PHY defaults may be too rigid for new PCI devices. Safety interrupts are enabled unconditionally after setup. Validate with PCI probe/remove, suspend/resume, MDIO scanning, multi-queue GMAC5 traffic, TSO/TBS, and STMMAC ethtool selftests.
