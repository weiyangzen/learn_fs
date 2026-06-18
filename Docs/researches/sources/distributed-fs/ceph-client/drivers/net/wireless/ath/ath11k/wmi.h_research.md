# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/wmi.h

## Purpose
`ath11k/wmi.h` is the main host/firmware protocol contract for the ath11k driver. It defines WMI TLV command IDs, event IDs, service bits, command payloads, event payloads, argument structures, and exported WMI helper prototypes used by the rest of ath11k. It is not an implementation file, but it controls the ABI between the Linux driver and Qualcomm 802.11ax firmware for bring-up, scan, vdev/peer lifecycle, regulatory data, management frames, statistics, power save, WoW, NLO/PNO, ARP/NS offload, GTK rekey, TWT, spectral scan, SAR/GEO, and CFR capture.

## Important APIs, Types, And Functions
- `struct wmi_cmd_hdr`, `struct wmi_tlv`, `WMI_TLV_LEN`, `WMI_TLV_TAG`, and `WMI_CMD_HDR_CMD_ID` define the packed TLV framing used by all command/event payloads.
- `enum wmi_cmd_group`, `enum wmi_tlv_cmd_id`, `enum wmi_tlv_event_id`, `enum wmi_tlv_pdev_param`, `enum wmi_tlv_vdev_param`, `enum wmi_tlv_tag`, and `enum wmi_tlv_service` encode firmware-visible IDs and capability bits.
- Capability and resource structures include `struct wmi_service_ready_event`, `struct wmi_service_ready_ext_event`, `struct wmi_mac_phy_capabilities`, `struct wmi_resource_config`, `struct ath11k_wmi_base`, and `struct ath11k_targ_cap`.
- Lifecycle argument/command structs cover init, pdev, vdev, peer, scan, channel list, management transmit, beacon template, key install, BA negotiation, AP/STA power-save, WMM, regulatory, stats, thermal, pktlog, TWT, OBSS spatial reuse, spectral, and DMA ring configuration.
- WoW and suspend-related definitions include `enum wmi_wow_wakeup_event`, `enum wmi_wow_wake_reason`, `struct wmi_wow_add_del_event_cmd`, `struct wmi_wow_add_pattern_cmd`, `struct wmi_wow_bitmap_pattern`, `struct wmi_pno_scan_req`, `struct wmi_wow_nlo_config_cmd`, ARP/NS offload tuples, GTK offload payloads, and STA keepalive payloads.
- Exported prototypes such as `ath11k_wmi_cmd_send()`, `ath11k_wmi_attach()`, `ath11k_wmi_wait_for_service_ready()`, `ath11k_wmi_vdev_start()`, `ath11k_wmi_send_scan_start_cmd()`, `ath11k_wmi_wow_enable()`, `ath11k_wmi_wow_add_pattern()`, `ath11k_wmi_arp_ns_offload()`, and `ath11k_wmi_sta_keepalive()` are implemented primarily in `wmi.c` and consumed by MAC, regulatory, debug, spectral, and WoW code.

## Control Flow And State Behavior
The header establishes a staged control model. Driver attach allocates WMI state in `ath11k_wmi_base`, connects HTC endpoints, waits for `service_ready` and `unified_ready`, parses firmware resource/capability events, and caches service bits in `svc_map`. Runtime callers then build typed argument structures and pass them to WMI helpers, which allocate SKBs with `WMI_SKB_HEADROOM`, fill packed TLVs, send through HTC, and wait for firmware events or completions where needed.

State is mostly firmware-backed but mirrored in host memory: service capability bitmaps, target memory chunks, resource configuration, target capabilities, per-pdev WMI endpoints, max message length, and preferred hardware mode. Event structures describe asynchronous updates that mutate higher-level driver state, including vdev start/stop responses, peer deletion, scan progress, regulatory rules, management TX completions, stats, radar, temperature, WoW wake reason, and GTK offload status.

## Dependencies And Integration Points
The file depends on mac80211 data types, HTC endpoint IDs, Linux bitfield helpers, packed firmware ABI layout, and ath11k core types. It is included widely by `wmi.c`, `mac.c`, `wow.c`, `reg.c`, `debugfs`, `thermal`, `spectral`, and power-management code. It forms the integration boundary to firmware; mismatches in enum values, TLV tags, lengths, or packed structure fields are protocol breaks rather than ordinary compile failures.

## Risks And Edge Cases
- Structure layout is firmware ABI. Reordering fields or changing packing can silently corrupt WMI commands.
- Large enums are sparse and grouped by firmware command group; inserting values in the wrong place can collide with existing firmware IDs.
- Capability gates must be honored by callers, especially WoW/NLO/TWT/spectral/6 GHz regulatory extensions, because older firmware may not implement every command.
- Several length constants define firmware maximums for scan IEs, PNO networks/channels, WoW patterns, SAR tables, and GTK keys. Callers must validate before copy.
- Inline string helpers for WoW events/reasons return `NULL` for unknown values, so logging code must tolerate unknown firmware reasons.

## Test Signals
Useful validation includes full ath11k build, sparse/packed layout checks, service-ready parsing on supported hardware, scan/vdev/peer lifecycle smoke tests, regulatory event parsing including 6 GHz extensions, WoW suspend/resume with magic packet and NLO, ARP/NS and GTK offload, TWT setup/teardown, spectral enable/configure, SAR/GEO commands, firmware stats parsing, and error injection for unsupported service bits or oversized TLV inputs.
