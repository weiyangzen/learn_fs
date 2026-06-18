# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/wmi-tlv.h

## Purpose

`wmi-tlv.h` is the ath10k firmware ABI header for the TLV-flavored WMI protocol used by `ATH10K_FW_WMI_OP_VERSION_TLV` firmware. It does not implement runtime logic itself; instead it defines command IDs, event IDs, TLV tags, service IDs, parameter IDs, packed wire structures, bit layouts, and a small amount of inline service-map translation that `wmi-tlv.c` uses to parse firmware events and generate host-to-firmware commands.

The header is a compatibility contract between the Linux ath10k driver and Qualcomm/Atheros firmware. Most definitions are little-endian packed layouts, so field order, tag values, enum ordinals, and advertised service bits are observable on the WMI transport and must remain firmware-compatible.

## Important APIs, Types, and Constants

- `WMI_TLV_CMD(grp_id)` and `WMI_TLV_EV(grp_id)` derive grouped command/event ID bases by shifting WMI TLV group IDs. `enum wmi_tlv_grp_id`, `enum wmi_tlv_cmd_id`, and `enum wmi_tlv_event_id` use these bases to define the command/event namespace for scan, pdev, vdev, peer, management, WOW, stats, TDLS, rfkill, mdns, SAP offload, and many other feature groups.
- `enum wmi_tlv_tag` is the central TLV schema registry. It covers generic array tags (`ARRAY_UINT32`, `ARRAY_BYTE`, `ARRAY_STRUCT`, `ARRAY_FIXED_STRUCT`) and hundreds of `STRUCT_*` tags for commands, events, substructures, and newer firmware capabilities. `WMI_TLV_TAG_MAX` sizes parser lookup tables in `wmi-tlv.c`.
- `struct wmi_tlv` is the common TLV envelope: 16-bit little-endian length, 16-bit little-endian tag, then flexible `value[]`. `wmi-tlv.c` walks these records with length validation and dispatches by tag.
- `enum wmi_tlv_service`, `WMI_TLV_MAX_SERVICE`, `WMI_TLV_MAX_EXT_SERVICE`, `wmi_tlv_svc_map()`, and `wmi_tlv_svc_map_ext()` translate TLV firmware service bits into ath10k's generic `WMI_SERVICE_*` bitmap. Services below 128 come from the service-ready bitmap; services at and above 128 are delivered through `WMI_TLV_SERVICE_AVAILABLE_EVENTID`.
- ABI/version and boot types include `struct wmi_tlv_abi_version`, `struct wmi_tlv_svc_rdy_ev`, `struct wmi_tlv_rdy_ev`, `struct wmi_tlv_resource_config`, `struct host_memory_chunk_tlv`, and `struct wmi_tlv_init_cmd`. These drive firmware startup, capability discovery, host memory chunk exchange, and ABI rejection on incompatible TLV firmware.
- Runtime command/event payload types include scan (`struct wmi_tlv_start_scan_cmd`, `struct wmi_tlv_scan_chan_list_cmd`), vdev/peer lifecycle (`struct wmi_tlv_vdev_start_cmd`, `struct wmi_tlv_peer_create_cmd`, `struct wmi_tlv_peer_assoc_cmd`), power management and WOW (`struct wmi_tlv_wow_enable_cmd`, `struct wmi_tlv_wow_add_pattern_cmd`), stats (`struct wmi_tlv_stats_ev`, `struct wmi_tlv_peer_stats_info`), diagnostics (`struct wmi_tlv_diag_data_ev`, `struct wmi_tlv_diag_item`), rfkill (`struct wmi_tlv_rfkill_state_change_ev`), and WMI management frame transmit-by-reference (`struct wmi_tlv_mgmt_tx_cmd`).
- Parameter/flag enums map higher-level ath10k settings into TLV firmware numeric IDs: `enum wmi_tlv_pdev_param`, `enum wmi_tlv_vdev_param`, `enum wmi_tlv_peer_param`, `enum wmi_tlv_peer_flags`, `enum wmi_tlv_tx_pause_id`, `enum wmi_tlv_tx_pause_action`, and rfkill config/radio-state values.
- Rate-code helpers `WMI_TLV_GET_HW_RC_PREAM_V1()`, `WMI_TLV_GET_HW_RC_NSS_V1()`, and `WMI_TLV_GET_HW_RC_RATE_V1()` decode the v1 firmware rate-code fields carried in peer stats and consumed by mac80211 station statistics.

