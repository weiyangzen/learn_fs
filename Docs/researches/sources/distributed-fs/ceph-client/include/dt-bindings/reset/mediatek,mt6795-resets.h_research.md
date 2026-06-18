# sources/distributed-fs/ceph-client/include/dt-bindings/reset/mediatek,mt6795-resets.h

Purpose: `mediatek,mt6795-resets.h` is a Devicetree binding header for a reset-controller provider. It
exports numeric C preprocessor constants that DTS files and provider drivers share as the ABI for
phandle cells, selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 35 `#define`s covering reset-controller IDs and
reset-line indexes. The main macro families are MT6795 (35). Representative constants are
`MT6795_INFRA_RST0_SCPSYS_RST`, `MT6795_INFRA_RST0_PMIC_WRAP_RST`, `MT6795_INFRA_RST1_MIPI_DSI_RST`,
`MT6795_INFRA_RST1_MIPI_CSI_RST`, `MT6795_INFRA_RST1_MM_IOMMU_RST`,
`MT6795_MMSYS_SW0_RST_B_SMI_COMMON`, `MT6795_MMSYS_SW0_RST_B_SMI_LARB`,
`MT6795_MMSYS_SW0_RST_B_CAM_MDP`, `...`, `MT6795_TOPRGU_IMG_SW_RST`, `MT6795_TOPRGU_DDRPHY_SW_RST`,
`MT6795_TOPRGU_MD_SW_RST`, `MT6795_TOPRGU_INFRA_AO_SW_RST`, `MT6795_TOPRGU_MD_LITE_SW_RST`,
`MT6795_TOPRGU_APMIXED_SW_RST`, `MT6795_TOPRGU_PWRAP_SPI_CTL_RST`, `MT6795_TOPRGU_SW_RST_NUM`.
Function-like helpers are none. Value shape: literal numeric range 0..13 across 35 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`_DT_BINDINGS_RESET_CONTROLLER_MT6795`; after preprocessing, DTS C-preprocessor users and C drivers
see only the constants and any packing helpers. Comment-delimited groups or observed macro clusters
are `INFRACFG resets`, `MMSYS resets`, `PERICFG resets`, `TOPRGU resets`, which is the intended
lookup structure for maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are reset-controller providers and consumer
device nodes that pass reset IDs in `resets` phandles.

Local source signals: The file is 53 lines long. Notable source comments include `INFRACFG resets`, `MMSYS resets`,
`PERICFG resets`, `TOPRGU resets`, `_DT_BINDINGS_RESET_CONTROLLER_MT6795`. Example value clusters
are MT6795: `MT6795_INFRA_RST0_SCPSYS_RST=0`, `MT6795_INFRA_RST0_PMIC_WRAP_RST=1`,
`MT6795_INFRA_RST1_MIPI_DSI_RST=2`, `MT6795_INFRA_RST1_MIPI_CSI_RST=3`.

Risks and test signals: Primary risks are reset ID drift can assert the wrong hardware line or leave a dependent block
permanently held in reset. Pay special attention to exported symbols such as
`MT6795_INFRA_RST0_SCPSYS_RST`, `MT6795_INFRA_RST0_PMIC_WRAP_RST`, `MT6795_INFRA_RST1_MIPI_DSI_RST`,
`MT6795_INFRA_RST1_MIPI_CSI_RST`, `MT6795_INFRA_RST1_MM_IOMMU_RST`,
`MT6795_MMSYS_SW0_RST_B_SMI_COMMON`, `MT6795_MMSYS_SW0_RST_B_SMI_LARB`,
`MT6795_MMSYS_SW0_RST_B_CAM_MDP`. Test signals include DTS compile checks, reset-controller probe,
driver reset/deassert paths, and peripheral reinitialization after module or runtime-PM cycles.
