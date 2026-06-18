# sources/distributed-fs/ceph-client/include/dt-bindings/regulator/qcom,rpmh-regulator.h

Purpose: `qcom,rpmh-regulator.h` is a Devicetree binding header for a regulator provider. It exports numeric
C preprocessor constants that DTS files and provider drivers share as the ABI for phandle cells,
selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 4 `#define`s covering regulator IDs and regulator
mode/state constants. The main macro families are RPMH (4). Representative constants are
`RPMH_REGULATOR_MODE_RET`, `RPMH_REGULATOR_MODE_LPM`, `RPMH_REGULATOR_MODE_AUTO`,
`RPMH_REGULATOR_MODE_HPM`, `RPMH_REGULATOR_MODE_RET`, `RPMH_REGULATOR_MODE_LPM`,
`RPMH_REGULATOR_MODE_AUTO`, `RPMH_REGULATOR_MODE_HPM`. Function-like helpers are none. Value shape:
literal numeric range 0..3 across 4 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`__QCOM_RPMH_REGULATOR_H`; after preprocessing, DTS C-preprocessor users and C drivers see only the
constants and any packing helpers. Comment-delimited groups or observed macro clusters are `RPMH
group`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are regulator drivers, PMIC binding
schemas, and consumers selecting regulator IDs or modes.

Local source signals: The file is 36 lines long. Notable source comments include `These mode constants may be used to
specify modes for various RPMh regulator device tree properties (e.g. regulator-initial-mode). Each
type of regulator supports a subset of the possible modes. %RPMH_REGULATOR_MODE_RET: Retention mode
in which only an extremely small load current is allowed. This mode is supported by LDO and SMPS
type regulators. %RPMH_REGULATOR_MODE_LPM: Low power mode in which a small load current is allowed.
This mode corresponds to PFM for SMPS and BOB type regulators. This mode is supported by LDO,
HFSMPS, BOB, and PMIC4 FTSMPS type regulators. %RPMH_REGULATOR_MODE_AUTO: Auto mode in which the
regulator hardware automatically switches between LPM and HPM based upon the real-time load current.
This mode is supported by HFSMPS, BOB, and PMIC4 FTSMPS type regulators. %RPMH_REGULATOR_MODE_HPM:
High power mode in which the full rated current of the regulator is allowed. This mode corresponds
to PWM for SMPS and BOB type regulators. This mode is supported by all types of regulators.`.
Example value clusters are RPMH: `RPMH_REGULATOR_MODE_RET=0`, `RPMH_REGULATOR_MODE_LPM=1`,
`RPMH_REGULATOR_MODE_AUTO=2`, `RPMH_REGULATOR_MODE_HPM=3`.

Risks and test signals: Primary risks are ID or mode changes can bind rails to the wrong regulator or select invalid PMIC
operating modes. Pay special attention to exported symbols such as `RPMH_REGULATOR_MODE_RET`,
`RPMH_REGULATOR_MODE_LPM`, `RPMH_REGULATOR_MODE_AUTO`, `RPMH_REGULATOR_MODE_HPM`. Test signals
include regulator schema validation, PMIC probe, regulator summary inspection, voltage/mode
transition checks, and suspend/resume.
