
# sources/distributed-fs/ceph-client/drivers/gpu/drm/hisilicon/hibmc/Kconfig

## Purpose
`hibmc/Kconfig` defines the kernel configuration option for the Hisilicon HIBMC DRM driver.

## Important APIs, Types, And Functions
It declares `config DRM_HISI_HIBMC` as a tristate option named "DRM Support for Hisilicon Hibmc". It depends on `DRM` and `PCI`, and selects `DRM_CLIENT_SELECTION`, `DRM_DISPLAY_HELPER`, `DRM_DISPLAY_DP_HELPER`, `DRM_KMS_HELPER`, `DRM_VRAM_HELPER`, `DRM_TTM`, `DRM_TTM_HELPER`, `I2C`, and `I2C_ALGOBIT`.

## Control Flow
There is no runtime flow. The option controls whether `hibmc/Makefile` builds the `hibmc-drm` driver as built-in or module.

## State And Persistence
The file stores build-time configuration state. When built as a module, the module is named `hibmc-drm`.

## Dependencies And Integration Points
The selected helpers match the driver tree's PCI device model, VRAM/TTM memory management, KMS helper use, DisplayPort AUX/link helpers, and I2C bit-banged VGA/DDC support.

## Risks
The option selects a broad set of DRM and I2C helpers; missing selections would break link or feature support in HIBMC display, DP, or VDAC/I2C code. PCI dependency means this option is not available for non-PCI HIBMC integration without Kconfig changes.

## Test Signals
Configuration and build tests should cover `CONFIG_DRM_HISI_HIBMC=y/m`, verify all selected helper symbols are enabled, and confirm the resulting module links all HIBMC core, DP, debugfs, VDAC, and I2C objects.
