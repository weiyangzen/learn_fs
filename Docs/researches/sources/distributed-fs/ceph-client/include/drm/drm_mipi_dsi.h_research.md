# sources/distributed-fs/ceph-client/include/drm/drm_mipi_dsi.h

Purpose: declares the MIPI DSI bus, host/device model, packet/message representation, DSI mode flags, DCS/generic command helpers, multi-command error accumulation, dual-DSI helpers, and DSI driver registration macros.

Important APIs and types: `struct mipi_dsi_msg` describes one transfer with channel, data type, flags, TX buffer, and optional RX buffer. `struct mipi_dsi_packet` is the protocol packet form. `struct mipi_dsi_host_ops` supplies attach/detach/transfer callbacks for host controllers, while `struct mipi_dsi_host` registers those ops on the DSI bus. `struct mipi_dsi_device` records host, device, attachment state, virtual channel, lanes, pixel format, mode flags, HS/LP rates, and optional DSC config. The API covers host/device registration, OF lookup, attach/detach, devm attach, peripheral power commands, compression and PPS commands, generic read/write, DCS command helpers, brightness helpers, multi-context variants, dual-interface macros, and `mipi_dsi_driver` registration.

Control flow: host drivers register a `mipi_dsi_host`; panel or bridge drivers create/find a `mipi_dsi_device`, set lanes/format/mode flags/rates, attach to the host, and send initialization commands. Message helpers build short or long DSI packets and call the host `transfer` callback. Multi helpers skip later commands after the first accumulated error, allowing panel init tables to be linear.

State and persistence behavior: DSI host/device state is Linux driver-model state. `attached` tracks successful host binding. Mode flags persist as device configuration and influence host transfer/video setup. `mipi_dsi_multi_context.accum_err` is transient command-sequence state.

Dependencies and integration points: depends on Linux devices, delays, OF graph lookup, DRM DSC structures, display bus formats, panel/bridge drivers, and module driver helpers. It bridges DRM display drivers to physical DSI host controller transfer implementations.

Risks: macros such as `mipi_dsi_dual()` evaluate function arguments twice and warn about side effects. HS/LP rates of zero are only legacy-compatible and should not hide real hardware limits. Host transfer callbacks may be called regardless of power state, so host drivers must power-manage internally. Packet type/length mistakes can corrupt panel command streams.

Test signals: packet creation for short/long formats, generic and DCS reads/writes, multi-context error short-circuiting, dual-DSI command ordering, attach/detach/devm cleanup, DSC compression/PPS sequences, pixel-format-to-bpp mapping, OF host/device lookup, and host transfer behavior in LP/HS modes.
