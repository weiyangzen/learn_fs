## sources/distributed-fs/ceph-client/drivers/gpu/drm/mcde/mcde_drm.h

### Purpose

`mcde_drm.h` is the shared internal MCDE driver header. It defines top-level MCDE control/error registers, display flow modes, the driver-private `struct mcde`, and cross-file function declarations.

### Important APIs, types, and functions

The key type is `struct mcde`, embedding `struct drm_device` plus device, panel/bridge/connector/simple-pipe, DSI device, DPI flag, stride, flow mode/accounting, MMIO base, clocks, FIFO clock handles, locks, and regulators. `enum mcde_flow_mode` models one-shot command, TE command, BTA+TE command, video TE, video formatter, and DPI formatter flows. Declarations connect DSI, display, and clock-divider modules.

### Control flow

The header has only inline flow classification through `mcde_flow_is_video()`. Real control flow is split across `mcde_drv.c`, `mcde_display.c`, `mcde_dsi.c`, and `mcde_clk_div.c`.

### State and persistence behavior

`struct mcde` is the long-lived per-device state allocated by `devm_drm_dev_alloc()`. It persists DRM object ownership, output routing, flow mode, flow-active count, clock/regulator references, and MMIO base through device lifetime.

### Dependencies

It includes DRM simple KMS helper types and relies on MIPI DSI, bridge, panel, clock, regulator, and MMIO types from including C files.

### Integration points

Every MCDE source file includes this header. It establishes the private object conversion via `to_mcde()` and the function contract between the top-level platform driver, the DSI component, the display pipe, and FIFO clock registration.

### Risks

The shared state assumes a single active DSI device and simple display pipe. Flow mode is global, so supporting multiple concurrent outputs would require structural changes. `mcde_flow_is_video()` intentionally treats DPI as not DSI video except through its own flow mode.

### Test signals

Build and runtime integration tests should cover DSI and DPI probe paths, output selection, flow mode selection from attached DSI mode flags, and component teardown.
