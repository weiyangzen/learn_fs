# Research Group: subset-b-005455

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/bcm63xx_uart.c -->
# sources/distributed-fs/ceph-client/drivers/tty/serial/bcm63xx_uart.c

Purpose: Broadcom BCM63xx integrated UART driver for up to two `ttyS` ports. It implements Linux serial-core `uart_ops`, a platform driver matched by `brcm,bcm6345-uart`, optional boot/early console support, and console-poll hooks.

Important APIs, types, and functions: the file keeps global `struct uart_port ports[BCM63XX_NR_UARTS]` and uses register definitions from `linux/serial_bcm63xx.h`. The `bcm_uart_ops` callbacks cover TX/RX control, modem control, termios, startup/shutdown, port verification, and optional `poll_get_char`/`poll_put_char`. Key hardware helpers are `bcm_uart_readl()` and `bcm_uart_writel()`. Interrupt work is split into `bcm_uart_do_rx()`, `bcm_uart_do_tx()`, and `bcm_uart_interrupt()`. Probe/remove are `bcm_uart_probe()` and `bcm_uart_remove()`, while console paths are `bcm_console_write()`, `bcm_console_setup()`, `bcm_early_write()`, and `bcm_early_console_setup()`.

Control flow: module init registers the `uart_driver` and then the platform driver. Probe derives the line from DT aliases, maps MMIO, obtains IRQ and clock, initializes `uart_port`, and calls `uart_add_one_port()`. Startup disables the UART, masks interrupts, resets FIFOs, configures thresholds/timeouts/external-input edge reporting, requests the IRQ, enables RX interrupts, and enables RX/TX/baud generation. The IRQ handler locks the port, dispatches RX FIFO drain, TX FIFO fill, and CTS/DCD change handling, then unlocks with SysRq processing. Shutdown masks interrupts, disables hardware, flushes FIFOs, and frees the IRQ.

State and persistence: persistent state is in the global `ports` array and hardware registers. Runtime masks live in `port->read_status_mask` and `port->ignore_status_mask`; counters live in `port->icount`; TX data comes from the serial-core xmit FIFO. There is no disk persistence. Probe marks an occupied slot by non-NULL `membase`; remove clears it.

Dependencies and integration points: depends on platform/DT resources, common clock APIs, serial core, TTY flip buffers, SysRq, console core, and Broadcom register layout. It integrates with DT through `brcm,bcm6345-uart` and `serial`/`uart` aliases. Console registration uses `console_initcall()` when enabled; early console uses `OF_EARLYCON_DECLARE`.

Risks: hardware flow control was explicitly untested in the file header. `set_termios()` busy-waits for TX empty before reprogramming and can delay under broken hardware. Error masking must stay aligned with FIFO status bits, especially break/parity/frame handling. Console and oops paths rely on careful trylock behavior. Clock lifetime is limited to reading the rate, so runtime clock management is not present here.

Test signals: useful checks include booting with DT aliases for both ports, interrupt-driven RX/TX, CTS/DCD modem status changes, console output under normal and oops paths, earlycon output, poll-console operation, termios changes for baud/data bits/parity/stop bits, RX overrun/error injection, and remove/reprobe slot cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/bcm63xx_uart.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/clps711x.c -->
# sources/distributed-fs/ceph-client/drivers/tty/serial/clps711x.c

Purpose: CLPS711x/EP7209 UART serial driver exposing two `ttyCL` ports through the serial core. It handles memory-mapped UART data/control registers plus CLPS711x syscon bits, optional modem-control GPIOs, and optional console support.

Important APIs, types, and functions: `struct clps711x_port` embeds `struct uart_port` and stores `tx_enabled`, a separate RX IRQ, a `struct regmap *syscon`, and `struct mctrl_gpios *gpios`. `uart_clps711x_ops` supplies serial-core callbacks. TX/RX handlers are `uart_clps711x_int_tx()` and `uart_clps711x_int_rx()`. Setup functions include `uart_clps711x_startup()`, `uart_clps711x_shutdown()`, `uart_clps711x_set_termios()`, and `uart_clps711x_set_ldisc()` for IrDA line-discipline switching on line 0. Probe/remove are `uart_clps711x_probe()` and `uart_clps711x_remove()`.

