# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/ipw2x00/libipw_wx.c

## Purpose
Implements shared Wireless Extensions helpers for libipw scan result reporting and key configuration. It translates the internal network cache into wext scan events and maps legacy/extended encode ioctls onto libipw security state and host crypto contexts.

## Important APIs, Types, and Functions
Exported functions are `libipw_wx_get_scan`, `libipw_wx_set_encode`, `libipw_wx_get_encode`, `libipw_wx_set_encodeext`, and `libipw_wx_get_encodeext`. Internal helpers include `elapsed_jiffies_msecs` and `libipw_translate_scan`. Static `libipw_modes` maps internal A/B/G bitmasks to protocol suffix strings.

## Control Flow
`libipw_wx_get_scan()` locks `ieee->lock`, walks `network_list`, filters entries by `scan_age`, and serializes each visible network into wext events: AP address, ESSID, protocol name, mode, frequency, privacy flag, sorted rates, quality, WPA/RSN IEs, last beacon age, and channel flags such as invalid/DFS. `libipw_wx_set_encode()` handles legacy WEP: selects a key index, disables keys or creates a WEP crypto context, pads 40/104-bit keys, updates the default TX key, sets open vs restricted auth, and calls the driver `set_security` callback. `libipw_wx_set_encodeext()` handles WEP/TKIP/CCMP, group-vs-pairwise rules, module autoload, crypto context replacement, key install with RX sequence, TX-key selection, and security-level updates. Getters return key/security state from `ieee->sec`.

## State and Persistence Behavior
The file mutates `ieee->crypt_info.crypt[]`, `tx_keyidx`, `open_wep`, and staged `libipw_security` values passed to the driver callback. Actual persistent device/firmware programming is delegated through `ieee->set_security`. Scan reporting is read-only except for returning buffer length/flags. Crypto replacement uses delayed deinit so old key contexts persist until active references drain.

## Dependencies and Integration Points
Depends on Wireless Extensions stream helpers, module autoload (`request_module`), libipw crypto registry, `libipw_geo` channel conversion/flags, and driver `set_security` callbacks. ipw2100/ipw2200 wext handlers call these functions for `SIOCGIWSCAN`, `SIOCSIWENCODE`, `SIOCGIWENCODE`, and extended encode operations.

## Risks
Wext scan buffer sizing is approximate: it checks `SCAN_ITEM_SIZE` before each network but individual event expansion can vary. Key state is split between host crypto contexts and `ieee->sec`; drivers must honor `sec.flags` correctly. Extended pairwise keys are restricted mostly to infrastructure index 0 except WEP, which may not fit all modern use cases. `get_encodeext()` advertises TX sequence validity for TKIP/CCMP but does not fill a sequence field itself. Legacy WEP zero-key default behavior is surprising but preserved.

## Test Signals
Scan output with many APs, hidden SSIDs, WPA/RSN IEs, stale entries, DFS/invalid channel flags, small user buffers, WEP set/get/disable/default-key switching, TKIP/CCMP set via encodeext with RX sequence, group-key install, pairwise validation errors, crypto module autoload failure, set_security callback contents, and key replacement during traffic are important signals.
