# sources/distributed-fs/ceph-client/drivers/gpu/drm/ingenic/ingenic-dw-hdmi.c

## Purpose
Provides the Ingenic JZ4780-specific platform wrapper for the generic Synopsys DesignWare HDMI bridge. It supplies PHY/MPLL/current tables, clock range validation, output-port selection, and devm cleanup.

## Important APIs, types, and functions
- Static platform data includes `ingenic_mpll_cfg`, `ingenic_cur_ctr`, `ingenic_phy_config`, and `ingenic_dw_hdmi_plat_data`.
- `ingenic_dw_hdmi_mode_valid()` restricts modes to 13.5 MHz through 216 MHz pixel clock.
- `ingenic_dw_hdmi_probe()` calls `dw_hdmi_probe()` and registers `ingenic_dw_hdmi_cleanup()` as a devm action.
- OF match supports `ingenic,jz4780-dw-hdmi`.

## Control flow
Probe is intentionally small: the generic DW-HDMI core is probed with Ingenic platform data and, if successful, registered for automatic removal with `devm_add_action_or_reset()`. The generic bridge uses `output_port = 1` to connect into the OF graph. Mode validation rejects very low clocks and clocks above 216 MHz because setup data for higher rates is missing.

## State and persistence
Runtime state is owned by the generic `dw_hdmi` instance returned from probe. This file stores no private struct. PHY configuration tables are static read-only data.

## Dependencies and integration points
Depends on the generic `drm/bridge/dw_hdmi` driver, OF platform matching, and DRM mode status definitions. It integrates with the Ingenic LCD controller driver through device-tree bridge discovery rather than direct symbol calls.

## Risks
The 216 MHz cap is conservative and may reject hardware-capable modes. Cleanup depends entirely on `dw_hdmi_remove()` through the devm action. The wrapper does not add Ingenic-specific mux or clock programming beyond generic DW-HDMI platform data, so board integration relies on device tree and the generic bridge.

## Test signals
Validation includes probing `ingenic,jz4780-dw-hdmi`, EDID and connector creation through the generic bridge, mode validation at 13.5 MHz and 216 MHz boundaries, graph connection via output port 1, and module removal cleanup.
