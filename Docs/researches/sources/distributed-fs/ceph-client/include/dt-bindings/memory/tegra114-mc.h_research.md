<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/memory/tegra114-mc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/memory/tegra114-mc.h

## Purpose
This header defines Tegra114 memory controller software group IDs and reset IDs for memory clients.

## Important APIs, types, and functions
It exports `TEGRA_SWGROUP_*` IDs for PTC, DC/DCB, EPP, G2, MPE, VI, AFI, AVPC, NV, HC, PPCS, SATA, VDE, and MPCORELP, plus reset IDs `TEGRA114_MC_RESET_*` for AVPC, display, EPP/2D/3D, HC/HDA, ISP, CPU clusters, MPE, PPCS, VDE, and VI.

## Control flow
Tegra114 DTS uses these constants in memory-controller/IOMMU and reset specifiers. The Tegra MC driver maps IDs to SWGROUP registers and reset controls.

## State and persistence
The header is stateless. DTB values persist; runtime isolation, reset, and fault state is in MC hardware and drivers.

## Dependencies and integration points
It integrates with Tegra114 memory controller, SMMU/SWGROUP configuration, reset controller users, display, video, SATA, host, and CPU-related clients.

## Risks and test signals
Risks include confusing SWGROUP IDs with reset IDs, wrong client reset line, and compatibility drift with Tegra124/210 headers that share names. Test signals include DTS validation, MC probe, client reset tests, DMA isolation tests, and memory fault logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/memory/tegra114-mc.h -->
