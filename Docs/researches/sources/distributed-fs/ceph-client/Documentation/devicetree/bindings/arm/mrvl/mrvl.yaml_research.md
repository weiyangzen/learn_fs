<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/mrvl/mrvl.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/mrvl/mrvl.yaml

## Purpose
This root platform schema catalogs Marvell/MRVL PXA and MMP-family boards.

## Important APIs, Types, And Functions
It validates root compatible chains for PXA168 Aspenite, PXA910 DKB, MMP2 boards including OLPC XO-1.75, MMP3 Dell Wyse Ariel, and PXA1908 Samsung Core Prime LTE.

## Control Flow
The schema fixes `$nodename` to `/` and selects one `oneOf` branch for the board/SoC fallback list.

## State And Persistence
The binding records immutable board/SoC identity only.

## Dependencies And Integration Points
It integrates with PXA/MMP DTS files and platform/SoC matching code.

## Risks
Vendor prefix drift is visible: both `mrvl` and `marvell` compatibles are present for different generations. New entries should preserve existing naming conventions.

## Test Signals
`dtbs_check` validates compatible chains; platform boot confirms correct SoC matching.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/mrvl/mrvl.yaml -->
