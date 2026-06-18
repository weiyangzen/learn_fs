# sources/distributed-fs/ceph-client/drivers/cpufreq/imx-cpufreq-dt.c

Purpose: wraps `cpufreq-dt` for NXP/Freescale i.MX platforms that need speed-grade or market-segment OPP filtering, and provides i.MX7ULP intermediate-clock callbacks for safe frequency switching.

Important APIs and control flow: for i.MX7ULP, `imx7ulp_get_intermediate()` returns the FIRC rate and `imx7ulp_target_intermediate()` reparents SCS selectors to FIRC, switches ARM between normal and high-speed cores based on target frequency, and is passed as `cpufreq_dt_platform_data` when registering `cpufreq-dt`. For other supported i.MX variants, probe requires `cpu-supply`, reads `speed_grade` nvmem, extracts speed grade and market segment with SoC-specific masks, applies early-sample fuse clamping for i.MX8M, calls `dev_pm_opp_set_supported_hw()`, and registers a child `cpufreq-dt` platform device. Remove unregisters the child and releases either OPP supported-hw token or bulk clocks.

State and persistence behavior: static globals hold the registered `cpufreq-dt` platform device, CPU device, and OPP supported-hw token. For i.MX7ULP, bulk clock handles persist until remove. OPP filtering state persists in the PM OPP core until `dev_pm_opp_put_supported_hw()`.

Dependencies and integration points: depends on CPU0 DT node, `cpu-supply`, nvmem cell `speed_grade`, OPP supported-hw bindings, i.MX machine compatibles, common clock bulk APIs, and `cpufreq-dt` platform data callbacks.

Risks and test signals: risks include CPU device/node assumptions without explicit null checks after `get_cpu_device(0)`, SoC-specific fuse masks needing exact alignment with bindings, early-sample clamping hiding real fuse problems, global singleton state, lack of return checking for individual `clk_set_parent()` calls in intermediate switching, and failure if `cpu-supply` is intentionally absent. Test signals include supported-hw masks logged as expected, OPP table filtered to legal frequencies, i.MX7ULP intermediate parent switching during transitions, cpufreq-dt child creation/removal, and correct cleanup on probe failures.
