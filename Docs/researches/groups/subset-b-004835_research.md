# Research: subset-b-004835

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/rs-fw.c -->
## sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/rs-fw.c

### Purpose
`rs-fw.c` implements the firmware-offloaded transmit rate-control path for the Intel `iwlwifi` MVM driver. Instead of running the full driver-side rate-scaling state machine, it translates mac80211 station/link capabilities into firmware `TLC_MNG_CONFIG_CMD` payloads, handles firmware TLC update notifications, and maintains the small persistent per-link RS state needed by debug/status paths.

### Important APIs, Types, and Functions
- `iwl_mvm_rs_fw_rate_init()` is the central entry point. It builds `struct iwl_tlc_config_cmd_v4`, derives the firmware station ID from `mvmsta->link[link_id]`, resets non-persistent `lq_sta->rs_fw` state, programs supported rates, updates mac80211 aggregate limits, and sends the command asynchronously.
- `rs_fw_set_supp_rates()` selects the firmware mode in priority order: EHT, HE, VHT, HT, then non-HT. It populates `non_ht_rates` and the `ht_rates[NSS][BW]` matrix.
- `rs_fw_eht_set_enabled_rates()`, `rs_fw_he_set_enabled_rates()`, and `rs_fw_vht_set_enabled_rates()` intersect peer RX capabilities with local TX capabilities and station NSS/SMPS limits.
- `rs_fw_get_config_flags()` derives LDPC, STBC, HE DCM NSS1, and EHT extra-LTF related flags from local configuration, station capabilities, and sband capabilities.
- `iwl_mvm_tlc_update_notif()` consumes firmware TLC notifications, updates `last_rate_n_flags`, and applies firmware-selected AMSDU policy to `mvmsta`, `link_sta->agg`, and per-TID max AMSDU sizes.
- `rs_fw_get_max_amsdu_len()` maps HT/VHT/HE 6 GHz/EHT capabilities to the max MPDU length used for AMSDU enablement.
- `iwl_mvm_rs_add_sta_link()` and `iwl_mvm_rs_add_sta()` initialize persistent `struct iwl_lq_sta_rs_fw` fields.

### Control Flow
The rate-init path starts from `iwl_mvm_rs_fw_rate_init()`, which collects band capabilities through mac80211 helpers, computes channel width from `link_sta->bandwidth`, computes feature flags, and records `sta_id` under RCU. It clears the volatile part of `struct iwl_lq_sta_rs_fw` up to `pers`, then calls `rs_fw_set_supp_rates()` to choose the best supported PHY mode. The command is sent as v4 when supported, translated to v3/v2 layout for older firmware, or rejected with `-EINVAL` for unsupported future command versions.

The notification path is asynchronous. `iwl_mvm_tlc_update_notif()` enters RCU, maps firmware station ID to mac80211 station and link station, validates that the link still exists, and then handles only the fields indicated by notification flags. Rate notifications update cached rate display state. AMSDU notifications are range-checked against current link limits and ignored if debugfs has overridden `orig_amsdu_len`; otherwise they update enabled TIDs, max length, per-TID aggregate lengths, and trigger `ieee80211_sta_recalc_aggregates()`.

### State and Persistence
The firmware-offload state is intentionally small. `last_rate_n_flags` is volatile and reset on rate init. The nested `pers` fields in `struct iwl_lq_sta_rs_fw` persist across rate reinitialization and store station ID, chain RSSI history, last RSSI, driver back-pointer, and debug fixed-rate data. AMSDU decisions persist in `struct iwl_mvm_sta` (`amsdu_enabled`, `max_amsdu_len`) and in `struct ieee80211_link_sta::agg`. `orig_amsdu_len` protects debug overrides from being silently overwritten by firmware updates.

### Dependencies and Integration Points
This file depends on mac80211 station/link capability structures, MVM station/link wrappers, firmware command version lookup, endian conversion helpers, RCU station maps, and firmware API constants from `fw-api.h`. It is selected by `iwl_mvm_rs_rate_init()` in `rs.c` when `iwl_mvm_has_tlc_offload(mvm)` is true. It also shares debug frame-stat reset and AMSDU sizing behavior with the driver-side RS path.

