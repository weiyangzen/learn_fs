# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/HalPhyRf.c

## Purpose

`HalPhyRf.c` provides generic ODM RF power-tracking glue for rtl8723bs and delegates chip-specific behavior to the 8723B calibration implementation. The file was read as a complete 273-line source.

## Important APIs, Types, and Functions

Public functions are `ConfigureTxpowerTrack`, `ODM_ClearTxPowerTrackingState`, and `ODM_TXPowerTrackingCallback_ThermalMeter`. `ConfigureTxpowerTrack` delegates to `ConfigureTxpowerTrack_8723B`. `ODM_ClearTxPowerTrackingState` resets swing indexes, delta/remnant power indexes, modify flags, and thermal baselines. `ODM_TXPowerTrackingCallback_ThermalMeter` is the main thermal watchdog callback.

## Control Flow

The thermal callback obtains the 8723B `txpwrtrack_cfg`, gets delta swing table pointers, reads RF thermal meter register `c.ThermalRegAddr`, exits if tracking is disabled or EEPROM thermal meter is invalid, updates a rolling average, computes deltas against previous thermal/LCK values, triggers LC calibration if threshold is crossed, maps thermal delta to path-specific positive/negative power index changes, clamps OFDM/CCK indexes, calls the chip-specific set-power function in `MIX_MODE`, updates base swing indexes, records the new thermal value, and resets `TXPowercount`.

## State and Persistence Behavior

The file mutates `pDM_Odm->RFCalibrateInfo`, including thermal history, average buffer/index, callback counters, delta power indexes, power offsets, OFDM/CCK indexes, Tx power changed flags, and LCK/IQK baselines. It also updates `BbSwingIdx*`, remnant swing indexes, and TxAGC modify flags. Persistent effects occur through chip-specific callbacks that write BB/RF/Tx power state.

## Dependencies and Integration Points

It includes `odm_precomp.h` and depends on `hal_com_data`, `struct dm_odm_t`, `struct txpwrtrack_cfg`, `PHY_QueryRFReg`, `PHY_SetTxPowerIndexByRateSection`, 8723B config callbacks, swing table constants, and ODM RF calibration state. It is usually driven by periodic dynamic mechanism/watchdog logic.

## Risks and Edge Cases

Several values are unsigned while negative offsets are represented through assignments to `u8`-like state in surrounding structures, so boundary behavior depends on struct field types. The callback assumes delta swing tables were populated by RF image loading. Invalid EEPROM thermal values disable tracking entirely. Only path A and optional path B are considered through `RfPathCount`; wrong path count or table size can miscalibrate power.

## Test Signals

Unit-style thermal delta tests, hardware traces for Tx power index updates, LCK trigger tests at threshold, checks that `ODM_ClearTxPowerTrackingState` is called after TxAGC changes, and watchdog tests with invalid EEPROM thermal values are useful signals.
