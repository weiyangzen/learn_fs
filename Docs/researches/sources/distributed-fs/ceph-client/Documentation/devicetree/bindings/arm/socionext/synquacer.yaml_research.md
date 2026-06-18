<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/socionext/synquacer.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/socionext/synquacer.yaml

## Purpose
This root platform binding identifies Socionext SynQuacer developer boxes.

## Important APIs, Types, And Functions
It validates `socionext,developer-box`, `socionext,synquacer`.

## Control Flow
The schema enforces a two-item ordered compatible list and allows other root properties.

## State And Persistence
It records immutable board and SoC-family identity only.

## Dependencies And Integration Points
It integrates with SynQuacer DTS files and platform matching.

## Risks
Derivative boards need explicit compatible additions. Missing the generic fallback can break shared SynQuacer support.

## Test Signals
`dtbs_check` validates root compatibles; boot and platform driver probing confirm runtime behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/socionext/synquacer.yaml -->
