# sources/distributed-fs/ceph-client/drivers/net/phy/nxp-c45-tja11xx.h

## Purpose
This header shares private state and MACsec integration declarations between the NXP Clause 45 TJA11xx core driver and its MACsec companion. It also provides no-op MACsec stubs when `CONFIG_MACSEC` is disabled.

## Important APIs, Types, and Functions
The key type is `struct nxp_c45_phy`, which stores variant data, `phy_device`, `mii_timestamper`, PTP clock and clock info, TX/RX timestamp skb queues, PTP mutex, timestamping mode flags, RGMII delays, external timestamp state, optional `struct nxp_c45_macsec *`, and flags. The shared register define is `VEND1_PORT_FUNC_ENABLES`.

The header declares or stubs `nxp_c45_macsec_config_init()`, `nxp_c45_macsec_probe()`, `nxp_c45_macsec_remove()`, and `nxp_c45_handle_macsec_interrupt()`.

## Control Flow
The core driver includes this header, allocates `struct nxp_c45_phy`, and calls the MACsec functions unconditionally. Build-time stubs make those calls compile to successful no-ops when MACsec is unavailable, keeping the main driver free from repeated preprocessor branches.

## State and Persistence
The struct defines all software state that persists across NXP C45 callbacks. It is allocated with device-managed memory during probe. PTP queues and clock registration are explicitly initialized and cleaned up by the core driver; the MACsec pointer is populated only when hardware and kernel config support it.

## Dependencies and Integration Points
The header depends on PTP clock kernel types, phylib types from includers, skb queue types, and MACsec configuration symbols. It is the narrow integration contract between `nxp-c45-tja11xx.c` and `nxp-c45-tja11xx-macsec.c`.

## Risks
Because this is a private shared header, layout changes affect both core and MACsec files. The unconditional no-op stubs mean callers must not assume MACsec state exists after a successful stubbed probe/config-init. The PTP/MACsec fields concentrate multiple subsystems in one private struct, so lifetime ordering is important.

## Test Signals
Build-test with `CONFIG_MACSEC=y/m/n`, `CONFIG_PTP_1588_CLOCK` and `CONFIG_NETWORK_PHY_TIMESTAMPING` combinations, plus runtime probe/remove with and without MACsec ability.
