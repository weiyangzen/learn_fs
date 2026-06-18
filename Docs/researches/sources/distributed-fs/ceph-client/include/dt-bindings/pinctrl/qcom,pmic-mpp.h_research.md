# sources/distributed-fs/ceph-client/include/dt-bindings/pinctrl/qcom,pmic-mpp.h

Purpose: `qcom,pmic-mpp.h` is a Devicetree binding header for a pin controller. It exports numeric C
preprocessor constants that DTS files and provider drivers share as the ABI for phandle cells,
selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 67 `#define`s covering pinctrl pin, pad, mux,
drive, bias, or electrical configuration cells. The main macro families are PMIC_MPP (22), PM8018
(7), PM8038 (6), PM8901 (5), PM8058 (4), PM8921 (4), PM8941 (4), PMA8084 (4), PM8994 (4), PM8916
(3). Representative constants are `PM8058_MPP_VPH`, `PM8058_MPP_S3`, `PM8058_MPP_L2`,
`PM8058_MPP_L3`, `PM8901_MPP_MSMIO`, `PM8901_MPP_DIG`, `PM8901_MPP_L5`, `PM8901_MPP_S4`, `...`,
`PMIC_MPP_AOUT_LVL_ABUS2`, `PMIC_MPP_AOUT_LVL_ABUS3`, `PMIC_MPP_FUNC_NORMAL`,
`PMIC_MPP_FUNC_PAIRED`, `PMIC_MPP_FUNC_DTEST1`, `PMIC_MPP_FUNC_DTEST2`, `PMIC_MPP_FUNC_DTEST3`,
`PMIC_MPP_FUNC_DTEST4`. Function-like helpers are none. Value shape: literal numeric range 0..7
across 61 macros; 6 alias or symbol-derived values.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`_DT_BINDINGS_PINCTRL_QCOM_PMIC_MPP_H`; after preprocessing, DTS C-preprocessor users and C drivers
see only the constants and any packing helpers. Comment-delimited groups or observed macro clusters
are `power-source`, `Digital Input/Output: level [PM8058]`, `Digital Input/Output: level [PM8901]`,
`Digital Input/Output: level [PM8921]`, `Digital Input/Output: level [PM8821]`, `Digital
Input/Output: level [PM8018]`, `Digital Input/Output: level [PM8038]`, `Only supported for
MPP_05-MPP_08`, `Analog Output: level`, `To be used with "function"`, which is the intended lookup
structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are pinctrl provider drivers, board DTS
files, and schema examples that encode pinmux or pin configuration cells.

Local source signals: The file is 106 lines long. Notable source comments include `This header provides constants for the
Qualcomm PMIC's Multi-Purpose Pin binding.`, `power-source`, `Digital Input/Output: level [PM8058]`,
`Digital Input/Output: level [PM8901]`, `Digital Input/Output: level [PM8921]`, `Digital
Input/Output: level [PM8821]`. Example value clusters are PMIC_MPP: `PMIC_MPP_AMUX_ROUTE_CH5=0`,
`PMIC_MPP_AMUX_ROUTE_CH6=1`, `PMIC_MPP_AMUX_ROUTE_CH7=2`, `PMIC_MPP_AMUX_ROUTE_CH8=3`; PM8018:
`PM8018_MPP_L4=0`, `PM8018_MPP_L14=1`, `PM8018_MPP_S3=2`, `PM8018_MPP_L6=3`; PM8038:
`PM8038_MPP_L20=0`, `PM8038_MPP_L11=1`, `PM8038_MPP_L5=2`, `PM8038_MPP_L15=3`; PM8901:
`PM8901_MPP_MSMIO=0`, `PM8901_MPP_DIG=1`, `PM8901_MPP_L5=2`, `PM8901_MPP_S4=3`; PM8058:
`PM8058_MPP_VPH=0`, `PM8058_MPP_S3=1`, `PM8058_MPP_L2=2`, `PM8058_MPP_L3=3`.

Risks and test signals: Primary risks are renumbering pin IDs, changing mux-function encodings, or altering packing macro
bit fields can silently route pins to the wrong peripheral. Pay special attention to exported
symbols such as `PM8058_MPP_VPH`, `PM8058_MPP_S3`, `PM8058_MPP_L2`, `PM8058_MPP_L3`,
`PM8901_MPP_MSMIO`, `PM8901_MPP_DIG`, `PM8901_MPP_L5`, `PM8901_MPP_S4`. Test signals include
dt_binding_check coverage, DTS compile coverage for each SoC, pinctrl probe logs, GPIO loopback, and
peripheral bring-up using representative mux groups.
