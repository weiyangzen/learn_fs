# sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/dss/video-pll.c

Purpose: Implements DRA7 video PLL frontends for the generic DSS PLL framework, including clock-control power sequencing and errata-aware type-A PLL registration.

Important APIs/functions: `dss_video_pll_init()` maps per-ID PLL and clock-control resources (`pll1`/`pll2`, `pll1_clkctrl`/`pll2_clkctrl`), gets `video1_clk` or `video2_clk`, allocates `struct dss_video_pll`, fills the embedded `struct dss_pll`, assigns DRA7 type-A hardware limits, stores optional regulator, and registers with DSS. `dss_video_pll_enable()` runtime-resumes DSS, enables DSS PLL routing, enables SCP clock, waits reset done, and powers the PLL. `dss_video_pll_disable()` powers down, disables SCP clock/routing, and runtime-suspends DSS. `dss_video_pll_uninit()` unregisters.

Control flow: Output clock users find the PLL by source/name, calculate type-A settings through `pll.c`, enable it, program config through `dss_pll_write_config_type_a()`, then disable on output teardown.

State and persistence: `struct dss_video_pll` wraps `struct dss_pll` plus device and clkctrl base. Active config is held by the generic `dss_pll` cache and hardware registers only.

Dependencies/integration: Depends on platform resource names, kernel clk/regulator APIs, DSS runtime/control helpers, generic PLL math/programming, and DRA7 errata flags i886/i932.

Risks and test signals: DRA7 PLL power status is not reliable, so enable uses a fixed 1 ms delay. Resource array indexing assumes valid caller IDs. Test both video PLLs, missing resources, regulator use, reset timeout, suspend/resume, and clock rates requiring errata retry behavior.
