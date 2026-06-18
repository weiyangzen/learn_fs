# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723be/phy.h

## Purpose
Declares RTL8723BE PHY constants, EFUSE offsets, calibration dimensions, antenna diversity modes, baseband config types, and the public PHY/RF API.

## Important APIs, Types, And Functions
Constants cover TX path counts, max power index, channel-switch command array sizes, IQK/LC/APK dimensions, EFUSE offsets for MAC/TX power/channel plan/thermal/RF option/customer id, RF path count, and RF register masks. Enums define baseband config type and antenna-diversity type. Function prototypes expose RF register access, MAC/BB/RF config, default register capture, TX-power setting, scan backup/restore, bandwidth and channel switching, IQK/LC calibration, RF path switching, RF table config, IO command handling, and RF power-state changes.

## Control Flow
No executable flow. The header defines what `hw.c`, `dm.c`, and rtlwifi operation tables can call in `phy.c`.

## State And Persistence
No mutable state is stored. Constants define array sizes and EFUSE offsets that shape persistent `rtl_phy` and `rtl_efuse` data.

## Dependencies And Integration Points
Depends on mac80211 channel types, rtlwifi radio path/power enums, and hardware register definitions. It bridges `hw.c` initialization, `dm.c` calibration/power tracking, `rf.c` RF6052 helpers, and generated table programming.

## Risks
Array-size constants such as `MAX_TX_COUNT`, IQK register counts, and command counts must match implementation loops and EFUSE layout. The comment warns `MAX_TX_COUNT` must remain 4 or EFUSE table reads break.

## Test Signals
Build coverage for prototypes and runtime validation of EFUSE TX-power parsing, channel switch, bandwidth switch, IQK/LC, scan backup/restore, and RF power state transitions.
