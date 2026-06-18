<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/dss/dss.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/dss/dss.c

## Purpose
`dss.c` is the OMAP Display Subsystem hardware core and component master. It manages DSS register access, SoC feature data, functional clocks, LCD/DISPC/DSI/HDMI/VENC clock source muxing, SDI setup, video PLL discovery, debugfs, runtime PM context handling, child component collection, and creation of the `omapdrm` platform device after all DSS children bind.

## Important APIs, types, and functions
External APIs implemented here include `dss_runtime_get()`, `dss_runtime_put()`, `dss_get_device()`, `dss_get_dispc_clk_rate()`, `dss_get_max_fck_rate()`, `dss_select_dsi_clk_source()`, `dss_select_lcd_clk_source()`, `dss_get_*_clk_source()`, `dss_select_hdmi_venc_clk_source()`, `dss_dpi_select_source()`, `dss_div_calc()`, and SDI helpers. Internal types `struct dss_ops` and `struct dss_features` describe SoC-specific routing, clock limits, supported ports, supported outputs, and register field layouts.

## Control flow
Probe allocates `struct dss_device`, maps DSS registers, selects a feature table from SoC match data or device tree compatible data, obtains clocks, programs a default DSS functional clock, probes video PLLs, initializes DPI/SDI ports from graph ports, enables runtime PM, probes hardware revision and default mux state, initializes debugfs, populates child platform devices, gathers OMAP DSS components, and registers as a component master. Master bind first binds all child components, disables VT switching, and registers the top-level `omapdrm` platform device with a `dss_pdata` pointer.

Clock selection paths program `DSS_CONTROL` fields or syscon PLL control bits depending on SoC. OMAP2/3 share DISPC and LCD clock source behavior, while OMAP4/5/DRA7 have per-LCD mux functions. Runtime suspend saves selected DSS registers, lowers bus throughput, and selects sleep pinctrl; runtime resume restores pinctrl, requests high throughput, and restores saved DSS context.

## State and persistence
`struct dss_device` stores mapped registers, syscon PLL control, child DRM device, clocks and cached rates, clock source selections, saved register context, feature table, debugfs entries, video PLL pointers, DISPC pointer, and manager operation state. Hardware register state includes DSS control muxes, SDI control, PLL control, and VENC/HDMI routing. Saved context persists across runtime suspend in `ctx` when `ctx_valid` is set.

## Dependencies and integration points
The file integrates with platform devices, OF graph parsing, component framework, DISPC, DSI, VENC, HDMI4/5, DPI, SDI, OMAP DSS helper APIs, DSS PLL code, regulators, syscon regmap, clocks, pinctrl, runtime PM, debugfs, and system sleep PM. It is the registration point for the DSS driver set through `omap_dss_init()` and `omap_dss_exit()`.

## Risks
SoC feature-table mistakes can route clocks to unsupported outputs or use invalid bit fields. Clock mux functions sometimes return after warnings rather than hard failures, so callers must verify effective state when debugging. Runtime context save only covers core DSS registers, not child components. Component matching recursively walks target modules and skips RFBI by name; device-tree topology changes can alter bind ordering. SDI and clock setup use hardware timeouts and can fail if clocks, pinctrl, or PLL regulators are not ready.

## Test signals
Validation signals include successful platform driver registration, DSS revision logging, child component bind, `omapdrm` platform device creation, debugfs `clk` and `dss` dumps, correct clock-source reports for DPI/DSI/HDMI modes, SDI enable timeout-free operation where supported, suspend/resume without lost DSS mux state, and display smoke tests across each supported SoC feature table.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/dss/dss.c -->
