# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/ti/ti,gate-clock.yaml

## Purpose
This file is a Linux Devicetree JSON-schema document for a clock provider/controller binding:
Texas Instruments gate clock. It lives under `clock` bindings and gives dt-schema a machine-
readable contract for matching hardware nodes before those nodes reach kernel drivers. The
description says: *Deprecated design pattern: one node per clock* This clock is quite much
similar to the basic gate-clock [1], however, it supports a number of additional features. If no
register is provided for this clock, the code assumes that a clockdomain will be controlled
instead and the corresponding hw-ops for that is used. [1]
Documentation/devicetree/bindings/clock/gpio-gate-clock.yaml [2]
Documentation/devicetree/bindings/clock/ti/clockdomain.txt

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/clock/ti/ti,gate-clock.yaml#` with meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Compatible contract: `ti,gate-clock`, `ti,wait-gate-clock`, `ti,dss-gate-clock`, `ti,am35xx-gate-clock`, `ti,clkdm-gate-clock`, `ti,hsdiv-gate-clock`, `ti,composite-gate-clock`, `ti,composite-no-wait-gate-clock`.
- Required properties: No top-level `required` list is declared..
- Top-level framework properties: `compatible`, `reg`, `clocks`, `#clock-cells`, `clock-output-names`.
- Vendor or device-specific extensions: `ti,bit-shift`, `ti,set-bit-to-disable`, `ti,set-rate-parent`.
- Other declared properties: No additional generic top-level properties beyond the highlighted framework/vendor keys..
- Child-node or pattern API: No `patternProperties` or object-valued child-node contract is declared..
- Property detail signals: `compatible` (enum `ti,gate-clock`, `ti,wait-gate-clock`, `ti,dss-gate-clock`, `ti,am35xx-gate-clock`, `ti,clkdm-gate-clock`, `ti,hsdiv-gate-clock`, `ti,composite-gate-clock`, `ti,composite-no-wait-gate-clock`); `reg` (max 1 items); `#clock-cells` (const `0`); `clock-output-names` (max 1 items); `ti,bit-shift` (ref `/schemas/types.yaml#/definitions/uint32`; Number of bits to shift the bit-mask); `ti,set-bit-to-disable` (type `boolean`; Inverts default gate programming. Setting the bit gates the clock and clearing the bit ungates the clock.); `ti,set-rate-parent` (type `boolean`; clk_set_rate is propagated to parent clock,).

## Control Flow
There is no imperative execution path in this YAML. Validation control flow starts when dt-
schema selects this document for a node whose `compatible` data matches the compatible schema,
then checks the top-level required list, evaluates referenced common schemas, applies property
constraints, and finally walks child-node patterns or named child objects. This file contains 0
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
- Schema references: `/schemas/types.yaml#/definitions/uint32`.
- Textual schema references: `/schemas/clock/ti/ti,gate-clock.yaml`, `/schemas/types.yaml#/definitions/uint32`.
Runtime integration is with clock framework consumers using `clocks`, `clock-names`, provider
cells such as `#clock-cells`, and driver-specific clock ID headers. Board `.dts` files
instantiate nodes that satisfy this schema; `make dt_binding_check` validates the schema and
inline examples, while `make dtbs_check` validates real board descriptions against the same
contract.

## Risks
- A missing or misspelled `compatible` value prevents the schema from matching the intended
hardware and can also keep the kernel driver from probing.
- Conditional and choice schemas can reject otherwise plausible nodes when a compatible-specific
branch changes required properties, item counts, or child-node limits.
- The closed property model is useful for catching typos, but newly needed board properties
require a schema update before DTS changes can pass validation.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/ti/ti,gate-clock.yaml` to parse this YAML, validate meta-schema rules, and compile its 2 inline example(s).
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/ti/ti,gate-clock.yaml` on affected board DTS files to confirm real nodes satisfy required properties, compatible choices, child-node names, and referenced common schemas.
- Useful negative tests remove one required property, change `compatible`, and add an undeclared property to confirm the schema catches the expected failures. Example seed: bus {; #address-cells = <1>;; #size-cells = <0>;; clock-controller@a00 {; #clock-cells = <0>;
