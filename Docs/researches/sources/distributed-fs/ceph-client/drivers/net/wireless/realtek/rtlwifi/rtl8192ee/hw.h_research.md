# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192ee/hw.h

## Purpose
`hw.h` is the public chip-hardware interface for the RTL8192EE implementation. It exposes the routines implemented in `hw.c` to the rtlwifi core and adjacent chip modules without carrying implementation state.

## Important APIs, Types, And Functions
The header declares hardware register access dispatch (`rtl92ee_get_hw_reg`, `rtl92ee_set_hw_reg`), EEPROM/EFUSE parsing, interrupt recognition and mask control, full hardware init and card disable, network type/BSSID/QoS/beacon configuration, rate-table updates, GPIO radio checking, security enablement and key programming, BT coexistence EFUSE and hardware init, suspend/resume hooks, receive-all-destination control, and the firmware clock-off timer callback. It uses shared rtlwifi/mac80211 types such as `struct ieee80211_hw`, `struct ieee80211_sta`, `struct rtl_int`, `enum nl80211_iftype`, and `enum led_ctl_mode` indirectly.

## Control Flow
This header does not implement flow, but it defines the callable surface used by the driver ops table and by sibling modules. The main lifecycle is `read_eeprom_info` before hardware bring-up, `hw_init`, runtime setters and interrupt helpers during operation, and `card_disable` during shutdown or IPS.

## State And Persistence Behavior
No state is stored here. All persistent and runtime state lives in rtlwifi structures reached from `struct ieee80211_hw`.

## Dependencies And Integration Points
It depends on the includer already having definitions for mac80211 and rtlwifi structures/enums. Integration is broad: PCI probe/remove, mac80211 callbacks, firmware power-save work, security key paths, and BT coexistence all consume these declarations.

## Risks
Because this is a declaration boundary, mismatches with `hw.c` signatures or missing prototypes would show up as build failures. The broad API also makes `hw.c` a high-blast-radius module; changes to these declarations affect driver ops registration and adjacent code.

## Test Signals
Compile coverage is the primary signal. Link-time success confirms all declared functions are implemented, and runtime smoke tests for initialization, interrupt handling, link setup, and shutdown validate the exported surface.
