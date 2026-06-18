# subset-b-005462 Research

Grouped source research for serial drivers in `sources/distributed-fs/ceph-client/drivers/tty/serial`. Each assigned source file has a marker-delimited section for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/serial_txx9.c -->
# sources/distributed-fs/ceph-client/drivers/tty/serial/serial_txx9.c

## Purpose

`serial_txx9.c` is the UART core driver for Toshiba TX39/TX49 internal SIO controllers and the TC86C001 PCI SIO. It registers a `uart_driver` named `serial_txx9`, exposes either `ttyTX` or standard `ttyS` minors depending on configuration, and supports platform-data ports, early setup, optional console/polling, suspend/resume, and optional PCI discovery. The source was read as a complete 1268-line file.

## Important APIs, Types, and Functions

The hardware contract is encoded by `TXX9_*` register offsets and status/control bit definitions for line control, interrupt control/status, FIFO control, flow control, baud generator, and TX/RX FIFOs. Low-level accessors are `sio_in()`, `sio_out()`, `sio_mask()`, `sio_set()`, and `sio_quot_set()`, with memory-mapped and `UPIO_PORT` paths.

Core UART operations are implemented by `serial_txx9_pops`: `serial_txx9_start_tx()`, `serial_txx9_stop_tx()`, `serial_txx9_stop_rx()`, `serial_txx9_tx_empty()`, `serial_txx9_get_mctrl()`, `serial_txx9_set_mctrl()`, `serial_txx9_break_ctl()`, `serial_txx9_startup()`, `serial_txx9_shutdown()`, `serial_txx9_set_termios()`, `serial_txx9_pm()`, resource methods, and optional poll methods. Runtime registration flows through `early_serial_txx9_setup()`, `serial_txx9_register_port()`, `serial_txx9_unregister_port()`, `serial_txx9_probe()`, `serial_txx9_remove()`, PCI `pciserial_txx9_init_one()`, and module `serial_txx9_init()`/`serial_txx9_exit()`.

## Control Flow

Module init registers the UART driver, creates a synthetic platform device, registers any statically initialized ports, binds the platform driver, and optionally registers the PCI driver. Platform probe consumes an array of `struct uart_port` platform data until `uartclk == 0`, copies each template into an unused or matching slot in `serial_txx9_ports[]`, and calls `uart_add_one_port()`. PCI probe enables the device, creates a port with `UPIO_PORT`, a fixed 66.67 MHz clock, and CTS capability, then registers it through the same helper.

`serial_txx9_startup()` resets FIFOs, clears interrupt status, requests a shared IRQ, restores modem control, enables RX/TX, and enables receive interrupts. The interrupt handler loops under `PASS_LIMIT`, locks the port, reads `SIDISR`, suppresses TX status if TX interrupts are disabled, services RX with `receive_chars()`, services TX with `transmit_chars()`, clears interrupt bits, and stops when no relevant status remains. RX drains the FIFO until `UVALID` indicates no valid data or the software count expires, updates `icount`, handles break/sysrq/parity/frame/overrun, inserts tty chars, and pushes the flip buffer. TX uses `uart_port_tx_limited()` to move up to the TX FIFO depth.

`serial_txx9_set_termios()` coerces unsupported formats to 8-bit data, disables unsupported modem semantics, computes the baud divisor, builds `read_status_mask` and `ignore_status_mask`, toggles hardware RTS/CTS support only when `CRTSCTS` and `UPF_TXX9_HAVE_CTS_LINE` are present, writes line control, baud generator, FIFO control, and modem state under the port lock. Console and polling paths temporarily disable interrupts, wait for transmitter status, write directly to `SITFIFO`, and restore saved interrupt/flow-control state.

## State and Persistence Behavior

Persistent driver state is in the static `serial_txx9_ports[UART_NR]`, `serial_txx9_reg`, the synthetic `serial_txx9_plat_devs`, and, when PCI is enabled, per-device PCI driver data pointing at a registered `uart_port`. Port hardware state lives in MMIO or I/O registers. There is no file-backed persistence. Runtime state includes UART core FIFOs and termios-derived masks, `up->mctrl`, `up->flags` feature bits, IRQ ownership, resource mappings, and console index state. Suspend/resume delegates to `uart_suspend_port()`/`uart_resume_port()`, while `serial_txx9_pm()` reinitializes hardware only when transitioning back on from a real low-power state, not during initial `uart_configure_port()`.

