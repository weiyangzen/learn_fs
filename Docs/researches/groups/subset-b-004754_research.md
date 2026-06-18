# Research: subset-b-004754

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/wmi.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/wmi.h

## Purpose

`wmi.h` is the central ath12k host/firmware WMI ABI declaration file. It defines the TLV framing, command groups, command IDs, event IDs, service bits, TLV tags, packed firmware command/event payloads, host-side argument structures, and exported WMI helper prototypes used by the rest of the driver. For this subset, its most relevant role is to provide the firmware contract consumed by `wow.c`: Wake-on-WLAN event IDs, wake reasons, bitmap wake pattern payloads, network-list offload/PNO structures, ARP/NS offload structures, GTK rekey offload structures, hardware data filter commands, and station keepalive definitions.

The file is not an implementation unit. It is a large protocol surface that must remain layout-compatible with firmware. Most structures that cross the firmware boundary use fixed-width little-endian fields and `__packed`; host-only inputs use normal CPU-endian scalar fields and are converted by `wmi.c`.

## Important APIs, Types, And Constants

- WMI TLV basics: `struct wmi_cmd_hdr`, `struct wmi_tlv`, `WMI_TLV_LEN`, `WMI_TLV_TAG`, `TLV_HDR_SIZE`, and `WMI_CMD_HDR_CMD_ID` define the generic command/event envelope.
- Command/event grouping: `enum wmi_cmd_group`, `WMI_TLV_CMD()`, `WMI_TLV_EV()`, `WMI_CMD_GRP()`, and `WMI_EVT_GRP_START_ID()` encode group-local IDs. The WoW-related groups include `WMI_GRP_WOW`, `WMI_GRP_ARP_NS_OFL`, `WMI_GRP_NLO_OFL`, `WMI_GRP_GTK_OFL`, and `WMI_GRP_HW_DATA_FILTER`.
- Command IDs: `WMI_WOW_ADD_WAKE_PATTERN_CMDID`, `WMI_WOW_DEL_WAKE_PATTERN_CMDID`, `WMI_WOW_ENABLE_DISABLE_WAKE_EVENT_CMDID`, `WMI_WOW_ENABLE_CMDID`, `WMI_WOW_HOSTWAKEUP_FROM_SLEEP_CMDID`, `WMI_SET_ARP_NS_OFFLOAD_CMDID`, `WMI_NETWORK_LIST_OFFLOAD_CONFIG_CMDID`, `WMI_GTK_OFFLOAD_CMDID`, `WMI_STA_KEEPALIVE_CMDID`, and `WMI_HW_DATA_FILTER_CMDID` are the command IDs used by suspend/resume offload flows.
- Event IDs: `WMI_WOW_WAKEUP_HOST_EVENTID`, `WMI_NLO_MATCH_EVENTID`, `WMI_GTK_OFFLOAD_STATUS_EVENTID`, and `WMI_GTK_REKEY_FAIL_EVENTID` provide asynchronous firmware notifications; `wmi.c` dispatches the WoW wake event to complete the ath12k wakeup completion.
- Service map bits: `WMI_TLV_SERVICE_WOW`, `WMI_TLV_SERVICE_ARPNS_OFFLOAD`, `WMI_TLV_SERVICE_NLO`, `WMI_TLV_SERVICE_GTK_OFFLOAD`, `WMI_TLV_SERVICE_D0WOW`, `WMI_TLV_SERVICE_UNIFIED_WOW_CAPABILITY`, and related bits gate feature advertisement before higher layers expose functionality.
- WoW events and reasons: `enum wmi_wow_wakeup_event` is the host-to-firmware enable bitmap (`WOW_BMISS_EVENT`, `WOW_MAGIC_PKT_RECVD_EVENT`, `WOW_NLO_DETECTED_EVENT`, `WOW_PATTERN_MATCH_EVENT`, `WOW_CSA_IE_EVENT`, `WOW_PROBE_REQ_WPS_IE_EVENT`, `WOW_AUTH_REQ_EVENT`, `WOW_ASSOC_REQ_EVENT`, `WOW_HTT_EVENT`, `WOW_RA_MATCH_EVENT`, and others). `enum wmi_wow_wake_reason` is the firmware-to-host reason value (`WOW_REASON_NLOD`, `WOW_REASON_PATTERN_MATCH_FOUND`, `WOW_REASON_RECV_MAGIC_PATTERN`, `WOW_REASON_PAGE_FAULT`, etc.). The inline `wow_wakeup_event()` and `wow_reason()` helpers map known values to strings for logs.
- Bitmap pattern ABI: `WOW_MIN_PATTERN_SIZE`, `WOW_MAX_PATTERN_SIZE`, `WOW_MAX_PKT_OFFSET`, `WOW_HDR_LEN`, `WOW_MAX_REDUCE`, `struct wmi_wow_bitmap_pattern_params`, `struct wmi_wow_add_pattern_cmd`, `struct wmi_wow_del_pattern_cmd`, and `enum wmi_tlv_pattern_type` define bitmap wake pattern upload and deletion.
- WoW enable/wakeup ABI: `enum wmi_wow_interface_cfg`, `struct wmi_wow_add_del_event_cmd`, `struct wmi_wow_enable_cmd`, `struct wmi_wow_host_wakeup_cmd`, `struct wmi_wow_ev_param`, `struct wmi_wow_ev_pg_fault_param`, and host-only `struct wmi_wow_ev_arg` define enable, host wake indication, and wake event parsing.
- PNO/NLO ABI: `WMI_PNO_MAX_SCHED_SCAN_PLANS`, `WMI_PNO_MAX_NETW_CHANNELS_EX`, `WMI_PNO_MAX_SUPP_NETWORKS`, dwell constants, `enum wmi_ssid_bcast_type`, NLO flag bits, `struct wmi_network_type_arg`, `struct wmi_pno_scan_req_arg`, `struct nlo_configured_params`, and `struct wmi_wow_nlo_config_cmd` define scheduled scan offload.
- Hardware data filter ABI: `enum hw_data_filter_type`, `struct wmi_hw_data_filter_cmd`, and `struct wmi_hw_data_filter_arg` define firmware filtering used during WoW to drop selected multicast/broadcast traffic.
- ARP/NS offload ABI: `WMI_IPV6_MAX_COUNT`, `WMI_IPV4_MAX_COUNT`, `struct wmi_arp_ns_offload_arg`, `struct wmi_arp_offload_params`, `struct wmi_ns_offload_params`, `struct wmi_set_arp_ns_offload_cmd`, and flag bits such as `WMI_ARPOL_FLAGS_VALID` and `WMI_NSOL_FLAGS_IS_IPV6_ANYCAST` define IPv4 ARP and IPv6 neighbor-solicitation response offload.
- GTK rekey ABI: `GTK_OFFLOAD_ENABLE_OPCODE`, `GTK_OFFLOAD_DISABLE_OPCODE`, `GTK_OFFLOAD_REQUEST_STATUS_OPCODE`, key/replay counter sizes, `struct wmi_gtk_rekey_offload_cmd`, and `struct wmi_gtk_offload_status_event` support GTK/IGTK state handoff to firmware and post-wake replay counter recovery.
- Keepalive ABI: `struct wmi_sta_keepalive_cmd`, `struct wmi_sta_keepalive_arg`, `enum wmi_sta_keepalive_method`, `WMI_STA_KEEPALIVE_INTERVAL_DEFAULT`, and `WMI_STA_KEEPALIVE_INTERVAL_DISABLE` support firmware null-frame keepalive during suspend.
- Exported helper prototypes: `ath12k_wmi_wow_host_wakeup_ind()`, `ath12k_wmi_wow_enable()`, `ath12k_wmi_wow_add_pattern()`, `ath12k_wmi_wow_del_pattern()`, `ath12k_wmi_wow_add_wakeup_event()`, `ath12k_wmi_wow_config_pno()`, `ath12k_wmi_hw_data_filter_cmd()`, `ath12k_wmi_arp_ns_offload()`, `ath12k_wmi_gtk_rekey_offload()`, `ath12k_wmi_gtk_rekey_getinfo()`, and `ath12k_wmi_sta_keepalive()` are the interface used by `wow.c`.

