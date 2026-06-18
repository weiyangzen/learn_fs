# sources/distributed-fs/ceph-client/arch/powerpc/platforms/pasemi/Makefile

Purpose: object list for PA Semi platform core, optional GPIO MDIO, and optional MSI support.

Important APIs and control flow: always builds setup, PCI, time, idle, powersave assembly, IOMMU, DMA library, and misc I2C registration. Adds `gpio_mdio.o` under `CONFIG_PPC_PASEMI_MDIO` and `msi.o` under `CONFIG_PCI_MSI`.

State, dependencies, and risks: state is link-time object inclusion and ordering. Dependencies include Kconfig symbols and exported functions from `dma_lib.c`/`pasemi.h`. Risks are building IOMMU object even when runtime disabled, and optional MSI/MDIO behavior changing PCI/PHY integration. Test signals are link success across MSI/MDIO/IOMMU/Nemo combinations.
