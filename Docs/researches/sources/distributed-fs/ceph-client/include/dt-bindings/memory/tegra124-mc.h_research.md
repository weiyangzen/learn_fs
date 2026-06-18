<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/memory/tegra124-mc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/memory/tegra124-mc.h

## Purpose
This header defines Tegra124 memory controller SWGROUP IDs, reset IDs, and memory client IDs for device tree.

## Important APIs, types, and functions
It exports `TEGRA_SWGROUP_*` IDs, `TEGRA124_MC_RESET_*` reset controls, and many `TEGRA124_MC_*` memory client IDs such as display, AFI, AVPC, HDA, host1x, MSENC, SATA, VDE, CPU, ISP, XUSB, TSEC, GPU, SDMMC, VIC, and displayD clients.

## Control flow
DTS nodes use SWGROUPs for memory isolation, reset IDs for MC-driven resets, and memory client IDs for MC client configuration. Tegra MC drivers decode the constants to program hardware tables and reset bits.

## State and persistence
No state exists here. IDs persist in DTBs; runtime MC state includes resets, arbitration, fault reporting, and SMMU/SWGROUP configuration.

## Dependencies and integration points
It integrates with Tegra124 MC/SMMU, reset controller, display, host1x, HDA, SATA, VDE, ISP, XUSB, TSEC, GPU, SDMMC, and VIC drivers.

## Risks and test signals
Risks include sparse memory client IDs, mixing reset and client namespaces, and using shared `TEGRA_SWGROUP_*` names from another Tegra generation incorrectly. Test signals include DTS validation, MC probe, reset assertions/deassertions, DMA from major clients, and MC fault decode correctness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/memory/tegra124-mc.h -->
