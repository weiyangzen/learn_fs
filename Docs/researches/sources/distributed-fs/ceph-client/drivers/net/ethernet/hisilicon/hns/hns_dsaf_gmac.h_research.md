# sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns/hns_dsaf_gmac.h

## Purpose
`hns_dsaf_gmac.h` declares GMAC-specific enums and small configuration structures used by `hns_dsaf_gmac.c`. It captures the hardware's port-mode encoding, duplex encoding, port-mode snapshot fields, and register-dump size.

## Important APIs and Types
`enum hns_port_mode` maps hardware mode values for MII, RGMII, SGMII, GMII, and a 10GE SGMII-coded value. `enum hns_gmac_duplex_mdoe` defines half/full duplex values as read from GMAC hardware. `struct hns_gmac_port_mode_cfg` carries decoded register state: mode, max frame size, runt threshold, pad/CRC, autoneg, runt packet, and strip-pad settings. `ETH_GMAC_DUMP_NUM` defines the 96-register GMAC dump size.

## Control Flow
The header does not implement control flow. It supports GMAC info collection, where `hns_gmac_port_mode_get` fills `struct hns_gmac_port_mode_cfg` and `hns_gmac_get_info` translates it into generic `struct mac_info`.

## State and Persistence
No state is stored in this header. Its types describe volatile hardware configuration snapshots.

## Dependencies and Integration Points
It includes `hns_dsaf_mac.h`, so it depends on the generic MAC abstraction. It is private to the HNS DSAF driver and primarily included by `hns_dsaf_gmac.c`.

## Risks
The enum name `hns_gmac_duplex_mdoe` contains a typo but is consistently used. Hardware mode values must stay synchronized with register definitions in `hns_dsaf_reg.h`; otherwise speed reporting and link adjustment can drift from actual hardware encoding.

## Test Signals
Compile-time use by GMAC code, `ETH_GMAC_DUMP_NUM` matching the number of registers filled in `hns_gmac_get_regs`, and correct speed/duplex reporting from ethtool are the main signals.
