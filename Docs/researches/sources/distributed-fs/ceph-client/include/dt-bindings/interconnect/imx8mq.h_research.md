# sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/imx8mq.h

## Purpose
defines NXP i.MX interconnect node identifiers for imx8mq, forming the numeric namespace used by Devicetree bandwidth consumers and the SoC interconnect provider driver.

## Important APIs, Types, and Functions
The exported API is 28 `#define` constants. Representative symbols are `IMX8MQ_ICN_NOC`, `IMX8MQ_ICS_DRAM`, `IMX8MQ_ICS_OCRAM`, `IMX8MQ_ICM_A53`, `IMX8MQ_ICM_VPU`, `IMX8MQ_ICN_VIDEO`, `IMX8MQ_ICM_GPU`, `IMX8MQ_ICN_GPU`, `IMX8MQ_ICM_DCSS`, `IMX8MQ_ICN_DCSS`. numeric values span 1..28 across 28 direct numeric defines. Top naming groups: `IMX8MQ_ICM` (17), `IMX8MQ_ICN` (9), `IMX8MQ_ICS` (2).

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
