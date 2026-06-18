# subset-b-000601 Research

Grouped source research for the subset B work item. Each section is delimited for deterministic reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/airoha,en7581-pinctrl.yaml -->
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

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/airoha,en7581-pinctrl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/allwinner,sun4i-a10-pinctrl.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/allwinner,sun4i-a10-pinctrl.yaml

## Purpose
This file is a Linux Devicetree JSON-schema document for a pin controller binding: Allwinner A10 Pin
Controller. It lives in the pinctrl binding tree and gives dt-schema a machine-readable contract for
board DTS nodes before the kernel pinctrl/GPIO drivers consume those nodes during probe.

The schema relies on title, compatible values, and property constraints rather than a long description block.

The binding is maintained in-source by Chen-Yu Tsai <wens@csie.org>, Maxime Ripard
<mripard@kernel.org>.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/pinctrl/allwinner,sun4i-a10-pinctrl.yaml#` with meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Compatible contract: `allwinner,sun4i-a10-pinctrl`, `allwinner,sun5i-a10s-pinctrl`, `allwinner,sun5i-a13-pinctrl`, `allwinner,sun6i-a31-pinctrl`, `allwinner,sun6i-a31-r-pinctrl`, `allwinner,sun6i-a31s-pinctrl`, `allwinner,sun7i-a20-pinctrl`, `allwinner,sun8i-a23-pinctrl`, `allwinner,sun8i-a23-r-pinctrl`, `allwinner,sun8i-a33-pinctrl`, `allwinner,sun8i-a83t-pinctrl`, `allwinner,sun8i-a83t-r-pinctrl`, ... (32 total).
- Required properties: `#gpio-cells`, `compatible`, `reg`, `clocks`, `clock-names`, `gpio-controller`.
- Top-level framework properties: `#gpio-cells`, `#interrupt-cells`, `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `gpio-controller`, `interrupt-controller`, `gpio-line-names`.
- Vendor or device-specific extensions: none declared.
- Other declared top-level properties: `input-debounce`.
- Child-node or reusable schema API: patternProperties `^([rs]-)?(([a-z0-9]{3,}|[a-oq-z0-9][a-z0-9]*?)?-)+?(p[a-ilm][0-9]*?-)??pins?$`, `^vcc-p[a-ilm]-supply$`.
- Property detail signals: #gpio-cells (const `3`; GPIO consumers must use three arguments, first the number of the bank, then the pin number inside...); #interrupt-cells (const `3`; Interrupts consumers must use three arguments, first the number of the bank, then the pin number...); compatible (enum `allwinner,sun4i-a10-pinctrl`, `allwinner,sun5i-a10s-pinctrl`, `allwinner,sun5i-a13-pinctrl`, `allwinner,sun6i-a31-pinctrl`, `allwinner,sun6i-a31-r-pinctrl`, `allwinner,sun6i-a31s-pinctrl`, `allwinner,sun7i-a20-pinctrl`, `allwinner,sun8i-a23-pinctrl`, ... (32 total)); reg (maxItems 1); interrupts (maxItems 8; minItems 1; One interrupt per external interrupt bank supported on the controller, sorted by bank number asce...); clocks; clock-names; gpio-controller; interrupt-controller; gpio-line-names; input-debounce (maxItems 8; minItems 1; Debouncing periods in microseconds, one period per interrupt bank found in the controller; ref `/schemas/types.yaml#/definitions/uint32-array`).

## Control Flow
There is no imperative execution path in this YAML. Validation starts when dt-schema selects this
document for a node whose `compatible` value matches the schema, checks the required list, evaluates
referenced common pinctrl/GPIO schemas, applies property constraints, then walks child-node patterns
and conditional branches.

This file contains 1 `allOf`, 0 `oneOf`, 0 `anyOf`, and 10 `if` blocks. Property closure: top-level
`additionalProperties: false` rejects undeclared properties.

## State and Persistence Behavior
The binding stores no runtime state. It persists as source-controlled schema text, while the state
it describes persists in DTS/DTB data: register windows, GPIO provider cell counts, interrupt
wiring, pin groups, mux functions, drive strengths, pulls, and optional child pin configuration
nodes. Kernel drivers consume the validated DT data at boot or device probe and then program
hardware pin mux, pad, and GPIO state; this YAML only constrains that data before runtime.

## Dependencies and Integration Points
- Schema references: `/schemas/types.yaml#/definitions/uint32-array`, `/schemas/types.yaml#/definitions/uint32`, `pinctrl.yaml#`.
- Example/header integration: `dt-bindings/clock/sun5i-ccu.h`.
- Textual schema references: `/schemas/pinctrl/allwinner,sun4i-a10-pinctrl.yaml#`, `/schemas/types.yaml#/definitions/uint32-array`, `/schemas/types.yaml#/definitions/uint32`.
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
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/allwinner,sun4i-a10-pinctrl.yaml` to parse this YAML, validate meta-schema rules, and compile its 1 inline example(s).
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/allwinner,sun4i-a10-pinctrl.yaml` on affected board DTS files to confirm real nodes satisfy required properties, compatible choices, child node names, and referenced common schemas.
- Useful negative tests remove one required property, change `compatible`, and add an undeclared property where closure is enabled. Example seed: #include <dt-bindings/clock/sun5i-ccu.h>; pio: pinctrl@1c20800 {; compatible = "allwinner,sun5i-a13-pinctrl";; reg = <0x01c20800 0x400>;.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/allwinner,sun4i-a10-pinctrl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/allwinner,sun55i-a523-pinctrl.yaml -->
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

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/allwinner,sun55i-a523-pinctrl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/amlogic,meson-pinctrl-a1.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/amlogic,meson-pinctrl-a1.yaml

## Purpose
This file is a Linux Devicetree JSON-schema document for a pin multiplexing controller binding:
Amlogic Meson A1 pinmux controller. It lives in the pinctrl binding tree and gives dt-schema a
machine-readable contract for board DTS nodes before the kernel pinctrl/GPIO drivers consume those
nodes during probe.

The schema relies on title, compatible values, and property constraints rather than a long description block.

The binding is maintained in-source by Neil Armstrong <neil.armstrong@linaro.org>.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/pinctrl/amlogic,meson-pinctrl-a1.yaml#` with meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Compatible contract: `amlogic,c3-periphs-pinctrl`, `amlogic,t7-periphs-pinctrl`, `amlogic,meson-a1-periphs-pinctrl`, `amlogic,meson-s4-periphs-pinctrl`.
- Required properties: `compatible`.
- Top-level framework properties: `compatible`.
- Vendor or device-specific extensions: none declared.
- Other declared top-level properties: none declared.
- Child-node or reusable schema API: patternProperties `^bank@[0-9a-f]+$`.
- Property detail signals: compatible (enum `amlogic,c3-periphs-pinctrl`, `amlogic,t7-periphs-pinctrl`, `amlogic,meson-a1-periphs-pinctrl`, `amlogic,meson-s4-periphs-pinctrl`).

## Control Flow
There is no imperative execution path in this YAML. Validation starts when dt-schema selects this
document for a node whose `compatible` value matches the schema, checks the required list, evaluates
referenced common pinctrl/GPIO schemas, applies property constraints, then walks child-node patterns
and conditional branches.

This file contains 1 `allOf`, 0 `oneOf`, 0 `anyOf`, and 0 `if` blocks. Property closure: no explicit
top-level closure keyword is present in the parsed schema.

## State and Persistence Behavior
The binding stores no runtime state. It persists as source-controlled schema text, while the state
it describes persists in DTS/DTB data: register windows, GPIO provider cell counts, interrupt
wiring, pin groups, mux functions, drive strengths, pulls, and optional child pin configuration
nodes. Kernel drivers consume the validated DT data at boot or device probe and then program
hardware pin mux, pad, and GPIO state; this YAML only constrains that data before runtime.

## Dependencies and Integration Points
- Schema references: `amlogic,meson-pinctrl-common.yaml#`, `amlogic,meson-pinctrl-common.yaml#/$defs/meson-gpio`, `amlogic,meson-pinctrl-common.yaml#/$defs/meson-pins`.
- Textual schema references: `/schemas/pinctrl/amlogic,meson-pinctrl-a1.yaml#`.
Runtime integration is with Linux pinctrl and GPIO framework drivers selected by `compatible`. Board
`.dts` files instantiate nodes that satisfy this schema; `make dt_binding_check` validates the
binding and inline examples, while `make dtbs_check` validates real board descriptions against the
same contract.

