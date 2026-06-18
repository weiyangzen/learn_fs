# subset-b-005451 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_exar.c -->
## sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_exar.c

Purpose: PCI 8250 glue for Exar/MaxLinear XR17C15x, XR17V25x, XR17V35x, Commtech/Fastcom, AccessIO, Advantech, USR, IBM, SeaLevel, Siemens IOT2040, and Connect Tech adapters. It discovers multiport PCI UART cards, applies board-specific register layout and RS485/GPIO quirks, and registers every channel with the serial8250 core.

Important APIs, types, and functions: `struct exar8250_board` selects `setup`/`exit` callbacks, port spacing, and optional fixed port count. `struct exar8250` holds the BAR mapping, EEPROM bit-bang adapter, oscillator frequency, and registered line numbers. `exar_pci_probe()` enables the PCI device, maps BAR0, allocates IRQ vectors, clears Exar global interrupt state, initializes 93cx6 EEPROM access, calls the board setup callback for each channel, and calls `serial8250_register_8250_port()`. `default_setup()`, `cti_port_setup_*()`, `pci_xr17v35x_setup()`, and `pci_fastcom335_setup()` populate `struct uart_8250_port`. `generic_rs485_config()`, `sealevel_rs485_config()`, `iot2040_rs485_config()`, and `cti_rs485_config_mpio_tristate()` implement RS485 modes. `xr17v35x_get_divisor()`/`set_divisor()` handle fractional baud divisors.

Control flow: PCI ID table entries point to board templates. Probe determines port count from board data, PCI vendor/device encoding, or Connect Tech FPGA IDs, then iterates channels until the BAR capacity limit. Setup callbacks choose UART type, clock, per-channel offset, FIFO trigger levels, fractional divisor handling, startup/shutdown hooks, RS485 support, and sometimes one-time MPIO/GPIO/EEPROM board initialization on channel 0. Remove unregisters every port and tears down GPIO child devices. Suspend/resume delegates to serial8250 per line and clears global INT0 on resume.

State and persistence: persistent hardware configuration comes from PCI IDs, DMI matches, and Connect Tech EEPROM words for oscillator/port flags. Runtime state is in `priv->line[]`, `priv->nr`, `priv->osc_freq`, child GPIO platform device private data, UART sleep registers, MPIO levels, and 8250 core per-port state. No filesystem state is written.

Dependencies and integration points: integrates with PCI, `8250_pcilib`, serial8250, 93cx6 EEPROM helpers, DMI, platform GPIO child devices (`gpio_exar` via software nodes), PM sleep hooks, and RS485 userspace ioctls through `uart_port.rs485_config`. The module imports `SERIAL_8250_PCI`.

Risks: board support is table- and EEPROM-sensitive; wrong subsystem IDs or malformed EEPROM values can select the wrong transceiver behavior. `exar_pci_probe()` breaks on first failed port setup/registration but returns success after setting `priv->nr`, so partial card registration is possible. RS485 polarity/tri-state handling touches nonstandard MPIO/DLD registers and can affect external buses. GPIO child teardown assumes channel 0 exists and was registered. Test signals: PCI probe/remove on representative 2/4/8/12/16-port cards, baud accuracy on XR17V fractional divisors, suspend/resume wake interrupts, RS232/RS422/RS485 mode switching, IOT2040 termination, SeaLevel polarity, Connect Tech EEPROM fallback, and partial failure cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_exar.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_exar_st16c554.c -->
## sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_exar_st16c554.c

Purpose: legacy static probe module for Exar ST16C554 ISA-style cards. It does not discover hardware dynamically; it publishes four fixed 8250 platform ports.

Important APIs, types, and functions: `exar_data[]` is an array of `struct plat_serial8250_port` entries created with `SERIAL8250_PORT()` at I/O bases `0x100`, `0x108`, `0x110`, and `0x118`, all sharing IRQ 5. `exar_device` is a `platform_device` named `serial8250` with ID `PLAT8250_DEV_EXAR_ST16C554`. `exar_init()` registers that device at module init.

Control flow: module load immediately calls `platform_device_register()`. The generic 8250 platform driver consumes `platform_data`, probes each fixed port, and owns subsequent tty registration. There is no module exit path in this file, so it is effectively an init-only platform-device producer.

State and persistence: the only local state is the static port table and platform device object. Runtime UART state is owned by the generic serial8250 platform layer. No dynamic allocation, persisted state, or private per-port data exists.

Dependencies and integration points: depends on `linux/serial_8250.h` and local `8250.h` platform IDs. It integrates by using the common `serial8250` platform-device ABI rather than calling `serial8250_register_8250_port()` itself.

