# sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,qca8k-nsscc.h

## Purpose

`sources/distributed-fs/ceph-client/include/dt-bindings/clock/qcom,qca8k-nsscc.h` defines the public device-tree numeric IDs for the Qualcomm network subsystem clock-controller binding associated with `qcom,qca8k-nsscc.h` / `qca8k`. The source was read completely for this report (101 lines). It is not executable kernel code; it is a stable binding contract included by DTS files and by the matching `drivers/clk/qcom` provider so that phandle clock, reset, and power-domain specifiers use the same indexes.

## Important APIs, Types, and Functions

There are no C functions, structs, or runtime APIs. The exported API is a set of preprocessor constants guarded by `_DT_BINDINGS_CLK_QCOM_QCA8K_NSS_CC_H`. This header defines 92 clock IDs, 0 reset IDs, and 0 power-domain/GDSC IDs, for 92 numeric binding macros total.

Clock ID range: `NSS_CC_SWITCH_CORE_CLK_SRC`=0 through `NSS_CC_GEPHY3_SYS_CLK`=91. Representative clocks: `NSS_CC_SWITCH_CORE_CLK_SRC`, `NSS_CC_SWITCH_CORE_CLK`, `NSS_CC_APB_BRIDGE_CLK`, `NSS_CC_MAC0_TX_CLK_SRC`, `NSS_CC_MAC0_TX_DIV_CLK_SRC`, `NSS_CC_MAC0_TX_CLK`, ... `NSS_CC_SRDS0_SYS_CLK`, `NSS_CC_SRDS1_SYS_CLK`, `NSS_CC_GEPHY0_SYS_CLK`, `NSS_CC_GEPHY1_SYS_CLK`, `NSS_CC_GEPHY2_SYS_CLK`, `NSS_CC_GEPHY3_SYS_CLK`.

Reset ID range: none. Representative resets: none.

Power-domain/GDSC range: none. Representative domains: none.

Macro inventory begins with:
- `NSS_CC_SWITCH_CORE_CLK_SRC` = 0 (clock, line 9)
- `NSS_CC_SWITCH_CORE_CLK` = 1 (clock, line 10)
- `NSS_CC_APB_BRIDGE_CLK` = 2 (clock, line 11)
- `NSS_CC_MAC0_TX_CLK_SRC` = 3 (clock, line 12)
- `NSS_CC_MAC0_TX_DIV_CLK_SRC` = 4 (clock, line 13)
- `NSS_CC_MAC0_TX_CLK` = 5 (clock, line 14)
- `NSS_CC_MAC0_TX_SRDS1_CLK` = 6 (clock, line 15)
- `NSS_CC_MAC0_RX_CLK_SRC` = 7 (clock, line 16)
- `NSS_CC_MAC0_RX_DIV_CLK_SRC` = 8 (clock, line 17)
- `NSS_CC_MAC0_RX_CLK` = 9 (clock, line 18)
- ... 82 additional numeric binding macros continue in the same contiguous namespace sections.

## Control Flow

This header has no branches, calls, or runtime control flow. The effective flow is build-time and probe-time: DTS sources include the constants, the device-tree compiler stores the resulting integers in clock/reset/power-domain specifier cells, and the Qualcomm clock-controller driver exposes provider arrays whose indexes must match these values. Consumer drivers later resolve those phandles through common clock, reset-controller, or genpd APIs.

## State and Persistence Behavior

The file owns no memory, locks, hardware registers, or persistent storage. Its state is the ABI value assigned to each macro. Those values persist in compiled DTBs and out-of-tree device trees, so renumbering or deleting an existing define is a compatibility break even though no runtime state is stored here. Actual enable counts, reset assertion state, and GDSC power state are maintained by the clock/reset/power-domain drivers and hardware registers, not by this header.

## Dependencies and Integration Points

Direct source dependencies are intentionally minimal: the header has only SPDX/copyright comments, an include guard, macro definitions, and `#endif`. It is integrated by textual inclusion rather than linking. Local integration evidence: clock-controller driver references: `sources/distributed-fs/ceph-client/drivers/clk/qcom/nsscc-qca8k.c`.

The semantic dependency is the matching provider implementation and its descriptor arrays. `qcom,qca8k-nsscc.h` IDs must stay aligned with driver tables for NSS/packet-processing, switch, UNIPHY, port, crypto, memory, AHB/AXI, reset, and fabric clocks. DTS consumers depend on these exact constants for properties such as `clocks`, `resets`, `power-domains`, and named clock inputs.

## Risks and Edge Cases

The main risk is ABI drift: inserting new IDs in the middle, reusing a removed value, or moving a reset/GDSC ID to a different number can silently bind a DTS consumer to the wrong hardware clock or power domain. It does not export reset IDs in this clock header; reset bindings are either absent for this controller or live in a paired reset binding header/driver table. It does not export GDSC or power-domain IDs. Shared names such as PLLs, XO/sleep sources, bus clocks, and GDSCs are easy to copy between SoCs, but the numeric ordering must follow this specific provider, not a visually similar controller. Because the file is pure macros, the compiler provides little semantic checking beyond duplicate definitions and include-guard correctness.

## Test Signals

Useful validation includes building the relevant `drivers/clk/qcom` object with this header, compiling DTBs that include `qcom,qca8k-nsscc.h`, and running `dtbs_check`/binding-schema checks for the affected SoC. Runtime smoke tests are provider probe success without missing clock/reset IDs, absence of `-ENOENT`/`-EINVAL` from clock lookups, expected entries under common-clock debugfs, and successful bring-up of consumers in the exported domain set: NSS/packet-processing, switch, UNIPHY, port, crypto, memory, AHB/AXI, reset, and fabric clocks. For edits, diff the numeric table against the matching driver arrays and boot at least one DTS consumer when local hardware or emulation coverage exists.
