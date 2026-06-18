# sources/distributed-fs/ceph-client/drivers/gpu/drm/mxsfb/lcdif_drv.h

## Purpose
This header defines the private driver state and KMS initialization contract for the LCDIFv3 DRM driver.

## Important APIs, Types, And Data
`struct lcdif_drm_private` stores the MMIO `base`, three clocks (`clk`, `clk_axi`, `clk_disp_axi`), IRQ number, back-pointer to `struct drm_device`, a primary plane, and one CRTC. `to_lcdif_drm_private()` returns `drm->dev_private`, and `lcdif_kms_init()` is declared for the driver setup file.

## Control Flow, State, And Integration
The header is shared by `lcdif_drv.c` and `lcdif_kms.c`. `lcdif_drv.c` allocates and fills the structure, while `lcdif_kms.c` consumes it for register programming, plane setup, vblank control, and atomic CRTC operations. State is not persistent across unload; it is devm/kzalloc-backed runtime driver state.

## Risks And Test Signals
Because this is the central private-state contract, field layout changes affect both driver and KMS files. The comment notes i.MXRT overlay-plane support is not implemented yet, so assumptions of a single primary plane are embedded in current code. Test signals are clean compilation, successful `drm->dev_private` casts, and KMS init paths finding initialized MMIO and clock fields.
