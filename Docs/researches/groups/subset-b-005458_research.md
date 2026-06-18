# subset-b-005458 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/mpc52xx_uart.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/mpc52xx_uart.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/mps2-uart.c -->
# sources/distributed-fs/ceph-client/drivers/tty/serial/mps2-uart.c

## Purpose

`mps2-uart.c` is the serial-core driver for the ARM MPS2 UART exposed as `ttyMPS`. It provides platform/OF probing for `"arm,mps2-uart"`, normal and early console support, and a small interrupt-driven RX/TX implementation over a minimal register set: data, state, control, interrupt status/ack, and baud divider.

The hardware model is simple: fixed 8N1 framing, no modem-control hardware, a one-byte effective FIFO, and either one combined IRQ or separate RX/TX/overrun IRQs depending on platform description.

## Important APIs, Types, And Functions

`struct mps2_uart_port` wraps `struct uart_port` with a clock, TX/RX IRQ numbers, and a `flags` field containing `UART_PORT_COMBINED_IRQ`. `ports_idr` maps line numbers to port objects for console setup and write paths.

Register helpers `mps2_uart_write8()`, `mps2_uart_read8()`, and `mps2_uart_write32()` centralize MMIO access. The serial operations are in `mps2_uart_pops`: `tx_empty`, modem controls, `start_tx`, `stop_tx`, `stop_rx`, `startup`, `shutdown`, `set_termios`, type/config/request/verify hooks.

Interrupt handlers are split into `mps2_uart_rxirq()`, `mps2_uart_txirq()`, `mps2_uart_oerrirq()`, and `mps2_uart_combinedirq()`. Data movement is handled by `mps2_uart_rx_chars()` and `mps2_uart_tx_chars()`, the latter using `uart_port_tx()`.

Probe is composed of `mps2_of_get_port()`, `mps2_init_port()`, and `mps2_serial_probe()`. Console paths are `mps2_uart_console_write()`, `mps2_uart_console_setup()`, and early console handlers declared with `OF_EARLYCON_DECLARE()`.

## Control Flow

`mps2_uart_init()` registers the UART driver and the platform driver at `arch_initcall`. Probe allocates a managed port, chooses a line from the `serial` alias or cyclic IDR allocation, notes whether there is one combined IRQ, maps registers, prepares enough clock state to capture `uartclk`, records IRQs, and calls `uart_add_one_port()`.

Startup masks TX/RX groups, requests either the combined IRQ or the overrun/RX/TX IRQ trio, and then enables RX and TX plus their interrupt and overrun bits. Shutdown clears those enable bits and frees the corresponding IRQs.

TX begins by enabling TX interrupt and immediately calling `mps2_uart_tx_chars()` to prime the hardware. TX IRQ acknowledges `UARTn_INT_TX` and continues sending while `mps2_uart_tx_empty()` reports room. RX IRQ acknowledges `UARTn_INT_RX`, drains bytes while `UARTn_STATE_RX_FULL` is set, inserts them as `TTY_NORMAL`, and pushes the flip buffer. Overrun IRQ inserts `TTY_OVERRUN` for RX overruns and acknowledges unexpected TX overruns.

Termios enforces hardware limits by clearing CRTSCTS/CMSPAR, forcing CS8, no parity, and one stop bit. It computes a rounded baud divider from `uartclk`, writes `UARTn_BAUDDIV`, updates timeouts, and encodes the actual baud back into termios.

## State And Persistence Behavior

State is in the allocated `mps2_uart_port`, the IDR line mapping, and hardware registers. There is no persistent storage. The clock is enabled only temporarily in probe to read the rate; startup does not enable/disable it, so the platform clock topology must keep the UART usable after probe-time rate discovery.

Console lookup depends on `ports_idr` retaining the port object for a given index. The driver has no remove path, and the platform driver suppresses bind attributes, matching the assumption that these platform UARTs are not dynamically unbound.

## Dependencies And Integration Points

The driver uses Linux serial core, tty flip buffers, console/earlycon, OF/platform helpers, clocks, IDR allocation, and MMIO primitives. The device-tree binding supplies register resources, clock, interrupts, and optional serial alias. It registers `ttyMPS` with up to `MPS2_MAX_PORTS` ports.

