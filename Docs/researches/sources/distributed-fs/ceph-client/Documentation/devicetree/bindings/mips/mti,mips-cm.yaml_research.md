<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mips/mti,mips-cm.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mips/mti,mips-cm.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mips/mti,mips-cm.yaml` defines the MIPS platform or SoC binding titled `MIPS Coherence Manager`. The Coherence Manager (CM) is responsible for establishing the global ordering of requests from all elements of the system and sending the correct data back to the requester. It is a Linux devicetree YAML schema used to validate hardware-description nodes before those nodes reach kernel drivers.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties and child-node shapes, not callable functions. `compatible` uses `oneOf` with 2 branches with 2 tokens: `mti,mips-cm`, `mobileye,eyeq6-cm`. Top-level properties are `compatible`, `reg`. Required top-level properties are `compatible`. Pattern properties are none. Nested required-property signals include `compatible`. The highest-risk API details are root-node compatible ordering, CPU node shape, address/size-cell inheritance, interrupt-controller links, and SoC-specific syscon or bus resources.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, resolves `$ref` dependencies, matches applicable compatible strings or reusable fragments, checks required properties, evaluates enum/const/items limits, applies no top-level conditionals, validates embedded examples, and enforces `additionalProperties` or `unevaluatedProperties`. At runtime the kernel consumes the compiled DTB: platform, MFD, MIPS, misc, or MMC drivers match `compatible`, request resources, parse phandles and cells, and create any children described by the node. The YAML itself has no executable branch logic.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, child-node names, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including machine probe state, CPU enumeration, early console/platform-device registration, and SoC infrastructure driver ownership.

## Dependencies and Integration Points
Maintainers listed: Jiaxun Yang <jiaxun.yang@flygoat.com>. Direct schema dependencies include dt-schema core/meta schemas only. Integration points include MIPS machine selection, CPU topology description, SoC buses, reset/clock/PMU/DMA controller drivers, early platform probing, and board DTS root nodes. The binding also integrates with kernel driver `of_match_table` entries, in-tree DTS users, schema example extraction, and the common `make dt_binding_check` / `make dtbs_check` validation path.

## Risks
Primary risks are incompatible ABI changes to root-node compatible ordering, CPU node shape, address/size-cell inheritance, interrupt-controller links, and SoC-specific syscon or bus resources, mismatches between documented compatibles and driver match tables, and resource ordering or cell-count changes that compile but break probe. This schema rejects unknown top-level properties with `additionalProperties: false`. Additional risk signals: examples can drift from the schema and must stay validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mips/mti,mips-cm.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mips/mti,mips-cm.yaml` against representative board DTBs. The schema has 2 embedded examples, so example validation is part of the signal. Useful regression checks are required-property failures, compatible-specific branches, unknown-property rejection, referenced common-schema resolution, example compilation, and a comparison between compatible strings here and the corresponding kernel driver match tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mips/mti,mips-cm.yaml -->
