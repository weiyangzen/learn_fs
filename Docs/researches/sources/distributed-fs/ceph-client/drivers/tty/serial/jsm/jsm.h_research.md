# sources/distributed-fs/ceph-client/drivers/tty/serial/jsm/jsm.h

## Purpose
`jsm.h` is the shared internal contract for the Digi Neo and Classic PCI serial driver. It defines debug categories, supported PCI IDs, board/channel state, board operation callbacks, UART register layouts, Exar-specific constants, and cross-file prototypes.

## Important APIs, types, and functions
`struct board_ops` is the chip-specific method table used for interrupts, UART init/off, termios programming, modem assertion, FIFO flushing, receiver control, break control, start/stop character send, and TX draining. `struct jsm_board` stores PCI identity, resources, remapped MMIO, IRQ, port count, interrupt lock, channel pointers, UART spacing/dividend, and selected ops. `struct jsm_channel` embeds `struct uart_port` and stores locks, termios snapshots, modem state, Classic/Neo MMIO pointers, read/error queues, queue indices, counters, FIFO thresholds, flow-control watermarks, and error statistics. `struct cls_uart_struct` and `struct neo_uart_struct` define mapped UART layouts.

## Control flow
The header defines no runtime flow. It lets `jsm_driver.c` select `jsm_cls_ops` or `jsm_neo_ops`, lets tty glue call chip methods through `board_ops`, and lets chip interrupt handlers move data through common queues consumed by `jsm_input()` and flow-control helpers.

## State and persistence behavior
The volatile state model is one `jsm_board` per PCI adapter and up to eight `jsm_channel` objects per board. Per-channel 8 KiB read/error queues, modem bytes, termios fields, flags, counters, and hardware pointers are defined here. There is no disk persistence.

## Dependencies and integration points
The header depends on kernel types, tty, serial core, and device APIs. It integrates JSM with PCI IDs, `uart_port`, tty termios state, and board-specific source files that use `readb()`, `writeb()`, and burst MMIO helpers.

## Risks and test signals
Risks include lock-sensitive queue/modem state, using the wrong Classic versus Neo register layout, queue mask assumptions, and PCI ID definitions split between this header and kernel PCI headers. Test representative Classic/Neo probe, `board_ops` coverage, channel mapping, and queue wrap/overflow.
