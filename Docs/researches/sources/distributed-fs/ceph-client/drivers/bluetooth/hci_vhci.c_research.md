# sources/distributed-fs/ceph-client/drivers/bluetooth/hci_vhci.c

## Purpose
Implements the Bluetooth virtual HCI misc device `/dev/vhci`. User space can create virtual HCI controllers, inject HCI frames into the Bluetooth core, read frames emitted by the core, and use debugfs controls for suspend, wakeup, Microsoft/AOSP extension testing, and devcoredump testing.

## Important APIs, Types, And Functions
`struct vhci_data` holds the HCI device, read waitqueue, outgoing read queue, open mutex, open timeout work, suspend work, suspend/wakeup/debug capability state, and initialization counter. HCI callbacks are `vhci_open_dev()`, `vhci_close_dev()`, `vhci_flush()`, `vhci_send_frame()`, `vhci_wakeup()`, and `vhci_setup()`. Character-device operations are `vhci_open()`, `vhci_read()`, `vhci_write()`, `vhci_poll()`, and `vhci_release()`. Debugfs operations expose `force_suspend`, `force_wakeup`, `msft_opcode`, `aosp_capable`, and `force_devcoredump`.

## Control Flow
Opening `/dev/vhci` allocates `vhci_data`, initializes queues/work, and schedules a one-second default device creation timeout. User writes with packet type `HCI_VENDOR_PKT` cancel the timeout and create a controller with opcode bits selecting external config and raw mode; normal HCI event/ACL/SCO/ISO writes inject frames into `hci_recv_frame()`. HCI frames sent by the Bluetooth core are prefixed with packet type, queued to `readq`, and woken for user-space reads after initialization. Release unregisters and frees the HCI device, removes debugfs files, drains queues, and frees private state.

## State And Persistence
All state is per open file descriptor and per virtual HCI device. Debugfs toggles are runtime-only. The module parameter `amp` exists but is not used in the shown code path. There is no persistent storage; devcoredump data goes through the kernel devcoredump facility.

## Dependencies And Integration Points
The file integrates with the miscdevice subsystem, Bluetooth core HCI registration, debugfs, waitqueues, workqueues, poll/read/write file operations, optional `CONFIG_BT_MSFTEXT`, optional `CONFIG_BT_AOSPEXT`, and optional `CONFIG_DEV_COREDUMP`. It is a key test hook for user-space Bluetooth stacks and kernel HCI behavior.

## Risks And Test Signals
Risks include userspace ABI regressions, failure to handle malformed packet lengths/types, races between auto-creation and explicit creation, debugfs lifetime issues, and queue wakeup mistakes that hang readers. Test signals are `/dev/vhci` open/read/write/poll behavior, virtual controller registration, injected frame delivery, debugfs suspend/resume effects, and forced devcoredump done/abort/timeout paths.
