# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192ce/dm.h

## Purpose
This header defines RTL8192CE dynamic-management thresholds, flags, rate-adaptive states, TX high-power levels, and function prototypes shared by CE and common DM code.

## Important APIs, Types, And Functions
Key constants include `HAL_DM_DIG_DISABLE`, `HAL_DM_HIPWR_DISABLE`, false-alarm DIG thresholds, bandwidth auto-switch thresholds, rate-adaptive states, CCK/OFDM table sizes, TX high-power levels, and near-field TX-power thresholds. Prototypes include shared routines such as `rtl92c_dm_init()`, `rtl92c_dm_watchdog()`, `rtl92c_dm_write_dig()`, `rtl92c_dm_init_edca_turbo()`, `rtl92c_dm_check_txpower_tracking()`, `rtl92c_dm_rf_saving()`, and CE-specific `rtl92ce_dm_dynamic_txpower()`.

## Control Flow
The header itself is declarative. The constants steer watchdog decisions for DIG, EDCA turbo, RF saving, rate adaptation, BT coexistence, and dynamic TX power in `dm.c` and the shared `rtl8192c/dm_common` implementation.

## State And Persistence
No storage is declared. The constants govern runtime fields in `rtlpriv->dm` and related PHY state. Nothing persists across driver unload or device reset.

## Dependencies And Integration Points
It is included by CE DM/HW/PHY/RF/SW code and by common PHY code where scan-time DIG pause/resume calls `rtl92c_dm_write_dig()`.

## Risks And Edge Cases
Threshold constants are tightly coupled to Realtek PHY calibration assumptions. Changing them can affect sensitivity, false alarms, throughput, and regulatory behavior. Some definitions duplicate table lengths and sizes.

## Test Signals
DM watchdog logs, false-alarm counters, rate-mask changes, RF-saving transitions, dynamic TX-power level changes, and stable scan/link behavior are the main signals.
