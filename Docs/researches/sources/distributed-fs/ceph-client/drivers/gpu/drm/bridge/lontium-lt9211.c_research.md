# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/lontium-lt9211.c

## Purpose

This file implements the Lontium LT9211 bridge for a supported subset of the chip: MIPI DSI input to LVDS output. It handles DSI host attachment, LVDS panel/bridge discovery, dual-link LVDS pixel ordering, register initialization, RX autodetection, timing programming, PLL setup, and LVDS transmitter configuration in atomic enable/disable callbacks.

## Important APIs, Types, And Functions

`struct lt9211` contains the DRM bridge, device, paged regmap, DSI device, panel bridge, reset GPIO, `vccio` regulator, and LVDS dual-link flags. `lt9211_regmap_config` restricts read/write access to known register ranges and uses `REGCACHE_MAPLE`.

Core routines are `lt9211_read_chipid()`, `lt9211_system_init()`, `lt9211_configure_rx()`, `lt9211_autodetect_rx()`, `lt9211_configure_timing()`, `lt9211_configure_plls()`, `lt9211_configure_tx()`, `lt9211_atomic_enable()`, and `lt9211_atomic_disable()`. DT/DSI integration is split between `lt9211_parse_dt()` and `lt9211_host_attach()`.

## Control Flow

Probe holds reset low, parses `vccio`, dual-link LVDS port ordering from ports 2/3, and panel/bridge from port 2. It initializes regmap, adds the bridge, and attaches to a DSI host discovered from port 0. DSI is configured as RGB888 video sync-pulse mode with several no-HSA/HFP/HBP flags.

Atomic enable enables `vccio`, releases reset, inspects the negotiated output LVDS bus format and flags, finds the adjusted CRTC mode through connector state, verifies chip ID, initializes system/RX, autodetects the incoming DSI stream and checks active size, writes output timing, configures PLLs based on pixel clock, and enables LVDS TX with JEIDA/SPWG, 18/24 bpp, DE polarity, and dual-link ordering. Atomic disable asserts reset, disables `vccio`, and marks regcache dirty.

## State And Persistence

Persistent driver state is limited to DSI pointer, regmap, panel bridge, regulator/reset handles, and LVDS link flags. Hardware register configuration is rebuilt on every atomic enable after reset. Regcache is marked dirty on disable because reset/regulator-off invalidates cached hardware state.

## Dependencies And Integration Points

The driver integrates DRM bridge atomic state, MIPI DSI, DRM panel bridge helpers, OF graph LVDS dual-link helpers, media bus formats, GPIO, regulators, and regmap. The output bridge/panel must provide or tolerate LVDS format negotiation; unsupported formats fall back to SPWG24 with a warning.

## Risks And Edge Cases

Atomic enable returns void; failed register operations abort silently after logging and can leave the regulator on if a later step fails. RX autodetection requires live DSI input before proceeding and rejects unsupported pixel formats. Only pixel clocks 25-176 MHz are valid. The supported conversion mode is much narrower than the chip's hardware capabilities. Dual-link detection depends on correct DT graph ordering.

## Test Signals

Test single and dual-link LVDS DTs, odd/even and even/odd pixel ordering, panel and bridge outputs, all supported LVDS bus formats plus fallback, reset/regulator sequencing, chip ID failure, DSI stream autodetect mismatch, clock boundaries at 25/176 MHz, enable/disable cycles, and regcache behavior after disable.
