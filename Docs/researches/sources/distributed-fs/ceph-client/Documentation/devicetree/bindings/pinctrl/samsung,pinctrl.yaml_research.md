# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/samsung,pinctrl.yaml

## Purpose
This top-level Samsung schema validates S3C/S5P/Exynos-style pin controller nodes, GPIO bank children, pin configuration states, and optional wake-up interrupt controller children. Source title: Samsung S3C/S5P/Exynos SoC pin controller. Description signal from the file: This is a part of device tree bindings for Samsung S3C/S5P/Exynos SoC pin controller. All the pin controller nodes should be represented in the aliases node using the following format 'pinctrl{n}' where n is a unique number for the alias. - External GPIO interrupts (see interrupts property in pin controller node); - External wake-up interrupts - multiplexed (capable of waking up the system see interrupts property in external wake-up interrupt con

## Important APIs, Types, and Schema Surface
- Lines read: 418.
- Compatible contract: axis,artpec8-pinctrl, axis,artpec9-pinctrl, google,gs101-pinctrl, samsung,s3c64xx-pinctrl, samsung,s5pv210-pinctrl, samsung,exynos2200-pinctrl, samsung,exynos3250-pinctrl, samsung,exynos4210-pinctrl, samsung,exynos4x12-pinctrl, samsung,exynos5250-pinctrl plus 17 more. Top-level required properties: compatible, reg. Important top-level properties found in the schema: reg, interrupts, clocks, clock-names, power-domains, wakeup-interrupt-controller. Child-node patterns: ^[a-z]+[0-9]*-gpio-bank$, ^[a-z0-9-]+-pins$, ^(initial|sleep)-state$. Referenced schemas: samsung,pinctrl-wakeup-interrupt.yaml, samsung,pinctrl-gpio-bank.yaml, samsung,pinctrl-pins-cfg.yaml, /schemas/types.yaml#/definitions/string-array, pinctrl.yaml#.

## Control Flow
Validation checks the top-level compatible and register resources, dispatches GPIO bank child nodes to `samsung,pinctrl-gpio-bank.yaml`, pin states to `samsung,pinctrl-pins-cfg.yaml`, and wake-up interrupt controller children to `samsung,pinctrl-wakeup-interrupt.yaml`. Conditional branches require clocks only for selected compatibles and constrain `reg` count.

## State and Persistence Behavior
The binding persists alias numbering expectations, bank child layout, pin state names, wake-up interrupt controller shape, and compatible-specific resource requirements for Samsung-family DTS files.

## Dependencies and Integration Points
This schema is consumed by Linux devicetree validation tooling (`dt-schema`), board DTS files under architecture trees, and the matching kernel pinctrl/GPIO/interrupt driver. Integration points include `pinctrl.yaml`, generic `pinmux-node.yaml`/`pincfg-node.yaml`, vendor common schemas, dt-bindings headers, GPIO and interrupt-controller bindings, and SoC clock/reset/power-domain providers where referenced.

## Risks and Edge Cases
Wake-up interrupt topology and bank naming are the sensitive areas. A schema edit that accepts the wrong bank node name or misses clock gating on GS101/Exynos8890 can validate DTS that the driver cannot initialize correctly.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/pinctrl/samsung,pinctrl.yaml` and at least one `make dtbs_check` target containing a DTS user of the compatible. For shared helper schemas, run the top-level importing bindings as well. Review the in-file example because it exercises required properties, child-node shape, and referenced dt-bindings constants.
