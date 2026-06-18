# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/iavf/iavf_ethtool.c

## Purpose
`iavf_ethtool.c` exposes the Intel Adaptive Virtual Function driver's userspace control surface through `struct ethtool_ops`. It translates ethtool requests into updates to `struct iavf_adapter`, queue rings, RSS configuration, Flow Director filters, and virtchnl admin-queue work scheduled by `iavf_main.c` and implemented by `iavf_virtchnl.c`.

## Important APIs, Types, And Functions
The local `struct iavf_stats` plus `IAVF_STAT`, `IAVF_QUEUE_STAT`, and `VF_STAT` define the ethtool statistic layout. `iavf_add_one_ethtool_stat`, `__iavf_add_ethtool_stats`, `iavf_add_queue_stats`, and `__iavf_add_stat_strings` copy adapter and ring counters into ethtool buffers while preserving queue counter consistency with `u64_stats_fetch_begin/retry`.

Core ethtool callbacks include `iavf_get_link_ksettings`, `iavf_get_sset_count`, `iavf_get_ethtool_stats`, `iavf_get_strings`, `iavf_get_msglevel`, `iavf_set_msglevel`, `iavf_get_drvinfo`, `iavf_get_ringparam`, `iavf_set_ringparam`, coalesce getters/setters, RX classification getters/setters, channel count getters/setters, and RSS key/LUT getters/setters. `iavf_set_ethtool_ops` installs the static `iavf_ethtool_ops` table on the netdev.

Flow Director support is the largest user-facing area. `iavf_ethtool_flow_to_fltr` and `iavf_fltr_to_ethtool_flow` map ethtool flow constants to `enum iavf_fdir_flow_type`. `iavf_parse_rx_flow_user_data` decodes two 32-bit user-defined flex words from `h_ext/m_ext.data`, enforcing full masks and a maximum offset of 504 bytes. `iavf_add_fdir_fltr_info` converts an `ethtool_rx_flow_spec` into `struct iavf_fdir_fltr`, validates full-or-empty masks via `iavf_validate_fdir_fltr_masks`, rejects duplicates, parses flex words, and builds a virtchnl add message with `iavf_fill_fdir_add_msg`. `iavf_add_fdir_ethtool` and `iavf_del_fdir_ethtool` are wired to `ETHTOOL_SRXCLSRLINS` and `ETHTOOL_SRXCLSRLDEL`.

Advanced RSS is handled by `iavf_adv_rss_parse_hdrs`, `iavf_adv_rss_parse_hash_flds`, `iavf_set_rxfh_fields`, and `iavf_get_rxfh_fields`, which translate ethtool RSS field requests into `iavf_adv_rss` records and `virtchnl_rss_cfg` messages. Standard RSS uses `iavf_get_rxfh`, `iavf_set_rxfh`, `iavf_get_rxfh_key_size`, and `iavf_get_rxfh_indir_size`.

## Control Flow
Most callbacks read or mutate adapter state under the netdev lock supplied by the core networking stack. Configuration callbacks usually validate request shape first, update cached adapter fields, then either call a synchronous helper or set an AQ flag. Examples: ring count changes set `adapter->tx_desc_count` and `rx_desc_count` and invoke `iavf_reset_step` if the interface is running; channel changes set `num_req_queues`, `IAVF_FLAG_REINIT_ITR_NEEDED`, and `IAVF_FLAG_RESET_NEEDED`; RSS field changes add/update an `iavf_adv_rss` list item and schedule `IAVF_FLAG_AQ_ADD_ADV_RSS_CFG`.

FDIR add flow is: ethtool command -> allocate `iavf_fdir_fltr` -> parse action/ring, flow-specific key/mask fields, optional flex words -> validate masks and duplicate status -> fill virtchnl protocol/action message -> insert into adapter FDIR list through `iavf_fdir_add_fltr`. Deletion maps a rule location to `iavf_fdir_del_fltr`, which marks the entry for PF deletion or frees inactive entries.

## State And Persistence Behavior
This file does not persist configuration outside memory. It updates adapter-owned state that survives normal down/up cycles and is replayed by reset/open paths: RSS key and LUT buffers, `adapter->hfunc`, ring descriptor counts, FDIR list entries, advanced RSS list entries, queue coalesce settings, and requested queue counts. Hardware state is asynchronous: many callbacks schedule virtchnl work and return before PF confirmation.

## Dependencies And Integration Points
It depends on Linux ethtool/netdev APIs, RCU and stats sync primitives, TC/RSS constants, `iavf.h`, `iavf_fdir.h`, `iavf_adv_rss.h`, and virtchnl definitions. It integrates with `iavf_main.c` for reset, RSS programming, queue state, and AQ scheduling; with `iavf_fdir.c` for FDIR validation/message building/list management; and with `iavf_adv_rss.c` and `iavf_virtchnl.c` for PF-visible advanced RSS programming.

## Risks
The main risks are asynchronous state races and mismatches between cached state and PF-confirmed state. FDIR and advanced RSS callbacks can return success after enqueueing work, so failures may surface later through virtchnl completions. Mask validation is intentionally strict; partial masks or unsupported flex offsets return errors. `iavf_set_rxfh` writes RSS LUT entries from user-provided indirection values without local queue-range validation in this function, so correctness depends on ethtool/core validation and PF/AQ handling. Reset-triggering operations run under netdev locking and can sleep.

## Test Signals
Useful signals include `ethtool -S` counter shape and per-queue zeroing beyond active queues, ring resize followed by reset and descriptor count preservation, coalesce get/set including per-queue adaptive ITR behavior, `ethtool -N/-n` FDIR add/list/delete paths for IPv4/IPv6/TCP/UDP/SCTP/AH/ESP/L2/user flows, duplicate and partial-mask rejection, `ethtool -X/-x` RSS key/LUT updates, advanced RSS field add/get errors, and channel changes with ADQ disabled/enabled.
