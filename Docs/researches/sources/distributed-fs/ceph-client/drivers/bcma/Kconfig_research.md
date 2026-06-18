# sources/distributed-fs/ceph-client/drivers/bcma/Kconfig

Purpose: this Kconfig file declares the Broadcom-specific AMBA (BCMA) bus subsystem and its optional host, core-driver, flash, GPIO, debugging, and SoC support options.

Important APIs, types, and functions: symbols include `BCMA_POSSIBLE`, `BCMA`, `BCMA_BLOCKIO`, `BCMA_HOST_PCI_POSSIBLE`, `BCMA_HOST_PCI`, `BCMA_HOST_SOC`, `BCMA_DRIVER_PCI`, `BCMA_DRIVER_PCI_HOSTMODE`, `BCMA_DRIVER_MIPS`, `BCMA_PFLASH`, `BCMA_SFLASH`, `BCMA_NFLASH`, `BCMA_DRIVER_GMAC_CMN`, `BCMA_DRIVER_GPIO`, and `BCMA_DEBUG`.

Control flow: this file influences the Makefile composition and conditional compilation in BCMA sources. `BCMA` is the main tristate menu. Host PCI support selects the PCI core driver by default when PCI is built in. MIPS support enables parallel/NAND flash defaults. GPIO support depends on `GPIOLIB` and selects `GPIOLIB_IRQCHIP` for SoC hosting.

State and persistence: configuration state determines which BCMA features are built. No runtime state is stored here.

Dependencies and integration points: it integrates with architecture features (`HAS_IOMEM`, `HAS_DMA`, `MIPS`), PCI, legacy PCI host-mode support, GPIOLIB, and compile-test coverage. The resulting symbols control the object list and inline fallbacks in `bcma_private.h`.

Risks: dependency mistakes can produce invalid combinations, such as MIPS-only host-mode support without needed PCI infrastructure or GPIO IRQ support without the IRQ chip helper. Defaults enable several features, so build coverage must account for more than the minimal bus core.

Test signals: configuration matrix builds should cover PCI-hosted, SoC-hosted, MIPS, GPIO, and debug combinations. The adjacent Makefile should include the expected object files for each symbol combination.
