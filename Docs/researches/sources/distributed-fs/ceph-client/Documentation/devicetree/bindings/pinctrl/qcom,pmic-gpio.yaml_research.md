## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,pmic-gpio.yaml

### Purpose
`qcom,pmic-gpio.yaml` describes Qualcomm PMIC GPIO controller blocks exposed over SPMI or SSBI. It covers a large family of PMIC-specific compatible strings, validates GPIO provider and interrupt-controller properties, and defines PMIC GPIO pin state nodes.

### Important Schema APIs
The binding accepts many PMIC-specific compatibles including `qcom,pm2250-gpio`, `qcom,pm660-gpio`, `qcom,pm660l-gpio`, `qcom,pm6125-gpio`, and newer PMIC families, followed by either `qcom,spmi-gpio` or `qcom,ssbi-gpio`. Top-level required properties are `compatible`, `reg`, `gpio-controller`, `'#gpio-cells'`, `gpio-ranges`, `interrupt-controller`. It constrains `reg`, `#gpio-cells`, `#interrupt-cells`, `gpio-ranges`, optional `gpio-line-names`, and `gpio-reserved-ranges`. Its `qcom-pmic-gpio-state` composes generic pinmux and pinconf helpers, requires `pins` and `function`, accepts `gpioN` pin names, and restricts functions to normal, paired, func1 through func4, and DTEST modes. It also defines Qualcomm-specific properties such as `qcom,pull-up-strength`, `qcom,drive-strength`, `qcom,analog-pass`, `qcom,atest`, and `qcom,dtest-buffer`.

### Validation Flow
Validation first checks the two-element compatible tuple ending in either `qcom,spmi-gpio` or `qcom,ssbi-gpio`. A long `allOf` chain then selects PMIC-specific `gpio-line-names` and `gpio-reserved-ranges` bounds from the first compatible, ranging from two GPIOs to forty-four. Pattern properties admit `*-state` nodes and `*-hog` GPIO hog nodes, while `additionalProperties: false` closes both top-level and state-node schemas.

### State And Persistence
The YAML is static, but DTS data persists PMIC GPIO counts, reserved ranges, interrupt-domain identity, GPIO hog defaults, and electrical/analog routing choices. The Linux PMIC GPIO driver converts these state nodes into SPMI or SSBI register programming and GPIO chip registration.

### Dependencies And Integration Points
It depends on generic `pinmux-node.yaml`, `pincfg-node.yaml`, `/schemas/types.yaml`, and GPIO/IRQ dt-bindings included by examples. It integrates with Qualcomm PMIC MFD nodes, the Linux GPIO and IRQ subsystems, pinctrl client states, and board-specific GPIO hogs.

### Risks
The compatible-specific GPIO count matrix is the main maintenance risk: adding a PMIC without updating both `gpio-line-names` and reserved-range bounds lets DTS files under- or over-describe pins. The `pins` regex accepts numeric names broadly, so not every out-of-range GPIO is caught by schema. Analog pass-through, ATEST, DTEST, and drive-strength enums must match the dt-bindings header and driver register definitions.

### Test Signals
Run `dt_binding_check` for many compatible branches, especially the smallest two-GPIO PMICs and forty-four-GPIO PMICs. Add negative tests for wrong fallback bus compatible, excessive `gpio-line-names`, missing `function`, invalid `qcom,atest`, and GPIO hog nodes. Runtime signals are GPIO chip line count, IRQ handling, hog application, and pinconf readback where supported.
