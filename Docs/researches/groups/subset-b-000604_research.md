# subset-b-000604 Research

Grouped research for the requested pinctrl devicetree binding schemas. Each section is wrapped for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,sdx75-tlmm.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,sdx75-tlmm.yaml

## Purpose
This schema describes a Qualcomm Top Level Mode Multiplexer controller for one SoC family. It binds the SoC-specific compatible string, register range, interrupt wiring, GPIO range metadata, and the state subnode grammar used by client devices to request pin muxing and electrical configuration. Source title: Qualcomm Technologies, Inc. SDX75 TLMM block. Description signal from the file: Top Level Mode Multiplexer pin controller in Qualcomm SDX75 SoC.

## Important APIs, Types, and Schema Surface
- Lines read: 131.
- Compatible contract: qcom,sdx75-tlmm. Top-level required properties: compatible, reg. Important top-level properties found in the schema: reg, interrupts, gpio-line-names, gpio-reserved-ranges. Child-node patterns: -state$, -pins$. Function enum sample: adsp_ext, atest_char, audio_ref_clk, bimc_dte, char_exec, coex_uart2, coex_uart, cri_trng, cri_trng0, cri_trng1, dbg_out_clk, ddr_bist, ddr_pxi0, ebi0_wrcdc, ebi2_a, ebi2_lcd plus 91 more. Pin enum sample: sdc1_clk, sdc1_cmd, sdc1_data, sdc1_rclk, sdc2_clk, sdc2_cmd, sdc2_data. Referenced schemas: /schemas/pinctrl/qcom,tlmm-common.yaml#, #/$defs/qcom-sdx75-tlmm-state, qcom,tlmm-common.yaml#/$defs/qcom-tlmm-state.

## Control Flow
Validation starts at the controller node, applies the shared Qualcomm TLMM schema through `allOf`, then accepts `*-state` children either as direct state objects or as containers of `*-pins` subnodes. Each state must provide `pins`; `function` is optional in schema terms but constrained to the SoC function enum when present. `unevaluatedProperties: false` closes both top-level and state objects after shared TLMM properties are applied.

## State and Persistence Behavior
There is no runtime persistence in the YAML itself. The persistent ABI is the devicetree shape: compatible string, register tuple, GPIO numbering, interrupt line, optional reserved ranges, and stable pin/function names consumed by board DTS files and the Qualcomm pinctrl driver.

## Dependencies and Integration Points
This schema is consumed by Linux devicetree validation tooling (`dt-schema`), board DTS files under architecture trees, and the matching kernel pinctrl/GPIO/interrupt driver. Integration points include `pinctrl.yaml`, generic `pinmux-node.yaml`/`pincfg-node.yaml`, vendor common schemas, dt-bindings headers, GPIO and interrupt-controller bindings, and SoC clock/reset/power-domain providers where referenced.

## Risks and Edge Cases
Primary risks are off-by-one GPIO ranges, stale function names relative to the driver tables, missing SDC special pins, or relaxing child-node closure so invalid board pin states pass dt-schema. Changes should also keep `gpio-line-names` and `gpio-reserved-ranges` maxima aligned with actual GPIO count.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/pinctrl/qcom,sdx75-tlmm.yaml` and at least one `make dtbs_check` target containing a DTS user of the compatible. For shared helper schemas, run the top-level importing bindings as well. Review the in-file example because it exercises required properties, child-node shape, and referenced dt-bindings constants.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,sdx75-tlmm.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,sm4250-lpass-lpi-pinctrl.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,sm4250-lpass-lpi-pinctrl.yaml

## Purpose
This schema describes the Qualcomm LPASS Low Power Island pin controller. It is narrower than a main TLMM block and validates audio-subsystem pin states, required LPASS clocks, and SoC-specific pin/function enumerations. Source title: Qualcomm SM4250 SoC LPASS LPI TLMM. Description signal from the file: Top Level Mode Multiplexer pin controller in the Low Power Audio SubSystem (LPASS) Low Power Island (LPI) of Qualcomm SM4250 SoC.

## Important APIs, Types, and Schema Surface
- Lines read: 118.
- Compatible contract: qcom,sm4250-lpass-lpi-pinctrl. Top-level required properties: compatible, reg, clocks, clock-names. Important top-level properties found in the schema: reg, clocks, clock-names. Child-node patterns: -state$, -pins$. Function enum sample: gpio, dmic01_clk, dmic01_data, dmic23_clk, dmic23_data, dmic4_clk, dmic4_data, ext_mclk0_a, ext_mclk0_b, ext_mclk1_a, ext_mclk1_b, ext_mclk1_c, i2s1_clk, i2s1_data, i2s1_ws, i2s2_clk plus 16 more. Referenced schemas: #/$defs/qcom-sm4250-lpass-state, qcom,lpass-lpi-common.yaml#/$defs/qcom-tlmm-state, qcom,lpass-lpi-common.yaml#.

## Control Flow
Validation requires the LPASS compatible, register range, clocks, and `clock-names`, then delegates common LPI state handling through `qcom,lpass-lpi-common.yaml`. State children use a SoC-local `$defs` entry and inherit the common TLMM state shape for pin configuration fields.

## State and Persistence Behavior
The binding persists LPASS audio pin naming, clock dependency names, and state-node structure used by audio clients. It does not store mutable state, but DTS compatibility depends on stable pin and function labels.

## Dependencies and Integration Points
This schema is consumed by Linux devicetree validation tooling (`dt-schema`), board DTS files under architecture trees, and the matching kernel pinctrl/GPIO/interrupt driver. Integration points include `pinctrl.yaml`, generic `pinmux-node.yaml`/`pincfg-node.yaml`, vendor common schemas, dt-bindings headers, GPIO and interrupt-controller bindings, and SoC clock/reset/power-domain providers where referenced.

## Risks and Edge Cases
High-risk edits include changing clock requirements, removing an alternate compatible fallback, or adding function names not backed by the LPASS pinctrl driver. Audio bring-up can fail quietly if a DTS validates but maps a serial/audio pin to the wrong LPASS function.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/pinctrl/qcom,sm4250-lpass-lpi-pinctrl.yaml` and at least one `make dtbs_check` target containing a DTS user of the compatible. For shared helper schemas, run the top-level importing bindings as well. Review the in-file example because it exercises required properties, child-node shape, and referenced dt-bindings constants.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,sm4250-lpass-lpi-pinctrl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,sm4450-tlmm.yaml -->
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

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,sm4450-tlmm.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,sm6115-lpass-lpi-pinctrl.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,sm6115-lpass-lpi-pinctrl.yaml

## Purpose
This schema describes the Qualcomm LPASS Low Power Island pin controller. It is narrower than a main TLMM block and validates audio-subsystem pin states, required LPASS clocks, and SoC-specific pin/function enumerations. Source title: Qualcomm SM6115 SoC LPASS LPI TLMM. Description signal from the file: Top Level Mode Multiplexer pin controller in the Low Power Audio SubSystem (LPASS) Low Power Island (LPI) of Qualcomm SM6115 SoC.

## Important APIs, Types, and Schema Surface
- Lines read: 100.
- Compatible contract: qcom,sm6115-lpass-lpi-pinctrl, qcom,qcm2290-lpass-lpi-pinctrl. Top-level required properties: compatible, reg, clocks, clock-names. Important top-level properties found in the schema: reg, clocks, clock-names. Child-node patterns: -state$, -pins$. Function enum sample: dmic01_clk, dmic01_data, dmic23_clk, dmic23_data, gpio, i2s1_clk, i2s1_data, i2s1_ws, i2s2_clk, i2s2_data, i2s2_ws, i2s3_clk, i2s3_data, i2s3_ws, qua_mi2s_data, qua_mi2s_sclk plus 6 more. Referenced schemas: #/$defs/qcom-sm6115-lpass-state, qcom,lpass-lpi-common.yaml#/$defs/qcom-tlmm-state, qcom,lpass-lpi-common.yaml#.

## Control Flow
Validation requires the LPASS compatible, register range, clocks, and `clock-names`, then delegates common LPI state handling through `qcom,lpass-lpi-common.yaml`. State children use a SoC-local `$defs` entry and inherit the common TLMM state shape for pin configuration fields.

## State and Persistence Behavior
The binding persists LPASS audio pin naming, clock dependency names, and state-node structure used by audio clients. It does not store mutable state, but DTS compatibility depends on stable pin and function labels.

## Dependencies and Integration Points
This schema is consumed by Linux devicetree validation tooling (`dt-schema`), board DTS files under architecture trees, and the matching kernel pinctrl/GPIO/interrupt driver. Integration points include `pinctrl.yaml`, generic `pinmux-node.yaml`/`pincfg-node.yaml`, vendor common schemas, dt-bindings headers, GPIO and interrupt-controller bindings, and SoC clock/reset/power-domain providers where referenced.

## Risks and Edge Cases
High-risk edits include changing clock requirements, removing an alternate compatible fallback, or adding function names not backed by the LPASS pinctrl driver. Audio bring-up can fail quietly if a DTS validates but maps a serial/audio pin to the wrong LPASS function.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/pinctrl/qcom,sm6115-lpass-lpi-pinctrl.yaml` and at least one `make dtbs_check` target containing a DTS user of the compatible. For shared helper schemas, run the top-level importing bindings as well. Review the in-file example because it exercises required properties, child-node shape, and referenced dt-bindings constants.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,sm6115-lpass-lpi-pinctrl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,sm6115-tlmm.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,sm6115-tlmm.yaml

## Purpose
This schema describes a Qualcomm Top Level Mode Multiplexer controller for one SoC family. It binds the SoC-specific compatible string, register range, interrupt wiring, GPIO range metadata, and the state subnode grammar used by client devices to request pin muxing and electrical configuration. Source title: Qualcomm Technologies, Inc. SM6115, SM4250 TLMM block. Description signal from the file: Top Level Mode Multiplexer pin controller in Qualcomm SM4250 and SM6115 SoCs.

## Important APIs, Types, and Schema Surface
- Lines read: 138.
- Compatible contract: qcom,sm6115-tlmm. Top-level required properties: compatible, reg, reg-names. Important top-level properties found in the schema: reg, interrupts, gpio-reserved-ranges. Child-node patterns: -state$, -pins$. Function enum sample: adsp_ext, agera_pll, atest, cam_mclk, cci_async, cci_i2c, cci_timer, cri_trng, dac_calib, dbg_out, ddr_bist, ddr_pxi0, ddr_pxi1, ddr_pxi2, ddr_pxi3, gcc_gp1 plus 51 more. Pin enum sample: sdc1_rclk, sdc1_clk, sdc1_cmd, sdc1_data, sdc2_clk, sdc2_cmd, sdc2_data, ufs_reset. Referenced schemas: #/$defs/qcom-sm6115-tlmm-state, qcom,tlmm-common.yaml#/$defs/qcom-tlmm-state, /schemas/pinctrl/qcom,tlmm-common.yaml#.

## Control Flow
Validation starts at the controller node, applies the shared Qualcomm TLMM schema through `allOf`, then accepts `*-state` children either as direct state objects or as containers of `*-pins` subnodes. Each state must provide `pins`; `function` is optional in schema terms but constrained to the SoC function enum when present. `unevaluatedProperties: false` closes both top-level and state objects after shared TLMM properties are applied.

## State and Persistence Behavior
There is no runtime persistence in the YAML itself. The persistent ABI is the devicetree shape: compatible string, register tuple, GPIO numbering, interrupt line, optional reserved ranges, and stable pin/function names consumed by board DTS files and the Qualcomm pinctrl driver.

## Dependencies and Integration Points
This schema is consumed by Linux devicetree validation tooling (`dt-schema`), board DTS files under architecture trees, and the matching kernel pinctrl/GPIO/interrupt driver. Integration points include `pinctrl.yaml`, generic `pinmux-node.yaml`/`pincfg-node.yaml`, vendor common schemas, dt-bindings headers, GPIO and interrupt-controller bindings, and SoC clock/reset/power-domain providers where referenced.

## Risks and Edge Cases
Primary risks are off-by-one GPIO ranges, stale function names relative to the driver tables, missing SDC special pins, or relaxing child-node closure so invalid board pin states pass dt-schema. Changes should also keep `gpio-line-names` and `gpio-reserved-ranges` maxima aligned with actual GPIO count.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/pinctrl/qcom,sm6115-tlmm.yaml` and at least one `make dtbs_check` target containing a DTS user of the compatible. For shared helper schemas, run the top-level importing bindings as well. Review the in-file example because it exercises required properties, child-node shape, and referenced dt-bindings constants.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,sm6115-tlmm.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,sm6125-tlmm.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,sm6125-tlmm.yaml

## Purpose
This schema describes a Qualcomm Top Level Mode Multiplexer controller for one SoC family. It binds the SoC-specific compatible string, register range, interrupt wiring, GPIO range metadata, and the state subnode grammar used by client devices to request pin muxing and electrical configuration. Source title: Qualcomm Technologies, Inc. SM6125 TLMM block. Description signal from the file: Top Level Mode Multiplexer pin controller in Qualcomm SM6125 SoC.

## Important APIs, Types, and Schema Surface
- Lines read: 136.
- Compatible contract: qcom,sm6125-tlmm. Top-level required properties: compatible, reg, reg-names. Important top-level properties found in the schema: reg, interrupts, gpio-reserved-ranges. Child-node patterns: -state$, -pins$. Function enum sample: adsp_ext, agera_pll, atest_char, atest_char0, atest_char1, atest_char2, atest_char3, atest_tsens, atest_tsens2, atest_usb1, atest_usb10, atest_usb11, atest_usb12, atest_usb13, atest_usb2, atest_usb20 plus 111 more. Pin enum sample: sdc1_clk, sdc1_cmd, sdc1_data, sdc2_clk, sdc2_cmd, sdc2_data. Referenced schemas: /schemas/pinctrl/qcom,tlmm-common.yaml#, #/$defs/qcom-sm6125-tlmm-state, qcom,tlmm-common.yaml#/$defs/qcom-tlmm-state.

## Control Flow
Validation starts at the controller node, applies the shared Qualcomm TLMM schema through `allOf`, then accepts `*-state` children either as direct state objects or as containers of `*-pins` subnodes. Each state must provide `pins`; `function` is optional in schema terms but constrained to the SoC function enum when present. `unevaluatedProperties: false` closes both top-level and state objects after shared TLMM properties are applied.

## State and Persistence Behavior
There is no runtime persistence in the YAML itself. The persistent ABI is the devicetree shape: compatible string, register tuple, GPIO numbering, interrupt line, optional reserved ranges, and stable pin/function names consumed by board DTS files and the Qualcomm pinctrl driver.

## Dependencies and Integration Points
This schema is consumed by Linux devicetree validation tooling (`dt-schema`), board DTS files under architecture trees, and the matching kernel pinctrl/GPIO/interrupt driver. Integration points include `pinctrl.yaml`, generic `pinmux-node.yaml`/`pincfg-node.yaml`, vendor common schemas, dt-bindings headers, GPIO and interrupt-controller bindings, and SoC clock/reset/power-domain providers where referenced.

