# sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,qdu1000-ecpricc.h

## Purpose

`sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,qdu1000-ecpricc.h` defines the public device-tree numeric IDs for the Qualcomm eCPRI clock-controller binding associated with `qcom,qdu1000-ecpricc.h` / `qdu1000`. The source was read completely for this report (147 lines). It is not executable kernel code; it is a stable binding contract included by DTS files and by the matching `drivers/clk/qcom` provider so that phandle clock, reset, and power-domain specifiers use the same indexes.

## Important APIs, Types, and Functions

There are no C functions, structs, or runtime APIs. The exported API is a set of preprocessor constants guarded by `_DT_BINDINGS_CLK_QCOM_ECPRI_CC_QDU1000_H`. This header defines 126 clock IDs, 8 reset IDs, and 0 power-domain/GDSC IDs, for 134 numeric binding macros total.

Clock ID range: `ECPRI_CC_PLL0`=0 through `ECPRI_CC_PHY4_LANE3_TX_CLK`=125. Representative clocks: `ECPRI_CC_PLL0`, `ECPRI_CC_PLL1`, `ECPRI_CC_ECPRI_CG_CLK`, `ECPRI_CC_ECPRI_CLK_SRC`, `ECPRI_CC_ECPRI_DMA_CLK`, `ECPRI_CC_ECPRI_DMA_CLK_SRC`, ... `ECPRI_CC_PHY4_LANE1_RX_CLK`, `ECPRI_CC_PHY4_LANE1_TX_CLK`, `ECPRI_CC_PHY4_LANE2_RX_CLK`, `ECPRI_CC_PHY4_LANE2_TX_CLK`, `ECPRI_CC_PHY4_LANE3_RX_CLK`, `ECPRI_CC_PHY4_LANE3_TX_CLK`.

Reset ID range: `ECPRI_CC_CLK_CTL_TOP_ECPRI_CC_ECPRI_SS_BCR`=0 through `ECPRI_CC_CLK_CTL_TOP_ECPRI_CC_NOC_BCR`=7. Representative resets: `ECPRI_CC_CLK_CTL_TOP_ECPRI_CC_ECPRI_SS_BCR`, `ECPRI_CC_CLK_CTL_TOP_ECPRI_CC_ETH_C2C_BCR`, `ECPRI_CC_CLK_CTL_TOP_ECPRI_CC_ETH_FH0_BCR`, `ECPRI_CC_CLK_CTL_TOP_ECPRI_CC_ETH_FH1_BCR`, `ECPRI_CC_CLK_CTL_TOP_ECPRI_CC_ETH_FH2_BCR`, `ECPRI_CC_CLK_CTL_TOP_ECPRI_CC_ETH_WRAPPER_TOP_BCR`, `ECPRI_CC_CLK_CTL_TOP_ECPRI_CC_MODEM_BCR`, `ECPRI_CC_CLK_CTL_TOP_ECPRI_CC_NOC_BCR`.

Power-domain/GDSC range: none. Representative domains: none.

Macro inventory begins with:
- `ECPRI_CC_PLL0` = 0 (clock, line 10)
- `ECPRI_CC_PLL1` = 1 (clock, line 11)
- `ECPRI_CC_ECPRI_CG_CLK` = 2 (clock, line 12)
- `ECPRI_CC_ECPRI_CLK_SRC` = 3 (clock, line 13)
- `ECPRI_CC_ECPRI_DMA_CLK` = 4 (clock, line 14)
- `ECPRI_CC_ECPRI_DMA_CLK_SRC` = 5 (clock, line 15)
- `ECPRI_CC_ECPRI_DMA_NOC_CLK` = 6 (clock, line 16)
- `ECPRI_CC_ECPRI_FAST_CLK` = 7 (clock, line 17)
- `ECPRI_CC_ECPRI_FAST_CLK_SRC` = 8 (clock, line 18)
- `ECPRI_CC_ECPRI_FAST_DIV2_CLK` = 9 (clock, line 19)
- ... 124 additional numeric binding macros continue in the same contiguous namespace sections.

## Control Flow

This header has no branches, calls, or runtime control flow. The effective flow is build-time and probe-time: DTS sources include the constants, the device-tree compiler stores the resulting integers in clock/reset/power-domain specifier cells, and the Qualcomm clock-controller driver exposes provider arrays whose indexes must match these values. Consumer drivers later resolve those phandles through common clock, reset-controller, or genpd APIs.

## State and Persistence Behavior

The file owns no memory, locks, hardware registers, or persistent storage. Its state is the ABI value assigned to each macro. Those values persist in compiled DTBs and out-of-tree device trees, so renumbering or deleting an existing define is a compatibility break even though no runtime state is stored here. Actual enable counts, reset assertion state, and GDSC power state are maintained by the clock/reset/power-domain drivers and hardware registers, not by this header.

## Dependencies and Integration Points

Direct source dependencies are intentionally minimal: the header has only SPDX/copyright comments, an include guard, macro definitions, and `#endif`. It is integrated by textual inclusion rather than linking. Local integration evidence: clock-controller driver references: `sources/distributed-fs/ceph-client/drivers/clk/qcom/ecpricc-qdu1000.c`.

The semantic dependency is the matching provider implementation and its descriptor arrays. `qcom,qdu1000-ecpricc.h` IDs must stay aligned with driver tables for eCPRI, Ethernet/PCS, PTP, DCC, AHB, AXI, memory, and PHY clock/reset IDs. DTS consumers depend on these exact constants for properties such as `clocks`, `resets`, `power-domains`, and named clock inputs.

## Risks and Edge Cases

The main risk is ABI drift: inserting new IDs in the middle, reusing a removed value, or moving a reset/GDSC ID to a different number can silently bind a DTS consumer to the wrong hardware clock or power domain. It also exports reset IDs (`ECPRI_CC_CLK_CTL_TOP_ECPRI_CC_ECPRI_SS_BCR`=0 through `ECPRI_CC_CLK_CTL_TOP_ECPRI_CC_NOC_BCR`=7). It does not export GDSC or power-domain IDs. Shared names such as PLLs, XO/sleep sources, bus clocks, and GDSCs are easy to copy between SoCs, but the numeric ordering must follow this specific provider, not a visually similar controller. Because the file is pure macros, the compiler provides little semantic checking beyond duplicate definitions and include-guard correctness.

## Test Signals

Useful validation includes building the relevant `drivers/clk/qcom` object with this header, compiling DTBs that include `qcom,qdu1000-ecpricc.h`, and running `dtbs_check`/binding-schema checks for the affected SoC. Runtime smoke tests are provider probe success without missing clock/reset IDs, absence of `-ENOENT`/`-EINVAL` from clock lookups, expected entries under common-clock debugfs, and successful bring-up of consumers in the exported domain set: eCPRI, Ethernet/PCS, PTP, DCC, AHB, AXI, memory, and PHY clock/reset IDs. For edits, diff the numeric table against the matching driver arrays and boot at least one DTS consumer when local hardware or emulation coverage exists.
