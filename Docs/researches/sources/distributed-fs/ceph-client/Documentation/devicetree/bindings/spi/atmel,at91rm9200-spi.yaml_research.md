<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/spi/atmel,at91rm9200-spi.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/spi/atmel,at91rm9200-spi.yaml

## Purpose
Devicetree binding schema for Atmel SPI device in the Linux SPI subsystem. It documents and validates nodes matched by `atmel,at91rm9200-spi`, `microchip,lan9691-spi`, `microchip,sam9x60-spi`, `microchip,sam9x7-spi`, `microchip,sama7d65-spi`.

## Important APIs/types/functions
- Schema property keys observed: `compatible`, `reg`, `interrupts`, `clock-names`, `clocks`, `dmas`, `dma-names`, `atmel,fifo-size`.
- Reusable local definitions: none declared.
- Pattern properties/child-node shapes: none declared.
- External schema APIs: `spi-controller.yaml#`, `/schemas/types.yaml#/definitions/uint32`.

## Control flow
The schema control flow is declarative: validation first composes 1 `allOf` block(s); then enforces required keys `compatible`, `reg`, `interrupts`, `clock-names`, `clocks`; conditional branches include 1 `oneOf`; 1 example block(s) exercise the expected DTS shape.

## State and persistence behavior
The file has no executable runtime state; its persistent effect is the validated DT source/DTB contract. Important persisted properties for this binding are `compatible`, `reg`, `interrupts`, `clock-names`, `clocks`, `dmas`, `dma-names`. Kernel state is created later when OF matching instantiates the corresponding platform, codec, controller, or bus device. Schema strictness controls which properties survive review and `dtbs_check`, but it does not store data outside the devicetree.

## Dependencies and integration points
Integrates with the Linux SPI core and `spi-controller.yaml` or peripheral-property schemas when referenced; child nodes normally bind through chip-select `reg` values and common SPI timing/mode properties. Referenced schemas include `spi-controller.yaml#`, `/schemas/types.yaml#/definitions/uint32`. Maintainer metadata routes binding review to Tudor Ambarus <tudor.ambarus@linaro.org>.

## Risks and edge cases
missing required properties (`compatible`, `reg`, `interrupts`, `clock-names`, `clocks`) will make example or board DTs fail validation and can prevent driver probe; conditional compatible/property branches must stay aligned with driver match tables and SoC-specific resource layouts; strict property filtering can reject board-specific extensions unless they are explicitly modeled or inherited through refs; clock/reset count or naming drift is a common integration failure for board DTS files.

## Test signals
`make dt_binding_check DT_SCHEMA_FILES=spi/atmel,at91rm9200-spi.yaml` should parse this YAML and validate its examples; `make dtbs_check` on boards using these compatibles should report no missing required properties or unevaluated-property errors; the 1 embedded example block(s) are the direct regression fixtures for compatible strings, resource ordering, and child-node topology.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/spi/atmel,at91rm9200-spi.yaml -->
