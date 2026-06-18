# sources/distributed-fs/ceph-client/drivers/phy/cadence/cdns-dphy-rx.c

Purpose: Implements the Cadence MIPI D-PHY receiver driver used for CSI-2 style RX operation. It validates MIPI D-PHY options, programs RX band selection and power island timing, starts/stops the RX state machine, and waits for clock/data lanes to become ready.

Important APIs and types: `struct cdns_dphy_rx` holds MMIO base, device, and PHY handle. `struct cdns_dphy_rx_band` maps Mbps ranges to hardware band indices. `struct cdns_dphy_soc_data` carries SoC quirks; currently J721E SR1.0 marks `has_hw_cmn_rstb`. The PHY ops are `cdns_dphy_rx_power_on()`, `cdns_dphy_rx_power_off()`, `cdns_dphy_rx_configure()`, and `cdns_dphy_rx_validate()`.

Control flow: Probe maps one resource, creates a generic PHY, registers an OF provider, and enables runtime PM. Validation requires `PHY_MODE_MIPI_DPHY`, confirms the lane rate maps to a supported band, then calls `phy_mipi_dphy_config_validate()`. Configure optionally asserts common lane reset through the wrapper unless SoC matching says hardware owns it, checks one to four lanes, converts `hs_clk_rate` to DDR bit rate, writes left/right band controls, writes mandated data/clock power island values, and polls clock plus active data lane ready bits. Power-on writes `DPHY_CMN_SSM` with RX mode, bandgap timer, and state-machine enable; power-off clears it.

State and persistence: The driver has minimal software state. Hardware configuration persists in PCS/PMA/wrapper registers after `.configure()` and while the PHY remains powered. Lane readiness is observed synchronously; no cached configured flag is kept.

Dependencies and integration points: Uses Linux PHY, MIPI D-PHY validation helpers, OF platform probing, `readl_relaxed_poll_timeout()`, runtime PM, and `soc_device_match()` for TI J721E SR1.0 reset behavior. It binds `cdns,dphy-rx`.

Risks: The SoC condition `if (!soc || (soc_data && !soc_data->has_hw_cmn_rstb))` means unknown SoCs take software common reset; regressions are possible if another integration has hardware-managed reset but lacks socinfo. Unsupported rates return `-EOPNOTSUPP`; boundary behavior is strict against `max_rate`. Configure waits up to 100 ms per lane-ready poll, so failures can slow camera pipeline startup.

Test signals: Build with `CONFIG_PHY_CADENCE_DPHY_RX`, validate reject paths for wrong mode/rate/lane counts, CSI-2 capture at every supported lane count and representative rates, J721E SR1.0 reset behavior, lane-ready timeout logging, and suspend/runtime PM interactions from the consuming CSI host.
