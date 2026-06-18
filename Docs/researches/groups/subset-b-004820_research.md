# subset-b-004820 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/dvm/rs.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/dvm/rs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/dvm/rs.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/dvm/rs.h

## Purpose
`rs.h` is the shared definition header for the DVM rate-scaling implementation. It declares the internal rate indexes, PLCP and IEEE encodings, rate masks, rate-control thresholds, mode-search action constants, traffic-load constants, table classification helpers, and the per-station state structures consumed by `rs.c` and related station code.

The header forms the contract between mac80211 station private data, firmware link-quality commands, and the DVM rate-control policy.

## Important APIs, Types, And Macros
- `struct iwl_rate_info` describes each rate's firmware PLCP encodings, IEEE value, and adjacent-rate relationships. `iwl_rates[]` is declared here and defined in `rs.c`.
- `IWL_RATE_*_INDEX`, `IWL_RATE_*_INDEX_TABLE`, and first/last OFDM/CCK enums define the internal indexing space.
- `IWL_RATE_*_MASK` macros build bitmasks for supported-rate filtering.
- Legacy and HT PLCP enums map internal rates to firmware API values for legacy, SISO, MIMO2, and MIMO3 rates.
- IEEE rate enums provide the mac80211-visible half-Mbps values.
- Threshold macros such as `IWL_RATE_HIGH_TH`, `IWL_RATE_INCREASE_TH`, and `IWL_RATE_DECREASE_TH` use a `128 * percent` success-ratio scale.
- `IWL_LEGACY_*` and `IWL_NONE_LEGACY_*` constants define how long the algorithm stays in a selected modulation table.
- `IWL_*_SWITCH_*` constants enumerate possible search actions from legacy, SISO, MIMO2, and MIMO3 modes.
- `enum iwl_table_type` plus helpers `is_legacy()`, `is_siso()`, `is_mimo2()`, `is_mimo3()`, `is_mimo()`, `is_Ht()`, and `is_a_band()` classify LQ tables.
- `struct iwl_rate_scale_data` stores per-rate sliding-window statistics.
- `struct iwl_scale_tbl_info` stores one active or search table's modulation type, antenna mask, SGI/HT40/duplicate flags, action cursor, expected throughput table, current rate, and per-rate windows.
- `struct iwl_traffic_load` stores a per-TID circular traffic-load history used to decide when to start TX aggregation.
- `struct iwl_lq_sta` is the central per-station rate-control state, including two `iwl_scale_tbl_info` tables, the current firmware `iwl_link_quality_cmd`, supported-rate masks, counters, aggregation flags, last selected rates, and a backpointer to `struct iwl_priv`.
- `first_antenna()` returns `ANT_A`, `ANT_B`, or `ANT_C` from a mask in priority order.
- Public functions are `iwl_rs_rate_init()`, `iwlagn_rate_control_register()`, and `iwlagn_rate_control_unregister()`.

## Control Flow
This header does not execute control flow, but it defines the state machine vocabulary. `LQ_SIZE` fixes two mode tables: active and search. `active_tbl`, `search_better_tbl`, `stay_in_tbl`, action counters, table count limits, and success/failure limits in `struct iwl_lq_sta` are the flags and counters that `rs.c` mutates when moving between rate adjustment and modulation-mode search.

Rate masks begin with peer/mac80211 capabilities (`supp_rates`, `active_*_rate`) and are intersected with mode-specific table masks during scaling. Action constants define the order in which `rs.c` tries antenna changes, SISO/MIMO transitions, and guard interval changes. Traffic-load constants define the time bucket size and maximum history used before requesting aggregation.

## State And Persistence Behavior
All persistent rate-control state described here is per station and lives in mac80211 station private storage through `struct iwl_station_priv`. It survives across many packets and callbacks until station teardown or reinitialization. The `iwl_link_quality_cmd lq` inside `struct iwl_lq_sta` is both a cached software representation and the template sent to firmware.

No state in this header is global except the declared `iwl_rates[]` table. The macros and enums are compile-time contracts with firmware encodings and cannot be changed without updating conversion logic and firmware command expectations.

## Dependencies And Integration Points
The header includes mac80211 definitions, `iwl-config.h`, and firmware command structures from `commands.h`. It references `struct iwl_priv`, `struct ieee80211_sta`, `struct iwl_link_quality_cmd`, `IWL_MAX_TID_COUNT`, antenna masks, and rate flag encodings declared elsewhere in the DVM driver.

