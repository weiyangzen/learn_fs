# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,sm8550-lpass-lpi-pinctrl.yaml

## Purpose
This schema describes the Qualcomm LPASS Low Power Island pin controller. It is narrower than a main TLMM block and validates audio-subsystem pin states, required LPASS clocks, and SoC-specific pin/function enumerations. Source title: Qualcomm SM8550 SoC LPASS LPI TLMM. Description signal from the file: Top Level Mode Multiplexer pin controller in the Low Power Audio SubSystem (LPASS) Low Power Island (LPI) of Qualcomm SM8550 SoC.

## Important APIs, Types, and Schema Surface
- Lines read: 113.
- Compatible contract: qcom,sm8550-lpass-lpi-pinctrl, qcom,x1e80100-lpass-lpi-pinctrl. Top-level required properties: compatible, reg, clocks, clock-names. Important top-level properties found in the schema: reg, clocks, clock-names. Child-node patterns: -state$, -pins$. Function enum sample: dmic1_clk, dmic1_data, dmic2_clk, dmic2_data, dmic3_clk, dmic3_data, dmic4_clk, dmic4_data, ext_mclk1_a, ext_mclk1_b, ext_mclk1_c, ext_mclk1_d, ext_mclk1_e, gpio, i2s0_clk, i2s0_data plus 23 more. Referenced schemas: #/$defs/qcom-sm8550-lpass-state, qcom,lpass-lpi-common.yaml#/$defs/qcom-tlmm-state, qcom,lpass-lpi-common.yaml#.

## Control Flow
Validation requires the LPASS compatible, register range, clocks, and `clock-names`, then delegates common LPI state handling through `qcom,lpass-lpi-common.yaml`. State children use a SoC-local `$defs` entry and inherit the common TLMM state shape for pin configuration fields.

## State and Persistence Behavior
The binding persists LPASS audio pin naming, clock dependency names, and state-node structure used by audio clients. It does not store mutable state, but DTS compatibility depends on stable pin and function labels.

## Dependencies and Integration Points
This schema is consumed by Linux devicetree validation tooling (`dt-schema`), board DTS files under architecture trees, and the matching kernel pinctrl/GPIO/interrupt driver. Integration points include `pinctrl.yaml`, generic `pinmux-node.yaml`/`pincfg-node.yaml`, vendor common schemas, dt-bindings headers, GPIO and interrupt-controller bindings, and SoC clock/reset/power-domain providers where referenced.

## Risks and Edge Cases
High-risk edits include changing clock requirements, removing an alternate compatible fallback, or adding function names not backed by the LPASS pinctrl driver. Audio bring-up can fail quietly if a DTS validates but maps a serial/audio pin to the wrong LPASS function.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/pinctrl/qcom,sm8550-lpass-lpi-pinctrl.yaml` and at least one `make dtbs_check` target containing a DTS user of the compatible. For shared helper schemas, run the top-level importing bindings as well. Review the in-file example because it exercises required properties, child-node shape, and referenced dt-bindings constants.
