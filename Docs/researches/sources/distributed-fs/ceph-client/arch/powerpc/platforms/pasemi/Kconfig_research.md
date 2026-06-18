# sources/distributed-fs/ceph-client/arch/powerpc/platforms/pasemi/Kconfig

Purpose: Kconfig options for PA Semi PWRficient SoC platforms, Nemo motherboard support, IOMMU behavior, and GPIO MDIO.

Important APIs and control flow: `PPC_PASEMI` depends on big-endian PPC64 Book3S and selects MPIC, forced PCI, udbg, hash MMU, and broken MPIC register-read handling. `PPC_PASEMI_NEMO` adds i8259 support for AmigaOne X1000/SB600. `PPC_PASEMI_IOMMU` and `PPC_PASEMI_IOMMU_DMA_FORCE` govern IOB translation and DMA-engine bypass behavior. `PPC_PASEMI_MDIO` builds a PHYLIB GPIO MDIO driver.

State, dependencies, and risks: state is compile-time feature inclusion. Dependencies determine machine descriptor capabilities, IOMMU setup, and southbridge workarounds. Risks include big-endian-only assumptions, optional IOMMU behavior changing DMA addressability, and MDIO default-y pulling platform code into builds with PHYLIB. Test signals are config dependency resolution, Nemo boot with i8259, IOMMU on/off boot, and PA Semi platform link coverage.