`sta.c` uses `iwl_rates[]` and `first_antenna()` when constructing default link-quality commands for local and broadcast stations. `rs.c` owns most consumers of the structures. RXON/HT configuration and station HT capabilities feed fields in `struct iwl_lq_sta` and `struct iwl_scale_tbl_info`.

## Risks And Edge Cases
- The internal rate ordering mixes CCK, OFDM, and a pseudo 60 Mbps index. Conversion code must respect gaps and band-specific offsets.
- Success ratio thresholds are scaled by 128, not plain percentages. Misinterpreting them changes rate-control aggressiveness.
- `is_g_and()` appears to be a typo-like helper name for `LQ_G`; callers should avoid propagating the naming mistake into new APIs.
- `TIME_WRAP_AROUND()` handles a wrapping millisecond counter by arithmetic expression; callers must pass comparable rounded times.
- `first_antenna()` returns `ANT_C` when neither A nor B is set, so callers should validate masks before treating its return as guaranteed supported.
- `struct iwl_lq_sta` mixes algorithm-only state, firmware command state, debugfs state, and driver backpointers. Lifetime and locking must be handled by station code and mac80211 callbacks.
- Action constants are mode-specific but some loops in `rs.c` compare against similarly valued constants from another mode; changes to these values need broad review.

## Test Signals
Build coverage should include debugfs enabled and disabled because `dbg_fixed_rate` changes `struct iwl_lq_sta`. Runtime validation should confirm rate mask derivation for 2.4 GHz CCK/OFDM, 5 GHz OFDM-only, and HT MCS masks for one, two, and three streams. Tests that inspect debugfs `rate_scale_table` and `rate_stats_table` can validate that structure fields are populated and evolve as expected. Any change to constants should be checked with throughput, aggregation, and Bluetooth coexistence tests because those thresholds directly steer rate-control state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/dvm/rs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/dvm/rx.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/dvm/rx.c

## Purpose
`rx.c` contains the generic receive notification and response handlers for the Intel DVM driver. It dispatches firmware RX packets, handles firmware errors, channel switch notifications, spectrum and power-management notifications, statistics, RF-kill/card-state changes, missed beacons, RX PHY/MPDU data, P2P Notice of Absence updates, and setup of the RX handler table.

The file is the bridge from transport-level firmware responses to mac80211-visible RX frames and driver-maintained health/calibration state.

## Important APIs, Types, And Functions
- `iwl_setup_rx_handlers()` installs command-id handlers into `priv->rx_handlers`.
- `iwl_rx_dispatch()` is the op-mode RX dispatcher. It notifies waiters, increments handler stats, and invokes the registered handler by firmware command id.
- `iwlagn_rx_reply_error()` logs firmware `REPLY_ERROR` details.
- `iwlagn_rx_csa()` handles channel switch completion/failure and calls `iwl_chswitch_done()`.
- `iwlagn_rx_statistics()` parses normal or Bluetooth-aware statistics notifications, updates `priv->statistics`, schedules calibration work, and triggers temperature callbacks.
- `iwlagn_rx_reply_statistics()` handles explicit statistics replies and clears debugfs accumulated statistics when firmware says counters were cleared.
- `iwl_force_rf_reset()` requests a radio reset by scheduling an internal short hardware scan.
- `iwlagn_recover_from_statistics()` and `iwlagn_good_plcp_health()` detect excessive PLCP errors and trigger RF reset.
- `iwlagn_rx_card_state_notif()` processes software/hardware/thermal RF-kill state and command blocking.
- `iwlagn_rx_reply_rx_phy()` caches PHY metadata for the following MPDU.
- `iwlagn_rx_reply_rx()` validates MPDU data, builds `struct ieee80211_rx_status`, translates decrypt status, calculates RSSI, handles AMPDU metadata, and passes frames to mac80211.
- `iwlagn_pass_packet_to_mac80211()` builds an skb, attaches a stolen RX page fragment when needed, applies passive-channel beacon recovery, and calls `ieee80211_rx_napi()`.
- `iwlagn_rx_noa_notification()` replaces P2P NoA data under RCU.

