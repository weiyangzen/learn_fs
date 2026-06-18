# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/sprd,sc9863a-clk.yaml

## Purpose
This file is a Linux Devicetree JSON-schema document for a clock provider/controller binding:
SC9863A Clock Control Unit. It lives under `clock` bindings and gives dt-schema a machine-
readable contract for matching hardware nodes before those nodes reach kernel drivers. The file
does not carry a long description, so its role is inferred from title, path, and schema
constraints.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/clock/sprd,sc9863a-clk.yaml#` with meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Compatible contract: `sprd,sc9863a-ap-clk`, `sprd,sc9863a-aon-clk`, `sprd,sc9863a-apahb-gate`, `sprd,sc9863a-pmu-gate`, `sprd,sc9863a-aonapb-gate`, `sprd,sc9863a-pll`, `sprd,sc9863a-mpll`, `sprd,sc9863a-rpll`, `sprd,sc9863a-dpll`, `sprd,sc9863a-mm-gate`, `sprd,sc9863a-mm-clk`, `sprd,sc9863a-apapb-gate`.
- Required properties: `compatible`, `#clock-cells`.
- Top-level framework properties: `compatible`, `reg`, `clocks`, `clock-names`, `#clock-cells`.
- Vendor or device-specific extensions: No vendor-prefixed top-level extension properties are declared..
- Other declared properties: No additional generic top-level properties beyond the highlighted framework/vendor keys..
- Child-node or pattern API: No `patternProperties` or object-valued child-node contract is declared..
- Property detail signals: `compatible` (enum `sprd,sc9863a-ap-clk`, `sprd,sc9863a-aon-clk`, `sprd,sc9863a-apahb-gate`, `sprd,sc9863a-pmu-gate`, `sprd,sc9863a-aonapb-gate`, `sprd,sc9863a-pll`, `sprd,sc9863a-mpll`, `sprd,sc9863a-rpll` (+4 more)); `reg` (max 1 items); `clocks` (1-4 items; The input parent clock(s) phandle for this clock, only list fixed clocks which are declared in devicetree.); `clock-names` (min 1 items); `#clock-cells` (const `1`).

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
- Schema references: No `$ref` dependencies were found in the parsed schema..
- Textual schema references: `/schemas/clock/sprd,sc9863a-clk.yaml`.
Runtime integration is with clock framework consumers using `clocks`, `clock-names`, provider
cells such as `#clock-cells`, and driver-specific clock ID headers. Board `.dts` files
instantiate nodes that satisfy this schema; `make dt_binding_check` validates the schema and
inline examples, while `make dtbs_check` validates real board descriptions against the same
contract.

## Risks
- A missing or misspelled `compatible` value prevents the schema from matching the intended
hardware and can also keep the kernel driver from probing.
- The required list is small but strict; omitting one of `compatible`, `#clock-cells` should be
caught by dt-schema before runtime.
- Conditional and choice schemas can reject otherwise plausible nodes when a compatible-specific
branch changes required properties, item counts, or child-node limits.
- The closed property model is useful for catching typos, but newly needed board properties
require a schema update before DTS changes can pass validation.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/sprd,sc9863a-clk.yaml` to parse this YAML, validate meta-schema rules, and compile its 2 inline example(s).
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/sprd,sc9863a-clk.yaml` on affected board DTS files to confirm real nodes satisfy required properties, compatible choices, child-node names, and referenced common schemas.
- Useful negative tests remove one required property, change `compatible`, and add an undeclared property to confirm the schema catches the expected failures. Example seed: ap_clk: clock-controller@21500000 {; compatible = "sprd,sc9863a-ap-clk";; reg = <0x21500000 0x1000>;; clocks = <&ext_26m>, <&ext_32k>;; clock-names = "ext-26m", "ext-32k";
