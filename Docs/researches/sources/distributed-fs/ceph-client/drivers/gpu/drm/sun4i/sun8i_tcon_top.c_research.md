# sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun8i_tcon_top.c

## Purpose

`sun8i_tcon_top.c` implements the Allwinner TCON TOP component driver used by the sun4i DRM stack. The block routes display-engine mixers to TCON outputs, selects HDMI's TCON source, gates TCON-TV/DSI clocks, handles reset and bus-clock lifetime, and exports helper symbols used by other sun4i display components.

## Important APIs, Types, and Functions

- `struct sun8i_tcon_top_quirks`: per-compatible feature flags for a second TCON-TV gate and DSI gate.
- `sun8i_tcon_top_set_hdmi_src(struct device *dev, int tcon)`: exported helper that selects HDMI source TCON 2 or TCON 3 via `TCON_TOP_GATE_SRC_REG`.
- `sun8i_tcon_top_de_config(struct device *dev, int mixer, int tcon)`: exported helper that routes display engine mixer 0/1 to a selected TCON output using `TCON_TOP_PORT_SEL_REG`.
- `sun8i_tcon_top_register_gate(...)`: creates clock gate hardware from DT parent and output names.
- `sun8i_tcon_top_bind()` / `sun8i_tcon_top_unbind()`: component lifecycle hooks that allocate state, deassert reset, enable bus clock, clear routing registers, register gate clocks, and publish the clock provider.
- `sun8i_tcon_top_of_table`: exported OF match table used by the driver and by `sun4i_drv` to identify TCON TOP nodes.

## Control Flow

Probe only registers a component. During component bind, the driver obtains SoC quirks from OF match data, allocates `struct sun8i_tcon_top` and `clk_hw_onecell_data`, initializes the shared register spinlock, acquires reset and bus clock resources, maps MMIO, deasserts reset, enables the bus clock, and clears the port-selection and gate/source registers. It then registers clock gates for `tcon-tv0`, optional `tcon-tv1`, and optional `dsi`, validates all gate handles, adds an OF clock provider, and stores driver data.

The exported routing helpers first verify that `dev->of_node` matches the TCON TOP table and that caller-provided indices are in range. They then take `reg_lock`, perform read-modify-write updates to shared routing/source registers, and release the lock. Unbind unregisters the clock provider and gates, disables the bus clock, and asserts reset.

## State and Persistence Behavior

Persistent state is device-managed except for registered clocks that are explicitly unregistered on error and unbind. Hardware state persists in TCON TOP MMIO registers until reprogrammed or reset. `reg_lock` serializes access to registers shared between gate clocks and routing helpers. The bind path intentionally clears registers that may have non-zero firmware/reset defaults.

## Dependencies and Integration Points

This file depends on Linux component, platform, reset, clock, OF, OF graph, bitfield, and MMIO helpers. It integrates with the Allwinner DT binding `dt-bindings/clock/sun8i-tcon-top.h`, the common sun4i DRM component graph, and other display blocks that call `sun8i_tcon_top_de_config()` or `sun8i_tcon_top_set_hdmi_src()`. The clock output names and parent names must match DT properties.

## Risks and Edge Cases

- The exported helpers assume `dev_get_drvdata(dev)` is initialized; calling them before bind or after unbind would dereference invalid state.
- `mixer` is only checked for `> 1`; negative values are not rejected but are unlikely through normal unsigned-like caller paths.
- `tcon` validation allows values 0..3 for mixer routing but only 2..3 for HDMI source; mismatched caller assumptions can produce `-EINVAL`.
- Gate registration relies on ordered `clock-output-names`; missing or reordered names fail bind.
- Error unwind unregisters only non-error gate pointers and reasserts reset, but any future non-devm resources need matching unwind additions.

## Test Signals

Build coverage should include all three compatibles. DT integration tests should verify required clock names, output names, reset, and MMIO resources. Runtime tests should exercise mixer-to-TCON routing, HDMI source selection, optional DSI/TCON-TV1 clocks, bind error unwind, and unbind cleanup. Lockdep or stress tests should verify concurrent gate enable/disable and routing updates do not race.
