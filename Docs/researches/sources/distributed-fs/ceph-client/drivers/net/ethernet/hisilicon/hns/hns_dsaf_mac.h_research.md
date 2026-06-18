# sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns/hns_dsaf_mac.h

## Purpose
`hns_dsaf_mac.h` declares the shared MAC abstraction used by DSAF, GMAC, XGMAC, and the AE adapter. It defines MAC modes, supported capabilities, MTU limits, address classification helpers, port state, backend callback shape, stats layout, and exported MAC helper APIs.

## Important APIs and Types
Key types are `struct hns_mac_cb`, the persistent per-port control block; `struct mac_driver`, the backend callback table; `struct mac_params`, initialization input for GMAC/XGMAC backends; `struct mac_info`, generic link/pause/mode snapshot; `struct mac_hw_stats`, shared ethtool counter storage; and `struct mac_stats_string`, mapping stat names to offsets. The header declares factories `hns_gmac_config` and `hns_xgmac_config` plus the public MAC service functions consumed by the AE adapter.

## Control Flow
The header is declarative. Its callback table shows the control path: shared MAC code creates a backend driver, then uses callbacks for reset/init, enable/disable, address setting, link adjustment, loopback, MTU, pause/autoneg, stats, register dumps, promiscuous mode, and FIFO drain.

## State and Persistence
`struct hns_mac_cb` is the main state container. It persists firmware-node pointers, MMIO/regmap handles, CPLD LED state, per-VM address indexes, link/speed/duplex/MTU/pause values, media and PHY data, hardware stats, and the backend pointer. This state lives for the platform device lifetime.

## Dependencies and Integration Points
The header depends on Linux VLAN, PHY, regmap, and kernel networking types, and it includes `hns_dsaf_main.h`, forming a tight mutual dependency between DSAF and MAC types. It is included by GMAC/XGMAC implementations, misc reset/LED code, DSAF main, and AE adaptation.

## Risks
The header contains many hardware constants and address macros whose correctness is assumed throughout the driver. `MAC_IS_*` macros evaluate pointer expressions directly and should only be called with valid 6-byte Ethernet addresses. The mutual include relationship with `hns_dsaf_main.h` is fragile and relies on include guards and forward declarations.

## Test Signals
Compile checks for callback-table completeness, ethtool stat count/name alignment through `MAC_STATS_FIELD_OFF`, MTU-limit behavior using `MAC_MIN_MTU`, `MAC_MAX_MTU`, and `MAC_MAX_MTU_V2`, and capability exposure for GMAC versus XGMAC ports are the main signals.
