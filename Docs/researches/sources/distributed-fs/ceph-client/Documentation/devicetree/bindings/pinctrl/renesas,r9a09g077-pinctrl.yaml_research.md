# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/renesas,r9a09g077-pinctrl.yaml

## Purpose
This schema describes a Renesas combined pin and GPIO or PFC block. It validates compatible-specific controller resources plus child pinmux/pinconf nodes that encode port, pin, and alternate-function selections. Source title: Renesas RZ/T2H and RZ/N2H Pin and GPIO controller. Description signal from the file: The Renesas RZ/T2H and RZ/N2H SoCs feature a combined Pin and GPIO controller. Pin multiplexing and GPIO configuration are performed on a per-pin basis. Each port supports up to 8 pins, each configurable for either GPIO (port mode) or alternate function mode. Each pin supports function mode values ranging from 0x0 to 0x2A, allowing selection from up to 43 different functions.

## Important APIs, Types, and Schema Surface
- Lines read: 202.
- Compatible contract: renesas,r9a09g077-pinctrl, renesas,r9a09g087-pinctrl. Top-level required properties: compatible, reg, reg-names, gpio-controller, #gpio-cells, gpio-ranges, clocks, power-domains. Important top-level properties found in the schema: reg, clocks, power-domains, gpio-controller, interrupt-controller, #gpio-cells, #interrupt-cells, gpio-ranges. Child-node patterns: -pins$. Referenced schemas: pincfg-node.yaml#, pinmux-node.yaml#, #/definitions/renesas-rzt2h-n2h-pins-node, pinctrl.yaml#.

## Control Flow
Validation starts with compatible-specific resources, then uses nested child objects for pinmux and pin configuration. Most Renesas bindings compose generic `pincfg-node.yaml`, `pinmux-node.yaml`, and `pinctrl.yaml`, with helper macros in dt-bindings headers encoding port/pin/function values.

## State and Persistence Behavior
Persistent state is the controller resource set, GPIO/interrupt provider shape where present, and the encoded pinmux values used by client pinctrl states. The YAML has no runtime storage but is a stable ABI for Renesas board DTS files.

## Dependencies and Integration Points
This schema is consumed by Linux devicetree validation tooling (`dt-schema`), board DTS files under architecture trees, and the matching kernel pinctrl/GPIO/interrupt driver. Integration points include `pinctrl.yaml`, generic `pinmux-node.yaml`/`pincfg-node.yaml`, vendor common schemas, dt-bindings headers, GPIO and interrupt-controller bindings, and SoC clock/reset/power-domain providers where referenced.

## Risks and Edge Cases
Risks concentrate around reset/clock requirements, GPIO cell semantics, and SoC-specific port encoding. Conditional compatible fallbacks and allowed electrical values should be tested with representative DTS examples and driver tables.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/pinctrl/renesas,r9a09g077-pinctrl.yaml` and at least one `make dtbs_check` target containing a DTS user of the compatible. For shared helper schemas, run the top-level importing bindings as well. Review the in-file example because it exercises required properties, child-node shape, and referenced dt-bindings constants.