## Risks And Edge Cases

The driver has no `remove` function and no IDR cleanup path, which is acceptable for non-hotpluggable platform devices but would be wrong for dynamic unbind. `mps2_uart_console_write()` assumes `idr_find()` succeeds and dereferences the result without a null check.

The separate-IRQ startup path requests the overrun IRQ as shared but RX/TX IRQs as non-shared; mismatched firmware IRQ descriptions will fail startup. Combined IRQ handling returns after the first handled source, so simultaneous RX/TX/overrun causes are serviced over multiple IRQ entries rather than one pass.

Because termios silently forces 8N1 and no flow control, tests expecting parity, stop-bit, or CRTSCTS behavior must assert that unsupported flags are cleared rather than applied.

## Test Signals

Boot with normal and early consoles on `"arm,mps2-uart"`, validate serial alias and cyclic IDR line assignment, test both one-IRQ and three-IRQ device-tree layouts, verify RX overrun reporting, confirm baud divider programming over the accepted range, and run TX/RX loopback under interrupt load. Static checks should flag the console null-dereference possibility and the missing remove/IDR cleanup if hot-unbind support is ever introduced.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/mps2-uart.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/msm_serial.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/msm_serial.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/mux.c -->
# sources/distributed-fs/ceph-client/drivers/tty/serial/mux.c

## Purpose

`mux.c` is the PA-RISC Serial MUX driver for Mux console hardware found in some HP PA-RISC servers. It registers `ttyB` ports on `MUX_MAJOR`, maps up to 256 MUX lines, and uses a polling timer rather than hardware IRQs to move data between the MUX FIFOs and the tty layer.

The file comments note that the driver currently supports console functionality on MUX port 0 and that full MUX functionality would need additional work. In practice the code registers all detected ports, but the implementation remains minimal: no real termios changes, modem controls, start/stop operations, or hardware IRQ integration.

## Important APIs, Types, And Functions

`struct mux_port` contains a `uart_port` and an `enabled` flag. Global state is `mux_ports[MUX_NR]`, `port_cnt`, `mux_driver`, and `mux_timer`. MMIO access is via `UART_PUT_CHAR()` and `UART_GET_FIFO_CNT()` plus direct raw reads of the data register.

`get_mux_port_count()` reads PA-RISC IODC data to determine port count and special-cases K-Class built-in MUX hardware to one connected port. `mux_read()` drains RX data/status words and handles break/sysrq. `mux_write()` uses `uart_port_tx_limited()` and waits for `mux_tx_done()` after writes. `mux_poll()` periodically services enabled ports.

Serial-core operations are in `mux_pops`, with many no-op hooks because the hardware/driver does not support modem control, termios, stop/start, or break control. Console support is `mux_console_write()` and `mux_console_setup()`.

Platform integration uses PA-RISC device tables `builtin_mux_tbl` and `mux_tbl`, drivers `builtin_serial_mux_driver` and `serial_mux_driver`, and lifecycle functions `mux_probe()`, `mux_remove()`, `mux_init()`, and `mux_exit()`.

## Control Flow

`mux_init()` registers the built-in MUX driver first, then the generic add-in MUX driver, preserving desired detection order. If any ports were probed, it starts `mux_timer` to run every `MUX_POLL_DELAY` and registers the console when configured.

`mux_probe()` determines port count, requests the MUX memory region, registers the UART driver on the first detected device, then initializes and maps each port line at `dev->hpa.start + MUX_OFFSET + i * MUX_LINE_OFFSET`. Each port is added with `uart_add_one_port()`, `PORT_MUX`, `UPF_BOOT_AUTOCONF`, FIFO size 255, and no IRQ.

Open/startup sets `mux_ports[line].enabled = 1`; shutdown clears it. The timer loops through `port_cnt`, skips disabled lines, calls `mux_read()` and then `mux_write()`, and rearms itself.

RX reads the data register until an EOFIFO marker appears. Status words are skipped. Break markers update break counters and invoke `uart_handle_break()`. Normal bytes pass through sysrq handling and enter the tty flip buffer. TX writes as much as fits based on FIFO count and then waits for FIFO drain in `mux_tx_done()`.

