# sources/distributed-fs/ceph-client/include/net/bluetooth/hci_drv.h

## Purpose

`hci_drv.h` defines an HCI driver-private command/event channel layered on Bluetooth HCI packet handling, allowing common and driver-specific commands to be sent to HCI drivers.

## Important APIs, Types, and Functions

`struct hci_drv_cmd_hdr` and `struct hci_drv_ev_hdr` carry little-endian opcode and length. Standard driver events include command status and command complete, with status values for success, unspecified error, unknown command, and invalid parameters. `HCI_DRV_OP_READ_INFO` returns driver name plus supported command opcodes in `struct hci_drv_rp_read_info`. Driver-specific commands are grouped under `HCI_DRV_OGF_DRIVER_SPECIFIC`. The processing API includes `hci_drv_cmd_status()`, `hci_drv_cmd_complete()`, and `hci_drv_process_cmd()`. `struct hci_drv_handler` binds a handler function to expected data length, and `struct hci_drv` holds common and driver-specific handler tables.

## Control Flow

An HCI driver packet is parsed by `hci_drv_process_cmd()`, routed to either common or specific handler tables by opcode group, length-checked, executed, and completed through status or complete events back to the HCI device path.

## State and Persistence Behavior

No persistent state is defined. Handler tables are static driver data referenced by `struct hci_dev`. Responses are transient skbs/events.

## Dependencies and Integration Points

The header depends on Bluetooth common and HCI headers. It integrates with `struct hci_dev` through the `hci_drv` pointer in `hci_core.h`, and with monitor/socket paths through HCI driver packet types.

## Risks and Edge Cases

Opcode namespaces must not collide between common and driver-specific handlers. Length validation relies on accurate `data_len` values. Flexible supported-command arrays in `READ_INFO` require careful allocation. Unknown commands must return defined driver status rather than leaking kernel errors directly.

## Test Signals

Test common `READ_INFO`, unsupported opcodes, invalid lengths, driver-specific routing, command status versus complete emission, long driver names at the 32-byte limit, and monitor visibility of HCI driver packets.
