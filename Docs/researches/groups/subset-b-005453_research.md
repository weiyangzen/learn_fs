# subset-b-005453 Research

Grouped research for the exact subset B work item. Each section preserves the original source path and is wrapped for deterministic reconciliation into per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_port.c -->
# sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_port.c

## Purpose
Implements the common 8250/16450/16550 UART port operations used by the serial core and by most 8250-family bus glue drivers. It supplies the default `uart_ops`, UART type/capability table, register access dispatch, autoconfiguration probes, RX/TX interrupt handling, runtime PM helpers, DMA hooks, RS485 software emulation, termios programming, resource claiming, sysfs RX trigger tuning, console write support, and console setup/exit helpers.

## Important APIs, Types, And Functions
`uart_config[]` maps `PORT_*` identifiers to names, FIFO sizes, TX load sizes, default FCR values, RX trigger byte tables, and capability flags such as FIFO, EFR, AFE, sleep, UUE, RTOIE, RPM, MINI, and HFIFO. Register access defaults are selected by `set_io_from_upio()` and include I/O port, HUB6, byte/16/32-bit MMIO, big-endian MMIO, and no-op fallbacks. Exported helpers include `serial8250_clear_fifos()`, `serial8250_clear_and_reinit_fifos()`, `serial8250_rpm_get()`, `serial8250_rpm_put()`, `serial8250_em485_destroy()`, `serial8250_em485_config()`, `serial8250_em485_start_tx()`, `serial8250_em485_stop_tx()`, `serial8250_read_char()`, `serial8250_rx_chars()`, `serial8250_tx_chars()`, `serial8250_modem_status()`, `serial8250_handle_irq_locked()`, `serial8250_handle_irq()`, `serial8250_do_get_mctrl()`, `serial8250_do_set_mctrl()`, `serial8250_do_startup()`, `serial8250_do_shutdown()`, `serial8250_do_set_divisor()`, `serial8250_update_uartclk()`, `serial8250_do_set_termios()`, `serial8250_do_set_ldisc()`, `serial8250_do_pm()`, `serial8250_init_port()`, `serial8250_set_defaults()`, `serial8250_fifo_wait_for_lsr_thre()`, `serial8250_console_write()`, `serial8250_console_setup()`, and `serial8250_console_exit()`.

## Control Flow
Port registration callers initialize a `struct uart_8250_port`, then `serial8250_init_port()` installs `serial8250_pops`; `serial8250_set_defaults()` fills type-derived FIFO/capability defaults and I/O callbacks. `serial8250_config_port()` claims the region, optionally probes UART type with `autoconfig()`, optionally probes IRQ with `autoconfig_irq()`, applies Tegra/NOMSR quirks, registers the RX-trigger sysfs attribute when supported, and seeds `up->fcr`. Startup runs `serial8250_do_startup()`: ensure defaults, switch I/O accessors if needed, runtime-PM get, device-specific wake/reset (`serial8250_startup_special()`), clear FIFOs/interrupt state, validate LSR, program TX thresholds, request IRQ, test THRE/TXEN behavior, initialize modem control, request DMA unless the port is a console, and seed `up->ier` for RX interrupts. Interrupt handling starts in `serial8250_default_handle_irq()`, reads IIR, locks the port, drains RX with DMA flush or `serial8250_rx_chars()`, processes modem status, and feeds TX with DMA or `serial8250_tx_chars()` when THRE is active. Shutdown disables IER under lock, synchronizes IRQ, releases DMA, drops OUT2/break, clears FIFOs, disables RSA mode, drains RX, synchronizes again for late IRQs, runtime-PM puts, and releases the IRQ.

## State And Persistence
All state is volatile kernel driver state: `struct uart_8250_port` shadows `ier`, `lcr`, `mcr`, `fcr`, capability and bug flags, saved LSR/MSR bits, DMA pointers, GPIO modem-control state, RS485 emulation timers, and runtime-PM TX activity. Port resources are reserved with `request_region()` or `request_mem_region()` and optionally `ioremap()` while the port is configured/open. The only externally visible persistent-like runtime surface is the tty device state, console binding, and the per-port `rx_trig_bytes` sysfs attribute while registered; no file-backed persistence exists.

