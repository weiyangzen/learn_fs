<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/tegra-icc.h -->
# sources/distributed-fs/ceph-client/include/linux/tegra-icc.h

## Purpose
defines NVIDIA Tegra interconnect client classes and BPMP memory-controller client IDs shared by Tegra interconnect and firmware-facing code.

## Important APIs, Types, and Functions
The file is 66 lines and exports these visible symbol families: types/enums `tegra_icc_client_type`; macros/constants `LINUX_TEGRA_ICC_H`, `TEGRA_ICC_BPMP_DEBUG`, `TEGRA_ICC_BPMP_CPU_CLUSTER0`, `TEGRA_ICC_BPMP_CPU_CLUSTER1`, `TEGRA_ICC_BPMP_CPU_CLUSTER2`, `TEGRA_ICC_BPMP_GPU`, `TEGRA_ICC_BPMP_CACTMON`, `TEGRA_ICC_BPMP_DISPLAY`, `TEGRA_ICC_BPMP_VI`, `TEGRA_ICC_BPMP_EQOS`, `TEGRA_ICC_BPMP_PCIE_0`, `TEGRA_ICC_BPMP_PCIE_1`, `TEGRA_ICC_BPMP_PCIE_2`, `TEGRA_ICC_BPMP_PCIE_3`, and 32 more; function-like macros none; inline helpers none; external prototypes none.

## Control Flow
Tegra drivers or device-tree-interpreting code select an ICC client type and BPMP client ID, then use the interconnect/BPMP path to request bandwidth or classify memory traffic for display, VI, audio, GPU, PCIe, DLA, XUSB, and other engines.

## State and Persistence Behavior
The header has no runtime state; the numeric IDs are stable firmware/protocol tokens.

## Dependencies and Integration Points
It is self-contained and integrates with Tegra BPMP firmware, memory controller clients, interconnect providers, and device-tree bandwidth consumers. Direct includes are none.

## Risks and Edge Cases
Renumbering or assigning the wrong BPMP client ID can throttle or over-provision the wrong hardware engine. ISO/non-ISO classification affects latency-sensitive display/camera/audio traffic.

## Test Signals
Compile Tegra configs and DTS users, compare IDs against BPMP ABI documentation, and validate bandwidth requests for display, VI, PCIe, XUSB, and GPU clients on hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/tegra-icc.h -->
