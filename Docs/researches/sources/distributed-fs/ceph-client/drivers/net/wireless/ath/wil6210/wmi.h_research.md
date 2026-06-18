# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wil6210/wmi.h

## Purpose
`wmi.h` is the generated protocol contract for the `wil6210` Wireless Module Interface. It defines all host-to-firmware command IDs, firmware-to-host event IDs, capability bits, fixed constants, command payload structures, event payload structures, packed wire formats, flexible-array payload conventions, status enums, and feature-specific configuration records used by the `wil6210` driver and firmware.

The header is not an implementation file; it is an ABI surface between host driver and firmware. Correct field layout, byte order, alignment, and enum values are essential for every WMI exchange in `wmi.c`, cfg80211 glue, Tx/Rx setup, debugfs, PMC, RF sector control, FTM/AOA, radar, power management, and link statistics.

## Important APIs, Types, and Data
- Top-level constants:
  - `WMI_MAC_LEN`, `WMI_MAX_SSID_LEN`, `WMI_MAX_IE_LEN`, `WMI_INVALID_TEMPERATURE`, `WMI_MAX_XIF_PORTS_NUM`, `WMI_QOS_*`, RF table lengths, scheduling limits, and firmware payload maxima.
  - `enum wmi_mid` defines default, debug, and broadcast MID addressing.
  - `enum wmi_fw_capability` maps firmware feature bits consumed by the driver.
- Common command header:
  - `struct wmi_cmd_hdr` contains MID, command/event ID, and firmware timestamp. It follows the mailbox header in every WMI message.
- Command namespace:
  - `enum wmi_command_id` assigns stable numeric IDs for connection, scan, security, management frame Tx, ring setup, BA control, RF/beamforming, power management, P2P, AP/PCP, FTM/AOA, RF sectors, EDMA ring setup, QoS, link stats, RBUFCAP, temperature, and vendor/internal commands.
- Event namespace:
  - `enum wmi_event_id` assigns stable numeric IDs for firmware ready, connect/disconnect, scan completion, management Rx/Tx, BA status, ring config completion, P2P/PCP/port events, suspend/resume, FTM/AOA, RF sectors, EDMA completion, link stats, CQM link monitor, command-not-supported, and internal firmware events.
- Core connection and scan structs:
  - `struct wmi_connect_cmd`, `struct wmi_disconnect_sta_cmd`, `struct wmi_connect_event`, `struct wmi_disconnect_event`.
  - `struct wmi_start_scan_cmd` with counted channel list, `struct wmi_start_sched_scan_cmd`, `struct wmi_sched_scan_result_event`, and PNO result structs.
  - `struct wmi_probed_ssid_cmd` and `struct wmi_set_appie_cmd`.
- Security structs:
  - `struct wmi_add_cipher_key_cmd`, `struct wmi_delete_cipher_key_cmd`, `enum wmi_key_usage`, and passphrase/key constants.
  - FT roaming structs `wmi_ft_auth_cmd`, `wmi_ft_reassoc_cmd`, `wmi_update_ft_ies_cmd`, `wmi_ft_auth_status_event`, and `wmi_ft_reassoc_status_event`.
- AP/P2P/port/power structs:
  - `struct wmi_bcon_ctrl_cmd`, `struct wmi_pcp_start_cmd`, `struct wmi_p2p_cfg_cmd`, `struct wmi_port_allocate_cmd`, `struct wmi_port_delete_cmd`.
  - `struct wmi_traffic_suspend_cmd`, `struct wmi_traffic_suspend_event`, `struct wmi_traffic_resume_event`, PS profile enums and structs.
- Ring and data-path structs:
  - Legacy ring structs `wmi_sw_ring_cfg`, `wmi_vring_cfg`, `wmi_vring_cfg_cmd`, `wmi_bcast_vring_cfg_cmd`, `wmi_cfg_rx_chain_cmd`.
  - EDMA structs `wmi_edma_ring_cfg`, `wmi_tx_status_ring_add_cmd`, `wmi_rx_status_ring_add_cmd`, `wmi_tx_desc_ring_add_cmd`, `wmi_rx_desc_ring_add_cmd`, `wmi_bcast_desc_ring_add_cmd`, and their completion events.
  - BA structs `wmi_ring_ba_en_cmd`, `wmi_ring_ba_dis_cmd`, `wmi_rcp_addba_resp_cmd`, `wmi_rcp_addba_resp_edma_cmd`, `wmi_rcp_delba_cmd`, `wmi_rcp_addba_req_event`, and `wmi_delba_event`.
- Management/telemetry structs:
  - `struct wmi_sw_tx_req_cmd`, `struct wmi_sw_tx_req_ext_cmd`, `struct wmi_rx_mgmt_info`, `struct wmi_rx_mgmt_packet_event`, and `struct wmi_tx_mgmt_packet_event`.
  - Temperature, LED, RSSI/link monitor, link stats, notify, RF status, firmware version, baseband type, and RBUFCAP structs.
