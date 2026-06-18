## sources/distributed-fs/ceph-client/drivers/pci/controller/mobiveil/Kconfig

Purpose: Kconfig menu for Mobiveil-based PCIe controllers. It defines common library symbols, host support, and two platform drivers: NXP Layerscape Gen4 and generic Mobiveil AXI soft IP.

Important APIs, types, and functions: `PCIE_MOBIVEIL` is the common bool selected by host support. `PCIE_MOBIVEIL_HOST` depends on `PCI_MSI`, selects `IRQ_MSI_LIB`, and selects the common core. `PCIE_LAYERSCAPE_GEN4` depends on `ARCH_LAYERSCAPE || COMPILE_TEST` and `PCI_MSI`, selects host support, and describes Layerscape SoC Gen4 support. `PCIE_MOBIVEIL_PLAT` depends on `ARCH_ZYNQMP || COMPILE_TEST`, `OF`, and `PCI_MSI`, selects host support, and describes the Mobiveil AXI soft IP with up to eight windows.

Control flow: no runtime flow. Build selection controls which objects are compiled by the adjacent Makefile.

State and persistence: no runtime state. The persistent effect is kernel configuration symbols that determine object inclusion and dependency availability.

Dependencies and integration points: Linux PCI subsystem, PCI MSI, IRQ MSI library, OF for platform soft-IP, and architecture symbols for Layerscape and ZynqMP.

Risks: Both concrete drivers require `PCI_MSI`, so platforms without MSI cannot enable them even if legacy INTx exists. `PCIE_MOBIVEIL` is hidden and must be selected indirectly. Build coverage through `COMPILE_TEST` is allowed but runtime dependencies still need proper DT resources.

Test signals: Kconfig should select `pcie-mobiveil.o` and `pcie-mobiveil-host.o` with either platform option, expose menu entries under PCI, and fail neither allyesconfig nor architecture-specific builds.
