# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/ti/ti,mux-clock.yaml

## Purpose
This file is a Linux Devicetree JSON-schema document for a clock provider/controller binding:
Texas Instruments mux clock. It lives under `clock` bindings and gives dt-schema a machine-
readable contract for matching hardware nodes before those nodes reach kernel drivers. The
description says: This clock assumes a register-mapped multiplexer with multiple inpt clock
signals or parents, one of which can be selected as output. This clock does not gate or adjust
the parent rate via a divider or multiplier. By default the "clocks" property lists the parents
in the same order as they are programmed into the register. E.g: clocks = <&foo_clock>,
<&bar_clock>, <&baz_clock>; Results in programming the register as follows: register value
selected parent clock 0 foo_clock 1 bar_clock 2 baz_clock Some clock controller IPs do not allow
a value of zero to be programmed into the register, instead in...

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/clock/ti/ti,mux-clock.yaml#` with meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Compatible contract: `ti,mux-clock`, `ti,composite-mux-clock`.
- Required properties: `compatible`, `#clock-cells`, `clocks`, `reg`.
- Top-level framework properties: `compatible`, `reg`, `clocks`, `#clock-cells`, `clock-output-names`.
- Vendor or device-specific extensions: `ti,bit-shift`, `ti,index-starts-at-one`, `ti,set-rate-parent`, `ti,latch-bit`.
- Other declared properties: No additional generic top-level properties beyond the highlighted framework/vendor keys..
- Child-node or pattern API: No `patternProperties` or object-valued child-node contract is declared..
- Property detail signals: `compatible` (enum `ti,mux-clock`, `ti,composite-mux-clock`); `reg` (max 1 items); `#clock-cells` (const `0`); `clock-output-names` (max 1 items); `ti,bit-shift` (ref `/schemas/types.yaml#/definitions/uint32`; Number of bits to shift the bit-mask); `ti,index-starts-at-one` (type `boolean`; Valid input select programming starts at 1, not zero); `ti,set-rate-parent` (type `boolean`; clk_set_rate is propagated to parent clock, not supported by the composite-mux-clock subtype.); `ti,latch-bit` (ref `/schemas/types.yaml#/definitions/uint32`; Latch the mux value to HW, only needed if the register access requires this. As an example, dra7x DPLL_GMAC H14 muxin...).

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
- Textual schema references: `/schemas/clock/ti/ti,mux-clock.yaml`, `/schemas/types.yaml#/definitions/uint32`.
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
- Conditional and choice schemas can reject otherwise plausible nodes when a compatible-specific
branch changes required properties, item counts, or child-node limits.
- The closed property model is useful for catching typos, but newly needed board properties
require a schema update before DTS changes can pass validation.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/ti/ti,mux-clock.yaml` to parse this YAML, validate meta-schema rules, and compile its 1 inline example(s).
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/ti/ti,mux-clock.yaml` on affected board DTS files to confirm real nodes satisfy required properties, compatible choices, child-node names, and referenced common schemas.
- Useful negative tests remove one required property, change `compatible`, and add an undeclared property to confirm the schema catches the expected failures. Example seed: bus {; #address-cells = <1>;; #size-cells = <0>;; clock-controller@110 {; compatible = "ti,mux-clock";
