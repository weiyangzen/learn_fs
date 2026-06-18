<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/arm,trace-buffer-extension.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/arm,trace-buffer-extension.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/arm,trace-buffer-extension.yaml` defines the root platform compatible binding titled `ARM Trace Buffer Extensions`. Arm Trace Buffer Extension (TRBE) is a per CPU component for storing trace generated on the CPU to memory. It is accessed via CPU system registers. The software can verify if it is permitted to use the component by checking the TRBIDR register. The file is a Linux devicetree YAML schema, so its primary consumer is dt-schema validation rather than executable kernel control flow.

## Important APIs, Types, and Functions
The main public contract is the root node `compatible` property. It uses ordered `items` sequence and lists 1 compatible token including `arm,trace-buffer-extension`. Top-level schema properties are `$nodename`, `compatible`, `interrupts`; required properties are `compatible`, `interrupts`.

## Control Flow, State, and Persistence
Validation is declarative: dt-schema matches the board root node name and walks the ordered `compatible` list to ensure the board-specific token is followed by the required SoC or family fallbacks. There is no runtime state or persistence in the file itself; the compatible ordering persists as ABI in shipped DTS files and selects downstream machine support.

## Dependencies and Integration Points
Maintainers: Anshuman Khandual <anshuman.khandual@arm.com>. Integration points include the Linux devicetree binding build, `dt_binding_check`, `dtbs_check`, and DTS files that instantiate the compatible strings. Schema dependencies/references: dt-schema core/meta schemas only. Top-level conditionals: no top-level conditionals. Examples present: 1 example.

## Risks
Primary risks are ABI drift in compatible ordering, incomplete fallback strings, and DTS examples that no longer satisfy the schema after refactoring. This file rejects unknown top-level properties with `additionalProperties: false`. Conditional schemas and broad compatible catalogues need extra care because small edits can silently reject existing boards or permit nodes that drivers do not support.

## Test Signals
Useful test signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/arm/arm,trace-buffer-extension.yaml`, repository-wide `make dtbs_check`, and building representative DTS files that use the listed compatible strings. For bindings with examples, successful example extraction/validation is the first regression signal; for root platform lists, coverage comes from existing board DTS files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/arm,trace-buffer-extension.yaml -->
