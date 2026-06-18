<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun6i_mipi_dsi.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun6i_mipi_dsi.c

## Purpose

`sun6i_mipi_dsi.c` implements the Allwinner MIPI DSI host and DRM DSI encoder/connector. It programs the DSI instruction engine, pixel/video timing packets, D-PHY configuration, panel lifecycle, and low-power DCS command transfers.

## Important APIs, Types, And Functions

Important areas include ECC/CRC helpers (`sun6i_dsi_ecc_compute()`, `sun6i_dsi_crc_compute()`), packet builders, instruction setup/start/wait helpers, video timing helpers (`sun6i_dsi_setup_burst()`, `sun6i_dsi_setup_format()`, `sun6i_dsi_setup_timings()`), encoder enable/disable callbacks, connector get/detect callbacks, DCS transfer helpers, MIPI host ops (`attach`, `detach`, `transfer`), component bind/unbind, and platform probe/remove. Variants control presence and exclusivity of the module clock.

## Control Flow

Probe maps registers, gets regulator/reset/clocks/D-PHY, attaches bus clock to regmap, optionally sets exclusive 297 MHz module clock, registers the MIPI host, and adds the DRM component. Attach stores panel/device only after DRM is registered and emits a hotplug event. Component bind creates a DSI encoder and connector. Encoder enable powers regulator/reset/mod clock, enables DSI, initializes instruction slots, computes video start delay, burst/loop/format/timing packets, configures and powers the D-PHY, prepares/enables the panel, then starts high-speed clock and data instructions. Host transfer waits for idle, clears command flags, and handles supported short writes, long writes, and one-byte reads in LP mode.

## State And Persistence Behavior

Persistent state lives in `struct sun6i_dsi`: connector, encoder, host, clocks, regmap, regulator, reset, D-PHY, attached device, panel, DRM pointer, and variant. Hardware state persists in DSI instruction, pixel, timing, command FIFO, and PHY registers until disable/reset. Attached panel/device pointers are updated by MIPI host attach/detach.

## Dependencies And Integration Points

It depends on DRM DSI/panel/simple-encoder helpers, Linux MIPI D-PHY phy APIs, regulator/clock/reset/regmap/component frameworks, and `sun4i_tcon.c`, which treats DSI as TCON channel 0 CPU interface with `SUN6I_DSI_TCON_DIV`.

## Risks And Test Signals

Risks include many magic timing formulas, only partial command-mode support, panel enable before HS mode due to DCS limitations, limited read support, command completion bits noted unreliable, possible DSI_START_HSD jump-table fragility, and mod-clock exclusivity. Test with RGB565/666/888 panels, burst and non-burst video, LP DCS short/long/read commands, D-PHY timing, hotplug attach/defer, enable/disable, and malformed transfer types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun6i_mipi_dsi.c -->
