## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,qcs404-pinctrl.yaml

### Purpose
`qcom,qcs404-pinctrl.yaml` describes the Qualcomm QCS404 Top Level Mode Multiplexer controller. It binds the SoC-specific TLMM register block, GPIO and interrupt provider resources, and the legal pin/function names for pinctrl state nodes.

### Important Schema APIs
The binding provides compatible `qcom,qcs404-pinctrl`. Top-level required properties are `compatible`, `reg`. State nodes matching `-state$` can be direct objects or containers of `-pins` objects, and their `$defs` entry references `qcom,tlmm-common.yaml#/$defs/qcom-tlmm-state`. pin names constrained by `^gpio([0-9]|[1-9][0-9]|1[0-1][0-9])$`. `function` is restricted to 183 local mux choices, starting with `gpio`, `adsp_ext`, `atest_char`, `atest_char0`, `atest_char1`, `atest_char2`, `atest_char3`, `aud_cdc`. The local schema setting is `unevaluatedProperties: false`. It also bounds `gpio-line-names` to the SoC GPIO count. `gpio-reserved-ranges` is available for pins owned by firmware or trusted applications.

### Validation Flow
Validation composes the common Qualcomm TLMM provider schema with this SoC-specific file. The common schema requires GPIO and interrupt provider properties, while this file restricts `compatible`, `reg`, interrupt count, optional line-name and reserved-range bounds, and local pin/function enums. The `oneOf` state-node pattern supports both flat state nodes and grouped child pin nodes.

### State And Persistence
The YAML has no mutable state. DTS data persists the physical TLMM register resource, interrupt summary line, GPIO range, reserved GPIO ranges, and pinctrl states. At runtime the Qualcomm TLMM driver maps state labels into mux selection, drive strength, bias, input/output, and GPIO/IRQ domain behavior.

### Dependencies And Integration Points
Dependencies include `qcom,tlmm-common.yaml`, `pinctrl.yaml`, `pinmux-node.yaml`, `pincfg-node.yaml`, `/schemas/types.yaml`, and interrupt-controller dt-bindings used in examples. Integration points are SoC DTSI files, board DTS pin states, Linux pinctrl and GPIO consumers, and wakeup-parent IRQ controllers when declared.

### Risks
The biggest risk is drift between the schema pin/function enum and the driver pin/function tables; a missing enum blocks valid DTS, while an extra enum can allow states the driver cannot program. Pin count limits in regexes and `gpio-line-names` must match hardware. The broad grouped-state pattern can hide semantic mistakes unless examples cover both flat and nested layouts.

### Test Signals
Run `dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/pinctrl/qcom,qcs404-pinctrl.yaml` and compile representative SoC DTSI users. Negative tests should cover invalid GPIO numbers, unsupported functions, missing `reg`, missing GPIO/IRQ provider cells, and illegal extra properties. Runtime signals are TLMM probe, GPIO chip registration, IRQ domain creation, and successful pin state switching for UART, SPI/I2C, storage, and audio/display functions listed in the enum.
