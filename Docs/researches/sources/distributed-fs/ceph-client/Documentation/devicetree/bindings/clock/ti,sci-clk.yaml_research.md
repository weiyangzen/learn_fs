# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/ti,sci-clk.yaml

## Purpose
This file is a Linux Devicetree JSON-schema document for a clock provider/controller binding:
TI-SCI clock controller. It lives under `clock` bindings and gives dt-schema a machine-readable
contract for matching hardware nodes before those nodes reach kernel drivers. The description
says: Some TI SoCs contain a system controller (like the Power Management Micro Controller
(PMMC) on Keystone 66AK2G SoC) that are responsible for controlling the state of the various
hardware modules present on the SoC. Communication between the host processor running an OS and
the system controller happens through a protocol called TI System Control Interface (TI-SCI
protocol). This clock controller node uses the TI SCI protocol to perform various clock
management of various hardware modules (devices) present on the SoC. This node must be a child
node of the associated TI-SCI system controller node.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/clock/ti,sci-clk.yaml#` with meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Compatible contract: `ti,k2g-sci-clk`.
- Required properties: No top-level `required` list is declared..
- Top-level framework properties: `compatible`, `#clock-cells`.
- Vendor or device-specific extensions: No vendor-prefixed top-level extension properties are declared..
- Other declared properties: `$nodename`.
- Child-node or pattern API: No `patternProperties` or object-valued child-node contract is declared..
- Property detail signals: `compatible` (const `ti,k2g-sci-clk`); `#clock-cells` (const `2`; The two cells represent values that the TI-SCI controller defines. The first cell should contain the device ID. The s...).

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
- Schema references: No `$ref` dependencies were found in the parsed schema..
- Textual schema references: `/schemas/clock/ti,sci-clk.yaml`.
Runtime integration is with clock framework consumers using `clocks`, `clock-names`, provider
cells such as `#clock-cells`, and driver-specific clock ID headers. Board `.dts` files
instantiate nodes that satisfy this schema; `make dt_binding_check` validates the schema and
inline examples, while `make dtbs_check` validates real board descriptions against the same
contract.

## Risks
- A missing or misspelled `compatible` value prevents the schema from matching the intended
hardware and can also keep the kernel driver from probing.
- The closed property model is useful for catching typos, but newly needed board properties
require a schema update before DTS changes can pass validation.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/ti,sci-clk.yaml` to parse this YAML, validate meta-schema rules, and compile its 1 inline example(s).
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/ti,sci-clk.yaml` on affected board DTS files to confirm real nodes satisfy required properties, compatible choices, child-node names, and referenced common schemas.
- Useful negative tests remove one required property, change `compatible`, and add an undeclared property to confirm the schema catches the expected failures. Example seed: k3_clks: clock-controller {; compatible = "ti,k2g-sci-clk";; #clock-cells = <2>;; };
