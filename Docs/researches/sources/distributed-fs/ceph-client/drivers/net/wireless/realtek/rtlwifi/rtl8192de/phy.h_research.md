# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192de/phy.h

## Purpose
Declares the RTL8192DE PHY interface and constants used by the PCIe PHY implementation. It exposes the BB/RF configuration, channel, bandwidth, RF power, power-on/off, IQK, LCK, and BB/RF update functions consumed by `sw.c`, `rf.c`, `hw.c`, and common rtl8192d code.

## Important APIs, Types, And Functions
The header defines channel-switch command capacities (`MAX_PRECMD_CNT`, `MAX_RFDEPENDCMD_CNT`, `MAX_POSTCMD_CNT`), RF sleep wait limits, IQK register counts, EEPROM/efuse offset constants, and `enum swchnlcmd_id` plus `struct swchnlcmd`. Exported prototypes cover BB register access, MAC/BB/RF configuration, RF table loading, bandwidth setting, software channel switch, RF power-state setting, power-on/check-poweroff, LCK, BBRF update, IQK, and IQK reload.

## Control Flow
The header does not execute control flow directly, but it defines the command IDs used by `phy.c` to build pre/RF/post channel-switch command arrays. `rtl92d_phy_sw_chnl()` consumes `struct swchnlcmd` entries to run TX power updates, port writes, and RF writes in ordered stages.

## State And Persistence
No state is allocated in this header. The constants shape persistent arrays and bounded loops in `phy.c`, especially channel-switch command arrays and IQK backup matrix dimensions. The EEPROM offset macros document efuse layout positions used by companion parsing/configuration code.

## Dependencies And Integration Points
Requires declarations for `struct ieee80211_hw`, `enum nl80211_channel_type`, `enum radio_path`, `enum rf_content`, and `enum rf_pwrstate` from rtlwifi/mac80211 headers included by users. It is included by 8192DE `phy.c`, `rf.c`, `sw.c`, and likely hardware initialization code to expose PHY operations.

## Risks
There is a prototype typo, `rtl92c_phy_config_rf_with_feaderfile`, that does not match the implemented `rtl92d_phy_config_rf_with_headerfile()` and appears unused here. Command array limits are fixed; adding new channel-switch commands without respecting these sizes would fail command insertion. Header constants encode chip-specific magic numbers, so sharing them across variants would be risky.

## Test Signals
Build coverage is the main signal: all translation units including this header should compile without missing enum or prototype conflicts. Runtime channel-switch tests indirectly validate the `swchnlcmd` structure and limits.
