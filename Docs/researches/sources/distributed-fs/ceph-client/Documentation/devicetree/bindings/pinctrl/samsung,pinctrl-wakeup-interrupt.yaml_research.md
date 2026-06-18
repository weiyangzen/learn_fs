# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/samsung,pinctrl-wakeup-interrupt.yaml

## Purpose
This helper schema describes Samsung external wake-up interrupt controller children. It validates SoC-specific wake-up interrupt compatible strings and interrupt wiring for suspend/resume wake paths. Source title: Samsung S3C/S5P/Exynos SoC pin controller - wake-up interrupt controller. Description signal from the file: This is a part of device tree bindings for Samsung S3C/S5P/Exynos SoC pin controller. External wake-up interrupts for Samsung S3C/S5P/Exynos SoC pin controller. For S3C24xx, S3C64xx, S5PV210 and Exynos4210 compatible wake-up interrupt controllers, only one pin-controller device node can include external wake-up interrupts child node (in other words, only one External wake-up interrupts pin-controller is supported). For newer controllers, multiple

## Important APIs, Types, and Schema Surface
- Lines read: 116.
- Compatible contract: samsung,s3c64xx-wakeup-eint, samsung,s5pv210-wakeup-eint, samsung,exynos4210-wakeup-eint, samsung,exynos7-wakeup-eint, samsung,exynosautov920-wakeup-eint, samsung,exynos5433-wakeup-eint, samsung,exynos7870-wakeup-eint, samsung,exynos7885-wakeup-eint, samsung,exynos850-wakeup-eint, samsung,exynos8890-wakeup-eint plus 7 more. Top-level required properties: compatible. Important top-level properties found in the schema: interrupts. Child-node patterns: None declared in this schema. Referenced schemas: None declared in this schema.

## Control Flow
This helper schema is not normally used alone; it is pulled into the top-level Samsung binding through `$ref`. dt-schema evaluates it when a wake-up interrupt controller child appears under a Samsung pin controller.

## State and Persistence Behavior
Persistent ABI is the child-node property set referenced by Samsung board files. The helper has no runtime state but determines what wake-up interrupt controller nodes are accepted.

## Dependencies and Integration Points
This schema is consumed by Linux devicetree validation tooling (`dt-schema`), board DTS files under architecture trees, and the matching kernel pinctrl/GPIO/interrupt driver. Integration points include `pinctrl.yaml`, generic `pinmux-node.yaml`/`pincfg-node.yaml`, vendor common schemas, dt-bindings headers, GPIO and interrupt-controller bindings, and SoC clock/reset/power-domain providers where referenced.

## Risks and Edge Cases
Because this helper is shared, incompatible changes can break many Samsung DTS files. Keep compatible strings and interrupt cardinality aligned with wake-up interrupt driver expectations.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/pinctrl/samsung,pinctrl-wakeup-interrupt.yaml` and at least one `make dtbs_check` target containing a DTS user of the compatible. For shared helper schemas, run the top-level importing bindings as well. Review the in-file example because it exercises required properties, child-node shape, and referenced dt-bindings constants.
