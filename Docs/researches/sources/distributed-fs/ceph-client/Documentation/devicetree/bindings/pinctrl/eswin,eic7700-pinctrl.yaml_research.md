# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/eswin,eic7700-pinctrl.yaml

## Purpose
This file is a Linux Devicetree JSON-schema document for a pin controller binding: Eswin Eic7700
Pinctrl. It lives in the pinctrl binding tree and gives dt-schema a machine-readable contract for
board DTS nodes before the kernel pinctrl/GPIO drivers consume those nodes during probe.

eic7700 pin configuration nodes act as a container for an arbitrary number of subnodes. Each of
these subnodes represents some desired configuration for one or more pins. This configuration can
include the mux function to select on those pin(s), and various pin configuration parameters, such
as input-enable, pull-up, etc.

The binding is maintained in-source by Yulin Lu <luyulin@eswincomputing.com>.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/pinctrl/eswin,eic7700-pinctrl.yaml#` with meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Compatible contract: `eswin,eic7700-pinctrl`.
- Required properties: `compatible`, `reg`.
- Top-level framework properties: `compatible`, `reg`.
- Vendor or device-specific extensions: none declared.
- Other declared top-level properties: `vrgmii-supply`.
- Child-node or reusable schema API: patternProperties `-grp$`.
- Property detail signals: compatible (const `eswin,eic7700-pinctrl`); reg (maxItems 1); vrgmii-supply (Regulator supply for the RGMII interface IO power domain. This property should reference a regula...).

## Control Flow
There is no imperative execution path in this YAML. Validation starts when dt-schema selects this
document for a node whose `compatible` value matches the schema, checks the required list, evaluates
referenced common pinctrl/GPIO schemas, applies property constraints, then walks child-node patterns
and conditional branches.

This file contains 2 `allOf`, 0 `oneOf`, 1 `anyOf`, and 1 `if` blocks. Property closure: top-level
`unevaluatedProperties: false` closes properties after referenced schemas are evaluated.

## State and Persistence Behavior
The binding stores no runtime state. It persists as source-controlled schema text, while the state
it describes persists in DTS/DTB data: register windows, GPIO provider cell counts, interrupt
wiring, pin groups, mux functions, drive strengths, pulls, and optional child pin configuration
nodes. Kernel drivers consume the validated DT data at boot or device probe and then program
hardware pin mux, pad, and GPIO state; this YAML only constrains that data before runtime.

## Dependencies and Integration Points
- Schema references: `pinctrl.yaml#`, `pincfg-node.yaml#`, `pinmux-node.yaml#`.
- Textual schema references: `/schemas/pinctrl/eswin,eic7700-pinctrl.yaml#`.
Runtime integration is with Linux pinctrl and GPIO framework drivers selected by `compatible`. Board
`.dts` files instantiate nodes that satisfy this schema; `make dt_binding_check` validates the
binding and inline examples, while `make dtbs_check` validates real board descriptions against the
same contract.

## Risks
- A missing or misspelled `compatible` value prevents both schema matching and driver binding.
- Omitting required fields such as `compatible`, `reg` should fail dt-schema validation before boot.
- Child node regexes and reusable pin configuration schemas are easy to misuse; incorrect group/function names can validate poorly or fail later in driver lookup tables.
- The closed property model catches typos, but any newly needed board property requires a binding update before DTS changes can pass validation.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/eswin,eic7700-pinctrl.yaml` to parse this YAML, validate meta-schema rules, and compile its 1 inline example(s).
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/eswin,eic7700-pinctrl.yaml` on affected board DTS files to confirm real nodes satisfy required properties, compatible choices, child node names, and referenced common schemas.
- Useful negative tests remove one required property, change `compatible`, and add an undeclared property where closure is enabled. Example seed: pinctrl@51600080 {; compatible = "eswin,eic7700-pinctrl";; reg = <0x51600080 0x1fff80>;; vrgmii-supply = <&vcc_1v8>;.
