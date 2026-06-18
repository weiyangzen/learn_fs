# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/dvm/rs.c

## Purpose
`rs.c` implements the Intel DVM `iwl-agn-rs` mac80211 rate-control algorithm. It translates between mac80211 rate indexes and firmware `rate_n_flags`, maintains per-station rate success windows, chooses legacy/SISO/MIMO2/MIMO3 modulation tables, builds firmware link-quality retry tables, and registers the algorithm through `struct rate_control_ops`.

The file is both policy and firmware programming glue. Its policy side decides when to raise/lower a rate, toggle antennas, try short guard interval, or search a different modulation mode. Its firmware side fills `struct iwl_link_quality_cmd` and sends `REPLY_TX_LINK_QUALITY_CMD` through station code.

## Important APIs, Types, And Functions
- `iwl_rates[]` is the exported rate metadata table used by this file and other DVM code. Each entry stores legacy PLCP, SISO/MIMO PLCP encodings, IEEE rates, and adjacent-rate indexes.
- `rs_extract_rate()` and `iwl_hwrate_to_plcp_idx()` decode firmware `rate_n_flags` into the internal `IWL_RATE_*_INDEX` space.
- `rs_collect_tx_data()` updates a 62-frame sliding bitmap in `struct iwl_rate_scale_data` and computes success ratio and average throughput.
- `rate_n_flags_from_tbl()` and `rs_get_tbl_info_from_mcs()` convert between a logical `struct iwl_scale_tbl_info` and firmware rate flags.
- `rs_get_adjacent_rate()` and `rs_get_lower_rate()` select fallback or neighboring rates within a supported-rate mask.
- `rs_set_expected_tpt_table()` selects one of the expected-throughput tables based on legacy/HT mode, stream count, 20/40 MHz, SGI, and aggregation.
- `rs_switch_to_siso()`, `rs_switch_to_mimo2()`, and `rs_switch_to_mimo3()` build search-table candidates.
- `rs_move_legacy_other()`, `rs_move_siso_to_other()`, `rs_move_mimo2_to_other()`, and `rs_move_mimo3_to_other()` drive the action search loop for antenna, SGI, and stream-count changes.
- `rs_stay_in_table()` and `rs_set_stay_in_table()` gate how long a chosen modulation table is held before another search.
- `rs_rate_scale_perform()` is the central state machine run from TX status feedback.
- `rs_tx_status()` is the mac80211 TX-status callback; it validates status against the current LQ table, updates statistics, and invokes scaling.
- `rs_get_rate()` is the mac80211 get-rate callback; it exposes the driver's last selected rate to mac80211.
- `iwl_rs_rate_init()` initializes per-station rate masks, state windows, aggregation permission, and the initial firmware link-quality command.
- `rs_fill_link_cmd()` builds the firmware retry table from a selected starting rate and lower fallback rates.
- Debugfs helpers under `CONFIG_MAC80211_DEBUGFS` expose fixed-rate programming and per-station rate statistics.
- `iwlagn_rate_control_register()` and `iwlagn_rate_control_unregister()` register/unregister `rs_ops`.

## Control Flow
Initialization starts when station setup calls `iwl_rs_rate_init()` after the station exists in firmware. The function clears all per-rate windows across both LQ tables, derives active legacy and HT masks from `sta->deflink.supp_rates` and HT MCS masks, records the band and station id, chooses the lowest usable starting rate, and calls `rs_initialize_lq()`. `rs_initialize_lq()` builds the first active table, fills `lq_sta->lq`, stores the LQ pointer in `priv->stations[sta_id].lq`, and sends a synchronous init LQ command.

Transmit feedback enters through `rs_tx_status()`. The callback ignores non-data/no-ack frames and aggregated frames that do not carry AMPDU status. It compares mac80211's first attempted rate against `lq_sta->lq.rs_table[0]`; repeated mismatches increment `missed_rate_counter` and eventually resend the current LQ command to resynchronize firmware. Matching feedback is associated with either the active or search table, then collected with `rs_collect_tx_data()` per AMPDU or per legacy retry entry.

`rs_rate_scale_perform()` consumes the updated history. It first updates traffic-load accounting per TID and detects whether TX aggregation is active. It chooses the working table: active table for normal scaling, or the alternate search table while evaluating a candidate. If the current rate lacks enough samples, it only calls `rs_stay_in_table()` and returns. Once enough samples exist, it either accepts/rejects a search table by comparing measured throughput against `last_tpt`, or adjusts rate within the current table by comparing current, lower, and higher expected/measured throughput.

