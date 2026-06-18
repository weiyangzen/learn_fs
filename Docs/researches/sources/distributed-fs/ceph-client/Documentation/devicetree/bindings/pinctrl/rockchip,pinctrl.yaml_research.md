# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/rockchip,pinctrl.yaml

## Purpose
This schema describes the Rockchip pinmux controller and its GPIO-bank children. It coordinates syscon phandles for GRF/PMU register access with nested bank schemas and per-state pin configuration arrays. Source title: Rockchip Pinmux Controller. Description signal from the file: The Rockchip Pinmux Controller enables the IC to share one PAD to several functional blocks. The sharing is done by multiplexing the PAD input/output signals. For each PAD there are several muxing options with option 0 being used as a GPIO. Please refer to pinctrl-bindings.txt in this directory for details of the common pinctrl bindings used by client devices, including the meaning of the phrase "pin configuration node". The Rockchip pin configur

## Important APIs, Types, and Schema Surface
- Lines read: 195.
- Compatible contract: rockchip,px30-pinctrl, rockchip,rk2928-pinctrl, rockchip,rk3036-pinctrl, rockchip,rk3066a-pinctrl, rockchip,rk3066b-pinctrl, rockchip,rk3128-pinctrl, rockchip,rk3188-pinctrl, rockchip,rk3228-pinctrl, rockchip,rk3288-pinctrl, rockchip,rk3308-pinctrl plus 13 more. Top-level required properties: compatible, rockchip,grf. Important top-level properties found in the schema: rockchip,grf, rockchip,pmu. Child-node patterns: None declared in this schema. Referenced schemas: /schemas/types.yaml#/definitions/phandle, pinctrl.yaml#, /schemas/gpio/rockchip,gpio-bank.yaml#, /schemas/types.yaml#/definitions/uint32-matrix.

## Control Flow
Validation checks a Rockchip SoC compatible, requires the GRF syscon phandle, and accepts GPIO bank children via the Rockchip GPIO-bank schema. Pin states are nested children containing arrays that encode bank, pin, mux, and config data.

## State and Persistence Behavior
Persistent ABI includes syscon phandles, bank child layout, and matrix values consumed by Rockchip pinctrl code. Optional PMU/PHP GRF references represent register-bank integration points rather than mutable YAML state.

## Dependencies and Integration Points
This schema is consumed by Linux devicetree validation tooling (`dt-schema`), board DTS files under architecture trees, and the matching kernel pinctrl/GPIO/interrupt driver. Integration points include `pinctrl.yaml`, generic `pinmux-node.yaml`/`pincfg-node.yaml`, vendor common schemas, dt-bindings headers, GPIO and interrupt-controller bindings, and SoC clock/reset/power-domain providers where referenced.

## Risks and Edge Cases
The packed matrix values and syscon phandles are easy to mis-specify. Schema changes need dtbs_check coverage for both older and newer compatibles, especially those needing PMU or PHP GRF access.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/pinctrl/rockchip,pinctrl.yaml` and at least one `make dtbs_check` target containing a DTS user of the compatible. For shared helper schemas, run the top-level importing bindings as well. Review the in-file example because it exercises required properties, child-node shape, and referenced dt-bindings constants.
