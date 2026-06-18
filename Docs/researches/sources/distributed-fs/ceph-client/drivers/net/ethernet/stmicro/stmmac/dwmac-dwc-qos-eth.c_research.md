# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-dwc-qos-eth.c

## Purpose
This glue driver supports Synopsys DWC Ethernet QoS v4.10 style bindings and related Tegra/Tesla variants. It prepares STMMAC platform data, AXI tuning, clocks, resets, Tegra PHY reset GPIO handling, Tegra pad calibration on speed changes, and variant remove hooks.

## Important APIs, Types, And Functions
- `dwc_eth_dwmac_config_dt()` allocates or fills `plat_dat->axi`, parses `snps,en-lpi`, read/write outstanding request limits, and burst map, then forces GMAC4, AAL, TSO, and PMT support.
- `dwc_qos_probe()` picks `phy_ref_clk` as platform clock.
- `struct tegra_eqos` stores device, register base, EQOS reset control, and PHY reset GPIO.
- `tegra_eqos_fix_speed()` calibrates Tegra pads for 100/1000 Mbps while holding the STMMAC MDIO lock; it disables calibration for 10 Mbps.
- `tegra_eqos_probe()` handles Tegra-specific TX clock, PHY reset GPIO pulse, MDIO reset suppression, EQOS reset assert/deassert, MAC speed callback, TX clock-rate callback, and flags for SPH disable, TX LPI clock behavior, and PHY WOL.
- `dwc_eth_dwmac_probe()` manually fills resources, enables all clocks, runs variant probe, applies common config, and calls `stmmac_dvr_probe()`.
- `dwc_eth_dwmac_remove()` calls `stmmac_dvr_remove()` and variant remove.

## Control Flow
The driver does not use `stmmac_get_platform_resources()` because it handles unnamed IRQ/MMIO directly. Probe gets IRQ and MMIO, parses DT, bulk-enables clocks, selects the STMMAC clock by variant name, runs optional variant setup, fills common QoS config, then probes the STMMAC core. Tegra speed changes call the calibration routine through `plat_dat->fix_mac_speed`.

## State And Persistence
Variant state is devm-managed and stored in `plat_dat->bsp_priv`. Hardware state includes EQOS reset, PHY reset GPIO value, auto-calibration registers, AXI config, and STMMAC platform flags. No disk state exists.

## Dependencies And Integration Points
Uses OF match strings `snps,dwc-qos-ethernet-4.10`, `nvidia,tegra186-eqos`, and `tesla,fsd-ethqos`; integrates with clock bulk APIs, reset controls, GPIO descriptors, STMMAC core, MDIO locking, and GMAC4 register definitions.

## Risks
- Tegra calibration polling has very short timeouts; marginal hardware can fail speed changes.
- The driver decrements explicit outstanding request properties, preserving legacy binding behavior but requiring valid nonzero DT values.
- Bulk clock enablement is devm-managed but variant remove must still undo non-devm reset/GPIO state.
- Manual resource setup may miss named IRQ behavior expected by other STMMAC platform helpers.

## Test Signals
Probe all compatible variants, validate clock names, Tegra PHY reset timing, 10/100/1000 speed changes with calibration logs, suspend/resume through `stmmac_pltfr_pm_ops`, WOL behavior, AXI register programming, and normal STMMAC traffic including TSO.
