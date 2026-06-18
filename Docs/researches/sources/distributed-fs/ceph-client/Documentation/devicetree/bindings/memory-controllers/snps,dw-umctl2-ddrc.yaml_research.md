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
