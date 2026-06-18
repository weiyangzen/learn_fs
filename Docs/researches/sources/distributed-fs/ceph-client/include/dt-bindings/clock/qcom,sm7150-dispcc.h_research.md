# sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sm7150-dispcc.h

## Purpose

`sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sm7150-dispcc.h` defines the public device-tree numeric IDs for the Qualcomm display clock-controller binding associated with `qcom,sm7150-dispcc.h` / `sm7150`. The source was read completely for this report (62 lines). It is not executable kernel code; it is a stable binding contract included by DTS files and by the matching `drivers/clk/qcom` provider so that phandle clock, reset, and power-domain specifiers use the same indexes.

## Important APIs, Types, and Functions

There are no C functions, structs, or runtime APIs. The exported API is a set of preprocessor constants guarded by `_DT_BINDINGS_CLK_QCOM_DISPCC_SM7150_H`. This header defines 43 clock IDs, 1 reset ID, and 1 power-domain/GDSC ID, for 45 numeric binding macros total.

Clock ID range: `DISPCC_PLL0`=0 through `DISPCC_SLEEP_CLK_SRC`=42. Representative clocks: `DISPCC_PLL0`, `DISPCC_MDSS_AHB_CLK`, `DISPCC_MDSS_AHB_CLK_SRC`, `DISPCC_MDSS_BYTE0_CLK`, `DISPCC_MDSS_BYTE0_CLK_SRC`, `DISPCC_MDSS_BYTE0_DIV_CLK_SRC`, ... `DISPCC_MDSS_RSCC_VSYNC_CLK`, `DISPCC_MDSS_VSYNC_CLK`, `DISPCC_MDSS_VSYNC_CLK_SRC`, `DISPCC_XO_CLK_SRC`, `DISPCC_SLEEP_CLK`, `DISPCC_SLEEP_CLK_SRC`.

Reset ID range: `DISPCC_MDSS_CORE_BCR`=0 through `DISPCC_MDSS_CORE_BCR`=0. Representative resets: `DISPCC_MDSS_CORE_BCR`.

Power-domain/GDSC range: `MDSS_GDSC`=0 through `MDSS_GDSC`=0. Representative domains: `MDSS_GDSC`.

Macro inventory begins with:
- `DISPCC_PLL0` = 0 (clock, line 12)
- `DISPCC_MDSS_AHB_CLK` = 1 (clock, line 13)
- `DISPCC_MDSS_AHB_CLK_SRC` = 2 (clock, line 14)
- `DISPCC_MDSS_BYTE0_CLK` = 3 (clock, line 15)
- `DISPCC_MDSS_BYTE0_CLK_SRC` = 4 (clock, line 16)
- `DISPCC_MDSS_BYTE0_DIV_CLK_SRC` = 5 (clock, line 17)
- `DISPCC_MDSS_BYTE0_INTF_CLK` = 6 (clock, line 18)
- `DISPCC_MDSS_BYTE1_CLK` = 7 (clock, line 19)
- `DISPCC_MDSS_BYTE1_CLK_SRC` = 8 (clock, line 20)
- `DISPCC_MDSS_BYTE1_DIV_CLK_SRC` = 9 (clock, line 21)
- ... 35 additional numeric binding macros continue in the same contiguous namespace sections.

## Control Flow

This header has no branches, calls, or runtime control flow. The effective flow is build-time and probe-time: DTS sources include the constants, the device-tree compiler stores the resulting integers in clock/reset/power-domain specifier cells, and the Qualcomm clock-controller driver exposes provider arrays whose indexes must match these values. Consumer drivers later resolve those phandles through common clock, reset-controller, or genpd APIs.

## State and Persistence Behavior

The file owns no memory, locks, hardware registers, or persistent storage. Its state is the ABI value assigned to each macro. Those values persist in compiled DTBs and out-of-tree device trees, so renumbering or deleting an existing define is a compatibility break even though no runtime state is stored here. Actual enable counts, reset assertion state, and GDSC power state are maintained by the clock/reset/power-domain drivers and hardware registers, not by this header.

## Dependencies and Integration Points

Direct source dependencies are intentionally minimal: the header has only SPDX/copyright comments, an include guard, macro definitions, and `#endif`. It is integrated by textual inclusion rather than linking. Local integration evidence: clock-controller driver references: `sources/distributed-fs/ceph-client/drivers/clk/qcom/dispcc-sm7150.c`.

The semantic dependency is the matching provider implementation and its descriptor arrays. `qcom,sm7150-dispcc.h` IDs must stay aligned with driver tables for MDSS AHB/AXI, MDP, DSI byte/escape/pixel, DisplayPort link/pixel/aux, vsync, resets, and display GDSCs. DTS consumers depend on these exact constants for properties such as `clocks`, `resets`, `power-domains`, and named clock inputs.

## Risks and Edge Cases

The main risk is ABI drift: inserting new IDs in the middle, reusing a removed value, or moving a reset/GDSC ID to a different number can silently bind a DTS consumer to the wrong hardware clock or power domain. It also exports reset IDs (`DISPCC_MDSS_CORE_BCR`=0 through `DISPCC_MDSS_CORE_BCR`=0). Power-domain/GDSC IDs are exported as `MDSS_GDSC`=0 through `MDSS_GDSC`=0. Shared names such as PLLs, XO/sleep sources, bus clocks, and GDSCs are easy to copy between SoCs, but the numeric ordering must follow this specific provider, not a visually similar controller. Because the file is pure macros, the compiler provides little semantic checking beyond duplicate definitions and include-guard correctness.

## Test Signals

Useful validation includes building the relevant `drivers/clk/qcom` object with this header, compiling DTBs that include `qcom,sm7150-dispcc.h`, and running `dtbs_check`/binding-schema checks for the affected SoC. Runtime smoke tests are provider probe success without missing clock/reset IDs, absence of `-ENOENT`/`-EINVAL` from clock lookups, expected entries under common-clock debugfs, and successful bring-up of consumers in the exported domain set: MDSS AHB/AXI, MDP, DSI byte/escape/pixel, DisplayPort link/pixel/aux, vsync, resets, and display GDSCs. For edits, diff the numeric table against the matching driver arrays and boot at least one DTS consumer when local hardware or emulation coverage exists.
