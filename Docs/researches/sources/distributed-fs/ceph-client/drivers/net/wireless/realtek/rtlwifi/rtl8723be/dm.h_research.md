# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723be/dm.h

## Purpose
Declares the RTL8723BE dynamic-management interface and the register/threshold constants that drive DIG, BB power saving, EDCA, TX power tracking, ATC/CFO tracking, antenna selection, and Bluetooth RSSI policy.

## Important APIs, Types, And Functions
Key constants include RF/BB/MAC register aliases, `DM_DIG_*` false-alarm thresholds, rate-adaptive states, TX high-power levels, `TXPWRTRACK_MAX_IDX`, CFO thresholds, and antenna identifiers. Enums define 1R CCA mode, RF save/normal mode, software antenna switching, and power tracking method (`BBSWING` or `TXAGC`). Public prototypes expose initialization, watchdog, DIG write, thermal tracking, rate-mask initialization, TX-power track adjustment, and antenna selection/statistics callbacks.

## Control Flow
No executable flow, but this header defines which knobs `dm.c` can drive and what external rtlwifi code can invoke. `GET_UNDECORATED_AVERAGE_RSSI()` selects the relevant smoothed RSSI source depending on adhoc versus infrastructure operation.

## State And Persistence
No state is stored in the header. Constants describe persistent hardware register addresses and stable policy thresholds; changing them alters runtime behavior across watchdog iterations.

## Dependencies And Integration Points
Included by `dm.c`, `hw.c`, and `phy.c`; it also depends on common rtlwifi structures such as `struct rtl_priv`. Bluetooth RSSI masks align with btcoexist logic, and antenna constants align with descriptor antenna-selection hooks.

## Risks
Register aliases and thresholds are global assumptions. Incorrect register numbers can redirect watchdog writes into unrelated BB/MAC state. Threshold changes can make DIG, CFO tracking, or TX-power tracking unstable across all runtime modes.

## Test Signals
Build coverage catches prototype drift. Runtime signals come from DM watchdog behavior: stable DIG values, no excessive false alarm response, correct thermal compensation, and expected Bluetooth coexistence decisions.
