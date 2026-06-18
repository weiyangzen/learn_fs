# subset-b-005457 Research

Grouped source research for Linux serial/TTY drivers under `sources/distributed-fs/ceph-client/drivers/tty/serial`. Each section is marker-delimited for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/jsm/jsm_tty.c -->
# sources/distributed-fs/ceph-client/drivers/tty/serial/jsm/jsm_tty.c

## Purpose

`jsm_tty.c` is the TTY/serial-core adapter for Digi JSM PCI multiport serial boards. It turns board/channel objects from the wider `jsm` driver into `struct uart_port` instances, translates Linux termios/modem-control operations into board-specific `bd_ops`, and moves received channel ring-buffer data into the TTY flip buffer.

## Important APIs, Types, and Functions

The public entry points used by the rest of the JSM driver are `jsm_tty_init()`, `jsm_uart_port_init()`, `jsm_remove_uart_port()`, `jsm_input()`, and `jsm_check_queue_flow_control()`. The `jsm_ops` `struct uart_ops` supplies serial-core methods including `startup`, `shutdown`, `set_termios`, `start_tx`, `stop_tx`, `stop_rx`, `send_xchar`, `break_ctl`, `get_mctrl`, and `set_mctrl`. Internal helpers include `jsm_get_mstat()` for TIOCM mapping, `jsm_tty_write()` for board TX draining, and `jsm_carrier()` for physical/virtual carrier state.

## Control Flow

Board initialization calls `jsm_tty_init()` to allocate and initialize per-channel `struct jsm_channel` objects, map UART register offsets, and set wait queues. `jsm_uart_port_init()` then assigns serial-core fields, allocates a line number from the static `linemap`, and calls `uart_add_one_port()`. Open/startup allocates channel read/error queues, flushes hardware queues through `bd_ops`, snapshots termios characters, initializes the UART, applies parameters, and evaluates carrier. TX is delegated to `bd_ops->copy_data_from_queue_to_uart()`, while RX enters through `jsm_input()`, which consumes channel ring buffers under `ch_lock`, annotates parity/frame/break errors, pushes flip data, and applies queue flow control.

## State and Persistence Behavior

Persistent runtime state is held in `struct jsm_channel`: read/error queues, ring indices, cached termios flags, start/stop chars, modem status, open count, cached LSR, and flow-control flags such as `CH_STOP`, `CH_STOPI`, `CH_RECEIVER_OFF`, `CH_CD`, and `CH_FCAR`. The static `linemap` persists line allocation across boards until `jsm_remove_uart_port()` clears bits. There is no file-backed persistence.

## Dependencies and Integration Points

The file depends on Linux TTY, tty flip buffers, serial core, PCI device ownership, and JSM-private `struct jsm_board`, `struct jsm_channel`, and `board_ops`. Hardware operations are abstracted through `bd_ops`, so this file integrates with board-specific UART implementations rather than directly programming every register.

## Risks and Edge Cases

Allocation failure in open can leave one queue allocated while the second fails. `jsm_input()` assumes `uart_port.state` exists when input is processed. Flow control is queue-depth based and can repeatedly send software stop characters up to `MAX_STOPS_SENT`. Carrier handling updates cached flags but leaves hangup policy mostly to surrounding serial/TTY behavior. `jsm_uart_port_init()` returns immediately on `uart_add_one_port()` failure without undoing earlier ports added in the same loop.

## Test Signals

Useful signals are multiport probe/remove with line reuse, open/close with HUPCL modem drop, termios changes for IXOFF/CRTSCTS, RX parity/frame/break annotation into the flip buffer, queue high/low-water flow-control transitions, and fault injection for queue allocation and `uart_add_one_port()` failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/jsm/jsm_tty.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/kgdboc.c -->
# sources/distributed-fs/ceph-client/drivers/tty/serial/kgdboc.c

## Purpose

`kgdboc.c` implements KGDB/KDB over an existing console-capable TTY polling driver. It multiplexes debugger I/O onto a configured serial console or keyboard path and supports built-in early console debugging when `CONFIG_KGDB_SERIAL_CONSOLE` allows it.

## Important APIs, Types, and Functions

The key KGDB object is `kgdboc_io_ops`, a `struct kgdb_io` with `read_char`, `write_char`, `pre_exception`, and `post_exception`. Configuration flows through `param_set_kgdboc_var()`, `configure_kgdboc()`, `cleanup_kgdboc()`, `kgdboc_probe()`, `init_kgdboc()`, and `exit_kgdboc()`. Keyboard support uses `kgdboc_register_kbd()`, `kgdboc_unregister_kbd()`, and an input-handler reset path guarded by `CONFIG_KDB_KEYBOARD`. Built-in early console support adds `kgdboc_earlycon_io_ops`, `kgdboc_earlycon_init()`, `kgdboc_earlycon_late_init()`, and deferred boot-console exit handling.

