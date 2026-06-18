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