The one exported function declaration, `ath10k_wmi_tlv_attach(struct ath10k *ar)`, is implemented in `wmi-tlv.c`. It binds TLV command maps, parameter maps, peer flag maps, and `struct wmi_ops` into `ar->wmi` when `wmi.c` selects the TLV op version.

## Control Flow and Integration

Attach-time selection starts in `ath10k_wmi_attach()` in `wmi.c`. When the firmware metadata reports `ATH10K_FW_WMI_OP_VERSION_TLV`, the driver calls `ath10k_wmi_tlv_attach()`, switches to the TLV cipher suite table, and uses TLV-specific command/event builders and parsers for the rest of the device lifetime.

Receive flow is implemented in `ath10k_wmi_tlv_op_rx()` in `wmi-tlv.c`. It strips the generic WMI command header, extracts a `WMI_TLV_*_EVENTID`, traces the payload, allows testmode to consume non-ready events, then dispatches the event to generic ath10k handlers or TLV-specific helpers. Those helpers parse `struct wmi_tlv` streams using the tags and packed structures declared here. Examples include service-ready parsing, management RX/TX completion parsing, beacon offload status, TX pause events, peer stats info, diagnostics, P2P NOA, TDLS teardown, rfkill state changes, and firmware temperature reports.

Transmit flow is the mirror image: `wmi-tlv.c` generator functions allocate SKBs and encode a sequence of TLV envelopes whose tags and payload structures come from this header. For example, init command generation emits `STRUCT_INIT_CMD`, `STRUCT_RESOURCE_CONFIG`, and an `ARRAY_STRUCT` of `host_memory_chunk_tlv` records; scan start emits a start-scan command plus channel, SSID, BSSID, and IE arrays; management transmit-by-reference uses `struct wmi_tlv_mgmt_tx_cmd` with DMA addresses; WOW/PNO and TDLS commands append nested TLV arrays described by comments in this header.

Service and capability flow is split across two firmware messages. `WMI_TLV_SERVICE_AVAILABLE_EVENTID` can carry extended service bits above `WMI_TLV_MAX_SERVICE`; `WMI_TLV_SERVICE_READY_EVENTID` carries the base service bitmap, regulatory capabilities, memory requests, system capability flags, and ABI version. `wmi_tlv_svc_map()` and `wmi_tlv_svc_map_ext()` collapse those into generic ath10k services used by mac, core, WOW, stats, and offload code.

## State and Persistence Behavior

This header stores no state by itself. It defines wire state that is persisted in driver-owned runtime structures after parsing:

- Service maps and extended service maps become bits in `ar->wmi.svc_map`, controlling feature availability for the active firmware session.
- `struct wmi_tlv_svc_rdy_ev` fields populate firmware version, RF chains, HT/VHT caps, regulatory bounds, memory request counts, and `ar->sys_cap_info`.
- `struct host_memory_chunk_tlv` records describe DMA memory chunks allocated by the host and later freed by `ath10k_wmi_free_host_mem()`.
- TX pause events update per-vdev queue pause bits through `ath10k_mac_handle_tx_pause_vdev()`.
- Peer stats info updates per-station cached rate-code and bitrate fields under `ar->data_lock`.
- Rfkill state changes update `ar->hw_rfkill_on`, firmware radio-enable parameters, and cfg80211 hardware rfkill state.

All persistent effects are therefore indirect and live in ath10k core/mac/WMI state, not in static data owned by the header.

## Dependencies

`wmi-tlv.h` depends on Linux kernel bit helpers (`<linux/bitops.h>`) and types/macros supplied by neighboring ath10k headers included before it in implementation units, especially `wmi.h`, `core.h`, `hw.h`, and mac80211/cfg80211-facing definitions. It uses kernel fixed-width little-endian types (`__le16`, `__le32`, `__le64`), packed layout annotations, DMA address types, `BIT()`, `GENMASK()`, and `FIELD_GET()`.

