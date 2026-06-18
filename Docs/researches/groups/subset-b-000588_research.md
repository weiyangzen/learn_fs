# Research Group subset-b-000588

Grouped research for Linux devicetree binding YAML schemas covering memory controllers, external memory buses, JEDEC SDRAM fragments, and MFD/system-controller devices under the Ceph client source tree. Each source file has a marker-bounded section for reconciliation into its mapped source-tree-aligned research document.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/ddr/jedec,lpddr3.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/ddr/jedec,lpddr3.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/ddr/jedec,lpddr3.yaml` defines the JEDEC SDRAM topology or device-property schema titled `LPDDR3 SDRAM compliant to JEDEC JESD209-3`. It constrains devicetree nodes through compatible strings, required resources, bus topology, and shared schema references before the corresponding Linux subsystem uses the node at probe time.

## Important APIs, Types, and Functions
The exported API is the devicetree ABI, not callable functions. `compatible` uses `oneOf` with 2 branches with 2 tokens: `samsung,K3QF2F20DB`, `jedec,lpddr3`. Top-level properties are `compatible`, `#address-cells`, `manufacturer-id`, `#size-cells`, `tCKE-min-tck`, `tCKESR-min-tck`, `tDQSCK-min-tck`, `tFAW-min-tck`, `tMRD-min-tck`, `tR2R-C2C-min-tck`, `tRAS-min-tck`, `tRC-min-tck`, `tRCD-min-tck`, `tRFC-min-tck`, `tRL-min-tck`, `tRPab-min-tck`, `tRPpb-min-tck`, `tRRD-min-tck`, `tRTP-min-tck`, `tW2W-C2C-min-tck`, `tWL-min-tck`, `tWR-min-tck`, `tWTR-min-tck`, `tXP-min-tck`, and 1 more. Required top-level properties are `compatible`, `density`, `io-width`. Important reusable or nested constraints are: composition/conditionals: `allOf`; child-node patterns: `^timings((-[0-9])+|(@[0-9a-f]+))?$`; referenced schemas: `/schemas/types.yaml#/definitions/uint32`, `jedec,lpddr3-timings.yaml`, `jedec,sdram-props.yaml#`; non-compatible enum/const values include `0`, `1`. The highest-risk contract area is SDRAM density, bus width, rank/channel placement, timing child nodes, and JEDEC manufacturer/revision compatible encoding.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this schema and any `$ref` targets, then `dtbs_check` matches real DTS nodes by `compatible`, `$nodename`, or inclusion from a parent schema. Validation checks required properties, array lengths and constants, applies `allOf`, descends into pattern-matched child nodes, and finally enforces `additionalProperties` or `unevaluatedProperties`. Runtime flow starts only after the DTB is loaded: Linux driver core or MFD population uses the compatible and resources to bind drivers.

## State and Persistence Behavior
The YAML file stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: property names, compatible fallback order, address-cell layout, child-node names, and example nodes become contracts shipped in source DTS files and compiled DTBs. Runtime state is owned by the matched kernel drivers after probe, including memory topology metadata consumed by memory-controller bindings and firmware-authored DTBs.

## Dependencies and Integration Points
Maintainers listed: Krzysztof Kozlowski <krzk@kernel.org>. Schema dependencies include `/schemas/types.yaml#/definitions/uint32`, `jedec,lpddr3-timings.yaml`, `jedec,sdram-props.yaml#`. Integration points include DDR/LPDDR memory description, boot firmware generated memory nodes, memory-controller child nodes, and dt-schema validation of rank/channel geometry. The binding also participates in Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to SDRAM density, bus width, rank/channel placement, timing child nodes, and JEDEC manufacturer/revision compatible encoding, mismatch between documented compatibles and the driver's match table, resource ordering or cell-count mistakes that pass review but break probe, conditional branches that accept one SoC or chip variant while silently rejecting another, child-node regexes that over-match unrelated children or under-match valid bus devices. This schema closes composed schemas with `unevaluatedProperties: false`. Because these bindings describe hardware contracts, regressions can appear as boot-time probe failures, missing child devices, invalid timing/ECC configuration, or dtbs_check noise across unrelated boards.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/memory-controllers/ddr/jedec,lpddr3.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/memory-controllers/ddr/jedec,lpddr3.yaml` against boards that instantiate the binding. The schema includes 1 embedded example; keep those examples compiling under `dt_binding_check`. Exercise child-node validation for `^timings((-[0-9])+|(@[0-9a-f]+))?$`. Also compare compatible strings with in-tree driver `of_match_table` entries and review DTS examples for register tuple counts, interrupt names, clocks/resets, address ranges, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/ddr/jedec,lpddr3.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/ddr/jedec,lpddr4.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/ddr/jedec,lpddr4.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/ddr/jedec,lpddr4.yaml` defines the JEDEC SDRAM topology or device-property schema titled `LPDDR4 SDRAM compliant to JEDEC JESD209-4`. It constrains devicetree nodes through compatible strings, required resources, bus topology, and shared schema references before the corresponding Linux subsystem uses the node at probe time.

## Important APIs, Types, and Functions
The exported API is the devicetree ABI, not callable functions. `compatible` uses an ordered compatible/fallback `items` sequence with 1 token: `jedec,lpddr4`. Top-level properties are `compatible`. Required top-level properties are `compatible`, `density`, `io-width`. Important reusable or nested constraints are: composition/conditionals: `allOf`; referenced schemas: `jedec,sdram-props.yaml#`. The highest-risk contract area is SDRAM density, bus width, rank/channel placement, timing child nodes, and JEDEC manufacturer/revision compatible encoding.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this schema and any `$ref` targets, then `dtbs_check` matches real DTS nodes by `compatible`, `$nodename`, or inclusion from a parent schema. Validation checks required properties, array lengths and constants, applies `allOf`, descends into pattern-matched child nodes, and finally enforces `additionalProperties` or `unevaluatedProperties`. Runtime flow starts only after the DTB is loaded: Linux driver core or MFD population uses the compatible and resources to bind drivers.

## State and Persistence Behavior
The YAML file stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: property names, compatible fallback order, address-cell layout, child-node names, and example nodes become contracts shipped in source DTS files and compiled DTBs. Runtime state is owned by the matched kernel drivers after probe, including memory topology metadata consumed by memory-controller bindings and firmware-authored DTBs.

## Dependencies and Integration Points
Maintainers listed: Krzysztof Kozlowski <krzk@kernel.org>. Schema dependencies include `jedec,sdram-props.yaml#`. Integration points include DDR/LPDDR memory description, boot firmware generated memory nodes, memory-controller child nodes, and dt-schema validation of rank/channel geometry. The binding also participates in Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to SDRAM density, bus width, rank/channel placement, timing child nodes, and JEDEC manufacturer/revision compatible encoding, mismatch between documented compatibles and the driver's match table, resource ordering or cell-count mistakes that pass review but break probe, conditional branches that accept one SoC or chip variant while silently rejecting another. This schema closes composed schemas with `unevaluatedProperties: false`. Because these bindings describe hardware contracts, regressions can appear as boot-time probe failures, missing child devices, invalid timing/ECC configuration, or dtbs_check noise across unrelated boards.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/memory-controllers/ddr/jedec,lpddr4.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/memory-controllers/ddr/jedec,lpddr4.yaml` against boards that instantiate the binding. The schema includes 1 embedded example; keep those examples compiling under `dt_binding_check`. Also compare compatible strings with in-tree driver `of_match_table` entries and review DTS examples for register tuple counts, interrupt names, clocks/resets, address ranges, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/ddr/jedec,lpddr4.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/ddr/jedec,lpddr5.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/ddr/jedec,lpddr5.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/ddr/jedec,lpddr5.yaml` defines the JEDEC SDRAM topology or device-property schema titled `LPDDR5 SDRAM compliant to JEDEC JESD209-5`. It constrains devicetree nodes through compatible strings, required resources, bus topology, and shared schema references before the corresponding Linux subsystem uses the node at probe time.

## Important APIs, Types, and Functions
The exported API is the devicetree ABI, not callable functions. `compatible` uses an ordered compatible/fallback `items` sequence with 1 token: `jedec,lpddr5`. Top-level properties are `compatible`, `serial-id`. Required top-level properties are `compatible`, `density`, `io-width`. Important reusable or nested constraints are: composition/conditionals: `allOf`; referenced schemas: `/schemas/types.yaml#/definitions/uint32-array`, `jedec,sdram-props.yaml#`. The highest-risk contract area is SDRAM density, bus width, rank/channel placement, timing child nodes, and JEDEC manufacturer/revision compatible encoding.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this schema and any `$ref` targets, then `dtbs_check` matches real DTS nodes by `compatible`, `$nodename`, or inclusion from a parent schema. Validation checks required properties, array lengths and constants, applies `allOf`, descends into pattern-matched child nodes, and finally enforces `additionalProperties` or `unevaluatedProperties`. Runtime flow starts only after the DTB is loaded: Linux driver core or MFD population uses the compatible and resources to bind drivers.

## State and Persistence Behavior
The YAML file stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: property names, compatible fallback order, address-cell layout, child-node names, and example nodes become contracts shipped in source DTS files and compiled DTBs. Runtime state is owned by the matched kernel drivers after probe, including memory topology metadata consumed by memory-controller bindings and firmware-authored DTBs.

## Dependencies and Integration Points
Maintainers listed: Krzysztof Kozlowski <krzk@kernel.org>. Schema dependencies include `/schemas/types.yaml#/definitions/uint32-array`, `jedec,sdram-props.yaml#`. Integration points include DDR/LPDDR memory description, boot firmware generated memory nodes, memory-controller child nodes, and dt-schema validation of rank/channel geometry. The binding also participates in Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to SDRAM density, bus width, rank/channel placement, timing child nodes, and JEDEC manufacturer/revision compatible encoding, mismatch between documented compatibles and the driver's match table, resource ordering or cell-count mistakes that pass review but break probe, conditional branches that accept one SoC or chip variant while silently rejecting another. This schema closes composed schemas with `unevaluatedProperties: false`. Because these bindings describe hardware contracts, regressions can appear as boot-time probe failures, missing child devices, invalid timing/ECC configuration, or dtbs_check noise across unrelated boards.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/memory-controllers/ddr/jedec,lpddr5.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/memory-controllers/ddr/jedec,lpddr5.yaml` against boards that instantiate the binding. The schema includes 1 embedded example; keep those examples compiling under `dt_binding_check`. Also compare compatible strings with in-tree driver `of_match_table` entries and review DTS examples for register tuple counts, interrupt names, clocks/resets, address ranges, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/ddr/jedec,lpddr5.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/ddr/jedec,sdram-channel.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/ddr/jedec,sdram-channel.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/ddr/jedec,sdram-channel.yaml` defines the JEDEC SDRAM topology or device-property schema titled `SDRAM channel with chip/rank topology description`. A memory channel of SDRAM memory like DDR SDRAM or LPDDR SDRAM is a completely independent set of pins (DQ, CA, CS, CK, etc.) that connect one or more memory chips to a host system. It is a Linux devicetree YAML schema that constrains source DTS/DTB hardware descriptions before the corresponding kernel drivers consume the nodes.

## Important APIs, Types, and Functions
The exported API is the devicetree ABI, not callable functions. `compatible` uses an `enum` of supported tokens with 5 tokens: `jedec,ddr4-channel`, `jedec,lpddr2-channel`, `jedec,lpddr3-channel`, `jedec,lpddr4-channel`, `jedec,lpddr5-channel`. Top-level properties are `$nodename`, `compatible`, `io-width`, `#address-cells`, `#size-cells`. Required top-level properties are `compatible`, `io-width`, `#address-cells`, `#size-cells`. Important reusable or nested constraints are: composition/conditionals: `allOf`; child-node patterns: `^rank@[0-9]+$`; referenced schemas: `/schemas/memory-controllers/ddr/jedec,ddr4.yaml#`, `/schemas/memory-controllers/ddr/jedec,lpddr2.yaml#`, `/schemas/memory-controllers/ddr/jedec,lpddr3.yaml#`, `/schemas/memory-controllers/ddr/jedec,lpddr4.yaml#`, `/schemas/memory-controllers/ddr/jedec,lpddr5.yaml#`; child-node API keys include `reg`; non-compatible enum/const values include `8`, `16`, `32`, `64`, `128`. The highest-risk contract area is SDRAM density, bus width, rank/channel placement, timing child nodes, and JEDEC manufacturer/revision compatible encoding.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this schema and any `$ref` targets, then `dtbs_check` matches real DTS nodes by `compatible`, `$nodename`, or inclusion from a parent schema. Validation checks required properties, array lengths and constants, applies `allOf`, descends into pattern-matched child nodes, and finally enforces `additionalProperties` or `unevaluatedProperties`. Runtime flow starts only after the DTB is loaded: Linux driver core or MFD population uses the compatible and resources to bind drivers.

## State and Persistence Behavior
The YAML file stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: property names, compatible fallback order, address-cell layout, child-node names, and example nodes become contracts shipped in source DTS files and compiled DTBs. Runtime state is owned by the matched kernel drivers after probe, including memory topology metadata consumed by memory-controller bindings and firmware-authored DTBs.

## Dependencies and Integration Points
Maintainers listed: Julius Werner <jwerner@chromium.org>. Schema dependencies include `/schemas/memory-controllers/ddr/jedec,ddr4.yaml#`, `/schemas/memory-controllers/ddr/jedec,lpddr2.yaml#`, `/schemas/memory-controllers/ddr/jedec,lpddr3.yaml#`, `/schemas/memory-controllers/ddr/jedec,lpddr4.yaml#`, `/schemas/memory-controllers/ddr/jedec,lpddr5.yaml#`. Integration points include DDR/LPDDR memory description, boot firmware generated memory nodes, memory-controller child nodes, and dt-schema validation of rank/channel geometry. The binding also participates in Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to SDRAM density, bus width, rank/channel placement, timing child nodes, and JEDEC manufacturer/revision compatible encoding, mismatch between documented compatibles and the driver's match table, resource ordering or cell-count mistakes that pass review but break probe, conditional branches that accept one SoC or chip variant while silently rejecting another, child-node regexes that over-match unrelated children or under-match valid bus devices. This schema rejects unknown top-level properties with `additionalProperties: false`. Because these bindings describe hardware contracts, regressions can appear as boot-time probe failures, missing child devices, invalid timing/ECC configuration, or dtbs_check noise across unrelated boards.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/memory-controllers/ddr/jedec,sdram-channel.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/memory-controllers/ddr/jedec,sdram-channel.yaml` against boards that instantiate the binding. The schema includes 1 embedded example; keep those examples compiling under `dt_binding_check`. Exercise child-node validation for `^rank@[0-9]+$`. Also compare compatible strings with in-tree driver `of_match_table` entries and review DTS examples for register tuple counts, interrupt names, clocks/resets, address ranges, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/ddr/jedec,sdram-channel.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/ddr/jedec,sdram-props.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/ddr/jedec,sdram-props.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/ddr/jedec,sdram-props.yaml` defines the JEDEC SDRAM topology or device-property schema titled `Common properties for SDRAM types`. Different SDRAM types generally use the same properties and only differ in the range of legal values for each. It is a Linux devicetree YAML schema that constrains source DTS/DTB hardware descriptions before the corresponding kernel drivers consume the nodes.

## Important APIs, Types, and Functions
The exported API is the devicetree ABI, not callable functions. `compatible` uses a composed compatible schema with 0 tokens: no local compatible constants. Top-level properties are `compatible`, `reg`, `revision-id`, `density`, `io-width`. Required top-level properties are none declared. Important reusable or nested constraints are: referenced schemas: `/schemas/types.yaml#/definitions/uint32`, `/schemas/types.yaml#/definitions/uint32-array`; non-compatible enum/const values include `64`, `128`, `256`, `512`, `1024`, `2048`, `3072`, `4096`, `6144`, `8192`, and 7 more. The highest-risk contract area is SDRAM density, bus width, rank/channel placement, timing child nodes, and JEDEC manufacturer/revision compatible encoding.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this schema and any `$ref` targets, then `dtbs_check` matches real DTS nodes by `compatible`, `$nodename`, or inclusion from a parent schema. Validation checks required properties, array lengths and constants, applies no top-level conditionals, descends into pattern-matched child nodes, and finally enforces `additionalProperties` or `unevaluatedProperties`. Runtime flow starts only after the DTB is loaded: Linux driver core or MFD population uses the compatible and resources to bind drivers.

## State and Persistence Behavior
The YAML file stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: property names, compatible fallback order, address-cell layout, child-node names, and example nodes become contracts shipped in source DTS files and compiled DTBs. Runtime state is owned by the matched kernel drivers after probe, including memory topology metadata consumed by memory-controller bindings and firmware-authored DTBs.

## Dependencies and Integration Points
Maintainers listed: Krzysztof Kozlowski <krzk@kernel.org>. Schema dependencies include `/schemas/types.yaml#/definitions/uint32`, `/schemas/types.yaml#/definitions/uint32-array`. Integration points include DDR/LPDDR memory description, boot firmware generated memory nodes, memory-controller child nodes, and dt-schema validation of rank/channel geometry. The binding also participates in Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to SDRAM density, bus width, rank/channel placement, timing child nodes, and JEDEC manufacturer/revision compatible encoding, mismatch between documented compatibles and the driver's match table, resource ordering or cell-count mistakes that pass review but break probe, permissive extra properties that can hide spelling errors unless a parent/child schema catches them, lack of embedded examples, leaving coverage dependent on in-tree DTS users. This schema permits additional top-level properties so it can be layered with device-specific child bindings. Because these bindings describe hardware contracts, regressions can appear as boot-time probe failures, missing child devices, invalid timing/ECC configuration, or dtbs_check noise across unrelated boards.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/memory-controllers/ddr/jedec,sdram-props.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/memory-controllers/ddr/jedec,sdram-props.yaml` against boards that instantiate the binding. There are no embedded examples, so representative DTS users and schema-only validation carry the coverage. Also compare compatible strings with in-tree driver `of_match_table` entries and review DTS examples for register tuple counts, interrupt names, clocks/resets, address ranges, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/ddr/jedec,sdram-props.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/exynos-srom.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/exynos-srom.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/exynos-srom.yaml` defines the memory-controller or external-bus binding titled `Samsung Exynos SoC SROM Controller driver`. The SROM controller can be used to attach external peripherals. It is a Linux devicetree YAML schema that constrains source DTS/DTB hardware descriptions before the corresponding kernel drivers consume the nodes.

## Important APIs, Types, and Functions
The exported API is the devicetree ABI, not callable functions. `compatible` uses an ordered compatible/fallback `items` sequence with 1 token: `samsung,exynos4210-srom`. Top-level properties are `compatible`, `reg`, `#address-cells`, `#size-cells`, `ranges`. Required top-level properties are `compatible`, `reg`. Important reusable or nested constraints are: child-node patterns: `^.*@[0-3],[a-f0-9]+$`; referenced schemas: `mc-peripheral-props.yaml#`; child-node API keys include `samsung,srom-timing`, `reg-io-width`; non-compatible enum/const values include `1`, `2`. The highest-risk contract area is compatible fallback ordering, register and interrupt resources, address/size cell layout, bus ranges, child-node regexes, timing properties, clocks, resets, and interconnect/IOMMU links.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this schema and any `$ref` targets, then `dtbs_check` matches real DTS nodes by `compatible`, `$nodename`, or inclusion from a parent schema. Validation checks required properties, array lengths and constants, applies no top-level conditionals, descends into pattern-matched child nodes, and finally enforces `additionalProperties` or `unevaluatedProperties`. Runtime flow starts only after the DTB is loaded: Linux driver core or MFD population uses the compatible and resources to bind drivers.

## State and Persistence Behavior
The YAML file stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: property names, compatible fallback order, address-cell layout, child-node names, and example nodes become contracts shipped in source DTS files and compiled DTBs. Runtime state is owned by the matched kernel drivers after probe, including controller probe state, bus decoding configuration, timing tables, ECC/error reporting, and child-device enumeration.

## Dependencies and Integration Points
Maintainers listed: Krzysztof Kozlowski <krzk@kernel.org>. Schema dependencies include `mc-peripheral-props.yaml#`. Integration points include Linux memory-controller, EDAC, devfreq, interconnect, syscon/regmap, MTD/NAND/NOR, and external-bus child-device probing paths. The binding also participates in Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to compatible fallback ordering, register and interrupt resources, address/size cell layout, bus ranges, child-node regexes, timing properties, clocks, resets, and interconnect/IOMMU links, mismatch between documented compatibles and the driver's match table, resource ordering or cell-count mistakes that pass review but break probe, child-node regexes that over-match unrelated children or under-match valid bus devices. This schema rejects unknown top-level properties with `additionalProperties: false`. Because these bindings describe hardware contracts, regressions can appear as boot-time probe failures, missing child devices, invalid timing/ECC configuration, or dtbs_check noise across unrelated boards.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/memory-controllers/exynos-srom.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/memory-controllers/exynos-srom.yaml` against boards that instantiate the binding. The schema includes 2 embedded examples; keep those examples compiling under `dt_binding_check`. Exercise child-node validation for `^.*@[0-3],[a-f0-9]+$`. Also compare compatible strings with in-tree driver `of_match_table` entries and review DTS examples for register tuple counts, interrupt names, clocks/resets, address ranges, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/exynos-srom.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/fsl/fsl,ddr.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/fsl/fsl,ddr.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/fsl/fsl,ddr.yaml` defines the memory-controller or external-bus binding titled `Freescale DDR memory controller`. It constrains devicetree nodes through compatible strings, required resources, bus topology, and shared schema references before the corresponding Linux subsystem uses the node at probe time.

## Important APIs, Types, and Functions
The exported API is the devicetree ABI, not callable functions. `compatible` uses `oneOf` with 2 branches with 21 tokens: `fsl,qoriq-memory-controller-v4.4`, `fsl,qoriq-memory-controller-v4.5`, `fsl,qoriq-memory-controller-v4.7`, `fsl,qoriq-memory-controller-v5.0`, `fsl,qoriq-memory-controller`, `fsl,bsc9132-memory-controller`, `fsl,mpc8536-memory-controller`, `fsl,mpc8540-memory-controller`, `fsl,mpc8541-memory-controller`, `fsl,mpc8544-memory-controller`, `fsl,mpc8548-memory-controller`, `fsl,mpc8555-memory-controller`, `fsl,mpc8560-memory-controller`, `fsl,mpc8568-memory-controller`, `fsl,mpc8569-memory-controller`, `fsl,mpc8572-memory-controller`, and 5 more. Top-level properties are `$nodename`, `compatible`, `interrupts`, `little-endian`, `reg`, `reg-names`. Required top-level properties are `compatible`, `interrupts`, `reg`. Important reusable or nested constraints are: composition/conditionals: `allOf`. The highest-risk contract area is compatible fallback ordering, register and interrupt resources, address/size cell layout, bus ranges, child-node regexes, timing properties, clocks, resets, and interconnect/IOMMU links.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this schema and any `$ref` targets, then `dtbs_check` matches real DTS nodes by `compatible`, `$nodename`, or inclusion from a parent schema. Validation checks required properties, array lengths and constants, applies `allOf`, descends into pattern-matched child nodes, and finally enforces `additionalProperties` or `unevaluatedProperties`. Runtime flow starts only after the DTB is loaded: Linux driver core or MFD population uses the compatible and resources to bind drivers.

## State and Persistence Behavior
The YAML file stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: property names, compatible fallback order, address-cell layout, child-node names, and example nodes become contracts shipped in source DTS files and compiled DTBs. Runtime state is owned by the matched kernel drivers after probe, including controller probe state, bus decoding configuration, timing tables, ECC/error reporting, and child-device enumeration.

## Dependencies and Integration Points
Maintainers listed: Borislav Petkov <bp@alien8.de>, York Sun <york.sun@nxp.com>. Schema dependencies include dt-schema core/meta schemas only. Integration points include Linux memory-controller, EDAC, devfreq, interconnect, syscon/regmap, MTD/NAND/NOR, and external-bus child-device probing paths. The binding also participates in Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to compatible fallback ordering, register and interrupt resources, address/size cell layout, bus ranges, child-node regexes, timing properties, clocks, resets, and interconnect/IOMMU links, mismatch between documented compatibles and the driver's match table, resource ordering or cell-count mistakes that pass review but break probe, conditional branches that accept one SoC or chip variant while silently rejecting another, large compatible sets where fallback ordering can drift across SoC generations. This schema rejects unknown top-level properties with `additionalProperties: false`. Because these bindings describe hardware contracts, regressions can appear as boot-time probe failures, missing child devices, invalid timing/ECC configuration, or dtbs_check noise across unrelated boards.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/memory-controllers/fsl/fsl,ddr.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/memory-controllers/fsl/fsl,ddr.yaml` against boards that instantiate the binding. The schema includes 2 embedded examples; keep those examples compiling under `dt_binding_check`. Also compare compatible strings with in-tree driver `of_match_table` entries and review DTS examples for register tuple counts, interrupt names, clocks/resets, address ranges, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/fsl/fsl,ddr.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/fsl/fsl,ifc.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/fsl/fsl,ifc.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/fsl/fsl,ifc.yaml` defines the memory-controller or external-bus binding titled `FSL/NXP Integrated Flash Controller`. NXP's integrated flash controller (IFC) is an advanced version of the enhanced local bus controller which includes similar programming and signal interfaces with an extended feature set. It is a Linux devicetree YAML schema that constrains source DTS/DTB hardware descriptions before the corresponding kernel drivers consume the nodes.

## Important APIs, Types, and Functions
The exported API is the devicetree ABI, not callable functions. `compatible` uses a single `const` token with 1 token: `fsl,ifc`. Top-level properties are `$nodename`, `compatible`, `#address-cells`, `#size-cells`, `reg`, `interrupts`, `little-endian`, `ranges`. Required top-level properties are `compatible`, `reg`, `interrupts`. Important reusable or nested constraints are: child-node patterns: `^nand@[a-f0-9]+(,[a-f0-9]+)+$`, `(flash|fpga|board-control|cpld)@[a-f0-9]+(,[a-f0-9]+)+$`; referenced schemas: `/schemas/board/fsl,fpga-qixis.yaml#`, `/schemas/mtd/mtd-physmap.yaml#`, `/schemas/mtd/partitions/partition.yaml#`; child-node API keys include `compatible`, `reg`, `#address-cells`, `#size-cells`; non-compatible enum/const values include `2`, `3`, `1`. The highest-risk contract area is compatible fallback ordering, register and interrupt resources, address/size cell layout, bus ranges, child-node regexes, timing properties, clocks, resets, and interconnect/IOMMU links.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this schema and any `$ref` targets, then `dtbs_check` matches real DTS nodes by `compatible`, `$nodename`, or inclusion from a parent schema. Validation checks required properties, array lengths and constants, applies no top-level conditionals, descends into pattern-matched child nodes, and finally enforces `additionalProperties` or `unevaluatedProperties`. Runtime flow starts only after the DTB is loaded: Linux driver core or MFD population uses the compatible and resources to bind drivers.

## State and Persistence Behavior
The YAML file stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: property names, compatible fallback order, address-cell layout, child-node names, and example nodes become contracts shipped in source DTS files and compiled DTBs. Runtime state is owned by the matched kernel drivers after probe, including controller probe state, bus decoding configuration, timing tables, ECC/error reporting, and child-device enumeration.

## Dependencies and Integration Points
Maintainers listed: Shawn Guo <shawnguo@kernel.org>. Schema dependencies include `/schemas/board/fsl,fpga-qixis.yaml#`, `/schemas/mtd/mtd-physmap.yaml#`, `/schemas/mtd/partitions/partition.yaml#`. Integration points include Linux memory-controller, EDAC, devfreq, interconnect, syscon/regmap, MTD/NAND/NOR, and external-bus child-device probing paths. The binding also participates in Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to compatible fallback ordering, register and interrupt resources, address/size cell layout, bus ranges, child-node regexes, timing properties, clocks, resets, and interconnect/IOMMU links, mismatch between documented compatibles and the driver's match table, resource ordering or cell-count mistakes that pass review but break probe, child-node regexes that over-match unrelated children or under-match valid bus devices. This schema rejects unknown top-level properties with `additionalProperties: false`. Because these bindings describe hardware contracts, regressions can appear as boot-time probe failures, missing child devices, invalid timing/ECC configuration, or dtbs_check noise across unrelated boards.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/memory-controllers/fsl/fsl,ifc.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/memory-controllers/fsl/fsl,ifc.yaml` against boards that instantiate the binding. The schema includes 1 embedded example; keep those examples compiling under `dt_binding_check`. Exercise child-node validation for `^nand@[a-f0-9]+(,[a-f0-9]+)+$`, `(flash|fpga|board-control|cpld)@[a-f0-9]+(,[a-f0-9]+)+$`. Also compare compatible strings with in-tree driver `of_match_table` entries and review DTS examples for register tuple counts, interrupt names, clocks/resets, address ranges, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/fsl/fsl,ifc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/fsl/fsl,imx-weim-peripherals.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/fsl/fsl,imx-weim-peripherals.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/fsl/fsl,imx-weim-peripherals.yaml` defines the memory-controller or external-bus binding titled `i.MX WEIM Bus Peripheral Nodes`. This binding is meant for the child nodes of the WEIM node. It is a Linux devicetree YAML schema that constrains source DTS/DTB hardware descriptions before the corresponding kernel drivers consume the nodes.

## Important APIs, Types, and Functions
The exported API is the devicetree ABI, not callable functions. This is a reusable child/common schema fragment rather than a directly probed node, so its API is the properties it adds to another binding. Top-level properties are `reg`, `fsl,weim-cs-timing`. Required top-level properties are none declared. Important reusable or nested constraints are: referenced schemas: `/schemas/types.yaml#/definitions/uint32-array`. The highest-risk contract area is compatible fallback ordering, register and interrupt resources, address/size cell layout, bus ranges, child-node regexes, timing properties, clocks, resets, and interconnect/IOMMU links.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this schema and any `$ref` targets, then `dtbs_check` matches real DTS nodes by `compatible`, `$nodename`, or inclusion from a parent schema. Validation checks required properties, array lengths and constants, applies no top-level conditionals, descends into pattern-matched child nodes, and finally enforces `additionalProperties` or `unevaluatedProperties`. Runtime flow starts only after the DTB is loaded: Linux driver core or MFD population uses the compatible and resources to bind drivers.

## State and Persistence Behavior
The YAML file stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: property names, compatible fallback order, address-cell layout, child-node names, and example nodes become contracts shipped in source DTS files and compiled DTBs. Runtime state is owned by the matched kernel drivers after probe, including controller probe state, bus decoding configuration, timing tables, ECC/error reporting, and child-device enumeration.

## Dependencies and Integration Points
Maintainers listed: Shawn Guo <shawnguo@kernel.org>, Sascha Hauer <s.hauer@pengutronix.de>. Schema dependencies include `/schemas/types.yaml#/definitions/uint32-array`. Integration points include Linux memory-controller, EDAC, devfreq, interconnect, syscon/regmap, MTD/NAND/NOR, and external-bus child-device probing paths. The binding also participates in Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to compatible fallback ordering, register and interrupt resources, address/size cell layout, bus ranges, child-node regexes, timing properties, clocks, resets, and interconnect/IOMMU links, mismatch between documented compatibles and the driver's match table, resource ordering or cell-count mistakes that pass review but break probe, permissive extra properties that can hide spelling errors unless a parent/child schema catches them, lack of embedded examples, leaving coverage dependent on in-tree DTS users. This schema permits additional top-level properties so it can be layered with device-specific child bindings. Because these bindings describe hardware contracts, regressions can appear as boot-time probe failures, missing child devices, invalid timing/ECC configuration, or dtbs_check noise across unrelated boards.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/memory-controllers/fsl/fsl,imx-weim-peripherals.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/memory-controllers/fsl/fsl,imx-weim-peripherals.yaml` against boards that instantiate the binding. There are no embedded examples, so representative DTS users and schema-only validation carry the coverage. Also compare compatible strings with in-tree driver `of_match_table` entries and review DTS examples for register tuple counts, interrupt names, clocks/resets, address ranges, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/fsl/fsl,imx-weim-peripherals.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/fsl/fsl,imx-weim.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/fsl/fsl,imx-weim.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/fsl/fsl,imx-weim.yaml` defines the memory-controller or external-bus binding titled `i.MX Wireless External Interface Module (WEIM)`. The term "wireless" does not imply that the WEIM is literally an interface without wires. It is a Linux devicetree YAML schema that constrains source DTS/DTB hardware descriptions before the corresponding kernel drivers consume the nodes.

