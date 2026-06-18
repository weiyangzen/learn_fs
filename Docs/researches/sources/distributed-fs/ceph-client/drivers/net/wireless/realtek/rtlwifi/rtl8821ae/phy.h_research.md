# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8821ae/phy.h

## Purpose

`phy.h` declares the RTL8821AE/RTL8812AE PHY programming interface and local data structures used by `phy.c`, RF code, dynamic-management code, and hardware ops. It defines efuse offsets, TX power layout structures, calibration constants, RF/path limits, channel-switch command structures, antenna-selection bitfields, and exported PHY function prototypes.

## Important APIs, Types, and Constants

- `MAX_TX_COUNT`, `TX_1S` through `TX_4S`, `MAX_POWER_INDEX`, `RTL8821AE_MAX_PATH_NUM`, and `RF6052_MAX_PATH` define TX power and RF path dimensions.
- `CT_OFFSET_*` constants describe compact efuse offsets for MAC address, power indexes and diffs, channel plan, thermal meter, RF options, version, and customer ID.
- `struct swchnlcmd` and `enum swchnlcmd_id` preserve an older channel-switch command-script model.
- `enum baseband_config_type` defines `BASEBAND_CONFIG_PHY_REG` and `BASEBAND_CONFIG_AGC_TAB`, both used by `phy.c`.
- `enum antenna_path`, `struct r_antenna_select_ofdm`, and `struct r_antenna_select_cck` define antenna register encodings.
- `struct efuse_contents` models parsed efuse payload: MAC address, power indexes, power diffs, max offsets, channel plan, thermal meter, RF options, version, OEM ID, and regulatory byte.
- `struct tx_power_struct` stores per-path/channel CCK/HT power tables, group power arrays, legacy/HT diffs, group count, and original MCS offsets.
- `enum _ANT_DIV_TYPE` names antenna-diversity modes.

Exported prototypes cover BB/RF register access, MAC/BB/RF configuration, band/channel/bandwidth changes, TX power programming, scan operation backup, IQK/LC calibration, RF path switching, RF table loading, scan I/O commands, RF power-state changes, and TX swing lookup.

## Control Flow

The header itself has no runtime flow. Its declarations shape hardware initialization, channel switching, scan handling, calibration, TX power tracking, and power-management call paths in `phy.c`, `rf.c`, `dm.c`, and hardware ops files.

## State and Persistence Behavior

`phy.h` defines in-memory structure layouts and constants. It does not persist state, but its efuse offsets and array dimensions determine how persistent device calibration and identity data are interpreted. `RT_CANNOT_IO(hw)` is defined as `false`, making I/O guard checks in the implementation effectively inactive unless this macro changes.

## Dependencies and Integration Points

The declarations assume common `rtlwifi` and kernel types such as `struct ieee80211_hw`, `enum radio_path`, `enum nl80211_channel_type`, `enum rf_pwrstate`, `enum io_type`, `ETH_ALEN`, and `CHANNEL_MAX_NUMBER`. Implementations are mostly in `phy.c`; callers include RF, DM, hardware ops, and power-management code in the same chip directory.

## Risks and Edge Cases

- `IQK_ADDA_REG_NUM` is defined twice with the same value.
- `RT_CANNOT_IO(hw)` being hardcoded to `false` weakens sleep/unload I/O guards.
- `MAX_TX_COUNT` must remain `4` or efuse table sequencing breaks.
- `struct efuse_contents` and `struct tx_power_struct` are tightly coupled to parser and channel dimensions.
- RTL8812AE IQK is declared even though the implementation is currently empty.
- Some names preserve vendor typos; cleanup must update every reference.

## Test Signals

Compile all RTL8821AE translation units after prototype or structure changes. On hardware, confirm efuse parsing, MAC address, channel plan, thermal meter, TX power arrays, RF path switching, channel changes, RF power state changes, and IQK callers still work.
