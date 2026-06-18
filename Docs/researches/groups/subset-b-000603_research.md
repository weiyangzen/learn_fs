# subset-b-000603 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/nxp,s32g2-siul2-pinctrl.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/nxp,s32g2-siul2-pinctrl.yaml

### Purpose
`nxp,s32g2-siul2-pinctrl.yaml` describes the NXP S32G2 SIUL2 pin controller, whose mux registers are split across SIUL2_0 and SIUL2_1 MSCR and IMCR windows. It documents the six required register regions and the nested pin group layout used to program S32G2 pin mux and electrical state.

### Important Schema APIs
The controller requires `compatible`, `reg` and accepts compatible `nxp,s32g2-siul2-pinctrl`. Child nodes ending in `-pins` contain group nodes ending in `-grp[0-9]`. Each group composes `pinmux-node.yaml` and `pincfg-node.yaml`, then locally allows `pinmux`, bias flags, high impedance, open drain, input/output enablement, and `slew-rate` values of 83, 133, 150, 166, or 208 MHz. The packed `pinmux` value is `(PIN_ID << 4) | SSS`.

### Validation Flow
Top-level validation confirms the compatible string and exactly described MSCR/IMCR register regions, then pattern validation walks from `*-pins` containers to `*-grpN` configuration groups. Group schemas close unknown properties, so unsupported pinconf keys should fail. The example covers LLCE CAN input and output groups with separate SSS values.

### State And Persistence
No state is held by the YAML file. Persistent DTS data records hardware register windows and packed pinmux values that the Linux S32G2 SIUL2 pinctrl driver decodes into MSCR and IMCR writes. Reserved register index ranges noted in the description remain a driver and DTS correctness concern.

### Dependencies And Integration Points
The binding depends on the generic pinmux and pinconf helpers. It integrates with S32G2 board DTS files, the platform device created from `pinctrl@...`, and client devices that reference the `*-pins` state labels through standard `pinctrl-0` style properties.

### Risks
The schema cannot fully verify that a packed pin ID avoids reserved MSCR/IMCR indexes or that the selected 4-bit SSS is valid for a specific pad. Incorrect register-region ordering would direct the driver to the wrong SIUL2 window. Closed group properties reduce typo risk but require binding updates when the driver gains new pinconf features.

### Test Signals
Use `dt_binding_check` on the example, negative tests for misspelled group names and unsupported slew rates, and board boot tests that exercise CAN, GPIO, and input mux paths across both SIUL2 regions.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/nxp,s32g2-siul2-pinctrl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/pincfg-node.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/pincfg-node.yaml

### Purpose
`pincfg-node.yaml` is the generic pin configuration state-node helper. It documents and validates common pinconf properties such as bias, drive mode, drive strength, input/output enablement, debounce, power source, low-power mode, skew, and sleep hardware state.

### Important Schema APIs
The schema exposes boolean-style configuration properties (`bias-disable`, `bias-pull-up`, `drive-open-drain`, `input-enable`, `output-high`, and related flags), numeric properties including `drive-strength`, `drive-strength-microamp`, `input-debounce`, `power-source`, `slew-rate`, skew delays, and array-valued low-power mode data. It also has conditional rules that require numeric companions when boolean-or-integer style properties are supplied with arguments.

### Validation Flow
Dt-schema evaluates a broad property map and then the `allOf` conditionals. The `if`/`then` blocks enforce that forms such as `bias-pull-up`, `bias-pull-down`, `input-debounce`, `drive-strength`, and skew settings use either flag-only or explicitly valued forms accepted by the Linux pinconf parser. `additionalProperties: true` lets concrete pin controller bindings add hardware-specific restrictions and close the schema later.

### State And Persistence
The file has no executable state. The persistent contract is a normalized vocabulary that Linux pinctrl drivers map onto generic pin configuration parameters. Values such as drive strength, pull strength, and debounce time become board description data and may directly affect electrical behavior.

### Dependencies And Integration Points
It depends on `/schemas/types.yaml` and is referenced by the generic mux helper consumers throughout this batch. Qualcomm TLMM and LPASS LPI schemas further restrict supported options; PMIC GPIO and MPP schemas add Qualcomm-specific analog, DTEST, drive, and pull-strength properties.

### Risks
Because the helper is permissive, unsupported properties can pass unless a concrete binding sets them to `false` or closes unevaluated properties. Electrical units are easy to confuse, especially mA versus microamp and skew-delay units. Flag-or-value alternatives also need examples to avoid DTS authors choosing forms not handled by a driver.

### Test Signals
High-value checks are `dt_binding_check` with examples for every conditional form, negative schemas for unsupported output/input flags in concrete bindings, and runtime board tests verifying pull, drive, debounce, and sleep-state programming on representative controllers.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/pincfg-node.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/pinctrl-single.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/pinctrl-single.yaml

### Purpose
`pinctrl-single.yaml` describes generic pin controllers where one register controls one or more pins, including `pinctrl-single` and several TI padconf variants. It provides the binding for register-width, mask, function-mask, optional interrupt controller behavior, and child state nodes that program packed register values.

### Important Schema APIs
The controller accepts `pinctrl-single` plus TI padconf compatibles such as `ti,am437-padconf`, `ti,am62l-padconf`, `ti,am654-padconf`, `ti,dra7-padconf`, and OMAP padconf variants. Important properties include `reg`, `#pinctrl-cells`, `pinctrl-single,register-width`, `pinctrl-single,function-mask`, `pinctrl-single,bit-per-mux`, `pinctrl-single,drive-strength`, optional interrupt properties, and child nodes carrying `pinctrl-single,pins`, `pinctrl-single,bits`, `pinctrl-single,bias-pullup`, `pinctrl-single,bias-pulldown`, drive-strength arrays, slew-rate arrays, power-source arrays, low-power-mode arrays, and wakeup-enable arrays.

### Validation Flow
The top-level schema applies `pinctrl.yaml`, validates the compatible choice, register sizing, and provider cell count, then evaluates child nodes under `patternProperties`. Child node validation closes unknown keys with `additionalProperties: false`, so misspelled `pinctrl-single,*` properties should fail early. The schema uses typed arrays to validate the register offset/value/mask tuples consumed by the generic pinctrl-single driver.

### State And Persistence
The schema itself is static. DTS data persists register offsets and values that the Linux `pinctrl-single` driver writes into controller registers for each selected state. Optional interrupt-controller properties persist GPIO/pin interrupt mapping for controllers that multiplex interrupt status into the same register block.

### Dependencies And Integration Points
It depends on `pinctrl.yaml`, `pinmux-node.yaml`, `pincfg-node.yaml`, and `/schemas/types.yaml`. Integration is with the generic Linux pinctrl-single driver and TI SoC pad configuration bindings that use the same register programming model.

### Risks
Packed offset/value arrays are hard for schema to validate semantically: a tuple can be well typed but target a reserved register or set illegal bits. `#pinctrl-cells` and function mask mismatches can break client references. Interrupt-related properties must stay consistent with the hardware and the generic IRQ domain setup.

### Test Signals
Run `dt_binding_check` for this file and compile DTS examples using both `pinctrl-single,pins` and `pinctrl-single,bits`. Runtime signals are successful state selection through the pinctrl core, correct register writes, and interrupt mapping tests on controllers advertising interrupt support.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/pinctrl-single.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/pinctrl.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/pinctrl.yaml

### Purpose
`pinctrl.yaml` is the generic pin controller device schema. It documents the Linux devicetree convention that controller nodes contain or own pin configuration state nodes referenced by client devices through `pinctrl-*` properties. It intentionally stays permissive because hardware-specific bindings define the contents and nesting of those state nodes.

### Important Schema APIs
The schema exposes the controller node name pattern `^(pinctrl|pinmux)(@[0-9a-f]+)?$`, the optional `#pinctrl-cells` provider shape, and the boolean `pinctrl-use-default` escape hatch for bootloader-provided pin states. It is maintained by Linus Walleij <linusw@kernel.org>, Rafał Miłecki <rafal@milecki.pl>. It does not declare child-state properties; those come from helper schemas such as `pinmux-node.yaml` and `pincfg-node.yaml` or from concrete SoC bindings.

### Validation Flow
Dt-schema first applies the core YAML meta-schema, then this file checks only the generic controller-level properties. `additionalProperties: true` is deliberate control flow: validation must continue in concrete bindings without this helper rejecting vendor registers, interrupts, clocks, GPIO provider properties, or vendor child node layouts.

### State And Persistence
There is no runtime state in this file. The persistent artifact is the binding contract consumed by `dt_binding_check` and by DTS authors. At runtime, Linux pinctrl drivers consume the resulting devicetree nodes and may either program hardware or honor `pinctrl-use-default` when the OS lacks a driver.

### Dependencies And Integration Points
The file integrates with every pinctrl provider binding that references `/schemas/pinctrl/pinctrl.yaml#`, including the Qualcomm TLMM and LPASS LPI schemas in this work item. It also anchors provider-style bindings that use `#pinctrl-cells` for hardware-indexed pin arrays.

### Risks
The permissive `additionalProperties` setting means this file cannot catch misspelled vendor properties by itself. That is acceptable only when concrete bindings close the schema with `unevaluatedProperties: false` or equivalent. Overusing `pinctrl-use-default` can hide missing driver support or board-specific mux requirements.

### Test Signals
Useful tests are `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/pinctrl/pinctrl.yaml`, sample nodes named `pinctrl@...` and `pinmux@...`, and downstream concrete bindings that prove this helper composes without rejecting vendor-specific controller properties.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/pinctrl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/pinmux-node.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/pinmux-node.yaml

### Purpose
`pinmux-node.yaml` is the generic pin multiplexing state-node helper. It standardizes the reusable vocabulary for selecting mux functions on named pins, named groups, packed numeric `pinmux` values, or hardware-indexed `pinctrl-pin-array` entries.

### Important Schema APIs
The schema defines `function` as a string, `pins` as either a string-array or uint32-array, `groups` as a string-array, `pinmux` as a uint32-array, and `pinctrl-pin-array` as a uint32-array. Hardware-specific schemas decide the legal pin IDs, group names, packed bit layout, and function enum.

### Validation Flow
The validation path is intentionally shallow: core dt-schema checks this helper, then concrete bindings add enum and pattern restrictions through `allOf` or `$defs`. The descriptive text explains three accepted mux forms and why `pinctrl-pin-array` uses hardware register indexes instead of virtual pin indexes. `additionalProperties: true` leaves pin configuration properties and vendor extensions available to companion schemas.

### State And Persistence
This file stores no runtime state. It persists a schema vocabulary used by DTS files and by drivers that parse state nodes into Linux pinctrl maps. Numeric `pinmux` and `pinctrl-pin-array` values persist hardware-specific encodings that drivers must decode consistently.

### Dependencies And Integration Points
It depends on `/schemas/types.yaml` for string and integer array typing. The Qualcomm TLMM, Qualcomm PMIC, LPASS LPI, NXP SIUL2, and generic `pinctrl-single` bindings in this batch all compose with this helper for their state nodes.

### Risks
The helper cannot enforce that one of `pins`, `groups`, or `pinmux` is present; concrete bindings must add required clauses where their drivers need them. Packed integer mux formats are opaque to dt-schema, so mistakes in macro definitions or bit assignments require binding examples and driver tests to catch.

### Test Signals
Run dt-schema checks against this helper and at least one concrete binding for each mux form: string pins with function, group-based functions, packed `pinmux`, and `pinctrl-pin-array`. DTS examples should include invalid types to prove the string-array and uint32-array constraints fire.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/pinmux-node.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,apq8064-pinctrl.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,apq8064-pinctrl.yaml

### Purpose
`qcom,apq8064-pinctrl.yaml` describes the Qualcomm APQ8064 Top Level Mode Multiplexer controller. It binds the SoC-specific TLMM register block, GPIO and interrupt provider resources, and the legal pin/function names for pinctrl state nodes.

### Important Schema APIs
The binding provides compatible `qcom,apq8064-pinctrl`. Top-level required properties are `compatible`, `reg`. State nodes matching `-state$` can be direct objects or containers of `-pins` objects, and their `$defs` entry references `qcom,tlmm-common.yaml#/$defs/qcom-tlmm-state`. pin names constrained by `^gpio([0-9]|[1-8][0-9])$`. `function` is restricted to 41 local mux choices, starting with `cam_mclk`, `codec_mic_i2s`, `codec_spkr_i2s`, `gp_clk_0a`, `gp_clk_0b`, `gp_clk_1a`, `gp_clk_1b`, `gp_clk_2a`. The local schema setting is `unevaluatedProperties: false`. `gpio-reserved-ranges` is available for pins owned by firmware or trusted applications.

### Validation Flow
Validation composes the common Qualcomm TLMM provider schema with this SoC-specific file. The common schema requires GPIO and interrupt provider properties, while this file restricts `compatible`, `reg`, interrupt count, optional line-name and reserved-range bounds, and local pin/function enums. The `oneOf` state-node pattern supports both flat state nodes and grouped child pin nodes.

### State And Persistence
The YAML has no mutable state. DTS data persists the physical TLMM register resource, interrupt summary line, GPIO range, reserved GPIO ranges, and pinctrl states. At runtime the Qualcomm TLMM driver maps state labels into mux selection, drive strength, bias, input/output, and GPIO/IRQ domain behavior.

### Dependencies And Integration Points
Dependencies include `qcom,tlmm-common.yaml`, `pinctrl.yaml`, `pinmux-node.yaml`, `pincfg-node.yaml`, `/schemas/types.yaml`, and interrupt-controller dt-bindings used in examples. Integration points are SoC DTSI files, board DTS pin states, Linux pinctrl and GPIO consumers, and wakeup-parent IRQ controllers when declared.

### Risks
The biggest risk is drift between the schema pin/function enum and the driver pin/function tables; a missing enum blocks valid DTS, while an extra enum can allow states the driver cannot program. Pin count limits in regexes and `gpio-line-names` must match hardware. The broad grouped-state pattern can hide semantic mistakes unless examples cover both flat and nested layouts.

### Test Signals
Run `dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/pinctrl/qcom,apq8064-pinctrl.yaml` and compile representative SoC DTSI users. Negative tests should cover invalid GPIO numbers, unsupported functions, missing `reg`, missing GPIO/IRQ provider cells, and illegal extra properties. Runtime signals are TLMM probe, GPIO chip registration, IRQ domain creation, and successful pin state switching for UART, SPI/I2C, storage, and audio/display functions listed in the enum.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,apq8064-pinctrl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,apq8084-pinctrl.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,apq8084-pinctrl.yaml

### Purpose
`qcom,apq8084-pinctrl.yaml` describes the Qualcomm APQ8084 Top Level Mode Multiplexer controller. It binds the SoC-specific TLMM register block, GPIO and interrupt provider resources, and the legal pin/function names for pinctrl state nodes.

### Important Schema APIs
The binding provides compatible `qcom,apq8084-pinctrl`. Top-level required properties are `compatible`, `reg`. State nodes matching `-state$` can be direct objects or containers of `-pins` objects, and their `$defs` entry references `qcom,tlmm-common.yaml#/$defs/qcom-tlmm-state`. pin names constrained by `^gpio([0-9]|[1-9][0-9]|1[0-3][0-9]|14[0-6])$`. `function` is restricted to 121 local mux choices, starting with `adsp_ext`, `audio_ref`, `blsp_i2c1`, `blsp_i2c2`, `blsp_i2c3`, `blsp_i2c4`, `blsp_i2c5`, `blsp_i2c6`. The local schema setting is `unevaluatedProperties: false`. `gpio-reserved-ranges` is available for pins owned by firmware or trusted applications.

### Validation Flow
Validation composes the common Qualcomm TLMM provider schema with this SoC-specific file. The common schema requires GPIO and interrupt provider properties, while this file restricts `compatible`, `reg`, interrupt count, optional line-name and reserved-range bounds, and local pin/function enums. The `oneOf` state-node pattern supports both flat state nodes and grouped child pin nodes.

### State And Persistence
The YAML has no mutable state. DTS data persists the physical TLMM register resource, interrupt summary line, GPIO range, reserved GPIO ranges, and pinctrl states. At runtime the Qualcomm TLMM driver maps state labels into mux selection, drive strength, bias, input/output, and GPIO/IRQ domain behavior.

### Dependencies And Integration Points
Dependencies include `qcom,tlmm-common.yaml`, `pinctrl.yaml`, `pinmux-node.yaml`, `pincfg-node.yaml`, `/schemas/types.yaml`, and interrupt-controller dt-bindings used in examples. Integration points are SoC DTSI files, board DTS pin states, Linux pinctrl and GPIO consumers, and wakeup-parent IRQ controllers when declared.

### Risks
The biggest risk is drift between the schema pin/function enum and the driver pin/function tables; a missing enum blocks valid DTS, while an extra enum can allow states the driver cannot program. Pin count limits in regexes and `gpio-line-names` must match hardware. The broad grouped-state pattern can hide semantic mistakes unless examples cover both flat and nested layouts.

### Test Signals
Run `dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/pinctrl/qcom,apq8084-pinctrl.yaml` and compile representative SoC DTSI users. Negative tests should cover invalid GPIO numbers, unsupported functions, missing `reg`, missing GPIO/IRQ provider cells, and illegal extra properties. Runtime signals are TLMM probe, GPIO chip registration, IRQ domain creation, and successful pin state switching for UART, SPI/I2C, storage, and audio/display functions listed in the enum.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,apq8084-pinctrl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,eliza-tlmm.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,eliza-tlmm.yaml

### Purpose
`qcom,eliza-tlmm.yaml` describes the Qualcomm ELIZA Top Level Mode Multiplexer controller. It binds the SoC-specific TLMM register block, GPIO and interrupt provider resources, and the legal pin/function names for pinctrl state nodes.

### Important Schema APIs
The binding provides compatible `qcom,eliza-tlmm`. Top-level required properties are `compatible`, `reg`. State nodes matching `-state$` can be direct objects or containers of `-pins` objects, and their `$defs` entry references `qcom,tlmm-common.yaml#/$defs/qcom-tlmm-state`. pin names constrained by `^gpio([0-9]|[1-9][0-9]|1[0-7][0-9]|18[0-4])$`. `function` is restricted to 123 local mux choices, starting with `gpio`, `aoss_cti`, `atest_char`, `atest_usb`, `audio_ext_mclk0`, `audio_ref_clk`, `cam_mclk`, `cci_async_in`. The local schema setting is `unevaluatedProperties: false`. It also bounds `gpio-line-names` to the SoC GPIO count. `gpio-reserved-ranges` is available for pins owned by firmware or trusted applications.

### Validation Flow
Validation composes the common Qualcomm TLMM provider schema with this SoC-specific file. The common schema requires GPIO and interrupt provider properties, while this file restricts `compatible`, `reg`, interrupt count, optional line-name and reserved-range bounds, and local pin/function enums. The `oneOf` state-node pattern supports both flat state nodes and grouped child pin nodes.

### State And Persistence
The YAML has no mutable state. DTS data persists the physical TLMM register resource, interrupt summary line, GPIO range, reserved GPIO ranges, and pinctrl states. At runtime the Qualcomm TLMM driver maps state labels into mux selection, drive strength, bias, input/output, and GPIO/IRQ domain behavior.

