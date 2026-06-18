# sources/distributed-fs/ceph-client/drivers/net/ethernet/synopsys/dwc-xlgmac-pci.c

Purpose: Provides PCI bus binding for the Synopsys DWC XLGMAC core driver.

Important APIs/functions: `xlgmac_probe()` enables the PCI device with managed APIs, finds and maps the first non-empty BAR, sets bus mastering, fills `struct xlgmac_resources` with IRQ and MMIO base, and calls `xlgmac_drv_probe()`. `xlgmac_remove()` delegates to `xlgmac_drv_remove()`. The PCI ID table matches Synopsys vendor ID with device `0x7302`, and `module_pci_driver()` registers the driver.

Control flow and state: PCI-managed resources own device enablement and BAR mappings. Runtime netdev state is created by common probe and stored as device drvdata. No suspend/resume or MSI/MSI-X setup is implemented here; it uses `pcidev->irq`.

Dependencies and integration points: Built only when `CONFIG_DWC_XLGMAC_PCI` is enabled. Integrates PCI core, managed BAR mapping, and common XLGMAC resource-based probe.

Risks and test signals: If all BARs are empty, index `i` can reach `PCI_STD_NUM_BARS` before `pcim_iomap_table(pcidev)[i]` is used. The first non-empty BAR is assumed to be MAC registers. Test devices with unexpected BAR layout, shared legacy IRQ behavior, probe/remove repeat, DMA bus mastering, and absence of MSI support.
