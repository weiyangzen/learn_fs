# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8188ee/hw.h

## Purpose

`hw.h` declares the RTL8188EE hardware-operation surface implemented by `hw.c`. It is the interface used by the rtlwifi core and adjacent RTL8188EE modules to initialize the NIC, manipulate hardware variables, manage interrupts, control beacon/network behavior, program security, read EFUSE data, and handle Bluetooth coexistence.

## Important APIs

The header exposes initialization and teardown (`rtl88ee_hw_init()`, `rtl88ee_card_disable()`), hardware variable dispatch (`rtl88ee_get_hw_reg()`, `rtl88ee_set_hw_reg()`), EEPROM parsing (`rtl88ee_read_eeprom_info()`), interrupt control and recognition, network type/BSSID/QoS/beacon operations, interrupt mask updates, rate table updates, channel access settings, GPIO radio checking, hardware security configuration, CAM key programming, Bluetooth coexistence parsing/register/hardware initialization, suspend/resume stubs, and `rtl88ee_fw_clk_off_timer_callback()`.

## Control Flow And Integration

The header itself is declarative. Function pointers in the device config table normally reference many of these functions, while other RTL8188EE modules call them directly for firmware clock timers and cross-module setup. `rtl88ee_set_hw_reg()` and `rtl88ee_get_hw_reg()` are especially important because they hide many register operations behind generic `HW_VAR_*` selectors used by common rtlwifi code.

## State, Dependencies, Risks, And Test Signals

No state is defined here, but the prototypes operate on shared `struct ieee80211_hw`, `struct rtl_int`, `struct ieee80211_sta`, and kernel/mac80211 types. The primary risk is signature drift from core rtlwifi operation tables or enum semantics. Build coverage should ensure this header remains consistent with `hw.c` and with the ops table that binds the RTL8188EE implementation. Runtime signals are the same as `hw.c`: init, interrupt, network mode, security, rate, RF-kill, and power-management behavior.
