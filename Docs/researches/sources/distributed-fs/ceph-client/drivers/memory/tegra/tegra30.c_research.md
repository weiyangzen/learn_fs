# sources/distributed-fs/ceph-client/drivers/memory/tegra/tegra30.c

Purpose: This file defines Tegra30 memory-controller SoC data for the shared Tegra MC driver and implements Tegra30-specific interconnect latency tuning. It covers MC client tables, SMMU groups, reset lines, EMEM timing-register lists, interrupt masks, ICC callbacks, and the exported `tegra30_mc_soc`.

Important APIs/types/functions: Data tables include `tegra30_mc_emem_regs`, `tegra30_mc_clients`, `tegra30_swgroups`, `tegra30_groups`, `tegra30_smmu_soc`, `tegra30_mc_resets`, and `tegra30_mc_intmasks`. `tegra30_mc_tune_client_latency()` converts a client's peak bandwidth and FIFO size into latency-allowance ticks with special compensation for display and VI. `tegra30_mc_icc_set()` applies that tuning from ICC peak bandwidth. `tegra30_mc_icc_aggreate()` boosts ISO peak bandwidth before aggregation. `tegra30_mc_of_icc_xlate_extended()` tags default ISO clients.

Control flow: The common MC core consumes `tegra30_mc_soc`. ICC translation maps DT client IDs to ICC nodes and assigns ISO/default tags. ICC aggregation scales ISO requests, then `set` programs latency allowance registers. Reset, SMMU, interrupt, and EMEM timing tables are used by shared Tegra MC operations.

State and persistence: All local data is immutable except hardware LA registers programmed by `tegra30_mc_tune_client_latency()`. There is no file-backed persistence. Hardware configuration remains until later ICC updates or reset.

Dependencies and integration: Depends on Tegra30 memory DT bindings, shared `mc.h`, Linux device/OF helpers, and common Tegra MC/SMMU/reset/ICC code. It pairs with `tegra30-emc.c`, which drives EMC rates and timing changes.

Risks and test signals: Risks include incorrect FIFO sizes, LA register fields, ISO tagging, and the misspelled but internally wired `tegra30_mc_icc_aggreate` callback being overlooked during refactors. Test signals include display/VI underrun testing, ICC path creation from DT, client fault attribution, SMMU mapping tests, and reset-control validation.
