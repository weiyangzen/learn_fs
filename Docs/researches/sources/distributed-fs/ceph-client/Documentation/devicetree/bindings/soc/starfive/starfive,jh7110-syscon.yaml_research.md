<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/starfive/starfive,jh7110-syscon.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/starfive/starfive,jh7110-syscon.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/starfive/starfive,jh7110-syscon.yaml` defines the SoC system-controller/syscon binding titled `StarFive JH7110 SoC system controller`. The StarFive JH7110 SoC system controller provides register information such as offset, mask and shift to configure related modules such as MMC and PCIe. It constrains source DTS and compiled DTB hardware descriptions before Linux drivers consume the node.

## Important APIs, Types, and Functions
The API surface is the devicetree ABI rather than callable code. `compatible` uses `oneOf` with 2 branches with 5 tokens: `starfive,jh7110-sys-syscon`, `syscon`, `simple-mfd`, `starfive,jh7110-aon-syscon`, `starfive,jh7110-stg-syscon`. Top-level properties are `compatible`, `reg`, `clock-controller`, `#power-domain-cells`. Required top-level properties are `compatible`, `reg`. Nested or reusable constraints include composition/conditionals: `allOf`; referenced schemas: `/schemas/clock/starfive,jh7110-pll.yaml#`; notable enum/const values: `1`. The highest-risk contract area is compatible fallback order, register window shape, syscon phandles, child-node schemas, and provider cell counts.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this file plus `$ref` targets, and enforces required properties, array cardinality, constants, enums, and `allOf`. `dtbs_check` then matches compiled DTS nodes by `compatible`, `$nodename`, or parent-schema inclusion, descends into pattern-matched children, and applies `additionalProperties` or `unevaluatedProperties` closure. Runtime flow begins only after the DTB is loaded: Linux bus, SoC, ASoC, MFD, syscon, or firmware drivers bind from compatible strings and acquire the resources described here.

## State and Persistence Behavior
The YAML itself stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: compatible strings, property names, phandle names, register tuple ordering, child-node names, and examples become contracts in source DTS files and compiled DTBs. Runtime state is created by the matched kernel drivers after probe, including regmap lifetime, child-device population, SoC control register access, and provider state owned by downstream clock/reset/power-domain or firmware drivers.

## Dependencies and Integration Points
Maintainers listed: William Qiu <william.qiu@starfivetech.com>. Schema dependencies include `/schemas/clock/starfive,jh7110-pll.yaml#`. Integration points include Linux platform probing, `syscon`/regmap consumers, MFD child population, reset/clock/power-domain providers, and SoC-specific DTS nodes. The file also integrates with Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and source DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to compatible fallback order, register window shape, syscon phandles, child-node schemas, and provider cell counts, drift between documented compatible strings and driver match tables, incorrect resource ordering, phandle names, or cell counts that block probe or misconfigure hardware, variant-specific conditional branches accepting one SoC/chip while rejecting another. This schema rejects unknown top-level properties with `additionalProperties: false`. Regressions usually show up as schema-check failures, boot-time probe failures, missing audio/SoC child devices, bad firmware/resource allocation, broken suspend/resume, or silent routing/clocking errors in board audio paths.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/soc/starfive/starfive,jh7110-syscon.yaml` for the targeted schema and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/soc/starfive/starfive,jh7110-syscon.yaml` against boards that instantiate it. The schema has 1 embedded example; keep those examples valid under targeted binding checks. Cross-check compatible strings against driver `of_match_table` entries and inspect DTS users for register tuple counts, interrupt names, clocks/resets, supplies, DMA channels, graph endpoints, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/starfive/starfive,jh7110-syscon.yaml -->