## Control Flow

Module init registers a platform driver and creates a single platform device so probe deferral can retry until the target TTY polling driver exists. `configure_kgdboc()` parses optional `kms,`, optional `kbd`/`kdb`, then asks `tty_find_polling_driver()` for the serial driver/line. It scans registered consoles under console locking to connect KGDB to the matching console, then registers the KGDB I/O module. Runtime debugger I/O calls the TTY driver's `poll_get_char` and `poll_put_char`. Exception entry can switch consoles into debug graphics mode and pins the module; exception exit restores graphics, releases the module, and queues keyboard reset work if needed.

## State and Persistence Behavior

State is global because KGDB has a single active I/O backend: `configured`, `config`, `kgdboc_use_kms`, `kgdb_tty_driver`, `kgdb_tty_line`, and `kgdboc_pdev`. `config_mutex` serializes setup/teardown and sysfs reconfiguration. Early console state stores the selected boot console and original `exit()` callback so cleanup can undo deferred exit.

## Dependencies and Integration Points

This file integrates with KGDB/KDB core, TTY polling operations, console registration, VT/KMS debug enter/leave, input core keyboard polling, irq_work, workqueues, module parameters, early params, and platform-device probe deferral. It requires the underlying console driver to implement polling hooks for normal kgdboc serial use.

## Risks and Edge Cases

Reconfiguration is blocked while KGDB is connected. Invalid sysfs configuration clears `config`, while invalid command-line configuration can remain so probe deferral keeps retrying. Early console support deliberately keeps a boot console usable after normal console takeover, which can be unsafe for some serial drivers and therefore warns once. Keyboard reset is carefully deferred from NMI-like context; failures there can leave keyboard state odd after KDB.

## Test Signals

Test with boot parameter and module-parameter configuration, missing TTY driver probe deferral, sysfs reconfiguration after driver load, KGDB attach/detach module refcount behavior, `kms,` graphics enter/leave, keyboard polling registration/removal, and earlycon registration/deinit across boot-console handoff.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/kgdboc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/lantiq.c -->
# sources/distributed-fs/ceph-client/drivers/tty/serial/lantiq.c

## Purpose

`lantiq.c` is a serial-core driver for the Lantiq ASC UART and Intel LGM ASC-compatible UARTs. It handles MMIO programming, FIFO/baud setup, interrupt variants, console and earlycon support, and device-tree platform probing.

## Important APIs, Types, and Functions

Important types are `struct ltq_uart_port`, which wraps `struct uart_port` with clocks, IRQ numbers, a private lock, and SoC hooks, and `struct ltq_soc_data`, which abstracts legacy three-IRQ Lantiq versus common-IRQ Intel wiring. The `lqasc_pops` `uart_ops` exposes startup/shutdown, termios, TX/RX control, request/release/config/verify, and modem stubs. Key functions include `lqasc_rx_chars()`, `lqasc_start_tx()`, `lqasc_startup()`, `lqasc_set_termios()`, `fetch_irq_lantiq()`, `request_irq_lantiq()`, `fetch_irq_intel()`, `request_irq_intel()`, and `lqasc_probe()`.

## Control Flow

Probe obtains MMIO resources, SoC match data, IRQ topology, alias line, clocks, and registers a `uart_port` in the static `lqasc_port` array. Startup enables the ASC clock gate, sets the run-mode clock divider, programs FIFO control, enables core UART mode and error reporting, requests SoC-specific IRQs, and enables RX/error/TX interrupts. RX IRQs clear interrupt status, drain the FIFO, read error bits, clear parity/frame/overrun state, and insert flip chars. TX IRQs acknowledge and call `uart_port_tx()` while FIFO space is available. Termios rewrites character size, parity, stop bits, masks, baud divisor, and receiver enable.

## State and Persistence Behavior

State persists in `lqasc_port[MAXPORTS]`, per-port clocks, IRQ ids, and hardware registers. The driver tracks read/ignore masks in `uart_port`, but modem control is mostly fixed as asserted. No suspend/resume state is implemented here; state is reconstructed by serial-core startup and termios paths.

## Dependencies and Integration Points

