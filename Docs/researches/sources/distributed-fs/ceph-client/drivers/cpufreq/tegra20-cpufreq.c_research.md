# sources/distributed-fs/ceph-client/drivers/cpufreq/tegra20-cpufreq.c

Purpose: configures Tegra20/Tegra30-era OPP supported-hardware masks from fuse-derived process and speedo IDs, then instantiates `cpufreq-dt`.

Important APIs and functions: `cpu0_node_has_opp_v2_prop()` validates CPU0 OPP-v2 presence. Probe computes two `versions[]` words from `tegra_sku_info`: Tegra20 uses CPU process and SoC speedo IDs; later matching platforms use CPU process and CPU speedo IDs. It calls `dev_pm_opp_set_supported_hw()` for CPU0 and registers cleanup through `devm_add_action_or_reset()`, then creates a `cpufreq-dt` platform device with devm unregister action.

Control flow and state: no persistent driver-private state is needed; devm cleanup stores the OPP token and platform device. The platform driver binds to a synthetic `tegra20-cpufreq` device provided elsewhere via platform alias.

Dependencies and integration points: depends on Tegra common/fuse SKU data, CPU0 OPP-v2 DT, OPP supported-hw filtering, and generic `cpufreq-dt`.

Risks and test signals: risks include only configuring CPU0, hard dependence on updated DT, assumptions about speedo field semantics across Tegra generations, and action data casting the OPP token through `void *`. Test signals include hardware version log matching fuse values, supported OPPs filtered to expected process/speedo rows, `cpufreq-dt` device creation, and devm cleanup clearing OPP config on probe failure or unbind.