## Important APIs, Types, and Functions
The exported API is the devicetree ABI, not callable functions. `compatible` uses `oneOf` with 3 branches with 9 tokens: `fsl,imx1-weim`, `fsl,imx27-weim`, `fsl,imx50-weim`, `fsl,imx51-weim`, `fsl,imx6q-weim`, `fsl,imx31-weim`, `fsl,imx35-weim`, `fsl,imx6sx-weim`, `fsl,imx6ul-weim`. Top-level properties are `$nodename`, `compatible`, `#address-cells`, `#size-cells`, `reg`, `clocks`, `interrupts`, `ranges`, `fsl,weim-cs-gpr`, `fsl,burst-clk-enable`, `fsl,continuous-burst-clk`. Required top-level properties are `compatible`, `reg`, `clocks`, `#address-cells`, `#size-cells`, `ranges`. Important reusable or nested constraints are: composition/conditionals: `allOf`; child-node patterns: `^.*@[0-7],[0-9a-f]+$`; referenced schemas: `/schemas/types.yaml#/definitions/phandle`, `fsl,imx-weim-peripherals.yaml`; child-node API keys include `fsl,weim-cs-timing`. The highest-risk contract area is compatible fallback ordering, register and interrupt resources, address/size cell layout, bus ranges, child-node regexes, timing properties, clocks, resets, and interconnect/IOMMU links.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this schema and any `$ref` targets, then `dtbs_check` matches real DTS nodes by `compatible`, `$nodename`, or inclusion from a parent schema. Validation checks required properties, array lengths and constants, applies `allOf`, descends into pattern-matched child nodes, and finally enforces `additionalProperties` or `unevaluatedProperties`. Runtime flow starts only after the DTB is loaded: Linux driver core or MFD population uses the compatible and resources to bind drivers.

## State and Persistence Behavior
The YAML file stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: property names, compatible fallback order, address-cell layout, child-node names, and example nodes become contracts shipped in source DTS files and compiled DTBs. Runtime state is owned by the matched kernel drivers after probe, including controller probe state, bus decoding configuration, timing tables, ECC/error reporting, and child-device enumeration.

## Dependencies and Integration Points
Maintainers listed: Shawn Guo <shawnguo@kernel.org>, Sascha Hauer <s.hauer@pengutronix.de>. Schema dependencies include `/schemas/types.yaml#/definitions/phandle`, `fsl,imx-weim-peripherals.yaml`. Integration points include Linux memory-controller, EDAC, devfreq, interconnect, syscon/regmap, MTD/NAND/NOR, and external-bus child-device probing paths. The binding also participates in Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to compatible fallback ordering, register and interrupt resources, address/size cell layout, bus ranges, child-node regexes, timing properties, clocks, resets, and interconnect/IOMMU links, mismatch between documented compatibles and the driver's match table, resource ordering or cell-count mistakes that pass review but break probe, conditional branches that accept one SoC or chip variant while silently rejecting another, child-node regexes that over-match unrelated children or under-match valid bus devices. This schema rejects unknown top-level properties with `additionalProperties: false`. Because these bindings describe hardware contracts, regressions can appear as boot-time probe failures, missing child devices, invalid timing/ECC configuration, or dtbs_check noise across unrelated boards.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/memory-controllers/fsl/fsl,imx-weim.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/memory-controllers/fsl/fsl,imx-weim.yaml` against boards that instantiate the binding. The schema includes 1 embedded example; keep those examples compiling under `dt_binding_check`. Exercise child-node validation for `^.*@[0-7],[0-9a-f]+$`. Also compare compatible strings with in-tree driver `of_match_table` entries and review DTS examples for register tuple counts, interrupt names, clocks/resets, address ranges, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/fsl/fsl,imx-weim.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/fsl/imx8m-ddrc.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/fsl/imx8m-ddrc.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/fsl/imx8m-ddrc.yaml` defines the memory-controller or external-bus binding titled `i.MX8M DDR Controller`. The DDRC block is integrated in i.MX8M for interfacing with DDR based memories. It is a Linux devicetree YAML schema that constrains source DTS/DTB hardware descriptions before the corresponding kernel drivers consume the nodes.

## Important APIs, Types, and Functions
The exported API is the devicetree ABI, not callable functions. `compatible` uses an ordered compatible/fallback `items` sequence with 4 tokens: `fsl,imx8mn-ddrc`, `fsl,imx8mm-ddrc`, `fsl,imx8mq-ddrc`, `fsl,imx8m-ddrc`. Top-level properties are `compatible`, `reg`, `clocks`, `clock-names`, `operating-points-v2`, `opp-table`. Required top-level properties are `reg`, `compatible`, `clocks`, `clock-names`. Important reusable or nested constraints are: no unusually complex local constraints beyond the top-level properties. The highest-risk contract area is compatible fallback ordering, register and interrupt resources, address/size cell layout, bus ranges, child-node regexes, timing properties, clocks, resets, and interconnect/IOMMU links.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this schema and any `$ref` targets, then `dtbs_check` matches real DTS nodes by `compatible`, `$nodename`, or inclusion from a parent schema. Validation checks required properties, array lengths and constants, applies no top-level conditionals, descends into pattern-matched child nodes, and finally enforces `additionalProperties` or `unevaluatedProperties`. Runtime flow starts only after the DTB is loaded: Linux driver core or MFD population uses the compatible and resources to bind drivers.

## State and Persistence Behavior
The YAML file stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: property names, compatible fallback order, address-cell layout, child-node names, and example nodes become contracts shipped in source DTS files and compiled DTBs. Runtime state is owned by the matched kernel drivers after probe, including controller probe state, bus decoding configuration, timing tables, ECC/error reporting, and child-device enumeration.

## Dependencies and Integration Points
Maintainers listed: Peng Fan <peng.fan@nxp.com>. Schema dependencies include dt-schema core/meta schemas only. Integration points include Linux memory-controller, EDAC, devfreq, interconnect, syscon/regmap, MTD/NAND/NOR, and external-bus child-device probing paths. The binding also participates in Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to compatible fallback ordering, register and interrupt resources, address/size cell layout, bus ranges, child-node regexes, timing properties, clocks, resets, and interconnect/IOMMU links, mismatch between documented compatibles and the driver's match table, resource ordering or cell-count mistakes that pass review but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Because these bindings describe hardware contracts, regressions can appear as boot-time probe failures, missing child devices, invalid timing/ECC configuration, or dtbs_check noise across unrelated boards.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/memory-controllers/fsl/imx8m-ddrc.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/memory-controllers/fsl/imx8m-ddrc.yaml` against boards that instantiate the binding. The schema includes 1 embedded example; keep those examples compiling under `dt_binding_check`. Also compare compatible strings with in-tree driver `of_match_table` entries and review DTS examples for register tuple counts, interrupt names, clocks/resets, address ranges, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/fsl/imx8m-ddrc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/fsl/mmdc.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/fsl/mmdc.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/fsl/mmdc.yaml` defines the memory-controller or external-bus binding titled `Freescale Multi Mode DDR controller (MMDC)`. It constrains devicetree nodes through compatible strings, required resources, bus topology, and shared schema references before the corresponding Linux subsystem uses the node at probe time.

## Important APIs, Types, and Functions
The exported API is the devicetree ABI, not callable functions. `compatible` uses `oneOf` with 2 branches with 7 tokens: `fsl,imx6q-mmdc`, `fsl,imx6qp-mmdc`, `fsl,imx6sl-mmdc`, `fsl,imx6sll-mmdc`, `fsl,imx6sx-mmdc`, `fsl,imx6ul-mmdc`, `fsl,imx7ulp-mmdc`. Top-level properties are `compatible`, `reg`, `clocks`. Required top-level properties are `compatible`, `reg`. Important reusable or nested constraints are: no unusually complex local constraints beyond the top-level properties. The highest-risk contract area is compatible fallback ordering, register and interrupt resources, address/size cell layout, bus ranges, child-node regexes, timing properties, clocks, resets, and interconnect/IOMMU links.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this schema and any `$ref` targets, then `dtbs_check` matches real DTS nodes by `compatible`, `$nodename`, or inclusion from a parent schema. Validation checks required properties, array lengths and constants, applies no top-level conditionals, descends into pattern-matched child nodes, and finally enforces `additionalProperties` or `unevaluatedProperties`. Runtime flow starts only after the DTB is loaded: Linux driver core or MFD population uses the compatible and resources to bind drivers.

## State and Persistence Behavior
The YAML file stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: property names, compatible fallback order, address-cell layout, child-node names, and example nodes become contracts shipped in source DTS files and compiled DTBs. Runtime state is owned by the matched kernel drivers after probe, including controller probe state, bus decoding configuration, timing tables, ECC/error reporting, and child-device enumeration.

## Dependencies and Integration Points
Maintainers listed: Shawn Guo <shawnguo@kernel.org>, Sascha Hauer <s.hauer@pengutronix.de>, Fabio Estevam <festevam@gmail.com>. Schema dependencies include dt-schema core/meta schemas only. Integration points include Linux memory-controller, EDAC, devfreq, interconnect, syscon/regmap, MTD/NAND/NOR, and external-bus child-device probing paths. The binding also participates in Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to compatible fallback ordering, register and interrupt resources, address/size cell layout, bus ranges, child-node regexes, timing properties, clocks, resets, and interconnect/IOMMU links, mismatch between documented compatibles and the driver's match table, resource ordering or cell-count mistakes that pass review but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Because these bindings describe hardware contracts, regressions can appear as boot-time probe failures, missing child devices, invalid timing/ECC configuration, or dtbs_check noise across unrelated boards.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/memory-controllers/fsl/mmdc.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/memory-controllers/fsl/mmdc.yaml` against boards that instantiate the binding. The schema includes 1 embedded example; keep those examples compiling under `dt_binding_check`. Also compare compatible strings with in-tree driver `of_match_table` entries and review DTS examples for register tuple counts, interrupt names, clocks/resets, address ranges, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/fsl/mmdc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/ingenic,nemc-peripherals.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/ingenic,nemc-peripherals.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/ingenic,nemc-peripherals.yaml` defines the memory-controller or external-bus binding titled `Ingenic SoCs NAND / External Memory Controller (NEMC)`. It constrains devicetree nodes through compatible strings, required resources, bus topology, and shared schema references before the corresponding Linux subsystem uses the node at probe time.

## Important APIs, Types, and Functions
The exported API is the devicetree ABI, not callable functions. This is a reusable child/common schema fragment rather than a directly probed node, so its API is the properties it adds to another binding. Top-level properties are `reg`, `ingenic,nemc-bus-width`, `ingenic,nemc-tAS`, `ingenic,nemc-tAH`, `ingenic,nemc-tBP`, `ingenic,nemc-tAW`, `ingenic,nemc-tSTRV`. Required top-level properties are `reg`. Important reusable or nested constraints are: referenced schemas: `/schemas/types.yaml#/definitions/uint32`; non-compatible enum/const values include `8`, `16`. The highest-risk contract area is compatible fallback ordering, register and interrupt resources, address/size cell layout, bus ranges, child-node regexes, timing properties, clocks, resets, and interconnect/IOMMU links.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this schema and any `$ref` targets, then `dtbs_check` matches real DTS nodes by `compatible`, `$nodename`, or inclusion from a parent schema. Validation checks required properties, array lengths and constants, applies no top-level conditionals, descends into pattern-matched child nodes, and finally enforces `additionalProperties` or `unevaluatedProperties`. Runtime flow starts only after the DTB is loaded: Linux driver core or MFD population uses the compatible and resources to bind drivers.

## State and Persistence Behavior
The YAML file stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: property names, compatible fallback order, address-cell layout, child-node names, and example nodes become contracts shipped in source DTS files and compiled DTBs. Runtime state is owned by the matched kernel drivers after probe, including controller probe state, bus decoding configuration, timing tables, ECC/error reporting, and child-device enumeration.

## Dependencies and Integration Points
Maintainers listed: Paul Cercueil <paul@crapouillou.net>. Schema dependencies include `/schemas/types.yaml#/definitions/uint32`. Integration points include Linux memory-controller, EDAC, devfreq, interconnect, syscon/regmap, MTD/NAND/NOR, and external-bus child-device probing paths. The binding also participates in Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to compatible fallback ordering, register and interrupt resources, address/size cell layout, bus ranges, child-node regexes, timing properties, clocks, resets, and interconnect/IOMMU links, mismatch between documented compatibles and the driver's match table, resource ordering or cell-count mistakes that pass review but break probe, permissive extra properties that can hide spelling errors unless a parent/child schema catches them, lack of embedded examples, leaving coverage dependent on in-tree DTS users. This schema permits additional top-level properties so it can be layered with device-specific child bindings. Because these bindings describe hardware contracts, regressions can appear as boot-time probe failures, missing child devices, invalid timing/ECC configuration, or dtbs_check noise across unrelated boards.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/memory-controllers/ingenic,nemc-peripherals.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/memory-controllers/ingenic,nemc-peripherals.yaml` against boards that instantiate the binding. There are no embedded examples, so representative DTS users and schema-only validation carry the coverage. Also compare compatible strings with in-tree driver `of_match_table` entries and review DTS examples for register tuple counts, interrupt names, clocks/resets, address ranges, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/ingenic,nemc-peripherals.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/ingenic,nemc.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/ingenic,nemc.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/ingenic,nemc.yaml` defines the memory-controller or external-bus binding titled `Ingenic SoCs NAND / External Memory Controller (NEMC)`. It constrains devicetree nodes through compatible strings, required resources, bus topology, and shared schema references before the corresponding Linux subsystem uses the node at probe time.

## Important APIs, Types, and Functions
The exported API is the devicetree ABI, not callable functions. `compatible` uses `oneOf` with 2 branches with 3 tokens: `ingenic,jz4740-nemc`, `ingenic,jz4780-nemc`, `ingenic,jz4725b-nemc`. Top-level properties are `$nodename`, `compatible`, `#address-cells`, `#size-cells`, `ranges`, `reg`, `clocks`. Required top-level properties are `compatible`, `#address-cells`, `#size-cells`, `ranges`, `reg`, `clocks`. Important reusable or nested constraints are: child-node patterns: `.*@[0-9]+$`; referenced schemas: `mc-peripheral-props.yaml#`. The highest-risk contract area is compatible fallback ordering, register and interrupt resources, address/size cell layout, bus ranges, child-node regexes, timing properties, clocks, resets, and interconnect/IOMMU links.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this schema and any `$ref` targets, then `dtbs_check` matches real DTS nodes by `compatible`, `$nodename`, or inclusion from a parent schema. Validation checks required properties, array lengths and constants, applies no top-level conditionals, descends into pattern-matched child nodes, and finally enforces `additionalProperties` or `unevaluatedProperties`. Runtime flow starts only after the DTB is loaded: Linux driver core or MFD population uses the compatible and resources to bind drivers.

## State and Persistence Behavior
The YAML file stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: property names, compatible fallback order, address-cell layout, child-node names, and example nodes become contracts shipped in source DTS files and compiled DTBs. Runtime state is owned by the matched kernel drivers after probe, including controller probe state, bus decoding configuration, timing tables, ECC/error reporting, and child-device enumeration.

## Dependencies and Integration Points
Maintainers listed: Paul Cercueil <paul@crapouillou.net>. Schema dependencies include `mc-peripheral-props.yaml#`. Integration points include Linux memory-controller, EDAC, devfreq, interconnect, syscon/regmap, MTD/NAND/NOR, and external-bus child-device probing paths. The binding also participates in Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to compatible fallback ordering, register and interrupt resources, address/size cell layout, bus ranges, child-node regexes, timing properties, clocks, resets, and interconnect/IOMMU links, mismatch between documented compatibles and the driver's match table, resource ordering or cell-count mistakes that pass review but break probe, child-node regexes that over-match unrelated children or under-match valid bus devices. This schema rejects unknown top-level properties with `additionalProperties: false`. Because these bindings describe hardware contracts, regressions can appear as boot-time probe failures, missing child devices, invalid timing/ECC configuration, or dtbs_check noise across unrelated boards.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/memory-controllers/ingenic,nemc.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/memory-controllers/ingenic,nemc.yaml` against boards that instantiate the binding. The schema includes 1 embedded example; keep those examples compiling under `dt_binding_check`. Exercise child-node validation for `.*@[0-9]+$`. Also compare compatible strings with in-tree driver `of_match_table` entries and review DTS examples for register tuple counts, interrupt names, clocks/resets, address ranges, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/ingenic,nemc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/intel,ixp4xx-expansion-bus-controller.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/intel,ixp4xx-expansion-bus-controller.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/intel,ixp4xx-expansion-bus-controller.yaml` defines the memory-controller or external-bus binding titled `Intel IXP4xx Expansion Bus Controller`. The IXP4xx expansion bus controller handles access to devices on the memory-mapped expansion bus on the Intel IXP4xx family of system on chips, including IXP42x, IXP43x, IXP45x and IXP46x. It is a Linux devicetree YAML schema that constrains source DTS/DTB hardware descriptions before the corresponding kernel drivers consume the nodes.

## Important APIs, Types, and Functions
The exported API is the devicetree ABI, not callable functions. `compatible` uses an ordered compatible/fallback `items` sequence with 5 tokens: `intel,ixp42x-expansion-bus-controller`, `intel,ixp43x-expansion-bus-controller`, `intel,ixp45x-expansion-bus-controller`, `intel,ixp46x-expansion-bus-controller`, `syscon`. Top-level properties are `$nodename`, `compatible`, `reg`, `native-endian`, `#address-cells`, `#size-cells`, `ranges`, `dma-ranges`. Required top-level properties are `compatible`, `reg`, `native-endian`, `#address-cells`, `#size-cells`, `ranges`, `dma-ranges`. Important reusable or nested constraints are: child-node patterns: `^.*@[0-7],[0-9a-f]+$`; referenced schemas: `/schemas/memory-controllers/intel,ixp4xx-expansion-peripheral-props.yaml#`, `/schemas/types.yaml#/definitions/flag`. The highest-risk contract area is compatible fallback ordering, register and interrupt resources, address/size cell layout, bus ranges, child-node regexes, timing properties, clocks, resets, and interconnect/IOMMU links.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this schema and any `$ref` targets, then `dtbs_check` matches real DTS nodes by `compatible`, `$nodename`, or inclusion from a parent schema. Validation checks required properties, array lengths and constants, applies no top-level conditionals, descends into pattern-matched child nodes, and finally enforces `additionalProperties` or `unevaluatedProperties`. Runtime flow starts only after the DTB is loaded: Linux driver core or MFD population uses the compatible and resources to bind drivers.

## State and Persistence Behavior
The YAML file stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: property names, compatible fallback order, address-cell layout, child-node names, and example nodes become contracts shipped in source DTS files and compiled DTBs. Runtime state is owned by the matched kernel drivers after probe, including controller probe state, bus decoding configuration, timing tables, ECC/error reporting, and child-device enumeration.

## Dependencies and Integration Points
Maintainers listed: Linus Walleij <linusw@kernel.org>. Schema dependencies include `/schemas/memory-controllers/intel,ixp4xx-expansion-peripheral-props.yaml#`, `/schemas/types.yaml#/definitions/flag`. Integration points include Linux memory-controller, EDAC, devfreq, interconnect, syscon/regmap, MTD/NAND/NOR, and external-bus child-device probing paths. The binding also participates in Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to compatible fallback ordering, register and interrupt resources, address/size cell layout, bus ranges, child-node regexes, timing properties, clocks, resets, and interconnect/IOMMU links, mismatch between documented compatibles and the driver's match table, resource ordering or cell-count mistakes that pass review but break probe, child-node regexes that over-match unrelated children or under-match valid bus devices. This schema rejects unknown top-level properties with `additionalProperties: false`. Because these bindings describe hardware contracts, regressions can appear as boot-time probe failures, missing child devices, invalid timing/ECC configuration, or dtbs_check noise across unrelated boards.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/memory-controllers/intel,ixp4xx-expansion-bus-controller.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/memory-controllers/intel,ixp4xx-expansion-bus-controller.yaml` against boards that instantiate the binding. The schema includes 1 embedded example; keep those examples compiling under `dt_binding_check`. Exercise child-node validation for `^.*@[0-7],[0-9a-f]+$`. Also compare compatible strings with in-tree driver `of_match_table` entries and review DTS examples for register tuple counts, interrupt names, clocks/resets, address ranges, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/intel,ixp4xx-expansion-bus-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/intel,ixp4xx-expansion-peripheral-props.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/intel,ixp4xx-expansion-peripheral-props.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/intel,ixp4xx-expansion-peripheral-props.yaml` defines the memory-controller or external-bus binding titled `Peripheral properties for Intel IXP4xx Expansion Bus`. The IXP4xx expansion bus controller handles access to devices on the memory-mapped expansion bus on the Intel IXP4xx family of system on chips, including IXP42x, IXP43x, IXP45x and IXP46x. It is a Linux devicetree YAML schema that constrains source DTS/DTB hardware descriptions before the corresponding kernel drivers consume the nodes.

## Important APIs, Types, and Functions
The exported API is the devicetree ABI, not callable functions. This is a reusable child/common schema fragment rather than a directly probed node, so its API is the properties it adds to another binding. Top-level properties are `intel,ixp4xx-eb-t1`, `intel,ixp4xx-eb-t2`, `intel,ixp4xx-eb-t3`, `intel,ixp4xx-eb-t4`, `intel,ixp4xx-eb-t5`, `intel,ixp4xx-eb-cycle-type`, `intel,ixp4xx-eb-byte-access-on-halfword`, `intel,ixp4xx-eb-hpi-hrdy-pol-high`, `intel,ixp4xx-eb-mux-address-and-data`, `intel,ixp4xx-eb-ahb-split-transfers`, `intel,ixp4xx-eb-write-enable`, `intel,ixp4xx-eb-byte-access`. Required top-level properties are none declared. Important reusable or nested constraints are: referenced schemas: `/schemas/types.yaml#/definitions/uint32`; non-compatible enum/const values include `0`, `1`, `2`. The highest-risk contract area is compatible fallback ordering, register and interrupt resources, address/size cell layout, bus ranges, child-node regexes, timing properties, clocks, resets, and interconnect/IOMMU links.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this schema and any `$ref` targets, then `dtbs_check` matches real DTS nodes by `compatible`, `$nodename`, or inclusion from a parent schema. Validation checks required properties, array lengths and constants, applies no top-level conditionals, descends into pattern-matched child nodes, and finally enforces `additionalProperties` or `unevaluatedProperties`. Runtime flow starts only after the DTB is loaded: Linux driver core or MFD population uses the compatible and resources to bind drivers.

## State and Persistence Behavior
The YAML file stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: property names, compatible fallback order, address-cell layout, child-node names, and example nodes become contracts shipped in source DTS files and compiled DTBs. Runtime state is owned by the matched kernel drivers after probe, including controller probe state, bus decoding configuration, timing tables, ECC/error reporting, and child-device enumeration.

## Dependencies and Integration Points
Maintainers listed: Linus Walleij <linusw@kernel.org>. Schema dependencies include `/schemas/types.yaml#/definitions/uint32`. Integration points include Linux memory-controller, EDAC, devfreq, interconnect, syscon/regmap, MTD/NAND/NOR, and external-bus child-device probing paths. The binding also participates in Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to compatible fallback ordering, register and interrupt resources, address/size cell layout, bus ranges, child-node regexes, timing properties, clocks, resets, and interconnect/IOMMU links, mismatch between documented compatibles and the driver's match table, resource ordering or cell-count mistakes that pass review but break probe, permissive extra properties that can hide spelling errors unless a parent/child schema catches them, lack of embedded examples, leaving coverage dependent on in-tree DTS users. This schema permits additional top-level properties so it can be layered with device-specific child bindings. Because these bindings describe hardware contracts, regressions can appear as boot-time probe failures, missing child devices, invalid timing/ECC configuration, or dtbs_check noise across unrelated boards.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/memory-controllers/intel,ixp4xx-expansion-peripheral-props.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/memory-controllers/intel,ixp4xx-expansion-peripheral-props.yaml` against boards that instantiate the binding. There are no embedded examples, so representative DTS users and schema-only validation carry the coverage. Also compare compatible strings with in-tree driver `of_match_table` entries and review DTS examples for register tuple counts, interrupt names, clocks/resets, address ranges, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/intel,ixp4xx-expansion-peripheral-props.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/marvell,mvebu-sdram-controller.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/marvell,mvebu-sdram-controller.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/marvell,mvebu-sdram-controller.yaml` defines the memory-controller or external-bus binding titled `Marvell MVEBU SDRAM controller`. It constrains devicetree nodes through compatible strings, required resources, bus topology, and shared schema references before the corresponding Linux subsystem uses the node at probe time.

## Important APIs, Types, and Functions
The exported API is the devicetree ABI, not callable functions. `compatible` uses a single `const` token with 1 token: `marvell,armada-xp-sdram-controller`. Top-level properties are `compatible`, `reg`. Required top-level properties are `compatible`, `reg`. Important reusable or nested constraints are: no unusually complex local constraints beyond the top-level properties. The highest-risk contract area is compatible fallback ordering, register and interrupt resources, address/size cell layout, bus ranges, child-node regexes, timing properties, clocks, resets, and interconnect/IOMMU links.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this schema and any `$ref` targets, then `dtbs_check` matches real DTS nodes by `compatible`, `$nodename`, or inclusion from a parent schema. Validation checks required properties, array lengths and constants, applies no top-level conditionals, descends into pattern-matched child nodes, and finally enforces `additionalProperties` or `unevaluatedProperties`. Runtime flow starts only after the DTB is loaded: Linux driver core or MFD population uses the compatible and resources to bind drivers.

## State and Persistence Behavior
The YAML file stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: property names, compatible fallback order, address-cell layout, child-node names, and example nodes become contracts shipped in source DTS files and compiled DTBs. Runtime state is owned by the matched kernel drivers after probe, including controller probe state, bus decoding configuration, timing tables, ECC/error reporting, and child-device enumeration.

## Dependencies and Integration Points
Maintainers listed: Jan Luebbe <jlu@pengutronix.de>, Krzysztof Kozlowski <krzk@kernel.org>. Schema dependencies include dt-schema core/meta schemas only. Integration points include Linux memory-controller, EDAC, devfreq, interconnect, syscon/regmap, MTD/NAND/NOR, and external-bus child-device probing paths. The binding also participates in Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to compatible fallback ordering, register and interrupt resources, address/size cell layout, bus ranges, child-node regexes, timing properties, clocks, resets, and interconnect/IOMMU links, mismatch between documented compatibles and the driver's match table, resource ordering or cell-count mistakes that pass review but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Because these bindings describe hardware contracts, regressions can appear as boot-time probe failures, missing child devices, invalid timing/ECC configuration, or dtbs_check noise across unrelated boards.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/memory-controllers/marvell,mvebu-sdram-controller.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/memory-controllers/marvell,mvebu-sdram-controller.yaml` against boards that instantiate the binding. The schema includes 1 embedded example; keep those examples compiling under `dt_binding_check`. Also compare compatible strings with in-tree driver `of_match_table` entries and review DTS examples for register tuple counts, interrupt names, clocks/resets, address ranges, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/marvell,mvebu-sdram-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/mc-peripheral-props.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/mc-peripheral-props.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/mc-peripheral-props.yaml` defines the memory-controller or external-bus binding titled `Peripheral-specific properties for a Memory Controller bus.`. Many Memory Controllers need to add properties to peripheral devices. It is a Linux devicetree YAML schema that constrains source DTS/DTB hardware descriptions before the corresponding kernel drivers consume the nodes.

## Important APIs, Types, and Functions
The exported API is the devicetree ABI, not callable functions. This is a reusable child/common schema fragment rather than a directly probed node, so its API is the properties it adds to another binding. Top-level properties are `reg`, `bank-width`. Required top-level properties are `reg`. Important reusable or nested constraints are: composition/conditionals: `allOf`; referenced schemas: `/schemas/types.yaml#/definitions/uint32`, `fsl/fsl,imx-weim-peripherals.yaml`, `ingenic,nemc-peripherals.yaml#`, `intel,ixp4xx-expansion-peripheral-props.yaml#`, `qcom,ebi2-peripheral-props.yaml#`, `samsung,exynos4210-srom-peripheral-props.yaml#`, `st,stm32-fmc2-ebi-props.yaml#`, `ti,gpmc-child.yaml#`; non-compatible enum/const values include `1`, `2`, `4`. The highest-risk contract area is compatible fallback ordering, register and interrupt resources, address/size cell layout, bus ranges, child-node regexes, timing properties, clocks, resets, and interconnect/IOMMU links.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this schema and any `$ref` targets, then `dtbs_check` matches real DTS nodes by `compatible`, `$nodename`, or inclusion from a parent schema. Validation checks required properties, array lengths and constants, applies `allOf`, descends into pattern-matched child nodes, and finally enforces `additionalProperties` or `unevaluatedProperties`. Runtime flow starts only after the DTB is loaded: Linux driver core or MFD population uses the compatible and resources to bind drivers.

## State and Persistence Behavior
The YAML file stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: property names, compatible fallback order, address-cell layout, child-node names, and example nodes become contracts shipped in source DTS files and compiled DTBs. Runtime state is owned by the matched kernel drivers after probe, including controller probe state, bus decoding configuration, timing tables, ECC/error reporting, and child-device enumeration.

## Dependencies and Integration Points
Maintainers listed: Marek Vasut <marex@denx.de>. Schema dependencies include `/schemas/types.yaml#/definitions/uint32`, `fsl/fsl,imx-weim-peripherals.yaml`, `ingenic,nemc-peripherals.yaml#`, `intel,ixp4xx-expansion-peripheral-props.yaml#`, `qcom,ebi2-peripheral-props.yaml#`, `samsung,exynos4210-srom-peripheral-props.yaml#`, `st,stm32-fmc2-ebi-props.yaml#`, `ti,gpmc-child.yaml#`. Integration points include Linux memory-controller, EDAC, devfreq, interconnect, syscon/regmap, MTD/NAND/NOR, and external-bus child-device probing paths. The binding also participates in Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to compatible fallback ordering, register and interrupt resources, address/size cell layout, bus ranges, child-node regexes, timing properties, clocks, resets, and interconnect/IOMMU links, mismatch between documented compatibles and the driver's match table, resource ordering or cell-count mistakes that pass review but break probe, conditional branches that accept one SoC or chip variant while silently rejecting another, permissive extra properties that can hide spelling errors unless a parent/child schema catches them, lack of embedded examples, leaving coverage dependent on in-tree DTS users. This schema permits additional top-level properties so it can be layered with device-specific child bindings. Because these bindings describe hardware contracts, regressions can appear as boot-time probe failures, missing child devices, invalid timing/ECC configuration, or dtbs_check noise across unrelated boards.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/memory-controllers/mc-peripheral-props.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/memory-controllers/mc-peripheral-props.yaml` against boards that instantiate the binding. There are no embedded examples, so representative DTS users and schema-only validation carry the coverage. Also compare compatible strings with in-tree driver `of_match_table` entries and review DTS examples for register tuple counts, interrupt names, clocks/resets, address ranges, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/mc-peripheral-props.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/mediatek,mt7621-memc.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/mediatek,mt7621-memc.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/mediatek,mt7621-memc.yaml` defines the memory-controller or external-bus binding titled `MT7621 SDRAM controller`. It constrains devicetree nodes through compatible strings, required resources, bus topology, and shared schema references before the corresponding Linux subsystem uses the node at probe time.

## Important APIs, Types, and Functions
The exported API is the devicetree ABI, not callable functions. `compatible` uses an ordered compatible/fallback `items` sequence with 2 tokens: `mediatek,mt7621-memc`, `syscon`. Top-level properties are `compatible`, `reg`. Required top-level properties are `compatible`, `reg`. Important reusable or nested constraints are: no unusually complex local constraints beyond the top-level properties. The highest-risk contract area is compatible fallback ordering, register and interrupt resources, address/size cell layout, bus ranges, child-node regexes, timing properties, clocks, resets, and interconnect/IOMMU links.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this schema and any `$ref` targets, then `dtbs_check` matches real DTS nodes by `compatible`, `$nodename`, or inclusion from a parent schema. Validation checks required properties, array lengths and constants, applies no top-level conditionals, descends into pattern-matched child nodes, and finally enforces `additionalProperties` or `unevaluatedProperties`. Runtime flow starts only after the DTB is loaded: Linux driver core or MFD population uses the compatible and resources to bind drivers.

