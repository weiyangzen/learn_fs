# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/rs.h

## Purpose
`rs.h` is the shared contract for Intel MVM rate scaling. It defines rate indexes, masks, table types, rate descriptors, persistent and volatile per-station state for both firmware-offloaded and driver-side RS, and the public functions used by the rest of MVM to initialize, update, and debug rate control.

## Important APIs, Types, and Functions
- `struct iwl_rs_rate_info` maps driver rate indexes to firmware PLCP values for legacy, HT SISO/MIMO2, and VHT SISO/MIMO2.
- `enum iwl_table_type` and `struct rs_rate` describe a concrete rate column: legacy/HT/VHT/HE, index, antenna mask, bandwidth, SGI, LDPC, STBC, and BF.
- The `is_type_*`, `is_*`, and `is_ht20/40/80/160` helpers are used throughout `rs.c` to keep mode decisions readable.
- `struct iwl_lq_sta_rs_fw` stores the compact firmware-offload state with persistent station ID, RSSI, chain signal, and debug fields.
- `struct iwl_rate_scale_data`, `struct rs_rate_stats`, `struct iwl_scale_tbl_info`, and `struct iwl_lq_sta` define the driver-side sliding windows, expected-throughput tables, active/search tables, RS state, masks, LQ command, aggregation/TPC state, and persistent debug/statistics fields.
- `RS_DRV_DATA_PACK()` and related masks encode reduced Tx power and LQ color into `ieee80211_tx_info.status_driver_data[0]`.
- Public APIs include `iwl_mvm_rs_rate_init()`, `iwl_mvm_rs_tx_status()`, rate-control register/unregister, `iwl_mvm_tx_protection()`, station add helpers, TLC notification handling, and `rs_fw_get_max_amsdu_len()`.

## Control Flow
The header itself has no runtime flow, but it encodes the boundary between subsystems. mac80211/MVM station setup calls `iwl_mvm_rs_add_sta*()` and `iwl_mvm_rs_rate_init()`. Tx completion calls `iwl_mvm_rs_tx_status()`. Firmware TLC notifications call `iwl_mvm_tlc_update_notif()`. Debug or protection paths call `iwl_mvm_reset_frame_stats()` and `iwl_mvm_tx_protection()`. The implementation selected at runtime is hidden behind these declarations.

## State and Persistence
The most important design choice is the placement of `pers` as the last field of both `struct iwl_lq_sta_rs_fw` and `struct iwl_lq_sta`. Implementations clear all fields before `pers` during reinitialization, preserving chain/RSSI history, debug fixed-rate controls, forced single-stream settings, cumulative stats, driver back-pointers, and locks. Driver RS has two `iwl_scale_tbl_info` entries (`LQ_SIZE == 2`) for active/search behavior. Firmware RS keeps only last-rate plus persistent per-link metadata because the firmware owns the adaptation state.

## Dependencies and Integration Points
The header includes mac80211, firmware API, transport, and device config headers. Its public structures are embedded in MVM station/link structures outside this file set. The rate table constants must match firmware definitions and `iwl_rate_mcs()` indexes. The status-driver-data packing is a private MVM/mac80211 contract that must match Tx status production and consumption.

## Risks
- Any field layout changes around `pers` can break the `memset(..., offsetof(..., pers))` preservation pattern used in both `rs.c` and `rs-fw.c`.
- Rate-count and mask constants must stay aligned with firmware and mac80211 expectations; `IWL_RATE_COUNT`, HE MCS indexes, and `LINK_QUAL_MAX_RETRY_NUM` are especially central.
- `status_driver_data` packing stores integers through `void *`; it depends on pointer-sized casts and matching masks on both producer and consumer sides.
- Helper macros are widely used and have no type safety beyond C expression checks.

## Test Signals
- Build coverage should compile both TLC-offload and driver-RS paths, with and without debugfs options.
- Static checks should confirm `pers` remains last and `offsetof(..., pers)` users still preserve intended fields.
- Tx status tests should validate `RS_DRV_DATA_PACK`, `RS_DRV_DATA_LQ_COLOR_GET`, and reduced-TPC extraction.
- Rate-table tests should exercise each `enum iwl_table_type` and column conversion path in `rs.c`.
