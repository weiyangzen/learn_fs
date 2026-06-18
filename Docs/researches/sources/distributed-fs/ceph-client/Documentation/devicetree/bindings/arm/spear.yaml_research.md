<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/spear.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/spear.yaml

## Purpose
This root platform schema catalogs ST SPEAr SoC evaluation boards.

## Important APIs, Types, And Functions
It validates board-to-SoC chains for SPEAr1310 EVB, SPEAr1340 EVB, SPEAr300 EVB, SPEAr310 EVB, SPEAr320 EVB, and SPEAr600 EVB.

## Control Flow
Validation uses a `oneOf` list of exact compatible chains and allows other root properties.

## State And Persistence
It records immutable platform identity only.

## Dependencies And Integration Points
It integrates with SPEAr DTS files and platform matching.

## Risks
The schema is narrow and board-specific. New boards need explicit additions and correct SoC fallback strings.

## Test Signals
`dtbs_check` validates compatible chains; platform boot confirms runtime matching.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/spear.yaml -->