## Dependencies and Integration Points

The driver integrates with Linux serial core, tty flip buffers, console and console-poll subsystems, platform devices, optional PCI, resource reservation, raw I/O accessors, and `asm/txx9/generic.h`. It depends on platform data providing valid `uart_port` templates and on optional PCI IDs for TC86C001. It uses `uart_handle_break()`, `uart_handle_sysrq_char()`, `uart_get_baud_rate()`, `uart_get_divisor()`, `uart_update_timeout()`, and `uart_console_write()` to stay aligned with UART core behavior.

## Risks and Edge Cases

The RX overrun path temporarily adds `RFDN_MASK` to `ignore_status_mask` to discard the next buffered character, so changes to error handling can easily alter raw-mode behavior. `serial_txx9_config_port()` returns without releasing resources for the active console path after `request_resource()`, matching console expectations but making resource lifetime subtle. Console and poll paths disable interrupts and can busy-wait up to 1 second for flow control. The initialization path contains a TX4925 bus-error workaround after soft reset. PCI and platform registrations share static slots, so matching/unregistering must preserve line ownership and avoid stale `dev` pointers. `serial_txx9_stop_rx()` only updates the read mask rather than disabling hardware receive interrupts.

## Test Signals

Useful validation signals are boot/probe with platform-data ports and TC86C001 PCI, console boot with `CONFIG_SERIAL_TXX9_CONSOLE`, `CONFIG_CONSOLE_POLL` kgdb-style polling, RX error injection for break/parity/frame/overrun, `CRTSCTS` with and without `UPF_TXX9_HAVE_CTS_LINE`, suspend/resume on console and non-console ports, module unload after PCI and platform registration, failed IRQ/resource allocation, and high-throughput TX/RX confirming no `PASS_LIMIT` livelock.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/serial_txx9.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/sh-sci-common.h -->
# sources/distributed-fs/ceph-client/drivers/tty/serial/sh-sci-common.h

## Purpose

`sh-sci-common.h` is the shared private contract for the SuperH/Renesas SCI, SCIF, SCIFA, SCIFB, HSCIF, and RSCI serial implementations. It defines port type identifiers, clock and IRQ indexing, shared register-description structures, the `struct sci_port` extension of `struct uart_port`, operation tables, OF match payloads, exported helper prototypes, and early-console setup declarations. The source was read as a complete 184-line file.

## Important APIs, Types, and Functions

Important constants include private `enum SCI_PORT_TYPE` values for RSCI variants, `enum SCI_CLKS` clock indexes, `SCIx_*_IRQ` offsets, `SCI_SR()` and `SCI_SR_RANGE()` sampling-rate masks, and `SCI_NR_REGS`. `struct plat_sci_reg` describes per-register offset and access width. `struct sci_port_params_bits`, `struct sci_common_regs`, and `struct sci_port_params` describe type-specific enable bits, common register indexes, FIFO size, overrun/error behavior, and sampling-rate support.

`struct sci_port_ops` is the internal polymorphic interface for reading/writing registers, clearing status, TX/RX character movement, polling, RX trigger configuration, shutdown completion, console save/restore, and suspend-register sizing. `struct sci_of_data` is the OF match payload that selects params and operations. `struct sci_port` carries platform config, clocks, IRQ arrays, GPIO modem control, reset control, suspend save area, optional DMA channels/cookies/buffers/work/timers, RX FIFO tuning, type/regtype, and flow-control booleans. Public helpers declared here include `sci_startup()`, `sci_shutdown()`, resource helpers, PM helper, `sci_port_enable()`, `sci_port_disable()`, and `sci_scbrr_calc()`.

## Control Flow

This header has no executable control flow, but it defines the call graph shape used by `sh-sci.c` and RSCI support. Platform or OF probe fills a `struct sci_port` with params, ops, register type, IRQs, clocks, and flags. UART core operations call the helpers declared here, and the helpers dispatch through `sci_port_ops` where type-specific behavior is needed. Earlycon setup is conditionally exported through `scix_early_console_setup()`.

