# sources/distributed-fs/ceph-client/drivers/bluetooth/hci_nokia.c

## Purpose
Implements the Nokia H4+ Bluetooth UART protocol as a `serdev` HCI UART device. It handles Nokia-specific packet types, GPIO wake/reset lines, runtime PM, controller negotiation, alive probing, firmware download, baud-rate switching, and registration of the resulting HCI device.

## Important APIs, Types, And Functions
The central state object is `struct nokia_bt_dev`, which embeds `struct hci_uart`, stores `serdev`, reset/wakeup GPIOs, system clock rate, RX/TX queues, negotiation completion, manufacturer/version IDs, and runtime TX/RX wake state. Protocol parsing uses `struct h4_recv_pkt` entries for normal H4 ACL/SCO/event frames plus Nokia negotiation, alive, and radio packet types. `nokia_proto` supplies the HCI UART callbacks: `open`, `close`, `recv`, `enqueue`, `dequeue`, `flush`, and `setup`. Probe is handled by `nokia_bluetooth_serdev_probe()`, which acquires GPIOs and `sysclk`, requests the host-wakeup IRQ, initializes the TX queue, sets word alignment, and calls `hci_uart_register_device()`.

## Control Flow
`nokia_setup()` disables flow control, takes a runtime PM reference, resets the controller, sends a negotiation packet, verifies liveness, downloads firmware, switches to the maximum baud rate, and installs Broadcom BDADDR handling for BCM2048 devices. Negotiation and alive packets are sent through `nokia_enqueue()` and waited on through `init_completion`; receive callbacks complete the same completion after validating payloads. Firmware is requested from `nokia/bcmfw.bin` or `nokia/ti1273.bin`, then HCI command records are replayed synchronously with `__hci_cmd_sync()`. Normal receive data is reassembled by `h4_recv_buf()`, and Nokia radio packets are converted into HCI events before being handed to `hci_recv_frame()`.

## State And Persistence
Persistent runtime state lives only in kernel memory: TX queue, partial RX skb, manufacturer/version IDs, BDADDR, init status, and wake flags. Hardware state is changed through GPIOs, UART baud/flow control, runtime PM references, and firmware commands. There is no disk persistence beyond firmware files loaded through the firmware API.

## Dependencies And Integration Points
The driver depends on `serdev`, GPIO descriptors named `reset`, `host-wakeup`, and `bluetooth-wakeup`, a `sysclk`, runtime PM, `hci_uart.h`, and `btbcm` for BCM2048 address programming. It binds to `nokia,h4p-bluetooth` device-tree nodes and integrates with the Bluetooth core through the HCI UART protocol table.

## Risks And Test Signals
Risks are mostly ordering and hardware-timing sensitive: missing CTS, wrong GPIO polarity, unsupported manufacturer IDs, incomplete firmware records, bad packet alignment, and runtime PM reference imbalance during wake transitions. Useful signals are successful `hci_register_dev`, negotiation/alive debug logs, firmware command completion, clean suspend/resume with host wake IRQ activity, and traffic tests at the final baud rate.
