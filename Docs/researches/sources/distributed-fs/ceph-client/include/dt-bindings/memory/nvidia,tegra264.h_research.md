<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/memory/nvidia,tegra264.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/memory/nvidia,tegra264.h

## Purpose
This header defines NVIDIA Tegra264 SMMU stream IDs and memory controller client IDs for device-tree memory/interconnect/IOMMU bindings.

## Important APIs, types, and functions
It exports `TEGRA264_SID(x)` and stream ID macros for AON, APE, BPMP, DCE, EQOS, GPCDMA, display, host1x, ISP, FSI, PVA, SDMMC0, MGBE, security engines, PSC, UFS, RCE, VI, VIC, and XUSB devices. It also exports `TEGRA264_MEMORY_CLIENT_*` IDs for host1x, VIC, VI, NVDEC, BPMP, display, UFS, DLA/PVA-like accelerators, PCIe, MGBE, SDMMC, and USB-related clients.

## Control flow
Tegra264 DTS nodes use SIDs in IOMMU specifiers and memory client IDs in memory controller properties. The SMMU and memory controller drivers decode the values to program stream matching, isolation, and bandwidth/fault accounting.

## State and persistence
The header has no state. SIDs and client IDs persist in DTBs; runtime state lives in the SMMU, memory controller, and client drivers.

## Dependencies and integration points
It integrates with Tegra264 SMMU, host1x/display, camera/VI/ISP/RCE, BPMP, networking, storage, USB, security engines, and memory controller drivers.

## Risks and test signals
Risks include SID shift misuse from `TEGRA264_SID(x)`, assigning unshifted values in DTS, and memory-client ID drift from hardware manuals. Test signals include `dtbs_check`, SMMU probe and stream table logs, DMA tests per client class, memory-controller fault reporting, and BPMP/firmware compatibility checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/memory/nvidia,tegra264.h -->