Dependencies include `clk`, device tree matching, Linux serial core, console/earlycon, Lantiq platform helpers for older non-common-clock builds, and raw MMIO. Device-tree compatibles are `lantiq,asc` and `intel,lgm-asc`.

## Risks and Edge Cases

The alias fallback for legacy Lantiq relies on physical address matching. `lqasc_remove()` removes the port but does not clear `lqasc_port[line]`, which matters if devices can re-probe. `lqasc_set_termios()` updates control bits with set-only masks in places, so stale bits must be considered when changing formats. Separate IRQ request cleanup is explicit and must remain matched to topology.

## Test Signals

Boot console and earlycon output, both `lantiq,asc` and `intel,lgm-asc` IRQ modes, RX errors and overrun clearing, termios changes for CS7/CS8/parity/stop bits, baud-rate accuracy, missing aliases, duplicate line allocation, clock-gate enable/disable, and module unload/reload behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/lantiq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/liteuart.c -->
# sources/distributed-fs/ceph-client/drivers/tty/serial/liteuart.c

## Purpose

`liteuart.c` is a serial-core driver for LiteX LiteUART controllers using 8-bit, 32-bit-aligned LiteX CSRs. It provides platform-device probing, optional IRQ operation, timer polling fallback, console support, and earlycon output.

## Important APIs, Types, and Functions

`struct liteuart_port` wraps `struct uart_port` with a polling `timer_list` and cached IRQ-enable register. `liteuart_driver` is the `uart_driver`, and `liteuart_ops` implements TX/RX, startup/shutdown, termios, config, and verify methods. Important helpers are `liteuart_update_irq_reg()`, `liteuart_rx_chars()`, `liteuart_tx_chars()`, `liteuart_interrupt()`, `liteuart_timer()`, `liteuart_probe()`, and console helpers `liteuart_console_write()` and `early_liteuart_setup()`.

## Control Flow

Probe maps the CSR region, optionally obtains an IRQ, allocates a line from DT alias or xarray, initializes the port, and calls `uart_add_one_port()`. Startup requests the IRQ when present; on request failure or no IRQ it sets `port->irq = 0` and starts a timer that repeatedly calls the same interrupt routine. RX drains until `OFF_RXEMPTY` is set, acknowledges RX pending to refresh the empty bit, and inserts normal chars because the hardware exposes no detailed error status. TX uses `uart_port_tx()` while `OFF_TXFULL` is clear. Shutdown disables event bits and frees either IRQ or timer.

## State and Persistence Behavior

Line ownership is stored in the static `liteuart_array` xarray. Per-port runtime state is the cached `irq_reg`, timer, and serial-core state. Hardware-visible state is event enable/pending and FIFO registers. There is no persistent configuration beyond the active port instance.

## Dependencies and Integration Points

The driver depends on LiteX CSR accessors (`litex_read8`/`litex_write8`), platform resources, OF aliases, xarray allocation, serial core, console core, and timer polling. Compatible string is `litex,liteuart`.

## Risks and Edge Cases

The CSR layout is explicitly limited to 8-bit CSR bus with 32-bit alignment. The timer path calls `liteuart_interrupt(0, port)`, passing a `uart_port *` where the IRQ handler expects a `struct liteuart_port *`; that path should be scrutinized because `to_liteuart_port()` is not applied there. Console write assumes a valid xarray entry. Error reporting is absent because hardware status lacks per-character error bits.

## Test Signals

Probe with DT aliases and auto allocation, IRQ and forced polling modes, TX/RX loopback, console and earlycon output, startup failure of IRQ request, timer shutdown, xarray cleanup on remove, and validation on nonstandard LiteX CSR layouts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/liteuart.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/lpc32xx_hs.c -->
# sources/distributed-fs/ceph-client/drivers/tty/serial/lpc32xx_hs.c

## Purpose

`lpc32xx_hs.c` drives the high-speed UART blocks on NXP LPC32xx SoCs. It provides a fixed-size platform UART set, MMIO FIFO/interrupt handling, baud-divider calculation from the main oscillator, console support, and basic PM suspend/resume through serial core.

## Important APIs, Types, and Functions

`struct lpc32xx_hsuart_port` wraps `struct uart_port`; static `lpc32xx_hs_ports[MAX_PORTS]` holds up to three ports. `serial_lpc32xx_pops` implements the serial-core operations. Key functions are `__serial_get_clock_div()`, `__serial_uart_flush()`, `__serial_lpc32xx_rx()`, `__serial_lpc32xx_tx()`, `serial_lpc32xx_interrupt()`, `serial_lpc32xx_startup()`, `serial_lpc32xx_shutdown()`, `serial_lpc32xx_set_termios()`, `serial_hs_lpc32xx_probe()`, and console wait/write/setup helpers.

