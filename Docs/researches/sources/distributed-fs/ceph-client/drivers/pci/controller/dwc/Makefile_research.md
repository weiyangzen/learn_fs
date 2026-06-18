<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/Makefile -->
# sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/Makefile

Purpose: object list for DesignWare PCIe controller drivers. It maps Kconfig symbols to common DWC core objects, debugfs, host/endpoint support, platform glue, SoC-specific drivers, and ACPI quirk objects.

Important APIs/types/functions: `obj-$(CONFIG_PCIE_DW) += pcie-designware.o`, host/EP objects, platform object, and per-driver mappings such as `obj-$(CONFIG_PCI_DRA7XX) += pci-dra7xx.o`, `obj-$(CONFIG_PCI_EXYNOS) += pci-exynos.o`, and `obj-$(CONFIG_PCI_IMX6) += pci-imx6.o`.

Control flow: build flow is declarative. Hidden aggregate symbols such as `PCI_IMX6` and `PCI_DRA7XX` compile a shared source once while host/EP Kconfig symbols control code paths inside the source through `IS_ENABLED()` or selected common support.

State/persistence: no runtime state. It determines which object files are linked into the kernel or modules.

Dependencies/integration: Kbuild, DWC Kconfig, and ACPI/PCI quirk conditions. The ACPI block always builds some quirk objects on ARM64 when ACPI and PCI quirks are enabled, independent of DT driver enablement.

Risks: object symbols must match Kconfig names exactly. A source that supports both host and endpoint must be keyed on the aggregate symbol, not only one mode, or the other mode will not link. Duplicate object inclusion through ACPI and DT paths must remain intentional.

Test signals: `make drivers/pci/controller/dwc/`, `allyesconfig`, `allmodconfig`, host-only and EP-only configs for i.MX/DRA7xx, and ARM64 ACPI quirk builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/Makefile -->