Removal finds the first port for the device by matching `mapbase`, removes each UART port, unmaps the line, and releases the memory region. Exit deletes the timer, unregisters console if needed, unregisters both PA-RISC drivers, and unregisters the UART driver.

## State And Persistence Behavior

State is entirely in static kernel memory and mapped device registers. `port_cnt` monotonically increases during probe and is used as both the number of registered lines and the next insertion index. `enabled` gates timer servicing for opened ports. There is no disk persistence.

The poll timer is global across all MUX devices. The driver assumes `port_cnt` and the static `mux_ports` layout remain coherent for the module lifetime. Remove does not compact `mux_ports` or reduce `port_cnt`, which is consistent with rare/non-hotplug PA-RISC hardware but important for any dynamic-unbind assumptions.

## Dependencies And Integration Points

This driver depends on PA-RISC platform APIs (`struct parisc_device`, `pdc_iodc_read()`, PA-RISC device tables), serial core, tty flip buffers, sysrq, console, timers, raw MMIO, and memory-region APIs. It exposes `ttyB` devices and a console when `CONFIG_SERIAL_MUX_CONSOLE` is enabled.

## Risks And Edge Cases

`get_mux_port_count()` calls `BUG_ON(status != PDC_OK)`, so malformed firmware reads panic the kernel rather than failing probe. `mux_probe()` calls `BUG_ON(status)` after `uart_add_one_port()`, making add failures fatal.

`request_mem_region()` return value is ignored. `ioremap()` result is not checked before use. Removal does not decrement `port_cnt`, clear mappings in the global array, or unregister the UART driver when the last device is removed outside module exit.

TX is polling and can busy-wait in `mux_tx_done()` until FIFO count reaches zero. The global timer services all enabled ports serially, so one slow or wedged port can delay others. Termios and modem controls are no-ops, so serial settings are effectively fixed.

## Test Signals

Test on PA-RISC systems with built-in and add-in MUX hardware, verifying built-in detection order and K-Class one-port override. Exercise console output on `ttyB0`, RX break/sysrq handling, timer polling under sustained RX/TX, open/close toggling of `enabled`, and module unload cleanup. Static review should focus on unchecked resource acquisition, fatal `BUG_ON()` paths, and behavior after device removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/mux.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/mvebu-uart.c -->
# sources/distributed-fs/ceph-client/drivers/tty/serial/mvebu-uart.c

## Purpose

`mvebu-uart.c` is the Marvell Armada 3700 UART driver and companion UART clock provider. It registers up to two `ttyMV` serial ports, supports standard and extended Armada 3700 UART register layouts, normal and early console output, suspend/resume state save/restore, and a platform clock provider that selects and gates shared UART parent clocks.

The file has two tightly related halves: the serial driver that moves bytes and configures baud divisors, and the `"marvell,armada-3700-uart-clock"` driver that owns shared clock-control bits in UART register space.

## Important APIs, Types, And Functions

Serial hardware variation is represented by `struct mvebu_uart_driver_data`, which embeds `struct uart_regs_layout` and `struct uart_flags` for standard versus extended offsets and ready/interrupt bits. Per-port state is `struct mvebu_uart`, containing the `uart_port`, clock, one summed IRQ or RX/TX IRQ pair, match data, and PM register snapshots.

The serial operation table `mvebu_uart_ops` provides TX/RX control, break control, startup/shutdown, termios, type/request/release, and optional console-poll hooks. RX/TX movement is handled by `mvebu_uart_rx_chars()` and `mvebu_uart_tx_chars()`. IRQ entry points are `mvebu_uart_isr()` for old single-IRQ bindings and `mvebu_uart_rx_isr()`/`mvebu_uart_tx_isr()` for named split IRQs.

Baud programming is in `mvebu_uart_baud_rate_set()`, protected by the global `mvebu_uart_lock` when touching `UART_BRDV` because the register shares baud divisor and clock-control fields. `mvebu_uart_set_termios()` restricts supported termios changes and computes min/max baud based on divisor limits and stability constraints.

Console support includes earlycon (`EARLYCON_DECLARE()` and `OF_EARLYCON_DECLARE()`), `mvebu_uart_console_write()`, and `mvebu_uart_console_setup()`.

