# sources/distributed-fs/ceph-client/drivers/net/ethernet/amazon/ena/ena_ethtool.c

## Purpose
`ena_ethtool.c` exposes ENA driver and device controls through ethtool: software/hardware statistics, link settings, interrupt coalescing, ring sizing and LLQ push-buffer length, RSS indirection/hash configuration, channel count, RX copybreak, driver info, and timestamping PHC index.

## Important APIs, Types, And Functions
Static statistic descriptors map names to offsets in `ena_stats_tx`, `ena_stats_rx`, `ena_stats_dev`, ENA admin queue stats, ENI metrics, and ENA SRD fields. `ena_get_sset_count()`, `ena_get_ethtool_stats()`, and `ena_get_ethtool_strings()` build the stats ABI. `ena_get_coalesce()`/`ena_set_coalesce()` wrap ENA interrupt moderation. `ena_get_ringparam()`/`ena_set_ringparam()` expose queue sizes and LLQ push length. RSS paths include `ena_get_rxfh()`, `ena_set_rxfh()`, `ena_get_rxfh_fields()`, `ena_set_rxfh_fields()`, and indirection table helpers. `ena_set_channels()` resizes combined queues and updates XDP feature flags. `ena_set_ethtool_ops()` installs the ops table.

## Control Flow, State, And Integration
Stats reads use `u64_stats_sync` to safely sample per-ring and adapter counters. Hardware metrics are conditional on admin capabilities: customer metrics take precedence over older ENI stats, and SRD info is appended when supported. Coalescing writes update ENA common moderation state and then per-ring cached moderation intervals. Ringparam changes are validated, rounded to powers of two, bounded by ENA minima, and handed to `ena_update_queue_params()`, which tears down and recreates queues. RSS writes update ENA common indirection/hash control tables. Channel changes call `ena_update_queue_count()` and account for XDP queue doubling requirements.

## Dependencies
This file depends on Linux ethtool/netlink APIs, PCI naming, PHC index helpers, XDP queue legality helpers, and many `ena_com_*` admin operations. It is tightly integrated with `ena_netdev.h` adapter/ring state.

## Risks And Test Signals
Risks include mismatched stat counts versus names, unsupported hardware metrics leaving holes, LLQ push-length changes requiring reset, RSS index conversion between ENA TX/RX queue numbering and combined ethtool numbering, and queue-count changes while XDP is active. Test signals include `ethtool -S`, `-c/-C`, `-g/-G`, `-l/-L`, `-x/-X`, RX hash field changes, PHC timestamp info, and XDP-on channel resize rejection.
