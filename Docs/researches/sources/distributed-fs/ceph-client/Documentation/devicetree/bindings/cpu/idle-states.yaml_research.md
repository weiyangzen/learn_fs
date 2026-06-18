# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/cpu/idle-states.yaml

## Purpose
This file is a Linux Devicetree JSON-schema document for a CPU idle-state binding: Idle states.
It lives under `cpu` bindings and gives dt-schema a machine-readable contract for matching
hardware nodes before those nodes reach kernel drivers. The description says:
========================================== 1 - Introduction
========================================== ARM and RISC-V systems contain HW capable of managing
power consumption dynamically, where cores can be put in different low-power states (ranging
from simple wfi to power gating) according to OS PM policies. The CPU states representing the
range of dynamic idle states that a processor can enter at run-time, can be specified through
device tree bindings representing the parameters required to enter/exit specific idle states on
a given processor. ========================================== 2 - ARM idle states
================...

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/cpu/idle-states.yaml#` with meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Compatible contract: No explicit compatible string was extracted from the parsed `compatible` schema; consumers rely on the surrounding schema constraints..
- Required properties: No top-level `required` list is declared..
- Top-level framework properties: No standard framework property from the clock/interrupt/reset/regulator shortlist is declared at top level..
- Vendor or device-specific extensions: No vendor-prefixed top-level extension properties are declared..
- Other declared properties: `$nodename`, `entry-method`.
- Child-node or pattern API: `^(cpu|cluster)-` requiring `compatible`, `entry-latency-us`, `exit-latency-us`, `min-residency-us`.
- Property detail signals: `$nodename` (const `idle-states`); `entry-method` (const `psci`; Usage and definition depend on ARM architecture version. On ARM v8 64-bit this property is required. On ARM 32-bit sy...).

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
- Schema references: `/schemas/types.yaml#/definitions/uint32`, `/schemas/types.yaml#/definitions/string`.
- Textual schema references: `/schemas/cpu/idle-states.yaml`, `/schemas/types.yaml#/definitions/string`, `/schemas/types.yaml#/definitions/uint32`.
Runtime integration is with CPU nodes through `cpu-idle-states`, PSCI/cpuidle drivers, and
scheduler/power-management validation. Board `.dts` files instantiate nodes that satisfy this
schema; `make dt_binding_check` validates the schema and inline examples, while `make
dtbs_check` validates real board descriptions against the same contract.

## Risks
- A missing or misspelled `compatible` value prevents the schema from matching the intended
hardware and can also keep the kernel driver from probing.
- Conditional and choice schemas can reject otherwise plausible nodes when a compatible-specific
branch changes required properties, item counts, or child-node limits.
- Child-node patterns must match exact unit-address/name conventions; mismatched child names may
be rejected or left unvalidated depending on the property-closure mode.
- The closed property model is useful for catching typos, but newly needed board properties
require a schema update before DTS changes can pass validation.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/cpu/idle-states.yaml` to parse this YAML, validate meta-schema rules, and compile its 3 inline example(s).
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/cpu/idle-states.yaml` on affected board DTS files to confirm real nodes satisfy required properties, compatible choices, child-node names, and referenced common schemas.
- Useful negative tests remove one required property, change `compatible`, and add an undeclared property to confirm the schema catches the expected failures. Example seed: cpus {; #size-cells = <0>;; #address-cells = <2>;; cpu@0 {; device_type = "cpu";
