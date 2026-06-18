# sources/distributed-fs/ceph-client/include/dt-bindings/reset/mediatek,mt8196-resets.h

Purpose: `mediatek,mt8196-resets.h` is a Devicetree binding header for a reset-controller provider. It
exports numeric C preprocessor constants that DTS files and provider drivers share as the ABI for
phandle cells, selector values, and stable symbolic names.

Important APIs/types/functions: The exported API is the preprocessor symbol set: 10 `#define`s covering reset-controller IDs and
reset-line indexes. The main macro families are MT8196 (10). Representative constants are
`MT8196_PEXTP0_RST0_PCIE0_MAC`, `MT8196_PEXTP0_RST0_PCIE0_PHY`, `MT8196_PEXTP1_RST0_PCIE1_MAC`,
`MT8196_PEXTP1_RST0_PCIE1_PHY`, `MT8196_PEXTP1_RST0_PCIE2_MAC`, `MT8196_PEXTP1_RST0_PCIE2_PHY`,
`MT8196_UFSAO_RST0_UFS_MPHY`, `MT8196_UFSAO_RST1_UFS_UNIPRO`, `MT8196_PEXTP1_RST0_PCIE1_MAC`,
`MT8196_PEXTP1_RST0_PCIE1_PHY`, `MT8196_PEXTP1_RST0_PCIE2_MAC`, `MT8196_PEXTP1_RST0_PCIE2_PHY`,
`MT8196_UFSAO_RST0_UFS_MPHY`, `MT8196_UFSAO_RST1_UFS_UNIPRO`, `MT8196_UFSAO_RST1_UFS_CRYPTO`,
`MT8196_UFSAO_RST1_UFSHCI`. Function-like helpers are none. Value shape: literal numeric range 0..3
across 10 macros.

Control flow: There is no runtime control flow in this header. Inclusion is controlled by
`_DT_BINDINGS_RESET_CONTROLLER_MT8196`; after preprocessing, DTS C-preprocessor users and C drivers
see only the constants and any packing helpers. Comment-delimited groups or observed macro clusters
are `PEXTP0 resets`, `PEXTP1 resets`, `UFS resets`, which is the intended lookup structure for
maintainers.

State and persistence behavior: The file owns no mutable kernel state and persists nothing at runtime. Its numeric assignments are
persistent ABI because compiled DTBs store the resulting cells and kernel providers interpret those
cell values later during probe, reset, power, regulator, PWM, PMU, or pinctrl operations.

Dependencies and integration points: Dependencies are no included headers. Integration points are reset-controller providers and consumer
device nodes that pass reset IDs in `resets` phandles.

Local source signals: The file is 26 lines long. Notable source comments include `PEXTP0 resets`, `PEXTP1 resets`, `UFS
resets`, `_DT_BINDINGS_RESET_CONTROLLER_MT8196`. Example value clusters are MT8196:
`MT8196_PEXTP0_RST0_PCIE0_MAC=0`, `MT8196_PEXTP0_RST0_PCIE0_PHY=1`,
`MT8196_PEXTP1_RST0_PCIE1_MAC=0`, `MT8196_PEXTP1_RST0_PCIE1_PHY=1`.

Risks and test signals: Primary risks are reset ID drift can assert the wrong hardware line or leave a dependent block
permanently held in reset. Pay special attention to exported symbols such as
`MT8196_PEXTP0_RST0_PCIE0_MAC`, `MT8196_PEXTP0_RST0_PCIE0_PHY`, `MT8196_PEXTP1_RST0_PCIE1_MAC`,
`MT8196_PEXTP1_RST0_PCIE1_PHY`, `MT8196_PEXTP1_RST0_PCIE2_MAC`, `MT8196_PEXTP1_RST0_PCIE2_PHY`,
`MT8196_UFSAO_RST0_UFS_MPHY`, `MT8196_UFSAO_RST1_UFS_UNIPRO`. Test signals include DTS compile
checks, reset-controller probe, driver reset/deassert paths, and peripheral reinitialization after
module or runtime-PM cycles.
