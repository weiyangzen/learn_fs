<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/sti.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/sti.yaml

## Purpose
This schema catalogs STMicroelectronics STi set-top-box platform root compatibles.

## Important APIs, Types, And Functions
It validates compatible chains for STiH407 B2120, STiH410 B2120, and STiH418 B2199 boards, each followed by its SoC fallback.

## Control Flow
`oneOf` selects one ordered board-to-SoC branch and allows normal root properties.

## State And Persistence
The schema records immutable platform identity only.

## Dependencies And Integration Points
It integrates with STi DTS files and platform matching.

## Risks
Board names are similar across SoC generations; using the wrong fallback can break SoC-specific support.

## Test Signals
`dtbs_check` validates root compatible lists; boot-time SoC/platform match confirms integration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/sti.yaml -->
