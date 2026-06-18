<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/atmel,sama5d2-secumod.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/atmel,sama5d2-secumod.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/atmel,sama5d2-secumod.yaml` defines the MMIO device binding titled `Microchip AT91 Security Module (SECUMOD)`. The Security Module also offers the PIOBU pins which can be used as GPIO pins. Note that they maintain their voltage during Backup/Self-refresh. The file is a Linux devicetree YAML schema, so its primary consumer is dt-schema validation rather than executable kernel control flow.

## Important APIs, Types, and Functions
The schema contract centers on properties `compatible`, `reg`, `gpio-controller`, `#gpio-cells` with required set `compatible`, `reg`. The `compatible` property uses `oneOf` with 2 accepted compatible sequences and lists 4 compatible tokens including `atmel,sama5d2-secumod`, `syscon`, `microchip,sama7d65-secumod`, `microchip,sama7g5-secumod`. Pattern properties are none.

## Control Flow, State, and Persistence
Control flow is schema evaluation: a node is selected by `compatible` or property shape, required properties are checked, referenced common schemas are applied, and extra properties are accepted or rejected according to `additionalProperties`/`unevaluatedProperties`. The file has no mutable state; its persistent behavior is the devicetree ABI for register ranges, clocks, interrupts, child nodes, or firmware methods used by kernel drivers.

## Dependencies and Integration Points
Maintainers: Nicolas Ferre <nicolas.ferre@microchip.com>. Integration points include the Linux devicetree binding build, `dt_binding_check`, `dtbs_check`, and DTS files that instantiate the compatible strings. Schema dependencies/references: dt-schema core/meta schemas only. Top-level conditionals: no top-level conditionals. Examples present: 1 example.

## Risks
Primary risks are ABI drift in compatible ordering, incomplete fallback strings, and DTS examples that no longer satisfy the schema after refactoring. This file uses `unevaluatedProperties: false` after composed refs. Conditional schemas and broad compatible catalogues need extra care because small edits can silently reject existing boards or permit nodes that drivers do not support.

## Test Signals
Useful test signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/arm/atmel,sama5d2-secumod.yaml`, repository-wide `make dtbs_check`, and building representative DTS files that use the listed compatible strings. For bindings with examples, successful example extraction/validation is the first regression signal; for root platform lists, coverage comes from existing board DTS files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/atmel,sama5d2-secumod.yaml -->
