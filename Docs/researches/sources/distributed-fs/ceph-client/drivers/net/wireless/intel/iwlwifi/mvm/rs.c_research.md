# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/rs.c

## Purpose
`rs.c` implements the legacy driver-side Intel MVM transmit rate-control algorithm and registers it with mac80211 as `iwl-mvm-rs`. When firmware TLC offload is unavailable, this file maintains per-station rate history, builds firmware Link Quality (`iwl_lq_cmd`) retry tables, reacts to Tx status, searches alternate modulation columns, starts aggregation, manages transmit power reduction, and exposes debugfs controls.

## Important APIs, Types, and Functions
- `rs_mvm_ops_drv` is the mac80211 `rate_control_ops` implementation. Its callbacks include `tx_status`, `get_rate`, `alloc_sta`, `rate_update`, and debugfs registration.
- `iwl_mvm_rs_rate_init()` dispatches either to firmware TLC (`rs-fw.c`) or the driver-side `rs_drv_rate_init()` path.
- `struct iwl_lq_sta` from `rs.h` is the main per-station state. This file fills its active/search tables, masks, timers, counters, retry command, and persistent statistics.
- `__iwl_mvm_rs_tx_status()` is the central Tx-status ingestion path. It validates the returned rate/color, updates TLC/TPC sliding windows, handles AMPDU and non-AMPDU accounting, and invokes `rs_rate_scale_perform()`.
- `rs_rate_scale_perform()` is the main state machine for rate up/down decisions, active/search table promotion or rollback, column exploration, AMSDU policy updates, TPC, and aggregation start.
- `rs_build_rates_table()` and `rs_fill_lq_cmd()` generate the firmware retry table, fallback columns, LQ color, aggregation limits, single-stream parameters, and RTS/P2P flags.
- `rs_ht_init()`, `rs_vht_init()`, `rs_get_initial_rate()`, and `rs_init_optimal_rate()` convert station capabilities and RSSI into initial masks and starting rates.
- Debug helpers include fixed-rate programming, scale-table/stat-table reads, driver Tx stats, `ss_force`, and frame-stat reset/update under `CONFIG_IWLWIFI_DEBUGFS`/`CONFIG_MAC80211_DEBUGFS`.

## Control Flow
Initialization enters through `iwl_mvm_rs_rate_init()`. Without TLC offload, it takes `lq_sta->pers.lock`, clears volatile state up to `pers`, constructs active legacy/SISO/MIMO masks from station capabilities, sets max allowed indices, initializes BT/coex antenna masks and aggregation eligibility, then calls `rs_initialize_lq()`. That chooses an initial rate from RSSI and capability tables, derives the current column, assigns expected throughput tables, fills the firmware LQ command, and sends it to firmware.

Tx status enters through mac80211 `rs_drv_mac80211_tx_status()` or direct `iwl_mvm_rs_tx_status()`. The status path skips uninitialized stations, no-ACK/control cases, stale AMPDU status, stale LQ colors, and invalid returned rates. It maps firmware rate bits to `struct rs_rate`, accumulates success/failure into the active or search table, updates per-TID throughput used to start BA sessions, and updates TPC windows keyed by reduced transmit power. For legacy retries it walks the firmware retry table and attributes each attempt to the matching active/search column.

The scaling loop uses `IWL_RATE_MAX_WINDOW` sliding windows. Once enough failures or successes have accumulated, `rs_get_rate_action()` compares measured throughput for current/adjacent rates with expected throughput and success-ratio thresholds. A stay action may run `rs_tpc_perform()`. A rate update rebuilds the LQ command and may adjust AMSDU policy. When stay limits expire, `rs_stay_in_table()` opens a search cycle, `rs_get_next_column()` chooses an unvisited and allowed modulation/antenna/SGI column, and `rs_switch_to_column()` fills the alternate table. The next status either promotes the search table if measured throughput improves or returns to the old active table.

## State and Persistence
`struct iwl_lq_sta` is split into volatile state and `pers`, and initialization uses `memset(..., offsetof(..., pers))` to preserve debug settings, RSSI, max aggregate buffer size, cumulative per-column Tx stats, driver pointer, and spinlock. Volatile state includes active/search table index, search state, throughput counters, visited columns, supported rate masks, LQ command, aggregate flags, TPC reduction, and last rate. `iwl_rate_scale_data` stores a 62-packet bitmap plus counters and fixed-point success ratio. `tid_data` in `struct iwl_mvm_sta` persists BA-session-related counters outside the RS object. Debug fixed rates and forced STBC/BFER/SISO settings persist in `pers`.

## Dependencies and Integration Points
The file integrates tightly with mac80211 rate-control callbacks, mac80211 BA sessions, firmware LQ commands, firmware rate bit encodings, MVM station/vif wrappers, BT coexistence policy, firmware API capability flags, debugfs, and RX RSSI updates from `rx.c` through `rs_update_last_rssi()`. It calls `rs_fw_get_max_amsdu_len()` from `rs-fw.c` even in driver-RS mode so AMSDU sizing remains common. `iwl_mvm_tx_protection()` dispatches to either the driver LQ flag update or the firmware-offload stub.

## Risks
- The active/search state machine is sensitive to stale firmware responses. LQ color mismatches are handled with a resync counter, but missed color updates can delay adaptation.
- Rate encoding/decoding spans HT, VHT, HE, STBC, BF, LDPC, NSS, antenna, and channel-width bitfields; incorrect masks can corrupt retry tables.
- Search-column decisions mix capability, BT coexistence, antenna availability, expected throughput, aggregation state, and SGI support. A bad check can trap a station in a poor column or attempt unsupported MIMO.
- The sliding-window algorithm needs enough traffic to converge; sparse traffic falls back to RSSI-derived reported rates.
- Debug fixed-rate mode bypasses normal scaling and is explicitly not self-recovering without reconfiguration.
- TPC decisions rely on windows indexed by reduced power; invalid firmware metadata or status attribution can cause over-aggressive power reduction.

## Test Signals
- Unit-level or trace-driven testing should verify `rs_rate_from_ucode_rate()` and `ucode_rate_from_rs_rate()` round trips for legacy, HT, VHT, HE, SISO, MIMO2, STBC, SGI, LDPC, and BF combinations.
- Tx-status replay should show sliding-window counters, active/search table promotion, rollback, and LQ color resync behavior.
- Debugfs `rate_scale_table`, `rate_stats_table`, `drv_tx_stats`, `reduced_tpc`, and `ss_force` should reflect live state and accept valid writes.
- BT coexistence scenarios should prevent MIMO/TPC when policy forbids them and force a new search from MIMO.
- Long idle gaps should trigger RS reinitialization. Aggregation should begin only after per-TID thresholds while station state is authorized and aggregation is off.
