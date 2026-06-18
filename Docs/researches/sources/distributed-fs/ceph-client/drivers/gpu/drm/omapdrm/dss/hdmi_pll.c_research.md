# sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/dss/hdmi_pll.c

Purpose: Adapts the HDMI PLL hardware to the generic DSS PLL framework for OMAP4 and OMAP5/DRA7 HDMI outputs.

Important APIs/functions: `hdmi_pll_init()` maps the `pll` resource, stores the platform device and wrapper pointer, obtains `sys_clk`, fills `struct dss_pll`, selects OMAP4 or OMAP5 type-B PLL limits, and registers it with DSS. `hdmi_pll_enable()` runtime-resumes the HDMI device, enables DSS PLL routing, and commands wrapper PLL power `BOTHON_ALLCLKS`. `hdmi_pll_disable()` powers the PLL off, disables routing, and releases runtime PM. `hdmi_pll_uninit()` unregisters the PLL. `hdmi_pll_dump()` prints PLL control/status/config registers.

Control flow: HDMI bridge enable computes `dss_pll_clock_info`, calls `dss_pll_enable()`, then `dss_pll_set_config()`, whose ops route to `dss_pll_write_config_type_b()`. Disable calls `dss_pll_disable()`.

State and persistence: Device-lifetime state in `struct hdmi_pll_data` includes base, platform device, wrapper pointer, and embedded `struct dss_pll`. Active clock config is cached in `pll->cinfo` by the generic PLL layer and cleared on disable.

Dependencies/integration: Depends on runtime PM, `sys_clk`, HDMI wrapper PLL power commands, DSS PLL registration/calculation/programming, and debugfs dumping from HDMI top-level code.

Risks and test signals: `hdmi_pll_enable()` warns on negative runtime PM but does not unwind runtime PM if wrapper power command fails. PLL hardware constraints differ between OMAP4 and OMAP5. Test PLL lock at common CEA clocks, error unwinding for wrapper timeout, runtime PM balance, and debugfs reads while powered.