### Risks
- Capability intersection is dense and version-sensitive. EHT 20 MHz-only handling, 160/320 MHz indices, NSS maps, and SMPS pruning can silently under-advertise or over-advertise rates if any mac80211 structure semantics change.
- Command-version translation must remain aligned with firmware ABI layouts; the v3/v2 fallback deliberately truncates fields.
- `iwl_mvm_tlc_update_notif()` receives updates during station removal, so RCU validation is critical. Missed null/ERR checks could dereference stale station/link state.
- AMSDU size handling intentionally disables AMSDU by setting per-TID length to `1`; future mac80211 changes could make that convention fragile.
- `rs_fw_tx_protection()` is a stub, so RTS/CTS protection requests are not effective under TLC offload.

### Test Signals
- Association with EHT, HE, VHT, HT, and legacy peers should emit expected `TLC CONFIG CMD` debug logs for mode, width, chains, flags, non-HT rates, and `ht_rates`.
- Firmware TLC notifications should update debug last-rate output and `link_sta->agg.max_rc_amsdu_len` without WARNs.
- 20 MHz VHT should not advertise MCS9; static SMPS should clear NSS2 rates.
- 6 GHz HE max MPDU and 2.4 GHz EHT max MPDU cases should produce expected AMSDU lengths.
- Station removal during TLC notification should log the invalid RCU pointer path and not crash.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/rs-fw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/rs.c -->
## sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/rs.c

### Purpose
`rs.c` implements the legacy driver-side Intel MVM transmit rate-control algorithm and registers it with mac80211 as `iwl-mvm-rs`. When firmware TLC offload is unavailable, this file maintains per-station rate history, builds firmware Link Quality (`iwl_lq_cmd`) retry tables, reacts to Tx status, searches alternate modulation columns, starts aggregation, manages transmit power reduction, and exposes debugfs controls.

### Important APIs, Types, and Functions
- `rs_mvm_ops_drv` is the mac80211 `rate_control_ops` implementation. Its callbacks include `tx_status`, `get_rate`, `alloc_sta`, `rate_update`, and debugfs registration.
- `iwl_mvm_rs_rate_init()` dispatches either to firmware TLC (`rs-fw.c`) or the driver-side `rs_drv_rate_init()` path.
- `struct iwl_lq_sta` from `rs.h` is the main per-station state. This file fills its active/search tables, masks, timers, counters, retry command, and persistent statistics.
- `__iwl_mvm_rs_tx_status()` is the central Tx-status ingestion path. It validates the returned rate/color, updates TLC/TPC sliding windows, handles AMPDU and non-AMPDU accounting, and invokes `rs_rate_scale_perform()`.
- `rs_rate_scale_perform()` is the main state machine for rate up/down decisions, active/search table promotion or rollback, column exploration, AMSDU policy updates, TPC, and aggregation start.
- `rs_build_rates_table()` and `rs_fill_lq_cmd()` generate the firmware retry table, fallback columns, LQ color, aggregation limits, single-stream parameters, and RTS/P2P flags.
- `rs_ht_init()`, `rs_vht_init()`, `rs_get_initial_rate()`, and `rs_init_optimal_rate()` convert station capabilities and RSSI into initial masks and starting rates.
- Debug helpers include fixed-rate programming, scale-table/stat-table reads, driver Tx stats, `ss_force`, and frame-stat reset/update under `CONFIG_IWLWIFI_DEBUGFS`/`CONFIG_MAC80211_DEBUGFS`.

### Control Flow
Initialization enters through `iwl_mvm_rs_rate_init()`. Without TLC offload, it takes `lq_sta->pers.lock`, clears volatile state up to `pers`, constructs active legacy/SISO/MIMO masks from station capabilities, sets max allowed indices, initializes BT/coex antenna masks and aggregation eligibility, then calls `rs_initialize_lq()`. That chooses an initial rate from RSSI and capability tables, derives the current column, assigns expected throughput tables, fills the firmware LQ command, and sends it to firmware.

Tx status enters through mac80211 `rs_drv_mac80211_tx_status()` or direct `iwl_mvm_rs_tx_status()`. The status path skips uninitialized stations, no-ACK/control cases, stale AMPDU status, stale LQ colors, and invalid returned rates. It maps firmware rate bits to `struct rs_rate`, accumulates success/failure into the active or search table, updates per-TID throughput used to start BA sessions, and updates TPC windows keyed by reduced transmit power. For legacy retries it walks the firmware retry table and attributes each attempt to the matching active/search column.

The scaling loop uses `IWL_RATE_MAX_WINDOW` sliding windows. Once enough failures or successes have accumulated, `rs_get_rate_action()` compares measured throughput for current/adjacent rates with expected throughput and success-ratio thresholds. A stay action may run `rs_tpc_perform()`. A rate update rebuilds the LQ command and may adjust AMSDU policy. When stay limits expire, `rs_stay_in_table()` opens a search cycle, `rs_get_next_column()` chooses an unvisited and allowed modulation/antenna/SGI column, and `rs_switch_to_column()` fills the alternate table. The next status either promotes the search table if measured throughput improves or returns to the old active table.

