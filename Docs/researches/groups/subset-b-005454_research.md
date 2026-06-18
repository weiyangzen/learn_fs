# subset-b-005454 Research

Grouped source research for AMBA PL010/PL011, GRLIB APBUART, AR933x, ARC, and Atmel serial drivers. Each source file has its own marker-delimited section for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/amba-pl010.c -->
# sources/distributed-fs/ceph-client/drivers/tty/serial/amba-pl010.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/tty/serial/amba-pl010.c` is the Linux serial-core driver for ARM AMBA PL010 UARTs. It binds AMBA devices with PrimeCell ID `0x00041010`, exposes up to eight `ttyAM` ports, supports optional console output, and handles a simple interrupt-driven RX/TX datapath. The source was read as a complete 804-line file.

## Important APIs, Types, and Functions

The private wrapper is `struct uart_amba_port`, containing the generic `struct uart_port`, the UART clock, AMBA device pointer, optional platform callbacks, and cached modem status. The serial-core operation table is `amba_pl010_pops`, implemented by `pl010_startup()`, `pl010_shutdown()`, `pl010_set_termios()`, `pl010_start_tx()`, `pl010_stop_tx()`, `pl010_stop_rx()`, `pl010_enable_ms()`, `pl010_get_mctrl()`, `pl010_set_mctrl()`, `pl010_break_ctl()`, and port request/config/verify helpers. Runtime data movement is in `pl010_rx_chars()`, `pl010_tx_chars()`, `pl010_modem_status()`, and `pl010_int()`. Device lifetime is rooted in `pl010_probe()`, `pl010_remove()`, `pl010_suspend()`, and `pl010_resume()`.

## Control Flow

Probe finds a free slot in the static `amba_ports[]`, allocates and maps the AMBA resource, obtains the clock, fills the `uart_port`, registers the shared `uart_driver` lazily, and calls `uart_add_one_port()`. Startup prepares/enables the clock, stores the live UART clock rate, requests the IRQ, snapshots modem status, and enables UART, receive, and receive-timeout interrupts. The interrupt handler locks the port, reads `UART010_IIR`, and loops up to `AMBA_ISR_PASS_LIMIT`, dispatching RX, modem-status, and TX work before rereading pending status.

RX drains the data register while `UART01x_FR_RXFE` is clear, updates `icount`, clears receive errors through `UART01x_ECR`, classifies break/parity/frame/overrun conditions using the current read/ignore masks, honors sysrq, inserts chars into the TTY flip buffer, and pushes the buffer after the drain. TX uses `uart_port_tx_limited()` with half the FIFO as the chunk limit. Termios computes the baud divisor with serial-core helpers, programs word length, stop bits, parity, FIFO enable, read/ignore masks, modem status interrupt enable, and writes LCRM/LCRL before LCRH as required by the hardware. Shutdown frees the IRQ, disables the UART and FIFOs/break, then disables the clock.

## State and Persistence Behavior

State is in the static `amba_ports[]`, the serial-core `uart_state`, `old_status`, UART registers, and the clock enable count. There is no file-backed persistence. Console setup may prepare the clock and infer baud/parity/bits from bootloader-programmed registers. Suspend/resume delegates to `uart_suspend_port()` and `uart_resume_port()`, so open-port configuration is restored through serial-core paths rather than custom persistent storage.

## Dependencies and Integration Points

The driver integrates with the AMBA bus, `serial_core`, TTY flip buffers, Linux clock APIs, AMBA platform data (`struct amba_pl010_data`) for external modem control outputs, optional `CONFIG_SERIAL_AMBA_PL010_CONSOLE`, sysrq, and generic PM. Register definitions come from `<linux/amba/serial.h>`.

## Risks and Edge Cases

`pl010_disable_ms()` casts `struct uart_port *` directly to `struct uart_amba_port *`, relying on the wrapper embedding `uart_port` as the first field. The device has no native DTR/RTS outputs, so modem output correctness depends on platform callbacks. Interrupt storms are bounded by `AMBA_ISR_PASS_LIMIT`, but persistent status bits can delay work. CREAD masking uses `UART_DUMMY_RSR_RX`; RX still drains hardware but suppresses delivery. Console writes temporarily alter control register state and rely on clock enable/disable balancing.

## Test Signals