## Risks and Edge Cases
Primary risks are off-by-one GPIO ranges, stale function names relative to the driver tables, missing SDC special pins, or relaxing child-node closure so invalid board pin states pass dt-schema. Changes should also keep `gpio-line-names` and `gpio-reserved-ranges` maxima aligned with actual GPIO count.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/pinctrl/qcom,sm6125-tlmm.yaml` and at least one `make dtbs_check` target containing a DTS user of the compatible. For shared helper schemas, run the top-level importing bindings as well. Review the in-file example because it exercises required properties, child-node shape, and referenced dt-bindings constants.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,sm6125-tlmm.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,sm6350-tlmm.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,sm6350-tlmm.yaml

## Purpose
This schema describes a Qualcomm Top Level Mode Multiplexer controller for one SoC family. It binds the SoC-specific compatible string, register range, interrupt wiring, GPIO range metadata, and the state subnode grammar used by client devices to request pin muxing and electrical configuration. Source title: Qualcomm Technologies, Inc. SM6350 TLMM block. Description signal from the file: Top Level Mode Multiplexer pin controller in Qualcomm SM6350 SoC.

## Important APIs, Types, and Schema Surface
- Lines read: 148.
- Compatible contract: qcom,sm6350-tlmm. Top-level required properties: compatible, reg. Important top-level properties found in the schema: reg, interrupts, gpio-line-names, gpio-reserved-ranges. Child-node patterns: -state$, -pins$. Function enum sample: adsp_ext, agera_pll, atest_char, atest_char0, atest_char1, atest_char2, atest_char3, atest_tsens, atest_tsens2, atest_usb1, atest_usb10, atest_usb11, atest_usb12, atest_usb13, atest_usb2, atest_usb20 plus 158 more. Pin enum sample: sdc1_clk, sdc1_cmd, sdc1_data, sdc2_clk, sdc2_cmd, sdc2_data. Referenced schemas: /schemas/pinctrl/qcom,tlmm-common.yaml#, #/$defs/qcom-sm6350-tlmm-state, qcom,tlmm-common.yaml#/$defs/qcom-tlmm-state.

## Control Flow
Validation starts at the controller node, applies the shared Qualcomm TLMM schema through `allOf`, then accepts `*-state` children either as direct state objects or as containers of `*-pins` subnodes. Each state must provide `pins`; `function` is optional in schema terms but constrained to the SoC function enum when present. `unevaluatedProperties: false` closes both top-level and state objects after shared TLMM properties are applied.

## State and Persistence Behavior
There is no runtime persistence in the YAML itself. The persistent ABI is the devicetree shape: compatible string, register tuple, GPIO numbering, interrupt line, optional reserved ranges, and stable pin/function names consumed by board DTS files and the Qualcomm pinctrl driver.

## Dependencies and Integration Points
This schema is consumed by Linux devicetree validation tooling (`dt-schema`), board DTS files under architecture trees, and the matching kernel pinctrl/GPIO/interrupt driver. Integration points include `pinctrl.yaml`, generic `pinmux-node.yaml`/`pincfg-node.yaml`, vendor common schemas, dt-bindings headers, GPIO and interrupt-controller bindings, and SoC clock/reset/power-domain providers where referenced.

## Risks and Edge Cases
Primary risks are off-by-one GPIO ranges, stale function names relative to the driver tables, missing SDC special pins, or relaxing child-node closure so invalid board pin states pass dt-schema. Changes should also keep `gpio-line-names` and `gpio-reserved-ranges` maxima aligned with actual GPIO count.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/pinctrl/qcom,sm6350-tlmm.yaml` and at least one `make dtbs_check` target containing a DTS user of the compatible. For shared helper schemas, run the top-level importing bindings as well. Review the in-file example because it exercises required properties, child-node shape, and referenced dt-bindings constants.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,sm6350-tlmm.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,sm6375-tlmm.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,sm6375-tlmm.yaml

## Purpose
This schema describes a Qualcomm Top Level Mode Multiplexer controller for one SoC family. It binds the SoC-specific compatible string, register range, interrupt wiring, GPIO range metadata, and the state subnode grammar used by client devices to request pin muxing and electrical configuration. Source title: Qualcomm Technologies, Inc. SM6375 TLMM block. Description signal from the file: Top Level Mode Multiplexer pin controller in Qualcomm SM6375 SoC.

## Important APIs, Types, and Schema Surface
- Lines read: 142.
- Compatible contract: qcom,sm6375-tlmm. Top-level required properties: compatible, reg. Important top-level properties found in the schema: reg, interrupts, gpio-reserved-ranges. Child-node patterns: -state$, -pins$. Function enum sample: adsp_ext, agera_pll, atest_char, atest_char0, atest_char1, atest_char2, atest_char3, atest_tsens, atest_tsens2, atest_usb1, atest_usb10, atest_usb11, atest_usb12, atest_usb13, atest_usb2, atest_usb20 plus 149 more. Pin enum sample: ufs_reset, sdc1_clk, sdc1_cmd, sdc1_data, sdc2_clk, sdc2_cmd, sdc2_data. Referenced schemas: /schemas/pinctrl/qcom,tlmm-common.yaml#, #/$defs/qcom-sm6375-tlmm-state, qcom,tlmm-common.yaml#/$defs/qcom-tlmm-state.

## Control Flow
Validation starts at the controller node, applies the shared Qualcomm TLMM schema through `allOf`, then accepts `*-state` children either as direct state objects or as containers of `*-pins` subnodes. Each state must provide `pins`; `function` is optional in schema terms but constrained to the SoC function enum when present. `unevaluatedProperties: false` closes both top-level and state objects after shared TLMM properties are applied.

## State and Persistence Behavior
There is no runtime persistence in the YAML itself. The persistent ABI is the devicetree shape: compatible string, register tuple, GPIO numbering, interrupt line, optional reserved ranges, and stable pin/function names consumed by board DTS files and the Qualcomm pinctrl driver.

## Dependencies and Integration Points
This schema is consumed by Linux devicetree validation tooling (`dt-schema`), board DTS files under architecture trees, and the matching kernel pinctrl/GPIO/interrupt driver. Integration points include `pinctrl.yaml`, generic `pinmux-node.yaml`/`pincfg-node.yaml`, vendor common schemas, dt-bindings headers, GPIO and interrupt-controller bindings, and SoC clock/reset/power-domain providers where referenced.

## Risks and Edge Cases
Primary risks are off-by-one GPIO ranges, stale function names relative to the driver tables, missing SDC special pins, or relaxing child-node closure so invalid board pin states pass dt-schema. Changes should also keep `gpio-line-names` and `gpio-reserved-ranges` maxima aligned with actual GPIO count.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/pinctrl/qcom,sm6375-tlmm.yaml` and at least one `make dtbs_check` target containing a DTS user of the compatible. For shared helper schemas, run the top-level importing bindings as well. Review the in-file example because it exercises required properties, child-node shape, and referenced dt-bindings constants.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,sm6375-tlmm.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,sm7150-tlmm.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,sm7150-tlmm.yaml

## Purpose
This schema describes a Qualcomm Top Level Mode Multiplexer controller for one SoC family. It binds the SoC-specific compatible string, register range, interrupt wiring, GPIO range metadata, and the state subnode grammar used by client devices to request pin muxing and electrical configuration. Source title: Qualcomm SM7150 TLMM pin controller. Description signal from the file: Top Level Mode Multiplexer pin controller in Qualcomm SM7150 SoC.

## Important APIs, Types, and Schema Surface
- Lines read: 146.
- Compatible contract: qcom,sm7150-tlmm. Top-level required properties: compatible, reg, reg-names. Important top-level properties found in the schema: reg, interrupts, gpio-line-names, gpio-reserved-ranges. Child-node patterns: -state$, -pins$. Function enum sample: gpio, adsp_ext, agera_pll, aoss_cti, atest_char, atest_tsens, atest_tsens2, atest_usb1, atest_usb2, cam_mclk, cci_async, cci_i2c, cci_timer0, cci_timer1, cci_timer2, cci_timer3 plus 94 more. Pin enum sample: sdc1_rclk, sdc1_clk, sdc1_cmd, sdc1_data, sdc2_clk, sdc2_cmd, sdc2_data, ufs_reset. Referenced schemas: /schemas/pinctrl/qcom,tlmm-common.yaml#, #/$defs/qcom-sm7150-tlmm-state, qcom,tlmm-common.yaml#/$defs/qcom-tlmm-state.

## Control Flow
Validation starts at the controller node, applies the shared Qualcomm TLMM schema through `allOf`, then accepts `*-state` children either as direct state objects or as containers of `*-pins` subnodes. Each state must provide `pins`; `function` is optional in schema terms but constrained to the SoC function enum when present. `unevaluatedProperties: false` closes both top-level and state objects after shared TLMM properties are applied.

## State and Persistence Behavior
There is no runtime persistence in the YAML itself. The persistent ABI is the devicetree shape: compatible string, register tuple, GPIO numbering, interrupt line, optional reserved ranges, and stable pin/function names consumed by board DTS files and the Qualcomm pinctrl driver.

## Dependencies and Integration Points
This schema is consumed by Linux devicetree validation tooling (`dt-schema`), board DTS files under architecture trees, and the matching kernel pinctrl/GPIO/interrupt driver. Integration points include `pinctrl.yaml`, generic `pinmux-node.yaml`/`pincfg-node.yaml`, vendor common schemas, dt-bindings headers, GPIO and interrupt-controller bindings, and SoC clock/reset/power-domain providers where referenced.

## Risks and Edge Cases
Primary risks are off-by-one GPIO ranges, stale function names relative to the driver tables, missing SDC special pins, or relaxing child-node closure so invalid board pin states pass dt-schema. Changes should also keep `gpio-line-names` and `gpio-reserved-ranges` maxima aligned with actual GPIO count.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/pinctrl/qcom,sm7150-tlmm.yaml` and at least one `make dtbs_check` target containing a DTS user of the compatible. For shared helper schemas, run the top-level importing bindings as well. Review the in-file example because it exercises required properties, child-node shape, and referenced dt-bindings constants.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,sm7150-tlmm.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,sm8150-pinctrl.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,sm8150-pinctrl.yaml

## Purpose
This schema describes a Qualcomm Top Level Mode Multiplexer controller for one SoC family. It binds the SoC-specific compatible string, register range, interrupt wiring, GPIO range metadata, and the state subnode grammar used by client devices to request pin muxing and electrical configuration. Source title: Qualcomm SM8150 TLMM pin controller. Description signal from the file: Top Level Mode Multiplexer pin controller in Qualcomm SM8150 SoC.

## Important APIs, Types, and Schema Surface
- Lines read: 159.
- Compatible contract: qcom,sm8150-pinctrl. Top-level required properties: compatible, reg, reg-names. Important top-level properties found in the schema: reg, interrupts, gpio-line-names, gpio-reserved-ranges. Child-node patterns: -state$, -pins$. Function enum sample: adsp_ext, agera_pll, aoss_cti, ddr_pxi2, atest_char, atest_char0, atest_char1, atest_char2, atest_char3, audio_ref, atest_usb1, atest_usb2, atest_usb10, atest_usb11, atest_usb12, atest_usb13 plus 113 more. Pin enum sample: sdc2_clk, sdc2_cmd, sdc2_data, ufs_reset. Referenced schemas: #/$defs/qcom-sm8150-tlmm-state, qcom,tlmm-common.yaml#/$defs/qcom-tlmm-state, /schemas/pinctrl/qcom,tlmm-common.yaml#.

## Control Flow
Validation starts at the controller node, applies the shared Qualcomm TLMM schema through `allOf`, then accepts `*-state` children either as direct state objects or as containers of `*-pins` subnodes. Each state must provide `pins`; `function` is optional in schema terms but constrained to the SoC function enum when present. `unevaluatedProperties: false` closes both top-level and state objects after shared TLMM properties are applied.

## State and Persistence Behavior
There is no runtime persistence in the YAML itself. The persistent ABI is the devicetree shape: compatible string, register tuple, GPIO numbering, interrupt line, optional reserved ranges, and stable pin/function names consumed by board DTS files and the Qualcomm pinctrl driver.

## Dependencies and Integration Points
This schema is consumed by Linux devicetree validation tooling (`dt-schema`), board DTS files under architecture trees, and the matching kernel pinctrl/GPIO/interrupt driver. Integration points include `pinctrl.yaml`, generic `pinmux-node.yaml`/`pincfg-node.yaml`, vendor common schemas, dt-bindings headers, GPIO and interrupt-controller bindings, and SoC clock/reset/power-domain providers where referenced.

## Risks and Edge Cases
Primary risks are off-by-one GPIO ranges, stale function names relative to the driver tables, missing SDC special pins, or relaxing child-node closure so invalid board pin states pass dt-schema. Changes should also keep `gpio-line-names` and `gpio-reserved-ranges` maxima aligned with actual GPIO count.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/pinctrl/qcom,sm8150-pinctrl.yaml` and at least one `make dtbs_check` target containing a DTS user of the compatible. For shared helper schemas, run the top-level importing bindings as well. Review the in-file example because it exercises required properties, child-node shape, and referenced dt-bindings constants.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,sm8150-pinctrl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,sm8250-lpass-lpi-pinctrl.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,sm8250-lpass-lpi-pinctrl.yaml

## Purpose
This schema describes the Qualcomm LPASS Low Power Island pin controller. It is narrower than a main TLMM block and validates audio-subsystem pin states, required LPASS clocks, and SoC-specific pin/function enumerations. Source title: Qualcomm SM8250 SoC LPASS LPI TLMM. Description signal from the file: Top Level Mode Multiplexer pin controller in the Low Power Audio SubSystem (LPASS) Low Power Island (LPI) of Qualcomm SM8250 SoC.

## Important APIs, Types, and Schema Surface
- Lines read: 120.
- Compatible contract: qcom,sm8250-lpass-lpi-pinctrl. Top-level required properties: compatible, reg, clocks, clock-names. Important top-level properties found in the schema: reg, clocks, clock-names. Child-node patterns: -state$, -pins$. Function enum sample: gpio, swr_tx_clk, qua_mi2s_sclk, swr_tx_data, qua_mi2s_ws, qua_mi2s_data, swr_rx_clk, swr_rx_data, dmic1_clk, i2s1_clk, dmic1_data, i2s1_ws, dmic2_clk, dmic2_data, i2s1_data, i2s2_clk plus 6 more. Referenced schemas: #/$defs/qcom-sm8250-lpass-state, qcom,lpass-lpi-common.yaml#/$defs/qcom-tlmm-state, qcom,lpass-lpi-common.yaml#.

## Control Flow
Validation requires the LPASS compatible, register range, clocks, and `clock-names`, then delegates common LPI state handling through `qcom,lpass-lpi-common.yaml`. State children use a SoC-local `$defs` entry and inherit the common TLMM state shape for pin configuration fields.

## State and Persistence Behavior
The binding persists LPASS audio pin naming, clock dependency names, and state-node structure used by audio clients. It does not store mutable state, but DTS compatibility depends on stable pin and function labels.

## Dependencies and Integration Points
This schema is consumed by Linux devicetree validation tooling (`dt-schema`), board DTS files under architecture trees, and the matching kernel pinctrl/GPIO/interrupt driver. Integration points include `pinctrl.yaml`, generic `pinmux-node.yaml`/`pincfg-node.yaml`, vendor common schemas, dt-bindings headers, GPIO and interrupt-controller bindings, and SoC clock/reset/power-domain providers where referenced.

## Risks and Edge Cases
High-risk edits include changing clock requirements, removing an alternate compatible fallback, or adding function names not backed by the LPASS pinctrl driver. Audio bring-up can fail quietly if a DTS validates but maps a serial/audio pin to the wrong LPASS function.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/pinctrl/qcom,sm8250-lpass-lpi-pinctrl.yaml` and at least one `make dtbs_check` target containing a DTS user of the compatible. For shared helper schemas, run the top-level importing bindings as well. Review the in-file example because it exercises required properties, child-node shape, and referenced dt-bindings constants.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,sm8250-lpass-lpi-pinctrl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,sm8250-pinctrl.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,sm8250-pinctrl.yaml

