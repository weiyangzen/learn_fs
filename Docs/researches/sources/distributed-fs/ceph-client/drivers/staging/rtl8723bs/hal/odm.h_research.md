# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/odm.h

## Purpose

`odm.h` is the primary ODM contract header for the RTL8723BS dynamic-management subsystem. It defines support flags, wireless/interface/chip enums, rate-adaptive and PHY-info types, RF calibration state, antenna/diversity state, `struct dm_odm_t`, configuration type enums, external swing tables, and ODM public prototypes. The source was read as a complete 1122-line file.

## Important APIs, Types, and Functions

The most important type is `struct dm_odm_t`, which aggregates adapter pointer, fixed chip metadata, dynamic driver-state pointers, linked/RSSI/BT/adaptivity fields, station pointer array, `struct dig_t`, `struct ps_t`, `struct cfo_tracking`, `struct edca_t`, `struct odm_rf_cal_t`, antenna/path diversity state, and TX power tracking swing state. Other key types are `struct odm_phy_info`, `struct odm_packet_info`, `struct odm_rate_adaptive`, `struct swat_t`, `struct fat_t`, `struct pathdiv_t`, `struct ant_detected_info`, and `enum odm_cmninfo_e`. Prototypes expose `ODM_DMInit`, `ODM_DMWatchdog`, common-info APIs, rate-bitmap APIs, TX power tracking, and timer hooks.

## Control Flow

There is no executable flow in the header. It defines the state and function surface consumed by `odm.c`, `rtl8723b_dm.c`, PHY status parsing, register configuration, and ODM submodules.

## State and Persistence Behavior

The header defines adapter-session state rather than owning storage. `dm_odm_t` persists inside `hal_com_data` after `rtw_hal_data_init` and is reset by `rtl8723b_init_dm_priv`. Many fields are pointers into MLME, security, traffic, power, and station structures; those are live views of changing driver state.

## Dependencies and Integration Points

It includes smaller ODM submodule headers and is included through `odm_precomp.h`. It is the contract among HAL DM setup, watchdog, PHY status query, register table application, RF calibration, H2C RSSI reporting, and rate adaptation.

## Risks and Edge Cases

The structure is large and contains many legacy fields not used by this trimmed staging driver, increasing risk of stale assumptions. Duplicate macro definitions exist for traffic and SW antenna steps. Some prototypes are declared but implemented elsewhere or not present in this subset, so compile/link coverage is needed. Pointer-hook fields can be dereferenced by ODM code without local NULL checks.

## Test Signals

Compile coverage with all ODM consumers, structure initialization tests after `memset`, sparse/clang warnings for unused or mismatched declarations, and watchdog tests that exercise fields sourced through common-info hooks are the main signals.