### Dependencies And Integration Points
Dependencies include `qcom,tlmm-common.yaml`, `pinctrl.yaml`, `pinmux-node.yaml`, `pincfg-node.yaml`, `/schemas/types.yaml`, and interrupt-controller dt-bindings used in examples. Integration points are SoC DTSI files, board DTS pin states, Linux pinctrl and GPIO consumers, and wakeup-parent IRQ controllers when declared.

### Risks
The biggest risk is drift between the schema pin/function enum and the driver pin/function tables; a missing enum blocks valid DTS, while an extra enum can allow states the driver cannot program. Pin count limits in regexes and `gpio-line-names` must match hardware. The broad grouped-state pattern can hide semantic mistakes unless examples cover both flat and nested layouts.

### Test Signals
Run `dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/pinctrl/qcom,eliza-tlmm.yaml` and compile representative SoC DTSI users. Negative tests should cover invalid GPIO numbers, unsupported functions, missing `reg`, missing GPIO/IRQ provider cells, and illegal extra properties. Runtime signals are TLMM probe, GPIO chip registration, IRQ domain creation, and successful pin state switching for UART, SPI/I2C, storage, and audio/display functions listed in the enum.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,eliza-tlmm.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,glymur-tlmm.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,glymur-tlmm.yaml

### Purpose
`qcom,glymur-tlmm.yaml` describes the Qualcomm GLYMUR Top Level Mode Multiplexer controller. It binds the SoC-specific TLMM register block, GPIO and interrupt provider resources, and the legal pin/function names for pinctrl state nodes.

### Important Schema APIs
The binding provides 2 compatible strings including `qcom,glymur-tlmm`, `qcom,mahua-tlmm`. Top-level required properties are `compatible`, `reg`. State nodes matching `-state$` can be direct objects or containers of `-pins` objects, and their `$defs` entry references `qcom,tlmm-common.yaml#/$defs/qcom-tlmm-state`. pin names constrained by `^gpio([0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9])$`. `function` is restricted to 123 local mux choices, starting with `gpio`, `resout_gpio_n`, `aoss_cti`, `asc_cci`, `atest_char`, `atest_usb`, `audio_ext_mclk0`, `audio_ext_mclk1`. The local schema setting is `unevaluatedProperties: false`. It also bounds `gpio-line-names` to the SoC GPIO count. `gpio-reserved-ranges` is available for pins owned by firmware or trusted applications.

### Validation Flow
Validation composes the common Qualcomm TLMM provider schema with this SoC-specific file. The common schema requires GPIO and interrupt provider properties, while this file restricts `compatible`, `reg`, interrupt count, optional line-name and reserved-range bounds, and local pin/function enums. The `oneOf` state-node pattern supports both flat state nodes and grouped child pin nodes.

### State And Persistence
The YAML has no mutable state. DTS data persists the physical TLMM register resource, interrupt summary line, GPIO range, reserved GPIO ranges, and pinctrl states. At runtime the Qualcomm TLMM driver maps state labels into mux selection, drive strength, bias, input/output, and GPIO/IRQ domain behavior.

### Dependencies And Integration Points
Dependencies include `qcom,tlmm-common.yaml`, `pinctrl.yaml`, `pinmux-node.yaml`, `pincfg-node.yaml`, `/schemas/types.yaml`, and interrupt-controller dt-bindings used in examples. Integration points are SoC DTSI files, board DTS pin states, Linux pinctrl and GPIO consumers, and wakeup-parent IRQ controllers when declared.

### Risks
The biggest risk is drift between the schema pin/function enum and the driver pin/function tables; a missing enum blocks valid DTS, while an extra enum can allow states the driver cannot program. Pin count limits in regexes and `gpio-line-names` must match hardware. The broad grouped-state pattern can hide semantic mistakes unless examples cover both flat and nested layouts.

### Test Signals
Run `dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/pinctrl/qcom,glymur-tlmm.yaml` and compile representative SoC DTSI users. Negative tests should cover invalid GPIO numbers, unsupported functions, missing `reg`, missing GPIO/IRQ provider cells, and illegal extra properties. Runtime signals are TLMM probe, GPIO chip registration, IRQ domain creation, and successful pin state switching for UART, SPI/I2C, storage, and audio/display functions listed in the enum.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,glymur-tlmm.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,hawi-tlmm.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,hawi-tlmm.yaml

### Purpose
`qcom,hawi-tlmm.yaml` describes the Qualcomm HAWI Top Level Mode Multiplexer controller. It binds the SoC-specific TLMM register block, GPIO and interrupt provider resources, and the legal pin/function names for pinctrl state nodes.

### Important Schema APIs
The binding provides compatible `qcom,hawi-tlmm`. Top-level required properties are `compatible`, `reg`. State nodes matching `-state$` can be direct objects or containers of `-pins` objects, and their `$defs` entry references `qcom,tlmm-common.yaml#/$defs/qcom-tlmm-state`. pin names constrained by `^gpio([0-9]|[1-9][0-9]|1[0-9][0-9]|20[0-9]|21[0-9]|22[0-5])$`. `function` is restricted to 110 local mux choices, starting with `gpio`, `aoss_cti`, `atest_char`, `atest_usb`, `audio_ext_mclk`, `audio_ref_clk`, `cam_mclk`, `cci_async_in`. The local schema setting is `unevaluatedProperties: false`. It also bounds `gpio-line-names` to the SoC GPIO count. `gpio-reserved-ranges` is available for pins owned by firmware or trusted applications.

### Validation Flow
Validation composes the common Qualcomm TLMM provider schema with this SoC-specific file. The common schema requires GPIO and interrupt provider properties, while this file restricts `compatible`, `reg`, interrupt count, optional line-name and reserved-range bounds, and local pin/function enums. The `oneOf` state-node pattern supports both flat state nodes and grouped child pin nodes.

### State And Persistence
The YAML has no mutable state. DTS data persists the physical TLMM register resource, interrupt summary line, GPIO range, reserved GPIO ranges, and pinctrl states. At runtime the Qualcomm TLMM driver maps state labels into mux selection, drive strength, bias, input/output, and GPIO/IRQ domain behavior.

### Dependencies And Integration Points
Dependencies include `qcom,tlmm-common.yaml`, `pinctrl.yaml`, `pinmux-node.yaml`, `pincfg-node.yaml`, `/schemas/types.yaml`, and interrupt-controller dt-bindings used in examples. Integration points are SoC DTSI files, board DTS pin states, Linux pinctrl and GPIO consumers, and wakeup-parent IRQ controllers when declared.

### Risks
The biggest risk is drift between the schema pin/function enum and the driver pin/function tables; a missing enum blocks valid DTS, while an extra enum can allow states the driver cannot program. Pin count limits in regexes and `gpio-line-names` must match hardware. The broad grouped-state pattern can hide semantic mistakes unless examples cover both flat and nested layouts.

### Test Signals
Run `dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/pinctrl/qcom,hawi-tlmm.yaml` and compile representative SoC DTSI users. Negative tests should cover invalid GPIO numbers, unsupported functions, missing `reg`, missing GPIO/IRQ provider cells, and illegal extra properties. Runtime signals are TLMM probe, GPIO chip registration, IRQ domain creation, and successful pin state switching for UART, SPI/I2C, storage, and audio/display functions listed in the enum.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,hawi-tlmm.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,ipq4019-pinctrl.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,ipq4019-pinctrl.yaml

### Purpose
`qcom,ipq4019-pinctrl.yaml` describes the Qualcomm IPQ4019 Top Level Mode Multiplexer controller. It binds the SoC-specific TLMM register block, GPIO and interrupt provider resources, and the legal pin/function names for pinctrl state nodes.

### Important Schema APIs
The binding provides compatible `qcom,ipq4019-pinctrl`. Top-level required properties are `compatible`, `reg`. State nodes matching `-state$` can be direct objects or containers of `-pins` objects, and their `$defs` entry references `qcom,tlmm-common.yaml#/$defs/qcom-tlmm-state`. pin names constrained by `^gpio([0-9]|[1-9][0-9])$`. `function` is restricted to 44 local mux choices, starting with `aud_pin`, `audio_pwm`, `blsp_i2c0`, `blsp_i2c1`, `blsp_spi0`, `blsp_spi1`, `blsp_uart0`, `blsp_uart1`. The local schema setting is `unevaluatedProperties: false`. `gpio-reserved-ranges` is available for pins owned by firmware or trusted applications.

### Validation Flow
Validation composes the common Qualcomm TLMM provider schema with this SoC-specific file. The common schema requires GPIO and interrupt provider properties, while this file restricts `compatible`, `reg`, interrupt count, optional line-name and reserved-range bounds, and local pin/function enums. The `oneOf` state-node pattern supports both flat state nodes and grouped child pin nodes.

### State And Persistence
The YAML has no mutable state. DTS data persists the physical TLMM register resource, interrupt summary line, GPIO range, reserved GPIO ranges, and pinctrl states. At runtime the Qualcomm TLMM driver maps state labels into mux selection, drive strength, bias, input/output, and GPIO/IRQ domain behavior.

### Dependencies And Integration Points
Dependencies include `qcom,tlmm-common.yaml`, `pinctrl.yaml`, `pinmux-node.yaml`, `pincfg-node.yaml`, `/schemas/types.yaml`, and interrupt-controller dt-bindings used in examples. Integration points are SoC DTSI files, board DTS pin states, Linux pinctrl and GPIO consumers, and wakeup-parent IRQ controllers when declared.

### Risks
The biggest risk is drift between the schema pin/function enum and the driver pin/function tables; a missing enum blocks valid DTS, while an extra enum can allow states the driver cannot program. Pin count limits in regexes and `gpio-line-names` must match hardware. The broad grouped-state pattern can hide semantic mistakes unless examples cover both flat and nested layouts.

### Test Signals
Run `dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/pinctrl/qcom,ipq4019-pinctrl.yaml` and compile representative SoC DTSI users. Negative tests should cover invalid GPIO numbers, unsupported functions, missing `reg`, missing GPIO/IRQ provider cells, and illegal extra properties. Runtime signals are TLMM probe, GPIO chip registration, IRQ domain creation, and successful pin state switching for UART, SPI/I2C, storage, and audio/display functions listed in the enum.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,ipq4019-pinctrl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,ipq5018-tlmm.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,ipq5018-tlmm.yaml

### Purpose
`qcom,ipq5018-tlmm.yaml` describes the Qualcomm IPQ5018 Top Level Mode Multiplexer controller. It binds the SoC-specific TLMM register block, GPIO and interrupt provider resources, and the legal pin/function names for pinctrl state nodes.

### Important Schema APIs
The binding provides compatible `qcom,ipq5018-tlmm`. Top-level required properties are `compatible`, `reg`. State nodes matching `-state$` can be direct objects or containers of `-pins` objects, and their `$defs` entry references `qcom,tlmm-common.yaml#/$defs/qcom-tlmm-state`. pin names constrained by `^gpio([0-9]|[1-3][0-9]|4[0-6])$`. `function` is restricted to 84 local mux choices, starting with `atest_char`, `audio_pdm0`, `audio_pdm1`, `audio_rxbclk`, `audio_rxd`, `audio_rxfsync`, `audio_rxmclk`, `audio_txbclk`. The local schema setting is `unevaluatedProperties: false`. It also bounds `gpio-line-names` to the SoC GPIO count. `gpio-reserved-ranges` is available for pins owned by firmware or trusted applications.

### Validation Flow
Validation composes the common Qualcomm TLMM provider schema with this SoC-specific file. The common schema requires GPIO and interrupt provider properties, while this file restricts `compatible`, `reg`, interrupt count, optional line-name and reserved-range bounds, and local pin/function enums. The `oneOf` state-node pattern supports both flat state nodes and grouped child pin nodes.

### State And Persistence
The YAML has no mutable state. DTS data persists the physical TLMM register resource, interrupt summary line, GPIO range, reserved GPIO ranges, and pinctrl states. At runtime the Qualcomm TLMM driver maps state labels into mux selection, drive strength, bias, input/output, and GPIO/IRQ domain behavior.

### Dependencies And Integration Points
Dependencies include `qcom,tlmm-common.yaml`, `pinctrl.yaml`, `pinmux-node.yaml`, `pincfg-node.yaml`, `/schemas/types.yaml`, and interrupt-controller dt-bindings used in examples. Integration points are SoC DTSI files, board DTS pin states, Linux pinctrl and GPIO consumers, and wakeup-parent IRQ controllers when declared.

### Risks
The biggest risk is drift between the schema pin/function enum and the driver pin/function tables; a missing enum blocks valid DTS, while an extra enum can allow states the driver cannot program. Pin count limits in regexes and `gpio-line-names` must match hardware. The broad grouped-state pattern can hide semantic mistakes unless examples cover both flat and nested layouts.

### Test Signals
Run `dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/pinctrl/qcom,ipq5018-tlmm.yaml` and compile representative SoC DTSI users. Negative tests should cover invalid GPIO numbers, unsupported functions, missing `reg`, missing GPIO/IRQ provider cells, and illegal extra properties. Runtime signals are TLMM probe, GPIO chip registration, IRQ domain creation, and successful pin state switching for UART, SPI/I2C, storage, and audio/display functions listed in the enum.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,ipq5018-tlmm.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,ipq5210-tlmm.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,ipq5210-tlmm.yaml

### Purpose
`qcom,ipq5210-tlmm.yaml` describes the Qualcomm IPQ5210 Top Level Mode Multiplexer controller. It binds the SoC-specific TLMM register block, GPIO and interrupt provider resources, and the legal pin/function names for pinctrl state nodes.

### Important Schema APIs
The binding provides compatible `qcom,ipq5210-tlmm`. Top-level required properties are `compatible`, `reg`. State nodes matching `-state$` can be direct objects or containers of `-pins` objects, and their `$defs` entry references `qcom,tlmm-common.yaml#/$defs/qcom-tlmm-state`. pin names constrained by `^gpio([0-9]|[1-4][0-9]|5[0-3])$`. `function` is restricted to 103 local mux choices, starting with `atest_char_start`, `atest_char_status0`, `atest_char_status1`, `atest_char_status2`, `atest_char_status3`, `atest_tic_en`, `audio_pri`, `audio_pri_mclk_out0`. The local schema setting is `unevaluatedProperties: false`. It also bounds `gpio-line-names` to the SoC GPIO count. `gpio-reserved-ranges` is available for pins owned by firmware or trusted applications.

### Validation Flow
Validation composes the common Qualcomm TLMM provider schema with this SoC-specific file. The common schema requires GPIO and interrupt provider properties, while this file restricts `compatible`, `reg`, interrupt count, optional line-name and reserved-range bounds, and local pin/function enums. The `oneOf` state-node pattern supports both flat state nodes and grouped child pin nodes.

### State And Persistence
The YAML has no mutable state. DTS data persists the physical TLMM register resource, interrupt summary line, GPIO range, reserved GPIO ranges, and pinctrl states. At runtime the Qualcomm TLMM driver maps state labels into mux selection, drive strength, bias, input/output, and GPIO/IRQ domain behavior.

### Dependencies And Integration Points
Dependencies include `qcom,tlmm-common.yaml`, `pinctrl.yaml`, `pinmux-node.yaml`, `pincfg-node.yaml`, `/schemas/types.yaml`, and interrupt-controller dt-bindings used in examples. Integration points are SoC DTSI files, board DTS pin states, Linux pinctrl and GPIO consumers, and wakeup-parent IRQ controllers when declared.

### Risks
The biggest risk is drift between the schema pin/function enum and the driver pin/function tables; a missing enum blocks valid DTS, while an extra enum can allow states the driver cannot program. Pin count limits in regexes and `gpio-line-names` must match hardware. The broad grouped-state pattern can hide semantic mistakes unless examples cover both flat and nested layouts.

### Test Signals
Run `dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/pinctrl/qcom,ipq5210-tlmm.yaml` and compile representative SoC DTSI users. Negative tests should cover invalid GPIO numbers, unsupported functions, missing `reg`, missing GPIO/IRQ provider cells, and illegal extra properties. Runtime signals are TLMM probe, GPIO chip registration, IRQ domain creation, and successful pin state switching for UART, SPI/I2C, storage, and audio/display functions listed in the enum.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,ipq5210-tlmm.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,ipq5332-tlmm.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,ipq5332-tlmm.yaml

### Purpose
`qcom,ipq5332-tlmm.yaml` describes the Qualcomm IPQ5332 Top Level Mode Multiplexer controller. It binds the SoC-specific TLMM register block, GPIO and interrupt provider resources, and the legal pin/function names for pinctrl state nodes.

### Important Schema APIs
The binding provides compatible `qcom,ipq5332-tlmm`. Top-level required properties are `compatible`, `reg`. State nodes matching `-state$` can be direct objects or containers of `-pins` objects, and their `$defs` entry references `qcom,tlmm-common.yaml#/$defs/qcom-tlmm-state`. pin names constrained by `^gpio([0-9]|[1-4][0-9]|5[0-2])$`. `function` is restricted to 95 local mux choices, starting with `atest_char`, `atest_char0`, `atest_char1`, `atest_char2`, `atest_char3`, `atest_tic`, `audio_pri`, `audio_pri0`. The local schema setting is `unevaluatedProperties: false`. It also bounds `gpio-line-names` to the SoC GPIO count. `gpio-reserved-ranges` is available for pins owned by firmware or trusted applications.

### Validation Flow
Validation composes the common Qualcomm TLMM provider schema with this SoC-specific file. The common schema requires GPIO and interrupt provider properties, while this file restricts `compatible`, `reg`, interrupt count, optional line-name and reserved-range bounds, and local pin/function enums. The `oneOf` state-node pattern supports both flat state nodes and grouped child pin nodes.

### State And Persistence
The YAML has no mutable state. DTS data persists the physical TLMM register resource, interrupt summary line, GPIO range, reserved GPIO ranges, and pinctrl states. At runtime the Qualcomm TLMM driver maps state labels into mux selection, drive strength, bias, input/output, and GPIO/IRQ domain behavior.

### Dependencies And Integration Points
Dependencies include `qcom,tlmm-common.yaml`, `pinctrl.yaml`, `pinmux-node.yaml`, `pincfg-node.yaml`, `/schemas/types.yaml`, and interrupt-controller dt-bindings used in examples. Integration points are SoC DTSI files, board DTS pin states, Linux pinctrl and GPIO consumers, and wakeup-parent IRQ controllers when declared.

### Risks
The biggest risk is drift between the schema pin/function enum and the driver pin/function tables; a missing enum blocks valid DTS, while an extra enum can allow states the driver cannot program. Pin count limits in regexes and `gpio-line-names` must match hardware. The broad grouped-state pattern can hide semantic mistakes unless examples cover both flat and nested layouts.

### Test Signals
Run `dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/pinctrl/qcom,ipq5332-tlmm.yaml` and compile representative SoC DTSI users. Negative tests should cover invalid GPIO numbers, unsupported functions, missing `reg`, missing GPIO/IRQ provider cells, and illegal extra properties. Runtime signals are TLMM probe, GPIO chip registration, IRQ domain creation, and successful pin state switching for UART, SPI/I2C, storage, and audio/display functions listed in the enum.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,ipq5332-tlmm.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,ipq5424-tlmm.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,ipq5424-tlmm.yaml

