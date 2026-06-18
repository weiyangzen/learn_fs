# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/ethtool_common.c

## Purpose
`ethtool_common.c` implements shared ethtool handlers for the non-Falcon Solarflare `sfc` driver stack. It translates kernel ethtool operations into `struct efx_nic` state updates and NIC-type callbacks for driver identity, message level, self-tests, pause/FEC/link settings, software and hardware stats, RX classification, RSS indirection/hash configuration, reset, and optical module EEPROM queries.

## Important APIs, Types, and Functions
The file centers on `struct efx_sw_stat_desc`, `EFX_ETHTOOL_STAT()` descriptors, and the exported `efx_ethtool_*` functions declared in `ethtool_common.h`. Stats are built from NIC-type hardware stat callbacks, software counters in `struct efx_nic`, `struct efx_channel`, and `struct efx_tx_queue`, plus per-queue and PTP stats. Self-test reporting is kept consistent by `efx_ethtool_fill_self_tests()`, which is used for count, string, and data paths.

Link and PHY APIs include `efx_ethtool_get_link_ksettings()`, `efx_ethtool_set_link_ksettings()`, `efx_ethtool_get_fecparam()`, and `efx_ethtool_set_fecparam()`, all serialized with `efx->mac_lock` and delegated to MCDI PHY helpers. Flow-control APIs update `efx->wanted_fc` and `efx->link_advertising[0]`, then run MCDI port reconfiguration and MAC reconfiguration. RX classification APIs translate between `ethtool_rx_flow_spec` and `struct efx_filter_spec`; RSS APIs expose default and custom RSS contexts through `ethtool_rxfh_param` and `ethtool_rxfh_context`.

## Control Flow
Self-test flow allocates `struct efx_self_tests`, rejects inactive NIC state, opens the netdev if necessary, invokes `efx_selftest()`, closes the temporary open, fills the ethtool result array, and sets `ETH_TEST_FL_FAILED` on error. Stats flow takes `stats_lock` while reading hardware/software aggregate counters, releases it, then appends per TX/RX/XDP queues and PTP values in the same order used by the string/count routines.

RX NFC get paths switch on `info->cmd` to return rule count, one rule, or all rule IDs. Rule get maps an installed manual filter back into ethtool TCP/UDP IPv4/IPv6, user-IP, or Ethernet flow forms, adding `FLOW_EXT` for VLAN and `FLOW_RSS` plus `rss_context` when the filter carries RSS. Rule set validates location, queue/drop cookie, VLAN extensions, full-mask-only fields, and supported flow types before inserting a manual filter. RSS get/set pulls or pushes NIC RSS configuration; custom context create initializes default indirection/key when absent and then delegates to NIC-type context push.

## State and Persistence
The file does not own persistent storage; it mutates live driver state. Key fields include `msg_enable`, `wanted_fc`, `link_advertising[0]`, `rss_context.rx_indir_table`, `rss_context.rx_hash_key`, custom RSS context private IDs, and manual RX filters in the NIC filter table. `mac_lock` protects PHY/MAC and module EEPROM interactions, `stats_lock` protects stat snapshots, and filter operations rely on the type-specific safe filter callbacks.

## Dependencies and Integration Points
Dependencies include Linux ethtool/netdevice APIs, MCDI firmware/PHY helpers, NIC-type operation tables, `rx_common` RSS helpers, filter helpers, self-test structures, PTP stat helpers, and module EEPROM helpers. The exported functions are meant to be assembled into per-device `struct ethtool_ops` tables by higher-level driver files.

## Risks
String count, string generation, and data generation must remain exactly aligned or ethtool consumers will mislabel results. RX classifier translation only supports full masks for many fields; accepting partial masks would require hardware/filter support changes. RSS context operations depend on NIC-type support and use extack messages for unsupported custom contexts. Lock ordering around `mac_lock`, MCDI calls, and MAC reconfigure paths is important because these operations can sleep and interact with resets. The reset handler trusts `efx->type->map_reset_flags()` to clear/translate user flags correctly.

## Test Signals
Useful signals are successful `ethtool -i`, `-S`, `-t online/offline`, `-a/-A`, `--show-fec/--set-fec`, `-n/-N` classifier add/list/delete, `-x/-X` RSS indirection/key changes, custom RSS context netlink tests, and module EEPROM reads. Regression tests should compare `get_sset_count(ETH_SS_STATS/TEST)` with string/data array lengths and verify failure paths for unsupported masks, invalid queues, unsupported RSS contexts, and inactive NIC self-tests.
