# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/atmel,at91rm9200-pinctrl.yaml

## Purpose
This file is a Linux Devicetree JSON-schema document for a pin multiplexing controller binding:
Microchip PIO3 Pinmux Controller. It lives in the pinctrl binding tree and gives dt-schema a
machine-readable contract for board DTS nodes before the kernel pinctrl/GPIO drivers consume those
nodes during probe.

The AT91 Pinmux Controller, enables the IC to share one PAD to several functional blocks. The
sharing is done by multiplexing the PAD input/output signals. For each PAD there are up to 8 muxing
options (called periph modes). Since different modules require different PAD settings (like pull up,
keeper, etc) the controller controls also the PAD settings parameters.

The binding is maintained in-source by Manikandan Muralidharan <manikandan.m@microchip.com>.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/pinctrl/atmel,at91rm9200-pinctrl.yaml#` with meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Compatible contract: `atmel,at91rm9200-pinctrl`, `atmel,at91sam9x5-pinctrl`, `atmel,sama5d3-pinctrl`, `microchip,sam9x60-pinctrl`, `simple-mfd`, `microchip,sam9x7-pinctrl`.
- Required properties: `compatible`, `ranges`, `#address-cells`, `#size-cells`, `atmel,mux-mask`.
- Top-level framework properties: `compatible`, `#address-cells`, `#size-cells`.
- Vendor or device-specific extensions: `atmel,mux-mask`.
- Other declared top-level properties: `ranges`.
- Child-node or reusable schema API: patternProperties `gpio@[0-9a-f]+$`.
- Property detail signals: compatible; #address-cells (const `1`); #size-cells (const `1`); ranges; atmel,mux-mask (Array of mask (periph per bank) to describe if a pin can be configured in this periph mode. All t...; ref `/schemas/types.yaml#/definitions/uint32-matrix`).

## Control Flow
There is no imperative execution path in this YAML. Validation starts when dt-schema selects this
document for a node whose `compatible` value matches the schema, checks the required list, evaluates
referenced common pinctrl/GPIO schemas, applies property constraints, then walks child-node patterns
and conditional branches.

This file contains 1 `allOf`, 1 `oneOf`, 0 `anyOf`, and 0 `if` blocks. Property closure: no explicit
top-level closure keyword is present in the parsed schema.

## State and Persistence Behavior
The binding stores no runtime state. It persists as source-controlled schema text, while the state
it describes persists in DTS/DTB data: register windows, GPIO provider cell counts, interrupt
wiring, pin groups, mux functions, drive strengths, pulls, and optional child pin configuration
nodes. Kernel drivers consume the validated DT data at boot or device probe and then program
hardware pin mux, pad, and GPIO state; this YAML only constrains that data before runtime.

## Dependencies and Integration Points
- Schema references: `/schemas/types.yaml#/definitions/uint32-matrix`, `pinctrl.yaml#`, `/schemas/gpio/atmel,at91rm9200-gpio.yaml`.
- Example/header integration: `dt-bindings/clock/at91.h`, `dt-bindings/interrupt-controller/irq.h`, `dt-bindings/pinctrl/at91.h`.
- Textual schema references: `/schemas/pinctrl/atmel,at91rm9200-pinctrl.yaml#`, `/schemas/types.yaml#/definitions/uint32-matrix`, `/schemas/gpio/atmel,at91rm9200-gpio.yaml`.
Runtime integration is with Linux pinctrl and GPIO framework drivers selected by `compatible`. Board
`.dts` files instantiate nodes that satisfy this schema; `make dt_binding_check` validates the
binding and inline examples, while `make dtbs_check` validates real board descriptions against the
same contract.

## Risks
- A missing or misspelled `compatible` value prevents both schema matching and driver binding.
- Omitting required fields such as `compatible`, `ranges`, `#address-cells`, `#size-cells`, `atmel,mux-mask` should fail dt-schema validation before boot.
- Child node regexes and reusable pin configuration schemas are easy to misuse; incorrect group/function names can validate poorly or fail later in driver lookup tables.
- Open or partially open property handling can let board-specific typos escape schema validation and surface only at driver probe time.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/atmel,at91rm9200-pinctrl.yaml` to parse this YAML, validate meta-schema rules, and compile its 1 inline example(s).
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/atmel,at91rm9200-pinctrl.yaml` on affected board DTS files to confirm real nodes satisfy required properties, compatible choices, child node names, and referenced common schemas.
- Useful negative tests remove one required property, change `compatible`, and add an undeclared property where closure is enabled. Example seed: #include <dt-bindings/clock/at91.h>; #include <dt-bindings/interrupt-controller/irq.h>; #include <dt-bindings/pinctrl/at91.h>; pinctrl@fffff400 {.
