# sources/distributed-fs/ceph-client/drivers/phy/phy-core-mipi-dphy.c

This file provides common MIPI D-PHY timing calculation and validation helpers for generic PHY consumers/providers. The important exported APIs are `phy_mipi_dphy_get_default_config()`, `phy_mipi_dphy_get_default_config_for_hsclk()`, and `phy_mipi_dphy_config_validate()`.

Control flow starts in `phy_mipi_dphy_calc_config()`, which derives high-speed clock rate from `pixel_clock * bpp / lanes` unless an explicit HS clock is supplied. It computes unit interval in picoseconds and fills `struct phy_configure_opts_mipi_dphy` with spec-derived minimum timings. The validation helper recomputes UI from `cfg->hs_clk_rate` and checks every timing field against MIPI D-PHY v1.2 limits, returning `-EINVAL` on the first violation.

State is caller-owned through the configuration struct; no persistent driver state exists. Dependencies are `linux/phy/phy-mipi-dphy.h`, `do_div()`, time constants, and exported symbol linkage. Integration is with display/camera PHY drivers that call these helpers before `phy_configure()`. Risks include division by zero if callers pass zero lanes or a config with zero `hs_clk_rate` to validation, narrow support for defaults based only on UI and lane count, and spec drift if newer D-PHY versions adjust limits. Test signals are indirect through users; this file has no local KUnit tests.