## Control Flow
RX setup is table-driven. `iwl_setup_rx_handlers()` assigns handlers for firmware command IDs and delegates scan handler registration to `iwl_setup_rx_scan_handlers()`. Once operational, `iwl_rx_dispatch()` receives every RX command buffer, first wakes notification waiters through `iwl_notification_wait_notify()`, then calls the command-specific function if present.

Statistics notifications are parsed by payload length into either `struct iwl_bt_notif_statistics` or `struct iwl_notif_statistics`. Under `priv->statistics.lock`, the handler updates accumulative debug stats, checks PLCP health if associated and enough time elapsed, copies current counters into `priv->statistics`, updates `rx_statistics_jiffies`, sets `STATUS_STATISTICS`, refreshes the periodic statistics timer, queues runtime calibration work outside scan, and invokes temperature handling on relevant changes.

RX frame delivery is split between PHY and MPDU notifications. `REPLY_RX_PHY_CMD` caches `priv->last_phy_res`, sets validity, and increments an AMPDU reference. `REPLY_RX_MPDU_CMD` requires that cache, validates packet sizes and CRC/FIFO status, computes channel/frequency/rate/signal/antenna/HT flags in `ieee80211_rx_status`, translates firmware decrypt bits to mac80211 flags, and hands the payload to `iwlagn_pass_packet_to_mac80211()`.

Card-state notifications can command-block firmware, enter or exit critical-temperature handling, update hardware RF-kill state, cancel scans when RXON is not disabled, and inform cfg80211 via `wiphy_rfkill_set_hw_state()`. Missed beacon notifications reinitialize sensitivity when thresholds are exceeded and not scanning.

## State And Persistence Behavior
The file updates persistent driver state in `struct iwl_priv`: statistics snapshots and debug deltas, measurement reports and flags, `ibss_manager`, RF reset counters/timestamps, `last_phy_res` and `last_phy_res_valid`, `ampdu_ref`, `ucode_beacon_time`, `passive_no_rx`, RF-kill bits, `noa_data`, and RX handler statistics.

Most RX frame state is transient per command buffer. If a frame is larger than the allocated skb headroom, `iwlagn_pass_packet_to_mac80211()` steals the RX page into an skb fragment, transferring ownership from the RX command buffer to mac80211.

`noa_data` is RCU-replaced and old data is freed with `kfree_rcu()`. Statistics timers and calibration work persist beyond the handler invocation.

## Dependencies And Integration Points
This file depends on the transport RX buffer API (`rxb_addr()`, `rxb_offset()`, `rxb_steal_page()`), firmware command/notification structs, CSR/HBUS register accessors, mac80211 RX APIs, cfg80211 RF-kill integration, calibration (`iwl_init_sensitivity()`, runtime calibration work), scan cancellation, Bluetooth RX handler setup, station add callback, TX reply/BA handlers, and notification wait infrastructure.

It integrates with `scan.c` by installing scan handlers and canceling scans on card-state changes. It integrates with `rxon.c` through CSA channel updates and passive-channel beacon recovery. It integrates with `sta.c` through `REPLY_ADD_STA` callback registration, and with aggregation/TX through BA and TX reply handlers registered here.

## Risks And Edge Cases
- `iwlagn_rx_reply_rx()` depends on receiving a valid PHY notification before MPDU. Missing or out-of-order notifications drop the frame.
- Packet length checks protect against firmware-reported length mismatches; weakening them risks skb overread or invalid page-frag offsets.
- Decryption handling drops WEP/TKIP packets with bad ICV/MIC because hardware decrypts in place. Incorrect status translation can either leak bad frames or drop recoverable software-decrypt frames.
- Statistics parsing relies on exact payload sizes for normal vs Bluetooth statistics.
- `accum_stats()` deliberately ignores counter roll-over in debugfs builds.
- RF reset is rate-limited for internal requests but external requests bypass that interval; both require association.
- Card-state command blocking manipulates device registers and must stay synchronized with firmware RF-kill semantics.
- The passive-channel beacon workaround wakes queues when beacons for active BSSIDs arrive; incorrect BSSID matching could leave queues stopped or lift restrictions too early.

## Test Signals
Test signals include RX data delivery with small and large frames, AMPDU RX status, encrypted WEP/TKIP/CCMP success and failure cases, scan plus card-state interactions, CSA success/failure, RF-kill toggles, thermal kill entry/exit, missed beacon sensitivity reinit, statistics notifications with and without Bluetooth sections, PLCP-error recovery scans, and P2P NoA update/free behavior under RCU. NAPI RX tests should verify that stolen RX pages are not reused after skb handoff.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/dvm/rx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/dvm/rxon.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/dvm/rxon.c

