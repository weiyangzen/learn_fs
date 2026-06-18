# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/ti/ti,autoidle.yaml

## Purpose
This file is a Linux Devicetree JSON-schema document for a clock provider/controller binding: TI
autoidle clock. It lives under `clock` bindings and gives dt-schema a machine-readable contract
for matching hardware nodes before those nodes reach kernel drivers. The description says: Some
clocks in TI SoC support the autoidle feature. These properties are applicable only if the clock
supports autoidle feature. It assumes a register mapped clock which can be put to idle
automatically by hardware based on usage and configuration bit setting. Autoidle clock is never
an individual clock, it is always a derivative of some basic clock like a gate, divider, or
fixed-factor.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/clock/ti/ti,autoidle.yaml#` with meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Compatible contract: No explicit compatible string was extracted from the parsed `compatible` schema; consumers rely on the surrounding schema constraints..
- Required properties: No top-level `required` list is declared..
- Top-level framework properties: No standard framework property from the clock/interrupt/reset/regulator shortlist is declared at top level..
- Vendor or device-specific extensions: `ti,autoidle-shift`, `ti,invert-autoidle-bit`.
- Other declared properties: No additional generic top-level properties beyond the highlighted framework/vendor keys..
- Child-node or pattern API: No `patternProperties` or object-valued child-node contract is declared..
- Property detail signals: `ti,autoidle-shift` (ref `/schemas/types.yaml#/definitions/uint32`; bit shift of the autoidle enable bit for the clock); `ti,invert-autoidle-bit` (type `boolean`; autoidle is enabled by setting the bit to 0).

## Control Flow
There is no imperative execution path in this YAML. Validation control flow starts when dt-
schema selects this document for a node whose `compatible` data matches the compatible schema,
then checks the top-level required list, evaluates referenced common schemas, applies property
constraints, and finally walks child-node patterns or named child objects. This file contains 0
`allOf`, 0 `oneOf`, 0 `anyOf`, and 0 `if` blocks, so conditional branches are part of the
accepted DTS shape where those counts are nonzero. The top-level schema leaves extra properties
open with `additionalProperties: true`.

## State and Persistence Behavior
The binding itself stores no runtime state and persists only as source-controlled schema text.
The state it describes is persistent board firmware data in DTS/DTB form: register ranges,
clock/reset/interrupt wiring, provider cells, power or GPIO relationships, and optional child
nodes. Kernel drivers consume that data during probe and then program hardware state such as
clocks, counters, connector roles, cpufreq domains, or crypto engines; this YAML only constrains
that data before boot-time use.

## Dependencies and Integration Points
- Schema references: `/schemas/types.yaml#/definitions/uint32`.
- Textual schema references: `/schemas/clock/ti/ti,autoidle.yaml`, `/schemas/types.yaml#/definitions/uint32`.
Runtime integration is with clock framework consumers using `clocks`, `clock-names`, provider
cells such as `#clock-cells`, and driver-specific clock ID headers. Board `.dts` files
instantiate nodes that satisfy this schema; `make dt_binding_check` validates the schema and
inline examples, while `make dtbs_check` validates real board descriptions against the same
contract.

## Risks
- A missing or misspelled `compatible` value prevents the schema from matching the intended
hardware and can also keep the kernel driver from probing.
- Because the top-level closure is not explicitly false, review should ensure common schemas still
prevent accidental typo properties from being accepted.
- There is no inline example, reducing regression coverage for real DTS shape changes in binding
checks.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/ti/ti,autoidle.yaml` to parse this YAML, validate meta-schema rules, and compile its 0 inline example(s).
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/ti/ti,autoidle.yaml` on affected board DTS files to confirm real nodes satisfy required properties, compatible choices, child-node names, and referenced common schemas.
- Useful negative tests remove one required property, change `compatible`, and add an undeclared property to confirm the schema catches the expected failures. Example seed: No inline DTS example is present.