Useful validation includes AMBA probe/remove with multiple PL010 ports, open/close clock and IRQ balancing, RX error injection for break/parity/frame/overrun, TX wakeup behavior, termios changes across baud/parity/data bits, modem-status change handling, N_PPS line discipline enabling hard PPS on DCD, suspend/resume of open and console ports, and console boot output with and without command-line options.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/amba-pl010.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/amba-pl011.c -->
# sources/distributed-fs/ceph-client/drivers/tty/serial/amba-pl011.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/tty/serial/amba-pl011.c` is the full Linux serial-core driver for ARM PL011-family UARTs, including ARM, ST-Ericsson, NVIDIA, SBSA UART, ACPI SPCR/QDF2400 erratum handling, DMA, RS485, console, earlycon, polling, and PM support. It exposes up to fourteen `ttyAMA` ports. The source was read as a complete 3223-line file.

## Important APIs, Types, and Functions

`struct vendor_data` captures register offsets, FIFO thresholds, flag bit meanings, access width, oversampling, DMA threshold quirks, always-enabled/fixed-option SBSA behavior, and optional FIFO sizing. `struct uart_amba_port` wraps `uart_port` and stores vendor offsets, clock, interrupt mask, FIFO size, RS485 timers/state, console tracking, and optional DMA state. DMA support is split into `struct pl011_dmatx_data`, `struct pl011_dmarx_data`, and `struct pl011_dmabuf`.

Core data paths include `pl011_fifo_to_tty()`, `pl011_rx_chars()`, `pl011_tx_chars()`, `pl011_int()`, `pl011_dma_tx_refill()`, `pl011_dma_tx_callback()`, `pl011_dma_rx_trigger_dma()`, `pl011_dma_rx_irq()`, `pl011_dma_rx_callback()`, and `pl011_dma_rx_poll()`. Serial-core ops are `amba_pl011_pops` and `sbsa_uart_pops`. Probe/register paths are `pl011_probe()`, `pl011_setup_port()`, `pl011_register_port()`, `sbsa_uart_probe()`, `pl011_remove()`, and `sbsa_uart_remove()`.

## Control Flow

AMBA probe chooses a free line, allocates a port, gets the clock, selects vendor data from AMBA ID, handles `reg-io-width`, initializes RS485 hrtimers, maps resources, registers the shared UART driver if needed, and adds the port. SBSA probe follows a platform-driver path, requires or defaults a fixed baud rate, uses 32-bit access, and avoids control-register programming that firmware owns.

Startup runs `pl011_hwinit()` to select pinctrl default state, enable the clock, clear pending errors/RX status, seed interrupt masks, and run platform `init()`. It requests a shared IRQ, programs FIFO trigger levels, enables UART/RX/TX according to RS485 mode, snapshots modem inputs, starts DMA if channels and buffers are available, and enables RX/timeout interrupts. IRQ handling reads raw status masked by `uap->im`, applies the ST CTS workaround if needed, clears non-RX/TX status, drains RX via DMA or PIO, updates modem state, and services TX.

TX favors DMA when enough queued data exists; otherwise PIO sends an x_char and then FIFO data, stopping TX interrupts when the queue empties. RX DMA uses alternating coherent page buffers, residue checks, DMA pause/terminate on timeout interrupts, a completion callback for full buffers, and an optional polling timer that falls back to interrupt mode after inactivity. RS485 uses `trigger_start_tx` and `trigger_stop_tx` hrtimers to honor before/after-send delays, gate RTS polarity, and optionally disable RX during transmit.

Termios computes baud based on 8x/16x oversampling and optional clock-rate programming, updates status masks, hardware flow control bits, ST oversampling bits, integer/fractional divisors unless the vendor skips them, and writes LCRH after divisors. Shutdown masks interrupts, stops DMA, stops RS485 transmit, frees IRQ, disables UART/FIFOs/break where allowed, disables clocks and pinctrl, runs platform `exit()`, and flushes DMA buffers.

## State and Persistence Behavior

State is held in `amba_ports[]`, per-port interrupt mask `im`, DMA channel/buffer state, hrtimers, cached modem status, console `console_line_ended`, UART registers, and clock/pinctrl state. No disk persistence exists. Hardware register state is deliberately preserved for SBSA always-enabled ports and for console/earlycon handoff. PM calls serial-core suspend/resume, with console paths able to run through nbcon atomic/threaded writers at any time.

## Dependencies and Integration Points

The driver depends on AMBA, platform devices, ACPI, OF aliases, serial core, TTY flip buffers, DMAengine, clocks, pinctrl, earlycon, nbcon console APIs, sysrq, and optional AMBA platform data. It integrates with ACPI SPCR through SBSA and QDF2400 E44 early console matching, and with device tree through `arm,pl011`, `arm,sbsa-uart`, and serial aliases.

## Risks and Edge Cases

