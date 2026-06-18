# sources/distributed-fs/ceph-client/drivers/cpufreq/airoha-cpufreq.c

Purpose: Airoha SoC cpufreq glue driver that configures CPU OPP/power-domain handling and then instantiates the generic `cpufreq-dt` platform driver.

Important APIs/types/functions: `struct airoha_cpufreq_priv` stores OPP config token, attached PM domain list, and child `cpufreq-dt` platform device. Global `cpufreq_pdev` holds the synthetic parent platform device. `airoha_cpufreq_config_clks_nop()` disables OPP clock setting by returning success without changing clocks. Probe/remove handle OPP config, PM domain attach/detach, and child device registration. Module init matches machine compatibles and registers the platform driver/device pair.

Control flow: module init checks `of_machine_get_match()` for `airoha,an7583` or `airoha,en7581`, registers the driver, and creates an `airoha-cpufreq` platform device carrying the match. Probe obtains CPU0 device, installs an OPP config with CPU clock name and no-op clock setter, attaches required `perf` power domain with OPP device links, registers `cpufreq-dt`, and stores private data. Remove unregisters the child, detaches PM domains, and clears OPP config.

State and persistence: runtime state is the OPP config token, PM domain attachment list, and child platform device. No frequency table is stored here; the generic cpufreq-dt driver owns actual cpufreq policy state.

Dependencies and integration: uses OPP core, PM domain list attach, platform devices, OF machine matching, and `cpufreq-dt.h`. It is built for `CONFIG_ARM_AIROHA_SOC_CPUFREQ`.

Risks: assumes CPU0 represents all CPUs and that CPUs share the same OPP table. Cleanup ordering must reverse probe exactly to avoid lingering OPP config or PM links. The no-op clock config means frequency changes rely on the PM domain/OPP machinery rather than direct clock changes.

Test signals: boot on matching Airoha DT, verify `cpufreq-dt` child appears, OPP table and required `perf` domain are attached, cpufreq policies scale through generic dt path, remove/unload unregisters child and detaches domains, and non-matching machines return `-ENODEV`.
