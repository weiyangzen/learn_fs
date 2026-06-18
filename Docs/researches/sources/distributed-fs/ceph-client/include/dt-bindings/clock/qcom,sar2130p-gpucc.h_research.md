# sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sar2130p-gpucc.h

## Purpose

`sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sar2130p-gpucc.h` defines the public device-tree numeric IDs for the Qualcomm GPU clock-controller binding associated with `qcom,sar2130p-gpucc.h` / `sar2130p`. The source was read completely for this report (33 lines). It is not executable kernel code; it is a stable binding contract included by DTS files and by the matching `drivers/clk/qcom` provider so that phandle clock, reset, and power-domain specifiers use the same indexes.

## Important APIs, Types, and Functions

There are no C functions, structs, or runtime APIs. The exported API is a set of preprocessor constants guarded by `_DT_BINDINGS_CLK_QCOM_GPU_CC_SAR2130P_H`. This header defines 17 clock IDs, 0 reset IDs, and 2 power-domain/GDSC IDs, for 19 numeric binding macros total.

Clock ID range: `GPU_CC_AHB_CLK`=0 through `GPU_CC_SLEEP_CLK`=16. Representative clocks: `GPU_CC_AHB_CLK`, `GPU_CC_CRC_AHB_CLK`, `GPU_CC_CX_FF_CLK`, `GPU_CC_CX_GMU_CLK`, `GPU_CC_CXO_AON_CLK`, `GPU_CC_CXO_CLK`, ... `GPU_CC_HUB_CLK_SRC`, `GPU_CC_HUB_CX_INT_CLK`, `GPU_CC_MEMNOC_GFX_CLK`, `GPU_CC_PLL0`, `GPU_CC_PLL1`, `GPU_CC_SLEEP_CLK`.

Reset ID range: none. Representative resets: none.

Power-domain/GDSC range: `GPU_GX_GDSC`=0 through `GPU_CX_GDSC`=1. Representative domains: `GPU_GX_GDSC`, `GPU_CX_GDSC`.

Macro inventory begins with:
- `GPU_CC_AHB_CLK` = 0 (clock, line 11)
- `GPU_CC_CRC_AHB_CLK` = 1 (clock, line 12)
- `GPU_CC_CX_FF_CLK` = 2 (clock, line 13)
- `GPU_CC_CX_GMU_CLK` = 3 (clock, line 14)
- `GPU_CC_CXO_AON_CLK` = 4 (clock, line 15)
- `GPU_CC_CXO_CLK` = 5 (clock, line 16)
- `GPU_CC_FF_CLK_SRC` = 6 (clock, line 17)
- `GPU_CC_GMU_CLK_SRC` = 7 (clock, line 18)
- `GPU_CC_GX_GMU_CLK` = 8 (clock, line 19)
- `GPU_CC_HLOS1_VOTE_GPU_SMMU_CLK` = 9 (clock, line 20)
- ... 9 additional numeric binding macros continue in the same contiguous namespace sections.

## Control Flow

This header has no branches, calls, or runtime control flow. The effective flow is build-time and probe-time: DTS sources include the constants, the device-tree compiler stores the resulting integers in clock/reset/power-domain specifier cells, and the Qualcomm clock-controller driver exposes provider arrays whose indexes must match these values. Consumer drivers later resolve those phandles through common clock, reset-controller, or genpd APIs.

## State and Persistence Behavior

The file owns no memory, locks, hardware registers, or persistent storage. Its state is the ABI value assigned to each macro. Those values persist in compiled DTBs and out-of-tree device trees, so renumbering or deleting an existing define is a compatibility break even though no runtime state is stored here. Actual enable counts, reset assertion state, and GDSC power state are maintained by the clock/reset/power-domain drivers and hardware registers, not by this header.

## Dependencies and Integration Points

Direct source dependencies are intentionally minimal: the header has only SPDX/copyright comments, an include guard, macro definitions, and `#endif`. It is integrated by textual inclusion rather than linking. Local integration evidence: clock-controller driver references: `sources/distributed-fs/ceph-client/drivers/clk/qcom/gpucc-sar2130p.c`; device-tree references: `sources/distributed-fs/ceph-client/arch/arm64/boot/dts/qcom/sar2130p.dtsi`.

The semantic dependency is the matching provider implementation and its descriptor arrays. `qcom,sar2130p-gpucc.h` IDs must stay aligned with driver tables for GPU PLL/RCG, GMU, CX/GX, hub, memory NoC, XO/sleep, SMMU vote, reset, and GDSC IDs. DTS consumers depend on these exact constants for properties such as `clocks`, `resets`, `power-domains`, and named clock inputs.

## Risks and Edge Cases

The main risk is ABI drift: inserting new IDs in the middle, reusing a removed value, or moving a reset/GDSC ID to a different number can silently bind a DTS consumer to the wrong hardware clock or power domain. It does not export reset IDs in this clock header; reset bindings are either absent for this controller or live in a paired reset binding header/driver table. Power-domain/GDSC IDs are exported as `GPU_GX_GDSC`=0 through `GPU_CX_GDSC`=1. Shared names such as PLLs, XO/sleep sources, bus clocks, and GDSCs are easy to copy between SoCs, but the numeric ordering must follow this specific provider, not a visually similar controller. Because the file is pure macros, the compiler provides little semantic checking beyond duplicate definitions and include-guard correctness.

## Test Signals

Useful validation includes building the relevant `drivers/clk/qcom` object with this header, compiling DTBs that include `qcom,sar2130p-gpucc.h`, and running `dtbs_check`/binding-schema checks for the affected SoC. Runtime smoke tests are provider probe success without missing clock/reset IDs, absence of `-ENOENT`/`-EINVAL` from clock lookups, expected entries under common-clock debugfs, and successful bring-up of consumers in the exported domain set: GPU PLL/RCG, GMU, CX/GX, hub, memory NoC, XO/sleep, SMMU vote, reset, and GDSC IDs. For edits, diff the numeric table against the matching driver arrays and boot at least one DTS consumer when local hardware or emulation coverage exists.
