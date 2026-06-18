# sources/distributed-fs/ceph-client/include/dt-bindings/reset/mt2701-resets.h

Purpose: `mt2701-resets.h` is a Devicetree binding header for a reset-controller provider. It exports numeric
C preprocessor constants that DTS files and provider drivers share as the ABI for phandle cells,
selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 64 `#define`s covering reset-controller IDs and
reset-line indexes. The main macro families are MT2701 (64). Representative constants are
`MT2701_INFRA_EMI_REG_RST`, `MT2701_INFRA_DRAMC0_A0_RST`, `MT2701_INFRA_FHCTL_RST`,
`MT2701_INFRA_APCIRQ_EINT_RST`, `MT2701_INFRA_APXGPT_RST`, `MT2701_INFRA_SCPSYS_RST`,
`MT2701_INFRA_KP_RST`, `MT2701_INFRA_PMIC_WRAP_RST`, `...`, `MT2701_HIFSYS_PCIE1_RST`,
`MT2701_HIFSYS_PCIE2_RST`, `MT2701_ETHSYS_SYS_RST`, `MT2701_ETHSYS_MCM_RST`, `MT2701_ETHSYS_FE_RST`,
`MT2701_ETHSYS_GMAC_RST`, `MT2701_ETHSYS_PPE_RST`, `MT2701_G3DSYS_CORE_RST`. Function-like helpers
are none. Value shape: literal numeric range 0..38 across 64 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`_DT_BINDINGS_RESET_CONTROLLER_MT2701`; after preprocessing, DTS C-preprocessor users and C drivers
see only the constants and any packing helpers. Comment-delimited groups or observed macro clusters
are `INFRACFG resets`, `PERICFG resets`, `TOPRGU resets`, `HIFSYS resets`, `ETHSYS resets`, `G3DSYS
resets`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are reset-controller providers and consumer
device nodes that pass reset IDs in `resets` phandles.

Local source signals: The file is 85 lines long. Notable source comments include `INFRACFG resets`, `PERICFG resets`,
`TOPRGU resets`, `HIFSYS resets`, `ETHSYS resets`, `G3DSYS resets`. Example value clusters are
MT2701: `MT2701_INFRA_EMI_REG_RST=0`, `MT2701_INFRA_DRAMC0_A0_RST=1`, `MT2701_INFRA_FHCTL_RST=2`,
`MT2701_INFRA_APCIRQ_EINT_RST=3`.

Risks and test signals: Primary risks are reset ID drift can assert the wrong hardware line or leave a dependent block
permanently held in reset. Pay special attention to exported symbols such as
`MT2701_INFRA_EMI_REG_RST`, `MT2701_INFRA_DRAMC0_A0_RST`, `MT2701_INFRA_FHCTL_RST`,
`MT2701_INFRA_APCIRQ_EINT_RST`, `MT2701_INFRA_APXGPT_RST`, `MT2701_INFRA_SCPSYS_RST`,
`MT2701_INFRA_KP_RST`, `MT2701_INFRA_PMIC_WRAP_RST`. Test signals include DTS compile checks, reset-
controller probe, driver reset/deassert paths, and peripheral reinitialization after module or
runtime-PM cycles.