## Control Flow And Data Flow

At compile time, this header gives `wmi.c`, `wow.c`, `mac.c`, and other ath12k files a shared ABI. At runtime, callers fill host-side argument structs, `wmi.c` serializes them into packed TLV commands, firmware executes the commands, and firmware events are parsed back into host state.

For WoW suspend, `wow.c` calls WMI helper prototypes declared here. Wake event enablement is represented as a one-bit `event_bitmap` in `struct wmi_wow_add_del_event_cmd`. Pattern upload uses a top-level `struct wmi_wow_add_pattern_cmd` followed by TLV arrays including `struct wmi_wow_bitmap_pattern_params`. PNO/NLO configuration uses a start/stop command with a fixed `struct wmi_wow_nlo_config_cmd` header followed by TLV arrays of SSID profile structures and channel lists. ARP/NS offload uses a fixed command header followed by arrays of `wmi_ns_offload_params` and `wmi_arp_offload_params`.

For wakeup, firmware emits `WMI_WOW_WAKEUP_HOST_EVENTID` with `WMI_TAG_WOW_EVENT_INFO`. The event parser in `wmi.c` interprets it through `struct wmi_wow_ev_param`, maps the reason through `wow_reason()`, optionally dumps page-fault data using `struct wmi_wow_ev_pg_fault_param`, and completes `ab->wow.wakeup_completed`.

## State And Persistence Behavior

The header itself persists no state. It defines state shapes and limits. Persistent runtime state lives in ath12k objects (`ar->wow`, `ab->wow`, per-vif rekey/offload data, service bitmaps, and firmware-maintained offload state). Important limits here directly constrain persistent firmware configuration:

- Wake patterns are capped by `WOW_MAX_PATTERN_SIZE`, `WOW_MAX_PKT_OFFSET`, and the driver-level pattern count.
- PNO supports up to `WMI_PNO_MAX_SUPP_NETWORKS` match sets and `WMI_PNO_MAX_NETW_CHANNELS_EX` channels.
- IPv6 NS offload can carry up to `WMI_IPV6_MAX_COUNT` addresses in the host argument, while WMI command arrays have base and extension tuple handling.
- GTK offload stores KEK/KCK/replay counter material in firmware while suspended and reports replay/key state back on resume.

The distinction between host-only `_arg` structures and packed firmware structures is important for persistence: `_arg` values can be CPU-endian/transient, while packed command/event structs are serialized protocol records.

## Dependencies And Integration Points

- Depends on Linux/mac80211 headers for `struct cfg80211_ssid`, `struct ieee80211_hdr_3addr`, `ETH_ALEN`, and cfg80211/mac80211 feature plumbing.
- Depends on ath12k shared definitions in `htc.h` and `cmn_defs.h`.
- Integrated by `wmi.c`, which allocates skbs, fills TLVs, endian-converts fields, sends commands, parses events, and dispatches event IDs.
- Integrated by `wow.c`, which builds user-facing suspend/resume policy and calls the declared WMI helpers.
- Integrated by `mac.c` and hardware ops tables, which expose WoW support to cfg80211/mac80211 only when firmware service bits are present.
- Integrated by GTK/rekey handling in WMI event parsing and per-vif state updates.

## Risks And Edge Cases

- ABI drift is the primary risk. Changing enum values, tag IDs, packed layout, field sizes, or TLV ordering can silently break firmware communication.
- Several event and command bitmaps use shifts based on enum values. If `WOW_EVENT_MAX` or event values exceed the width assumed by implementation code, bitmap construction becomes unsafe.
- `WOW_REASON_UNSPECIFIED` is `-1` while many wire fields are unsigned little-endian. Consumers need explicit enum handling and should not assume every reason maps to a non-negative value.
- Pattern-size constants are shared with Ethernet-to-native-WiFi conversion logic. Off-by-one errors in `WOW_MAX_REDUCE`, offsets, or mask lengths can produce firmware pattern mismatch or memory corruption in command construction.
- PNO/NLO arrays are bounded in multiple places. The cfg80211 request conversion must validate SSID count, channel count, SSID length, and scan plan count before WMI serialization.
- ARP/NS offload crosses IPv4, IPv6, anycast, multicast solicitation, and MAC-address state. Incorrect flags can make firmware answer for invalid addresses while host sleeps.
- GTK material is sensitive key state. Logging and dumps must avoid exposing secret fields; the header itself only defines the structures.

## Test Signals

