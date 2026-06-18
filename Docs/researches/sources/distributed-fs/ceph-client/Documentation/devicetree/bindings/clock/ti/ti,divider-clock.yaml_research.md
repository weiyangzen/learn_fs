# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/ti/ti,divider-clock.yaml

## Purpose
This file is a Linux Devicetree JSON-schema document for a clock provider/controller binding:
Texas Instruments divider clock. It lives under `clock` bindings and gives dt-schema a machine-
readable contract for matching hardware nodes before those nodes reach kernel drivers. The
description says: This clock It assumes a register-mapped adjustable clock rate divider that
does not gate and has only one input clock or parent. By default the value programmed into the
register is one less than the actual divisor value. E.g: register value actual divisor value 0 1
1 2 2 3 This assumption may be modified by the following optional properties: ti,index-starts-
at-one - valid divisor values start at 1, not the default of 0. E.g: register value actual
divisor value 1 1 2 2 3 3 ti,index-power-of-two - valid divisor values are powers of two. E.g:
register value actual divisor value 0 1 1 2 2 4 Addi...

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/clock/ti/ti,divider-clock.yaml#` with meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Compatible contract: `ti,divider-clock`, `ti,composite-divider-clock`.
- Required properties: `compatible`, `#clock-cells`, `clocks`, `reg`.
- Top-level framework properties: `compatible`, `reg`, `clocks`, `#clock-cells`, `clock-output-names`.
- Vendor or device-specific extensions: `ti,dividers`, `ti,bit-shift`, `ti,min-div`, `ti,max-div`, `ti,index-starts-at-one`, `ti,index-power-of-two`, `ti,set-rate-parent`, `ti,latch-bit`.
- Other declared properties: No additional generic top-level properties beyond the highlighted framework/vendor keys..
- Child-node or pattern API: No `patternProperties` or object-valued child-node contract is declared..
- Property detail signals: `compatible` (enum `ti,divider-clock`, `ti,composite-divider-clock`); `reg` (max 1 items); `clocks` (max 1 items); `#clock-cells` (const `0`); `clock-output-names` (max 1 items); `ti,dividers` (ref `/schemas/types.yaml#/definitions/uint32-array`; array of integers defining divisors); `ti,bit-shift` (ref `/schemas/types.yaml#/definitions/uint32`; number of bits to shift the divider value); `ti,min-div` (ref `/schemas/types.yaml#/definitions/uint32`; min divisor for dividing the input clock rate, only needed if the first divisor is offset from the default value (1)).

## Control Flow
There is no imperative execution path in this YAML. Validation control flow starts when dt-
schema selects this document for a node whose `compatible` data matches the compatible schema,
then checks the top-level required list, evaluates referenced common schemas, applies property
constraints, and finally walks child-node patterns or named child objects. This file contains 1
`allOf`, 0 `oneOf`, 0 `anyOf`, and 0 `if` blocks, so conditional branches are part of the
accepted DTS shape where those counts are nonzero. `unevaluatedProperties: false` closes the
node after referenced schemas and conditional branches are evaluated.

## State and Persistence Behavior
The binding itself stores no runtime state and persists only as source-controlled schema text.
The state it describes is persistent board firmware data in DTS/DTB form: register ranges,
clock/reset/interrupt wiring, provider cells, power or GPIO relationships, and optional child
nodes. Kernel drivers consume that data during probe and then program hardware state such as
clocks, counters, connector roles, cpufreq domains, or crypto engines; this YAML only constrains
that data before boot-time use.

## Dependencies and Integration Points
- Schema references: `ti,autoidle.yaml#`, `/schemas/types.yaml#/definitions/uint32-array`, `/schemas/types.yaml#/definitions/uint32`.
- Textual schema references: `/schemas/clock/ti/ti,divider-clock.yaml`, `/schemas/types.yaml#/definitions/uint32`, `/schemas/types.yaml#/definitions/uint32-array`.
Runtime integration is with clock framework consumers using `clocks`, `clock-names`, provider
cells such as `#clock-cells`, and driver-specific clock ID headers. Board `.dts` files
instantiate nodes that satisfy this schema; `make dt_binding_check` validates the schema and
inline examples, while `make dtbs_check` validates real board descriptions against the same
contract.

## Risks
- A missing or misspelled `compatible` value prevents the schema from matching the intended
hardware and can also keep the kernel driver from probing.
- The required list is small but strict; omitting one of `compatible`, `#clock-cells`, `clocks`,
`reg` should be caught by dt-schema before runtime.
- The closed property model is useful for catching typos, but newly needed board properties
require a schema update before DTS changes can pass validation.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/ti/ti,divider-clock.yaml` to parse this YAML, validate meta-schema rules, and compile its 1 inline example(s).
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/ti/ti,divider-clock.yaml` on affected board DTS files to confirm real nodes satisfy required properties, compatible choices, child-node names, and referenced common schemas.
- Useful negative tests remove one required property, change `compatible`, and add an undeclared property to confirm the schema catches the expected failures. Example seed: bus {; #address-cells = <1>;; #size-cells = <0>;; clock-controller@190 {; #clock-cells = <0>;
