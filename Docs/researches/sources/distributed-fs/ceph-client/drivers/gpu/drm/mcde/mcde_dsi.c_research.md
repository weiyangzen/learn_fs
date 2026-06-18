## sources/distributed-fs/ceph-client/drivers/gpu/drm/mcde/mcde_dsi.c

### Purpose

`mcde_dsi.c` implements the MCDE MIPI DSI host and bridge component. It handles MIPI host attach/detach/transfer, DSI IRQ decoding, TE requests, DSI PHY/link startup, video-mode timing programming, bridge attachment, panel bridge discovery, PRCMU reset, and component binding to the main MCDE device.

### Important APIs, types, and functions

`struct mcde_dsi` stores device, MCDE pointer, bridge, panel, MIPI host/device, current mode, LP/HS clocks and rates, MMIO, and PRCMU regmap. Exported functions used by the display core are `mcde_dsi_irq()`, `mcde_dsi_te_request()`, `mcde_dsi_enable()`, and `mcde_dsi_disable()`. Host ops are attach, detach, and transfer. Bridge ops are attach and mode_set.

### Control flow

Probe maps DSI registers, finds the PRCMU syscon, logs hardware ID, registers a MIPI DSI host, and adds a component. Bind obtains LP/HS clocks, discovers a child panel or bridge, wraps panels with a DSI panel bridge, adds the MCDE DSI bridge, and installs it as `mcde->bridge`. Host attach validates one or two data lanes and selects MCDE flow mode: video formatter for video panels or command TE for command panels. Display enable sets LP/HS rates, enables clocks, toggles PRCMU reset, starts the DSI link, optionally programs video timing, and enables video or command mode. Transfers program direct-command settings and data registers, retry up to three times, and support writes up to 16 bytes and reads up to four bytes.

### State and persistence behavior

State persists in `struct mcde_dsi`, attached `mipi_dsi_device`, current display mode, selected clock rates, PRCMU reset state, and DSI controller registers. IRQ status is latched in DSI status registers and cleared explicitly. The bridge is owned by DRM bridge registration and points to the downstream panel bridge.

### Dependencies

It depends on DRM bridge/panel/MIPI DSI helpers, component framework, common-clock APIs, syscon/regmap PRCMU reset, OF child discovery, MIPI packet constants, and DSI register definitions.

### Integration points

The DSI component binds under the MCDE master and supplies the output bridge consumed by `mcde_modeset_init()`. `mcde_display.c` calls enable/disable from its pipe sequencing and routes DSI IRQ/TE handling through `mcde_dsi_irq()` and `mcde_dsi_te_request()`.

### Risks

The code supports only one active DSI link and hardcodes reset bit DSI0 despite a FIXME. Direct-command reads beyond four bytes and writes beyond 16 bytes are unsupported. Many DSI video timing formulas are copied from vendor behavior with documented uncertainty. Clock enable error handling logs but does not always abort. Non-panel bridges are detected but rejected.

### Test signals

Test DSI host attach, panel probe, command writes/reads, TE IRQs, video-mode panels, command-mode panels, LP/HS clock programming, reset sequencing, lane-ready/PLL-lock polling, display disable waits, and error IRQ logging for missing sync/data.
