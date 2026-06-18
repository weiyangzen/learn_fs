# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnge/bnge_link.h

## Purpose
This header defines the driver's cached link-state structures, firmware-to-driver aliases for link speed, pause, autoneg, FEC, and signal mode, plus the link-management API exported to netdev, ethtool, and HWRM wrappers.

## Important APIs, Types, And Functions
Important types are `enum bnge_link_state`, `struct bnge_link_info`, and `struct bnge_ethtool_link_info`. Key macros include `BNGE_PHY_CFG_ABLE`, `BNGE_LINK_IS_UP`, `BNGE_AUTO_MODE`, speed constants for 50G through 800G, speed2 masks, FEC capability/enabled masks, and signal mode constants. Function declarations mirror the public functions in `bnge_link.c`.

## Control Flow
The header supports three flows: firmware query into `bnge_link_info`, ethtool request storage in `bnge_ethtool_link_info`, and HWRM PHY configuration construction from the requested state. Async events enter through `bnge_link_async_event_process`.

## State And Persistence
`bnge_link_info` caches current firmware state including PHY type, media, link status, active lanes, duplex, pause, autoneg mode, speed masks, module status, active FEC, full qcfg response copy, and retry timing. `bnge_ethtool_link_info` persists user-requested autoneg, signal mode, duplex, flow control, speed, advertising mask, and whether a forced link change is pending.

## Dependencies And Integration Points
It includes `<linux/ethtool.h>` and uses HSI constants from included driver headers. It is included by `bnge_netdev.h`, making link state part of the central netdev private structure.

## Risks
The structures are caches, not authoritative hardware state. Callers must refresh with HWRM qcfg/qcaps at the right times. Pause and speed autoneg are tracked separately in a bitmask, which makes partial-autoneg transitions easy to mishandle.

## Test Signals
Compile-time use checks declarations. Runtime test signals are ethtool reporting, link up/down carrier, pause changes, forced-speed settings, module warnings, and PHY retry behavior after failed open-time configuration.
