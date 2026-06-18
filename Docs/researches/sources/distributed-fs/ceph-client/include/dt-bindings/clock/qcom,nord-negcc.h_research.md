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