## Control Flow

Probe selects the next static port slot, stores mapbase and IRQ, initializes `uart_port`, puts the hardware into loopback mode by default, and registers the port. Startup flushes the FIFO, clears latched TX/error/break/overrun interrupts, programs default timeout and trigger levels, disables loopback, requests IRQ, and enables RX/error interrupts. IRQ handling clears latched status, reports break/frame/overrun events, drains RX FIFO, and transmits pending bytes on TX interrupts. Termios forces 8N1, rejects modem-style flags, computes the closest rate divider, toggles RX/error interrupts for CREAD, writes the divider, and updates timeout.

## State and Persistence Behavior

State is mostly static per-port `uart_port` data plus the global `uarts_registered` count. Hardware loopback is used as a quiescent state outside active use. PM suspend/resume delegates to `uart_suspend_port()` and `uart_resume_port()`; detailed register restoration is not locally cached.

## Dependencies and Integration Points

Dependencies include serial core, platform resources, OF matching (`nxp,lpc3220-hsuart`), LPC32xx misc loopback helper `lpc32xx_loopback_set()`, console core, NMI watchdog touch in console write, and MMIO accessors.

## Risks and Edge Cases

Probe registration is order-based rather than alias-based, so device order matters. Termios masks off `CLOCAL` and `CRTSCTS`; applications expecting modem control or hardware flow will not get it. Only framing errors, break, and overrun are represented; parity is not supported. `uarts_registered` is not decremented on remove, limiting reprobe scenarios.

## Test Signals

Exercise all three ports, loopback transitions on startup/shutdown, forced termios normalization to 8N1, baud divider accuracy, RX timeout/trigger interrupts, break and overrun handling, console output during oops, PM suspend/resume, and remove/reprobe behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/lpc32xx_hs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/ma35d1_serial.c -->
# sources/distributed-fs/ceph-client/drivers/tty/serial/ma35d1_serial.c

## Purpose

`ma35d1_serial.c` is the Nuvoton MA35D1 UART driver. It supports up to 17 UARTs, MMIO FIFO operation, modem/auto-flow control, RS-485 function selection constants, console support, platform PM callbacks, and OF-based probing.

## Important APIs, Types, and Functions

`struct uart_ma35d1_port` wraps `struct uart_port` with a clock, local `ier/lcr/mcr` fields, and console register caches. `ma35d1serial_ops` exposes serial-core operations. Key routines include `serial_in()`, `serial_out()`, `transmit_chars()`, `receive_chars()`, `ma35d1serial_interrupt()`, `ma35d1serial_set_mctrl()`, `ma35d1serial_set_termios()`, `ma35d1serial_startup()`, `ma35d1serial_probe()`, `ma35d1serial_suspend()`, and `ma35d1serial_resume()`.

## Control Flow

Probe requires a DT node and serial alias, selects a static port slot, maps MMIO, obtains/enables the UART clock, obtains the IRQ, initializes the port, and registers with serial core. Startup resets FIFOs, clears pending interrupts, requests the IRQ, configures FIFO thresholds, default 8-bit LCR, RX timeout, and RX/buffer/time-out interrupts. The interrupt handler checks receive, timeout, TX-empty, and buffer-error conditions, calls `receive_chars()` or `transmit_chars()`, and clears TX overflow. Termios builds LCR from character format, computes baud as `uartclk / (quot + 2)`, updates read/ignore masks, toggles auto RTS/CTS via `ma35d1serial_set_mctrl()`, and writes baud/LCR.

## State and Persistence Behavior

Static `ma35d1serial_ports[MA35_UART_NR]` persists per-line objects. Runtime state is split between serial-core fields, cached `mcr`, and hardware registers. Suspend caches BAUD/LCR/IER only for console line 0 before `uart_suspend_port()` and restores them before `uart_resume_port()` on resume.

## Dependencies and Integration Points

The file depends on OF aliases, platform resources, clocks, MMIO, serial core, tty flip buffers, console core, and `read_poll_timeout_atomic()` for console TX waits. Compatible string is `nuvoton,ma35d1-uart`.

## Risks and Edge Cases

Console setup independently `ioremap()`s from DT `reg`, which must remain coherent with normal probe mapping. Probe error cleanup calls `free_irq()` after `uart_add_one_port()` failure even though request_irq occurs later in startup. `remove()` disables the clock but does not unmap normal probe MMIO. Flow-control polarity is hardcoded through active-level bits and needs hardware validation.

