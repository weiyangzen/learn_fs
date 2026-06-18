# subset-b-005820 Research

Grouped source research for Qualcomm Linux device-tree clock binding headers under `include/dt-bindings/clock`. Each section is marker-delimited for deterministic reconciliation into the source-tree-aligned per-file research documents. All 74 listed headers were read as complete files; the reports focus on their binding ABI, macro inventories, integration points, and compatibility risks.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,milos-camcc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,milos-camcc.h

## Purpose

`sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,milos-camcc.h` defines the public device-tree numeric IDs for the Qualcomm camera clock-controller binding associated with `qcom,milos-camcc.h` / `milos`. The source was read completely for this report (131 lines). It is not executable kernel code; it is a stable binding contract included by DTS files and by the matching `drivers/clk/qcom` provider so that phandle clock, reset, and power-domain specifiers use the same indexes.

## Important APIs, Types, and Functions

There are no C functions, structs, or runtime APIs. The exported API is a set of preprocessor constants guarded by `_DT_BINDINGS_CLK_QCOM_CAM_CC_MILOS_H`. This header defines 93 clock IDs, 21 reset IDs, and 1 power-domain/GDSC ID, for 115 numeric binding macros total.

Clock ID range: `CAM_CC_PLL0`=0 through `CAM_CC_XO_CLK_SRC`=92. Representative clocks: `CAM_CC_PLL0`, `CAM_CC_PLL0_OUT_EVEN`, `CAM_CC_PLL0_OUT_ODD`, `CAM_CC_PLL1`, `CAM_CC_PLL1_OUT_EVEN`, `CAM_CC_PLL2`, ... `CAM_CC_TFE_2_CLK_SRC`, `CAM_CC_TFE_2_CPHY_RX_CLK`, `CAM_CC_TFE_2_CSID_CLK`, `CAM_CC_TFE_2_CSID_CLK_SRC`, `CAM_CC_TOP_SHIFT_CLK`, `CAM_CC_XO_CLK_SRC`.

Reset ID range: `CAM_CC_BPS_BCR`=0 through `CAM_CC_TFE_2_BCR`=20. Representative resets: `CAM_CC_BPS_BCR`, `CAM_CC_CAMNOC_BCR`, `CAM_CC_CAMSS_TOP_BCR`, `CAM_CC_CCI_0_BCR`, `CAM_CC_CCI_1_BCR`, `CAM_CC_CPAS_BCR`, ... `CAM_CC_MCLK3_BCR`, `CAM_CC_MCLK4_BCR`, `CAM_CC_OPE_0_BCR`, `CAM_CC_TFE_0_BCR`, `CAM_CC_TFE_1_BCR`, `CAM_CC_TFE_2_BCR`.

Power-domain/GDSC range: `CAM_CC_CAMSS_TOP_GDSC`=0 through `CAM_CC_CAMSS_TOP_GDSC`=0. Representative domains: `CAM_CC_CAMSS_TOP_GDSC`.

Macro inventory begins with:
- `CAM_CC_PLL0` = 0 (clock, line 11)
- `CAM_CC_PLL0_OUT_EVEN` = 1 (clock, line 12)
- `CAM_CC_PLL0_OUT_ODD` = 2 (clock, line 13)
- `CAM_CC_PLL1` = 3 (clock, line 14)
- `CAM_CC_PLL1_OUT_EVEN` = 4 (clock, line 15)
- `CAM_CC_PLL2` = 5 (clock, line 16)
- `CAM_CC_PLL2_OUT_EVEN` = 6 (clock, line 17)
- `CAM_CC_PLL3` = 7 (clock, line 18)
- `CAM_CC_PLL3_OUT_EVEN` = 8 (clock, line 19)
- `CAM_CC_PLL4` = 9 (clock, line 20)
- ... 105 additional numeric binding macros continue in the same contiguous namespace sections.

## Control Flow

This header has no branches, calls, or runtime control flow. The effective flow is build-time and probe-time: DTS sources include the constants, the device-tree compiler stores the resulting integers in clock/reset/power-domain specifier cells, and the Qualcomm clock-controller driver exposes provider arrays whose indexes must match these values. Consumer drivers later resolve those phandles through common clock, reset-controller, or genpd APIs.

## State and Persistence Behavior

The file owns no memory, locks, hardware registers, or persistent storage. Its state is the ABI value assigned to each macro. Those values persist in compiled DTBs and out-of-tree device trees, so renumbering or deleting an existing define is a compatibility break even though no runtime state is stored here. Actual enable counts, reset assertion state, and GDSC power state are maintained by the clock/reset/power-domain drivers and hardware registers, not by this header.

## Dependencies and Integration Points

Direct source dependencies are intentionally minimal: the header has only SPDX/copyright comments, an include guard, macro definitions, and `#endif`. It is integrated by textual inclusion rather than linking. Local integration evidence: clock-controller driver references: `sources/distributed-fs/ceph-client/drivers/clk/qcom/camcc-milos.c`; device-tree references: `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/milos.dtsi`.

The semantic dependency is the matching provider implementation and its descriptor arrays. `qcom,milos-camcc.h` IDs must stay aligned with driver tables for camera PLLs, MCLKs, CSI/CSIPHY timers, IFE/TFE/SFE/BPS/IPE/JPEG/CPAS fabric clocks, resets, and camera GDSCs. DTS consumers depend on these exact constants for properties such as `clocks`, `resets`, `power-domains`, and named clock inputs.

## Risks and Edge Cases

The main risk is ABI drift: inserting new IDs in the middle, reusing a removed value, or moving a reset/GDSC ID to a different number can silently bind a DTS consumer to the wrong hardware clock or power domain. It also exports reset IDs (`CAM_CC_BPS_BCR`=0 through `CAM_CC_TFE_2_BCR`=20). Power-domain/GDSC IDs are exported as `CAM_CC_CAMSS_TOP_GDSC`=0 through `CAM_CC_CAMSS_TOP_GDSC`=0. Shared names such as PLLs, XO/sleep sources, bus clocks, and GDSCs are easy to copy between SoCs, but the numeric ordering must follow this specific provider, not a visually similar controller. Because the file is pure macros, the compiler provides little semantic checking beyond duplicate definitions and include-guard correctness.

## Test Signals

Useful validation includes building the relevant `drivers/clk/qcom` object with this header, compiling DTBs that include `qcom,milos-camcc.h`, and running `dtbs_check`/binding-schema checks for the affected SoC. Runtime smoke tests are provider probe success without missing clock/reset IDs, absence of `-ENOENT`/`-EINVAL` from clock lookups, expected entries under common-clock debugfs, and successful bring-up of consumers in the exported domain set: camera PLLs, MCLKs, CSI/CSIPHY timers, IFE/TFE/SFE/BPS/IPE/JPEG/CPAS fabric clocks, resets, and camera GDSCs. For edits, diff the numeric table against the matching driver arrays and boot at least one DTS consumer when local hardware or emulation coverage exists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,milos-camcc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,milos-dispcc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,milos-dispcc.h

## Purpose

`sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,milos-dispcc.h` defines the public device-tree numeric IDs for the Qualcomm display clock-controller binding associated with `qcom,milos-dispcc.h` / `milos`. The source was read completely for this report (61 lines). It is not executable kernel code; it is a stable binding contract included by DTS files and by the matching `drivers/clk/qcom` provider so that phandle clock, reset, and power-domain specifiers use the same indexes.

## Important APIs, Types, and Functions

There are no C functions, structs, or runtime APIs. The exported API is a set of preprocessor constants guarded by `_DT_BINDINGS_CLK_QCOM_DISP_CC_MILOS_H`. This header defines 40 clock IDs, 3 reset IDs, and 2 power-domain/GDSC IDs, for 45 numeric binding macros total.

Clock ID range: `DISP_CC_PLL0`=0 through `DISP_CC_XO_CLK_SRC`=39. Representative clocks: `DISP_CC_PLL0`, `DISP_CC_MDSS_ACCU_CLK`, `DISP_CC_MDSS_AHB1_CLK`, `DISP_CC_MDSS_AHB_CLK`, `DISP_CC_MDSS_AHB_CLK_SRC`, `DISP_CC_MDSS_BYTE0_CLK`, ... `DISP_CC_MDSS_VSYNC_CLK`, `DISP_CC_MDSS_VSYNC_CLK_SRC`, `DISP_CC_SLEEP_CLK`, `DISP_CC_SLEEP_CLK_SRC`, `DISP_CC_XO_CLK`, `DISP_CC_XO_CLK_SRC`.

Reset ID range: `DISP_CC_MDSS_CORE_BCR`=0 through `DISP_CC_MDSS_RSCC_BCR`=2. Representative resets: `DISP_CC_MDSS_CORE_BCR`, `DISP_CC_MDSS_CORE_INT2_BCR`, `DISP_CC_MDSS_RSCC_BCR`.

Power-domain/GDSC range: `DISP_CC_MDSS_CORE_GDSC`=0 through `DISP_CC_MDSS_CORE_INT2_GDSC`=1. Representative domains: `DISP_CC_MDSS_CORE_GDSC`, `DISP_CC_MDSS_CORE_INT2_GDSC`.

Macro inventory begins with:
- `DISP_CC_PLL0` = 0 (clock, line 11)
- `DISP_CC_MDSS_ACCU_CLK` = 1 (clock, line 12)
- `DISP_CC_MDSS_AHB1_CLK` = 2 (clock, line 13)
- `DISP_CC_MDSS_AHB_CLK` = 3 (clock, line 14)
- `DISP_CC_MDSS_AHB_CLK_SRC` = 4 (clock, line 15)
- `DISP_CC_MDSS_BYTE0_CLK` = 5 (clock, line 16)
- `DISP_CC_MDSS_BYTE0_CLK_SRC` = 6 (clock, line 17)
- `DISP_CC_MDSS_BYTE0_DIV_CLK_SRC` = 7 (clock, line 18)
- `DISP_CC_MDSS_BYTE0_INTF_CLK` = 8 (clock, line 19)
- `DISP_CC_MDSS_DPTX0_AUX_CLK` = 9 (clock, line 20)
- ... 35 additional numeric binding macros continue in the same contiguous namespace sections.

## Control Flow

This header has no branches, calls, or runtime control flow. The effective flow is build-time and probe-time: DTS sources include the constants, the device-tree compiler stores the resulting integers in clock/reset/power-domain specifier cells, and the Qualcomm clock-controller driver exposes provider arrays whose indexes must match these values. Consumer drivers later resolve those phandles through common clock, reset-controller, or genpd APIs.

## State and Persistence Behavior

The file owns no memory, locks, hardware registers, or persistent storage. Its state is the ABI value assigned to each macro. Those values persist in compiled DTBs and out-of-tree device trees, so renumbering or deleting an existing define is a compatibility break even though no runtime state is stored here. Actual enable counts, reset assertion state, and GDSC power state are maintained by the clock/reset/power-domain drivers and hardware registers, not by this header.

## Dependencies and Integration Points

Direct source dependencies are intentionally minimal: the header has only SPDX/copyright comments, an include guard, macro definitions, and `#endif`. It is integrated by textual inclusion rather than linking. Local integration evidence: clock-controller driver references: `sources/distributed-fs/ceph-client/drivers/clk/qcom/dispcc-milos.c`; device-tree references: `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/milos.dtsi`.

The semantic dependency is the matching provider implementation and its descriptor arrays. `qcom,milos-dispcc.h` IDs must stay aligned with driver tables for MDSS AHB/AXI, MDP, DSI byte/escape/pixel, DisplayPort link/pixel/aux, vsync, resets, and display GDSCs. DTS consumers depend on these exact constants for properties such as `clocks`, `resets`, `power-domains`, and named clock inputs.

## Risks and Edge Cases

The main risk is ABI drift: inserting new IDs in the middle, reusing a removed value, or moving a reset/GDSC ID to a different number can silently bind a DTS consumer to the wrong hardware clock or power domain. It also exports reset IDs (`DISP_CC_MDSS_CORE_BCR`=0 through `DISP_CC_MDSS_RSCC_BCR`=2). Power-domain/GDSC IDs are exported as `DISP_CC_MDSS_CORE_GDSC`=0 through `DISP_CC_MDSS_CORE_INT2_GDSC`=1. Shared names such as PLLs, XO/sleep sources, bus clocks, and GDSCs are easy to copy between SoCs, but the numeric ordering must follow this specific provider, not a visually similar controller. Because the file is pure macros, the compiler provides little semantic checking beyond duplicate definitions and include-guard correctness.

## Test Signals

Useful validation includes building the relevant `drivers/clk/qcom` object with this header, compiling DTBs that include `qcom,milos-dispcc.h`, and running `dtbs_check`/binding-schema checks for the affected SoC. Runtime smoke tests are provider probe success without missing clock/reset IDs, absence of `-ENOENT`/`-EINVAL` from clock lookups, expected entries under common-clock debugfs, and successful bring-up of consumers in the exported domain set: MDSS AHB/AXI, MDP, DSI byte/escape/pixel, DisplayPort link/pixel/aux, vsync, resets, and display GDSCs. For edits, diff the numeric table against the matching driver arrays and boot at least one DTS consumer when local hardware or emulation coverage exists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,milos-dispcc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,milos-gcc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,milos-gcc.h

## Purpose

`sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,milos-gcc.h` defines the public device-tree numeric IDs for the Qualcomm global clock-controller binding associated with `qcom,milos-gcc.h` / `milos`. The source was read completely for this report (210 lines). It is not executable kernel code; it is a stable binding contract included by DTS files and by the matching `drivers/clk/qcom` provider so that phandle clock, reset, and power-domain specifiers use the same indexes.

## Important APIs, Types, and Functions

There are no C functions, structs, or runtime APIs. The exported API is a set of preprocessor constants guarded by `_DT_BINDINGS_CLK_QCOM_GCC_MILOS_H`. This header defines 158 clock IDs, 28 reset IDs, and 8 power-domain/GDSC IDs, for 194 numeric binding macros total.

Clock ID range: `GCC_GPLL0`=0 through `GCC_VIDEO_XO_CLK`=157. Representative clocks: `GCC_GPLL0`, `GCC_GPLL0_OUT_EVEN`, `GCC_GPLL2`, `GCC_GPLL4`, `GCC_GPLL6`, `GCC_GPLL7`, ... `GCC_USB3_PRIM_PHY_COM_AUX_CLK`, `GCC_USB3_PRIM_PHY_PIPE_CLK`, `GCC_USB3_PRIM_PHY_PIPE_CLK_SRC`, `GCC_VIDEO_AHB_CLK`, `GCC_VIDEO_AXI0_CLK`, `GCC_VIDEO_XO_CLK`.

Reset ID range: `GCC_CAMERA_BCR`=0 through `GCC_VIDEO_BCR`=27. Representative resets: `GCC_CAMERA_BCR`, `GCC_DISPLAY_BCR`, `GCC_GPU_BCR`, `GCC_PCIE_0_BCR`, `GCC_PCIE_0_LINK_DOWN_BCR`, `GCC_PCIE_0_NOCSR_COM_PHY_BCR`, ... `GCC_USB30_PRIM_BCR`, `GCC_USB3_DP_PHY_PRIM_BCR`, `GCC_USB3_PHY_PRIM_BCR`, `GCC_USB3PHY_PHY_PRIM_BCR`, `GCC_VIDEO_AXI0_CLK_ARES`, `GCC_VIDEO_BCR`.

Power-domain/GDSC range: `PCIE_0_GDSC`=0 through `USB3_PHY_GDSC`=7. Representative domains: `PCIE_0_GDSC`, `PCIE_0_PHY_GDSC`, `PCIE_1_GDSC`, `PCIE_1_PHY_GDSC`, `UFS_PHY_GDSC`, `UFS_MEM_PHY_GDSC`, `USB30_PRIM_GDSC`, `USB3_PHY_GDSC`.

Macro inventory begins with:
- `GCC_GPLL0` = 0 (clock, line 11)
- `GCC_GPLL0_OUT_EVEN` = 1 (clock, line 12)
- `GCC_GPLL2` = 2 (clock, line 13)
- `GCC_GPLL4` = 3 (clock, line 14)
- `GCC_GPLL6` = 4 (clock, line 15)
- `GCC_GPLL7` = 5 (clock, line 16)
- `GCC_GPLL9` = 6 (clock, line 17)
- `GCC_AGGRE_NOC_PCIE_AXI_CLK` = 7 (clock, line 18)
- `GCC_AGGRE_UFS_PHY_AXI_CLK` = 8 (clock, line 19)
- `GCC_AGGRE_UFS_PHY_AXI_HW_CTL_CLK` = 9 (clock, line 20)
- ... 184 additional numeric binding macros continue in the same contiguous namespace sections.

## Control Flow

This header has no branches, calls, or runtime control flow. The effective flow is build-time and probe-time: DTS sources include the constants, the device-tree compiler stores the resulting integers in clock/reset/power-domain specifier cells, and the Qualcomm clock-controller driver exposes provider arrays whose indexes must match these values. Consumer drivers later resolve those phandles through common clock, reset-controller, or genpd APIs.

## State and Persistence Behavior

The file owns no memory, locks, hardware registers, or persistent storage. Its state is the ABI value assigned to each macro. Those values persist in compiled DTBs and out-of-tree device trees, so renumbering or deleting an existing define is a compatibility break even though no runtime state is stored here. Actual enable counts, reset assertion state, and GDSC power state are maintained by the clock/reset/power-domain drivers and hardware registers, not by this header.

## Dependencies and Integration Points

Direct source dependencies are intentionally minimal: the header has only SPDX/copyright comments, an include guard, macro definitions, and `#endif`. It is integrated by textual inclusion rather than linking. Local integration evidence: clock-controller driver references: `sources/distributed-fs/ceph-client/drivers/clk/qcom/gcc-milos.c`; device-tree references: `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/milos.dtsi`.

The semantic dependency is the matching provider implementation and its descriptor arrays. `qcom,milos-gcc.h` IDs must stay aligned with driver tables for global PLLs plus bus, QUP, USB, PCIe, UFS, SDCC, camera/display/video/gpu vote, reset, and GDSC IDs. DTS consumers depend on these exact constants for properties such as `clocks`, `resets`, `power-domains`, and named clock inputs.

## Risks and Edge Cases

The main risk is ABI drift: inserting new IDs in the middle, reusing a removed value, or moving a reset/GDSC ID to a different number can silently bind a DTS consumer to the wrong hardware clock or power domain. It also exports reset IDs (`GCC_CAMERA_BCR`=0 through `GCC_VIDEO_BCR`=27). Power-domain/GDSC IDs are exported as `PCIE_0_GDSC`=0 through `USB3_PHY_GDSC`=7. Shared names such as PLLs, XO/sleep sources, bus clocks, and GDSCs are easy to copy between SoCs, but the numeric ordering must follow this specific provider, not a visually similar controller. Because the file is pure macros, the compiler provides little semantic checking beyond duplicate definitions and include-guard correctness.

## Test Signals

Useful validation includes building the relevant `drivers/clk/qcom` object with this header, compiling DTBs that include `qcom,milos-gcc.h`, and running `dtbs_check`/binding-schema checks for the affected SoC. Runtime smoke tests are provider probe success without missing clock/reset IDs, absence of `-ENOENT`/`-EINVAL` from clock lookups, expected entries under common-clock debugfs, and successful bring-up of consumers in the exported domain set: global PLLs plus bus, QUP, USB, PCIe, UFS, SDCC, camera/display/video/gpu vote, reset, and GDSC IDs. For edits, diff the numeric table against the matching driver arrays and boot at least one DTS consumer when local hardware or emulation coverage exists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,milos-gcc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,milos-gpucc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,milos-gpucc.h

## Purpose

`sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,milos-gpucc.h` defines the public device-tree numeric IDs for the Qualcomm GPU clock-controller binding associated with `qcom,milos-gpucc.h` / `milos`. The source was read completely for this report (56 lines). It is not executable kernel code; it is a stable binding contract included by DTS files and by the matching `drivers/clk/qcom` provider so that phandle clock, reset, and power-domain specifiers use the same indexes.

## Important APIs, Types, and Functions

There are no C functions, structs, or runtime APIs. The exported API is a set of preprocessor constants guarded by `_DT_BINDINGS_CLK_QCOM_GPU_CC_MILOS_H`. This header defines 31 clock IDs, 8 reset IDs, and 1 power-domain/GDSC ID, for 40 numeric binding macros total.

Clock ID range: `GPU_CC_PLL0`=0 through `GPU_CC_XO_DIV_CLK_SRC`=30. Representative clocks: `GPU_CC_PLL0`, `GPU_CC_PLL0_OUT_EVEN`, `GPU_CC_AHB_CLK`, `GPU_CC_CB_CLK`, `GPU_CC_CX_ACCU_SHIFT_CLK`, `GPU_CC_CX_FF_CLK`, ... `GPU_CC_MEMNOC_GFX_CLK`, `GPU_CC_RSCC_HUB_AON_CLK`, `GPU_CC_RSCC_XO_AON_CLK`, `GPU_CC_SLEEP_CLK`, `GPU_CC_XO_CLK_SRC`, `GPU_CC_XO_DIV_CLK_SRC`.

Reset ID range: `GPU_CC_CB_BCR`=0 through `GPU_CC_XO_BCR`=7. Representative resets: `GPU_CC_CB_BCR`, `GPU_CC_CX_BCR`, `GPU_CC_FAST_HUB_BCR`, `GPU_CC_FF_BCR`, `GPU_CC_GMU_BCR`, `GPU_CC_GX_BCR`, `GPU_CC_RBCPR_BCR`, `GPU_CC_XO_BCR`.

Power-domain/GDSC range: `GPU_CC_CX_GDSC`=0 through `GPU_CC_CX_GDSC`=0. Representative domains: `GPU_CC_CX_GDSC`.

Macro inventory begins with:
- `GPU_CC_PLL0` = 0 (clock, line 11)
- `GPU_CC_PLL0_OUT_EVEN` = 1 (clock, line 12)
- `GPU_CC_AHB_CLK` = 2 (clock, line 13)
- `GPU_CC_CB_CLK` = 3 (clock, line 14)
- `GPU_CC_CX_ACCU_SHIFT_CLK` = 4 (clock, line 15)
- `GPU_CC_CX_FF_CLK` = 5 (clock, line 16)
- `GPU_CC_CX_GMU_CLK` = 6 (clock, line 17)
- `GPU_CC_CXO_AON_CLK` = 7 (clock, line 18)
- `GPU_CC_CXO_CLK` = 8 (clock, line 19)
- `GPU_CC_DEMET_CLK` = 9 (clock, line 20)
- ... 30 additional numeric binding macros continue in the same contiguous namespace sections.

## Control Flow

This header has no branches, calls, or runtime control flow. The effective flow is build-time and probe-time: DTS sources include the constants, the device-tree compiler stores the resulting integers in clock/reset/power-domain specifier cells, and the Qualcomm clock-controller driver exposes provider arrays whose indexes must match these values. Consumer drivers later resolve those phandles through common clock, reset-controller, or genpd APIs.

## State and Persistence Behavior

The file owns no memory, locks, hardware registers, or persistent storage. Its state is the ABI value assigned to each macro. Those values persist in compiled DTBs and out-of-tree device trees, so renumbering or deleting an existing define is a compatibility break even though no runtime state is stored here. Actual enable counts, reset assertion state, and GDSC power state are maintained by the clock/reset/power-domain drivers and hardware registers, not by this header.

## Dependencies and Integration Points

Direct source dependencies are intentionally minimal: the header has only SPDX/copyright comments, an include guard, macro definitions, and `#endif`. It is integrated by textual inclusion rather than linking. Local integration evidence: clock-controller driver references: `sources/distributed-fs/ceph-client/drivers/clk/qcom/gpucc-milos.c`; device-tree references: `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/milos.dtsi`.

The semantic dependency is the matching provider implementation and its descriptor arrays. `qcom,milos-gpucc.h` IDs must stay aligned with driver tables for GPU PLL/RCG, GMU, CX/GX, hub, memory NoC, XO/sleep, SMMU vote, reset, and GDSC IDs. DTS consumers depend on these exact constants for properties such as `clocks`, `resets`, `power-domains`, and named clock inputs.

## Risks and Edge Cases

The main risk is ABI drift: inserting new IDs in the middle, reusing a removed value, or moving a reset/GDSC ID to a different number can silently bind a DTS consumer to the wrong hardware clock or power domain. It also exports reset IDs (`GPU_CC_CB_BCR`=0 through `GPU_CC_XO_BCR`=7). Power-domain/GDSC IDs are exported as `GPU_CC_CX_GDSC`=0 through `GPU_CC_CX_GDSC`=0. Shared names such as PLLs, XO/sleep sources, bus clocks, and GDSCs are easy to copy between SoCs, but the numeric ordering must follow this specific provider, not a visually similar controller. Because the file is pure macros, the compiler provides little semantic checking beyond duplicate definitions and include-guard correctness.

## Test Signals

Useful validation includes building the relevant `drivers/clk/qcom` object with this header, compiling DTBs that include `qcom,milos-gpucc.h`, and running `dtbs_check`/binding-schema checks for the affected SoC. Runtime smoke tests are provider probe success without missing clock/reset IDs, absence of `-ENOENT`/`-EINVAL` from clock lookups, expected entries under common-clock debugfs, and successful bring-up of consumers in the exported domain set: GPU PLL/RCG, GMU, CX/GX, hub, memory NoC, XO/sleep, SMMU vote, reset, and GDSC IDs. For edits, diff the numeric table against the matching driver arrays and boot at least one DTS consumer when local hardware or emulation coverage exists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,milos-gpucc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,milos-videocc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,milos-videocc.h

## Purpose

`sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,milos-videocc.h` defines the public device-tree numeric IDs for the Qualcomm video clock-controller binding associated with `qcom,milos-videocc.h` / `milos`. The source was read completely for this report (36 lines). It is not executable kernel code; it is a stable binding contract included by DTS files and by the matching `drivers/clk/qcom` provider so that phandle clock, reset, and power-domain specifiers use the same indexes.

## Important APIs, Types, and Functions

There are no C functions, structs, or runtime APIs. The exported API is a set of preprocessor constants guarded by `_DT_BINDINGS_CLK_QCOM_VIDEO_CC_MILOS_H`. This header defines 14 clock IDs, 4 reset IDs, and 2 power-domain/GDSC IDs, for 20 numeric binding macros total.

Clock ID range: `VIDEO_CC_PLL0`=0 through `VIDEO_CC_XO_CLK_SRC`=13. Representative clocks: `VIDEO_CC_PLL0`, `VIDEO_CC_AHB_CLK`, `VIDEO_CC_AHB_CLK_SRC`, `VIDEO_CC_MVS0_CLK`, `VIDEO_CC_MVS0_CLK_SRC`, `VIDEO_CC_MVS0_DIV_CLK_SRC`, ... `VIDEO_CC_MVS0C_DIV2_DIV_CLK_SRC`, `VIDEO_CC_MVS0C_SHIFT_CLK`, `VIDEO_CC_SLEEP_CLK`, `VIDEO_CC_SLEEP_CLK_SRC`, `VIDEO_CC_XO_CLK`, `VIDEO_CC_XO_CLK_SRC`.

Reset ID range: `VIDEO_CC_INTERFACE_BCR`=0 through `VIDEO_CC_MVS0C_BCR`=3. Representative resets: `VIDEO_CC_INTERFACE_BCR`, `VIDEO_CC_MVS0_BCR`, `VIDEO_CC_MVS0C_CLK_ARES`, `VIDEO_CC_MVS0C_BCR`.

Power-domain/GDSC range: `VIDEO_CC_MVS0_GDSC`=0 through `VIDEO_CC_MVS0C_GDSC`=1. Representative domains: `VIDEO_CC_MVS0_GDSC`, `VIDEO_CC_MVS0C_GDSC`.

Macro inventory begins with:
- `VIDEO_CC_PLL0` = 0 (clock, line 11)
- `VIDEO_CC_AHB_CLK` = 1 (clock, line 12)
- `VIDEO_CC_AHB_CLK_SRC` = 2 (clock, line 13)
- `VIDEO_CC_MVS0_CLK` = 3 (clock, line 14)
- `VIDEO_CC_MVS0_CLK_SRC` = 4 (clock, line 15)
- `VIDEO_CC_MVS0_DIV_CLK_SRC` = 5 (clock, line 16)
- `VIDEO_CC_MVS0_SHIFT_CLK` = 6 (clock, line 17)
- `VIDEO_CC_MVS0C_CLK` = 7 (clock, line 18)
- `VIDEO_CC_MVS0C_DIV2_DIV_CLK_SRC` = 8 (clock, line 19)
- `VIDEO_CC_MVS0C_SHIFT_CLK` = 9 (clock, line 20)
- ... 10 additional numeric binding macros continue in the same contiguous namespace sections.

## Control Flow

This header has no branches, calls, or runtime control flow. The effective flow is build-time and probe-time: DTS sources include the constants, the device-tree compiler stores the resulting integers in clock/reset/power-domain specifier cells, and the Qualcomm clock-controller driver exposes provider arrays whose indexes must match these values. Consumer drivers later resolve those phandles through common clock, reset-controller, or genpd APIs.

## State and Persistence Behavior

The file owns no memory, locks, hardware registers, or persistent storage. Its state is the ABI value assigned to each macro. Those values persist in compiled DTBs and out-of-tree device trees, so renumbering or deleting an existing define is a compatibility break even though no runtime state is stored here. Actual enable counts, reset assertion state, and GDSC power state are maintained by the clock/reset/power-domain drivers and hardware registers, not by this header.

## Dependencies and Integration Points

Direct source dependencies are intentionally minimal: the header has only SPDX/copyright comments, an include guard, macro definitions, and `#endif`. It is integrated by textual inclusion rather than linking. Local integration evidence: clock-controller driver references: `sources/distributed-fs/ceph-client/drivers/clk/qcom/videocc-milos.c`.

The semantic dependency is the matching provider implementation and its descriptor arrays. `qcom,milos-videocc.h` IDs must stay aligned with driver tables for video codec MVS/MVS0/MVS1, AHB, AXI, sleep/XO, reset, and GDSC IDs. DTS consumers depend on these exact constants for properties such as `clocks`, `resets`, `power-domains`, and named clock inputs.

## Risks and Edge Cases

The main risk is ABI drift: inserting new IDs in the middle, reusing a removed value, or moving a reset/GDSC ID to a different number can silently bind a DTS consumer to the wrong hardware clock or power domain. It also exports reset IDs (`VIDEO_CC_INTERFACE_BCR`=0 through `VIDEO_CC_MVS0C_BCR`=3). Power-domain/GDSC IDs are exported as `VIDEO_CC_MVS0_GDSC`=0 through `VIDEO_CC_MVS0C_GDSC`=1. Shared names such as PLLs, XO/sleep sources, bus clocks, and GDSCs are easy to copy between SoCs, but the numeric ordering must follow this specific provider, not a visually similar controller. Because the file is pure macros, the compiler provides little semantic checking beyond duplicate definitions and include-guard correctness.

## Test Signals

Useful validation includes building the relevant `drivers/clk/qcom` object with this header, compiling DTBs that include `qcom,milos-videocc.h`, and running `dtbs_check`/binding-schema checks for the affected SoC. Runtime smoke tests are provider probe success without missing clock/reset IDs, absence of `-ENOENT`/`-EINVAL` from clock lookups, expected entries under common-clock debugfs, and successful bring-up of consumers in the exported domain set: video codec MVS/MVS0/MVS1, AHB, AXI, sleep/XO, reset, and GDSC IDs. For edits, diff the numeric table against the matching driver arrays and boot at least one DTS consumer when local hardware or emulation coverage exists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,milos-videocc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,mmcc-apq8084.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,mmcc-apq8084.h

## Purpose

`sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,mmcc-apq8084.h` defines the public device-tree numeric IDs for the Qualcomm legacy multimedia clock-controller binding associated with `qcom,mmcc-apq8084.h` / `mmcc`. The source was read completely for this report (185 lines). It is not executable kernel code; it is a stable binding contract included by DTS files and by the matching `drivers/clk/qcom` provider so that phandle clock, reset, and power-domain specifiers use the same indexes.

## Important APIs, Types, and Functions

There are no C functions, structs, or runtime APIs. The exported API is a set of preprocessor constants guarded by `_DT_BINDINGS_CLK_APQ_MMCC_8084_H`. This header defines 165 clock IDs, 0 reset IDs, and 8 power-domain/GDSC IDs, for 173 numeric binding macros total.

Clock ID range: `MMSS_AHB_CLK_SRC`=0 through `VPU_VDP_CLK`=164. Representative clocks: `MMSS_AHB_CLK_SRC`, `MMSS_AXI_CLK_SRC`, `MMPLL0`, `MMPLL0_VOTE`, `MMPLL1`, `MMPLL1_VOTE`, ... `VPU_AXI_CLK`, `VPU_BUS_CLK`, `VPU_CXO_CLK`, `VPU_MAPLE_CLK`, `VPU_SLEEP_CLK`, `VPU_VDP_CLK`.

Reset ID range: none. Representative resets: none.

Power-domain/GDSC range: `VENUS0_GDSC`=0 through `OXILICX_GDSC`=7. Representative domains: `VENUS0_GDSC`, `VENUS0_CORE0_GDSC`, `VENUS0_CORE1_GDSC`, `MDSS_GDSC`, `CAMSS_JPEG_GDSC`, `CAMSS_VFE_GDSC`, `OXILI_GDSC`, `OXILICX_GDSC`.

Macro inventory begins with:
- `MMSS_AHB_CLK_SRC` = 0 (clock, line 9)
- `MMSS_AXI_CLK_SRC` = 1 (clock, line 10)
- `MMPLL0` = 2 (clock, line 11)
- `MMPLL0_VOTE` = 3 (clock, line 12)
- `MMPLL1` = 4 (clock, line 13)
- `MMPLL1_VOTE` = 5 (clock, line 14)
- `MMPLL2` = 6 (clock, line 15)
- `MMPLL3` = 7 (clock, line 16)
- `MMPLL4` = 8 (clock, line 17)
- `CSI0_CLK_SRC` = 9 (clock, line 18)
- ... 163 additional numeric binding macros continue in the same contiguous namespace sections.

## Control Flow

This header has no branches, calls, or runtime control flow. The effective flow is build-time and probe-time: DTS sources include the constants, the device-tree compiler stores the resulting integers in clock/reset/power-domain specifier cells, and the Qualcomm clock-controller driver exposes provider arrays whose indexes must match these values. Consumer drivers later resolve those phandles through common clock, reset-controller, or genpd APIs.

## State and Persistence Behavior

The file owns no memory, locks, hardware registers, or persistent storage. Its state is the ABI value assigned to each macro. Those values persist in compiled DTBs and out-of-tree device trees, so renumbering or deleting an existing define is a compatibility break even though no runtime state is stored here. Actual enable counts, reset assertion state, and GDSC power state are maintained by the clock/reset/power-domain drivers and hardware registers, not by this header.

## Dependencies and Integration Points

Direct source dependencies are intentionally minimal: the header has only SPDX/copyright comments, an include guard, macro definitions, and `#endif`. It is integrated by textual inclusion rather than linking. Local integration evidence: clock-controller driver references: `sources/distributed-fs/ceph-client/drivers/clk/qcom/mmcc-apq8084.c`.

The semantic dependency is the matching provider implementation and its descriptor arrays. `qcom,mmcc-apq8084.h` IDs must stay aligned with driver tables for camera, display, JPEG/VFE/CSI, MDSS, HDMI/eDP/DSI, GPU/OCMEM, video codec, multimedia AXI/AHB, and MMSS GDSC IDs. DTS consumers depend on these exact constants for properties such as `clocks`, `resets`, `power-domains`, and named clock inputs.

## Risks and Edge Cases

The main risk is ABI drift: inserting new IDs in the middle, reusing a removed value, or moving a reset/GDSC ID to a different number can silently bind a DTS consumer to the wrong hardware clock or power domain. It does not export reset IDs in this clock header; reset bindings are either absent for this controller or live in a paired reset binding header/driver table. Power-domain/GDSC IDs are exported as `VENUS0_GDSC`=0 through `OXILICX_GDSC`=7. Shared names such as PLLs, XO/sleep sources, bus clocks, and GDSCs are easy to copy between SoCs, but the numeric ordering must follow this specific provider, not a visually similar controller. Because the file is pure macros, the compiler provides little semantic checking beyond duplicate definitions and include-guard correctness.

## Test Signals

Useful validation includes building the relevant `drivers/clk/qcom` object with this header, compiling DTBs that include `qcom,mmcc-apq8084.h`, and running `dtbs_check`/binding-schema checks for the affected SoC. Runtime smoke tests are provider probe success without missing clock/reset IDs, absence of `-ENOENT`/`-EINVAL` from clock lookups, expected entries under common-clock debugfs, and successful bring-up of consumers in the exported domain set: camera, display, JPEG/VFE/CSI, MDSS, HDMI/eDP/DSI, GPU/OCMEM, video codec, multimedia AXI/AHB, and MMSS GDSC IDs. For edits, diff the numeric table against the matching driver arrays and boot at least one DTS consumer when local hardware or emulation coverage exists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,mmcc-apq8084.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,mmcc-msm8960.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,mmcc-msm8960.h

## Purpose

`sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,mmcc-msm8960.h` defines the public device-tree numeric IDs for the Qualcomm legacy multimedia clock-controller binding associated with `qcom,mmcc-msm8960.h` / `mmcc`. The source was read completely for this report (139 lines). It is not executable kernel code; it is a stable binding contract included by DTS files and by the matching `drivers/clk/qcom` provider so that phandle clock, reset, and power-domain specifiers use the same indexes.

## Important APIs, Types, and Functions

There are no C functions, structs, or runtime APIs. The exported API is a set of preprocessor constants guarded by `_DT_BINDINGS_CLK_MSM_MMCC_8960_H`. This header defines 129 clock IDs, 0 reset IDs, and 0 power-domain/GDSC IDs, for 129 numeric binding macros total.

Clock ID range: `MMSS_AHB_SRC`=0 through `LVDS_CLK`=128. Representative clocks: `MMSS_AHB_SRC`, `FAB_AHB_CLK`, `APU_AHB_CLK`, `TV_ENC_AHB_CLK`, `AMP_AHB_CLK`, `DSI2_S_AHB_CLK`, ... `VCAP_SRC`, `VCAP_CLK`, `VCAP_NPL_CLK`, `PLL15`, `DSI2_PIXEL_LVDS_SRC`, `LVDS_CLK`.

Reset ID range: none. Representative resets: none.

Power-domain/GDSC range: none. Representative domains: none.

Macro inventory begins with:
- `MMSS_AHB_SRC` = 0 (clock, line 9)
- `FAB_AHB_CLK` = 1 (clock, line 10)
- `APU_AHB_CLK` = 2 (clock, line 11)
- `TV_ENC_AHB_CLK` = 3 (clock, line 12)
- `AMP_AHB_CLK` = 4 (clock, line 13)
- `DSI2_S_AHB_CLK` = 5 (clock, line 14)
- `JPEGD_AHB_CLK` = 6 (clock, line 15)
- `GFX2D0_AHB_CLK` = 7 (clock, line 16)
- `DSI_S_AHB_CLK` = 8 (clock, line 17)
- `DSI2_M_AHB_CLK` = 9 (clock, line 18)
- ... 119 additional numeric binding macros continue in the same contiguous namespace sections.

## Control Flow

This header has no branches, calls, or runtime control flow. The effective flow is build-time and probe-time: DTS sources include the constants, the device-tree compiler stores the resulting integers in clock/reset/power-domain specifier cells, and the Qualcomm clock-controller driver exposes provider arrays whose indexes must match these values. Consumer drivers later resolve those phandles through common clock, reset-controller, or genpd APIs.

## State and Persistence Behavior

The file owns no memory, locks, hardware registers, or persistent storage. Its state is the ABI value assigned to each macro. Those values persist in compiled DTBs and out-of-tree device trees, so renumbering or deleting an existing define is a compatibility break even though no runtime state is stored here. Actual enable counts, reset assertion state, and GDSC power state are maintained by the clock/reset/power-domain drivers and hardware registers, not by this header.

## Dependencies and Integration Points

Direct source dependencies are intentionally minimal: the header has only SPDX/copyright comments, an include guard, macro definitions, and `#endif`. It is integrated by textual inclusion rather than linking. Local integration evidence: clock-controller driver references: `sources/distributed-fs/ceph-client/drivers/clk/qcom/mmcc-msm8960.c`; device-tree references: `sources/distributed-fs/ceph-client/arch/arm/boot/dts/qcom/qcom-apq8064.dtsi`.

The semantic dependency is the matching provider implementation and its descriptor arrays. `qcom,mmcc-msm8960.h` IDs must stay aligned with driver tables for camera, display, JPEG/VFE/CSI, MDSS, HDMI/eDP/DSI, GPU/OCMEM, video codec, multimedia AXI/AHB, and MMSS GDSC IDs. DTS consumers depend on these exact constants for properties such as `clocks`, `resets`, `power-domains`, and named clock inputs.

## Risks and Edge Cases

The main risk is ABI drift: inserting new IDs in the middle, reusing a removed value, or moving a reset/GDSC ID to a different number can silently bind a DTS consumer to the wrong hardware clock or power domain. It does not export reset IDs in this clock header; reset bindings are either absent for this controller or live in a paired reset binding header/driver table. It does not export GDSC or power-domain IDs. Shared names such as PLLs, XO/sleep sources, bus clocks, and GDSCs are easy to copy between SoCs, but the numeric ordering must follow this specific provider, not a visually similar controller. Because the file is pure macros, the compiler provides little semantic checking beyond duplicate definitions and include-guard correctness.

## Test Signals

Useful validation includes building the relevant `drivers/clk/qcom` object with this header, compiling DTBs that include `qcom,mmcc-msm8960.h`, and running `dtbs_check`/binding-schema checks for the affected SoC. Runtime smoke tests are provider probe success without missing clock/reset IDs, absence of `-ENOENT`/`-EINVAL` from clock lookups, expected entries under common-clock debugfs, and successful bring-up of consumers in the exported domain set: camera, display, JPEG/VFE/CSI, MDSS, HDMI/eDP/DSI, GPU/OCMEM, video codec, multimedia AXI/AHB, and MMSS GDSC IDs. For edits, diff the numeric table against the matching driver arrays and boot at least one DTS consumer when local hardware or emulation coverage exists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,mmcc-msm8960.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,mmcc-msm8974.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,mmcc-msm8974.h

## Purpose

`sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,mmcc-msm8974.h` defines the public device-tree numeric IDs for the Qualcomm legacy multimedia clock-controller binding associated with `qcom,mmcc-msm8974.h` / `mmcc`. The source was read completely for this report (160 lines). It is not executable kernel code; it is a stable binding contract included by DTS files and by the matching `drivers/clk/qcom` provider so that phandle clock, reset, and power-domain specifiers use the same indexes. This header is shared by multiple DTS or driver consumers in this tree, so numeric stability matters beyond one board file.

## Important APIs, Types, and Functions

There are no C functions, structs, or runtime APIs. The exported API is a set of preprocessor constants guarded by `_DT_BINDINGS_CLK_MSM_MMCC_8974_H`. This header defines 142 clock IDs, 0 reset IDs, and 6 power-domain/GDSC IDs, for 148 numeric binding macros total.

Clock ID range: `MMSS_AHB_CLK_SRC`=0 through `SPDM_RM_OCMEMNOC`=142. Representative clocks: `MMSS_AHB_CLK_SRC`, `MMSS_AXI_CLK_SRC`, `MMPLL0`, `MMPLL0_VOTE`, `MMPLL1`, `MMPLL1_VOTE`, ... `SPDM_AHB`, `SPDM_PCLK0`, `SPDM_OCMEMNOC`, `SPDM_CSI0`, `SPDM_RM_AXI`, `SPDM_RM_OCMEMNOC`.

Reset ID range: none. Representative resets: none.

Power-domain/GDSC range: `VENUS0_GDSC`=0 through `OXILICX_GDSC`=5. Representative domains: `VENUS0_GDSC`, `MDSS_GDSC`, `CAMSS_JPEG_GDSC`, `CAMSS_VFE_GDSC`, `OXILI_GDSC`, `OXILICX_GDSC`.

Macro inventory begins with:
- `MMSS_AHB_CLK_SRC` = 0 (clock, line 9)
- `MMSS_AXI_CLK_SRC` = 1 (clock, line 10)
- `MMPLL0` = 2 (clock, line 11)
- `MMPLL0_VOTE` = 3 (clock, line 12)
- `MMPLL1` = 4 (clock, line 13)
- `MMPLL1_VOTE` = 5 (clock, line 14)
- `MMPLL2` = 6 (clock, line 15)
- `MMPLL3` = 7 (clock, line 16)
- `CSI0_CLK_SRC` = 8 (clock, line 17)
- `CSI1_CLK_SRC` = 9 (clock, line 18)
- ... 138 additional numeric binding macros continue in the same contiguous namespace sections.

## Control Flow

This header has no branches, calls, or runtime control flow. The effective flow is build-time and probe-time: DTS sources include the constants, the device-tree compiler stores the resulting integers in clock/reset/power-domain specifier cells, and the Qualcomm clock-controller driver exposes provider arrays whose indexes must match these values. Consumer drivers later resolve those phandles through common clock, reset-controller, or genpd APIs.

## State and Persistence Behavior

The file owns no memory, locks, hardware registers, or persistent storage. Its state is the ABI value assigned to each macro. Those values persist in compiled DTBs and out-of-tree device trees, so renumbering or deleting an existing define is a compatibility break even though no runtime state is stored here. Actual enable counts, reset assertion state, and GDSC power state are maintained by the clock/reset/power-domain drivers and hardware registers, not by this header.

## Dependencies and Integration Points

Direct source dependencies are intentionally minimal: the header has only SPDX/copyright comments, an include guard, macro definitions, and `#endif`. It is integrated by textual inclusion rather than linking. Local integration evidence: clock-controller driver references: `sources/distributed-fs/ceph-client/drivers/clk/qcom/mmcc-msm8974.c`; device-tree references: `sources/distributed-fs/ceph-client/arch/arm/boot/dts/qcom/qcom-msm8974.dtsi`, `sources/distributed-fs/ceph-client/arch/arm/boot/dts/qcom/qcom-msm8226.dtsi`, `sources/distributed-fs/ceph-client/arch/arm/boot/dts/qcom/qcom-apq8026-lg-lenok.dts`.

The semantic dependency is the matching provider implementation and its descriptor arrays. `qcom,mmcc-msm8974.h` IDs must stay aligned with driver tables for camera, display, JPEG/VFE/CSI, MDSS, HDMI/eDP/DSI, GPU/OCMEM, video codec, multimedia AXI/AHB, and MMSS GDSC IDs. DTS consumers depend on these exact constants for properties such as `clocks`, `resets`, `power-domains`, and named clock inputs.

## Risks and Edge Cases

The main risk is ABI drift: inserting new IDs in the middle, reusing a removed value, or moving a reset/GDSC ID to a different number can silently bind a DTS consumer to the wrong hardware clock or power domain. It does not export reset IDs in this clock header; reset bindings are either absent for this controller or live in a paired reset binding header/driver table. Power-domain/GDSC IDs are exported as `VENUS0_GDSC`=0 through `OXILICX_GDSC`=5. Shared names such as PLLs, XO/sleep sources, bus clocks, and GDSCs are easy to copy between SoCs, but the numeric ordering must follow this specific provider, not a visually similar controller. Because the file is pure macros, the compiler provides little semantic checking beyond duplicate definitions and include-guard correctness.

## Test Signals

Useful validation includes building the relevant `drivers/clk/qcom` object with this header, compiling DTBs that include `qcom,mmcc-msm8974.h`, and running `dtbs_check`/binding-schema checks for the affected SoC. Runtime smoke tests are provider probe success without missing clock/reset IDs, absence of `-ENOENT`/`-EINVAL` from clock lookups, expected entries under common-clock debugfs, and successful bring-up of consumers in the exported domain set: camera, display, JPEG/VFE/CSI, MDSS, HDMI/eDP/DSI, GPU/OCMEM, video codec, multimedia AXI/AHB, and MMSS GDSC IDs. For edits, diff the numeric table against the matching driver arrays and boot at least one DTS consumer when local hardware or emulation coverage exists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,mmcc-msm8974.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,mmcc-msm8994.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,mmcc-msm8994.h

## Purpose

`sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,mmcc-msm8994.h` defines the public device-tree numeric IDs for the Qualcomm legacy multimedia clock-controller binding associated with `qcom,mmcc-msm8994.h` / `mmcc`. The source was read completely for this report (155 lines). It is not executable kernel code; it is a stable binding contract included by DTS files and by the matching `drivers/clk/qcom` provider so that phandle clock, reset, and power-domain specifiers use the same indexes.

## Important APIs, Types, and Functions

There are no C functions, structs, or runtime APIs. The exported API is a set of preprocessor constants guarded by `_DT_BINDINGS_CLK_MSM_MMCC_8994_H`. This header defines 127 clock IDs, 1 reset ID, and 12 power-domain/GDSC IDs, for 140 numeric binding macros total.

Clock ID range: `MMPLL0_EARLY`=0 through `FD_AHB_CLK`=126. Representative clocks: `MMPLL0_EARLY`, `MMPLL0_PLL`, `MMPLL1_EARLY`, `MMPLL1_PLL`, `MMPLL3_EARLY`, `MMPLL3_PLL`, ... `VENUS0_VCODEC0_CLK`, `VENUS0_CORE0_VCODEC_CLK`, `VENUS0_CORE1_VCODEC_CLK`, `VENUS0_CORE2_VCODEC_CLK`, `AHB_CLK_SRC`, `FD_AHB_CLK`.

Reset ID range: `CAMSS_MICRO_BCR`=0 through `CAMSS_MICRO_BCR`=0. Representative resets: `CAMSS_MICRO_BCR`.

Power-domain/GDSC range: `VENUS_GDSC`=0 through `FD_GDSC`=11. Representative domains: `VENUS_GDSC`, `VENUS_CORE0_GDSC`, `VENUS_CORE1_GDSC`, `VENUS_CORE2_GDSC`, `CAMSS_TOP_GDSC`, `MDSS_GDSC`, `JPEG_GDSC`, `VFE_GDSC`, `CPP_GDSC`, `OXILI_GX_GDSC`, `OXILI_CX_GDSC`, `FD_GDSC`.

Macro inventory begins with:
- `MMPLL0_EARLY` = 0 (clock, line 10)
- `MMPLL0_PLL` = 1 (clock, line 11)
- `MMPLL1_EARLY` = 2 (clock, line 12)
- `MMPLL1_PLL` = 3 (clock, line 13)
- `MMPLL3_EARLY` = 4 (clock, line 14)
- `MMPLL3_PLL` = 5 (clock, line 15)
- `MMPLL4_EARLY` = 6 (clock, line 16)
- `MMPLL4_PLL` = 7 (clock, line 17)
- `MMPLL5_EARLY` = 8 (clock, line 18)
- `MMPLL5_PLL` = 9 (clock, line 19)
- ... 130 additional numeric binding macros continue in the same contiguous namespace sections.

## Control Flow

This header has no branches, calls, or runtime control flow. The effective flow is build-time and probe-time: DTS sources include the constants, the device-tree compiler stores the resulting integers in clock/reset/power-domain specifier cells, and the Qualcomm clock-controller driver exposes provider arrays whose indexes must match these values. Consumer drivers later resolve those phandles through common clock, reset-controller, or genpd APIs.

## State and Persistence Behavior

The file owns no memory, locks, hardware registers, or persistent storage. Its state is the ABI value assigned to each macro. Those values persist in compiled DTBs and out-of-tree device trees, so renumbering or deleting an existing define is a compatibility break even though no runtime state is stored here. Actual enable counts, reset assertion state, and GDSC power state are maintained by the clock/reset/power-domain drivers and hardware registers, not by this header.

## Dependencies and Integration Points

Direct source dependencies are intentionally minimal: the header has only SPDX/copyright comments, an include guard, macro definitions, and `#endif`. It is integrated by textual inclusion rather than linking. Local integration evidence: clock-controller driver references: `sources/distributed-fs/ceph-client/drivers/clk/qcom/mmcc-msm8994.c`; device-tree references: `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/msm8994.dtsi`.

The semantic dependency is the matching provider implementation and its descriptor arrays. `qcom,mmcc-msm8994.h` IDs must stay aligned with driver tables for camera, display, JPEG/VFE/CSI, MDSS, HDMI/eDP/DSI, GPU/OCMEM, video codec, multimedia AXI/AHB, and MMSS GDSC IDs. DTS consumers depend on these exact constants for properties such as `clocks`, `resets`, `power-domains`, and named clock inputs.

## Risks and Edge Cases

The main risk is ABI drift: inserting new IDs in the middle, reusing a removed value, or moving a reset/GDSC ID to a different number can silently bind a DTS consumer to the wrong hardware clock or power domain. It also exports reset IDs (`CAMSS_MICRO_BCR`=0 through `CAMSS_MICRO_BCR`=0). Power-domain/GDSC IDs are exported as `VENUS_GDSC`=0 through `FD_GDSC`=11. Shared names such as PLLs, XO/sleep sources, bus clocks, and GDSCs are easy to copy between SoCs, but the numeric ordering must follow this specific provider, not a visually similar controller. Because the file is pure macros, the compiler provides little semantic checking beyond duplicate definitions and include-guard correctness.

## Test Signals

Useful validation includes building the relevant `drivers/clk/qcom` object with this header, compiling DTBs that include `qcom,mmcc-msm8994.h`, and running `dtbs_check`/binding-schema checks for the affected SoC. Runtime smoke tests are provider probe success without missing clock/reset IDs, absence of `-ENOENT`/`-EINVAL` from clock lookups, expected entries under common-clock debugfs, and successful bring-up of consumers in the exported domain set: camera, display, JPEG/VFE/CSI, MDSS, HDMI/eDP/DSI, GPU/OCMEM, video codec, multimedia AXI/AHB, and MMSS GDSC IDs. For edits, diff the numeric table against the matching driver arrays and boot at least one DTS consumer when local hardware or emulation coverage exists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,mmcc-msm8994.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,mmcc-msm8996.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,mmcc-msm8996.h

## Purpose

`sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,mmcc-msm8996.h` defines the public device-tree numeric IDs for the Qualcomm legacy multimedia clock-controller binding associated with `qcom,mmcc-msm8996.h` / `mmcc`. The source was read completely for this report (295 lines). It is not executable kernel code; it is a stable binding contract included by DTS files and by the matching `drivers/clk/qcom` provider so that phandle clock, reset, and power-domain specifiers use the same indexes.

## Important APIs, Types, and Functions

There are no C functions, structs, or runtime APIs. The exported API is a set of preprocessor constants guarded by `_DT_BINDINGS_CLK_MSM_MMCC_8996_H`. This header defines 206 clock IDs, 60 reset IDs, and 16 power-domain/GDSC IDs, for 282 numeric binding macros total.

Clock ID range: `MMPLL0_EARLY`=0 through `MMSS_SPDM_RM_MAXI_CLK`=205. Representative clocks: `MMPLL0_EARLY`, `MMPLL0_PLL`, `MMPLL1_EARLY`, `MMPLL1_PLL`, `MMPLL2_EARLY`, `MMPLL2_PLL`, ... `MMSS_SPDM_VIDEO_CORE_CLK`, `MMSS_SPDM_AXI_CLK`, `MMSS_SPDM_MDP_CLK`, `MMSS_SPDM_JPEG0_CLK`, `MMSS_SPDM_RM_AXI_CLK`, `MMSS_SPDM_RM_MAXI_CLK`.

Reset ID range: `MMAGICAHB_BCR`=0 through `MMSS_SPDM_RM_BCR`=59. Representative resets: `MMAGICAHB_BCR`, `MMAGIC_CFG_BCR`, `MISC_BCR`, `BTO_BCR`, `MMAGICAXI_BCR`, `MMAGICMAXI_BCR`, ... `CAMSS_CSI3_BCR`, `CAMSS_CSI3RDI_BCR`, `CAMSS_CSI3PIX_BCR`, `CAMSS_ISPIF_BCR`, `FD_BCR`, `MMSS_SPDM_RM_BCR`.

Power-domain/GDSC range: `MMAGIC_VIDEO_GDSC`=0 through `MMAGIC_BIMC_GDSC`=15. Representative domains: `MMAGIC_VIDEO_GDSC`, `MMAGIC_MDSS_GDSC`, `MMAGIC_CAMSS_GDSC`, `GPU_GDSC`, `VENUS_GDSC`, `VENUS_CORE0_GDSC`, ... `JPEG_GDSC`, `CPP_GDSC`, `FD_GDSC`, `MDSS_GDSC`, `GPU_GX_GDSC`, `MMAGIC_BIMC_GDSC`.

Macro inventory begins with:
- `MMPLL0_EARLY` = 0 (clock, line 9)
- `MMPLL0_PLL` = 1 (clock, line 10)
- `MMPLL1_EARLY` = 2 (clock, line 11)
- `MMPLL1_PLL` = 3 (clock, line 12)
- `MMPLL2_EARLY` = 4 (clock, line 13)
- `MMPLL2_PLL` = 5 (clock, line 14)
- `MMPLL3_EARLY` = 6 (clock, line 15)
- `MMPLL3_PLL` = 7 (clock, line 16)
- `MMPLL4_EARLY` = 8 (clock, line 17)
- `MMPLL4_PLL` = 9 (clock, line 18)
- ... 272 additional numeric binding macros continue in the same contiguous namespace sections.

## Control Flow

This header has no branches, calls, or runtime control flow. The effective flow is build-time and probe-time: DTS sources include the constants, the device-tree compiler stores the resulting integers in clock/reset/power-domain specifier cells, and the Qualcomm clock-controller driver exposes provider arrays whose indexes must match these values. Consumer drivers later resolve those phandles through common clock, reset-controller, or genpd APIs.

## State and Persistence Behavior

The file owns no memory, locks, hardware registers, or persistent storage. Its state is the ABI value assigned to each macro. Those values persist in compiled DTBs and out-of-tree device trees, so renumbering or deleting an existing define is a compatibility break even though no runtime state is stored here. Actual enable counts, reset assertion state, and GDSC power state are maintained by the clock/reset/power-domain drivers and hardware registers, not by this header.

## Dependencies and Integration Points

Direct source dependencies are intentionally minimal: the header has only SPDX/copyright comments, an include guard, macro definitions, and `#endif`. It is integrated by textual inclusion rather than linking. Local integration evidence: clock-controller driver references: `sources/distributed-fs/ceph-client/drivers/clk/qcom/mmcc-msm8996.c`; device-tree references: `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/msm8996.dtsi`.

The semantic dependency is the matching provider implementation and its descriptor arrays. `qcom,mmcc-msm8996.h` IDs must stay aligned with driver tables for camera, display, JPEG/VFE/CSI, MDSS, HDMI/eDP/DSI, GPU/OCMEM, video codec, multimedia AXI/AHB, and MMSS GDSC IDs. DTS consumers depend on these exact constants for properties such as `clocks`, `resets`, `power-domains`, and named clock inputs.

## Risks and Edge Cases

The main risk is ABI drift: inserting new IDs in the middle, reusing a removed value, or moving a reset/GDSC ID to a different number can silently bind a DTS consumer to the wrong hardware clock or power domain. It also exports reset IDs (`MMAGICAHB_BCR`=0 through `MMSS_SPDM_RM_BCR`=59). Power-domain/GDSC IDs are exported as `MMAGIC_VIDEO_GDSC`=0 through `MMAGIC_BIMC_GDSC`=15. Shared names such as PLLs, XO/sleep sources, bus clocks, and GDSCs are easy to copy between SoCs, but the numeric ordering must follow this specific provider, not a visually similar controller. Because the file is pure macros, the compiler provides little semantic checking beyond duplicate definitions and include-guard correctness.

## Test Signals

Useful validation includes building the relevant `drivers/clk/qcom` object with this header, compiling DTBs that include `qcom,mmcc-msm8996.h`, and running `dtbs_check`/binding-schema checks for the affected SoC. Runtime smoke tests are provider probe success without missing clock/reset IDs, absence of `-ENOENT`/`-EINVAL` from clock lookups, expected entries under common-clock debugfs, and successful bring-up of consumers in the exported domain set: camera, display, JPEG/VFE/CSI, MDSS, HDMI/eDP/DSI, GPU/OCMEM, video codec, multimedia AXI/AHB, and MMSS GDSC IDs. For edits, diff the numeric table against the matching driver arrays and boot at least one DTS consumer when local hardware or emulation coverage exists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,mmcc-msm8996.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,mmcc-msm8998.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,mmcc-msm8998.h

## Purpose

`sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,mmcc-msm8998.h` defines the public device-tree numeric IDs for the Qualcomm legacy multimedia clock-controller binding associated with `qcom,mmcc-msm8998.h` / `mmcc`. The source was read completely for this report (210 lines). It is not executable kernel code; it is a stable binding contract included by DTS files and by the matching `drivers/clk/qcom` provider so that phandle clock, reset, and power-domain specifiers use the same indexes.

## Important APIs, Types, and Functions

There are no C functions, structs, or runtime APIs. The exported API is a set of preprocessor constants guarded by `_DT_BINDINGS_CLK_MSM_MMCC_8998_H`. This header defines 146 clock IDs, 43 reset IDs, and 9 power-domain/GDSC IDs, for 198 numeric binding macros total.

Clock ID range: `MMPLL0`=0 through `VMEM_AHB_CLK`=145. Representative clocks: `MMPLL0`, `MMPLL0_OUT_EVEN`, `MMPLL1`, `MMPLL1_OUT_EVEN`, `MMPLL3`, `MMPLL3_OUT_EVEN`, ... `MNOC_AHB_CLK`, `BIMC_SMMU_AHB_CLK`, `BIMC_SMMU_AXI_CLK`, `MNOC_MAXI_CLK`, `VMEM_MAXI_CLK`, `VMEM_AHB_CLK`.

Reset ID range: `SPDM_BCR`=0 through `BTO_BCR`=42. Representative resets: `SPDM_BCR`, `SPDM_RM_BCR`, `MISC_BCR`, `VIDEO_TOP_BCR`, `THROTTLE_VIDEO_BCR`, `MDSS_BCR`, ... `MNOCAHB_BCR`, `MNOCAXI_BCR`, `BMIC_SMMU_BCR`, `MNOC_MAXI_BCR`, `VMEM_BCR`, `BTO_BCR`.

Power-domain/GDSC range: `VIDEO_TOP_GDSC`=1 through `BIMC_SMMU_GDSC`=9. Representative domains: `VIDEO_TOP_GDSC`, `VIDEO_SUBCORE0_GDSC`, `VIDEO_SUBCORE1_GDSC`, `MDSS_GDSC`, `CAMSS_TOP_GDSC`, `CAMSS_VFE0_GDSC`, `CAMSS_VFE1_GDSC`, `CAMSS_CPP_GDSC`, `BIMC_SMMU_GDSC`.

Macro inventory begins with:
- `MMPLL0` = 0 (clock, line 9)
- `MMPLL0_OUT_EVEN` = 1 (clock, line 10)
- `MMPLL1` = 2 (clock, line 11)
- `MMPLL1_OUT_EVEN` = 3 (clock, line 12)
- `MMPLL3` = 4 (clock, line 13)
- `MMPLL3_OUT_EVEN` = 5 (clock, line 14)
- `MMPLL4` = 6 (clock, line 15)
- `MMPLL4_OUT_EVEN` = 7 (clock, line 16)
- `MMPLL5` = 8 (clock, line 17)
- `MMPLL5_OUT_EVEN` = 9 (clock, line 18)
- ... 188 additional numeric binding macros continue in the same contiguous namespace sections.

## Control Flow

This header has no branches, calls, or runtime control flow. The effective flow is build-time and probe-time: DTS sources include the constants, the device-tree compiler stores the resulting integers in clock/reset/power-domain specifier cells, and the Qualcomm clock-controller driver exposes provider arrays whose indexes must match these values. Consumer drivers later resolve those phandles through common clock, reset-controller, or genpd APIs.

## State and Persistence Behavior

The file owns no memory, locks, hardware registers, or persistent storage. Its state is the ABI value assigned to each macro. Those values persist in compiled DTBs and out-of-tree device trees, so renumbering or deleting an existing define is a compatibility break even though no runtime state is stored here. Actual enable counts, reset assertion state, and GDSC power state are maintained by the clock/reset/power-domain drivers and hardware registers, not by this header.

## Dependencies and Integration Points

Direct source dependencies are intentionally minimal: the header has only SPDX/copyright comments, an include guard, macro definitions, and `#endif`. It is integrated by textual inclusion rather than linking. Local integration evidence: clock-controller driver references: `sources/distributed-fs/ceph-client/drivers/clk/qcom/mmcc-msm8998.c`; device-tree references: `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/msm8998.dtsi`.

The semantic dependency is the matching provider implementation and its descriptor arrays. `qcom,mmcc-msm8998.h` IDs must stay aligned with driver tables for camera, display, JPEG/VFE/CSI, MDSS, HDMI/eDP/DSI, GPU/OCMEM, video codec, multimedia AXI/AHB, and MMSS GDSC IDs. DTS consumers depend on these exact constants for properties such as `clocks`, `resets`, `power-domains`, and named clock inputs.

## Risks and Edge Cases

The main risk is ABI drift: inserting new IDs in the middle, reusing a removed value, or moving a reset/GDSC ID to a different number can silently bind a DTS consumer to the wrong hardware clock or power domain. It also exports reset IDs (`SPDM_BCR`=0 through `BTO_BCR`=42). Power-domain/GDSC IDs are exported as `VIDEO_TOP_GDSC`=1 through `BIMC_SMMU_GDSC`=9. Shared names such as PLLs, XO/sleep sources, bus clocks, and GDSCs are easy to copy between SoCs, but the numeric ordering must follow this specific provider, not a visually similar controller. Because the file is pure macros, the compiler provides little semantic checking beyond duplicate definitions and include-guard correctness.

## Test Signals

Useful validation includes building the relevant `drivers/clk/qcom` object with this header, compiling DTBs that include `qcom,mmcc-msm8998.h`, and running `dtbs_check`/binding-schema checks for the affected SoC. Runtime smoke tests are provider probe success without missing clock/reset IDs, absence of `-ENOENT`/`-EINVAL` from clock lookups, expected entries under common-clock debugfs, and successful bring-up of consumers in the exported domain set: camera, display, JPEG/VFE/CSI, MDSS, HDMI/eDP/DSI, GPU/OCMEM, video codec, multimedia AXI/AHB, and MMSS GDSC IDs. For edits, diff the numeric table against the matching driver arrays and boot at least one DTS consumer when local hardware or emulation coverage exists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,mmcc-msm8998.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,mmcc-sdm660.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,mmcc-sdm660.h

## Purpose

`sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,mmcc-sdm660.h` defines the public device-tree numeric IDs for the Qualcomm legacy multimedia clock-controller binding associated with `qcom,mmcc-sdm660.h` / `mmcc`. The source was read completely for this report (163 lines). It is not executable kernel code; it is a stable binding contract included by DTS files and by the matching `drivers/clk/qcom` provider so that phandle clock, reset, and power-domain specifiers use the same indexes.

## Important APIs, Types, and Functions

There are no C functions, structs, or runtime APIs. The exported API is a set of preprocessor constants guarded by `_DT_BINDINGS_CLK_MSM_MMCC_660_H`. This header defines 140 clock IDs, 2 reset IDs, and 8 power-domain/GDSC IDs, for 150 numeric binding macros total.

Clock ID range: `AHB_CLK_SRC`=0 through `AXI_CLK_SRC`=139. Representative clocks: `AHB_CLK_SRC`, `BYTE0_CLK_SRC`, `BYTE1_CLK_SRC`, `CAMSS_GP0_CLK_SRC`, `CAMSS_GP1_CLK_SRC`, `CCI_CLK_SRC`, ... `VFE0_CLK_SRC`, `VFE1_CLK_SRC`, `VIDEO_CORE_CLK_SRC`, `VSYNC_CLK_SRC`, `MDSS_BYTE1_INTF_DIV_CLK`, `AXI_CLK_SRC`.

Reset ID range: `CAMSS_MICRO_BCR`=0 through `MDSS_BCR`=1. Representative resets: `CAMSS_MICRO_BCR`, `MDSS_BCR`.

Power-domain/GDSC range: `VENUS_GDSC`=0 through `BIMC_SMMU_GDSC`=7. Representative domains: `VENUS_GDSC`, `VENUS_CORE0_GDSC`, `MDSS_GDSC`, `CAMSS_TOP_GDSC`, `CAMSS_VFE0_GDSC`, `CAMSS_VFE1_GDSC`, `CAMSS_CPP_GDSC`, `BIMC_SMMU_GDSC`.

Macro inventory begins with:
- `AHB_CLK_SRC` = 0 (clock, line 9)
- `BYTE0_CLK_SRC` = 1 (clock, line 10)
- `BYTE1_CLK_SRC` = 2 (clock, line 11)
- `CAMSS_GP0_CLK_SRC` = 3 (clock, line 12)
- `CAMSS_GP1_CLK_SRC` = 4 (clock, line 13)
- `CCI_CLK_SRC` = 5 (clock, line 14)
- `CPP_CLK_SRC` = 6 (clock, line 15)
- `CSI0_CLK_SRC` = 7 (clock, line 16)
- `CSI0PHYTIMER_CLK_SRC` = 8 (clock, line 17)
- `CSI1_CLK_SRC` = 9 (clock, line 18)
- ... 140 additional numeric binding macros continue in the same contiguous namespace sections.

## Control Flow

This header has no branches, calls, or runtime control flow. The effective flow is build-time and probe-time: DTS sources include the constants, the device-tree compiler stores the resulting integers in clock/reset/power-domain specifier cells, and the Qualcomm clock-controller driver exposes provider arrays whose indexes must match these values. Consumer drivers later resolve those phandles through common clock, reset-controller, or genpd APIs.

## State and Persistence Behavior

The file owns no memory, locks, hardware registers, or persistent storage. Its state is the ABI value assigned to each macro. Those values persist in compiled DTBs and out-of-tree device trees, so renumbering or deleting an existing define is a compatibility break even though no runtime state is stored here. Actual enable counts, reset assertion state, and GDSC power state are maintained by the clock/reset/power-domain drivers and hardware registers, not by this header.

## Dependencies and Integration Points

Direct source dependencies are intentionally minimal: the header has only SPDX/copyright comments, an include guard, macro definitions, and `#endif`. It is integrated by textual inclusion rather than linking. Local integration evidence: clock-controller driver references: `sources/distributed-fs/ceph-client/drivers/clk/qcom/mmcc-sdm660.c`; device-tree references: `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/sdm630.dtsi`.

The semantic dependency is the matching provider implementation and its descriptor arrays. `qcom,mmcc-sdm660.h` IDs must stay aligned with driver tables for camera, display, JPEG/VFE/CSI, MDSS, HDMI/eDP/DSI, GPU/OCMEM, video codec, multimedia AXI/AHB, and MMSS GDSC IDs. DTS consumers depend on these exact constants for properties such as `clocks`, `resets`, `power-domains`, and named clock inputs.

## Risks and Edge Cases

The main risk is ABI drift: inserting new IDs in the middle, reusing a removed value, or moving a reset/GDSC ID to a different number can silently bind a DTS consumer to the wrong hardware clock or power domain. It also exports reset IDs (`CAMSS_MICRO_BCR`=0 through `MDSS_BCR`=1). Power-domain/GDSC IDs are exported as `VENUS_GDSC`=0 through `BIMC_SMMU_GDSC`=7. Shared names such as PLLs, XO/sleep sources, bus clocks, and GDSCs are easy to copy between SoCs, but the numeric ordering must follow this specific provider, not a visually similar controller. Because the file is pure macros, the compiler provides little semantic checking beyond duplicate definitions and include-guard correctness.

## Test Signals

Useful validation includes building the relevant `drivers/clk/qcom` object with this header, compiling DTBs that include `qcom,mmcc-sdm660.h`, and running `dtbs_check`/binding-schema checks for the affected SoC. Runtime smoke tests are provider probe success without missing clock/reset IDs, absence of `-ENOENT`/`-EINVAL` from clock lookups, expected entries under common-clock debugfs, and successful bring-up of consumers in the exported domain set: camera, display, JPEG/VFE/CSI, MDSS, HDMI/eDP/DSI, GPU/OCMEM, video codec, multimedia AXI/AHB, and MMSS GDSC IDs. For edits, diff the numeric table against the matching driver arrays and boot at least one DTS consumer when local hardware or emulation coverage exists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,mmcc-sdm660.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,nord-gcc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,nord-gcc.h

## Purpose

`sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,nord-gcc.h` defines the public device-tree numeric IDs for the Qualcomm global clock-controller binding associated with `qcom,nord-gcc.h` / `nord`. The source was read completely for this report (147 lines). It is not executable kernel code; it is a stable binding contract included by DTS files and by the matching `drivers/clk/qcom` provider so that phandle clock, reset, and power-domain specifiers use the same indexes.

## Important APIs, Types, and Functions

There are no C functions, structs, or runtime APIs. The exported API is a set of preprocessor constants guarded by `_DT_BINDINGS_CLK_QCOM_GCC_NORD_H`. This header defines 91 clock IDs, 32 reset IDs, and 9 power-domain/GDSC IDs, for 132 numeric binding macros total.

Clock ID range: `GCC_BOOT_ROM_AHB_CLK`=0 through `GCC_SMMU_PCIE_QTC_VOTE_CLK`=90. Representative clocks: `GCC_BOOT_ROM_AHB_CLK`, `GCC_GP1_CLK`, `GCC_GP1_CLK_SRC`, `GCC_GP2_CLK`, `GCC_GP2_CLK_SRC`, `GCC_GPLL0`, ... `GCC_QUPV3_WRAP3_QSPI_REF_CLK`, `GCC_QUPV3_WRAP3_QSPI_REF_CLK_SRC`, `GCC_QUPV3_WRAP3_S0_CLK`, `GCC_QUPV3_WRAP3_S0_CLK_SRC`, `GCC_QUPV3_WRAP3_S_AHB_CLK`, `GCC_SMMU_PCIE_QTC_VOTE_CLK`.

Reset ID range: `GCC_PCIE_A_BCR`=0 through `GCC_TCSR_PCIE_BCR`=31. Representative resets: `GCC_PCIE_A_BCR`, `GCC_PCIE_A_LINK_DOWN_BCR`, `GCC_PCIE_A_NOCSR_COM_PHY_BCR`, `GCC_PCIE_A_PHY_BCR`, `GCC_PCIE_A_PHY_CFG_AHB_BCR`, `GCC_PCIE_A_PHY_COM_BCR`, ... `GCC_PCIE_D_PHY_COM_BCR`, `GCC_PCIE_D_PHY_NOCSR_COM_PHY_BCR`, `GCC_PCIE_NOC_BCR`, `GCC_PDM_BCR`, `GCC_QUPV3_WRAPPER_3_BCR`, `GCC_TCSR_PCIE_BCR`.

Power-domain/GDSC range: `GCC_PCIE_A_GDSC`=0 through `GCC_PCIE_NOC_GDSC`=8. Representative domains: `GCC_PCIE_A_GDSC`, `GCC_PCIE_A_PHY_GDSC`, `GCC_PCIE_B_GDSC`, `GCC_PCIE_B_PHY_GDSC`, `GCC_PCIE_C_GDSC`, `GCC_PCIE_C_PHY_GDSC`, `GCC_PCIE_D_GDSC`, `GCC_PCIE_D_PHY_GDSC`, `GCC_PCIE_NOC_GDSC`.

Macro inventory begins with:
- `GCC_BOOT_ROM_AHB_CLK` = 0 (clock, line 10)
- `GCC_GP1_CLK` = 1 (clock, line 11)
- `GCC_GP1_CLK_SRC` = 2 (clock, line 12)
- `GCC_GP2_CLK` = 3 (clock, line 13)
- `GCC_GP2_CLK_SRC` = 4 (clock, line 14)
- `GCC_GPLL0` = 5 (clock, line 15)
- `GCC_GPLL0_OUT_EVEN` = 6 (clock, line 16)
- `GCC_MMU_0_TCU_VOTE_CLK` = 7 (clock, line 17)
- `GCC_PCIE_A_AUX_CLK` = 8 (clock, line 18)
- `GCC_PCIE_A_AUX_CLK_SRC` = 9 (clock, line 19)
- ... 122 additional numeric binding macros continue in the same contiguous namespace sections.

## Control Flow

This header has no branches, calls, or runtime control flow. The effective flow is build-time and probe-time: DTS sources include the constants, the device-tree compiler stores the resulting integers in clock/reset/power-domain specifier cells, and the Qualcomm clock-controller driver exposes provider arrays whose indexes must match these values. Consumer drivers later resolve those phandles through common clock, reset-controller, or genpd APIs.

## State and Persistence Behavior

The file owns no memory, locks, hardware registers, or persistent storage. Its state is the ABI value assigned to each macro. Those values persist in compiled DTBs and out-of-tree device trees, so renumbering or deleting an existing define is a compatibility break even though no runtime state is stored here. Actual enable counts, reset assertion state, and GDSC power state are maintained by the clock/reset/power-domain drivers and hardware registers, not by this header.

## Dependencies and Integration Points

Direct source dependencies are intentionally minimal: the header has only SPDX/copyright comments, an include guard, macro definitions, and `#endif`. It is integrated by textual inclusion rather than linking. Local integration evidence: clock-controller driver references: `sources/distributed-fs/ceph-client/drivers/clk/qcom/gcc-nord.c`.

The semantic dependency is the matching provider implementation and its descriptor arrays. `qcom,nord-gcc.h` IDs must stay aligned with driver tables for global PLLs plus bus, QUP, USB, PCIe, UFS, SDCC, camera/display/video/gpu vote, reset, and GDSC IDs. DTS consumers depend on these exact constants for properties such as `clocks`, `resets`, `power-domains`, and named clock inputs.

## Risks and Edge Cases

The main risk is ABI drift: inserting new IDs in the middle, reusing a removed value, or moving a reset/GDSC ID to a different number can silently bind a DTS consumer to the wrong hardware clock or power domain. It also exports reset IDs (`GCC_PCIE_A_BCR`=0 through `GCC_TCSR_PCIE_BCR`=31). Power-domain/GDSC IDs are exported as `GCC_PCIE_A_GDSC`=0 through `GCC_PCIE_NOC_GDSC`=8. Shared names such as PLLs, XO/sleep sources, bus clocks, and GDSCs are easy to copy between SoCs, but the numeric ordering must follow this specific provider, not a visually similar controller. Because the file is pure macros, the compiler provides little semantic checking beyond duplicate definitions and include-guard correctness.

## Test Signals

Useful validation includes building the relevant `drivers/clk/qcom` object with this header, compiling DTBs that include `qcom,nord-gcc.h`, and running `dtbs_check`/binding-schema checks for the affected SoC. Runtime smoke tests are provider probe success without missing clock/reset IDs, absence of `-ENOENT`/`-EINVAL` from clock lookups, expected entries under common-clock debugfs, and successful bring-up of consumers in the exported domain set: global PLLs plus bus, QUP, USB, PCIe, UFS, SDCC, camera/display/video/gpu vote, reset, and GDSC IDs. For edits, diff the numeric table against the matching driver arrays and boot at least one DTS consumer when local hardware or emulation coverage exists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,nord-gcc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,nord-negcc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,nord-negcc.h

## Purpose

`sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,nord-negcc.h` defines the public device-tree numeric IDs for the Qualcomm global clock-controller binding associated with `qcom,nord-negcc.h` / `nord`. The source was read completely for this report (124 lines). It is not executable kernel code; it is a stable binding contract included by DTS files and by the matching `drivers/clk/qcom` provider so that phandle clock, reset, and power-domain specifiers use the same indexes.

## Important APIs, Types, and Functions

There are no C functions, structs, or runtime APIs. The exported API is a set of preprocessor constants guarded by `_DT_BINDINGS_CLK_QCOM_NE_GCC_NORD_H`. This header defines 89 clock IDs, 13 reset IDs, and 7 power-domain/GDSC IDs, for 109 numeric binding macros total.

Clock ID range: `NE_GCC_AGGRE_NOC_UFS_PHY_AXI_CLK`=0 through `NE_GCC_USB3_SEC_PHY_PIPE_CLK_SRC`=88. Representative clocks: `NE_GCC_AGGRE_NOC_UFS_PHY_AXI_CLK`, `NE_GCC_AGGRE_NOC_USB2_AXI_CLK`, `NE_GCC_AGGRE_NOC_USB3_PRIM_AXI_CLK`, `NE_GCC_AGGRE_NOC_USB3_SEC_AXI_CLK`, `NE_GCC_AHB2PHY_CLK`, `NE_GCC_CNOC_USB2_AXI_CLK`, ... `NE_GCC_USB3_PRIM_PHY_PIPE_CLK_SRC`, `NE_GCC_USB3_SEC_PHY_AUX_CLK`, `NE_GCC_USB3_SEC_PHY_AUX_CLK_SRC`, `NE_GCC_USB3_SEC_PHY_COM_AUX_CLK`, `NE_GCC_USB3_SEC_PHY_PIPE_CLK`, `NE_GCC_USB3_SEC_PHY_PIPE_CLK_SRC`.

Reset ID range: `NE_GCC_GPU_2_BCR`=0 through `NE_GCC_USB3PHY_PHY_SEC_BCR`=12. Representative resets: `NE_GCC_GPU_2_BCR`, `NE_GCC_QUPV3_WRAPPER_2_BCR`, `NE_GCC_SDCC4_BCR`, `NE_GCC_UFS_PHY_BCR`, `NE_GCC_USB20_PRIM_BCR`, `NE_GCC_USB31_PRIM_BCR`, ... `NE_GCC_USB3_DP_PHY_PRIM_BCR`, `NE_GCC_USB3_DP_PHY_SEC_BCR`, `NE_GCC_USB3_PHY_PRIM_BCR`, `NE_GCC_USB3_PHY_SEC_BCR`, `NE_GCC_USB3PHY_PHY_PRIM_BCR`, `NE_GCC_USB3PHY_PHY_SEC_BCR`.

Power-domain/GDSC range: `NE_GCC_UFS_MEM_PHY_GDSC`=0 through `NE_GCC_USB3_SEC_PHY_GDSC`=6. Representative domains: `NE_GCC_UFS_MEM_PHY_GDSC`, `NE_GCC_UFS_PHY_GDSC`, `NE_GCC_USB20_PRIM_GDSC`, `NE_GCC_USB31_PRIM_GDSC`, `NE_GCC_USB31_SEC_GDSC`, `NE_GCC_USB3_PHY_GDSC`, `NE_GCC_USB3_SEC_PHY_GDSC`.

Macro inventory begins with:
- `NE_GCC_AGGRE_NOC_UFS_PHY_AXI_CLK` = 0 (clock, line 10)
- `NE_GCC_AGGRE_NOC_USB2_AXI_CLK` = 1 (clock, line 11)
- `NE_GCC_AGGRE_NOC_USB3_PRIM_AXI_CLK` = 2 (clock, line 12)
- `NE_GCC_AGGRE_NOC_USB3_SEC_AXI_CLK` = 3 (clock, line 13)
- `NE_GCC_AHB2PHY_CLK` = 4 (clock, line 14)
- `NE_GCC_CNOC_USB2_AXI_CLK` = 5 (clock, line 15)
- `NE_GCC_CNOC_USB3_PRIM_AXI_CLK` = 6 (clock, line 16)
- `NE_GCC_CNOC_USB3_SEC_AXI_CLK` = 7 (clock, line 17)
- `NE_GCC_FRQ_MEASURE_REF_CLK` = 8 (clock, line 18)
- `NE_GCC_GP1_CLK` = 9 (clock, line 19)
- ... 99 additional numeric binding macros continue in the same contiguous namespace sections.

## Control Flow

This header has no branches, calls, or runtime control flow. The effective flow is build-time and probe-time: DTS sources include the constants, the device-tree compiler stores the resulting integers in clock/reset/power-domain specifier cells, and the Qualcomm clock-controller driver exposes provider arrays whose indexes must match these values. Consumer drivers later resolve those phandles through common clock, reset-controller, or genpd APIs.

## State and Persistence Behavior

The file owns no memory, locks, hardware registers, or persistent storage. Its state is the ABI value assigned to each macro. Those values persist in compiled DTBs and out-of-tree device trees, so renumbering or deleting an existing define is a compatibility break even though no runtime state is stored here. Actual enable counts, reset assertion state, and GDSC power state are maintained by the clock/reset/power-domain drivers and hardware registers, not by this header.

## Dependencies and Integration Points

Direct source dependencies are intentionally minimal: the header has only SPDX/copyright comments, an include guard, macro definitions, and `#endif`. It is integrated by textual inclusion rather than linking. Local integration evidence: clock-controller driver references: `sources/distributed-fs/ceph-client/drivers/clk/qcom/negcc-nord.c`.

The semantic dependency is the matching provider implementation and its descriptor arrays. `qcom,nord-negcc.h` IDs must stay aligned with driver tables for global PLLs plus bus, QUP, USB, PCIe, UFS, SDCC, camera/display/video/gpu vote, reset, and GDSC IDs. DTS consumers depend on these exact constants for properties such as `clocks`, `resets`, `power-domains`, and named clock inputs.

## Risks and Edge Cases

The main risk is ABI drift: inserting new IDs in the middle, reusing a removed value, or moving a reset/GDSC ID to a different number can silently bind a DTS consumer to the wrong hardware clock or power domain. It also exports reset IDs (`NE_GCC_GPU_2_BCR`=0 through `NE_GCC_USB3PHY_PHY_SEC_BCR`=12). Power-domain/GDSC IDs are exported as `NE_GCC_UFS_MEM_PHY_GDSC`=0 through `NE_GCC_USB3_SEC_PHY_GDSC`=6. Shared names such as PLLs, XO/sleep sources, bus clocks, and GDSCs are easy to copy between SoCs, but the numeric ordering must follow this specific provider, not a visually similar controller. Because the file is pure macros, the compiler provides little semantic checking beyond duplicate definitions and include-guard correctness.

## Test Signals

Useful validation includes building the relevant `drivers/clk/qcom` object with this header, compiling DTBs that include `qcom,nord-negcc.h`, and running `dtbs_check`/binding-schema checks for the affected SoC. Runtime smoke tests are provider probe success without missing clock/reset IDs, absence of `-ENOENT`/`-EINVAL` from clock lookups, expected entries under common-clock debugfs, and successful bring-up of consumers in the exported domain set: global PLLs plus bus, QUP, USB, PCIe, UFS, SDCC, camera/display/video/gpu vote, reset, and GDSC IDs. For edits, diff the numeric table against the matching driver arrays and boot at least one DTS consumer when local hardware or emulation coverage exists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,nord-negcc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,nord-nwgcc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,nord-nwgcc.h

## Purpose

`sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,nord-nwgcc.h` defines the public device-tree numeric IDs for the Qualcomm global clock-controller binding associated with `qcom,nord-nwgcc.h` / `nord`. The source was read completely for this report (69 lines). It is not executable kernel code; it is a stable binding contract included by DTS files and by the matching `drivers/clk/qcom` provider so that phandle clock, reset, and power-domain specifiers use the same indexes.

## Important APIs, Types, and Functions

There are no C functions, structs, or runtime APIs. The exported API is a set of preprocessor constants guarded by `_DT_BINDINGS_CLK_QCOM_NW_GCC_NORD_H`. This header defines 45 clock IDs, 9 reset IDs, and 0 power-domain/GDSC IDs, for 54 numeric binding macros total.

Clock ID range: `NW_GCC_ACMU_MUX_CLK`=0 through `NW_GCC_VIDEO_XO_CLK`=44. Representative clocks: `NW_GCC_ACMU_MUX_CLK`, `NW_GCC_CAMERA_AHB_CLK`, `NW_GCC_CAMERA_HF_AXI_CLK`, `NW_GCC_CAMERA_SF_AXI_CLK`, `NW_GCC_CAMERA_TRIG_CLK`, `NW_GCC_CAMERA_XO_CLK`, ... `NW_GCC_MMU_1_TCU_VOTE_CLK`, `NW_GCC_VIDEO_AHB_CLK`, `NW_GCC_VIDEO_AXI0_CLK`, `NW_GCC_VIDEO_AXI0C_CLK`, `NW_GCC_VIDEO_AXI1_CLK`, `NW_GCC_VIDEO_XO_CLK`.

Reset ID range: `NW_GCC_CAMERA_BCR`=0 through `NW_GCC_VIDEO_BCR`=8. Representative resets: `NW_GCC_CAMERA_BCR`, `NW_GCC_DISPLAY_0_BCR`, `NW_GCC_DISPLAY_1_BCR`, `NW_GCC_DPRX0_BCR`, `NW_GCC_DPRX1_BCR`, `NW_GCC_EVA_BCR`, `NW_GCC_GPU_2_BCR`, `NW_GCC_GPU_BCR`, `NW_GCC_VIDEO_BCR`.

Power-domain/GDSC range: none. Representative domains: none.

Macro inventory begins with:
- `NW_GCC_ACMU_MUX_CLK` = 0 (clock, line 10)
- `NW_GCC_CAMERA_AHB_CLK` = 1 (clock, line 11)
- `NW_GCC_CAMERA_HF_AXI_CLK` = 2 (clock, line 12)
- `NW_GCC_CAMERA_SF_AXI_CLK` = 3 (clock, line 13)
- `NW_GCC_CAMERA_TRIG_CLK` = 4 (clock, line 14)
- `NW_GCC_CAMERA_XO_CLK` = 5 (clock, line 15)
- `NW_GCC_DISP_0_AHB_CLK` = 6 (clock, line 16)
- `NW_GCC_DISP_0_HF_AXI_CLK` = 7 (clock, line 17)
- `NW_GCC_DISP_0_TRIG_CLK` = 8 (clock, line 18)
- `NW_GCC_DISP_1_AHB_CLK` = 9 (clock, line 19)
- ... 44 additional numeric binding macros continue in the same contiguous namespace sections.

## Control Flow

This header has no branches, calls, or runtime control flow. The effective flow is build-time and probe-time: DTS sources include the constants, the device-tree compiler stores the resulting integers in clock/reset/power-domain specifier cells, and the Qualcomm clock-controller driver exposes provider arrays whose indexes must match these values. Consumer drivers later resolve those phandles through common clock, reset-controller, or genpd APIs.

## State and Persistence Behavior

The file owns no memory, locks, hardware registers, or persistent storage. Its state is the ABI value assigned to each macro. Those values persist in compiled DTBs and out-of-tree device trees, so renumbering or deleting an existing define is a compatibility break even though no runtime state is stored here. Actual enable counts, reset assertion state, and GDSC power state are maintained by the clock/reset/power-domain drivers and hardware registers, not by this header.

## Dependencies and Integration Points

Direct source dependencies are intentionally minimal: the header has only SPDX/copyright comments, an include guard, macro definitions, and `#endif`. It is integrated by textual inclusion rather than linking. Local integration evidence: clock-controller driver references: `sources/distributed-fs/ceph-client/drivers/clk/qcom/nwgcc-nord.c`.

The semantic dependency is the matching provider implementation and its descriptor arrays. `qcom,nord-nwgcc.h` IDs must stay aligned with driver tables for global PLLs plus bus, QUP, USB, PCIe, UFS, SDCC, camera/display/video/gpu vote, reset, and GDSC IDs. DTS consumers depend on these exact constants for properties such as `clocks`, `resets`, `power-domains`, and named clock inputs.

## Risks and Edge Cases

The main risk is ABI drift: inserting new IDs in the middle, reusing a removed value, or moving a reset/GDSC ID to a different number can silently bind a DTS consumer to the wrong hardware clock or power domain. It also exports reset IDs (`NW_GCC_CAMERA_BCR`=0 through `NW_GCC_VIDEO_BCR`=8). It does not export GDSC or power-domain IDs. Shared names such as PLLs, XO/sleep sources, bus clocks, and GDSCs are easy to copy between SoCs, but the numeric ordering must follow this specific provider, not a visually similar controller. Because the file is pure macros, the compiler provides little semantic checking beyond duplicate definitions and include-guard correctness.

## Test Signals

Useful validation includes building the relevant `drivers/clk/qcom` object with this header, compiling DTBs that include `qcom,nord-nwgcc.h`, and running `dtbs_check`/binding-schema checks for the affected SoC. Runtime smoke tests are provider probe success without missing clock/reset IDs, absence of `-ENOENT`/`-EINVAL` from clock lookups, expected entries under common-clock debugfs, and successful bring-up of consumers in the exported domain set: global PLLs plus bus, QUP, USB, PCIe, UFS, SDCC, camera/display/video/gpu vote, reset, and GDSC IDs. For edits, diff the numeric table against the matching driver arrays and boot at least one DTS consumer when local hardware or emulation coverage exists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,nord-nwgcc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,nord-segcc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,nord-segcc.h

## Purpose

`sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,nord-segcc.h` defines the public device-tree numeric IDs for the Qualcomm global clock-controller binding associated with `qcom,nord-segcc.h` / `nord`. The source was read completely for this report (98 lines). It is not executable kernel code; it is a stable binding contract included by DTS files and by the matching `drivers/clk/qcom` provider so that phandle clock, reset, and power-domain specifiers use the same indexes.

## Important APIs, Types, and Functions

There are no C functions, structs, or runtime APIs. The exported API is a set of preprocessor constants guarded by `_DT_BINDINGS_CLK_QCOM_SE_GCC_NORD_H`. This header defines 77 clock IDs, 4 reset IDs, and 2 power-domain/GDSC IDs, for 83 numeric binding macros total.

Clock ID range: `SE_GCC_EEE_EMAC0_CLK`=0 through `SE_GCC_QUPV3_WRAP1_S_AHB_CLK`=76. Representative clocks: `SE_GCC_EEE_EMAC0_CLK`, `SE_GCC_EEE_EMAC0_CLK_SRC`, `SE_GCC_EEE_EMAC1_CLK`, `SE_GCC_EEE_EMAC1_CLK_SRC`, `SE_GCC_EMAC0_AXI_CLK`, `SE_GCC_EMAC0_CC_SGMIIPHY_RX_CLK`, ... `SE_GCC_QUPV3_WRAP1_S4_CLK_SRC`, `SE_GCC_QUPV3_WRAP1_S5_CLK`, `SE_GCC_QUPV3_WRAP1_S5_CLK_SRC`, `SE_GCC_QUPV3_WRAP1_S6_CLK`, `SE_GCC_QUPV3_WRAP1_S6_CLK_SRC`, `SE_GCC_QUPV3_WRAP1_S_AHB_CLK`.

Reset ID range: `SE_GCC_EMAC0_BCR`=0 through `SE_GCC_QUPV3_WRAPPER_1_BCR`=3. Representative resets: `SE_GCC_EMAC0_BCR`, `SE_GCC_EMAC1_BCR`, `SE_GCC_QUPV3_WRAPPER_0_BCR`, `SE_GCC_QUPV3_WRAPPER_1_BCR`.

Power-domain/GDSC range: `SE_GCC_EMAC0_GDSC`=0 through `SE_GCC_EMAC1_GDSC`=1. Representative domains: `SE_GCC_EMAC0_GDSC`, `SE_GCC_EMAC1_GDSC`.

Macro inventory begins with:
- `SE_GCC_EEE_EMAC0_CLK` = 0 (clock, line 10)
- `SE_GCC_EEE_EMAC0_CLK_SRC` = 1 (clock, line 11)
- `SE_GCC_EEE_EMAC1_CLK` = 2 (clock, line 12)
- `SE_GCC_EEE_EMAC1_CLK_SRC` = 3 (clock, line 13)
- `SE_GCC_EMAC0_AXI_CLK` = 4 (clock, line 14)
- `SE_GCC_EMAC0_CC_SGMIIPHY_RX_CLK` = 5 (clock, line 15)
- `SE_GCC_EMAC0_CC_SGMIIPHY_TX_CLK` = 6 (clock, line 16)
- `SE_GCC_EMAC0_PHY_AUX_CLK` = 7 (clock, line 17)
- `SE_GCC_EMAC0_PHY_AUX_CLK_SRC` = 8 (clock, line 18)
- `SE_GCC_EMAC0_PTP_CLK` = 9 (clock, line 19)
- ... 73 additional numeric binding macros continue in the same contiguous namespace sections.

## Control Flow

This header has no branches, calls, or runtime control flow. The effective flow is build-time and probe-time: DTS sources include the constants, the device-tree compiler stores the resulting integers in clock/reset/power-domain specifier cells, and the Qualcomm clock-controller driver exposes provider arrays whose indexes must match these values. Consumer drivers later resolve those phandles through common clock, reset-controller, or genpd APIs.

## State and Persistence Behavior

The file owns no memory, locks, hardware registers, or persistent storage. Its state is the ABI value assigned to each macro. Those values persist in compiled DTBs and out-of-tree device trees, so renumbering or deleting an existing define is a compatibility break even though no runtime state is stored here. Actual enable counts, reset assertion state, and GDSC power state are maintained by the clock/reset/power-domain drivers and hardware registers, not by this header.

## Dependencies and Integration Points

Direct source dependencies are intentionally minimal: the header has only SPDX/copyright comments, an include guard, macro definitions, and `#endif`. It is integrated by textual inclusion rather than linking. Local integration evidence: clock-controller driver references: `sources/distributed-fs/ceph-client/drivers/clk/qcom/segcc-nord.c`.

The semantic dependency is the matching provider implementation and its descriptor arrays. `qcom,nord-segcc.h` IDs must stay aligned with driver tables for global PLLs plus bus, QUP, USB, PCIe, UFS, SDCC, camera/display/video/gpu vote, reset, and GDSC IDs. DTS consumers depend on these exact constants for properties such as `clocks`, `resets`, `power-domains`, and named clock inputs.

## Risks and Edge Cases

The main risk is ABI drift: inserting new IDs in the middle, reusing a removed value, or moving a reset/GDSC ID to a different number can silently bind a DTS consumer to the wrong hardware clock or power domain. It also exports reset IDs (`SE_GCC_EMAC0_BCR`=0 through `SE_GCC_QUPV3_WRAPPER_1_BCR`=3). Power-domain/GDSC IDs are exported as `SE_GCC_EMAC0_GDSC`=0 through `SE_GCC_EMAC1_GDSC`=1. Shared names such as PLLs, XO/sleep sources, bus clocks, and GDSCs are easy to copy between SoCs, but the numeric ordering must follow this specific provider, not a visually similar controller. Because the file is pure macros, the compiler provides little semantic checking beyond duplicate definitions and include-guard correctness.

## Test Signals

Useful validation includes building the relevant `drivers/clk/qcom` object with this header, compiling DTBs that include `qcom,nord-segcc.h`, and running `dtbs_check`/binding-schema checks for the affected SoC. Runtime smoke tests are provider probe success without missing clock/reset IDs, absence of `-ENOENT`/`-EINVAL` from clock lookups, expected entries under common-clock debugfs, and successful bring-up of consumers in the exported domain set: global PLLs plus bus, QUP, USB, PCIe, UFS, SDCC, camera/display/video/gpu vote, reset, and GDSC IDs. For edits, diff the numeric table against the matching driver arrays and boot at least one DTS consumer when local hardware or emulation coverage exists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,nord-segcc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,nord-tcsrcc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,nord-tcsrcc.h

## Purpose

`sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,nord-tcsrcc.h` defines the public device-tree numeric IDs for the Qualcomm TCSR clock-reference binding associated with `qcom,nord-tcsrcc.h` / `nord`. The source was read completely for this report (26 lines). It is not executable kernel code; it is a stable binding contract included by DTS files and by the matching `drivers/clk/qcom` provider so that phandle clock, reset, and power-domain specifiers use the same indexes.

## Important APIs, Types, and Functions

There are no C functions, structs, or runtime APIs. The exported API is a set of preprocessor constants guarded by `_DT_BINDINGS_CLK_QCOM_TCSR_CC_NORD_H`. This header defines 15 clock IDs, 0 reset IDs, and 0 power-domain/GDSC IDs, for 15 numeric binding macros total.

Clock ID range: `TCSR_DP_RX_0_CLKREF_EN`=0 through `TCSR_UX_SGMII_1_CLKREF_EN`=14. Representative clocks: `TCSR_DP_RX_0_CLKREF_EN`, `TCSR_DP_RX_1_CLKREF_EN`, `TCSR_DP_TX_0_CLKREF_EN`, `TCSR_DP_TX_1_CLKREF_EN`, `TCSR_DP_TX_2_CLKREF_EN`, `TCSR_DP_TX_3_CLKREF_EN`, ... `TCSR_USB2_1_CLKREF_EN`, `TCSR_USB2_2_CLKREF_EN`, `TCSR_USB3_0_CLKREF_EN`, `TCSR_USB3_1_CLKREF_EN`, `TCSR_UX_SGMII_0_CLKREF_EN`, `TCSR_UX_SGMII_1_CLKREF_EN`.

Reset ID range: none. Representative resets: none.

Power-domain/GDSC range: none. Representative domains: none.

Macro inventory begins with:
- `TCSR_DP_RX_0_CLKREF_EN` = 0 (clock, line 10)
- `TCSR_DP_RX_1_CLKREF_EN` = 1 (clock, line 11)
- `TCSR_DP_TX_0_CLKREF_EN` = 2 (clock, line 12)
- `TCSR_DP_TX_1_CLKREF_EN` = 3 (clock, line 13)
- `TCSR_DP_TX_2_CLKREF_EN` = 4 (clock, line 14)
- `TCSR_DP_TX_3_CLKREF_EN` = 5 (clock, line 15)
- `TCSR_PCIE_CLKREF_EN` = 6 (clock, line 16)
- `TCSR_UFS_CLKREF_EN` = 7 (clock, line 17)
- `TCSR_USB2_0_CLKREF_EN` = 8 (clock, line 18)
- `TCSR_USB2_1_CLKREF_EN` = 9 (clock, line 19)
- ... 5 additional numeric binding macros continue in the same contiguous namespace sections.

## Control Flow

This header has no branches, calls, or runtime control flow. The effective flow is build-time and probe-time: DTS sources include the constants, the device-tree compiler stores the resulting integers in clock/reset/power-domain specifier cells, and the Qualcomm clock-controller driver exposes provider arrays whose indexes must match these values. Consumer drivers later resolve those phandles through common clock, reset-controller, or genpd APIs.

## State and Persistence Behavior

The file owns no memory, locks, hardware registers, or persistent storage. Its state is the ABI value assigned to each macro. Those values persist in compiled DTBs and out-of-tree device trees, so renumbering or deleting an existing define is a compatibility break even though no runtime state is stored here. Actual enable counts, reset assertion state, and GDSC power state are maintained by the clock/reset/power-domain drivers and hardware registers, not by this header.

## Dependencies and Integration Points

Direct source dependencies are intentionally minimal: the header has only SPDX/copyright comments, an include guard, macro definitions, and `#endif`. It is integrated by textual inclusion rather than linking. Local integration evidence: clock-controller driver references: `sources/distributed-fs/ceph-client/drivers/clk/qcom/tcsrcc-nord.c`.

The semantic dependency is the matching provider implementation and its descriptor arrays. `qcom,nord-tcsrcc.h` IDs must stay aligned with driver tables for TCSR clock reference enable IDs for PCIe, UFS, USB2, and USB3 pads. DTS consumers depend on these exact constants for properties such as `clocks`, `resets`, `power-domains`, and named clock inputs.

## Risks and Edge Cases

The main risk is ABI drift: inserting new IDs in the middle, reusing a removed value, or moving a reset/GDSC ID to a different number can silently bind a DTS consumer to the wrong hardware clock or power domain. It does not export reset IDs in this clock header; reset bindings are either absent for this controller or live in a paired reset binding header/driver table. It does not export GDSC or power-domain IDs. Shared names such as PLLs, XO/sleep sources, bus clocks, and GDSCs are easy to copy between SoCs, but the numeric ordering must follow this specific provider, not a visually similar controller. Because the file is pure macros, the compiler provides little semantic checking beyond duplicate definitions and include-guard correctness.

## Test Signals

Useful validation includes building the relevant `drivers/clk/qcom` object with this header, compiling DTBs that include `qcom,nord-tcsrcc.h`, and running `dtbs_check`/binding-schema checks for the affected SoC. Runtime smoke tests are provider probe success without missing clock/reset IDs, absence of `-ENOENT`/`-EINVAL` from clock lookups, expected entries under common-clock debugfs, and successful bring-up of consumers in the exported domain set: TCSR clock reference enable IDs for PCIe, UFS, USB2, and USB3 pads. For edits, diff the numeric table against the matching driver arrays and boot at least one DTS consumer when local hardware or emulation coverage exists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,nord-tcsrcc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,q6sstopcc-qcs404.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,q6sstopcc-qcs404.h

## Purpose

`sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,q6sstopcc-qcs404.h` defines the public device-tree numeric IDs for the Qualcomm Q6 subsystem top clock-controller binding associated with `qcom,q6sstopcc-qcs404.h` / `q6sstopcc`. The source was read completely for this report (18 lines). It is not executable kernel code; it is a stable binding contract included by DTS files and by the matching `drivers/clk/qcom` provider so that phandle clock, reset, and power-domain specifiers use the same indexes.

## Important APIs, Types, and Functions

There are no C functions, structs, or runtime APIs. The exported API is a set of preprocessor constants guarded by `_DT_BINDINGS_CLK_Q6SSTOP_QCS404_H`. This header defines 8 clock IDs, 0 reset IDs, and 0 power-domain/GDSC IDs, for 8 numeric binding macros total.

Clock ID range: `LCC_AHBFABRIC_CBC_CLK`=0 through `TCSR_Q6SS_LCC_CBCR_CLK`=6. Representative clocks: `LCC_AHBFABRIC_CBC_CLK`, `LCC_Q6SS_AHBS_CBC_CLK`, `LCC_Q6SS_TCM_SLAVE_CBC_CLK`, `LCC_Q6SS_AHBM_CBC_CLK`, `LCC_Q6SS_AXIM_CBC_CLK`, `LCC_Q6SS_BCR_SLEEP_CLK`, `TCSR_Q6SS_LCC_CBCR_CLK`, `Q6SSTOP_BCR_RESET`.

Reset ID range: none. Representative resets: none.

Power-domain/GDSC range: none. Representative domains: none.

Macro inventory begins with:
- `LCC_AHBFABRIC_CBC_CLK` = 0 (clock, line 9)
- `LCC_Q6SS_AHBS_CBC_CLK` = 1 (clock, line 10)
- `LCC_Q6SS_TCM_SLAVE_CBC_CLK` = 2 (clock, line 11)
- `LCC_Q6SS_AHBM_CBC_CLK` = 3 (clock, line 12)
- `LCC_Q6SS_AXIM_CBC_CLK` = 4 (clock, line 13)
- `LCC_Q6SS_BCR_SLEEP_CLK` = 5 (clock, line 14)
- `TCSR_Q6SS_LCC_CBCR_CLK` = 6 (clock, line 15)
- `Q6SSTOP_BCR_RESET` = 1 (clock, line 17)

## Control Flow

This header has no branches, calls, or runtime control flow. The effective flow is build-time and probe-time: DTS sources include the constants, the device-tree compiler stores the resulting integers in clock/reset/power-domain specifier cells, and the Qualcomm clock-controller driver exposes provider arrays whose indexes must match these values. Consumer drivers later resolve those phandles through common clock, reset-controller, or genpd APIs.

## State and Persistence Behavior

The file owns no memory, locks, hardware registers, or persistent storage. Its state is the ABI value assigned to each macro. Those values persist in compiled DTBs and out-of-tree device trees, so renumbering or deleting an existing define is a compatibility break even though no runtime state is stored here. Actual enable counts, reset assertion state, and GDSC power state are maintained by the clock/reset/power-domain drivers and hardware registers, not by this header.

## Dependencies and Integration Points

Direct source dependencies are intentionally minimal: the header has only SPDX/copyright comments, an include guard, macro definitions, and `#endif`. It is integrated by textual inclusion rather than linking. Local integration evidence: clock-controller driver references: `sources/distributed-fs/ceph-client/drivers/clk/qcom/q6sstop-qcs404.c`.

The semantic dependency is the matching provider implementation and its descriptor arrays. `qcom,q6sstopcc-qcs404.h` IDs must stay aligned with driver tables for Q6 stop/top AHB, XO, sleep, and DSP-related branch clock IDs. DTS consumers depend on these exact constants for properties such as `clocks`, `resets`, `power-domains`, and named clock inputs.

## Risks and Edge Cases

The main risk is ABI drift: inserting new IDs in the middle, reusing a removed value, or moving a reset/GDSC ID to a different number can silently bind a DTS consumer to the wrong hardware clock or power domain. It does not export reset IDs in this clock header; reset bindings are either absent for this controller or live in a paired reset binding header/driver table. It does not export GDSC or power-domain IDs. Shared names such as PLLs, XO/sleep sources, bus clocks, and GDSCs are easy to copy between SoCs, but the numeric ordering must follow this specific provider, not a visually similar controller. Because the file is pure macros, the compiler provides little semantic checking beyond duplicate definitions and include-guard correctness.

## Test Signals

Useful validation includes building the relevant `drivers/clk/qcom` object with this header, compiling DTBs that include `qcom,q6sstopcc-qcs404.h`, and running `dtbs_check`/binding-schema checks for the affected SoC. Runtime smoke tests are provider probe success without missing clock/reset IDs, absence of `-ENOENT`/`-EINVAL` from clock lookups, expected entries under common-clock debugfs, and successful bring-up of consumers in the exported domain set: Q6 stop/top AHB, XO, sleep, and DSP-related branch clock IDs. For edits, diff the numeric table against the matching driver arrays and boot at least one DTS consumer when local hardware or emulation coverage exists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,q6sstopcc-qcs404.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,qca8k-nsscc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,qca8k-nsscc.h

## Purpose

`sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,qca8k-nsscc.h` defines the public device-tree numeric IDs for the Qualcomm network subsystem clock-controller binding associated with `qcom,qca8k-nsscc.h` / `qca8k`. The source was read completely for this report (101 lines). It is not executable kernel code; it is a stable binding contract included by DTS files and by the matching `drivers/clk/qcom` provider so that phandle clock, reset, and power-domain specifiers use the same indexes.

## Important APIs, Types, and Functions

There are no C functions, structs, or runtime APIs. The exported API is a set of preprocessor constants guarded by `_DT_BINDINGS_CLK_QCOM_QCA8K_NSS_CC_H`. This header defines 92 clock IDs, 0 reset IDs, and 0 power-domain/GDSC IDs, for 92 numeric binding macros total.

Clock ID range: `NSS_CC_SWITCH_CORE_CLK_SRC`=0 through `NSS_CC_GEPHY3_SYS_CLK`=91. Representative clocks: `NSS_CC_SWITCH_CORE_CLK_SRC`, `NSS_CC_SWITCH_CORE_CLK`, `NSS_CC_APB_BRIDGE_CLK`, `NSS_CC_MAC0_TX_CLK_SRC`, `NSS_CC_MAC0_TX_DIV_CLK_SRC`, `NSS_CC_MAC0_TX_CLK`, ... `NSS_CC_SRDS0_SYS_CLK`, `NSS_CC_SRDS1_SYS_CLK`, `NSS_CC_GEPHY0_SYS_CLK`, `NSS_CC_GEPHY1_SYS_CLK`, `NSS_CC_GEPHY2_SYS_CLK`, `NSS_CC_GEPHY3_SYS_CLK`.

Reset ID range: none. Representative resets: none.

Power-domain/GDSC range: none. Representative domains: none.

Macro inventory begins with:
- `NSS_CC_SWITCH_CORE_CLK_SRC` = 0 (clock, line 9)
- `NSS_CC_SWITCH_CORE_CLK` = 1 (clock, line 10)
- `NSS_CC_APB_BRIDGE_CLK` = 2 (clock, line 11)
- `NSS_CC_MAC0_TX_CLK_SRC` = 3 (clock, line 12)
- `NSS_CC_MAC0_TX_DIV_CLK_SRC` = 4 (clock, line 13)
- `NSS_CC_MAC0_TX_CLK` = 5 (clock, line 14)
- `NSS_CC_MAC0_TX_SRDS1_CLK` = 6 (clock, line 15)
- `NSS_CC_MAC0_RX_CLK_SRC` = 7 (clock, line 16)
- `NSS_CC_MAC0_RX_DIV_CLK_SRC` = 8 (clock, line 17)
- `NSS_CC_MAC0_RX_CLK` = 9 (clock, line 18)
- ... 82 additional numeric binding macros continue in the same contiguous namespace sections.

## Control Flow

This header has no branches, calls, or runtime control flow. The effective flow is build-time and probe-time: DTS sources include the constants, the device-tree compiler stores the resulting integers in clock/reset/power-domain specifier cells, and the Qualcomm clock-controller driver exposes provider arrays whose indexes must match these values. Consumer drivers later resolve those phandles through common clock, reset-controller, or genpd APIs.

## State and Persistence Behavior

The file owns no memory, locks, hardware registers, or persistent storage. Its state is the ABI value assigned to each macro. Those values persist in compiled DTBs and out-of-tree device trees, so renumbering or deleting an existing define is a compatibility break even though no runtime state is stored here. Actual enable counts, reset assertion state, and GDSC power state are maintained by the clock/reset/power-domain drivers and hardware registers, not by this header.

## Dependencies and Integration Points

Direct source dependencies are intentionally minimal: the header has only SPDX/copyright comments, an include guard, macro definitions, and `#endif`. It is integrated by textual inclusion rather than linking. Local integration evidence: clock-controller driver references: `sources/distributed-fs/ceph-client/drivers/clk/qcom/nsscc-qca8k.c`.

The semantic dependency is the matching provider implementation and its descriptor arrays. `qcom,qca8k-nsscc.h` IDs must stay aligned with driver tables for NSS/packet-processing, switch, UNIPHY, port, crypto, memory, AHB/AXI, reset, and fabric clocks. DTS consumers depend on these exact constants for properties such as `clocks`, `resets`, `power-domains`, and named clock inputs.

## Risks and Edge Cases

The main risk is ABI drift: inserting new IDs in the middle, reusing a removed value, or moving a reset/GDSC ID to a different number can silently bind a DTS consumer to the wrong hardware clock or power domain. It does not export reset IDs in this clock header; reset bindings are either absent for this controller or live in a paired reset binding header/driver table. It does not export GDSC or power-domain IDs. Shared names such as PLLs, XO/sleep sources, bus clocks, and GDSCs are easy to copy between SoCs, but the numeric ordering must follow this specific provider, not a visually similar controller. Because the file is pure macros, the compiler provides little semantic checking beyond duplicate definitions and include-guard correctness.

## Test Signals

Useful validation includes building the relevant `drivers/clk/qcom` object with this header, compiling DTBs that include `qcom,qca8k-nsscc.h`, and running `dtbs_check`/binding-schema checks for the affected SoC. Runtime smoke tests are provider probe success without missing clock/reset IDs, absence of `-ENOENT`/`-EINVAL` from clock lookups, expected entries under common-clock debugfs, and successful bring-up of consumers in the exported domain set: NSS/packet-processing, switch, UNIPHY, port, crypto, memory, AHB/AXI, reset, and fabric clocks. For edits, diff the numeric table against the matching driver arrays and boot at least one DTS consumer when local hardware or emulation coverage exists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,qca8k-nsscc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,qcm2290-gpucc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,qcm2290-gpucc.h

## Purpose

`sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,qcm2290-gpucc.h` defines the public device-tree numeric IDs for the Qualcomm GPU clock-controller binding associated with `qcom,qcm2290-gpucc.h` / `qcm2290`. The source was read completely for this report (32 lines). It is not executable kernel code; it is a stable binding contract included by DTS files and by the matching `drivers/clk/qcom` provider so that phandle clock, reset, and power-domain specifiers use the same indexes.

## Important APIs, Types, and Functions

There are no C functions, structs, or runtime APIs. The exported API is a set of preprocessor constants guarded by `_DT_BINDINGS_CLK_QCOM_GPU_CC_QCM2290_H`. This header defines 13 clock IDs, 1 reset ID, and 2 power-domain/GDSC IDs, for 16 numeric binding macros total.

Clock ID range: `GPU_CC_AHB_CLK`=0 through `GPU_CC_HLOS1_VOTE_GPU_SMMU_CLK`=12. Representative clocks: `GPU_CC_AHB_CLK`, `GPU_CC_CRC_AHB_CLK`, `GPU_CC_CX_GFX3D_CLK`, `GPU_CC_CX_GMU_CLK`, `GPU_CC_CX_SNOC_DVM_CLK`, `GPU_CC_CXO_AON_CLK`, ... `GPU_CC_GMU_CLK_SRC`, `GPU_CC_GX_GFX3D_CLK`, `GPU_CC_GX_GFX3D_CLK_SRC`, `GPU_CC_PLL0`, `GPU_CC_SLEEP_CLK`, `GPU_CC_HLOS1_VOTE_GPU_SMMU_CLK`.

Reset ID range: `GPU_GX_BCR`=0 through `GPU_GX_BCR`=0. Representative resets: `GPU_GX_BCR`.

Power-domain/GDSC range: `GPU_CX_GDSC`=0 through `GPU_GX_GDSC`=1. Representative domains: `GPU_CX_GDSC`, `GPU_GX_GDSC`.

Macro inventory begins with:
- `GPU_CC_AHB_CLK` = 0 (clock, line 11)
- `GPU_CC_CRC_AHB_CLK` = 1 (clock, line 12)
- `GPU_CC_CX_GFX3D_CLK` = 2 (clock, line 13)
- `GPU_CC_CX_GMU_CLK` = 3 (clock, line 14)
- `GPU_CC_CX_SNOC_DVM_CLK` = 4 (clock, line 15)
- `GPU_CC_CXO_AON_CLK` = 5 (clock, line 16)
- `GPU_CC_CXO_CLK` = 6 (clock, line 17)
- `GPU_CC_GMU_CLK_SRC` = 7 (clock, line 18)
- `GPU_CC_GX_GFX3D_CLK` = 8 (clock, line 19)
- `GPU_CC_GX_GFX3D_CLK_SRC` = 9 (clock, line 20)
- ... 6 additional numeric binding macros continue in the same contiguous namespace sections.

## Control Flow

This header has no branches, calls, or runtime control flow. The effective flow is build-time and probe-time: DTS sources include the constants, the device-tree compiler stores the resulting integers in clock/reset/power-domain specifier cells, and the Qualcomm clock-controller driver exposes provider arrays whose indexes must match these values. Consumer drivers later resolve those phandles through common clock, reset-controller, or genpd APIs.

## State and Persistence Behavior

The file owns no memory, locks, hardware registers, or persistent storage. Its state is the ABI value assigned to each macro. Those values persist in compiled DTBs and out-of-tree device trees, so renumbering or deleting an existing define is a compatibility break even though no runtime state is stored here. Actual enable counts, reset assertion state, and GDSC power state are maintained by the clock/reset/power-domain drivers and hardware registers, not by this header.

## Dependencies and Integration Points

Direct source dependencies are intentionally minimal: the header has only SPDX/copyright comments, an include guard, macro definitions, and `#endif`. It is integrated by textual inclusion rather than linking. Local integration evidence: clock-controller driver references: `sources/distributed-fs/ceph-client/drivers/clk/qcom/gpucc-qcm2290.c`; device-tree references: `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/agatti.dtsi`.

The semantic dependency is the matching provider implementation and its descriptor arrays. `qcom,qcm2290-gpucc.h` IDs must stay aligned with driver tables for GPU PLL/RCG, GMU, CX/GX, hub, memory NoC, XO/sleep, SMMU vote, reset, and GDSC IDs. DTS consumers depend on these exact constants for properties such as `clocks`, `resets`, `power-domains`, and named clock inputs.

## Risks and Edge Cases

The main risk is ABI drift: inserting new IDs in the middle, reusing a removed value, or moving a reset/GDSC ID to a different number can silently bind a DTS consumer to the wrong hardware clock or power domain. It also exports reset IDs (`GPU_GX_BCR`=0 through `GPU_GX_BCR`=0). Power-domain/GDSC IDs are exported as `GPU_CX_GDSC`=0 through `GPU_GX_GDSC`=1. Shared names such as PLLs, XO/sleep sources, bus clocks, and GDSCs are easy to copy between SoCs, but the numeric ordering must follow this specific provider, not a visually similar controller. Because the file is pure macros, the compiler provides little semantic checking beyond duplicate definitions and include-guard correctness.

## Test Signals

Useful validation includes building the relevant `drivers/clk/qcom` object with this header, compiling DTBs that include `qcom,qcm2290-gpucc.h`, and running `dtbs_check`/binding-schema checks for the affected SoC. Runtime smoke tests are provider probe success without missing clock/reset IDs, absence of `-ENOENT`/`-EINVAL` from clock lookups, expected entries under common-clock debugfs, and successful bring-up of consumers in the exported domain set: GPU PLL/RCG, GMU, CX/GX, hub, memory NoC, XO/sleep, SMMU vote, reset, and GDSC IDs. For edits, diff the numeric table against the matching driver arrays and boot at least one DTS consumer when local hardware or emulation coverage exists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,qcm2290-gpucc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,qcs615-camcc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,qcs615-camcc.h

## Purpose

`sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,qcs615-camcc.h` defines the public device-tree numeric IDs for the Qualcomm camera clock-controller binding associated with `qcom,qcs615-camcc.h` / `qcs615`. The source was read completely for this report (110 lines). It is not executable kernel code; it is a stable binding contract included by DTS files and by the matching `drivers/clk/qcom` provider so that phandle clock, reset, and power-domain specifiers use the same indexes. This header is shared by multiple DTS or driver consumers in this tree, so numeric stability matters beyond one board file.

## Important APIs, Types, and Functions

There are no C functions, structs, or runtime APIs. The exported API is a set of preprocessor constants guarded by `_DT_BINDINGS_CLK_QCOM_CAM_CC_QCS615_H`. This header defines 71 clock IDs, 19 reset IDs, and 5 power-domain/GDSC IDs, for 95 numeric binding macros total.

Clock ID range: `CAM_CC_BPS_AHB_CLK`=0 through `CAM_CC_SYS_TMR_CLK`=70. Representative clocks: `CAM_CC_BPS_AHB_CLK`, `CAM_CC_BPS_AREG_CLK`, `CAM_CC_BPS_AXI_CLK`, `CAM_CC_BPS_CLK`, `CAM_CC_BPS_CLK_SRC`, `CAM_CC_CAMNOC_ATB_CLK`, ... `CAM_CC_PLL2`, `CAM_CC_PLL2_OUT_AUX2`, `CAM_CC_PLL3`, `CAM_CC_SLOW_AHB_CLK_SRC`, `CAM_CC_SOC_AHB_CLK`, `CAM_CC_SYS_TMR_CLK`.

Reset ID range: `CAM_CC_BPS_BCR`=0 through `CAM_CC_TITAN_TOP_BCR`=18. Representative resets: `CAM_CC_BPS_BCR`, `CAM_CC_CAMNOC_BCR`, `CAM_CC_CCI_BCR`, `CAM_CC_CPAS_BCR`, `CAM_CC_CSI0PHY_BCR`, `CAM_CC_CSI1PHY_BCR`, ... `CAM_CC_LRME_BCR`, `CAM_CC_MCLK0_BCR`, `CAM_CC_MCLK1_BCR`, `CAM_CC_MCLK2_BCR`, `CAM_CC_MCLK3_BCR`, `CAM_CC_TITAN_TOP_BCR`.

Power-domain/GDSC range: `BPS_GDSC`=0 through `TITAN_TOP_GDSC`=4. Representative domains: `BPS_GDSC`, `IFE_0_GDSC`, `IFE_1_GDSC`, `IPE_0_GDSC`, `TITAN_TOP_GDSC`.

Macro inventory begins with:
- `CAM_CC_BPS_AHB_CLK` = 0 (clock, line 10)
- `CAM_CC_BPS_AREG_CLK` = 1 (clock, line 11)
- `CAM_CC_BPS_AXI_CLK` = 2 (clock, line 12)
- `CAM_CC_BPS_CLK` = 3 (clock, line 13)
- `CAM_CC_BPS_CLK_SRC` = 4 (clock, line 14)
- `CAM_CC_CAMNOC_ATB_CLK` = 5 (clock, line 15)
- `CAM_CC_CAMNOC_AXI_CLK` = 6 (clock, line 16)
- `CAM_CC_CCI_CLK` = 7 (clock, line 17)
- `CAM_CC_CCI_CLK_SRC` = 8 (clock, line 18)
- `CAM_CC_CORE_AHB_CLK` = 9 (clock, line 19)
- ... 85 additional numeric binding macros continue in the same contiguous namespace sections.

## Control Flow

This header has no branches, calls, or runtime control flow. The effective flow is build-time and probe-time: DTS sources include the constants, the device-tree compiler stores the resulting integers in clock/reset/power-domain specifier cells, and the Qualcomm clock-controller driver exposes provider arrays whose indexes must match these values. Consumer drivers later resolve those phandles through common clock, reset-controller, or genpd APIs.

## State and Persistence Behavior

The file owns no memory, locks, hardware registers, or persistent storage. Its state is the ABI value assigned to each macro. Those values persist in compiled DTBs and out-of-tree device trees, so renumbering or deleting an existing define is a compatibility break even though no runtime state is stored here. Actual enable counts, reset assertion state, and GDSC power state are maintained by the clock/reset/power-domain drivers and hardware registers, not by this header.

## Dependencies and Integration Points

Direct source dependencies are intentionally minimal: the header has only SPDX/copyright comments, an include guard, macro definitions, and `#endif`. It is integrated by textual inclusion rather than linking. Local integration evidence: clock-controller driver references: `sources/distributed-fs/ceph-client/drivers/clk/qcom/camcc-qcs615.c`; device-tree references: `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/talos-evk-camera-imx577.dtso`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/talos.dtsi`.

The semantic dependency is the matching provider implementation and its descriptor arrays. `qcom,qcs615-camcc.h` IDs must stay aligned with driver tables for camera PLLs, MCLKs, CSI/CSIPHY timers, IFE/TFE/SFE/BPS/IPE/JPEG/CPAS fabric clocks, resets, and camera GDSCs. DTS consumers depend on these exact constants for properties such as `clocks`, `resets`, `power-domains`, and named clock inputs.

## Risks and Edge Cases

The main risk is ABI drift: inserting new IDs in the middle, reusing a removed value, or moving a reset/GDSC ID to a different number can silently bind a DTS consumer to the wrong hardware clock or power domain. It also exports reset IDs (`CAM_CC_BPS_BCR`=0 through `CAM_CC_TITAN_TOP_BCR`=18). Power-domain/GDSC IDs are exported as `BPS_GDSC`=0 through `TITAN_TOP_GDSC`=4. Shared names such as PLLs, XO/sleep sources, bus clocks, and GDSCs are easy to copy between SoCs, but the numeric ordering must follow this specific provider, not a visually similar controller. Because the file is pure macros, the compiler provides little semantic checking beyond duplicate definitions and include-guard correctness.

## Test Signals

Useful validation includes building the relevant `drivers/clk/qcom` object with this header, compiling DTBs that include `qcom,qcs615-camcc.h`, and running `dtbs_check`/binding-schema checks for the affected SoC. Runtime smoke tests are provider probe success without missing clock/reset IDs, absence of `-ENOENT`/`-EINVAL` from clock lookups, expected entries under common-clock debugfs, and successful bring-up of consumers in the exported domain set: camera PLLs, MCLKs, CSI/CSIPHY timers, IFE/TFE/SFE/BPS/IPE/JPEG/CPAS fabric clocks, resets, and camera GDSCs. For edits, diff the numeric table against the matching driver arrays and boot at least one DTS consumer when local hardware or emulation coverage exists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,qcs615-camcc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,qcs615-dispcc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,qcs615-dispcc.h

## Purpose

`sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,qcs615-dispcc.h` defines the public device-tree numeric IDs for the Qualcomm display clock-controller binding associated with `qcom,qcs615-dispcc.h` / `qcs615`. The source was read completely for this report (52 lines). It is not executable kernel code; it is a stable binding contract included by DTS files and by the matching `drivers/clk/qcom` provider so that phandle clock, reset, and power-domain specifiers use the same indexes.

## Important APIs, Types, and Functions

There are no C functions, structs, or runtime APIs. The exported API is a set of preprocessor constants guarded by `_DT_BINDINGS_CLK_QCOM_DISP_CC_QCS615_H`. This header defines 34 clock IDs, 2 reset IDs, and 1 power-domain/GDSC ID, for 37 numeric binding macros total.

Clock ID range: `DISP_CC_MDSS_AHB_CLK`=0 through `DISP_CC_XO_CLK`=33. Representative clocks: `DISP_CC_MDSS_AHB_CLK`, `DISP_CC_MDSS_AHB_CLK_SRC`, `DISP_CC_MDSS_BYTE0_CLK`, `DISP_CC_MDSS_BYTE0_CLK_SRC`, `DISP_CC_MDSS_BYTE0_DIV_CLK_SRC`, `DISP_CC_MDSS_BYTE0_INTF_CLK`, ... `DISP_CC_MDSS_RSCC_AHB_CLK`, `DISP_CC_MDSS_RSCC_VSYNC_CLK`, `DISP_CC_MDSS_VSYNC_CLK`, `DISP_CC_MDSS_VSYNC_CLK_SRC`, `DISP_CC_PLL0`, `DISP_CC_XO_CLK`.

Reset ID range: `DISP_CC_MDSS_CORE_BCR`=0 through `DISP_CC_MDSS_RSCC_BCR`=1. Representative resets: `DISP_CC_MDSS_CORE_BCR`, `DISP_CC_MDSS_RSCC_BCR`.

Power-domain/GDSC range: `MDSS_CORE_GDSC`=0 through `MDSS_CORE_GDSC`=0. Representative domains: `MDSS_CORE_GDSC`.

Macro inventory begins with:
- `DISP_CC_MDSS_AHB_CLK` = 0 (clock, line 10)
- `DISP_CC_MDSS_AHB_CLK_SRC` = 1 (clock, line 11)
- `DISP_CC_MDSS_BYTE0_CLK` = 2 (clock, line 12)
- `DISP_CC_MDSS_BYTE0_CLK_SRC` = 3 (clock, line 13)
- `DISP_CC_MDSS_BYTE0_DIV_CLK_SRC` = 4 (clock, line 14)
- `DISP_CC_MDSS_BYTE0_INTF_CLK` = 5 (clock, line 15)
- `DISP_CC_MDSS_DP_AUX_CLK` = 6 (clock, line 16)
- `DISP_CC_MDSS_DP_AUX_CLK_SRC` = 7 (clock, line 17)
- `DISP_CC_MDSS_DP_CRYPTO_CLK` = 8 (clock, line 18)
- `DISP_CC_MDSS_DP_CRYPTO_CLK_SRC` = 9 (clock, line 19)
- ... 27 additional numeric binding macros continue in the same contiguous namespace sections.

## Control Flow

This header has no branches, calls, or runtime control flow. The effective flow is build-time and probe-time: DTS sources include the constants, the device-tree compiler stores the resulting integers in clock/reset/power-domain specifier cells, and the Qualcomm clock-controller driver exposes provider arrays whose indexes must match these values. Consumer drivers later resolve those phandles through common clock, reset-controller, or genpd APIs.

## State and Persistence Behavior

The file owns no memory, locks, hardware registers, or persistent storage. Its state is the ABI value assigned to each macro. Those values persist in compiled DTBs and out-of-tree device trees, so renumbering or deleting an existing define is a compatibility break even though no runtime state is stored here. Actual enable counts, reset assertion state, and GDSC power state are maintained by the clock/reset/power-domain drivers and hardware registers, not by this header.

## Dependencies and Integration Points

Direct source dependencies are intentionally minimal: the header has only SPDX/copyright comments, an include guard, macro definitions, and `#endif`. It is integrated by textual inclusion rather than linking. Local integration evidence: clock-controller driver references: `sources/distributed-fs/ceph-client/drivers/clk/qcom/dispcc-qcs615.c`; device-tree references: `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/talos.dtsi`.

The semantic dependency is the matching provider implementation and its descriptor arrays. `qcom,qcs615-dispcc.h` IDs must stay aligned with driver tables for MDSS AHB/AXI, MDP, DSI byte/escape/pixel, DisplayPort link/pixel/aux, vsync, resets, and display GDSCs. DTS consumers depend on these exact constants for properties such as `clocks`, `resets`, `power-domains`, and named clock inputs.

## Risks and Edge Cases

The main risk is ABI drift: inserting new IDs in the middle, reusing a removed value, or moving a reset/GDSC ID to a different number can silently bind a DTS consumer to the wrong hardware clock or power domain. It also exports reset IDs (`DISP_CC_MDSS_CORE_BCR`=0 through `DISP_CC_MDSS_RSCC_BCR`=1). Power-domain/GDSC IDs are exported as `MDSS_CORE_GDSC`=0 through `MDSS_CORE_GDSC`=0. Shared names such as PLLs, XO/sleep sources, bus clocks, and GDSCs are easy to copy between SoCs, but the numeric ordering must follow this specific provider, not a visually similar controller. Because the file is pure macros, the compiler provides little semantic checking beyond duplicate definitions and include-guard correctness.

## Test Signals

Useful validation includes building the relevant `drivers/clk/qcom` object with this header, compiling DTBs that include `qcom,qcs615-dispcc.h`, and running `dtbs_check`/binding-schema checks for the affected SoC. Runtime smoke tests are provider probe success without missing clock/reset IDs, absence of `-ENOENT`/`-EINVAL` from clock lookups, expected entries under common-clock debugfs, and successful bring-up of consumers in the exported domain set: MDSS AHB/AXI, MDP, DSI byte/escape/pixel, DisplayPort link/pixel/aux, vsync, resets, and display GDSCs. For edits, diff the numeric table against the matching driver arrays and boot at least one DTS consumer when local hardware or emulation coverage exists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,qcs615-dispcc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,qcs615-gcc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,qcs615-gcc.h

## Purpose

`sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,qcs615-gcc.h` defines the public device-tree numeric IDs for the Qualcomm global clock-controller binding associated with `qcom,qcs615-gcc.h` / `qcs615`. The source was read completely for this report (211 lines). It is not executable kernel code; it is a stable binding contract included by DTS files and by the matching `drivers/clk/qcom` provider so that phandle clock, reset, and power-domain specifiers use the same indexes.

## Important APIs, Types, and Functions

There are no C functions, structs, or runtime APIs. The exported API is a set of preprocessor constants guarded by `_DT_BINDINGS_CLK_QCOM_GCC_QCS615_H`. This header defines 167 clock IDs, 17 reset IDs, and 12 power-domain/GDSC IDs, for 196 numeric binding macros total.

Clock ID range: `GPLL0_OUT_AUX2_DIV`=0 through `GCC_UFS_PHY_UNIPRO_CORE_HW_CTL_CLK`=166. Representative clocks: `GPLL0_OUT_AUX2_DIV`, `GPLL3_OUT_AUX2_DIV`, `GPLL0`, `GPLL3`, `GPLL4`, `GPLL6`, ... `GCC_VSENSOR_CLK_SRC`, `GCC_AGGRE_UFS_PHY_AXI_HW_CTL_CLK`, `GCC_UFS_PHY_AXI_HW_CTL_CLK`, `GCC_UFS_PHY_ICE_CORE_HW_CTL_CLK`, `GCC_UFS_PHY_PHY_AUX_HW_CTL_CLK`, `GCC_UFS_PHY_UNIPRO_CORE_HW_CTL_CLK`.

Reset ID range: `GCC_EMAC_BCR`=0 through `GCC_SDCC2_BCR`=16. Representative resets: `GCC_EMAC_BCR`, `GCC_QUSB2PHY_PRIM_BCR`, `GCC_QUSB2PHY_SEC_BCR`, `GCC_USB30_PRIM_BCR`, `GCC_USB2_PHY_SEC_BCR`, `GCC_USB3_DP_PHY_SEC_BCR`, ... `GCC_UFS_PHY_BCR`, `GCC_USB20_SEC_BCR`, `GCC_USB3_PHY_PRIM_SP0_BCR`, `GCC_USB3PHY_PHY_PRIM_SP0_BCR`, `GCC_SDCC1_BCR`, `GCC_SDCC2_BCR`.

Power-domain/GDSC range: `EMAC_GDSC`=0 through `HLOS1_VOTE_MMNOC_MMU_TBU_HF1_GDSC`=11. Representative domains: `EMAC_GDSC`, `PCIE_0_GDSC`, `UFS_PHY_GDSC`, `USB20_SEC_GDSC`, `USB30_PRIM_GDSC`, `HLOS1_VOTE_AGGRE_NOC_MMU_AUDIO_TBU_GDSC`, `HLOS1_VOTE_AGGRE_NOC_MMU_TBU1_GDSC`, `HLOS1_VOTE_AGGRE_NOC_MMU_TBU2_GDSC`, `HLOS1_VOTE_AGGRE_NOC_MMU_PCIE_TBU_GDSC`, `HLOS1_VOTE_MMNOC_MMU_TBU_HF0_GDSC`, `HLOS1_VOTE_MMNOC_MMU_TBU_SF_GDSC`, `HLOS1_VOTE_MMNOC_MMU_TBU_HF1_GDSC`.

Macro inventory begins with:
- `GPLL0_OUT_AUX2_DIV` = 0 (clock, line 10)
- `GPLL3_OUT_AUX2_DIV` = 1 (clock, line 11)
- `GPLL0` = 2 (clock, line 12)
- `GPLL3` = 3 (clock, line 13)
- `GPLL4` = 4 (clock, line 14)
- `GPLL6` = 5 (clock, line 15)
- `GPLL6_OUT_MAIN` = 6 (clock, line 16)
- `GPLL7` = 7 (clock, line 17)
- `GPLL8` = 8 (clock, line 18)
- `GPLL8_OUT_MAIN` = 9 (clock, line 19)
- ... 186 additional numeric binding macros continue in the same contiguous namespace sections.

## Control Flow

This header has no branches, calls, or runtime control flow. The effective flow is build-time and probe-time: DTS sources include the constants, the device-tree compiler stores the resulting integers in clock/reset/power-domain specifier cells, and the Qualcomm clock-controller driver exposes provider arrays whose indexes must match these values. Consumer drivers later resolve those phandles through common clock, reset-controller, or genpd APIs.

## State and Persistence Behavior

The file owns no memory, locks, hardware registers, or persistent storage. Its state is the ABI value assigned to each macro. Those values persist in compiled DTBs and out-of-tree device trees, so renumbering or deleting an existing define is a compatibility break even though no runtime state is stored here. Actual enable counts, reset assertion state, and GDSC power state are maintained by the clock/reset/power-domain drivers and hardware registers, not by this header.

## Dependencies and Integration Points

Direct source dependencies are intentionally minimal: the header has only SPDX/copyright comments, an include guard, macro definitions, and `#endif`. It is integrated by textual inclusion rather than linking. Local integration evidence: clock-controller driver references: `sources/distributed-fs/ceph-client/drivers/clk/qcom/gcc-qcs615.c`; device-tree references: `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/talos.dtsi`.

The semantic dependency is the matching provider implementation and its descriptor arrays. `qcom,qcs615-gcc.h` IDs must stay aligned with driver tables for global PLLs plus bus, QUP, USB, PCIe, UFS, SDCC, camera/display/video/gpu vote, reset, and GDSC IDs. DTS consumers depend on these exact constants for properties such as `clocks`, `resets`, `power-domains`, and named clock inputs.

## Risks and Edge Cases

The main risk is ABI drift: inserting new IDs in the middle, reusing a removed value, or moving a reset/GDSC ID to a different number can silently bind a DTS consumer to the wrong hardware clock or power domain. It also exports reset IDs (`GCC_EMAC_BCR`=0 through `GCC_SDCC2_BCR`=16). Power-domain/GDSC IDs are exported as `EMAC_GDSC`=0 through `HLOS1_VOTE_MMNOC_MMU_TBU_HF1_GDSC`=11. Shared names such as PLLs, XO/sleep sources, bus clocks, and GDSCs are easy to copy between SoCs, but the numeric ordering must follow this specific provider, not a visually similar controller. Because the file is pure macros, the compiler provides little semantic checking beyond duplicate definitions and include-guard correctness.

## Test Signals

Useful validation includes building the relevant `drivers/clk/qcom` object with this header, compiling DTBs that include `qcom,qcs615-gcc.h`, and running `dtbs_check`/binding-schema checks for the affected SoC. Runtime smoke tests are provider probe success without missing clock/reset IDs, absence of `-ENOENT`/`-EINVAL` from clock lookups, expected entries under common-clock debugfs, and successful bring-up of consumers in the exported domain set: global PLLs plus bus, QUP, USB, PCIe, UFS, SDCC, camera/display/video/gpu vote, reset, and GDSC IDs. For edits, diff the numeric table against the matching driver arrays and boot at least one DTS consumer when local hardware or emulation coverage exists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,qcs615-gcc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,qcs615-gpucc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,qcs615-gpucc.h

## Purpose

`sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,qcs615-gpucc.h` defines the public device-tree numeric IDs for the Qualcomm GPU clock-controller binding associated with `qcom,qcs615-gpucc.h` / `qcs615`. The source was read completely for this report (39 lines). It is not executable kernel code; it is a stable binding contract included by DTS files and by the matching `drivers/clk/qcom` provider so that phandle clock, reset, and power-domain specifiers use the same indexes.

## Important APIs, Types, and Functions

There are no C functions, structs, or runtime APIs. The exported API is a set of preprocessor constants guarded by `_DT_BINDINGS_CLK_QCOM_GPU_CC_QCS615_H`. This header defines 17 clock IDs, 5 reset IDs, and 2 power-domain/GDSC IDs, for 24 numeric binding macros total.

Clock ID range: `CRC_DIV_PLL0`=0 through `GPU_CC_SLEEP_CLK`=16. Representative clocks: `CRC_DIV_PLL0`, `CRC_DIV_PLL1`, `GPU_CC_PLL0`, `GPU_CC_PLL1`, `GPU_CC_CRC_AHB_CLK`, `GPU_CC_CX_GFX3D_CLK`, ... `GPU_CC_GMU_CLK_SRC`, `GPU_CC_GX_GFX3D_CLK`, `GPU_CC_GX_GFX3D_CLK_SRC`, `GPU_CC_GX_GMU_CLK`, `GPU_CC_HLOS1_VOTE_GPU_SMMU_CLK`, `GPU_CC_SLEEP_CLK`.

Reset ID range: `GPU_CC_CX_BCR`=0 through `GPU_CC_XO_BCR`=4. Representative resets: `GPU_CC_CX_BCR`, `GPU_CC_GFX3D_AON_BCR`, `GPU_CC_GMU_BCR`, `GPU_CC_GX_BCR`, `GPU_CC_XO_BCR`.

Power-domain/GDSC range: `CX_GDSC`=0 through `GX_GDSC`=1. Representative domains: `CX_GDSC`, `GX_GDSC`.

Macro inventory begins with:
- `CRC_DIV_PLL0` = 0 (clock, line 10)
- `CRC_DIV_PLL1` = 1 (clock, line 11)
- `GPU_CC_PLL0` = 2 (clock, line 12)
- `GPU_CC_PLL1` = 3 (clock, line 13)
- `GPU_CC_CRC_AHB_CLK` = 4 (clock, line 14)
- `GPU_CC_CX_GFX3D_CLK` = 5 (clock, line 15)
- `GPU_CC_CX_GFX3D_SLV_CLK` = 6 (clock, line 16)
- `GPU_CC_CX_GMU_CLK` = 7 (clock, line 17)
- `GPU_CC_CX_SNOC_DVM_CLK` = 8 (clock, line 18)
- `GPU_CC_CXO_AON_CLK` = 9 (clock, line 19)
- ... 14 additional numeric binding macros continue in the same contiguous namespace sections.

## Control Flow

This header has no branches, calls, or runtime control flow. The effective flow is build-time and probe-time: DTS sources include the constants, the device-tree compiler stores the resulting integers in clock/reset/power-domain specifier cells, and the Qualcomm clock-controller driver exposes provider arrays whose indexes must match these values. Consumer drivers later resolve those phandles through common clock, reset-controller, or genpd APIs.

## State and Persistence Behavior

The file owns no memory, locks, hardware registers, or persistent storage. Its state is the ABI value assigned to each macro. Those values persist in compiled DTBs and out-of-tree device trees, so renumbering or deleting an existing define is a compatibility break even though no runtime state is stored here. Actual enable counts, reset assertion state, and GDSC power state are maintained by the clock/reset/power-domain drivers and hardware registers, not by this header.

## Dependencies and Integration Points

Direct source dependencies are intentionally minimal: the header has only SPDX/copyright comments, an include guard, macro definitions, and `#endif`. It is integrated by textual inclusion rather than linking. Local integration evidence: clock-controller driver references: `sources/distributed-fs/ceph-client/drivers/clk/qcom/gpucc-qcs615.c`; device-tree references: `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/talos.dtsi`.

The semantic dependency is the matching provider implementation and its descriptor arrays. `qcom,qcs615-gpucc.h` IDs must stay aligned with driver tables for GPU PLL/RCG, GMU, CX/GX, hub, memory NoC, XO/sleep, SMMU vote, reset, and GDSC IDs. DTS consumers depend on these exact constants for properties such as `clocks`, `resets`, `power-domains`, and named clock inputs.

## Risks and Edge Cases

The main risk is ABI drift: inserting new IDs in the middle, reusing a removed value, or moving a reset/GDSC ID to a different number can silently bind a DTS consumer to the wrong hardware clock or power domain. It also exports reset IDs (`GPU_CC_CX_BCR`=0 through `GPU_CC_XO_BCR`=4). Power-domain/GDSC IDs are exported as `CX_GDSC`=0 through `GX_GDSC`=1. Shared names such as PLLs, XO/sleep sources, bus clocks, and GDSCs are easy to copy between SoCs, but the numeric ordering must follow this specific provider, not a visually similar controller. Because the file is pure macros, the compiler provides little semantic checking beyond duplicate definitions and include-guard correctness.

## Test Signals

Useful validation includes building the relevant `drivers/clk/qcom` object with this header, compiling DTBs that include `qcom,qcs615-gpucc.h`, and running `dtbs_check`/binding-schema checks for the affected SoC. Runtime smoke tests are provider probe success without missing clock/reset IDs, absence of `-ENOENT`/`-EINVAL` from clock lookups, expected entries under common-clock debugfs, and successful bring-up of consumers in the exported domain set: GPU PLL/RCG, GMU, CX/GX, hub, memory NoC, XO/sleep, SMMU vote, reset, and GDSC IDs. For edits, diff the numeric table against the matching driver arrays and boot at least one DTS consumer when local hardware or emulation coverage exists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,qcs615-gpucc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,qcs615-videocc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,qcs615-videocc.h

## Purpose

`sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,qcs615-videocc.h` defines the public device-tree numeric IDs for the Qualcomm video clock-controller binding associated with `qcom,qcs615-videocc.h` / `qcs615`. The source was read completely for this report (30 lines). It is not executable kernel code; it is a stable binding contract included by DTS files and by the matching `drivers/clk/qcom` provider so that phandle clock, reset, and power-domain specifiers use the same indexes.

## Important APIs, Types, and Functions

There are no C functions, structs, or runtime APIs. The exported API is a set of preprocessor constants guarded by `_DT_BINDINGS_CLK_QCOM_VIDEO_CC_QCS615_H`. This header defines 10 clock IDs, 3 reset IDs, and 2 power-domain/GDSC IDs, for 15 numeric binding macros total.

Clock ID range: `VIDEO_CC_SLEEP_CLK`=0 through `VIDEO_PLL0`=9. Representative clocks: `VIDEO_CC_SLEEP_CLK`, `VIDEO_CC_SLEEP_CLK_SRC`, `VIDEO_CC_VCODEC0_AXI_CLK`, `VIDEO_CC_VCODEC0_CORE_CLK`, `VIDEO_CC_VENUS_AHB_CLK`, `VIDEO_CC_VENUS_CLK_SRC`, `VIDEO_CC_VENUS_CTL_AXI_CLK`, `VIDEO_CC_VENUS_CTL_CORE_CLK`, `VIDEO_CC_XO_CLK`, `VIDEO_PLL0`.

Reset ID range: `VIDEO_CC_INTERFACE_BCR`=0 through `VIDEO_CC_VENUS_BCR`=2. Representative resets: `VIDEO_CC_INTERFACE_BCR`, `VIDEO_CC_VCODEC0_BCR`, `VIDEO_CC_VENUS_BCR`.

Power-domain/GDSC range: `VCODEC0_GDSC`=0 through `VENUS_GDSC`=1. Representative domains: `VCODEC0_GDSC`, `VENUS_GDSC`.

Macro inventory begins with:
- `VIDEO_CC_SLEEP_CLK` = 0 (clock, line 10)
- `VIDEO_CC_SLEEP_CLK_SRC` = 1 (clock, line 11)
- `VIDEO_CC_VCODEC0_AXI_CLK` = 2 (clock, line 12)
- `VIDEO_CC_VCODEC0_CORE_CLK` = 3 (clock, line 13)
- `VIDEO_CC_VENUS_AHB_CLK` = 4 (clock, line 14)
- `VIDEO_CC_VENUS_CLK_SRC` = 5 (clock, line 15)
- `VIDEO_CC_VENUS_CTL_AXI_CLK` = 6 (clock, line 16)
- `VIDEO_CC_VENUS_CTL_CORE_CLK` = 7 (clock, line 17)
- `VIDEO_CC_XO_CLK` = 8 (clock, line 18)
- `VIDEO_PLL0` = 9 (clock, line 19)
- ... 5 additional numeric binding macros continue in the same contiguous namespace sections.

## Control Flow

This header has no branches, calls, or runtime control flow. The effective flow is build-time and probe-time: DTS sources include the constants, the device-tree compiler stores the resulting integers in clock/reset/power-domain specifier cells, and the Qualcomm clock-controller driver exposes provider arrays whose indexes must match these values. Consumer drivers later resolve those phandles through common clock, reset-controller, or genpd APIs.

## State and Persistence Behavior

The file owns no memory, locks, hardware registers, or persistent storage. Its state is the ABI value assigned to each macro. Those values persist in compiled DTBs and out-of-tree device trees, so renumbering or deleting an existing define is a compatibility break even though no runtime state is stored here. Actual enable counts, reset assertion state, and GDSC power state are maintained by the clock/reset/power-domain drivers and hardware registers, not by this header.

## Dependencies and Integration Points

Direct source dependencies are intentionally minimal: the header has only SPDX/copyright comments, an include guard, macro definitions, and `#endif`. It is integrated by textual inclusion rather than linking. Local integration evidence: clock-controller driver references: `sources/distributed-fs/ceph-client/drivers/clk/qcom/videocc-qcs615.c`; device-tree references: `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/talos.dtsi`.

The semantic dependency is the matching provider implementation and its descriptor arrays. `qcom,qcs615-videocc.h` IDs must stay aligned with driver tables for video codec MVS/MVS0/MVS1, AHB, AXI, sleep/XO, reset, and GDSC IDs. DTS consumers depend on these exact constants for properties such as `clocks`, `resets`, `power-domains`, and named clock inputs.

## Risks and Edge Cases

The main risk is ABI drift: inserting new IDs in the middle, reusing a removed value, or moving a reset/GDSC ID to a different number can silently bind a DTS consumer to the wrong hardware clock or power domain. It also exports reset IDs (`VIDEO_CC_INTERFACE_BCR`=0 through `VIDEO_CC_VENUS_BCR`=2). Power-domain/GDSC IDs are exported as `VCODEC0_GDSC`=0 through `VENUS_GDSC`=1. Shared names such as PLLs, XO/sleep sources, bus clocks, and GDSCs are easy to copy between SoCs, but the numeric ordering must follow this specific provider, not a visually similar controller. Because the file is pure macros, the compiler provides little semantic checking beyond duplicate definitions and include-guard correctness.

## Test Signals

Useful validation includes building the relevant `drivers/clk/qcom` object with this header, compiling DTBs that include `qcom,qcs615-videocc.h`, and running `dtbs_check`/binding-schema checks for the affected SoC. Runtime smoke tests are provider probe success without missing clock/reset IDs, absence of `-ENOENT`/`-EINVAL` from clock lookups, expected entries under common-clock debugfs, and successful bring-up of consumers in the exported domain set: video codec MVS/MVS0/MVS1, AHB, AXI, sleep/XO, reset, and GDSC IDs. For edits, diff the numeric table against the matching driver arrays and boot at least one DTS consumer when local hardware or emulation coverage exists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,qcs615-videocc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,qcs8300-camcc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,qcs8300-camcc.h

## Purpose

`sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,qcs8300-camcc.h` defines the public device-tree numeric IDs for the Qualcomm camera clock-controller binding associated with `qcom,qcs8300-camcc.h` / `qcs8300`. The source was read completely for this report (16 lines). It is not executable kernel code; it is a stable binding contract included by DTS files and by the matching `drivers/clk/qcom` provider so that phandle clock, reset, and power-domain specifiers use the same indexes.

## Important APIs, Types, and Functions

There are no C functions, structs, or runtime APIs. The exported API is a set of preprocessor constants guarded by `_DT_BINDINGS_CLK_QCOM_QCS8300_CAM_CC_H`. This header defines 1 clock ID, 0 reset IDs, and 0 power-domain/GDSC IDs, for 1 numeric binding macro total.

Clock ID range: `CAM_CC_TITAN_TOP_ACCU_SHIFT_CLK`=86 through `CAM_CC_TITAN_TOP_ACCU_SHIFT_CLK`=86. Representative clocks: `CAM_CC_TITAN_TOP_ACCU_SHIFT_CLK`.

Reset ID range: none. Representative resets: none.

Power-domain/GDSC range: none. Representative domains: none.

Macro inventory begins with:
- `CAM_CC_TITAN_TOP_ACCU_SHIFT_CLK` = 86 (clock, line 14)

## Control Flow

This header has no branches, calls, or runtime control flow. The effective flow is build-time and probe-time: DTS sources include the constants, the device-tree compiler stores the resulting integers in clock/reset/power-domain specifier cells, and the Qualcomm clock-controller driver exposes provider arrays whose indexes must match these values. Consumer drivers later resolve those phandles through common clock, reset-controller, or genpd APIs.

## State and Persistence Behavior

The file owns no memory, locks, hardware registers, or persistent storage. Its state is the ABI value assigned to each macro. Those values persist in compiled DTBs and out-of-tree device trees, so renumbering or deleting an existing define is a compatibility break even though no runtime state is stored here. Actual enable counts, reset assertion state, and GDSC power state are maintained by the clock/reset/power-domain drivers and hardware registers, not by this header.

## Dependencies and Integration Points

Direct source dependencies are intentionally minimal: the header has only SPDX/copyright comments, an include guard, macro definitions, and `#endif`. It is integrated by textual inclusion rather than linking. Local integration evidence: clock-controller driver references: `sources/distributed-fs/ceph-client/drivers/clk/qcom/camcc-sa8775p.c`.

The semantic dependency is the matching provider implementation and its descriptor arrays. `qcom,qcs8300-camcc.h` IDs must stay aligned with driver tables for camera PLLs, MCLKs, CSI/CSIPHY timers, IFE/TFE/SFE/BPS/IPE/JPEG/CPAS fabric clocks, resets, and camera GDSCs. DTS consumers depend on these exact constants for properties such as `clocks`, `resets`, `power-domains`, and named clock inputs.

## Risks and Edge Cases

The main risk is ABI drift: inserting new IDs in the middle, reusing a removed value, or moving a reset/GDSC ID to a different number can silently bind a DTS consumer to the wrong hardware clock or power domain. It does not export reset IDs in this clock header; reset bindings are either absent for this controller or live in a paired reset binding header/driver table. It does not export GDSC or power-domain IDs. Shared names such as PLLs, XO/sleep sources, bus clocks, and GDSCs are easy to copy between SoCs, but the numeric ordering must follow this specific provider, not a visually similar controller. Because the file is pure macros, the compiler provides little semantic checking beyond duplicate definitions and include-guard correctness.

## Test Signals

Useful validation includes building the relevant `drivers/clk/qcom` object with this header, compiling DTBs that include `qcom,qcs8300-camcc.h`, and running `dtbs_check`/binding-schema checks for the affected SoC. Runtime smoke tests are provider probe success without missing clock/reset IDs, absence of `-ENOENT`/`-EINVAL` from clock lookups, expected entries under common-clock debugfs, and successful bring-up of consumers in the exported domain set: camera PLLs, MCLKs, CSI/CSIPHY timers, IFE/TFE/SFE/BPS/IPE/JPEG/CPAS fabric clocks, resets, and camera GDSCs. For edits, diff the numeric table against the matching driver arrays and boot at least one DTS consumer when local hardware or emulation coverage exists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,qcs8300-camcc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,qcs8300-gcc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,qcs8300-gcc.h

## Purpose

`sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,qcs8300-gcc.h` defines the public device-tree numeric IDs for the Qualcomm global clock-controller binding associated with `qcom,qcs8300-gcc.h` / `qcs8300`. The source was read completely for this report (234 lines). It is not executable kernel code; it is a stable binding contract included by DTS files and by the matching `drivers/clk/qcom` provider so that phandle clock, reset, and power-domain specifiers use the same indexes.

## Important APIs, Types, and Functions

There are no C functions, structs, or runtime APIs. The exported API is a set of preprocessor constants guarded by `_DT_BINDINGS_CLK_QCOM_GCC_QCS8300_H`. This header defines 184 clock IDs, 29 reset IDs, and 6 power-domain/GDSC IDs, for 219 numeric binding macros total.

Clock ID range: `GCC_GPLL0`=0 through `GCC_VIDEO_XO_CLK`=183. Representative clocks: `GCC_GPLL0`, `GCC_GPLL0_OUT_EVEN`, `GCC_GPLL1`, `GCC_GPLL4`, `GCC_GPLL7`, `GCC_GPLL9`, ... `GCC_USB3_PRIM_PHY_PIPE_CLK_SRC`, `GCC_USB_CLKREF_EN`, `GCC_VIDEO_AHB_CLK`, `GCC_VIDEO_AXI0_CLK`, `GCC_VIDEO_AXI1_CLK`, `GCC_VIDEO_XO_CLK`.

Reset ID range: `GCC_EMAC0_BCR`=0 through `GCC_VIDEO_AXI1_CLK_ARES`=28. Representative resets: `GCC_EMAC0_BCR`, `GCC_PCIE_0_BCR`, `GCC_PCIE_0_LINK_DOWN_BCR`, `GCC_PCIE_0_NOCSR_COM_PHY_BCR`, `GCC_PCIE_0_PHY_BCR`, `GCC_PCIE_0_PHY_NOCSR_COM_PHY_BCR`, ... `GCC_USB3UNIPHY_PHY_MP0_BCR`, `GCC_USB3UNIPHY_PHY_MP1_BCR`, `GCC_USB_PHY_CFG_AHB2PHY_BCR`, `GCC_VIDEO_BCR`, `GCC_VIDEO_AXI0_CLK_ARES`, `GCC_VIDEO_AXI1_CLK_ARES`.

Power-domain/GDSC range: `GCC_EMAC0_GDSC`=0 through `GCC_USB30_PRIM_GDSC`=5. Representative domains: `GCC_EMAC0_GDSC`, `GCC_PCIE_0_GDSC`, `GCC_PCIE_1_GDSC`, `GCC_UFS_PHY_GDSC`, `GCC_USB20_PRIM_GDSC`, `GCC_USB30_PRIM_GDSC`.

Macro inventory begins with:
- `GCC_GPLL0` = 0 (clock, line 10)
- `GCC_GPLL0_OUT_EVEN` = 1 (clock, line 11)
- `GCC_GPLL1` = 2 (clock, line 12)
- `GCC_GPLL4` = 3 (clock, line 13)
- `GCC_GPLL7` = 4 (clock, line 14)
- `GCC_GPLL9` = 5 (clock, line 15)
- `GCC_AGGRE_NOC_QUPV3_AXI_CLK` = 6 (clock, line 16)
- `GCC_AGGRE_UFS_PHY_AXI_CLK` = 7 (clock, line 17)
- `GCC_AGGRE_USB2_PRIM_AXI_CLK` = 8 (clock, line 18)
- `GCC_AGGRE_USB3_PRIM_AXI_CLK` = 9 (clock, line 19)
- ... 209 additional numeric binding macros continue in the same contiguous namespace sections.

## Control Flow

This header has no branches, calls, or runtime control flow. The effective flow is build-time and probe-time: DTS sources include the constants, the device-tree compiler stores the resulting integers in clock/reset/power-domain specifier cells, and the Qualcomm clock-controller driver exposes provider arrays whose indexes must match these values. Consumer drivers later resolve those phandles through common clock, reset-controller, or genpd APIs.

## State and Persistence Behavior

The file owns no memory, locks, hardware registers, or persistent storage. Its state is the ABI value assigned to each macro. Those values persist in compiled DTBs and out-of-tree device trees, so renumbering or deleting an existing define is a compatibility break even though no runtime state is stored here. Actual enable counts, reset assertion state, and GDSC power state are maintained by the clock/reset/power-domain drivers and hardware registers, not by this header.

## Dependencies and Integration Points

Direct source dependencies are intentionally minimal: the header has only SPDX/copyright comments, an include guard, macro definitions, and `#endif`. It is integrated by textual inclusion rather than linking. Local integration evidence: clock-controller driver references: `sources/distributed-fs/ceph-client/drivers/clk/qcom/gcc-qcs8300.c`; device-tree references: `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/monaco.dtsi`.

The semantic dependency is the matching provider implementation and its descriptor arrays. `qcom,qcs8300-gcc.h` IDs must stay aligned with driver tables for global PLLs plus bus, QUP, USB, PCIe, UFS, SDCC, camera/display/video/gpu vote, reset, and GDSC IDs. DTS consumers depend on these exact constants for properties such as `clocks`, `resets`, `power-domains`, and named clock inputs.

## Risks and Edge Cases

The main risk is ABI drift: inserting new IDs in the middle, reusing a removed value, or moving a reset/GDSC ID to a different number can silently bind a DTS consumer to the wrong hardware clock or power domain. It also exports reset IDs (`GCC_EMAC0_BCR`=0 through `GCC_VIDEO_AXI1_CLK_ARES`=28). Power-domain/GDSC IDs are exported as `GCC_EMAC0_GDSC`=0 through `GCC_USB30_PRIM_GDSC`=5. Shared names such as PLLs, XO/sleep sources, bus clocks, and GDSCs are easy to copy between SoCs, but the numeric ordering must follow this specific provider, not a visually similar controller. Because the file is pure macros, the compiler provides little semantic checking beyond duplicate definitions and include-guard correctness.

## Test Signals

Useful validation includes building the relevant `drivers/clk/qcom` object with this header, compiling DTBs that include `qcom,qcs8300-gcc.h`, and running `dtbs_check`/binding-schema checks for the affected SoC. Runtime smoke tests are provider probe success without missing clock/reset IDs, absence of `-ENOENT`/`-EINVAL` from clock lookups, expected entries under common-clock debugfs, and successful bring-up of consumers in the exported domain set: global PLLs plus bus, QUP, USB, PCIe, UFS, SDCC, camera/display/video/gpu vote, reset, and GDSC IDs. For edits, diff the numeric table against the matching driver arrays and boot at least one DTS consumer when local hardware or emulation coverage exists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,qcs8300-gcc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,qcs8300-gpucc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,qcs8300-gpucc.h

## Purpose

`sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,qcs8300-gpucc.h` defines the public device-tree numeric IDs for the Qualcomm GPU clock-controller binding associated with `qcom,qcs8300-gpucc.h` / `qcs8300`. The source was read completely for this report (17 lines). It is not executable kernel code; it is a stable binding contract included by DTS files and by the matching `drivers/clk/qcom` provider so that phandle clock, reset, and power-domain specifiers use the same indexes.

## Important APIs, Types, and Functions

There are no C functions, structs, or runtime APIs. The exported API is a set of preprocessor constants guarded by `_DT_BINDINGS_CLK_QCOM_GPUCC_QCS8300_H`. This header defines 2 clock IDs, 0 reset IDs, and 0 power-domain/GDSC IDs, for 2 numeric binding macros total.

Clock ID range: `GPU_CC_CX_ACCU_SHIFT_CLK`=23 through `GPU_CC_GX_ACCU_SHIFT_CLK`=24. Representative clocks: `GPU_CC_CX_ACCU_SHIFT_CLK`, `GPU_CC_GX_ACCU_SHIFT_CLK`.

Reset ID range: none. Representative resets: none.

Power-domain/GDSC range: none. Representative domains: none.

Macro inventory begins with:
- `GPU_CC_CX_ACCU_SHIFT_CLK` = 23 (clock, line 14)
- `GPU_CC_GX_ACCU_SHIFT_CLK` = 24 (clock, line 15)

## Control Flow

This header has no branches, calls, or runtime control flow. The effective flow is build-time and probe-time: DTS sources include the constants, the device-tree compiler stores the resulting integers in clock/reset/power-domain specifier cells, and the Qualcomm clock-controller driver exposes provider arrays whose indexes must match these values. Consumer drivers later resolve those phandles through common clock, reset-controller, or genpd APIs.

## State and Persistence Behavior

The file owns no memory, locks, hardware registers, or persistent storage. Its state is the ABI value assigned to each macro. Those values persist in compiled DTBs and out-of-tree device trees, so renumbering or deleting an existing define is a compatibility break even though no runtime state is stored here. Actual enable counts, reset assertion state, and GDSC power state are maintained by the clock/reset/power-domain drivers and hardware registers, not by this header.

## Dependencies and Integration Points

Direct source dependencies are intentionally minimal: the header has only SPDX/copyright comments, an include guard, macro definitions, and `#endif`. It is integrated by textual inclusion rather than linking. Local integration evidence: clock-controller driver references: `sources/distributed-fs/ceph-client/drivers/clk/qcom/gpucc-sa8775p.c`.

The semantic dependency is the matching provider implementation and its descriptor arrays. `qcom,qcs8300-gpucc.h` IDs must stay aligned with driver tables for GPU PLL/RCG, GMU, CX/GX, hub, memory NoC, XO/sleep, SMMU vote, reset, and GDSC IDs. DTS consumers depend on these exact constants for properties such as `clocks`, `resets`, `power-domains`, and named clock inputs.

## Risks and Edge Cases

The main risk is ABI drift: inserting new IDs in the middle, reusing a removed value, or moving a reset/GDSC ID to a different number can silently bind a DTS consumer to the wrong hardware clock or power domain. It does not export reset IDs in this clock header; reset bindings are either absent for this controller or live in a paired reset binding header/driver table. It does not export GDSC or power-domain IDs. Shared names such as PLLs, XO/sleep sources, bus clocks, and GDSCs are easy to copy between SoCs, but the numeric ordering must follow this specific provider, not a visually similar controller. Because the file is pure macros, the compiler provides little semantic checking beyond duplicate definitions and include-guard correctness.

## Test Signals

Useful validation includes building the relevant `drivers/clk/qcom` object with this header, compiling DTBs that include `qcom,qcs8300-gpucc.h`, and running `dtbs_check`/binding-schema checks for the affected SoC. Runtime smoke tests are provider probe success without missing clock/reset IDs, absence of `-ENOENT`/`-EINVAL` from clock lookups, expected entries under common-clock debugfs, and successful bring-up of consumers in the exported domain set: GPU PLL/RCG, GMU, CX/GX, hub, memory NoC, XO/sleep, SMMU vote, reset, and GDSC IDs. For edits, diff the numeric table against the matching driver arrays and boot at least one DTS consumer when local hardware or emulation coverage exists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,qcs8300-gpucc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,qdu1000-ecpricc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,qdu1000-ecpricc.h

## Purpose

`sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,qdu1000-ecpricc.h` defines the public device-tree numeric IDs for the Qualcomm eCPRI clock-controller binding associated with `qcom,qdu1000-ecpricc.h` / `qdu1000`. The source was read completely for this report (147 lines). It is not executable kernel code; it is a stable binding contract included by DTS files and by the matching `drivers/clk/qcom` provider so that phandle clock, reset, and power-domain specifiers use the same indexes.

## Important APIs, Types, and Functions

There are no C functions, structs, or runtime APIs. The exported API is a set of preprocessor constants guarded by `_DT_BINDINGS_CLK_QCOM_ECPRI_CC_QDU1000_H`. This header defines 126 clock IDs, 8 reset IDs, and 0 power-domain/GDSC IDs, for 134 numeric binding macros total.

Clock ID range: `ECPRI_CC_PLL0`=0 through `ECPRI_CC_PHY4_LANE3_TX_CLK`=125. Representative clocks: `ECPRI_CC_PLL0`, `ECPRI_CC_PLL1`, `ECPRI_CC_ECPRI_CG_CLK`, `ECPRI_CC_ECPRI_CLK_SRC`, `ECPRI_CC_ECPRI_DMA_CLK`, `ECPRI_CC_ECPRI_DMA_CLK_SRC`, ... `ECPRI_CC_PHY4_LANE1_RX_CLK`, `ECPRI_CC_PHY4_LANE1_TX_CLK`, `ECPRI_CC_PHY4_LANE2_RX_CLK`, `ECPRI_CC_PHY4_LANE2_TX_CLK`, `ECPRI_CC_PHY4_LANE3_RX_CLK`, `ECPRI_CC_PHY4_LANE3_TX_CLK`.

Reset ID range: `ECPRI_CC_CLK_CTL_TOP_ECPRI_CC_ECPRI_SS_BCR`=0 through `ECPRI_CC_CLK_CTL_TOP_ECPRI_CC_NOC_BCR`=7. Representative resets: `ECPRI_CC_CLK_CTL_TOP_ECPRI_CC_ECPRI_SS_BCR`, `ECPRI_CC_CLK_CTL_TOP_ECPRI_CC_ETH_C2C_BCR`, `ECPRI_CC_CLK_CTL_TOP_ECPRI_CC_ETH_FH0_BCR`, `ECPRI_CC_CLK_CTL_TOP_ECPRI_CC_ETH_FH1_BCR`, `ECPRI_CC_CLK_CTL_TOP_ECPRI_CC_ETH_FH2_BCR`, `ECPRI_CC_CLK_CTL_TOP_ECPRI_CC_ETH_WRAPPER_TOP_BCR`, `ECPRI_CC_CLK_CTL_TOP_ECPRI_CC_MODEM_BCR`, `ECPRI_CC_CLK_CTL_TOP_ECPRI_CC_NOC_BCR`.

Power-domain/GDSC range: none. Representative domains: none.

Macro inventory begins with:
- `ECPRI_CC_PLL0` = 0 (clock, line 10)
- `ECPRI_CC_PLL1` = 1 (clock, line 11)
- `ECPRI_CC_ECPRI_CG_CLK` = 2 (clock, line 12)
- `ECPRI_CC_ECPRI_CLK_SRC` = 3 (clock, line 13)
- `ECPRI_CC_ECPRI_DMA_CLK` = 4 (clock, line 14)
- `ECPRI_CC_ECPRI_DMA_CLK_SRC` = 5 (clock, line 15)
- `ECPRI_CC_ECPRI_DMA_NOC_CLK` = 6 (clock, line 16)
- `ECPRI_CC_ECPRI_FAST_CLK` = 7 (clock, line 17)
- `ECPRI_CC_ECPRI_FAST_CLK_SRC` = 8 (clock, line 18)
- `ECPRI_CC_ECPRI_FAST_DIV2_CLK` = 9 (clock, line 19)
- ... 124 additional numeric binding macros continue in the same contiguous namespace sections.

## Control Flow

This header has no branches, calls, or runtime control flow. The effective flow is build-time and probe-time: DTS sources include the constants, the device-tree compiler stores the resulting integers in clock/reset/power-domain specifier cells, and the Qualcomm clock-controller driver exposes provider arrays whose indexes must match these values. Consumer drivers later resolve those phandles through common clock, reset-controller, or genpd APIs.

## State and Persistence Behavior

The file owns no memory, locks, hardware registers, or persistent storage. Its state is the ABI value assigned to each macro. Those values persist in compiled DTBs and out-of-tree device trees, so renumbering or deleting an existing define is a compatibility break even though no runtime state is stored here. Actual enable counts, reset assertion state, and GDSC power state are maintained by the clock/reset/power-domain drivers and hardware registers, not by this header.

## Dependencies and Integration Points

Direct source dependencies are intentionally minimal: the header has only SPDX/copyright comments, an include guard, macro definitions, and `#endif`. It is integrated by textual inclusion rather than linking. Local integration evidence: clock-controller driver references: `sources/distributed-fs/ceph-client/drivers/clk/qcom/ecpricc-qdu1000.c`.

The semantic dependency is the matching provider implementation and its descriptor arrays. `qcom,qdu1000-ecpricc.h` IDs must stay aligned with driver tables for eCPRI, Ethernet/PCS, PTP, DCC, AHB, AXI, memory, and PHY clock/reset IDs. DTS consumers depend on these exact constants for properties such as `clocks`, `resets`, `power-domains`, and named clock inputs.

## Risks and Edge Cases

The main risk is ABI drift: inserting new IDs in the middle, reusing a removed value, or moving a reset/GDSC ID to a different number can silently bind a DTS consumer to the wrong hardware clock or power domain. It also exports reset IDs (`ECPRI_CC_CLK_CTL_TOP_ECPRI_CC_ECPRI_SS_BCR`=0 through `ECPRI_CC_CLK_CTL_TOP_ECPRI_CC_NOC_BCR`=7). It does not export GDSC or power-domain IDs. Shared names such as PLLs, XO/sleep sources, bus clocks, and GDSCs are easy to copy between SoCs, but the numeric ordering must follow this specific provider, not a visually similar controller. Because the file is pure macros, the compiler provides little semantic checking beyond duplicate definitions and include-guard correctness.

## Test Signals

Useful validation includes building the relevant `drivers/clk/qcom` object with this header, compiling DTBs that include `qcom,qdu1000-ecpricc.h`, and running `dtbs_check`/binding-schema checks for the affected SoC. Runtime smoke tests are provider probe success without missing clock/reset IDs, absence of `-ENOENT`/`-EINVAL` from clock lookups, expected entries under common-clock debugfs, and successful bring-up of consumers in the exported domain set: eCPRI, Ethernet/PCS, PTP, DCC, AHB, AXI, memory, and PHY clock/reset IDs. For edits, diff the numeric table against the matching driver arrays and boot at least one DTS consumer when local hardware or emulation coverage exists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,qdu1000-ecpricc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,qdu1000-gcc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,qdu1000-gcc.h

## Purpose

`sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,qdu1000-gcc.h` defines the public device-tree numeric IDs for the Qualcomm global clock-controller binding associated with `qcom,qdu1000-gcc.h` / `qdu1000`. The source was read completely for this report (177 lines). It is not executable kernel code; it is a stable binding contract included by DTS files and by the matching `drivers/clk/qcom` provider so that phandle clock, reset, and power-domain specifiers use the same indexes.

## Important APIs, Types, and Functions

There are no C functions, structs, or runtime APIs. The exported API is a set of preprocessor constants guarded by `_DT_BINDINGS_CLK_QCOM_GCC_QDU1000_H`. This header defines 133 clock IDs, 26 reset IDs, and 3 power-domain/GDSC IDs, for 162 numeric binding macros total.

Clock ID range: `GCC_GPLL0`=0 through `GCC_DDRSS_ECPRI_GSI_CLK`=132. Representative clocks: `GCC_GPLL0`, `GCC_GPLL0_OUT_EVEN`, `GCC_GPLL1`, `GCC_GPLL2`, `GCC_GPLL2_OUT_EVEN`, `GCC_GPLL3`, ... `GCC_ETH_DBG_C2C_HM_APB_CLK`, `GCC_AGGRE_NOC_ECPRI_GSI_CLK`, `GCC_PCIE_0_PIPE_CLK_SRC`, `GCC_PCIE_0_PHY_AUX_CLK_SRC`, `GCC_GPLL1_OUT_EVEN`, `GCC_DDRSS_ECPRI_GSI_CLK`.

Reset ID range: `GCC_ECPRI_CC_BCR`=0 through `GCC_USB_PHY_CFG_AHB2PHY_BCR`=25. Representative resets: `GCC_ECPRI_CC_BCR`, `GCC_ECPRI_SS_BCR`, `GCC_ETH_WRAPPER_BCR`, `GCC_PCIE_0_BCR`, `GCC_PCIE_0_LINK_DOWN_BCR`, `GCC_PCIE_0_NOCSR_COM_PHY_BCR`, ... `GCC_USB3_DP_PHY_SEC_BCR`, `GCC_USB3_PHY_PRIM_BCR`, `GCC_USB3_PHY_SEC_BCR`, `GCC_USB3PHY_PHY_PRIM_BCR`, `GCC_USB3PHY_PHY_SEC_BCR`, `GCC_USB_PHY_CFG_AHB2PHY_BCR`.

Power-domain/GDSC range: `PCIE_0_GDSC`=0 through `USB30_PRIM_GDSC`=2. Representative domains: `PCIE_0_GDSC`, `PCIE_0_PHY_GDSC`, `USB30_PRIM_GDSC`.

Macro inventory begins with:
- `GCC_GPLL0` = 0 (clock, line 10)
- `GCC_GPLL0_OUT_EVEN` = 1 (clock, line 11)
- `GCC_GPLL1` = 2 (clock, line 12)
- `GCC_GPLL2` = 3 (clock, line 13)
- `GCC_GPLL2_OUT_EVEN` = 4 (clock, line 14)
- `GCC_GPLL3` = 5 (clock, line 15)
- `GCC_GPLL4` = 6 (clock, line 16)
- `GCC_GPLL5` = 7 (clock, line 17)
- `GCC_GPLL5_OUT_EVEN` = 8 (clock, line 18)
- `GCC_GPLL6` = 9 (clock, line 19)
- ... 152 additional numeric binding macros continue in the same contiguous namespace sections.

## Control Flow

This header has no branches, calls, or runtime control flow. The effective flow is build-time and probe-time: DTS sources include the constants, the device-tree compiler stores the resulting integers in clock/reset/power-domain specifier cells, and the Qualcomm clock-controller driver exposes provider arrays whose indexes must match these values. Consumer drivers later resolve those phandles through common clock, reset-controller, or genpd APIs.

## State and Persistence Behavior

The file owns no memory, locks, hardware registers, or persistent storage. Its state is the ABI value assigned to each macro. Those values persist in compiled DTBs and out-of-tree device trees, so renumbering or deleting an existing define is a compatibility break even though no runtime state is stored here. Actual enable counts, reset assertion state, and GDSC power state are maintained by the clock/reset/power-domain drivers and hardware registers, not by this header.

## Dependencies and Integration Points

Direct source dependencies are intentionally minimal: the header has only SPDX/copyright comments, an include guard, macro definitions, and `#endif`. It is integrated by textual inclusion rather than linking. Local integration evidence: clock-controller driver references: `sources/distributed-fs/ceph-client/drivers/clk/qcom/gcc-qdu1000.c`; device-tree references: `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/qdu1000.dtsi`.

The semantic dependency is the matching provider implementation and its descriptor arrays. `qcom,qdu1000-gcc.h` IDs must stay aligned with driver tables for global PLLs plus bus, QUP, USB, PCIe, UFS, SDCC, camera/display/video/gpu vote, reset, and GDSC IDs. DTS consumers depend on these exact constants for properties such as `clocks`, `resets`, `power-domains`, and named clock inputs.

## Risks and Edge Cases

The main risk is ABI drift: inserting new IDs in the middle, reusing a removed value, or moving a reset/GDSC ID to a different number can silently bind a DTS consumer to the wrong hardware clock or power domain. It also exports reset IDs (`GCC_ECPRI_CC_BCR`=0 through `GCC_USB_PHY_CFG_AHB2PHY_BCR`=25). Power-domain/GDSC IDs are exported as `PCIE_0_GDSC`=0 through `USB30_PRIM_GDSC`=2. Shared names such as PLLs, XO/sleep sources, bus clocks, and GDSCs are easy to copy between SoCs, but the numeric ordering must follow this specific provider, not a visually similar controller. Because the file is pure macros, the compiler provides little semantic checking beyond duplicate definitions and include-guard correctness.

## Test Signals

Useful validation includes building the relevant `drivers/clk/qcom` object with this header, compiling DTBs that include `qcom,qdu1000-gcc.h`, and running `dtbs_check`/binding-schema checks for the affected SoC. Runtime smoke tests are provider probe success without missing clock/reset IDs, absence of `-ENOENT`/`-EINVAL` from clock lookups, expected entries under common-clock debugfs, and successful bring-up of consumers in the exported domain set: global PLLs plus bus, QUP, USB, PCIe, UFS, SDCC, camera/display/video/gpu vote, reset, and GDSC IDs. For edits, diff the numeric table against the matching driver arrays and boot at least one DTS consumer when local hardware or emulation coverage exists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,qdu1000-gcc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,rpmcc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,rpmcc.h

## Purpose

`sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,rpmcc.h` defines the public device-tree numeric IDs for the Qualcomm RPM/RPM-SMD clock binding associated with `qcom,rpmcc.h` / `rpmcc`. The source was read completely for this report (178 lines). It is not executable kernel code; it is a stable binding contract included by DTS files and by the matching `drivers/clk/qcom` provider so that phandle clock, reset, and power-domain specifiers use the same indexes. This header is shared by multiple DTS or driver consumers in this tree, so numeric stability matters beyond one board file.

## Important APIs, Types, and Functions

There are no C functions, structs, or runtime APIs. The exported API is a set of preprocessor constants guarded by `_DT_BINDINGS_CLK_MSM_RPMCC_H`. This header defines 165 clock IDs, 0 reset IDs, and 0 power-domain/GDSC IDs, for 165 numeric binding macros total.

Clock ID range: `RPM_PXO_CLK`=0 through `RPM_SMD_BB_CLK3_A_PIN`=130. Representative clocks: `RPM_PXO_CLK`, `RPM_PXO_A_CLK`, `RPM_CXO_CLK`, `RPM_CXO_A_CLK`, `RPM_APPS_FABRIC_CLK`, `RPM_APPS_FABRIC_A_CLK`, ... `RPM_SMD_LN_BB_CLK_PIN`, `RPM_SMD_LN_BB_A_CLK_PIN`, `RPM_SMD_BB_CLK3`, `RPM_SMD_BB_CLK3_A`, `RPM_SMD_BB_CLK3_PIN`, `RPM_SMD_BB_CLK3_A_PIN`.

Reset ID range: none. Representative resets: none.

Power-domain/GDSC range: none. Representative domains: none.

Macro inventory begins with:
- `RPM_PXO_CLK` = 0 (clock, line 10)
- `RPM_PXO_A_CLK` = 1 (clock, line 11)
- `RPM_CXO_CLK` = 2 (clock, line 12)
- `RPM_CXO_A_CLK` = 3 (clock, line 13)
- `RPM_APPS_FABRIC_CLK` = 4 (clock, line 14)
- `RPM_APPS_FABRIC_A_CLK` = 5 (clock, line 15)
- `RPM_CFPB_CLK` = 6 (clock, line 16)
- `RPM_CFPB_A_CLK` = 7 (clock, line 17)
- `RPM_QDSS_CLK` = 8 (clock, line 18)
- `RPM_QDSS_A_CLK` = 9 (clock, line 19)
- ... 155 additional numeric binding macros continue in the same contiguous namespace sections.

## Control Flow

This header has no branches, calls, or runtime control flow. The effective flow is build-time and probe-time: DTS sources include the constants, the device-tree compiler stores the resulting integers in clock/reset/power-domain specifier cells, and the Qualcomm clock-controller driver exposes provider arrays whose indexes must match these values. Consumer drivers later resolve those phandles through common clock, reset-controller, or genpd APIs.

## State and Persistence Behavior

The file owns no memory, locks, hardware registers, or persistent storage. Its state is the ABI value assigned to each macro. Those values persist in compiled DTBs and out-of-tree device trees, so renumbering or deleting an existing define is a compatibility break even though no runtime state is stored here. Actual enable counts, reset assertion state, and GDSC power state are maintained by the clock/reset/power-domain drivers and hardware registers, not by this header.

## Dependencies and Integration Points

Direct source dependencies are intentionally minimal: the header has only SPDX/copyright comments, an include guard, macro definitions, and `#endif`. It is integrated by textual inclusion rather than linking. Local integration evidence: clock-controller driver references: `sources/distributed-fs/ceph-client/drivers/clk/qcom/clk-rpm.c`, `sources/distributed-fs/ceph-client/drivers/clk/qcom/clk-smd-rpm.c`; device-tree references: `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/msm8937.dtsi`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/msm8976.dtsi`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/msm8917.dtsi`, `sources/distributed-fs/ceph-client/arch/arm/boot/dts/qcom/qcom-msm8226.dtsi`, `sources/distributed-fs/ceph-client/arch/arm/boot/dts/qcom/qcom-msm8974.dtsi`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/sdm630.dtsi`, `sources/distributed-fs/ceph-client/arch/arm/boot/dts/qcom/qcom-apq8064.dtsi`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/msm8998.dtsi` and 11 more.

The semantic dependency is the matching provider implementation and its descriptor arrays. `qcom,rpmcc.h` IDs must stay aligned with driver tables for legacy RPM and SMD RPM fabric, XO, baseband, RF, BIMC, QDSS, IPA, crypto, and multimedia clocks. DTS consumers depend on these exact constants for properties such as `clocks`, `resets`, `power-domains`, and named clock inputs.

## Risks and Edge Cases

The main risk is ABI drift: inserting new IDs in the middle, reusing a removed value, or moving a reset/GDSC ID to a different number can silently bind a DTS consumer to the wrong hardware clock or power domain. It does not export reset IDs in this clock header; reset bindings are either absent for this controller or live in a paired reset binding header/driver table. It does not export GDSC or power-domain IDs. Shared names such as PLLs, XO/sleep sources, bus clocks, and GDSCs are easy to copy between SoCs, but the numeric ordering must follow this specific provider, not a visually similar controller. Because the file is pure macros, the compiler provides little semantic checking beyond duplicate definitions and include-guard correctness.

## Test Signals

Useful validation includes building the relevant `drivers/clk/qcom` object with this header, compiling DTBs that include `qcom,rpmcc.h`, and running `dtbs_check`/binding-schema checks for the affected SoC. Runtime smoke tests are provider probe success without missing clock/reset IDs, absence of `-ENOENT`/`-EINVAL` from clock lookups, expected entries under common-clock debugfs, and successful bring-up of consumers in the exported domain set: legacy RPM and SMD RPM fabric, XO, baseband, RF, BIMC, QDSS, IPA, crypto, and multimedia clocks. For edits, diff the numeric table against the matching driver arrays and boot at least one DTS consumer when local hardware or emulation coverage exists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,rpmcc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,rpmh.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,rpmh.h

## Purpose

`sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,rpmh.h` defines the public device-tree numeric IDs for the Qualcomm RPMh always-on/resource-state clock binding associated with `qcom,rpmh.h` / `rpmh`. The source was read completely for this report (37 lines). It is not executable kernel code; it is a stable binding contract included by DTS files and by the matching `drivers/clk/qcom` provider so that phandle clock, reset, and power-domain specifiers use the same indexes. This header is shared by multiple DTS or driver consumers in this tree, so numeric stability matters beyond one board file.

## Important APIs, Types, and Functions

There are no C functions, structs, or runtime APIs. The exported API is a set of preprocessor constants guarded by `_DT_BINDINGS_CLK_MSM_RPMH_H`. This header defines 27 clock IDs, 0 reset IDs, and 0 power-domain/GDSC IDs, for 27 numeric binding macros total.

Clock ID range: `RPMH_CXO_CLK`=0 through `RPMH_QLINK_CLK_A`=26. Representative clocks: `RPMH_CXO_CLK`, `RPMH_CXO_CLK_A`, `RPMH_LN_BB_CLK2`, `RPMH_LN_BB_CLK2_A`, `RPMH_LN_BB_CLK3`, `RPMH_LN_BB_CLK3_A`, ... `RPMH_RF_CLK5`, `RPMH_RF_CLK5_A`, `RPMH_PKA_CLK`, `RPMH_HWKM_CLK`, `RPMH_QLINK_CLK`, `RPMH_QLINK_CLK_A`.

Reset ID range: none. Representative resets: none.

Power-domain/GDSC range: none. Representative domains: none.

Macro inventory begins with:
- `RPMH_CXO_CLK` = 0 (clock, line 9)
- `RPMH_CXO_CLK_A` = 1 (clock, line 10)
- `RPMH_LN_BB_CLK2` = 2 (clock, line 11)
- `RPMH_LN_BB_CLK2_A` = 3 (clock, line 12)
- `RPMH_LN_BB_CLK3` = 4 (clock, line 13)
- `RPMH_LN_BB_CLK3_A` = 5 (clock, line 14)
- `RPMH_RF_CLK1` = 6 (clock, line 15)
- `RPMH_RF_CLK1_A` = 7 (clock, line 16)
- `RPMH_RF_CLK2` = 8 (clock, line 17)
- `RPMH_RF_CLK2_A` = 9 (clock, line 18)
- ... 17 additional numeric binding macros continue in the same contiguous namespace sections.

## Control Flow

This header has no branches, calls, or runtime control flow. The effective flow is build-time and probe-time: DTS sources include the constants, the device-tree compiler stores the resulting integers in clock/reset/power-domain specifier cells, and the Qualcomm clock-controller driver exposes provider arrays whose indexes must match these values. Consumer drivers later resolve those phandles through common clock, reset-controller, or genpd APIs.

## State and Persistence Behavior

The file owns no memory, locks, hardware registers, or persistent storage. Its state is the ABI value assigned to each macro. Those values persist in compiled DTBs and out-of-tree device trees, so renumbering or deleting an existing define is a compatibility break even though no runtime state is stored here. Actual enable counts, reset assertion state, and GDSC power state are maintained by the clock/reset/power-domain drivers and hardware registers, not by this header.

## Dependencies and Integration Points

Direct source dependencies are intentionally minimal: the header has only SPDX/copyright comments, an include guard, macro definitions, and `#endif`. It is integrated by textual inclusion rather than linking. Local integration evidence: clock-controller driver references: `sources/distributed-fs/ceph-client/drivers/clk/qcom/clk-rpmh.c`; device-tree references: `sources/distributed-fs/ceph-client/arch/arm/boot/dts/qcom/qcom-sdx55.dtsi`, `sources/distributed-fs/ceph-client/arch/arm/boot/dts/qcom/qcom-sdx65.dtsi`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/sm8250.dtsi`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/sm4450.dtsi`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/eliza.dtsi`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/kaanapali.dtsi`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/sc8180x.dtsi`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/hamoa.dtsi` and 20 more.

The semantic dependency is the matching provider implementation and its descriptor arrays. `qcom,rpmh.h` IDs must stay aligned with driver tables for RPMh resource clocks such as CXO, RF, baseband, IPA, crypto, QPIC, and QLINK sources. DTS consumers depend on these exact constants for properties such as `clocks`, `resets`, `power-domains`, and named clock inputs.

## Risks and Edge Cases

The main risk is ABI drift: inserting new IDs in the middle, reusing a removed value, or moving a reset/GDSC ID to a different number can silently bind a DTS consumer to the wrong hardware clock or power domain. It does not export reset IDs in this clock header; reset bindings are either absent for this controller or live in a paired reset binding header/driver table. It does not export GDSC or power-domain IDs. Shared names such as PLLs, XO/sleep sources, bus clocks, and GDSCs are easy to copy between SoCs, but the numeric ordering must follow this specific provider, not a visually similar controller. Because the file is pure macros, the compiler provides little semantic checking beyond duplicate definitions and include-guard correctness.

## Test Signals

Useful validation includes building the relevant `drivers/clk/qcom` object with this header, compiling DTBs that include `qcom,rpmh.h`, and running `dtbs_check`/binding-schema checks for the affected SoC. Runtime smoke tests are provider probe success without missing clock/reset IDs, absence of `-ENOENT`/`-EINVAL` from clock lookups, expected entries under common-clock debugfs, and successful bring-up of consumers in the exported domain set: RPMh resource clocks such as CXO, RF, baseband, IPA, crypto, QPIC, and QLINK sources. For edits, diff the numeric table against the matching driver arrays and boot at least one DTS consumer when local hardware or emulation coverage exists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,rpmh.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sa8775p-camcc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sa8775p-camcc.h

## Purpose

`sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sa8775p-camcc.h` defines the public device-tree numeric IDs for the Qualcomm camera clock-controller binding associated with `qcom,sa8775p-camcc.h` / `sa8775p`. The source was read completely for this report (108 lines). It is not executable kernel code; it is a stable binding contract included by DTS files and by the matching `drivers/clk/qcom` provider so that phandle clock, reset, and power-domain specifiers use the same indexes. This header is shared by multiple DTS or driver consumers in this tree, so numeric stability matters beyond one board file.

## Important APIs, Types, and Functions

There are no C functions, structs, or runtime APIs. The exported API is a set of preprocessor constants guarded by `_DT_BINDINGS_CLK_QCOM_SA8775P_CAM_CC_H`. This header defines 86 clock IDs, 6 reset IDs, and 1 power-domain/GDSC ID, for 93 numeric binding macros total.

Clock ID range: `CAM_CC_CAMNOC_AXI_CLK`=0 through `CAM_CC_QDSS_DEBUG_XO_CLK`=85. Representative clocks: `CAM_CC_CAMNOC_AXI_CLK`, `CAM_CC_CAMNOC_AXI_CLK_SRC`, `CAM_CC_CAMNOC_DCD_XO_CLK`, `CAM_CC_CAMNOC_XO_CLK`, `CAM_CC_CCI_0_CLK`, `CAM_CC_CCI_0_CLK_SRC`, ... `CAM_CC_SLEEP_CLK`, `CAM_CC_SLEEP_CLK_SRC`, `CAM_CC_SLOW_AHB_CLK_SRC`, `CAM_CC_SM_OBS_CLK`, `CAM_CC_XO_CLK_SRC`, `CAM_CC_QDSS_DEBUG_XO_CLK`.

Reset ID range: `CAM_CC_ICP_BCR`=0 through `CAM_CC_SFE_LITE_1_BCR`=5. Representative resets: `CAM_CC_ICP_BCR`, `CAM_CC_IFE_0_BCR`, `CAM_CC_IFE_1_BCR`, `CAM_CC_IPE_0_BCR`, `CAM_CC_SFE_LITE_0_BCR`, `CAM_CC_SFE_LITE_1_BCR`.

Power-domain/GDSC range: `CAM_CC_TITAN_TOP_GDSC`=0 through `CAM_CC_TITAN_TOP_GDSC`=0. Representative domains: `CAM_CC_TITAN_TOP_GDSC`.

Macro inventory begins with:
- `CAM_CC_CAMNOC_AXI_CLK` = 0 (clock, line 10)
- `CAM_CC_CAMNOC_AXI_CLK_SRC` = 1 (clock, line 11)
- `CAM_CC_CAMNOC_DCD_XO_CLK` = 2 (clock, line 12)
- `CAM_CC_CAMNOC_XO_CLK` = 3 (clock, line 13)
- `CAM_CC_CCI_0_CLK` = 4 (clock, line 14)
- `CAM_CC_CCI_0_CLK_SRC` = 5 (clock, line 15)
- `CAM_CC_CCI_1_CLK` = 6 (clock, line 16)
- `CAM_CC_CCI_1_CLK_SRC` = 7 (clock, line 17)
- `CAM_CC_CCI_2_CLK` = 8 (clock, line 18)
- `CAM_CC_CCI_2_CLK_SRC` = 9 (clock, line 19)
- ... 83 additional numeric binding macros continue in the same contiguous namespace sections.

## Control Flow

This header has no branches, calls, or runtime control flow. The effective flow is build-time and probe-time: DTS sources include the constants, the device-tree compiler stores the resulting integers in clock/reset/power-domain specifier cells, and the Qualcomm clock-controller driver exposes provider arrays whose indexes must match these values. Consumer drivers later resolve those phandles through common clock, reset-controller, or genpd APIs.

## State and Persistence Behavior

The file owns no memory, locks, hardware registers, or persistent storage. Its state is the ABI value assigned to each macro. Those values persist in compiled DTBs and out-of-tree device trees, so renumbering or deleting an existing define is a compatibility break even though no runtime state is stored here. Actual enable counts, reset assertion state, and GDSC power state are maintained by the clock/reset/power-domain drivers and hardware registers, not by this header.

## Dependencies and Integration Points

Direct source dependencies are intentionally minimal: the header has only SPDX/copyright comments, an include guard, macro definitions, and `#endif`. It is integrated by textual inclusion rather than linking. Local integration evidence: device-tree references: `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/monaco-evk-camera-imx577.dtso`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/lemans-evk-camera-csi1-imx577.dtso`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/lemans-evk-camera.dtso`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/lemans.dtsi`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/monaco.dtsi`.

The semantic dependency is the matching provider implementation and its descriptor arrays. `qcom,sa8775p-camcc.h` IDs must stay aligned with driver tables for camera PLLs, MCLKs, CSI/CSIPHY timers, IFE/TFE/SFE/BPS/IPE/JPEG/CPAS fabric clocks, resets, and camera GDSCs. DTS consumers depend on these exact constants for properties such as `clocks`, `resets`, `power-domains`, and named clock inputs.

## Risks and Edge Cases

The main risk is ABI drift: inserting new IDs in the middle, reusing a removed value, or moving a reset/GDSC ID to a different number can silently bind a DTS consumer to the wrong hardware clock or power domain. It also exports reset IDs (`CAM_CC_ICP_BCR`=0 through `CAM_CC_SFE_LITE_1_BCR`=5). Power-domain/GDSC IDs are exported as `CAM_CC_TITAN_TOP_GDSC`=0 through `CAM_CC_TITAN_TOP_GDSC`=0. Shared names such as PLLs, XO/sleep sources, bus clocks, and GDSCs are easy to copy between SoCs, but the numeric ordering must follow this specific provider, not a visually similar controller. Because the file is pure macros, the compiler provides little semantic checking beyond duplicate definitions and include-guard correctness.

## Test Signals

Useful validation includes building the relevant `drivers/clk/qcom` object with this header, compiling DTBs that include `qcom,sa8775p-camcc.h`, and running `dtbs_check`/binding-schema checks for the affected SoC. Runtime smoke tests are provider probe success without missing clock/reset IDs, absence of `-ENOENT`/`-EINVAL` from clock lookups, expected entries under common-clock debugfs, and successful bring-up of consumers in the exported domain set: camera PLLs, MCLKs, CSI/CSIPHY timers, IFE/TFE/SFE/BPS/IPE/JPEG/CPAS fabric clocks, resets, and camera GDSCs. For edits, diff the numeric table against the matching driver arrays and boot at least one DTS consumer when local hardware or emulation coverage exists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sa8775p-camcc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sa8775p-dispcc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sa8775p-dispcc.h

## Purpose

`sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sa8775p-dispcc.h` defines the public device-tree numeric IDs for the Qualcomm display clock-controller binding associated with `qcom,sa8775p-dispcc.h` / `sa8775p`. The source was read completely for this report (87 lines). It is not executable kernel code; it is a stable binding contract included by DTS files and by the matching `drivers/clk/qcom` provider so that phandle clock, reset, and power-domain specifiers use the same indexes. This header is shared by multiple DTS or driver consumers in this tree, so numeric stability matters beyond one board file.

## Important APIs, Types, and Functions

There are no C functions, structs, or runtime APIs. The exported API is a set of preprocessor constants guarded by `_DT_BINDINGS_CLK_QCOM_SA8775P_DISP_CC_H`. This header defines 68 clock IDs, 2 reset IDs, and 2 power-domain/GDSC IDs, for 72 numeric binding macros total.

Clock ID range: `MDSS_DISP_CC_MDSS_AHB1_CLK`=0 through `MDSS_DISP_CC_XO_CLK_SRC`=67. Representative clocks: `MDSS_DISP_CC_MDSS_AHB1_CLK`, `MDSS_DISP_CC_MDSS_AHB_CLK`, `MDSS_DISP_CC_MDSS_AHB_CLK_SRC`, `MDSS_DISP_CC_MDSS_BYTE0_CLK`, `MDSS_DISP_CC_MDSS_BYTE0_CLK_SRC`, `MDSS_DISP_CC_MDSS_BYTE0_DIV_CLK_SRC`, ... `MDSS_DISP_CC_PLL1`, `MDSS_DISP_CC_SLEEP_CLK`, `MDSS_DISP_CC_SLEEP_CLK_SRC`, `MDSS_DISP_CC_SM_OBS_CLK`, `MDSS_DISP_CC_XO_CLK`, `MDSS_DISP_CC_XO_CLK_SRC`.

Reset ID range: `MDSS_DISP_CC_MDSS_CORE_BCR`=0 through `MDSS_DISP_CC_MDSS_RSCC_BCR`=1. Representative resets: `MDSS_DISP_CC_MDSS_CORE_BCR`, `MDSS_DISP_CC_MDSS_RSCC_BCR`.

Power-domain/GDSC range: `MDSS_DISP_CC_MDSS_CORE_GDSC`=0 through `MDSS_DISP_CC_MDSS_CORE_INT2_GDSC`=1. Representative domains: `MDSS_DISP_CC_MDSS_CORE_GDSC`, `MDSS_DISP_CC_MDSS_CORE_INT2_GDSC`.

Macro inventory begins with:
- `MDSS_DISP_CC_MDSS_AHB1_CLK` = 0 (clock, line 10)
- `MDSS_DISP_CC_MDSS_AHB_CLK` = 1 (clock, line 11)
- `MDSS_DISP_CC_MDSS_AHB_CLK_SRC` = 2 (clock, line 12)
- `MDSS_DISP_CC_MDSS_BYTE0_CLK` = 3 (clock, line 13)
- `MDSS_DISP_CC_MDSS_BYTE0_CLK_SRC` = 4 (clock, line 14)
- `MDSS_DISP_CC_MDSS_BYTE0_DIV_CLK_SRC` = 5 (clock, line 15)
- `MDSS_DISP_CC_MDSS_BYTE0_INTF_CLK` = 6 (clock, line 16)
- `MDSS_DISP_CC_MDSS_BYTE1_CLK` = 7 (clock, line 17)
- `MDSS_DISP_CC_MDSS_BYTE1_CLK_SRC` = 8 (clock, line 18)
- `MDSS_DISP_CC_MDSS_BYTE1_DIV_CLK_SRC` = 9 (clock, line 19)
- ... 62 additional numeric binding macros continue in the same contiguous namespace sections.

## Control Flow

This header has no branches, calls, or runtime control flow. The effective flow is build-time and probe-time: DTS sources include the constants, the device-tree compiler stores the resulting integers in clock/reset/power-domain specifier cells, and the Qualcomm clock-controller driver exposes provider arrays whose indexes must match these values. Consumer drivers later resolve those phandles through common clock, reset-controller, or genpd APIs.

## State and Persistence Behavior

The file owns no memory, locks, hardware registers, or persistent storage. Its state is the ABI value assigned to each macro. Those values persist in compiled DTBs and out-of-tree device trees, so renumbering or deleting an existing define is a compatibility break even though no runtime state is stored here. Actual enable counts, reset assertion state, and GDSC power state are maintained by the clock/reset/power-domain drivers and hardware registers, not by this header.

## Dependencies and Integration Points

Direct source dependencies are intentionally minimal: the header has only SPDX/copyright comments, an include guard, macro definitions, and `#endif`. It is integrated by textual inclusion rather than linking. Local integration evidence: clock-controller driver references: `sources/distributed-fs/ceph-client/drivers/clk/qcom/dispcc1-sa8775p.c`, `sources/distributed-fs/ceph-client/drivers/clk/qcom/dispcc0-sa8775p.c`; device-tree references: `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/lemans.dtsi`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/monaco.dtsi`.

The semantic dependency is the matching provider implementation and its descriptor arrays. `qcom,sa8775p-dispcc.h` IDs must stay aligned with driver tables for MDSS AHB/AXI, MDP, DSI byte/escape/pixel, DisplayPort link/pixel/aux, vsync, resets, and display GDSCs. DTS consumers depend on these exact constants for properties such as `clocks`, `resets`, `power-domains`, and named clock inputs.

## Risks and Edge Cases

The main risk is ABI drift: inserting new IDs in the middle, reusing a removed value, or moving a reset/GDSC ID to a different number can silently bind a DTS consumer to the wrong hardware clock or power domain. It also exports reset IDs (`MDSS_DISP_CC_MDSS_CORE_BCR`=0 through `MDSS_DISP_CC_MDSS_RSCC_BCR`=1). Power-domain/GDSC IDs are exported as `MDSS_DISP_CC_MDSS_CORE_GDSC`=0 through `MDSS_DISP_CC_MDSS_CORE_INT2_GDSC`=1. Shared names such as PLLs, XO/sleep sources, bus clocks, and GDSCs are easy to copy between SoCs, but the numeric ordering must follow this specific provider, not a visually similar controller. Because the file is pure macros, the compiler provides little semantic checking beyond duplicate definitions and include-guard correctness.

## Test Signals

Useful validation includes building the relevant `drivers/clk/qcom` object with this header, compiling DTBs that include `qcom,sa8775p-dispcc.h`, and running `dtbs_check`/binding-schema checks for the affected SoC. Runtime smoke tests are provider probe success without missing clock/reset IDs, absence of `-ENOENT`/`-EINVAL` from clock lookups, expected entries under common-clock debugfs, and successful bring-up of consumers in the exported domain set: MDSS AHB/AXI, MDP, DSI byte/escape/pixel, DisplayPort link/pixel/aux, vsync, resets, and display GDSCs. For edits, diff the numeric table against the matching driver arrays and boot at least one DTS consumer when local hardware or emulation coverage exists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sa8775p-dispcc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sa8775p-gcc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sa8775p-gcc.h

## Purpose

`sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sa8775p-gcc.h` defines the public device-tree numeric IDs for the Qualcomm global clock-controller binding associated with `qcom,sa8775p-gcc.h` / `sa8775p`. The source was read completely for this report (320 lines). It is not executable kernel code; it is a stable binding contract included by DTS files and by the matching `drivers/clk/qcom` provider so that phandle clock, reset, and power-domain specifiers use the same indexes.

## Important APIs, Types, and Functions

There are no C functions, structs, or runtime APIs. The exported API is a set of preprocessor constants guarded by `_DT_BINDINGS_CLK_QCOM_GCC_SA8775P_H`. This header defines 249 clock IDs, 46 reset IDs, and 9 power-domain/GDSC IDs, for 304 numeric binding macros total.

Clock ID range: `GCC_GPLL0`=0 through `GCC_UFS_PHY_UNIPRO_CORE_HW_CTL_CLK`=248. Representative clocks: `GCC_GPLL0`, `GCC_GPLL0_OUT_EVEN`, `GCC_GPLL1`, `GCC_GPLL4`, `GCC_GPLL5`, `GCC_GPLL7`, ... `GCC_VIDEO_XO_CLK`, `GCC_AGGRE_UFS_PHY_AXI_HW_CTL_CLK`, `GCC_UFS_PHY_AXI_HW_CTL_CLK`, `GCC_UFS_PHY_ICE_CORE_HW_CTL_CLK`, `GCC_UFS_PHY_PHY_AUX_HW_CTL_CLK`, `GCC_UFS_PHY_UNIPRO_CORE_HW_CTL_CLK`.

Reset ID range: `GCC_CAMERA_BCR`=0 through `GCC_VIDEO_AXI1_CLK_ARES`=45. Representative resets: `GCC_CAMERA_BCR`, `GCC_DISPLAY1_BCR`, `GCC_DISPLAY_BCR`, `GCC_EMAC0_BCR`, `GCC_EMAC1_BCR`, `GCC_GPU_BCR`, ... `GCC_USB3UNIPHY_PHY_MP0_BCR`, `GCC_USB3UNIPHY_PHY_MP1_BCR`, `GCC_USB_PHY_CFG_AHB2PHY_BCR`, `GCC_VIDEO_BCR`, `GCC_VIDEO_AXI0_CLK_ARES`, `GCC_VIDEO_AXI1_CLK_ARES`.

Power-domain/GDSC range: `PCIE_0_GDSC`=0 through `EMAC1_GDSC`=8. Representative domains: `PCIE_0_GDSC`, `PCIE_1_GDSC`, `UFS_CARD_GDSC`, `UFS_PHY_GDSC`, `USB20_PRIM_GDSC`, `USB30_PRIM_GDSC`, `USB30_SEC_GDSC`, `EMAC0_GDSC`, `EMAC1_GDSC`.

Macro inventory begins with:
- `GCC_GPLL0` = 0 (clock, line 11)
- `GCC_GPLL0_OUT_EVEN` = 1 (clock, line 12)
- `GCC_GPLL1` = 2 (clock, line 13)
- `GCC_GPLL4` = 3 (clock, line 14)
- `GCC_GPLL5` = 4 (clock, line 15)
- `GCC_GPLL7` = 5 (clock, line 16)
- `GCC_GPLL9` = 6 (clock, line 17)
- `GCC_AGGRE_NOC_QUPV3_AXI_CLK` = 7 (clock, line 18)
- `GCC_AGGRE_UFS_CARD_AXI_CLK` = 8 (clock, line 19)
- `GCC_AGGRE_UFS_PHY_AXI_CLK` = 9 (clock, line 20)
- ... 294 additional numeric binding macros continue in the same contiguous namespace sections.

## Control Flow

This header has no branches, calls, or runtime control flow. The effective flow is build-time and probe-time: DTS sources include the constants, the device-tree compiler stores the resulting integers in clock/reset/power-domain specifier cells, and the Qualcomm clock-controller driver exposes provider arrays whose indexes must match these values. Consumer drivers later resolve those phandles through common clock, reset-controller, or genpd APIs.

## State and Persistence Behavior

The file owns no memory, locks, hardware registers, or persistent storage. Its state is the ABI value assigned to each macro. Those values persist in compiled DTBs and out-of-tree device trees, so renumbering or deleting an existing define is a compatibility break even though no runtime state is stored here. Actual enable counts, reset assertion state, and GDSC power state are maintained by the clock/reset/power-domain drivers and hardware registers, not by this header.

## Dependencies and Integration Points

Direct source dependencies are intentionally minimal: the header has only SPDX/copyright comments, an include guard, macro definitions, and `#endif`. It is integrated by textual inclusion rather than linking. Local integration evidence: clock-controller driver references: `sources/distributed-fs/ceph-client/drivers/clk/qcom/gcc-sa8775p.c`; device-tree references: `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/lemans.dtsi`.

The semantic dependency is the matching provider implementation and its descriptor arrays. `qcom,sa8775p-gcc.h` IDs must stay aligned with driver tables for global PLLs plus bus, QUP, USB, PCIe, UFS, SDCC, camera/display/video/gpu vote, reset, and GDSC IDs. DTS consumers depend on these exact constants for properties such as `clocks`, `resets`, `power-domains`, and named clock inputs.

## Risks and Edge Cases

The main risk is ABI drift: inserting new IDs in the middle, reusing a removed value, or moving a reset/GDSC ID to a different number can silently bind a DTS consumer to the wrong hardware clock or power domain. It also exports reset IDs (`GCC_CAMERA_BCR`=0 through `GCC_VIDEO_AXI1_CLK_ARES`=45). Power-domain/GDSC IDs are exported as `PCIE_0_GDSC`=0 through `EMAC1_GDSC`=8. Shared names such as PLLs, XO/sleep sources, bus clocks, and GDSCs are easy to copy between SoCs, but the numeric ordering must follow this specific provider, not a visually similar controller. Because the file is pure macros, the compiler provides little semantic checking beyond duplicate definitions and include-guard correctness.

## Test Signals

Useful validation includes building the relevant `drivers/clk/qcom` object with this header, compiling DTBs that include `qcom,sa8775p-gcc.h`, and running `dtbs_check`/binding-schema checks for the affected SoC. Runtime smoke tests are provider probe success without missing clock/reset IDs, absence of `-ENOENT`/`-EINVAL` from clock lookups, expected entries under common-clock debugfs, and successful bring-up of consumers in the exported domain set: global PLLs plus bus, QUP, USB, PCIe, UFS, SDCC, camera/display/video/gpu vote, reset, and GDSC IDs. For edits, diff the numeric table against the matching driver arrays and boot at least one DTS consumer when local hardware or emulation coverage exists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sa8775p-gcc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sa8775p-gpucc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sa8775p-gpucc.h

## Purpose

`sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sa8775p-gpucc.h` defines the public device-tree numeric IDs for the Qualcomm GPU clock-controller binding associated with `qcom,sa8775p-gpucc.h` / `sa8775p`. The source was read completely for this report (50 lines). It is not executable kernel code; it is a stable binding contract included by DTS files and by the matching `drivers/clk/qcom` provider so that phandle clock, reset, and power-domain specifiers use the same indexes.

## Important APIs, Types, and Functions

There are no C functions, structs, or runtime APIs. The exported API is a set of preprocessor constants guarded by `_DT_BINDINGS_CLK_QCOM_GPUCC_SA8775P_H`. This header defines 23 clock IDs, 9 reset IDs, and 2 power-domain/GDSC IDs, for 34 numeric binding macros total.

Clock ID range: `GPU_CC_PLL0`=0 through `GPU_CC_XO_CLK_SRC`=22. Representative clocks: `GPU_CC_PLL0`, `GPU_CC_PLL1`, `GPU_CC_AHB_CLK`, `GPU_CC_CB_CLK`, `GPU_CC_CRC_AHB_CLK`, `GPU_CC_CX_FF_CLK`, ... `GPU_CC_HUB_CLK_SRC`, `GPU_CC_HUB_CX_INT_CLK`, `GPU_CC_HUB_CX_INT_DIV_CLK_SRC`, `GPU_CC_MEMNOC_GFX_CLK`, `GPU_CC_SLEEP_CLK`, `GPU_CC_XO_CLK_SRC`.

Reset ID range: `GPUCC_GPU_CC_ACD_BCR`=0 through `GPUCC_GPU_CC_XO_BCR`=8. Representative resets: `GPUCC_GPU_CC_ACD_BCR`, `GPUCC_GPU_CC_CB_BCR`, `GPUCC_GPU_CC_CX_BCR`, `GPUCC_GPU_CC_FAST_HUB_BCR`, `GPUCC_GPU_CC_FF_BCR`, `GPUCC_GPU_CC_GFX3D_AON_BCR`, `GPUCC_GPU_CC_GMU_BCR`, `GPUCC_GPU_CC_GX_BCR`, `GPUCC_GPU_CC_XO_BCR`.

Power-domain/GDSC range: `GPU_CC_CX_GDSC`=0 through `GPU_CC_GX_GDSC`=1. Representative domains: `GPU_CC_CX_GDSC`, `GPU_CC_GX_GDSC`.

Macro inventory begins with:
- `GPU_CC_PLL0` = 0 (clock, line 11)
- `GPU_CC_PLL1` = 1 (clock, line 12)
- `GPU_CC_AHB_CLK` = 2 (clock, line 13)
- `GPU_CC_CB_CLK` = 3 (clock, line 14)
- `GPU_CC_CRC_AHB_CLK` = 4 (clock, line 15)
- `GPU_CC_CX_FF_CLK` = 5 (clock, line 16)
- `GPU_CC_CX_GMU_CLK` = 6 (clock, line 17)
- `GPU_CC_CX_SNOC_DVM_CLK` = 7 (clock, line 18)
- `GPU_CC_CXO_AON_CLK` = 8 (clock, line 19)
- `GPU_CC_CXO_CLK` = 9 (clock, line 20)
- ... 24 additional numeric binding macros continue in the same contiguous namespace sections.

## Control Flow

This header has no branches, calls, or runtime control flow. The effective flow is build-time and probe-time: DTS sources include the constants, the device-tree compiler stores the resulting integers in clock/reset/power-domain specifier cells, and the Qualcomm clock-controller driver exposes provider arrays whose indexes must match these values. Consumer drivers later resolve those phandles through common clock, reset-controller, or genpd APIs.

## State and Persistence Behavior

The file owns no memory, locks, hardware registers, or persistent storage. Its state is the ABI value assigned to each macro. Those values persist in compiled DTBs and out-of-tree device trees, so renumbering or deleting an existing define is a compatibility break even though no runtime state is stored here. Actual enable counts, reset assertion state, and GDSC power state are maintained by the clock/reset/power-domain drivers and hardware registers, not by this header.

## Dependencies and Integration Points

Direct source dependencies are intentionally minimal: the header has only SPDX/copyright comments, an include guard, macro definitions, and `#endif`. It is integrated by textual inclusion rather than linking. Local integration evidence: device-tree references: `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/lemans.dtsi`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/monaco.dtsi`.

The semantic dependency is the matching provider implementation and its descriptor arrays. `qcom,sa8775p-gpucc.h` IDs must stay aligned with driver tables for GPU PLL/RCG, GMU, CX/GX, hub, memory NoC, XO/sleep, SMMU vote, reset, and GDSC IDs. DTS consumers depend on these exact constants for properties such as `clocks`, `resets`, `power-domains`, and named clock inputs.

## Risks and Edge Cases

The main risk is ABI drift: inserting new IDs in the middle, reusing a removed value, or moving a reset/GDSC ID to a different number can silently bind a DTS consumer to the wrong hardware clock or power domain. It also exports reset IDs (`GPUCC_GPU_CC_ACD_BCR`=0 through `GPUCC_GPU_CC_XO_BCR`=8). Power-domain/GDSC IDs are exported as `GPU_CC_CX_GDSC`=0 through `GPU_CC_GX_GDSC`=1. Shared names such as PLLs, XO/sleep sources, bus clocks, and GDSCs are easy to copy between SoCs, but the numeric ordering must follow this specific provider, not a visually similar controller. Because the file is pure macros, the compiler provides little semantic checking beyond duplicate definitions and include-guard correctness.

## Test Signals

Useful validation includes building the relevant `drivers/clk/qcom` object with this header, compiling DTBs that include `qcom,sa8775p-gpucc.h`, and running `dtbs_check`/binding-schema checks for the affected SoC. Runtime smoke tests are provider probe success without missing clock/reset IDs, absence of `-ENOENT`/`-EINVAL` from clock lookups, expected entries under common-clock debugfs, and successful bring-up of consumers in the exported domain set: GPU PLL/RCG, GMU, CX/GX, hub, memory NoC, XO/sleep, SMMU vote, reset, and GDSC IDs. For edits, diff the numeric table against the matching driver arrays and boot at least one DTS consumer when local hardware or emulation coverage exists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sa8775p-gpucc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sa8775p-videocc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sa8775p-videocc.h

## Purpose

`sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sa8775p-videocc.h` defines the public device-tree numeric IDs for the Qualcomm video clock-controller binding associated with `qcom,sa8775p-videocc.h` / `sa8775p`. The source was read completely for this report (47 lines). It is not executable kernel code; it is a stable binding contract included by DTS files and by the matching `drivers/clk/qcom` provider so that phandle clock, reset, and power-domain specifiers use the same indexes. This header is shared by multiple DTS or driver consumers in this tree, so numeric stability matters beyond one board file.

## Important APIs, Types, and Functions

There are no C functions, structs, or runtime APIs. The exported API is a set of preprocessor constants guarded by `_DT_BINDINGS_CLK_QCOM_SA8775P_VIDEO_CC_H`. This header defines 21 clock IDs, 7 reset IDs, and 4 power-domain/GDSC IDs, for 32 numeric binding macros total.

Clock ID range: `VIDEO_CC_AHB_CLK`=0 through `VIDEO_PLL1`=20. Representative clocks: `VIDEO_CC_AHB_CLK`, `VIDEO_CC_AHB_CLK_SRC`, `VIDEO_CC_MVS0_CLK`, `VIDEO_CC_MVS0_CLK_SRC`, `VIDEO_CC_MVS0_DIV_CLK_SRC`, `VIDEO_CC_MVS0C_CLK`, ... `VIDEO_CC_SM_DIV_CLK_SRC`, `VIDEO_CC_SM_OBS_CLK`, `VIDEO_CC_XO_CLK`, `VIDEO_CC_XO_CLK_SRC`, `VIDEO_PLL0`, `VIDEO_PLL1`.

Reset ID range: `VIDEO_CC_INTERFACE_BCR`=0 through `VIDEO_CC_MVS1C_BCR`=6. Representative resets: `VIDEO_CC_INTERFACE_BCR`, `VIDEO_CC_MVS0_BCR`, `VIDEO_CC_MVS0C_CLK_ARES`, `VIDEO_CC_MVS0C_BCR`, `VIDEO_CC_MVS1_BCR`, `VIDEO_CC_MVS1C_CLK_ARES`, `VIDEO_CC_MVS1C_BCR`.

Power-domain/GDSC range: `VIDEO_CC_MVS0C_GDSC`=0 through `VIDEO_CC_MVS1_GDSC`=3. Representative domains: `VIDEO_CC_MVS0C_GDSC`, `VIDEO_CC_MVS0_GDSC`, `VIDEO_CC_MVS1C_GDSC`, `VIDEO_CC_MVS1_GDSC`.

Macro inventory begins with:
- `VIDEO_CC_AHB_CLK` = 0 (clock, line 10)
- `VIDEO_CC_AHB_CLK_SRC` = 1 (clock, line 11)
- `VIDEO_CC_MVS0_CLK` = 2 (clock, line 12)
- `VIDEO_CC_MVS0_CLK_SRC` = 3 (clock, line 13)
- `VIDEO_CC_MVS0_DIV_CLK_SRC` = 4 (clock, line 14)
- `VIDEO_CC_MVS0C_CLK` = 5 (clock, line 15)
- `VIDEO_CC_MVS0C_DIV2_DIV_CLK_SRC` = 6 (clock, line 16)
- `VIDEO_CC_MVS1_CLK` = 7 (clock, line 17)
- `VIDEO_CC_MVS1_CLK_SRC` = 8 (clock, line 18)
- `VIDEO_CC_MVS1_DIV_CLK_SRC` = 9 (clock, line 19)
- ... 22 additional numeric binding macros continue in the same contiguous namespace sections.

## Control Flow

This header has no branches, calls, or runtime control flow. The effective flow is build-time and probe-time: DTS sources include the constants, the device-tree compiler stores the resulting integers in clock/reset/power-domain specifier cells, and the Qualcomm clock-controller driver exposes provider arrays whose indexes must match these values. Consumer drivers later resolve those phandles through common clock, reset-controller, or genpd APIs.

## State and Persistence Behavior

The file owns no memory, locks, hardware registers, or persistent storage. Its state is the ABI value assigned to each macro. Those values persist in compiled DTBs and out-of-tree device trees, so renumbering or deleting an existing define is a compatibility break even though no runtime state is stored here. Actual enable counts, reset assertion state, and GDSC power state are maintained by the clock/reset/power-domain drivers and hardware registers, not by this header.

## Dependencies and Integration Points

Direct source dependencies are intentionally minimal: the header has only SPDX/copyright comments, an include guard, macro definitions, and `#endif`. It is integrated by textual inclusion rather than linking. Local integration evidence: clock-controller driver references: `sources/distributed-fs/ceph-client/drivers/clk/qcom/videocc-sa8775p.c`; device-tree references: `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/monaco.dtsi`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/lemans.dtsi`.

The semantic dependency is the matching provider implementation and its descriptor arrays. `qcom,sa8775p-videocc.h` IDs must stay aligned with driver tables for video codec MVS/MVS0/MVS1, AHB, AXI, sleep/XO, reset, and GDSC IDs. DTS consumers depend on these exact constants for properties such as `clocks`, `resets`, `power-domains`, and named clock inputs.

## Risks and Edge Cases

The main risk is ABI drift: inserting new IDs in the middle, reusing a removed value, or moving a reset/GDSC ID to a different number can silently bind a DTS consumer to the wrong hardware clock or power domain. It also exports reset IDs (`VIDEO_CC_INTERFACE_BCR`=0 through `VIDEO_CC_MVS1C_BCR`=6). Power-domain/GDSC IDs are exported as `VIDEO_CC_MVS0C_GDSC`=0 through `VIDEO_CC_MVS1_GDSC`=3. Shared names such as PLLs, XO/sleep sources, bus clocks, and GDSCs are easy to copy between SoCs, but the numeric ordering must follow this specific provider, not a visually similar controller. Because the file is pure macros, the compiler provides little semantic checking beyond duplicate definitions and include-guard correctness.

## Test Signals

Useful validation includes building the relevant `drivers/clk/qcom` object with this header, compiling DTBs that include `qcom,sa8775p-videocc.h`, and running `dtbs_check`/binding-schema checks for the affected SoC. Runtime smoke tests are provider probe success without missing clock/reset IDs, absence of `-ENOENT`/`-EINVAL` from clock lookups, expected entries under common-clock debugfs, and successful bring-up of consumers in the exported domain set: video codec MVS/MVS0/MVS1, AHB, AXI, sleep/XO, reset, and GDSC IDs. For edits, diff the numeric table against the matching driver arrays and boot at least one DTS consumer when local hardware or emulation coverage exists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sa8775p-videocc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sar2130p-gcc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sar2130p-gcc.h

## Purpose

`sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sar2130p-gcc.h` defines the public device-tree numeric IDs for the Qualcomm global clock-controller binding associated with `qcom,sar2130p-gcc.h` / `sar2130p`. The source was read completely for this report (185 lines). It is not executable kernel code; it is a stable binding contract included by DTS files and by the matching `drivers/clk/qcom` provider so that phandle clock, reset, and power-domain specifiers use the same indexes.

## Important APIs, Types, and Functions

There are no C functions, structs, or runtime APIs. The exported API is a set of preprocessor constants guarded by `_DT_BINDINGS_CLK_QCOM_GCC_SAR2130P_H`. This header defines 125 clock IDs, 35 reset IDs, and 10 power-domain/GDSC IDs, for 170 numeric binding macros total.

Clock ID range: `GCC_GPLL0`=0 through `GCC_IRIS_SS_SPD_AXI1_SREG`=124. Representative clocks: `GCC_GPLL0`, `GCC_GPLL0_OUT_EVEN`, `GCC_GPLL1`, `GCC_GPLL9`, `GCC_GPLL9_OUT_EVEN`, `GCC_AGGRE_NOC_PCIE_1_AXI_CLK`, ... `GCC_DDRSS_SPAD_CLK`, `GCC_DDRSS_SPAD_CLK_SRC`, `GCC_VIDEO_AXI0_SREG`, `GCC_VIDEO_AXI1_SREG`, `GCC_IRIS_SS_HF_AXI1_SREG`, `GCC_IRIS_SS_SPD_AXI1_SREG`.

Reset ID range: `GCC_CAMERA_BCR`=0 through `GCC_DDRSS_SPAD_CLK_ARES`=34. Representative resets: `GCC_CAMERA_BCR`, `GCC_DISPLAY_BCR`, `GCC_GPU_BCR`, `GCC_PCIE_0_BCR`, `GCC_PCIE_0_LINK_DOWN_BCR`, `GCC_PCIE_0_NOCSR_COM_PHY_BCR`, ... `GCC_VIDEO_AXI0_CLK_ARES`, `GCC_VIDEO_AXI1_CLK_ARES`, `GCC_VIDEO_BCR`, `GCC_IRIS_SS_HF_AXI_CLK_ARES`, `GCC_IRIS_SS_SPD_AXI_CLK_ARES`, `GCC_DDRSS_SPAD_CLK_ARES`.

Power-domain/GDSC range: `PCIE_0_GDSC`=0 through `HLOS1_VOTE_TURING_MMU_TBU1_GDSC`=9. Representative domains: `PCIE_0_GDSC`, `PCIE_0_PHY_GDSC`, `PCIE_1_GDSC`, `PCIE_1_PHY_GDSC`, `USB30_PRIM_GDSC`, `USB3_PHY_GDSC`, `HLOS1_VOTE_MM_SNOC_MMU_TBU_HF0_GDSC`, `HLOS1_VOTE_MM_SNOC_MMU_TBU_SF0_GDSC`, `HLOS1_VOTE_TURING_MMU_TBU0_GDSC`, `HLOS1_VOTE_TURING_MMU_TBU1_GDSC`.

Macro inventory begins with:
- `GCC_GPLL0` = 0 (clock, line 10)
- `GCC_GPLL0_OUT_EVEN` = 1 (clock, line 11)
- `GCC_GPLL1` = 2 (clock, line 12)
- `GCC_GPLL9` = 3 (clock, line 13)
- `GCC_GPLL9_OUT_EVEN` = 4 (clock, line 14)
- `GCC_AGGRE_NOC_PCIE_1_AXI_CLK` = 5 (clock, line 15)
- `GCC_AGGRE_USB3_PRIM_AXI_CLK` = 6 (clock, line 16)
- `GCC_BOOT_ROM_AHB_CLK` = 7 (clock, line 17)
- `GCC_CAMERA_AHB_CLK` = 8 (clock, line 18)
- `GCC_CAMERA_HF_AXI_CLK` = 9 (clock, line 19)
- ... 160 additional numeric binding macros continue in the same contiguous namespace sections.

## Control Flow

This header has no branches, calls, or runtime control flow. The effective flow is build-time and probe-time: DTS sources include the constants, the device-tree compiler stores the resulting integers in clock/reset/power-domain specifier cells, and the Qualcomm clock-controller driver exposes provider arrays whose indexes must match these values. Consumer drivers later resolve those phandles through common clock, reset-controller, or genpd APIs.

## State and Persistence Behavior

The file owns no memory, locks, hardware registers, or persistent storage. Its state is the ABI value assigned to each macro. Those values persist in compiled DTBs and out-of-tree device trees, so renumbering or deleting an existing define is a compatibility break even though no runtime state is stored here. Actual enable counts, reset assertion state, and GDSC power state are maintained by the clock/reset/power-domain drivers and hardware registers, not by this header.

## Dependencies and Integration Points

Direct source dependencies are intentionally minimal: the header has only SPDX/copyright comments, an include guard, macro definitions, and `#endif`. It is integrated by textual inclusion rather than linking. Local integration evidence: clock-controller driver references: `sources/distributed-fs/ceph-client/drivers/clk/qcom/gcc-sar2130p.c`; device-tree references: `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/sar2130p.dtsi`.

The semantic dependency is the matching provider implementation and its descriptor arrays. `qcom,sar2130p-gcc.h` IDs must stay aligned with driver tables for global PLLs plus bus, QUP, USB, PCIe, UFS, SDCC, camera/display/video/gpu vote, reset, and GDSC IDs. DTS consumers depend on these exact constants for properties such as `clocks`, `resets`, `power-domains`, and named clock inputs.

## Risks and Edge Cases

The main risk is ABI drift: inserting new IDs in the middle, reusing a removed value, or moving a reset/GDSC ID to a different number can silently bind a DTS consumer to the wrong hardware clock or power domain. It also exports reset IDs (`GCC_CAMERA_BCR`=0 through `GCC_DDRSS_SPAD_CLK_ARES`=34). Power-domain/GDSC IDs are exported as `PCIE_0_GDSC`=0 through `HLOS1_VOTE_TURING_MMU_TBU1_GDSC`=9. Shared names such as PLLs, XO/sleep sources, bus clocks, and GDSCs are easy to copy between SoCs, but the numeric ordering must follow this specific provider, not a visually similar controller. Because the file is pure macros, the compiler provides little semantic checking beyond duplicate definitions and include-guard correctness.

## Test Signals

Useful validation includes building the relevant `drivers/clk/qcom` object with this header, compiling DTBs that include `qcom,sar2130p-gcc.h`, and running `dtbs_check`/binding-schema checks for the affected SoC. Runtime smoke tests are provider probe success without missing clock/reset IDs, absence of `-ENOENT`/`-EINVAL` from clock lookups, expected entries under common-clock debugfs, and successful bring-up of consumers in the exported domain set: global PLLs plus bus, QUP, USB, PCIe, UFS, SDCC, camera/display/video/gpu vote, reset, and GDSC IDs. For edits, diff the numeric table against the matching driver arrays and boot at least one DTS consumer when local hardware or emulation coverage exists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sar2130p-gcc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sar2130p-gpucc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sar2130p-gpucc.h

## Purpose

`sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sar2130p-gpucc.h` defines the public device-tree numeric IDs for the Qualcomm GPU clock-controller binding associated with `qcom,sar2130p-gpucc.h` / `sar2130p`. The source was read completely for this report (33 lines). It is not executable kernel code; it is a stable binding contract included by DTS files and by the matching `drivers/clk/qcom` provider so that phandle clock, reset, and power-domain specifiers use the same indexes.

## Important APIs, Types, and Functions

There are no C functions, structs, or runtime APIs. The exported API is a set of preprocessor constants guarded by `_DT_BINDINGS_CLK_QCOM_GPU_CC_SAR2130P_H`. This header defines 17 clock IDs, 0 reset IDs, and 2 power-domain/GDSC IDs, for 19 numeric binding macros total.

Clock ID range: `GPU_CC_AHB_CLK`=0 through `GPU_CC_SLEEP_CLK`=16. Representative clocks: `GPU_CC_AHB_CLK`, `GPU_CC_CRC_AHB_CLK`, `GPU_CC_CX_FF_CLK`, `GPU_CC_CX_GMU_CLK`, `GPU_CC_CXO_AON_CLK`, `GPU_CC_CXO_CLK`, ... `GPU_CC_HUB_CLK_SRC`, `GPU_CC_HUB_CX_INT_CLK`, `GPU_CC_MEMNOC_GFX_CLK`, `GPU_CC_PLL0`, `GPU_CC_PLL1`, `GPU_CC_SLEEP_CLK`.

Reset ID range: none. Representative resets: none.

Power-domain/GDSC range: `GPU_GX_GDSC`=0 through `GPU_CX_GDSC`=1. Representative domains: `GPU_GX_GDSC`, `GPU_CX_GDSC`.

Macro inventory begins with:
- `GPU_CC_AHB_CLK` = 0 (clock, line 11)
- `GPU_CC_CRC_AHB_CLK` = 1 (clock, line 12)
- `GPU_CC_CX_FF_CLK` = 2 (clock, line 13)
- `GPU_CC_CX_GMU_CLK` = 3 (clock, line 14)
- `GPU_CC_CXO_AON_CLK` = 4 (clock, line 15)
- `GPU_CC_CXO_CLK` = 5 (clock, line 16)
- `GPU_CC_FF_CLK_SRC` = 6 (clock, line 17)
- `GPU_CC_GMU_CLK_SRC` = 7 (clock, line 18)
- `GPU_CC_GX_GMU_CLK` = 8 (clock, line 19)
- `GPU_CC_HLOS1_VOTE_GPU_SMMU_CLK` = 9 (clock, line 20)
- ... 9 additional numeric binding macros continue in the same contiguous namespace sections.

## Control Flow

This header has no branches, calls, or runtime control flow. The effective flow is build-time and probe-time: DTS sources include the constants, the device-tree compiler stores the resulting integers in clock/reset/power-domain specifier cells, and the Qualcomm clock-controller driver exposes provider arrays whose indexes must match these values. Consumer drivers later resolve those phandles through common clock, reset-controller, or genpd APIs.

## State and Persistence Behavior

The file owns no memory, locks, hardware registers, or persistent storage. Its state is the ABI value assigned to each macro. Those values persist in compiled DTBs and out-of-tree device trees, so renumbering or deleting an existing define is a compatibility break even though no runtime state is stored here. Actual enable counts, reset assertion state, and GDSC power state are maintained by the clock/reset/power-domain drivers and hardware registers, not by this header.

## Dependencies and Integration Points

Direct source dependencies are intentionally minimal: the header has only SPDX/copyright comments, an include guard, macro definitions, and `#endif`. It is integrated by textual inclusion rather than linking. Local integration evidence: clock-controller driver references: `sources/distributed-fs/ceph-client/drivers/clk/qcom/gpucc-sar2130p.c`; device-tree references: `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/sar2130p.dtsi`.

The semantic dependency is the matching provider implementation and its descriptor arrays. `qcom,sar2130p-gpucc.h` IDs must stay aligned with driver tables for GPU PLL/RCG, GMU, CX/GX, hub, memory NoC, XO/sleep, SMMU vote, reset, and GDSC IDs. DTS consumers depend on these exact constants for properties such as `clocks`, `resets`, `power-domains`, and named clock inputs.

## Risks and Edge Cases

The main risk is ABI drift: inserting new IDs in the middle, reusing a removed value, or moving a reset/GDSC ID to a different number can silently bind a DTS consumer to the wrong hardware clock or power domain. It does not export reset IDs in this clock header; reset bindings are either absent for this controller or live in a paired reset binding header/driver table. Power-domain/GDSC IDs are exported as `GPU_GX_GDSC`=0 through `GPU_CX_GDSC`=1. Shared names such as PLLs, XO/sleep sources, bus clocks, and GDSCs are easy to copy between SoCs, but the numeric ordering must follow this specific provider, not a visually similar controller. Because the file is pure macros, the compiler provides little semantic checking beyond duplicate definitions and include-guard correctness.

## Test Signals

Useful validation includes building the relevant `drivers/clk/qcom` object with this header, compiling DTBs that include `qcom,sar2130p-gpucc.h`, and running `dtbs_check`/binding-schema checks for the affected SoC. Runtime smoke tests are provider probe success without missing clock/reset IDs, absence of `-ENOENT`/`-EINVAL` from clock lookups, expected entries under common-clock debugfs, and successful bring-up of consumers in the exported domain set: GPU PLL/RCG, GMU, CX/GX, hub, memory NoC, XO/sleep, SMMU vote, reset, and GDSC IDs. For edits, diff the numeric table against the matching driver arrays and boot at least one DTS consumer when local hardware or emulation coverage exists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sar2130p-gpucc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sc8180x-camcc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sc8180x-camcc.h

## Purpose

`sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sc8180x-camcc.h` defines the public device-tree numeric IDs for the Qualcomm camera clock-controller binding associated with `qcom,sc8180x-camcc.h` / `sc8180x`. The source was read completely for this report (181 lines). It is not executable kernel code; it is a stable binding contract included by DTS files and by the matching `drivers/clk/qcom` provider so that phandle clock, reset, and power-domain specifiers use the same indexes.

## Important APIs, Types, and Functions

There are no C functions, structs, or runtime APIs. The exported API is a set of preprocessor constants guarded by `_DT_BINDINGS_CLK_QCOM_CAM_CC_SC8180X_H`. This header defines 127 clock IDs, 30 reset IDs, and 8 power-domain/GDSC IDs, for 165 numeric binding macros total.

Clock ID range: `CAM_CC_BPS_AHB_CLK`=0 through `CAM_CC_XO_CLK_SRC`=126. Representative clocks: `CAM_CC_BPS_AHB_CLK`, `CAM_CC_BPS_AREG_CLK`, `CAM_CC_BPS_AXI_CLK`, `CAM_CC_BPS_CLK`, `CAM_CC_BPS_CLK_SRC`, `CAM_CC_CAMNOC_AXI_CLK`, ... `CAM_CC_PLL3`, `CAM_CC_PLL4`, `CAM_CC_PLL5`, `CAM_CC_PLL6`, `CAM_CC_SLOW_AHB_CLK_SRC`, `CAM_CC_XO_CLK_SRC`.

Reset ID range: `CAM_CC_BPS_BCR`=0 through `CAM_CC_MCLK7_BCR`=29. Representative resets: `CAM_CC_BPS_BCR`, `CAM_CC_CAMNOC_BCR`, `CAM_CC_CCI_BCR`, `CAM_CC_CPAS_BCR`, `CAM_CC_CSI0PHY_BCR`, `CAM_CC_CSI1PHY_BCR`, ... `CAM_CC_MCLK2_BCR`, `CAM_CC_MCLK3_BCR`, `CAM_CC_MCLK4_BCR`, `CAM_CC_MCLK5_BCR`, `CAM_CC_MCLK6_BCR`, `CAM_CC_MCLK7_BCR`.

Power-domain/GDSC range: `BPS_GDSC`=0 through `TITAN_TOP_GDSC`=7. Representative domains: `BPS_GDSC`, `IFE_0_GDSC`, `IFE_1_GDSC`, `IFE_2_GDSC`, `IFE_3_GDSC`, `IPE_0_GDSC`, `IPE_1_GDSC`, `TITAN_TOP_GDSC`.

Macro inventory begins with:
- `CAM_CC_BPS_AHB_CLK` = 0 (clock, line 10)
- `CAM_CC_BPS_AREG_CLK` = 1 (clock, line 11)
- `CAM_CC_BPS_AXI_CLK` = 2 (clock, line 12)
- `CAM_CC_BPS_CLK` = 3 (clock, line 13)
- `CAM_CC_BPS_CLK_SRC` = 4 (clock, line 14)
- `CAM_CC_CAMNOC_AXI_CLK` = 5 (clock, line 15)
- `CAM_CC_CAMNOC_AXI_CLK_SRC` = 6 (clock, line 16)
- `CAM_CC_CAMNOC_DCD_XO_CLK` = 7 (clock, line 17)
- `CAM_CC_CCI_0_CLK` = 8 (clock, line 18)
- `CAM_CC_CCI_0_CLK_SRC` = 9 (clock, line 19)
- ... 155 additional numeric binding macros continue in the same contiguous namespace sections.

## Control Flow

This header has no branches, calls, or runtime control flow. The effective flow is build-time and probe-time: DTS sources include the constants, the device-tree compiler stores the resulting integers in clock/reset/power-domain specifier cells, and the Qualcomm clock-controller driver exposes provider arrays whose indexes must match these values. Consumer drivers later resolve those phandles through common clock, reset-controller, or genpd APIs.

## State and Persistence Behavior

The file owns no memory, locks, hardware registers, or persistent storage. Its state is the ABI value assigned to each macro. Those values persist in compiled DTBs and out-of-tree device trees, so renumbering or deleting an existing define is a compatibility break even though no runtime state is stored here. Actual enable counts, reset assertion state, and GDSC power state are maintained by the clock/reset/power-domain drivers and hardware registers, not by this header.

## Dependencies and Integration Points

Direct source dependencies are intentionally minimal: the header has only SPDX/copyright comments, an include guard, macro definitions, and `#endif`. It is integrated by textual inclusion rather than linking. Local integration evidence: clock-controller driver references: `sources/distributed-fs/ceph-client/drivers/clk/qcom/camcc-sc8180x.c`; device-tree references: `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/sc8180x.dtsi`.

The semantic dependency is the matching provider implementation and its descriptor arrays. `qcom,sc8180x-camcc.h` IDs must stay aligned with driver tables for camera PLLs, MCLKs, CSI/CSIPHY timers, IFE/TFE/SFE/BPS/IPE/JPEG/CPAS fabric clocks, resets, and camera GDSCs. DTS consumers depend on these exact constants for properties such as `clocks`, `resets`, `power-domains`, and named clock inputs.

## Risks and Edge Cases

The main risk is ABI drift: inserting new IDs in the middle, reusing a removed value, or moving a reset/GDSC ID to a different number can silently bind a DTS consumer to the wrong hardware clock or power domain. It also exports reset IDs (`CAM_CC_BPS_BCR`=0 through `CAM_CC_MCLK7_BCR`=29). Power-domain/GDSC IDs are exported as `BPS_GDSC`=0 through `TITAN_TOP_GDSC`=7. Shared names such as PLLs, XO/sleep sources, bus clocks, and GDSCs are easy to copy between SoCs, but the numeric ordering must follow this specific provider, not a visually similar controller. Because the file is pure macros, the compiler provides little semantic checking beyond duplicate definitions and include-guard correctness.

## Test Signals

Useful validation includes building the relevant `drivers/clk/qcom` object with this header, compiling DTBs that include `qcom,sc8180x-camcc.h`, and running `dtbs_check`/binding-schema checks for the affected SoC. Runtime smoke tests are provider probe success without missing clock/reset IDs, absence of `-ENOENT`/`-EINVAL` from clock lookups, expected entries under common-clock debugfs, and successful bring-up of consumers in the exported domain set: camera PLLs, MCLKs, CSI/CSIPHY timers, IFE/TFE/SFE/BPS/IPE/JPEG/CPAS fabric clocks, resets, and camera GDSCs. For edits, diff the numeric table against the matching driver arrays and boot at least one DTS consumer when local hardware or emulation coverage exists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sc8180x-camcc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sc8280xp-camcc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sc8280xp-camcc.h

## Purpose

`sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sc8280xp-camcc.h` defines the public device-tree numeric IDs for the Qualcomm camera clock-controller binding associated with `qcom,sc8280xp-camcc.h` / `sc8280xp`. The source was read completely for this report (179 lines). It is not executable kernel code; it is a stable binding contract included by DTS files and by the matching `drivers/clk/qcom` provider so that phandle clock, reset, and power-domain specifiers use the same indexes.

## Important APIs, Types, and Functions

There are no C functions, structs, or runtime APIs. The exported API is a set of preprocessor constants guarded by `__DT_BINDINGS_CLK_QCOM_CAMCC_SC8280XP_H__`. This header defines 134 clock IDs, 21 reset IDs, and 8 power-domain/GDSC IDs, for 163 numeric binding macros total.

Clock ID range: `CAMCC_PLL0`=0 through `CAMCC_XO_CLK_SRC`=133. Representative clocks: `CAMCC_PLL0`, `CAMCC_PLL0_OUT_EVEN`, `CAMCC_PLL0_OUT_ODD`, `CAMCC_PLL1`, `CAMCC_PLL1_OUT_EVEN`, `CAMCC_PLL2`, ... `CAMCC_MCLK7_CLK`, `CAMCC_MCLK7_CLK_SRC`, `CAMCC_SLEEP_CLK`, `CAMCC_SLEEP_CLK_SRC`, `CAMCC_SLOW_AHB_CLK_SRC`, `CAMCC_XO_CLK_SRC`.

Reset ID range: `CAMCC_BPS_BCR`=0 through `CAMCC_LRME_BCR`=20. Representative resets: `CAMCC_BPS_BCR`, `CAMCC_CAMNOC_BCR`, `CAMCC_CCI_BCR`, `CAMCC_CPAS_BCR`, `CAMCC_CSI0PHY_BCR`, `CAMCC_CSI1PHY_BCR`, ... `CAMCC_IFE_LITE_2_BCR`, `CAMCC_IFE_LITE_3_BCR`, `CAMCC_IPE_0_BCR`, `CAMCC_IPE_1_BCR`, `CAMCC_JPEG_BCR`, `CAMCC_LRME_BCR`.

Power-domain/GDSC range: `BPS_GDSC`=0 through `TITAN_TOP_GDSC`=7. Representative domains: `BPS_GDSC`, `IFE_0_GDSC`, `IFE_1_GDSC`, `IFE_2_GDSC`, `IFE_3_GDSC`, `IPE_0_GDSC`, `IPE_1_GDSC`, `TITAN_TOP_GDSC`.

Macro inventory begins with:
- `CAMCC_PLL0` = 0 (clock, line 11)
- `CAMCC_PLL0_OUT_EVEN` = 1 (clock, line 12)
- `CAMCC_PLL0_OUT_ODD` = 2 (clock, line 13)
- `CAMCC_PLL1` = 3 (clock, line 14)
- `CAMCC_PLL1_OUT_EVEN` = 4 (clock, line 15)
- `CAMCC_PLL2` = 5 (clock, line 16)
- `CAMCC_PLL3` = 6 (clock, line 17)
- `CAMCC_PLL3_OUT_EVEN` = 7 (clock, line 18)
- `CAMCC_PLL4` = 8 (clock, line 19)
- `CAMCC_PLL4_OUT_EVEN` = 9 (clock, line 20)
- ... 153 additional numeric binding macros continue in the same contiguous namespace sections.

## Control Flow

This header has no branches, calls, or runtime control flow. The effective flow is build-time and probe-time: DTS sources include the constants, the device-tree compiler stores the resulting integers in clock/reset/power-domain specifier cells, and the Qualcomm clock-controller driver exposes provider arrays whose indexes must match these values. Consumer drivers later resolve those phandles through common clock, reset-controller, or genpd APIs.

## State and Persistence Behavior

The file owns no memory, locks, hardware registers, or persistent storage. Its state is the ABI value assigned to each macro. Those values persist in compiled DTBs and out-of-tree device trees, so renumbering or deleting an existing define is a compatibility break even though no runtime state is stored here. Actual enable counts, reset assertion state, and GDSC power state are maintained by the clock/reset/power-domain drivers and hardware registers, not by this header.

## Dependencies and Integration Points

Direct source dependencies are intentionally minimal: the header has only SPDX/copyright comments, an include guard, macro definitions, and `#endif`. It is integrated by textual inclusion rather than linking. Local integration evidence: clock-controller driver references: `sources/distributed-fs/ceph-client/drivers/clk/qcom/camcc-sc8280xp.c`; device-tree references: `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/sc8280xp.dtsi`.

The semantic dependency is the matching provider implementation and its descriptor arrays. `qcom,sc8280xp-camcc.h` IDs must stay aligned with driver tables for camera PLLs, MCLKs, CSI/CSIPHY timers, IFE/TFE/SFE/BPS/IPE/JPEG/CPAS fabric clocks, resets, and camera GDSCs. DTS consumers depend on these exact constants for properties such as `clocks`, `resets`, `power-domains`, and named clock inputs.

## Risks and Edge Cases

The main risk is ABI drift: inserting new IDs in the middle, reusing a removed value, or moving a reset/GDSC ID to a different number can silently bind a DTS consumer to the wrong hardware clock or power domain. It also exports reset IDs (`CAMCC_BPS_BCR`=0 through `CAMCC_LRME_BCR`=20). Power-domain/GDSC IDs are exported as `BPS_GDSC`=0 through `TITAN_TOP_GDSC`=7. Shared names such as PLLs, XO/sleep sources, bus clocks, and GDSCs are easy to copy between SoCs, but the numeric ordering must follow this specific provider, not a visually similar controller. Because the file is pure macros, the compiler provides little semantic checking beyond duplicate definitions and include-guard correctness.

## Test Signals

Useful validation includes building the relevant `drivers/clk/qcom` object with this header, compiling DTBs that include `qcom,sc8280xp-camcc.h`, and running `dtbs_check`/binding-schema checks for the affected SoC. Runtime smoke tests are provider probe success without missing clock/reset IDs, absence of `-ENOENT`/`-EINVAL` from clock lookups, expected entries under common-clock debugfs, and successful bring-up of consumers in the exported domain set: camera PLLs, MCLKs, CSI/CSIPHY timers, IFE/TFE/SFE/BPS/IPE/JPEG/CPAS fabric clocks, resets, and camera GDSCs. For edits, diff the numeric table against the matching driver arrays and boot at least one DTS consumer when local hardware or emulation coverage exists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sc8280xp-camcc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sc8280xp-lpasscc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sc8280xp-lpasscc.h

## Purpose

`sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sc8280xp-lpasscc.h` defines the public device-tree numeric IDs for the Qualcomm LPASS/audio clock-controller binding associated with `qcom,sc8280xp-lpasscc.h` / `sc8280xp`. The source was read completely for this report (17 lines). It is not executable kernel code; it is a stable binding contract included by DTS files and by the matching `drivers/clk/qcom` provider so that phandle clock, reset, and power-domain specifiers use the same indexes. This header is shared by multiple DTS or driver consumers in this tree, so numeric stability matters beyond one board file.

## Important APIs, Types, and Functions

There are no C functions, structs, or runtime APIs. The exported API is a set of preprocessor constants guarded by `_DT_BINDINGS_CLK_QCOM_LPASSCC_SC8280XP_H`. This header defines 4 clock IDs, 0 reset IDs, and 0 power-domain/GDSC IDs, for 4 numeric binding macros total.

Clock ID range: `LPASS_AUDIO_SWR_RX_CGCR`=0 through `LPASS_AUDIO_SWR_WSA2_CGCR`=2. Representative clocks: `LPASS_AUDIO_SWR_RX_CGCR`, `LPASS_AUDIO_SWR_WSA_CGCR`, `LPASS_AUDIO_SWR_WSA2_CGCR`, `LPASS_AUDIO_SWR_TX_CGCR`.

Reset ID range: none. Representative resets: none.

Power-domain/GDSC range: none. Representative domains: none.

Macro inventory begins with:
- `LPASS_AUDIO_SWR_RX_CGCR` = 0 (clock, line 10)
- `LPASS_AUDIO_SWR_WSA_CGCR` = 1 (clock, line 11)
- `LPASS_AUDIO_SWR_WSA2_CGCR` = 2 (clock, line 12)
- `LPASS_AUDIO_SWR_TX_CGCR` = 0 (clock, line 15)

## Control Flow

This header has no branches, calls, or runtime control flow. The effective flow is build-time and probe-time: DTS sources include the constants, the device-tree compiler stores the resulting integers in clock/reset/power-domain specifier cells, and the Qualcomm clock-controller driver exposes provider arrays whose indexes must match these values. Consumer drivers later resolve those phandles through common clock, reset-controller, or genpd APIs.

## State and Persistence Behavior

The file owns no memory, locks, hardware registers, or persistent storage. Its state is the ABI value assigned to each macro. Those values persist in compiled DTBs and out-of-tree device trees, so renumbering or deleting an existing define is a compatibility break even though no runtime state is stored here. Actual enable counts, reset assertion state, and GDSC power state are maintained by the clock/reset/power-domain drivers and hardware registers, not by this header.

## Dependencies and Integration Points

Direct source dependencies are intentionally minimal: the header has only SPDX/copyright comments, an include guard, macro definitions, and `#endif`. It is integrated by textual inclusion rather than linking. Local integration evidence: clock-controller driver references: `sources/distributed-fs/ceph-client/drivers/clk/qcom/lpasscc-sc8280xp.c`; device-tree references: `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/sc8280xp.dtsi`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/hamoa.dtsi`.

The semantic dependency is the matching provider implementation and its descriptor arrays. `qcom,sc8280xp-lpasscc.h` IDs must stay aligned with driver tables for audio and always-on LPASS clock IDs used by the Qualcomm GFM/LPASS clock driver. DTS consumers depend on these exact constants for properties such as `clocks`, `resets`, `power-domains`, and named clock inputs.

## Risks and Edge Cases

The main risk is ABI drift: inserting new IDs in the middle, reusing a removed value, or moving a reset/GDSC ID to a different number can silently bind a DTS consumer to the wrong hardware clock or power domain. It does not export reset IDs in this clock header; reset bindings are either absent for this controller or live in a paired reset binding header/driver table. It does not export GDSC or power-domain IDs. Shared names such as PLLs, XO/sleep sources, bus clocks, and GDSCs are easy to copy between SoCs, but the numeric ordering must follow this specific provider, not a visually similar controller. Because the file is pure macros, the compiler provides little semantic checking beyond duplicate definitions and include-guard correctness.

## Test Signals

Useful validation includes building the relevant `drivers/clk/qcom` object with this header, compiling DTBs that include `qcom,sc8280xp-lpasscc.h`, and running `dtbs_check`/binding-schema checks for the affected SoC. Runtime smoke tests are provider probe success without missing clock/reset IDs, absence of `-ENOENT`/`-EINVAL` from clock lookups, expected entries under common-clock debugfs, and successful bring-up of consumers in the exported domain set: audio and always-on LPASS clock IDs used by the Qualcomm GFM/LPASS clock driver. For edits, diff the numeric table against the matching driver arrays and boot at least one DTS consumer when local hardware or emulation coverage exists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sc8280xp-lpasscc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sdx75-gcc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sdx75-gcc.h

## Purpose

`sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sdx75-gcc.h` defines the public device-tree numeric IDs for the Qualcomm global clock-controller binding associated with `qcom,sdx75-gcc.h` / `sdx75`. The source was read completely for this report (193 lines). It is not executable kernel code; it is a stable binding contract included by DTS files and by the matching `drivers/clk/qcom` provider so that phandle clock, reset, and power-domain specifiers use the same indexes.

## Important APIs, Types, and Functions

There are no C functions, structs, or runtime APIs. The exported API is a set of preprocessor constants guarded by `_DT_BINDINGS_CLK_QCOM_GCC_SDX75_H`. This header defines 143 clock IDs, 25 reset IDs, and 10 power-domain/GDSC IDs, for 178 numeric binding macros total.

Clock ID range: `GPLL0`=0 through `GCC_XO_PCIE_LINK_CLK`=142. Representative clocks: `GPLL0`, `GPLL0_OUT_EVEN`, `GPLL4`, `GPLL5`, `GPLL6`, `GPLL8`, ... `GCC_USB3_PHY_AUX_CLK_SRC`, `GCC_USB3_PHY_PIPE_CLK`, `GCC_USB3_PHY_PIPE_CLK_SRC`, `GCC_USB3_PRIM_CLKREF_EN`, `GCC_USB_PHY_CFG_AHB2PHY_CLK`, `GCC_XO_PCIE_LINK_CLK`.

Reset ID range: `GCC_EMAC0_BCR`=0 through `GCC_EMAC0_RGMII_CLK_ARES`=24. Representative resets: `GCC_EMAC0_BCR`, `GCC_EMAC1_BCR`, `GCC_EMMC_BCR`, `GCC_PCIE_1_BCR`, `GCC_PCIE_1_LINK_DOWN_BCR`, `GCC_PCIE_1_NOCSR_COM_PHY_BCR`, ... `GCC_TCSR_PCIE_BCR`, `GCC_USB30_BCR`, `GCC_USB3_PHY_BCR`, `GCC_USB3PHY_PHY_BCR`, `GCC_USB_PHY_CFG_AHB2PHY_BCR`, `GCC_EMAC0_RGMII_CLK_ARES`.

Power-domain/GDSC range: `GCC_EMAC0_GDSC`=0 through `GCC_USB3_PHY_GDSC`=9. Representative domains: `GCC_EMAC0_GDSC`, `GCC_EMAC1_GDSC`, `GCC_PCIE_1_GDSC`, `GCC_PCIE_1_PHY_GDSC`, `GCC_PCIE_2_GDSC`, `GCC_PCIE_2_PHY_GDSC`, `GCC_PCIE_GDSC`, `GCC_PCIE_PHY_GDSC`, `GCC_USB30_GDSC`, `GCC_USB3_PHY_GDSC`.

Macro inventory begins with:
- `GPLL0` = 0 (clock, line 10)
- `GPLL0_OUT_EVEN` = 1 (clock, line 11)
- `GPLL4` = 2 (clock, line 12)
- `GPLL5` = 3 (clock, line 13)
- `GPLL6` = 4 (clock, line 14)
- `GPLL8` = 5 (clock, line 15)
- `GCC_AHB_PCIE_LINK_CLK` = 6 (clock, line 16)
- `GCC_BOOT_ROM_AHB_CLK` = 7 (clock, line 17)
- `GCC_EEE_EMAC0_CLK` = 8 (clock, line 18)
- `GCC_EEE_EMAC0_CLK_SRC` = 9 (clock, line 19)
- ... 168 additional numeric binding macros continue in the same contiguous namespace sections.

## Control Flow

This header has no branches, calls, or runtime control flow. The effective flow is build-time and probe-time: DTS sources include the constants, the device-tree compiler stores the resulting integers in clock/reset/power-domain specifier cells, and the Qualcomm clock-controller driver exposes provider arrays whose indexes must match these values. Consumer drivers later resolve those phandles through common clock, reset-controller, or genpd APIs.

## State and Persistence Behavior

The file owns no memory, locks, hardware registers, or persistent storage. Its state is the ABI value assigned to each macro. Those values persist in compiled DTBs and out-of-tree device trees, so renumbering or deleting an existing define is a compatibility break even though no runtime state is stored here. Actual enable counts, reset assertion state, and GDSC power state are maintained by the clock/reset/power-domain drivers and hardware registers, not by this header.

## Dependencies and Integration Points

Direct source dependencies are intentionally minimal: the header has only SPDX/copyright comments, an include guard, macro definitions, and `#endif`. It is integrated by textual inclusion rather than linking. Local integration evidence: clock-controller driver references: `sources/distributed-fs/ceph-client/drivers/clk/qcom/gcc-sdx75.c`; device-tree references: `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/sdx75.dtsi`.

The semantic dependency is the matching provider implementation and its descriptor arrays. `qcom,sdx75-gcc.h` IDs must stay aligned with driver tables for global PLLs plus bus, QUP, USB, PCIe, UFS, SDCC, camera/display/video/gpu vote, reset, and GDSC IDs. DTS consumers depend on these exact constants for properties such as `clocks`, `resets`, `power-domains`, and named clock inputs.

## Risks and Edge Cases

The main risk is ABI drift: inserting new IDs in the middle, reusing a removed value, or moving a reset/GDSC ID to a different number can silently bind a DTS consumer to the wrong hardware clock or power domain. It also exports reset IDs (`GCC_EMAC0_BCR`=0 through `GCC_EMAC0_RGMII_CLK_ARES`=24). Power-domain/GDSC IDs are exported as `GCC_EMAC0_GDSC`=0 through `GCC_USB3_PHY_GDSC`=9. Shared names such as PLLs, XO/sleep sources, bus clocks, and GDSCs are easy to copy between SoCs, but the numeric ordering must follow this specific provider, not a visually similar controller. Because the file is pure macros, the compiler provides little semantic checking beyond duplicate definitions and include-guard correctness.

## Test Signals

Useful validation includes building the relevant `drivers/clk/qcom` object with this header, compiling DTBs that include `qcom,sdx75-gcc.h`, and running `dtbs_check`/binding-schema checks for the affected SoC. Runtime smoke tests are provider probe success without missing clock/reset IDs, absence of `-ENOENT`/`-EINVAL` from clock lookups, expected entries under common-clock debugfs, and successful bring-up of consumers in the exported domain set: global PLLs plus bus, QUP, USB, PCIe, UFS, SDCC, camera/display/video/gpu vote, reset, and GDSC IDs. For edits, diff the numeric table against the matching driver arrays and boot at least one DTS consumer when local hardware or emulation coverage exists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sdx75-gcc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sm4450-camcc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sm4450-camcc.h

## Purpose

`sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sm4450-camcc.h` defines the public device-tree numeric IDs for the Qualcomm camera clock-controller binding associated with `qcom,sm4450-camcc.h` / `sm4450`. The source was read completely for this report (106 lines). It is not executable kernel code; it is a stable binding contract included by DTS files and by the matching `drivers/clk/qcom` provider so that phandle clock, reset, and power-domain specifiers use the same indexes.

## Important APIs, Types, and Functions

There are no C functions, structs, or runtime APIs. The exported API is a set of preprocessor constants guarded by `_DT_BINDINGS_CLK_QCOM_CAM_CC_SM4450_H`. This header defines 72 clock IDs, 18 reset IDs, and 1 power-domain/GDSC ID, for 91 numeric binding macros total.

Clock ID range: `CAM_CC_BPS_AHB_CLK`=0 through `CAM_CC_TFE_1_CSID_CLK_SRC`=71. Representative clocks: `CAM_CC_BPS_AHB_CLK`, `CAM_CC_BPS_AREG_CLK`, `CAM_CC_BPS_CLK`, `CAM_CC_BPS_CLK_SRC`, `CAM_CC_CAMNOC_ATB_CLK`, `CAM_CC_CAMNOC_AXI_CLK`, ... `CAM_CC_TFE_1_AHB_CLK`, `CAM_CC_TFE_1_CLK`, `CAM_CC_TFE_1_CLK_SRC`, `CAM_CC_TFE_1_CPHY_RX_CLK`, `CAM_CC_TFE_1_CSID_CLK`, `CAM_CC_TFE_1_CSID_CLK_SRC`.

Reset ID range: `CAM_CC_BPS_BCR`=0 through `CAM_CC_TFE_1_BCR`=17. Representative resets: `CAM_CC_BPS_BCR`, `CAM_CC_CAMNOC_BCR`, `CAM_CC_CAMSS_TOP_BCR`, `CAM_CC_CCI_0_BCR`, `CAM_CC_CCI_1_BCR`, `CAM_CC_CPAS_BCR`, ... `CAM_CC_MCLK1_BCR`, `CAM_CC_MCLK2_BCR`, `CAM_CC_MCLK3_BCR`, `CAM_CC_OPE_0_BCR`, `CAM_CC_TFE_0_BCR`, `CAM_CC_TFE_1_BCR`.

Power-domain/GDSC range: `CAM_CC_CAMSS_TOP_GDSC`=0 through `CAM_CC_CAMSS_TOP_GDSC`=0. Representative domains: `CAM_CC_CAMSS_TOP_GDSC`.

Macro inventory begins with:
- `CAM_CC_BPS_AHB_CLK` = 0 (clock, line 10)
- `CAM_CC_BPS_AREG_CLK` = 1 (clock, line 11)
- `CAM_CC_BPS_CLK` = 2 (clock, line 12)
- `CAM_CC_BPS_CLK_SRC` = 3 (clock, line 13)
- `CAM_CC_CAMNOC_ATB_CLK` = 4 (clock, line 14)
- `CAM_CC_CAMNOC_AXI_CLK` = 5 (clock, line 15)
- `CAM_CC_CAMNOC_AXI_CLK_SRC` = 6 (clock, line 16)
- `CAM_CC_CAMNOC_AXI_HF_CLK` = 7 (clock, line 17)
- `CAM_CC_CAMNOC_AXI_SF_CLK` = 8 (clock, line 18)
- `CAM_CC_CCI_0_CLK` = 9 (clock, line 19)
- ... 81 additional numeric binding macros continue in the same contiguous namespace sections.

## Control Flow

This header has no branches, calls, or runtime control flow. The effective flow is build-time and probe-time: DTS sources include the constants, the device-tree compiler stores the resulting integers in clock/reset/power-domain specifier cells, and the Qualcomm clock-controller driver exposes provider arrays whose indexes must match these values. Consumer drivers later resolve those phandles through common clock, reset-controller, or genpd APIs.

## State and Persistence Behavior

The file owns no memory, locks, hardware registers, or persistent storage. Its state is the ABI value assigned to each macro. Those values persist in compiled DTBs and out-of-tree device trees, so renumbering or deleting an existing define is a compatibility break even though no runtime state is stored here. Actual enable counts, reset assertion state, and GDSC power state are maintained by the clock/reset/power-domain drivers and hardware registers, not by this header.

## Dependencies and Integration Points

Direct source dependencies are intentionally minimal: the header has only SPDX/copyright comments, an include guard, macro definitions, and `#endif`. It is integrated by textual inclusion rather than linking. Local integration evidence: clock-controller driver references: `sources/distributed-fs/ceph-client/drivers/clk/qcom/camcc-sm4450.c`; device-tree references: `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/sm4450.dtsi`.

The semantic dependency is the matching provider implementation and its descriptor arrays. `qcom,sm4450-camcc.h` IDs must stay aligned with driver tables for camera PLLs, MCLKs, CSI/CSIPHY timers, IFE/TFE/SFE/BPS/IPE/JPEG/CPAS fabric clocks, resets, and camera GDSCs. DTS consumers depend on these exact constants for properties such as `clocks`, `resets`, `power-domains`, and named clock inputs.

## Risks and Edge Cases

The main risk is ABI drift: inserting new IDs in the middle, reusing a removed value, or moving a reset/GDSC ID to a different number can silently bind a DTS consumer to the wrong hardware clock or power domain. It also exports reset IDs (`CAM_CC_BPS_BCR`=0 through `CAM_CC_TFE_1_BCR`=17). Power-domain/GDSC IDs are exported as `CAM_CC_CAMSS_TOP_GDSC`=0 through `CAM_CC_CAMSS_TOP_GDSC`=0. Shared names such as PLLs, XO/sleep sources, bus clocks, and GDSCs are easy to copy between SoCs, but the numeric ordering must follow this specific provider, not a visually similar controller. Because the file is pure macros, the compiler provides little semantic checking beyond duplicate definitions and include-guard correctness.

## Test Signals

Useful validation includes building the relevant `drivers/clk/qcom` object with this header, compiling DTBs that include `qcom,sm4450-camcc.h`, and running `dtbs_check`/binding-schema checks for the affected SoC. Runtime smoke tests are provider probe success without missing clock/reset IDs, absence of `-ENOENT`/`-EINVAL` from clock lookups, expected entries under common-clock debugfs, and successful bring-up of consumers in the exported domain set: camera PLLs, MCLKs, CSI/CSIPHY timers, IFE/TFE/SFE/BPS/IPE/JPEG/CPAS fabric clocks, resets, and camera GDSCs. For edits, diff the numeric table against the matching driver arrays and boot at least one DTS consumer when local hardware or emulation coverage exists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sm4450-camcc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sm4450-dispcc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sm4450-dispcc.h

## Purpose

`sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sm4450-dispcc.h` defines the public device-tree numeric IDs for the Qualcomm display clock-controller binding associated with `qcom,sm4450-dispcc.h` / `sm4450`. The source was read completely for this report (51 lines). It is not executable kernel code; it is a stable binding contract included by DTS files and by the matching `drivers/clk/qcom` provider so that phandle clock, reset, and power-domain specifiers use the same indexes.

## Important APIs, Types, and Functions

There are no C functions, structs, or runtime APIs. The exported API is a set of preprocessor constants guarded by `_DT_BINDINGS_CLK_QCOM_DISP_CC_SM4450_H`. This header defines 31 clock IDs, 3 reset IDs, and 2 power-domain/GDSC IDs, for 36 numeric binding macros total.

Clock ID range: `DISP_CC_MDSS_AHB1_CLK`=0 through `DISP_CC_XO_CLK_SRC`=30. Representative clocks: `DISP_CC_MDSS_AHB1_CLK`, `DISP_CC_MDSS_AHB_CLK`, `DISP_CC_MDSS_AHB_CLK_SRC`, `DISP_CC_MDSS_BYTE0_CLK`, `DISP_CC_MDSS_BYTE0_CLK_SRC`, `DISP_CC_MDSS_BYTE0_DIV_CLK_SRC`, ... `DISP_CC_PLL0`, `DISP_CC_PLL1`, `DISP_CC_SLEEP_CLK`, `DISP_CC_SLEEP_CLK_SRC`, `DISP_CC_XO_CLK`, `DISP_CC_XO_CLK_SRC`.

Reset ID range: `DISP_CC_MDSS_CORE_BCR`=0 through `DISP_CC_MDSS_RSCC_BCR`=2. Representative resets: `DISP_CC_MDSS_CORE_BCR`, `DISP_CC_MDSS_CORE_INT2_BCR`, `DISP_CC_MDSS_RSCC_BCR`.

Power-domain/GDSC range: `DISP_CC_MDSS_CORE_GDSC`=0 through `DISP_CC_MDSS_CORE_INT2_GDSC`=1. Representative domains: `DISP_CC_MDSS_CORE_GDSC`, `DISP_CC_MDSS_CORE_INT2_GDSC`.

Macro inventory begins with:
- `DISP_CC_MDSS_AHB1_CLK` = 0 (clock, line 10)
- `DISP_CC_MDSS_AHB_CLK` = 1 (clock, line 11)
- `DISP_CC_MDSS_AHB_CLK_SRC` = 2 (clock, line 12)
- `DISP_CC_MDSS_BYTE0_CLK` = 3 (clock, line 13)
- `DISP_CC_MDSS_BYTE0_CLK_SRC` = 4 (clock, line 14)
- `DISP_CC_MDSS_BYTE0_DIV_CLK_SRC` = 5 (clock, line 15)
- `DISP_CC_MDSS_BYTE0_INTF_CLK` = 6 (clock, line 16)
- `DISP_CC_MDSS_ESC0_CLK` = 7 (clock, line 17)
- `DISP_CC_MDSS_ESC0_CLK_SRC` = 8 (clock, line 18)
- `DISP_CC_MDSS_MDP1_CLK` = 9 (clock, line 19)
- ... 26 additional numeric binding macros continue in the same contiguous namespace sections.

## Control Flow

This header has no branches, calls, or runtime control flow. The effective flow is build-time and probe-time: DTS sources include the constants, the device-tree compiler stores the resulting integers in clock/reset/power-domain specifier cells, and the Qualcomm clock-controller driver exposes provider arrays whose indexes must match these values. Consumer drivers later resolve those phandles through common clock, reset-controller, or genpd APIs.

## State and Persistence Behavior

The file owns no memory, locks, hardware registers, or persistent storage. Its state is the ABI value assigned to each macro. Those values persist in compiled DTBs and out-of-tree device trees, so renumbering or deleting an existing define is a compatibility break even though no runtime state is stored here. Actual enable counts, reset assertion state, and GDSC power state are maintained by the clock/reset/power-domain drivers and hardware registers, not by this header.

## Dependencies and Integration Points

Direct source dependencies are intentionally minimal: the header has only SPDX/copyright comments, an include guard, macro definitions, and `#endif`. It is integrated by textual inclusion rather than linking. Local integration evidence: clock-controller driver references: `sources/distributed-fs/ceph-client/drivers/clk/qcom/dispcc-sm4450.c`; device-tree references: `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/sm4450.dtsi`.

The semantic dependency is the matching provider implementation and its descriptor arrays. `qcom,sm4450-dispcc.h` IDs must stay aligned with driver tables for MDSS AHB/AXI, MDP, DSI byte/escape/pixel, DisplayPort link/pixel/aux, vsync, resets, and display GDSCs. DTS consumers depend on these exact constants for properties such as `clocks`, `resets`, `power-domains`, and named clock inputs.

## Risks and Edge Cases

The main risk is ABI drift: inserting new IDs in the middle, reusing a removed value, or moving a reset/GDSC ID to a different number can silently bind a DTS consumer to the wrong hardware clock or power domain. It also exports reset IDs (`DISP_CC_MDSS_CORE_BCR`=0 through `DISP_CC_MDSS_RSCC_BCR`=2). Power-domain/GDSC IDs are exported as `DISP_CC_MDSS_CORE_GDSC`=0 through `DISP_CC_MDSS_CORE_INT2_GDSC`=1. Shared names such as PLLs, XO/sleep sources, bus clocks, and GDSCs are easy to copy between SoCs, but the numeric ordering must follow this specific provider, not a visually similar controller. Because the file is pure macros, the compiler provides little semantic checking beyond duplicate definitions and include-guard correctness.

## Test Signals

Useful validation includes building the relevant `drivers/clk/qcom` object with this header, compiling DTBs that include `qcom,sm4450-dispcc.h`, and running `dtbs_check`/binding-schema checks for the affected SoC. Runtime smoke tests are provider probe success without missing clock/reset IDs, absence of `-ENOENT`/`-EINVAL` from clock lookups, expected entries under common-clock debugfs, and successful bring-up of consumers in the exported domain set: MDSS AHB/AXI, MDP, DSI byte/escape/pixel, DisplayPort link/pixel/aux, vsync, resets, and display GDSCs. For edits, diff the numeric table against the matching driver arrays and boot at least one DTS consumer when local hardware or emulation coverage exists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sm4450-dispcc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sm4450-gcc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sm4450-gcc.h

## Purpose

`sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sm4450-gcc.h` defines the public device-tree numeric IDs for the Qualcomm global clock-controller binding associated with `qcom,sm4450-gcc.h` / `sm4450`. The source was read completely for this report (197 lines). It is not executable kernel code; it is a stable binding contract included by DTS files and by the matching `drivers/clk/qcom` provider so that phandle clock, reset, and power-domain specifiers use the same indexes.

## Important APIs, Types, and Functions

There are no C functions, structs, or runtime APIs. The exported API is a set of preprocessor constants guarded by `_DT_BINDINGS_CLK_QCOM_GCC_SM4450_H`. This header defines 145 clock IDs, 32 reset IDs, and 5 power-domain/GDSC IDs, for 182 numeric binding macros total.

Clock ID range: `GCC_AGGRE_NOC_PCIE_0_AXI_CLK`=0 through `GCC_VIDEO_XO_CLK`=144. Representative clocks: `GCC_AGGRE_NOC_PCIE_0_AXI_CLK`, `GCC_AGGRE_UFS_PHY_AXI_CLK`, `GCC_AGGRE_UFS_PHY_AXI_HW_CTL_CLK`, `GCC_AGGRE_USB3_PRIM_AXI_CLK`, `GCC_BOOT_ROM_AHB_CLK`, `GCC_CAMERA_AHB_CLK`, ... `GCC_VIDEO_AHB_CLK`, `GCC_VIDEO_THROTTLE_CORE_CLK`, `GCC_VIDEO_VCODEC0_SYS_CLK`, `GCC_VIDEO_VENUS_CLK_SRC`, `GCC_VIDEO_VENUS_CTL_CLK`, `GCC_VIDEO_XO_CLK`.

Reset ID range: `GCC_CAMERA_BCR`=0 through `GCC_VIDEO_VENUS_CTL_CLK_ARES`=31. Representative resets: `GCC_CAMERA_BCR`, `GCC_DISPLAY_BCR`, `GCC_GPU_BCR`, `GCC_PCIE_0_BCR`, `GCC_PCIE_0_LINK_DOWN_BCR`, `GCC_PCIE_0_NOCSR_COM_PHY_BCR`, ... `GCC_VCODEC0_BCR`, `GCC_VENUS_BCR`, `GCC_VIDEO_BCR`, `GCC_VIDEO_VENUS_BCR`, `GCC_VENUS_CTL_AXI_CLK_ARES`, `GCC_VIDEO_VENUS_CTL_CLK_ARES`.

Power-domain/GDSC range: `GCC_PCIE_0_GDSC`=0 through `GCC_VENUS_GDSC`=4. Representative domains: `GCC_PCIE_0_GDSC`, `GCC_UFS_PHY_GDSC`, `GCC_USB30_PRIM_GDSC`, `GCC_VCODEC0_GDSC`, `GCC_VENUS_GDSC`.

Macro inventory begins with:
- `GCC_AGGRE_NOC_PCIE_0_AXI_CLK` = 0 (clock, line 10)
- `GCC_AGGRE_UFS_PHY_AXI_CLK` = 1 (clock, line 11)
- `GCC_AGGRE_UFS_PHY_AXI_HW_CTL_CLK` = 2 (clock, line 12)
- `GCC_AGGRE_USB3_PRIM_AXI_CLK` = 3 (clock, line 13)
- `GCC_BOOT_ROM_AHB_CLK` = 4 (clock, line 14)
- `GCC_CAMERA_AHB_CLK` = 5 (clock, line 15)
- `GCC_CAMERA_HF_AXI_CLK` = 6 (clock, line 16)
- `GCC_CAMERA_SF_AXI_CLK` = 7 (clock, line 17)
- `GCC_CAMERA_SLEEP_CLK` = 8 (clock, line 18)
- `GCC_CAMERA_XO_CLK` = 9 (clock, line 19)
- ... 172 additional numeric binding macros continue in the same contiguous namespace sections.

## Control Flow

This header has no branches, calls, or runtime control flow. The effective flow is build-time and probe-time: DTS sources include the constants, the device-tree compiler stores the resulting integers in clock/reset/power-domain specifier cells, and the Qualcomm clock-controller driver exposes provider arrays whose indexes must match these values. Consumer drivers later resolve those phandles through common clock, reset-controller, or genpd APIs.

## State and Persistence Behavior

The file owns no memory, locks, hardware registers, or persistent storage. Its state is the ABI value assigned to each macro. Those values persist in compiled DTBs and out-of-tree device trees, so renumbering or deleting an existing define is a compatibility break even though no runtime state is stored here. Actual enable counts, reset assertion state, and GDSC power state are maintained by the clock/reset/power-domain drivers and hardware registers, not by this header.

## Dependencies and Integration Points

Direct source dependencies are intentionally minimal: the header has only SPDX/copyright comments, an include guard, macro definitions, and `#endif`. It is integrated by textual inclusion rather than linking. Local integration evidence: clock-controller driver references: `sources/distributed-fs/ceph-client/drivers/clk/qcom/gcc-sm4450.c`; device-tree references: `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/sm4450.dtsi`.

The semantic dependency is the matching provider implementation and its descriptor arrays. `qcom,sm4450-gcc.h` IDs must stay aligned with driver tables for global PLLs plus bus, QUP, USB, PCIe, UFS, SDCC, camera/display/video/gpu vote, reset, and GDSC IDs. DTS consumers depend on these exact constants for properties such as `clocks`, `resets`, `power-domains`, and named clock inputs.

## Risks and Edge Cases

The main risk is ABI drift: inserting new IDs in the middle, reusing a removed value, or moving a reset/GDSC ID to a different number can silently bind a DTS consumer to the wrong hardware clock or power domain. It also exports reset IDs (`GCC_CAMERA_BCR`=0 through `GCC_VIDEO_VENUS_CTL_CLK_ARES`=31). Power-domain/GDSC IDs are exported as `GCC_PCIE_0_GDSC`=0 through `GCC_VENUS_GDSC`=4. Shared names such as PLLs, XO/sleep sources, bus clocks, and GDSCs are easy to copy between SoCs, but the numeric ordering must follow this specific provider, not a visually similar controller. Because the file is pure macros, the compiler provides little semantic checking beyond duplicate definitions and include-guard correctness.

## Test Signals

Useful validation includes building the relevant `drivers/clk/qcom` object with this header, compiling DTBs that include `qcom,sm4450-gcc.h`, and running `dtbs_check`/binding-schema checks for the affected SoC. Runtime smoke tests are provider probe success without missing clock/reset IDs, absence of `-ENOENT`/`-EINVAL` from clock lookups, expected entries under common-clock debugfs, and successful bring-up of consumers in the exported domain set: global PLLs plus bus, QUP, USB, PCIe, UFS, SDCC, camera/display/video/gpu vote, reset, and GDSC IDs. For edits, diff the numeric table against the matching driver arrays and boot at least one DTS consumer when local hardware or emulation coverage exists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sm4450-gcc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sm4450-gpucc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sm4450-gpucc.h

## Purpose

`sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sm4450-gpucc.h` defines the public device-tree numeric IDs for the Qualcomm GPU clock-controller binding associated with `qcom,sm4450-gpucc.h` / `sm4450`. The source was read completely for this report (62 lines). It is not executable kernel code; it is a stable binding contract included by DTS files and by the matching `drivers/clk/qcom` provider so that phandle clock, reset, and power-domain specifiers use the same indexes.

## Important APIs, Types, and Functions

There are no C functions, structs, or runtime APIs. The exported API is a set of preprocessor constants guarded by `_DT_BINDINGS_CLK_QCOM_GPU_CC_SM4450_H`. This header defines 34 clock IDs, 11 reset IDs, and 2 power-domain/GDSC IDs, for 47 numeric binding macros total.

Clock ID range: `GPU_CC_AHB_CLK`=0 through `GPU_CC_XO_DIV_CLK_SRC`=33. Representative clocks: `GPU_CC_AHB_CLK`, `GPU_CC_CB_CLK`, `GPU_CC_CRC_AHB_CLK`, `GPU_CC_CX_FF_CLK`, `GPU_CC_CX_GFX3D_CLK`, `GPU_CC_CX_GFX3D_SLV_CLK`, ... `GPU_CC_MND1X_0_GFX3D_CLK`, `GPU_CC_PLL0`, `GPU_CC_PLL1`, `GPU_CC_SLEEP_CLK`, `GPU_CC_XO_CLK_SRC`, `GPU_CC_XO_DIV_CLK_SRC`.

Reset ID range: `GPU_CC_ACD_BCR`=0 through `GPU_CC_RBCPR_BCR`=10. Representative resets: `GPU_CC_ACD_BCR`, `GPU_CC_CB_BCR`, `GPU_CC_CX_BCR`, `GPU_CC_FAST_HUB_BCR`, `GPU_CC_FF_BCR`, `GPU_CC_GFX3D_AON_BCR`, `GPU_CC_GMU_BCR`, `GPU_CC_GX_BCR`, `GPU_CC_XO_BCR`, `GPU_CC_GX_ACD_IROOT_BCR`, `GPU_CC_RBCPR_BCR`.

Power-domain/GDSC range: `GPU_CC_CX_GDSC`=0 through `GPU_CC_GX_GDSC`=1. Representative domains: `GPU_CC_CX_GDSC`, `GPU_CC_GX_GDSC`.

Macro inventory begins with:
- `GPU_CC_AHB_CLK` = 0 (clock, line 10)
- `GPU_CC_CB_CLK` = 1 (clock, line 11)
- `GPU_CC_CRC_AHB_CLK` = 2 (clock, line 12)
- `GPU_CC_CX_FF_CLK` = 3 (clock, line 13)
- `GPU_CC_CX_GFX3D_CLK` = 4 (clock, line 14)
- `GPU_CC_CX_GFX3D_SLV_CLK` = 5 (clock, line 15)
- `GPU_CC_CX_GMU_CLK` = 6 (clock, line 16)
- `GPU_CC_CX_SNOC_DVM_CLK` = 7 (clock, line 17)
- `GPU_CC_CXO_AON_CLK` = 8 (clock, line 18)
- `GPU_CC_CXO_CLK` = 9 (clock, line 19)
- ... 37 additional numeric binding macros continue in the same contiguous namespace sections.

## Control Flow

This header has no branches, calls, or runtime control flow. The effective flow is build-time and probe-time: DTS sources include the constants, the device-tree compiler stores the resulting integers in clock/reset/power-domain specifier cells, and the Qualcomm clock-controller driver exposes provider arrays whose indexes must match these values. Consumer drivers later resolve those phandles through common clock, reset-controller, or genpd APIs.

## State and Persistence Behavior

The file owns no memory, locks, hardware registers, or persistent storage. Its state is the ABI value assigned to each macro. Those values persist in compiled DTBs and out-of-tree device trees, so renumbering or deleting an existing define is a compatibility break even though no runtime state is stored here. Actual enable counts, reset assertion state, and GDSC power state are maintained by the clock/reset/power-domain drivers and hardware registers, not by this header.

## Dependencies and Integration Points

Direct source dependencies are intentionally minimal: the header has only SPDX/copyright comments, an include guard, macro definitions, and `#endif`. It is integrated by textual inclusion rather than linking. Local integration evidence: clock-controller driver references: `sources/distributed-fs/ceph-client/drivers/clk/qcom/gpucc-sm4450.c`; device-tree references: `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/sm4450.dtsi`.

The semantic dependency is the matching provider implementation and its descriptor arrays. `qcom,sm4450-gpucc.h` IDs must stay aligned with driver tables for GPU PLL/RCG, GMU, CX/GX, hub, memory NoC, XO/sleep, SMMU vote, reset, and GDSC IDs. DTS consumers depend on these exact constants for properties such as `clocks`, `resets`, `power-domains`, and named clock inputs.

## Risks and Edge Cases

The main risk is ABI drift: inserting new IDs in the middle, reusing a removed value, or moving a reset/GDSC ID to a different number can silently bind a DTS consumer to the wrong hardware clock or power domain. It also exports reset IDs (`GPU_CC_ACD_BCR`=0 through `GPU_CC_RBCPR_BCR`=10). Power-domain/GDSC IDs are exported as `GPU_CC_CX_GDSC`=0 through `GPU_CC_GX_GDSC`=1. Shared names such as PLLs, XO/sleep sources, bus clocks, and GDSCs are easy to copy between SoCs, but the numeric ordering must follow this specific provider, not a visually similar controller. Because the file is pure macros, the compiler provides little semantic checking beyond duplicate definitions and include-guard correctness.

## Test Signals

Useful validation includes building the relevant `drivers/clk/qcom` object with this header, compiling DTBs that include `qcom,sm4450-gpucc.h`, and running `dtbs_check`/binding-schema checks for the affected SoC. Runtime smoke tests are provider probe success without missing clock/reset IDs, absence of `-ENOENT`/`-EINVAL` from clock lookups, expected entries under common-clock debugfs, and successful bring-up of consumers in the exported domain set: GPU PLL/RCG, GMU, CX/GX, hub, memory NoC, XO/sleep, SMMU vote, reset, and GDSC IDs. For edits, diff the numeric table against the matching driver arrays and boot at least one DTS consumer when local hardware or emulation coverage exists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sm4450-gpucc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sm6115-dispcc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sm6115-dispcc.h

## Purpose

`sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sm6115-dispcc.h` defines the public device-tree numeric IDs for the Qualcomm display clock-controller binding associated with `qcom,sm6115-dispcc.h` / `sm6115`. The source was read completely for this report (39 lines). It is not executable kernel code; it is a stable binding contract included by DTS files and by the matching `drivers/clk/qcom` provider so that phandle clock, reset, and power-domain specifiers use the same indexes.

## Important APIs, Types, and Functions

There are no C functions, structs, or runtime APIs. The exported API is a set of preprocessor constants guarded by `_DT_BINDINGS_CLK_QCOM_DISP_CC_SM6115_H`. This header defines 22 clock IDs, 1 reset ID, and 1 power-domain/GDSC ID, for 24 numeric binding macros total.

Clock ID range: `DISP_CC_PLL0`=0 through `DISP_CC_SLEEP_CLK_SRC`=21. Representative clocks: `DISP_CC_PLL0`, `DISP_CC_PLL0_OUT_MAIN`, `DISP_CC_MDSS_AHB_CLK`, `DISP_CC_MDSS_AHB_CLK_SRC`, `DISP_CC_MDSS_BYTE0_CLK`, `DISP_CC_MDSS_BYTE0_CLK_SRC`, ... `DISP_CC_MDSS_ROT_CLK`, `DISP_CC_MDSS_ROT_CLK_SRC`, `DISP_CC_MDSS_VSYNC_CLK`, `DISP_CC_MDSS_VSYNC_CLK_SRC`, `DISP_CC_SLEEP_CLK`, `DISP_CC_SLEEP_CLK_SRC`.

Reset ID range: `DISP_CC_MDSS_CORE_BCR`=0 through `DISP_CC_MDSS_CORE_BCR`=0. Representative resets: `DISP_CC_MDSS_CORE_BCR`.

Power-domain/GDSC range: `MDSS_GDSC`=0 through `MDSS_GDSC`=0. Representative domains: `MDSS_GDSC`.

Macro inventory begins with:
- `DISP_CC_PLL0` = 0 (clock, line 10)
- `DISP_CC_PLL0_OUT_MAIN` = 1 (clock, line 11)
- `DISP_CC_MDSS_AHB_CLK` = 2 (clock, line 12)
- `DISP_CC_MDSS_AHB_CLK_SRC` = 3 (clock, line 13)
- `DISP_CC_MDSS_BYTE0_CLK` = 4 (clock, line 14)
- `DISP_CC_MDSS_BYTE0_CLK_SRC` = 5 (clock, line 15)
- `DISP_CC_MDSS_BYTE0_DIV_CLK_SRC` = 6 (clock, line 16)
- `DISP_CC_MDSS_BYTE0_INTF_CLK` = 7 (clock, line 17)
- `DISP_CC_MDSS_ESC0_CLK` = 8 (clock, line 18)
- `DISP_CC_MDSS_ESC0_CLK_SRC` = 9 (clock, line 19)
- ... 14 additional numeric binding macros continue in the same contiguous namespace sections.

## Control Flow

This header has no branches, calls, or runtime control flow. The effective flow is build-time and probe-time: DTS sources include the constants, the device-tree compiler stores the resulting integers in clock/reset/power-domain specifier cells, and the Qualcomm clock-controller driver exposes provider arrays whose indexes must match these values. Consumer drivers later resolve those phandles through common clock, reset-controller, or genpd APIs.

## State and Persistence Behavior

The file owns no memory, locks, hardware registers, or persistent storage. Its state is the ABI value assigned to each macro. Those values persist in compiled DTBs and out-of-tree device trees, so renumbering or deleting an existing define is a compatibility break even though no runtime state is stored here. Actual enable counts, reset assertion state, and GDSC power state are maintained by the clock/reset/power-domain drivers and hardware registers, not by this header.

## Dependencies and Integration Points

Direct source dependencies are intentionally minimal: the header has only SPDX/copyright comments, an include guard, macro definitions, and `#endif`. It is integrated by textual inclusion rather than linking. Local integration evidence: clock-controller driver references: `sources/distributed-fs/ceph-client/drivers/clk/qcom/dispcc-sm6115.c`; device-tree references: `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/sm6115.dtsi`.

The semantic dependency is the matching provider implementation and its descriptor arrays. `qcom,sm6115-dispcc.h` IDs must stay aligned with driver tables for MDSS AHB/AXI, MDP, DSI byte/escape/pixel, DisplayPort link/pixel/aux, vsync, resets, and display GDSCs. DTS consumers depend on these exact constants for properties such as `clocks`, `resets`, `power-domains`, and named clock inputs.

## Risks and Edge Cases

The main risk is ABI drift: inserting new IDs in the middle, reusing a removed value, or moving a reset/GDSC ID to a different number can silently bind a DTS consumer to the wrong hardware clock or power domain. It also exports reset IDs (`DISP_CC_MDSS_CORE_BCR`=0 through `DISP_CC_MDSS_CORE_BCR`=0). Power-domain/GDSC IDs are exported as `MDSS_GDSC`=0 through `MDSS_GDSC`=0. Shared names such as PLLs, XO/sleep sources, bus clocks, and GDSCs are easy to copy between SoCs, but the numeric ordering must follow this specific provider, not a visually similar controller. Because the file is pure macros, the compiler provides little semantic checking beyond duplicate definitions and include-guard correctness.

## Test Signals

Useful validation includes building the relevant `drivers/clk/qcom` object with this header, compiling DTBs that include `qcom,sm6115-dispcc.h`, and running `dtbs_check`/binding-schema checks for the affected SoC. Runtime smoke tests are provider probe success without missing clock/reset IDs, absence of `-ENOENT`/`-EINVAL` from clock lookups, expected entries under common-clock debugfs, and successful bring-up of consumers in the exported domain set: MDSS AHB/AXI, MDP, DSI byte/escape/pixel, DisplayPort link/pixel/aux, vsync, resets, and display GDSCs. For edits, diff the numeric table against the matching driver arrays and boot at least one DTS consumer when local hardware or emulation coverage exists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sm6115-dispcc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sm6115-gpucc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sm6115-gpucc.h

## Purpose

`sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sm6115-gpucc.h` defines the public device-tree numeric IDs for the Qualcomm GPU clock-controller binding associated with `qcom,sm6115-gpucc.h` / `sm6115`. The source was read completely for this report (36 lines). It is not executable kernel code; it is a stable binding contract included by DTS files and by the matching `drivers/clk/qcom` provider so that phandle clock, reset, and power-domain specifiers use the same indexes.

## Important APIs, Types, and Functions

There are no C functions, structs, or runtime APIs. The exported API is a set of preprocessor constants guarded by `_DT_BINDINGS_CLK_QCOM_GPU_CC_SM6115_H`. This header defines 17 clock IDs, 1 reset ID, and 2 power-domain/GDSC IDs, for 20 numeric binding macros total.

Clock ID range: `GPU_CC_PLL0`=0 through `GPU_CC_HLOS1_VOTE_GPU_SMMU_CLK`=16. Representative clocks: `GPU_CC_PLL0`, `GPU_CC_PLL0_OUT_AUX2`, `GPU_CC_PLL1`, `GPU_CC_PLL1_OUT_AUX`, `GPU_CC_AHB_CLK`, `GPU_CC_CRC_AHB_CLK`, ... `GPU_CC_GMU_CLK_SRC`, `GPU_CC_GX_CXO_CLK`, `GPU_CC_GX_GFX3D_CLK`, `GPU_CC_GX_GFX3D_CLK_SRC`, `GPU_CC_SLEEP_CLK`, `GPU_CC_HLOS1_VOTE_GPU_SMMU_CLK`.

Reset ID range: `GPU_GX_BCR`=0 through `GPU_GX_BCR`=0. Representative resets: `GPU_GX_BCR`.

Power-domain/GDSC range: `GPU_CX_GDSC`=0 through `GPU_GX_GDSC`=1. Representative domains: `GPU_CX_GDSC`, `GPU_GX_GDSC`.

Macro inventory begins with:
- `GPU_CC_PLL0` = 0 (clock, line 11)
- `GPU_CC_PLL0_OUT_AUX2` = 1 (clock, line 12)
- `GPU_CC_PLL1` = 2 (clock, line 13)
- `GPU_CC_PLL1_OUT_AUX` = 3 (clock, line 14)
- `GPU_CC_AHB_CLK` = 4 (clock, line 15)
- `GPU_CC_CRC_AHB_CLK` = 5 (clock, line 16)
- `GPU_CC_CX_GFX3D_CLK` = 6 (clock, line 17)
- `GPU_CC_CX_GMU_CLK` = 7 (clock, line 18)
- `GPU_CC_CX_SNOC_DVM_CLK` = 8 (clock, line 19)
- `GPU_CC_CXO_AON_CLK` = 9 (clock, line 20)
- ... 10 additional numeric binding macros continue in the same contiguous namespace sections.

## Control Flow

This header has no branches, calls, or runtime control flow. The effective flow is build-time and probe-time: DTS sources include the constants, the device-tree compiler stores the resulting integers in clock/reset/power-domain specifier cells, and the Qualcomm clock-controller driver exposes provider arrays whose indexes must match these values. Consumer drivers later resolve those phandles through common clock, reset-controller, or genpd APIs.

## State and Persistence Behavior

The file owns no memory, locks, hardware registers, or persistent storage. Its state is the ABI value assigned to each macro. Those values persist in compiled DTBs and out-of-tree device trees, so renumbering or deleting an existing define is a compatibility break even though no runtime state is stored here. Actual enable counts, reset assertion state, and GDSC power state are maintained by the clock/reset/power-domain drivers and hardware registers, not by this header.

## Dependencies and Integration Points

Direct source dependencies are intentionally minimal: the header has only SPDX/copyright comments, an include guard, macro definitions, and `#endif`. It is integrated by textual inclusion rather than linking. Local integration evidence: clock-controller driver references: `sources/distributed-fs/ceph-client/drivers/clk/qcom/gpucc-sm6115.c`; device-tree references: `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/sm6115.dtsi`.

The semantic dependency is the matching provider implementation and its descriptor arrays. `qcom,sm6115-gpucc.h` IDs must stay aligned with driver tables for GPU PLL/RCG, GMU, CX/GX, hub, memory NoC, XO/sleep, SMMU vote, reset, and GDSC IDs. DTS consumers depend on these exact constants for properties such as `clocks`, `resets`, `power-domains`, and named clock inputs.

## Risks and Edge Cases

The main risk is ABI drift: inserting new IDs in the middle, reusing a removed value, or moving a reset/GDSC ID to a different number can silently bind a DTS consumer to the wrong hardware clock or power domain. It also exports reset IDs (`GPU_GX_BCR`=0 through `GPU_GX_BCR`=0). Power-domain/GDSC IDs are exported as `GPU_CX_GDSC`=0 through `GPU_GX_GDSC`=1. Shared names such as PLLs, XO/sleep sources, bus clocks, and GDSCs are easy to copy between SoCs, but the numeric ordering must follow this specific provider, not a visually similar controller. Because the file is pure macros, the compiler provides little semantic checking beyond duplicate definitions and include-guard correctness.

## Test Signals

Useful validation includes building the relevant `drivers/clk/qcom` object with this header, compiling DTBs that include `qcom,sm6115-gpucc.h`, and running `dtbs_check`/binding-schema checks for the affected SoC. Runtime smoke tests are provider probe success without missing clock/reset IDs, absence of `-ENOENT`/`-EINVAL` from clock lookups, expected entries under common-clock debugfs, and successful bring-up of consumers in the exported domain set: GPU PLL/RCG, GMU, CX/GX, hub, memory NoC, XO/sleep, SMMU vote, reset, and GDSC IDs. For edits, diff the numeric table against the matching driver arrays and boot at least one DTS consumer when local hardware or emulation coverage exists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sm6115-gpucc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sm6115-lpasscc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sm6115-lpasscc.h

## Purpose

`sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sm6115-lpasscc.h` defines the public device-tree numeric IDs for the Qualcomm LPASS/audio clock-controller binding associated with `qcom,sm6115-lpasscc.h` / `sm6115`. The source was read completely for this report (15 lines). It is not executable kernel code; it is a stable binding contract included by DTS files and by the matching `drivers/clk/qcom` provider so that phandle clock, reset, and power-domain specifiers use the same indexes.

## Important APIs, Types, and Functions

There are no C functions, structs, or runtime APIs. The exported API is a set of preprocessor constants guarded by `_DT_BINDINGS_CLK_QCOM_LPASSCC_SM6115_H`. This header defines 2 clock IDs, 0 reset IDs, and 0 power-domain/GDSC IDs, for 2 numeric binding macros total.

Clock ID range: `LPASS_SWR_TX_CONFIG_CGCR`=0 through `LPASS_SWR_TX_CONFIG_CGCR`=0. Representative clocks: `LPASS_SWR_TX_CONFIG_CGCR`, `LPASS_AUDIO_SWR_RX_CGCR`.

Reset ID range: none. Representative resets: none.

Power-domain/GDSC range: none. Representative domains: none.

Macro inventory begins with:
- `LPASS_SWR_TX_CONFIG_CGCR` = 0 (clock, line 10)
- `LPASS_AUDIO_SWR_RX_CGCR` = 0 (clock, line 13)

## Control Flow

This header has no branches, calls, or runtime control flow. The effective flow is build-time and probe-time: DTS sources include the constants, the device-tree compiler stores the resulting integers in clock/reset/power-domain specifier cells, and the Qualcomm clock-controller driver exposes provider arrays whose indexes must match these values. Consumer drivers later resolve those phandles through common clock, reset-controller, or genpd APIs.

## State and Persistence Behavior

The file owns no memory, locks, hardware registers, or persistent storage. Its state is the ABI value assigned to each macro. Those values persist in compiled DTBs and out-of-tree device trees, so renumbering or deleting an existing define is a compatibility break even though no runtime state is stored here. Actual enable counts, reset assertion state, and GDSC power state are maintained by the clock/reset/power-domain drivers and hardware registers, not by this header.

## Dependencies and Integration Points

Direct source dependencies are intentionally minimal: the header has only SPDX/copyright comments, an include guard, macro definitions, and `#endif`. It is integrated by textual inclusion rather than linking. Local integration evidence: clock-controller driver references: `sources/distributed-fs/ceph-client/drivers/clk/qcom/lpasscc-sm6115.c`.

The semantic dependency is the matching provider implementation and its descriptor arrays. `qcom,sm6115-lpasscc.h` IDs must stay aligned with driver tables for audio and always-on LPASS clock IDs used by the Qualcomm GFM/LPASS clock driver. DTS consumers depend on these exact constants for properties such as `clocks`, `resets`, `power-domains`, and named clock inputs.

## Risks and Edge Cases

The main risk is ABI drift: inserting new IDs in the middle, reusing a removed value, or moving a reset/GDSC ID to a different number can silently bind a DTS consumer to the wrong hardware clock or power domain. It does not export reset IDs in this clock header; reset bindings are either absent for this controller or live in a paired reset binding header/driver table. It does not export GDSC or power-domain IDs. Shared names such as PLLs, XO/sleep sources, bus clocks, and GDSCs are easy to copy between SoCs, but the numeric ordering must follow this specific provider, not a visually similar controller. Because the file is pure macros, the compiler provides little semantic checking beyond duplicate definitions and include-guard correctness.

## Test Signals

Useful validation includes building the relevant `drivers/clk/qcom` object with this header, compiling DTBs that include `qcom,sm6115-lpasscc.h`, and running `dtbs_check`/binding-schema checks for the affected SoC. Runtime smoke tests are provider probe success without missing clock/reset IDs, absence of `-ENOENT`/`-EINVAL` from clock lookups, expected entries under common-clock debugfs, and successful bring-up of consumers in the exported domain set: audio and always-on LPASS clock IDs used by the Qualcomm GFM/LPASS clock driver. For edits, diff the numeric table against the matching driver arrays and boot at least one DTS consumer when local hardware or emulation coverage exists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sm6115-lpasscc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sm6125-gpucc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sm6125-gpucc.h

## Purpose

`sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sm6125-gpucc.h` defines the public device-tree numeric IDs for the Qualcomm GPU clock-controller binding associated with `qcom,sm6125-gpucc.h` / `sm6125`. The source was read completely for this report (31 lines). It is not executable kernel code; it is a stable binding contract included by DTS files and by the matching `drivers/clk/qcom` provider so that phandle clock, reset, and power-domain specifiers use the same indexes.

## Important APIs, Types, and Functions

There are no C functions, structs, or runtime APIs. The exported API is a set of preprocessor constants guarded by `_DT_BINDINGS_CLK_QCOM_GPU_CC_SM6125_H`. This header defines 15 clock IDs, 0 reset IDs, and 2 power-domain/GDSC IDs, for 17 numeric binding macros total.

Clock ID range: `GPU_CC_PLL0_OUT_AUX2`=0 through `GPU_CC_HLOS1_VOTE_GPU_SMMU_CLK`=14. Representative clocks: `GPU_CC_PLL0_OUT_AUX2`, `GPU_CC_PLL1_OUT_AUX2`, `GPU_CC_CRC_AHB_CLK`, `GPU_CC_CX_APB_CLK`, `GPU_CC_CX_GFX3D_CLK`, `GPU_CC_CX_GMU_CLK`, ... `GPU_CC_GMU_CLK_SRC`, `GPU_CC_SLEEP_CLK`, `GPU_CC_GX_GFX3D_CLK`, `GPU_CC_GX_GFX3D_CLK_SRC`, `GPU_CC_AHB_CLK`, `GPU_CC_HLOS1_VOTE_GPU_SMMU_CLK`.

Reset ID range: none. Representative resets: none.

Power-domain/GDSC range: `GPU_CX_GDSC`=0 through `GPU_GX_GDSC`=1. Representative domains: `GPU_CX_GDSC`, `GPU_GX_GDSC`.

Macro inventory begins with:
- `GPU_CC_PLL0_OUT_AUX2` = 0 (clock, line 11)
- `GPU_CC_PLL1_OUT_AUX2` = 1 (clock, line 12)
- `GPU_CC_CRC_AHB_CLK` = 2 (clock, line 13)
- `GPU_CC_CX_APB_CLK` = 3 (clock, line 14)
- `GPU_CC_CX_GFX3D_CLK` = 4 (clock, line 15)
- `GPU_CC_CX_GMU_CLK` = 5 (clock, line 16)
- `GPU_CC_CX_SNOC_DVM_CLK` = 6 (clock, line 17)
- `GPU_CC_CXO_AON_CLK` = 7 (clock, line 18)
- `GPU_CC_CXO_CLK` = 8 (clock, line 19)
- `GPU_CC_GMU_CLK_SRC` = 9 (clock, line 20)
- ... 7 additional numeric binding macros continue in the same contiguous namespace sections.

## Control Flow

This header has no branches, calls, or runtime control flow. The effective flow is build-time and probe-time: DTS sources include the constants, the device-tree compiler stores the resulting integers in clock/reset/power-domain specifier cells, and the Qualcomm clock-controller driver exposes provider arrays whose indexes must match these values. Consumer drivers later resolve those phandles through common clock, reset-controller, or genpd APIs.

## State and Persistence Behavior

The file owns no memory, locks, hardware registers, or persistent storage. Its state is the ABI value assigned to each macro. Those values persist in compiled DTBs and out-of-tree device trees, so renumbering or deleting an existing define is a compatibility break even though no runtime state is stored here. Actual enable counts, reset assertion state, and GDSC power state are maintained by the clock/reset/power-domain drivers and hardware registers, not by this header.

## Dependencies and Integration Points

Direct source dependencies are intentionally minimal: the header has only SPDX/copyright comments, an include guard, macro definitions, and `#endif`. It is integrated by textual inclusion rather than linking. Local integration evidence: clock-controller driver references: `sources/distributed-fs/ceph-client/drivers/clk/qcom/gpucc-sm6125.c`.

The semantic dependency is the matching provider implementation and its descriptor arrays. `qcom,sm6125-gpucc.h` IDs must stay aligned with driver tables for GPU PLL/RCG, GMU, CX/GX, hub, memory NoC, XO/sleep, SMMU vote, reset, and GDSC IDs. DTS consumers depend on these exact constants for properties such as `clocks`, `resets`, `power-domains`, and named clock inputs.

## Risks and Edge Cases

The main risk is ABI drift: inserting new IDs in the middle, reusing a removed value, or moving a reset/GDSC ID to a different number can silently bind a DTS consumer to the wrong hardware clock or power domain. It does not export reset IDs in this clock header; reset bindings are either absent for this controller or live in a paired reset binding header/driver table. Power-domain/GDSC IDs are exported as `GPU_CX_GDSC`=0 through `GPU_GX_GDSC`=1. Shared names such as PLLs, XO/sleep sources, bus clocks, and GDSCs are easy to copy between SoCs, but the numeric ordering must follow this specific provider, not a visually similar controller. Because the file is pure macros, the compiler provides little semantic checking beyond duplicate definitions and include-guard correctness.

## Test Signals

Useful validation includes building the relevant `drivers/clk/qcom` object with this header, compiling DTBs that include `qcom,sm6125-gpucc.h`, and running `dtbs_check`/binding-schema checks for the affected SoC. Runtime smoke tests are provider probe success without missing clock/reset IDs, absence of `-ENOENT`/`-EINVAL` from clock lookups, expected entries under common-clock debugfs, and successful bring-up of consumers in the exported domain set: GPU PLL/RCG, GMU, CX/GX, hub, memory NoC, XO/sleep, SMMU vote, reset, and GDSC IDs. For edits, diff the numeric table against the matching driver arrays and boot at least one DTS consumer when local hardware or emulation coverage exists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sm6125-gpucc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sm6350-camcc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sm6350-camcc.h

## Purpose

`sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sm6350-camcc.h` defines the public device-tree numeric IDs for the Qualcomm camera clock-controller binding associated with `qcom,sm6350-camcc.h` / `sm6350`. The source was read completely for this report (109 lines). It is not executable kernel code; it is a stable binding contract included by DTS files and by the matching `drivers/clk/qcom` provider so that phandle clock, reset, and power-domain specifiers use the same indexes.

## Important APIs, Types, and Functions

There are no C functions, structs, or runtime APIs. The exported API is a set of preprocessor constants guarded by `_DT_BINDINGS_CLK_QCOM_CAMCC_SM6350_H`. This header defines 89 clock IDs, 0 reset IDs, and 6 power-domain/GDSC IDs, for 95 numeric binding macros total.

Clock ID range: `CAMCC_PLL2_OUT_EARLY`=0 through `CAMCC_SYS_TMR_CLK`=88. Representative clocks: `CAMCC_PLL2_OUT_EARLY`, `CAMCC_PLL0`, `CAMCC_PLL0_OUT_EVEN`, `CAMCC_PLL1`, `CAMCC_PLL1_OUT_EVEN`, `CAMCC_PLL2`, ... `CAMCC_MCLK3_CLK_SRC`, `CAMCC_MCLK4_CLK`, `CAMCC_MCLK4_CLK_SRC`, `CAMCC_SLOW_AHB_CLK_SRC`, `CAMCC_SOC_AHB_CLK`, `CAMCC_SYS_TMR_CLK`.

Reset ID range: none. Representative resets: none.

Power-domain/GDSC range: `BPS_GDSC`=0 through `TITAN_TOP_GDSC`=5. Representative domains: `BPS_GDSC`, `IPE_0_GDSC`, `IFE_0_GDSC`, `IFE_1_GDSC`, `IFE_2_GDSC`, `TITAN_TOP_GDSC`.

Macro inventory begins with:
- `CAMCC_PLL2_OUT_EARLY` = 0 (clock, line 11)
- `CAMCC_PLL0` = 1 (clock, line 12)
- `CAMCC_PLL0_OUT_EVEN` = 2 (clock, line 13)
- `CAMCC_PLL1` = 3 (clock, line 14)
- `CAMCC_PLL1_OUT_EVEN` = 4 (clock, line 15)
- `CAMCC_PLL2` = 5 (clock, line 16)
- `CAMCC_PLL2_OUT_MAIN` = 6 (clock, line 17)
- `CAMCC_PLL3` = 7 (clock, line 18)
- `CAMCC_BPS_AHB_CLK` = 8 (clock, line 19)
- `CAMCC_BPS_AREG_CLK` = 9 (clock, line 20)
- ... 85 additional numeric binding macros continue in the same contiguous namespace sections.

## Control Flow

This header has no branches, calls, or runtime control flow. The effective flow is build-time and probe-time: DTS sources include the constants, the device-tree compiler stores the resulting integers in clock/reset/power-domain specifier cells, and the Qualcomm clock-controller driver exposes provider arrays whose indexes must match these values. Consumer drivers later resolve those phandles through common clock, reset-controller, or genpd APIs.

## State and Persistence Behavior

The file owns no memory, locks, hardware registers, or persistent storage. Its state is the ABI value assigned to each macro. Those values persist in compiled DTBs and out-of-tree device trees, so renumbering or deleting an existing define is a compatibility break even though no runtime state is stored here. Actual enable counts, reset assertion state, and GDSC power state are maintained by the clock/reset/power-domain drivers and hardware registers, not by this header.

## Dependencies and Integration Points

Direct source dependencies are intentionally minimal: the header has only SPDX/copyright comments, an include guard, macro definitions, and `#endif`. It is integrated by textual inclusion rather than linking. Local integration evidence: clock-controller driver references: `sources/distributed-fs/ceph-client/drivers/clk/qcom/camcc-sm6350.c`; device-tree references: `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/sm6350.dtsi`.

The semantic dependency is the matching provider implementation and its descriptor arrays. `qcom,sm6350-camcc.h` IDs must stay aligned with driver tables for camera PLLs, MCLKs, CSI/CSIPHY timers, IFE/TFE/SFE/BPS/IPE/JPEG/CPAS fabric clocks, resets, and camera GDSCs. DTS consumers depend on these exact constants for properties such as `clocks`, `resets`, `power-domains`, and named clock inputs.

## Risks and Edge Cases

The main risk is ABI drift: inserting new IDs in the middle, reusing a removed value, or moving a reset/GDSC ID to a different number can silently bind a DTS consumer to the wrong hardware clock or power domain. It does not export reset IDs in this clock header; reset bindings are either absent for this controller or live in a paired reset binding header/driver table. Power-domain/GDSC IDs are exported as `BPS_GDSC`=0 through `TITAN_TOP_GDSC`=5. Shared names such as PLLs, XO/sleep sources, bus clocks, and GDSCs are easy to copy between SoCs, but the numeric ordering must follow this specific provider, not a visually similar controller. Because the file is pure macros, the compiler provides little semantic checking beyond duplicate definitions and include-guard correctness.

## Test Signals

Useful validation includes building the relevant `drivers/clk/qcom` object with this header, compiling DTBs that include `qcom,sm6350-camcc.h`, and running `dtbs_check`/binding-schema checks for the affected SoC. Runtime smoke tests are provider probe success without missing clock/reset IDs, absence of `-ENOENT`/`-EINVAL` from clock lookups, expected entries under common-clock debugfs, and successful bring-up of consumers in the exported domain set: camera PLLs, MCLKs, CSI/CSIPHY timers, IFE/TFE/SFE/BPS/IPE/JPEG/CPAS fabric clocks, resets, and camera GDSCs. For edits, diff the numeric table against the matching driver arrays and boot at least one DTS consumer when local hardware or emulation coverage exists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sm6350-camcc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sm6350-videocc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sm6350-videocc.h

## Purpose

`sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sm6350-videocc.h` defines the public device-tree numeric IDs for the Qualcomm video clock-controller binding associated with `qcom,sm6350-videocc.h` / `sm6350`. The source was read completely for this report (27 lines). It is not executable kernel code; it is a stable binding contract included by DTS files and by the matching `drivers/clk/qcom` provider so that phandle clock, reset, and power-domain specifiers use the same indexes.

## Important APIs, Types, and Functions

There are no C functions, structs, or runtime APIs. The exported API is a set of preprocessor constants guarded by `_DT_BINDINGS_CLK_QCOM_VIDEO_CC_SM6350_H`. This header defines 11 clock IDs, 0 reset IDs, and 2 power-domain/GDSC IDs, for 13 numeric binding macros total.

Clock ID range: `VIDEO_PLL0`=0 through `VIDEO_CC_VENUS_AHB_CLK`=10. Representative clocks: `VIDEO_PLL0`, `VIDEO_PLL0_OUT_EVEN`, `VIDEO_CC_IRIS_AHB_CLK`, `VIDEO_CC_IRIS_CLK_SRC`, `VIDEO_CC_MVS0_AXI_CLK`, `VIDEO_CC_MVS0_CORE_CLK`, `VIDEO_CC_MVSC_CORE_CLK`, `VIDEO_CC_MVSC_CTL_AXI_CLK`, `VIDEO_CC_SLEEP_CLK`, `VIDEO_CC_SLEEP_CLK_SRC`, `VIDEO_CC_VENUS_AHB_CLK`.

Reset ID range: none. Representative resets: none.

Power-domain/GDSC range: `MVSC_GDSC`=0 through `MVS0_GDSC`=1. Representative domains: `MVSC_GDSC`, `MVS0_GDSC`.

Macro inventory begins with:
- `VIDEO_PLL0` = 0 (clock, line 11)
- `VIDEO_PLL0_OUT_EVEN` = 1 (clock, line 12)
- `VIDEO_CC_IRIS_AHB_CLK` = 2 (clock, line 13)
- `VIDEO_CC_IRIS_CLK_SRC` = 3 (clock, line 14)
- `VIDEO_CC_MVS0_AXI_CLK` = 4 (clock, line 15)
- `VIDEO_CC_MVS0_CORE_CLK` = 5 (clock, line 16)
- `VIDEO_CC_MVSC_CORE_CLK` = 6 (clock, line 17)
- `VIDEO_CC_MVSC_CTL_AXI_CLK` = 7 (clock, line 18)
- `VIDEO_CC_SLEEP_CLK` = 8 (clock, line 19)
- `VIDEO_CC_SLEEP_CLK_SRC` = 9 (clock, line 20)
- ... 3 additional numeric binding macros continue in the same contiguous namespace sections.

## Control Flow

This header has no branches, calls, or runtime control flow. The effective flow is build-time and probe-time: DTS sources include the constants, the device-tree compiler stores the resulting integers in clock/reset/power-domain specifier cells, and the Qualcomm clock-controller driver exposes provider arrays whose indexes must match these values. Consumer drivers later resolve those phandles through common clock, reset-controller, or genpd APIs.

## State and Persistence Behavior

The file owns no memory, locks, hardware registers, or persistent storage. Its state is the ABI value assigned to each macro. Those values persist in compiled DTBs and out-of-tree device trees, so renumbering or deleting an existing define is a compatibility break even though no runtime state is stored here. Actual enable counts, reset assertion state, and GDSC power state are maintained by the clock/reset/power-domain drivers and hardware registers, not by this header.

## Dependencies and Integration Points

Direct source dependencies are intentionally minimal: the header has only SPDX/copyright comments, an include guard, macro definitions, and `#endif`. It is integrated by textual inclusion rather than linking. Local integration evidence: clock-controller driver references: `sources/distributed-fs/ceph-client/drivers/clk/qcom/videocc-sm6350.c`.

The semantic dependency is the matching provider implementation and its descriptor arrays. `qcom,sm6350-videocc.h` IDs must stay aligned with driver tables for video codec MVS/MVS0/MVS1, AHB, AXI, sleep/XO, reset, and GDSC IDs. DTS consumers depend on these exact constants for properties such as `clocks`, `resets`, `power-domains`, and named clock inputs.

## Risks and Edge Cases

The main risk is ABI drift: inserting new IDs in the middle, reusing a removed value, or moving a reset/GDSC ID to a different number can silently bind a DTS consumer to the wrong hardware clock or power domain. It does not export reset IDs in this clock header; reset bindings are either absent for this controller or live in a paired reset binding header/driver table. Power-domain/GDSC IDs are exported as `MVSC_GDSC`=0 through `MVS0_GDSC`=1. Shared names such as PLLs, XO/sleep sources, bus clocks, and GDSCs are easy to copy between SoCs, but the numeric ordering must follow this specific provider, not a visually similar controller. Because the file is pure macros, the compiler provides little semantic checking beyond duplicate definitions and include-guard correctness.

## Test Signals

Useful validation includes building the relevant `drivers/clk/qcom` object with this header, compiling DTBs that include `qcom,sm6350-videocc.h`, and running `dtbs_check`/binding-schema checks for the affected SoC. Runtime smoke tests are provider probe success without missing clock/reset IDs, absence of `-ENOENT`/`-EINVAL` from clock lookups, expected entries under common-clock debugfs, and successful bring-up of consumers in the exported domain set: video codec MVS/MVS0/MVS1, AHB, AXI, sleep/XO, reset, and GDSC IDs. For edits, diff the numeric table against the matching driver arrays and boot at least one DTS consumer when local hardware or emulation coverage exists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sm6350-videocc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sm6375-dispcc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sm6375-dispcc.h

## Purpose

`sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sm6375-dispcc.h` defines the public device-tree numeric IDs for the Qualcomm display clock-controller binding associated with `qcom,sm6375-dispcc.h` / `sm6375`. The source was read completely for this report (42 lines). It is not executable kernel code; it is a stable binding contract included by DTS files and by the matching `drivers/clk/qcom` provider so that phandle clock, reset, and power-domain specifiers use the same indexes.

## Important APIs, Types, and Functions

There are no C functions, structs, or runtime APIs. The exported API is a set of preprocessor constants guarded by `_DT_BINDINGS_CLK_QCOM_DISP_CC_SM6375_H`. This header defines 23 clock IDs, 2 reset IDs, and 1 power-domain/GDSC ID, for 26 numeric binding macros total.

Clock ID range: `DISP_CC_PLL0`=0 through `DISP_CC_XO_CLK`=22. Representative clocks: `DISP_CC_PLL0`, `DISP_CC_MDSS_AHB_CLK`, `DISP_CC_MDSS_AHB_CLK_SRC`, `DISP_CC_MDSS_BYTE0_CLK`, `DISP_CC_MDSS_BYTE0_CLK_SRC`, `DISP_CC_MDSS_BYTE0_DIV_CLK_SRC`, ... `DISP_CC_MDSS_RSCC_AHB_CLK`, `DISP_CC_MDSS_RSCC_VSYNC_CLK`, `DISP_CC_MDSS_VSYNC_CLK`, `DISP_CC_MDSS_VSYNC_CLK_SRC`, `DISP_CC_SLEEP_CLK`, `DISP_CC_XO_CLK`.

Reset ID range: `DISP_CC_MDSS_CORE_BCR`=0 through `DISP_CC_MDSS_RSCC_BCR`=1. Representative resets: `DISP_CC_MDSS_CORE_BCR`, `DISP_CC_MDSS_RSCC_BCR`.

Power-domain/GDSC range: `MDSS_GDSC`=0 through `MDSS_GDSC`=0. Representative domains: `MDSS_GDSC`.

Macro inventory begins with:
- `DISP_CC_PLL0` = 0 (clock, line 11)
- `DISP_CC_MDSS_AHB_CLK` = 1 (clock, line 12)
- `DISP_CC_MDSS_AHB_CLK_SRC` = 2 (clock, line 13)
- `DISP_CC_MDSS_BYTE0_CLK` = 3 (clock, line 14)
- `DISP_CC_MDSS_BYTE0_CLK_SRC` = 4 (clock, line 15)
- `DISP_CC_MDSS_BYTE0_DIV_CLK_SRC` = 5 (clock, line 16)
- `DISP_CC_MDSS_BYTE0_INTF_CLK` = 6 (clock, line 17)
- `DISP_CC_MDSS_ESC0_CLK` = 7 (clock, line 18)
- `DISP_CC_MDSS_ESC0_CLK_SRC` = 8 (clock, line 19)
- `DISP_CC_MDSS_MDP_CLK` = 9 (clock, line 20)
- ... 16 additional numeric binding macros continue in the same contiguous namespace sections.

## Control Flow

This header has no branches, calls, or runtime control flow. The effective flow is build-time and probe-time: DTS sources include the constants, the device-tree compiler stores the resulting integers in clock/reset/power-domain specifier cells, and the Qualcomm clock-controller driver exposes provider arrays whose indexes must match these values. Consumer drivers later resolve those phandles through common clock, reset-controller, or genpd APIs.

## State and Persistence Behavior

The file owns no memory, locks, hardware registers, or persistent storage. Its state is the ABI value assigned to each macro. Those values persist in compiled DTBs and out-of-tree device trees, so renumbering or deleting an existing define is a compatibility break even though no runtime state is stored here. Actual enable counts, reset assertion state, and GDSC power state are maintained by the clock/reset/power-domain drivers and hardware registers, not by this header.

## Dependencies and Integration Points

Direct source dependencies are intentionally minimal: the header has only SPDX/copyright comments, an include guard, macro definitions, and `#endif`. It is integrated by textual inclusion rather than linking. Local integration evidence: clock-controller driver references: `sources/distributed-fs/ceph-client/drivers/clk/qcom/dispcc-sm6375.c`.

The semantic dependency is the matching provider implementation and its descriptor arrays. `qcom,sm6375-dispcc.h` IDs must stay aligned with driver tables for MDSS AHB/AXI, MDP, DSI byte/escape/pixel, DisplayPort link/pixel/aux, vsync, resets, and display GDSCs. DTS consumers depend on these exact constants for properties such as `clocks`, `resets`, `power-domains`, and named clock inputs.

## Risks and Edge Cases

The main risk is ABI drift: inserting new IDs in the middle, reusing a removed value, or moving a reset/GDSC ID to a different number can silently bind a DTS consumer to the wrong hardware clock or power domain. It also exports reset IDs (`DISP_CC_MDSS_CORE_BCR`=0 through `DISP_CC_MDSS_RSCC_BCR`=1). Power-domain/GDSC IDs are exported as `MDSS_GDSC`=0 through `MDSS_GDSC`=0. Shared names such as PLLs, XO/sleep sources, bus clocks, and GDSCs are easy to copy between SoCs, but the numeric ordering must follow this specific provider, not a visually similar controller. Because the file is pure macros, the compiler provides little semantic checking beyond duplicate definitions and include-guard correctness.

## Test Signals

Useful validation includes building the relevant `drivers/clk/qcom` object with this header, compiling DTBs that include `qcom,sm6375-dispcc.h`, and running `dtbs_check`/binding-schema checks for the affected SoC. Runtime smoke tests are provider probe success without missing clock/reset IDs, absence of `-ENOENT`/`-EINVAL` from clock lookups, expected entries under common-clock debugfs, and successful bring-up of consumers in the exported domain set: MDSS AHB/AXI, MDP, DSI byte/escape/pixel, DisplayPort link/pixel/aux, vsync, resets, and display GDSCs. For edits, diff the numeric table against the matching driver arrays and boot at least one DTS consumer when local hardware or emulation coverage exists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sm6375-dispcc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sm6375-gcc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sm6375-gcc.h

## Purpose

`sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sm6375-gcc.h` defines the public device-tree numeric IDs for the Qualcomm global clock-controller binding associated with `qcom,sm6375-gcc.h` / `sm6375`. The source was read completely for this report (234 lines). It is not executable kernel code; it is a stable binding contract included by DTS files and by the matching `drivers/clk/qcom` provider so that phandle clock, reset, and power-domain specifiers use the same indexes.

## Important APIs, Types, and Functions

There are no C functions, structs, or runtime APIs. The exported API is a set of preprocessor constants guarded by `_DT_BINDINGS_CLK_QCOM_GCC_SM6375_H`. This header defines 188 clock IDs, 21 reset IDs, and 9 power-domain/GDSC IDs, for 218 numeric binding macros total.

Clock ID range: `GPLL0`=0 through `GCC_VIDEO_XO_CLK`=187. Representative clocks: `GPLL0`, `GPLL0_OUT_EVEN`, `GPLL0_OUT_ODD`, `GPLL1`, `GPLL10`, `GPLL11`, ... `GCC_VIDEO_AXI0_CLK`, `GCC_VIDEO_THROTTLE_CORE_CLK`, `GCC_VIDEO_VCODEC0_SYS_CLK`, `GCC_VIDEO_VENUS_CLK_SRC`, `GCC_VIDEO_VENUS_CTL_CLK`, `GCC_VIDEO_XO_CLK`.

Reset ID range: `GCC_CAMSS_OPE_BCR`=0 through `GCC_USB3_PHY_PRIM_SP0_BCR`=20. Representative resets: `GCC_CAMSS_OPE_BCR`, `GCC_CAMSS_TFE_BCR`, `GCC_CAMSS_TOP_BCR`, `GCC_GPU_BCR`, `GCC_MMSS_BCR`, `GCC_PDM_BCR`, ... `GCC_USB_PHY_CFG_AHB2PHY_BCR`, `GCC_VCODEC0_BCR`, `GCC_VENUS_BCR`, `GCC_VIDEO_INTERFACE_BCR`, `GCC_USB3_DP_PHY_PRIM_BCR`, `GCC_USB3_PHY_PRIM_SP0_BCR`.

Power-domain/GDSC range: `USB30_PRIM_GDSC`=0 through `HLOS1_VOTE_TURING_MMU_TBU1_GDSC`=8. Representative domains: `USB30_PRIM_GDSC`, `UFS_PHY_GDSC`, `CAMSS_TOP_GDSC`, `VENUS_GDSC`, `VCODEC0_GDSC`, `HLOS1_VOTE_MM_SNOC_MMU_TBU_NRT_GDSC`, `HLOS1_VOTE_MM_SNOC_MMU_TBU_RT_GDSC`, `HLOS1_VOTE_TURING_MMU_TBU0_GDSC`, `HLOS1_VOTE_TURING_MMU_TBU1_GDSC`.

Macro inventory begins with:
- `GPLL0` = 0 (clock, line 11)
- `GPLL0_OUT_EVEN` = 1 (clock, line 12)
- `GPLL0_OUT_ODD` = 2 (clock, line 13)
- `GPLL1` = 3 (clock, line 14)
- `GPLL10` = 4 (clock, line 15)
- `GPLL11` = 5 (clock, line 16)
- `GPLL3` = 6 (clock, line 17)
- `GPLL3_OUT_EVEN` = 7 (clock, line 18)
- `GPLL4` = 8 (clock, line 19)
- `GPLL5` = 9 (clock, line 20)
- ... 208 additional numeric binding macros continue in the same contiguous namespace sections.

## Control Flow

This header has no branches, calls, or runtime control flow. The effective flow is build-time and probe-time: DTS sources include the constants, the device-tree compiler stores the resulting integers in clock/reset/power-domain specifier cells, and the Qualcomm clock-controller driver exposes provider arrays whose indexes must match these values. Consumer drivers later resolve those phandles through common clock, reset-controller, or genpd APIs.

## State and Persistence Behavior

The file owns no memory, locks, hardware registers, or persistent storage. Its state is the ABI value assigned to each macro. Those values persist in compiled DTBs and out-of-tree device trees, so renumbering or deleting an existing define is a compatibility break even though no runtime state is stored here. Actual enable counts, reset assertion state, and GDSC power state are maintained by the clock/reset/power-domain drivers and hardware registers, not by this header.

## Dependencies and Integration Points

Direct source dependencies are intentionally minimal: the header has only SPDX/copyright comments, an include guard, macro definitions, and `#endif`. It is integrated by textual inclusion rather than linking. Local integration evidence: clock-controller driver references: `sources/distributed-fs/ceph-client/drivers/clk/qcom/gcc-sm6375.c`; device-tree references: `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/sm6375.dtsi`.

The semantic dependency is the matching provider implementation and its descriptor arrays. `qcom,sm6375-gcc.h` IDs must stay aligned with driver tables for global PLLs plus bus, QUP, USB, PCIe, UFS, SDCC, camera/display/video/gpu vote, reset, and GDSC IDs. DTS consumers depend on these exact constants for properties such as `clocks`, `resets`, `power-domains`, and named clock inputs.

## Risks and Edge Cases

The main risk is ABI drift: inserting new IDs in the middle, reusing a removed value, or moving a reset/GDSC ID to a different number can silently bind a DTS consumer to the wrong hardware clock or power domain. It also exports reset IDs (`GCC_CAMSS_OPE_BCR`=0 through `GCC_USB3_PHY_PRIM_SP0_BCR`=20). Power-domain/GDSC IDs are exported as `USB30_PRIM_GDSC`=0 through `HLOS1_VOTE_TURING_MMU_TBU1_GDSC`=8. Shared names such as PLLs, XO/sleep sources, bus clocks, and GDSCs are easy to copy between SoCs, but the numeric ordering must follow this specific provider, not a visually similar controller. Because the file is pure macros, the compiler provides little semantic checking beyond duplicate definitions and include-guard correctness.

## Test Signals

Useful validation includes building the relevant `drivers/clk/qcom` object with this header, compiling DTBs that include `qcom,sm6375-gcc.h`, and running `dtbs_check`/binding-schema checks for the affected SoC. Runtime smoke tests are provider probe success without missing clock/reset IDs, absence of `-ENOENT`/`-EINVAL` from clock lookups, expected entries under common-clock debugfs, and successful bring-up of consumers in the exported domain set: global PLLs plus bus, QUP, USB, PCIe, UFS, SDCC, camera/display/video/gpu vote, reset, and GDSC IDs. For edits, diff the numeric table against the matching driver arrays and boot at least one DTS consumer when local hardware or emulation coverage exists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sm6375-gcc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sm6375-gpucc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sm6375-gpucc.h

## Purpose

`sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sm6375-gpucc.h` defines the public device-tree numeric IDs for the Qualcomm GPU clock-controller binding associated with `qcom,sm6375-gpucc.h` / `sm6375`. The source was read completely for this report (36 lines). It is not executable kernel code; it is a stable binding contract included by DTS files and by the matching `drivers/clk/qcom` provider so that phandle clock, reset, and power-domain specifiers use the same indexes.

## Important APIs, Types, and Functions

There are no C functions, structs, or runtime APIs. The exported API is a set of preprocessor constants guarded by `_DT_BINDINGS_CLK_QCOM_GPU_CC_BLAIR_H`. This header defines 15 clock IDs, 3 reset IDs, and 2 power-domain/GDSC IDs, for 20 numeric binding macros total.

Clock ID range: `GPU_CC_PLL0`=0 through `GPU_CC_SLEEP_CLK`=14. Representative clocks: `GPU_CC_PLL0`, `GPU_CC_PLL1`, `GPU_CC_AHB_CLK`, `GPU_CC_CX_GFX3D_CLK`, `GPU_CC_CX_GFX3D_SLV_CLK`, `GPU_CC_CX_GMU_CLK`, ... `GPU_CC_GMU_CLK_SRC`, `GPU_CC_GX_CXO_CLK`, `GPU_CC_GX_GFX3D_CLK`, `GPU_CC_GX_GFX3D_CLK_SRC`, `GPU_CC_GX_GMU_CLK`, `GPU_CC_SLEEP_CLK`.

Reset ID range: `GPU_GX_BCR`=0 through `GPU_GX_ACD_MISC_BCR`=2. Representative resets: `GPU_GX_BCR`, `GPU_ACD_BCR`, `GPU_GX_ACD_MISC_BCR`.

Power-domain/GDSC range: `GPU_CX_GDSC`=0 through `GPU_GX_GDSC`=1. Representative domains: `GPU_CX_GDSC`, `GPU_GX_GDSC`.

Macro inventory begins with:
- `GPU_CC_PLL0` = 0 (clock, line 11)
- `GPU_CC_PLL1` = 1 (clock, line 12)
- `GPU_CC_AHB_CLK` = 2 (clock, line 13)
- `GPU_CC_CX_GFX3D_CLK` = 3 (clock, line 14)
- `GPU_CC_CX_GFX3D_SLV_CLK` = 4 (clock, line 15)
- `GPU_CC_CX_GMU_CLK` = 5 (clock, line 16)
- `GPU_CC_CX_SNOC_DVM_CLK` = 6 (clock, line 17)
- `GPU_CC_CXO_AON_CLK` = 7 (clock, line 18)
- `GPU_CC_CXO_CLK` = 8 (clock, line 19)
- `GPU_CC_GMU_CLK_SRC` = 9 (clock, line 20)
- ... 10 additional numeric binding macros continue in the same contiguous namespace sections.

## Control Flow

This header has no branches, calls, or runtime control flow. The effective flow is build-time and probe-time: DTS sources include the constants, the device-tree compiler stores the resulting integers in clock/reset/power-domain specifier cells, and the Qualcomm clock-controller driver exposes provider arrays whose indexes must match these values. Consumer drivers later resolve those phandles through common clock, reset-controller, or genpd APIs.

## State and Persistence Behavior

The file owns no memory, locks, hardware registers, or persistent storage. Its state is the ABI value assigned to each macro. Those values persist in compiled DTBs and out-of-tree device trees, so renumbering or deleting an existing define is a compatibility break even though no runtime state is stored here. Actual enable counts, reset assertion state, and GDSC power state are maintained by the clock/reset/power-domain drivers and hardware registers, not by this header.

## Dependencies and Integration Points

Direct source dependencies are intentionally minimal: the header has only SPDX/copyright comments, an include guard, macro definitions, and `#endif`. It is integrated by textual inclusion rather than linking. Local integration evidence: clock-controller driver references: `sources/distributed-fs/ceph-client/drivers/clk/qcom/gpucc-sm6375.c`; device-tree references: `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/sm6375.dtsi`.

The semantic dependency is the matching provider implementation and its descriptor arrays. `qcom,sm6375-gpucc.h` IDs must stay aligned with driver tables for GPU PLL/RCG, GMU, CX/GX, hub, memory NoC, XO/sleep, SMMU vote, reset, and GDSC IDs. DTS consumers depend on these exact constants for properties such as `clocks`, `resets`, `power-domains`, and named clock inputs.

## Risks and Edge Cases

The main risk is ABI drift: inserting new IDs in the middle, reusing a removed value, or moving a reset/GDSC ID to a different number can silently bind a DTS consumer to the wrong hardware clock or power domain. It also exports reset IDs (`GPU_GX_BCR`=0 through `GPU_GX_ACD_MISC_BCR`=2). Power-domain/GDSC IDs are exported as `GPU_CX_GDSC`=0 through `GPU_GX_GDSC`=1. Shared names such as PLLs, XO/sleep sources, bus clocks, and GDSCs are easy to copy between SoCs, but the numeric ordering must follow this specific provider, not a visually similar controller. Because the file is pure macros, the compiler provides little semantic checking beyond duplicate definitions and include-guard correctness.

## Test Signals

Useful validation includes building the relevant `drivers/clk/qcom` object with this header, compiling DTBs that include `qcom,sm6375-gpucc.h`, and running `dtbs_check`/binding-schema checks for the affected SoC. Runtime smoke tests are provider probe success without missing clock/reset IDs, absence of `-ENOENT`/`-EINVAL` from clock lookups, expected entries under common-clock debugfs, and successful bring-up of consumers in the exported domain set: GPU PLL/RCG, GMU, CX/GX, hub, memory NoC, XO/sleep, SMMU vote, reset, and GDSC IDs. For edits, diff the numeric table against the matching driver arrays and boot at least one DTS consumer when local hardware or emulation coverage exists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sm6375-gpucc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sm7150-camcc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sm7150-camcc.h

## Purpose

`sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sm7150-camcc.h` defines the public device-tree numeric IDs for the Qualcomm camera clock-controller binding associated with `qcom,sm7150-camcc.h` / `sm7150`. The source was read completely for this report (113 lines). It is not executable kernel code; it is a stable binding contract included by DTS files and by the matching `drivers/clk/qcom` provider so that phandle clock, reset, and power-domain specifiers use the same indexes.

## Important APIs, Types, and Functions

There are no C functions, structs, or runtime APIs. The exported API is a set of preprocessor constants guarded by `_DT_BINDINGS_CLK_QCOM_CAMCC_SM7150_H`. This header defines 91 clock IDs, 0 reset IDs, and 6 power-domain/GDSC IDs, for 97 numeric binding macros total.

Clock ID range: `CAMCC_PLL0_OUT_EVEN`=0 through `CAMCC_XO_CLK_SRC`=90. Representative clocks: `CAMCC_PLL0_OUT_EVEN`, `CAMCC_PLL0_OUT_ODD`, `CAMCC_PLL1_OUT_EVEN`, `CAMCC_PLL2_OUT_EARLY`, `CAMCC_PLL3_OUT_EVEN`, `CAMCC_PLL4_OUT_EVEN`, ... `CAMCC_MCLK3_CLK`, `CAMCC_MCLK3_CLK_SRC`, `CAMCC_SLEEP_CLK`, `CAMCC_SLEEP_CLK_SRC`, `CAMCC_SLOW_AHB_CLK_SRC`, `CAMCC_XO_CLK_SRC`.

Reset ID range: none. Representative resets: none.

Power-domain/GDSC range: `BPS_GDSC`=0 through `TITAN_TOP_GDSC`=5. Representative domains: `BPS_GDSC`, `IFE_0_GDSC`, `IFE_1_GDSC`, `IPE_0_GDSC`, `IPE_1_GDSC`, `TITAN_TOP_GDSC`.

Macro inventory begins with:
- `CAMCC_PLL0_OUT_EVEN` = 0 (clock, line 11)
- `CAMCC_PLL0_OUT_ODD` = 1 (clock, line 12)
- `CAMCC_PLL1_OUT_EVEN` = 2 (clock, line 13)
- `CAMCC_PLL2_OUT_EARLY` = 3 (clock, line 14)
- `CAMCC_PLL3_OUT_EVEN` = 4 (clock, line 15)
- `CAMCC_PLL4_OUT_EVEN` = 5 (clock, line 16)
- `CAMCC_PLL0` = 6 (clock, line 19)
- `CAMCC_PLL1` = 7 (clock, line 20)
- `CAMCC_PLL2` = 8 (clock, line 21)
- `CAMCC_PLL2_OUT_AUX` = 9 (clock, line 22)
- ... 87 additional numeric binding macros continue in the same contiguous namespace sections.

## Control Flow

This header has no branches, calls, or runtime control flow. The effective flow is build-time and probe-time: DTS sources include the constants, the device-tree compiler stores the resulting integers in clock/reset/power-domain specifier cells, and the Qualcomm clock-controller driver exposes provider arrays whose indexes must match these values. Consumer drivers later resolve those phandles through common clock, reset-controller, or genpd APIs.

## State and Persistence Behavior

The file owns no memory, locks, hardware registers, or persistent storage. Its state is the ABI value assigned to each macro. Those values persist in compiled DTBs and out-of-tree device trees, so renumbering or deleting an existing define is a compatibility break even though no runtime state is stored here. Actual enable counts, reset assertion state, and GDSC power state are maintained by the clock/reset/power-domain drivers and hardware registers, not by this header.

## Dependencies and Integration Points

Direct source dependencies are intentionally minimal: the header has only SPDX/copyright comments, an include guard, macro definitions, and `#endif`. It is integrated by textual inclusion rather than linking. Local integration evidence: clock-controller driver references: `sources/distributed-fs/ceph-client/drivers/clk/qcom/camcc-sm7150.c`.

The semantic dependency is the matching provider implementation and its descriptor arrays. `qcom,sm7150-camcc.h` IDs must stay aligned with driver tables for camera PLLs, MCLKs, CSI/CSIPHY timers, IFE/TFE/SFE/BPS/IPE/JPEG/CPAS fabric clocks, resets, and camera GDSCs. DTS consumers depend on these exact constants for properties such as `clocks`, `resets`, `power-domains`, and named clock inputs.

## Risks and Edge Cases

The main risk is ABI drift: inserting new IDs in the middle, reusing a removed value, or moving a reset/GDSC ID to a different number can silently bind a DTS consumer to the wrong hardware clock or power domain. It does not export reset IDs in this clock header; reset bindings are either absent for this controller or live in a paired reset binding header/driver table. Power-domain/GDSC IDs are exported as `BPS_GDSC`=0 through `TITAN_TOP_GDSC`=5. Shared names such as PLLs, XO/sleep sources, bus clocks, and GDSCs are easy to copy between SoCs, but the numeric ordering must follow this specific provider, not a visually similar controller. Because the file is pure macros, the compiler provides little semantic checking beyond duplicate definitions and include-guard correctness.

## Test Signals

Useful validation includes building the relevant `drivers/clk/qcom` object with this header, compiling DTBs that include `qcom,sm7150-camcc.h`, and running `dtbs_check`/binding-schema checks for the affected SoC. Runtime smoke tests are provider probe success without missing clock/reset IDs, absence of `-ENOENT`/`-EINVAL` from clock lookups, expected entries under common-clock debugfs, and successful bring-up of consumers in the exported domain set: camera PLLs, MCLKs, CSI/CSIPHY timers, IFE/TFE/SFE/BPS/IPE/JPEG/CPAS fabric clocks, resets, and camera GDSCs. For edits, diff the numeric table against the matching driver arrays and boot at least one DTS consumer when local hardware or emulation coverage exists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sm7150-camcc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sm7150-dispcc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sm7150-dispcc.h

## Purpose

`sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sm7150-dispcc.h` defines the public device-tree numeric IDs for the Qualcomm display clock-controller binding associated with `qcom,sm7150-dispcc.h` / `sm7150`. The source was read completely for this report (62 lines). It is not executable kernel code; it is a stable binding contract included by DTS files and by the matching `drivers/clk/qcom` provider so that phandle clock, reset, and power-domain specifiers use the same indexes.

## Important APIs, Types, and Functions

There are no C functions, structs, or runtime APIs. The exported API is a set of preprocessor constants guarded by `_DT_BINDINGS_CLK_QCOM_DISPCC_SM7150_H`. This header defines 43 clock IDs, 1 reset ID, and 1 power-domain/GDSC ID, for 45 numeric binding macros total.

Clock ID range: `DISPCC_PLL0`=0 through `DISPCC_SLEEP_CLK_SRC`=42. Representative clocks: `DISPCC_PLL0`, `DISPCC_MDSS_AHB_CLK`, `DISPCC_MDSS_AHB_CLK_SRC`, `DISPCC_MDSS_BYTE0_CLK`, `DISPCC_MDSS_BYTE0_CLK_SRC`, `DISPCC_MDSS_BYTE0_DIV_CLK_SRC`, ... `DISPCC_MDSS_RSCC_VSYNC_CLK`, `DISPCC_MDSS_VSYNC_CLK`, `DISPCC_MDSS_VSYNC_CLK_SRC`, `DISPCC_XO_CLK_SRC`, `DISPCC_SLEEP_CLK`, `DISPCC_SLEEP_CLK_SRC`.

Reset ID range: `DISPCC_MDSS_CORE_BCR`=0 through `DISPCC_MDSS_CORE_BCR`=0. Representative resets: `DISPCC_MDSS_CORE_BCR`.

Power-domain/GDSC range: `MDSS_GDSC`=0 through `MDSS_GDSC`=0. Representative domains: `MDSS_GDSC`.

Macro inventory begins with:
- `DISPCC_PLL0` = 0 (clock, line 12)
- `DISPCC_MDSS_AHB_CLK` = 1 (clock, line 13)
- `DISPCC_MDSS_AHB_CLK_SRC` = 2 (clock, line 14)
- `DISPCC_MDSS_BYTE0_CLK` = 3 (clock, line 15)
- `DISPCC_MDSS_BYTE0_CLK_SRC` = 4 (clock, line 16)
- `DISPCC_MDSS_BYTE0_DIV_CLK_SRC` = 5 (clock, line 17)
- `DISPCC_MDSS_BYTE0_INTF_CLK` = 6 (clock, line 18)
- `DISPCC_MDSS_BYTE1_CLK` = 7 (clock, line 19)
- `DISPCC_MDSS_BYTE1_CLK_SRC` = 8 (clock, line 20)
- `DISPCC_MDSS_BYTE1_DIV_CLK_SRC` = 9 (clock, line 21)
- ... 35 additional numeric binding macros continue in the same contiguous namespace sections.

## Control Flow

This header has no branches, calls, or runtime control flow. The effective flow is build-time and probe-time: DTS sources include the constants, the device-tree compiler stores the resulting integers in clock/reset/power-domain specifier cells, and the Qualcomm clock-controller driver exposes provider arrays whose indexes must match these values. Consumer drivers later resolve those phandles through common clock, reset-controller, or genpd APIs.

## State and Persistence Behavior

The file owns no memory, locks, hardware registers, or persistent storage. Its state is the ABI value assigned to each macro. Those values persist in compiled DTBs and out-of-tree device trees, so renumbering or deleting an existing define is a compatibility break even though no runtime state is stored here. Actual enable counts, reset assertion state, and GDSC power state are maintained by the clock/reset/power-domain drivers and hardware registers, not by this header.

## Dependencies and Integration Points

Direct source dependencies are intentionally minimal: the header has only SPDX/copyright comments, an include guard, macro definitions, and `#endif`. It is integrated by textual inclusion rather than linking. Local integration evidence: clock-controller driver references: `sources/distributed-fs/ceph-client/drivers/clk/qcom/dispcc-sm7150.c`.

The semantic dependency is the matching provider implementation and its descriptor arrays. `qcom,sm7150-dispcc.h` IDs must stay aligned with driver tables for MDSS AHB/AXI, MDP, DSI byte/escape/pixel, DisplayPort link/pixel/aux, vsync, resets, and display GDSCs. DTS consumers depend on these exact constants for properties such as `clocks`, `resets`, `power-domains`, and named clock inputs.

## Risks and Edge Cases

The main risk is ABI drift: inserting new IDs in the middle, reusing a removed value, or moving a reset/GDSC ID to a different number can silently bind a DTS consumer to the wrong hardware clock or power domain. It also exports reset IDs (`DISPCC_MDSS_CORE_BCR`=0 through `DISPCC_MDSS_CORE_BCR`=0). Power-domain/GDSC IDs are exported as `MDSS_GDSC`=0 through `MDSS_GDSC`=0. Shared names such as PLLs, XO/sleep sources, bus clocks, and GDSCs are easy to copy between SoCs, but the numeric ordering must follow this specific provider, not a visually similar controller. Because the file is pure macros, the compiler provides little semantic checking beyond duplicate definitions and include-guard correctness.

## Test Signals

Useful validation includes building the relevant `drivers/clk/qcom` object with this header, compiling DTBs that include `qcom,sm7150-dispcc.h`, and running `dtbs_check`/binding-schema checks for the affected SoC. Runtime smoke tests are provider probe success without missing clock/reset IDs, absence of `-ENOENT`/`-EINVAL` from clock lookups, expected entries under common-clock debugfs, and successful bring-up of consumers in the exported domain set: MDSS AHB/AXI, MDP, DSI byte/escape/pixel, DisplayPort link/pixel/aux, vsync, resets, and display GDSCs. For edits, diff the numeric table against the matching driver arrays and boot at least one DTS consumer when local hardware or emulation coverage exists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sm7150-dispcc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sm7150-gcc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sm7150-gcc.h

## Purpose

`sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sm7150-gcc.h` defines the public device-tree numeric IDs for the Qualcomm global clock-controller binding associated with `qcom,sm7150-gcc.h` / `sm7150`. The source was read completely for this report (186 lines). It is not executable kernel code; it is a stable binding contract included by DTS files and by the matching `drivers/clk/qcom` provider so that phandle clock, reset, and power-domain specifiers use the same indexes.

## Important APIs, Types, and Functions

There are no C functions, structs, or runtime APIs. The exported API is a set of preprocessor constants guarded by `_DT_BINDINGS_CLK_QCOM_GCC_SM7150_H`. This header defines 148 clock IDs, 11 reset IDs, and 10 power-domain/GDSC IDs, for 169 numeric binding macros total.

Clock ID range: `GCC_GPLL0_MAIN_DIV_CDIV`=0 through `GCC_VSENSOR_CLK_SRC`=147. Representative clocks: `GCC_GPLL0_MAIN_DIV_CDIV`, `GPLL0`, `GPLL0_OUT_EVEN`, `GPLL6`, `GPLL7`, `GCC_AGGRE_NOC_PCIE_TBU_CLK`, ... `GCC_VDDMX_VS_CLK`, `GCC_VIDEO_AXI_CLK`, `GCC_VS_CTRL_AHB_CLK`, `GCC_VS_CTRL_CLK`, `GCC_VS_CTRL_CLK_SRC`, `GCC_VSENSOR_CLK_SRC`.

Reset ID range: `GCC_PCIE_0_BCR`=0 through `GCC_VIDEO_AXI_CLK_BCR`=10. Representative resets: `GCC_PCIE_0_BCR`, `GCC_PCIE_PHY_BCR`, `GCC_PCIE_PHY_COM_BCR`, `GCC_UFS_PHY_BCR`, `GCC_USB30_PRIM_BCR`, `GCC_USB3_DP_PHY_PRIM_BCR`, `GCC_USB3_DP_PHY_SEC_BCR`, `GCC_USB3_PHY_PRIM_BCR`, `GCC_USB3_PHY_SEC_BCR`, `GCC_QUSB2PHY_PRIM_BCR`, `GCC_VIDEO_AXI_CLK_BCR`.

Power-domain/GDSC range: `PCIE_0_GDSC`=0 through `HLOS1_VOTE_MMNOC_MMU_TBU_SF_GDSC`=9. Representative domains: `PCIE_0_GDSC`, `UFS_PHY_GDSC`, `USB30_PRIM_GDSC`, `HLOS1_VOTE_AGGRE_NOC_MMU_AUDIO_TBU_GDSC`, `HLOS1_VOTE_AGGRE_NOC_MMU_PCIE_TBU_GDSC`, `HLOS1_VOTE_AGGRE_NOC_MMU_TBU1_GDSC`, `HLOS1_VOTE_AGGRE_NOC_MMU_TBU2_GDSC`, `HLOS1_VOTE_MMNOC_MMU_TBU_HF0_GDSC`, `HLOS1_VOTE_MMNOC_MMU_TBU_HF1_GDSC`, `HLOS1_VOTE_MMNOC_MMU_TBU_SF_GDSC`.

Macro inventory begins with:
- `GCC_GPLL0_MAIN_DIV_CDIV` = 0 (clock, line 12)
- `GPLL0` = 1 (clock, line 13)
- `GPLL0_OUT_EVEN` = 2 (clock, line 14)
- `GPLL6` = 3 (clock, line 15)
- `GPLL7` = 4 (clock, line 16)
- `GCC_AGGRE_NOC_PCIE_TBU_CLK` = 5 (clock, line 17)
- `GCC_AGGRE_UFS_PHY_AXI_CLK` = 6 (clock, line 18)
- `GCC_AGGRE_UFS_PHY_AXI_HW_CTL_CLK` = 7 (clock, line 19)
- `GCC_AGGRE_USB3_PRIM_AXI_CLK` = 8 (clock, line 20)
- `GCC_APC_VS_CLK` = 9 (clock, line 21)
- ... 159 additional numeric binding macros continue in the same contiguous namespace sections.

## Control Flow

This header has no branches, calls, or runtime control flow. The effective flow is build-time and probe-time: DTS sources include the constants, the device-tree compiler stores the resulting integers in clock/reset/power-domain specifier cells, and the Qualcomm clock-controller driver exposes provider arrays whose indexes must match these values. Consumer drivers later resolve those phandles through common clock, reset-controller, or genpd APIs.

## State and Persistence Behavior

The file owns no memory, locks, hardware registers, or persistent storage. Its state is the ABI value assigned to each macro. Those values persist in compiled DTBs and out-of-tree device trees, so renumbering or deleting an existing define is a compatibility break even though no runtime state is stored here. Actual enable counts, reset assertion state, and GDSC power state are maintained by the clock/reset/power-domain drivers and hardware registers, not by this header.

## Dependencies and Integration Points

Direct source dependencies are intentionally minimal: the header has only SPDX/copyright comments, an include guard, macro definitions, and `#endif`. It is integrated by textual inclusion rather than linking. Local integration evidence: clock-controller driver references: `sources/distributed-fs/ceph-client/drivers/clk/qcom/gcc-sm7150.c`.

The semantic dependency is the matching provider implementation and its descriptor arrays. `qcom,sm7150-gcc.h` IDs must stay aligned with driver tables for global PLLs plus bus, QUP, USB, PCIe, UFS, SDCC, camera/display/video/gpu vote, reset, and GDSC IDs. DTS consumers depend on these exact constants for properties such as `clocks`, `resets`, `power-domains`, and named clock inputs.

## Risks and Edge Cases

The main risk is ABI drift: inserting new IDs in the middle, reusing a removed value, or moving a reset/GDSC ID to a different number can silently bind a DTS consumer to the wrong hardware clock or power domain. It also exports reset IDs (`GCC_PCIE_0_BCR`=0 through `GCC_VIDEO_AXI_CLK_BCR`=10). Power-domain/GDSC IDs are exported as `PCIE_0_GDSC`=0 through `HLOS1_VOTE_MMNOC_MMU_TBU_SF_GDSC`=9. Shared names such as PLLs, XO/sleep sources, bus clocks, and GDSCs are easy to copy between SoCs, but the numeric ordering must follow this specific provider, not a visually similar controller. Because the file is pure macros, the compiler provides little semantic checking beyond duplicate definitions and include-guard correctness.

## Test Signals

Useful validation includes building the relevant `drivers/clk/qcom` object with this header, compiling DTBs that include `qcom,sm7150-gcc.h`, and running `dtbs_check`/binding-schema checks for the affected SoC. Runtime smoke tests are provider probe success without missing clock/reset IDs, absence of `-ENOENT`/`-EINVAL` from clock lookups, expected entries under common-clock debugfs, and successful bring-up of consumers in the exported domain set: global PLLs plus bus, QUP, USB, PCIe, UFS, SDCC, camera/display/video/gpu vote, reset, and GDSC IDs. For edits, diff the numeric table against the matching driver arrays and boot at least one DTS consumer when local hardware or emulation coverage exists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sm7150-gcc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sm7150-videocc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sm7150-videocc.h

## Purpose

`sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sm7150-videocc.h` defines the public device-tree numeric IDs for the Qualcomm video clock-controller binding associated with `qcom,sm7150-videocc.h` / `sm7150`. The source was read completely for this report (28 lines). It is not executable kernel code; it is a stable binding contract included by DTS files and by the matching `drivers/clk/qcom` provider so that phandle clock, reset, and power-domain specifiers use the same indexes.

## Important APIs, Types, and Functions

There are no C functions, structs, or runtime APIs. The exported API is a set of preprocessor constants guarded by `_DT_BINDINGS_CLK_QCOM_VIDEOCC_SM7150_H`. This header defines 12 clock IDs, 0 reset IDs, and 3 power-domain/GDSC IDs, for 15 numeric binding macros total.

Clock ID range: `VIDEOCC_PLL0`=0 through `VIDEOCC_XO_CLK_SRC`=11. Representative clocks: `VIDEOCC_PLL0`, `VIDEOCC_IRIS_AHB_CLK`, `VIDEOCC_IRIS_CLK_SRC`, `VIDEOCC_MVS0_AXI_CLK`, `VIDEOCC_MVS0_CORE_CLK`, `VIDEOCC_MVS1_AXI_CLK`, `VIDEOCC_MVS1_CORE_CLK`, `VIDEOCC_MVSC_CORE_CLK`, `VIDEOCC_MVSC_CTL_AXI_CLK`, `VIDEOCC_VENUS_AHB_CLK`, `VIDEOCC_XO_CLK`, `VIDEOCC_XO_CLK_SRC`.

Reset ID range: none. Representative resets: none.

Power-domain/GDSC range: `VENUS_GDSC`=0 through `VCODEC1_GDSC`=2. Representative domains: `VENUS_GDSC`, `VCODEC0_GDSC`, `VCODEC1_GDSC`.

Macro inventory begins with:
- `VIDEOCC_PLL0` = 0 (clock, line 10)
- `VIDEOCC_IRIS_AHB_CLK` = 1 (clock, line 11)
- `VIDEOCC_IRIS_CLK_SRC` = 2 (clock, line 12)
- `VIDEOCC_MVS0_AXI_CLK` = 3 (clock, line 13)
- `VIDEOCC_MVS0_CORE_CLK` = 4 (clock, line 14)
- `VIDEOCC_MVS1_AXI_CLK` = 5 (clock, line 15)
- `VIDEOCC_MVS1_CORE_CLK` = 6 (clock, line 16)
- `VIDEOCC_MVSC_CORE_CLK` = 7 (clock, line 17)
- `VIDEOCC_MVSC_CTL_AXI_CLK` = 8 (clock, line 18)
- `VIDEOCC_VENUS_AHB_CLK` = 9 (clock, line 19)
- ... 5 additional numeric binding macros continue in the same contiguous namespace sections.

## Control Flow

This header has no branches, calls, or runtime control flow. The effective flow is build-time and probe-time: DTS sources include the constants, the device-tree compiler stores the resulting integers in clock/reset/power-domain specifier cells, and the Qualcomm clock-controller driver exposes provider arrays whose indexes must match these values. Consumer drivers later resolve those phandles through common clock, reset-controller, or genpd APIs.

## State and Persistence Behavior

The file owns no memory, locks, hardware registers, or persistent storage. Its state is the ABI value assigned to each macro. Those values persist in compiled DTBs and out-of-tree device trees, so renumbering or deleting an existing define is a compatibility break even though no runtime state is stored here. Actual enable counts, reset assertion state, and GDSC power state are maintained by the clock/reset/power-domain drivers and hardware registers, not by this header.

## Dependencies and Integration Points

Direct source dependencies are intentionally minimal: the header has only SPDX/copyright comments, an include guard, macro definitions, and `#endif`. It is integrated by textual inclusion rather than linking. Local integration evidence: clock-controller driver references: `sources/distributed-fs/ceph-client/drivers/clk/qcom/videocc-sm7150.c`.

The semantic dependency is the matching provider implementation and its descriptor arrays. `qcom,sm7150-videocc.h` IDs must stay aligned with driver tables for video codec MVS/MVS0/MVS1, AHB, AXI, sleep/XO, reset, and GDSC IDs. DTS consumers depend on these exact constants for properties such as `clocks`, `resets`, `power-domains`, and named clock inputs.

## Risks and Edge Cases

The main risk is ABI drift: inserting new IDs in the middle, reusing a removed value, or moving a reset/GDSC ID to a different number can silently bind a DTS consumer to the wrong hardware clock or power domain. It does not export reset IDs in this clock header; reset bindings are either absent for this controller or live in a paired reset binding header/driver table. Power-domain/GDSC IDs are exported as `VENUS_GDSC`=0 through `VCODEC1_GDSC`=2. Shared names such as PLLs, XO/sleep sources, bus clocks, and GDSCs are easy to copy between SoCs, but the numeric ordering must follow this specific provider, not a visually similar controller. Because the file is pure macros, the compiler provides little semantic checking beyond duplicate definitions and include-guard correctness.

## Test Signals

Useful validation includes building the relevant `drivers/clk/qcom` object with this header, compiling DTBs that include `qcom,sm7150-videocc.h`, and running `dtbs_check`/binding-schema checks for the affected SoC. Runtime smoke tests are provider probe success without missing clock/reset IDs, absence of `-ENOENT`/`-EINVAL` from clock lookups, expected entries under common-clock debugfs, and successful bring-up of consumers in the exported domain set: video codec MVS/MVS0/MVS1, AHB, AXI, sleep/XO, reset, and GDSC IDs. For edits, diff the numeric table against the matching driver arrays and boot at least one DTS consumer when local hardware or emulation coverage exists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sm7150-videocc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sm8150-camcc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sm8150-camcc.h

## Purpose

`sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sm8150-camcc.h` defines the public device-tree numeric IDs for the Qualcomm camera clock-controller binding associated with `qcom,sm8150-camcc.h` / `sm8150`. The source was read completely for this report (135 lines). It is not executable kernel code; it is a stable binding contract included by DTS files and by the matching `drivers/clk/qcom` provider so that phandle clock, reset, and power-domain specifiers use the same indexes.

## Important APIs, Types, and Functions

There are no C functions, structs, or runtime APIs. The exported API is a set of preprocessor constants guarded by `_DT_BINDINGS_CLK_QCOM_CAM_CC_SM8150_H`. This header defines 92 clock IDs, 22 reset IDs, and 6 power-domain/GDSC IDs, for 120 numeric binding macros total.

Clock ID range: `CAM_CC_PLL0`=0 through `CAM_CC_SLOW_AHB_CLK_SRC`=91. Representative clocks: `CAM_CC_PLL0`, `CAM_CC_PLL0_OUT_EVEN`, `CAM_CC_PLL0_OUT_ODD`, `CAM_CC_PLL1`, `CAM_CC_PLL1_OUT_EVEN`, `CAM_CC_PLL2`, ... `CAM_CC_MCLK1_CLK_SRC`, `CAM_CC_MCLK2_CLK`, `CAM_CC_MCLK2_CLK_SRC`, `CAM_CC_MCLK3_CLK`, `CAM_CC_MCLK3_CLK_SRC`, `CAM_CC_SLOW_AHB_CLK_SRC`.

Reset ID range: `CAM_CC_BPS_BCR`=0 through `CAM_CC_MCLK3_BCR`=21. Representative resets: `CAM_CC_BPS_BCR`, `CAM_CC_CAMNOC_BCR`, `CAM_CC_CCI_BCR`, `CAM_CC_CPAS_BCR`, `CAM_CC_CSI0PHY_BCR`, `CAM_CC_CSI1PHY_BCR`, ... `CAM_CC_JPEG_BCR`, `CAM_CC_LRME_BCR`, `CAM_CC_MCLK0_BCR`, `CAM_CC_MCLK1_BCR`, `CAM_CC_MCLK2_BCR`, `CAM_CC_MCLK3_BCR`.

Power-domain/GDSC range: `TITAN_TOP_GDSC`=0 through `IPE_1_GDSC`=5. Representative domains: `TITAN_TOP_GDSC`, `BPS_GDSC`, `IFE_0_GDSC`, `IFE_1_GDSC`, `IPE_0_GDSC`, `IPE_1_GDSC`.

Macro inventory begins with:
- `CAM_CC_PLL0` = 0 (clock, line 10)
- `CAM_CC_PLL0_OUT_EVEN` = 1 (clock, line 11)
- `CAM_CC_PLL0_OUT_ODD` = 2 (clock, line 12)
- `CAM_CC_PLL1` = 3 (clock, line 13)
- `CAM_CC_PLL1_OUT_EVEN` = 4 (clock, line 14)
- `CAM_CC_PLL2` = 5 (clock, line 15)
- `CAM_CC_PLL2_OUT_MAIN` = 6 (clock, line 16)
- `CAM_CC_PLL3` = 7 (clock, line 17)
- `CAM_CC_PLL3_OUT_EVEN` = 8 (clock, line 18)
- `CAM_CC_PLL4` = 9 (clock, line 19)
- ... 110 additional numeric binding macros continue in the same contiguous namespace sections.

## Control Flow

This header has no branches, calls, or runtime control flow. The effective flow is build-time and probe-time: DTS sources include the constants, the device-tree compiler stores the resulting integers in clock/reset/power-domain specifier cells, and the Qualcomm clock-controller driver exposes provider arrays whose indexes must match these values. Consumer drivers later resolve those phandles through common clock, reset-controller, or genpd APIs.

## State and Persistence Behavior

The file owns no memory, locks, hardware registers, or persistent storage. Its state is the ABI value assigned to each macro. Those values persist in compiled DTBs and out-of-tree device trees, so renumbering or deleting an existing define is a compatibility break even though no runtime state is stored here. Actual enable counts, reset assertion state, and GDSC power state are maintained by the clock/reset/power-domain drivers and hardware registers, not by this header.

## Dependencies and Integration Points

Direct source dependencies are intentionally minimal: the header has only SPDX/copyright comments, an include guard, macro definitions, and `#endif`. It is integrated by textual inclusion rather than linking. Local integration evidence: clock-controller driver references: `sources/distributed-fs/ceph-client/drivers/clk/qcom/camcc-sm8150.c`; device-tree references: `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/sm8150.dtsi`.

The semantic dependency is the matching provider implementation and its descriptor arrays. `qcom,sm8150-camcc.h` IDs must stay aligned with driver tables for camera PLLs, MCLKs, CSI/CSIPHY timers, IFE/TFE/SFE/BPS/IPE/JPEG/CPAS fabric clocks, resets, and camera GDSCs. DTS consumers depend on these exact constants for properties such as `clocks`, `resets`, `power-domains`, and named clock inputs.

## Risks and Edge Cases

The main risk is ABI drift: inserting new IDs in the middle, reusing a removed value, or moving a reset/GDSC ID to a different number can silently bind a DTS consumer to the wrong hardware clock or power domain. It also exports reset IDs (`CAM_CC_BPS_BCR`=0 through `CAM_CC_MCLK3_BCR`=21). Power-domain/GDSC IDs are exported as `TITAN_TOP_GDSC`=0 through `IPE_1_GDSC`=5. Shared names such as PLLs, XO/sleep sources, bus clocks, and GDSCs are easy to copy between SoCs, but the numeric ordering must follow this specific provider, not a visually similar controller. Because the file is pure macros, the compiler provides little semantic checking beyond duplicate definitions and include-guard correctness.

## Test Signals

Useful validation includes building the relevant `drivers/clk/qcom` object with this header, compiling DTBs that include `qcom,sm8150-camcc.h`, and running `dtbs_check`/binding-schema checks for the affected SoC. Runtime smoke tests are provider probe success without missing clock/reset IDs, absence of `-ENOENT`/`-EINVAL` from clock lookups, expected entries under common-clock debugfs, and successful bring-up of consumers in the exported domain set: camera PLLs, MCLKs, CSI/CSIPHY timers, IFE/TFE/SFE/BPS/IPE/JPEG/CPAS fabric clocks, resets, and camera GDSCs. For edits, diff the numeric table against the matching driver arrays and boot at least one DTS consumer when local hardware or emulation coverage exists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sm8150-camcc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sm8250-lpass-aoncc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sm8250-lpass-aoncc.h

## Purpose

`sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sm8250-lpass-aoncc.h` defines the public device-tree numeric IDs for the Qualcomm LPASS/audio clock-controller binding associated with `qcom,sm8250-lpass-aoncc.h` / `sm8250`. The source was read completely for this report (11 lines). It is not executable kernel code; it is a stable binding contract included by DTS files and by the matching `drivers/clk/qcom` provider so that phandle clock, reset, and power-domain specifiers use the same indexes.

## Important APIs, Types, and Functions

There are no C functions, structs, or runtime APIs. The exported API is a set of preprocessor constants guarded by `_DT_BINDINGS_CLK_LPASS_AONCC_SM8250_H`. This header defines 3 clock IDs, 0 reset IDs, and 0 power-domain/GDSC IDs, for 3 numeric binding macros total.

Clock ID range: `LPASS_CDC_VA_MCLK`=0 through `LPASS_CDC_TX_MCLK`=2. Representative clocks: `LPASS_CDC_VA_MCLK`, `LPASS_CDC_TX_NPL`, `LPASS_CDC_TX_MCLK`.

Reset ID range: none. Representative resets: none.

Power-domain/GDSC range: none. Representative domains: none.

Macro inventory begins with:
- `LPASS_CDC_VA_MCLK` = 0 (clock, line 7)
- `LPASS_CDC_TX_NPL` = 1 (clock, line 8)
- `LPASS_CDC_TX_MCLK` = 2 (clock, line 9)

## Control Flow

This header has no branches, calls, or runtime control flow. The effective flow is build-time and probe-time: DTS sources include the constants, the device-tree compiler stores the resulting integers in clock/reset/power-domain specifier cells, and the Qualcomm clock-controller driver exposes provider arrays whose indexes must match these values. Consumer drivers later resolve those phandles through common clock, reset-controller, or genpd APIs.

## State and Persistence Behavior

The file owns no memory, locks, hardware registers, or persistent storage. Its state is the ABI value assigned to each macro. Those values persist in compiled DTBs and out-of-tree device trees, so renumbering or deleting an existing define is a compatibility break even though no runtime state is stored here. Actual enable counts, reset assertion state, and GDSC power state are maintained by the clock/reset/power-domain drivers and hardware registers, not by this header.

## Dependencies and Integration Points

Direct source dependencies are intentionally minimal: the header has only SPDX/copyright comments, an include guard, macro definitions, and `#endif`. It is integrated by textual inclusion rather than linking. Local integration evidence: clock-controller driver references: `sources/distributed-fs/ceph-client/drivers/clk/qcom/lpass-gfm-sm8250.c`.

The semantic dependency is the matching provider implementation and its descriptor arrays. `qcom,sm8250-lpass-aoncc.h` IDs must stay aligned with driver tables for audio and always-on LPASS clock IDs used by the Qualcomm GFM/LPASS clock driver. DTS consumers depend on these exact constants for properties such as `clocks`, `resets`, `power-domains`, and named clock inputs.

## Risks and Edge Cases

The main risk is ABI drift: inserting new IDs in the middle, reusing a removed value, or moving a reset/GDSC ID to a different number can silently bind a DTS consumer to the wrong hardware clock or power domain. It does not export reset IDs in this clock header; reset bindings are either absent for this controller or live in a paired reset binding header/driver table. It does not export GDSC or power-domain IDs. Shared names such as PLLs, XO/sleep sources, bus clocks, and GDSCs are easy to copy between SoCs, but the numeric ordering must follow this specific provider, not a visually similar controller. Because the file is pure macros, the compiler provides little semantic checking beyond duplicate definitions and include-guard correctness.

## Test Signals

Useful validation includes building the relevant `drivers/clk/qcom` object with this header, compiling DTBs that include `qcom,sm8250-lpass-aoncc.h`, and running `dtbs_check`/binding-schema checks for the affected SoC. Runtime smoke tests are provider probe success without missing clock/reset IDs, absence of `-ENOENT`/`-EINVAL` from clock lookups, expected entries under common-clock debugfs, and successful bring-up of consumers in the exported domain set: audio and always-on LPASS clock IDs used by the Qualcomm GFM/LPASS clock driver. For edits, diff the numeric table against the matching driver arrays and boot at least one DTS consumer when local hardware or emulation coverage exists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sm8250-lpass-aoncc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sm8250-lpass-audiocc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sm8250-lpass-audiocc.h

## Purpose

`sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sm8250-lpass-audiocc.h` defines the public device-tree numeric IDs for the Qualcomm LPASS/audio clock-controller binding associated with `qcom,sm8250-lpass-audiocc.h` / `sm8250`. The source was read completely for this report (13 lines). It is not executable kernel code; it is a stable binding contract included by DTS files and by the matching `drivers/clk/qcom` provider so that phandle clock, reset, and power-domain specifiers use the same indexes.

## Important APIs, Types, and Functions

There are no C functions, structs, or runtime APIs. The exported API is a set of preprocessor constants guarded by `_DT_BINDINGS_CLK_LPASS_AUDIOCC_SM8250_H`. This header defines 5 clock IDs, 0 reset IDs, and 0 power-domain/GDSC IDs, for 5 numeric binding macros total.

Clock ID range: `LPASS_CDC_WSA_NPL`=0 through `LPASS_CDC_RX_MCLK_MCLK2`=4. Representative clocks: `LPASS_CDC_WSA_NPL`, `LPASS_CDC_WSA_MCLK`, `LPASS_CDC_RX_MCLK`, `LPASS_CDC_RX_NPL`, `LPASS_CDC_RX_MCLK_MCLK2`.

Reset ID range: none. Representative resets: none.

Power-domain/GDSC range: none. Representative domains: none.

Macro inventory begins with:
- `LPASS_CDC_WSA_NPL` = 0 (clock, line 7)
- `LPASS_CDC_WSA_MCLK` = 1 (clock, line 8)
- `LPASS_CDC_RX_MCLK` = 2 (clock, line 9)
- `LPASS_CDC_RX_NPL` = 3 (clock, line 10)
- `LPASS_CDC_RX_MCLK_MCLK2` = 4 (clock, line 11)

## Control Flow

This header has no branches, calls, or runtime control flow. The effective flow is build-time and probe-time: DTS sources include the constants, the device-tree compiler stores the resulting integers in clock/reset/power-domain specifier cells, and the Qualcomm clock-controller driver exposes provider arrays whose indexes must match these values. Consumer drivers later resolve those phandles through common clock, reset-controller, or genpd APIs.

## State and Persistence Behavior

The file owns no memory, locks, hardware registers, or persistent storage. Its state is the ABI value assigned to each macro. Those values persist in compiled DTBs and out-of-tree device trees, so renumbering or deleting an existing define is a compatibility break even though no runtime state is stored here. Actual enable counts, reset assertion state, and GDSC power state are maintained by the clock/reset/power-domain drivers and hardware registers, not by this header.

## Dependencies and Integration Points

Direct source dependencies are intentionally minimal: the header has only SPDX/copyright comments, an include guard, macro definitions, and `#endif`. It is integrated by textual inclusion rather than linking. Local integration evidence: clock-controller driver references: `sources/distributed-fs/ceph-client/drivers/clk/qcom/lpass-gfm-sm8250.c`.

The semantic dependency is the matching provider implementation and its descriptor arrays. `qcom,sm8250-lpass-audiocc.h` IDs must stay aligned with driver tables for audio and always-on LPASS clock IDs used by the Qualcomm GFM/LPASS clock driver. DTS consumers depend on these exact constants for properties such as `clocks`, `resets`, `power-domains`, and named clock inputs.

## Risks and Edge Cases

The main risk is ABI drift: inserting new IDs in the middle, reusing a removed value, or moving a reset/GDSC ID to a different number can silently bind a DTS consumer to the wrong hardware clock or power domain. It does not export reset IDs in this clock header; reset bindings are either absent for this controller or live in a paired reset binding header/driver table. It does not export GDSC or power-domain IDs. Shared names such as PLLs, XO/sleep sources, bus clocks, and GDSCs are easy to copy between SoCs, but the numeric ordering must follow this specific provider, not a visually similar controller. Because the file is pure macros, the compiler provides little semantic checking beyond duplicate definitions and include-guard correctness.

## Test Signals

Useful validation includes building the relevant `drivers/clk/qcom` object with this header, compiling DTBs that include `qcom,sm8250-lpass-audiocc.h`, and running `dtbs_check`/binding-schema checks for the affected SoC. Runtime smoke tests are provider probe success without missing clock/reset IDs, absence of `-ENOENT`/`-EINVAL` from clock lookups, expected entries under common-clock debugfs, and successful bring-up of consumers in the exported domain set: audio and always-on LPASS clock IDs used by the Qualcomm GFM/LPASS clock driver. For edits, diff the numeric table against the matching driver arrays and boot at least one DTS consumer when local hardware or emulation coverage exists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sm8250-lpass-audiocc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sm8350-videocc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sm8350-videocc.h

## Purpose

`sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sm8350-videocc.h` defines the public device-tree numeric IDs for the Qualcomm video clock-controller binding associated with `qcom,sm8350-videocc.h` / `sm8350`. The source was read completely for this report (35 lines). It is not executable kernel code; it is a stable binding contract included by DTS files and by the matching `drivers/clk/qcom` provider so that phandle clock, reset, and power-domain specifiers use the same indexes.

## Important APIs, Types, and Functions

There are no C functions, structs, or runtime APIs. The exported API is a set of preprocessor constants guarded by `_DT_BINDINGS_CLK_QCOM_VIDEO_CC_SM8350_H`. This header defines 17 clock IDs, 0 reset IDs, and 4 power-domain/GDSC IDs, for 21 numeric binding macros total.

Clock ID range: `VIDEO_CC_AHB_CLK_SRC`=0 through `VIDEO_PLL1`=16. Representative clocks: `VIDEO_CC_AHB_CLK_SRC`, `VIDEO_CC_MVS0_CLK`, `VIDEO_CC_MVS0_CLK_SRC`, `VIDEO_CC_MVS0_DIV_CLK_SRC`, `VIDEO_CC_MVS0C_CLK`, `VIDEO_CC_MVS0C_DIV2_DIV_CLK_SRC`, ... `VIDEO_CC_MVS1C_DIV2_DIV_CLK_SRC`, `VIDEO_CC_SLEEP_CLK`, `VIDEO_CC_SLEEP_CLK_SRC`, `VIDEO_CC_XO_CLK_SRC`, `VIDEO_PLL0`, `VIDEO_PLL1`.

Reset ID range: none. Representative resets: none.

Power-domain/GDSC range: `MVS0C_GDSC`=0 through `MVS1_GDSC`=3. Representative domains: `MVS0C_GDSC`, `MVS1C_GDSC`, `MVS0_GDSC`, `MVS1_GDSC`.

Macro inventory begins with:
- `VIDEO_CC_AHB_CLK_SRC` = 0 (clock, line 11)
- `VIDEO_CC_MVS0_CLK` = 1 (clock, line 12)
- `VIDEO_CC_MVS0_CLK_SRC` = 2 (clock, line 13)
- `VIDEO_CC_MVS0_DIV_CLK_SRC` = 3 (clock, line 14)
- `VIDEO_CC_MVS0C_CLK` = 4 (clock, line 15)
- `VIDEO_CC_MVS0C_DIV2_DIV_CLK_SRC` = 5 (clock, line 16)
- `VIDEO_CC_MVS1_CLK` = 6 (clock, line 17)
- `VIDEO_CC_MVS1_CLK_SRC` = 7 (clock, line 18)
- `VIDEO_CC_MVS1_DIV2_CLK` = 8 (clock, line 19)
- `VIDEO_CC_MVS1_DIV_CLK_SRC` = 9 (clock, line 20)
- ... 11 additional numeric binding macros continue in the same contiguous namespace sections.

## Control Flow

This header has no branches, calls, or runtime control flow. The effective flow is build-time and probe-time: DTS sources include the constants, the device-tree compiler stores the resulting integers in clock/reset/power-domain specifier cells, and the Qualcomm clock-controller driver exposes provider arrays whose indexes must match these values. Consumer drivers later resolve those phandles through common clock, reset-controller, or genpd APIs.

## State and Persistence Behavior

The file owns no memory, locks, hardware registers, or persistent storage. Its state is the ABI value assigned to each macro. Those values persist in compiled DTBs and out-of-tree device trees, so renumbering or deleting an existing define is a compatibility break even though no runtime state is stored here. Actual enable counts, reset assertion state, and GDSC power state are maintained by the clock/reset/power-domain drivers and hardware registers, not by this header.

## Dependencies and Integration Points

Direct source dependencies are intentionally minimal: the header has only SPDX/copyright comments, an include guard, macro definitions, and `#endif`. It is integrated by textual inclusion rather than linking. Local integration evidence: clock-controller driver references: `sources/distributed-fs/ceph-client/drivers/clk/qcom/videocc-sm8350.c`.

The semantic dependency is the matching provider implementation and its descriptor arrays. `qcom,sm8350-videocc.h` IDs must stay aligned with driver tables for video codec MVS/MVS0/MVS1, AHB, AXI, sleep/XO, reset, and GDSC IDs. DTS consumers depend on these exact constants for properties such as `clocks`, `resets`, `power-domains`, and named clock inputs.

## Risks and Edge Cases

The main risk is ABI drift: inserting new IDs in the middle, reusing a removed value, or moving a reset/GDSC ID to a different number can silently bind a DTS consumer to the wrong hardware clock or power domain. It does not export reset IDs in this clock header; reset bindings are either absent for this controller or live in a paired reset binding header/driver table. Power-domain/GDSC IDs are exported as `MVS0C_GDSC`=0 through `MVS1_GDSC`=3. Shared names such as PLLs, XO/sleep sources, bus clocks, and GDSCs are easy to copy between SoCs, but the numeric ordering must follow this specific provider, not a visually similar controller. Because the file is pure macros, the compiler provides little semantic checking beyond duplicate definitions and include-guard correctness.

## Test Signals

Useful validation includes building the relevant `drivers/clk/qcom` object with this header, compiling DTBs that include `qcom,sm8350-videocc.h`, and running `dtbs_check`/binding-schema checks for the affected SoC. Runtime smoke tests are provider probe success without missing clock/reset IDs, absence of `-ENOENT`/`-EINVAL` from clock lookups, expected entries under common-clock debugfs, and successful bring-up of consumers in the exported domain set: video codec MVS/MVS0/MVS1, AHB, AXI, sleep/XO, reset, and GDSC IDs. For edits, diff the numeric table against the matching driver arrays and boot at least one DTS consumer when local hardware or emulation coverage exists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sm8350-videocc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sm8450-camcc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sm8450-camcc.h

## Purpose

`sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sm8450-camcc.h` defines the public device-tree numeric IDs for the Qualcomm camera clock-controller binding associated with `qcom,sm8450-camcc.h` / `sm8450`. The source was read completely for this report (159 lines). It is not executable kernel code; it is a stable binding contract included by DTS files and by the matching `drivers/clk/qcom` provider so that phandle clock, reset, and power-domain specifiers use the same indexes.

## Important APIs, Types, and Functions

There are no C functions, structs, or runtime APIs. The exported API is a set of preprocessor constants guarded by `_DT_BINDINGS_CLK_QCOM_CAM_CC_SM8450_H`. This header defines 125 clock IDs, 10 reset IDs, and 9 power-domain/GDSC IDs, for 144 numeric binding macros total.

Clock ID range: `CAM_CC_BPS_AHB_CLK`=0 through `CAM_CC_XO_CLK_SRC`=124. Representative clocks: `CAM_CC_BPS_AHB_CLK`, `CAM_CC_BPS_CLK`, `CAM_CC_BPS_CLK_SRC`, `CAM_CC_BPS_FAST_AHB_CLK`, `CAM_CC_CAMNOC_AXI_CLK`, `CAM_CC_CAMNOC_AXI_CLK_SRC`, ... `CAM_CC_SFE_1_CLK_SRC`, `CAM_CC_SFE_1_FAST_AHB_CLK`, `CAM_CC_SLEEP_CLK`, `CAM_CC_SLEEP_CLK_SRC`, `CAM_CC_SLOW_AHB_CLK_SRC`, `CAM_CC_XO_CLK_SRC`.

Reset ID range: `CAM_CC_BPS_BCR`=0 through `CAM_CC_SFE_1_BCR`=9. Representative resets: `CAM_CC_BPS_BCR`, `CAM_CC_ICP_BCR`, `CAM_CC_IFE_0_BCR`, `CAM_CC_IFE_1_BCR`, `CAM_CC_IFE_2_BCR`, `CAM_CC_IPE_0_BCR`, `CAM_CC_QDSS_DEBUG_BCR`, `CAM_CC_SBI_BCR`, `CAM_CC_SFE_0_BCR`, `CAM_CC_SFE_1_BCR`.

Power-domain/GDSC range: `BPS_GDSC`=0 through `TITAN_TOP_GDSC`=8. Representative domains: `BPS_GDSC`, `IPE_0_GDSC`, `SBI_GDSC`, `IFE_0_GDSC`, `IFE_1_GDSC`, `IFE_2_GDSC`, `SFE_0_GDSC`, `SFE_1_GDSC`, `TITAN_TOP_GDSC`.

Macro inventory begins with:
- `CAM_CC_BPS_AHB_CLK` = 0 (clock, line 10)
- `CAM_CC_BPS_CLK` = 1 (clock, line 11)
- `CAM_CC_BPS_CLK_SRC` = 2 (clock, line 12)
- `CAM_CC_BPS_FAST_AHB_CLK` = 3 (clock, line 13)
- `CAM_CC_CAMNOC_AXI_CLK` = 4 (clock, line 14)
- `CAM_CC_CAMNOC_AXI_CLK_SRC` = 5 (clock, line 15)
- `CAM_CC_CAMNOC_DCD_XO_CLK` = 6 (clock, line 16)
- `CAM_CC_CCI_0_CLK` = 7 (clock, line 17)
- `CAM_CC_CCI_0_CLK_SRC` = 8 (clock, line 18)
- `CAM_CC_CCI_1_CLK` = 9 (clock, line 19)
- ... 134 additional numeric binding macros continue in the same contiguous namespace sections.

## Control Flow

This header has no branches, calls, or runtime control flow. The effective flow is build-time and probe-time: DTS sources include the constants, the device-tree compiler stores the resulting integers in clock/reset/power-domain specifier cells, and the Qualcomm clock-controller driver exposes provider arrays whose indexes must match these values. Consumer drivers later resolve those phandles through common clock, reset-controller, or genpd APIs.

## State and Persistence Behavior

The file owns no memory, locks, hardware registers, or persistent storage. Its state is the ABI value assigned to each macro. Those values persist in compiled DTBs and out-of-tree device trees, so renumbering or deleting an existing define is a compatibility break even though no runtime state is stored here. Actual enable counts, reset assertion state, and GDSC power state are maintained by the clock/reset/power-domain drivers and hardware registers, not by this header.

## Dependencies and Integration Points

Direct source dependencies are intentionally minimal: the header has only SPDX/copyright comments, an include guard, macro definitions, and `#endif`. It is integrated by textual inclusion rather than linking. Local integration evidence: clock-controller driver references: `sources/distributed-fs/ceph-client/drivers/clk/qcom/camcc-sm8450.c`; device-tree references: `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/sm8450.dtsi`.

The semantic dependency is the matching provider implementation and its descriptor arrays. `qcom,sm8450-camcc.h` IDs must stay aligned with driver tables for camera PLLs, MCLKs, CSI/CSIPHY timers, IFE/TFE/SFE/BPS/IPE/JPEG/CPAS fabric clocks, resets, and camera GDSCs. DTS consumers depend on these exact constants for properties such as `clocks`, `resets`, `power-domains`, and named clock inputs.

## Risks and Edge Cases

The main risk is ABI drift: inserting new IDs in the middle, reusing a removed value, or moving a reset/GDSC ID to a different number can silently bind a DTS consumer to the wrong hardware clock or power domain. It also exports reset IDs (`CAM_CC_BPS_BCR`=0 through `CAM_CC_SFE_1_BCR`=9). Power-domain/GDSC IDs are exported as `BPS_GDSC`=0 through `TITAN_TOP_GDSC`=8. Shared names such as PLLs, XO/sleep sources, bus clocks, and GDSCs are easy to copy between SoCs, but the numeric ordering must follow this specific provider, not a visually similar controller. Because the file is pure macros, the compiler provides little semantic checking beyond duplicate definitions and include-guard correctness.

## Test Signals

Useful validation includes building the relevant `drivers/clk/qcom` object with this header, compiling DTBs that include `qcom,sm8450-camcc.h`, and running `dtbs_check`/binding-schema checks for the affected SoC. Runtime smoke tests are provider probe success without missing clock/reset IDs, absence of `-ENOENT`/`-EINVAL` from clock lookups, expected entries under common-clock debugfs, and successful bring-up of consumers in the exported domain set: camera PLLs, MCLKs, CSI/CSIPHY timers, IFE/TFE/SFE/BPS/IPE/JPEG/CPAS fabric clocks, resets, and camera GDSCs. For edits, diff the numeric table against the matching driver arrays and boot at least one DTS consumer when local hardware or emulation coverage exists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sm8450-camcc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sm8450-dispcc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sm8450-dispcc.h

## Purpose

`sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sm8450-dispcc.h` defines the public device-tree numeric IDs for the Qualcomm display clock-controller binding associated with `qcom,sm8450-dispcc.h` / `sm8450`. The source was read completely for this report (103 lines). It is not executable kernel code; it is a stable binding contract included by DTS files and by the matching `drivers/clk/qcom` provider so that phandle clock, reset, and power-domain specifiers use the same indexes.

## Important APIs, Types, and Functions

There are no C functions, structs, or runtime APIs. The exported API is a set of preprocessor constants guarded by `_DT_BINDINGS_CLK_QCOM_DISP_CC_SM8450_H`. This header defines 83 clock IDs, 3 reset IDs, and 2 power-domain/GDSC IDs, for 88 numeric binding macros total.

Clock ID range: `DISP_CC_MDSS_AHB1_CLK`=0 through `DISP_CC_XO_CLK_SRC`=82. Representative clocks: `DISP_CC_MDSS_AHB1_CLK`, `DISP_CC_MDSS_AHB_CLK`, `DISP_CC_MDSS_AHB_CLK_SRC`, `DISP_CC_MDSS_BYTE0_CLK`, `DISP_CC_MDSS_BYTE0_CLK_SRC`, `DISP_CC_MDSS_BYTE0_DIV_CLK_SRC`, ... `DISP_CC_PLL0`, `DISP_CC_PLL1`, `DISP_CC_SLEEP_CLK`, `DISP_CC_SLEEP_CLK_SRC`, `DISP_CC_XO_CLK`, `DISP_CC_XO_CLK_SRC`.

Reset ID range: `DISP_CC_MDSS_CORE_BCR`=0 through `DISP_CC_MDSS_RSCC_BCR`=2. Representative resets: `DISP_CC_MDSS_CORE_BCR`, `DISP_CC_MDSS_CORE_INT2_BCR`, `DISP_CC_MDSS_RSCC_BCR`.

Power-domain/GDSC range: `MDSS_GDSC`=0 through `MDSS_INT2_GDSC`=1. Representative domains: `MDSS_GDSC`, `MDSS_INT2_GDSC`.

Macro inventory begins with:
- `DISP_CC_MDSS_AHB1_CLK` = 0 (clock, line 10)
- `DISP_CC_MDSS_AHB_CLK` = 1 (clock, line 11)
- `DISP_CC_MDSS_AHB_CLK_SRC` = 2 (clock, line 12)
- `DISP_CC_MDSS_BYTE0_CLK` = 3 (clock, line 13)
- `DISP_CC_MDSS_BYTE0_CLK_SRC` = 4 (clock, line 14)
- `DISP_CC_MDSS_BYTE0_DIV_CLK_SRC` = 5 (clock, line 15)
- `DISP_CC_MDSS_BYTE0_INTF_CLK` = 6 (clock, line 16)
- `DISP_CC_MDSS_BYTE1_CLK` = 7 (clock, line 17)
- `DISP_CC_MDSS_BYTE1_CLK_SRC` = 8 (clock, line 18)
- `DISP_CC_MDSS_BYTE1_DIV_CLK_SRC` = 9 (clock, line 19)
- ... 78 additional numeric binding macros continue in the same contiguous namespace sections.

## Control Flow

This header has no branches, calls, or runtime control flow. The effective flow is build-time and probe-time: DTS sources include the constants, the device-tree compiler stores the resulting integers in clock/reset/power-domain specifier cells, and the Qualcomm clock-controller driver exposes provider arrays whose indexes must match these values. Consumer drivers later resolve those phandles through common clock, reset-controller, or genpd APIs.

## State and Persistence Behavior

The file owns no memory, locks, hardware registers, or persistent storage. Its state is the ABI value assigned to each macro. Those values persist in compiled DTBs and out-of-tree device trees, so renumbering or deleting an existing define is a compatibility break even though no runtime state is stored here. Actual enable counts, reset assertion state, and GDSC power state are maintained by the clock/reset/power-domain drivers and hardware registers, not by this header.

## Dependencies and Integration Points

Direct source dependencies are intentionally minimal: the header has only SPDX/copyright comments, an include guard, macro definitions, and `#endif`. It is integrated by textual inclusion rather than linking. Local integration evidence: clock-controller driver references: `sources/distributed-fs/ceph-client/drivers/clk/qcom/dispcc-sm8450.c`; device-tree references: `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/sm8450.dtsi`.

The semantic dependency is the matching provider implementation and its descriptor arrays. `qcom,sm8450-dispcc.h` IDs must stay aligned with driver tables for MDSS AHB/AXI, MDP, DSI byte/escape/pixel, DisplayPort link/pixel/aux, vsync, resets, and display GDSCs. DTS consumers depend on these exact constants for properties such as `clocks`, `resets`, `power-domains`, and named clock inputs.

## Risks and Edge Cases

The main risk is ABI drift: inserting new IDs in the middle, reusing a removed value, or moving a reset/GDSC ID to a different number can silently bind a DTS consumer to the wrong hardware clock or power domain. It also exports reset IDs (`DISP_CC_MDSS_CORE_BCR`=0 through `DISP_CC_MDSS_RSCC_BCR`=2). Power-domain/GDSC IDs are exported as `MDSS_GDSC`=0 through `MDSS_INT2_GDSC`=1. Shared names such as PLLs, XO/sleep sources, bus clocks, and GDSCs are easy to copy between SoCs, but the numeric ordering must follow this specific provider, not a visually similar controller. Because the file is pure macros, the compiler provides little semantic checking beyond duplicate definitions and include-guard correctness.

## Test Signals

Useful validation includes building the relevant `drivers/clk/qcom` object with this header, compiling DTBs that include `qcom,sm8450-dispcc.h`, and running `dtbs_check`/binding-schema checks for the affected SoC. Runtime smoke tests are provider probe success without missing clock/reset IDs, absence of `-ENOENT`/`-EINVAL` from clock lookups, expected entries under common-clock debugfs, and successful bring-up of consumers in the exported domain set: MDSS AHB/AXI, MDP, DSI byte/escape/pixel, DisplayPort link/pixel/aux, vsync, resets, and display GDSCs. For edits, diff the numeric table against the matching driver arrays and boot at least one DTS consumer when local hardware or emulation coverage exists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sm8450-dispcc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sm8450-gpucc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sm8450-gpucc.h

## Purpose

`sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sm8450-gpucc.h` defines the public device-tree numeric IDs for the Qualcomm GPU clock-controller binding associated with `qcom,sm8450-gpucc.h` / `sm8450`. The source was read completely for this report (48 lines). It is not executable kernel code; it is a stable binding contract included by DTS files and by the matching `drivers/clk/qcom` provider so that phandle clock, reset, and power-domain specifiers use the same indexes.

## Important APIs, Types, and Functions

There are no C functions, structs, or runtime APIs. The exported API is a set of preprocessor constants guarded by `_DT_BINDINGS_CLK_QCOM_GPU_CC_SM8450_H`. This header defines 32 clock IDs, 0 reset IDs, and 2 power-domain/GDSC IDs, for 34 numeric binding macros total.

Clock ID range: `GPU_CC_AHB_CLK`=0 through `GPU_CC_XO_DIV_CLK_SRC`=31. Representative clocks: `GPU_CC_AHB_CLK`, `GPU_CC_CRC_AHB_CLK`, `GPU_CC_CX_APB_CLK`, `GPU_CC_CX_FF_CLK`, `GPU_CC_CX_GMU_CLK`, `GPU_CC_CX_SNOC_DVM_CLK`, ... `GPU_CC_MND1X_1_GFX3D_CLK`, `GPU_CC_PLL0`, `GPU_CC_PLL1`, `GPU_CC_SLEEP_CLK`, `GPU_CC_XO_CLK_SRC`, `GPU_CC_XO_DIV_CLK_SRC`.

Reset ID range: none. Representative resets: none.

Power-domain/GDSC range: `GPU_GX_GDSC`=0 through `GPU_CX_GDSC`=1. Representative domains: `GPU_GX_GDSC`, `GPU_CX_GDSC`.

Macro inventory begins with:
- `GPU_CC_AHB_CLK` = 0 (clock, line 11)
- `GPU_CC_CRC_AHB_CLK` = 1 (clock, line 12)
- `GPU_CC_CX_APB_CLK` = 2 (clock, line 13)
- `GPU_CC_CX_FF_CLK` = 3 (clock, line 14)
- `GPU_CC_CX_GMU_CLK` = 4 (clock, line 15)
- `GPU_CC_CX_SNOC_DVM_CLK` = 5 (clock, line 16)
- `GPU_CC_CXO_AON_CLK` = 6 (clock, line 17)
- `GPU_CC_CXO_CLK` = 7 (clock, line 18)
- `GPU_CC_DEMET_CLK` = 8 (clock, line 19)
- `GPU_CC_DEMET_DIV_CLK_SRC` = 9 (clock, line 20)
- ... 24 additional numeric binding macros continue in the same contiguous namespace sections.

## Control Flow

This header has no branches, calls, or runtime control flow. The effective flow is build-time and probe-time: DTS sources include the constants, the device-tree compiler stores the resulting integers in clock/reset/power-domain specifier cells, and the Qualcomm clock-controller driver exposes provider arrays whose indexes must match these values. Consumer drivers later resolve those phandles through common clock, reset-controller, or genpd APIs.

## State and Persistence Behavior

The file owns no memory, locks, hardware registers, or persistent storage. Its state is the ABI value assigned to each macro. Those values persist in compiled DTBs and out-of-tree device trees, so renumbering or deleting an existing define is a compatibility break even though no runtime state is stored here. Actual enable counts, reset assertion state, and GDSC power state are maintained by the clock/reset/power-domain drivers and hardware registers, not by this header.

## Dependencies and Integration Points

Direct source dependencies are intentionally minimal: the header has only SPDX/copyright comments, an include guard, macro definitions, and `#endif`. It is integrated by textual inclusion rather than linking. Local integration evidence: clock-controller driver references: `sources/distributed-fs/ceph-client/drivers/clk/qcom/gpucc-sm8450.c`; device-tree references: `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/sm8450.dtsi`.

The semantic dependency is the matching provider implementation and its descriptor arrays. `qcom,sm8450-gpucc.h` IDs must stay aligned with driver tables for GPU PLL/RCG, GMU, CX/GX, hub, memory NoC, XO/sleep, SMMU vote, reset, and GDSC IDs. DTS consumers depend on these exact constants for properties such as `clocks`, `resets`, `power-domains`, and named clock inputs.

## Risks and Edge Cases

The main risk is ABI drift: inserting new IDs in the middle, reusing a removed value, or moving a reset/GDSC ID to a different number can silently bind a DTS consumer to the wrong hardware clock or power domain. It does not export reset IDs in this clock header; reset bindings are either absent for this controller or live in a paired reset binding header/driver table. Power-domain/GDSC IDs are exported as `GPU_GX_GDSC`=0 through `GPU_CX_GDSC`=1. Shared names such as PLLs, XO/sleep sources, bus clocks, and GDSCs are easy to copy between SoCs, but the numeric ordering must follow this specific provider, not a visually similar controller. Because the file is pure macros, the compiler provides little semantic checking beyond duplicate definitions and include-guard correctness.

## Test Signals

Useful validation includes building the relevant `drivers/clk/qcom` object with this header, compiling DTBs that include `qcom,sm8450-gpucc.h`, and running `dtbs_check`/binding-schema checks for the affected SoC. Runtime smoke tests are provider probe success without missing clock/reset IDs, absence of `-ENOENT`/`-EINVAL` from clock lookups, expected entries under common-clock debugfs, and successful bring-up of consumers in the exported domain set: GPU PLL/RCG, GMU, CX/GX, hub, memory NoC, XO/sleep, SMMU vote, reset, and GDSC IDs. For edits, diff the numeric table against the matching driver arrays and boot at least one DTS consumer when local hardware or emulation coverage exists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sm8450-gpucc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sm8450-videocc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sm8450-videocc.h

## Purpose

`sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sm8450-videocc.h` defines the public device-tree numeric IDs for the Qualcomm video clock-controller binding associated with `qcom,sm8450-videocc.h` / `sm8450`. The source was read completely for this report (38 lines). It is not executable kernel code; it is a stable binding contract included by DTS files and by the matching `drivers/clk/qcom` provider so that phandle clock, reset, and power-domain specifiers use the same indexes. This header is shared by multiple DTS or driver consumers in this tree, so numeric stability matters beyond one board file.

## Important APIs, Types, and Functions

There are no C functions, structs, or runtime APIs. The exported API is a set of preprocessor constants guarded by `_DT_BINDINGS_CLK_QCOM_VIDEO_CC_SM8450_H`. This header defines 12 clock IDs, 7 reset IDs, and 4 power-domain/GDSC IDs, for 23 numeric binding macros total.

Clock ID range: `VIDEO_CC_MVS0_CLK`=0 through `VIDEO_CC_PLL1`=11. Representative clocks: `VIDEO_CC_MVS0_CLK`, `VIDEO_CC_MVS0_CLK_SRC`, `VIDEO_CC_MVS0_DIV_CLK_SRC`, `VIDEO_CC_MVS0C_CLK`, `VIDEO_CC_MVS0C_DIV2_DIV_CLK_SRC`, `VIDEO_CC_MVS1_CLK`, `VIDEO_CC_MVS1_CLK_SRC`, `VIDEO_CC_MVS1_DIV_CLK_SRC`, `VIDEO_CC_MVS1C_CLK`, `VIDEO_CC_MVS1C_DIV2_DIV_CLK_SRC`, `VIDEO_CC_PLL0`, `VIDEO_CC_PLL1`.

Reset ID range: `CVP_VIDEO_CC_INTERFACE_BCR`=0 through `VIDEO_CC_MVS1C_CLK_ARES`=6. Representative resets: `CVP_VIDEO_CC_INTERFACE_BCR`, `CVP_VIDEO_CC_MVS0_BCR`, `CVP_VIDEO_CC_MVS0C_BCR`, `CVP_VIDEO_CC_MVS1_BCR`, `CVP_VIDEO_CC_MVS1C_BCR`, `VIDEO_CC_MVS0C_CLK_ARES`, `VIDEO_CC_MVS1C_CLK_ARES`.

Power-domain/GDSC range: `VIDEO_CC_MVS0C_GDSC`=0 through `VIDEO_CC_MVS1_GDSC`=3. Representative domains: `VIDEO_CC_MVS0C_GDSC`, `VIDEO_CC_MVS0_GDSC`, `VIDEO_CC_MVS1C_GDSC`, `VIDEO_CC_MVS1_GDSC`.

Macro inventory begins with:
- `VIDEO_CC_MVS0_CLK` = 0 (clock, line 10)
- `VIDEO_CC_MVS0_CLK_SRC` = 1 (clock, line 11)
- `VIDEO_CC_MVS0_DIV_CLK_SRC` = 2 (clock, line 12)
- `VIDEO_CC_MVS0C_CLK` = 3 (clock, line 13)
- `VIDEO_CC_MVS0C_DIV2_DIV_CLK_SRC` = 4 (clock, line 14)
- `VIDEO_CC_MVS1_CLK` = 5 (clock, line 15)
- `VIDEO_CC_MVS1_CLK_SRC` = 6 (clock, line 16)
- `VIDEO_CC_MVS1_DIV_CLK_SRC` = 7 (clock, line 17)
- `VIDEO_CC_MVS1C_CLK` = 8 (clock, line 18)
- `VIDEO_CC_MVS1C_DIV2_DIV_CLK_SRC` = 9 (clock, line 19)
- ... 13 additional numeric binding macros continue in the same contiguous namespace sections.

## Control Flow

This header has no branches, calls, or runtime control flow. The effective flow is build-time and probe-time: DTS sources include the constants, the device-tree compiler stores the resulting integers in clock/reset/power-domain specifier cells, and the Qualcomm clock-controller driver exposes provider arrays whose indexes must match these values. Consumer drivers later resolve those phandles through common clock, reset-controller, or genpd APIs.

## State and Persistence Behavior

The file owns no memory, locks, hardware registers, or persistent storage. Its state is the ABI value assigned to each macro. Those values persist in compiled DTBs and out-of-tree device trees, so renumbering or deleting an existing define is a compatibility break even though no runtime state is stored here. Actual enable counts, reset assertion state, and GDSC power state are maintained by the clock/reset/power-domain drivers and hardware registers, not by this header.

## Dependencies and Integration Points

Direct source dependencies are intentionally minimal: the header has only SPDX/copyright comments, an include guard, macro definitions, and `#endif`. It is integrated by textual inclusion rather than linking. Local integration evidence: clock-controller driver references: `sources/distributed-fs/ceph-client/drivers/clk/qcom/videocc-sm8450.c`; device-tree references: `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/hamoa.dtsi`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/sm8450.dtsi`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/sm8550.dtsi`.

The semantic dependency is the matching provider implementation and its descriptor arrays. `qcom,sm8450-videocc.h` IDs must stay aligned with driver tables for video codec MVS/MVS0/MVS1, AHB, AXI, sleep/XO, reset, and GDSC IDs. DTS consumers depend on these exact constants for properties such as `clocks`, `resets`, `power-domains`, and named clock inputs.

## Risks and Edge Cases

The main risk is ABI drift: inserting new IDs in the middle, reusing a removed value, or moving a reset/GDSC ID to a different number can silently bind a DTS consumer to the wrong hardware clock or power domain. It also exports reset IDs (`CVP_VIDEO_CC_INTERFACE_BCR`=0 through `VIDEO_CC_MVS1C_CLK_ARES`=6). Power-domain/GDSC IDs are exported as `VIDEO_CC_MVS0C_GDSC`=0 through `VIDEO_CC_MVS1_GDSC`=3. Shared names such as PLLs, XO/sleep sources, bus clocks, and GDSCs are easy to copy between SoCs, but the numeric ordering must follow this specific provider, not a visually similar controller. Because the file is pure macros, the compiler provides little semantic checking beyond duplicate definitions and include-guard correctness.

## Test Signals

Useful validation includes building the relevant `drivers/clk/qcom` object with this header, compiling DTBs that include `qcom,sm8450-videocc.h`, and running `dtbs_check`/binding-schema checks for the affected SoC. Runtime smoke tests are provider probe success without missing clock/reset IDs, absence of `-ENOENT`/`-EINVAL` from clock lookups, expected entries under common-clock debugfs, and successful bring-up of consumers in the exported domain set: video codec MVS/MVS0/MVS1, AHB, AXI, sleep/XO, reset, and GDSC IDs. For edits, diff the numeric table against the matching driver arrays and boot at least one DTS consumer when local hardware or emulation coverage exists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sm8450-videocc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sm8550-camcc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sm8550-camcc.h

## Purpose

`sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sm8550-camcc.h` defines the public device-tree numeric IDs for the Qualcomm camera clock-controller binding associated with `qcom,sm8550-camcc.h` / `sm8550`. The source was read completely for this report (187 lines). It is not executable kernel code; it is a stable binding contract included by DTS files and by the matching `drivers/clk/qcom` provider so that phandle clock, reset, and power-domain specifiers use the same indexes. This header is shared by multiple DTS or driver consumers in this tree, so numeric stability matters beyond one board file.

## Important APIs, Types, and Functions

There are no C functions, structs, or runtime APIs. The exported API is a set of preprocessor constants guarded by `_DT_BINDINGS_CLK_QCOM_CAM_CC_SM8550_H`. This header defines 152 clock IDs, 11 reset IDs, and 9 power-domain/GDSC IDs, for 172 numeric binding macros total.

Clock ID range: `CAM_CC_BPS_AHB_CLK`=0 through `CAM_CC_XO_CLK_SRC`=151. Representative clocks: `CAM_CC_BPS_AHB_CLK`, `CAM_CC_BPS_CLK`, `CAM_CC_BPS_CLK_SRC`, `CAM_CC_BPS_FAST_AHB_CLK`, `CAM_CC_CAMNOC_AXI_CLK`, `CAM_CC_CAMNOC_AXI_CLK_SRC`, ... `CAM_CC_SFE_1_CLK_SRC`, `CAM_CC_SFE_1_FAST_AHB_CLK`, `CAM_CC_SLEEP_CLK`, `CAM_CC_SLEEP_CLK_SRC`, `CAM_CC_SLOW_AHB_CLK_SRC`, `CAM_CC_XO_CLK_SRC`.

Reset ID range: `CAM_CC_BPS_BCR`=0 through `CAM_CC_SFE_1_BCR`=10. Representative resets: `CAM_CC_BPS_BCR`, `CAM_CC_DRV_BCR`, `CAM_CC_ICP_BCR`, `CAM_CC_IFE_0_BCR`, `CAM_CC_IFE_1_BCR`, `CAM_CC_IFE_2_BCR`, `CAM_CC_IPE_0_BCR`, `CAM_CC_QDSS_DEBUG_BCR`, `CAM_CC_SBI_BCR`, `CAM_CC_SFE_0_BCR`, `CAM_CC_SFE_1_BCR`.

Power-domain/GDSC range: `CAM_CC_BPS_GDSC`=0 through `CAM_CC_TITAN_TOP_GDSC`=8. Representative domains: `CAM_CC_BPS_GDSC`, `CAM_CC_IFE_0_GDSC`, `CAM_CC_IFE_1_GDSC`, `CAM_CC_IFE_2_GDSC`, `CAM_CC_IPE_0_GDSC`, `CAM_CC_SBI_GDSC`, `CAM_CC_SFE_0_GDSC`, `CAM_CC_SFE_1_GDSC`, `CAM_CC_TITAN_TOP_GDSC`.

Macro inventory begins with:
- `CAM_CC_BPS_AHB_CLK` = 0 (clock, line 10)
- `CAM_CC_BPS_CLK` = 1 (clock, line 11)
- `CAM_CC_BPS_CLK_SRC` = 2 (clock, line 12)
- `CAM_CC_BPS_FAST_AHB_CLK` = 3 (clock, line 13)
- `CAM_CC_CAMNOC_AXI_CLK` = 4 (clock, line 14)
- `CAM_CC_CAMNOC_AXI_CLK_SRC` = 5 (clock, line 15)
- `CAM_CC_CAMNOC_DCD_XO_CLK` = 6 (clock, line 16)
- `CAM_CC_CAMNOC_XO_CLK` = 7 (clock, line 17)
- `CAM_CC_CCI_0_CLK` = 8 (clock, line 18)
- `CAM_CC_CCI_0_CLK_SRC` = 9 (clock, line 19)
- ... 162 additional numeric binding macros continue in the same contiguous namespace sections.

## Control Flow

This header has no branches, calls, or runtime control flow. The effective flow is build-time and probe-time: DTS sources include the constants, the device-tree compiler stores the resulting integers in clock/reset/power-domain specifier cells, and the Qualcomm clock-controller driver exposes provider arrays whose indexes must match these values. Consumer drivers later resolve those phandles through common clock, reset-controller, or genpd APIs.

## State and Persistence Behavior

The file owns no memory, locks, hardware registers, or persistent storage. Its state is the ABI value assigned to each macro. Those values persist in compiled DTBs and out-of-tree device trees, so renumbering or deleting an existing define is a compatibility break even though no runtime state is stored here. Actual enable counts, reset assertion state, and GDSC power state are maintained by the clock/reset/power-domain drivers and hardware registers, not by this header.

## Dependencies and Integration Points

Direct source dependencies are intentionally minimal: the header has only SPDX/copyright comments, an include guard, macro definitions, and `#endif`. It is integrated by textual inclusion rather than linking. Local integration evidence: clock-controller driver references: `sources/distributed-fs/ceph-client/drivers/clk/qcom/camcc-sm8550.c`; device-tree references: `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/sm8550-hdk-rear-camera-card.dtso`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/sm8550.dtsi`.

The semantic dependency is the matching provider implementation and its descriptor arrays. `qcom,sm8550-camcc.h` IDs must stay aligned with driver tables for camera PLLs, MCLKs, CSI/CSIPHY timers, IFE/TFE/SFE/BPS/IPE/JPEG/CPAS fabric clocks, resets, and camera GDSCs. DTS consumers depend on these exact constants for properties such as `clocks`, `resets`, `power-domains`, and named clock inputs.

## Risks and Edge Cases

The main risk is ABI drift: inserting new IDs in the middle, reusing a removed value, or moving a reset/GDSC ID to a different number can silently bind a DTS consumer to the wrong hardware clock or power domain. It also exports reset IDs (`CAM_CC_BPS_BCR`=0 through `CAM_CC_SFE_1_BCR`=10). Power-domain/GDSC IDs are exported as `CAM_CC_BPS_GDSC`=0 through `CAM_CC_TITAN_TOP_GDSC`=8. Shared names such as PLLs, XO/sleep sources, bus clocks, and GDSCs are easy to copy between SoCs, but the numeric ordering must follow this specific provider, not a visually similar controller. Because the file is pure macros, the compiler provides little semantic checking beyond duplicate definitions and include-guard correctness.

## Test Signals

Useful validation includes building the relevant `drivers/clk/qcom` object with this header, compiling DTBs that include `qcom,sm8550-camcc.h`, and running `dtbs_check`/binding-schema checks for the affected SoC. Runtime smoke tests are provider probe success without missing clock/reset IDs, absence of `-ENOENT`/`-EINVAL` from clock lookups, expected entries under common-clock debugfs, and successful bring-up of consumers in the exported domain set: camera PLLs, MCLKs, CSI/CSIPHY timers, IFE/TFE/SFE/BPS/IPE/JPEG/CPAS fabric clocks, resets, and camera GDSCs. For edits, diff the numeric table against the matching driver arrays and boot at least one DTS consumer when local hardware or emulation coverage exists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sm8550-camcc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sm8550-dispcc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sm8550-dispcc.h

## Purpose

`sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sm8550-dispcc.h` defines the public device-tree numeric IDs for the Qualcomm display clock-controller binding associated with `qcom,sm8550-dispcc.h` / `sm8550`. The source was read completely for this report (101 lines). It is not executable kernel code; it is a stable binding contract included by DTS files and by the matching `drivers/clk/qcom` provider so that phandle clock, reset, and power-domain specifiers use the same indexes. This header is shared by multiple DTS or driver consumers in this tree, so numeric stability matters beyond one board file.

## Important APIs, Types, and Functions

There are no C functions, structs, or runtime APIs. The exported API is a set of preprocessor constants guarded by `_DT_BINDINGS_CLK_QCOM_SM8550_DISP_CC_H`. This header defines 81 clock IDs, 3 reset IDs, and 2 power-domain/GDSC IDs, for 86 numeric binding macros total.

Clock ID range: `DISP_CC_MDSS_ACCU_CLK`=0 through `DISP_CC_XO_CLK_SRC`=80. Representative clocks: `DISP_CC_MDSS_ACCU_CLK`, `DISP_CC_MDSS_AHB1_CLK`, `DISP_CC_MDSS_AHB_CLK`, `DISP_CC_MDSS_AHB_CLK_SRC`, `DISP_CC_MDSS_BYTE0_CLK`, `DISP_CC_MDSS_BYTE0_CLK_SRC`, ... `DISP_CC_PLL0`, `DISP_CC_PLL1`, `DISP_CC_SLEEP_CLK`, `DISP_CC_SLEEP_CLK_SRC`, `DISP_CC_XO_CLK`, `DISP_CC_XO_CLK_SRC`.

Reset ID range: `DISP_CC_MDSS_CORE_BCR`=0 through `DISP_CC_MDSS_RSCC_BCR`=2. Representative resets: `DISP_CC_MDSS_CORE_BCR`, `DISP_CC_MDSS_CORE_INT2_BCR`, `DISP_CC_MDSS_RSCC_BCR`.

Power-domain/GDSC range: `MDSS_GDSC`=0 through `MDSS_INT2_GDSC`=1. Representative domains: `MDSS_GDSC`, `MDSS_INT2_GDSC`.

Macro inventory begins with:
- `DISP_CC_MDSS_ACCU_CLK` = 0 (clock, line 10)
- `DISP_CC_MDSS_AHB1_CLK` = 1 (clock, line 11)
- `DISP_CC_MDSS_AHB_CLK` = 2 (clock, line 12)
- `DISP_CC_MDSS_AHB_CLK_SRC` = 3 (clock, line 13)
- `DISP_CC_MDSS_BYTE0_CLK` = 4 (clock, line 14)
- `DISP_CC_MDSS_BYTE0_CLK_SRC` = 5 (clock, line 15)
- `DISP_CC_MDSS_BYTE0_DIV_CLK_SRC` = 6 (clock, line 16)
- `DISP_CC_MDSS_BYTE0_INTF_CLK` = 7 (clock, line 17)
- `DISP_CC_MDSS_BYTE1_CLK` = 8 (clock, line 18)
- `DISP_CC_MDSS_BYTE1_CLK_SRC` = 9 (clock, line 19)
- ... 76 additional numeric binding macros continue in the same contiguous namespace sections.

## Control Flow

This header has no branches, calls, or runtime control flow. The effective flow is build-time and probe-time: DTS sources include the constants, the device-tree compiler stores the resulting integers in clock/reset/power-domain specifier cells, and the Qualcomm clock-controller driver exposes provider arrays whose indexes must match these values. Consumer drivers later resolve those phandles through common clock, reset-controller, or genpd APIs.

## State and Persistence Behavior

The file owns no memory, locks, hardware registers, or persistent storage. Its state is the ABI value assigned to each macro. Those values persist in compiled DTBs and out-of-tree device trees, so renumbering or deleting an existing define is a compatibility break even though no runtime state is stored here. Actual enable counts, reset assertion state, and GDSC power state are maintained by the clock/reset/power-domain drivers and hardware registers, not by this header.

## Dependencies and Integration Points

Direct source dependencies are intentionally minimal: the header has only SPDX/copyright comments, an include guard, macro definitions, and `#endif`. It is integrated by textual inclusion rather than linking. Local integration evidence: clock-controller driver references: `sources/distributed-fs/ceph-client/drivers/clk/qcom/dispcc-sm8550.c`; device-tree references: `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/sm8550.dtsi`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/sar2130p.dtsi`.

The semantic dependency is the matching provider implementation and its descriptor arrays. `qcom,sm8550-dispcc.h` IDs must stay aligned with driver tables for MDSS AHB/AXI, MDP, DSI byte/escape/pixel, DisplayPort link/pixel/aux, vsync, resets, and display GDSCs. DTS consumers depend on these exact constants for properties such as `clocks`, `resets`, `power-domains`, and named clock inputs.

## Risks and Edge Cases

The main risk is ABI drift: inserting new IDs in the middle, reusing a removed value, or moving a reset/GDSC ID to a different number can silently bind a DTS consumer to the wrong hardware clock or power domain. It also exports reset IDs (`DISP_CC_MDSS_CORE_BCR`=0 through `DISP_CC_MDSS_RSCC_BCR`=2). Power-domain/GDSC IDs are exported as `MDSS_GDSC`=0 through `MDSS_INT2_GDSC`=1. Shared names such as PLLs, XO/sleep sources, bus clocks, and GDSCs are easy to copy between SoCs, but the numeric ordering must follow this specific provider, not a visually similar controller. Because the file is pure macros, the compiler provides little semantic checking beyond duplicate definitions and include-guard correctness.

## Test Signals

Useful validation includes building the relevant `drivers/clk/qcom` object with this header, compiling DTBs that include `qcom,sm8550-dispcc.h`, and running `dtbs_check`/binding-schema checks for the affected SoC. Runtime smoke tests are provider probe success without missing clock/reset IDs, absence of `-ENOENT`/`-EINVAL` from clock lookups, expected entries under common-clock debugfs, and successful bring-up of consumers in the exported domain set: MDSS AHB/AXI, MDP, DSI byte/escape/pixel, DisplayPort link/pixel/aux, vsync, resets, and display GDSCs. For edits, diff the numeric table against the matching driver arrays and boot at least one DTS consumer when local hardware or emulation coverage exists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sm8550-dispcc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sm8550-gcc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sm8550-gcc.h

## Purpose

`sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sm8550-gcc.h` defines the public device-tree numeric IDs for the Qualcomm global clock-controller binding associated with `qcom,sm8550-gcc.h` / `sm8550`. The source was read completely for this report (231 lines). It is not executable kernel code; it is a stable binding contract included by DTS files and by the matching `drivers/clk/qcom` provider so that phandle clock, reset, and power-domain specifiers use the same indexes.

## Important APIs, Types, and Functions

There are no C functions, structs, or runtime APIs. The exported API is a set of preprocessor constants guarded by `_DT_BINDINGS_CLK_QCOM_GCC_SM8550_H`. This header defines 171 clock IDs, 36 reset IDs, and 8 power-domain/GDSC IDs, for 215 numeric binding macros total.

Clock ID range: `GCC_AGGRE_NOC_PCIE_AXI_CLK`=0 through `GCC_VIDEO_XO_CLK`=170. Representative clocks: `GCC_AGGRE_NOC_PCIE_AXI_CLK`, `GCC_AGGRE_UFS_PHY_AXI_CLK`, `GCC_AGGRE_UFS_PHY_AXI_HW_CTL_CLK`, `GCC_AGGRE_USB3_PRIM_AXI_CLK`, `GCC_AHB2PHY_0_CLK`, `GCC_BOOT_ROM_AHB_CLK`, ... `GCC_USB3_PRIM_PHY_PIPE_CLK`, `GCC_USB3_PRIM_PHY_PIPE_CLK_SRC`, `GCC_VIDEO_AHB_CLK`, `GCC_VIDEO_AXI0_CLK`, `GCC_VIDEO_AXI1_CLK`, `GCC_VIDEO_XO_CLK`.

Reset ID range: `GCC_CAMERA_BCR`=0 through `GCC_VIDEO_BCR`=35. Representative resets: `GCC_CAMERA_BCR`, `GCC_DISPLAY_BCR`, `GCC_GPU_BCR`, `GCC_PCIE_0_BCR`, `GCC_PCIE_0_LINK_DOWN_BCR`, `GCC_PCIE_0_NOCSR_COM_PHY_BCR`, ... `GCC_USB3PHY_PHY_PRIM_BCR`, `GCC_USB3PHY_PHY_SEC_BCR`, `GCC_USB_PHY_CFG_AHB2PHY_BCR`, `GCC_VIDEO_AXI0_CLK_ARES`, `GCC_VIDEO_AXI1_CLK_ARES`, `GCC_VIDEO_BCR`.

Power-domain/GDSC range: `PCIE_0_GDSC`=0 through `USB3_PHY_GDSC`=7. Representative domains: `PCIE_0_GDSC`, `PCIE_0_PHY_GDSC`, `PCIE_1_GDSC`, `PCIE_1_PHY_GDSC`, `UFS_PHY_GDSC`, `UFS_MEM_PHY_GDSC`, `USB30_PRIM_GDSC`, `USB3_PHY_GDSC`.

Macro inventory begins with:
- `GCC_AGGRE_NOC_PCIE_AXI_CLK` = 0 (clock, line 11)
- `GCC_AGGRE_UFS_PHY_AXI_CLK` = 1 (clock, line 12)
- `GCC_AGGRE_UFS_PHY_AXI_HW_CTL_CLK` = 2 (clock, line 13)
- `GCC_AGGRE_USB3_PRIM_AXI_CLK` = 3 (clock, line 14)
- `GCC_AHB2PHY_0_CLK` = 4 (clock, line 15)
- `GCC_BOOT_ROM_AHB_CLK` = 5 (clock, line 16)
- `GCC_CAMERA_AHB_CLK` = 6 (clock, line 17)
- `GCC_CAMERA_HF_AXI_CLK` = 7 (clock, line 18)
- `GCC_CAMERA_SF_AXI_CLK` = 8 (clock, line 19)
- `GCC_CAMERA_XO_CLK` = 9 (clock, line 20)
- ... 205 additional numeric binding macros continue in the same contiguous namespace sections.

## Control Flow

This header has no branches, calls, or runtime control flow. The effective flow is build-time and probe-time: DTS sources include the constants, the device-tree compiler stores the resulting integers in clock/reset/power-domain specifier cells, and the Qualcomm clock-controller driver exposes provider arrays whose indexes must match these values. Consumer drivers later resolve those phandles through common clock, reset-controller, or genpd APIs.

## State and Persistence Behavior

The file owns no memory, locks, hardware registers, or persistent storage. Its state is the ABI value assigned to each macro. Those values persist in compiled DTBs and out-of-tree device trees, so renumbering or deleting an existing define is a compatibility break even though no runtime state is stored here. Actual enable counts, reset assertion state, and GDSC power state are maintained by the clock/reset/power-domain drivers and hardware registers, not by this header.

## Dependencies and Integration Points

Direct source dependencies are intentionally minimal: the header has only SPDX/copyright comments, an include guard, macro definitions, and `#endif`. It is integrated by textual inclusion rather than linking. Local integration evidence: clock-controller driver references: `sources/distributed-fs/ceph-client/drivers/clk/qcom/gcc-sm8550.c`; device-tree references: `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/sm8550.dtsi`.

The semantic dependency is the matching provider implementation and its descriptor arrays. `qcom,sm8550-gcc.h` IDs must stay aligned with driver tables for global PLLs plus bus, QUP, USB, PCIe, UFS, SDCC, camera/display/video/gpu vote, reset, and GDSC IDs. DTS consumers depend on these exact constants for properties such as `clocks`, `resets`, `power-domains`, and named clock inputs.

## Risks and Edge Cases

The main risk is ABI drift: inserting new IDs in the middle, reusing a removed value, or moving a reset/GDSC ID to a different number can silently bind a DTS consumer to the wrong hardware clock or power domain. It also exports reset IDs (`GCC_CAMERA_BCR`=0 through `GCC_VIDEO_BCR`=35). Power-domain/GDSC IDs are exported as `PCIE_0_GDSC`=0 through `USB3_PHY_GDSC`=7. Shared names such as PLLs, XO/sleep sources, bus clocks, and GDSCs are easy to copy between SoCs, but the numeric ordering must follow this specific provider, not a visually similar controller. Because the file is pure macros, the compiler provides little semantic checking beyond duplicate definitions and include-guard correctness.

## Test Signals

Useful validation includes building the relevant `drivers/clk/qcom` object with this header, compiling DTBs that include `qcom,sm8550-gcc.h`, and running `dtbs_check`/binding-schema checks for the affected SoC. Runtime smoke tests are provider probe success without missing clock/reset IDs, absence of `-ENOENT`/`-EINVAL` from clock lookups, expected entries under common-clock debugfs, and successful bring-up of consumers in the exported domain set: global PLLs plus bus, QUP, USB, PCIe, UFS, SDCC, camera/display/video/gpu vote, reset, and GDSC IDs. For edits, diff the numeric table against the matching driver arrays and boot at least one DTS consumer when local hardware or emulation coverage exists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sm8550-gcc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sm8550-gpucc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sm8550-gpucc.h

## Purpose

`sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sm8550-gpucc.h` defines the public device-tree numeric IDs for the Qualcomm GPU clock-controller binding associated with `qcom,sm8550-gpucc.h` / `sm8550`. The source was read completely for this report (48 lines). It is not executable kernel code; it is a stable binding contract included by DTS files and by the matching `drivers/clk/qcom` provider so that phandle clock, reset, and power-domain specifiers use the same indexes.

## Important APIs, Types, and Functions

There are no C functions, structs, or runtime APIs. The exported API is a set of preprocessor constants guarded by `_DT_BINDINGS_CLK_QCOM_GPU_CC_SM8550_H`. This header defines 23 clock IDs, 8 reset IDs, and 2 power-domain/GDSC IDs, for 33 numeric binding macros total.

Clock ID range: `GPU_CC_AHB_CLK`=0 through `GPU_CC_XO_DIV_CLK_SRC`=22. Representative clocks: `GPU_CC_AHB_CLK`, `GPU_CC_CRC_AHB_CLK`, `GPU_CC_CX_FF_CLK`, `GPU_CC_CX_GMU_CLK`, `GPU_CC_CXO_AON_CLK`, `GPU_CC_CXO_CLK`, ... `GPU_CC_MND1X_1_GFX3D_CLK`, `GPU_CC_PLL0`, `GPU_CC_PLL1`, `GPU_CC_SLEEP_CLK`, `GPU_CC_XO_CLK_SRC`, `GPU_CC_XO_DIV_CLK_SRC`.

Reset ID range: `GPUCC_GPU_CC_ACD_BCR`=0 through `GPUCC_GPU_CC_XO_BCR`=7. Representative resets: `GPUCC_GPU_CC_ACD_BCR`, `GPUCC_GPU_CC_CX_BCR`, `GPUCC_GPU_CC_FAST_HUB_BCR`, `GPUCC_GPU_CC_FF_BCR`, `GPUCC_GPU_CC_GFX3D_AON_BCR`, `GPUCC_GPU_CC_GMU_BCR`, `GPUCC_GPU_CC_GX_BCR`, `GPUCC_GPU_CC_XO_BCR`.

Power-domain/GDSC range: `GPU_CC_CX_GDSC`=0 through `GPU_CC_GX_GDSC`=1. Representative domains: `GPU_CC_CX_GDSC`, `GPU_CC_GX_GDSC`.

Macro inventory begins with:
- `GPU_CC_AHB_CLK` = 0 (clock, line 10)
- `GPU_CC_CRC_AHB_CLK` = 1 (clock, line 11)
- `GPU_CC_CX_FF_CLK` = 2 (clock, line 12)
- `GPU_CC_CX_GMU_CLK` = 3 (clock, line 13)
- `GPU_CC_CXO_AON_CLK` = 4 (clock, line 14)
- `GPU_CC_CXO_CLK` = 5 (clock, line 15)
- `GPU_CC_DEMET_CLK` = 6 (clock, line 16)
- `GPU_CC_DEMET_DIV_CLK_SRC` = 7 (clock, line 17)
- `GPU_CC_FF_CLK_SRC` = 8 (clock, line 18)
- `GPU_CC_FREQ_MEASURE_CLK` = 9 (clock, line 19)
- ... 23 additional numeric binding macros continue in the same contiguous namespace sections.

## Control Flow

This header has no branches, calls, or runtime control flow. The effective flow is build-time and probe-time: DTS sources include the constants, the device-tree compiler stores the resulting integers in clock/reset/power-domain specifier cells, and the Qualcomm clock-controller driver exposes provider arrays whose indexes must match these values. Consumer drivers later resolve those phandles through common clock, reset-controller, or genpd APIs.

## State and Persistence Behavior

The file owns no memory, locks, hardware registers, or persistent storage. Its state is the ABI value assigned to each macro. Those values persist in compiled DTBs and out-of-tree device trees, so renumbering or deleting an existing define is a compatibility break even though no runtime state is stored here. Actual enable counts, reset assertion state, and GDSC power state are maintained by the clock/reset/power-domain drivers and hardware registers, not by this header.

## Dependencies and Integration Points

Direct source dependencies are intentionally minimal: the header has only SPDX/copyright comments, an include guard, macro definitions, and `#endif`. It is integrated by textual inclusion rather than linking. Local integration evidence: clock-controller driver references: `sources/distributed-fs/ceph-client/drivers/clk/qcom/gpucc-sm8550.c`; device-tree references: `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/sm8550.dtsi`.

The semantic dependency is the matching provider implementation and its descriptor arrays. `qcom,sm8550-gpucc.h` IDs must stay aligned with driver tables for GPU PLL/RCG, GMU, CX/GX, hub, memory NoC, XO/sleep, SMMU vote, reset, and GDSC IDs. DTS consumers depend on these exact constants for properties such as `clocks`, `resets`, `power-domains`, and named clock inputs.

## Risks and Edge Cases

The main risk is ABI drift: inserting new IDs in the middle, reusing a removed value, or moving a reset/GDSC ID to a different number can silently bind a DTS consumer to the wrong hardware clock or power domain. It also exports reset IDs (`GPUCC_GPU_CC_ACD_BCR`=0 through `GPUCC_GPU_CC_XO_BCR`=7). Power-domain/GDSC IDs are exported as `GPU_CC_CX_GDSC`=0 through `GPU_CC_GX_GDSC`=1. Shared names such as PLLs, XO/sleep sources, bus clocks, and GDSCs are easy to copy between SoCs, but the numeric ordering must follow this specific provider, not a visually similar controller. Because the file is pure macros, the compiler provides little semantic checking beyond duplicate definitions and include-guard correctness.

## Test Signals

Useful validation includes building the relevant `drivers/clk/qcom` object with this header, compiling DTBs that include `qcom,sm8550-gpucc.h`, and running `dtbs_check`/binding-schema checks for the affected SoC. Runtime smoke tests are provider probe success without missing clock/reset IDs, absence of `-ENOENT`/`-EINVAL` from clock lookups, expected entries under common-clock debugfs, and successful bring-up of consumers in the exported domain set: GPU PLL/RCG, GMU, CX/GX, hub, memory NoC, XO/sleep, SMMU vote, reset, and GDSC IDs. For edits, diff the numeric table against the matching driver arrays and boot at least one DTS consumer when local hardware or emulation coverage exists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sm8550-gpucc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sm8550-tcsr.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sm8550-tcsr.h

## Purpose

`sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sm8550-tcsr.h` defines the public device-tree numeric IDs for the Qualcomm TCSR clock-reference binding associated with `qcom,sm8550-tcsr.h` / `sm8550`. The source was read completely for this report (18 lines). It is not executable kernel code; it is a stable binding contract included by DTS files and by the matching `drivers/clk/qcom` provider so that phandle clock, reset, and power-domain specifiers use the same indexes. This header is shared by multiple DTS or driver consumers in this tree, so numeric stability matters beyond one board file.

## Important APIs, Types, and Functions

There are no C functions, structs, or runtime APIs. The exported API is a set of preprocessor constants guarded by `_DT_BINDINGS_CLK_QCOM_TCSR_CC_SM8550_H`. This header defines 6 clock IDs, 0 reset IDs, and 0 power-domain/GDSC IDs, for 6 numeric binding macros total.

Clock ID range: `TCSR_PCIE_0_CLKREF_EN`=0 through `TCSR_USB3_CLKREF_EN`=5. Representative clocks: `TCSR_PCIE_0_CLKREF_EN`, `TCSR_PCIE_1_CLKREF_EN`, `TCSR_UFS_CLKREF_EN`, `TCSR_UFS_PAD_CLKREF_EN`, `TCSR_USB2_CLKREF_EN`, `TCSR_USB3_CLKREF_EN`.

Reset ID range: none. Representative resets: none.

Power-domain/GDSC range: none. Representative domains: none.

Macro inventory begins with:
- `TCSR_PCIE_0_CLKREF_EN` = 0 (clock, line 11)
- `TCSR_PCIE_1_CLKREF_EN` = 1 (clock, line 12)
- `TCSR_UFS_CLKREF_EN` = 2 (clock, line 13)
- `TCSR_UFS_PAD_CLKREF_EN` = 3 (clock, line 14)
- `TCSR_USB2_CLKREF_EN` = 4 (clock, line 15)
- `TCSR_USB3_CLKREF_EN` = 5 (clock, line 16)

## Control Flow

This header has no branches, calls, or runtime control flow. The effective flow is build-time and probe-time: DTS sources include the constants, the device-tree compiler stores the resulting integers in clock/reset/power-domain specifier cells, and the Qualcomm clock-controller driver exposes provider arrays whose indexes must match these values. Consumer drivers later resolve those phandles through common clock, reset-controller, or genpd APIs.

## State and Persistence Behavior

The file owns no memory, locks, hardware registers, or persistent storage. Its state is the ABI value assigned to each macro. Those values persist in compiled DTBs and out-of-tree device trees, so renumbering or deleting an existing define is a compatibility break even though no runtime state is stored here. Actual enable counts, reset assertion state, and GDSC power state are maintained by the clock/reset/power-domain drivers and hardware registers, not by this header.

## Dependencies and Integration Points

Direct source dependencies are intentionally minimal: the header has only SPDX/copyright comments, an include guard, macro definitions, and `#endif`. It is integrated by textual inclusion rather than linking. Local integration evidence: clock-controller driver references: `sources/distributed-fs/ceph-client/drivers/clk/qcom/tcsrcc-sm8550.c`; device-tree references: `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/sm8550.dtsi`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/sar2130p.dtsi`.

The semantic dependency is the matching provider implementation and its descriptor arrays. `qcom,sm8550-tcsr.h` IDs must stay aligned with driver tables for TCSR clock reference enable IDs for PCIe, UFS, USB2, and USB3 pads. DTS consumers depend on these exact constants for properties such as `clocks`, `resets`, `power-domains`, and named clock inputs.

## Risks and Edge Cases

The main risk is ABI drift: inserting new IDs in the middle, reusing a removed value, or moving a reset/GDSC ID to a different number can silently bind a DTS consumer to the wrong hardware clock or power domain. It does not export reset IDs in this clock header; reset bindings are either absent for this controller or live in a paired reset binding header/driver table. It does not export GDSC or power-domain IDs. Shared names such as PLLs, XO/sleep sources, bus clocks, and GDSCs are easy to copy between SoCs, but the numeric ordering must follow this specific provider, not a visually similar controller. Because the file is pure macros, the compiler provides little semantic checking beyond duplicate definitions and include-guard correctness.

## Test Signals

Useful validation includes building the relevant `drivers/clk/qcom` object with this header, compiling DTBs that include `qcom,sm8550-tcsr.h`, and running `dtbs_check`/binding-schema checks for the affected SoC. Runtime smoke tests are provider probe success without missing clock/reset IDs, absence of `-ENOENT`/`-EINVAL` from clock lookups, expected entries under common-clock debugfs, and successful bring-up of consumers in the exported domain set: TCSR clock reference enable IDs for PCIe, UFS, USB2, and USB3 pads. For edits, diff the numeric table against the matching driver arrays and boot at least one DTS consumer when local hardware or emulation coverage exists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sm8550-tcsr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sm8650-camcc.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sm8650-camcc.h

## Purpose

`sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sm8650-camcc.h` defines the public device-tree numeric IDs for the Qualcomm camera clock-controller binding associated with `qcom,sm8650-camcc.h` / `sm8650`. The source was read completely for this report (195 lines). It is not executable kernel code; it is a stable binding contract included by DTS files and by the matching `drivers/clk/qcom` provider so that phandle clock, reset, and power-domain specifiers use the same indexes. This header is shared by multiple DTS or driver consumers in this tree, so numeric stability matters beyond one board file.

## Important APIs, Types, and Functions

There are no C functions, structs, or runtime APIs. The exported API is a set of preprocessor constants guarded by `_DT_BINDINGS_CLK_QCOM_CAM_CC_SM8650_H`. This header defines 158 clock IDs, 12 reset IDs, and 10 power-domain/GDSC IDs, for 180 numeric binding macros total.

Clock ID range: `CAM_CC_BPS_AHB_CLK`=0 through `CAM_CC_XO_CLK_SRC`=157. Representative clocks: `CAM_CC_BPS_AHB_CLK`, `CAM_CC_BPS_CLK`, `CAM_CC_BPS_CLK_SRC`, `CAM_CC_BPS_FAST_AHB_CLK`, `CAM_CC_BPS_SHIFT_CLK`, `CAM_CC_CAMNOC_AXI_NRT_CLK`, ... `CAM_CC_SFE_2_SHIFT_CLK`, `CAM_CC_SLEEP_CLK`, `CAM_CC_SLEEP_CLK_SRC`, `CAM_CC_SLOW_AHB_CLK_SRC`, `CAM_CC_TITAN_TOP_SHIFT_CLK`, `CAM_CC_XO_CLK_SRC`.

Reset ID range: `CAM_CC_BPS_BCR`=0 through `CAM_CC_SFE_2_BCR`=11. Representative resets: `CAM_CC_BPS_BCR`, `CAM_CC_DRV_BCR`, `CAM_CC_ICP_BCR`, `CAM_CC_IFE_0_BCR`, `CAM_CC_IFE_1_BCR`, `CAM_CC_IFE_2_BCR`, `CAM_CC_IPE_0_BCR`, `CAM_CC_QDSS_DEBUG_BCR`, `CAM_CC_SBI_BCR`, `CAM_CC_SFE_0_BCR`, `CAM_CC_SFE_1_BCR`, `CAM_CC_SFE_2_BCR`.

Power-domain/GDSC range: `CAM_CC_TITAN_TOP_GDSC`=0 through `CAM_CC_SFE_2_GDSC`=9. Representative domains: `CAM_CC_TITAN_TOP_GDSC`, `CAM_CC_BPS_GDSC`, `CAM_CC_IFE_0_GDSC`, `CAM_CC_IFE_1_GDSC`, `CAM_CC_IFE_2_GDSC`, `CAM_CC_IPE_0_GDSC`, `CAM_CC_SBI_GDSC`, `CAM_CC_SFE_0_GDSC`, `CAM_CC_SFE_1_GDSC`, `CAM_CC_SFE_2_GDSC`.

Macro inventory begins with:
- `CAM_CC_BPS_AHB_CLK` = 0 (clock, line 10)
- `CAM_CC_BPS_CLK` = 1 (clock, line 11)
- `CAM_CC_BPS_CLK_SRC` = 2 (clock, line 12)
- `CAM_CC_BPS_FAST_AHB_CLK` = 3 (clock, line 13)
- `CAM_CC_BPS_SHIFT_CLK` = 4 (clock, line 14)
- `CAM_CC_CAMNOC_AXI_NRT_CLK` = 5 (clock, line 15)
- `CAM_CC_CAMNOC_AXI_RT_CLK` = 6 (clock, line 16)
- `CAM_CC_CAMNOC_AXI_RT_CLK_SRC` = 7 (clock, line 17)
- `CAM_CC_CAMNOC_DCD_XO_CLK` = 8 (clock, line 18)
- `CAM_CC_CAMNOC_XO_CLK` = 9 (clock, line 19)
- ... 170 additional numeric binding macros continue in the same contiguous namespace sections.

## Control Flow

This header has no branches, calls, or runtime control flow. The effective flow is build-time and probe-time: DTS sources include the constants, the device-tree compiler stores the resulting integers in clock/reset/power-domain specifier cells, and the Qualcomm clock-controller driver exposes provider arrays whose indexes must match these values. Consumer drivers later resolve those phandles through common clock, reset-controller, or genpd APIs.

## State and Persistence Behavior

The file owns no memory, locks, hardware registers, or persistent storage. Its state is the ABI value assigned to each macro. Those values persist in compiled DTBs and out-of-tree device trees, so renumbering or deleting an existing define is a compatibility break even though no runtime state is stored here. Actual enable counts, reset assertion state, and GDSC power state are maintained by the clock/reset/power-domain drivers and hardware registers, not by this header.

## Dependencies and Integration Points

Direct source dependencies are intentionally minimal: the header has only SPDX/copyright comments, an include guard, macro definitions, and `#endif`. It is integrated by textual inclusion rather than linking. Local integration evidence: clock-controller driver references: `sources/distributed-fs/ceph-client/drivers/clk/qcom/camcc-sm8650.c`; device-tree references: `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/sm8650.dtsi`, `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/sm8650-hdk-rear-camera-card.dtso`.

The semantic dependency is the matching provider implementation and its descriptor arrays. `qcom,sm8650-camcc.h` IDs must stay aligned with driver tables for camera PLLs, MCLKs, CSI/CSIPHY timers, IFE/TFE/SFE/BPS/IPE/JPEG/CPAS fabric clocks, resets, and camera GDSCs. DTS consumers depend on these exact constants for properties such as `clocks`, `resets`, `power-domains`, and named clock inputs.

## Risks and Edge Cases

The main risk is ABI drift: inserting new IDs in the middle, reusing a removed value, or moving a reset/GDSC ID to a different number can silently bind a DTS consumer to the wrong hardware clock or power domain. It also exports reset IDs (`CAM_CC_BPS_BCR`=0 through `CAM_CC_SFE_2_BCR`=11). Power-domain/GDSC IDs are exported as `CAM_CC_TITAN_TOP_GDSC`=0 through `CAM_CC_SFE_2_GDSC`=9. Shared names such as PLLs, XO/sleep sources, bus clocks, and GDSCs are easy to copy between SoCs, but the numeric ordering must follow this specific provider, not a visually similar controller. Because the file is pure macros, the compiler provides little semantic checking beyond duplicate definitions and include-guard correctness.

## Test Signals

Useful validation includes building the relevant `drivers/clk/qcom` object with this header, compiling DTBs that include `qcom,sm8650-camcc.h`, and running `dtbs_check`/binding-schema checks for the affected SoC. Runtime smoke tests are provider probe success without missing clock/reset IDs, absence of `-ENOENT`/`-EINVAL` from clock lookups, expected entries under common-clock debugfs, and successful bring-up of consumers in the exported domain set: camera PLLs, MCLKs, CSI/CSIPHY timers, IFE/TFE/SFE/BPS/IPE/JPEG/CPAS fabric clocks, resets, and camera GDSCs. For edits, diff the numeric table against the matching driver arrays and boot at least one DTS consumer when local hardware or emulation coverage exists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sm8650-camcc.h -->