When no rate update is needed and searches are allowed, `rs_rate_scale_perform()` saves `last_tpt` and calls a mode-specific `rs_move_*_other()` function. Those functions iterate action indexes, applying Bluetooth restrictions, antenna restrictions, HT capability checks, SMPS constraints, valid antenna masks, and SGI capability checks. A successful action populates the alternate table and sets `search_better_tbl`; the new table is then sent to firmware through `rs_fill_link_cmd()` plus `iwl_send_lq_cmd()`. Later TX feedback accepts it by swapping `active_tbl` or rejects it by nulling the search table and restoring the active table.

`rs_fill_link_cmd()` is the last step before firmware. It writes the selected first rate, repeats HT rates up to `IWL_HT_NUMBER_TRY`, falls back through lower rates using `rs_get_lower_rate()`, optionally toggles antennas for legacy retries, then sets aggregation thresholds and Bluetooth-specific aggregation time limits.

## State And Persistence Behavior
Most state is per station in `struct iwl_lq_sta` from `rs.h`. It persists across TX status callbacks and includes active/search table indexes, stay/search flags, total success/failure counters, rate masks, last throughput, last selected firmware rate, aggregation state, Bluetooth traffic snapshot, and traffic-load rings per TID.

Rate history is held in `struct iwl_rate_scale_data.win[]` per table and rate. Each window stores a bitset of recent successes, counters, success ratio, computed average throughput, and a `jiffies` stamp. `rs_stay_in_table()` periodically clears windows to avoid stale decisions and controls when the algorithm may search again.

Firmware-visible persistent state is the station LQ command. The current command is stored in `lq_sta->lq` and often mirrored by `priv->stations[sta_id].lq`; it remains active in firmware until a new LQ command, station removal, firmware reset, or RXON transition clears/restores station state.

Debugfs can persistently force a fixed rate in `dbg_fixed_rate` for the lifetime of the module/station. The comments explicitly note that returning to normal operation requires module reload once fixed-rate operation is programmed.

## Dependencies And Integration Points
The file depends on mac80211 rate-control callbacks, `struct ieee80211_sta`, TX status metadata, HT capability fields, and BA session APIs. It depends on DVM state from `struct iwl_priv`, including NVM antenna masks, hardware TX chain count, Bluetooth coexistence state, workqueue, station table, TID aggregation state, and op-mode conversion helpers.

Station integration is through `iwl_send_lq_cmd()` from `sta.c`, `priv->stations[sta_id].lq`, and `struct iwl_station_priv` for the RXON context. RXON and HT channel configuration constrain HT40 decisions through `iwl_is_ht40_tx_allowed()`, `conf_is_ht()`, and per-context HT state. Bluetooth integration updates LQ tables and queues `bt_full_concurrency` work when coexistence state changes. Aggregation integration uses `ieee80211_start_tx_ba_session()` and `ieee80211_stop_tx_ba_session()` based on throughput and TID load.

## Risks And Edge Cases
- The algorithm assumes TX status rate metadata matches the most recent firmware LQ command. If firmware or mac80211 reports stale metadata, feedback is ignored until a resync threshold is hit.
- Rate index conversion has special cases for HT indexes, 9 Mbps gaps, and 5 GHz OFDM offsets; off-by-one mistakes directly corrupt rate choices.
- `rs_collect_tx_data()` uses a 62-bit history in a `u64`; the mask and shifting logic must stay aligned with `IWL_RATE_MAX_WINDOW`.
- The active/search table swap is stateful and sensitive to `search_better_tbl`, `active_tbl`, and `lq_type = LQ_NONE`. Failed or interrupted LQ commands can leave software and firmware policy out of sync.
- Bluetooth high traffic and full concurrency force one-chain behavior and can drive down from MIMO; regressions need coexistence testing, not just WLAN throughput tests.
- `rs_use_green()` always returns false due to a documented GF+SGI/SISO issue. Re-enabling greenfield would reopen that interoperability risk.
- Debugfs fixed-rate overrides can bypass normal rate adaptation and antenna validation only rejects invalid antenna masks.
- `rs_initialize_lq()` stores `&lq_sta->lq` into the station table, while local/broadcast station code may allocate separate LQ commands. Lifetime assumptions differ by station type.

## Test Signals
Useful signals include association and throughput tests on 2.4 GHz and 5 GHz, legacy-only and HT networks, 20 MHz and HT40, SISO/MIMO2/MIMO3 hardware, SMPS static/dynamic/off peers, and one/two/three antenna masks. TX status traces should show rate increases, decreases, table searches, search accept/reject, and LQ command resync after missed-rate mismatches. Aggregation tests should verify BA session start only when TID load and throughput permit it. Bluetooth coexistence tests should confirm MIMO suppression, single-antenna operation, LQ refresh, and aggregation time-limit changes. Debugfs fixed-rate read/write paths should be exercised with valid and invalid antenna masks.
