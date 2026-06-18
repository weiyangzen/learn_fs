<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/marvell/marvell,ac5.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/marvell/marvell,ac5.yaml

## Purpose
This root platform schema identifies Marvell Alleycat5 and Alleycat5X switch reference designs.

## Important APIs, Types, And Functions
It validates `marvell,rd-ac5`, `marvell,ac5` and `marvell,rd-ac5x`, `marvell,ac5x`, `marvell,ac5` compatible chains.

## Control Flow
The schema selects between AC5 and AC5X branches and requires the root node name `/`. Other root properties are allowed.

## State And Persistence
It carries immutable platform identity for switch SoCs; no runtime state is described here.

## Dependencies And Integration Points
It integrates with AC5/AC5X DTS files and switch SoC platform initialization.

## Risks
AC5X must retain the AC5 fallback for shared support. New boards require explicit enum additions.

## Test Signals
`dtbs_check` validates root compatibles; switch platform boot and Ethernet subsystem probing provide runtime signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/marvell/marvell,ac5.yaml -->
