# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wcn36xx/smd.h

## Purpose
`smd.h` is the public control-plane interface for the WCN36xx SMD/rpmsg HAL layer. It defines transport constants, common response/indication wrappers, firmware result values, and the exported functions used by the rest of the driver to command firmware.

## Important APIs, Types, and Functions
- `WCN36XX_NV_FRAGMENT_SIZE`, `WCN36XX_HAL_BUF_SIZE`, and `HAL_MSG_TIMEOUT` constrain NV transfer, shared HAL buffer size, and synchronous command wait time.
- `enum wcn36xx_fw_msg_result` documents success and known failure result codes returned in firmware responses.
- `struct wcn36xx_fw_msg_status_rsp` is the generic status body used by many HAL responses.
- `struct wcn36xx_hal_ind_msg` is the queued asynchronous indication container, using a flexible counted payload.
- Function prototypes expose the full SMD control surface: open/close, firmware start/stop/NV load, scan, STA/BSS lifecycle, keys, power, statistics, BA aggregation, offloads, host suspend/resume, beacon filter, multicast, testmode PTT, and rpmsg response dispatch.

## Control Flow
The header defines no executable control flow, but it establishes the driver layering: mac80211-facing code calls these exported functions, `smd.c` serializes them to firmware, and rpmsg calls `wcn36xx_smd_rsp_process()` for both command responses and asynchronous firmware events.

## State and Persistence Behavior
The API operates on `struct wcn36xx` plus per-VIF/per-STA mac80211 objects. Calls persist firmware-assigned BSS/STA indices, power/offload settings, firmware capabilities, and scan state in the private objects declared in `wcn36xx.h`.

## Dependencies and Integration Points
The header includes `wcn36xx.h` and references `rpmsg_device`, `ieee80211_vif`, `ieee80211_sta`, `cfg80211_scan_request`, `station_info`, and multiple HAL-specific structures. It is included by core driver files and testmode code.

## Risks and Test Signals
Because this is the driver ABI boundary, prototype or constant drift can break many call sites. Tests should build all WCN36xx configurations, exercise each mac80211 operation family, and verify that disabled optional paths, especially IPv6 and testmode, still compile cleanly.