## Purpose
`rxon.c` owns DVM RXON context configuration and commit logic. RXON commands describe firmware receive/transmit context state: interface type, channel, band, BSSID, node address, association bit, basic ACK rates, HT flags, RX chains, hardware crypto, beacon timing, QoS, PAN coexistence slots, and TX power. The file translates mac80211 configuration and BSS changes into staging RXON state and decides whether firmware can be updated with `RXON_ASSOC` or needs a full RXON transition.

## Important APIs, Types, And Functions
- `iwl_connection_init_rx_config()` initializes `ctx->staging` from interface type, channel, band, and default HT basic rates.
- `iwlagn_commit_rxon()` is the central commit function for a staging RXON context.
- `iwl_full_rxon_required()` compares staging and active RXON fields to choose full RXON vs association update.
- `iwlagn_send_rxon_assoc()` sends the smaller RXON association update when only allowed flags/rates/chains changed.
- `iwlagn_rxon_disconn()` clears association, restores firmware station/key state, and updates active RXON.
- `iwlagn_rxon_connect()` sends timing/QoS/beacon data, full associated RXON, sensitivity init, and TX power.
- `iwl_send_rxon_timing()` computes and sends beacon timing, DTIM, listen interval, and beacon init values.
- `iwlagn_set_pan_params()` programs two-slot BSS/PAN time slicing.
- `iwl_set_rxon_ht()` and `_iwl_set_rxon_ht()` translate HT configuration into RXON channel-mode/protection flags and RX chain selection.
- `iwl_set_rxon_channel()` and `iwl_set_flags_for_band()` update channel and 2.4/5 GHz flags.
- `iwl_check_rxon_cmd()` validates staging RXON before commit.
- `iwl_calc_basic_rates()` derives firmware ACK/basic-rate bitmaps from mac80211 BSS basic rates plus mandatory lower rates.
- `iwlagn_mac_config()` handles global mac80211 configuration changes.
- `iwlagn_bss_info_changed()` handles per-vif BSS changes such as association, QoS, beaconing, HT operation, protection, BSSID, and IBSS station management.
- `iwlagn_post_scan()` applies deferred power/TX/RXON/PAN changes after scanning.

## Control Flow
Configuration is staged first, committed later. Interface creation or reset calls `iwl_connection_init_rx_config()` to populate `ctx->staging`. mac80211 changes enter through `iwlagn_mac_config()` and `iwlagn_bss_info_changed()`, which mutate staging fields while holding `priv->mutex`. If staging differs from active, they call `iwlagn_commit_rxon()`.

`iwlagn_commit_rxon()` recalculates basic rates, sets TSF-to-host and protection flags, adjusts short-slot state, validates the command, aborts conflicting channel switches, and then branches. If `iwl_full_rxon_required()` is false, it sends `RXON_ASSOC`, copies staging to active, applies deferred TX power, and updates power mode. If a full RXON is needed, it configures hardware crypto, first sends an unassociated RXON through `iwlagn_rxon_disconn()`, updates PAN parameters, and if the target is associated calls `iwlagn_rxon_connect()`.

Disconnect is special because unassociated RXON clears firmware station and WEP key tables. `iwlagn_rxon_disconn()` therefore clears the driver's ucode-active station bits, updates broadcast station LQ, restores driver-known stations, and restores default WEP keys before copying staging to active.

Association connect sends timing first for BSS contexts, updates QoS, sends a beacon before AP RXON when needed, sends the full associated RXON, sends IBSS beacon after assoc for adhoc, initializes sensitivity, and forces TX power programming because channel retune requires it.

Post-scan flow applies changes deferred while scanning: power mode, TX power, pending RXON commits for each context, and PAN parameters.

## State And Persistence Behavior
Each `struct iwl_rxon_context` maintains `staging` and `active` RXON commands. Staging is the desired software state; active mirrors the last committed firmware state. Additional persistent context state includes timing, beacon interval, QoS data, WEP keys, HT mode/protection, whether multiple chains are needed, station IDs, and active/vif flags.

The file also updates global persistent state such as `priv->band`, `priv->timestamp`, `priv->tx_power_user_lmt`, `priv->tx_power_next`, `priv->beacon_skb`, `priv->beacon_ctx`, `priv->have_rekey_data`, chain noise calibration state, and PAN slot settings in firmware.

