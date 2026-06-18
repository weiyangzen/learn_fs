# sources/distributed-fs/ceph-client/drivers/gpu/drm/mxsfb/lcdif_kms.c

## Purpose
`lcdif_kms.c` implements the LCDIFv3 KMS pipeline: primary plane validation/update, CRTC atomic state, mode programming, colorspace conversion, buffer-address programming, vblank control, and CRTC/plane registration.

## Important APIs, Types, And Functions
`struct lcdif_crtc_state` extends `drm_crtc_state` with bridge-selected `bus_format` and `bus_flags`. Key functions are `lcdif_set_formats`, `lcdif_set_mode`, `lcdif_enable_controller`, `lcdif_disable_controller`, `lcdif_reset_block`, `lcdif_crtc_atomic_check`, `lcdif_crtc_atomic_flush`, `lcdif_crtc_atomic_enable`, `lcdif_crtc_atomic_disable`, vblank enable/disable helpers, primary-plane `atomic_check`/`atomic_update`, and `lcdif_kms_init`. Supported primary formats include RGB565/RGB888/XRGB variants and packed YCbCr formats; only linear modifiers are accepted. Plane color properties support BT.601, BT.709, BT.2020 and limited/full range.

## Control Flow, State, And Integration
Atomic check requires the primary plane when the CRTC is active and derives a consistent input bus format/flags from connected bridge state. Enable sets the pixel clock, resumes runtime PM, resets the hardware, programs bus/pixel format and CSC coefficients, writes timing and pitch registers, writes the initial DMA address to low/high descriptor registers, enables FIFO panic priority boosting, turns on display and descriptor enable, then enables vblank. Flush sets `SHADOW_LOAD_EN` and arms or sends pending vblank events. Disable turns vblank off, disables the controller with a poll, sends any pending event, and drops runtime PM.

## State, Dependencies, Risks, And Tests
State is volatile MMIO plus atomic CRTC state. Dependencies include DRM atomic helpers, bridge bus-format negotiation, DMA GEM helpers, media bus formats, runtime PM, and `lcdif_regs.h` macros. Risks include unknown bridge formats falling back to RGB888, CSC coefficient mistakes, a disabled primary plane on active CRTC, timeout disabling the controller, and address handling relying on the 36-bit DMA mask. Test signals are atomic modeset/page-flip tests, YUV-to-RGB/RGB-to-YCbCr visual validation, vblank event timing, suspend/resume, and underrun/panic behavior under memory pressure.
