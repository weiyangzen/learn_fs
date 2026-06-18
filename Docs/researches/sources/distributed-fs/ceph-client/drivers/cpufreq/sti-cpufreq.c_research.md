# sources/distributed-fs/ceph-client/drivers/cpufreq/sti-cpufreq.c

Purpose: prepares STMicroelectronics STiH407/STiH410/STiH418 CPU OPP selection before launching the generic `cpufreq-dt` platform device. It selects OPP variants by SoC major/minor version, process code, and substrate code read from syscon registers.

Important APIs and functions: `sti_cpufreq_fetch_syscon_registers()` obtains `st,syscfg` and `st,syscfg-eng` regmaps. `sti_cpufreq_fetch_major()`, `sti_cpufreq_fetch_minor()`, and `sti_cpufreq_fetch_regmap_field()` read version and DVFS bitfields. `sti_cpufreq_set_opp_info()` builds a `dev_pm_opp_config` with `supported_hw` and a `prop_name` such as `pcode0`, then calls `dev_pm_opp_set_config()`. `sti_cpufreq_init()` gates by machine compatible, validates CPU0 OPP-v2, and always registers `cpufreq-dt` after the voltage-scaling attempt.

Control flow and state: a single static `ddata` holds CPU device and syscon regmaps. Missing hardware info offset falls back to default version bits; failed pcode/substrate/major/minor reads mostly degrade to defaults except syscon acquisition failure. The OPP token is not stored for later cleanup because this is an init-only platform setup path.

Dependencies and integration points: depends on DT properties `operating-points-v2`, `st,syscfg`, and `st,syscfg-eng`, ST machine compatibles, regmap fields, OPP supported-hw/prop-name filtering, and generic `cpufreq-dt`.

Risks and test signals: risks include `dev_err(ddata.cpu, ...)` after `get_cpu_device(0)` returns NULL, no unregister path for the OPP config token or created platform device, defaulting that may expose conservative but unexpected OPPs, and only STiH407 field layout support. Test signals include syscon phandle reads, debug pcode/version values, OPP table filtered by `opp-supported-hw` and named voltages, and `cpufreq-dt` binding even when voltage scaling is skipped.
