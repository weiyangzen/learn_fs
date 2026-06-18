# Research: subset-b-005461

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/sc16is7xx.c -->
# sources/distributed-fs/ceph-client/drivers/tty/serial/sc16is7xx.c

## Purpose
Core tty/serial implementation for NXP SC16IS7xx UART expanders. It is bus-neutral: SPI and I2C wrappers provide per-port regmaps and call `sc16is7xx_probe()`, while this file registers `ttySC*` UART ports, handles interrupts or polling, GPIO side functions, IrDA selection, hardware modem lines, RS-485 support, and clock/reset/power sequencing.

## Important APIs, Types, And Functions
Key state is split between `struct sc16is7xx_port` for chip-wide resources and `struct sc16is7xx_one` for each UART. `sc16is7xx_one` owns `struct uart_port`, a regmap, register mutex, kthread work items, cached modem state, RX buffer, pending config bits, and IrDA mode. `struct sc16is7xx_devtype` instances describe variant name, GPIO count, and UART count.

Exported APIs are `sc16is7xx_probe()`, `sc16is7xx_remove()`, `sc16is7xx_regcfg`, `sc16is7xx_dt_ids`, devtype symbols, `sc16is7xx_regmap_name()`, and `sc16is7xx_regmap_port_mask()`. UART operations are collected in `sc16is7xx_ops`: TX/RX control, modem control, termios, startup/shutdown, RS-485 config, break, PM, and port verification.

## Control Flow
Module init registers `sc16is7xx_uart`; bus wrappers later call `sc16is7xx_probe()`. Probe validates regmaps by reading LSR, obtains clock or `clock-frequency`, starts a FIFO-priority kthread worker, resets the chip, allocates line IDs, configures each channel with `uart_add_one_port()`, optionally configures IrDA, modem-control GPIO muxing, and gpiochip export, then installs a threaded IRQ. If no IRQ exists, delayed kthread polling repeatedly invokes the same interrupt service path.

The IRQ path loops over all UARTs and calls `sc16is7xx_port_irq()`. It reads IIR under the per-port register mutex, dispatches RX sources to FIFO reads and `uart_insert_char()`, TX empty to `sc16is7xx_handle_tx()`, modem sources to cached mctrl updates and serial-core notifications, and logs unexpected IDs with rate limiting. TX is deferred through `tx_work`; register changes that require sleeping regmap access are coalesced through `reg_work`.

## State And Persistence
Runtime state is in driver-private memory and hardware registers. There is no durable persistence. Line allocation uses a module-global IDA. Cached state includes `old_mctrl`, `old_lcr`, pending IER/MCR/RS485 config, and optional gpio valid masks. Regmap cache uses `REGCACHE_MAPLE`; volatile, precious, and no-increment callbacks protect FIFO and status registers.

## Dependencies And Integration Points
Depends on Linux serial core, tty flip buffers, regmap, clk, GPIO/descriptor APIs, kthread worker APIs, IRQ handling, device properties, and optional GPIOLIB. Device tree properties include `clock-frequency`, `irda-mode-ports`, `nxp,modem-control-line-ports`, reset GPIO, and RS-485 properties consumed by serial core.

## Risks
The chip has overlapping register banks selected by magic LCR values; the mutex and regcache bypass are critical because interrupts can otherwise read EFR as IIR. Polling mode can hide IRQ wiring problems and adds latency. FIFO level sanity checks handle bad TXLVL/RXLVL readings but indicate possible hardware or regmap issues. Cleanup paths must free IDA lines only after registration state is known. RS-485 only supports hardware RTS timing plus optional pre-send delay; post-send delay is rejected.

## Test Signals
Useful signals include successful `ttySC*` registration, IRQ or polling RX/TX loopback, termios changes across baud/parity/word/stop settings, CTS/DCD change propagation, RS-485 ioctl behavior including rejected post-send delay, gpiochip visibility for 75x/76x variants, reset GPIO and software-reset coverage, suspend power bit behavior, and stress tests around enhanced-register access while interrupts fire.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/sc16is7xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/sc16is7xx.h -->
# sources/distributed-fs/ceph-client/drivers/tty/serial/sc16is7xx.h

## Purpose
Shared public header for the SC16IS7xx serial implementation and its I2C/SPI transport modules. It defines the transport-neutral device type contract, maximum UART channel count, and exported symbols needed by bus-specific probe/remove code.

