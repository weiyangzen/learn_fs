# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/qmi.c

## Purpose

`qmi.c` implements ath10k's Qualcomm WLFW QMI client for SNOC/WCN3990 devices. It discovers the firmware QMI service, registers indications, negotiates host capabilities, shares MSA memory and permissions, downloads board data, reports calibration metadata, switches firmware WLAN modes, reads firmware/chip capabilities, controls firmware log mode, and translates asynchronous QMI indications into ordered ath10k SNOC events.

## Important APIs, Types, and Functions

- `ath10k_qmi_init()` allocates QMI state, initializes the QMI handle, workqueue, event list, message handlers, and service lookup.
- `ath10k_qmi_deinit()` releases the QMI handle, drains work, destroys the workqueue, and frees state.
- `ath10k_qmi_wlan_enable()` sends WLAN config then mode; `ath10k_qmi_wlan_disable()` sends mode OFF.
- `ath10k_qmi_set_fw_log_mode()` sends WLFW INI firmware-log mode.
- MSA helpers send MSA base/size, validate returned memory regions, assign/unassign SCM permissions, and notify MSA ready.
- Capability/config helpers send host capability, CE config, mode, capability, BDF download, and calibration report requests.
- Event helpers post internal events from QRTR/QMI callbacks and process them on an ordered workqueue.

## Control Flow

Initialization reads device-tree booleans for fixed MSA permissions and no MSA-ready indication, creates a QMI handle for WLFW messages, allocates an ordered workqueue, and registers service lookup. Server discovery connects the QRTR socket and posts `SERVER_ARRIVE`.

The arrival worker registers indications. If firmware is already ready, it notifies SNOC immediately. Otherwise it optionally sends host capabilities, sends MSA info, waits 20 ms for an SDM845 security workaround, assigns MSA permissions, sends MSA ready, and requests capabilities. MSA-ready handling fetches the board file using QMI IDs, downloads BDF segments, and sends calibration report. FW-ready handling notifies SNOC. Server exit removes permissions, frees board files, optionally triggers crash dump, and sends FW_DOWN.

WLAN enable serializes CE target/service/shadow-register config into the WLFW config request, clamps array lengths to protocol maxima, waits for success, then sends the requested mode.

## State and Persistence Behavior

`struct ath10k_qmi` persists QMI handle/socket, ordered workqueue, event list/lock, MSA regions, chip/board/SoC IDs, firmware version/build strings, calibration metadata, platform booleans, readiness flag, and lifecycle state. SCM memory ownership changes persist outside ordinary kernel pointer lifetime until removed. The file may also write the firmware build ID into Qualcomm SMEM.

## Dependencies and Integration Points

The file depends on Linux QMI/QRTR, sockets, workqueues, device tree, Qualcomm SCM, SMEM, and firmware helpers. ath10k integration goes through `snoc.h`, core board-file lookup/freeing, SNOC firmware indications/crash dumps, SNOC quirk flags, and the WLFW schema from `qmi_wlfw_v01.h/.c`.

## Risks and Edge Cases

- MSA region validation and overflow checks are security-critical.
- SCM permission assignment must unwind already-mapped regions on partial failure.
- `ath10k_qmi_msa_ready_send_sync_msg()` appears to set `ret = -EINVAL` on rejected response but then returns success at the final return; this should be reviewed.
- Final BDF segment malformed-message is intentionally treated as non-fatal for known firmware CRC behavior.
- Event allocation uses `GFP_ATOMIC`; dropped events can stall boot/recovery.
- The host-capability 8-bit quirk must match firmware expectations.
- `version` is accepted by config send but not actually sent.

## Test Signals

- Boot tests should trace server discovery, indication registration, MSA info/permissions/ready, capability read, BDF download, calibration report, and FW ready.
- Device-tree variants should cover fixed permissions and no MSA-ready indication.
- QMI fault injection should cover rejected responses, timeouts, oversized/out-of-range memory regions, BDF failures, and event allocation failure.
- Recovery tests should verify server-exit permission cleanup, board-file freeing, FW_DOWN, and crash-dump gating.
