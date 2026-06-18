# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/stats.h

## Purpose
Declares shared rtlwifi receive-statistics helper APIs and smoothing-window constants used by chip-specific RX descriptor code.

## Important APIs, Types, And Functions
Defines `PHY_RSSI_SLID_WIN_MAX` as 100, `PHY_LINKQUALITY_SLID_WIN_MAX` as 20, `PHY_BEACON_RSSI_SLID_WIN_MAX` as 10, and `RX_SMOOTH_FACTOR` as 20. Declares `rtl_query_rxpwrpercentage`, `rtl_evm_db_to_percentage`, `rtl_signal_scale_mapping`, and `rtl_process_phyinfo`.

## Control Flow
No runtime control flow exists in the header. It enables descriptor parsers to call shared signal conversion and smoothing routines.

## State And Persistence
No state is stored here. The constants size and tune in-memory rolling windows maintained by `stats.c`.

## Dependencies And Integration Points
Depends on surrounding includes for `u8`, `s8`, `long`, and `struct ieee80211_hw`. It is included by rtlwifi chip RX paths and by `stats.c`.

## Risks And Edge Cases
Changing constants alters smoothing behavior across all rtlwifi chips. Like several rtlwifi headers, it does not include all type providers itself, so it assumes inclusion after `wifi.h` or equivalent kernel headers.

## Test Signals
Build all rtlwifi chip modules and run RX signal reporting tests. Any change to constants should be checked against UI RSSI/link-quality stability and roaming decisions.
