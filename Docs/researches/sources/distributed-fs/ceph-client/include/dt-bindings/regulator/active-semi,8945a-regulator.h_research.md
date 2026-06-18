# sources/distributed-fs/ceph-client/include/dt-bindings/regulator/active-semi,8945a-regulator.h

Purpose: `active-semi,8945a-regulator.h` is a Devicetree binding header for a regulator provider. It exports
numeric C preprocessor constants that DTS files and provider drivers share as the ABI for phandle
cells, selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 3 `#define`s covering regulator IDs and regulator
mode/state constants. The main macro families are ACT8945A (3). Representative constants are
`ACT8945A_REGULATOR_MODE_FIXED`, `ACT8945A_REGULATOR_MODE_NORMAL`,
`ACT8945A_REGULATOR_MODE_LOWPOWER`, `ACT8945A_REGULATOR_MODE_FIXED`,
`ACT8945A_REGULATOR_MODE_NORMAL`, `ACT8945A_REGULATOR_MODE_LOWPOWER`. Function-like helpers are
none. Value shape: literal numeric range 1..3 across 3 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`_DT_BINDINGS_REGULATOR_ACT8945A_H`; after preprocessing, DTS C-preprocessor users and C drivers see
only the constants and any packing helpers. Comment-delimited groups or observed macro clusters are
`ACT8945A group`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are regulator drivers, PMIC binding
schemas, and consumers selecting regulator IDs or modes.

Local source signals: The file is 30 lines long. Notable source comments include `Device Tree binding constants for the
ACT8945A PMIC regulators`, `These constants should be used to specify regulator modes in device tree
for ACT8945A regulators as follows: ACT8945A_REGULATOR_MODE_FIXED: It is specific to DCDC regulators
and it specifies the usage of fixed-frequency PWM. ACT8945A_REGULATOR_MODE_NORMAL: It is specific to
LDO regulators and it specifies the usage of normal mode. ACT8945A_REGULATOR_MODE_LOWPOWER: For DCDC
and LDO regulators; it specify the usage of proprietary power-saving mode.`. Example value clusters
are ACT8945A: `ACT8945A_REGULATOR_MODE_FIXED=1`, `ACT8945A_REGULATOR_MODE_NORMAL=2`,
`ACT8945A_REGULATOR_MODE_LOWPOWER=3`.

Risks and test signals: Primary risks are ID or mode changes can bind rails to the wrong regulator or select invalid PMIC
operating modes. Pay special attention to exported symbols such as `ACT8945A_REGULATOR_MODE_FIXED`,
`ACT8945A_REGULATOR_MODE_NORMAL`, `ACT8945A_REGULATOR_MODE_LOWPOWER`. Test signals include regulator
schema validation, PMIC probe, regulator summary inspection, voltage/mode transition checks, and
suspend/resume.
