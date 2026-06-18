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
