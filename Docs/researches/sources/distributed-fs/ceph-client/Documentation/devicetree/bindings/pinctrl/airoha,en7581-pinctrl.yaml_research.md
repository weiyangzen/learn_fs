# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/airoha,en7581-pinctrl.yaml

## Purpose
This file is a Linux Devicetree JSON-schema document for a pin controller binding: Airoha EN7581 Pin
Controller. It lives in the pinctrl binding tree and gives dt-schema a machine-readable contract for
board DTS nodes before the kernel pinctrl/GPIO drivers consume those nodes during probe.

The Airoha's EN7581 Pin controller is used to control SoC pins.

The binding is maintained in-source by Lorenzo Bianconi <lorenzo@kernel.org>.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/pinctrl/airoha,en7581-pinctrl.yaml#` with meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Compatible contract: `airoha,en7581-pinctrl`.
- Required properties: `compatible`, `interrupts`, `gpio-controller`, `#gpio-cells`, `interrupt-controller`, `#interrupt-cells`.
- Top-level framework properties: `compatible`, `interrupts`, `gpio-controller`, `#gpio-cells`, `gpio-ranges`, `interrupt-controller`, `#interrupt-cells`.
- Vendor or device-specific extensions: none declared.
- Other declared top-level properties: none declared.
- Child-node or reusable schema API: patternProperties `-pins$`.
- Property detail signals: compatible (const `airoha,en7581-pinctrl`); interrupts (maxItems 1); gpio-controller; #gpio-cells (const `2`); gpio-ranges (maxItems 1); interrupt-controller; #interrupt-cells (const `2`).

## Control Flow
There is no imperative execution path in this YAML. Validation starts when dt-schema selects this
document for a node whose `compatible` value matches the schema, checks the required list, evaluates
referenced common pinctrl/GPIO schemas, applies property constraints, then walks child-node patterns
and conditional branches.

This file contains 2 `allOf`, 0 `oneOf`, 0 `anyOf`, and 23 `if` blocks. Property closure: top-level
`additionalProperties: false` rejects undeclared properties.

## State and Persistence Behavior
The binding stores no runtime state. It persists as source-controlled schema text, while the state
it describes persists in DTS/DTB data: register windows, GPIO provider cell counts, interrupt
wiring, pin groups, mux functions, drive strengths, pulls, and optional child pin configuration
nodes. Kernel drivers consume the validated DT data at boot or device probe and then program
hardware pin mux, pad, and GPIO state; this YAML only constrains that data before runtime.

## Dependencies and Integration Points
- Schema references: `pinctrl.yaml#`, `/schemas/pinctrl/pinmux-node.yaml`, `/schemas/pinctrl/pincfg-node.yaml`.
- Example/header integration: `dt-bindings/interrupt-controller/arm-gic.h`.
- Textual schema references: `/schemas/pinctrl/airoha,en7581-pinctrl.yaml#`, `/schemas/pinctrl/pinmux-node.yaml`, `/schemas/pinctrl/pincfg-node.yaml`.
Runtime integration is with Linux pinctrl and GPIO framework drivers selected by `compatible`. Board
`.dts` files instantiate nodes that satisfy this schema; `make dt_binding_check` validates the
binding and inline examples, while `make dtbs_check` validates real board descriptions against the
same contract.

## Risks
- A missing or misspelled `compatible` value prevents both schema matching and driver binding.
- Omitting required fields such as `compatible`, `interrupts`, `gpio-controller`, `#gpio-cells`, `interrupt-controller` should fail dt-schema validation before boot.
- Child node regexes and reusable pin configuration schemas are easy to misuse; incorrect group/function names can validate poorly or fail later in driver lookup tables.
- The closed property model catches typos, but any newly needed board property requires a binding update before DTS changes can pass validation.
- GPIO provider fields such as `#gpio-cells`, `gpio-ranges`, and interrupt controller wiring must match the runtime driver's expectations or GPIO consumers will resolve the wrong pins.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/airoha,en7581-pinctrl.yaml` to parse this YAML, validate meta-schema rules, and compile its 1 inline example(s).
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/airoha,en7581-pinctrl.yaml` on affected board DTS files to confirm real nodes satisfy required properties, compatible choices, child node names, and referenced common schemas.
- Useful negative tests remove one required property, change `compatible`, and add an undeclared property where closure is enabled. Example seed: #include <dt-bindings/interrupt-controller/arm-gic.h>; pinctrl {; compatible = "airoha,en7581-pinctrl";.
