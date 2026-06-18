<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/nuvoton/nuvoton,ma35d1.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/nuvoton/nuvoton,ma35d1.yaml

## Purpose
This root platform schema identifies ARMv8 Nuvoton MA35D1 boards.

## Important APIs, Types, And Functions
It validates board strings `nuvoton,ma35d1-iot` and `nuvoton,ma35d1-som` followed by `nuvoton,ma35d1`.

## Control Flow
The schema fixes the root node name to `/` and uses a single `oneOf` branch for MA35D1 boards.

## State And Persistence
It records immutable root platform identity only.

## Dependencies And Integration Points
It integrates with MA35D1 DTS files and SoC driver matching.

## Risks
New MA35 variants require explicit schema additions. Missing the generic fallback can break common MA35D1 support.

## Test Signals
`dtbs_check` validates root compatibles; successful MA35D1 boot confirms runtime matching.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/nuvoton/nuvoton,ma35d1.yaml -->
