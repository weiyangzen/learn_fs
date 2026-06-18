<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/verisilicon/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/verisilicon/Kconfig

## Purpose
`verisilicon/Kconfig` declares the `DRM_VERISILICON_DC` build option for VeriSilicon DC-series display controllers. It documents module naming and selects the DRM, bridge, helper, DMA GEM, regmap MMIO, and videomode infrastructure needed by the driver.

## Important APIs, Types, and Functions
The key symbol is `config DRM_VERISILICON_DC`, a tristate depending on `DRM`, `COMMON_CLK`, and either `RISCV` or `COMPILE_TEST`. It selects `DRM_BRIDGE_CONNECTOR`, `DRM_CLIENT_SELECTION`, `DRM_DISPLAY_HELPER`, `DRM_GEM_DMA_HELPER`, `DRM_KMS_HELPER`, `REGMAP_MMIO`, and `VIDEOMODE_HELPERS`.

## Control Flow
Kconfig evaluation exposes the driver only on supported architectures or compile-test builds. When enabled as built-in or module, the Makefile builds `verisilicon-dc.o`, allowing the platform driver to bind to `verisilicon,dc` nodes.

## State and Persistence Behavior
There is no runtime state in this file. Its persistent effect is build-time configuration, module availability, and selected helper subsystems.

## Dependencies and Integration Points
The symbol integrates with the DRM subsystem menu, common clock framework, RISC-V SoC builds, module autoloading, and the adjacent Makefile. Selected dependencies match the runtime code's use of atomic KMS, bridge connectors, DMA-backed GEM dumb buffers, and MMIO regmaps.

## Risks
Missing selects would create link or compile failures in minimal configs. The architecture dependency may hide the driver from non-RISC-V SoCs if VeriSilicon DC IP appears elsewhere. Over-selection increases kernel image size but keeps the small driver self-contained.

## Test Signals
Build coverage should include `m`, `y`, and `COMPILE_TEST` configurations, allmodconfig/allyesconfig, and minimal DRM+COMMON_CLK configs on RISC-V.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/verisilicon/Kconfig -->
