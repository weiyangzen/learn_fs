<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/marvell-88x2222.c -->
# sources/distributed-fs/ceph-client/drivers/net/phy/marvell-88x2222.c

## Purpose
`marvell-88x2222.c` is the PHYLIB driver for the Marvell 88X2222 dual-port multi-speed Ethernet transceiver. It bridges an XAUI host-side interface to line-side 10GBASE-R, 1000BASE-X, or SGMII, supports SFP/PHY port integration, dynamically swaps line type based on advertised capabilities and link progress, and controls PMA transmitter power on suspend/resume.

## Important APIs, Types, And Functions
`struct mv2222_data` stores current line interface, a filtered supported-linkmode mask, and SFP link state. Important functions are `mv2222_probe()`, `mv2222_config_init()`, `mv2222_configure_serdes()`, `mv2222_attach_mii_port()`, `mv2222_config_aneg()`, `mv2222_setup_forced()`, `mv2222_swap_line_type()`, `mv2222_read_status()`, `mv2222_read_status_10g()`, `mv2222_read_status_1g()`, `mv2222_aneg_done()`, `mv2222_soft_reset()`, and TX enable/disable helpers.

## Control Flow
Probe seeds `phydev->supported` with fibre, twisted-pair, 10/100/1000, 1000BASE-X, 10G, pause, and autoneg modes, then allocates private state with no active line interface. Config init rejects any host interface except XAUI. When a PHY port configures MII/SerDes, `mv2222_configure_serdes()` stores the requested line interface, intersects PHY and port supported masks, writes the PCS host/line configuration, and tries to run autoneg under `phydev->lock`.

`config_aneg()` does nothing until a line interface is attached. Forced mode or 10GBASE-R uses `mv2222_setup_forced()`, which may swap from 10G to 1G/SGMII for lower forced speeds and programs SGMII speed bits before disabling AN. For 1G autoneg, it writes 1000BASE-X advertisement bits and enables AN. Status first requires PMA signal detect and, when an SFP bus exists, SFP link-up notification. Then it uses 10G PCS status or 1G/SGMII status. If autoneg/link does not complete within `AUTONEG_TIMEOUT` polls, it swaps between 10G and 1G-capable line types and restarts configuration.

## State And Persistence
Private state persists line interface, SFP link state, and the port-filtered capability mask. The 10G and 1G status functions each use a file-static `timeout`, shared across devices. Hardware state includes PCS configuration, port reset bits, PMA TX disable, 1GBX control/advertisement/status, and signal-detect status.

## Dependencies And Integration Points
The driver depends on PHYLIB, Marvell PHY IDs, Clause 45 MMD helpers, `phy_port` operations, SFP link notifications, and ethtool linkmode conversion helpers. It integrates with MACs that expose XAUI host connectivity and with pluggable/line-side ports that can request 10GBASE-R, 1000BASE-X, or SGMII.

## Risks
The static timeout counters are not per device and can cross-contaminate multiple transceivers. Dynamic line-type swapping can surprise users if supported masks are too broad or SFP link reporting is delayed. `mutex_trylock()` in SerDes configuration means autoneg may be skipped if the PHY lock is busy. SGMII forced speed selection depends on the filtered `priv->supported` mask and returns `-EINVAL` when no matching mode remains.

## Test Signals
Test XAUI-only host validation, SerDes enable/disable for 10GBASE-R/1000BASE-X/SGMII, SFP link-up/down gating, 10G forced link, 1G autoneg advertisement, SGMII forced 10/100/1000 speeds, line-type fallback after timeout, PMA TX disable/enable during suspend/resume, multi-device timeout behavior, and port capability filtering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/marvell-88x2222.c -->
