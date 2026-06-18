# sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic/hinic_hw_dev.h

## Purpose
Defines the central HINIC hardware device model, firmware command IDs, capabilities, management event IDs, resource state values, command payload structs, fault/watchdog payloads, PF extension state, and the public hardware-device API.

## Important APIs, Types, and Functions
Important enums include `hinic_port_cmd`, `hinic_hilink_cmd`, `hinic_ucode_cmd`, `hinic_mgmt_msg_cmd`, `hinic_cb_state`, `hinic_res_state`, fault types and fault levels. Important structs include `hinic_cap`, `hinic_cmd_fw_ctxt`, `hinic_cmd_hw_ioctxt`, `hinic_ceq_ctrl_reg`, `hinic_msix_config`, `hinic_board_info`, `hinic_hwdev`, `hinic_nic_cb`, `hinic_pfhwdev`, `hinic_dev_cap`, `hinic_fault_event`, and `hinic_mgmt_watchdog_info`. Public APIs cover lifecycle, port/hilink messaging, ifup/ifdown, callback registration, queue lookup, MSI-X configuration, SQ CI configuration, and board-info retrieval.

## Control Flow
The header has no execution, but it defines the staged contracts used by `hinic_hw_dev.c`, `hinic_hw_mgmt.c`, `hinic_hw_mbox.c`, `hinic_hw_io.c`, and the upper NIC driver. The port command enum maps user-facing NIC operations to firmware messages.

## State and Persistence Behavior
`struct hinic_hwdev` is the long-lived root object for one PCI function. Payload structs are serialized to firmware and therefore represent persistent hardware/firmware state such as queue depths, page sizes, resource state, interrupt moderation, VF random IDs, firmware context, board information, and health events.

## Dependencies and Integration Points
Includes devlink and the HINIC hardware interface, event queue, management, QP, IO, and mailbox headers. It links the hardware layer to SR-IOV, devlink health, L2NIC port configuration, queue operations, and management event callbacks.

## Risks
Command IDs and struct layouts are firmware ABI. Duplicate enum values exist in the port command list for compatibility and require careful command routing. Several structs start with `status` and `version` fields expected by firmware; changing field order or endian handling breaks responses. `HINIC_MGMT_NUM_MSG_CMD` depends on command-base arithmetic.

## Test Signals
Build coverage, firmware command round trips for common port commands, fault/watchdog devlink events, MSI-X config get/set, capability parsing, VF command validation, and queue lifecycle tests validate the header contract.