- Build coverage for `CONFIG_ATH12K`, `CONFIG_PM`, and WoW-enabled firmware paths catches prototype/layout mismatches.
- Suspend/resume smoke tests should show successful `WMI_WOW_ENABLE_CMDID`, HTC suspend completion, HIF suspend, HIF resume, `WMI_WOW_HOSTWAKEUP_FROM_SLEEP_CMDID`, and wake completion.
- WoW trigger tests should exercise magic packet, disconnect, pattern match, NLO match, and GTK rekey failure wake paths and verify logged `wow_reason()` strings.
- PNO tests should validate one-plan and two-plan cfg80211 scheduled scan requests, hidden SSIDs, passive scans, random MAC settings, and channel-count limits.
- ARP/NS offload tests should verify firmware responds for configured IPv4/IPv6 addresses during suspend and stops after resume cleanup.
- Static analysis should pay attention to packed-struct size assumptions, endian conversion, TLV length construction, and enum-to-bit shifts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/wmi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/wow.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/wow.c

## Purpose

`wow.c` implements ath12k Wake-on-WLAN suspend/resume support. It translates cfg80211/mac80211 WoWLAN requests into firmware WMI configuration, prepares protocol offloads that allow the device to stay associated while the host sleeps, coordinates HTC/HIF suspend and wakeup handshakes, and registers WoWLAN capabilities with the wiphy when firmware advertises support.

The file is active only when power-management support compiles the non-stub functions from `wow.h`. It is tightly coupled to ath12k WMI helpers, HIF interrupt/suspend operations, mac80211 vif state, IPv4/IPv6 address state, GTK rekey state, and cfg80211 WoWLAN request structures.

## Important APIs And Functions

- `ath12k_wow_enable(struct ath12k *ar)`: sends firmware WoW enable and waits for HTC suspend completion. It retries up to `ATH12K_WOW_RETRY_NUM` times when firmware NACKs or does not complete immediately.
- `ath12k_wow_wakeup(struct ath12k *ar)`: sends host-wakeup indication and waits for `ab->wow.wakeup_completed`.
- `ath12k_wow_op_suspend(struct ieee80211_hw *hw, struct cfg80211_wowlan *wowlan)`: mac80211 suspend callback. It clears stale firmware state, programs wake events/patterns/offloads/filters/keepalive, enables WoW, disables interrupts, and suspends HIF.
- `ath12k_wow_op_resume(struct ieee80211_hw *hw)`: mac80211 resume callback. It resumes HIF, re-enables interrupts, wakes firmware, cleans NLO/filter/protocol offloads, disables keepalive, and requests restart on recoverable failure.
- `ath12k_wow_op_set_wakeup(struct ieee80211_hw *hw, bool enabled)`: toggles Linux device wakeup capability.
- `ath12k_wow_init(struct ath12k *ar)`: advertises WoWLAN capabilities to cfg80211 when `WMI_TLV_SERVICE_WOW` is present, adjusts pattern limits for native WiFi decap, and enables net-detect capability when `WMI_TLV_SERVICE_NLO` exists.
- `ath12k_wow_vif_set_wakeups()`: maps cfg80211 WoWLAN settings to WMI wake events and bitmap wake patterns per vdev.
- `ath12k_wow_convert_8023_to_80211()`: converts cfg80211 Ethernet-format packet patterns into 802.11/native-WiFi offsets and masks when firmware receive decap mode is native WiFi.
- `ath12k_wow_pno_check_and_convert()`: validates cfg80211 scheduled-scan net-detect config and converts it into `struct wmi_pno_scan_req_arg`.
- `ath12k_wow_arp_ns_offload()`, `ath12k_wow_prepare_ns_offload()`, and `ath12k_wow_prepare_arp_offload()`: collect interface IPv6/IPv4 addresses and program ARP/NS response offload.
- `ath12k_gtk_rekey_offload()`: enables/disables firmware GTK rekey offload and fetches rekey info before disabling on resume.
- `ath12k_wow_set_hw_filter()` and `ath12k_wow_clear_hw_filter()`: enable/disable firmware data filtering, currently dropping non-ICMPv6 multicast on STA vdevs during WoW.
- `ath12k_wow_set_keepalive()`: configures per-vif firmware keepalive via `ath12k_mac_vif_set_keepalive()`.

## Control Flow

Suspend starts in `ath12k_wow_op_suspend()`. It asserts the wiphy lock, selects the first radio (`ath12k_ah_to_ar(ah, 0)`), and runs a strict setup sequence:

1. `ath12k_wow_cleanup()` disables all wake events and deletes all possible bitmap patterns for every default-link vif.
2. `ath12k_wow_set_wakeups()` skips P2P vdevs and programs requested events/patterns per vdev.
3. `ath12k_wow_protocol_offload(ar, true)` enables ARP/NS and GTK rekey offloads.
4. `ath12k_mac_wait_tx_complete()` drains pending transmit work before the device sleeps.
5. `ath12k_wow_set_hw_filter()` enables firmware filtering for STA vdevs.
6. `ath12k_wow_set_keepalive()` enables null-frame keepalive with the default interval.
7. `ath12k_wow_enable()` sends the WMI WoW enable command and waits for HTC suspend completion, retrying after firmware NACK-like incomplete attempts.
8. HIF and CE IRQs are disabled and `ath12k_hif_suspend()` suspends the bus.

If any setup step fails before HIF suspend, the code jumps to cleanup and clears wake events/patterns. If HIF suspend fails after WoW enable, it sends a WoW wakeup indication before cleanup. The return value follows mac80211 suspend semantics: nonzero failure is returned as `1` rather than the original negative errno.

Resume starts in `ath12k_wow_op_resume()`. It resumes HIF, enables CE and core IRQs, sends a firmware wakeup indication, stops PNO if it was enabled, clears hardware filters, disables ARP/NS and GTK offload, and disables keepalive. If resume fails while hardware state is `ATH12K_HW_STATE_ON`, it requests restart by changing state to `ATH12K_HW_STATE_RESTARTING` and returning `1`; if the state is already off/restarting/wedged/testmode, it returns `-EIO`.

## State And Persistence Behavior

- `ab->dev_flags` bit `ATH12K_FLAG_HTC_SUSPEND_COMPLETE` records the asynchronous HTC suspend completion result used by `ath12k_wow_enable()`.
- `ab->htc_suspend` and `ab->wow.wakeup_completed` are completions that serialize firmware suspend/wakeup handshakes with host control flow.
- `ar->wow.wowlan_support` is populated in init and assigned to `wiphy->wowlan`; it persists as the advertised userspace capability set.
- `ar->wow.max_num_patterns` is set to `ATH12K_WOW_PATTERNS` and used both for cfg80211 capability and cleanup deletion loops.
- `ar->nlo_enabled` records whether PNO/NLO was started so resume cleanup can send a stop command.
- Per-vif `rekey_data.enable_offload` gates GTK offload; on resume, the driver fetches firmware rekey status before disabling offload.
- IPv4/IPv6 offload state is gathered from live netdev/vif state each suspend and is not locally persisted after command submission.

