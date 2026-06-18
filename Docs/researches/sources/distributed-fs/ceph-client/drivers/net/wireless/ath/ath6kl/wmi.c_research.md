# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath6kl/wmi.c

## Purpose

This file implements the ath6kl host-side Wireless Module Interface control plane. It translates cfg80211/mac80211 driver actions into WMI command sk_buffs for firmware, parses WMI events returned by firmware, and maintains the small amount of host state needed to sequence commands, QoS streams, power management, management TX status, scan results, and virtual-interface event routing.

## Important APIs, types, and functions

- `ath6kl_wmi_cmd_send()` is the common command transport wrapper. It validates the interface index, optionally creates sync points, pushes `struct wmi_cmd_hdr`, handles `WMI_OPT_TX_FRAME_CMDID` as data-path traffic on the BE endpoint, and sends through `ath6kl_control_tx()`.
- `ath6kl_wmi_control_rx()` and `ath6kl_wmi_proc_events()` are the central receive path for firmware control packets. They parse `struct wmi_cmd_hdr`, trace/debug the raw event, dispatch global events directly, and route interface-specific events through `ath6kl_wmi_proc_events_vif()`.
- Packet format helpers include `ath6kl_wmi_dix_2_dot3()`, `ath6kl_wmi_dot3_2_dix()`, `ath6kl_wmi_dot11_hdr_remove()`, and `ath6kl_wmi_data_hdr_add()`. They prepend or remove WMI, LLC/SNAP, Ethernet, and 802.11 framing.
- Connection, roaming, scan, and security command builders include `ath6kl_wmi_connect_cmd()`, `ath6kl_wmi_reconnect_cmd()`, `ath6kl_wmi_disconnect_cmd()`, `ath6kl_wmi_beginscan_cmd()`, `ath6kl_wmi_scanparams_cmd()`, `ath6kl_wmi_addkey_cmd()`, `ath6kl_wmi_deletekey_cmd()`, and `ath6kl_wmi_setpmkid_cmd()`.
- QoS and stream management flows through `ath6kl_wmi_implicit_create_pstream()`, `ath6kl_wmi_create_pstream_cmd()`, `ath6kl_wmi_delete_pstream_cmd()`, `ath6kl_wmi_pstream_timeout_event_rx()`, and `ath6kl_wmi_sync_point()`.
- P2P/cfg80211 management operations are handled by remain-on-channel, action/mgmt TX, probe-response, probe-request-report, and P2P-info command/event helpers.
- Lifecycle APIs are `ath6kl_wmi_init()`, `ath6kl_wmi_reset()`, and `ath6kl_wmi_shutdown()`.

## Control flow

Outbound commands allocate a zeroed payload with `ath6kl_wmi_get_new_buf()`, fill packed WMI structures with little-endian conversions, then call `ath6kl_wmi_cmd_send()`. Commands with ordering requirements request a sync before or after the command. Sync builds a control `WMI_SYNCHRONIZE_CMDID` bitmap for active AC endpoints and sends empty `SYNC_MSGTYPE` data packets on each active data endpoint.

Inbound firmware events arrive as sk_buffs on the WMI control endpoint. `ath6kl_wmi_control_rx()` rejects undersized packets, emits a trace event, and hands ownership to `ath6kl_wmi_proc_events()`, which frees the skb after dispatch. Global replies/events such as ready, bitrate, regdomain, pstream timeout, RSSI/SNR threshold, WMIX extension events, testmode, and PMKID list are handled immediately. Unknown global IDs are attempted as vif-specific events by looking up `fw_vif_idx`; vif events then call cfg80211/mac80211-facing ath6kl callbacks such as connect, disconnect, scan-complete, BSS inform, MIC failure, CAC, PS-Poll, DTIM expiry, ADDBA/DELBA, ROC, TX status, RX probe request/action, and TX-error notification.

## State and persistence behavior

The state is in-memory only inside `struct wmi`. `fat_pipe_exist` and `stream_exist_for_ac[]` track active QoS pstreams and are protected by `wmi->lock`. `pwr_mode`, `saved_pwr_mode`, `is_wmm_enabled`, `traffic_class`, and `is_probe_ssid` reflect current host/firmware operating state. `last_mgmt_tx_frame` holds a copied management frame until a matching TX status event reports it to cfg80211, then it is freed. Reset clears pstream state; shutdown frees the pending management frame and the `wmi` object. No durable on-disk state exists.

## Dependencies and integration points

This file depends on ath6kl core callbacks, HTC endpoint routing, cfg80211 notification APIs, kernel sk_buff helpers, regulatory-domain tables from `../regd*.h`, aggregation callbacks, debug/testmode/recovery hooks, and firmware capability bits. It is the boundary between Linux network configuration and ath6kl firmware WMI ABI, so field layout, endianness, flexible-array sizing, and command IDs must match `wmi.h` and target firmware.

## Risks

Risk centers on malformed firmware lengths, flexible array bounds, interface-index routing, skb headroom, and lifetime of asynchronous management TX state. Many handlers check minimum struct sizes, but variable-length structures require exact `struct_size()` and pointer-bound checks. QoS pstream state has comments noting questionable lock granularity and a stale workaround around `traffic_class == 100`. `ath6kl_get_vif_by_index()` has a FIXME about locking, making vif lifetime assumptions important. Firmware command errors are logged as programming errors but not recovered locally.

## Test signals

Useful validation signals include WMI trace/debug dumps, connect/disconnect/scan success through cfg80211, BSS table updates from beacon/probe events, remain-on-channel readiness and expiry callbacks, management TX status completion, TXE CQM notification, scheduled-scan timer behavior, pstream activity indications per AC, suspend/WOW transitions, and negative tests for invalid channel lists, key lengths, multicast filters, PMKID payload lengths, unsupported wait-on-mgmt-TX, invalid vif indices, and truncated event payloads.
