# subset-b-005464 Research

Grouped source research for Linux serial drivers in `sources/distributed-fs/ceph-client/drivers/tty/serial`. Each section is marker-delimited for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/timbuart.c -->
# sources/distributed-fs/ceph-client/drivers/tty/serial/timbuart.c

## Purpose

`timbuart.c` is the platform serial driver for the Timberdale FPGA UART. It registers one `ttyTU` UART port with Linux serial core, maps the Timberdale MMIO register block, handles shared IRQs by deferring RX/TX/modem work into a tasklet, and exposes the device as a `platform:timb-uart` driver. The file was read as a complete 496-line source file.

## Important APIs, Types, and Functions

The private `struct timbuart_port` wraps `struct uart_port` with a tasklet, DMA flag placeholder, last interrupt-enable snapshot, and platform device pointer. The `timbuart_ops` serial-core table implements `tx_empty`, modem-control methods, TX/RX start-stop, buffer flush, startup/shutdown, termios setup, resource request/release, and port verification. Notable helpers are `timbuart_handleinterrupt()`, `timbuart_tasklet()`, `timbuart_rx_chars()`, `timbuart_tx_chars()`, `timbuart_handle_rx_port()`, `timbuart_handle_tx_port()`, `timbuart_mctrl_check()`, and `timbuart_probe()/timbuart_remove()`.

## Control Flow

Probe allocates `struct timbuart_port`, initializes serial-core fields, discovers IORESOURCE_MEM and IRQ resources, sets up the tasklet, registers `timbuart_driver`, and adds the single port. Serial core later calls `timbuart_config_port()`, which requests and maps MMIO. On open, `timbuart_startup()` flushes RX, clears interrupt status, enables RX and CTS-delta interrupts, and requests the IRQ. The top-half interrupt checks `TIMBUART_IPR`, snapshots `IER`, disables interrupts, and schedules `timbuart_tasklet()`. The tasklet runs under `uart_port_lock()`, processes TX if DMA is not used, checks CTS changes, processes RX, then writes the newly composed interrupt-enable mask. TX is pull-based from the tty xmit FIFO and RX pushes characters into the tty flip buffer.

## State and Persistence Behavior

Persistent driver state is in the allocated `timbuart_port`, serial-core `uart_port`, tasklet, and the hardware registers. `last_ier` preserves pre-disable interrupt enables across the top half and tasklet. `port->icount`, `read_status_mask`, `ignore_status_mask`, modem state, and xmit FIFO state are owned by serial core. There is no file-backed persistence. Hardware state is reset or reprogrammed on startup, shutdown, flush, and termios changes.

## Dependencies and Integration Points

The driver depends on Linux platform devices, serial core, tty flip buffers, MMIO accessors, IRQ handling, tasklets, and register definitions from `timbuart.h`. It integrates with Timberdale platform-device enumeration via `.driver.name = "timb-uart"` and `MODULE_ALIAS("platform:timb-uart")`. The UART major/minor and register layout are local to the Timberdale UART interface.

## Risks and Edge Cases

`timbuart_tx_chars()` writes bytes but does not increment `port->icount.tx`, so diagnostics may under-report transmitted bytes. The type callback appears inverted, returning `"timbuart"` when `PORT_UNKNOWN`; that is unusual for serial-core type reporting. `timbuart_startup()` returns directly after `request_irq()` and does not undo enabled interrupts on IRQ failure. Probe registers the `uart_driver` per device even though `.nr = 1`, so multiple platform instances would conflict. RX error handling is minimal: full FIFO is counted as overrun and flushed, but individual parity/framing conditions are not represented. The `usedma` field is always zero here, so DMA paths are placeholders rather than implemented behavior.

## Test Signals

Useful validation includes boot/probe tests for `timb-uart`, `ttyTU0` creation, open/close cycles, IRQ handling under shared interrupts, TX/RX loopback or board-level data transfer, CTS-delta wakeups, termios baud selection across the supported `baudrates[]`, FIFO flush behavior, and module unload/reload. Kernel build coverage should include serial-core API compatibility and `PORT_TIMBUART` definitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/timbuart.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/timbuart.h -->
# sources/distributed-fs/ceph-client/drivers/tty/serial/timbuart.h

## Purpose

`timbuart.h` defines the Timberdale FPGA UART register offsets, FIFO size, control bits, interrupt/status bits, grouped RX/TX flag masks, and tty major/minor values consumed by `timbuart.c`. The file was read as a complete 46-line header.

