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
