<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/nxp/lpc32xx.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/nxp/lpc32xx.yaml

## Purpose
This schema catalogs NXP LPC32xx and LPC43xx platform compatibles.

## Important APIs, Types, And Functions
It allows plain SoC compatibles for LPC3220/3230/3240, board-to-SoC chains for EA/Phytec LPC3250 boards, and LPC43xx development/evaluation boards with LPC4357/LPC4337/LPC4350 fallbacks.

## Control Flow
Validation selects one `oneOf` branch. Some branches are single-string SoC compatibles while others are ordered board fallback chains.

## State And Persistence
The binding records immutable platform identity only.

## Dependencies And Integration Points
It integrates with NXP LPC DTS files and platform matching.

## Risks
Mixing LPC32xx and LPC43xx families in one schema requires care when adding boards. Single-string SoC compatibles offer less board-specific validation than ordered board chains.

## Test Signals
`dtbs_check` validates compatible lists; boot-time platform match confirms runtime behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/nxp/lpc32xx.yaml -->