## Important APIs, Types, and Functions

There are no functions or types. The important definitions are `TIMBUART_FIFO_SIZE`, register offsets `TIMBUART_RXFIFO` through `TIMBUART_BAUDRATE`, control bits `TIMBUART_CTRL_RTS`, `TIMBUART_CTRL_CTS`, `TIMBUART_CTRL_FLSHTX`, `TIMBUART_CTRL_FLSHRX`, interrupt/status bits such as `TXBF`, `TXBAE`, `CTS_DELTA`, `RXDP`, `RXBF`, `RXTT`, `RXBNAE`, `TXBE`, aggregate masks `RXFLAGS` and `TXFLAGS`, and `TIMBUART_MAJOR`/`TIMBUART_MINOR`.

## Control Flow

The header has no executable control flow. Its masks drive runtime decisions in the driver: RX events trigger FIFO draining or flushing, TX events trigger xmit FIFO pumping, `CTS_DELTA` triggers modem-status wakeups, and control bits manipulate RTS or FIFO flushes.

## State and Persistence Behavior

No state is owned by the header. The values are compile-time constants that define how the driver interprets persistent MMIO register state in Timberdale hardware.

## Dependencies and Integration Points

The only integration point is the Timberdale UART driver. The major/minor definitions align the device with Linux serial numbering, while the offsets and bit masks are the ABI between `timbuart.c` and the FPGA register block.

## Risks and Edge Cases

Any incorrect bit assignment changes interrupt acknowledgement, FIFO flushing, or modem-control behavior globally for the driver. `RXFLAGS` includes several conditions that the driver mostly acknowledges together, so adding new bits without matching error handling could hide hardware events. The comment says "GPIO driver" even though the header is for UART; this is documentation drift but not a runtime issue.

## Test Signals

Build coverage of `timbuart.c` is the primary signal. Hardware or emulator tests should verify that each offset reaches the expected register, that `RXFLAGS`/`TXFLAGS` acknowledgement clears only intended events, and that RTS/CTS and FIFO flush bits behave as documented by the Timberdale FPGA.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/timbuart.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/uartlite.c -->
# sources/distributed-fs/ceph-client/drivers/tty/serial/uartlite.c

## Purpose

`uartlite.c` is the Linux serial-core driver for Xilinx UARTLite controllers. It supports platform and device-tree binding, runtime/system power management, optional clocks, endian detection, console and earlycon output, and a fixed synthesized baud/parity/data-bit configuration. The file was read as a complete 949-line source file.

## Important APIs, Types, and Functions

`struct uartlite_data` stores endian register operations, optional `s_axi_aclk`, synthesized baud, and supported cflags. `struct uartlite_reg_ops` abstracts big-endian versus little-endian MMIO. `ulite_ops` provides the serial-core methods. Main runtime helpers include `ulite_receive()`, `ulite_transmit()`, `ulite_isr()`, `ulite_startup()`, `ulite_shutdown()`, `ulite_set_termios()`, `ulite_assign()`, `ulite_release()`, `ulite_probe()`, and `ulite_remove()`. Console support is in `ulite_console_write()/setup()` and early console support is declared for `uartlite`, `xlnx,opb-uartlite-1.00.b`, and `xlnx,xps-uartlite-1.00.a`.

## Control Flow

Module init registers `ulite_uart_driver` and the platform driver. Probe allocates private data, reads DT properties such as `port-number`, `current-speed`, `xlnx,use-parity`, `xlnx,odd-parity`, and `xlnx,data-bits`, gets the memory resource and IRQ, prepares the optional clock, enables runtime PM, then calls `ulite_assign()` to populate a slot in the static `ulite_ports[]` array and add the port to serial core. Port request maps the 16-byte register region and detects endian mode by writing reset and checking `ULITE_STATUS_TXEMPTY`. Startup enables the clock, requests a shared rising-edge IRQ, resets FIFOs, and enables interrupts. The ISR loops while RX or TX work is possible, receiving one character or error indication and transmitting one byte per iteration, then pushes the flip buffer if work occurred.

## State and Persistence Behavior

State is stored in static `ulite_ports[]`, per-device `uartlite_data`, serial-core buffers/masks, the optional global console pointer, and hardware control/status registers. The hardware's baud, parity, and data width are treated as synthesized constants; `ulite_set_termios()` forces termios back to what DT or defaults describe. Runtime PM uses autosuspend to disable the clock when idle and re-enable it on demand. There is no file-backed persistence.

