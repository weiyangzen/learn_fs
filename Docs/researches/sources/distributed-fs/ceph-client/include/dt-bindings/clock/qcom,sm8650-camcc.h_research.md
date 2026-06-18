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
