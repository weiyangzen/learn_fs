<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/marvell/armada-37xx.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/marvell/armada-37xx.yaml

## Purpose
This schema validates root compatibles for Marvell Armada 37xx boards, especially Armada 3720/3710 devices and Globalscale Espressobin variants.

## Important APIs, Types, And Functions
The root `compatible` is one of several ordered chains. Common board strings such as `cznic,turris-mox`, `glinet,gl-mv1000`, `globalscale,espressobin`, and `methode,edpu` fall back to `marvell,armada3720`, `marvell,armada3710`; Espressobin subvariants include extra intermediate board fallbacks.

## Control Flow
Validation selects one `oneOf` branch and enforces every list item in order. The root node name must be `/`.

## State And Persistence
The binding stores board/SoC identity only. Platform-specific state is represented by other nodes.

## Dependencies And Integration Points
It integrates with Armada 37xx DTS files, machine matching, and SoC drivers keyed by the fallback compatibles.

## Risks
Subvariant chains are easy to misorder, especially Espressobin V7 and eMMC/Ultra models. Missing the generic Armada fallback can prevent common drivers from matching.

## Test Signals
`dtbs_check` catches incompatible root strings. Boot logs showing correct Armada 37xx platform probing provide runtime confirmation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/marvell/armada-37xx.yaml -->