Scanning can defer TX power and RXON commits. `iwlagn_post_scan()` is responsible for reconciling deferred software state with firmware.

## Dependencies And Integration Points
`rxon.c` depends on mac80211 config and BSS callbacks, firmware commands (`ctx->rxon_cmd`, `rxon_assoc_cmd`, `rxon_timing_cmd`, QoS and PAN commands), station restoration from `sta.c`, WEP key restoration, beacon command generation, power management, calibration, Bluetooth coexistence monitoring, scan status, and channel-switch completion.

It integrates with rate control and station code indirectly by changing HT40, RX chains, and station restoration conditions. It integrates with scan code by deferring changes during scan and by using `STATUS_SCAN_HW` in PAN slot calculations. It integrates with RF calibration by resetting chain-noise calibration after association.

## Risks And Edge Cases
- Incorrect full-RXON vs RXON_ASSOC classification can either retune unnecessarily or attempt an unsupported partial update.
- Full unassociated RXON clears firmware station and WEP state; failure to restore stations, broadcast station LQ, or keys breaks traffic after channel/interface changes.
- PAN timing has dual-context assumptions enforced by `BUILD_BUG_ON(NUM_IWL_RXON_CTX != 2)`. Extending contexts requires redesign.
- Beacon timing copies values between BSS and PAN in some association states; zero or mismatched beacon intervals can cause poor power-save or PAN behavior.
- `iwl_set_tx_power()` defers during scan or channel change and must restore previous limits on command failure.
- HT40 flags depend on mac80211 channel definition, peer capability, context association state, and regulatory/channel flags. A wrong flag can make firmware transmit with an invalid width.
- `iwl_check_rxon_cmd()` catches invalid combinations such as multicast addresses, missing mandatory basic rates, impossible CCK/short-slot combinations, and zero channel. Treat warnings as real configuration bugs.
- `iwlagn_bss_info_changed()` assumes context/vif readiness under mutex; races during teardown are handled by early returns, but new paths must preserve locking.

## Test Signals
High-value tests include association/disassociation, AP/IBSS/station modes, channel switch, HT20/HT40 changes, power-save and idle changes, TX power changes during scan and after scan, hardware and software crypto toggles, QoS updates, beacon interval changes, AP/IBSS beacon updates, BSS plus PAN coexistence, WEP key restoration after RXON, station restoration after full RXON, and chain-noise calibration start after association. Debug output from `iwl_print_rx_config_cmd()` and validation warnings from `iwl_check_rxon_cmd()` are useful diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/dvm/rxon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/dvm/scan.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/dvm/scan.c

## Purpose
`scan.c` implements firmware hardware scanning for the DVM driver. It builds `REPLY_SCAN_CMD` payloads, handles scan notifications, maintains scan state bits, supports cancellation and watchdog completion, performs internal short passive scans used as RF reset, and applies deferred RXON/power settings when scans finish.

## Important APIs, Types, And Functions
- `iwl_scan_initiate()` is the main entry point for normal and internal scan start.
- `iwlagn_request_scan()` allocates/fills `struct iwl_scan_cmd`, including probe request, channel list, dwell times, TX rate, RX chain selection, suspend timing, and PAN updates.
- `iwl_send_scan_abort()`, `iwl_do_scan_abort()`, `iwl_scan_cancel()`, and `iwl_scan_cancel_timeout()` implement asynchronous and timeout-based cancellation.
- `iwl_process_scan_complete()` reconciles scan completion bits, reports completion to mac80211, restarts pending normal scans after internal scans, and calls `iwlagn_post_scan()`.
- `iwl_force_scan_end()` forcibly clears scan state and reports an aborted scan.
- `iwl_rx_reply_scan()`, `iwl_rx_scan_start_notif()`, `iwl_rx_scan_results_notif()`, and `iwl_rx_scan_complete_notif()` handle firmware scan responses and notifications.
- `iwl_setup_rx_scan_handlers()` registers scan notification handlers into `priv->rx_handlers`.
- `iwl_get_active_dwell_time()`, `iwl_get_passive_dwell_time()`, and `iwl_limit_dwell()` compute dwell limits, including association beacon timing constraints.
- `iwl_get_channels_for_scan()` fills the per-channel scan descriptors from `priv->scan_request`.
- `iwl_get_channel_for_reset_scan()` selects a single passive channel for RF reset scans.
- `iwl_fill_probe_req()` builds the probe request template.
- `iwl_internal_short_hw_scan()` queues an internal radio-reset scan.
- `iwl_setup_scan_deferred_work()` and `iwl_cancel_scan_deferred_work()` manage workqueue items.

