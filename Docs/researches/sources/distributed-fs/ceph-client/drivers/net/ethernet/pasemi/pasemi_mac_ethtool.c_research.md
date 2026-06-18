# sources/distributed-fs/ceph-client/drivers/net/ethernet/pasemi/pasemi_mac_ethtool.c

Purpose: Provides ethtool support for the PaSemi MAC driver: message level, link query, ring occupancy, hardware/RMON statistics, strings, and PHY-backed link settings.

Important APIs and flow: `pasemi_mac_ethtool_get_msglevel()` and `pasemi_mac_ethtool_set_msglevel()` expose `mac->msg_enable`. `pasemi_mac_ethtool_get_ringparam()` reports static max pending values and current `RING_USED()` counts scaled to hardware descriptor units. `pasemi_mac_get_sset_count()`, `pasemi_mac_get_strings()`, and `pasemi_mac_get_ethtool_stats()` publish 33 stats: DMA RX drops plus 32 MAC RMON counters. `pasemi_mac_ethtool_ops` wires these to ethtool and delegates link ksettings to phylib.

State and persistence: Reads live DMA/MAC registers and in-memory ring pointers; it does not persist settings except for the debug message mask.

Dependencies and integration: Depends on `pasemi_mac.h`, PA Semi DMA register helpers, netdev ethtool APIs, and an attached PHY for link setting get/set operations.

Risks and test signals: `get_ringparam()` assumes `mac->tx` and `mac->rx` exist, so ethtool ring queries before open can dereference null private ring pointers. Stats string count must stay aligned with RMON reads. Test with interface down/up, PHY absent fallback, RMON counter reset on open, and unsupported string sets.
