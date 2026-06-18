# sources/distributed-fs/ceph-client/drivers/usb/serial/io_edgeport.c

## Purpose

This file implements the Inside Out Networks Edgeport and EPiC USB serial drivers. It supports 2-, 4-, and 8-port Edgeport adapters plus compatible EPiC devices, multiplexing all serial ports over shared USB bulk and interrupt endpoints. The driver handles firmware and descriptor setup, IOSP packet parsing, tty operations, termios programming, flow control, modem and line status accounting, and close/drain behavior.

## Important APIs, Types, And Functions

`struct edgeport_serial` stores device-level state: product/manufacturing/boot/EPiC descriptors, endpoint addresses and URBs, shared bulk buffers, receive parser state, pending byte counts, and the backpointer to `struct usb_serial`. `struct edgeport_port` stores per-port state: transmit credits, maximum credits, a circular `TxFifo`, a write URB, write/open/close/command/chase flags, shadow UART registers, baud/data settings, wait queues, and the owning `usb_serial_port`.

Important callbacks and APIs include `edge_startup`, `edge_disconnect`, `edge_release`, `edge_port_probe`, `edge_port_remove`, `edge_open`, `edge_close`, `edge_write`, `edge_write_room`, `edge_chars_in_buffer`, `edge_throttle`, `edge_unthrottle`, `edge_set_termios`, `edge_tiocmget`, `edge_tiocmset`, `edge_ioctl`, `edge_break`, `edge_interrupt_callback`, `edge_bulk_in_callback`, `edge_bulk_out_data_callback`, and `edge_bulk_out_cmd_callback`. Protocol helpers include `process_rcvd_data`, `process_rcvd_status`, `send_more_port_data`, `send_iosp_ext_cmd`, `write_cmd_usb`, `send_cmd_write_baud_rate`, `send_cmd_write_uart_register`, and `change_port_settings`. Firmware/configuration helpers include `get_epic_descriptor`, `get_manufacturing_desc`, `get_boot_desc`, `get_product_info`, `load_application_firmware`, `update_edgeport_E2PROM`, `sram_write`, `rom_write`, and `rom_read`.

## Control Flow

Startup allocates `edgeport_serial`, reads the device name, then tries to read an EPiC descriptor. EPiC devices provide capability bits and endpoint descriptors directly from the active interface. Non-EPiC devices read manufacturing and boot descriptors from ROM, derive product information, download application firmware into SRAM, optionally update boot EEPROM firmware, and later reuse endpoint URBs created by the USB serial core.

Open lazily wires the shared interrupt and bulk URBs from port 0 for non-EPiC devices, starts interrupt polling, initializes wait queues and UART shadow state, sends `IOSP_CMD_OPEN_PORT`, and waits for an open response. The open response carries initial modem status and TX buffer size; it sets `txCredits` and `maxTxCredits`, synchronizes termios settings to the device, clears `openPending`, and wakes open waiters. Open then allocates the per-port TX FIFO and write URB.

The interrupt endpoint reports total bulk-IN bytes available and per-port TX credits. The callback increments `rxBytesAvail` and submits a shared bulk read if no read is active, then distributes new credits to open ports, wakes tty writers, and calls `send_more_port_data`. The bulk-IN callback decrements `rxBytesAvail`, feeds the IOSP stream parser, and resubmits while more bytes remain. `process_rcvd_data` walks a state machine over IOSP data headers and command/status headers, routing data payloads to the target tty and status messages to `process_rcvd_status`.

Writes enter `edge_write`, which copies only as many bytes as current credits allow into the per-port circular FIFO. `send_more_port_data` sends queued data only when the port is open, no write URB is in progress, the FIFO is non-empty, and enough credits are available. It prepends an IOSP data header, submits one bulk OUT URB, decrements credits, and updates TX counters. Completion clears `write_in_progress`, wakes tty writers, and tries to send more.

Close waits for the local FIFO to empty, optionally sends a chase command and waits for a chase response or timeout, optionally sends close, clears open flags, kills and frees the write URB, and frees the FIFO. Termios changes map tty settings to UART LCR/MCR values, IOSP RX/TX flow commands, XON/XOFF characters, and baud divisor writes.

## State And Persistence

Device-level state persists from attach to release; per-port state persists from port probe to removal, with FIFO and write URB allocated only while opened. Transmit flow is credit-based, so `txCredits`, `maxTxCredits`, FIFO occupancy, and `write_in_progress` are the core mutable state. Receive parser state (`rxState`, headers, port, remaining bytes) persists across bulk URB boundaries. Shadow UART registers store the driver's last programmed LCR/MCR/MSR/LSR values and are used for modem ioctls and incremental termios changes. Firmware downloads and EEPROM boot updates affect device memory; SRAM firmware lasts until reset, while ROM writes are persistent device changes.

## Dependencies And Integration Points

The driver depends on the USB serial core, tty core, serial ioctls, firmware loader for Intel HEX images, USB control transfers, wait queues, spinlocks, and the Edgeport headers `io_edgeport.h`, `io_ionsp.h`, and `io_16654.h`. It registers four `usb_serial_driver` instances: `edgeport_2`, `edgeport_4`, `edgeport_8`, and `epic`, each with matching ID tables and shared operations. It reuses generic USB serial helpers for `tiocmiwait` and `get_icount`.

## Risks

The driver has several concurrency-sensitive paths. Shared device-level read state is protected by `es_lock`, while per-port TX state uses `ep_lock`; callbacks, open/close, write, throttle, and termios changes can interact. TX credits must never underflow or exceed actual device buffer capacity, or writes can be dropped or stall. `send_more_port_data` removes bytes from the FIFO before URB submission; on submit failure it restores credits and counters but not FIFO contents, logging data loss. Receive parsing must handle IOSP headers split across URBs without getting stuck. Firmware and ROM update code writes to device memory and depends on correct firmware files and descriptor interpretation. Capability gating for EPiC devices must be respected or unsupported commands may fail silently.

## Test Signals

Signals include probe for all supported port-count variants and EPiC devices, missing firmware handling, firmware download and no-download cases, EEPROM update paths on controlled hardware, open response timeout, multi-port simultaneous reads/writes, TX credit replenishment, bulk-IN parser headers split across URBs, status handling for open/chase/LSR/MSR, termios matrix coverage, throttle/unthrottle with RTS and XON/XOFF, `TIOCMGET`/`TIOCMSET`, `TIOCSERGETLSR`, break control, close drain/chase timeout, disconnect during active URBs, and data-loss behavior on bulk OUT submit failure.