## Control Flow
Normal scans enter through `iwl_scan_initiate()` under `priv->mutex`. The function rejects scans when RF is not ready, hardware scan is already active, or abort is pending. It sets `STATUS_SCANNING`, records scan type/start/band, calls `iwlagn_request_scan()`, and arms `scan_check` as a watchdog.

`iwlagn_request_scan()` builds the firmware command. For associated scans, it computes suspend timing so firmware periodically returns to the operating channel. For active scans, it inserts the first SSID into the probe request and other SSIDs into `direct_scan` in reverse order. It chooses 1 Mbps CCK or 6 Mbps OFDM on 2.4 GHz depending on `no_cck` and channel mode, always 6 Mbps on 5 GHz, applies Bluetooth coexistence TX flags, selects scan TX antenna, forces RX chains as needed for power-save or full concurrency, fills probe request bytes, fills either the requested channel list or a single radio-reset channel, sets `STATUS_SCAN_HW`, updates PAN params, and sends `REPLY_SCAN_CMD`.

Firmware completion enters through `iwl_rx_scan_complete_notif()`. The handler sets `STATUS_SCAN_COMPLETE`, clears `STATUS_SCAN_HW`, queues `scan_completed` work, and updates Bluetooth traffic status if provided. The work item calls `iwl_process_scan_complete()`, which clears completion/aborting/scanning bits, reports mac80211 scan completion, handles a pending normal scan queued during an internal scan, and calls `iwlagn_post_scan()` if RF is still ready.

Cancellation uses workqueues to avoid doing abort work directly from arbitrary contexts. `iwl_scan_cancel()` queues `abort_scan`. `iwl_bg_abort_scan()` calls `iwl_scan_cancel_timeout()`, which sends abort and waits for `STATUS_SCAN_HW` to clear, then runs completion inline if firmware already completed before the background completion work runs.

Internal RF reset scans are queued through `iwl_internal_short_hw_scan()`, started by `iwl_bg_start_internal_scan()`, and use `IWL_SCAN_RADIO_RESET` with short passive dwell on a valid unused channel.

## State And Persistence Behavior
Scan state is tracked through `priv->status` bits: `STATUS_SCANNING`, `STATUS_SCAN_HW`, `STATUS_SCAN_ABORTING`, and `STATUS_SCAN_COMPLETE`. Additional persistent fields include `scan_type`, `scan_band`, `scan_start`, `scan_start_tsf`, `scan_vif`, `scan_request`, `scan_cmd`, `scan_cmd_size`, and per-band `scan_tx_ant`.

`priv->scan_cmd` is allocated once large enough for firmware channel descriptors plus maximum probe length and reused. Normal scan completion clears `scan_vif` and `scan_request` after reporting to mac80211. Internal scans can leave a mac80211 scan pending and then initiate it after internal completion.

Bluetooth scan status from firmware updates `bt_status`, `bt_traffic_load`, and queues `bt_traffic_change_work`.

## Dependencies And Integration Points
The file depends on mac80211 scan requests, channel flags, supported-band data, firmware scan command structures, DVM command sending, PAN parameter updates from `rxon.c`, post-scan RXON/power reconciliation through `iwlagn_post_scan()`, Bluetooth coexistence state, antenna helpers from rate-scaling definitions, and workqueue infrastructure.

It integrates with `rx.c` through scan RX handler registration. It integrates with RF reset from `rx.c` via `iwl_force_rf_reset()` calling `iwl_internal_short_hw_scan()`. It integrates with RXON because scans defer or alter PAN slots, power settings, and RXON commits.

