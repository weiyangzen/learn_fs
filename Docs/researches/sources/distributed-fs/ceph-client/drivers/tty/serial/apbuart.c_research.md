# sources/distributed-fs/ceph-client/drivers/tty/serial/apbuart.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/tty/serial/apbuart.c` is the serial-core driver for Aeroflex/Gaisler GRLIB APBUART devices found through Open Firmware device nodes. It exposes up to eight `ttyS` ports using APBUART-specific data, status, control, and scaler registers. The source was read as a complete 662-line file.

## Important APIs, Types, and Functions

The driver uses static `grlib_apbuart_ports[]` and `grlib_apbuart_nodes[]` arrays sized by `UART_NR` from `apbuart.h`. Its serial-core operation table is `grlib_apbuart_ops`, implemented by `apbuart_startup()`, `apbuart_shutdown()`, `apbuart_set_termios()`, RX/TX start/stop helpers, modem stubs, and request/config/verify helpers. Runtime handlers are `apbuart_rx_chars()`, `apbuart_tx_chars()`, and `apbuart_int()`. Discovery and binding are split between `grlib_apbuart_configure()`, `apbuart_probe()`, `grlib_apbuart_init()`, and the optional console init path.

## Control Flow

`grlib_apbuart_configure()` scans matching OF nodes named `GAISLER_APBUART` or `01_00c`, skips nodes marked `ampopts = 0`, reads `reg` and `freq`, maps the register block, initializes the `uart_port`, detects FIFO size by temporarily enabling/disabling the transmitter and writing test bytes, and records the node-to-line mapping. Module init configures ports, registers the UART driver, then registers the OF platform driver. Platform probe matches the device node back to the preconfigured line, fills `dev` and IRQ, adds the port, flushes stale FIFO contents, and logs the address.

Startup requests the IRQ and enables receiver, transmitter, RX interrupt, and TX interrupt bits in the APBUART control register. IRQ handling locks the port, checks data-ready and TX-hold-empty bits, drains RX, and transmits pending data. RX loops up to `port->fifosize`, clears status by writing zero, accounts break/parity/frame/overrun errors, applies read/ignore masks and sysrq, then pushes the TTY flip buffer. TX uses `uart_port_tx_limited()` with the FIFO size. Termios computes APBUART's scaler from the serial-core divisor, applies parity and CRTSCTS hardware flow-control bits, updates masks and timeout, then writes scaler and control.

## State and Persistence Behavior

State is static for the module lifetime: configured ports, matching OF nodes, `grlib_apbuart_port_nr`, and UART registers. There is no dynamic per-device allocation in probe and no file persistence. Console setup can run early and calls `grlib_apbuart_configure()` before normal driver init, so configuration must be idempotent enough for both paths.

## Dependencies and Integration Points

The file depends on `apbuart.h` for register layout/macros, Linux OF/platform APIs, serial core, TTY flip buffers, sysrq, and SPARC/LEON style `op->archdata.irqs[0]` IRQ plumbing. Console support is gated by `CONFIG_SERIAL_GRLIB_GAISLER_APBUART_CONSOLE`.

## Risks and Edge Cases

The driver performs manual OF property parsing using APBUART-specific `struct amba_prom_registers`; malformed `reg` or `freq` properties skip ports. FIFO probing writes bytes while interrupts are locally disabled and assumes the disabled transmitter will not leak data externally. `apbuart_request_port()` has an unreachable second `return 0`. Verify uses `NR_IRQS` rather than `irq_get_nr_irqs()`. The console option reader appears to check parity bits against `status` rather than `ctrl`, which is worth regression attention.

## Test Signals

Key tests include OF scan ordering, `ampopts` exclusion, FIFO-size detection on FIFO and non-FIFO hardware, interrupt RX/TX loopback, parity/frame/overrun handling, CRTSCTS control-bit programming, console boot output, invalid/missing `freq` and `reg` properties, multiport registration/removal, and stale FIFO flush after probe.
