# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192ce/phy.h

## Purpose
This header declares the RTL8192CE PHY API and duplicates many RTL8192C common PHY constants for CE-local includes.

## Important APIs, Types, And Functions
It defines PHY command limits, IQK/APK counts, EFUSE offsets, TX-power maximums, and `RTL92C_MAX_PATH_NUM`. Prototypes include BB/RF access, MAC/BB/RF configuration, TX power, bandwidth/channel switch, IQ/AP/LC calibration, RF path switching, RF power, scan I/O control, RF serial helpers, table-loading hooks, and bandwidth callback.

## Control Flow
The header allows `hw.c`, `sw.c`, and `phy.c` to share the CE PHY function surface. `sw.c` wires many functions into HAL ops; common code calls CE table-loading and bandwidth callbacks through that HAL.

## State And Persistence
No storage is declared. Constants influence runtime state in `rtl_phy`, `rtl_efuse`, and hardware registers.

## Dependencies And Integration Points
It depends on rtlwifi/mac80211 types and overlaps with `../rtl8192c/phy_common.h`. It bridges CE-specific implementation and common RTL8192C PHY logic.

## Risks And Edge Cases
Duplication with `phy_common.h` can drift. Both headers expose a misspelled `rtl92c_phy_config_rf_with_feaderfile()` prototype. Consumers must include the correct header when they need CE-specific functions such as `_rtl92ce_phy_lc_calibrate()`.

## Test Signals
Compile coverage across `hw.c`, `phy.c`, `rf.c`, and `sw.c`, plus runtime exercise of HAL PHY callbacks, validates this header.
