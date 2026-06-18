<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/spi/brcm,bcm63xx-hsspi.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/spi/brcm,bcm63xx-hsspi.yaml

## Purpose
Devicetree binding schema for Broadcom Broadband SoC High Speed SPI controller in the Linux SPI subsystem. It documents and validates nodes matched by `brcm,bcm6328-hsspi`, `brcm,bcm47622-hsspi`, `brcm,bcm4908-hsspi`, `brcm,bcm63138-hsspi`, `brcm,bcm63146-hsspi`, `brcm,bcm63148-hsspi`, and 12 more compatible strings. The schema description narrows this to: Broadcom Broadband SoC supports High Speed SPI master controller since the early MIPS based chips such as BCM6328 and BCM63268. This initial rev 1.0 controller was carried over to recent ARM based chips, such as BCM63138, BCM4908 and BCM6858. The old MIPS based chip should continue to use the brcm,bcm6328-hsspi compatible string. The recent ARM based chip is required to use the brcm,bcmbca-hsspi-v1.0 as part of it...

## Important APIs/types/functions
- Schema property keys observed: `compatible`, `reg`, `reg-names`, `clocks`, `clock-names`, `interrupts`.
- Reusable local definitions: none declared.
- Pattern properties/child-node shapes: none declared.
- External schema APIs: `spi-controller.yaml#`.

## Control flow
The schema control flow is declarative: validation first composes 2 `allOf` block(s); then enforces required keys `compatible`, `reg`, `clocks`, `clock-names`, `interrupts`; conditional branches include 1 `oneOf`, 1 `if`, 1 `then`, 1 `else`; 1 example block(s) exercise the expected DTS shape.

## State and persistence behavior
The file has no executable runtime state; its persistent effect is the validated DT source/DTB contract. Important persisted properties for this binding are `compatible`, `reg`, `reg-names`, `clocks`, `clock-names`, `interrupts`. Kernel state is created later when OF matching instantiates the corresponding platform, codec, controller, or bus device. Schema strictness controls which properties survive review and `dtbs_check`, but it does not store data outside the devicetree.

## Dependencies and integration points
Integrates with the Linux SPI core and `spi-controller.yaml` or peripheral-property schemas when referenced; child nodes normally bind through chip-select `reg` values and common SPI timing/mode properties. Referenced schemas include `spi-controller.yaml#`. Maintainer metadata routes binding review to William Zhang <william.zhang@broadcom.com>, Kursad Oney <kursad.oney@broadcom.com>, Jonas Gorski <jonas.gorski@gmail.com>.

## Risks and edge cases
missing required properties (`compatible`, `reg`, `clocks`, `clock-names`, `interrupts`) will make example or board DTs fail validation and can prevent driver probe; conditional compatible/property branches must stay aligned with driver match tables and SoC-specific resource layouts; strict property filtering can reject board-specific extensions unless they are explicitly modeled or inherited through refs; clock/reset count or naming drift is a common integration failure for board DTS files.

## Test signals
`make dt_binding_check DT_SCHEMA_FILES=spi/brcm,bcm63xx-hsspi.yaml` should parse this YAML and validate its examples; `make dtbs_check` on boards using these compatibles should report no missing required properties or unevaluated-property errors; the 1 embedded example block(s) are the direct regression fixtures for compatible strings, resource ordering, and child-node topology.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/spi/brcm,bcm63xx-hsspi.yaml -->
