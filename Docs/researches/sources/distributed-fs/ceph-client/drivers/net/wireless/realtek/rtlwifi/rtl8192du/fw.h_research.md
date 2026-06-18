# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192du/fw.h

## Purpose
Declares the RTL8192DU firmware download entry point.

## Important APIs, Types, And Functions
Exports `rtl92du_download_fw(struct ieee80211_hw *hw)`, returning 0 on success or an error-style nonzero value from the firmware helpers.

## Control Flow
No executable flow. `hw.c` calls this during hardware initialization after MAC/LLT setup and before PHY/RF configuration.

## State And Persistence
No state is owned here. The implementation updates firmware version fields and device MCU state.

## Dependencies And Integration Points
Requires `struct ieee80211_hw` from including headers. Used by DU hardware init and the firmware implementation.

## Risks
Low direct risk. Prototype drift would break the hardware initialization path.

## Test Signals
Build success plus successful firmware download in `rtl92du_hw_init()` validate the declaration.
