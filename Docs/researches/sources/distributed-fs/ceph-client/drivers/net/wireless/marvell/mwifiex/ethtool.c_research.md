# sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/mwifiex/ethtool.c

## Purpose
`ethtool.c` provides the mwifiex netdev ethtool operations for Wake-on-LAN reporting and configuration. It maps ethtool WOL flags to the driver's host-sleep condition bitmap stored on the adapter.

## Important APIs, types, and functions
`mwifiex_ethtool_get_wol()` fills `struct ethtool_wolinfo` with supported wake sources and currently configured options. `mwifiex_ethtool_set_wol()` validates requested options and updates `priv->adapter->hs_cfg.conditions`. `mwifiex_ethtool_ops` exposes these as `.get_wol` and `.set_wol`; `cfg80211.c` assigns this ops table to each allocated netdev.

## Control flow
Get flow reads little-endian `adapter->hs_cfg.conditions`, always reports support for unicast, multicast, broadcast, and PHY/MAC-event wake, then returns no enabled options if conditions are at the default value. Otherwise, individual host-sleep condition bits are translated to `WAKE_UCAST`, `WAKE_MCAST`, `WAKE_BCAST`, and `WAKE_PHY`.

Set flow rejects unsupported ethtool bits, builds a host-sleep condition bitmap from requested WOL flags, uses `HS_CFG_COND_DEF` when no options are requested, and stores the result back to the adapter in little-endian form. It does not directly send a firmware command; later host-sleep/WoWLAN paths consume the stored configuration.

## State and persistence behavior
The only persistent state update is `priv->adapter->hs_cfg.conditions`, lasting for the adapter lifetime and influencing future host-sleep configuration. No hardware command is issued here, so ethtool configuration is staged driver state until power-management code applies it.

## Dependencies and integration points
This file depends on `main.h` for `mwifiex_netdev_get_priv()` and host-sleep condition constants. It integrates with Linux ethtool through `struct ethtool_ops` and with netdev setup in `mwifiex_add_virtual_intf()`. Runtime effect is coupled to `cmdevt.c` host-sleep handling and cfg80211 suspend/WoWLAN flows.

## Risks and test signals
Risk is low but semantic: ethtool may report WOL support regardless of firmware/runtime readiness, and setting options only updates cached conditions. Endianness must remain consistent because `hs_cfg.conditions` is stored little-endian. Test signals include `ethtool -s wol`/`ethtool` get cycles for all flag combinations, unsupported flag rejection, suspend/resume wake behavior after ethtool configuration, and interaction with cfg80211 WoWLAN settings.
