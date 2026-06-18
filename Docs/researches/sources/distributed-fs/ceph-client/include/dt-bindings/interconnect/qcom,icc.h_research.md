# sources/distributed-fs/ceph-client/include/dt-bindings/interconnect/qcom,icc.h

## Purpose
defines shared Qualcomm interconnect helper constants used by multiple SoC-specific interconnect bindings.

## Important APIs, Types, and Functions
The exported API is 9 `#define` constants. Representative symbols are `QCOM_ICC_BUCKET_AMC`, `QCOM_ICC_BUCKET_WAKE`, `QCOM_ICC_BUCKET_SLEEP`, `QCOM_ICC_NUM_BUCKETS`, `QCOM_ICC_TAG_AMC`, `QCOM_ICC_TAG_WAKE`, `QCOM_ICC_TAG_SLEEP`, `QCOM_ICC_TAG_ACTIVE_ONLY`, `QCOM_ICC_TAG_ALWAYS`. numeric values span 0..3 across 4 direct numeric defines. Top naming groups: `QCOM_ICC` (9).

## Control Flow
The header contains no executable flow. Devicetree interconnect specifiers reference these IDs; the interconnect framework passes them to the provider, which maps each ID to an internal node and aggregates bandwidth votes at runtime.

## State, Persistence, and Dependencies
The header stores no mutable state. The persistent contract is the stable ID-to-node mapping encoded in DTBs and mirrored by provider-driver topology tables. It is included by Qualcomm interconnect DTS files or binding users that need shared tag/bus identifiers, and is interpreted by the qcom interconnect framework/provider drivers.

## Integration Points
Primary integration points are Devicetree source files that include this header, binding schemas that document the allowed cells/properties, and the platform driver or subsystem core that consumes the numeric value after OF parsing.

## Risks
The main risks are numeric mismatch with provider arrays, duplicate or skipped IDs not handled by the driver, and renumbering nodes after DTBs ship. Those failures can silently under-vote or over-vote NoC bandwidth and break devices under load.

## Test Signals
Use dtbs_check, compile all SoC DTS users, compare max exported IDs against provider table sizes, scan for duplicates, and run device stress tests that exercise interconnect bandwidth votes for major masters/slaves.
