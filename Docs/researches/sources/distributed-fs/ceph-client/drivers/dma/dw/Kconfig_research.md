## sources/distributed-fs/ceph-client/drivers/dma/dw/Kconfig

Purpose: Configuration entries for classic Synopsys DesignWare AHB DMA core, platform driver, PCI driver, and Renesas RZ/N1 DMAMUX frontend.

Important APIs/types/functions: defines `CONFIG_DW_DMAC_CORE`, `CONFIG_DW_DMAC`, `CONFIG_RZN1_DMAMUX`, and `CONFIG_DW_DMAC_PCI`. Platform and PCI drivers select the shared core; the Renesas DMAMUX depends on the platform driver.

Control flow: build-time symbols determine which bus glue and support modules are compiled.

State and persistence: no runtime state.

Dependencies and integration: declares PCI, HAS_IOMEM, architecture, and DMAengine dependencies needed by the DW AHB driver family.

Risks and test signals: dependency errors can cause unmet symbols or unusable driver selections. Test with platform-only, PCI-only, both, and compile-test DMAMUX configurations.
