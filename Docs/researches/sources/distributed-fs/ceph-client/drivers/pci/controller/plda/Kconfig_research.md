# sources/distributed-fs/ceph-client/drivers/pci/controller/plda/Kconfig

Purpose: Defines Kconfig options for PLDA-based PCIe host controller support, including the shared PLDA host core and Microchip/StarFive host drivers.

Important APIs/types/functions: The menu is `PLDA-based PCIe controllers` and depends on `PCI`. `PCIE_PLDA_HOST` is a hidden bool selecting `IRQ_MSI_LIB`. `PCIE_MICROCHIP_HOST` is a tristate depending on `PCI_MSI && OF`, selects `PCI_HOST_COMMON` and `PCIE_PLDA_HOST`, and describes Microchip AXI PCIe host bridge support. `PCIE_STARFIVE_HOST` is a tristate depending on `PCI_MSI && OF` and `ARCH_STARFIVE || COMPILE_TEST`, selects `PCIE_PLDA_HOST`, and builds module `pcie-starfive.ko` when modular.

Control flow: No runtime control flow. During kernel configuration, enabling a concrete PLDA host driver selects the shared helper object and MSI library support needed by the source files in this directory.

State and persistence: Kconfig choices persist in the generated kernel `.config` and determine which objects are compiled built-in or as modules.

Dependencies/integration: Integrates with the PCI controller Kconfig hierarchy and the sibling `Makefile`. It controls compilation of `pcie-plda-host.o`, `pcie-microchip-host.o`, and `pcie-starfive.o`.

Risks: The concrete drivers require `PCI_MSI`; systems without MSI cannot build these host drivers. `PCIE_PLDA_HOST` is hidden and selected, so dependency mistakes in concrete drivers can produce missing helper symbols. `COMPILE_TEST` broadens StarFive coverage beyond native architecture and must not imply runtime support.

Test signals: `olddefconfig` and menuconfig visibility, builds for Microchip and StarFive as built-in and modules, dependency checks with `PCI_MSI=n`, and link coverage that shared PLDA symbols are present when either concrete driver is enabled.