## Purpose
This schema describes a Qualcomm Top Level Mode Multiplexer controller for one SoC family. It binds the SoC-specific compatible string, register range, interrupt wiring, GPIO range metadata, and the state subnode grammar used by client devices to request pin muxing and electrical configuration. Source title: Qualcomm Technologies, Inc. SM8250 TLMM block. Description signal from the file: Top Level Mode Multiplexer pin controller in the Qualcomm SM8250 SoC.

## Important APIs, Types, and Schema Surface
- Lines read: 120.
- Compatible contract: qcom,sm8250-pinctrl. Top-level required properties: compatible, reg, reg-names. Important top-level properties found in the schema: reg, interrupts, gpio-line-names, gpio-reserved-ranges. Child-node patterns: -state$, -pins$. Function enum sample: aoss_cti, atest, audio_ref, cam_mclk, cci_async, cci_i2c, cci_timer0, cci_timer1, cci_timer2, cci_timer3, cci_timer4, cri_trng, cri_trng0, cri_trng1, dbg_out, ddr_bist plus 99 more. Pin enum sample: sdc2_clk, sdc2_cmd, sdc2_data, ufs_reset. Referenced schemas: #/$defs/qcom-sm8250-tlmm-state, qcom,tlmm-common.yaml#/$defs/qcom-tlmm-state, /schemas/pinctrl/qcom,tlmm-common.yaml#.

## Control Flow
Validation starts at the controller node, applies the shared Qualcomm TLMM schema through `allOf`, then accepts `*-state` children either as direct state objects or as containers of `*-pins` subnodes. Each state must provide `pins`; `function` is optional in schema terms but constrained to the SoC function enum when present. `unevaluatedProperties: false` closes both top-level and state objects after shared TLMM properties are applied.

## State and Persistence Behavior
There is no runtime persistence in the YAML itself. The persistent ABI is the devicetree shape: compatible string, register tuple, GPIO numbering, interrupt line, optional reserved ranges, and stable pin/function names consumed by board DTS files and the Qualcomm pinctrl driver.

## Dependencies and Integration Points
This schema is consumed by Linux devicetree validation tooling (`dt-schema`), board DTS files under architecture trees, and the matching kernel pinctrl/GPIO/interrupt driver. Integration points include `pinctrl.yaml`, generic `pinmux-node.yaml`/`pincfg-node.yaml`, vendor common schemas, dt-bindings headers, GPIO and interrupt-controller bindings, and SoC clock/reset/power-domain providers where referenced.

## Risks and Edge Cases
Primary risks are off-by-one GPIO ranges, stale function names relative to the driver tables, missing SDC special pins, or relaxing child-node closure so invalid board pin states pass dt-schema. Changes should also keep `gpio-line-names` and `gpio-reserved-ranges` maxima aligned with actual GPIO count.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/pinctrl/qcom,sm8250-pinctrl.yaml` and at least one `make dtbs_check` target containing a DTS user of the compatible. For shared helper schemas, run the top-level importing bindings as well. Review the in-file example because it exercises required properties, child-node shape, and referenced dt-bindings constants.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,sm8250-pinctrl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,sm8350-lpass-lpi-pinctrl.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,sm8350-lpass-lpi-pinctrl.yaml

## Purpose
This schema describes the Qualcomm LPASS Low Power Island pin controller. It is narrower than a main TLMM block and validates audio-subsystem pin states, required LPASS clocks, and SoC-specific pin/function enumerations. Source title: Qualcomm SM8350 SoC LPASS LPI TLMM. Description signal from the file: Top Level Mode Multiplexer pin controller in the Low Power Audio SubSystem (LPASS) Low Power Island (LPI) of Qualcomm SM8350 SoC.

## Important APIs, Types, and Schema Surface
- Lines read: 102.
- Compatible contract: qcom,sm8350-lpass-lpi-pinctrl. Top-level required properties: compatible, reg, clocks, clock-names. Important top-level properties found in the schema: reg, clocks, clock-names. Child-node patterns: -state$, -pins$. Function enum sample: dmic1_clk, dmic1_data, dmic2_clk, dmic2_data, dmic3_clk, dmic3_data, dmic4_clk, dmic4_data, ext_mclk1_a, ext_mclk1_b, ext_mclk1_c, ext_mclk1_d, ext_mclk1_e, gpio, i2s0_clk, i2s0_data plus 23 more. Referenced schemas: #/$defs/qcom-sm8350-lpass-state, qcom,lpass-lpi-common.yaml#/$defs/qcom-tlmm-state, qcom,lpass-lpi-common.yaml#.

## Control Flow
Validation requires the LPASS compatible, register range, clocks, and `clock-names`, then delegates common LPI state handling through `qcom,lpass-lpi-common.yaml`. State children use a SoC-local `$defs` entry and inherit the common TLMM state shape for pin configuration fields.

## State and Persistence Behavior
The binding persists LPASS audio pin naming, clock dependency names, and state-node structure used by audio clients. It does not store mutable state, but DTS compatibility depends on stable pin and function labels.

## Dependencies and Integration Points
This schema is consumed by Linux devicetree validation tooling (`dt-schema`), board DTS files under architecture trees, and the matching kernel pinctrl/GPIO/interrupt driver. Integration points include `pinctrl.yaml`, generic `pinmux-node.yaml`/`pincfg-node.yaml`, vendor common schemas, dt-bindings headers, GPIO and interrupt-controller bindings, and SoC clock/reset/power-domain providers where referenced.

## Risks and Edge Cases
High-risk edits include changing clock requirements, removing an alternate compatible fallback, or adding function names not backed by the LPASS pinctrl driver. Audio bring-up can fail quietly if a DTS validates but maps a serial/audio pin to the wrong LPASS function.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/pinctrl/qcom,sm8350-lpass-lpi-pinctrl.yaml` and at least one `make dtbs_check` target containing a DTS user of the compatible. For shared helper schemas, run the top-level importing bindings as well. Review the in-file example because it exercises required properties, child-node shape, and referenced dt-bindings constants.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,sm8350-lpass-lpi-pinctrl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,sm8350-tlmm.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,sm8350-tlmm.yaml

## Purpose
This schema describes a Qualcomm Top Level Mode Multiplexer controller for one SoC family. It binds the SoC-specific compatible string, register range, interrupt wiring, GPIO range metadata, and the state subnode grammar used by client devices to request pin muxing and electrical configuration. Source title: Qualcomm Technologies, Inc. SM8350 TLMM block. Description signal from the file: Top Level Mode Multiplexer pin controller in Qualcomm SM8350 SoC.

## Important APIs, Types, and Schema Surface
- Lines read: 135.
- Compatible contract: qcom,sm8350-tlmm. Top-level required properties: compatible, reg. Important top-level properties found in the schema: reg, interrupts, gpio-line-names, gpio-reserved-ranges. Child-node patterns: -state$, -pins$. Function enum sample: atest_char, atest_usb, audio_ref, cam_mclk, cci_async, cci_i2c, cci_timer, cmu_rng, coex_uart1, coex_uart2, cri_trng, cri_trng0, cri_trng1, dbg_out, ddr_bist, ddr_pxi0 plus 119 more. Pin enum sample: sdc1_clk, sdc1_cmd, sdc1_data, sdc2_clk, sdc2_cmd, sdc2_data. Referenced schemas: /schemas/pinctrl/qcom,tlmm-common.yaml#, #/$defs/qcom-sm8350-tlmm-state, qcom,tlmm-common.yaml#/$defs/qcom-tlmm-state.

## Control Flow
Validation starts at the controller node, applies the shared Qualcomm TLMM schema through `allOf`, then accepts `*-state` children either as direct state objects or as containers of `*-pins` subnodes. Each state must provide `pins`; `function` is optional in schema terms but constrained to the SoC function enum when present. `unevaluatedProperties: false` closes both top-level and state objects after shared TLMM properties are applied.

## State and Persistence Behavior
There is no runtime persistence in the YAML itself. The persistent ABI is the devicetree shape: compatible string, register tuple, GPIO numbering, interrupt line, optional reserved ranges, and stable pin/function names consumed by board DTS files and the Qualcomm pinctrl driver.

## Dependencies and Integration Points
This schema is consumed by Linux devicetree validation tooling (`dt-schema`), board DTS files under architecture trees, and the matching kernel pinctrl/GPIO/interrupt driver. Integration points include `pinctrl.yaml`, generic `pinmux-node.yaml`/`pincfg-node.yaml`, vendor common schemas, dt-bindings headers, GPIO and interrupt-controller bindings, and SoC clock/reset/power-domain providers where referenced.

## Risks and Edge Cases
Primary risks are off-by-one GPIO ranges, stale function names relative to the driver tables, missing SDC special pins, or relaxing child-node closure so invalid board pin states pass dt-schema. Changes should also keep `gpio-line-names` and `gpio-reserved-ranges` maxima aligned with actual GPIO count.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/pinctrl/qcom,sm8350-tlmm.yaml` and at least one `make dtbs_check` target containing a DTS user of the compatible. For shared helper schemas, run the top-level importing bindings as well. Review the in-file example because it exercises required properties, child-node shape, and referenced dt-bindings constants.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,sm8350-tlmm.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,sm8450-lpass-lpi-pinctrl.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,sm8450-lpass-lpi-pinctrl.yaml

## Purpose
This schema describes the Qualcomm LPASS Low Power Island pin controller. It is narrower than a main TLMM block and validates audio-subsystem pin states, required LPASS clocks, and SoC-specific pin/function enumerations. Source title: Qualcomm SM8450 SoC LPASS LPI TLMM. Description signal from the file: Top Level Mode Multiplexer pin controller in the Low Power Audio SubSystem (LPASS) Low Power Island (LPI) of Qualcomm SM8450 SoC.

## Important APIs, Types, and Schema Surface
- Lines read: 129.
- Compatible contract: qcom,sm8450-lpass-lpi-pinctrl, qcom,qcs8300-lpass-lpi-pinctrl, qcom,sa8775p-lpass-lpi-pinctrl. Top-level required properties: compatible, reg, clocks, clock-names. Important top-level properties found in the schema: reg, clocks, clock-names. Child-node patterns: -state$, -pins$. Function enum sample: swr_tx_clk, swr_tx_data, swr_rx_clk, swr_rx_data, dmic1_clk, dmic1_data, dmic2_clk, dmic2_data, dmic4_clk, dmic4_data, i2s2_clk, i2s2_ws, dmic3_clk, dmic3_data, qua_mi2s_sclk, qua_mi2s_ws plus 22 more. Referenced schemas: #/$defs/qcom-sm8450-lpass-state, qcom,lpass-lpi-common.yaml#/$defs/qcom-tlmm-state, qcom,lpass-lpi-common.yaml#.

## Control Flow
Validation requires the LPASS compatible, register range, clocks, and `clock-names`, then delegates common LPI state handling through `qcom,lpass-lpi-common.yaml`. State children use a SoC-local `$defs` entry and inherit the common TLMM state shape for pin configuration fields.

## State and Persistence Behavior
The binding persists LPASS audio pin naming, clock dependency names, and state-node structure used by audio clients. It does not store mutable state, but DTS compatibility depends on stable pin and function labels.

## Dependencies and Integration Points
This schema is consumed by Linux devicetree validation tooling (`dt-schema`), board DTS files under architecture trees, and the matching kernel pinctrl/GPIO/interrupt driver. Integration points include `pinctrl.yaml`, generic `pinmux-node.yaml`/`pincfg-node.yaml`, vendor common schemas, dt-bindings headers, GPIO and interrupt-controller bindings, and SoC clock/reset/power-domain providers where referenced.

## Risks and Edge Cases
High-risk edits include changing clock requirements, removing an alternate compatible fallback, or adding function names not backed by the LPASS pinctrl driver. Audio bring-up can fail quietly if a DTS validates but maps a serial/audio pin to the wrong LPASS function.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/pinctrl/qcom,sm8450-lpass-lpi-pinctrl.yaml` and at least one `make dtbs_check` target containing a DTS user of the compatible. For shared helper schemas, run the top-level importing bindings as well. Review the in-file example because it exercises required properties, child-node shape, and referenced dt-bindings constants.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,sm8450-lpass-lpi-pinctrl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,sm8450-tlmm.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,sm8450-tlmm.yaml

## Purpose
This schema describes a Qualcomm Top Level Mode Multiplexer controller for one SoC family. It binds the SoC-specific compatible string, register range, interrupt wiring, GPIO range metadata, and the state subnode grammar used by client devices to request pin muxing and electrical configuration. Source title: Qualcomm Technologies, Inc. SM8450 TLMM block. Description signal from the file: Top Level Mode Multiplexer pin controller in Qualcomm SM8450 SoC.

## Important APIs, Types, and Schema Surface
- Lines read: 134.
- Compatible contract: qcom,sm8450-tlmm. Top-level required properties: compatible, reg. Important top-level properties found in the schema: reg, interrupts, gpio-line-names, gpio-reserved-ranges. Child-node patterns: -state$, -pins$. Function enum sample: aon_cam, atest_char, atest_usb, audio_ref, cam_mclk, cci_async, cci_i2c, cci_timer, cmu_rng, coex_uart1, coex_uart2, cri_trng, cri_trng0, cri_trng1, dbg_out, ddr_bist plus 119 more. Pin enum sample: ufs_reset, sdc2_clk, sdc2_cmd, sdc2_data. Referenced schemas: /schemas/pinctrl/qcom,tlmm-common.yaml#, #/$defs/qcom-sm8450-tlmm-state, qcom,tlmm-common.yaml#/$defs/qcom-tlmm-state.

## Control Flow
Validation starts at the controller node, applies the shared Qualcomm TLMM schema through `allOf`, then accepts `*-state` children either as direct state objects or as containers of `*-pins` subnodes. Each state must provide `pins`; `function` is optional in schema terms but constrained to the SoC function enum when present. `unevaluatedProperties: false` closes both top-level and state objects after shared TLMM properties are applied.

## State and Persistence Behavior
There is no runtime persistence in the YAML itself. The persistent ABI is the devicetree shape: compatible string, register tuple, GPIO numbering, interrupt line, optional reserved ranges, and stable pin/function names consumed by board DTS files and the Qualcomm pinctrl driver.

## Dependencies and Integration Points
This schema is consumed by Linux devicetree validation tooling (`dt-schema`), board DTS files under architecture trees, and the matching kernel pinctrl/GPIO/interrupt driver. Integration points include `pinctrl.yaml`, generic `pinmux-node.yaml`/`pincfg-node.yaml`, vendor common schemas, dt-bindings headers, GPIO and interrupt-controller bindings, and SoC clock/reset/power-domain providers where referenced.