### Purpose
`qcom,ipq5424-tlmm.yaml` describes the Qualcomm IPQ5424 Top Level Mode Multiplexer controller. It binds the SoC-specific TLMM register block, GPIO and interrupt provider resources, and the legal pin/function names for pinctrl state nodes.

### Important Schema APIs
The binding provides compatible `qcom,ipq5424-tlmm`. Top-level required properties are `compatible`, `reg`. State nodes matching `-state$` can be direct objects or containers of `-pins` objects, and their `$defs` entry references `qcom,tlmm-common.yaml#/$defs/qcom-tlmm-state`. pin names constrained by `^gpio([0-9]|[1-4][0-9])$`. `function` is restricted to 90 local mux choices, starting with `atest_char`, `atest_char0`, `atest_char1`, `atest_char2`, `atest_char3`, `atest_tic`, `audio_pri`, `audio_pri0`. The local schema setting is `unevaluatedProperties: false`. It also bounds `gpio-line-names` to the SoC GPIO count. `gpio-reserved-ranges` is available for pins owned by firmware or trusted applications.

### Validation Flow
Validation composes the common Qualcomm TLMM provider schema with this SoC-specific file. The common schema requires GPIO and interrupt provider properties, while this file restricts `compatible`, `reg`, interrupt count, optional line-name and reserved-range bounds, and local pin/function enums. The `oneOf` state-node pattern supports both flat state nodes and grouped child pin nodes.

### State And Persistence
The YAML has no mutable state. DTS data persists the physical TLMM register resource, interrupt summary line, GPIO range, reserved GPIO ranges, and pinctrl states. At runtime the Qualcomm TLMM driver maps state labels into mux selection, drive strength, bias, input/output, and GPIO/IRQ domain behavior.

### Dependencies And Integration Points
Dependencies include `qcom,tlmm-common.yaml`, `pinctrl.yaml`, `pinmux-node.yaml`, `pincfg-node.yaml`, `/schemas/types.yaml`, and interrupt-controller dt-bindings used in examples. Integration points are SoC DTSI files, board DTS pin states, Linux pinctrl and GPIO consumers, and wakeup-parent IRQ controllers when declared.

### Risks
The biggest risk is drift between the schema pin/function enum and the driver pin/function tables; a missing enum blocks valid DTS, while an extra enum can allow states the driver cannot program. Pin count limits in regexes and `gpio-line-names` must match hardware. The broad grouped-state pattern can hide semantic mistakes unless examples cover both flat and nested layouts.

### Test Signals
Run `dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/pinctrl/qcom,ipq5424-tlmm.yaml` and compile representative SoC DTSI users. Negative tests should cover invalid GPIO numbers, unsupported functions, missing `reg`, missing GPIO/IRQ provider cells, and illegal extra properties. Runtime signals are TLMM probe, GPIO chip registration, IRQ domain creation, and successful pin state switching for UART, SPI/I2C, storage, and audio/display functions listed in the enum.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,ipq5424-tlmm.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,ipq6018-pinctrl.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,ipq6018-pinctrl.yaml

### Purpose
`qcom,ipq6018-pinctrl.yaml` describes the Qualcomm IPQ6018 Top Level Mode Multiplexer controller. It binds the SoC-specific TLMM register block, GPIO and interrupt provider resources, and the legal pin/function names for pinctrl state nodes.

### Important Schema APIs
The binding provides compatible `qcom,ipq6018-pinctrl`. Top-level required properties are `compatible`, `reg`. State nodes matching `-state$` can be direct objects or containers of `-pins` objects, and their `$defs` entry references `qcom,tlmm-common.yaml#/$defs/qcom-tlmm-state`. pin names constrained by `^gpio([1-9]|[1-7][0-9]|80)$`. `function` is restricted to 130 local mux choices, starting with `adsp_ext`, `alsp_int`, `atest_bbrx0`, `atest_bbrx1`, `atest_char`, `atest_char0`, `atest_char1`, `atest_char2`. The local schema setting is `unevaluatedProperties: false`.

### Validation Flow
Validation composes the common Qualcomm TLMM provider schema with this SoC-specific file. The common schema requires GPIO and interrupt provider properties, while this file restricts `compatible`, `reg`, interrupt count, optional line-name and reserved-range bounds, and local pin/function enums. The `oneOf` state-node pattern supports both flat state nodes and grouped child pin nodes.

### State And Persistence
The YAML has no mutable state. DTS data persists the physical TLMM register resource, interrupt summary line, GPIO range, reserved GPIO ranges, and pinctrl states. At runtime the Qualcomm TLMM driver maps state labels into mux selection, drive strength, bias, input/output, and GPIO/IRQ domain behavior.

### Dependencies And Integration Points
Dependencies include `qcom,tlmm-common.yaml`, `pinctrl.yaml`, `pinmux-node.yaml`, `pincfg-node.yaml`, `/schemas/types.yaml`, and interrupt-controller dt-bindings used in examples. Integration points are SoC DTSI files, board DTS pin states, Linux pinctrl and GPIO consumers, and wakeup-parent IRQ controllers when declared.

### Risks
The biggest risk is drift between the schema pin/function enum and the driver pin/function tables; a missing enum blocks valid DTS, while an extra enum can allow states the driver cannot program. Pin count limits in regexes and `gpio-line-names` must match hardware. The broad grouped-state pattern can hide semantic mistakes unless examples cover both flat and nested layouts.

### Test Signals
Run `dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/pinctrl/qcom,ipq6018-pinctrl.yaml` and compile representative SoC DTSI users. Negative tests should cover invalid GPIO numbers, unsupported functions, missing `reg`, missing GPIO/IRQ provider cells, and illegal extra properties. Runtime signals are TLMM probe, GPIO chip registration, IRQ domain creation, and successful pin state switching for UART, SPI/I2C, storage, and audio/display functions listed in the enum.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,ipq6018-pinctrl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,ipq8064-pinctrl.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,ipq8064-pinctrl.yaml

### Purpose
`qcom,ipq8064-pinctrl.yaml` describes the Qualcomm IPQ8064 Top Level Mode Multiplexer controller. It binds the SoC-specific TLMM register block, GPIO and interrupt provider resources, and the legal pin/function names for pinctrl state nodes.

### Important Schema APIs
The binding provides compatible `qcom,ipq8064-pinctrl`. Top-level required properties are `compatible`, `reg`. State nodes matching `-state$` can be direct objects or containers of `-pins` objects, and their `$defs` entry references `qcom,tlmm-common.yaml#/$defs/qcom-tlmm-state`. pin names constrained by `^gpio([0-9]|[1-5][0-9]|6[0-8])$`. `function` is restricted to 46 local mux choices, starting with `mdio`, `mi2s`, `pdm`, `ssbi`, `spmi`, `audio_pcm`, `gpio`, `gsbi1`. The local schema setting is `unevaluatedProperties: false`. `gpio-reserved-ranges` is available for pins owned by firmware or trusted applications.

### Validation Flow
Validation composes the common Qualcomm TLMM provider schema with this SoC-specific file. The common schema requires GPIO and interrupt provider properties, while this file restricts `compatible`, `reg`, interrupt count, optional line-name and reserved-range bounds, and local pin/function enums. The `oneOf` state-node pattern supports both flat state nodes and grouped child pin nodes.

### State And Persistence
The YAML has no mutable state. DTS data persists the physical TLMM register resource, interrupt summary line, GPIO range, reserved GPIO ranges, and pinctrl states. At runtime the Qualcomm TLMM driver maps state labels into mux selection, drive strength, bias, input/output, and GPIO/IRQ domain behavior.

### Dependencies And Integration Points
Dependencies include `qcom,tlmm-common.yaml`, `pinctrl.yaml`, `pinmux-node.yaml`, `pincfg-node.yaml`, `/schemas/types.yaml`, and interrupt-controller dt-bindings used in examples. Integration points are SoC DTSI files, board DTS pin states, Linux pinctrl and GPIO consumers, and wakeup-parent IRQ controllers when declared.

### Risks
The biggest risk is drift between the schema pin/function enum and the driver pin/function tables; a missing enum blocks valid DTS, while an extra enum can allow states the driver cannot program. Pin count limits in regexes and `gpio-line-names` must match hardware. The broad grouped-state pattern can hide semantic mistakes unless examples cover both flat and nested layouts.

### Test Signals
Run `dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/pinctrl/qcom,ipq8064-pinctrl.yaml` and compile representative SoC DTSI users. Negative tests should cover invalid GPIO numbers, unsupported functions, missing `reg`, missing GPIO/IRQ provider cells, and illegal extra properties. Runtime signals are TLMM probe, GPIO chip registration, IRQ domain creation, and successful pin state switching for UART, SPI/I2C, storage, and audio/display functions listed in the enum.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,ipq8064-pinctrl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,ipq8074-pinctrl.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,ipq8074-pinctrl.yaml

### Purpose
`qcom,ipq8074-pinctrl.yaml` describes the Qualcomm IPQ8074 Top Level Mode Multiplexer controller. It binds the SoC-specific TLMM register block, GPIO and interrupt provider resources, and the legal pin/function names for pinctrl state nodes.

### Important Schema APIs
The binding provides compatible `qcom,ipq8074-pinctrl`. Top-level required properties are `compatible`, `reg`. State nodes matching `-state$` can be direct objects or containers of `-pins` objects, and their `$defs` entry references `qcom,tlmm-common.yaml#/$defs/qcom-tlmm-state`. pin names constrained by `^gpio([0-9]|[1-6][0-9]|70)$`. `function` is restricted to 112 local mux choices, starting with `gpio`, `atest_char`, `atest_char0`, `atest_char1`, `atest_char2`, `atest_char3`, `audio_rxbclk`, `audio_rxd`. The local schema setting is `unevaluatedProperties: false`. It also bounds `gpio-line-names` to the SoC GPIO count. `gpio-reserved-ranges` is available for pins owned by firmware or trusted applications.

### Validation Flow
Validation composes the common Qualcomm TLMM provider schema with this SoC-specific file. The common schema requires GPIO and interrupt provider properties, while this file restricts `compatible`, `reg`, interrupt count, optional line-name and reserved-range bounds, and local pin/function enums. The `oneOf` state-node pattern supports both flat state nodes and grouped child pin nodes.

### State And Persistence
The YAML has no mutable state. DTS data persists the physical TLMM register resource, interrupt summary line, GPIO range, reserved GPIO ranges, and pinctrl states. At runtime the Qualcomm TLMM driver maps state labels into mux selection, drive strength, bias, input/output, and GPIO/IRQ domain behavior.

### Dependencies And Integration Points
Dependencies include `qcom,tlmm-common.yaml`, `pinctrl.yaml`, `pinmux-node.yaml`, `pincfg-node.yaml`, `/schemas/types.yaml`, and interrupt-controller dt-bindings used in examples. Integration points are SoC DTSI files, board DTS pin states, Linux pinctrl and GPIO consumers, and wakeup-parent IRQ controllers when declared.

### Risks
The biggest risk is drift between the schema pin/function enum and the driver pin/function tables; a missing enum blocks valid DTS, while an extra enum can allow states the driver cannot program. Pin count limits in regexes and `gpio-line-names` must match hardware. The broad grouped-state pattern can hide semantic mistakes unless examples cover both flat and nested layouts.

### Test Signals
Run `dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/pinctrl/qcom,ipq8074-pinctrl.yaml` and compile representative SoC DTSI users. Negative tests should cover invalid GPIO numbers, unsupported functions, missing `reg`, missing GPIO/IRQ provider cells, and illegal extra properties. Runtime signals are TLMM probe, GPIO chip registration, IRQ domain creation, and successful pin state switching for UART, SPI/I2C, storage, and audio/display functions listed in the enum.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,ipq8074-pinctrl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,ipq9574-tlmm.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,ipq9574-tlmm.yaml

### Purpose
`qcom,ipq9574-tlmm.yaml` describes the Qualcomm IPQ9574 Top Level Mode Multiplexer controller. It binds the SoC-specific TLMM register block, GPIO and interrupt provider resources, and the legal pin/function names for pinctrl state nodes.

### Important Schema APIs
The binding provides compatible `qcom,ipq9574-tlmm`. Top-level required properties are `compatible`, `reg`. State nodes matching `-state$` can be direct objects or containers of `-pins` objects, and their `$defs` entry references `qcom,tlmm-common.yaml#/$defs/qcom-tlmm-state`. pin names constrained by `^gpio([0-9]|[1-5][0-9]|6[0-4])$`. `function` is restricted to 80 local mux choices, starting with `atest_char`, `atest_char0`, `atest_char1`, `atest_char2`, `atest_char3`, `audio_pdm0`, `audio_pdm1`, `audio_pri`. The local schema setting is `unevaluatedProperties: false`. It also bounds `gpio-line-names` to the SoC GPIO count. `gpio-reserved-ranges` is available for pins owned by firmware or trusted applications.

### Validation Flow
Validation composes the common Qualcomm TLMM provider schema with this SoC-specific file. The common schema requires GPIO and interrupt provider properties, while this file restricts `compatible`, `reg`, interrupt count, optional line-name and reserved-range bounds, and local pin/function enums. The `oneOf` state-node pattern supports both flat state nodes and grouped child pin nodes.

### State And Persistence
The YAML has no mutable state. DTS data persists the physical TLMM register resource, interrupt summary line, GPIO range, reserved GPIO ranges, and pinctrl states. At runtime the Qualcomm TLMM driver maps state labels into mux selection, drive strength, bias, input/output, and GPIO/IRQ domain behavior.

### Dependencies And Integration Points
Dependencies include `qcom,tlmm-common.yaml`, `pinctrl.yaml`, `pinmux-node.yaml`, `pincfg-node.yaml`, `/schemas/types.yaml`, and interrupt-controller dt-bindings used in examples. Integration points are SoC DTSI files, board DTS pin states, Linux pinctrl and GPIO consumers, and wakeup-parent IRQ controllers when declared.

### Risks
The biggest risk is drift between the schema pin/function enum and the driver pin/function tables; a missing enum blocks valid DTS, while an extra enum can allow states the driver cannot program. Pin count limits in regexes and `gpio-line-names` must match hardware. The broad grouped-state pattern can hide semantic mistakes unless examples cover both flat and nested layouts.

### Test Signals
Run `dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/pinctrl/qcom,ipq9574-tlmm.yaml` and compile representative SoC DTSI users. Negative tests should cover invalid GPIO numbers, unsupported functions, missing `reg`, missing GPIO/IRQ provider cells, and illegal extra properties. Runtime signals are TLMM probe, GPIO chip registration, IRQ domain creation, and successful pin state switching for UART, SPI/I2C, storage, and audio/display functions listed in the enum.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,ipq9574-tlmm.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,kaanapali-tlmm.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,kaanapali-tlmm.yaml

### Purpose
`qcom,kaanapali-tlmm.yaml` describes the Qualcomm KAANAPALI Top Level Mode Multiplexer controller. It binds the SoC-specific TLMM register block, GPIO and interrupt provider resources, and the legal pin/function names for pinctrl state nodes.

### Important Schema APIs
The binding provides compatible `qcom,kaanapali-tlmm`. Top-level required properties are `compatible`, `reg`. State nodes matching `-state$` can be direct objects or containers of `-pins` objects, and their `$defs` entry references `qcom,tlmm-common.yaml#/$defs/qcom-tlmm-state`. pin names constrained by `^gpio([0-9]|[1-9][0-9]|1[0-9][0-9]|20[0-9]|21[0-6])$`. `function` is restricted to 146 local mux choices, starting with `gpio`, `aoss_cti`, `atest_char`, `atest_usb`, `audio_ext_mclk0`, `audio_ext_mclk1`, `audio_ref_clk`, `cam_asc_mclk2`. The local schema setting is `unevaluatedProperties: false`. It also bounds `gpio-line-names` to the SoC GPIO count. `gpio-reserved-ranges` is available for pins owned by firmware or trusted applications.

### Validation Flow
Validation composes the common Qualcomm TLMM provider schema with this SoC-specific file. The common schema requires GPIO and interrupt provider properties, while this file restricts `compatible`, `reg`, interrupt count, optional line-name and reserved-range bounds, and local pin/function enums. The `oneOf` state-node pattern supports both flat state nodes and grouped child pin nodes.

### State And Persistence
The YAML has no mutable state. DTS data persists the physical TLMM register resource, interrupt summary line, GPIO range, reserved GPIO ranges, and pinctrl states. At runtime the Qualcomm TLMM driver maps state labels into mux selection, drive strength, bias, input/output, and GPIO/IRQ domain behavior.

### Dependencies And Integration Points
Dependencies include `qcom,tlmm-common.yaml`, `pinctrl.yaml`, `pinmux-node.yaml`, `pincfg-node.yaml`, `/schemas/types.yaml`, and interrupt-controller dt-bindings used in examples. Integration points are SoC DTSI files, board DTS pin states, Linux pinctrl and GPIO consumers, and wakeup-parent IRQ controllers when declared.

### Risks
The biggest risk is drift between the schema pin/function enum and the driver pin/function tables; a missing enum blocks valid DTS, while an extra enum can allow states the driver cannot program. Pin count limits in regexes and `gpio-line-names` must match hardware. The broad grouped-state pattern can hide semantic mistakes unless examples cover both flat and nested layouts.

### Test Signals
Run `dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/pinctrl/qcom,kaanapali-tlmm.yaml` and compile representative SoC DTSI users. Negative tests should cover invalid GPIO numbers, unsupported functions, missing `reg`, missing GPIO/IRQ provider cells, and illegal extra properties. Runtime signals are TLMM probe, GPIO chip registration, IRQ domain creation, and successful pin state switching for UART, SPI/I2C, storage, and audio/display functions listed in the enum.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,kaanapali-tlmm.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,lpass-lpi-common.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,lpass-lpi-common.yaml

### Purpose
`qcom,lpass-lpi-common.yaml` is the reusable common schema for Qualcomm LPASS Low Power Island TLMM controllers. It captures the GPIO-provider contract and the shared state-node pinconf/pinmux vocabulary used by LPASS LPI bindings such as Milos, SC7280, SC8280XP, SDM660, and SDM670.

### Important Schema APIs
The controller requires `gpio-controller`, `#gpio-cells`, and `gpio-ranges`, and optionally supports `gpio-reserved-ranges`. Its `$defs/qcom-tlmm-state` requires `pins` and `function`, composes `pincfg-node.yaml` and `pinmux-node.yaml`, and permits drive strengths 2 through 16 mA, `slew-rate` values 0 through 3, bus-hold/pull/disable bias controls, input enablement, and output high/low.

### Validation Flow
Concrete LPASS schemas first validate SoC-specific compatible, registers, clocks, and local pin/function enums, then reference this common schema through `allOf`. State nodes therefore inherit the generic pinconf and mux rules while concrete files close `unevaluatedProperties` and restrict legal GPIO names.

### State And Persistence
The YAML is stateless. DTS state persists LPASS audio pin mux, GPIO numbering, reserved ranges, and electrical settings used by the LPASS LPI pinctrl driver. Because LPASS pins often gate audio interfaces, stale pin states can affect audio bring-up and low-power transitions.

