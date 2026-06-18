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
