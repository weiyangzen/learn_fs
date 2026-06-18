# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/imx/imx8qm-ldb.c

# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/imx/imx8qm-ldb.c

## Purpose

This driver implements the i.MX8QM LVDS Display Bridge, also called pixel mapper, using the shared i.MX LDB helper plus LVDS PHY configuration. It supports single-link and odd-even dual-link LVDS output.

## Important APIs, Types, And Functions

`struct imx8qm_ldb_channel` extends `ldb_channel` with a PHY. `struct imx8qm_ldb` embeds `struct ldb`, channel pointers, pixel/bypass clocks, and active channel. Key paths are `imx8qm_ldb_probe/remove()`, `imx8qm_ldb_bridge_atomic_check()`, `imx8qm_ldb_bridge_mode_set()`, `imx8qm_ldb_bridge_atomic_enable/disable()`, bus-format negotiation helpers, and runtime resume.

## Control Flow

Probe allocates two bridge channels, gets pixel and bypass clocks, initializes the common LDB, validates available channels and dual-link odd-even order, gets per-channel LVDS PHYs, resolves downstream bridges, enables runtime PM, and adds bridges for available channels. Atomic check records bus formats and validates primary and, for split mode, slave PHY LVDS settings. Mode set resumes runtime PM, initializes/configures PHYs, sets clocks to adjusted pixel clock, programs sync polarity and data-width bits, then delegates common LDB control setup. Enable starts clocks, sets channel-to-DI routing, powers PHYs, and writes LDB control. Disable reverses helper control, PHY power, clocks, and runtime PM.

## State And Persistence Behavior

State includes active channel number, link type, cached `ldb_ctrl`, per-channel availability, bus formats, PHY handles, and clocks. Runtime resume resets the LDB control register to POR default. No persistent storage exists.

## Dependencies And Integration Points

It depends on `imx-ldb-helper`, DRM bridge atomic helpers, OF graph dual-link parsing, generic LVDS PHY API, syscon regmap, clocks, runtime PM, and media bus formats.

## Risks And Test Signals

Risks include only accepting odd-even dual-link order, accumulating control bits across mode sets, error paths that log but continue after PM/PHY/clock failures, and split-mode slave PHY configuration tied to `active_chno ^ 1`. Test signals are PHY validate/configure success, single and dual-link LVDS output, correct SPWG/JEIDA negotiation, runtime PM reset behavior, and clock/PHY balance on disable.
