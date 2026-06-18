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