### State and Persistence
`struct iwl_lq_sta` is split into volatile state and `pers`, and initialization uses `memset(..., offsetof(..., pers))` to preserve debug settings, RSSI, max aggregate buffer size, cumulative per-column Tx stats, driver pointer, and spinlock. Volatile state includes active/search table index, search state, throughput counters, visited columns, supported rate masks, LQ command, aggregate flags, TPC reduction, and last rate. `iwl_rate_scale_data` stores a 62-packet bitmap plus counters and fixed-point success ratio. `tid_data` in `struct iwl_mvm_sta` persists BA-session-related counters outside the RS object. Debug fixed rates and forced STBC/BFER/SISO settings persist in `pers`.

### Dependencies and Integration Points
The file integrates tightly with mac80211 rate-control callbacks, mac80211 BA sessions, firmware LQ commands, firmware rate bit encodings, MVM station/vif wrappers, BT coexistence policy, firmware API capability flags, debugfs, and RX RSSI updates from `rx.c` through `rs_update_last_rssi()`. It calls `rs_fw_get_max_amsdu_len()` from `rs-fw.c` even in driver-RS mode so AMSDU sizing remains common. `iwl_mvm_tx_protection()` dispatches to either the driver LQ flag update or the firmware-offload stub.

### Risks
- The active/search state machine is sensitive to stale firmware responses. LQ color mismatches are handled with a resync counter, but missed color updates can delay adaptation.
- Rate encoding/decoding spans HT, VHT, HE, STBC, BF, LDPC, NSS, antenna, and channel-width bitfields; incorrect masks can corrupt retry tables.
- Search-column decisions mix capability, BT coexistence, antenna availability, expected throughput, aggregation state, and SGI support. A bad check can trap a station in a poor column or attempt unsupported MIMO.
- The sliding-window algorithm needs enough traffic to converge; sparse traffic falls back to RSSI-derived reported rates.
- Debug fixed-rate mode bypasses normal scaling and is explicitly not self-recovering without reconfiguration.
- TPC decisions rely on windows indexed by reduced power; invalid firmware metadata or status attribution can cause over-aggressive power reduction.

### Test Signals
- Unit-level or trace-driven testing should verify `rs_rate_from_ucode_rate()` and `ucode_rate_from_rs_rate()` round trips for legacy, HT, VHT, HE, SISO, MIMO2, STBC, SGI, LDPC, and BF combinations.
- Tx-status replay should show sliding-window counters, active/search table promotion, rollback, and LQ color resync behavior.
- Debugfs `rate_scale_table`, `rate_stats_table`, `drv_tx_stats`, `reduced_tpc`, and `ss_force` should reflect live state and accept valid writes.
- BT coexistence scenarios should prevent MIMO/TPC when policy forbids them and force a new search from MIMO.
- Long idle gaps should trigger RS reinitialization. Aggregation should begin only after per-TID thresholds while station state is authorized and aggregation is off.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/rs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/rs.h -->
## sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/rs.h

### Purpose
`rs.h` is the shared contract for Intel MVM rate scaling. It defines rate indexes, masks, table types, rate descriptors, persistent and volatile per-station state for both firmware-offloaded and driver-side RS, and the public functions used by the rest of MVM to initialize, update, and debug rate control.

### Important APIs, Types, and Functions
- `struct iwl_rs_rate_info` maps driver rate indexes to firmware PLCP values for legacy, HT SISO/MIMO2, and VHT SISO/MIMO2.
- `enum iwl_table_type` and `struct rs_rate` describe a concrete rate column: legacy/HT/VHT/HE, index, antenna mask, bandwidth, SGI, LDPC, STBC, and BF.
- The `is_type_*`, `is_*`, and `is_ht20/40/80/160` helpers are used throughout `rs.c` to keep mode decisions readable.
- `struct iwl_lq_sta_rs_fw` stores the compact firmware-offload state with persistent station ID, RSSI, chain signal, and debug fields.
- `struct iwl_rate_scale_data`, `struct rs_rate_stats`, `struct iwl_scale_tbl_info`, and `struct iwl_lq_sta` define the driver-side sliding windows, expected-throughput tables, active/search tables, RS state, masks, LQ command, aggregation/TPC state, and persistent debug/statistics fields.
- `RS_DRV_DATA_PACK()` and related masks encode reduced Tx power and LQ color into `ieee80211_tx_info.status_driver_data[0]`.
- Public APIs include `iwl_mvm_rs_rate_init()`, `iwl_mvm_rs_tx_status()`, rate-control register/unregister, `iwl_mvm_tx_protection()`, station add helpers, TLC notification handling, and `rs_fw_get_max_amsdu_len()`.

