# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/brcm,ns-pinmux.yaml

## Purpose
This file is a Linux Devicetree JSON-schema document for a pin multiplexing controller binding:
Broadcom Northstar pins mux controller. It lives in the pinctrl binding tree and gives dt-schema a
machine-readable contract for board DTS nodes before the kernel pinctrl/GPIO drivers consume those
nodes during probe.

Some of Northstar SoCs's pins can be used for various purposes thanks to the mux controller. This
binding allows describing mux controller and listing available functions. They can be referenced
later by other bindings to let system configure controller correctly. A list of pins varies across
chipsets so few bindings are available.

The binding is maintained in-source by Rafał Miłecki <rafal@milecki.pl>.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/pinctrl/brcm,ns-pinmux.yaml#` with meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Compatible contract: `brcm,bcm4708-pinmux`, `brcm,bcm4709-pinmux`, `brcm,bcm53012-pinmux`.
- Required properties: `reg`, `reg-names`.
- Top-level framework properties: `compatible`, `reg`, `reg-names`.
- Vendor or device-specific extensions: none declared.
- Other declared top-level properties: none declared.
- Child-node or reusable schema API: patternProperties `-pins$`.
- Property detail signals: compatible (enum `brcm,bcm4708-pinmux`, `brcm,bcm4709-pinmux`, `brcm,bcm53012-pinmux`); reg (maxItems 1); reg-names (const `cru_gpio_control`).

## Control Flow
There is no imperative execution path in this YAML. Validation starts when dt-schema selects this
document for a node whose `compatible` value matches the schema, checks the required list, evaluates
referenced common pinctrl/GPIO schemas, applies property constraints, then walks child-node patterns
and conditional branches.

This file contains 1 `allOf`, 0 `oneOf`, 0 `anyOf`, and 1 `if` blocks. Property closure: top-level
`additionalProperties: false` rejects undeclared properties.

## State and Persistence Behavior
The binding stores no runtime state. It persists as source-controlled schema text, while the state
it describes persists in DTS/DTB data: register windows, GPIO provider cell counts, interrupt
wiring, pin groups, mux functions, drive strengths, pulls, and optional child pin configuration
nodes. Kernel drivers consume the validated DT data at boot or device probe and then program
hardware pin mux, pad, and GPIO state; this YAML only constrains that data before runtime.

## Dependencies and Integration Points
- Schema references: `pinmux-node.yaml#`, `pinctrl.yaml#`.
- Textual schema references: `/schemas/pinctrl/brcm,ns-pinmux.yaml#`.
Runtime integration is with Linux pinctrl and GPIO framework drivers selected by `compatible`. Board
`.dts` files instantiate nodes that satisfy this schema; `make dt_binding_check` validates the
binding and inline examples, while `make dtbs_check` validates real board descriptions against the
same contract.

## Risks
- A missing or misspelled `compatible` value prevents both schema matching and driver binding.
- Omitting required fields such as `reg`, `reg-names` should fail dt-schema validation before boot.
- Child node regexes and reusable pin configuration schemas are easy to misuse; incorrect group/function names can validate poorly or fail later in driver lookup tables.
- The closed property model catches typos, but any newly needed board property requires a binding update before DTS changes can pass validation.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/brcm,ns-pinmux.yaml` to parse this YAML, validate meta-schema rules, and compile its 1 inline example(s).
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/brcm,ns-pinmux.yaml` on affected board DTS files to confirm real nodes satisfy required properties, compatible choices, child node names, and referenced common schemas.
- Useful negative tests remove one required property, change `compatible`, and add an undeclared property where closure is enabled. Example seed: pinctrl@1800c1c0 {; compatible = "brcm,bcm4708-pinmux";; reg = <0x1800c1c0 0x24>;; reg-names = "cru_gpio_control";.
