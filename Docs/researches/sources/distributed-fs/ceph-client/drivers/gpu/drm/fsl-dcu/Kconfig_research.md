# sources/distributed-fs/ceph-client/drivers/gpu/drm/fsl-dcu/Kconfig

## Purpose
This Kconfig entry defines the build option for the Freescale DCU DRM driver. It declares the hardware support as tristate and encodes the core subsystem dependencies and selected helper libraries needed by the driver.

## Important APIs, Types, and Functions
The config symbol is `DRM_FSL_DCU` with prompt `DRM Support for Freescale DCU`. It depends on `DRM`, `OF`, `ARM`, and `COMMON_CLK`. It selects `BACKLIGHT_CLASS_DEVICE`, `DRM_CLIENT_SELECTION`, `DRM_GEM_DMA_HELPER`, `DRM_KMS_HELPER`, `DRM_PANEL`, `REGMAP_MMIO`, `VIDEOMODE_HELPERS`, and conditionally `MFD_SYSCON` for `SOC_LS1021A`.

## Control Flow
There is no runtime control flow. At configuration time, this symbol controls whether the Makefile builds the `fsl-dcu-drm` module or built-in driver. The selected symbols ensure the source files have the helpers required for KMS, panels, DMA GEM buffers, regmap MMIO access, backlight, and videomode conversion.

## State and Persistence Behavior
Kconfig state persists in the kernel `.config`. If selected as `m`, the resulting module is named `fsl-dcu-drm`; if built in, the driver initializes with the kernel.

## Dependencies and Integration Points
The entry integrates with the DRM subsystem, ARM device-tree platforms, common clock framework, Freescale/NXP DCU device-tree nodes, panel/backlight infrastructure, and LS1021A syscon routing needs. The Makefile consumes `CONFIG_DRM_FSL_DCU`.

## Risks
The ARM dependency excludes non-ARM platforms even if similar DCU IP appeared elsewhere. Conditional `MFD_SYSCON` only for LS1021A means other SoCs needing syscon support would require Kconfig updates. Selected helper symbols increase build surface and must match actual driver use. The help text says "an Freescale" but that is cosmetic.

## Test Signals
Run Kconfig build coverage for disabled, module, and built-in configurations; verify dependency selection; build on LS1021A and non-LS1021A ARM configs; and confirm the module name and autoload behavior with matching device-tree compatibles.
