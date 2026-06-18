# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/ingenic,pinctrl.yaml

## Purpose
This file is a Linux Devicetree JSON-schema document for a pin controller binding: Ingenic SoCs pin
controller. It lives in the pinctrl binding tree and gives dt-schema a machine-readable contract for
board DTS nodes before the kernel pinctrl/GPIO drivers consume those nodes during probe.

Please refer to pinctrl-bindings.txt in this directory for details of the common pinctrl bindings
used by client devices, including the meaning of the phrase "pin configuration node". For the
Ingenic SoCs, pin control is tightly bound with GPIO ports. All pins may be used as GPIOs,
multiplexed device functions are configured within the GPIO port configuration registers and it is
typical to refer to pins using the naming scheme "PxN" where x is a character identifying the GPIO
port with which the pin is associated and N is an integer from 0 to 31 identifying the pin within
that GPIO port. For example PA0 is the first pin in GPIO port A, and PB31 is the last pin in GPIO
port B. The JZ4730, the JZ4740, the JZ4725B, the X1000 and the X1830 contains 4 GPIO ports, PA to
PD, for a total of 128 pins. The X2000 and the X2100 contains 5 GPIO ports, PA to PE, for a total of
160 pins. The JZ4750, the JZ4755 the JZ4760, the JZ4770 and the JZ4780 contains 6 GPIO ports, PA to
PF, for a total of 192 pins. The JZ4775 contains 7 GPIO ports, PA to PG, for a total of 224 pins.

The binding is maintained in-source by Paul Cercueil <paul@crapouillou.net>.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/pinctrl/ingenic,pinctrl.yaml#` with meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Compatible contract: `ingenic,jz4730-pinctrl`, `ingenic,jz4740-pinctrl`, `ingenic,jz4725b-pinctrl`, `ingenic,jz4750-pinctrl`, `ingenic,jz4755-pinctrl`, `ingenic,jz4760-pinctrl`, `ingenic,jz4770-pinctrl`, `ingenic,jz4775-pinctrl`, `ingenic,jz4780-pinctrl`, `ingenic,x1000-pinctrl`, `ingenic,x1500-pinctrl`, `ingenic,x1600-pinctrl`, ... (33 total).
- Required properties: `compatible`, `reg`, `#address-cells`, `#size-cells`.
- Top-level framework properties: `compatible`, `reg`, `#address-cells`, `#size-cells`.
- Vendor or device-specific extensions: none declared.
- Other declared top-level properties: none declared.
- Child-node or reusable schema API: patternProperties `^gpio@[0-9]$`.
- Property detail signals: compatible; reg (maxItems 1); #address-cells (const `1`); #size-cells (const `0`).

## Control Flow
There is no imperative execution path in this YAML. Validation starts when dt-schema selects this
document for a node whose `compatible` value matches the schema, checks the required list, evaluates
referenced common pinctrl/GPIO schemas, applies property constraints, then walks child-node patterns
and conditional branches.

This file contains 3 `allOf`, 1 `oneOf`, 1 `anyOf`, and 0 `if` blocks. Property closure: no explicit
top-level closure keyword is present in the parsed schema.

## State and Persistence Behavior
The binding stores no runtime state. It persists as source-controlled schema text, while the state
it describes persists in DTS/DTB data: register windows, GPIO provider cell counts, interrupt
wiring, pin groups, mux functions, drive strengths, pulls, and optional child pin configuration
nodes. Kernel drivers consume the validated DT data at boot or device probe and then program
hardware pin mux, pad, and GPIO state; this YAML only constrains that data before runtime.

## Dependencies and Integration Points
- Schema references: `pinctrl.yaml#`, `pincfg-node.yaml#`, `pinmux-node.yaml#`.
- Textual schema references: `/schemas/pinctrl/ingenic,pinctrl.yaml#`.
Runtime integration is with Linux pinctrl and GPIO framework drivers selected by `compatible`. Board
`.dts` files instantiate nodes that satisfy this schema; `make dt_binding_check` validates the
binding and inline examples, while `make dtbs_check` validates real board descriptions against the
same contract.

## Risks
- A missing or misspelled `compatible` value prevents both schema matching and driver binding.
- Omitting required fields such as `compatible`, `reg`, `#address-cells`, `#size-cells` should fail dt-schema validation before boot.
- Child node regexes and reusable pin configuration schemas are easy to misuse; incorrect group/function names can validate poorly or fail later in driver lookup tables.
- Open or partially open property handling can let board-specific typos escape schema validation and surface only at driver probe time.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/ingenic,pinctrl.yaml` to parse this YAML, validate meta-schema rules, and compile its 1 inline example(s).
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/ingenic,pinctrl.yaml` on affected board DTS files to confirm real nodes satisfy required properties, compatible choices, child node names, and referenced common schemas.
- Useful negative tests remove one required property, change `compatible`, and add an undeclared property where closure is enabled. Example seed: pinctrl@10010000 {; compatible = "ingenic,jz4770-pinctrl";; reg = <0x10010000 0x600>;; #address-cells = <1>;.
