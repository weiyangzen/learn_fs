# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,sm8650-tlmm.yaml

## Purpose
This schema describes a Qualcomm Top Level Mode Multiplexer controller for one SoC family. It binds the SoC-specific compatible string, register range, interrupt wiring, GPIO range metadata, and the state subnode grammar used by client devices to request pin muxing and electrical configuration. Source title: Qualcomm Technologies, Inc. SM8650 TLMM block. Description signal from the file: Top Level Mode Multiplexer pin controller in Qualcomm SM8650 SoC.

## Important APIs, Types, and Schema Surface
- Lines read: 141.
- Compatible contract: qcom,sm8650-tlmm. Top-level required properties: compatible, reg. Important top-level properties found in the schema: reg, interrupts, gpio-line-names, gpio-reserved-ranges. Child-node patterns: -state$, -pins$. Function enum sample: gpio, aoss_cti, atest_char, atest_usb, audio_ext_mclk0, audio_ext_mclk1, audio_ref_clk, cam_aon_mclk2, cam_aon_mclk4, cam_mclk, cci_async_in, cci_i2c_scl, cci_i2c_sda, cci_timer, cmu_rng, coex_uart1_rx plus 121 more. Pin enum sample: ufs_reset, sdc2_clk, sdc2_cmd, sdc2_data. Referenced schemas: /schemas/pinctrl/qcom,tlmm-common.yaml#, #/$defs/qcom-sm8650-tlmm-state, qcom,tlmm-common.yaml#/$defs/qcom-tlmm-state.

## Control Flow
Validation starts at the controller node, applies the shared Qualcomm TLMM schema through `allOf`, then accepts `*-state` children either as direct state objects or as containers of `*-pins` subnodes. Each state must provide `pins`; `function` is optional in schema terms but constrained to the SoC function enum when present. `unevaluatedProperties: false` closes both top-level and state objects after shared TLMM properties are applied.

## State and Persistence Behavior
There is no runtime persistence in the YAML itself. The persistent ABI is the devicetree shape: compatible string, register tuple, GPIO numbering, interrupt line, optional reserved ranges, and stable pin/function names consumed by board DTS files and the Qualcomm pinctrl driver.

## Dependencies and Integration Points
This schema is consumed by Linux devicetree validation tooling (`dt-schema`), board DTS files under architecture trees, and the matching kernel pinctrl/GPIO/interrupt driver. Integration points include `pinctrl.yaml`, generic `pinmux-node.yaml`/`pincfg-node.yaml`, vendor common schemas, dt-bindings headers, GPIO and interrupt-controller bindings, and SoC clock/reset/power-domain providers where referenced.

## Risks and Edge Cases
Primary risks are off-by-one GPIO ranges, stale function names relative to the driver tables, missing SDC special pins, or relaxing child-node closure so invalid board pin states pass dt-schema. Changes should also keep `gpio-line-names` and `gpio-reserved-ranges` maxima aligned with actual GPIO count.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/pinctrl/qcom,sm8650-tlmm.yaml` and at least one `make dtbs_check` target containing a DTS user of the compatible. For shared helper schemas, run the top-level importing bindings as well. Review the in-file example because it exercises required properties, child-node shape, and referenced dt-bindings constants.