## State and Persistence Behavior
The YAML file stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: property names, compatible fallback order, address-cell layout, child-node names, and example nodes become contracts shipped in source DTS files and compiled DTBs. Runtime state is owned by the matched kernel drivers after probe, including controller probe state, bus decoding configuration, timing tables, ECC/error reporting, and child-device enumeration.

## Dependencies and Integration Points
Maintainers listed: Sergio Paracuellos <sergio.paracuellos@gmail.com>. Schema dependencies include dt-schema core/meta schemas only. Integration points include Linux memory-controller, EDAC, devfreq, interconnect, syscon/regmap, MTD/NAND/NOR, and external-bus child-device probing paths. The binding also participates in Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to compatible fallback ordering, register and interrupt resources, address/size cell layout, bus ranges, child-node regexes, timing properties, clocks, resets, and interconnect/IOMMU links, mismatch between documented compatibles and the driver's match table, resource ordering or cell-count mistakes that pass review but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Because these bindings describe hardware contracts, regressions can appear as boot-time probe failures, missing child devices, invalid timing/ECC configuration, or dtbs_check noise across unrelated boards.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/memory-controllers/mediatek,mt7621-memc.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/memory-controllers/mediatek,mt7621-memc.yaml` against boards that instantiate the binding. The schema includes 1 embedded example; keep those examples compiling under `dt_binding_check`. Also compare compatible strings with in-tree driver `of_match_table` entries and review DTS examples for register tuple counts, interrupt names, clocks/resets, address ranges, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/mediatek,mt7621-memc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/mediatek,smi-common.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/mediatek,smi-common.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/mediatek,smi-common.yaml` defines the memory-controller or external-bus binding titled `SMI (Smart Multimedia Interface) Common`. The hardware block diagram please check bindings/iommu/mediatek,iommu.yaml MediaTek SMI have two generations of HW architecture, here is the list which generation the SoCs use: generation 1: mt2701 and mt7623. It is a Linux devicetree YAML schema that constrains source DTS/DTB hardware descriptions before the corresponding kernel drivers consume the nodes.

## Important APIs, Types, and Functions
The exported API is the devicetree ABI, not callable functions. `compatible` uses `oneOf` with 2 branches with 17 tokens: `mediatek,mt2701-smi-common`, `mediatek,mt2712-smi-common`, `mediatek,mt6779-smi-common`, `mediatek,mt6795-smi-common`, `mediatek,mt6893-smi-common`, `mediatek,mt8167-smi-common`, `mediatek,mt8173-smi-common`, `mediatek,mt8183-smi-common`, `mediatek,mt8186-smi-common`, `mediatek,mt8188-smi-common-vdo`, `mediatek,mt8188-smi-common-vpp`, `mediatek,mt8192-smi-common`, `mediatek,mt8195-smi-common-vdo`, `mediatek,mt8195-smi-common-vpp`, `mediatek,mt8195-smi-sub-common`, `mediatek,mt8365-smi-common`, and 1 more. Top-level properties are `compatible`, `reg`, `power-domains`, `clocks`, `clock-names`, `mediatek,smi`. Required top-level properties are `compatible`, `reg`, `power-domains`, `clocks`, `clock-names`. Important reusable or nested constraints are: composition/conditionals: `allOf`; referenced schemas: `/schemas/types.yaml#/definitions/phandle`. The highest-risk contract area is compatible fallback ordering, register and interrupt resources, address/size cell layout, bus ranges, child-node regexes, timing properties, clocks, resets, and interconnect/IOMMU links.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this schema and any `$ref` targets, then `dtbs_check` matches real DTS nodes by `compatible`, `$nodename`, or inclusion from a parent schema. Validation checks required properties, array lengths and constants, applies `allOf`, descends into pattern-matched child nodes, and finally enforces `additionalProperties` or `unevaluatedProperties`. Runtime flow starts only after the DTB is loaded: Linux driver core or MFD population uses the compatible and resources to bind drivers.

## State and Persistence Behavior
The YAML file stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: property names, compatible fallback order, address-cell layout, child-node names, and example nodes become contracts shipped in source DTS files and compiled DTBs. Runtime state is owned by the matched kernel drivers after probe, including controller probe state, bus decoding configuration, timing tables, ECC/error reporting, and child-device enumeration.

## Dependencies and Integration Points
Maintainers listed: Yong Wu <yong.wu@mediatek.com>. Schema dependencies include `/schemas/types.yaml#/definitions/phandle`. Integration points include Linux memory-controller, EDAC, devfreq, interconnect, syscon/regmap, MTD/NAND/NOR, and external-bus child-device probing paths. The binding also participates in Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to compatible fallback ordering, register and interrupt resources, address/size cell layout, bus ranges, child-node regexes, timing properties, clocks, resets, and interconnect/IOMMU links, mismatch between documented compatibles and the driver's match table, resource ordering or cell-count mistakes that pass review but break probe, conditional branches that accept one SoC or chip variant while silently rejecting another, large compatible sets where fallback ordering can drift across SoC generations. This schema rejects unknown top-level properties with `additionalProperties: false`. Because these bindings describe hardware contracts, regressions can appear as boot-time probe failures, missing child devices, invalid timing/ECC configuration, or dtbs_check noise across unrelated boards.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/memory-controllers/mediatek,smi-common.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/memory-controllers/mediatek,smi-common.yaml` against boards that instantiate the binding. The schema includes 1 embedded example; keep those examples compiling under `dt_binding_check`. Also compare compatible strings with in-tree driver `of_match_table` entries and review DTS examples for register tuple counts, interrupt names, clocks/resets, address ranges, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/mediatek,smi-common.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/mediatek,smi-larb.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/mediatek,smi-larb.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/mediatek,smi-larb.yaml` defines the memory-controller or external-bus binding titled `SMI (Smart Multimedia Interface) Local Arbiter`. The hardware block diagram please check bindings/iommu/mediatek,iommu.yaml It is a Linux devicetree YAML schema that constrains source DTS/DTB hardware descriptions before the corresponding kernel drivers consume the nodes.

## Important APIs, Types, and Functions
The exported API is the devicetree ABI, not callable functions. `compatible` uses `oneOf` with 3 branches with 14 tokens: `mediatek,mt2701-smi-larb`, `mediatek,mt2712-smi-larb`, `mediatek,mt6779-smi-larb`, `mediatek,mt6795-smi-larb`, `mediatek,mt6893-smi-larb`, `mediatek,mt8167-smi-larb`, `mediatek,mt8173-smi-larb`, `mediatek,mt8183-smi-larb`, `mediatek,mt8186-smi-larb`, `mediatek,mt8188-smi-larb`, `mediatek,mt8192-smi-larb`, `mediatek,mt8195-smi-larb`, `mediatek,mt7623-smi-larb`, `mediatek,mt8365-smi-larb`. Top-level properties are `compatible`, `reg`, `clocks`, `clock-names`, `power-domains`, `mediatek,smi`, `mediatek,larb-id`. Required top-level properties are `compatible`, `reg`, `clocks`, `clock-names`, `power-domains`. Important reusable or nested constraints are: composition/conditionals: `allOf`; referenced schemas: `/schemas/types.yaml#/definitions/phandle`, `/schemas/types.yaml#/definitions/uint32`. The highest-risk contract area is compatible fallback ordering, register and interrupt resources, address/size cell layout, bus ranges, child-node regexes, timing properties, clocks, resets, and interconnect/IOMMU links.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this schema and any `$ref` targets, then `dtbs_check` matches real DTS nodes by `compatible`, `$nodename`, or inclusion from a parent schema. Validation checks required properties, array lengths and constants, applies `allOf`, descends into pattern-matched child nodes, and finally enforces `additionalProperties` or `unevaluatedProperties`. Runtime flow starts only after the DTB is loaded: Linux driver core or MFD population uses the compatible and resources to bind drivers.

## State and Persistence Behavior
The YAML file stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: property names, compatible fallback order, address-cell layout, child-node names, and example nodes become contracts shipped in source DTS files and compiled DTBs. Runtime state is owned by the matched kernel drivers after probe, including controller probe state, bus decoding configuration, timing tables, ECC/error reporting, and child-device enumeration.

## Dependencies and Integration Points
Maintainers listed: Yong Wu <yong.wu@mediatek.com>. Schema dependencies include `/schemas/types.yaml#/definitions/phandle`, `/schemas/types.yaml#/definitions/uint32`. Integration points include Linux memory-controller, EDAC, devfreq, interconnect, syscon/regmap, MTD/NAND/NOR, and external-bus child-device probing paths. The binding also participates in Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to compatible fallback ordering, register and interrupt resources, address/size cell layout, bus ranges, child-node regexes, timing properties, clocks, resets, and interconnect/IOMMU links, mismatch between documented compatibles and the driver's match table, resource ordering or cell-count mistakes that pass review but break probe, conditional branches that accept one SoC or chip variant while silently rejecting another, large compatible sets where fallback ordering can drift across SoC generations. This schema rejects unknown top-level properties with `additionalProperties: false`. Because these bindings describe hardware contracts, regressions can appear as boot-time probe failures, missing child devices, invalid timing/ECC configuration, or dtbs_check noise across unrelated boards.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/memory-controllers/mediatek,smi-larb.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/memory-controllers/mediatek,smi-larb.yaml` against boards that instantiate the binding. The schema includes 1 embedded example; keep those examples compiling under `dt_binding_check`. Also compare compatible strings with in-tree driver `of_match_table` entries and review DTS examples for register tuple counts, interrupt names, clocks/resets, address ranges, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/mediatek,smi-larb.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/nuvoton,npcm-memory-controller.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/nuvoton,npcm-memory-controller.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/nuvoton,npcm-memory-controller.yaml` defines the memory-controller or external-bus binding titled `Nuvoton NPCM Memory Controller`. The Nuvoton BMC SoC supports DDR4 memory with or without ECC (error correction check). It is a Linux devicetree YAML schema that constrains source DTS/DTB hardware descriptions before the corresponding kernel drivers consume the nodes.

## Important APIs, Types, and Functions
The exported API is the devicetree ABI, not callable functions. `compatible` uses an `enum` of supported tokens with 2 tokens: `nuvoton,npcm750-memory-controller`, `nuvoton,npcm845-memory-controller`. Top-level properties are `compatible`, `reg`, `interrupts`. Required top-level properties are `compatible`, `reg`, `interrupts`. Important reusable or nested constraints are: no unusually complex local constraints beyond the top-level properties. The highest-risk contract area is compatible fallback ordering, register and interrupt resources, address/size cell layout, bus ranges, child-node regexes, timing properties, clocks, resets, and interconnect/IOMMU links.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this schema and any `$ref` targets, then `dtbs_check` matches real DTS nodes by `compatible`, `$nodename`, or inclusion from a parent schema. Validation checks required properties, array lengths and constants, applies no top-level conditionals, descends into pattern-matched child nodes, and finally enforces `additionalProperties` or `unevaluatedProperties`. Runtime flow starts only after the DTB is loaded: Linux driver core or MFD population uses the compatible and resources to bind drivers.

## State and Persistence Behavior
The YAML file stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: property names, compatible fallback order, address-cell layout, child-node names, and example nodes become contracts shipped in source DTS files and compiled DTBs. Runtime state is owned by the matched kernel drivers after probe, including controller probe state, bus decoding configuration, timing tables, ECC/error reporting, and child-device enumeration.

## Dependencies and Integration Points
Maintainers listed: Marvin Lin <kflin@nuvoton.com>, Stanley Chu <yschu@nuvoton.com>. Schema dependencies include dt-schema core/meta schemas only. Integration points include Linux memory-controller, EDAC, devfreq, interconnect, syscon/regmap, MTD/NAND/NOR, and external-bus child-device probing paths. The binding also participates in Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to compatible fallback ordering, register and interrupt resources, address/size cell layout, bus ranges, child-node regexes, timing properties, clocks, resets, and interconnect/IOMMU links, mismatch between documented compatibles and the driver's match table, resource ordering or cell-count mistakes that pass review but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Because these bindings describe hardware contracts, regressions can appear as boot-time probe failures, missing child devices, invalid timing/ECC configuration, or dtbs_check noise across unrelated boards.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/memory-controllers/nuvoton,npcm-memory-controller.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/memory-controllers/nuvoton,npcm-memory-controller.yaml` against boards that instantiate the binding. The schema includes 1 embedded example; keep those examples compiling under `dt_binding_check`. Also compare compatible strings with in-tree driver `of_match_table` entries and review DTS examples for register tuple counts, interrupt names, clocks/resets, address ranges, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/nuvoton,npcm-memory-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/nvidia,tegra124-emc.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/nvidia,tegra124-emc.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/nvidia,tegra124-emc.yaml` defines the memory-controller or external-bus binding titled `NVIDIA Tegra124 SoC External Memory Controller`. The EMC interfaces with the off-chip SDRAM to service the request stream sent from the memory controller. It is a Linux devicetree YAML schema that constrains source DTS/DTB hardware descriptions before the corresponding kernel drivers consume the nodes.

## Important APIs, Types, and Functions
The exported API is the devicetree ABI, not callable functions. `compatible` uses a single `const` token with 1 token: `nvidia,tegra124-emc`. Top-level properties are `compatible`, `reg`, `clocks`, `clock-names`, `#interconnect-cells`, `nvidia,memory-controller`, `power-domains`, `operating-points-v2`. Required top-level properties are `compatible`, `reg`, `clocks`, `clock-names`, `nvidia,memory-controller`, `#interconnect-cells`, `operating-points-v2`. Important reusable or nested constraints are: child-node patterns: `^emc-timings-[0-9]+$`; referenced schemas: `/schemas/types.yaml#/definitions/phandle`, `/schemas/types.yaml#/definitions/uint32`, `/schemas/types.yaml#/definitions/uint32-array`; child-node API keys include `nvidia,ram-code`. The highest-risk contract area is compatible fallback ordering, register and interrupt resources, address/size cell layout, bus ranges, child-node regexes, timing properties, clocks, resets, and interconnect/IOMMU links.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this schema and any `$ref` targets, then `dtbs_check` matches real DTS nodes by `compatible`, `$nodename`, or inclusion from a parent schema. Validation checks required properties, array lengths and constants, applies no top-level conditionals, descends into pattern-matched child nodes, and finally enforces `additionalProperties` or `unevaluatedProperties`. Runtime flow starts only after the DTB is loaded: Linux driver core or MFD population uses the compatible and resources to bind drivers.

## State and Persistence Behavior
The YAML file stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: property names, compatible fallback order, address-cell layout, child-node names, and example nodes become contracts shipped in source DTS files and compiled DTBs. Runtime state is owned by the matched kernel drivers after probe, including controller probe state, bus decoding configuration, timing tables, ECC/error reporting, and child-device enumeration.

## Dependencies and Integration Points
Maintainers listed: Thierry Reding <thierry.reding@gmail.com>, Jon Hunter <jonathanh@nvidia.com>. Schema dependencies include `/schemas/types.yaml#/definitions/phandle`, `/schemas/types.yaml#/definitions/uint32`, `/schemas/types.yaml#/definitions/uint32-array`. Integration points include Linux memory-controller, EDAC, devfreq, interconnect, syscon/regmap, MTD/NAND/NOR, and external-bus child-device probing paths. The binding also participates in Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to compatible fallback ordering, register and interrupt resources, address/size cell layout, bus ranges, child-node regexes, timing properties, clocks, resets, and interconnect/IOMMU links, mismatch between documented compatibles and the driver's match table, resource ordering or cell-count mistakes that pass review but break probe, child-node regexes that over-match unrelated children or under-match valid bus devices. This schema rejects unknown top-level properties with `additionalProperties: false`. Because these bindings describe hardware contracts, regressions can appear as boot-time probe failures, missing child devices, invalid timing/ECC configuration, or dtbs_check noise across unrelated boards.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/memory-controllers/nvidia,tegra124-emc.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/memory-controllers/nvidia,tegra124-emc.yaml` against boards that instantiate the binding. The schema includes 1 embedded example; keep those examples compiling under `dt_binding_check`. Exercise child-node validation for `^emc-timings-[0-9]+$`. Also compare compatible strings with in-tree driver `of_match_table` entries and review DTS examples for register tuple counts, interrupt names, clocks/resets, address ranges, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/nvidia,tegra124-emc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/nvidia,tegra124-mc.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/nvidia,tegra124-mc.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/nvidia,tegra124-mc.yaml` defines the memory-controller or external-bus binding titled `NVIDIA Tegra124 SoC Memory Controller`. Tegra124 SoC features a hybrid 2x32-bit / 1x64-bit memory controller. It is a Linux devicetree YAML schema that constrains source DTS/DTB hardware descriptions before the corresponding kernel drivers consume the nodes.

## Important APIs, Types, and Functions
The exported API is the devicetree ABI, not callable functions. `compatible` uses a single `const` token with 1 token: `nvidia,tegra124-mc`. Top-level properties are `compatible`, `reg`, `clocks`, `clock-names`, `interrupts`, `#reset-cells`, `#iommu-cells`, `#interconnect-cells`. Required top-level properties are `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `#reset-cells`, `#iommu-cells`, `#interconnect-cells`. Important reusable or nested constraints are: child-node patterns: `^emc-timings-[0-9]+$`; referenced schemas: `/schemas/types.yaml#/definitions/uint32`, `/schemas/types.yaml#/definitions/uint32-array`; child-node API keys include `nvidia,ram-code`. The highest-risk contract area is compatible fallback ordering, register and interrupt resources, address/size cell layout, bus ranges, child-node regexes, timing properties, clocks, resets, and interconnect/IOMMU links.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this schema and any `$ref` targets, then `dtbs_check` matches real DTS nodes by `compatible`, `$nodename`, or inclusion from a parent schema. Validation checks required properties, array lengths and constants, applies no top-level conditionals, descends into pattern-matched child nodes, and finally enforces `additionalProperties` or `unevaluatedProperties`. Runtime flow starts only after the DTB is loaded: Linux driver core or MFD population uses the compatible and resources to bind drivers.

## State and Persistence Behavior
The YAML file stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: property names, compatible fallback order, address-cell layout, child-node names, and example nodes become contracts shipped in source DTS files and compiled DTBs. Runtime state is owned by the matched kernel drivers after probe, including controller probe state, bus decoding configuration, timing tables, ECC/error reporting, and child-device enumeration.

## Dependencies and Integration Points
Maintainers listed: Jon Hunter <jonathanh@nvidia.com>, Thierry Reding <thierry.reding@gmail.com>. Schema dependencies include `/schemas/types.yaml#/definitions/uint32`, `/schemas/types.yaml#/definitions/uint32-array`. Integration points include Linux memory-controller, EDAC, devfreq, interconnect, syscon/regmap, MTD/NAND/NOR, and external-bus child-device probing paths. The binding also participates in Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to compatible fallback ordering, register and interrupt resources, address/size cell layout, bus ranges, child-node regexes, timing properties, clocks, resets, and interconnect/IOMMU links, mismatch between documented compatibles and the driver's match table, resource ordering or cell-count mistakes that pass review but break probe, child-node regexes that over-match unrelated children or under-match valid bus devices. This schema rejects unknown top-level properties with `additionalProperties: false`. Because these bindings describe hardware contracts, regressions can appear as boot-time probe failures, missing child devices, invalid timing/ECC configuration, or dtbs_check noise across unrelated boards.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/memory-controllers/nvidia,tegra124-mc.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/memory-controllers/nvidia,tegra124-mc.yaml` against boards that instantiate the binding. The schema includes 1 embedded example; keep those examples compiling under `dt_binding_check`. Exercise child-node validation for `^emc-timings-[0-9]+$`. Also compare compatible strings with in-tree driver `of_match_table` entries and review DTS examples for register tuple counts, interrupt names, clocks/resets, address ranges, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/nvidia,tegra124-mc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/nvidia,tegra186-mc.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/nvidia,tegra186-mc.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/nvidia,tegra186-mc.yaml` defines the memory-controller or external-bus binding titled `NVIDIA Tegra186 (and later) SoC Memory Controller`. The NVIDIA Tegra186 SoC features a 128 bit memory controller that is split into four 32 bit channels to support LPDDR4 with x16 subpartitions. It is a Linux devicetree YAML schema that constrains source DTS/DTB hardware descriptions before the corresponding kernel drivers consume the nodes.

## Important APIs, Types, and Functions
The exported API is the devicetree ABI, not callable functions. `compatible` uses an ordered compatible/fallback `items` sequence with 4 tokens: `nvidia,tegra186-mc`, `nvidia,tegra194-mc`, `nvidia,tegra234-mc`, `nvidia,tegra264-mc`. Top-level properties are `$nodename`, `compatible`, `reg`, `reg-names`, `interrupts`, `interrupt-names`, `#address-cells`, `#size-cells`, `ranges`, `dma-ranges`, `#interconnect-cells`. Required top-level properties are `compatible`, `reg`, `reg-names`, `interrupts`, `#address-cells`, `#size-cells`. Important reusable or nested constraints are: composition/conditionals: `allOf`; child-node patterns: `^external-memory-controller@[0-9a-f]+$`; referenced schemas: `/schemas/types.yaml#/definitions/phandle`; child-node API keys include `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `#interconnect-cells`, `nvidia,bpmp`; non-compatible enum/const values include `nvidia,tegra186-emc`, `nvidia,tegra194-emc`, `nvidia,tegra234-emc`, `nvidia,tegra264-emc`. The highest-risk contract area is compatible fallback ordering, register and interrupt resources, address/size cell layout, bus ranges, child-node regexes, timing properties, clocks, resets, and interconnect/IOMMU links.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this schema and any `$ref` targets, then `dtbs_check` matches real DTS nodes by `compatible`, `$nodename`, or inclusion from a parent schema. Validation checks required properties, array lengths and constants, applies `allOf`, descends into pattern-matched child nodes, and finally enforces `additionalProperties` or `unevaluatedProperties`. Runtime flow starts only after the DTB is loaded: Linux driver core or MFD population uses the compatible and resources to bind drivers.

## State and Persistence Behavior
The YAML file stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: property names, compatible fallback order, address-cell layout, child-node names, and example nodes become contracts shipped in source DTS files and compiled DTBs. Runtime state is owned by the matched kernel drivers after probe, including controller probe state, bus decoding configuration, timing tables, ECC/error reporting, and child-device enumeration.

## Dependencies and Integration Points
Maintainers listed: Jon Hunter <jonathanh@nvidia.com>, Thierry Reding <thierry.reding@gmail.com>. Schema dependencies include `/schemas/types.yaml#/definitions/phandle`. Integration points include Linux memory-controller, EDAC, devfreq, interconnect, syscon/regmap, MTD/NAND/NOR, and external-bus child-device probing paths. The binding also participates in Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to compatible fallback ordering, register and interrupt resources, address/size cell layout, bus ranges, child-node regexes, timing properties, clocks, resets, and interconnect/IOMMU links, mismatch between documented compatibles and the driver's match table, resource ordering or cell-count mistakes that pass review but break probe, conditional branches that accept one SoC or chip variant while silently rejecting another, child-node regexes that over-match unrelated children or under-match valid bus devices. This schema rejects unknown top-level properties with `additionalProperties: false`. Because these bindings describe hardware contracts, regressions can appear as boot-time probe failures, missing child devices, invalid timing/ECC configuration, or dtbs_check noise across unrelated boards.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/memory-controllers/nvidia,tegra186-mc.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/memory-controllers/nvidia,tegra186-mc.yaml` against boards that instantiate the binding. The schema includes 1 embedded example; keep those examples compiling under `dt_binding_check`. Exercise child-node validation for `^external-memory-controller@[0-9a-f]+$`. Also compare compatible strings with in-tree driver `of_match_table` entries and review DTS examples for register tuple counts, interrupt names, clocks/resets, address ranges, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/nvidia,tegra186-mc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/nvidia,tegra20-emc.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/nvidia,tegra20-emc.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/nvidia,tegra20-emc.yaml` defines the memory-controller or external-bus binding titled `NVIDIA Tegra20 SoC External Memory Controller`. The External Memory Controller (EMC) interfaces with the off-chip SDRAM to service the request stream sent from Memory Controller. It is a Linux devicetree YAML schema that constrains source DTS/DTB hardware descriptions before the corresponding kernel drivers consume the nodes.

## Important APIs, Types, and Functions
The exported API is the devicetree ABI, not callable functions. `compatible` uses a single `const` token with 1 token: `nvidia,tegra20-emc`. Top-level properties are `compatible`, `reg`, `clocks`, `interrupts`, `#address-cells`, `#size-cells`, `#interconnect-cells`, `nvidia,memory-controller`, `power-domains`, `operating-points-v2`, `nvidia,use-ram-code`. Required top-level properties are `compatible`, `reg`, `interrupts`, `clocks`, `nvidia,memory-controller`, `#interconnect-cells`, `operating-points-v2`. Important reusable or nested constraints are: child-node patterns: `^emc-table@[0-9]+$`, `^emc-tables@[a-f0-9-]+$`; referenced schemas: `#/$defs/emc-table`, `/schemas/types.yaml#/definitions/phandle`, `/schemas/types.yaml#/definitions/uint32`, `/schemas/types.yaml#/definitions/uint32-array`, `ddr/jedec,lpddr2.yaml#`; child-node API keys include `reg`, `nvidia,ram-code`, `#address-cells`, `#size-cells`, `lpddr2`. The highest-risk contract area is compatible fallback ordering, register and interrupt resources, address/size cell layout, bus ranges, child-node regexes, timing properties, clocks, resets, and interconnect/IOMMU links.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this schema and any `$ref` targets, then `dtbs_check` matches real DTS nodes by `compatible`, `$nodename`, or inclusion from a parent schema. Validation checks required properties, array lengths and constants, applies no top-level conditionals, descends into pattern-matched child nodes, and finally enforces `additionalProperties` or `unevaluatedProperties`. Runtime flow starts only after the DTB is loaded: Linux driver core or MFD population uses the compatible and resources to bind drivers.

## State and Persistence Behavior
The YAML file stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: property names, compatible fallback order, address-cell layout, child-node names, and example nodes become contracts shipped in source DTS files and compiled DTBs. Runtime state is owned by the matched kernel drivers after probe, including controller probe state, bus decoding configuration, timing tables, ECC/error reporting, and child-device enumeration.

## Dependencies and Integration Points
Maintainers listed: Dmitry Osipenko <digetx@gmail.com>, Jon Hunter <jonathanh@nvidia.com>, Thierry Reding <thierry.reding@gmail.com>. Schema dependencies include `#/$defs/emc-table`, `/schemas/types.yaml#/definitions/phandle`, `/schemas/types.yaml#/definitions/uint32`, `/schemas/types.yaml#/definitions/uint32-array`, `ddr/jedec,lpddr2.yaml#`. Integration points include Linux memory-controller, EDAC, devfreq, interconnect, syscon/regmap, MTD/NAND/NOR, and external-bus child-device probing paths. The binding also participates in Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to compatible fallback ordering, register and interrupt resources, address/size cell layout, bus ranges, child-node regexes, timing properties, clocks, resets, and interconnect/IOMMU links, mismatch between documented compatibles and the driver's match table, resource ordering or cell-count mistakes that pass review but break probe, child-node regexes that over-match unrelated children or under-match valid bus devices. This schema rejects unknown top-level properties with `additionalProperties: false`. Because these bindings describe hardware contracts, regressions can appear as boot-time probe failures, missing child devices, invalid timing/ECC configuration, or dtbs_check noise across unrelated boards.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/memory-controllers/nvidia,tegra20-emc.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/memory-controllers/nvidia,tegra20-emc.yaml` against boards that instantiate the binding. The schema includes 1 embedded example; keep those examples compiling under `dt_binding_check`. Exercise child-node validation for `^emc-table@[0-9]+$`, `^emc-tables@[a-f0-9-]+$`. Also compare compatible strings with in-tree driver `of_match_table` entries and review DTS examples for register tuple counts, interrupt names, clocks/resets, address ranges, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/nvidia,tegra20-emc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/nvidia,tegra20-mc.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/nvidia,tegra20-mc.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/nvidia,tegra20-mc.yaml` defines the memory-controller or external-bus binding titled `NVIDIA Tegra20 SoC Memory Controller`. The Tegra20 Memory Controller merges request streams from various client interfaces into request stream(s) for the various memory target devices, and returns response data to the various clients. It is a Linux devicetree YAML schema that constrains source DTS/DTB hardware descriptions before the corresponding kernel drivers consume the nodes.

## Important APIs, Types, and Functions
The exported API is the devicetree ABI, not callable functions. `compatible` uses a single `const` token with 1 token: `nvidia,tegra20-mc-gart`. Top-level properties are `compatible`, `reg`, `clocks`, `clock-names`, `interrupts`, `#reset-cells`, `#iommu-cells`, `#interconnect-cells`. Required top-level properties are `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `#reset-cells`, `#iommu-cells`, `#interconnect-cells`. Important reusable or nested constraints are: no unusually complex local constraints beyond the top-level properties. The highest-risk contract area is compatible fallback ordering, register and interrupt resources, address/size cell layout, bus ranges, child-node regexes, timing properties, clocks, resets, and interconnect/IOMMU links.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this schema and any `$ref` targets, then `dtbs_check` matches real DTS nodes by `compatible`, `$nodename`, or inclusion from a parent schema. Validation checks required properties, array lengths and constants, applies no top-level conditionals, descends into pattern-matched child nodes, and finally enforces `additionalProperties` or `unevaluatedProperties`. Runtime flow starts only after the DTB is loaded: Linux driver core or MFD population uses the compatible and resources to bind drivers.

## State and Persistence Behavior
The YAML file stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: property names, compatible fallback order, address-cell layout, child-node names, and example nodes become contracts shipped in source DTS files and compiled DTBs. Runtime state is owned by the matched kernel drivers after probe, including controller probe state, bus decoding configuration, timing tables, ECC/error reporting, and child-device enumeration.

## Dependencies and Integration Points
Maintainers listed: Dmitry Osipenko <digetx@gmail.com>, Jon Hunter <jonathanh@nvidia.com>, Thierry Reding <thierry.reding@gmail.com>. Schema dependencies include dt-schema core/meta schemas only. Integration points include Linux memory-controller, EDAC, devfreq, interconnect, syscon/regmap, MTD/NAND/NOR, and external-bus child-device probing paths. The binding also participates in Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to compatible fallback ordering, register and interrupt resources, address/size cell layout, bus ranges, child-node regexes, timing properties, clocks, resets, and interconnect/IOMMU links, mismatch between documented compatibles and the driver's match table, resource ordering or cell-count mistakes that pass review but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Because these bindings describe hardware contracts, regressions can appear as boot-time probe failures, missing child devices, invalid timing/ECC configuration, or dtbs_check noise across unrelated boards.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/memory-controllers/nvidia,tegra20-mc.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/memory-controllers/nvidia,tegra20-mc.yaml` against boards that instantiate the binding. The schema includes 1 embedded example; keep those examples compiling under `dt_binding_check`. Also compare compatible strings with in-tree driver `of_match_table` entries and review DTS examples for register tuple counts, interrupt names, clocks/resets, address ranges, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/nvidia,tegra20-mc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/nvidia,tegra210-emc.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/nvidia,tegra210-emc.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/nvidia,tegra210-emc.yaml` defines the memory-controller or external-bus binding titled `NVIDIA Tegra210 SoC External Memory Controller`. The EMC interfaces with the off-chip SDRAM to service the request stream sent from the memory controller. It is a Linux devicetree YAML schema that constrains source DTS/DTB hardware descriptions before the corresponding kernel drivers consume the nodes.

## Important APIs, Types, and Functions
The exported API is the devicetree ABI, not callable functions. `compatible` uses a single `const` token with 1 token: `nvidia,tegra210-emc`. Top-level properties are `compatible`, `reg`, `clocks`, `clock-names`, `interrupts`, `#interconnect-cells`, `memory-region`, `nvidia,memory-controller`, `operating-points-v2`. Required top-level properties are `compatible`, `reg`, `clocks`, `clock-names`, `nvidia,memory-controller`. Important reusable or nested constraints are: composition/conditionals: `allOf`; referenced schemas: `/schemas/thermal/thermal-cooling-devices.yaml`, `/schemas/types.yaml#/definitions/phandle`. The highest-risk contract area is compatible fallback ordering, register and interrupt resources, address/size cell layout, bus ranges, child-node regexes, timing properties, clocks, resets, and interconnect/IOMMU links.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this schema and any `$ref` targets, then `dtbs_check` matches real DTS nodes by `compatible`, `$nodename`, or inclusion from a parent schema. Validation checks required properties, array lengths and constants, applies `allOf`, descends into pattern-matched child nodes, and finally enforces `additionalProperties` or `unevaluatedProperties`. Runtime flow starts only after the DTB is loaded: Linux driver core or MFD population uses the compatible and resources to bind drivers.

