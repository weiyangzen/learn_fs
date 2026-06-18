# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/cpufreq/airoha,en7581-cpufreq.yaml

## Purpose
This file is a Linux Devicetree JSON-schema document for a CPU frequency scaling binding: Airoha
EN7581 CPUFreq. It lives under `cpufreq` bindings and gives dt-schema a machine-readable
contract for matching hardware nodes before those nodes reach kernel drivers. The description
says: On newer Airoha SoC, CPU Frequency is scaled indirectly with SMC commands to ATF. A
virtual clock is exposed. This virtual clock is a get-only clock and is used to expose the
current global CPU clock. The frequency info comes by the output of the SMC command that reports
the clock in MHz. The SMC sets the CPU clock by providing an index, this is modelled as
performance states in a power domain. CPUs can't be individually scaled as the CPU frequency is
shared across all CPUs and is global.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/cpufreq/airoha,en7581-cpufreq.yaml#` with meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Compatible contract: `airoha,en7581-cpufreq`.
- Required properties: `compatible`, `#clock-cells`, `#power-domain-cells`, `operating-points-v2`.
- Top-level framework properties: `compatible`, `#clock-cells`, `operating-points-v2`.
- Vendor or device-specific extensions: No vendor-prefixed top-level extension properties are declared..
- Other declared properties: `#power-domain-cells`.
- Child-node or pattern API: No `patternProperties` or object-valued child-node contract is declared..
- Property detail signals: `compatible` (const `airoha,en7581-cpufreq`); `#clock-cells` (const `0`); `#power-domain-cells` (const `0`).

## Control Flow
There is no imperative execution path in this YAML. Validation control flow starts when dt-
schema selects this document for a node whose `compatible` data matches the compatible schema,
then checks the top-level required list, evaluates referenced common schemas, applies property
constraints, and finally walks child-node patterns or named child objects. This file contains 0
`allOf`, 0 `oneOf`, 0 `anyOf`, and 0 `if` blocks, so conditional branches are part of the
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
- Textual schema references: `/schemas/cpufreq/airoha,en7581-cpufreq.yaml`.
Runtime integration is with cpufreq platform drivers, OPP tables, clocks, regulators, NVMEM,
firmware, and performance-domain providers. Board `.dts` files instantiate nodes that satisfy
this schema; `make dt_binding_check` validates the schema and inline examples, while `make
dtbs_check` validates real board descriptions against the same contract.

## Risks
- A missing or misspelled `compatible` value prevents the schema from matching the intended
hardware and can also keep the kernel driver from probing.
- The required list is small but strict; omitting one of `compatible`, `#clock-cells`, `#power-
domain-cells`, `operating-points-v2` should be caught by dt-schema before runtime.
- The closed property model is useful for catching typos, but newly needed board properties
require a schema update before DTS changes can pass validation.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/cpufreq/airoha,en7581-cpufreq.yaml` to parse this YAML, validate meta-schema rules, and compile its 1 inline example(s).
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/cpufreq/airoha,en7581-cpufreq.yaml` on affected board DTS files to confirm real nodes satisfy required properties, compatible choices, child-node names, and referenced common schemas.
- Useful negative tests remove one required property, change `compatible`, and add an undeclared property to confirm the schema catches the expected failures. Example seed: performance-domain {; compatible = "airoha,en7581-cpufreq";; operating-points-v2 = <&cpu_smcc_opp_table>;; #power-domain-cells = <0>;; #clock-cells = <0>;
