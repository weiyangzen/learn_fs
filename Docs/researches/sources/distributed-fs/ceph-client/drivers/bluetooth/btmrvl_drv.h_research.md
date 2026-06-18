# sources/distributed-fs/ceph-client/drivers/bluetooth/btmrvl_drv.h

## Purpose
Defines shared Marvell Bluetooth driver data structures, constants, vendor command/event IDs, power-management states, firmware-dump markers, function-pointer hooks, and core function prototypes used by the Marvell SDIO transport and common driver files.

## Important APIs, Types, And Functions
- Packet and timing constants include `BTM_HEADER_LEN`, `BTM_UPLD_SIZE`, `WAIT_UNTIL_HS_STATE_CHANGED`, and `WAIT_UNTIL_CMD_RESP`.
- Firmware dump helpers are represented by `enum rdwr_status`, `struct memory_type_mapping`, and markers such as `FW_DUMP_HOST_READY`, `FW_DUMP_DONE`, and `FW_DUMP_READ_DONE`.
- Runtime containers include `struct btmrvl_thread`, `struct btmrvl_device`, `struct btmrvl_adapter`, and `struct btmrvl_private`.
- Vendor opcodes and event IDs cover module config, scan-window reporting, SCO routing, BDADDR set, auto-sleep, host-sleep config/enable, config data load, and power-state events.
- Prototypes expose interrupt, event, command, HCI registration, card add/remove, and optional debugfs functions.

## Control Flow
The header itself does not execute logic, but it defines how the common driver and transport cooperate. The transport fills hardware callbacks in `struct btmrvl_private`; the main service thread uses those callbacks to process interrupts, wake firmware, and send packets. Vendor command helpers update `btmrvl_device` flags and wait on `btmrvl_adapter` wait queues. Event processing updates `btmrvl_adapter` power-save and host-sleep fields that gate TX scheduling.

## State And Persistence
`struct btmrvl_device` persists card/HCI identity, current command trigger fields, GPIO/gap configuration, download readiness, and send-command state. `struct btmrvl_adapter` persists TX queue, interrupt count, power-save mode/state, host-sleep state, wakeup retry count, command and host-sleep wait queues, command completion flag, suspend booleans, and an aligned hardware register buffer. `struct btmrvl_private` ties these together with hardware callbacks, a spinlock, optional debugfs data, and surprise-removal state.

## Dependencies And Integration Points
Includes kernel threading, wait queue, interrupt, I/O, OF/platform, PM runtime, and Bluetooth headers. It also intentionally exposes transport-independent logic to bus-specific code such as `btmrvl_sdio.c`, while debugfs and main logic include this header to share state and prototypes.

## Risks And Edge Cases
Many fields are updated from interrupt, service-thread, command-wait, debugfs, and PM contexts, so races are controlled partly by `driver_lock` and partly by wait-queue ordering. Function pointers must be installed before the service thread can process TX or interrupts. The upload size and four-byte Marvell header limit must match firmware expectations. Debugfs direct writes and device-tree configuration both mutate `gpio_gap`, so invalid board data can affect host-sleep behavior.

## Test Signals
Compile tests should cover debugfs enabled/disabled and the SDIO transport. Runtime signals include correct initialization of wait queues and skb queue, command completion wakeups, power-save/host-sleep state transitions, surprise removal waking blocked waiters, and transport callbacks being non-null before packet transmission or interrupt processing.