## Risks and Edge Cases
Primary risks are off-by-one GPIO ranges, stale function names relative to the driver tables, missing SDC special pins, or relaxing child-node closure so invalid board pin states pass dt-schema. Changes should also keep `gpio-line-names` and `gpio-reserved-ranges` maxima aligned with actual GPIO count.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/pinctrl/qcom,sm8450-tlmm.yaml` and at least one `make dtbs_check` target containing a DTS user of the compatible. For shared helper schemas, run the top-level importing bindings as well. Review the in-file example because it exercises required properties, child-node shape, and referenced dt-bindings constants.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,sm8450-tlmm.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,sm8550-lpass-lpi-pinctrl.yaml -->
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

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,sm8550-lpass-lpi-pinctrl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,sm8550-tlmm.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,sm8550-tlmm.yaml

## Purpose
This schema describes a Qualcomm Top Level Mode Multiplexer controller for one SoC family. It binds the SoC-specific compatible string, register range, interrupt wiring, GPIO range metadata, and the state subnode grammar used by client devices to request pin muxing and electrical configuration. Source title: Qualcomm Technologies, Inc. SM8550 TLMM block. Description signal from the file: Top Level Mode Multiplexer pin controller in Qualcomm SM8550 SoC.

## Important APIs, Types, and Schema Surface
- Lines read: 148.
- Compatible contract: qcom,sm8550-tlmm. Top-level required properties: compatible, reg. Important top-level properties found in the schema: reg, interrupts, gpio-line-names, gpio-reserved-ranges. Child-node patterns: -state$, -pins$. Function enum sample: aon_cci, aoss_cti, atest_char, atest_usb, audio_ext_mclk0, audio_ext_mclk1, audio_ref_clk, cam_aon_mclk4, cam_mclk, cci_async_in, cci_i2c_scl, cci_i2c_sda, cci_timer, cmu_rng, coex_uart1_rx, coex_uart1_tx plus 129 more. Pin enum sample: ufs_reset, sdc2_clk, sdc2_cmd, sdc2_data. Referenced schemas: /schemas/pinctrl/qcom,tlmm-common.yaml#, #/$defs/qcom-sm8550-tlmm-state, qcom,tlmm-common.yaml#/$defs/qcom-tlmm-state.

## Control Flow
Validation starts at the controller node, applies the shared Qualcomm TLMM schema through `allOf`, then accepts `*-state` children either as direct state objects or as containers of `*-pins` subnodes. Each state must provide `pins`; `function` is optional in schema terms but constrained to the SoC function enum when present. `unevaluatedProperties: false` closes both top-level and state objects after shared TLMM properties are applied.

## State and Persistence Behavior
There is no runtime persistence in the YAML itself. The persistent ABI is the devicetree shape: compatible string, register tuple, GPIO numbering, interrupt line, optional reserved ranges, and stable pin/function names consumed by board DTS files and the Qualcomm pinctrl driver.

## Dependencies and Integration Points
This schema is consumed by Linux devicetree validation tooling (`dt-schema`), board DTS files under architecture trees, and the matching kernel pinctrl/GPIO/interrupt driver. Integration points include `pinctrl.yaml`, generic `pinmux-node.yaml`/`pincfg-node.yaml`, vendor common schemas, dt-bindings headers, GPIO and interrupt-controller bindings, and SoC clock/reset/power-domain providers where referenced.

## Risks and Edge Cases
Primary risks are off-by-one GPIO ranges, stale function names relative to the driver tables, missing SDC special pins, or relaxing child-node closure so invalid board pin states pass dt-schema. Changes should also keep `gpio-line-names` and `gpio-reserved-ranges` maxima aligned with actual GPIO count.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/pinctrl/qcom,sm8550-tlmm.yaml` and at least one `make dtbs_check` target containing a DTS user of the compatible. For shared helper schemas, run the top-level importing bindings as well. Review the in-file example because it exercises required properties, child-node shape, and referenced dt-bindings constants.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,sm8550-tlmm.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,sm8650-lpass-lpi-pinctrl.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,sm8650-lpass-lpi-pinctrl.yaml

## Purpose
This schema describes the Qualcomm LPASS Low Power Island pin controller. It is narrower than a main TLMM block and validates audio-subsystem pin states, required LPASS clocks, and SoC-specific pin/function enumerations. Source title: Qualcomm SM8650 SoC LPASS LPI TLMM. Description signal from the file: Top Level Mode Multiplexer pin controller in the Low Power Audio SubSystem (LPASS) Low Power Island (LPI) of Qualcomm SM8650 SoC.

## Important APIs, Types, and Schema Surface
- Lines read: 113.
- Compatible contract: qcom,sm8650-lpass-lpi-pinctrl, qcom,glymur-lpass-lpi-pinctrl, qcom,sm8750-lpass-lpi-pinctrl. Top-level required properties: compatible, reg, clocks, clock-names. Important top-level properties found in the schema: reg, clocks, clock-names. Child-node patterns: -state$, -pins$. Function enum sample: dmic1_clk, dmic1_data, dmic2_clk, dmic2_data, dmic3_clk, dmic3_data, dmic4_clk, dmic4_data, ext_mclk1_a, ext_mclk1_b, ext_mclk1_c, ext_mclk1_d, ext_mclk1_e, gpio, i2s0_clk, i2s0_data plus 25 more. Referenced schemas: #/$defs/qcom-sm8650-lpass-state, qcom,lpass-lpi-common.yaml#/$defs/qcom-tlmm-state, qcom,lpass-lpi-common.yaml#.

## Control Flow
Validation requires the LPASS compatible, register range, clocks, and `clock-names`, then delegates common LPI state handling through `qcom,lpass-lpi-common.yaml`. State children use a SoC-local `$defs` entry and inherit the common TLMM state shape for pin configuration fields.

## State and Persistence Behavior
The binding persists LPASS audio pin naming, clock dependency names, and state-node structure used by audio clients. It does not store mutable state, but DTS compatibility depends on stable pin and function labels.

## Dependencies and Integration Points
This schema is consumed by Linux devicetree validation tooling (`dt-schema`), board DTS files under architecture trees, and the matching kernel pinctrl/GPIO/interrupt driver. Integration points include `pinctrl.yaml`, generic `pinmux-node.yaml`/`pincfg-node.yaml`, vendor common schemas, dt-bindings headers, GPIO and interrupt-controller bindings, and SoC clock/reset/power-domain providers where referenced.

## Risks and Edge Cases
High-risk edits include changing clock requirements, removing an alternate compatible fallback, or adding function names not backed by the LPASS pinctrl driver. Audio bring-up can fail quietly if a DTS validates but maps a serial/audio pin to the wrong LPASS function.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/pinctrl/qcom,sm8650-lpass-lpi-pinctrl.yaml` and at least one `make dtbs_check` target containing a DTS user of the compatible. For shared helper schemas, run the top-level importing bindings as well. Review the in-file example because it exercises required properties, child-node shape, and referenced dt-bindings constants.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,sm8650-lpass-lpi-pinctrl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,sm8650-tlmm.yaml -->
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

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,sm8650-tlmm.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,sm8750-tlmm.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,sm8750-tlmm.yaml

## Purpose
This schema describes a Qualcomm Top Level Mode Multiplexer controller for one SoC family. It binds the SoC-specific compatible string, register range, interrupt wiring, GPIO range metadata, and the state subnode grammar used by client devices to request pin muxing and electrical configuration. Source title: Qualcomm Technologies, Inc. SM8750 TLMM block. Description signal from the file: Top Level Mode Multiplexer pin controller in Qualcomm SM8750 SoC.

## Important APIs, Types, and Schema Surface
- Lines read: 138.
- Compatible contract: qcom,sm8750-tlmm. Top-level required properties: compatible, reg. Important top-level properties found in the schema: reg, interrupts, gpio-line-names, gpio-reserved-ranges. Child-node patterns: -state$, -pins$. Function enum sample: gpio, aoss_cti, atest_char, atest_usb, audio_ext_mclk0, audio_ext_mclk1, audio_ref_clk, cam_aon_mclk2, cam_aon_mclk4, cam_mclk, cci_async_in, cci_i2c_scl, cci_i2c_sda, cci_timer, cmu_rng, coex_uart1_rx plus 120 more. Pin enum sample: ufs_reset, sdc2_clk, sdc2_cmd, sdc2_data. Referenced schemas: /schemas/pinctrl/qcom,tlmm-common.yaml#, #/$defs/qcom-sm8750-tlmm-state, qcom,tlmm-common.yaml#/$defs/qcom-tlmm-state.

## Control Flow
Validation starts at the controller node, applies the shared Qualcomm TLMM schema through `allOf`, then accepts `*-state` children either as direct state objects or as containers of `*-pins` subnodes. Each state must provide `pins`; `function` is optional in schema terms but constrained to the SoC function enum when present. `unevaluatedProperties: false` closes both top-level and state objects after shared TLMM properties are applied.

## State and Persistence Behavior
There is no runtime persistence in the YAML itself. The persistent ABI is the devicetree shape: compatible string, register tuple, GPIO numbering, interrupt line, optional reserved ranges, and stable pin/function names consumed by board DTS files and the Qualcomm pinctrl driver.

## Dependencies and Integration Points
This schema is consumed by Linux devicetree validation tooling (`dt-schema`), board DTS files under architecture trees, and the matching kernel pinctrl/GPIO/interrupt driver. Integration points include `pinctrl.yaml`, generic `pinmux-node.yaml`/`pincfg-node.yaml`, vendor common schemas, dt-bindings headers, GPIO and interrupt-controller bindings, and SoC clock/reset/power-domain providers where referenced.

## Risks and Edge Cases
Primary risks are off-by-one GPIO ranges, stale function names relative to the driver tables, missing SDC special pins, or relaxing child-node closure so invalid board pin states pass dt-schema. Changes should also keep `gpio-line-names` and `gpio-reserved-ranges` maxima aligned with actual GPIO count.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/pinctrl/qcom,sm8750-tlmm.yaml` and at least one `make dtbs_check` target containing a DTS user of the compatible. For shared helper schemas, run the top-level importing bindings as well. Review the in-file example because it exercises required properties, child-node shape, and referenced dt-bindings constants.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,sm8750-tlmm.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,tlmm-common.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,tlmm-common.yaml

## Purpose
This shared schema supplies the common Qualcomm TLMM contract reused by SoC-specific Qualcomm bindings. It centralizes GPIO/interrupt controller requirements and the common pin configuration and pin mux node definition. Source title: Qualcomm Technologies, Inc. Top Level Mode Multiplexer (TLMM) definitions. Description signal from the file: This defines the common properties used to describe all Qualcomm Top Level Mode Multiplexer bindings and pinconf/pinmux states for these.

## Important APIs, Types, and Schema Surface
- Lines read: 101.
- Compatible contract: None declared in this schema. Top-level required properties: interrupts, interrupt-controller, #interrupt-cells, gpio-controller, #gpio-cells, gpio-ranges. Important top-level properties found in the schema: interrupts, gpio-controller, interrupt-controller, #gpio-cells, #interrupt-cells, gpio-ranges, gpio-reserved-ranges. Child-node patterns: None declared in this schema. Referenced schemas: pinctrl.yaml#, pincfg-node.yaml#, pinmux-node.yaml#.

## Control Flow
SoC-specific Qualcomm schemas include this file with `allOf`. The common schema validates controller capabilities and defines `$defs/qcom-tlmm-state`, which composes generic `pincfg-node.yaml` and `pinmux-node.yaml` with Qualcomm-specific state allowances.

## State and Persistence Behavior
The file is a shared ABI fragment. Its definitions persist expectations for every importing Qualcomm TLMM schema, including GPIO and interrupt-controller provider cells and permitted state-node properties.

## Dependencies and Integration Points
This schema is consumed by Linux devicetree validation tooling (`dt-schema`), board DTS files under architecture trees, and the matching kernel pinctrl/GPIO/interrupt driver. Integration points include `pinctrl.yaml`, generic `pinmux-node.yaml`/`pincfg-node.yaml`, vendor common schemas, dt-bindings headers, GPIO and interrupt-controller bindings, and SoC clock/reset/power-domain providers where referenced.

## Risks and Edge Cases
Any change here fans out to many Qualcomm SoCs. Tightening or loosening common properties can create broad dtbs_check regressions, so edits need cross-SoC validation rather than testing one binding only.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/pinctrl/qcom,tlmm-common.yaml` and at least one `make dtbs_check` target containing a DTS user of the compatible. For shared helper schemas, run the top-level importing bindings as well. Review the in-file example because it exercises required properties, child-node shape, and referenced dt-bindings constants.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,tlmm-common.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,x1e80100-tlmm.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,x1e80100-tlmm.yaml

## Purpose
This schema describes a Qualcomm Top Level Mode Multiplexer controller for one SoC family. It binds the SoC-specific compatible string, register range, interrupt wiring, GPIO range metadata, and the state subnode grammar used by client devices to request pin muxing and electrical configuration. Source title: Qualcomm Technologies, Inc. X1E80100 TLMM block. Description signal from the file: Top Level Mode Multiplexer pin controller in Qualcomm X1E80100 SoC.

## Important APIs, Types, and Schema Surface
- Lines read: 137.
- Compatible contract: qcom,x1e80100-tlmm. Top-level required properties: compatible, reg. Important top-level properties found in the schema: reg, interrupts, gpio-line-names, gpio-reserved-ranges. Child-node patterns: -state$, -pins$. Function enum sample: aon_cci, aoss_cti, atest_char, atest_char0, atest_char1, atest_char2, atest_char3, atest_usb, audio_ext, audio_ref, cam_aon, cam_mclk, cci_async, cci_i2c, cci_timer0, cci_timer1 plus 134 more. Pin enum sample: ufs_reset, sdc2_clk, sdc2_cmd, sdc2_data. Referenced schemas: /schemas/pinctrl/qcom,tlmm-common.yaml#, #/$defs/qcom-x1e80100-tlmm-state, qcom,tlmm-common.yaml#/$defs/qcom-tlmm-state.

## Control Flow
Validation starts at the controller node, applies the shared Qualcomm TLMM schema through `allOf`, then accepts `*-state` children either as direct state objects or as containers of `*-pins` subnodes. Each state must provide `pins`; `function` is optional in schema terms but constrained to the SoC function enum when present. `unevaluatedProperties: false` closes both top-level and state objects after shared TLMM properties are applied.

## State and Persistence Behavior
There is no runtime persistence in the YAML itself. The persistent ABI is the devicetree shape: compatible string, register tuple, GPIO numbering, interrupt line, optional reserved ranges, and stable pin/function names consumed by board DTS files and the Qualcomm pinctrl driver.

## Dependencies and Integration Points
This schema is consumed by Linux devicetree validation tooling (`dt-schema`), board DTS files under architecture trees, and the matching kernel pinctrl/GPIO/interrupt driver. Integration points include `pinctrl.yaml`, generic `pinmux-node.yaml`/`pincfg-node.yaml`, vendor common schemas, dt-bindings headers, GPIO and interrupt-controller bindings, and SoC clock/reset/power-domain providers where referenced.

## Risks and Edge Cases
Primary risks are off-by-one GPIO ranges, stale function names relative to the driver tables, missing SDC special pins, or relaxing child-node closure so invalid board pin states pass dt-schema. Changes should also keep `gpio-line-names` and `gpio-reserved-ranges` maxima aligned with actual GPIO count.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/pinctrl/qcom,x1e80100-tlmm.yaml` and at least one `make dtbs_check` target containing a DTS user of the compatible. For shared helper schemas, run the top-level importing bindings as well. Review the in-file example because it exercises required properties, child-node shape, and referenced dt-bindings constants.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,x1e80100-tlmm.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/ralink,rt2880-pinctrl.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/ralink,rt2880-pinctrl.yaml

