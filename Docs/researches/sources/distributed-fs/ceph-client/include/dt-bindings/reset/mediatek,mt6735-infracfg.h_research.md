# sources/distributed-fs/ceph-client/include/dt-bindings/reset/mediatek,mt6735-infracfg.h

Purpose: `mediatek,mt6735-infracfg.h` is a Devicetree binding header for a reset-controller provider. It
exports numeric C preprocessor constants that DTS files and provider drivers share as the ABI for
phandle cells, selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 20 `#define`s covering reset-controller IDs and
reset-line indexes. The main macro families are MT6735 (20). Representative constants are
`MT6735_INFRA_RST0_EMI_REG`, `MT6735_INFRA_RST0_DRAMC0_AO`, `MT6735_INFRA_RST0_AP_CIRQ_EINT`,
`MT6735_INFRA_RST0_APXGPT`, `MT6735_INFRA_RST0_SCPSYS`, `MT6735_INFRA_RST0_KP`,
`MT6735_INFRA_RST0_PMIC_WRAP`, `MT6735_INFRA_RST0_CLDMA_AO_TOP`, `...`,
`MT6735_INFRA_RST0_EMI_AO_REG`, `MT6735_INFRA_RST0_CCIF_AO`, `MT6735_INFRA_RST0_TRNG`,
`MT6735_INFRA_RST0_SYS_CIRQ`, `MT6735_INFRA_RST0_GCE`, `MT6735_INFRA_RST0_M4U`,
`MT6735_INFRA_RST0_CCIF1`, `MT6735_INFRA_RST0_CLDMA_TOP_PD`. Function-like helpers are none. Value
shape: literal numeric range 0..19 across 20 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`_DT_BINDINGS_RESET_MT6735_INFRACFG_H`; after preprocessing, DTS C-preprocessor users and C drivers
see only the constants and any packing helpers. Comment-delimited groups or observed macro clusters
are `MT6735 group`, which is the intended lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are reset-controller providers and consumer
device nodes that pass reset IDs in `resets` phandles.

Local source signals: The file is 27 lines long. Notable source comments include none. Example value clusters are MT6735:
`MT6735_INFRA_RST0_EMI_REG=0`, `MT6735_INFRA_RST0_DRAMC0_AO=1`, `MT6735_INFRA_RST0_AP_CIRQ_EINT=2`,
`MT6735_INFRA_RST0_APXGPT=3`.

Risks and test signals: Primary risks are reset ID drift can assert the wrong hardware line or leave a dependent block
permanently held in reset. Pay special attention to exported symbols such as
`MT6735_INFRA_RST0_EMI_REG`, `MT6735_INFRA_RST0_DRAMC0_AO`, `MT6735_INFRA_RST0_AP_CIRQ_EINT`,
`MT6735_INFRA_RST0_APXGPT`, `MT6735_INFRA_RST0_SCPSYS`, `MT6735_INFRA_RST0_KP`,
`MT6735_INFRA_RST0_PMIC_WRAP`, `MT6735_INFRA_RST0_CLDMA_AO_TOP`. Test signals include DTS compile
checks, reset-controller probe, driver reset/deassert paths, and peripheral reinitialization after
module or runtime-PM cycles.