Control flow: module init optionally wires the console into `clps711x_uart`, registers the `uart_driver`, and registers the platform driver. Probe allocates per-port state, fetches clock/MMIO/TX IRQ/RX IRQ/syscon, initializes GPIO modem control, adds the serial port, disables the hardware unless it is a console, then requests TX and RX IRQs. Startup clears break and enables the UART via `SYSCON_UARTEN`. RX IRQ loops until `SYSFLG_URXFE` says empty, reads `UARTDR`, classifies parity/frame/overrun, handles SysRq, and pushes flip data. TX IRQ writes `x_char` first, then drains the xmit FIFO until `SYSFLG_UTXFF` says full, disabling TX IRQ when idle.

State and persistence: all persistent runtime state is per-device memory plus syscon/hardware registers. `tx_enabled` mirrors whether the TX IRQ is enabled. Serial settings are encoded in `UBRLCR`; termios masks live in `uart_port`. No persistent storage is used.

Dependencies and integration points: uses platform resources, device tree compatible `cirrus,ep7209-uart`, syscon phandle named `syscon`, common clock, regmap, `serial_mctrl_gpio`, serial core, TTY flip buffers, and optional console core. Modem signals are delegated to the generic mctrl GPIO helper.

Risks: TX and RX use separate IRQs; incorrect DT IRQ order breaks the driver. `tx_enabled` must stay synchronized with IRQ enable/disable calls. Syscon bits are shared hardware state, so incorrect phandle/register definitions affect enable and IrDA mode. Unsupported termios features are masked in place.

Test signals: validate both IRQs, syscon enable/disable, GPIO modem control, IrDA line-discipline selection on port 0, console setup with and without bootloader-provided settings, RX parity/frame/overrun paths, TX wakeup thresholds, and unload/remove after active use.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/clps711x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/cpm_uart.c -->
# sources/distributed-fs/ceph-client/drivers/tty/serial/cpm_uart.c

Purpose: Freescale CPM1/CPM2 SCC/SMC UART driver for PowerPC CPM communication processors. It implements `ttyCPM` serial ports backed by CPM parameter RAM, CPM buffer descriptors, coherent/DPRAM data buffers, optional console/poll/udbg support, optional GPIO modem lines, and OF platform binding for `fsl,cpm*-smc-uart` and `fsl,cpm*-scc-uart`.

Important APIs, types, and functions: the main state type is `struct uart_cpm_port` from `cpm_uart.h`; the C file owns `static struct uart_cpm_port cpm_uart_ports[UART_NR]`. `cpm_uart_pops` is the serial-core operation table. Important flows include `cpm_uart_startup()`, `cpm_uart_shutdown()`, `cpm_uart_set_termios()`, `cpm_uart_tx_pump()`, `cpm_uart_int_rx()`, `cpm_uart_int()`, `cpm_uart_allocbuf()`, `cpm_uart_initbd()`, `cpm_uart_init_smc()`, `cpm_uart_init_scc()`, `cpm_uart_map_pram()`, and `cpm_uart_init_port()`. Console-specific code uses `cpm_uart_early_write()` and `cpm_uart_console_setup()`.

Control flow: module init registers the `uart_driver` and OF platform driver. Probe assigns a sequential `probe_index`, maps IRQ, initializes the CPM port from DT, then adds it to serial core. `cpm_uart_init_port()` finds clock or BRG, reads CPM command opcode, maps SMC/SCC registers and parameter RAM, configures GPIO modem descriptors, initializes `uart_port`, and calls `cpm_uart_request_port()`. Request-port disables hardware, allocates MURAM descriptors plus host/DPRAM data buffers, initializes descriptors, and configures SMC or SCC parameter registers. Startup reinitializes descriptors for non-console ports, requests the IRQ, and enables RX/TX hardware. The IRQ handler acknowledges SMC/SCC events and dispatches break, RX, and TX handling. RX walks completed buffer descriptors, copies bytes into the TTY flip buffer, processes errors/SysRq, and returns descriptors to CPM ownership. TX fills available descriptors from `x_char` or the xmit FIFO and enables/disables TX interrupts as needed.

