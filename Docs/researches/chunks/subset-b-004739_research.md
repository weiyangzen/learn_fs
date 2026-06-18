# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/wmi.c lines 9186-10050

## Scope And Purpose

This chunk is a late section of the ath11k WMI command encoder. It covers the tail of firmware debug-log configuration, WMI endpoint attach/detach helpers, hardware data filtering, WoWLAN command construction, preferred network offload (PNO/NLO) configuration, ARP/IPv6 neighbor-solicitation offload, GTK rekey offload, BIOS SAR/GEO table commands, station keepalive, and a small helper that gates 6 GHz country-code extension handling.

The code is almost entirely host-to-firmware command serialization. Each public helper allocates an `sk_buff` with `ath11k_wmi_alloc_skb()`, writes one or more WMI TLV records with `FIELD_PREP(WMI_TLV_TAG, ...)` and `FIELD_PREP(WMI_TLV_LEN, ...)`, fills command-specific fields from `struct ath11k`, `struct ath11k_vif`, cfg80211/mac80211-derived arguments, or debugfs input, and sends the buffer with `ath11k_wmi_cmd_send()`. The functions do not process received packets and do not persist configuration to disk; they transfer current driver state into firmware-owned suspend, offload, regulatory, and diagnostic state.

## Important APIs, Types, And Constants

- `ath11k_wmi_fw_dbglog_cfg()` finishes in this range. It sends `WMI_DBGLOG_CFG_CMDID` for debugfs-selected firmware logging parameters and optionally copies `MAX_MODULE_ID_BITMAP_WORDS` from `ar->debug.module_id_bitmap`.
- `ath11k_wmi_connect()`, `ath11k_wmi_pdev_attach()`, `ath11k_wmi_attach()`, and `ath11k_wmi_detach()` wire `struct ath11k_base::wmi_ab` and per-PDEV `struct ath11k_pdev_wmi` handles to HTC WMI services and completions.
- WoWLAN helpers include `ath11k_wmi_hw_data_filter_cmd()`, `ath11k_wmi_wow_host_wakeup_ind()`, `ath11k_wmi_wow_enable()`, `ath11k_wmi_scan_prob_req_oui()`, `ath11k_wmi_wow_add_wakeup_event()`, `ath11k_wmi_wow_add_pattern()`, and `ath11k_wmi_wow_del_pattern()`.
- PNO/NLO command generation uses `struct wmi_pno_scan_req`, `struct wmi_network_type`, `struct wmi_wow_nlo_config_cmd`, and `struct nlo_configured_parameters`. The public entry point is `ath11k_wmi_wow_config_pno()`, which selects start or stop command generation and sends `WMI_NETWORK_LIST_OFFLOAD_CONFIG_CMDID`.
- Protocol offload uses `struct ath11k_arp_ns_offload` stored in `struct ath11k_vif`, plus firmware tuple types `struct wmi_ns_offload_tuple`, `struct wmi_arp_offload_tuple`, and `struct wmi_set_arp_ns_offload_cmd`. Host-side maximums are `ATH11K_IPV6_MAX_COUNT` and `ATH11K_IPV4_MAX_COUNT`; the base WMI command has `WMI_MAX_NS_OFFLOADS` and `WMI_MAX_ARP_OFFLOADS` slots, with an extension array for additional IPv6 NS entries.
- GTK offload uses `struct ath11k_rekey_data` from `arvif->rekey_data`, `struct wmi_gtk_rekey_offload_cmd`, and opcodes `GTK_OFFLOAD_ENABLE_OPCODE`, `GTK_OFFLOAD_DISABLE_OPCODE`, and `GTK_OFFLOAD_REQUEST_STATUS_OPCODE`.
- BIOS power-limit commands use `struct wmi_pdev_set_sar_table_cmd`, `struct wmi_pdev_set_geo_table_cmd`, `BIOS_SAR_TABLE_LEN`, `BIOS_SAR_RSVD1_LEN`, and `BIOS_SAR_RSVD2_LEN`.
- Keepalive uses `struct wmi_sta_keepalive_arg`, `struct wmi_sta_keepalive_cmd`, `struct wmi_sta_keepalive_arp_resp`, and `enum wmi_sta_keepalive_method`.
- `ath11k_wmi_supports_6ghz_cc_ext()` checks `WMI_TLV_SERVICE_REG_CC_EXT_EVENT_SUPPORT` in `ar->ab->wmi_ab.svc_map` and `ar->supports_6ghz`.

