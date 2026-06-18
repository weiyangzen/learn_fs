# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/aspeed,ast2500-pinctrl.yaml

## Purpose
This file is a Linux Devicetree JSON-schema document for a pin controller binding: ASPEED AST2500
Pin Controller. It lives in the pinctrl binding tree and gives dt-schema a machine-readable contract
for board DTS nodes before the kernel pinctrl/GPIO drivers consume those nodes during probe.

The pin controller node should be the child of a syscon node with the required property: -
compatible: Should be one of the following: "aspeed,ast2500-scu", "syscon", "simple-mfd"
"aspeed,g5-scu", "syscon", "simple-mfd" Refer to the bindings described in
Documentation/devicetree/bindings/mfd/syscon.yaml

The binding is maintained in-source by Andrew Jeffery <andrew@aj.id.au>.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/pinctrl/aspeed,ast2500-pinctrl.yaml#` with meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Compatible contract: `aspeed,ast2500-pinctrl`.
- Required properties: `compatible`, `aspeed,external-nodes`.
- Top-level framework properties: `compatible`, `reg`.
- Vendor or device-specific extensions: `aspeed,external-nodes`.
- Other declared top-level properties: none declared.
- Child-node or reusable schema API: no named child-node API or pattern child-node contract is declared.
- Property detail signals: compatible (const `aspeed,ast2500-pinctrl`); reg (maxItems 2); aspeed,external-nodes (maxItems 2; minItems 2; A cell of phandles to external controller nodes: 0: compatible with "aspeed,ast2500-gfx", "syscon...; ref `/schemas/types.yaml#/definitions/phandle-array`).

## Control Flow
There is no imperative execution path in this YAML. Validation starts when dt-schema selects this
document for a node whose `compatible` value matches the schema, checks the required list, evaluates
referenced common pinctrl/GPIO schemas, applies property constraints, then walks child-node patterns
and conditional branches.

This file contains 1 `allOf`, 0 `oneOf`, 0 `anyOf`, and 0 `if` blocks. Property closure: no explicit
top-level closure keyword is present in the parsed schema.

## State and Persistence Behavior
The binding stores no runtime state. It persists as source-controlled schema text, while the state
it describes persists in DTS/DTB data: register windows, GPIO provider cell counts, interrupt
wiring, pin groups, mux functions, drive strengths, pulls, and optional child pin configuration
nodes. Kernel drivers consume the validated DT data at boot or device probe and then program
hardware pin mux, pad, and GPIO state; this YAML only constrains that data before runtime.

## Dependencies and Integration Points
- Schema references: `/schemas/types.yaml#/definitions/phandle-array`, `pinmux-node.yaml#`, `pinctrl.yaml#`.
- Example/header integration: `dt-bindings/clock/aspeed-clock.h`.
- Textual schema references: `/schemas/pinctrl/aspeed,ast2500-pinctrl.yaml#`, `/schemas/types.yaml#/definitions/phandle-array`.
Runtime integration is with Linux pinctrl and GPIO framework drivers selected by `compatible`. Board
`.dts` files instantiate nodes that satisfy this schema; `make dt_binding_check` validates the
binding and inline examples, while `make dtbs_check` validates real board descriptions against the
same contract.

## Risks
- A missing or misspelled `compatible` value prevents both schema matching and driver binding.
- Omitting required fields such as `compatible`, `aspeed,external-nodes` should fail dt-schema validation before boot.
- Open or partially open property handling can let board-specific typos escape schema validation and surface only at driver probe time.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/aspeed,ast2500-pinctrl.yaml` to parse this YAML, validate meta-schema rules, and compile its 1 inline example(s).
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/aspeed,ast2500-pinctrl.yaml` on affected board DTS files to confirm real nodes satisfy required properties, compatible choices, child node names, and referenced common schemas.
- Useful negative tests remove one required property, change `compatible`, and add an undeclared property where closure is enabled. Example seed: #include <dt-bindings/clock/aspeed-clock.h>; scu@1e6e2000 {; compatible = "aspeed,ast2500-scu", "syscon", "simple-mfd";; reg = <0x1e6e2000 0x1a8>;; #clock-cells = <1>;.
