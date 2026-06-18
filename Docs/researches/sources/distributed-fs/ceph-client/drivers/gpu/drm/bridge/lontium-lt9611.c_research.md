# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/lontium-lt9611.c

## Purpose

This driver supports the Lontium LT9611 MIPI DSI to HDMI bridge. It handles one or two DSI inputs, HDMI HPD/EDID, mode programming, PLL/PCR setup, HDMI PHY and infoframes, and HDMI audio through DRM bridge HDMI audio callbacks.

## Important APIs, Types, And Functions

`struct lt9611` stores the bridge, next bridge, regmap, DSI endpoint nodes/devices, AC/DC HDMI PHY mode, reset/enable GPIOs, power/sleep flags, two regulators, cached connector status, and a 256-byte EDID buffer. The regmap uses page register `0xff`.

Configuration functions include `lt9611_mipi_input_analog()`, `lt9611_mipi_input_digital()`, `lt9611_mipi_video_setup()`, `lt9611_pll_setup()`, `lt9611_pcr_setup()`, `lt9611_hdmi_tx_digital()`, `lt9611_hdmi_tx_phy()`, and `lt9611_video_check()`. Bridge ops include detect, EDID, HPD enable, atomic pre_enable/enable/disable/post_disable, input bus format, HDMI infoframe write/clear hooks, TMDS rate validation, and HDMI audio startup/prepare/shutdown.

## Control Flow

Probe validates I2C, initializes regmap, parses DSI0/DSI1 endpoints and output bridge on port 2, gets GPIOs/regulators, asserts optional 5V enable, powers and resets the chip, reads revision, requests the threaded IRQ, disables the default audio infoframe, fills HDMI bridge metadata/audio capabilities, adds the bridge, attaches primary and optional secondary DSI devices, and enables HPD interrupts.

Atomic enable locates the active connector and adjusted mode, configures DSI input selection for single/dual/port-B modes, programs TX PLL postdivider based on pixel clock, writes MIPI timing registers, sets PCR, ensures chip power-on, configures analog MIPI input, updates HDMI infoframes, selects HDMI/DVI digital mode, configures PHY, waits, logs video check values, and enables HDMI output. Post-disable enters sleep setup; pre-enable exits sleep. EDID reading powers the chip and reads two 128-byte blocks through an internal DDC engine.

## State And Persistence

`power_on` and `sleep` prevent duplicate power setup and select resume behavior. `status` caches detect result. `edid_buf` stores the latest two-block EDID read. DSI endpoint references are retained until remove. Registers retain mode/audio/infoframe state until power-off, sleep, or reset.

## Dependencies And Integration Points

The driver integrates I2C/regmap, DRM bridge HDMI operations, DRM HDMI state helper, MIPI DSI, OF graph, GPIO, regulators, IRQs, and HDMI codec bridge callbacks. It attaches a downstream bridge found at DT port 2 and advertises `DRM_BRIDGE_OP_HDMI`, audio, SPD infoframe, EDID, detect, HPD, and modes.

## Risks And Edge Cases

EDID support is limited to base plus one extension block. Mode validation allows up to 3840 horizontal pixels but requires dual DSI for width above 2000 and caps TMDS at 297 MHz. Atomic enable can fail mid-sequence without rollback. IRQ handling reports HPD/video-input changes but does not inspect every error source. HDMI audio prepare only accepts 48 kHz and 96 kHz. DSI lanes are fixed to 4 in attach. Register writes are often unchecked.

## Test Signals

Validate single DSI0, single DSI1, and dual DSI routing; HPD IRQs; EDID reads; 1080p and 4K30 dual-port modes; HDMI versus DVI sink infoframe behavior; sleep/post-disable and pre-enable; 48/96 kHz HDMI audio; regulator/GPIO/IRQ failures; and removal after both DSI devices attach.