## Purpose
This schema documents an older Ralink SoC pin controller that only selects mux functions at group granularity. It intentionally excludes per-pin muxing and pinconf support, so its binding surface is small but its group/function enum is hardware-specific. Source title: Ralink RT2880 Pin Controller. Description signal from the file: Ralink RT2880 pin controller for RT2880 SoC. The pin controller can only set the muxing of pin groups. Muxing individual pins is not supported. There is no pinconf support.

## Important APIs, Types, and Schema Surface
- Lines read: 141.
- Compatible contract: ralink,rt2880-pinctrl. Top-level required properties: compatible. Important top-level properties found in the schema: None declared in this schema. Child-node patterns: -pins$. Function enum sample: gpio, i2c, spi, uartlite, jtag, mdio, sdram, pci. Referenced schemas: pinmux-node.yaml#, pinctrl.yaml#.

## Control Flow
Validation checks the Ralink compatible, then validates child mux nodes against `pinmux-node.yaml`. Function and group selections are enum-constrained; the schemas intentionally omit generic pinconf properties because the hardware binding only models group muxing.

## State and Persistence Behavior
The persistent ABI is the list of group and function strings used by DTS files. No mutable runtime state is represented in YAML; the pinctrl driver applies the mux selections during device probe and state activation.

## Dependencies and Integration Points
This schema is consumed by Linux devicetree validation tooling (`dt-schema`), board DTS files under architecture trees, and the matching kernel pinctrl/GPIO/interrupt driver. Integration points include `pinctrl.yaml`, generic `pinmux-node.yaml`/`pincfg-node.yaml`, vendor common schemas, dt-bindings headers, GPIO and interrupt-controller bindings, and SoC clock/reset/power-domain providers where referenced.

## Risks and Edge Cases
The main risk is making the schema look more capable than the hardware by accepting per-pin or pinconf properties. Group/function enum drift can also cause board DTS files to validate but fail to select the intended mux.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/pinctrl/ralink,rt2880-pinctrl.yaml` and at least one `make dtbs_check` target containing a DTS user of the compatible. For shared helper schemas, run the top-level importing bindings as well. Review the in-file example because it exercises required properties, child-node shape, and referenced dt-bindings constants.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/ralink,rt2880-pinctrl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/ralink,rt305x-pinctrl.yaml -->
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

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/ralink,rt305x-pinctrl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/ralink,rt3352-pinctrl.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/ralink,rt3352-pinctrl.yaml

## Purpose
This schema documents an older Ralink SoC pin controller that only selects mux functions at group granularity. It intentionally excludes per-pin muxing and pinconf support, so its binding surface is small but its group/function enum is hardware-specific. Source title: Ralink RT3352 Pin Controller. Description signal from the file: Ralink RT3352 pin controller for RT3352 SoC. The pin controller can only set the muxing of pin groups. Muxing individual pins is not supported. There is no pinconf support.

## Important APIs, Types, and Schema Surface
- Lines read: 243.
- Compatible contract: ralink,rt3352-pinctrl. Top-level required properties: compatible. Important top-level properties found in the schema: None declared in this schema. Child-node patterns: -pins$. Function enum sample: gpio, gpio i2s, gpio uartf, i2c, i2s uartf, jtag, led, lna, mdio, pa, pcm gpio, pcm i2s, pcm uartf, rgmii, spi, spi_cs1 plus 3 more. Referenced schemas: pinmux-node.yaml#, pinctrl.yaml#.

## Control Flow
Validation checks the Ralink compatible, then validates child mux nodes against `pinmux-node.yaml`. Function and group selections are enum-constrained; the schemas intentionally omit generic pinconf properties because the hardware binding only models group muxing.

## State and Persistence Behavior
The persistent ABI is the list of group and function strings used by DTS files. No mutable runtime state is represented in YAML; the pinctrl driver applies the mux selections during device probe and state activation.

## Dependencies and Integration Points
This schema is consumed by Linux devicetree validation tooling (`dt-schema`), board DTS files under architecture trees, and the matching kernel pinctrl/GPIO/interrupt driver. Integration points include `pinctrl.yaml`, generic `pinmux-node.yaml`/`pincfg-node.yaml`, vendor common schemas, dt-bindings headers, GPIO and interrupt-controller bindings, and SoC clock/reset/power-domain providers where referenced.

## Risks and Edge Cases
The main risk is making the schema look more capable than the hardware by accepting per-pin or pinconf properties. Group/function enum drift can also cause board DTS files to validate but fail to select the intended mux.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/pinctrl/ralink,rt3352-pinctrl.yaml` and at least one `make dtbs_check` target containing a DTS user of the compatible. For shared helper schemas, run the top-level importing bindings as well. Review the in-file example because it exercises required properties, child-node shape, and referenced dt-bindings constants.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/ralink,rt3352-pinctrl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/ralink,rt3883-pinctrl.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/ralink,rt3883-pinctrl.yaml

## Purpose
This schema documents an older Ralink SoC pin controller that only selects mux functions at group granularity. It intentionally excludes per-pin muxing and pinconf support, so its binding surface is small but its group/function enum is hardware-specific. Source title: Ralink RT3883 Pin Controller. Description signal from the file: Ralink RT3883 pin controller for RT3883 SoC. The pin controller can only set the muxing of pin groups. Muxing individual pins is not supported. There is no pinconf support.

## Important APIs, Types, and Schema Surface
- Lines read: 261.
- Compatible contract: ralink,rt3883-pinctrl. Top-level required properties: compatible. Important top-level properties found in the schema: None declared in this schema. Child-node patterns: -pins$. Function enum sample: ge1, ge2, gpio, gpio i2s, gpio uartf, i2c, i2s uartf, jtag, lna a, lna g, mdio, pci-dev, pci-fnc, pci-host1, pci-host2, pcm gpio plus 5 more. Referenced schemas: pinmux-node.yaml#, pinctrl.yaml#.

## Control Flow
Validation checks the Ralink compatible, then validates child mux nodes against `pinmux-node.yaml`. Function and group selections are enum-constrained; the schemas intentionally omit generic pinconf properties because the hardware binding only models group muxing.

## State and Persistence Behavior
The persistent ABI is the list of group and function strings used by DTS files. No mutable runtime state is represented in YAML; the pinctrl driver applies the mux selections during device probe and state activation.

## Dependencies and Integration Points
This schema is consumed by Linux devicetree validation tooling (`dt-schema`), board DTS files under architecture trees, and the matching kernel pinctrl/GPIO/interrupt driver. Integration points include `pinctrl.yaml`, generic `pinmux-node.yaml`/`pincfg-node.yaml`, vendor common schemas, dt-bindings headers, GPIO and interrupt-controller bindings, and SoC clock/reset/power-domain providers where referenced.

## Risks and Edge Cases
The main risk is making the schema look more capable than the hardware by accepting per-pin or pinconf properties. Group/function enum drift can also cause board DTS files to validate but fail to select the intended mux.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/pinctrl/ralink,rt3883-pinctrl.yaml` and at least one `make dtbs_check` target containing a DTS user of the compatible. For shared helper schemas, run the top-level importing bindings as well. Review the in-file example because it exercises required properties, child-node shape, and referenced dt-bindings constants.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/ralink,rt3883-pinctrl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/ralink,rt5350-pinctrl.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/ralink,rt5350-pinctrl.yaml

## Purpose
This schema documents an older Ralink SoC pin controller that only selects mux functions at group granularity. It intentionally excludes per-pin muxing and pinconf support, so its binding surface is small but its group/function enum is hardware-specific. Source title: Ralink RT5350 Pin Controller. Description signal from the file: Ralink RT5350 pin controller for RT5350 SoC. The pin controller can only set the muxing of pin groups. Muxing individual pins is not supported. There is no pinconf support.

## Important APIs, Types, and Schema Surface
- Lines read: 206.
- Compatible contract: ralink,rt5350-pinctrl. Top-level required properties: compatible. Important top-level properties found in the schema: None declared in this schema. Child-node patterns: -pins$. Function enum sample: gpio, gpio i2s, gpio uartf, i2c, i2s uartf, jtag, led, pcm gpio, pcm i2s, pcm uartf, spi, spi_cs1, uartf, uartlite, wdg_cs1. Referenced schemas: pinmux-node.yaml#, pinctrl.yaml#.

## Control Flow
Validation checks the Ralink compatible, then validates child mux nodes against `pinmux-node.yaml`. Function and group selections are enum-constrained; the schemas intentionally omit generic pinconf properties because the hardware binding only models group muxing.

## State and Persistence Behavior
The persistent ABI is the list of group and function strings used by DTS files. No mutable runtime state is represented in YAML; the pinctrl driver applies the mux selections during device probe and state activation.

## Dependencies and Integration Points
This schema is consumed by Linux devicetree validation tooling (`dt-schema`), board DTS files under architecture trees, and the matching kernel pinctrl/GPIO/interrupt driver. Integration points include `pinctrl.yaml`, generic `pinmux-node.yaml`/`pincfg-node.yaml`, vendor common schemas, dt-bindings headers, GPIO and interrupt-controller bindings, and SoC clock/reset/power-domain providers where referenced.

## Risks and Edge Cases
The main risk is making the schema look more capable than the hardware by accepting per-pin or pinconf properties. Group/function enum drift can also cause board DTS files to validate but fail to select the intended mux.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/pinctrl/ralink,rt5350-pinctrl.yaml` and at least one `make dtbs_check` target containing a DTS user of the compatible. For shared helper schemas, run the top-level importing bindings as well. Review the in-file example because it exercises required properties, child-node shape, and referenced dt-bindings constants.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/ralink,rt5350-pinctrl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/raspberrypi,rp1-gpio.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/raspberrypi,rp1-gpio.yaml

## Purpose
This schema covers the Raspberry Pi RP1 GPIO, pinconf, pinmux, and interrupt-controller submodule. It validates three register banks, GPIO and interrupt provider cells, and nested pin state nodes. Source title: RaspberryPi RP1 GPIO/Pinconf/Pinmux Controller submodule. Description signal from the file: The RP1 chipset is a Multi Function Device containing, among other sub-peripherals, a gpio/pinconf/mux controller whose 54 pins are grouped into 3 banks. It works also as an interrupt controller for those gpios.

## Important APIs, Types, and Schema Surface
- Lines read: 231.
- Compatible contract: raspberrypi,rp1-gpio. Top-level required properties: reg, compatible, #gpio-cells, gpio-controller, interrupts, #interrupt-cells, interrupt-controller. Important top-level properties found in the schema: reg, interrupts, gpio-controller, interrupt-controller, #gpio-cells, #interrupt-cells, gpio-ranges, gpio-line-names. Child-node patterns: -state$, -pins$. Function enum sample: alt0, alt1, alt2, alt3, alt4, gpio, alt6, alt7, alt8, none, aaud, dcd0, dpi, dsi0_te_ext, dsi1_te_ext, dsr0 plus 46 more. Referenced schemas: #/$defs/raspberrypi-rp1-state, pincfg-node.yaml#, pinmux-node.yaml#, pinctrl.yaml#.

## Control Flow
Validation requires three register bank ranges, GPIO and interrupt-controller provider declarations, interrupt lines, and `gpio-ranges`. State nodes use `$defs/raspberrypi-rp1-state` to combine generic pinmux/pinconf properties with RP1 pin numbering and function constraints.

## State and Persistence Behavior
Persistent state is the RP1 MFD submodule topology: bank registers, GPIO numbering across 54 pins, interrupt provider cells, and named pinctrl states used by RP1 clients.

## Dependencies and Integration Points
This schema is consumed by Linux devicetree validation tooling (`dt-schema`), board DTS files under architecture trees, and the matching kernel pinctrl/GPIO/interrupt driver. Integration points include `pinctrl.yaml`, generic `pinmux-node.yaml`/`pincfg-node.yaml`, vendor common schemas, dt-bindings headers, GPIO and interrupt-controller bindings, and SoC clock/reset/power-domain providers where referenced.

## Risks and Edge Cases
Bank count, interrupt count, and GPIO range mismatches are the main hazards. Because RP1 is an MFD submodule, integration tests should validate the parent bus representation and child pin state references together.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/pinctrl/raspberrypi,rp1-gpio.yaml` and at least one `make dtbs_check` target containing a DTS user of the compatible. For shared helper schemas, run the top-level importing bindings as well. Review the in-file example because it exercises required properties, child-node shape, and referenced dt-bindings constants.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/raspberrypi,rp1-gpio.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/realtek,rtd1315e-pinctrl.yaml -->
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

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/realtek,rtd1315e-pinctrl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/realtek,rtd1319d-pinctrl.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/realtek,rtd1319d-pinctrl.yaml

## Purpose
This schema describes a Realtek DHC media SoC pin controller. It validates function mux selection, pin lists, pull settings, drive strength, Schmitt trigger controls, voltage selection, and vendor-specific electrical tuning fields where supported. Source title: Realtek DHC RTD1319D Pin Controller. Description signal from the file: The Realtek DHC RTD1319D is a high-definition media processor SoC. The RTD1319D pin controller is used to control pin function, pull up/down resistor, drive strength, schmitt trigger and power source.

## Important APIs, Types, and Schema Surface
- Lines read: 190.
- Compatible contract: realtek,rtd1319d-pinctrl. Top-level required properties: compatible, reg. Important top-level properties found in the schema: reg. Child-node patterns: -pins$. Function enum sample: gpio, nf, emmc, tp0, tp1, sc0, sc0_data0, sc0_data1, sc0_data2, sc1, sc1_data0, sc1_data1, sc1_data2, ao, gspi_loc0, gspi_loc1 plus 92 more. Pin enum sample: gpio_0, gpio_1, gpio_2, gpio_3, gpio_4, gpio_5, gpio_6, gpio_7, gpio_8, gpio_9, gpio_10, gpio_11, gpio_12, gpio_13, gpio_14, gpio_15 plus 91 more. Referenced schemas: pincfg-node.yaml#, pinmux-node.yaml#, /schemas/types.yaml#/definitions/uint32.

## Control Flow
Validation accepts one Realtek compatible, one register range, and `*-pins` child nodes. Each child composes generic pinconf and pinmux definitions, then restricts `pins`, `function`, and electrical properties to the SoC-specific enum and vendor extensions.

## State and Persistence Behavior
The persistent interface is the DTS pin group name, selected function, and electrical tuning values. For RTD1625 this includes P/N drive strengths, duty-cycle adjustment, high-VIL mode, voltage and slew settings; older RTD schemas focus on pulls, drive, Schmitt, and power source.

## Dependencies and Integration Points
This schema is consumed by Linux devicetree validation tooling (`dt-schema`), board DTS files under architecture trees, and the matching kernel pinctrl/GPIO/interrupt driver. Integration points include `pinctrl.yaml`, generic `pinmux-node.yaml`/`pincfg-node.yaml`, vendor common schemas, dt-bindings headers, GPIO and interrupt-controller bindings, and SoC clock/reset/power-domain providers where referenced.

## Risks and Edge Cases
Electrical tuning fields can affect signal integrity. The risky edits are changing enum meanings, accepting unsupported pin/function combinations, or losing vendor-specific constraints that protect HDMI/I2C, eMMC, SD, and RGMII configurations.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/pinctrl/realtek,rtd1319d-pinctrl.yaml` and at least one `make dtbs_check` target containing a DTS user of the compatible. For shared helper schemas, run the top-level importing bindings as well. Review the in-file example because it exercises required properties, child-node shape, and referenced dt-bindings constants.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/realtek,rtd1319d-pinctrl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/realtek,rtd1619b-pinctrl.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/realtek,rtd1619b-pinctrl.yaml

