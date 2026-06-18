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
