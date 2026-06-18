# sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic/hinic_hw_dev.c

## Purpose
Implements the main HINIC hardware-device lifecycle and firmware-facing device control. It initializes the hardware interface, MSI-X, AEQs, PF/VF management and mailbox channels, device reset/capability discovery, VF bookkeeping, firmware context, resource state, and later brings IO queues up and down for data traffic.

## Important APIs, Types, and Functions
Public functions include `hinic_init_hwdev`, `hinic_free_hwdev`, `hinic_hwdev_ifup`, `hinic_hwdev_ifdown`, `hinic_port_msg_cmd`, `hinic_hilink_msg_cmd`, callback registration helpers, queue accessors, MSI-X helpers, `hinic_hwdev_hw_ci_addr_set`, `hinic_set_interrupt_cfg`, and `hinic_get_board_info`. Important internal routines include `parse_capability`, `get_capability`, `init_msix`, `init_fw_ctxt`, `set_hw_ioctxt`, `clear_io_resources`, `set_resources_state`, `get_base_qpn`, `init_pfhwdev`, `free_pfhwdev`, and `hinic_l2nic_reset`.

## Control Flow
`hinic_init_hwdev` allocates and initializes `hinic_hwif`, allocates `hinic_pfhwdev`, enables MSI-X, waits for outbound state, initializes AEQs, initializes PF/VF management and mailbox infrastructure, performs L2NIC reset, obtains capabilities, initializes VF functions, initializes firmware tables, and marks resources active. `hinic_hwdev_ifup` gets the global base QPN, initializes CEQs/command queues/work queues, creates QPs, waits or re-enables doorbells, and sends HW IO context. `hinic_hwdev_ifdown` clears IO resources, destroys QPs, and frees IO infrastructure. Free reverses resource state, VF state, management/mailbox, AEQs, MSI-X, and HWIF mappings.

## State and Persistence Behavior
Long-lived state is rooted in `struct hinic_hwdev` inside `struct hinic_pfhwdev`: hardware interface, MSI-X entries, AEQs, IO channel, function-to-function mailbox, NIC capabilities, port id, devlink private data, PF-to-management channel, NIC event callbacks, and self-command handlers. Firmware-persistent state includes resource active/clean state, firmware context, function table, interrupt config, SQ high-CI DMA address, base QPN, and queue depths.

## Dependencies and Integration Points
Integrates with PCI, MSI-X, devlink health reporters, SR-IOV helper `hinic_vf_func_init/free`, event queues, management messages, mailbox, IO/QP setup, and NIC-facing modules that use port commands. `hinic_msg_to_mgmt` is the common transport for most firmware commands, routing VF requests through mailbox.

## Risks
Initialization has many firmware-dependent stages and must unwind in exact reverse order. `hinic_hwdev_get_sq/rq` indexes `qps[i]` before range validation, so callers must pass valid queue indices. Some state waits try to re-enable outbound or doorbell state after timeout, which may hide hardware readiness issues. Callback unregister paths spin until running callbacks complete, so hung handlers can block teardown. Capability parsing relies on firmware-reported IRQ and queue counts.

## Test Signals
Probe/remove, PF and VF init, devlink health reporter creation, L2NIC reset failures, capability negotiation, resource state set/clear, ifup/ifdown loops, MSI-X config read/write, SQ CI address setup, board-info query, queue accessor bounds tests, and fault/watchdog event reporting are useful signals.
