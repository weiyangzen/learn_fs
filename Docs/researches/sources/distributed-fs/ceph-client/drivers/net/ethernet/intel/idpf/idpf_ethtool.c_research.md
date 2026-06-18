# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/idpf/idpf_ethtool.c

## Purpose
`idpf_ethtool.c` is the IDPF driver's ethtool integration layer. It exposes vport state to userspace for RSS, ntuple flow steering, queue/channel sizing, ring descriptor sizing, interrupt coalescing, statistics, link settings, and timestamping capabilities. It is deliberately thin on hardware programming: most user requests are validated here, cached into `idpf_vport_config->user_config`, and then pushed to firmware or hardware through virtchnl helpers or a soft reset.

## Important APIs, types, and functions
- `idpf_set_ethtool_ops()` installs `idpf_ethtool_ops` on the netdev.
- Flow steering: `idpf_get_rxnfc()`, `idpf_set_rxnfc()`, `idpf_add_flow_steer()`, `idpf_del_flow_steer()`, plus protocol builders `idpf_fsteer_fill_ipv4()`, `idpf_fsteer_fill_udp()`, and `idpf_fsteer_fill_tcp()`.
- RSS: `idpf_get_rxfh_key_size()`, `idpf_get_rxfh_indir_size()`, `idpf_get_rxfh()`, and `idpf_set_rxfh()` operate on cached `struct idpf_rss_data`.
- Queue and ring controls: `idpf_get_channels()`, `idpf_set_channels()`, `idpf_get_ringparam()`, and `idpf_set_ringparam()`.
- Statistics: `struct idpf_stats`, `IDPF_STAT`, queue/port statistic arrays, `idpf_get_strings()`, `idpf_get_sset_count()`, and `idpf_get_ethtool_stats()`.
- Coalescing: `idpf_find_rxq_vec()`, `idpf_find_txq_vec()`, `idpf_get_q_coalesce()`, `idpf_set_q_coalesce()`, `idpf_set_coalesce()`, and per-queue variants.
- Link and timestamp reporting: `idpf_get_link_ksettings()`, `idpf_get_ts_info()`, `idpf_get_ts_stats()`, and `idpf_get_timestamp_filters()`.

## Control flow
Flow steering requests enter via ethtool rxnfc. Get paths lock the vport control mutex, read `flow_steer_list` under `flow_steer_list_lock`, and return either counts, a specific saved `ethtool_rx_flow_spec`, or all rule locations. Insert validates unsupported flow extensions, sideband capabilities, rule count, queue index, and duplicate locations. It then builds a `virtchnl2_flow_rule_add_del` rule for TCP/UDP IPv4 and sends `VIRTCHNL2_OP_ADD_FLOW_RULE`; only after firmware success does it cache the ethtool spec in sorted list order. Delete sends `VIRTCHNL2_OP_DEL_FLOW_RULE` first and then removes the cached list entry.

RSS get/set reads and writes the cached RSS key and LUT in `user_config.rss_data`. `set_rxfh` accepts only Toeplitz or no-change hash function, stores new key/LUT values, and if the vport is up calls `idpf_config_rss()` so the running device observes the change. If RXHASH is disabled, `get_rxfh` reports zeroed indirection entries while preserving the cached configured LUT.

Queue count and descriptor changes are staged in `user_config` and applied through `idpf_initiate_soft_reset()`. `set_channels` rejects simultaneous dedicated RX and TX queues, validates the combined plus dedicated counts against `max_q`, updates requested TX/RX queue counts, and rolls back if the queue-change soft reset fails. `set_ringparam` enforces min descriptor counts, aligns requested counts to hardware multiples, updates RX buffer queue descriptor counts for split queues, updates header split state, and triggers a descriptor-change soft reset.

Statistics are a stable userspace ABI. The string count and ordering are based on maximum queue counts, not the currently allocated queues, to avoid size changes between ethtool string/count/data ioctl phases. Runtime stats collection locks the vport, requires `IDPF_VPORT_UP`, uses RCU to walk queues, folds per-queue software stats into port-level counters with `u64_stats_sync`, emits real queue stats where queues exist, and fills missing max-queue slots with zeros.

Coalesce get maps a queue index to the owning `idpf_q_vector` for split or single queue models and reads static or dynamic ITR state. Set paths reject static usec changes while adaptive mode is enabled, clamp to `IDPF_ITR_MAX`, round odd ITR values down to even values, update both the live q-vector and persistent `user_config->q_coalesce`, and write static ITR to hardware immediately.

Timestamp ethtool paths report PHC index and socket timestamping modes only when PTP capability and clock registration are present. `get_ts_stats` combines vport timestamp counters with per-TX-queue skipped timestamp counts while preserving `u64_stats_sync` consistency.

## State and persistence behavior
Persistent user-facing settings are cached in `adapter->vport_config[np->vport_idx]->user_config`: requested queue counts, descriptor counts, RSS key/LUT, coalescing settings, header split flag, MAC/flow steering lists, and flow steering count. These settings survive queue resource teardown and are replayed by open/reset paths in `idpf_lib.c`. Live state exists in `vport->dflt_qv_rsrc`, q-vectors, queue stats, and PTP/timestamp counters. The file uses `idpf_vport_ctrl_lock()` for vport lifetime protection and spinlocks for list state.

## Dependencies and integration points
The file depends on Linux ethtool, netdevice, PTP timestamping, RCU, `u64_stats_sync`, and virtchnl2 flow rule structures. It integrates with IDPF helpers from `idpf.h`, `idpf_virtchnl.h`, and `idpf_ptp.h`: capability checks, `idpf_config_rss()`, `idpf_add_del_fsteer_filters()`, soft reset initiation, queue model helpers, interrupt ITR writes, and timestamp capability tests. It is installed from `idpf_cfg_netdev()` in `idpf_lib.c`.

## Risks and edge cases
- Ettool stats must keep constant count and order across queue changes; changing max-count based reporting would break userspace buffers.
- Flow steering cache and firmware must stay synchronized. Firmware success with later cache failure or list races would produce misleading rule state.
- `idpf_add_flow_steer()` checks `num_fsteer_fltrs > max`; an off-by-one interpretation around full capacity should be reviewed against firmware expectations.
- Per-queue coalesce uses `q_coalesce[q_num]` for both TX and RX; q index validation depends on callers and q-vector lookup.
- Soft reset rollback differs by operation: channel changes roll back requested counts, while descriptor changes rely on reset behavior after staging.
- Timestamp reporting depends on `adapter->ptp`; missing or partially initialized PTP state must return ethtool fallbacks or `-EOPNOTSUPP`.

## Test signals
Useful signals include `ethtool -x/-X` RSS key/LUT changes with interface up and down, `ethtool -L` queue count changes and rollback on injected reset failure, `ethtool -G` descriptor alignment and TCP data split toggles, `ethtool -C` and per-queue coalesce changes including adaptive/static conflicts, `ethtool -S` count stability before and after queue changes, ntuple TCP/UDP IPv4 add/delete/list tests, PHC/timestamp capability reporting with and without PTP support, and concurrency tests around reset/remove while ethtool queries run.
