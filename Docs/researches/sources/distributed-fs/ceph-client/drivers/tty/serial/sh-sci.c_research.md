# sources/distributed-fs/ceph-client/drivers/tty/serial/sh-sci.c

## Purpose

`sh-sci.c` is the main SuperH/Renesas SCI-family serial driver. It supports legacy SCI, SCIF, SCIFA, SCIFB, HSCIF, RZ SCIFA-like variants, RZ/V2H SCIF, optional RSCI integration, platform data, device tree, console, earlyprintk, earlycon, GPIO modem control, runtime PM, reset control, sysfs FIFO tuning, and optional DMA. The source was read as a complete 4136-line file.

## Important APIs, Types, and Functions

The top of the file defines the common register enum (`SCSMR`, `SCBRR`, `SCSCR`, `SCxSR`, FIFO/data/count/status registers, BRG registers, HSCIF trigger registers, `SEMR`) and many bit definitions for line format, status/error clear masks, FIFO control, pin control, BRG clock select, and sampling rates. `sci_port_params[]` maps each register layout to offsets, access widths, FIFO sizes, overrun/error masks, and sampling-rate support.

Core hardware helpers include `sci_serial_in()`, `sci_serial_out()`, `sci_clear_SCxSR()`, `sci_txfill()`, `sci_txroom()`, `sci_rxfill()`, `sci_reset()`, `sci_sck_calc()`, `sci_brg_calc()`, and exported `sci_scbrr_calc()`. UART operations are collected in `sci_uart_ops`, while SCI-internal operations are collected in `sci_port_ops`. Major paths include `sci_start_tx()`, `sci_stop_tx()`, `sci_start_rx()`, `sci_stop_rx()`, `sci_transmit_chars()`, `sci_receive_chars()`, `sci_handle_errors()`, `sci_handle_fifo_overrun()`, `sci_handle_breaks()`, split/muxed IRQ handlers, DMA helpers, modem-control helpers, `sci_startup()`, `sci_shutdown()`, `sci_set_termios()`, probe helpers, console callbacks, PM callbacks, and earlycon setup functions.

## Control Flow

Platform driver init registers `sci_driver`; per-device probe parses either OF data (`sci_parse_dt()`) or platform data, picks a `sci_port` slot, allocates suspend-register storage, handles earlycon alias conflicts, initializes clocks/IRQs/register maps in `sci_init_single()`, initializes modem GPIOs, and registers the port with `uart_add_one_port()`. The UART driver itself is lazily registered under `sci_uart_registration_lock` the first time a port probes. FIFO sysfs attributes are created for ports with FIFO depth greater than one.

Startup requests DMA when configured, then requests either split IRQs or a muxed IRQ. RX interrupts optionally switch to DMA or arm a FIFO timeout timer before calling the configured `receive_chars()`. TX interrupts call `transmit_chars()` under the port lock. Error, break, transmit-end, overrun, and muxed handlers inspect status/control registers, call the appropriate helpers, clear hardware bits using the register-type-specific clear semantics, and may kick TX after errors. Shutdown disables modem-status GPIO monitoring, stops RX/TX, calls the type-specific shutdown completion hook, deletes RX timers, frees IRQs, and releases DMA.

Termios setup computes the best baud source across optional external SCK, BRG external/internal clocks, and functional clock divisors. It enables clocks/runtime PM while programming, resets FIFOs/status, writes BRG and sampling registers, sets frame format, updates UART timeout, initializes pins, configures auto RTS/CTS, enables TX/RX bits, accounts for SCIFA/SCIFB 1/5 sampling delays, computes RX frame timing for DMA/timeouts, starts RX when `CREAD` is set, disables clocks again, and enables modem status if needed.

## State and Persistence Behavior

Static state includes `sci_ports[SCI_NPORTS]`, `sci_ports_in_use`, `sci_uart_driver`, and earlycon booleans. Per-port state in `struct sci_port` persists across open/close and PM and tracks params, platform config, register size, clocks and cached rates, IRQs and names, GPIO modem control, DMA channels/cookies/buffers/work/timers, RX FIFO trigger/timeout, HSCIF timeout bits, type/regtype, ops, RTS/CTS mode, and whether TX occurred. Suspend may either save console registers when console suspend is disabled or assert reset; resume restores registers or deasserts reset before `uart_resume_port()`. No file-backed state exists, but sysfs attributes mutate live RX trigger/timeout configuration.

## Dependencies and Integration Points

The file integrates with serial core, tty flip buffers, console and earlycon, platform devices, OF match data, clocks, runtime PM, reset control, DMA engine, scatterlists, hrtimers, classic timers, GPIO modem control via `serial_mctrl_gpio.h`, SuperH early platform and BIOS hooks, and optional RSCI data from `rsci.h`. OF compatibles include generic Renesas SCI/SCIF/SCIFA/SCIFB/HSCIF, R-Car generations, RZ/RZV2H variants, and optional RSCI SoCs. Exported helpers in namespace `"SH_SCI"` are integration points for related SCI-family modules.

## Risks and Edge Cases

The highest-risk areas are register-layout differences and status-clear semantics across SCI, SCIF, SCIFA/B, HSCIF, RZ variants, and RSCI. DMA paths must correctly fall back to PIO on descriptor failures, avoid DMA on console ports, and coordinate RX hrtimer timeout with IRQ reenablement. Muxed IRQ detection, repeated IRQ numbers, and partial IRQ resources require careful request/free symmetry. Termios programming temporarily enables clocks and runtime PM, so clock availability and earlyprintk with `uartclk == 0` are special cases. Earlycon occupies `sci_ports[0]` and has explicit alias conflict handling. Sysfs FIFO trigger changes can interact with active RX timeout timers. Reset-control suspend differs for live consoles when console suspend is disabled.

## Test Signals

Strong signals include boot/probe for representative SCI, SCIF, SCIFA, SCIFB, HSCIF, RZ SCIFA, RZ/V2H, and RSCI nodes; split and muxed IRQ configurations; PIO and DMA TX/RX including DMA descriptor failure fallback; console and earlycon handoff with `keep_bootcon`; sysfs `rx_fifo_trigger` and `rx_fifo_timeout`; `CRTSCTS` with GPIO and hardware RTS/CTS; break/parity/frame/overrun injection; runtime PM and system suspend/resume with and without console suspend; reset controller failures; and clock-source combinations covering SCK, BRG, and functional clock divisor paths.
