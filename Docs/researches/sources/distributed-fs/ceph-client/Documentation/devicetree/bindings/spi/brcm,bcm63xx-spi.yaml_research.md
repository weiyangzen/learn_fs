<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/spi/brcm,bcm63xx-spi.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/spi/brcm,bcm63xx-spi.yaml

## Purpose
Devicetree binding schema for Broadcom BCM6348/BCM6358 SPI controller in the Linux SPI subsystem. It documents and validates nodes matched by `brcm,bcm6368-spi`, `brcm,bcm6362-spi`, `brcm,bcm63268-spi`, `brcm,bcm6358-spi`, `brcm,bcm6348-spi`. The schema description narrows this to: Broadcom "Low Speed" SPI controller found in many older MIPS based Broadband SoCs. This controller has a limitation that can not keep the chip select line active between the SPI transfers within the same SPI message. This can terminate the transaction to some SPI devices prematurely. The issue can be worked around by the controller's prepend mode.

## Important APIs/types/functions
- Schema property keys observed: `compatible`, `reg`, `clocks`, `clock-names`, `interrupts`.
- Reusable local definitions: none declared.
- Pattern properties/child-node shapes: none declared.
- External schema APIs: `spi-controller.yaml#`.

## Control flow
The schema control flow is declarative: validation first composes 1 `allOf` block(s); then enforces required keys `compatible`, `reg`, `clocks`, `clock-names`, `interrupts`; conditional branches include 1 `oneOf`; 1 example block(s) exercise the expected DTS shape.

## State and persistence behavior
The file has no executable runtime state; its persistent effect is the validated DT source/DTB contract. Important persisted properties for this binding are `compatible`, `reg`, `clocks`, `clock-names`, `interrupts`. Kernel state is created later when OF matching instantiates the corresponding platform, codec, controller, or bus device. Schema strictness controls which properties survive review and `dtbs_check`, but it does not store data outside the devicetree.

## Dependencies and integration points
Integrates with the Linux SPI core and `spi-controller.yaml` or peripheral-property schemas when referenced; child nodes normally bind through chip-select `reg` values and common SPI timing/mode properties. Referenced schemas include `spi-controller.yaml#`. Maintainer metadata routes binding review to Jonas Gorski <jonas.gorski@gmail.com>.

## Risks and edge cases
missing required properties (`compatible`, `reg`, `clocks`, `clock-names`, `interrupts`) will make example or board DTs fail validation and can prevent driver probe; conditional compatible/property branches must stay aligned with driver match tables and SoC-specific resource layouts; strict property filtering can reject board-specific extensions unless they are explicitly modeled or inherited through refs; clock/reset count or naming drift is a common integration failure for board DTS files.

## Test signals
`make dt_binding_check DT_SCHEMA_FILES=spi/brcm,bcm63xx-spi.yaml` should parse this YAML and validate its examples; `make dtbs_check` on boards using these compatibles should report no missing required properties or unevaluated-property errors; the 1 embedded example block(s) are the direct regression fixtures for compatible strings, resource ordering, and child-node topology.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/spi/brcm,bcm63xx-spi.yaml -->
