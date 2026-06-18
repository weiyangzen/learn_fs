# sources/distributed-fs/ceph-client/drivers/tty/serial/xilinx_uartps.c

## Purpose

`xilinx_uartps.c` is the Cadence UART driver used by Xilinx Zynq/ZynqMP and compatible Cadence UART instances. It exposes dynamic-major `ttyPS` ports, supports console and earlycon output, runtime/system PM, clock rate change notifiers, reset controls, modem control, optional GPIO RTS, RS485 timing, RX byte-status quirks, and OF platform binding. The file was read as a complete 1924-line source file.

## Important APIs, Types, and Functions

`struct cdns_uart` stores the serial port pointer, UART/APB clocks, current baud, clock notifier, quirk flags, CTS override, optional RTS GPIO, RS485 state/timer, and reset controller. `struct cdns_platform_data` carries quirk flags, and `cdns_rs485_supported` advertises supported RS485 flags/delays. The serial-core table `cdns_uart_ops` covers modem control, TX/RX control, termios, startup/shutdown, PM, resource mapping, verification, and polling. Important runtime functions include `cdns_uart_handle_rx()`, `cdns_uart_handle_tx()`, `cdns_uart_isr()`, `cdns_uart_calc_baud_divs()`, `cdns_uart_set_baud_rate()`, `cdns_uart_clk_notifier_cb()`, `cdns_uart_start_tx()`, `cdns_uart_set_termios()`, `cdns_uart_startup()`, `cdns_uart_shutdown()`, `cdns_rs485_config()`, `cdns_uart_probe()`, and `cdns_uart_remove()`.

## Control Flow

The platform driver is registered at `arch_initcall()`. Probe allocates private data and a `uart_port`, chooses a line from the `serial` alias, lazily registers the global `uart_driver` on the first instance, reads quirk data, obtains clocks and optional reset control, enables clocks, maps resources, registers a clock notifier, initializes serial-core fields, gets RS485 mode and optional RTS GPIO, enables runtime PM and wakeup, assigns console state when needed, adds the port, and increments the instance count. Startup deasserts reset, disables and resets TX/RX, initializes RS485 receive state if enabled, enables RX, sets default mode, programs RX watermark and timeout, clears pending interrupts, requests IRQ, and enables RX interrupts plus break support where available. The ISR clears pending interrupts, handles TX-empty first, filters RX status through masks, and drains RX unless RX is disabled. TX starts by enabling the transmitter, respecting RS485 pre-send delay if configured, and filling FIFO until full. Shutdown cancels RS485 timers, disables interrupts and TX/RX, and frees the IRQ.

## State and Persistence Behavior

Driver state persists in `struct cdns_uart`, the allocated `uart_port`, static `instances`, and optional static `console_port`. Hardware state includes CR/MR, baud generator/divider, RX timeout/watermark, modem control/status, interrupt mask/status, and reset state. `cdns_uart->baud` tracks the requested/current baud so clock notifier callbacks can reject impossible new rates or reprogram divisors after rate changes. Runtime PM autosuspends clocks; system PM has special console-wakeup paths that change RX trigger and timeout behavior. RS485 state persists in `port->rs485`, `rs485_tx_started`, and a high-resolution timer.

## Dependencies and Integration Points

The driver depends on platform/OF devices, serial core, tty flip buffers, Linux clocks and clock notifiers, runtime PM, reset controls, GPIO descriptors, hrtimers, earlycon, console, and optional console-poll. It binds `xlnx,xuartps`, `cdns,uart-r1p8`, `cdns,uart-r1p12`, and `xlnx,zynqmp-uart`; the latter two enable RX byte-status support. It exposes RS485 through serial core and can consume DT properties such as `cts-override`, RS485 mode, and `rts-gpios`.

## Risks and Edge Cases

The global `instances` count is incremented only after success, so early probe failures call `uart_unregister_driver()` when `instances` is zero even if another successful instance already exists but a later probe fails before incrementing; concurrent or interleaved probes deserve scrutiny. RX handling has complex break detection split between legacy framing/all-zero inference and RXBS quirk status, with a likely typo where RXBS framing is checked against `CDNS_UART_IXR_PARITY` rather than the framing mask. `cdns_uart_set_baud_rate()` stores the requested baud, while some callers assign the returned actual baud back to `cdns_uart->baud`; this mixed meaning matters during clock-rate changes. Console write restores interrupts by writing the saved IMR mask to IER, which is correct for this hardware but can accidentally enable stale bits if IMR semantics change. RS485 uses one hrtimer for both pre- and post-send paths and requires careful cancellation during shutdown and mode changes.

## Test Signals

Recommended signals include build coverage for console, earlycon, PM, common-clk, poll-console, GPIO, RS485, and non-console builds; OF probe/remove tests across all compatibles and alias IDs; baud divisor unit tests over low/high clock rates; clock-rate notifier PRE/POST/ABORT tests; RXBS and non-RXBS error/break injection; TX/RX FIFO loopback; modem-control and `cts-override` tests; RS485 RTS timing with and without GPIO; runtime autosuspend/resume and system suspend/resume with console wakeup; and multi-instance registration/removal failure injection.