### Dependencies And Integration Points
It depends on `pinctrl.yaml`, `pincfg-node.yaml`, and `pinmux-node.yaml`. It integrates with the Linux GPIO and pinctrl subsystems, LPASS clock providers in the concrete bindings, and audio clients such as SoundWire, I2S, DMIC, and external master clock consumers.

### Risks
The common schema permits `additionalProperties: true`, so concrete LPASS bindings must close their schemas. Requiring `pins` and `function` is stricter than generic TLMM and should match driver expectations. GPIO reserved ranges must remain synchronized with firmware ownership or LPASS-internal reservations.

### Test Signals
Run dt-schema checks for this common schema and every LPASS consumer. Useful negative cases include missing `function`, unsupported `slew-rate`, wrong `#gpio-cells`, and reserved-range tuple errors; runtime tests should verify audio pin states and GPIO range registration.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,lpass-lpi-common.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,mdm9607-tlmm.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,mdm9607-tlmm.yaml

### Purpose
`qcom,mdm9607-tlmm.yaml` describes the Qualcomm MDM9607 Top Level Mode Multiplexer controller. It binds the SoC-specific TLMM register block, GPIO and interrupt provider resources, and the legal pin/function names for pinctrl state nodes.

### Important Schema APIs
The binding provides compatible `qcom,mdm9607-tlmm`. Top-level required properties are `compatible`, `reg`. State nodes matching `-state$` can be direct objects or containers of `-pins` objects, and their `$defs` entry references `qcom,tlmm-common.yaml#/$defs/qcom-tlmm-state`. pin names constrained by `^gpio([1-9]|[1-7][0-9]|80)$`. `function` is restricted to 127 local mux choices, starting with `adsp_ext`, `atest_bbrx0`, `atest_bbrx1`, `atest_char`, `atest_char0`, `atest_char1`, `atest_char2`, `atest_char3`. The local schema setting is `unevaluatedProperties: false`. `gpio-reserved-ranges` is available for pins owned by firmware or trusted applications.

### Validation Flow
Validation composes the common Qualcomm TLMM provider schema with this SoC-specific file. The common schema requires GPIO and interrupt provider properties, while this file restricts `compatible`, `reg`, interrupt count, optional line-name and reserved-range bounds, and local pin/function enums. The `oneOf` state-node pattern supports both flat state nodes and grouped child pin nodes.

### State And Persistence
The YAML has no mutable state. DTS data persists the physical TLMM register resource, interrupt summary line, GPIO range, reserved GPIO ranges, and pinctrl states. At runtime the Qualcomm TLMM driver maps state labels into mux selection, drive strength, bias, input/output, and GPIO/IRQ domain behavior.

### Dependencies And Integration Points
Dependencies include `qcom,tlmm-common.yaml`, `pinctrl.yaml`, `pinmux-node.yaml`, `pincfg-node.yaml`, `/schemas/types.yaml`, and interrupt-controller dt-bindings used in examples. Integration points are SoC DTSI files, board DTS pin states, Linux pinctrl and GPIO consumers, and wakeup-parent IRQ controllers when declared.

### Risks
The biggest risk is drift between the schema pin/function enum and the driver pin/function tables; a missing enum blocks valid DTS, while an extra enum can allow states the driver cannot program. Pin count limits in regexes and `gpio-line-names` must match hardware. The broad grouped-state pattern can hide semantic mistakes unless examples cover both flat and nested layouts.

### Test Signals
Run `dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/pinctrl/qcom,mdm9607-tlmm.yaml` and compile representative SoC DTSI users. Negative tests should cover invalid GPIO numbers, unsupported functions, missing `reg`, missing GPIO/IRQ provider cells, and illegal extra properties. Runtime signals are TLMM probe, GPIO chip registration, IRQ domain creation, and successful pin state switching for UART, SPI/I2C, storage, and audio/display functions listed in the enum.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,mdm9607-tlmm.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,mdm9615-pinctrl.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,mdm9615-pinctrl.yaml

### Purpose
`qcom,mdm9615-pinctrl.yaml` describes the Qualcomm MDM9615 Top Level Mode Multiplexer controller. It binds the SoC-specific TLMM register block, GPIO and interrupt provider resources, and the legal pin/function names for pinctrl state nodes.

### Important Schema APIs
The binding provides compatible `qcom,mdm9615-pinctrl`. Top-level required properties are `compatible`, `reg`. State nodes matching `-state$` can be direct objects or containers of `-pins` objects, and their `$defs` entry references `qcom,tlmm-common.yaml#/$defs/qcom-tlmm-state`. pin names constrained by `^gpio([0-9]|[1-7][0-9]|8[0-7])$`. `function` is restricted to 12 local mux choices, starting with `gpio`, `gsbi2_i2c`, `gsbi3`, `gsbi4`, `gsbi5_i2c`, `gsbi5_uart`, `sdc2`, `ebi2_lcdc`. The local schema setting is `unevaluatedProperties: false`.

### Validation Flow
Validation composes the common Qualcomm TLMM provider schema with this SoC-specific file. The common schema requires GPIO and interrupt provider properties, while this file restricts `compatible`, `reg`, interrupt count, optional line-name and reserved-range bounds, and local pin/function enums. The `oneOf` state-node pattern supports both flat state nodes and grouped child pin nodes.

### State And Persistence
The YAML has no mutable state. DTS data persists the physical TLMM register resource, interrupt summary line, GPIO range, reserved GPIO ranges, and pinctrl states. At runtime the Qualcomm TLMM driver maps state labels into mux selection, drive strength, bias, input/output, and GPIO/IRQ domain behavior.

### Dependencies And Integration Points
Dependencies include `qcom,tlmm-common.yaml`, `pinctrl.yaml`, `pinmux-node.yaml`, `pincfg-node.yaml`, `/schemas/types.yaml`, and interrupt-controller dt-bindings used in examples. Integration points are SoC DTSI files, board DTS pin states, Linux pinctrl and GPIO consumers, and wakeup-parent IRQ controllers when declared.

### Risks
The biggest risk is drift between the schema pin/function enum and the driver pin/function tables; a missing enum blocks valid DTS, while an extra enum can allow states the driver cannot program. Pin count limits in regexes and `gpio-line-names` must match hardware. The broad grouped-state pattern can hide semantic mistakes unless examples cover both flat and nested layouts.

### Test Signals
Run `dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/pinctrl/qcom,mdm9615-pinctrl.yaml` and compile representative SoC DTSI users. Negative tests should cover invalid GPIO numbers, unsupported functions, missing `reg`, missing GPIO/IRQ provider cells, and illegal extra properties. Runtime signals are TLMM probe, GPIO chip registration, IRQ domain creation, and successful pin state switching for UART, SPI/I2C, storage, and audio/display functions listed in the enum.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,mdm9615-pinctrl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,milos-lpass-lpi-pinctrl.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,milos-lpass-lpi-pinctrl.yaml

### Purpose
`qcom,milos-lpass-lpi-pinctrl.yaml` describes the Qualcomm MILOS LPASS LPI TLMM pin controller. It specializes the common LPASS LPI schema with this SoC's compatible string, register layout, GPIO pin range, and audio-oriented mux function list.

### Important Schema APIs
The binding provides compatible `qcom,milos-lpass-lpi-pinctrl`. Top-level required properties are `compatible`, `reg`, `clocks`, `clock-names`. The controller also requires clock handles and `clock-names` where the file declares LPASS vote clocks. State nodes matching `-state$` can either be direct state objects or containers of `-pins` objects. They reference `qcom,lpass-lpi-common.yaml#/$defs/qcom-tlmm-state`, so each state requires `pins` and `function` and may set LPASS drive strength, slew rate, bias, input, and output properties. pin names constrained by `^gpio([0-9]|1[0-9]|2[0-2])$`. `function` is restricted to 36 local mux choices, starting with `dmic1_clk`, `dmic1_data`, `dmic2_clk`, `dmic2_data`, `dmic3_clk`, `dmic3_data`, `dmic4_clk`, `dmic4_data`.

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

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,milos-lpass-lpi-pinctrl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,milos-tlmm.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,milos-tlmm.yaml

### Purpose
`qcom,milos-tlmm.yaml` describes the Qualcomm MILOS Top Level Mode Multiplexer controller. It binds the SoC-specific TLMM register block, GPIO and interrupt provider resources, and the legal pin/function names for pinctrl state nodes.

### Important Schema APIs
The binding provides compatible `qcom,milos-tlmm`. Top-level required properties are `compatible`, `reg`. State nodes matching `-state$` can be direct objects or containers of `-pins` objects, and their `$defs` entry references `qcom,tlmm-common.yaml#/$defs/qcom-tlmm-state`. pin names constrained by `^gpio([0-9]|[1-9][0-9]|1[0-5][0-9]|16[0-7])$`. `function` is restricted to 113 local mux choices, starting with `gpio`, `aoss_cti`, `atest_char`, `atest_usb`, `audio_ext_mclk0`, `audio_ext_mclk1`, `audio_ref_clk`, `cam_mclk`. The local schema setting is `unevaluatedProperties: false`. It also bounds `gpio-line-names` to the SoC GPIO count. `gpio-reserved-ranges` is available for pins owned by firmware or trusted applications.

### Validation Flow
Validation composes the common Qualcomm TLMM provider schema with this SoC-specific file. The common schema requires GPIO and interrupt provider properties, while this file restricts `compatible`, `reg`, interrupt count, optional line-name and reserved-range bounds, and local pin/function enums. The `oneOf` state-node pattern supports both flat state nodes and grouped child pin nodes.

### State And Persistence
The YAML has no mutable state. DTS data persists the physical TLMM register resource, interrupt summary line, GPIO range, reserved GPIO ranges, and pinctrl states. At runtime the Qualcomm TLMM driver maps state labels into mux selection, drive strength, bias, input/output, and GPIO/IRQ domain behavior.

### Dependencies And Integration Points
Dependencies include `qcom,tlmm-common.yaml`, `pinctrl.yaml`, `pinmux-node.yaml`, `pincfg-node.yaml`, `/schemas/types.yaml`, and interrupt-controller dt-bindings used in examples. Integration points are SoC DTSI files, board DTS pin states, Linux pinctrl and GPIO consumers, and wakeup-parent IRQ controllers when declared.

### Risks
The biggest risk is drift between the schema pin/function enum and the driver pin/function tables; a missing enum blocks valid DTS, while an extra enum can allow states the driver cannot program. Pin count limits in regexes and `gpio-line-names` must match hardware. The broad grouped-state pattern can hide semantic mistakes unless examples cover both flat and nested layouts.

### Test Signals
Run `dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/pinctrl/qcom,milos-tlmm.yaml` and compile representative SoC DTSI users. Negative tests should cover invalid GPIO numbers, unsupported functions, missing `reg`, missing GPIO/IRQ provider cells, and illegal extra properties. Runtime signals are TLMM probe, GPIO chip registration, IRQ domain creation, and successful pin state switching for UART, SPI/I2C, storage, and audio/display functions listed in the enum.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,milos-tlmm.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,msm8226-pinctrl.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,msm8226-pinctrl.yaml

### Purpose
`qcom,msm8226-pinctrl.yaml` describes the Qualcomm MSM8226 Top Level Mode Multiplexer controller. It binds the SoC-specific TLMM register block, GPIO and interrupt provider resources, and the legal pin/function names for pinctrl state nodes.

### Important Schema APIs
The binding provides compatible `qcom,msm8226-pinctrl`. Top-level required properties are `compatible`, `reg`. State nodes matching `-state$` can be direct objects or containers of `-pins` objects, and their `$defs` entry references `qcom,tlmm-common.yaml#/$defs/qcom-tlmm-state`. pin names constrained by `^gpio([0-9]|[1-9][0-9]|10[0-9]|11[0-6])$`. `function` is restricted to 27 local mux choices, starting with `gpio`, `cci_i2c0`, `blsp_uim1`, `blsp_uim2`, `blsp_uim3`, `blsp_uim5`, `blsp_i2c1`, `blsp_i2c2`. The local schema setting is `unevaluatedProperties: false`. `gpio-reserved-ranges` is available for pins owned by firmware or trusted applications.

### Validation Flow
Validation composes the common Qualcomm TLMM provider schema with this SoC-specific file. The common schema requires GPIO and interrupt provider properties, while this file restricts `compatible`, `reg`, interrupt count, optional line-name and reserved-range bounds, and local pin/function enums. The `oneOf` state-node pattern supports both flat state nodes and grouped child pin nodes.

### State And Persistence
The YAML has no mutable state. DTS data persists the physical TLMM register resource, interrupt summary line, GPIO range, reserved GPIO ranges, and pinctrl states. At runtime the Qualcomm TLMM driver maps state labels into mux selection, drive strength, bias, input/output, and GPIO/IRQ domain behavior.

### Dependencies And Integration Points
Dependencies include `qcom,tlmm-common.yaml`, `pinctrl.yaml`, `pinmux-node.yaml`, `pincfg-node.yaml`, `/schemas/types.yaml`, and interrupt-controller dt-bindings used in examples. Integration points are SoC DTSI files, board DTS pin states, Linux pinctrl and GPIO consumers, and wakeup-parent IRQ controllers when declared.

### Risks
The biggest risk is drift between the schema pin/function enum and the driver pin/function tables; a missing enum blocks valid DTS, while an extra enum can allow states the driver cannot program. Pin count limits in regexes and `gpio-line-names` must match hardware. The broad grouped-state pattern can hide semantic mistakes unless examples cover both flat and nested layouts.

### Test Signals
Run `dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/pinctrl/qcom,msm8226-pinctrl.yaml` and compile representative SoC DTSI users. Negative tests should cover invalid GPIO numbers, unsupported functions, missing `reg`, missing GPIO/IRQ provider cells, and illegal extra properties. Runtime signals are TLMM probe, GPIO chip registration, IRQ domain creation, and successful pin state switching for UART, SPI/I2C, storage, and audio/display functions listed in the enum.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,msm8226-pinctrl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,msm8660-pinctrl.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,msm8660-pinctrl.yaml

### Purpose
`qcom,msm8660-pinctrl.yaml` describes the Qualcomm MSM8660 Top Level Mode Multiplexer controller. It binds the SoC-specific TLMM register block, GPIO and interrupt provider resources, and the legal pin/function names for pinctrl state nodes.

### Important Schema APIs
The binding provides compatible `qcom,msm8660-pinctrl`. Top-level required properties are `compatible`, `reg`. State nodes matching `-state$` can be direct objects or containers of `-pins` objects, and their `$defs` entry references `qcom,tlmm-common.yaml#/$defs/qcom-tlmm-state`. pin names constrained by `^gpio([0-9]|[1-9][0-9]|1[0-6][0-9]|17[0-2])$`. `function` is restricted to 53 local mux choices, starting with `gpio`, `cam_mclk`, `dsub`, `ext_gps`, `gp_clk_0a`, `gp_clk_0b`, `gp_clk_1a`, `gp_clk_1b`. The local schema setting is `unevaluatedProperties: false`. It also bounds `gpio-line-names` to the SoC GPIO count. `gpio-reserved-ranges` is available for pins owned by firmware or trusted applications.

### Validation Flow
Validation composes the common Qualcomm TLMM provider schema with this SoC-specific file. The common schema requires GPIO and interrupt provider properties, while this file restricts `compatible`, `reg`, interrupt count, optional line-name and reserved-range bounds, and local pin/function enums. The `oneOf` state-node pattern supports both flat state nodes and grouped child pin nodes.

### State And Persistence
The YAML has no mutable state. DTS data persists the physical TLMM register resource, interrupt summary line, GPIO range, reserved GPIO ranges, and pinctrl states. At runtime the Qualcomm TLMM driver maps state labels into mux selection, drive strength, bias, input/output, and GPIO/IRQ domain behavior.

### Dependencies And Integration Points
Dependencies include `qcom,tlmm-common.yaml`, `pinctrl.yaml`, `pinmux-node.yaml`, `pincfg-node.yaml`, `/schemas/types.yaml`, and interrupt-controller dt-bindings used in examples. Integration points are SoC DTSI files, board DTS pin states, Linux pinctrl and GPIO consumers, and wakeup-parent IRQ controllers when declared.

### Risks
The biggest risk is drift between the schema pin/function enum and the driver pin/function tables; a missing enum blocks valid DTS, while an extra enum can allow states the driver cannot program. Pin count limits in regexes and `gpio-line-names` must match hardware. The broad grouped-state pattern can hide semantic mistakes unless examples cover both flat and nested layouts.

### Test Signals
Run `dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/pinctrl/qcom,msm8660-pinctrl.yaml` and compile representative SoC DTSI users. Negative tests should cover invalid GPIO numbers, unsupported functions, missing `reg`, missing GPIO/IRQ provider cells, and illegal extra properties. Runtime signals are TLMM probe, GPIO chip registration, IRQ domain creation, and successful pin state switching for UART, SPI/I2C, storage, and audio/display functions listed in the enum.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,msm8660-pinctrl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,msm8909-tlmm.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,msm8909-tlmm.yaml

### Purpose
`qcom,msm8909-tlmm.yaml` describes the Qualcomm MSM8909 Top Level Mode Multiplexer controller. It binds the SoC-specific TLMM register block, GPIO and interrupt provider resources, and the legal pin/function names for pinctrl state nodes.

### Important Schema APIs
The binding provides compatible `qcom,msm8909-tlmm`. Top-level required properties are `compatible`, `reg`. State nodes matching `-state$` can be direct objects or containers of `-pins` objects, and their `$defs` entry references `qcom,tlmm-common.yaml#/$defs/qcom-tlmm-state`. pin names constrained by `^gpio([0-9]|[1-9][0-9]|10[0-9]|11[0-2])$`. `function` is restricted to 123 local mux choices, starting with `adsp_ext`, `atest_bbrx0`, `atest_bbrx1`, `atest_char`, `atest_char0`, `atest_char1`, `atest_char2`, `atest_char3`. The local schema setting is `unevaluatedProperties: false`. `gpio-reserved-ranges` is available for pins owned by firmware or trusted applications.

### Validation Flow
Validation composes the common Qualcomm TLMM provider schema with this SoC-specific file. The common schema requires GPIO and interrupt provider properties, while this file restricts `compatible`, `reg`, interrupt count, optional line-name and reserved-range bounds, and local pin/function enums. The `oneOf` state-node pattern supports both flat state nodes and grouped child pin nodes.

### State And Persistence
The YAML has no mutable state. DTS data persists the physical TLMM register resource, interrupt summary line, GPIO range, reserved GPIO ranges, and pinctrl states. At runtime the Qualcomm TLMM driver maps state labels into mux selection, drive strength, bias, input/output, and GPIO/IRQ domain behavior.

### Dependencies And Integration Points
Dependencies include `qcom,tlmm-common.yaml`, `pinctrl.yaml`, `pinmux-node.yaml`, `pincfg-node.yaml`, `/schemas/types.yaml`, and interrupt-controller dt-bindings used in examples. Integration points are SoC DTSI files, board DTS pin states, Linux pinctrl and GPIO consumers, and wakeup-parent IRQ controllers when declared.

