# sources/distributed-fs/ceph-client/include/dt-bindings/regulator/st,stm32mp15-regulator.h

Purpose: `st,stm32mp15-regulator.h` is a Devicetree binding header for a regulator provider. It exports
numeric C preprocessor constants that DTS files and provider drivers share as the ABI for phandle
cells, selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 23 `#define`s covering regulator IDs and regulator
mode/state constants. The main macro families are VOLTD (23). Representative constants are
`VOLTD_SCMI_REG11`, `VOLTD_SCMI_REG18`, `VOLTD_SCMI_USB33`, `VOLTD_SCMI_STPMIC1_BUCK1`,
`VOLTD_SCMI_STPMIC1_BUCK2`, `VOLTD_SCMI_STPMIC1_BUCK3`, `VOLTD_SCMI_STPMIC1_BUCK4`,
`VOLTD_SCMI_STPMIC1_LDO1`, `...`, `VOLTD_SCMI_STPMIC1_PWR_SW1`, `VOLTD_SCMI_STPMIC1_PWR_SW2`,
`VOLTD_SCMI_VREFBUF`, `VOLTD_SCMI_REGU0`, `VOLTD_SCMI_REGU1`, `VOLTD_SCMI_REGU2`,
`VOLTD_SCMI_REGU3`, `VOLTD_SCMI_REGU4`. Function-like helpers are none. Value shape: literal numeric
range 0..22 across 23 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`__DT_BINDINGS_REGULATOR_ST_STM32MP15_REGULATOR_H`; after preprocessing, DTS C-preprocessor users
and C drivers see only the constants and any packing helpers. Comment-delimited groups or observed
macro clusters are `SCMI voltage domain identifiers`, `SOC Internal regulators`, `STPMIC1
regulators`, `External regulators`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are regulator drivers, PMIC binding
schemas, and consumers selecting regulator IDs or modes.

Local source signals: The file is 40 lines long. Notable source comments include `SCMI voltage domain identifiers`, `SOC
Internal regulators`, `STPMIC1 regulators`, `External regulators`,
`__DT_BINDINGS_REGULATOR_ST_STM32MP15_REGULATOR_H`. Example value clusters are VOLTD:
`VOLTD_SCMI_REG11=0`, `VOLTD_SCMI_REG18=1`, `VOLTD_SCMI_USB33=2`, `VOLTD_SCMI_STPMIC1_BUCK1=3`.

Risks and test signals: Primary risks are ID or mode changes can bind rails to the wrong regulator or select invalid PMIC
operating modes. Pay special attention to exported symbols such as `VOLTD_SCMI_REG11`,
`VOLTD_SCMI_REG18`, `VOLTD_SCMI_USB33`, `VOLTD_SCMI_STPMIC1_BUCK1`, `VOLTD_SCMI_STPMIC1_BUCK2`,
`VOLTD_SCMI_STPMIC1_BUCK3`, `VOLTD_SCMI_STPMIC1_BUCK4`, `VOLTD_SCMI_STPMIC1_LDO1`. Test signals
include regulator schema validation, PMIC probe, regulator summary inspection, voltage/mode
transition checks, and suspend/resume.