## Important APIs, Types, And Functions
`SC16IS7XX_MAX_PORTS` is fixed at two. `struct sc16is7xx_devtype` carries the variant name plus `nr_gpio` and `nr_uart`. The header declares the exported `sc16is7xx_regcfg`, `sc16is7xx_dt_ids`, variant descriptors, `sc16is7xx_regmap_name()`, `sc16is7xx_regmap_port_mask()`, `sc16is7xx_probe()`, and `sc16is7xx_remove()`.

## Control Flow
Bus drivers include this header, match a device to one of the exported devtypes, create one regmap per UART channel, and pass the resulting array and IRQ to `sc16is7xx_probe()`. Removal calls `sc16is7xx_remove()` with the same device object.

## State And Persistence
The header owns no runtime storage. It defines the ABI between the core module and transport modules, so layout and symbol changes affect module loading and namespace imports.

## Dependencies And Integration Points
Includes `mod_devicetable.h`, `regmap.h`, and `types.h`; forward declares `struct device`. Symbols are exported from the core module under the `SERIAL_NXP_SC16IS7XX` namespace and imported by SPI/I2C wrappers.

## Risks
The regmap array contract relies on callers allocating entries up to `devtype->nr_uart` and respecting `SC16IS7XX_MAX_PORTS`. Changing devtype contents or symbol names can break both bus modules.

## Test Signals
Build both SPI and I2C modules, verify namespace import/export resolution, probe one- and two-port variants, and confirm invalid or missing match data returns probe errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/sc16is7xx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/sc16is7xx_i2c.c -->
# sources/distributed-fs/ceph-client/drivers/tty/serial/sc16is7xx_i2c.c

## Purpose
I2C transport wrapper for SC16IS7xx chips. It handles I2C/OF matching, creates per-channel I2C regmaps using the shared core regmap configuration, and delegates all UART behavior to `sc16is7xx_probe()`.

## Important APIs, Types, And Functions
`sc16is7xx_i2c_probe()` obtains match data with `i2c_get_match_data()`, copies `sc16is7xx_regcfg`, sets a per-port regmap name and I2C port-select read/write flag masks, and calls `devm_regmap_init_i2c()`. `sc16is7xx_i2c_remove()` delegates to `sc16is7xx_remove()`. The I2C ID table maps SC16IS740/741/74x/750/752/760/762 names to shared devtypes.

## Control Flow
`module_i2c_driver()` registers the driver. Probe fails with `-ENODEV` if match data is absent. For each UART channel in the variant, it creates a regmap configured with `sc16is7xx_regmap_port_mask(i)` for both reads and writes, then calls the core probe with `i2c->irq`.

## State And Persistence
No persistent state beyond devm-managed regmaps. All long-lived UART state is allocated by the core driver and attached as device driver data.

## Dependencies And Integration Points
Depends on I2C core, regmap-I2C, module device tables, and the SC16IS7xx exported namespace. It shares `sc16is7xx_dt_ids` with the core so DT compatible matching remains centralized.

## Risks
The copied `regmap_config` is mutated in a loop; every per-port field must be set before each `devm_regmap_init_i2c()` call. Incorrect flag masks would address the wrong UART channel on dual-port chips.

## Test Signals
Probe all ID aliases through I2C modalias and OF matching, verify `i2cdetect`-level reachability is not enough without LSR read success in the core, and exercise dual-UART traffic to confirm port mask isolation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/sc16is7xx_i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/sc16is7xx_spi.c -->
# sources/distributed-fs/ceph-client/drivers/tty/serial/sc16is7xx_spi.c

## Purpose
SPI transport wrapper for SC16IS7xx chips. It validates SPI mode, applies default SPI transfer settings, creates per-UART SPI regmaps, and delegates UART lifecycle to the bus-neutral core.

## Important APIs, Types, And Functions
`SC16IS7XX_SPI_READ_BIT` marks SPI reads. `sc16is7xx_spi_probe()` sets `bits_per_word` to 8, rejects non-mode-0 transfers, defaults speed to 4 MHz when unspecified, calls `spi_setup()`, obtains match data, and builds regmaps with per-port masks. `sc16is7xx_spi_remove()` calls `sc16is7xx_remove()`. The SPI ID table mirrors the I2C aliases.

