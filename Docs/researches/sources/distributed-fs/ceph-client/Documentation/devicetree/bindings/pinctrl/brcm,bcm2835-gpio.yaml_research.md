# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/brcm,bcm2835-gpio.yaml

## Purpose
This file is a Linux Devicetree JSON-schema document for a pin multiplexing controller binding:
Broadcom BCM2835 GPIO (and pinmux) controller. It lives in the pinctrl binding tree and gives dt-
schema a machine-readable contract for board DTS nodes before the kernel pinctrl/GPIO drivers
consume those nodes during probe.

The BCM2835 GPIO module is a combined GPIO controller, (GPIO) interrupt controller, and
pinmux/control device.

The binding is maintained in-source by Florian Fainelli <f.fainelli@gmail.com>.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/pinctrl/brcm,bcm2835-gpio.yaml#` with meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Compatible contract: `brcm,bcm2835-gpio`, `brcm,bcm2711-gpio`, `brcm,bcm7211-gpio`.
- Required properties: none declared.
- Top-level framework properties: `compatible`, `reg`, `#gpio-cells`, `gpio-controller`, `gpio-ranges`, `gpio-line-names`, `interrupts`, `#interrupt-cells`, `interrupt-controller`.
- Vendor or device-specific extensions: none declared.
- Other declared top-level properties: none declared.
- Child-node or reusable schema API: no named child-node API or pattern child-node contract is declared.
- Property detail signals: compatible (enum `brcm,bcm2835-gpio`, `brcm,bcm2711-gpio`, `brcm,bcm7211-gpio`); reg (maxItems 1); #gpio-cells (const `2`); gpio-controller; gpio-ranges; gpio-line-names; interrupts (maxItems 10; minItems 4; Interrupt outputs: one per bank, then the combined “all banks” line. BCM7211 may specify up to fo...); #interrupt-cells (const `2`); interrupt-controller.

## Control Flow
There is no imperative execution path in this YAML. Validation starts when dt-schema selects this
document for a node whose `compatible` value matches the schema, checks the required list, evaluates
referenced common pinctrl/GPIO schemas, applies property constraints, then walks child-node patterns
and conditional branches.

This file contains 2 `allOf`, 1 `oneOf`, 0 `anyOf`, and 1 `if` blocks. Property closure: no explicit
top-level closure keyword is present in the parsed schema.

## State and Persistence Behavior
The binding stores no runtime state. It persists as source-controlled schema text, while the state
it describes persists in DTS/DTB data: register windows, GPIO provider cell counts, interrupt
wiring, pin groups, mux functions, drive strengths, pulls, and optional child pin configuration
nodes. Kernel drivers consume the validated DT data at boot or device probe and then program
hardware pin mux, pad, and GPIO state; this YAML only constrains that data before runtime.

## Dependencies and Integration Points
- Schema references: `/schemas/pinctrl/pincfg-node.yaml#`, `/schemas/pinctrl/pinmux-node.yaml#`, `/schemas/types.yaml#/definitions/uint32-array`.
- Textual schema references: `/schemas/pinctrl/brcm,bcm2835-gpio.yaml#`, `/schemas/pinctrl/pincfg-node.yaml#`, `/schemas/pinctrl/pinmux-node.yaml#`, `/schemas/types.yaml#/definitions/uint32-array`.
Runtime integration is with Linux pinctrl and GPIO framework drivers selected by `compatible`. Board
`.dts` files instantiate nodes that satisfy this schema; `make dt_binding_check` validates the
binding and inline examples, while `make dtbs_check` validates real board descriptions against the
same contract.

## Risks
- A missing or misspelled `compatible` value prevents both schema matching and driver binding.
- Open or partially open property handling can let board-specific typos escape schema validation and surface only at driver probe time.
- GPIO provider fields such as `#gpio-cells`, `gpio-ranges`, and interrupt controller wiring must match the runtime driver's expectations or GPIO consumers will resolve the wrong pins.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/brcm,bcm2835-gpio.yaml` to parse this YAML, validate meta-schema rules, and compile its 1 inline example(s).
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/brcm,bcm2835-gpio.yaml` on affected board DTS files to confirm real nodes satisfy required properties, compatible choices, child node names, and referenced common schemas.
- Useful negative tests remove one required property, change `compatible`, and add an undeclared property where closure is enabled. Example seed: gpio@2200000 {; compatible = "brcm,bcm2835-gpio";; reg = <0x2200000 0xb4>;; interrupts = <2 17>, <2 19>, <2 18>, <2 20>, <2 21>;; #gpio-cells = <2>;.
