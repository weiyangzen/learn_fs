<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mips/cpus.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mips/cpus.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mips/cpus.yaml` defines the MIPS platform or SoC binding titled `MIPS CPUs`. The device tree allows to describe the layout of CPUs in a system through the "cpus" node, which in turn contains a number of subnodes (ie "cpu") defining properties for every CPU. It is a Linux devicetree YAML schema used to validate hardware-description nodes before those nodes reach kernel drivers.

## Important APIs, Types, and Functions
The public ABI is the set of DTS properties and child-node shapes, not callable functions. `compatible` uses an `enum` with 23 tokens: `brcm,bmips3300`, `brcm,bmips4350`, `brcm,bmips4380`, `brcm,bmips5000`, `brcm,bmips5200`, `img,i6500`, `ingenic,xburst-fpu1.0-mxu1.1`, `ingenic,xburst-fpu2.0-mxu2.0`, `ingenic,xburst-mxu1.0`, `ingenic,xburst2-fpu2.1-mxu2.1-smt`, `loongson,gs264`, `mips,m14Kc`, `mips,mips1004Kc`, `mips,mips24KEc`, `mips,mips24Kc`, `mips,mips34Kc`, and 7 more. Top-level properties are `compatible`, `reg`, `clocks`, `device_type`. Required top-level properties are `compatible`, `reg`. Pattern properties are none. Nested required-property signals include `device_type`, `clocks`, `compatible`, `reg`. The highest-risk API details are root-node compatible ordering, CPU node shape, address/size-cell inheritance, interrupt-controller links, and SoC-specific syscon or bus resources.

## Control Flow
Control flow is declarative schema evaluation. During `dt_binding_check` or `dtbs_check`, dt-schema loads the YAML, resolves `$ref` dependencies, matches applicable compatible strings or reusable fragments, checks required properties, evaluates enum/const/items limits, applies `allOf`, validates embedded examples, and enforces `additionalProperties` or `unevaluatedProperties`. At runtime the kernel consumes the compiled DTB: platform, MFD, MIPS, misc, or MMC drivers match `compatible`, request resources, parse phandles and cells, and create any children described by the node. The YAML itself has no executable branch logic.

## State and Persistence Behavior
The file stores no mutable state and creates no persistent data. Persistence is the devicetree ABI: compatible strings, property names, phandle layout, child-node names, and example nodes become contracts shipped in DTS/DTB artifacts. Runtime state is owned by kernel drivers after probe, including machine probe state, CPU enumeration, early console/platform-device registration, and SoC infrastructure driver ownership.

## Dependencies and Integration Points
Maintainers listed: Thomas Bogendoerfer <tsbogend@alpha.franken.de>, 周琰杰 (Zhou Yanjie) <zhouyanjie@wanyeetech.com>. Direct schema dependencies include `/schemas/opp/opp-v1.yaml#`. Integration points include MIPS machine selection, CPU topology description, SoC buses, reset/clock/PMU/DMA controller drivers, early platform probing, and board DTS root nodes. The binding also integrates with kernel driver `of_match_table` entries, in-tree DTS users, schema example extraction, and the common `make dt_binding_check` / `make dtbs_check` validation path.

## Risks
Primary risks are incompatible ABI changes to root-node compatible ordering, CPU node shape, address/size-cell inheritance, interrupt-controller links, and SoC-specific syscon or bus resources, mismatches between documented compatibles and driver match tables, and resource ordering or cell-count changes that compile but break probe. This schema closes composed schemas with `unevaluatedProperties: false`. Additional risk signals: conditional branches can accidentally validate one hardware variant while rejecting another; large compatible catalogues are prone to missing fallback ordering or stale driver matches; examples can drift from the schema and must stay validated.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mips/cpus.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/mips/cpus.yaml` against representative board DTBs. The schema has 2 embedded examples, so example validation is part of the signal. Useful regression checks are required-property failures, compatible-specific branches, unknown-property rejection, referenced common-schema resolution, example compilation, and a comparison between compatible strings here and the corresponding kernel driver match tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mips/cpus.yaml -->