### Risks
The biggest risk is drift between the schema pin/function enum and the driver pin/function tables; a missing enum blocks valid DTS, while an extra enum can allow states the driver cannot program. Pin count limits in regexes and `gpio-line-names` must match hardware. The broad grouped-state pattern can hide semantic mistakes unless examples cover both flat and nested layouts.

### Test Signals
Run `dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/pinctrl/qcom,msm8909-tlmm.yaml` and compile representative SoC DTSI users. Negative tests should cover invalid GPIO numbers, unsupported functions, missing `reg`, missing GPIO/IRQ provider cells, and illegal extra properties. Runtime signals are TLMM probe, GPIO chip registration, IRQ domain creation, and successful pin state switching for UART, SPI/I2C, storage, and audio/display functions listed in the enum.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,msm8909-tlmm.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,msm8916-pinctrl.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,msm8916-pinctrl.yaml

### Purpose
`qcom,msm8916-pinctrl.yaml` describes the Qualcomm MSM8916 Top Level Mode Multiplexer controller. It binds the SoC-specific TLMM register block, GPIO and interrupt provider resources, and the legal pin/function names for pinctrl state nodes.

### Important Schema APIs
The binding provides compatible `qcom,msm8916-pinctrl`. Top-level required properties are `compatible`, `reg`. State nodes matching `-state$` can be direct objects or containers of `-pins` objects, and their `$defs` entry references `qcom,tlmm-common.yaml#/$defs/qcom-tlmm-state`. pin names constrained by `^gpio([0-9]|[1-9][0-9]|1[0-1][0-9]|12[01])$`. `function` is restricted to 128 local mux choices, starting with `gpio`, `adsp_ext`, `alsp_int`, `atest_bbrx0`, `atest_bbrx1`, `atest_char`, `atest_char0`, `atest_char1`. The local schema setting is `unevaluatedProperties: false`. It also bounds `gpio-line-names` to the SoC GPIO count. `gpio-reserved-ranges` is available for pins owned by firmware or trusted applications.

### Validation Flow
Validation composes the common Qualcomm TLMM provider schema with this SoC-specific file. The common schema requires GPIO and interrupt provider properties, while this file restricts `compatible`, `reg`, interrupt count, optional line-name and reserved-range bounds, and local pin/function enums. The `oneOf` state-node pattern supports both flat state nodes and grouped child pin nodes.

### State And Persistence
The YAML has no mutable state. DTS data persists the physical TLMM register resource, interrupt summary line, GPIO range, reserved GPIO ranges, and pinctrl states. At runtime the Qualcomm TLMM driver maps state labels into mux selection, drive strength, bias, input/output, and GPIO/IRQ domain behavior.

### Dependencies And Integration Points
Dependencies include `qcom,tlmm-common.yaml`, `pinctrl.yaml`, `pinmux-node.yaml`, `pincfg-node.yaml`, `/schemas/types.yaml`, and interrupt-controller dt-bindings used in examples. Integration points are SoC DTSI files, board DTS pin states, Linux pinctrl and GPIO consumers, and wakeup-parent IRQ controllers when declared.

### Risks
The biggest risk is drift between the schema pin/function enum and the driver pin/function tables; a missing enum blocks valid DTS, while an extra enum can allow states the driver cannot program. Pin count limits in regexes and `gpio-line-names` must match hardware. The broad grouped-state pattern can hide semantic mistakes unless examples cover both flat and nested layouts.

### Test Signals
Run `dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/pinctrl/qcom,msm8916-pinctrl.yaml` and compile representative SoC DTSI users. Negative tests should cover invalid GPIO numbers, unsupported functions, missing `reg`, missing GPIO/IRQ provider cells, and illegal extra properties. Runtime signals are TLMM probe, GPIO chip registration, IRQ domain creation, and successful pin state switching for UART, SPI/I2C, storage, and audio/display functions listed in the enum.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,msm8916-pinctrl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,msm8917-pinctrl.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,msm8917-pinctrl.yaml

### Purpose
`qcom,msm8917-pinctrl.yaml` describes the Qualcomm MSM8917 Top Level Mode Multiplexer controller. It binds the SoC-specific TLMM register block, GPIO and interrupt provider resources, and the legal pin/function names for pinctrl state nodes.

### Important Schema APIs
The binding provides compatible `qcom,msm8917-pinctrl`. Top-level required properties are `compatible`, `reg`. State nodes matching `-state$` can be direct objects or containers of `-pins` objects, and their `$defs` entry references `qcom,tlmm-common.yaml#/$defs/qcom-tlmm-state`. pin names constrained by `^gpio([0-9]|[1-9][0-9]|1[0-2][0-9]|13[0-3])$`. `function` is restricted to 162 local mux choices, starting with `accel_int`, `adsp_ext`, `alsp_int`, `atest_bbrx0`, `atest_bbrx1`, `atest_char`, `atest_char0`, `atest_char1`. The local schema setting is `unevaluatedProperties: false`. It also bounds `gpio-line-names` to the SoC GPIO count. `gpio-reserved-ranges` is available for pins owned by firmware or trusted applications.

### Validation Flow
Validation composes the common Qualcomm TLMM provider schema with this SoC-specific file. The common schema requires GPIO and interrupt provider properties, while this file restricts `compatible`, `reg`, interrupt count, optional line-name and reserved-range bounds, and local pin/function enums. The `oneOf` state-node pattern supports both flat state nodes and grouped child pin nodes.

### State And Persistence
The YAML has no mutable state. DTS data persists the physical TLMM register resource, interrupt summary line, GPIO range, reserved GPIO ranges, and pinctrl states. At runtime the Qualcomm TLMM driver maps state labels into mux selection, drive strength, bias, input/output, and GPIO/IRQ domain behavior.

### Dependencies And Integration Points
Dependencies include `qcom,tlmm-common.yaml`, `pinctrl.yaml`, `pinmux-node.yaml`, `pincfg-node.yaml`, `/schemas/types.yaml`, and interrupt-controller dt-bindings used in examples. Integration points are SoC DTSI files, board DTS pin states, Linux pinctrl and GPIO consumers, and wakeup-parent IRQ controllers when declared.

### Risks
The biggest risk is drift between the schema pin/function enum and the driver pin/function tables; a missing enum blocks valid DTS, while an extra enum can allow states the driver cannot program. Pin count limits in regexes and `gpio-line-names` must match hardware. The broad grouped-state pattern can hide semantic mistakes unless examples cover both flat and nested layouts.

### Test Signals
Run `dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/pinctrl/qcom,msm8917-pinctrl.yaml` and compile representative SoC DTSI users. Negative tests should cover invalid GPIO numbers, unsupported functions, missing `reg`, missing GPIO/IRQ provider cells, and illegal extra properties. Runtime signals are TLMM probe, GPIO chip registration, IRQ domain creation, and successful pin state switching for UART, SPI/I2C, storage, and audio/display functions listed in the enum.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,msm8917-pinctrl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,msm8953-pinctrl.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,msm8953-pinctrl.yaml

### Purpose
`qcom,msm8953-pinctrl.yaml` describes the Qualcomm MSM8953 Top Level Mode Multiplexer controller. It binds the SoC-specific TLMM register block, GPIO and interrupt provider resources, and the legal pin/function names for pinctrl state nodes.

### Important Schema APIs
The binding provides compatible `qcom,msm8953-pinctrl`. Top-level required properties are `compatible`, `reg`. State nodes matching `-state$` can be direct objects or containers of `-pins` objects, and their `$defs` entry references `qcom,tlmm-common.yaml#/$defs/qcom-tlmm-state`. pin names constrained by `^gpio([0-9]|[1-9][0-9]|1[0-3][0-9]|14[01])$`. `function` is restricted to 201 local mux choices, starting with `accel_int`, `adsp_ext`, `alsp_int`, `atest_bbrx0`, `atest_bbrx1`, `atest_char`, `atest_char0`, `atest_char1`. The local schema setting is `unevaluatedProperties: false`. `gpio-reserved-ranges` is available for pins owned by firmware or trusted applications.

### Validation Flow
Validation composes the common Qualcomm TLMM provider schema with this SoC-specific file. The common schema requires GPIO and interrupt provider properties, while this file restricts `compatible`, `reg`, interrupt count, optional line-name and reserved-range bounds, and local pin/function enums. The `oneOf` state-node pattern supports both flat state nodes and grouped child pin nodes.

### State And Persistence
The YAML has no mutable state. DTS data persists the physical TLMM register resource, interrupt summary line, GPIO range, reserved GPIO ranges, and pinctrl states. At runtime the Qualcomm TLMM driver maps state labels into mux selection, drive strength, bias, input/output, and GPIO/IRQ domain behavior.

### Dependencies And Integration Points
Dependencies include `qcom,tlmm-common.yaml`, `pinctrl.yaml`, `pinmux-node.yaml`, `pincfg-node.yaml`, `/schemas/types.yaml`, and interrupt-controller dt-bindings used in examples. Integration points are SoC DTSI files, board DTS pin states, Linux pinctrl and GPIO consumers, and wakeup-parent IRQ controllers when declared.

### Risks
The biggest risk is drift between the schema pin/function enum and the driver pin/function tables; a missing enum blocks valid DTS, while an extra enum can allow states the driver cannot program. Pin count limits in regexes and `gpio-line-names` must match hardware. The broad grouped-state pattern can hide semantic mistakes unless examples cover both flat and nested layouts.

### Test Signals
Run `dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/pinctrl/qcom,msm8953-pinctrl.yaml` and compile representative SoC DTSI users. Negative tests should cover invalid GPIO numbers, unsupported functions, missing `reg`, missing GPIO/IRQ provider cells, and illegal extra properties. Runtime signals are TLMM probe, GPIO chip registration, IRQ domain creation, and successful pin state switching for UART, SPI/I2C, storage, and audio/display functions listed in the enum.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,msm8953-pinctrl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,msm8960-pinctrl.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,msm8960-pinctrl.yaml

### Purpose
`qcom,msm8960-pinctrl.yaml` describes the Qualcomm MSM8960 Top Level Mode Multiplexer controller. It binds the SoC-specific TLMM register block, GPIO and interrupt provider resources, and the legal pin/function names for pinctrl state nodes.

### Important Schema APIs
The binding provides compatible `qcom,msm8960-pinctrl`. Top-level required properties are `compatible`, `reg`. State nodes matching `-state$` can be direct objects or containers of `-pins` objects, and their `$defs` entry references `qcom,tlmm-common.yaml#/$defs/qcom-tlmm-state`. pin names constrained by `^gpio([0-9]|[1-9][0-9]|1[0-4][0-9]|15[0-1])$`. `function` is restricted to 104 local mux choices, starting with `gpio`, `audio_pcm`, `bt`, `cam_mclk0`, `cam_mclk1`, `cam_mclk2`, `codec_mic_i2s`, `codec_spkr_i2s`. The local schema setting is `unevaluatedProperties: false`. It also bounds `gpio-line-names` to the SoC GPIO count. `gpio-reserved-ranges` is available for pins owned by firmware or trusted applications.

### Validation Flow
Validation composes the common Qualcomm TLMM provider schema with this SoC-specific file. The common schema requires GPIO and interrupt provider properties, while this file restricts `compatible`, `reg`, interrupt count, optional line-name and reserved-range bounds, and local pin/function enums. The `oneOf` state-node pattern supports both flat state nodes and grouped child pin nodes.

### State And Persistence
The YAML has no mutable state. DTS data persists the physical TLMM register resource, interrupt summary line, GPIO range, reserved GPIO ranges, and pinctrl states. At runtime the Qualcomm TLMM driver maps state labels into mux selection, drive strength, bias, input/output, and GPIO/IRQ domain behavior.

### Dependencies And Integration Points
Dependencies include `qcom,tlmm-common.yaml`, `pinctrl.yaml`, `pinmux-node.yaml`, `pincfg-node.yaml`, `/schemas/types.yaml`, and interrupt-controller dt-bindings used in examples. Integration points are SoC DTSI files, board DTS pin states, Linux pinctrl and GPIO consumers, and wakeup-parent IRQ controllers when declared.

### Risks
The biggest risk is drift between the schema pin/function enum and the driver pin/function tables; a missing enum blocks valid DTS, while an extra enum can allow states the driver cannot program. Pin count limits in regexes and `gpio-line-names` must match hardware. The broad grouped-state pattern can hide semantic mistakes unless examples cover both flat and nested layouts.

### Test Signals
Run `dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/pinctrl/qcom,msm8960-pinctrl.yaml` and compile representative SoC DTSI users. Negative tests should cover invalid GPIO numbers, unsupported functions, missing `reg`, missing GPIO/IRQ provider cells, and illegal extra properties. Runtime signals are TLMM probe, GPIO chip registration, IRQ domain creation, and successful pin state switching for UART, SPI/I2C, storage, and audio/display functions listed in the enum.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,msm8960-pinctrl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,msm8974-pinctrl.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,msm8974-pinctrl.yaml

### Purpose
`qcom,msm8974-pinctrl.yaml` describes the Qualcomm MSM8974 Top Level Mode Multiplexer controller. It binds the SoC-specific TLMM register block, GPIO and interrupt provider resources, and the legal pin/function names for pinctrl state nodes.

### Important Schema APIs
The binding provides compatible `qcom,msm8974-pinctrl`. Top-level required properties are `compatible`, `reg`. State nodes matching `-state$` can be direct objects or containers of `-pins` objects, and their `$defs` entry references `qcom,tlmm-common.yaml#/$defs/qcom-tlmm-state`. pin names constrained by `^gpio([0-9]|[1-9][0-9]|1[0-3][0-9]|14[0-5])$`. `function` is restricted to 105 local mux choices, starting with `gpio`, `cci_i2c0`, `cci_i2c1`, `uim1`, `uim2`, `uim_batt_alarm`, `blsp_uim1`, `blsp_uart1`. The local schema setting is `unevaluatedProperties: false`. This file has an extra conditional for HSIC pads that disables generic bias, drive-strength, input, and output pinconf keys on `hsic_data` and `hsic_strobe` because those pins are not normal GPIO pads. It also bounds `gpio-line-names` to the SoC GPIO count. `gpio-reserved-ranges` is available for pins owned by firmware or trusted applications.

### Validation Flow
Validation composes the common Qualcomm TLMM provider schema with this SoC-specific file. The common schema requires GPIO and interrupt provider properties, while this file restricts `compatible`, `reg`, interrupt count, optional line-name and reserved-range bounds, and local pin/function enums. The `oneOf` state-node pattern supports both flat state nodes and grouped child pin nodes.

### State And Persistence
The YAML has no mutable state. DTS data persists the physical TLMM register resource, interrupt summary line, GPIO range, reserved GPIO ranges, and pinctrl states. At runtime the Qualcomm TLMM driver maps state labels into mux selection, drive strength, bias, input/output, and GPIO/IRQ domain behavior.

### Dependencies And Integration Points
Dependencies include `qcom,tlmm-common.yaml`, `pinctrl.yaml`, `pinmux-node.yaml`, `pincfg-node.yaml`, `/schemas/types.yaml`, and interrupt-controller dt-bindings used in examples. Integration points are SoC DTSI files, board DTS pin states, Linux pinctrl and GPIO consumers, and wakeup-parent IRQ controllers when declared.

### Risks
The biggest risk is drift between the schema pin/function enum and the driver pin/function tables; a missing enum blocks valid DTS, while an extra enum can allow states the driver cannot program. Pin count limits in regexes and `gpio-line-names` must match hardware. The broad grouped-state pattern can hide semantic mistakes unless examples cover both flat and nested layouts.

### Test Signals
Run `dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/pinctrl/qcom,msm8974-pinctrl.yaml` and compile representative SoC DTSI users. Negative tests should cover invalid GPIO numbers, unsupported functions, missing `reg`, missing GPIO/IRQ provider cells, and illegal extra properties. Runtime signals are TLMM probe, GPIO chip registration, IRQ domain creation, and successful pin state switching for UART, SPI/I2C, storage, and audio/display functions listed in the enum.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,msm8974-pinctrl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,msm8976-pinctrl.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,msm8976-pinctrl.yaml

### Purpose
`qcom,msm8976-pinctrl.yaml` describes the Qualcomm MSM8976 Top Level Mode Multiplexer controller. It binds the SoC-specific TLMM register block, GPIO and interrupt provider resources, and the legal pin/function names for pinctrl state nodes.

### Important Schema APIs
The binding provides compatible `qcom,msm8976-pinctrl`. Top-level required properties are `compatible`, `reg`. State nodes matching `-state$` can be direct objects or containers of `-pins` objects, and their `$defs` entry references `qcom,tlmm-common.yaml#/$defs/qcom-tlmm-state`. pin names constrained by `^gpio([0-9]|[1-9][0-9]|1[0-3][0-9]|14[0-4])$`. `function` is restricted to 95 local mux choices, starting with `gpio`, `blsp_uart1`, `blsp_spi1`, `smb_int`, `blsp_i2c1`, `blsp_spi2`, `blsp_uart2`, `blsp_i2c2`. The local schema setting is `unevaluatedProperties: false`. It also bounds `gpio-line-names` to the SoC GPIO count. `gpio-reserved-ranges` is available for pins owned by firmware or trusted applications.

### Validation Flow
Validation composes the common Qualcomm TLMM provider schema with this SoC-specific file. The common schema requires GPIO and interrupt provider properties, while this file restricts `compatible`, `reg`, interrupt count, optional line-name and reserved-range bounds, and local pin/function enums. The `oneOf` state-node pattern supports both flat state nodes and grouped child pin nodes.

### State And Persistence
The YAML has no mutable state. DTS data persists the physical TLMM register resource, interrupt summary line, GPIO range, reserved GPIO ranges, and pinctrl states. At runtime the Qualcomm TLMM driver maps state labels into mux selection, drive strength, bias, input/output, and GPIO/IRQ domain behavior.

### Dependencies And Integration Points
Dependencies include `qcom,tlmm-common.yaml`, `pinctrl.yaml`, `pinmux-node.yaml`, `pincfg-node.yaml`, `/schemas/types.yaml`, and interrupt-controller dt-bindings used in examples. Integration points are SoC DTSI files, board DTS pin states, Linux pinctrl and GPIO consumers, and wakeup-parent IRQ controllers when declared.

### Risks
The biggest risk is drift between the schema pin/function enum and the driver pin/function tables; a missing enum blocks valid DTS, while an extra enum can allow states the driver cannot program. Pin count limits in regexes and `gpio-line-names` must match hardware. The broad grouped-state pattern can hide semantic mistakes unless examples cover both flat and nested layouts.

### Test Signals
Run `dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/pinctrl/qcom,msm8976-pinctrl.yaml` and compile representative SoC DTSI users. Negative tests should cover invalid GPIO numbers, unsupported functions, missing `reg`, missing GPIO/IRQ provider cells, and illegal extra properties. Runtime signals are TLMM probe, GPIO chip registration, IRQ domain creation, and successful pin state switching for UART, SPI/I2C, storage, and audio/display functions listed in the enum.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,msm8976-pinctrl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,msm8994-pinctrl.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,msm8994-pinctrl.yaml

### Purpose
`qcom,msm8994-pinctrl.yaml` describes the Qualcomm MSM8994 Top Level Mode Multiplexer controller. It binds the SoC-specific TLMM register block, GPIO and interrupt provider resources, and the legal pin/function names for pinctrl state nodes.

