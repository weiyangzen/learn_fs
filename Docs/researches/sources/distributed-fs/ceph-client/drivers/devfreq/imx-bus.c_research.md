<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/devfreq/imx-bus.c -->
# sources/distributed-fs/ceph-client/drivers/devfreq/imx-bus.c

Purpose: generic i.MX bus frequency scaling driver. It exposes a bus clock as a devfreq device, typically controlled from userspace, and can spawn a matching i.MX interconnect provider.

Important APIs and control flow: `imx_bus_probe()` allocates state, obtains the bus clock, loads the OPP table, fills a devfreq profile with `target`, `get_cur_freq`, `exit`, and initial clock rate, registers a userspace-governed devfreq device, and optionally calls `imx_bus_init_icc()`. `imx_bus_target()` chooses a recommended OPP and applies it with `dev_pm_opp_set_rate()`. `imx_bus_get_cur_freq()` reports `clk_get_rate()`. Exit removes the OPP table and unregisters the optional interconnect child.

State and persistence behavior: state is a profile, devfreq pointer, clock, and optional interconnect platform device. OPP state is loaded from DT and removed in profile exit or probe error.

Dependencies and integration points: depends on clk, OPP, devfreq userspace governor, OF compatibles for i.MX8M NoC/NIC variants, and optional `CONFIG_INTERCONNECT_IMX` provider names supplied through match data.

Risks and test signals: the clock is intentionally not enabled, relying on safe `clk_set_rate()` while disabled. `imx_bus_init_icc()` logs but returns success for unknown interconnect driver match data, so missing ICC providers can be easy to miss. Test signals include OPP rate changes through userspace `set_freq`, current frequency reporting, disabled-clock rate programming, OPP-table cleanup on failure, ICC child creation when `#interconnect-cells` is present, and no crash when interconnect support is disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/devfreq/imx-bus.c -->
