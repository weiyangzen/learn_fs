# sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sm7150-camcc.h

## Purpose

`sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,sm7150-camcc.h` defines the public device-tree numeric IDs for the Qualcomm camera clock-controller binding associated with `qcom,sm7150-camcc.h` / `sm7150`. The source was read completely for this report (113 lines). It is not executable kernel code; it is a stable binding contract included by DTS files and by the matching `drivers/clk/qcom` provider so that phandle clock, reset, and power-domain specifiers use the same indexes.

## Important APIs, Types, and Functions

There are no C functions, structs, or runtime APIs. The exported API is a set of preprocessor constants guarded by `_DT_BINDINGS_CLK_QCOM_CAMCC_SM7150_H`. This header defines 91 clock IDs, 0 reset IDs, and 6 power-domain/GDSC IDs, for 97 numeric binding macros total.

Clock ID range: `CAMCC_PLL0_OUT_EVEN`=0 through `CAMCC_XO_CLK_SRC`=90. Representative clocks: `CAMCC_PLL0_OUT_EVEN`, `CAMCC_PLL0_OUT_ODD`, `CAMCC_PLL1_OUT_EVEN`, `CAMCC_PLL2_OUT_EARLY`, `CAMCC_PLL3_OUT_EVEN`, `CAMCC_PLL4_OUT_EVEN`, ... `CAMCC_MCLK3_CLK`, `CAMCC_MCLK3_CLK_SRC`, `CAMCC_SLEEP_CLK`, `CAMCC_SLEEP_CLK_SRC`, `CAMCC_SLOW_AHB_CLK_SRC`, `CAMCC_XO_CLK_SRC`.

Reset ID range: none. Representative resets: none.

Power-domain/GDSC range: `BPS_GDSC`=0 through `TITAN_TOP_GDSC`=5. Representative domains: `BPS_GDSC`, `IFE_0_GDSC`, `IFE_1_GDSC`, `IPE_0_GDSC`, `IPE_1_GDSC`, `TITAN_TOP_GDSC`.

Macro inventory begins with:
- `CAMCC_PLL0_OUT_EVEN` = 0 (clock, line 11)
- `CAMCC_PLL0_OUT_ODD` = 1 (clock, line 12)
- `CAMCC_PLL1_OUT_EVEN` = 2 (clock, line 13)
- `CAMCC_PLL2_OUT_EARLY` = 3 (clock, line 14)
- `CAMCC_PLL3_OUT_EVEN` = 4 (clock, line 15)
- `CAMCC_PLL4_OUT_EVEN` = 5 (clock, line 16)
- `CAMCC_PLL0` = 6 (clock, line 19)
- `CAMCC_PLL1` = 7 (clock, line 20)
- `CAMCC_PLL2` = 8 (clock, line 21)
- `CAMCC_PLL2_OUT_AUX` = 9 (clock, line 22)
- ... 87 additional numeric binding macros continue in the same contiguous namespace sections.

## Control Flow

This header has no branches, calls, or runtime control flow. The effective flow is build-time and probe-time: DTS sources include the constants, the device-tree compiler stores the resulting integers in clock/reset/power-domain specifier cells, and the Qualcomm clock-controller driver exposes provider arrays whose indexes must match these values. Consumer drivers later resolve those phandles through common clock, reset-controller, or genpd APIs.

## State and Persistence Behavior

The file owns no memory, locks, hardware registers, or persistent storage. Its state is the ABI value assigned to each macro. Those values persist in compiled DTBs and out-of-tree device trees, so renumbering or deleting an existing define is a compatibility break even though no runtime state is stored here. Actual enable counts, reset assertion state, and GDSC power state are maintained by the clock/reset/power-domain drivers and hardware registers, not by this header.

## Dependencies and Integration Points

Direct source dependencies are intentionally minimal: the header has only SPDX/copyright comments, an include guard, macro definitions, and `#endif`. It is integrated by textual inclusion rather than linking. Local integration evidence: clock-controller driver references: `sources/distributed-fs/ceph-client/drivers/clk/qcom/camcc-sm7150.c`.

The semantic dependency is the matching provider implementation and its descriptor arrays. `qcom,sm7150-camcc.h` IDs must stay aligned with driver tables for camera PLLs, MCLKs, CSI/CSIPHY timers, IFE/TFE/SFE/BPS/IPE/JPEG/CPAS fabric clocks, resets, and camera GDSCs. DTS consumers depend on these exact constants for properties such as `clocks`, `resets`, `power-domains`, and named clock inputs.

## Risks and Edge Cases

The main risk is ABI drift: inserting new IDs in the middle, reusing a removed value, or moving a reset/GDSC ID to a different number can silently bind a DTS consumer to the wrong hardware clock or power domain. It does not export reset IDs in this clock header; reset bindings are either absent for this controller or live in a paired reset binding header/driver table. Power-domain/GDSC IDs are exported as `BPS_GDSC`=0 through `TITAN_TOP_GDSC`=5. Shared names such as PLLs, XO/sleep sources, bus clocks, and GDSCs are easy to copy between SoCs, but the numeric ordering must follow this specific provider, not a visually similar controller. Because the file is pure macros, the compiler provides little semantic checking beyond duplicate definitions and include-guard correctness.

## Test Signals

Useful validation includes building the relevant `drivers/clk/qcom` object with this header, compiling DTBs that include `qcom,sm7150-camcc.h`, and running `dtbs_check`/binding-schema checks for the affected SoC. Runtime smoke tests are provider probe success without missing clock/reset IDs, absence of `-ENOENT`/`-EINVAL` from clock lookups, expected entries under common-clock debugfs, and successful bring-up of consumers in the exported domain set: camera PLLs, MCLKs, CSI/CSIPHY timers, IFE/TFE/SFE/BPS/IPE/JPEG/CPAS fabric clocks, resets, and camera GDSCs. For edits, diff the numeric table against the matching driver arrays and boot at least one DTS consumer when local hardware or emulation coverage exists.