## Control Flow

The debug-log tail writes the fixed TLV array header for module bitmaps, switches on `dbglog->param`, and either sets only `cmd->value` or copies the caller-provided module bitmap into the TLV payload. For module-bitmap parameters it clears the input bitmap after copying so debugfs can accumulate multi-write bitmap state only until the final `is_end` write. Unsupported parameters free the newly allocated skb and return `-EINVAL`. Send failures are logged and also free the skb.

The WMI attach path is deliberately small. `ath11k_wmi_connect()` reads `ab->htc.wmi_ep_count`, rejects endpoint counts above `ab->hw_params.max_radios`, and connects each PDEV service with `ath11k_connect_pdev_htc_service()`. `ath11k_wmi_pdev_attach()` bounds-checks the PDEV ID, stores `&ab->wmi_ab` into the per-PDEV WMI handle, and refreshes `ab->wmi_ab.ab`. `ath11k_wmi_attach()` initializes PDEV 0, sets `preferred_hw_mode` to `WMI_HOST_HW_MODE_MAX` or single-PDEV mode for single-PDEV multi-RXDMA hardware, and initializes the `service_ready` and `unified_ready` completions. `ath11k_wmi_detach()` iterates all HTC WMI endpoints, calls the currently placeholder PDEV detach helper, and releases DBR ring capabilities through `ath11k_wmi_free_dbring_caps()`.

The WoWLAN control helpers follow a common one-command pattern. Hardware data filtering fills `WMI_TAG_HW_DATA_FILTER_CMD` and uses the caller bitmap when enabling; when disabling it sends all bits set so firmware clears all filter modes. Host wakeup and global WoW enable send fixed commands. Probe-request OUI extracts the first three bytes from a MAC address into a 24-bit OUI. Wakeup-event enable/disable encodes `1 << event` into the firmware event bitmap.

Pattern add is more complex because firmware expects several TLV arrays after `WMI_TAG_WOW_ADD_PATTERN_CMD`. The function allocates space for one bitmap pattern, empty IPv4 sync, empty IPv6 sync, empty magic-pattern, empty timeout array, and a one-word rate-limit interval array. It copies the pattern and mask into `struct wmi_wow_bitmap_pattern`, byte-swaps both rounded to a 4-byte boundary, then appends the required empty placeholders before sending `WMI_WOW_ADD_WAKE_PATTERN_CMDID`. Pattern delete sends only the fixed delete command with `WOW_BITMAP_PATTERN`.

PNO start builds `WMI_TAG_NLO_CONFIG_CMD` followed by an array of `nlo_configured_parameters` and an array of channel frequencies. It sets start and hidden-SSID flags, maps active/passive dwell to the max dwell values because the firmware path does not support min/max ranges, optionally enables passive scanning, and copies fast/slow scan periods, fast cycles, delay, and randomized probe-request MAC/mask. It then serializes each match SSID, optional RSSI threshold, and broadcast network type. Channel serialization uses `pno->a_networks[0].channel_count` and `pno->a_networks[0].channels[]` for the single firmware channel list. PNO stop emits only a fixed `WMI_NLO_CONFIG_STOP` command. The public wrapper returns `-ENOMEM` for NULL/error skb generation and otherwise sends the chosen command.