The clock provider uses `struct mvebu_uart_clock` and `struct mvebu_uart_clock_base`, `mvebu_uart_clock_ops`, and `mvebu_uart_clock_probe()`. It registers two clocks, `uart_1` and `uart_2`, from parent candidates `TBG-A-P`, `TBG-B-P`, `TBG-A-S`, `TBG-B-S`, and `xtal`.

## Control Flow

`mvebu_uart_init()` registers the UART driver, then the clock platform driver, then the UART platform driver at `arch_initcall`. UART probe selects a line from the `serial` alias or a counter, fills a static `uart_port`, maps resources, allocates `struct mvebu_uart`, attaches standard/extended match data, gets the port clock, records single or split IRQs, soft-resets the UART, and calls `uart_add_one_port()`.

Startup resets TX/RX FIFOs, clears stale error bits, enables break/error interrupts and RX ready interrupts, then requests either the summed IRQ or the RX/TX pair. Shutdown disables UART interrupts and frees the requested IRQs.

The summed ISR reads status and dispatches RX when RX/error/break bits are set and TX when TX-ready is set. Split ISRs perform the same work by direction. RX loops until no RX-ready or break-detect status remains, handling parity, frame, overrun, break, sysrq, ignore masks, and the extended-UART requirement to explicitly clear error bits. TX uses `uart_port_tx_limited()` while the TX FIFO is not full.

Termios sets status masks, ignores unsupported flag changes by copying old termios bits back, constrains baud to a derived min/max range, calls `mvebu_uart_baud_rate_set()`, encodes actual baud, and updates timeout. Only baud, CREAD, INPCK, IGNPAR, and fixed CS8 behavior are supported.

The clock provider maps UART1 and UART2 BRDV register resources with `devm_ioremap()` to avoid exclusive conflicts with the UART drivers. It chooses a usable parent clock that can produce 9600 baud, keeps the chosen parent enabled, registers two child clocks, and exposes them through an OF onecell provider. On first prepare, it reprograms the shared UART clock control register and adjusts both UART baud divisors so active baud rates do not change.

## State And Persistence Behavior

Serial ports are stored in static `mvebu_uart_ports[2]`. `port->private_data` points to managed `struct mvebu_uart`. PM suspend stores UART data/control/status/baud/oversampling registers and resume writes them back before `uart_resume_port()`.

The global `mvebu_uart_lock` serializes `UART_BRDV` access between the UART baud path, suspend/resume, and clock provider. The clock provider has persistent runtime state for selected parent index, parent rates, divider, and a `configured` boolean that makes parent/divisor reconfiguration a one-time operation.

There is no filesystem persistence. Hardware register state is restored across system PM through in-memory snapshots.

## Dependencies And Integration Points

The driver uses serial core, tty flip buffers, console/earlycon, OF/platform helpers, clocks and clk-provider APIs, MMIO, polling helpers, PM, and device-managed resources. It depends on Armada 3700 device-tree compatibles `"marvell,armada-3700-uart"`, `"marvell,armada-3700-uart-ext"`, and `"marvell,armada-3700-uart-clock"`.

It integrates with the common clock framework as both a clock consumer for UART ports and a clock provider for the two UART clocks. This creates an important ordering dependency: extended UART probe treats missing clock as fatal except for probe deferral.

## Risks And Edge Cases

Shared `UART_BRDV` fields are easy to corrupt if any new path omits `mvebu_uart_lock`. The code comments document swapped UART clock-disable bits compared with Marvell documentation; any register cleanup that follows the manual instead of the driver comments would break clock gating.

The extended UART requires explicit error-bit clearing to avoid interrupt loops. RX status/error handling should be tested separately for standard and extended layouts. The old single-IRQ path is noted as UART0-only; using old bindings for other ports would be suspect.

The clock provider intentionally maps registers already used by UART drivers without exclusive reservation. That is safe only because access is locked and field ownership is understood. `mvebu_uart_clock_set_rate()` is a no-op that returns success, relying on determine-rate constraints and the fixed parent/divider model.

## Test Signals

