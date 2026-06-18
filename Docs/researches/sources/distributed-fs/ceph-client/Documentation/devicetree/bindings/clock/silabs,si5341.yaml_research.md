# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/silabs,si5341.yaml

## Purpose
This file is a Linux Devicetree JSON-schema document for a clock provider/controller binding:
Silicon Labs Si5340/1/2/4/5 programmable i2c clock generator. It lives under `clock` bindings
and gives dt-schema a machine-readable contract for matching hardware nodes before those nodes
reach kernel drivers. The description says: Silicon Labs Si5340, Si5341 Si5342, Si5344 and
Si5345 programmable i2c clock generator. Reference [1] Si5341 Data Sheet
https://www.silabs.com/documents/public/data-sheets/Si5341-40-D-DataSheet.pdf [2] Si5341
Reference Manual https://www.silabs.com/documents/public/reference-manuals/Si5341-40-D-RM.pdf
[3] Si5345 Reference Manual https://www.silabs.com/documents/public/reference-
manuals/Si5345-44-42-D-RM.pdf The Si5341 and Si5340 are programmable i2c clock generators with
up to 10 output clocks. The chip contains a PLL that sources 5 (or 4) multisynth clocks,
which...

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/silabs,si5341.yaml#` with meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Compatible contract: `silabs,si5340`, `silabs,si5341`, `silabs,si5342`, `silabs,si5344`, `silabs,si5345`.
- Required properties: `compatible`, `reg`, `#clock-cells`, `#address-cells`, `#size-cells`, `clocks`, `clock-names`.
- Top-level framework properties: `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `#clock-cells`, `clock-output-names`, `#address-cells`, `#size-cells`.
- Vendor or device-specific extensions: `silabs,pll-m-num`, `silabs,pll-m-den`, `silabs,reprogram`, `silabs,xaxb-ext-clk`, `silabs,iovdd-33`.
- Other declared properties: `vdd-supply`, `vdda-supply`, `vdds-supply`.
- Child-node or pattern API: `^vddo[0-9]-supply$`; `^out@[0-9]$` requiring `reg`.
- Property detail signals: `compatible` (enum `silabs,si5340`, `silabs,si5341`, `silabs,si5342`, `silabs,si5344`, `silabs,si5345`); `reg` (max 1 items); `interrupts` (max 1 items; Interrupt for INTRb pin); `clocks` (1-4 items); `clock-names` (min 1 items); `#clock-cells` (const `2`; The first value is "0" for outputs, "1" for synthesizers. The second value is the output or synthesizer index.); `#address-cells` (const `1`); `#size-cells` (const `0`).

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
- Schema references: `/schemas/types.yaml#/definitions/uint32`.
- Textual schema references: `/schemas/silabs,si5341.yaml`, `/schemas/types.yaml#/definitions/uint32`.
Runtime integration is with clock framework consumers using `clocks`, `clock-names`, provider
cells such as `#clock-cells`, and driver-specific clock ID headers. Board `.dts` files
instantiate nodes that satisfy this schema; `make dt_binding_check` validates the schema and
inline examples, while `make dtbs_check` validates real board descriptions against the same
contract.

## Risks
- A missing or misspelled `compatible` value prevents the schema from matching the intended
hardware and can also keep the kernel driver from probing.
- The required list is small but strict; omitting one of `compatible`, `reg`, `#clock-cells`,
`#address-cells`, `#size-cells`, `clocks`, `clock-names` should be caught by dt-schema before
runtime.
- Child-node patterns must match exact unit-address/name conventions; mismatched child names may
be rejected or left unvalidated depending on the property-closure mode.
- The closed property model is useful for catching typos, but newly needed board properties
require a schema update before DTS changes can pass validation.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/silabs,si5341.yaml` to parse this YAML, validate meta-schema rules, and compile its 1 inline example(s).
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/silabs,si5341.yaml` on affected board DTS files to confirm real nodes satisfy required properties, compatible choices, child-node names, and referenced common schemas.
- Useful negative tests remove one required property, change `compatible`, and add an undeclared property to confirm the schema catches the expected failures. Example seed: i2c {; #address-cells = <1>;; #size-cells = <0>;; clock-generator@74 {; reg = <0x74>;
