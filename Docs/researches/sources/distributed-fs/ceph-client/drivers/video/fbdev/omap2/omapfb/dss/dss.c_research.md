# sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/dss/dss.c

## Purpose

This file implements the core OMAP DSS hardware driver. It maps the DSS register block, owns global DSS clocks and clock-source mux state, saves/restores DSS context across runtime PM, initializes DT display ports, manages video PLL discovery, exposes SDI/VENC/HDMI/DPI clock/source helpers, and acts as the component master for DSS child IP blocks. The complete 1,296-line source was read.

## Important APIs, Types, and Functions

Global state lives in the static `dss` struct: platform device, MMIO base, optional syscon PLL control regmap/offset, parent and fck clocks, cached clock calculation data, DSI/DISPC/LCD clock-source selections, saved register context, SoC feature table, and optional video PLLs. Local `struct dss_features` describes SoC fck dividers, parent clock, exposed ports, and DPI source selection callback.

Important public functions include `omapdss_is_initialized()`, `dss_runtime_get()`, `dss_runtime_put()`, `dss_ctrl_pll_enable()`, `dss_ctrl_pll_set_control_mux()`, `dss_sdi_init()/enable()/disable()`, `dss_select_dsi_clk_source()`, `dss_select_lcd_clk_source()`, `dss_dpi_select_source()`, `dss_div_calc()`, `dss_set_fck_rate()`, `dss_select_hdmi_venc_clk_source()`, and platform driver init/uninit.

## Control Flow

The platform probe creates a component master match for child devices, skipping RFBI. Master bind selects SoC DSS features from `omapdss_get_version()`, maps registers, obtains clocks, sets a default fck, probes optional syscon/video PLLs and DT ports, enables runtime PM, resumes the block, initializes DSS control clock sources and VENC-related bits, prints hardware revision, drops runtime PM, binds all child components, adds a debugfs register dump, disables VT switching, and marks DSS initialized.

Runtime suspend saves `DSS_CONTROL` plus SDI registers when relevant, drops bus throughput, and selects sleep pinctrl state. Runtime resume restores pinctrl, requests high bus throughput, and restores saved context. Unbind reverses child binding, PLLs, DT ports, PM, and clocks.

Clock helpers select between DSS fck and DSI/DSI2 PLL hsdivs for DISPC/LCD/DSI consumers, using feature-specific register fields and SoC-specific LCD source availability. `dss_div_calc()` walks possible DSS fck dividers using the SoC parent clock and fck multiplier or delegates to `clk_round_rate()` on AM43xx-style direct clocks.

## State and Persistence Behavior

State is global and volatile. The driver caches clock rates and mux selections in memory and programs corresponding DSS control bits in hardware. Runtime PM context save/restore persists selected DSS registers across clock/power loss during a boot session. DT port initialization stores per-port output data in `port->data` through DPI/SDI helpers. There is no disk persistence.

## Dependencies and Integration Points

The file depends on Linux platform, clock, runtime PM, pinctrl, regmap/syscon, regulator, OF graph, suspend, and component APIs. It integrates with `dss_features.c` for limits and feature bits, DISPC for runtime and manager programming, DPI/SDI port drivers for DT output registration, video PLL code for DRA7/OMAP5-style PLLs, HDMI/VENC/DSI code through shared mux helpers, and debugfs through `dss_debugfs_create_file()`.

## Risks and Edge Cases

The core uses one global `dss` object, so multiple DSS instances are not supported. Port initialization loops can skip unsupported/out-of-range DT ports; partial failures call `dss_uninit_ports()`. Some invalid source selections use `BUG()` or `BUG_ON()`, so callers must validate channel/source combinations. Clock-rate setting warns if the clock framework returns a nearby rate rather than the requested rate. The SDI enable path has multiple 500 ms polling timeouts. Video PLL cleanup must handle partially initialized PLL1/PLL2. Runtime context is restored only after `ctx_valid` has been set by suspend.

## Test Signals

Test signals include probe/bind/unbind on all compatible SoC versions, DT ports for DPI/SDI including DRA7 multi-DPI ports, video PLL resources and `syscon-pll-ctrl`, runtime suspend/resume register preservation, fck rate and divider calculations, HDMI/VENC clock-source selection on SoCs with one or both outputs, SDI PLL lock/reset timeouts, child component bind failures, and debugfs DSS register/clock dumps.
