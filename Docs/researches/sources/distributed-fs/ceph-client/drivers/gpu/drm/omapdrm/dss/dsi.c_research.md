<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/dss/dsi.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/dss/dsi.c

## Purpose
`dsi.c` is the OMAP DRM Display Subsystem MIPI DSI host and bridge implementation. It owns the DSI protocol engine, PHY, DSI PLL, virtual channels, command/video mode setup, external TE handling, MIPI DSI host callbacks, DRM bridge callbacks, component binding, and runtime PM integration for OMAP3, OMAP4, and OMAP5 DSI blocks.

## Important APIs, types, and functions
The file centers on `struct dsi_data` from `dsi.h`, with register access helpers `dsi_read_reg()` and `dsi_write_reg()`. The MIPI host entry points are `omap_dsi_host_attach()`, `omap_dsi_host_detach()`, and `omap_dsi_host_transfer()`. DRM bridge operations are `dsi_bridge_mode_valid()`, `dsi_bridge_mode_set()`, `dsi_bridge_enable()`, and `dsi_bridge_disable()`. Component and platform lifecycle code is handled by `dsi_bind()`, `dsi_unbind()`, `dsi_probe()`, and `dsi_remove()`.

Important internal subsystems include IRQ registration through `dsi_register_isr()` and `dsi_register_isr_vc()`, PLL and clock setup through `dsi_pll_enable()`, `dsi_configure_dsi_clocks()`, `dsi_cm_calc()`, and `dsi_vm_calc()`, PHY/CIO setup through `dsi_cio_init()`, lane setup through `dsi_configure_pins()` and `dsi_set_lane_config()`, packet IO through `dsi_vc_send_short()`, `dsi_vc_send_long()`, `dsi_vc_read_rx_fifo()`, and update handling through `dsi_update_channel()`.

## Control flow
Probe maps the `proto`, `phy`, and `pll` register windows, requests the shared IRQ, gets the DSI regulator and clock, resolves SoC-specific quirks and module ID, parses endpoint lane data, registers the MIPI DSI host, initializes an OMAP DSS output, and joins the DSS component graph. Bind registers the DSI PLL with the DSS PLL framework and installs debugfs views.

On panel attach, the host records command or video mode, pixel format, high-speed and low-power clock limits, transfer mode, and optional TE GPIO state. Mode validation and mode set run `__dsi_calc_config()`, which selects DSI PLL, DISPC divider, LP clock, DISPC videomode, and DSI video timing values. Bridge enable cancels delayed disable work, locks the DSI bus, powers and configures the interface if needed, initializes DISPC output, and enables video output. Bridge disable reverses the output, DISPC, DSI interface, CIO, PLL, and runtime PM state.

Command transfers use virtual channel `VC_CMD`, opportunistically enable the DSI block when it is idle, send packets in LP or HS mode based on `MIPI_DSI_MSG_USE_LPM`, and use BTA synchronization for writes and reads. Video output uses `VC_VIDEO`, configures the video port path, and in command mode performs explicit DISPC updates with framedone and TE timeout handling.

## State and persistence
Persistent in-memory state includes calculated PLL clocks, LP clocks, DISPC dividers, videomode timings, selected MIPI mode and pixel format, lane mapping, virtual channel source and FIFO allocations, TE GPIO and IRQ state, delayed works, error bits, IRQ tables, and debugfs entries. Hardware state persists in DSI protocol, PHY, PLL, and DSS clock mux registers until disabled, reset, or runtime suspended. Runtime suspend gates IRQ handling with `is_enabled` and synchronizes the IRQ before power down; it does not perform a full register context save in this file.

## Dependencies and integration points
The file integrates with the DRM bridge chain, DRM panel/MIPI DSI core, OMAP DSS output helpers, DISPC manager programming, DSS clock-source selection, the common DSS PLL framework, runtime PM, regulators, GPIO descriptors, IRQs, syscon pad muxing on OMAP4/5, device tree graph endpoints, and optional debugfs/IRQ statistics.

## Risks
The highest risks are timing and state ordering bugs. DSI clock calculation is tightly coupled to lane count, pixel format, line buffer size, transfer mode, and panel clock tolerances. Incorrect lane mappings or SoC quirk selection can leave PHY lanes disabled or inverted. Packet paths assume the DSI bus semaphore is held and use short timeouts around hardware FIFO and BTA state; races can deadlock updates or lose errors. Command-mode update completion is fragile: missing TE or framedone events rely on timeout work, and the comments note that canceling hardware transfers is buggy. Runtime PM must preserve IRQ ordering through `is_enabled` and `synchronize_irq()`.

## Test signals
Useful signals include successful probe and component bind on OMAP3/4/5 device trees, MIPI DSI host attach/detach, mode validation for expected panel modes, LP and HS command transfers, DCS reads and writes with BTA completion, TE-on and TE-off command behavior, command-mode full-screen updates with framedone, video-mode continuous output, suspend/resume cycles, debugfs register/clock dumps, absence of DSI IRQ error bits, and panel conformance tests across RGB565, RGB666, and RGB888.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/dss/dsi.c -->