## Dependencies And Integration Points
The file sits between `serial_core` and all 8250 bus/platform drivers. It depends on `linux/serial_core.h`, `linux/serial_8250.h`, tty flip buffers, termios, IRQ probing, runtime PM, GPIO modem-control helpers, optional DMA routines from the 8250 DMA layer, optional console poll, Fintek/RSA helpers, and architecture I/O accessors. Platform drivers such as PXA, Tegra, UniPhier, RT288x, PCI, OF, PCMCIA, and board drivers register ports whose specialized callbacks override only the pieces not covered here.

## Risks And Test Signals
High-risk areas are hardware probing side effects, FIFO sizing, EFR/16750/NatSemi/XScale/RSA detection, shared IRQ behavior, DMA fallback, runtime-PM balancing, console lockless/panic paths, RS485 timer races, and termios divisor programming across variant-specific register maps. Useful test signals include successful boot console and runtime tty operation, loopback RX/TX at multiple baud rates, modem-control transitions, CTS/RTS flow control, sysfs `rx_trig_bytes` get/set, suspend/resume, DMA and non-DMA paths, RS485 delays and RTS polarity, KGDB console polling, and regression coverage for known variants such as Tegra, XScale/PXA, RSA, Altera 16550, BCM mini UART, and 16C950.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_port.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_pxa.c -->
# sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_pxa.c

## Purpose
Provides 8250-platform glue for Marvell/Intel PXA and MMP on-chip UARTs, replacing the older non-8250 PXA serial driver for systems that can use the generic 8250 core.

## Important APIs, Types, And Functions
`struct pxa8250_data` stores the registered 8250 line and device clock. `serial_pxa_probe()` allocates state, gets/prepares the clock, fills a `struct uart_8250_port`, reads firmware port properties, configures XScale-style FIFO parameters, and calls `serial8250_register_8250_port()`. `serial_pxa_remove()` unregisters and unprepares the clock. `serial_pxa_pm()` gates the clock from the 8250 PM callback, while `serial_pxa_suspend()` and `serial_pxa_resume()` delegate to `serial8250_suspend_port()` and `serial8250_resume_port()`. `serial_pxa_dl_write()` writes DLL/DLM and verifies DLL as a workaround for PXA270M erratum #74.

## Control Flow
The platform driver matches `mrvl,pxa-uart`, `mrvl,mmp-uart`, or `platform:pxa2xx-uart`. Probe requires one memory resource and one clock, prepares the clock, sets `PORT_XSCALE`, `UPIO_MEM32`, `regshift = 2`, `fifosize = 64`, `tx_loadsz = 32`, `UPF_IOREMAP | UPF_SKIP_TEST | UPF_FIXED_TYPE`, and then registers with the 8250 core. Runtime port power transitions flow through `uart_port.pm`, which enables the clock for state 0 and disables it otherwise. System sleep suspends/resumes the 8250 line.

## State And Persistence
State is only `pxa8250_data` plus the 8250 core's registered line state. The clock is prepared for the driver's lifetime and enabled/disabled by port PM. No persistent configuration is stored beyond firmware properties and module binding.

## Dependencies And Integration Points
Depends on platform resources, common clock framework, OF match tables, `uart_read_port_properties()`, and the 8250 registration/suspend/resume APIs. Integrates with the 8250 core through `PORT_XSCALE`, custom divisor-latch write, PM callback, and private data.

## Risks And Test Signals
The probe path returns immediately on `uart_read_port_properties()` failure without unpreparing the already prepared clock, so error unwinding deserves attention. Other risks are incorrect clock rate, erratum workaround warnings, and power-state clock imbalance. Test signals include DT/legacy probe, baud-rate programming after DLL verification, suspend/resume console and non-console ports, and module remove after active use.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_pxa.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_rsa.c -->
# sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_rsa.c

## Purpose
Adds support for IODATA RSA-DV II/S ISA-style high-speed RSA UART extensions without creating a direct module dependency loop between the 8250 base and 8250 core modules.

