# sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/dss/dpi.c

## Purpose
`dpi.c` implements the OMAP DSS DPI output as a DRM bridge. It chooses the DISPC manager channel and clock source for a DPI port, computes and applies PLL/DSS/DISPC clock divisors for a requested display mode, configures LCD manager parameters, sequences regulator/PLL/DISPC enablement, and registers an `omap_dss_device` output connected to the next bridge in the device-tree graph.

## Important APIs, Types, And Data
- `struct dpi_data` is the private output state: platform device, DSS model, parent `dss_device`, DPI port id, optional OMAP3-family `vdds_dsi` regulator, selected DSS clock source, optional PLL, LCD manager config, current pixel clock, data-line count, `omap_dss_device` output, and embedded `drm_bridge`.
- `struct dpi_clk_calc_ctx` carries clock-search inputs and outputs across nested DSS/PLL/DISPC divisor callbacks: pixel clock min/max, PLL clock info, selected fck, and DISPC divider info.
- DRM bridge operations are `dpi_bridge_attach`, `dpi_bridge_mode_valid`, `dpi_bridge_mode_fixup`, `dpi_bridge_mode_set`, `dpi_bridge_enable`, and `dpi_bridge_disable`.
- Public lifecycle functions are `dpi_init_port()` and `dpi_uninit_port()`, called by DSS core while walking output ports.

## Control Flow
Initialization starts in `dpi_init_port()`. It allocates `struct dpi_data` as a managed DRM bridge object, finds the first endpoint, reads the endpoint `data-lines` property, stores parent/model references, initializes any needed OMAP3-family `vdds_dsi` regulator, and calls `dpi_init_output_port()`. Output-port initialization adds the DRM bridge, reads the port `reg` number as `dpi->id`, names the output (`dpi.0`..`dpi.2`), selects a hardcoded manager channel with `dpi_get_channel()`, initializes/registers the `omap_dss_device`, and links it to the bridge. Cleanup unregisters the output and removes the bridge.

Clock source selection is model-specific. OMAP2/3 use FCK because sharing DSI PLL with DISPC fclk can break other outputs. OMAP4/5 use fixed PLL outputs for certain LCD managers. DRA7 probes available PLL sources per LCD channel and falls back to FCK. `dpi_init_pll()` verifies a candidate PLL by enabling/disabling it once before storing it.

Mode validation and fixup call `dpi_clock_update()`, which attempts either PLL-backed clock calculation or DSS fck/divider calculation and returns the realizable pixel clock. `dpi_pll_clk_calc()` handles PLL type A through nested PLL, HSDIV, and DISPC divider searches; PLL type B uses direct PLL calculation with 1:1 DISPC divisors. `dpi_dss_clk_calc()` widens the accepted pixel-clock range over multiple attempts because FCK-only clocking has few exact combinations.

Bridge enable sequences hardware in dependency order: enable `vdds_dsi` if present, runtime-get DISPC, select the DPI source for this port/channel, enable the PLL if present, set the mode clocks, configure LCD manager state (`DSS_IO_PAD_MODE_BYPASS`, no stall/FIFO handcheck, data-line width, lcden polarity), delay 2 ms, enable the manager, and finally call `omapdss_device_enable()` for downstream output state. Error labels unwind PLL, DISPC runtime PM, and regulator. Disable reverses output/manager, switches LCD clock source back to FCK when a PLL was used, disables PLL, releases DISPC runtime PM, and disables the regulator.

## State And Persistence Behavior
The file persists no on-disk state. Runtime state lives in `dpi_data` and in DSS/DISPC hardware: selected pixel clock, manager divisor config, selected clock source, PLL configuration, regulator enable count, and the bridge/output registration. `port->data` stores the `dpi_data` pointer for uninitialization. Mode setting stores `adjusted_mode->clock * 1000` in `dpi->pixelclock`; actual hardware programming is deferred to bridge enable.

## Dependencies And Integration Points
`dpi.c` depends on Linux clk/regulator/platform/of_graph/SoC helpers, DRM bridge APIs, and local DSS/DISPC/PLL helpers. It integrates tightly with `dispc.c` through `dispc_runtime_get/put` and `dispc_div_calc`, with DSS core through `dss_select_lcd_clk_source`, `dss_dpi_select_source`, `dss_set_fck_rate`, `dss_div_calc`, `dss_mgr_set_lcd_config`, `dss_mgr_enable/disable`, and with PLL providers through `dss_pll_*`. Device tree supplies the DPI port number and endpoint `data-lines`; downstream bridge attachment requires `DRM_BRIDGE_ATTACH_NO_CONNECTOR`.

## Risks And Edge Cases
- The manager-channel mapping is hardcoded by DSS model and DPI id. New boards or SoCs with different routing need code changes.
- DPI bridge attach rejects callers that expect it to create a connector; the DRM pipeline must attach with `DRM_BRIDGE_ATTACH_NO_CONNECTOR`.
- Mode validation rejects widths not divisible by 8 and zero clocks. FCK-only clocking may accept an adjusted clock significantly widened from the requested target because the search range expands up to roughly 15 MHz.
- High pixel clocks skip odd LCD/pixel dividers to avoid duty-cycle problems after level shifting, which can reduce available modes.
- Enable failure paths must keep regulator, PLL, and runtime PM balanced; regression here can leave clocks/regulators on or DISPC references leaked.
- `dpi_init_port()` returns success when no endpoint exists, leaving no output initialized for that port; callers must treat this as an absent graph connection rather than a fatal error.

## Test Signals
Validation should include mode-valid/fixup tests for zero clock, non-8-aligned widths, PLL and FCK clock paths, high-clock odd-divider filtering, DRA7 source fallback, and adjusted clock results. Integration tests should cover bridge attach flags, enable/disable reference balancing with and without PLL/regulator, regulator probe deferral, missing endpoint behavior, data-lines parsing, port `reg` to output name/id/channel mapping, and full DRM modeset smoke tests on OMAP2/3/4/5/DRA7 hardware or emulation.
