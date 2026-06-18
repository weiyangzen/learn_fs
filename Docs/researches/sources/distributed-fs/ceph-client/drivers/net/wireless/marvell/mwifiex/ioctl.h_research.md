# sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/mwifiex/ioctl.h

## Purpose
`ioctl.h` defines user/configuration-facing mwifiex data structures used by command preparation, cfg80211 glue, debug reporting, power management, AP configuration, register/memory access, custom IE handling, coalescing, MEF, and TDLS operations. Despite the name, these structures are shared internal request/result contracts rather than a standalone ioctl implementation.

## Important APIs, Types, and Functions
The header defines scan types and `struct mwifiex_user_scan`, multicast modes and `struct mwifiex_multicast_list`, band constants, WPA/WEP/AP configuration types (`struct mwifiex_uap_bss_param`, `struct wpa_param`, `struct wep_key`), debug output (`struct mwifiex_debug_info`), reorder/BA table snapshots, encryption keys (`struct mwifiex_ds_encrypt_key`), power and host-sleep config (`struct mwifiex_ds_pm_cfg`, `mwifiex_ds_hs_cfg`, `mwifiex_ds_auto_ds`), 11n/11ac/antenna config, register/eeprom/memory access, generic IE buffers, RSSI subscription, MEF and packet coalescing rules, and TDLS operation parameters.

## Control Flow
Other mwifiex modules populate these structures from cfg80211/netdev/debugfs requests and pass them into `mwifiex_send_cmd()` or status functions. For example multicast updates in `main.c` fill `mwifiex_multicast_list`; AP start code fills `mwifiex_uap_bss_param`; debugfs gathers `mwifiex_debug_info`; key paths consume `mwifiex_ds_encrypt_key`; power paths use `mwifiex_ds_pm_cfg`; custom IE code respects `IEEE_MAX_IE_SIZE` and `MWIFIEX_IE_HDR_SIZE`.

## State and Persistence
The header itself stores no state. Its structs mirror transient request payloads or cached runtime fields inside `mwifiex_private` and `mwifiex_adapter`. Some values, such as WEP keys, WPA passphrases, MEF entries, GTK replay counters, and host-sleep conditions, may be sent to firmware and persist there until reconfigured or firmware resets.

## Dependencies and Integration Points
`ioctl.h` depends on cfg80211 types, Linux WLAN key size constants, mwifiex firmware structures, and `MAX_NUM_TID`/BA constants shared with `main.h`. It is included before or alongside `fw.h`/`main.h` in command, cfg80211, debugfs, power, AP, TDLS, and scan code.

## Risks and Edge Cases
Many structures contain fixed maximum arrays: multicast list 32 addresses, generic IE 256 bytes, EEPROM 256 bytes, MEF 10 filters, coalesce 8 rules, and reorder windows 64 slots. Callers must validate counts before copying. Several fields carry sensitive material, so dumps and error paths should avoid exposing keys/passphrases. Pointer members such as MEF entries and TDLS extension/rate/capability buffers require lifetime discipline by callers.

## Test Signals
Exercise multicast modes, AP security combinations, scan config boundaries, debug info generation, power/host-sleep toggles, memory/register/eeprom access bounds, custom IE size limits, MEF/coalesce rule maxima, TDLS parameter construction, and key installation/removal including WAPI/IGTK/current WEP flags.
