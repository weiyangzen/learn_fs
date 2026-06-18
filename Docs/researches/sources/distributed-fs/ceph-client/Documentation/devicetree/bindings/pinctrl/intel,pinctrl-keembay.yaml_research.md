# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/intel,pinctrl-keembay.yaml

## Purpose
This file is a Linux Devicetree JSON-schema document for a pin controller binding: Intel Keem Bay
pin controller. It lives in the pinctrl binding tree and gives dt-schema a machine-readable contract
for board DTS nodes before the kernel pinctrl/GPIO drivers consume those nodes during probe.

Intel Keem Bay SoC integrates a pin controller which enables control of pin directions, input/output
values and configuration for a total of 80 pins.

The binding is maintained in-source by Lakshmi Sowjanya D <lakshmi.sowjanya.d@intel.com>.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/pinctrl/intel,pinctrl-keembay.yaml#` with meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Compatible contract: `intel,keembay-pinctrl`.
- Required properties: `compatible`, `reg`, `gpio-controller`, `ngpios`, `#gpio-cells`, `interrupts`, `interrupt-controller`, `#interrupt-cells`.
- Top-level framework properties: `compatible`, `reg`, `gpio-controller`, `#gpio-cells`, `interrupts`, `interrupt-controller`, `#interrupt-cells`.
- Vendor or device-specific extensions: none declared.
- Other declared top-level properties: `ngpios`.
- Child-node or reusable schema API: patternProperties `^gpio@[0-9a-f]*$`.
- Property detail signals: compatible (const `intel,keembay-pinctrl`); reg (maxItems 2); gpio-controller; #gpio-cells (const `2`); ngpios (const `80`; The number of GPIOs exposed.); interrupts (maxItems 8; Specifies the interrupt lines to be used by the controller. Each interrupt line is shared by up t...); interrupt-controller; #interrupt-cells (const `2`).

## Control Flow
There is no imperative execution path in this YAML. Validation starts when dt-schema selects this
document for a node whose `compatible` value matches the schema, checks the required list, evaluates
referenced common pinctrl/GPIO schemas, applies property constraints, then walks child-node patterns
and conditional branches.

This file contains 0 `allOf`, 0 `oneOf`, 0 `anyOf`, and 0 `if` blocks. Property closure: top-level
`additionalProperties: false` rejects undeclared properties.

## State and Persistence Behavior
The binding stores no runtime state. It persists as source-controlled schema text, while the state
it describes persists in DTS/DTB data: register windows, GPIO provider cell counts, interrupt
wiring, pin groups, mux functions, drive strengths, pulls, and optional child pin configuration
nodes. Kernel drivers consume the validated DT data at boot or device probe and then program
hardware pin mux, pad, and GPIO state; this YAML only constrains that data before runtime.

## Dependencies and Integration Points
- Schema references: none declared.
- Example/header integration: `dt-bindings/interrupt-controller/arm-gic.h`, `dt-bindings/interrupt-controller/irq.h`.
- Textual schema references: `/schemas/pinctrl/intel,pinctrl-keembay.yaml#`.
Runtime integration is with Linux pinctrl and GPIO framework drivers selected by `compatible`. Board
`.dts` files instantiate nodes that satisfy this schema; `make dt_binding_check` validates the
binding and inline examples, while `make dtbs_check` validates real board descriptions against the
same contract.

## Risks
- A missing or misspelled `compatible` value prevents both schema matching and driver binding.
- Omitting required fields such as `compatible`, `reg`, `gpio-controller`, `ngpios`, `#gpio-cells` should fail dt-schema validation before boot.
- Child node regexes and reusable pin configuration schemas are easy to misuse; incorrect group/function names can validate poorly or fail later in driver lookup tables.
- The closed property model catches typos, but any newly needed board property requires a binding update before DTS changes can pass validation.
- GPIO provider fields such as `#gpio-cells`, `gpio-ranges`, and interrupt controller wiring must match the runtime driver's expectations or GPIO consumers will resolve the wrong pins.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/intel,pinctrl-keembay.yaml` to parse this YAML, validate meta-schema rules, and compile its 1 inline example(s).
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/intel,pinctrl-keembay.yaml` on affected board DTS files to confirm real nodes satisfy required properties, compatible choices, child node names, and referenced common schemas.
- Useful negative tests remove one required property, change `compatible`, and add an undeclared property where closure is enabled. Example seed: #include <dt-bindings/interrupt-controller/arm-gic.h>; #include <dt-bindings/interrupt-controller/irq.h>; // Example 1; gpio@0 {; compatible = "intel,keembay-pinctrl";.
