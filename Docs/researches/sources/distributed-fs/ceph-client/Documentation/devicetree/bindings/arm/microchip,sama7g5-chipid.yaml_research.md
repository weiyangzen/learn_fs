<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/microchip,sama7g5-chipid.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/microchip,sama7g5-chipid.yaml

## Purpose
This binding describes Atmel/Microchip Chip ID register blocks used to read SoC identification and revision information.

## Important APIs, Types, And Functions
It accepts `atmel,sama5d2-chipid`, `microchip,sama7d65-chipid`, or `microchip,sama7g5-chipid`, and requires a single `reg` range.

## Control Flow
Validation is a strict compatible-plus-reg check with no unevaluated properties allowed.

## State And Persistence
The node describes read-only or mostly read-only chip identification registers. Runtime state is limited to driver reads of the register contents.

## Dependencies And Integration Points
It integrates with SoC identification code and any platform logic using chip revision data.

## Risks
The title mentions RAMC SDRAM/DDR controller while the description and compatible strings describe Chip ID; that mismatch can confuse maintainers. Incorrect `reg` size can hide revision fields.

## Test Signals
`dt_binding_check` validates schema shape; boot logs or sysfs/debug output showing correct SoC ID validate runtime reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/microchip,sama7g5-chipid.yaml -->