High-risk areas are DMA fallback and residue accounting, RX FIFO threshold behavior after startup, RS485 timer/state transitions under concurrent TX stop/start, vendor register-offset differences, ST split LCRH ordering and CTS workaround, NVIDIA clock programming and skipped divisors, SBSA fixed-options behavior, and QDF2400 E44 inverted/busy flag handling. `amba_ports[]` is shared by AMBA and SBSA paths; alias collisions are warned but enumeration can still be surprising.

## Test Signals

Strong signals include probe on ARM/ST/NVIDIA/SBSA variants, 8-bit and 32-bit register access, DMA TX/RX with fallback injection, RX timeout and poll-mode behavior, high-baud ST oversampling, RS485 before/after delay and RX-during-TX combinations, modem status interrupts, console and earlycon takeover including QDF2400 E44, suspend/resume with console active, OF alias conflicts, and fault injection around clock, IRQ, DMA channel, and UART registration failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/amba-pl011.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/apbuart.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/apbuart.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/apbuart.h -->
# sources/distributed-fs/ceph-client/drivers/tty/serial/apbuart.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/tty/serial/apbuart.h` is the local register contract for the GRLIB APBUART serial driver. It defines the memory layout, firmware register property shape, status/control bits, and raw MMIO accessor macros used by `apbuart.c`. The source was read as a complete 65-line file.

## Important APIs, Types, and Functions

The header defines `UART_NR` as eight ports and declares the file-scope `grlib_apbuart_port_nr`. `struct grlib_apbuart_regs_map` models the four 32-bit APBUART registers: `data`, `status`, `ctrl`, and `scaler`. `struct amba_prom_registers` models the OF `reg` payload consumed by the driver. Macros define status flags (`UART_STATUS_DR`, `THE`, `BR`, `OE`, `PE`, `FE`, and `ERR`) and control flags (`RE`, `TE`, `RI`, `TI`, parity, flow control, loopback). Accessors such as `UART_GET_CHAR()`, `UART_PUT_CTRL()`, and `UART_PUT_SCAL()` use `__raw_readl()`/`__raw_writel()`.

## Control Flow

There is no executable control flow in the header. It shapes the driver's control flow by providing predicates `UART_RX_DATA()` and `UART_TX_READY()` and by mapping a `uart_port`'s `membase` into typed APBUART register pointers.

## State and Persistence Behavior

The header itself owns no runtime state except the unusual `static int grlib_apbuart_port_nr` definition, which becomes a private variable in each translation unit that includes it. In this tree it is included by `apbuart.c`, so it backs the driver's discovered port count for the module lifetime. Hardware state is represented by status/control/scaler registers only.

## Dependencies and Integration Points

It includes `<asm/io.h>` and assumes Linux integer types are available. It is tightly coupled to `apbuart.c`; moving it to a shared include context would require care because of the `static` variable definition.

## Risks and Edge Cases

The raw accessors impose no endian conversion or barriers beyond raw MMIO semantics. Incorrect struct layout would make every register access wrong. The APBBASE macros depend on `membase` being valid and mapped to at least `sizeof(struct grlib_apbuart_regs_map)`. The header-level `static int` is safe for single-user inclusion but would be surprising if included by multiple C files.

## Test Signals

Build coverage of `apbuart.c`, register read/write smoke tests on APBUART hardware, status/control bit toggling, scaler programming, and sparse/compile checks around the header's static variable are the relevant signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/apbuart.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/ar933x_uart.c -->
# sources/distributed-fs/ceph-client/drivers/tty/serial/ar933x_uart.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/tty/serial/ar933x_uart.c` is the platform serial driver for the Atheros/Qualcomm AR933x SoC UART. It exposes `ttyATH` ports, programs the AR933x fractional clock/step baud generator, supports GPIO-backed modem control, optional RS485 half-duplex RTS handling, console output, and console polling. The source was read as a complete 940-line file.

## Important APIs, Types, and Functions

`struct ar933x_uart_port` wraps `uart_port` with an interrupt-enable shadow `ier`, min/max baud limits, a UART clock, modem-control GPIOs, and an RTS GPIO descriptor. Register helpers are `ar933x_uart_read()`, `ar933x_uart_write()`, and read-modify-write variants. Serial-core ops are in `ar933x_uart_ops`, including TX/RX start/stop, termios, break, poll, and config/verify functions. Data movement is in `ar933x_uart_rx_chars()`, `ar933x_uart_tx_chars()`, and `ar933x_uart_interrupt()`. Probe/remove and module registration are in `ar933x_uart_probe()`, `ar933x_uart_remove()`, `ar933x_uart_init()`, and `ar933x_uart_exit()`.