## Dependencies and Integration Points

The driver depends on platform devices, OF properties, Linux clock APIs, runtime PM, serial core, tty flip buffers, IRQs, `read_poll_timeout_atomic()`, and earlycon/console infrastructure. It binds OF compatibles `xlnx,opb-uartlite-1.00.b` and `xlnx,xps-uartlite-1.00.a`, exposes `ttyUL*`, and supports `CONFIG_CONSOLE_POLL` for polling console/debug paths.

## Risks and Edge Cases

`ulite_startup()` leaks an enabled clock if `request_irq()` fails because it returns without disabling the clock. `ulite_remove()` reads `port->private_data` before `ulite_release()` clears drvdata, but a failed or unusual probe path could make `port` unavailable. The driver intentionally cannot change baud or format at runtime; user termios requests are coerced, which can surprise applications. Endian detection depends on reset/status behavior and could misdetect broken or inaccessible hardware. The IRQ loop is bounded only by work exhaustion, so pathological status behavior could spin. Early console uses raw little-endian `readl/writel`, independent of runtime endian detection.

## Test Signals

Signals include build coverage for platform, OF, console, earlycon, poll-console, and PM configurations; DT probe tests for property validation and automatic port assignment; data-loopback RX/TX tests; parity/frame/overrun injection; endian-mode tests; runtime autosuspend/resume clock checks; console output during normal boot and oops paths; and failure-injection around IRQ and clock acquisition.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/uartlite.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/ucc_uart.c -->
# sources/distributed-fs/ceph-client/drivers/tty/serial/ucc_uart.c

## Purpose

`ucc_uart.c` is the Freescale QUICC Engine UCC slow UART driver. It exposes QE UCC UARTs as `ttyQE0` through `ttyQE3`, manages QE buffer descriptors and coherent DMA buffers, programs UCC parameter RAM, supports optional Soft-UART microcode on PPC32, and binds device-tree UCC UART nodes. The file was read as a complete 1531-line source file.

## Important APIs, Types, and Functions

`struct ucc_uart_pram` models the UCC UART parameter RAM, including standard and Soft-UART-only fields. `struct uart_qe_port` wraps `struct uart_port` with UCC register pointers, `ucc_slow_info`, UCC private state, OF node, descriptor rings, coherent buffer addresses, FIFO sizing, and shutdown delay. The serial-core table `qe_uart_pops` implements TX/RX control, startup/shutdown, termios, resource request/release, and validation. Important functions include `cpu2qe_addr()`, `qe2cpu_addr()`, `qe_uart_tx_pump()`, `qe_uart_int_rx()`, `qe_uart_int()`, `qe_uart_initbd()`, `qe_uart_init_ucc()`, `qe_uart_request_port()`, `qe_uart_set_termios()`, `soft_uart_init()`, `uart_firmware_cont()`, `ucc_uart_probe()`, and `ucc_uart_remove()`.

## Control Flow

Module init registers the fixed-major UART driver and OF platform driver. Probe optionally initializes Soft-UART, allocates `uart_qe_port`, reads MMIO resource, UCC number, RX/TX BRG clock names, port number, IRQ, and QE `brg-frequency`, then initializes serial-core fields and UCC slow-info fields before `uart_add_one_port()`. During serial-core config, `qe_uart_request_port()` calls `ucc_slow_init()`, captures UCC register/PRAM/BD pointers, and allocates coherent RX/TX character buffers. Startup refuses Soft-UART if firmware is not loaded, initializes RX/TX BDs, programs UCC registers/PRAM, requests the shared IRQ, enables RX interrupt events, and starts RX/TX in UCC slow mode. The IRQ handler clears UCCE events, dispatches break handling, drains RX BDs into tty buffers, and pumps queued TX data into free BDs. Shutdown waits for TX BDs to drain, optionally waits `UCC_WAIT_CLOSING`, disables UCC, gracefully stops TX, reinitializes BDs, and frees the IRQ.

## State and Persistence Behavior