### Important Schema APIs
The binding provides 2 compatible strings including `qcom,msm8992-pinctrl`, `qcom,msm8994-pinctrl`. Top-level required properties are `compatible`, `reg`. State nodes matching `-state$` can be direct objects or containers of `-pins` objects, and their `$defs` entry references `qcom,tlmm-common.yaml#/$defs/qcom-tlmm-state`. pin names constrained by `^gpio([0-9]|[1-9][0-9]|1[0-3][0-9]|14[0-5])$`. `function` is restricted to 129 local mux choices, starting with `gpio`, `audio_ref_clk`, `blsp_i2c1`, `blsp_i2c2`, `blsp_i2c3`, `blsp_i2c4`, `blsp_i2c5`, `blsp_i2c6`. The local schema setting is `unevaluatedProperties: false`. It also bounds `gpio-line-names` to the SoC GPIO count. `gpio-reserved-ranges` is available for pins owned by firmware or trusted applications.

### Validation Flow
Validation composes the common Qualcomm TLMM provider schema with this SoC-specific file. The common schema requires GPIO and interrupt provider properties, while this file restricts `compatible`, `reg`, interrupt count, optional line-name and reserved-range bounds, and local pin/function enums. The `oneOf` state-node pattern supports both flat state nodes and grouped child pin nodes.

### State And Persistence
The YAML has no mutable state. DTS data persists the physical TLMM register resource, interrupt summary line, GPIO range, reserved GPIO ranges, and pinctrl states. At runtime the Qualcomm TLMM driver maps state labels into mux selection, drive strength, bias, input/output, and GPIO/IRQ domain behavior.

### Dependencies And Integration Points
Dependencies include `qcom,tlmm-common.yaml`, `pinctrl.yaml`, `pinmux-node.yaml`, `pincfg-node.yaml`, `/schemas/types.yaml`, and interrupt-controller dt-bindings used in examples. Integration points are SoC DTSI files, board DTS pin states, Linux pinctrl and GPIO consumers, and wakeup-parent IRQ controllers when declared.

### Risks
The biggest risk is drift between the schema pin/function enum and the driver pin/function tables; a missing enum blocks valid DTS, while an extra enum can allow states the driver cannot program. Pin count limits in regexes and `gpio-line-names` must match hardware. The broad grouped-state pattern can hide semantic mistakes unless examples cover both flat and nested layouts.

### Test Signals
Run `dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/pinctrl/qcom,msm8994-pinctrl.yaml` and compile representative SoC DTSI users. Negative tests should cover invalid GPIO numbers, unsupported functions, missing `reg`, missing GPIO/IRQ provider cells, and illegal extra properties. Runtime signals are TLMM probe, GPIO chip registration, IRQ domain creation, and successful pin state switching for UART, SPI/I2C, storage, and audio/display functions listed in the enum.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,msm8994-pinctrl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,msm8996-pinctrl.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,msm8996-pinctrl.yaml

### Purpose
`qcom,msm8996-pinctrl.yaml` describes the Qualcomm MSM8996 Top Level Mode Multiplexer controller. It binds the SoC-specific TLMM register block, GPIO and interrupt provider resources, and the legal pin/function names for pinctrl state nodes.

### Important Schema APIs
The binding provides compatible `qcom,msm8996-pinctrl`. Top-level required properties are `compatible`, `reg`. State nodes matching `-state$` can be direct objects or containers of `-pins` objects, and their `$defs` entry references `qcom,tlmm-common.yaml#/$defs/qcom-tlmm-state`. pin names constrained by `^gpio([0-9]|[1-9][0-9]|1[0-4][0-9])$`. `function` is restricted to 243 local mux choices, starting with `gpio`, `blsp_uart1`, `blsp_spi1`, `blsp_i2c1`, `blsp_uim1`, `atest_tsens`, `bimc_dte1`, `dac_calib0`. The local schema setting is `unevaluatedProperties: false`. It also bounds `gpio-line-names` to the SoC GPIO count. `gpio-reserved-ranges` is available for pins owned by firmware or trusted applications.

### Validation Flow
Validation composes the common Qualcomm TLMM provider schema with this SoC-specific file. The common schema requires GPIO and interrupt provider properties, while this file restricts `compatible`, `reg`, interrupt count, optional line-name and reserved-range bounds, and local pin/function enums. The `oneOf` state-node pattern supports both flat state nodes and grouped child pin nodes.

### State And Persistence
The YAML has no mutable state. DTS data persists the physical TLMM register resource, interrupt summary line, GPIO range, reserved GPIO ranges, and pinctrl states. At runtime the Qualcomm TLMM driver maps state labels into mux selection, drive strength, bias, input/output, and GPIO/IRQ domain behavior.

### Dependencies And Integration Points
Dependencies include `qcom,tlmm-common.yaml`, `pinctrl.yaml`, `pinmux-node.yaml`, `pincfg-node.yaml`, `/schemas/types.yaml`, and interrupt-controller dt-bindings used in examples. Integration points are SoC DTSI files, board DTS pin states, Linux pinctrl and GPIO consumers, and wakeup-parent IRQ controllers when declared.

### Risks
The biggest risk is drift between the schema pin/function enum and the driver pin/function tables; a missing enum blocks valid DTS, while an extra enum can allow states the driver cannot program. Pin count limits in regexes and `gpio-line-names` must match hardware. The broad grouped-state pattern can hide semantic mistakes unless examples cover both flat and nested layouts.

### Test Signals
Run `dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/pinctrl/qcom,msm8996-pinctrl.yaml` and compile representative SoC DTSI users. Negative tests should cover invalid GPIO numbers, unsupported functions, missing `reg`, missing GPIO/IRQ provider cells, and illegal extra properties. Runtime signals are TLMM probe, GPIO chip registration, IRQ domain creation, and successful pin state switching for UART, SPI/I2C, storage, and audio/display functions listed in the enum.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,msm8996-pinctrl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,msm8998-pinctrl.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,msm8998-pinctrl.yaml

### Purpose
`qcom,msm8998-pinctrl.yaml` describes the Qualcomm MSM8998 Top Level Mode Multiplexer controller. It binds the SoC-specific TLMM register block, GPIO and interrupt provider resources, and the legal pin/function names for pinctrl state nodes.

### Important Schema APIs
The binding provides compatible `qcom,msm8998-pinctrl`. Top-level required properties are `compatible`, `reg`. State nodes matching `-state$` can be direct objects or containers of `-pins` objects, and their `$defs` entry references `qcom,tlmm-common.yaml#/$defs/qcom-tlmm-state`. pin names constrained by `^gpio([0-9]|[1-9][0-9]|1[0-4][0-9])$`. `function` is restricted to 176 local mux choices, starting with `gpio`, `adsp_ext`, `agera_pll`, `atest_char`, `atest_gpsadc0`, `atest_gpsadc1`, `atest_tsens`, `atest_tsens2`. The local schema setting is `unevaluatedProperties: false`. It also bounds `gpio-line-names` to the SoC GPIO count. `gpio-reserved-ranges` is available for pins owned by firmware or trusted applications.

### Validation Flow
Validation composes the common Qualcomm TLMM provider schema with this SoC-specific file. The common schema requires GPIO and interrupt provider properties, while this file restricts `compatible`, `reg`, interrupt count, optional line-name and reserved-range bounds, and local pin/function enums. The `oneOf` state-node pattern supports both flat state nodes and grouped child pin nodes.

### State And Persistence
The YAML has no mutable state. DTS data persists the physical TLMM register resource, interrupt summary line, GPIO range, reserved GPIO ranges, and pinctrl states. At runtime the Qualcomm TLMM driver maps state labels into mux selection, drive strength, bias, input/output, and GPIO/IRQ domain behavior.

### Dependencies And Integration Points
Dependencies include `qcom,tlmm-common.yaml`, `pinctrl.yaml`, `pinmux-node.yaml`, `pincfg-node.yaml`, `/schemas/types.yaml`, and interrupt-controller dt-bindings used in examples. Integration points are SoC DTSI files, board DTS pin states, Linux pinctrl and GPIO consumers, and wakeup-parent IRQ controllers when declared.

### Risks
The biggest risk is drift between the schema pin/function enum and the driver pin/function tables; a missing enum blocks valid DTS, while an extra enum can allow states the driver cannot program. Pin count limits in regexes and `gpio-line-names` must match hardware. The broad grouped-state pattern can hide semantic mistakes unless examples cover both flat and nested layouts.

### Test Signals
Run `dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/pinctrl/qcom,msm8998-pinctrl.yaml` and compile representative SoC DTSI users. Negative tests should cover invalid GPIO numbers, unsupported functions, missing `reg`, missing GPIO/IRQ provider cells, and illegal extra properties. Runtime signals are TLMM probe, GPIO chip registration, IRQ domain creation, and successful pin state switching for UART, SPI/I2C, storage, and audio/display functions listed in the enum.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,msm8998-pinctrl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,pmic-gpio.yaml -->
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

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,pmic-gpio.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,pmic-mpp.yaml -->
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

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,pmic-mpp.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,qcm2290-tlmm.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,qcm2290-tlmm.yaml

### Purpose
`qcom,qcm2290-tlmm.yaml` describes the Qualcomm QCM2290 Top Level Mode Multiplexer controller. It binds the SoC-specific TLMM register block, GPIO and interrupt provider resources, and the legal pin/function names for pinctrl state nodes.

### Important Schema APIs
The binding provides compatible `qcom,qcm2290-tlmm`. Top-level required properties are `compatible`, `reg`. State nodes matching `-state$` can be direct objects or containers of `-pins` objects, and their `$defs` entry references `qcom,tlmm-common.yaml#/$defs/qcom-tlmm-state`. pin names constrained by `^gpio([0-9]|[1-9][0-9]|1[0-1][0-9]|12[0-6])$`. `function` is restricted to 101 local mux choices, starting with `adsp_ext`, `agera_pll`, `atest`, `cam_mclk`, `cci_async`, `cci_i2c`, `cci_timer0`, `cci_timer1`. The local schema setting is `unevaluatedProperties: false`.

### Validation Flow
Validation composes the common Qualcomm TLMM provider schema with this SoC-specific file. The common schema requires GPIO and interrupt provider properties, while this file restricts `compatible`, `reg`, interrupt count, optional line-name and reserved-range bounds, and local pin/function enums. The `oneOf` state-node pattern supports both flat state nodes and grouped child pin nodes.

### State And Persistence
The YAML has no mutable state. DTS data persists the physical TLMM register resource, interrupt summary line, GPIO range, reserved GPIO ranges, and pinctrl states. At runtime the Qualcomm TLMM driver maps state labels into mux selection, drive strength, bias, input/output, and GPIO/IRQ domain behavior.

### Dependencies And Integration Points
Dependencies include `qcom,tlmm-common.yaml`, `pinctrl.yaml`, `pinmux-node.yaml`, `pincfg-node.yaml`, `/schemas/types.yaml`, and interrupt-controller dt-bindings used in examples. Integration points are SoC DTSI files, board DTS pin states, Linux pinctrl and GPIO consumers, and wakeup-parent IRQ controllers when declared.

### Risks
The biggest risk is drift between the schema pin/function enum and the driver pin/function tables; a missing enum blocks valid DTS, while an extra enum can allow states the driver cannot program. Pin count limits in regexes and `gpio-line-names` must match hardware. The broad grouped-state pattern can hide semantic mistakes unless examples cover both flat and nested layouts.

### Test Signals
Run `dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/pinctrl/qcom,qcm2290-tlmm.yaml` and compile representative SoC DTSI users. Negative tests should cover invalid GPIO numbers, unsupported functions, missing `reg`, missing GPIO/IRQ provider cells, and illegal extra properties. Runtime signals are TLMM probe, GPIO chip registration, IRQ domain creation, and successful pin state switching for UART, SPI/I2C, storage, and audio/display functions listed in the enum.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,qcm2290-tlmm.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,qcs404-pinctrl.yaml -->
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

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,qcs404-pinctrl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,qcs615-tlmm.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,qcs615-tlmm.yaml

### Purpose
`qcom,qcs615-tlmm.yaml` describes the Qualcomm QCS615 Top Level Mode Multiplexer controller. It binds the SoC-specific TLMM register block, GPIO and interrupt provider resources, and the legal pin/function names for pinctrl state nodes.

### Important Schema APIs
The binding provides compatible `qcom,qcs615-tlmm`. Top-level required properties are `compatible`, `reg`, `reg-names`. State nodes matching `-state$` can be direct objects or containers of `-pins` objects, and their `$defs` entry references `qcom,tlmm-common.yaml#/$defs/qcom-tlmm-state`. pin names constrained by `^gpio([0-9]|[1-9][0-9]|1[0-1][0-9]|12[0-2])$`. `function` is restricted to 75 local mux choices, starting with `gpio`, `adsp_ext`, `agera_pll`, `aoss_cti`, `atest_char`, `atest_tsens`, `atest_usb`, `cam_mclk`. The local schema setting is `unevaluatedProperties: false`. It also bounds `gpio-line-names` to the SoC GPIO count. `gpio-reserved-ranges` is available for pins owned by firmware or trusted applications.

### Validation Flow
Validation composes the common Qualcomm TLMM provider schema with this SoC-specific file. The common schema requires GPIO and interrupt provider properties, while this file restricts `compatible`, `reg`, interrupt count, optional line-name and reserved-range bounds, and local pin/function enums. The `oneOf` state-node pattern supports both flat state nodes and grouped child pin nodes.

### State And Persistence
The YAML has no mutable state. DTS data persists the physical TLMM register resource, interrupt summary line, GPIO range, reserved GPIO ranges, and pinctrl states. At runtime the Qualcomm TLMM driver maps state labels into mux selection, drive strength, bias, input/output, and GPIO/IRQ domain behavior.

### Dependencies And Integration Points
Dependencies include `qcom,tlmm-common.yaml`, `pinctrl.yaml`, `pinmux-node.yaml`, `pincfg-node.yaml`, `/schemas/types.yaml`, and interrupt-controller dt-bindings used in examples. Integration points are SoC DTSI files, board DTS pin states, Linux pinctrl and GPIO consumers, and wakeup-parent IRQ controllers when declared.

### Risks
The biggest risk is drift between the schema pin/function enum and the driver pin/function tables; a missing enum blocks valid DTS, while an extra enum can allow states the driver cannot program. Pin count limits in regexes and `gpio-line-names` must match hardware. The broad grouped-state pattern can hide semantic mistakes unless examples cover both flat and nested layouts.

### Test Signals
Run `dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/pinctrl/qcom,qcs615-tlmm.yaml` and compile representative SoC DTSI users. Negative tests should cover invalid GPIO numbers, unsupported functions, missing `reg`, missing GPIO/IRQ provider cells, and illegal extra properties. Runtime signals are TLMM probe, GPIO chip registration, IRQ domain creation, and successful pin state switching for UART, SPI/I2C, storage, and audio/display functions listed in the enum.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,qcs615-tlmm.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,qcs8300-tlmm.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,qcs8300-tlmm.yaml

### Purpose
`qcom,qcs8300-tlmm.yaml` describes the Qualcomm QCS8300 Top Level Mode Multiplexer controller. It binds the SoC-specific TLMM register block, GPIO and interrupt provider resources, and the legal pin/function names for pinctrl state nodes.

### Important Schema APIs
The binding provides compatible `qcom,qcs8300-tlmm`. Top-level required properties are `compatible`, `reg`. State nodes matching `-state$` can be direct objects or containers of `-pins` objects, and their `$defs` entry references `qcom,tlmm-common.yaml#/$defs/qcom-tlmm-state`. pin names constrained by `^gpio([0-9]|[1-9][0-9]|1[0-2][0-9]|13[0-2])$`. `function` is restricted to 98 local mux choices, starting with `aoss_cti`, `atest_char`, `atest_usb2`, `audio_ref`, `cam_mclk`, `cci_async`, `cci_i2c_scl`, `cci_i2c_sda`. The local schema setting is `unevaluatedProperties: false`. It also bounds `gpio-line-names` to the SoC GPIO count. `gpio-reserved-ranges` is available for pins owned by firmware or trusted applications.

### Validation Flow
Validation composes the common Qualcomm TLMM provider schema with this SoC-specific file. The common schema requires GPIO and interrupt provider properties, while this file restricts `compatible`, `reg`, interrupt count, optional line-name and reserved-range bounds, and local pin/function enums. The `oneOf` state-node pattern supports both flat state nodes and grouped child pin nodes.

### State And Persistence
The YAML has no mutable state. DTS data persists the physical TLMM register resource, interrupt summary line, GPIO range, reserved GPIO ranges, and pinctrl states. At runtime the Qualcomm TLMM driver maps state labels into mux selection, drive strength, bias, input/output, and GPIO/IRQ domain behavior.

### Dependencies And Integration Points
Dependencies include `qcom,tlmm-common.yaml`, `pinctrl.yaml`, `pinmux-node.yaml`, `pincfg-node.yaml`, `/schemas/types.yaml`, and interrupt-controller dt-bindings used in examples. Integration points are SoC DTSI files, board DTS pin states, Linux pinctrl and GPIO consumers, and wakeup-parent IRQ controllers when declared.

### Risks
The biggest risk is drift between the schema pin/function enum and the driver pin/function tables; a missing enum blocks valid DTS, while an extra enum can allow states the driver cannot program. Pin count limits in regexes and `gpio-line-names` must match hardware. The broad grouped-state pattern can hide semantic mistakes unless examples cover both flat and nested layouts.

### Test Signals
Run `dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/pinctrl/qcom,qcs8300-tlmm.yaml` and compile representative SoC DTSI users. Negative tests should cover invalid GPIO numbers, unsupported functions, missing `reg`, missing GPIO/IRQ provider cells, and illegal extra properties. Runtime signals are TLMM probe, GPIO chip registration, IRQ domain creation, and successful pin state switching for UART, SPI/I2C, storage, and audio/display functions listed in the enum.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,qcs8300-tlmm.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,qdu1000-tlmm.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,qdu1000-tlmm.yaml

### Purpose
`qcom,qdu1000-tlmm.yaml` describes the Qualcomm QDU1000 Top Level Mode Multiplexer controller. It binds the SoC-specific TLMM register block, GPIO and interrupt provider resources, and the legal pin/function names for pinctrl state nodes.

### Important Schema APIs
The binding provides compatible `qcom,qdu1000-tlmm`. Top-level required properties are `compatible`, `reg`. State nodes matching `-state$` can be direct objects or containers of `-pins` objects, and their `$defs` entry references `qcom,tlmm-common.yaml#/$defs/qcom-tlmm-state`. pin names constrained by `^gpio([0-9]|[1-9][0-9]|1[0-4][0-9]|150)$`. `function` is restricted to 108 local mux choices, starting with `atest_char`, `atest_usb`, `char_exec`, `CMO_PRI`, `cmu_rng`, `dbg_out_clk`, `ddr_bist`, `ddr_pxi1`. The local schema setting is `unevaluatedProperties: false`. It also bounds `gpio-line-names` to the SoC GPIO count. `gpio-reserved-ranges` is available for pins owned by firmware or trusted applications.

