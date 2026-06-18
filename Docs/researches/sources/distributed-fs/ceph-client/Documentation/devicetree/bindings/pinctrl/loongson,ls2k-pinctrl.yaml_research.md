# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/loongson,ls2k-pinctrl.yaml

## Purpose
This file is a Linux Devicetree JSON-schema document for a pin controller binding: Loongson-2 SoC
Pinctrl Controller. It lives in the pinctrl binding tree and gives dt-schema a machine-readable
contract for board DTS nodes before the kernel pinctrl/GPIO drivers consume those nodes during
probe.

The schema relies on title, compatible values, and property constraints rather than a long description block.

The binding is maintained in-source by zhanghongchen <zhanghongchen@loongson.cn>, Yinbo Zhu
<zhuyinbo@loongson.cn>.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/pinctrl/loongson,ls2k-pinctrl.yaml#` with meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Compatible contract: `loongson,ls2k-pinctrl`.
- Required properties: `compatible`, `reg`.
- Top-level framework properties: `compatible`, `reg`.
- Vendor or device-specific extensions: none declared.
- Other declared top-level properties: none declared.
- Child-node or reusable schema API: patternProperties `-pins$`.
- Property detail signals: compatible (const `loongson,ls2k-pinctrl`); reg (maxItems 1).

## Control Flow
There is no imperative execution path in this YAML. Validation starts when dt-schema selects this
document for a node whose `compatible` value matches the schema, checks the required list, evaluates
referenced common pinctrl/GPIO schemas, applies property constraints, then walks child-node patterns
and conditional branches.

This file contains 1 `allOf`, 0 `oneOf`, 0 `anyOf`, and 0 `if` blocks. Property closure: top-level
`additionalProperties: false` rejects undeclared properties.

## State and Persistence Behavior
The binding stores no runtime state. It persists as source-controlled schema text, while the state
it describes persists in DTS/DTB data: register windows, GPIO provider cell counts, interrupt
wiring, pin groups, mux functions, drive strengths, pulls, and optional child pin configuration
nodes. Kernel drivers consume the validated DT data at boot or device probe and then program
hardware pin mux, pad, and GPIO state; this YAML only constrains that data before runtime.

## Dependencies and Integration Points
- Schema references: `pinctrl.yaml#`, `pinmux-node.yaml#`.
- Textual schema references: `/schemas/pinctrl/loongson,ls2k-pinctrl.yaml#`.
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
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/loongson,ls2k-pinctrl.yaml` to parse this YAML, validate meta-schema rules, and compile its 1 inline example(s).
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/loongson,ls2k-pinctrl.yaml` on affected board DTS files to confirm real nodes satisfy required properties, compatible choices, child node names, and referenced common schemas.
- Useful negative tests remove one required property, change `compatible`, and add an undeclared property where closure is enabled. Example seed: pctrl: pinctrl@1fe00420 {; compatible = "loongson,ls2k-pinctrl";; reg = <0x1fe00420 0x18>;; sdio_pins_default: sdio-pins {; sdio-pinmux {.
