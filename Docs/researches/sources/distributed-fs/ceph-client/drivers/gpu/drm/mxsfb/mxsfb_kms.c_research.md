# sources/distributed-fs/ceph-client/drivers/gpu/drm/mxsfb/mxsfb_kms.c

## Purpose
`mxsfb_kms.c` implements KMS for classic MXS/i.MX LCDIF controllers: CRTC mode programming, controller reset/enable/disable, primary and optional overlay planes, vblank, CRC capture, and encoder/CRTC registration.

## Important APIs, Types, And Functions
Important functions include `mxsfb_set_formats`, `mxsfb_set_mode`, `mxsfb_enable_controller`, `mxsfb_disable_controller`, `mxsfb_reset_block`, `mxsfb_crtc_mode_set_nofb`, atomic CRTC enable/disable/flush/check helpers, vblank enable/disable, CRC source callbacks, primary/overlay plane updates, and `mxsfb_kms_init`. Supported primary formats are RGB565 and XRGB8888; overlay formats include XRGB/ARGB 4444, 1555, RGB565, XRGB8888, and ARGB8888. Only linear modifiers are supported.

## Control Flow, State, And Integration
Enable resumes runtime PM, enables AXI, turns vblank on, chooses a bridge or connector bus format with RGB888 fallback, resets the block, programs format/timing/clock, writes current and next buffer addresses, then starts the controller. Mode programming writes transfer count, VDCTRL timing registers, bus polarity, dotclock edge, and valid-data count. Controller enable turns on display clocks, sets outstanding requests on newer IP, enables sync signals, sets underflow recovery, and starts DMA. Disable stops dotclock mode, polls for `CTRL_RUN` clear, disables sync signals and clocks, sends pending events, turns vblank off, disables AXI, and drops runtime PM.

## State, Dependencies, Risks, And Tests
State includes MMIO registers, devdata-specific offsets, runtime clocks, optional overlay registers, and `crc_active`. Dependencies include DRM atomic helpers, panel/bridge bus metadata, DMA GEM helpers, PM runtime, and `mxsfb_regs.h`. Risks include ignored reset errors beyond an early return from mode programming, fallback bus formats, the overlay 64-byte DMA offset hack, no scaling support, strict linear layout, and underflow recovery relying on undocumented behavior. Test signals are primary/overlay plane tests, vblank/page-flip timing, CRC readout, reset/enable/disable under repeated modesets, and hardware tests on V3/V4/V6 variants.