## State and Persistence Behavior

No storage is allocated by the header, but it defines all per-port runtime state for the SCI family. State includes clock handles/rates, IRQ names and numbers, DMA cookies and buffers, RX trigger/timeouts, saved suspend registers, GPIO modem control, reset control, and booleans such as `has_rtscts`, `autorts`, and `tx_occurred`. This state persists for the lifetime of each registered platform device and is reset or restored by the implementation during probe, shutdown, PM, and console handoff.

## Dependencies and Integration Points

The header includes `linux/serial_core.h` and assumes definitions from `linux/serial_sci.h`, DMA engine types, reset control, clocks, timers, and GPIO modem control are available to implementation users. It is consumed by `sh-sci.c` and by RSCI-related code included through `rsci.h`. The exported namespace `"SH_SCI"` lets related modules share the common helpers without exposing a generic user-space ABI.

## Risks and Edge Cases

Because this header is the internal ABI between SCI-family implementations, field ordering and semantic changes can break RSCI or OF data users. Register descriptors must match the hardware access width; a bad `.size` causes warning paths or wrong MMIO accesses. The private RSCI type IDs intentionally overlap generic UART type space using `BIT(7)`, so callers must use `SCI_PUBLIC_PORT_ID()` style translation before exposing port type to serial core. Optional DMA fields are present only under `CONFIG_SERIAL_SH_SCI_DMA`, so shared code must keep conditional layout and helper assumptions consistent.

## Test Signals

Compile tests with and without `CONFIG_SERIAL_SH_SCI_DMA`, `CONFIG_SERIAL_SH_SCI_EARLYCON`, and `CONFIG_SERIAL_RSCI` are essential. Probe tests for SCI, SCIF, HSCIF, and RSCI-compatible nodes should confirm `sci_of_data` to `sci_port` initialization. Namespace export users should link cleanly, and suspend/resume/earlycon tests should confirm the ops table contract is complete for every registered port family.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/sh-sci-common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/sh-sci.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/sh-sci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/sifive.c -->
# sources/distributed-fs/ceph-client/drivers/tty/serial/sifive.c

## Purpose

`sifive.c` is the serial-core driver for SiFive UART v0 hardware, which is not 8250-compatible and intentionally supports a small feature set: 8-bit characters, configurable stop bits, RX/TX FIFO watermarks, console, earlycon, console polling, clock-rate notification, and platform/OF probing. It registers `ttySIF` ports through a `sifive-serial` UART driver. The source was read as a complete 1150-line file.

## Important APIs, Types, and Functions

The register contract is defined by `SIFIVE_SERIAL_*` offsets and masks for `TXDATA`, `RXDATA`, `TXCTRL`, `RXCTRL`, interrupt enable/pending, and divisor registers. `struct sifive_serial_port` embeds `struct uart_port` and adds a device pointer, a shadow interrupt-enable byte `ier`, current `baud_rate`, clock handle, clock notifier, and console line-ended state.

Low-level helpers are `__ssp_early_readl()`, `__ssp_early_writel()`, `__ssp_readl()`, `__ssp_writel()`, `sifive_serial_is_txfifo_full()`, `__ssp_transmit_char()`, `__ssp_transmit_chars()`, RX/TX watermark enable/disable helpers, `__ssp_receive_char()`, `__ssp_receive_chars()`, `__ssp_update_div()`, `__ssp_update_baud_rate()`, `__ssp_set_stop_bits()`, and `__ssp_wait_for_xmitr()`. UART operations are in `sifive_serial_uops`; probe/remove/PM are `sifive_serial_probe()`, `sifive_serial_remove()`, `sifive_serial_suspend()`, and `sifive_serial_resume()`.

## Control Flow

Module init registers the UART driver, then the platform driver. Probe obtains IRQ, maps MMIO, enables the clock, reads the `serial` alias as the UART line, allocates `struct sifive_serial_port`, registers a clock notifier, programs the initial divisor for 115200 baud, enables TX and RX hardware with watermark levels, requests the IRQ, adds the port to the console lookup table, and calls `uart_add_one_port()`.

