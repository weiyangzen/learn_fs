# sources/distributed-fs/ceph-client/include/dt-bindings/regulator/maxim,max77802.h

Purpose: `maxim,max77802.h` is a Devicetree binding header for a regulator provider. It exports numeric C
preprocessor constants that DTS files and provider drivers share as the ABI for phandle cells,
selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 2 `#define`s covering regulator IDs and regulator
mode/state constants. The main macro families are MAX77802 (2). Representative constants are
`MAX77802_OPMODE_LP`, `MAX77802_OPMODE_NORMAL`, `MAX77802_OPMODE_LP`, `MAX77802_OPMODE_NORMAL`.
Function-like helpers are none. Value shape: literal numeric range 1..3 across 2 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`_DT_BINDINGS_REGULATOR_MAXIM_MAX77802_H`; after preprocessing, DTS C-preprocessor users and C
drivers see only the constants and any packing helpers. Comment-delimited groups or observed macro
clusters are `Regulator operating modes`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are regulator drivers, PMIC binding
schemas, and consumers selecting regulator IDs or modes.

Local source signals: The file is 15 lines long. Notable source comments include `Device Tree binding constants for the
Maxim 77802 PMIC regulators`, `Regulator operating modes`,
`_DT_BINDINGS_REGULATOR_MAXIM_MAX77802_H`. Example value clusters are MAX77802:
`MAX77802_OPMODE_LP=1`, `MAX77802_OPMODE_NORMAL=3`.

Risks and test signals: Primary risks are ID or mode changes can bind rails to the wrong regulator or select invalid PMIC
operating modes. Pay special attention to exported symbols such as `MAX77802_OPMODE_LP`,
`MAX77802_OPMODE_NORMAL`. Test signals include regulator schema validation, PMIC probe, regulator
summary inspection, voltage/mode transition checks, and suspend/resume.
