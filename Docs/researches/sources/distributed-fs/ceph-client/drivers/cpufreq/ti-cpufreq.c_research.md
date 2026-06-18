# sources/distributed-fs/ceph-client/drivers/cpufreq/ti-cpufreq.c

Purpose: selects TI CPU OPPs by SoC revision and eFuse speed grade, then launches `cpufreq-dt`. It supports AM33xx/AM43xx/DRA7/OMAP3 and newer K3 AM62 family variants with SoC-specific eFuse translation.

Important APIs and functions: `ti_cpufreq_soc_data` describes register offsets, masks, translations, regulator names, and compatibility quirks. Translators such as `amx3_efuse_xlate()`, `dra7_efuse_xlate()`, `omap3_efuse_xlate()`, `am625_efuse_xlate()`, and AM62 variants convert raw bins into OPP supported-hw bitmasks. `ti_cpufreq_get_efuse()` and `ti_cpufreq_get_rev()` read syscon or fallback MMIO for older OMAP quirks. `ti_cpufreq_probe()` gets CPU0 OPP node, syscon, computes the two-version array, optionally supplies multi-regulator names, calls `dev_pm_opp_set_config()`, and registers `cpufreq-dt`.

Control flow and state: init uses `of_machine_get_match()` and `platform_device_register_data()` to pass the matched SoC data to a built-in platform driver. Probe uses devm allocation for context but does not store it after setup. Missing OPP-v2 falls through so legacy tables can be tried by `cpufreq-dt`.

Dependencies and integration points: depends on SoC DT compatibles, CPU0 OPP-v2 `syscon` phandle, sys_soc matching for K3 revision handling, OPP supported-hw and regulator-name configuration, and generic `cpufreq-dt`.

Risks and test signals: risks include no OPP config token cleanup, hard-coded fallback `ioremap()` for OMAP3 control registers, K3 revision hard-coded to 0x1, broad eFuse translation fallthrough semantics, and `platform_device_register_simple("cpufreq-dt")` return value ignored. Test signals include revision/eFuse values matching silicon docs, OPP tables filtered to available speed grades, multi-regulator names applied on DRA7/OMAP36xx, legacy DT path still registering cpufreq-dt, and syscon single-register quirk working for AM625.
