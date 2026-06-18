# sources/distributed-fs/ceph-client/drivers/tty/serial/atmel_serial.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/tty/serial/atmel_serial.c` is the Linux serial-core driver for Atmel/Microchip AT91 USART/UART serial ports. It supports `ttyAT` or `ttyS` naming, PIO, legacy PDC, generic DMA, FIFO thresholds, modem GPIOs, RS485, ISO7816 smart-card modes, console/earlycon, wakeup, and suspend/resume. The source was read as a complete 3026-line file.

## Important APIs, Types, and Functions

`struct atmel_uart_port` is the central state object around `uart_port`, clocks, wake/suspend state, PDC buffers, DMA channels/descriptors/cookies, tasklets, RX ring, GPIO modem controls, RS485/ISO7816 backup state, FIFO metadata, hardware capability flags, timers, cached registers, and function pointers for selected RX/TX engines. Serial-core ops are `atmel_pops`. Mode configuration is handled by `atmel_config_rs485()` and `atmel_config_iso7816()`. Data paths include `atmel_rx_chars()`, `atmel_tx_chars()`, `atmel_tx_dma()`, `atmel_rx_from_dma()`, `atmel_tx_pdc()`, `atmel_rx_from_pdc()`, `atmel_rx_from_ring()`, `atmel_interrupt()`, and tasklet functions. Lifecycle paths include `atmel_serial_probe()`, `atmel_startup()`, `atmel_shutdown()`, `atmel_serial_pm()`, `atmel_serial_suspend()`, and `atmel_serial_resume()`.

## Control Flow

Probe is invoked by the AT91 USART MFD child, aliases the child OF node to its parent, chooses a line from the `serial` alias or bitmap, enables the USART clock, obtains optional generic clock, initializes the port, modem GPIOs, RX ring allocation when not using PDC RX, adds the port, enables device wakeup, applies initial RS485 RTS state if needed, reads IP name/version to discover USART/UART capabilities, then disables the peripheral clock until open.

Startup masks all interrupts, requests a shared conditional-suspend IRQ, initializes tasklets, rereads DMA/PDC properties, selects engine callbacks, prepares RX/TX DMA or PDC resources with fallback to PIO, enables FIFO and thresholds if present, snapshots modem status, resets status/RX, enables TX/RX, sets up the timeout timer, and enables either RXRDY, PDC ENDRX/TIMEOUT, or DMA TIMEOUT interrupts. The ISR loops up to `ATMEL_ISR_PASS_LIMIT`, reading CSR and IMR. If suspended, it records pending bits, masks interrupts, and triggers system wakeup. Otherwise it dispatches receive, modem/status, and transmit handling. Heavy RX/TX movement is usually deferred to tasklets.

PIO RX buffers status+char pairs into a 1024-entry ring and schedules the RX tasklet, which classifies errors, handles break/sysrq, inserts chars, and pushes TTY data. DMA RX uses a cyclic DMA buffer and residue tracking on timeout/tasklet callbacks. PDC RX uses two 512-byte buffers and requeues full buffers. PIO TX uses `uart_port_tx()`, generic DMA TX maps the serial-core xmit buffer and submits scatterlist segments, and PDC TX programs TPR/TCR from the linear xmit tail. Half-duplex RS485/ISO7816 paths stop RX while transmitting and restart RX after TX completion.

Termios rebuilds the mode register for USART or UART IP, programs data bits, stop bits, parity including mark/space, RS485/ISO7816/HWHS mode, baud divisors with optional fractional baud and optional generic clock selection, read/ignore masks, modem status interrupts, and TX/RX enable state. PM callbacks save/restore interrupt masks and clocks; system suspend caches console registers when console suspend is disabled and preserves pending wake interrupts when slow clock disables UART wake.

## State and Persistence Behavior

Runtime state is static in `atmel_ports[]` plus `atmel_ports_in_use`, per-port DMA/PDC buffers, RX ring memory, tasklets/timers, cached register values, clock state, GPIO state, and hardware registers. There is no file-backed persistence. Register caches survive suspend for no-console-suspend paths, and `backup_mode`/`backup_brgr` preserve RS232 configuration across ISO7816 mode.

## Dependencies and Integration Points

The driver depends on serial core, TTY flip buffers, AT91 USART MFD/platform devices, OF aliases/properties, DMAengine, legacy Atmel PDC registers, clocks and optional generic clock, suspend APIs, GPIO modem-control helpers, console/earlycon, and register definitions from `atmel_serial.h`. It is initialized with `device_initcall()` after registering `atmel_uart`.

## Risks and Edge Cases

The largest risks are mode switching among PIO/PDC/DMA, DMA residue and circular-buffer accounting, tasklet shutdown races, suspended interrupt capture/replay, half-duplex RX restart timing, generic clock baud selection error handling, and ISO7816 validation/restoration. PDC RX error handling is explicitly incomplete. CREAD ignore-all is noted as TODO. Probe relies on parent resources and parent OF nodes, so MFD binding shape matters. FIFO RTS thresholds are derived heuristically from FIFO size.

## Test Signals

Important signals include probe through the AT91 USART MFD, PIO/PDC/DMA RX and TX transfers, fallback when DMA channels fail, RX timeout behavior with/without hardware timers, FIFO threshold programming, RS485 half/full-duplex behavior, ISO7816 T=0/T=1 validation and restore, modem GPIO and hardware modem interrupts, console and earlycon output, suspend/resume with console suspend enabled/disabled, wake from serial while slow clock is active, and unbind/rebind cleanup.
