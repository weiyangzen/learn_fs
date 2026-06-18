# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723be/hw.h

## Purpose
Declares the RTL8723BE hardware-operation API implemented by `hw.c` and consumed by the rtlwifi core/device operation table.

## Important APIs, Types, And Functions
The prototypes cover register get/set, EEPROM/EFUSE parsing, interrupt recognition and masking, hardware initialization, card disable, network type/BSSID/QoS/beacon setup, rate-table update, channel-access update, GPIO radio check, hardware security/CAM configuration, key programming, BT coexistence EFUSE/register/hardware init, and suspend/resume stubs.

## Control Flow
No local flow. The header defines the callable surface that higher-level rtlwifi callbacks use during probe, start/stop, config changes, association, key install/remove, interrupt handling, RF-kill polling, and power transitions.

## State And Persistence
No state is held here, but all declared functions mutate persistent driver and hardware state in `hw.c`.

## Dependencies And Integration Points
Depends on mac80211 types (`ieee80211_hw`, `ieee80211_sta`, `nl80211_iftype`) and rtlwifi types (`rtl_int`). It is included by `hw.c` and likely `sw.c` for operation-table binding.

## Risks
Prototype drift breaks operation table assignments or causes mismatched call signatures. Since most functions accept raw `u8 *` values or hardware-level enums, callers must honor the expected payload type for each operation.

## Test Signals
Build warnings are the primary header signal. Runtime coverage comes from successful probe, interrupts, association, key programming, RF-kill, and power-management callbacks reaching the implementations.
