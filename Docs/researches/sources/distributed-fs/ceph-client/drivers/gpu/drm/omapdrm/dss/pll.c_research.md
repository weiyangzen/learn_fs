# sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/dss/pll.c

Purpose: Implements the generic DSS PLL registry, enable/disable/configuration facade, clock divider calculation helpers, and low-level type-A/type-B PLL programming routines.

Important APIs/functions: `dss_pll_register()`, `dss_pll_unregister()`, `dss_pll_find()`, and `dss_pll_find_by_src()` manage PLLs in `dss->plls`. `dss_pll_enable()`, `dss_pll_disable()`, and `dss_pll_set_config()` wrap input clocks, regulators, hardware ops, and cached clock info. `dss_pll_calc_a()` and `dss_pll_hsdiv_calc_a()` search integer PLL/HSDIV parameters for type-A hardware. `dss_pll_calc_b()` calculates type-B fractional PLL settings for a target clkout. `dss_pll_write_config_type_a()` and `_type_b()` program registers, wait for GO/lock, handle errata i886/i932, and enable HSDIV outputs.

Control flow: HDMI and video PLL frontends register `struct dss_pll` instances with hardware limits and ops. Output enable computes clock info, enables the PLL, writes config, and later disables/clears cached info.

State and persistence: `struct dss_pll` stores hardware descriptors, base, clkin/regulator, ops, cached `cinfo`, and DSS owner. All state is runtime memory and hardware registers.

Dependencies/integration: Uses kernel clk/regulator APIs, DSS logging/control routing, SoC-specific PLL descriptors, and callers in HDMI/video/DPI/SDI paths.

Risks and test signals: Search loops must obey hardware min/max and errata direction constraints. Type-B calculation uses WARN_ON for unexpected fractional delta but still proceeds. Lock/GO timeouts fail modeset. Test PLL calculations near min/max clocks, OMAP3/4/5/DRA7 variants, regulator failure unwind, HSDIV ack bits, and errata retry paths.
