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
