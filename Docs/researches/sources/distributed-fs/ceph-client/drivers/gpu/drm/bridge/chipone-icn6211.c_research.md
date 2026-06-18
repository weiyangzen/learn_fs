# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/chipone-icn6211.c

# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/chipone-icn6211.c

## Purpose

This driver supports the Chipone ICN6211 MIPI DSI to RGB/DPI bridge. It can be controlled either as a MIPI DSI peripheral using generic DSI reads/writes through regmap, or over I2C while creating and attaching a DSI device to the upstream host.

## Important APIs, Types, And Functions

`struct chipone` tracks regmap, bridge, panel bridge, DSI device, regulators, enable GPIO, optional refclk, and control-interface mode. Core functions are `chipone_parse_dt()`, `chipone_common_probe()`, `chipone_dsi_probe()`, `chipone_i2c_probe()`, `chipone_dsi_host_attach()`, `chipone_dsi_attach()`, `chipone_atomic_pre_enable()`, `chipone_atomic_enable()`, `chipone_atomic_post_disable()`, and `chipone_configure_pll()`.

## Control Flow

Probe parses supplies, refclk, enable GPIO, and output panel bridge. DSI-control probe initializes a custom regmap bus over generic DSI packets, adds the bridge, and attaches the existing DSI device. I2C-control probe initializes I2C regmap, adds the bridge, finds the upstream DSI host from OF graph, registers a DSI child, and attaches it. Pre-enable powers supplies/refclk/GPIO. Mode set caches the adjusted mode. Enable validates chip IDs, selects I2C/DSI config password, writes active/porch/sync timing, DSI lane count, polarity, PLL setup, and final configuration. Post-disable turns power back off.

## State And Persistence Behavior

The cached display mode and refclk rate are stored in memory. Regmap uses MAPLE cache, while the chip is reprogrammed on each atomic enable. No nonvolatile state is written.

## Dependencies And Integration Points

It integrates DRM bridge chaining, DRM OF graph, MIPI DSI, I2C, regmap, regulators, GPIO, optional clock, media bus formats, and downstream panel bridges. It returns RGB888 input bus format to the upstream source.

## Risks And Test Signals

Risks include PLL search edge cases when no best divider is found, fixed DSI rates, optional regulator error handling that logs but continues on enable failures, and different lifetime paths for DSI-control versus I2C-control instances. Test signals are chip ID reads, valid DSI lane parsing, stable pixel clock, RGB panel output, and successful remove without leaking registered DSI devices.