State and persistence: state spans `uart_cpm_port`, CPM hardware registers, CPM parameter RAM, MURAM buffer descriptors, coherent/DPRAM buffers, clock/BRG selection, and optional GPIO descriptors. Descriptor ownership bits are the core producer/consumer state. Console ports are flagged with `FLAG_CONSOLE` and use special allocation and shutdown paths. Poll mode has static `serial_polled`, `poll_buf`, `pollp`, `poll_chars`, and optional `udbg_port`. No disk persistence exists.

Dependencies and integration points: depends on CPM architecture headers, MURAM APIs, CPM commands, OF address/IRQ/platform APIs, DMA mapping, memblock-era console allocation behavior, GPIO descriptors, clocks, serial core, TTY flip buffers, console, SysRq, and PowerPC udbg. DT must supply compatible, register resources, parameter RAM resource, `fsl,cpm-command`, and either `clock` or `fsl,cpm-brg`.

Risks: CPM descriptor ownership is fragile; incorrect memory translation in `cpu2cpm_addr()`/`cpm2cpu_addr()` hits `BUG()`. Console allocation/freeing differs from normal DMA paths. `probe_index` assumes stable probe order and no more than `UART_NR` ports. The RX path can stop early if flip-buffer space is insufficient. Parameter RAM mapping has compatibility fallback behavior for old CPM2 SMC DTs. Shutdown waits for TX descriptors and can sleep.

Test signals: cover SMC and SCC variants, CPM1/CPM2 builds, console and non-console allocation paths, DT validation failures, RX/TX descriptor wraparound, low-latency and low-baud RX buffer sizing, GPIO modem signals, poll console/udbg, termios parity/stop/baud updates, break handling, remove after probe failure, and IRQ event acknowledgement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/cpm_uart.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/cpm_uart.h -->
# sources/distributed-fs/ceph-client/drivers/tty/serial/cpm_uart.h

Purpose: shared header for the CPM SCC/SMC UART driver. It defines constants, feature flags, FIFO sizes, modem GPIO indexes, the `struct uart_cpm_port` state container, and address-translation helpers between CPU virtual buffer addresses and CPM/DMA bus addresses.

Important APIs, types, and functions: `struct uart_cpm_port` embeds `struct uart_port` and tracks SMC/SCC register pointers, parameter RAM pointers, RX/TX buffer descriptor bases and cursors, backing TX/RX buffers, flags, clock/BRG command metadata, allocation bookkeeping, wait-on-close delay, and optional modem GPIO descriptors. Macros include `SERIAL_CPM_MAJOR`, `SERIAL_CPM_MINOR`, `UART_NR`, `RX_NUM_FIFO`, `RX_BUF_SIZE`, `TX_NUM_FIFO`, `TX_BUF_SIZE`, `FLAG_SMC`, `FLAG_CONSOLE`, `IS_SMC()`, and GPIO indexes. `cpu2cpm_addr()` and `cpm2cpu_addr()` validate addresses against the allocated host buffer span and translate by offset.

Control flow: the header itself has no runtime entry point, but every CPM UART path depends on the state layout. Allocation fills `mem_addr`, `dma_addr`, and `mem_size`; descriptor initialization calls `cpu2cpm_addr()` to program buffer addresses; RX/TX paths call `cpm2cpu_addr()` to access buffers from descriptor bus addresses.

State and persistence: the structure is the persistent in-memory identity of a CPM UART port. It stores both hardware-facing state and serial-core state for the lifetime of the device or console. Address helpers enforce that only buffers inside the allocated span are translated.

Dependencies and integration points: conditionally includes `asm/cpm1.h` or `asm/cpm2.h`, exposes `DPRAM_BASE` through `cpm_muram_addr(0)`, forward-declares `struct gpio_desc`, and includes platform-device support. It is tightly coupled to `cpm_uart.c` and the CPM architecture register types.

