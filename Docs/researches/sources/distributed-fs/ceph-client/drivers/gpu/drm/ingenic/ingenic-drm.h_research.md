# sources/distributed-fs/ceph-client/drivers/gpu/drm/ingenic/ingenic-drm.h

## Purpose
Defines Ingenic LCD controller register offsets, bit fields, descriptor fields, and the small private API shared between the main Ingenic DRM driver and optional IPU support.

## Important APIs, types, and functions
- Register offsets cover timing/config/control/state/DMA descriptor registers, RGB configuration, OSD control/status, alpha/keying, IPU restart, plane position/size, and priority config.
- Bit definitions cover LCD mode selection, sync polarity, bus width, descriptor width, burst size, EOF/SOF interrupts, frame enable, palette enable, OSD F0/F1 enables, IPU source selection, color depth, RGB ordering, descriptor size/cpos fields, and priority thresholds.
- Exports `ingenic_drm_plane_config()`, `ingenic_drm_plane_disable()`, and `ingenic_drm_map_noncoherent()`.
- Declares `extern struct platform_driver *ingenic_ipu_driver_ptr` for optional IPU driver registration.

## Control flow
No executable control flow exists. The macros are consumed by register programming and descriptor construction in `ingenic-drm-drv.c` and by optional IPU code that needs to configure or disable shared LCD planes.

## State and persistence
No C state is defined, but the constants describe persistent hardware state in LCD controller registers and DMA descriptors. The declared functions operate on the main driver's private state found from `struct device`.

## Dependencies and integration points
Depends on Linux bit operation/types headers and forward declarations for device, DRM plane, plane state, and platform driver. It is the private integration point between the LCD controller driver, IPU integration, and any local code that needs shared register definitions.

## Risks
Register-field mistakes are high impact because they affect DMA descriptor interpretation, pixel format, interrupts, and output timing. The typo-like `JZ_LCD_CTRL_LSB_FISRT` name must remain consistent with users. Exposing plane config/disable to IPU code requires stable semantics around plane identity and device drvdata.

## Test signals
Build coverage catches macro/API drift. Runtime validation comes indirectly from correct mode setup, plane enable/disable, descriptor DMA operation, OSD/IPU integration, interrupts, and format programming on all supported SoCs.
