<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/memory/tegra194-mc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/memory/tegra194-mc.h

## Purpose
This header defines Tegra194 SMMU stream IDs and memory controller client IDs, including virtualization-capable host1x/security-engine stream IDs and a large set of MC clients.

## Important APIs, types, and functions
It exports `TEGRA194_SID_*` values for core engines, GPU, AFI/HDA/ETR/EQOS/UFS/AON/SDMMC/XUSB/SATA/APE/SCE, GPCDMA, RCE/VI/ISP falcons, BPMP, host1x contexts/VMs, SE VMs, NVDLA/PVA/NVENC/PCIe/XUSB VFs, and additional VM/server IDs. It also exports `TEGRA194_MEMORY_CLIENT_*` IDs from low legacy clients through MIU, NVL, DLA, PVA, RCE, PCIe, and extended codec clients.

## Control flow
DTS uses SIDs for IOMMU stream matching and memory client IDs for memory controller configuration or fault identification. Tegra SMMU/MC drivers decode them during device attach, context isolation, and fault reporting.

## State and persistence
No state lives in the header. The IDs persist in DTBs; runtime state exists in SMMU stream tables, MC registers, virtualization contexts, and firmware-coordinated clients.

## Dependencies and integration points
It integrates with Tegra194 SMMU, memory controller, host1x virtualization, display, camera/RCE/VI/ISP, GPU, NVDLA/PVA, PCIe, XUSB, UFS, EQOS, BPMP, AON, SCE, APE, and security engine drivers.

## Risks and test signals
Risks include altering firmware-sensitive IDs such as BPMP, confusing host1x context IDs with VM IDs, passthrough misuse, and sparse MC client IDs hiding omissions. Test signals include DTS validation, SMMU attach logs, virtualization context tests, BPMP boot, PCIe/XUSB/UFS DMA, accelerator DMA, and MC fault decode tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/memory/tegra194-mc.h -->
