# sources/distributed-fs/ceph-client/drivers/bluetooth/hci_uart.h

## Purpose
Defines the common HCI UART line-discipline and serdev protocol interface used by Bluetooth UART transports. It centralizes protocol IDs, ioctl numbers, flags, core structures, and H4 receive packet descriptors.

## Important APIs, Types, And Functions
`struct hci_uart_proto` is the protocol vtable for open/close/flush/setup/set_baudrate/recv/enqueue/dequeue. `struct hci_uart` stores tty/serdev handles, HCI device pointer, protocol flags, work items, protocol pointer, lock, private data, TX state, speed settings, and alignment/padding. Public functions include protocol registration (`hci_uart_register_proto()`, `hci_uart_unregister_proto()`), serdev device registration (`hci_uart_register_device_priv()`, `hci_uart_register_device()`, `hci_uart_unregister_device()`), TX helpers, init readiness, baud/flow-control helpers, and speed setters. `struct h4_recv_pkt` and the `H4_RECV_*` macros describe packet type, header length, length offset/size, maximum length, and receive callback.

## Control Flow
This header does not execute control flow, but it defines the contract used by both tty line discipline and serdev implementations. Protocol modules fill `struct hci_uart_proto`; core HCI UART code registers protocols by ID and calls protocol callbacks during open, setup, RX parsing, enqueue/dequeue, and close. H4-derived drivers pass arrays of `struct h4_recv_pkt` to `h4_recv_buf()` for reassembly.

## State And Persistence
It declares in-memory state only. Flag bits distinguish protocol set/registered/ready/init states and HCI device quirks such as raw, reset-on-init, init-pending, external-config, and vendor-detect.

## Dependencies And Integration Points
The header is consumed by all HCI UART protocol files. It depends on Bluetooth core types such as `struct hci_dev`, `struct sk_buff`, and HCI packet constants, plus tty/serdev abstractions. Conditional declarations mirror Kconfig options for H4, BCSP, LL, ATH3K, 3WIRE, Intel, BCM, QCA, AG6XX, MRVL, and AML protocol modules.

## Risks And Test Signals
Interface risk comes from changing IDs, flag meanings, or callback semantics because many protocol modules depend on them. Test signals are build coverage across enabled/disabled protocol configs, H4 parser tests using ACL/SCO/event/ISO frames, and runtime smoke tests for both tty and serdev Bluetooth UART devices.