## Dependencies And Integration Points

- cfg80211/mac80211: consumes `struct cfg80211_wowlan`, `cfg80211_pkt_pattern`, scheduled-scan request data, vif types, `wiphy_wowlan_support`, and mac80211 suspend/resume hooks.
- WMI: all firmware programming goes through helpers declared in `wmi.h` and implemented in `wmi.c`.
- HIF/HTC: WoW enable requires HTC suspend completion; actual platform sleep uses `ath12k_hif_suspend()`, `ath12k_hif_resume()`, and IRQ enable/disable helpers.
- Linux IPv6/IPv4 stack: `in6_dev_get()`, `inet6_dev` address lists, anycast lists, and vif ARP address configuration feed NS/ARP offload.
- ath12k MAC/vif state: iterates `ar->arvifs`, uses default links only, skips P2P vdevs for wake programming, checks vdev type/subtype and `is_up`.
- Device power management: `device_set_wakeup_capable()` and `device_set_wakeup_enable()` integrate with the Linux device wakeup model.

## Risks And Edge Cases

- Multi-link/MLO limitation: the suspend/resume callbacks select link/radio 0 and the vif loops generally operate only on default links. This is intentional in current code but is a risk if non-default links need independent WoW handling.
- Pattern conversion is offset-sensitive. Native-WiFi decap requires translating Ethernet destination/source/type fields into 802.11 addr1/addr3/RFC1042 locations. Boundary mistakes would cause missed wakeups or oversized patterns.
- `ath12k_wow_vif_set_wakeups()` sets `ar->nlo_enabled = true` before validating/converting PNO. If conversion fails, NLO may be marked enabled even though no firmware start command succeeded.
- PNO WMI config return is not checked inside the `if (!ret)` block in `ath12k_wow_vif_set_wakeups()`. A failed `ath12k_wmi_wow_config_pno()` can still lead to `WOW_NLO_DETECTED_EVENT` being enabled.
- Hardware filter clear must run on resume. If resume fails early, firmware filters/offloads may remain inconsistent until restart.
- ARP/NS offload allocates one reusable `offload` buffer and clears it per vif. Any future asynchronous use would need lifetime changes, but current WMI calls serialize before freeing.
- IPv6 address collection uses nested `idev->lock` and RCU read sections. Changes here need care around lock ordering and address lifetime.
- Return code normalization in suspend loses specific errno details to mac80211. Logs are essential for diagnosing which step failed.

## Test Signals

- WoW capability should appear in `iw phy` only when firmware service bits include WoW; net-detect should appear only with NLO support.
- Suspend with no patterns, with magic packet, with disconnect wake, and with user packet patterns should issue the expected WMI add-event/add-pattern commands and complete HTC suspend.
- Native-WiFi decap devices need pattern tests across destination MAC, source MAC, EtherType, and payload offsets to validate 802.3-to-802.11 conversion.
- Scheduled scan WoW tests should cover one and two scan plans, hidden SSIDs, random MAC, passive scan, invalid SSID length, too many channels, and no match sets.
- IPv4 ARP and IPv6 NS offload can be validated by ping/neighbor probes while the host is suspended.
- GTK rekey offload tests should verify no disconnect across rekey while suspended and correct replay/key state after resume.
- Failure-injection useful signals include WMI command send failure, HTC suspend timeout, HIF suspend failure, wakeup completion timeout, and resume failure state transition to restart.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/wow.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/wow.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/wow.h

## Purpose

`wow.h` is the public ath12k Wake-on-WLAN interface for the driver. It defines small driver-local WoW state structures, constants used by the implementation, helper pattern conversion types, and function prototypes exported to MAC/HW operations. It also provides no-op inline stubs when `CONFIG_PM` is disabled, allowing the rest of ath12k to compile without conditionalizing every call site.

## Important APIs, Types, And Constants

- `ATH12K_WOW_RETRY_NUM` and `ATH12K_WOW_RETRY_WAIT_MS`: bound the firmware WoW-enable retry loop in `ath12k_wow_enable()`.
- `ATH12K_WOW_PATTERNS`: driver-advertised maximum number of WoW bitmap patterns, assigned to `ar->wow.max_num_patterns`.
- `struct ath12k_wow`: per-radio WoW state containing `max_num_patterns`, the `wakeup_completed` completion, and the cfg80211-visible `wiphy_wowlan_support`.
- `struct ath12k_pkt_pattern`: driver-local converted pattern buffer with pattern bytes, byte mask, length, and packet offset. It is used when converting cfg80211 Ethernet patterns into firmware bitmap patterns.
- `struct rfc1042_hdr`: packed RFC1042/SNAP header shape used to calculate native-WiFi pattern offsets for EtherType matching.
- PM-enabled prototypes: `ath12k_wow_init()`, `ath12k_wow_op_suspend()`, `ath12k_wow_op_resume()`, `ath12k_wow_op_set_wakeup()`, `ath12k_wow_enable()`, and `ath12k_wow_wakeup()`.
- PM-disabled stubs: `ath12k_wow_init()`, `ath12k_wow_enable()`, and `ath12k_wow_wakeup()` return success. Suspend/resume/set_wakeup callbacks are omitted because they are only wired when PM support exists.

## Control Flow

The header is included by ath12k implementation files that need WoW state or callbacks. `mac.c` calls `ath12k_wow_init()` during hardware setup, while HW ops registration uses `ath12k_wow_op_suspend`, `ath12k_wow_op_resume`, and `ath12k_wow_op_set_wakeup` as mac80211 PM callbacks when compiled. `wow.c` uses the constants and local structures to bound retry behavior and pattern conversion buffers.

When `CONFIG_PM` is not set, callers can still invoke init/enable/wakeup helper names without linker errors, but they do not program firmware. That preserves build coverage while making actual WoW functionality unavailable.

## State And Persistence Behavior

`struct ath12k_wow` persists in the ath12k radio structure. Its `wiphy_wowlan_support` member is assigned into `wiphy->wowlan`, so its lifetime must cover the wiphy lifetime. `wakeup_completed` is initialized elsewhere in core setup and reused across wakeup handshakes. The local `ath12k_pkt_pattern` buffers are transient stack objects in `wow.c`; they do not persist after WMI command construction.

