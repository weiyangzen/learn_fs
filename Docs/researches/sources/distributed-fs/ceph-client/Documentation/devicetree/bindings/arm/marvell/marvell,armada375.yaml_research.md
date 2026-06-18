<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/marvell/marvell,armada375.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/marvell/marvell,armada375.yaml

## Purpose
This schema identifies the Marvell Armada 375 development board platform.

## Important APIs, Types, And Functions
The root compatible must be `marvell,a375-db`, `marvell,armada375`.

## Control Flow
Validation is a single ordered `items` check with the root node name fixed to `/`.

## State And Persistence
It records immutable board/SoC identity only.

## Dependencies And Integration Points
It integrates with Armada 375 DTS files and platform matching.

## Risks
The schema covers one board, so variants need new enum entries. Missing the SoC fallback breaks common Armada 375 matching.

## Test Signals
`dtbs_check` validates DTS root nodes; runtime platform selection validates integration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/marvell/marvell,armada375.yaml -->
