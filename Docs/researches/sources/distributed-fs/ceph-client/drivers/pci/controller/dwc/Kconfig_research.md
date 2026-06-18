<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/Kconfig

Purpose: Kconfig menu for DesignWare-based PCIe controller support. It defines common DWC core symbols, debugfs, host/endpoint capability symbols, and many SoC-specific host/EP options including DRA7xx, Exynos, and i.MX covered in this work item.

Important APIs/types/functions: config symbols `PCIE_DW`, `PCIE_DW_DEBUGFS`, `PCIE_DW_HOST`, `PCIE_DW_EP`, `PCI_IMX6`, `PCI_IMX6_HOST`, `PCI_IMX6_EP`, `PCI_EXYNOS`, `PCI_DRA7XX`, `PCI_DRA7XX_HOST`, and `PCI_DRA7XX_EP`, plus numerous sibling DesignWare platform symbols.

Control flow: Kconfig has declarative dependency flow. SoC options depend on architecture or `COMPILE_TEST`, MSI or endpoint framework needs, OF/HAS_IOMEM/PHY requirements, and select `PCIE_DW_HOST` or `PCIE_DW_EP`, which in turn select the common `PCIE_DW` core. Some aggregate symbols are hidden and selected by host/EP variants.

State/persistence: no runtime state. The file determines which drivers and common objects are compiled into the kernel or modules, and therefore which runtime code paths can exist.

Dependencies/integration: Linux Kconfig, PCI core, endpoint framework, MSI support, debugfs, architecture symbols, and the DWC Makefile object list.

Risks: missing `select` lines can compile a glue driver without required common DWC host/EP code. Overly broad `COMPILE_TEST` can expose missing stubs on unsupported architectures. Some options are bool while others are tristate; common ARM32 constraints, such as Keystone not being loadable due to fault hooks, are documented separately and should not be generalized blindly.

Test signals: `allyesconfig`, `allmodconfig`, `COMPILE_TEST`, host-only and EP-only builds, module builds for tristate users, debugfs enabled/disabled builds, and dependency checks for `PCI_MSI` and `PCI_ENDPOINT`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/Kconfig -->
