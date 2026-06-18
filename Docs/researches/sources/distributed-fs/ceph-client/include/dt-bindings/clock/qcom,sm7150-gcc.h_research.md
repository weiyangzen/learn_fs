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