## Important APIs, Types, And Functions
`probe_rsa[]` and `probe_rsa_count` expose the `probe_rsa` module parameter for I/O bases to probe. `rsa8250_request_resource()` and `rsa8250_release_resource()` reserve the RSA extension register window at `UART_RSA_BASE`. `univ8250_rsa_support()` patches a supplied `uart_ops` table so config/request/release wrappers can reserve RSA resources around core operations. `rsa_enable()`, `rsa_disable()`, `rsa_autoconfig()`, and `rsa_reset()` are called by 8250 core paths to enter high-speed FIFO mode, return to compatibility mode, identify RSA ports, and reset FIFO state.

## Control Flow
During 8250 setup, `univ8250_rsa_support()` installs wrapper callbacks. `univ8250_config_port()` marks a port for RSA probing if its type is already `PORT_RSA` or its I/O base matches the module parameter, calls the original config method, and releases the probe-only region if the hardware does not become `PORT_RSA`. `rsa_autoconfig()` only acts on a `PORT_16550A` with `UART_PROBE_RSA`; if `__rsa_enable()` observes the FIFO bit, it promotes the port to `PORT_RSA`. Startup calls `rsa_enable()`, shutdown calls `rsa_disable()`, and reset paths write `UART_RSA_FRR`.

## State And Persistence
Persistent kernel state is limited to the module parameter array and the saved `core_port_base_ops` pointer. Per-port RSA state lives in `up->probe`, `port->type`, `port->uartclk`, and the reserved I/O region. Hardware FIFO mode is volatile and explicitly toggled.

## Dependencies And Integration Points
Depends on `CONFIG_SERIAL_8250_RSA`, I/O port resources, `serial_in()`/`serial_out()`, and 8250 internals declared in `8250.h`. The symbol export is intentionally restricted for the 8250 module to break a dependency cycle.

## Risks And Test Signals
Risks include stale or incorrect `probe_rsa` addresses, resource conflicts with normal serial ranges, unsupported non-I/O-port mappings returning `-EINVAL`, and clock changes when enabling/disabling RSA mode. Test signals are module parameter probing, `PORT_RSA` type detection, UART clock changing between `SERIAL_RSA_BAUD_BASE` and low compatibility base, clean release of RSA resources, and high-speed transfer with FIFO reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_rsa.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_rt288x.c -->
# sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_rt288x.c

## Purpose
Supplies custom 8250 register access for Ralink RT288x/RT305x, Alchemy Au1xxx, and similar UARTs with a non-standard register layout and a separate divisor latch register.

## Important APIs, Types, And Functions
`au_io_in_map[]` and `au_io_out_map[]` translate standard UART offsets to the hardware's sparse layout. `au_serial_in()` and `au_serial_out()` perform raw 32-bit MMIO accesses through those maps. `au_serial_dl_read()` and `au_serial_dl_write()` access the divisor latch at `RT288X_DL`. `au_platform_setup()` configures `struct plat_serial8250_port` for board-style registration; `rt288x_setup()` configures an already allocated `struct uart_port`/`uart_8250_port`. Early console support uses `early_au_setup()`.

## Control Flow
Callers invoke `au_platform_setup()` or `rt288x_setup()` before registering the port. Those functions set `UPIO_AU`, custom serial accessors, custom divisor accessors, mapsize, and `UART_BUG_NOMSR`. If 8250 console support is enabled, the earlycon declaration for `ralink,rt2880-uart` applies the setup to the early console port and installs `au_early_serial8250_write()`, which writes characters through `au_putc()` and waits for TX empty.

## State And Persistence
No private driver state is allocated. The setup functions mutate the caller-owned port structure. Hardware state is volatile MMIO register state and divisor latch contents managed by the 8250 core.

## Dependencies And Integration Points
Depends on `serial_8250`, earlycon support, and the 8250 core's `UPIO_AU` path. It is selected by `SERIAL_8250_RT288X` and exported for board/platform code that needs the alternate layout.

## Risks And Test Signals
Risks are wrong offset maps, out-of-range offsets silently returning `UINT_MAX` or ignoring writes, raw MMIO ordering assumptions, and the NOMSR quirk hiding modem status. Test signals include early console output on `ralink,rt2880-uart`, normal ttyS operation, divisor programming at multiple baud rates, no modem-status dependent stalls, and successful registration with both platform setup entry points.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_rt288x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_tegra.c -->
# sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_tegra.c

