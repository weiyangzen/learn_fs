# sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,nord-segcc.h

## Purpose

`sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,nord-segcc.h` defines the public device-tree numeric IDs for the Qualcomm global clock-controller binding associated with `qcom,nord-segcc.h` / `nord`. The source was read completely for this report (98 lines). It is not executable kernel code; it is a stable binding contract included by DTS files and by the matching `drivers/clk/qcom` provider so that phandle clock, reset, and power-domain specifiers use the same indexes.

## Important APIs, Types, and Functions

There are no C functions, structs, or runtime APIs. The exported API is a set of preprocessor constants guarded by `_DT_BINDINGS_CLK_QCOM_SE_GCC_NORD_H`. This header defines 77 clock IDs, 4 reset IDs, and 2 power-domain/GDSC IDs, for 83 numeric binding macros total.

Clock ID range: `SE_GCC_EEE_EMAC0_CLK`=0 through `SE_GCC_QUPV3_WRAP1_S_AHB_CLK`=76. Representative clocks: `SE_GCC_EEE_EMAC0_CLK`, `SE_GCC_EEE_EMAC0_CLK_SRC`, `SE_GCC_EEE_EMAC1_CLK`, `SE_GCC_EEE_EMAC1_CLK_SRC`, `SE_GCC_EMAC0_AXI_CLK`, `SE_GCC_EMAC0_CC_SGMIIPHY_RX_CLK`, ... `SE_GCC_QUPV3_WRAP1_S4_CLK_SRC`, `SE_GCC_QUPV3_WRAP1_S5_CLK`, `SE_GCC_QUPV3_WRAP1_S5_CLK_SRC`, `SE_GCC_QUPV3_WRAP1_S6_CLK`, `SE_GCC_QUPV3_WRAP1_S6_CLK_SRC`, `SE_GCC_QUPV3_WRAP1_S_AHB_CLK`.

Reset ID range: `SE_GCC_EMAC0_BCR`=0 through `SE_GCC_QUPV3_WRAPPER_1_BCR`=3. Representative resets: `SE_GCC_EMAC0_BCR`, `SE_GCC_EMAC1_BCR`, `SE_GCC_QUPV3_WRAPPER_0_BCR`, `SE_GCC_QUPV3_WRAPPER_1_BCR`.

Power-domain/GDSC range: `SE_GCC_EMAC0_GDSC`=0 through `SE_GCC_EMAC1_GDSC`=1. Representative domains: `SE_GCC_EMAC0_GDSC`, `SE_GCC_EMAC1_GDSC`.

Macro inventory begins with:
- `SE_GCC_EEE_EMAC0_CLK` = 0 (clock, line 10)
- `SE_GCC_EEE_EMAC0_CLK_SRC` = 1 (clock, line 11)
- `SE_GCC_EEE_EMAC1_CLK` = 2 (clock, line 12)
- `SE_GCC_EEE_EMAC1_CLK_SRC` = 3 (clock, line 13)
- `SE_GCC_EMAC0_AXI_CLK` = 4 (clock, line 14)
- `SE_GCC_EMAC0_CC_SGMIIPHY_RX_CLK` = 5 (clock, line 15)
- `SE_GCC_EMAC0_CC_SGMIIPHY_TX_CLK` = 6 (clock, line 16)
- `SE_GCC_EMAC0_PHY_AUX_CLK` = 7 (clock, line 17)
- `SE_GCC_EMAC0_PHY_AUX_CLK_SRC` = 8 (clock, line 18)
- `SE_GCC_EMAC0_PTP_CLK` = 9 (clock, line 19)
- ... 73 additional numeric binding macros continue in the same contiguous namespace sections.

## Control Flow

This header has no branches, calls, or runtime control flow. The effective flow is build-time and probe-time: DTS sources include the constants, the device-tree compiler stores the resulting integers in clock/reset/power-domain specifier cells, and the Qualcomm clock-controller driver exposes provider arrays whose indexes must match these values. Consumer drivers later resolve those phandles through common clock, reset-controller, or genpd APIs.

## State and Persistence Behavior

The file owns no memory, locks, hardware registers, or persistent storage. Its state is the ABI value assigned to each macro. Those values persist in compiled DTBs and out-of-tree device trees, so renumbering or deleting an existing define is a compatibility break even though no runtime state is stored here. Actual enable counts, reset assertion state, and GDSC power state are maintained by the clock/reset/power-domain drivers and hardware registers, not by this header.

## Dependencies and Integration Points

Direct source dependencies are intentionally minimal: the header has only SPDX/copyright comments, an include guard, macro definitions, and `#endif`. It is integrated by textual inclusion rather than linking. Local integration evidence: clock-controller driver references: `sources/distributed-fs/ceph-client/drivers/clk/qcom/segcc-nord.c`.

The semantic dependency is the matching provider implementation and its descriptor arrays. `qcom,nord-segcc.h` IDs must stay aligned with driver tables for global PLLs plus bus, QUP, USB, PCIe, UFS, SDCC, camera/display/video/gpu vote, reset, and GDSC IDs. DTS consumers depend on these exact constants for properties such as `clocks`, `resets`, `power-domains`, and named clock inputs.

## Risks and Edge Cases

The main risk is ABI drift: inserting new IDs in the middle, reusing a removed value, or moving a reset/GDSC ID to a different number can silently bind a DTS consumer to the wrong hardware clock or power domain. It also exports reset IDs (`SE_GCC_EMAC0_BCR`=0 through `SE_GCC_QUPV3_WRAPPER_1_BCR`=3). Power-domain/GDSC IDs are exported as `SE_GCC_EMAC0_GDSC`=0 through `SE_GCC_EMAC1_GDSC`=1. Shared names such as PLLs, XO/sleep sources, bus clocks, and GDSCs are easy to copy between SoCs, but the numeric ordering must follow this specific provider, not a visually similar controller. Because the file is pure macros, the compiler provides little semantic checking beyond duplicate definitions and include-guard correctness.

## Test Signals

Useful validation includes building the relevant `drivers/clk/qcom` object with this header, compiling DTBs that include `qcom,nord-segcc.h`, and running `dtbs_check`/binding-schema checks for the affected SoC. Runtime smoke tests are provider probe success without missing clock/reset IDs, absence of `-ENOENT`/`-EINVAL` from clock lookups, expected entries under common-clock debugfs, and successful bring-up of consumers in the exported domain set: global PLLs plus bus, QUP, USB, PCIe, UFS, SDCC, camera/display/video/gpu vote, reset, and GDSC IDs. For edits, diff the numeric table against the matching driver arrays and boot at least one DTS consumer when local hardware or emulation coverage exists.
