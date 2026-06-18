# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/lvds-codec.c

## Purpose

`lvds-codec.c` is a generic DRM bridge driver for simple LVDS encoders and decoders that need power control and panel bridging but no register programming. It covers `lvds-decoder`, `lvds-encoder`, and `thine,thc63lvdm83d` compatibles.

## Important APIs, Types, And Functions

`struct lvds_codec` stores the device, DRM bridge, downstream panel bridge, bridge timings, `power` regulator, optional `powerdown` GPIO, connector type, and input bus format. Bridge ops are attach, enable, disable, atomic state helpers, and `atomic_get_input_bus_fmts()`.

Probe allocates the bridge, derives connector type from match data, gets the regulator/GPIO, finds the panel from output port 1, wraps it with `devm_drm_panel_bridge_add_typed()`, parses decoder data mapping for non-LVDS connector type, parses optional `pclk-sample` for LVDS encoders, attaches bridge timings, and registers the bridge.

## Control Flow

Attach simply attaches the wrapped panel bridge. Enable turns on the regulator and deasserts powerdown. Disable asserts powerdown then disables the regulator. Bus-format negotiation returns the configured LVDS/RGB input format.

## State And Persistence

There is no mutable display mode state. Persistent state is limited to regulator and GPIO power state plus the parsed bus format/timing flags. Hardware behavior is mostly strapped or board-defined.

## Dependencies And Integration Points

The driver depends on platform device probing, OF graph, GPIO, regulators, DRM bridge/panel helpers, LVDS data-mapping helpers, media bus formats, and DRM bus flags. It bridges a source on port 0 to a panel on port 1.

## Risks And Edge Cases

Missing `data-mapping` is only a warning for decoder-style use, leaving `bus_format` at zero if no legacy fallback applies. `pclk-sample` is only parsed for LVDS connector type. Enable failure leaves the bridge off but cannot propagate an error through the void bridge callback. The driver assumes the downstream panel is present at probe time.

## Test Signals

Validate all compatibles, panel probe deferral, missing/invalid `data-mapping`, `pclk-sample` flags, powerdown GPIO polarity, regulator enable/disable failures, and bus-format negotiation with panels requiring specific LVDS mappings.
