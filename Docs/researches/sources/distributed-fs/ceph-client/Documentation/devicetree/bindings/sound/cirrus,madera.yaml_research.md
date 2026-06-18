<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/cirrus,madera.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/cirrus,madera.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/cirrus,madera.yaml` defines the audio codec or amplifier binding titled `Cirrus Logic Madera class audio CODECs`. This describes audio configuration bindings for these codecs. It constrains source DTS and compiled DTB hardware descriptions before Linux drivers consume the node.

## Important APIs, Types, and Functions
The API surface is the devicetree ABI rather than callable code. This is a reusable schema fragment, so its exported API is the properties it contributes to including bindings. Top-level properties are `#sound-dai-cells`, `cirrus,inmode`, `cirrus,out-mono`, `cirrus,dmic-ref`, `cirrus,max-channels-clocked`, `cirrus,pdm-fmt`, `cirrus,pdm-mute`. Required top-level properties are none declared. Nested or reusable constraints include composition/conditionals: `allOf`; referenced schemas: `/schemas/types.yaml#/definitions/uint32-array`, `dai-common.yaml#`; notable enum/const values: `1`. The highest-risk contract area is compatible strings, bus address, reset/shutdown GPIOs, supplies, clocks, interrupts, DAI cells, widgets/routes, and chip-specific tuning properties.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this file plus `$ref` targets, and enforces required properties, array cardinality, constants, enums, and `allOf`. `dtbs_check` then matches compiled DTS nodes by `compatible`, `$nodename`, or parent-schema inclusion, descends into pattern-matched children, and applies `additionalProperties` or `unevaluatedProperties` closure. Runtime flow begins only after the DTB is loaded: Linux bus, SoC, ASoC, MFD, syscon, or firmware drivers bind from compatible strings and acquire the resources described here.

## State and Persistence Behavior
The YAML itself stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: compatible strings, property names, phandle names, register tuple ordering, child-node names, and examples become contracts in source DTS files and compiled DTBs. Runtime state is created by the matched kernel drivers after probe, including regmap cache, DAPM power state, bias levels, PLL/clock configuration, jack/interrupt state, and audio stream parameters owned by ASoC drivers.

## Dependencies and Integration Points
Maintainers listed: patches@opensource.cirrus.com. Schema dependencies include `/schemas/types.yaml#/definitions/uint32-array`, `dai-common.yaml#`. Integration points include ASoC codec/component drivers, I2C/SPI/platform bus probing, DAPM graph construction, regulators, clocks, GPIO controls, and machine-driver links. The file also integrates with Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and source DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to compatible strings, bus address, reset/shutdown GPIOs, supplies, clocks, interrupts, DAI cells, widgets/routes, and chip-specific tuning properties, drift between documented compatible strings and driver match tables, incorrect resource ordering, phandle names, or cell counts that block probe or misconfigure hardware, variant-specific conditional branches accepting one SoC/chip while rejecting another, permissive extra properties that can hide spelling mistakes, lack of embedded examples, leaving coverage dependent on in-tree DTS users. This schema permits additional top-level properties. Regressions usually show up as schema-check failures, boot-time probe failures, missing audio/SoC child devices, bad firmware/resource allocation, broken suspend/resume, or silent routing/clocking errors in board audio paths.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/sound/cirrus,madera.yaml` for the targeted schema and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/sound/cirrus,madera.yaml` against boards that instantiate it. There are no embedded examples, so real DTS users and schema-only checks are the main coverage. Cross-check compatible strings against driver `of_match_table` entries and inspect DTS users for register tuple counts, interrupt names, clocks/resets, supplies, DMA channels, graph endpoints, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/cirrus,madera.yaml -->
