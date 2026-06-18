<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/kmb/kmb_dsi.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/kmb/kmb_dsi.c

## Purpose
Programs the Keem Bay MIPI DSI transmitter and D-PHY, creates a minimal MIPI DSI host for the external ADV7535 bridge path, attaches the bridge to the DRM encoder, and connects the LCD controller output to MIPI.

## Important APIs, types, and functions
Public entry points are `kmb_dsi_host_bridge_init()`, `kmb_dsi_init()`, `kmb_dsi_encoder_init()`, `kmb_dsi_map_mmio()`, `kmb_dsi_clk_init()`, `kmb_dsi_mode_set()`, and `kmb_dsi_host_unregister()`. Major internal groups are datatype/word-count helpers, frame-generator programming (`mipi_tx_fg_section_cfg()`, `mipi_tx_fg_cfg()`), controller programming (`mipi_tx_init_cntrl()`), D-PHY test-mode writes (`test_mode_send()`), PLL selection (`mipi_tx_pll_setup()`), slew-rate setup, D-PHY init/wait helpers, and `connect_lcd_to_mipi()`.

## Control flow
The early host bridge init allocates global `mipi_dsi_host` and `mipi_dsi_device` objects, registers the host, follows DT graph output endpoint 1 to the bridge, and returns `-EPROBE_DEFER` until the bridge driver is ready. A modeset copies the DRM adjusted mode into global frame config, computes lane data rate from total pixels, refresh, bpp, and active lanes, drops to two lanes for low rates, initializes frame section/header/timing/FIFO/controller registers, initializes the D-PHY or paired D-PHYs, enables the bridge chain, and sets MSSCAM routing from LCD to MIPI. Encoder init creates a simple DSI encoder, attaches the bridge without an internal connector, creates a bridge connector, and attaches it.

## State and persistence
File-scope globals store the DSI host, DSI device, bridge, default frame section, frame timing, DSI config, and controller config. `struct kmb_dsi` stores MMIO, clocks, device pointers, encoder base, and system clock MHz. Hardware state includes MIPI HS controller registers, frame generator registers, FIFO allocation, D-PHY PLL/test configuration, lane enables, and syscon routing.

## Dependencies and integration points
Depends on OF graph, DRM bridge and bridge-connector helpers, DRM MIPI DSI host infrastructure, platform resources named `mipi`, clocks `clk_mipi`, `clk_mipi_ecfg`, `clk_mipi_cfg`, `intel,keembay-msscam` syscon, and register macros from `kmb_regs.h`. It is called from KMB probe, mode config, and CRTC mode-set paths.

## Risks
The host transfer/attach/detach callbacks are stubs, so this only supports bridges configured out-of-band, as documented for ADV7535. Many configuration objects are global, so multi-instance support is unsafe. Several D-PHY wait loops only log timeout but return success. PLL best-value search does not explicitly fail if no good `m/n` pair is found. Hardcoded controller number `MIPI_CTRL6`, default four-lane assumptions, and low-rate two-lane fallback are hardware-board specific.

## Test signals
Validate probe deferral until the bridge appears, encoder/connector creation, 1080p timing programming, two-lane fallback for low pixel rates, D-PHY PLL lock and FSM logs, bridge-chain enable, syscon routing, and MIPI clock-rate programming. Oscilloscope or bridge link status is the strongest hardware signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/kmb/kmb_dsi.c -->
