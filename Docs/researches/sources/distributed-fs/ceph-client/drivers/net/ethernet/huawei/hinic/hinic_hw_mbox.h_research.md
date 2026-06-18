# sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic/hinic_hw_mbox.h

## Purpose
Declares mailbox constants, CSR offsets, callback signatures, mailbox send/receive state, function-to-function mailbox aggregate state, validation helpers, and PF/VF mailbox APIs.

## Important APIs, Types, and Functions
Important types include `vf_cmd_check_handle`, `mbox_msg_info`, `hinic_recv_mbox`, `hinic_send_mbox`, callback typedefs, `mbox_event_state`, `hinic_mbox_cb_state`, `hinic_mbox_func_to_func`, `hinic_mbox_work`, and `vf_cmd_msg_handle`. Public APIs cover callback registration, mailbox init/free, message send to PF/VF/function, VF random-id init, and command validation.

## Control Flow
The header has no runtime flow. It defines state and contracts implemented by `hinic_hw_mbox.c` and consumed by management, SR-IOV, and NIC control paths.

## State and Persistence Behavior
The mailbox aggregate stores transient in-memory send/receive state plus VF random ids cached from firmware. CSR offsets and writeback status describe hardware-persistent mailbox coordination points.

## Dependencies and Integration Points
Forward references `hinic_hwdev` and uses `hinic_mod_type` from HWIF definitions. It integrates VF mailbox callbacks with PF management forwarding and VF NIC event delivery.

## Risks
Callback state bit numbering is ABI only within the driver but drives teardown waits. `HINIC_MAX_FUNCTIONS` sizes large per-function arrays. CSR offsets must match hardware. `HINIC_MBOX_DATA_SIZE` is the maximum payload and must remain aligned with segmentation constants.

## Test Signals
Compile coverage, callback register/unregister, VF and PF mailbox send paths, oversized payload rejection, random-id initialization, and PF command validation cover this header.
