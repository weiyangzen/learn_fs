# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/imx/imx8qxp-ldb.c

### Purpose
`imx8qxp-ldb.c` implements the DRM bridge for the i.MX8QXP LVDS Display Bridge and pixel mapper. It adapts a display controller pixel-link input into one active LVDS channel, supports SPWG/JEIDA output formats, and coordinates optional dual-link LVDS operation through a companion LDB bridge.

### Important APIs, Types, And Functions
The main state is split between `struct imx8qxp_ldb`, which owns the common `struct ldb`, clocks, active channel index, and optional companion bridge, and `struct imx8qxp_ldb_channel`, which extends `struct ldb_channel` with an LVDS PHY and display-interface ID. Important bridge callbacks are `imx8qxp_ldb_bridge_atomic_check()`, `imx8qxp_ldb_bridge_mode_set()`, `imx8qxp_ldb_bridge_atomic_pre_enable()`, `imx8qxp_ldb_bridge_atomic_enable()`, `imx8qxp_ldb_bridge_atomic_disable()`, bus-format callbacks, and `imx8qxp_ldb_bridge_mode_valid()`. Probe-time helpers include `imx8qxp_ldb_set_di_id()`, `imx8qxp_ldb_parse_dt_companion()`, and `imx8qxp_ldb_check_chno_and_dual_link()`.

### Control Flow
Probe allocates two channel bridge objects, fetches `pixel` and `bypass` clocks, initializes the shared LDB helper, requires exactly one available local channel, obtains that channel's `lvds_phy`, finds the next bridge, derives the DI ID from the upstream endpoint, parses a companion LDB if dual-link is described in devicetree, enables runtime PM, and registers the bridge. Atomic check delegates format/link validation to `ldb_bridge_atomic_check_helper()`, derives an LVDS PHY configuration from adjusted pixel clock and split-link state, validates it, and optionally calls the companion bridge check. Mode set gets runtime PM, initializes and configures the PHY, mirrors bus formats into the companion channel for split mode, sets both LDB clocks to the adjusted pixel clock, writes channel selection and VSYNC polarity into `ldb_ctrl`, lets the generic helper program format bits, updates HSYNC/VSYNC polarity in `SS_CTRL`, and propagates mode set to the companion. Pre-enable enables clocks, enable writes channel mode bits and powers the PHY, and disable powers the PHY off, exits it, disables clocks, propagates disable, and drops runtime PM.

### State, Persistence, And Dependencies
Persistent driver state is in devm-managed bridge/channel objects plus `ldb->ldb_ctrl`, the active channel number, DI ID, PHY pointer, and optional companion reference. Hardware state persists in the syscon-backed LDB control register, `SS_CTRL`, clock rates, and PHY programming until runtime resume or disable resets it. Dependencies include `imx-ldb-helper.h`, DRM bridge atomic helpers, DRM OF LVDS dual-link helpers, Linux PHY LVDS options, regmap, runtime PM, and devicetree graph endpoints.

### Integration Points
The driver integrates into a larger i.MX display pipeline through DRM bridge chaining and media-bus format negotiation. It consumes the upstream DI selected from port 0, drives a downstream panel or bridge found by the LDB helper, and can coordinate a second LDB via `fsl,companion-ldb` for odd/even dual-link LVDS. Runtime PM resume resets the LDB control register to power-on defaults before normal mode programming.

### Risks
Probe intentionally rejects more than one locally available channel, so DTs exposing both channels on one instance will fail. Companion handling calls bridge function pointers directly and assumes the companion bridge is an LDB-compatible object. `pm_runtime_get_sync()` errors are logged but mode programming continues, which can lead to register or PHY operations while power state is uncertain. Split-link correctness depends on channel number matching the odd/even pixel order. Clock and PHY configuration errors are mostly logged after mode_set starts rather than converted into atomic failures.

### Test Signals
Useful signals are DT probe with single-link channel 0 and channel 1, dual-link odd/even and even/odd companion layouts, invalid companion compatible strings, deferred companion bridge probe, mode validation around 150 MHz single-link and 170 MHz split-link limits, SPWG/JEIDA/RGB666 bus-format negotiation, PHY validate/configure failures, runtime suspend/resume register reset, and hot disable/enable cycles that verify clock and PHY balance.
