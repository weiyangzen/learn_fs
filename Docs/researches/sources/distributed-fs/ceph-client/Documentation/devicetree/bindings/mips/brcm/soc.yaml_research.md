<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mips/brcm/soc.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mips/brcm/soc.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mips/brcm/soc.yaml` defines the MIPS platform or SoC binding titled `Broadcom cable/DSL/settop platforms`. Boards Broadcom cable/DSL/settop SoC shall have the following properties. It is a Linux devicetree YAML schema used to validate hardware-description nodes before those nodes reach kernel drivers.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties and child-node shapes, not callable functions. `compatible` uses an `enum` with 18 tokens: `brcm,bcm3368`, `brcm,bcm3384`, `brcm,bcm33843`, `brcm,bcm3384-viper`, `brcm,bcm33843-viper`, `brcm,bcm6328`, `brcm,bcm6358`, `brcm,bcm6362`, `brcm,bcm6368`, `brcm,bcm63168`, `brcm,bcm63268`, `brcm,bcm7125`, `brcm,bcm7346`, `brcm,bcm7358`, `brcm,bcm7360`, `brcm,bcm7362`, and 2 more. Top-level properties are `$nodename`, `compatible`, `cpus`. Required top-level properties are none declared. Pattern properties are none. Nested required-property signals include `mips-hpt-frequency`, `brcm,bmips-cbr-reg`. The highest-risk API details are root-node compatible ordering, CPU node shape, address/size-cell inheritance, interrupt-controller links, and SoC-specific syscon or bus resources.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, resolves `$ref` dependencies, matches applicable compatible strings or reusable fragments, checks required properties, evaluates enum/const/items limits, applies `if`, `then`, validates embedded examples, and enforces `additionalProperties` or `unevaluatedProperties`. At runtime the kernel consumes the compiled DTB: platform, MFD, MIPS, misc, or MMC drivers match `compatible`, request resources, parse phandles and cells, and create any children described by the node. The YAML itself has no executable branch logic.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, child-node names, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including machine probe state, CPU enumeration, early console/platform-device registration, and SoC infrastructure driver ownership.

## Dependencies and Integration Points
Maintainers listed: Florian Fainelli <f.fainelli@gmail.com>. Direct schema dependencies include `/schemas/mips/cpus.yaml#`, `/schemas/types.yaml#/definitions/uint32`. Integration points include MIPS machine selection, CPU topology description, SoC buses, reset/clock/PMU/DMA controller drivers, early platform probing, and board DTS root nodes. The binding also integrates with kernel driver `of_match_table` entries, in-tree DTS users, schema example extraction, and the common `make dt_binding_check` / `make dtbs_check` validation path.

## Risks
Primary risks are incompatible ABI changes to root-node compatible ordering, CPU node shape, address/size-cell inheritance, interrupt-controller links, and SoC-specific syscon or bus resources, mismatches between documented compatibles and driver match tables, and resource ordering or cell-count changes that compile but break probe. This schema permits extra top-level properties. Additional risk signals: conditional branches can accidentally validate one hardware variant while rejecting another; large compatible catalogues are prone to missing fallback ordering or stale driver matches; examples can drift from the schema and must stay validated; lack of top-level required properties shifts correctness into referenced schemas or DTS review.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mips/brcm/soc.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mips/brcm/soc.yaml` against representative board DTBs. The schema has 1 embedded example, so example validation is part of the signal. Useful regression checks are required-property failures, compatible-specific branches, unknown-property rejection, referenced common-schema resolution, example compilation, and a comparison between compatible strings here and the corresponding kernel driver match tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mips/brcm/soc.yaml -->
