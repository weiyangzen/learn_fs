<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/marvell/marvell,dove.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/marvell/marvell,dove.yaml

## Purpose
This root schema catalogs Marvell Dove boards such as CuBox, D2Plug/D3Plug, CM-A510, and Dove DB.

## Important APIs, Types, And Functions
Compatible chains either use a board enum followed by `marvell,dove`, or include intermediate board fallbacks such as `solidrun,cubox` or `compulab,cm-a510`.

## Control Flow
Validation chooses one `oneOf` branch and enforces exact ordering from board variant to generic Dove SoC.

## State And Persistence
The schema stores immutable platform identity only.

## Dependencies And Integration Points
It integrates with Marvell Dove DTS files and legacy ARM platform matching.

## Risks
Intermediate fallback boards are important for variants; omitting them can bypass board-specific quirks.

## Test Signals
`dtbs_check` validates root compatible order; boot-time board and SoC driver matching confirms use.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/marvell/marvell,dove.yaml -->
