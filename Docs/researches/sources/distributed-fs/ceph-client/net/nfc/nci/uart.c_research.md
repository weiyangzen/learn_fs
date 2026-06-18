# sources/distributed-fs/ceph-client/net/nfc/nci/uart.c

## Purpose

This file implements the `N_NCI` tty line discipline and the generic NCI-over-UART transport framework. It lets controller-specific UART drivers register an `nci_uart` template, attach it to a tty through `NCIUARTSETDRIVER`, queue NCI frames for tty output, and parse byte-stream input into complete NCI packets for the driver receive callback.

## Important APIs, Types, and Functions

The public driver API is `nci_uart_register()`, `nci_uart_unregister()`, and `nci_uart_set_config()`. Registration validates mandatory callbacks (`open`, `recv`, `close`), installs `nci_uart_send()` as the transport send callback, and stores the template in `nci_uart_drivers[]`. `nci_uart_set_config()` updates tty baud and RTS/CTS flow control. The line discipline is represented by `nci_uart_ldisc` with open, close, receive, write wakeup, ioctl, and no-op read/write methods.

Key internal functions are `nci_uart_set_driver()` for per-tty allocation and driver open, `nci_uart_write_work()` for draining queued skbs to `tty->ops->write`, `nci_uart_tx_wakeup()` for serialized scheduling, and `nci_uart_default_recv_buf()` for assembling byte-stream input into NCI frames using `NCI_CTRL_HDR_SIZE` and `nci_plen()`.

## Control Flow

Opening the line discipline initializes tty state and flushes pending bytes. User space then selects a registered driver with `NCIUARTSETDRIVER`; the code copies the registered template into a new per-tty `struct nci_uart`, initializes queues/work/locks, calls the driver's `open()`, and pins the module. Transmit callers enqueue skbs and schedule write work. The worker calls optional `tx_start`, writes until the tty refuses more bytes or the queue empties, preserves a partially written skb in `tx_skb`, and calls optional `tx_done` when empty.

Receive flow is entered from `receive_buf`. It serializes parsing with `rx_lock`, allocates an NCI skb once a packet starts, reads the three-byte control header, computes total packet length from the payload length, copies chunks until complete, then hands the skb to `nu->ops.recv()`.

## State and Persistence

Per-tty state includes `tx_q`, `tx_skb`, `tx_state` bits, `rx_skb`, `rx_packet_len`, `write_work`, `rx_lock`, and the attached tty/device pointers. State is volatile and destroyed on line discipline close, which purges queues, frees partial RX/TX skbs, calls driver close, drops the module reference, cancels pending work, and frees the instance.

## Dependencies and Integration Points

This code integrates the tty subsystem, NCI core skb allocation, NFC logging, and controller-specific NCI UART drivers. User space interacts only through tty line discipline selection and ioctl; normal tty read/write are disabled.

## Risks and Edge Cases

Partial writes rely on the tty driver returning a sane length. The write worker sets `TTY_DO_WRITE_WAKEUP`; broken tty wakeups can stall output until another trigger. RX parsing assumes standard unframed NCI packets; drivers needing other framing must handle it through their registered callbacks. Close ordering is important: queued skbs are freed before `cancel_work_sync()`, but the worker can still run until cancellation completes.

## Test Signals

Tests should cover driver registration collisions, ioctl before/after attachment, partial tty writes, wakeup rescheduling, close while TX is active, receive of fragmented headers and multiple packets in one buffer, corrupted receive callback return, and baud/flow-control termios changes.
