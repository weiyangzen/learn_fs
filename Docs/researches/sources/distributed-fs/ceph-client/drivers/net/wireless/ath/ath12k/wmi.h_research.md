# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/wmi.h

## Purpose

`wmi.h` is the central ath12k host/firmware WMI ABI declaration file. It defines TLV framing, command groups, command IDs, event IDs, service bits, TLV tags, packed command/event payloads, host-side argument structures, and exported WMI helper prototypes. For this subset, its key role is the firmware contract consumed by `wow.c`: Wake-on-WLAN events/reasons, bitmap wake patterns, PNO/NLO, ARP/NS offload, GTK rekey offload, hardware data filtering, and station keepalive.

## Important APIs, Types, And Constants

- Generic ABI: `struct wmi_cmd_hdr`, `struct wmi_tlv`, `WMI_TLV_LEN`, `WMI_TLV_TAG`, `TLV_HDR_SIZE`, `WMI_TLV_CMD()`, and `WMI_TLV_EV()`.
- WoW command/event groups: `WMI_GRP_WOW`, `WMI_GRP_ARP_NS_OFL`, `WMI_GRP_NLO_OFL`, `WMI_GRP_GTK_OFL`, and `WMI_GRP_HW_DATA_FILTER`.
- WoW commands: `WMI_WOW_ADD_WAKE_PATTERN_CMDID`, `WMI_WOW_DEL_WAKE_PATTERN_CMDID`, `WMI_WOW_ENABLE_DISABLE_WAKE_EVENT_CMDID`, `WMI_WOW_ENABLE_CMDID`, `WMI_WOW_HOSTWAKEUP_FROM_SLEEP_CMDID`, `WMI_SET_ARP_NS_OFFLOAD_CMDID`, `WMI_NETWORK_LIST_OFFLOAD_CONFIG_CMDID`, `WMI_GTK_OFFLOAD_CMDID`, `WMI_STA_KEEPALIVE_CMDID`, and `WMI_HW_DATA_FILTER_CMDID`.
- Events/services: `WMI_WOW_WAKEUP_HOST_EVENTID`, `WMI_NLO_MATCH_EVENTID`, `WMI_GTK_OFFLOAD_STATUS_EVENTID`, `WMI_GTK_REKEY_FAIL_EVENTID`, and service bits such as `WMI_TLV_SERVICE_WOW`, `WMI_TLV_SERVICE_NLO`, `WMI_TLV_SERVICE_ARPNS_OFFLOAD`, and `WMI_TLV_SERVICE_GTK_OFFLOAD`.
- WoW event/reason enums: `enum wmi_wow_wakeup_event`, `enum wmi_wow_wake_reason`, plus `wow_wakeup_event()` and `wow_reason()` logging helpers.
- Pattern ABI: `WOW_MIN_PATTERN_SIZE`, `WOW_MAX_PATTERN_SIZE`, `WOW_MAX_PKT_OFFSET`, `WOW_HDR_LEN`, `WOW_MAX_REDUCE`, `struct wmi_wow_bitmap_pattern_params`, `struct wmi_wow_add_pattern_cmd`, and `struct wmi_wow_del_pattern_cmd`.
- Offload ABI: `struct wmi_pno_scan_req_arg`, `struct wmi_wow_nlo_config_cmd`, `struct wmi_hw_data_filter_arg`, `struct wmi_arp_ns_offload_arg`, `struct wmi_gtk_rekey_offload_cmd`, `struct wmi_gtk_offload_status_event`, and `struct wmi_sta_keepalive_arg`.
- Exported helpers used by `wow.c`: `ath12k_wmi_wow_enable()`, `ath12k_wmi_wow_host_wakeup_ind()`, `ath12k_wmi_wow_add_pattern()`, `ath12k_wmi_wow_del_pattern()`, `ath12k_wmi_wow_add_wakeup_event()`, `ath12k_wmi_wow_config_pno()`, `ath12k_wmi_hw_data_filter_cmd()`, `ath12k_wmi_arp_ns_offload()`, `ath12k_wmi_gtk_rekey_offload()`, `ath12k_wmi_gtk_rekey_getinfo()`, and `ath12k_wmi_sta_keepalive()`.

## Control Flow

The header itself does not execute. `wow.c` fills host-side argument structures, `wmi.c` converts them into packed little-endian TLV records, firmware executes them, and firmware events are parsed back into host state. During WoW suspend, wake events become `struct wmi_wow_add_del_event_cmd` bitmaps, patterns become `struct wmi_wow_bitmap_pattern_params`, PNO becomes `struct wmi_wow_nlo_config_cmd` plus SSID/channel TLV arrays, ARP/NS becomes offload tuple arrays, GTK rekey becomes key/replay-counter commands, and keepalive becomes `struct wmi_sta_keepalive_cmd`.

For wakeup, firmware emits `WMI_WOW_WAKEUP_HOST_EVENTID` with `WMI_TAG_WOW_EVENT_INFO`; `wmi.c` parses `struct wmi_wow_ev_param`, logs `wow_reason()`, optionally handles page-fault payloads, and completes `ab->wow.wakeup_completed`.

## State And Persistence Behavior

No state is stored in the header. It defines state shape and limits. Persistent runtime state lives in `ar->wow`, `ab->wow`, per-vif rekey/offload state, firmware service bitmaps, and firmware-resident offload records. The `_arg` structures are host-side transient data; packed WMI structures are the serialized firmware ABI.

## Dependencies And Integration Points

The file depends on mac80211/cfg80211 types, `htc.h`, and `cmn_defs.h`. It is integrated by `wmi.c` for serialization/event parsing, `wow.c` for suspend/resume offload policy, `mac.c` for feature setup, and firmware service negotiation for feature advertisement.

## Risks

ABI drift is the main risk: enum values, TLV tags, packed layout, endian fields, and array limits must match firmware. Bitmap shifts depend on enum values. Pattern constants are shared with Ethernet-to-native-WiFi conversion logic. PNO, ARP/NS, and GTK structures cross address/key lifetimes and must be bounded and logged carefully.

## Test Signals

Build with ath12k PM/WoW support, run suspend/resume with magic packet, disconnect, packet-pattern, NLO, ARP/NS, and GTK rekey scenarios, and inspect WMI logs for the expected command IDs, TLV lengths, wake reasons, and cleanup commands. Static analysis should focus on packed sizes, endian conversion, TLV length construction, and enum-to-bit shifts.
