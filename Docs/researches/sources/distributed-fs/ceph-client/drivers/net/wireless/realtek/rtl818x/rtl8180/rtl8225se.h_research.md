# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtl818x/rtl8180/rtl8225se.h

## Purpose
This header declares the RTL8225-SE radio interface used by the RTL8187SE path and defines analog power constants and PHY write helpers for CCK/OFDM baseband programming.

## Important APIs, Types, And Functions
The public declarations are `rtl8187se_detect_rf()`, `rtl8225se_rf_stop()`, `rtl8225se_rf_set_channel()`, `rtl8225se_rf_conf_erp()`, and `rtl8225se_rf_init()`. The file also defines `enum rtl8187se_power_state`, although the enum is not used by `rtl8225se.c` itself.

`rtl8225se_write_phy_ofdm()` and `rtl8225se_write_phy_cck()` are inline wrappers around `rtl8180_write_phy()`. The CCK helper ORs in `0x10000`, which is the local convention for selecting the CCK PHY address space.

## Control Flow
The header has no runtime control flow. It shapes how the C file writes baseband registers and exposes the RF ops provider to the parent driver.

## State And Persistence
The analog constants (`RTL8225SE_ANAPARAM_*`, `RTL8225SE_ANAPARAM2_*`, `RTL8225SE_ANAPARAM3`) are persisted only when the C file writes them into hardware through `rtl8180_set_anaparam*()`. There is no software state in the header.

## Dependencies And Integration Points
It depends on `struct ieee80211_hw`, `struct ieee80211_conf`, `struct ieee80211_bss_conf`, and `struct rtl818x_rf_ops` being visible through included driver headers. It is consumed by `rtl8225se.c` and by any RTL8180-side code that calls the declared RF functions.

## Risks
The declaration `rtl8225se_rf_conf_erp()` has no implementation in the paired source file, so callers must not require it unless implemented elsewhere. The analog constants encode board-power policy; incorrect reuse on a different chip revision could power down the wrong blocks.

## Test Signals
Compilation with `CONFIG_RTL8180`/RTL8187SE support is the main header signal. Runtime validation comes indirectly through successful RF init/stop/channel operations and correct CCK/OFDM writes.