### Validation Flow
Validation composes the common Qualcomm TLMM provider schema with this SoC-specific file. The common schema requires GPIO and interrupt provider properties, while this file restricts `compatible`, `reg`, interrupt count, optional line-name and reserved-range bounds, and local pin/function enums. The `oneOf` state-node pattern supports both flat state nodes and grouped child pin nodes.

### State And Persistence
The YAML has no mutable state. DTS data persists the physical TLMM register resource, interrupt summary line, GPIO range, reserved GPIO ranges, and pinctrl states. At runtime the Qualcomm TLMM driver maps state labels into mux selection, drive strength, bias, input/output, and GPIO/IRQ domain behavior.

### Dependencies And Integration Points
Dependencies include `qcom,tlmm-common.yaml`, `pinctrl.yaml`, `pinmux-node.yaml`, `pincfg-node.yaml`, `/schemas/types.yaml`, and interrupt-controller dt-bindings used in examples. Integration points are SoC DTSI files, board DTS pin states, Linux pinctrl and GPIO consumers, and wakeup-parent IRQ controllers when declared.

### Risks
The biggest risk is drift between the schema pin/function enum and the driver pin/function tables; a missing enum blocks valid DTS, while an extra enum can allow states the driver cannot program. Pin count limits in regexes and `gpio-line-names` must match hardware. The broad grouped-state pattern can hide semantic mistakes unless examples cover both flat and nested layouts.

### Test Signals
Run `dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/pinctrl/qcom,qdu1000-tlmm.yaml` and compile representative SoC DTSI users. Negative tests should cover invalid GPIO numbers, unsupported functions, missing `reg`, missing GPIO/IRQ provider cells, and illegal extra properties. Runtime signals are TLMM probe, GPIO chip registration, IRQ domain creation, and successful pin state switching for UART, SPI/I2C, storage, and audio/display functions listed in the enum.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,qdu1000-tlmm.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,sa8775p-tlmm.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,sa8775p-tlmm.yaml

### Purpose
`qcom,sa8775p-tlmm.yaml` describes the Qualcomm SA8775P Top Level Mode Multiplexer controller. It binds the SoC-specific TLMM register block, GPIO and interrupt provider resources, and the legal pin/function names for pinctrl state nodes.

### Important Schema APIs
The binding provides compatible `qcom,sa8255p-tlmm`. Top-level required properties are `compatible`, `reg`. State nodes matching `-state$` can be direct objects or containers of `-pins` objects, and their `$defs` entry references `qcom,tlmm-common.yaml#/$defs/qcom-tlmm-state`. pin names constrained by `^gpio([0-9]|[1-9][0-9]|1[0-3][0-9]|14[0-7])$`. `function` is restricted to 141 local mux choices, starting with `atest_char`, `atest_usb2`, `audio_ref`, `cam_mclk`, `cci_async`, `cci_i2c`, `cci_timer0`, `cci_timer1`. The local schema setting is `unevaluatedProperties: false`. It also bounds `gpio-line-names` to the SoC GPIO count. `gpio-reserved-ranges` is available for pins owned by firmware or trusted applications.

### Validation Flow
Validation composes the common Qualcomm TLMM provider schema with this SoC-specific file. The common schema requires GPIO and interrupt provider properties, while this file restricts `compatible`, `reg`, interrupt count, optional line-name and reserved-range bounds, and local pin/function enums. The `oneOf` state-node pattern supports both flat state nodes and grouped child pin nodes.

### State And Persistence
The YAML has no mutable state. DTS data persists the physical TLMM register resource, interrupt summary line, GPIO range, reserved GPIO ranges, and pinctrl states. At runtime the Qualcomm TLMM driver maps state labels into mux selection, drive strength, bias, input/output, and GPIO/IRQ domain behavior.

### Dependencies And Integration Points
Dependencies include `qcom,tlmm-common.yaml`, `pinctrl.yaml`, `pinmux-node.yaml`, `pincfg-node.yaml`, `/schemas/types.yaml`, and interrupt-controller dt-bindings used in examples. Integration points are SoC DTSI files, board DTS pin states, Linux pinctrl and GPIO consumers, and wakeup-parent IRQ controllers when declared.

### Risks
The biggest risk is drift between the schema pin/function enum and the driver pin/function tables; a missing enum blocks valid DTS, while an extra enum can allow states the driver cannot program. Pin count limits in regexes and `gpio-line-names` must match hardware. The broad grouped-state pattern can hide semantic mistakes unless examples cover both flat and nested layouts.

### Test Signals
Run `dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/pinctrl/qcom,sa8775p-tlmm.yaml` and compile representative SoC DTSI users. Negative tests should cover invalid GPIO numbers, unsupported functions, missing `reg`, missing GPIO/IRQ provider cells, and illegal extra properties. Runtime signals are TLMM probe, GPIO chip registration, IRQ domain creation, and successful pin state switching for UART, SPI/I2C, storage, and audio/display functions listed in the enum.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,sa8775p-tlmm.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,sar2130p-tlmm.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,sar2130p-tlmm.yaml

### Purpose
`qcom,sar2130p-tlmm.yaml` describes the Qualcomm SAR2130P Top Level Mode Multiplexer controller. It binds the SoC-specific TLMM register block, GPIO and interrupt provider resources, and the legal pin/function names for pinctrl state nodes.

### Important Schema APIs
The binding provides compatible `qcom,sar2130p-tlmm`. Top-level required properties are `compatible`, `reg`. State nodes matching `-state$` can be direct objects or containers of `-pins` objects, and their `$defs` entry references `qcom,tlmm-common.yaml#/$defs/qcom-tlmm-state`. pin names constrained by `^gpio([0-9]|[1-9][0-9]|1[0-4][0-9]|15[0-5])$`. `function` is restricted to 138 local mux choices, starting with `aoss_cti`, `atest_char`, `atest_char0`, `atest_char1`, `atest_char2`, `atest_char3`, `atest_usb0`, `atest_usb00`. The local schema setting is `unevaluatedProperties: false`. It also bounds `gpio-line-names` to the SoC GPIO count. `gpio-reserved-ranges` is available for pins owned by firmware or trusted applications.

### Validation Flow
Validation composes the common Qualcomm TLMM provider schema with this SoC-specific file. The common schema requires GPIO and interrupt provider properties, while this file restricts `compatible`, `reg`, interrupt count, optional line-name and reserved-range bounds, and local pin/function enums. The `oneOf` state-node pattern supports both flat state nodes and grouped child pin nodes.

### State And Persistence
The YAML has no mutable state. DTS data persists the physical TLMM register resource, interrupt summary line, GPIO range, reserved GPIO ranges, and pinctrl states. At runtime the Qualcomm TLMM driver maps state labels into mux selection, drive strength, bias, input/output, and GPIO/IRQ domain behavior.

### Dependencies And Integration Points
Dependencies include `qcom,tlmm-common.yaml`, `pinctrl.yaml`, `pinmux-node.yaml`, `pincfg-node.yaml`, `/schemas/types.yaml`, and interrupt-controller dt-bindings used in examples. Integration points are SoC DTSI files, board DTS pin states, Linux pinctrl and GPIO consumers, and wakeup-parent IRQ controllers when declared.

### Risks
The biggest risk is drift between the schema pin/function enum and the driver pin/function tables; a missing enum blocks valid DTS, while an extra enum can allow states the driver cannot program. Pin count limits in regexes and `gpio-line-names` must match hardware. The broad grouped-state pattern can hide semantic mistakes unless examples cover both flat and nested layouts.

### Test Signals
Run `dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/pinctrl/qcom,sar2130p-tlmm.yaml` and compile representative SoC DTSI users. Negative tests should cover invalid GPIO numbers, unsupported functions, missing `reg`, missing GPIO/IRQ provider cells, and illegal extra properties. Runtime signals are TLMM probe, GPIO chip registration, IRQ domain creation, and successful pin state switching for UART, SPI/I2C, storage, and audio/display functions listed in the enum.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,sar2130p-tlmm.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,sc7180-pinctrl.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,sc7180-pinctrl.yaml

### Purpose
`qcom,sc7180-pinctrl.yaml` describes the Qualcomm SC7180 Top Level Mode Multiplexer controller. It binds the SoC-specific TLMM register block, GPIO and interrupt provider resources, and the legal pin/function names for pinctrl state nodes.

### Important Schema APIs
The binding provides compatible `qcom,sc7180-pinctrl`. Top-level required properties are `compatible`, `reg`, `reg-names`. State nodes matching `-state$` can be direct objects or containers of `-pins` objects, and their `$defs` entry references `qcom,tlmm-common.yaml#/$defs/qcom-tlmm-state`. pin names constrained by `^gpio([0-9]|[1-9][0-9]|10[0-9]|11[0-8])$`. `function` is restricted to 113 local mux choices, starting with `adsp_ext`, `agera_pll`, `aoss_cti`, `atest_char`, `atest_char0`, `atest_char1`, `atest_char2`, `atest_char3`. The local schema setting is `unevaluatedProperties: false`. It also bounds `gpio-line-names` to the SoC GPIO count. `gpio-reserved-ranges` is available for pins owned by firmware or trusted applications.

### Validation Flow
Validation composes the common Qualcomm TLMM provider schema with this SoC-specific file. The common schema requires GPIO and interrupt provider properties, while this file restricts `compatible`, `reg`, interrupt count, optional line-name and reserved-range bounds, and local pin/function enums. The `oneOf` state-node pattern supports both flat state nodes and grouped child pin nodes.

### State And Persistence
The YAML has no mutable state. DTS data persists the physical TLMM register resource, interrupt summary line, GPIO range, reserved GPIO ranges, and pinctrl states. At runtime the Qualcomm TLMM driver maps state labels into mux selection, drive strength, bias, input/output, and GPIO/IRQ domain behavior.

### Dependencies And Integration Points
Dependencies include `qcom,tlmm-common.yaml`, `pinctrl.yaml`, `pinmux-node.yaml`, `pincfg-node.yaml`, `/schemas/types.yaml`, and interrupt-controller dt-bindings used in examples. Integration points are SoC DTSI files, board DTS pin states, Linux pinctrl and GPIO consumers, and wakeup-parent IRQ controllers when declared.

### Risks
The biggest risk is drift between the schema pin/function enum and the driver pin/function tables; a missing enum blocks valid DTS, while an extra enum can allow states the driver cannot program. Pin count limits in regexes and `gpio-line-names` must match hardware. The broad grouped-state pattern can hide semantic mistakes unless examples cover both flat and nested layouts.

### Test Signals
Run `dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/pinctrl/qcom,sc7180-pinctrl.yaml` and compile representative SoC DTSI users. Negative tests should cover invalid GPIO numbers, unsupported functions, missing `reg`, missing GPIO/IRQ provider cells, and illegal extra properties. Runtime signals are TLMM probe, GPIO chip registration, IRQ domain creation, and successful pin state switching for UART, SPI/I2C, storage, and audio/display functions listed in the enum.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,sc7180-pinctrl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,sc7280-lpass-lpi-pinctrl.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,sc7280-lpass-lpi-pinctrl.yaml

### Purpose
`qcom,sc7280-lpass-lpi-pinctrl.yaml` describes the Qualcomm SC7280 LPASS LPI TLMM pin controller. It specializes the common LPASS LPI schema with this SoC's compatible string, register layout, GPIO pin range, and audio-oriented mux function list.

### Important Schema APIs
The binding provides compatible `qcom,sc7280-lpass-lpi-pinctrl`. Top-level required properties are `compatible`, `reg`. The controller also requires clock handles and `clock-names` where the file declares LPASS vote clocks. State nodes matching `-state$` can either be direct state objects or containers of `-pins` objects. They reference `qcom,lpass-lpi-common.yaml#/$defs/qcom-tlmm-state`, so each state requires `pins` and `function` and may set LPASS drive strength, slew rate, bias, input, and output properties. pin names constrained by `^gpio([0-9]|1[0-4])$`. `function` is restricted to 22 local mux choices, starting with `gpio`, `swr_tx_clk`, `qua_mi2s_sclk`, `swr_tx_data`, `qua_mi2s_ws`, `qua_mi2s_data`, `swr_rx_clk`, `swr_rx_data`.

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

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,sc7280-lpass-lpi-pinctrl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,sc7280-pinctrl.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,sc7280-pinctrl.yaml

### Purpose
`qcom,sc7280-pinctrl.yaml` describes the Qualcomm SC7280 Top Level Mode Multiplexer controller. It binds the SoC-specific TLMM register block, GPIO and interrupt provider resources, and the legal pin/function names for pinctrl state nodes.

### Important Schema APIs
The binding provides compatible `qcom,sc7280-pinctrl`. Top-level required properties are `compatible`, `reg`. State nodes matching `-state$` can be direct objects or containers of `-pins` objects, and their `$defs` entry references `qcom,tlmm-common.yaml#/$defs/qcom-tlmm-state`. pin names constrained by `^gpio([0-9]|[1-9][0-9]|1[0-6][0-9]|17[0-4])$`. `function` is restricted to 146 local mux choices, starting with `atest_char`, `atest_char0`, `atest_char1`, `atest_char2`, `atest_char3`, `atest_usb0`, `atest_usb00`, `atest_usb01`. The local schema setting is `unevaluatedProperties: false`. It also bounds `gpio-line-names` to the SoC GPIO count. `gpio-reserved-ranges` is available for pins owned by firmware or trusted applications.

### Validation Flow
Validation composes the common Qualcomm TLMM provider schema with this SoC-specific file. The common schema requires GPIO and interrupt provider properties, while this file restricts `compatible`, `reg`, interrupt count, optional line-name and reserved-range bounds, and local pin/function enums. The `oneOf` state-node pattern supports both flat state nodes and grouped child pin nodes.

### State And Persistence
The YAML has no mutable state. DTS data persists the physical TLMM register resource, interrupt summary line, GPIO range, reserved GPIO ranges, and pinctrl states. At runtime the Qualcomm TLMM driver maps state labels into mux selection, drive strength, bias, input/output, and GPIO/IRQ domain behavior.

### Dependencies And Integration Points
Dependencies include `qcom,tlmm-common.yaml`, `pinctrl.yaml`, `pinmux-node.yaml`, `pincfg-node.yaml`, `/schemas/types.yaml`, and interrupt-controller dt-bindings used in examples. Integration points are SoC DTSI files, board DTS pin states, Linux pinctrl and GPIO consumers, and wakeup-parent IRQ controllers when declared.

### Risks
The biggest risk is drift between the schema pin/function enum and the driver pin/function tables; a missing enum blocks valid DTS, while an extra enum can allow states the driver cannot program. Pin count limits in regexes and `gpio-line-names` must match hardware. The broad grouped-state pattern can hide semantic mistakes unless examples cover both flat and nested layouts.

### Test Signals
Run `dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/pinctrl/qcom,sc7280-pinctrl.yaml` and compile representative SoC DTSI users. Negative tests should cover invalid GPIO numbers, unsupported functions, missing `reg`, missing GPIO/IRQ provider cells, and illegal extra properties. Runtime signals are TLMM probe, GPIO chip registration, IRQ domain creation, and successful pin state switching for UART, SPI/I2C, storage, and audio/display functions listed in the enum.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,sc7280-pinctrl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,sc8180x-tlmm.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,sc8180x-tlmm.yaml

### Purpose
`qcom,sc8180x-tlmm.yaml` describes the Qualcomm SC8180X Top Level Mode Multiplexer controller. It binds the SoC-specific TLMM register block, GPIO and interrupt provider resources, and the legal pin/function names for pinctrl state nodes.

### Important Schema APIs
The binding provides compatible `qcom,sc8180x-tlmm`. Top-level required properties are `compatible`, `reg`, `reg-names`. State nodes matching `-state$` can be direct objects or containers of `-pins` objects, and their `$defs` entry references `qcom,tlmm-common.yaml#/$defs/qcom-tlmm-state`. pin names constrained by `^gpio([0-9]|[1-9][0-9]|1[0-8][0-9])$`. `function` is restricted to 129 local mux choices, starting with `adsp_ext`, `agera_pll`, `aoss_cti`, `atest_char`, `atest_tsens`, `atest_tsens2`, `atest_usb0`, `atest_usb1`. The local schema setting is `unevaluatedProperties: false`. `gpio-reserved-ranges` is available for pins owned by firmware or trusted applications.

### Validation Flow
Validation composes the common Qualcomm TLMM provider schema with this SoC-specific file. The common schema requires GPIO and interrupt provider properties, while this file restricts `compatible`, `reg`, interrupt count, optional line-name and reserved-range bounds, and local pin/function enums. The `oneOf` state-node pattern supports both flat state nodes and grouped child pin nodes.

### State And Persistence
The YAML has no mutable state. DTS data persists the physical TLMM register resource, interrupt summary line, GPIO range, reserved GPIO ranges, and pinctrl states. At runtime the Qualcomm TLMM driver maps state labels into mux selection, drive strength, bias, input/output, and GPIO/IRQ domain behavior.

### Dependencies And Integration Points
Dependencies include `qcom,tlmm-common.yaml`, `pinctrl.yaml`, `pinmux-node.yaml`, `pincfg-node.yaml`, `/schemas/types.yaml`, and interrupt-controller dt-bindings used in examples. Integration points are SoC DTSI files, board DTS pin states, Linux pinctrl and GPIO consumers, and wakeup-parent IRQ controllers when declared.

### Risks
The biggest risk is drift between the schema pin/function enum and the driver pin/function tables; a missing enum blocks valid DTS, while an extra enum can allow states the driver cannot program. Pin count limits in regexes and `gpio-line-names` must match hardware. The broad grouped-state pattern can hide semantic mistakes unless examples cover both flat and nested layouts.

### Test Signals
Run `dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/pinctrl/qcom,sc8180x-tlmm.yaml` and compile representative SoC DTSI users. Negative tests should cover invalid GPIO numbers, unsupported functions, missing `reg`, missing GPIO/IRQ provider cells, and illegal extra properties. Runtime signals are TLMM probe, GPIO chip registration, IRQ domain creation, and successful pin state switching for UART, SPI/I2C, storage, and audio/display functions listed in the enum.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,sc8180x-tlmm.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,sc8280xp-lpass-lpi-pinctrl.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,sc8280xp-lpass-lpi-pinctrl.yaml

### Purpose
`qcom,sc8280xp-lpass-lpi-pinctrl.yaml` describes the Qualcomm SC8280XP LPASS LPI TLMM pin controller. It specializes the common LPASS LPI schema with this SoC's compatible string, register layout, GPIO pin range, and audio-oriented mux function list.

### Important Schema APIs
The binding provides compatible `qcom,sc8280xp-lpass-lpi-pinctrl`. Top-level required properties are `compatible`, `reg`, `clocks`, `clock-names`. The controller also requires clock handles and `clock-names` where the file declares LPASS vote clocks. State nodes matching `-state$` can either be direct state objects or containers of `-pins` objects. They reference `qcom,lpass-lpi-common.yaml#/$defs/qcom-tlmm-state`, so each state requires `pins` and `function` and may set LPASS drive strength, slew rate, bias, input, and output properties. pin names constrained by `^gpio([0-9]|1[0-8])$`. `function` is restricted to 31 local mux choices, starting with `swr_tx_clk`, `swr_tx_data`, `swr_rx_clk`, `swr_rx_data`, `dmic1_clk`, `dmic1_data`, `dmic2_clk`, `dmic2_data`.

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

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,sc8280xp-lpass-lpi-pinctrl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,sc8280xp-tlmm.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,sc8280xp-tlmm.yaml

