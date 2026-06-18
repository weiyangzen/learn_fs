<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/memory/tegra20-mc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/memory/tegra20-mc.h

## Purpose
This header defines Tegra20 memory controller reset IDs and memory client IDs for early Tegra device-tree bindings.

## Important APIs, types, and functions
It exports reset IDs `TEGRA20_MC_RESET_*` for AVPC, display, EPP, 2D/3D, HC, ISP, CPU, MPE, PPCS, VDE, and VI. It also exports `TEGRA20_MC_*` memory client IDs for display, EPP, G2, MPE, VI, AVPC, host1x, CPU, PPCS, texture, VDE, ISP, and read/write variants.

## Control flow
Tegra20 DTS uses these constants in memory-controller reset and client specifiers. The Tegra20 MC driver maps IDs to reset bits and memory client registers.

## State and persistence
The header is stateless. DTB IDs persist; runtime state includes memory client arbitration/faults and reset-control state.

## Dependencies and integration points
It integrates with Tegra20 MC, reset controller, display, host1x, 2D/3D, VI/ISP, VDE, MPE, PPCS, and CPU memory clients.

## Risks and test signals
Risks include mixing reset IDs and memory client IDs, sparse client numbering, and old-generation naming differences from later Tegra headers. Test signals include DTS validation, MC probe, reset tests for display/VDE/VI, DMA smoke tests, and MC fault decode checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/memory/tegra20-mc.h -->
