# sources/distributed-fs/ceph-client/drivers/cpufreq/sun50i-cpufreq-nvmem.c

Purpose: reads Allwinner sun50i speed-bin efuses and configures CPU OPP filtering before instantiating `cpufreq-dt`. It handles H6, A100, H616/H618/H700 style OPP descriptors.

Important APIs and functions: efuse translators `sun50i_h6_efuse_xlate()`, `sun50i_a100_efuse_xlate()`, and `sun50i_h616_efuse_xlate()` map raw nvmem bits to speed grade indexes. `sun50i_cpufreq_get_efuse()` locates CPU0's OPP descriptor node, matches its compatible, reads the unnamed nvmem cell, converts little-endian data, and returns a speed bin. `dt_has_supported_hw()` checks whether OPP children contain `opp-supported-hw`. Probe allocates per-CPU OPP config tokens, sets `supported_hw` only when needed, sets a `prop_name` like `speed2`, applies the config to all present CPUs, then registers `cpufreq-dt`.

Control flow and state: module init first verifies machine compatibility, registers a platform driver, then creates a matching platform device so probe can defer on nvmem. Global platform-device pointers are used for cleanup. Per-probe state is the `opp_tokens` array stored in drvdata and cleared on remove.

Dependencies and integration points: depends on NVMEM cells under OPP tables, OPP-v2 descriptors, optional SMCCC SoC revision for H616 bin interpretation, CPU devices for all present CPUs, and generic `cpufreq-dt`.

Risks and test signals: risks include treating unknown bins as slowest, skipping `supported_hw` when DT lacks it but still selecting named properties, partial OPP config cleanup across possible/present CPU mismatch, a global `cpufreq_dt_pdev`, and H616 revision behavior depending on SMCCC discovery availability. Test signals include nvmem probe deferral, warning on unknown H616 bins, OPPs filtered to expected speed grade, all present CPUs receiving tokens, and clean remove unregistering `cpufreq-dt` and clearing configs.