## Control Flow

Probe obtains the line number from the OF `serial` alias or platform ID, validates it against `CONFIG_SERIAL_AR933X_NR_UARTS`, gets the IRQ, allocates the wrapper, gets/enables the `uart` clock, maps MMIO, fills `uart_port`, computes supported baud limits from hardware scale/step extremes, reads RS485 mode from firmware, initializes modem GPIOs, disables RS485 if no RTS GPIO exists, registers the console port pointer when configured, and adds the UART port.

Termios forces CS8 and one stop bit, supports none/even/odd parity only, clears mark/space parity, searches scale/step values for the closest baud, disables the interface while programming clock and parity, updates timeout and CREAD masking, enables host interrupts and ready overrides, then re-enables DCE mode. Startup requests the IRQ, enables host interrupt and ready override bits, and enables RX interrupts. IRQ handling first checks the host-interrupt latch, then locks the port, masks interrupt status by the shadow enable register, clears RX/TX interrupt bits, drains RX, and services TX; `uart_unlock_and_check_sysrq()` handles deferred sysrq.

RX drains up to 256 valid chars by reading `DATA_REG`, acknowledging each RX character by writing `RX_CSR`, and inserting normal chars unless CREAD masking is active. TX handles x_char and FIFO data while `DATA_TX_CSR` says space is available. When RS485 is enabled and data exists, it disables RX interrupts, drives RTS to the configured send polarity, transmits, waits for TX complete, flushes RX, reenables RX interrupts, and drives RTS to the after-send polarity.

## State and Persistence Behavior

State lives in the allocated port wrapper, shadow `ier`, clock enable state, GPIO descriptors, RS485 config in `uart_port.rs485`, and hardware registers. There is no file persistence. Console state is stored in a static array indexed by line and is populated at probe time. Remove unregisters the port and disables the clock.

## Dependencies and Integration Points

The driver depends on platform/OF APIs, clock APIs, serial core, TTY flip buffers, sysrq, GPIO modem-control helpers from `serial_mctrl_gpio.h`, AR933x register definitions from `<asm/mach-ath79/ar933x_uart.h>`, and optional console/poll configuration. It matches `qca,ar9330-uart`.

## Risks and Edge Cases

The baud search is brute force over scale values and depends on valid clock rate. TX-complete waits use fixed 60 ms polling timeouts, so wedged hardware can delay interrupt/console paths. RS485 depends on an RTS GPIO; firmware enabling RS485 without one is corrected by probe. RX has no parity/frame error classification in this driver. Console write disables interrupts and must restore interrupt enable state even during oops trylock paths.

## Test Signals

Relevant tests include OF alias numbering, clock failure and zero-rate handling, baud accuracy across min/max limits, RX/TX interrupt loopback, CREAD suppression, RS485 RTS polarity and RX flush behavior, modem GPIO get/set, console output under normal and oops paths, poll get/put, and removal clock balancing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/ar933x_uart.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/arc_uart.c -->
# sources/distributed-fs/ceph-client/drivers/tty/serial/arc_uart.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/tty/serial/arc_uart.c` is the serial-core driver for Synopsys ARC on-chip FPGA UART hardware. It provides `ttyARC` ports, interrupt-driven RX/TX, console and earlycon support, and optional console polling for a small non-16550-compatible register set. The source was read as a complete 671-line file.

## Important APIs, Types, and Functions

The private object is `struct arc_uart_port`, wrapping `uart_port` plus the configured baud. Register macros describe 8-bit word-aligned registers `R_DATA`, `R_STS`, `R_BAUDL`, and `R_BAUDH`, with bits for RX/TX interrupt enable, FIFO empty/full, frame error, and overrun. Serial-core operations are `arc_serial_pops`, implemented by TX/RX start/stop, `arc_serial_tx_empty()`, `arc_serial_set_termios()`, modem stubs, break stub, startup/shutdown, config/verify, and poll helpers. Platform integration is through `arc_serial_probe()`, `arc_serial_init()`, and `arc_serial_exit()`.

## Control Flow

Module init registers the UART driver and then the platform driver. Probe requires an OF node, derives the line from the `serial` alias or defaults to zero, reads `clock-frequency` and `current-speed`, maps the MMIO resource, maps the IRQ, fills the static port entry, sets FIFO size to one for TX, initializes ignore masks, and adds the port.

