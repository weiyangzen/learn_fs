# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8821ae/hw.h

## Purpose

`hw.h` is the public hardware-control interface for the RTL8821AE/RTL8812AE rtlwifi chip module. It exposes the functions implemented in `hw.c` that the chip operation table, PCI glue, mac80211 callbacks, power-management code, and adjacent chip files need to call. The header contains no state of its own; it is a declaration boundary over register programming, initialization, power management, security, rate adaptation, beacon control, WoWLAN, and Bluetooth coexistence helpers.

## Important APIs, Types, and Functions

The declarations use rtlwifi and mac80211 types from included compilation units rather than including those headers directly. Key types include `struct ieee80211_hw`, `struct ieee80211_sta`, `struct rtl_int`, `struct rtl_wow_pattern`, `enum nl80211_iftype`, and standard integer/boolean types.

The header groups the driver surface into hardware variable access, adapter lifecycle, interrupt handling, MAC/media/beacon/QoS, rate and channel access, RF and power-state checks, security, Bluetooth coexistence, receive filtering, and WoWLAN. Notable declarations include `rtl8821ae_get_hw_reg()`, `rtl8821ae_set_hw_reg()`, `rtl8821ae_read_eeprom_info()`, `rtl8821ae_hw_init()`, `rtl8821ae_card_disable()`, `rtl8821ae_interrupt_recognized()`, `rtl8821ae_update_hal_rate_tbl()`, `rtl8821ae_enable_hw_security_config()`, `rtl8821ae_set_key()`, `rtl8821ae_add_wowlan_pattern()`, `_rtl8821ae_stop_tx_beacon()`, and `_rtl8821ae_resume_tx_beacon()`.

## Control Flow

The header does not implement control flow, but its declarations outline the call graph expected by the rest of the chip driver. Probe/setup code calls `rtl8821ae_read_eeprom_info()` before `rtl8821ae_hw_init()` so chip version, RF paths, EFUSE power tables, and board features are known before MAC/BB/RF configuration. Runtime mac80211 state changes call the media, QoS, beacon, rate, and security functions. Interrupt service code calls `rtl8821ae_interrupt_recognized()` after masks have been installed through `rtl8821ae_enable_interrupt()`. Power-management code calls `rtl8821ae_card_disable()` for normal shutdown or WoWLAN preparation, and the empty suspend/resume hooks remain available for the rtlwifi operation table.

## State and Persistence Behavior

No storage is declared in this header. The functions it exposes mutate persistent driver and hardware state in `struct rtl_priv` subobjects and device registers: interrupt masks, receive configuration, beacon control, firmware power-save flags, EFUSE-derived calibration fields, CAM keys, and WoWLAN pattern memory. Because the header is a broad interface, callers must assume many functions have side effects beyond their parameter list. For example, `rtl8821ae_set_key()` uses key material already stored in `rtlpriv->sec`, and `rtl8821ae_update_hal_rate_tbl()` depends on station driver-private metadata.

## Dependencies and Integration Points

`hw.h` is included by the chip implementation and likely by the chip operations registration code. It intentionally relies on prior includes for definitions of mac80211, rtlwifi, and integer types, so include order matters in C files that consume it. It also exposes two underscore-prefixed beacon helpers that are implemented as low-level register routines but remain callable outside `hw.c`; that makes beacon sequencing part of the module ABI.

## Risks and Edge Cases

The header has no compile-time guards beyond the include guard and no documentation for pointer ownership or required locks. Several APIs take untyped `u8 *val` switchboard parameters, so type correctness is implicit in the selected hardware variable. The exported `_rtl8821ae_stop_tx_beacon()` and `_rtl8821ae_resume_tx_beacon()` names look private but are public, which can encourage callers to bypass higher-level media-state routines. Empty `suspend` and `resume` declarations may hide the fact that real suspend behavior is handled by `card_disable()` and WoWLAN helpers.

## Test Signals

Build tests should catch signature drift between this header and `hw.c`. Runtime integration should confirm every function pointer assignment in the RTL8821AE ops table matches these prototypes, especially `get_hw_reg`, `set_hw_reg`, interrupt hooks, security hooks, rate updates, and LED/media paths that call beacon helpers. Static analysis should flag any include-order breakage where `struct ieee80211_hw`, `struct rtl_int`, or `struct rtl_wow_pattern` are not visible before including this header.
