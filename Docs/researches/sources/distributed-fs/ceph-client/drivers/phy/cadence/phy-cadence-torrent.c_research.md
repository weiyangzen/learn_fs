# sources/distributed-fs/ceph-client/drivers/phy/cadence/phy-cadence-torrent.c

## Purpose
This is the Cadence Torrent SD0801 PHY platform driver. It exposes a Generic PHY provider for a multi-lane, multi-protocol SerDes block used as DisplayPort, PCIe, SGMII, QSGMII, USB3, USXGMII, and XAUI. It also registers three output clocks for reference-clock routing: `refclk-driver`, `refclk-der`, and `refclk-rec`. The driver supports Cadence default hardware plus TI J721E and J7200 variants through different register-offset shifts and per-SoC register-value tables.

## Important APIs, types, and functions
The primary state is `struct cdns_torrent_phy`, which owns the MMIO bases, regmaps, reset controls, input clocks, reference-clock rates, lane instances, protocol bitmask, and variant `struct cdns_torrent_data`. Each child link is represented by `struct cdns_torrent_inst`, carrying master lane, protocol, lane count, link reset, and SSC mode. Static table types `cdns_reg_pairs`, `cdns_torrent_vals`, `cdns_torrent_vals_entry`, and `cdns_torrent_vals_table` encode hardware programming by `(refclk0, refclk1, link0, link1, ssc)` key. The Generic PHY hooks are `cdns_torrent_phy_init()`, `cdns_torrent_dp_configure()`, `cdns_torrent_phy_on()`, and `cdns_torrent_phy_off()`. Probe/removal and noirq PM are implemented by `cdns_torrent_phy_probe()`, `cdns_torrent_phy_remove()`, `cdns_torrent_phy_suspend_noirq()`, and `cdns_torrent_phy_resume_noirq()`.

## Control flow
Probe obtains match data, maps the SD0801 range, initializes regmaps/regmap fields, registers the clock provider, gets resets and clocks, detects `already_configured`, then walks child nodes named `phy`. It reads `reg`, `cdns,phy-type`, `cdns,num-lanes`, optional `cdns,ssc-mode`, and DP-only `cdns,max-bit-rate`, creates one Generic PHY per link, and registers the provider. Single-link init selects and writes table groups for the active protocol/refclk/SSC. Multi-link init resolves one or two protocol classes, special-cases two PCIe links as `TYPE_PCIE_ML`, writes matching tables, deasserts link resets, and releases the global reset. DisplayPort has extra control paths for initial PLL setup, lane changes, link-rate changes, and voltage/pre-emphasis programming.

## State and persistence behavior
Driver state records topology, protocols, refclk rates, clocks, resets, regmaps, and table data. Hardware state persists in PHY registers; `already_configured` avoids reprogramming firmware-initialized hardware. Suspend saves the refclk-driver parent, asserts resets, and disables clocks unless inheriting preconfigured state; resume restores the parent, reenables clocks/APB, and replays multi-link programming as needed.

## Dependencies and integration points
The driver uses platform devices, OF child nodes, reset controls, common clock framework, Generic PHY, regmap, Cadence/TI PHY bindings, and DP `phy_configure_opts_dp`. Match data covers `cdns,torrent-phy`, `ti,j721e-serdes-10g`, and `ti,j7200-serdes-10g`.

## Risks
Table coverage is the main risk: unsupported key combinations can skip programming groups, and correctness depends on exact DT protocol/refclk/SSC combinations. Lane overlap is not deeply validated beyond total lanes and DP lane counts. DP rate changes rely on tight PLL/readiness polling. Error and cleanup paths mix manual reset puts with device-managed resources. PM saves only driver-owned refclk mux state.

## Test signals
Test DT binding combinations, single and multi-link boot, DP link training at all rates/lane counts, PCIe/USB/network link bring-up on Cadence and TI variants, suspend/resume, invalid DT properties, and PLL/readiness timeout fault injection.
