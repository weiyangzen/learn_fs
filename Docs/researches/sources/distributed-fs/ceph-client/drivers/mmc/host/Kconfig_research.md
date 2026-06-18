# sources/distributed-fs/ceph-client/drivers/mmc/host/Kconfig Research

## sources/distributed-fs/ceph-client/drivers/mmc/host/Kconfig

### Purpose
`drivers/mmc/host/Kconfig` defines the configuration menu for MMC/SD/SDIO host controller drivers and related host-side features. It controls which host drivers and support layers are buildable for a kernel configuration.

### Important APIs, Types, And Functions
This is declarative Kconfig rather than C. Important symbols include generic/debug/support options such as `MMC_DEBUG`, `MMC_SDHCI`, `MMC_SDHCI_IO_ACCESSORS`, `MMC_SDHCI_UHS2`, `MMC_SDHCI_PLTFM`, `MMC_CQHCI`, `MMC_HSQ`, and `MMC_SDHCI_EXTERNAL_DMA`; bus/platform families such as PCI, ACPI, OF/platform SDHCI, DesignWare, TMIO/SDHI, SPI, USB, PCI readers, and many SoC-specific controllers; and test/support choices such as `MMC_SDHCI_OF_ASPEED_TEST`.

### Control Flow
Kconfig dependency and selection flow determines menu visibility and build graph. For example SDHCI derivatives depend on `MMC_SDHCI` or `MMC_SDHCI_PLTFM`; some select `MMC_CQHCI`, `MMC_HSQ`, `MMC_SDHCI_IO_ACCESSORS`, DMA helpers, clocks/regulators/regmap, or platform-specific support. Tristate symbols allow built-in or module host drivers, while bool helper symbols are selected by concrete drivers.

### State, Persistence, And Dependencies
The persistent artifact is the kernel `.config`, which feeds Makefile object selection and preprocessor conditionals. Dependencies encode architecture, bus, DMA, OF/ACPI, PCI/USB, regulator, clock, reset, GPIO, thermal, KUnit, and compile-test availability.

### Integration Points
The symbols here map directly to object rules in `drivers/mmc/host/Makefile` and to feature checks throughout host drivers. Core SD/SDIO behavior depends indirectly on selected host capabilities such as SDHCI, UHS-II, CQHCI, HSQ, DMA, GPIO, and retuning support.

### Risks
Incorrect `depends on` or `select` relationships can create impossible builds, missing helper objects, or drivers visible on unsupported platforms. Silent helper symbols such as `MMC_SDHCI_IO_ACCESSORS` and `MMC_SDHCI_EXTERNAL_DMA` are easy to misuse. Selecting CQHCI/HSQ/UHS2 changes interactions with core SD and SDIO attach paths, so host capabilities must match actual hardware.

### Test Signals
Run Kconfig/compile matrix coverage for allmodconfig, allyesconfig, randconfig, COMPILE_TEST, key architectures, SDHCI PCI/ACPI/OF, UHS-II, CQHCI/HSQ, KUnit ASPEED tests, and module versus built-in combinations.