Per-port persistent state includes descriptor ring positions `rx_cur`/`tx_cur`, coherent buffer mappings, UCC parameter RAM, UCC slow-private state, OF node reference, serial-core masks, and FIFO sizing. Global `soft_uart` and `firmware_loaded` apply process-wide to all ports. Hardware state is programmed into UCC GUMR, UCCM/UCCE, UPSMR/SUPSMR, BRGs, and PRAM fields on startup and termios changes. There is no disk persistence; firmware loading is asynchronous and stored only in the global flag.

## Dependencies and Integration Points

The driver depends on serial core, tty flip buffers, OF address/IRQ parsing, DMA coherent allocation, QUICC Engine UCC slow APIs, CPM/QE firmware APIs, Linux firmware loading, and PPC32 CPU revision probing for Soft-UART filenames. It binds OF nodes with `.type = "serial", compatible = "ucc_uart"` and `fsl,t1040-ucc-uart`, uses `qe_setbrg()` for BRG clocks, and presents major 204 minor 46-49 to match Freescale CPM-style devices.

## Risks and Edge Cases

The DMA address translation helpers call `BUG()` if a BD buffer points outside the coherent allocation, turning corruption into a kernel crash. `qe_uart_request_port()` does not call `ucc_slow_free()` if coherent allocation fails after `ucc_slow_init()`. The Soft-UART globals mean one port requiring Soft-UART affects all instances, and asynchronous firmware loading can make early opens fail until `firmware_loaded` is set. Termios bit clearing is suspicious: `upsmr &= UCC_UART_UPSMR_CL_MASK` and `supsmr &= UCC_UART_SUPSMR_CL_MASK` retain only character-length bits before ORing new values, which may discard other mode bits. `CREAD` handling modifies `read_status_mask` instead of `ignore_status_mask`, so receive suppression deserves careful hardware testing. The probe path holds a QE node reference in `qe_port->np`; error paths release it only after the QE node is found.

## Test Signals

Useful tests include OF probe validation for required properties, multiple port-number bounds, BRG clock-name validation, coherent DMA allocation failure injection, `ucc_slow_init()`/free leak checks, Soft-UART firmware present/missing/asynchronous scenarios, RX/TX descriptor wrap tests, break/parity/frame/overrun injection, termios matrix coverage for CS5-CS8/parity/stop/CREAD, shutdown drain timeout behavior, and serial-console or user-space loopback traffic across all four supported ports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/ucc_uart.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/vt8500_serial.c -->
# sources/distributed-fs/ceph-client/drivers/tty/serial/vt8500_serial.c

## Purpose

`vt8500_serial.c` is the serial-core driver for VIA/WonderMedia VT8500-family UARTs. It supports device-tree probing, a maximum of six `ttyWMT` ports, optional console and poll-console paths, clock-derived baud programming, FIFO interrupt handling, and variant handling for WM8880 software RTS/CTS switching. The file was read as a complete 719-line source file.

## Important APIs, Types, and Functions

`struct vt8500_port` wraps `struct uart_port` with a name buffer, clock pointer, clock predivider, cached interrupt-enable mask, and variant flags. `vt8500_uart_pops` implements serial-core operations. Important helpers are `handle_rx()`, `handle_tx()`, `vt8500_irq()`, `vt8500_set_baud_rate()`, `vt8500_startup()`, `vt8500_shutdown()`, `vt8500_set_termios()`, `vt8500_serial_probe()`, and console helpers `vt8500_console_write()/setup()` plus `vt8500_get_poll_char()/put_poll_char()` when enabled.

## Control Flow

`device_initcall()` registers the UART driver and platform driver. Probe matches variant flags, obtains IRQ, chooses a line from the `serial` alias or a bitmap, allocates a managed `vt8500_port`, maps registers, obtains and enables the clock, derives the UART clock from a predivider and oversampling divisor, initializes the serial-core port, stores it in `vt8500_uart_ports[]`, and adds it to serial core. Startup requests a high-triggered IRQ and enables TX/RX. The interrupt handler locks the port, reads and acknowledges `URISR`, dispatches RX FIFO/error handling, TX FIFO pumping, and CTS delta handling, then unlocks. Termios reprograms baud, parity, size, stop bits, optional software RTS/CTS mode, read masks, FIFO reset, FIFO enable, and interrupt mask.

## State and Persistence Behavior

State is split between the static `vt8500_uart_ports[]` pointer table, `vt8500_ports_in_use` bitmap, per-port cached `ier`, variant flags, clock predivider, and serial-core state. Hardware state lives in UART line-control, divisor, FIFO, interrupt, break, and status registers. There is no remove function in this source, so successfully probed ports are effectively lifetime devices. No file-backed persistence exists.

