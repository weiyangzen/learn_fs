# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/netdevsim/ethtool-pause.sh

Purpose: Tests pause-frame statistics reporting through ethtool JSON on netdevsim.

Important APIs/functions: Sources `ethtool-common.sh`; requires ethtool `--include-statistics` support; creates `NSIM_NETDEV`; toggles debugfs `ethtool/pause/report_stats_tx` and `report_stats_rx`; reads `ethtool --json -a` and `ethtool -I --json -a` with `jq`.

Control flow: The script disables both stats in debugfs and verifies normal JSON reports `statistics: null` while include-statistics reports `{}`. It enables Tx stats and checks one stat with `tx_pause_frames == 2`, then enables Rx stats and checks both `rx_pause_frames == 1` and `tx_pause_frames == 2`.

State and persistence: Mutates only temporary netdevsim debugfs flags controlling pause stat reporting. The shared cleanup path removes the simulated device.

Dependencies and integration: Requires ethtool pause support and netdevsim pause ops. It provides narrower command-line coverage than `stats.py`, which checks standard pause statistics over netlink.

Risks: Depends on ethtool JSON and `-I` semantics. Expected counter values are netdevsim constants. It does not test changing pause configuration, only statistics visibility.

Test signals: PASS means statistics are absent without include-statistics, empty when disabled with include-statistics, and populated with the expected Tx/Rx counters when debugfs reporting flags are enabled.
