<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/socionext/uniphier.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/socionext/uniphier.yaml

## Purpose
This schema catalogs Socionext UniPhier platform root compatibles.

## Important APIs, Types, And Functions
It validates compatible chains for LD4, Pro4, SLD8, Pro5, PXs2, LD6b, LD11, LD20, PXs3, NX1, and additional board prefixes such as Buffalo LinkStation and PXs3 reference boards, all falling back to the relevant `socionext,uniphier-*` SoC string.

## Control Flow
`oneOf` selects one SoC or board branch. Some branches are pure SoC strings and others are board-to-SoC chains.

## State And Persistence
It stores immutable platform identity only.

## Dependencies And Integration Points
It integrates with UniPhier DTS files and platform matching.

## Risks
Pure SoC branches validate less board identity. Board-specific additions should keep the SoC fallback to preserve generic driver matching.

## Test Signals
`dtbs_check` validates root compatible lists; boot-time platform and peripheral probing validate runtime integration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/socionext/uniphier.yaml -->
