# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/ethtool_common.c

## Purpose
Implements shared Siena ethtool behavior: driver info, debug level, pause parameters, self-tests, stats/string sets, link settings, FEC parameters, RX classifier rules, RSS configuration, reset, and module EEPROM/info access.

## Important APIs and functions
`struct efx_sw_stat_desc` describes software stat sources. Public functions cover drvinfo, message level, pause, self-test, string counts/strings/stats, link ksettings, FEC, RX NFC, RX ring count, RSS hash fields/table/key get/set, ethtool reset, and module EEPROM/info. Internal helpers format tests, describe per-queue stats, and translate filters between ethtool flow specs and `efx_filter_spec`.

## Control flow
Self-test opens the netdev temporarily if needed, calls `efx_siena_selftest()`, closes if it opened it, and fills ethtool data. Stats pull hardware stats under lock, accumulate software/channel/TX stats, add per-queue and XDP stats, then PTP stats. RX classifier get/list/delete/insert operations validate masks and route through safe filter APIs. RSS get pulls hardware config; RSS set validates Toeplitz/no-change and pushes updated table/key.

## State and persistence behavior
Reads and mutates `msg_enable`, flow-control settings, netdev open state during tests, stats counters, manual filters, RSS context, reset state through reset call, and module EEPROM reads. No disk persistence.

## Dependencies
Depends on ethtool core, MCDI firmware helpers, PHY/link/FEC/module EEPROM helpers, filter APIs, PTP stats, RX/TX/channel structures, self-test, and NIC type callbacks.

## Risks
Offline self-tests disrupt traffic. Stats string counts must exactly match data ordering. Classifier masks are intentionally strict. Equal-priority filter insertion can replace existing entries. Pause parameter rollback can be partial if reconfigure fails after state changes.

## Test signals
Ettool self-test count/data alignment, stats alignment, pause/link/FEC get/set, classifier add/list/delete for supported flow types, RSS get/set, ethtool reset, and module EEPROM reads.
