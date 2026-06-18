<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/icplus.c -->
# sources/distributed-fs/ceph-client/drivers/net/phy/icplus.c

## Purpose
`icplus.c` supports ICPlus IP175C, IP1001, IP101A, and IP101G PHYs. It covers an embedded switch-style IP175C path, IP1001 gigabit RGMII delay and power saving setup, IP101A/G interrupt and MDIX handling, IP101G hardware counters, and package-specific pin mux selection for IP101GR.

## Important APIs, Types, And Functions
Private state is `struct ip101a_g_phy_priv`, containing the selected RXER/INTR32 mode and accumulated IP101G stats. `struct ip101g_hw_stat` maps stat names to pages. Important functions include `ip175c_config_init()`, `ip1001_config_init()`, `ip101a_g_probe()`, `ip101a_g_config_intr_pin()`, `ip101a_g_read_status()`, `ip101a_g_config_mdix()`, interrupt callbacks, IP101A/G page helpers and match functions, and IP101G stats callbacks.

## Control Flow
IP175C initialization performs a one-time module-static full reset sequence across MDIO addresses 29/30 and switch ports 0-4, then treats non-WAN ports as always-running 100 Mbps full-duplex links. IP1001 enables auto power saving and sets RX/TX clock phase bits according to RGMII interface mode.

IP101A/G probe parses `icplus,select-rx-error` and `icplus,select-interrupt`, rejecting the conflicting combination. Init enables APS for IP101A or enables/clear-on-read counters for IP101G, then applies the optional INTR32 pin mux through paged register access. Status calls `genphy_read_status()`, reads MDIX control/status from the default page, and updates `phydev->mdix_ctrl`/`mdix`. Autoneg first programs forced/auto MDIX and then delegates to generic autoneg.

IP101A and IP101G share a PHY ID. Matching distinguishes them by probing whether the page select register behaves like IP101G. IP101A fakes page operations to let shared paged helper code work.

## State And Persistence
IP175C has a file-static `full_reset_performed` flag shared across all devices. IP101A/G private state persists pin selection and accumulated stats. Hardware state includes page registers, interrupt masks, MDIX control, APS mode, counters, and RGMII delay bits.

## Dependencies And Integration Points
The file depends on PHYLIB, device property APIs, ethtool stats helpers, paged PHY register helpers, and netdev carrier operations for IP175C switch ports. It integrates with board properties for IP101GR pin selection and with MACs via RGMII delay modes and MDIX controls.

## Risks
One-time IP175C reset state is module-wide and assumes one shared switch reset is sufficient. IP101A/G ID disambiguation writes `0xffff` to the page register and restores it, which is necessary but risky on unexpected silicon. Paged register restore paths must always run to avoid leaving the wrong page selected. Hardware stats return `U64_MAX` on read errors, which callers must treat as invalid.

## Test Signals
Test IP175C WAN versus switch-port behavior, one-time reset across multiple ports, IP1001 RGMII delay modes, IP101A versus IP101G matching, conflicting pinmux DT properties, interrupt enable/disable and link/speed/duplex IRQs, forced MDI/MDIX/auto modes, IP101G stats accumulation and clear-on-read behavior, and page restore after injected errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/icplus.c -->