Risks: fixed I/O addresses and IRQ can collide with other ISA resources if loaded on unsuitable hardware. The absence of autoprobed resources means tests should verify that the platform registration is only enabled where the user expects this card. Test signals: module load should create four `ttyS*` ports with the expected bases and shared IRQ; serial loopback or interrupt-driven RX/TX on every channel should validate the static map.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_exar_st16c554.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_fintek.c -->
## sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_fintek.c

Purpose: Super I/O companion probe for Fintek LPC/eSPI multi-UART chips. It is invoked by 8250 PNP/legacy probing to identify the backing Fintek logical device, configure interrupt mode/FIFO/clocking, and attach RS485 and termios callbacks to an already discovered `uart_8250_port`.

Important APIs, types, and functions: `struct fintek_8250` stores chip ID, Super I/O base, LDN index, and unlock key. `fintek_8250_probe()` is the external entry point. `probe_setup_port()` scans common config ports (`0x4e`, `0x2e`) and keys, validates vendor/chip IDs, walks chip-specific LDN ranges, and matches the UART I/O base. `fintek_8250_rs485_config()` writes the `RS485` register. `fintek_8250_set_termios()` chooses a supported Fintek UART input clock to satisfy requested baud rates. `fintek_8250_set_irq_mode()` aligns Super I/O IRQ sharing/polarity with Linux IRQ trigger type.

Control flow: the probe temporarily enters Super I/O configuration mode with `request_muxed_region()`, matches the target UART, sets IRQ/FIFO features, exits config mode, then stores a devm-allocated private copy in `uart->port.private_data`. Handler installation is conditional on chip capabilities. Later termios and RS485 ioctls re-enter Super I/O mode briefly to update registers.

State and persistence: chip configuration is persisted in Super I/O registers until reset or firmware change. Driver runtime state is just the copied config tuple in `private_data`. The UART core owns baud, tty, and RS485 user-visible state.

Dependencies and integration points: depends on raw I/O port access (`inb`/`outb`), IRQ trigger metadata, PNP/PCI-era 8250 probing, `serial8250_do_set_termios()`, and serial RS485 core validation.

Risks: config-mode access is fragile; wrong key/base scanning could touch another Super I/O, though `request_muxed_region()` reduces races. RS485 validation has non-obvious polarity constraints and delay support differs for port 0 and chip family. Unsupported baud requests are silently reverted to the old baud. Test signals: chip-ID scan on each supported Fintek PID, IRQ mode verification for level and edge interrupts, FIFO depth behavior, baud clock switching at 115200/921600/1152000/1500000, RS485 delay clamping, and concurrent Super I/O users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_fintek.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_fourport.c -->
## sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_fourport.c

Purpose: legacy static platform-device registration for AST Fourport-compatible 8250 boards. It publishes two groups of four fixed I/O ports to the generic serial8250 platform layer.

Important APIs, types, and functions: `SERIAL8250_FOURPORT()` wraps `SERIAL8250_PORT_FLAGS()` with `UPF_FOURPORT`. `fourport_data[]` lists ports at `0x1a0`..`0x1b8` on IRQ 9 and `0x2a0`..`0x2b8` on IRQ 5. `fourport_device` is named `serial8250` with ID `PLAT8250_DEV_FOURPORT`. `fourport_init()` registers it at module init.

Control flow: module init registers one platform device; generic 8250 code parses the static port list and handles hardware probing, tty registration, and interrupts.

State and persistence: static table only. There is no per-device allocation or remove callback in this file. All runtime state lives in serial8250 once the platform device is registered.

Dependencies and integration points: integrates with `serial8250` platform probing through `platform_data`; `UPF_FOURPORT` tells the common code to use fourport interrupt semantics.

Risks: fixed ISA-style resources can conflict or create false-positive ports if loaded on machines without the board. Test signals: verify all eight fixed entries are exposed only when intended, shared interrupt behavior works for each group, and `UPF_FOURPORT` produces correct interrupt acknowledgment under RX/TX load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_fourport.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_fsl.c -->
## sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_fsl.c

Purpose: Freescale/NXP 16550 variant support for a break-interrupt erratum and ACPI instantiation. The file is intentionally not a complete UART driver; it reuses serial8250 and provides an alternate IRQ handler plus an ACPI platform wrapper for `NXP0018`.

Important APIs, types, and functions: `fsl8250_handle_irq()` is exported for other 8250 frontends, including Open Firmware serial. It follows `serial8250_default_handle_irq()` but tracks break state in `up->lsr_saved_flags` and performs a dummy RX read on the interrupt after a break to avoid endless BI/FIFO-aging interrupts. Under `CONFIG_ACPI`, `fsl8250_acpi_probe()` maps MMIO, reads `clock-frequency`, fills a `uart_8250_port`, sets `port.handle_irq = fsl8250_handle_irq`, registers it, and stores the line in `struct fsl8250_data`.

Control flow: IRQ handling locks the port, reads IIR, handles the special RLSI-after-BI path early, otherwise drains RX, backs off on overrun, handles modem status and TX, then saves the BI bit for the next event. ACPI probe/remove simply register/unregister one 8250 port.