## State and Persistence Behavior
The YAML file stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: property names, compatible fallback order, address-cell layout, child-node names, and example nodes become contracts shipped in source DTS files and compiled DTBs. Runtime state is owned by the matched kernel drivers after probe, including controller probe state, bus decoding configuration, timing tables, ECC/error reporting, and child-device enumeration.

## Dependencies and Integration Points
Maintainers listed: Thierry Reding <thierry.reding@gmail.com>, Jon Hunter <jonathanh@nvidia.com>. Schema dependencies include `/schemas/thermal/thermal-cooling-devices.yaml`, `/schemas/types.yaml#/definitions/phandle`. Integration points include Linux memory-controller, EDAC, devfreq, interconnect, syscon/regmap, MTD/NAND/NOR, and external-bus child-device probing paths. The binding also participates in Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to compatible fallback ordering, register and interrupt resources, address/size cell layout, bus ranges, child-node regexes, timing properties, clocks, resets, and interconnect/IOMMU links, mismatch between documented compatibles and the driver's match table, resource ordering or cell-count mistakes that pass review but break probe, conditional branches that accept one SoC or chip variant while silently rejecting another. This schema closes composed schemas with `unevaluatedProperties: false`. Because these bindings describe hardware contracts, regressions can appear as boot-time probe failures, missing child devices, invalid timing/ECC configuration, or dtbs_check noise across unrelated boards.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/memory-controllers/nvidia,tegra210-emc.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/memory-controllers/nvidia,tegra210-emc.yaml` against boards that instantiate the binding. The schema includes 1 embedded example; keep those examples compiling under `dt_binding_check`. Also compare compatible strings with in-tree driver `of_match_table` entries and review DTS examples for register tuple counts, interrupt names, clocks/resets, address ranges, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/nvidia,tegra210-emc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/nvidia,tegra210-mc.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/nvidia,tegra210-mc.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/nvidia,tegra210-mc.yaml` defines the memory-controller or external-bus binding titled `NVIDIA Tegra210 SoC Memory Controller`. The NVIDIA Tegra210 SoC features a 64 bit memory controller that is split into two 32 bit channels to support LPDDR3 and LPDDR4 with x16 subpartitions. It is a Linux devicetree YAML schema that constrains source DTS/DTB hardware descriptions before the corresponding kernel drivers consume the nodes.

## Important APIs, Types, and Functions
The exported API is the devicetree ABI, not callable functions. `compatible` uses an ordered compatible/fallback `items` sequence with 1 token: `nvidia,tegra210-mc`. Top-level properties are `$nodename`, `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `#iommu-cells`, `#reset-cells`. Required top-level properties are `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `#iommu-cells`, `#reset-cells`. Important reusable or nested constraints are: no unusually complex local constraints beyond the top-level properties. The highest-risk contract area is compatible fallback ordering, register and interrupt resources, address/size cell layout, bus ranges, child-node regexes, timing properties, clocks, resets, and interconnect/IOMMU links.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this schema and any `$ref` targets, then `dtbs_check` matches real DTS nodes by `compatible`, `$nodename`, or inclusion from a parent schema. Validation checks required properties, array lengths and constants, applies no top-level conditionals, descends into pattern-matched child nodes, and finally enforces `additionalProperties` or `unevaluatedProperties`. Runtime flow starts only after the DTB is loaded: Linux driver core or MFD population uses the compatible and resources to bind drivers.

## State and Persistence Behavior
The YAML file stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: property names, compatible fallback order, address-cell layout, child-node names, and example nodes become contracts shipped in source DTS files and compiled DTBs. Runtime state is owned by the matched kernel drivers after probe, including controller probe state, bus decoding configuration, timing tables, ECC/error reporting, and child-device enumeration.

## Dependencies and Integration Points
Maintainers listed: Thierry Reding <thierry.reding@gmail.com>, Jon Hunter <jonathanh@nvidia.com>. Schema dependencies include dt-schema core/meta schemas only. Integration points include Linux memory-controller, EDAC, devfreq, interconnect, syscon/regmap, MTD/NAND/NOR, and external-bus child-device probing paths. The binding also participates in Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to compatible fallback ordering, register and interrupt resources, address/size cell layout, bus ranges, child-node regexes, timing properties, clocks, resets, and interconnect/IOMMU links, mismatch between documented compatibles and the driver's match table, resource ordering or cell-count mistakes that pass review but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Because these bindings describe hardware contracts, regressions can appear as boot-time probe failures, missing child devices, invalid timing/ECC configuration, or dtbs_check noise across unrelated boards.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/memory-controllers/nvidia,tegra210-mc.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/memory-controllers/nvidia,tegra210-mc.yaml` against boards that instantiate the binding. The schema includes 1 embedded example; keep those examples compiling under `dt_binding_check`. Also compare compatible strings with in-tree driver `of_match_table` entries and review DTS examples for register tuple counts, interrupt names, clocks/resets, address ranges, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/nvidia,tegra210-mc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/nvidia,tegra30-emc.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/nvidia,tegra30-emc.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/nvidia,tegra30-emc.yaml` defines the memory-controller or external-bus binding titled `NVIDIA Tegra30 SoC External Memory Controller`. The EMC interfaces with the off-chip SDRAM to service the request stream sent from Memory Controller. It is a Linux devicetree YAML schema that constrains source DTS/DTB hardware descriptions before the corresponding kernel drivers consume the nodes.

## Important APIs, Types, and Functions
The exported API is the devicetree ABI, not callable functions. `compatible` uses a single `const` token with 1 token: `nvidia,tegra30-emc`. Top-level properties are `compatible`, `reg`, `clocks`, `interrupts`, `#interconnect-cells`, `nvidia,memory-controller`, `power-domains`, `operating-points-v2`. Required top-level properties are `compatible`, `reg`, `interrupts`, `clocks`, `nvidia,memory-controller`, `#interconnect-cells`, `operating-points-v2`. Important reusable or nested constraints are: child-node patterns: `^emc-timings-[0-9]+$`; referenced schemas: `/schemas/types.yaml#/definitions/phandle`, `/schemas/types.yaml#/definitions/uint32`, `/schemas/types.yaml#/definitions/uint32-array`; child-node API keys include `nvidia,ram-code`. The highest-risk contract area is compatible fallback ordering, register and interrupt resources, address/size cell layout, bus ranges, child-node regexes, timing properties, clocks, resets, and interconnect/IOMMU links.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this schema and any `$ref` targets, then `dtbs_check` matches real DTS nodes by `compatible`, `$nodename`, or inclusion from a parent schema. Validation checks required properties, array lengths and constants, applies no top-level conditionals, descends into pattern-matched child nodes, and finally enforces `additionalProperties` or `unevaluatedProperties`. Runtime flow starts only after the DTB is loaded: Linux driver core or MFD population uses the compatible and resources to bind drivers.

## State and Persistence Behavior
The YAML file stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: property names, compatible fallback order, address-cell layout, child-node names, and example nodes become contracts shipped in source DTS files and compiled DTBs. Runtime state is owned by the matched kernel drivers after probe, including controller probe state, bus decoding configuration, timing tables, ECC/error reporting, and child-device enumeration.

## Dependencies and Integration Points
Maintainers listed: Dmitry Osipenko <digetx@gmail.com>, Jon Hunter <jonathanh@nvidia.com>, Thierry Reding <thierry.reding@gmail.com>. Schema dependencies include `/schemas/types.yaml#/definitions/phandle`, `/schemas/types.yaml#/definitions/uint32`, `/schemas/types.yaml#/definitions/uint32-array`. Integration points include Linux memory-controller, EDAC, devfreq, interconnect, syscon/regmap, MTD/NAND/NOR, and external-bus child-device probing paths. The binding also participates in Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to compatible fallback ordering, register and interrupt resources, address/size cell layout, bus ranges, child-node regexes, timing properties, clocks, resets, and interconnect/IOMMU links, mismatch between documented compatibles and the driver's match table, resource ordering or cell-count mistakes that pass review but break probe, child-node regexes that over-match unrelated children or under-match valid bus devices. This schema rejects unknown top-level properties with `additionalProperties: false`. Because these bindings describe hardware contracts, regressions can appear as boot-time probe failures, missing child devices, invalid timing/ECC configuration, or dtbs_check noise across unrelated boards.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/memory-controllers/nvidia,tegra30-emc.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/memory-controllers/nvidia,tegra30-emc.yaml` against boards that instantiate the binding. The schema includes 1 embedded example; keep those examples compiling under `dt_binding_check`. Exercise child-node validation for `^emc-timings-[0-9]+$`. Also compare compatible strings with in-tree driver `of_match_table` entries and review DTS examples for register tuple counts, interrupt names, clocks/resets, address ranges, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/nvidia,tegra30-emc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/nvidia,tegra30-mc.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/nvidia,tegra30-mc.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/nvidia,tegra30-mc.yaml` defines the memory-controller or external-bus binding titled `NVIDIA Tegra30 SoC Memory Controller`. Tegra30 Memory Controller architecturally consists of the following parts: Arbitration Domains, which can handle a single request or response per clock from a group of clients. It is a Linux devicetree YAML schema that constrains source DTS/DTB hardware descriptions before the corresponding kernel drivers consume the nodes.

## Important APIs, Types, and Functions
The exported API is the devicetree ABI, not callable functions. `compatible` uses a single `const` token with 1 token: `nvidia,tegra30-mc`. Top-level properties are `compatible`, `reg`, `clocks`, `clock-names`, `interrupts`, `#reset-cells`, `#iommu-cells`, `#interconnect-cells`. Required top-level properties are `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `#reset-cells`, `#iommu-cells`, `#interconnect-cells`. Important reusable or nested constraints are: child-node patterns: `^emc-timings-[0-9]+$`; referenced schemas: `/schemas/types.yaml#/definitions/uint32`, `/schemas/types.yaml#/definitions/uint32-array`; child-node API keys include `nvidia,ram-code`. The highest-risk contract area is compatible fallback ordering, register and interrupt resources, address/size cell layout, bus ranges, child-node regexes, timing properties, clocks, resets, and interconnect/IOMMU links.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this schema and any `$ref` targets, then `dtbs_check` matches real DTS nodes by `compatible`, `$nodename`, or inclusion from a parent schema. Validation checks required properties, array lengths and constants, applies no top-level conditionals, descends into pattern-matched child nodes, and finally enforces `additionalProperties` or `unevaluatedProperties`. Runtime flow starts only after the DTB is loaded: Linux driver core or MFD population uses the compatible and resources to bind drivers.

## State and Persistence Behavior
The YAML file stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: property names, compatible fallback order, address-cell layout, child-node names, and example nodes become contracts shipped in source DTS files and compiled DTBs. Runtime state is owned by the matched kernel drivers after probe, including controller probe state, bus decoding configuration, timing tables, ECC/error reporting, and child-device enumeration.

## Dependencies and Integration Points
Maintainers listed: Dmitry Osipenko <digetx@gmail.com>, Jon Hunter <jonathanh@nvidia.com>, Thierry Reding <thierry.reding@gmail.com>. Schema dependencies include `/schemas/types.yaml#/definitions/uint32`, `/schemas/types.yaml#/definitions/uint32-array`. Integration points include Linux memory-controller, EDAC, devfreq, interconnect, syscon/regmap, MTD/NAND/NOR, and external-bus child-device probing paths. The binding also participates in Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to compatible fallback ordering, register and interrupt resources, address/size cell layout, bus ranges, child-node regexes, timing properties, clocks, resets, and interconnect/IOMMU links, mismatch between documented compatibles and the driver's match table, resource ordering or cell-count mistakes that pass review but break probe, child-node regexes that over-match unrelated children or under-match valid bus devices. This schema rejects unknown top-level properties with `additionalProperties: false`. Because these bindings describe hardware contracts, regressions can appear as boot-time probe failures, missing child devices, invalid timing/ECC configuration, or dtbs_check noise across unrelated boards.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/memory-controllers/nvidia,tegra30-mc.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/memory-controllers/nvidia,tegra30-mc.yaml` against boards that instantiate the binding. The schema includes 1 embedded example; keep those examples compiling under `dt_binding_check`. Exercise child-node validation for `^emc-timings-[0-9]+$`. Also compare compatible strings with in-tree driver `of_match_table` entries and review DTS examples for register tuple counts, interrupt names, clocks/resets, address ranges, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/nvidia,tegra30-mc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/qca,ath79-ddr-controller.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/qca,ath79-ddr-controller.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/qca,ath79-ddr-controller.yaml` defines the memory-controller or external-bus binding titled `Qualcomm Atheros AR7xxx/AR9xxx DDR controller`. The DDR controller of the AR7xxx and AR9xxx families provides an interface to flush the FIFO between various devices and the DDR. It is a Linux devicetree YAML schema that constrains source DTS/DTB hardware descriptions before the corresponding kernel drivers consume the nodes.

## Important APIs, Types, and Functions
The exported API is the devicetree ABI, not callable functions. `compatible` uses `oneOf` with 2 branches with 3 tokens: `qca,ar9132-ddr-controller`, `qca,ar7240-ddr-controller`, `qca,ar7100-ddr-controller`. Top-level properties are `compatible`, `#qca,ddr-wb-channel-cells`, `reg`. Required top-level properties are `compatible`, `#qca,ddr-wb-channel-cells`, `reg`. Important reusable or nested constraints are: referenced schemas: `/schemas/types.yaml#/definitions/uint32`. The highest-risk contract area is compatible fallback ordering, register and interrupt resources, address/size cell layout, bus ranges, child-node regexes, timing properties, clocks, resets, and interconnect/IOMMU links.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this schema and any `$ref` targets, then `dtbs_check` matches real DTS nodes by `compatible`, `$nodename`, or inclusion from a parent schema. Validation checks required properties, array lengths and constants, applies no top-level conditionals, descends into pattern-matched child nodes, and finally enforces `additionalProperties` or `unevaluatedProperties`. Runtime flow starts only after the DTB is loaded: Linux driver core or MFD population uses the compatible and resources to bind drivers.

## State and Persistence Behavior
The YAML file stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: property names, compatible fallback order, address-cell layout, child-node names, and example nodes become contracts shipped in source DTS files and compiled DTBs. Runtime state is owned by the matched kernel drivers after probe, including controller probe state, bus decoding configuration, timing tables, ECC/error reporting, and child-device enumeration.

## Dependencies and Integration Points
Maintainers listed: Krzysztof Kozlowski <krzk@kernel.org>. Schema dependencies include `/schemas/types.yaml#/definitions/uint32`. Integration points include Linux memory-controller, EDAC, devfreq, interconnect, syscon/regmap, MTD/NAND/NOR, and external-bus child-device probing paths. The binding also participates in Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to compatible fallback ordering, register and interrupt resources, address/size cell layout, bus ranges, child-node regexes, timing properties, clocks, resets, and interconnect/IOMMU links, mismatch between documented compatibles and the driver's match table, resource ordering or cell-count mistakes that pass review but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Because these bindings describe hardware contracts, regressions can appear as boot-time probe failures, missing child devices, invalid timing/ECC configuration, or dtbs_check noise across unrelated boards.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/memory-controllers/qca,ath79-ddr-controller.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/memory-controllers/qca,ath79-ddr-controller.yaml` against boards that instantiate the binding. The schema includes 1 embedded example; keep those examples compiling under `dt_binding_check`. Also compare compatible strings with in-tree driver `of_match_table` entries and review DTS examples for register tuple counts, interrupt names, clocks/resets, address ranges, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/qca,ath79-ddr-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/qcom,ebi2-peripheral-props.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/qcom,ebi2-peripheral-props.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/qcom,ebi2-peripheral-props.yaml` defines the memory-controller or external-bus binding titled `Peripheral Properties for Qualcomm External Bus Interface 2 (EBI2)`. It constrains devicetree nodes through compatible strings, required resources, bus topology, and shared schema references before the corresponding Linux subsystem uses the node at probe time.

## Important APIs, Types, and Functions
The exported API is the devicetree ABI, not callable functions. This is a reusable child/common schema fragment rather than a directly probed node, so its API is the properties it adds to another binding. Top-level properties are `qcom,xmem-recovery-cycles`, `qcom,xmem-write-hold-cycles`, `qcom,xmem-write-delta-cycles`, `qcom,xmem-read-delta-cycles`, `qcom,xmem-write-wait-cycles`, `qcom,xmem-read-wait-cycles`, `qcom,xmem-address-hold-enable`, `qcom,xmem-adv-to-oe-recovery-cycles`, `qcom,xmem-read-hold-cycles`. Required top-level properties are none declared. Important reusable or nested constraints are: referenced schemas: `/schemas/types.yaml#/definitions/uint32`; non-compatible enum/const values include `0`, `1`. The highest-risk contract area is compatible fallback ordering, register and interrupt resources, address/size cell layout, bus ranges, child-node regexes, timing properties, clocks, resets, and interconnect/IOMMU links.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this schema and any `$ref` targets, then `dtbs_check` matches real DTS nodes by `compatible`, `$nodename`, or inclusion from a parent schema. Validation checks required properties, array lengths and constants, applies no top-level conditionals, descends into pattern-matched child nodes, and finally enforces `additionalProperties` or `unevaluatedProperties`. Runtime flow starts only after the DTB is loaded: Linux driver core or MFD population uses the compatible and resources to bind drivers.

## State and Persistence Behavior
The YAML file stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: property names, compatible fallback order, address-cell layout, child-node names, and example nodes become contracts shipped in source DTS files and compiled DTBs. Runtime state is owned by the matched kernel drivers after probe, including controller probe state, bus decoding configuration, timing tables, ECC/error reporting, and child-device enumeration.

## Dependencies and Integration Points
Maintainers listed: Bjorn Andersson <andersson@kernel.org>. Schema dependencies include `/schemas/types.yaml#/definitions/uint32`. Integration points include Linux memory-controller, EDAC, devfreq, interconnect, syscon/regmap, MTD/NAND/NOR, and external-bus child-device probing paths. The binding also participates in Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to compatible fallback ordering, register and interrupt resources, address/size cell layout, bus ranges, child-node regexes, timing properties, clocks, resets, and interconnect/IOMMU links, mismatch between documented compatibles and the driver's match table, resource ordering or cell-count mistakes that pass review but break probe, permissive extra properties that can hide spelling errors unless a parent/child schema catches them, lack of embedded examples, leaving coverage dependent on in-tree DTS users. This schema permits additional top-level properties so it can be layered with device-specific child bindings. Because these bindings describe hardware contracts, regressions can appear as boot-time probe failures, missing child devices, invalid timing/ECC configuration, or dtbs_check noise across unrelated boards.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/memory-controllers/qcom,ebi2-peripheral-props.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/memory-controllers/qcom,ebi2-peripheral-props.yaml` against boards that instantiate the binding. There are no embedded examples, so representative DTS users and schema-only validation carry the coverage. Also compare compatible strings with in-tree driver `of_match_table` entries and review DTS examples for register tuple counts, interrupt names, clocks/resets, address ranges, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/qcom,ebi2-peripheral-props.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/qcom,ebi2.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/qcom,ebi2.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/qcom,ebi2.yaml` defines the memory-controller or external-bus binding titled `Qualcomm External Bus Interface 2 (EBI2)`. The EBI2 contains two peripheral blocks: XMEM and LCDC. It is a Linux devicetree YAML schema that constrains source DTS/DTB hardware descriptions before the corresponding kernel drivers consume the nodes.

## Important APIs, Types, and Functions
The exported API is the devicetree ABI, not callable functions. `compatible` uses an `enum` of supported tokens with 2 tokens: `qcom,apq8060-ebi2`, `qcom,msm8660-ebi2`. Top-level properties are `compatible`, `reg`, `reg-names`, `ranges`, `clocks`, `clock-names`, `#address-cells`, `#size-cells`. Required top-level properties are `compatible`, `reg`, `reg-names`, `ranges`, `clocks`, `clock-names`, `#address-cells`, `#size-cells`. Important reusable or nested constraints are: child-node patterns: `^.*@[0-5],[0-9a-f]+$`; referenced schemas: `mc-peripheral-props.yaml#`. The highest-risk contract area is compatible fallback ordering, register and interrupt resources, address/size cell layout, bus ranges, child-node regexes, timing properties, clocks, resets, and interconnect/IOMMU links.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this schema and any `$ref` targets, then `dtbs_check` matches real DTS nodes by `compatible`, `$nodename`, or inclusion from a parent schema. Validation checks required properties, array lengths and constants, applies no top-level conditionals, descends into pattern-matched child nodes, and finally enforces `additionalProperties` or `unevaluatedProperties`. Runtime flow starts only after the DTB is loaded: Linux driver core or MFD population uses the compatible and resources to bind drivers.

## State and Persistence Behavior
The YAML file stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: property names, compatible fallback order, address-cell layout, child-node names, and example nodes become contracts shipped in source DTS files and compiled DTBs. Runtime state is owned by the matched kernel drivers after probe, including controller probe state, bus decoding configuration, timing tables, ECC/error reporting, and child-device enumeration.

## Dependencies and Integration Points
Maintainers listed: Bjorn Andersson <andersson@kernel.org>. Schema dependencies include `mc-peripheral-props.yaml#`. Integration points include Linux memory-controller, EDAC, devfreq, interconnect, syscon/regmap, MTD/NAND/NOR, and external-bus child-device probing paths. The binding also participates in Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to compatible fallback ordering, register and interrupt resources, address/size cell layout, bus ranges, child-node regexes, timing properties, clocks, resets, and interconnect/IOMMU links, mismatch between documented compatibles and the driver's match table, resource ordering or cell-count mistakes that pass review but break probe, child-node regexes that over-match unrelated children or under-match valid bus devices. This schema rejects unknown top-level properties with `additionalProperties: false`. Because these bindings describe hardware contracts, regressions can appear as boot-time probe failures, missing child devices, invalid timing/ECC configuration, or dtbs_check noise across unrelated boards.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/memory-controllers/qcom,ebi2.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/memory-controllers/qcom,ebi2.yaml` against boards that instantiate the binding. The schema includes 1 embedded example; keep those examples compiling under `dt_binding_check`. Exercise child-node validation for `^.*@[0-5],[0-9a-f]+$`. Also compare compatible strings with in-tree driver `of_match_table` entries and review DTS examples for register tuple counts, interrupt names, clocks/resets, address ranges, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/qcom,ebi2.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/renesas,dbsc.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/renesas,dbsc.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/renesas,dbsc.yaml` defines the memory-controller or external-bus binding titled `Renesas DDR Bus Controllers`. Renesas SoCs contain one or more memory controllers. It is a Linux devicetree YAML schema that constrains source DTS/DTB hardware descriptions before the corresponding kernel drivers consume the nodes.

## Important APIs, Types, and Functions
The exported API is the devicetree ABI, not callable functions. `compatible` uses an `enum` of supported tokens with 3 tokens: `renesas,dbsc-r8a73a4`, `renesas,dbsc3-r8a7740`, `renesas,sbsc-sh73a0`. Top-level properties are `compatible`, `reg`, `interrupts`, `interrupt-names`, `power-domains`. Required top-level properties are `compatible`, `reg`, `power-domains`. Important reusable or nested constraints are: no unusually complex local constraints beyond the top-level properties. The highest-risk contract area is compatible fallback ordering, register and interrupt resources, address/size cell layout, bus ranges, child-node regexes, timing properties, clocks, resets, and interconnect/IOMMU links.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this schema and any `$ref` targets, then `dtbs_check` matches real DTS nodes by `compatible`, `$nodename`, or inclusion from a parent schema. Validation checks required properties, array lengths and constants, applies no top-level conditionals, descends into pattern-matched child nodes, and finally enforces `additionalProperties` or `unevaluatedProperties`. Runtime flow starts only after the DTB is loaded: Linux driver core or MFD population uses the compatible and resources to bind drivers.

## State and Persistence Behavior
The YAML file stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: property names, compatible fallback order, address-cell layout, child-node names, and example nodes become contracts shipped in source DTS files and compiled DTBs. Runtime state is owned by the matched kernel drivers after probe, including controller probe state, bus decoding configuration, timing tables, ECC/error reporting, and child-device enumeration.

## Dependencies and Integration Points
Maintainers listed: Geert Uytterhoeven <geert+renesas@glider.be>. Schema dependencies include dt-schema core/meta schemas only. Integration points include Linux memory-controller, EDAC, devfreq, interconnect, syscon/regmap, MTD/NAND/NOR, and external-bus child-device probing paths. The binding also participates in Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to compatible fallback ordering, register and interrupt resources, address/size cell layout, bus ranges, child-node regexes, timing properties, clocks, resets, and interconnect/IOMMU links, mismatch between documented compatibles and the driver's match table, resource ordering or cell-count mistakes that pass review but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Because these bindings describe hardware contracts, regressions can appear as boot-time probe failures, missing child devices, invalid timing/ECC configuration, or dtbs_check noise across unrelated boards.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/memory-controllers/renesas,dbsc.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/memory-controllers/renesas,dbsc.yaml` against boards that instantiate the binding. The schema includes 1 embedded example; keep those examples compiling under `dt_binding_check`. Also compare compatible strings with in-tree driver `of_match_table` entries and review DTS examples for register tuple counts, interrupt names, clocks/resets, address ranges, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/renesas,dbsc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/renesas,rpc-if.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/renesas,rpc-if.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/renesas,rpc-if.yaml` defines the memory-controller or external-bus binding titled `Renesas Reduced Pin Count Interface (RPC-IF)`. Renesas RPC-IF allows a SPI flash or HyperFlash connected to the SoC to be accessed via the external address space read mode or the manual mode. It is a Linux devicetree YAML schema that constrains source DTS/DTB hardware descriptions before the corresponding kernel drivers consume the nodes.

## Important APIs, Types, and Functions
The exported API is the devicetree ABI, not callable functions. `compatible` uses `oneOf` with 3 branches with 21 tokens: `renesas,r8a774a1-rpc-if`, `renesas,r8a774b1-rpc-if`, `renesas,r8a774c0-rpc-if`, `renesas,r8a774e1-rpc-if`, `renesas,r8a7795-rpc-if`, `renesas,r8a7796-rpc-if`, `renesas,r8a77961-rpc-if`, `renesas,r8a77965-rpc-if`, `renesas,r8a77970-rpc-if`, `renesas,r8a77980-rpc-if`, `renesas,r8a77990-rpc-if`, `renesas,r8a77995-rpc-if`, `renesas,r8a779a0-rpc-if`, `renesas,rcar-gen3-rpc-if`, `renesas,r8a779g0-rpc-if`, `renesas,r8a779h0-rpc-if`, and 5 more. Top-level properties are `compatible`, `reg`, `reg-names`, `clocks`, `interrupts`, `power-domains`, `resets`. Required top-level properties are `compatible`, `reg`, `reg-names`, `clocks`, `power-domains`, `resets`, `#address-cells`, `#size-cells`. Important reusable or nested constraints are: composition/conditionals: `allOf`, `if`, `then`, `else`; child-node patterns: `flash@[0-9a-f]+$`; referenced schemas: `/schemas/spi/spi-controller.yaml#`; child-node API keys include `compatible`; non-compatible enum/const values include `cfi-flash`, `jedec,spi-nor`. The highest-risk contract area is compatible fallback ordering, register and interrupt resources, address/size cell layout, bus ranges, child-node regexes, timing properties, clocks, resets, and interconnect/IOMMU links.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this schema and any `$ref` targets, then `dtbs_check` matches real DTS nodes by `compatible`, `$nodename`, or inclusion from a parent schema. Validation checks required properties, array lengths and constants, applies `allOf`, `if`, `then`, `else`, descends into pattern-matched child nodes, and finally enforces `additionalProperties` or `unevaluatedProperties`. Runtime flow starts only after the DTB is loaded: Linux driver core or MFD population uses the compatible and resources to bind drivers.

## State and Persistence Behavior
The YAML file stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: property names, compatible fallback order, address-cell layout, child-node names, and example nodes become contracts shipped in source DTS files and compiled DTBs. Runtime state is owned by the matched kernel drivers after probe, including controller probe state, bus decoding configuration, timing tables, ECC/error reporting, and child-device enumeration.

## Dependencies and Integration Points
Maintainers listed: Sergei Shtylyov <sergei.shtylyov@gmail.com>. Schema dependencies include `/schemas/spi/spi-controller.yaml#`. Integration points include Linux memory-controller, EDAC, devfreq, interconnect, syscon/regmap, MTD/NAND/NOR, and external-bus child-device probing paths. The binding also participates in Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to compatible fallback ordering, register and interrupt resources, address/size cell layout, bus ranges, child-node regexes, timing properties, clocks, resets, and interconnect/IOMMU links, mismatch between documented compatibles and the driver's match table, resource ordering or cell-count mistakes that pass review but break probe, conditional branches that accept one SoC or chip variant while silently rejecting another, child-node regexes that over-match unrelated children or under-match valid bus devices, large compatible sets where fallback ordering can drift across SoC generations. This schema closes composed schemas with `unevaluatedProperties: false`. Because these bindings describe hardware contracts, regressions can appear as boot-time probe failures, missing child devices, invalid timing/ECC configuration, or dtbs_check noise across unrelated boards.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/memory-controllers/renesas,rpc-if.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/memory-controllers/renesas,rpc-if.yaml` against boards that instantiate the binding. The schema includes 1 embedded example; keep those examples compiling under `dt_binding_check`. Exercise child-node validation for `flash@[0-9a-f]+$`. Also compare compatible strings with in-tree driver `of_match_table` entries and review DTS examples for register tuple counts, interrupt names, clocks/resets, address ranges, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/renesas,rpc-if.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/renesas,rzg3e-xspi.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/renesas,rzg3e-xspi.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/renesas,rzg3e-xspi.yaml` defines the memory-controller or external-bus binding titled `Renesas Expanded Serial Peripheral Interface (xSPI)`. Renesas xSPI allows a SPI flash connected to the SoC to be accessed via the memory-mapping or the manual command mode. It is a Linux devicetree YAML schema that constrains source DTS/DTB hardware descriptions before the corresponding kernel drivers consume the nodes.

## Important APIs, Types, and Functions
The exported API is the devicetree ABI, not callable functions. `compatible` uses `oneOf` with 2 branches with 3 tokens: `renesas,r9a09g047-xspi`, `renesas,r9a09g056-xspi`, `renesas,r9a09g057-xspi`. Top-level properties are `compatible`, `reg`, `reg-names`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, `power-domains`, `resets`, `reset-names`, `renesas,xspi-cs-addr-sys`. Required top-level properties are `compatible`, `reg`, `reg-names`, `interrupts`, `interrupt-names`, `clocks`, `clock-names`, `power-domains`, `resets`, `reset-names`, `#address-cells`, `#size-cells`. Important reusable or nested constraints are: composition/conditionals: `allOf`; child-node patterns: `flash@[0-9a-f]+$`; referenced schemas: `/schemas/spi/spi-controller.yaml#`, `/schemas/types.yaml#/definitions/phandle`; child-node API keys include `compatible`. The highest-risk contract area is compatible fallback ordering, register and interrupt resources, address/size cell layout, bus ranges, child-node regexes, timing properties, clocks, resets, and interconnect/IOMMU links.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this schema and any `$ref` targets, then `dtbs_check` matches real DTS nodes by `compatible`, `$nodename`, or inclusion from a parent schema. Validation checks required properties, array lengths and constants, applies `allOf`, descends into pattern-matched child nodes, and finally enforces `additionalProperties` or `unevaluatedProperties`. Runtime flow starts only after the DTB is loaded: Linux driver core or MFD population uses the compatible and resources to bind drivers.

## State and Persistence Behavior
The YAML file stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: property names, compatible fallback order, address-cell layout, child-node names, and example nodes become contracts shipped in source DTS files and compiled DTBs. Runtime state is owned by the matched kernel drivers after probe, including controller probe state, bus decoding configuration, timing tables, ECC/error reporting, and child-device enumeration.

