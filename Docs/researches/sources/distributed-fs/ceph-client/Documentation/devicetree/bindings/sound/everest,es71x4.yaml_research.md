<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/everest,es71x4.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/everest,es71x4.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/everest,es71x4.yaml` defines the audio codec or amplifier binding titled `Everest ES7134/7144/7154 2 channels I2S analog to digital converter`. It constrains source DTS and compiled DTB hardware descriptions through compatible strings, required resources, child-node topology, and shared schema references before Linux drivers consume the node.

## Important APIs, Types, and Functions
The API surface is the devicetree ABI rather than callable code. `compatible` uses an `enum` of supported tokens with 3 tokens: `everest,es7134`, `everest,es7144`, `everest,es7154`. Top-level properties are `compatible`, `VDD-supply`, `PVDD-supply`, `#sound-dai-cells`. Required top-level properties are `compatible`, `VDD-supply`. Nested or reusable constraints include composition/conditionals: `allOf`; referenced schemas: `dai-common.yaml#`; notable enum/const values: `0`. The highest-risk contract area is compatible strings, bus address, reset/shutdown GPIOs, supplies, clocks, interrupts, DAI cells, widgets/routes, and chip-specific tuning properties.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this file plus `$ref` targets, and enforces required properties, array cardinality, constants, enums, and `allOf`. `dtbs_check` then matches compiled DTS nodes by `compatible`, `$nodename`, or parent-schema inclusion, descends into pattern-matched children, and applies `additionalProperties` or `unevaluatedProperties` closure. Runtime flow begins only after the DTB is loaded: Linux bus, SoC, ASoC, MFD, syscon, or firmware drivers bind from compatible strings and acquire the resources described here.

## State and Persistence Behavior
The YAML itself stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: compatible strings, property names, phandle names, register tuple ordering, child-node names, and examples become contracts in source DTS files and compiled DTBs. Runtime state is created by the matched kernel drivers after probe, including regmap cache, DAPM power state, bias levels, PLL/clock configuration, jack/interrupt state, and audio stream parameters owned by ASoC drivers.

## Dependencies and Integration Points
Maintainers listed: Neil Armstrong <neil.armstrong@linaro.org>. Schema dependencies include `dai-common.yaml#`. Integration points include ASoC codec/component drivers, I2C/SPI/platform bus probing, DAPM graph construction, regulators, clocks, GPIO controls, and machine-driver links. The file also integrates with Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and source DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to compatible strings, bus address, reset/shutdown GPIOs, supplies, clocks, interrupts, DAI cells, widgets/routes, and chip-specific tuning properties, drift between documented compatible strings and driver match tables, incorrect resource ordering, phandle names, or cell counts that block probe or misconfigure hardware, variant-specific conditional branches accepting one SoC/chip while rejecting another. This schema closes composed schemas with `unevaluatedProperties: false`. Regressions usually show up as schema-check failures, boot-time probe failures, missing audio/SoC child devices, bad firmware/resource allocation, broken suspend/resume, or silent routing/clocking errors in board audio paths.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/sound/everest,es71x4.yaml` for the targeted schema and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/sound/everest,es71x4.yaml` against boards that instantiate it. The schema has 1 embedded example; keep those examples valid under targeted binding checks. Cross-check compatible strings against driver `of_match_table` entries and inspect DTS users for register tuple counts, interrupt names, clocks/resets, supplies, DMA channels, graph endpoints, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/everest,es71x4.yaml -->
