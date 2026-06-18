# Research: subset-b-000612

Grouped research for Linux devicetree binding YAML schemas covering SoC support blocks and sound/ASoC hardware under the Ceph client source tree. Each section preserves the source path and marker pair required for deterministic reconciliation into source-tree-aligned per-file documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/socionext/socionext,uniphier-soc-glue.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/socionext/socionext,uniphier-soc-glue.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/socionext/socionext,uniphier-soc-glue.yaml` defines the SoC support binding titled `Socionext UniPhier SoC-glue logic`. SoC-glue logic implemented on Socionext UniPhier SoCs is a collection of miscellaneous function registers handling signals outside system components. It constrains source DTS and compiled DTB hardware descriptions before Linux drivers consume the node.

## Important APIs, Types, and Functions
The API surface is the devicetree ABI rather than callable code. `compatible` uses an ordered compatible/fallback `items` sequence with 11 tokens: `socionext,uniphier-ld4-soc-glue`, `socionext,uniphier-pro4-soc-glue`, `socionext,uniphier-pro5-soc-glue`, `socionext,uniphier-pxs2-soc-glue`, `socionext,uniphier-sld8-soc-glue`, `socionext,uniphier-ld11-soc-glue`, `socionext,uniphier-ld20-soc-glue`, `socionext,uniphier-pxs3-soc-glue`, `socionext,uniphier-nx1-soc-glue`, `simple-mfd`, `syscon`. Top-level properties are `compatible`, `reg`, `pinctrl`, `usb-hub`, `clock-controller`. Required top-level properties are `compatible`, `reg`. Nested or reusable constraints include composition/conditionals: `allOf`; referenced schemas: `/schemas/clock/socionext,uniphier-clock.yaml#`, `/schemas/phy/socionext,uniphier-usb2-phy.yaml#`, `/schemas/pinctrl/socionext,uniphier-pinctrl.yaml#`. The highest-risk contract area is compatible strings, register resources, child-node layout, clock/reset/power-domain hooks, and phandle references.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this file plus `$ref` targets, and enforces required properties, array cardinality, constants, enums, and `allOf`. `dtbs_check` then matches compiled DTS nodes by `compatible`, `$nodename`, or parent-schema inclusion, descends into pattern-matched children, and applies `additionalProperties` or `unevaluatedProperties` closure. Runtime flow begins only after the DTB is loaded: Linux bus, SoC, ASoC, MFD, syscon, or firmware drivers bind from compatible strings and acquire the resources described here.

## State and Persistence Behavior
The YAML itself stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: compatible strings, property names, phandle names, register tuple ordering, child-node names, and examples become contracts in source DTS files and compiled DTBs. Runtime state is created by the matched kernel drivers after probe, including driver probe state, mapped control registers, child-device state, and SoC integration resources.

## Dependencies and Integration Points
Maintainers listed: Kunihiko Hayashi <hayashi.kunihiko@socionext.com>. Schema dependencies include `/schemas/clock/socionext,uniphier-clock.yaml#`, `/schemas/phy/socionext,uniphier-usb2-phy.yaml#`, `/schemas/pinctrl/socionext,uniphier-pinctrl.yaml#`. Integration points include Linux platform probing, syscon/regmap helpers, board-level DTS nodes, and SoC-specific drivers. The file also integrates with Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and source DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to compatible strings, register resources, child-node layout, clock/reset/power-domain hooks, and phandle references, drift between documented compatible strings and driver match tables, incorrect resource ordering, phandle names, or cell counts that block probe or misconfigure hardware, variant-specific conditional branches accepting one SoC/chip while rejecting another, large compatible sets where fallback ordering can drift over hardware generations. This schema rejects unknown top-level properties with `additionalProperties: false`. Regressions usually show up as schema-check failures, boot-time probe failures, missing audio/SoC child devices, bad firmware/resource allocation, broken suspend/resume, or silent routing/clocking errors in board audio paths.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/soc/socionext/socionext,uniphier-soc-glue.yaml` for the targeted schema and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/soc/socionext/socionext,uniphier-soc-glue.yaml` against boards that instantiate it. The schema has 1 embedded example; keep those examples valid under targeted binding checks. Cross-check compatible strings against driver `of_match_table` entries and inspect DTS users for register tuple counts, interrupt names, clocks/resets, supplies, DMA channels, graph endpoints, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/socionext/socionext,uniphier-soc-glue.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/socionext/socionext,uniphier-sysctrl.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/socionext/socionext,uniphier-sysctrl.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/socionext/socionext,uniphier-sysctrl.yaml` defines the SoC system-controller/syscon binding titled `Socionext UniPhier system controller`. System controller implemented on Socionext UniPhier SoCs has multiple functions such as clock control, reset control, internal watchdog timer, thermal management, and so on. It constrains source DTS and compiled DTB hardware descriptions before Linux drivers consume the node.

## Important APIs, Types, and Functions
The API surface is the devicetree ABI rather than callable code. `compatible` uses an ordered compatible/fallback `items` sequence with 11 tokens: `socionext,uniphier-ld4-sysctrl`, `socionext,uniphier-pro4-sysctrl`, `socionext,uniphier-pro5-sysctrl`, `socionext,uniphier-pxs2-sysctrl`, `socionext,uniphier-sld8-sysctrl`, `socionext,uniphier-ld11-sysctrl`, `socionext,uniphier-ld20-sysctrl`, `socionext,uniphier-pxs3-sysctrl`, `socionext,uniphier-nx1-sysctrl`, `simple-mfd`, `syscon`. Top-level properties are `compatible`, `reg`, `clock-controller`, `reset-controller`, `watchdog`, `thermal-sensor`. Required top-level properties are `compatible`, `reg`. Nested or reusable constraints include composition/conditionals: `allOf`; referenced schemas: `/schemas/clock/socionext,uniphier-clock.yaml#`, `/schemas/reset/socionext,uniphier-reset.yaml#`, `/schemas/thermal/socionext,uniphier-thermal.yaml#`, `/schemas/watchdog/socionext,uniphier-wdt.yaml#`. The highest-risk contract area is compatible fallback order, register window shape, syscon phandles, child-node schemas, and provider cell counts.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this file plus `$ref` targets, and enforces required properties, array cardinality, constants, enums, and `allOf`. `dtbs_check` then matches compiled DTS nodes by `compatible`, `$nodename`, or parent-schema inclusion, descends into pattern-matched children, and applies `additionalProperties` or `unevaluatedProperties` closure. Runtime flow begins only after the DTB is loaded: Linux bus, SoC, ASoC, MFD, syscon, or firmware drivers bind from compatible strings and acquire the resources described here.

## State and Persistence Behavior
The YAML itself stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: compatible strings, property names, phandle names, register tuple ordering, child-node names, and examples become contracts in source DTS files and compiled DTBs. Runtime state is created by the matched kernel drivers after probe, including regmap lifetime, child-device population, SoC control register access, and provider state owned by downstream clock/reset/power-domain or firmware drivers.

## Dependencies and Integration Points
Maintainers listed: Kunihiko Hayashi <hayashi.kunihiko@socionext.com>. Schema dependencies include `/schemas/clock/socionext,uniphier-clock.yaml#`, `/schemas/reset/socionext,uniphier-reset.yaml#`, `/schemas/thermal/socionext,uniphier-thermal.yaml#`, `/schemas/watchdog/socionext,uniphier-wdt.yaml#`. Integration points include Linux platform probing, `syscon`/regmap consumers, MFD child population, reset/clock/power-domain providers, and SoC-specific DTS nodes. The file also integrates with Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and source DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to compatible fallback order, register window shape, syscon phandles, child-node schemas, and provider cell counts, drift between documented compatible strings and driver match tables, incorrect resource ordering, phandle names, or cell counts that block probe or misconfigure hardware, variant-specific conditional branches accepting one SoC/chip while rejecting another, large compatible sets where fallback ordering can drift over hardware generations. This schema rejects unknown top-level properties with `additionalProperties: false`. Regressions usually show up as schema-check failures, boot-time probe failures, missing audio/SoC child devices, bad firmware/resource allocation, broken suspend/resume, or silent routing/clocking errors in board audio paths.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/soc/socionext/socionext,uniphier-sysctrl.yaml` for the targeted schema and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/soc/socionext/socionext,uniphier-sysctrl.yaml` against boards that instantiate it. The schema has 1 embedded example; keep those examples valid under targeted binding checks. Cross-check compatible strings against driver `of_match_table` entries and inspect DTS users for register tuple counts, interrupt names, clocks/resets, supplies, DMA channels, graph endpoints, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/socionext/socionext,uniphier-sysctrl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/sophgo/sophgo,cv1800b-top-syscon.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/sophgo/sophgo,cv1800b-top-syscon.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/sophgo/sophgo,cv1800b-top-syscon.yaml` defines the SoC system-controller/syscon binding titled `Sophgo CV18XX/SG200X SoC top system controller`. The Sophgo CV18XX/SG200X SoC top misc system controller provides register access to configure related modules. It constrains source DTS and compiled DTB hardware descriptions before Linux drivers consume the node.

## Important APIs, Types, and Functions
The API surface is the devicetree ABI rather than callable code. `compatible` uses `oneOf` with 1 branch with 3 tokens: `sophgo,cv1800b-top-syscon`, `syscon`, `simple-mfd`. Top-level properties are `compatible`, `reg`, `#address-cells`, `#size-cells`, `ranges`, `dma-router@154`, `phy@48`. Required top-level properties are `compatible`, `reg`, `#address-cells`, `#size-cells`. Nested or reusable constraints include referenced schemas: `/schemas/dma/sophgo,cv1800b-dmamux.yaml#`, `/schemas/phy/sophgo,cv1800b-usb2-phy.yaml#`; notable enum/const values: `1`. The highest-risk contract area is compatible fallback order, register window shape, syscon phandles, child-node schemas, and provider cell counts.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this file plus `$ref` targets, and enforces required properties, array cardinality, constants, enums, and no top-level conditionals. `dtbs_check` then matches compiled DTS nodes by `compatible`, `$nodename`, or parent-schema inclusion, descends into pattern-matched children, and applies `additionalProperties` or `unevaluatedProperties` closure. Runtime flow begins only after the DTB is loaded: Linux bus, SoC, ASoC, MFD, syscon, or firmware drivers bind from compatible strings and acquire the resources described here.

## State and Persistence Behavior
The YAML itself stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: compatible strings, property names, phandle names, register tuple ordering, child-node names, and examples become contracts in source DTS files and compiled DTBs. Runtime state is created by the matched kernel drivers after probe, including regmap lifetime, child-device population, SoC control register access, and provider state owned by downstream clock/reset/power-domain or firmware drivers.

## Dependencies and Integration Points
Maintainers listed: Inochi Amaoto <inochiama@outlook.com>. Schema dependencies include `/schemas/dma/sophgo,cv1800b-dmamux.yaml#`, `/schemas/phy/sophgo,cv1800b-usb2-phy.yaml#`. Integration points include Linux platform probing, `syscon`/regmap consumers, MFD child population, reset/clock/power-domain providers, and SoC-specific DTS nodes. The file also integrates with Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and source DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to compatible fallback order, register window shape, syscon phandles, child-node schemas, and provider cell counts, drift between documented compatible strings and driver match tables, incorrect resource ordering, phandle names, or cell counts that block probe or misconfigure hardware. This schema rejects unknown top-level properties with `additionalProperties: false`. Regressions usually show up as schema-check failures, boot-time probe failures, missing audio/SoC child devices, bad firmware/resource allocation, broken suspend/resume, or silent routing/clocking errors in board audio paths.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/soc/sophgo/sophgo,cv1800b-top-syscon.yaml` for the targeted schema and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/soc/sophgo/sophgo,cv1800b-top-syscon.yaml` against boards that instantiate it. The schema has 1 embedded example; keep those examples valid under targeted binding checks. Cross-check compatible strings against driver `of_match_table` entries and inspect DTS users for register tuple counts, interrupt names, clocks/resets, supplies, DMA channels, graph endpoints, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/sophgo/sophgo,cv1800b-top-syscon.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/sophgo/sophgo,sg2044-top-syscon.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/sophgo/sophgo,sg2044-top-syscon.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/sophgo/sophgo,sg2044-top-syscon.yaml` defines the SoC system-controller/syscon binding titled `Sophgo SG2044 SoC TOP system controller`. The Sophgo SG2044 TOP system controller is a hardware block grouping multiple small functions, such as clocks and some other internal function. It constrains source DTS and compiled DTB hardware descriptions before Linux drivers consume the node.

## Important APIs, Types, and Functions
The API surface is the devicetree ABI rather than callable code. `compatible` uses an ordered compatible/fallback `items` sequence with 2 tokens: `sophgo,sg2044-top-syscon`, `syscon`. Top-level properties are `compatible`, `reg`, `clocks`, `#clock-cells`. Required top-level properties are `compatible`, `reg`, `clocks`, `#clock-cells`. Nested or reusable constraints include notable enum/const values: `1`. The highest-risk contract area is compatible fallback order, register window shape, syscon phandles, child-node schemas, and provider cell counts.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this file plus `$ref` targets, and enforces required properties, array cardinality, constants, enums, and no top-level conditionals. `dtbs_check` then matches compiled DTS nodes by `compatible`, `$nodename`, or parent-schema inclusion, descends into pattern-matched children, and applies `additionalProperties` or `unevaluatedProperties` closure. Runtime flow begins only after the DTB is loaded: Linux bus, SoC, ASoC, MFD, syscon, or firmware drivers bind from compatible strings and acquire the resources described here.

## State and Persistence Behavior
The YAML itself stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: compatible strings, property names, phandle names, register tuple ordering, child-node names, and examples become contracts in source DTS files and compiled DTBs. Runtime state is created by the matched kernel drivers after probe, including regmap lifetime, child-device population, SoC control register access, and provider state owned by downstream clock/reset/power-domain or firmware drivers.

## Dependencies and Integration Points
Maintainers listed: Inochi Amaoto <inochiama@gmail.com>. Schema dependencies include dt-schema core/meta schemas only. Integration points include Linux platform probing, `syscon`/regmap consumers, MFD child population, reset/clock/power-domain providers, and SoC-specific DTS nodes. The file also integrates with Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and source DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to compatible fallback order, register window shape, syscon phandles, child-node schemas, and provider cell counts, drift between documented compatible strings and driver match tables, incorrect resource ordering, phandle names, or cell counts that block probe or misconfigure hardware. This schema rejects unknown top-level properties with `additionalProperties: false`. Regressions usually show up as schema-check failures, boot-time probe failures, missing audio/SoC child devices, bad firmware/resource allocation, broken suspend/resume, or silent routing/clocking errors in board audio paths.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/soc/sophgo/sophgo,sg2044-top-syscon.yaml` for the targeted schema and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/soc/sophgo/sophgo,sg2044-top-syscon.yaml` against boards that instantiate it. The schema has 1 embedded example; keep those examples valid under targeted binding checks. Cross-check compatible strings against driver `of_match_table` entries and inspect DTS users for register tuple counts, interrupt names, clocks/resets, supplies, DMA channels, graph endpoints, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/sophgo/sophgo,sg2044-top-syscon.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/sophgo/sophgo.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/sophgo/sophgo.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/sophgo/sophgo.yaml` defines the SoC support binding titled `Sophgo SoC-based boards`. Sophgo SoC-based boards It constrains source DTS and compiled DTB hardware descriptions before Linux drivers consume the node.

## Important APIs, Types, and Functions
The API surface is the devicetree ABI rather than callable code. `compatible` uses `oneOf` with 6 branches with 16 tokens: `milkv,duo`, `sophgo,cv1800b`, `sophgo,huashan-pi`, `sophgo,cv1812h`, `milkv,duo-module-01-evb`, `milkv,duo-module-01`, `sophgo,sg2000`, `sipeed,licheerv-nano-b`, `sipeed,licheerv-nano`, `sophgo,sg2002`, `milkv,pioneer`, `sophgo,sg2042-evb-v1`, `sophgo,sg2042-evb-v2`, `sophgo,sg2042`, `sophgo,srd3-10`, `sophgo,sg2044`. Top-level properties are `$nodename`, `compatible`. Required top-level properties are none declared. Nested or reusable constraints include notable enum/const values: `/`. The highest-risk contract area is compatible strings, register resources, child-node layout, clock/reset/power-domain hooks, and phandle references.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this file plus `$ref` targets, and enforces required properties, array cardinality, constants, enums, and no top-level conditionals. `dtbs_check` then matches compiled DTS nodes by `compatible`, `$nodename`, or parent-schema inclusion, descends into pattern-matched children, and applies `additionalProperties` or `unevaluatedProperties` closure. Runtime flow begins only after the DTB is loaded: Linux bus, SoC, ASoC, MFD, syscon, or firmware drivers bind from compatible strings and acquire the resources described here.

## State and Persistence Behavior
The YAML itself stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: compatible strings, property names, phandle names, register tuple ordering, child-node names, and examples become contracts in source DTS files and compiled DTBs. Runtime state is created by the matched kernel drivers after probe, including driver probe state, mapped control registers, child-device state, and SoC integration resources.

## Dependencies and Integration Points
Maintainers listed: Chao Wei <chao.wei@sophgo.com>, Chen Wang <unicorn_wang@outlook.com>. Schema dependencies include dt-schema core/meta schemas only. Integration points include Linux platform probing, syscon/regmap helpers, board-level DTS nodes, and SoC-specific drivers. The file also integrates with Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and source DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to compatible strings, register resources, child-node layout, clock/reset/power-domain hooks, and phandle references, drift between documented compatible strings and driver match tables, incorrect resource ordering, phandle names, or cell counts that block probe or misconfigure hardware, large compatible sets where fallback ordering can drift over hardware generations, permissive extra properties that can hide spelling mistakes, lack of embedded examples, leaving coverage dependent on in-tree DTS users. This schema permits additional top-level properties. Regressions usually show up as schema-check failures, boot-time probe failures, missing audio/SoC child devices, bad firmware/resource allocation, broken suspend/resume, or silent routing/clocking errors in board audio paths.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/soc/sophgo/sophgo.yaml` for the targeted schema and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/soc/sophgo/sophgo.yaml` against boards that instantiate it. There are no embedded examples, so real DTS users and schema-only checks are the main coverage. Cross-check compatible strings against driver `of_match_table` entries and inspect DTS users for register tuple counts, interrupt names, clocks/resets, supplies, DMA channels, graph endpoints, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/sophgo/sophgo.yaml -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/sprd/sprd,sc9863a-glbregs.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/sprd/sprd,sc9863a-glbregs.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/sprd/sprd,sc9863a-glbregs.yaml` defines the SoC support binding titled `SC9863A Syscon`. It constrains source DTS and compiled DTB hardware descriptions through compatible strings, required resources, child-node topology, and shared schema references before Linux drivers consume the node.

## Important APIs, Types, and Functions
The API surface is the devicetree ABI rather than callable code. `compatible` uses an ordered compatible/fallback `items` sequence with 3 tokens: `sprd,sc9863a-glbregs`, `syscon`, `simple-mfd`. Top-level properties are `compatible`, `reg`, `ranges`, `#address-cells`, `#size-cells`. Required top-level properties are none declared. Nested or reusable constraints include child-node patterns: `@[0-9a-f]+$`; referenced schemas: `/schemas/clock/sprd,sc9863a-clk.yaml`; notable enum/const values: `1`. The highest-risk contract area is compatible strings, register resources, child-node layout, clock/reset/power-domain hooks, and phandle references.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this file plus `$ref` targets, and enforces required properties, array cardinality, constants, enums, and no top-level conditionals. `dtbs_check` then matches compiled DTS nodes by `compatible`, `$nodename`, or parent-schema inclusion, descends into pattern-matched children, and applies `additionalProperties` or `unevaluatedProperties` closure. Runtime flow begins only after the DTB is loaded: Linux bus, SoC, ASoC, MFD, syscon, or firmware drivers bind from compatible strings and acquire the resources described here.

## State and Persistence Behavior
The YAML itself stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: compatible strings, property names, phandle names, register tuple ordering, child-node names, and examples become contracts in source DTS files and compiled DTBs. Runtime state is created by the matched kernel drivers after probe, including driver probe state, mapped control registers, child-device state, and SoC integration resources.

## Dependencies and Integration Points
Maintainers listed: Orson Zhai <orsonzhai@gmail.com>, Baolin Wang <baolin.wang7@gmail.com>, Chunyan Zhang <zhang.lyra@gmail.com>. Schema dependencies include `/schemas/clock/sprd,sc9863a-clk.yaml`. Integration points include Linux platform probing, syscon/regmap helpers, board-level DTS nodes, and SoC-specific drivers. The file also integrates with Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and source DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to compatible strings, register resources, child-node layout, clock/reset/power-domain hooks, and phandle references, drift between documented compatible strings and driver match tables, incorrect resource ordering, phandle names, or cell counts that block probe or misconfigure hardware, child-node regexes that over-match unrelated children or under-match valid hardware nodes. This schema rejects unknown top-level properties with `additionalProperties: false`. Regressions usually show up as schema-check failures, boot-time probe failures, missing audio/SoC child devices, bad firmware/resource allocation, broken suspend/resume, or silent routing/clocking errors in board audio paths.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/soc/sprd/sprd,sc9863a-glbregs.yaml` for the targeted schema and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/soc/sprd/sprd,sc9863a-glbregs.yaml` against boards that instantiate it. The schema has 1 embedded example; keep those examples valid under targeted binding checks. Include child-node validation for `@[0-9a-f]+$`. Cross-check compatible strings against driver `of_match_table` entries and inspect DTS users for register tuple counts, interrupt names, clocks/resets, supplies, DMA channels, graph endpoints, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/sprd/sprd,sc9863a-glbregs.yaml -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/sti/st,sti-syscon.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/sti/st,sti-syscon.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/sti/st,sti-syscon.yaml` defines the SoC system-controller/syscon binding titled `STMicroelectronics STi platform sysconfig`. Binding for the various sysconfig nodes used within the STi platform device-tree to point to some common configuration registers used by other nodes. It constrains source DTS and compiled DTB hardware descriptions before Linux drivers consume the node.

## Important APIs, Types, and Functions
The API surface is the devicetree ABI rather than callable code. `compatible` uses an ordered compatible/fallback `items` sequence with 8 tokens: `st,stih407-core-syscfg`, `st,stih407-flash-syscfg`, `st,stih407-front-syscfg`, `st,stih407-lpm-syscfg`, `st,stih407-rear-syscfg`, `st,stih407-sbc-reg-syscfg`, `st,stih407-sbc-syscfg`, `syscon`. Top-level properties are `compatible`, `reg`, `sti-sasg-codec`. Required top-level properties are `compatible`, `reg`. Nested or reusable constraints include notable enum/const values: `st,stih407-sas-codec`. The highest-risk contract area is compatible fallback order, register window shape, syscon phandles, child-node schemas, and provider cell counts.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this file plus `$ref` targets, and enforces required properties, array cardinality, constants, enums, and no top-level conditionals. `dtbs_check` then matches compiled DTS nodes by `compatible`, `$nodename`, or parent-schema inclusion, descends into pattern-matched children, and applies `additionalProperties` or `unevaluatedProperties` closure. Runtime flow begins only after the DTB is loaded: Linux bus, SoC, ASoC, MFD, syscon, or firmware drivers bind from compatible strings and acquire the resources described here.

## State and Persistence Behavior
The YAML itself stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: compatible strings, property names, phandle names, register tuple ordering, child-node names, and examples become contracts in source DTS files and compiled DTBs. Runtime state is created by the matched kernel drivers after probe, including regmap lifetime, child-device population, SoC control register access, and provider state owned by downstream clock/reset/power-domain or firmware drivers.

## Dependencies and Integration Points
Maintainers listed: Patrice Chotard <patrice.chotard@foss.st.com>. Schema dependencies include dt-schema core/meta schemas only. Integration points include Linux platform probing, `syscon`/regmap consumers, MFD child population, reset/clock/power-domain providers, and SoC-specific DTS nodes. The file also integrates with Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and source DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to compatible fallback order, register window shape, syscon phandles, child-node schemas, and provider cell counts, drift between documented compatible strings and driver match tables, incorrect resource ordering, phandle names, or cell counts that block probe or misconfigure hardware. This schema rejects unknown top-level properties with `additionalProperties: false`. Regressions usually show up as schema-check failures, boot-time probe failures, missing audio/SoC child devices, bad firmware/resource allocation, broken suspend/resume, or silent routing/clocking errors in board audio paths.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/soc/sti/st,sti-syscon.yaml` for the targeted schema and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/soc/sti/st,sti-syscon.yaml` against boards that instantiate it. The schema has 1 embedded example; keep those examples valid under targeted binding checks. Cross-check compatible strings against driver `of_match_table` entries and inspect DTS users for register tuple counts, interrupt names, clocks/resets, supplies, DMA channels, graph endpoints, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/sti/st,sti-syscon.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/tegra/nvidia,nvec.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/tegra/nvidia,nvec.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/tegra/nvidia,nvec.yaml` defines the NVIDIA Tegra SoC infrastructure binding titled `NVIDIA compliant embedded controller`. It constrains source DTS and compiled DTB hardware descriptions through compatible strings, required resources, child-node topology, and shared schema references before Linux drivers consume the node.

## Important APIs, Types, and Functions
The API surface is the devicetree ABI rather than callable code. `compatible` uses a single `const` token with 1 token: `nvidia,nvec`. Top-level properties are `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `resets`, `reset-names`, `clock-frequency`, `request-gpios`, `slave-addr`. Required top-level properties are `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `resets`, `reset-names`, `clock-frequency`, `request-gpios`, `slave-addr`. Nested or reusable constraints include referenced schemas: `/schemas/types.yaml#/definitions/uint32`; notable enum/const values: `div-clk`, `fast-clk`, `i2c`. The highest-risk contract area is register resources, interrupts, clock/reset inputs, power-management flags, child devices, and Tegra generation-specific compatible strings.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this file plus `$ref` targets, and enforces required properties, array cardinality, constants, enums, and no top-level conditionals. `dtbs_check` then matches compiled DTS nodes by `compatible`, `$nodename`, or parent-schema inclusion, descends into pattern-matched children, and applies `additionalProperties` or `unevaluatedProperties` closure. Runtime flow begins only after the DTB is loaded: Linux bus, SoC, ASoC, MFD, syscon, or firmware drivers bind from compatible strings and acquire the resources described here.

## State and Persistence Behavior
The YAML itself stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: compatible strings, property names, phandle names, register tuple ordering, child-node names, and examples become contracts in source DTS files and compiled DTBs. Runtime state is created by the matched kernel drivers after probe, including power-management, suspend/resume, bus-control, interrupt, and embedded-controller state owned by Tegra drivers.

## Dependencies and Integration Points
Maintainers listed: Thierry Reding <thierry.reding@gmail.com>, Jon Hunter <jonathanh@nvidia.com>. Schema dependencies include `/schemas/types.yaml#/definitions/uint32`. Integration points include Tegra platform drivers, firmware/power-management paths, AHB/PMC/flow-controller/nvec subsystems, and board DTS integration. The file also integrates with Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and source DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to register resources, interrupts, clock/reset inputs, power-management flags, child devices, and Tegra generation-specific compatible strings, drift between documented compatible strings and driver match tables, incorrect resource ordering, phandle names, or cell counts that block probe or misconfigure hardware. This schema rejects unknown top-level properties with `additionalProperties: false`. Regressions usually show up as schema-check failures, boot-time probe failures, missing audio/SoC child devices, bad firmware/resource allocation, broken suspend/resume, or silent routing/clocking errors in board audio paths.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/soc/tegra/nvidia,nvec.yaml` for the targeted schema and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/soc/tegra/nvidia,nvec.yaml` against boards that instantiate it. The schema has 1 embedded example; keep those examples valid under targeted binding checks. Cross-check compatible strings against driver `of_match_table` entries and inspect DTS users for register tuple counts, interrupt names, clocks/resets, supplies, DMA channels, graph endpoints, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/tegra/nvidia,nvec.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/tegra/nvidia,tegra20-ahb.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/tegra/nvidia,tegra20-ahb.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/tegra/nvidia,tegra20-ahb.yaml` defines the NVIDIA Tegra SoC infrastructure binding titled `NVIDIA Tegra AHB`. It constrains source DTS and compiled DTB hardware descriptions through compatible strings, required resources, child-node topology, and shared schema references before Linux drivers consume the node.

## Important APIs, Types, and Functions
The API surface is the devicetree ABI rather than callable code. `compatible` uses `oneOf` with 2 branches with 5 tokens: `nvidia,tegra20-ahb`, `nvidia,tegra30-ahb`, `nvidia,tegra114-ahb`, `nvidia,tegra124-ahb`, `nvidia,tegra210-ahb`. Top-level properties are `compatible`, `reg`. Required top-level properties are `compatible`, `reg`. Nested or reusable constraints include no unusually complex nested constraints beyond the top-level properties. The highest-risk contract area is register resources, interrupts, clock/reset inputs, power-management flags, child devices, and Tegra generation-specific compatible strings.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this file plus `$ref` targets, and enforces required properties, array cardinality, constants, enums, and no top-level conditionals. `dtbs_check` then matches compiled DTS nodes by `compatible`, `$nodename`, or parent-schema inclusion, descends into pattern-matched children, and applies `additionalProperties` or `unevaluatedProperties` closure. Runtime flow begins only after the DTB is loaded: Linux bus, SoC, ASoC, MFD, syscon, or firmware drivers bind from compatible strings and acquire the resources described here.

## State and Persistence Behavior
The YAML itself stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: compatible strings, property names, phandle names, register tuple ordering, child-node names, and examples become contracts in source DTS files and compiled DTBs. Runtime state is created by the matched kernel drivers after probe, including power-management, suspend/resume, bus-control, interrupt, and embedded-controller state owned by Tegra drivers.

## Dependencies and Integration Points
Maintainers listed: Thierry Reding <thierry.reding@gmail.com>, Jon Hunter <jonathanh@nvidia.com>. Schema dependencies include dt-schema core/meta schemas only. Integration points include Tegra platform drivers, firmware/power-management paths, AHB/PMC/flow-controller/nvec subsystems, and board DTS integration. The file also integrates with Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and source DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to register resources, interrupts, clock/reset inputs, power-management flags, child devices, and Tegra generation-specific compatible strings, drift between documented compatible strings and driver match tables, incorrect resource ordering, phandle names, or cell counts that block probe or misconfigure hardware. This schema rejects unknown top-level properties with `additionalProperties: false`. Regressions usually show up as schema-check failures, boot-time probe failures, missing audio/SoC child devices, bad firmware/resource allocation, broken suspend/resume, or silent routing/clocking errors in board audio paths.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/soc/tegra/nvidia,tegra20-ahb.yaml` for the targeted schema and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/soc/tegra/nvidia,tegra20-ahb.yaml` against boards that instantiate it. The schema has 1 embedded example; keep those examples valid under targeted binding checks. Cross-check compatible strings against driver `of_match_table` entries and inspect DTS users for register tuple counts, interrupt names, clocks/resets, supplies, DMA channels, graph endpoints, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/tegra/nvidia,tegra20-ahb.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/tegra/nvidia,tegra20-flowctrl.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/tegra/nvidia,tegra20-flowctrl.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/tegra/nvidia,tegra20-flowctrl.yaml` defines the NVIDIA Tegra SoC infrastructure binding titled `NVIDIA Tegra Flow Controller`. It constrains source DTS and compiled DTB hardware descriptions through compatible strings, required resources, child-node topology, and shared schema references before Linux drivers consume the node.

## Important APIs, Types, and Functions
The API surface is the devicetree ABI rather than callable code. `compatible` uses `oneOf` with 2 branches with 6 tokens: `nvidia,tegra20-flowctrl`, `nvidia,tegra30-flowctrl`, `nvidia,tegra114-flowctrl`, `nvidia,tegra124-flowctrl`, `nvidia,tegra210-flowctrl`, `nvidia,tegra132-flowctrl`. Top-level properties are `compatible`, `reg`. Required top-level properties are `compatible`, `reg`. Nested or reusable constraints include no unusually complex nested constraints beyond the top-level properties. The highest-risk contract area is register resources, interrupts, clock/reset inputs, power-management flags, child devices, and Tegra generation-specific compatible strings.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this file plus `$ref` targets, and enforces required properties, array cardinality, constants, enums, and no top-level conditionals. `dtbs_check` then matches compiled DTS nodes by `compatible`, `$nodename`, or parent-schema inclusion, descends into pattern-matched children, and applies `additionalProperties` or `unevaluatedProperties` closure. Runtime flow begins only after the DTB is loaded: Linux bus, SoC, ASoC, MFD, syscon, or firmware drivers bind from compatible strings and acquire the resources described here.

## State and Persistence Behavior
The YAML itself stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: compatible strings, property names, phandle names, register tuple ordering, child-node names, and examples become contracts in source DTS files and compiled DTBs. Runtime state is created by the matched kernel drivers after probe, including power-management, suspend/resume, bus-control, interrupt, and embedded-controller state owned by Tegra drivers.

## Dependencies and Integration Points
Maintainers listed: Thierry Reding <thierry.reding@gmail.com>, Jon Hunter <jonathanh@nvidia.com>. Schema dependencies include dt-schema core/meta schemas only. Integration points include Tegra platform drivers, firmware/power-management paths, AHB/PMC/flow-controller/nvec subsystems, and board DTS integration. The file also integrates with Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and source DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to register resources, interrupts, clock/reset inputs, power-management flags, child devices, and Tegra generation-specific compatible strings, drift between documented compatible strings and driver match tables, incorrect resource ordering, phandle names, or cell counts that block probe or misconfigure hardware. This schema rejects unknown top-level properties with `additionalProperties: false`. Regressions usually show up as schema-check failures, boot-time probe failures, missing audio/SoC child devices, bad firmware/resource allocation, broken suspend/resume, or silent routing/clocking errors in board audio paths.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/soc/tegra/nvidia,tegra20-flowctrl.yaml` for the targeted schema and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/soc/tegra/nvidia,tegra20-flowctrl.yaml` against boards that instantiate it. The schema has 1 embedded example; keep those examples valid under targeted binding checks. Cross-check compatible strings against driver `of_match_table` entries and inspect DTS users for register tuple counts, interrupt names, clocks/resets, supplies, DMA channels, graph endpoints, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/tegra/nvidia,tegra20-flowctrl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/tegra/nvidia,tegra20-pmc.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/tegra/nvidia,tegra20-pmc.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/tegra/nvidia,tegra20-pmc.yaml` defines the NVIDIA Tegra SoC infrastructure binding titled `Tegra Power Management Controller (PMC)`. It constrains source DTS and compiled DTB hardware descriptions through compatible strings, required resources, child-node topology, and shared schema references before Linux drivers consume the node.

## Important APIs, Types, and Functions
The API surface is the devicetree ABI rather than callable code. `compatible` uses an `enum` of supported tokens with 5 tokens: `nvidia,tegra20-pmc`, `nvidia,tegra30-pmc`, `nvidia,tegra114-pmc`, `nvidia,tegra124-pmc`, `nvidia,tegra210-pmc`. Top-level properties are `compatible`, `reg`, `clock-names`, `clocks`, `#clock-cells`, `#interrupt-cells`, `interrupt-controller`, `nvidia,invert-interrupt`, `nvidia,core-power-req-active-high`, `nvidia,sys-clock-req-active-high`, `nvidia,combined-power-req`, `nvidia,cpu-pwr-good-en`, `nvidia,suspend-mode`, `nvidia,cpu-pwr-good-time`, `nvidia,cpu-pwr-off-time`, `nvidia,core-pwr-good-time`, `nvidia,core-pwr-off-time`, `nvidia,lp0-vec`, `core-supply`, `core-domain`, `i2c-thermtrip`, `powergates`, `pinmux`. Required top-level properties are `compatible`, `reg`, `clock-names`, `clocks`, `#clock-cells`. Nested or reusable constraints include composition/conditionals: `allOf`, `dependencies`; referenced schemas: `/schemas/types.yaml#/definitions/flag`, `/schemas/types.yaml#/definitions/string-array`, `/schemas/types.yaml#/definitions/uint32`, `/schemas/types.yaml#/definitions/uint32-array`; notable enum/const values: `audio`, `bb`, `cam`, `comp`, `csia`, `csb`, `cse`, `dsi`, `dsib`, `dsic`, `dsid`, `hdmi`, `hsic`, `hv`, `lvds`, `mipi-bias`, and 36 more. The highest-risk contract area is register resources, interrupts, clock/reset inputs, power-management flags, child devices, and Tegra generation-specific compatible strings.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this file plus `$ref` targets, and enforces required properties, array cardinality, constants, enums, and `allOf`, `dependencies`. `dtbs_check` then matches compiled DTS nodes by `compatible`, `$nodename`, or parent-schema inclusion, descends into pattern-matched children, and applies `additionalProperties` or `unevaluatedProperties` closure. Runtime flow begins only after the DTB is loaded: Linux bus, SoC, ASoC, MFD, syscon, or firmware drivers bind from compatible strings and acquire the resources described here.

## State and Persistence Behavior
The YAML itself stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: compatible strings, property names, phandle names, register tuple ordering, child-node names, and examples become contracts in source DTS files and compiled DTBs. Runtime state is created by the matched kernel drivers after probe, including power-management, suspend/resume, bus-control, interrupt, and embedded-controller state owned by Tegra drivers.

## Dependencies and Integration Points
Maintainers listed: Thierry Reding <thierry.reding@gmail.com>, Jonathan Hunter <jonathanh@nvidia.com>. Schema dependencies include `/schemas/types.yaml#/definitions/flag`, `/schemas/types.yaml#/definitions/string-array`, `/schemas/types.yaml#/definitions/uint32`, `/schemas/types.yaml#/definitions/uint32-array`. Integration points include Tegra platform drivers, firmware/power-management paths, AHB/PMC/flow-controller/nvec subsystems, and board DTS integration. The file also integrates with Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and source DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to register resources, interrupts, clock/reset inputs, power-management flags, child devices, and Tegra generation-specific compatible strings, drift between documented compatible strings and driver match tables, incorrect resource ordering, phandle names, or cell counts that block probe or misconfigure hardware, variant-specific conditional branches accepting one SoC/chip while rejecting another. This schema rejects unknown top-level properties with `additionalProperties: false`. Regressions usually show up as schema-check failures, boot-time probe failures, missing audio/SoC child devices, bad firmware/resource allocation, broken suspend/resume, or silent routing/clocking errors in board audio paths.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/soc/tegra/nvidia,tegra20-pmc.yaml` for the targeted schema and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/soc/tegra/nvidia,tegra20-pmc.yaml` against boards that instantiate it. The schema has 1 embedded example; keep those examples valid under targeted binding checks. Cross-check compatible strings against driver `of_match_table` entries and inspect DTS users for register tuple counts, interrupt names, clocks/resets, supplies, DMA channels, graph endpoints, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/tegra/nvidia,tegra20-pmc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/ti/k3-ringacc.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/ti/k3-ringacc.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/ti/k3-ringacc.yaml` defines the Texas Instruments SoC service binding titled `Texas Instruments K3 NavigatorSS Ring Accelerator`. The Ring Accelerator (RA) is a machine which converts read/write accesses from/to a constant address into corresponding read/write accesses from/to a circular data structure in memory. It constrains source DTS and compiled DTB hardware descriptions before Linux drivers consume the node.

## Important APIs, Types, and Functions
The API surface is the devicetree ABI rather than callable code. `compatible` uses an ordered compatible/fallback `items` sequence with 1 token: `ti,am654-navss-ringacc`. Top-level properties are `compatible`, `reg`, `reg-names`, `msi-parent`, `ti,num-rings`, `ti,sci-rm-range-gp-rings`. Required top-level properties are `compatible`, `reg`, `reg-names`, `msi-parent`, `ti,num-rings`, `ti,sci-rm-range-gp-rings`, `ti,sci`, `ti,sci-dev-id`. Nested or reusable constraints include composition/conditionals: `allOf`; referenced schemas: `/schemas/arm/keystone/ti,k3-sci-common.yaml#`, `/schemas/types.yaml#/definitions/uint32`; notable enum/const values: `rt`, `fifos`, `proxy_gcfg`, `proxy_target`, `cfg`. The highest-risk contract area is firmware phandles, device IDs, register ranges, interrupts, DMA/ring resources, power-domain cells, and PRUSS child topology.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this file plus `$ref` targets, and enforces required properties, array cardinality, constants, enums, and `allOf`. `dtbs_check` then matches compiled DTS nodes by `compatible`, `$nodename`, or parent-schema inclusion, descends into pattern-matched children, and applies `additionalProperties` or `unevaluatedProperties` closure. Runtime flow begins only after the DTB is loaded: Linux bus, SoC, ASoC, MFD, syscon, or firmware drivers bind from compatible strings and acquire the resources described here.

## State and Persistence Behavior
The YAML itself stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: compatible strings, property names, phandle names, register tuple ordering, child-node names, and examples become contracts in source DTS files and compiled DTBs. Runtime state is created by the matched kernel drivers after probe, including firmware-mediated device state, ring/queue allocation, remote-processor resources, power-domain state, and IPC state owned by TI subsystem drivers.

## Dependencies and Integration Points
Maintainers listed: Santosh Shilimkar <ssantosh@kernel.org>, Grygorii Strashko <grygorii.strashko@ti.com>. Schema dependencies include `/schemas/arm/keystone/ti,k3-sci-common.yaml#`, `/schemas/types.yaml#/definitions/uint32`. Integration points include TI K3/DaVinci/PRUSS platform drivers, TI-SCI firmware channels, DMA/ring acceleration, power-domain providers, wakeup firmware, and board DTS validation. The file also integrates with Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and source DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to firmware phandles, device IDs, register ranges, interrupts, DMA/ring resources, power-domain cells, and PRUSS child topology, drift between documented compatible strings and driver match tables, incorrect resource ordering, phandle names, or cell counts that block probe or misconfigure hardware, variant-specific conditional branches accepting one SoC/chip while rejecting another. This schema closes composed schemas with `unevaluatedProperties: false`. Regressions usually show up as schema-check failures, boot-time probe failures, missing audio/SoC child devices, bad firmware/resource allocation, broken suspend/resume, or silent routing/clocking errors in board audio paths.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/soc/ti/k3-ringacc.yaml` for the targeted schema and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/soc/ti/k3-ringacc.yaml` against boards that instantiate it. The schema has 1 embedded example; keep those examples valid under targeted binding checks. Cross-check compatible strings against driver `of_match_table` entries and inspect DTS users for register tuple counts, interrupt names, clocks/resets, supplies, DMA channels, graph endpoints, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/ti/k3-ringacc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/ti/sci-pm-domain.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/ti/sci-pm-domain.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/ti/sci-pm-domain.yaml` defines the Texas Instruments SoC service binding titled `TI-SCI generic power domain`. Some TI SoCs contain a system controller (like the Power Management Micro Controller (PMMC) on Keystone 66AK2G SoC) that are responsible for controlling the state of the various hardware modules present on the SoC. It constrains source DTS and compiled DTB hardware descriptions before Linux drivers consume the node.

## Important APIs, Types, and Functions
The API surface is the devicetree ABI rather than callable code. `compatible` uses a single `const` token with 1 token: `ti,sci-pm-domain`. Top-level properties are `compatible`, `#power-domain-cells`. Required top-level properties are none declared. Nested or reusable constraints include composition/conditionals: `allOf`; referenced schemas: `/schemas/power/power-domain.yaml#`; notable enum/const values: `1`, `2`. The highest-risk contract area is firmware phandles, device IDs, register ranges, interrupts, DMA/ring resources, power-domain cells, and PRUSS child topology.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this file plus `$ref` targets, and enforces required properties, array cardinality, constants, enums, and `allOf`. `dtbs_check` then matches compiled DTS nodes by `compatible`, `$nodename`, or parent-schema inclusion, descends into pattern-matched children, and applies `additionalProperties` or `unevaluatedProperties` closure. Runtime flow begins only after the DTB is loaded: Linux bus, SoC, ASoC, MFD, syscon, or firmware drivers bind from compatible strings and acquire the resources described here.

## State and Persistence Behavior
The YAML itself stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: compatible strings, property names, phandle names, register tuple ordering, child-node names, and examples become contracts in source DTS files and compiled DTBs. Runtime state is created by the matched kernel drivers after probe, including firmware-mediated device state, ring/queue allocation, remote-processor resources, power-domain state, and IPC state owned by TI subsystem drivers.

## Dependencies and Integration Points
Maintainers listed: Nishanth Menon <nm@ti.com>. Schema dependencies include `/schemas/power/power-domain.yaml#`. Integration points include TI K3/DaVinci/PRUSS platform drivers, TI-SCI firmware channels, DMA/ring acceleration, power-domain providers, wakeup firmware, and board DTS validation. The file also integrates with Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and source DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to firmware phandles, device IDs, register ranges, interrupts, DMA/ring resources, power-domain cells, and PRUSS child topology, drift between documented compatible strings and driver match tables, incorrect resource ordering, phandle names, or cell counts that block probe or misconfigure hardware, variant-specific conditional branches accepting one SoC/chip while rejecting another. This schema rejects unknown top-level properties with `additionalProperties: false`. Regressions usually show up as schema-check failures, boot-time probe failures, missing audio/SoC child devices, bad firmware/resource allocation, broken suspend/resume, or silent routing/clocking errors in board audio paths.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/soc/ti/sci-pm-domain.yaml` for the targeted schema and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/soc/ti/sci-pm-domain.yaml` against boards that instantiate it. The schema has 2 embedded examples; keep those examples valid under targeted binding checks. Cross-check compatible strings against driver `of_match_table` entries and inspect DTS users for register tuple counts, interrupt names, clocks/resets, supplies, DMA channels, graph endpoints, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/ti/sci-pm-domain.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/ti/ti,am654-serdes-ctrl.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/ti/ti,am654-serdes-ctrl.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/ti/ti,am654-serdes-ctrl.yaml` defines the Texas Instruments SoC service binding titled `Texas Instruments AM654 Serdes Control Syscon`. It constrains source DTS and compiled DTB hardware descriptions through compatible strings, required resources, child-node topology, and shared schema references before Linux drivers consume the node.

## Important APIs, Types, and Functions
The API surface is the devicetree ABI rather than callable code. `compatible` uses an ordered compatible/fallback `items` sequence with 3 tokens: `ti,am654-serdes-ctrl`, `syscon`, `simple-mfd`. Top-level properties are `compatible`, `reg`, `mux-controller`. Required top-level properties are `compatible`, `reg`, `mux-controller`. Nested or reusable constraints include referenced schemas: `/schemas/mux/reg-mux.yaml#`. The highest-risk contract area is firmware phandles, device IDs, register ranges, interrupts, DMA/ring resources, power-domain cells, and PRUSS child topology.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this file plus `$ref` targets, and enforces required properties, array cardinality, constants, enums, and no top-level conditionals. `dtbs_check` then matches compiled DTS nodes by `compatible`, `$nodename`, or parent-schema inclusion, descends into pattern-matched children, and applies `additionalProperties` or `unevaluatedProperties` closure. Runtime flow begins only after the DTB is loaded: Linux bus, SoC, ASoC, MFD, syscon, or firmware drivers bind from compatible strings and acquire the resources described here.

## State and Persistence Behavior
The YAML itself stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: compatible strings, property names, phandle names, register tuple ordering, child-node names, and examples become contracts in source DTS files and compiled DTBs. Runtime state is created by the matched kernel drivers after probe, including firmware-mediated device state, ring/queue allocation, remote-processor resources, power-domain state, and IPC state owned by TI subsystem drivers.

## Dependencies and Integration Points
Maintainers listed: Nishanth Menon <nm@ti.com>. Schema dependencies include `/schemas/mux/reg-mux.yaml#`. Integration points include TI K3/DaVinci/PRUSS platform drivers, TI-SCI firmware channels, DMA/ring acceleration, power-domain providers, wakeup firmware, and board DTS validation. The file also integrates with Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and source DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to firmware phandles, device IDs, register ranges, interrupts, DMA/ring resources, power-domain cells, and PRUSS child topology, drift between documented compatible strings and driver match tables, incorrect resource ordering, phandle names, or cell counts that block probe or misconfigure hardware. This schema rejects unknown top-level properties with `additionalProperties: false`. Regressions usually show up as schema-check failures, boot-time probe failures, missing audio/SoC child devices, bad firmware/resource allocation, broken suspend/resume, or silent routing/clocking errors in board audio paths.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/soc/ti/ti,am654-serdes-ctrl.yaml` for the targeted schema and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/soc/ti/ti,am654-serdes-ctrl.yaml` against boards that instantiate it. The schema has 1 embedded example; keep those examples valid under targeted binding checks. Cross-check compatible strings against driver `of_match_table` entries and inspect DTS users for register tuple counts, interrupt names, clocks/resets, supplies, DMA channels, graph endpoints, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/ti/ti,am654-serdes-ctrl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/ti/ti,j721e-system-controller.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/ti/ti,j721e-system-controller.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/ti/ti,j721e-system-controller.yaml` defines the SoC system-controller/syscon binding titled `TI J721e System Controller Registers R/W`. This represents the Control Module registers (CTRL_MMR0) on the SoC. It constrains source DTS and compiled DTB hardware descriptions before Linux drivers consume the node.

## Important APIs, Types, and Functions
The API surface is the devicetree ABI rather than callable code. `compatible` uses an ordered compatible/fallback `items` sequence with 6 tokens: `ti,am654-system-controller`, `ti,j7200-system-controller`, `ti,j721e-system-controller`, `ti,j721s2-system-controller`, `syscon`, `simple-mfd`. Top-level properties are `compatible`, `reg`, `#address-cells`, `#size-cells`, `ranges`. Required top-level properties are `compatible`, `reg`, `#address-cells`, `#size-cells`, `ranges`. Nested or reusable constraints include child-node patterns: `^mux-controller@[0-9a-f]+$`, `^clock-controller@[0-9a-f]+$`, `phy@[0-9a-f]+$`, `^chipid@[0-9a-f]+$`, `^pcie-ctrl@[0-9a-f]+$`, `^clock@[0-9a-f]+$`, `^dss-oldi-io-ctrl@[0-9a-f]+$`; referenced schemas: `/schemas/clock/ti,am654-ehrpwm-tbclk.yaml#`, `/schemas/hwinfo/ti,k3-socinfo.yaml#`, `/schemas/mfd/syscon.yaml#`, `/schemas/phy/ti,phy-gmii-sel.yaml#`, `/schemas/soc/ti/ti,am654-serdes-ctrl.yaml#`; notable enum/const values: `1`. The highest-risk contract area is compatible fallback order, register window shape, syscon phandles, child-node schemas, and provider cell counts.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this file plus `$ref` targets, and enforces required properties, array cardinality, constants, enums, and no top-level conditionals. `dtbs_check` then matches compiled DTS nodes by `compatible`, `$nodename`, or parent-schema inclusion, descends into pattern-matched children, and applies `additionalProperties` or `unevaluatedProperties` closure. Runtime flow begins only after the DTB is loaded: Linux bus, SoC, ASoC, MFD, syscon, or firmware drivers bind from compatible strings and acquire the resources described here.

## State and Persistence Behavior
The YAML itself stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: compatible strings, property names, phandle names, register tuple ordering, child-node names, and examples become contracts in source DTS files and compiled DTBs. Runtime state is created by the matched kernel drivers after probe, including regmap lifetime, child-device population, SoC control register access, and provider state owned by downstream clock/reset/power-domain or firmware drivers.

## Dependencies and Integration Points
Maintainers listed: Kishon Vijay Abraham I <kishon@kernel.org>, Roger Quadros <rogerq@kernel.org>. Schema dependencies include `/schemas/clock/ti,am654-ehrpwm-tbclk.yaml#`, `/schemas/hwinfo/ti,k3-socinfo.yaml#`, `/schemas/mfd/syscon.yaml#`, `/schemas/phy/ti,phy-gmii-sel.yaml#`, `/schemas/soc/ti/ti,am654-serdes-ctrl.yaml#`. Integration points include Linux platform probing, `syscon`/regmap consumers, MFD child population, reset/clock/power-domain providers, and SoC-specific DTS nodes. The file also integrates with Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and source DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to compatible fallback order, register window shape, syscon phandles, child-node schemas, and provider cell counts, drift between documented compatible strings and driver match tables, incorrect resource ordering, phandle names, or cell counts that block probe or misconfigure hardware, child-node regexes that over-match unrelated children or under-match valid hardware nodes. This schema rejects unknown top-level properties with `additionalProperties: false`. Regressions usually show up as schema-check failures, boot-time probe failures, missing audio/SoC child devices, bad firmware/resource allocation, broken suspend/resume, or silent routing/clocking errors in board audio paths.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/soc/ti/ti,j721e-system-controller.yaml` for the targeted schema and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/soc/ti/ti,j721e-system-controller.yaml` against boards that instantiate it. The schema has 1 embedded example; keep those examples valid under targeted binding checks. Include child-node validation for `^mux-controller@[0-9a-f]+$`, `^clock-controller@[0-9a-f]+$`, `phy@[0-9a-f]+$`, `^chipid@[0-9a-f]+$`, `^pcie-ctrl@[0-9a-f]+$`, and 2 more. Cross-check compatible strings against driver `of_match_table` entries and inspect DTS users for register tuple counts, interrupt names, clocks/resets, supplies, DMA channels, graph endpoints, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/ti/ti,j721e-system-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/ti/ti,j784s4-bist.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/ti/ti,j784s4-bist.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/ti/ti,j784s4-bist.yaml` defines the Texas Instruments SoC service binding titled `Texas Instruments K3 BIST`. The BIST (Built-In Self Test) module is an IP block present in K3 devices that support triggering of BIST tests, both PBIST (Memory BIST) and LBIST (Logic BIST) on a core. It constrains source DTS and compiled DTB hardware descriptions before Linux drivers consume the node.

## Important APIs, Types, and Functions
The API surface is the devicetree ABI rather than callable code. `compatible` uses a single `const` token with 1 token: `ti,j784s4-bist`. Top-level properties are `compatible`, `reg`, `reg-names`, `clocks`, `power-domains`. Required top-level properties are `compatible`, `reg`, `reg-names`, `ti,sci-dev-id`. Nested or reusable constraints include composition/conditionals: `allOf`; referenced schemas: `/schemas/arm/keystone/ti,k3-sci-common.yaml#`; notable enum/const values: `cfg`, `ctrl_mmr`. The highest-risk contract area is firmware phandles, device IDs, register ranges, interrupts, DMA/ring resources, power-domain cells, and PRUSS child topology.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this file plus `$ref` targets, and enforces required properties, array cardinality, constants, enums, and `allOf`. `dtbs_check` then matches compiled DTS nodes by `compatible`, `$nodename`, or parent-schema inclusion, descends into pattern-matched children, and applies `additionalProperties` or `unevaluatedProperties` closure. Runtime flow begins only after the DTB is loaded: Linux bus, SoC, ASoC, MFD, syscon, or firmware drivers bind from compatible strings and acquire the resources described here.

## State and Persistence Behavior
The YAML itself stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: compatible strings, property names, phandle names, register tuple ordering, child-node names, and examples become contracts in source DTS files and compiled DTBs. Runtime state is created by the matched kernel drivers after probe, including firmware-mediated device state, ring/queue allocation, remote-processor resources, power-domain state, and IPC state owned by TI subsystem drivers.

## Dependencies and Integration Points
Maintainers listed: Neha Malcom Francis <n-francis@ti.com>. Schema dependencies include `/schemas/arm/keystone/ti,k3-sci-common.yaml#`. Integration points include TI K3/DaVinci/PRUSS platform drivers, TI-SCI firmware channels, DMA/ring acceleration, power-domain providers, wakeup firmware, and board DTS validation. The file also integrates with Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and source DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to firmware phandles, device IDs, register ranges, interrupts, DMA/ring resources, power-domain cells, and PRUSS child topology, drift between documented compatible strings and driver match tables, incorrect resource ordering, phandle names, or cell counts that block probe or misconfigure hardware, variant-specific conditional branches accepting one SoC/chip while rejecting another. This schema closes composed schemas with `unevaluatedProperties: false`. Regressions usually show up as schema-check failures, boot-time probe failures, missing audio/SoC child devices, bad firmware/resource allocation, broken suspend/resume, or silent routing/clocking errors in board audio paths.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/soc/ti/ti,j784s4-bist.yaml` for the targeted schema and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/soc/ti/ti,j784s4-bist.yaml` against boards that instantiate it. The schema has 1 embedded example; keep those examples valid under targeted binding checks. Cross-check compatible strings against driver `of_match_table` entries and inspect DTS users for register tuple counts, interrupt names, clocks/resets, supplies, DMA channels, graph endpoints, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/ti/ti,j784s4-bist.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/ti/ti,pruss.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/ti/ti,pruss.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/ti/ti,pruss.yaml` defines the Texas Instruments SoC service binding titled `TI Programmable Real-Time Unit and Industrial Communication Subsystem

`. The Programmable Real-Time Unit and Industrial Communication Subsystem (PRU-ICSS a.k.a. It constrains source DTS and compiled DTB hardware descriptions before Linux drivers consume the node.

## Important APIs, Types, and Functions
The API surface is the devicetree ABI rather than callable code. `compatible` uses an `enum` of supported tokens with 9 tokens: `ti,am3356-pruss`, `ti,am4376-pruss0`, `ti,am4376-pruss1`, `ti,am5728-pruss`, `ti,am625-pruss`, `ti,am642-icssg`, `ti,am654-icssg`, `ti,j721e-icssg`, `ti,k2g-pruss`. Top-level properties are `$nodename`, `compatible`, `reg`, `#address-cells`, `#size-cells`, `ranges`, `dma-ranges`, `dma-coherent`, `power-domains`, `clocks`. Required top-level properties are `compatible`, `reg`, `ranges`. Nested or reusable constraints include composition/conditionals: `allOf`; child-node patterns: `memories@[a-f0-9]+$`, `cfg@[a-f0-9]+$`, `iep@[a-f0-9]+$`, `ecap@[a-f0-9]+$`, `mii-rt@[a-f0-9]+$`, `mii-g-rt@[a-f0-9]+$`, `^pa-stats@[a-f0-9]+$`, `interrupt-controller@[a-f0-9]+$`, and 2 more; referenced schemas: `/schemas/interrupt-controller/ti,pruss-intc.yaml#`, `/schemas/net/ti,davinci-mdio.yaml#`, `/schemas/net/ti,pruss-ecap.yaml#`, `/schemas/remoteproc/ti,pru-rproc.yaml#`; child-node API keys: `reg`, `reg-names`, `compatible`, `#address-cells`, `#size-cells`, `ranges`, `clocks`; notable enum/const values: `1`, `dram0`, `dram1`, `shrdram2`, `ti,pruss-cfg`, `syscon`, `0`, `ti,pruss-mii`, `ti,pruss-mii-g`, `ti,pruss-pa-st`. The highest-risk contract area is firmware phandles, device IDs, register ranges, interrupts, DMA/ring resources, power-domain cells, and PRUSS child topology.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this file plus `$ref` targets, and enforces required properties, array cardinality, constants, enums, and `allOf`. `dtbs_check` then matches compiled DTS nodes by `compatible`, `$nodename`, or parent-schema inclusion, descends into pattern-matched children, and applies `additionalProperties` or `unevaluatedProperties` closure. Runtime flow begins only after the DTB is loaded: Linux bus, SoC, ASoC, MFD, syscon, or firmware drivers bind from compatible strings and acquire the resources described here.

## State and Persistence Behavior
The YAML itself stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: compatible strings, property names, phandle names, register tuple ordering, child-node names, and examples become contracts in source DTS files and compiled DTBs. Runtime state is created by the matched kernel drivers after probe, including firmware-mediated device state, ring/queue allocation, remote-processor resources, power-domain state, and IPC state owned by TI subsystem drivers.

## Dependencies and Integration Points
Maintainers listed: Suman Anna <s-anna@ti.com>. Schema dependencies include `/schemas/interrupt-controller/ti,pruss-intc.yaml#`, `/schemas/net/ti,davinci-mdio.yaml#`, `/schemas/net/ti,pruss-ecap.yaml#`, `/schemas/remoteproc/ti,pru-rproc.yaml#`. Integration points include TI K3/DaVinci/PRUSS platform drivers, TI-SCI firmware channels, DMA/ring acceleration, power-domain providers, wakeup firmware, and board DTS validation. The file also integrates with Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and source DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to firmware phandles, device IDs, register ranges, interrupts, DMA/ring resources, power-domain cells, and PRUSS child topology, drift between documented compatible strings and driver match tables, incorrect resource ordering, phandle names, or cell counts that block probe or misconfigure hardware, variant-specific conditional branches accepting one SoC/chip while rejecting another, child-node regexes that over-match unrelated children or under-match valid hardware nodes. This schema rejects unknown top-level properties with `additionalProperties: false`. Regressions usually show up as schema-check failures, boot-time probe failures, missing audio/SoC child devices, bad firmware/resource allocation, broken suspend/resume, or silent routing/clocking errors in board audio paths.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/soc/ti/ti,pruss.yaml` for the targeted schema and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/soc/ti/ti,pruss.yaml` against boards that instantiate it. The schema has 2 embedded examples; keep those examples valid under targeted binding checks. Include child-node validation for `memories@[a-f0-9]+$`, `cfg@[a-f0-9]+$`, `iep@[a-f0-9]+$`, `ecap@[a-f0-9]+$`, `mii-rt@[a-f0-9]+$`, and 5 more. Cross-check compatible strings against driver `of_match_table` entries and inspect DTS users for register tuple counts, interrupt names, clocks/resets, supplies, DMA channels, graph endpoints, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/ti/ti,pruss.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/ti/wkup-m3-ipc.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/ti/wkup-m3-ipc.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/ti/wkup-m3-ipc.yaml` defines the Texas Instruments SoC service binding titled `Wakeup M3 IPC device`. The TI AM33xx and AM43xx family of devices use a small Cortex M3 co-processor (commonly referred to as Wakeup M3 or CM3) to help with various low power tasks that cannot be controlled from the MPU, like suspend/resume and certain deep C-states for CPU Idle. It constrains source DTS and compiled DTB hardware descriptions before Linux drivers consume the node.

## Important APIs, Types, and Functions
The API surface is the devicetree ABI rather than callable code. `compatible` uses an `enum` of supported tokens with 2 tokens: `ti,am3352-wkup-m3-ipc`, `ti,am4372-wkup-m3-ipc`. Top-level properties are `compatible`, `reg`, `interrupts`, `ti,rproc`, `mboxes`, `firmware-name`, `ti,vtt-gpio-pin`, `ti,set-io-isolation`. Required top-level properties are `compatible`, `reg`, `interrupts`, `ti,rproc`, `mboxes`. Nested or reusable constraints include composition/conditionals: `allOf`; referenced schemas: `/schemas/types.yaml#/definitions/phandle`, `/schemas/types.yaml#/definitions/uint32`. The highest-risk contract area is firmware phandles, device IDs, register ranges, interrupts, DMA/ring resources, power-domain cells, and PRUSS child topology.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this file plus `$ref` targets, and enforces required properties, array cardinality, constants, enums, and `allOf`. `dtbs_check` then matches compiled DTS nodes by `compatible`, `$nodename`, or parent-schema inclusion, descends into pattern-matched children, and applies `additionalProperties` or `unevaluatedProperties` closure. Runtime flow begins only after the DTB is loaded: Linux bus, SoC, ASoC, MFD, syscon, or firmware drivers bind from compatible strings and acquire the resources described here.

## State and Persistence Behavior
The YAML itself stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: compatible strings, property names, phandle names, register tuple ordering, child-node names, and examples become contracts in source DTS files and compiled DTBs. Runtime state is created by the matched kernel drivers after probe, including firmware-mediated device state, ring/queue allocation, remote-processor resources, power-domain state, and IPC state owned by TI subsystem drivers.

## Dependencies and Integration Points
Maintainers listed: Dave Gerlach <d-gerlach@ti.com>, Drew Fustini <dfustini@baylibre.com>. Schema dependencies include `/schemas/types.yaml#/definitions/phandle`, `/schemas/types.yaml#/definitions/uint32`. Integration points include TI K3/DaVinci/PRUSS platform drivers, TI-SCI firmware channels, DMA/ring acceleration, power-domain providers, wakeup firmware, and board DTS validation. The file also integrates with Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and source DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to firmware phandles, device IDs, register ranges, interrupts, DMA/ring resources, power-domain cells, and PRUSS child topology, drift between documented compatible strings and driver match tables, incorrect resource ordering, phandle names, or cell counts that block probe or misconfigure hardware, variant-specific conditional branches accepting one SoC/chip while rejecting another. This schema rejects unknown top-level properties with `additionalProperties: false`. Regressions usually show up as schema-check failures, boot-time probe failures, missing audio/SoC child devices, bad firmware/resource allocation, broken suspend/resume, or silent routing/clocking errors in board audio paths.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/soc/ti/wkup-m3-ipc.yaml` for the targeted schema and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/soc/ti/wkup-m3-ipc.yaml` against boards that instantiate it. The schema has 2 embedded examples; keep those examples valid under targeted binding checks. Cross-check compatible strings against driver `of_match_table` entries and inspect DTS users for register tuple counts, interrupt names, clocks/resets, supplies, DMA channels, graph endpoints, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/ti/wkup-m3-ipc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/xilinx/xilinx.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/xilinx/xilinx.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/xilinx/xilinx.yaml` defines the SoC support binding titled `Xilinx Zynq Platforms`. AMD/Xilinx boards with ARM 32/64bits cores It constrains source DTS and compiled DTB hardware descriptions before Linux drivers consume the node.

## Important APIs, Types, and Functions
The API surface is the devicetree ABI rather than callable code. `compatible` uses `oneOf` with 24 branches with 86 tokens: `adapteva,parallella`, `digilent,zynq-zybo`, `digilent,zynq-zybo-z7`, `ebang,ebaz4205`, `myir,zynq-zturn-v5`, `myir,zynq-zturn`, `xlnx,zynq-cc108`, `xlnx,zynq-zc702`, `xlnx,zynq-zc706`, `xlnx,zynq-zc770-xm010`, `xlnx,zynq-zc770-xm011`, `xlnx,zynq-zc770-xm012`, `xlnx,zynq-zc770-xm013`, `xlnx,zynq-7000`, `avnet,zynq-microzed`, `xlnx,zynq-microzed`, `avnet,zynq-zed`, `xlnx,zynq-zed`, and 68 more. Top-level properties are `$nodename`, `compatible`. Required top-level properties are none declared. Nested or reusable constraints include notable enum/const values: `/`. The highest-risk contract area is compatible strings, register resources, child-node layout, clock/reset/power-domain hooks, and phandle references.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this file plus `$ref` targets, and enforces required properties, array cardinality, constants, enums, and no top-level conditionals. `dtbs_check` then matches compiled DTS nodes by `compatible`, `$nodename`, or parent-schema inclusion, descends into pattern-matched children, and applies `additionalProperties` or `unevaluatedProperties` closure. Runtime flow begins only after the DTB is loaded: Linux bus, SoC, ASoC, MFD, syscon, or firmware drivers bind from compatible strings and acquire the resources described here.

## State and Persistence Behavior
The YAML itself stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: compatible strings, property names, phandle names, register tuple ordering, child-node names, and examples become contracts in source DTS files and compiled DTBs. Runtime state is created by the matched kernel drivers after probe, including driver probe state, mapped control registers, child-device state, and SoC integration resources.

## Dependencies and Integration Points
Maintainers listed: Michal Simek <michal.simek@amd.com>. Schema dependencies include dt-schema core/meta schemas only. Integration points include Linux platform probing, syscon/regmap helpers, board-level DTS nodes, and SoC-specific drivers. The file also integrates with Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and source DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to compatible strings, register resources, child-node layout, clock/reset/power-domain hooks, and phandle references, drift between documented compatible strings and driver match tables, incorrect resource ordering, phandle names, or cell counts that block probe or misconfigure hardware, large compatible sets where fallback ordering can drift over hardware generations, permissive extra properties that can hide spelling mistakes, lack of embedded examples, leaving coverage dependent on in-tree DTS users. This schema permits additional top-level properties. Regressions usually show up as schema-check failures, boot-time probe failures, missing audio/SoC child devices, bad firmware/resource allocation, broken suspend/resume, or silent routing/clocking errors in board audio paths.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/soc/xilinx/xilinx.yaml` for the targeted schema and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/soc/xilinx/xilinx.yaml` against boards that instantiate it. There are no embedded examples, so real DTS users and schema-only checks are the main coverage. Cross-check compatible strings against driver `of_match_table` entries and inspect DTS users for register tuple counts, interrupt names, clocks/resets, supplies, DMA channels, graph endpoints, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/xilinx/xilinx.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/xilinx/xlnx,vcu-settings.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/xilinx/xlnx,vcu-settings.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/xilinx/xlnx,vcu-settings.yaml` defines the SoC support binding titled `Xilinx VCU Settings`. The Xilinx VCU Settings provides information about the configuration of the video codec unit. It constrains source DTS and compiled DTB hardware descriptions before Linux drivers consume the node.

## Important APIs, Types, and Functions
The API surface is the devicetree ABI rather than callable code. `compatible` uses an ordered compatible/fallback `items` sequence with 2 tokens: `xlnx,vcu-settings`, `syscon`. Top-level properties are `compatible`, `reg`. Required top-level properties are `compatible`, `reg`. Nested or reusable constraints include no unusually complex nested constraints beyond the top-level properties. The highest-risk contract area is compatible strings, register resources, child-node layout, clock/reset/power-domain hooks, and phandle references.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this file plus `$ref` targets, and enforces required properties, array cardinality, constants, enums, and no top-level conditionals. `dtbs_check` then matches compiled DTS nodes by `compatible`, `$nodename`, or parent-schema inclusion, descends into pattern-matched children, and applies `additionalProperties` or `unevaluatedProperties` closure. Runtime flow begins only after the DTB is loaded: Linux bus, SoC, ASoC, MFD, syscon, or firmware drivers bind from compatible strings and acquire the resources described here.

## State and Persistence Behavior
The YAML itself stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: compatible strings, property names, phandle names, register tuple ordering, child-node names, and examples become contracts in source DTS files and compiled DTBs. Runtime state is created by the matched kernel drivers after probe, including driver probe state, mapped control registers, child-device state, and SoC integration resources.

## Dependencies and Integration Points
Maintainers listed: Michael Tretter <kernel@pengutronix.de>. Schema dependencies include dt-schema core/meta schemas only. Integration points include Linux platform probing, syscon/regmap helpers, board-level DTS nodes, and SoC-specific drivers. The file also integrates with Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and source DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to compatible strings, register resources, child-node layout, clock/reset/power-domain hooks, and phandle references, drift between documented compatible strings and driver match tables, incorrect resource ordering, phandle names, or cell counts that block probe or misconfigure hardware. This schema rejects unknown top-level properties with `additionalProperties: false`. Regressions usually show up as schema-check failures, boot-time probe failures, missing audio/SoC child devices, bad firmware/resource allocation, broken suspend/resume, or silent routing/clocking errors in board audio paths.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/soc/xilinx/xlnx,vcu-settings.yaml` for the targeted schema and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/soc/xilinx/xlnx,vcu-settings.yaml` against boards that instantiate it. The schema has 1 embedded example; keep those examples valid under targeted binding checks. Cross-check compatible strings against driver `of_match_table` entries and inspect DTS users for register tuple counts, interrupt names, clocks/resets, supplies, DMA channels, graph endpoints, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/soc/xilinx/xlnx,vcu-settings.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/adi,adau1372.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/adi,adau1372.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/adi,adau1372.yaml` defines the audio codec or amplifier binding titled `Analog Devices ADAU1372 CODEC`. Analog Devices ADAU1372 four inputs and two outputs codec. It constrains source DTS and compiled DTB hardware descriptions before Linux drivers consume the node.

## Important APIs, Types, and Functions
The API surface is the devicetree ABI rather than callable code. `compatible` uses an `enum` of supported tokens with 1 token: `adi,adau1372`. Top-level properties are `compatible`, `reg`, `#sound-dai-cells`, `clocks`, `clock-names`, `powerdown-gpios`. Required top-level properties are `#sound-dai-cells`, `compatible`, `reg`, `clocks`, `clock-names`. Nested or reusable constraints include composition/conditionals: `allOf`; referenced schemas: `dai-common.yaml#`; notable enum/const values: `0`, `mclk`. The highest-risk contract area is compatible strings, bus address, reset/shutdown GPIOs, supplies, clocks, interrupts, DAI cells, widgets/routes, and chip-specific tuning properties.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this file plus `$ref` targets, and enforces required properties, array cardinality, constants, enums, and `allOf`. `dtbs_check` then matches compiled DTS nodes by `compatible`, `$nodename`, or parent-schema inclusion, descends into pattern-matched children, and applies `additionalProperties` or `unevaluatedProperties` closure. Runtime flow begins only after the DTB is loaded: Linux bus, SoC, ASoC, MFD, syscon, or firmware drivers bind from compatible strings and acquire the resources described here.

## State and Persistence Behavior
The YAML itself stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: compatible strings, property names, phandle names, register tuple ordering, child-node names, and examples become contracts in source DTS files and compiled DTBs. Runtime state is created by the matched kernel drivers after probe, including regmap cache, DAPM power state, bias levels, PLL/clock configuration, jack/interrupt state, and audio stream parameters owned by ASoC drivers.

## Dependencies and Integration Points
Maintainers listed: Alexandre Belloni <alexandre.belloni@bootlin.com>. Schema dependencies include `dai-common.yaml#`. Integration points include ASoC codec/component drivers, I2C/SPI/platform bus probing, DAPM graph construction, regulators, clocks, GPIO controls, and machine-driver links. The file also integrates with Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and source DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to compatible strings, bus address, reset/shutdown GPIOs, supplies, clocks, interrupts, DAI cells, widgets/routes, and chip-specific tuning properties, drift between documented compatible strings and driver match tables, incorrect resource ordering, phandle names, or cell counts that block probe or misconfigure hardware, variant-specific conditional branches accepting one SoC/chip while rejecting another. This schema closes composed schemas with `unevaluatedProperties: false`. Regressions usually show up as schema-check failures, boot-time probe failures, missing audio/SoC child devices, bad firmware/resource allocation, broken suspend/resume, or silent routing/clocking errors in board audio paths.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/sound/adi,adau1372.yaml` for the targeted schema and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/sound/adi,adau1372.yaml` against boards that instantiate it. The schema has 1 embedded example; keep those examples valid under targeted binding checks. Cross-check compatible strings against driver `of_match_table` entries and inspect DTS users for register tuple counts, interrupt names, clocks/resets, supplies, DMA channels, graph endpoints, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/adi,adau1372.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/adi,adau1373.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/adi,adau1373.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/adi,adau1373.yaml` defines the audio codec or amplifier binding titled `Analog Devices ADAU1373 CODEC`. Analog Devices ADAU1373 Low power codec with speaker and headphone amplifiers. It constrains source DTS and compiled DTB hardware descriptions before Linux drivers consume the node.

## Important APIs, Types, and Functions
The API surface is the devicetree ABI rather than callable code. `compatible` uses an `enum` of supported tokens with 1 token: `adi,adau1373`. Top-level properties are `compatible`, `reg`, `#sound-dai-cells`, `powerdown-gpios`, `adi,micbias1-microvolt`, `adi,micbias2-microvolt`, `adi,input1-differential`, `adi,input2-differential`, `adi,input3-differential`, `adi,input4-differential`, `adi,lineout-differential`, `adi,lineout-gnd-sense`, `adi,drc-settings`. Required top-level properties are `#sound-dai-cells`, `compatible`, `reg`. Nested or reusable constraints include composition/conditionals: `allOf`; referenced schemas: `/schemas/types.yaml#/definitions/uint8-array`, `dai-common.yaml#`; notable enum/const values: `1800000`, `2200000`, `2600000`, `2900000`, `0`. The highest-risk contract area is compatible strings, bus address, reset/shutdown GPIOs, supplies, clocks, interrupts, DAI cells, widgets/routes, and chip-specific tuning properties.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this file plus `$ref` targets, and enforces required properties, array cardinality, constants, enums, and `allOf`. `dtbs_check` then matches compiled DTS nodes by `compatible`, `$nodename`, or parent-schema inclusion, descends into pattern-matched children, and applies `additionalProperties` or `unevaluatedProperties` closure. Runtime flow begins only after the DTB is loaded: Linux bus, SoC, ASoC, MFD, syscon, or firmware drivers bind from compatible strings and acquire the resources described here.

## State and Persistence Behavior
The YAML itself stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: compatible strings, property names, phandle names, register tuple ordering, child-node names, and examples become contracts in source DTS files and compiled DTBs. Runtime state is created by the matched kernel drivers after probe, including regmap cache, DAPM power state, bias levels, PLL/clock configuration, jack/interrupt state, and audio stream parameters owned by ASoC drivers.

## Dependencies and Integration Points
Maintainers listed: Nuno Sá <nuno.sa@analog.com>. Schema dependencies include `/schemas/types.yaml#/definitions/uint8-array`, `dai-common.yaml#`. Integration points include ASoC codec/component drivers, I2C/SPI/platform bus probing, DAPM graph construction, regulators, clocks, GPIO controls, and machine-driver links. The file also integrates with Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and source DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to compatible strings, bus address, reset/shutdown GPIOs, supplies, clocks, interrupts, DAI cells, widgets/routes, and chip-specific tuning properties, drift between documented compatible strings and driver match tables, incorrect resource ordering, phandle names, or cell counts that block probe or misconfigure hardware, variant-specific conditional branches accepting one SoC/chip while rejecting another. This schema closes composed schemas with `unevaluatedProperties: false`. Regressions usually show up as schema-check failures, boot-time probe failures, missing audio/SoC child devices, bad firmware/resource allocation, broken suspend/resume, or silent routing/clocking errors in board audio paths.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/sound/adi,adau1373.yaml` for the targeted schema and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/sound/adi,adau1373.yaml` against boards that instantiate it. The schema has 1 embedded example; keep those examples valid under targeted binding checks. Cross-check compatible strings against driver `of_match_table` entries and inspect DTS users for register tuple counts, interrupt names, clocks/resets, supplies, DMA channels, graph endpoints, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/adi,adau1373.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/adi,adau17x1.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/adi,adau17x1.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/adi,adau17x1.yaml` defines the audio codec or amplifier binding titled `Analog Devices ADAU1361/ADAU1461/ADAU1761/ADAU1961/ADAU1381/ADAU1781 Codec`. It constrains source DTS and compiled DTB hardware descriptions through compatible strings, required resources, child-node topology, and shared schema references before Linux drivers consume the node.

## Important APIs, Types, and Functions
The API surface is the devicetree ABI rather than callable code. `compatible` uses an `enum` of supported tokens with 6 tokens: `adi,adau1361`, `adi,adau1381`, `adi,adau1461`, `adi,adau1761`, `adi,adau1781`, `adi,adau1961`. Top-level properties are `compatible`, `reg`, `clock-names`, `clocks`. Required top-level properties are `compatible`, `reg`. Nested or reusable constraints include notable enum/const values: `mclk`. The highest-risk contract area is compatible strings, bus address, reset/shutdown GPIOs, supplies, clocks, interrupts, DAI cells, widgets/routes, and chip-specific tuning properties.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this file plus `$ref` targets, and enforces required properties, array cardinality, constants, enums, and no top-level conditionals. `dtbs_check` then matches compiled DTS nodes by `compatible`, `$nodename`, or parent-schema inclusion, descends into pattern-matched children, and applies `additionalProperties` or `unevaluatedProperties` closure. Runtime flow begins only after the DTB is loaded: Linux bus, SoC, ASoC, MFD, syscon, or firmware drivers bind from compatible strings and acquire the resources described here.

## State and Persistence Behavior
The YAML itself stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: compatible strings, property names, phandle names, register tuple ordering, child-node names, and examples become contracts in source DTS files and compiled DTBs. Runtime state is created by the matched kernel drivers after probe, including regmap cache, DAPM power state, bias levels, PLL/clock configuration, jack/interrupt state, and audio stream parameters owned by ASoC drivers.

## Dependencies and Integration Points
Maintainers listed: Lars-Peter Clausen <lars@metafoo.de>. Schema dependencies include dt-schema core/meta schemas only. Integration points include ASoC codec/component drivers, I2C/SPI/platform bus probing, DAPM graph construction, regulators, clocks, GPIO controls, and machine-driver links. The file also integrates with Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and source DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to compatible strings, bus address, reset/shutdown GPIOs, supplies, clocks, interrupts, DAI cells, widgets/routes, and chip-specific tuning properties, drift between documented compatible strings and driver match tables, incorrect resource ordering, phandle names, or cell counts that block probe or misconfigure hardware. This schema rejects unknown top-level properties with `additionalProperties: false`. Regressions usually show up as schema-check failures, boot-time probe failures, missing audio/SoC child devices, bad firmware/resource allocation, broken suspend/resume, or silent routing/clocking errors in board audio paths.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/sound/adi,adau17x1.yaml` for the targeted schema and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/sound/adi,adau17x1.yaml` against boards that instantiate it. The schema has 1 embedded example; keep those examples valid under targeted binding checks. Cross-check compatible strings against driver `of_match_table` entries and inspect DTS users for register tuple counts, interrupt names, clocks/resets, supplies, DMA channels, graph endpoints, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/adi,adau17x1.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/adi,adau1977.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/adi,adau1977.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/adi,adau1977.yaml` defines the audio codec or amplifier binding titled `Analog Devices ADAU1977/ADAU1978/ADAU1979 Quad ADC with Diagnostics`. Analog Devices ADAU1977 and similar quad ADC with Diagnostics https://www.analog.com/media/en/technical-documentation/data-sheets/ADAU1977.pdf https://www.analog.com/media/en/technical-documentation/data-sheets/ADAU1978.pdf https://www.analog.com/media/en/technical-documentation/data-sheets/ADAU1979.pdf It constrains source DTS and compiled DTB hardware descriptions before Linux drivers consume the node.

## Important APIs, Types, and Functions
The API surface is the devicetree ABI rather than callable code. `compatible` uses an `enum` of supported tokens with 3 tokens: `adi,adau1977`, `adi,adau1978`, `adi,adau1979`. Top-level properties are `compatible`, `reg`, `#sound-dai-cells`, `reset-gpios`, `AVDD-supply`, `DVDD-supply`, `adi,micbias`. Required top-level properties are `reg`, `compatible`, `AVDD-supply`. Nested or reusable constraints include composition/conditionals: `allOf`; referenced schemas: `/schemas/spi/spi-peripheral-props.yaml#`, `/schemas/types.yaml#/definitions/uint32`, `dai-common.yaml#`; notable enum/const values: `0`, `1`, `2`, `3`, `4`, `5`, `6`, `7`, `8`. The highest-risk contract area is compatible strings, bus address, reset/shutdown GPIOs, supplies, clocks, interrupts, DAI cells, widgets/routes, and chip-specific tuning properties.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this file plus `$ref` targets, and enforces required properties, array cardinality, constants, enums, and `allOf`. `dtbs_check` then matches compiled DTS nodes by `compatible`, `$nodename`, or parent-schema inclusion, descends into pattern-matched children, and applies `additionalProperties` or `unevaluatedProperties` closure. Runtime flow begins only after the DTB is loaded: Linux bus, SoC, ASoC, MFD, syscon, or firmware drivers bind from compatible strings and acquire the resources described here.

## State and Persistence Behavior
The YAML itself stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: compatible strings, property names, phandle names, register tuple ordering, child-node names, and examples become contracts in source DTS files and compiled DTBs. Runtime state is created by the matched kernel drivers after probe, including regmap cache, DAPM power state, bias levels, PLL/clock configuration, jack/interrupt state, and audio stream parameters owned by ASoC drivers.

## Dependencies and Integration Points
Maintainers listed: Lars-Peter Clausen <lars@metafoo.de>, Bogdan Togorean <bogdan.togorean@analog.com>. Schema dependencies include `/schemas/spi/spi-peripheral-props.yaml#`, `/schemas/types.yaml#/definitions/uint32`, `dai-common.yaml#`. Integration points include ASoC codec/component drivers, I2C/SPI/platform bus probing, DAPM graph construction, regulators, clocks, GPIO controls, and machine-driver links. The file also integrates with Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and source DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to compatible strings, bus address, reset/shutdown GPIOs, supplies, clocks, interrupts, DAI cells, widgets/routes, and chip-specific tuning properties, drift between documented compatible strings and driver match tables, incorrect resource ordering, phandle names, or cell counts that block probe or misconfigure hardware, variant-specific conditional branches accepting one SoC/chip while rejecting another. This schema closes composed schemas with `unevaluatedProperties: false`. Regressions usually show up as schema-check failures, boot-time probe failures, missing audio/SoC child devices, bad firmware/resource allocation, broken suspend/resume, or silent routing/clocking errors in board audio paths.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/sound/adi,adau1977.yaml` for the targeted schema and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/sound/adi,adau1977.yaml` against boards that instantiate it. The schema has 2 embedded examples; keep those examples valid under targeted binding checks. Cross-check compatible strings against driver `of_match_table` entries and inspect DTS users for register tuple counts, interrupt names, clocks/resets, supplies, DMA channels, graph endpoints, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/adi,adau1977.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/adi,adau7002.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/adi,adau7002.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/adi,adau7002.yaml` defines the audio codec or amplifier binding titled `Analog Devices ADAU7002 Stereo PDM-to-I2S/TDM Converter`. It constrains source DTS and compiled DTB hardware descriptions through compatible strings, required resources, child-node topology, and shared schema references before Linux drivers consume the node.

## Important APIs, Types, and Functions
The API surface is the devicetree ABI rather than callable code. `compatible` uses a single `const` token with 1 token: `adi,adau7002`. Top-level properties are `compatible`, `IOVDD-supply`, `wakeup-delay-ms`. Required top-level properties are `compatible`. Nested or reusable constraints include composition/conditionals: `allOf`; referenced schemas: `dai-common.yaml#`. The highest-risk contract area is compatible strings, bus address, reset/shutdown GPIOs, supplies, clocks, interrupts, DAI cells, widgets/routes, and chip-specific tuning properties.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this file plus `$ref` targets, and enforces required properties, array cardinality, constants, enums, and `allOf`. `dtbs_check` then matches compiled DTS nodes by `compatible`, `$nodename`, or parent-schema inclusion, descends into pattern-matched children, and applies `additionalProperties` or `unevaluatedProperties` closure. Runtime flow begins only after the DTB is loaded: Linux bus, SoC, ASoC, MFD, syscon, or firmware drivers bind from compatible strings and acquire the resources described here.

## State and Persistence Behavior
The YAML itself stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: compatible strings, property names, phandle names, register tuple ordering, child-node names, and examples become contracts in source DTS files and compiled DTBs. Runtime state is created by the matched kernel drivers after probe, including regmap cache, DAPM power state, bias levels, PLL/clock configuration, jack/interrupt state, and audio stream parameters owned by ASoC drivers.

## Dependencies and Integration Points
Maintainers listed: Krzysztof Kozlowski <krzk@kernel.org>. Schema dependencies include `dai-common.yaml#`. Integration points include ASoC codec/component drivers, I2C/SPI/platform bus probing, DAPM graph construction, regulators, clocks, GPIO controls, and machine-driver links. The file also integrates with Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and source DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to compatible strings, bus address, reset/shutdown GPIOs, supplies, clocks, interrupts, DAI cells, widgets/routes, and chip-specific tuning properties, drift between documented compatible strings and driver match tables, incorrect resource ordering, phandle names, or cell counts that block probe or misconfigure hardware, variant-specific conditional branches accepting one SoC/chip while rejecting another. This schema closes composed schemas with `unevaluatedProperties: false`. Regressions usually show up as schema-check failures, boot-time probe failures, missing audio/SoC child devices, bad firmware/resource allocation, broken suspend/resume, or silent routing/clocking errors in board audio paths.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/sound/adi,adau7002.yaml` for the targeted schema and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/sound/adi,adau7002.yaml` against boards that instantiate it. The schema has 1 embedded example; keep those examples valid under targeted binding checks. Cross-check compatible strings against driver `of_match_table` entries and inspect DTS users for register tuple counts, interrupt names, clocks/resets, supplies, DMA channels, graph endpoints, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/adi,adau7002.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/adi,adau7118.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/adi,adau7118.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/adi,adau7118.yaml` defines the audio codec or amplifier binding titled `Analog Devices ADAU7118 8 Channel PDM to I2S/TDM Converter`. Analog Devices ADAU7118 8 Channel PDM to I2S/TDM Converter over I2C or HW standalone mode. It constrains source DTS and compiled DTB hardware descriptions before Linux drivers consume the node.

## Important APIs, Types, and Functions
The API surface is the devicetree ABI rather than callable code. `compatible` uses an `enum` of supported tokens with 1 token: `adi,adau7118`. Top-level properties are `compatible`, `reg`, `#sound-dai-cells`, `iovdd-supply`, `dvdd-supply`, `adi,decimation-ratio`, `adi,pdm-clk-map`. Required top-level properties are `#sound-dai-cells`, `compatible`, `iovdd-supply`, `dvdd-supply`. Nested or reusable constraints include composition/conditionals: `allOf`; referenced schemas: `/schemas/types.yaml#/definitions/uint32`, `/schemas/types.yaml#/definitions/uint32-array`, `dai-common.yaml#`; notable enum/const values: `64`, `32`, `16`, `0`. The highest-risk contract area is compatible strings, bus address, reset/shutdown GPIOs, supplies, clocks, interrupts, DAI cells, widgets/routes, and chip-specific tuning properties.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this file plus `$ref` targets, and enforces required properties, array cardinality, constants, enums, and `allOf`. `dtbs_check` then matches compiled DTS nodes by `compatible`, `$nodename`, or parent-schema inclusion, descends into pattern-matched children, and applies `additionalProperties` or `unevaluatedProperties` closure. Runtime flow begins only after the DTB is loaded: Linux bus, SoC, ASoC, MFD, syscon, or firmware drivers bind from compatible strings and acquire the resources described here.

## State and Persistence Behavior
The YAML itself stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: compatible strings, property names, phandle names, register tuple ordering, child-node names, and examples become contracts in source DTS files and compiled DTBs. Runtime state is created by the matched kernel drivers after probe, including regmap cache, DAPM power state, bias levels, PLL/clock configuration, jack/interrupt state, and audio stream parameters owned by ASoC drivers.

## Dependencies and Integration Points
Maintainers listed: Nuno Sá <nuno.sa@analog.com>. Schema dependencies include `/schemas/types.yaml#/definitions/uint32`, `/schemas/types.yaml#/definitions/uint32-array`, `dai-common.yaml#`. Integration points include ASoC codec/component drivers, I2C/SPI/platform bus probing, DAPM graph construction, regulators, clocks, GPIO controls, and machine-driver links. The file also integrates with Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and source DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to compatible strings, bus address, reset/shutdown GPIOs, supplies, clocks, interrupts, DAI cells, widgets/routes, and chip-specific tuning properties, drift between documented compatible strings and driver match tables, incorrect resource ordering, phandle names, or cell counts that block probe or misconfigure hardware, variant-specific conditional branches accepting one SoC/chip while rejecting another. This schema closes composed schemas with `unevaluatedProperties: false`. Regressions usually show up as schema-check failures, boot-time probe failures, missing audio/SoC child devices, bad firmware/resource allocation, broken suspend/resume, or silent routing/clocking errors in board audio paths.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/sound/adi,adau7118.yaml` for the targeted schema and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/sound/adi,adau7118.yaml` against boards that instantiate it. The schema has 1 embedded example; keep those examples valid under targeted binding checks. Cross-check compatible strings against driver `of_match_table` entries and inspect DTS users for register tuple counts, interrupt names, clocks/resets, supplies, DMA channels, graph endpoints, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/adi,adau7118.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/adi,max98388.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/adi,max98388.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/adi,max98388.yaml` defines the audio codec or amplifier binding titled `Analog Devices MAX98388 Speaker Amplifier`. The MAX98388 is a mono Class-D speaker amplifier with I/V feedback. It constrains source DTS and compiled DTB hardware descriptions before Linux drivers consume the node.

## Important APIs, Types, and Functions
The API surface is the devicetree ABI rather than callable code. `compatible` uses an `enum` of supported tokens with 1 token: `adi,max98388`. Top-level properties are `compatible`, `reg`, `#sound-dai-cells`, `adi,vmon-slot-no`, `adi,imon-slot-no`, `adi,interleave-mode`, `reset-gpios`. Required top-level properties are `compatible`, `reg`, `#sound-dai-cells`. Nested or reusable constraints include composition/conditionals: `allOf`; referenced schemas: `/schemas/types.yaml#/definitions/uint32`, `dai-common.yaml#`; notable enum/const values: `0`. The highest-risk contract area is compatible strings, bus address, reset/shutdown GPIOs, supplies, clocks, interrupts, DAI cells, widgets/routes, and chip-specific tuning properties.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this file plus `$ref` targets, and enforces required properties, array cardinality, constants, enums, and `allOf`. `dtbs_check` then matches compiled DTS nodes by `compatible`, `$nodename`, or parent-schema inclusion, descends into pattern-matched children, and applies `additionalProperties` or `unevaluatedProperties` closure. Runtime flow begins only after the DTB is loaded: Linux bus, SoC, ASoC, MFD, syscon, or firmware drivers bind from compatible strings and acquire the resources described here.

## State and Persistence Behavior
The YAML itself stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: compatible strings, property names, phandle names, register tuple ordering, child-node names, and examples become contracts in source DTS files and compiled DTBs. Runtime state is created by the matched kernel drivers after probe, including regmap cache, DAPM power state, bias levels, PLL/clock configuration, jack/interrupt state, and audio stream parameters owned by ASoC drivers.

## Dependencies and Integration Points
Maintainers listed: Ryan Lee <ryans.lee@analog.com>. Schema dependencies include `/schemas/types.yaml#/definitions/uint32`, `dai-common.yaml#`. Integration points include ASoC codec/component drivers, I2C/SPI/platform bus probing, DAPM graph construction, regulators, clocks, GPIO controls, and machine-driver links. The file also integrates with Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and source DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to compatible strings, bus address, reset/shutdown GPIOs, supplies, clocks, interrupts, DAI cells, widgets/routes, and chip-specific tuning properties, drift between documented compatible strings and driver match tables, incorrect resource ordering, phandle names, or cell counts that block probe or misconfigure hardware, variant-specific conditional branches accepting one SoC/chip while rejecting another. This schema closes composed schemas with `unevaluatedProperties: false`. Regressions usually show up as schema-check failures, boot-time probe failures, missing audio/SoC child devices, bad firmware/resource allocation, broken suspend/resume, or silent routing/clocking errors in board audio paths.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/sound/adi,max98388.yaml` for the targeted schema and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/sound/adi,max98388.yaml` against boards that instantiate it. The schema has 1 embedded example; keep those examples valid under targeted binding checks. Cross-check compatible strings against driver `of_match_table` entries and inspect DTS users for register tuple counts, interrupt names, clocks/resets, supplies, DMA channels, graph endpoints, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/adi,max98388.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/adi,max98396.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/adi,max98396.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/adi,max98396.yaml` defines the audio codec or amplifier binding titled `Analog Devices MAX98396 Speaker Amplifier`. The MAX98396 is a mono Class-DG speaker amplifier with I/V sense. It constrains source DTS and compiled DTB hardware descriptions before Linux drivers consume the node.

## Important APIs, Types, and Functions
The API surface is the devicetree ABI rather than callable code. `compatible` uses an `enum` of supported tokens with 2 tokens: `adi,max98396`, `adi,max98397`. Top-level properties are `compatible`, `reg`, `avdd-supply`, `dvdd-supply`, `dvddio-supply`, `pvdd-supply`, `vbat-supply`, `adi,vmon-slot-no`, `adi,imon-slot-no`, `adi,spkfb-slot-no`, `adi,bypass-slot-no`, `adi,interleave-mode`, `adi,dmon-stuck-enable`, `adi,dmon-stuck-threshold-bits`, `adi,dmon-magnitude-enable`, `adi,dmon-magnitude-threshold-bits`, `adi,dmon-duration-ms`, `reset-gpios`. Required top-level properties are `compatible`, `reg`. Nested or reusable constraints include referenced schemas: `/schemas/types.yaml#/definitions/uint32`; notable enum/const values: `9`, `11`, `13`, `15`, `2`, `3`, `4`, `5`, `64`, `256`, `1024`, `4096`. The highest-risk contract area is compatible strings, bus address, reset/shutdown GPIOs, supplies, clocks, interrupts, DAI cells, widgets/routes, and chip-specific tuning properties.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this file plus `$ref` targets, and enforces required properties, array cardinality, constants, enums, and no top-level conditionals. `dtbs_check` then matches compiled DTS nodes by `compatible`, `$nodename`, or parent-schema inclusion, descends into pattern-matched children, and applies `additionalProperties` or `unevaluatedProperties` closure. Runtime flow begins only after the DTB is loaded: Linux bus, SoC, ASoC, MFD, syscon, or firmware drivers bind from compatible strings and acquire the resources described here.

## State and Persistence Behavior
The YAML itself stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: compatible strings, property names, phandle names, register tuple ordering, child-node names, and examples become contracts in source DTS files and compiled DTBs. Runtime state is created by the matched kernel drivers after probe, including regmap cache, DAPM power state, bias levels, PLL/clock configuration, jack/interrupt state, and audio stream parameters owned by ASoC drivers.

## Dependencies and Integration Points
Maintainers listed: Ryan Lee <ryans.lee@analog.com>. Schema dependencies include `/schemas/types.yaml#/definitions/uint32`. Integration points include ASoC codec/component drivers, I2C/SPI/platform bus probing, DAPM graph construction, regulators, clocks, GPIO controls, and machine-driver links. The file also integrates with Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and source DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to compatible strings, bus address, reset/shutdown GPIOs, supplies, clocks, interrupts, DAI cells, widgets/routes, and chip-specific tuning properties, drift between documented compatible strings and driver match tables, incorrect resource ordering, phandle names, or cell counts that block probe or misconfigure hardware. This schema rejects unknown top-level properties with `additionalProperties: false`. Regressions usually show up as schema-check failures, boot-time probe failures, missing audio/SoC child devices, bad firmware/resource allocation, broken suspend/resume, or silent routing/clocking errors in board audio paths.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/sound/adi,max98396.yaml` for the targeted schema and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/sound/adi,max98396.yaml` against boards that instantiate it. The schema has 1 embedded example; keep those examples valid under targeted binding checks. Cross-check compatible strings against driver `of_match_table` entries and inspect DTS users for register tuple counts, interrupt names, clocks/resets, supplies, DMA channels, graph endpoints, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/adi,max98396.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/adi,ssm2305.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/adi,ssm2305.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/adi,ssm2305.yaml` defines the audio codec or amplifier binding titled `Analog Devices SSM2305 Class-D Speaker Amplifier`. The SSM2305 is a filterless, high efficiency, mono 2.8 W Class-D audio amplifier with a micropower shutdown mode controlled via a dedicated active-low GPIO pin. It constrains source DTS and compiled DTB hardware descriptions before Linux drivers consume the node.

## Important APIs, Types, and Functions
The API surface is the devicetree ABI rather than callable code. `compatible` uses a single `const` token with 1 token: `adi,ssm2305`. Top-level properties are `compatible`, `shutdown-gpios`. Required top-level properties are `compatible`, `shutdown-gpios`. Nested or reusable constraints include composition/conditionals: `allOf`; referenced schemas: `dai-common.yaml#`. The highest-risk contract area is compatible strings, bus address, reset/shutdown GPIOs, supplies, clocks, interrupts, DAI cells, widgets/routes, and chip-specific tuning properties.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this file plus `$ref` targets, and enforces required properties, array cardinality, constants, enums, and `allOf`. `dtbs_check` then matches compiled DTS nodes by `compatible`, `$nodename`, or parent-schema inclusion, descends into pattern-matched children, and applies `additionalProperties` or `unevaluatedProperties` closure. Runtime flow begins only after the DTB is loaded: Linux bus, SoC, ASoC, MFD, syscon, or firmware drivers bind from compatible strings and acquire the resources described here.

## State and Persistence Behavior
The YAML itself stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: compatible strings, property names, phandle names, register tuple ordering, child-node names, and examples become contracts in source DTS files and compiled DTBs. Runtime state is created by the matched kernel drivers after probe, including regmap cache, DAPM power state, bias levels, PLL/clock configuration, jack/interrupt state, and audio stream parameters owned by ASoC drivers.

## Dependencies and Integration Points
Maintainers listed: Lars-Peter Clausen <lars@metafoo.de>. Schema dependencies include `dai-common.yaml#`. Integration points include ASoC codec/component drivers, I2C/SPI/platform bus probing, DAPM graph construction, regulators, clocks, GPIO controls, and machine-driver links. The file also integrates with Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and source DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to compatible strings, bus address, reset/shutdown GPIOs, supplies, clocks, interrupts, DAI cells, widgets/routes, and chip-specific tuning properties, drift between documented compatible strings and driver match tables, incorrect resource ordering, phandle names, or cell counts that block probe or misconfigure hardware, variant-specific conditional branches accepting one SoC/chip while rejecting another. This schema closes composed schemas with `unevaluatedProperties: false`. Regressions usually show up as schema-check failures, boot-time probe failures, missing audio/SoC child devices, bad firmware/resource allocation, broken suspend/resume, or silent routing/clocking errors in board audio paths.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/sound/adi,ssm2305.yaml` for the targeted schema and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/sound/adi,ssm2305.yaml` against boards that instantiate it. The schema has 1 embedded example; keep those examples valid under targeted binding checks. Cross-check compatible strings against driver `of_match_table` entries and inspect DTS users for register tuple counts, interrupt names, clocks/resets, supplies, DMA channels, graph endpoints, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/adi,ssm2305.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/adi,ssm2518.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/adi,ssm2518.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/adi,ssm2518.yaml` defines the audio codec or amplifier binding titled `Analog Devices SSM2518 audio amplifier`. It constrains source DTS and compiled DTB hardware descriptions through compatible strings, required resources, child-node topology, and shared schema references before Linux drivers consume the node.

## Important APIs, Types, and Functions
The API surface is the devicetree ABI rather than callable code. `compatible` uses a single `const` token with 1 token: `adi,ssm2518`. Top-level properties are `compatible`, `reg`, `gpios`. Required top-level properties are `compatible`, `reg`. Nested or reusable constraints include composition/conditionals: `allOf`; referenced schemas: `dai-common.yaml#`. The highest-risk contract area is compatible strings, bus address, reset/shutdown GPIOs, supplies, clocks, interrupts, DAI cells, widgets/routes, and chip-specific tuning properties.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this file plus `$ref` targets, and enforces required properties, array cardinality, constants, enums, and `allOf`. `dtbs_check` then matches compiled DTS nodes by `compatible`, `$nodename`, or parent-schema inclusion, descends into pattern-matched children, and applies `additionalProperties` or `unevaluatedProperties` closure. Runtime flow begins only after the DTB is loaded: Linux bus, SoC, ASoC, MFD, syscon, or firmware drivers bind from compatible strings and acquire the resources described here.

## State and Persistence Behavior
The YAML itself stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: compatible strings, property names, phandle names, register tuple ordering, child-node names, and examples become contracts in source DTS files and compiled DTBs. Runtime state is created by the matched kernel drivers after probe, including regmap cache, DAPM power state, bias levels, PLL/clock configuration, jack/interrupt state, and audio stream parameters owned by ASoC drivers.

## Dependencies and Integration Points
Maintainers listed: Lars-Peter Clausen <lars@metafoo.de>. Schema dependencies include `dai-common.yaml#`. Integration points include ASoC codec/component drivers, I2C/SPI/platform bus probing, DAPM graph construction, regulators, clocks, GPIO controls, and machine-driver links. The file also integrates with Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and source DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to compatible strings, bus address, reset/shutdown GPIOs, supplies, clocks, interrupts, DAI cells, widgets/routes, and chip-specific tuning properties, drift between documented compatible strings and driver match tables, incorrect resource ordering, phandle names, or cell counts that block probe or misconfigure hardware, variant-specific conditional branches accepting one SoC/chip while rejecting another. This schema closes composed schemas with `unevaluatedProperties: false`. Regressions usually show up as schema-check failures, boot-time probe failures, missing audio/SoC child devices, bad firmware/resource allocation, broken suspend/resume, or silent routing/clocking errors in board audio paths.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/sound/adi,ssm2518.yaml` for the targeted schema and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/sound/adi,ssm2518.yaml` against boards that instantiate it. The schema has 1 embedded example; keep those examples valid under targeted binding checks. Cross-check compatible strings against driver `of_match_table` entries and inspect DTS users for register tuple counts, interrupt names, clocks/resets, supplies, DMA channels, graph endpoints, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/adi,ssm2518.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/allwinner,sun4i-a10-codec.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/allwinner,sun4i-a10-codec.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/allwinner,sun4i-a10-codec.yaml` defines the audio codec or amplifier binding titled `Allwinner A10 Codec`. It constrains source DTS and compiled DTB hardware descriptions through compatible strings, required resources, child-node topology, and shared schema references before Linux drivers consume the node.

## Important APIs, Types, and Functions
The API surface is the devicetree ABI rather than callable code. `compatible` uses an `enum` of supported tokens with 8 tokens: `allwinner,sun4i-a10-codec`, `allwinner,sun6i-a31-codec`, `allwinner,sun7i-a20-codec`, `allwinner,sun8i-a23-codec`, `allwinner,sun8i-h3-codec`, `allwinner,sun8i-v3s-codec`, `allwinner,sun50i-h616-codec`, `allwinner,suniv-f1c100s-codec`. Top-level properties are `#sound-dai-cells`, `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `dmas`, `dma-names`, `resets`, `allwinner,audio-routing`, `allwinner,codec-analog-controls`, `allwinner,pa-gpios`, `hp-det-gpios`. Required top-level properties are `#sound-dai-cells`, `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `dmas`, `dma-names`. Nested or reusable constraints include composition/conditionals: `allOf`; referenced schemas: `/schemas/types.yaml#/definitions/non-unique-string-array`, `/schemas/types.yaml#/definitions/phandle`, `dai-common.yaml#`; notable enum/const values: `HP`, `HPCOM`, `LINEIN`, `LINEOUT`, `MIC1`, `MIC2`, `MIC3`, `MIC`, `HBIAS`, `MBIAS`, `Headphone`, `Headset Mic`, `Line In`, `Line Out`, `Right FM In`, `Left FM In`, and 7 more. The highest-risk contract area is compatible strings, bus address, reset/shutdown GPIOs, supplies, clocks, interrupts, DAI cells, widgets/routes, and chip-specific tuning properties.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this file plus `$ref` targets, and enforces required properties, array cardinality, constants, enums, and `allOf`. `dtbs_check` then matches compiled DTS nodes by `compatible`, `$nodename`, or parent-schema inclusion, descends into pattern-matched children, and applies `additionalProperties` or `unevaluatedProperties` closure. Runtime flow begins only after the DTB is loaded: Linux bus, SoC, ASoC, MFD, syscon, or firmware drivers bind from compatible strings and acquire the resources described here.

## State and Persistence Behavior
The YAML itself stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: compatible strings, property names, phandle names, register tuple ordering, child-node names, and examples become contracts in source DTS files and compiled DTBs. Runtime state is created by the matched kernel drivers after probe, including regmap cache, DAPM power state, bias levels, PLL/clock configuration, jack/interrupt state, and audio stream parameters owned by ASoC drivers.

## Dependencies and Integration Points
Maintainers listed: Chen-Yu Tsai <wens@csie.org>, Maxime Ripard <mripard@kernel.org>. Schema dependencies include `/schemas/types.yaml#/definitions/non-unique-string-array`, `/schemas/types.yaml#/definitions/phandle`, `dai-common.yaml#`. Integration points include ASoC codec/component drivers, I2C/SPI/platform bus probing, DAPM graph construction, regulators, clocks, GPIO controls, and machine-driver links. The file also integrates with Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and source DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to compatible strings, bus address, reset/shutdown GPIOs, supplies, clocks, interrupts, DAI cells, widgets/routes, and chip-specific tuning properties, drift between documented compatible strings and driver match tables, incorrect resource ordering, phandle names, or cell counts that block probe or misconfigure hardware, variant-specific conditional branches accepting one SoC/chip while rejecting another. This schema closes composed schemas with `unevaluatedProperties: false`. Regressions usually show up as schema-check failures, boot-time probe failures, missing audio/SoC child devices, bad firmware/resource allocation, broken suspend/resume, or silent routing/clocking errors in board audio paths.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/sound/allwinner,sun4i-a10-codec.yaml` for the targeted schema and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/sound/allwinner,sun4i-a10-codec.yaml` against boards that instantiate it. The schema has 2 embedded examples; keep those examples valid under targeted binding checks. Cross-check compatible strings against driver `of_match_table` entries and inspect DTS users for register tuple counts, interrupt names, clocks/resets, supplies, DMA channels, graph endpoints, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/allwinner,sun4i-a10-codec.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/allwinner,sun4i-a10-i2s.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/allwinner,sun4i-a10-i2s.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/allwinner,sun4i-a10-i2s.yaml` defines the audio controller or sound-card binding titled `Allwinner A10 I2S Controller`. It constrains source DTS and compiled DTB hardware descriptions through compatible strings, required resources, child-node topology, and shared schema references before Linux drivers consume the node.

## Important APIs, Types, and Functions
The API surface is the devicetree ABI rather than callable code. `compatible` uses `oneOf` with 11 branches with 12 tokens: `allwinner,sun4i-a10-i2s`, `allwinner,sun6i-a31-i2s`, `allwinner,sun8i-a83t-i2s`, `allwinner,sun8i-h3-i2s`, `allwinner,sun8i-r40-i2s`, `allwinner,sun8i-v3-i2s`, `allwinner,sun50i-a64-codec-i2s`, `allwinner,sun50i-a64-i2s`, `allwinner,sun50i-h6-i2s`, `allwinner,sun50i-r329-i2s`, `allwinner,sun20i-d1-i2s`, `allwinner,sun55i-a523-i2s`. Top-level properties are `#sound-dai-cells`, `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `dmas`, `dma-names`, `resets`. Required top-level properties are `#sound-dai-cells`, `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `dmas`, `dma-names`. Nested or reusable constraints include composition/conditionals: `allOf`; referenced schemas: `dai-common.yaml#`; notable enum/const values: `0`, `apb`, `mod`, `rx`, `tx`. The highest-risk contract area is register and interrupt resources, clocks/resets, DMA channels, sound-dai cells, graph ports/endpoints, routing, and SoC-specific compatible strings.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this file plus `$ref` targets, and enforces required properties, array cardinality, constants, enums, and `allOf`. `dtbs_check` then matches compiled DTS nodes by `compatible`, `$nodename`, or parent-schema inclusion, descends into pattern-matched children, and applies `additionalProperties` or `unevaluatedProperties` closure. Runtime flow begins only after the DTB is loaded: Linux bus, SoC, ASoC, MFD, syscon, or firmware drivers bind from compatible strings and acquire the resources described here.

## State and Persistence Behavior
The YAML itself stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: compatible strings, property names, phandle names, register tuple ordering, child-node names, and examples become contracts in source DTS files and compiled DTBs. Runtime state is created by the matched kernel drivers after probe, including DAI/controller probe state, DMA stream state, clocking, reset state, and sound-card topology owned by ASoC runtime drivers.

## Dependencies and Integration Points
Maintainers listed: Chen-Yu Tsai <wens@csie.org>, Maxime Ripard <mripard@kernel.org>. Schema dependencies include `dai-common.yaml#`. Integration points include ASoC CPU DAI drivers, platform DMA engines, machine drivers, graph/simple-card parsing, clocks/resets, pinctrl, and board DTS sound links. The file also integrates with Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and source DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to register and interrupt resources, clocks/resets, DMA channels, sound-dai cells, graph ports/endpoints, routing, and SoC-specific compatible strings, drift between documented compatible strings and driver match tables, incorrect resource ordering, phandle names, or cell counts that block probe or misconfigure hardware, variant-specific conditional branches accepting one SoC/chip while rejecting another, large compatible sets where fallback ordering can drift over hardware generations. This schema closes composed schemas with `unevaluatedProperties: false`. Regressions usually show up as schema-check failures, boot-time probe failures, missing audio/SoC child devices, bad firmware/resource allocation, broken suspend/resume, or silent routing/clocking errors in board audio paths.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/sound/allwinner,sun4i-a10-i2s.yaml` for the targeted schema and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/sound/allwinner,sun4i-a10-i2s.yaml` against boards that instantiate it. The schema has 1 embedded example; keep those examples valid under targeted binding checks. Cross-check compatible strings against driver `of_match_table` entries and inspect DTS users for register tuple counts, interrupt names, clocks/resets, supplies, DMA channels, graph endpoints, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/allwinner,sun4i-a10-i2s.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/allwinner,sun4i-a10-spdif.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/allwinner,sun4i-a10-spdif.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/allwinner,sun4i-a10-spdif.yaml` defines the audio controller or sound-card binding titled `Allwinner A10 S/PDIF Controller`. It constrains source DTS and compiled DTB hardware descriptions through compatible strings, required resources, child-node topology, and shared schema references before Linux drivers consume the node.

## Important APIs, Types, and Functions
The API surface is the devicetree ABI rather than callable code. `compatible` uses `oneOf` with 8 branches with 8 tokens: `allwinner,sun4i-a10-spdif`, `allwinner,sun6i-a31-spdif`, `allwinner,sun8i-h3-spdif`, `allwinner,sun50i-h6-spdif`, `allwinner,sun50i-h616-spdif`, `allwinner,sun55i-a523-spdif`, `allwinner,sun8i-a83t-spdif`, `allwinner,sun50i-a64-spdif`. Top-level properties are `#sound-dai-cells`, `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `dmas`, `dma-names`, `resets`. Required top-level properties are `#sound-dai-cells`, `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `dmas`, `dma-names`. Nested or reusable constraints include composition/conditionals: `allOf`; referenced schemas: `dai-common.yaml#`; notable enum/const values: `0`, `tx`, `rx`, `apb`, `spdif`. The highest-risk contract area is register and interrupt resources, clocks/resets, DMA channels, sound-dai cells, graph ports/endpoints, routing, and SoC-specific compatible strings.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this file plus `$ref` targets, and enforces required properties, array cardinality, constants, enums, and `allOf`. `dtbs_check` then matches compiled DTS nodes by `compatible`, `$nodename`, or parent-schema inclusion, descends into pattern-matched children, and applies `additionalProperties` or `unevaluatedProperties` closure. Runtime flow begins only after the DTB is loaded: Linux bus, SoC, ASoC, MFD, syscon, or firmware drivers bind from compatible strings and acquire the resources described here.

## State and Persistence Behavior
The YAML itself stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: compatible strings, property names, phandle names, register tuple ordering, child-node names, and examples become contracts in source DTS files and compiled DTBs. Runtime state is created by the matched kernel drivers after probe, including DAI/controller probe state, DMA stream state, clocking, reset state, and sound-card topology owned by ASoC runtime drivers.

## Dependencies and Integration Points
Maintainers listed: Chen-Yu Tsai <wens@csie.org>, Liam Girdwood <lgirdwood@gmail.com>, Mark Brown <broonie@kernel.org>, Maxime Ripard <mripard@kernel.org>. Schema dependencies include `dai-common.yaml#`. Integration points include ASoC CPU DAI drivers, platform DMA engines, machine drivers, graph/simple-card parsing, clocks/resets, pinctrl, and board DTS sound links. The file also integrates with Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and source DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to register and interrupt resources, clocks/resets, DMA channels, sound-dai cells, graph ports/endpoints, routing, and SoC-specific compatible strings, drift between documented compatible strings and driver match tables, incorrect resource ordering, phandle names, or cell counts that block probe or misconfigure hardware, variant-specific conditional branches accepting one SoC/chip while rejecting another. This schema closes composed schemas with `unevaluatedProperties: false`. Regressions usually show up as schema-check failures, boot-time probe failures, missing audio/SoC child devices, bad firmware/resource allocation, broken suspend/resume, or silent routing/clocking errors in board audio paths.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/sound/allwinner,sun4i-a10-spdif.yaml` for the targeted schema and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/sound/allwinner,sun4i-a10-spdif.yaml` against boards that instantiate it. The schema has 1 embedded example; keep those examples valid under targeted binding checks. Cross-check compatible strings against driver `of_match_table` entries and inspect DTS users for register tuple counts, interrupt names, clocks/resets, supplies, DMA channels, graph endpoints, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/allwinner,sun4i-a10-spdif.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/allwinner,sun50i-a64-codec-analog.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/allwinner,sun50i-a64-codec-analog.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/allwinner,sun50i-a64-codec-analog.yaml` defines the audio codec or amplifier binding titled `Allwinner A64 Analog Codec`. It constrains source DTS and compiled DTB hardware descriptions through compatible strings, required resources, child-node topology, and shared schema references before Linux drivers consume the node.

## Important APIs, Types, and Functions
The API surface is the devicetree ABI rather than callable code. `compatible` uses a single `const` token with 1 token: `allwinner,sun50i-a64-codec-analog`. Top-level properties are `compatible`, `reg`, `cpvdd-supply`, `allwinner,internal-bias-resistor`. Required top-level properties are `compatible`, `reg`, `cpvdd-supply`. Nested or reusable constraints include no unusually complex nested constraints beyond the top-level properties. The highest-risk contract area is compatible strings, bus address, reset/shutdown GPIOs, supplies, clocks, interrupts, DAI cells, widgets/routes, and chip-specific tuning properties.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this file plus `$ref` targets, and enforces required properties, array cardinality, constants, enums, and no top-level conditionals. `dtbs_check` then matches compiled DTS nodes by `compatible`, `$nodename`, or parent-schema inclusion, descends into pattern-matched children, and applies `additionalProperties` or `unevaluatedProperties` closure. Runtime flow begins only after the DTB is loaded: Linux bus, SoC, ASoC, MFD, syscon, or firmware drivers bind from compatible strings and acquire the resources described here.

## State and Persistence Behavior
The YAML itself stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: compatible strings, property names, phandle names, register tuple ordering, child-node names, and examples become contracts in source DTS files and compiled DTBs. Runtime state is created by the matched kernel drivers after probe, including regmap cache, DAPM power state, bias levels, PLL/clock configuration, jack/interrupt state, and audio stream parameters owned by ASoC drivers.

## Dependencies and Integration Points
Maintainers listed: Chen-Yu Tsai <wens@csie.org>, Maxime Ripard <mripard@kernel.org>. Schema dependencies include dt-schema core/meta schemas only. Integration points include ASoC codec/component drivers, I2C/SPI/platform bus probing, DAPM graph construction, regulators, clocks, GPIO controls, and machine-driver links. The file also integrates with Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and source DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to compatible strings, bus address, reset/shutdown GPIOs, supplies, clocks, interrupts, DAI cells, widgets/routes, and chip-specific tuning properties, drift between documented compatible strings and driver match tables, incorrect resource ordering, phandle names, or cell counts that block probe or misconfigure hardware. This schema rejects unknown top-level properties with `additionalProperties: false`. Regressions usually show up as schema-check failures, boot-time probe failures, missing audio/SoC child devices, bad firmware/resource allocation, broken suspend/resume, or silent routing/clocking errors in board audio paths.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/sound/allwinner,sun50i-a64-codec-analog.yaml` for the targeted schema and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/sound/allwinner,sun50i-a64-codec-analog.yaml` against boards that instantiate it. The schema has 1 embedded example; keep those examples valid under targeted binding checks. Cross-check compatible strings against driver `of_match_table` entries and inspect DTS users for register tuple counts, interrupt names, clocks/resets, supplies, DMA channels, graph endpoints, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/allwinner,sun50i-a64-codec-analog.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/allwinner,sun50i-h6-dmic.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/allwinner,sun50i-h6-dmic.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/allwinner,sun50i-h6-dmic.yaml` defines the audio controller or sound-card binding titled `Allwinner H6 DMIC`. It constrains source DTS and compiled DTB hardware descriptions through compatible strings, required resources, child-node topology, and shared schema references before Linux drivers consume the node.

## Important APIs, Types, and Functions
The API surface is the devicetree ABI rather than callable code. `compatible` uses `oneOf` with 2 branches with 2 tokens: `allwinner,sun20i-d1-dmic`, `allwinner,sun50i-h6-dmic`. Top-level properties are `compatible`, `#sound-dai-cells`, `reg`, `interrupts`, `clocks`, `clock-names`, `dmas`, `dma-names`, `resets`. Required top-level properties are `#sound-dai-cells`, `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `dmas`, `dma-names`, `resets`. Nested or reusable constraints include composition/conditionals: `allOf`; referenced schemas: `dai-common.yaml#`; notable enum/const values: `0`, `bus`, `mod`, `rx`. The highest-risk contract area is register and interrupt resources, clocks/resets, DMA channels, sound-dai cells, graph ports/endpoints, routing, and SoC-specific compatible strings.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this file plus `$ref` targets, and enforces required properties, array cardinality, constants, enums, and `allOf`. `dtbs_check` then matches compiled DTS nodes by `compatible`, `$nodename`, or parent-schema inclusion, descends into pattern-matched children, and applies `additionalProperties` or `unevaluatedProperties` closure. Runtime flow begins only after the DTB is loaded: Linux bus, SoC, ASoC, MFD, syscon, or firmware drivers bind from compatible strings and acquire the resources described here.

## State and Persistence Behavior
The YAML itself stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: compatible strings, property names, phandle names, register tuple ordering, child-node names, and examples become contracts in source DTS files and compiled DTBs. Runtime state is created by the matched kernel drivers after probe, including DAI/controller probe state, DMA stream state, clocking, reset state, and sound-card topology owned by ASoC runtime drivers.

## Dependencies and Integration Points
Maintainers listed: Ban Tao <fengzheng923@gmail.com>. Schema dependencies include `dai-common.yaml#`. Integration points include ASoC CPU DAI drivers, platform DMA engines, machine drivers, graph/simple-card parsing, clocks/resets, pinctrl, and board DTS sound links. The file also integrates with Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and source DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to register and interrupt resources, clocks/resets, DMA channels, sound-dai cells, graph ports/endpoints, routing, and SoC-specific compatible strings, drift between documented compatible strings and driver match tables, incorrect resource ordering, phandle names, or cell counts that block probe or misconfigure hardware, variant-specific conditional branches accepting one SoC/chip while rejecting another. This schema closes composed schemas with `unevaluatedProperties: false`. Regressions usually show up as schema-check failures, boot-time probe failures, missing audio/SoC child devices, bad firmware/resource allocation, broken suspend/resume, or silent routing/clocking errors in board audio paths.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/sound/allwinner,sun50i-h6-dmic.yaml` for the targeted schema and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/sound/allwinner,sun50i-h6-dmic.yaml` against boards that instantiate it. The schema has 1 embedded example; keep those examples valid under targeted binding checks. Cross-check compatible strings against driver `of_match_table` entries and inspect DTS users for register tuple counts, interrupt names, clocks/resets, supplies, DMA channels, graph endpoints, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/allwinner,sun50i-h6-dmic.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/allwinner,sun8i-a23-codec-analog.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/allwinner,sun8i-a23-codec-analog.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/allwinner,sun8i-a23-codec-analog.yaml` defines the audio codec or amplifier binding titled `Allwinner A23 Analog Codec`. It constrains source DTS and compiled DTB hardware descriptions through compatible strings, required resources, child-node topology, and shared schema references before Linux drivers consume the node.

## Important APIs, Types, and Functions
The API surface is the devicetree ABI rather than callable code. `compatible` uses `oneOf` with 3 branches with 3 tokens: `allwinner,sun8i-h3-codec-analog`, `allwinner,sun8i-v3-codec-analog`, `allwinner,sun8i-v3s-codec-analog`. Top-level properties are `compatible`, `reg`. Required top-level properties are `compatible`, `reg`. Nested or reusable constraints include no unusually complex nested constraints beyond the top-level properties. The highest-risk contract area is compatible strings, bus address, reset/shutdown GPIOs, supplies, clocks, interrupts, DAI cells, widgets/routes, and chip-specific tuning properties.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this file plus `$ref` targets, and enforces required properties, array cardinality, constants, enums, and no top-level conditionals. `dtbs_check` then matches compiled DTS nodes by `compatible`, `$nodename`, or parent-schema inclusion, descends into pattern-matched children, and applies `additionalProperties` or `unevaluatedProperties` closure. Runtime flow begins only after the DTB is loaded: Linux bus, SoC, ASoC, MFD, syscon, or firmware drivers bind from compatible strings and acquire the resources described here.

## State and Persistence Behavior
The YAML itself stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: compatible strings, property names, phandle names, register tuple ordering, child-node names, and examples become contracts in source DTS files and compiled DTBs. Runtime state is created by the matched kernel drivers after probe, including regmap cache, DAPM power state, bias levels, PLL/clock configuration, jack/interrupt state, and audio stream parameters owned by ASoC drivers.

## Dependencies and Integration Points
Maintainers listed: Chen-Yu Tsai <wens@csie.org>, Maxime Ripard <mripard@kernel.org>. Schema dependencies include dt-schema core/meta schemas only. Integration points include ASoC codec/component drivers, I2C/SPI/platform bus probing, DAPM graph construction, regulators, clocks, GPIO controls, and machine-driver links. The file also integrates with Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and source DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to compatible strings, bus address, reset/shutdown GPIOs, supplies, clocks, interrupts, DAI cells, widgets/routes, and chip-specific tuning properties, drift between documented compatible strings and driver match tables, incorrect resource ordering, phandle names, or cell counts that block probe or misconfigure hardware. This schema rejects unknown top-level properties with `additionalProperties: false`. Regressions usually show up as schema-check failures, boot-time probe failures, missing audio/SoC child devices, bad firmware/resource allocation, broken suspend/resume, or silent routing/clocking errors in board audio paths.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/sound/allwinner,sun8i-a23-codec-analog.yaml` for the targeted schema and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/sound/allwinner,sun8i-a23-codec-analog.yaml` against boards that instantiate it. The schema has 1 embedded example; keep those examples valid under targeted binding checks. Cross-check compatible strings against driver `of_match_table` entries and inspect DTS users for register tuple counts, interrupt names, clocks/resets, supplies, DMA channels, graph endpoints, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/allwinner,sun8i-a23-codec-analog.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/allwinner,sun8i-a33-codec.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/allwinner,sun8i-a33-codec.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/allwinner,sun8i-a33-codec.yaml` defines the audio codec or amplifier binding titled `Allwinner A33 Codec`. It constrains source DTS and compiled DTB hardware descriptions through compatible strings, required resources, child-node topology, and shared schema references before Linux drivers consume the node.

## Important APIs, Types, and Functions
The API surface is the devicetree ABI rather than callable code. `compatible` uses `oneOf` with 2 branches with 2 tokens: `allwinner,sun50i-a64-codec`, `allwinner,sun8i-a33-codec`. Top-level properties are `#sound-dai-cells`, `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`. Required top-level properties are `#sound-dai-cells`, `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`. Nested or reusable constraints include composition/conditionals: `allOf`; referenced schemas: `dai-common.yaml#`; notable enum/const values: `bus`, `mod`. The highest-risk contract area is compatible strings, bus address, reset/shutdown GPIOs, supplies, clocks, interrupts, DAI cells, widgets/routes, and chip-specific tuning properties.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this file plus `$ref` targets, and enforces required properties, array cardinality, constants, enums, and `allOf`. `dtbs_check` then matches compiled DTS nodes by `compatible`, `$nodename`, or parent-schema inclusion, descends into pattern-matched children, and applies `additionalProperties` or `unevaluatedProperties` closure. Runtime flow begins only after the DTB is loaded: Linux bus, SoC, ASoC, MFD, syscon, or firmware drivers bind from compatible strings and acquire the resources described here.

## State and Persistence Behavior
The YAML itself stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: compatible strings, property names, phandle names, register tuple ordering, child-node names, and examples become contracts in source DTS files and compiled DTBs. Runtime state is created by the matched kernel drivers after probe, including regmap cache, DAPM power state, bias levels, PLL/clock configuration, jack/interrupt state, and audio stream parameters owned by ASoC drivers.

## Dependencies and Integration Points
Maintainers listed: Chen-Yu Tsai <wens@csie.org>, Maxime Ripard <mripard@kernel.org>. Schema dependencies include `dai-common.yaml#`. Integration points include ASoC codec/component drivers, I2C/SPI/platform bus probing, DAPM graph construction, regulators, clocks, GPIO controls, and machine-driver links. The file also integrates with Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and source DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to compatible strings, bus address, reset/shutdown GPIOs, supplies, clocks, interrupts, DAI cells, widgets/routes, and chip-specific tuning properties, drift between documented compatible strings and driver match tables, incorrect resource ordering, phandle names, or cell counts that block probe or misconfigure hardware, variant-specific conditional branches accepting one SoC/chip while rejecting another. This schema closes composed schemas with `unevaluatedProperties: false`. Regressions usually show up as schema-check failures, boot-time probe failures, missing audio/SoC child devices, bad firmware/resource allocation, broken suspend/resume, or silent routing/clocking errors in board audio paths.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/sound/allwinner,sun8i-a33-codec.yaml` for the targeted schema and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/sound/allwinner,sun8i-a33-codec.yaml` against boards that instantiate it. The schema has 1 embedded example; keep those examples valid under targeted binding checks. Cross-check compatible strings against driver `of_match_table` entries and inspect DTS users for register tuple counts, interrupt names, clocks/resets, supplies, DMA channels, graph endpoints, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/allwinner,sun8i-a33-codec.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/amlogic,aiu.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/amlogic,aiu.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/amlogic,aiu.yaml` defines the audio controller or sound-card binding titled `Amlogic AIU audio output controller`. It constrains source DTS and compiled DTB hardware descriptions through compatible strings, required resources, child-node topology, and shared schema references before Linux drivers consume the node.

## Important APIs, Types, and Functions
The API surface is the devicetree ABI rather than callable code. `compatible` uses an ordered compatible/fallback `items` sequence with 5 tokens: `amlogic,aiu-gxbb`, `amlogic,aiu-gxl`, `amlogic,aiu-meson8`, `amlogic,aiu-meson8b`, `amlogic,aiu`. Top-level properties are `$nodename`, `#sound-dai-cells`, `compatible`, `clocks`, `clock-names`, `interrupts`, `interrupt-names`, `reg`, `resets`, `sound-name-prefix`. Required top-level properties are `#sound-dai-cells`, `compatible`, `clocks`, `clock-names`, `interrupts`, `interrupt-names`, `reg`, `resets`. Nested or reusable constraints include composition/conditionals: `allOf`; referenced schemas: `dai-common.yaml#`; notable enum/const values: `2`, `pclk`, `i2s_pclk`, `i2s_aoclk`, `i2s_mclk`, `i2s_mixer`, `spdif_pclk`, `spdif_aoclk`, `spdif_mclk`, `spdif_mclk_sel`, `i2s`, `spdif`. The highest-risk contract area is register and interrupt resources, clocks/resets, DMA channels, sound-dai cells, graph ports/endpoints, routing, and SoC-specific compatible strings.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this file plus `$ref` targets, and enforces required properties, array cardinality, constants, enums, and `allOf`. `dtbs_check` then matches compiled DTS nodes by `compatible`, `$nodename`, or parent-schema inclusion, descends into pattern-matched children, and applies `additionalProperties` or `unevaluatedProperties` closure. Runtime flow begins only after the DTB is loaded: Linux bus, SoC, ASoC, MFD, syscon, or firmware drivers bind from compatible strings and acquire the resources described here.

## State and Persistence Behavior
The YAML itself stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: compatible strings, property names, phandle names, register tuple ordering, child-node names, and examples become contracts in source DTS files and compiled DTBs. Runtime state is created by the matched kernel drivers after probe, including DAI/controller probe state, DMA stream state, clocking, reset state, and sound-card topology owned by ASoC runtime drivers.

## Dependencies and Integration Points
Maintainers listed: Jerome Brunet <jbrunet@baylibre.com>. Schema dependencies include `dai-common.yaml#`. Integration points include ASoC CPU DAI drivers, platform DMA engines, machine drivers, graph/simple-card parsing, clocks/resets, pinctrl, and board DTS sound links. The file also integrates with Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and source DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to register and interrupt resources, clocks/resets, DMA channels, sound-dai cells, graph ports/endpoints, routing, and SoC-specific compatible strings, drift between documented compatible strings and driver match tables, incorrect resource ordering, phandle names, or cell counts that block probe or misconfigure hardware, variant-specific conditional branches accepting one SoC/chip while rejecting another. This schema rejects unknown top-level properties with `additionalProperties: false`. Regressions usually show up as schema-check failures, boot-time probe failures, missing audio/SoC child devices, bad firmware/resource allocation, broken suspend/resume, or silent routing/clocking errors in board audio paths.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/sound/amlogic,aiu.yaml` for the targeted schema and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/sound/amlogic,aiu.yaml` against boards that instantiate it. The schema has 1 embedded example; keep those examples valid under targeted binding checks. Cross-check compatible strings against driver `of_match_table` entries and inspect DTS users for register tuple counts, interrupt names, clocks/resets, supplies, DMA channels, graph endpoints, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/amlogic,aiu.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/amlogic,axg-fifo.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/amlogic,axg-fifo.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/amlogic,axg-fifo.yaml` defines the audio controller or sound-card binding titled `Amlogic AXG Audio FIFO controllers`. It constrains source DTS and compiled DTB hardware descriptions through compatible strings, required resources, child-node topology, and shared schema references before Linux drivers consume the node.

## Important APIs, Types, and Functions
The API surface is the devicetree ABI rather than callable code. `compatible` uses `oneOf` with 3 branches with 6 tokens: `amlogic,axg-toddr`, `amlogic,axg-frddr`, `amlogic,g12a-toddr`, `amlogic,sm1-toddr`, `amlogic,g12a-frddr`, `amlogic,sm1-frddr`. Top-level properties are `compatible`, `reg`, `#sound-dai-cells`, `clocks`, `interrupts`, `resets`, `reset-names`, `amlogic,fifo-depth`. Required top-level properties are `compatible`, `reg`, `#sound-dai-cells`, `clocks`, `interrupts`, `resets`, `amlogic,fifo-depth`. Nested or reusable constraints include composition/conditionals: `allOf`; referenced schemas: `/schemas/types.yaml#/definitions/uint32`, `dai-common.yaml#`; notable enum/const values: `0`, `arb`, `rst`. The highest-risk contract area is register and interrupt resources, clocks/resets, DMA channels, sound-dai cells, graph ports/endpoints, routing, and SoC-specific compatible strings.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this file plus `$ref` targets, and enforces required properties, array cardinality, constants, enums, and `allOf`. `dtbs_check` then matches compiled DTS nodes by `compatible`, `$nodename`, or parent-schema inclusion, descends into pattern-matched children, and applies `additionalProperties` or `unevaluatedProperties` closure. Runtime flow begins only after the DTB is loaded: Linux bus, SoC, ASoC, MFD, syscon, or firmware drivers bind from compatible strings and acquire the resources described here.

## State and Persistence Behavior
The YAML itself stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: compatible strings, property names, phandle names, register tuple ordering, child-node names, and examples become contracts in source DTS files and compiled DTBs. Runtime state is created by the matched kernel drivers after probe, including DAI/controller probe state, DMA stream state, clocking, reset state, and sound-card topology owned by ASoC runtime drivers.

## Dependencies and Integration Points
Maintainers listed: Jerome Brunet <jbrunet@baylibre.com>. Schema dependencies include `/schemas/types.yaml#/definitions/uint32`, `dai-common.yaml#`. Integration points include ASoC CPU DAI drivers, platform DMA engines, machine drivers, graph/simple-card parsing, clocks/resets, pinctrl, and board DTS sound links. The file also integrates with Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and source DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to register and interrupt resources, clocks/resets, DMA channels, sound-dai cells, graph ports/endpoints, routing, and SoC-specific compatible strings, drift between documented compatible strings and driver match tables, incorrect resource ordering, phandle names, or cell counts that block probe or misconfigure hardware, variant-specific conditional branches accepting one SoC/chip while rejecting another. This schema closes composed schemas with `unevaluatedProperties: false`. Regressions usually show up as schema-check failures, boot-time probe failures, missing audio/SoC child devices, bad firmware/resource allocation, broken suspend/resume, or silent routing/clocking errors in board audio paths.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/sound/amlogic,axg-fifo.yaml` for the targeted schema and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/sound/amlogic,axg-fifo.yaml` against boards that instantiate it. The schema has 1 embedded example; keep those examples valid under targeted binding checks. Cross-check compatible strings against driver `of_match_table` entries and inspect DTS users for register tuple counts, interrupt names, clocks/resets, supplies, DMA channels, graph endpoints, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/amlogic,axg-fifo.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/amlogic,axg-pdm.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/amlogic,axg-pdm.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/amlogic,axg-pdm.yaml` defines the audio controller or sound-card binding titled `Amlogic Audio AXG PDM input`. It constrains source DTS and compiled DTB hardware descriptions through compatible strings, required resources, child-node topology, and shared schema references before Linux drivers consume the node.

## Important APIs, Types, and Functions
The API surface is the devicetree ABI rather than callable code. `compatible` uses `oneOf` with 2 branches with 3 tokens: `amlogic,g12a-pdm`, `amlogic,sm1-pdm`, `amlogic,axg-pdm`. Top-level properties are `compatible`, `reg`, `#sound-dai-cells`, `clocks`, `clock-names`, `resets`. Required top-level properties are `compatible`, `reg`, `#sound-dai-cells`, `clocks`, `clock-names`. Nested or reusable constraints include composition/conditionals: `allOf`; referenced schemas: `dai-common.yaml#`; notable enum/const values: `0`, `pclk`, `dclk`, `sysclk`. The highest-risk contract area is register and interrupt resources, clocks/resets, DMA channels, sound-dai cells, graph ports/endpoints, routing, and SoC-specific compatible strings.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this file plus `$ref` targets, and enforces required properties, array cardinality, constants, enums, and `allOf`. `dtbs_check` then matches compiled DTS nodes by `compatible`, `$nodename`, or parent-schema inclusion, descends into pattern-matched children, and applies `additionalProperties` or `unevaluatedProperties` closure. Runtime flow begins only after the DTB is loaded: Linux bus, SoC, ASoC, MFD, syscon, or firmware drivers bind from compatible strings and acquire the resources described here.

## State and Persistence Behavior
The YAML itself stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: compatible strings, property names, phandle names, register tuple ordering, child-node names, and examples become contracts in source DTS files and compiled DTBs. Runtime state is created by the matched kernel drivers after probe, including DAI/controller probe state, DMA stream state, clocking, reset state, and sound-card topology owned by ASoC runtime drivers.

## Dependencies and Integration Points
Maintainers listed: Jerome Brunet <jbrunet@baylibre.com>. Schema dependencies include `dai-common.yaml#`. Integration points include ASoC CPU DAI drivers, platform DMA engines, machine drivers, graph/simple-card parsing, clocks/resets, pinctrl, and board DTS sound links. The file also integrates with Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and source DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to register and interrupt resources, clocks/resets, DMA channels, sound-dai cells, graph ports/endpoints, routing, and SoC-specific compatible strings, drift between documented compatible strings and driver match tables, incorrect resource ordering, phandle names, or cell counts that block probe or misconfigure hardware, variant-specific conditional branches accepting one SoC/chip while rejecting another. This schema closes composed schemas with `unevaluatedProperties: false`. Regressions usually show up as schema-check failures, boot-time probe failures, missing audio/SoC child devices, bad firmware/resource allocation, broken suspend/resume, or silent routing/clocking errors in board audio paths.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/sound/amlogic,axg-pdm.yaml` for the targeted schema and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/sound/amlogic,axg-pdm.yaml` against boards that instantiate it. The schema has 1 embedded example; keep those examples valid under targeted binding checks. Cross-check compatible strings against driver `of_match_table` entries and inspect DTS users for register tuple counts, interrupt names, clocks/resets, supplies, DMA channels, graph endpoints, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/amlogic,axg-pdm.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/amlogic,axg-sound-card.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/amlogic,axg-sound-card.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/amlogic,axg-sound-card.yaml` defines the audio controller or sound-card binding titled `Amlogic AXG sound card`. It constrains source DTS and compiled DTB hardware descriptions through compatible strings, required resources, child-node topology, and shared schema references before Linux drivers consume the node.

## Important APIs, Types, and Functions
The API surface is the devicetree ABI rather than callable code. `compatible` uses a single `const` token with 1 token: `amlogic,axg-sound-card`. Top-level properties are `compatible`, `audio-aux-devs`, `audio-widgets`, `clocks`. Required top-level properties are `dai-link-0`. Nested or reusable constraints include composition/conditionals: `allOf`; child-node patterns: `^dai-link-[0-9]+$`; referenced schemas: `/schemas/types.yaml#/definitions/non-unique-string-array`, `/schemas/types.yaml#/definitions/phandle-array`, `/schemas/types.yaml#/definitions/string`, `/schemas/types.yaml#/definitions/uint32`, `/schemas/types.yaml#/definitions/uint32-array`, `sound-card-common.yaml#`; child-node API keys: `sound-dai`, `dai-format`, `dai-tdm-slot-num`, `dai-tdm-slot-width`, `mclk-fs`; notable enum/const values: `i2s`, `left-j`, `dsp_a`, `8`, `16`, `20`, `24`, `32`. The highest-risk contract area is register and interrupt resources, clocks/resets, DMA channels, sound-dai cells, graph ports/endpoints, routing, and SoC-specific compatible strings.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this file plus `$ref` targets, and enforces required properties, array cardinality, constants, enums, and `allOf`. `dtbs_check` then matches compiled DTS nodes by `compatible`, `$nodename`, or parent-schema inclusion, descends into pattern-matched children, and applies `additionalProperties` or `unevaluatedProperties` closure. Runtime flow begins only after the DTB is loaded: Linux bus, SoC, ASoC, MFD, syscon, or firmware drivers bind from compatible strings and acquire the resources described here.

## State and Persistence Behavior
The YAML itself stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: compatible strings, property names, phandle names, register tuple ordering, child-node names, and examples become contracts in source DTS files and compiled DTBs. Runtime state is created by the matched kernel drivers after probe, including DAI/controller probe state, DMA stream state, clocking, reset state, and sound-card topology owned by ASoC runtime drivers.

## Dependencies and Integration Points
Maintainers listed: Jerome Brunet <jbrunet@baylibre.com>. Schema dependencies include `/schemas/types.yaml#/definitions/non-unique-string-array`, `/schemas/types.yaml#/definitions/phandle-array`, `/schemas/types.yaml#/definitions/string`, `/schemas/types.yaml#/definitions/uint32`, `/schemas/types.yaml#/definitions/uint32-array`, `sound-card-common.yaml#`. Integration points include ASoC CPU DAI drivers, platform DMA engines, machine drivers, graph/simple-card parsing, clocks/resets, pinctrl, and board DTS sound links. The file also integrates with Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and source DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to register and interrupt resources, clocks/resets, DMA channels, sound-dai cells, graph ports/endpoints, routing, and SoC-specific compatible strings, drift between documented compatible strings and driver match tables, incorrect resource ordering, phandle names, or cell counts that block probe or misconfigure hardware, variant-specific conditional branches accepting one SoC/chip while rejecting another, child-node regexes that over-match unrelated children or under-match valid hardware nodes. This schema closes composed schemas with `unevaluatedProperties: false`. Regressions usually show up as schema-check failures, boot-time probe failures, missing audio/SoC child devices, bad firmware/resource allocation, broken suspend/resume, or silent routing/clocking errors in board audio paths.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/sound/amlogic,axg-sound-card.yaml` for the targeted schema and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/sound/amlogic,axg-sound-card.yaml` against boards that instantiate it. The schema has 1 embedded example; keep those examples valid under targeted binding checks. Include child-node validation for `^dai-link-[0-9]+$`. Cross-check compatible strings against driver `of_match_table` entries and inspect DTS users for register tuple counts, interrupt names, clocks/resets, supplies, DMA channels, graph endpoints, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/amlogic,axg-sound-card.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/amlogic,axg-spdifin.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/amlogic,axg-spdifin.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/amlogic,axg-spdifin.yaml` defines the audio controller or sound-card binding titled `Amlogic Audio AXG SPDIF Input`. It constrains source DTS and compiled DTB hardware descriptions through compatible strings, required resources, child-node topology, and shared schema references before Linux drivers consume the node.

## Important APIs, Types, and Functions
The API surface is the devicetree ABI rather than callable code. `compatible` uses `oneOf` with 2 branches with 3 tokens: `amlogic,axg-spdifin`, `amlogic,g12a-spdifin`, `amlogic,sm1-spdifin`. Top-level properties are `compatible`, `reg`, `#sound-dai-cells`, `clocks`, `clock-names`, `interrupts`, `resets`. Required top-level properties are `compatible`, `reg`, `#sound-dai-cells`, `clocks`, `clock-names`, `interrupts`. Nested or reusable constraints include composition/conditionals: `allOf`; referenced schemas: `dai-common.yaml#`; notable enum/const values: `0`, `pclk`, `refclk`. The highest-risk contract area is register and interrupt resources, clocks/resets, DMA channels, sound-dai cells, graph ports/endpoints, routing, and SoC-specific compatible strings.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this file plus `$ref` targets, and enforces required properties, array cardinality, constants, enums, and `allOf`. `dtbs_check` then matches compiled DTS nodes by `compatible`, `$nodename`, or parent-schema inclusion, descends into pattern-matched children, and applies `additionalProperties` or `unevaluatedProperties` closure. Runtime flow begins only after the DTB is loaded: Linux bus, SoC, ASoC, MFD, syscon, or firmware drivers bind from compatible strings and acquire the resources described here.

## State and Persistence Behavior
The YAML itself stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: compatible strings, property names, phandle names, register tuple ordering, child-node names, and examples become contracts in source DTS files and compiled DTBs. Runtime state is created by the matched kernel drivers after probe, including DAI/controller probe state, DMA stream state, clocking, reset state, and sound-card topology owned by ASoC runtime drivers.

## Dependencies and Integration Points
Maintainers listed: Jerome Brunet <jbrunet@baylibre.com>. Schema dependencies include `dai-common.yaml#`. Integration points include ASoC CPU DAI drivers, platform DMA engines, machine drivers, graph/simple-card parsing, clocks/resets, pinctrl, and board DTS sound links. The file also integrates with Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and source DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to register and interrupt resources, clocks/resets, DMA channels, sound-dai cells, graph ports/endpoints, routing, and SoC-specific compatible strings, drift between documented compatible strings and driver match tables, incorrect resource ordering, phandle names, or cell counts that block probe or misconfigure hardware, variant-specific conditional branches accepting one SoC/chip while rejecting another. This schema closes composed schemas with `unevaluatedProperties: false`. Regressions usually show up as schema-check failures, boot-time probe failures, missing audio/SoC child devices, bad firmware/resource allocation, broken suspend/resume, or silent routing/clocking errors in board audio paths.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/sound/amlogic,axg-spdifin.yaml` for the targeted schema and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/sound/amlogic,axg-spdifin.yaml` against boards that instantiate it. The schema has 1 embedded example; keep those examples valid under targeted binding checks. Cross-check compatible strings against driver `of_match_table` entries and inspect DTS users for register tuple counts, interrupt names, clocks/resets, supplies, DMA channels, graph endpoints, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/amlogic,axg-spdifin.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/amlogic,axg-spdifout.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/amlogic,axg-spdifout.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/amlogic,axg-spdifout.yaml` defines the audio controller or sound-card binding titled `Amlogic Audio AXG SPDIF Output`. It constrains source DTS and compiled DTB hardware descriptions through compatible strings, required resources, child-node topology, and shared schema references before Linux drivers consume the node.

## Important APIs, Types, and Functions
The API surface is the devicetree ABI rather than callable code. `compatible` uses `oneOf` with 2 branches with 3 tokens: `amlogic,axg-spdifout`, `amlogic,g12a-spdifout`, `amlogic,sm1-spdifout`. Top-level properties are `compatible`, `reg`, `#sound-dai-cells`, `clocks`, `clock-names`, `resets`. Required top-level properties are `compatible`, `reg`, `#sound-dai-cells`, `clocks`, `clock-names`. Nested or reusable constraints include composition/conditionals: `allOf`; referenced schemas: `dai-common.yaml#`; notable enum/const values: `0`, `pclk`, `mclk`. The highest-risk contract area is register and interrupt resources, clocks/resets, DMA channels, sound-dai cells, graph ports/endpoints, routing, and SoC-specific compatible strings.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this file plus `$ref` targets, and enforces required properties, array cardinality, constants, enums, and `allOf`. `dtbs_check` then matches compiled DTS nodes by `compatible`, `$nodename`, or parent-schema inclusion, descends into pattern-matched children, and applies `additionalProperties` or `unevaluatedProperties` closure. Runtime flow begins only after the DTB is loaded: Linux bus, SoC, ASoC, MFD, syscon, or firmware drivers bind from compatible strings and acquire the resources described here.

## State and Persistence Behavior
The YAML itself stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: compatible strings, property names, phandle names, register tuple ordering, child-node names, and examples become contracts in source DTS files and compiled DTBs. Runtime state is created by the matched kernel drivers after probe, including DAI/controller probe state, DMA stream state, clocking, reset state, and sound-card topology owned by ASoC runtime drivers.

## Dependencies and Integration Points
Maintainers listed: Jerome Brunet <jbrunet@baylibre.com>. Schema dependencies include `dai-common.yaml#`. Integration points include ASoC CPU DAI drivers, platform DMA engines, machine drivers, graph/simple-card parsing, clocks/resets, pinctrl, and board DTS sound links. The file also integrates with Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and source DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to register and interrupt resources, clocks/resets, DMA channels, sound-dai cells, graph ports/endpoints, routing, and SoC-specific compatible strings, drift between documented compatible strings and driver match tables, incorrect resource ordering, phandle names, or cell counts that block probe or misconfigure hardware, variant-specific conditional branches accepting one SoC/chip while rejecting another. This schema closes composed schemas with `unevaluatedProperties: false`. Regressions usually show up as schema-check failures, boot-time probe failures, missing audio/SoC child devices, bad firmware/resource allocation, broken suspend/resume, or silent routing/clocking errors in board audio paths.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/sound/amlogic,axg-spdifout.yaml` for the targeted schema and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/sound/amlogic,axg-spdifout.yaml` against boards that instantiate it. The schema has 1 embedded example; keep those examples valid under targeted binding checks. Cross-check compatible strings against driver `of_match_table` entries and inspect DTS users for register tuple counts, interrupt names, clocks/resets, supplies, DMA channels, graph endpoints, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/amlogic,axg-spdifout.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/amlogic,axg-tdm-formatters.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/amlogic,axg-tdm-formatters.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/amlogic,axg-tdm-formatters.yaml` defines the audio controller or sound-card binding titled `Amlogic Audio AXG TDM formatters`. It constrains source DTS and compiled DTB hardware descriptions through compatible strings, required resources, child-node topology, and shared schema references before Linux drivers consume the node.

## Important APIs, Types, and Functions
The API surface is the devicetree ABI rather than callable code. `compatible` uses an `enum` of supported tokens with 6 tokens: `amlogic,g12a-tdmout`, `amlogic,sm1-tdmout`, `amlogic,axg-tdmout`, `amlogic,g12a-tdmin`, `amlogic,sm1-tdmin`, `amlogic,axg-tdmin`. Top-level properties are `compatible`, `clocks`, `clock-names`, `reg`, `resets`. Required top-level properties are `compatible`, `reg`, `clocks`, `clock-names`. Nested or reusable constraints include composition/conditionals: `allOf`; referenced schemas: `component-common.yaml#`; notable enum/const values: `pclk`, `sclk`, `sclk_sel`, `lrclk`, `lrclk_sel`. The highest-risk contract area is register and interrupt resources, clocks/resets, DMA channels, sound-dai cells, graph ports/endpoints, routing, and SoC-specific compatible strings.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this file plus `$ref` targets, and enforces required properties, array cardinality, constants, enums, and `allOf`. `dtbs_check` then matches compiled DTS nodes by `compatible`, `$nodename`, or parent-schema inclusion, descends into pattern-matched children, and applies `additionalProperties` or `unevaluatedProperties` closure. Runtime flow begins only after the DTB is loaded: Linux bus, SoC, ASoC, MFD, syscon, or firmware drivers bind from compatible strings and acquire the resources described here.

## State and Persistence Behavior
The YAML itself stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: compatible strings, property names, phandle names, register tuple ordering, child-node names, and examples become contracts in source DTS files and compiled DTBs. Runtime state is created by the matched kernel drivers after probe, including DAI/controller probe state, DMA stream state, clocking, reset state, and sound-card topology owned by ASoC runtime drivers.

## Dependencies and Integration Points
Maintainers listed: Jerome Brunet <jbrunet@baylibre.com>. Schema dependencies include `component-common.yaml#`. Integration points include ASoC CPU DAI drivers, platform DMA engines, machine drivers, graph/simple-card parsing, clocks/resets, pinctrl, and board DTS sound links. The file also integrates with Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and source DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to register and interrupt resources, clocks/resets, DMA channels, sound-dai cells, graph ports/endpoints, routing, and SoC-specific compatible strings, drift between documented compatible strings and driver match tables, incorrect resource ordering, phandle names, or cell counts that block probe or misconfigure hardware, variant-specific conditional branches accepting one SoC/chip while rejecting another. This schema closes composed schemas with `unevaluatedProperties: false`. Regressions usually show up as schema-check failures, boot-time probe failures, missing audio/SoC child devices, bad firmware/resource allocation, broken suspend/resume, or silent routing/clocking errors in board audio paths.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/sound/amlogic,axg-tdm-formatters.yaml` for the targeted schema and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/sound/amlogic,axg-tdm-formatters.yaml` against boards that instantiate it. The schema has 1 embedded example; keep those examples valid under targeted binding checks. Cross-check compatible strings against driver `of_match_table` entries and inspect DTS users for register tuple counts, interrupt names, clocks/resets, supplies, DMA channels, graph endpoints, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/amlogic,axg-tdm-formatters.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/amlogic,axg-tdm-iface.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/amlogic,axg-tdm-iface.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/amlogic,axg-tdm-iface.yaml` defines the audio controller or sound-card binding titled `Amlogic Audio TDM Interfaces`. It constrains source DTS and compiled DTB hardware descriptions through compatible strings, required resources, child-node topology, and shared schema references before Linux drivers consume the node.

## Important APIs, Types, and Functions
The API surface is the devicetree ABI rather than callable code. `compatible` uses a single `const` token with 1 token: `amlogic,axg-tdm-iface`. Top-level properties are `compatible`, `#sound-dai-cells`, `clocks`, `clock-names`. Required top-level properties are `compatible`, `#sound-dai-cells`, `clocks`, `clock-names`. Nested or reusable constraints include composition/conditionals: `allOf`; referenced schemas: `dai-common.yaml#`; notable enum/const values: `0`, `sclk`, `lrclk`, `mclk`. The highest-risk contract area is register and interrupt resources, clocks/resets, DMA channels, sound-dai cells, graph ports/endpoints, routing, and SoC-specific compatible strings.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this file plus `$ref` targets, and enforces required properties, array cardinality, constants, enums, and `allOf`. `dtbs_check` then matches compiled DTS nodes by `compatible`, `$nodename`, or parent-schema inclusion, descends into pattern-matched children, and applies `additionalProperties` or `unevaluatedProperties` closure. Runtime flow begins only after the DTB is loaded: Linux bus, SoC, ASoC, MFD, syscon, or firmware drivers bind from compatible strings and acquire the resources described here.

## State and Persistence Behavior
The YAML itself stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: compatible strings, property names, phandle names, register tuple ordering, child-node names, and examples become contracts in source DTS files and compiled DTBs. Runtime state is created by the matched kernel drivers after probe, including DAI/controller probe state, DMA stream state, clocking, reset state, and sound-card topology owned by ASoC runtime drivers.

## Dependencies and Integration Points
Maintainers listed: Jerome Brunet <jbrunet@baylibre.com>. Schema dependencies include `dai-common.yaml#`. Integration points include ASoC CPU DAI drivers, platform DMA engines, machine drivers, graph/simple-card parsing, clocks/resets, pinctrl, and board DTS sound links. The file also integrates with Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and source DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to register and interrupt resources, clocks/resets, DMA channels, sound-dai cells, graph ports/endpoints, routing, and SoC-specific compatible strings, drift between documented compatible strings and driver match tables, incorrect resource ordering, phandle names, or cell counts that block probe or misconfigure hardware, variant-specific conditional branches accepting one SoC/chip while rejecting another. This schema closes composed schemas with `unevaluatedProperties: false`. Regressions usually show up as schema-check failures, boot-time probe failures, missing audio/SoC child devices, bad firmware/resource allocation, broken suspend/resume, or silent routing/clocking errors in board audio paths.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/sound/amlogic,axg-tdm-iface.yaml` for the targeted schema and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/sound/amlogic,axg-tdm-iface.yaml` against boards that instantiate it. The schema has 1 embedded example; keep those examples valid under targeted binding checks. Cross-check compatible strings against driver `of_match_table` entries and inspect DTS users for register tuple counts, interrupt names, clocks/resets, supplies, DMA channels, graph endpoints, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/amlogic,axg-tdm-iface.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/amlogic,g12a-toacodec.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/amlogic,g12a-toacodec.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/amlogic,g12a-toacodec.yaml` defines the audio codec or amplifier binding titled `Amlogic G12a Internal DAC Control Glue`. It constrains source DTS and compiled DTB hardware descriptions through compatible strings, required resources, child-node topology, and shared schema references before Linux drivers consume the node.

## Important APIs, Types, and Functions
The API surface is the devicetree ABI rather than callable code. `compatible` uses `oneOf` with 2 branches with 2 tokens: `amlogic,g12a-toacodec`, `amlogic,sm1-toacodec`. Top-level properties are `$nodename`, `#sound-dai-cells`, `compatible`, `reg`, `resets`, `sound-name-prefix`. Required top-level properties are `#sound-dai-cells`, `compatible`, `reg`, `resets`. Nested or reusable constraints include composition/conditionals: `allOf`; referenced schemas: `dai-common.yaml#`; notable enum/const values: `1`. The highest-risk contract area is compatible strings, bus address, reset/shutdown GPIOs, supplies, clocks, interrupts, DAI cells, widgets/routes, and chip-specific tuning properties.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this file plus `$ref` targets, and enforces required properties, array cardinality, constants, enums, and `allOf`. `dtbs_check` then matches compiled DTS nodes by `compatible`, `$nodename`, or parent-schema inclusion, descends into pattern-matched children, and applies `additionalProperties` or `unevaluatedProperties` closure. Runtime flow begins only after the DTB is loaded: Linux bus, SoC, ASoC, MFD, syscon, or firmware drivers bind from compatible strings and acquire the resources described here.

## State and Persistence Behavior
The YAML itself stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: compatible strings, property names, phandle names, register tuple ordering, child-node names, and examples become contracts in source DTS files and compiled DTBs. Runtime state is created by the matched kernel drivers after probe, including regmap cache, DAPM power state, bias levels, PLL/clock configuration, jack/interrupt state, and audio stream parameters owned by ASoC drivers.

## Dependencies and Integration Points
Maintainers listed: Jerome Brunet <jbrunet@baylibre.com>. Schema dependencies include `dai-common.yaml#`. Integration points include ASoC codec/component drivers, I2C/SPI/platform bus probing, DAPM graph construction, regulators, clocks, GPIO controls, and machine-driver links. The file also integrates with Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and source DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to compatible strings, bus address, reset/shutdown GPIOs, supplies, clocks, interrupts, DAI cells, widgets/routes, and chip-specific tuning properties, drift between documented compatible strings and driver match tables, incorrect resource ordering, phandle names, or cell counts that block probe or misconfigure hardware, variant-specific conditional branches accepting one SoC/chip while rejecting another. This schema rejects unknown top-level properties with `additionalProperties: false`. Regressions usually show up as schema-check failures, boot-time probe failures, missing audio/SoC child devices, bad firmware/resource allocation, broken suspend/resume, or silent routing/clocking errors in board audio paths.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/sound/amlogic,g12a-toacodec.yaml` for the targeted schema and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/sound/amlogic,g12a-toacodec.yaml` against boards that instantiate it. The schema has 1 embedded example; keep those examples valid under targeted binding checks. Cross-check compatible strings against driver `of_match_table` entries and inspect DTS users for register tuple counts, interrupt names, clocks/resets, supplies, DMA channels, graph endpoints, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/amlogic,g12a-toacodec.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/amlogic,g12a-tohdmitx.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/amlogic,g12a-tohdmitx.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/amlogic,g12a-tohdmitx.yaml` defines the audio controller or sound-card binding titled `Amlogic G12a HDMI TX Control Glue`. It constrains source DTS and compiled DTB hardware descriptions through compatible strings, required resources, child-node topology, and shared schema references before Linux drivers consume the node.

## Important APIs, Types, and Functions
The API surface is the devicetree ABI rather than callable code. `compatible` uses `oneOf` with 2 branches with 2 tokens: `amlogic,g12a-tohdmitx`, `amlogic,sm1-tohdmitx`. Top-level properties are `$nodename`, `compatible`, `reg`, `resets`, `#sound-dai-cells`. Required top-level properties are `compatible`, `reg`, `resets`, `#sound-dai-cells`. Nested or reusable constraints include composition/conditionals: `allOf`; referenced schemas: `dai-common.yaml#`; notable enum/const values: `1`. The highest-risk contract area is register and interrupt resources, clocks/resets, DMA channels, sound-dai cells, graph ports/endpoints, routing, and SoC-specific compatible strings.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this file plus `$ref` targets, and enforces required properties, array cardinality, constants, enums, and `allOf`. `dtbs_check` then matches compiled DTS nodes by `compatible`, `$nodename`, or parent-schema inclusion, descends into pattern-matched children, and applies `additionalProperties` or `unevaluatedProperties` closure. Runtime flow begins only after the DTB is loaded: Linux bus, SoC, ASoC, MFD, syscon, or firmware drivers bind from compatible strings and acquire the resources described here.

## State and Persistence Behavior
The YAML itself stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: compatible strings, property names, phandle names, register tuple ordering, child-node names, and examples become contracts in source DTS files and compiled DTBs. Runtime state is created by the matched kernel drivers after probe, including DAI/controller probe state, DMA stream state, clocking, reset state, and sound-card topology owned by ASoC runtime drivers.

## Dependencies and Integration Points
Maintainers listed: Jerome Brunet <jbrunet@baylibre.com>. Schema dependencies include `dai-common.yaml#`. Integration points include ASoC CPU DAI drivers, platform DMA engines, machine drivers, graph/simple-card parsing, clocks/resets, pinctrl, and board DTS sound links. The file also integrates with Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and source DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to register and interrupt resources, clocks/resets, DMA channels, sound-dai cells, graph ports/endpoints, routing, and SoC-specific compatible strings, drift between documented compatible strings and driver match tables, incorrect resource ordering, phandle names, or cell counts that block probe or misconfigure hardware, variant-specific conditional branches accepting one SoC/chip while rejecting another. This schema closes composed schemas with `unevaluatedProperties: false`. Regressions usually show up as schema-check failures, boot-time probe failures, missing audio/SoC child devices, bad firmware/resource allocation, broken suspend/resume, or silent routing/clocking errors in board audio paths.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/sound/amlogic,g12a-tohdmitx.yaml` for the targeted schema and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/sound/amlogic,g12a-tohdmitx.yaml` against boards that instantiate it. The schema has 1 embedded example; keep those examples valid under targeted binding checks. Cross-check compatible strings against driver `of_match_table` entries and inspect DTS users for register tuple counts, interrupt names, clocks/resets, supplies, DMA channels, graph endpoints, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/amlogic,g12a-tohdmitx.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/amlogic,gx-sound-card.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/amlogic,gx-sound-card.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/amlogic,gx-sound-card.yaml` defines the audio controller or sound-card binding titled `Amlogic GX sound card`. It constrains source DTS and compiled DTB hardware descriptions through compatible strings, required resources, child-node topology, and shared schema references before Linux drivers consume the node.

## Important APIs, Types, and Functions
The API surface is the devicetree ABI rather than callable code. `compatible` uses an ordered compatible/fallback `items` sequence with 1 token: `amlogic,gx-sound-card`. Top-level properties are `compatible`, `audio-aux-devs`, `audio-widgets`, `clocks`. Required top-level properties are `model`, `dai-link-0`. Nested or reusable constraints include composition/conditionals: `allOf`; child-node patterns: `^dai-link-[0-9]+$`; referenced schemas: `/schemas/types.yaml#/definitions/non-unique-string-array`, `/schemas/types.yaml#/definitions/phandle-array`, `/schemas/types.yaml#/definitions/string`, `/schemas/types.yaml#/definitions/uint32`, `sound-card-common.yaml#`; child-node API keys: `sound-dai`, `dai-format`, `mclk-fs`; notable enum/const values: `i2s`, `left-j`, `dsp_a`. The highest-risk contract area is register and interrupt resources, clocks/resets, DMA channels, sound-dai cells, graph ports/endpoints, routing, and SoC-specific compatible strings.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this file plus `$ref` targets, and enforces required properties, array cardinality, constants, enums, and `allOf`. `dtbs_check` then matches compiled DTS nodes by `compatible`, `$nodename`, or parent-schema inclusion, descends into pattern-matched children, and applies `additionalProperties` or `unevaluatedProperties` closure. Runtime flow begins only after the DTB is loaded: Linux bus, SoC, ASoC, MFD, syscon, or firmware drivers bind from compatible strings and acquire the resources described here.

## State and Persistence Behavior
The YAML itself stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: compatible strings, property names, phandle names, register tuple ordering, child-node names, and examples become contracts in source DTS files and compiled DTBs. Runtime state is created by the matched kernel drivers after probe, including DAI/controller probe state, DMA stream state, clocking, reset state, and sound-card topology owned by ASoC runtime drivers.

## Dependencies and Integration Points
Maintainers listed: Jerome Brunet <jbrunet@baylibre.com>. Schema dependencies include `/schemas/types.yaml#/definitions/non-unique-string-array`, `/schemas/types.yaml#/definitions/phandle-array`, `/schemas/types.yaml#/definitions/string`, `/schemas/types.yaml#/definitions/uint32`, `sound-card-common.yaml#`. Integration points include ASoC CPU DAI drivers, platform DMA engines, machine drivers, graph/simple-card parsing, clocks/resets, pinctrl, and board DTS sound links. The file also integrates with Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and source DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to register and interrupt resources, clocks/resets, DMA channels, sound-dai cells, graph ports/endpoints, routing, and SoC-specific compatible strings, drift between documented compatible strings and driver match tables, incorrect resource ordering, phandle names, or cell counts that block probe or misconfigure hardware, variant-specific conditional branches accepting one SoC/chip while rejecting another, child-node regexes that over-match unrelated children or under-match valid hardware nodes. This schema closes composed schemas with `unevaluatedProperties: false`. Regressions usually show up as schema-check failures, boot-time probe failures, missing audio/SoC child devices, bad firmware/resource allocation, broken suspend/resume, or silent routing/clocking errors in board audio paths.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/sound/amlogic,gx-sound-card.yaml` for the targeted schema and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/sound/amlogic,gx-sound-card.yaml` against boards that instantiate it. The schema has 1 embedded example; keep those examples valid under targeted binding checks. Include child-node validation for `^dai-link-[0-9]+$`. Cross-check compatible strings against driver `of_match_table` entries and inspect DTS users for register tuple counts, interrupt names, clocks/resets, supplies, DMA channels, graph endpoints, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/amlogic,gx-sound-card.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/amlogic,t9015.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/amlogic,t9015.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/amlogic,t9015.yaml` defines the audio controller or sound-card binding titled `Amlogic T9015 Internal Audio DAC`. It constrains source DTS and compiled DTB hardware descriptions through compatible strings, required resources, child-node topology, and shared schema references before Linux drivers consume the node.

## Important APIs, Types, and Functions
The API surface is the devicetree ABI rather than callable code. `compatible` uses an ordered compatible/fallback `items` sequence with 1 token: `amlogic,t9015`. Top-level properties are `$nodename`, `#sound-dai-cells`, `compatible`, `clocks`, `clock-names`, `reg`, `resets`, `AVDD-supply`, `sound-name-prefix`. Required top-level properties are `#sound-dai-cells`, `compatible`, `reg`, `clocks`, `clock-names`, `resets`, `AVDD-supply`. Nested or reusable constraints include composition/conditionals: `allOf`; referenced schemas: `dai-common.yaml#`; notable enum/const values: `0`, `pclk`. The highest-risk contract area is register and interrupt resources, clocks/resets, DMA channels, sound-dai cells, graph ports/endpoints, routing, and SoC-specific compatible strings.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this file plus `$ref` targets, and enforces required properties, array cardinality, constants, enums, and `allOf`. `dtbs_check` then matches compiled DTS nodes by `compatible`, `$nodename`, or parent-schema inclusion, descends into pattern-matched children, and applies `additionalProperties` or `unevaluatedProperties` closure. Runtime flow begins only after the DTB is loaded: Linux bus, SoC, ASoC, MFD, syscon, or firmware drivers bind from compatible strings and acquire the resources described here.

## State and Persistence Behavior
The YAML itself stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: compatible strings, property names, phandle names, register tuple ordering, child-node names, and examples become contracts in source DTS files and compiled DTBs. Runtime state is created by the matched kernel drivers after probe, including DAI/controller probe state, DMA stream state, clocking, reset state, and sound-card topology owned by ASoC runtime drivers.

## Dependencies and Integration Points
Maintainers listed: Jerome Brunet <jbrunet@baylibre.com>. Schema dependencies include `dai-common.yaml#`. Integration points include ASoC CPU DAI drivers, platform DMA engines, machine drivers, graph/simple-card parsing, clocks/resets, pinctrl, and board DTS sound links. The file also integrates with Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and source DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to register and interrupt resources, clocks/resets, DMA channels, sound-dai cells, graph ports/endpoints, routing, and SoC-specific compatible strings, drift between documented compatible strings and driver match tables, incorrect resource ordering, phandle names, or cell counts that block probe or misconfigure hardware, variant-specific conditional branches accepting one SoC/chip while rejecting another. This schema rejects unknown top-level properties with `additionalProperties: false`. Regressions usually show up as schema-check failures, boot-time probe failures, missing audio/SoC child devices, bad firmware/resource allocation, broken suspend/resume, or silent routing/clocking errors in board audio paths.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/sound/amlogic,t9015.yaml` for the targeted schema and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/sound/amlogic,t9015.yaml` against boards that instantiate it. The schema has 1 embedded example; keep those examples valid under targeted binding checks. Cross-check compatible strings against driver `of_match_table` entries and inspect DTS users for register tuple counts, interrupt names, clocks/resets, supplies, DMA channels, graph endpoints, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/amlogic,t9015.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/apple,mca.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/apple,mca.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/apple,mca.yaml` defines the audio controller or sound-card binding titled `Apple MCA I2S transceiver`. MCA is an I2S transceiver peripheral found on M1 and other Apple chips. It constrains source DTS and compiled DTB hardware descriptions before Linux drivers consume the node.

## Important APIs, Types, and Functions
The API surface is the devicetree ABI rather than callable code. `compatible` uses `oneOf` with 2 branches with 5 tokens: `apple,t6020-mca`, `apple,t8103-mca`, `apple,t6000-mca`, `apple,t8112-mca`, `apple,mca`. Top-level properties are `compatible`, `reg`, `interrupts`, `#address-cells`, `#size-cells`, `dmas`, `dma-names`, `clocks`, `resets`, `power-domains`, `#sound-dai-cells`. Required top-level properties are `compatible`, `reg`, `dmas`, `dma-names`, `clocks`, `power-domains`, `#sound-dai-cells`. Nested or reusable constraints include composition/conditionals: `allOf`; referenced schemas: `dai-common.yaml#`; notable enum/const values: `1`, `0`, `tx0a`, `rx0a`, `tx0b`, `rx0b`, `tx1a`, `rx1a`, `tx1b`, `rx1b`, `tx2a`, `rx2a`, `tx2b`, `rx2b`, `tx3a`, `rx3a`, and 10 more. The highest-risk contract area is register and interrupt resources, clocks/resets, DMA channels, sound-dai cells, graph ports/endpoints, routing, and SoC-specific compatible strings.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this file plus `$ref` targets, and enforces required properties, array cardinality, constants, enums, and `allOf`. `dtbs_check` then matches compiled DTS nodes by `compatible`, `$nodename`, or parent-schema inclusion, descends into pattern-matched children, and applies `additionalProperties` or `unevaluatedProperties` closure. Runtime flow begins only after the DTB is loaded: Linux bus, SoC, ASoC, MFD, syscon, or firmware drivers bind from compatible strings and acquire the resources described here.

## State and Persistence Behavior
The YAML itself stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: compatible strings, property names, phandle names, register tuple ordering, child-node names, and examples become contracts in source DTS files and compiled DTBs. Runtime state is created by the matched kernel drivers after probe, including DAI/controller probe state, DMA stream state, clocking, reset state, and sound-card topology owned by ASoC runtime drivers.

## Dependencies and Integration Points
Maintainers listed: Martin Povišer <povik+lin@cutebit.org>. Schema dependencies include `dai-common.yaml#`. Integration points include ASoC CPU DAI drivers, platform DMA engines, machine drivers, graph/simple-card parsing, clocks/resets, pinctrl, and board DTS sound links. The file also integrates with Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and source DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to register and interrupt resources, clocks/resets, DMA channels, sound-dai cells, graph ports/endpoints, routing, and SoC-specific compatible strings, drift between documented compatible strings and driver match tables, incorrect resource ordering, phandle names, or cell counts that block probe or misconfigure hardware, variant-specific conditional branches accepting one SoC/chip while rejecting another. This schema closes composed schemas with `unevaluatedProperties: false`. Regressions usually show up as schema-check failures, boot-time probe failures, missing audio/SoC child devices, bad firmware/resource allocation, broken suspend/resume, or silent routing/clocking errors in board audio paths.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/sound/apple,mca.yaml` for the targeted schema and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/sound/apple,mca.yaml` against boards that instantiate it. The schema has 1 embedded example; keep those examples valid under targeted binding checks. Cross-check compatible strings against driver `of_match_table` entries and inspect DTS users for register tuple counts, interrupt names, clocks/resets, supplies, DMA channels, graph endpoints, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/apple,mca.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/arm,pl041.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/arm,pl041.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/arm,pl041.yaml` defines the audio controller or sound-card binding titled `Arm Ltd. PrimeCell PL041 AACI sound interface`. The Arm PrimeCell Advanced Audio CODEC Interface (AACI) is an AMBA compliant peripheral that provides communication with an audio CODEC using the AC-link protocol. It constrains source DTS and compiled DTB hardware descriptions before Linux drivers consume the node.

## Important APIs, Types, and Functions
The API surface is the devicetree ABI rather than callable code. `compatible` uses an ordered compatible/fallback `items` sequence with 2 tokens: `arm,pl041`, `arm,primecell`. Top-level properties are `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`. Required top-level properties are `compatible`, `reg`, `interrupts`, `clocks`. Nested or reusable constraints include notable enum/const values: `apb_pclk`. The highest-risk contract area is register and interrupt resources, clocks/resets, DMA channels, sound-dai cells, graph ports/endpoints, routing, and SoC-specific compatible strings.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this file plus `$ref` targets, and enforces required properties, array cardinality, constants, enums, and no top-level conditionals. `dtbs_check` then matches compiled DTS nodes by `compatible`, `$nodename`, or parent-schema inclusion, descends into pattern-matched children, and applies `additionalProperties` or `unevaluatedProperties` closure. Runtime flow begins only after the DTB is loaded: Linux bus, SoC, ASoC, MFD, syscon, or firmware drivers bind from compatible strings and acquire the resources described here.

## State and Persistence Behavior
The YAML itself stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: compatible strings, property names, phandle names, register tuple ordering, child-node names, and examples become contracts in source DTS files and compiled DTBs. Runtime state is created by the matched kernel drivers after probe, including DAI/controller probe state, DMA stream state, clocking, reset state, and sound-card topology owned by ASoC runtime drivers.

## Dependencies and Integration Points
Maintainers listed: Andre Przywara <andre.przywara@arm.com>. Schema dependencies include dt-schema core/meta schemas only. Integration points include ASoC CPU DAI drivers, platform DMA engines, machine drivers, graph/simple-card parsing, clocks/resets, pinctrl, and board DTS sound links. The file also integrates with Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and source DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to register and interrupt resources, clocks/resets, DMA channels, sound-dai cells, graph ports/endpoints, routing, and SoC-specific compatible strings, drift between documented compatible strings and driver match tables, incorrect resource ordering, phandle names, or cell counts that block probe or misconfigure hardware. This schema rejects unknown top-level properties with `additionalProperties: false`. Regressions usually show up as schema-check failures, boot-time probe failures, missing audio/SoC child devices, bad firmware/resource allocation, broken suspend/resume, or silent routing/clocking errors in board audio paths.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/sound/arm,pl041.yaml` for the targeted schema and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/sound/arm,pl041.yaml` against boards that instantiate it. The schema has 1 embedded example; keep those examples valid under targeted binding checks. Cross-check compatible strings against driver `of_match_table` entries and inspect DTS users for register tuple counts, interrupt names, clocks/resets, supplies, DMA channels, graph endpoints, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/arm,pl041.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/asahi-kasei,ak4104.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/asahi-kasei,ak4104.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/asahi-kasei,ak4104.yaml` defines the audio codec or amplifier binding titled `AK4104 S/PDIF transmitter`. It constrains source DTS and compiled DTB hardware descriptions through compatible strings, required resources, child-node topology, and shared schema references before Linux drivers consume the node.

## Important APIs, Types, and Functions
The API surface is the devicetree ABI rather than callable code. `compatible` uses a single `const` token with 1 token: `asahi-kasei,ak4104`. Top-level properties are `compatible`, `reg`, `vdd-supply`, `reset-gpios`. Required top-level properties are `compatible`, `reg`, `vdd-supply`. Nested or reusable constraints include composition/conditionals: `allOf`; referenced schemas: `dai-common.yaml#`. The highest-risk contract area is compatible strings, bus address, reset/shutdown GPIOs, supplies, clocks, interrupts, DAI cells, widgets/routes, and chip-specific tuning properties.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this file plus `$ref` targets, and enforces required properties, array cardinality, constants, enums, and `allOf`. `dtbs_check` then matches compiled DTS nodes by `compatible`, `$nodename`, or parent-schema inclusion, descends into pattern-matched children, and applies `additionalProperties` or `unevaluatedProperties` closure. Runtime flow begins only after the DTB is loaded: Linux bus, SoC, ASoC, MFD, syscon, or firmware drivers bind from compatible strings and acquire the resources described here.

## State and Persistence Behavior
The YAML itself stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: compatible strings, property names, phandle names, register tuple ordering, child-node names, and examples become contracts in source DTS files and compiled DTBs. Runtime state is created by the matched kernel drivers after probe, including regmap cache, DAPM power state, bias levels, PLL/clock configuration, jack/interrupt state, and audio stream parameters owned by ASoC drivers.

## Dependencies and Integration Points
Maintainers listed: Daniel Mack <github@zonque.org>, Xiaxi Shen <shenxiaxi26@gmail.com>. Schema dependencies include `dai-common.yaml#`. Integration points include ASoC codec/component drivers, I2C/SPI/platform bus probing, DAPM graph construction, regulators, clocks, GPIO controls, and machine-driver links. The file also integrates with Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and source DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to compatible strings, bus address, reset/shutdown GPIOs, supplies, clocks, interrupts, DAI cells, widgets/routes, and chip-specific tuning properties, drift between documented compatible strings and driver match tables, incorrect resource ordering, phandle names, or cell counts that block probe or misconfigure hardware, variant-specific conditional branches accepting one SoC/chip while rejecting another. This schema closes composed schemas with `unevaluatedProperties: false`. Regressions usually show up as schema-check failures, boot-time probe failures, missing audio/SoC child devices, bad firmware/resource allocation, broken suspend/resume, or silent routing/clocking errors in board audio paths.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/sound/asahi-kasei,ak4104.yaml` for the targeted schema and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/sound/asahi-kasei,ak4104.yaml` against boards that instantiate it. The schema has 1 embedded example; keep those examples valid under targeted binding checks. Cross-check compatible strings against driver `of_match_table` entries and inspect DTS users for register tuple counts, interrupt names, clocks/resets, supplies, DMA channels, graph endpoints, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/asahi-kasei,ak4104.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/asahi-kasei,ak4375.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/asahi-kasei,ak4375.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/asahi-kasei,ak4375.yaml` defines the audio codec or amplifier binding titled `AK4375 DAC and headphones amplifier`. It constrains source DTS and compiled DTB hardware descriptions through compatible strings, required resources, child-node topology, and shared schema references before Linux drivers consume the node.

## Important APIs, Types, and Functions
The API surface is the devicetree ABI rather than callable code. `compatible` uses a single `const` token with 1 token: `asahi-kasei,ak4375`. Top-level properties are `compatible`, `reg`, `#sound-dai-cells`, `avdd-supply`, `tvdd-supply`, `pdn-gpios`. Required top-level properties are `compatible`, `reg`, `#sound-dai-cells`, `avdd-supply`, `tvdd-supply`. Nested or reusable constraints include composition/conditionals: `allOf`; referenced schemas: `dai-common.yaml#`; notable enum/const values: `0`. The highest-risk contract area is compatible strings, bus address, reset/shutdown GPIOs, supplies, clocks, interrupts, DAI cells, widgets/routes, and chip-specific tuning properties.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this file plus `$ref` targets, and enforces required properties, array cardinality, constants, enums, and `allOf`. `dtbs_check` then matches compiled DTS nodes by `compatible`, `$nodename`, or parent-schema inclusion, descends into pattern-matched children, and applies `additionalProperties` or `unevaluatedProperties` closure. Runtime flow begins only after the DTB is loaded: Linux bus, SoC, ASoC, MFD, syscon, or firmware drivers bind from compatible strings and acquire the resources described here.

## State and Persistence Behavior
The YAML itself stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: compatible strings, property names, phandle names, register tuple ordering, child-node names, and examples become contracts in source DTS files and compiled DTBs. Runtime state is created by the matched kernel drivers after probe, including regmap cache, DAPM power state, bias levels, PLL/clock configuration, jack/interrupt state, and audio stream parameters owned by ASoC drivers.

## Dependencies and Integration Points
Maintainers listed: Vincent Knecht <vincent.knecht@mailoo.org>. Schema dependencies include `dai-common.yaml#`. Integration points include ASoC codec/component drivers, I2C/SPI/platform bus probing, DAPM graph construction, regulators, clocks, GPIO controls, and machine-driver links. The file also integrates with Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and source DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to compatible strings, bus address, reset/shutdown GPIOs, supplies, clocks, interrupts, DAI cells, widgets/routes, and chip-specific tuning properties, drift between documented compatible strings and driver match tables, incorrect resource ordering, phandle names, or cell counts that block probe or misconfigure hardware, variant-specific conditional branches accepting one SoC/chip while rejecting another. This schema closes composed schemas with `unevaluatedProperties: false`. Regressions usually show up as schema-check failures, boot-time probe failures, missing audio/SoC child devices, bad firmware/resource allocation, broken suspend/resume, or silent routing/clocking errors in board audio paths.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/sound/asahi-kasei,ak4375.yaml` for the targeted schema and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/sound/asahi-kasei,ak4375.yaml` against boards that instantiate it. The schema has 1 embedded example; keep those examples valid under targeted binding checks. Cross-check compatible strings against driver `of_match_table` entries and inspect DTS users for register tuple counts, interrupt names, clocks/resets, supplies, DMA channels, graph endpoints, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/asahi-kasei,ak4375.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/asahi-kasei,ak4458.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/asahi-kasei,ak4458.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/asahi-kasei,ak4458.yaml` defines the audio codec or amplifier binding titled `AK4458 audio DAC`. It constrains source DTS and compiled DTB hardware descriptions through compatible strings, required resources, child-node topology, and shared schema references before Linux drivers consume the node.

## Important APIs, Types, and Functions
The API surface is the devicetree ABI rather than callable code. `compatible` uses an `enum` of supported tokens with 2 tokens: `asahi-kasei,ak4458`, `asahi-kasei,ak4497`. Top-level properties are `compatible`, `#sound-dai-cells`, `reg`, `AVDD-supply`, `DVDD-supply`, `reset-gpios`, `mute-gpios`, `dsd-path`. Required top-level properties are `compatible`, `reg`. Nested or reusable constraints include composition/conditionals: `allOf`; referenced schemas: `/schemas/types.yaml#/definitions/uint32`, `dai-common.yaml#`; notable enum/const values: `0`, `1`. The highest-risk contract area is compatible strings, bus address, reset/shutdown GPIOs, supplies, clocks, interrupts, DAI cells, widgets/routes, and chip-specific tuning properties.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this file plus `$ref` targets, and enforces required properties, array cardinality, constants, enums, and `allOf`. `dtbs_check` then matches compiled DTS nodes by `compatible`, `$nodename`, or parent-schema inclusion, descends into pattern-matched children, and applies `additionalProperties` or `unevaluatedProperties` closure. Runtime flow begins only after the DTB is loaded: Linux bus, SoC, ASoC, MFD, syscon, or firmware drivers bind from compatible strings and acquire the resources described here.

## State and Persistence Behavior
The YAML itself stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: compatible strings, property names, phandle names, register tuple ordering, child-node names, and examples become contracts in source DTS files and compiled DTBs. Runtime state is created by the matched kernel drivers after probe, including regmap cache, DAPM power state, bias levels, PLL/clock configuration, jack/interrupt state, and audio stream parameters owned by ASoC drivers.

## Dependencies and Integration Points
Maintainers listed: Shengjiu Wang <shengjiu.wang@nxp.com>. Schema dependencies include `/schemas/types.yaml#/definitions/uint32`, `dai-common.yaml#`. Integration points include ASoC codec/component drivers, I2C/SPI/platform bus probing, DAPM graph construction, regulators, clocks, GPIO controls, and machine-driver links. The file also integrates with Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and source DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to compatible strings, bus address, reset/shutdown GPIOs, supplies, clocks, interrupts, DAI cells, widgets/routes, and chip-specific tuning properties, drift between documented compatible strings and driver match tables, incorrect resource ordering, phandle names, or cell counts that block probe or misconfigure hardware, variant-specific conditional branches accepting one SoC/chip while rejecting another. This schema closes composed schemas with `unevaluatedProperties: false`. Regressions usually show up as schema-check failures, boot-time probe failures, missing audio/SoC child devices, bad firmware/resource allocation, broken suspend/resume, or silent routing/clocking errors in board audio paths.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/sound/asahi-kasei,ak4458.yaml` for the targeted schema and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/sound/asahi-kasei,ak4458.yaml` against boards that instantiate it. The schema has 1 embedded example; keep those examples valid under targeted binding checks. Cross-check compatible strings against driver `of_match_table` entries and inspect DTS users for register tuple counts, interrupt names, clocks/resets, supplies, DMA channels, graph endpoints, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/asahi-kasei,ak4458.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/asahi-kasei,ak4554.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/asahi-kasei,ak4554.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/asahi-kasei,ak4554.yaml` defines the audio codec or amplifier binding titled `AK4554 sound codec`. It constrains source DTS and compiled DTB hardware descriptions through compatible strings, required resources, child-node topology, and shared schema references before Linux drivers consume the node.

## Important APIs, Types, and Functions
The API surface is the devicetree ABI rather than callable code. `compatible` uses a single `const` token with 1 token: `asahi-kasei,ak4554`. Top-level properties are `compatible`. Required top-level properties are `compatible`. Nested or reusable constraints include no unusually complex nested constraints beyond the top-level properties. The highest-risk contract area is compatible strings, bus address, reset/shutdown GPIOs, supplies, clocks, interrupts, DAI cells, widgets/routes, and chip-specific tuning properties.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this file plus `$ref` targets, and enforces required properties, array cardinality, constants, enums, and no top-level conditionals. `dtbs_check` then matches compiled DTS nodes by `compatible`, `$nodename`, or parent-schema inclusion, descends into pattern-matched children, and applies `additionalProperties` or `unevaluatedProperties` closure. Runtime flow begins only after the DTB is loaded: Linux bus, SoC, ASoC, MFD, syscon, or firmware drivers bind from compatible strings and acquire the resources described here.

## State and Persistence Behavior
The YAML itself stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: compatible strings, property names, phandle names, register tuple ordering, child-node names, and examples become contracts in source DTS files and compiled DTBs. Runtime state is created by the matched kernel drivers after probe, including regmap cache, DAPM power state, bias levels, PLL/clock configuration, jack/interrupt state, and audio stream parameters owned by ASoC drivers.

## Dependencies and Integration Points
Maintainers listed: Kuninori Morimoto <kuninori.morimoto.gx@renesas.com>, Liam Girdwood <lgirdwood@gmail.com>, Mark Brown <broonie@kernel.org>. Schema dependencies include dt-schema core/meta schemas only. Integration points include ASoC codec/component drivers, I2C/SPI/platform bus probing, DAPM graph construction, regulators, clocks, GPIO controls, and machine-driver links. The file also integrates with Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and source DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to compatible strings, bus address, reset/shutdown GPIOs, supplies, clocks, interrupts, DAI cells, widgets/routes, and chip-specific tuning properties, drift between documented compatible strings and driver match tables, incorrect resource ordering, phandle names, or cell counts that block probe or misconfigure hardware. This schema rejects unknown top-level properties with `additionalProperties: false`. Regressions usually show up as schema-check failures, boot-time probe failures, missing audio/SoC child devices, bad firmware/resource allocation, broken suspend/resume, or silent routing/clocking errors in board audio paths.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/sound/asahi-kasei,ak4554.yaml` for the targeted schema and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/sound/asahi-kasei,ak4554.yaml` against boards that instantiate it. The schema has 1 embedded example; keep those examples valid under targeted binding checks. Cross-check compatible strings against driver `of_match_table` entries and inspect DTS users for register tuple counts, interrupt names, clocks/resets, supplies, DMA channels, graph endpoints, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/asahi-kasei,ak4554.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/asahi-kasei,ak4613.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/asahi-kasei,ak4613.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/asahi-kasei,ak4613.yaml` defines the audio codec or amplifier binding titled `AK4613 I2C transmitter`. It constrains source DTS and compiled DTB hardware descriptions through compatible strings, required resources, child-node topology, and shared schema references before Linux drivers consume the node.

## Important APIs, Types, and Functions
The API surface is the devicetree ABI rather than callable code. `compatible` uses a single `const` token with 1 token: `asahi-kasei,ak4613`. Top-level properties are `compatible`, `reg`, `clocks`, `#sound-dai-cells`, `ports`, `port`. Required top-level properties are `compatible`, `reg`. Nested or reusable constraints include composition/conditionals: `allOf`; child-node patterns: `^asahi-kasei,in[1-2]-single-end$`, `^asahi-kasei,out[1-6]-single-end$`; referenced schemas: `/schemas/types.yaml#/definitions/flag`, `audio-graph-port.yaml#`, `audio-graph-port.yaml#/definitions/ports`, `dai-common.yaml#`; notable enum/const values: `0`. The highest-risk contract area is compatible strings, bus address, reset/shutdown GPIOs, supplies, clocks, interrupts, DAI cells, widgets/routes, and chip-specific tuning properties.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this file plus `$ref` targets, and enforces required properties, array cardinality, constants, enums, and `allOf`. `dtbs_check` then matches compiled DTS nodes by `compatible`, `$nodename`, or parent-schema inclusion, descends into pattern-matched children, and applies `additionalProperties` or `unevaluatedProperties` closure. Runtime flow begins only after the DTB is loaded: Linux bus, SoC, ASoC, MFD, syscon, or firmware drivers bind from compatible strings and acquire the resources described here.

## State and Persistence Behavior
The YAML itself stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: compatible strings, property names, phandle names, register tuple ordering, child-node names, and examples become contracts in source DTS files and compiled DTBs. Runtime state is created by the matched kernel drivers after probe, including regmap cache, DAPM power state, bias levels, PLL/clock configuration, jack/interrupt state, and audio stream parameters owned by ASoC drivers.

## Dependencies and Integration Points
Maintainers listed: Kuninori Morimoto <kuninori.morimoto.gx@renesas.com>. Schema dependencies include `/schemas/types.yaml#/definitions/flag`, `audio-graph-port.yaml#`, `audio-graph-port.yaml#/definitions/ports`, `dai-common.yaml#`. Integration points include ASoC codec/component drivers, I2C/SPI/platform bus probing, DAPM graph construction, regulators, clocks, GPIO controls, and machine-driver links. The file also integrates with Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and source DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to compatible strings, bus address, reset/shutdown GPIOs, supplies, clocks, interrupts, DAI cells, widgets/routes, and chip-specific tuning properties, drift between documented compatible strings and driver match tables, incorrect resource ordering, phandle names, or cell counts that block probe or misconfigure hardware, variant-specific conditional branches accepting one SoC/chip while rejecting another, child-node regexes that over-match unrelated children or under-match valid hardware nodes. This schema closes composed schemas with `unevaluatedProperties: false`. Regressions usually show up as schema-check failures, boot-time probe failures, missing audio/SoC child devices, bad firmware/resource allocation, broken suspend/resume, or silent routing/clocking errors in board audio paths.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/sound/asahi-kasei,ak4613.yaml` for the targeted schema and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/sound/asahi-kasei,ak4613.yaml` against boards that instantiate it. The schema has 1 embedded example; keep those examples valid under targeted binding checks. Include child-node validation for `^asahi-kasei,in[1-2]-single-end$`, `^asahi-kasei,out[1-6]-single-end$`. Cross-check compatible strings against driver `of_match_table` entries and inspect DTS users for register tuple counts, interrupt names, clocks/resets, supplies, DMA channels, graph endpoints, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/asahi-kasei,ak4613.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/asahi-kasei,ak4619.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/asahi-kasei,ak4619.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/asahi-kasei,ak4619.yaml` defines the audio codec or amplifier binding titled `AK4619 I2C transmitter`. It constrains source DTS and compiled DTB hardware descriptions through compatible strings, required resources, child-node topology, and shared schema references before Linux drivers consume the node.

## Important APIs, Types, and Functions
The API surface is the devicetree ABI rather than callable code. `compatible` uses a single `const` token with 1 token: `asahi-kasei,ak4619`. Top-level properties are `compatible`, `reg`, `clocks`, `clock-names`, `#sound-dai-cells`, `port`. Required top-level properties are `compatible`, `reg`. Nested or reusable constraints include composition/conditionals: `allOf`; referenced schemas: `audio-graph-port.yaml#`, `dai-common.yaml#`; notable enum/const values: `mclk`, `0`. The highest-risk contract area is compatible strings, bus address, reset/shutdown GPIOs, supplies, clocks, interrupts, DAI cells, widgets/routes, and chip-specific tuning properties.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this file plus `$ref` targets, and enforces required properties, array cardinality, constants, enums, and `allOf`. `dtbs_check` then matches compiled DTS nodes by `compatible`, `$nodename`, or parent-schema inclusion, descends into pattern-matched children, and applies `additionalProperties` or `unevaluatedProperties` closure. Runtime flow begins only after the DTB is loaded: Linux bus, SoC, ASoC, MFD, syscon, or firmware drivers bind from compatible strings and acquire the resources described here.

## State and Persistence Behavior
The YAML itself stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: compatible strings, property names, phandle names, register tuple ordering, child-node names, and examples become contracts in source DTS files and compiled DTBs. Runtime state is created by the matched kernel drivers after probe, including regmap cache, DAPM power state, bias levels, PLL/clock configuration, jack/interrupt state, and audio stream parameters owned by ASoC drivers.

## Dependencies and Integration Points
Maintainers listed: Kuninori Morimoto <kuninori.morimoto.gx@renesas.com>, Khanh Le <khanh.le.xr@renesas.com>. Schema dependencies include `audio-graph-port.yaml#`, `dai-common.yaml#`. Integration points include ASoC codec/component drivers, I2C/SPI/platform bus probing, DAPM graph construction, regulators, clocks, GPIO controls, and machine-driver links. The file also integrates with Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and source DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to compatible strings, bus address, reset/shutdown GPIOs, supplies, clocks, interrupts, DAI cells, widgets/routes, and chip-specific tuning properties, drift between documented compatible strings and driver match tables, incorrect resource ordering, phandle names, or cell counts that block probe or misconfigure hardware, variant-specific conditional branches accepting one SoC/chip while rejecting another. This schema closes composed schemas with `unevaluatedProperties: false`. Regressions usually show up as schema-check failures, boot-time probe failures, missing audio/SoC child devices, bad firmware/resource allocation, broken suspend/resume, or silent routing/clocking errors in board audio paths.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/sound/asahi-kasei,ak4619.yaml` for the targeted schema and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/sound/asahi-kasei,ak4619.yaml` against boards that instantiate it. The schema has 1 embedded example; keep those examples valid under targeted binding checks. Cross-check compatible strings against driver `of_match_table` entries and inspect DTS users for register tuple counts, interrupt names, clocks/resets, supplies, DMA channels, graph endpoints, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/asahi-kasei,ak4619.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/asahi-kasei,ak4642.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/asahi-kasei,ak4642.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/asahi-kasei,ak4642.yaml` defines the audio codec or amplifier binding titled `AK4642 I2C transmitter`. It constrains source DTS and compiled DTB hardware descriptions through compatible strings, required resources, child-node topology, and shared schema references before Linux drivers consume the node.

## Important APIs, Types, and Functions
The API surface is the devicetree ABI rather than callable code. `compatible` uses an `enum` of supported tokens with 3 tokens: `asahi-kasei,ak4642`, `asahi-kasei,ak4643`, `asahi-kasei,ak4648`. Top-level properties are `compatible`, `reg`, `#clock-cells`, `#sound-dai-cells`, `clocks`, `clock-frequency`, `clock-output-names`. Required top-level properties are `compatible`, `reg`. Nested or reusable constraints include composition/conditionals: `allOf`; referenced schemas: `dai-common.yaml#`; notable enum/const values: `0`. The highest-risk contract area is compatible strings, bus address, reset/shutdown GPIOs, supplies, clocks, interrupts, DAI cells, widgets/routes, and chip-specific tuning properties.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this file plus `$ref` targets, and enforces required properties, array cardinality, constants, enums, and `allOf`. `dtbs_check` then matches compiled DTS nodes by `compatible`, `$nodename`, or parent-schema inclusion, descends into pattern-matched children, and applies `additionalProperties` or `unevaluatedProperties` closure. Runtime flow begins only after the DTB is loaded: Linux bus, SoC, ASoC, MFD, syscon, or firmware drivers bind from compatible strings and acquire the resources described here.

## State and Persistence Behavior
The YAML itself stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: compatible strings, property names, phandle names, register tuple ordering, child-node names, and examples become contracts in source DTS files and compiled DTBs. Runtime state is created by the matched kernel drivers after probe, including regmap cache, DAPM power state, bias levels, PLL/clock configuration, jack/interrupt state, and audio stream parameters owned by ASoC drivers.

## Dependencies and Integration Points
Maintainers listed: Kuninori Morimoto <kuninori.morimoto.gx@renesas.com>. Schema dependencies include `dai-common.yaml#`. Integration points include ASoC codec/component drivers, I2C/SPI/platform bus probing, DAPM graph construction, regulators, clocks, GPIO controls, and machine-driver links. The file also integrates with Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and source DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to compatible strings, bus address, reset/shutdown GPIOs, supplies, clocks, interrupts, DAI cells, widgets/routes, and chip-specific tuning properties, drift between documented compatible strings and driver match tables, incorrect resource ordering, phandle names, or cell counts that block probe or misconfigure hardware, variant-specific conditional branches accepting one SoC/chip while rejecting another. This schema closes composed schemas with `unevaluatedProperties: false`. Regressions usually show up as schema-check failures, boot-time probe failures, missing audio/SoC child devices, bad firmware/resource allocation, broken suspend/resume, or silent routing/clocking errors in board audio paths.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/sound/asahi-kasei,ak4642.yaml` for the targeted schema and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/sound/asahi-kasei,ak4642.yaml` against boards that instantiate it. The schema has 1 embedded example; keep those examples valid under targeted binding checks. Cross-check compatible strings against driver `of_match_table` entries and inspect DTS users for register tuple counts, interrupt names, clocks/resets, supplies, DMA channels, graph endpoints, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/asahi-kasei,ak4642.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/asahi-kasei,ak5558.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/asahi-kasei,ak5558.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/asahi-kasei,ak5558.yaml` defines the audio codec or amplifier binding titled `AK5558 8 channel differential 32-bit delta-sigma ADC`. It constrains source DTS and compiled DTB hardware descriptions through compatible strings, required resources, child-node topology, and shared schema references before Linux drivers consume the node.

## Important APIs, Types, and Functions
The API surface is the devicetree ABI rather than callable code. `compatible` uses an `enum` of supported tokens with 2 tokens: `asahi-kasei,ak5552`, `asahi-kasei,ak5558`. Top-level properties are `compatible`, `reg`, `AVDD-supply`, `DVDD-supply`, `reset-gpios`. Required top-level properties are `compatible`, `reg`. Nested or reusable constraints include composition/conditionals: `allOf`; referenced schemas: `dai-common.yaml#`. The highest-risk contract area is compatible strings, bus address, reset/shutdown GPIOs, supplies, clocks, interrupts, DAI cells, widgets/routes, and chip-specific tuning properties.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this file plus `$ref` targets, and enforces required properties, array cardinality, constants, enums, and `allOf`. `dtbs_check` then matches compiled DTS nodes by `compatible`, `$nodename`, or parent-schema inclusion, descends into pattern-matched children, and applies `additionalProperties` or `unevaluatedProperties` closure. Runtime flow begins only after the DTB is loaded: Linux bus, SoC, ASoC, MFD, syscon, or firmware drivers bind from compatible strings and acquire the resources described here.

## State and Persistence Behavior
The YAML itself stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: compatible strings, property names, phandle names, register tuple ordering, child-node names, and examples become contracts in source DTS files and compiled DTBs. Runtime state is created by the matched kernel drivers after probe, including regmap cache, DAPM power state, bias levels, PLL/clock configuration, jack/interrupt state, and audio stream parameters owned by ASoC drivers.

## Dependencies and Integration Points
Maintainers listed: Junichi Wakasugi <wakasugi.jb@om.asahi-kasei.co.jp>, Mihai Serban <mihai.serban@nxp.com>. Schema dependencies include `dai-common.yaml#`. Integration points include ASoC codec/component drivers, I2C/SPI/platform bus probing, DAPM graph construction, regulators, clocks, GPIO controls, and machine-driver links. The file also integrates with Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and source DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to compatible strings, bus address, reset/shutdown GPIOs, supplies, clocks, interrupts, DAI cells, widgets/routes, and chip-specific tuning properties, drift between documented compatible strings and driver match tables, incorrect resource ordering, phandle names, or cell counts that block probe or misconfigure hardware, variant-specific conditional branches accepting one SoC/chip while rejecting another. This schema closes composed schemas with `unevaluatedProperties: false`. Regressions usually show up as schema-check failures, boot-time probe failures, missing audio/SoC child devices, bad firmware/resource allocation, broken suspend/resume, or silent routing/clocking errors in board audio paths.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/sound/asahi-kasei,ak5558.yaml` for the targeted schema and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/sound/asahi-kasei,ak5558.yaml` against boards that instantiate it. The schema has 1 embedded example; keep those examples valid under targeted binding checks. Cross-check compatible strings against driver `of_match_table` entries and inspect DTS users for register tuple counts, interrupt names, clocks/resets, supplies, DMA channels, graph endpoints, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/asahi-kasei,ak5558.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/atmel,asoc-wm8904.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/atmel,asoc-wm8904.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/atmel,asoc-wm8904.yaml` defines the audio controller or sound-card binding titled `Atmel wm8904 audio codec complex`. The ASoC audio complex configuration for Atmel with WM8904 audio codec. It constrains source DTS and compiled DTB hardware descriptions before Linux drivers consume the node.

## Important APIs, Types, and Functions
The API surface is the devicetree ABI rather than callable code. `compatible` uses a single `const` token with 1 token: `atmel,asoc-wm8904`. Top-level properties are `compatible`, `atmel,model`, `atmel,ssc-controller`, `atmel,audio-codec`, `atmel,audio-routing`. Required top-level properties are `compatible`, `atmel,model`, `atmel,audio-routing`, `atmel,ssc-controller`, `atmel,audio-codec`. Nested or reusable constraints include referenced schemas: `/schemas/types.yaml#/definitions/non-unique-string-array`, `/schemas/types.yaml#/definitions/phandle`, `/schemas/types.yaml#/definitions/string`; notable enum/const values: `Headphone Jack`, `Line In Jack`, `Mic`, `IN1L`, `IN1R`, `IN2L`, `IN2R`, `IN3L`, `IN3R`, `HPOUTL`, `HPOUTR`, `LINEOUTL`, `LINEOUTR`, `MICBIAS`. The highest-risk contract area is register and interrupt resources, clocks/resets, DMA channels, sound-dai cells, graph ports/endpoints, routing, and SoC-specific compatible strings.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this file plus `$ref` targets, and enforces required properties, array cardinality, constants, enums, and no top-level conditionals. `dtbs_check` then matches compiled DTS nodes by `compatible`, `$nodename`, or parent-schema inclusion, descends into pattern-matched children, and applies `additionalProperties` or `unevaluatedProperties` closure. Runtime flow begins only after the DTB is loaded: Linux bus, SoC, ASoC, MFD, syscon, or firmware drivers bind from compatible strings and acquire the resources described here.

## State and Persistence Behavior
The YAML itself stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: compatible strings, property names, phandle names, register tuple ordering, child-node names, and examples become contracts in source DTS files and compiled DTBs. Runtime state is created by the matched kernel drivers after probe, including DAI/controller probe state, DMA stream state, clocking, reset state, and sound-card topology owned by ASoC runtime drivers.

## Dependencies and Integration Points
Maintainers listed: Dharma Balasubiramani <dharma.b@microchip.com>. Schema dependencies include `/schemas/types.yaml#/definitions/non-unique-string-array`, `/schemas/types.yaml#/definitions/phandle`, `/schemas/types.yaml#/definitions/string`. Integration points include ASoC CPU DAI drivers, platform DMA engines, machine drivers, graph/simple-card parsing, clocks/resets, pinctrl, and board DTS sound links. The file also integrates with Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and source DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to register and interrupt resources, clocks/resets, DMA channels, sound-dai cells, graph ports/endpoints, routing, and SoC-specific compatible strings, drift between documented compatible strings and driver match tables, incorrect resource ordering, phandle names, or cell counts that block probe or misconfigure hardware. This schema rejects unknown top-level properties with `additionalProperties: false`. Regressions usually show up as schema-check failures, boot-time probe failures, missing audio/SoC child devices, bad firmware/resource allocation, broken suspend/resume, or silent routing/clocking errors in board audio paths.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/sound/atmel,asoc-wm8904.yaml` for the targeted schema and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/sound/atmel,asoc-wm8904.yaml` against boards that instantiate it. The schema has 1 embedded example; keep those examples valid under targeted binding checks. Cross-check compatible strings against driver `of_match_table` entries and inspect DTS users for register tuple counts, interrupt names, clocks/resets, supplies, DMA channels, graph endpoints, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/atmel,asoc-wm8904.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/atmel,at91-ssc.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/atmel,at91-ssc.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/atmel,at91-ssc.yaml` defines the audio controller or sound-card binding titled `Atmel Serial Synchronous Serial (SSC)`. The Atmel Synchronous Serial Controller (SSC) provides a versatile synchronous communication link for audio and telecom applications, supporting protocols like I2S, Short Frame Sync, and Long Frame Sync. It constrains source DTS and compiled DTB hardware descriptions before Linux drivers consume the node.

## Important APIs, Types, and Functions
The API surface is the devicetree ABI rather than callable code. `compatible` uses `oneOf` with 2 branches with 3 tokens: `atmel,at91rm9200-ssc`, `atmel,at91sam9g45-ssc`, `microchip,sam9x7-ssc`. Top-level properties are `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `dmas`, `dma-names`, `atmel,clk-from-rk-pin`, `#sound-dai-cells`. Required top-level properties are `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`. Nested or reusable constraints include composition/conditionals: `allOf`; referenced schemas: `dai-common.yaml#`; notable enum/const values: `pclk`, `tx`, `rx`, `0`. The highest-risk contract area is register and interrupt resources, clocks/resets, DMA channels, sound-dai cells, graph ports/endpoints, routing, and SoC-specific compatible strings.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this file plus `$ref` targets, and enforces required properties, array cardinality, constants, enums, and `allOf`. `dtbs_check` then matches compiled DTS nodes by `compatible`, `$nodename`, or parent-schema inclusion, descends into pattern-matched children, and applies `additionalProperties` or `unevaluatedProperties` closure. Runtime flow begins only after the DTB is loaded: Linux bus, SoC, ASoC, MFD, syscon, or firmware drivers bind from compatible strings and acquire the resources described here.

## State and Persistence Behavior
The YAML itself stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: compatible strings, property names, phandle names, register tuple ordering, child-node names, and examples become contracts in source DTS files and compiled DTBs. Runtime state is created by the matched kernel drivers after probe, including DAI/controller probe state, DMA stream state, clocking, reset state, and sound-card topology owned by ASoC runtime drivers.

## Dependencies and Integration Points
Maintainers listed: Andrei Simion <andrei.simion@microchip.com>. Schema dependencies include `dai-common.yaml#`. Integration points include ASoC CPU DAI drivers, platform DMA engines, machine drivers, graph/simple-card parsing, clocks/resets, pinctrl, and board DTS sound links. The file also integrates with Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and source DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to register and interrupt resources, clocks/resets, DMA channels, sound-dai cells, graph ports/endpoints, routing, and SoC-specific compatible strings, drift between documented compatible strings and driver match tables, incorrect resource ordering, phandle names, or cell counts that block probe or misconfigure hardware, variant-specific conditional branches accepting one SoC/chip while rejecting another. This schema closes composed schemas with `unevaluatedProperties: false`. Regressions usually show up as schema-check failures, boot-time probe failures, missing audio/SoC child devices, bad firmware/resource allocation, broken suspend/resume, or silent routing/clocking errors in board audio paths.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/sound/atmel,at91-ssc.yaml` for the targeted schema and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/sound/atmel,at91-ssc.yaml` against boards that instantiate it. The schema has 1 embedded example; keep those examples valid under targeted binding checks. Cross-check compatible strings against driver `of_match_table` entries and inspect DTS users for register tuple counts, interrupt names, clocks/resets, supplies, DMA channels, graph endpoints, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/atmel,at91-ssc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/atmel,at91sam9g20ek-wm8731.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/atmel,at91sam9g20ek-wm8731.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/atmel,at91sam9g20ek-wm8731.yaml` defines the audio controller or sound-card binding titled `Atmel at91sam9g20ek wm8731 audio complex`. The audio complex configuration for Atmel at91sam9g20ek with WM8731 audio codec. It constrains source DTS and compiled DTB hardware descriptions before Linux drivers consume the node.

## Important APIs, Types, and Functions
The API surface is the devicetree ABI rather than callable code. `compatible` uses a single `const` token with 1 token: `atmel,at91sam9g20ek-wm8731-audio`. Top-level properties are `compatible`, `atmel,model`, `atmel,audio-routing`, `atmel,ssc-controller`, `atmel,audio-codec`. Required top-level properties are `compatible`, `atmel,model`, `atmel,audio-routing`, `atmel,ssc-controller`, `atmel,audio-codec`. Nested or reusable constraints include referenced schemas: `/schemas/types.yaml#/definitions/non-unique-string-array`, `/schemas/types.yaml#/definitions/phandle`, `/schemas/types.yaml#/definitions/string`; notable enum/const values: `Ext Spk`, `Int Mic`, `LOUT`, `ROUT`, `LHPOUT`, `RHPOUT`, `LLINEIN`, `RLINEIN`, `MICIN`. The highest-risk contract area is register and interrupt resources, clocks/resets, DMA channels, sound-dai cells, graph ports/endpoints, routing, and SoC-specific compatible strings.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this file plus `$ref` targets, and enforces required properties, array cardinality, constants, enums, and no top-level conditionals. `dtbs_check` then matches compiled DTS nodes by `compatible`, `$nodename`, or parent-schema inclusion, descends into pattern-matched children, and applies `additionalProperties` or `unevaluatedProperties` closure. Runtime flow begins only after the DTB is loaded: Linux bus, SoC, ASoC, MFD, syscon, or firmware drivers bind from compatible strings and acquire the resources described here.

## State and Persistence Behavior
The YAML itself stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: compatible strings, property names, phandle names, register tuple ordering, child-node names, and examples become contracts in source DTS files and compiled DTBs. Runtime state is created by the matched kernel drivers after probe, including DAI/controller probe state, DMA stream state, clocking, reset state, and sound-card topology owned by ASoC runtime drivers.

## Dependencies and Integration Points
Maintainers listed: Balakrishnan Sambath <balakrishnan.s@microchip.com>. Schema dependencies include `/schemas/types.yaml#/definitions/non-unique-string-array`, `/schemas/types.yaml#/definitions/phandle`, `/schemas/types.yaml#/definitions/string`. Integration points include ASoC CPU DAI drivers, platform DMA engines, machine drivers, graph/simple-card parsing, clocks/resets, pinctrl, and board DTS sound links. The file also integrates with Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and source DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to register and interrupt resources, clocks/resets, DMA channels, sound-dai cells, graph ports/endpoints, routing, and SoC-specific compatible strings, drift between documented compatible strings and driver match tables, incorrect resource ordering, phandle names, or cell counts that block probe or misconfigure hardware. This schema rejects unknown top-level properties with `additionalProperties: false`. Regressions usually show up as schema-check failures, boot-time probe failures, missing audio/SoC child devices, bad firmware/resource allocation, broken suspend/resume, or silent routing/clocking errors in board audio paths.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/sound/atmel,at91sam9g20ek-wm8731.yaml` for the targeted schema and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/sound/atmel,at91sam9g20ek-wm8731.yaml` against boards that instantiate it. The schema has 1 embedded example; keep those examples valid under targeted binding checks. Cross-check compatible strings against driver `of_match_table` entries and inspect DTS users for register tuple counts, interrupt names, clocks/resets, supplies, DMA channels, graph endpoints, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/atmel,at91sam9g20ek-wm8731.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/atmel,sam9x5-wm8731-audio.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/atmel,sam9x5-wm8731-audio.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/atmel,sam9x5-wm8731-audio.yaml` defines the audio controller or sound-card binding titled `Atmel at91sam9x5ek wm8731 audio complex`. The audio complex configuration for Atmel at91sam9x5ek with WM8731 audio codec. It constrains source DTS and compiled DTB hardware descriptions before Linux drivers consume the node.

## Important APIs, Types, and Functions
The API surface is the devicetree ABI rather than callable code. `compatible` uses a single `const` token with 1 token: `atmel,sam9x5-wm8731-audio`. Top-level properties are `compatible`, `atmel,model`, `atmel,ssc-controller`, `atmel,audio-codec`, `atmel,audio-routing`. Required top-level properties are `compatible`, `atmel,model`, `atmel,ssc-controller`, `atmel,audio-codec`, `atmel,audio-routing`. Nested or reusable constraints include referenced schemas: `/schemas/types.yaml#/definitions/non-unique-string-array`, `/schemas/types.yaml#/definitions/phandle`, `/schemas/types.yaml#/definitions/string`; notable enum/const values: `Headphone Jack`, `Line In Jack`, `LOUT`, `ROUT`, `LHPOUT`, `RHPOUT`, `LLINEIN`, `RLINEIN`, `MICIN`. The highest-risk contract area is register and interrupt resources, clocks/resets, DMA channels, sound-dai cells, graph ports/endpoints, routing, and SoC-specific compatible strings.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this file plus `$ref` targets, and enforces required properties, array cardinality, constants, enums, and no top-level conditionals. `dtbs_check` then matches compiled DTS nodes by `compatible`, `$nodename`, or parent-schema inclusion, descends into pattern-matched children, and applies `additionalProperties` or `unevaluatedProperties` closure. Runtime flow begins only after the DTB is loaded: Linux bus, SoC, ASoC, MFD, syscon, or firmware drivers bind from compatible strings and acquire the resources described here.

## State and Persistence Behavior
The YAML itself stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: compatible strings, property names, phandle names, register tuple ordering, child-node names, and examples become contracts in source DTS files and compiled DTBs. Runtime state is created by the matched kernel drivers after probe, including DAI/controller probe state, DMA stream state, clocking, reset state, and sound-card topology owned by ASoC runtime drivers.

## Dependencies and Integration Points
Maintainers listed: Dharma Balasubiramani <dharma.b@microchip.com>. Schema dependencies include `/schemas/types.yaml#/definitions/non-unique-string-array`, `/schemas/types.yaml#/definitions/phandle`, `/schemas/types.yaml#/definitions/string`. Integration points include ASoC CPU DAI drivers, platform DMA engines, machine drivers, graph/simple-card parsing, clocks/resets, pinctrl, and board DTS sound links. The file also integrates with Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and source DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to register and interrupt resources, clocks/resets, DMA channels, sound-dai cells, graph ports/endpoints, routing, and SoC-specific compatible strings, drift between documented compatible strings and driver match tables, incorrect resource ordering, phandle names, or cell counts that block probe or misconfigure hardware. This schema rejects unknown top-level properties with `additionalProperties: false`. Regressions usually show up as schema-check failures, boot-time probe failures, missing audio/SoC child devices, bad firmware/resource allocation, broken suspend/resume, or silent routing/clocking errors in board audio paths.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/sound/atmel,sam9x5-wm8731-audio.yaml` for the targeted schema and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/sound/atmel,sam9x5-wm8731-audio.yaml` against boards that instantiate it. The schema has 1 embedded example; keep those examples valid under targeted binding checks. Cross-check compatible strings against driver `of_match_table` entries and inspect DTS users for register tuple counts, interrupt names, clocks/resets, supplies, DMA channels, graph endpoints, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/atmel,sam9x5-wm8731-audio.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/atmel,sama5d2-classd.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/atmel,sama5d2-classd.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/atmel,sama5d2-classd.yaml` defines the audio controller or sound-card binding titled `Atmel ClassD Amplifier`. The Audio Class D Amplifier (CLASSD) is a digital input, Pulse Width Modulated (PWM) output stereo Class D amplifier. It constrains source DTS and compiled DTB hardware descriptions before Linux drivers consume the node.

## Important APIs, Types, and Functions
The API surface is the devicetree ABI rather than callable code. `compatible` uses `oneOf` with 2 branches with 2 tokens: `atmel,sama5d2-classd`, `microchip,sam9x7-classd`. Top-level properties are `compatible`, `reg`, `interrupts`, `dmas`, `dma-names`, `clocks`, `clock-names`, `atmel,model`, `atmel,pwm-type`, `atmel,non-overlap-time`. Required top-level properties are `compatible`, `reg`, `interrupts`, `dmas`, `dma-names`, `clock-names`, `clocks`. Nested or reusable constraints include referenced schemas: `/schemas/types.yaml#/definitions/string`, `/schemas/types.yaml#/definitions/uint32`; notable enum/const values: `single`, `diff`, `5`, `10`, `15`, `20`, `tx`, `pclk`, `gclk`. The highest-risk contract area is register and interrupt resources, clocks/resets, DMA channels, sound-dai cells, graph ports/endpoints, routing, and SoC-specific compatible strings.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this file plus `$ref` targets, and enforces required properties, array cardinality, constants, enums, and no top-level conditionals. `dtbs_check` then matches compiled DTS nodes by `compatible`, `$nodename`, or parent-schema inclusion, descends into pattern-matched children, and applies `additionalProperties` or `unevaluatedProperties` closure. Runtime flow begins only after the DTB is loaded: Linux bus, SoC, ASoC, MFD, syscon, or firmware drivers bind from compatible strings and acquire the resources described here.

## State and Persistence Behavior
The YAML itself stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: compatible strings, property names, phandle names, register tuple ordering, child-node names, and examples become contracts in source DTS files and compiled DTBs. Runtime state is created by the matched kernel drivers after probe, including DAI/controller probe state, DMA stream state, clocking, reset state, and sound-card topology owned by ASoC runtime drivers.

## Dependencies and Integration Points
Maintainers listed: Nicolas Ferre <nicolas.ferre@microchip.com>, Alexandre Belloni <alexandre.belloni@bootlin.com>, Claudiu Beznea <claudiu.beznea@microchip.com>. Schema dependencies include `/schemas/types.yaml#/definitions/string`, `/schemas/types.yaml#/definitions/uint32`. Integration points include ASoC CPU DAI drivers, platform DMA engines, machine drivers, graph/simple-card parsing, clocks/resets, pinctrl, and board DTS sound links. The file also integrates with Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and source DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to register and interrupt resources, clocks/resets, DMA channels, sound-dai cells, graph ports/endpoints, routing, and SoC-specific compatible strings, drift between documented compatible strings and driver match tables, incorrect resource ordering, phandle names, or cell counts that block probe or misconfigure hardware. This schema rejects unknown top-level properties with `additionalProperties: false`. Regressions usually show up as schema-check failures, boot-time probe failures, missing audio/SoC child devices, bad firmware/resource allocation, broken suspend/resume, or silent routing/clocking errors in board audio paths.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/sound/atmel,sama5d2-classd.yaml` for the targeted schema and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/sound/atmel,sama5d2-classd.yaml` against boards that instantiate it. The schema has 1 embedded example; keep those examples valid under targeted binding checks. Cross-check compatible strings against driver `of_match_table` entries and inspect DTS users for register tuple counts, interrupt names, clocks/resets, supplies, DMA channels, graph endpoints, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/atmel,sama5d2-classd.yaml -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/atmel,sama5d2-pdmic.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/atmel,sama5d2-pdmic.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/atmel,sama5d2-pdmic.yaml` defines the audio controller or sound-card binding titled `Atmel PDMIC decoder`. Atmel Pulse Density Modulation Interface Controller (PDMIC) peripheral is a mono PDM decoder module that decodes an incoming PDM sample stream. It constrains source DTS and compiled DTB hardware descriptions before Linux drivers consume the node.

## Important APIs, Types, and Functions
The API surface is the devicetree ABI rather than callable code. `compatible` uses a single `const` token with 1 token: `atmel,sama5d2-pdmic`. Top-level properties are `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `dmas`, `dma-names`, `atmel,mic-min-freq`, `atmel,mic-max-freq`, `atmel,model`, `atmel,mic-offset`. Required top-level properties are `compatible`, `reg`, `interrupts`, `dmas`, `dma-names`, `clock-names`, `clocks`, `atmel,mic-min-freq`, `atmel,mic-max-freq`. Nested or reusable constraints include referenced schemas: `/schemas/types.yaml#/definitions/int32`, `/schemas/types.yaml#/definitions/string`, `/schemas/types.yaml#/definitions/uint32`; notable enum/const values: `pclk`, `gclk`, `rx`. The highest-risk contract area is register and interrupt resources, clocks/resets, DMA channels, sound-dai cells, graph ports/endpoints, routing, and SoC-specific compatible strings.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this file plus `$ref` targets, and enforces required properties, array cardinality, constants, enums, and no top-level conditionals. `dtbs_check` then matches compiled DTS nodes by `compatible`, `$nodename`, or parent-schema inclusion, descends into pattern-matched children, and applies `additionalProperties` or `unevaluatedProperties` closure. Runtime flow begins only after the DTB is loaded: Linux bus, SoC, ASoC, MFD, syscon, or firmware drivers bind from compatible strings and acquire the resources described here.

## State and Persistence Behavior
The YAML itself stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: compatible strings, property names, phandle names, register tuple ordering, child-node names, and examples become contracts in source DTS files and compiled DTBs. Runtime state is created by the matched kernel drivers after probe, including DAI/controller probe state, DMA stream state, clocking, reset state, and sound-card topology owned by ASoC runtime drivers.

## Dependencies and Integration Points
Maintainers listed: Claudiu Beznea <claudiu.beznea@microchip.com>. Schema dependencies include `/schemas/types.yaml#/definitions/int32`, `/schemas/types.yaml#/definitions/string`, `/schemas/types.yaml#/definitions/uint32`. Integration points include ASoC CPU DAI drivers, platform DMA engines, machine drivers, graph/simple-card parsing, clocks/resets, pinctrl, and board DTS sound links. The file also integrates with Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and source DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to register and interrupt resources, clocks/resets, DMA channels, sound-dai cells, graph ports/endpoints, routing, and SoC-specific compatible strings, drift between documented compatible strings and driver match tables, incorrect resource ordering, phandle names, or cell counts that block probe or misconfigure hardware. This schema rejects unknown top-level properties with `additionalProperties: false`. Regressions usually show up as schema-check failures, boot-time probe failures, missing audio/SoC child devices, bad firmware/resource allocation, broken suspend/resume, or silent routing/clocking errors in board audio paths.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/sound/atmel,sama5d2-pdmic.yaml` for the targeted schema and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/sound/atmel,sama5d2-pdmic.yaml` against boards that instantiate it. The schema has 1 embedded example; keep those examples valid under targeted binding checks. Cross-check compatible strings against driver `of_match_table` entries and inspect DTS users for register tuple counts, interrupt names, clocks/resets, supplies, DMA channels, graph endpoints, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/atmel,sama5d2-pdmic.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/audio-graph-card.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/audio-graph-card.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/audio-graph-card.yaml` defines the reusable ASoC graph/common binding titled `Audio Graph Card`. It constrains source DTS and compiled DTB hardware descriptions through compatible strings, required resources, child-node topology, and shared schema references before Linux drivers consume the node.

## Important APIs, Types, and Functions
The API surface is the devicetree ABI rather than callable code. `compatible` uses an `enum` of supported tokens with 2 tokens: `audio-graph-card`, `audio-graph-scu-card`. Top-level properties are `compatible`. Required top-level properties are `compatible`. Nested or reusable constraints include composition/conditionals: `allOf`; referenced schemas: `/schemas/sound/audio-graph.yaml#`. The highest-risk contract area is sound-dai links, endpoint graph topology, DAI format and clock-master flags, routing/widgets, and reusable component constraints.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this file plus `$ref` targets, and enforces required properties, array cardinality, constants, enums, and `allOf`. `dtbs_check` then matches compiled DTS nodes by `compatible`, `$nodename`, or parent-schema inclusion, descends into pattern-matched children, and applies `additionalProperties` or `unevaluatedProperties` closure. Runtime flow begins only after the DTB is loaded: Linux bus, SoC, ASoC, MFD, syscon, or firmware drivers bind from compatible strings and acquire the resources described here.

## State and Persistence Behavior
The YAML itself stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: compatible strings, property names, phandle names, register tuple ordering, child-node names, and examples become contracts in source DTS files and compiled DTBs. Runtime state is created by the matched kernel drivers after probe, including ASoC card/link topology, endpoint phandle resolution, DAI format negotiation, and runtime stream state owned by sound drivers.

## Dependencies and Integration Points
Maintainers listed: Kuninori Morimoto <kuninori.morimoto.gx@renesas.com>. Schema dependencies include `/schemas/sound/audio-graph.yaml#`. Integration points include ASoC card parsing, graph-card endpoint walking, DAI link construction, codec/component schemas, and DTS sound-card validation. The file also integrates with Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and source DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to sound-dai links, endpoint graph topology, DAI format and clock-master flags, routing/widgets, and reusable component constraints, drift between documented compatible strings and driver match tables, incorrect resource ordering, phandle names, or cell counts that block probe or misconfigure hardware, variant-specific conditional branches accepting one SoC/chip while rejecting another. This schema closes composed schemas with `unevaluatedProperties: false`. Regressions usually show up as schema-check failures, boot-time probe failures, missing audio/SoC child devices, bad firmware/resource allocation, broken suspend/resume, or silent routing/clocking errors in board audio paths.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/sound/audio-graph-card.yaml` for the targeted schema and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/sound/audio-graph-card.yaml` against boards that instantiate it. The schema has 1 embedded example; keep those examples valid under targeted binding checks. Cross-check compatible strings against driver `of_match_table` entries and inspect DTS users for register tuple counts, interrupt names, clocks/resets, supplies, DMA channels, graph endpoints, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/audio-graph-card.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/audio-graph-card2.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/audio-graph-card2.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/audio-graph-card2.yaml` defines the reusable ASoC graph/common binding titled `Audio Graph Card2`. It constrains source DTS and compiled DTB hardware descriptions through compatible strings, required resources, child-node topology, and shared schema references before Linux drivers consume the node.

## Important APIs, Types, and Functions
The API surface is the devicetree ABI rather than callable code. `compatible` uses an `enum` of supported tokens with 1 token: `audio-graph-card2`. Top-level properties are `compatible`, `links`, `label`, `routing`, `aux-devs`, `multi`, `dpcm`, `codec2codec`, `hp-det-gpios`, `mic-det-gpios`, `widgets`. Required top-level properties are `compatible`, `links`. Nested or reusable constraints include referenced schemas: `/schemas/types.yaml#/definitions/phandle-array`, `audio-graph.yaml#/properties/hp-det-gpios`, `audio-graph.yaml#/properties/mic-det-gpios`, `audio-graph.yaml#/properties/routing`, `audio-graph.yaml#/properties/widgets`. The highest-risk contract area is sound-dai links, endpoint graph topology, DAI format and clock-master flags, routing/widgets, and reusable component constraints.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this file plus `$ref` targets, and enforces required properties, array cardinality, constants, enums, and no top-level conditionals. `dtbs_check` then matches compiled DTS nodes by `compatible`, `$nodename`, or parent-schema inclusion, descends into pattern-matched children, and applies `additionalProperties` or `unevaluatedProperties` closure. Runtime flow begins only after the DTB is loaded: Linux bus, SoC, ASoC, MFD, syscon, or firmware drivers bind from compatible strings and acquire the resources described here.

## State and Persistence Behavior
The YAML itself stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: compatible strings, property names, phandle names, register tuple ordering, child-node names, and examples become contracts in source DTS files and compiled DTBs. Runtime state is created by the matched kernel drivers after probe, including ASoC card/link topology, endpoint phandle resolution, DAI format negotiation, and runtime stream state owned by sound drivers.

## Dependencies and Integration Points
Maintainers listed: Kuninori Morimoto <kuninori.morimoto.gx@renesas.com>. Schema dependencies include `/schemas/types.yaml#/definitions/phandle-array`, `audio-graph.yaml#/properties/hp-det-gpios`, `audio-graph.yaml#/properties/mic-det-gpios`, `audio-graph.yaml#/properties/routing`, `audio-graph.yaml#/properties/widgets`. Integration points include ASoC card parsing, graph-card endpoint walking, DAI link construction, codec/component schemas, and DTS sound-card validation. The file also integrates with Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and source DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to sound-dai links, endpoint graph topology, DAI format and clock-master flags, routing/widgets, and reusable component constraints, drift between documented compatible strings and driver match tables, incorrect resource ordering, phandle names, or cell counts that block probe or misconfigure hardware, lack of embedded examples, leaving coverage dependent on in-tree DTS users. This schema rejects unknown top-level properties with `additionalProperties: false`. Regressions usually show up as schema-check failures, boot-time probe failures, missing audio/SoC child devices, bad firmware/resource allocation, broken suspend/resume, or silent routing/clocking errors in board audio paths.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/sound/audio-graph-card2.yaml` for the targeted schema and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/sound/audio-graph-card2.yaml` against boards that instantiate it. There are no embedded examples, so real DTS users and schema-only checks are the main coverage. Cross-check compatible strings against driver `of_match_table` entries and inspect DTS users for register tuple counts, interrupt names, clocks/resets, supplies, DMA channels, graph endpoints, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/audio-graph-card2.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/audio-graph-port.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/audio-graph-port.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/audio-graph-port.yaml` defines the reusable ASoC graph/common binding titled `Audio Graph Card 'port'`. It constrains source DTS and compiled DTB hardware descriptions through compatible strings, required resources, child-node topology, and shared schema references before Linux drivers consume the node.

## Important APIs, Types, and Functions
The API surface is the devicetree ABI rather than callable code. This is a reusable schema fragment, so its exported API is the properties it contributes to including bindings. Top-level properties are none. Required top-level properties are none declared. Nested or reusable constraints include composition/conditionals: `allOf`; child-node patterns: `^endpoint(@[0-9a-f]+)?`; referenced schemas: `#/definitions/endpoint-base`, `#/definitions/port-base`, `/schemas/graph.yaml#/$defs/endpoint-base`, `/schemas/graph.yaml#/$defs/port-base`, `/schemas/sound/dai-params.yaml#`, `/schemas/types.yaml#/definitions/flag`, `/schemas/types.yaml#/definitions/phandle`, `/schemas/types.yaml#/definitions/uint32`, `/schemas/types.yaml#/definitions/uint32-array`, `/schemas/types.yaml#/definitions/uint32-matrix`, `simple-card.yaml#/definitions/mclk-fs`, `simple-card.yaml#/definitions/system-clock-direction-out`, and 2 more; notable enum/const values: `i2s`, `right_j`, `left_j`, `dsp_a`, `dsp_b`, `ac97`, `pdm`, `msb`, `lsb`. The highest-risk contract area is sound-dai links, endpoint graph topology, DAI format and clock-master flags, routing/widgets, and reusable component constraints.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this file plus `$ref` targets, and enforces required properties, array cardinality, constants, enums, and `allOf`. `dtbs_check` then matches compiled DTS nodes by `compatible`, `$nodename`, or parent-schema inclusion, descends into pattern-matched children, and applies `additionalProperties` or `unevaluatedProperties` closure. Runtime flow begins only after the DTB is loaded: Linux bus, SoC, ASoC, MFD, syscon, or firmware drivers bind from compatible strings and acquire the resources described here.

## State and Persistence Behavior
The YAML itself stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: compatible strings, property names, phandle names, register tuple ordering, child-node names, and examples become contracts in source DTS files and compiled DTBs. Runtime state is created by the matched kernel drivers after probe, including ASoC card/link topology, endpoint phandle resolution, DAI format negotiation, and runtime stream state owned by sound drivers.

## Dependencies and Integration Points
Maintainers listed: Kuninori Morimoto <kuninori.morimoto.gx@renesas.com>. Schema dependencies include `#/definitions/endpoint-base`, `#/definitions/port-base`, `/schemas/graph.yaml#/$defs/endpoint-base`, `/schemas/graph.yaml#/$defs/port-base`, `/schemas/sound/dai-params.yaml#`, `/schemas/types.yaml#/definitions/flag`, `/schemas/types.yaml#/definitions/phandle`, `/schemas/types.yaml#/definitions/uint32`, `/schemas/types.yaml#/definitions/uint32-array`, `/schemas/types.yaml#/definitions/uint32-matrix`, `simple-card.yaml#/definitions/mclk-fs`, `simple-card.yaml#/definitions/system-clock-direction-out`, `simple-card.yaml#/definitions/system-clock-fixed`, `simple-card.yaml#/definitions/system-clock-frequency`. Integration points include ASoC card parsing, graph-card endpoint walking, DAI link construction, codec/component schemas, and DTS sound-card validation. The file also integrates with Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and source DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to sound-dai links, endpoint graph topology, DAI format and clock-master flags, routing/widgets, and reusable component constraints, drift between documented compatible strings and driver match tables, incorrect resource ordering, phandle names, or cell counts that block probe or misconfigure hardware, variant-specific conditional branches accepting one SoC/chip while rejecting another, child-node regexes that over-match unrelated children or under-match valid hardware nodes, permissive extra properties that can hide spelling mistakes, lack of embedded examples, leaving coverage dependent on in-tree DTS users. This schema permits additional top-level properties. Regressions usually show up as schema-check failures, boot-time probe failures, missing audio/SoC child devices, bad firmware/resource allocation, broken suspend/resume, or silent routing/clocking errors in board audio paths.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/sound/audio-graph-port.yaml` for the targeted schema and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/sound/audio-graph-port.yaml` against boards that instantiate it. There are no embedded examples, so real DTS users and schema-only checks are the main coverage. Include child-node validation for `^endpoint(@[0-9a-f]+)?`. Cross-check compatible strings against driver `of_match_table` entries and inspect DTS users for register tuple counts, interrupt names, clocks/resets, supplies, DMA channels, graph endpoints, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/audio-graph-port.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/audio-graph.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/audio-graph.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/audio-graph.yaml` defines the reusable ASoC graph/common binding titled `Audio Graph`. It constrains source DTS and compiled DTB hardware descriptions through compatible strings, required resources, child-node topology, and shared schema references before Linux drivers consume the node.

## Important APIs, Types, and Functions
The API surface is the devicetree ABI rather than callable code. This is a reusable schema fragment, so its exported API is the properties it contributes to including bindings. Top-level properties are `dais`, `label`, `prefix`, `routing`, `widgets`, `pa-gpios`, `hp-det-gpio`, `hp-det-gpios`, `mic-det-gpio`, `mic-det-gpios`. Required top-level properties are `dais`. Nested or reusable constraints include composition/conditionals: `allOf`; referenced schemas: `/schemas/sound/dai-params.yaml#`, `/schemas/types.yaml#/definitions/non-unique-string-array`, `/schemas/types.yaml#/definitions/phandle-array`, `/schemas/types.yaml#/definitions/string`. The highest-risk contract area is sound-dai links, endpoint graph topology, DAI format and clock-master flags, routing/widgets, and reusable component constraints.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this file plus `$ref` targets, and enforces required properties, array cardinality, constants, enums, and `allOf`. `dtbs_check` then matches compiled DTS nodes by `compatible`, `$nodename`, or parent-schema inclusion, descends into pattern-matched children, and applies `additionalProperties` or `unevaluatedProperties` closure. Runtime flow begins only after the DTB is loaded: Linux bus, SoC, ASoC, MFD, syscon, or firmware drivers bind from compatible strings and acquire the resources described here.

## State and Persistence Behavior
The YAML itself stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: compatible strings, property names, phandle names, register tuple ordering, child-node names, and examples become contracts in source DTS files and compiled DTBs. Runtime state is created by the matched kernel drivers after probe, including ASoC card/link topology, endpoint phandle resolution, DAI format negotiation, and runtime stream state owned by sound drivers.

## Dependencies and Integration Points
Maintainers listed: Kuninori Morimoto <kuninori.morimoto.gx@renesas.com>. Schema dependencies include `/schemas/sound/dai-params.yaml#`, `/schemas/types.yaml#/definitions/non-unique-string-array`, `/schemas/types.yaml#/definitions/phandle-array`, `/schemas/types.yaml#/definitions/string`. Integration points include ASoC card parsing, graph-card endpoint walking, DAI link construction, codec/component schemas, and DTS sound-card validation. The file also integrates with Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and source DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to sound-dai links, endpoint graph topology, DAI format and clock-master flags, routing/widgets, and reusable component constraints, drift between documented compatible strings and driver match tables, incorrect resource ordering, phandle names, or cell counts that block probe or misconfigure hardware, variant-specific conditional branches accepting one SoC/chip while rejecting another, permissive extra properties that can hide spelling mistakes, lack of embedded examples, leaving coverage dependent on in-tree DTS users. This schema permits additional top-level properties. Regressions usually show up as schema-check failures, boot-time probe failures, missing audio/SoC child devices, bad firmware/resource allocation, broken suspend/resume, or silent routing/clocking errors in board audio paths.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/sound/audio-graph.yaml` for the targeted schema and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/sound/audio-graph.yaml` against boards that instantiate it. There are no embedded examples, so real DTS users and schema-only checks are the main coverage. Cross-check compatible strings against driver `of_match_table` entries and inspect DTS users for register tuple counts, interrupt names, clocks/resets, supplies, DMA channels, graph endpoints, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/audio-graph.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/audio-iio-aux.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/audio-iio-aux.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/audio-iio-aux.yaml` defines the audio controller or sound-card binding titled `Audio IIO auxiliary`. Auxiliary device based on Industrial I/O device channels It constrains source DTS and compiled DTB hardware descriptions before Linux drivers consume the node.

## Important APIs, Types, and Functions
The API surface is the devicetree ABI rather than callable code. `compatible` uses a single `const` token with 1 token: `audio-iio-aux`. Top-level properties are `compatible`, `io-channels`, `io-channel-names`, `snd-control-invert-range`. Required top-level properties are `compatible`, `io-channels`, `io-channel-names`. Nested or reusable constraints include composition/conditionals: `allOf`; referenced schemas: `/schemas/types.yaml#/definitions/uint32-array`, `dai-common.yaml#`; notable enum/const values: `0`, `1`. The highest-risk contract area is register and interrupt resources, clocks/resets, DMA channels, sound-dai cells, graph ports/endpoints, routing, and SoC-specific compatible strings.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this file plus `$ref` targets, and enforces required properties, array cardinality, constants, enums, and `allOf`. `dtbs_check` then matches compiled DTS nodes by `compatible`, `$nodename`, or parent-schema inclusion, descends into pattern-matched children, and applies `additionalProperties` or `unevaluatedProperties` closure. Runtime flow begins only after the DTB is loaded: Linux bus, SoC, ASoC, MFD, syscon, or firmware drivers bind from compatible strings and acquire the resources described here.

## State and Persistence Behavior
The YAML itself stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: compatible strings, property names, phandle names, register tuple ordering, child-node names, and examples become contracts in source DTS files and compiled DTBs. Runtime state is created by the matched kernel drivers after probe, including DAI/controller probe state, DMA stream state, clocking, reset state, and sound-card topology owned by ASoC runtime drivers.

## Dependencies and Integration Points
Maintainers listed: Herve Codina <herve.codina@bootlin.com>. Schema dependencies include `/schemas/types.yaml#/definitions/uint32-array`, `dai-common.yaml#`. Integration points include ASoC CPU DAI drivers, platform DMA engines, machine drivers, graph/simple-card parsing, clocks/resets, pinctrl, and board DTS sound links. The file also integrates with Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and source DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to register and interrupt resources, clocks/resets, DMA channels, sound-dai cells, graph ports/endpoints, routing, and SoC-specific compatible strings, drift between documented compatible strings and driver match tables, incorrect resource ordering, phandle names, or cell counts that block probe or misconfigure hardware, variant-specific conditional branches accepting one SoC/chip while rejecting another. This schema closes composed schemas with `unevaluatedProperties: false`. Regressions usually show up as schema-check failures, boot-time probe failures, missing audio/SoC child devices, bad firmware/resource allocation, broken suspend/resume, or silent routing/clocking errors in board audio paths.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/sound/audio-iio-aux.yaml` for the targeted schema and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/sound/audio-iio-aux.yaml` against boards that instantiate it. The schema has 1 embedded example; keep those examples valid under targeted binding checks. Cross-check compatible strings against driver `of_match_table` entries and inspect DTS users for register tuple counts, interrupt names, clocks/resets, supplies, DMA channels, graph endpoints, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/audio-iio-aux.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/awinic,aw8738.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/awinic,aw8738.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/awinic,aw8738.yaml` defines the audio codec or amplifier binding titled `Awinic AW8738 Audio Amplifier`. The Awinic AW8738 is a simple audio amplifier with different operation modes (set using one-wire pulse control). It constrains source DTS and compiled DTB hardware descriptions before Linux drivers consume the node.

## Important APIs, Types, and Functions
The API surface is the devicetree ABI rather than callable code. `compatible` uses a single `const` token with 1 token: `awinic,aw8738`. Top-level properties are `compatible`, `mode-gpios`, `awinic,mode`, `sound-name-prefix`. Required top-level properties are `compatible`, `mode-gpios`, `awinic,mode`. Nested or reusable constraints include composition/conditionals: `allOf`; referenced schemas: `/schemas/types.yaml#/definitions/uint32`, `dai-common.yaml#`. The highest-risk contract area is compatible strings, bus address, reset/shutdown GPIOs, supplies, clocks, interrupts, DAI cells, widgets/routes, and chip-specific tuning properties.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this file plus `$ref` targets, and enforces required properties, array cardinality, constants, enums, and `allOf`. `dtbs_check` then matches compiled DTS nodes by `compatible`, `$nodename`, or parent-schema inclusion, descends into pattern-matched children, and applies `additionalProperties` or `unevaluatedProperties` closure. Runtime flow begins only after the DTB is loaded: Linux bus, SoC, ASoC, MFD, syscon, or firmware drivers bind from compatible strings and acquire the resources described here.

## State and Persistence Behavior
The YAML itself stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: compatible strings, property names, phandle names, register tuple ordering, child-node names, and examples become contracts in source DTS files and compiled DTBs. Runtime state is created by the matched kernel drivers after probe, including regmap cache, DAPM power state, bias levels, PLL/clock configuration, jack/interrupt state, and audio stream parameters owned by ASoC drivers.

## Dependencies and Integration Points
Maintainers listed: Stephan Gerhold <stephan@gerhold.net>. Schema dependencies include `/schemas/types.yaml#/definitions/uint32`, `dai-common.yaml#`. Integration points include ASoC codec/component drivers, I2C/SPI/platform bus probing, DAPM graph construction, regulators, clocks, GPIO controls, and machine-driver links. The file also integrates with Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and source DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to compatible strings, bus address, reset/shutdown GPIOs, supplies, clocks, interrupts, DAI cells, widgets/routes, and chip-specific tuning properties, drift between documented compatible strings and driver match tables, incorrect resource ordering, phandle names, or cell counts that block probe or misconfigure hardware, variant-specific conditional branches accepting one SoC/chip while rejecting another. This schema rejects unknown top-level properties with `additionalProperties: false`. Regressions usually show up as schema-check failures, boot-time probe failures, missing audio/SoC child devices, bad firmware/resource allocation, broken suspend/resume, or silent routing/clocking errors in board audio paths.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/sound/awinic,aw8738.yaml` for the targeted schema and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/sound/awinic,aw8738.yaml` against boards that instantiate it. The schema has 1 embedded example; keep those examples valid under targeted binding checks. Cross-check compatible strings against driver `of_match_table` entries and inspect DTS users for register tuple counts, interrupt names, clocks/resets, supplies, DMA channels, graph endpoints, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/awinic,aw8738.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/awinic,aw87390.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/awinic,aw87390.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/awinic,aw87390.yaml` defines the audio codec or amplifier binding titled `Awinic Aw87390 Audio Amplifier`. The awinic aw87390 is specifically designed to improve the musical output dynamic range, enhance the overall sound quallity, which is a new high efficiency, low noise, constant large volume, 6th Smart K audio amplifier. It constrains source DTS and compiled DTB hardware descriptions before Linux drivers consume the node.

## Important APIs, Types, and Functions
The API surface is the devicetree ABI rather than callable code. `compatible` uses `oneOf` with 2 branches with 3 tokens: `awinic,aw87390`, `anbernic,rgds-amp`, `awinic,aw87391`. Top-level properties are `compatible`, `reg`, `#sound-dai-cells`, `awinic,audio-channel`. Required top-level properties are `compatible`, `reg`, `#sound-dai-cells`. Nested or reusable constraints include composition/conditionals: `allOf`; referenced schemas: `/schemas/types.yaml#/definitions/uint32`, `dai-common.yaml#`; notable enum/const values: `0`. The highest-risk contract area is compatible strings, bus address, reset/shutdown GPIOs, supplies, clocks, interrupts, DAI cells, widgets/routes, and chip-specific tuning properties.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this file plus `$ref` targets, and enforces required properties, array cardinality, constants, enums, and `allOf`. `dtbs_check` then matches compiled DTS nodes by `compatible`, `$nodename`, or parent-schema inclusion, descends into pattern-matched children, and applies `additionalProperties` or `unevaluatedProperties` closure. Runtime flow begins only after the DTB is loaded: Linux bus, SoC, ASoC, MFD, syscon, or firmware drivers bind from compatible strings and acquire the resources described here.

## State and Persistence Behavior
The YAML itself stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: compatible strings, property names, phandle names, register tuple ordering, child-node names, and examples become contracts in source DTS files and compiled DTBs. Runtime state is created by the matched kernel drivers after probe, including regmap cache, DAPM power state, bias levels, PLL/clock configuration, jack/interrupt state, and audio stream parameters owned by ASoC drivers.

## Dependencies and Integration Points
Maintainers listed: Weidong Wang <wangweidong.a@awinic.com>. Schema dependencies include `/schemas/types.yaml#/definitions/uint32`, `dai-common.yaml#`. Integration points include ASoC codec/component drivers, I2C/SPI/platform bus probing, DAPM graph construction, regulators, clocks, GPIO controls, and machine-driver links. The file also integrates with Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and source DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to compatible strings, bus address, reset/shutdown GPIOs, supplies, clocks, interrupts, DAI cells, widgets/routes, and chip-specific tuning properties, drift between documented compatible strings and driver match tables, incorrect resource ordering, phandle names, or cell counts that block probe or misconfigure hardware, variant-specific conditional branches accepting one SoC/chip while rejecting another. This schema closes composed schemas with `unevaluatedProperties: false`. Regressions usually show up as schema-check failures, boot-time probe failures, missing audio/SoC child devices, bad firmware/resource allocation, broken suspend/resume, or silent routing/clocking errors in board audio paths.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/sound/awinic,aw87390.yaml` for the targeted schema and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/sound/awinic,aw87390.yaml` against boards that instantiate it. The schema has 1 embedded example; keep those examples valid under targeted binding checks. Cross-check compatible strings against driver `of_match_table` entries and inspect DTS users for register tuple counts, interrupt names, clocks/resets, supplies, DMA channels, graph endpoints, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/awinic,aw87390.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/awinic,aw88395.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/awinic,aw88395.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/awinic,aw88395.yaml` defines the audio codec or amplifier binding titled `Awinic AW88395 Smart Audio Amplifier`. The Awinic AW88395 is an I2S/TDM input, high efficiency digital Smart K audio amplifier with an integrated 10.25V smart boost convert. It constrains source DTS and compiled DTB hardware descriptions before Linux drivers consume the node.

## Important APIs, Types, and Functions
The API surface is the devicetree ABI rather than callable code. `compatible` uses an `enum` of supported tokens with 6 tokens: `awinic,aw88081`, `awinic,aw88083`, `awinic,aw88166`, `awinic,aw88261`, `awinic,aw88395`, `awinic,aw88399`. Top-level properties are `compatible`, `reg`, `#sound-dai-cells`, `reset-gpios`, `dvdd-supply`, `firmware-name`, `awinic,audio-channel`, `awinic,sync-flag`. Required top-level properties are `compatible`, `reg`, `#sound-dai-cells`, `awinic,audio-channel`. Nested or reusable constraints include composition/conditionals: `allOf`; referenced schemas: `/schemas/types.yaml#/definitions/flag`, `/schemas/types.yaml#/definitions/uint32`, `dai-common.yaml#`; notable enum/const values: `0`. The highest-risk contract area is compatible strings, bus address, reset/shutdown GPIOs, supplies, clocks, interrupts, DAI cells, widgets/routes, and chip-specific tuning properties.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this file plus `$ref` targets, and enforces required properties, array cardinality, constants, enums, and `allOf`. `dtbs_check` then matches compiled DTS nodes by `compatible`, `$nodename`, or parent-schema inclusion, descends into pattern-matched children, and applies `additionalProperties` or `unevaluatedProperties` closure. Runtime flow begins only after the DTB is loaded: Linux bus, SoC, ASoC, MFD, syscon, or firmware drivers bind from compatible strings and acquire the resources described here.

## State and Persistence Behavior
The YAML itself stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: compatible strings, property names, phandle names, register tuple ordering, child-node names, and examples become contracts in source DTS files and compiled DTBs. Runtime state is created by the matched kernel drivers after probe, including regmap cache, DAPM power state, bias levels, PLL/clock configuration, jack/interrupt state, and audio stream parameters owned by ASoC drivers.

## Dependencies and Integration Points
Maintainers listed: Weidong Wang <wangweidong.a@awinic.com>. Schema dependencies include `/schemas/types.yaml#/definitions/flag`, `/schemas/types.yaml#/definitions/uint32`, `dai-common.yaml#`. Integration points include ASoC codec/component drivers, I2C/SPI/platform bus probing, DAPM graph construction, regulators, clocks, GPIO controls, and machine-driver links. The file also integrates with Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and source DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to compatible strings, bus address, reset/shutdown GPIOs, supplies, clocks, interrupts, DAI cells, widgets/routes, and chip-specific tuning properties, drift between documented compatible strings and driver match tables, incorrect resource ordering, phandle names, or cell counts that block probe or misconfigure hardware, variant-specific conditional branches accepting one SoC/chip while rejecting another. This schema closes composed schemas with `unevaluatedProperties: false`. Regressions usually show up as schema-check failures, boot-time probe failures, missing audio/SoC child devices, bad firmware/resource allocation, broken suspend/resume, or silent routing/clocking errors in board audio paths.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/sound/awinic,aw88395.yaml` for the targeted schema and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/sound/awinic,aw88395.yaml` against boards that instantiate it. The schema has 1 embedded example; keep those examples valid under targeted binding checks. Cross-check compatible strings against driver `of_match_table` entries and inspect DTS users for register tuple counts, interrupt names, clocks/resets, supplies, DMA channels, graph endpoints, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/awinic,aw88395.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/brcm,bcm2835-i2s.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/brcm,bcm2835-i2s.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/brcm,bcm2835-i2s.yaml` defines the audio controller or sound-card binding titled `Broadcom BCM2835 SoC I2S/PCM module`. It constrains source DTS and compiled DTB hardware descriptions through compatible strings, required resources, child-node topology, and shared schema references before Linux drivers consume the node.

## Important APIs, Types, and Functions
The API surface is the devicetree ABI rather than callable code. `compatible` uses a single `const` token with 1 token: `brcm,bcm2835-i2s`. Top-level properties are `compatible`, `reg`, `clocks`, `dmas`, `dma-names`. Required top-level properties are `compatible`, `reg`, `clocks`, `dmas`, `dma-names`. Nested or reusable constraints include notable enum/const values: `tx`, `rx`. The highest-risk contract area is register and interrupt resources, clocks/resets, DMA channels, sound-dai cells, graph ports/endpoints, routing, and SoC-specific compatible strings.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this file plus `$ref` targets, and enforces required properties, array cardinality, constants, enums, and no top-level conditionals. `dtbs_check` then matches compiled DTS nodes by `compatible`, `$nodename`, or parent-schema inclusion, descends into pattern-matched children, and applies `additionalProperties` or `unevaluatedProperties` closure. Runtime flow begins only after the DTB is loaded: Linux bus, SoC, ASoC, MFD, syscon, or firmware drivers bind from compatible strings and acquire the resources described here.

## State and Persistence Behavior
The YAML itself stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: compatible strings, property names, phandle names, register tuple ordering, child-node names, and examples become contracts in source DTS files and compiled DTBs. Runtime state is created by the matched kernel drivers after probe, including DAI/controller probe state, DMA stream state, clocking, reset state, and sound-card topology owned by ASoC runtime drivers.

## Dependencies and Integration Points
Maintainers listed: Florian Fainelli <florian.fainelli@broadcom.com>. Schema dependencies include dt-schema core/meta schemas only. Integration points include ASoC CPU DAI drivers, platform DMA engines, machine drivers, graph/simple-card parsing, clocks/resets, pinctrl, and board DTS sound links. The file also integrates with Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and source DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to register and interrupt resources, clocks/resets, DMA channels, sound-dai cells, graph ports/endpoints, routing, and SoC-specific compatible strings, drift between documented compatible strings and driver match tables, incorrect resource ordering, phandle names, or cell counts that block probe or misconfigure hardware. This schema rejects unknown top-level properties with `additionalProperties: false`. Regressions usually show up as schema-check failures, boot-time probe failures, missing audio/SoC child devices, bad firmware/resource allocation, broken suspend/resume, or silent routing/clocking errors in board audio paths.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/sound/brcm,bcm2835-i2s.yaml` for the targeted schema and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/sound/brcm,bcm2835-i2s.yaml` against boards that instantiate it. The schema has 1 embedded example; keep those examples valid under targeted binding checks. Cross-check compatible strings against driver `of_match_table` entries and inspect DTS users for register tuple counts, interrupt names, clocks/resets, supplies, DMA channels, graph endpoints, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/brcm,bcm2835-i2s.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/cirrus,cs35l41.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/cirrus,cs35l41.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/cirrus,cs35l41.yaml` defines the audio codec or amplifier binding titled `Cirrus Logic CS35L41 Speaker Amplifier`. CS35L41 is a boosted mono Class D amplifier with DSP speaker protection and equalization It constrains source DTS and compiled DTB hardware descriptions before Linux drivers consume the node.

## Important APIs, Types, and Functions
The API surface is the devicetree ABI rather than callable code. `compatible` uses an `enum` of supported tokens with 2 tokens: `cirrus,cs35l40`, `cirrus,cs35l41`. Top-level properties are `compatible`, `reg`, `interrupts`, `#sound-dai-cells`, `reset-gpios`, `VA-supply`, `VP-supply`, `cirrus,boost-peak-milliamp`, `cirrus,boost-ind-nanohenry`, `cirrus,boost-cap-microfarad`, `cirrus,asp-sdout-hiz`, `cirrus,boost-type`, `cirrus,gpio1-polarity-invert`, `cirrus,gpio1-output-enable`, `cirrus,gpio1-src-select`, `cirrus,gpio2-polarity-invert`, `cirrus,gpio2-output-enable`, `cirrus,gpio2-src-select`, `cirrus,subsystem-id`. Required top-level properties are `compatible`, `reg`, `#sound-dai-cells`. Nested or reusable constraints include composition/conditionals: `allOf`; referenced schemas: `/schemas/types.yaml#/definitions/string`, `/schemas/types.yaml#/definitions/uint32`, `dai-common.yaml#`; notable enum/const values: `1`, `0`. The highest-risk contract area is compatible strings, bus address, reset/shutdown GPIOs, supplies, clocks, interrupts, DAI cells, widgets/routes, and chip-specific tuning properties.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this file plus `$ref` targets, and enforces required properties, array cardinality, constants, enums, and `allOf`. `dtbs_check` then matches compiled DTS nodes by `compatible`, `$nodename`, or parent-schema inclusion, descends into pattern-matched children, and applies `additionalProperties` or `unevaluatedProperties` closure. Runtime flow begins only after the DTB is loaded: Linux bus, SoC, ASoC, MFD, syscon, or firmware drivers bind from compatible strings and acquire the resources described here.

## State and Persistence Behavior
The YAML itself stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: compatible strings, property names, phandle names, register tuple ordering, child-node names, and examples become contracts in source DTS files and compiled DTBs. Runtime state is created by the matched kernel drivers after probe, including regmap cache, DAPM power state, bias levels, PLL/clock configuration, jack/interrupt state, and audio stream parameters owned by ASoC drivers.

## Dependencies and Integration Points
Maintainers listed: david.rhodes@cirrus.com. Schema dependencies include `/schemas/types.yaml#/definitions/string`, `/schemas/types.yaml#/definitions/uint32`, `dai-common.yaml#`. Integration points include ASoC codec/component drivers, I2C/SPI/platform bus probing, DAPM graph construction, regulators, clocks, GPIO controls, and machine-driver links. The file also integrates with Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and source DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to compatible strings, bus address, reset/shutdown GPIOs, supplies, clocks, interrupts, DAI cells, widgets/routes, and chip-specific tuning properties, drift between documented compatible strings and driver match tables, incorrect resource ordering, phandle names, or cell counts that block probe or misconfigure hardware, variant-specific conditional branches accepting one SoC/chip while rejecting another. This schema closes composed schemas with `unevaluatedProperties: false`. Regressions usually show up as schema-check failures, boot-time probe failures, missing audio/SoC child devices, bad firmware/resource allocation, broken suspend/resume, or silent routing/clocking errors in board audio paths.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/sound/cirrus,cs35l41.yaml` for the targeted schema and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/sound/cirrus,cs35l41.yaml` against boards that instantiate it. The schema has 1 embedded example; keep those examples valid under targeted binding checks. Cross-check compatible strings against driver `of_match_table` entries and inspect DTS users for register tuple counts, interrupt names, clocks/resets, supplies, DMA channels, graph endpoints, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/cirrus,cs35l41.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/cirrus,cs35l45.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/cirrus,cs35l45.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/cirrus,cs35l45.yaml` defines the audio codec or amplifier binding titled `Cirrus Logic CS35L45 Speaker Amplifier`. CS35L45 is a Boosted Mono Class D Amplifier with DSP Speaker Protection and Adaptive Battery Management. It constrains source DTS and compiled DTB hardware descriptions before Linux drivers consume the node.

## Important APIs, Types, and Functions
The API surface is the devicetree ABI rather than callable code. `compatible` uses an `enum` of supported tokens with 1 token: `cirrus,cs35l45`. Top-level properties are `compatible`, `reg`, `interrupts`, `#sound-dai-cells`, `reset-gpios`, `vdd-a-supply`, `vdd-batt-supply`, `spi-max-frequency`, `cirrus,asp-sdout-hiz-ctrl`. Required top-level properties are `compatible`, `reg`, `#sound-dai-cells`. Nested or reusable constraints include composition/conditionals: `allOf`; child-node patterns: `^cirrus,gpio-ctrl[1-3]$`; referenced schemas: `/schemas/types.yaml#/definitions/uint32`, `dai-common.yaml#`; child-node API keys: `gpio-dir`, `gpio-lvl`, `gpio-op-cfg`, `gpio-pol`, `gpio-ctrl`; notable enum/const values: `1`. The highest-risk contract area is compatible strings, bus address, reset/shutdown GPIOs, supplies, clocks, interrupts, DAI cells, widgets/routes, and chip-specific tuning properties.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this file plus `$ref` targets, and enforces required properties, array cardinality, constants, enums, and `allOf`. `dtbs_check` then matches compiled DTS nodes by `compatible`, `$nodename`, or parent-schema inclusion, descends into pattern-matched children, and applies `additionalProperties` or `unevaluatedProperties` closure. Runtime flow begins only after the DTB is loaded: Linux bus, SoC, ASoC, MFD, syscon, or firmware drivers bind from compatible strings and acquire the resources described here.

## State and Persistence Behavior
The YAML itself stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: compatible strings, property names, phandle names, register tuple ordering, child-node names, and examples become contracts in source DTS files and compiled DTBs. Runtime state is created by the matched kernel drivers after probe, including regmap cache, DAPM power state, bias levels, PLL/clock configuration, jack/interrupt state, and audio stream parameters owned by ASoC drivers.

## Dependencies and Integration Points
Maintainers listed: Ricardo Rivera-Matos <rriveram@opensource.cirrus.com>, Richard Fitzgerald <rf@opensource.cirrus.com>. Schema dependencies include `/schemas/types.yaml#/definitions/uint32`, `dai-common.yaml#`. Integration points include ASoC codec/component drivers, I2C/SPI/platform bus probing, DAPM graph construction, regulators, clocks, GPIO controls, and machine-driver links. The file also integrates with Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and source DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to compatible strings, bus address, reset/shutdown GPIOs, supplies, clocks, interrupts, DAI cells, widgets/routes, and chip-specific tuning properties, drift between documented compatible strings and driver match tables, incorrect resource ordering, phandle names, or cell counts that block probe or misconfigure hardware, variant-specific conditional branches accepting one SoC/chip while rejecting another, child-node regexes that over-match unrelated children or under-match valid hardware nodes. This schema closes composed schemas with `unevaluatedProperties: false`. Regressions usually show up as schema-check failures, boot-time probe failures, missing audio/SoC child devices, bad firmware/resource allocation, broken suspend/resume, or silent routing/clocking errors in board audio paths.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/sound/cirrus,cs35l45.yaml` for the targeted schema and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/sound/cirrus,cs35l45.yaml` against boards that instantiate it. The schema has 1 embedded example; keep those examples valid under targeted binding checks. Include child-node validation for `^cirrus,gpio-ctrl[1-3]$`. Cross-check compatible strings against driver `of_match_table` entries and inspect DTS users for register tuple counts, interrupt names, clocks/resets, supplies, DMA channels, graph endpoints, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/cirrus,cs35l45.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/cirrus,cs4234.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/cirrus,cs4234.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/cirrus,cs4234.yaml` defines the audio codec or amplifier binding titled `Cirrus Logic cs4234 audio CODEC`. The CS4234 is a highly versatile CODEC that combines 4 channels of high performance analog to digital conversion, 4 channels of high performance digital to analog conversion for audio, and 1 channel of digital to analog conversion to provide a nondelayed audio reference signal to an external Class H tracking power supply. It constrains source DTS and compiled DTB hardware descriptions before Linux drivers consume the node.

## Important APIs, Types, and Functions
The API surface is the devicetree ABI rather than callable code. `compatible` uses an `enum` of supported tokens with 1 token: `cirrus,cs4234`. Top-level properties are `compatible`, `reg`, `VA-supply`, `VL-supply`, `reset-gpios`. Required top-level properties are `compatible`, `reg`, `VA-supply`, `VL-supply`. Nested or reusable constraints include no unusually complex nested constraints beyond the top-level properties. The highest-risk contract area is compatible strings, bus address, reset/shutdown GPIOs, supplies, clocks, interrupts, DAI cells, widgets/routes, and chip-specific tuning properties.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this file plus `$ref` targets, and enforces required properties, array cardinality, constants, enums, and no top-level conditionals. `dtbs_check` then matches compiled DTS nodes by `compatible`, `$nodename`, or parent-schema inclusion, descends into pattern-matched children, and applies `additionalProperties` or `unevaluatedProperties` closure. Runtime flow begins only after the DTB is loaded: Linux bus, SoC, ASoC, MFD, syscon, or firmware drivers bind from compatible strings and acquire the resources described here.

## State and Persistence Behavior
The YAML itself stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: compatible strings, property names, phandle names, register tuple ordering, child-node names, and examples become contracts in source DTS files and compiled DTBs. Runtime state is created by the matched kernel drivers after probe, including regmap cache, DAPM power state, bias levels, PLL/clock configuration, jack/interrupt state, and audio stream parameters owned by ASoC drivers.

## Dependencies and Integration Points
Maintainers listed: patches@opensource.cirrus.com. Schema dependencies include dt-schema core/meta schemas only. Integration points include ASoC codec/component drivers, I2C/SPI/platform bus probing, DAPM graph construction, regulators, clocks, GPIO controls, and machine-driver links. The file also integrates with Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and source DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to compatible strings, bus address, reset/shutdown GPIOs, supplies, clocks, interrupts, DAI cells, widgets/routes, and chip-specific tuning properties, drift between documented compatible strings and driver match tables, incorrect resource ordering, phandle names, or cell counts that block probe or misconfigure hardware. This schema rejects unknown top-level properties with `additionalProperties: false`. Regressions usually show up as schema-check failures, boot-time probe failures, missing audio/SoC child devices, bad firmware/resource allocation, broken suspend/resume, or silent routing/clocking errors in board audio paths.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/sound/cirrus,cs4234.yaml` for the targeted schema and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/sound/cirrus,cs4234.yaml` against boards that instantiate it. The schema has 1 embedded example; keep those examples valid under targeted binding checks. Cross-check compatible strings against driver `of_match_table` entries and inspect DTS users for register tuple counts, interrupt names, clocks/resets, supplies, DMA channels, graph endpoints, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/cirrus,cs4234.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/cirrus,cs4270.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/cirrus,cs4270.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/cirrus,cs4270.yaml` defines the audio codec or amplifier binding titled `Cirrus Logic CS4270 audio CODEC`. The CS4270 is a stereo audio codec. It constrains source DTS and compiled DTB hardware descriptions before Linux drivers consume the node.

## Important APIs, Types, and Functions
The API surface is the devicetree ABI rather than callable code. `compatible` uses a single `const` token with 1 token: `cirrus,cs4270`. Top-level properties are `compatible`, `reg`, `#sound-dai-cells`, `reset-gpios`, `va-supply`, `vd-supply`, `vlc-supply`. Required top-level properties are `compatible`, `reg`. Nested or reusable constraints include composition/conditionals: `allOf`; referenced schemas: `dai-common.yaml#`; notable enum/const values: `0`. The highest-risk contract area is compatible strings, bus address, reset/shutdown GPIOs, supplies, clocks, interrupts, DAI cells, widgets/routes, and chip-specific tuning properties.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this file plus `$ref` targets, and enforces required properties, array cardinality, constants, enums, and `allOf`. `dtbs_check` then matches compiled DTS nodes by `compatible`, `$nodename`, or parent-schema inclusion, descends into pattern-matched children, and applies `additionalProperties` or `unevaluatedProperties` closure. Runtime flow begins only after the DTB is loaded: Linux bus, SoC, ASoC, MFD, syscon, or firmware drivers bind from compatible strings and acquire the resources described here.

## State and Persistence Behavior
The YAML itself stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: compatible strings, property names, phandle names, register tuple ordering, child-node names, and examples become contracts in source DTS files and compiled DTBs. Runtime state is created by the matched kernel drivers after probe, including regmap cache, DAPM power state, bias levels, PLL/clock configuration, jack/interrupt state, and audio stream parameters owned by ASoC drivers.

## Dependencies and Integration Points
Maintainers listed: patches@opensource.cirrus.com. Schema dependencies include `dai-common.yaml#`. Integration points include ASoC codec/component drivers, I2C/SPI/platform bus probing, DAPM graph construction, regulators, clocks, GPIO controls, and machine-driver links. The file also integrates with Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and source DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to compatible strings, bus address, reset/shutdown GPIOs, supplies, clocks, interrupts, DAI cells, widgets/routes, and chip-specific tuning properties, drift between documented compatible strings and driver match tables, incorrect resource ordering, phandle names, or cell counts that block probe or misconfigure hardware, variant-specific conditional branches accepting one SoC/chip while rejecting another. This schema closes composed schemas with `unevaluatedProperties: false`. Regressions usually show up as schema-check failures, boot-time probe failures, missing audio/SoC child devices, bad firmware/resource allocation, broken suspend/resume, or silent routing/clocking errors in board audio paths.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/sound/cirrus,cs4270.yaml` for the targeted schema and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/sound/cirrus,cs4270.yaml` against boards that instantiate it. The schema has 1 embedded example; keep those examples valid under targeted binding checks. Cross-check compatible strings against driver `of_match_table` entries and inspect DTS users for register tuple counts, interrupt names, clocks/resets, supplies, DMA channels, graph endpoints, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/cirrus,cs4270.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/cirrus,cs4271.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/cirrus,cs4271.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/cirrus,cs4271.yaml` defines the audio codec or amplifier binding titled `Cirrus Logic CS4271 audio CODEC`. The CS4271 is a stereo audio codec. It constrains source DTS and compiled DTB hardware descriptions before Linux drivers consume the node.

## Important APIs, Types, and Functions
The API surface is the devicetree ABI rather than callable code. `compatible` uses a single `const` token with 1 token: `cirrus,cs4271`. Top-level properties are `compatible`, `reg`, `clocks`, `clock-names`, `spi-cpha`, `spi-cpol`, `#sound-dai-cells`, `reset-gpios`, `va-supply`, `vd-supply`, `vl-supply`, `port`, `cirrus,amuteb-eq-bmutec`, `cirrus,enable-soft-reset`. Required top-level properties are `compatible`, `reg`. Nested or reusable constraints include composition/conditionals: `allOf`; referenced schemas: `/schemas/spi/spi-peripheral-props.yaml#`, `audio-graph-port.yaml#`, `dai-common.yaml#`; notable enum/const values: `mclk`, `0`. The highest-risk contract area is compatible strings, bus address, reset/shutdown GPIOs, supplies, clocks, interrupts, DAI cells, widgets/routes, and chip-specific tuning properties.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this file plus `$ref` targets, and enforces required properties, array cardinality, constants, enums, and `allOf`. `dtbs_check` then matches compiled DTS nodes by `compatible`, `$nodename`, or parent-schema inclusion, descends into pattern-matched children, and applies `additionalProperties` or `unevaluatedProperties` closure. Runtime flow begins only after the DTB is loaded: Linux bus, SoC, ASoC, MFD, syscon, or firmware drivers bind from compatible strings and acquire the resources described here.

## State and Persistence Behavior
The YAML itself stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: compatible strings, property names, phandle names, register tuple ordering, child-node names, and examples become contracts in source DTS files and compiled DTBs. Runtime state is created by the matched kernel drivers after probe, including regmap cache, DAPM power state, bias levels, PLL/clock configuration, jack/interrupt state, and audio stream parameters owned by ASoC drivers.

## Dependencies and Integration Points
Maintainers listed: Alexander Sverdlin <alexander.sverdlin@gmail.com>, Nikita Shubin <nikita.shubin@maquefel.me>. Schema dependencies include `/schemas/spi/spi-peripheral-props.yaml#`, `audio-graph-port.yaml#`, `dai-common.yaml#`. Integration points include ASoC codec/component drivers, I2C/SPI/platform bus probing, DAPM graph construction, regulators, clocks, GPIO controls, and machine-driver links. The file also integrates with Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and source DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to compatible strings, bus address, reset/shutdown GPIOs, supplies, clocks, interrupts, DAI cells, widgets/routes, and chip-specific tuning properties, drift between documented compatible strings and driver match tables, incorrect resource ordering, phandle names, or cell counts that block probe or misconfigure hardware, variant-specific conditional branches accepting one SoC/chip while rejecting another. This schema closes composed schemas with `unevaluatedProperties: false`. Regressions usually show up as schema-check failures, boot-time probe failures, missing audio/SoC child devices, bad firmware/resource allocation, broken suspend/resume, or silent routing/clocking errors in board audio paths.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/sound/cirrus,cs4271.yaml` for the targeted schema and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/sound/cirrus,cs4271.yaml` against boards that instantiate it. The schema has 1 embedded example; keep those examples valid under targeted binding checks. Cross-check compatible strings against driver `of_match_table` entries and inspect DTS users for register tuple counts, interrupt names, clocks/resets, supplies, DMA channels, graph endpoints, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/cirrus,cs4271.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/cirrus,cs42l42.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/cirrus,cs42l42.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/cirrus,cs42l42.yaml` defines the audio codec or amplifier binding titled `Cirrus Logic CS42L42 audio CODEC`. The CS42L42 is a low-power audio codec designed for portable applications. It constrains source DTS and compiled DTB hardware descriptions before Linux drivers consume the node.

## Important APIs, Types, and Functions
The API surface is the devicetree ABI rather than callable code. `compatible` uses an `enum` of supported tokens with 2 tokens: `cirrus,cs42l42`, `cirrus,cs42l83`. Top-level properties are `compatible`, `reg`, `VP-supply`, `VCP-supply`, `VD_FILT-supply`, `VL-supply`, `VA-supply`, `reset-gpios`, `interrupts`, `cirrus,ts-inv`, `cirrus,ts-dbnc-rise`, `cirrus,ts-dbnc-fall`, `cirrus,btn-det-init-dbnce`, `cirrus,btn-det-event-dbnce`, `cirrus,bias-lvls`, `cirrus,hs-bias-ramp-rate`, `cirrus,hs-bias-sense-disable`. Required top-level properties are `compatible`, `reg`, `VP-supply`, `VCP-supply`, `VD_FILT-supply`, `VL-supply`, `VA-supply`. Nested or reusable constraints include referenced schemas: `/schemas/types.yaml#/definitions/uint32`, `/schemas/types.yaml#/definitions/uint32-array`. The highest-risk contract area is compatible strings, bus address, reset/shutdown GPIOs, supplies, clocks, interrupts, DAI cells, widgets/routes, and chip-specific tuning properties.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this file plus `$ref` targets, and enforces required properties, array cardinality, constants, enums, and no top-level conditionals. `dtbs_check` then matches compiled DTS nodes by `compatible`, `$nodename`, or parent-schema inclusion, descends into pattern-matched children, and applies `additionalProperties` or `unevaluatedProperties` closure. Runtime flow begins only after the DTB is loaded: Linux bus, SoC, ASoC, MFD, syscon, or firmware drivers bind from compatible strings and acquire the resources described here.

## State and Persistence Behavior
The YAML itself stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: compatible strings, property names, phandle names, register tuple ordering, child-node names, and examples become contracts in source DTS files and compiled DTBs. Runtime state is created by the matched kernel drivers after probe, including regmap cache, DAPM power state, bias levels, PLL/clock configuration, jack/interrupt state, and audio stream parameters owned by ASoC drivers.

## Dependencies and Integration Points
Maintainers listed: patches@opensource.cirrus.com. Schema dependencies include `/schemas/types.yaml#/definitions/uint32`, `/schemas/types.yaml#/definitions/uint32-array`. Integration points include ASoC codec/component drivers, I2C/SPI/platform bus probing, DAPM graph construction, regulators, clocks, GPIO controls, and machine-driver links. The file also integrates with Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and source DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to compatible strings, bus address, reset/shutdown GPIOs, supplies, clocks, interrupts, DAI cells, widgets/routes, and chip-specific tuning properties, drift between documented compatible strings and driver match tables, incorrect resource ordering, phandle names, or cell counts that block probe or misconfigure hardware. This schema rejects unknown top-level properties with `additionalProperties: false`. Regressions usually show up as schema-check failures, boot-time probe failures, missing audio/SoC child devices, bad firmware/resource allocation, broken suspend/resume, or silent routing/clocking errors in board audio paths.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/sound/cirrus,cs42l42.yaml` for the targeted schema and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/sound/cirrus,cs42l42.yaml` against boards that instantiate it. The schema has 1 embedded example; keep those examples valid under targeted binding checks. Cross-check compatible strings against driver `of_match_table` entries and inspect DTS users for register tuple counts, interrupt names, clocks/resets, supplies, DMA channels, graph endpoints, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/cirrus,cs42l42.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/cirrus,cs42l43.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/cirrus,cs42l43.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/cirrus,cs42l43.yaml` defines the audio codec or amplifier binding titled `Cirrus Logic CS42L43 Audio CODEC`. The CS42L43 is an audio CODEC with integrated MIPI SoundWire interface (Version 1.2.1 compliant), I2C, SPI, and I2S/TDM interfaces designed for portable applications. It constrains source DTS and compiled DTB hardware descriptions before Linux drivers consume the node.

## Important APIs, Types, and Functions
The API surface is the devicetree ABI rather than callable code. `compatible` uses an `enum` of supported tokens with 2 tokens: `cirrus,cs42l43`, `cirrus,cs42l43b`. Top-level properties are `compatible`, `reg`, `vdd-p-supply`, `vdd-a-supply`, `vdd-d-supply`, `vdd-io-supply`, `vdd-cp-supply`, `vdd-amp-supply`, `reset-gpios`, `interrupt-controller`, `#interrupt-cells`, `interrupts`, `#sound-dai-cells`, `clocks`, `clock-names`, `cirrus,bias-low`, `cirrus,bias-sense-microamp`, `cirrus,bias-ramp-ms`, `cirrus,detect-us`, `cirrus,button-automute`, `cirrus,buttons-ohms`, `cirrus,tip-debounce-ms`, `cirrus,tip-invert`, `cirrus,tip-disable-pullup`, `cirrus,tip-fall-db-ms`, `cirrus,tip-rise-db-ms`, `cirrus,use-ring-sense`, `cirrus,ring-invert`, and 5 more. Required top-level properties are `compatible`, `reg`, `vdd-p-supply`, `vdd-a-supply`, `vdd-io-supply`, `vdd-cp-supply`. Nested or reusable constraints include composition/conditionals: `allOf`; referenced schemas: `#/$defs/cirrus-cs42l43-state`, `/schemas/pinctrl/pincfg-node.yaml#`, `/schemas/pinctrl/pinctrl.yaml#`, `/schemas/pinctrl/pinmux-node.yaml#`, `/schemas/spi/spi-controller.yaml#`, `dai-common.yaml#`; notable enum/const values: `0`, `14`, `24`, `43`, `52`, `61`, `71`, `90`, `99`, `10`, `40`, `170`, `20`, `100`, `1000`, `10000`, and 45 more. The highest-risk contract area is compatible strings, bus address, reset/shutdown GPIOs, supplies, clocks, interrupts, DAI cells, widgets/routes, and chip-specific tuning properties.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this file plus `$ref` targets, and enforces required properties, array cardinality, constants, enums, and `allOf`. `dtbs_check` then matches compiled DTS nodes by `compatible`, `$nodename`, or parent-schema inclusion, descends into pattern-matched children, and applies `additionalProperties` or `unevaluatedProperties` closure. Runtime flow begins only after the DTB is loaded: Linux bus, SoC, ASoC, MFD, syscon, or firmware drivers bind from compatible strings and acquire the resources described here.

## State and Persistence Behavior
The YAML itself stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: compatible strings, property names, phandle names, register tuple ordering, child-node names, and examples become contracts in source DTS files and compiled DTBs. Runtime state is created by the matched kernel drivers after probe, including regmap cache, DAPM power state, bias levels, PLL/clock configuration, jack/interrupt state, and audio stream parameters owned by ASoC drivers.

## Dependencies and Integration Points
Maintainers listed: patches@opensource.cirrus.com. Schema dependencies include `#/$defs/cirrus-cs42l43-state`, `/schemas/pinctrl/pincfg-node.yaml#`, `/schemas/pinctrl/pinctrl.yaml#`, `/schemas/pinctrl/pinmux-node.yaml#`, `/schemas/spi/spi-controller.yaml#`, `dai-common.yaml#`. Integration points include ASoC codec/component drivers, I2C/SPI/platform bus probing, DAPM graph construction, regulators, clocks, GPIO controls, and machine-driver links. The file also integrates with Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and source DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to compatible strings, bus address, reset/shutdown GPIOs, supplies, clocks, interrupts, DAI cells, widgets/routes, and chip-specific tuning properties, drift between documented compatible strings and driver match tables, incorrect resource ordering, phandle names, or cell counts that block probe or misconfigure hardware, variant-specific conditional branches accepting one SoC/chip while rejecting another. This schema rejects unknown top-level properties with `additionalProperties: false`. Regressions usually show up as schema-check failures, boot-time probe failures, missing audio/SoC child devices, bad firmware/resource allocation, broken suspend/resume, or silent routing/clocking errors in board audio paths.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/sound/cirrus,cs42l43.yaml` for the targeted schema and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/sound/cirrus,cs42l43.yaml` against boards that instantiate it. The schema has 1 embedded example; keep those examples valid under targeted binding checks. Cross-check compatible strings against driver `of_match_table` entries and inspect DTS users for register tuple counts, interrupt names, clocks/resets, supplies, DMA channels, graph endpoints, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/cirrus,cs42l43.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/cirrus,cs42l51.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/cirrus,cs42l51.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/cirrus,cs42l51.yaml` defines the audio codec or amplifier binding titled `CS42L51 audio codec`. It constrains source DTS and compiled DTB hardware descriptions through compatible strings, required resources, child-node topology, and shared schema references before Linux drivers consume the node.

## Important APIs, Types, and Functions
The API surface is the devicetree ABI rather than callable code. `compatible` uses a single `const` token with 1 token: `cirrus,cs42l51`. Top-level properties are `compatible`, `reg`, `#sound-dai-cells`, `clocks`, `clock-names`, `reset-gpios`, `VL-supply`, `VD-supply`, `VA-supply`, `VAHP-supply`, `port`. Required top-level properties are `compatible`, `reg`, `#sound-dai-cells`. Nested or reusable constraints include composition/conditionals: `allOf`; referenced schemas: `audio-graph-port.yaml#`, `dai-common.yaml#`; notable enum/const values: `0`, `MCLK`. The highest-risk contract area is compatible strings, bus address, reset/shutdown GPIOs, supplies, clocks, interrupts, DAI cells, widgets/routes, and chip-specific tuning properties.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this file plus `$ref` targets, and enforces required properties, array cardinality, constants, enums, and `allOf`. `dtbs_check` then matches compiled DTS nodes by `compatible`, `$nodename`, or parent-schema inclusion, descends into pattern-matched children, and applies `additionalProperties` or `unevaluatedProperties` closure. Runtime flow begins only after the DTB is loaded: Linux bus, SoC, ASoC, MFD, syscon, or firmware drivers bind from compatible strings and acquire the resources described here.

## State and Persistence Behavior
The YAML itself stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: compatible strings, property names, phandle names, register tuple ordering, child-node names, and examples become contracts in source DTS files and compiled DTBs. Runtime state is created by the matched kernel drivers after probe, including regmap cache, DAPM power state, bias levels, PLL/clock configuration, jack/interrupt state, and audio stream parameters owned by ASoC drivers.

## Dependencies and Integration Points
Maintainers listed: Olivier Moysan <olivier.moysan@foss.st.com>. Schema dependencies include `audio-graph-port.yaml#`, `dai-common.yaml#`. Integration points include ASoC codec/component drivers, I2C/SPI/platform bus probing, DAPM graph construction, regulators, clocks, GPIO controls, and machine-driver links. The file also integrates with Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and source DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to compatible strings, bus address, reset/shutdown GPIOs, supplies, clocks, interrupts, DAI cells, widgets/routes, and chip-specific tuning properties, drift between documented compatible strings and driver match tables, incorrect resource ordering, phandle names, or cell counts that block probe or misconfigure hardware, variant-specific conditional branches accepting one SoC/chip while rejecting another. This schema closes composed schemas with `unevaluatedProperties: false`. Regressions usually show up as schema-check failures, boot-time probe failures, missing audio/SoC child devices, bad firmware/resource allocation, broken suspend/resume, or silent routing/clocking errors in board audio paths.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/sound/cirrus,cs42l51.yaml` for the targeted schema and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/sound/cirrus,cs42l51.yaml` against boards that instantiate it. The schema has 1 embedded example; keep those examples valid under targeted binding checks. Cross-check compatible strings against driver `of_match_table` entries and inspect DTS users for register tuple counts, interrupt names, clocks/resets, supplies, DMA channels, graph endpoints, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/cirrus,cs42l51.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/cirrus,cs42l84.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/cirrus,cs42l84.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/cirrus,cs42l84.yaml` defines the audio codec or amplifier binding titled `Cirrus Logic CS42L84 audio CODEC`. The CS42L84 is a headphone jack codec made by Cirrus Logic and embedded in personal computers sold by Apple. It constrains source DTS and compiled DTB hardware descriptions before Linux drivers consume the node.

## Important APIs, Types, and Functions
The API surface is the devicetree ABI rather than callable code. `compatible` uses an `enum` of supported tokens with 1 token: `cirrus,cs42l84`. Top-level properties are `compatible`, `reg`, `reset-gpios`, `interrupts`, `#sound-dai-cells`. Required top-level properties are `compatible`, `reg`. Nested or reusable constraints include notable enum/const values: `0`. The highest-risk contract area is compatible strings, bus address, reset/shutdown GPIOs, supplies, clocks, interrupts, DAI cells, widgets/routes, and chip-specific tuning properties.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this file plus `$ref` targets, and enforces required properties, array cardinality, constants, enums, and no top-level conditionals. `dtbs_check` then matches compiled DTS nodes by `compatible`, `$nodename`, or parent-schema inclusion, descends into pattern-matched children, and applies `additionalProperties` or `unevaluatedProperties` closure. Runtime flow begins only after the DTB is loaded: Linux bus, SoC, ASoC, MFD, syscon, or firmware drivers bind from compatible strings and acquire the resources described here.

## State and Persistence Behavior
The YAML itself stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: compatible strings, property names, phandle names, register tuple ordering, child-node names, and examples become contracts in source DTS files and compiled DTBs. Runtime state is created by the matched kernel drivers after probe, including regmap cache, DAPM power state, bias levels, PLL/clock configuration, jack/interrupt state, and audio stream parameters owned by ASoC drivers.

## Dependencies and Integration Points
Maintainers listed: Martin Povišer <povik+lin@cutebit.org>. Schema dependencies include dt-schema core/meta schemas only. Integration points include ASoC codec/component drivers, I2C/SPI/platform bus probing, DAPM graph construction, regulators, clocks, GPIO controls, and machine-driver links. The file also integrates with Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and source DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to compatible strings, bus address, reset/shutdown GPIOs, supplies, clocks, interrupts, DAI cells, widgets/routes, and chip-specific tuning properties, drift between documented compatible strings and driver match tables, incorrect resource ordering, phandle names, or cell counts that block probe or misconfigure hardware. This schema rejects unknown top-level properties with `additionalProperties: false`. Regressions usually show up as schema-check failures, boot-time probe failures, missing audio/SoC child devices, bad firmware/resource allocation, broken suspend/resume, or silent routing/clocking errors in board audio paths.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/sound/cirrus,cs42l84.yaml` for the targeted schema and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/sound/cirrus,cs42l84.yaml` against boards that instantiate it. The schema has 1 embedded example; keep those examples valid under targeted binding checks. Cross-check compatible strings against driver `of_match_table` entries and inspect DTS users for register tuple counts, interrupt names, clocks/resets, supplies, DMA channels, graph endpoints, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/cirrus,cs42l84.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/cirrus,cs42xx8.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/cirrus,cs42xx8.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/cirrus,cs42xx8.yaml` defines the audio codec or amplifier binding titled `Cirrus Logic CS42448/CS42888 audio CODEC`. It constrains source DTS and compiled DTB hardware descriptions through compatible strings, required resources, child-node topology, and shared schema references before Linux drivers consume the node.

## Important APIs, Types, and Functions
The API surface is the devicetree ABI rather than callable code. `compatible` uses an `enum` of supported tokens with 2 tokens: `cirrus,cs42448`, `cirrus,cs42888`. Top-level properties are `compatible`, `reg`, `clocks`, `clock-names`, `VA-supply`, `VD-supply`, `VLC-supply`, `VLS-supply`, `reset-gpios`, `port`. Required top-level properties are `compatible`, `reg`, `clocks`, `clock-names`. Nested or reusable constraints include composition/conditionals: `allOf`, `if`, `then`; referenced schemas: `audio-graph-port.yaml#`, `dai-common.yaml#`; notable enum/const values: `mclk`. The highest-risk contract area is compatible strings, bus address, reset/shutdown GPIOs, supplies, clocks, interrupts, DAI cells, widgets/routes, and chip-specific tuning properties.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this file plus `$ref` targets, and enforces required properties, array cardinality, constants, enums, and `allOf`, `if`, `then`. `dtbs_check` then matches compiled DTS nodes by `compatible`, `$nodename`, or parent-schema inclusion, descends into pattern-matched children, and applies `additionalProperties` or `unevaluatedProperties` closure. Runtime flow begins only after the DTB is loaded: Linux bus, SoC, ASoC, MFD, syscon, or firmware drivers bind from compatible strings and acquire the resources described here.

## State and Persistence Behavior
The YAML itself stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: compatible strings, property names, phandle names, register tuple ordering, child-node names, and examples become contracts in source DTS files and compiled DTBs. Runtime state is created by the matched kernel drivers after probe, including regmap cache, DAPM power state, bias levels, PLL/clock configuration, jack/interrupt state, and audio stream parameters owned by ASoC drivers.

## Dependencies and Integration Points
Maintainers listed: patches@opensource.cirrus.com. Schema dependencies include `audio-graph-port.yaml#`, `dai-common.yaml#`. Integration points include ASoC codec/component drivers, I2C/SPI/platform bus probing, DAPM graph construction, regulators, clocks, GPIO controls, and machine-driver links. The file also integrates with Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and source DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to compatible strings, bus address, reset/shutdown GPIOs, supplies, clocks, interrupts, DAI cells, widgets/routes, and chip-specific tuning properties, drift between documented compatible strings and driver match tables, incorrect resource ordering, phandle names, or cell counts that block probe or misconfigure hardware, variant-specific conditional branches accepting one SoC/chip while rejecting another. This schema closes composed schemas with `unevaluatedProperties: false`. Regressions usually show up as schema-check failures, boot-time probe failures, missing audio/SoC child devices, bad firmware/resource allocation, broken suspend/resume, or silent routing/clocking errors in board audio paths.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/sound/cirrus,cs42xx8.yaml` for the targeted schema and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/sound/cirrus,cs42xx8.yaml` against boards that instantiate it. The schema has 1 embedded example; keep those examples valid under targeted binding checks. Cross-check compatible strings against driver `of_match_table` entries and inspect DTS users for register tuple counts, interrupt names, clocks/resets, supplies, DMA channels, graph endpoints, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/cirrus,cs42xx8.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/cirrus,cs48l32.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/cirrus,cs48l32.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/cirrus,cs48l32.yaml` defines the audio codec or amplifier binding titled `Cirrus Logic CS48L32 audio DSP.`. The CS48L32 is a high-performance low-power audio DSP for smartphones and other portable audio devices. It constrains source DTS and compiled DTB hardware descriptions before Linux drivers consume the node.

## Important APIs, Types, and Functions
The API surface is the devicetree ABI rather than callable code. `compatible` uses an `enum` of supported tokens with 1 token: `cirrus,cs48l32`. Top-level properties are `compatible`, `reg`, `spi-max-frequency`, `vdd-a-supply`, `vdd-d-supply`, `vdd-io-supply`, `vdd-cp-supply`, `reset-gpios`, `interrupts`, `clocks`, `clock-names`, `#sound-dai-cells`, `cirrus,in-type`, `cirrus,pdm-sup`. Required top-level properties are `compatible`, `reg`, `vdd-a-supply`, `vdd-d-supply`, `vdd-io-supply`, `vdd-cp-supply`. Nested or reusable constraints include composition/conditionals: `allOf`; referenced schemas: `/schemas/spi/spi-peripheral-props.yaml#`, `/schemas/types.yaml#/definitions/uint32-array`, `dai-common.yaml#`; notable enum/const values: `mclk1`, `1`. The highest-risk contract area is compatible strings, bus address, reset/shutdown GPIOs, supplies, clocks, interrupts, DAI cells, widgets/routes, and chip-specific tuning properties.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this file plus `$ref` targets, and enforces required properties, array cardinality, constants, enums, and `allOf`. `dtbs_check` then matches compiled DTS nodes by `compatible`, `$nodename`, or parent-schema inclusion, descends into pattern-matched children, and applies `additionalProperties` or `unevaluatedProperties` closure. Runtime flow begins only after the DTB is loaded: Linux bus, SoC, ASoC, MFD, syscon, or firmware drivers bind from compatible strings and acquire the resources described here.

## State and Persistence Behavior
The YAML itself stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: compatible strings, property names, phandle names, register tuple ordering, child-node names, and examples become contracts in source DTS files and compiled DTBs. Runtime state is created by the matched kernel drivers after probe, including regmap cache, DAPM power state, bias levels, PLL/clock configuration, jack/interrupt state, and audio stream parameters owned by ASoC drivers.

## Dependencies and Integration Points
Maintainers listed: patches@opensource.cirrus.com. Schema dependencies include `/schemas/spi/spi-peripheral-props.yaml#`, `/schemas/types.yaml#/definitions/uint32-array`, `dai-common.yaml#`. Integration points include ASoC codec/component drivers, I2C/SPI/platform bus probing, DAPM graph construction, regulators, clocks, GPIO controls, and machine-driver links. The file also integrates with Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and source DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to compatible strings, bus address, reset/shutdown GPIOs, supplies, clocks, interrupts, DAI cells, widgets/routes, and chip-specific tuning properties, drift between documented compatible strings and driver match tables, incorrect resource ordering, phandle names, or cell counts that block probe or misconfigure hardware, variant-specific conditional branches accepting one SoC/chip while rejecting another. This schema rejects unknown top-level properties with `additionalProperties: false`. Regressions usually show up as schema-check failures, boot-time probe failures, missing audio/SoC child devices, bad firmware/resource allocation, broken suspend/resume, or silent routing/clocking errors in board audio paths.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/sound/cirrus,cs48l32.yaml` for the targeted schema and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/sound/cirrus,cs48l32.yaml` against boards that instantiate it. The schema has 2 embedded examples; keep those examples valid under targeted binding checks. Cross-check compatible strings against driver `of_match_table` entries and inspect DTS users for register tuple counts, interrupt names, clocks/resets, supplies, DMA channels, graph endpoints, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/cirrus,cs48l32.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/cirrus,cs530x.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/cirrus,cs530x.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/cirrus,cs530x.yaml` defines the audio codec or amplifier binding titled `Cirrus Logic cs530x family of audio ADCs`. The CS530X devices are a family of high performance audio ADCs. It constrains source DTS and compiled DTB hardware descriptions before Linux drivers consume the node.

## Important APIs, Types, and Functions
The API surface is the devicetree ABI rather than callable code. `compatible` uses an `enum` of supported tokens with 7 tokens: `cirrus,cs4282`, `cirrus,cs4302`, `cirrus,cs4304`, `cirrus,cs4308`, `cirrus,cs5302`, `cirrus,cs5304`, `cirrus,cs5308`. Top-level properties are `compatible`, `reg`, `spi-max-frequency`, `#sound-dai-cells`, `reset-gpios`, `vdd-a-supply`, `vdd-io-supply`, `cirrus,in-hiz-pin12`, `cirrus,in-hiz-pin34`, `cirrus,in-hiz-pin56`, `cirrus,in-hiz-pin78`. Required top-level properties are `compatible`, `reg`, `#sound-dai-cells`. Nested or reusable constraints include composition/conditionals: `allOf`; referenced schemas: `/schemas/spi/spi-peripheral-props.yaml#`, `dai-common.yaml#`; notable enum/const values: `1`. The highest-risk contract area is compatible strings, bus address, reset/shutdown GPIOs, supplies, clocks, interrupts, DAI cells, widgets/routes, and chip-specific tuning properties.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this file plus `$ref` targets, and enforces required properties, array cardinality, constants, enums, and `allOf`. `dtbs_check` then matches compiled DTS nodes by `compatible`, `$nodename`, or parent-schema inclusion, descends into pattern-matched children, and applies `additionalProperties` or `unevaluatedProperties` closure. Runtime flow begins only after the DTB is loaded: Linux bus, SoC, ASoC, MFD, syscon, or firmware drivers bind from compatible strings and acquire the resources described here.

## State and Persistence Behavior
The YAML itself stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: compatible strings, property names, phandle names, register tuple ordering, child-node names, and examples become contracts in source DTS files and compiled DTBs. Runtime state is created by the matched kernel drivers after probe, including regmap cache, DAPM power state, bias levels, PLL/clock configuration, jack/interrupt state, and audio stream parameters owned by ASoC drivers.

## Dependencies and Integration Points
Maintainers listed: Paul Handrigan <paulha@opensource.cirrus.com>, patches@opensource.cirrus.com. Schema dependencies include `/schemas/spi/spi-peripheral-props.yaml#`, `dai-common.yaml#`. Integration points include ASoC codec/component drivers, I2C/SPI/platform bus probing, DAPM graph construction, regulators, clocks, GPIO controls, and machine-driver links. The file also integrates with Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and source DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to compatible strings, bus address, reset/shutdown GPIOs, supplies, clocks, interrupts, DAI cells, widgets/routes, and chip-specific tuning properties, drift between documented compatible strings and driver match tables, incorrect resource ordering, phandle names, or cell counts that block probe or misconfigure hardware, variant-specific conditional branches accepting one SoC/chip while rejecting another. This schema closes composed schemas with `unevaluatedProperties: false`. Regressions usually show up as schema-check failures, boot-time probe failures, missing audio/SoC child devices, bad firmware/resource allocation, broken suspend/resume, or silent routing/clocking errors in board audio paths.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/sound/cirrus,cs530x.yaml` for the targeted schema and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/sound/cirrus,cs530x.yaml` against boards that instantiate it. The schema has 1 embedded example; keep those examples valid under targeted binding checks. Cross-check compatible strings against driver `of_match_table` entries and inspect DTS users for register tuple counts, interrupt names, clocks/resets, supplies, DMA channels, graph endpoints, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/cirrus,cs530x.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/cirrus,ep9301-i2s.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/cirrus,ep9301-i2s.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/cirrus,ep9301-i2s.yaml` defines the audio codec or amplifier binding titled `Cirrus EP93xx I2S Controller`. The I2S controller is used to stream serial audio data between the external I2S CODECs’, ADCs/DACs, and the ARM Core. It constrains source DTS and compiled DTB hardware descriptions before Linux drivers consume the node.

## Important APIs, Types, and Functions
The API surface is the devicetree ABI rather than callable code. `compatible` uses a single `const` token with 1 token: `cirrus,ep9301-i2s`. Top-level properties are `compatible`, `#sound-dai-cells`, `reg`, `interrupts`, `clocks`, `clock-names`, `dmas`, `dma-names`, `port`. Required top-level properties are `compatible`, `#sound-dai-cells`, `reg`, `clocks`, `clock-names`. Nested or reusable constraints include composition/conditionals: `allOf`; referenced schemas: `audio-graph-port.yaml#`, `dai-common.yaml#`; notable enum/const values: `0`, `mclk`, `sclk`, `lrclk`, `tx`, `rx`. The highest-risk contract area is compatible strings, bus address, reset/shutdown GPIOs, supplies, clocks, interrupts, DAI cells, widgets/routes, and chip-specific tuning properties.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this file plus `$ref` targets, and enforces required properties, array cardinality, constants, enums, and `allOf`. `dtbs_check` then matches compiled DTS nodes by `compatible`, `$nodename`, or parent-schema inclusion, descends into pattern-matched children, and applies `additionalProperties` or `unevaluatedProperties` closure. Runtime flow begins only after the DTB is loaded: Linux bus, SoC, ASoC, MFD, syscon, or firmware drivers bind from compatible strings and acquire the resources described here.

## State and Persistence Behavior
The YAML itself stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: compatible strings, property names, phandle names, register tuple ordering, child-node names, and examples become contracts in source DTS files and compiled DTBs. Runtime state is created by the matched kernel drivers after probe, including regmap cache, DAPM power state, bias levels, PLL/clock configuration, jack/interrupt state, and audio stream parameters owned by ASoC drivers.

## Dependencies and Integration Points
Maintainers listed: Alexander Sverdlin <alexander.sverdlin@gmail.com>. Schema dependencies include `audio-graph-port.yaml#`, `dai-common.yaml#`. Integration points include ASoC codec/component drivers, I2C/SPI/platform bus probing, DAPM graph construction, regulators, clocks, GPIO controls, and machine-driver links. The file also integrates with Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and source DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to compatible strings, bus address, reset/shutdown GPIOs, supplies, clocks, interrupts, DAI cells, widgets/routes, and chip-specific tuning properties, drift between documented compatible strings and driver match tables, incorrect resource ordering, phandle names, or cell counts that block probe or misconfigure hardware, variant-specific conditional branches accepting one SoC/chip while rejecting another. This schema rejects unknown top-level properties with `additionalProperties: false`. Regressions usually show up as schema-check failures, boot-time probe failures, missing audio/SoC child devices, bad firmware/resource allocation, broken suspend/resume, or silent routing/clocking errors in board audio paths.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/sound/cirrus,ep9301-i2s.yaml` for the targeted schema and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/sound/cirrus,ep9301-i2s.yaml` against boards that instantiate it. The schema has 1 embedded example; keep those examples valid under targeted binding checks. Cross-check compatible strings against driver `of_match_table` entries and inspect DTS users for register tuple counts, interrupt names, clocks/resets, supplies, DMA channels, graph endpoints, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/cirrus,ep9301-i2s.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/cirrus,lochnagar.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/cirrus,lochnagar.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/cirrus,lochnagar.yaml` defines the audio codec or amplifier binding titled `Cirrus Logic Lochnagar Audio Development Board`. Lochnagar is an evaluation and development board for Cirrus Logic Smart CODEC and Amp devices. It constrains source DTS and compiled DTB hardware descriptions before Linux drivers consume the node.

## Important APIs, Types, and Functions
The API surface is the devicetree ABI rather than callable code. `compatible` uses an `enum` of supported tokens with 1 token: `cirrus,lochnagar2-soundcard`. Top-level properties are `compatible`, `#sound-dai-cells`, `clocks`, `clock-names`. Required top-level properties are `compatible`, `#sound-dai-cells`, `clocks`, `clock-names`. Nested or reusable constraints include composition/conditionals: `allOf`; referenced schemas: `dai-common.yaml#`; notable enum/const values: `1`, `mclk`. The highest-risk contract area is compatible strings, bus address, reset/shutdown GPIOs, supplies, clocks, interrupts, DAI cells, widgets/routes, and chip-specific tuning properties.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this file plus `$ref` targets, and enforces required properties, array cardinality, constants, enums, and `allOf`. `dtbs_check` then matches compiled DTS nodes by `compatible`, `$nodename`, or parent-schema inclusion, descends into pattern-matched children, and applies `additionalProperties` or `unevaluatedProperties` closure. Runtime flow begins only after the DTB is loaded: Linux bus, SoC, ASoC, MFD, syscon, or firmware drivers bind from compatible strings and acquire the resources described here.

## State and Persistence Behavior
The YAML itself stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: compatible strings, property names, phandle names, register tuple ordering, child-node names, and examples become contracts in source DTS files and compiled DTBs. Runtime state is created by the matched kernel drivers after probe, including regmap cache, DAPM power state, bias levels, PLL/clock configuration, jack/interrupt state, and audio stream parameters owned by ASoC drivers.

## Dependencies and Integration Points
Maintainers listed: patches@opensource.cirrus.com. Schema dependencies include `dai-common.yaml#`. Integration points include ASoC codec/component drivers, I2C/SPI/platform bus probing, DAPM graph construction, regulators, clocks, GPIO controls, and machine-driver links. The file also integrates with Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and source DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to compatible strings, bus address, reset/shutdown GPIOs, supplies, clocks, interrupts, DAI cells, widgets/routes, and chip-specific tuning properties, drift between documented compatible strings and driver match tables, incorrect resource ordering, phandle names, or cell counts that block probe or misconfigure hardware, variant-specific conditional branches accepting one SoC/chip while rejecting another, lack of embedded examples, leaving coverage dependent on in-tree DTS users. This schema closes composed schemas with `unevaluatedProperties: false`. Regressions usually show up as schema-check failures, boot-time probe failures, missing audio/SoC child devices, bad firmware/resource allocation, broken suspend/resume, or silent routing/clocking errors in board audio paths.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/sound/cirrus,lochnagar.yaml` for the targeted schema and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/sound/cirrus,lochnagar.yaml` against boards that instantiate it. There are no embedded examples, so real DTS users and schema-only checks are the main coverage. Cross-check compatible strings against driver `of_match_table` entries and inspect DTS users for register tuple counts, interrupt names, clocks/resets, supplies, DMA channels, graph endpoints, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/cirrus,lochnagar.yaml -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/cix,sky1-ipbloq-hda.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/cix,sky1-ipbloq-hda.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/cix,sky1-ipbloq-hda.yaml` defines the audio controller or sound-card binding titled `CIX IPBLOQ HDA controller`. CIX IPBLOQ High Definition Audio (HDA) Controller It constrains source DTS and compiled DTB hardware descriptions before Linux drivers consume the node.

## Important APIs, Types, and Functions
The API surface is the devicetree ABI rather than callable code. `compatible` uses a single `const` token with 1 token: `cix,sky1-ipbloq-hda`. Top-level properties are `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `resets`. Required top-level properties are `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `resets`. Nested or reusable constraints include composition/conditionals: `allOf`; referenced schemas: `sound-card-common.yaml#`; notable enum/const values: `ipg`, `per`. The highest-risk contract area is register and interrupt resources, clocks/resets, DMA channels, sound-dai cells, graph ports/endpoints, routing, and SoC-specific compatible strings.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this file plus `$ref` targets, and enforces required properties, array cardinality, constants, enums, and `allOf`. `dtbs_check` then matches compiled DTS nodes by `compatible`, `$nodename`, or parent-schema inclusion, descends into pattern-matched children, and applies `additionalProperties` or `unevaluatedProperties` closure. Runtime flow begins only after the DTB is loaded: Linux bus, SoC, ASoC, MFD, syscon, or firmware drivers bind from compatible strings and acquire the resources described here.

## State and Persistence Behavior
The YAML itself stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: compatible strings, property names, phandle names, register tuple ordering, child-node names, and examples become contracts in source DTS files and compiled DTBs. Runtime state is created by the matched kernel drivers after probe, including DAI/controller probe state, DMA stream state, clocking, reset state, and sound-card topology owned by ASoC runtime drivers.

## Dependencies and Integration Points
Maintainers listed: Joakim Zhang <joakim.zhang@cixtech.com>. Schema dependencies include `sound-card-common.yaml#`. Integration points include ASoC CPU DAI drivers, platform DMA engines, machine drivers, graph/simple-card parsing, clocks/resets, pinctrl, and board DTS sound links. The file also integrates with Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and source DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to register and interrupt resources, clocks/resets, DMA channels, sound-dai cells, graph ports/endpoints, routing, and SoC-specific compatible strings, drift between documented compatible strings and driver match tables, incorrect resource ordering, phandle names, or cell counts that block probe or misconfigure hardware, variant-specific conditional branches accepting one SoC/chip while rejecting another. This schema closes composed schemas with `unevaluatedProperties: false`. Regressions usually show up as schema-check failures, boot-time probe failures, missing audio/SoC child devices, bad firmware/resource allocation, broken suspend/resume, or silent routing/clocking errors in board audio paths.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/sound/cix,sky1-ipbloq-hda.yaml` for the targeted schema and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/sound/cix,sky1-ipbloq-hda.yaml` against boards that instantiate it. The schema has 1 embedded example; keep those examples valid under targeted binding checks. Cross-check compatible strings against driver `of_match_table` entries and inspect DTS users for register tuple counts, interrupt names, clocks/resets, supplies, DMA channels, graph endpoints, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/cix,sky1-ipbloq-hda.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/component-common.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/component-common.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/component-common.yaml` defines the reusable ASoC graph/common binding titled `Audio Component Common Properties`. It constrains source DTS and compiled DTB hardware descriptions through compatible strings, required resources, child-node topology, and shared schema references before Linux drivers consume the node.

## Important APIs, Types, and Functions
The API surface is the devicetree ABI rather than callable code. This is a reusable schema fragment, so its exported API is the properties it contributes to including bindings. Top-level properties are `sound-name-prefix`. Required top-level properties are none declared. Nested or reusable constraints include referenced schemas: `/schemas/types.yaml#/definitions/string`. The highest-risk contract area is sound-dai links, endpoint graph topology, DAI format and clock-master flags, routing/widgets, and reusable component constraints.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this file plus `$ref` targets, and enforces required properties, array cardinality, constants, enums, and no top-level conditionals. `dtbs_check` then matches compiled DTS nodes by `compatible`, `$nodename`, or parent-schema inclusion, descends into pattern-matched children, and applies `additionalProperties` or `unevaluatedProperties` closure. Runtime flow begins only after the DTB is loaded: Linux bus, SoC, ASoC, MFD, syscon, or firmware drivers bind from compatible strings and acquire the resources described here.

## State and Persistence Behavior
The YAML itself stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: compatible strings, property names, phandle names, register tuple ordering, child-node names, and examples become contracts in source DTS files and compiled DTBs. Runtime state is created by the matched kernel drivers after probe, including ASoC card/link topology, endpoint phandle resolution, DAI format negotiation, and runtime stream state owned by sound drivers.

## Dependencies and Integration Points
Maintainers listed: Jerome Brunet <jbrunet@baylibre.com>. Schema dependencies include `/schemas/types.yaml#/definitions/string`. Integration points include ASoC card parsing, graph-card endpoint walking, DAI link construction, codec/component schemas, and DTS sound-card validation. The file also integrates with Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and source DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to sound-dai links, endpoint graph topology, DAI format and clock-master flags, routing/widgets, and reusable component constraints, drift between documented compatible strings and driver match tables, incorrect resource ordering, phandle names, or cell counts that block probe or misconfigure hardware, permissive extra properties that can hide spelling mistakes, lack of embedded examples, leaving coverage dependent on in-tree DTS users. This schema permits additional top-level properties. Regressions usually show up as schema-check failures, boot-time probe failures, missing audio/SoC child devices, bad firmware/resource allocation, broken suspend/resume, or silent routing/clocking errors in board audio paths.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/sound/component-common.yaml` for the targeted schema and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/sound/component-common.yaml` against boards that instantiate it. There are no embedded examples, so real DTS users and schema-only checks are the main coverage. Cross-check compatible strings against driver `of_match_table` entries and inspect DTS users for register tuple counts, interrupt names, clocks/resets, supplies, DMA channels, graph endpoints, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/component-common.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/dai-common.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/dai-common.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/dai-common.yaml` defines the reusable ASoC graph/common binding titled `Digital Audio Interface Common Properties`. It constrains source DTS and compiled DTB hardware descriptions through compatible strings, required resources, child-node topology, and shared schema references before Linux drivers consume the node.

## Important APIs, Types, and Functions
The API surface is the devicetree ABI rather than callable code. This is a reusable schema fragment, so its exported API is the properties it contributes to including bindings. Top-level properties are `#sound-dai-cells`. Required top-level properties are none declared. Nested or reusable constraints include composition/conditionals: `allOf`; referenced schemas: `component-common.yaml#`. The highest-risk contract area is sound-dai links, endpoint graph topology, DAI format and clock-master flags, routing/widgets, and reusable component constraints.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this file plus `$ref` targets, and enforces required properties, array cardinality, constants, enums, and `allOf`. `dtbs_check` then matches compiled DTS nodes by `compatible`, `$nodename`, or parent-schema inclusion, descends into pattern-matched children, and applies `additionalProperties` or `unevaluatedProperties` closure. Runtime flow begins only after the DTB is loaded: Linux bus, SoC, ASoC, MFD, syscon, or firmware drivers bind from compatible strings and acquire the resources described here.

## State and Persistence Behavior
The YAML itself stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: compatible strings, property names, phandle names, register tuple ordering, child-node names, and examples become contracts in source DTS files and compiled DTBs. Runtime state is created by the matched kernel drivers after probe, including ASoC card/link topology, endpoint phandle resolution, DAI format negotiation, and runtime stream state owned by sound drivers.

## Dependencies and Integration Points
Maintainers listed: Jerome Brunet <jbrunet@baylibre.com>. Schema dependencies include `component-common.yaml#`. Integration points include ASoC card parsing, graph-card endpoint walking, DAI link construction, codec/component schemas, and DTS sound-card validation. The file also integrates with Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and source DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to sound-dai links, endpoint graph topology, DAI format and clock-master flags, routing/widgets, and reusable component constraints, drift between documented compatible strings and driver match tables, incorrect resource ordering, phandle names, or cell counts that block probe or misconfigure hardware, variant-specific conditional branches accepting one SoC/chip while rejecting another, permissive extra properties that can hide spelling mistakes, lack of embedded examples, leaving coverage dependent on in-tree DTS users. This schema permits additional top-level properties. Regressions usually show up as schema-check failures, boot-time probe failures, missing audio/SoC child devices, bad firmware/resource allocation, broken suspend/resume, or silent routing/clocking errors in board audio paths.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/sound/dai-common.yaml` for the targeted schema and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/sound/dai-common.yaml` against boards that instantiate it. There are no embedded examples, so real DTS users and schema-only checks are the main coverage. Cross-check compatible strings against driver `of_match_table` entries and inspect DTS users for register tuple counts, interrupt names, clocks/resets, supplies, DMA channels, graph endpoints, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/dai-common.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/dai-params.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/dai-params.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/dai-params.yaml` defines the reusable ASoC graph/common binding titled `Digital Audio Interface (DAI) Stream Parameters`. It constrains source DTS and compiled DTB hardware descriptions through compatible strings, required resources, child-node topology, and shared schema references before Linux drivers consume the node.

## Important APIs, Types, and Functions
The API surface is the devicetree ABI rather than callable code. This is a reusable schema fragment, so its exported API is the properties it contributes to including bindings. Top-level properties are `convert-channels`, `convert-sample-format`, `convert-rate`. Required top-level properties are none declared. Nested or reusable constraints include referenced schemas: `/schemas/types.yaml#/definitions/string`, `/schemas/types.yaml#/definitions/uint32`; notable enum/const values: `s8`, `s16_le`, `s24_le`, `s24_3le`, `s32_le`. The highest-risk contract area is sound-dai links, endpoint graph topology, DAI format and clock-master flags, routing/widgets, and reusable component constraints.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this file plus `$ref` targets, and enforces required properties, array cardinality, constants, enums, and no top-level conditionals. `dtbs_check` then matches compiled DTS nodes by `compatible`, `$nodename`, or parent-schema inclusion, descends into pattern-matched children, and applies `additionalProperties` or `unevaluatedProperties` closure. Runtime flow begins only after the DTB is loaded: Linux bus, SoC, ASoC, MFD, syscon, or firmware drivers bind from compatible strings and acquire the resources described here.

## State and Persistence Behavior
The YAML itself stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: compatible strings, property names, phandle names, register tuple ordering, child-node names, and examples become contracts in source DTS files and compiled DTBs. Runtime state is created by the matched kernel drivers after probe, including ASoC card/link topology, endpoint phandle resolution, DAI format negotiation, and runtime stream state owned by sound drivers.

## Dependencies and Integration Points
Maintainers listed: Kuninori Morimoto <kuninori.morimoto.gx@renesas.com>. Schema dependencies include `/schemas/types.yaml#/definitions/string`, `/schemas/types.yaml#/definitions/uint32`. Integration points include ASoC card parsing, graph-card endpoint walking, DAI link construction, codec/component schemas, and DTS sound-card validation. The file also integrates with Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and source DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to sound-dai links, endpoint graph topology, DAI format and clock-master flags, routing/widgets, and reusable component constraints, drift between documented compatible strings and driver match tables, incorrect resource ordering, phandle names, or cell counts that block probe or misconfigure hardware, permissive extra properties that can hide spelling mistakes, lack of embedded examples, leaving coverage dependent on in-tree DTS users. This schema permits additional top-level properties. Regressions usually show up as schema-check failures, boot-time probe failures, missing audio/SoC child devices, bad firmware/resource allocation, broken suspend/resume, or silent routing/clocking errors in board audio paths.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/sound/dai-params.yaml` for the targeted schema and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/sound/dai-params.yaml` against boards that instantiate it. There are no embedded examples, so real DTS users and schema-only checks are the main coverage. Cross-check compatible strings against driver `of_match_table` entries and inspect DTS users for register tuple counts, interrupt names, clocks/resets, supplies, DMA channels, graph endpoints, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/dai-params.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/davinci-mcasp-audio.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/davinci-mcasp-audio.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/davinci-mcasp-audio.yaml` defines the audio controller or sound-card binding titled `McASP Controller for TI SoCs`. It constrains source DTS and compiled DTB hardware descriptions through compatible strings, required resources, child-node topology, and shared schema references before Linux drivers consume the node.

## Important APIs, Types, and Functions
The API surface is the devicetree ABI rather than callable code. `compatible` uses an `enum` of supported tokens with 5 tokens: `ti,dm646x-mcasp-audio`, `ti,da830-mcasp-audio`, `ti,am33xx-mcasp-audio`, `ti,dra7-mcasp-audio`, `ti,omap4-mcasp-audio`. Top-level properties are `compatible`, `reg`, `reg-names`, `op-mode`, `tdm-slots`, `tdm-slots-rx`, `ti,async-mode`, `serial-dir`, `dmas`, `dma-names`, `ti,hwmods`, `tx-num-evt`, `rx-num-evt`, `dismod`, `interrupts`, `interrupt-names`, `fck_parent`, `auxclk-fs-ratio`, `auxclk-fs-ratio-rx`, `gpio-controller`, `#gpio-cells`, `clocks`, `clock-names`, `power-domains`, `#sound-dai-cells`, `port`. Required top-level properties are `compatible`, `reg`, `reg-names`, `dmas`, `dma-names`, `interrupts`, `interrupt-names`. Nested or reusable constraints include composition/conditionals: `allOf`; referenced schemas: `/schemas/types.yaml#/definitions/string`, `/schemas/types.yaml#/definitions/uint32`, `/schemas/types.yaml#/definitions/uint32-array`, `dai-common.yaml#`; notable enum/const values: `0`, `1`, `2`, `3`, `mpu`, `dat`, `tx`, `rx`, `common`, `fck`, `ahclkx`, `ahclkr`. The highest-risk contract area is register and interrupt resources, clocks/resets, DMA channels, sound-dai cells, graph ports/endpoints, routing, and SoC-specific compatible strings.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this file plus `$ref` targets, and enforces required properties, array cardinality, constants, enums, and `allOf`. `dtbs_check` then matches compiled DTS nodes by `compatible`, `$nodename`, or parent-schema inclusion, descends into pattern-matched children, and applies `additionalProperties` or `unevaluatedProperties` closure. Runtime flow begins only after the DTB is loaded: Linux bus, SoC, ASoC, MFD, syscon, or firmware drivers bind from compatible strings and acquire the resources described here.

## State and Persistence Behavior
The YAML itself stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: compatible strings, property names, phandle names, register tuple ordering, child-node names, and examples become contracts in source DTS files and compiled DTBs. Runtime state is created by the matched kernel drivers after probe, including DAI/controller probe state, DMA stream state, clocking, reset state, and sound-card topology owned by ASoC runtime drivers.

## Dependencies and Integration Points
Maintainers listed: Jayesh Choudhary <j-choudhary@ti.com>. Schema dependencies include `/schemas/types.yaml#/definitions/string`, `/schemas/types.yaml#/definitions/uint32`, `/schemas/types.yaml#/definitions/uint32-array`, `dai-common.yaml#`. Integration points include ASoC CPU DAI drivers, platform DMA engines, machine drivers, graph/simple-card parsing, clocks/resets, pinctrl, and board DTS sound links. The file also integrates with Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and source DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to register and interrupt resources, clocks/resets, DMA channels, sound-dai cells, graph ports/endpoints, routing, and SoC-specific compatible strings, drift between documented compatible strings and driver match tables, incorrect resource ordering, phandle names, or cell counts that block probe or misconfigure hardware, variant-specific conditional branches accepting one SoC/chip while rejecting another. This schema closes composed schemas with `unevaluatedProperties: false`. Regressions usually show up as schema-check failures, boot-time probe failures, missing audio/SoC child devices, bad firmware/resource allocation, broken suspend/resume, or silent routing/clocking errors in board audio paths.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/sound/davinci-mcasp-audio.yaml` for the targeted schema and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/sound/davinci-mcasp-audio.yaml` against boards that instantiate it. The schema has 1 embedded example; keep those examples valid under targeted binding checks. Cross-check compatible strings against driver `of_match_table` entries and inspect DTS users for register tuple counts, interrupt names, clocks/resets, supplies, DMA channels, graph endpoints, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/davinci-mcasp-audio.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/davinci-mcbsp.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/davinci-mcbsp.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/davinci-mcbsp.yaml` defines the audio controller or sound-card binding titled `McBSP Controller for TI SoCs`. It constrains source DTS and compiled DTB hardware descriptions through compatible strings, required resources, child-node topology, and shared schema references before Linux drivers consume the node.

## Important APIs, Types, and Functions
The API surface is the devicetree ABI rather than callable code. `compatible` uses an `enum` of supported tokens with 1 token: `ti,da850-mcbsp`. Top-level properties are `compatible`, `reg`, `reg-names`, `dmas`, `dma-names`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, `power-domains`, `#sound-dai-cells`, `ti,T1-framing-tx`, `ti,T1-framing-rx`. Required top-level properties are `#sound-dai-cells`, `compatible`, `reg`, `reg-names`, `dmas`, `dma-names`, `clocks`. Nested or reusable constraints include composition/conditionals: `allOf`; referenced schemas: `/schemas/types.yaml#/definitions/flag`, `dai-common.yaml#`; notable enum/const values: `mpu`, `dat`, `tx`, `rx`, `fck`, `clks`, `0`. The highest-risk contract area is register and interrupt resources, clocks/resets, DMA channels, sound-dai cells, graph ports/endpoints, routing, and SoC-specific compatible strings.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this file plus `$ref` targets, and enforces required properties, array cardinality, constants, enums, and `allOf`. `dtbs_check` then matches compiled DTS nodes by `compatible`, `$nodename`, or parent-schema inclusion, descends into pattern-matched children, and applies `additionalProperties` or `unevaluatedProperties` closure. Runtime flow begins only after the DTB is loaded: Linux bus, SoC, ASoC, MFD, syscon, or firmware drivers bind from compatible strings and acquire the resources described here.

## State and Persistence Behavior
The YAML itself stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: compatible strings, property names, phandle names, register tuple ordering, child-node names, and examples become contracts in source DTS files and compiled DTBs. Runtime state is created by the matched kernel drivers after probe, including DAI/controller probe state, DMA stream state, clocking, reset state, and sound-card topology owned by ASoC runtime drivers.

## Dependencies and Integration Points
Maintainers listed: Bastien Curutchet <bastien.curutchet@bootlin.com>. Schema dependencies include `/schemas/types.yaml#/definitions/flag`, `dai-common.yaml#`. Integration points include ASoC CPU DAI drivers, platform DMA engines, machine drivers, graph/simple-card parsing, clocks/resets, pinctrl, and board DTS sound links. The file also integrates with Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and source DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to register and interrupt resources, clocks/resets, DMA channels, sound-dai cells, graph ports/endpoints, routing, and SoC-specific compatible strings, drift between documented compatible strings and driver match tables, incorrect resource ordering, phandle names, or cell counts that block probe or misconfigure hardware, variant-specific conditional branches accepting one SoC/chip while rejecting another. This schema closes composed schemas with `unevaluatedProperties: false`. Regressions usually show up as schema-check failures, boot-time probe failures, missing audio/SoC child devices, bad firmware/resource allocation, broken suspend/resume, or silent routing/clocking errors in board audio paths.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/sound/davinci-mcbsp.yaml` for the targeted schema and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/sound/davinci-mcbsp.yaml` against boards that instantiate it. The schema has 1 embedded example; keep those examples valid under targeted binding checks. Cross-check compatible strings against driver `of_match_table` entries and inspect DTS users for register tuple counts, interrupt names, clocks/resets, supplies, DMA channels, graph endpoints, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/davinci-mcbsp.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/dialog,da7219.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/dialog,da7219.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/dialog,da7219.yaml` defines the audio codec or amplifier binding titled `Dialog Semiconductor DA7219 Audio Codec`. The DA7219 is an ultra low-power audio codec with in-built advanced accessory detection (AAD) for mobile computing and accessory applications, which supports sample rates up to 96 kHz at 24-bit resolution. It constrains source DTS and compiled DTB hardware descriptions before Linux drivers consume the node.

## Important APIs, Types, and Functions
The API surface is the devicetree ABI rather than callable code. `compatible` uses a single `const` token with 1 token: `dlg,da7219`. Top-level properties are `compatible`, `reg`, `interrupts`, `VDD-supply`, `VDDMIC-supply`, `VDDIO-supply`, `interrupt-names`, `wakeup-source`, `#clock-cells`, `clock-output-names`, `clocks`, `clock-names`, `dlg,micbias-lvl`, `dlg,mic-amp-in-sel`, `da7219_aad`. Required top-level properties are `compatible`, `reg`, `interrupts`, `VDD-supply`, `VDDMIC-supply`, `VDDIO-supply`. Nested or reusable constraints include referenced schemas: `/schemas/types.yaml#/definitions/string`, `/schemas/types.yaml#/definitions/uint32`; notable enum/const values: `wakeup`, `irq`, `1600`, `1800`, `2000`, `2200`, `2400`, `2600`, `diff`, `se_p`, `se_n`, `2800`, `2900`, `2`, `5`, `10`, and 17 more. The highest-risk contract area is compatible strings, bus address, reset/shutdown GPIOs, supplies, clocks, interrupts, DAI cells, widgets/routes, and chip-specific tuning properties.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this file plus `$ref` targets, and enforces required properties, array cardinality, constants, enums, and no top-level conditionals. `dtbs_check` then matches compiled DTS nodes by `compatible`, `$nodename`, or parent-schema inclusion, descends into pattern-matched children, and applies `additionalProperties` or `unevaluatedProperties` closure. Runtime flow begins only after the DTB is loaded: Linux bus, SoC, ASoC, MFD, syscon, or firmware drivers bind from compatible strings and acquire the resources described here.

## State and Persistence Behavior
The YAML itself stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: compatible strings, property names, phandle names, register tuple ordering, child-node names, and examples become contracts in source DTS files and compiled DTBs. Runtime state is created by the matched kernel drivers after probe, including regmap cache, DAPM power state, bias levels, PLL/clock configuration, jack/interrupt state, and audio stream parameters owned by ASoC drivers.

## Dependencies and Integration Points
Maintainers listed: David Rau <David.Rau.opensource@dm.renesas.com>. Schema dependencies include `/schemas/types.yaml#/definitions/string`, `/schemas/types.yaml#/definitions/uint32`. Integration points include ASoC codec/component drivers, I2C/SPI/platform bus probing, DAPM graph construction, regulators, clocks, GPIO controls, and machine-driver links. The file also integrates with Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and source DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to compatible strings, bus address, reset/shutdown GPIOs, supplies, clocks, interrupts, DAI cells, widgets/routes, and chip-specific tuning properties, drift between documented compatible strings and driver match tables, incorrect resource ordering, phandle names, or cell counts that block probe or misconfigure hardware. This schema rejects unknown top-level properties with `additionalProperties: false`. Regressions usually show up as schema-check failures, boot-time probe failures, missing audio/SoC child devices, bad firmware/resource allocation, broken suspend/resume, or silent routing/clocking errors in board audio paths.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/sound/dialog,da7219.yaml` for the targeted schema and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/sound/dialog,da7219.yaml` against boards that instantiate it. The schema has 1 embedded example; keep those examples valid under targeted binding checks. Cross-check compatible strings against driver `of_match_table` entries and inspect DTS users for register tuple counts, interrupt names, clocks/resets, supplies, DMA channels, graph endpoints, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/dialog,da7219.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/dlg,da7213.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/dlg,da7213.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/dlg,da7213.yaml` defines the audio codec or amplifier binding titled `Dialog Semiconductor DA7212/DA7213 Audio Codec`. It constrains source DTS and compiled DTB hardware descriptions through compatible strings, required resources, child-node topology, and shared schema references before Linux drivers consume the node.

## Important APIs, Types, and Functions
The API surface is the devicetree ABI rather than callable code. `compatible` uses an `enum` of supported tokens with 2 tokens: `dlg,da7212`, `dlg,da7213`. Top-level properties are `compatible`, `reg`, `clocks`, `clock-names`, `#sound-dai-cells`, `dlg,micbias1-lvl`, `dlg,micbias2-lvl`, `dlg,dmic-data-sel`, `dlg,dmic-samplephase`, `dlg,dmic-clkrate`, `VDDA-supply`, `VDDIO-supply`, `VDDMIC-supply`, `VDDSP-supply`, `ports`, `port`. Required top-level properties are `compatible`, `reg`. Nested or reusable constraints include composition/conditionals: `allOf`; referenced schemas: `/schemas/types.yaml#/definitions/uint32`, `audio-graph-port.yaml#`, `audio-graph-port.yaml#/definitions/ports`, `dai-common.yaml#`; notable enum/const values: `1600`, `2200`, `2500`, `3000`, `lrise_rfall`, `lfall_rrise`, `on_clkedge`, `between_clkedge`, `1500000`, `3000000`, `mclk`, `0`. The highest-risk contract area is compatible strings, bus address, reset/shutdown GPIOs, supplies, clocks, interrupts, DAI cells, widgets/routes, and chip-specific tuning properties.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this file plus `$ref` targets, and enforces required properties, array cardinality, constants, enums, and `allOf`. `dtbs_check` then matches compiled DTS nodes by `compatible`, `$nodename`, or parent-schema inclusion, descends into pattern-matched children, and applies `additionalProperties` or `unevaluatedProperties` closure. Runtime flow begins only after the DTB is loaded: Linux bus, SoC, ASoC, MFD, syscon, or firmware drivers bind from compatible strings and acquire the resources described here.

## State and Persistence Behavior
The YAML itself stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: compatible strings, property names, phandle names, register tuple ordering, child-node names, and examples become contracts in source DTS files and compiled DTBs. Runtime state is created by the matched kernel drivers after probe, including regmap cache, DAPM power state, bias levels, PLL/clock configuration, jack/interrupt state, and audio stream parameters owned by ASoC drivers.

## Dependencies and Integration Points
Maintainers listed: Support Opensource <support.opensource@diasemi.com>. Schema dependencies include `/schemas/types.yaml#/definitions/uint32`, `audio-graph-port.yaml#`, `audio-graph-port.yaml#/definitions/ports`, `dai-common.yaml#`. Integration points include ASoC codec/component drivers, I2C/SPI/platform bus probing, DAPM graph construction, regulators, clocks, GPIO controls, and machine-driver links. The file also integrates with Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and source DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to compatible strings, bus address, reset/shutdown GPIOs, supplies, clocks, interrupts, DAI cells, widgets/routes, and chip-specific tuning properties, drift between documented compatible strings and driver match tables, incorrect resource ordering, phandle names, or cell counts that block probe or misconfigure hardware, variant-specific conditional branches accepting one SoC/chip while rejecting another. This schema closes composed schemas with `unevaluatedProperties: false`. Regressions usually show up as schema-check failures, boot-time probe failures, missing audio/SoC child devices, bad firmware/resource allocation, broken suspend/resume, or silent routing/clocking errors in board audio paths.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/sound/dlg,da7213.yaml` for the targeted schema and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/sound/dlg,da7213.yaml` against boards that instantiate it. The schema has 1 embedded example; keep those examples valid under targeted binding checks. Cross-check compatible strings against driver `of_match_table` entries and inspect DTS users for register tuple counts, interrupt names, clocks/resets, supplies, DMA channels, graph endpoints, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/dlg,da7213.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/dmic-codec.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/dmic-codec.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/dmic-codec.yaml` defines the audio codec or amplifier binding titled `Generic PDM Digital microphone (DMIC) codec`. It constrains source DTS and compiled DTB hardware descriptions through compatible strings, required resources, child-node topology, and shared schema references before Linux drivers consume the node.

## Important APIs, Types, and Functions
The API surface is the devicetree ABI rather than callable code. `compatible` uses a single `const` token with 1 token: `dmic-codec`. Top-level properties are `compatible`, `#sound-dai-cells`, `vref-supply`, `dmicen-gpios`, `num-channels`, `modeswitch-delay-ms`, `wakeup-delay-ms`. Required top-level properties are `compatible`. Nested or reusable constraints include composition/conditionals: `allOf`; referenced schemas: `/schemas/types.yaml#/definitions/uint32`, `dai-common.yaml#`; notable enum/const values: `0`. The highest-risk contract area is compatible strings, bus address, reset/shutdown GPIOs, supplies, clocks, interrupts, DAI cells, widgets/routes, and chip-specific tuning properties.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this file plus `$ref` targets, and enforces required properties, array cardinality, constants, enums, and `allOf`. `dtbs_check` then matches compiled DTS nodes by `compatible`, `$nodename`, or parent-schema inclusion, descends into pattern-matched children, and applies `additionalProperties` or `unevaluatedProperties` closure. Runtime flow begins only after the DTB is loaded: Linux bus, SoC, ASoC, MFD, syscon, or firmware drivers bind from compatible strings and acquire the resources described here.

## State and Persistence Behavior
The YAML itself stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: compatible strings, property names, phandle names, register tuple ordering, child-node names, and examples become contracts in source DTS files and compiled DTBs. Runtime state is created by the matched kernel drivers after probe, including regmap cache, DAPM power state, bias levels, PLL/clock configuration, jack/interrupt state, and audio stream parameters owned by ASoC drivers.

## Dependencies and Integration Points
Maintainers listed: Arnaud Pouliquen <arnaud.pouliquen@foss.st.com>. Schema dependencies include `/schemas/types.yaml#/definitions/uint32`, `dai-common.yaml#`. Integration points include ASoC codec/component drivers, I2C/SPI/platform bus probing, DAPM graph construction, regulators, clocks, GPIO controls, and machine-driver links. The file also integrates with Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and source DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to compatible strings, bus address, reset/shutdown GPIOs, supplies, clocks, interrupts, DAI cells, widgets/routes, and chip-specific tuning properties, drift between documented compatible strings and driver match tables, incorrect resource ordering, phandle names, or cell counts that block probe or misconfigure hardware, variant-specific conditional branches accepting one SoC/chip while rejecting another. This schema closes composed schemas with `unevaluatedProperties: false`. Regressions usually show up as schema-check failures, boot-time probe failures, missing audio/SoC child devices, bad firmware/resource allocation, broken suspend/resume, or silent routing/clocking errors in board audio paths.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/sound/dmic-codec.yaml` for the targeted schema and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/sound/dmic-codec.yaml` against boards that instantiate it. The schema has 1 embedded example; keep those examples valid under targeted binding checks. Cross-check compatible strings against driver `of_match_table` entries and inspect DTS users for register tuple counts, interrupt names, clocks/resets, supplies, DMA channels, graph endpoints, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/dmic-codec.yaml -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/everest,es7241.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/everest,es7241.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/everest,es7241.yaml` defines the audio codec or amplifier binding titled `Everest ES7241 2 channels I2S analog to digital converter`. It constrains source DTS and compiled DTB hardware descriptions through compatible strings, required resources, child-node topology, and shared schema references before Linux drivers consume the node.

## Important APIs, Types, and Functions
The API surface is the devicetree ABI rather than callable code. `compatible` uses an `enum` of supported tokens with 1 token: `everest,es7241`. Top-level properties are `compatible`, `reset-gpios`, `m0-gpios`, `m1-gpios`, `everest,sdout-pull-down`, `VDDP-supply`, `VDDA-supply`, `VDDD-supply`, `#sound-dai-cells`. Required top-level properties are `compatible`, `VDDP-supply`, `VDDA-supply`, `VDDD-supply`. Nested or reusable constraints include composition/conditionals: `allOf`; referenced schemas: `dai-common.yaml#`; notable enum/const values: `0`. The highest-risk contract area is compatible strings, bus address, reset/shutdown GPIOs, supplies, clocks, interrupts, DAI cells, widgets/routes, and chip-specific tuning properties.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this file plus `$ref` targets, and enforces required properties, array cardinality, constants, enums, and `allOf`. `dtbs_check` then matches compiled DTS nodes by `compatible`, `$nodename`, or parent-schema inclusion, descends into pattern-matched children, and applies `additionalProperties` or `unevaluatedProperties` closure. Runtime flow begins only after the DTB is loaded: Linux bus, SoC, ASoC, MFD, syscon, or firmware drivers bind from compatible strings and acquire the resources described here.

## State and Persistence Behavior
The YAML itself stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: compatible strings, property names, phandle names, register tuple ordering, child-node names, and examples become contracts in source DTS files and compiled DTBs. Runtime state is created by the matched kernel drivers after probe, including regmap cache, DAPM power state, bias levels, PLL/clock configuration, jack/interrupt state, and audio stream parameters owned by ASoC drivers.

## Dependencies and Integration Points
Maintainers listed: Neil Armstrong <neil.armstrong@linaro.org>. Schema dependencies include `dai-common.yaml#`. Integration points include ASoC codec/component drivers, I2C/SPI/platform bus probing, DAPM graph construction, regulators, clocks, GPIO controls, and machine-driver links. The file also integrates with Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and source DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to compatible strings, bus address, reset/shutdown GPIOs, supplies, clocks, interrupts, DAI cells, widgets/routes, and chip-specific tuning properties, drift between documented compatible strings and driver match tables, incorrect resource ordering, phandle names, or cell counts that block probe or misconfigure hardware, variant-specific conditional branches accepting one SoC/chip while rejecting another. This schema closes composed schemas with `unevaluatedProperties: false`. Regressions usually show up as schema-check failures, boot-time probe failures, missing audio/SoC child devices, bad firmware/resource allocation, broken suspend/resume, or silent routing/clocking errors in board audio paths.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/sound/everest,es7241.yaml` for the targeted schema and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/sound/everest,es7241.yaml` against boards that instantiate it. The schema has 1 embedded example; keep those examples valid under targeted binding checks. Cross-check compatible strings against driver `of_match_table` entries and inspect DTS users for register tuple counts, interrupt names, clocks/resets, supplies, DMA channels, graph endpoints, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/everest,es7241.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/everest,es8316.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/everest,es8316.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/everest,es8316.yaml` defines the audio codec or amplifier binding titled `Everest ES8311, ES8316 and ES8323 audio CODECs`. Everest ES8311, ES8316 and ES8323 audio CODECs Pins on the device (for linking into audio routes): Outputs: * LOUT: Left Analog Output * ROUT: Right Analog Output * MICBIAS: Microphone Bias Inputs: * MIC1P: Microphone 1 Positive Analog Input * MIC1N: Microphone 1 Negative Analog Input * MIC2P: Microphone 2 Positive Analog Input * MIC2N: Microphone 2 Negative Analog Input It constrains source DTS and compiled DTB hardware descriptions before Linux drivers consume the node.

## Important APIs, Types, and Functions
The API surface is the devicetree ABI rather than callable code. `compatible` uses an `enum` of supported tokens with 3 tokens: `everest,es8311`, `everest,es8316`, `everest,es8323`. Top-level properties are `compatible`, `reg`, `clocks`, `clock-names`, `interrupts`, `port`, `#sound-dai-cells`. Required top-level properties are `compatible`, `reg`, `#sound-dai-cells`. Nested or reusable constraints include composition/conditionals: `allOf`; referenced schemas: `audio-graph-port.yaml#`, `dai-common.yaml#`; notable enum/const values: `mclk`, `0`. The highest-risk contract area is compatible strings, bus address, reset/shutdown GPIOs, supplies, clocks, interrupts, DAI cells, widgets/routes, and chip-specific tuning properties.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this file plus `$ref` targets, and enforces required properties, array cardinality, constants, enums, and `allOf`. `dtbs_check` then matches compiled DTS nodes by `compatible`, `$nodename`, or parent-schema inclusion, descends into pattern-matched children, and applies `additionalProperties` or `unevaluatedProperties` closure. Runtime flow begins only after the DTB is loaded: Linux bus, SoC, ASoC, MFD, syscon, or firmware drivers bind from compatible strings and acquire the resources described here.

## State and Persistence Behavior
The YAML itself stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: compatible strings, property names, phandle names, register tuple ordering, child-node names, and examples become contracts in source DTS files and compiled DTBs. Runtime state is created by the matched kernel drivers after probe, including regmap cache, DAPM power state, bias levels, PLL/clock configuration, jack/interrupt state, and audio stream parameters owned by ASoC drivers.

## Dependencies and Integration Points
Maintainers listed: Daniel Drake <drake@endlessm.com>, Katsuhiro Suzuki <katsuhiro@katsuster.net>, Matteo Martelli <matteomartelli3@gmail.com>, Binbin Zhou <zhoubinbin@loongson.cn>. Schema dependencies include `audio-graph-port.yaml#`, `dai-common.yaml#`. Integration points include ASoC codec/component drivers, I2C/SPI/platform bus probing, DAPM graph construction, regulators, clocks, GPIO controls, and machine-driver links. The file also integrates with Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and source DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to compatible strings, bus address, reset/shutdown GPIOs, supplies, clocks, interrupts, DAI cells, widgets/routes, and chip-specific tuning properties, drift between documented compatible strings and driver match tables, incorrect resource ordering, phandle names, or cell counts that block probe or misconfigure hardware, variant-specific conditional branches accepting one SoC/chip while rejecting another. This schema closes composed schemas with `unevaluatedProperties: false`. Regressions usually show up as schema-check failures, boot-time probe failures, missing audio/SoC child devices, bad firmware/resource allocation, broken suspend/resume, or silent routing/clocking errors in board audio paths.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/sound/everest,es8316.yaml` for the targeted schema and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/sound/everest,es8316.yaml` against boards that instantiate it. The schema has 1 embedded example; keep those examples valid under targeted binding checks. Cross-check compatible strings against driver `of_match_table` entries and inspect DTS users for register tuple counts, interrupt names, clocks/resets, supplies, DMA channels, graph endpoints, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/everest,es8316.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/everest,es8326.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/everest,es8326.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/everest,es8326.yaml` defines the audio codec or amplifier binding titled `Everest ES8326 audio CODEC`. It constrains source DTS and compiled DTB hardware descriptions through compatible strings, required resources, child-node topology, and shared schema references before Linux drivers consume the node.

## Important APIs, Types, and Functions
The API surface is the devicetree ABI rather than callable code. `compatible` uses a single `const` token with 1 token: `everest,es8326`. Top-level properties are `compatible`, `reg`, `clocks`, `clock-names`, `interrupts`, `#sound-dai-cells`, `everest,jack-pol`, `everest,mic1-src`, `everest,mic2-src`, `everest,jack-detect-inverted`, `everest,interrupt-src`, `everest,interrupt-clk`. Required top-level properties are `compatible`, `reg`, `#sound-dai-cells`. Nested or reusable constraints include referenced schemas: `/schemas/types.yaml#/definitions/flag`, `/schemas/types.yaml#/definitions/uint8`; notable enum/const values: `mclk`, `0`. The highest-risk contract area is compatible strings, bus address, reset/shutdown GPIOs, supplies, clocks, interrupts, DAI cells, widgets/routes, and chip-specific tuning properties.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this file plus `$ref` targets, and enforces required properties, array cardinality, constants, enums, and no top-level conditionals. `dtbs_check` then matches compiled DTS nodes by `compatible`, `$nodename`, or parent-schema inclusion, descends into pattern-matched children, and applies `additionalProperties` or `unevaluatedProperties` closure. Runtime flow begins only after the DTB is loaded: Linux bus, SoC, ASoC, MFD, syscon, or firmware drivers bind from compatible strings and acquire the resources described here.

## State and Persistence Behavior
The YAML itself stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: compatible strings, property names, phandle names, register tuple ordering, child-node names, and examples become contracts in source DTS files and compiled DTBs. Runtime state is created by the matched kernel drivers after probe, including regmap cache, DAPM power state, bias levels, PLL/clock configuration, jack/interrupt state, and audio stream parameters owned by ASoC drivers.

## Dependencies and Integration Points
Maintainers listed: David Yang <yangxiaohua@everest-semi.com>. Schema dependencies include `/schemas/types.yaml#/definitions/flag`, `/schemas/types.yaml#/definitions/uint8`. Integration points include ASoC codec/component drivers, I2C/SPI/platform bus probing, DAPM graph construction, regulators, clocks, GPIO controls, and machine-driver links. The file also integrates with Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and source DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to compatible strings, bus address, reset/shutdown GPIOs, supplies, clocks, interrupts, DAI cells, widgets/routes, and chip-specific tuning properties, drift between documented compatible strings and driver match tables, incorrect resource ordering, phandle names, or cell counts that block probe or misconfigure hardware. This schema rejects unknown top-level properties with `additionalProperties: false`. Regressions usually show up as schema-check failures, boot-time probe failures, missing audio/SoC child devices, bad firmware/resource allocation, broken suspend/resume, or silent routing/clocking errors in board audio paths.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/sound/everest,es8326.yaml` for the targeted schema and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/sound/everest,es8326.yaml` against boards that instantiate it. The schema has 1 embedded example; keep those examples valid under targeted binding checks. Cross-check compatible strings against driver `of_match_table` entries and inspect DTS users for register tuple counts, interrupt names, clocks/resets, supplies, DMA channels, graph endpoints, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/sound/everest,es8326.yaml -->