## Purpose
This schema describes a Realtek DHC media SoC pin controller. It validates function mux selection, pin lists, pull settings, drive strength, Schmitt trigger controls, voltage selection, and vendor-specific electrical tuning fields where supported. Source title: Realtek DHC RTD1619B Pin Controller. Description signal from the file: The Realtek DHC RTD1619B is a high-definition media processor SoC. The RTD1619B pin controller is used to control pin function, pull up/down resistor, drive strength, schmitt trigger and power source.

## Important APIs, Types, and Schema Surface
- Lines read: 189.
- Compatible contract: realtek,rtd1619b-pinctrl. Top-level required properties: compatible, reg. Important top-level properties found in the schema: reg. Child-node patterns: -pins$. Function enum sample: gpio, nf, nf_spi, spi, pmic, spdif, spdif_coaxial, spdif_optical_loc0, spdif_optical_loc1, emmc_spi, emmc, sc1, uart0, uart1, uart2_loc0, uart2_loc1 plus 87 more. Pin enum sample: gpio_0, gpio_1, gpio_2, gpio_3, gpio_4, gpio_5, gpio_6, gpio_7, gpio_8, gpio_9, gpio_10, gpio_11, gpio_12, gpio_13, gpio_14, gpio_15 plus 96 more. Referenced schemas: pincfg-node.yaml#, pinmux-node.yaml#, /schemas/types.yaml#/definitions/uint32.

## Control Flow
Validation accepts one Realtek compatible, one register range, and `*-pins` child nodes. Each child composes generic pinconf and pinmux definitions, then restricts `pins`, `function`, and electrical properties to the SoC-specific enum and vendor extensions.

## State and Persistence Behavior
The persistent interface is the DTS pin group name, selected function, and electrical tuning values. For RTD1625 this includes P/N drive strengths, duty-cycle adjustment, high-VIL mode, voltage and slew settings; older RTD schemas focus on pulls, drive, Schmitt, and power source.

## Dependencies and Integration Points
This schema is consumed by Linux devicetree validation tooling (`dt-schema`), board DTS files under architecture trees, and the matching kernel pinctrl/GPIO/interrupt driver. Integration points include `pinctrl.yaml`, generic `pinmux-node.yaml`/`pincfg-node.yaml`, vendor common schemas, dt-bindings headers, GPIO and interrupt-controller bindings, and SoC clock/reset/power-domain providers where referenced.

## Risks and Edge Cases
Electrical tuning fields can affect signal integrity. The risky edits are changing enum meanings, accepting unsupported pin/function combinations, or losing vendor-specific constraints that protect HDMI/I2C, eMMC, SD, and RGMII configurations.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/pinctrl/realtek,rtd1619b-pinctrl.yaml` and at least one `make dtbs_check` target containing a DTS user of the compatible. For shared helper schemas, run the top-level importing bindings as well. Review the in-file example because it exercises required properties, child-node shape, and referenced dt-bindings constants.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/realtek,rtd1619b-pinctrl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/realtek,rtd1625-pinctrl.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/realtek,rtd1625-pinctrl.yaml

## Purpose
This schema describes a Realtek DHC media SoC pin controller. It validates function mux selection, pin lists, pull settings, drive strength, Schmitt trigger controls, voltage selection, and vendor-specific electrical tuning fields where supported. Source title: Realtek DHC RTD1625 Pin Controller. Description signal from the file: The Realtek DHC RTD1625 is a high-definition media processor SoC. The RTD1625 pin controller is used to control pin function, pull-up/down resistors, drive strength, slew rate, Schmitt trigger, power source (I/O output voltage), input threshold domain selection and a higher-VIL mode.

## Important APIs, Types, and Schema Surface
- Lines read: 260.
- Compatible contract: realtek,rtd1625-iso-pinctrl, realtek,rtd1625-main2-pinctrl, realtek,rtd1625-isom-pinctrl, realtek,rtd1625-ve4-pinctrl. Top-level required properties: compatible, reg. Important top-level properties found in the schema: reg. Child-node patterns: -pins$. Function enum sample: gpio, ai_i2s0, ai_i2s2, ai_tdm0, ai_tdm1, ai_tdm2, ao_i2s0, ao_i2s2, ao_tdm0, ao_tdm1, ao_tdm2, csi0, csi1, csi_1v2, csi_1v8, csi_2v5 plus 119 more. Pin enum sample: gpio_0, gpio_1, gpio_2, gpio_3, gpio_4, gpio_5, gpio_6, gpio_7, gpio_8, gpio_9, gpio_10, gpio_11, gpio_12, gpio_13, gpio_14, gpio_15 plus 155 more. Referenced schemas: pincfg-node.yaml#, pinmux-node.yaml#, /schemas/types.yaml#/definitions/uint32.

## Control Flow
Validation accepts one Realtek compatible, one register range, and `*-pins` child nodes. Each child composes generic pinconf and pinmux definitions, then restricts `pins`, `function`, and electrical properties to the SoC-specific enum and vendor extensions.

## State and Persistence Behavior
The persistent interface is the DTS pin group name, selected function, and electrical tuning values. For RTD1625 this includes P/N drive strengths, duty-cycle adjustment, high-VIL mode, voltage and slew settings; older RTD schemas focus on pulls, drive, Schmitt, and power source.

## Dependencies and Integration Points
This schema is consumed by Linux devicetree validation tooling (`dt-schema`), board DTS files under architecture trees, and the matching kernel pinctrl/GPIO/interrupt driver. Integration points include `pinctrl.yaml`, generic `pinmux-node.yaml`/`pincfg-node.yaml`, vendor common schemas, dt-bindings headers, GPIO and interrupt-controller bindings, and SoC clock/reset/power-domain providers where referenced.

## Risks and Edge Cases
Electrical tuning fields can affect signal integrity. The risky edits are changing enum meanings, accepting unsupported pin/function combinations, or losing vendor-specific constraints that protect HDMI/I2C, eMMC, SD, and RGMII configurations.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/pinctrl/realtek,rtd1625-pinctrl.yaml` and at least one `make dtbs_check` target containing a DTS user of the compatible. For shared helper schemas, run the top-level importing bindings as well. Review the in-file example because it exercises required properties, child-node shape, and referenced dt-bindings constants.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/realtek,rtd1625-pinctrl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/renesas,pfc.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/renesas,pfc.yaml

## Purpose
This schema describes a Renesas combined pin and GPIO or PFC block. It validates compatible-specific controller resources plus child pinmux/pinconf nodes that encode port, pin, and alternate-function selections. Source title: Renesas Pin Function Controller (GPIO and Pin Mux/Config). Description signal from the file: The Pin Function Controller (PFC) is a Pin Mux/Config controller. On SH/R-Mobile SoCs it also acts as a GPIO controller.

## Important APIs, Types, and Schema Surface
- Lines read: 196.
- Compatible contract: renesas,pfc-emev2, renesas,pfc-r8a73a4, renesas,pfc-r8a7740, renesas,pfc-r8a7742, renesas,pfc-r8a7743, renesas,pfc-r8a7744, renesas,pfc-r8a7745, renesas,pfc-r8a77470, renesas,pfc-r8a774a1, renesas,pfc-r8a774a3 plus 23 more. Top-level required properties: compatible, reg. Important top-level properties found in the schema: reg, interrupts-extended, power-domains, gpio-controller, #gpio-cells, gpio-ranges. Child-node patterns: None declared in this schema. Referenced schemas: pinctrl.yaml#, pincfg-node.yaml#, pinmux-node.yaml#, #/additionalProperties/anyOf/0.

## Control Flow
Validation starts with compatible-specific resources, then uses nested child objects for pinmux and pin configuration. Most Renesas bindings compose generic `pincfg-node.yaml`, `pinmux-node.yaml`, and `pinctrl.yaml`, with helper macros in dt-bindings headers encoding port/pin/function values.

## State and Persistence Behavior
Persistent state is the controller resource set, GPIO/interrupt provider shape where present, and the encoded pinmux values used by client pinctrl states. The YAML has no runtime storage but is a stable ABI for Renesas board DTS files.

## Dependencies and Integration Points
This schema is consumed by Linux devicetree validation tooling (`dt-schema`), board DTS files under architecture trees, and the matching kernel pinctrl/GPIO/interrupt driver. Integration points include `pinctrl.yaml`, generic `pinmux-node.yaml`/`pincfg-node.yaml`, vendor common schemas, dt-bindings headers, GPIO and interrupt-controller bindings, and SoC clock/reset/power-domain providers where referenced.

## Risks and Edge Cases
Risks concentrate around reset/clock requirements, GPIO cell semantics, and SoC-specific port encoding. Conditional compatible fallbacks and allowed electrical values should be tested with representative DTS examples and driver tables.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/pinctrl/renesas,pfc.yaml` and at least one `make dtbs_check` target containing a DTS user of the compatible. For shared helper schemas, run the top-level importing bindings as well. Review the in-file example because it exercises required properties, child-node shape, and referenced dt-bindings constants.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/renesas,pfc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/renesas,r9a09g077-pinctrl.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/renesas,r9a09g077-pinctrl.yaml

## Purpose
This schema describes a Renesas combined pin and GPIO or PFC block. It validates compatible-specific controller resources plus child pinmux/pinconf nodes that encode port, pin, and alternate-function selections. Source title: Renesas RZ/T2H and RZ/N2H Pin and GPIO controller. Description signal from the file: The Renesas RZ/T2H and RZ/N2H SoCs feature a combined Pin and GPIO controller. Pin multiplexing and GPIO configuration are performed on a per-pin basis. Each port supports up to 8 pins, each configurable for either GPIO (port mode) or alternate function mode. Each pin supports function mode values ranging from 0x0 to 0x2A, allowing selection from up to 43 different functions.

## Important APIs, Types, and Schema Surface
- Lines read: 202.
- Compatible contract: renesas,r9a09g077-pinctrl, renesas,r9a09g087-pinctrl. Top-level required properties: compatible, reg, reg-names, gpio-controller, #gpio-cells, gpio-ranges, clocks, power-domains. Important top-level properties found in the schema: reg, clocks, power-domains, gpio-controller, interrupt-controller, #gpio-cells, #interrupt-cells, gpio-ranges. Child-node patterns: -pins$. Referenced schemas: pincfg-node.yaml#, pinmux-node.yaml#, #/definitions/renesas-rzt2h-n2h-pins-node, pinctrl.yaml#.

## Control Flow
Validation starts with compatible-specific resources, then uses nested child objects for pinmux and pin configuration. Most Renesas bindings compose generic `pincfg-node.yaml`, `pinmux-node.yaml`, and `pinctrl.yaml`, with helper macros in dt-bindings headers encoding port/pin/function values.

## State and Persistence Behavior
Persistent state is the controller resource set, GPIO/interrupt provider shape where present, and the encoded pinmux values used by client pinctrl states. The YAML has no runtime storage but is a stable ABI for Renesas board DTS files.

## Dependencies and Integration Points
This schema is consumed by Linux devicetree validation tooling (`dt-schema`), board DTS files under architecture trees, and the matching kernel pinctrl/GPIO/interrupt driver. Integration points include `pinctrl.yaml`, generic `pinmux-node.yaml`/`pincfg-node.yaml`, vendor common schemas, dt-bindings headers, GPIO and interrupt-controller bindings, and SoC clock/reset/power-domain providers where referenced.

## Risks and Edge Cases
Risks concentrate around reset/clock requirements, GPIO cell semantics, and SoC-specific port encoding. Conditional compatible fallbacks and allowed electrical values should be tested with representative DTS examples and driver tables.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/pinctrl/renesas,r9a09g077-pinctrl.yaml` and at least one `make dtbs_check` target containing a DTS user of the compatible. For shared helper schemas, run the top-level importing bindings as well. Review the in-file example because it exercises required properties, child-node shape, and referenced dt-bindings constants.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/renesas,r9a09g077-pinctrl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/renesas,rza1-ports.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/renesas,rza1-ports.yaml

## Purpose
This schema describes a Renesas combined pin and GPIO or PFC block. It validates compatible-specific controller resources plus child pinmux/pinconf nodes that encode port, pin, and alternate-function selections. Source title: Renesas RZ/A1 combined Pin and GPIO controller. Description signal from the file: The Renesas SoCs of the RZ/A1 family feature a combined Pin and GPIO controller, named "Ports" in the hardware reference manual. Pin multiplexing and GPIO configuration is performed on a per-pin basis writing configuration values to per-port register sets. Each "port" features up to 16 pins, each of them configurable for GPIO function (port mode) or in alternate function mode. Up to 8 different alternate function modes exist for each single pin.

## Important APIs, Types, and Schema Surface
- Lines read: 187.
- Compatible contract: renesas,r7s72100-ports, renesas,r7s72101-ports, renesas,r7s72102-ports. Top-level required properties: compatible, reg. Important top-level properties found in the schema: reg. Child-node patterns: None declared in this schema. Referenced schemas: pinctrl.yaml#, pincfg-node.yaml#, pinmux-node.yaml#, #/additionalProperties/anyOf/0.

## Control Flow
Validation starts with compatible-specific resources, then uses nested child objects for pinmux and pin configuration. Most Renesas bindings compose generic `pincfg-node.yaml`, `pinmux-node.yaml`, and `pinctrl.yaml`, with helper macros in dt-bindings headers encoding port/pin/function values.

## State and Persistence Behavior
Persistent state is the controller resource set, GPIO/interrupt provider shape where present, and the encoded pinmux values used by client pinctrl states. The YAML has no runtime storage but is a stable ABI for Renesas board DTS files.

## Dependencies and Integration Points
This schema is consumed by Linux devicetree validation tooling (`dt-schema`), board DTS files under architecture trees, and the matching kernel pinctrl/GPIO/interrupt driver. Integration points include `pinctrl.yaml`, generic `pinmux-node.yaml`/`pincfg-node.yaml`, vendor common schemas, dt-bindings headers, GPIO and interrupt-controller bindings, and SoC clock/reset/power-domain providers where referenced.

