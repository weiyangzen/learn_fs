# sources/distributed-fs/ceph-client/drivers/pci/Kconfig

Purpose: top-level PCI subsystem configuration. It defines the main `PCI` menu and options controlling core PCI, PCIe, MSI, quirks, IOV, ATS/PRI/PASID, DOE, TSM, P2PDMA, Hyper-V, dynamic OF nodes, hierarchy tuning, VGA arbitration, and subordinate PCI menus.

Important symbols: `HAVE_PCI` gates visibility, `FORCE_PCI` selects PCI unconditionally, `PCI` depends on `HAVE_PCI` and `MMU`, `PCI_MSI` selects generic MSI IRQ support, `PCI_IOV` selects `PCI_ATS`, `PCI_PRI` and `PCI_PASID` also select `PCI_ATS`, and `PCI_TSM` selects `PCI_IDE`, `PCI_DOE`, and `TSM`. It sources `pcie`, hotplug, controller, endpoint, switch, and pwrctrl Kconfigs.

Control flow/state: Kconfig state controls which objects the PCI Makefile builds and which code paths are compiled in core files such as `ats.c`, `access.c`, and controller drivers. The MPS/MRRS choice defaults to `PCIE_BUS_DEFAULT` and can be overridden at boot.

Dependencies/integration: integrates arch-provided PCI support with subsystem features and platform controller menus. Risks include hidden selects enabling security-sensitive capability code, compile-test dependency drift, and feature combinations requiring IOMMU/MSI/ACPI/OF support. Test signals include Kconfig dependency resolution, allmodconfig/allyesconfig builds, boot parameter overrides, and feature-specific object inclusion.