## Dependencies and Integration Points

The driver depends on device tree matching for `via,vt8500-uart` and `wm,wm8880-uart`, OF aliases, platform MMIO/IRQ resources, Linux clocks, serial core, tty flip buffers, and optional console/poll-console infrastructure. It uses `PORT_VT8500`, exposes `ttyWMT`, and integrates with DEC-style system init through `device_initcall()` rather than regular module init/exit.

## Risks and Edge Cases

Probe reserves a port bit before several failure points and does not clear it on later errors. There is no platform remove path to disable clocks, remove ports, or clear `vt8500_uart_ports[]`. `vt8500_break_ctl()` sets break when requested but does not explicitly clear it in the `else` path. Console write calls `vt8500_write(&vt8500_port->uart, VT8500_URIER, 0)` with arguments reversed relative to the helper signature, which would write the register offset as a value at offset zero rather than disabling interrupts. RX handling masks received data with `~port->read_status_mask`, which is unusual because the data word includes both character and error bits. Clock predivider calculation can produce zero if the input clock is unexpectedly low, which would break divisor programming.

## Test Signals

Validation should include DT compatible/alias probe, six-port allocation behavior, probe failure cleanup, clock-rate/divisor sanity, TX/RX FIFO loopback, parity/frame/overrun injection, CTS delta wakeups, break assertion and release, WM8880 software RTS/CTS termios behavior, console output, poll-console operations, and static analysis or runtime tests for the console interrupt-disable write ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/vt8500_serial.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/xilinx_uartps.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/xilinx_uartps.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/zs.c -->
# sources/distributed-fs/ceph-client/drivers/tty/serial/zs.c

## Purpose

`zs.c` is the DECstation IOASIC Zilog Z85C30 SCC serial driver. It initializes up to two SCC chips with two channels each, exposes them as `ttyS` ports through serial core, handles DECstation-specific modem-line wiring, supports serial console output, and directly programs the Z85C30 register set using the definitions in `zs.h`. The file was read as a complete 1308-line source file.

## Important APIs, Types, and Functions

The driver uses `struct zs_scc` and `struct zs_port` from `zs.h`, plus local `struct zs_parms` for discovered SCC resources. Important low-level helpers are `read_zsreg()`, `write_zsreg()`, `read_zsdata()`, `write_zsdata()`, `load_zsregs()`, `zs_receive_drain()`, `zs_transmit_drain()`, and `zs_line_drain()`. Serial-core operations are in `zs_ops`, including modem control, TX/RX start-stop, break, startup/shutdown, termios, PM, request/release/configure, and verify. Runtime paths include `zs_receive_chars()`, `zs_raw_transmit_chars()`, `zs_status_handle()`, and `zs_interrupt()`. Setup paths include `zs_probe_sccs()`, `zs_console_setup()`, `zs_init()`, and `zs_exit()`.

## Control Flow

`zs_probe_sccs()` discovers SCC0/SCC1 IRQ availability from DECstation platform arrays, initializes `zs_sccs[]`, fills each channel's `uart_port`, mapbase, IRQ, clock, and register shadow from `zs_init_regs`. Console init can map and reset a port before normal module init. Module init registers the `ttyS` UART driver and adds each discovered port. During config, `zs_request_port()` reserves and maps MMIO, then `zs_reset()` resets the chip once per SCC and loads the register shadow. Startup reference-counts the shared IRQ per SCC through `irq_guard`, clears receive and pending interrupts, enables RX/TX/ext interrupts, enables break detection, records modem and break state, and marks TX stopped. The shared interrupt handler reads RR3 from channel A, prioritizes RX for both channels, then external status and TX. Termios edits the register shadow for character size, parity, stop bits, clock mode, BRG constants, read/ignore masks, receive enable, and modem interrupts, then reloads hardware registers.

## State and Persistence Behavior

Persistent state is held in static `zs_sccs[]`; each `zs_port` contains a register shadow `regs[16]`, current modem state, break state, clock mode, and TX-stopped flag. Each `zs_scc` has a shared spinlock, IRQ reference guard, and one-time initialized flag. Hardware state persists in Z85C30 registers and is deliberately mirrored through the register shadow because many write registers are not readable. There is no file-backed persistence. Console paths temporarily alter TX enable and interrupt bits, then restore the saved shadow values.

