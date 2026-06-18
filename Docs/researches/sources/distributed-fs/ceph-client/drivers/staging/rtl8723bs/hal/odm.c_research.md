# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/odm.c

## Purpose

`odm.c` is the central ODM dynamic-management coordinator for RTL8723BS. It contains OFDM/CCK swing tables, initializes common ODM state, computes rate-adaptation masks, monitors RSSI, initializes antenna and thermal tracking state, runs the periodic ODM watchdog, and exposes common-info init/hook/update APIs used by chip-specific DM setup. The source was read as a complete 1026-line file.

## Important APIs, Types, and Functions

Important objects and APIs include `OFDMSwingTable_New`, `CCKSwingTable_Ch1_Ch13_New`, `CCKSwingTable_Ch14_New`, `ODM_Get_Rate_Bitmap`, `ODM_RAStateCheck`, `odm_TXPowerTrackingInit`, `ODM_TXPowerTrackingCheck`, `ODM_DMInit`, `ODM_DMWatchdog`, `ODM_CmnInfoInit`, `ODM_CmnInfoHook`, `ODM_CmnInfoPtrArrayHook`, and `ODM_CmnInfoUpdate`. Internal helpers include common-info self init/update, rate-adaptive mask refresh, RSSI monitor, software antenna detect init, and swing-index discovery.

## Control Flow

`ODM_DMInit` initializes hardware-derived common fields, DIG, NHM, adaptivity, rate adaptation, CFO tracking, EDCA turbo, RSSI monitoring, TX power tracking, RF calibration state, BB power saving, dynamic TX power, and software antenna state. `ODM_DMWatchdog` updates current channel/control-channel and station-count state, reads false-alarm and NHM counters, updates RSSI, runs DIG or low-power DIG depending on firmware PS mode, applies adaptivity and CCK packet-detect thresholds, then, unless power saving is active, refreshes rate masks, EDCA, CFO tracking, and thermal TX power tracking.

## State and Persistence Behavior

The persistent runtime state is `struct dm_odm_t`, embedded in `hal_com_data`. It holds support-ability masks, fixed chip/interface/package metadata, pointers into driver state, linked/station/RSSI flags, station pointer array, DIG/FA/EDCA/CFO/RF-calibration substructures, swing indices, and thermal tracking values. Common-info hooks store live pointers rather than snapshots, so lifetime and update ordering are critical.

## Dependencies and Integration Points

The file depends on ODM submodules (`odm_DIG`, `odm_CfoTracking`, `odm_EdcaTurboCheck`, power-saving and TX-power modules), PHY register helpers, H2C RSSI reporting (`rtl8723b_set_rssi_cmd`), station rate update (`rtw_hal_update_ra_mask`), power-control state, MLME/station state, RF calibration (`ODM_TXPowerTrackingCallback_ThermalMeter`, `ODM_ClearTxPowerTrackingState`), and register definitions from ODM headers.

## Risks and Edge Cases

Common-info pointers can be NULL if `Update_ODM_ComInfo_8723b` did not hook them before `ODM_DMWatchdog`. `ODM_Get_Rate_Bitmap` trusts `macid` as an array index. The watchdog returns early when `pbPowerSaving` is true, skipping rate/EDCA/CFO/thermal work. Thermal tracking uses a two-phase trigger/callback sequence that depends on watchdog cadence. The swing tables and default indices must match RF calibration code expectations.

## Test Signals

Good signals include ODM init field snapshots, watchdog traces under linked/unlinked/LPS/power-saving states, rate-mask outputs for B/G/N modes and RSSI levels, RSSI monitor station aggregation tests, thermal tracking trigger/callback sequencing, and fault-injection for missing station pointers or disabled support abilities.
