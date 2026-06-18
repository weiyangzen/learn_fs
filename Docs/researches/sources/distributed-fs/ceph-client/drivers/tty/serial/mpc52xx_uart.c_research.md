# sources/distributed-fs/ceph-client/drivers/tty/serial/mpc52xx_uart.c

## Purpose

`mpc52xx_uart.c` is the Linux serial-core driver for Freescale/NXP MPC52xx and MPC512x PSC blocks when configured as UARTs. It registers `ttyPSC` ports on major 204/minor 148, supports an optional boot/normal console, and adapts one UART implementation across MPC5200, MPC5200B, MPC5121, and MPC5125-compatible PSC register/FIFO variants.

The driver is not Ceph-specific; in this source tree it is a kernel serial driver dependency that exposes hardware UARTs as tty devices. Its core role is to translate serial-core callbacks into PSC register writes, FIFO operations, interrupt handling, modem-status reporting, baud programming, and OF platform probing.

## Important APIs, Types, And Functions

The central abstraction is `struct psc_ops`, a per-SoC vtable for FIFO setup, readiness tests, TX/RX interrupt masking, byte IO, console interrupt save/restore, baud programming, clock management, FIFOC lifecycle, IRQ selection, and basic PSC register access. The global `psc_ops` pointer is selected from the OF match table data during device-tree enumeration.

Important state includes `mpc52xx_uart_ports[MPC52xx_PSC_MAXNUM]`, the static `uart_port` array; `mpc52xx_uart_nodes[]`, the OF node-to-line lookup table; `port->read_status_mask`, which is also used as an interrupt-mask shadow for MPC52xx and as packed FIFO interrupt masks for MPC512x console writes; and global MPC512x FIFOC resources `psc_fifoc`, `psc_fifoc_irq`, `psc_fifoc_clk`.

Variant operations include `mpc52xx_psc_ops` and `mpc5200b_psc_ops` for native 52xx FIFOs; `mpc512x_psc_ops` for MPC5121 with a shared PSC FIFO controller; and `mpc5125_psc_ops` for MPC5125 register layout differences. The baud paths are `mpc5200_psc_set_baudrate()`, `mpc5200b_psc_set_baudrate()`, `mpc512x_psc_set_baudrate()`, and `mpc5125_psc_set_baudrate()`, each encoding hardware-specific prescaler assumptions.

The serial-core operations are collected in `mpc52xx_uart_ops`: `tx_empty`, modem control, TX/RX start/stop, `enable_ms`, break control, startup/shutdown, termios, port request/release/config/verify. Console support is implemented by `mpc52xx_console_write()`, `mpc52xx_console_setup()`, and `mpc52xx_console_init()` when `CONFIG_SERIAL_MPC52xx_CONSOLE` is enabled.

Interrupt processing is split into `mpc52xx_uart_int()`, the IRQ entry with the port lock held; SoC-specific `psc_ops->handle_irq()`; common `mpc5xxx_uart_process_int()`; and helper loops `mpc52xx_uart_int_rx_chars()` and `mpc52xx_uart_int_tx_chars()`.

## Control Flow

Initialization enters `mpc52xx_uart_init()`, registers the `uart_driver`, enumerates matching OF nodes, optionally initializes the MPC512x FIFOC, and registers the platform driver. `mpc52xx_uart_of_enumerate()` scans all matching nodes, updates global `psc_ops` from the match data, and assigns each node to the first free `ttyPSC` index. Probe later confirms the node was enumerated, fills the static `uart_port`, gets bus frequency and resource address, asks `psc_ops->get_irq()` for the IRQ wiring, and calls `uart_add_one_port()`.

Startup enables variant clocks when provided, requests the IRQ, resets RX/TX, delays after TX reset to avoid a documented TX-pin spike, puts the PSC in UART mode, initializes the FIFO, and enables TX/RX. Shutdown resets RX and, unless the port is a console, TX, clears interrupt masks, disables clocks, disables console-write interrupts, and frees the IRQ.

RX interrupt flow repeatedly drains bytes while `raw_rx_rdy()` reports data. Each byte is passed through sysrq handling, annotated with break/parity/frame/overrun status from `get_status()`, then pushed into the tty flip buffer. TX flow uses `uart_port_tx()` while `raw_tx_rdy()` permits writes. The common interrupt loop also handles DCD/CTS deltas through `uart_handle_dcd_change()` and `uart_handle_cts_change()` and is bounded by `ISR_PASS_LIMIT` to avoid an infinite interrupt loop.

Termios changes build PSC mode register values for word size, parity, stop bits, and CRTSCTS; wait for TX to empty up to a finite count; reset RX/TX; write mode and baud; update serial-core timeout; optionally enable modem-status interrupts; then re-enable TX/RX. Console writes disable PSC interrupts through the variant `cw_disable_ints()`, poll for transmit completion, write CRLF-expanded bytes, and restore the saved interrupt state.

## State And Persistence Behavior

Persistent runtime state is kernel-resident only. There is no disk persistence. Static arrays preserve port objects and OF line assignments for the lifetime of the module. `read_status_mask` persists across normal operation and is intentionally reused as an IMR shadow, so interrupt mask changes and status filtering are coupled. MPC512x clock pointers are kept in arrays indexed from the PSC number derived from `mapbase`.

Console setup can pre-map and partially initialize a port before normal platform probe. Probe respects that by omitting `UPF_IOREMAP` for console ports. Shutdown preserves TX on console ports so console output remains possible.

## Dependencies And Integration Points

The driver depends on Linux serial core, tty flip buffers, sysrq, console infrastructure, OF address/IRQ helpers, platform devices, common clock APIs, and PowerPC-specific `asm/mpc52xx*.h` register definitions. Device-tree compatible strings are the contract for selecting the correct `psc_ops`.

It integrates with the serial core through `uart_register_driver()`, `uart_add_one_port()`, `uart_suspend_port()`, `uart_resume_port()`, and console registration. MPC512x integrates with a shared `"fsl,mpc5121-psc-fifo"` node and its shared interrupt, so FIFO-controller availability is a prerequisite for those variants.

## Risks And Edge Cases

The global `psc_ops` assumes all enumerated PSC UART nodes in the running kernel use compatible operation semantics; mixed compatible variants could be fragile because the last enumerated match overwrites the global pointer used by all ports.

The file header calls out a possible status-register race where PSC status bits may not update on CPU FIFO access. The implementation relies on those bits for RX/TX loop decisions.

`mpc52xx_uart_shutdown()` disables clocks before `cw_disable_ints()` and `free_irq()`, so any change to clock gating semantics should verify register access remains valid. MPC512x FIFOC handling is shared and uses bit positions derived from `mapbase`; incorrect resources can route or filter interrupts incorrectly.

Termios reconfiguration resets FIFOs and can lose data if TX does not drain before the finite timeout. The code also leaves an old commented-out RX drain because early-console termios could oops if RX were processed too early.

## Test Signals

Useful validation includes booting with `console=ttyPSC<n>` and verifying early and normal console output, probing all supported compatible strings, exercising baud changes across low and high rates for each prescaler path, RX/TX flood tests with sysrq and break injection, CTS/DCD transition tests, suspend/resume for platform PM, and MPC512x shared-FIFOC interrupt tests with multiple PSC ports active.

Static review should check OF aliases against `mpc52xx_uart_nodes[]`, ensure `port->read_status_mask` transitions match expected IMR bits, and verify module unload frees FIFOC, clocks, IRQs, and mappings in the right order for non-console and console ports.
