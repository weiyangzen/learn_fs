# sources/distributed-fs/ceph-client/drivers/cpufreq/tegra186-cpufreq.c

Purpose: implements a Tegra186 CPUFreq driver that reads BPMP firmware voltage/frequency hints, writes per-core EDVD registers to request CPU frequency/voltage, and optionally scales DRAM bandwidth through OPP/interconnect data.

Important APIs and functions: `tegra_cpufreq_bpmp_read_lut()` sends `MRQ_CPU_VHINT` through BPMP using coherent DMA, filters valid `ndiv` entries, stores EDVD `driver_data`, and computes kHz rates. `tegra186_cpufreq_probe()` maps the EDVD MMIO resource, reads LUTs for two clusters, initializes cores to each cluster's max EDVD value, enables optional ICC scaling if CPU0 has OPP/interconnect paths, and registers `tegra186_cpufreq_driver`. Driver hooks include `tegra186_cpufreq_init()`, `tegra186_cpufreq_set_target()`, and `tegra186_cpufreq_get()`.

Control flow and state: static CPU metadata maps logical CPUs to BPMP cluster IDs and EDVD offsets. Runtime data stores MMIO base, per-cluster LUT/ref clock/divisor, and an `icc_dram_bw_scaling` flag. Policy init groups CPUs by BPMP cluster and either builds a DT OPP-filtered table or falls back to the BPMP LUT.

Dependencies and integration points: depends on Tegra BPMP firmware ABI, platform MMIO resource, CPU OPP-v2/interconnect support, CPUFreq generic table verification, and per-policy governors. `driver_data` is stored globally in the cpufreq driver.

Risks and test signals: risks include global driver data for one device instance, allocated OPP-derived frequency tables not explicitly freed, ICC scaling being disabled globally after one failure, policy init loops over `ARRAY_SIZE(tegra186_cpus)` rather than dynamic CPU count, and no readback after EDVD writes. Test signals include BPMP LUT nonempty for both clusters, EDVD registers initialized to max, policy masks matching Denver/A57 clusters, `get` rate matching `ref_clk_khz * ndiv / div`, and OPP/ICC fallback message only when DT data is missing or invalid.
