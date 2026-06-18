# sources/distributed-fs/ceph-client/drivers/bluetooth/hci_serdev.c

## Purpose
Provides the shared `serdev` transport glue for Bluetooth HCI UART protocol drivers. It connects serdev RX/TX callbacks to `struct hci_uart_proto`, creates/registers `struct hci_dev`, and manages open/close, flushing, setup, and asynchronous writes.

## Important APIs, Types, And Functions
The main exported APIs are `hci_uart_register_device_priv()` and `hci_uart_unregister_device()`. The serdev callbacks are `hci_uart_receive_buf()` and `hci_uart_write_wakeup()`. HCI device callbacks include `hci_uart_open()`, `hci_uart_close()`, `hci_uart_flush()`, `hci_uart_send_frame()`, and `hci_uart_setup()`. TX uses `hci_uart_write_work()`, `hu->tx_skb`, and the protocol `dequeue()` callback to drain frames through `serdev_device_write_buf()`.

## Control Flow
Registration installs serdev client ops, initializes the protocol lock, opens the serdev port, calls the protocol `open()`, marks the protocol ready, allocates an HCI device, sets bus/callbacks/quirks, and registers it unless `HCI_UART_INIT_PENDING` defers registration. Sending from Bluetooth core calls the protocol `enqueue()` and schedules TX wakeup. The write worker loops until no wakeup was raced in, writes as much of each skb as serdev accepts, stores a partially written skb if needed, updates TX counters, and frees completed frames. Receive callbacks ignore data until the protocol is ready, then call protocol `recv()` and update RX byte counters.

## State And Persistence
State lives in the caller-owned `struct hci_uart`: flags, HCI device, protocol pointer, protocol private data, pending TX skb, TX state bits, init/oper speeds, alignment, and work items. There is no persistence; all state is created on probe/registration and destroyed on unregister.

## Dependencies And Integration Points
This file is the bridge between `drivers/bluetooth` protocol implementations and the serdev subsystem. It depends on Bluetooth core HCI registration and quirks, `struct hci_uart_proto` from `hci_uart.h`, and serdev write/flush/open/close semantics. It also supports optional raw/external-config/no-suspend-notifier HCI quirks through flags populated by protocol drivers.

## Risks And Test Signals
Risks include partial-write handling, TX wakeup races, registering devices before vendor setup is ready, closing serdev too early for non-persistent setup devices, and protocol callbacks that assume stronger locking than provided. Test signals are reliable HCI device registration/unregistration, stable TX/RX counters, no leaked `tx_skb`, working suspend notifier quirks, and successful vendor protocol setup through serdev.
