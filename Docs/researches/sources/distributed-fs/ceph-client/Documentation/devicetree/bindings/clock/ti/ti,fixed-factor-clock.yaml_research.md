# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/ti/ti,fixed-factor-clock.yaml

## Purpose
This file is a Linux Devicetree JSON-schema document for a clock provider/controller binding: TI
fixed factor rate clock sources. It lives under `clock` bindings and gives dt-schema a machine-
readable contract for matching hardware nodes before those nodes reach kernel drivers. The
description says: This consists of a divider and a multiplier used to generate a fixed rate
clock. This also uses the autoidle support from TI autoidle clock.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/clock/ti/ti,fixed-factor-clock.yaml#` with meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Compatible contract: `ti,fixed-factor-clock`.
- Required properties: `compatible`, `clocks`, `#clock-cells`, `ti,clock-mult`, `ti,clock-div`.
- Top-level framework properties: `compatible`, `reg`, `clocks`, `#clock-cells`, `clock-output-names`.
- Vendor or device-specific extensions: `ti,clock-div`, `ti,clock-mult`, `ti,set-rate-parent`.
- Other declared properties: No additional generic top-level properties beyond the highlighted framework/vendor keys..
- Child-node or pattern API: No `patternProperties` or object-valued child-node contract is declared..
- Property detail signals: `compatible` (const `ti,fixed-factor-clock`); `reg` (max 1 items); `clocks` (max 1 items); `#clock-cells` (const `0`); `clock-output-names` (max 1 items); `ti,clock-div` (ref `/schemas/types.yaml#/definitions/uint32`; Fixed divider); `ti,clock-mult` (ref `/schemas/types.yaml#/definitions/uint32`; Fixed multiplier); `ti,set-rate-parent` (type `boolean`; Propagate to parent clock).

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
- Schema references: `ti,autoidle.yaml#`, `/schemas/types.yaml#/definitions/uint32`.
- Textual schema references: `/schemas/clock/ti/ti,fixed-factor-clock.yaml`, `/schemas/types.yaml#/definitions/uint32`.
Runtime integration is with clock framework consumers using `clocks`, `clock-names`, provider
cells such as `#clock-cells`, and driver-specific clock ID headers. Board `.dts` files
instantiate nodes that satisfy this schema; `make dt_binding_check` validates the schema and
inline examples, while `make dtbs_check` validates real board descriptions against the same
contract.

## Risks
- A missing or misspelled `compatible` value prevents the schema from matching the intended
hardware and can also keep the kernel driver from probing.
- The required list is small but strict; omitting one of `compatible`, `clocks`, `#clock-cells`,
`ti,clock-mult`, `ti,clock-div` should be caught by dt-schema before runtime.
- The closed property model is useful for catching typos, but newly needed board properties
require a schema update before DTS changes can pass validation.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/ti/ti,fixed-factor-clock.yaml` to parse this YAML, validate meta-schema rules, and compile its 1 inline example(s).
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/ti/ti,fixed-factor-clock.yaml` on affected board DTS files to confirm real nodes satisfy required properties, compatible choices, child-node names, and referenced common schemas.
- Useful negative tests remove one required property, change `compatible`, and add an undeclared property to confirm the schema catches the expected failures. Example seed: bus{; #address-cells = <1>;; #size-cells = <0>;; clock@1b4 {; compatible = "ti,fixed-factor-clock";
