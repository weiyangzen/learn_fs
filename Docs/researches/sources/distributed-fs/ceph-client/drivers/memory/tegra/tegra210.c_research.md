# sources/distributed-fs/ceph-client/drivers/memory/tegra/tegra210.c

Purpose: This file describes the Tegra210 memory-controller SoC integration for the shared Tegra MC driver. It enumerates MC clients, SMMU software groups, display grouping, reset lines, interrupt masks, and the exported `tegra210_mc_soc` descriptor.

Important APIs/types/functions: The primary exported object is `const struct tegra_mc_soc tegra210_mc_soc`. Supporting tables include `tegra210_mc_clients`, `tegra210_swgroups`, `tegra210_groups`, `tegra210_smmu_soc`, `tegra210_mc_resets`, and `tegra210_mc_intmasks`. Each `struct tegra_mc_client` maps a DT binding client ID to a name, SWGROUP, SMMU enable bit, latency-allowance register field, and default LA value. Reset entries use `TEGRA210_MC_RESET`.

Control flow: This file has no probe function. At runtime the common Tegra MC core selects `tegra210_mc_soc`, registers clients/SMMU groups, initializes reset controls, programs interrupt masks, and routes faults through common `tegra30_mc_irq_handlers`. Client and reset tables are indexed by common code rather than traversed locally.

State and persistence: Static const tables define hardware topology and default configuration. Live state resides in the common MC driver and hardware registers. The table data is persistent for the lifetime of the kernel image.

Dependencies and integration: Depends on `dt-bindings/memory/tegra210-mc.h` and shared `mc.h`. It integrates with the Tegra SMMU, reset controller, interconnect/latency allowance logic, and shared Tegra20/Tegra30 register/IRQ helper sets.

Risks and test signals: Risks are table mismatches: wrong client IDs, LA fields, SWGROUP registers, reset bits, or interrupt masks can break DMA isolation, reset sequencing, or fault attribution. Test signals include IOMMU attach for all Tegra210 clients, working display/GPU/storage/video clients, correct MC fault logs, and reset-controller exercise for each listed hardware block.