## Dependencies and Integration Points
Maintainers listed: Biju Das <biju.das.jz@bp.renesas.com>. Schema dependencies include `/schemas/spi/spi-controller.yaml#`, `/schemas/types.yaml#/definitions/phandle`. Integration points include Linux memory-controller, EDAC, devfreq, interconnect, syscon/regmap, MTD/NAND/NOR, and external-bus child-device probing paths. The binding also participates in Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to compatible fallback ordering, register and interrupt resources, address/size cell layout, bus ranges, child-node regexes, timing properties, clocks, resets, and interconnect/IOMMU links, mismatch between documented compatibles and the driver's match table, resource ordering or cell-count mistakes that pass review but break probe, conditional branches that accept one SoC or chip variant while silently rejecting another, child-node regexes that over-match unrelated children or under-match valid bus devices. This schema closes composed schemas with `unevaluatedProperties: false`. Because these bindings describe hardware contracts, regressions can appear as boot-time probe failures, missing child devices, invalid timing/ECC configuration, or dtbs_check noise across unrelated boards.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/memory-controllers/renesas,rzg3e-xspi.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/memory-controllers/renesas,rzg3e-xspi.yaml` against boards that instantiate the binding. The schema includes 1 embedded example; keep those examples compiling under `dt_binding_check`. Exercise child-node validation for `flash@[0-9a-f]+$`. Also compare compatible strings with in-tree driver `of_match_table` entries and review DTS examples for register tuple counts, interrupt names, clocks/resets, address ranges, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/renesas,rzg3e-xspi.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/rockchip,rk3399-dmc.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/rockchip,rk3399-dmc.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/rockchip,rk3399-dmc.yaml` defines the memory-controller or external-bus binding titled `Rockchip rk3399 DMC (Dynamic Memory Controller) device`. It constrains devicetree nodes through compatible strings, required resources, bus topology, and shared schema references before the corresponding Linux subsystem uses the node at probe time.

## Important APIs, Types, and Functions
The exported API is the devicetree ABI, not callable functions. `compatible` uses an `enum` of supported tokens with 1 token: `rockchip,rk3399-dmc`. Top-level properties are `compatible`, `devfreq-events`, `clocks`, `clock-names`, `operating-points-v2`, `center-supply`, `rockchip,pmu`, `interrupts`, `rockchip,ddr3_speed_bin`, `rockchip,pd_idle`, `rockchip,sr_idle`, `rockchip,sr_mc_gate_idle`, `rockchip,srpd_lite_idle`, `rockchip,standby_idle`, `rockchip,dram_dll_dis_freq`, `rockchip,phy_dll_dis_freq`, `rockchip,auto_pd_dis_freq`, `rockchip,ddr3_odt_dis_freq`, `rockchip,ddr3_drv`, `rockchip,ddr3_odt`, `rockchip,phy_ddr3_ca_drv`, `rockchip,phy_ddr3_dq_drv`, `rockchip,phy_ddr3_odt`, `rockchip,lpddr3_odt_dis_freq`, and 23 more. Required top-level properties are `compatible`, `devfreq-events`, `clocks`, `clock-names`, `operating-points-v2`, `center-supply`. Important reusable or nested constraints are: referenced schemas: `/schemas/types.yaml#/definitions/phandle`, `/schemas/types.yaml#/definitions/uint32`. The highest-risk contract area is compatible fallback ordering, register and interrupt resources, address/size cell layout, bus ranges, child-node regexes, timing properties, clocks, resets, and interconnect/IOMMU links.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this schema and any `$ref` targets, then `dtbs_check` matches real DTS nodes by `compatible`, `$nodename`, or inclusion from a parent schema. Validation checks required properties, array lengths and constants, applies no top-level conditionals, descends into pattern-matched child nodes, and finally enforces `additionalProperties` or `unevaluatedProperties`. Runtime flow starts only after the DTB is loaded: Linux driver core or MFD population uses the compatible and resources to bind drivers.

## State and Persistence Behavior
The YAML file stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: property names, compatible fallback order, address-cell layout, child-node names, and example nodes become contracts shipped in source DTS files and compiled DTBs. Runtime state is owned by the matched kernel drivers after probe, including controller probe state, bus decoding configuration, timing tables, ECC/error reporting, and child-device enumeration.

## Dependencies and Integration Points
Maintainers listed: Brian Norris <briannorris@chromium.org>. Schema dependencies include `/schemas/types.yaml#/definitions/phandle`, `/schemas/types.yaml#/definitions/uint32`. Integration points include Linux memory-controller, EDAC, devfreq, interconnect, syscon/regmap, MTD/NAND/NOR, and external-bus child-device probing paths. The binding also participates in Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to compatible fallback ordering, register and interrupt resources, address/size cell layout, bus ranges, child-node regexes, timing properties, clocks, resets, and interconnect/IOMMU links, mismatch between documented compatibles and the driver's match table, resource ordering or cell-count mistakes that pass review but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Because these bindings describe hardware contracts, regressions can appear as boot-time probe failures, missing child devices, invalid timing/ECC configuration, or dtbs_check noise across unrelated boards.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/memory-controllers/rockchip,rk3399-dmc.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/memory-controllers/rockchip,rk3399-dmc.yaml` against boards that instantiate the binding. The schema includes 1 embedded example; keep those examples compiling under `dt_binding_check`. Also compare compatible strings with in-tree driver `of_match_table` entries and review DTS examples for register tuple counts, interrupt names, clocks/resets, address ranges, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/rockchip,rk3399-dmc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/samsung,exynos4210-srom-peripheral-props.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/samsung,exynos4210-srom-peripheral-props.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/samsung,exynos4210-srom-peripheral-props.yaml` defines the memory-controller or external-bus binding titled `Peripheral Properties for Samsung Exynos SoC SROM Controller`. It constrains devicetree nodes through compatible strings, required resources, bus topology, and shared schema references before the corresponding Linux subsystem uses the node at probe time.

## Important APIs, Types, and Functions
The exported API is the devicetree ABI, not callable functions. This is a reusable child/common schema fragment rather than a directly probed node, so its API is the properties it adds to another binding. Top-level properties are `samsung,srom-page-mode`, `samsung,srom-timing`. Required top-level properties are none declared. Important reusable or nested constraints are: referenced schemas: `/schemas/types.yaml#/definitions/uint32-array`. The highest-risk contract area is compatible fallback ordering, register and interrupt resources, address/size cell layout, bus ranges, child-node regexes, timing properties, clocks, resets, and interconnect/IOMMU links.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this schema and any `$ref` targets, then `dtbs_check` matches real DTS nodes by `compatible`, `$nodename`, or inclusion from a parent schema. Validation checks required properties, array lengths and constants, applies no top-level conditionals, descends into pattern-matched child nodes, and finally enforces `additionalProperties` or `unevaluatedProperties`. Runtime flow starts only after the DTB is loaded: Linux driver core or MFD population uses the compatible and resources to bind drivers.

## State and Persistence Behavior
The YAML file stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: property names, compatible fallback order, address-cell layout, child-node names, and example nodes become contracts shipped in source DTS files and compiled DTBs. Runtime state is owned by the matched kernel drivers after probe, including controller probe state, bus decoding configuration, timing tables, ECC/error reporting, and child-device enumeration.

## Dependencies and Integration Points
Maintainers listed: Krzysztof Kozlowski <krzk@kernel.org>. Schema dependencies include `/schemas/types.yaml#/definitions/uint32-array`. Integration points include Linux memory-controller, EDAC, devfreq, interconnect, syscon/regmap, MTD/NAND/NOR, and external-bus child-device probing paths. The binding also participates in Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to compatible fallback ordering, register and interrupt resources, address/size cell layout, bus ranges, child-node regexes, timing properties, clocks, resets, and interconnect/IOMMU links, mismatch between documented compatibles and the driver's match table, resource ordering or cell-count mistakes that pass review but break probe, permissive extra properties that can hide spelling errors unless a parent/child schema catches them, lack of embedded examples, leaving coverage dependent on in-tree DTS users. This schema permits additional top-level properties so it can be layered with device-specific child bindings. Because these bindings describe hardware contracts, regressions can appear as boot-time probe failures, missing child devices, invalid timing/ECC configuration, or dtbs_check noise across unrelated boards.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/memory-controllers/samsung,exynos4210-srom-peripheral-props.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/memory-controllers/samsung,exynos4210-srom-peripheral-props.yaml` against boards that instantiate the binding. There are no embedded examples, so representative DTS users and schema-only validation carry the coverage. Also compare compatible strings with in-tree driver `of_match_table` entries and review DTS examples for register tuple counts, interrupt names, clocks/resets, address ranges, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/samsung,exynos4210-srom-peripheral-props.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/samsung,exynos5422-dmc.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/samsung,exynos5422-dmc.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/samsung,exynos5422-dmc.yaml` defines the memory-controller or external-bus binding titled `Samsung Exynos5422 SoC frequency and voltage scaling for Dynamic Memory
Controller device
`. The Samsung Exynos5422 SoC has DMC (Dynamic Memory Controller) to which the DRAM memory chips are connected. It is a Linux devicetree YAML schema that constrains source DTS/DTB hardware descriptions before the corresponding kernel drivers consume the nodes.

## Important APIs, Types, and Functions
The exported API is the devicetree ABI, not callable functions. `compatible` uses an ordered compatible/fallback `items` sequence with 1 token: `samsung,exynos5422-dmc`. Top-level properties are `compatible`, `clock-names`, `clocks`, `devfreq-events`, `device-handle`, `operating-points-v2`, `interrupts`, `interrupt-names`, `reg`, `samsung,syscon-clk`, `vdd-supply`. Required top-level properties are `compatible`, `clock-names`, `clocks`, `devfreq-events`, `device-handle`, `reg`, `samsung,syscon-clk`. Important reusable or nested constraints are: referenced schemas: `/schemas/types.yaml#/definitions/phandle`, `/schemas/types.yaml#/definitions/phandle-array`. The highest-risk contract area is compatible fallback ordering, register and interrupt resources, address/size cell layout, bus ranges, child-node regexes, timing properties, clocks, resets, and interconnect/IOMMU links.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this schema and any `$ref` targets, then `dtbs_check` matches real DTS nodes by `compatible`, `$nodename`, or inclusion from a parent schema. Validation checks required properties, array lengths and constants, applies no top-level conditionals, descends into pattern-matched child nodes, and finally enforces `additionalProperties` or `unevaluatedProperties`. Runtime flow starts only after the DTB is loaded: Linux driver core or MFD population uses the compatible and resources to bind drivers.

## State and Persistence Behavior
The YAML file stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: property names, compatible fallback order, address-cell layout, child-node names, and example nodes become contracts shipped in source DTS files and compiled DTBs. Runtime state is owned by the matched kernel drivers after probe, including controller probe state, bus decoding configuration, timing tables, ECC/error reporting, and child-device enumeration.

## Dependencies and Integration Points
Maintainers listed: Krzysztof Kozlowski <krzk@kernel.org>, Lukasz Luba <lukasz.luba@arm.com>. Schema dependencies include `/schemas/types.yaml#/definitions/phandle`, `/schemas/types.yaml#/definitions/phandle-array`. Integration points include Linux memory-controller, EDAC, devfreq, interconnect, syscon/regmap, MTD/NAND/NOR, and external-bus child-device probing paths. The binding also participates in Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to compatible fallback ordering, register and interrupt resources, address/size cell layout, bus ranges, child-node regexes, timing properties, clocks, resets, and interconnect/IOMMU links, mismatch between documented compatibles and the driver's match table, resource ordering or cell-count mistakes that pass review but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Because these bindings describe hardware contracts, regressions can appear as boot-time probe failures, missing child devices, invalid timing/ECC configuration, or dtbs_check noise across unrelated boards.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/memory-controllers/samsung,exynos5422-dmc.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/memory-controllers/samsung,exynos5422-dmc.yaml` against boards that instantiate the binding. The schema includes 1 embedded example; keep those examples compiling under `dt_binding_check`. Also compare compatible strings with in-tree driver `of_match_table` entries and review DTS examples for register tuple counts, interrupt names, clocks/resets, address ranges, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/samsung,exynos5422-dmc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/samsung,s5pv210-dmc.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/samsung,s5pv210-dmc.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/samsung,s5pv210-dmc.yaml` defines the memory-controller or external-bus binding titled `Samsung S5Pv210 SoC Dynamic Memory Controller`. Dynamic Memory Controller interfaces external JEDEC DDR-type SDRAM. It is a Linux devicetree YAML schema that constrains source DTS/DTB hardware descriptions before the corresponding kernel drivers consume the nodes.

## Important APIs, Types, and Functions
The exported API is the devicetree ABI, not callable functions. `compatible` uses a single `const` token with 1 token: `samsung,s5pv210-dmc`. Top-level properties are `compatible`, `reg`. Required top-level properties are `compatible`, `reg`. Important reusable or nested constraints are: no unusually complex local constraints beyond the top-level properties. The highest-risk contract area is compatible fallback ordering, register and interrupt resources, address/size cell layout, bus ranges, child-node regexes, timing properties, clocks, resets, and interconnect/IOMMU links.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this schema and any `$ref` targets, then `dtbs_check` matches real DTS nodes by `compatible`, `$nodename`, or inclusion from a parent schema. Validation checks required properties, array lengths and constants, applies no top-level conditionals, descends into pattern-matched child nodes, and finally enforces `additionalProperties` or `unevaluatedProperties`. Runtime flow starts only after the DTB is loaded: Linux driver core or MFD population uses the compatible and resources to bind drivers.

## State and Persistence Behavior
The YAML file stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: property names, compatible fallback order, address-cell layout, child-node names, and example nodes become contracts shipped in source DTS files and compiled DTBs. Runtime state is owned by the matched kernel drivers after probe, including controller probe state, bus decoding configuration, timing tables, ECC/error reporting, and child-device enumeration.

## Dependencies and Integration Points
Maintainers listed: Krzysztof Kozlowski <krzk@kernel.org>. Schema dependencies include dt-schema core/meta schemas only. Integration points include Linux memory-controller, EDAC, devfreq, interconnect, syscon/regmap, MTD/NAND/NOR, and external-bus child-device probing paths. The binding also participates in Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to compatible fallback ordering, register and interrupt resources, address/size cell layout, bus ranges, child-node regexes, timing properties, clocks, resets, and interconnect/IOMMU links, mismatch between documented compatibles and the driver's match table, resource ordering or cell-count mistakes that pass review but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Because these bindings describe hardware contracts, regressions can appear as boot-time probe failures, missing child devices, invalid timing/ECC configuration, or dtbs_check noise across unrelated boards.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/memory-controllers/samsung,s5pv210-dmc.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/memory-controllers/samsung,s5pv210-dmc.yaml` against boards that instantiate the binding. The schema includes 1 embedded example; keep those examples compiling under `dt_binding_check`. Also compare compatible strings with in-tree driver `of_match_table` entries and review DTS examples for register tuple counts, interrupt names, clocks/resets, address ranges, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/samsung,s5pv210-dmc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/snps,dw-umctl2-ddrc.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/snps,dw-umctl2-ddrc.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/snps,dw-umctl2-ddrc.yaml` defines the memory-controller or external-bus binding titled `Synopsys DesignWare Universal Multi-Protocol Memory Controller`. Synopsys DesignWare Enhanced uMCTL2 DDR Memory Controller is capable of working with the memory devices supporting up to (LP)DDR4 protocol. It is a Linux devicetree YAML schema that constrains source DTS/DTB hardware descriptions before the corresponding kernel drivers consume the nodes.

## Important APIs, Types, and Functions
The exported API is the devicetree ABI, not callable functions. `compatible` uses `oneOf` with 3 branches with 3 tokens: `snps,ddrc-3.80a`, `snps,dw-umctl2-ddrc`, `xlnx,zynqmp-ddrc-2.40a`. Top-level properties are `compatible`, `interrupts`, `interrupt-names`, `reg`, `clocks`, `clock-names`, `resets`, `reset-names`. Required top-level properties are `compatible`, `reg`, `interrupts`. Important reusable or nested constraints are: non-compatible enum/const values include `ecc_ce`, `ecc_ue`, `ecc_ap`, `ecc_sbr`, `dfi_e`, `pclk`, `aclk`, `core`, `sbr`, `prst`, and 1 more. The highest-risk contract area is compatible fallback ordering, register and interrupt resources, address/size cell layout, bus ranges, child-node regexes, timing properties, clocks, resets, and interconnect/IOMMU links.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this schema and any `$ref` targets, then `dtbs_check` matches real DTS nodes by `compatible`, `$nodename`, or inclusion from a parent schema. Validation checks required properties, array lengths and constants, applies no top-level conditionals, descends into pattern-matched child nodes, and finally enforces `additionalProperties` or `unevaluatedProperties`. Runtime flow starts only after the DTB is loaded: Linux driver core or MFD population uses the compatible and resources to bind drivers.

## State and Persistence Behavior
The YAML file stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: property names, compatible fallback order, address-cell layout, child-node names, and example nodes become contracts shipped in source DTS files and compiled DTBs. Runtime state is owned by the matched kernel drivers after probe, including controller probe state, bus decoding configuration, timing tables, ECC/error reporting, and child-device enumeration.

## Dependencies and Integration Points
Maintainers listed: Krzysztof Kozlowski <krzk@kernel.org>, Michal Simek <michal.simek@amd.com>. Schema dependencies include dt-schema core/meta schemas only. Integration points include Linux memory-controller, EDAC, devfreq, interconnect, syscon/regmap, MTD/NAND/NOR, and external-bus child-device probing paths. The binding also participates in Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to compatible fallback ordering, register and interrupt resources, address/size cell layout, bus ranges, child-node regexes, timing properties, clocks, resets, and interconnect/IOMMU links, mismatch between documented compatibles and the driver's match table, resource ordering or cell-count mistakes that pass review but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Because these bindings describe hardware contracts, regressions can appear as boot-time probe failures, missing child devices, invalid timing/ECC configuration, or dtbs_check noise across unrelated boards.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/memory-controllers/snps,dw-umctl2-ddrc.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/memory-controllers/snps,dw-umctl2-ddrc.yaml` against boards that instantiate the binding. The schema includes 2 embedded examples; keep those examples compiling under `dt_binding_check`. Also compare compatible strings with in-tree driver `of_match_table` entries and review DTS examples for register tuple counts, interrupt names, clocks/resets, address ranges, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/snps,dw-umctl2-ddrc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/st,stm32-fmc2-ebi-props.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/st,stm32-fmc2-ebi-props.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/st,stm32-fmc2-ebi-props.yaml` defines the memory-controller or external-bus binding titled `Peripheral properties for ST FMC2 Controller`. It constrains devicetree nodes through compatible strings, required resources, bus topology, and shared schema references before the corresponding Linux subsystem uses the node at probe time.

## Important APIs, Types, and Functions
The exported API is the devicetree ABI, not callable functions. This is a reusable child/common schema fragment rather than a directly probed node, so its API is the properties it adds to another binding. Top-level properties are `st,fmc2-ebi-cs-transaction-type`, `st,fmc2-ebi-cs-cclk-enable`, `st,fmc2-ebi-cs-mux-enable`, `st,fmc2-ebi-cs-buswidth`, `st,fmc2-ebi-cs-waitpol-high`, `st,fmc2-ebi-cs-waitcfg-enable`, `st,fmc2-ebi-cs-wait-enable`, `st,fmc2-ebi-cs-asyncwait-enable`, `st,fmc2-ebi-cs-cpsize`, `st,fmc2-ebi-cs-byte-lane-setup-ns`, `st,fmc2-ebi-cs-address-setup-ns`, `st,fmc2-ebi-cs-address-hold-ns`, `st,fmc2-ebi-cs-data-setup-ns`, `st,fmc2-ebi-cs-bus-turnaround-ns`, `st,fmc2-ebi-cs-data-hold-ns`, `st,fmc2-ebi-cs-clk-period-ns`, `st,fmc2-ebi-cs-data-latency-ns`, `st,fmc2-ebi-cs-write-address-setup-ns`, `st,fmc2-ebi-cs-write-address-hold-ns`, `st,fmc2-ebi-cs-write-data-setup-ns`, `st,fmc2-ebi-cs-write-bus-turnaround-ns`, `st,fmc2-ebi-cs-write-data-hold-ns`, `st,fmc2-ebi-cs-max-low-pulse-ns`. Required top-level properties are none declared. Important reusable or nested constraints are: referenced schemas: `/schemas/types.yaml#/definitions/flag`, `/schemas/types.yaml#/definitions/uint32`; non-compatible enum/const values include `8`, `16`, `0`, `128`, `256`, `512`, `1024`. The highest-risk contract area is compatible fallback ordering, register and interrupt resources, address/size cell layout, bus ranges, child-node regexes, timing properties, clocks, resets, and interconnect/IOMMU links.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this schema and any `$ref` targets, then `dtbs_check` matches real DTS nodes by `compatible`, `$nodename`, or inclusion from a parent schema. Validation checks required properties, array lengths and constants, applies no top-level conditionals, descends into pattern-matched child nodes, and finally enforces `additionalProperties` or `unevaluatedProperties`. Runtime flow starts only after the DTB is loaded: Linux driver core or MFD population uses the compatible and resources to bind drivers.

## State and Persistence Behavior
The YAML file stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: property names, compatible fallback order, address-cell layout, child-node names, and example nodes become contracts shipped in source DTS files and compiled DTBs. Runtime state is owned by the matched kernel drivers after probe, including controller probe state, bus decoding configuration, timing tables, ECC/error reporting, and child-device enumeration.

## Dependencies and Integration Points
Maintainers listed: Christophe Kerello <christophe.kerello@foss.st.com>, Marek Vasut <marex@denx.de>. Schema dependencies include `/schemas/types.yaml#/definitions/flag`, `/schemas/types.yaml#/definitions/uint32`. Integration points include Linux memory-controller, EDAC, devfreq, interconnect, syscon/regmap, MTD/NAND/NOR, and external-bus child-device probing paths. The binding also participates in Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to compatible fallback ordering, register and interrupt resources, address/size cell layout, bus ranges, child-node regexes, timing properties, clocks, resets, and interconnect/IOMMU links, mismatch between documented compatibles and the driver's match table, resource ordering or cell-count mistakes that pass review but break probe, permissive extra properties that can hide spelling errors unless a parent/child schema catches them, lack of embedded examples, leaving coverage dependent on in-tree DTS users. This schema permits additional top-level properties so it can be layered with device-specific child bindings. Because these bindings describe hardware contracts, regressions can appear as boot-time probe failures, missing child devices, invalid timing/ECC configuration, or dtbs_check noise across unrelated boards.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/memory-controllers/st,stm32-fmc2-ebi-props.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/memory-controllers/st,stm32-fmc2-ebi-props.yaml` against boards that instantiate the binding. There are no embedded examples, so representative DTS users and schema-only validation carry the coverage. Also compare compatible strings with in-tree driver `of_match_table` entries and review DTS examples for register tuple counts, interrupt names, clocks/resets, address ranges, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/st,stm32-fmc2-ebi-props.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/st,stm32-fmc2-ebi.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/st,stm32-fmc2-ebi.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/st,stm32-fmc2-ebi.yaml` defines the memory-controller or external-bus binding titled `STMicroelectronics Flexible Memory Controller 2 (FMC2)`. The FMC2 functional block makes the interface with: synchronous and asynchronous static devices (such as PSNOR, PSRAM or other memory-mapped peripherals) and NAND flash memories. It is a Linux devicetree YAML schema that constrains source DTS/DTB hardware descriptions before the corresponding kernel drivers consume the nodes.

## Important APIs, Types, and Functions
The exported API is the devicetree ABI, not callable functions. `compatible` uses an `enum` of supported tokens with 2 tokens: `st,stm32mp1-fmc2-ebi`, `st,stm32mp25-fmc2-ebi`. Top-level properties are `compatible`, `reg`, `clocks`, `resets`, `power-domains`, `#address-cells`, `#size-cells`, `ranges`, `access-controllers`. Required top-level properties are `#address-cells`, `#size-cells`, `compatible`, `reg`, `clocks`, `ranges`. Important reusable or nested constraints are: child-node patterns: `^.*@[0-4],[a-f0-9]+$`; referenced schemas: `mc-peripheral-props.yaml#`. The highest-risk contract area is compatible fallback ordering, register and interrupt resources, address/size cell layout, bus ranges, child-node regexes, timing properties, clocks, resets, and interconnect/IOMMU links.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this schema and any `$ref` targets, then `dtbs_check` matches real DTS nodes by `compatible`, `$nodename`, or inclusion from a parent schema. Validation checks required properties, array lengths and constants, applies no top-level conditionals, descends into pattern-matched child nodes, and finally enforces `additionalProperties` or `unevaluatedProperties`. Runtime flow starts only after the DTB is loaded: Linux driver core or MFD population uses the compatible and resources to bind drivers.

## State and Persistence Behavior
The YAML file stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: property names, compatible fallback order, address-cell layout, child-node names, and example nodes become contracts shipped in source DTS files and compiled DTBs. Runtime state is owned by the matched kernel drivers after probe, including controller probe state, bus decoding configuration, timing tables, ECC/error reporting, and child-device enumeration.

## Dependencies and Integration Points
Maintainers listed: Christophe Kerello <christophe.kerello@foss.st.com>. Schema dependencies include `mc-peripheral-props.yaml#`. Integration points include Linux memory-controller, EDAC, devfreq, interconnect, syscon/regmap, MTD/NAND/NOR, and external-bus child-device probing paths. The binding also participates in Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to compatible fallback ordering, register and interrupt resources, address/size cell layout, bus ranges, child-node regexes, timing properties, clocks, resets, and interconnect/IOMMU links, mismatch between documented compatibles and the driver's match table, resource ordering or cell-count mistakes that pass review but break probe, child-node regexes that over-match unrelated children or under-match valid bus devices. This schema rejects unknown top-level properties with `additionalProperties: false`. Because these bindings describe hardware contracts, regressions can appear as boot-time probe failures, missing child devices, invalid timing/ECC configuration, or dtbs_check noise across unrelated boards.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/memory-controllers/st,stm32-fmc2-ebi.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/memory-controllers/st,stm32-fmc2-ebi.yaml` against boards that instantiate the binding. The schema includes 1 embedded example; keep those examples compiling under `dt_binding_check`. Exercise child-node validation for `^.*@[0-4],[a-f0-9]+$`. Also compare compatible strings with in-tree driver `of_match_table` entries and review DTS examples for register tuple counts, interrupt names, clocks/resets, address ranges, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/st,stm32-fmc2-ebi.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/st,stm32mp25-omm.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/st,stm32mp25-omm.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/st,stm32mp25-omm.yaml` defines the memory-controller or external-bus binding titled `STM32 Octo Memory Manager (OMM)`. The STM32 Octo Memory Manager is a low-level interface that enables an efficient OCTOSPI pin assignment with a full I/O matrix (before alternate function map) and multiplex of single/dual/quad/octal SPI interfaces over the same bus. It is a Linux devicetree YAML schema that constrains source DTS/DTB hardware descriptions before the corresponding kernel drivers consume the nodes.

## Important APIs, Types, and Functions
The exported API is the devicetree ABI, not callable functions. `compatible` uses a single `const` token with 1 token: `st,stm32mp25-omm`. Top-level properties are `compatible`, `#address-cells`, `#size-cells`, `ranges`, `reg`, `reg-names`, `memory-region`, `memory-region-names`, `clocks`, `clock-names`, `resets`, `reset-names`, `access-controllers`, `power-domains`, `st,syscfg-amcr`, `st,omm-req2ack-ns`, `st,omm-cssel-ovr`, `st,omm-mux`. Required top-level properties are `compatible`, `reg`, `#address-cells`, `#size-cells`, `clocks`, `clock-names`, `resets`, `reset-names`, `st,syscfg-amcr`, `ranges`. Important reusable or nested constraints are: child-node patterns: `^spi@[0-9]`; referenced schemas: `/schemas/spi/st,stm32mp25-ospi.yaml#`, `/schemas/types.yaml#/definitions/phandle-array`, `/schemas/types.yaml#/definitions/uint32`; non-compatible enum/const values include `ospi1`, `ospi2`. The highest-risk contract area is compatible fallback ordering, register and interrupt resources, address/size cell layout, bus ranges, child-node regexes, timing properties, clocks, resets, and interconnect/IOMMU links.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this schema and any `$ref` targets, then `dtbs_check` matches real DTS nodes by `compatible`, `$nodename`, or inclusion from a parent schema. Validation checks required properties, array lengths and constants, applies no top-level conditionals, descends into pattern-matched child nodes, and finally enforces `additionalProperties` or `unevaluatedProperties`. Runtime flow starts only after the DTB is loaded: Linux driver core or MFD population uses the compatible and resources to bind drivers.

## State and Persistence Behavior
The YAML file stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: property names, compatible fallback order, address-cell layout, child-node names, and example nodes become contracts shipped in source DTS files and compiled DTBs. Runtime state is owned by the matched kernel drivers after probe, including controller probe state, bus decoding configuration, timing tables, ECC/error reporting, and child-device enumeration.

## Dependencies and Integration Points
Maintainers listed: Patrice Chotard <patrice.chotard@foss.st.com>. Schema dependencies include `/schemas/spi/st,stm32mp25-ospi.yaml#`, `/schemas/types.yaml#/definitions/phandle-array`, `/schemas/types.yaml#/definitions/uint32`. Integration points include Linux memory-controller, EDAC, devfreq, interconnect, syscon/regmap, MTD/NAND/NOR, and external-bus child-device probing paths. The binding also participates in Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to compatible fallback ordering, register and interrupt resources, address/size cell layout, bus ranges, child-node regexes, timing properties, clocks, resets, and interconnect/IOMMU links, mismatch between documented compatibles and the driver's match table, resource ordering or cell-count mistakes that pass review but break probe, child-node regexes that over-match unrelated children or under-match valid bus devices. This schema rejects unknown top-level properties with `additionalProperties: false`. Because these bindings describe hardware contracts, regressions can appear as boot-time probe failures, missing child devices, invalid timing/ECC configuration, or dtbs_check noise across unrelated boards.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/memory-controllers/st,stm32mp25-omm.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/memory-controllers/st,stm32mp25-omm.yaml` against boards that instantiate the binding. The schema includes 1 embedded example; keep those examples compiling under `dt_binding_check`. Exercise child-node validation for `^spi@[0-9]`. Also compare compatible strings with in-tree driver `of_match_table` entries and review DTS examples for register tuple counts, interrupt names, clocks/resets, address ranges, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/st,stm32mp25-omm.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/starfive,jh7110-dmc.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/starfive,jh7110-dmc.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/starfive,jh7110-dmc.yaml` defines the memory-controller or external-bus binding titled `StarFive JH7110 DMC`. JH7110 DDR external memory interface LPDDR4/DDR4/DDR3/LPDDR3 32-bit at 2133Mbps (up to 2800Mbps). It is a Linux devicetree YAML schema that constrains source DTS/DTB hardware descriptions before the corresponding kernel drivers consume the nodes.

## Important APIs, Types, and Functions
The exported API is the devicetree ABI, not callable functions. `compatible` uses an ordered compatible/fallback `items` sequence with 1 token: `starfive,jh7110-dmc`. Top-level properties are `compatible`, `reg`, `clocks`, `clock-names`, `resets`, `reset-names`. Required top-level properties are `compatible`, `reg`, `clocks`, `clock-names`, `resets`, `reset-names`. Important reusable or nested constraints are: no unusually complex local constraints beyond the top-level properties. The highest-risk contract area is compatible fallback ordering, register and interrupt resources, address/size cell layout, bus ranges, child-node regexes, timing properties, clocks, resets, and interconnect/IOMMU links.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this schema and any `$ref` targets, then `dtbs_check` matches real DTS nodes by `compatible`, `$nodename`, or inclusion from a parent schema. Validation checks required properties, array lengths and constants, applies no top-level conditionals, descends into pattern-matched child nodes, and finally enforces `additionalProperties` or `unevaluatedProperties`. Runtime flow starts only after the DTB is loaded: Linux driver core or MFD population uses the compatible and resources to bind drivers.

## State and Persistence Behavior
The YAML file stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: property names, compatible fallback order, address-cell layout, child-node names, and example nodes become contracts shipped in source DTS files and compiled DTBs. Runtime state is owned by the matched kernel drivers after probe, including controller probe state, bus decoding configuration, timing tables, ECC/error reporting, and child-device enumeration.

## Dependencies and Integration Points
Maintainers listed: E Shattow <e@freeshell.de>. Schema dependencies include dt-schema core/meta schemas only. Integration points include Linux memory-controller, EDAC, devfreq, interconnect, syscon/regmap, MTD/NAND/NOR, and external-bus child-device probing paths. The binding also participates in Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to compatible fallback ordering, register and interrupt resources, address/size cell layout, bus ranges, child-node regexes, timing properties, clocks, resets, and interconnect/IOMMU links, mismatch between documented compatibles and the driver's match table, resource ordering or cell-count mistakes that pass review but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Because these bindings describe hardware contracts, regressions can appear as boot-time probe failures, missing child devices, invalid timing/ECC configuration, or dtbs_check noise across unrelated boards.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/memory-controllers/starfive,jh7110-dmc.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/memory-controllers/starfive,jh7110-dmc.yaml` against boards that instantiate the binding. The schema includes 1 embedded example; keep those examples compiling under `dt_binding_check`. Also compare compatible strings with in-tree driver `of_match_table` entries and review DTS examples for register tuple counts, interrupt names, clocks/resets, address ranges, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/starfive,jh7110-dmc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/ti,da8xx-ddrctl.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/ti,da8xx-ddrctl.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/ti,da8xx-ddrctl.yaml` defines the memory-controller or external-bus binding titled `Texas Instruments da8xx DDR2/mDDR memory controller`. Documentation: OMAP-L138 (DA850) - http://www.ti.com/lit/ug/spruh82c/spruh82c.pdf It is a Linux devicetree YAML schema that constrains source DTS/DTB hardware descriptions before the corresponding kernel drivers consume the nodes.