Important consumers are:

- `wmi-tlv.c`: primary implementation of TLV parsing, event dispatch, command generation, service mapping, parameter maps, command maps, and `ath10k_wmi_tlv_attach()`.
- `wmi.c`: WMI op-version selection, TLV cipher mapping, generic event handling, service-ready processing, host memory lifecycle, and firmware startup/shutdown orchestration.
- `mac.c` and `mac.h`: TX pause integration, rfkill configuration, rfkill radio enable/disable, rate-code decoding for station statistics, and TLV-specific comments around beacon-offload behavior.
- `testmode.c`: builds TLV byte-array messages for UTF/testmode paths.
- `wmi-ops.h`: generic operation surface that exposes TLV pull/generate methods to the rest of the driver.

## Risks and Edge Cases

- ABI drift is the dominant risk. Numeric command IDs, event IDs, tag IDs, service ordinals, and packed struct layouts must match firmware. Reordering enums or inserting fields into packed wire structs can silently break command/event decoding.
- TLV length handling is security-sensitive. `wmi-tlv.c` validates envelope lengths and minimum sizes for selected tags, but this header defines many tags and structs that are not all covered by parser policies. Any new parser must validate presence, envelope length, array length, and element count before dereferencing.
- Flexible arrays and nested TLV comments require exact size accounting. Several commands append arrays after fixed headers; generator bugs can produce malformed messages or under-sized SKBs.
- Endianness is explicit. All firmware fields are little-endian and must be converted at parse/build boundaries. Direct arithmetic on `__le32` fields is a common regression risk.
- Service-map semantics are split between base and extended events. New service bits at or above 128 must be mapped through `wmi_tlv_svc_map_ext()` using the extended bitmap layout, not only the base service-ready bitmap.
- The `WMI_TLV_EXT_SERVICE_IS_ENABLED()` macro relies on the provided `len` boundary. Passing the wrong bitmap length can test the wrong service word.
- Rate-code comments mention 11AX values even though ath10k is mainly 11ac-generation hardware. Consumers should treat those fields as firmware-provided encodings and validate ranges before mapping to mac80211 rates.
- Some TLV commands and params are defined by the header but deliberately marked unsupported in `wmi_tlv_cmd_map`, `wmi_tlv_pdev_param_map`, or `wmi_tlv_vdev_param_map`. A definition in this header is not sufficient evidence that the Linux driver path supports the feature.
- Management TX by reference uses DMA addresses and pending-ID cleanup. Structure size, `frame_len`/`buf_len`, and lifetime mismatches can leak DMA mappings or complete the wrong management frame.

## Test Signals

Useful validation signals for changes touching this header or its consumers:

- Build coverage for ath10k with TLV support enabled; compile errors often expose missing tag/struct names, incomplete maps, or type/layout mismatches.
- Firmware boot on TLV devices should reach service-ready and ready completion without `-EOPNOTSUPP`, `failed to parse tlv`, or service-ready timeout messages.
- WMI tracing/debug output should show expected TLV event IDs for scan, vdev start/stop, peer lifecycle, management RX/TX completions, and WOW/rfkill events when those paths are exercised.
- ABI compatibility checks in `ath10k_wmi_tlv_op_pull_svc_rdy_ev()` should log matching `WMI_TLV_ABI_VER*` values.
- Negative parser tests or fuzz-style malformed TLV injections should return `-EINVAL`/`-EPROTO` without out-of-bounds reads, especially for array tags and diagnostic data.
- Feature smoke tests should cover service-bit-dependent paths: beacon offload, scan offload, WOW patterns/PNO, peer stats info, TDLS events, rfkill if `WMI_TLV_SYS_CAP_INFO_RFKILL` is advertised, and management TX WMI if `WMI_SERVICE_MGMT_TX_WMI` is present.
- Runtime warnings to watch include unknown TX pause action/id, failed peer lookup during peer-stats parsing, malformed diagnostic data, invalid service-available parsing, and unsupported command/parameter IDs.
