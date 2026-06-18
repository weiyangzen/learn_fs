<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/socionext/milbeaut.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/socionext/milbeaut.yaml

## Purpose
This root platform binding identifies Socionext Milbeaut M10V evaluation boards.

## Important APIs, Types, And Functions
The compatible list is `socionext,milbeaut-m10v-evb`, `socionext,sc2000a`.

## Control Flow
Validation is a single ordered compatible check with other root properties allowed.

## State And Persistence
The schema stores immutable platform identity only.

## Dependencies And Integration Points
It integrates with Milbeaut DTS files and platform matching for the SC2000A SoC.

## Risks
The binding covers one board chain; new boards or SoC variants need explicit updates.

## Test Signals
`dtbs_check` validates root compatible shape; boot confirms platform match.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/socionext/milbeaut.yaml -->
