# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/counter/ti-eqep.yaml

## Purpose
This file is a Linux Devicetree JSON-schema document for a counter device binding: Texas
Instruments Enhanced Quadrature Encoder Pulse (eQEP) Module. It lives under `counter` bindings
and gives dt-schema a machine-readable contract for matching hardware nodes before those nodes
reach kernel drivers. The file does not carry a long description, so its role is inferred from
title, path, and schema constraints.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/counter/ti-eqep.yaml#` with meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Compatible contract: `ti,am3352-eqep`, `ti,am62-eqep`.
- Required properties: `compatible`, `reg`, `interrupts`, `clocks`.
- Top-level framework properties: `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `power-domains`.
- Vendor or device-specific extensions: No vendor-prefixed top-level extension properties are declared..
- Other declared properties: No additional generic top-level properties beyond the highlighted framework/vendor keys..
- Child-node or pattern API: No `patternProperties` or object-valued child-node contract is declared..
- Property detail signals: `compatible` (enum `ti,am3352-eqep`, `ti,am62-eqep`); `reg` (max 1 items); `interrupts` (max 1 items; The eQEP event interrupt); `clocks` (max 1 items; The functional and interface clock that determines the clock rate for the eQEP peripheral.); `clock-names` (const `sysclkout`); `power-domains` (max 1 items).

## Control Flow
There is no imperative execution path in this YAML. Validation control flow starts when dt-
schema selects this document for a node whose `compatible` data matches the compatible schema,
then checks the top-level required list, evaluates referenced common schemas, applies property
constraints, and finally walks child-node patterns or named child objects. This file contains 1
`allOf`, 0 `oneOf`, 0 `anyOf`, and 1 `if` blocks, so conditional branches are part of the
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
- Textual schema references: `/schemas/counter/ti-eqep.yaml`.
Runtime integration is with Linux counter subsystem drivers, interrupt/GPIO providers, clocks,
and pin/control blocks. Board `.dts` files instantiate nodes that satisfy this schema; `make
dt_binding_check` validates the schema and inline examples, while `make dtbs_check` validates
real board descriptions against the same contract.

## Risks
- A missing or misspelled `compatible` value prevents the schema from matching the intended
hardware and can also keep the kernel driver from probing.
- The required list is small but strict; omitting one of `compatible`, `reg`, `interrupts`,
`clocks` should be caught by dt-schema before runtime.
- Conditional and choice schemas can reject otherwise plausible nodes when a compatible-specific
branch changes required properties, item counts, or child-node limits.
- The closed property model is useful for catching typos, but newly needed board properties
require a schema update before DTS changes can pass validation.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/counter/ti-eqep.yaml` to parse this YAML, validate meta-schema rules, and compile its 1 inline example(s).
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/counter/ti-eqep.yaml` on affected board DTS files to confirm real nodes satisfy required properties, compatible choices, child-node names, and referenced common schemas.
- Useful negative tests remove one required property, change `compatible`, and add an undeclared property to confirm the schema catches the expected failures. Example seed: eqep0: counter@180 {; compatible = "ti,am3352-eqep";; reg = <0x180 0x80>;; clocks = <&l4ls_gclk>;; interrupts = <79>;
