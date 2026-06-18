# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/cpufreq/apple,cluster-cpufreq.yaml

## Purpose
This file is a Linux Devicetree JSON-schema document for a CPU frequency scaling binding: Apple
SoC cluster cpufreq device. It lives under `cpufreq` bindings and gives dt-schema a machine-
readable contract for matching hardware nodes before those nodes reach kernel drivers. The
description says: Apple SoCs (e.g. M1) have a per-cpu-cluster DVFS controller that is part of
the cluster management register block. This binding uses the standard operating-points-v2 table
to define the CPU performance states, with the opp-level property specifying the hardware
p-state index for that level.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/cpufreq/apple,cluster-cpufreq.yaml#` with meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Compatible contract: `apple,cluster-cpufreq`, `apple,t8103-cluster-cpufreq`, `apple,t7000-cluster-cpufreq`, `apple,s5l8960x-cluster-cpufreq`, `apple,t6020-cluster-cpufreq`, `apple,t8112-cluster-cpufreq`, `apple,s8000-cluster-cpufreq`, `apple,t8010-cluster-cpufreq`, `apple,t8015-cluster-cpufreq`, `apple,t6000-cluster-cpufreq`.
- Required properties: `compatible`, `reg`, `#performance-domain-cells`.
- Top-level framework properties: `compatible`, `reg`.
- Vendor or device-specific extensions: No vendor-prefixed top-level extension properties are declared..
- Other declared properties: `#performance-domain-cells`.
- Child-node or pattern API: No `patternProperties` or object-valued child-node contract is declared..
- Property detail signals: `reg` (max 1 items); `#performance-domain-cells` (const `0`).

## Control Flow
There is no imperative execution path in this YAML. Validation control flow starts when dt-
schema selects this document for a node whose `compatible` data matches the compatible schema,
then checks the top-level required list, evaluates referenced common schemas, applies property
constraints, and finally walks child-node patterns or named child objects. This file contains 0
`allOf`, 1 `oneOf`, 0 `anyOf`, and 0 `if` blocks, so conditional branches are part of the
accepted DTS shape where those counts are nonzero. `additionalProperties: false` closes the top-
level node to undeclared keys.

## State and Persistence Behavior
The binding itself stores no runtime state and persists only as source-controlled schema text.
The state it describes is persistent board firmware data in DTS/DTB form: register ranges,
clock/reset/interrupt wiring, provider cells, power or GPIO relationships, and optional child
nodes. Kernel drivers consume that data during probe and then program hardware state such as
clocks, counters, connector roles, cpufreq domains, or crypto engines; this YAML only constrains
that data before boot-time use.

## Dependencies and Integration Points
- Schema references: No `$ref` dependencies were found in the parsed schema..
- Textual schema references: `/schemas/cpufreq/apple,cluster-cpufreq.yaml`.
Runtime integration is with cpufreq platform drivers, OPP tables, clocks, regulators, NVMEM,
firmware, and performance-domain providers. Board `.dts` files instantiate nodes that satisfy
this schema; `make dt_binding_check` validates the schema and inline examples, while `make
dtbs_check` validates real board descriptions against the same contract.

## Risks
- A missing or misspelled `compatible` value prevents the schema from matching the intended
hardware and can also keep the kernel driver from probing.
- The required list is small but strict; omitting one of `compatible`, `reg`, `#performance-
domain-cells` should be caught by dt-schema before runtime.
- Conditional and choice schemas can reject otherwise plausible nodes when a compatible-specific
branch changes required properties, item counts, or child-node limits.
- The closed property model is useful for catching typos, but newly needed board properties
require a schema update before DTS changes can pass validation.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/cpufreq/apple,cluster-cpufreq.yaml` to parse this YAML, validate meta-schema rules, and compile its 1 inline example(s).
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/cpufreq/apple,cluster-cpufreq.yaml` on affected board DTS files to confirm real nodes satisfy required properties, compatible choices, child-node names, and referenced common schemas.
- Useful negative tests remove one required property, change `compatible`, and add an undeclared property to confirm the schema catches the expected failures. Example seed: // This example shows a single CPU per domain and 2 domains,; // with two p-states per domain.; // Shipping hardware has 2-4 CPUs per domain and 2-6 domains.; cpus {; #address-cells = <2>;
