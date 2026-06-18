# sources/distributed-fs/ceph-client/drivers/gpu/drm/rockchip/rk3066_hdmi.c

## Purpose
Implements a native Rockchip RK3066 HDMI bridge/encoder driver, including MMIO programming, DDC/EDID I2C adapter, HPD IRQ handling, bridge HDMI infoframe callbacks, video timing setup, and component integration.

## Important APIs, Types, And Functions
Key state types are `hdmi_data_info`, `rk3066_hdmi_i2c`, and `rk3066_hdmi`. Important functions include power-mode sequencing, I2C init/xfer/read/write, AVI infoframe write/clear, video timing setup, PHY config, bridge atomic enable/disable, detect/EDID/mode_valid, IRQ handlers, `rk3066_hdmi_register()`, and bind/unbind.

## Control Flow
Bind maps registers, requests IRQ, enables hclk, obtains GRF, initializes internal divider and interrupt masks, registers the DRM bridge/connector, then requests threaded IRQ. Atomic enable chooses VOP mux in GRF, configures HDMI video: mute, power mode B, RGB 8-bit input/output, timing registers, HDMI/DVI mode, infoframes, PHY magic values by TMDS clock, power mode E, DDC clock, and unmute video. Atomic disable mutes/reset audio/video and powers down to mode A. DDC transfers program EDID segment/word and wait for EDID completion IRQ.

## State And Persistence
Tracks current `tmdsclk`, HDMI colorimetry/VIC data, I2C DDC state, completion status, connector, bridge, encoder, GRF, hclk, and MMIO base. Hardware registers persist power, timing, PHY, interrupt, and infoframe state.

## Dependencies And Integration Points
Depends on DRM bridge connector and HDMI state helpers, I2C core, syscon GRF, clock framework, IRQ completions, and Rockchip CRTC state.

## Risks
PHY configuration uses undocumented magic values. The DDC adapter only supports EDID-style read sequences and returns `-EINVAL` for general writes. Mode validation only accepts CEA VIC > 1. HDMI Vendor Specific InfoFrame is stubbed with a warning.

## Test Signals
CEA mode validation, EDID reads across segment/address messages, HPD and MSENS IRQs, power-mode transition timing, VOP mux selection, AVI infoframe writes, high/medium/low TMDS PHY tables, and cleanup after IRQ or registration failures.
