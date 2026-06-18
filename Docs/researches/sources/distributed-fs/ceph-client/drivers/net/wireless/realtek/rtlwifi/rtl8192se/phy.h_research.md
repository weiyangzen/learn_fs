# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192se/phy.h

## Purpose
This header declares RTL8192SE PHY constants, channel-switch command structures, baseband configuration categories, firmware-version helper, and public PHY/RF control functions.

## Important APIs, Types, And Functions
Constants define maximum TX power index, RF sleep queue wait count, channel-switch command table sizes, and RF path limits. `enum version_8192s` identifies chip cuts. `enum swchnlcmd_id` and `struct swchnlcmd` define table-driven channel-switch commands. `enum baseband_config_type` selects PHY register or AGC table configuration. `hal_get_firmwareversion()` reads the firmware version from `rtlhal->pfirmware`. Prototypes expose BB/RF register access, scan backup/restore, bandwidth and channel switching, RF power state, MAC/BB/RF config, EPHY parameter switching, original register capture, TX power programming, firmware command handling, beacon hardware timing, and RF path configuration.

## Control Flow
The header has no executable flow. `hw.c` and `sw.c` call these APIs during HAL init and runtime operations. `phy.c` implements the staged flows and uses `struct swchnlcmd` for its channel-switch state machine.

## State And Persistence
The header stores no state. It defines the shape of channel-switch command records and exposes functions that mutate `rtlphy`, `rtlhal`, `ppsc`, hardware registers, and firmware command state.

## Dependencies And Integration Points
It depends on `enum radio_path`, `enum rf_pwrstate`, `enum nl80211_channel_type`, `enum fwcmd_iotype`, and `struct ieee80211_hw` from rtlwifi/mac80211 headers. `hal_get_firmwareversion()` assumes `rtlhal->pfirmware` points to `struct rt_firmware`, making it tightly coupled to `fw.h`.

## Risks
`hal_get_firmwareversion()` has no null check, so callers must only use it after firmware buffer allocation/parse. Channel-switch table sizes must be large enough for any future multi-step commands. Firmware/chip version enums must remain aligned with hardware detection in `hw.c`.

## Test Signals
Build/link coverage validates prototypes. Runtime tests should hit every HAL-wired function: BB/RF access, bandwidth/channel changes, RF power transitions, firmware command dispatch, and beacon interval updates.
