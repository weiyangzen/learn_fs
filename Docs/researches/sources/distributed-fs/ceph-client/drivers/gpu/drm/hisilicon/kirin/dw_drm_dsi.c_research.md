# sources/distributed-fs/ceph-client/drivers/gpu/drm/hisilicon/kirin/dw_drm_dsi.c

Purpose: implements a DesignWare MIPI DSI host/encoder for HiSilicon Kirin/Hi6220 platforms, including D-PHY PLL/timing calculation, DSI video-mode programming, MIPI DSI host attach/detach, component binding, and bridge attachment.

Important APIs/functions: `dsi_probe()` allocates driver data, maps registers, gets `pclk`, and registers a MIPI DSI host. `dsi_host_attach()` records lanes, format, and mode flags and adds the component. `dsi_bind()` initializes the DRM DSI encoder and attaches the downstream bridge. Encoder helpers validate mode/PHY rate, store adjusted mode, and enable/disable DSI core and PHY. `dsi_calc_phy_rate()` and `dsi_get_phy_params()` compute PLL and timing parameters.

Control flow: platform probe registers the host. When a DSI peripheral attaches, the driver becomes a DRM component. Master bind calls `dsi_bind()`, which creates an encoder and attaches bridge endpoint port 1. Atomic modeset calls mode validation through possible CRTC mode fixup, then mode set stores adjusted mode. Enable prepares the pixel clock and calls `dsi_mipi_init()` to reset core, program PHY, timing, video mode, and power up.

State and persistence: `struct dw_dsi` stores encoder, host, current mode, DSI format/lanes/flags, PHY parameters, and enable flag. Hardware state is DSI/D-PHY registers. No disk persistence.

Dependencies and integration points: depends on Linux component framework, DRM encoder/bridge/OF helpers, MIPI DSI host APIs, platform resources, clocks, and `dw_dsi_reg.h`. It expects a downstream panel/bridge in OF graph.

Risks: only RGB888 color coding is effectively supported. PHY mode validation uses a strict denominator relationship between adjusted pixel clock and lane byte clock. PLL calculation increments requested rate until valid and must stay within supported ranges. DSI host component add/del is tied to peripheral attach/detach, so missing peripheral prevents component bind.

Test signals: OF probe, DSI peripheral attach/detach, bridge discovery, mode validation at supported clocks, scope-visible D-PHY clock/data lanes, panel enable/disable, and suspend/remove paths.
