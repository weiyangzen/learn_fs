# sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/dsi.c

## Purpose
`dsi.c` implements the Tegra MIPI DSI host and DRM encoder/connector output. It handles DSI register programming, packet sequence selection for video and command mode, D-PHY timing, MIPI calibration, panel prepare/enable sequencing, host FIFO transfers, runtime PM, regulator/clock/reset control, debugfs register dumps, and optional dual-channel ganged-mode operation.

## Important APIs, Types, and Functions
`struct tegra_dsi_state` extends connector state with D-PHY timing, bit period, refresh rate, lane count, pixel and byte clocks, hardware format, and pixel-format multiplier/divider. `struct tegra_dsi` embeds a host1x client, `tegra_output`, MIPI DSI host, register/clock/reset/regulator handles, MIPI calibration handle, FIFO depths, mode flags, format/lanes, debugfs files, and master/slave pointers for ganged mode.

Important flows include `tegra_dsi_encoder_atomic_check()` for clock/timing state calculation, `tegra_dsi_encoder_enable()` and `tegra_dsi_encoder_disable()` for modeset sequencing, `tegra_dsi_configure()` for packet/timing register programming, `tegra_dsi_host_transfer()` for MIPI DSI command transport, `tegra_dsi_host_attach()` and detach for peripheral/panel binding, and host1x/runtime PM callbacks.

## Control Flow
Probe allocates `struct tegra_dsi`, resolves ganged slave if referenced, probes generic output resources, sets default video/RGB888/4-lane mode, gets reset if needed, gets module/LP/parent clocks and regulator, sets clock parent routing, maps registers, requests the MIPI calibration device, registers the MIPI DSI host, enables runtime PM, and registers as a host1x client.

When a DSI peripheral attaches, the host stores mode flags, pixel format, and lane count; if a slave exists it sets up shared PLL parentage. Non-slave instances look up the panel and trigger HPD if a DRM connector already exists. Host1x init creates the DRM DSI connector and simple encoder for non-slave instances, attaches helpers, registers the connector, initializes generic output resources, and sets possible CRTCs.

Atomic check computes pixel clock, format multiplier/divider, aggregate lane count, hardware DSI format, vrefresh, byte clock, bit clock rounded to MHz, D-PHY timing defaults/validation, halves PLLD for hardware constraints, calculates shift-clock divider, and stores the selected DSI parent clock into the DC CRTC state. Encoder enable resumes host1x/runtime resources, enables MIPI calibration, calibrates pads, sets timeouts and PHY timing, prepares the panel, configures packet sequencing and horizontal packet lengths, enables the DC DSI output bit, commits DC state, powers DSI, and enables the panel. Disable reverses panel/video/DC state, waits idle, soft-resets, unprepares panel, powers DSI down, disables MIPI calibration, and suspends host1x resources.

Host transfer creates a MIPI packet, validates FIFO capacity, clears FIFO error flags, powers the controller, configures host control for HS/LP, host/video FIFO selection, CRC/ECC, optional BTA, writes header/payload to `DSI_WR_DATA`, triggers host transmission, optionally waits for and parses read/ACK response, and returns either received byte count or transmitted header+payload count.

## State and Persistence
Persistent runtime state includes panel/output binding, DSI host parameters from the attached peripheral, clock/regulator/reset/MIPI handles, FIFO depth constants, master/slave topology, and connector atomic state. Hardware state includes DSI power, control, packet sequence, packet length, timeout, PHY timing, pad, ganged-mode, FIFO, and trigger registers. There is no disk persistence.

## Dependencies and Integration Points
The file integrates with DRM connector/encoder helpers, generic Tegra output handling, Tegra DC clock setup and output-enable registers, MIPI DSI host APIs, DRM panel APIs, MIPI D-PHY timing helpers, Tegra MIPI calibration, host1x client lifecycle, runtime PM, clocks, reset, regulator, OF platform lookup, and local `dsi.h` register definitions.

## Risks
The DSI enable/disable order is panel- and hardware-sensitive; changing panel prepare/enable, DC DSI bit, DSI power, soft reset, or MIPI calibration order can break panels. `tegra_dsi_read_response()` appears to index `rx[j + k]` after already offsetting `rx = msg->rx_buf + j`, which is suspicious for long responses and deserves targeted review. Ganged mode assumes symmetric left/right split and shared PLL setup. `tegra_dsi_prepare()` logs MIPI enable/calibration failures but still returns 0 after those failures, so later register programming may proceed on a bad PHY. Packet length arithmetic subtracts fixed overhead and could underflow for invalid tiny modes if not filtered elsewhere.

## Test Signals
Signals include panel attach/detach HPD events, successful video-mode and command-mode panel enable, D-PHY timing validation, stable byte/bit clock and DC shift divider values, MIPI DCS reads/writes through host transfer, FIFO overflow/underflow recovery, idle wait success on disable, runtime PM cycles, debugfs `regs` while active, ganged dual-channel panels with correct left/right split, and no panel artifacts across suspend/resume.
