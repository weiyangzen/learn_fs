
<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/lgm/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/dma/lgm/Kconfig

Purpose: declares the build-time option for Intel Lightning Mountain centralized DMA controllers.

Important APIs and control flow: `config INTEL_LDMA` is a boolean option labeled "Lightning Mountain centralized DMA controllers". It depends on `X86 || COMPILE_TEST` and selects `DMA_ENGINE` plus `DMA_VIRTUAL_CHANNELS`. Its help text describes DMA support for on-chip devices including HSNAND and GSWIP.

State and persistence behavior: no runtime state is present. The option controls whether `lgm-dma.o` is built into the kernel because it is `bool`, matching the driver’s `builtin_platform_driver()` registration.

Dependencies and integration points: integrates with the parent DMA Kconfig hierarchy and the local Makefile. Selecting DMAEngine and virt-dma guarantees the symbols used by `lgm-dma.c` are available.

Risks and test signals: risks include lack of module build coverage due to `bool`, architecture gating hiding compile errors outside X86 unless `COMPILE_TEST` is enabled, and missing dependencies for reset/clk/OF APIs if parent menus change. Test signals are successful `CONFIG_INTEL_LDMA=y` builds, visible platform driver registration, and compile-test coverage with OF/reset/clk stubs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/lgm/Kconfig -->
