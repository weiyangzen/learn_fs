# sources/distributed-fs/ceph-client/drivers/tty/serial/msm_serial.c

## Purpose

`msm_serial.c` is the Qualcomm MSM/MSM7x serial and console driver for legacy MSM UART and UARTDM hardware. It registers up to three `ttyMSM` ports, supports normal console and earlycon for `"qcom,msm-uart"` and `"qcom,msm-uartdm"`, handles UARTDM DMA when channels are present, and falls back to FIFO/PIO paths when DMA cannot be used.

The driver covers several UARTDM revisions (`UARTDM_1P1` through `UARTDM_1P4`) with different DMA enable bits and TX count behavior. It also integrates with the OPP framework to set the core clock rate used for baud generation.

## Important APIs, Types, And Functions

`struct msm_port` wraps `uart_port` with `core` and optional `iface` clocks, cached interrupt mask `imr`, UARTDM revision, RX stale snapshot state, break-detection state, and TX/RX `struct msm_dma` descriptors. `struct msm_dma` stores a DMA channel, direction, mapping state, cookie, UARTDM enable bit, and either RX buffer metadata or a TX scatterlist.

MMIO helpers are `msm_write()` and `msm_read()`. Clock and baud helpers include `msm_serial_set_mnd_regs()`, `msm_find_best_baud()`, `msm_set_baud_rate()`, and `msm_init_clock()`. DMA setup and teardown are `msm_request_tx_dma()`, `msm_request_rx_dma()`, `msm_stop_dma()`, and `msm_release_dma()`.

TX paths are `msm_start_tx()`, `msm_stop_tx()`, `msm_handle_tx()`, `msm_handle_tx_pio()`, `msm_handle_tx_dma()`, and `msm_complete_tx_dma()`. RX paths are `msm_handle_rx()` for legacy FIFO, `msm_handle_rx_dm()` for UARTDM FIFO/packing mode, `msm_start_rx_dma()`, and `msm_complete_rx_dma()`.

The main IRQ handler is `msm_uart_irq()`. Serial-core operations are in `msm_uart_pops`, including PM and optional console-poll methods. Console support is implemented by `__msm_console_write()`, `msm_console_write()`, `msm_console_setup()`, and earlycon setup for both single-byte and DM modes.

Probe and lifecycle use `msm_serial_probe()`, `msm_serial_remove()`, `msm_serial_suspend()`, `msm_serial_resume()`, `msm_serial_init()`, and `msm_serial_exit()`.

## Control Flow

Module init registers the `uart_driver`, then the platform driver. Probe selects the line from `serial` alias, platform ID, or `atomic_inc_return()`, rejects lines outside the static three-port array, determines whether the node matches a specific UARTDM revision, gets clocks, configures OPP clock naming/table, records `uartclk`, resource base, IRQ, sysrq capability, and calls `uart_add_one_port()`.

Startup enables clocks/OPP rate, programs automatic RFR level, opportunistically requests TX/RX DMA for UARTDM, then requests the IRQ. Startup does not fully program line settings; serial core subsequently calls termios, where baud, watermarks, reset, RX/TX enable, interrupt masks, and RX DMA start are configured.

The IRQ handler locks the port, snapshots `MISR`, masks interrupts, records break-start state, and dispatches RX, TX, and CTS-delta work. If RX DMA is active, an RX stale/level interrupt disables stale events, resets stale state, and terminates the DMA channel so the DMA completion callback flushes data. Otherwise UARTDM and legacy paths drain receive data synchronously. The cached `imr` is restored before unlocking and sysrq processing is finalized.

TX first handles `x_char`, then stops if the FIFO is empty or flow-controlled. It chooses a DMA count from the linear xmit FIFO, aligns/count-limits for the UARTDM revision, and uses DMA when a channel exists and the transfer is large enough; otherwise it uses PIO. DMA completion unmaps, disables the UARTDM DMA enable bit, resets TX for newer UARTDM revisions, advances the xmit FIFO by actual transferred count, restores TXLEV interrupts, wakes writers if needed, and chains into more TX work.

Termios stops active RX DMA, finds and applies an OPP-backed baud rate, programs parity/word/stop bits, hardware flow control, status masks, timeout, and restarts RX DMA if available. Shutdown masks interrupts, releases DMA, disables clocks/OPP rate, and frees the IRQ.

## State And Persistence Behavior

All state is runtime kernel state. `msm_uart_ports[]` is a static array whose entries persist across probe/remove. `msm_port->imr` is the authoritative software cache of enabled interrupts and is written repeatedly around IRQ dispatch, DMA mode switches, TX start/stop, and CTS monitoring.

DMA mapping state is implicit in `sg_dma_len(&tx_sg)` for TX and `rx.count` for RX. These fields are also used as "already active/stopped" guards in callbacks and stop paths. `old_snap_state` persists across UARTDM RXLEV/RXSTALE processing to account for packed FIFO words before stale completion. `break_detected` bridges a break-start interrupt to the following zero byte in RX data.

Clock state is managed through `dev_pm_opp_set_rate()`, `clk_prepare_enable()`, and disable calls. The core clock rate can be changed during baud selection, and `port->uartclk` is updated to the chosen rate.

## Dependencies And Integration Points

The driver depends on serial core, tty flip buffers, sysrq, console/earlycon, platform/OF, clocks, OPP, DMAengine, Qualcomm ADM DMA peripheral config, DMA mapping, wait queues for modem status, and optional console polling. Device tree provides compatible strings, resources, IRQs, clocks named `"core"` and `"iface"` for UARTDM, optional OPP tables, and optional `qcom,tx-crci`/`qcom,rx-crci`.

It integrates with `uart_suspend_port()`/`uart_resume_port()`, serial-core PM through `msm_power()`, and console polling for kgdb-like users when enabled.

## Risks And Edge Cases

`msm_shutdown()` disables only `clk` and OPP rate, while startup error handling disables both `pclk` and `clk`; UARTDM iface-clock lifetime should be reviewed against serial-core PM paths. DMA callbacks rely on mapping-state guards rather than explicit booleans, so any change to scatterlist initialization or RX count handling can cause double-unmap or missed completion bugs.

RX DMA intentionally terminates the DMA engine on stale/level interrupt to flush data; this hardware-specific behavior is timing-sensitive. `msm_stop_dma()` comments warn about DMA stalls when enqueue and flush overlap and disables UARTDM DMA before unmapping.

UARTDM break reporting is imprecise: break-start is latched separately and then associated with a zero byte. `msm_handle_rx_dm()` has a TODO for precise error reporting, and DMA RX inserts strings without per-byte parity/frame status.

Line allocation is limited to three static ports. Probe without aliases uses an atomic counter, so repeated probe/remove cycles could exhaust IDs because the counter is not decremented.

## Test Signals

Validation should include legacy `"qcom,msm-uart"` and all UARTDM compatible revisions, with and without DMA channels. Exercise RX stale handling, DMA fallback, TX DMA alignment/count limits for v1.3 versus v1.4, break and sysrq handling, CTS delta wakeups, OPP-backed baud changes, suspend/resume, console write under oops-in-progress, and console polling. Instrumentation should watch `imr`, `UARTDM_DMEN`, DMA map/unmap counts, and `old_snap_state` under high RX rates.
