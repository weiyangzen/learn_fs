# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723ae/hal_btc.h

## Purpose
`hal_btc.h` defines RTL8723AE Bluetooth coexistence policy constants, enums, C2H event metadata, and public policy-engine entry points.

## APIs, Types, And Constants
It defines BT TX/RX counter thresholds and levels, queue/power/coex toggles, TDMA/PTA/rate-adaptive/RF-corner modes, C2H close markers, BT traffic/profile/spec/state enums, `struct c2h_evt_hdr`, and C2H event IDs including `C2H_V0_BT_INFO`. It declares all-off routines, main coexistence execution, policy application, C2H handling, media notification, and LPS pre-entry coexistence shutdown.

## Control Flow, State, And Persistence
The header has no flow but encodes the state vocabulary for `hal_btc.c`. Thresholds classify BT counter totals; event IDs control C2H dispatch; TDMA/PTA constants become H2C command bits. Resulting policies persist in firmware mailboxes, PTA registers, and RF/BB state.

## Dependencies And Integration Points
It includes `../wifi.h`, `btc.h`, and `hal_bt_coexist.h`. It is used by DM, firmware/coexistence code, and C2H handling to coordinate Wi-Fi link state with BT profile/counter information.

## Risks And Test Signals
Risks include threshold changes that alter policy selection, mismatched C2H IDs, enum value drift, and prototype mismatches. Signals are clean builds, correct C2H BT info dispatch, expected counter-level classification, media-status H2C commands, and stable coexistence profile behavior.