State and persistence: the only erratum state is the BI bit carried in `lsr_saved_flags`; ACPI state is the registered line number. Hardware state is normal 8250 MMIO plus interrupt flags.

Dependencies and integration points: depends on serial8250 RX/TX helpers, ACPI platform device resources, shared IRQ support, and `EXPORT_SYMBOL_GPL` for reuse from `8250_of.c`.

Risks: the workaround intentionally avoids reading LSR in one path; changes around LSR clearing can reintroduce interrupt storms. ACPI probe requires a clock-frequency property and does not support optional clocks. Test signals: forced break at common baud rates, overrun backoff, normal RX/TX after a break, ACPI resource parsing, and OF `fsl,ns16550` integration using this handler.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_fsl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_hp300.c -->
## sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_hp300.c

Purpose: HP 300/400 DCA/APCI serial support layered onto serial8250. It handles DIO-bus DCA cards, Frodo APCI internal ports, and early console setup from hp300 boot information.

Important APIs, types, and functions: `hp300_setup_serial_console()` prepares an early `uart_port` for either APCI select code 256 or DCA select codes. `hpdca_init_one()` registers a DIO DCA UART and enables board interrupts. `hp300_8250_init()` gates on `MACH_IS_HP300`, registers the DCA DIO driver, and optionally registers APCI ports 1-3 on HP 400-class systems. `hpdca_remove_one()` and `hp300_8250_exit()` unregister ports and free the APCI linked list.

Control flow: early console setup runs before full driver init and may reserve the console port. Normal init registers DIO devices and then enumerates static APCI offsets. DCA probe fills `uart_8250_port` with memory-mapped DIO address, IRQ, baud base, `regshift=1`, and common 8250 flags. APCI uses Frodo base offsets, `regshift=2`, and currently no interrupt support.

State and persistence: `num_ports` tracks discovered ports. APCI lines are stored in a linked list of `struct hp300_port`; DCA line numbers are stored as DIO driver data. Board interrupt-enable and reset registers are written directly.

Dependencies and integration points: depends on m68k HP300 platform globals, DIO bus APIs, early serial console, 8250 registration, and architecture I/O helpers.

Risks: APCI port 1 is skipped when console support is enabled, so console/non-console combinations need care. APCI lacks interrupt support and may rely on polling. The DCA early-console path avoids double registration by select code. Test signals: boot console on DCA and APCI, DIO hot/remove paths, DCA interrupt enable/reset behavior, APCI polling TX/RX, and module unload freeing every registered line.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_hp300.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_hub6.c -->
## sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_hub6.c

Purpose: static platform-device producer for legacy HUB6 serial cards. It exposes up to twelve hub-addressed ports to the generic serial8250 platform driver.

Important APIs, types, and functions: `HUB6(card, port)` fills `struct plat_serial8250_port` with I/O base `0x302`, IRQ 3, clock `1843200`, `iotype = UPIO_HUB6`, boot autoconfig, and encoded `hub6` selector bits. `hub6_data[]` contains six ports on card 0 and six on card 1. `hub6_init()` registers a `serial8250` platform device with ID `PLAT8250_DEV_HUB6`.

Control flow: module init registers the platform device; the 8250 platform driver handles indexed HUB6 I/O access, port testing, tty creation, and interrupts.

State and persistence: only static registration data exists locally. Runtime port and tty state belongs to serial8250.

Dependencies and integration points: uses the `UPIO_HUB6` 8250 I/O type, so it depends on common 8250 support for HUB6 multiplexing.

Risks: fixed base/IRQ and large static port count can conflict or generate dead ports on systems without compatible hardware. Test signals: verify selector encoding for all 12 entries, shared IRQ RX/TX under simultaneous ports, and no false registration when hardware is absent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_hub6.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_ingenic.c -->
## sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_ingenic.c

Purpose: OF platform driver and early console support for Ingenic JZ/X-series SoC UARTs with 8250-like registers plus SoC-specific enable, modem, timeout, and FIFO behavior.

Important APIs, types, and functions: `struct ingenic_uart_config` supplies FIFO and TX load size per compatible. `struct ingenic_uart_data` stores module/baud clocks and the registered line. `OF_EARLYCON_DECLARE()` entries install early console setup variants; JZ4750 adjusts high oscillator clocks by `/2`. `ingenic_uart_serial_out()` forces `UART_FCR_UME`, mirrors RLSI to timeout interrupt enable, and toggles modem-control extension bits. `ingenic_uart_serial_in()` hides nonstandard bits. `ingenic_uart_probe()` maps registers, enables clocks, fills a `uart_8250_port`, and registers it.

