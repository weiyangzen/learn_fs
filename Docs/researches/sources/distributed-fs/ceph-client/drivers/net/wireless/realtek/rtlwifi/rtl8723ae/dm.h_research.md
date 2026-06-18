# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723ae/dm.h

## Purpose
`dm.h` defines RTL8723AE dynamic-management thresholds, enums, helper macros, and public DM entry points.

## APIs, Types, And Constants
It defines DIG disable flags, OFDM/CCK table sizes, bandwidth switch thresholds, false-alarm thresholds, rate-adaptive states, TX high-power levels, DM ownership modes, near-field TX-power thresholds, and BT RSSI state masks. `struct swat_t` tracks software antenna-switch attempts. Enums describe DIG operations, 1R CCA, RF save/normal state, and software antenna choices. `GET_UNDECORATED_AVERAGE_RSSI` abstracts station vs adhoc RSSI source.

## Control Flow, State, And Persistence
The header has no runtime flow but its constants govern watchdog state transitions in `dm.c` and coexistence decisions. Public functions initialize and periodically update hardware state; those updates persist in BB/RF/MAC registers.

## Dependencies And Integration Points
It is included by RTL8723AE DM and BT coexistence code and depends on rtlwifi/mac80211 structures through surrounding includes. It shares state meanings with common RTL8723 DM helpers and `rtlpriv->dm`.

## Risks And Test Signals
Risks include threshold changes causing oscillation, mismatch with `dm.c` expectations, and RSSI macro misuse. Signals are clean builds, stable DIG values, appropriate TX power reduction near APs, correct rate-adaptive transitions, and no regressions in low-power RF saving.
