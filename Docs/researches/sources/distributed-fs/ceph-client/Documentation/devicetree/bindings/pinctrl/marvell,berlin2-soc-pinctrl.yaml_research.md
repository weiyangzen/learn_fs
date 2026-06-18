# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/marvell,berlin2-soc-pinctrl.yaml

## Purpose
This file is a Linux Devicetree JSON-schema document for a pin controller binding: Marvell Berlin
pin-controller driver. It lives in the pinctrl binding tree and gives dt-schema a machine-readable
contract for board DTS nodes before the kernel pinctrl/GPIO drivers consume those nodes during
probe.

Pin control registers are part of both chip controller and system controller register sets. Pin
controller nodes should be a sub-node of either the chip controller or system controller node. The
pins controlled are organized in groups, so no actual pin information is needed. A pin-controller
node should contain subnodes representing the pin group configurations, one per function. Each
subnode has the group name and the muxing function used. Be aware the Marvell Berlin datasheets use
the keyword 'mode' for what is called a 'function' in the pin-controller subsystem.

The binding is maintained in-source by Antoine Tenart <atenart@kernel.org>, Jisheng Zhang
<jszhang@kernel.org>.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/pinctrl/marvell,berlin2-soc-pinctrl.yaml#` with meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Compatible contract: `marvell,berlin2-soc-pinctrl`, `marvell,berlin2-system-pinctrl`, `marvell,berlin2cd-soc-pinctrl`, `marvell,berlin2cd-system-pinctrl`, `marvell,berlin2q-soc-pinctrl`, `marvell,berlin2q-system-pinctrl`, `marvell,berlin4ct-avio-pinctrl`, `marvell,berlin4ct-soc-pinctrl`, `marvell,berlin4ct-system-pinctrl`, `syna,as370-soc-pinctrl`.
- Required properties: none declared.
- Top-level framework properties: `compatible`, `reg`.
- Vendor or device-specific extensions: none declared.
- Other declared top-level properties: none declared.
- Child-node or reusable schema API: no named child-node API or pattern child-node contract is declared.
- Property detail signals: compatible; reg (maxItems 1).

## Control Flow
There is no imperative execution path in this YAML. Validation starts when dt-schema selects this
document for a node whose `compatible` value matches the schema, checks the required list, evaluates
referenced common pinctrl/GPIO schemas, applies property constraints, then walks child-node patterns
and conditional branches.

This file contains 1 `allOf`, 0 `oneOf`, 0 `anyOf`, and 1 `if` blocks. Property closure: no explicit
top-level closure keyword is present in the parsed schema.

## State and Persistence Behavior
The binding stores no runtime state. It persists as source-controlled schema text, while the state
it describes persists in DTS/DTB data: register windows, GPIO provider cell counts, interrupt
wiring, pin groups, mux functions, drive strengths, pulls, and optional child pin configuration
nodes. Kernel drivers consume the validated DT data at boot or device probe and then program
hardware pin mux, pad, and GPIO state; this YAML only constrains that data before runtime.

## Dependencies and Integration Points
- Schema references: `/schemas/pinctrl/pinmux-node.yaml#`, `/schemas/types.yaml#/definitions/string-array`, `/schemas/types.yaml#/definitions/string`.
- Textual schema references: `/schemas/pinctrl/marvell,berlin2-soc-pinctrl.yaml#`, `/schemas/pinctrl/pinmux-node.yaml#`, `/schemas/types.yaml#/definitions/string-array`, `/schemas/types.yaml#/definitions/string`.
Runtime integration is with Linux pinctrl and GPIO framework drivers selected by `compatible`. Board
`.dts` files instantiate nodes that satisfy this schema; `make dt_binding_check` validates the
binding and inline examples, while `make dtbs_check` validates real board descriptions against the
same contract.

## Risks
- A missing or misspelled `compatible` value prevents both schema matching and driver binding.
- Open or partially open property handling can let board-specific typos escape schema validation and surface only at driver probe time.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/marvell,berlin2-soc-pinctrl.yaml` to parse this YAML, validate meta-schema rules, and compile its 1 inline example(s).
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/marvell,berlin2-soc-pinctrl.yaml` on affected board DTS files to confirm real nodes satisfy required properties, compatible choices, child node names, and referenced common schemas.
- Useful negative tests remove one required property, change `compatible`, and add an undeclared property where closure is enabled. Example seed: pinctrl {; compatible = "marvell,berlin2q-system-pinctrl";; uart0-pmux {; groups = "GSM12";.
