# sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sm8350-videocc.h

## Purpose

`sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sm8350-videocc.h` defines the public device-tree numeric IDs for the Qualcomm video clock-controller binding associated with `qcom,sm8350-videocc.h` / `sm8350`. The source was read completely for this report (35 lines). It is not executable kernel code; it is a stable binding contract included by DTS files and by the matching `drivers/clk/qcom` provider so that phandle clock, reset, and power-domain specifiers use the same indexes.

## Important APIs, Types, and Functions

There are no C functions, structs, or runtime APIs. The exported API is a set of preprocessor constants guarded by `_DT_BINDINGS_CLK_QCOM_VIDEO_CC_SM8350_H`. This header defines 17 clock IDs, 0 reset IDs, and 4 power-domain/GDSC IDs, for 21 numeric binding macros total.

Clock ID range: `VIDEO_CC_AHB_CLK_SRC`=0 through `VIDEO_PLL1`=16. Representative clocks: `VIDEO_CC_AHB_CLK_SRC`, `VIDEO_CC_MVS0_CLK`, `VIDEO_CC_MVS0_CLK_SRC`, `VIDEO_CC_MVS0_DIV_CLK_SRC`, `VIDEO_CC_MVS0C_CLK`, `VIDEO_CC_MVS0C_DIV2_DIV_CLK_SRC`, ... `VIDEO_CC_MVS1C_DIV2_DIV_CLK_SRC`, `VIDEO_CC_SLEEP_CLK`, `VIDEO_CC_SLEEP_CLK_SRC`, `VIDEO_CC_XO_CLK_SRC`, `VIDEO_PLL0`, `VIDEO_PLL1`.

Reset ID range: none. Representative resets: none.

Power-domain/GDSC range: `MVS0C_GDSC`=0 through `MVS1_GDSC`=3. Representative domains: `MVS0C_GDSC`, `MVS1C_GDSC`, `MVS0_GDSC`, `MVS1_GDSC`.

Macro inventory begins with:
- `VIDEO_CC_AHB_CLK_SRC` = 0 (clock, line 11)
- `VIDEO_CC_MVS0_CLK` = 1 (clock, line 12)
- `VIDEO_CC_MVS0_CLK_SRC` = 2 (clock, line 13)
- `VIDEO_CC_MVS0_DIV_CLK_SRC` = 3 (clock, line 14)
- `VIDEO_CC_MVS0C_CLK` = 4 (clock, line 15)
- `VIDEO_CC_MVS0C_DIV2_DIV_CLK_SRC` = 5 (clock, line 16)
- `VIDEO_CC_MVS1_CLK` = 6 (clock, line 17)
- `VIDEO_CC_MVS1_CLK_SRC` = 7 (clock, line 18)
- `VIDEO_CC_MVS1_DIV2_CLK` = 8 (clock, line 19)
- `VIDEO_CC_MVS1_DIV_CLK_SRC` = 9 (clock, line 20)
- ... 11 additional numeric binding macros continue in the same contiguous namespace sections.

## Control Flow

This header has no branches, calls, or runtime control flow. The effective flow is build-time and probe-time: DTS sources include the constants, the device-tree compiler stores the resulting integers in clock/reset/power-domain specifier cells, and the Qualcomm clock-controller driver exposes provider arrays whose indexes must match these values. Consumer drivers later resolve those phandles through common clock, reset-controller, or genpd APIs.

## State and Persistence Behavior

The file owns no memory, locks, hardware registers, or persistent storage. Its state is the ABI value assigned to each macro. Those values persist in compiled DTBs and out-of-tree device trees, so renumbering or deleting an existing define is a compatibility break even though no runtime state is stored here. Actual enable counts, reset assertion state, and GDSC power state are maintained by the clock/reset/power-domain drivers and hardware registers, not by this header.

## Dependencies and Integration Points

Direct source dependencies are intentionally minimal: the header has only SPDX/copyright comments, an include guard, macro definitions, and `#endif`. It is integrated by textual inclusion rather than linking. Local integration evidence: clock-controller driver references: `sources/distributed-fs/ceph-client/drivers/clk/qcom/videocc-sm8350.c`.

The semantic dependency is the matching provider implementation and its descriptor arrays. `qcom,sm8350-videocc.h` IDs must stay aligned with driver tables for video codec MVS/MVS0/MVS1, AHB, AXI, sleep/XO, reset, and GDSC IDs. DTS consumers depend on these exact constants for properties such as `clocks`, `resets`, `power-domains`, and named clock inputs.

## Risks and Edge Cases

The main risk is ABI drift: inserting new IDs in the middle, reusing a removed value, or moving a reset/GDSC ID to a different number can silently bind a DTS consumer to the wrong hardware clock or power domain. It does not export reset IDs in this clock header; reset bindings are either absent for this controller or live in a paired reset binding header/driver table. Power-domain/GDSC IDs are exported as `MVS0C_GDSC`=0 through `MVS1_GDSC`=3. Shared names such as PLLs, XO/sleep sources, bus clocks, and GDSCs are easy to copy between SoCs, but the numeric ordering must follow this specific provider, not a visually similar controller. Because the file is pure macros, the compiler provides little semantic checking beyond duplicate definitions and include-guard correctness.

## Test Signals

Useful validation includes building the relevant `drivers/clk/qcom` object with this header, compiling DTBs that include `qcom,sm8350-videocc.h`, and running `dtbs_check`/binding-schema checks for the affected SoC. Runtime smoke tests are provider probe success without missing clock/reset IDs, absence of `-ENOENT`/`-EINVAL` from clock lookups, expected entries under common-clock debugfs, and successful bring-up of consumers in the exported domain set: video codec MVS/MVS0/MVS1, AHB, AXI, sleep/XO, reset, and GDSC IDs. For edits, diff the numeric table against the matching driver arrays and boot at least one DTS consumer when local hardware or emulation coverage exists.
