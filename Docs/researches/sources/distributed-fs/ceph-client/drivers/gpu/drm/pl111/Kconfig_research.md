# sources/distributed-fs/ceph-client/drivers/gpu/drm/pl111/Kconfig

## Purpose
Defines the kernel configuration option for the DRM PL111 CLCD controller driver.

## Important APIs, Types, and Functions
Introduces `config DRM_PL111` as a tristate option titled "DRM Support for PL111 CLCD Controller". It depends on DRM, ARM/ARM64/COMPILE_TEST, optional VExpress config availability, and COMMON_CLK. It selects DRM client selection, KMS helper, GEM DMA helper, DRM bridge, and panel bridge support.

## Control Flow
Kconfig dependency resolution determines whether the driver can be built in, built as a module, or hidden. When enabled as a module, the help text states the module is `pl111_drm`.

## State and Persistence
No runtime state. The selected config persists in kernel `.config` and controls compilation of the PL111 object from the Makefile.

## Dependencies and Integration Points
Integrates the PL111 driver with DRM core, simple KMS helper usage, DMA GEM framebuffer allocation, bridge/panel display pipelines, common clock framework, and Arm platform support.

## Risks and Edge Cases
Dependency mistakes can expose the driver on platforms lacking clock or display bridge infrastructure. `VEXPRESS_CONFIG || VEXPRESS_CONFIG=n` allows builds when VExpress config is absent/disabled while avoiding incompatible enabled states.

## Test Signals
Signals are `allyesconfig`/`allmodconfig`/`COMPILE_TEST` coverage, module build as `pl111_drm`, and correct dependency selection for DRM helper symbols.
