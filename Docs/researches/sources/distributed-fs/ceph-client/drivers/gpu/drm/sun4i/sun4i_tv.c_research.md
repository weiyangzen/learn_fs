<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun4i_tv.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun4i_tv.c

## Purpose

`sun4i_tv.c` implements the Allwinner A10 composite TV encoder as a DRM TVDAC encoder and composite connector. It programs fixed PAL/NTSC register tables, exposes the DRM TV mode property, and applies display-engine color correction for analog output.

## Important APIs, Types, And Functions

Important structs are `struct tv_mode` plus small level/gain/resync parameter structs, and `struct sun4i_tv`. Key functions are `sun4i_tv_bind()`, `sun4i_tv_unbind()`, `sun4i_tv_enable()`, `sun4i_tv_disable()`, `sun4i_tv_find_tv_by_mode()`, and connector reset helpers using `drm_atomic_helper_connector_tv_reset()`. Static `tv_modes[]` holds PAL and NTSC programming constants.

## Control Flow

Probe registers a component. Bind maps and regmaps TVE registers, deasserts reset, enables clock, creates a simple TVDAC encoder, discovers possible CRTCs from OF graph, creates a composite connector, enables interlace, creates TV properties for NTSC/PAL, sets NTSC default, and attaches encoder. Atomic enable reads connector TV mode state, selects `tv_mode`, programs DAC mapping, TV standard, DAC levels, chroma frequency, porches, line count, blank/black levels, burst/gain/sync/VBI/active-line/resync registers, applies engine color correction, and enables TVE. Disable clears enable and disables color correction.

## State And Persistence Behavior

Persistent driver state is connector, encoder, clock, reset, regmap, and driver pointer. Hardware state persists in the TVE analog registers and engine color-correction configuration. Connector TV mode is DRM atomic state and defaults to NTSC.

## Dependencies And Integration Points

It depends on DRM TV connector helpers, component framework, regmap, clocks/resets, OF CRTC matching, `sunxi_engine_apply_color_correction()`, and TCON channel 1 timing selected through encoder type `DRM_MODE_ENCODER_TVDAC`.

## Risks And Test Signals

Risks include hardcoded vendor/BSP analog constants, limited mode table to PAL/NTSC, interlace timing sensitivity, no load-detect implementation despite status register definitions, and color-correction pairing on disable. Test PAL/NTSC modes, connector property changes, interlaced CRTC timing, enable/disable, analog output quality, probe error unwinds, and color-correction state after TV off.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun4i_tv.c -->
