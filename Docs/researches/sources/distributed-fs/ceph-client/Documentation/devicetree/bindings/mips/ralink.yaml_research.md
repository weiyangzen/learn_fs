<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mips/ralink.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mips/ralink.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mips/ralink.yaml` defines the MIPS platform or SoC binding titled `Ralink SoC based Platforms`. Boards with a Ralink SoC shall have the following properties. It is a Linux devicetree YAML schema used to validate hardware-description nodes before those nodes reach kernel drivers.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties and child-node shapes, not callable functions. `compatible` uses `oneOf` with 12 branches with 21 tokens: `ralink,rt2880-eval-board`, `ralink,rt2880-soc`, `ralink,rt3050-soc`, `ralink,rt3052-eval-board`, `ralink,rt3052-soc`, `ralink,rt3350-soc`, `ralink,rt3352-soc`, `ralink,rt3883-eval-board`, `ralink,rt3383-soc`, `ralink,rt5350-soc`, `ralink,mt7620a-eval-board`, `ralink,mt7620a-soc`, `ralink,mt7620n-soc`, `onion,omega2+`, `vocore,vocore2`, `ralink,mt7628a-soc`, and 5 more. Top-level properties are `$nodename`, `compatible`. Required top-level properties are none declared. Pattern properties are none. Nested required-property signals include none beyond the top-level list. The highest-risk API details are root-node compatible ordering, CPU node shape, address/size-cell inheritance, interrupt-controller links, and SoC-specific syscon or bus resources.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, resolves `$ref` dependencies, matches applicable compatible strings or reusable fragments, checks required properties, evaluates enum/const/items limits, applies no top-level conditionals, validates embedded examples, and enforces `additionalProperties` or `unevaluatedProperties`. At runtime the kernel consumes the compiled DTB: platform, MFD, MIPS, misc, or MMC drivers match `compatible`, request resources, parse phandles and cells, and create any children described by the node. The YAML itself has no executable branch logic.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, child-node names, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including machine probe state, CPU enumeration, early console/platform-device registration, and SoC infrastructure driver ownership.

## Dependencies and Integration Points
Maintainers listed: Sergio Paracuellos <sergio.paracuellos@gmail.com>. Direct schema dependencies include dt-schema core/meta schemas only. Integration points include MIPS machine selection, CPU topology description, SoC buses, reset/clock/PMU/DMA controller drivers, early platform probing, and board DTS root nodes. The binding also integrates with kernel driver `of_match_table` entries, in-tree DTS users, schema example extraction, and the common `make dt_binding_check` / `make dtbs_check` validation path.

## Risks
Primary risks are incompatible ABI changes to root-node compatible ordering, CPU node shape, address/size-cell inheritance, interrupt-controller links, and SoC-specific syscon or bus resources, mismatches between documented compatibles and driver match tables, and resource ordering or cell-count changes that compile but break probe. This schema permits extra top-level properties. Additional risk signals: large compatible catalogues are prone to missing fallback ordering or stale driver matches; lack of top-level required properties shifts correctness into referenced schemas or DTS review.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mips/ralink.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mips/ralink.yaml` against representative board DTBs. There are no embedded examples, so coverage must come from schema-only validation and DTS users. Useful regression checks are required-property failures, compatible-specific branches, unknown-property rejection, referenced common-schema resolution, example compilation, and a comparison between compatible strings here and the corresponding kernel driver match tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mips/ralink.yaml -->
