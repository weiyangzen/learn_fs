# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/core.h

## Purpose
Public declarations for the shared rtlwifi core, including `rtl_ops`, firmware callbacks, RF delay helpers, command TX, LED setup, DIG initialization, beacon work, and dynamic mechanism thresholds.

## Important APIs, Types, And Functions
`RTL_SUPPORTED_FILTERS` declares accepted mac80211 filter bits. DIG constants define RSSI/false-alarm thresholds, IGI bounds, and backoff limits. Enums encode CCK packet detection, DIG external-port stages, and connection states. Declared functions include `rtl_fw_cb()`, `rtl_wowlan_fw_cb()`, `rtl_rfreg_delay()`, `rtl_cmd_send_packet()`, `rtl_btc_status_false()`, and `rtl_dm_diginit()`.

## Control Flow
Included by shared and chip-specific code. `rtl_ops` is used for mac80211 registration, firmware callbacks are passed to request-firmware, and delay/DIG helpers support PHY/RF programming.

## State And Persistence
Owns no storage. It standardizes constants that initialize `struct dig_t`, filter behavior, and shared core callbacks.

## Dependencies And Integration Points
Requires mac80211, firmware, workqueue, and rtlwifi radio path types. It connects common core code with chip PHY/RF/LED/firmware/beacon units.

## Risks
Filter mask changes alter mac80211-visible behavior. DIG threshold changes affect receive sensitivity across chips. Enum values are driver state-machine contracts.

## Test Signals
Build all users, verify mac80211 registration, RX filter behavior, and DIG behavior under low/high RSSI and false-alarm conditions.
