# sources/distributed-fs/ceph-client/drivers/bus/mhi/host/Kconfig

Purpose: declares host-side MHI configuration symbols: the core bus, optional debugfs support, and generic PCI controller driver.

Important declarations: `CONFIG_MHI_BUS` builds the MHI host stack; `CONFIG_MHI_BUS_DEBUG` depends on `MHI_BUS && DEBUG_FS`; `CONFIG_MHI_BUS_PCI_GENERIC` depends on `MHI_BUS` and `PCI`.

Control flow and state: configuration-time only. These symbols control compilation of host core, debugfs, and PCI controller objects.

Dependencies and integration: connects the MHI host protocol stack to kernel debugfs and PCI support. The generic PCI driver covers Qualcomm SDX-class PCIe modems per help text.

Risks and tests: dependency mistakes can create build/link failures or missing debugfs files. Test signals include allmodconfig, host core built-in/module, debugfs enabled/disabled, PCI generic enabled without endpoint, and help/menu visibility.
