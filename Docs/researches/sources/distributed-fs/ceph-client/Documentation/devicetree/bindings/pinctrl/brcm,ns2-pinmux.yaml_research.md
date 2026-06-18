# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/brcm,ns2-pinmux.yaml

## Purpose
This file is a Linux Devicetree JSON-schema document for a pin multiplexing controller binding:
Broadcom Northstar2 IOMUX Controller. It lives in the pinctrl binding tree and gives dt-schema a
machine-readable contract for board DTS nodes before the kernel pinctrl/GPIO drivers consume those
nodes during probe.

The schema relies on title, compatible values, and property constraints rather than a long description block.

The binding is maintained in-source by Ray Jui <rjui@broadcom.com>, Scott Branden
<sbranden@broadcom.com>.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/pinctrl/brcm,ns2-pinmux.yaml#` with meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Compatible contract: `brcm,ns2-pinmux`.
- Required properties: `compatible`, `reg`.
- Top-level framework properties: `compatible`, `reg`.
- Vendor or device-specific extensions: none declared.
- Other declared top-level properties: none declared.
- Child-node or reusable schema API: no named child-node API or pattern child-node contract is declared.
- Property detail signals: compatible (const `brcm,ns2-pinmux`); reg (maxItems 3).

## Control Flow
There is no imperative execution path in this YAML. Validation starts when dt-schema selects this
document for a node whose `compatible` value matches the schema, checks the required list, evaluates
referenced common pinctrl/GPIO schemas, applies property constraints, then walks child-node patterns
and conditional branches.

This file contains 1 `allOf`, 1 `oneOf`, 0 `anyOf`, and 0 `if` blocks. Property closure: no explicit
top-level closure keyword is present in the parsed schema.

## State and Persistence Behavior
The binding stores no runtime state. It persists as source-controlled schema text, while the state
it describes persists in DTS/DTB data: register windows, GPIO provider cell counts, interrupt
wiring, pin groups, mux functions, drive strengths, pulls, and optional child pin configuration
nodes. Kernel drivers consume the validated DT data at boot or device probe and then program
hardware pin mux, pad, and GPIO state; this YAML only constrains that data before runtime.

## Dependencies and Integration Points
- Schema references: `/schemas/pinctrl/pincfg-node.yaml#`, `/schemas/pinctrl/pinmux-node.yaml#`, `/schemas/types.yaml#/definitions/string`.
- Textual schema references: `/schemas/pinctrl/brcm,ns2-pinmux.yaml#`, `/schemas/pinctrl/pincfg-node.yaml#`, `/schemas/pinctrl/pinmux-node.yaml#`, `/schemas/types.yaml#/definitions/string`.
Runtime integration is with Linux pinctrl and GPIO framework drivers selected by `compatible`. Board
`.dts` files instantiate nodes that satisfy this schema; `make dt_binding_check` validates the
binding and inline examples, while `make dtbs_check` validates real board descriptions against the
same contract.

## Risks
- A missing or misspelled `compatible` value prevents both schema matching and driver binding.
- Omitting required fields such as `compatible`, `reg` should fail dt-schema validation before boot.
- Open or partially open property handling can let board-specific typos escape schema validation and surface only at driver probe time.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/brcm,ns2-pinmux.yaml` to parse this YAML, validate meta-schema rules, and compile its 1 inline example(s).
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/brcm,ns2-pinmux.yaml` on affected board DTS files to confirm real nodes satisfy required properties, compatible choices, child node names, and referenced common schemas.
- Useful negative tests remove one required property, change `compatible`, and add an undeclared property where closure is enabled. Example seed: pinctrl@6501d130 {; compatible = "brcm,ns2-pinmux";; reg = <0x6501d130 0x08>,; <0x660a0028 0x04>,; <0x660009b0 0x40>;.