## Risks
- A missing or misspelled `compatible` value prevents both schema matching and driver binding.
- Omitting required fields such as `compatible` should fail dt-schema validation before boot.
- Child node regexes and reusable pin configuration schemas are easy to misuse; incorrect group/function names can validate poorly or fail later in driver lookup tables.
- Open or partially open property handling can let board-specific typos escape schema validation and surface only at driver probe time.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/amlogic,meson-pinctrl-a1.yaml` to parse this YAML, validate meta-schema rules, and compile its 1 inline example(s).
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/amlogic,meson-pinctrl-a1.yaml` on affected board DTS files to confirm real nodes satisfy required properties, compatible choices, child node names, and referenced common schemas.
- Useful negative tests remove one required property, change `compatible`, and add an undeclared property where closure is enabled. Example seed: periphs_pinctrl: pinctrl {; compatible = "amlogic,meson-a1-periphs-pinctrl";; #address-cells = <1>;; #size-cells = <1>;; ranges;.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/amlogic,meson-pinctrl-a1.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/amlogic,meson-pinctrl-common.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/amlogic,meson-pinctrl-common.yaml

## Purpose
This file is a Linux Devicetree JSON-schema document for a pin multiplexing controller binding:
Amlogic Meson pinmux controller. It lives in the pinctrl binding tree and gives dt-schema a machine-
readable contract for board DTS nodes before the kernel pinctrl/GPIO drivers consume those nodes
during probe.

The schema relies on title, compatible values, and property constraints rather than a long description block.

The binding is maintained in-source by Neil Armstrong <neil.armstrong@linaro.org>.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/pinctrl/amlogic,meson-pinctrl-common.yaml#` with meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Compatible contract: none declared.
- Required properties: `ranges`, `#address-cells`, `#size-cells`.
- Top-level framework properties: `#address-cells`, `#size-cells`.
- Vendor or device-specific extensions: none declared.
- Other declared top-level properties: `ranges`.
- Child-node or reusable schema API: local definitions `meson-gpio`, `meson-pins`.
- Property detail signals: ranges; #address-cells (enum `1`, `2`); #size-cells (enum `1`, `2`).

## Control Flow
There is no imperative execution path in this YAML. Validation starts when dt-schema selects this
document for a node whose `compatible` value matches the schema, checks the required list, evaluates
referenced common pinctrl/GPIO schemas, applies property constraints, then walks child-node patterns
and conditional branches.

This file contains 2 `allOf`, 0 `oneOf`, 0 `anyOf`, and 0 `if` blocks. Property closure: top-level
`additionalProperties: true` allows extensions beyond declared keys.

## State and Persistence Behavior
The binding stores no runtime state. It persists as source-controlled schema text, while the state
it describes persists in DTS/DTB data: register windows, GPIO provider cell counts, interrupt
wiring, pin groups, mux functions, drive strengths, pulls, and optional child pin configuration
nodes. Kernel drivers consume the validated DT data at boot or device probe and then program
hardware pin mux, pad, and GPIO state; this YAML only constrains that data before runtime.

## Dependencies and Integration Points
- Schema references: `pinctrl.yaml#`, `pincfg-node.yaml#`, `pinmux-node.yaml#`.
- Textual schema references: `/schemas/pinctrl/amlogic,meson-pinctrl-common.yaml#`.
Runtime integration is with Linux pinctrl and GPIO framework drivers selected by `compatible`. Board
`.dts` files instantiate nodes that satisfy this schema; `make dt_binding_check` validates the
binding and inline examples, while `make dtbs_check` validates real board descriptions against the
same contract.

## Risks
- A missing or misspelled `compatible` value prevents both schema matching and driver binding.
- Omitting required fields such as `ranges`, `#address-cells`, `#size-cells` should fail dt-schema validation before boot.
- Open or partially open property handling can let board-specific typos escape schema validation and surface only at driver probe time.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/amlogic,meson-pinctrl-common.yaml` to parse this YAML, validate meta-schema rules, and compile its 0 inline example(s).
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/amlogic,meson-pinctrl-common.yaml` on affected board DTS files to confirm real nodes satisfy required properties, compatible choices, child node names, and referenced common schemas.
- Useful negative tests remove one required property, change `compatible`, add a bogus pin group/function, and add an undeclared property where closure is enabled.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/amlogic,meson-pinctrl-common.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/amlogic,meson-pinctrl-g12a-aobus.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/amlogic,meson-pinctrl-g12a-aobus.yaml

## Purpose
This file is a Linux Devicetree JSON-schema document for a pin multiplexing controller binding:
Amlogic Meson G12 AOBUS pinmux controller. It lives in the pinctrl binding tree and gives dt-schema
a machine-readable contract for board DTS nodes before the kernel pinctrl/GPIO drivers consume those
nodes during probe.

The schema relies on title, compatible values, and property constraints rather than a long description block.

The binding is maintained in-source by Neil Armstrong <neil.armstrong@linaro.org>.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/pinctrl/amlogic,meson-pinctrl-g12a-aobus.yaml#` with meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Compatible contract: `amlogic,meson-g12a-aobus-pinctrl`.
- Required properties: `compatible`.
- Top-level framework properties: `compatible`.
- Vendor or device-specific extensions: none declared.
- Other declared top-level properties: none declared.
- Child-node or reusable schema API: patternProperties `^bank@[0-9a-f]+$`.
- Property detail signals: compatible (enum `amlogic,meson-g12a-aobus-pinctrl`).

## Control Flow
There is no imperative execution path in this YAML. Validation starts when dt-schema selects this
document for a node whose `compatible` value matches the schema, checks the required list, evaluates
referenced common pinctrl/GPIO schemas, applies property constraints, then walks child-node patterns
and conditional branches.

This file contains 1 `allOf`, 0 `oneOf`, 0 `anyOf`, and 0 `if` blocks. Property closure: no explicit
top-level closure keyword is present in the parsed schema.

## State and Persistence Behavior
The binding stores no runtime state. It persists as source-controlled schema text, while the state
it describes persists in DTS/DTB data: register windows, GPIO provider cell counts, interrupt
wiring, pin groups, mux functions, drive strengths, pulls, and optional child pin configuration
nodes. Kernel drivers consume the validated DT data at boot or device probe and then program
hardware pin mux, pad, and GPIO state; this YAML only constrains that data before runtime.

## Dependencies and Integration Points
- Schema references: `amlogic,meson-pinctrl-common.yaml#`, `amlogic,meson-pinctrl-common.yaml#/$defs/meson-gpio`, `amlogic,meson-pinctrl-common.yaml#/$defs/meson-pins`.
- Textual schema references: `/schemas/pinctrl/amlogic,meson-pinctrl-g12a-aobus.yaml#`.
Runtime integration is with Linux pinctrl and GPIO framework drivers selected by `compatible`. Board
`.dts` files instantiate nodes that satisfy this schema; `make dt_binding_check` validates the
binding and inline examples, while `make dtbs_check` validates real board descriptions against the
same contract.

## Risks
- A missing or misspelled `compatible` value prevents both schema matching and driver binding.
- Omitting required fields such as `compatible` should fail dt-schema validation before boot.
- Child node regexes and reusable pin configuration schemas are easy to misuse; incorrect group/function names can validate poorly or fail later in driver lookup tables.
- Open or partially open property handling can let board-specific typos escape schema validation and surface only at driver probe time.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/amlogic,meson-pinctrl-g12a-aobus.yaml` to parse this YAML, validate meta-schema rules, and compile its 1 inline example(s).
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/amlogic,meson-pinctrl-g12a-aobus.yaml` on affected board DTS files to confirm real nodes satisfy required properties, compatible choices, child node names, and referenced common schemas.
- Useful negative tests remove one required property, change `compatible`, and add an undeclared property where closure is enabled. Example seed: ao_pinctrl: pinctrl {; compatible = "amlogic,meson-g12a-aobus-pinctrl";; #address-cells = <1>;; #size-cells = <1>;; ranges;.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/amlogic,meson-pinctrl-g12a-aobus.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/amlogic,meson-pinctrl-g12a-periphs.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/amlogic,meson-pinctrl-g12a-periphs.yaml

## Purpose
This file is a Linux Devicetree JSON-schema document for a pin multiplexing controller binding:
Amlogic Meson G12 PERIPHS pinmux controller. It lives in the pinctrl binding tree and gives dt-
schema a machine-readable contract for board DTS nodes before the kernel pinctrl/GPIO drivers
consume those nodes during probe.

The schema relies on title, compatible values, and property constraints rather than a long description block.

The binding is maintained in-source by Neil Armstrong <neil.armstrong@linaro.org>.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/pinctrl/amlogic,meson-pinctrl-g12a-periphs.yaml#` with meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Compatible contract: `amlogic,meson-g12a-periphs-pinctrl`.
- Required properties: `compatible`.
- Top-level framework properties: `compatible`.
- Vendor or device-specific extensions: none declared.
- Other declared top-level properties: none declared.
- Child-node or reusable schema API: patternProperties `^bank@[0-9a-f]+$`.
- Property detail signals: compatible (enum `amlogic,meson-g12a-periphs-pinctrl`).

## Control Flow
There is no imperative execution path in this YAML. Validation starts when dt-schema selects this
document for a node whose `compatible` value matches the schema, checks the required list, evaluates
referenced common pinctrl/GPIO schemas, applies property constraints, then walks child-node patterns
and conditional branches.

This file contains 1 `allOf`, 0 `oneOf`, 0 `anyOf`, and 0 `if` blocks. Property closure: no explicit
top-level closure keyword is present in the parsed schema.

## State and Persistence Behavior
The binding stores no runtime state. It persists as source-controlled schema text, while the state
it describes persists in DTS/DTB data: register windows, GPIO provider cell counts, interrupt
wiring, pin groups, mux functions, drive strengths, pulls, and optional child pin configuration
nodes. Kernel drivers consume the validated DT data at boot or device probe and then program
hardware pin mux, pad, and GPIO state; this YAML only constrains that data before runtime.

## Dependencies and Integration Points
- Schema references: `amlogic,meson-pinctrl-common.yaml#`, `amlogic,meson-pinctrl-common.yaml#/$defs/meson-gpio`, `amlogic,meson-pinctrl-common.yaml#/$defs/meson-pins`.
- Textual schema references: `/schemas/pinctrl/amlogic,meson-pinctrl-g12a-periphs.yaml#`.
Runtime integration is with Linux pinctrl and GPIO framework drivers selected by `compatible`. Board
`.dts` files instantiate nodes that satisfy this schema; `make dt_binding_check` validates the
binding and inline examples, while `make dtbs_check` validates real board descriptions against the
same contract.

## Risks
- A missing or misspelled `compatible` value prevents both schema matching and driver binding.
- Omitting required fields such as `compatible` should fail dt-schema validation before boot.
- Child node regexes and reusable pin configuration schemas are easy to misuse; incorrect group/function names can validate poorly or fail later in driver lookup tables.
- Open or partially open property handling can let board-specific typos escape schema validation and surface only at driver probe time.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/amlogic,meson-pinctrl-g12a-periphs.yaml` to parse this YAML, validate meta-schema rules, and compile its 1 inline example(s).
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/amlogic,meson-pinctrl-g12a-periphs.yaml` on affected board DTS files to confirm real nodes satisfy required properties, compatible choices, child node names, and referenced common schemas.
- Useful negative tests remove one required property, change `compatible`, and add an undeclared property where closure is enabled. Example seed: periphs_pinctrl: pinctrl {; compatible = "amlogic,meson-g12a-periphs-pinctrl";; #address-cells = <1>;; #size-cells = <1>;; ranges;.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/amlogic,meson-pinctrl-g12a-periphs.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/amlogic,meson8-pinctrl-aobus.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/amlogic,meson8-pinctrl-aobus.yaml

## Purpose
This file is a Linux Devicetree JSON-schema document for a pin multiplexing controller binding:
Amlogic Meson8 AOBUS pinmux controller. It lives in the pinctrl binding tree and gives dt-schema a
machine-readable contract for board DTS nodes before the kernel pinctrl/GPIO drivers consume those
nodes during probe.

The schema relies on title, compatible values, and property constraints rather than a long description block.

The binding is maintained in-source by Neil Armstrong <neil.armstrong@linaro.org>.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/pinctrl/amlogic,meson8-pinctrl-aobus.yaml#` with meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Compatible contract: `amlogic,meson8-aobus-pinctrl`, `amlogic,meson8b-aobus-pinctrl`, `amlogic,meson-gxbb-aobus-pinctrl`, `amlogic,meson-gxl-aobus-pinctrl`, `amlogic,meson-axg-aobus-pinctrl`, `amlogic,meson8m2-aobus-pinctrl`.
- Required properties: `compatible`.
- Top-level framework properties: `compatible`.
- Vendor or device-specific extensions: none declared.
- Other declared top-level properties: none declared.
- Child-node or reusable schema API: patternProperties `^bank@[0-9a-f]+$`.
- Property detail signals: compatible.

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
- Schema references: `amlogic,meson-pinctrl-common.yaml#`, `amlogic,meson-pinctrl-common.yaml#/$defs/meson-gpio`, `amlogic,meson-pinctrl-common.yaml#/$defs/meson-pins`.
- Textual schema references: `/schemas/pinctrl/amlogic,meson8-pinctrl-aobus.yaml#`.
Runtime integration is with Linux pinctrl and GPIO framework drivers selected by `compatible`. Board
`.dts` files instantiate nodes that satisfy this schema; `make dt_binding_check` validates the
binding and inline examples, while `make dtbs_check` validates real board descriptions against the
same contract.

## Risks
- A missing or misspelled `compatible` value prevents both schema matching and driver binding.
- Omitting required fields such as `compatible` should fail dt-schema validation before boot.
- Child node regexes and reusable pin configuration schemas are easy to misuse; incorrect group/function names can validate poorly or fail later in driver lookup tables.
- Open or partially open property handling can let board-specific typos escape schema validation and surface only at driver probe time.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/amlogic,meson8-pinctrl-aobus.yaml` to parse this YAML, validate meta-schema rules, and compile its 1 inline example(s).
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/amlogic,meson8-pinctrl-aobus.yaml` on affected board DTS files to confirm real nodes satisfy required properties, compatible choices, child node names, and referenced common schemas.
- Useful negative tests remove one required property, change `compatible`, and add an undeclared property where closure is enabled. Example seed: pinctrl_aobus: pinctrl {; compatible = "amlogic,meson8-aobus-pinctrl";; #address-cells = <1>;; #size-cells = <1>;; ranges;.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/amlogic,meson8-pinctrl-aobus.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/amlogic,meson8-pinctrl-cbus.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/amlogic,meson8-pinctrl-cbus.yaml

## Purpose
This file is a Linux Devicetree JSON-schema document for a pin multiplexing controller binding:
Amlogic Meson8 CBUS pinmux controller. It lives in the pinctrl binding tree and gives dt-schema a
machine-readable contract for board DTS nodes before the kernel pinctrl/GPIO drivers consume those
nodes during probe.

The schema relies on title, compatible values, and property constraints rather than a long description block.

The binding is maintained in-source by Neil Armstrong <neil.armstrong@linaro.org>.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/pinctrl/amlogic,meson8-pinctrl-cbus.yaml#` with meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Compatible contract: `amlogic,meson8-cbus-pinctrl`, `amlogic,meson8b-cbus-pinctrl`, `amlogic,meson-gxbb-periphs-pinctrl`, `amlogic,meson-gxl-periphs-pinctrl`, `amlogic,meson-axg-periphs-pinctrl`, `amlogic,meson8m2-cbus-pinctrl`.
- Required properties: `compatible`.
- Top-level framework properties: `compatible`.
- Vendor or device-specific extensions: none declared.
- Other declared top-level properties: none declared.
- Child-node or reusable schema API: patternProperties `^bank@[0-9a-f]+$`.
- Property detail signals: compatible.

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
- Schema references: `amlogic,meson-pinctrl-common.yaml#`, `amlogic,meson-pinctrl-common.yaml#/$defs/meson-gpio`, `amlogic,meson-pinctrl-common.yaml#/$defs/meson-pins`.
- Textual schema references: `/schemas/pinctrl/amlogic,meson8-pinctrl-cbus.yaml#`.
Runtime integration is with Linux pinctrl and GPIO framework drivers selected by `compatible`. Board
`.dts` files instantiate nodes that satisfy this schema; `make dt_binding_check` validates the
binding and inline examples, while `make dtbs_check` validates real board descriptions against the
same contract.

## Risks
- A missing or misspelled `compatible` value prevents both schema matching and driver binding.
- Omitting required fields such as `compatible` should fail dt-schema validation before boot.
- Child node regexes and reusable pin configuration schemas are easy to misuse; incorrect group/function names can validate poorly or fail later in driver lookup tables.
- Open or partially open property handling can let board-specific typos escape schema validation and surface only at driver probe time.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/amlogic,meson8-pinctrl-cbus.yaml` to parse this YAML, validate meta-schema rules, and compile its 1 inline example(s).
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/amlogic,meson8-pinctrl-cbus.yaml` on affected board DTS files to confirm real nodes satisfy required properties, compatible choices, child node names, and referenced common schemas.
- Useful negative tests remove one required property, change `compatible`, and add an undeclared property where closure is enabled. Example seed: pinctrl_cbus: pinctrl {; compatible = "amlogic,meson8-cbus-pinctrl";; #address-cells = <1>;; #size-cells = <1>;; ranges;.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/amlogic,meson8-pinctrl-cbus.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/amlogic,pinctrl-a4.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/amlogic,pinctrl-a4.yaml

## Purpose
This file is a Linux Devicetree JSON-schema document for a pin multiplexing controller binding:
Amlogic pinmux controller. It lives in the pinctrl binding tree and gives dt-schema a machine-
readable contract for board DTS nodes before the kernel pinctrl/GPIO drivers consume those nodes
during probe.

The schema relies on title, compatible values, and property constraints rather than a long description block.

The binding is maintained in-source by Xianwei Zhao <xianwei.zhao@amlogic.com>.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/pinctrl/amlogic,pinctrl-a4.yaml#` with meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Compatible contract: `amlogic,pinctrl-a4`, `amlogic,pinctrl-s6`, `amlogic,pinctrl-s7`, `amlogic,pinctrl-a5`, `amlogic,pinctrl-s7d`.
- Required properties: `compatible`, `#address-cells`, `#size-cells`, `ranges`.
- Top-level framework properties: `compatible`, `#address-cells`, `#size-cells`.
- Vendor or device-specific extensions: none declared.
- Other declared top-level properties: `ranges`.
- Child-node or reusable schema API: patternProperties `^gpio@[0-9a-f]+$`, `^func-[0-9a-z-]+$`.
- Property detail signals: compatible; #address-cells (const `2`); #size-cells (const `2`); ranges.

## Control Flow
There is no imperative execution path in this YAML. Validation starts when dt-schema selects this
document for a node whose `compatible` value matches the schema, checks the required list, evaluates
referenced common pinctrl/GPIO schemas, applies property constraints, then walks child-node patterns
and conditional branches.

This file contains 2 `allOf`, 1 `oneOf`, 0 `anyOf`, and 0 `if` blocks. Property closure: top-level
`additionalProperties: false` rejects undeclared properties.

## State and Persistence Behavior
The binding stores no runtime state. It persists as source-controlled schema text, while the state
it describes persists in DTS/DTB data: register windows, GPIO provider cell counts, interrupt
wiring, pin groups, mux functions, drive strengths, pulls, and optional child pin configuration
nodes. Kernel drivers consume the validated DT data at boot or device probe and then program
hardware pin mux, pad, and GPIO state; this YAML only constrains that data before runtime.

## Dependencies and Integration Points
- Schema references: `pinctrl.yaml#`, `/schemas/pinctrl/pincfg-node.yaml`, `/schemas/pinctrl/pinmux-node.yaml`.
- Example/header integration: `dt-bindings/pinctrl/amlogic,pinctrl.h`.
- Textual schema references: `/schemas/pinctrl/amlogic,pinctrl-a4.yaml#`, `/schemas/pinctrl/pincfg-node.yaml`, `/schemas/pinctrl/pinmux-node.yaml`.
Runtime integration is with Linux pinctrl and GPIO framework drivers selected by `compatible`. Board
`.dts` files instantiate nodes that satisfy this schema; `make dt_binding_check` validates the
binding and inline examples, while `make dtbs_check` validates real board descriptions against the
same contract.

## Risks
- A missing or misspelled `compatible` value prevents both schema matching and driver binding.
- Omitting required fields such as `compatible`, `#address-cells`, `#size-cells`, `ranges` should fail dt-schema validation before boot.
- Child node regexes and reusable pin configuration schemas are easy to misuse; incorrect group/function names can validate poorly or fail later in driver lookup tables.
- The closed property model catches typos, but any newly needed board property requires a binding update before DTS changes can pass validation.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/amlogic,pinctrl-a4.yaml` to parse this YAML, validate meta-schema rules, and compile its 1 inline example(s).
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/amlogic,pinctrl-a4.yaml` on affected board DTS files to confirm real nodes satisfy required properties, compatible choices, child node names, and referenced common schemas.
- Useful negative tests remove one required property, change `compatible`, and add an undeclared property where closure is enabled. Example seed: #include <dt-bindings/pinctrl/amlogic,pinctrl.h>; apb {; #address-cells = <2>;; #size-cells = <2>;; periphs_pinctrl: pinctrl {.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/amlogic,pinctrl-a4.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/apple,pinctrl.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/apple,pinctrl.yaml

## Purpose
This file is a Linux Devicetree JSON-schema document for a pin controller binding: Apple GPIO
controller. It lives in the pinctrl binding tree and gives dt-schema a machine-readable contract for
board DTS nodes before the kernel pinctrl/GPIO drivers consume those nodes during probe.

The Apple GPIO controller is a simple combined pin and GPIO controller present on Apple ARM SoC
platforms, including various iPhone and iPad devices and the "Apple Silicon" Macs.

The binding is maintained in-source by Mark Kettenis <kettenis@openbsd.org>.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/pinctrl/apple,pinctrl.yaml#` with meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Compatible contract: `apple,t6020-pinctrl`, `apple,t8122-pinctrl`, `apple,t8103-pinctrl`, `apple,s5l8960x-pinctrl`, `apple,t7000-pinctrl`, `apple,s8000-pinctrl`, `apple,t8010-pinctrl`, `apple,t8015-pinctrl`, `apple,t8112-pinctrl`, `apple,t6000-pinctrl`, `apple,pinctrl`.
- Required properties: `compatible`, `reg`, `gpio-controller`, `#gpio-cells`, `gpio-ranges`, `apple,npins`.
- Top-level framework properties: `compatible`, `reg`, `clocks`, `gpio-controller`, `#gpio-cells`, `gpio-ranges`, `interrupts`, `interrupt-controller`, `#interrupt-cells`, `power-domains`.
- Vendor or device-specific extensions: `apple,npins`.
- Other declared top-level properties: none declared.
- Child-node or reusable schema API: patternProperties `-pins$`.
- Property detail signals: compatible; reg (maxItems 1); clocks (maxItems 1); gpio-controller; #gpio-cells (const `2`); gpio-ranges (maxItems 1); apple,npins (The number of pins in this GPIO controller.; ref `/schemas/types.yaml#/definitions/uint32`); interrupts (maxItems 7; minItems 1; One interrupt for each of the (up to 7) interrupt groups supported by the controller sorted by in...); interrupt-controller; #interrupt-cells (const `2`); power-domains (maxItems 1).

## Control Flow
There is no imperative execution path in this YAML. Validation starts when dt-schema selects this
document for a node whose `compatible` value matches the schema, checks the required list, evaluates
referenced common pinctrl/GPIO schemas, applies property constraints, then walks child-node patterns
and conditional branches.

This file contains 1 `allOf`, 1 `oneOf`, 0 `anyOf`, and 0 `if` blocks. Property closure: top-level
`additionalProperties: false` rejects undeclared properties.

## State and Persistence Behavior
The binding stores no runtime state. It persists as source-controlled schema text, while the state
it describes persists in DTS/DTB data: register windows, GPIO provider cell counts, interrupt
wiring, pin groups, mux functions, drive strengths, pulls, and optional child pin configuration
nodes. Kernel drivers consume the validated DT data at boot or device probe and then program
hardware pin mux, pad, and GPIO state; this YAML only constrains that data before runtime.

## Dependencies and Integration Points
- Schema references: `/schemas/types.yaml#/definitions/uint32`, `pinmux-node.yaml#`, `pinctrl.yaml#`.
- Example/header integration: `dt-bindings/interrupt-controller/apple-aic.h`, `dt-bindings/pinctrl/apple.h`.
- Textual schema references: `/schemas/pinctrl/apple,pinctrl.yaml#`, `/schemas/types.yaml#/definitions/uint32`.
Runtime integration is with Linux pinctrl and GPIO framework drivers selected by `compatible`. Board
`.dts` files instantiate nodes that satisfy this schema; `make dt_binding_check` validates the
binding and inline examples, while `make dtbs_check` validates real board descriptions against the
same contract.

## Risks
- A missing or misspelled `compatible` value prevents both schema matching and driver binding.
- Omitting required fields such as `compatible`, `reg`, `gpio-controller`, `#gpio-cells`, `gpio-ranges` should fail dt-schema validation before boot.
- Child node regexes and reusable pin configuration schemas are easy to misuse; incorrect group/function names can validate poorly or fail later in driver lookup tables.
- The closed property model catches typos, but any newly needed board property requires a binding update before DTS changes can pass validation.
- GPIO provider fields such as `#gpio-cells`, `gpio-ranges`, and interrupt controller wiring must match the runtime driver's expectations or GPIO consumers will resolve the wrong pins.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/apple,pinctrl.yaml` to parse this YAML, validate meta-schema rules, and compile its 1 inline example(s).
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/apple,pinctrl.yaml` on affected board DTS files to confirm real nodes satisfy required properties, compatible choices, child node names, and referenced common schemas.
- Useful negative tests remove one required property, change `compatible`, and add an undeclared property where closure is enabled. Example seed: #include <dt-bindings/interrupt-controller/apple-aic.h>; #include <dt-bindings/pinctrl/apple.h>; soc {; #address-cells = <2>;.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/apple,pinctrl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/aspeed,ast2400-pinctrl.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/aspeed,ast2400-pinctrl.yaml

## Purpose
This file is a Linux Devicetree JSON-schema document for a pin controller binding: ASPEED AST2400
Pin Controller. It lives in the pinctrl binding tree and gives dt-schema a machine-readable contract
for board DTS nodes before the kernel pinctrl/GPIO drivers consume those nodes during probe.

The pin controller node should be the child of a syscon node with the required property: -
compatible: Should be one of the following: "aspeed,ast2400-scu", "syscon", "simple-mfd" Refer to
the bindings described in Documentation/devicetree/bindings/mfd/syscon.yaml

The binding is maintained in-source by Andrew Jeffery <andrew@aj.id.au>.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/pinctrl/aspeed,ast2400-pinctrl.yaml#` with meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Compatible contract: `aspeed,ast2400-pinctrl`.
- Required properties: `compatible`.
- Top-level framework properties: `compatible`, `reg`.
- Vendor or device-specific extensions: none declared.
- Other declared top-level properties: none declared.
- Child-node or reusable schema API: no named child-node API or pattern child-node contract is declared.
- Property detail signals: compatible (const `aspeed,ast2400-pinctrl`); reg (maxItems 2).

## Control Flow
There is no imperative execution path in this YAML. Validation starts when dt-schema selects this
document for a node whose `compatible` value matches the schema, checks the required list, evaluates
referenced common pinctrl/GPIO schemas, applies property constraints, then walks child-node patterns
and conditional branches.

This file contains 1 `allOf`, 0 `oneOf`, 0 `anyOf`, and 0 `if` blocks. Property closure: no explicit
top-level closure keyword is present in the parsed schema.

## State and Persistence Behavior
The binding stores no runtime state. It persists as source-controlled schema text, while the state
it describes persists in DTS/DTB data: register windows, GPIO provider cell counts, interrupt
wiring, pin groups, mux functions, drive strengths, pulls, and optional child pin configuration
nodes. Kernel drivers consume the validated DT data at boot or device probe and then program
hardware pin mux, pad, and GPIO state; this YAML only constrains that data before runtime.

## Dependencies and Integration Points
- Schema references: `pinmux-node.yaml#`, `pinctrl.yaml#`.
- Textual schema references: `/schemas/pinctrl/aspeed,ast2400-pinctrl.yaml#`.
Runtime integration is with Linux pinctrl and GPIO framework drivers selected by `compatible`. Board
`.dts` files instantiate nodes that satisfy this schema; `make dt_binding_check` validates the
binding and inline examples, while `make dtbs_check` validates real board descriptions against the
same contract.

## Risks
- A missing or misspelled `compatible` value prevents both schema matching and driver binding.
- Omitting required fields such as `compatible` should fail dt-schema validation before boot.
- Open or partially open property handling can let board-specific typos escape schema validation and surface only at driver probe time.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/aspeed,ast2400-pinctrl.yaml` to parse this YAML, validate meta-schema rules, and compile its 1 inline example(s).
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/aspeed,ast2400-pinctrl.yaml` on affected board DTS files to confirm real nodes satisfy required properties, compatible choices, child node names, and referenced common schemas.
- Useful negative tests remove one required property, change `compatible`, and add an undeclared property where closure is enabled. Example seed: syscon: scu@1e6e2000 {; compatible = "aspeed,ast2400-scu", "syscon", "simple-mfd";; reg = <0x1e6e2000 0x1a8>;; #clock-cells = <1>;; #reset-cells = <1>;.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/aspeed,ast2400-pinctrl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/aspeed,ast2500-pinctrl.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/aspeed,ast2500-pinctrl.yaml

## Purpose
This file is a Linux Devicetree JSON-schema document for a pin controller binding: ASPEED AST2500
Pin Controller. It lives in the pinctrl binding tree and gives dt-schema a machine-readable contract
for board DTS nodes before the kernel pinctrl/GPIO drivers consume those nodes during probe.

The pin controller node should be the child of a syscon node with the required property: -
compatible: Should be one of the following: "aspeed,ast2500-scu", "syscon", "simple-mfd"
"aspeed,g5-scu", "syscon", "simple-mfd" Refer to the bindings described in
Documentation/devicetree/bindings/mfd/syscon.yaml

The binding is maintained in-source by Andrew Jeffery <andrew@aj.id.au>.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/pinctrl/aspeed,ast2500-pinctrl.yaml#` with meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Compatible contract: `aspeed,ast2500-pinctrl`.
- Required properties: `compatible`, `aspeed,external-nodes`.
- Top-level framework properties: `compatible`, `reg`.
- Vendor or device-specific extensions: `aspeed,external-nodes`.
- Other declared top-level properties: none declared.
- Child-node or reusable schema API: no named child-node API or pattern child-node contract is declared.
- Property detail signals: compatible (const `aspeed,ast2500-pinctrl`); reg (maxItems 2); aspeed,external-nodes (maxItems 2; minItems 2; A cell of phandles to external controller nodes: 0: compatible with "aspeed,ast2500-gfx", "syscon...; ref `/schemas/types.yaml#/definitions/phandle-array`).

## Control Flow
There is no imperative execution path in this YAML. Validation starts when dt-schema selects this
document for a node whose `compatible` value matches the schema, checks the required list, evaluates
referenced common pinctrl/GPIO schemas, applies property constraints, then walks child-node patterns
and conditional branches.

This file contains 1 `allOf`, 0 `oneOf`, 0 `anyOf`, and 0 `if` blocks. Property closure: no explicit
top-level closure keyword is present in the parsed schema.

## State and Persistence Behavior
The binding stores no runtime state. It persists as source-controlled schema text, while the state
it describes persists in DTS/DTB data: register windows, GPIO provider cell counts, interrupt
wiring, pin groups, mux functions, drive strengths, pulls, and optional child pin configuration
nodes. Kernel drivers consume the validated DT data at boot or device probe and then program
hardware pin mux, pad, and GPIO state; this YAML only constrains that data before runtime.

## Dependencies and Integration Points
- Schema references: `/schemas/types.yaml#/definitions/phandle-array`, `pinmux-node.yaml#`, `pinctrl.yaml#`.
- Example/header integration: `dt-bindings/clock/aspeed-clock.h`.
- Textual schema references: `/schemas/pinctrl/aspeed,ast2500-pinctrl.yaml#`, `/schemas/types.yaml#/definitions/phandle-array`.
Runtime integration is with Linux pinctrl and GPIO framework drivers selected by `compatible`. Board
`.dts` files instantiate nodes that satisfy this schema; `make dt_binding_check` validates the
binding and inline examples, while `make dtbs_check` validates real board descriptions against the
same contract.

## Risks
- A missing or misspelled `compatible` value prevents both schema matching and driver binding.
- Omitting required fields such as `compatible`, `aspeed,external-nodes` should fail dt-schema validation before boot.
- Open or partially open property handling can let board-specific typos escape schema validation and surface only at driver probe time.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/aspeed,ast2500-pinctrl.yaml` to parse this YAML, validate meta-schema rules, and compile its 1 inline example(s).
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/aspeed,ast2500-pinctrl.yaml` on affected board DTS files to confirm real nodes satisfy required properties, compatible choices, child node names, and referenced common schemas.
- Useful negative tests remove one required property, change `compatible`, and add an undeclared property where closure is enabled. Example seed: #include <dt-bindings/clock/aspeed-clock.h>; scu@1e6e2000 {; compatible = "aspeed,ast2500-scu", "syscon", "simple-mfd";; reg = <0x1e6e2000 0x1a8>;; #clock-cells = <1>;.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/aspeed,ast2500-pinctrl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/aspeed,ast2600-pinctrl.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/aspeed,ast2600-pinctrl.yaml

## Purpose
This file is a Linux Devicetree JSON-schema document for a pin controller binding: ASPEED AST2600
Pin Controller. It lives in the pinctrl binding tree and gives dt-schema a machine-readable contract
for board DTS nodes before the kernel pinctrl/GPIO drivers consume those nodes during probe.

The pin controller node should be the child of a syscon node with the required property: -
compatible: Should be one of the following: "aspeed,ast2600-scu", "syscon", "simple-mfd" Refer to
the bindings described in Documentation/devicetree/bindings/mfd/syscon.yaml Note: According to the
NCSI specification, the reference clock output pin (RMIIXRCLKO) is not required on the management
controller side. To optimize pin usage, add "NCSI" pin groups that are equivalent to the RMII pin
groups, but without the RMIIXRCLKO pin.

The binding is maintained in-source by Andrew Jeffery <andrew@aj.id.au>.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/pinctrl/aspeed,ast2600-pinctrl.yaml#` with meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Compatible contract: `aspeed,ast2600-pinctrl`.
- Required properties: `compatible`.
- Top-level framework properties: `compatible`.
- Vendor or device-specific extensions: none declared.
- Other declared top-level properties: none declared.
- Child-node or reusable schema API: no named child-node API or pattern child-node contract is declared.
- Property detail signals: compatible (const `aspeed,ast2600-pinctrl`).

## Control Flow
There is no imperative execution path in this YAML. Validation starts when dt-schema selects this
document for a node whose `compatible` value matches the schema, checks the required list, evaluates
referenced common pinctrl/GPIO schemas, applies property constraints, then walks child-node patterns
and conditional branches.

This file contains 1 `allOf`, 0 `oneOf`, 0 `anyOf`, and 0 `if` blocks. Property closure: no explicit
top-level closure keyword is present in the parsed schema.

## State and Persistence Behavior
The binding stores no runtime state. It persists as source-controlled schema text, while the state
it describes persists in DTS/DTB data: register windows, GPIO provider cell counts, interrupt
wiring, pin groups, mux functions, drive strengths, pulls, and optional child pin configuration
nodes. Kernel drivers consume the validated DT data at boot or device probe and then program
hardware pin mux, pad, and GPIO state; this YAML only constrains that data before runtime.

## Dependencies and Integration Points
- Schema references: `pinmux-node.yaml#`, `pinctrl.yaml#`.
- Textual schema references: `/schemas/pinctrl/aspeed,ast2600-pinctrl.yaml#`.
Runtime integration is with Linux pinctrl and GPIO framework drivers selected by `compatible`. Board
`.dts` files instantiate nodes that satisfy this schema; `make dt_binding_check` validates the
binding and inline examples, while `make dtbs_check` validates real board descriptions against the
same contract.

## Risks
- A missing or misspelled `compatible` value prevents both schema matching and driver binding.
- Omitting required fields such as `compatible` should fail dt-schema validation before boot.
- Open or partially open property handling can let board-specific typos escape schema validation and surface only at driver probe time.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/aspeed,ast2600-pinctrl.yaml` to parse this YAML, validate meta-schema rules, and compile its 1 inline example(s).
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/aspeed,ast2600-pinctrl.yaml` on affected board DTS files to confirm real nodes satisfy required properties, compatible choices, child node names, and referenced common schemas.
- Useful negative tests remove one required property, change `compatible`, and add an undeclared property where closure is enabled. Example seed: syscon: scu@1e6e2000 {; compatible = "aspeed,ast2600-scu", "syscon", "simple-mfd";; reg = <0x1e6e2000 0xf6c>;; #clock-cells = <1>;; #reset-cells = <1>;.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/aspeed,ast2600-pinctrl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/atmel,at91rm9200-pinctrl.yaml -->
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

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/atmel,at91rm9200-pinctrl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/awinic,aw9523-pinctrl.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/awinic,aw9523-pinctrl.yaml

## Purpose
This file is a Linux Devicetree JSON-schema document for a pin controller binding: Awinic
AW9523/AW9523B I2C GPIO Expander. It lives in the pinctrl binding tree and gives dt-schema a
machine-readable contract for board DTS nodes before the kernel pinctrl/GPIO drivers consume those
nodes during probe.

The Awinic AW9523/AW9523B I2C GPIO Expander featuring 16 multi-function I/O, 256 steps PWM mode and
interrupt support.

The binding is maintained in-source by AngeloGioacchino Del Regno
<angelogioacchino.delregno@somainline.org>.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/pinctrl/awinic,aw9523-pinctrl.yaml#` with meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Compatible contract: `awinic,aw9523-pinctrl`.
- Required properties: `compatible`, `reg`, `gpio-controller`, `#gpio-cells`, `gpio-ranges`.
- Top-level framework properties: `compatible`, `reg`, `#gpio-cells`, `gpio-controller`, `gpio-ranges`, `interrupt-controller`, `interrupts`, `#interrupt-cells`.
- Vendor or device-specific extensions: none declared.
- Other declared top-level properties: `reset-gpios`.
- Child-node or reusable schema API: patternProperties `-pins$`.
- Property detail signals: compatible (const `awinic,aw9523-pinctrl`); reg (maxItems 1); #gpio-cells (const `2`; Specifying the pin number and flags, as defined in include/dt-bindings/gpio/gpio.h); gpio-controller; gpio-ranges (maxItems 1); interrupt-controller; interrupts (maxItems 1; Specifies the INTN pin IRQ.); #interrupt-cells (const `2`; Specifies the PIN numbers and Flags, as defined in defined in include/dt-bindings/interrupt-contr...); reset-gpios (maxItems 1).

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
- Schema references: `/schemas/pinctrl/pincfg-node.yaml`.
- Example/header integration: `dt-bindings/gpio/gpio.h`, `dt-bindings/interrupt-controller/irq.h`.
- Textual schema references: `/schemas/pinctrl/awinic,aw9523-pinctrl.yaml#`, `/schemas/pinctrl/pincfg-node.yaml`.
Runtime integration is with Linux pinctrl and GPIO framework drivers selected by `compatible`. Board
`.dts` files instantiate nodes that satisfy this schema; `make dt_binding_check` validates the
binding and inline examples, while `make dtbs_check` validates real board descriptions against the
same contract.

## Risks
- A missing or misspelled `compatible` value prevents both schema matching and driver binding.
- Omitting required fields such as `compatible`, `reg`, `gpio-controller`, `#gpio-cells`, `gpio-ranges` should fail dt-schema validation before boot.
- Child node regexes and reusable pin configuration schemas are easy to misuse; incorrect group/function names can validate poorly or fail later in driver lookup tables.
- The closed property model catches typos, but any newly needed board property requires a binding update before DTS changes can pass validation.
- GPIO provider fields such as `#gpio-cells`, `gpio-ranges`, and interrupt controller wiring must match the runtime driver's expectations or GPIO consumers will resolve the wrong pins.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/awinic,aw9523-pinctrl.yaml` to parse this YAML, validate meta-schema rules, and compile its 1 inline example(s).
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/awinic,aw9523-pinctrl.yaml` on affected board DTS files to confirm real nodes satisfy required properties, compatible choices, child node names, and referenced common schemas.
- Useful negative tests remove one required property, change `compatible`, and add an undeclared property where closure is enabled. Example seed: #include <dt-bindings/gpio/gpio.h>; #include <dt-bindings/interrupt-controller/irq.h>; i2c {; #address-cells = <1>;.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/awinic,aw9523-pinctrl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/bitmain,bm1880-pinctrl.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/bitmain,bm1880-pinctrl.yaml

## Purpose
This file is a Linux Devicetree JSON-schema document for a pin controller binding: Bitmain BM1880
Pin Controller. It lives in the pinctrl binding tree and gives dt-schema a machine-readable contract
for board DTS nodes before the kernel pinctrl/GPIO drivers consume those nodes during probe.

The schema relies on title, compatible values, and property constraints rather than a long description block.

The binding is maintained in-source by Manivannan Sadhasivam <manivannan.sadhasivam@linaro.org>.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/pinctrl/bitmain,bm1880-pinctrl.yaml#` with meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Compatible contract: `bitmain,bm1880-pinctrl`.
- Required properties: `compatible`, `reg`.
- Top-level framework properties: `compatible`, `reg`.
- Vendor or device-specific extensions: none declared.
- Other declared top-level properties: none declared.
- Child-node or reusable schema API: no named child-node API or pattern child-node contract is declared.
- Property detail signals: compatible (const `bitmain,bm1880-pinctrl`); reg (maxItems 1).

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
- Schema references: `/schemas/pinctrl/pincfg-node.yaml#`, `/schemas/pinctrl/pinmux-node.yaml#`.
- Textual schema references: `/schemas/pinctrl/bitmain,bm1880-pinctrl.yaml#`, `/schemas/pinctrl/pincfg-node.yaml#`, `/schemas/pinctrl/pinmux-node.yaml#`.
Runtime integration is with Linux pinctrl and GPIO framework drivers selected by `compatible`. Board
`.dts` files instantiate nodes that satisfy this schema; `make dt_binding_check` validates the
binding and inline examples, while `make dtbs_check` validates real board descriptions against the
same contract.

## Risks
- A missing or misspelled `compatible` value prevents both schema matching and driver binding.
- Omitting required fields such as `compatible`, `reg` should fail dt-schema validation before boot.
- Open or partially open property handling can let board-specific typos escape schema validation and surface only at driver probe time.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/bitmain,bm1880-pinctrl.yaml` to parse this YAML, validate meta-schema rules, and compile its 1 inline example(s).
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/bitmain,bm1880-pinctrl.yaml` on affected board DTS files to confirm real nodes satisfy required properties, compatible choices, child node names, and referenced common schemas.
- Useful negative tests remove one required property, change `compatible`, and add an undeclared property where closure is enabled. Example seed: pinctrl@400 {; compatible = "bitmain,bm1880-pinctrl";; reg = <0x400 0x120>;; uart0-default {.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/bitmain,bm1880-pinctrl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/brcm,bcm11351-pinctrl.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/brcm,bcm11351-pinctrl.yaml

## Purpose
This file is a Linux Devicetree JSON-schema document for a pin controller binding: Broadcom BCM281xx
pin controller. It lives in the pinctrl binding tree and gives dt-schema a machine-readable contract
for board DTS nodes before the kernel pinctrl/GPIO drivers consume those nodes during probe.

The schema relies on title, compatible values, and property constraints rather than a long description block.

The binding is maintained in-source by Florian Fainelli <florian.fainelli@broadcom.com>, Ray Jui
<rjui@broadcom.com>, Scott Branden <sbranden@broadcom.com>.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/pinctrl/brcm,bcm11351-pinctrl.yaml#` with meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Compatible contract: `brcm,bcm11351-pinctrl`.
- Required properties: `compatible`, `reg`.
- Top-level framework properties: `compatible`, `reg`.
- Vendor or device-specific extensions: none declared.
- Other declared top-level properties: none declared.
- Child-node or reusable schema API: patternProperties `-pins$`.
- Property detail signals: compatible (const `brcm,bcm11351-pinctrl`); reg (maxItems 1).

## Control Flow
There is no imperative execution path in this YAML. Validation starts when dt-schema selects this
document for a node whose `compatible` value matches the schema, checks the required list, evaluates
referenced common pinctrl/GPIO schemas, applies property constraints, then walks child-node patterns
and conditional branches.

This file contains 2 `allOf`, 0 `oneOf`, 0 `anyOf`, and 2 `if` blocks. Property closure: top-level
`unevaluatedProperties: false` closes properties after referenced schemas are evaluated.

## State and Persistence Behavior
The binding stores no runtime state. It persists as source-controlled schema text, while the state
it describes persists in DTS/DTB data: register windows, GPIO provider cell counts, interrupt
wiring, pin groups, mux functions, drive strengths, pulls, and optional child pin configuration
nodes. Kernel drivers consume the validated DT data at boot or device probe and then program
hardware pin mux, pad, and GPIO state; this YAML only constrains that data before runtime.

## Dependencies and Integration Points
- Schema references: `pinctrl.yaml#`, `pincfg-node.yaml#`.
- Textual schema references: `/schemas/pinctrl/brcm,bcm11351-pinctrl.yaml#`.
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
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/brcm,bcm11351-pinctrl.yaml` to parse this YAML, validate meta-schema rules, and compile its 1 inline example(s).
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/brcm,bcm11351-pinctrl.yaml` on affected board DTS files to confirm real nodes satisfy required properties, compatible choices, child node names, and referenced common schemas.
- Useful negative tests remove one required property, change `compatible`, and add an undeclared property where closure is enabled. Example seed: pinctrl@35004800 {; compatible = "brcm,bcm11351-pinctrl";; reg = <0x35004800 0x430>;; dev-a-active-pins {.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/brcm,bcm11351-pinctrl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/brcm,bcm21664-pinctrl.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/brcm,bcm21664-pinctrl.yaml

## Purpose
This file is a Linux Devicetree JSON-schema document for a pin controller binding: Broadcom BCM21664
pin controller. It lives in the pinctrl binding tree and gives dt-schema a machine-readable contract
for board DTS nodes before the kernel pinctrl/GPIO drivers consume those nodes during probe.

The schema relies on title, compatible values, and property constraints rather than a long description block.

The binding is maintained in-source by Florian Fainelli <florian.fainelli@broadcom.com>, Ray Jui
<rjui@broadcom.com>, Scott Branden <sbranden@broadcom.com>.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/pinctrl/brcm,bcm21664-pinctrl.yaml#` with meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Compatible contract: `brcm,bcm21664-pinctrl`.
- Required properties: `compatible`, `reg`.
- Top-level framework properties: `compatible`, `reg`.
- Vendor or device-specific extensions: none declared.
- Other declared top-level properties: none declared.
- Child-node or reusable schema API: patternProperties `-pins$`.
- Property detail signals: compatible (const `brcm,bcm21664-pinctrl`); reg (maxItems 1).

## Control Flow
There is no imperative execution path in this YAML. Validation starts when dt-schema selects this
document for a node whose `compatible` value matches the schema, checks the required list, evaluates
referenced common pinctrl/GPIO schemas, applies property constraints, then walks child-node patterns
and conditional branches.

This file contains 2 `allOf`, 0 `oneOf`, 0 `anyOf`, and 1 `if` blocks. Property closure: top-level
`unevaluatedProperties: false` closes properties after referenced schemas are evaluated.

## State and Persistence Behavior
The binding stores no runtime state. It persists as source-controlled schema text, while the state
it describes persists in DTS/DTB data: register windows, GPIO provider cell counts, interrupt
wiring, pin groups, mux functions, drive strengths, pulls, and optional child pin configuration
nodes. Kernel drivers consume the validated DT data at boot or device probe and then program
hardware pin mux, pad, and GPIO state; this YAML only constrains that data before runtime.

## Dependencies and Integration Points
- Schema references: `pinctrl.yaml#`, `pincfg-node.yaml#`.
- Textual schema references: `/schemas/pinctrl/brcm,bcm21664-pinctrl.yaml#`.
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
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/brcm,bcm21664-pinctrl.yaml` to parse this YAML, validate meta-schema rules, and compile its 1 inline example(s).
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/brcm,bcm21664-pinctrl.yaml` on affected board DTS files to confirm real nodes satisfy required properties, compatible choices, child node names, and referenced common schemas.
- Useful negative tests remove one required property, change `compatible`, and add an undeclared property where closure is enabled. Example seed: pinctrl@35004800 {; compatible = "brcm,bcm21664-pinctrl";; reg = <0x35004800 0x7f0>;; dev-a-active-pins {.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/brcm,bcm21664-pinctrl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/brcm,bcm2712c0-pinctrl.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/brcm,bcm2712c0-pinctrl.yaml

## Purpose
This file is a Linux Devicetree JSON-schema document for a pin multiplexing controller binding:
Broadcom STB family pin controller. It lives in the pinctrl binding tree and gives dt-schema a
machine-readable contract for board DTS nodes before the kernel pinctrl/GPIO drivers consume those
nodes during probe.

Broadcom's STB family of memory-mapped pin controllers. This includes the pin controllers inside the
BCM2712 SoC which are instances of the STB family and has two silicon variants, C0 and D0, which
differs slightly in terms of registers layout. The -aon- (Always On) variant is the same IP block
but differs in the number of pins that are associated and the pinmux functions for each of those
pins.

The binding is maintained in-source by Ivan T. Ivanov <iivanov@suse.de>, A. della Porta
<andrea.porta@suse.com>.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/pinctrl/brcm,bcm2712c0-pinctrl.yaml#` with meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Compatible contract: `brcm,bcm2712c0-pinctrl`, `brcm,bcm2712c0-aon-pinctrl`, `brcm,bcm2712d0-pinctrl`, `brcm,bcm2712d0-aon-pinctrl`.
- Required properties: `compatible`, `reg`.
- Top-level framework properties: `compatible`, `reg`.
- Vendor or device-specific extensions: none declared.
- Other declared top-level properties: none declared.
- Child-node or reusable schema API: patternProperties `-state$`; local definitions `brcmstb-pinctrl-state`.
- Property detail signals: compatible (enum `brcm,bcm2712c0-pinctrl`, `brcm,bcm2712c0-aon-pinctrl`, `brcm,bcm2712d0-pinctrl`, `brcm,bcm2712d0-aon-pinctrl`); reg (maxItems 1).

## Control Flow
There is no imperative execution path in this YAML. Validation starts when dt-schema selects this
document for a node whose `compatible` value matches the schema, checks the required list, evaluates
referenced common pinctrl/GPIO schemas, applies property constraints, then walks child-node patterns
and conditional branches.

This file contains 2 `allOf`, 1 `oneOf`, 0 `anyOf`, and 1 `if` blocks. Property closure: top-level
`unevaluatedProperties: false` closes properties after referenced schemas are evaluated.

## State and Persistence Behavior
The binding stores no runtime state. It persists as source-controlled schema text, while the state
it describes persists in DTS/DTB data: register windows, GPIO provider cell counts, interrupt
wiring, pin groups, mux functions, drive strengths, pulls, and optional child pin configuration
nodes. Kernel drivers consume the validated DT data at boot or device probe and then program
hardware pin mux, pad, and GPIO state; this YAML only constrains that data before runtime.

## Dependencies and Integration Points
- Schema references: `pinctrl.yaml#`, `#/$defs/brcmstb-pinctrl-state`, `pincfg-node.yaml#`, `pinmux-node.yaml#`.
- Textual schema references: `/schemas/pinctrl/brcm,bcm2712c0-pinctrl.yaml#`.
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
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/brcm,bcm2712c0-pinctrl.yaml` to parse this YAML, validate meta-schema rules, and compile its 1 inline example(s).
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/brcm,bcm2712c0-pinctrl.yaml` on affected board DTS files to confirm real nodes satisfy required properties, compatible choices, child node names, and referenced common schemas.
- Useful negative tests remove one required property, change `compatible`, and add an undeclared property where closure is enabled. Example seed: pinctrl@7d504100 {; compatible = "brcm,bcm2712c0-pinctrl";; reg = <0x7d504100 0x30>;; bt-shutdown-default-state {.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/brcm,bcm2712c0-pinctrl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/brcm,bcm2835-gpio.yaml -->
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

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/brcm,bcm2835-gpio.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/brcm,bcm4908-pinctrl.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/brcm,bcm4908-pinctrl.yaml

## Purpose
This file is a Linux Devicetree JSON-schema document for a pin controller binding: Broadcom BCM4908
pin controller. It lives in the pinctrl binding tree and gives dt-schema a machine-readable contract
for board DTS nodes before the kernel pinctrl/GPIO drivers consume those nodes during probe.

Binding for pin controller present on BCM4908 family SoCs.

The binding is maintained in-source by Rafał Miłecki <rafal@milecki.pl>.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/pinctrl/brcm,bcm4908-pinctrl.yaml#` with meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Compatible contract: `brcm,bcm4908-pinctrl`.
- Required properties: `compatible`, `reg`.
- Top-level framework properties: `compatible`, `reg`.
- Vendor or device-specific extensions: none declared.
- Other declared top-level properties: none declared.
- Child-node or reusable schema API: patternProperties `-pins$`.
- Property detail signals: compatible (const `brcm,bcm4908-pinctrl`); reg (maxItems 1).

## Control Flow
There is no imperative execution path in this YAML. Validation starts when dt-schema selects this
document for a node whose `compatible` value matches the schema, checks the required list, evaluates
referenced common pinctrl/GPIO schemas, applies property constraints, then walks child-node patterns
and conditional branches.

This file contains 1 `allOf`, 0 `oneOf`, 0 `anyOf`, and 0 `if` blocks. Property closure: top-level
`unevaluatedProperties: false` closes properties after referenced schemas are evaluated.

## State and Persistence Behavior
The binding stores no runtime state. It persists as source-controlled schema text, while the state
it describes persists in DTS/DTB data: register windows, GPIO provider cell counts, interrupt
wiring, pin groups, mux functions, drive strengths, pulls, and optional child pin configuration
nodes. Kernel drivers consume the validated DT data at boot or device probe and then program
hardware pin mux, pad, and GPIO state; this YAML only constrains that data before runtime.

## Dependencies and Integration Points
- Schema references: `pinmux-node.yaml#`, `pinctrl.yaml#`.
- Textual schema references: `/schemas/pinctrl/brcm,bcm4908-pinctrl.yaml#`.
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
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/brcm,bcm4908-pinctrl.yaml` to parse this YAML, validate meta-schema rules, and compile its 1 inline example(s).
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/brcm,bcm4908-pinctrl.yaml` on affected board DTS files to confirm real nodes satisfy required properties, compatible choices, child node names, and referenced common schemas.
- Useful negative tests remove one required property, change `compatible`, and add an undeclared property where closure is enabled. Example seed: pinctrl@ff800560 {; compatible = "brcm,bcm4908-pinctrl";; reg = <0xff800560 0x10>;; led_0-a-pins {.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/brcm,bcm4908-pinctrl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/brcm,bcm6318-pinctrl.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/brcm,bcm6318-pinctrl.yaml

## Purpose
This file is a Linux Devicetree JSON-schema document for a pin controller binding: Broadcom BCM6318
pin controller. It lives in the pinctrl binding tree and gives dt-schema a machine-readable contract
for board DTS nodes before the kernel pinctrl/GPIO drivers consume those nodes during probe.

Bindings for Broadcom's BCM6318 memory-mapped pin controller.

The binding is maintained in-source by Álvaro Fernández Rojas <noltari@gmail.com>, Jonas Gorski
<jonas.gorski@gmail.com>.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/pinctrl/brcm,bcm6318-pinctrl.yaml#` with meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Compatible contract: `brcm,bcm6318-pinctrl`.
- Required properties: `compatible`, `reg`.
- Top-level framework properties: `compatible`, `reg`.
- Vendor or device-specific extensions: none declared.
- Other declared top-level properties: none declared.
- Child-node or reusable schema API: patternProperties `-pins$`.
- Property detail signals: compatible (const `brcm,bcm6318-pinctrl`); reg (maxItems 2).

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
- Schema references: `pinmux-node.yaml#`, `#/patternProperties/-pins$`, `pinctrl.yaml#`.
- Textual schema references: `/schemas/pinctrl/brcm,bcm6318-pinctrl.yaml#`.
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
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/brcm,bcm6318-pinctrl.yaml` to parse this YAML, validate meta-schema rules, and compile its 1 inline example(s).
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/brcm,bcm6318-pinctrl.yaml` on affected board DTS files to confirm real nodes satisfy required properties, compatible choices, child node names, and referenced common schemas.
- Useful negative tests remove one required property, change `compatible`, and add an undeclared property where closure is enabled. Example seed: pinctrl@18 {; compatible = "brcm,bcm6318-pinctrl";; reg = <0x18 0x10>, <0x54 0x18>;; pinctrl_ephy0_spd_led: ephy0_spd_led-pins {.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/brcm,bcm6318-pinctrl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/brcm,bcm63268-pinctrl.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/brcm,bcm63268-pinctrl.yaml

## Purpose
This file is a Linux Devicetree JSON-schema document for a pin controller binding: Broadcom BCM63268
pin controller. It lives in the pinctrl binding tree and gives dt-schema a machine-readable contract
for board DTS nodes before the kernel pinctrl/GPIO drivers consume those nodes during probe.

Bindings for Broadcom's BCM63268 memory-mapped pin controller.

The binding is maintained in-source by Álvaro Fernández Rojas <noltari@gmail.com>, Jonas Gorski
<jonas.gorski@gmail.com>.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/pinctrl/brcm,bcm63268-pinctrl.yaml#` with meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Compatible contract: `brcm,bcm63268-pinctrl`.
- Required properties: `compatible`, `reg`.
- Top-level framework properties: `compatible`, `reg`.
- Vendor or device-specific extensions: none declared.
- Other declared top-level properties: none declared.
- Child-node or reusable schema API: patternProperties `-pins$`.
- Property detail signals: compatible (const `brcm,bcm63268-pinctrl`); reg (maxItems 3).

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
- Schema references: `pinmux-node.yaml#`, `#/patternProperties/-pins$`, `pinctrl.yaml#`.
- Textual schema references: `/schemas/pinctrl/brcm,bcm63268-pinctrl.yaml#`.
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
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/brcm,bcm63268-pinctrl.yaml` to parse this YAML, validate meta-schema rules, and compile its 1 inline example(s).
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/brcm,bcm63268-pinctrl.yaml` on affected board DTS files to confirm real nodes satisfy required properties, compatible choices, child node names, and referenced common schemas.
- Useful negative tests remove one required property, change `compatible`, and add an undeclared property where closure is enabled. Example seed: pinctrl@10 {; compatible = "brcm,bcm63268-pinctrl";; reg = <0x10 0x4>, <0x18 0x8>, <0x38 0x4>;; pinctrl_serial_led: serial_led-pins {.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/brcm,bcm63268-pinctrl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/brcm,bcm6328-pinctrl.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/brcm,bcm6328-pinctrl.yaml

## Purpose
This file is a Linux Devicetree JSON-schema document for a pin controller binding: Broadcom BCM6328
pin controller. It lives in the pinctrl binding tree and gives dt-schema a machine-readable contract
for board DTS nodes before the kernel pinctrl/GPIO drivers consume those nodes during probe.

Bindings for Broadcom's BCM6328 memory-mapped pin controller.

The binding is maintained in-source by Álvaro Fernández Rojas <noltari@gmail.com>, Jonas Gorski
<jonas.gorski@gmail.com>.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/pinctrl/brcm,bcm6328-pinctrl.yaml#` with meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Compatible contract: `brcm,bcm6328-pinctrl`.
- Required properties: `compatible`, `reg`.
- Top-level framework properties: `compatible`, `reg`.
- Vendor or device-specific extensions: none declared.
- Other declared top-level properties: none declared.
- Child-node or reusable schema API: patternProperties `-pins$`.
- Property detail signals: compatible (const `brcm,bcm6328-pinctrl`); reg (maxItems 1).

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
- Schema references: `pinmux-node.yaml#`, `#/patternProperties/-pins$`, `pinctrl.yaml#`.
- Textual schema references: `/schemas/pinctrl/brcm,bcm6328-pinctrl.yaml#`.
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
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/brcm,bcm6328-pinctrl.yaml` to parse this YAML, validate meta-schema rules, and compile its 1 inline example(s).
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/brcm,bcm6328-pinctrl.yaml` on affected board DTS files to confirm real nodes satisfy required properties, compatible choices, child node names, and referenced common schemas.
- Useful negative tests remove one required property, change `compatible`, and add an undeclared property where closure is enabled. Example seed: pinctrl@18 {; compatible = "brcm,bcm6328-pinctrl";; reg = <0x18 0x10>;; pinctrl_serial_led: serial_led-pins {.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/brcm,bcm6328-pinctrl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/brcm,bcm6358-pinctrl.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/brcm,bcm6358-pinctrl.yaml

## Purpose
This file is a Linux Devicetree JSON-schema document for a pin controller binding: Broadcom BCM6358
pin controller. It lives in the pinctrl binding tree and gives dt-schema a machine-readable contract
for board DTS nodes before the kernel pinctrl/GPIO drivers consume those nodes during probe.

Bindings for Broadcom's BCM6358 memory-mapped pin controller.

The binding is maintained in-source by Álvaro Fernández Rojas <noltari@gmail.com>, Jonas Gorski
<jonas.gorski@gmail.com>.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/pinctrl/brcm,bcm6358-pinctrl.yaml#` with meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Compatible contract: `brcm,bcm6358-pinctrl`.
- Required properties: `compatible`, `reg`.
- Top-level framework properties: `compatible`, `reg`.
- Vendor or device-specific extensions: none declared.
- Other declared top-level properties: none declared.
- Child-node or reusable schema API: patternProperties `-pins$`.
- Property detail signals: compatible (const `brcm,bcm6358-pinctrl`); reg (maxItems 1).

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
- Schema references: `pinmux-node.yaml#`, `pinctrl.yaml#`.
- Textual schema references: `/schemas/pinctrl/brcm,bcm6358-pinctrl.yaml#`.
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
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/brcm,bcm6358-pinctrl.yaml` to parse this YAML, validate meta-schema rules, and compile its 1 inline example(s).
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/brcm,bcm6358-pinctrl.yaml` on affected board DTS files to confirm real nodes satisfy required properties, compatible choices, child node names, and referenced common schemas.
- Useful negative tests remove one required property, change `compatible`, and add an undeclared property where closure is enabled. Example seed: pinctrl@18 {; compatible = "brcm,bcm6358-pinctrl";; reg = <0x18 0x4>;; pinctrl_ebi_cs: ebi_cs-pins {.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/brcm,bcm6358-pinctrl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/brcm,bcm6362-pinctrl.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/brcm,bcm6362-pinctrl.yaml

## Purpose
This file is a Linux Devicetree JSON-schema document for a pin controller binding: Broadcom BCM6362
pin controller. It lives in the pinctrl binding tree and gives dt-schema a machine-readable contract
for board DTS nodes before the kernel pinctrl/GPIO drivers consume those nodes during probe.

Bindings for Broadcom's BCM6362 memory-mapped pin controller.

The binding is maintained in-source by Álvaro Fernández Rojas <noltari@gmail.com>, Jonas Gorski
<jonas.gorski@gmail.com>.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/pinctrl/brcm,bcm6362-pinctrl.yaml#` with meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Compatible contract: `brcm,bcm6362-pinctrl`.
- Required properties: `compatible`, `reg`.
- Top-level framework properties: `compatible`, `reg`.
- Vendor or device-specific extensions: none declared.
- Other declared top-level properties: none declared.
- Child-node or reusable schema API: patternProperties `-pins$`.
- Property detail signals: compatible (const `brcm,bcm6362-pinctrl`); reg (maxItems 2).

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
- Schema references: `pinmux-node.yaml#`, `#/patternProperties/-pins$`, `pinctrl.yaml#`.
- Textual schema references: `/schemas/pinctrl/brcm,bcm6362-pinctrl.yaml#`.
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
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/brcm,bcm6362-pinctrl.yaml` to parse this YAML, validate meta-schema rules, and compile its 1 inline example(s).
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/brcm,bcm6362-pinctrl.yaml` on affected board DTS files to confirm real nodes satisfy required properties, compatible choices, child node names, and referenced common schemas.
- Useful negative tests remove one required property, change `compatible`, and add an undeclared property where closure is enabled. Example seed: pinctrl@18 {; compatible = "brcm,bcm6362-pinctrl";; reg = <0x18 0x10>, <0x38 0x4>;; pinctrl_usb_device_led: usb_device_led-pins {.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/brcm,bcm6362-pinctrl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/brcm,bcm6368-pinctrl.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/brcm,bcm6368-pinctrl.yaml

## Purpose
This file is a Linux Devicetree JSON-schema document for a pin controller binding: Broadcom BCM6368
pin controller. It lives in the pinctrl binding tree and gives dt-schema a machine-readable contract
for board DTS nodes before the kernel pinctrl/GPIO drivers consume those nodes during probe.

Bindings for Broadcom's BCM6368 memory-mapped pin controller.

The binding is maintained in-source by Álvaro Fernández Rojas <noltari@gmail.com>, Jonas Gorski
<jonas.gorski@gmail.com>.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/pinctrl/brcm,bcm6368-pinctrl.yaml#` with meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Compatible contract: `brcm,bcm6368-pinctrl`.
- Required properties: `compatible`, `reg`.
- Top-level framework properties: `compatible`, `reg`.
- Vendor or device-specific extensions: none declared.
- Other declared top-level properties: none declared.
- Child-node or reusable schema API: patternProperties `-pins$`.
- Property detail signals: compatible (const `brcm,bcm6368-pinctrl`); reg (maxItems 2).

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
- Schema references: `pinmux-node.yaml#`, `#/patternProperties/-pins$`, `pinctrl.yaml#`.
- Textual schema references: `/schemas/pinctrl/brcm,bcm6368-pinctrl.yaml#`.
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
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/brcm,bcm6368-pinctrl.yaml` to parse this YAML, validate meta-schema rules, and compile its 1 inline example(s).
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/brcm,bcm6368-pinctrl.yaml` on affected board DTS files to confirm real nodes satisfy required properties, compatible choices, child node names, and referenced common schemas.
- Useful negative tests remove one required property, change `compatible`, and add an undeclared property where closure is enabled. Example seed: pinctrl@18 {; compatible = "brcm,bcm6368-pinctrl";; reg = <0x18 0x4>, <0x38 0x4>;; pinctrl_analog_afe_0: analog_afe_0-pins {.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/brcm,bcm6368-pinctrl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/brcm,iproc-gpio.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/brcm,iproc-gpio.yaml

## Purpose
This file is a Linux Devicetree JSON-schema document for a pin controller binding: Broadcom iProc
GPIO/PINCONF Controller. It lives in the pinctrl binding tree and gives dt-schema a machine-readable
contract for board DTS nodes before the kernel pinctrl/GPIO drivers consume those nodes during
probe.

The schema relies on title, compatible values, and property constraints rather than a long description block.

The binding is maintained in-source by Ray Jui <rjui@broadcom.com>, Scott Branden
<sbranden@broadcom.com>.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/pinctrl/brcm,iproc-gpio.yaml#` with meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Compatible contract: `brcm,cygnus-asiu-gpio`, `brcm,cygnus-ccm-gpio`, `brcm,cygnus-crmu-gpio`, `brcm,iproc-gpio`, `brcm,iproc-stingray-gpio`, `brcm,iproc-hr2-gpio`, `brcm,iproc-nsp-gpio`.
- Required properties: `compatible`, `reg`, `#gpio-cells`, `gpio-controller`, `ngpios`.
- Top-level framework properties: `compatible`, `reg`, `#gpio-cells`, `gpio-controller`, `gpio-ranges`, `#interrupt-cells`, `interrupts`, `interrupt-controller`.
- Vendor or device-specific extensions: none declared.
- Other declared top-level properties: `ngpios`.
- Child-node or reusable schema API: patternProperties `-pins$`.
- Property detail signals: compatible; reg (minItems 1); #gpio-cells (const `2`); gpio-controller; gpio-ranges; ngpios; #interrupt-cells (const `2`); interrupts (maxItems 1); interrupt-controller.

## Control Flow
There is no imperative execution path in this YAML. Validation starts when dt-schema selects this
document for a node whose `compatible` value matches the schema, checks the required list, evaluates
referenced common pinctrl/GPIO schemas, applies property constraints, then walks child-node patterns
and conditional branches.

This file contains 1 `allOf`, 1 `oneOf`, 0 `anyOf`, and 0 `if` blocks. Property closure: top-level
`additionalProperties: false` rejects undeclared properties.

## State and Persistence Behavior
The binding stores no runtime state. It persists as source-controlled schema text, while the state
it describes persists in DTS/DTB data: register windows, GPIO provider cell counts, interrupt
wiring, pin groups, mux functions, drive strengths, pulls, and optional child pin configuration
nodes. Kernel drivers consume the validated DT data at boot or device probe and then program
hardware pin mux, pad, and GPIO state; this YAML only constrains that data before runtime.

## Dependencies and Integration Points
- Schema references: `pincfg-node.yaml#`, `pinmux-node.yaml#`.
- Example/header integration: `dt-bindings/interrupt-controller/arm-gic.h`.
- Textual schema references: `/schemas/pinctrl/brcm,iproc-gpio.yaml#`.
Runtime integration is with Linux pinctrl and GPIO framework drivers selected by `compatible`. Board
`.dts` files instantiate nodes that satisfy this schema; `make dt_binding_check` validates the
binding and inline examples, while `make dtbs_check` validates real board descriptions against the
same contract.

## Risks
- A missing or misspelled `compatible` value prevents both schema matching and driver binding.
- Omitting required fields such as `compatible`, `reg`, `#gpio-cells`, `gpio-controller`, `ngpios` should fail dt-schema validation before boot.
- Child node regexes and reusable pin configuration schemas are easy to misuse; incorrect group/function names can validate poorly or fail later in driver lookup tables.
- The closed property model catches typos, but any newly needed board property requires a binding update before DTS changes can pass validation.
- GPIO provider fields such as `#gpio-cells`, `gpio-ranges`, and interrupt controller wiring must match the runtime driver's expectations or GPIO consumers will resolve the wrong pins.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/brcm,iproc-gpio.yaml` to parse this YAML, validate meta-schema rules, and compile its 1 inline example(s).
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/brcm,iproc-gpio.yaml` on affected board DTS files to confirm real nodes satisfy required properties, compatible choices, child node names, and referenced common schemas.
- Useful negative tests remove one required property, change `compatible`, and add an undeclared property where closure is enabled. Example seed: #include <dt-bindings/interrupt-controller/arm-gic.h>; gpio@1800a000 {; compatible = "brcm,cygnus-ccm-gpio";; reg = <0x1800a000 0x50>,.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/brcm,iproc-gpio.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/brcm,ns-pinmux.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/brcm,ns-pinmux.yaml

## Purpose
This file is a Linux Devicetree JSON-schema document for a pin multiplexing controller binding:
Broadcom Northstar pins mux controller. It lives in the pinctrl binding tree and gives dt-schema a
machine-readable contract for board DTS nodes before the kernel pinctrl/GPIO drivers consume those
nodes during probe.

Some of Northstar SoCs's pins can be used for various purposes thanks to the mux controller. This
binding allows describing mux controller and listing available functions. They can be referenced
later by other bindings to let system configure controller correctly. A list of pins varies across
chipsets so few bindings are available.

The binding is maintained in-source by Rafał Miłecki <rafal@milecki.pl>.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/pinctrl/brcm,ns-pinmux.yaml#` with meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Compatible contract: `brcm,bcm4708-pinmux`, `brcm,bcm4709-pinmux`, `brcm,bcm53012-pinmux`.
- Required properties: `reg`, `reg-names`.
- Top-level framework properties: `compatible`, `reg`, `reg-names`.
- Vendor or device-specific extensions: none declared.
- Other declared top-level properties: none declared.
- Child-node or reusable schema API: patternProperties `-pins$`.
- Property detail signals: compatible (enum `brcm,bcm4708-pinmux`, `brcm,bcm4709-pinmux`, `brcm,bcm53012-pinmux`); reg (maxItems 1); reg-names (const `cru_gpio_control`).

## Control Flow
There is no imperative execution path in this YAML. Validation starts when dt-schema selects this
document for a node whose `compatible` value matches the schema, checks the required list, evaluates
referenced common pinctrl/GPIO schemas, applies property constraints, then walks child-node patterns
and conditional branches.

This file contains 1 `allOf`, 0 `oneOf`, 0 `anyOf`, and 1 `if` blocks. Property closure: top-level
`additionalProperties: false` rejects undeclared properties.

## State and Persistence Behavior
The binding stores no runtime state. It persists as source-controlled schema text, while the state
it describes persists in DTS/DTB data: register windows, GPIO provider cell counts, interrupt
wiring, pin groups, mux functions, drive strengths, pulls, and optional child pin configuration
nodes. Kernel drivers consume the validated DT data at boot or device probe and then program
hardware pin mux, pad, and GPIO state; this YAML only constrains that data before runtime.

## Dependencies and Integration Points
- Schema references: `pinmux-node.yaml#`, `pinctrl.yaml#`.
- Textual schema references: `/schemas/pinctrl/brcm,ns-pinmux.yaml#`.
Runtime integration is with Linux pinctrl and GPIO framework drivers selected by `compatible`. Board
`.dts` files instantiate nodes that satisfy this schema; `make dt_binding_check` validates the
binding and inline examples, while `make dtbs_check` validates real board descriptions against the
same contract.

## Risks
- A missing or misspelled `compatible` value prevents both schema matching and driver binding.
- Omitting required fields such as `reg`, `reg-names` should fail dt-schema validation before boot.
- Child node regexes and reusable pin configuration schemas are easy to misuse; incorrect group/function names can validate poorly or fail later in driver lookup tables.
- The closed property model catches typos, but any newly needed board property requires a binding update before DTS changes can pass validation.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/brcm,ns-pinmux.yaml` to parse this YAML, validate meta-schema rules, and compile its 1 inline example(s).
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/brcm,ns-pinmux.yaml` on affected board DTS files to confirm real nodes satisfy required properties, compatible choices, child node names, and referenced common schemas.
- Useful negative tests remove one required property, change `compatible`, and add an undeclared property where closure is enabled. Example seed: pinctrl@1800c1c0 {; compatible = "brcm,bcm4708-pinmux";; reg = <0x1800c1c0 0x24>;; reg-names = "cru_gpio_control";.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/brcm,ns-pinmux.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/brcm,ns2-pinmux.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/brcm,ns2-pinmux.yaml

## Purpose
This file is a Linux Devicetree JSON-schema document for a pin multiplexing controller binding:
Broadcom Northstar2 IOMUX Controller. It lives in the pinctrl binding tree and gives dt-schema a
machine-readable contract for board DTS nodes before the kernel pinctrl/GPIO drivers consume those
nodes during probe.

The schema relies on title, compatible values, and property constraints rather than a long description block.

The binding is maintained in-source by Ray Jui <rjui@broadcom.com>, Scott Branden
<sbranden@broadcom.com>.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/pinctrl/brcm,ns2-pinmux.yaml#` with meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Compatible contract: `brcm,ns2-pinmux`.
- Required properties: `compatible`, `reg`.
- Top-level framework properties: `compatible`, `reg`.
- Vendor or device-specific extensions: none declared.
- Other declared top-level properties: none declared.
- Child-node or reusable schema API: no named child-node API or pattern child-node contract is declared.
- Property detail signals: compatible (const `brcm,ns2-pinmux`); reg (maxItems 3).

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
- Schema references: `/schemas/pinctrl/pincfg-node.yaml#`, `/schemas/pinctrl/pinmux-node.yaml#`, `/schemas/types.yaml#/definitions/string`.
- Textual schema references: `/schemas/pinctrl/brcm,ns2-pinmux.yaml#`, `/schemas/pinctrl/pincfg-node.yaml#`, `/schemas/pinctrl/pinmux-node.yaml#`, `/schemas/types.yaml#/definitions/string`.
Runtime integration is with Linux pinctrl and GPIO framework drivers selected by `compatible`. Board
`.dts` files instantiate nodes that satisfy this schema; `make dt_binding_check` validates the
binding and inline examples, while `make dtbs_check` validates real board descriptions against the
same contract.

## Risks
- A missing or misspelled `compatible` value prevents both schema matching and driver binding.
- Omitting required fields such as `compatible`, `reg` should fail dt-schema validation before boot.
- Open or partially open property handling can let board-specific typos escape schema validation and surface only at driver probe time.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/brcm,ns2-pinmux.yaml` to parse this YAML, validate meta-schema rules, and compile its 1 inline example(s).
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/brcm,ns2-pinmux.yaml` on affected board DTS files to confirm real nodes satisfy required properties, compatible choices, child node names, and referenced common schemas.
- Useful negative tests remove one required property, change `compatible`, and add an undeclared property where closure is enabled. Example seed: pinctrl@6501d130 {; compatible = "brcm,ns2-pinmux";; reg = <0x6501d130 0x08>,; <0x660a0028 0x04>,; <0x660009b0 0x40>;.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/brcm,ns2-pinmux.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/canaan,k210-fpioa.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/canaan,k210-fpioa.yaml

## Purpose
This file is a Linux Devicetree JSON-schema document for a field programmable IO array binding:
Canaan Kendryte K210 FPIOA. It lives in the pinctrl binding tree and gives dt-schema a machine-
readable contract for board DTS nodes before the kernel pinctrl/GPIO drivers consume those nodes
during probe.

The Canaan Kendryte K210 SoC Fully Programmable IO Array (FPIOA) controller allows assigning any of
256 possible functions to any of 48 IO pins of the SoC. Pin function configuration is performed on a
per-pin basis.

The binding is maintained in-source by Damien Le Moal <dlemoal@kernel.org>.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/pinctrl/canaan,k210-fpioa.yaml#` with meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Compatible contract: `canaan,k210-fpioa`.
- Required properties: `compatible`, `reg`, `clocks`, `canaan,k210-sysctl-power`.
- Top-level framework properties: `compatible`, `reg`, `clocks`, `clock-names`, `resets`.
- Vendor or device-specific extensions: `canaan,k210-sysctl-power`.
- Other declared top-level properties: none declared.
- Child-node or reusable schema API: patternProperties `-pinmux$`, `-pins$`.
- Property detail signals: compatible (const `canaan,k210-fpioa`); reg (maxItems 1; Address and length of the register set for the FPIOA controller.); clocks; clock-names; resets (maxItems 1); canaan,k210-sysctl-power (phandle of the K210 system controller node and offset of its power domain control register.; ref `/schemas/types.yaml#/definitions/phandle-array`).

## Control Flow
There is no imperative execution path in this YAML. Validation starts when dt-schema selects this
document for a node whose `compatible` value matches the schema, checks the required list, evaluates
referenced common pinctrl/GPIO schemas, applies property constraints, then walks child-node patterns
and conditional branches.

This file contains 1 `allOf`, 0 `oneOf`, 1 `anyOf`, and 0 `if` blocks. Property closure: top-level
`additionalProperties: false` rejects undeclared properties.

## State and Persistence Behavior
The binding stores no runtime state. It persists as source-controlled schema text, while the state
it describes persists in DTS/DTB data: register windows, GPIO provider cell counts, interrupt
wiring, pin groups, mux functions, drive strengths, pulls, and optional child pin configuration
nodes. Kernel drivers consume the validated DT data at boot or device probe and then program
hardware pin mux, pad, and GPIO state; this YAML only constrains that data before runtime.

## Dependencies and Integration Points
- Schema references: `/schemas/types.yaml#/definitions/phandle-array`, `/schemas/pinctrl/pinmux-node.yaml`, `/schemas/pinctrl/pincfg-node.yaml`, `pinctrl.yaml#`.
- Example/header integration: `dt-bindings/pinctrl/k210-fpioa.h`, `dt-bindings/clock/k210-clk.h`, `dt-bindings/reset/k210-rst.h`.
- Textual schema references: `/schemas/pinctrl/canaan,k210-fpioa.yaml#`, `/schemas/types.yaml#/definitions/phandle-array`, `/schemas/pinctrl/pinmux-node.yaml`, `/schemas/pinctrl/pincfg-node.yaml`.
Runtime integration is with Linux pinctrl and GPIO framework drivers selected by `compatible`. Board
`.dts` files instantiate nodes that satisfy this schema; `make dt_binding_check` validates the
binding and inline examples, while `make dtbs_check` validates real board descriptions against the
same contract.

## Risks
- A missing or misspelled `compatible` value prevents both schema matching and driver binding.
- Omitting required fields such as `compatible`, `reg`, `clocks`, `canaan,k210-sysctl-power` should fail dt-schema validation before boot.
- Child node regexes and reusable pin configuration schemas are easy to misuse; incorrect group/function names can validate poorly or fail later in driver lookup tables.
- The closed property model catches typos, but any newly needed board property requires a binding update before DTS changes can pass validation.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/canaan,k210-fpioa.yaml` to parse this YAML, validate meta-schema rules, and compile its 1 inline example(s).
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/canaan,k210-fpioa.yaml` on affected board DTS files to confirm real nodes satisfy required properties, compatible choices, child node names, and referenced common schemas.
- Useful negative tests remove one required property, change `compatible`, and add an undeclared property where closure is enabled. Example seed: #include <dt-bindings/pinctrl/k210-fpioa.h>; #include <dt-bindings/clock/k210-clk.h>; #include <dt-bindings/reset/k210-rst.h>; fpioa: pinmux@502b0000 {.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/canaan,k210-fpioa.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/canaan,k230-pinctrl.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/canaan,k230-pinctrl.yaml

## Purpose
This file is a Linux Devicetree JSON-schema document for a pin controller binding: Canaan Kendryte
K230 Pin Controller. It lives in the pinctrl binding tree and gives dt-schema a machine-readable
contract for board DTS nodes before the kernel pinctrl/GPIO drivers consume those nodes during
probe.

The Canaan Kendryte K230 platform includes 64 IO pins, each capable of multiplexing up to 5
different functions. Pin function configuration is performed on a per-pin basis.

The binding is maintained in-source by Ze Huang <18771902331@163.com>.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/pinctrl/canaan,k230-pinctrl.yaml#` with meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Compatible contract: `canaan,k230-pinctrl`.
- Required properties: `compatible`, `reg`.
- Top-level framework properties: `compatible`, `reg`.
- Vendor or device-specific extensions: none declared.
- Other declared top-level properties: none declared.
- Child-node or reusable schema API: patternProperties `-pins$`.
- Property detail signals: compatible (const `canaan,k230-pinctrl`); reg (maxItems 1).

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
- Schema references: `/schemas/pinctrl/pincfg-node.yaml`, `/schemas/pinctrl/pinmux-node.yaml`.
- Textual schema references: `/schemas/pinctrl/canaan,k230-pinctrl.yaml#`, `/schemas/pinctrl/pincfg-node.yaml`, `/schemas/pinctrl/pinmux-node.yaml`.
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
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/canaan,k230-pinctrl.yaml` to parse this YAML, validate meta-schema rules, and compile its 1 inline example(s).
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/canaan,k230-pinctrl.yaml` on affected board DTS files to confirm real nodes satisfy required properties, compatible choices, child node names, and referenced common schemas.
- Useful negative tests remove one required property, change `compatible`, and add an undeclared property where closure is enabled. Example seed: pinctrl@91105000 {; compatible = "canaan,k230-pinctrl";; reg = <0x91105000 0x100>;; uart2-pins {.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/canaan,k230-pinctrl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/cirrus,lochnagar.yaml -->
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

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/cirrus,lochnagar.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/cirrus,madera.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/cirrus,madera.yaml

## Purpose
This file is a Linux Devicetree JSON-schema document for a pin controller binding: Cirrus Logic
Madera class audio CODECs pinctrl driver. It lives in the pinctrl binding tree and gives dt-schema a
machine-readable contract for board DTS nodes before the kernel pinctrl/GPIO drivers consume those
nodes during probe.

The Cirrus Logic Madera codecs provide a number of GPIO functions for interfacing to external
hardware and to provide logic outputs to other devices. Certain groups of GPIO pins also have an
alternate function, normally as an audio interface. The set of available GPIOs, functions and
alternate function groups differs between CODECs so refer to the datasheet for the CODEC for further
information on what is supported on that device. The properties for this driver exist within the
parent MFD driver node. See also the core bindings for the parent MFD driver:
Documentation/devicetree/bindings/mfd/cirrus,madera.yaml And the generic pinmix bindings:
Documentation/devicetree/bindings/pinctrl/pinctrl-bindings.txt

The binding is maintained in-source by patches@opensource.cirrus.com.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/pinctrl/cirrus,madera.yaml#` with meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Compatible contract: none declared.
- Required properties: `pinctrl-0`, `pinctrl-names`.
- Top-level framework properties: none declared.
- Vendor or device-specific extensions: none declared.
- Other declared top-level properties: `pin-settings`.
- Child-node or reusable schema API: object-valued child/property schemas `pin-settings`.
- Property detail signals: pin-settings (One subnode is required to contain the default settings. It contains an arbitrary number of confi...).

## Control Flow
There is no imperative execution path in this YAML. Validation starts when dt-schema selects this
document for a node whose `compatible` value matches the schema, checks the required list, evaluates
referenced common pinctrl/GPIO schemas, applies property constraints, then walks child-node patterns
and conditional branches.

This file contains 1 `allOf`, 0 `oneOf`, 0 `anyOf`, and 0 `if` blocks. Property closure: top-level
`additionalProperties: true` allows extensions beyond declared keys.

## State and Persistence Behavior
The binding stores no runtime state. It persists as source-controlled schema text, while the state
it describes persists in DTS/DTB data: register windows, GPIO provider cell counts, interrupt
wiring, pin groups, mux functions, drive strengths, pulls, and optional child pin configuration
nodes. Kernel drivers consume the validated DT data at boot or device probe and then program
hardware pin mux, pad, and GPIO state; this YAML only constrains that data before runtime.

## Dependencies and Integration Points
- Schema references: `pincfg-node.yaml#`, `pinmux-node.yaml#`.
- Textual schema references: `/schemas/pinctrl/cirrus,madera.yaml#`.
Runtime integration is with Linux pinctrl and GPIO framework drivers selected by `compatible`. Board
`.dts` files instantiate nodes that satisfy this schema; `make dt_binding_check` validates the
binding and inline examples, while `make dtbs_check` validates real board descriptions against the
same contract.

## Risks
- A missing or misspelled `compatible` value prevents both schema matching and driver binding.
- Omitting required fields such as `pinctrl-0`, `pinctrl-names` should fail dt-schema validation before boot.
- Child node regexes and reusable pin configuration schemas are easy to misuse; incorrect group/function names can validate poorly or fail later in driver lookup tables.
- Open or partially open property handling can let board-specific typos escape schema validation and surface only at driver probe time.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/cirrus,madera.yaml` to parse this YAML, validate meta-schema rules, and compile its 0 inline example(s).
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/cirrus,madera.yaml` on affected board DTS files to confirm real nodes satisfy required properties, compatible choices, child node names, and referenced common schemas.
- Useful negative tests remove one required property, change `compatible`, add a bogus pin group/function, and add an undeclared property where closure is enabled.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/cirrus,madera.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/cix,sky1-pinctrl.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/cix,sky1-pinctrl.yaml

## Purpose
This file is a Linux Devicetree JSON-schema document for a pin controller binding: Cix Sky1 Soc Pin
Controller. It lives in the pinctrl binding tree and gives dt-schema a machine-readable contract for
board DTS nodes before the kernel pinctrl/GPIO drivers consume those nodes during probe.

The pin-controller is used to control Soc pins. There are two pin-controllers on Cix Sky1 platform.
one is used under S0 state, the other one is used under S0 and S5 state.

The binding is maintained in-source by Gary Yang <gary.yang@cixtech.com>.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/pinctrl/cix,sky1-pinctrl.yaml#` with meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Compatible contract: `cix,sky1-pinctrl`, `cix,sky1-pinctrl-s5`.
- Required properties: `compatible`, `reg`.
- Top-level framework properties: `compatible`, `reg`.
- Vendor or device-specific extensions: none declared.
- Other declared top-level properties: none declared.
- Child-node or reusable schema API: patternProperties `-cfg$`.
- Property detail signals: compatible (enum `cix,sky1-pinctrl`, `cix,sky1-pinctrl-s5`); reg.

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
- Schema references: `pincfg-node.yaml#`, `pinmux-node.yaml#`.
- Textual schema references: `/schemas/pinctrl/cix,sky1-pinctrl.yaml#`.
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
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/cix,sky1-pinctrl.yaml` to parse this YAML, validate meta-schema rules, and compile its 1 inline example(s).
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/cix,sky1-pinctrl.yaml` on affected board DTS files to confirm real nodes satisfy required properties, compatible choices, child node names, and referenced common schemas.
- Useful negative tests remove one required property, change `compatible`, and add an undeclared property where closure is enabled. Example seed: #define CIX_PAD_GPIO012_FUNC_GPIO012 (11 << 8 | 0x0); pinctrl@4170000 {; compatible = "cix,sky1-pinctrl";; reg = <0x4170000 0x1000>;.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/cix,sky1-pinctrl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/cypress,cy8c95x0.yaml -->
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

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/cypress,cy8c95x0.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/eswin,eic7700-pinctrl.yaml -->
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

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/eswin,eic7700-pinctrl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/fsl,imx27-iomuxc.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/fsl,imx27-iomuxc.yaml

## Purpose
This file is a Linux Devicetree JSON-schema document for a pin multiplexing controller binding:
Freescale i.MX1/i.MX25/i.MX27 IOMUX Controller. It lives in the pinctrl binding tree and gives dt-
schema a machine-readable contract for board DTS nodes before the kernel pinctrl/GPIO drivers
consume those nodes during probe.

Please refer to fsl,imx-pinctrl.txt and pinctrl-bindings.txt in this directory for common binding
part and usage.

The binding is maintained in-source by Frank Li <Frank.Li@nxp.com>.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/pinctrl/fsl,imx27-iomuxc.yaml#` with meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Compatible contract: `fsl,imx1-iomuxc`, `fsl,imx27-iomuxc`.
- Required properties: `compatible`, `reg`.
- Top-level framework properties: `compatible`, `reg`, `#address-cells`, `#size-cells`.
- Vendor or device-specific extensions: none declared.
- Other declared top-level properties: `ranges`.
- Child-node or reusable schema API: patternProperties `^gpio@[0-9a-f]+$`, `grp$`.
- Property detail signals: compatible (enum `fsl,imx1-iomuxc`, `fsl,imx27-iomuxc`); reg (maxItems 1); #address-cells (const `1`); #size-cells (const `1`); ranges.

## Control Flow
There is no imperative execution path in this YAML. Validation starts when dt-schema selects this
document for a node whose `compatible` value matches the schema, checks the required list, evaluates
referenced common pinctrl/GPIO schemas, applies property constraints, then walks child-node patterns
and conditional branches.

This file contains 1 `allOf`, 0 `oneOf`, 0 `anyOf`, and 0 `if` blocks. Property closure: top-level
`unevaluatedProperties: false` closes properties after referenced schemas are evaluated.

## State and Persistence Behavior
The binding stores no runtime state. It persists as source-controlled schema text, while the state
it describes persists in DTS/DTB data: register windows, GPIO provider cell counts, interrupt
wiring, pin groups, mux functions, drive strengths, pulls, and optional child pin configuration
nodes. Kernel drivers consume the validated DT data at boot or device probe and then program
hardware pin mux, pad, and GPIO state; this YAML only constrains that data before runtime.

## Dependencies and Integration Points
- Schema references: `/schemas/gpio/fsl-imx-gpio.yaml`, `/schemas/types.yaml#/definitions/uint32-matrix`, `pinctrl.yaml#`.
- Textual schema references: `/schemas/pinctrl/fsl,imx27-iomuxc.yaml#`, `/schemas/gpio/fsl-imx-gpio.yaml`, `/schemas/types.yaml#/definitions/uint32-matrix`.
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
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/fsl,imx27-iomuxc.yaml` to parse this YAML, validate meta-schema rules, and compile its 1 inline example(s).
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/fsl,imx27-iomuxc.yaml` on affected board DTS files to confirm real nodes satisfy required properties, compatible choices, child node names, and referenced common schemas.
- Useful negative tests remove one required property, change `compatible`, and add an undeclared property where closure is enabled. Example seed: pinmux@10015000 {; compatible = "fsl,imx27-iomuxc";; reg = <0x10015000 0x600>;; uartgrp {.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/fsl,imx27-iomuxc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/fsl,imx35-pinctrl.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/fsl,imx35-pinctrl.yaml

## Purpose
This file is a Linux Devicetree JSON-schema document for a pin multiplexing controller binding:
Freescale IMX35/IMX5x/IMX6 IOMUX Controller. It lives in the pinctrl binding tree and gives dt-
schema a machine-readable contract for board DTS nodes before the kernel pinctrl/GPIO drivers
consume those nodes during probe.

Please refer to fsl,imx-pinctrl.txt and pinctrl-bindings.txt in this directory for common binding
part and usage.

The binding is maintained in-source by Dong Aisheng <aisheng.dong@nxp.com>.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/pinctrl/fsl,imx35-pinctrl.yaml#` with meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Compatible contract: `fsl,imx25-iomuxc`, `fsl,imx35-iomuxc`, `fsl,imx51-iomuxc`, `fsl,imx53-iomuxc`, `fsl,imx6dl-iomuxc`, `fsl,imx6q-iomuxc`, `fsl,imx6sl-iomuxc`, `fsl,imx6sll-iomuxc`, `fsl,imx6sx-iomuxc`, `fsl,imx6ul-iomuxc`, `fsl,imx6ull-iomuxc-snvs`, `fsl,imx50-iomuxc`.
- Required properties: `compatible`, `reg`.
- Top-level framework properties: `compatible`, `reg`.
- Vendor or device-specific extensions: none declared.
- Other declared top-level properties: none declared.
- Child-node or reusable schema API: patternProperties `grp$`.
- Property detail signals: compatible; reg (maxItems 1).

## Control Flow
There is no imperative execution path in this YAML. Validation starts when dt-schema selects this
document for a node whose `compatible` value matches the schema, checks the required list, evaluates
referenced common pinctrl/GPIO schemas, applies property constraints, then walks child-node patterns
and conditional branches.

This file contains 1 `allOf`, 1 `oneOf`, 0 `anyOf`, and 0 `if` blocks. Property closure: top-level
`additionalProperties: false` rejects undeclared properties.

## State and Persistence Behavior
The binding stores no runtime state. It persists as source-controlled schema text, while the state
it describes persists in DTS/DTB data: register windows, GPIO provider cell counts, interrupt
wiring, pin groups, mux functions, drive strengths, pulls, and optional child pin configuration
nodes. Kernel drivers consume the validated DT data at boot or device probe and then program
hardware pin mux, pad, and GPIO state; this YAML only constrains that data before runtime.

## Dependencies and Integration Points
- Schema references: `pinctrl.yaml#`, `/schemas/types.yaml#/definitions/uint32-matrix`.
- Textual schema references: `/schemas/pinctrl/fsl,imx35-pinctrl.yaml#`, `/schemas/types.yaml#/definitions/uint32-matrix`.
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
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/fsl,imx35-pinctrl.yaml` to parse this YAML, validate meta-schema rules, and compile its 3 inline example(s).
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/fsl,imx35-pinctrl.yaml` on affected board DTS files to confirm real nodes satisfy required properties, compatible choices, child node names, and referenced common schemas.
- Useful negative tests remove one required property, change `compatible`, and add an undeclared property where closure is enabled. Example seed: iomuxc: pinctrl@20e0000 {; compatible = "fsl,imx6ul-iomuxc";; reg = <0x020e0000 0x4000>;; mux_uart: uartgrp {.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/fsl,imx35-pinctrl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/fsl,imx7d-pinctrl.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/fsl,imx7d-pinctrl.yaml

## Purpose
This file is a Linux Devicetree JSON-schema document for a pin multiplexing controller binding:
Freescale IMX7D IOMUX Controller. It lives in the pinctrl binding tree and gives dt-schema a
machine-readable contract for board DTS nodes before the kernel pinctrl/GPIO drivers consume those
nodes during probe.

Please refer to fsl,imx-pinctrl.txt and pinctrl-bindings.txt in this directory for common binding
part and usage.

The binding is maintained in-source by Dong Aisheng <aisheng.dong@nxp.com>.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/pinctrl/fsl,imx7d-pinctrl.yaml#` with meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Compatible contract: `fsl,imx7d-iomuxc`, `fsl,imx7d-iomuxc-lpsr`.
- Required properties: `compatible`, `reg`.
- Top-level framework properties: `compatible`, `reg`.
- Vendor or device-specific extensions: `fsl,input-sel`.
- Other declared top-level properties: none declared.
- Child-node or reusable schema API: patternProperties `grp$`.
- Property detail signals: compatible; reg (maxItems 1); fsl,input-sel (phandle for main iomuxc controller which shares the input select register for daisy chain settings.; ref `/schemas/types.yaml#/definitions/phandle`).

## Control Flow
There is no imperative execution path in this YAML. Validation starts when dt-schema selects this
document for a node whose `compatible` value matches the schema, checks the required list, evaluates
referenced common pinctrl/GPIO schemas, applies property constraints, then walks child-node patterns
and conditional branches.

This file contains 1 `allOf`, 1 `oneOf`, 0 `anyOf`, and 1 `if` blocks. Property closure: top-level
`additionalProperties: false` rejects undeclared properties.

## State and Persistence Behavior
The binding stores no runtime state. It persists as source-controlled schema text, while the state
it describes persists in DTS/DTB data: register windows, GPIO provider cell counts, interrupt
wiring, pin groups, mux functions, drive strengths, pulls, and optional child pin configuration
nodes. Kernel drivers consume the validated DT data at boot or device probe and then program
hardware pin mux, pad, and GPIO state; this YAML only constrains that data before runtime.

## Dependencies and Integration Points
- Schema references: `/schemas/types.yaml#/definitions/phandle`, `/schemas/types.yaml#/definitions/uint32-matrix`, `pinctrl.yaml#`.
- Textual schema references: `/schemas/pinctrl/fsl,imx7d-pinctrl.yaml#`, `/schemas/types.yaml#/definitions/phandle`, `/schemas/types.yaml#/definitions/uint32-matrix`.
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
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/fsl,imx7d-pinctrl.yaml` to parse this YAML, validate meta-schema rules, and compile its 2 inline example(s).
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/fsl,imx7d-pinctrl.yaml` on affected board DTS files to confirm real nodes satisfy required properties, compatible choices, child node names, and referenced common schemas.
- Useful negative tests remove one required property, change `compatible`, and add an undeclared property where closure is enabled. Example seed: iomuxc: pinctrl@30330000 {; compatible = "fsl,imx7d-iomuxc";; reg = <0x30330000 0x10000>;; pinctrl_uart5: uart5grp {.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/fsl,imx7d-pinctrl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/fsl,imx7ulp-iomuxc1.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/fsl,imx7ulp-iomuxc1.yaml

## Purpose
This file is a Linux Devicetree JSON-schema document for a pin multiplexing controller binding:
Freescale i.MX7ULP IOMUX Controller. It lives in the pinctrl binding tree and gives dt-schema a
machine-readable contract for board DTS nodes before the kernel pinctrl/GPIO drivers consume those
nodes during probe.

i.MX 7ULP has three IOMUXC instances: IOMUXC0 for M4 ports, IOMUXC1 for A7 ports and IOMUXC DDR for
DDR interface. Note: This binding doc is only for the IOMUXC1 support in A7 Domain and it only
supports generic pin config. Please refer to fsl,imx-pinctrl.txt in this directory for common
binding part and usage.

The binding is maintained in-source by Frank Li <Frank.Li@nxp.com>.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/pinctrl/fsl,imx7ulp-iomuxc1.yaml#` with meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Compatible contract: `fsl,imx7ulp-iomuxc1`.
- Required properties: `compatible`, `reg`.
- Top-level framework properties: `compatible`, `reg`.
- Vendor or device-specific extensions: none declared.
- Other declared top-level properties: none declared.
- Child-node or reusable schema API: patternProperties `grp$`.
- Property detail signals: compatible (const `fsl,imx7ulp-iomuxc1`); reg (maxItems 1).

## Control Flow
There is no imperative execution path in this YAML. Validation starts when dt-schema selects this
document for a node whose `compatible` value matches the schema, checks the required list, evaluates
referenced common pinctrl/GPIO schemas, applies property constraints, then walks child-node patterns
and conditional branches.

This file contains 1 `allOf`, 0 `oneOf`, 0 `anyOf`, and 0 `if` blocks. Property closure: top-level
`unevaluatedProperties: false` closes properties after referenced schemas are evaluated.

## State and Persistence Behavior
The binding stores no runtime state. It persists as source-controlled schema text, while the state
it describes persists in DTS/DTB data: register windows, GPIO provider cell counts, interrupt
wiring, pin groups, mux functions, drive strengths, pulls, and optional child pin configuration
nodes. Kernel drivers consume the validated DT data at boot or device probe and then program
hardware pin mux, pad, and GPIO state; this YAML only constrains that data before runtime.

## Dependencies and Integration Points
- Schema references: `/schemas/types.yaml#/definitions/uint32-matrix`, `pinctrl.yaml#`.
- Textual schema references: `/schemas/pinctrl/fsl,imx7ulp-iomuxc1.yaml#`, `/schemas/types.yaml#/definitions/uint32-matrix`.
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
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/fsl,imx7ulp-iomuxc1.yaml` to parse this YAML, validate meta-schema rules, and compile its 1 inline example(s).
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/fsl,imx7ulp-iomuxc1.yaml` on affected board DTS files to confirm real nodes satisfy required properties, compatible choices, child node names, and referenced common schemas.
- Useful negative tests remove one required property, change `compatible`, and add an undeclared property where closure is enabled. Example seed: pinctrl@40ac0000 {; compatible = "fsl,imx7ulp-iomuxc1";; reg = <0x40ac0000 0x1000>;; lpuart4grp {.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/fsl,imx7ulp-iomuxc1.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/fsl,imx8m-pinctrl.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/fsl,imx8m-pinctrl.yaml

## Purpose
This file is a Linux Devicetree JSON-schema document for a pin multiplexing controller binding:
Freescale IMX8M IOMUX Controller. It lives in the pinctrl binding tree and gives dt-schema a
machine-readable contract for board DTS nodes before the kernel pinctrl/GPIO drivers consume those
nodes during probe.

Please refer to fsl,imx-pinctrl.txt and pinctrl-bindings.txt in this directory for common binding
part and usage.

The binding is maintained in-source by Peng Fan <peng.fan@nxp.com>.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/pinctrl/fsl,imx8m-pinctrl.yaml#` with meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Compatible contract: `fsl,imx8mm-iomuxc`, `fsl,imx8mn-iomuxc`, `fsl,imx8mp-iomuxc`, `fsl,imx8mq-iomuxc`.
- Required properties: `compatible`, `reg`.
- Top-level framework properties: `compatible`, `reg`.
- Vendor or device-specific extensions: none declared.
- Other declared top-level properties: none declared.
- Child-node or reusable schema API: patternProperties `grp$`.
- Property detail signals: compatible (enum `fsl,imx8mm-iomuxc`, `fsl,imx8mn-iomuxc`, `fsl,imx8mp-iomuxc`, `fsl,imx8mq-iomuxc`); reg (maxItems 1).

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
- Schema references: `/schemas/types.yaml#/definitions/uint32-matrix`, `pinctrl.yaml#`.
- Textual schema references: `/schemas/pinctrl/fsl,imx8m-pinctrl.yaml#`, `/schemas/types.yaml#/definitions/uint32-matrix`.
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
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/fsl,imx8m-pinctrl.yaml` to parse this YAML, validate meta-schema rules, and compile its 1 inline example(s).
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/fsl,imx8m-pinctrl.yaml` on affected board DTS files to confirm real nodes satisfy required properties, compatible choices, child node names, and referenced common schemas.
- Useful negative tests remove one required property, change `compatible`, and add an undeclared property where closure is enabled. Example seed: iomuxc: pinctrl@30330000 {; compatible = "fsl,imx8mm-iomuxc";; reg = <0x30330000 0x10000>;; pinctrl_uart2: uart2grp {.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/fsl,imx8m-pinctrl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/fsl,imx8ulp-pinctrl.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/fsl,imx8ulp-pinctrl.yaml

## Purpose
This file is a Linux Devicetree JSON-schema document for a pin multiplexing controller binding:
Freescale IMX8ULP IOMUX Controller. It lives in the pinctrl binding tree and gives dt-schema a
machine-readable contract for board DTS nodes before the kernel pinctrl/GPIO drivers consume those
nodes during probe.

Please refer to fsl,imx-pinctrl.txt and pinctrl-bindings.txt in this directory for common binding
part and usage.

The binding is maintained in-source by Jacky Bai <ping.bai@nxp.com>.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/pinctrl/fsl,imx8ulp-pinctrl.yaml#` with meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Compatible contract: `fsl,imx8ulp-iomuxc1`.
- Required properties: `compatible`, `reg`.
- Top-level framework properties: `compatible`, `reg`.
- Vendor or device-specific extensions: none declared.
- Other declared top-level properties: none declared.
- Child-node or reusable schema API: patternProperties `grp$`.
- Property detail signals: compatible (const `fsl,imx8ulp-iomuxc1`); reg (maxItems 1).

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
- Schema references: `/schemas/types.yaml#/definitions/uint32-matrix`, `pinctrl.yaml#`.
- Textual schema references: `/schemas/pinctrl/fsl,imx8ulp-pinctrl.yaml#`, `/schemas/types.yaml#/definitions/uint32-matrix`.
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
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/fsl,imx8ulp-pinctrl.yaml` to parse this YAML, validate meta-schema rules, and compile its 1 inline example(s).
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/fsl,imx8ulp-pinctrl.yaml` on affected board DTS files to confirm real nodes satisfy required properties, compatible choices, child node names, and referenced common schemas.
- Useful negative tests remove one required property, change `compatible`, and add an undeclared property where closure is enabled. Example seed: iomuxc: pinctrl@298c0000 {; compatible = "fsl,imx8ulp-iomuxc1";; reg = <0x298c0000 0x10000>;; pinctrl_lpuart5: lpuart5grp {.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/fsl,imx8ulp-pinctrl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/fsl,imx9-pinctrl.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/fsl,imx9-pinctrl.yaml

## Purpose
This file is a Linux Devicetree JSON-schema document for a pin multiplexing controller binding:
Freescale IMX9 IOMUX Controller. It lives in the pinctrl binding tree and gives dt-schema a machine-
readable contract for board DTS nodes before the kernel pinctrl/GPIO drivers consume those nodes
during probe.

Please refer to fsl,imx-pinctrl.txt and pinctrl-bindings.txt in this directory for common binding
part and usage.

The binding is maintained in-source by Peng Fan <peng.fan@nxp.com>.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/pinctrl/fsl,imx9-pinctrl.yaml#` with meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Compatible contract: `fsl,imx91-iomuxc`, `fsl,imx93-iomuxc`.
- Required properties: `compatible`, `reg`.
- Top-level framework properties: `compatible`, `reg`.
- Vendor or device-specific extensions: none declared.
- Other declared top-level properties: none declared.
- Child-node or reusable schema API: patternProperties `grp$`.
- Property detail signals: compatible (enum `fsl,imx91-iomuxc`, `fsl,imx93-iomuxc`); reg (maxItems 1).

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
- Schema references: `pinctrl.yaml#`, `/schemas/types.yaml#/definitions/uint32-matrix`.
- Textual schema references: `/schemas/pinctrl/fsl,imx9-pinctrl.yaml#`, `/schemas/types.yaml#/definitions/uint32-matrix`.
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
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/fsl,imx9-pinctrl.yaml` to parse this YAML, validate meta-schema rules, and compile its 1 inline example(s).
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/fsl,imx9-pinctrl.yaml` on affected board DTS files to confirm real nodes satisfy required properties, compatible choices, child node names, and referenced common schemas.
- Useful negative tests remove one required property, change `compatible`, and add an undeclared property where closure is enabled. Example seed: iomuxc: pinctrl@443c0000 {; compatible = "fsl,imx93-iomuxc";; reg = <0x30330000 0x10000>;; pinctrl_uart3: uart3grp {.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/fsl,imx9-pinctrl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/fsl,imxrt1050.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/fsl,imxrt1050.yaml

## Purpose
This file is a Linux Devicetree JSON-schema document for a pin multiplexing controller binding:
Freescale IMXRT1050 IOMUX Controller. It lives in the pinctrl binding tree and gives dt-schema a
machine-readable contract for board DTS nodes before the kernel pinctrl/GPIO drivers consume those
nodes during probe.

Please refer to fsl,imx-pinctrl.txt and pinctrl-bindings.txt in this directory for common binding
part and usage.

The binding is maintained in-source by Giulio Benetti <giulio.benetti@benettiengineering.com>, Jesse
Taube <Mr.Bossman075@gmail.com>.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/pinctrl/fsl,imxrt1050.yaml#` with meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Compatible contract: `fsl,imxrt1050-iomuxc`.
- Required properties: `compatible`, `reg`.
- Top-level framework properties: `compatible`, `reg`.
- Vendor or device-specific extensions: none declared.
- Other declared top-level properties: none declared.
- Child-node or reusable schema API: patternProperties `grp$`.
- Property detail signals: compatible (const `fsl,imxrt1050-iomuxc`); reg (maxItems 1).

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
- Schema references: `/schemas/types.yaml#/definitions/uint32-matrix`.
- Textual schema references: `/schemas/pinctrl/fsl,imxrt1050.yaml#`, `/schemas/types.yaml#/definitions/uint32-matrix`.
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
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/fsl,imxrt1050.yaml` to parse this YAML, validate meta-schema rules, and compile its 1 inline example(s).
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/fsl,imxrt1050.yaml` on affected board DTS files to confirm real nodes satisfy required properties, compatible choices, child node names, and referenced common schemas.
- Useful negative tests remove one required property, change `compatible`, and add an undeclared property where closure is enabled. Example seed: iomuxc: iomuxc@401f8000 {; compatible = "fsl,imxrt1050-iomuxc";; reg = <0x401f8000 0x4000>;; pinctrl_lpuart1: lpuart1grp {.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/fsl,imxrt1050.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/fsl,imxrt1170.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/fsl,imxrt1170.yaml

## Purpose
This file is a Linux Devicetree JSON-schema document for a pin multiplexing controller binding:
Freescale i.MXRT1170 IOMUX Controller. It lives in the pinctrl binding tree and gives dt-schema a
machine-readable contract for board DTS nodes before the kernel pinctrl/GPIO drivers consume those
nodes during probe.

Please refer to fsl,imx-pinctrl.txt and pinctrl-bindings.txt in this directory for common binding
part and usage.

The binding is maintained in-source by Giulio Benetti <giulio.benetti@benettiengineering.com>, Jesse
Taube <Mr.Bossman075@gmail.com>.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/pinctrl/fsl,imxrt1170.yaml#` with meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Compatible contract: `fsl,imxrt1170-iomuxc`.
- Required properties: `compatible`, `reg`.
- Top-level framework properties: `compatible`, `reg`.
- Vendor or device-specific extensions: none declared.
- Other declared top-level properties: none declared.
- Child-node or reusable schema API: patternProperties `grp$`.
- Property detail signals: compatible (const `fsl,imxrt1170-iomuxc`); reg (maxItems 1).

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
- Schema references: `/schemas/types.yaml#/definitions/uint32-matrix`.
- Textual schema references: `/schemas/pinctrl/fsl,imxrt1170.yaml#`, `/schemas/types.yaml#/definitions/uint32-matrix`.
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
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/fsl,imxrt1170.yaml` to parse this YAML, validate meta-schema rules, and compile its 1 inline example(s).
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/fsl,imxrt1170.yaml` on affected board DTS files to confirm real nodes satisfy required properties, compatible choices, child node names, and referenced common schemas.
- Useful negative tests remove one required property, change `compatible`, and add an undeclared property where closure is enabled. Example seed: iomuxc: iomuxc@400e8000 {; compatible = "fsl,imxrt1170-iomuxc";; reg = <0x400e8000 0x4000>;; pinctrl_lpuart1: lpuart1grp {; fsl,pins =.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/fsl,imxrt1170.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/fsl,scu-pinctrl.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/fsl,scu-pinctrl.yaml

## Purpose
This file is a Linux Devicetree JSON-schema document for a pin controller binding: i.MX SCU Client
Device Node - Pinctrl Based on SCU Message Protocol. It lives in the pinctrl binding tree and gives
dt-schema a machine-readable contract for board DTS nodes before the kernel pinctrl/GPIO drivers
consume those nodes during probe.

i.MX SCU Client Device Node Client nodes are maintained as children of the relevant IMX-SCU device
node. This binding uses the i.MX common pinctrl binding.
(Documentation/devicetree/bindings/pinctrl/fsl,imx-pinctrl.txt)

The binding is maintained in-source by Dong Aisheng <aisheng.dong@nxp.com>.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/pinctrl/fsl,scu-pinctrl.yaml#` with meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Compatible contract: `fsl,imx8qm-iomuxc`, `fsl,imx8qxp-iomuxc`, `fsl,imx8dxl-iomuxc`.
- Required properties: `compatible`.
- Top-level framework properties: `compatible`.
- Vendor or device-specific extensions: none declared.
- Other declared top-level properties: none declared.
- Child-node or reusable schema API: patternProperties `grp$`.
- Property detail signals: compatible (enum `fsl,imx8qm-iomuxc`, `fsl,imx8qxp-iomuxc`, `fsl,imx8dxl-iomuxc`).

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
- Schema references: `pinctrl.yaml#`, `/schemas/types.yaml#/definitions/uint32-matrix`.
- Textual schema references: `/schemas/pinctrl/fsl,scu-pinctrl.yaml#`, `/schemas/types.yaml#/definitions/uint32-matrix`.
Runtime integration is with Linux pinctrl and GPIO framework drivers selected by `compatible`. Board
`.dts` files instantiate nodes that satisfy this schema; `make dt_binding_check` validates the
binding and inline examples, while `make dtbs_check` validates real board descriptions against the
same contract.

## Risks
- A missing or misspelled `compatible` value prevents both schema matching and driver binding.
- Omitting required fields such as `compatible` should fail dt-schema validation before boot.
- Child node regexes and reusable pin configuration schemas are easy to misuse; incorrect group/function names can validate poorly or fail later in driver lookup tables.
- The closed property model catches typos, but any newly needed board property requires a binding update before DTS changes can pass validation.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/fsl,scu-pinctrl.yaml` to parse this YAML, validate meta-schema rules, and compile its 1 inline example(s).
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/fsl,scu-pinctrl.yaml` on affected board DTS files to confirm real nodes satisfy required properties, compatible choices, child node names, and referenced common schemas.
- Useful negative tests remove one required property, change `compatible`, and add an undeclared property where closure is enabled. Example seed: pinctrl {; compatible = "fsl,imx8qxp-iomuxc";; pinctrl_lpuart0: lpuart0grp {; fsl,pins = <.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/fsl,scu-pinctrl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/fsl,vf610-iomuxc.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/fsl,vf610-iomuxc.yaml

## Purpose
This file is a Linux Devicetree JSON-schema document for a pin multiplexing controller binding:
Freescale Vybrid VF610 IOMUX Controller. It lives in the pinctrl binding tree and gives dt-schema a
machine-readable contract for board DTS nodes before the kernel pinctrl/GPIO drivers consume those
nodes during probe.

Please refer to fsl,imx-pinctrl.txt in this directory for common binding part and usage.

The binding is maintained in-source by Frank Li <Frank.Li@nxp.com>.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/pinctrl/fsl,vf610-iomuxc.yaml#` with meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Compatible contract: `fsl,vf610-iomuxc`.
- Required properties: `compatible`, `reg`.
- Top-level framework properties: `compatible`, `reg`.
- Vendor or device-specific extensions: none declared.
- Other declared top-level properties: none declared.
- Child-node or reusable schema API: patternProperties `grp$`.
- Property detail signals: compatible (const `fsl,vf610-iomuxc`); reg (maxItems 1).

## Control Flow
There is no imperative execution path in this YAML. Validation starts when dt-schema selects this
document for a node whose `compatible` value matches the schema, checks the required list, evaluates
referenced common pinctrl/GPIO schemas, applies property constraints, then walks child-node patterns
and conditional branches.

This file contains 1 `allOf`, 0 `oneOf`, 0 `anyOf`, and 0 `if` blocks. Property closure: top-level
`unevaluatedProperties: false` closes properties after referenced schemas are evaluated.

## State and Persistence Behavior
The binding stores no runtime state. It persists as source-controlled schema text, while the state
it describes persists in DTS/DTB data: register windows, GPIO provider cell counts, interrupt
wiring, pin groups, mux functions, drive strengths, pulls, and optional child pin configuration
nodes. Kernel drivers consume the validated DT data at boot or device probe and then program
hardware pin mux, pad, and GPIO state; this YAML only constrains that data before runtime.

## Dependencies and Integration Points
- Schema references: `/schemas/types.yaml#/definitions/uint32-matrix`, `pinctrl.yaml#`.
- Textual schema references: `/schemas/pinctrl/fsl,vf610-iomuxc.yaml#`, `/schemas/types.yaml#/definitions/uint32-matrix`.
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
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/fsl,vf610-iomuxc.yaml` to parse this YAML, validate meta-schema rules, and compile its 0 inline example(s).
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/fsl,vf610-iomuxc.yaml` on affected board DTS files to confirm real nodes satisfy required properties, compatible choices, child node names, and referenced common schemas.
- Useful negative tests remove one required property, change `compatible`, add a bogus pin group/function, and add an undeclared property where closure is enabled.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/fsl,vf610-iomuxc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/ingenic,pinctrl.yaml -->
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

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/ingenic,pinctrl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/intel,lgm-io.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/intel,lgm-io.yaml

## Purpose
This file is a Linux Devicetree JSON-schema document for a pin multiplexing controller binding:
Intel Lightning Mountain SoC pinmux & GPIO controller. It lives in the pinctrl binding tree and
gives dt-schema a machine-readable contract for board DTS nodes before the kernel pinctrl/GPIO
drivers consume those nodes during probe.

Pinmux & GPIO controller controls pin multiplexing & configuration including GPIO function selection
& GPIO attributes configuration.

The binding is maintained in-source by Rahul Tanwar <rahul.tanwar@linux.intel.com>.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/pinctrl/intel,lgm-io.yaml#` with meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Compatible contract: `intel,lgm-io`.
- Required properties: `compatible`, `reg`.
- Top-level framework properties: `compatible`, `reg`.
- Vendor or device-specific extensions: none declared.
- Other declared top-level properties: none declared.
- Child-node or reusable schema API: patternProperties `-pins$`.
- Property detail signals: compatible (const `intel,lgm-io`); reg (maxItems 1).

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
- Schema references: `pinmux-node.yaml#`, `pinctrl.yaml#`.
- Textual schema references: `/schemas/pinctrl/intel,lgm-io.yaml#`.
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
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/intel,lgm-io.yaml` to parse this YAML, validate meta-schema rules, and compile its 1 inline example(s).
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/intel,lgm-io.yaml` on affected board DTS files to confirm real nodes satisfy required properties, compatible choices, child node names, and referenced common schemas.
- Useful negative tests remove one required property, change `compatible`, and add an undeclared property where closure is enabled. Example seed: pinctrl: pinctrl@e2880000 {; compatible = "intel,lgm-io";; reg = <0xe2880000 0x100000>;; uart0-pins {.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/intel,lgm-io.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/intel,pinctrl-keembay.yaml -->
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

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/intel,pinctrl-keembay.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/loongson,ls2k-pinctrl.yaml -->
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

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/loongson,ls2k-pinctrl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/marvell,ac5-pinctrl.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/marvell,ac5-pinctrl.yaml

## Purpose
This file is a Linux Devicetree JSON-schema document for a pin controller binding: Marvell AC5 pin
controller. It lives in the pinctrl binding tree and gives dt-schema a machine-readable contract for
board DTS nodes before the kernel pinctrl/GPIO drivers consume those nodes during probe.

Bindings for Marvell's AC5 memory-mapped pin controller.

The binding is maintained in-source by Chris Packham <chris.packham@alliedtelesis.co.nz>.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/pinctrl/marvell,ac5-pinctrl.yaml#` with meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Compatible contract: `marvell,ac5-pinctrl`.
- Required properties: `compatible`, `reg`.
- Top-level framework properties: `compatible`, `reg`.
- Vendor or device-specific extensions: none declared.
- Other declared top-level properties: none declared.
- Child-node or reusable schema API: patternProperties `-pins$`.
- Property detail signals: compatible; reg (maxItems 1).

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
- Schema references: `pinmux-node.yaml#`, `/schemas/types.yaml#/definitions/string`, `/schemas/types.yaml#/definitions/string-array`, `pinctrl.yaml#`.
- Textual schema references: `/schemas/pinctrl/marvell,ac5-pinctrl.yaml#`, `/schemas/types.yaml#/definitions/string`, `/schemas/types.yaml#/definitions/string-array`.
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
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/marvell,ac5-pinctrl.yaml` to parse this YAML, validate meta-schema rules, and compile its 1 inline example(s).
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/marvell,ac5-pinctrl.yaml` on affected board DTS files to confirm real nodes satisfy required properties, compatible choices, child node names, and referenced common schemas.
- Useful negative tests remove one required property, change `compatible`, and add an undeclared property where closure is enabled. Example seed: pinctrl@80020100 {; compatible = "marvell,ac5-pinctrl";; reg = <0x80020100 0x20>;; i2c0_pins: i2c0-pins {.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/marvell,ac5-pinctrl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/marvell,ap806-pinctrl.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/marvell,ap806-pinctrl.yaml

## Purpose
This file is a Linux Devicetree JSON-schema document for a pin controller binding: Marvell AP806 pin
controller. It lives in the pinctrl binding tree and gives dt-schema a machine-readable contract for
board DTS nodes before the kernel pinctrl/GPIO drivers consume those nodes during probe.

The schema relies on title, compatible values, and property constraints rather than a long description block.

The binding is maintained in-source by Gregory Clement <gregory.clement@bootlin.com>, Miquel Raynal
<miquel.raynal@bootlin.com>.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/pinctrl/marvell,ap806-pinctrl.yaml#` with meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Compatible contract: `marvell,ap806-pinctrl`.
- Required properties: `compatible`.
- Top-level framework properties: `compatible`, `reg`.
- Vendor or device-specific extensions: none declared.
- Other declared top-level properties: none declared.
- Child-node or reusable schema API: patternProperties `-pins$`.
- Property detail signals: compatible (const `marvell,ap806-pinctrl`); reg (maxItems 1).

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
- Schema references: `/schemas/types.yaml#/definitions/string`, `/schemas/types.yaml#/definitions/string-array`, `pinctrl.yaml#`.
- Textual schema references: `/schemas/pinctrl/marvell,ap806-pinctrl.yaml#`, `/schemas/types.yaml#/definitions/string`, `/schemas/types.yaml#/definitions/string-array`.
Runtime integration is with Linux pinctrl and GPIO framework drivers selected by `compatible`. Board
`.dts` files instantiate nodes that satisfy this schema; `make dt_binding_check` validates the
binding and inline examples, while `make dtbs_check` validates real board descriptions against the
same contract.

## Risks
- A missing or misspelled `compatible` value prevents both schema matching and driver binding.
- Omitting required fields such as `compatible` should fail dt-schema validation before boot.
- Child node regexes and reusable pin configuration schemas are easy to misuse; incorrect group/function names can validate poorly or fail later in driver lookup tables.
- The closed property model catches typos, but any newly needed board property requires a binding update before DTS changes can pass validation.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/marvell,ap806-pinctrl.yaml` to parse this YAML, validate meta-schema rules, and compile its 1 inline example(s).
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/marvell,ap806-pinctrl.yaml` on affected board DTS files to confirm real nodes satisfy required properties, compatible choices, child node names, and referenced common schemas.
- Useful negative tests remove one required property, change `compatible`, and add an undeclared property where closure is enabled. Example seed: pinctrl {; compatible = "marvell,ap806-pinctrl";; uart0_pins: uart0-pins {; marvell,pins = "mpp11", "mpp19";.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/marvell,ap806-pinctrl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/marvell,armada-7k-pinctrl.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/marvell,armada-7k-pinctrl.yaml

## Purpose
This file is a Linux Devicetree JSON-schema document for a pin controller binding: Marvell Armada
7K/8K pin controller. It lives in the pinctrl binding tree and gives dt-schema a machine-readable
contract for board DTS nodes before the kernel pinctrl/GPIO drivers consume those nodes during
probe.

The schema relies on title, compatible values, and property constraints rather than a long description block.

The binding is maintained in-source by Gregory Clement <gregory.clement@bootlin.com>, Miquel Raynal
<miquel.raynal@bootlin.com>.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/pinctrl/marvell,armada-7k-pinctrl.yaml#` with meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Compatible contract: `marvell,armada-7k-pinctrl`, `marvell,armada-8k-cpm-pinctrl`, `marvell,armada-8k-cps-pinctrl`, `marvell,cp115-standalone-pinctrl`.
- Required properties: `compatible`.
- Top-level framework properties: `compatible`, `reg`.
- Vendor or device-specific extensions: none declared.
- Other declared top-level properties: none declared.
- Child-node or reusable schema API: patternProperties `-pins(-.+)?$`.
- Property detail signals: compatible (enum `marvell,armada-7k-pinctrl`, `marvell,armada-8k-cpm-pinctrl`, `marvell,armada-8k-cps-pinctrl`, `marvell,cp115-standalone-pinctrl`); reg (maxItems 1).

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
- Schema references: `/schemas/types.yaml#/definitions/string`, `/schemas/types.yaml#/definitions/string-array`, `pinctrl.yaml#`.
- Textual schema references: `/schemas/pinctrl/marvell,armada-7k-pinctrl.yaml#`, `/schemas/types.yaml#/definitions/string`, `/schemas/types.yaml#/definitions/string-array`.
Runtime integration is with Linux pinctrl and GPIO framework drivers selected by `compatible`. Board
`.dts` files instantiate nodes that satisfy this schema; `make dt_binding_check` validates the
binding and inline examples, while `make dtbs_check` validates real board descriptions against the
same contract.

## Risks
- A missing or misspelled `compatible` value prevents both schema matching and driver binding.
- Omitting required fields such as `compatible` should fail dt-schema validation before boot.
- Child node regexes and reusable pin configuration schemas are easy to misuse; incorrect group/function names can validate poorly or fail later in driver lookup tables.
- The closed property model catches typos, but any newly needed board property requires a binding update before DTS changes can pass validation.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/marvell,armada-7k-pinctrl.yaml` to parse this YAML, validate meta-schema rules, and compile its 1 inline example(s).
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/marvell,armada-7k-pinctrl.yaml` on affected board DTS files to confirm real nodes satisfy required properties, compatible choices, child node names, and referenced common schemas.
- Useful negative tests remove one required property, change `compatible`, and add an undeclared property where closure is enabled. Example seed: pinctrl {; compatible = "marvell,armada-7k-pinctrl";; nand_pins: nand-pins {; marvell,pins =.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/marvell,armada-7k-pinctrl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/marvell,armada3710-xb-pinctrl.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/marvell,armada3710-xb-pinctrl.yaml

## Purpose
This file is a Linux Devicetree JSON-schema document for a pin controller binding: Marvell Armada
37xx SoC pin and gpio controller. It lives in the pinctrl binding tree and gives dt-schema a
machine-readable contract for board DTS nodes before the kernel pinctrl/GPIO drivers consume those
nodes during probe.

Each Armada 37xx SoC come with two pin and gpio controller one for the south bridge and the other
for the north bridge. Inside this set of register the gpio latch allows exposing some configuration
of the SoC and especially the clock frequency of the xtal. Hence, this node is a represent as syscon
allowing sharing the register between multiple hardware block.

The binding is maintained in-source by Gregory CLEMENT <gregory.clement@bootlin.com>, Marek Behún
<kabel@kernel.org>, Miquel Raynal <miquel.raynal@bootlin.com>.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/pinctrl/marvell,armada3710-xb-pinctrl.yaml#` with meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Compatible contract: `marvell,armada3710-sb-pinctrl`, `marvell,armada3710-nb-pinctrl`, `syscon`, `simple-mfd`, `marvell,armada-3700-xtal-clock`.
- Required properties: `compatible`, `reg`.
- Top-level framework properties: `compatible`, `reg`.
- Vendor or device-specific extensions: none declared.
- Other declared top-level properties: `gpio`, `xtal-clk`.
- Child-node or reusable schema API: patternProperties `-pins$`; object-valued child/property schemas `gpio`, `xtal-clk`.
- Property detail signals: compatible; reg; gpio (GPIO controller subnode); xtal-clk.

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
- Schema references: `pinmux-node.yaml#`.
- Example/header integration: `dt-bindings/interrupt-controller/arm-gic.h`.
- Textual schema references: `/schemas/pinctrl/marvell,armada3710-xb-pinctrl.yaml#`.
Runtime integration is with Linux pinctrl and GPIO framework drivers selected by `compatible`. Board
`.dts` files instantiate nodes that satisfy this schema; `make dt_binding_check` validates the
binding and inline examples, while `make dtbs_check` validates real board descriptions against the
same contract.

## Risks
- A missing or misspelled `compatible` value prevents both schema matching and driver binding.
- Omitting required fields such as `compatible`, `reg` should fail dt-schema validation before boot.
- Child node regexes and reusable pin configuration schemas are easy to misuse; incorrect group/function names can validate poorly or fail later in driver lookup tables.
- The closed property model catches typos, but any newly needed board property requires a binding update before DTS changes can pass validation.
- GPIO provider fields such as `#gpio-cells`, `gpio-ranges`, and interrupt controller wiring must match the runtime driver's expectations or GPIO consumers will resolve the wrong pins.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/marvell,armada3710-xb-pinctrl.yaml` to parse this YAML, validate meta-schema rules, and compile its 1 inline example(s).
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/marvell,armada3710-xb-pinctrl.yaml` on affected board DTS files to confirm real nodes satisfy required properties, compatible choices, child node names, and referenced common schemas.
- Useful negative tests remove one required property, change `compatible`, and add an undeclared property where closure is enabled. Example seed: #include <dt-bindings/interrupt-controller/arm-gic.h>; pinctrl_sb: pinctrl@18800 {; compatible = "marvell,armada3710-sb-pinctrl", "syscon", "simple-mfd";; reg = <0x18800 0x100>, <0x18C00 0x20>;.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/marvell,armada3710-xb-pinctrl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/marvell,berlin2-soc-pinctrl.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/marvell,berlin2-soc-pinctrl.yaml

## Purpose
This file is a Linux Devicetree JSON-schema document for a pin controller binding: Marvell Berlin
pin-controller driver. It lives in the pinctrl binding tree and gives dt-schema a machine-readable
contract for board DTS nodes before the kernel pinctrl/GPIO drivers consume those nodes during
probe.

Pin control registers are part of both chip controller and system controller register sets. Pin
controller nodes should be a sub-node of either the chip controller or system controller node. The
pins controlled are organized in groups, so no actual pin information is needed. A pin-controller
node should contain subnodes representing the pin group configurations, one per function. Each
subnode has the group name and the muxing function used. Be aware the Marvell Berlin datasheets use
the keyword 'mode' for what is called a 'function' in the pin-controller subsystem.

The binding is maintained in-source by Antoine Tenart <atenart@kernel.org>, Jisheng Zhang
<jszhang@kernel.org>.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/pinctrl/marvell,berlin2-soc-pinctrl.yaml#` with meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Compatible contract: `marvell,berlin2-soc-pinctrl`, `marvell,berlin2-system-pinctrl`, `marvell,berlin2cd-soc-pinctrl`, `marvell,berlin2cd-system-pinctrl`, `marvell,berlin2q-soc-pinctrl`, `marvell,berlin2q-system-pinctrl`, `marvell,berlin4ct-avio-pinctrl`, `marvell,berlin4ct-soc-pinctrl`, `marvell,berlin4ct-system-pinctrl`, `syna,as370-soc-pinctrl`.
- Required properties: none declared.
- Top-level framework properties: `compatible`, `reg`.
- Vendor or device-specific extensions: none declared.
- Other declared top-level properties: none declared.
- Child-node or reusable schema API: no named child-node API or pattern child-node contract is declared.
- Property detail signals: compatible; reg (maxItems 1).

## Control Flow
There is no imperative execution path in this YAML. Validation starts when dt-schema selects this
document for a node whose `compatible` value matches the schema, checks the required list, evaluates
referenced common pinctrl/GPIO schemas, applies property constraints, then walks child-node patterns
and conditional branches.

This file contains 1 `allOf`, 0 `oneOf`, 0 `anyOf`, and 1 `if` blocks. Property closure: no explicit
top-level closure keyword is present in the parsed schema.

## State and Persistence Behavior
The binding stores no runtime state. It persists as source-controlled schema text, while the state
it describes persists in DTS/DTB data: register windows, GPIO provider cell counts, interrupt
wiring, pin groups, mux functions, drive strengths, pulls, and optional child pin configuration
nodes. Kernel drivers consume the validated DT data at boot or device probe and then program
hardware pin mux, pad, and GPIO state; this YAML only constrains that data before runtime.

## Dependencies and Integration Points
- Schema references: `/schemas/pinctrl/pinmux-node.yaml#`, `/schemas/types.yaml#/definitions/string-array`, `/schemas/types.yaml#/definitions/string`.
- Textual schema references: `/schemas/pinctrl/marvell,berlin2-soc-pinctrl.yaml#`, `/schemas/pinctrl/pinmux-node.yaml#`, `/schemas/types.yaml#/definitions/string-array`, `/schemas/types.yaml#/definitions/string`.
Runtime integration is with Linux pinctrl and GPIO framework drivers selected by `compatible`. Board
`.dts` files instantiate nodes that satisfy this schema; `make dt_binding_check` validates the
binding and inline examples, while `make dtbs_check` validates real board descriptions against the
same contract.

## Risks
- A missing or misspelled `compatible` value prevents both schema matching and driver binding.
- Open or partially open property handling can let board-specific typos escape schema validation and surface only at driver probe time.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/marvell,berlin2-soc-pinctrl.yaml` to parse this YAML, validate meta-schema rules, and compile its 1 inline example(s).
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/marvell,berlin2-soc-pinctrl.yaml` on affected board DTS files to confirm real nodes satisfy required properties, compatible choices, child node names, and referenced common schemas.
- Useful negative tests remove one required property, change `compatible`, and add an undeclared property where closure is enabled. Example seed: pinctrl {; compatible = "marvell,berlin2q-system-pinctrl";; uart0-pmux {; groups = "GSM12";.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/marvell,berlin2-soc-pinctrl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/maxim,max77620-pinctrl.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/maxim,max77620-pinctrl.yaml

## Purpose
This file is a Linux Devicetree JSON-schema document for a pin multiplexing controller binding:
Pinmux controller function for Maxim MAX77620 Power management IC. It lives in the pinctrl binding
tree and gives dt-schema a machine-readable contract for board DTS nodes before the kernel
pinctrl/GPIO drivers consume those nodes during probe.

Device has 8 GPIO pins which can be configured as GPIO as well as the special IO functions.

The binding is maintained in-source by Svyatoslav Ryhel <clamor95@gmail.com>.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/pinctrl/maxim,max77620-pinctrl.yaml#` with meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Compatible contract: none declared.
- Required properties: none declared.
- Top-level framework properties: none declared.
- Vendor or device-specific extensions: none declared.
- Other declared top-level properties: none declared.
- Child-node or reusable schema API: patternProperties `^(pin|gpio).`.
- Property detail signals: no explicit top-level `properties` map is declared.

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
- Schema references: `/schemas/pinctrl/pincfg-node.yaml`, `/schemas/pinctrl/pinmux-node.yaml`, `/schemas/types.yaml#/definitions/uint32`.
- Textual schema references: `/schemas/pinctrl/maxim,max77620-pinctrl.yaml#`, `/schemas/pinctrl/pincfg-node.yaml`, `/schemas/pinctrl/pinmux-node.yaml`, `/schemas/types.yaml#/definitions/uint32`.
Runtime integration is with Linux pinctrl and GPIO framework drivers selected by `compatible`. Board
`.dts` files instantiate nodes that satisfy this schema; `make dt_binding_check` validates the
binding and inline examples, while `make dtbs_check` validates real board descriptions against the
same contract.

## Risks
- A missing or misspelled `compatible` value prevents both schema matching and driver binding.
- Child node regexes and reusable pin configuration schemas are easy to misuse; incorrect group/function names can validate poorly or fail later in driver lookup tables.
- The closed property model catches typos, but any newly needed board property requires a binding update before DTS changes can pass validation.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/maxim,max77620-pinctrl.yaml` to parse this YAML, validate meta-schema rules, and compile its 0 inline example(s).
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/maxim,max77620-pinctrl.yaml` on affected board DTS files to confirm real nodes satisfy required properties, compatible choices, child node names, and referenced common schemas.
- Useful negative tests remove one required property, change `compatible`, add a bogus pin group/function, and add an undeclared property where closure is enabled.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/maxim,max77620-pinctrl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/mediatek,mt65xx-pinctrl.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/mediatek,mt65xx-pinctrl.yaml

## Purpose
This file is a Linux Devicetree JSON-schema document for a pin controller binding: MediaTek MT65xx
Pin Controller. It lives in the pinctrl binding tree and gives dt-schema a machine-readable contract
for board DTS nodes before the kernel pinctrl/GPIO drivers consume those nodes during probe.

The MediaTek's MT65xx Pin controller is used to control SoC pins.

The binding is maintained in-source by Sean Wang <sean.wang@kernel.org>.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/pinctrl/mediatek,mt65xx-pinctrl.yaml#` with meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Compatible contract: `mediatek,mt2701-pinctrl`, `mediatek,mt2712-pinctrl`, `mediatek,mt6397-pinctrl`, `mediatek,mt7623-pinctrl`, `mediatek,mt8127-pinctrl`, `mediatek,mt8135-pinctrl`, `mediatek,mt8167-pinctrl`, `mediatek,mt8173-pinctrl`, `mediatek,mt8516-pinctrl`.
- Required properties: `compatible`, `gpio-controller`, `#gpio-cells`.
- Top-level framework properties: `compatible`, `reg`, `gpio-controller`, `#gpio-cells`, `gpio-line-names`, `interrupt-controller`, `interrupts`, `#interrupt-cells`.
- Vendor or device-specific extensions: `mediatek,pctl-regmap`.
- Other declared top-level properties: `pins-are-numbered`.
- Child-node or reusable schema API: patternProperties `pins$`.
- Property detail signals: compatible (enum `mediatek,mt2701-pinctrl`, `mediatek,mt2712-pinctrl`, `mediatek,mt6397-pinctrl`, `mediatek,mt7623-pinctrl`, `mediatek,mt8127-pinctrl`, `mediatek,mt8135-pinctrl`, `mediatek,mt8167-pinctrl`, `mediatek,mt8173-pinctrl`, ... (9 total)); reg (maxItems 1); pins-are-numbered (Specify the subnodes are using numbered pinmux to specify pins. (UNUSED); ref `/schemas/types.yaml#/definitions/flag`); gpio-controller; #gpio-cells (const `2`; Number of cells in GPIO specifier. Since the generic GPIO binding is used, the amount of cells mu...); gpio-line-names; mediatek,pctl-regmap (maxItems 2; minItems 1; Should be phandles of the syscfg node.; ref `/schemas/types.yaml#/definitions/phandle-array`); interrupt-controller; interrupts (maxItems 3; minItems 1); #interrupt-cells (const `2`).

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
- Schema references: `/schemas/types.yaml#/definitions/flag`, `/schemas/types.yaml#/definitions/phandle-array`, `pinctrl.yaml#`, `/schemas/pinctrl/pincfg-node.yaml`.
- Example/header integration: `dt-bindings/interrupt-controller/irq.h`, `dt-bindings/interrupt-controller/arm-gic.h`, `dt-bindings/pinctrl/mt8135-pinfunc.h`.
- Textual schema references: `/schemas/pinctrl/mediatek,mt65xx-pinctrl.yaml#`, `/schemas/types.yaml#/definitions/flag`, `/schemas/types.yaml#/definitions/phandle-array`, `/schemas/pinctrl/pincfg-node.yaml`.
Runtime integration is with Linux pinctrl and GPIO framework drivers selected by `compatible`. Board
`.dts` files instantiate nodes that satisfy this schema; `make dt_binding_check` validates the
binding and inline examples, while `make dtbs_check` validates real board descriptions against the
same contract.

## Risks
- A missing or misspelled `compatible` value prevents both schema matching and driver binding.
- Omitting required fields such as `compatible`, `gpio-controller`, `#gpio-cells` should fail dt-schema validation before boot.
- Child node regexes and reusable pin configuration schemas are easy to misuse; incorrect group/function names can validate poorly or fail later in driver lookup tables.
- The closed property model catches typos, but any newly needed board property requires a binding update before DTS changes can pass validation.
- GPIO provider fields such as `#gpio-cells`, `gpio-ranges`, and interrupt controller wiring must match the runtime driver's expectations or GPIO consumers will resolve the wrong pins.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/mediatek,mt65xx-pinctrl.yaml` to parse this YAML, validate meta-schema rules, and compile its 1 inline example(s).
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/mediatek,mt65xx-pinctrl.yaml` on affected board DTS files to confirm real nodes satisfy required properties, compatible choices, child node names, and referenced common schemas.
- Useful negative tests remove one required property, change `compatible`, and add an undeclared property where closure is enabled. Example seed: #include <dt-bindings/interrupt-controller/irq.h>; #include <dt-bindings/interrupt-controller/arm-gic.h>; #include <dt-bindings/pinctrl/mt8135-pinfunc.h>; soc {.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/mediatek,mt65xx-pinctrl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/mediatek,mt6779-pinctrl.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/mediatek,mt6779-pinctrl.yaml

## Purpose
This file is a Linux Devicetree JSON-schema document for a pin controller binding: MediaTek MT6779
Pin Controller. It lives in the pinctrl binding tree and gives dt-schema a machine-readable contract
for board DTS nodes before the kernel pinctrl/GPIO drivers consume those nodes during probe.

The MediaTek pin controller on MT6779 is used to control pin functions, pull up/down resistance and
drive strength options.

The binding is maintained in-source by Andy Teng <andy.teng@mediatek.com>, Sean Wang
<sean.wang@kernel.org>.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/pinctrl/mediatek,mt6779-pinctrl.yaml#` with meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Compatible contract: `mediatek,mt6779-pinctrl`, `mediatek,mt6797-pinctrl`.
- Required properties: `compatible`, `reg`, `reg-names`, `gpio-controller`, `#gpio-cells`.
- Top-level framework properties: `compatible`, `reg`, `reg-names`, `gpio-controller`, `#gpio-cells`, `gpio-ranges`, `interrupt-controller`, `interrupts`, `#interrupt-cells`.
- Vendor or device-specific extensions: none declared.
- Other declared top-level properties: none declared.
- Child-node or reusable schema API: patternProperties `-[0-9]*$`.
- Property detail signals: compatible (enum `mediatek,mt6779-pinctrl`, `mediatek,mt6797-pinctrl`); reg (Physical addresses for GPIO base(s) and EINT registers.); reg-names; gpio-controller; #gpio-cells (const `2`; Number of cells in GPIO specifier. Since the generic GPIO binding is used, the amount of cells mu...); gpio-ranges (maxItems 5; minItems 1; GPIO valid number range.); interrupt-controller; interrupts (maxItems 1; Specifies the summary IRQ.); #interrupt-cells (const `2`).

## Control Flow
There is no imperative execution path in this YAML. Validation starts when dt-schema selects this
document for a node whose `compatible` value matches the schema, checks the required list, evaluates
referenced common pinctrl/GPIO schemas, applies property constraints, then walks child-node patterns
and conditional branches.

This file contains 1 `allOf`, 0 `oneOf`, 0 `anyOf`, and 3 `if` blocks. Property closure: top-level
`additionalProperties: false` rejects undeclared properties.

## State and Persistence Behavior
The binding stores no runtime state. It persists as source-controlled schema text, while the state
it describes persists in DTS/DTB data: register windows, GPIO provider cell counts, interrupt
wiring, pin groups, mux functions, drive strengths, pulls, and optional child pin configuration
nodes. Kernel drivers consume the validated DT data at boot or device probe and then program
hardware pin mux, pad, and GPIO state; this YAML only constrains that data before runtime.

## Dependencies and Integration Points
- Schema references: `pinctrl.yaml#`, `/schemas/pinctrl/pincfg-node.yaml`, `/schemas/types.yaml#/definitions/uint32`.
- Example/header integration: `dt-bindings/interrupt-controller/irq.h`, `dt-bindings/interrupt-controller/arm-gic.h`, `dt-bindings/pinctrl/mt6779-pinfunc.h`.
- Textual schema references: `/schemas/pinctrl/mediatek,mt6779-pinctrl.yaml#`, `/schemas/pinctrl/pincfg-node.yaml`, `/schemas/types.yaml#/definitions/uint32`.
Runtime integration is with Linux pinctrl and GPIO framework drivers selected by `compatible`. Board
`.dts` files instantiate nodes that satisfy this schema; `make dt_binding_check` validates the
binding and inline examples, while `make dtbs_check` validates real board descriptions against the
same contract.

## Risks
- A missing or misspelled `compatible` value prevents both schema matching and driver binding.
- Omitting required fields such as `compatible`, `reg`, `reg-names`, `gpio-controller`, `#gpio-cells` should fail dt-schema validation before boot.
- Child node regexes and reusable pin configuration schemas are easy to misuse; incorrect group/function names can validate poorly or fail later in driver lookup tables.
- The closed property model catches typos, but any newly needed board property requires a binding update before DTS changes can pass validation.
- GPIO provider fields such as `#gpio-cells`, `gpio-ranges`, and interrupt controller wiring must match the runtime driver's expectations or GPIO consumers will resolve the wrong pins.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/mediatek,mt6779-pinctrl.yaml` to parse this YAML, validate meta-schema rules, and compile its 1 inline example(s).
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/mediatek,mt6779-pinctrl.yaml` on affected board DTS files to confirm real nodes satisfy required properties, compatible choices, child node names, and referenced common schemas.
- Useful negative tests remove one required property, change `compatible`, and add an undeclared property where closure is enabled. Example seed: #include <dt-bindings/interrupt-controller/irq.h>; #include <dt-bindings/interrupt-controller/arm-gic.h>; #include <dt-bindings/pinctrl/mt6779-pinfunc.h>; soc {.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/mediatek,mt6779-pinctrl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/mediatek,mt6795-pinctrl.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/mediatek,mt6795-pinctrl.yaml

## Purpose
This file is a Linux Devicetree JSON-schema document for a pin controller binding: MediaTek MT6795
Pin Controller. It lives in the pinctrl binding tree and gives dt-schema a machine-readable contract
for board DTS nodes before the kernel pinctrl/GPIO drivers consume those nodes during probe.

The MediaTek's MT6795 Pin controller is used to control SoC pins.

The binding is maintained in-source by AngeloGioacchino Del Regno
<angelogioacchino.delregno@collabora.com>, Sean Wang <sean.wang@kernel.org>.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/pinctrl/mediatek,mt6795-pinctrl.yaml#` with meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Compatible contract: `mediatek,mt6795-pinctrl`.
- Required properties: `compatible`, `reg`, `reg-names`, `interrupts`, `interrupt-controller`, `#interrupt-cells`, `gpio-controller`, `#gpio-cells`, `gpio-ranges`.
- Top-level framework properties: `compatible`, `gpio-controller`, `#gpio-cells`, `gpio-ranges`, `reg`, `reg-names`, `interrupt-controller`, `#interrupt-cells`, `interrupts`.
- Vendor or device-specific extensions: none declared.
- Other declared top-level properties: none declared.
- Child-node or reusable schema API: patternProperties `-pins$`.
- Property detail signals: compatible (const `mediatek,mt6795-pinctrl`); gpio-controller; #gpio-cells (const `2`; Number of cells in GPIO specifier. Since the generic GPIO binding is used, the amount of cells mu...); gpio-ranges (maxItems 1; GPIO valid number range.); reg (minItems 2; Physical address base for GPIO base and eint registers.); reg-names; interrupt-controller; #interrupt-cells (const `2`); interrupts (minItems 1; Interrupt outputs to the system interrupt controller (sysirq).).

## Control Flow
There is no imperative execution path in this YAML. Validation starts when dt-schema selects this
document for a node whose `compatible` value matches the schema, checks the required list, evaluates
referenced common pinctrl/GPIO schemas, applies property constraints, then walks child-node patterns
and conditional branches.

This file contains 1 `allOf`, 2 `oneOf`, 0 `anyOf`, and 0 `if` blocks. Property closure: top-level
`additionalProperties: false` rejects undeclared properties.

## State and Persistence Behavior
The binding stores no runtime state. It persists as source-controlled schema text, while the state
it describes persists in DTS/DTB data: register windows, GPIO provider cell counts, interrupt
wiring, pin groups, mux functions, drive strengths, pulls, and optional child pin configuration
nodes. Kernel drivers consume the validated DT data at boot or device probe and then program
hardware pin mux, pad, and GPIO state; this YAML only constrains that data before runtime.

## Dependencies and Integration Points
- Schema references: `pinmux-node.yaml`, `/schemas/types.yaml#/definitions/uint32`, `pinctrl.yaml#`.
- Example/header integration: `dt-bindings/interrupt-controller/arm-gic.h`, `dt-bindings/interrupt-controller/irq.h`, `dt-bindings/pinctrl/mt6795-pinfunc.h`.
- Textual schema references: `/schemas/pinctrl/mediatek,mt6795-pinctrl.yaml#`, `/schemas/types.yaml#/definitions/uint32`.
Runtime integration is with Linux pinctrl and GPIO framework drivers selected by `compatible`. Board
`.dts` files instantiate nodes that satisfy this schema; `make dt_binding_check` validates the
binding and inline examples, while `make dtbs_check` validates real board descriptions against the
same contract.

## Risks
- A missing or misspelled `compatible` value prevents both schema matching and driver binding.
- Omitting required fields such as `compatible`, `reg`, `reg-names`, `interrupts`, `interrupt-controller` should fail dt-schema validation before boot.
- Child node regexes and reusable pin configuration schemas are easy to misuse; incorrect group/function names can validate poorly or fail later in driver lookup tables.
- The closed property model catches typos, but any newly needed board property requires a binding update before DTS changes can pass validation.
- GPIO provider fields such as `#gpio-cells`, `gpio-ranges`, and interrupt controller wiring must match the runtime driver's expectations or GPIO consumers will resolve the wrong pins.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/mediatek,mt6795-pinctrl.yaml` to parse this YAML, validate meta-schema rules, and compile its 1 inline example(s).
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/mediatek,mt6795-pinctrl.yaml` on affected board DTS files to confirm real nodes satisfy required properties, compatible choices, child node names, and referenced common schemas.
- Useful negative tests remove one required property, change `compatible`, and add an undeclared property where closure is enabled. Example seed: #include <dt-bindings/interrupt-controller/arm-gic.h>; #include <dt-bindings/interrupt-controller/irq.h>; #include <dt-bindings/pinctrl/mt6795-pinfunc.h>; soc {.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/mediatek,mt6795-pinctrl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/mediatek,mt6878-pinctrl.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/mediatek,mt6878-pinctrl.yaml

## Purpose
This file is a Linux Devicetree JSON-schema document for a pin controller binding: MediaTek MT6878
Pin Controller. It lives in the pinctrl binding tree and gives dt-schema a machine-readable contract
for board DTS nodes before the kernel pinctrl/GPIO drivers consume those nodes during probe.

The MediaTek MT6878 Pin controller is used to control SoC pins.

The binding is maintained in-source by AngeloGioacchino Del Regno
<angelogioacchino.delregno@collabora.com>, Igor Belwon <igor.belwon@mentallysanemainliners.org>.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/pinctrl/mediatek,mt6878-pinctrl.yaml#` with meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Compatible contract: `mediatek,mt6878-pinctrl`.
- Required properties: `compatible`, `reg`, `interrupts`, `interrupt-controller`, `#interrupt-cells`, `gpio-controller`, `#gpio-cells`, `gpio-ranges`.
- Top-level framework properties: `compatible`, `reg`, `reg-names`, `gpio-controller`, `#gpio-cells`, `gpio-ranges`, `gpio-line-names`, `interrupts`, `interrupt-controller`, `#interrupt-cells`.
- Vendor or device-specific extensions: none declared.
- Other declared top-level properties: none declared.
- Child-node or reusable schema API: patternProperties `-pins$`.
- Property detail signals: compatible (const `mediatek,mt6878-pinctrl`); reg; reg-names; gpio-controller; #gpio-cells (const `2`; Number of cells in GPIO specifier. Since the generic GPIO binding is used, the amount of cells mu...); gpio-ranges (maxItems 1); gpio-line-names (maxItems 216); interrupts (maxItems 1; The interrupt outputs to sysirq); interrupt-controller; #interrupt-cells (const `2`).

## Control Flow
There is no imperative execution path in this YAML. Validation starts when dt-schema selects this
document for a node whose `compatible` value matches the schema, checks the required list, evaluates
referenced common pinctrl/GPIO schemas, applies property constraints, then walks child-node patterns
and conditional branches.

This file contains 1 `allOf`, 2 `oneOf`, 0 `anyOf`, and 0 `if` blocks. Property closure: top-level
`additionalProperties: false` rejects undeclared properties.

## State and Persistence Behavior
The binding stores no runtime state. It persists as source-controlled schema text, while the state
it describes persists in DTS/DTB data: register windows, GPIO provider cell counts, interrupt
wiring, pin groups, mux functions, drive strengths, pulls, and optional child pin configuration
nodes. Kernel drivers consume the validated DT data at boot or device probe and then program
hardware pin mux, pad, and GPIO state; this YAML only constrains that data before runtime.

## Dependencies and Integration Points
- Schema references: `/schemas/pinctrl/pincfg-node.yaml`, `/schemas/pinctrl/pinmux-node.yaml`.
- Example/header integration: `dt-bindings/interrupt-controller/arm-gic.h`, `dt-bindings/pinctrl/mt65xx.h`.
- Textual schema references: `/schemas/pinctrl/mediatek,mt6878-pinctrl.yaml#`, `/schemas/pinctrl/pincfg-node.yaml`, `/schemas/pinctrl/pinmux-node.yaml`.
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
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/mediatek,mt6878-pinctrl.yaml` to parse this YAML, validate meta-schema rules, and compile its 1 inline example(s).
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/mediatek,mt6878-pinctrl.yaml` on affected board DTS files to confirm real nodes satisfy required properties, compatible choices, child node names, and referenced common schemas.
- Useful negative tests remove one required property, change `compatible`, and add an undeclared property where closure is enabled. Example seed: #include <dt-bindings/interrupt-controller/arm-gic.h>; #include <dt-bindings/pinctrl/mt65xx.h>; #define PINMUX_GPIO0__FUNC_GPIO0 (MTK_PIN_NO(0) | 0); #define PINMUX_GPIO99__FUNC_SCL0 (MTK_PIN_NO(99) | 1); #define PINMUX_GPIO100__FUNC_SDA0 (MTK_PIN_NO(100) | 1).

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/mediatek,mt6878-pinctrl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/mediatek,mt6893-pinctrl.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/mediatek,mt6893-pinctrl.yaml

## Purpose
This file is a Linux Devicetree JSON-schema document for a pin controller binding: MediaTek MT6893
Pin Controller. It lives in the pinctrl binding tree and gives dt-schema a machine-readable contract
for board DTS nodes before the kernel pinctrl/GPIO drivers consume those nodes during probe.

The MediaTek's MT6893 Pin controller is used to control SoC pins.

The binding is maintained in-source by AngeloGioacchino Del Regno
<angelogioacchino.delregno@collabora.com>.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/pinctrl/mediatek,mt6893-pinctrl.yaml#` with meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Compatible contract: `mediatek,mt6893-pinctrl`.
- Required properties: `compatible`, `reg`, `interrupts`, `interrupt-controller`, `#interrupt-cells`, `gpio-controller`, `#gpio-cells`, `gpio-ranges`.
- Top-level framework properties: `compatible`, `reg`, `reg-names`, `gpio-controller`, `#gpio-cells`, `gpio-ranges`, `gpio-line-names`, `interrupts`, `interrupt-controller`, `#interrupt-cells`.
- Vendor or device-specific extensions: none declared.
- Other declared top-level properties: none declared.
- Child-node or reusable schema API: patternProperties `-pins$`.
- Property detail signals: compatible (const `mediatek,mt6893-pinctrl`); reg; reg-names; gpio-controller; #gpio-cells (const `2`; Number of cells in GPIO specifier. Since the generic GPIO binding is used, the amount of cells mu...); gpio-ranges (maxItems 1); gpio-line-names; interrupts (maxItems 1; The interrupt outputs to sysirq); interrupt-controller; #interrupt-cells (const `2`).

## Control Flow
There is no imperative execution path in this YAML. Validation starts when dt-schema selects this
document for a node whose `compatible` value matches the schema, checks the required list, evaluates
referenced common pinctrl/GPIO schemas, applies property constraints, then walks child-node patterns
and conditional branches.

This file contains 1 `allOf`, 2 `oneOf`, 0 `anyOf`, and 0 `if` blocks. Property closure: top-level
`additionalProperties: false` rejects undeclared properties.

## State and Persistence Behavior
The binding stores no runtime state. It persists as source-controlled schema text, while the state
it describes persists in DTS/DTB data: register windows, GPIO provider cell counts, interrupt
wiring, pin groups, mux functions, drive strengths, pulls, and optional child pin configuration
nodes. Kernel drivers consume the validated DT data at boot or device probe and then program
hardware pin mux, pad, and GPIO state; this YAML only constrains that data before runtime.

## Dependencies and Integration Points
- Schema references: `/schemas/pinctrl/pincfg-node.yaml`, `/schemas/pinctrl/pinmux-node.yaml`.
- Example/header integration: `dt-bindings/interrupt-controller/arm-gic.h`, `dt-bindings/pinctrl/mt65xx.h`.
- Textual schema references: `/schemas/pinctrl/mediatek,mt6893-pinctrl.yaml#`, `/schemas/pinctrl/pincfg-node.yaml`, `/schemas/pinctrl/pinmux-node.yaml`.
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
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/mediatek,mt6893-pinctrl.yaml` to parse this YAML, validate meta-schema rules, and compile its 1 inline example(s).
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/mediatek,mt6893-pinctrl.yaml` on affected board DTS files to confirm real nodes satisfy required properties, compatible choices, child node names, and referenced common schemas.
- Useful negative tests remove one required property, change `compatible`, and add an undeclared property where closure is enabled. Example seed: #include <dt-bindings/interrupt-controller/arm-gic.h>; #include <dt-bindings/pinctrl/mt65xx.h>; #define PINMUX_GPIO0__FUNC_GPIO0 (MTK_PIN_NO(0) | 0); #define PINMUX_GPIO99__FUNC_SCL0 (MTK_PIN_NO(99) | 1); #define PINMUX_GPIO100__FUNC_SDA0 (MTK_PIN_NO(100) | 1).

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/mediatek,mt6893-pinctrl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/mediatek,mt7620-pinctrl.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/mediatek,mt7620-pinctrl.yaml

## Purpose
This file is a Linux Devicetree JSON-schema document for a pin controller binding: MediaTek MT7620
Pin Controller. It lives in the pinctrl binding tree and gives dt-schema a machine-readable contract
for board DTS nodes before the kernel pinctrl/GPIO drivers consume those nodes during probe.

MediaTek MT7620 pin controller for MT7620 SoC. The pin controller can only set the muxing of pin
groups. Muxing individual pins is not supported. There is no pinconf support.

The binding is maintained in-source by Arınç ÜNAL <arinc.unal@arinc9.com>, Sergio Paracuellos
<sergio.paracuellos@gmail.com>.

## Important APIs, Types, and Functions
- Schema identity: `$id` `http://devicetree.org/schemas/pinctrl/mediatek,mt7620-pinctrl.yaml#` with meta-schema `http://devicetree.org/meta-schemas/core.yaml#`.
- Compatible contract: `ralink,mt7620-pinctrl`.
- Required properties: `compatible`.
- Top-level framework properties: `compatible`.
- Vendor or device-specific extensions: none declared.
- Other declared top-level properties: none declared.
- Child-node or reusable schema API: patternProperties `-pins$`.
- Property detail signals: compatible (const `ralink,mt7620-pinctrl`).

## Control Flow
There is no imperative execution path in this YAML. Validation starts when dt-schema selects this
document for a node whose `compatible` value matches the schema, checks the required list, evaluates
referenced common pinctrl/GPIO schemas, applies property constraints, then walks child-node patterns
and conditional branches.

This file contains 2 `allOf`, 0 `oneOf`, 0 `anyOf`, and 25 `if` blocks. Property closure: top-level
`additionalProperties: false` rejects undeclared properties.

## State and Persistence Behavior
The binding stores no runtime state. It persists as source-controlled schema text, while the state
it describes persists in DTS/DTB data: register windows, GPIO provider cell counts, interrupt
wiring, pin groups, mux functions, drive strengths, pulls, and optional child pin configuration
nodes. Kernel drivers consume the validated DT data at boot or device probe and then program
hardware pin mux, pad, and GPIO state; this YAML only constrains that data before runtime.

## Dependencies and Integration Points
- Schema references: `pinmux-node.yaml#`, `pinctrl.yaml#`.
- Textual schema references: `/schemas/pinctrl/mediatek,mt7620-pinctrl.yaml#`.
Runtime integration is with Linux pinctrl and GPIO framework drivers selected by `compatible`. Board
`.dts` files instantiate nodes that satisfy this schema; `make dt_binding_check` validates the
binding and inline examples, while `make dtbs_check` validates real board descriptions against the
same contract.

## Risks
- A missing or misspelled `compatible` value prevents both schema matching and driver binding.
- Omitting required fields such as `compatible` should fail dt-schema validation before boot.
- Child node regexes and reusable pin configuration schemas are easy to misuse; incorrect group/function names can validate poorly or fail later in driver lookup tables.
- The closed property model catches typos, but any newly needed board property requires a binding update before DTS changes can pass validation.

## Test Signals
- Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/mediatek,mt7620-pinctrl.yaml` to parse this YAML, validate meta-schema rules, and compile its 1 inline example(s).
- Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/mediatek,mt7620-pinctrl.yaml` on affected board DTS files to confirm real nodes satisfy required properties, compatible choices, child node names, and referenced common schemas.
- Useful negative tests remove one required property, change `compatible`, and add an undeclared property where closure is enabled. Example seed: pinctrl {; compatible = "ralink,mt7620-pinctrl";; i2c_pins: i2c0-pins {; pinmux {.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/mediatek,mt7620-pinctrl.yaml -->
