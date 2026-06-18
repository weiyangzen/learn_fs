# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeon_ep/octep_ethtool.c Research

## Purpose
`octep_ethtool.c` provides ethtool support for the Octeon EP NIC driver. It reports driver identity, link state, global and per-queue statistics, supported/advertised link modes, link settings updates, and channel counts.

## Important APIs, Types, And Functions
The public entry point is `octep_set_ethtool_ops()`, which assigns `octep_ethtool_ops` to a netdev. Operations include `octep_get_drvinfo()`, `octep_get_strings()`, `octep_get_sset_count()`, `octep_get_ethtool_stats()`, `octep_get_link_ksettings()`, `octep_set_link_ksettings()`, and `octep_get_channels()`. Static string tables define global stats and per-Tx/per-Rx queue stat names. `OCTEP_SET_ETHTOOL_LINK_MODES_BITMAP` maps firmware Octeon link-mode bits to ethtool link-mode bits.

## Control Flow
Stats reporting builds ethtool string output for global counters and active queues, then fetches firmware interface stats through `octep_ctrl_net_get_if_stats()` and aggregates software per-queue stats from `oct->stats_iq[]` and `oct->stats_oq[]`. Link settings get flow fetches firmware link info, clears ethtool supported/advertising bitmaps, maps Octeon speed bits, sets autoneg and pause bits, reports fibre port, and returns speed/duplex only when carrier is up. Link settings set flow validates duplex, autoneg support, and advertising subset, maps ethtool advertised modes back to Octeon bits, sends new link info to firmware, and updates the cached `oct->link_info` on success. Channel reporting exposes maximum and active IO ring counts from config.

## State, Persistence, And Dependencies
State is read from `struct octep_device`: PCI device, config, queue stats, firmware stats caches, link info cache, and netdev carrier. Persistent link changes are delegated to firmware through `octep_ctrl_net_set_link_info()`. Dependencies include Linux ethtool APIs, PCI naming, netdev private data, Octeon config macros, firmware control-net APIs, and Octeon link-mode constants.

## Integration Points
Main netdev setup calls `octep_set_ethtool_ops()`. User space reaches these operations through `ethtool -i`, `-S`, `-k`-like stats consumers, `ethtool <dev>` link settings, and channel queries. Control-net firmware commands supply hardware stats and link information; queue datapath code supplies software queue counters.

## Risks
`octep_get_sset_count()` uses the active queue count, but `octep_get_ethtool_stats()` loops over `OCTEP_MAX_QUEUES` for per-queue stats, which can write more values than the string/count path exposes if active queues are less than the maximum. Firmware command errors from stats and link-info getters are ignored, so ethtool can report stale or zeroed cached values. Link-mode mapping in `octep_get_link_ksettings()` stores 64-bit firmware bitmaps in `u32`, truncating high bits if future modes use them. The set path compares `cmd->base.autoneg` to `link_info->autoneg`, but `link_info->autoneg` is a firmware bitfield, not just `AUTONEG_ENABLE/DISABLE`.

## Test Signals
Run `ethtool -i`, `ethtool -S`, link settings get/set, and channel queries with different active queue counts. Validate stats buffer sizing, firmware stats failure behavior, link mode mapping for all advertised speeds, autoneg and pause reporting, unsupported duplex rejection, advertising subset rejection, firmware link-info set failures, carrier up/down reporting, and high-bit link-mode preservation if new firmware modes are added.