- Advanced feature structs:
  - RF sector read/write/select/on commands and events.
  - FTM/TOF/AOA commands and events with variable destination/result arrays.
  - Radar configuration and PCI buffer control structs.
  - Rate search, beamforming, scheduling scheme, long range, QoS priority, internal firmware ioctl/event, and CCA indication structs.

## Control Flow
This header has no executable control flow. It describes the message formats used by executable control flow in `wmi.c` and other driver files. A typical flow is:

1. Driver code selects a `WMI_*_CMDID`, fills the matching packed command struct, converts multi-byte scalar fields to little endian, and sends it through `wmi_send()` or `wmi_call()`.
2. Firmware replies with a `WMI_*_EVENTID` and matching packed event struct.
3. `wmi.c` validates length, MID, status fields, and feature-specific payloads before mutating driver/cfg80211 state.

Flexible array members and counted arrays are common. Consumers must use `sizeof(base) + dynamic_len`, `offsetof(..., payload)`, `__struct_size()`, or `DEFINE_FLEX()` style helpers so that variable payloads are neither truncated nor overrun.

## State and Persistence
The header owns no runtime state. Its structs represent transient messages copied through mailbox buffers or DMA-visible firmware memory. Any lasting state is held by firmware or by driver structures populated from events, such as firmware capabilities, connection state, ring tail pointers, link statistics, RF sector data, and temperature readings.

The enum values and struct layouts are persistent ABI in the sense that firmware and host must agree across builds. The file comment identifies it as automatically generated, so manual changes are risky unless the generator and firmware contract are updated together.

## Dependencies and Integration Points
- Included by `wmi.c` and many `wil6210` subsystem files that build WMI payloads directly, including cfg80211, Tx/Rx, debugfs, PMC, main/netdev, interrupt, and PM code.
- Relies on Linux fixed-width and endian types such as `u8`, `s8`, `__le16`, `__le32`, and `__le64`.
- All command/event structs are `__packed`, making them wire-format definitions rather than normal in-memory kernel structs.
- Uses modern flexible-array annotations in several places, including `__counted_by`, `DECLARE_FLEX_ARRAY`, and open-ended arrays.
- Numeric IDs are used by `cmdid2name()` and `eventid2name()` in `wmi.c`, tracepoints, debugfs WMI injection, and firmware event dispatch.

## Risks and Edge Cases
- ABI drift is the largest risk. Reordering enum values, changing struct packing, changing field widths, or moving flexible arrays breaks firmware interoperability without necessarily causing compile errors.
- Multi-byte fields must be endian-converted at every use. The header marks fields as little-endian but cannot enforce conversions in callers.
- Several comments note deprecated commands/events. They remain in the ABI for compatibility and should not be reused casually.
- Some fields use sentinel values such as `MID_BROADCAST`, `CIDXTID_EXTENDED_CID_TID`, `WMI_INVALID_TEMPERATURE`, `WMI_LINK_MAINTAIN_CFG_CID_BROADCAST`, and `WMI_INVALID_RF_SECTOR_INDEX`; callers must preserve their special semantics.
- Compatibility values such as `WMI_NUM_MCS` remain for old fixed-size arrays while newer commands prefer dynamic arrays. Mixing old and new rate-search formats can cause sizing mistakes.
- Counted variable payloads must be bounded by firmware maxima such as `WMI_MAX_IOCTL_PAYLOAD_SIZE`, `WMI_MAX_INTERNAL_EVENT_PAYLOAD_SIZE`, `WMI_MAX_IE_LEN`, and feature-specific max counts.
- Some arrays and sizes are coupled by comments rather than code, for example RF DTYPE/ETYPE/RX2TX configuration lengths. Generated output must keep these synchronized.
- `wmi_delete_cipher_key_cmd` does not encode key usage even though `wmi_del_cipher_key()` accepts it; driver/firmware behavior depends on command semantics outside this struct.

## Test Signals
- Compile tests should catch missing struct names, enum names, and flexible-array annotations used by the rest of the driver.
- ABI-oriented tests should verify `sizeof()` and `offsetof()` for command/event structs that have firmware-visible layouts, especially mailbox header adjacency, EDMA ring commands, connect/scan events, and variable payload bases.
- Runtime tests should exercise representative command/event pairs: echo, ready, connect/disconnect, scan complete, management Tx/Rx, ring config done, BA request/response, suspend/resume, link monitor, link stats, and temperature.
- Fuzz or fault-injection tests should feed short, oversized, inconsistent, and unsupported event payloads to ensure `wmi.c` length checks match this header.
- Cross-version firmware tests are important whenever generated WMI definitions change, particularly around capability-gated features and command-not-supported handling.
