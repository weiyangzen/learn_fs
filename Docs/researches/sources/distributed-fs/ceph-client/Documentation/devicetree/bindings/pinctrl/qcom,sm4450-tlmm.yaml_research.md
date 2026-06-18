# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,sm4450-tlmm.yaml

## Purpose
This schema describes a Qualcomm Top Level Mode Multiplexer controller for one SoC family. It binds the SoC-specific compatible string, register range, interrupt wiring, GPIO range metadata, and the state subnode grammar used by client devices to request pin muxing and electrical configuration. Source title: Qualcomm Technologies, Inc. SM4450 TLMM block. Description signal from the file: Top Level Mode Multiplexer pin controller in Qualcomm SM4450 SoC.

## Important APIs, Types, and Schema Surface
- Lines read: 135.
- Compatible contract: qcom,sm4450-tlmm. Top-level required properties: compatible, reg. Important top-level properties found in the schema: reg, interrupts, gpio-controller, interrupt-controller, #gpio-cells, #interrupt-cells, gpio-ranges, gpio-line-names, gpio-reserved-ranges. Child-node patterns: -state$, -pins$. Function enum sample: gpio, atest_char, atest_usb0, audio_ref_clk, cam_mclk, cci_async_in0, cci_i2c, cci, cmu_rng, coex_uart1_rx, coex_uart1_tx, cri_trng, dbg_out_clk, ddr_bist, ddr_pxi0_test, ddr_pxi1_test plus 55 more. Pin enum sample: sdc2_clk, sdc2_cmd, sdc2_data, ufs_reset. Referenced schemas: /schemas/pinctrl/qcom,tlmm-common.yaml#, #/$defs/qcom-sm4450-tlmm-state, qcom,tlmm-common.yaml#/$defs/qcom-tlmm-state.

## Control Flow
Validation starts at the controller node, applies the shared Qualcomm TLMM schema through `allOf`, then accepts `*-state` children either as direct state objects or as containers of `*-pins` subnodes. Each state must provide `pins`; `function` is optional in schema terms but constrained to the SoC function enum when present. `unevaluatedProperties: false` closes both top-level and state objects after shared TLMM properties are applied.

## State and Persistence Behavior
There is no runtime persistence in the YAML itself. The persistent ABI is the devicetree shape: compatible string, register tuple, GPIO numbering, interrupt line, optional reserved ranges, and stable pin/function names consumed by board DTS files and the Qualcomm pinctrl driver.

## Dependencies and Integration Points
This schema is consumed by Linux devicetree validation tooling (`dt-schema`), board DTS files under architecture trees, and the matching kernel pinctrl/GPIO/interrupt driver. Integration points include `pinctrl.yaml`, generic `pinmux-node.yaml`/`pincfg-node.yaml`, vendor common schemas, dt-bindings headers, GPIO and interrupt-controller bindings, and SoC clock/reset/power-domain providers where referenced.

## Risks and Edge Cases
Primary risks are off-by-one GPIO ranges, stale function names relative to the driver tables, missing SDC special pins, or relaxing child-node closure so invalid board pin states pass dt-schema. Changes should also keep `gpio-line-names` and `gpio-reserved-ranges` maxima aligned with actual GPIO count.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/pinctrl/qcom,sm4450-tlmm.yaml` and at least one `make dtbs_check` target containing a DTS user of the compatible. For shared helper schemas, run the top-level importing bindings as well. Review the in-file example because it exercises required properties, child-node shape, and referenced dt-bindings constants.