## Important APIs, Types, and Functions
The exported API is the devicetree ABI, not callable functions. `compatible` uses a single `const` token with 1 token: `ti,da850-ddr-controller`. Top-level properties are `compatible`, `reg`. Required top-level properties are `compatible`, `reg`. Important reusable or nested constraints are: no unusually complex local constraints beyond the top-level properties. The highest-risk contract area is compatible fallback ordering, register and interrupt resources, address/size cell layout, bus ranges, child-node regexes, timing properties, clocks, resets, and interconnect/IOMMU links.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this schema and any `$ref` targets, then `dtbs_check` matches real DTS nodes by `compatible`, `$nodename`, or inclusion from a parent schema. Validation checks required properties, array lengths and constants, applies no top-level conditionals, descends into pattern-matched child nodes, and finally enforces `additionalProperties` or `unevaluatedProperties`. Runtime flow starts only after the DTB is loaded: Linux driver core or MFD population uses the compatible and resources to bind drivers.

## State and Persistence Behavior
The YAML file stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: property names, compatible fallback order, address-cell layout, child-node names, and example nodes become contracts shipped in source DTS files and compiled DTBs. Runtime state is owned by the matched kernel drivers after probe, including controller probe state, bus decoding configuration, timing tables, ECC/error reporting, and child-device enumeration.

## Dependencies and Integration Points
Maintainers listed: Bartosz Golaszewski <bgolaszewski@baylibre.com>, Krzysztof Kozlowski <krzk@kernel.org>. Schema dependencies include dt-schema core/meta schemas only. Integration points include Linux memory-controller, EDAC, devfreq, interconnect, syscon/regmap, MTD/NAND/NOR, and external-bus child-device probing paths. The binding also participates in Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to compatible fallback ordering, register and interrupt resources, address/size cell layout, bus ranges, child-node regexes, timing properties, clocks, resets, and interconnect/IOMMU links, mismatch between documented compatibles and the driver's match table, resource ordering or cell-count mistakes that pass review but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Because these bindings describe hardware contracts, regressions can appear as boot-time probe failures, missing child devices, invalid timing/ECC configuration, or dtbs_check noise across unrelated boards.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/memory-controllers/ti,da8xx-ddrctl.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/memory-controllers/ti,da8xx-ddrctl.yaml` against boards that instantiate the binding. The schema includes 1 embedded example; keep those examples compiling under `dt_binding_check`. Also compare compatible strings with in-tree driver `of_match_table` entries and review DTS examples for register tuple counts, interrupt names, clocks/resets, address ranges, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/ti,da8xx-ddrctl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/ti,gpmc-child.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/ti,gpmc-child.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/ti,gpmc-child.yaml` defines the memory-controller or external-bus binding titled `Texas Instruments GPMC Bus Child Nodes`. This binding is meant for the child nodes of the GPMC node. It is a Linux devicetree YAML schema that constrains source DTS/DTB hardware descriptions before the corresponding kernel drivers consume the nodes.

## Important APIs, Types, and Functions
The exported API is the devicetree ABI, not callable functions. This is a reusable child/common schema fragment rather than a directly probed node, so its API is the properties it adds to another binding. Top-level properties are `reg`, `gpmc,sync-clk-ps`, `gpmc,cs-on-ns`, `gpmc,cs-rd-off-ns`, `gpmc,cs-wr-off-ns`, `gpmc,adv-on-ns`, `gpmc,adv-rd-off-ns`, `gpmc,adv-wr-off-ns`, `gpmc,adv-aad-mux-on-ns`, `gpmc,adv-aad-mux-rd-off-ns`, `gpmc,adv-aad-mux-wr-off-ns`, `gpmc,we-on-ns`, `gpmc,we-off-ns`, `gpmc,oe-on-ns`, `gpmc,oe-off-ns`, `gpmc,oe-aad-mux-on-ns`, `gpmc,oe-aad-mux-off-ns`, `gpmc,page-burst-access-ns`, `gpmc,access-ns`, `gpmc,rd-cycle-ns`, `gpmc,wr-cycle-ns`, `gpmc,bus-turnaround-ns`, `gpmc,cycle2cycle-delay-ns`, `gpmc,clk-activation-ns`, and 22 more. Required top-level properties are `reg`. Important reusable or nested constraints are: referenced schemas: `/schemas/types.yaml#/definitions/uint32`; non-compatible enum/const values include `0`, `4`, `8`, `16`, `1`, `2`. The highest-risk contract area is compatible fallback ordering, register and interrupt resources, address/size cell layout, bus ranges, child-node regexes, timing properties, clocks, resets, and interconnect/IOMMU links.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this schema and any `$ref` targets, then `dtbs_check` matches real DTS nodes by `compatible`, `$nodename`, or inclusion from a parent schema. Validation checks required properties, array lengths and constants, applies no top-level conditionals, descends into pattern-matched child nodes, and finally enforces `additionalProperties` or `unevaluatedProperties`. Runtime flow starts only after the DTB is loaded: Linux driver core or MFD population uses the compatible and resources to bind drivers.

## State and Persistence Behavior
The YAML file stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: property names, compatible fallback order, address-cell layout, child-node names, and example nodes become contracts shipped in source DTS files and compiled DTBs. Runtime state is owned by the matched kernel drivers after probe, including controller probe state, bus decoding configuration, timing tables, ECC/error reporting, and child-device enumeration.

## Dependencies and Integration Points
Maintainers listed: Tony Lindgren <tony@atomide.com>, Roger Quadros <rogerq@kernel.org>. Schema dependencies include `/schemas/types.yaml#/definitions/uint32`. Integration points include Linux memory-controller, EDAC, devfreq, interconnect, syscon/regmap, MTD/NAND/NOR, and external-bus child-device probing paths. The binding also participates in Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to compatible fallback ordering, register and interrupt resources, address/size cell layout, bus ranges, child-node regexes, timing properties, clocks, resets, and interconnect/IOMMU links, mismatch between documented compatibles and the driver's match table, resource ordering or cell-count mistakes that pass review but break probe, permissive extra properties that can hide spelling errors unless a parent/child schema catches them, lack of embedded examples, leaving coverage dependent on in-tree DTS users. This schema permits additional top-level properties so it can be layered with device-specific child bindings. Because these bindings describe hardware contracts, regressions can appear as boot-time probe failures, missing child devices, invalid timing/ECC configuration, or dtbs_check noise across unrelated boards.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/memory-controllers/ti,gpmc-child.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/memory-controllers/ti,gpmc-child.yaml` against boards that instantiate the binding. There are no embedded examples, so representative DTS users and schema-only validation carry the coverage. Also compare compatible strings with in-tree driver `of_match_table` entries and review DTS examples for register tuple counts, interrupt names, clocks/resets, address ranges, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/ti,gpmc-child.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/ti,gpmc.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/ti,gpmc.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/ti,gpmc.yaml` defines the memory-controller or external-bus binding titled `Texas Instruments GPMC Memory Controller`. The GPMC is a unified memory controller dedicated for interfacing with external memory devices like - Asynchronous SRAM-like memories and ASICs - Asynchronous, synchronous, and page mode burst NOR flash - NAND flash - Pseudo-SRAM devices It is a Linux devicetree YAML schema that constrains source DTS/DTB hardware descriptions before the corresponding kernel drivers consume the nodes.

## Important APIs, Types, and Functions
The exported API is the devicetree ABI, not callable functions. `compatible` uses an ordered compatible/fallback `items` sequence with 6 tokens: `ti,am3352-gpmc`, `ti,am64-gpmc`, `ti,omap2420-gpmc`, `ti,omap2430-gpmc`, `ti,omap3430-gpmc`, `ti,omap4430-gpmc`. Top-level properties are `compatible`, `reg`, `reg-names`, `interrupts`, `clocks`, `clock-names`, `power-domains`, `dmas`, `dma-names`, `#address-cells`, `#size-cells`, `gpmc,num-cs`, `gpmc,num-waitpins`, `ranges`, `#interrupt-cells`, `interrupt-controller`, `#gpio-cells`, `gpio-controller`, `ti,hwmods`, `ti,no-idle-on-init`. Required top-level properties are `compatible`, `reg`, `gpmc,num-cs`, `gpmc,num-waitpins`, `#address-cells`, `#size-cells`. Important reusable or nested constraints are: composition/conditionals: `allOf`; child-node patterns: `@[0-7],[a-f0-9]+$`; referenced schemas: `/schemas/types.yaml#/definitions/string`, `/schemas/types.yaml#/definitions/uint32`, `ti,gpmc-child.yaml`. The highest-risk contract area is compatible fallback ordering, register and interrupt resources, address/size cell layout, bus ranges, child-node regexes, timing properties, clocks, resets, and interconnect/IOMMU links.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this schema and any `$ref` targets, then `dtbs_check` matches real DTS nodes by `compatible`, `$nodename`, or inclusion from a parent schema. Validation checks required properties, array lengths and constants, applies `allOf`, descends into pattern-matched child nodes, and finally enforces `additionalProperties` or `unevaluatedProperties`. Runtime flow starts only after the DTB is loaded: Linux driver core or MFD population uses the compatible and resources to bind drivers.

## State and Persistence Behavior
The YAML file stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: property names, compatible fallback order, address-cell layout, child-node names, and example nodes become contracts shipped in source DTS files and compiled DTBs. Runtime state is owned by the matched kernel drivers after probe, including controller probe state, bus decoding configuration, timing tables, ECC/error reporting, and child-device enumeration.

## Dependencies and Integration Points
Maintainers listed: Tony Lindgren <tony@atomide.com>, Roger Quadros <rogerq@kernel.org>. Schema dependencies include `/schemas/types.yaml#/definitions/string`, `/schemas/types.yaml#/definitions/uint32`, `ti,gpmc-child.yaml`. Integration points include Linux memory-controller, EDAC, devfreq, interconnect, syscon/regmap, MTD/NAND/NOR, and external-bus child-device probing paths. The binding also participates in Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to compatible fallback ordering, register and interrupt resources, address/size cell layout, bus ranges, child-node regexes, timing properties, clocks, resets, and interconnect/IOMMU links, mismatch between documented compatibles and the driver's match table, resource ordering or cell-count mistakes that pass review but break probe, conditional branches that accept one SoC or chip variant while silently rejecting another, child-node regexes that over-match unrelated children or under-match valid bus devices. This schema rejects unknown top-level properties with `additionalProperties: false`. Because these bindings describe hardware contracts, regressions can appear as boot-time probe failures, missing child devices, invalid timing/ECC configuration, or dtbs_check noise across unrelated boards.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/memory-controllers/ti,gpmc.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/memory-controllers/ti,gpmc.yaml` against boards that instantiate the binding. The schema includes 1 embedded example; keep those examples compiling under `dt_binding_check`. Exercise child-node validation for `@[0-7],[a-f0-9]+$`. Also compare compatible strings with in-tree driver `of_match_table` entries and review DTS examples for register tuple counts, interrupt names, clocks/resets, address ranges, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/ti,gpmc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/xlnx,versal-ddrmc-edac.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/xlnx,versal-ddrmc-edac.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/xlnx,versal-ddrmc-edac.yaml` defines the memory-controller or external-bus binding titled `Xilinx Versal DDRMC (Integrated DDR Memory Controller)`. The integrated DDR Memory Controllers (DDRMCs) support both DDR4 and LPDDR4/ 4X memory interfaces. It is a Linux devicetree YAML schema that constrains source DTS/DTB hardware descriptions before the corresponding kernel drivers consume the nodes.

## Important APIs, Types, and Functions
The exported API is the devicetree ABI, not callable functions. `compatible` uses a single `const` token with 1 token: `xlnx,versal-ddrmc`. Top-level properties are `compatible`, `reg`, `reg-names`, `interrupts`. Required top-level properties are `compatible`, `reg`, `reg-names`, `interrupts`. Important reusable or nested constraints are: no unusually complex local constraints beyond the top-level properties. The highest-risk contract area is compatible fallback ordering, register and interrupt resources, address/size cell layout, bus ranges, child-node regexes, timing properties, clocks, resets, and interconnect/IOMMU links.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this schema and any `$ref` targets, then `dtbs_check` matches real DTS nodes by `compatible`, `$nodename`, or inclusion from a parent schema. Validation checks required properties, array lengths and constants, applies no top-level conditionals, descends into pattern-matched child nodes, and finally enforces `additionalProperties` or `unevaluatedProperties`. Runtime flow starts only after the DTB is loaded: Linux driver core or MFD population uses the compatible and resources to bind drivers.

## State and Persistence Behavior
The YAML file stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: property names, compatible fallback order, address-cell layout, child-node names, and example nodes become contracts shipped in source DTS files and compiled DTBs. Runtime state is owned by the matched kernel drivers after probe, including controller probe state, bus decoding configuration, timing tables, ECC/error reporting, and child-device enumeration.

## Dependencies and Integration Points
Maintainers listed: Shubhrajyoti Datta <shubhrajyoti.datta@amd.com>, Sai Krishna Potthuri <sai.krishna.potthuri@amd.com>. Schema dependencies include dt-schema core/meta schemas only. Integration points include Linux memory-controller, EDAC, devfreq, interconnect, syscon/regmap, MTD/NAND/NOR, and external-bus child-device probing paths. The binding also participates in Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to compatible fallback ordering, register and interrupt resources, address/size cell layout, bus ranges, child-node regexes, timing properties, clocks, resets, and interconnect/IOMMU links, mismatch between documented compatibles and the driver's match table, resource ordering or cell-count mistakes that pass review but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Because these bindings describe hardware contracts, regressions can appear as boot-time probe failures, missing child devices, invalid timing/ECC configuration, or dtbs_check noise across unrelated boards.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/memory-controllers/xlnx,versal-ddrmc-edac.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/memory-controllers/xlnx,versal-ddrmc-edac.yaml` against boards that instantiate the binding. The schema includes 1 embedded example; keep those examples compiling under `dt_binding_check`. Also compare compatible strings with in-tree driver `of_match_table` entries and review DTS examples for register tuple counts, interrupt names, clocks/resets, address ranges, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/xlnx,versal-ddrmc-edac.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/xlnx,versal-net-ddrmc5.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/xlnx,versal-net-ddrmc5.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/xlnx,versal-net-ddrmc5.yaml` defines the memory-controller or external-bus binding titled `Xilinx Versal NET Memory Controller`. The integrated DDR Memory Controllers (DDRMCs) support both DDR5 and LPDDR5 compact and extended memory interfaces. It is a Linux devicetree YAML schema that constrains source DTS/DTB hardware descriptions before the corresponding kernel drivers consume the nodes.

## Important APIs, Types, and Functions
The exported API is the devicetree ABI, not callable functions. `compatible` uses a single `const` token with 1 token: `xlnx,versal-net-ddrmc5`. Top-level properties are `compatible`, `amd,rproc`. Required top-level properties are `compatible`, `amd,rproc`. Important reusable or nested constraints are: referenced schemas: `/schemas/types.yaml#/definitions/phandle`. The highest-risk contract area is compatible fallback ordering, register and interrupt resources, address/size cell layout, bus ranges, child-node regexes, timing properties, clocks, resets, and interconnect/IOMMU links.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this schema and any `$ref` targets, then `dtbs_check` matches real DTS nodes by `compatible`, `$nodename`, or inclusion from a parent schema. Validation checks required properties, array lengths and constants, applies no top-level conditionals, descends into pattern-matched child nodes, and finally enforces `additionalProperties` or `unevaluatedProperties`. Runtime flow starts only after the DTB is loaded: Linux driver core or MFD population uses the compatible and resources to bind drivers.

## State and Persistence Behavior
The YAML file stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: property names, compatible fallback order, address-cell layout, child-node names, and example nodes become contracts shipped in source DTS files and compiled DTBs. Runtime state is owned by the matched kernel drivers after probe, including controller probe state, bus decoding configuration, timing tables, ECC/error reporting, and child-device enumeration.

## Dependencies and Integration Points
Maintainers listed: Shubhrajyoti Datta <shubhrajyoti.datta@amd.com>. Schema dependencies include `/schemas/types.yaml#/definitions/phandle`. Integration points include Linux memory-controller, EDAC, devfreq, interconnect, syscon/regmap, MTD/NAND/NOR, and external-bus child-device probing paths. The binding also participates in Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to compatible fallback ordering, register and interrupt resources, address/size cell layout, bus ranges, child-node regexes, timing properties, clocks, resets, and interconnect/IOMMU links, mismatch between documented compatibles and the driver's match table, resource ordering or cell-count mistakes that pass review but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Because these bindings describe hardware contracts, regressions can appear as boot-time probe failures, missing child devices, invalid timing/ECC configuration, or dtbs_check noise across unrelated boards.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/memory-controllers/xlnx,versal-net-ddrmc5.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/memory-controllers/xlnx,versal-net-ddrmc5.yaml` against boards that instantiate the binding. The schema includes 1 embedded example; keep those examples compiling under `dt_binding_check`. Also compare compatible strings with in-tree driver `of_match_table` entries and review DTS examples for register tuple counts, interrupt names, clocks/resets, address ranges, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/xlnx,versal-net-ddrmc5.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/xlnx,zynq-ddrc-a05.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/xlnx,zynq-ddrc-a05.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/xlnx,zynq-ddrc-a05.yaml` defines the memory-controller or external-bus binding titled `Zynq A05 DDR Memory Controller`. The Zynq DDR ECC controller has an optional ECC support in half-bus width (16-bit) configuration. It is a Linux devicetree YAML schema that constrains source DTS/DTB hardware descriptions before the corresponding kernel drivers consume the nodes.

## Important APIs, Types, and Functions
The exported API is the devicetree ABI, not callable functions. `compatible` uses a single `const` token with 1 token: `xlnx,zynq-ddrc-a05`. Top-level properties are `compatible`, `reg`. Required top-level properties are `compatible`, `reg`. Important reusable or nested constraints are: no unusually complex local constraints beyond the top-level properties. The highest-risk contract area is compatible fallback ordering, register and interrupt resources, address/size cell layout, bus ranges, child-node regexes, timing properties, clocks, resets, and interconnect/IOMMU links.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this schema and any `$ref` targets, then `dtbs_check` matches real DTS nodes by `compatible`, `$nodename`, or inclusion from a parent schema. Validation checks required properties, array lengths and constants, applies no top-level conditionals, descends into pattern-matched child nodes, and finally enforces `additionalProperties` or `unevaluatedProperties`. Runtime flow starts only after the DTB is loaded: Linux driver core or MFD population uses the compatible and resources to bind drivers.

## State and Persistence Behavior
The YAML file stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: property names, compatible fallback order, address-cell layout, child-node names, and example nodes become contracts shipped in source DTS files and compiled DTBs. Runtime state is owned by the matched kernel drivers after probe, including controller probe state, bus decoding configuration, timing tables, ECC/error reporting, and child-device enumeration.

## Dependencies and Integration Points
Maintainers listed: Krzysztof Kozlowski <krzk@kernel.org>, Michal Simek <michal.simek@amd.com>. Schema dependencies include dt-schema core/meta schemas only. Integration points include Linux memory-controller, EDAC, devfreq, interconnect, syscon/regmap, MTD/NAND/NOR, and external-bus child-device probing paths. The binding also participates in Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to compatible fallback ordering, register and interrupt resources, address/size cell layout, bus ranges, child-node regexes, timing properties, clocks, resets, and interconnect/IOMMU links, mismatch between documented compatibles and the driver's match table, resource ordering or cell-count mistakes that pass review but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Because these bindings describe hardware contracts, regressions can appear as boot-time probe failures, missing child devices, invalid timing/ECC configuration, or dtbs_check noise across unrelated boards.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/memory-controllers/xlnx,zynq-ddrc-a05.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/memory-controllers/xlnx,zynq-ddrc-a05.yaml` against boards that instantiate the binding. The schema includes 1 embedded example; keep those examples compiling under `dt_binding_check`. Also compare compatible strings with in-tree driver `of_match_table` entries and review DTS examples for register tuple counts, interrupt names, clocks/resets, address ranges, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/xlnx,zynq-ddrc-a05.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/xlnx,zynqmp-ocmc-1.0.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/xlnx,zynqmp-ocmc-1.0.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/xlnx,zynqmp-ocmc-1.0.yaml` defines the memory-controller or external-bus binding titled `Xilinx Zynqmp OCM(On-Chip Memory) Controller`. The OCM supports 64-bit wide ECC functionality to detect multi-bit errors and recover from a single-bit memory fault.On a write, if all bytes are being written, the ECC is generated and written into the ECC RAM along with the write-data that is written into the data RAM. It is a Linux devicetree YAML schema that constrains source DTS/DTB hardware descriptions before the corresponding kernel drivers consume the nodes.

## Important APIs, Types, and Functions
The exported API is the devicetree ABI, not callable functions. `compatible` uses a single `const` token with 1 token: `xlnx,zynqmp-ocmc-1.0`. Top-level properties are `compatible`, `reg`, `interrupts`. Required top-level properties are `compatible`, `reg`, `interrupts`. Important reusable or nested constraints are: no unusually complex local constraints beyond the top-level properties. The highest-risk contract area is compatible fallback ordering, register and interrupt resources, address/size cell layout, bus ranges, child-node regexes, timing properties, clocks, resets, and interconnect/IOMMU links.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this schema and any `$ref` targets, then `dtbs_check` matches real DTS nodes by `compatible`, `$nodename`, or inclusion from a parent schema. Validation checks required properties, array lengths and constants, applies no top-level conditionals, descends into pattern-matched child nodes, and finally enforces `additionalProperties` or `unevaluatedProperties`. Runtime flow starts only after the DTB is loaded: Linux driver core or MFD population uses the compatible and resources to bind drivers.

## State and Persistence Behavior
The YAML file stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: property names, compatible fallback order, address-cell layout, child-node names, and example nodes become contracts shipped in source DTS files and compiled DTBs. Runtime state is owned by the matched kernel drivers after probe, including controller probe state, bus decoding configuration, timing tables, ECC/error reporting, and child-device enumeration.

## Dependencies and Integration Points
Maintainers listed: Shubhrajyoti Datta <shubhrajyoti.datta@amd.com>, Sai Krishna Potthuri <sai.krishna.potthuri@amd.com>. Schema dependencies include dt-schema core/meta schemas only. Integration points include Linux memory-controller, EDAC, devfreq, interconnect, syscon/regmap, MTD/NAND/NOR, and external-bus child-device probing paths. The binding also participates in Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to compatible fallback ordering, register and interrupt resources, address/size cell layout, bus ranges, child-node regexes, timing properties, clocks, resets, and interconnect/IOMMU links, mismatch between documented compatibles and the driver's match table, resource ordering or cell-count mistakes that pass review but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Because these bindings describe hardware contracts, regressions can appear as boot-time probe failures, missing child devices, invalid timing/ECC configuration, or dtbs_check noise across unrelated boards.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/memory-controllers/xlnx,zynqmp-ocmc-1.0.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/memory-controllers/xlnx,zynqmp-ocmc-1.0.yaml` against boards that instantiate the binding. The schema includes 1 embedded example; keep those examples compiling under `dt_binding_check`. Also compare compatible strings with in-tree driver `of_match_table` entries and review DTS examples for register tuple counts, interrupt names, clocks/resets, address ranges, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/memory-controllers/xlnx,zynqmp-ocmc-1.0.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/actions,atc260x.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/actions,atc260x.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/actions,atc260x.yaml` defines the MFD or system-controller binding titled `Actions Semi ATC260x Power Management IC`. ATC260x series PMICs integrates Audio Codec, Power Management, RTC, IR and GPIO controller blocks. It is a Linux devicetree YAML schema that constrains source DTS/DTB hardware descriptions before the corresponding kernel drivers consume the nodes.

## Important APIs, Types, and Functions
The exported API is the devicetree ABI, not callable functions. `compatible` uses an `enum` of supported tokens with 2 tokens: `actions,atc2603c`, `actions,atc2609a`. Top-level properties are `compatible`, `reg`, `interrupts`, `reset-time-sec`, `regulators`. Required top-level properties are `compatible`, `reg`, `interrupts`. Important reusable or nested constraints are: composition/conditionals: `allOf`; referenced schemas: `/schemas/input/input.yaml`, `/schemas/regulator/regulator.yaml`; non-compatible enum/const values include `0`, `6`, `8`, `10`, `12`, `actions,atc2603c-regulator`, `actions,atc2609a-regulator`. The highest-risk contract area is parent compatible strings, register windows, interrupt wiring, child-node schemas, regulator or functional subnode names, clock/reset cell counts, and `simple-mfd`/`syscon` fallback ordering.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this schema and any `$ref` targets, then `dtbs_check` matches real DTS nodes by `compatible`, `$nodename`, or inclusion from a parent schema. Validation checks required properties, array lengths and constants, applies `allOf`, descends into pattern-matched child nodes, and finally enforces `additionalProperties` or `unevaluatedProperties`. Runtime flow starts only after the DTB is loaded: Linux driver core or MFD population uses the compatible and resources to bind drivers.

## State and Persistence Behavior
The YAML file stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: property names, compatible fallback order, address-cell layout, child-node names, and example nodes become contracts shipped in source DTS files and compiled DTBs. Runtime state is owned by the matched kernel drivers after probe, including parent regmap lifetime, child-device population, IRQ domains, regulator state, GPIO/pinctrl state, clock/reset providers, and subdriver probe ordering.

## Dependencies and Integration Points
Maintainers listed: Manivannan Sadhasivam <manivannan.sadhasivam@linaro.org>, Cristian Ciocaltea <cristian.ciocaltea@gmail.com>. Schema dependencies include `/schemas/input/input.yaml`, `/schemas/regulator/regulator.yaml`. Integration points include the Linux MFD core, regmap/syscon, I2C/platform/SPI instantiation, child device creation, GPIO/pinctrl/clock/reset/regulator/RTC/PWM/input/display subdrivers, and board DTS nodes. The binding also participates in Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to parent compatible strings, register windows, interrupt wiring, child-node schemas, regulator or functional subnode names, clock/reset cell counts, and `simple-mfd`/`syscon` fallback ordering, mismatch between documented compatibles and the driver's match table, resource ordering or cell-count mistakes that pass review but break probe, conditional branches that accept one SoC or chip variant while silently rejecting another. This schema rejects unknown top-level properties with `additionalProperties: false`. Because these bindings describe hardware contracts, regressions can appear as boot-time probe failures, missing child devices, invalid timing/ECC configuration, or dtbs_check noise across unrelated boards.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mfd/actions,atc260x.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mfd/actions,atc260x.yaml` against boards that instantiate the binding. The schema includes 1 embedded example; keep those examples compiling under `dt_binding_check`. Also compare compatible strings with in-tree driver `of_match_table` entries and review DTS examples for register tuple counts, interrupt names, clocks/resets, address ranges, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/actions,atc260x.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/adi,adp5585.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/adi,adp5585.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/adi,adp5585.yaml` defines the MFD or system-controller binding titled `Analog Devices ADP5585 Keypad Decoder and I/O Expansion`. The ADP5585 is a 10/11 input/output port expander with a built in keypad matrix decoder, programmable logic, reset generator, and PWM generator. It is a Linux devicetree YAML schema that constrains source DTS/DTB hardware descriptions before the corresponding kernel drivers consume the nodes.

## Important APIs, Types, and Functions
The exported API is the devicetree ABI, not callable functions. `compatible` uses `oneOf` with 2 branches with 10 tokens: `adi,adp5585-00`, `adi,adp5585-01`, `adi,adp5585-02`, `adi,adp5585-03`, `adi,adp5585-04`, `adi,adp5585`, `adi,adp5589-00`, `adi,adp5589-01`, `adi,adp5589-02`, `adi,adp5589`. Top-level properties are `compatible`, `reg`, `interrupts`, `vdd-supply`, `reset-gpios`, `gpio-controller`, `#gpio-cells`, `gpio-reserved-ranges`, `#pwm-cells`, `interrupt-controller`, `#interrupt-cells`, `poll-interval`, `adi,keypad-pins`, `adi,unlock-events`, `adi,unlock-trigger-sec`, `adi,reset1-events`, `adi,reset2-events`, `adi,reset1-active-high`, `adi,reset2-active-high`, `adi,rst-passthrough-enable`, `adi,reset-trigger-ms`, `adi,reset-pulse-width-us`. Required top-level properties are `compatible`, `reg`. Important reusable or nested constraints are: composition/conditionals: `allOf`, `dependencies`; child-node patterns: `-hog(-[0-9]+)?$`; referenced schemas: `/schemas/input/input.yaml#`, `/schemas/input/matrix-keymap.yaml#`, `/schemas/types.yaml#/definitions/uint32-array`; child-node API keys include `gpio-hog`; non-compatible enum/const values include `10`, `20`, `30`, `40`, `0`, `1000`, `1500`, `2000`, `2500`, `3000`, and 21 more. The highest-risk contract area is parent compatible strings, register windows, interrupt wiring, child-node schemas, regulator or functional subnode names, clock/reset cell counts, and `simple-mfd`/`syscon` fallback ordering.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this schema and any `$ref` targets, then `dtbs_check` matches real DTS nodes by `compatible`, `$nodename`, or inclusion from a parent schema. Validation checks required properties, array lengths and constants, applies `allOf`, `dependencies`, descends into pattern-matched child nodes, and finally enforces `additionalProperties` or `unevaluatedProperties`. Runtime flow starts only after the DTB is loaded: Linux driver core or MFD population uses the compatible and resources to bind drivers.

## State and Persistence Behavior
The YAML file stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: property names, compatible fallback order, address-cell layout, child-node names, and example nodes become contracts shipped in source DTS files and compiled DTBs. Runtime state is owned by the matched kernel drivers after probe, including parent regmap lifetime, child-device population, IRQ domains, regulator state, GPIO/pinctrl state, clock/reset providers, and subdriver probe ordering.

## Dependencies and Integration Points
Maintainers listed: Laurent Pinchart <laurent.pinchart@ideasonboard.com>. Schema dependencies include `/schemas/input/input.yaml#`, `/schemas/input/matrix-keymap.yaml#`, `/schemas/types.yaml#/definitions/uint32-array`. Integration points include the Linux MFD core, regmap/syscon, I2C/platform/SPI instantiation, child device creation, GPIO/pinctrl/clock/reset/regulator/RTC/PWM/input/display subdrivers, and board DTS nodes. The binding also participates in Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to parent compatible strings, register windows, interrupt wiring, child-node schemas, regulator or functional subnode names, clock/reset cell counts, and `simple-mfd`/`syscon` fallback ordering, mismatch between documented compatibles and the driver's match table, resource ordering or cell-count mistakes that pass review but break probe, conditional branches that accept one SoC or chip variant while silently rejecting another, child-node regexes that over-match unrelated children or under-match valid bus devices. This schema closes composed schemas with `unevaluatedProperties: false`. Because these bindings describe hardware contracts, regressions can appear as boot-time probe failures, missing child devices, invalid timing/ECC configuration, or dtbs_check noise across unrelated boards.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mfd/adi,adp5585.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mfd/adi,adp5585.yaml` against boards that instantiate the binding. The schema includes 1 embedded example; keep those examples compiling under `dt_binding_check`. Exercise child-node validation for `-hog(-[0-9]+)?$`. Also compare compatible strings with in-tree driver `of_match_table` entries and review DTS examples for register tuple counts, interrupt names, clocks/resets, address ranges, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/adi,adp5585.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/adi,max77541.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/adi,max77541.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/adi,max77541.yaml` defines the MFD or system-controller binding titled `MAX77540/MAX77541 PMIC from ADI`. MAX77540 is a Power Management IC with 2 buck regulators. It is a Linux devicetree YAML schema that constrains source DTS/DTB hardware descriptions before the corresponding kernel drivers consume the nodes.

