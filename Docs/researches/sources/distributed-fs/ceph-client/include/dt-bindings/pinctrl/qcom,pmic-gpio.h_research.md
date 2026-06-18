# sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/qcom,pmic-gpio.h

Purpose: `qcom,pmic-gpio.h` is a Devicetree binding header for a pin controller. It exports numeric C
preprocessor constants that DTS files and provider drivers share as the ABI for phandle cells,
selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 116 `#define`s covering pinctrl pin, pad, mux,
drive, bias, or electrical configuration cells. The main macro families are PM8058 (22), PMIC_GPIO
(18), PM8038 (15), PM8917 (12), PM8941 (12), PMA8084 (11), PM8916 (9), PM8018 (7), PM8921 (7),
PM8994 (3). Representative constants are `PMIC_GPIO_PULL_UP_30`, `PMIC_GPIO_PULL_UP_1P5`,
`PMIC_GPIO_PULL_UP_31P5`, `PMIC_GPIO_PULL_UP_1P5_30`, `PMIC_GPIO_STRENGTH_NO`,
`PMIC_GPIO_STRENGTH_HIGH`, `PMIC_GPIO_STRENGTH_MED`, `PMIC_GPIO_STRENGTH_LOW`, `...`,
`PM8941_GPIO33_36_LPG_DRV_HI`, `PMA8084_GPIO4_5_LPG_DRV`, `PMA8084_GPIO7_10_LPG_DRV`,
`PMA8084_GPIO5_14_KEYP_DRV`, `PMA8084_GPIO19_21_KEYP_DRV`, `PMA8084_GPIO15_18_DIV_CLK`,
`PMA8084_GPIO15_18_SLEEP_CLK`, `PMA8084_GPIO22_BAT_ALRM_OUT`. Function-like helpers are none. Value
shape: literal numeric range 0..7 across 57 macros; 59 alias or symbol-derived values.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`_DT_BINDINGS_PINCTRL_QCOM_PMIC_GPIO_H`; after preprocessing, DTS C-preprocessor users and C drivers
see only the constants and any packing helpers. Comment-delimited groups or observed macro clusters
are `To be used with "function"`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are pinctrl provider drivers, board DTS
files, and schema examples that encode pinmux or pin configuration cells.

Local source signals: The file is 164 lines long. Notable source comments include `This header provides constants for the
Qualcomm PMIC GPIO binding.`, `Note: PM8018 GPIO3 and GPIO4 are supporting only S3 and L2 options
(1.8V)`, `Note: PM8038 GPIO7 and GPIO8 are supporting only L11 and L4 options (1.8V)`, `Note: PM8916
GPIO1 and GPIO2 are supporting only L2(1.15V) and L5(1.8V) options`, `Note: PM8941 gpios from 15 to
18 are supporting only S3 and L6 options (1.8V)`, `Note: PMA8084 gpios from 15 to 18 are supporting
only S4 and L6 options (1.8V)`. Example value clusters are PM8058: `PM8058_GPIO_VPH=0`,
`PM8058_GPIO_BB=1`, `PM8058_GPIO_S3=2`, `PM8058_GPIO_L3=3`; PMIC_GPIO: `PMIC_GPIO_PULL_UP_30=0`,
`PMIC_GPIO_PULL_UP_1P5=1`, `PMIC_GPIO_PULL_UP_31P5=2`, `PMIC_GPIO_PULL_UP_1P5_30=3`; PM8038:
`PM8038_GPIO_VPH=0`, `PM8038_GPIO_BB=1`, `PM8038_GPIO_L11=2`, `PM8038_GPIO_L15=3`; PM8917:
`PM8917_GPIO_VPH=0`, `PM8917_GPIO_S4=2`, `PM8917_GPIO_L15=3`, `PM8917_GPIO_L4=4`; PM8941:
`PM8941_GPIO_VPH=0`, `PM8941_GPIO_L1=1`, `PM8941_GPIO_S3=2`, `PM8941_GPIO_L6=3`.

Risks and test signals: Primary risks are renumbering pin IDs, changing mux-function encodings, or altering packing macro
bit fields can silently route pins to the wrong peripheral. Pay special attention to exported
symbols such as `PMIC_GPIO_PULL_UP_30`, `PMIC_GPIO_PULL_UP_1P5`, `PMIC_GPIO_PULL_UP_31P5`,
`PMIC_GPIO_PULL_UP_1P5_30`, `PMIC_GPIO_STRENGTH_NO`, `PMIC_GPIO_STRENGTH_HIGH`,
`PMIC_GPIO_STRENGTH_MED`, `PMIC_GPIO_STRENGTH_LOW`. Test signals include dt_binding_check coverage,
DTS compile coverage for each SoC, pinctrl probe logs, GPIO loopback, and peripheral bring-up using
representative mux groups.
