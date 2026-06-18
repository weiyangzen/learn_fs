# sources/distributed-fs/ceph-client/drivers/net/phy/nxp-c45-tja11xx.c

## Purpose
This is the main NXP Clause 45 TJA1103/TJA1104/TJA1120/TJA1121 PHY driver. It handles PHY configuration, interface mode selection, RGMII delay setup, link interrupts, cable tests, SQI, ethtool stats, PTP hardware timestamping, PHC registration, external timestamp/perout GPIO functions, and optional MACsec integration.

## Important APIs, Types, and Functions
The central private type is `struct nxp_c45_phy` from the companion header, allocated in `nxp_c45_probe()` and stored in `phydev->priv`. Internal data tables use `struct nxp_c45_regmap`, `struct nxp_c45_phy_data`, `struct nxp_c45_reg_field`, `struct nxp_c45_hwts`, and `struct nxp_c45_phy_stats` to abstract register differences between TJA1103 and TJA1120 families.

Major functions include register-field helpers, PTP clock methods (`nxp_c45_ptp_gettimex64()`, `settime64`, `adjfine`, `adjtime`, `enable`), timestamp queue handling (`nxp_c45_txtstamp()`, `nxp_c45_rxtstamp()`, `nxp_c45_do_aux_work()`), PHY configuration (`nxp_c45_config_enable()`, `nxp_c45_set_phy_mode()`, `nxp_c45_config_init()`), interrupts (`nxp_c45_handle_interrupt()` plus TJA-specific NMI handlers), cable tests, SQI, stats, and probe/remove.

## Control Flow
Probe allocates and initializes private state, skb queues, mutexes, device-tree flags, PTP support when the hardware and kernel config allow it, and MACsec support when advertised by the PHY. Config-init enables global/port/PHY configuration, applies PMAPMD write-access and TJA1120 engineering-sample errata, enables automatic PHY config, validates and programs the selected host interface, disables autoneg, enables counters, initializes PTP, initializes MACsec, and starts operation.

PTP TX timestamping queues SKBs after parsing PTP headers and either waits for IRQs or schedules worker polling. Egress timestamp retrieval differs by family; TJA1120 has FIFO workarounds for engineering samples. RX timestamping queues incoming SKBs, reconstructs seconds from the current PHC time plus embedded timestamp bits, clears reserved header storage, and reinjects via `netif_rx()`. The auxiliary worker drains TX timestamps, RX timestamps, and optional external timestamp events.

Interrupt handling reads PHY link IRQ status, acknowledges link events and triggers phylib, drains egress timestamp IRQs, invokes TJA-specific NMI handlers, and delegates MACsec IRQ handling to the companion file. Cable tests enable test mode, start a vendor cable test, report ethtool pair-A result when valid, disable test mode, and restart operation.

## State and Persistence
State includes the PHC pointer, timestamp queues, PTP configuration, RGMII delays, external timestamp last value/index, hardware timestamp enable flags, and optional MACsec state. It persists for the driver lifetime and is cleaned up in `nxp_c45_remove()` by unregistering the PHC, purging queues, and removing MACsec state. Hardware registers store PTP time, event filters, GPIO pin mux, counters, interface mode, delays, and cable-test state.

## Dependencies and Integration Points
The driver integrates with phylib, `mii_timestamper`, PTP clock kernel APIs, network hardware timestamping APIs, ethtool stats/cable/SQI, device tree properties, generic Clause 45 helpers, and the MACsec companion through `nxp-c45-tja11xx.h`. PHY variants are split by matching MACsec ability so the same PHY IDs register separate no-MACsec and MACsec-capable driver entries.

## Risks
PTP timestamp reconstruction uses truncated hardware seconds and current PHC time, so long delays or queue stalls can misassociate seconds. SKB queue lifetime must be correct across remove and timestamp configuration changes. Errata sequences use magic registers and must be constrained to the right silicon. Interface mode validation depends on hardware ability bits. PTP/MACsec/link interrupt sharing increases risk of missed acknowledgements. RGMII delay range enforcement can reject boards with invalid DT values.

## Test Signals
Test probe for TJA1103/TJA1104/TJA1120/TJA1121 with and without MACsec, all supported host interface modes, RGMII delay DT properties, PHC registration and time adjustments, TX/RX hardware timestamping under IRQ and polling, external timestamp and PPS GPIO functions, cable test results, SQI reads, stats reads, link IRQs, suspend/resume, TJA1120 link-recovery workaround, and MACsec interrupt coexistence.
