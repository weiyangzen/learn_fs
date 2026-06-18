# sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/imx8mm.h

## Purpose
defines NXP i.MX interconnect node identifiers for imx8mm, forming the numeric namespace used by Devicetree bandwidth consumers and the SoC interconnect provider driver.

## Important APIs, Types, and Functions
The exported API is 29 `#define` constants. Representative symbols are `IMX8MM_ICN_NOC`, `IMX8MM_ICS_DRAM`, `IMX8MM_ICS_OCRAM`, `IMX8MM_ICM_A53`, `IMX8MM_ICM_VPU_H1`, `IMX8MM_ICM_VPU_G1`, `IMX8MM_ICM_VPU_G2`, `IMX8MM_ICN_VIDEO`, `IMX8MM_ICM_GPU2D`, `IMX8MM_ICM_GPU3D`. numeric values span 1..29 across 29 direct numeric defines. Top naming groups: `IMX8MM_ICM` (19), `IMX8MM_ICN` (8), `IMX8MM_ICS` (2).

## Control Flow
The header contains no executable flow. Devicetree interconnect specifiers reference these IDs; the interconnect framework passes them to the provider, which maps each ID to an internal node and aggregates bandwidth votes at runtime.

## State, Persistence, and Dependencies
The header stores no mutable state. The persistent contract is the stable ID-to-node mapping encoded in DTBs and mirrored by provider-driver topology tables. It integrates with the NXP i.MX interconnect provider driver, SoC DTS files, and consumers such as display, camera, GPU, CPU, storage, USB, PCIe, memory controller, and NoC endpoints.

## Integration Points
Primary integration points are Devicetree source files that include this header, binding schemas that document the allowed cells/properties, and the platform driver or subsystem core that consumes the numeric value after OF parsing.

## Risks
The main risks are numeric mismatch with provider arrays, duplicate or skipped IDs not handled by the driver, and renumbering nodes after DTBs ship. Those failures can silently under-vote or over-vote NoC bandwidth and break devices under load.

## Test Signals
Use dtbs_check, compile all SoC DTS users, compare max exported IDs against provider table sizes, scan for duplicates, and run device stress tests that exercise interconnect bandwidth votes for major masters/slaves.