Control flow: early console reads `/ext` clock-frequency from the flat DT, programs divisor/FIFO/MCR, and replaces console write with an Ingenic polling putc. Normal probe selects match data, maps MMIO, reads port properties, enables clocks, sets serial in/out hooks and FIFO capabilities, registers with serial8250, then stores the line for remove.

State and persistence: runtime state consists of two enabled clocks and the line number. Hardware state includes UART module enable, FIFO trigger state, and modem extension bits. No suspend/resume hooks are present here.

Dependencies and integration points: relies on OF matching, clock framework, earlycon infrastructure, serial8250 registration, and standard tty/console paths.

Risks: early console clock discovery assumes an `/ext` node and can misprogram baud if DT differs. `serial_in/out` masks nonstandard bits; future core changes reading those registers must preserve this abstraction. Test signals: earlycon on every compatible, baud correctness with 12/24 MHz ext clocks, modem-status interrupt behavior, FIFO sizes per SoC, and clock disable on remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_ingenic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_ioc3.c -->
## sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_ioc3.c

Purpose: platform driver for SGI IOC3 8250-compatible UARTs. It adapts IOC3 byte-lane ordering and fixed UART clock to the generic serial8250 core.

Important APIs, types, and functions: `struct ioc3_8250_data` is intended to store the registered line. `ioc3_serial_in()` and `ioc3_serial_out()` access `membase + (offset ^ 3)` to compensate for register byte layout. `serial8250_ioc3_probe()` obtains MMIO resource, maps it, gets optional IRQ, fills `uart_8250_port`, and registers it. `serial8250_ioc3_remove()` unregisters `data->line`.

Control flow: probe maps the resource, falls back to IRQ 0 polling if no IRQ is available, installs custom serial accessors, and registers a fixed `PORT_16550A` with `IOC3_UARTCLK`. Remove unregisters the stored line.

State and persistence: intended runtime state is only the registered line in devm-allocated data. Hardware state is standard 16550 registers behind custom byte addressing.

Dependencies and integration points: platform bus resources, `devm_ioremap()`, serial8250 port registration, and SGI IOC3 platform device creation.

Risks: the probe stores `line` in a local variable but does not assign `data->line = line` before `platform_set_drvdata()`. Remove therefore may unregister an uninitialized or zero line, which is a concrete teardown bug. Test signals: probe/remove with dynamic debug or KASAN, polling fallback when IRQ is absent, byte-lane register read/write validation, and repeated bind/unbind to catch the line-storage issue.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_ioc3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_keba.c -->
## sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_keba.c

Purpose: auxiliary-bus driver for KEBA UART FPGA IP cores. It exposes a 16550/16750/16C950-like UART through serial8250 and manages physical RS232/RS422/RS485 mode switching.

Important APIs, types, and functions: `struct kuart` stores the parent KEBA auxiliary device, control-register mapping, line, flags, capabilities, and current mode. `kuart_probe()` maps the pre-UART control area, reads optional capability bits, fills a `uart_8250_port`, sets RS485 defaults, and registers the port. `kuart_rs485_config()` switches physical interface mode and programs 16C950 Additional Control Register DTR behavior via enhanced mode. `kuart_remove()` disables the physical interface when capability-controlled and unregisters the line.

Control flow: auxiliary device IDs distinguish fixed RS485, fixed RS232, and capability-based variants. Probe maps only registers before `KUART_BASE`; serial8250 maps the UART registers. For capability-based cores, default mode priority is RS485 over RS422 over RS232. RS485 ioctls may break-before-make by setting `KUART_MODE_NONE`, configure DTR line behavior, then enable the selected PHY.

State and persistence: `kuart->mode` is runtime state tracking the active physical mode. Hardware control register persists selected PHY mode until reset. Serial8250 owns tty state.

Dependencies and integration points: depends on `auxiliary_bus`, KEBA misc auxiliary device structure, MMIO, serial8250, and RS485 core flags including `SER_RS485_MODE_RS422`.

Risks: mode switching affects external transceivers and bus contention; capability reads must be trustworthy. Enhanced-mode ICR access must preserve LCR/EFR state. Test signals: all auxiliary IDs, capability masks with no supported mode, RS485/RS422/RS232 ioctl transitions, DTR-controlled direction, remove setting mode none, and loopback/line-level validation after every mode switch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_keba.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_loongson.c -->
## sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_loongson.c

Purpose: OF platform driver for Loongson UARTs with optional fractional divisor support and inverted modem-control/status pins. It registers one fixed 16550A-style port with serial8250.

Important APIs, types, and functions: `struct loongson_uart_ddata` describes fractional divisor availability and MCR/MSR inversion masks. `struct loongson_uart_priv` stores line, clock, resource, reset control, and match data. `loongson_serial_in/out()` apply `serial_fixup()` around MMIO access. `loongson_frac_get_divisor()`/`set_divisor()` use `LOONGSON_UART_DLF` for an 8-bit fractional part. `loongson_uart_probe()` maps resources, reads properties/clock, deasserts reset, registers the port, and stores private state. PM callbacks suspend/resume the serial8250 line and clock around console rules.

