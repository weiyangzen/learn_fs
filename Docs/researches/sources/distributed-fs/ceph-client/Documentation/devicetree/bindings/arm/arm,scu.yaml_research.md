<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/arm,scu.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/arm,scu.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/arm,scu.yaml` defines the MMIO device binding titled `ARM Snoop Control Unit (SCU)`. As part of the MPCore complex, Cortex-A5 and Cortex-A9 are provided with a Snoop Control Unit. The register range is usually 256 (0x100) bytes. References: - Cortex-A9: see DDI0407E Cortex-A9 MPCore Technical Reference Manual Revision r2p0 - Cortex-A5: see DDI0434B Cortex-A5 MPCore Technical Reference Manual Revision r0p1 - ARM11 MPCore: see DDI0360F ARM 11 MPCore Processor Technical Reference Manial Revision r2p0 The file is a Linux devicetree YAML schema, so its primary consumer is dt-schema validation rather than executable kernel control flow.

## Important APIs, Types, and Functions
The schema contract centers on properties `compatible`, `reg` with required set `compatible`, `reg`. The `compatible` property uses `enum` list and lists 3 compatible tokens including `arm,cortex-a9-scu`, `arm,cortex-a5-scu`, `arm,arm11mp-scu`. Pattern properties are none.

## Control Flow, State, and Persistence
Control flow is schema evaluation: a node is selected by `compatible` or property shape, required properties are checked, referenced common schemas are applied, and extra properties are accepted or rejected according to `additionalProperties`/`unevaluatedProperties`. The file has no mutable state; its persistent behavior is the devicetree ABI for register ranges, clocks, interrupts, child nodes, or firmware methods used by kernel drivers.

## Dependencies and Integration Points
Maintainers: Linus Walleij <linusw@kernel.org>. Integration points include the Linux devicetree binding build, `dt_binding_check`, `dtbs_check`, and DTS files that instantiate the compatible strings. Schema dependencies/references: dt-schema core/meta schemas only. Top-level conditionals: no top-level conditionals. Examples present: 1 example.

## Risks
Primary risks are ABI drift in compatible ordering, incomplete fallback strings, and DTS examples that no longer satisfy the schema after refactoring. This file rejects unknown top-level properties with `additionalProperties: false`. Conditional schemas and broad compatible catalogues need extra care because small edits can silently reject existing boards or permit nodes that drivers do not support.

## Test Signals
Useful test signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/arm/arm,scu.yaml`, repository-wide `make dtbs_check`, and building representative DTS files that use the listed compatible strings. For bindings with examples, successful example extraction/validation is the first regression signal; for root platform lists, coverage comes from existing board DTS files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/arm,scu.yaml -->
