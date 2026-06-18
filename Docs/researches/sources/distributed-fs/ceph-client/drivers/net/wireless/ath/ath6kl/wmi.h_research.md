# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath6kl/wmi.h

## Purpose

This header defines the ath6kl WMI ABI shared by the host driver and firmware-facing code. It contains protocol versions, command and event IDs, packed command/event payload structures, bitfield helpers for WMI data and command headers, rate/security/scan/power/QoS/P2P/AP-mode enums, and function prototypes implemented by `wmi.c`.

## Important APIs, types, and constants

- `struct wmi` is the host control-plane state object. It stores the parent device, control endpoint, power mode, WMM/pstream bitmaps, signal-quality thresholds, probe/WMM flags, and pending management TX frame copy.
- `struct wmi_data_hdr` and helpers such as `wmi_data_hdr_get_up()`, `wmi_data_hdr_get_dot11()`, `wmi_data_hdr_get_seqno()`, `wmi_data_hdr_get_meta()`, and `wmi_data_hdr_get_if_idx()` describe the data-path header that carries message type, user priority, metadata version, A-MSDU, and vif index.
- `struct wmi_cmd_hdr` plus `wmi_cmd_hdr_get_if_idx()` define the control message prefix used by `ath6kl_wmi_cmd_send()` and `ath6kl_wmi_control_rx()`.
- `enum wmi_cmd_id` and `enum wmi_event_id` enumerate a large firmware ABI, including base connection/scan/security commands, developer commands, AP/P2P/WOW/DFS/coexistence extensions, scheduled scan, and TXE notify.
- Packed payloads cover connect/reconnect, key install/delete, PMKID, scan, BSS filter, power parameters, pstreams, RSSI/SNR thresholds, target stats, roam tables, CAC, AP mode, remain-on-channel, management TX, P2P info, WMIX extension commands, and WOW filters.
- Exported prototypes expose the command builders, receive dispatcher, packet conversion helpers, rate lookup, WMI lifecycle, and vif lookup.

## Control flow encoded by the ABI

The header separates host-to-firmware commands from firmware-to-host events. Host commands are packed into `struct wmi_cmd_hdr` plus one command-specific payload and sent by `wmi.c`. Firmware events return the same header form with an event ID and a payload from the event section. Data packets use `struct wmi_data_hdr`, while out-of-band WMIX messages are nested under `WMI_EXTENSION_CMDID` or `WMI_EXTENSION_EVENTID` with `struct wmix_cmd_hdr`.

## State and persistence behavior

No persistent storage is defined. All structures are transient kernel/firmware ABI records. Because most payloads are `__packed` and include explicit endian types, the persistent contract is binary layout compatibility with firmware rather than local disk state. `struct wmi` fields are runtime state initialized in `ath6kl_wmi_init()` and reset by `ath6kl_wmi_reset()`.

## Dependencies and integration points

The header depends on Linux IEEE 802.11 definitions, HTC endpoint IDs, cfg80211/nl80211 enums visible through included headers, ath6kl crypto and HT capability types from core headers, and firmware WMI version compatibility. It is included by WMI implementation and other ath6kl modules that need command prototypes or protocol constants.

## Risks

The primary risk is ABI drift: command IDs, event IDs, enum numeric values, field ordering, packing, flexible arrays, and endian annotations must match firmware. Several comments warn that changing AP-mode constants requires rebuilding firmware and driver. Duplicate-looking prototypes and long enum ranges raise maintenance risk. `P2P_FLAG_HMODEL_REQ` shares the same value as `P2P_FLAG_MACADDR_REQ`, which may be intentional firmware behavior or a bug-prone overlap. Flexible-array payloads require callers to allocate with the exact payload length.

## Test signals

Compile-time signals include sparse/endian warnings, packed-structure layout assumptions, and all callers building against prototypes. Runtime signals include successful WMI ready/version negotiation, correct command/event dispatch IDs in debug logs, successful scan/connect/security/AP/P2P/WOW operations, and negative handling of invalid payload lengths for flexible event structures.