Risks: translation helpers cast pointers and DMA addresses to `u32`, which matches the legacy CPM environment but is not a general 64-bit-safe abstraction. On invalid addresses they call `BUG()`, so corruption becomes a kernel crash. Constants define small fixed descriptor/buffer counts that shape latency and throughput.

Test signals: validate descriptor address round-trips, SMC/SCC flag-dependent paths, console flag paths, GPIO index ordering, CPM1 and CPM2 compilation, and all callers that mutate `mem_addr`, `dma_addr`, or `mem_size`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/cpm_uart.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/digicolor-usart.c -->
# sources/distributed-fs/ceph-client/drivers/tty/serial/digicolor-usart.c

Purpose: Conexant Digicolor USART platform serial driver for up to three `ttyS` ports. It provides interrupt-driven TX/RX, console support, and a delayed-work RX poll workaround for hardware whose RX interrupt threshold cannot be set below half FIFO.

Important APIs, types, and functions: `struct digicolor_port` embeds `struct uart_port` and `struct delayed_work rx_poll_work`. Global `digicolor_ports[]` backs console lookup. `digicolor_uart_ops` provides serial callbacks. Core functions are `digicolor_uart_rx()`, `digicolor_uart_tx()`, `digicolor_uart_int()`, `digicolor_rx_poll()`, `digicolor_uart_startup()`, `digicolor_uart_shutdown()`, `digicolor_uart_set_termios()`, `digicolor_uart_probe()`, and `digicolor_uart_remove()`.

Control flow: init optionally attaches a console, registers the UART driver, and registers the platform driver. Probe requires a DT node and `serial` alias, maps MMIO, obtains clock and IRQ, initializes the port, stores it for console lookup, initializes delayed work, requests the IRQ, and adds the port. Startup enables the peripheral, soft-resets it, configures FIFO mode/thresholds, enables RX/TX and interrupts, and schedules periodic RX polling. The poll work forces an RX interrupt when FIFO data is present below the hardware threshold. The IRQ clears RX/TX flags and dispatches RX/TX handlers. Shutdown disables the device and cancels delayed work synchronously.

State and persistence: state is per-port memory plus the delayed work item and hardware registers. The RX polling cadence is fixed at 100 ms. Termios state is represented by hardware config/divisor registers and serial-core masks. No persistent storage is used.

Dependencies and integration points: depends on DT compatible `cnxt,cx92755-usart`, clocks, platform IRQ/MMIO, workqueues, serial core, TTY flip buffers, and console core. It exposes `PORT_DIGICOLOR` and uses `ttyS` naming.

Risks: RX latency depends on the 100 ms poll workaround when traffic remains below FIFO threshold. The driver does not implement real modem control; `get_mctrl()` reports CTS. Break control is empty. Error handling uses a single status register snapshot per character and only one error class wins due to `else if` ordering. Console name `ttyS` can overlap with other serial drivers if platform numbering is wrong.

Test signals: verify low-rate RX below FIFO threshold, periodic work cancellation on shutdown/remove, TX interrupt disable on idle, console output and setup, baud divisor limits, parity/frame/overrun reporting, DT alias bounds, and behavior when no DT node is present.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/digicolor-usart.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/dz.c -->
# sources/distributed-fs/ceph-client/drivers/tty/serial/dz.c

Purpose: DECstation DZ chipset serial driver. It exposes four muxed `ttyS` lines behind one DZ device and one shared IRQ, supports optional console output, and integrates with MIPS DECstation machine resources.

Important APIs, types, and functions: `struct dz_port` embeds a `struct uart_port`, cached line parameter `cflag`, and a parent `struct dz_mux *`. `struct dz_mux` owns four ports plus atomic guards for shared MMIO mapping and IRQ ownership. `dz_ops` supplies serial-core callbacks. Key functions include `dz_receive_chars()`, `dz_transmit_chars()`, `dz_interrupt()`, `dz_startup()`, `dz_shutdown()`, `dz_set_termios()`, `dz_request_port()`, `dz_release_port()`, `dz_config_port()`, `dz_reset()`, and console helpers `dz_console_putchar()` and `dz_console_setup()`.

