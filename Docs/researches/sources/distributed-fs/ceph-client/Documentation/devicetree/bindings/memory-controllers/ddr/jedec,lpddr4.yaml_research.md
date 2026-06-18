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