## Dependencies And Integration Points

- Depends on WoW constants from `wmi.h` such as `WOW_MAX_PATTERN_SIZE`.
- Depends on cfg80211/mac80211 types through included compilation context (`struct wiphy_wowlan_support`, `struct ieee80211_hw`, `struct cfg80211_wowlan`).
- Integrated by ath12k MAC/HW operation registration and `wow.c`.
- The RFC1042 header definition is consumed by pattern conversion in `wow.c` and must stay consistent with 802.11 SNAP encapsulation assumptions.

## Risks And Edge Cases

- `struct ath12k_pkt_pattern` embeds arrays sized by `WOW_MAX_PATTERN_SIZE`; changes to WMI limits affect stack usage in pattern conversion.
- The PM-disabled stubs return success. Callers must avoid assuming that a successful stub means firmware WoW was configured.
- `wiphy->wowlan` points into `ar->wow.wowlan_support`; moving or shortening the lifetime of `struct ath12k_wow` would create dangling capability pointers.
- Retry constants encode firmware behavior assumptions. Reducing retry count or wait time can make suspend flaky on firmware that legitimately asks the host to retry.

## Test Signals

- PM-enabled builds should link real WoW callbacks and expose WoWLAN only with firmware support.
- PM-disabled builds should compile without undefined WoW helper symbols and should not expose operational suspend/resume WoW callbacks.
- Static checks should verify `WOW_MAX_PATTERN_SIZE` changes still leave pattern conversion and WMI bitmap structures aligned.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/wow.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath5k/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath5k/Kconfig

## Purpose

This Kconfig file defines build-time configuration for the ath5k driver, covering the main Atheros 5xxx mac80211 driver plus optional debug, tracing, AHB bus, PCI bus, and testing-channel support. It controls which source files in the ath5k Makefile are compiled and which platform families can use the driver.

## Important Symbols

- `ATH5K`: main tristate driver option for Atheros 5xxx wireless cards. It depends on `(PCI || ATH25) && MAC80211`, selects `ATH_COMMON`, selects mac80211 LED support when LED dependencies allow it, and selects `ATH5K_AHB` on ATH25 or `ATH5K_PCI` otherwise.
- `ATH5K_DEBUG`: optional bool for ath5k debug messages and debugfs controls. It depends on `ATH5K`.
- `ATH5K_TRACER`: optional bool for tracepoint support. It depends on `ATH5K` and `EVENT_TRACING`.
- `ATH5K_AHB`: bool for WiSoC/AHB support on ATH25 platforms. It depends on `ATH25 && ATH5K`.
- `ATH5K_PCI`: bool for PCI support. It depends on `!ATH25 && PCI`.
- `ATH5K_TEST_CHANNELS`: optional research/testing feature that enables non-standard channels only when `CFG80211_CERTIFICATION_ONUS` is set.

## Control Flow

Kconfig resolution selects the driver and bus backend at build configuration time. On ATH25 systems, `ATH5K` automatically selects `ATH5K_AHB`, causing `ahb.o` to be included. On non-ATH25 PCI systems, it selects `ATH5K_PCI`, causing `pci.o` to be included. Optional debug and tracing choices add debug code paths and user-visible debugfs/tracing features but do not change the core module name.

## State And Persistence Behavior

The file does not define runtime state. It persists configuration into the kernel build through generated config symbols. Those symbols determine which objects are linked into `ath5k.o` and which runtime controls exist. `ATH5K_TEST_CHANNELS` affects regulatory/channel behavior and therefore should be treated as a build-time policy decision rather than a runtime toggle.

## Dependencies And Integration Points

- Integrates with the kernel wireless stack through `MAC80211` and `ATH_COMMON`.
- Integrates with platform selection via `PCI` and `ATH25`.
- Integrates with LED support through `MAC80211_LEDS` when LED class support is compatible.
- Integrates with the ath5k Makefile via `CONFIG_ATH5K_DEBUG`, `CONFIG_ATH5K_AHB`, and `CONFIG_ATH5K_PCI`.
- User-facing help text documents supported MAC/PHY families and debugfs usage.

## Risks And Edge Cases

- `ATH5K_AHB` and `ATH5K_PCI` are selected based on ATH25 vs non-ATH25 assumptions. Unusual platforms with both buses or nonstandard integration may need careful config review.
- Debug and tracer features increase observability but can alter timing or add build dependencies.
- `ATH5K_TEST_CHANNELS` must remain gated by certification-onus because it enables non-standard channels intended only for research.
- If `ATH5K` is built as a module, the resulting module is still `ath5k`; bus backend objects are folded into that module, not separate modules.

## Test Signals

- `make oldconfig`/`menuconfig` should show AHB only on ATH25 and PCI only when PCI is available and ATH25 is not selected.
- Build matrix should include `ATH5K=m/y`, debug on/off, tracer on/off with `EVENT_TRACING`, and ATH25 AHB builds.
- Runtime module composition can be checked by verifying that AHB probe symbols exist only in ATH25/AHB builds and PCI support only in PCI builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath5k/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath5k/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath5k/Makefile

## Purpose

The ath5k Makefile declares the object composition for the `ath5k.o` driver module. It lists common core objects, conditionally includes debug and bus-backend objects, adds a local include path for `base.o`, and connects the final composite object to `CONFIG_ATH5K`.

## Important Build Rules

- `ath5k-y` includes core hardware/driver components: capabilities, init values, EEPROM, GPIO, descriptors, DMA, queues, PCU/PHY/reset, attach/base, LED, rfkill, ANI, sysfs, and mac80211 operations.
- `CFLAGS_base.o += -I$(src)` adds the ath5k source directory to the include path for `base.o`.
- `ath5k-$(CONFIG_ATH5K_DEBUG) += debug.o` conditionally compiles debug support.
- `ath5k-$(CONFIG_ATH5K_AHB) += ahb.o` conditionally compiles the ATH25/AHB platform backend.
- `ath5k-$(CONFIG_ATH5K_PCI) += pci.o` conditionally compiles the PCI backend.
- `obj-$(CONFIG_ATH5K) += ath5k.o` ties the composite module to the main Kconfig symbol.

## Control Flow

Kbuild expands the `ath5k-y` and `ath5k-$(CONFIG_*)` lists into a single composite `ath5k.o`. Runtime bus attach behavior depends on whether `ahb.o` or `pci.o` was linked. Core functionality such as ANI is always present when ath5k is built because `ani.o` is unconditionally listed.