## Control Flow
`module_spi_driver()` registers the driver. Probe performs bus setup before match-data validation, copies shared regmap config, and for each UART sets `read_flag_mask` to port mask OR `BIT(7)` because regmap otherwise substitutes its own default read bit. Write masks contain only the port selector. The core receives `spi->irq`.

## State And Persistence
The wrapper keeps no private runtime state. Regmaps are devm-managed and core state is stored through `dev_set_drvdata()` in `sc16is7xx_probe()`.

## Dependencies And Integration Points
Depends on SPI core, regmap-SPI, units macros for MHz defaults, module tables, and the SC16IS7xx namespace. OF matching uses the common `sc16is7xx_dt_ids`.

## Risks
SPI read-mask handling is subtle: omitting the explicit read bit would cause bad addressing. SPI mode validation is strict because variants support only mode 0. Defaulting speed may be too conservative or too high for marginal boards depending on wiring, but is bounded at 4 MHz.

## Test Signals
Probe with valid and invalid SPI modes, verify correct register reads on port 0 and port 1, run RX/TX under interrupts and polling fallback, and test unspecified `spi-max-frequency` paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/sc16is7xx_spi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/sccnxp.c -->
# sources/distributed-fs/ceph-client/drivers/tty/serial/sccnxp.c

## Purpose
Platform driver for NXP/Philips SCCNXP/SC26xx-style memory-mapped UART chips. It supports one- and two-channel devices, optional console support, IRQ or timer polling, platform modem-control mapping, regulators, clocks, and the Linux serial core.

## Important APIs, Types, And Functions
`struct sccnxp_chip` describes variant frequency limits, FIFO size, feature flags, channel count, and read/write delay. `struct sccnxp_port` owns one `uart_driver`, an array of `uart_port`s, IRQ mask, opened flags, timer state, platform data, regulator, and optional console. `sccnxp_ops` implements serial core callbacks. Major paths include `sccnxp_probe()`, `sccnxp_remove()`, `sccnxp_set_baud()`, `sccnxp_handle_events()`, `sccnxp_handle_rx()`, `sccnxp_handle_tx()`, `sccnxp_set_termios()`, `sccnxp_startup()`, and `sccnxp_shutdown()`.

## Control Flow
Probe maps MMIO, allocates state, enables regulator and clock, falls back to the chip standard frequency when needed, validates frequency bounds, copies platform data, selects IRQ or polling mode, registers a `ttySC` UART driver, initializes every UART port, disables chip interrupts, and installs a falling-edge threaded IRQ or periodic timer. RX/TX event handling reads ISR masked by IMR and loops until no enabled events remain. Startup resets FIFOs/status, enables RX/TX, enables RXRDY interrupt, and marks the line opened. TX start enables TXRDY and may set external transceiver direction via output pins.

## State And Persistence
State is volatile: IMR shadow, opened-line flags, timer mode, platform mctrl mapping, and hardware register contents. There is no durable persistence. Console state is embedded when enabled. Regulator and clock lifetimes are tied to probe/remove.

## Dependencies And Integration Points
Integrates with platform devices and ID tables rather than OF compatible data in this file. Uses serial core, tty FIFO helpers, regulator and clk frameworks, ioremap resources, timers, IRQs, and optional console registration. Platform data (`struct sccnxp_pdata`) supplies polling interval, register shift, and modem-line bit mapping.

## Risks
`sccnxp_verify_port()` appears permissive because matching type or matching IRQ returns success; ioctl validation should be treated carefully. Poll mode depends on platform-provided microsecond interval. Baud selection mixes timer-derived and fixed-table rates; unsupported chip MR0 features are skipped. Direction-control output pins depend entirely on platform mctrl mapping.

## Test Signals
Probe each platform ID, validate frequency-bound failures, open/close both channels, run IRQ and polling RX/TX, exercise console write/setup if configured, test baud accuracy across table and timer paths, verify modem input/output bit mapping, and confirm regulator disable on remove and probe error.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/sccnxp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/serial-tegra.c -->
# sources/distributed-fs/ceph-client/drivers/tty/serial/serial-tegra.c

## Purpose
High-speed UART platform driver for NVIDIA Tegra SoCs. It registers `ttyTHS*` ports, supports PIO and DMA TX/RX paths, SoC-specific FIFO and clock quirks, modem control, suspend/resume through serial core, and device-tree configuration.

