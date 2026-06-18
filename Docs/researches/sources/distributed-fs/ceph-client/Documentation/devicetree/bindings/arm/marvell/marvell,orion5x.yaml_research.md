<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/marvell/marvell,orion5x.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/marvell/marvell,orion5x.yaml

## Purpose
This schema catalogs Marvell Orion5x platform root compatibles for 88F5181 and 88F5182 boards.

## Important APIs, Types, And Functions
It validates board enums followed by `marvell,orion5x-88f5181`, `marvell,orion5x` or by `marvell,orion5x-88f5182`, `marvell,orion5x`.

## Control Flow
`oneOf` selects the SoC branch and enforces the exact board-to-SoC fallback order.

## State And Persistence
Only root identity is represented; mutable device state is outside this schema.

## Dependencies And Integration Points
It integrates with Orion5x DTS files and legacy Marvell platform code.

## Risks
The two SoC variants are close enough that board placement in the wrong enum would select incorrect low-level support.

## Test Signals
`dtbs_check` validates root compatibles. Successful boot and peripheral setup confirm runtime matching.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/marvell/marvell,orion5x.yaml -->
