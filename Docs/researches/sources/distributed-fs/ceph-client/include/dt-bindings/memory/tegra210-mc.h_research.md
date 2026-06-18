<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/memory/tegra210-mc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/memory/tegra210-mc.h

## Purpose
This header defines Tegra210 memory controller SWGROUP IDs, reset IDs, and memory client IDs for DT memory/SMMU/reset bindings.

## Important APIs, types, and functions
It exports `TEGRA_SWGROUP_*` IDs for PTC, display, AFI, AVPC, HDA, host, NVENC, SATA, CPU, ISP, XUSB, TSEC, GPU, SDMMC, VIC, VI, NVDEC, APE, NVJPG, SE, AXIAP, ETR, and related groups. It also exports `TEGRA210_MC_RESET_*` reset IDs and `TEGRA210_MC_*` memory clients for display, AFI, AVPC, HDA, host1x, NVENC, SATA, CPU, ISP, XUSB, TSEC, GPU, SDMMC, VIC, VI, NVDEC, APE, NVJPG, SE, AXIAP, and ETR read/write clients.

## Control flow
Tegra210 DTS nodes reference these constants in SMMU/memory-controller/reset specifiers. The Tegra MC/SMMU and reset drivers decode the numeric cells to program SWGROUP isolation, reset bits, and memory client tracking.

## State and persistence
No state is stored in the header. IDs persist in DTBs; runtime state lives in MC registers, SMMU/SWGROUP configuration, reset controls, and fault reporting.

## Dependencies and integration points
It integrates with Tegra210 memory controller, SMMU, reset controller, display, host1x, storage, USB, GPU, media, security, audio, and CPU clients.

## Risks and test signals
Risks include namespace confusion between SWGROUP, reset, and memory client constants, sparse client ID gaps, and generation drift from Tegra124. Test signals include `dtbs_check`, MC/SMMU probe, reset operations, DMA from display/GPU/storage/USB/media clients, and MC fault decode accuracy.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/memory/tegra210-mc.h -->
