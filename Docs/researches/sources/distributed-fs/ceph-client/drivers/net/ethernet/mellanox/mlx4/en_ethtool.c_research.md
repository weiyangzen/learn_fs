# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx4/en_ethtool.c

## Purpose
Implements the `ethtool_ops` surface for the mlx4 Ethernet driver. It exposes driver and firmware identity, Wake-on-LAN, statistics strings and values, self-tests, link mode query/set, interrupt coalescing, pause/PFC configuration, ring sizes, RSS hash settings, ntuple flow steering, channel counts, timestamp capabilities, private flags, TX copybreak, module EEPROM access, and physical identify/beacon control.

## Important APIs, Types, and Functions
The exported integration point is `mlx4_en_ethtool_ops`; `mlx4_en_moderation_update` is also used by netdev reconfiguration paths. Link support centers on `mlx4_en_get_link_ksettings`, `mlx4_en_set_link_ksettings`, `mlx4_en_init_ptys2ethtool_map`, `ptys2ethtool_update_link_modes`, and `ethtool2ptys_link_modes`. Stats use `main_strings`, `mlx4_en_get_sset_count`, `mlx4_en_get_strings`, `mlx4_en_get_ethtool_stats`, and the local `bitmap_iterator` over `priv->stats_bitmap`. Flow steering uses `mlx4_en_validate_flow`, `mlx4_en_ethtool_to_net_trans_rule`, `mlx4_en_flow_replace`, `mlx4_en_flow_detach`, and cached `priv->ethtool_rules`. Reconfiguration APIs include coalesce, pause, ringparam, RXFH, channels, private flags, tunables, and module EEPROM helpers.

## Control Flow
Simple getters read cached state from `mlx4_en_priv`, `mlx4_en_dev`, and hardware capability fields. Link getters first call `mlx4_en_QUERY_PORT`, then prefer the PTYS register path when firmware supports Ethernet protocol control, falling back to a default transceiver mapping. Link setting queries PTYS, validates duplex/autoneg/speed/advertisement, writes the new admin protocol mask, then restarts the port under `state_lock` if it is up. Ring, channel, RXFH, and selected feature changes allocate a temporary profile through netdev helpers, stop the port if active, replace resources, restart, and refresh moderation. Ntuple insertion converts ethtool flow specs into mlx4 flow specs, detaches any prior rule at the same location, attaches the new rule, and stores the firmware registration id.

## State and Persistence Behavior
Most settings are runtime state in `struct mlx4_en_priv`: message level, coalescing thresholds, adaptive RX moderation parameters, RSS key/hash function/ring count, profile ring sizes, pause/PFC bits, private flags, and cached flow rules. Hardware-persistent or firmware-owned state is modified through mlx4 commands and registers: WoL config, PTYS advertised link modes, port pause/PFC policy, CQ moderation, flow steering entries, PHV bit, module EEPROM reads, and port beacon duration. The file does not store durable configuration outside driver and firmware state.

## Dependencies and Integration Points
Depends on Linux ethtool, bitmap, netdevice, MII/link mode, IPv4 helpers, and mlx4 core command/register APIs. It integrates with `en_port.c` for port query and port configuration, `en_netdev.c` for resource reset/restart paths, `en_selftest.c` for test execution, the flow steering API for ntuple rules, and timestamp/PHC support exposed by the broader mlx4_en driver.

## Risks
Many ethtool setters restart live ports, so lock ordering around RTNL and `mdev->state_lock` is critical. Flow rule conversion accepts only restricted masks; loosening validation can create firmware rules that do not match Linux semantics. RSS indirection validation assumes evenly repeated ring ids and power-of-two sizes. RX timestamping conflicts with RX VLAN stripping, so reset paths must keep feature state coherent. Stats string count and stats value order must remain exactly aligned with `stats_bitmap` and per-ring counters.

## Test Signals
Useful tests include `ethtool -i`, `-S`, `--show-priv-flags`, `--set-priv-flags`, `-c/-C`, `-g/-G`, `-l/-L`, `-x/-X`, `-k/-K`, `--show-pause/--pause`, `--test online/offline`, WoL read/write, link speed/autoneg setting with PTYS-capable firmware, ntuple rule add/delete/list, timestamp info with and without PHC, module EEPROM reads for SFP/QSFP variants, beacon identify, and port restart coverage while traffic is running.