## Risks And Edge Cases
- `MAX_SCAN_CHANNEL` is enforced only for normal scans with a warning; firmware command sizing depends on this maximum.
- Scan state uses several bits with ordering constraints. Completion sets `STATUS_SCAN_COMPLETE` before clearing `STATUS_SCAN_HW` to avoid abort races.
- `iwl_limit_dwell()` clamps dwell based on beacon intervals and active contexts; arithmetic underflow would be dangerous if limits become smaller than tune time.
- `iwl_fill_probe_req()` must respect available command buffer space; it returns partial length if optional IEs do not fit after warning.
- Internal radio-reset scans pass `vif = NULL`; paths must avoid dereferencing it except where scan type guarantees normal scan.
- PAN params are changed before scan command submission and restored if command submission fails.
- The scan command is reused; if firmware capability max probe length unexpectedly grows, the function refuses rather than reallocating.
- Cancellation can complete inline while a background completion work item is queued; the status-bit protocol prevents double completion.

## Test Signals
Test normal passive and active scans on 2.4 GHz and 5 GHz, with multiple SSIDs, `no_cck`, passive/no-IR channels, associated scans, unassociated scans, P2P/PAN concurrent contexts, power-save scans, Bluetooth full concurrency, aborts, timeout watchdog completion, and internal RF reset scans. Verify mac80211 receives exactly one completion with correct aborted flag. Check that post-scan power, TX power, PAN slots, and pending RXON commits are applied.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/dvm/scan.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/dvm/sta.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/dvm/sta.c

## Purpose
`sta.c` manages DVM firmware station table state. It adds, modifies, removes, deactivates, clears, and restores firmware stations; builds default link-quality commands for local/broadcast stations; manages static WEP and dynamic per-station keys; allocates and updates broadcast stations; and issues station modifications for TX enable, RX aggregation, and sleep TX count.

This file is the central consistency layer between mac80211 station objects, driver station bookkeeping, and firmware `REPLY_ADD_STA`/`REPLY_REMOVE_STA`/`REPLY_TX_LINK_QUALITY_CMD` commands.

## Important APIs, Types, And Functions
- `iwl_send_add_sta()` sends `REPLY_ADD_STA`, optionally synchronously with response validation.
- `iwl_add_sta_callback()` and `iwl_process_add_sta_resp()` handle asynchronous add-station responses.
- `iwl_prep_station()` assigns or reuses a station id, initializes `priv->stations[sta_id].sta`, sets context id, and applies HT flags.
- `iwl_add_station_common()` prepares and synchronously adds a station to firmware.
- `iwl_remove_station()` removes a driver-active/ucode-active station and sends `REPLY_REMOVE_STA`.
- `iwl_deactivate_station()` clears driver-active state without sending removal, used when firmware is not necessarily updated immediately.
- `iwl_clear_ucode_stations()` clears software ucode-active bits after firmware operations, such as unassociated RXON, implicitly clear the firmware table.
- `iwl_restore_stations()` re-adds driver-active stations missing from firmware and resends saved LQ commands.
- `iwl_sta_fill_lq()`, `iwl_sta_alloc_lq()`, and `iwl_send_lq_cmd()` build and send default link-quality commands.
- `iwl_is_ht40_tx_allowed()`, `iwl_sta_calc_ht_flags()`, and `iwl_sta_update_ht()` compute and update per-station HT flags.
- Static WEP functions are `iwl_set_default_wep_key()`, `iwl_remove_default_wep_key()`, and `iwl_restore_default_wep_keys()`.
- Dynamic key functions are `iwl_set_dynamic_key()`, `iwl_remove_dynamic_key()`, `iwl_update_tkip_key()`, and helper `iwlagn_send_sta_key()`.
- Broadcast/local station helpers are `iwlagn_add_bssid_station()`, `iwlagn_alloc_bcast_station()`, `iwl_update_bcast_station()`, `iwl_update_bcast_stations()`, and `iwl_dealloc_bcast_stations()`.
- Aggregation/station modify helpers are `iwl_sta_tx_modify_enable_tid()`, `iwl_sta_rx_agg_start()`, `iwl_sta_rx_agg_stop()`, and `iwl_sta_modify_sleep_tx_count()`.

## Control Flow
Adding a station begins with `iwl_add_station_common()`. Under `sta_lock`, it calls `iwl_prep_station()` to choose a fixed AP/broadcast id or a free peer id, reject in-progress duplicates, initialize command fields, increment `num_stations`, store context id, attach the context to mac80211 station private data, and set HT flags. It marks `IWL_STA_UCODE_INPROGRESS`, copies the command, unlocks, and sends it synchronously. On successful firmware response, `iwl_send_add_sta()` activates the ucode bit; on failure, the driver-active and in-progress bits are cleared.

