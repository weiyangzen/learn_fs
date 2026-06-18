# sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/mediatek,mt8183.h

## Purpose
defines MediaTek interconnect node identifiers for mediatek mt8183, forming the numeric namespace used by Devicetree bandwidth consumers and the SoC interconnect provider driver.

## Important APIs, Types, and Functions
The exported API is 11 `#define` constants. Representative symbols are `SLAVE_DDR_EMI`, `MASTER_MCUSYS`, `MASTER_MFG`, `MASTER_MMSYS`, `MASTER_MM_VPU`, `MASTER_MM_DISP`, `MASTER_MM_VDEC`, `MASTER_MM_VENC`, `MASTER_MM_CAM`, `MASTER_MM_IMG`. numeric values span 0..10 across 11 direct numeric defines. Top naming groups: `MASTER_MM` (7), `MASTER` (3), `SLAVE_DDR` (1).

## Control Flow
The header contains no executable flow. Devicetree interconnect specifiers reference these IDs; the interconnect framework passes them to the provider, which maps each ID to an internal node and aggregates bandwidth votes at runtime.

## State, Persistence, and Dependencies
The header stores no mutable state. The persistent contract is the stable ID-to-node mapping encoded in DTBs and mirrored by provider-driver topology tables. It integrates with the MediaTek interconnect provider driver, SoC DTS files, and consumers such as display, camera, GPU, CPU, storage, USB, PCIe, memory controller, and NoC endpoints.

## Integration Points
Primary integration points are Devicetree source files that include this header, binding schemas that document the allowed cells/properties, and the platform driver or subsystem core that consumes the numeric value after OF parsing.

## Risks
The main risks are numeric mismatch with provider arrays, duplicate or skipped IDs not handled by the driver, and renumbering nodes after DTBs ship. Those failures can silently under-vote or over-vote NoC bandwidth and break devices under load.

## Test Signals
Use dtbs_check, compile all SoC DTS users, compare max exported IDs against provider table sizes, scan for duplicates, and run device stress tests that exercise interconnect bandwidth votes for major masters/slaves.
