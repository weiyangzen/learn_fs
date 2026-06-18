# sources/distributed-fs/ceph-client/drivers/net/ethernet/pensando/ionic/ionic_stats.c

Purpose: Provides the Ionic ethtool statistics group implementation. It defines ordered stat descriptors for LIF software counters, port hardware counters, TX queues, and RX queues, then exposes functions for ethtool string, count, and value retrieval through `ionic_stats_groups`.

Important APIs and functions: Descriptor arrays include `ionic_lif_stats_desc`, `ionic_port_stats_desc`, `ionic_tx_stats_desc`, and `ionic_rx_stats_desc`. `ionic_get_lif_stats()` aggregates per-queue software counters plus netdev `rtnl_link_stats64` error/drop counters. `ionic_sw_stats_get_count()` calculates total rows, adding extra hardware timestamp queues when present. `ionic_sw_stats_get_strings()` emits ethtool names in the same order values are read. `ionic_sw_stats_get_values()` copies aggregated LIF stats, little-endian port stats, TX queue stats, and RX queue stats. `ionic_stats_groups[]` exports the group interface.

Control flow: Count, strings, and values share one strict ordering: aggregate LIF stats, port stats, all normal TX queues, optional hwstamp TX queue, all normal RX queues, optional hwstamp RX queue. The value path first aggregates LIF stats from `lif->txqstats` and `lif->rxqstats`, calls `ionic_get_stats64()` for netdev error counters, then reads port stats from `lif->ionic->idev.port_info->stats`.

State and persistence behavior: This file does not own counters; it reads live in-memory queue statistics and device-shared port statistics. There is no persistence or reset logic here. The stat descriptors store byte offsets into target structures, so the ABI is the descriptor order plus ethtool string names.

Dependencies and integration points: Depends on ethtool string helpers, `ionic_lif`, queue stats structures, port stats layout, `ionic_get_stats64()`, and macros from `ionic_stats.h`. The exported group is consumed by Ionic ethtool code that iterates stats groups.

Risks: Descriptor order must stay aligned between names and values; adding a counter in one array changes ethtool output shape. Offset-based reads assume every descriptor names a `u64` or `__le64` field of the matching structure. Optional hwstamp queues can duplicate indices outside `real_num_tx_queues`, so consumers must accept variable counts.

Test signals: Validate `ethtool -S` count and names against values, with and without hardware timestamp queues, after TX/RX/XDP traffic. Exercise endian conversion of port stats and check that netdev drop/error counters map to the expected LIF software stat names.
