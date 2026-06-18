# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/debug.h

## Purpose
Defines rtlwifi debug levels, component masks, legacy print flags, debug macros, and debugfs lifecycle declarations, with no-op fallbacks when debug is disabled.

## Important APIs, Types, And Functions
Levels include `DBG_WARNING`, `DBG_DMESG`, `DBG_LOUD`, and `DBG_TRACE`. Component masks cover firmware, init, RX/TX, MLME, power, efuse, regulatory, USB, BT coexistence, IQK, and TX reports. Macros are `rtl_dbg()`, `RTPRINT()`, and `RT_PRINT_DATA()`.

## Control Flow
Enabled builds call `_rtl_dbg_print()` or `_rtl_dbg_print_data()` after component/level filtering. Disabled builds compile calls to inline stubs.

## State And Persistence
No state is owned here. Runtime filtering reads module `debug_mask` and `debug_level`.

## Dependencies And Integration Points
Used across shared and chip-specific rtlwifi code as the common debug vocabulary.

## Risks
`COMP_EASY_CONCURRENT` intentionally reuses the USB bit. Both debug and non-debug builds need coverage because macro targets differ.

## Test Signals
Build both configurations, verify component/level filtering, debugfs symbols only in debug builds, and no runtime debug output in disabled builds.