The IRQ handler locks the port, reads interrupt-pending bits, drains RX when the RX watermark is pending, transmits queued chars when the TX watermark is pending, then unlocks through `uart_unlock_and_check_sysrq()`. Startup only enables RX watermark interrupts; start/stop TX toggle the TX watermark bit in the shadowed `ier`. Termios rejects unsupported word lengths, parity checking, and break handling by coercing flags and logging once, sets stop bits and baud divisor, updates timeout, and toggles RX enable according to `CREAD`. Console and earlycon write directly by waiting for TX FIFO space and writing `TXDATA`; the normal console uses nbcon atomic/thread callbacks and temporarily disables hardware interrupts around console output.

## State and Persistence Behavior

Per-port state is allocated with devm and lives until platform remove. The hardware divisor tracks `ssp->baud_rate` and `port.uartclk`; `ier` shadows the hardware interrupt enable register so watermark toggles do not require read-modify-write state from MMIO. The clock notifier updates `port.uartclk` and divisor after clock rate changes. Console state uses `sifive_serial_console_ports[]` and `console_line_ended` to prepend a newline for atomic writes that interrupt an unfinished line. There is no persistent storage beyond live hardware and driver memory.

## Dependencies and Integration Points

The driver depends on serial core, tty flip buffers, console/nbcon, earlycon, OF aliases and compatibles (`sifive,uart0`, `sifive,fu540-c000-uart`), platform resources, IRQs, clocks, and clock notifiers. It uses `uart_port_tx_limited()`, `uart_insert_char()`, `uart_prepare_sysrq_char()`, `uart_set_options()`, `uart_suspend_port()`, and `uart_resume_port()` for UART-core integration.

## Risks and Edge Cases

The hardware lacks parity, break, flow control, and modem signals, so termios callers may think requested settings were accepted unless they inspect coerced flags and one-time logs. `sifive_serial_tx_empty()` always returns empty because the hardware lacks a shift-register empty signal, while the clock notifier approximates drain time with a worst-case delay after TX FIFO empty. The divisor mask definition references `SIFIVE_SERIAL_IP_DIV_SHIFT`, which is not defined in the file and would be a compile-time risk if the mask were used. Probe only checks `id > SIFIVE_SERIAL_MAX_PORTS` under console config, leaving an off-by-one concern because valid indexes are `0..MAX_PORTS-1`. Busy waits in console/poll paths can spin indefinitely if hardware never frees TX space.

## Test Signals

Validation should include OF probe with valid and missing aliases, IRQ-driven RX/TX, console and nbcon atomic/thread writes, earlycon output, clock-rate change notification while TX is active, termios coercion for unsupported parity/break/word sizes, `CREAD` enable/disable, suspend/resume, remove cleanup of IRQ and notifier, and stress around TX watermark interrupts and sysrq reception.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/sifive.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/sprd_serial.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/sprd_serial.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/st-asc.c -->
# sources/distributed-fs/ceph-client/drivers/tty/serial/st-asc.c

## Purpose

`st-asc.c` is the STMicroelectronics Asynchronous Serial Controller driver. It registers up to eight `ttyAS` ports, supports memory-mapped ASC FIFOs, configurable baud modes, parity/stop/data-length handling, optional hardware CTS/RTS flow control, manual RTS through GPIO and pinctrl state switching, console, console polling, wakeup signaling on RX, and suspend/resume through serial core. The source was read as a complete 976-line file.

## Important APIs, Types, and Functions

The hardware contract is described by `ASC_*` offsets and masks for baud rate, TX/RX buffers, control, interrupt enable, status, timeout, resets, retries, RX error bits, FIFO status, and control modes. `struct asc_port` embeds `struct uart_port` and stores an optional RTS GPIO, clock, pinctrl handle, default/no-hardware-flow-control states, and booleans for hardware flow control and forced baud mode 1.