## Important APIs, Types, And Functions
`struct tegra_uart_chip_data` captures SoC capabilities: FIFO full status, FIFO reset behavior, clock source divider support, FIFO enable status, max port count, DMA burst size, and baud tolerance. `struct tegra_uart_port` embeds `uart_port` and tracks clock/reset, register shadows, DMA channels/buffers/descriptors/cookies, current baud, RX/TX progress, modem interrupt enablement, and DT baud tolerance entries. `tegra_uart_ops` implements serial callbacks. Central functions include `tegra_uart_probe()`, `tegra_uart_parse_dt()`, `tegra_uart_startup()`, `tegra_uart_hw_init()`, `tegra_uart_isr()`, DMA completion handlers, `tegra_uart_set_termios()`, and `tegra_uart_hw_deinit()`.

## Control Flow
Module init finds a matching OF node to size `tegra_uart_driver.nr`, registers the UART driver, then registers the platform driver. Probe matches chip data, parses DT alias and DMA availability, maps MMIO, obtains clock/reset/IRQ, and calls `uart_add_one_port()`. Startup allocates DMA channels unless PIO was selected, initializes hardware, requests IRQ, and enables receive interrupts. ISR loops on IIR: modem changes update serial-core counters, TX interrupt drains PIO TX, RX status/timeout/EORD dispatches PIO or DMA receive termination/restart, and line errors are decoded before tty insertion. Shutdown deinitializes hardware, drains/frees DMA, disables clock, and frees IRQ.

## State And Persistence
All state is runtime-only. Register shadows (`fcr_shadow`, `mcr_shadow`, `lcr_shadow`, `ier_shadow`) are authoritative for writes. DMA buffer mappings persist for an open port and are freed on shutdown. Device tree controls line number, modem interrupt support, DMA mode, and optional baud adjustment ranges.

## Dependencies And Integration Points
Depends on serial core, tty, DMAengine, clk, reset controller, platform/OF APIs, MMIO accessors, and system sleep PM. DT compatibles include Tegra20, Tegra30, Tegra186, and Tegra194 HSUART variants.

## Risks
DMA and PIO interleaving is complex, especially residue handling, alignment fallback, and flow-control RTS suppression around RX termination. FIFO reset requires SoC-specific waits to avoid data loss. Baud programming must satisfy chip-data tolerance or returns `-EIO`. Shutdown waits for TX empty and may report unready slaves when CTS flow control blocks drain.

## Test Signals
Boot with each compatible, verify `serial` aliases map expected lines, run RX/TX in pure PIO and DMA modes, test unaligned TX FIFO fallback, suspend/resume active ports, change baud/parity/stop/flow control, inject RX line errors, monitor DMA residue correctness, and verify FIFO reset waits prevent lost bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/serial-tegra.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/serial_base.h -->
# sources/distributed-fs/ceph-client/drivers/tty/serial/serial_base.h

## Purpose
Internal header for the Linux serial-base bus glue used by serial core, controller devices, and port devices. It is not intended for low-level UART drivers directly.

## Important APIs, Types, And Functions
Defines `struct serial_ctrl_device`, containing a child `struct device` and an IDA for port IDs, and `struct serial_port_device`, containing a child `struct device`, backing `uart_port`, and TX-enabled flag. It declares init/exit hooks for controller and port drivers, bus driver registration helpers, add/remove helpers for synthetic serial-base devices, serial core register/unregister entry points, and console preference matching when console support is enabled.

## Control Flow
`serial_base_bus.c`, `serial_ctrl.c`, `serial_port.c`, and `serial_core.c` share this header. `uart_add_one_port()` reaches `serial_ctrl_register_port()`, then `serial_core_register_port()`, which creates or reuses a controller device and creates a port device before registering the tty.

## State And Persistence
The structures hold only runtime device-model state. IDA state persists for the lifetime of a controller device and is released when its ports are removed.

## Dependencies And Integration Points
Depends on Linux device model, serial core, and container macros. It bridges traditional `uart_port` registration with the newer `serial-base` bus.

## Risks
The header defines internal contracts: misuse by low-level drivers or stale assumptions about `port_dev` lifecycle can lead to runtime PM or device-model bugs.