### Control Flow
The header itself has no runtime flow, but it encodes the boundary between subsystems. mac80211/MVM station setup calls `iwl_mvm_rs_add_sta*()` and `iwl_mvm_rs_rate_init()`. Tx completion calls `iwl_mvm_rs_tx_status()`. Firmware TLC notifications call `iwl_mvm_tlc_update_notif()`. Debug or protection paths call `iwl_mvm_reset_frame_stats()` and `iwl_mvm_tx_protection()`. The implementation selected at runtime is hidden behind these declarations.

### State and Persistence
The most important design choice is the placement of `pers` as the last field of both `struct iwl_lq_sta_rs_fw` and `struct iwl_lq_sta`. Implementations clear all fields before `pers` during reinitialization, preserving chain/RSSI history, debug fixed-rate controls, forced single-stream settings, cumulative stats, driver back-pointers, and locks. Driver RS has two `iwl_scale_tbl_info` entries (`LQ_SIZE == 2`) for active/search behavior. Firmware RS keeps only last-rate plus persistent per-link metadata because the firmware owns the adaptation state.

### Dependencies and Integration Points
The header includes mac80211, firmware API, transport, and device config headers. Its public structures are embedded in MVM station/link structures outside this file set. The rate table constants must match firmware definitions and `iwl_rate_mcs()` indexes. The status-driver-data packing is a private MVM/mac80211 contract that must match Tx status production and consumption.

### Risks
- Any field layout changes around `pers` can break the `memset(..., offsetof(..., pers))` preservation pattern used in both `rs.c` and `rs-fw.c`.
- Rate-count and mask constants must stay aligned with firmware and mac80211 expectations; `IWL_RATE_COUNT`, HE MCS indexes, and `LINK_QUAL_MAX_RETRY_NUM` are especially central.
- `status_driver_data` packing stores integers through `void *`; it depends on pointer-sized casts and matching masks on both producer and consumer sides.
- Helper macros are widely used and have no type safety beyond C expression checks.

