<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-ipq806x.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-ipq806x.c

## Purpose
`dwmac-ipq806x.c` is the Qualcomm Atheros IPQ806x platform glue layer for the Synopsys stmmac Ethernet core. It translates IPQ806x device-tree resources into `plat_stmmacenet_data`, programs NSS common and QSGMII CSR registers for RGMII or SGMII operation, and adapts MAC clocks when link speed changes.

## Important APIs, Types, and Functions
- `struct ipq806x_gmac` stores the platform device, NSS common regmap, QSGMII regmap, GMAC id, core clock, and selected PHY mode.
- `ipq806x_gmac_of_parse()` reads `qcom,id`, `qcom,nss-common`, `qcom,qsgmii-csr`, and the `stmmaceth` clock.
- `ipq806x_gmac_set_speed()` chooses RGMII or SGMII dividers and temporarily gates RX/TX clocks while updating `NSS_COMMON_CLK_DIV0`.
- `ipq806x_gmac_configure_qsgmii_params()` and `ipq806x_gmac_configure_qsgmii_pcs_speed()` tune QSGMII PHY parameters and fixed-link speed forcing.
- `ipq806x_gmac_probe()` wires `set_clk_tx_rate`, FIFO sizes, `core_type`, and calls `stmmac_dvr_probe()`.

## Control Flow
Probe obtains stmmac MMIO/IRQ resources, parses common stmmac DT data, allocates private state, then parses IPQ806x-specific syscon and clock resources. It resets QSGMII calibration lock detect, writes per-GMAC NSS control bits for IFG, AXI low-power exit, interface selection, source clock selection, and clock gates, then performs SGMII-only QSGMII PHY/PCS setup. Runtime link speed changes enter through `plat_dat->set_clk_tx_rate`, which calls the divider programming path.

## State and Persistence
The driver keeps only per-device private state in `bsp_priv`. Persistent hardware state is in shared syscon/regmap registers for NSS clock gates/dividers/source selection, GMAC control, and QSGMII PCS/PHY tuning. There is no filesystem or firmware persistence.

## Dependencies and Integration Points
It depends on stmmac platform helpers, Linux clk, regmap/syscon, OF fixed-link parsing, and SoC revision matching. It integrates with `stmmac_pltfr_pm_ops`, `stmmac_dvr_probe()`, and stmmac speed callbacks. The OF binding is `qcom,ipq806x-gmac`.

## Risks and Edge Cases
- `qcom,id` must be 0..3; invalid IDs can shift clock bits into the wrong MAC lane.
- GMAC0 cannot use SGMII, and SGMII setup relies on a valid QSGMII CSR regmap.
- Unsupported speeds return `-EINVAL`; only 10/100/1000 are handled.
- Fixed-link nodes without a `speed` property make PCS speed forcing fail.
- Clock and syscon register writes are shared across NSS MACs, so mask precision matters.

## Test Signals
Useful tests include DT probe with each GMAC id, RGMII and SGMII mode bring-up, fixed-link 10/100/1000 operation, link-speed transitions checking `NSS_COMMON_CLK_DIV0`, suspend/resume through stmmac PM, and negative DT tests for missing syscon phandles, invalid id, unsupported PHY mode, and malformed fixed-link speed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-ipq806x.c -->
