# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/cirrus,lochnagar.yaml

## Purpose
This file is a Linux Devicetree JSON-schema document for a pin controller binding: Cirrus Logic
Lochnagar Audio Development Board. It lives in the pinctrl binding tree and gives dt-schema a
machine-readable contract for board DTS nodes before the kernel pinctrl/GPIO drivers consume those
nodes during probe.

Lochnagar is an evaluation and development board for Cirrus Logic Smart CODEC and Amp devices. It
allows the connection of most Cirrus Logic devices on mini-cards, as well as allowing connection of
various application processor systems to provide a full evaluation platform. Audio system topology,
clocking and power can all be controlled through the Lochnagar, allowing the device under test to be
used in a variety of possible use cases. This binding document describes the binding for the pinctrl
portion of the driver. Also see these documents for generic binding information: [1] GPIO :
../gpio/gpio.txt [2] Pinctrl: ../pinctrl/pinctrl-bindings.txt And these for relevant defines: [3]
include/dt-bindings/pinctrl/lochnagar.h This binding must be part of the Lochnagar MFD binding: [4]
../mfd/cirrus,lochnagar.yaml

The binding is maintained in-source by patches@opensource.cirrus.com.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/pinctrl/cirrus,lochnagar.yaml#` with meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Compatible contract: `cirrus,lochnagar-pinctrl`.
- Required properties: `compatible`, `gpio-controller`, `#gpio-cells`, `gpio-ranges`, `pinctrl-0`, `pinctrl-names`.
- Top-level framework properties: `compatible`, `gpio-controller`, `#gpio-cells`, `gpio-ranges`.
- Vendor or device-specific extensions: none declared.
- Other declared top-level properties: `pin-settings`.
- Child-node or reusable schema API: object-valued child/property schemas `pin-settings`.
- Property detail signals: compatible (enum `cirrus,lochnagar-pinctrl`); gpio-controller; #gpio-cells (const `2`; The first cell is the pin number and the second cell is used to specify optional parameters.); gpio-ranges (maxItems 1; Range of pins managed by the GPIO controller, see [1]. Both the GPIO and Pinctrl base should be s...); pin-settings.

## Control Flow
There is no imperative execution path in this YAML. Validation starts when dt-schema selects this
document for a node whose `compatible` value matches the schema, checks the required list, evaluates
referenced common pinctrl/GPIO schemas, applies property constraints, then walks child-node patterns
and conditional branches.

This file contains 2 `allOf`, 0 `oneOf`, 0 `anyOf`, and 0 `if` blocks. Property closure: top-level
`additionalProperties: false` rejects undeclared properties.

## State and Persistence Behavior
The binding stores no runtime state. It persists as source-controlled schema text, while the state
it describes persists in DTS/DTB data: register windows, GPIO provider cell counts, interrupt
wiring, pin groups, mux functions, drive strengths, pulls, and optional child pin configuration
nodes. Kernel drivers consume the validated DT data at boot or device probe and then program
hardware pin mux, pad, and GPIO state; this YAML only constrains that data before runtime.

## Dependencies and Integration Points
- Schema references: `pincfg-node.yaml#`, `pinmux-node.yaml#`, `pinctrl.yaml#`.
- Textual schema references: `/schemas/pinctrl/cirrus,lochnagar.yaml#`.
Runtime integration is with Linux pinctrl and GPIO framework drivers selected by `compatible`. Board
`.dts` files instantiate nodes that satisfy this schema; `make dt_binding_check` validates the
binding and inline examples, while `make dtbs_check` validates real board descriptions against the
same contract.

## Risks
- A missing or misspelled `compatible` value prevents both schema matching and driver binding.
- Omitting required fields such as `compatible`, `gpio-controller`, `#gpio-cells`, `gpio-ranges`, `pinctrl-0` should fail dt-schema validation before boot.
- Child node regexes and reusable pin configuration schemas are easy to misuse; incorrect group/function names can validate poorly or fail later in driver lookup tables.
- The closed property model catches typos, but any newly needed board property requires a binding update before DTS changes can pass validation.
- GPIO provider fields such as `#gpio-cells`, `gpio-ranges`, and interrupt controller wiring must match the runtime driver's expectations or GPIO consumers will resolve the wrong pins.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/cirrus,lochnagar.yaml` to parse this YAML, validate meta-schema rules, and compile its 0 inline example(s).
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/cirrus,lochnagar.yaml` on affected board DTS files to confirm real nodes satisfy required properties, compatible choices, child node names, and referenced common schemas.
- Useful negative tests remove one required property, change `compatible`, add a bogus pin group/function, and add an undeclared property where closure is enabled.
