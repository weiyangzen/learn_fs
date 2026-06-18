# sources/distributed-fs/ceph-client/drivers/net/ethernet/synopsys/Makefile

Purpose: Defines how the Synopsys XLGMAC driver objects are linked.

Important APIs/build targets: `obj-$(CONFIG_DWC_XLGMAC) += dwc-xlgmac.o` builds the core module from `dwc-xlgmac-net.o`, `dwc-xlgmac-desc.o`, `dwc-xlgmac-hw.o`, `dwc-xlgmac-common.o`, and `dwc-xlgmac-ethtool.o`. `dwc-xlgmac-$(CONFIG_DWC_XLGMAC_PCI) += dwc-xlgmac-pci.o` conditionally adds PCI bus binding.

Control flow and state: Build-time composition only. The object list mirrors runtime layering: common probe/init, descriptor allocation, hardware ops, netdev/NAPI, ethtool, and optional PCI resource discovery.

Dependencies and integration points: Consumed by kbuild under the Synopsys Ethernet directory and driven by Kconfig symbols in the same folder.

Risks and test signals: Missing an object breaks operation table registration or module entry points. Build-test core and PCI configurations, including module builds, to catch unresolved symbols around `xlgmac_get_netdev_ops()`, `xlgmac_init_hw_ops()`, and `xlgmac_drv_probe()`.