## Important APIs, Types, and Functions
The exported API is the devicetree ABI, not callable functions. `compatible` uses an `enum` of supported tokens with 2 tokens: `adi,max77540`, `adi,max77541`. Top-level properties are `compatible`, `reg`, `interrupts`, `regulators`. Required top-level properties are `compatible`, `reg`, `interrupts`. Important reusable or nested constraints are: referenced schemas: `/schemas/regulator/adi,max77541-regulator.yaml#`. The highest-risk contract area is parent compatible strings, register windows, interrupt wiring, child-node schemas, regulator or functional subnode names, clock/reset cell counts, and `simple-mfd`/`syscon` fallback ordering.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this schema and any `$ref` targets, then `dtbs_check` matches real DTS nodes by `compatible`, `$nodename`, or inclusion from a parent schema. Validation checks required properties, array lengths and constants, applies no top-level conditionals, descends into pattern-matched child nodes, and finally enforces `additionalProperties` or `unevaluatedProperties`. Runtime flow starts only after the DTB is loaded: Linux driver core or MFD population uses the compatible and resources to bind drivers.

## State and Persistence Behavior
The YAML file stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: property names, compatible fallback order, address-cell layout, child-node names, and example nodes become contracts shipped in source DTS files and compiled DTBs. Runtime state is owned by the matched kernel drivers after probe, including parent regmap lifetime, child-device population, IRQ domains, regulator state, GPIO/pinctrl state, clock/reset providers, and subdriver probe ordering.

## Dependencies and Integration Points
Maintainers listed: Okan Sahin <okan.sahin@analog.com>. Schema dependencies include `/schemas/regulator/adi,max77541-regulator.yaml#`. Integration points include the Linux MFD core, regmap/syscon, I2C/platform/SPI instantiation, child device creation, GPIO/pinctrl/clock/reset/regulator/RTC/PWM/input/display subdrivers, and board DTS nodes. The binding also participates in Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to parent compatible strings, register windows, interrupt wiring, child-node schemas, regulator or functional subnode names, clock/reset cell counts, and `simple-mfd`/`syscon` fallback ordering, mismatch between documented compatibles and the driver's match table, resource ordering or cell-count mistakes that pass review but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Because these bindings describe hardware contracts, regressions can appear as boot-time probe failures, missing child devices, invalid timing/ECC configuration, or dtbs_check noise across unrelated boards.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mfd/adi,max77541.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mfd/adi,max77541.yaml` against boards that instantiate the binding. The schema includes 1 embedded example; keep those examples compiling under `dt_binding_check`. Also compare compatible strings with in-tree driver `of_match_table` entries and review DTS examples for register tuple counts, interrupt names, clocks/resets, address ranges, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/adi,max77541.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/airoha,en7581-gpio-sysctl.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/airoha,en7581-gpio-sysctl.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/airoha,en7581-gpio-sysctl.yaml` defines the MFD or system-controller binding titled `Airoha EN7581 GPIO System Controller`. Airoha EN7581 SoC GPIO system controller which provided a register map for controlling the GPIO, pins and PWM of the SoC. It is a Linux devicetree YAML schema that constrains source DTS/DTB hardware descriptions before the corresponding kernel drivers consume the nodes.

## Important APIs, Types, and Functions
The exported API is the devicetree ABI, not callable functions. `compatible` uses an ordered compatible/fallback `items` sequence with 3 tokens: `airoha,en7581-gpio-sysctl`, `syscon`, `simple-mfd`. Top-level properties are `compatible`, `reg`, `pinctrl`, `pwm`. Required top-level properties are `compatible`, `reg`. Important reusable or nested constraints are: referenced schemas: `/schemas/pinctrl/airoha,en7581-pinctrl.yaml`, `/schemas/pwm/airoha,en7581-pwm.yaml`. The highest-risk contract area is parent compatible strings, register windows, interrupt wiring, child-node schemas, regulator or functional subnode names, clock/reset cell counts, and `simple-mfd`/`syscon` fallback ordering.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this schema and any `$ref` targets, then `dtbs_check` matches real DTS nodes by `compatible`, `$nodename`, or inclusion from a parent schema. Validation checks required properties, array lengths and constants, applies no top-level conditionals, descends into pattern-matched child nodes, and finally enforces `additionalProperties` or `unevaluatedProperties`. Runtime flow starts only after the DTB is loaded: Linux driver core or MFD population uses the compatible and resources to bind drivers.

## State and Persistence Behavior
The YAML file stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: property names, compatible fallback order, address-cell layout, child-node names, and example nodes become contracts shipped in source DTS files and compiled DTBs. Runtime state is owned by the matched kernel drivers after probe, including parent regmap lifetime, child-device population, IRQ domains, regulator state, GPIO/pinctrl state, clock/reset providers, and subdriver probe ordering.

## Dependencies and Integration Points
Maintainers listed: Christian Marangi <ansuelsmth@gmail.com>, Lorenzo Bianconi <lorenzo@kernel.org>. Schema dependencies include `/schemas/pinctrl/airoha,en7581-pinctrl.yaml`, `/schemas/pwm/airoha,en7581-pwm.yaml`. Integration points include the Linux MFD core, regmap/syscon, I2C/platform/SPI instantiation, child device creation, GPIO/pinctrl/clock/reset/regulator/RTC/PWM/input/display subdrivers, and board DTS nodes. The binding also participates in Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to parent compatible strings, register windows, interrupt wiring, child-node schemas, regulator or functional subnode names, clock/reset cell counts, and `simple-mfd`/`syscon` fallback ordering, mismatch between documented compatibles and the driver's match table, resource ordering or cell-count mistakes that pass review but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Because these bindings describe hardware contracts, regressions can appear as boot-time probe failures, missing child devices, invalid timing/ECC configuration, or dtbs_check noise across unrelated boards.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mfd/airoha,en7581-gpio-sysctl.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mfd/airoha,en7581-gpio-sysctl.yaml` against boards that instantiate the binding. The schema includes 1 embedded example; keep those examples compiling under `dt_binding_check`. Also compare compatible strings with in-tree driver `of_match_table` entries and review DTS examples for register tuple counts, interrupt names, clocks/resets, address ranges, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/airoha,en7581-gpio-sysctl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/allwinner,sun4i-a10-ts.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/allwinner,sun4i-a10-ts.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/allwinner,sun4i-a10-ts.yaml` defines the MFD or system-controller binding titled `Allwinner A10 Resistive Touchscreen Controller`. It constrains devicetree nodes through compatible strings, required resources, bus topology, and shared schema references before the corresponding Linux subsystem uses the node at probe time.

## Important APIs, Types, and Functions
The exported API is the devicetree ABI, not callable functions. `compatible` uses an `enum` of supported tokens with 3 tokens: `allwinner,sun4i-a10-ts`, `allwinner,sun5i-a13-ts`, `allwinner,sun6i-a31-ts`. Top-level properties are `#thermal-sensor-cells`, `compatible`, `reg`, `interrupts`, `allwinner,ts-attached`, `allwinner,tp-sensitive-adjust`, `allwinner,filter-type`. Required top-level properties are `#thermal-sensor-cells`, `compatible`, `reg`, `interrupts`. Important reusable or nested constraints are: referenced schemas: `/schemas/types.yaml#/definitions/flag`, `/schemas/types.yaml#/definitions/uint32`. The highest-risk contract area is parent compatible strings, register windows, interrupt wiring, child-node schemas, regulator or functional subnode names, clock/reset cell counts, and `simple-mfd`/`syscon` fallback ordering.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this schema and any `$ref` targets, then `dtbs_check` matches real DTS nodes by `compatible`, `$nodename`, or inclusion from a parent schema. Validation checks required properties, array lengths and constants, applies no top-level conditionals, descends into pattern-matched child nodes, and finally enforces `additionalProperties` or `unevaluatedProperties`. Runtime flow starts only after the DTB is loaded: Linux driver core or MFD population uses the compatible and resources to bind drivers.

## State and Persistence Behavior
The YAML file stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: property names, compatible fallback order, address-cell layout, child-node names, and example nodes become contracts shipped in source DTS files and compiled DTBs. Runtime state is owned by the matched kernel drivers after probe, including parent regmap lifetime, child-device population, IRQ domains, regulator state, GPIO/pinctrl state, clock/reset providers, and subdriver probe ordering.

## Dependencies and Integration Points
Maintainers listed: Chen-Yu Tsai <wens@csie.org>, Maxime Ripard <mripard@kernel.org>. Schema dependencies include `/schemas/types.yaml#/definitions/flag`, `/schemas/types.yaml#/definitions/uint32`. Integration points include the Linux MFD core, regmap/syscon, I2C/platform/SPI instantiation, child device creation, GPIO/pinctrl/clock/reset/regulator/RTC/PWM/input/display subdrivers, and board DTS nodes. The binding also participates in Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to parent compatible strings, register windows, interrupt wiring, child-node schemas, regulator or functional subnode names, clock/reset cell counts, and `simple-mfd`/`syscon` fallback ordering, mismatch between documented compatibles and the driver's match table, resource ordering or cell-count mistakes that pass review but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Because these bindings describe hardware contracts, regressions can appear as boot-time probe failures, missing child devices, invalid timing/ECC configuration, or dtbs_check noise across unrelated boards.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mfd/allwinner,sun4i-a10-ts.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mfd/allwinner,sun4i-a10-ts.yaml` against boards that instantiate the binding. The schema includes 1 embedded example; keep those examples compiling under `dt_binding_check`. Also compare compatible strings with in-tree driver `of_match_table` entries and review DTS examples for register tuple counts, interrupt names, clocks/resets, address ranges, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/allwinner,sun4i-a10-ts.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/allwinner,sun6i-a31-prcm.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/allwinner,sun6i-a31-prcm.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/allwinner,sun6i-a31-prcm.yaml` defines the MFD or system-controller binding titled `Allwinner A31 PRCM`. It constrains devicetree nodes through compatible strings, required resources, bus topology, and shared schema references before the corresponding Linux subsystem uses the node at probe time.

## Important APIs, Types, and Functions
The exported API is the devicetree ABI, not callable functions. `compatible` uses a single `const` token with 1 token: `allwinner,sun6i-a31-prcm`. Top-level properties are `compatible`, `reg`. Required top-level properties are `compatible`, `reg`. Important reusable or nested constraints are: child-node patterns: `^.*-(clk|rst)$`; referenced schemas: `/schemas/clock/fixed-factor-clock.yaml#`; child-node API keys include `compatible`; non-compatible enum/const values include `allwinner,sun4i-a10-mod0-clk`, `allwinner,sun6i-a31-apb0-clk`, `allwinner,sun6i-a31-apb0-gates-clk`, `allwinner,sun6i-a31-ar100-clk`, `allwinner,sun6i-a31-clock-reset`, `fixed-factor-clock`. The highest-risk contract area is parent compatible strings, register windows, interrupt wiring, child-node schemas, regulator or functional subnode names, clock/reset cell counts, and `simple-mfd`/`syscon` fallback ordering.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this schema and any `$ref` targets, then `dtbs_check` matches real DTS nodes by `compatible`, `$nodename`, or inclusion from a parent schema. Validation checks required properties, array lengths and constants, applies no top-level conditionals, descends into pattern-matched child nodes, and finally enforces `additionalProperties` or `unevaluatedProperties`. Runtime flow starts only after the DTB is loaded: Linux driver core or MFD population uses the compatible and resources to bind drivers.

## State and Persistence Behavior
The YAML file stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: property names, compatible fallback order, address-cell layout, child-node names, and example nodes become contracts shipped in source DTS files and compiled DTBs. Runtime state is owned by the matched kernel drivers after probe, including parent regmap lifetime, child-device population, IRQ domains, regulator state, GPIO/pinctrl state, clock/reset providers, and subdriver probe ordering.

## Dependencies and Integration Points
Maintainers listed: Chen-Yu Tsai <wens@csie.org>, Maxime Ripard <mripard@kernel.org>. Schema dependencies include `/schemas/clock/fixed-factor-clock.yaml#`. Integration points include the Linux MFD core, regmap/syscon, I2C/platform/SPI instantiation, child device creation, GPIO/pinctrl/clock/reset/regulator/RTC/PWM/input/display subdrivers, and board DTS nodes. The binding also participates in Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to parent compatible strings, register windows, interrupt wiring, child-node schemas, regulator or functional subnode names, clock/reset cell counts, and `simple-mfd`/`syscon` fallback ordering, mismatch between documented compatibles and the driver's match table, resource ordering or cell-count mistakes that pass review but break probe, child-node regexes that over-match unrelated children or under-match valid bus devices. This schema rejects unknown top-level properties with `additionalProperties: false`. Because these bindings describe hardware contracts, regressions can appear as boot-time probe failures, missing child devices, invalid timing/ECC configuration, or dtbs_check noise across unrelated boards.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mfd/allwinner,sun6i-a31-prcm.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mfd/allwinner,sun6i-a31-prcm.yaml` against boards that instantiate the binding. The schema includes 1 embedded example; keep those examples compiling under `dt_binding_check`. Exercise child-node validation for `^.*-(clk|rst)$`. Also compare compatible strings with in-tree driver `of_match_table` entries and review DTS examples for register tuple counts, interrupt names, clocks/resets, address ranges, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/allwinner,sun6i-a31-prcm.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/allwinner,sun8i-a23-prcm.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/allwinner,sun8i-a23-prcm.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/allwinner,sun8i-a23-prcm.yaml` defines the MFD or system-controller binding titled `Allwinner A23 PRCM`. It constrains devicetree nodes through compatible strings, required resources, bus topology, and shared schema references before the corresponding Linux subsystem uses the node at probe time.

## Important APIs, Types, and Functions
The exported API is the devicetree ABI, not callable functions. `compatible` uses a single `const` token with 1 token: `allwinner,sun8i-a23-prcm`. Top-level properties are `compatible`, `reg`. Required top-level properties are `compatible`, `reg`. Important reusable or nested constraints are: child-node patterns: `^.*(clk|rst|codec).*$`; referenced schemas: `/schemas/clock/fixed-factor-clock.yaml#`; child-node API keys include `compatible`; non-compatible enum/const values include `fixed-factor-clock`, `allwinner,sun8i-a23-apb0-clk`, `allwinner,sun8i-a23-apb0-gates-clk`, `allwinner,sun6i-a31-clock-reset`, `allwinner,sun8i-a23-codec-analog`. The highest-risk contract area is parent compatible strings, register windows, interrupt wiring, child-node schemas, regulator or functional subnode names, clock/reset cell counts, and `simple-mfd`/`syscon` fallback ordering.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this schema and any `$ref` targets, then `dtbs_check` matches real DTS nodes by `compatible`, `$nodename`, or inclusion from a parent schema. Validation checks required properties, array lengths and constants, applies no top-level conditionals, descends into pattern-matched child nodes, and finally enforces `additionalProperties` or `unevaluatedProperties`. Runtime flow starts only after the DTB is loaded: Linux driver core or MFD population uses the compatible and resources to bind drivers.

## State and Persistence Behavior
The YAML file stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: property names, compatible fallback order, address-cell layout, child-node names, and example nodes become contracts shipped in source DTS files and compiled DTBs. Runtime state is owned by the matched kernel drivers after probe, including parent regmap lifetime, child-device population, IRQ domains, regulator state, GPIO/pinctrl state, clock/reset providers, and subdriver probe ordering.

## Dependencies and Integration Points
Maintainers listed: Chen-Yu Tsai <wens@csie.org>, Maxime Ripard <mripard@kernel.org>. Schema dependencies include `/schemas/clock/fixed-factor-clock.yaml#`. Integration points include the Linux MFD core, regmap/syscon, I2C/platform/SPI instantiation, child device creation, GPIO/pinctrl/clock/reset/regulator/RTC/PWM/input/display subdrivers, and board DTS nodes. The binding also participates in Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to parent compatible strings, register windows, interrupt wiring, child-node schemas, regulator or functional subnode names, clock/reset cell counts, and `simple-mfd`/`syscon` fallback ordering, mismatch between documented compatibles and the driver's match table, resource ordering or cell-count mistakes that pass review but break probe, child-node regexes that over-match unrelated children or under-match valid bus devices. This schema rejects unknown top-level properties with `additionalProperties: false`. Because these bindings describe hardware contracts, regressions can appear as boot-time probe failures, missing child devices, invalid timing/ECC configuration, or dtbs_check noise across unrelated boards.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mfd/allwinner,sun8i-a23-prcm.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mfd/allwinner,sun8i-a23-prcm.yaml` against boards that instantiate the binding. The schema includes 1 embedded example; keep those examples compiling under `dt_binding_check`. Exercise child-node validation for `^.*(clk|rst|codec).*$`. Also compare compatible strings with in-tree driver `of_match_table` entries and review DTS examples for register tuple counts, interrupt names, clocks/resets, address ranges, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/allwinner,sun8i-a23-prcm.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/ampere,smpro.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/ampere,smpro.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/ampere,smpro.yaml` defines the MFD or system-controller binding titled `Ampere Altra SMPro firmware driver`. Ampere Altra SMPro firmware may contain different blocks like hardware monitoring, error monitoring and other miscellaneous features. It is a Linux devicetree YAML schema that constrains source DTS/DTB hardware descriptions before the corresponding kernel drivers consume the nodes.

## Important APIs, Types, and Functions
The exported API is the devicetree ABI, not callable functions. `compatible` uses an `enum` of supported tokens with 1 token: `ampere,smpro`. Top-level properties are `compatible`, `reg`. Required top-level properties are `compatible`, `reg`. Important reusable or nested constraints are: no unusually complex local constraints beyond the top-level properties. The highest-risk contract area is parent compatible strings, register windows, interrupt wiring, child-node schemas, regulator or functional subnode names, clock/reset cell counts, and `simple-mfd`/`syscon` fallback ordering.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this schema and any `$ref` targets, then `dtbs_check` matches real DTS nodes by `compatible`, `$nodename`, or inclusion from a parent schema. Validation checks required properties, array lengths and constants, applies no top-level conditionals, descends into pattern-matched child nodes, and finally enforces `additionalProperties` or `unevaluatedProperties`. Runtime flow starts only after the DTB is loaded: Linux driver core or MFD population uses the compatible and resources to bind drivers.

## State and Persistence Behavior
The YAML file stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: property names, compatible fallback order, address-cell layout, child-node names, and example nodes become contracts shipped in source DTS files and compiled DTBs. Runtime state is owned by the matched kernel drivers after probe, including parent regmap lifetime, child-device population, IRQ domains, regulator state, GPIO/pinctrl state, clock/reset providers, and subdriver probe ordering.

## Dependencies and Integration Points
Maintainers listed: Quan Nguyen <quan@os.amperecomputing.com>. Schema dependencies include dt-schema core/meta schemas only. Integration points include the Linux MFD core, regmap/syscon, I2C/platform/SPI instantiation, child device creation, GPIO/pinctrl/clock/reset/regulator/RTC/PWM/input/display subdrivers, and board DTS nodes. The binding also participates in Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to parent compatible strings, register windows, interrupt wiring, child-node schemas, regulator or functional subnode names, clock/reset cell counts, and `simple-mfd`/`syscon` fallback ordering, mismatch between documented compatibles and the driver's match table, resource ordering or cell-count mistakes that pass review but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Because these bindings describe hardware contracts, regressions can appear as boot-time probe failures, missing child devices, invalid timing/ECC configuration, or dtbs_check noise across unrelated boards.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mfd/ampere,smpro.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mfd/ampere,smpro.yaml` against boards that instantiate the binding. The schema includes 1 embedded example; keep those examples compiling under `dt_binding_check`. Also compare compatible strings with in-tree driver `of_match_table` entries and review DTS examples for register tuple counts, interrupt names, clocks/resets, address ranges, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/ampere,smpro.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/ams,as3711.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/ams,as3711.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/ams,as3711.yaml` defines the MFD or system-controller binding titled `Austria MicroSystems AS3711 Quad Buck High Current PMIC with Charger`. AS3711 is an I2C PMIC from Austria MicroSystems with multiple DC/DC and LDO power supplies, a battery charger and an RTC. It is a Linux devicetree YAML schema that constrains source DTS/DTB hardware descriptions before the corresponding kernel drivers consume the nodes.

## Important APIs, Types, and Functions
The exported API is the devicetree ABI, not callable functions. `compatible` uses a single `const` token with 1 token: `ams,as3711`. Top-level properties are `compatible`, `reg`, `backlight`, `regulators`. Required top-level properties are `compatible`, `reg`. Important reusable or nested constraints are: referenced schemas: `/schemas/regulator/regulator.yaml#`, `/schemas/types.yaml#/definitions/phandle`, `/schemas/types.yaml#/definitions/uint32`. The highest-risk contract area is parent compatible strings, register windows, interrupt wiring, child-node schemas, regulator or functional subnode names, clock/reset cell counts, and `simple-mfd`/`syscon` fallback ordering.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this schema and any `$ref` targets, then `dtbs_check` matches real DTS nodes by `compatible`, `$nodename`, or inclusion from a parent schema. Validation checks required properties, array lengths and constants, applies no top-level conditionals, descends into pattern-matched child nodes, and finally enforces `additionalProperties` or `unevaluatedProperties`. Runtime flow starts only after the DTB is loaded: Linux driver core or MFD population uses the compatible and resources to bind drivers.

## State and Persistence Behavior
The YAML file stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: property names, compatible fallback order, address-cell layout, child-node names, and example nodes become contracts shipped in source DTS files and compiled DTBs. Runtime state is owned by the matched kernel drivers after probe, including parent regmap lifetime, child-device population, IRQ domains, regulator state, GPIO/pinctrl state, clock/reset providers, and subdriver probe ordering.

## Dependencies and Integration Points
Maintainers listed: Guennadi Liakhovetski <guennadi.liakhovetski@linux.intel.com>. Schema dependencies include `/schemas/regulator/regulator.yaml#`, `/schemas/types.yaml#/definitions/phandle`, `/schemas/types.yaml#/definitions/uint32`. Integration points include the Linux MFD core, regmap/syscon, I2C/platform/SPI instantiation, child device creation, GPIO/pinctrl/clock/reset/regulator/RTC/PWM/input/display subdrivers, and board DTS nodes. The binding also participates in Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to parent compatible strings, register windows, interrupt wiring, child-node schemas, regulator or functional subnode names, clock/reset cell counts, and `simple-mfd`/`syscon` fallback ordering, mismatch between documented compatibles and the driver's match table, resource ordering or cell-count mistakes that pass review but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Because these bindings describe hardware contracts, regressions can appear as boot-time probe failures, missing child devices, invalid timing/ECC configuration, or dtbs_check noise across unrelated boards.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mfd/ams,as3711.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mfd/ams,as3711.yaml` against boards that instantiate the binding. The schema includes 1 embedded example; keep those examples compiling under `dt_binding_check`. Also compare compatible strings with in-tree driver `of_match_table` entries and review DTS examples for register tuple counts, interrupt names, clocks/resets, address ranges, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/ams,as3711.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/apple,smc.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/apple,smc.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/apple,smc.yaml` defines the MFD or system-controller binding titled `Apple Mac System Management Controller`. Apple Mac System Management Controller implements various functions such as GPIO, RTC, power, reboot. It is a Linux devicetree YAML schema that constrains source DTS/DTB hardware descriptions before the corresponding kernel drivers consume the nodes.

## Important APIs, Types, and Functions
The exported API is the devicetree ABI, not callable functions. `compatible` uses `oneOf` with 2 branches with 5 tokens: `apple,t6020-smc`, `apple,t8103-smc`, `apple,t6000-smc`, `apple,t8112-smc`, `apple,smc`. Top-level properties are `compatible`, `reg`, `reg-names`, `mboxes`, `gpio`, `reboot`, `rtc`. Required top-level properties are `compatible`, `reg`, `reg-names`, `mboxes`. Important reusable or nested constraints are: referenced schemas: `/schemas/gpio/apple,smc-gpio.yaml`, `/schemas/power/reset/apple,smc-reboot.yaml`, `/schemas/rtc/apple,smc-rtc.yaml`. The highest-risk contract area is parent compatible strings, register windows, interrupt wiring, child-node schemas, regulator or functional subnode names, clock/reset cell counts, and `simple-mfd`/`syscon` fallback ordering.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this schema and any `$ref` targets, then `dtbs_check` matches real DTS nodes by `compatible`, `$nodename`, or inclusion from a parent schema. Validation checks required properties, array lengths and constants, applies no top-level conditionals, descends into pattern-matched child nodes, and finally enforces `additionalProperties` or `unevaluatedProperties`. Runtime flow starts only after the DTB is loaded: Linux driver core or MFD population uses the compatible and resources to bind drivers.

## State and Persistence Behavior
The YAML file stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: property names, compatible fallback order, address-cell layout, child-node names, and example nodes become contracts shipped in source DTS files and compiled DTBs. Runtime state is owned by the matched kernel drivers after probe, including parent regmap lifetime, child-device population, IRQ domains, regulator state, GPIO/pinctrl state, clock/reset providers, and subdriver probe ordering.

## Dependencies and Integration Points
Maintainers listed: Sven Peter <sven@kernel.org>. Schema dependencies include `/schemas/gpio/apple,smc-gpio.yaml`, `/schemas/power/reset/apple,smc-reboot.yaml`, `/schemas/rtc/apple,smc-rtc.yaml`. Integration points include the Linux MFD core, regmap/syscon, I2C/platform/SPI instantiation, child device creation, GPIO/pinctrl/clock/reset/regulator/RTC/PWM/input/display subdrivers, and board DTS nodes. The binding also participates in Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to parent compatible strings, register windows, interrupt wiring, child-node schemas, regulator or functional subnode names, clock/reset cell counts, and `simple-mfd`/`syscon` fallback ordering, mismatch between documented compatibles and the driver's match table, resource ordering or cell-count mistakes that pass review but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Because these bindings describe hardware contracts, regressions can appear as boot-time probe failures, missing child devices, invalid timing/ECC configuration, or dtbs_check noise across unrelated boards.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mfd/apple,smc.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mfd/apple,smc.yaml` against boards that instantiate the binding. The schema includes 1 embedded example; keep those examples compiling under `dt_binding_check`. Also compare compatible strings with in-tree driver `of_match_table` entries and review DTS examples for register tuple counts, interrupt names, clocks/resets, address ranges, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/apple,smc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/arm,dev-platforms-syscon.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/arm,dev-platforms-syscon.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/arm,dev-platforms-syscon.yaml` defines the MFD or system-controller binding titled `Arm Ltd Developer Platforms System Controllers`. The Arm Ltd Integrator, Realview, and Versatile families of developer platforms are contain various system controller blocks. It is a Linux devicetree YAML schema that constrains source DTS/DTB hardware descriptions before the corresponding kernel drivers consume the nodes.

## Important APIs, Types, and Functions
The exported API is the devicetree ABI, not callable functions. `compatible` uses `oneOf` with 3 branches with 15 tokens: `arm,integrator-ap-syscon`, `arm,integrator-cp-syscon`, `arm,integrator-sp-syscon`, `arm,im-pd1-syscon`, `syscon`, `arm,core-module-integrator`, `arm,realview-eb-syscon`, `arm,realview-pb1176-syscon`, `arm,realview-pb11mp-syscon`, `arm,realview-pba8-syscon`, `arm,realview-pbx-syscon`, `arm,versatile-ib2-syscon`, `simple-mfd`, `arm,realview-eb11mp-revb-syscon`, `arm,realview-eb11mp-revc-syscon`. Top-level properties are `compatible`, `reg`, `ranges`, `#address-cells`, `#size-cells`. Required top-level properties are `compatible`, `reg`. Important reusable or nested constraints are: no unusually complex local constraints beyond the top-level properties. The highest-risk contract area is parent compatible strings, register windows, interrupt wiring, child-node schemas, regulator or functional subnode names, clock/reset cell counts, and `simple-mfd`/`syscon` fallback ordering.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this schema and any `$ref` targets, then `dtbs_check` matches real DTS nodes by `compatible`, `$nodename`, or inclusion from a parent schema. Validation checks required properties, array lengths and constants, applies no top-level conditionals, descends into pattern-matched child nodes, and finally enforces `additionalProperties` or `unevaluatedProperties`. Runtime flow starts only after the DTB is loaded: Linux driver core or MFD population uses the compatible and resources to bind drivers.

## State and Persistence Behavior
The YAML file stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: property names, compatible fallback order, address-cell layout, child-node names, and example nodes become contracts shipped in source DTS files and compiled DTBs. Runtime state is owned by the matched kernel drivers after probe, including parent regmap lifetime, child-device population, IRQ domains, regulator state, GPIO/pinctrl state, clock/reset providers, and subdriver probe ordering.

## Dependencies and Integration Points
Maintainers listed: Linus Walleij <linusw@kernel.org>. Schema dependencies include dt-schema core/meta schemas only. Integration points include the Linux MFD core, regmap/syscon, I2C/platform/SPI instantiation, child device creation, GPIO/pinctrl/clock/reset/regulator/RTC/PWM/input/display subdrivers, and board DTS nodes. The binding also participates in Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to parent compatible strings, register windows, interrupt wiring, child-node schemas, regulator or functional subnode names, clock/reset cell counts, and `simple-mfd`/`syscon` fallback ordering, mismatch between documented compatibles and the driver's match table, resource ordering or cell-count mistakes that pass review but break probe, large compatible sets where fallback ordering can drift across SoC generations, lack of embedded examples, leaving coverage dependent on in-tree DTS users. This schema allows additional properties only if they match the supplied object schema. Because these bindings describe hardware contracts, regressions can appear as boot-time probe failures, missing child devices, invalid timing/ECC configuration, or dtbs_check noise across unrelated boards.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mfd/arm,dev-platforms-syscon.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mfd/arm,dev-platforms-syscon.yaml` against boards that instantiate the binding. There are no embedded examples, so representative DTS users and schema-only validation carry the coverage. Also compare compatible strings with in-tree driver `of_match_table` entries and review DTS examples for register tuple counts, interrupt names, clocks/resets, address ranges, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/arm,dev-platforms-syscon.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/aspeed,ast2x00-scu.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/aspeed,ast2x00-scu.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/aspeed,ast2x00-scu.yaml` defines the MFD or system-controller binding titled `Aspeed System Control Unit`. The Aspeed System Control Unit manages the global behaviour of the SoC, configuring elements such as clocks, pinmux, and reset. It is a Linux devicetree YAML schema that constrains source DTS/DTB hardware descriptions before the corresponding kernel drivers consume the nodes.

## Important APIs, Types, and Functions
The exported API is the devicetree ABI, not callable functions. `compatible` uses an ordered compatible/fallback `items` sequence with 7 tokens: `aspeed,ast2400-scu`, `aspeed,ast2500-scu`, `aspeed,ast2600-scu`, `aspeed,ast2700-scu0`, `aspeed,ast2700-scu1`, `syscon`, `simple-mfd`. Top-level properties are `compatible`, `reg`, `ranges`, `#address-cells`, `#size-cells`, `#clock-cells`, `#reset-cells`. Required top-level properties are `compatible`, `reg`, `ranges`, `#address-cells`, `#size-cells`, `#clock-cells`, `#reset-cells`. Important reusable or nested constraints are: child-node patterns: `^p2a-control@[0-9a-f]+$`, `^pinctrl(@[0-9a-f]+)?$`, `^interrupt-controller@[0-9a-f]+$`, `^silicon-id@[0-9a-f]+$`, `^smp-memram@[0-9a-f]+$`; child-node API keys include `compatible`, `reg`, `memory-region`; non-compatible enum/const values include `aspeed,ast2400-p2a-ctrl`, `aspeed,ast2500-p2a-ctrl`, `aspeed,ast2400-pinctrl`, `aspeed,ast2500-pinctrl`, `aspeed,ast2600-pinctrl`, `aspeed,ast2500-scu-ic`, `aspeed,ast2600-scu-ic0`, `aspeed,ast2600-scu-ic1`, `aspeed,ast2700-scu-ic0`, `aspeed,ast2700-scu-ic1`, and 6 more. The highest-risk contract area is parent compatible strings, register windows, interrupt wiring, child-node schemas, regulator or functional subnode names, clock/reset cell counts, and `simple-mfd`/`syscon` fallback ordering.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this schema and any `$ref` targets, then `dtbs_check` matches real DTS nodes by `compatible`, `$nodename`, or inclusion from a parent schema. Validation checks required properties, array lengths and constants, applies no top-level conditionals, descends into pattern-matched child nodes, and finally enforces `additionalProperties` or `unevaluatedProperties`. Runtime flow starts only after the DTB is loaded: Linux driver core or MFD population uses the compatible and resources to bind drivers.

