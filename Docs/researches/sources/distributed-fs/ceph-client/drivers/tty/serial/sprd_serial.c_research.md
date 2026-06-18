# sources/distributed-fs/ceph-client/drivers/tty/serial/sprd_serial.c

## Purpose

`sprd_serial.c` is the Spreadtrum/Unisoc SoC UART serial driver. It supports up to eight `ttyS` ports, memory-mapped FIFO registers, configurable line format and hardware flow control, loopback through modem control, optional TX/RX DMA, console, earlycon, console polling, OF match data for different timeout interrupt bits, and PM clock gating. The source was read as a complete 1306-line file.

## Important APIs, Types, and Functions

The file defines `SPRD_*` register offsets and masks for TX/RX data, line status, FIFO counts, interrupt enable/clear/masked status, line control, control registers, FIFO thresholds, baud divisors, and DMA settings. `struct sprd_uart_dma` tracks a DMA channel, coherent/physical buffers, cookie, transfer length, and enable state. `struct sprd_uart_data` abstracts SoC-specific timeout interrupt enable/clear/status bits. `struct sprd_uart_port` embeds `struct uart_port` and stores a name, clock, TX/RX DMA state, current RX DMA position, RX tail pointer, and match data.

Key functions include PIO helpers `serial_in()`/`serial_out()`, DMA helpers `sprd_request_dma()`, `sprd_release_dma()`, `sprd_tx_buf_remap()`, `sprd_tx_dma_config()`, `sprd_start_tx_dma()`, `sprd_stop_tx_dma()`, `sprd_rx_alloc_buf()`, `sprd_start_dma_rx()`, `sprd_uart_dma_irq()`, and completion callbacks. UART operations are collected in `serial_sprd_ops`, with startup/shutdown in `sprd_startup()` and `sprd_shutdown()`, IRQ handling in `sprd_handle_irq()`, termios in `sprd_set_termios()`, console in `sprd_console_*`, and platform integration in `sprd_probe()`/`sprd_remove()`.

## Control Flow

Probe reads the `serial` alias, allocates a port, initializes serial-core fields, initializes clocks, maps MMIO, reads OF match data, gets IRQ, preallocates an RX DMA buffer, lazily registers the shared UART driver, stores the port in `sprd_port[]`, and adds the UART port. Startup sets FIFO thresholds, drains RX and TX FIFOs, clears interrupts, requests DMA channels and starts RX DMA when available, requests a shared IRQ with devm, programs timeout/flow thresholds, and enables break/timeout/RX interrupts depending on DMA mode.

In PIO mode the IRQ handler reads masked status, clears timeout and break sources, calls `sprd_rx()` for RX-full/break/timeout, and calls `sprd_tx()` on TX-empty. `sprd_rx()` loops while RX FIFO count is nonzero, reads LSR and RXD, updates error counts and sysrq/break handling, inserts chars into tty flip buffers, and pushes. `sprd_tx()` uses `uart_port_tx_limited()` up to the TX threshold. In DMA mode, start TX maps the linear portion of the UART xmit FIFO and submits a slave-single transfer; completion unmaps, advances the UART FIFO, wakes writers, and chains another transfer if data remains. RX DMA uses a coherent circular-sized buffer, data-timeout or full-completion paths compute bytes since the previous DMA position, insert them into the tty buffer, advance the software tail, and resubmit.

## State and Persistence Behavior

Global state is `sprd_port[UART_NR_MAX]` and `sprd_ports_num`, which control lazy `uart_register_driver()`/`uart_unregister_driver()`. Per-port state persists until remove and includes DMA channels, preallocated RX buffer, DMA cookies, transfer lengths, RX DMA position/tail, clock pointer, and SoC timeout-data pointer. Termios-derived `read_status_mask` and `ignore_status_mask` live in `uart_port`. No file-backed persistence exists. PM operations call `uart_suspend_port()`/`uart_resume_port()`, while UART-core PM toggles the enable clock.

## Dependencies and Integration Points

The driver integrates with serial core, tty flip buffers, console/earlycon/polling, platform devices, OF aliases and compatibles (`sprd,sc9836-uart`, `sprd,sc9632-uart`), clock framework (`uart`, `source`, and `enable` clocks), DMA engine plus Spreadtrum DMA flags, and devm IRQ/resource management. It relies on UART core helpers for baud selection, timeout updates, xmit FIFO advancement, wakeups, sysrq, and console setup.

## Risks and Edge Cases

The DMA RX accounting is subtle: it stores `sp->pos` as a DMA address and compares it with `state.residue`, which is normally a byte count, so this path needs hardware-specific validation. `sprd_stop_tx_dma()` computes `trans_len = state.residue - phys_addr`, also mixing residue and address-like values. DMA channel request failure disables the affected direction but still enables the global DMA bit if either direction works. Startup uses devm IRQ request and shutdown calls `devm_free_irq()`, which is unusual but balanced for repeated open/close. Clock init allows missing enable clock only for console ports by setting `u->clk = NULL`; PM must tolerate NULL clock calls. PIO polling waits without timeout. Baud divisor programming is integer-only and capped by `SPRD_BAUD_IO_LIMIT`.

## Test Signals

Useful tests include OF probe for both compatible data sets, missing/invalid aliases, clock fallback and console-clock-error paths, PIO RX/TX without DMA channels, TX DMA chaining and stop/flush behavior, RX DMA timeout/full-buffer accounting, break/parity/frame/overrun insertion, hardware flow control via `CRTSCTS`, loopback via `TIOCM_LOOP`, console/earlycon/poll output, suspend/resume with active console, open/close cycles to catch IRQ/DMA lifetime issues, and fault injection for DMA mapping/config/submit failures.