## State And Persistence Behavior

The file has no runtime state. Its persistent effect is the compiled object graph. The unconditional inclusion of `ani.o` means `struct ath5k_ani_state` and the ANI sysfs/debug integration are available in all ath5k builds, though runtime ANI behavior still depends on hardware revision and mode.

## Dependencies And Integration Points

- Mirrors `Kconfig`: `CONFIG_ATH5K_DEBUG`, `CONFIG_ATH5K_AHB`, and `CONFIG_ATH5K_PCI` directly select optional object files.
- Integrates with Linux Kbuild composite-object syntax.
- Build ordering is declarative, but dependencies between objects are resolved by linking the composite module.

## Risks And Edge Cases

- Adding a source file without updating this Makefile leaves code unbuilt.
- Moving headers or relying on local include paths outside `base.o` may require additional `CFLAGS_*.o` rules.
- Conditional bus objects must remain aligned with Kconfig dependency logic; otherwise unsupported probe code could be linked or required backend code omitted.

## Test Signals

- `make M=drivers/net/wireless/ath/ath5k` or the repository equivalent should show `ani.o` always built with ath5k.
- Build with `CONFIG_ATH5K_DEBUG=y` should include `debug.o`.
- ATH25 builds should include `ahb.o`; non-ATH25 PCI builds should include `pci.o`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath5k/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath5k/ahb.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath5k/ahb.c

## Purpose

`ahb.c` is the ath5k platform-driver backend for Atheros 5xxx WiSoC devices on ATH25/AHB systems. It provides platform EEPROM/MAC accessors, reads the hardware revision from board configuration, maps device registers, enables SoC-specific WLAN bus access and byte swapping, attaches the common ath5k hardware layer, and tears everything down on platform-device removal.

## Important APIs And Functions

- `ath5k_ahb_read_cachesize()`: returns cache-line size in 4-byte word units through the ath bus ops interface.
- `ath5k_ahb_eeprom_read()`: reads EEPROM words from platform board configuration radio data.
- `ath5k_hw_read_srev()`: sets `ah->ah_mac_srev` from `ar231x_board_config.devid`; this AHB backend provides the symbol used by common attach code.
- `ath5k_ahb_eeprom_read_mac()`: copies WLAN0 or WLAN1 MAC address from board config depending on platform device ID.
- `ath_ahb_bus_ops`: declares bus type `ATH_AHB` and provides cache/EEPROM/MAC callbacks to common ath5k init.
- `ath_ahb_probe()`: platform probe path that validates platform data/resources, ioremaps MMIO, obtains IRQ, allocates `ieee80211_hw`, initializes `struct ath5k_hw`, enables SoC WLAN access, calls `ath5k_init_ah()`, and stores driver data.
- `ath_ahb_remove()`: platform remove path that disables WLAN access, deinitializes ath5k, unmaps registers, and frees `ieee80211_hw`.
- `module_platform_driver(ath_ahb_driver)`: registers the `ar231x-wmac` platform driver.

## Control Flow

Probe requires platform data. It fetches the memory resource, maps it with `ioremap()`, gets the IRQ, and allocates a mac80211 hardware object sized for `struct ath5k_hw`. It fills `ah->hw`, `ah->dev`, `ah->iobase`, `ah->irq`, and `ah->devid`.

For AR2315-or-newer devices (`devid >= AR5K_SREV_AR2315_R6`), probe enables WMAC AHB arbitration and global WMAC byte swapping through SoC registers. For older AR5312/231x style devices, it enables WLAN0 or WLAN1 DMA access through `AR5K_AR5312_ENABLE`. On dual-band AR5312 board configurations where radio 0 is a pass-through multiband radio, it sets `cap_needs_2GHz_ovr` to disable 2 GHz support in the driver for that device.

After platform setup, `ath5k_init_ah(ah, &ath_ahb_bus_ops)` attaches the common ath5k driver. On failure, probe frees `ieee80211_hw`, unmaps MMIO, and returns an error. Remove reverses SoC enablement, calls `ath5k_deinit_ah()`, unmaps `ah->iobase`, and frees the hardware object.

## State And Persistence Behavior

- Platform data (`struct ar231x_board_config`) is treated as persistent firmware/board configuration and supplies device ID, EEPROM/radio data, board flags, and MAC addresses.
- `struct ath5k_hw` stores mapped MMIO base, IRQ, device ID, capabilities override, and mac80211 hardware pointer for the lifetime of the platform device.
- SoC registers controlling AHB arbitration, byte swapping, and WLAN DMA access are persistent hardware state while the driver is bound. Remove clears the arbitration/DMA enable bits but does not clear the AR2315 byte-swap bit.
- Driver data on the platform device stores the `ieee80211_hw` pointer after successful attach.

## Dependencies And Integration Points

- Depends on ATH25 platform definitions from `<ath25_platform.h>`, especially `struct ar231x_board_config`.
- Depends on Linux platform-device resource APIs, `ioremap()`/`iounmap()`, and mac80211 `ieee80211_alloc_hw()`.
- Integrates with common ath5k attach/deinit through `ath5k_init_ah()` and `ath5k_deinit_ah()`.
- Integrates with ath common bus operations via `struct ath_bus_ops`.
- Uses register definitions from `reg.h` for SoC-level enable/arbitration/byteswap registers.

## Risks And Edge Cases

- `ath5k_ahb_eeprom_read()` checks `if (eeprom > eeprom_end)` after advancing by word offset. A pointer exactly at the end is not rejected, and the comparison crosses typed `u16 *` vs a `void *`-derived end; changes should be careful about byte/word bounds.
- Probe assumes platform data remains valid and correctly sized. Bad board data can lead to invalid EEPROM reads or MAC addresses.
- Global SoC register accesses use fixed physical addresses cast to `void __iomem *`, not resources from the platform device. This is platform-specific and risky to generalize.
- Remove disables AHB arbitration/DMA but does not undo the AR2315 global WMAC byteswap bit set in probe.
- Error cleanup is mostly complete, but any future resource added after `ath5k_init_ah()` must be unwound on all probe failures.

## Test Signals

