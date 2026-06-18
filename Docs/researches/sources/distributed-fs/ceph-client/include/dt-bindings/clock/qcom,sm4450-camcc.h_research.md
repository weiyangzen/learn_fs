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
