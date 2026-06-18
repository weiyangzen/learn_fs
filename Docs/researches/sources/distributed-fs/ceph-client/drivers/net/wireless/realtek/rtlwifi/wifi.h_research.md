# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/wifi.h

## Purpose
`wifi.h` is the central shared contract for the legacy `rtlwifi` Realtek mac80211 driver family. It is not an implementation file; it defines hardware constants, firmware command/event formats, register masks, rate identifiers, state enums, shared driver data structures, operation tables, and small inline wrappers used by PCI/USB bus code and chip-specific HALs. Most `rtlwifi` modules include this header to agree on the shape of `struct rtl_priv` and its subobjects.

## Important APIs, types, and state
The top of the file defines common register masks, RF power-change reasons, queue indexes, CAM/key sizes, channel group sizes, firmware H2C/C2H IDs, TX report extractors, WoWLAN pattern limits, and hardware type predicates such as `IS_HARDWARE_TYPE_8822B()`. These constants are consumed throughout descriptor handling, firmware mailbox handling, RF/BB programming, and power management.

The major state containers are `struct rtl_priv` and the structures embedded in it: `rtl_mac` for mac80211-visible link, queue, HT/VHT, BSSID, EDCA, and scanning state; `rtl_hal` for chip identity, firmware buffers, H2C state, interface type, dual-MAC state, and WoWLAN firmware; `rtl_phy` for RF path, channel, bandwidth, IQK, power indexes, per-rate power tables, and calibration backup registers; `rtl_dm` for dynamic mechanism state such as DIG, thermal tracking, CFO, tx power tracking, and antenna training; `rtl_security` for key buffers and CAM bitmap; `rtl_efuse` for EEPROM/efuse-derived board and power data; `rtl_ps_ctl` for IPS/LPS/RF power state and wake reasons; `rtl_stats` and `wireless_stats` for per-packet and aggregate signal/counter data; `rtl_btc_info`, `bt_coexist_info`, and `rtl_btc_ops` for Bluetooth coexistence; and `rtl_hal_ops` plus `rtl_intf_ops` for chip and bus callbacks.

The inline API layer includes `rtl_read_byte/word/dword()`, `rtl_write_byte/word/dword()`, `rtl_write_chunk()`, `rtl_get_bbreg()`, `rtl_set_bbreg()`, `rtl_get_rfreg()`, `rtl_set_rfreg()`, HAL state helpers, SKB header/TID helpers, station lookup helpers, and `calculate_bit_shift()`. These wrappers route all MMIO/USB/PCI register access through `rtlpriv->io` and chip operations through `rtlpriv->cfg->ops`.

## Control flow and integration
Control flow is indirect by design. mac80211 callbacks and bus drivers operate on `struct ieee80211_hw`, recover `struct rtl_priv` with `rtl_priv(hw)`, then use `rtl_hal_ops` for chip-specific hardware work and `rtl_intf_ops` for bus-specific transport. Descriptor fill/query, RF calibration, channel switching, firmware command filling, security CAM programming, rate updates, and debug/BT coexistence are all reached through these callback tables.

## State and persistence behavior
This header describes mostly runtime state. Persistent hardware configuration enters through efuse/EEPROM fields in `rtl_efuse`, firmware images in `rtl_hal`, and WoWLAN pattern state in `rtl_wow_pattern` and `rtl_ps_ctl`. Security state persists only for the live device instance in CAM bitmap/key buffers. Power-save and BT coexistence fields are state machines carried across callbacks, timers, and workqueue activity.

## Dependencies and risks
The file depends on Linux kernel networking, mac80211, firmware loading, USB, completions, and local `debug.h`. Its risk profile is high because structure layout and enum values are shared ABI inside the driver family. A change can silently break descriptor programming, firmware commands, power save, or chip-specific callbacks. The duplicated mask definitions near the top are harmless but indicate historical accumulation. Bitfield structures and packed station data require attention to endian/layout assumptions.

## Test signals
Useful test signals include successful compile across representative `rtlwifi` PCI and USB chip configs, firmware load and C2H/H2C handling, association on 2.4 GHz and 5 GHz, WoWLAN suspend/resume, encryption key install/remove, rate control updates, BT coexistence debug output, and lockdep or KASAN coverage around workqueues, SKB control block use, and register wrappers.
