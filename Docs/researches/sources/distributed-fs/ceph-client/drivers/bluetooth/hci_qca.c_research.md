# sources/distributed-fs/ceph-client/drivers/bluetooth/hci_qca.c

## Purpose
Implements Qualcomm Bluetooth HCI UART support, including H4 framing plus Qualcomm HCI In-Band Sleep, SoC-specific power sequencing, firmware/NVM setup, baud-rate negotiation, subsystem-restart memory dumps, debugfs counters, serdev probing, and suspend/resume behavior.

## Important APIs, Types, And Functions
`struct qca_data` is the protocol runtime state: RX skb, TX queues, IBS wait queue, memdump queue, IBS spinlock/state, clock votes, timers, ordered workqueue, completions, flags, memdump state, firmware/controller IDs, and debug counters. `struct qca_serdev` stores serdev-side power/control resources such as `bt_en`, `sw_ctrl`, `susclk`, SoC type, regulator/power-sequencer data, UART speeds, broken-BDADDR marker, HFP offload support, and optional firmware names. The exported protocol is `qca_proto`, and the serdev driver is `qca_serdev_driver`. Major helpers include `qca_open()`, `qca_close()`, `qca_enqueue()`, `qca_recv()`, `qca_set_speed()`, `qca_setup()`, `qca_power_on()`, `qca_power_off()`, `qca_hw_error()`, and `qca_controller_memdump()`.

## Control Flow
Open allocates `qca_data`, requires UART flow control, creates queues/timers/work, and initializes IBS states as asleep. Transmit prepends the HCI packet type; if IBS is disabled or suspend is active it queues directly, otherwise it either sends while awake, queues while waking, or starts a WAKE_IND handshake. Device WAKE/SLEEP/ACK bytes are parsed as synthetic H4 receive packet types and drive `device_want_to_wakeup()`, `device_want_to_sleep()`, and `device_woke_up()`. Setup disables IBS during initialization, powers the controller, reads SoC version, sets init/operating speeds, downloads firmware/NVM through `qca_uart_setup()`, enables quirks and debugfs, registers coredump callbacks, and retries power-on up to `MAX_INIT_RETRIES`.

## State And Persistence
State is volatile kernel state plus hardware regulator/GPIO/clock/UART state. The driver tracks many flags: `QCA_IBS_DISABLED`, vendor-event dropping, suspend, memdump collection, hardware error, SSR, BT off, ROM firmware, and debugfs creation. Memory dumps are streamed into the HCI devcoredump facility; firmware names are read from firmware-name properties but not persisted.

## Dependencies And Integration Points
The file depends on `btqca` vendor helpers, `hci_uart`, serdev, optional ACPI/OF matches, regulators, clocks, GPIOs, power sequencing, debugfs, devcoredump, and Bluetooth core quirks. It supports many compatible strings, including QCA2066, QCA6390, WCN3950/3988/399x/6750/6855/7850, and ACPI IDs. It also wires HFP non-HCI data path support for capable SoCs.

## Risks And Test Signals
Risk concentrates in concurrent state machines: IBS timers and workqueue, suspend waiting on RX sleep, SSR/memdump flag clearing, vendor-event dropping during baud changes, power-sequencer versus legacy regulator control, and non-persistent setup shutdown paths. Test signals include successful firmware setup, debugfs IBS counters changing as expected, suspend/resume without wake storms, coredump creation on forced crash, BT on/off cycles, max-speed property coverage, and probe on both OF and ACPI-described devices.
