# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/silabs,si5351.yaml

## Purpose
This file is a Linux Devicetree JSON-schema document for a clock provider/controller binding:
Silicon Labs Si5351A/B/C programmable I2C clock generators. It lives under `clock` bindings and
gives dt-schema a machine-readable contract for matching hardware nodes before those nodes reach
kernel drivers. The description says: The Silicon Labs Si5351A/B/C are programmable I2C clock
generators with up to 8 outputs. Si5351A also has a reduced pin-count package (10-MSOP) where
only 3 output clocks are accessible. The internal structure of the clock generators can be found
in [1]. [1] Si5351A/B/C Data Sheet
https://www.skyworksinc.com/-/media/Skyworks/SL/documents/public/data-sheets/Si5351-B.pdf

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/clock/silabs,si5351.yaml#` with meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Compatible contract: `silabs,si5351a`, `silabs,si5351a-msop`, `silabs,si5351b`, `silabs,si5351c`.
- Required properties: `reg`, `#address-cells`, `#size-cells`, `#clock-cells`, `clocks`, `clock-names`.
- Top-level framework properties: `compatible`, `reg`, `clocks`, `clock-names`, `#clock-cells`, `#address-cells`, `#size-cells`.
- Vendor or device-specific extensions: `silabs,pll-source`, `silabs,pll-reset-mode`.
- Other declared properties: No additional generic top-level properties beyond the highlighted framework/vendor keys..
- Child-node or pattern API: `^clkout@[0-7]$` requiring `reg`.
- Property detail signals: `compatible` (enum `silabs,si5351a`, `silabs,si5351a-msop`, `silabs,si5351b`, `silabs,si5351c`); `reg` (enum `96`, `97`); `clocks` (1-2 items); `clock-names` (min 1 items); `#clock-cells` (const `1`); `#address-cells` (const `1`); `#size-cells` (const `0`); `silabs,pll-source` (ref `/schemas/types.yaml#/definitions/uint32-matrix`; A list of cell pairs containing a PLL index and its source. Allows to overwrite clock source of the internal PLLs.).

## Control Flow
There is no imperative execution path in this YAML. Validation control flow starts when dt-
schema selects this document for a node whose `compatible` data matches the compatible schema,
then checks the top-level required list, evaluates referenced common schemas, applies property
constraints, and finally walks child-node patterns or named child objects. This file contains 2
`allOf`, 0 `oneOf`, 0 `anyOf`, and 3 `if` blocks, so conditional branches are part of the
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
- Schema references: `/schemas/types.yaml#/definitions/uint32-matrix`, `/schemas/types.yaml#/definitions/uint32`.
- Textual schema references: `/schemas/clock/silabs,si5351.yaml`, `/schemas/types.yaml#/definitions/uint32`, `/schemas/types.yaml#/definitions/uint32-matrix`.
Runtime integration is with clock framework consumers using `clocks`, `clock-names`, provider
cells such as `#clock-cells`, and driver-specific clock ID headers. Board `.dts` files
instantiate nodes that satisfy this schema; `make dt_binding_check` validates the schema and
inline examples, while `make dtbs_check` validates real board descriptions against the same
contract.

## Risks
- A missing or misspelled `compatible` value prevents the schema from matching the intended
hardware and can also keep the kernel driver from probing.
- The required list is small but strict; omitting one of `reg`, `#address-cells`, `#size-cells`,
`#clock-cells`, `clocks`, `clock-names` should be caught by dt-schema before runtime.
- Conditional and choice schemas can reject otherwise plausible nodes when a compatible-specific
branch changes required properties, item counts, or child-node limits.
- Child-node patterns must match exact unit-address/name conventions; mismatched child names may
be rejected or left unvalidated depending on the property-closure mode.
- The closed property model is useful for catching typos, but newly needed board properties
require a schema update before DTS changes can pass validation.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/silabs,si5351.yaml` to parse this YAML, validate meta-schema rules, and compile its 1 inline example(s).
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/silabs,si5351.yaml` on affected board DTS files to confirm real nodes satisfy required properties, compatible choices, child-node names, and referenced common schemas.
- Useful negative tests remove one required property, change `compatible`, and add an undeclared property to confirm the schema catches the expected failures. Example seed: i2c {; #address-cells = <1>;; #size-cells = <0>;; clock-generator@60 {; compatible = "silabs,si5351a-msop";
