<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/memory/tegra186-mc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/memory/tegra186-mc.h

## Purpose
This header defines Tegra186 SMMU stream IDs and memory controller client IDs for device-tree memory/IOMMU configuration.

## Important APIs, types, and functions
It exports SIDs including `TEGRA186_SID_INVALID`, `PASSTHROUGH`, host1x, CSI, VIC, VI, ISP, NVDEC, NVENC, NVJPG, display, TSEC, SE, GPU, AFI, HDA, ETR, APE, SCE, BPMP, AON, SDMMC, XUSB, SATA, and APEDMA-related IDs. It also exports `TEGRA186_MEMORY_CLIENT_*` IDs for MC fault/accounting clients.

## Control flow
Tegra186 DTS nodes use SIDs in IOMMU specifiers and memory client IDs in MC-related properties. The SMMU and MC drivers decode the values during device attach, stream setup, and fault reporting.

## State and persistence
The header is stateless. DTB IDs persist across boots; runtime state is held by SMMU context, MC registers, and client drivers.

## Dependencies and integration points
It integrates with Tegra186 SMMU, memory controller, host1x/display, camera, video, security engines, storage, USB, BPMP, AON, and DMA clients.

## Risks and test signals
Risks include using `PASSTHROUGH` unintentionally, mismatched SID/client ID namespaces, and firmware-reserved IDs changing behavior. Test signals include DTS validation, SMMU attach logs, DMA tests for each client class, MC fault injection, and BPMP/AON communication tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/memory/tegra186-mc.h -->