## Risks and Edge Cases
Risks concentrate around reset/clock requirements, GPIO cell semantics, and SoC-specific port encoding. Conditional compatible fallbacks and allowed electrical values should be tested with representative DTS examples and driver tables.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/pinctrl/renesas,rza1-ports.yaml` and at least one `make dtbs_check` target containing a DTS user of the compatible. For shared helper schemas, run the top-level importing bindings as well. Review the in-file example because it exercises required properties, child-node shape, and referenced dt-bindings constants.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/renesas,rza1-ports.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/renesas,rza2-pinctrl.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/renesas,rza2-pinctrl.yaml

## Purpose
This schema describes a Renesas combined pin and GPIO or PFC block. It validates compatible-specific controller resources plus child pinmux/pinconf nodes that encode port, pin, and alternate-function selections. Source title: Renesas RZ/A2 combined Pin and GPIO controller. Description signal from the file: The Renesas SoCs of the RZ/A2 series feature a combined Pin and GPIO controller. Pin multiplexing and GPIO configuration is performed on a per-pin basis. Each port features up to 8 pins, each of them configurable for GPIO function (port mode) or in alternate function mode. Up to 8 different alternate function modes exist for each single pin.

## Important APIs, Types, and Schema Surface
- Lines read: 98.
- Compatible contract: renesas,r7s9210-pinctrl. Top-level required properties: compatible, reg, gpio-controller, #gpio-cells, gpio-ranges. Important top-level properties found in the schema: reg, gpio-controller, #gpio-cells, gpio-ranges. Child-node patterns: None declared in this schema. Referenced schemas: pincfg-node.yaml#, pinmux-node.yaml#, pinctrl.yaml#.

## Control Flow
Validation starts with compatible-specific resources, then uses nested child objects for pinmux and pin configuration. Most Renesas bindings compose generic `pincfg-node.yaml`, `pinmux-node.yaml`, and `pinctrl.yaml`, with helper macros in dt-bindings headers encoding port/pin/function values.

## State and Persistence Behavior
Persistent state is the controller resource set, GPIO/interrupt provider shape where present, and the encoded pinmux values used by client pinctrl states. The YAML has no runtime storage but is a stable ABI for Renesas board DTS files.

## Dependencies and Integration Points
This schema is consumed by Linux devicetree validation tooling (`dt-schema`), board DTS files under architecture trees, and the matching kernel pinctrl/GPIO/interrupt driver. Integration points include `pinctrl.yaml`, generic `pinmux-node.yaml`/`pincfg-node.yaml`, vendor common schemas, dt-bindings headers, GPIO and interrupt-controller bindings, and SoC clock/reset/power-domain providers where referenced.

## Risks and Edge Cases
Risks concentrate around reset/clock requirements, GPIO cell semantics, and SoC-specific port encoding. Conditional compatible fallbacks and allowed electrical values should be tested with representative DTS examples and driver tables.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/pinctrl/renesas,rza2-pinctrl.yaml` and at least one `make dtbs_check` target containing a DTS user of the compatible. For shared helper schemas, run the top-level importing bindings as well. Review the in-file example because it exercises required properties, child-node shape, and referenced dt-bindings constants.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/renesas,rza2-pinctrl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/renesas,rzg2l-pinctrl.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/renesas,rzg2l-pinctrl.yaml

## Purpose
This schema describes a Renesas combined pin and GPIO or PFC block. It validates compatible-specific controller resources plus child pinmux/pinconf nodes that encode port, pin, and alternate-function selections. Source title: Renesas RZ/{G2L,V2L} combined Pin and GPIO controller. Description signal from the file: The Renesas SoCs of the RZ/{G2L,V2L} alike series feature a combined Pin and GPIO controller. Pin multiplexing and GPIO configuration is performed on a per-pin basis. Each port features up to 8 pins, each of them configurable for GPIO function (port mode) or in alternate function mode. Up to 8 different alternate function modes exist for each single pin.

## Important APIs, Types, and Schema Surface
- Lines read: 226.
- Compatible contract: renesas,r9a07g043-pinctrl, renesas,r9a07g044-pinctrl, renesas,r9a08g045-pinctrl, renesas,r9a09g047-pinctrl, renesas,r9a09g056-pinctrl, renesas,r9a09g057-pinctrl, renesas,r9a07g054-pinctrl. Top-level required properties: compatible, reg, gpio-controller, #gpio-cells, gpio-ranges, interrupt-controller, #interrupt-cells, clocks, power-domains, resets. Important top-level properties found in the schema: reg, clocks, resets, power-domains, gpio-controller, interrupt-controller, #gpio-cells, #interrupt-cells, gpio-ranges. Child-node patterns: None declared in this schema. Referenced schemas: pincfg-node.yaml#, pinmux-node.yaml#, /schemas/types.yaml#/definitions/uint32, #/additionalProperties/anyOf/0, pinctrl.yaml#.

## Control Flow
Validation starts with compatible-specific resources, then uses nested child objects for pinmux and pin configuration. Most Renesas bindings compose generic `pincfg-node.yaml`, `pinmux-node.yaml`, and `pinctrl.yaml`, with helper macros in dt-bindings headers encoding port/pin/function values.

## State and Persistence Behavior
Persistent state is the controller resource set, GPIO/interrupt provider shape where present, and the encoded pinmux values used by client pinctrl states. The YAML has no runtime storage but is a stable ABI for Renesas board DTS files.

## Dependencies and Integration Points
This schema is consumed by Linux devicetree validation tooling (`dt-schema`), board DTS files under architecture trees, and the matching kernel pinctrl/GPIO/interrupt driver. Integration points include `pinctrl.yaml`, generic `pinmux-node.yaml`/`pincfg-node.yaml`, vendor common schemas, dt-bindings headers, GPIO and interrupt-controller bindings, and SoC clock/reset/power-domain providers where referenced.

## Risks and Edge Cases
Risks concentrate around reset/clock requirements, GPIO cell semantics, and SoC-specific port encoding. Conditional compatible fallbacks and allowed electrical values should be tested with representative DTS examples and driver tables.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/pinctrl/renesas,rzg2l-pinctrl.yaml` and at least one `make dtbs_check` target containing a DTS user of the compatible. For shared helper schemas, run the top-level importing bindings as well. Review the in-file example because it exercises required properties, child-node shape, and referenced dt-bindings constants.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/renesas,rzg2l-pinctrl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/renesas,rzg2l-poeg.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/renesas,rzg2l-poeg.yaml

## Purpose
This schema is for Renesas RZ/G2L Port Output Enable for GPT rather than a general pinctrl provider. It validates the safety/control sideband that can disable timer output pins through POEG inputs and GPT linkage. Source title: Renesas RZ/G2L Port Output Enable for GPT (POEG). Description signal from the file: The output pins(GTIOCxA and GTIOCxB) of the general PWM timer (GPT) can be disabled by using the port output enabling function for the GPT (POEG). Specifically, either of the following ways can be used. * Input level detection of the GTETRGA to GTETRGD pins. * Output-disable request from the GPT. * SSF bit setting(ie, by setting POEGGn.SSF to 1) The state of the GTIOCxA and the GTIOCxB pins when the output is disabled, are controlled by the GPT m

## Important APIs, Types, and Schema Surface
- Lines read: 86.
- Compatible contract: renesas,r9a07g044-poeg, renesas,r9a07g054-poeg, renesas,rzg2l-poeg, renesas,poeg-id, renesas,gpt. Top-level required properties: compatible, reg, interrupts, clocks, power-domains, resets, renesas,poeg-id, renesas,gpt. Important top-level properties found in the schema: reg, interrupts, clocks, resets, power-domains, renesas,poeg-id, renesas,gpt. Child-node patterns: None declared in this schema. Referenced schemas: /schemas/types.yaml#/definitions/phandle, /schemas/types.yaml#/definitions/uint32.

## Control Flow
Validation requires POEG resources, interrupt, clock/reset/power-domain wiring, a `renesas,poeg-id`, and a `renesas,gpt` phandle. Unlike pinmux schemas, there are no arbitrary pin state children; the control flow models a fixed hardware sideband relation to GPT outputs.

## State and Persistence Behavior
Persistent ABI is the POEG node identity and linkage to the GPT provider. The runtime driver can use this relationship to disable timer outputs according to hardware input conditions, but the YAML only validates the static topology.

## Dependencies and Integration Points
This schema is consumed by Linux devicetree validation tooling (`dt-schema`), board DTS files under architecture trees, and the matching kernel pinctrl/GPIO/interrupt driver. Integration points include `pinctrl.yaml`, generic `pinmux-node.yaml`/`pincfg-node.yaml`, vendor common schemas, dt-bindings headers, GPIO and interrupt-controller bindings, and SoC clock/reset/power-domain providers where referenced.

## Risks and Edge Cases
Wrong phandle typing or POEG ID constraints can misrepresent safety-related timer output disable wiring. Tests should include the documented compatible fallback and required resource set.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/pinctrl/renesas,rzg2l-poeg.yaml` and at least one `make dtbs_check` target containing a DTS user of the compatible. For shared helper schemas, run the top-level importing bindings as well. Review the in-file example because it exercises required properties, child-node shape, and referenced dt-bindings constants.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/renesas,rzg2l-poeg.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/renesas,rzn1-pinctrl.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/renesas,rzn1-pinctrl.yaml

## Purpose
This schema describes a Renesas combined pin and GPIO or PFC block. It validates compatible-specific controller resources plus child pinmux/pinconf nodes that encode port, pin, and alternate-function selections. Source title: Renesas RZ/N1 Pin Controller. Description signal from the file: No long-form description is present; the binding contract is carried by the schema properties and examples.

## Important APIs, Types, and Schema Surface
- Lines read: 126.
- Compatible contract: renesas,r9a06g032-pinctrl, renesas,rzn1-pinctrl. Top-level required properties: compatible, reg, clocks, clock-names. Important top-level properties found in the schema: reg, clocks, clock-names. Child-node patterns: None declared in this schema. Referenced schemas: pinctrl.yaml#, pincfg-node.yaml#, pinmux-node.yaml#, #/additionalProperties/anyOf/0.

## Control Flow
Validation starts with compatible-specific resources, then uses nested child objects for pinmux and pin configuration. Most Renesas bindings compose generic `pincfg-node.yaml`, `pinmux-node.yaml`, and `pinctrl.yaml`, with helper macros in dt-bindings headers encoding port/pin/function values.

## State and Persistence Behavior
Persistent state is the controller resource set, GPIO/interrupt provider shape where present, and the encoded pinmux values used by client pinctrl states. The YAML has no runtime storage but is a stable ABI for Renesas board DTS files.

## Dependencies and Integration Points
This schema is consumed by Linux devicetree validation tooling (`dt-schema`), board DTS files under architecture trees, and the matching kernel pinctrl/GPIO/interrupt driver. Integration points include `pinctrl.yaml`, generic `pinmux-node.yaml`/`pincfg-node.yaml`, vendor common schemas, dt-bindings headers, GPIO and interrupt-controller bindings, and SoC clock/reset/power-domain providers where referenced.

## Risks and Edge Cases
Risks concentrate around reset/clock requirements, GPIO cell semantics, and SoC-specific port encoding. Conditional compatible fallbacks and allowed electrical values should be tested with representative DTS examples and driver tables.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/pinctrl/renesas,rzn1-pinctrl.yaml` and at least one `make dtbs_check` target containing a DTS user of the compatible. For shared helper schemas, run the top-level importing bindings as well. Review the in-file example because it exercises required properties, child-node shape, and referenced dt-bindings constants.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/renesas,rzn1-pinctrl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/renesas,rzv2m-pinctrl.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/renesas,rzv2m-pinctrl.yaml

## Purpose
This schema describes a Renesas combined pin and GPIO or PFC block. It validates compatible-specific controller resources plus child pinmux/pinconf nodes that encode port, pin, and alternate-function selections. Source title: Renesas RZ/V2M combined Pin and GPIO controller. Description signal from the file: The Renesas RZ/V2M SoC features a combined Pin and GPIO controller. Pin multiplexing and GPIO configuration is performed on a per-pin basis. Each port features up to 16 pins, each of them configurable for GPIO function (port mode) or in alternate function mode. Up to 8 different alternate function modes exist for each single pin.

## Important APIs, Types, and Schema Surface
- Lines read: 167.
- Compatible contract: renesas,r9a09g011-pinctrl. Top-level required properties: compatible, reg, gpio-controller, #gpio-cells, gpio-ranges, interrupts, clocks, power-domains, resets. Important top-level properties found in the schema: reg, interrupts, clocks, resets, power-domains, gpio-controller, #gpio-cells, gpio-ranges. Child-node patterns: None declared in this schema. Referenced schemas: pincfg-node.yaml#, pinmux-node.yaml#, #/additionalProperties/anyOf/0, pinctrl.yaml#.

## Control Flow
Validation starts with compatible-specific resources, then uses nested child objects for pinmux and pin configuration. Most Renesas bindings compose generic `pincfg-node.yaml`, `pinmux-node.yaml`, and `pinctrl.yaml`, with helper macros in dt-bindings headers encoding port/pin/function values.

## State and Persistence Behavior
Persistent state is the controller resource set, GPIO/interrupt provider shape where present, and the encoded pinmux values used by client pinctrl states. The YAML has no runtime storage but is a stable ABI for Renesas board DTS files.

## Dependencies and Integration Points
This schema is consumed by Linux devicetree validation tooling (`dt-schema`), board DTS files under architecture trees, and the matching kernel pinctrl/GPIO/interrupt driver. Integration points include `pinctrl.yaml`, generic `pinmux-node.yaml`/`pincfg-node.yaml`, vendor common schemas, dt-bindings headers, GPIO and interrupt-controller bindings, and SoC clock/reset/power-domain providers where referenced.

## Risks and Edge Cases
Risks concentrate around reset/clock requirements, GPIO cell semantics, and SoC-specific port encoding. Conditional compatible fallbacks and allowed electrical values should be tested with representative DTS examples and driver tables.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/pinctrl/renesas,rzv2m-pinctrl.yaml` and at least one `make dtbs_check` target containing a DTS user of the compatible. For shared helper schemas, run the top-level importing bindings as well. Review the in-file example because it exercises required properties, child-node shape, and referenced dt-bindings constants.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/renesas,rzv2m-pinctrl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/rockchip,pinctrl.yaml -->
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

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/rockchip,pinctrl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/samsung,pinctrl-gpio-bank.yaml -->
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

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/samsung,pinctrl-gpio-bank.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/samsung,pinctrl-pins-cfg.yaml -->
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

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/samsung,pinctrl-pins-cfg.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/samsung,pinctrl-wakeup-interrupt.yaml -->
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

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/samsung,pinctrl-wakeup-interrupt.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/samsung,pinctrl.yaml -->
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

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/samsung,pinctrl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/semtech,sx1501q.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/semtech,sx1501q.yaml

## Purpose
This schema describes the I2C-attached Semtech SX150x GPIO expander family. It combines GPIO provider, optional interrupt provider, and pin configuration child nodes with chip-specific GPIO and OSCIO pin limits. Source title: Semtech SX150x GPIO expander. Description signal from the file: No long-form description is present; the binding contract is carried by the schema properties and examples.

## Important APIs, Types, and Schema Surface
- Lines read: 251.
- Compatible contract: semtech,sx1501q, semtech,sx1502q, semtech,sx1503q, semtech,sx1504q, semtech,sx1505q, semtech,sx1506q, semtech,sx1507q, semtech,sx1508q, semtech,sx1509q. Top-level required properties: compatible, reg, #gpio-cells, gpio-controller. Important top-level properties found in the schema: reg, interrupts, gpio-controller, interrupt-controller, #gpio-cells, #interrupt-cells, gpio-line-names, semtech,probe-reset. Child-node patterns: -cfg$. Referenced schemas: pincfg-node.yaml#, pinmux-node.yaml#, pinctrl.yaml#.

## Control Flow
Validation first selects the SX150x compatible, then conditional `allOf` branches set `gpio-line-names` cardinality and allowed `pins` patterns for each chip width. `*-cfg` children combine pinconf and pinmux schema references; OSCIO pins deliberately reject bias and open-drain properties.

