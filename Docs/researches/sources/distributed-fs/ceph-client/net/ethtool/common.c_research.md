# sources/distributed-fs/ceph-client/net/ethtool/common.c

## Purpose
This shared ethtool implementation file provides string tables, link-mode metadata, legacy conversion helpers, channel/RSS validation, timestamp/PHC discovery, PHY ops registration, RSS context lifecycle helpers, RSS indirection resize helpers, and link-medium parsing used by both ioctl and netlink ethtool paths.

## Important APIs, Types, And Functions
It exports name tables for netdev features, RSS hash functions, tunables, PHY tunables, link modes, debug classes, Wake-on-LAN modes, timestamping names, timestamp flags, and UDP tunnel types. Important functions include `convert_legacy_settings_to_link_ksettings()`, `__ethtool_get_link()`, `ethtool_get_rx_ring_count()`, `ethtool_check_max_channel()`, `ethtool_rxfh_ctx_alloc()`, `ethtool_check_rss_ctx_busy()`, `ethtool_rxfh_config_is_sym()`, `ethtool_check_ops()`, `ethtool_ringparam_get_cfg()`, timestamp/PHC helpers, `ethtool_set_ethtool_phy_ops()`, `ethtool_params_from_link_mode()`, `ethtool_forced_speed_maps_init()`, `ethtool_rxfh_context_lost()`, `netif_is_rxfh_configured()`, `ethtool_rxfh_indir_lost()`, RSS resize helpers, and `ethtool_str_to_medium()`.

## Control Flow
Static tables are initialized at build time with `static_assert()` coverage against enum sizes. Channel validation queries ntuple rules, RSS contexts, default RSS indirection, and memory-provider queue requirements before allowing channel reductions. Timestamp discovery prefers an explicit hwtstamp provider when present, otherwise checks default PHY timestamping and then netdev callbacks, always adding software timestamping capabilities. RSS context loss erases xarray entries and notifies userspace. RSS resize validation checks user-configured patterns can be shrunk or expanded without data loss, then resize helpers replicate existing patterns and notify contexts.

## State, Persistence, And Dependencies
The file mutates in-memory netdevice ethtool state: RSS context xarrays, default RSS user-size markers, registered global PHY ops pointer, and caller-provided config structs. It depends on netdevice internals, PHY topology, PTP clocks, hwtstamp providers, xarray, mutex/RCU locking, netdev queue/memory provider helpers, and ethtool netlink notifications.

## Integration Points
Feature-specific ethtool files depend on the exported string tables and validation helpers. Drivers rely on exported RSS and link-mode utilities. The legacy ioctl path and netlink path both use these shared helpers to keep behavior aligned.

## Risks
String table and link-mode metadata must stay in enum order or userspace names and bitsets break. Channel validation must not miss active RSS/ntuple/memory-provider references when reducing queues. RSS resize logic assumes periodic tables for safe shrinking. Timestamp provider selection must avoid reporting the wrong PHC source. Locking requirements around RTNL and `rss_lock` are enforced with warnings but still depend on callers.

## Test Signals
Signals include static assertion build failures after enum changes, channel reductions blocked by RSS/ntuple/memory provider state, timestamp info tests for netdev vs PHY vs explicit providers, RSS context loss notifications, RSS resize can/cannot cases for periodic and non-periodic tables, and link-medium string parsing.
