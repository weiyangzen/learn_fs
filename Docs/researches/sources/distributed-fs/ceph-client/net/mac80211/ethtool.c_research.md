<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/ethtool.c -->
# sources/distributed-fs/ceph-client/net/mac80211/ethtool.c

## Purpose
Provides mac80211's netdev `ethtool_ops` implementation. It exposes generic driver information through cfg80211, ring parameter get/set hooks through low-level driver operations, and a merged statistics view containing mac80211 station/survey counters plus driver-specific ethtool strings and stats.

## Important APIs, Types, and Functions
The exported integration point is `ieee80211_ethtool_ops`, installed by interface setup code as the default ethtool operations for mac80211 netdevs. `ieee80211_set_ringparam()` and `ieee80211_get_ringparam()` translate ethtool ring requests to `drv_set_ringparam()` and `drv_get_ringparam()` while holding the wiphy lock. `ieee80211_get_sset_count()`, `ieee80211_get_strings()`, and `ieee80211_get_stats()` combine the fixed `ieee80211_gstrings_sta_stats` names with driver-provided `drv_get_et_*()` data. `ieee80211_get_regs_len()` and `ieee80211_get_regs()` advertise no register dump but report the wiphy hardware version.

## Control Flow
Ring changes reject `rx_mini_pending` and `rx_jumbo_pending`, then call the driver with only TX/RX pending counts. Stats collection zeroes the fixed mac80211 section, locks the wiphy, and either resolves the managed BSSID station or iterates all local stations belonging to the netdev. For each station it fills packet/byte/retry/drop counters through `sta_set_sinfo()` and local `sta_info` fields. It then resolves the current channel from the link channel context or monitor channel, scans driver survey indexes with `drv_get_survey()` until the matching channel is found, fills channel/noise/time counters or `-1` sentinels, verifies the fixed length, and appends driver-specific ethtool stats after `STA_STATS_LEN`.

## State and Persistence
The file owns no durable state. It reads persistent mac80211 state from `ieee80211_local`, `ieee80211_sub_if_data`, `sta_info`, channel contexts, monitor configuration, and driver survey state. The fixed string table and `STA_STATS_LEN` define a stable ABI-like ordering for the mac80211 stats prefix.

## Dependencies and Integration Points
Depends on cfg80211 ethtool helpers, mac80211 private structures from `ieee80211_i.h`, station helpers from `sta_info.h`, and driver operation wrappers from `driver-ops.h`. It integrates with `iface.c` via `netdev_set_default_ethtool_ops()`, with low-level hardware drivers through `drv_get_ringparam()`, `drv_set_ringparam()`, `drv_get_et_sset_count()`, `drv_get_et_strings()`, `drv_get_et_stats()`, and `drv_get_survey()`, and with cfg80211 bitrate formatting through `cfg80211_calculate_bitrate()`.

## Risks
The fixed stats string order must stay synchronized with the data indexes, especially the survey tail length. Survey lookup is linear and treats any driver error before the matching channel as no survey data. Signal and noise values are cast into unsigned `u64` slots, so user space must understand ethtool's raw numeric representation. The non-station path repeatedly starts at index zero and accumulates multiple STAs into the same fixed fields, which is intentional but can surprise consumers expecting per-peer rows. Locking expectations depend on all station and driver helper calls being safe under the wiphy guard.

## Test Signals
Useful signals are `ethtool -S` output with the fixed mac80211 names followed by driver-specific names, ring parameter get/set error paths for mini/jumbo rings, station-mode stats against an associated BSSID, AP/IBSS stats aggregated over multiple peer STAs, monitor-only survey reporting, and driver survey failures producing channel zero and `-1` time/noise sentinels. Compile-time signal comes from `WARN_ON(i != STA_STATS_LEN)` catching drift between strings and data population.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/ethtool.c -->