Validate standard and extended compatibles, old summed IRQ and new named RX/TX IRQ bindings, early console and normal console on `ttyMV`, baud changes across low rates and high-rate stability limits, parity/frame/break/overrun insertion, suspend/resume register restoration, and simultaneous use of both UARTs while the clock provider prepares/gates clocks. Clock tests should confirm parent selection, `uart_1`/`uart_2` rates, lock-protected BRDV updates, and no baud jump when the clock provider first prepares.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/mvebu-uart.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/mxs-auart.c -->
# sources/distributed-fs/ceph-client/drivers/tty/serial/mxs-auart.c

## Purpose

`mxs-auart.c` is the Freescale MXS/i.MX23/i.MX28 Application UART driver with Alphascale ASM9260 support. It registers up to five `ttyAPP` ports, supports console output, optional DMA for i.MX28 hardware flow-control configurations, modem-control GPIO integration, and vendor-specific register offset tables for STMP37xx-style and ASM9260-style AUART blocks.

The driver translates serial-core callbacks into AUART register operations, manages reset/clock state, handles RX/TX interrupts, optionally drives DMA transfers, and exposes platform devices matched by `"fsl,imx28-auart"`, `"fsl,imx23-auart"`, and `"alphascale,asm9260-auart"`.

## Important APIs, Types, And Functions

`struct mxs_auart_port` wraps `uart_port` with flags, previous modem-control state, device type, vendor register table, clocks, DMA channels/buffers/scatterlists, modem GPIO descriptors, GPIO IRQs, and modem-status IRQ enable state.

Vendor register indirection is defined by `struct vendor_data`, `mxs_asm9260_offsets[]`, `mxs_stmp37xx_offsets[]`, `mxs_reg_to_offset()`, `mxs_read()`, `mxs_write()`, `mxs_set()`, and `mxs_clr()`. This lets common logic address different layouts.

DMA functions include `mxs_auart_dma_init()`, `mxs_auart_dma_exit()`, `mxs_auart_dma_exit_channel()`, `mxs_auart_dma_tx()`, `dma_tx_callback()`, `mxs_auart_dma_prep_rx()`, and `dma_rx_callback()`. PIO RX/TX uses `mxs_auart_rx_char()`, `mxs_auart_rx_chars()`, and `mxs_auart_tx_chars()`.

Modem control is handled by `mxs_auart_set_mctrl()`, `mxs_auart_get_mctrl()`, `mxs_auart_modem_status()`, `mxs_auart_enable_ms()`, `mxs_auart_disable_ms()`, GPIO init/free/request helpers, and `serial_mctrl_gpio.h`.

Serial-core operations are collected in `mxs_auart_ops`, including `set_ldisc` for PPS-on-DCD handling. Probe/remove/init/exit are `mxs_auart_probe()`, `mxs_auart_remove()`, `mxs_auart_init()`, and `mxs_auart_exit()`. Console support is `auart_console_write()`, `auart_console_setup()`, and `auart_console_get_options()`.

## Control Flow

Module init registers the `uart_driver` and platform driver. Probe allocates the port, gets the required `serial` alias as the line number, records RTS/CTS capability from modern or deprecated DT properties, validates the line, determines device type from match data, gets clocks, maps the MMIO resource, fills `uart_port`, selects the vendor register offsets, requests the main IRQ, initializes modem GPIOs and GPIO IRQs, stores the port in `auart_port[]`, deasserts reset, adds the UART port, and logs hardware version or ASM9260 detection.

Startup enables the module clock, either ungates the console port or fully resets/deasserts a non-console port, enables UARTEN, enables RX/timeout/CTS interrupts, resets FIFO size to the PIO default, enables FIFO mode, samples initial modem GPIO status, and marks modem-status IRQs disabled until termios requests them.

The main IRQ handler locks the port, reads status and interrupt state, acknowledges pending AUART interrupt bits, handles GPIO IRQs for modem line changes, handles CTSMIS, drains RX in PIO mode on RX/timeout interrupts, and services TX interrupts through `mxs_auart_tx_chars()`.

