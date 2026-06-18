<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/microchip,sparx5.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/microchip,sparx5.yaml

## Purpose
This root platform schema describes Microchip Sparx5 ARMv8 TSN-capable Ethernet switch boards.

## Important APIs, Types, And Functions
The root compatible must identify one of `microchip,sparx5-pcb125`, `pcb134`, or `pcb135` followed by `microchip,sparx5`. The root must also contain an `axi@600000000` simple-bus child.

## Control Flow
Validation requires both `compatible` and the fixed-address AXI bus child. The child object requires `compatible = "simple-bus"` while other root properties are allowed.

## State And Persistence
The binding records immutable board identity and the top-level AXI bus location. Runtime state belongs to switch, bus, and peripheral drivers.

## Dependencies And Integration Points
It integrates with Sparx5 board DTS files and the SoC bus/peripheral layout rooted at `axi@600000000`.

## Risks
The mandatory fixed AXI child is stricter than most root schemas; missing it invalidates the platform even if the root compatible is correct.

## Test Signals
`dtbs_check` validates root and AXI child structure; switch subsystem probe validates runtime integration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/microchip,sparx5.yaml -->
