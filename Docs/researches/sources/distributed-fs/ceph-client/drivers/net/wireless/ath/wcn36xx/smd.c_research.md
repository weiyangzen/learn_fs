# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wcn36xx/smd.c

## Purpose
`smd.c` is the Qualcomm WCN36xx firmware control-plane transport implementation. It builds HAL request messages in `wcn->hal_buf`, sends them over the rpmsg/SMD endpoint, waits for matching firmware responses, and translates mac80211/cfg80211 operations into firmware commands for startup, NV download, scanning, station/BSS setup, keys, power management, BA aggregation, WoWLAN offloads, beacon filtering, and firmware indications.

## Important APIs, Types, and Functions
- `wcn36xx_smd_send_and_wait()` is the central synchronous RPC primitive. It initializes `hal_rsp_compl`, sends `wcn->hal_buf` through `rpmsg_send()`, waits up to `HAL_MSG_TIMEOUT`, and leaves the response copied back into `wcn->hal_buf`.
- `INIT_HAL_MSG*`, `PREPARE_HAL_BUF`, and `PREPARE_HAL_PTT_MSG_BUF` standardize HAL header setup and padding into the shared buffer.
- Startup/configuration APIs include `wcn36xx_smd_load_nv()`, `wcn36xx_smd_start()`, `wcn36xx_smd_stop()`, `wcn36xx_smd_feature_caps_exchange()`, and `wcn36xx_smd_update_cfg()`.
- Connection APIs include `wcn36xx_smd_add_sta_self()`, `wcn36xx_smd_join()`, `wcn36xx_smd_set_link_st()`, `wcn36xx_smd_config_sta()`, `wcn36xx_smd_config_bss()`, and delete variants.
- Runtime APIs cover software/hardware scan, channel list updates, channel switch, beacon/probe-response templates, unicast/group key programming, BMPS/IMPS power states, keepalive, ARP/IPv6 NS/GTK offloads, multicast filter setup, and beacon filter programming.
- `wcn36xx_smd_rsp_process()` is the rpmsg callback. Synchronous responses are copied to `hal_buf` and complete the waiter; asynchronous indications are copied into `struct wcn36xx_hal_ind_msg` and queued to `wcn36xx_ind_smd_work()`.

## Control Flow
Most exported operations lock `wcn->hal_mutex`, initialize a stack or allocated HAL message, fill firmware-specific fields from mac80211 state, copy into `hal_buf`, call `wcn36xx_smd_send_and_wait()`, and validate the firmware response with either `wcn36xx_smd_rsp_status_check()` or a command-specific parser. Firmware version and RF ID decide whether v0 or v1 STA/BSS structures are used, with WCN3680 enabling VHT and extra config values.

The response path is split. Expected command responses arrive through `wcn36xx_smd_rsp_process()`, overwrite the same shared buffer, set `hal_rsp_len`, and complete the blocked sender. Indications such as TX completion, scan offload events, missed beacon, station context deletion, and register info are copied under `hal_ind_lock` to a list and processed later on `hal_ind_wq`, where they call mac80211 notifications such as `ieee80211_scan_completed()`, `ieee80211_beacon_loss()`, `ieee80211_connection_loss()`, and DXE TX ACK handling.

## State and Persistence Behavior
The file mutates long-lived driver state: firmware version strings and API numbers, `fw_feat_caps`, scan flags and scan request pointer, VIF BSS/self station indices, STA firmware indices and DPU descriptors, GTK replay counter, SMD indication queue, and firmware-backed power/offload state. The NV image is requested from firmware storage through `request_firmware()` and fragmented in 3072-byte chunks; it persists in `wcn->nv` until released by wider driver teardown.

## Dependencies and Integration Points
This file depends on Linux rpmsg, firmware loading, mac80211/cfg80211 structures, Qualcomm HAL definitions in `hal.h`, firmware capability helpers in `firmware.h`, and DXE TX ACK callbacks. It is used by the WCN36xx mac80211 operations layer for control operations and by `testmode.c` for production test passthrough.

## Risks and Test Signals
Key risks are HAL ABI drift, buffer length mistakes in variable-length messages, firmware-version-specific structure sizing, race mistakes around the shared `hal_buf`, and stale firmware state if response parsing fails after the firmware partially applied a command. Test signals include successful firmware start/version logging, NV download completion, scan completion/abort behavior, association and AP bring-up, key install/remove, suspend/resume offloads, beacon-loss handling, and lack of HAL timeout or "response failed" logs under traffic and scan stress.
