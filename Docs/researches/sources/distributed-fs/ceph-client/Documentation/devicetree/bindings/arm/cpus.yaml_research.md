<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/cpus.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/cpus.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/cpus.yaml` defines the cpu-node binding titled `ARM CPUs`. The device tree allows to describe the layout of CPUs in a system through the "cpus" node, which in turn contains a number of subnodes (ie "cpu") defining properties for every cpu. Bindings for CPU nodes follow the Devicetree Specification, available from: https://www.devicetree.org/specifications/ with updates for 32-bit and 64-bit ARM systems provided in this document. ================================ Convention used in this document ================================ This document follows the conventions described in the Devicetree Specification, with the addition: - square brackets define bitfields, eg reg[7:0] value of the bitfield in the reg property contained in bits 7 down to 0 ====... The file is a Linux devicetree YAML schema, so its primary consumer is dt-schema validation rather than executable kernel control flow.

## Important APIs, Types, and Functions
The binding describes ARM `cpu` subnodes under `/cpus`. It accepts a large `compatible` catalogue (151 tokens), requires `device_type`, `reg`, `compatible`, and exposes CPU topology, boot, power, OPP, supply, cache, idle-state, interconnect, and coherency properties such as `reg`, `compatible`, `enable-method`, `cpu-release-addr`, `cpu-idle-states`, `capacity-dmips-mhz`, `cci-control-port`, `dynamic-power-coefficient`, `interconnects`, `nvmem-cells`, `nvmem-cell-names`, `performance-domains`, `power-domains`, `power-domain-names`, `resets`, `arm-supply`, `cpu0-supply`, `mem-supply`, and 13 more.

## Control Flow, State, and Persistence
Validation follows CPU-node schema composition: core devicetree CPU requirements are checked first, then conditional blocks constrain `enable-method`, `cpu-release-addr`, idle states, PSCI/spin-table boot paths, performance domains, supplies, and implementation-specific compatible strings. The file does not store runtime CPU state; it locks the ABI used by architecture boot code, CPU hotplug, cpufreq/OPP, idle, power-domain, and topology code.

## Dependencies and Integration Points
Maintainers: Lorenzo Pieralisi <lorenzo.pieralisi@arm.com>. Integration points include the Linux devicetree binding build, `dt_binding_check`, `dtbs_check`, and DTS files that instantiate the compatible strings. Schema dependencies/references: `/schemas/cpu.yaml#`, `/schemas/opp/opp-v1.yaml#`, `/schemas/types.yaml#/definitions/flag`, `/schemas/types.yaml#/definitions/phandle`, `/schemas/types.yaml#/definitions/phandle-array`, `/schemas/types.yaml#/definitions/string`, `/schemas/types.yaml#/definitions/uint32`, `/schemas/types.yaml#/definitions/uint32-matrix`, and 1 more. Top-level conditionals: `allOf`, `dependencies`. Examples present: 4 examples.

## Risks
Primary risks are ABI drift in compatible ordering, incomplete fallback strings, and DTS examples that no longer satisfy the schema after refactoring. This file uses `unevaluatedProperties: false` after composed refs. Conditional schemas and broad compatible catalogues need extra care because small edits can silently reject existing boards or permit nodes that drivers do not support.

## Test Signals
Useful test signals are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/arm/cpus.yaml`, repository-wide `make dtbs_check`, and building representative DTS files that use the listed compatible strings. For bindings with examples, successful example extraction/validation is the first regression signal; for root platform lists, coverage comes from existing board DTS files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/cpus.yaml -->
