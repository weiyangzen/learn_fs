# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/samsung,pinctrl-pins-cfg.yaml

## Purpose
This helper schema describes Samsung pin configuration nodes. It validates the `samsung,pins` array and Samsung-specific function, pull, drive, and pull-up/down strength properties. Source title: Samsung S3C/S5P/Exynos SoC pin controller - pins configuration. Description signal from the file: This is a part of device tree bindings for Samsung S3C/S5P/Exynos SoC pin controller. Pins configuration for Samsung S3C/S5P/Exynos SoC pin controller. The values used for config properties should be derived from the hardware manual and these values are programmed as-is into the pin pull up/down and driver strength register of the pin-controller. See also Documentation/devicetree/bindings/pinctrl/samsung,pinctrl.yaml for additional information an

## Important APIs, Types, and Schema Surface
- Lines read: 80.
- Compatible contract: samsung,pins. Top-level required properties: samsung,pins. Important top-level properties found in the schema: None declared in this schema. Child-node patterns: None declared in this schema. Referenced schemas: /schemas/types.yaml#/definitions/string-array, /schemas/types.yaml#/definitions/uint32.

## Control Flow
This helper schema is not normally used alone; it is pulled into the top-level Samsung binding through `$ref`. dt-schema evaluates it when a matching pin configuration child node appears under a Samsung pin controller.

## State and Persistence Behavior
Persistent ABI is the child-node property set referenced by Samsung board files. The helper has no runtime state but determines what pin configuration nodes are accepted.

## Dependencies and Integration Points
This schema is consumed by Linux devicetree validation tooling (`dt-schema`), board DTS files under architecture trees, and the matching kernel pinctrl/GPIO/interrupt driver. Integration points include `pinctrl.yaml`, generic `pinmux-node.yaml`/`pincfg-node.yaml`, vendor common schemas, dt-bindings headers, GPIO and interrupt-controller bindings, and SoC clock/reset/power-domain providers where referenced.

## Risks and Edge Cases
Because this helper is shared, incompatible changes can break many Samsung DTS files. Keep property names and cardinality aligned with the top-level schema and Samsung pinctrl driver expectations.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/pinctrl/samsung,pinctrl-pins-cfg.yaml` and at least one `make dtbs_check` target containing a DTS user of the compatible. For shared helper schemas, run the top-level importing bindings as well. Review the in-file example because it exercises required properties, child-node shape, and referenced dt-bindings constants.