## Purpose
Implements 8250 glue for NVIDIA Tegra UARTs, including Tegra-specific break handling, clock/reset management, DT/ACPI matching, and console-aware suspend/resume.

## Important APIs, Types, And Functions
`struct tegra_uart` stores the clock, optional shared reset control, and 8250 line number. `tegra_uart_handle_break()` drains RX while FIFO/error/break bits remain set to clear Tegra break/error conditions. `tegra_uart_probe()` builds a `PORT_TEGRA` `uart_8250_port`, maps memory, reads firmware port properties, gets optional reset and clock resources, deasserts reset, and registers the port. Remove and PM callbacks unregister/suspend/resume through 8250 and manage reset/clock state.

## Control Flow
Probe allocates private state, initializes the embedded `uart_port` lock, sets `UPF_BOOT_AUTOCONF | UPF_FIXED_PORT | UPF_FIXED_TYPE`, installs `handle_break`, maps the MMIO resource with `devm_ioremap()`, reads port properties, configures `UPIO_MEM32`/`regshift = 2`, gets an optional shared reset, and either uses firmware-provided `uartclk` or enables a clock and derives it. Reset is deasserted before `serial8250_register_8250_port()`. Suspend delegates to 8250 and disables the clock unless the port is an active console with console suspend disabled; resume mirrors that order.

## State And Persistence
Runtime state is in `tegra_uart` and the 8250 core's port. Clock enablement may persist across suspend for active consoles. Reset state is asserted on remove and probe failure after registration failure. There is no file-backed persistence.

## Dependencies And Integration Points
Depends on platform devices, OF compatible `nvidia,tegra20-uart`, ACPI ID `NVDA0100`, reset controls, clocks, console state helpers, `uart_read_port_properties()`, and the 8250 core's `PORT_TEGRA` entry.

## Risks And Test Signals
Risks include break-drain timeout behavior, clock handling when `uartclk` is firmware-provided but `uart->clk` is NULL, console suspend corner cases, and reset assertion ordering. Test signals include DT and ACPI probe, RX break handling without interrupt storms, suspend/resume with console and non-console ports, remove after registration, and baud correctness when the clock is supplied by firmware versus the clock framework.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_tegra.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_uniphier.c -->
# sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_uniphier.c

## Purpose
Adapts Socionext UniPhier UART hardware to the 8250 core. The hardware is 8250-like but uses 32-bit MMIO, shared register words for CHAR/FCR and LCR/MCR, no SCR, and a divisor latch at a fixed offset without DLAB.

## Important APIs, Types, And Functions
`struct uniphier8250_priv` stores the registered line, clock, and `atomic_write_lock` used for read-modify-write access to shared 32-bit register words. `uniphier_serial_in()` and `uniphier_serial_out()` remap standard UART offsets and mask/shift byte lanes. `uniphier_serial_dl_read()` and `uniphier_serial_dl_write()` access `UNIPHIER_UART_DLR`. `uniphier_uart_probe()` maps MMIO, enables the clock, initializes the customized `uart_8250_port`, and registers it. Early console setup configures the port as MMIO32 and sets `device->baud = 0` to avoid touching the divisor.

## Control Flow
Probe gets the MMIO resource, maps it, allocates private state, gets/enables the clock, stores `uartclk`, initializes the shared-write spinlock, fills the port with mapbase/membase/mapsize and firmware properties, sets fixed `PORT_16550A`, `UPIO_MEM32`, `fifosize = 64`, `regshift = 2`, `UART_CAP_FIFO`, optional `UART_CAP_AFE` from `auto-flow-control`, custom serial and divisor callbacks, then calls `serial8250_register_8250_port()`. Remove unregisters and disables the clock. System suspend/resume delegates to 8250 and gates the clock unless the active console must remain powered.

## State And Persistence
Private state is per device and exists for the platform driver's lifetime. The lock protects non-atomic shared-register updates against concurrent console/interrupt accesses. Hardware register contents are volatile and reprogrammed by the 8250 core; no persistent storage is used.

## Dependencies And Integration Points
Depends on OF compatible `socionext,uniphier-uart`, common clocks, 8250 registration, firmware port property parsing, and earlycon. It integrates by overriding accessors while leaving most line discipline, interrupts, termios, console, and PM behavior to `8250_port.c`.

