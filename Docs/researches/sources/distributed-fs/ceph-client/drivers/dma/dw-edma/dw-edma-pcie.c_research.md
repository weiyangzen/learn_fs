## sources/distributed-fs/ceph-client/drivers/dma/dw-edma/dw-edma-pcie.c

Purpose: PCIe glue/reference driver that discovers DW eDMA/HDMA resources, maps BARs, allocates MSI/MSI-X vectors, fills `struct dw_edma_chip`, and starts the common eDMA core.

Important APIs/types/functions: `dw_edma_pcie_probe()`, `dw_edma_pcie_remove()`, PCI ID table entries for Synopsys EDDA and Xilinx/AMD MDB, static platform data (`snps_edda_data`, `xilinx_mdb_data`), VSEC parsers `dw_edma_pcie_get_synopsys_dma_data()` and `dw_edma_pcie_get_xilinx_dma_data()`, `dw_edma_set_chan_region_offset()`, and platform ops `irq_vector`/`pci_address`.

Control flow: probe enables PCI, copies default layout data, optionally overrides map format, BAR, register offset, and channel counts from vendor-specific capabilities, maps all required BARs, sets DMA mask, allocates IRQ vectors, fills register/LL/data regions for write and read channels, validates MSI, invokes `dw_edma_probe()`, and stores driver data. Remove delegates to `dw_edma_remove()` and frees PCI IRQ vectors.

State and persistence: per-device state is in devm-allocated `dw_edma_chip` plus copied probe-time layout data. Mapped BAR pointers and physical/bus addresses remain valid for driver lifetime only.

Dependencies and integration: integrates PCI core, VSEC parsing, MSI/MSI-X, PCI bus address translation, and the common eDMA core. For Xilinx MDB it supports native HDMA and falls back to non-linked-list mode when device memory offset is unavailable.

Risks and test signals: resource map correctness is critical; wrong BAR/offset/channel count can corrupt device memory. Test with Synopsys and Xilinx IDs, VSEC-present and default layouts, MSI and MSI-X vector allocation, non-LL fallback, DMA transfers in both directions, and remove after active/inactive probe.