## Test Signals
Build serial core with and without console support, add/remove multiple ports sharing the same physical device and controller ID, and validate generated device names and port ID reuse.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/serial_base.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/serial_base_bus.c -->
# sources/distributed-fs/ceph-client/drivers/tty/serial/serial_base_bus.c

## Purpose
Implements the `serial-base` bus and the synthetic controller/port devices that sit between physical UART hardware devices and tty/serial-core registration.

## Important APIs, Types, And Functions
`serial_base_driver_register()` and unregister bind controller/port drivers to the bus. `serial_base_ctrl_add()` creates controller devices named `physical:ctrl_id`; `serial_base_port_add()` creates port devices named `physical:ctrl_id.port_id`; remove helpers delete and put devices. `serial_base_match_and_update_preferred_console()` supports `console=DEVNAME:0.0` style matching under console builds.

## Control Flow
`arch_initcall(serial_base_init)` registers the bus, then the controller and port drivers, and sets `serial_base_initialized`. Device creation before init returns `-EPROBE_DEFER`. Matching is prefix-based on device type (`ctrl` or `port`) against driver name. Port IDs are allocated from the controller's IDA unless `uart_port.port_id` is preselected.

## State And Persistence
Runtime state includes the bus registration flag, device objects, fwnode references reused from physical parents, and per-controller IDA allocations. No persistent data survives module unload.

## Dependencies And Integration Points
Uses device core, IDA, fwnode/property handling, spinlock includes, serial core, and optional console matching. `serial_core.c` is the primary caller for add/remove.

## Risks
Reference counting is central: fwnode handles are acquired during init and released in device release callbacks, and failed add paths must call `put_device()`. Prefix matching is simple, so driver names must remain `ctrl` and `port` aligned. Early port registration depends on `-EPROBE_DEFER` behavior.

## Test Signals
Validate `/sys/bus/serial-base` devices, add multiple UARTs under one physical device, test fixed and automatic `port_id`, force early registration deferral, remove last port and confirm controller cleanup, and test preferred-console matching.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/serial_base_bus.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/serial_core.c -->
# sources/distributed-fs/ceph-client/drivers/tty/serial/serial_core.c

## Purpose
Main Linux UART/tty serial core. It implements tty operations, UART driver registration, port lifecycle, termios and ioctl handling, RS-485/ISO7816 configuration validation, console helpers, suspend/resume, sysrq support, and the serial-base-backed `uart_add_one_port()` registration path.

## Important APIs, Types, And Functions
Exported APIs include `uart_register_driver()`, `uart_unregister_driver()`, `uart_update_timeout()`, `uart_get_baud_rate()`, `uart_get_divisor()`, `uart_console_write()`, `uart_parse_earlycon()`, `uart_parse_options()`, `uart_set_options()`, `uart_suspend_port()`, `uart_resume_port()`, `uart_match_port()`, `uart_handle_dcd_change()`, `uart_handle_cts_change()`, `uart_insert_char()`, `uart_try_toggle_sysrq()`, and `uart_get_rs485_mode()`. Internally, `serial_core_register_port()` creates serial-base devices before `serial_core_add_one_port()` links `uart_state`, `tty_port`, and low-level `uart_port`.

## Control Flow
Low-level drivers register a `uart_driver`; each port is then added through `uart_add_one_port()` in `serial_port.c`, which reaches `serial_core_register_port()`. The core sets `UPF_DEAD`, creates/reuses the serial-base controller, adds a port device, updates preferred console if needed, then configures and registers the tty/serdev device. Open/startup paths allocate xmit buffers, power the port, call low-level startup and termios setup, and manage DTR/RTS. Close/hangup/shutdown drains TX, disables line discipline paths, and calls low-level shutdown. Remove unregisters tty, hangs up users, releases resources, drops serial-base devices, and waits for references.

## State And Persistence
State lives in `uart_driver.state[]`, `uart_state`, `tty_port`, `uart_port`, circular TX kfifo, PM state, modem counters, console associations, and RS-485/ISO7816 configs. It is runtime-only but visible through tty devices, procfs, sysfs attributes, ioctls, and console registration.

## Dependencies And Integration Points
Integrates deeply with tty core, serdev, console, device model, serial-base bus, PM, line disciplines, kfifo, wait queues, locks, and firmware properties for RS-485 GPIOs. Low-level drivers interact through `struct uart_ops`.

