# sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/qcom,sdx55.h

## Purpose
defines Qualcomm interconnect node identifiers for qcom sdx55, forming the numeric namespace used by Devicetree bandwidth consumers and the SoC interconnect provider driver.

## Important APIs, Types, and Functions
The exported API is 58 `#define` constants. Representative symbols are `MASTER_LLCC`, `SLAVE_EBI_CH0`, `MASTER_TCU_0`, `MASTER_SNOC_GC_MEM_NOC`, `MASTER_AMPSS_M0`, `SLAVE_LLCC`, `SLAVE_MEM_NOC_SNOC`, `SLAVE_MEM_NOC_PCIE_SNOC`, `MASTER_AUDIO`, `MASTER_BLSP_1`. numeric values span 0..49 across 58 direct numeric defines. Top naming groups: `SLAVE` (13), `MASTER` (7), `MASTER_MEM` (2), `MASTER_QDSS` (2), `MASTER_SNOC` (2).

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
