<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/arm,cci-400.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/arm,cci-400.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/arm,cci-400.yaml` defines the MMIO controller or bus binding titled `ARM CCI Cache Coherent Interconnect`. ARM multi-cluster systems maintain intra-cluster coherency through a cache coherent interconnect (CCI) that is capable of monitoring bus transactions and manage coherency, TLB invalidations and memory barriers. It allows snooping and distributed virtual memory message broadcast across clusters, through memory mapped interface, with a global control register space and multiple sets of interface control registers, one per slave interface. The file is a Linux devicetree YAML schema, so its primary consumer is dt-schema validation rather than executable kernel control flow.

## Important APIs, Types, and Functions
The schema contract centers on properties `$nodename`, `compatible`, `reg`, `#address-cells`, `#size-cells`, `ranges` with required set `#address-cells`, `#size-cells`, `compatible`, `ranges`, `reg`. The `compatible` property uses `enum` list and lists 3 compatible tokens including `arm,cci-400`, `arm,cci-500`, `arm,cci-550`. Pattern properties are `^slave-if@[0-9a-f]+$`, `^pmu@[0-9a-f]+$`.

## Control Flow, State, and Persistence
Control flow is schema evaluation: a node is selected by `compatible` or property shape, required properties are checked, referenced common schemas are applied, and extra properties are accepted or rejected according to `additionalProperties`/`unevaluatedProperties`. The file has no mutable state; its persistent behavior is the devicetree ABI for register ranges, clocks, interrupts, child nodes, or firmware methods used by kernel drivers.

## Dependencies and Integration Points
Maintainers: Lorenzo Pieralisi <lorenzo.pieralisi@arm.com>. Integration points include the Linux devicetree binding build, `dt_binding_check`, `dtbs_check`, and DTS files that instantiate the compatible strings. Schema dependencies/references: dt-schema core/meta schemas only. Top-level conditionals: no top-level conditionals. Examples present: 1 example.

## Risks
Primary risks are ABI drift in compatible ordering, incomplete fallback strings, and DTS examples that no longer satisfy the schema after refactoring. This file rejects unknown top-level properties with `additionalProperties: false`. Conditional schemas and broad compatible catalogues need extra care because small edits can silently reject existing boards or permit nodes that drivers do not support.

## Test Signals
Useful test signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/arm/arm,cci-400.yaml`, repository-wide `make dtbs_check`, and building representative DTS files that use the listed compatible strings. For bindings with examples, successful example extraction/validation is the first regression signal; for root platform lists, coverage comes from existing board DTS files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/arm,cci-400.yaml -->