## State and Persistence Behavior
The YAML file stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: property names, compatible fallback order, address-cell layout, child-node names, and example nodes become contracts shipped in source DTS files and compiled DTBs. Runtime state is owned by the matched kernel drivers after probe, including parent regmap lifetime, child-device population, IRQ domains, regulator state, GPIO/pinctrl state, clock/reset providers, and subdriver probe ordering.

## Dependencies and Integration Points
Maintainers listed: Joel Stanley <joel@jms.id.au>, Andrew Jeffery <andrew@aj.id.au>. Schema dependencies include dt-schema core/meta schemas only. Integration points include the Linux MFD core, regmap/syscon, I2C/platform/SPI instantiation, child device creation, GPIO/pinctrl/clock/reset/regulator/RTC/PWM/input/display subdrivers, and board DTS nodes. The binding also participates in Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to parent compatible strings, register windows, interrupt wiring, child-node schemas, regulator or functional subnode names, clock/reset cell counts, and `simple-mfd`/`syscon` fallback ordering, mismatch between documented compatibles and the driver's match table, resource ordering or cell-count mistakes that pass review but break probe, child-node regexes that over-match unrelated children or under-match valid bus devices. This schema rejects unknown top-level properties with `additionalProperties: false`. Because these bindings describe hardware contracts, regressions can appear as boot-time probe failures, missing child devices, invalid timing/ECC configuration, or dtbs_check noise across unrelated boards.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mfd/aspeed,ast2x00-scu.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mfd/aspeed,ast2x00-scu.yaml` against boards that instantiate the binding. The schema includes 1 embedded example; keep those examples compiling under `dt_binding_check`. Exercise child-node validation for `^p2a-control@[0-9a-f]+$`, `^pinctrl(@[0-9a-f]+)?$`, `^interrupt-controller@[0-9a-f]+$`, `^silicon-id@[0-9a-f]+$`, `^smp-memram@[0-9a-f]+$`. Also compare compatible strings with in-tree driver `of_match_table` entries and review DTS examples for register tuple counts, interrupt names, clocks/resets, address ranges, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/aspeed,ast2x00-scu.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/aspeed-lpc.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/aspeed-lpc.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/aspeed-lpc.yaml` defines the MFD or system-controller binding titled `Aspeed Low Pin Count (LPC) Bus Controller`. The LPC bus is a means to bridge a host CPU to a number of low-bandwidth peripheral devices, replacing the use of the ISA bus in the age of PCI[0]. It is a Linux devicetree YAML schema that constrains source DTS/DTB hardware descriptions before the corresponding kernel drivers consume the nodes.

## Important APIs, Types, and Functions
The exported API is the devicetree ABI, not callable functions. `compatible` uses an ordered compatible/fallback `items` sequence with 5 tokens: `aspeed,ast2400-lpc-v2`, `aspeed,ast2500-lpc-v2`, `aspeed,ast2600-lpc-v2`, `simple-mfd`, `syscon`. Top-level properties are `compatible`, `reg`, `#address-cells`, `#size-cells`, `ranges`. Required top-level properties are `compatible`, `reg`, `#address-cells`, `#size-cells`, `ranges`. Important reusable or nested constraints are: child-node patterns: `^lpc-ctrl@[0-9a-f]+$`, `^reset-controller@[0-9a-f]+$`, `^lpc-snoop@[0-9a-f]+$`, `^uart-routing@[0-9a-f]+$`; referenced schemas: `/schemas/soc/aspeed/uart-routing.yaml#`, `/schemas/types.yaml#/definitions/phandle`, `/schemas/types.yaml#/definitions/uint32-array`; child-node API keys include `compatible`, `clocks`, `reg`, `memory-region`, `flash`, `#reset-cells`, `interrupts`, `snoop-ports`; non-compatible enum/const values include `aspeed,ast2400-lpc-ctrl`, `aspeed,ast2500-lpc-ctrl`, `aspeed,ast2600-lpc-ctrl`, `aspeed,ast2400-lpc-reset`, `aspeed,ast2500-lpc-reset`, `aspeed,ast2600-lpc-reset`, `aspeed,ast2400-lpc-snoop`, `aspeed,ast2500-lpc-snoop`, `aspeed,ast2600-lpc-snoop`. The highest-risk contract area is parent compatible strings, register windows, interrupt wiring, child-node schemas, regulator or functional subnode names, clock/reset cell counts, and `simple-mfd`/`syscon` fallback ordering.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this schema and any `$ref` targets, then `dtbs_check` matches real DTS nodes by `compatible`, `$nodename`, or inclusion from a parent schema. Validation checks required properties, array lengths and constants, applies no top-level conditionals, descends into pattern-matched child nodes, and finally enforces `additionalProperties` or `unevaluatedProperties`. Runtime flow starts only after the DTB is loaded: Linux driver core or MFD population uses the compatible and resources to bind drivers.

## State and Persistence Behavior
The YAML file stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: property names, compatible fallback order, address-cell layout, child-node names, and example nodes become contracts shipped in source DTS files and compiled DTBs. Runtime state is owned by the matched kernel drivers after probe, including parent regmap lifetime, child-device population, IRQ domains, regulator state, GPIO/pinctrl state, clock/reset providers, and subdriver probe ordering.

## Dependencies and Integration Points
Maintainers listed: Andrew Jeffery <andrew@aj.id.au>, Chia-Wei Wang <chiawei_wang@aspeedtech.com>. Schema dependencies include `/schemas/soc/aspeed/uart-routing.yaml#`, `/schemas/types.yaml#/definitions/phandle`, `/schemas/types.yaml#/definitions/uint32-array`. Integration points include the Linux MFD core, regmap/syscon, I2C/platform/SPI instantiation, child device creation, GPIO/pinctrl/clock/reset/regulator/RTC/PWM/input/display subdrivers, and board DTS nodes. The binding also participates in Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to parent compatible strings, register windows, interrupt wiring, child-node schemas, regulator or functional subnode names, clock/reset cell counts, and `simple-mfd`/`syscon` fallback ordering, mismatch between documented compatibles and the driver's match table, resource ordering or cell-count mistakes that pass review but break probe, child-node regexes that over-match unrelated children or under-match valid bus devices. This schema allows additional properties only if they match the supplied object schema. Because these bindings describe hardware contracts, regressions can appear as boot-time probe failures, missing child devices, invalid timing/ECC configuration, or dtbs_check noise across unrelated boards.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mfd/aspeed-lpc.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mfd/aspeed-lpc.yaml` against boards that instantiate the binding. The schema includes 1 embedded example; keep those examples compiling under `dt_binding_check`. Exercise child-node validation for `^lpc-ctrl@[0-9a-f]+$`, `^reset-controller@[0-9a-f]+$`, `^lpc-snoop@[0-9a-f]+$`, `^uart-routing@[0-9a-f]+$`. Also compare compatible strings with in-tree driver `of_match_table` entries and review DTS examples for register tuple counts, interrupt names, clocks/resets, address ranges, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/aspeed-lpc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/atmel,at91sam9260-gpbr.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/atmel,at91sam9260-gpbr.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/atmel,at91sam9260-gpbr.yaml` defines the MFD or system-controller binding titled `Microchip AT91 General Purpose Backup Registers`. The system controller embeds 256 bits of General Purpose Backup registers organized as 8 32-bit registers. It is a Linux devicetree YAML schema that constrains source DTS/DTB hardware descriptions before the corresponding kernel drivers consume the nodes.

## Important APIs, Types, and Functions
The exported API is the devicetree ABI, not callable functions. `compatible` uses `oneOf` with 2 branches with 5 tokens: `atmel,at91sam9260-gpbr`, `microchip,sama7d65-gpbr`, `syscon`, `microchip,sam9x60-gpbr`, `microchip,sam9x7-gpbr`. Top-level properties are `compatible`, `reg`. Required top-level properties are `compatible`, `reg`. Important reusable or nested constraints are: no unusually complex local constraints beyond the top-level properties. The highest-risk contract area is parent compatible strings, register windows, interrupt wiring, child-node schemas, regulator or functional subnode names, clock/reset cell counts, and `simple-mfd`/`syscon` fallback ordering.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this schema and any `$ref` targets, then `dtbs_check` matches real DTS nodes by `compatible`, `$nodename`, or inclusion from a parent schema. Validation checks required properties, array lengths and constants, applies no top-level conditionals, descends into pattern-matched child nodes, and finally enforces `additionalProperties` or `unevaluatedProperties`. Runtime flow starts only after the DTB is loaded: Linux driver core or MFD population uses the compatible and resources to bind drivers.

## State and Persistence Behavior
The YAML file stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: property names, compatible fallback order, address-cell layout, child-node names, and example nodes become contracts shipped in source DTS files and compiled DTBs. Runtime state is owned by the matched kernel drivers after probe, including parent regmap lifetime, child-device population, IRQ domains, regulator state, GPIO/pinctrl state, clock/reset providers, and subdriver probe ordering.

## Dependencies and Integration Points
Maintainers listed: Nicolas Ferre <nicolas.ferre@microchip.com>. Schema dependencies include dt-schema core/meta schemas only. Integration points include the Linux MFD core, regmap/syscon, I2C/platform/SPI instantiation, child device creation, GPIO/pinctrl/clock/reset/regulator/RTC/PWM/input/display subdrivers, and board DTS nodes. The binding also participates in Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to parent compatible strings, register windows, interrupt wiring, child-node schemas, regulator or functional subnode names, clock/reset cell counts, and `simple-mfd`/`syscon` fallback ordering, mismatch between documented compatibles and the driver's match table, resource ordering or cell-count mistakes that pass review but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Because these bindings describe hardware contracts, regressions can appear as boot-time probe failures, missing child devices, invalid timing/ECC configuration, or dtbs_check noise across unrelated boards.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mfd/atmel,at91sam9260-gpbr.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mfd/atmel,at91sam9260-gpbr.yaml` against boards that instantiate the binding. The schema includes 1 embedded example; keep those examples compiling under `dt_binding_check`. Also compare compatible strings with in-tree driver `of_match_table` entries and review DTS examples for register tuple counts, interrupt names, clocks/resets, address ranges, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/atmel,at91sam9260-gpbr.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/atmel,at91sam9260-matrix.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/atmel,at91sam9260-matrix.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/atmel,at91sam9260-matrix.yaml` defines the MFD or system-controller binding titled `Microchip AT91 Bus Matrix`. The Bus Matrix (MATRIX) implements a multi-layer AHB, based on the AHB-Lite protocol, that enables parallel access paths between multiple masters and slaves in a system, thus increasing the overall bandwidth. It is a Linux devicetree YAML schema that constrains source DTS/DTB hardware descriptions before the corresponding kernel drivers consume the nodes.

## Important APIs, Types, and Functions
The exported API is the devicetree ABI, not callable functions. `compatible` uses `oneOf` with 2 branches with 11 tokens: `atmel,at91sam9260-matrix`, `atmel,at91sam9261-matrix`, `atmel,at91sam9263-matrix`, `atmel,at91sam9rl-matrix`, `atmel,at91sam9g45-matrix`, `atmel,at91sam9n12-matrix`, `atmel,at91sam9x5-matrix`, `atmel,sama5d3-matrix`, `syscon`, `microchip,sam9x60-matrix`, `microchip,sam9x7-matrix`. Top-level properties are `compatible`, `reg`. Required top-level properties are `compatible`, `reg`. Important reusable or nested constraints are: no unusually complex local constraints beyond the top-level properties. The highest-risk contract area is parent compatible strings, register windows, interrupt wiring, child-node schemas, regulator or functional subnode names, clock/reset cell counts, and `simple-mfd`/`syscon` fallback ordering.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this schema and any `$ref` targets, then `dtbs_check` matches real DTS nodes by `compatible`, `$nodename`, or inclusion from a parent schema. Validation checks required properties, array lengths and constants, applies no top-level conditionals, descends into pattern-matched child nodes, and finally enforces `additionalProperties` or `unevaluatedProperties`. Runtime flow starts only after the DTB is loaded: Linux driver core or MFD population uses the compatible and resources to bind drivers.

## State and Persistence Behavior
The YAML file stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: property names, compatible fallback order, address-cell layout, child-node names, and example nodes become contracts shipped in source DTS files and compiled DTBs. Runtime state is owned by the matched kernel drivers after probe, including parent regmap lifetime, child-device population, IRQ domains, regulator state, GPIO/pinctrl state, clock/reset providers, and subdriver probe ordering.

## Dependencies and Integration Points
Maintainers listed: Nicolas Ferre <nicolas.ferre@microchip.com>. Schema dependencies include dt-schema core/meta schemas only. Integration points include the Linux MFD core, regmap/syscon, I2C/platform/SPI instantiation, child device creation, GPIO/pinctrl/clock/reset/regulator/RTC/PWM/input/display subdrivers, and board DTS nodes. The binding also participates in Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to parent compatible strings, register windows, interrupt wiring, child-node schemas, regulator or functional subnode names, clock/reset cell counts, and `simple-mfd`/`syscon` fallback ordering, mismatch between documented compatibles and the driver's match table, resource ordering or cell-count mistakes that pass review but break probe, large compatible sets where fallback ordering can drift across SoC generations. This schema rejects unknown top-level properties with `additionalProperties: false`. Because these bindings describe hardware contracts, regressions can appear as boot-time probe failures, missing child devices, invalid timing/ECC configuration, or dtbs_check noise across unrelated boards.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mfd/atmel,at91sam9260-matrix.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mfd/atmel,at91sam9260-matrix.yaml` against boards that instantiate the binding. The schema includes 1 embedded example; keep those examples compiling under `dt_binding_check`. Also compare compatible strings with in-tree driver `of_match_table` entries and review DTS examples for register tuple counts, interrupt names, clocks/resets, address ranges, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/atmel,at91sam9260-matrix.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/atmel,hlcdc.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/atmel,hlcdc.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/atmel,hlcdc.yaml` defines the MFD or system-controller binding titled `Atmel's HLCD Controller`. The Atmel HLCDC (HLCD Controller) IP available on Atmel SoCs exposes two subdevices, a PWM chip and a Display Controller. It is a Linux devicetree YAML schema that constrains source DTS/DTB hardware descriptions before the corresponding kernel drivers consume the nodes.

## Important APIs, Types, and Functions
The exported API is the devicetree ABI, not callable functions. `compatible` uses an `enum` of supported tokens with 8 tokens: `atmel,at91sam9n12-hlcdc`, `atmel,at91sam9x5-hlcdc`, `atmel,sama5d2-hlcdc`, `atmel,sama5d3-hlcdc`, `atmel,sama5d4-hlcdc`, `microchip,sam9x60-hlcdc`, `microchip,sam9x75-xlcdc`, `microchip,sama7d65-xlcdc`. Top-level properties are `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `display-controller`, `pwm`. Required top-level properties are `compatible`, `reg`, `clocks`, `clock-names`, `interrupts`. Important reusable or nested constraints are: referenced schemas: `/schemas/display/atmel/atmel,hlcdc-display-controller.yaml`, `/schemas/pwm/atmel,hlcdc-pwm.yaml`. The highest-risk contract area is parent compatible strings, register windows, interrupt wiring, child-node schemas, regulator or functional subnode names, clock/reset cell counts, and `simple-mfd`/`syscon` fallback ordering.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this schema and any `$ref` targets, then `dtbs_check` matches real DTS nodes by `compatible`, `$nodename`, or inclusion from a parent schema. Validation checks required properties, array lengths and constants, applies no top-level conditionals, descends into pattern-matched child nodes, and finally enforces `additionalProperties` or `unevaluatedProperties`. Runtime flow starts only after the DTB is loaded: Linux driver core or MFD population uses the compatible and resources to bind drivers.

## State and Persistence Behavior
The YAML file stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: property names, compatible fallback order, address-cell layout, child-node names, and example nodes become contracts shipped in source DTS files and compiled DTBs. Runtime state is owned by the matched kernel drivers after probe, including parent regmap lifetime, child-device population, IRQ domains, regulator state, GPIO/pinctrl state, clock/reset providers, and subdriver probe ordering.

## Dependencies and Integration Points
Maintainers listed: Nicolas Ferre <nicolas.ferre@microchip.com>, Alexandre Belloni <alexandre.belloni@bootlin.com>, Claudiu Beznea <claudiu.beznea@tuxon.dev>. Schema dependencies include `/schemas/display/atmel/atmel,hlcdc-display-controller.yaml`, `/schemas/pwm/atmel,hlcdc-pwm.yaml`. Integration points include the Linux MFD core, regmap/syscon, I2C/platform/SPI instantiation, child device creation, GPIO/pinctrl/clock/reset/regulator/RTC/PWM/input/display subdrivers, and board DTS nodes. The binding also participates in Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to parent compatible strings, register windows, interrupt wiring, child-node schemas, regulator or functional subnode names, clock/reset cell counts, and `simple-mfd`/`syscon` fallback ordering, mismatch between documented compatibles and the driver's match table, resource ordering or cell-count mistakes that pass review but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Because these bindings describe hardware contracts, regressions can appear as boot-time probe failures, missing child devices, invalid timing/ECC configuration, or dtbs_check noise across unrelated boards.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mfd/atmel,hlcdc.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mfd/atmel,hlcdc.yaml` against boards that instantiate the binding. The schema includes 1 embedded example; keep those examples compiling under `dt_binding_check`. Also compare compatible strings with in-tree driver `of_match_table` entries and review DTS examples for register tuple counts, interrupt names, clocks/resets, address ranges, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/atmel,hlcdc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/atmel,sama5d2-flexcom.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/atmel,sama5d2-flexcom.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/atmel,sama5d2-flexcom.yaml` defines the MFD or system-controller binding titled `Microchip Flexcom (Flexible Serial Communication Unit)`. The Microchip Flexcom is just a wrapper which embeds a SPI controller, an I2C controller and an USART. It is a Linux devicetree YAML schema that constrains source DTS/DTB hardware descriptions before the corresponding kernel drivers consume the nodes.

## Important APIs, Types, and Functions
The exported API is the devicetree ABI, not callable functions. `compatible` uses `oneOf` with 2 branches with 5 tokens: `atmel,sama5d2-flexcom`, `microchip,lan9691-flexcom`, `microchip,sam9x7-flexcom`, `microchip,sama7d65-flexcom`, `microchip,sama7g5-flexcom`. Top-level properties are `compatible`, `reg`, `clocks`, `#address-cells`, `#size-cells`, `ranges`, `atmel,flexcom-mode`. Required top-level properties are `compatible`, `reg`, `clocks`, `#address-cells`, `#size-cells`, `ranges`, `atmel,flexcom-mode`. Important reusable or nested constraints are: child-node patterns: `^serial@[0-9a-f]+$`, `^spi@[0-9a-f]+$`, `^i2c@[0-9a-f]+$`; referenced schemas: `/schemas/i2c/atmel,at91sam-i2c.yaml`, `/schemas/types.yaml#/definitions/uint32`; non-compatible enum/const values include `1`, `2`, `3`. The highest-risk contract area is parent compatible strings, register windows, interrupt wiring, child-node schemas, regulator or functional subnode names, clock/reset cell counts, and `simple-mfd`/`syscon` fallback ordering.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this schema and any `$ref` targets, then `dtbs_check` matches real DTS nodes by `compatible`, `$nodename`, or inclusion from a parent schema. Validation checks required properties, array lengths and constants, applies no top-level conditionals, descends into pattern-matched child nodes, and finally enforces `additionalProperties` or `unevaluatedProperties`. Runtime flow starts only after the DTB is loaded: Linux driver core or MFD population uses the compatible and resources to bind drivers.

## State and Persistence Behavior
The YAML file stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: property names, compatible fallback order, address-cell layout, child-node names, and example nodes become contracts shipped in source DTS files and compiled DTBs. Runtime state is owned by the matched kernel drivers after probe, including parent regmap lifetime, child-device population, IRQ domains, regulator state, GPIO/pinctrl state, clock/reset providers, and subdriver probe ordering.

## Dependencies and Integration Points
Maintainers listed: Kavyasree Kotagiri <kavyasree.kotagiri@microchip.com>. Schema dependencies include `/schemas/i2c/atmel,at91sam-i2c.yaml`, `/schemas/types.yaml#/definitions/uint32`. Integration points include the Linux MFD core, regmap/syscon, I2C/platform/SPI instantiation, child device creation, GPIO/pinctrl/clock/reset/regulator/RTC/PWM/input/display subdrivers, and board DTS nodes. The binding also participates in Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to parent compatible strings, register windows, interrupt wiring, child-node schemas, regulator or functional subnode names, clock/reset cell counts, and `simple-mfd`/`syscon` fallback ordering, mismatch between documented compatibles and the driver's match table, resource ordering or cell-count mistakes that pass review but break probe, child-node regexes that over-match unrelated children or under-match valid bus devices. This schema rejects unknown top-level properties with `additionalProperties: false`. Because these bindings describe hardware contracts, regressions can appear as boot-time probe failures, missing child devices, invalid timing/ECC configuration, or dtbs_check noise across unrelated boards.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mfd/atmel,sama5d2-flexcom.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mfd/atmel,sama5d2-flexcom.yaml` against boards that instantiate the binding. The schema includes 1 embedded example; keep those examples compiling under `dt_binding_check`. Exercise child-node validation for `^serial@[0-9a-f]+$`, `^spi@[0-9a-f]+$`, `^i2c@[0-9a-f]+$`. Also compare compatible strings with in-tree driver `of_match_table` entries and review DTS examples for register tuple counts, interrupt names, clocks/resets, address ranges, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/atmel,sama5d2-flexcom.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/bitmain,bm1880-sctrl.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/bitmain,bm1880-sctrl.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/bitmain,bm1880-sctrl.yaml` defines the MFD or system-controller binding titled `Bitmain BM1880 System Controller`. It constrains devicetree nodes through compatible strings, required resources, bus topology, and shared schema references before the corresponding Linux subsystem uses the node at probe time.

## Important APIs, Types, and Functions
The exported API is the devicetree ABI, not callable functions. `compatible` uses an ordered compatible/fallback `items` sequence with 3 tokens: `bitmain,bm1880-sctrl`, `syscon`, `simple-mfd`. Top-level properties are `compatible`, `reg`, `ranges`, `#address-cells`, `#size-cells`. Required top-level properties are `compatible`, `reg`, `ranges`, `#address-cells`, `#size-cells`. Important reusable or nested constraints are: child-node patterns: `^pinctrl@[0-9a-f]+$`, `^clock-controller@[0-9a-f]+$`, `^reset-controller@[0-9a-f]+$`; child-node API keys include `compatible`. The highest-risk contract area is parent compatible strings, register windows, interrupt wiring, child-node schemas, regulator or functional subnode names, clock/reset cell counts, and `simple-mfd`/`syscon` fallback ordering.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this schema and any `$ref` targets, then `dtbs_check` matches real DTS nodes by `compatible`, `$nodename`, or inclusion from a parent schema. Validation checks required properties, array lengths and constants, applies no top-level conditionals, descends into pattern-matched child nodes, and finally enforces `additionalProperties` or `unevaluatedProperties`. Runtime flow starts only after the DTB is loaded: Linux driver core or MFD population uses the compatible and resources to bind drivers.

## State and Persistence Behavior
The YAML file stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: property names, compatible fallback order, address-cell layout, child-node names, and example nodes become contracts shipped in source DTS files and compiled DTBs. Runtime state is owned by the matched kernel drivers after probe, including parent regmap lifetime, child-device population, IRQ domains, regulator state, GPIO/pinctrl state, clock/reset providers, and subdriver probe ordering.

## Dependencies and Integration Points
Maintainers listed: Manivannan Sadhasivam <mani@kernel.org>. Schema dependencies include dt-schema core/meta schemas only. Integration points include the Linux MFD core, regmap/syscon, I2C/platform/SPI instantiation, child device creation, GPIO/pinctrl/clock/reset/regulator/RTC/PWM/input/display subdrivers, and board DTS nodes. The binding also participates in Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to parent compatible strings, register windows, interrupt wiring, child-node schemas, regulator or functional subnode names, clock/reset cell counts, and `simple-mfd`/`syscon` fallback ordering, mismatch between documented compatibles and the driver's match table, resource ordering or cell-count mistakes that pass review but break probe, child-node regexes that over-match unrelated children or under-match valid bus devices, lack of embedded examples, leaving coverage dependent on in-tree DTS users. This schema rejects unknown top-level properties with `additionalProperties: false`. Because these bindings describe hardware contracts, regressions can appear as boot-time probe failures, missing child devices, invalid timing/ECC configuration, or dtbs_check noise across unrelated boards.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mfd/bitmain,bm1880-sctrl.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mfd/bitmain,bm1880-sctrl.yaml` against boards that instantiate the binding. There are no embedded examples, so representative DTS users and schema-only validation carry the coverage. Exercise child-node validation for `^pinctrl@[0-9a-f]+$`, `^clock-controller@[0-9a-f]+$`, `^reset-controller@[0-9a-f]+$`. Also compare compatible strings with in-tree driver `of_match_table` entries and review DTS examples for register tuple counts, interrupt names, clocks/resets, address ranges, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/bitmain,bm1880-sctrl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/brcm,bcm59056.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/brcm,bcm59056.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/brcm,bcm59056.yaml` defines the MFD or system-controller binding titled `Broadcom BCM590xx Power Management Units`. It constrains devicetree nodes through compatible strings, required resources, bus topology, and shared schema references before the corresponding Linux subsystem uses the node at probe time.

## Important APIs, Types, and Functions
The exported API is the devicetree ABI, not callable functions. `compatible` uses an `enum` of supported tokens with 2 tokens: `brcm,bcm59054`, `brcm,bcm59056`. Top-level properties are `compatible`, `reg`, `interrupts`, `regulators`. Required top-level properties are `compatible`, `reg`, `interrupts`. Important reusable or nested constraints are: composition/conditionals: `allOf`; referenced schemas: `/schemas/regulator/brcm,bcm59054.yaml#`, `/schemas/regulator/brcm,bcm59056.yaml#`. The highest-risk contract area is parent compatible strings, register windows, interrupt wiring, child-node schemas, regulator or functional subnode names, clock/reset cell counts, and `simple-mfd`/`syscon` fallback ordering.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this schema and any `$ref` targets, then `dtbs_check` matches real DTS nodes by `compatible`, `$nodename`, or inclusion from a parent schema. Validation checks required properties, array lengths and constants, applies `allOf`, descends into pattern-matched child nodes, and finally enforces `additionalProperties` or `unevaluatedProperties`. Runtime flow starts only after the DTB is loaded: Linux driver core or MFD population uses the compatible and resources to bind drivers.

## State and Persistence Behavior
The YAML file stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: property names, compatible fallback order, address-cell layout, child-node names, and example nodes become contracts shipped in source DTS files and compiled DTBs. Runtime state is owned by the matched kernel drivers after probe, including parent regmap lifetime, child-device population, IRQ domains, regulator state, GPIO/pinctrl state, clock/reset providers, and subdriver probe ordering.

## Dependencies and Integration Points
Maintainers listed: Artur Weber <aweber.kernel@gmail.com>. Schema dependencies include `/schemas/regulator/brcm,bcm59054.yaml#`, `/schemas/regulator/brcm,bcm59056.yaml#`. Integration points include the Linux MFD core, regmap/syscon, I2C/platform/SPI instantiation, child device creation, GPIO/pinctrl/clock/reset/regulator/RTC/PWM/input/display subdrivers, and board DTS nodes. The binding also participates in Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to parent compatible strings, register windows, interrupt wiring, child-node schemas, regulator or functional subnode names, clock/reset cell counts, and `simple-mfd`/`syscon` fallback ordering, mismatch between documented compatibles and the driver's match table, resource ordering or cell-count mistakes that pass review but break probe, conditional branches that accept one SoC or chip variant while silently rejecting another. This schema rejects unknown top-level properties with `additionalProperties: false`. Because these bindings describe hardware contracts, regressions can appear as boot-time probe failures, missing child devices, invalid timing/ECC configuration, or dtbs_check noise across unrelated boards.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mfd/brcm,bcm59056.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mfd/brcm,bcm59056.yaml` against boards that instantiate the binding. The schema includes 1 embedded example; keep those examples compiling under `dt_binding_check`. Also compare compatible strings with in-tree driver `of_match_table` entries and review DTS examples for register tuple counts, interrupt names, clocks/resets, address ranges, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/brcm,bcm59056.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/brcm,bcm6318-gpio-sysctl.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/brcm,bcm6318-gpio-sysctl.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/brcm,bcm6318-gpio-sysctl.yaml` defines the MFD or system-controller binding titled `Broadcom BCM6318 GPIO System Controller`. Broadcom BCM6318 SoC GPIO system controller which provides a register map for controlling the GPIO and pins of the SoC. It is a Linux devicetree YAML schema that constrains source DTS/DTB hardware descriptions before the corresponding kernel drivers consume the nodes.

## Important APIs, Types, and Functions
The exported API is the devicetree ABI, not callable functions. `compatible` uses an ordered compatible/fallback `items` sequence with 3 tokens: `brcm,bcm6318-gpio-sysctl`, `syscon`, `simple-mfd`. Top-level properties are `#address-cells`, `#size-cells`, `compatible`, `ranges`, `reg`. Required top-level properties are `#address-cells`, `compatible`, `ranges`, `reg`, `#size-cells`. Important reusable or nested constraints are: child-node patterns: `^gpio@[0-9a-f]+$`, `^pinctrl@[0-9a-f]+$`; referenced schemas: `/schemas/gpio/brcm,bcm63xx-gpio.yaml`, `/schemas/pinctrl/brcm,bcm6318-pinctrl.yaml`. The highest-risk contract area is parent compatible strings, register windows, interrupt wiring, child-node schemas, regulator or functional subnode names, clock/reset cell counts, and `simple-mfd`/`syscon` fallback ordering.

## Control Flow
Control flow is declarative schema evaluation. `dt_binding_check` parses the YAML, validates embedded examples against this schema and any `$ref` targets, then `dtbs_check` matches real DTS nodes by `compatible`, `$nodename`, or inclusion from a parent schema. Validation checks required properties, array lengths and constants, applies no top-level conditionals, descends into pattern-matched child nodes, and finally enforces `additionalProperties` or `unevaluatedProperties`. Runtime flow starts only after the DTB is loaded: Linux driver core or MFD population uses the compatible and resources to bind drivers.

## State and Persistence Behavior
The YAML file stores no mutable runtime state and writes no persistent data. Its persistent behavior is ABI-level: property names, compatible fallback order, address-cell layout, child-node names, and example nodes become contracts shipped in source DTS files and compiled DTBs. Runtime state is owned by the matched kernel drivers after probe, including parent regmap lifetime, child-device population, IRQ domains, regulator state, GPIO/pinctrl state, clock/reset providers, and subdriver probe ordering.

## Dependencies and Integration Points
Maintainers listed: Álvaro Fernández Rojas <noltari@gmail.com>, Jonas Gorski <jonas.gorski@gmail.com>. Schema dependencies include `/schemas/gpio/brcm,bcm63xx-gpio.yaml`, `/schemas/pinctrl/brcm,bcm6318-pinctrl.yaml`. Integration points include the Linux MFD core, regmap/syscon, I2C/platform/SPI instantiation, child device creation, GPIO/pinctrl/clock/reset/regulator/RTC/PWM/input/display subdrivers, and board DTS nodes. The binding also participates in Linux `make dt_binding_check`, `make dtbs_check`, YAML example extraction, driver `of_match_table` review, and DTS board-file validation.

## Risks
Primary risks are incompatible ABI changes to parent compatible strings, register windows, interrupt wiring, child-node schemas, regulator or functional subnode names, clock/reset cell counts, and `simple-mfd`/`syscon` fallback ordering, mismatch between documented compatibles and the driver's match table, resource ordering or cell-count mistakes that pass review but break probe, child-node regexes that over-match unrelated children or under-match valid bus devices. This schema rejects unknown top-level properties with `additionalProperties: false`. Because these bindings describe hardware contracts, regressions can appear as boot-time probe failures, missing child devices, invalid timing/ECC configuration, or dtbs_check noise across unrelated boards.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mfd/brcm,bcm6318-gpio-sysctl.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mfd/brcm,bcm6318-gpio-sysctl.yaml` against boards that instantiate the binding. The schema includes 1 embedded example; keep those examples compiling under `dt_binding_check`. Exercise child-node validation for `^gpio@[0-9a-f]+$`, `^pinctrl@[0-9a-f]+$`. Also compare compatible strings with in-tree driver `of_match_table` entries and review DTS examples for register tuple counts, interrupt names, clocks/resets, address ranges, and phandle references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/brcm,bcm6318-gpio-sysctl.yaml -->
