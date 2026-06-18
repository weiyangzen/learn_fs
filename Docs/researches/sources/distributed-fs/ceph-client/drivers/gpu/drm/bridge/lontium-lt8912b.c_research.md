# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/lontium-lt8912b.c

## Purpose

This driver supports the Lontium LT8912B bridge, converting MIPI DSI input to an HDMI output path with auxiliary LVDS-related programming. It registers a DRM bridge, attaches a DSI peripheral to the upstream DSI host, delegates EDID/HPD to the downstream HDMI connector bridge when available, and can create a connector itself when the upstream encoder does not request connectorless attachment.

## Important APIs, Types, And Functions

`struct lt8912` owns the DRM bridge and optional connector, two I2C clients/regmaps (`I2C_MAIN` at 0x48 and `I2C_CEC_DSI` at 0x49), the upstream DSI host node/device, reset GPIO, current `videomode`, seven regulators, DSI lane count, and `is_power_on`. Register programming is split across `lt8912_write_init_config()`, `lt8912_write_mipi_basic_config()`, `lt8912_write_dds_config()`, `lt8912_write_rxlogicres_config()`, `lt8912_write_lvds_config()`, and `lt8912_video_setup()`.

Bridge callbacks include attach/detach, mode_set, enable, mode_valid, detect, and edid_read. Connector helpers are `lt8912_connector_detect()` and `lt8912_connector_get_modes()`. PM callbacks are `lt8912_bridge_suspend()` and `lt8912_bridge_resume()`.

## Control Flow

Probe parses reset GPIO, data lanes from input endpoint, DSI host node from port 0, HDMI connector bridge from port 1, regulator names, initializes dummy I2C client 0x49, registers the bridge with EDID and detect ops, and attaches a DSI device with RGB888 video/LPM/no-EOT flags.

Attach first attaches the downstream bridge with `DRM_BRIDGE_ATTACH_NO_CONNECTOR`. If a connector is requested, it initializes a connector, enables downstream HPD if supported, and attaches the encoder. Then it hard-powers the chip, deasserts reset, and runs soft power-on initialization. Mode set stores adjusted timings in `lt->mode`; enable programs video timings, DDS, RX logic reset, and LVDS/HDMI register sequences. Suspend powers off; resume powers on, reapplies soft config, and reruns video setup.

## State And Persistence

`lt->mode` persists the last adjusted mode for enable/resume. `is_power_on` prevents duplicate soft initialization and is cleared only by hard power-off. Regulator and reset state define hardware power state. Dummy I2C client lifetime is explicit and released in remove/error paths. Connector display info is updated from downstream EDID and bus format is forced to RGB888.

## Dependencies And Integration Points

The driver depends on DRM bridge/connector helpers, MIPI DSI registration, OF graph, regmap, GPIO, regulators, videomode conversion, and downstream HDMI connector bridge operations. It expects an `hdmi-connector` compatible node on output port 1 and a DSI host on input port 0.

## Risks And Edge Cases

Many register writes are ORed into a single return value, losing exact failure location. Hardcoded DDS/LVDS sequences may not fit all modes despite timing register updates. `lt8912_bridge_enable()` ignores `lt8912_video_on()` errors. DSI attach happens during probe, so probe ordering depends on DSI host availability. Connector init mixes self-created connector behavior with a downstream bridge and must keep HPD enable/disable balanced. Mode validation caps at 1920x1080 and 150 MHz.

## Test Signals

Exercise DT probe ordering with missing DSI host or connector, dummy I2C client creation/removal, all regulator failures, connectorless and connector-creating attach paths, HPD delegation, EDID mode enumeration, suspend/resume preserving the last mode, 720p/1080p modes, DSI lane counts 1-4, and power-cycle recovery.
