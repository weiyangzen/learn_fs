# sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/qcom,milos-rpmh.h

## Purpose
defines Qualcomm interconnect node identifiers for qcom milos rpmh, forming the numeric namespace used by Devicetree bandwidth consumers and the SoC interconnect provider driver.

## Important APIs, Types, and Functions
The exported API is 118 `#define` constants. Representative symbols are `MASTER_QUP_1`, `MASTER_UFS_MEM`, `MASTER_USB3_0`, `SLAVE_A1NOC_SNOC`, `MASTER_QDSS_BAM`, `MASTER_QSPI_0`, `MASTER_QUP_0`, `MASTER_CRYPTO`, `MASTER_IPA`, `MASTER_QDSS_ETR`. numeric values span 0..35 across 118 direct numeric defines. Top naming groups: `SLAVE` (13), `MASTER` (8), `SLAVE_PCIE` (5), `SLAVE_SERVICE` (5), `MASTER_CNOC` (4).

## Control Flow
The header contains no executable flow. Devicetree interconnect specifiers reference these IDs; the interconnect framework passes them to the provider, which maps each ID to an internal node and aggregates bandwidth votes at runtime.

## State, Persistence, and Dependencies
The header stores no mutable state. The persistent contract is the stable ID-to-node mapping encoded in DTBs and mirrored by provider-driver topology tables. It integrates with the Qualcomm interconnect provider driver, SoC DTS files, and consumers such as display, camera, GPU, CPU, storage, USB, PCIe, memory controller, and NoC endpoints.

## Integration Points
Primary integration points are Devicetree source files that include this header, binding schemas that document the allowed cells/properties, and the platform driver or subsystem core that consumes the numeric value after OF parsing.

## Risks
The main risks are numeric mismatch with provider arrays, duplicate or skipped IDs not handled by the driver, and renumbering nodes after DTBs ship. Those failures can silently under-vote or over-vote NoC bandwidth and break devices under load.

## Test Signals
Use dtbs_check, compile all SoC DTS users, compare max exported IDs against provider table sizes, scan for duplicates, and run device stress tests that exercise interconnect bandwidth votes for major masters/slaves.