### Purpose
`qcom,sc8280xp-tlmm.yaml` describes the Qualcomm SC8280XP Top Level Mode Multiplexer controller. It binds the SoC-specific TLMM register block, GPIO and interrupt provider resources, and the legal pin/function names for pinctrl state nodes.

### Important Schema APIs
The binding provides compatible `qcom,sc8280xp-tlmm`. Top-level required properties are `compatible`, `reg`. State nodes matching `-state$` can be direct objects or containers of `-pins` objects, and their `$defs` entry references `qcom,tlmm-common.yaml#/$defs/qcom-tlmm-state`. pin names constrained by `^gpio([0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-1][0-9]|22[0-7])$`. `function` is restricted to 164 local mux choices, starting with `atest_char`, `atest_usb`, `audio_ref`, `cam_mclk`, `cci_async`, `cci_i2c`, `cci_timer0`, `cci_timer1`. The local schema setting is `unevaluatedProperties: false`. `gpio-reserved-ranges` is available for pins owned by firmware or trusted applications.

### Validation Flow
Validation composes the common Qualcomm TLMM provider schema with this SoC-specific file. The common schema requires GPIO and interrupt provider properties, while this file restricts `compatible`, `reg`, interrupt count, optional line-name and reserved-range bounds, and local pin/function enums. The `oneOf` state-node pattern supports both flat state nodes and grouped child pin nodes.

### State And Persistence
The YAML has no mutable state. DTS data persists the physical TLMM register resource, interrupt summary line, GPIO range, reserved GPIO ranges, and pinctrl states. At runtime the Qualcomm TLMM driver maps state labels into mux selection, drive strength, bias, input/output, and GPIO/IRQ domain behavior.

### Dependencies And Integration Points
Dependencies include `qcom,tlmm-common.yaml`, `pinctrl.yaml`, `pinmux-node.yaml`, `pincfg-node.yaml`, `/schemas/types.yaml`, and interrupt-controller dt-bindings used in examples. Integration points are SoC DTSI files, board DTS pin states, Linux pinctrl and GPIO consumers, and wakeup-parent IRQ controllers when declared.

### Risks
The biggest risk is drift between the schema pin/function enum and the driver pin/function tables; a missing enum blocks valid DTS, while an extra enum can allow states the driver cannot program. Pin count limits in regexes and `gpio-line-names` must match hardware. The broad grouped-state pattern can hide semantic mistakes unless examples cover both flat and nested layouts.

### Test Signals
Run `dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/pinctrl/qcom,sc8280xp-tlmm.yaml` and compile representative SoC DTSI users. Negative tests should cover invalid GPIO numbers, unsupported functions, missing `reg`, missing GPIO/IRQ provider cells, and illegal extra properties. Runtime signals are TLMM probe, GPIO chip registration, IRQ domain creation, and successful pin state switching for UART, SPI/I2C, storage, and audio/display functions listed in the enum.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,sc8280xp-tlmm.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,sdm630-pinctrl.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,sdm630-pinctrl.yaml

### Purpose
`qcom,sdm630-pinctrl.yaml` describes the Qualcomm SDM630 Top Level Mode Multiplexer controller. It binds the SoC-specific TLMM register block, GPIO and interrupt provider resources, and the legal pin/function names for pinctrl state nodes.

### Important Schema APIs
The binding provides 2 compatible strings including `qcom,sdm630-pinctrl`, `qcom,sdm660-pinctrl`. Top-level required properties are `compatible`, `reg`. State nodes matching `-state$` can be direct objects or containers of `-pins` objects, and their `$defs` entry references `qcom,tlmm-common.yaml#/$defs/qcom-tlmm-state`. pin names constrained by `^gpio([0-9]|[1-9][0-9]|10[0-9]|11[0-3])$`. `function` is restricted to 182 local mux choices, starting with `adsp_ext`, `agera_pll`, `atest_char`, `atest_char0`, `atest_char1`, `atest_char2`, `atest_char3`, `atest_gpsadc0`. The local schema setting is `unevaluatedProperties: false`. It also bounds `gpio-line-names` to the SoC GPIO count. `gpio-reserved-ranges` is available for pins owned by firmware or trusted applications.

### Validation Flow
Validation composes the common Qualcomm TLMM provider schema with this SoC-specific file. The common schema requires GPIO and interrupt provider properties, while this file restricts `compatible`, `reg`, interrupt count, optional line-name and reserved-range bounds, and local pin/function enums. The `oneOf` state-node pattern supports both flat state nodes and grouped child pin nodes.

### State And Persistence
The YAML has no mutable state. DTS data persists the physical TLMM register resource, interrupt summary line, GPIO range, reserved GPIO ranges, and pinctrl states. At runtime the Qualcomm TLMM driver maps state labels into mux selection, drive strength, bias, input/output, and GPIO/IRQ domain behavior.

### Dependencies And Integration Points
Dependencies include `qcom,tlmm-common.yaml`, `pinctrl.yaml`, `pinmux-node.yaml`, `pincfg-node.yaml`, `/schemas/types.yaml`, and interrupt-controller dt-bindings used in examples. Integration points are SoC DTSI files, board DTS pin states, Linux pinctrl and GPIO consumers, and wakeup-parent IRQ controllers when declared.

### Risks
The biggest risk is drift between the schema pin/function enum and the driver pin/function tables; a missing enum blocks valid DTS, while an extra enum can allow states the driver cannot program. Pin count limits in regexes and `gpio-line-names` must match hardware. The broad grouped-state pattern can hide semantic mistakes unless examples cover both flat and nested layouts.

### Test Signals
Run `dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/pinctrl/qcom,sdm630-pinctrl.yaml` and compile representative SoC DTSI users. Negative tests should cover invalid GPIO numbers, unsupported functions, missing `reg`, missing GPIO/IRQ provider cells, and illegal extra properties. Runtime signals are TLMM probe, GPIO chip registration, IRQ domain creation, and successful pin state switching for UART, SPI/I2C, storage, and audio/display functions listed in the enum.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,sdm630-pinctrl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,sdm660-lpass-lpi-pinctrl.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,sdm660-lpass-lpi-pinctrl.yaml

### Purpose
`qcom,sdm660-lpass-lpi-pinctrl.yaml` describes the Qualcomm SDM660 LPASS LPI TLMM pin controller. It specializes the common LPASS LPI schema with this SoC's compatible string, register layout, GPIO pin range, and audio-oriented mux function list.

### Important Schema APIs
The binding provides compatible `qcom,sdm660-lpass-lpi-pinctrl`. Top-level required properties are `compatible`, `reg`. State nodes matching `-state$` can either be direct state objects or containers of `-pins` objects. They reference `qcom,lpass-lpi-common.yaml#/$defs/qcom-tlmm-state`, so each state requires `pins` and `function` and may set LPASS drive strength, slew rate, bias, input, and output properties. pin names constrained by `^gpio([0-9]|[1-2][0-9]|3[0-1])$`. `function` is restricted to 11 local mux choices, starting with `gpio`, `comp_rx`, `dmic1_clk`, `dmic1_data`, `dmic2_clk`, `dmic2_data`, `mclk0`, `pdm_tx`.

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

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,sdm660-lpass-lpi-pinctrl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,sdm670-lpass-lpi-pinctrl.yaml -->
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

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,sdm670-lpass-lpi-pinctrl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,sdm670-tlmm.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,sdm670-tlmm.yaml

### Purpose
`qcom,sdm670-tlmm.yaml` describes the Qualcomm SDM670 Top Level Mode Multiplexer controller. It binds the SoC-specific TLMM register block, GPIO and interrupt provider resources, and the legal pin/function names for pinctrl state nodes.

### Important Schema APIs
The binding provides compatible `qcom,sdm670-tlmm`. Top-level required properties are `compatible`, `reg`. State nodes matching `-state$` can be direct objects or containers of `-pins` objects, and their `$defs` entry references `qcom,tlmm-common.yaml#/$defs/qcom-tlmm-state`. pin names constrained by `^gpio([0-9]|[1-9][0-9]|1[0-4][0-9])$`. `function` is restricted to 125 local mux choices, starting with `adsp_ext`, `agera_pll`, `atest_char`, `atest_tsens`, `atest_tsens2`, `atest_usb1`, `atest_usb10`, `atest_usb11`. The local schema setting is `unevaluatedProperties: false`. `gpio-reserved-ranges` is available for pins owned by firmware or trusted applications.

### Validation Flow
Validation composes the common Qualcomm TLMM provider schema with this SoC-specific file. The common schema requires GPIO and interrupt provider properties, while this file restricts `compatible`, `reg`, interrupt count, optional line-name and reserved-range bounds, and local pin/function enums. The `oneOf` state-node pattern supports both flat state nodes and grouped child pin nodes.

### State And Persistence
The YAML has no mutable state. DTS data persists the physical TLMM register resource, interrupt summary line, GPIO range, reserved GPIO ranges, and pinctrl states. At runtime the Qualcomm TLMM driver maps state labels into mux selection, drive strength, bias, input/output, and GPIO/IRQ domain behavior.

### Dependencies And Integration Points
Dependencies include `qcom,tlmm-common.yaml`, `pinctrl.yaml`, `pinmux-node.yaml`, `pincfg-node.yaml`, `/schemas/types.yaml`, and interrupt-controller dt-bindings used in examples. Integration points are SoC DTSI files, board DTS pin states, Linux pinctrl and GPIO consumers, and wakeup-parent IRQ controllers when declared.

### Risks
The biggest risk is drift between the schema pin/function enum and the driver pin/function tables; a missing enum blocks valid DTS, while an extra enum can allow states the driver cannot program. Pin count limits in regexes and `gpio-line-names` must match hardware. The broad grouped-state pattern can hide semantic mistakes unless examples cover both flat and nested layouts.

### Test Signals
Run `dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/pinctrl/qcom,sdm670-tlmm.yaml` and compile representative SoC DTSI users. Negative tests should cover invalid GPIO numbers, unsupported functions, missing `reg`, missing GPIO/IRQ provider cells, and illegal extra properties. Runtime signals are TLMM probe, GPIO chip registration, IRQ domain creation, and successful pin state switching for UART, SPI/I2C, storage, and audio/display functions listed in the enum.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,sdm670-tlmm.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,sdm845-pinctrl.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,sdm845-pinctrl.yaml

### Purpose
`qcom,sdm845-pinctrl.yaml` describes the Qualcomm SDM845 Top Level Mode Multiplexer controller. It binds the SoC-specific TLMM register block, GPIO and interrupt provider resources, and the legal pin/function names for pinctrl state nodes.

### Important Schema APIs
The binding provides compatible `qcom,sdm845-pinctrl`. Top-level required properties are `compatible`, `reg`. State nodes matching `-state$` can be direct objects or containers of `-pins` objects, and their `$defs` entry references `qcom,tlmm-common.yaml#/$defs/qcom-tlmm-state`. pin names constrained by `^gpio([0-9]|[1-9][0-9]|1[0-4][0-9])$`. `function` is restricted to 129 local mux choices, starting with `adsp_ext`, `agera_pll`, `atest_char`, `atest_tsens`, `atest_tsens2`, `atest_usb1`, `atest_usb10`, `atest_usb11`. The local schema setting is `unevaluatedProperties: false`. It also bounds `gpio-line-names` to the SoC GPIO count. `gpio-reserved-ranges` is available for pins owned by firmware or trusted applications.

### Validation Flow
Validation composes the common Qualcomm TLMM provider schema with this SoC-specific file. The common schema requires GPIO and interrupt provider properties, while this file restricts `compatible`, `reg`, interrupt count, optional line-name and reserved-range bounds, and local pin/function enums. The `oneOf` state-node pattern supports both flat state nodes and grouped child pin nodes.

### State And Persistence
The YAML has no mutable state. DTS data persists the physical TLMM register resource, interrupt summary line, GPIO range, reserved GPIO ranges, and pinctrl states. At runtime the Qualcomm TLMM driver maps state labels into mux selection, drive strength, bias, input/output, and GPIO/IRQ domain behavior.

### Dependencies And Integration Points
Dependencies include `qcom,tlmm-common.yaml`, `pinctrl.yaml`, `pinmux-node.yaml`, `pincfg-node.yaml`, `/schemas/types.yaml`, and interrupt-controller dt-bindings used in examples. Integration points are SoC DTSI files, board DTS pin states, Linux pinctrl and GPIO consumers, and wakeup-parent IRQ controllers when declared.

### Risks
The biggest risk is drift between the schema pin/function enum and the driver pin/function tables; a missing enum blocks valid DTS, while an extra enum can allow states the driver cannot program. Pin count limits in regexes and `gpio-line-names` must match hardware. The broad grouped-state pattern can hide semantic mistakes unless examples cover both flat and nested layouts.

### Test Signals
Run `dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/pinctrl/qcom,sdm845-pinctrl.yaml` and compile representative SoC DTSI users. Negative tests should cover invalid GPIO numbers, unsupported functions, missing `reg`, missing GPIO/IRQ provider cells, and illegal extra properties. Runtime signals are TLMM probe, GPIO chip registration, IRQ domain creation, and successful pin state switching for UART, SPI/I2C, storage, and audio/display functions listed in the enum.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,sdm845-pinctrl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,sdx55-pinctrl.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,sdx55-pinctrl.yaml

### Purpose
`qcom,sdx55-pinctrl.yaml` describes the Qualcomm SDX55 Top Level Mode Multiplexer controller. It binds the SoC-specific TLMM register block, GPIO and interrupt provider resources, and the legal pin/function names for pinctrl state nodes.

### Important Schema APIs
The binding provides compatible `qcom,sdx55-pinctrl`. Top-level required properties are `compatible`, `reg`. State nodes matching `-state$` can be direct objects or containers of `-pins` objects, and their `$defs` entry references `qcom,tlmm-common.yaml#/$defs/qcom-tlmm-state`. pin names constrained by `^gpio([0-9]|[1-9][0-9]|10[0-7])$`. `function` is restricted to 131 local mux choices, starting with `adsp_ext`, `atest`, `audio_ref`, `bimc_dte0`, `bimc_dte1`, `blsp_i2c1`, `blsp_i2c2`, `blsp_i2c3`. The local schema setting is `unevaluatedProperties: false`. `gpio-reserved-ranges` is available for pins owned by firmware or trusted applications.

### Validation Flow
Validation composes the common Qualcomm TLMM provider schema with this SoC-specific file. The common schema requires GPIO and interrupt provider properties, while this file restricts `compatible`, `reg`, interrupt count, optional line-name and reserved-range bounds, and local pin/function enums. The `oneOf` state-node pattern supports both flat state nodes and grouped child pin nodes.

### State And Persistence
The YAML has no mutable state. DTS data persists the physical TLMM register resource, interrupt summary line, GPIO range, reserved GPIO ranges, and pinctrl states. At runtime the Qualcomm TLMM driver maps state labels into mux selection, drive strength, bias, input/output, and GPIO/IRQ domain behavior.

### Dependencies And Integration Points
Dependencies include `qcom,tlmm-common.yaml`, `pinctrl.yaml`, `pinmux-node.yaml`, `pincfg-node.yaml`, `/schemas/types.yaml`, and interrupt-controller dt-bindings used in examples. Integration points are SoC DTSI files, board DTS pin states, Linux pinctrl and GPIO consumers, and wakeup-parent IRQ controllers when declared.

### Risks
The biggest risk is drift between the schema pin/function enum and the driver pin/function tables; a missing enum blocks valid DTS, while an extra enum can allow states the driver cannot program. Pin count limits in regexes and `gpio-line-names` must match hardware. The broad grouped-state pattern can hide semantic mistakes unless examples cover both flat and nested layouts.

### Test Signals
Run `dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/pinctrl/qcom,sdx55-pinctrl.yaml` and compile representative SoC DTSI users. Negative tests should cover invalid GPIO numbers, unsupported functions, missing `reg`, missing GPIO/IRQ provider cells, and illegal extra properties. Runtime signals are TLMM probe, GPIO chip registration, IRQ domain creation, and successful pin state switching for UART, SPI/I2C, storage, and audio/display functions listed in the enum.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,sdx55-pinctrl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,sdx65-tlmm.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,sdx65-tlmm.yaml

### Purpose
`qcom,sdx65-tlmm.yaml` describes the Qualcomm SDX65 Top Level Mode Multiplexer controller. It binds the SoC-specific TLMM register block, GPIO and interrupt provider resources, and the legal pin/function names for pinctrl state nodes.

### Important Schema APIs
The binding provides compatible `qcom,sdx65-tlmm`. Top-level required properties are `compatible`, `reg`. State nodes matching `-state$` can be direct objects or containers of `-pins` objects, and their `$defs` entry references `qcom,tlmm-common.yaml#/$defs/qcom-tlmm-state`. pin names constrained by `^gpio([0-9]|[1-9][0-9]|10[0-7])$`. `function` is restricted to 244 local mux choices, starting with `blsp_uart1`, `blsp_spi1`, `blsp_i2c1`, `blsp_uim1`, `atest_tsens`, `bimc_dte1`, `dac_calib0`, `blsp_spi8`. The local schema setting is `unevaluatedProperties: false`. `gpio-reserved-ranges` is available for pins owned by firmware or trusted applications.

### Validation Flow
Validation composes the common Qualcomm TLMM provider schema with this SoC-specific file. The common schema requires GPIO and interrupt provider properties, while this file restricts `compatible`, `reg`, interrupt count, optional line-name and reserved-range bounds, and local pin/function enums. The `oneOf` state-node pattern supports both flat state nodes and grouped child pin nodes.

### State And Persistence
The YAML has no mutable state. DTS data persists the physical TLMM register resource, interrupt summary line, GPIO range, reserved GPIO ranges, and pinctrl states. At runtime the Qualcomm TLMM driver maps state labels into mux selection, drive strength, bias, input/output, and GPIO/IRQ domain behavior.

### Dependencies And Integration Points
Dependencies include `qcom,tlmm-common.yaml`, `pinctrl.yaml`, `pinmux-node.yaml`, `pincfg-node.yaml`, `/schemas/types.yaml`, and interrupt-controller dt-bindings used in examples. Integration points are SoC DTSI files, board DTS pin states, Linux pinctrl and GPIO consumers, and wakeup-parent IRQ controllers when declared.

### Risks
The biggest risk is drift between the schema pin/function enum and the driver pin/function tables; a missing enum blocks valid DTS, while an extra enum can allow states the driver cannot program. Pin count limits in regexes and `gpio-line-names` must match hardware. The broad grouped-state pattern can hide semantic mistakes unless examples cover both flat and nested layouts.

### Test Signals
Run `dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/pinctrl/qcom,sdx65-tlmm.yaml` and compile representative SoC DTSI users. Negative tests should cover invalid GPIO numbers, unsupported functions, missing `reg`, missing GPIO/IRQ provider cells, and illegal extra properties. Runtime signals are TLMM probe, GPIO chip registration, IRQ domain creation, and successful pin state switching for UART, SPI/I2C, storage, and audio/display functions listed in the enum.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,sdx65-tlmm.yaml -->
