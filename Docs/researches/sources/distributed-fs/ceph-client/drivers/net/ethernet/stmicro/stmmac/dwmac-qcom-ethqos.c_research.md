<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-qcom-ethqos.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-qcom-ethqos.c

## Purpose
`dwmac-qcom-ethqos.c` is the Qualcomm ETHQOS glue driver for GMAC4-based SoCs. It configures RGMII IO macro registers, SGMII/2500BASE-X helper state, link clocks, optional SerDes PHY power, variant-specific register layouts, PTP clock rate, and queue features before binding the stmmac core.

## Important APIs, Types, and Functions
- `struct ethqos_emac_driver_data` describes reset defaults, loopback quirks, DMA width, link clock name, GMAC4 address layout, and SGMII loopback requirements.
- `struct qcom_ethqos` stores RGMII MMIO base, link clock, optional SerDes PHY, PHY mode, and selected variant flags.
- `ethqos_set_clk_tx_rate()` sets the link clock to twice the RGMII line clock.
- `ethqos_fix_mac_speed_rgmii()` restores POR values, initializes DLLs, waits for lock, and programs speed-specific RGMII macro fields.
- `ethqos_fix_mac_speed_sgmii()` handles SGMII clock divider and PCS in-band autonegotiation.
- `qcom_ethqos_serdes_powerup/powerdown()` and `ethqos_mac_finish_serdes()` integrate optional PHY framework SerDes control.
- `qcom_ethqos_probe()` assembles stmmac platform data and calls `devm_stmmac_pltfr_probe()`.

## Control Flow
Probe parses stmmac resources/DT, selects a speed-fix callback based on PHY mode, maps the named `rgmii` resource, loads variant data, obtains and enables the link clock, gets optional SerDes, pre-sets 1000 Mbps RGMII clocking and functional clock bits, then fills stmmac parameters such as CSR clock range, debug dump callback, PTP clock configuration, GMAC4 address offsets, PMT, TSO, DMA width, SerDes hooks, and per-queue TBS. Link changes invoke either the RGMII macro reinitialization path or the SGMII in-band path.

## State and Persistence
Per-device state is devm-managed. Hardware state includes RGMII IO macro registers, DLL configuration and lock state, SGMII loopback bit, link clock rate, SerDes power/mode, PCS autonegotiation, and optional PTP reference clock rate. No storage is persisted outside hardware registers.

## Dependencies and Integration Points
The driver depends on stmmac GMAC4 support, clk APIs, PHY framework, OF match data, phylink/PCS control through stmmac, and platform MMIO resources. Compatible strings include `qcom,qcs404-ethqos`, `qcom,sa8775p-ethqos`, `qcom,sc8280xp-ethqos`, and `qcom,sm8150-ethqos`.

## Risks and Edge Cases
- RGMII DLL lock polling logs errors but continues, so later link failures may be timing-related.
- `of_device_get_match_data()` is assumed non-NULL.
- SGMII loopback is conditionally required for some 2500BASE-X variants during clock enable.
- Different EMAC versions use different register defaults and address maps; wrong compatible can corrupt configuration.
- RGMII TX delay phase shift depends on whether PHY mode says the PHY supplies delay.

## Test Signals
Test RGMII 10/100/1000 on every compatible, SGMII and 2500BASE-X with SerDes mode setting, PTP clock rate update, suspend/resume clock re-enable, TSO/TBS queue behavior, and debug register dumps. Negative tests should cover unsupported PHY mode, missing `rgmii` resource, missing link clock, SerDes probe defer, and DLL timeout observation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-qcom-ethqos.c -->
