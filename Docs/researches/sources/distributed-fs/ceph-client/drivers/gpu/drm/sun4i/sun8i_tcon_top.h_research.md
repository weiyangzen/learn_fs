# sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun8i_tcon_top.h

## Purpose

`sun8i_tcon_top.h` defines the TCON TOP register layout, bit masks, runtime state, OF match export, and public routing helpers for Allwinner TCON TOP support.

## Important APIs, Types, and Definitions

- Register offsets: `TCON_TOP_TCON_TV_SETUP_REG`, `TCON_TOP_PORT_SEL_REG`, and `TCON_TOP_GATE_SRC_REG`.
- Field masks and bits: DE0/DE1 port masks, HDMI source mask, and TCON-TV0/TCON-TV1/DSI gate bit positions.
- `CLK_NUM`: fixed onecell clock count of three possible clock outputs.
- `struct sun8i_tcon_top`: stores bus clock, onecell clock data, MMIO base, reset control, and `reg_lock`.
- `sun8i_tcon_top_of_table`: shared OF match table.
- `sun8i_tcon_top_set_hdmi_src()` and `sun8i_tcon_top_de_config()`: exported cross-module control functions.

## Control Flow and State

The header is consumed by the TCON TOP driver and other sun4i display components. It establishes that all register access goes through a `struct sun8i_tcon_top` instance and that shared register updates are protected by `reg_lock`. It does not own resources directly but defines the persistent state allocated by the C file.

## Dependencies and Integration Points

It requires Linux clock-provider, reset, and spinlock declarations, and it expects bit macros such as `GENMASK()` and `BIT()` to be available through included kernel headers. It integrates with TCON TOP DT compatibles, clock-provider registration, and HDMI/display-engine routing callers.

## Risks and Edge Cases

- Register offsets and bit positions are hardware ABI. Any incorrect value breaks routing or clock gating silently.
- `CLK_NUM` must remain synchronized with DT binding indices and the C file's clock registration.
- The public helpers expose `struct device *` rather than a private type, so callers can pass non-TCON devices and rely on runtime validation.

## Test Signals

Compile tests should catch signature drift with callers. Hardware tests should validate each bit mask against observed register changes. Binding tests should ensure clock indices and output names stay synchronized with this header.