ARP/NS offload first calculates a command length containing the fixed command, a base NS tuple array of `WMI_MAX_NS_OFFLOADS`, an ARP tuple array of `WMI_MAX_ARP_OFFLOADS`, and, when needed, an extension NS tuple array for IPv6 addresses beyond the base firmware slots. `ath11k_wmi_fill_ns_offload()` emits either the base or extension array. When enabled, it marks entries below `offload->ipv6_count` valid, copies target IPv6 and solicited-node multicast IPv6 addresses, flags anycast addresses, copies the target MAC, and marks the MAC valid when nonzero. `ath11k_wmi_fill_arp_offload()` emits two ARP tuple slots and marks entries below `offload->ipv4_count` valid when enabled. Disable commands still send tuple TLVs but leave validity flags clear.

GTK rekey offload sends the same WMI command for enable, disable, and status request. Enable copies KCK, KEK, and a little-endian replay counter from `arvif->rekey_data`, then applies `ath11k_ce_byte_swap()` to the byte arrays before sending. Disable only sets the disable opcode. Status request sets the request-status opcode and is used before disabling so the resume path can retrieve updated replay counters from firmware events.

The BIOS SAR and GEO functions encode per-PDEV power-limit table commands. SAR allocates fixed command space plus two byte arrays: the 22-byte SAR table rounded to a 32-bit boundary and a 6-byte reserved array rounded to a 32-bit boundary. It copies only the SAR bytes from the caller and leaves the reserved array payload untouched apart from allocator initialization. GEO sends the fixed command plus an 18-byte reserved byte array rounded to 32-bit alignment. Both commands use `ar->pdev->pdev_id`.

Station keepalive allocates a fixed keepalive command followed immediately by an ARP-response TLV. It fills vdev, enable flag, interval, and method for all methods, and fills IPv4 source/destination plus destination MAC only for unsolicited ARP response or gratuitous ARP request methods. `ath11k_wmi_supports_6ghz_cc_ext()` has no send path; it is a pure predicate used by mac80211/regulatory code to decide whether 6 GHz country-code extension behavior is available.

## State And Persistence Behavior

The main persistent host state touched in this chunk is in `struct ath11k_base::wmi_ab`, per-PDEV WMI handles, `struct ath11k_vif`, and debugfs state. Attach initializes `wmi_ab.ab`, per-PDEV `wmi_handle->wmi_ab`, `preferred_hw_mode`, and WMI readiness completions. Detach releases DBR ring capability storage but leaves most PDEV/SOC WMI cleanup as TODO placeholders.

Firmware debug-log configuration consumes `ar->debug.module_id_bitmap` by copying it into the command and clearing it for bitmap-style parameters. This is observable by debugfs users because multiple debugfs writes can populate bitmap words before the final send, but the buffer is reset after the WMI command is generated.

WoWLAN, PNO, ARP/NS offload, GTK offload, hardware filters, and keepalive all persist primarily inside firmware after `ath11k_wmi_cmd_send()` succeeds. Host-side source state remains in existing structures: `arvif->arp_ns_offload` is populated by mac80211 IPv6 address callbacks, `arvif->rekey_data` is populated by key/offload setup, and PNO requests are built transiently from cfg80211 scheduled-scan/WoWLAN requests in `wow.c`. The WMI helpers themselves do not cache success state, so callers track higher-level state such as `ar->nlo_enabled` and `arvif->rekey_data.enable_offload`.

The skb payloads are temporary command buffers. On success, ownership transfers to `ath11k_wmi_cmd_send()`; on explicit pre-send validation failures or send failures where this function sees an error, the local helper frees the skb only in paths that are written to do so. Most one-line wrappers return the send result directly and rely on the common WMI send path's ownership behavior.

## Dependencies And Integration Points

This code depends on the ath11k WMI TLV ABI defined in `wmi.h`: tags, command IDs, fixed command structs, tuple structs, and service bits must match firmware expectations exactly. It also depends on the common command allocator/sender, CE byte-swapping helper, Linux skb allocation semantics, and bitfield helpers.