Control flow: probe selects match data, installs accessors, optionally installs fractional divisor callbacks, reads UART properties, obtains a clock only if no `clock-frequency` was provided, deasserts reset, then registers. Remove unregisters and reasserts reset. Suspend/resume disable clocks unless the port is an active console with console suspend disabled.

State and persistence: runtime state is `line`, optional enabled clock, and reset deassertion. Hardware state includes DLF fractional divisor and inverted pin semantics. No persistent storage.

Dependencies and integration points: OF matching, reset framework, clock framework, serial8250, PM core, and console handling.

Risks: `loongson_serial_out()` shifts `offset` before passing it to `serial_fixup()`, so MCR writes may not match the unshifted `UART_MCR` case if `regshift` changes from zero in future; currently probe sets `regshift=0`. Clock pointer may remain NULL if `uartclk` came from properties, so suspend/resume clock handling relies on console branch not dereferencing an invalid clock path. Test signals: fractional baud accuracy on `ls2k1500`, inverted RTS/DTR/CTS/DSR behavior, reset assertion on remove, suspend/resume with and without console, and property-provided clock versus clock-provider path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_loongson.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_lpc18xx.c -->
## sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_lpc18xx.c

Purpose: NXP LPC18xx/43xx OF platform driver for 8250-compatible UARTs with hardware RS485 control and DMA-friendly FIFO setup.

Important APIs, types, and functions: `struct lpc18xx_uart_data` holds DMA config, UART/register clocks, and the registered line. `lpc18xx_rs485_config()` programs `RS485CTRL` and `RS485DLY`, translating requested after-send delay to baud-clock ticks and clamping to 255. `lpc18xx_uart_serial_out()` forces `UART_FCR_DMA_SELECT` whenever FIFO is enabled. `lpc18xx_serial_probe()` maps MMIO, enables clocks, reads port properties, installs RS485 and serial-out hooks, configures DMA bursts, and registers the port.

Control flow: probe validates MMIO, enables register then UART clocks, initializes a fixed `PORT_16550A` with `UPIO_MEM32`, `regshift=2`, hardware RS485 support, and a `uart_8250_dma` structure. Remove unregisters and disables both clocks.

State and persistence: runtime state is the two prepared clocks, DMA parameters, and line number. Hardware RS485 control and delay registers persist until reconfigured or reset.

Dependencies and integration points: OF matching for `nxp,lpc1850-uart`, clock framework, serial8250 DMA hooks, RS485 core, and MMIO access.

Risks: delay conversion divides by `up->dl_read(up)`; if divisor state is not valid when RS485 config runs, delay math can be wrong. DMA select is forced globally on FIFO enable and should be checked against non-DMA operation. Test signals: RS485 polarity/delay clamp, DMA and PIO transfers, clock failure unwind, device-tree property parsing, and remove-time clock disable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_lpc18xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_lpss.c -->
## sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_lpss.c

Purpose: PCI driver for Intel LPSS/Quark/Baytrail/Braswell/Broadwell/Elkhart Lake UARTs using the DesignWare 8250 library plus Intel-specific clock and DMA setup.

Important APIs, types, and functions: `struct lpss8250_board` supplies reference frequency, base baud, setup, and exit hooks. `struct lpss8250` embeds `dw8250_port_data`, board pointer, DW DMA chip/slave params, and burst size. `byt_set_termios()` programs the BYT private clock M/N divider using `rational_best_approximation()`. `byt_serial_setup()`, `ehl_serial_setup()`, and `qrk_serial_setup()` install board-specific DMA and callbacks. `lpss8250_dma_setup()` connects UART DMA filters/params. `lpss8250_probe()` maps PCI BAR0, calls board setup, `dw8250_setup_port()`, DMA setup, and `serial8250_register_8250_port()`.

Control flow: PCI ID table selects board data. Probe enables PCI, allocates one IRQ vector, fills a `uart_8250_port` as MEM32/regshift 2, maps BAR0, calls setup, configures DesignWare capabilities, registers the port, and stores `data.line`. Remove unregisters, calls board exit, and frees vectors.

State and persistence: runtime state includes registered line, DMA parameter/device references, DMA chip mapping for Quark, and board pointer. BYT clock divider registers persist in device MMIO.

Dependencies and integration points: PCI core, DesignWare 8250 library, DW DMA engine/platform data, DMAengine filter callback, rational arithmetic, and serial8250.

