## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,sdm670-lpass-lpi-pinctrl.yaml

### Purpose
`qcom,sdm670-lpass-lpi-pinctrl.yaml` describes the Qualcomm SDM670 LPASS LPI TLMM pin controller. It specializes the common LPASS LPI schema with this SoC's compatible string, register layout, GPIO pin range, and audio-oriented mux function list.

### Important Schema APIs
The binding provides compatible `qcom,sdm670-lpass-lpi-pinctrl`. Top-level required properties are `compatible`, `reg`. State nodes matching `-state$` can either be direct state objects or containers of `-pins` objects. They reference `qcom,lpass-lpi-common.yaml#/$defs/qcom-tlmm-state`, so each state requires `pins` and `function` and may set LPASS drive strength, slew rate, bias, input, and output properties. pin names constrained by `^gpio([0-9]|1[0-9]|2[0-9]|3[0-1])$`. `function` is restricted to 15 local mux choices, starting with `gpio`, `comp_rx`, `dmic1_clk`, `dmic1_data`, `dmic2_clk`, `dmic2_data`, `i2s1_clk`, `i2s_data`.

### Validation Flow
Dt-schema validates the concrete compatible and registers first, applies the state-node pattern, then composes the common LPASS schema through `allOf`. `unevaluatedProperties: false` makes the concrete file responsible for closing properties after common GPIO-provider requirements and local pin/function enums are evaluated.

### State And Persistence
The YAML is not executable. DTS data persists LPASS register resources, GPIO range mapping, optional clock votes, and pin states for audio buses such as SoundWire, I2S, DMIC, Slimbus, and external master clocks. The LPASS LPI pinctrl driver applies this state during device probe and pinctrl state selection.

### Dependencies And Integration Points
Dependencies are `qcom,lpass-lpi-common.yaml`, `pinctrl.yaml`, generic pinmux/pinconf helpers, and any clock or sound dt-binding headers used by examples. Integration points include Linux pinctrl, GPIO, LPASS audio clock providers, and audio client drivers referencing the state labels.

### Risks
Pin regexes and function enums must match the driver pin tables exactly. Missing clocks or wrong clock names can leave the controller inaccessible even when schema passes for bindings without explicit clocks. Reserved ranges and GPIO counts must stay aligned with firmware and LPASS ownership.

### Test Signals
Run `dt_binding_check` for this file and negative cases for invalid GPIO names, unsupported audio functions, missing required clocks, and extra state properties. Runtime tests should switch active and sleep states for at least one audio interface and verify GPIO range registration.