- ATH25/AHB boot should bind the `ar231x-wmac` platform device and create an ath5k phy.
- EEPROM and MAC address reads should match board configuration for both WLAN0 and WLAN1 IDs.
- Probe failure injection for missing platform data, missing memory resource, ioremap failure, IRQ failure, allocation failure, and attach failure should release resources without leaks.
- On AR2315+ hardware, register traces should show AHB arbitration and byteswap enablement; on older hardware, WLAN0/WLAN1 DMA bits should track bind/unbind.
- Dual-band AR5312 boards should show the expected 2 GHz capability override behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath5k/ahb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath5k/ani.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath5k/ani.c

## Purpose

`ani.c` implements ath5k Adaptive Noise Immunity. ANI dynamically tunes PHY sensitivity/noise-immunity parameters based on OFDM and CCK timing errors relative to channel listen time. It supports automatic mode, manual low-sensitivity/high-sensitivity presets, interrupt-driven hardware PHY error counters on newer chips, and frame-by-frame PHY error reporting on older chips.

The goal is to reduce false detects and interference impact without permanently sacrificing sensitivity. The code writes PHY registers to adjust noise immunity, spur immunity, firstep level, OFDM weak-signal detection, and CCK weak-signal detection.

## Important APIs And Functions

- `ath5k_ani_set_noise_immunity_level()`: writes desired-size, AGC coarse low/high, and FIR power fields. This driver uses two effective levels (`ATH5K_ANI_MAX_NOISE_IMM_LVL` is 1).
- `ath5k_ani_set_spur_immunity_level()`: writes OFDM self-correlation CYPWR threshold. Maximum spur level is chip-revision dependent.
- `ath5k_ani_set_firstep_level()`: writes the PHY firstep threshold with levels 0, 4, and 8.
- `ath5k_ani_set_ofdm_weak_signal_detection()`: toggles OFDM weak-signal detection by writing multiple weak OFDM threshold fields and enabling/disabling self-correlation.
- `ath5k_ani_set_cck_weak_signal_detection()`: toggles the CCK weak-signal threshold.
- `ath5k_ani_raise_immunity()`: automatic-mode state machine for increasing immunity when OFDM/CCK errors are high. It considers current immunity levels, opmode, OFDM vs CCK trigger, beacon RSSI, band, and weak-signal state.
- `ath5k_ani_lower_immunity()`: automatic-mode state machine for reducing immunity after a long low-error period.
- `ath5k_hw_ani_get_listen_time()`: updates ath common cycle counters under `cc_lock`, snapshots counters into ANI state, and returns listen time.
- `ath5k_ani_save_and_clear_phy_errors()`: reads hardware PHY error counters, resets them quickly, converts counter values into OFDM/CCK error counts, and accumulates both period and total debug counters.
- `ath5k_ani_calibration()`: main periodic ANI algorithm. It accumulates listen time, checks high and low error thresholds scaled by listen time, raises or lowers immunity, and restarts the ANI period when action is taken or after a long low-error interval.
- `ath5k_ani_mib_intr()`: interrupt handler for hardware PHY error counter overflow. It clears counters, accumulates errors, and schedules the ANI tasklet if thresholds are exceeded.
- `ath5k_ani_phy_error_report()`: older-hardware path for counting OFDM/CCK timing errors from received PHY error frames.
- `ath5k_ani_init()`: initializes mode, default levels, max spur level, PHY counter/rxfilter plumbing, and `ah->ani_state.ani_mode`.
- `ath5k_ani_print_counters()`: debug-only register dump for ANI and MAC counters.

## Control Flow

Initialization with `ath5k_ani_init()` is skipped on pre-AR5212 hardware. For valid modes, it clears `ah->ani_state`, chooses `max_spur_level` based on MAC revision, applies initial register settings, and enables either hardware PHY error counters or RX filtering of PHY error frames when automatic mode is selected. Non-auto modes disable those automatic error inputs.

In normal operation, `ath5k_ani_calibration()` is invoked by the calibration path/tasklet. It always updates listen time so busy-time stats remain useful even in manual modes. In automatic mode it then merges pending PHY errors, computes high and low OFDM/CCK thresholds as `listen_time * trigger / 1000`, and reacts:

- If OFDM or CCK errors exceed high thresholds, it raises immunity and restarts the period.
- If listen time exceeds five ANI listen periods and both error counts are below low thresholds, it lowers immunity and restarts the period.
- Otherwise, it leaves current settings and keeps accumulating period counters.

The raise path first increases noise immunity, then for OFDM can increase spur immunity. AP mode then raises firstep as a simple fallback. STA/IBSS mode uses beacon RSSI: high RSSI can disable OFDM weak-signal detection and reset spur level before raising firstep; mid RSSI keeps/enables OFDM weak-signal detection and can raise firstep; low RSSI on 2 GHz disables OFDM weak-signal detection and lowers firstep to preserve CCK sensitivity.

The lower path reverses in a conservative order: AP mode lowers firstep first; STA/IBSS behavior depends on RSSI, then all modes lower spur immunity and finally noise immunity.

## State And Persistence Behavior

`ah->ani_state` persists current mode and live tuning state:

- Current parameters: `noise_imm_level`, `spur_level`, `firstep_level`, `ofdm_weak_sig`, `cck_weak_sig`, and `max_spur_level`.
- Current algorithm counters: `listen_time`, `ofdm_errors`, and `cck_errors`.
- Debug/stat counters: `last_cc`, `last_listen`, `last_ofdm_errors`, `last_cck_errors`, `sum_ofdm_errors`, and `sum_cck_errors`.

PHY register writes persist in hardware until reinitialized, reset, or overwritten by later ANI changes. `ath5k_ani_period_restart()` preserves last period values for debugging while clearing active period counters. `ath5k_ani_init()` clears the whole state each time mode changes, which resets accumulated debug totals.

## Dependencies And Integration Points

- Uses register definitions and helpers from `reg.h`, including `AR5K_REG_WRITE_BITS`, `AR5K_REG_ENABLE_BITS`, and `AR5K_REG_DISABLE_BITS`.
- Uses ath common cycle counters (`ath_hw_cycle_counters_update()`, `ath_hw_get_listen_time()`) protected by `ath_common.cc_lock`.
- Integrated with interrupt handling through `ath5k_ani_mib_intr()` when MIB/PHY counters overflow.
- Integrated with RX descriptor processing through `ath5k_ani_phy_error_report()` on hardware without PHY error counters.
- Integrated with calibration/timer/tasklet code through `ath5k_ani_calibration()`.
- Integrated with sysfs and debugfs through exported manual setters and debug counter state.
- Depends on `ewma_beacon_rssi_read(&ah->ah_beacon_rssi_avg)` and current channel/opmode to make RSSI-sensitive decisions.

