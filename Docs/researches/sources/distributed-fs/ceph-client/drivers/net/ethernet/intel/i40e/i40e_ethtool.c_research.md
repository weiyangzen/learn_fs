# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/i40e/i40e_ethtool.c

## Purpose
`i40e_ethtool.c` is the Intel i40e driver's ethtool front end. It exposes link settings, FEC, pause, EEPROM/NVM access, driver/register dumps, ring sizing, statistics, self-tests, Wake-on-LAN, LED identify, interrupt coalescing, RSS, Flow Director classification, channel counts, private driver flags, module EEPROM, timestamp capabilities, EEE, DDP flash, and recovery-mode ethtool behavior for the PF netdev.

## Important APIs, types, and functions
- `struct i40e_stats` plus `I40E_STAT`, `I40E_*_STAT`, and the `i40e_gstrings_*` arrays define fixed ethtool stat names and offsets for netdev, VSI, PF, VEB, traffic-class, PFC, and queue stats.
- `i40e_add_one_ethtool_stat`, `i40e_add_ethtool_stats`, `i40e_add_queue_stats`, and `i40e_add_stat_strings` implement the common stats/string copy paths; queue stats use `u64_stats_fetch_begin/retry` under RCU.
- Link and FEC helpers include `i40e_phy_type_to_ethtool`, `i40e_get_settings_link_up_fec`, `i40e_get_settings_link_up`, `i40e_get_settings_link_down`, `i40e_get_link_ksettings`, `i40e_speed_to_link_speed`, `i40e_set_link_ksettings`, `i40e_get_fec_param`, `i40e_set_fec_param`, and `i40e_set_fec_cfg`.
- Pause and autoneg paths are `i40e_nway_reset`, `i40e_get_pauseparam`, and `i40e_set_pauseparam`.
- NVM APIs are `i40e_get_eeprom`, `i40e_get_eeprom_len`, and `i40e_set_eeprom`; they support normal reads and the NVMUpdate command protocol through the ethtool EEPROM hook.
- Ring APIs are `i40e_get_ringparam`, `i40e_active_tx_ring_index`, and `i40e_set_ringparam`.
- Stats and strings are surfaced through `i40e_get_stats_count`, `i40e_get_sset_count`, `i40e_get_ethtool_stats`, `i40e_get_stat_strings`, `i40e_get_priv_flag_strings`, and `i40e_get_strings`.
- Diagnostics and auxiliary features include `i40e_get_ts_info`, `i40e_diag_test`, `i40e_get_link_ext_stats`, `i40e_get_wol`, `i40e_set_wol`, and `i40e_set_phys_id`.
- Coalescing paths are `__i40e_get_coalesce`, `i40e_get_coalesce`, `i40e_get_per_queue_coalesce`, `i40e_set_itr_per_queue`, `__i40e_set_coalesce`, `i40e_set_coalesce`, and `i40e_set_per_queue_coalesce`.
- RSS APIs are `i40e_get_rxfh_fields`, `i40e_get_rss_hash_bits`, `i40e_set_rxfh_fields`, `i40e_get_rxfh_key_size`, `i40e_get_rxfh_indir_size`, `i40e_get_rxfh`, and `i40e_set_rxfh`.
- Flow Director APIs are `i40e_parse_rx_flow_user_data`, `i40e_fill_rx_flow_user_data`, `i40e_get_ethtool_fdir_all`, `i40e_get_ethtool_fdir_entry`, `i40e_check_fdir_input_set`, `i40e_add_fdir_ethtool`, `i40e_del_fdir_entry`, and related flex-PIT helpers.
- Device controls include `i40e_get_channels`, `i40e_set_channels`, `i40e_get_priv_flags`, `i40e_set_priv_flags`, `i40e_get_module_info`, `i40e_get_module_eeprom`, `i40e_get_eee`, `i40e_set_eee`, and `i40e_set_ethtool_ops`.

## Control flow and behavior
The exported control surface is the `i40e_ethtool_ops` table. The netdev receives the full table unless the PF is in recovery mode, where `i40e_ethtool_recovery_mode_ops` limits access to driver info and NVM operations. Most ethtool callbacks recover `i40e_vsi`, `i40e_pf`, and `i40e_hw` from `netdev_priv()` and then either read cached driver state or issue Admin Queue/register operations.