The debug-log helper is called from `debugfs.c` under `ar->conf_mutex` after parsing user input from the firmware debug-log debugfs file. The bitmap clearing behavior is paired with that parser's `is_end` protocol.

The WoWLAN helpers are called from `wow.c` during suspend/resume preparation. `ath11k_vif_wow_set_wakeups()` uses wakeup-event and pattern helpers, configures NLO through `ath11k_wmi_wow_config_pno()`, and sets hardware filters through `ath11k_wmi_hw_data_filter_cmd()`. Resume cleanup disables NLO, clears hardware filters, may request GTK rekey status, disables GTK offload, and notifies firmware that the host is awake.

ARP/NS offload input is populated by mac80211 operations in `mac.c`, notably IPv6 address change handling for solicited-node multicast addresses and ARP/IPv4 state tracking. `wow.c` applies the offload only to STA vdevs during protocol-offload setup.

GTK offload is part of the WoWLAN suspend/resume path. Firmware status events are handled elsewhere in WMI event parsing, but this chunk provides the commands that enable, disable, and request state.

Station keepalive is called from `ath11k_mac_vif_set_keepalive()` for STA vdevs only when firmware advertises `WMI_TLV_SERVICE_STA_KEEP_ALIVE`. That mac80211-side wrapper supplies null-frame keepalive by default, while this WMI helper also supports ARP-style payload fields for methods that need them.

The 6 GHz predicate is used from several mac80211/regulatory paths: station TPC support checks, interface-add regulatory rule handling, and STA authorization/regulatory power-type handling. It combines firmware service discovery with per-radio 6 GHz support so callers do not enable country-code extension behavior on non-6 GHz radios or firmware lacking the event service.

The source path is under `sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/`, a copied Linux wireless driver subtree inside this repository. There is no direct Ceph filesystem logic in this chunk; its integration surface is Linux wireless firmware control.

## Risks And Edge Cases

The most important local risk is TLV size and pointer arithmetic drift. Pattern add, PNO start, and ARP/NS offload manually compute lengths and then advance raw pointers through packed firmware records. Any future change to the serialized structures, tuple counts, or placeholder arrays must update both the length expression and write sequence together, or the command can be truncated, overrun, or rejected by firmware.

Caller-side validation is assumed for several inputs. `ath11k_wmi_wow_add_pattern()` copies `pattern_len` bytes into fixed firmware buffers and byte-swaps `roundup(pattern_len, 4)` bytes; `wow.c` bounds-checks patterns against `WOW_MAX_PATTERN_SIZE` before calling, so direct new callers would need equivalent validation. PNO start trusts `uc_networks_count`, SSID lengths, and channel counts; current conversion in `wow.c` bounds these against WMI maximums. ARP/NS offload trusts `offload->ipv6_count` and `offload->ipv4_count`; host structures have fixed array sizes, so producers must cap counts.

The PNO channel-list model uses only `a_networks[0].channel_count` and `a_networks[0].channels[]` even though each network entry has its own channel array. This matches the conversion helper, which copies the same cfg80211 channel list into every network, but it is a coupling worth preserving if PNO conversion changes.

There are several byte-order and byte-swap subtleties. PNO randomized MAC/mask, SSID bytes, WoW patterns/masks, NS IPv6 addresses, target MACs, ARP IPv4 addresses, GTK keys, and replay counters are run through `ath11k_ce_byte_swap()` because firmware/CE expects 32-bit word-swapped payloads. Incorrectly adding or removing byte swaps can produce failures that look like firmware ignoring otherwise well-formed commands.

`ath11k_wmi_wow_add_wakeup_event()` uses `1 << event`; this assumes the enum value is within the width of the integer bitmap. Current callers iterate `WOW_EVENT_MAX`, but new events above bit 31 would require a wider bitmap or different command layout.

