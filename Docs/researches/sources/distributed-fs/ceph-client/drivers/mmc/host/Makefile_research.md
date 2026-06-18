# sources/distributed-fs/ceph-client/drivers/mmc/host/Makefile Research

## sources/distributed-fs/ceph-client/drivers/mmc/host/Makefile

### Purpose
`drivers/mmc/host/Makefile` maps MMC host Kconfig symbols to compiled object files and composite driver objects.

### Important APIs, Types, And Functions
The file contains kbuild object rules such as `obj-$(CONFIG_MMC_SDHCI) += sdhci.o`, platform-specific SDHCI objects, DesignWare objects, TMIO/SDHI objects, USB/PCI reader objects, CQHCI/HSQ objects, and SoC-specific drivers. Composite objects include `armmmci-y`, `sdhci-pci-y`, `octeon-mmc-objs`, `thunderx-mmc-objs`, `meson-mx-sdhc-objs`, `cqhci-y`, `cqhci-$(CONFIG_MMC_CRYPTO)`, and `sdhci-xenon-driver-y`.

### Control Flow
Kbuild includes objects when the corresponding `CONFIG_` symbol is `y` or `m`. Composite assignments collect multiple `.o` files into one module/built-in object. A small conditional adds `-DDEBUG` to `cb710-mmc` when `CONFIG_CB710_DEBUG=y`.

### State, Persistence, And Dependencies
The Makefile stores no runtime state. Its persistent outputs are built objects/modules determined by `.config`. It depends on Kconfig symbol names remaining synchronized with driver source files and module composition.

### Integration Points
This file is the build counterpart to host `Kconfig`. Selected host drivers provide `struct mmc_host_ops` and capabilities consumed by the SD/SDIO core files researched in this subset. Missing or stale object rules directly affect whether hardware support exists in the kernel image/modules.

### Risks
Symbol/object mismatches cause selected drivers not to build or stale objects to be referenced. Composite driver ordering and conditional additions must include all required companion files, such as PCI SDHCI vendor pieces, CQHCI crypto support, and Xenon PHY support. Duplicate or obsolete config names can hide build gaps until a specific config is tested.

### Test Signals
Validate with `make drivers/mmc/host/` under allmodconfig/allyesconfig/randconfig, module install checks for expected names, config-symbol-to-object audits, and targeted builds for composite drivers such as `sdhci-pci`, `cqhci`, `armmmci`, `sdhci-xenon-driver`, and Renesas SDHI variants.