Link reporting splits between link-up and link-down. Link-up handling maps the active PHY type to ethtool link modes, adds FEC modes where applicable, intersects those modes with NVM-supported capabilities from `i40e_phy_type_to_ethtool`, and reports the current speed. Link-down handling falls back to `phy_types` capability data and reports unknown speed/duplex. Link writes validate controlling partition, VSI type, media/device restrictions, supported advertised masks, and autoneg rules before acquiring `__I40E_CONFIG_BUSY`, issuing `i40e_aq_get_phy_capabilities`, building `i40e_aq_set_phy_config`, possibly taking carrier down, calling `i40e_aq_set_phy_config`, and refreshing link info.

Stats flow is deliberately static. `i40e_get_stats_count` returns a count that does not vary with runtime queue enablement; values for disabled queues or optional VEB stats are zero-filled while strings/counts remain present. `i40e_get_ethtool_stats` updates VSI stats, copies netdev/VSI stats, copies all fixed queue-pair slots under RCU, and appends PF/VEB/PFC stats only for the controlling main PF netdev.

Ring resizing validates descriptor bounds, rejects AF_XDP-attached Rx rings, serializes with `__I40E_CONFIG_BUSY`, and either updates counts while down or allocates replacement Tx/Rx ring resources before `i40e_down()`, swaps ring structs in place so MSI-X ISR references remain valid, and brings the VSI back up.

Flow Director handling validates ethtool flow specs against hardware input-set limits. If a new mask or flex offset is needed, the code rejects the change while MFP is enabled or while existing filters of that flow type depend on the old input set. Accepted rules are stored in `pf->fdir_filter_list`, programmed with `i40e_add_del_fdir`, and counted in `pf->fdir_pf_active_filters`. Deletes remove hardware rules, prune unused flex-PIT offsets, and try to re-enable FDIR if resources allow.

Private flags are converted from ethtool bit positions to internal `pf->flags`, with read-only protection and capability checks. Some changes trigger resets, FDIR flushes, switch-config Admin Queue writes, FEC reconfiguration, LLDP start/stop commands, or warnings about MFP/port-wide side effects.

## State and persistence
This file mutates persistent in-driver state including `pf->flags`, `pf->state`, `pf->msg_enable`, `pf->hw.debug_mask`, `pf->hw.phy.link_info.requested_speeds`, `hw->fc.requested_mode`, `pf->wol_en`, `vsi->num_tx_desc`, `vsi->num_rx_desc`, ring `count` and ITR fields, `vsi->int_rate_limit`, `vsi->rss_hkey_user`, `vsi->rss_lut_user`, `pf->fdir_filter_list`, FDIR counters, flex-PIT lists, and LLDP/FEC/EEE hardware configuration. NVMUpdate operations can affect device NVM through firmware-mediated commands; normal ethtool EEPROM writes are rejected.

## Dependencies and integration points
The file integrates with Linux ethtool, netdev, PCI, PTP, NVM, XDP/AF_XDP, RCU, bitmap/linkmode helpers, and device wakeup APIs. Driver-internal dependencies include Admin Queue helpers, diagnostics, RSS configuration, queue setup/free, reset/open/close/down/up paths, Flow Director programming, DCB/PFC state, VF/VSI lookup, LED/PHY access, register definitions, `i40e_ddp_flash`, and libie packet classification constants.

## Risks and edge cases
- Ettool stats ABI requires string/count/value order to remain stable for a netdev lifetime; adding runtime-dependent stats would break callers.
- Link/FEC/pause writes affect physical port state and are constrained to controlling PF/partition, but incorrect capability checks could disrupt MFP or backplane configurations.
- Ring resizing performs complex live resource replacement; error unwinds and AF_XDP checks are critical to avoid leaks, dangling ISR-visible ring data, or buffer corruption.
- Flow Director input sets are global by flow type and, in MFP, can affect multiple ports; flex-PIT programming is order-sensitive and limited to three entries per L3/L4 table.
- `i40e_set_priv_flags` performs side effects before the final bitmap copy for some flags; failures after partial hardware actions can leave hardware and software state temporarily divergent.
- Module EEPROM and NVMUpdate paths rely on firmware access controls and reset-state checks; callers should expect `-EIO`, `-EBUSY`, or `-EAGAIN`.

## Test signals
Runtime test signals include `ethtool -S`, `--show-priv-flags`, `--set-priv-flags`, `--show-fec/--set-fec`, `--show-pause/--pause`, `--show-coalesce/--coalesce`, per-queue coalesce, `--show-rxfh/--set-rxfh`, `--config-nfc/--show-nfc`, `--show-channels/--set-channels`, `--test online/offline`, `--register-dump`, `--eeprom-dump`, `--module-info`, `--show-eee/--set-eee`, WoL toggles, and LED identify. Kernel log messages and WARN_ONCE checks around stats counts, input-set changes, unsupported flags, AQ failures, and diagnostics provide useful regression signals.