## Risks
This file is concurrency-sensitive: port mutex, tty port mutex, atomic references, spinlocks, runtime PM, hangups, console paths, and IRQ-side callbacks must align. Registration failures after partial device creation require strict cleanup. RS-485 sanitization must keep userspace ABI layout and hardware-supported flags consistent.

## Test Signals
Run open/close/hangup races, add/remove active ports, suspend/resume console and non-console ports, ioctl coverage for serial info, modem waiting, RS-485 and ISO7816 configs, sysrq sequences, flow-control CTS/DCD changes, tty write wakeups, and serdev immediate-open behavior after device registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/serial_core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/serial_ctrl.c -->
# sources/distributed-fs/ceph-client/drivers/tty/serial/serial_ctrl.c

## Purpose
Serial-base controller device driver. It binds synthetic controller devices on the `serial-base` bus and enables runtime PM for the controller-level device.

## Important APIs, Types, And Functions
`serial_ctrl_probe()` enables runtime PM; `serial_ctrl_remove()` disables it. `serial_ctrl_register_port()` forwards to `serial_core_register_port()`, and `serial_ctrl_unregister_port()` forwards to `serial_core_unregister_port()`. `serial_base_ctrl_init()` and exit register/unregister the internal driver named `ctrl`.

## Control Flow
The serial-base bus init calls `serial_base_ctrl_init()`. When a controller device created by `serial_base_ctrl_add()` binds, probe enables PM. UART add/remove calls from low-level drivers are routed through this layer into `serial_core.c`.

## State And Persistence
No private persistent state is kept in this file. Runtime PM enablement is tied to the lifetime of the synthetic controller device.

## Dependencies And Integration Points
Uses Linux device core, PM runtime, serial core, and the local serial-base header. It is a thin bridge between serial-base controller devices and serial-core registration.

## Risks
Because it intentionally does little, most risk is ordering: controller PM must be enabled only after a controller device exists and disabled on remove. Forwarding functions preserve the serial-core contract.

## Test Signals
Inspect controller devices on the serial-base bus, verify PM runtime state appears for controller devices, and confirm `uart_add_one_port()`/`uart_remove_one_port()` still create and destroy tty devices through this layer.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/serial_ctrl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/serial_mctrl_gpio.c -->
# sources/distributed-fs/ceph-client/drivers/tty/serial/serial_mctrl_gpio.c

## Purpose
Reusable helper implementation for UART modem-control lines backed by GPIO descriptors. It lets low-level serial drivers set RTS/DTR, read CTS/DSR/DCD/RI, and receive GPIO IRQ notifications as serial-core modem-status changes.

## Important APIs, Types, And Functions
`struct mctrl_gpios` stores the owning `uart_port`, GPIO descriptors, IRQ numbers, previous modem-control state, and enable flag. Exported functions include `mctrl_gpio_set()`, `mctrl_gpio_get()`, `mctrl_gpio_get_outputs()`, `mctrl_gpio_to_gpiod()`, `mctrl_gpio_init_noauto()`, `mctrl_gpio_init()`, enable/disable modem-status IRQ helpers, and IRQ wake helpers. `mctrl_gpio_irq_handle()` maps GPIO edge changes to UART icount updates and `uart_handle_dcd_change()`/`uart_handle_cts_change()`.

## Control Flow
Initialization scans device properties named `cts-gpios`, `dsr-gpios`, `dcd-gpios`, `rng-gpios`, `rts-gpios`, and `dtr-gpios`. Input GPIOs are converted to IRQs with `IRQ_NOAUTOEN` and requested edge-both. `.enable_ms` calls `mctrl_gpio_enable_ms()`, snapshots current input state, and enables IRQs. IRQs update cached state under the UART port lock and wake `delta_msr_wait`.

## State And Persistence
State is devm-allocated and lasts for the device lifetime. Output GPIO states are hardware state; input cached state is `mctrl_prev`. There is no durable persistence.

## Dependencies And Integration Points
Depends on GPIOLIB, device properties, IRQ APIs, termios modem-control constants, and serial-core modem helpers. The paired header provides no-op stubs when `CONFIG_GPIOLIB` is disabled.

## Risks
Drivers must not also handle the same GPIO input line changes or duplicate events may occur. IRQ enable/disable tracks `mctrl_on`; imbalance would leave modem interrupts disabled or enabled unexpectedly. `gpiod_get_value()` assumes appropriate sleep context for these calls.

