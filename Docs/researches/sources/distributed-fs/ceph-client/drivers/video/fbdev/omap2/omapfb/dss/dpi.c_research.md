# sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/dss/dpi.c

## Purpose

This file implements the OMAP DSS DPI output driver. It registers a DPI `omap_dss_device`, parses DT display ports when present, connects the output to a downstream panel/encoder, calculates pixel clocks from either the DSS functional clock or a DSI/video PLL, programs the LCD manager, and enables/disables the display path. The complete 887-line source was read.

## Important APIs, Types, and Functions

Private state is `struct dpi_data`, containing the platform device, optional `vdds_dsi` regulator, optional `struct dss_pll`, mutex, cached timings, LCD manager config, data-line width, output device, and DT port initialization flag. The external surface is `dpi_init_platform_driver()`, `dpi_uninit_platform_driver()`, `dpi_init_port()`, and `dpi_uninit_port()`, plus the `omapdss_dpi_ops` callbacks: `connect`, `disconnect`, `enable`, `disable`, `check_timings`, `set_timings`, `get_timings`, and `set_data_lines`.

Key helpers are `dpi_get_pll()`, `dpi_get_alt_clk_src()`, `dpi_dsi_clk_calc()`, `dpi_dss_clk_calc()`, `dpi_set_dsi_clk()`, `dpi_set_dispc_clk()`, `dpi_set_mode()`, `dpi_config_lcd_manager()`, `dpi_init_regulator()`, `dpi_init_pll()`, and `dpi_get_channel()`.

## Control Flow

Non-DT probing registers a component; bind allocates `dpi_data`, initializes its lock, and registers `dpi.0`. DT DSS port initialization allocates one `dpi_data` per port, reads endpoint `data-lines`, derives the port name and DISPC channel from SoC generation and `reg`, and registers the output.

Connect initializes the regulator and optional PLL, obtains the hardcoded overlay manager for the output channel, connects the manager, then links the downstream device. Enable is serialized by `dpi->lock`: it verifies regulator/manager availability, enables `vdds_dsi` on older SoCs that require it, gets DISPC runtime PM, selects the DPI source in DSS, enables the PLL if used, computes and programs clocks/timings, sets LCD manager config, delays 2 ms, and enables the manager. Disable reverses manager enable, clock source, PLL, DISPC PM, and regulator state.

Clock selection first tries an exact DSI/video PLL path when available; otherwise it widens the acceptable pixel-clock range across repeated DSS fclk/divider searches. High pixel clocks reject odd dividers to avoid uneven duty cycles through level shifters.

## State and Persistence Behavior

All state is in memory and hardware registers. Cached state includes requested/current timings, data-line width, manager clock config, optional PLL pointer, and regulator pointer. Enable mutates DSS clock-source registers, DISPC manager timing/config registers, PLL configuration, runtime PM references, and regulator state. There is no file-backed persistence.

## Dependencies and Integration Points

The driver depends on the OMAP DSS output/manager API, DISPC runtime and divider helpers, DSS PLL registration, DSS feature flags, Linux regulators, OF graph parsing, and the component framework. It integrates with `dss.c` for port initialization and source muxing, `dss_features.c` for SoC limits/features, `pll.c`/`video-pll.c`/DSI PLL providers for clock generation, and downstream panel drivers through `omapdss_output_set_device()`.

## Risks and Edge Cases

Pixel-clock calculation may silently adjust `timings->pixelclock` when exact rates are unavailable. Several channel choices are hardcoded by SoC generation, so unusual board routing depends on DT port numbering matching driver assumptions. DT `dpi_init_port()` returns success without initializing anything if a port has no endpoint, so `dpi_uninit_port()` relies on `port_initialized` only after `port->data` exists. PLL verification temporarily enables the PLL and can cause probe failure or fallback to DSS fclk if a DSI/video PLL is not operational. Error paths must preserve regulator, DISPC runtime PM, PLL, and manager balance.

## Test Signals

Useful validation includes boot/probe on OMAP3, OMAP4, OMAP5, AM43xx, and DRA7 variants; DT ports with `reg` 0/1/2 and valid `data-lines`; connect/disconnect to panels; enable/disable loops under runtime PM; pixel-clock checks around 100 MHz and rates requiring widened DSS fclk tolerance; regulator deferral/failure injection; PLL unavailable/failing cases; and visible output timing validation with DISPC manager register dumps.