## Test Signals

Probe all alias lines, console line 0 boot/resume, baud bounds at divider min/max, CRTSCTS auto-flow enable/disable, break/parity/frame/overrun RX paths, TX overflow clearing, IRQ request failure, clock failures, suspend/resume with active console, and module unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/ma35d1_serial.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/max3100.c -->
# sources/distributed-fs/ceph-client/drivers/tty/serial/max3100.c

## Purpose

`max3100.c` is a SPI UART driver for the Maxim MAX3100. Because register access requires sleeping SPI transfers and the chip has limited IRQ support, the driver uses a per-port freezable workqueue plus a polling timer for TX/RX, modem status, and flow-control updates.

## Important APIs, Types, and Functions

`struct max3100_port` wraps `uart_port` with SPI state, cached config/RTS/loopback commits, parity mode, RX enable, workqueue/work item, timer, suspend flags, and minor number. `max3100_ops` implements serial-core callbacks. Key functions are `max3100_sr()` for 16-bit SPI exchange, parity helpers, `max3100_handlerx_unlocked()`, `max3100_work()`, `max3100_dowork()`, `max3100_set_termios()`, `max3100_startup()`, `max3100_shutdown()`, `max3100_probe()`, and PM suspend/resume.

## Control Flow

Probe lazily registers the UART driver, allocates a free static slot, initializes the SPI-backed port, reads `clock-frequency`, calls `uart_add_one_port()`, and writes shutdown mode. Startup initializes config, creates the workqueue, requests the falling-edge IRQ, schedules config commit, waits for clock settle, and starts modem polling. The worker commits pending config/loopback/RTS changes, reads RX/status, handles CTS changes, sends x_char or FIFO data when TX-empty, pushes flip buffers periodically, and loops while RX or TX work remains. Timer and IRQ both schedule the worker.

## State and Persistence Behavior

State is held in static `max3100s[MAX_MAX3100]` under `max3100s_lock` and in each port's cached config fields. `conf_commit`, `rts_commit`, and `loopback_commit` are software persistence points for later SPI writes. Suspend disables IRQ, marks `suspending`, suspends the UART port, and writes chip shutdown; resume restarts serial core and schedules config commit if open.

## Dependencies and Integration Points

The driver integrates with SPI core, serial core, tty flip buffers, timer polling, workqueues/freezer, PM sleep ops, device properties for `clock-frequency`, and OF/SPI ID matching for `maxim,max3100`.

## Risks and Edge Cases

TX-empty and modem state can be stale because reads are scheduled asynchronously. Shutdown destroys the workqueue and then performs SPI I/O; suspend avoids normal shutdown with `suspending`. IRQ request failure disables IRQ operation entirely and returns busy. Parity is partly emulated in software, so 7-bit/parity combinations need careful testing. Probe returns success even if `uart_add_one_port()` fails after logging the error.

## Test Signals

SPI transfer fault injection, missing clock-frequency, open/close power transitions, IRQ and timer scheduling, CTS polling changes, parity modes, loopback via TIOCM_LOOP, suspend/resume during active TX/RX, workqueue freezer behavior, and repeated probe/remove with last-device UART unregister.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/max3100.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/max310x.c -->
# sources/distributed-fs/ceph-client/drivers/tty/serial/max310x.c

## Purpose

`max310x.c` is a regmap-based SPI/I2C UART driver for MAX3107, MAX3108, MAX3109, and MAX14830 chips. It supports one to four UART ports per chip, FIFO batch I/O, threaded IRQ dispatch, clock/PLL setup, RS-485 mode, optional GPIO controller registration, and PM suspend/resume.

## Important APIs, Types, and Functions

Important types are `struct max310x_devtype`, `struct max310x_if_cfg`, `struct max310x_one`, and `struct max310x_port`. `max310x_ops` provides serial-core callbacks; `max310x_uart` is the shared `uart_driver`. Core functions include `max310x_detect()`, `max310x_set_ref_clk()`, `max310x_set_baud()`, `max310x_handle_rx()`, `max310x_handle_tx()`, `max310x_port_irq()`, `max310x_ist()`, `max310x_set_termios()`, `max310x_rs485_config()`, `max310x_probe()`, bus-specific SPI/I2C probe functions, and GPIO callbacks under `CONFIG_GPIOLIB`.

## Control Flow