Risks: `byt_serial_setup()` takes a DMA controller reference via `pci_get_slot()` and `byt_serial_exit()` unconditionally `put_device(param->dma_dev)`, so setup failures before assignment must be guarded by board flow. Quark falls back to PIO if DMA probe fails. Clock-divider changes happen in termios and need baud-accuracy coverage. Test signals: each PCI ID family, BYT high baud rates, forced DCD/DSR behavior, DMA channel assignment and fallback, Quark BAR1 DMA mapping cleanup, EHL ACPI DMA request, and bind/unbind leak checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_lpss.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_men_mcb.c -->
## sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_men_mcb.c

Purpose: MCB bus driver for MEN Z025/Z057/Z125 8250 UART IP cores. It discovers how many UART channels are implemented and registers each channel with serial8250.

Important APIs, types, and functions: `struct serial_8250_men_mcb_data` stores port count, line numbers, and per-port offsets. `men_lookup_uartclk()` derives a board-specific clock from the MCB bus name. `read_uarts_available_from_register()` maps the global availability register at offset `0x40`. `read_serial_data()` decodes the upper nibble into channel offsets. `init_serial_data()` handles single-port Z125 versus multiport Z025/Z057. `serial_8250_men_mcb_probe()` loops over discovered offsets and registers each port.

Control flow: probe obtains the MCB memory resource, initializes serial metadata, stores driver data, and for each channel fills a `uart_8250_port` with I/O remap, shared IRQ, board-derived clock, and mapbase offset. Remove iterates stored lines and unregisters them.

State and persistence: line numbers and offsets are stored in devm data. Availability is read from hardware at probe time; no persistent software state is written.

Dependencies and integration points: MCB bus resource/IRQ APIs, MMIO mapping, serial8250, and board-name conventions for clock selection.

Risks: `read_serial_data()` switches on `(uarts_available & mask)` but the case constants are absolute masks for UART1-4; the default branch returns `-EINVAL` for absent ports, so sparse or zero bits can abort discovery. Clock derivation from string prefixes is fragile. Test signals: Z125 single-port, Z025/Z057 with 1-4 populated UARTs, sparse availability patterns, each known board name clock, IRQ sharing, and remove cleanup after partial registration failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_men_mcb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_mid.c -->
## sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_mid.c

Purpose: PCI driver for Intel MID/Penwell/Tangier/Denverton UARTs. It adapts Intel-specific clock programming and HSU DMA integration to serial8250.

Important APIs, types, and functions: `struct mid8250_board` supplies reference clock, base baud, BAR, setup, and exit. `struct mid8250` stores line, DMA index/device, DMA config, board, and embedded HSU DMA chip for DNV. `pnw_setup()`, `tng_setup()`, and `dnv_setup()` locate or initialize DMA devices and set custom IRQ handlers. `mid8250_set_termios()` programs prescaler, multiplier, and divider registers. `mid8250_dma_setup()` allocates RX/TX HSU slave params. `mid8250_probe()` registers a `PORT_16750` port.

Control flow: PCI ID selects board data. Probe enables PCI, maps the board BAR, runs setup, attaches DMA, registers the port, and stores driver data. Custom IRQ handlers service DMA status first, flush RX DMA on specific statuses, then call serial8250 IRQ handling. Remove unregisters and calls board exit.

State and persistence: runtime state includes DMA device references, DMA channel index, HSU DMA chip state, and line number. Termios writes hardware PS/MUL/DIV clock registers.

Dependencies and integration points: PCI, HSU DMA engine, serial8250 DMA callbacks, rational arithmetic, and shared interrupt handling.

Risks: `dnv_setup()` allocates IRQ vectors but `dnv_exit()` does not free them; probe/remove lifecycle should be reviewed against pcim ownership. Tangier skips function 0 as a global register block. DMA fallback paths must still leave PIO functional. Test signals: PNW/TNG/DNV/CDF IDs, function-0 skip, baud accuracy across high rates, DMA IRQ status paths, PIO fallback when DMA probe fails, and repeated bind/unbind for PCI refs/vectors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_mid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_mtk.c -->
## sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_mtk.c

Purpose: MediaTek MT6577-compatible platform driver and earlycon adapter for 8250-like UARTs with high-speed baud sampling, custom flow control, optional DMA, runtime PM, and wake IRQ support.

Important APIs, types, and functions: `struct mtk8250_data` stores line, DMA RX ring position/status, clocks, optional DMA config, and wake IRQ. DMA helpers `mtk8250_rx_dma()`, `mtk8250_dma_rx_complete()`, and `mtk8250_dma_enable()` run circular-style RX transfers and push tty flip buffers. `mtk8250_set_termios()` recalculates high-speed divisor/sample/fraction registers and installs hardware/software flow control through `mtk8250_set_flow_ctrl()`. PM hooks manage clocks and pinctrl/wake IRQs. `mtk8250_probe()` maps MMIO, enables clocks, configures port callbacks, disables rate-fix, registers with serial8250, and enables runtime PM.

