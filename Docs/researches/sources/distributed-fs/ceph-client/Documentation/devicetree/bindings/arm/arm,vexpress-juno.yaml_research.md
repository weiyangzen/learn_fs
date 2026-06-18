<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/arm,vexpress-juno.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/arm,vexpress-juno.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/arm,vexpress-juno.yaml` defines the devicetree schema binding titled `ARM Versatile Express and Juno Boards`. ARM's Versatile Express platform were built as reference designs for exploring multicore Cortex-A class systems. The Versatile Express family contains both 32 bit (Aarch32) and 64 bit (Aarch64) systems. The board consist of a motherboard and one or more daughterboards (tiles). The motherboard provides a set of peripherals. Processor and RAM "live" on the tiles. The motherboard and each core tile should be described by a separate Device Tree source file, with the tile's description including the motherboard file using an include directive. As the motherboard can be initialized in one of two different configurations ("memory maps"), care must be taken to include the correct one. When a new... The file is a Linux devicetree YAML schema, so its primary consumer is dt-schema validation rather than executable kernel control flow.

## Important APIs, Types, and Functions
The schema contract centers on properties `$nodename`, `compatible`, `arm,vexpress,position`, `arm,vexpress,dcc` with required set none declared at the top level. The `compatible` property uses `oneOf` with 13 accepted compatible sequences and lists 16 compatible tokens including `arm,vexpress,v2p-ca9`, `arm,vexpress`, `arm,vexpress,v2p-ca5s`, `arm,vexpress,v2p-ca15`, `arm,vexpress,v2p-ca15,tc1`, `arm,vexpress,v2p-ca15_a7`, `arm,vexpress,v2f-1xv7,ca53x2`, `arm,vexpress,v2f-1xv7`, `arm,juno`, `arm,juno-r1` and more. Pattern properties are `^bus@[0-9a-f]+$`.

## Control Flow, State, and Persistence
Control flow is schema evaluation: a node is selected by `compatible` or property shape, required properties are checked, referenced common schemas are applied, and extra properties are accepted or rejected according to `additionalProperties`/`unevaluatedProperties`. The file has no mutable state; its persistent behavior is the devicetree ABI for register ranges, clocks, interrupts, child nodes, or firmware methods used by kernel drivers.

## Dependencies and Integration Points
Maintainers: Sudeep Holla <sudeep.holla@arm.com>, Linus Walleij <linusw@kernel.org>. Integration points include the Linux devicetree binding build, `dt_binding_check`, `dtbs_check`, and DTS files that instantiate the compatible strings. Schema dependencies/references: `/schemas/simple-bus.yaml`, `/schemas/types.yaml#/definitions/string`, `/schemas/types.yaml#/definitions/uint32`. Top-level conditionals: `allOf`. Examples present: 0 examples.

## Risks
Primary risks are ABI drift in compatible ordering, incomplete fallback strings, and DTS examples that no longer satisfy the schema after refactoring. This file allows additional root properties, so validation is intentionally permissive. Conditional schemas and broad compatible catalogues need extra care because small edits can silently reject existing boards or permit nodes that drivers do not support.

## Test Signals
Useful test signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/arm/arm,vexpress-juno.yaml`, repository-wide `make dtbs_check`, and building representative DTS files that use the listed compatible strings. For bindings with examples, successful example extraction/validation is the first regression signal; for root platform lists, coverage comes from existing board DTS files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/arm,vexpress-juno.yaml -->