## Risks And Test Signals
The custom accessor path is sensitive to byte-lane shifts and shared-register read-modify-write races. Probe has an error path after `clk_prepare_enable()` where a failing `uart_read_port_properties()` returns without disabling the clock. Test signals include early console without divisor writes, normal console/tty operation, LCR/MCR/FCR/SCR behavior, hardware flow control from `auto-flow-control`, suspend/resume clock balance, and lockdep coverage under console plus interrupt traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_uniphier.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/8250/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/tty/serial/8250/Kconfig

## Purpose
Defines the configuration surface for the 8250/16550 serial subsystem and its platform, bus, console, DMA, ISA, PCI, ACPI, DT, and SoC-specific variants.

## Important APIs, Types, And Functions
The root `SERIAL_8250` tristate selects `SERIAL_CORE` and optional modem GPIO support. Core options include PNP support, 16550A variant probing, console/earlycon, DMA, PCI library, PCMCIA (`SERIAL_8250_CS`), runtime UART limits, extended legacy options, shared IRQs, IRQ autodetection, RSA support, and many multiport ISA boards. Later entries select or gate platform drivers such as ASPEED VUART, BCM2835 AUX, DFL, DesignWare, Emma Mobile, IOC3, KEBA, RT288X, OMAP, Loongson, LPC18xx, MT6577, UniPhier, Ingenic, LPSS, MID, Pericom, PXA, Tegra, Broadcom, FSL, NI, PCI1XXXX, and others.

## Control Flow
Kconfig selections determine which object files are built by `drivers/tty/serial/8250/Makefile`, which symbols are available for registration, and which generic features the core compiles in. Console support requires built-in `SERIAL_8250=y`, while many bus/platform variants are tristates that depend on `SERIAL_8250` and their bus/architecture prerequisites.

## State And Persistence
State is kernel configuration. Values persist in `.config` and shape built-in/module composition, default port counts, default runtime UARTs, and whether boot/early console support exists.

## Dependencies And Integration Points
Integrates with top-level serial Kconfig and Makefiles, `SERIAL_CORE`, `SERIAL_EARLYCON`, DMAEngine, PCI, PCMCIA, OF, ACPI, architecture symbols, GPIO modem-control helpers, MFD/regmap, and SoC-specific clock/bus dependencies.

## Risks And Test Signals
Risks include invalid dependency combinations, console options enabled as modules when built-in is required, missing selects for helper libraries, and defaults that build unsupported drivers on compile-test targets. Test signals are `olddefconfig`, allyesconfig/allmodconfig, architecture-specific builds, module dependency checks, boot with `console=ttyS*` and `earlycon`, and confirming each selected symbol has a matching object in the 8250 Makefile.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/8250/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/8250/Makefile -->
# sources/distributed-fs/ceph-client/drivers/tty/serial/8250/Makefile

## Purpose
Defines the object graph for the 8250 serial subsystem, splitting the common driver into module components and wiring each Kconfig option to its platform or bus-specific object.

## Important APIs, Types, And Functions
`obj-$(CONFIG_SERIAL_8250) += 8250.o` and `8250-y := 8250_core.o` form the main module, with conditional additions for PNP, DMA, PCI library, Fintek, and RSA. `obj-$(CONFIG_SERIAL_8250) += 8250_base.o` builds the base-port module from `8250_port.o`, `8250_dma.o` when enabled, and `8250_dwlib.o` when selected. Console support adds `8250_early.o`. The remaining `obj-*` lines map individual options to files such as `8250_pxa.o`, `8250_rt288x.o`, `serial_cs.o`, `8250_uniphier.o`, and `8250_tegra.o`.

## Control Flow
The build graph enforces the division described in `8250_rsa.c`: common port operations live in `8250_base`, while `8250.ko` can pass operation pointers to RSA support without direct circular references. Enabled Kconfig symbols determine which registration frontends are compiled as built-ins or modules.

## State And Persistence
No runtime state. The file is build metadata that persists in the kernel build tree and affects generated modules and link order.

## Dependencies And Integration Points
Depends directly on the symbols declared in `8250/Kconfig` and integrates with the parent serial Makefile, which always descends into `8250/`. Its object naming must match source files and module aliases expected by platform/PCI/PCMCIA binding.

