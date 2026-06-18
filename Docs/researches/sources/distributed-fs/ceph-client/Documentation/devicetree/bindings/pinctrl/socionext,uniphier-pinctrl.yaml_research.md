# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/socionext,uniphier-pinctrl.yaml

## Purpose
This schema describes Socionext UniPhier pin controllers. It uses standard pinmux and pinconf child nodes and a broad compatible enum across UniPhier SoC generations. Source title: UniPhier SoCs pin controller. Description signal from the file: No long-form description is present; the binding contract is carried by the schema properties and examples.

## Important APIs, Types, and Schema Surface
- Lines read: 84.
- Compatible contract: socionext,uniphier-ld4-pinctrl, socionext,uniphier-pro4-pinctrl, socionext,uniphier-sld8-pinctrl, socionext,uniphier-pro5-pinctrl, socionext,uniphier-pxs2-pinctrl, socionext,uniphier-ld6b-pinctrl, socionext,uniphier-ld11-pinctrl, socionext,uniphier-ld20-pinctrl, socionext,uniphier-pxs3-pinctrl, socionext,uniphier-nx1-pinctrl. Top-level required properties: compatible. Important top-level properties found in the schema: None declared in this schema. Child-node patterns: None declared in this schema. Referenced schemas: pincfg-node.yaml#, pinmux-node.yaml#, pinctrl.yaml#.

## Control Flow
Validation selects one UniPhier compatible and uses standard pinctrl, pinmux, and pinconf schema composition for child state nodes. The binding is intentionally compact, leaving SoC-specific pin/function tables to the driver and DTS conventions.

## State and Persistence Behavior
Persistent ABI is the compatible string and child state format. There is no stateful data in the schema beyond accepted DTS property names and values.

## Dependencies and Integration Points
This schema is consumed by Linux devicetree validation tooling (`dt-schema`), board DTS files under architecture trees, and the matching kernel pinctrl/GPIO/interrupt driver. Integration points include `pinctrl.yaml`, generic `pinmux-node.yaml`/`pincfg-node.yaml`, vendor common schemas, dt-bindings headers, GPIO and interrupt-controller bindings, and SoC clock/reset/power-domain providers where referenced.

## Risks and Edge Cases
The broad compatible enum must stay aligned with driver support. Overly permissive child properties could hide invalid board states until runtime.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/pinctrl/socionext,uniphier-pinctrl.yaml` and at least one `make dtbs_check` target containing a DTS user of the compatible. For shared helper schemas, run the top-level importing bindings as well. Review the in-file example because it exercises required properties, child-node shape, and referenced dt-bindings constants.
