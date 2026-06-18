# sources/distributed-fs/ceph-client/drivers/net/ethernet/microsoft/mana/mana_ethtool.c

## Purpose
`mana_ethtool.c` implements ethtool operations for MANA Ethernet devices. It exposes driver, host-controller, PHY, RX queue, and TX queue statistics; RSS key and indirection table access; channel count changes; RX CQE coalescing controls; ring-size controls; and link settings.

## Important APIs, Types, And Functions
The exported object is `const struct ethtool_ops mana_ethtool_ops`. Local descriptor arrays map ethtool stat names to offsets in `struct mana_ethtool_stats`, `struct mana_ethtool_hc_stats`, and `struct mana_ethtool_phy_stats`. Major callbacks include `mana_get_sset_count`, `mana_get_strings`, `mana_get_ethtool_stats`, `mana_get_rxfh`, `mana_set_rxfh`, `mana_get_channels`, `mana_set_channels`, `mana_get_coalesce`, `mana_set_coalesce`, `mana_get_ringparam`, `mana_set_ringparam`, and `mana_get_link_ksettings`.

## Control Flow
Stats collection returns early when the port is down. When up, `mana_get_ethtool_stats` first refreshes PHY stats through `mana_query_phy_stats`, copies global software and hardware counters through descriptor offsets, then reads RX/TX per-queue counters under `u64_stats_fetch_begin/retry`. RSS reads copy the current indirection table and hash key; RSS writes validate Toeplitz-only hashing, clone current state, update requested key/table fields, call `mana_config_rss`, and restore the saved values if hardware programming fails. Channel, ring, and MTU-affecting operations preallocate RX buffers before calling `mana_detach`, mutate the relevant queue count or ring sizes, call `mana_attach`, and roll back software values if attach fails. Coalescing toggles `cqe_coalescing_enable` and reprograms RSS/steering while the port is up.

## State And Persistence
The file does not persist data outside memory. It reads and mutates `mana_port_context` fields such as `num_queues`, `max_queues`, `indir_table`, `hashkey`, `cqe_coalescing_enable`, `cqe_coalescing_timeout_ns`, `rx_queue_size`, and `tx_queue_size`. It also surfaces counters owned by RX/TX queues and MANA hardware-stat snapshots. State changes are applied through `mana_detach`/`mana_attach`, meaning hardware and queue state is rebuilt rather than patched in place for channel and ring changes.

## Dependencies And Integration Points
This file depends on `mana_en.c` for RSS programming, PHY/link queries, queue preallocation, detach, and attach. It integrates with the kernel ethtool core, netlink extended ACK strings for invalid parameters, and MANA hardware command helpers.

## Risks
Key risks are mismatches between stat string count and data fill order, insufficient rollback after RSS or attach failures, queue/ring changes while traffic is active, and stale PHY stats if hardware commands fail silently. `mana_set_ringparam` rounds requested counts to powers of two, so user-visible behavior should be tested. `mana_set_channels` trusts the requested combined count after preallocation and depends on ethtool core validation for min/max bounds.

## Test Signals
Run `ethtool -S`, `ethtool -x/-X`, `ethtool -l/-L`, `ethtool -c/-C`, `ethtool -g/-G`, and `ethtool -k` while traffic is flowing and while the port is down. Regression tests should verify RSS rollback on invalid table entries, coalescing frame limits, ring min validation, stat count stability, and successful detach/attach recovery after channel or ring changes.