## Risks And Test Signals
Risks are missing object mappings for Kconfig entries, circular module dependencies, and feature objects linked into the wrong module. Test signals include `make drivers/tty/serial/8250/`, `modpost` dependency output, loading `8250`, `8250_base`, and selected platform modules, and verifying console/earlycon objects appear only when configured.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/8250/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/8250/serial_cs.c -->
# sources/distributed-fs/ceph-client/drivers/tty/serial/8250/serial_cs.c

## Purpose
Implements the PCMCIA/CardBus-era frontend for 8250-compatible serial and modem cards, including many legacy multifunction Ethernet/modem, multiport, and vendor-quirked cards.

## Important APIs, Types, And Functions
`struct serial_quirk` describes manufacturer/product matching, multiport count overrides, configuration hooks, UART setup hooks, wakeup hooks, and post-enable hooks. `struct serial_info` tracks the PCMCIA device, registered 8250 lines, multiport/slave state, IDs, OXCF950 control port, and chosen quirk. Quirk helpers adjust clocks, enable IBM config bits, collapse Nokia multiport behavior, enable Socket ESR IRQs, and wake OXSEMI/Possio devices. Core lifecycle functions are `serial_probe()`, `serial_detach()`, `serial_remove()`, `serial_suspend()`, `serial_resume()`, `serial_config()`, `setup_serial()`, `simple_config()`, `multi_config()`, and `pfc_config()`.

## Control Flow
Probe allocates `serial_info`, enables IRQ and auto I/O assignment flags, optionally enables speaker support, and calls `serial_config()`. Configuration determines whether the card is multifunction or multiport from socket/function metadata, CIS resources, and quirk tables. Simple cards try normal CIS windows, aliases, standard COM bases, then any free port. Multiport cards try a contiguous window or paired windows, enable the device, and register each port with `serial8250_register_8250_port()`. PFC cards find the serial function's resource and register a slave port. Remove/unbind unregisters each line and disables the PCMCIA device for non-slave functions. Suspend/resume delegates to 8250 and reruns wakeup quirks.

## State And Persistence
State is per inserted card and exists only while the PCMCIA device is bound. `line[]` stores up to four registered 8250 line numbers, `ndev` is the authoritative count, and `slave` prevents disabling a shared multifunction device from a secondary function. Module parameters `do_sound` and `buggy_uart` affect probe behavior globally.

## Dependencies And Integration Points
Depends on PCMCIA CIS/resource APIs, manufacturer/product constants, firmware CIS overrides declared with `MODULE_FIRMWARE()`, I/O port accessors, and the 8250 registration/suspend/resume APIs. It integrates legacy PCMCIA hotplug with the normal `ttyS*` 8250 core.

## Risks And Test Signals
Risk is dominated by legacy hardware quirks: bad CIS windows, incorrect multiport count, OXCF950 control sequencing, shared multifunction disable ordering, and registering ports before post-init quirks. `line[4]` bounds rely on quirk/multiport values not exceeding four. Test signals include insertion/removal of single-port, dual-port, quad-port, PFC, and OXSEMI/Possio cards; correct IRQ sharing; suspend/resume wakeup; firmware CIS loading; `buggy_uart` probe bypass; and no resource leaks after failed configuration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/8250/serial_cs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/tty/serial/Kconfig

## Purpose
Provides the top-level kernel configuration menu for serial drivers, including generic serial core support, early console transports, the included 8250 submenu, and many non-8250 UART drivers.

## Important APIs, Types, And Functions
Top-level symbols include `SERIAL_CORE`, `SERIAL_CORE_CONSOLE`, `SERIAL_EARLYCON`, semihosting and RISC-V SBI earlycon options, legacy/architecture drivers, SoC UART drivers, and helper `SERIAL_MCTRL_GPIO`. The file sources `drivers/tty/serial/8250/Kconfig`, then defines options for drivers including Altera JTAG UART, Altera UART, AMBA PL010/PL011, Atmel, BCM63xx, Cadence/Xilinx, Freescale LPUART/LINFlex, LiteUART, Tegra, STM32, Sunplus, Nuvoton MA35D1, and many others, often with paired console symbols.

