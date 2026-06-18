# sources/distributed-fs/ceph-client/drivers/clk/tegra/Kconfig

Defines build-time configuration symbols for selected Tegra clock features: BPMP-managed clocks, DFLL support, and Tegra124 EMC clock support.

`CLK_TEGRA_BPMP` defaults to yes when `TEGRA_BPMP` is enabled. `TEGRA_CLK_DFLL` defaults to yes for Tegra114/124/210 SoCs and selects `PM_OPP`, reflecting DFLL's dependence on OPP voltage/frequency tables. `TEGRA124_CLK_EMC` is a plain bool selected elsewhere.

There is no runtime state; these symbols shape which object files are compiled and which runtime drivers can exist. The file feeds the Tegra clock Makefile and Kbuild dependency graph and ensures DFLL builds with OPP support.

Wrong dependencies either omit required clock drivers or build unsupported code for SoCs. Test signals are kernel config diffs, object inclusion in build logs, and successful link with/without BPMP and DFLL SoC configs.
