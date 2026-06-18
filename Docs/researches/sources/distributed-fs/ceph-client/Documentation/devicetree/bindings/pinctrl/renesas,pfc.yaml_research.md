# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/renesas,pfc.yaml

## Purpose
This schema describes a Renesas combined pin and GPIO or PFC block. It validates compatible-specific controller resources plus child pinmux/pinconf nodes that encode port, pin, and alternate-function selections. Source title: Renesas Pin Function Controller (GPIO and Pin Mux/Config). Description signal from the file: The Pin Function Controller (PFC) is a Pin Mux/Config controller. On SH/R-Mobile SoCs it also acts as a GPIO controller.

## Important APIs, Types, and Schema Surface
- Lines read: 196.
- Compatible contract: renesas,pfc-emev2, renesas,pfc-r8a73a4, renesas,pfc-r8a7740, renesas,pfc-r8a7742, renesas,pfc-r8a7743, renesas,pfc-r8a7744, renesas,pfc-r8a7745, renesas,pfc-r8a77470, renesas,pfc-r8a774a1, renesas,pfc-r8a774a3 plus 23 more. Top-level required properties: compatible, reg. Important top-level properties found in the schema: reg, interrupts-extended, power-domains, gpio-controller, #gpio-cells, gpio-ranges. Child-node patterns: None declared in this schema. Referenced schemas: pinctrl.yaml#, pincfg-node.yaml#, pinmux-node.yaml#, #/additionalProperties/anyOf/0.

## Control Flow
Validation starts with compatible-specific resources, then uses nested child objects for pinmux and pin configuration. Most Renesas bindings compose generic `pincfg-node.yaml`, `pinmux-node.yaml`, and `pinctrl.yaml`, with helper macros in dt-bindings headers encoding port/pin/function values.

## State and Persistence Behavior
Persistent state is the controller resource set, GPIO/interrupt provider shape where present, and the encoded pinmux values used by client pinctrl states. The YAML has no runtime storage but is a stable ABI for Renesas board DTS files.

## Dependencies and Integration Points
This schema is consumed by Linux devicetree validation tooling (`dt-schema`), board DTS files under architecture trees, and the matching kernel pinctrl/GPIO/interrupt driver. Integration points include `pinctrl.yaml`, generic `pinmux-node.yaml`/`pincfg-node.yaml`, vendor common schemas, dt-bindings headers, GPIO and interrupt-controller bindings, and SoC clock/reset/power-domain providers where referenced.

## Risks and Edge Cases
Risks concentrate around reset/clock requirements, GPIO cell semantics, and SoC-specific port encoding. Conditional compatible fallbacks and allowed electrical values should be tested with representative DTS examples and driver tables.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/pinctrl/renesas,pfc.yaml` and at least one `make dtbs_check` target containing a DTS user of the compatible. For shared helper schemas, run the top-level importing bindings as well. Review the in-file example because it exercises required properties, child-node shape, and referenced dt-bindings constants.