### Test Signals
- Build coverage should compile both TLC-offload and driver-RS paths, with and without debugfs options.
- Static checks should confirm `pers` remains last and `offsetof(..., pers)` users still preserve intended fields.
- Tx status tests should validate `RS_DRV_DATA_PACK`, `RS_DRV_DATA_LQ_COLOR_GET`, and reduced-TPC extraction.
- Rate-table tests should exercise each `enum iwl_table_type` and column conversion path in `rs.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/rs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/rx.c -->
## sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/rx.c

### Purpose
`rx.c` handles receive-side firmware notifications for the Intel MVM driver. It pairs PHY and MPDU notifications, builds mac80211 RX status and SKBs, updates RSSI/TCM/statistics state, translates firmware crypto and rate metadata, triggers debug collection, and reports BA-window filtering information.

### Important APIs, Types, and Functions
- `iwl_mvm_rx_rx_phy_cmd()` stores the latest PHY information in `mvm->last_phy_info`, increments `ampdu_ref`, and updates debug AMPDU counters.
- `iwl_mvm_rx_rx_mpdu()` is the main MPDU handler. It validates packet length, allocates an SKB, fills `ieee80211_rx_status`, resolves the station, handles decryption status, updates RSSI/TCM/checksum state, decodes rate flags, records debug frame stats, and passes the packet to mac80211.
- `iwl_mvm_pass_packet_to_mac80211()` constructs the SKB using head data plus an RX page fragment when the packet is larger than the small head allocation.
- `iwl_mvm_set_mac80211_rx_flag()` maps firmware security status to mac80211 `RX_FLAG_DECRYPTED` and crypto header lengths, or drops frames with failed MIC/ICV checks.
- `iwl_mvm_get_signal_strength()` decodes per-chain energy and updates `rx_status->signal`, `chains`, and `chain_signal`.
- `iwl_mvm_rx_handle_tcm()` updates traffic classification manager counters, RX airtime, and U-APSD non-aggregation detection.
- Statistics handlers include legacy `iwl_mvm_handle_rx_statistics()`, TLV versions 14/15, system operational notifications, part1 radio-time notifications, per-link MLO handling, per-phy channel load, per-station average energy, and firmware debug trigger checks.
- `iwl_mvm_window_status_notif()` forwards BA-window bitmaps to `ieee80211_mark_rx_ba_filtered_frames()`.

### Control Flow
For older RX API flows, firmware sends a PHY notification followed by one or more MPDU notifications. `iwl_mvm_rx_rx_phy_cmd()` snapshots the PHY metadata, and `iwl_mvm_rx_rx_mpdu()` uses that snapshot for timestamps, channel, RSSI, rate, AMPDU grouping, and frame time. The MPDU path validates lengths before accessing the header/status trailer, marks CRC/FIFO errors for monitor visibility, finds the station by firmware station ID or source address, rejects protected multicast before authorization, and asks `iwl_mvm_set_mac80211_rx_flag()` whether hardware decryption succeeded. Under RCU it updates station-local state, CSA unblock state, rate-scaling RSSI, low-RSSI debug triggers, TCM, and RX checksum offload.

After station handling, the MPDU path converts firmware rate bits into mac80211 RX encoding. HT, VHT, and legacy are decoded separately, including bandwidth, SGI, LDPC, STBC, NSS, and BF flags. It then handles scheduled-scan pass-all beacon/probe response state, timestamps beacons/probe responses with boottime, and finally passes the SKB to mac80211.

Statistics flow is version-gated. If the system statistics command exists, legacy `STATISTICS_NOTIFICATION` is ignored. TLV version 14/15 handlers verify payload/header size and notification version, update beacon stats, radio times, per-station energy, per-mac TCM airtime/RX bytes when stats were cleared, and per-phy channel load. Newer system operational stats use per-link data and aggregate airtime/RX bytes per vif ID only when `mvm->statistics_clear` is set to avoid double counting.

### State and Persistence
`mvm->last_phy_info` and `mvm->ampdu_ref` bridge PHY and MPDU notifications. `rx_status` is per-SKB and handed to mac80211. Persistent updates include `mvmsta->deflink.avg_energy`, `mvmvif->link[*].beacon_stats`, `mvmvif->deflink.beacon_stats`, `mvm->radio_stats`, `mvm->rx_stats`/`rx_stats_v3`, `mvm->phy_ctxts[*].channel_load_*`, TCM counters, and RS RSSI via `rs_update_last_rssi()`. CQM and BT-coex last-event thresholds are stored in link beacon-filter data to avoid duplicate notifications.

### Dependencies and Integration Points
This file depends on firmware RX/status structures, MVM station/vif maps, mac80211 RX APIs, checksum offload flags, debug trigger infrastructure, TCM work, BT coexistence RSSI events, rate-scaling RSSI state in `rs.c`, and BA reordering support. Its behavior is tied to firmware API version helpers such as `iwl_mvm_has_new_rx_api()`, `iwl_mvm_has_new_rx_stats_api()`, `iwl_fw_lookup_notif_ver()`, and command-version lookup.

### Risks
- The PHY/MPDU split assumes `mvm->last_phy_info` is the correct metadata for the following MPDU sequence; ordering bugs or API transitions can misattribute rates, RSSI, or AMPDU references.
- Length validation is critical because the handler computes header and trailer offsets inside firmware-provided buffers.
- Security status mapping must be conservative. Incorrect MIC/ICV handling can either drop valid frames or pass corrupted/decrypted frames incorrectly.
- Statistics format handling has many version branches; a firmware ABI mismatch can silently skip stats or double-count airtime if clear flags are misunderstood.
- RCU station/vif lookups must tolerate station removal and CSA transitions.
- The SKB fragment path steals the RX page, so offset/length errors could corrupt packet delivery or page ownership.

### Test Signals
- RX MPDU tests should cover bad length, bad CRC/FIFO, encrypted CCMP/TKIP/WEP/EXT cases, multicast before authorization, and missing station mapping.
- Rate decode coverage should include HT, VHT, legacy, SGI, LDPC, STBC, BF, and bandwidth cases.
- Monitor-mode paths should preserve CRC-failed frames with `RX_FLAG_FAILED_FCS_CRC`.
- Statistics tests should replay legacy, TLV v14/v15, and system operational notifications and verify beacon stats, radio stats, average energy, TCM updates, and per-phy channel load.
- BA-window notifications should mark filtered frames only for valid TID entries with nonzero MPDU counts and valid station IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/rx.c -->
