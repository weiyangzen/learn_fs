# sources/distributed-fs/ceph-client/drivers/memory/tegra/tegra124.c

## Purpose
This file is the Tegra124/Tegra132 memory-controller SoC description consumed by the common Tegra MC driver. It enumerates memory clients, SMMU software groups, grouped DRM SMMU policy, reset controls, interrupt masks, and interconnect aggregation behavior. There is no standalone platform driver here; the exported `tegra124_mc_soc` and `tegra132_mc_soc` structures are selected by the common MC match table when the corresponding SoC config is enabled.

## Important APIs, Types, And Functions
The core data objects are `tegra124_mc_clients`, `tegra124_swgroups`, `tegra124_groups`, `tegra124_mc_resets`, `tegra124_smmu_soc`, `tegra132_smmu_soc`, `tegra124_mc_intmasks`, `tegra132_mc_intmasks`, `tegra124_mc_soc`, and `tegra132_mc_soc`. Client entries map numeric memory-client IDs to names, SMMU enable bits, latency-allowance register fields, and SWGROUP IDs. Reset entries are created with `TEGRA124_MC_RESET()` and use common reset ops. ICC hooks are `tegra124_mc_of_icc_xlate_extended()`, `tegra124_mc_icc_aggreate()`, and `tegra124_mc_icc_set()`.

## Control Flow
At probe time the common MC driver reads the selected `struct tegra_mc_soc`, creates memory-client ICC nodes, configures interrupt masks, and exposes resets using this file's static tables. ICC translation looks up the requested client ID among provider nodes. If the client exists but its ICC node has not been created yet, translation returns `-EPROBE_DEFER`; unknown IDs are logged and rejected with `-EINVAL`. Display, display-B, PTC, and VI clients are tagged isochronous by default. Aggregation sums average bandwidth and uses the maximum peak bandwidth, scaling isochronous peak requests by 400 percent. The `set` hook is a stub that returns success with a TODO for PTSA programming.

## State And Persistence
The file itself maintains no runtime state. State is stored by the common MC/SMMU/ICC layers using these constant descriptors: hardware registers hold SMMU enables, latency allowances, interrupt masks, and reset state; ICC node data allocated by `kzalloc_obj()` is transient per translation. Configuration is rebuilt on driver probe and resume by common code, not persisted in this file.

## Dependencies And Integration Points
It depends on `mc.h`, `dt-bindings/memory/tegra124-mc.h`, the common Tegra MC register definitions (`tegra20_mc_regs`, `tegra30_mc_ops`, `tegra30_mc_irq_handlers`), common reset operations, the Tegra SMMU integration, and the Linux interconnect framework. The `CONFIG_ARCH_TEGRA_124_SOC` and `CONFIG_ARCH_TEGRA_132_SOC` blocks export separate SoC descriptors sharing the same client/reset/SMMU tables. Device tree interconnect specifiers must use memory-client IDs that match `tegra124_mc_clients`.

## Risks
The table is correctness-critical: wrong IDs, SMMU bits, reset bits, or latency-allowance shifts can break DMA isolation, reset sequencing, display/video throughput, or error attribution. The 400 percent ISO scaling is conservative but may over-reserve bandwidth. The `tegra124_mc_icc_set()` stub means bandwidth requests do not program PTSA knobs despite successful ICC votes, so performance behavior depends on boot defaults and other MC/EMC drivers. Array indexing in xlate uses `mc->soc->clients[idx]` after matching `node->id == idx`; this assumes client IDs are dense enough to index the clients array, which should be watched when adding sparse IDs.

## Test Signals
Useful validation signals are successful MC probe on Tegra124/Tegra132, SMMU client registration, reset-controller consumers toggling each reset, interrupt decode logs for DECERR/security/page faults, and ICC paths resolving for display/VI/PTC as ISO. Device-tree ABI tests should cover valid and invalid interconnect client IDs. Hardware smoke tests should exercise display, VIC, XUSB, SDMMC, SATA, GPU, and VDE DMA with SMMU enabled and verify no unexpected MC faults.
