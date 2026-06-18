# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/samsung,pinctrl-gpio-bank.yaml

## Purpose
This helper schema describes a Samsung pin controller GPIO bank child. It supplies the bank-level GPIO and interrupt provider contract that the top-level Samsung binding references. Source title: Samsung S3C/S5P/Exynos SoC pin controller - gpio bank. Description signal from the file: This is a part of device tree bindings for Samsung S3C/S5P/Exynos SoC pin controller. GPIO bank description for Samsung S3C/S5P/Exynos SoC pin controller. See also Documentation/devicetree/bindings/pinctrl/samsung,pinctrl.yaml for additional information and example.

## Important APIs, Types, and Schema Surface
- Lines read: 52.
- Compatible contract: None declared in this schema. Top-level required properties: #gpio-cells, gpio-controller. Important top-level properties found in the schema: interrupts, gpio-controller, interrupt-controller, #gpio-cells, #interrupt-cells. Child-node patterns: None declared in this schema. Referenced schemas: None declared in this schema.

## Control Flow
This helper schema is not normally used alone; it is pulled into the top-level Samsung binding through `$ref`. dt-schema evaluates it when a matching GPIO-bank child node appears under a Samsung pin controller.

## State and Persistence Behavior
Persistent ABI is the child-node property set referenced by Samsung board files. The helper has no runtime state but determines what bank child nodes are accepted.

## Dependencies and Integration Points
This schema is consumed by Linux devicetree validation tooling (`dt-schema`), board DTS files under architecture trees, and the matching kernel pinctrl/GPIO/interrupt driver. Integration points include `pinctrl.yaml`, generic `pinmux-node.yaml`/`pincfg-node.yaml`, vendor common schemas, dt-bindings headers, GPIO and interrupt-controller bindings, and SoC clock/reset/power-domain providers where referenced.

## Risks and Edge Cases
Because this helper is shared, incompatible changes can break many Samsung DTS files. Keep property names and cardinality aligned with the top-level schema and Samsung pinctrl driver expectations.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/pinctrl/samsung,pinctrl-gpio-bank.yaml` and at least one `make dtbs_check` target containing a DTS user of the compatible. For shared helper schemas, run the top-level importing bindings as well. Review the in-file example because it exercises required properties, child-node shape, and referenced dt-bindings constants.
