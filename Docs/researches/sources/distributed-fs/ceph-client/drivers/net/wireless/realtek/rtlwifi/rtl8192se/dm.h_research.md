# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192se/dm.h

## Purpose
This header declares the RTL8192SE dynamic-management states, thresholds, flags, and public DM entry points. It provides the vocabulary used by `dm.c`, `hw.c`, and related PHY/firmware paths.

## Important APIs, Types, And Functions
Enums classify DIG algorithms (`dm_dig_alg`), two-port DIG algorithms (`dm_dig_two_port_alg`), debug mode, DIG on/off state, and rate-adaptive RSSI state (`dm_ratr_sta`). Macros define driver-vs-firmware DM type, high-power levels, disable flags, near-field TX power thresholds, DIG high-power thresholds, and minimum netcore value. Public functions are `rtl92s_dm_watchdog()`, `rtl92s_dm_init()`, and `rtl92s_dm_init_edca_turbo()`.

## Control Flow
The header has no executable flow. `sw.c` wires `rtl92s_dm_watchdog()` into HAL ops, `hw.c` calls `rtl92s_dm_init()` after hardware init, and QoS changes call `rtl92s_dm_init_edca_turbo()`.

## State And Persistence
The declarations map to state in shared rtlwifi structures, especially `rtlpriv->dm`, `rtlpriv->dm_digtable`, and `rtlpriv->ra`. Threshold macros are compile-time policy constants.

## Dependencies And Integration Points
It depends on `struct ieee80211_hw` and shared rtlwifi DM structures from included driver headers. Changing enum values or thresholds affects watchdog behavior, firmware command selection, rate table updates, and power behavior.

## Risks
Threshold changes can alter RF sensitivity, transmit power, and rate adaptation. Enum values may be stored or compared across modules; changing their order can break logic that assumes exact numeric states. Duplicate-looking high-power level macros (`TX_HIGH_PWR_LEVEL_*` and `TX_HIGHPWR_LEVEL_*`) require care when maintaining code.

## Test Signals
Build coverage should catch missing declarations. Runtime tests should verify watchdog invocation, EDCA reset on QoS changes, DIG threshold behavior, and dynamic TX power transitions after any enum or macro change.
