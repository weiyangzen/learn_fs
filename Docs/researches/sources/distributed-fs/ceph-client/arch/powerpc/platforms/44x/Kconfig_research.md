<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/44x/Kconfig -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/44x/Kconfig

Purpose: defines the 44x/47x platform, board, CPU-variant, GPIO, PCIe, MSI, and errata configuration menu entries that control which 44x source files and SoC support blocks are built.

Important APIs/types/functions: Kconfig symbols include board selectors such as `EBONY`, `SAM440EP`, `WARP`, `CANYONLANDS`, `ISS4xx`, `CURRITUCK`, `FSP2`, and `AKEBONO`; shared selector `PPC44x_SIMPLE`; driver-like `PPC4xx_GPIO`; CPU feature symbols `440EP`, `440EPX`, `440GRX`, `440GP`, `440GX`, `440SPe`, `460EX`, `460SX`, `476FPE`, `APM821xx`; and errata symbols `476FPE_ERR46` and `IBM440EP_ERR42`.

Control flow: Kconfig selection drives compilation through the 44x Makefile and other architecture Makefiles. Board symbols select CPU variants and subsystem dependencies such as `FORCE_PCI`, `PPC4xx_PCI_EXPRESS`, `PCI_MSI`, `PPC4xx_HSTA_MSI`, `COMMON_CLK`, `I2C`, USB host support, and EMAC PHY helpers.

State and persistence: persistent build-time state only; no runtime state. The selected symbols determine machine descriptors, interrupt controllers, PCI support, idle/CPM behavior, and board quirks.

Dependencies and integration: integrates with architecture `44x` and `PPC_47x` options, PCI, MPIC/UIC, EMAC, USB, I2C, GPIOLIB, SWIOTLB, and linker errata options.

Risks and test signals: incorrect `select` chains can omit mandatory interrupt/PCI/clock drivers or build incompatible board combinations. Test with `olddefconfig`/`randconfig` for representative boards, compile coverage for simple 44x and 47x, and boot logs verifying selected machine descriptors and bus probes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/44x/Kconfig -->