## Control Flow
Kconfig controls whether each driver is built, whether its console/earlycon support is available, and whether supporting subsystems such as `SERIAL_CORE_CONSOLE`, `SERIAL_EARLYCON`, `SERIAL_MCTRL_GPIO`, DMA, clocks, OF, PCI, or architecture support are selected. The parent Makefile consumes these symbols to include object files.

## State And Persistence
State is static kernel build configuration. It persists as `.config` and controls module availability, major/minor device support, console support, and limits such as Altera UART max ports and default baud rate.

## Dependencies And Integration Points
Integrates with the TTY serial core, console subsystem, earlycon, architecture-specific platform support, OF/ACPI, PCI, DMA, clocks, and the `drivers/tty/serial/Makefile`. The 8250 submenu is a major integration point and is always sourced from this top-level menu.

## Risks And Test Signals
Risks include missing `select SERIAL_CORE`, console options not requiring built-in drivers, stale architecture dependencies, and config options without Makefile counterparts. Test signals are Kconfig parse, `olddefconfig`, allyesconfig/allmodconfig, per-architecture builds, console boot tests for selected console symbols, and verifying Altera/8250 choices map to expected tty device names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/Makefile -->
# sources/distributed-fs/ceph-client/drivers/tty/serial/Makefile

## Purpose
Defines the build composition for the top-level serial driver directory.

## Important APIs, Types, And Functions
The file builds `serial_base.o` from `serial_core.o`, `serial_base_bus.o`, `serial_ctrl.o`, and `serial_port.o` when `SERIAL_CORE` is enabled. It maps earlycon helpers and individual serial drivers to their Kconfig symbols. It always descends into `8250/` with `obj-y += 8250/`, adds Altera JTAG UART and Altera UART objects for their symbols, orders SPARC serial drivers before 8250 to preserve `ttySx` minor naming, and links modem-control GPIO and KGDB console helpers as configured.

## Control Flow
The build system evaluates each `obj-$(CONFIG_*)` line and includes the object or subdirectory as built-in or module. The explicit SPARC ordering comment documents a behavioral dependency on link/probe order for shared ttyS minor space.

## State And Persistence
No runtime state. This is build metadata that persists in the source tree and affects generated kernel images and modules.

## Dependencies And Integration Points
Consumes symbols from `drivers/tty/serial/Kconfig`, descends into 8250-specific build rules, and links drivers into the TTY, console, and platform-driver ecosystems.

## Risks And Test Signals
Risks are stale object mappings, wrong ordering for drivers sharing `ttySx`, and missing subdirectory traversal. Test signals are directory-level builds, `modpost`, boot enumeration of SPARC/8250 ttyS devices, and checking every enabled Kconfig symbol used in this work item (`SERIAL_ALTERA_JTAGUART`, `SERIAL_ALTERA_UART`, `SERIAL_8250*`) produces an expected object.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/altera_jtaguart.c -->
# sources/distributed-fs/ceph-client/drivers/tty/serial/altera_jtaguart.c

## Purpose
Implements the Linux serial-core driver for the Altera/Intel FPGA JTAG UART, a simple two-register UART-like console/debug interface exposed through platform devices or device tree.

## Important APIs, Types, And Functions
Register definitions cover data valid/available bits and control read/write interrupt, activity, and write-space fields. `altera_jtaguart_tx_space()` reads write FIFO capacity with `FIELD_GET()`. UART ops include TX empty, fixed modem-control reporting, TX/RX interrupt mask toggling via `read_status_mask`, no-op break/termios controls, RX drain (`altera_jtaguart_rx_chars()`), bounded TX fill (`altera_jtaguart_tx_chars()`), IRQ handler, startup/shutdown, config/type/request/release/verify callbacks, optional console write/setup, optional console bypass when no JTAG host activity exists, and earlycon setup. `altera_jtaguart_probe()` maps the single port and registers it with `uart_add_one_port()`.

## Control Flow
Module init registers a `uart_driver` for `ttyJ` and then the platform driver. Probe accepts platform id `-1` as line 0, gets MMIO and IRQ from resources or platform data, maps eight bytes, initializes the global single `uart_port`, and adds it to serial core. Startup requests IRQ and enables RX interrupts. IRQ handling reads interrupt status bits, locks the port, drains RX if RE is pending, fills TX if WE is pending, and returns whether work was done. Remove unregisters the port and unmaps MMIO.