## State and Persistence Behavior
Persistent state is the I2C address, GPIO/interrupt provider cells, optional `semtech,probe-reset`, and named child configs. The schema encodes family capabilities so existing DTS files remain tied to the correct 4, 8, or 16 GPIO variants plus optional OSCIO.

## Dependencies and Integration Points
This schema is consumed by Linux devicetree validation tooling (`dt-schema`), board DTS files under architecture trees, and the matching kernel pinctrl/GPIO/interrupt driver. Integration points include `pinctrl.yaml`, generic `pinmux-node.yaml`/`pincfg-node.yaml`, vendor common schemas, dt-bindings headers, GPIO and interrupt-controller bindings, and SoC clock/reset/power-domain providers where referenced.

## Risks and Edge Cases
Main risks are permitting `semtech,probe-reset` on older devices, accepting the wrong GPIO count, or allowing OSCIO-only invalid electrical settings. Tests should cover each conditional compatible family.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/pinctrl/semtech,sx1501q.yaml` and at least one `make dtbs_check` target containing a DTS user of the compatible. For shared helper schemas, run the top-level importing bindings as well. Review the in-file example because it exercises required properties, child-node shape, and referenced dt-bindings constants.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/semtech,sx1501q.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/socionext,uniphier-pinctrl.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/socionext,uniphier-pinctrl.yaml

## Purpose
This schema describes Socionext UniPhier pin controllers. It uses standard pinmux and pinconf child nodes and a broad compatible enum across UniPhier SoC generations. Source title: UniPhier SoCs pin controller. Description signal from the file: No long-form description is present; the binding contract is carried by the schema properties and examples.

## Important APIs, Types, and Schema Surface
- Lines read: 84.
- Compatible contract: socionext,uniphier-ld4-pinctrl, socionext,uniphier-pro4-pinctrl, socionext,uniphier-sld8-pinctrl, socionext,uniphier-pro5-pinctrl, socionext,uniphier-pxs2-pinctrl, socionext,uniphier-ld6b-pinctrl, socionext,uniphier-ld11-pinctrl, socionext,uniphier-ld20-pinctrl, socionext,uniphier-pxs3-pinctrl, socionext,uniphier-nx1-pinctrl. Top-level required properties: compatible. Important top-level properties found in the schema: None declared in this schema. Child-node patterns: None declared in this schema. Referenced schemas: pincfg-node.yaml#, pinmux-node.yaml#, pinctrl.yaml#.

## Control Flow
Validation selects one UniPhier compatible and uses standard pinctrl, pinmux, and pinconf schema composition for child state nodes. The binding is intentionally compact, leaving SoC-specific pin/function tables to the driver and DTS conventions.

## State and Persistence Behavior
Persistent ABI is the compatible string and child state format. There is no stateful data in the schema beyond accepted DTS property names and values.

## Dependencies and Integration Points
This schema is consumed by Linux devicetree validation tooling (`dt-schema`), board DTS files under architecture trees, and the matching kernel pinctrl/GPIO/interrupt driver. Integration points include `pinctrl.yaml`, generic `pinmux-node.yaml`/`pincfg-node.yaml`, vendor common schemas, dt-bindings headers, GPIO and interrupt-controller bindings, and SoC clock/reset/power-domain providers where referenced.

## Risks and Edge Cases
The broad compatible enum must stay aligned with driver support. Overly permissive child properties could hide invalid board states until runtime.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/pinctrl/socionext,uniphier-pinctrl.yaml` and at least one `make dtbs_check` target containing a DTS user of the compatible. For shared helper schemas, run the top-level importing bindings as well. Review the in-file example because it exercises required properties, child-node shape, and referenced dt-bindings constants.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/socionext,uniphier-pinctrl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/sophgo,cv1800-pinctrl.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/sophgo,cv1800-pinctrl.yaml

## Purpose
This schema describes a Sophgo pin controller using standard pinmux and pinconf state nodes with SoC-specific compatible strings and enumerated mux/electrical properties. Source title: Sophgo CV1800 Pin Controller. Description signal from the file: No long-form description is present; the binding contract is carried by the schema properties and examples.

## Important APIs, Types, and Schema Surface
- Lines read: 122.
- Compatible contract: sophgo,cv1800b-pinctrl, sophgo,cv1812h-pinctrl, sophgo,sg2000-pinctrl, sophgo,sg2002-pinctrl. Top-level required properties: compatible, reg, reg-names. Important top-level properties found in the schema: reg, resets. Child-node patterns: -cfg$, -pins$. Referenced schemas: pincfg-node.yaml#, pinmux-node.yaml#.

## Control Flow
Validation selects a Sophgo compatible and accepts child pinctrl groups with standard `pinmux` and pin configuration properties. The child nodes encode mux choice, bias, drive, input, output, and slew-related settings according to the schema enums.

## State and Persistence Behavior
Persistent ABI is the compatible and pin group property vocabulary used by board DTS files. Runtime state is applied by the pinctrl driver when clients select a pinctrl state.

## Dependencies and Integration Points
This schema is consumed by Linux devicetree validation tooling (`dt-schema`), board DTS files under architecture trees, and the matching kernel pinctrl/GPIO/interrupt driver. Integration points include `pinctrl.yaml`, generic `pinmux-node.yaml`/`pincfg-node.yaml`, vendor common schemas, dt-bindings headers, GPIO and interrupt-controller bindings, and SoC clock/reset/power-domain providers where referenced.

## Risks and Edge Cases
Risk comes from mismatched mux/electrical enum values and from allowing child state properties not implemented by the Sophgo driver. Tests should cover each listed compatible.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/pinctrl/sophgo,cv1800-pinctrl.yaml` and at least one `make dtbs_check` target containing a DTS user of the compatible. For shared helper schemas, run the top-level importing bindings as well. Review the in-file example because it exercises required properties, child-node shape, and referenced dt-bindings constants.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/sophgo,cv1800-pinctrl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/sophgo,sg2042-pinctrl.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/sophgo,sg2042-pinctrl.yaml

## Purpose
This schema describes a Sophgo pin controller using standard pinmux and pinconf state nodes with SoC-specific compatible strings and enumerated mux/electrical properties. Source title: Sophgo SG2042 Pin Controller. Description signal from the file: No long-form description is present; the binding contract is carried by the schema properties and examples.

## Important APIs, Types, and Schema Surface
- Lines read: 129.
- Compatible contract: sophgo,sg2042-pinctrl, sophgo,sg2044-pinctrl. Top-level required properties: compatible, reg. Important top-level properties found in the schema: reg. Child-node patterns: -cfg$, -pins$. Referenced schemas: pincfg-node.yaml#, pinmux-node.yaml#.

## Control Flow
Validation selects a Sophgo compatible and accepts child pinctrl groups with standard `pinmux` and pin configuration properties. The child nodes encode mux choice, bias, drive, input, output, and slew-related settings according to the schema enums.

## State and Persistence Behavior
Persistent ABI is the compatible and pin group property vocabulary used by board DTS files. Runtime state is applied by the pinctrl driver when clients select a pinctrl state.

## Dependencies and Integration Points
This schema is consumed by Linux devicetree validation tooling (`dt-schema`), board DTS files under architecture trees, and the matching kernel pinctrl/GPIO/interrupt driver. Integration points include `pinctrl.yaml`, generic `pinmux-node.yaml`/`pincfg-node.yaml`, vendor common schemas, dt-bindings headers, GPIO and interrupt-controller bindings, and SoC clock/reset/power-domain providers where referenced.

## Risks and Edge Cases
Risk comes from mismatched mux/electrical enum values and from allowing child state properties not implemented by the Sophgo driver. Tests should cover each listed compatible.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/pinctrl/sophgo,sg2042-pinctrl.yaml` and at least one `make dtbs_check` target containing a DTS user of the compatible. For shared helper schemas, run the top-level importing bindings as well. Review the in-file example because it exercises required properties, child-node shape, and referenced dt-bindings constants.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/sophgo,sg2042-pinctrl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/spacemit,k1-pinctrl.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/spacemit,k1-pinctrl.yaml

## Purpose
This schema describes the SpacemiT K1/K3 pin controller, including protected register access through syscon-style integration and standard pinmux/pinconf child nodes. Source title: SpacemiT K1 SoC Pin Controller. Description signal from the file: No long-form description is present; the binding contract is carried by the schema properties and examples.

## Important APIs, Types, and Schema Surface
- Lines read: 159.
- Compatible contract: spacemit,k1-pinctrl, spacemit,k3-pinctrl. Top-level required properties: compatible, reg, clocks, clock-names. Important top-level properties found in the schema: reg, clocks, clock-names, resets, spacemit,apbc. Child-node patterns: -cfg$, -pins$. Referenced schemas: /schemas/types.yaml#/definitions/phandle, pincfg-node.yaml#, pinmux-node.yaml#, /schemas/types.yaml#/definitions/uint32.

## Control Flow
Validation selects K1/K3 compatibles, validates syscon/protected-register integration, and accepts child groups that combine standard pinmux/pinconf with SpacemiT-specific power, drive, and register access properties.

## State and Persistence Behavior
Persistent ABI includes syscon phandles and pin state values. The schema itself is stateless, but it guards access to protected register configuration expected by the driver.

## Dependencies and Integration Points
This schema is consumed by Linux devicetree validation tooling (`dt-schema`), board DTS files under architecture trees, and the matching kernel pinctrl/GPIO/interrupt driver. Integration points include `pinctrl.yaml`, generic `pinmux-node.yaml`/`pincfg-node.yaml`, vendor common schemas, dt-bindings headers, GPIO and interrupt-controller bindings, and SoC clock/reset/power-domain providers where referenced.

## Risks and Edge Cases
Incorrect syscon references or electrical values can lead to invalid protected-register writes. Keep phandle typing and vendor property ranges aligned with the driver.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/pinctrl/spacemit,k1-pinctrl.yaml` and at least one `make dtbs_check` target containing a DTS user of the compatible. For shared helper schemas, run the top-level importing bindings as well. Review the in-file example because it exercises required properties, child-node shape, and referenced dt-bindings constants.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/spacemit,k1-pinctrl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/sprd,sc9860-pinctrl.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/sprd,sc9860-pinctrl.yaml

## Purpose
This schema describes the Spreadtrum SC9860 pin controller, organized around typed register blocks and pin nodes with both standard and Spreadtrum-specific sleep/global-control fields. Source title: Spreadtrum SC9860 Pin Controller. Description signal from the file: The Spreadtrum pin controller are organized in 3 blocks (types). The first block comprises some global control registers, and each register contains several bit fields with one bit or several bits to configure for some global common configuration, such as domain pad driving level, system control select and so on ("domain pad driving level": One pin can output 3.0v or 1.8v, depending on the related domain pad driving selection, if the related doma

## Important APIs, Types, and Schema Surface
- Lines read: 199.
- Compatible contract: sprd,sc9860-pinctrl. Top-level required properties: compatible, reg. Important top-level properties found in the schema: reg. Child-node patterns: sleep$. Function enum sample: func1, func2, func3, func4. Referenced schemas: #/$defs/pin-node, /schemas/types.yaml#/definitions/uint32, /schemas/pinctrl/pincfg-node.yaml#, /schemas/pinctrl/pinmux-node.yaml#, /schemas/types.yaml#/definitions/string-array.

## Control Flow
Validation requires compatible and register resources, then dispatches child pin nodes through `$defs/pin-node`. The pin node composes standard pinconf/pinmux with Spreadtrum-specific sleep mode, global-control, and register block fields.

## State and Persistence Behavior
Persistent ABI is the register block layout and pin-node vocabulary used by SC9860 DTS files. Sleep-related properties describe static low-power state selection rather than mutable YAML persistence.

## Dependencies and Integration Points
This schema is consumed by Linux devicetree validation tooling (`dt-schema`), board DTS files under architecture trees, and the matching kernel pinctrl/GPIO/interrupt driver. Integration points include `pinctrl.yaml`, generic `pinmux-node.yaml`/`pincfg-node.yaml`, vendor common schemas, dt-bindings headers, GPIO and interrupt-controller bindings, and SoC clock/reset/power-domain providers where referenced.

## Risks and Edge Cases
The risky area is sleep/global control encoding. Values are tied to databook meanings, so schema broadening can validate DTS settings that produce incorrect low-power behavior.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/pinctrl/sprd,sc9860-pinctrl.yaml` and at least one `make dtbs_check` target containing a DTS user of the compatible. For shared helper schemas, run the top-level importing bindings as well. Review the in-file example because it exercises required properties, child-node shape, and referenced dt-bindings constants.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/sprd,sc9860-pinctrl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/st,stm32-hdp.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/st,stm32-hdp.yaml

## Purpose
This schema describes the STM32 Hardware Debug Port mux/config block. It exposes internal debug signals onto GPIO-capable pins through pinmux-style state nodes rather than acting as a full GPIO controller. Source title: STM32 Hardware Debug Port Mux/Config. Description signal from the file: STMicroelectronics's STM32 MPUs integrate a Hardware Debug Port (HDP). It allows to output internal signals on SoC's GPIO.

## Important APIs, Types, and Schema Surface
- Lines read: 193.
- Compatible contract: st,stm32mp131-hdp, st,stm32mp151-hdp, st,stm32mp251-hdp. Top-level required properties: compatible, reg, clocks. Important top-level properties found in the schema: reg, clocks. Child-node patterns: ^hdp[0-7]-pins$. Function enum sample: pwr_pwrwake_sys, pwr_stop_forbidden, pwr_stdby_wakeup, pwr_encomp_vddcore, bsec_out_sec_niden, aiec_sys_wakeup, none, ddrctrl_lp_req, pwr_ddr_ret_enable_n, dts_clk_ptat, sram3ctrl_tamp_erase_act, gpoval0, pwr_sel_vth_vddcpu, pwr_mpu_ram_lowspeed, ca7_naxierrirq, pwr_okin_mr plus 231 more. Referenced schemas: pinmux-node.yaml#, pinctrl.yaml#.

## Control Flow
Validation selects the STM32MP HDP compatible, then validates pinmux state children that map internal debug signals to output-capable pins. It references generic pinmux and pinctrl schemas but does not expose generic GPIO provider behavior.

## State and Persistence Behavior
Persistent ABI is the HDP compatible and signal-to-pin mux state representation. Runtime state is the selected debug signal route applied by the platform driver from the static devicetree.

## Dependencies and Integration Points
This schema is consumed by Linux devicetree validation tooling (`dt-schema`), board DTS files under architecture trees, and the matching kernel pinctrl/GPIO/interrupt driver. Integration points include `pinctrl.yaml`, generic `pinmux-node.yaml`/`pincfg-node.yaml`, vendor common schemas, dt-bindings headers, GPIO and interrupt-controller bindings, and SoC clock/reset/power-domain providers where referenced.

## Risks and Edge Cases
Risk is mostly enum drift between signal IDs and supported SoC variants. Tests should validate each compatible example and reject ordinary GPIO-controller properties.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/pinctrl/st,stm32-hdp.yaml` and at least one `make dtbs_check` target containing a DTS user of the compatible. For shared helper schemas, run the top-level importing bindings as well. Review the in-file example because it exercises required properties, child-node shape, and referenced dt-bindings constants.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/st,stm32-hdp.yaml -->
