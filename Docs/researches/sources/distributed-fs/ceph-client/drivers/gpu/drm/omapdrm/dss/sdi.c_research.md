# sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/dss/sdi.c

Purpose: Implements the OMAP SDI output as a DRM bridge and OMAP DSS output, including clock divisor search, LCD manager configuration, regulator/runtime sequencing, and DT parsing.

Important APIs/functions: `sdi_init_port()` allocates `struct sdi_device`, reads endpoint `datapairs`, gets `vdds_sdi`, initializes the local bridge/output, and stores the object in `port->data`. `sdi_calc_clock_div()` repeatedly widens the accepted pixel-clock range and uses `dss_div_calc()` plus `dispc_div_calc()` callbacks to find a DSS fclk and DISPC divisors. Bridge callbacks validate/fixup/set modes, attach to the next bridge, enable/disable SDI, and store adjusted pixel clock.

Control flow: Mode validation and fixup search for achievable clocks; fixup adjusts `adjusted_mode->clock` to the exact computed pclk. Enable turns on the regulator, runtime-resumes DISPC, recomputes clocks, sets DSS fclk, configures LCD manager, writes DISPC clock divisors early for pck-free use, initializes/enables SDI in DSS, delays, and enables the manager. Disable reverses manager, SDI, runtime PM, and regulator.

State and persistence: `struct sdi_device` stores DSS pointer, pixelclock, datapairs, regulator, manager config, output, and bridge. No disk persistence exists.

Dependencies/integration: Depends on DRM bridge callbacks, OF graph endpoint data, DSS SDI control functions, DISPC clock/divider APIs, OMAP DSS output/manager helpers, and regulator framework.

Risks and test signals: Clock search may accept up to about +/-1 MHz drift after retries; no exact clock guarantee. Enable failures must unwind regulator and DISPC runtime PM. Early direct divider programming bypasses normal shadow timing semantics by necessity. Test supported panels, adjusted clock reporting, regulator failure, SDI enable timeout, suspend/resume, and invalid/missing `datapairs`.
