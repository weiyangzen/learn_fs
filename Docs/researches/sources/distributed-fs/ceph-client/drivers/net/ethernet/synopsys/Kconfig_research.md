# sources/distributed-fs/ceph-client/drivers/net/ethernet/synopsys/Kconfig

Purpose: Adds Kconfig switches for Synopsys Ethernet devices and the DWC XLGMAC driver family.

Important APIs/options: `NET_VENDOR_SYNOPSYS` gates the vendor submenu and defaults to yes. `DWC_XLGMAC` is a tristate depending on `HAS_IOMEM && HAS_DMA` and selects `BITREVERSE` and `CRC32`, matching VLAN/MAC hash-table code in `dwc-xlgmac-hw.c`. `DWC_XLGMAC_PCI` is a tristate bus glue option depending on `DWC_XLGMAC && PCI`.

Control flow and state: Build-time only. These symbols decide whether the common XLGMAC object and optional PCI module are compiled and linked. No runtime state is stored here.

Dependencies and integration points: Makefile consumes `CONFIG_DWC_XLGMAC` and `CONFIG_DWC_XLGMAC_PCI`. Source code depends on selected CRC/bit-reversal helpers and on I/O memory/DMA capabilities.

Risks and test signals: Misconfigured dependencies would produce link failures or unusable drivers on non-DMA platforms. Test all three build modes: vendor disabled, XLGMAC built-in/module without PCI, and PCI glue built-in/module.
