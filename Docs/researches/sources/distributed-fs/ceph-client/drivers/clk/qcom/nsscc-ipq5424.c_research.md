# sources/distributed-fs/ceph-client/drivers/clk/qcom/nsscc-ipq5424.c

## Purpose
`nsscc-ipq5424.c` implements the Qualcomm NSS clock controller for IPQ5424 networking SoCs. It registers NSS/PPE/packet-engine clocks, Ethernet port RX/TX and MAC clocks, UNIPHY clocks, XGMAC PTP reference clocks, reset lines, and hardware-backed interconnect nodes for NSS NoC paths. Clock IDs, reset IDs, and interconnect node IDs come from `dt-bindings/clock/qcom,ipq5424-nsscc.h`, `dt-bindings/reset/qcom,ipq5424-nsscc.h`, and `dt-bindings/interconnect/qcom,ipq5424.h`.

## Important APIs, Types, And Functions
The core data types are `struct parent_map`, `struct clk_parent_data`, `struct freq_tbl`, `struct freq_conf`, `struct freq_multi_tbl`, `struct clk_rcg2`, `struct clk_regmap_div`, `struct clk_branch`, `struct qcom_reset_map`, `struct qcom_icc_hws_data`, `struct regmap_config`, and `struct qcom_cc_desc`. The networking port RCGs use `freq_multi_tbl` and `clk_rcg2_floor_ops`, allowing discrete multi-output frequency programming for 25 MHz and 125 MHz Ethernet-style rates.

`nss_cc_ipq5424_probe()` is the only custom runtime function. It enables runtime PM, creates a PM clock container, adds a `"bus"` PM clock, resumes the device so the NSSCC register block is accessible, calls `qcom_cc_probe()`, and then drops the runtime PM reference. Runtime PM callbacks are `pm_clk_suspend` and `pm_clk_resume` through `SET_RUNTIME_PM_OPS()`. The platform driver also sets `.sync_state = icc_sync_state` so interconnect aggregation can synchronize after consumers are ready.

## Clock Model And Control Flow
The parent model is built from external DT-supplied parents: common PLL XO, common PLL NSS 300 MHz, common PLL NSS 375 MHz, GCC GPLL0 auxiliary, and three UNIPHY RX/TX parent pairs. Parent maps select combinations appropriate for generic NSS roots and for each port's RX/TX path.

The RCG set covers CE, NSS configuration, EIP BFDCD, PPE, and port1/port2/port3 RX and TX sources. Port RX/TX source clocks use two supported rate configurations, 25 MHz and 125 MHz, with separate RX/TX parent selections. Divider clocks sit after the port RCGs, and XGMAC PTP reference divider clocks provide per-MAC PTP timing sources.

Branch clocks expose CE APB/AXI, debug, EIP, NSS CSR, NSSNOC CE/EIP/NSS CSR/PPE/PPE CFG, three MAC clocks, three port RX/TX clocks, PPE eDMA and switch clocks, UNIPHY port RX/TX clocks, and XGMAC0-2 PTP reference clocks. Most branches set `CLK_SET_RATE_PARENT`, which lets Ethernet, PPE, and NSS consumers vote rates through branches to their RCGs or dividers.

## State And Persistence Behavior
The register map is 32-bit, 4-byte-stride, fast I/O, with a maximum register offset of `0x800`. Runtime PM and the `"bus"` PM clock gate access to that register space during probe and suspend/resume. After registration, clock enable bits, RCG source/divider settings, divider settings, reset bits, and interconnect hardware clock votes persist in hardware registers.

The descriptor registers six hardware-backed interconnect links with an `icc_first_node_id` derived from `5424 * 2`. These entries connect NSSNOC masters and slaves to concrete branch clock IDs, so bandwidth votes can enable or scale the backing NSSNOC clocks rather than relying only on direct clock consumers.

## Dependencies And Integration Points
The driver depends on Linux CCF, runtime PM, PM clock support, interconnect provider support, regmap, Qualcomm common clock/reset helpers, and a device tree that supplies the NSSCC MMIO resource, `"bus"` clock, and all listed parent clocks in binding order. It integrates with networking drivers for NSS, PPE switch/eDMA, crypto/EIP, Ethernet MAC/UNIPHY/XGMAC PTP paths, reset-controller consumers, and interconnect consumers that vote NSSNOC bandwidth.

The platform match compatible is `qcom,ipq5424-nsscc`. The driver name is also set to `qcom,ipq5424-nsscc`, and the PM ops must remain wired so register access is only attempted while the bus clock is active.

## Risks And Edge Cases
The main risk is hardware table accuracy. Parent selector values, multi-frequency port configurations, divider widths, branch offsets, halt registers, and reset bits must match IPQ5424 NSSCC. A bad port parent or divider can produce link-speed-specific failures that only appear at 10/100/1000 mode transitions or PTP validation. Interconnect node IDs also need to remain unique and aligned with the bindings; collisions would misroute bandwidth votes.

Probe ordering depends on the `"bus"` PM clock. If DT omits or misnames it, `pm_clk_add()` fails and no NSS clocks are registered. If runtime PM usage changes, `qcom_cc_probe()` may touch registers while the bus is off. The `pm_runtime_put()` call after probe means later accesses rely on clock-framework and PM-clock integration rather than a permanently active bus.

## Test Signals
Probe should complete without `"Fail to enable runtime PM"`, `"Fail to create PM clock"`, `"Fail to add bus clock"`, or `"Fail to resume"` errors. Debugfs should show CE, PPE, NSSNOC, port, UNIPHY, and XGMAC clocks with expected parents and rates. Functional tests should cover Ethernet links on all three ports at supported speeds, PTP timestamp stability on XGMAC0-2, PPE/eDMA traffic, EIP/crypto traffic if available, runtime suspend/resume, and interconnect bandwidth votes that enable the mapped NSSNOC clocks. Reset tests should assert/deassert PPE, port, UNIPHY, CE, EIP, and XGMAC resets and verify the owning drivers recover.