## Risks And Edge Cases

- The high/low threshold math depends on listen time. Very small listen windows can produce low thresholds and aggressive changes; very busy channels may delay lowering immunity.
- Hardware PHY error counters are reset inside interrupt context to prevent repeated interrupts. Incorrect ordering could cause interrupt storms or lost counts.
- `ath5k_ani_save_and_clear_phy_errors()` stores unsigned counter reads but checks `<= 0`; the zero/superfluous-interrupt case works, but underflow/overflow reasoning is subtle because hardware counters count up from a programmed offset.
- Manual mode changes through sysfs/debug paths can race conceptually with automatic calibration if callers do not ensure mode expectations.
- Beacon RSSI heuristics are global for STA/IBSS; the code comments note IBSS would ideally use per-neighbor RSSI to avoid deafening distant peers.
- CCK weak-signal lowering is left as a TODO/commented idea, so CCK behavior is less symmetric than OFDM behavior.
- Register values come from HAL/ath9k precedent and comments acknowledge unused alternative five-level tables. Changing these values requires hardware validation.

## Test Signals

- Automatic mode in a clean RF environment should eventually lower immunity after sustained low OFDM/CCK error counts.
- Injected OFDM timing errors should schedule ANI and raise noise/spur/OFDM-related immunity in the expected order.
- Injected CCK timing errors should raise noise/firstep-related immunity without OFDM-only spur steps.
- MIB interrupt tests on hardware with PHY error counters should show counters reset and no repeated spurious interrupts.
- Older hardware tests should show `AR5K_RX_FILTER_PHYERR` enabled in auto mode and `ath5k_ani_phy_error_report()` driving the same tasklet behavior.
- Sysfs/debug manual controls should update both registers and `ah->ani_state` fields and reject out-of-range levels.
- Reset/reconfigure tests should verify `ath5k_ani_init()` restores expected defaults and counter state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath5k/ani.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath5k/ani.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath5k/ani.h

## Purpose

`ani.h` declares the ath5k Adaptive Noise Immunity interface and state. It defines thresholds, maximum levels, ANI operating modes, the persistent `struct ath5k_ani_state`, and function prototypes used by calibration, interrupt, RX error, sysfs, and debug code.

## Important APIs, Types, And Constants

- Threshold constants: `ATH5K_ANI_LISTEN_PERIOD`, `ATH5K_ANI_OFDM_TRIG_HIGH`, `ATH5K_ANI_OFDM_TRIG_LOW`, `ATH5K_ANI_CCK_TRIG_HIGH`, and `ATH5K_ANI_CCK_TRIG_LOW` define error thresholds relative to listen time.
- RSSI thresholds: `ATH5K_ANI_RSSI_THR_HIGH` and `ATH5K_ANI_RSSI_THR_LOW` guide sensitivity choices in STA/IBSS mode.
- Level caps: `ATH5K_ANI_MAX_FIRSTEP_LVL` and `ATH5K_ANI_MAX_NOISE_IMM_LVL` bound exported setter inputs.
- `enum ath5k_ani_mode`: defines off, manual low, manual high, and automatic modes. Manual low maximizes sensitivity; manual high minimizes sensitivity; auto adapts based on error counts.
- `struct ath5k_ani_state`: stores mode, current parameter levels, max spur level, active algorithm counters, and debug/stat snapshots.
- Main lifecycle/functions: `ath5k_ani_init()`, `ath5k_ani_mib_intr()`, `ath5k_ani_calibration()`, and `ath5k_ani_phy_error_report()`.
- Manual controls: `ath5k_ani_set_noise_immunity_level()`, `ath5k_ani_set_spur_immunity_level()`, `ath5k_ani_set_firstep_level()`, `ath5k_ani_set_ofdm_weak_signal_detection()`, and `ath5k_ani_set_cck_weak_signal_detection()`.
- Debug function: `ath5k_ani_print_counters()`.

## Control Flow

The header is consumed by `ani.c` and by callers elsewhere in ath5k. Attach/base code initializes or restores ANI mode; interrupt handling calls `ath5k_ani_mib_intr()`; RX descriptor paths call `ath5k_ani_phy_error_report()` on older hardware; calibration code calls `ath5k_ani_calibration()`; sysfs/debug code invokes the manual setters and reads state fields.

The exported setters make individual PHY parameter changes possible outside the automatic algorithm. `ath5k_ani_init()` is the mode boundary: it applies mode defaults, enables/disables error sources, and updates `ani_state.ani_mode`.

## State And Persistence Behavior

`struct ath5k_ani_state` is embedded in `struct ath5k_hw`, so it persists for the device lifetime. It tracks current hardware-programmed parameter levels and algorithm counters. `last_*` and `sum_*` fields exist for debug/statistics only and are not required for making tuning decisions. `last_cc` snapshots ath common cycle counters from the previous ANI run.

Threshold constants define how quickly state changes persist or revert. Because state is embedded and not dynamically allocated, callers must initialize it through `ath5k_ani_init()` after attach/reset or mode change.

## Dependencies And Integration Points

- Includes `../ath.h` for `struct ath_cycle_counters` and shared ath definitions.
- Forward-declares `enum ath5k_phy_error_code` for RX PHY error reporting.
- The state is referenced by `ath5k.h`, `ani.c`, `base.c`, `desc.c`, `sysfs.c`, and `debug.c`.
- `CONFIG_ATH5K_DEBUG` controls whether the debug counter printing implementation is compiled, but the prototype is always visible.

## Risks And Edge Cases

- Constants are part of driver behavior, not firmware ABI, but changing them can materially affect sensitivity, throughput, and stability in noisy environments.
- `max_spur_level` is stored in state rather than as a macro because it depends on chip revision; callers must not use fixed spur bounds.
- Manual setters are exported and can be called while mode is auto. Callers should understand that the next calibration may overwrite manual settings.
- Debug/stat fields can be reset by `ath5k_ani_init()`, so tests relying on accumulated counters need to account for mode changes and resets.

## Test Signals

- Compile coverage should confirm all declared functions are defined when ath5k is built.
- Sysfs/debug controls should reflect `struct ath5k_ani_state` values and enforce max-level constants.
- Mode transitions through `ath5k_ani_init()` should reset state and apply expected defaults for off/manual-low/manual-high/auto.
- RX and MIB interrupt paths should compile against `ath5k_ani_phy_error_report()` and `ath5k_ani_mib_intr()` declarations across debug and non-debug builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath5k/ani.h -->
