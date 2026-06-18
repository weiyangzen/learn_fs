# sources/distributed-fs/ceph-client/sound/drivers/mpu401/mpu401_uart.c

## Purpose

This file provides the reusable ALSA MPU-401 UART rawmidi implementation. It handles low-level port or MMIO access, command/reset sequencing, IRQ and polling-driven input/output, rawmidi stream callbacks, resource ownership, and creation of the rawmidi device.

## Important APIs, Types, and Functions

Exported APIs are `snd_mpu401_uart_interrupt()`, `snd_mpu401_uart_interrupt_tx()`, and `snd_mpu401_uart_new()`. Internal helpers include low-level `mpu401_read/write_port/mmio`, `snd_mpu401_uart_cmd()`, `snd_mpu401_do_reset()`, input/output open/close/trigger callbacks, `snd_mpu401_uart_input_read()`, `snd_mpu401_uart_output_write()`, polling timer add/remove callbacks, and `snd_mpu401_uart_free()`.

## Control Flow

Creation builds an ALSA rawmidi device, allocates `struct snd_mpu401`, requests I/O regions unless integrated, selects port or MMIO accessors, requests IRQ when provided, enables timer polling when no IRQ/hook is available, assigns rawmidi ops, and returns the rawmidi object. Open callbacks run optional board hooks, reset and enter UART mode if the opposite stream is not already open, then set stream mode bits. Input trigger flushes FIFO on first enable, optionally starts polling, and performs an initial read. Output trigger sets output-trigger mode, optionally starts polling, and writes pending bytes. IRQ handlers read input and opportunistically write output; timer polling requeues itself each jiffy and calls the same interrupt worker. Close callbacks clear mode bits, reset hardware when both streams are closed, and run optional close hooks.

## State and Persistence Behavior

`struct snd_mpu401` persists accessors, ports, IRQ, rawmidi pointer, substream pointers, mode bits, timer state, locks, resource handle, hardware type, board hooks, and info flags. The polling timer persists while input or output timer bits are set. Rawmidi transmit buffers own queued output bytes; the driver peeks, writes to hardware, and acknowledges bytes after successful writes.

## Dependencies and Integration Points

It depends on ALSA rawmidi/core, `sound/mpu401.h`, Linux I/O port/MMIO APIs, IRQ APIs, timers, spinlocks, and optional hardware hook callbacks. The generic `mpu401.c` front-end and other ALSA drivers can instantiate this helper through `snd_mpu401_uart_new()`.

## Risks

Hardware timing is the main risk. Command ACK waits, reset sequencing, and FIFO polling use bounded busy loops and may fail on slow or nonstandard devices. Polling mode runs every jiffy and can perform poorly. Output has no real transmit IRQ on standard UART mode, so output latency depends on opportunistic input IRQs or polling. Locking spans input, output, and timer state; timer removal uses non-sync deletion, so lifetime is protected by rawmidi/card teardown assumptions. Resource cleanup must match requested regions and IRQs.

## Test Signals

Test port and MMIO access modes, IRQ and polling modes, input-only/output-only/duplex flags, reset failure paths, command ACK/no-ACK hardware flags, transmit FIFO full behavior, rawmidi trigger start/stop races, timer polling add/remove balance, module unload while streams are closed, and legacy MPU hardware variants such as PC98II port layout.
