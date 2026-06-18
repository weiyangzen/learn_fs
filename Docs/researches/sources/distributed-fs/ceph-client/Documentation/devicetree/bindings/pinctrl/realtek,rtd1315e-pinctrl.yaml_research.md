# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/realtek,rtd1315e-pinctrl.yaml

## Purpose
This schema describes a Realtek DHC media SoC pin controller. It validates function mux selection, pin lists, pull settings, drive strength, Schmitt trigger controls, voltage selection, and vendor-specific electrical tuning fields where supported. Source title: Realtek DHC RTD1315E Pin Controller. Description signal from the file: The Realtek DHC RTD1315E is a high-definition media processor SoC. The RTD1315E pin controller is used to control pin function, pull up/down resistor, drive strength, schmitt trigger and power source.

## Important APIs, Types, and Schema Surface
- Lines read: 191.
- Compatible contract: realtek,rtd1315e-pinctrl. Top-level required properties: compatible, reg. Important top-level properties found in the schema: reg. Child-node patterns: -pins$. Function enum sample: gpio, nf, emmc, ao, gspi_loc0, gspi_loc1, uart0, uart1, uart2_loc0, uart2_loc1, i2c0, i2c1, i2c4, i2c5, pcie1, etn_led plus 75 more. Pin enum sample: gpio_0, gpio_1, emmc_rst_n, emmc_dd_sb, emmc_clk, emmc_cmd, gpio_6, gpio_7, gpio_8, gpio_9, gpio_10, gpio_11, gpio_12, gpio_13, gpio_14, gpio_15 plus 88 more. Referenced schemas: pincfg-node.yaml#, pinmux-node.yaml#, /schemas/types.yaml#/definitions/uint32.

## Control Flow
Validation accepts one Realtek compatible, one register range, and `*-pins` child nodes. Each child composes generic pinconf and pinmux definitions, then restricts `pins`, `function`, and electrical properties to the SoC-specific enum and vendor extensions.

## State and Persistence Behavior
The persistent interface is the DTS pin group name, selected function, and electrical tuning values. For RTD1625 this includes P/N drive strengths, duty-cycle adjustment, high-VIL mode, voltage and slew settings; older RTD schemas focus on pulls, drive, Schmitt, and power source.

## Dependencies and Integration Points
This schema is consumed by Linux devicetree validation tooling (`dt-schema`), board DTS files under architecture trees, and the matching kernel pinctrl/GPIO/interrupt driver. Integration points include `pinctrl.yaml`, generic `pinmux-node.yaml`/`pincfg-node.yaml`, vendor common schemas, dt-bindings headers, GPIO and interrupt-controller bindings, and SoC clock/reset/power-domain providers where referenced.

## Risks and Edge Cases
Electrical tuning fields can affect signal integrity. The risky edits are changing enum meanings, accepting unsupported pin/function combinations, or losing vendor-specific constraints that protect HDMI/I2C, eMMC, SD, and RGMII configurations.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/pinctrl/realtek,rtd1315e-pinctrl.yaml` and at least one `make dtbs_check` target containing a DTS user of the compatible. For shared helper schemas, run the top-level importing bindings as well. Review the in-file example because it exercises required properties, child-node shape, and referenced dt-bindings constants.
