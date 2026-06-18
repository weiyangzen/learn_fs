# sources/distributed-fs/ceph-client/drivers/net/ethernet/google/gve/gve_ethtool.c

## Purpose

`gve_ethtool.c` exposes driver diagnostics and reconfiguration through `struct ethtool_ops`: driver info, message level, string/stat tables, channels, ring parameters, private flags, link speed, interrupt coalescing, RX flow classification, RSS, reset, tunables, and timestamp capabilities.

## Important APIs, types, and functions

- `gve_get_strings`, `gve_get_sset_count`, `gve_get_ethtool_stats`: define and populate main, per-RX, per-TX, NIC, XDP, and adminq stats.
- `gve_get_channels`, `gve_set_channels`: read and adjust RX/TX queue counts with XDP constraints and optional RSS reset.
- `gve_get_ringparam`, `gve_set_ringparam`: report descriptor counts, RX buffer length, and TCP data split; apply live changes through `gve_adjust_config()`.
- `gve_set_ring_sizes_config`, `gve_validate_req_ring_size`: enforce supported power-of-two ring sizes and device support for ring-size modification.
- `gve_get_tunable`, `gve_set_tunable`: expose `ETHTOOL_RX_COPYBREAK`.
- `gve_get_priv_flags`, `gve_set_priv_flags`: manage the `report-stats` flag and timer/report buffer clearing.
- `gve_get_coalesce`, `gve_set_coalesce`: DQO-only interrupt coalescing; writes existing notify blocks when values change.
- `gve_set_rxnfc`, `gve_get_rxnfc`: integrate ntuple flow-rule add/delete/query through `gve_flow_rule.c` and adminq.
- `gve_get_rxfh`, `gve_set_rxfh`: RSS key/indirection table access, optionally using the local cache.
- `gve_get_ts_info`: reports hardware RX timestamping and PHC index when the clock path is enabled.

## Control flow and state

Stats collection starts by aggregating per-ring counters under `u64_stats` retry loops, then maps NIC-reported stat records from the DMA stats report by queue id. Queue/ring changes create allocation configs from current state and either adjust live queues or store values for the next open. Private `report-stats` state lives in `priv->ethtool_flags`, the report timer, and the coherent stats-report buffer. RSS state may be cached in `priv->rss_config` and synchronized through adminq.

## Dependencies and integration points

This file depends heavily on `gve_main.c` for `gve_adjust_config()`, `gve_adjust_queues()`, `gve_set_rx_buf_len_config()`, `gve_set_hsplit_config()`, reset, and queue state helpers. It uses adminq for link speed, RSS, stats, and flow-rule operations, DQO helpers for coalescing, and kernel ethtool/netlink extack APIs for validation feedback.

## Risks and test signals

Risks include stats-string ordering mismatches, incorrect NIC stats indexing when queues are stopped, live reconfiguration failures leaving queues down, XDP/channel incompatibilities, RSS cache divergence, and coalescing writes to inactive notify blocks. Test signals include `ethtool -S` count/name alignment, channel/ring resize while up and down, XDP-loaded queue resize rejection, ntuple add/list/delete, RSS get/set round trips, `ethtool --reset`, coalescing on DQO versus `-EOPNOTSUPP` on GQI, and timestamp info with/without PTP support.
