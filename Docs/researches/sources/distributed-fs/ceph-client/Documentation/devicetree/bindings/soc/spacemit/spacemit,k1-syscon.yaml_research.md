<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/spacemit/spacemit,k1-syscon.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/spacemit/spacemit,k1-syscon.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/spacemit/spacemit,k1-syscon.yaml` defines the SoC system-controller/syscon binding titled `SpacemiT K1/K3 SoC System Controller`. System controllers found on SpacemiT K1/K3 SoC, which are capable of clock, reset and power-management functions. It constrains source DTS and compiled DTB hardware descriptions before Linux drivers consume the node.

## Important APIs, Types, and Functions
The API surface is the devicetree ABI rather than callable code. `compatible` uses an `enum` of supported tokens with 10 tokens: `spacemit,k1-syscon-apbc`, `spacemit,k1-syscon-apmu`, `spacemit,k1-syscon-mpmu`, `spacemit,k1-syscon-rcpu`, `spacemit,k1-syscon-rcpu2`, `spacemit,k1-syscon-apbc2`, `spacemit,k3-syscon-apbc`, `spacemit,k3-syscon-apmu`, `spacemit,k3-syscon-dciu`, `spacemit,k3-syscon-mpmu`. Top-level properties are `compatible`, `reg`, `clocks`, `clock-names`, `#clock-cells`, `#power-domain-cells`, `#reset-cells`. Required top-level properties are `compatible`, `reg`, `#reset-cells`. Nested or reusable constraints include composition/conditionals: `allOf`; notable enum/const values: `osc`, `vctcxo_1m`, `vctcxo_3m`, `vctcxo_24m`, `1`. The highest-risk contract area is compatible fallback order, register window shape, syscon phandles, child-node schemas, and provider cell counts.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this file plus `$ref` targets, and enforces required properties, array cardinality, constants, enums, and `allOf`. `dtbs_check` then matches compiled DTS nodes by `compatible`, `$nodename`, or parent-schema inclusion, descends into pattern-matched children, and applies `additionalProperties` or `unevaluatedProperties` closure. Runtime flow begins only after the DTB is loaded: Linux bus, SoC, ASoC, MFD, syscon, or firmware drivers bind from compatible strings and acquire the resources described here.

## State and Persistence Behavior
The YAML itself stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: compatible strings, property names, phandle names, register tuple ordering, child-node names, and examples become contracts in source DTS files and compiled DTBs. Runtime state is created by the matched kernel drivers after probe, including regmap lifetime, child-device population, SoC control register access, and provider state owned by downstream clock/reset/power-domain or firmware drivers.

## Dependencies and Integration Points
Maintainers listed: Haylen Chu <heylenay@4d2.org>. Schema dependencies include dt-schema core/meta schemas only. Integration points include Linux platform probing, `syscon`/regmap consumers, MFD child population, reset/clock/power-domain providers, and SoC-specific DTS nodes. The file also integrates with Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and source DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to compatible fallback order, register window shape, syscon phandles, child-node schemas, and provider cell counts, drift between documented compatible strings and driver match tables, incorrect resource ordering, phandle names, or cell counts that block probe or misconfigure hardware, variant-specific conditional branches accepting one SoC/chip while rejecting another. This schema rejects unknown top-level properties with `additionalProperties: false`. Regressions usually show up as schema-check failures, boot-time probe failures, missing audio/SoC child devices, bad firmware/resource allocation, broken suspend/resume, or silent routing/clocking errors in board audio paths.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/soc/spacemit/spacemit,k1-syscon.yaml` for the targeted schema and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/soc/spacemit/spacemit,k1-syscon.yaml` against boards that instantiate it. The schema has 1 embedded example; keep those examples valid under targeted binding checks. Cross-check compatible strings against driver `of_match_table` entries and inspect DTS users for register tuple counts, interrupt names, clocks/resets, supplies, DMA channels, graph endpoints, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/spacemit/spacemit,k1-syscon.yaml -->