Control flow: init exits on IOASIC machines, initializes port descriptors based on DECstation machine type, registers the UART driver, and adds four ports. Each line shares the same MMIO base and IRQ. Request-port uses `map_guard` so the memory region and ioremap are acquired once for the mux. Startup uses `irq_guard` so the shared IRQ is requested once and enables DZ receive/transmit interrupts. The interrupt handler reads CSR, drains receive data for any line with `DZ_DVAL`, and transmits one character for the line identified by `DZ_TLINE` when ready. Shutdown disables per-line TX and releases the shared IRQ when the final open user closes.

State and persistence: global `dz_mux` is the durable runtime state. Per-line `cflag` caches line-parameter register settings, while atomic guards track shared resource users. Hardware line parameters and transmitter enables are held in DZ registers. There is no persistent storage.

Dependencies and integration points: depends on DECstation MIPS headers, `dec_kn_slot_base`, `dec_kn_slot_size`, `dec_interrupt`, machine type detection, PROM/console support, serial core, SysRq, TTY flip buffers, and `dz.h` register definitions. The driver is architecture/platform-specific and not DT-driven.

Risks: receive and transmit are multiplexed through shared registers; line selection must be decoded correctly. Some modem-status handling is incomplete and marked FIXME. BREAK detection is inferred from NUL plus framing error because hardware lacks a separate bit. Console output is a careful polling sequence that masks TX interrupts and may time out. Resource guards must remain balanced across partial failures.

Test signals: test all four lines, shared open/close IRQ behavior, request/release MMIO balance, console boot on supported non-IOASIC DECstations, termios baud fallback to supported rates, inferred break behavior, modem line behavior for line 2, and TX scanner interaction when several lines transmit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/dz.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/dz.h -->
# sources/distributed-fs/ceph-client/drivers/tty/serial/dz.h

Purpose: register and bit definition header for the DECstation DZ serial chipset driver. It names CSR, receive, transmit, modem, line-parameter, baud, line-number, and buffer constants used by `dz.c`.

Important APIs, types, and functions: this header has no functions. It defines status bits such as `DZ_TRDY`, `DZ_TIE`, `DZ_RDONE`, `DZ_RIE`, receive bits `DZ_DVAL`, `DZ_OERR`, `DZ_FERR`, `DZ_PERR`, software `DZ_BREAK`, modem bits, line IDs, baud encodings, character-size/parity/stop bits, register offsets, `DZ_NB_PORT`, `DZ_XMIT_SIZE`, and `DZ_WAKEUP_CHARS`. Helper macros `LINE(x)` and `UCHAR(x)` decode receive-buffer status.

Control flow: the C driver uses these constants to decode interrupt causes, select muxed receive/transmit lines, program line parameters, enable per-line TX/RX, infer errors, and size wakeup thresholds.

State and persistence: no state is stored in the header, but the bit definitions define the persistent hardware register contract for the DZ device.

Dependencies and integration points: included by `dz.c`; constants are tied to DEC DZ hardware layout and serial-core expectations for line count and wakeup threshold.

Risks: incorrect bit definitions break all I/O because DZ multiplexes several meanings onto shared offsets (`DZ_RBUF`/`DZ_LPR`, `DZ_MSR`/`DZ_TDR`). `DZ_BREAK` is a software flag placed alongside hardware error bits and must not collide with real hardware fields. Baud encodings are limited to classic DZ-supported rates up to 9600.