Module init registers the UART driver, then SPI and/or I2C bus drivers. Bus probe creates per-port regmaps and calls common `max310x_probe()`. Common probe validates clocks, detects the chip by revision/default register, resets each port, waits for startup, programs mode registers, configures reference clock/PLL, allocates global line numbers, initializes serial-core ports and work items, registers each UART, powers ports down, optionally registers GPIOs, and requests a threaded IRQ. IRQ service dispatches global per-port IRQ state, handles CTS changes, drains RX FIFO, and schedules TX work on TX-empty. Termios writes LCR, status masks, hardware/software flow control, XON/XOFF chars, baud generator, and timeout.

## State and Persistence Behavior

Global line allocation uses `max310x_lines`. Per-chip state includes devtype, interface config, root regmap, clock, optional gpio chip, and flexible-array per-port state. Per-port state includes regmap, RX buffer, TX/modem/RS485 work items, serial-core state, and RS-485 configuration. Suspend iterates ports through `uart_suspend_port()` and powers them off; resume powers them on and calls `uart_resume_port()`.

## Dependencies and Integration Points

The file integrates with serial core, regmap, SPI, I2C, common clock framework, GPIO library, device properties, OF and bus ID tables, threaded IRQs, workqueues, and Linux RS-485 serial APIs. It uses noinc regmap operations for FIFO batch transfers.

## Risks and Edge Cases

The `max310x_uart_init()` error label for I2C failure unconditionally references the SPI unregister path, so build configurations with I2C but without SPI need scrutiny. Probe must unwind partially registered multiport chips correctly; line bits are set only after successful add. Regmap cache volatility/precious settings are critical for FIFO/status correctness. Clock detection chooses `xtal` based on absence of `clock-names = "osc"`, which is subtle. Batch RX optimization ignores detailed errors unless masks request them.

## Test Signals

SPI and I2C probe for all devtypes, multiport global IRQ dispatch, revision mismatch, PLL/clock stability failures, FIFO batch RX/TX at boundaries, hardware and software flow control, RS-485 delay validation, GPIO direction/get/set/config, suspend/resume across active ports, and module init error paths for SPI-only/I2C-only builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/max310x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/mcf.c -->
# sources/distributed-fs/ceph-client/drivers/tty/serial/mcf.c

## Purpose

`mcf.c` is the Freescale ColdFire internal UART serial driver. It registers platform-provided UARTs with serial core, handles classic ColdFire UART registers, supports console output, and exposes basic RS-485 automatic RTS behavior.

## Important APIs, Types, and Functions

`struct mcf_uart` wraps `uart_port` with a local modem-signal cache and interrupt-mask mirror. `mcf_uart_ops` provides serial-core callbacks. Key functions include `mcf_startup()`, `mcf_shutdown()`, `mcf_set_termios()`, `mcf_rx_chars()`, `mcf_tx_chars()`, `mcf_interrupt()`, `mcf_config_port()`, `mcf_config_rs485()`, `mcf_probe()`, and console helpers.

## Control Flow

Platform probe iterates platform data entries, initializes static `mcf_ports`, assigns MMIO/IRQ/clock/ops/RS485 hooks, and adds each port. `mcf_config_port()` sets type/FIFO size, masks interrupts, and requests the IRQ. Startup resets RX/TX, enables both directions, and enables RX-ready interrupts. TX start enables transmitter/RTS for RS-485 and sets TX-ready interrupt. IRQ handling reads masked status and dispatches RX/TX under the port lock. RX drains ready bytes, resets error status, updates counters, handles break/sysrq, and pushes flip data. TX uses `uart_port_tx()` and disables TX after completion in RS-485 mode to negate RTS automatically.

## State and Persistence Behavior

Static `mcf_ports[10]` persists all port objects. `pp->imr` mirrors the hardware interrupt mask and `pp->sigs` mirrors modem outputs. Board-specific DTR/DCD macros can persist external GPIO state. There is no runtime PM or register cache beyond serial-core termios reprogramming.

## Dependencies and Integration Points

The driver depends on ColdFire architecture headers (`asm/coldfire.h`, `asm/mcfsim.h`, `asm/mcfuart.h`, `asm/nettel.h`), platform data `struct mcf_platform_uart`, serial core, console core, and optional board GPIO macros for DTR/DCD.

## Risks and Edge Cases

A FIXME notes `read_status_mask` and `ignore_status_mask` are not initialized from termios, so RX error filtering may be incomplete. IRQs are requested in `config_port()` and never freed in `release_port()`, which is normal for fixed internal UARTs but limits reprobe assumptions. `mcf_remove()` tests `if (port)` on addresses of static array elements, so it attempts removal for all slots. Console output busy-waits with fixed loop counts.

