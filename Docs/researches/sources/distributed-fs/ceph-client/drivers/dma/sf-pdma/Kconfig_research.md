# sources/distributed-fs/ceph-client/drivers/dma/sf-pdma/Kconfig

Purpose: Kconfig entry for the SiFive Platform DMA controller driver.

Important APIs/types/functions: defines `config SF_PDMA` as a tristate option named "Sifive PDMA controller driver". It depends on `HAS_IOMEM` and selects `DMA_ENGINE` plus `DMA_VIRTUAL_CHANNELS`.

Control flow: when enabled as built-in or module, the build system compiles `sf-pdma.o` through the adjacent Makefile. Selecting DMAEngine and virtual channels ensures required framework support for `sf-pdma.c`.

State/persistence: no runtime state; this is build configuration only.

Dependencies/integration: integrates with the kernel DMAEngine Kconfig hierarchy and gates the SiFive/Microchip PDMA platform driver.

Risks: the option does not depend on `OF`, even though the driver uses OF match/controller registration; this may be acceptable through compile-time stubs or broader DMAEngine configuration but should be considered in randconfig failures.

Test signals: `allyesconfig`, `allmodconfig`, `COMPILE_TEST` style builds, and configurations with `HAS_IOMEM=n` confirming the option is hidden.