Removal checks readiness and station state under `sta_lock`, clears local LQ storage if needed, clears TID aggregation data, clears `IWL_STA_DRIVER_ACTIVE`, decrements station count, then sends `REPLY_REMOVE_STA`. Firmware success calls `iwl_sta_ucode_deactivate()` unless removal is temporary, which clears ucode-active and zeros the station entry.

RXON transitions can clear firmware station state without explicit remove commands. `iwl_clear_ucode_stations()` clears only software ucode-active bits, and `iwl_restore_stations()` later finds driver-active but not ucode-active entries, marks them in progress, sends add-station commands, and optionally resends their cached LQ commands. During WoWLAN restore it creates a simple default LQ instead of trusting the saved command.

Key programming is station modification. Static WEP uses a context-level WEP command with four slots. Dynamic CCMP/TKIP/WEP keys allocate a firmware key-cache offset, build station key flags, copy key material, and send an add-station modify with `STA_MODIFY_KEY_MASK`. TKIP updates can be asynchronous after scan cancellation.

Aggregation and TID modifications copy the current station command under lock, set the relevant modify mask and TID fields, unlock, and send `REPLY_ADD_STA` modify commands.

## State And Persistence Behavior
Persistent software state lives in `priv->stations[]`, `priv->num_stations`, `priv->tid_data[][]`, `priv->ucode_key_table`, and per-context WEP/key counters. Each station has `used` flags such as `IWL_STA_DRIVER_ACTIVE`, `IWL_STA_UCODE_ACTIVE`, `IWL_STA_UCODE_INPROGRESS`, `IWL_STA_LOCAL`, and `IWL_STA_BCAST`.

Firmware-visible state includes the firmware station table, per-station HT flags, key mappings, BA/TID settings, sleep TX count, and link-quality command. Firmware can implicitly clear station/key state during RXON transitions, so this file separates driver-active and ucode-active state to support restoration.

LQ commands for local/broadcast stations are heap allocated and stored in `priv->stations[sta_id].lq`; normal peer LQ commands are owned by rate-control station private state and referenced from the station table.

## Dependencies And Integration Points
The file depends on DVM command sending, firmware station/key command layouts, `sta_lock`, `priv->mutex` for operations that sleep or coordinate with RXON, mac80211 station/HT/key APIs, rate definitions from `rs.h`, RXON context state, and aggregation TID state. It is called from mac80211 station/key callbacks elsewhere in the driver, from RXON commit/restore logic in `rxon.c`, from rate scaling in `rs.c`, and from RX dispatch for add-station responses.

`iwl_send_lq_cmd()` is a major integration point for `rs.c`; it validates station active state and rejects HT LQ tables when the current RXON context is not HT-enabled.

## Risks And Edge Cases
- Station state is split between driver-active, ucode-active, and in-progress bits. Missing a bit transition can leak station slots, duplicate adds, or skip restoration.
- `iwl_prep_station()` increments `num_stations` when preparing a new station; all failure paths must decrement or clear state correctly.
- Add-station in-progress serialization protects firmware from concurrent add requests. New asynchronous paths must respect it.
- `iwl_send_lq_cmd()` rejects HT rates on non-HT channels to avoid a known disconnect race; callers must handle `-EINVAL`.
- Key-cache offsets are global bits. Failure to clear bits on key install/remove errors can exhaust hardware key slots.
- Static WEP and dynamic key paths differ. RXON unassociated transitions clear firmware WEP keys and require explicit restore.
- TKIP update cancels scan but, if cancellation fails, leaves a brief reliance on software decryption.
- Broadcast station LQ update replaces heap memory under `sta_lock`; concurrent users must follow existing lock/lifetime assumptions.
- Remove/deactivate behavior intentionally returns success when device is not ready, because teardown often removes stations after firmware shutdown.

## Test Signals
Test station add/remove/readd, AP station and broadcast station IDs, duplicate add handling, firmware add failure statuses, RXON station clear plus restore, WoWLAN station restore, HT flag updates for SMPS/HT40/AMPDU factor/density, LQ validation on HT and non-HT channels, default WEP set/remove/restore, dynamic CCMP/TKIP/WEP keys, key slot exhaustion and cleanup, TKIP phase1 updates during scans, RX aggregation start/stop, TID TX enable, sleep TX count modify, and teardown while device is not ready.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/dvm/sta.c -->