## Dependencies and Integration Points

The driver depends on DECstation platform headers (`dec_interrupt`, IOASIC addresses, `dec_kn_slot_base`), serial core, tty flip buffers, sysrq, shared IRQs, MMIO, and the Z85C30 register definitions in `zs.h`. It exposes classic `ttyS` major/minor numbering, supports `CONFIG_SERIAL_ZS_CONSOLE`, and relies on DECstation channel wiring where channel A signals are used to represent some modem lines for channel B.

## Risks and Edge Cases

Register access requires recovery delays and high-byte IOASIC offsets; timing or offset mistakes can corrupt SCC programming. The driver has complex channel-A/channel-B modem-line coupling, so DTR/RTS/DSR/RI/DCD regressions are easy when changing modem code. `zs_status_handle()` increments `dsr` for `TIOCM_RNG` and `rng` for `TIOCM_DSR`, which appears swapped. `zs_shutdown()` disables RX but writes R5 without clearing `TxENAB`, relying on other paths for TX state. IRQ sharing is guarded per SCC, but startup failure after IRQ acquisition must keep `irq_guard` balanced. The code uses static maximum SCC counts and cannot dynamically scale beyond two chips.

## Test Signals

Signals include MIPS/DECstation build coverage, boot discovery with SCC0/SCC1 present and absent, console setup/write before and after normal registration, TX/RX loopback per channel, shared IRQ receive-priority behavior, modem-line delta tests for channel B wiring, break/sysrq handling, termios coverage for BRG and CS/parity/stop settings, startup/shutdown reference-count tests on both channels of one SCC, and static analysis of register-shadow updates versus hardware writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/zs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/zs.h -->
# sources/distributed-fs/ceph-client/drivers/tty/serial/zs.h

## Purpose

`zs.h` defines the private data structures and complete Zilog Z85C30 SCC register/bit vocabulary used by the DECstation `zs.c` serial driver. It is both a driver-private state contract and the hardware register map for programming channel control, modem status, baud generator constants, interrupts, and error reporting. The file was read as a complete 285-line header.

## Important APIs, Types, and Functions

Under `__KERNEL__`, `struct zs_port` stores the containing SCC pointer, embedded `uart_port`, clock mode, break/TX-stop state, modem state, current break state, and a 16-byte write-register shadow. `struct zs_scc` groups two channels with a spinlock, atomic IRQ guard, and one-time initialization flag. The conversion macros `ZS_BRG_TO_BPS()` and `ZS_BPS_TO_BRG()` convert between Z85C30 baud-rate-generator constants and baud rates. The rest of the header defines write register numbers `R0`-`R15`, command values, interrupt masks, RX/TX format bits, clock-source bits, modem bits, read-register status bits, and receive error flags.

## Control Flow

The header has no executable control flow. Its constants drive every control path in `zs.c`: register shadow initialization, reset/load sequencing, TX/RX enablement, interrupt decoding, termios translation, modem-line handling, break/sysrq detection, baud generation, and console output.

## State and Persistence Behavior

The header defines the shape of persistent in-memory driver state. The `regs[ZS_NUM_REGS]` shadow is especially important because Z85C30 write registers are programmed repeatedly and not all are safely readable. Hardware state persists in SCC registers; software state persists in static `zs_sccs[]` instances in `zs.c`.

## Dependencies and Integration Points

The structures depend on `struct uart_port`, `spinlock_t`, and `atomic_t` when included in the kernel build. Constants are tightly integrated with the Z85C30 hardware manual and the DECstation IOASIC driver implementation. The baud macros are consumed by termios and validation logic in `zs.c`.

## Risks and Edge Cases

Bit definitions are hardware ABI. A wrong mask can misprogram interrupts, clocking, parity, stop bits, or modem signals. Some names encode historical SCC terminology, so confusing read-register and write-register meanings is easy. The baud macros assume valid nonzero baud and frequency inputs and do not protect against divide-by-zero. Structure layout is private to this driver, but changes must preserve all users in `zs.c`, especially the shared lock and register shadow assumptions.

## Test Signals

Build coverage of `zs.c` is the primary signal. Targeted validation should check baud macro calculations, register-shadow initialization against expected Z85C30 values, interrupt-mask constants against observed RR3/RR0 behavior, modem and break bit interpretation, and compile coverage with and without `CONFIG_SERIAL_ZS_CONSOLE`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/zs.h -->
