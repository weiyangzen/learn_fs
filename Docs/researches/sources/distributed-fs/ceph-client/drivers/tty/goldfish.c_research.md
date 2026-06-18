# sources/distributed-fs/ceph-client/drivers/tty/goldfish.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/tty/goldfish.c` implements the TTY, console, and early-console driver for the Goldfish virtual platform. It exposes MMIO-backed emulator TTY devices as `/dev/ttyGF*`, supports legacy Goldfish virtual-address I/O and newer Ranchu DMA/physical-address I/O, handles interrupts for incoming data, and registers per-line consoles. The source was read as a complete 472-line file for this report.

## Important APIs, Types, and Functions

The main type is `struct goldfish_tty`, containing `tty_port`, spinlock, MMIO base, IRQ, console, device pointer, and device version. Key globals are `goldfish_tty_driver`, `goldfish_tty_line_count`, `goldfish_tty_current_line_count`, `goldfish_ttys`, and `goldfish_tty_lock`.

Important functions include `do_rw_io`, `goldfish_tty_rw`, `goldfish_tty_do_write`, `goldfish_tty_interrupt`, `goldfish_tty_activate`, `goldfish_tty_shutdown`, `goldfish_tty_open`, `goldfish_tty_close`, `goldfish_tty_hangup`, `goldfish_tty_write`, `goldfish_tty_write_room`, `goldfish_tty_chars_in_buffer`, `goldfish_tty_console_write`, `goldfish_tty_console_setup`, `goldfish_tty_create_driver`, `goldfish_tty_delete_driver`, `goldfish_tty_probe`, `goldfish_tty_remove`, `gf_earlycon_setup`, and the platform driver/of-match declarations.

## Control Flow

Probe maps the MMIO resource, gets the IRQ, assigns a line from platform ID or the current count, creates the shared TTY driver on the first device, initializes per-line port state, reads the device version, sets a 32-bit DMA mask for Ranchu-style devices, disables interrupts, requests the IRQ, registers the TTY device, registers a per-line console, and stores driver data. Remove unregisters the console and TTY device, unmaps MMIO, frees the IRQ, destroys the port, and deletes the shared driver when the last line is removed.

Writes flow through `goldfish_tty_rw`. Version 0 devices pass virtual addresses to MMIO registers. Version > 0 devices split the buffer by page, DMA-map each chunk, program data pointer and length registers, issue read/write commands, and unmap after completion. RX interrupts read `BYTES_READY`, reserve flip-buffer space, command a device read into the prepared buffer, and push the flip buffer. Port activation and shutdown enable/disable device interrupts with MMIO commands.

Console writes reuse the same write path by console index. Early console setup installs a UART-console write shim that writes characters directly to the mapped MMIO address for `google,goldfish-tty`.

## State and Persistence Behavior

Driver state is kept in the global `goldfish_ttys` array and per-device `struct goldfish_tty`: port state, MMIO base, IRQ, console, version, and device pointer. Global line count controls allocation and lifetime of the shared TTY driver. Hardware state is in Goldfish MMIO registers for data pointer, length, command, interrupt enable, bytes-ready, and version. There is no persistent storage.

## Dependencies and Integration Points

The driver depends on the platform bus, OF matching for `google,goldfish-tty`, Goldfish MMIO helpers (`gf_ioread32`, `gf_iowrite32`, `gf_write_ptr`), DMA mapping APIs, TTY core, `tty_port`, flip buffers, console and earlycon infrastructure, IRQ handling, and serial core console helpers. It is selected by `CONFIG_GOLDFISH_TTY`; early console is controlled by `CONFIG_GOLDFISH_TTY_EARLY_CONSOLE`.

## Risks and Edge Cases

The driver creates the shared TTY driver lazily on the first probed device and deletes it when the last device is removed, so line-count accounting must remain balanced on all probe failures. Ranchu DMA mode assumes 32-bit DMA addressing and splits transfers at page boundaries. `goldfish_tty_chars_in_buffer` returns `BYTES_READY`, which is receive-side device state rather than pending TX bytes. The reported maximum write room is a fixed large value because the emulator accepts command-buffer writes. Console writes depend on the per-line device already being probed unless earlycon is used.

## Test Signals

Useful signals include Goldfish/Ranchu boot with `ttyGF*` devices; IRQ-driven input into the TTY flip buffer; writes in legacy version 0 and DMA version > 0 modes; DMA mapping failure handling; console registration per probed line; earlycon output for `google,goldfish-tty`; probe failure unwinding for IRQ, DMA mask, and TTY registration errors; and remove/unregister behavior across multiple lines.