Control flow: probe reads OF clocks and optional `dma-names`, fills a MEM32/regshift 2 `PORT_16550`, and registers. Startup disables DMA for console, resets counters, and delegates to serial8250. Termios may enable DMA then rewrites baud/sampling registers under port lock. Suspend selects sleep pinctrl and wake IRQ; runtime suspend waits for `DEBUG0` idle then disables clocks.

State and persistence: driver state tracks DMA RX position/status, clock handles, registered line, and wake IRQ. Hardware state includes highspeed/sample/fraction registers, EFR flow-control state, escape character, DMA enable, and PM clock state.

Dependencies and integration points: OF, clocks, DMAengine through serial8250 DMA, runtime PM, pinctrl, tty flip buffers, earlycon, and serial8250.

Risks: runtime suspend spins while `MTK_UART_DEBUG0` is nonzero with no timeout. DMA RX completion restarts transfers while holding the port lock and must avoid shutdown races. Flow-control mode uses `termios->c_iflag & CRTSCTS`, which is unusual because `CRTSCTS` is a c_cflag bit. Test signals: high baud accuracy, low baud fallback, hardware/software/no flow control, DMA RX wraparound and shutdown, console mode without DMA, runtime PM idle timeout behavior, wake IRQ suspend/resume, and earlycon output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_mtk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_ni.c -->
## sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_ni.c

Purpose: ACPI platform driver for National Instruments 16550-compatible UARTs with extra FIFO-size, prescaler, transceiver, and RS485/RS422 controls.

Important APIs, types, and functions: `struct ni16550_device_info` supplies static clock, prescaler, and PMR availability per ACPI ID. `struct ni16550_data` stores line and optional clock. `ni16550_get_regs()` handles either I/O port or MMIO resources. `ni16550_read_fifo_size()` reads hardware FIFO sizes. `ni16550_config_prescaler()` pages enhanced registers and writes CPR via ICR. `ni16550_rs485_config()` programs PCR wire mode and ACR auto-DTR. Startup/shutdown enable or disable transceivers around serial8250 startup/shutdown.

Control flow: probe allocates a `uart_8250_port`, sets defaults early so `serial_in/out` work, reads FIFO sizes and clock from match data/properties/clk, optionally configures prescaler, determines RS232 versus RS485 from `transceiver` property or PMR, installs RS485 setup for non-RS232 ports, registers, and stores the line. Remove unregisters.

State and persistence: runtime state is line plus optional clock. Hardware state includes PCR transceiver enable/wire mode, PMR mode/capability, ACR auto-DTR, CPR prescaler, FIFO size registers, and MCR clock-select bit.

Dependencies and integration points: ACPI matching, generic device properties, optional clk, serial8250 enhanced-register helpers, and RS485 core.

Risks: old devices may report missing FIFO size as `0x00` or `0xff`, so the fallback to 128 is intentional but could mask bad reads. Prescaler writes depend on enhanced-mode register paging. `transceiver` string compatibility must remain stable. Test signals: all ACPI IDs, MMIO and I/O resources, PMR and property-based RS232/RS485 detection, transceiver enable/disable at open/close, prescaler baud accuracy, FIFO size reporting, and RS422/RS485 ioctl modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_ni.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_of.c -->
## sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_of.c

Purpose: generic Open Firmware/platform frontend for many 8250-compatible UART device-tree nodes. It translates DT resources and properties into `uart_8250_port` instances, with small hooks for NPCM, RT2880, Freescale errata, clocks, resets, RS485 emulation, and PM.

Important APIs, types, and functions: `struct of_serial_info` stores clocks, reset control, port type, line, and clock notifier. `of_platform_serial_setup()` maps resources, reads validated port properties, obtains clocks, deasserts reset, installs em485 callbacks, applies type-specific setup, and optionally installs `fsl8250_handle_irq`. `of_platform_serial_probe()` handles exclusions, tx-threshold, auto-flow-control, overrun throttle, registration, and clock notifier setup. `of_platform_serial_clk_notifier_cb()` updates UART clock on rate changes. PM callbacks suspend/resume serial8250 and clocks.

Control flow: OF match data supplies the serial port type. Probe rejects RTAS-owned nodes and some BCM7271 nodes handled elsewhere, allocates info, builds the port, registers it, then installs a clock notifier. Remove unregisters the notifier/port, asserts reset, drops runtime PM, and frees info.

State and persistence: runtime state is info struct with line, clocks, reset, and notifier. Hardware state includes reset deassertion, clock rates, custom divisor if `current-speed` is present, and optional NPCM timeout setup.

Dependencies and integration points: OF address/IRQ/property helpers, clocks and notifiers, reset framework, runtime PM, serial8250, `serial8250_em485_*`, RT2880 setup, and optional Freescale handler symbol.

