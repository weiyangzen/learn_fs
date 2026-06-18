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