## Test Signals

Platform data with multiple UARTs, RX parity/frame/break/overrun counters, RS-485 RTS behavior, termios character/parity/baud modes including M5272 fractional divider, console output, DTR/DCD board macro behavior, and repeated platform remove/probe if supported.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/mcf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/men_z135_uart.c -->
# sources/distributed-fs/ceph-client/drivers/tty/serial/men_z135_uart.c

## Purpose

`men_z135_uart.c` drives MEN 16z135 high-speed UART MCB cores. It registers MCB devices as serial-core UARTs with large memory-mapped FIFOs, configurable TX/RX trigger levels, modem-status handling, and module parameters for FIFO alignment and RX timeout.

## Important APIs, Types, and Functions

`struct men_z135_port` wraps `uart_port` with MCB device/resource pointers, an RX bounce page, cached status register, lock, and automode flag. `men_z135_ops` supplies serial-core methods. Important functions are `men_z135_handle_rx()`, `men_z135_handle_tx()`, `men_z135_intr()`, `men_z135_request_irq()`, `men_z135_set_mctrl()`, `men_z135_get_mctrl()`, `men_z135_startup()`, `men_z135_set_termios()`, `men_z135_request_port()`, `men_z135_probe()`, and `men_z135_remove()`.

## Control Flow

Module init registers the UART driver and MCB driver. MCB probe allocates the port and a page-sized RX buffer, fills UART metadata, and calls `uart_add_one_port()`. Serial-core config/request maps the MCB memory resource. Startup requests a shared IRQ, enables all IRQs except TX-space-available, programs trigger levels from module params, and optionally sets RX timeout. The interrupt handler reads a destructive status/IIR register, acknowledges IRQ bits, then handles receiver line status, RX data/timeout, TX-space available, and modem status under the port lock.

## State and Persistence Behavior

Global `line` assigns monotonically increasing port lines and is decremented on remove. Per-port state includes MCB memory ownership, `rxbuf`, cached `stat_reg`, and `automode` for CRTSCTS behavior. Hardware register state includes CONF, BAUD, TIMEOUT, FIFO control pointers, and modem/LCR fields.

## Dependencies and Integration Points

The driver integrates with the MEN Chameleon Bus (`mcb_register_driver`, `mcb_request_mem`, `mcb_get_irq`), serial core, TTY flip buffers, module parameters, MMIO bulk copy helpers, and modem-control callbacks.

## Risks and Edge Cases

`men_z135_set_termios()` ORs new LCR bits into the previous value without clearing word/parity/stop fields first, so changing formats can leave stale bits. RX is capped at `MEN_Z135_FIFO_WATERMARK` to avoid crossing into TX FIFO space. `verify_port()` always rejects user serial_struct changes. The global `line` counter can reuse line numbers incorrectly if removes are not strictly LIFO.

## Test Signals

MCB probe/remove with multiple cores, RX FIFO watermark and flip-buffer truncation, TX FIFO alignment mode, configurable trigger levels and timeout, modem DCD/CTS change notifications, CRTSCTS automode, termios format changes, destructive IRQ status handling with multiple bits set, and IRQ request failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/men_z135_uart.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/meson_uart.c -->
# sources/distributed-fs/ceph-client/drivers/tty/serial/meson_uart.c

## Purpose

`meson_uart.c` is the Amlogic Meson UART driver. It supports multiple compatibles, two possible TTY driver names (`ttyAML` and `ttyS`), console/earlycon and polling-console support, clock-based baud programming, optional hardware flow control, and dynamic registration/unregistration of the relevant UART driver.

## Important APIs, Types, and Functions

`struct meson_uart_data` selects the UART driver and XTAL divider behavior. Static `meson_ports[AML_UART_PORT_NUM]` tracks active ports. `meson_uart_ops` provides serial-core callbacks plus optional `poll_get_char`/`poll_put_char`. Key routines are `meson_uart_start_tx()`, `meson_receive_chars()`, `meson_uart_interrupt()`, `meson_uart_reset()`, `meson_uart_startup()`, `meson_uart_change_speed()`, `meson_uart_set_termios()`, `meson_uart_probe_clocks()`, `meson_uart_probe()`, and console/earlycon helpers.

## Control Flow

