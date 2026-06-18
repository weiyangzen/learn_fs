# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/registers/display/hdmi.xml

## Purpose
This XML defines the MSM HDMI controller and multiple HDMI PHY/PLL register maps. It covers HDMI core enable, audio packet/ACR/infoframe/generic packet programming, HDCP authentication and DDC handshakes, DDC/I2C transactions, HPD, CEC, video timing, frame control, audio interrupts, PHY reset, legacy PHY variants, 8x74/8996/8998 PHY blocks, and QSERDES common/TX PLL domains.

## Important APIs, Types, and Functions
Generated APIs include `REG_HDMI_*`, `REG_HDMI_8x60_*`, `REG_HDMI_8960_*`, `REG_HDMI_8x74_*`, `REG_HDMI_8996_*`, `REG_HDMI_PHY_QSERDES_*`, and `REG_HDMI_8998_*` macros. Important enums are `hdmi_hdcp_key_state`, `hdmi_ddc_read_write`, `hdmi_acr_cts`, and `hdmi_cec_tx_status`. Key controller registers include `CTRL`, audio packet and ACR controls, VBI/infoframe/generic packet controls, AVI/audio/vendor info arrays, HDCP control/status/DDC/SHA/receiver-port registers, DDC control/status/speed/setup/transaction/data registers, HPD status/control, CEC control/data/status/interrupt registers, timing registers, `FRAME_CTRL`, audio interrupt, and `PHY_CTRL`.

## Control Flow
HDMI modeset flow programs PHY/PLL for the pixel clock, writes video timing and frame polarity/interlace fields, configures AVI/audio/vendor infoframes and audio clock regeneration, then enables the controller. HPD flow uses HPD status/control/interrupt registers, DDC flow sequences I2C transactions through DDC control/data/status registers, and HDCP flow uses the HDCP control/status/DDC/SHA/register-port block for authentication. CEC flow uses transmit/receive data, retry/status, address, timing, and interrupt registers.

## State and Persistence Behavior
Runtime state includes controller enable/encryption mode, active video timings, infoframe payloads, audio clock regeneration values, DDC transaction state, HDCP authentication/key/SHA state, HPD masks/status, CEC transmit/receive state, PHY power/reset/PLL state, and QSERDES calibration/tuning. This hardware state is reprogrammed on hotplug, modeset, audio changes, HDCP transitions, CEC activity, and resume.

## Dependencies and Integration Points
The generated macros are used by `hdmi.c`, `hdmi_bridge.c`, `hdmi_hpd.c`, `hdmi_hdcp.c`, and per-SoC PHY drivers. Integration points include DRM bridge/connector helpers, EDID/DDC, HDMI audio, HDCP core policy, CEC framework, hotplug handling, clock framework, regulator/reset management, and SoC-specific PHY tuning tables.

## Risks
This file has many hardware generations in one XML, so register-name collisions and same-offset aliases must be handled by the correct domain. HDCP and DDC status/ack/mask bits are sequencing-sensitive and can deadlock authentication or EDID reads. Infoframe length/checksum and ACR fields must match HDMI spec expectations. QSERDES PLL fields are dense and generation-specific; wrong values can break high pixel clocks or hotplug recovery.

## Test Signals
Signals include generated-header build, HDMI hotplug and EDID reads, modesets across pixel-clock ranges, AVI/audio/vendor infoframe validation, audio playback and ACR checks, HDCP authentication success/failure paths, DDC timeout/NACK handling, CEC transmit/receive tests, suspend/resume, and PHY lock/status validation for each supported SoC.
