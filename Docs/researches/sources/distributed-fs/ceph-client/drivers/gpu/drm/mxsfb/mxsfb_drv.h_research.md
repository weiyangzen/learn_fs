# sources/distributed-fs/ceph-client/drivers/gpu/drm/mxsfb/mxsfb_drv.h

## Purpose
This header defines the private data model and exported helper functions for the classic MXSFB DRM driver.

## Important APIs, Types, And Data
`struct mxsfb_devdata` captures hardware-generation differences: register offsets for transfer count/current/next buffer, hsync width mask/shift, and booleans for overlay, CTRL2, and CRC32 support. `struct mxsfb_drm_private` stores devdata, MMIO, clocks, IRQ, DRM objects, primary/overlay planes, CRTC, encoder, connector, bridge, and CRC active state. It declares AXI clock helpers and `mxsfb_kms_init()`.

## Control Flow, State, And Integration
The header is the state contract between `mxsfb_drv.c` and `mxsfb_kms.c`. The probe path initializes fields; KMS code reads devdata to choose offsets and optional features. No persistence exists outside the live device instance.

## Risks And Test Signals
Incorrect devdata values affect all register programming paths. Optional fields such as `clk_disp_axi`, overlay plane, and CRC support require KMS and driver code to branch consistently. Test signals are successful compile, correct SoC match data, mode setting on V3/V4/V6 hardware, overlay initialization only where supported, and CRC source availability only on CRC-capable variants.