Low-level helpers are `asc_in()`, `asc_out()`, interrupt enable/disable helpers, FIFO status helpers, `asc_hw_txroom()`, `asc_transmit_chars()`, and `asc_receive_chars()`. UART operations are in `asc_uart_ops`: TX/RX control, modem control, startup/shutdown, PM, termios, config/type/verify, and optional poll operations. Platform setup flows through `asc_of_get_asc_port()`, `asc_init_port()`, `asc_serial_probe()`, and `asc_serial_remove()`. Console support is implemented by `asc_console_putchar()`, `asc_console_write()`, and `asc_console_setup()`.

## Control Flow

Module init registers the UART driver and platform driver. Probe resolves the port slot from `serial` or `ttyAS` aliases, records DT booleans (`uart-has-rtscts`, `st,force-m1`), maps MMIO, gets IRQ and clock, briefly enables the clock to read `uartclk`, initializes pinctrl states, and adds the port. Startup requests the IRQ, primes TX, and enables RX interrupts. The IRQ handler locks the port, reads status, receives while RX buffer full, transmits when TX FIFO is at least half empty and TX interrupts are enabled, then unlocks.

RX reads `ASC_STA` and `ASC_RXBUF`, synthesizes dummy status bits for normal RX, break, and overrun, optionally ignores parity in 8-bit modes because the datasheet marks PE undefined, handles wakeup events when the IRQ is configured as wake-capable, updates `icount`, calls break/sysrq helpers, inserts chars with the correct tty flag, and pushes the flip buffer. TX uses `uart_port_tx_limited()` with space computed from empty/half-empty/not-full status. Termios stops the controller, resets FIFOs, coerces unsupported CMSPAR and unavailable CRTSCTS, selects 7-bit-with-parity or 8-bit modes, sets stop/parity, toggles CTS hardware flow control, programs either simple divisor mode for low baud or mode 1 fractional-style baud for higher rates or `st,force-m1`, updates masks and timeout, restarts the controller, and outside the port lock switches pinctrl/GPIO RTS ownership if flow-control mode changed.

## State and Persistence Behavior

Static state is `asc_ports[ASC_MAX_PORTS]` plus `asc_uart_driver`. Each `asc_port` persists for its platform device and stores clock, pinctrl states, RTS GPIO ownership, line number, and DT booleans. Live controller state is in ASC control/baud/FIFO/interrupt registers and is reprogrammed by termios and PM. PM `UART_PM_STATE_OFF` clears `ASC_CTL_RUN` under the port lock and disables the clock; PM on enables the clock. There is no file-backed persistence.

## Dependencies and Integration Points

The driver integrates with serial core, tty flip buffers, console and console-poll, platform/OF matching (`st,asc`), clock framework, pinctrl, GPIO descriptors, IRQ wakeup metadata, and PM helpers. It uses `uart_get_baud_rate()`, `uart_update_timeout()`, `uart_handle_break()`, `uart_handle_sysrq_char()`, `uart_insert_char()`, `uart_console_write()`, and `uart_suspend_port()`/`uart_resume_port()`.

## Risks and Edge Cases

Manual RTS switching is delicate: when hardware flow control is disabled and the optional `no-hw-flowctrl` pinctrl state exists, the driver obtains an RTS GPIO with devm during termios; when hardware flow control is reenabled, it releases the GPIO and restores the default pinctrl state. `manual_rts` is only assigned inside the branches that set `toggle_rts`, so future edits must preserve that invariant. Console writes disable all ASC interrupts and busy-wait up to 1 second for FIFO empty/space. The driver has no early console and expects console setup only after probe/mapping. `asc_startup()` calls `asc_transmit_chars()` before RX interrupt enable, which depends on valid tty state. `asc_receive_chars()` dereferences `tport->tty->dev` for wakeup events when IRQ wake is set, so wake configuration should only occur when tty state is valid.

## Test Signals

Important signals include OF probe with `serial` and `ttyAS` aliases, missing/invalid pinctrl states, `uart-has-rtscts` and `st,force-m1` combinations, termios transitions between hardware flow control and manual RTS GPIO, baud programming below and above 19200, 7-bit/parity and 8-bit modes with parity-error behavior, RX break/frame/parity/overrun injection, wakeup IRQ RX activity, console and poll I/O, suspend/resume clock and `ASC_CTL_RUN` handling, module unload, and repeated open/close IRQ lifetime checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/st-asc.c -->