Risks: this broad generic driver can bind devices better handled by specialized drivers unless excluded. Clock notifier cleanup must match successful registration. `pm_runtime_get_sync()` return values are not deeply handled. Test signals: each compatible type, IORESOURCE_IO versus MMIO, clock-frequency versus clk provider, clock rate changes, reset assert/deassert, RS485 emulation, `tx-threshold`, `auto-flow-control`, overrun throttle, FSL compatible IRQ behavior, and suspend/resume on console and non-console ports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_of.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_omap.c -->
## sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_omap.c

Purpose: full platform driver for TI OMAP/AM/DRA/K3 UARTs using the 8250 core while handling OMAP-specific register banking, DMA, wakeup, runtime PM, errata, flow control, and optional native RS485.

Important APIs, types, and functions: `struct omap8250_priv` stores MMIO, line, errata/features (`habit`), saved MDR/EFR/SCR/XON/XOFF/divisor state, FIFO triggers, PM QoS state, DMA state, wake IRQ, throttling, and pinctrl. `omap_8250_set_termios()` chooses 13x/16x mode and calls `omap8250_restore_regs()`. `omap8250_irq()` wraps non-DMA IRQ handling with runtime PM and timeout/overrun quirks. Under DMA, `omap_8250_rx_dma()`, `omap_8250_rx_dma_flush()`, `omap_8250_tx_dma()`, and `omap_8250_dma_handle_irq()` manage RX/TX DMA. `omap8250_rs485_config()` selects native MDR3 direction control or falls back to em485. Probe initializes platform data, PM, IRQ, DMA, and serial8250 registration.

Control flow: probe maps MMIO, fills 8250 callbacks, reads DT properties, initializes PM QoS and runtime PM, detects UART revision/errata, configures optional DMA from DT, requests an initially disabled IRQ, registers the port, and discovers wake pinctrl. Startup sets wake IRQ, enables runtime PM capability, clears FIFOs, conditionally requests DMA, enables WER, starts RX DMA, and enables IRQ. Shutdown reverses WER/IER/DMA/IRQ. Runtime suspend may soft-reset for clock-disable errata, flush DMA, and relax QoS; runtime resume restores registers if context was lost.

State and persistence: much hardware state is shadowed in `priv` because context can be lost during runtime PM. DMA state tracks running transfers, broken RX DMA, delayed register restore while TX DMA is active, and throttle state. PM QoS latency is recalculated from baud and updated through workqueue.

Dependencies and integration points: OF matching, serial8250 core, DMAengine, runtime/system PM, wakeirq, pinctrl, PM QoS, SoC revision matching, tty flip buffers, reboot/console fixup, and `serial8250_em485`.

Risks: DMA/PM/interrupt ordering is complex; delayed restore during TX DMA, RX timeout errata, and wake IRQ races are high-risk areas. Native RS485 only handles fixed delays and falls back to software for unsupported combinations. Soft reset on runtime suspend deliberately clears SCR and depends on later restore. Test signals: non-DMA and DMA RX/TX, AM654 EFR2 timeout path, overrun throttle, K3 RX timeout quirk, runtime PM context loss, system suspend with wake-source and console, native and emulated RS485, 13x/16x baud accuracy, throttle/unthrottle, and ttyO console command-line fixup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_omap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_parisc.c -->
## sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_parisc.c

Purpose: PA-RISC GSC serial initialization for Lasi/Asp/Wax/Dino/Timi-style 8250 UARTs. It registers platform-discovered PA-RISC serial hardware with serial8250 and preserves expected tty ordering for some machines.

Important APIs, types, and functions: `serial_init_chip()` maps a PA-RISC device HPA address, derives IRQ and clock, fills `uart_8250_port`, and registers it. Two `parisc_device_id` tables split Lasi-specific systems from the broader serial table. `probe_serial_gsc()` registers `lasi_driver` first and `serial_driver` second to force `ttyS0` ordering where SERIAL_0 is under Lasi and SERIAL_1 under Dino.

Control flow: module init registers both parisc drivers. Each probe validates or synthesizes IRQ, adjusts address by `0x800` except for one sversion, maps 16 bytes, sets `UPIO_MEM`, clock, IRQ, boot autoconfig, and registers the port. There is no remove callback; these are init-time system devices.

State and persistence: no private driver data is stored after successful registration. The ioremap pointer is passed to serial8250. Hardware discovery state comes from PA-RISC device IDs and HPA resources.

Dependencies and integration points: PA-RISC device bus, IOSAPIC serial IRQ helper on 64-bit IOSAPIC builds, architecture I/O mapping, and serial8250 registration.

Risks: no successful-path unmap is present in this file because serial8250 takes over the mapping; teardown is not modeled. IRQ-less devices are ignored or logged depending on parent type. Test signals: boot on Lasi-first and Dino-first systems, tty numbering, IOSAPIC IRQ derivation for sversion `0xad`, address offset handling, and registration failure cleanup with `iounmap()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/8250/8250_parisc.c -->
