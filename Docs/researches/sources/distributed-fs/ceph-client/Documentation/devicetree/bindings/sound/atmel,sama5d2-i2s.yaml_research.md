<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/atmel,sama5d2-i2s.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/atmel,sama5d2-i2s.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/atmel,sama5d2-i2s.yaml` defines the audio controller or sound-card binding titled `Atmel I2S controller`. Atmel I2S (Inter-IC Sound Controller) bus is the standard interface for connecting audio devices, such as audio codecs. It constrains source DTS and compiled DTB hardware descriptions before Linux drivers consume the node.

## Important APIs, Types, and Functions
The API surface is the devicetree ABI rather than callable code. `compatible` uses a single `const` token with 1 token: `atmel,sama5d2-i2s`. Top-level properties are `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `dmas`, `dma-names`. Required top-level properties are `compatible`, `reg`, `interrupts`, `dmas`, `dma-names`, `clocks`, `clock-names`. Nested or reusable constraints include notable enum/const values: `pclk`, `gclk`, `muxclk`, `tx`, `rx`. The highest-risk contract area is register and interrupt resources, clocks/resets, DMA channels, sound-dai cells, graph ports/endpoints, routing, and SoC-specific compatible strings.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this file plus `$ref` targets, and enforces required properties, array cardinality, constants, enums, and no top-level conditionals. `dtbs_check` then matches compiled DTS nodes by `compatible`, `$nodename`, or parent-schema inclusion, descends into pattern-matched children, and applies `additionalProperties` or `unevaluatedProperties` closure. Runtime flow begins only after the DTB is loaded: Linux bus, SoC, ASoC, MFD, syscon, or firmware drivers bind from compatible strings and acquire the resources described here.

## State and Persistence Behavior
The YAML itself stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: compatible strings, property names, phandle names, register tuple ordering, child-node names, and examples become contracts in source DTS files and compiled DTBs. Runtime state is created by the matched kernel drivers after probe, including DAI/controller probe state, DMA stream state, clocking, reset state, and sound-card topology owned by ASoC runtime drivers.

## Dependencies and Integration Points
Maintainers listed: Nicolas Ferre <nicolas.ferre@microchip.com>, Alexandre Belloni <alexandre.belloni@bootlin.com>, Claudiu Beznea <claudiu.beznea@microchip.com>. Schema dependencies include dt-schema core/meta schemas only. Integration points include ASoC CPU DAI drivers, platform DMA engines, machine drivers, graph/simple-card parsing, clocks/resets, pinctrl, and board DTS sound links. The file also integrates with Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and source DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to register and interrupt resources, clocks/resets, DMA channels, sound-dai cells, graph ports/endpoints, routing, and SoC-specific compatible strings, drift between documented compatible strings and driver match tables, incorrect resource ordering, phandle names, or cell counts that block probe or misconfigure hardware. This schema rejects unknown top-level properties with `additionalProperties: false`. Regressions usually show up as schema-check failures, boot-time probe failures, missing audio/SoC child devices, bad firmware/resource allocation, broken suspend/resume, or silent routing/clocking errors in board audio paths.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/sound/atmel,sama5d2-i2s.yaml` for the targeted schema and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/sound/atmel,sama5d2-i2s.yaml` against boards that instantiate it. The schema has 1 embedded example; keep those examples valid under targeted binding checks. Cross-check compatible strings against driver `of_match_table` entries and inspect DTS users for register tuple counts, interrupt names, clocks/resets, supplies, DMA channels, graph endpoints, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/atmel,sama5d2-i2s.yaml -->
