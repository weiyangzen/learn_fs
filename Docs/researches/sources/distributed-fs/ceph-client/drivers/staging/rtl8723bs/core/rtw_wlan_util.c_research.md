# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/core/rtw_wlan_util.c

## Purpose
`rtw_wlan_util.c` is a shared 802.11 utility layer for rtl8723bs. It translates wireless modes to rate-adaptation IDs, manages supported/basic rates, controls channel and bandwidth hardware settings, owns CAM key-cache allocation helpers, handles WMM/HT/ERP association and beacon updates, validates beacon consistency, detects AP vendor IOT quirks, updates station rate/HT capabilities, processes ADDBA receive setup, handles TSF tracking, and allocates firmware MAC IDs.

## Important APIs, Types, And Functions
Rate and mode helpers include `networktype_to_raid_ex()`, `ratetbl_val_2wifirate()`, `ratetbl2rateset()`, `get_rate_set()`, `set_mcs_rate_by_mask()`, `update_basic_rate_table()`, and `update_basic_rate_table_soft_ap()`. Hardware control helpers include `r8723bs_select_channel()` and `set_channel_bwmode()`. CAM APIs include `invalidate_cam_all()`, `_write_cam()`, `write_cam()`, `clear_cam_entry()`, `rtw_camid_search()`, `rtw_camid_alloc()`, `rtw_camid_free()`, and `flush_all_cam_entry()`. Association/beacon handlers include `WMMOnAssocRsp()`, `HT_caps_handler()`, `HT_info_handler()`, `HTOnAssocRsp()`, `ERP_IE_handler()`, `VCS_update()`, `rtw_check_bcn_info()`, and `update_beacon_info()`.

## Control Flow
Rate setup flows from network mode and AP IEs into rate tables, MCS masks, station `raid`, and HAL RA mask updates. Channel changes are serialized by `setch_mutex`; the code updates `dvobj_priv` operating channel/bandwidth/offset state before calling HAL setters. CAM programming writes six 32-bit words per entry to hardware and maintains a software cache protected by `cam_ctl->lock`; allocation reserves default-key CAM IDs for AP/ad-hoc group keys and otherwise searches/reuses matching entries or picks free entries starting at 4.

Association response handling parses WMM parameters into EDCA registers, updates ACM masks, and stores WMM queue ordering. HT capability and operation handlers merge AP capabilities with local defaults, set AMPDU factor/spacing, update bandwidth and secondary-channel offset, and notify rate adaptation. Beacon validation constructs a temporary BSS descriptor from received IEs, compares BSSID, channel, SSID, privacy, WPA/WPA2 protocol, pairwise/group cipher, and 802.1X mode, and only returns failure after three mismatches within a one-second window.

## State, Dependencies, And Integration
The file mutates `mlmeextpriv` operating channel, bandwidth, TSF, wireless mode, beacon delay histograms, and current network information. `dvobj_priv` persists shared channel and CAM state across interfaces. It bridges MLME parsing, station management, security key programming, transmit QoS/protection, receive reorder setup, HAL register access, and firmware/H2C behavior. `rtw_xmit.c` consumes WMM order, VCS settings, station rates, SGI, LDPC/STBC, and MAC IDs established here.

## Risks And Test Signals
IE walking often advances by `pIE->length + 2` and assumes caller-provided bounds are trustworthy. CAM allocation/write ordering matters during rekey, and CAM exhaustion requires caller handling. Beacon validation debounce can delay detection of real AP changes. Tests should cover channel/bandwidth transitions, CAM pairwise/group allocation with duplicate key IDs, CAM exhaustion, WMM/ACM remapping, HT negotiation, beacon mismatch debounce, malformed IE fuzzing, AP vendor detection, ADDBA setup, TSF parsing, and MAC ID allocate/release.
