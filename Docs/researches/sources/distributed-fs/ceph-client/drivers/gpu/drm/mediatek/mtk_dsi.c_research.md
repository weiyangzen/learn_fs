# sources/distributed-fs/ceph-client/drivers/gpu/drm/mediatek/mtk_dsi.c

## Purpose
Implements the MediaTek MIPI DSI controller as both a DRM bridge and a `mipi_dsi_host`. It owns controller register programming, D-PHY timing setup, panel/bridge attachment, command-mode transfers, video-mode start/stop, and component binding into the MediaTek DRM pipeline.

## Important APIs, types, and functions
- `struct mtk_dsi` stores host, bridge, encoder, connector, PHY, clocks, current videomode, format/lanes/mode flags, IRQ wait state, and SoC-specific `mtk_dsi_driver_data`.
- `mtk_dsi_poweron()` and `mtk_dsi_poweroff()` are the main refcounted hardware sequencing paths.
- Bridge callbacks include `mtk_dsi_bridge_attach()`, `mtk_dsi_bridge_mode_set()`, atomic pre-enable/enable/disable/post-disable, and `mtk_dsi_bridge_mode_valid()`.
- Host callbacks are `mtk_dsi_host_attach()`, `mtk_dsi_host_detach()`, and `mtk_dsi_host_transfer()`.
- DDP integration exports `mtk_dsi_ddp_start()`, `mtk_dsi_ddp_stop()`, and `mtk_dsi_encoder_index()`.

## Control flow
Probe allocates the bridge-backed DSI object, resolves engine/digital/HS clocks, MMIO, D-PHY, IRQ, initializes the wait queue, registers the MIPI DSI host, and installs an IRQ handler. Host attach records the attached panel/bridge parameters, resolves the next bridge from the OF graph with an old-DT fallback, adds the DRM bridge, and registers the component. Component bind creates the DRM encoder, attaches the internal bridge, and creates a bridge connector.

During atomic pre-enable, `mtk_dsi_poweron()` calculates HS data rate from pixel clock, bpp, and lanes, sets `hs_clk`, powers the PHY, enables clocks, enables/reset the controller, programs optional shadow-control bypass, computes D-PHY timing, writes pixel stream and video timing registers, enables DSI interrupts, prepares lanes, and enters HS clock mode. Atomic enable sets command/video mode and starts the engine. Disable/post-disable clear the enabled flag and then stop the engine, wait for video-mode completion, reset, enter ULPM, pull down lanes, disable clocks, and power down the PHY.

Command transfers temporarily stop video mode if needed, switch to command mode using VM-done IRQ synchronization, prepare lane state, write CMDQ payload/registers, start the engine, wait for CMD-done and optional LPRX-ready interrupts, read up to 16 bytes from RX registers, clamp to caller buffer length, and restore the previous video mode.

## State and persistence
Runtime state lives in `struct mtk_dsi`: `refcount`, `enabled`, `lanes_ready`, `irq_data`, `data_rate`, cached display mode and DSI bus parameters. Hardware state persists in controller, PHY, CMDQ, timing, interrupt, lane, and mode registers until reset or poweroff. The code uses a wait queue plus IRQ status bits as transient synchronization state for mode switches and command completion.

## Dependencies and integration points
Depends on DRM bridge/bridge-connector helpers, MIPI DSI host APIs, DRM OF graph bridge lookup, MediaTek component/DDP helpers, `mtk_find_possible_crtcs()`, Linux PHY and clock APIs, optional reset control, and SoC match data for register offsets/features. It integrates with downstream panels/bridges through the MIPI host and with the display pipeline through the component framework and DDP start/stop hooks.

## Risks
Timing and lane sequencing are hardware-sensitive. Errors in bpp/lane-derived HS rate, per-frame versus per-line low-power timing, CMDQ packet sizing, or ULPM transitions can produce blank panels or transfer timeouts. `mtk_dsi_recv_cnt()` computes long-read length as `read_data[1] + read_data[2] * 16`, which is notable because MIPI long packet length is normally byte-low plus byte-high shifted by 8. Refcounted power paths also rely on balanced DDP and bridge calls.

## Test signals
Useful signals are DSI IRQ timeout warnings, `failed to switch cmd mode`, mode-valid rejections above 1.5 Gbps/lane, panel command read logs, and visible panel bring-up across command and video modes. Test matrices should cover all matched SoC data variants, 1-4 lane panels, RGB565/666/888, burst/sync-pulse/sync-event modes, non-continuous clock, suspend/resume, and command transfers while streaming.