Test signals: validate `LINE()` extraction, register offset use for read vs write paths, baud encoding coverage, modem/printer line bit mapping, and wakeup threshold behavior in `dz.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/dz.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/earlycon-riscv-sbi.c -->
# sources/distributed-fs/ceph-client/drivers/tty/serial/earlycon-riscv-sbi.c

Purpose: RISC-V SBI-backed early console provider named `sbi`. It lets very early printk output use firmware SBI console services before a real UART driver is available.

Important APIs, types, and functions: `sbi_putc()` wraps legacy `sbi_console_putchar()`. `sbi_0_1_console_write()` uses `uart_console_write()` for SBI v0.1-style byte output. `sbi_dbcn_console_write()` writes chunks through the SBI debug console extension with `sbi_debug_console_write()`. `early_sbi_setup()` chooses the debug console extension if available, otherwise legacy v0.1 if configured. `EARLYCON_DECLARE(sbi, early_sbi_setup)` registers the provider.

Control flow: the generic earlycon framework matches `earlycon=sbi`, allocates an `earlycon_device`, and calls `early_sbi_setup()`. The setup function installs the chosen console write callback or returns `-ENODEV`. The debug-console path loops until all bytes are accepted or an SBI error occurs; the legacy path delegates CR/LF handling to `uart_console_write()`.

State and persistence: no private persistent state is stored. It uses global SBI availability/configuration state and the generic early console device.

Dependencies and integration points: depends on RISC-V SBI interfaces, generic console/earlycon serial-core support, and kernel config `CONFIG_RISCV_SBI_V01` for legacy fallback.

Risks: output availability is firmware-dependent. The debug-console write loop stops on negative return and does not retry or report detailed errors. Legacy SBI v0.1 support must be compiled in or setup fails when DBCN is absent.

Test signals: boot with `earlycon=sbi` on firmware with SBI DBCN, boot on legacy v0.1 firmware when enabled, verify failure when neither path is present, and check long writes where SBI accepts partial chunks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/earlycon-riscv-sbi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/earlycon-semihost.c -->
# sources/distributed-fs/ceph-client/drivers/tty/serial/earlycon-semihost.c

Purpose: semihosting-backed early console provider named `smh`. It routes early printk output through architecture semihosting calls.

Important APIs, types, and functions: `smh_write()` retrieves the `earlycon_device` from `console->data` and writes through `uart_console_write()` using `smh_putc`. `early_smh_setup()` installs `smh_write` as the console write callback. `EARLYCON_DECLARE(smh, early_smh_setup)` registers it.

Control flow: generic earlycon matching calls `early_smh_setup()`, which unconditionally assigns the write callback. Later early console writes are serialized by console core and emitted one character at a time via semihosting.

State and persistence: no driver-private state exists beyond the generic earlycon device pointer.

Dependencies and integration points: depends on `asm/semihost.h`, generic console support, and earlycon registration. It is intended for platforms where semihosting is available from the execution environment.

Risks: semihosting can be slow or unavailable depending on firmware/debugger setup. There is no runtime availability probe here. Since output is character based, large early logs can be expensive.

Test signals: boot with `earlycon=smh` under a semihosting-capable monitor, verify CR/LF handling through `uart_console_write()`, and confirm behavior when semihosting is absent in the target environment.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/earlycon-semihost.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/earlycon.c -->
# sources/distributed-fs/ceph-client/drivers/tty/serial/earlycon.c

Purpose: generic early console framework for serial-style boot consoles. It parses `earlycon=` and `console=` early parameters, maps MMIO/I/O resources, matches entries from the linker earlycon table, initializes `struct earlycon_device`, supports OF early console setup, and registers the boot console.

Important APIs, types, and functions: global `early_con` is the boot console, and `early_console_dev` holds its `uart_port`. `setup_earlycon()` is the main named-earlycon entry point. `register_earlycon()` parses options, initializes port defaults, maps MMIO, invokes the matched provider setup, prints info, and registers the console. `parse_options()` wraps `uart_parse_earlycon()`. `of_setup_earlycon()` initializes from flattened device tree properties. Early params are `param_setup_earlycon()` and `param_setup_earlycon_console_alias()`. `earlycon_acpi_spcr_enable` defers ACPI SPCR boot-console setup.

Control flow: boot parameters enter through early param callbacks. A specific string is matched against `__earlycon_table`, preferring entries with empty compatible before compatible-specific entries. Addressed forms are parsed into `uart_port` iotype/mapbase/iobase/options; MMIO gets mapped by `earlycon_map()`. The matched setup callback must install `con->write`; otherwise registration fails. For OF, the framework translates the node address, applies `reg-offset`, `reg-shift`, `reg-io-width`, endian flags, `current-speed`, and `clock-frequency`, then calls provider setup and registers the console.

State and persistence: state is global boot-time state: one `early_con`, one `early_console_dev`, parsed options, baud, uartclk, iotype, mapbase/membase, and the ACPI SPCR enable flag. The console is marked `CON_BOOT`; it is not long-term persistent after normal consoles take over.

Dependencies and integration points: depends on console core, serial core, early parameter parsing, fixmap or ioremap, OF flattened tree, optional ACPI SPCR, architecture serial `BASE_BAUD`, and earlycon provider declarations.

Risks: only one early console is registered; duplicates return `-EALREADY`. Mapping size is fixed in some paths. Malformed options can be passed to provider setup when parse fails by design. OF property interpretation must match UART register width and endianness or early output corrupts hardware access. Early boot context limits allocation and error recovery.

Test signals: test all accepted parameter forms, duplicate registration, empty `earlycon` with DT and ACPI SPCR, `console=uart...` alias behavior, MMIO/I/O and width/endian parsing, provider setup failure, and OF `stdout-path` options with clock/current-speed properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/earlycon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/fsl_linflexuart.c -->
# sources/distributed-fs/ceph-client/drivers/tty/serial/fsl_linflexuart.c

Purpose: Freescale/NXP LINFlexD UART serial driver for up to four `ttyLF` ports. It supports interrupt-driven UART mode, termios reconfiguration through LINFlex init mode, normal console, OF early console, suspend/resume, and a special early-console handoff buffer when the boot console and real console use the same instance.

Important APIs, types, and functions: global `linflex_ports[]` stores registered ports. `linflex_pops` supplies serial-core operations. Core routines include `linflex_setup_watermark()`, `linflex_startup()`, `linflex_shutdown()`, `linflex_set_termios()`, `linflex_int()`, `linflex_rxint()`, `linflex_txint()`, `linflex_transmit_buffer()`, and `linflex_put_char()`. Console/earlycon paths include `linflex_console_write()`, `linflex_console_setup()`, `linflex_earlycon_write()`, and `linflex_early_console_setup()`.

Control flow: init registers a UART driver and platform driver matched by `fsl,s32v234-linflexuart`. Probe allocates a `uart_port`, reads the DT serial alias, maps MMIO, gets IRQ, fills serial-core fields, stores it in `linflex_ports`, and calls `uart_add_one_port()`. Startup enters init mode via `linflex_setup_watermark()`, configures UART mode/RX/TX/interrupts, and requests IRQ. The IRQ handler reads `UARTSR` and dispatches RX when data-ready and TX when transmit-empty. RX drains bytes from `BDRM`, tracks break/frame/parity/overrun status, handles SysRq, inserts flip chars, and acknowledges status. TX writes through `BDRL` and waits for completion.

State and persistence: state is mostly hardware registers plus `uart_port`. Console builds add global earlycon handoff state: `earlycon_port`, `linflex_earlycon_same_instance`, `init_lock`, `during_init`, and dynamically grown `earlycon_buf`. This buffer temporarily captures earlycon output while the real console enters init mode, then replays it.

Dependencies and integration points: depends on DT compatible `fsl,s32v234-linflexuart`, platform IRQ/MMIO, serial core, TTY flip buffers, console and OF earlycon frameworks, and PM sleep helpers.

Risks: several hardware-state transitions busy-wait for init mode or TX completion without timeout. The earlycon same-instance path allocates with `GFP_ATOMIC` and caps by log-buffer size; allocation failure drops buffered characters. RX status masking appears less complete than termios masks suggest because inserted flags are not fully set for all error cases. Modem and break control are stubs.

Test signals: validate earlycon-to-console handoff on the same MMIO base, console setup without options, supported CS7/CS8/parity combinations, rejection/mutation of unsupported stop/CMSPAR modes, RX break/framing/parity/overrun, suspend/resume through `uart_suspend_port()`/`uart_resume_port()`, and IRQ-driven TX/RX.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/fsl_linflexuart.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/fsl_lpuart.c -->
# sources/distributed-fs/ceph-client/drivers/tty/serial/fsl_lpuart.c

Purpose: Freescale/NXP LPUART driver for multiple SoC variants and up to twelve `ttyLP` ports. It supports 8-bit and 32-bit register layouts, little- and big-endian 32-bit access, DMA TX/RX, interrupt RX/TX fallback, RS485 automatic RTS, console and early console, console polling, runtime PM, system sleep, and wakeup handling.

Important APIs, types, and functions: `struct lpuart_port` extends `uart_port` with SoC type, clocks, FIFO sizes, DMA channels/descriptors/cookies/scatterlists, cyclic RX ring, timer, wait queue, CS7 tracking, and DMA idle-interrupt mode. `struct lpuart_soc_data` selects devtype, iotype, register offset, and RX watermark. Serial operations are split between `lpuart_pops` for 8-bit registers and `lpuart32_pops` for 32-bit registers. Key functions include `lpuart_probe()`, `lpuart_startup()`, `lpuart32_startup()`, `lpuart_set_termios()`, `lpuart32_set_termios()`, DMA helpers, interrupt handlers, RS485 config, console/earlycon setup, `lpuart_global_reset()`, and PM callbacks.

Control flow: module init registers the shared UART driver and platform driver. Probe matches SoC data, maps MMIO plus optional offset, selects ops and IRQ handler, gets clocks, obtains DT alias, enables clocks, chooses console object, enables runtime PM, optionally performs global reset, reads RS485 mode, adds the port, and requests IRQ. Startup discovers FIFO sizes, requests DMA channels, configures watermarks, enables RX/TX, and starts DMA when possible. Interrupt mode drains FIFOs and fills TX FIFOs. DMA TX prepares scatterlists from the xmit FIFO and advances serial-core state on completion. DMA RX uses a cyclic ring, residue tracking, a timer or IDLE interrupt to detect completed packets, syncs DMA ownership, handles SysRq, and pushes data to TTY.

State and persistence: per-port state includes clocks, watermarks, FIFO sizes, DMA channels, ring-buffer head/tail, residue, timer, `dma_tx_in_progress`, `lpuart_dma_*_use`, and `is_cs7`. Hardware state includes CTRL/BAUD/FIFO/WATER/MODIR or 8-bit equivalents. Runtime PM stores active/suspended state in device PM core. No disk persistence exists.

Dependencies and integration points: depends on OF compatibles for VF610, LS1021A, LS1028A, i.MX7ULP, i.MX8ULP, i.MX8QXP, and i.MXRT1050; platform IRQ/MMIO; common clocks; DMAengine; scatterlist/circ buffer helpers; serial core; RS485 core; console/earlycon/poll console; pinctrl PM; and runtime/system PM.

Risks: one file handles many hardware variants, so iotype, register offset, endianness, FIFO-size encoding, and baud clock source must match SoC data. DMA RX has complex lifetime rules around timers, residue, sync ownership, termios restart, and suspend. Some waits poll hardware bits. Break handling differs between 8-bit and 32-bit variants, with 32-bit using TX inversion to avoid known hardware bugs. Probe mutates the shared `lpuart_reg.cons` based on port type, which can matter on mixed systems.

Test signals: cover each compatible family, 8-bit and 32-bit register paths, big-endian Layerscape access, IMX register offset earlycon, DMA and non-DMA TX/RX, RX DMA timer and IDLE interrupt modes, SysRq during DMA, RS485 polarity, CRTSCTS interaction, termios CS7/CS8/parity/CMSPAR/stop bits/baud, console and earlycon output, poll console, runtime autosuspend/resume, wakeup from suspend, no-console-suspend behavior, and probe/remove error unwinding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/fsl_lpuart.c -->
