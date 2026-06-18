# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/qmi.h

## Purpose

`qmi.h` declares ath10k's SNOC/WCN3990 WLFW QMI client state, configuration structures, event types, and exported control APIs. It is the contract between SNOC bus code, ath10k core, and `qmi.c`.

## Important APIs, Types, and Functions

- `enum ath10k_qmi_driver_event_type` covers server arrival/exit, FW ready/down, MSA ready, and max sentinel.
- `enum ath10k_qmi_state` distinguishes initialized from deinitializing/deinitialized state.
- `struct ath10k_msa_mem_info` records physical address, size, and secure flag for an MSA region.
- Chip/board/SoC structs store firmware-provided IDs.
- `struct ath10k_qmi_cal_data` tracks calibration ID, total size, and data pointer.
- CE config structs describe target pipe, service pipe, and shadow register data sent to firmware.
- `struct ath10k_qmi_wlan_enable_cfg` bundles CE config arrays and counts.
- `struct ath10k_qmi` holds the QMI handle, QRTR endpoint, event workqueue/list/lock, MSA region state, firmware identity strings, calibration data, platform flags, readiness flag, and lifecycle state.
- Exported APIs are `ath10k_qmi_wlan_enable()`, `ath10k_qmi_wlan_disable()`, `ath10k_qmi_init()`, `ath10k_qmi_deinit()`, and `ath10k_qmi_set_fw_log_mode()`.

## Control Flow and Integration

SNOC code initializes QMI with MSA size, waits for QMI-driven firmware preparation, then enables WLAN with CE/shadow-register config and a WLFW mode. Shutdown or recovery disables WLAN and deinitializes QMI. The config structures bridge host-native CE arrays into `wlfw_wlan_cfg_req_msg_v01`.

## State and Persistence Behavior

`struct ath10k_qmi` persists from init to deinit. Its memory-region fields may correspond to permissions changed in secure firmware. Firmware identity fields persist for board-file selection/logging. The event list persists queued asynchronous QMI state changes until the ordered worker processes them.

## Dependencies and Integration Points

The header includes Linux QMI/QRTR types and `qmi_wlfw_v01.h`. It integrates with SNOC private state, Qualcomm SCM/SMEM through implementation code, ath10k core board-file logic, and WLFW firmware schema.

## Risks and Contract Notes

- Count-plus-pointer fields in `ath10k_qmi_wlan_enable_cfg` must remain valid for the synchronous config call.
- Local `MAX_*` constants should stay aligned with WLFW schema sizes.
- Event `data` is a raw pointer; future payload ownership rules must be explicit.
- External callers should not mutate `fw_ready` or `state` directly.

## Test Signals

- Compile SNOC/QMI builds to catch schema/header drift.
- Lifecycle tests should cover init, server arrive, WLAN enable/disable, server exit, and deinit.
- Static checks should verify count fields are clamped before copying into fixed-size WLFW arrays.
- Recovery tests should ensure event work is drained before freeing state.
