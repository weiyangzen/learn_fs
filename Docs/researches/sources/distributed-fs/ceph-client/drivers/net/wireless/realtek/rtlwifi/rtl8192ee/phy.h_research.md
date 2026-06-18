# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192ee/phy.h

## Purpose
`phy.h` defines the public PHY/RF interface and local constants needed by RTL8192EE baseband, RF, tx-power, channel switching, antenna diversity, and calibration code.

## Important APIs, Types, And Functions
The header defines tx-count and power constants, IQK/APK array sizes, tolerance/delay limits, EFUSE content offsets, RF path limits, `enum swchnlcmd_id`, `struct swchnlcmd`, `enum baseband_config_type`, `enum ant_div_type`, and all public `rtl92ee_phy_*` functions. The exported functions cover BB/RF register access, MAC/BB/RF config, tx-power programming, scan backup, bandwidth/channel switching, IQ/LC calibration, RF path switching, RF table config, IO commands, and RF power state transitions.

## Control Flow
The header itself has no flow, but it constrains the control structures used by `phy.c`: channel changes are expressed as `struct swchnlcmd` sequences, baseband config selects PHY register or AGC tables, and antenna diversity values guide RF path switching.

## State And Persistence Behavior
No state is allocated here. Constants such as `MAX_TX_COUNT`, EFUSE offsets, IQK dimensions, and RF path limits define the shape of persistent arrays in `struct rtl_phy` and `struct rtl_efuse`.

## Dependencies And Integration Points
It depends on shared rtlwifi/mac80211 types and radio/power enums defined elsewhere. It is consumed by `hw.c`, `rf.c`, and `phy.c`, making it the main local contract for PHY services.

## Risks
The comment on `MAX_TX_COUNT` warns that changing it breaks EFUSE parsing sequence. Function prototypes expose many timing-sensitive operations; callers must respect in-progress flags and RF power state. `RT_CANNOT_IO(hw)` is hardcoded to `false`, so any future sleep/unload protection would need real implementation elsewhere.

## Test Signals
Compile coverage validates prototypes and enum visibility. Runtime coverage should exercise all declared public operations through init, scan, channel switch, bandwidth switch, calibration, and RF power transitions.