Startup disables all UART interrupts, requests the shared RX/TX ISR, and enables only RX interrupts initially. The ISR reads status, handles RX when RX interrupts are enabled, and handles TX when TX interrupts are enabled and the TX register is empty. RX loops until `RXEMPTY`, clearing and accounting overrun/frame errors, reading chars, honoring sysrq, inserting into the TTY flip buffer, and pushing. TX is dynamic: start_tx writes one x_char or FIFO byte and enables TX interrupt if data was sent; TX ISR disables TX interrupts first, then calls the same TX helper, which reenables them only if more data was sent.

Termios obtains a baud from serial core, programs two baud registers using the ARC formula `CLK/(baud*4)-1`, disables all interrupts during programming, reenables RX interrupts, forces 8N1 and no hardware flow control/parity, copies old hardware settings when present, encodes baud back into termios, and updates the timeout.

## State and Persistence Behavior

State is static in `arc_uart_ports[]` and hardware registers. No persistent storage exists. The console path can be deferred until the backing port has a mapped `membase`. Earlycon programs baud registers from the early console baud and writes directly through the same polling putchar path.

## Dependencies and Integration Points

The driver depends on platform devices, OF address/IRQ helpers, serial core, TTY flip buffers, console/earlycon APIs, sysrq, and MMIO byte accessors. It matches `snps,arc-uart`.

## Risks and Edge Cases

`arc_serial_set_termios()` stores the requested baud in a local `baud` but calculates `hw_val` from `uart->baud`, which is initialized from the `current-speed` property; this means runtime baud changes deserve scrutiny. `arc_serial_poll_getchar()` loops while `!(status & RXEMPTY)`, which appears inverted for waiting on available data and could return stale/invalid data. The hardware has no real modem control, break generation, parity, or flow control. TX FIFO size is one, so interrupt pacing is sensitive to missed TX-empty events.

## Test Signals

Test signals include OF property validation, boot console and regular console handoff, RX/TX loopback, TX interrupt enable/disable sequencing, frame/overrun accounting, runtime termios baud changes, poll get/put behavior, multiport alias bounds, and startup/shutdown IRQ balancing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/arc_uart.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/atmel_serial.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/atmel_serial.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/atmel_serial.h -->
# sources/distributed-fs/ceph-client/drivers/tty/serial/atmel_serial.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/tty/serial/atmel_serial.h` defines the Atmel/Microchip USART/UART register offsets, control/status bits, mode fields, FIFO fields, and helper field macros consumed by `atmel_serial.c`. The source was read as a complete 171-line file.

## Important APIs, Types, and Functions

The header is macro-only. It defines control-register commands such as `ATMEL_US_RSTRX`, `RXEN`, `TXEN`, `RSTSTA`, break control, DTR/RTS control, and FIFO enable/clear bits. Mode-register fields cover USART mode selection (`NORMAL`, `RS485`, `HWHS`, `MODEM`, `ISO7816_T0/T1`, `IRDA`), clock source, character length, parity variants, stop bits, channel mode, oversampling, ISO7816 ACK behavior, max iterations, and filters. Interrupt/status definitions cover RX/TX readiness, DMA/PDC completion, break, overrun/frame/parity errors, timeout, TX empty, ISO7816 iteration/NACK, and modem input changes. Additional definitions cover baud generator, timeout, timeguard, FIDI, FIFO mode/level/interrupt registers, IP name, and version.

## Control Flow

There is no executable control flow in the header. `atmel_serial.c` uses these constants to build mode words, issue write-only control commands, mask/unmask interrupts, classify RX errors, configure baud and ISO7816 parameters, and program FIFO thresholds.

## State and Persistence Behavior

The header owns no state. It describes hardware state that persists in MMIO registers until reset, power management, or explicit driver writes. Some registers are command-style write-only controls, while others are latched status or configuration registers.

## Dependencies and Integration Points

The header includes `<linux/bitfield.h>` and uses `BIT()`, `GENMASK()`, `FIELD_PREP()`, and `FIELD_GET()` to keep field definitions explicit. It is tightly integrated with the Atmel serial driver and any other local code that needs the same USART register contract.

## Risks and Edge Cases

Incorrect offsets or masks would corrupt core serial behavior, especially because many control register bits are write commands rather than persistent readable configuration. UART and USART variants reuse offsets differently, for example `ATMEL_US_RTOR`, `ATMEL_UA_RTOR`, and `ATMEL_US_TTGR`. FIFO threshold helpers assume caller-provided values fit field widths. Mode constants built with `FIELD_PREP()` must stay aligned with hardware documentation.

## Test Signals

Build coverage, register readback on supported AT91/SAMA5 variants, termios mode programming, FIFO threshold behavior, ISO7816 configuration, RS485 mode switching, interrupt mask/status handling, and suspend/resume register-cache restoration validate this header contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/atmel_serial.h -->