## Test Signals
Use GPIO-backed CTS/DCD/DSR/RI lines with edge injection, verify `TIOCMGET` state, test RTS/DTR output changes, enable/disable modem status repeatedly, suspend wake enable/disable paths, and build with GPIOLIB disabled to verify stubs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/serial_mctrl_gpio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/serial_mctrl_gpio.h -->
# sources/distributed-fs/ceph-client/drivers/tty/serial/serial_mctrl_gpio.h

## Purpose
Public helper header for serial drivers that use GPIOs as modem-control lines. It defines GPIO line indexes, the opaque `mctrl_gpios` handle, function prototypes, and no-op fallbacks when GPIOLIB is not built.

## Important APIs, Types, And Functions
`enum mctrl_gpio_idx` maps CTS, DSR, DCD, RNG/RI, RTS, and DTR. The API surface provides setters/getters, GPIO descriptor lookup, automatic and no-auto initialization, modem-status IRQ enable/disable, and IRQ wake enable/disable.

## Control Flow
Serial drivers include this header, call `mctrl_gpio_init()` or `mctrl_gpio_init_noauto()`, then delegate modem callbacks to the helper functions. With GPIOLIB disabled, inline stubs preserve buildability and return unchanged modem-control state or NULL handles.

## State And Persistence
The header owns no storage. It defines an opaque runtime handle whose real layout is private to `serial_mctrl_gpio.c`.

## Dependencies And Integration Points
Includes error, device, and GPIO consumer headers. Integrates with `struct uart_port` without exposing serial-core internals.

## Risks
Callers must tolerate NULL helper handles because absent GPIOs and disabled GPIOLIB are valid. The alias `UART_GPIO_RI = UART_GPIO_RNG` means code should treat ring naming consistently.

## Test Signals
Compile serial drivers with GPIOLIB on and off, validate NULL-safe calls, and confirm each GPIO property name maps to the expected modem-control bit through the implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/serial_mctrl_gpio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/serial_port.c -->
# sources/distributed-fs/ceph-client/drivers/tty/serial/serial_port.c

## Purpose
Serial-base port device driver. It provides runtime PM behavior for synthetic serial port devices, routes public `uart_add_one_port()`/`uart_remove_one_port()` into the serial-base/controller/core stack, and reads common UART firmware properties.

## Important APIs, Types, And Functions
`serial_port_runtime_resume()` restarts pending TX after runtime resume when TX is enabled. `serial_port_runtime_suspend()` refuses suspend with `-EBUSY` while TX data remains. `serial_base_port_startup()` and shutdown toggle the port device `tx_enabled` flag. Public exports are `uart_add_one_port()`, `uart_remove_one_port()`, `uart_read_port_properties()`, and `uart_read_and_validate_port_properties()`. `__uart_read_properties()` handles common firmware parsing and validation.

## Control Flow
The serial-base bus init registers an internal driver named `port`. Probe enables runtime PM autosuspend with a 500 ms delay. Low-level drivers calling `uart_add_one_port()` are forwarded through controller registration to serial core. Firmware property reading can apply defaults or validate an already-initialized port: clock frequency, reg shift, IO width, reg offset, FIFO size, no-loopback-test, OF alias, IRQ, and shared-IRQ flag.

## State And Persistence
Per-port state is the synthetic `serial_port_device` and its `tx_enabled` bit. Firmware-derived values are written into `uart_port` fields. No persistent data is stored.

## Dependencies And Integration Points
Depends on device core, runtime PM, platform/PNP/fwnode IRQ APIs, OF aliases, serial core, and kfifo helpers. It is the public wrapper layer that low-level UART drivers use for add/remove.

## Risks
Runtime PM only models pending TX, so RX wake behavior remains driver-specific. Property validation must avoid mapbase/mapsize underflow when applying `reg-offset`. IRQ defaults differ between defaulting and validation modes. Resume calls low-level `start_tx()` under the port lock, so driver callbacks must obey serial-core locking expectations.

## Test Signals
Read properties from platform, PNP, and generic fwnode devices; validate bad `reg-io-width` and out-of-range `reg-offset`; verify autosuspend blocks on pending TX; confirm `uart_add_one_port()` creates serial-base and tty devices; and test remove while TX is disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tty/serial/serial_port.c -->
