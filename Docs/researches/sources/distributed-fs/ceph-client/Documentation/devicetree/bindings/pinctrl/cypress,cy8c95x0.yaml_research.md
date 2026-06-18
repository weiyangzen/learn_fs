# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/cypress,cy8c95x0.yaml

## Purpose
This file is a Linux Devicetree JSON-schema document for a pin controller binding: Cypress CY8C95X0
I2C GPIO expander. It lives in the pinctrl binding tree and gives dt-schema a machine-readable
contract for board DTS nodes before the kernel pinctrl/GPIO drivers consume those nodes during
probe.

This supports the 20/40/60 pin Cypress CYC95x0 GPIO I2C expanders. Pin function configuration is
performed on a per-pin basis.

The binding is maintained in-source by Patrick Rudolph <patrick.rudolph@9elements.com>.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/pinctrl/cypress,cy8c95x0.yaml#` with meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Compatible contract: `cypress,cy8c9520`, `cypress,cy8c9540`, `cypress,cy8c9560`.
- Required properties: `compatible`, `reg`, `interrupts`, `interrupt-controller`, `#interrupt-cells`, `gpio-controller`, `#gpio-cells`.
- Top-level framework properties: `compatible`, `reg`, `gpio-controller`, `#gpio-cells`, `interrupts`, `interrupt-controller`, `#interrupt-cells`, `gpio-line-names`, `gpio-ranges`, `gpio-reserved-ranges`.
- Vendor or device-specific extensions: none declared.
- Other declared top-level properties: `vdd-supply`, `reset-gpios`.
- Child-node or reusable schema API: patternProperties `-pins$`.
- Property detail signals: compatible (enum `cypress,cy8c9520`, `cypress,cy8c9540`, `cypress,cy8c9560`); reg (maxItems 1); gpio-controller; #gpio-cells (const `2`; The first cell is the GPIO number and the second cell specifies GPIO flags, as defined in <dt-bin...); interrupts (maxItems 1); interrupt-controller; #interrupt-cells (const `2`); gpio-line-names; gpio-ranges (maxItems 1); gpio-reserved-ranges (maxItems 60; minItems 1); vdd-supply (Optional power supply.); reset-gpios (maxItems 1; GPIO connected to the XRES pin).

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
- Schema references: `pincfg-node.yaml#`, `pinctrl.yaml#`.
- Example/header integration: `dt-bindings/interrupt-controller/arm-gic.h`, `dt-bindings/interrupt-controller/irq.h`.
- Textual schema references: `/schemas/pinctrl/cypress,cy8c95x0.yaml#`.
Runtime integration is with Linux pinctrl and GPIO framework drivers selected by `compatible`. Board
`.dts` files instantiate nodes that satisfy this schema; `make dt_binding_check` validates the
binding and inline examples, while `make dtbs_check` validates real board descriptions against the
same contract.

## Risks
- A missing or misspelled `compatible` value prevents both schema matching and driver binding.
- Omitting required fields such as `compatible`, `reg`, `interrupts`, `interrupt-controller`, `#interrupt-cells` should fail dt-schema validation before boot.
- Child node regexes and reusable pin configuration schemas are easy to misuse; incorrect group/function names can validate poorly or fail later in driver lookup tables.
- The closed property model catches typos, but any newly needed board property requires a binding update before DTS changes can pass validation.
- GPIO provider fields such as `#gpio-cells`, `gpio-ranges`, and interrupt controller wiring must match the runtime driver's expectations or GPIO consumers will resolve the wrong pins.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/cypress,cy8c95x0.yaml` to parse this YAML, validate meta-schema rules, and compile its 1 inline example(s).
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/cypress,cy8c95x0.yaml` on affected board DTS files to confirm real nodes satisfy required properties, compatible choices, child node names, and referenced common schemas.
- Useful negative tests remove one required property, change `compatible`, and add an undeclared property where closure is enabled. Example seed: #include <dt-bindings/interrupt-controller/arm-gic.h>; #include <dt-bindings/interrupt-controller/irq.h>; i2c {; #address-cells = <1>;.