TX in DMA mode serializes with `MXS_AUART_DMA_TX_SYNC`, copies bytes out of the xmit FIFO into a DMA buffer, submits a PIO transfer-count command followed by a MEM_TO_DEV transfer, and chains more TX from the callback. In PIO mode it uses `uart_port_tx_flags()` while the TX FIFO is not full and enables/disables TX interrupt based on pending work.

RX in PIO mode reads one character at a time, classifies break/parity/frame/overrun based on `REG_STAT`, applies status masks, handles sysrq, inserts through `uart_insert_char()`, clears status, and pushes the flip buffer. RX DMA prepares a timeout-count PIO command plus DEV_TO_MEM transfer of `UART_XMIT_SIZE`; completion unmaps, reads RX count from status, inserts the received string without per-byte error flags, clears status, pushes the buffer, and immediately starts another RX DMA.

Termios builds line-control bits for word length, parity, stick parity, stop bits, status masks, CREAD, flow control, and baud divisor. DMA is only attempted for i.MX28 with hardware RTS/CTS support and without GPIO RTS/CTS lines. It writes line control and CTRL2, updates timeout, starts RX DMA if enabled, and enables or disables modem-status IRQs based on `UART_ENABLE_MS()`.

Shutdown disables modem-status IRQs, tears down DMA if active, resets or gates the UART depending on console status, and disables the clock.

## State And Persistence Behavior

Runtime state is stored in `auart_port[]` and each `mxs_auart_port`. There is no disk persistence. Flags in `s->flags` encode DMA enabled, TX DMA synchronization, RX DMA readiness, and hardware RTS/CTS capability. `mctrl_prev` persists previous modem-line state so GPIO and CTS interrupts can report deltas.

DMA changes `port.fifosize` to `UART_XMIT_SIZE` while enabled and startup resets it to `MXS_AUART_FIFO_SIZE`. Console writes save/restore CTRL0 and CTRL2 when the transmitter becomes idle, preserving hardware state around synchronous console output.

For ASM9260, both `mod` and `ahb` clocks are prepared during probe and remain enabled until remove; for non-ASM variants, the main clock is acquired but enabled around startup/console operations.

## Dependencies And Integration Points

The driver depends on serial core, tty flip buffers, console, platform/OF, clocks, DMAengine and DMA mapping, GPIO consumer APIs, IRQ APIs, and `serial_mctrl_gpio`. Device tree supplies compatible string, serial alias, optional RTS/CTS property, clock names for ASM9260, MMIO resource, and IRQ.

It integrates with PPS through `set_ldisc`: selecting `N_PPS` sets `UPF_HARDPPS_CD` and enables modem-status monitoring. It integrates with modem-control GPIOs for RTS/CTS/DCD/DSR/RI when pins are not native AUART signals.

## Risks And Edge Cases

DMA support is deliberately constrained because MX23 has DMA erratum 2836 and GPIO-based RTS/CTS is warned as problematic. RX DMA sacrifices precise break/parity/frame reporting by inserting a raw string based on RX count after clearing error bits.

`mxs_auart_dma_tx()` prepares a PIO descriptor and then overwrites `desc` with the data descriptor without explicitly submitting the first descriptor; this relies on DMAengine/controller semantics for `DMA_TRANS_NONE` preparation and is a maintenance-sensitive path.

Probe requires a valid `serial` alias and fails otherwise. Error paths use `auart_port[pdev->id] = NULL` even though the port line comes from the alias; if `pdev->id` differs from `s->port.line`, cleanup can clear the wrong slot.

Main IRQ and GPIO modem IRQs share `mxs_auart_irq_handle()`, so register reads/acks occur even for GPIO IRQ invocation. Native AUART CTS interrupt enable/disable is left as TODO when CTS is not GPIO.

## Test Signals

Test each compatible and register offset table, probe failure without a serial alias, clock enable/disable on ASM9260 and non-ASM variants, console setup/write/restore, PIO RX/TX with break/parity/frame/overrun/sysrq, hardware and GPIO RTS/CTS combinations, modem GPIO IRQ deltas, PPS line discipline, DMA enable only on i.MX28 hardware RTS/CTS, RX DMA timeout/count behavior, TX DMA serialization, shutdown DMA cleanup, and remove cleanup using both `pdev->id` and alias-derived line values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/mxs-auart.c -->
