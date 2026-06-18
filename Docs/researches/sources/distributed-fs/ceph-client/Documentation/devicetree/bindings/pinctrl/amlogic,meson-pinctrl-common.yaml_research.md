# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/amlogic,meson-pinctrl-common.yaml

## Purpose
This file is a Linux Devicetree JSON-schema document for a pin multiplexing controller binding:
Amlogic Meson pinmux controller. It lives in the pinctrl binding tree and gives dt-schema a machine-
readable contract for board DTS nodes before the kernel pinctrl/GPIO drivers consume those nodes
during probe.

The schema relies on title, compatible values, and property constraints rather than a long description block.

The binding is maintained in-source by Neil Armstrong <neil.armstrong@linaro.org>.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/pinctrl/amlogic,meson-pinctrl-common.yaml#` with meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Compatible contract: none declared.
- Required properties: `ranges`, `#address-cells`, `#size-cells`.
- Top-level framework properties: `#address-cells`, `#size-cells`.
- Vendor or device-specific extensions: none declared.
- Other declared top-level properties: `ranges`.
- Child-node or reusable schema API: local definitions `meson-gpio`, `meson-pins`.
- Property detail signals: ranges; #address-cells (enum `1`, `2`); #size-cells (enum `1`, `2`).

## Control Flow
There is no imperative execution path in this YAML. Validation starts when dt-schema selects this
document for a node whose `compatible` value matches the schema, checks the required list, evaluates
referenced common pinctrl/GPIO schemas, applies property constraints, then walks child-node patterns
and conditional branches.

This file contains 2 `allOf`, 0 `oneOf`, 0 `anyOf`, and 0 `if` blocks. Property closure: top-level
`additionalProperties: true` allows extensions beyond declared keys.

## State and Persistence Behavior
The binding stores no runtime state. It persists as source-controlled schema text, while the state
it describes persists in DTS/DTB data: register windows, GPIO provider cell counts, interrupt
wiring, pin groups, mux functions, drive strengths, pulls, and optional child pin configuration
nodes. Kernel drivers consume the validated DT data at boot or device probe and then program
hardware pin mux, pad, and GPIO state; this YAML only constrains that data before runtime.

## Dependencies and Integration Points
- Schema references: `pinctrl.yaml#`, `pincfg-node.yaml#`, `pinmux-node.yaml#`.
- Textual schema references: `/schemas/pinctrl/amlogic,meson-pinctrl-common.yaml#`.
Runtime integration is with Linux pinctrl and GPIO framework drivers selected by `compatible`. Board
`.dts` files instantiate nodes that satisfy this schema; `make dt_binding_check` validates the
binding and inline examples, while `make dtbs_check` validates real board descriptions against the
same contract.

## Risks
- A missing or misspelled `compatible` value prevents both schema matching and driver binding.
- Omitting required fields such as `ranges`, `#address-cells`, `#size-cells` should fail dt-schema validation before boot.
- Open or partially open property handling can let board-specific typos escape schema validation and surface only at driver probe time.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/amlogic,meson-pinctrl-common.yaml` to parse this YAML, validate meta-schema rules, and compile its 0 inline example(s).
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/amlogic,meson-pinctrl-common.yaml` on affected board DTS files to confirm real nodes satisfy required properties, compatible choices, child node names, and referenced common schemas.
- Useful negative tests remove one required property, change `compatible`, add a bogus pin group/function, and add an undeclared property where closure is enabled.