The debug-log module bitmap is cleared immediately after command serialization, before command success is known. If `ath11k_wmi_cmd_send()` fails, the accumulated bitmap is lost and must be supplied again through debugfs.

`ath11k_wmi_connect()` returns `-1` rather than a conventional errno for too many WMI endpoints. Callers that expect Linux errno values may log or handle this less clearly than `-EINVAL`.

The attach/detach helpers still contain TODOs for PDEV- and SOC-specific resource initialization/cleanup. At present that is safe only because this chunk initializes very little per-PDEV WMI state. Any future allocation added to attach must have a matching detach/unwind path.

The SAR/GEO reserved byte-array payloads are not explicitly filled. This is probably acceptable if `ath11k_wmi_alloc_skb()` zeroes command buffers, but it is an implicit dependency. A different allocator behavior would leak stack/heap contents to firmware or create nondeterministic command contents.

Most direct-send helpers do not free the skb on send failure in the local function. This is consistent with the common ath11k WMI send ownership model in much of the file, but functions with custom failure handling, such as the debug-log tail, make ownership easy to get wrong when copying patterns into new helpers.

## Test Signals

Useful test and review signals for this chunk include:

- Debugfs firmware logging tests for each accepted `WMI_DEBUG_LOG_PARAM_*` value, including multi-word module bitmap writes where non-final writes do not send WMI and final writes send the bitmap then clear `ar->debug.module_id_bitmap`.
- WMI attach/connect tests or boot logs on single-radio and multi-radio hardware verifying endpoint count bounds, PDEV WMI handle setup, `service_ready`/`unified_ready` completions, and `preferred_hw_mode` for single-PDEV multi-RXDMA targets.
- WoWLAN suspend tests covering magic packet, disconnect wake, AP/IBSS wake events, pattern wake, host wakeup indication on resume, and hardware data filter enable/disable. Firmware traces should show the expected command IDs and event bitmaps.
- Pattern offload tests for zero, maximum, and rejected-over-maximum pattern lengths, plus native Wi-Fi decap conversion paths in `wow.c`, checking that pattern and mask matching still works after CE byte-swapping.
- PNO/NLO tests using one and two scan plans, hidden SSIDs, passive scans, randomized MAC requests, RSSI thresholds, maximum SSID count, and maximum channel count. Resume cleanup should send `WMI_NLO_CONFIG_STOP` only when `ar->nlo_enabled` was set.
- ARP/NS protocol-offload tests with zero, one, two, and more-than-two IPv6 addresses to exercise both base and extension NS tuple arrays, plus up to two IPv4 ARP targets. Disable should send tuples with validity flags cleared.
- GTK rekey offload tests around suspend/resume should verify enable command payloads, request-status-before-disable ordering, replay counter update from firmware status events, and correct behavior when `arvif->rekey_data.enable_offload` is false.
- BIOS SAR/GEO tests on platforms with ACPI/BIOS SAR inputs should verify pdev ID, table lengths, alignment, and firmware acceptance of `WMI_PDEV_SET_BIOS_SAR_TABLE_CMDID` and `WMI_PDEV_SET_BIOS_GEO_TABLE_CMDID`.
- STA keepalive tests should verify service-bit gating in `mac.c`, null-frame keepalive command generation, and ARP/gratuitous-ARP payload fields if those methods are enabled by a caller.
- 6 GHz regulatory tests should compare behavior with and without `WMI_TLV_SERVICE_REG_CC_EXT_EVENT_SUPPORT` and with radios that do or do not set `ar->supports_6ghz`, especially station TPC, interface-add regulatory updates, and STA authorization on 6 GHz channels.

For the research pipeline, the artifact signal is that this source-tree-aligned chunk document exists at `Docs/researches/chunks/subset-b-004739_research.md` and covers only `wmi.c` lines 9186-10050. The final per-file synthesis should merge this with adjacent `ath11k/wmi.c` chunks that cover earlier command definitions, shared allocation/send helpers, and later WMI event parsing.
