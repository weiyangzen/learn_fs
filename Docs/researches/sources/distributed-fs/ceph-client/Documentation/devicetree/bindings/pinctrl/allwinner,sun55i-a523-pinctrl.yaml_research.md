# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/allwinner,sun55i-a523-pinctrl.yaml

## Purpose
This file is a Linux Devicetree JSON-schema document for a pin controller binding: Allwinner A523
Pin Controller. It lives in the pinctrl binding tree and gives dt-schema a machine-readable contract
for board DTS nodes before the kernel pinctrl/GPIO drivers consume those nodes during probe.

The schema relies on title, compatible values, and property constraints rather than a long description block.

The binding is maintained in-source by Andre Przywara <andre.przywara@arm.com>.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/pinctrl/allwinner,sun55i-a523-pinctrl.yaml#` with meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Compatible contract: `allwinner,sun55i-a523-pinctrl`, `allwinner,sun55i-a523-r-pinctrl`.
- Required properties: `#gpio-cells`, `compatible`, `reg`, `clocks`, `clock-names`, `gpio-controller`, `#interrupt-cells`, `interrupts`, `interrupt-controller`.
- Top-level framework properties: `#gpio-cells`, `#interrupt-cells`, `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `gpio-controller`, `interrupt-controller`, `gpio-line-names`.
- Vendor or device-specific extensions: none declared.
- Other declared top-level properties: `input-debounce`.
- Child-node or reusable schema API: patternProperties `^([rs]-)?(([a-z0-9]{3,}|[a-oq-z][a-z0-9]*?)?-)+?(p[a-m][0-9]*?-)??pins?$`, `^vcc-p[a-m]-supply$`.
- Property detail signals: #gpio-cells (const `3`; GPIO consumers must use three arguments, first the number of the bank, then the pin number inside...); #interrupt-cells (const `3`; Interrupts consumers must use three arguments, first the number of the bank, then the pin number...); compatible (enum `allwinner,sun55i-a523-pinctrl`, `allwinner,sun55i-a523-r-pinctrl`); reg (maxItems 1); interrupts (maxItems 10; minItems 2; One interrupt per external interrupt bank supported on the controller, sorted by bank number asce...); clocks; clock-names; gpio-controller; interrupt-controller; gpio-line-names; input-debounce (maxItems 10; minItems 2; Debouncing periods in microseconds, one period per interrupt bank found in the controller; ref `/schemas/types.yaml#/definitions/uint32-array`).

## Control Flow
There is no imperative execution path in this YAML. Validation starts when dt-schema selects this
document for a node whose `compatible` value matches the schema, checks the required list, evaluates
referenced common pinctrl/GPIO schemas, applies property constraints, then walks child-node patterns
and conditional branches.

This file contains 1 `allOf`, 0 `oneOf`, 0 `anyOf`, and 2 `if` blocks. Property closure: top-level
`additionalProperties: false` rejects undeclared properties.

## State and Persistence Behavior
The binding stores no runtime state. It persists as source-controlled schema text, while the state
it describes persists in DTS/DTB data: register windows, GPIO provider cell counts, interrupt
wiring, pin groups, mux functions, drive strengths, pulls, and optional child pin configuration
nodes. Kernel drivers consume the validated DT data at boot or device probe and then program
hardware pin mux, pad, and GPIO state; this YAML only constrains that data before runtime.

## Dependencies and Integration Points
- Schema references: `/schemas/types.yaml#/definitions/uint32-array`, `/schemas/types.yaml#/definitions/uint32`, `pinctrl.yaml#`.
- Textual schema references: `/schemas/pinctrl/allwinner,sun55i-a523-pinctrl.yaml#`, `/schemas/types.yaml#/definitions/uint32-array`, `/schemas/types.yaml#/definitions/uint32`.
Runtime integration is with Linux pinctrl and GPIO framework drivers selected by `compatible`. Board
`.dts` files instantiate nodes that satisfy this schema; `make dt_binding_check` validates the
binding and inline examples, while `make dtbs_check` validates real board descriptions against the
same contract.

## Risks
- A missing or misspelled `compatible` value prevents both schema matching and driver binding.
- Omitting required fields such as `#gpio-cells`, `compatible`, `reg`, `clocks`, `clock-names` should fail dt-schema validation before boot.
- Child node regexes and reusable pin configuration schemas are easy to misuse; incorrect group/function names can validate poorly or fail later in driver lookup tables.
- The closed property model catches typos, but any newly needed board property requires a binding update before DTS changes can pass validation.
- GPIO provider fields such as `#gpio-cells`, `gpio-ranges`, and interrupt controller wiring must match the runtime driver's expectations or GPIO consumers will resolve the wrong pins.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/allwinner,sun55i-a523-pinctrl.yaml` to parse this YAML, validate meta-schema rules, and compile its 1 inline example(s).
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/allwinner,sun55i-a523-pinctrl.yaml` on affected board DTS files to confirm real nodes satisfy required properties, compatible choices, child node names, and referenced common schemas.
- Useful negative tests remove one required property, change `compatible`, and add an undeclared property where closure is enabled. Example seed: r_pio: pinctrl@7022000 {; compatible = "allwinner,sun55i-a523-r-pinctrl";; reg = <0x7022000 0x800>;; interrupts = <0 159 4>, <0 161 4>;; clocks = <&r_ccu 1>, <&osc24M>, <&osc32k>;.
