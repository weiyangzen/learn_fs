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
