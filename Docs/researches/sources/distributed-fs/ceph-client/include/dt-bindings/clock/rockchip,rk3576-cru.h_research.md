# sources/distributed-fs/ceph-client/include/dt-bindings/clock/rockchip,rk3576-cru.h

## Purpose
`rockchip,rk3576-cru.h` is the RK3576 clock binding header. It exposes a broad CRU clock ID space, secure clock IDs, SCMI aliases, and IO-controlled output clocks for a recent Rockchip SoC.

## Important APIs, types, and functions
The macro namespace begins with PLLs (`PLL_BPLL`, `PLL_LPLL`, `PLL_VPLL`, `PLL_AUPLL`, `PLL_CPLL`, `PLL_GPLL`, `PLL_PPLL`) and CPU clocks (`ARMCLK_L`, `ARMCLK_B`). It defines many `CLK_*`, `ACLK_*`, `HCLK_*`, `PCLK_*`, `MCLK_*`, `SCLK_*`, `DCLK_*`, `TCLK_*`, `DBCLK_*`, and `FCLK_*` IDs. Later sections include secure clock IDs, `SCMI_ARMCLK_L`, `SCMI_ARMCLK_B`, `SCMI_CLK_GPU`, and IO output clocks such as `CLK_SAI*_MCLKOUT_TO_IO` and `CLK_FSPI*_TO_IO`.

## Control flow
The header has no runtime logic. Device-tree users reference IDs; the RK3576 CRU provider, SCMI firmware, or IO mux/output-clock path carries out the requested operation.

## State and persistence
No state is stored in the file. The duplicate `CLK_SAI4_MCLKOUT_TO_IO` definition documents the same value twice and should be treated carefully because external users may already rely on that spelling/value. Hardware and firmware hold clock state.

## Dependencies and integration points
It integrates with RK3576 DTS, the Rockchip clock driver, SCMI firmware, secure-world clock management, audio SAI output pins, FSPI clock output routing, and drivers for CPU/GPU, display, video, ISP, storage, network, USB/PCIe PHYs, crypto, watchdog/timers, and serial buses.

## Risks and test signals
Risks include SCMI/direct ID confusion, accidental renumbering in a dense ABI, duplicated definitions hiding merge mistakes, and output clocks requiring coordinated pinctrl/IO-domain setup. Test signals include schema validation, clk-summary coverage, SCMI get-rate/set-rate for CPU/GPU clocks, audio MCLK output validation, FSPI operation, and peripheral probe success across secure and non-secure domains.