Probe derives the line from DT alias or an offset auto-allocation range, obtains resources/IRQ/fifo size/flow-control property, enables pclk/xtal/baud clocks, registers the selected UART driver if needed, initializes the port, briefly maps/resets/releases hardware before `uart_add_one_port()`, and stores it in `meson_ports`. Startup clears errors, enables RX/TX and both IRQs, configures FIFO IRQ trigger levels, and requests IRQ. IRQ handling drains RX when non-empty and starts TX when TX FIFO is not full and TX interrupts are enabled. Termios updates format, parity, stop bits, two-wire/RTSCTS mode, baud, and status masks.

## State and Persistence Behavior

State persists in `meson_ports`, serial-core port objects, clock-enabled resources managed by devm, and hardware control/status registers. Removal unregisters the selected UART driver only when no ports remain. No explicit suspend/resume state appears in this file.

## Dependencies and Integration Points

Dependencies include platform/OF, common clock framework, serial core, console and earlycon, console polling for KGDB-style use, MMIO, and compatible-specific data for G12A/A1/S4. Earlycon supports `amlogic,meson-ao-uart` and `amlogic,meson-s4-uart`.

## Risks and Edge Cases

The RX error path increments `icount.frame` for parity errors, which should be checked against intended accounting. Dynamic UART driver unregister only considers the current driver pointer; mixed `ttyAML` and `ttyS` devices need careful remove ordering. Probe reset maps and releases before normal serial-core request, so mapping lifecycle must remain matched. Hardware flow is disabled in termios if the DT property did not set `UPF_HARD_FLOW`.

## Test Signals

Compatibles selecting `ttyAML` versus `ttyS`, alias and auto line assignment, console/earlycon/polling I/O, XTAL div2 baud programming, RTSCTS property behavior, RX break/parity/frame/overrun handling, TX interrupt enable/disable, mixed port removal, and clock failure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/meson_uart.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/milbeaut_usio.c -->
# sources/distributed-fs/ceph-client/drivers/tty/serial/milbeaut_usio.c

## Purpose

`milbeaut_usio.c` is the Socionext Milbeaut USIO UART driver. It manages a compile-time fixed array of platform UART ports, split RX/TX IRQs, FIFO setup, optional auto-flow-control property support, console and earlycon output, and clock-based baud generation.

## Important APIs, Types, and Functions

The driver uses static `mlb_usio_ports[]` and `mlb_usio_irq[][RX/TX]` arrays rather than a private wrapper type. `mlb_usio_ops` implements serial-core methods. Key functions include `mlb_usio_tx_chars()`, `mlb_usio_start_tx()`, `mlb_usio_rx_chars()`, `mlb_usio_rx_irq()`, `mlb_usio_tx_irq()`, `mlb_usio_startup()`, `mlb_usio_set_termios()`, `mlb_usio_probe()`, console helpers, and `mlb_usio_init()/exit()`.

## Control Flow

Module init registers the UART driver and platform driver. Probe enables the device clock, reads the `index` property to select the static port, maps registers, records named RX/TX IRQs, initializes serial-core fields, and adds the port. Startup requests separate RX and TX IRQs, applies optional auto-flow-control to ESCR, resets SCR/SSR/FCR/FBYTE, enables FIFOs, and enables TX/RX plus RX/TX buffer interrupts. RX IRQ drains up to a small count or FIFO-reported amount, handles parity/overrun/frame/break flags, resets error state, and pushes flip data. TX fills FIFO space from x_char or xmit FIFO and controls FCR/SCR TX interrupt bits.

## State and Persistence Behavior

State persists in static arrays keyed by DT `index`; the clock pointer is stored in `port->private_data`. Runtime status is mostly hardware register state and serial-core masks/counters. Removal uses `pdev->id` to select the port, while probe uses the `index` property, so platform IDs and DT indices must align.

## Dependencies and Integration Points

Dependencies include platform/OF, named IRQs, common clock framework, serial core, console/earlycon, and MMIO accessors. Compatible string is `socionext,milbeaut-usio-uart`; optional property `auto-flow-control` affects startup, termios, and console setup.

## Risks and Edge Cases

Probe does not validate negative results from `platform_get_irq_byname()` before storing them. Remove indexes by `pdev->id`, which may not equal the DT `index`. `mlb_usio_rx_chars()` only increments frame/parity/overrun counters for some statuses and uses nested conditionals that can leave `flag` from a previous iteration if not reset carefully. Startup/shutdown do not disable the clock until remove.

## Test Signals

DT index bounds and remove alignment, missing named IRQs, auto-flow-control property and CRTSCTS termios, RX parity/frame/overrun/break paths, TX FIFO refill and wakeup thresholds, console/earlycon output, clock enable failure, and multiple configured ports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/milbeaut_usio.c -->
