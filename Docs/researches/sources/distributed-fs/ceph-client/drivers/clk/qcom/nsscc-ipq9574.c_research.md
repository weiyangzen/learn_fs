# sources/distributed-fs/ceph-client/drivers/clk/qcom/nsscc-ipq9574.c

## Purpose
`nsscc-ipq9574.c` implements the Qualcomm NSS clock controller for IPQ9574. It is a larger networking clock provider than the IPQ5424 variant, covering CE, CLC, crypto/EIP, HAQ, IMEM, NSS CSR, NSSNOC, PPE, six Ethernet ports, six UNIPHY RX/TX paths, six XGMAC PTP reference paths, and four UBI32 core complexes. It also exposes a local UBI32 Huayra alpha PLL and hardware-backed interconnect clock nodes. IDs come from the IPQ9574 clock, reset, and interconnect DT binding headers.

## Important APIs, Types, And Functions
Key types include `clk_alpha_pll`, `clk_alpha_pll_postdiv`, `alpha_pll_config`, `clk_rcg2`, `clk_regmap_div`, `clk_branch`, `freq_tbl`, `freq_conf`, `freq_multi_tbl`, `qcom_reset_map`, `qcom_icc_hws_data`, `regmap_config`, and `qcom_cc_desc`. The local `ubi32_pll_main` uses `CLK_ALPHA_PLL_TYPE_NSS_HUAYRA`, `SUPPORTS_DYNAMIC_UPDATE`, and `clk_alpha_pll_huayra_ops`; `ubi32_pll` is a read-only postdivider exported as the usable PLL output.

`nss_cc_ipq9574_probe()` performs runtime PM setup, adds the `"bus"` PM clock, resumes the hardware, maps the controller with `qcom_cc_map()`, programs the UBI32 PLL using `clk_alpha_pll_configure()`, registers clocks/resets/interconnect nodes through `qcom_cc_really_probe()`, and releases the runtime PM reference. Runtime suspend/resume is delegated to `pm_clk_suspend` and `pm_clk_resume`, and driver sync state is `icc_sync_state`.

## Clock Model And Control Flow
The root parent model includes XO, bias PLL CC, bias PLL UBI NC, GCC GPLL0 auxiliary, the local UBI32 PLL output, and three UNIPHY RX/TX parent pairs. Parent maps are specialized for generic NSS roots, port roots, PPE/UBI roots, and PTP references.

RCGs define CE, configuration, CLC, crypto, HAQ, IMEM, internal configuration, PPE, UBI0-UBI3, UBI AXI, UBI NC AXI BFDCD, and port1-port6 RX/TX source clocks. Port 1 and 6 support 25/125 MHz style configurations; ports 5 adds a 312.5 MHz configuration for higher-speed operation; the source structures for ports 2-4 reuse the same base patterns with different offsets and parent maps. UBI RCGs select from the local UBI32 PLL and other NSS parents, with divider clocks for each UBI core.

Branch clocks expose the full hierarchy: CE, CLC, crypto/PPE, HAQ, IMEM, NSS CSR, NSSNOC mirrors, six MAC and port RX/TX branches, PPE switch/eDMA branches, many UBI32 AHB/AXI/core/intr/NC/UTCM branches, six UNIPHY port RX/TX branches, and XGMAC0-5 PTP reference branches. Most branches propagate rate changes upward with `CLK_SET_RATE_PARENT`, reflecting that consumers often control the backing RCG through the leaf clock they request.

## State And Persistence Behavior
The regmap is 32-bit, 4-byte-stride, fast I/O, with a maximum offset of `0x28a34`. Persistent state includes UBI32 PLL programming at `0x28000`, RCG command/source/divider registers, branch enable and halt state, divider registers, reset bits, aggregate bitmask resets, and interconnect hardware votes. Runtime PM gates access through the `"bus"` PM clock, so probe explicitly resumes before mapping and configuring the PLL.

The reset table is unusually rich. It includes block resets for CE/CLC/EIP/HAQ/IMEM/MAC/PPE/UBI/UNIPHY, individual ARES bits across grouped reset registers, UBI clamp enables, and aggregate bitmask resets such as `PPE_FULL_RESET`, `UNIPHY*_SOFT_RESET`, `UNIPHY_PORT*_ARES`, `NSSPORT*_RESET`, and `EDMA_HW_RESET`. These aggregate entries rely on `bitmask` rather than a single bit, giving reset consumers coarse-grained hardware sequences where needed.

## Dependencies And Integration Points
The driver depends on Linux CCF, runtime PM, PM clocks, interconnect provider support, regmap, Qualcomm alpha PLL, RCG, branch, divider, mux, reset, and common clock helpers. The device tree must provide compatible `qcom,ipq9574-nsscc`, a register resource, the `"bus"` clock, and parent clocks in binding order. Consumers are NSS/PPE networking drivers, Ethernet MAC and UNIPHY drivers, XGMAC PTP users, crypto/EIP and HAQ users, UBI32 firmware/core drivers, reset consumers, and interconnect clients voting NSSNOC bandwidth.

Interconnect integration exposes five NSSNOC hardware clock links: PPE, PPE CFG, NSS CSR, IMEM QSB, and IMEM AHB. The `icc_first_node_id` value is derived from `9574 * 2` to provide a unique base for the provider.

## Risks And Edge Cases
The highest risk areas are PLL configuration, reset aggregation, and port-rate tables. Incorrect UBI32 Huayra PLL parameters can break all UBI core clocks. Incorrect aggregate reset bitmasks can reset neighboring hardware unexpectedly or fail to reset all required lanes. Port 5 high-speed 312.5 MHz handling, six-port parent mapping, and XGMAC PTP dividers need per-port validation because failures can be speed-specific or only visible under timestamping tests.

Runtime PM ordering is also important. Mapping and PLL configuration are done while the device is resumed; removing that ordering can cause bus faults or ignored writes. Binding order matters for `.index` parent references. The interconnect node base must remain unique across providers, and the clock IDs referenced by `qcom_icc_hws_data` must stay synchronized with the clock table.

## Test Signals
Probe should show successful runtime PM setup, bus-clock acquisition, register mapping, UBI PLL programming, and common clock registration. Debugfs should show `ubi32_pll_main`, `ubi32_pll`, six port RX/TX trees, six XGMAC PTP references, and UBI32 branch clocks. Functional validation should cover all Ethernet ports at supported rates, PTP timestamping on XGMAC0-5, PPE/eDMA forwarding, crypto/HAQ/IMEM traffic, UBI firmware/core operation, runtime suspend/resume, and interconnect bandwidth votes. Reset validation should separately cover block resets, aggregate PPE/UNIPHY/NSSPORT resets, UBI clamp/reset controls, and EDMA reset recovery.
