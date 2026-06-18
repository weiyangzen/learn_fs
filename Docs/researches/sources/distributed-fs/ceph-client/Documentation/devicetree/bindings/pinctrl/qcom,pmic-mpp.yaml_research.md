## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,pmic-mpp.yaml

### Purpose
`qcom,pmic-mpp.yaml` describes Qualcomm PMIC multi-purpose pin blocks. MPPs can operate as digital, analog, or current-sink style pins, so the schema combines GPIO-provider validation with PMIC-specific pin state properties for analog routing and paired mode.

### Important Schema APIs
The binding accepts PMIC-specific compatibles such as `qcom,pm8019-mpp`, `qcom,pm8226-mpp`, `qcom,pm8841-mpp`, `qcom,pm8916-mpp`, and related SPMI or SSBI MPP variants followed by `qcom,spmi-mpp` or `qcom,ssbi-mpp`. Required top-level properties are `compatible`, `reg`, `gpio-controller`, `'#gpio-cells'`, `gpio-ranges`, `interrupt-controller`. State nodes under `*-state` or nested `*-pins` use `$defs/qcom-pmic-mpp-state`, which composes `pinmux-node.yaml` and `pincfg-node.yaml`, requires `pins` and `function`, accepts `mppN` pin names, and restricts `function` to `digital`, `analog`, or `sink`. PMIC-specific properties include `qcom,analog-level`, `qcom,atest`, `qcom,dtest`, `qcom,amux-route`, and boolean `qcom,paired`.

### Validation Flow
The compatible schema chooses either SPMI-backed or SSBI-backed MPP compatibles and requires the common fallback. Top-level `additionalProperties: false` rejects unknown controller properties. Pattern properties validate each state node directly or through nested `*-pins` objects, and state nodes close unknown properties after the generic pinmux/pinconf helpers and PMIC-specific enums are applied.

### State And Persistence
There is no runtime state in the YAML. DTS data persists MPP line names, GPIO range mapping, interrupt-controller identity, analog mux routes, DTEST/ATEST selections, and power-source choices. The PMIC MPP driver maps these values onto PMIC peripheral registers.

### Dependencies And Integration Points
It depends on generic pinmux/pinconf schemas and Qualcomm PMIC MPP dt-bindings constants used in examples. It integrates with PMIC parent buses, Linux GPIO and IRQ domains, pinctrl client states, and board circuits that consume MPP analog or current-sink functions.

### Risks
The schema documents only selected valid pin ranges in prose and accepts a broad `^mpp([0-9]+)$` pattern, so out-of-range MPP numbers may pass schema. Analog constants must stay synchronized with `qcom,pmic-mpp.h` and driver tables. Incorrect fallback compatible can bind the wrong bus-specific register access path.

### Test Signals
Use dt-schema examples for both SPMI and SSBI compatibles, invalid function names, invalid analog and DTEST enum values, missing `gpio-ranges`, and nested `*-pins` layouts. Runtime validation should confirm GPIO line count, IRQ delivery, analog route programming, and paired mode behavior.
