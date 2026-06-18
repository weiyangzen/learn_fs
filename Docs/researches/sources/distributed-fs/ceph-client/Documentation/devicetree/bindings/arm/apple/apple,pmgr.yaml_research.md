<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/apple/apple,pmgr.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/apple/apple,pmgr.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/apple/apple,pmgr.yaml` defines the MMIO controller or bus binding titled `Apple SoC Power Manager (PMGR)`. Apple SoCs include PMGR blocks responsible for power management, which can control various clocks, resets, power states, and performance features. This node represents the PMGR as a syscon, with sub-nodes representing individual features. The file is a Linux devicetree YAML schema, so its primary consumer is dt-schema validation rather than executable kernel control flow.

## Important APIs, Types, and Functions
The schema contract centers on properties `$nodename`, `compatible`, `reg`, `#address-cells`, `#size-cells` with required set `compatible`, `reg`. The `compatible` property uses `oneOf` with 2 accepted compatible sequences and lists 12 compatible tokens including `apple,s5l8960x-pmgr`, `apple,t7000-pmgr`, `apple,s8000-pmgr`, `apple,t8010-pmgr`, `apple,t8015-pmgr`, `apple,t8103-pmgr`, `apple,t8112-pmgr`, `apple,t6000-pmgr`, `apple,pmgr`, `syscon` and more. Pattern properties are `power-controller@[0-9a-f]+$`.

## Control Flow, State, and Persistence
Control flow is schema evaluation: a node is selected by `compatible` or property shape, required properties are checked, referenced common schemas are applied, and extra properties are accepted or rejected according to `additionalProperties`/`unevaluatedProperties`. The file has no mutable state; its persistent behavior is the devicetree ABI for register ranges, clocks, interrupts, child nodes, or firmware methods used by kernel drivers.

## Dependencies and Integration Points
Maintainers: Hector Martin <marcan@marcan.st>. Integration points include the Linux devicetree binding build, `dt_binding_check`, `dtbs_check`, and DTS files that instantiate the compatible strings. Schema dependencies/references: `/schemas/power/apple,pmgr-pwrstate.yaml#`. Top-level conditionals: no top-level conditionals. Examples present: 1 example.

## Risks
Primary risks are ABI drift in compatible ordering, incomplete fallback strings, and DTS examples that no longer satisfy the schema after refactoring. This file rejects unknown top-level properties with `additionalProperties: false`. Conditional schemas and broad compatible catalogues need extra care because small edits can silently reject existing boards or permit nodes that drivers do not support.

## Test Signals
Useful test signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/arm/apple/apple,pmgr.yaml`, repository-wide `make dtbs_check`, and building representative DTS files that use the listed compatible strings. For bindings with examples, successful example extraction/validation is the first regression signal; for root platform lists, coverage comes from existing board DTS files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/apple/apple,pmgr.yaml -->