## State And Persistence
The driver uses one static `uart_port` in `altera_jtaguart_ports[1]`; interrupt enable state is stored in `port->read_status_mask`. Runtime state is otherwise serial-core tty state and volatile JTAG UART registers. There is no persistent storage or baud/termios programming because JTAG UART does not expose normal line settings.

## Dependencies And Integration Points
Depends on platform devices, OF compatibles `ALTR,juart-1.0` and `altr,juart-1.0`, serial core, optional console/earlycon, and legacy platform data from `linux/altera_jtaguart.h`. The device appears as major/minor from `ALTERA_JTAGUART_MAJOR`/`ALTERA_JTAGUART_MINOR` and tty name `ttyJ`.

## Risks And Test Signals
Risks include the single-port static limit, mandatory IRQ requirement for normal operation, use of `read_status_mask` as both status mask and control shadow, busy-wait console output when no host is connected unless bypass is enabled, and no platform drvdata on probe. Test signals include DT and platform-data probe, ttyJ console and earlycon output, RX/TX IRQs, console bypass behavior with disconnected host, removal/unmap, and sysrq handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/altera_jtaguart.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/altera_uart.c -->
# sources/distributed-fs/ceph-client/drivers/tty/serial/altera_uart.c

## Purpose
Implements the Linux serial-core driver for the Altera softcore UART used in FPGA/Nios systems, including interrupt or timer-polled operation, platform-data and device-tree probe, console support, and earlycon.

## Important APIs, Types, And Functions
Register definitions cover RX/TX data, status, control, divisor, and EOP. `struct altera_uart` embeds `uart_port`, a polling timer, modem signal shadow `sigs`, and interrupt/control shadow `imr`. Core callbacks include `altera_uart_tx_empty()`, `altera_uart_get_mctrl()`, `altera_uart_set_mctrl()`, TX/RX start/stop, break control, divisor-only termios programming, RX/TX handlers, IRQ handler, poll timer, startup/shutdown, config/type/request/release/verify, optional console poll, console write/setup, earlycon setup, platform probe/remove, and module init/exit.

## Control Flow
Module init registers the `ttyAL` `uart_driver` and platform driver. Probe chooses a line from `pdev->id` or the first free static slot, reads MMIO, optional IRQ, clock frequency from platform data or DT `clock-frequency`, maps the UART register window, fills the `uart_port`, stores drvdata, and calls `uart_add_one_port()`. Startup uses IRQ mode when an IRQ exists; otherwise it starts a periodic timer that calls the same interrupt routine. It enables RX-ready interrupts in `imr`. The IRQ routine masks status with `imr`, locks the port, drains RX, fills TX, and returns `IRQ_RETVAL(isr)`. Shutdown disables all interrupts and frees IRQ or deletes the timer.

## State And Persistence
The driver uses a static `altera_uart_ports[CONFIG_SERIAL_ALTERA_UART_MAXPORTS]` array. Per-port state includes mapped MMIO, line, clock, local control-register mirror, modem signal shadow, and optional timer. Hardware divisor and control/status registers are volatile. No persistent storage exists.

## Dependencies And Integration Points
Depends on serial core, tty flip buffers, platform devices, OF compatibles `ALTR,uart-1.0` and `altr,uart-1.0`, optional platform data from `linux/altera_uart.h`, console/earlycon infrastructure, and configured max-port/default-baud Kconfig symbols. The driver exposes `ttyAL` devices with major 204/minor 213.

## Risks And Test Signals
Risks include static-slot reuse, manual `ioremap()` cleanup, no runtime PM or clock framework integration, incomplete termios error-mask handling noted by FIXME, timer polling when no IRQ is present, and control-register mirror consistency. Test signals include DT and platform-data probe, IRQ and no-IRQ polling modes, baud divisor programming from `clock-frequency`, RX error counters for parity/frame/break/overrun, RTS/CTS behavior, console and earlycon output, poll console operations, module unload, and max-port bounds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/altera_uart.c -->
