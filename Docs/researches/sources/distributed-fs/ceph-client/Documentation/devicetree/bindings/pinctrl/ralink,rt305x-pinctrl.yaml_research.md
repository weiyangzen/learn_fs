# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/ralink,rt305x-pinctrl.yaml

## Purpose
This schema documents an older Ralink SoC pin controller that only selects mux functions at group granularity. It intentionally excludes per-pin muxing and pinconf support, so its binding surface is small but its group/function enum is hardware-specific. Source title: Ralink RT305X Pin Controller. Description signal from the file: Ralink RT305X pin controller for RT3050, RT3052, and RT3350 SoCs. The pin controller can only set the muxing of pin groups. Muxing individual pins is not supported. There is no pinconf support.

## Important APIs, Types, and Schema Surface
- Lines read: 206.
- Compatible contract: ralink,rt305x-pinctrl. Top-level required properties: compatible. Important top-level properties found in the schema: None declared in this schema. Child-node patterns: -pins$. Function enum sample: gpio, gpio i2s, gpio uartf, i2c, i2s uartf, jtag, mdio, pcm gpio, pcm i2s, pcm uartf, rgmii, sdram, spi, uartf, uartlite. Referenced schemas: pinmux-node.yaml#, pinctrl.yaml#.

## Control Flow
Validation checks the Ralink compatible, then validates child mux nodes against `pinmux-node.yaml`. Function and group selections are enum-constrained; the schemas intentionally omit generic pinconf properties because the hardware binding only models group muxing.

## State and Persistence Behavior
The persistent ABI is the list of group and function strings used by DTS files. No mutable runtime state is represented in YAML; the pinctrl driver applies the mux selections during device probe and state activation.

## Dependencies and Integration Points
This schema is consumed by Linux devicetree validation tooling (`dt-schema`), board DTS files under architecture trees, and the matching kernel pinctrl/GPIO/interrupt driver. Integration points include `pinctrl.yaml`, generic `pinmux-node.yaml`/`pincfg-node.yaml`, vendor common schemas, dt-bindings headers, GPIO and interrupt-controller bindings, and SoC clock/reset/power-domain providers where referenced.

## Risks and Edge Cases
The main risk is making the schema look more capable than the hardware by accepting per-pin or pinconf properties. Group/function enum drift can also cause board DTS files to validate but fail to select the intended mux.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/pinctrl/ralink,rt305x-pinctrl.yaml` and at least one `make dtbs_check` target containing a DTS user of the compatible. For shared helper schemas, run the top-level importing bindings as well. Review the in-file example because it exercises required properties, child-node shape, and referenced dt-bindings constants.
