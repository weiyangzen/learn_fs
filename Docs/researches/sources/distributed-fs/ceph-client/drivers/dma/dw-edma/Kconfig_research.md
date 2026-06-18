## sources/distributed-fs/ceph-client/drivers/dma/dw-edma/Kconfig

Purpose: Configuration entries for the Synopsys DesignWare eDMA core and the PCIe reference/glue driver.

Important APIs/types/functions: defines `CONFIG_DW_EDMA` and `CONFIG_DW_EDMA_PCIE`. `DW_EDMA` depends on PCI and PCI_MSI and selects DMAengine and virtual channels; `DW_EDMA_PCIE` depends on the parent feature and PCI/MSI support.

Control flow: build-time selection controls whether the common eDMA core and PCIe glue are compiled.

State and persistence: no runtime state.

Dependencies and integration: the dependency on PCI/MSI reflects that this eDMA implementation is normally exposed through PCIe endpoint/root-port designs and MSI/MSI-X interrupts.

Risks and test signals: wrong dependencies can produce compile failures or a driver with missing interrupt prerequisites. Test with all combinations `DW_EDMA=n`, `DW_EDMA=m/y`, and `DW_EDMA_PCIE=m/y` on PCI-enabled configs.
