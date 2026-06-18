# sources/distributed-fs/ceph-client/include/dt-bindings/regulator/samsung,s2mpg10-regulator.h

Purpose: `samsung,s2mpg10-regulator.h` is a Devicetree binding header for a regulator provider. It exports
numeric C preprocessor constants that DTS files and provider drivers share as the ABI for phandle
cells, selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 22 `#define`s covering regulator IDs and regulator
mode/state constants. The main macro families are S2MPG10 (13), S2MPG11 (9). Representative
constants are `S2MPG10_EXTCTRL_PWREN`, `S2MPG10_EXTCTRL_PWREN_MIF`, `S2MPG10_EXTCTRL_AP_ACTIVE_N`,
`S2MPG10_EXTCTRL_CPUCL1_EN`, `S2MPG10_EXTCTRL_CPUCL1_EN2`, `S2MPG10_EXTCTRL_CPUCL2_EN`,
`S2MPG10_EXTCTRL_CPUCL2_EN2`, `S2MPG10_EXTCTRL_TPU_EN`, `...`, `S2MPG11_EXTCTRL_PWREN_MIF`,
`S2MPG11_EXTCTRL_AP_ACTIVE_N`, `S2MPG11_EXTCTRL_G3D_EN`, `S2MPG11_EXTCTRL_G3D_EN2`,
`S2MPG11_EXTCTRL_AOC_VDD`, `S2MPG11_EXTCTRL_AOC_RET`, `S2MPG11_EXTCTRL_UFS_EN`,
`S2MPG11_EXTCTRL_LDO13S_EN`. Function-like helpers are none. Value shape: 22 alias or symbol-derived
values.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`_DT_BINDINGS_REGULATOR_SAMSUNG_S2MPG10_H`; after preprocessing, DTS C-preprocessor users and C
drivers see only the constants and any packing helpers. Comment-delimited groups or observed macro
clusters are `S2MPG10 group`, `S2MPG11 group`, which is the intended lookup structure for
maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are regulator drivers, PMIC binding
schemas, and consumers selecting regulator IDs or modes.

Local source signals: The file is 53 lines long. Notable source comments include `Device Tree binding constants for the
Samsung S2MPG1x PMIC regulators`, `Several regulators may be controlled via external signals instead
of via software. These constants describe the possible signals for such regulators and generally
correspond to the respecitve on-chip pins. S2MPG10 regulators supporting these are: - buck1m ..
buck7m buck10m - ldo3m .. ldo19m ldo20m supports external control, but using a different set of
control signals. S2MPG11 regulators supporting these are: - buck1s .. buck3s buck5s buck8s buck9s
bucka buckd - ldo1s ldo2s ldo8s ldo13s`, `PWREN pin`, `PWREN_MIF pin`, `~AP_ACTIVE_N pin`,
`CPUCL1_EN pin`. Example value clusters are S2MPG10: `S2MPG10_EXTCTRL_PWREN=0 /* PWREN pin */`,
`S2MPG10_EXTCTRL_PWREN_MIF=1 /* PWREN_MIF pin */`, `S2MPG10_EXTCTRL_AP_ACTIVE_N=2 /* ~AP_ACTIVE_N
pin */`, `S2MPG10_EXTCTRL_CPUCL1_EN=3 /* CPUCL1_EN pin */`; S2MPG11: `S2MPG11_EXTCTRL_PWREN=0 /*
PWREN pin */`, `S2MPG11_EXTCTRL_PWREN_MIF=1 /* PWREN_MIF pin */`, `S2MPG11_EXTCTRL_AP_ACTIVE_N=2 /*
~AP_ACTIVE_N pin */`, `S2MPG11_EXTCTRL_G3D_EN=3 /* G3D_EN pin */`.

Risks and test signals: Primary risks are ID or mode changes can bind rails to the wrong regulator or select invalid PMIC
operating modes. Pay special attention to exported symbols such as `S2MPG10_EXTCTRL_PWREN`,
`S2MPG10_EXTCTRL_PWREN_MIF`, `S2MPG10_EXTCTRL_AP_ACTIVE_N`, `S2MPG10_EXTCTRL_CPUCL1_EN`,
`S2MPG10_EXTCTRL_CPUCL1_EN2`, `S2MPG10_EXTCTRL_CPUCL2_EN`, `S2MPG10_EXTCTRL_CPUCL2_EN2`,
`S2MPG10_EXTCTRL_TPU_EN`. Test signals include regulator schema validation, PMIC probe, regulator
summary inspection, voltage/mode transition checks, and suspend/resume.
