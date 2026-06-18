# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/imx/imx8qxp-pixel-combiner.c

### Purpose
`imx8qxp-pixel-combiner.c` implements the i.MX8QM/QXP pixel combiner DRM bridge. In the current driver it primarily operates each channel in bypass mode, converting a 30-bit internal RGB bus into the 36-bit pixel-link bus and programming signal polarity, reset, and basic RGB data-format controls.

### Important APIs, Types, And Functions
`struct imx8qxp_pc` owns the MMIO base, APB clock, runtime PM device, and up to two `struct imx8qxp_pc_channel` bridges. Channel state stores the stream ID and back-pointer. Register helpers `imx8qxp_pc_read()`, `imx8qxp_pc_write()`, `imx8qxp_pc_write_set()`, and `imx8qxp_pc_write_clr()` use the hardware's set/clear windows. Main bridge callbacks are `imx8qxp_pc_bridge_attach()`, `imx8qxp_pc_bridge_mode_set()`, `imx8qxp_pc_bridge_atomic_disable()`, `imx8qxp_pc_bridge_mode_valid()`, and bus-format callbacks. Runtime PM callbacks reset or release the combiner via `PC_SW_RESET_REG`.

### Control Flow
Probe maps registers, gets the `apb` clock, enables runtime PM, and iterates available child channel nodes. For each channel, it validates `reg` as 0 or 1, allocates a bridge, finds the port 1 remote bridge, stores `stream_id`, and registers the bridge. Attach requires `DRM_BRIDGE_ATTACH_NO_CONNECTOR` and attaches the downstream bridge. Mode set gets runtime PM, temporarily enables the APB clock, programs HSYNC and VSYNC as active-low toward the pixel link, data-valid as active-high, enables first-frame VSYNC masking, selects RGB for the channel's pixel data format, sets bypass mode, and disables the APB clock. Atomic disable only drops runtime PM; runtime suspend performs full reset and runtime resume releases full reset.

### State, Persistence, And Dependencies
Driver state is devm-managed and per-channel. Hardware state is in the combiner MMIO registers and is lost or explicitly reset across runtime suspend. `mode_set()` takes a runtime PM reference that is later released by `atomic_disable()`, so bridge lifecycle and runtime PM are coupled. Dependencies include DRM bridge helpers, OF graph remote bridge lookup, media-bus format constants, APB clock control, runtime PM, and direct MMIO access.

### Integration Points
This bridge sits between the upstream display stream and downstream pixel-link bridge or other i.MX display bridge. It participates in DRM bus-format negotiation by accepting RGB888/RGB666 30-bit input formats and advertising 36-bit CPADLO output formats. It supports two independent channel nodes in devicetree, each with its own downstream bridge.

### Risks
The implementation only supports bypass and RGB, despite register definitions for combine and YUV modes. Runtime PM errors in mode_set are logged but do not stop register programming. Probe error cleanup removes channel 0 only for a narrow `i == 1` case and does not put a downstream bridge reference when later errors occur for the same channel. A failed APB clock enable is logged but writes still proceed. The maximum hdisplay check is a simple 2560 limit and does not validate total bandwidth or multi-stream combine modes.

### Test Signals
Test channel 0 and channel 1 DT probes, downstream bridge deferral, attach without `DRM_BRIDGE_ATTACH_NO_CONNECTOR`, bus-format propagation for RGB888 and RGB666, hdisplay greater than 2560 rejection, runtime suspend/resume reset bits, repeated enable/disable PM balance, and register traces showing bypass, polarity, and first-frame mask programming.
